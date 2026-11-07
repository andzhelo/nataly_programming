"""Write a week file from what is in TrainHeroic.

    .venv/bin/python tools/download_week.py eddie 2026-11-08 [-o path] [--status published]

Reads the athlete's calendar and renders every session in that Sun..Sat window in
the week-file format (docs/format.md). Default output: stdout.
"""
from __future__ import annotations
import argparse, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from th_api import TH, SET_CIRCUIT, P1_TIME, P2_KG, P2_PERCENT
from weekfile import render
from common import athlete_ids, week_range, sessions_in_week


def _fmt_num(v) -> str:
    s = str(v)
    return s[:-2] if s.endswith(".0") else s


def session_to_day(p: dict) -> dict:
    blocks = []
    for s in sorted(p["sets"].values(), key=lambda s: int(s["order"])):
        exs = [e for e in (s.get("exercises") or []) if e.get("title")]
        if int(s["type"]) == SET_CIRCUIT or not exs:
            blocks.append({"title": s["title"], "instruction": (s.get("instruction") or "").strip(), "exercises": []})
            continue
        items = []
        for e in sorted(exs, key=lambda e: int(e["order"] or 0)):
            n = int(e.get("param_count") or 0)
            reps = [str(e.get(f"param_1_data_{i}") or "") for i in range(1, n + 1)]
            p2t = int(e.get("param_2_type") or 0)
            loads = [_fmt_num(e.get(f"param_2_data_{i}")) for i in range(1, n + 1)] if p2t in (P2_KG, P2_PERCENT) else []
            if any(l in ("", "None") for l in loads):
                loads = []
            unit = {P2_KG: "kg", P2_PERCENT: "%"}.get(p2t) if loads else None
            if p2t not in (0, P2_KG, P2_PERCENT):
                print(f"warning: {p['date']} {e['title']}: load type {p2t} not supported, dropped", file=sys.stderr)
            items.append({"name": e["title"], "sets": n, "reps": reps, "reps_kind": "time" if int(e.get("param_1_type") or 0) == P1_TIME else "reps",
                          "loads": loads, "load_unit": unit, "notes": (e.get("instruction") or "").strip()})
        blocks.append({"title": s["title"], "instruction": (s.get("instruction") or "").strip(), "exercises": items})
    title = p.get("title") or ""
    if title.replace("-", "").isdigit() or title == p["date"].replace("-0", "-").replace("-", "-"):
        title = ""  # TrainHeroic default title is the date
    return {"date": p["date"], "title": title, "blocks": blocks, "published": p.get("published")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("athlete"); ap.add_argument("week_start"); ap.add_argument("-o", "--out")
    ap.add_argument("--status", default=None, help="status to write in frontmatter (default: published/uploaded by TH state)")
    a = ap.parse_args()
    athlete_id, program_id = athlete_ids(a.athlete)
    ws, we = week_range(a.week_start)
    th = TH()
    cal = th.calendar(athlete_id, ws.year, ws.month, ws.day)
    sessions = sessions_in_week(cal, ws, we)
    if not sessions:
        raise SystemExit(f"no sessions between {ws} and {we}")
    days = [session_to_day(p) for p in sessions]
    status = a.status or ("published" if all(d["published"] for d in days) else "uploaded")
    meta = {"athlete": a.athlete, "athlete_id": athlete_id, "program_id": program_id, "week_start": a.week_start, "status": status}
    text = render(meta, days)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8"); print(f"wrote {a.out} ({len(days)} sessions)")
    else:
        print(text)


if __name__ == "__main__":
    main()
