"""Parse and write week files (see docs/format.md).

    python3 tools/weekfile.py athletes/eddie/weeks/2026-11-08.md          # summary
    python3 tools/weekfile.py athletes/eddie/weeks/2026-11-08.md --json

Model:
  week  = {meta: {...}, days: [day]}
  day   = {dow, date (ISO), title, blocks: [block]}
  block = {letter, title, kind: "text"|"exercises", instruction, exercises: [exercise]}
  exercise = {name, sets, reps: [..], reps_kind: "reps"|"time", loads: [..], load_unit: "kg"|"%"|None, notes}
"""
from __future__ import annotations
import json, re, sys
from datetime import date, timedelta
from pathlib import Path

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DOWS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_RE = re.compile(r"^## (?P<dow>Sun|Mon|Tue|Wed|Thu|Fri|Sat) (?P<day>\d{1,2}) (?P<mon>[A-Za-z]{3})(?:\s+[—–-]\s+(?P<title>.*))?\s*$")
BLOCK_RE = re.compile(r"^### (?P<letter>[A-Z])\. (?P<title>.*?)\s*$")
EX_RE = re.compile(r"^- (?P<name>[^:]+):\s*(?P<sets>\d+)\s*[x×]\s*(?P<reps>[^,@\s]+(?:\s*,\s*[^,@\s]+)*)(?:\s*@\s*(?P<loads>[\d.]+(?:\s*,\s*[\d.]+)*)\s*(?P<unit>kg|%))?\s*$")


class FormatError(Exception):
    pass


def _frontmatter(lines):
    if not lines or lines[0].strip() != "---":
        return {}, lines
    meta, i = {}, 1
    while i < len(lines) and lines[i].strip() != "---":
        if ":" in lines[i]:
            k, v = lines[i].split(":", 1)
            meta[k.strip()] = v.split("#")[0].strip()
        i += 1
    return meta, lines[i + 1:]


def _expand(vals: str, n: int, what: str, where: str):
    parts = [p.strip() for p in vals.split(",")]
    if len(parts) == 1:
        parts = parts * n
    if len(parts) != n:
        raise FormatError(f"{where}: {what} has {len(parts)} values for {n} sets")
    return parts


def parse_exercise(line: str, where: str) -> dict:
    m = EX_RE.match(line)
    if not m:
        raise FormatError(f"{where}: cannot parse exercise line {line!r}. Expected '- Name: S x R [@ loads kg|%]'")
    n = int(m["sets"])
    reps = _expand(m["reps"], n, "reps", where)
    reps_kind = "time" if any(":" in r for r in reps) else "reps"
    if reps_kind == "time":
        reps = [r if len(r.split(":")[0]) == 2 else "0" + r for r in reps]  # 0:20 -> 00:20
    loads = _expand(m["loads"], n, "loads", where) if m["loads"] else []
    return {"name": m["name"].strip(), "sets": n, "reps": reps, "reps_kind": reps_kind,
            "loads": loads, "load_unit": m["unit"], "notes": ""}


def parse(path) -> dict:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    meta, lines = _frontmatter(lines)
    if "week_start" not in meta:
        raise FormatError("frontmatter needs week_start: YYYY-MM-DD")
    ws = date.fromisoformat(meta["week_start"])
    days, day, block, ex = [], None, None, None

    def close_block():
        nonlocal block, ex
        if block is None:
            return
        block["instruction"] = block["instruction"].strip()
        for e in block["exercises"]:
            e["notes"] = e["notes"].strip()
        block["kind"] = "exercises" if block["exercises"] else "text"
        day["blocks"].append(block)
        block, ex = None, None

    for ln, line in enumerate(lines, 1):
        where = f"{Path(path).name}:{ln}"
        m = DAY_RE.match(line)
        if m:
            close_block()
            mon = MONTHS.index(m["mon"].title()) + 1
            year = ws.year if mon >= ws.month else ws.year + 1
            d = date(year, mon, int(m["day"]))
            if not (ws <= d <= ws + timedelta(days=6)):
                raise FormatError(f"{where}: {d} is outside week starting {ws}")
            if DOWS[d.weekday()] != m["dow"]:
                raise FormatError(f"{where}: {d} is a {DOWS[d.weekday()]}, not {m['dow']}")
            day = {"dow": m["dow"], "date": d.isoformat(), "title": (m["title"] or "").strip(), "blocks": []}
            days.append(day)
            continue
        m = BLOCK_RE.match(line)
        if m:
            if day is None:
                raise FormatError(f"{where}: block before any day heading")
            close_block()
            block = {"letter": m["letter"], "title": m["title"], "instruction": "", "exercises": []}
            continue
        if block is None:
            if line.strip():
                raise FormatError(f"{where}: text outside a block: {line!r}")
            continue
        if line.startswith("- "):
            ex = parse_exercise(line.rstrip(), where)
            block["exercises"].append(ex)
        elif ex is not None and (line.startswith("  ") or not line.strip()):
            ex["notes"] += line[2:] + "\n" if line.startswith("  ") else "\n"
        elif block["exercises"]:
            raise FormatError(f"{where}: after exercise lines, notes must be indented by two spaces: {line!r}")
        else:
            block["instruction"] += line + "\n"
    close_block()
    return {"meta": meta, "days": days}


def render(meta: dict, days: list[dict]) -> str:
    out = ["---"] + [f"{k}: {v}" for k, v in meta.items()] + ["---", ""]
    for d in days:
        dt = date.fromisoformat(d["date"])
        head = f"## {DOWS[dt.weekday()]} {dt.day:02d} {MONTHS[dt.month - 1]}"
        if d.get("title"):
            head += f" — {d['title']}"
        out += [head, ""]
        for i, b in enumerate(d["blocks"]):
            out.append(f"### {chr(65 + i)}. {b['title']}")
            if b.get("instruction"):
                out.append(b["instruction"].rstrip())
            for e in b.get("exercises", []):
                reps = e["reps"]
                reps_s = reps[0] if len(set(reps)) == 1 else ", ".join(reps)
                if e["reps_kind"] == "time":
                    reps_s = ", ".join(r.lstrip("0") if r.startswith("00") else r for r in reps_s.split(", "))
                line = f"- {e['name']}: {e['sets']} x {reps_s}"
                if e.get("loads"):
                    loads = e["loads"]
                    loads_s = loads[0] if len(set(loads)) == 1 else ", ".join(loads)
                    line += f" @ {loads_s} {e['load_unit']}"
                out.append(line)
                for nl in (e.get("notes") or "").rstrip().splitlines():
                    out.append(("  " + nl) if nl.strip() else "")
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def summary(week: dict) -> str:
    m = week["meta"]
    out = [f"{m.get('athlete', '?')}  week of {m.get('week_start')}  [{m.get('status', '?')}]"]
    for d in week["days"]:
        out.append(f"\n{d['dow']} {d['date']} — {d['title']}")
        for b in d["blocks"]:
            if b["kind"] == "text":
                first = b["instruction"].splitlines()[0] if b["instruction"] else ""
                out.append(f"  {b['letter']}. {b['title']} [text] {first[:60]}")
            else:
                out.append(f"  {b['letter']}. {b['title']} [{len(b['exercises'])} exercises]")
                for e in b["exercises"]:
                    load = f" @ {','.join(e['loads'])} {e['load_unit']}" if e["loads"] else ""
                    out.append(f"      - {e['name']}: {e['sets']} x {','.join(e['reps'])}{load}")
    return "\n".join(out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); sys.exit(1)
    try:
        w = parse(args[0])
    except FormatError as e:
        print("FORMAT ERROR:", e); sys.exit(2)
    print(json.dumps(w, ensure_ascii=False, indent=2) if "--json" in sys.argv else summary(w))
