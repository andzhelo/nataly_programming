#!/bin/sh
# One-time setup on a new machine (macOS / Linux; on Windows run the same three commands in PowerShell with .venv\Scripts\python).
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/playwright install chromium
echo "Now run: .venv/bin/python tools/th_login.py   (Nataly logs in once)"
