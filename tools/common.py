"""Shared helpers: athlete config from profile frontmatter-ish constants."""
from __future__ import annotations
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ATHLETES = {
    # name: (athlete_id, program_id)
    "eddie": (2615164, 4414542),
}


def athlete_ids(name: str) -> tuple[int, int]:
    if name not in ATHLETES:
        raise SystemExit(f"unknown athlete {name!r}; known: {', '.join(ATHLETES)}")
    return ATHLETES[name]


def week_range(week_start: str) -> tuple[date, date]:
    ws = date.fromisoformat(week_start)
    if ws.weekday() != 6:
        raise SystemExit(f"{week_start} is not a Sunday")
    return ws, ws + timedelta(days=6)


def sessions_in_week(cal: dict, ws: date, we: date) -> list[dict]:
    out = [p for p in cal.get("programWorkouts", []) if not p.get("deleted") and ws <= date.fromisoformat(p["date"]) <= we]
    return sorted(out, key=lambda p: (p["date"], p.get("session") or 0))
