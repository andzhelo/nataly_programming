"""Delete UNPUBLISHED sessions of an athlete in a week. Published sessions are never touched.

    .venv/bin/python tools/delete_week.py eddie 2027-03-07 [--yes]
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from th_api import TH
from common import athlete_ids, week_range, sessions_in_week


def delete_unpublished(th, athlete_id, program_id, ws, we, yes=False) -> int:
    cal = th.calendar(athlete_id, ws.year, ws.month, ws.day)
    sessions = sessions_in_week(cal, ws, we)
    pub = [p for p in sessions if p.get("published")]
    unpub = [p for p in sessions if not p.get("published")]
    if pub:
        print("published (kept):", ", ".join(f"{p['date']} {p.get('title') or ''}".strip() for p in pub))
    if not unpub:
        print("nothing unpublished to delete"); return 0
    print("unpublished to delete:", ", ".join(f"{p['date']} {p.get('title') or ''}".strip() for p in unpub))
    if not yes:
        if input("type DELETE to confirm: ").strip() != "DELETE":
            print("aborted"); return 0
    for p in unpub:
        th.remove_session(program_id, p["id"])
    print(f"deleted {len(unpub)} sessions")
    return len(unpub)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("athlete"); ap.add_argument("week_start"); ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    athlete_id, program_id = athlete_ids(a.athlete)
    ws, we = week_range(a.week_start)
    delete_unpublished(TH(), athlete_id, program_id, ws, we, a.yes)
