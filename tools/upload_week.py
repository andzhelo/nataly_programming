"""Upload a week file to TrainHeroic, UNPUBLISHED, and verify by reading it back.

    .venv/bin/python tools/upload_week.py athletes/eddie/weeks/2026-11-15.md [--replace] [--dry-run] [--only 2026-11-16]

Safety:
- Refuses if any exercise name is not in the library (prints closest matches).
- Refuses if a session already exists on a target date, unless --replace, which deletes
  UNPUBLISHED sessions on those dates first. Published sessions are never touched;
  a day with a published session is skipped with a warning.
- Never publishes. On success sets status: uploaded in the file.
"""
from __future__ import annotations
import argparse, re, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from th_api import TH, SET_EXERCISES, SET_CIRCUIT, P1_REPS, P1_TIME, P2_KG, P2_PERCENT, P2_NONE
from weekfile import parse, FormatError
from library import Library
from common import athlete_ids, week_range, sessions_in_week
from download_week import session_to_day


def resolve_all(week, lib):
    problems = []
    for d in week["days"]:
        for b in d["blocks"]:
            for e in b["exercises"]:
                hit = lib.resolve(e["name"])
                if hit:
                    e["exercise_id"], e["library_title"] = hit["id"], hit["title"]
                else:
                    problems.append(f"{d['date']} {b['title']}: unknown exercise {e['name']!r}. Closest: {', '.join(lib.suggest(e['name'])) or 'none'}")
    return problems


def to_exercise_payload(e, order):
    return {"exercise_id": e["exercise_id"], "title": e["library_title"], "order": order, "instruction": e["notes"],
            "p1_type": P1_TIME if e["reps_kind"] == "time" else P1_REPS, "p1": e["reps"],
            "p2_type": {"kg": P2_KG, "%": P2_PERCENT}.get(e["load_unit"], P2_NONE), "p2": e["loads"]}


def upload_day(th, program_id, d):
    dt = date.fromisoformat(d["date"])
    pw = th.create_session(program_id, dt.year, dt.month, dt.day, d["title"] or f"{dt.year}-{dt.month}-{dt.day}")
    for i, b in enumerate(d["blocks"], 1):
        if b["kind"] == "text":
            th.add_set(pw["workout_id"], i, b["title"], SET_CIRCUIT, b["instruction"])
        else:
            s = th.add_set(pw["workout_id"], i, b["title"], SET_EXERCISES, b["instruction"])
            th.add_exercises(s["id"], [to_exercise_payload(e, j) for j, e in enumerate(b["exercises"], 1)])
    return pw


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def diff_day(expected, actual):
    """Compare a parsed day with a downloaded day; return list of differences."""
    out = []
    if norm(expected["title"]) != norm(actual["title"]):
        out.append(f"title {expected['title']!r} != {actual['title']!r}")
    if len(expected["blocks"]) != len(actual["blocks"]):
        out.append(f"{len(expected['blocks'])} blocks expected, {len(actual['blocks'])} found")
    for eb, ab in zip(expected["blocks"], actual["blocks"]):
        if norm(eb["title"]) != norm(ab["title"]):
            out.append(f"block {eb['title']!r} != {ab['title']!r}")
        if norm(eb["instruction"]) != norm(ab["instruction"]):
            out.append(f"block {eb['title']}: instruction differs")
        if len(eb["exercises"]) != len(ab["exercises"]):
            out.append(f"block {eb['title']}: {len(eb['exercises'])} exercises expected, {len(ab['exercises'])} found")
        for ee, ae in zip(eb["exercises"], ab["exercises"]):
            exp = (ee.get("library_title", ee["name"]), ee["reps"], [str(float(x)) for x in ee["loads"]], ee["load_unit"], norm(ee["notes"]))
            act = (ae["name"], ae["reps"], [str(float(x)) for x in ae["loads"]], ae["load_unit"], norm(ae["notes"]))
            if exp != act:
                out.append(f"block {eb['title']}: {ee['name']}: expected {exp[1:]} got {act[1:]}" if exp[0] == act[0] else f"block {eb['title']}: {exp[0]!r} != {act[0]!r}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("week_file"); ap.add_argument("--replace", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="upload a single date YYYY-MM-DD"); ap.add_argument("--refresh-library", action="store_true")
    a = ap.parse_args()
    try:
        week = parse(a.week_file)
    except FormatError as e:
        raise SystemExit(f"FORMAT ERROR: {e}")
    athlete = week["meta"]["athlete"]
    athlete_id, program_id = athlete_ids(athlete)
    ws, we = week_range(week["meta"]["week_start"])
    days = [d for d in week["days"] if not a.only or d["date"] == a.only]
    if not days:
        raise SystemExit("no days to upload")

    th = TH()
    lib = Library(th, refresh=a.refresh_library)
    problems = resolve_all(week, lib)
    if problems:
        print("Cannot upload:"); [print("  -", p) for p in problems]
        print("Fix the name in the week file or add an alias in tools/aliases.json."); sys.exit(2)
    for d in days:
        for b in d["blocks"]:
            for e in b["exercises"]:
                if e["library_title"].lower() != e["name"].lower():
                    print(f"  note: {d['date']} {e['name']!r} -> library {e['library_title']!r}")

    cal = th.calendar(athlete_id, ws.year, ws.month, ws.day)
    existing = {}
    for p in sessions_in_week(cal, ws, we):
        existing.setdefault(p["date"], []).append(p)
    plan, skipped = [], []
    for d in days:
        ex = existing.get(d["date"], [])
        if any(p.get("published") for p in ex):
            skipped.append(f"{d['date']}: has a PUBLISHED session, skipped"); continue
        if ex and not a.replace:
            skipped.append(f"{d['date']}: already has {len(ex)} unpublished session(s); use --replace"); continue
        plan.append((d, ex))
    for s in skipped:
        print("  skip:", s)
    if not plan:
        raise SystemExit("nothing to upload")
    print(f"Will upload {len(plan)} session(s) for {athlete} as UNPUBLISHED:", flush=True); print("   ",
          ", ".join(f"{d['date']} ({len(d['blocks'])} blocks{', replacing ' + str(len(ex)) if ex else ''})" for d, ex in plan))
    if a.dry_run:
        print("dry run, nothing sent"); return

    from concurrent.futures import ThreadPoolExecutor
    def do(item):
        d, ex = item
        for p in ex:
            th.remove_session(program_id, p["id"])
        upload_day(th, program_id, d)
        print(f"  uploaded {d['date']} {d['title']}", flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool:   # one worker per day; TrainHeroic takes ~3 s per call
        list(pool.map(do, plan))

    # read back and verify
    cal = th.calendar(athlete_id, ws.year, ws.month, ws.day)
    actual = {p["date"]: session_to_day(p) for p in sessions_in_week(cal, ws, we) if not p.get("published")}
    ok = True
    for d, _ in plan:
        diffs = diff_day(d, actual.get(d["date"], {"title": "", "blocks": []}))
        if diffs:
            ok = False; print(f"  VERIFY {d['date']}: differences:"); [print("     -", x) for x in diffs]
        else:
            print(f"  verified {d['date']}: matches")
    if ok and not a.only:
        p = Path(a.week_file); txt = p.read_text(encoding="utf-8")
        txt2 = re.sub(r"^status:.*$", "status: uploaded", txt, count=1, flags=re.M)
        if txt2 != txt:
            p.write_text(txt2, encoding="utf-8"); print("  status -> uploaded")
    print("Done. Sessions are unpublished; Nataly reviews and publishes in the coach app.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
