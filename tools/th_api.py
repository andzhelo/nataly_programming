"""Thin client for TrainHeroic's coach API, using the session from the uploader's
browser profile (~/.nataly_programming/th-profile). No passwords are handled here.

The coach web app authenticates every call with two headers:
    session-token: <value of the app-Session cookie>
    api-token: DISABLED
We read the cookie from the persistent Playwright profile that Nataly logged into
once (tools/th_record.py or tools/th_login.py).

Endpoints (observed 2026-11-07, unofficial and may change):
    GET  /v5/exerciseLibrary/all
    GET  /2.0/coach/athlete/calendar/edit/{athleteId}/{Y}/{M}/{D}   ~6-week window
    POST /2.0/coach/calendar/workout/createWorkoutForDay/{programId}/{Y}/{M}/{D}/0
    PUT  /3.0/coach/workout/{workoutId}                               title etc.
    POST /2.0/coach/calendar/saveProgramWorkoutSets                   [set]
    POST /2.0/coach/calendar/saveWorkoutSetExercises                  [exercise]
    POST /2.0/coach/calendar/workout/workoutSet/save/{setId}          circuit text
    POST /2.0/coach/calendar/removeProgramWorkout                     {programId,pwId}
"""
from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

API = "https://api.trainheroic.com"
PROFILE = Path.home() / ".nataly_programming" / "th-profile"
TOKEN_CACHE = Path.home() / ".nataly_programming" / "session-token"

# Set (block) types
SET_EXERCISES = 4   # list of tracked exercises (sets/reps/load)
SET_CIRCUIT = 5     # free text block (warm-up, metcon)
# param_1 types
P1_REPS = 3
P1_TIME = 4         # "mm:ss"
# param_2 types
P2_NONE = 0
P2_PERCENT = 2
P2_KG = 19


def read_token_from_profile() -> str:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=True)
        try:
            for c in ctx.cookies("https://api.trainheroic.com"):
                if c["name"] == "app-Session":
                    return c["value"]
        finally:
            ctx.close()
    raise SystemExit("No TrainHeroic session in the browser profile. Run tools/th_login.py first.")


def get_token(refresh: bool = False) -> str:
    if not refresh and TOKEN_CACHE.exists():
        return TOKEN_CACHE.read_text().strip()
    tok = read_token_from_profile()
    TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE.write_text(tok)
    TOKEN_CACHE.chmod(0o600)
    return tok


class TH:
    def __init__(self, token: str | None = None):
        self.token = token or get_token()

    def _call(self, method: str, path: str, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(API + path, data=data, method=method, headers={
            "session-token": self.token,
            "api-token": "DISABLED",
            "content-type": "application/json",
            "accept": "application/json",
            "origin": "https://coachapp.trainheroic.com",
            "referer": "https://coachapp.trainheroic.com/",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36",
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                txt = r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{method} {path} -> {e.code}: {e.read()[:300]!r}") from None
        return json.loads(txt) if txt.strip() else None

    # ---- read
    def me(self):
        return self._call("GET", "/user/simple")

    def library(self):
        return self._call("GET", "/v5/exerciseLibrary/all")

    def calendar(self, athlete_id: int, y: int, m: int, d: int):
        return self._call("GET", f"/2.0/coach/athlete/calendar/edit/{athlete_id}/{y}/{m}/{d}")

    # ---- write (all leave the session UNPUBLISHED)
    def create_session(self, program_id: int, y: int, m: int, d: int, title: str):
        pw = self._call("POST", f"/2.0/coach/calendar/workout/createWorkoutForDay/{program_id}/{y}/{m}/{d}/0")
        pw["title"] = title
        self._call("PUT", f"/3.0/coach/workout/{pw['workout_id']}", pw)
        return pw  # has id (programWorkout id) and workout_id

    def add_set(self, workout_id: int, order: int, title: str, kind: int, instruction: str = ""):
        body = [{"workout_id": workout_id, "order": order, "type": kind, "instruction": instruction,
                 "is_redzone": None, "redzone_type": 0, "exercises": [], "exerciseKeys": [],
                 "key": f"k::{order}", "title": title}]
        s = self._call("POST", "/2.0/coach/calendar/saveProgramWorkoutSets", body)[0]
        if kind == SET_CIRCUIT and instruction:
            s.update(instruction=instruction, plain_text=1)
            s = self._call("POST", f"/2.0/coach/calendar/workout/workoutSet/save/{s['id']}", s)
        return s

    def add_exercises(self, set_id: int, exercises: list[dict]):
        """exercises: [{exercise_id, title, order, instruction, p1_type, p1, p2_type, p2}]
        p1/p2 are lists per set (len = number of sets).

        Two-step save on purpose: TrainHeroic converts kg->lb when an exercise is
        CREATED with a kg load in one request, but keeps kg when an existing
        exercise is UPDATED with it (that is what the web app does)."""
        def item(ex, n, p1, p2, p2_type, existing=None):
            d = dict(existing or {})
            d.update({"exercise_id": ex["exercise_id"], "workout_set_id": set_id, "set_id": set_id,
                      "title": ex["title"], "instruction": ex.get("instruction", ""), "order": ex["order"],
                      "param_1_type": ex["p1_type"], "param_2_type": p2_type,
                      "workout_set_exercise_template_id": None, "no_sets": 0, "param_count": n, "set_num": n,
                      "key": d.get("id") or f"k::e{ex['order']}", "setKey": f"k::{set_id}", "eType": "e"})
            d.setdefault("tags", [])
            for i in range(1, 11):
                d[f"param_1_data_{i}"] = str(p1[i - 1]) if i <= len(p1) else ""
                d[f"param_2_data_{i}"] = str(p2[i - 1]) if i <= len(p2) else ""
            return d
        # step 1: create with reps only (param_2 empty, type 1 like the UI default)
        step1 = [item(ex, len(ex["p1"]), ex["p1"], [], 1) for ex in exercises]
        created = self._call("POST", "/2.0/coach/calendar/saveWorkoutSetExercises", step1)
        # step 2: update with loads (kg / % / none)
        step2 = [item(ex, len(ex["p1"]), ex["p1"], ex.get("p2") or [], ex.get("p2_type", P2_NONE), existing=c)
                 for ex, c in zip(exercises, created)]
        return self._call("POST", "/2.0/coach/calendar/saveWorkoutSetExercises", step2)

    def remove_session(self, program_id: int, pw_id: int):
        return self._call("POST", "/2.0/coach/calendar/removeProgramWorkout", {"programId": program_id, "pwId": pw_id})


if __name__ == "__main__":
    th = TH(get_token(refresh="--refresh" in sys.argv))
    me = th.me()
    print("logged in as:", {k: me.get(k) for k in ("id", "first_name", "last_name", "email", "role") if k in me} if isinstance(me, dict) else str(me)[:200])
