"""One-time login: opens TrainHeroic in the uploader's own browser profile.
Nataly logs in herself; the session is kept in ~/.nataly_programming/th-profile.
Close the window when the coach calendar is visible. Nothing is recorded.

    .venv/bin/python tools/th_login.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from th_api import PROFILE, TOKEN_CACHE, get_token

PROFILE.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=False, viewport={"width": 1400, "height": 900})
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://coachapp.trainheroic.com/")
    print("Log in, wait for the calendar, then close the browser window.", flush=True)
    try:
        page.wait_for_event("close", timeout=0)
    except Exception:
        pass
    try:
        ctx.close()
    except Exception:
        pass
TOKEN_CACHE.unlink(missing_ok=True)
print("saved session; token ok:", bool(get_token(refresh=True)))
