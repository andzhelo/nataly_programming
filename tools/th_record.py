"""Open TrainHeroic in the uploader's own browser profile and record all traffic.

Usage:
    .venv/bin/python tools/th_record.py [name]

- Opens a Chromium window on coachapp.trainheroic.com using a persistent profile at
  ~/.nataly_programming/th-profile (login survives between runs).
- Records every request/response into recordings/<name>.har (gitignored; contains
  session tokens, never commit or share it).
- Finishes when recordings/STOP appears (or the browser window is closed); the HAR is then written.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE = Path.home() / ".nataly_programming" / "th-profile"
name = sys.argv[1] if len(sys.argv) > 1 else "session"
har = Path(__file__).resolve().parent.parent / "recordings" / f"{name}.har"
har.parent.mkdir(parents=True, exist_ok=True)
PROFILE.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        str(PROFILE),
        headless=False,
        viewport={"width": 1400, "height": 900},
        record_har_path=str(har),
        record_har_content="embed",
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://coachapp.trainheroic.com/")
    stop = har.parent / "STOP"
    stop.unlink(missing_ok=True)
    print(f"\nBrowser open. Recording to {har}\nDo the steps in TrainHeroic. To finish, create the file {stop} (Claude does this).", flush=True)
    import time
    while not stop.exists():
        if not ctx.pages:
            break
        time.sleep(1)
    stop.unlink(missing_ok=True)
    ctx.close()
    print(f"Saved {har} ({har.stat().st_size // 1024} KB)")
