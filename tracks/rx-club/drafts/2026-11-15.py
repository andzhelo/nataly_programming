"""Rx Club, week of Sun 15 Nov 2026 (Week 12 of the Aug–Nov cycle: test week), drafted by Claude.

One source for both outputs:
  python3 tracks/rx-club/drafts/2026-11-15.py   → tracks/rx-club/weeks/2026-11-15.md (status: draft)
                                                  + tracks/rx-club/drafts/2026-11-15.json (Sinergy's shape for
                                                    sinergy/scripts/days-to-sql --json, structure written here,
                                                    so Sinergy's AI reader is not used)
Each part: title, kind, format, score, the text as Nataly would write it, the notes the athlete sees
in the coach's-note box, and the rows (movement slug from Sinergy's library).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEEK = "2026-11-15"


def it(slug, name, reps=None, reps_text=None, load=None, unit=None, cal=None, note=None, per_side=None, dist=None):
    row = {"slug": slug, "raw_name": name} if slug else {"raw_name": name}   # no slug: a row with its name only
    if reps is not None: row["reps"] = reps
    if reps_text: row["reps_text"] = reps_text
    if load: row["load_m"], row["load_f"], row["load_unit"] = load[0], load[1], unit or "kg"
    if cal: row["cal_m"], row["cal_f"] = cal
    if dist: row["distance_m"], row["distance_f"], row["distance_unit"] = dist, dist, "m"
    if per_side: row["per_side"] = True
    if note: row["note"] = note
    return row


def part(title, text, kind, fmt="none", score="none", notes=None, items=(), **extra):
    text = text.strip("\n")
    # A part with no rows is read from its text, so the athlete sees all of it.
    return {"title": title, "text": text, "kind": kind, "format": fmt, "score_type": score,
            "athlete_text": notes if notes or items else text, "items": list(items), **extra}


def pct(slug, name, sets, reps, p, note=None):
    return it(slug, name, reps=reps, reps_text=f"{sets}x{reps}", load=(p, p), unit="%", note=note)


SNATCH_PREP = """A) Snatch Grip OH Elbow Rotations
20 reps
B) Snatch Grip Sots Press
3 sets of 5 reps @empty Bar
C) Snatch Lift Off:
2 Sets of 5 reps @30%
D) No Feet Snatch Pull
2 Sets of 5 reps @30%
E) Muscle Snatch
2 sets of 3 reps @30%"""

CLEAN_PREP = """A) Butcher Block Stretch
2 sets of 1:00
B) Banded Front Rack Opener
1:00 each side
C) Wrist Flexion + Extension with Small Plates
2 sets of 15 reps each"""

SHOULDER_PREHAB = """A) Incline Chest Supported DB Front Raises
3-4 sets of 8-12 reps @light weight
B) Banded Shoulder Extension Pull Downs
3-4 sets of 12-15 reps
C) Half Kneeling Banded External Rotation Press:
3-4 sets of 5-8 reps each side"""

TEST_NOTE = "בהצלחה!\nאפשר חגורה כמובן"

DAYS = [
    {"date": "2026-11-15", "dow": "Sun 15 Nov", "title": "Snatch", "parts": [
        part("Snatch Prep MUST DO", SNATCH_PREP, "warmup", score="checkmark"),
        part("Snatch", """
Week 12:
Take 15 mins and build up to a heavy Squat Snatch single for the day @RPE 8-9
rest 2:00 between heavy attempts
תתחילו נמוך ותעלו בהדרגה אם הטכניקה יושבת טוב
לא רודפים משקלים - רק סינגלים נקיים
""", "strength", "strength", "load",
             notes="Take 15 mins, heavy single for the day @RPE 8-9\nRest 2:00 between heavy attempts\nתתחילו נמוך ותעלו בהדרגה אם הטכניקה יושבת טוב\nלא רודפים משקלים - רק סינגלים נקיים",
             items=[it("snatch", "Squat Snatch", reps=1, reps_text="1RM of the day")]),
        part("Snatch Balance", """
3 sets of 2 reps @light - moderate
rest 1:30
Focus on speed under the bar
""", "strength", "strength", "load", notes="Focus on speed under the bar\nRest 1:30", rounds=3,
             items=[it("snatch-balance", "Snatch Balance", reps=2, reps_text="3x2", note="@light - moderate")]),
        part("Metcon", """
AMRAP 12:
6 Power Snatches @42,5/30 kg
9 Box Jump Overs
12/10 Cal Echo Bike
""", "metcon", "amrap", "rounds_reps", time_cap_sec=720,
             items=[it("power-snatch", "Power Snatches", reps=6, load=(42.5, 30)),
                    it("box-jump-over", "Box Jump Overs", reps=9),
                    it("bike-erg", "Cal Echo Bike", cal=(12, 10))]),
        part("Accessory", """
3-4 Sets:
10-12 Diamond Push ups
20 Band Face Pulls
5-8 Strict Top Half Toes To Bar or Tuck ups
rest 1:20-2:00
""", "accessory", "rounds", "checkmark", notes="Rest 1:20-2:00\nStrict Top Half Toes To Bar or Tuck ups", rounds=3,
             items=[it("push-up", "Diamond Push ups", reps_text="10-12"),
                    it("face-pull", "Band Face Pulls", reps=20),
                    it("toes-to-bar", "Strict Top Half Toes To Bar", reps_text="5-8")]),
    ]},
    {"date": "2026-11-16", "dow": "Mon 16 Nov", "title": "Deadlift + Strict Press", "parts": [
        part("Deadlift Prep", """
2 Rounds:
10 Cat - Cow
5 Straight Leg Inchworm Push ups
10 Good Mornings @empty Bar
""", "warmup", "rounds", "checkmark", rounds=2,
             items=[it("cat-cow", "Cat - Cow", reps=10), it("inchworm", "Straight Leg Inchworm Push ups", reps=5),
                    it("good-morning", "Good Mornings", reps=10, note="@empty Bar")]),
        part("Deadlift", f"""
Week 12:
Find Your True 1RM
rest 3:00 between heavy attempts
{TEST_NOTE}
""", "strength", "strength", "load", notes=f"Week 12\nRest 3:00 between heavy attempts\n{TEST_NOTE}",
             items=[it("deadlift", "Deadlift", reps=1, reps_text="1RM")]),
        part("Strict Press", """
Week 12:
Find Your True 1RM
Rest: 3:00 !!!
בהצלחה!
""", "strength", "strength", "load", notes="Week 12\nRest: 3:00 !!!\nבהצלחה!",
             items=[it("strict-press", "Strict Press", reps=1, reps_text="1RM")]),
        part("Metcon", """
For Time:
3 Rounds:
400 m Run
15 T2B
12 Alternating DB Snatches @22,5/15 kg
TC: 14
*500/400 m Row instead of the run
""", "metcon", "for_time", "time", notes="*500/400 m Row instead of the run", rounds=3, time_cap_sec=840,
             items=[it("run", "Run", dist=400), it("toes-to-bar", "T2B", reps=15),
                    it("dumbbell-snatch", "Alternating DB Snatches", reps=12, load=(22.5, 15))]),
        part("Pendlay Row", """
4 Sets of 8-10 reps @moderate - heavy
rest 2:00 - 2:30
""", "accessory", "strength", "load", notes="Rest 2:00 - 2:30", rounds=4,
             items=[it("pendlay-row", "Pendlay Row", reps_text="8-10", note="@moderate - heavy")]),
        part("DB Lateral Raises", """
4 sets of 10-12 reps @moderate weight @RPE 6
rest 2:00 - 2:30
אפשרי לבצע בסופרסט עם משיכות
""", "accessory", "rounds", "load", notes="Rest 2:00 - 2:30\nאפשרי לבצע בסופרסט עם משיכות", rounds=4,
             items=[it("lateral-raise", "DB Lateral Raises", reps_text="10-12", note="@moderate weight @RPE 6")]),
    ]},
    {"date": "2026-11-17", "dow": "Tue 17 Nov", "title": "Clean & Jerk", "parts": [
        part("Clean Prep", CLEAN_PREP, "warmup", score="checkmark"),
        part("Squat Clean + Split Jerk", """
Week 12:
Take 15 mins and build up to a heavy single of 1 Squat Clean + 1 Split Jerk @RPE 8-9
rest 2:00 between heavy attempts
תתחילו נמוך ותעלו בהדרגה אם הטכניקה יושבת טוב
""", "strength", "strength", "load",
             notes="Take 15 mins, heavy single for the day @RPE 8-9\nRest 2:00 between heavy attempts\nתתחילו נמוך ותעלו בהדרגה אם הטכניקה יושבת טוב",
             items=[it("clean-and-jerk", "Squat Clean + Split Jerk", reps=1, reps_text="1+1")]),
        part("Front Squat", """
3 sets of 3 reps @75% of the new 1RM
rest 2:30
אחרי שבוע של מקסים - נפח קל, מהירות ועומק
""", "strength", "strength", "load", notes="Of the new 1RM from last week\nRest 2:30\nאחרי שבוע של מקסים - נפח קל, מהירות ועומק", rounds=3,
             items=[pct("front-squat", "Front Squat", 3, 3, 75)]),
        part("Strict Ring Dips", """
3 sets of 8-12 reps @2-3RIR
rest 2:30
""", "accessory", "rounds", "reps", notes="@2-3RIR\nRest 2:30", rounds=3,
             items=[it("ring-dip", "Strict Ring Dips", reps_text="8-12")]),
        part("Shoulder PRE-HAB", SHOULDER_PREHAB, "accessory", score="checkmark"),
        part("Metcon Optional", """
AMRAP 10:
5 Bar Muscle Ups
10 Wall Balls @9/6 kg
30 DU
""", "metcon", "amrap", "rounds_reps", time_cap_sec=600,
             items=[it("bar-muscle-up", "Bar Muscle Ups", reps=5), it("wall-ball", "Wall Balls", reps=10, load=(9, 6)),
                    it("double-under", "DU", reps=30)]),
    ]},
    {"date": "2026-11-18", "dow": "Wed 18 Nov — RECOVERY DAY", "title": "RECOVERY DAY", "parts": [
        part("RECOVERY DAY", """
MANDATORY MOBILITY AND SAUNA
IF YOU WANNA BE STRONG
TREAT YOURSELF
""", "cooldown", score="checkmark", notes="MANDATORY MOBILITY AND SAUNA\nIF YOU WANNA BE STRONG\nTREAT YOURSELF"),
    ]},
    {"date": "2026-11-19", "dow": "Thu 19 Nov", "title": "Bench + Pull-up retest", "parts": [
        part("Upper Body Prep", """
2 Rounds:
20 Band Pull Aparts
10 Scap Push ups
10 Banded Shoulder Dislocates
""", "warmup", "rounds", "checkmark", rounds=2,
             items=[it("band-pull-apart", "Band Pull Aparts", reps=20), it("push-up", "Scap Push ups", reps=10),
                    it(None, "Banded Shoulder Dislocates", reps=10)]),
        part("Bench Press", f"""
**Week 12:**
Find Your True 1RM
rest 2:30 - 3:00
{TEST_NOTE.splitlines()[0]}
""", "strength", "strength", "load", notes="Week 12\nRest 2:30 - 3:00\nבהצלחה!",
             items=[it("bench-press", "Bench Press", reps=1, reps_text="1RM")]),
        part("Strict Pull Ups", """
RETEST:
Track C:
1 set of Max Reps Strict Pull ups
Track B:
1 set of Max Reps Strict Pull ups
Track A:
Find your 1RM Weighted Strict Pull up
rest 3:00 between attempts
Score: Track C / B - reps. Track A - write the weight in the notes
""", "strength", "none", "reps", notes="Track C / B: 1 set of max reps\nTrack A: 1RM weighted strict pull up, write the weight in the notes\nRest 3:00 between attempts",
             items=[it("strict-pull-up", "Strict Pull ups", reps_text="Max reps")]),
        part("Gymnastics", """
EMOM 12:
1: 8-12 C2B
2: 45 sec easy Erg Bike
3: 5-10 m Handstand Walk ( 2 x 5 m )
חזרות יפות וטכניות בלי מלחמה
""", "skill", "emom", "none", notes="חזרות יפות וטכניות בלי מלחמה", time_cap_sec=720, interval_sec=60,
             items=[it("chest-to-bar-pull-up", "C2B", reps_text="8-12"), it("bike-erg", "Erg Bike", reps_text="45 sec easy"),
                    it("handstand-walk", "Handstand Walk", reps_text="5-10 m")]),
        part("Accessory", """
A) DB Concentration Curls:
3 sets of 10-12 reps each Arm @light - moderate
B)Single Arm Overhead Triceps Extension
3 sets of 10-12 reps each Arm @light - moderate
C) Banded Russian Twists
3 sets of 30 sec Each Side
""", "accessory", "rounds", "checkmark", rounds=3,
             items=[it("dumbbell-concentration-curl", "DB Concentration Curls", reps_text="10-12", per_side=True, note="@light - moderate"),
                    it("single-arm-overhead-triceps-extension", "Single Arm Overhead Triceps Extension", reps_text="10-12", per_side=True, note="@light - moderate"),
                    it("banded-russian-twist", "Banded Russian Twists", reps_text="0:30", per_side=True)]),
    ]},
    {"date": "2026-11-20", "dow": "Fri 20 Nov — Partner WOD", "title": "Partner WOD", "parts": [
        part("Warm Up", """
3 Rounds:
200 m Run
10 Air Squats
10 Push ups
5 Inchworms
""", "warmup", "rounds", "checkmark", rounds=3,
             items=[it("run", "Run", dist=200), it("air-squat", "Air Squats", reps=10), it("push-up", "Push ups", reps=10),
                    it("inchworm", "Inchworms", reps=5)]),
        part("Partner WOD", """
In Pairs:
For Time:
60/50 Cal Row
50 Wall Balls @9/6 kg
40 T2B
30 Power Cleans @60/42,5 kg
40 T2B
50 Wall Balls @9/6 kg
60/50 Cal Row
TC: 25
One works at a time, split the reps as you like
סוף מחזור - תהנו!
""", "metcon", "for_time", "time", notes="In pairs, one works at a time, split the reps as you like\nסוף מחזור - תהנו!", time_cap_sec=1500,
             items=[it("row", "Cal Row", cal=(60, 50)), it("wall-ball", "Wall Balls", reps=50, load=(9, 6)),
                    it("toes-to-bar", "T2B", reps=40), it("power-clean", "Power Cleans", reps=30, load=(60, 42.5)),
                    it("toes-to-bar", "T2B", reps=40), it("wall-ball", "Wall Balls", reps=50, load=(9, 6)),
                    it("row", "Cal Row", cal=(60, 50))]),
        part("Body Armor MUST DO", """
3 Sets:
A) Chest Supported Rear Delt Fly
12-15 reps @light
B) Dumbbell Bicep Curl
10-12 reps
C) Single Arm Dumbbell Tricep Kickback
12 reps each arm
""", "accessory", "rounds", "checkmark", rounds=3,
             items=[it(None, "Chest Supported Rear Delt Fly", reps_text="12-15", note="@light"),
                    it("dumbbell-curl", "Dumbbell Bicep Curl", reps_text="10-12"),
                    it("triceps-extension", "Single Arm Dumbbell Tricep Kickback", reps=12, per_side=True)]),
    ]},
    {"date": "2026-11-21", "dow": "Sat 21 Nov — REST DAY", "title": "REST DAY", "parts": [
        part("REST DAY", "FULL REST DAY", "cooldown", notes="FULL REST DAY"),
    ]},
]


def main():
    md = ["---", "track: rx-club", f"week_start: {WEEK}", "status: draft",
          "source: drafted by Claude from the track's history (Week 12 of the Aug–Nov cycle: test week)", "---", ""]
    out = []
    for d in DAYS:
        md.append(f"## {d['dow']}\n")
        src = []
        for i, p in enumerate(d["parts"]):
            letter = chr(ord("A") + i)
            md.append(f"### {letter}. {p['title']}\n{p['text']}\n")
            src.append(f"{letter}. {p['title']}\n{p['text']}")
        out.append({"date": d["date"], "title": d["title"], "source_text": "\n\n".join(src), "sections": [
            {k: v for k, v in p.items() if k != "text" and v is not None}
            for p in d["parts"]]})
    (HERE.parent / "weeks" / f"{WEEK}.md").write_text("\n".join(md).rstrip() + "\n")
    (HERE / f"{WEEK}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"{len(out)} days, {sum(len(d['sections']) for d in out)} parts")


main()
