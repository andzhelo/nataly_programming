"""Publish a week file into Sinergy (the `week-publish` Edge Function; sinergy/docs/10).

    .venv/bin/python tools/publish_sinergy.py tracks/rx-club/weeks/2026-11-15.md [--dry-run] [--publish] [--only 2026-11-16]
    .venv/bin/python tools/publish_sinergy.py athletes/eddie/weeks/2026-11-08.md --track "Eddie"

Each day of the file becomes one workout on the track, each block one part: exercise blocks
("- Name: S x R @ load") become structured rows, plain-text blocks are read by Sinergy's
parser with the text kept as written. Repeating a week updates the same days in place.
Days land UNPUBLISHED unless --publish is given; Nataly publishes in the console otherwise.

Login: SINERGY_LOGIN / SINERGY_PASSWORD in the environment (a programmer of the track), or a
prompt. Target: SINERGY_URL / SINERGY_ANON_KEY, defaulting to the hosted project.
"""
from __future__ import annotations
import argparse, getpass, json, os, sys, urllib.request, urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import weekfile  # noqa: E402

URL = os.environ.get("SINERGY_URL", "https://oyozrjdxnqdrqkpgexai.supabase.co")
ANON = os.environ.get("SINERGY_ANON_KEY", "sb_publishable_k6a_Bt2wYKkef11Mzs6evw_aLzcPwSi")
TRACKS = {"rx-club": "Rx Club"}   # folder name -> track name in Sinergy

KIND_WORDS = {"warm": "warmup", "skill": "skill", "gymnast": "skill", "strength": "strength", "lift": "strength",
              "metcon": "metcon", "wod": "metcon", "condition": "metcon", "accessor": "accessory", "core": "accessory",
              "cool": "cooldown", "stretch": "cooldown", "mobility": "warmup"}


def kind_for(title: str) -> str | None:
    t = title.lower()
    for k, v in KIND_WORDS.items():
        if k in t:
            return v
    return None


def section_of(block: dict) -> dict:
    title = f"{block['letter']}. {block['title']}".strip()
    lines = []
    if block["instruction"]:
        lines.append(block["instruction"])
    items = []
    for e in block["exercises"]:
        sets, reps = e["sets"], e["reps"]
        reps_text = f"{sets}x{reps[0]}" if len(set(reps)) == 1 else f"{sets} x {', '.join(reps)}"
        row = {"name": e["name"], "reps_text": reps_text}
        if e["reps_kind"] == "reps" and len(set(reps)) == 1 and reps[0].isdigit():
            row["reps"] = int(reps[0])
        if e["reps_kind"] == "time" and len(set(reps)) == 1:
            m, s = reps[0].split(":")
            row["duration_sec"] = int(m) * 60 + int(s)
        if e["loads"]:
            try:
                row["load_m"] = float(e["loads"][-1])   # the top load of the set list
                row["load_unit"] = e["load_unit"] or "kg"
            except ValueError:
                pass
        if e["notes"]:
            row["note"] = e["notes"].replace("\n", " ")
        items.append(row)
        load = f" @ {', '.join(e['loads'])} {e['load_unit']}" if e["loads"] else ""
        lines.append(f"{e['name']}: {e['sets']} x {', '.join(e['reps'])}{load}")
        if e["notes"]:
            lines.extend("  " + n for n in e["notes"].splitlines())
    sec = {"title": title, "text": "\n".join(lines).strip()}
    kind = kind_for(block["title"])
    if kind:
        sec["kind"] = kind
    if items:
        sec["items"] = items
        sec.setdefault("kind", "strength")
        sec["score_type"] = "load" if any("load_m" in i for i in items) else "checkmark"
    return sec


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("week_file")
    ap.add_argument("--track", help="track name in Sinergy (default: from the folder, e.g. rx-club -> Rx Club)")
    ap.add_argument("--publish", action="store_true", help="publish the days right away")
    ap.add_argument("--dry-run", action="store_true", help="parse and resolve only; nothing is written")
    ap.add_argument("--only", help="one date (YYYY-MM-DD) of the week")
    a = ap.parse_args()

    week = weekfile.parse(a.week_file)
    folder = Path(a.week_file).resolve().parts
    track_name = a.track or TRACKS.get(week["meta"].get("track", ""), None)
    if not track_name:
        for part in folder:
            if part in TRACKS:
                track_name = TRACKS[part]
    if not track_name:
        sys.exit("--track is required (no track in the frontmatter or the path)")

    days = []
    for d in week["days"]:
        if a.only and d["date"] != a.only:
            continue
        day = {"date": d["date"], "sections": [section_of(b) for b in d["blocks"]]}
        if d.get("title"):
            day["title"] = d["title"]
        days.append(day)
    if not days:
        sys.exit("no days to publish")

    login = os.environ.get("SINERGY_LOGIN") or input("Sinergy login (email): ")
    password = os.environ.get("SINERGY_PASSWORD") or getpass.getpass("Password: ")
    headers = {"apikey": ANON, "Content-Type": "application/json"}
    req = urllib.request.Request(f"{URL}/auth/v1/token?grant_type=password", data=json.dumps({"email": login, "password": password}).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            token = json.load(r)["access_token"]
    except urllib.error.HTTPError as e:
        sys.exit(f"login failed: {e.read().decode()[:200]}")
    headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(f"{URL}/rest/v1/tracks?name=eq.{urllib.request.quote(track_name)}&select=id,name", headers=headers)
    with urllib.request.urlopen(req) as r:
        tracks = json.load(r)
    if not tracks:
        sys.exit(f"no track named {track_name!r} is visible to {login}")

    body = {"track_id": tracks[0]["id"], "days": days, "publish": a.publish, "dry_run": a.dry_run}
    req = urllib.request.Request(f"{URL}/functions/v1/week-publish", data=json.dumps(body).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"week-publish failed: {e.read().decode()[:400]}")
    for d in out["days"]:
        parts = ""
        if d.get("sections"):
            parts = " (" + "; ".join(f"{s.get('title') or '?'}: {len(s.get('items') or [])} rows" for s in d["sections"]) + ")"
        print(f"{d['date']}: {d['action']}{parts}")
        for w in d.get("warnings") or []:
            print(f"   ! {w}")
    print(f"published days: {out.get('published', 0)}")


if __name__ == "__main__":
    main()
