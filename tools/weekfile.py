"""Parse a week file (athletes/<name>/weeks/YYYY-MM-DD.md) into structured data.

Usage:
    python3 tools/weekfile.py athletes/eddie/weeks/2026-11-08.md        # pretty summary
    python3 tools/weekfile.py athletes/eddie/weeks/2026-11-08.md --json # JSON for the uploader

Structure produced:
    {
      "meta": {...frontmatter...},
      "days": [
        {"heading": "Sun 08 Nov", "focus": "Squat + RMU", "date": "2026-11-08",
         "blocks": [
            {"letter": "A", "title": "Warm-up (~10 min)", "kind": "warmup",
             "prescription": "...", "notes": "...", "raw": "..."},
            ...
         ]}
      ]
    }
"""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

DAY_RE = re.compile(r"^## (?P<dow>Sun|Mon|Tue|Wed|Thu|Fri|Sat) (?P<day>\d{1,2}) (?P<mon>[A-Za-z]{3})(?: [—-] (?P<focus>.*))?$")
BLOCK_RE = re.compile(r"^### (?P<letter>[A-Z])\. (?P<title>.*)$")
MONTHS = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}

KIND_RULES = [
    ("warmup", re.compile(r"warm.?up", re.I)),
    ("metcon", re.compile(r"metcon|amrap|rft|for time|intervals", re.I)),
    ("accessory", re.compile(r"accessor", re.I)),
]


def parse_frontmatter(lines):
    if not lines or lines[0].strip() != "---":
        return {}, lines
    meta, i = {}, 1
    while i < len(lines) and lines[i].strip() != "---":
        if ":" in lines[i]:
            k, v = lines[i].split(":", 1)
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
            meta[k.strip()] = v
        i += 1
    return meta, lines[i + 1:]


def block_kind(title):
    for kind, rx in KIND_RULES:
        if rx.search(title):
            return kind
    return "work"


def split_block_body(body_lines):
    """First non-empty line is the prescription; the rest is notes."""
    body = [l.rstrip() for l in body_lines]
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    if not body:
        return "", ""
    return body[0].strip(), "\n".join(body[1:]).strip()


def parse(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    meta, lines = parse_frontmatter(lines)
    year = int(str(meta.get("week_start", date.today().isoformat()))[:4])

    days, cur_day, cur_block, buf = [], None, None, []

    def flush_block():
        nonlocal cur_block, buf
        if cur_block is not None:
            pres, notes = split_block_body(buf)
            cur_block.update(prescription=pres, notes=notes, raw="\n".join(buf).strip())
            cur_day["blocks"].append(cur_block)
        cur_block, buf = None, []

    for line in lines:
        m = DAY_RE.match(line)
        if m:
            flush_block()
            d = date(year, MONTHS[m["mon"].title()], int(m["day"]))
            cur_day = {"heading": f"{m['dow']} {m['day']} {m['mon']}", "dow": m["dow"],
                       "date": d.isoformat(), "focus": (m["focus"] or "").strip(), "blocks": []}
            days.append(cur_day)
            continue
        m = BLOCK_RE.match(line)
        if m and cur_day is not None:
            flush_block()
            cur_block = {"letter": m["letter"], "title": m["title"].strip(), "kind": block_kind(m["title"])}
            continue
        if cur_block is not None:
            buf.append(line)
    flush_block()

    # sanity: week_start should be the Sunday of the first day
    if days and "week_start" in meta:
        first = date.fromisoformat(days[0]["date"])
        sunday = first - timedelta(days=(first.weekday() + 1) % 7)
        if sunday.isoformat() != meta["week_start"]:
            print(f"warning: week_start {meta['week_start']} but first day {first} belongs to week of {sunday}", file=sys.stderr)
    return {"meta": meta, "days": days}


def summary(week):
    out = [f"{week['meta'].get('athlete','?')}  week of {week['meta'].get('week_start','?')}  [{week['meta'].get('status','?')}]"]
    for d in week["days"]:
        out.append(f"\n{d['heading']} ({d['date']}) — {d['focus']}")
        for b in d["blocks"]:
            pres = b["prescription"][:70] + ("…" if len(b["prescription"]) > 70 else "")
            out.append(f"  {b['letter']}. [{b['kind']:9}] {b['title']}: {pres}")
    return "\n".join(out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    week = parse(args[0])
    if "--json" in sys.argv:
        print(json.dumps(week, ensure_ascii=False, indent=2))
    else:
        print(summary(week))
