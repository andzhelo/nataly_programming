# Tools

All scripts run with the repo's venv: `.venv/bin/python tools/<script>`. First time on a
machine: `./setup.sh`, then `tools/th_login.py` (Nataly logs in once; the session is kept
in `~/.nataly_programming/th-profile`, no password is ever stored by us).

| Script | What it does |
|---|---|
| `th_login.py` | One-time login in the uploader's own browser profile. |
| `upload_week.py <week-file> [--dry-run] [--replace] [--only DATE]` | Creates the week's sessions in TrainHeroic, UNPUBLISHED, then reads them back and verifies. Refuses unknown exercise names. Never touches published sessions. |
| `download_week.py <athlete> <sunday> [-o file]` | Writes a week file from what is in TrainHeroic. |
| `delete_week.py <athlete> <sunday>` | Deletes UNPUBLISHED sessions of that week (asks for confirmation). |
| `weekfile.py <week-file> [--json]` | Parses and summarises a week file (format check). |
| `th_record.py [name]` | Opens the profile browser and records traffic to `recordings/*.har` for reverse-engineering. HARs contain session tokens: gitignored, never share. |
| `publish_sinergy.py <week-file> [--dry-run] [--publish] [--only DATE] [--track NAME]` | Posts a week (athlete or track file) to Sinergy's `week-publish` function. Login from `SINERGY_LOGIN`/`SINERGY_PASSWORD` or a prompt; target from `SINERGY_URL`/`SINERGY_ANON_KEY` (default: the hosted project). |
| `th_api.py` | The API client. `aliases.json`: Nataly's shorthand -> library exercise names. |

Timing: TrainHeroic answers in ~3 s per call; a 4-day week uploads in about 3 minutes
(days run in parallel).

## How auth works

The coach web app sends `session-token: <app-Session cookie>` and `api-token: DISABLED`
on every call. `th_api.get_token()` reads that cookie from the browser profile and caches
it in `~/.nataly_programming/session-token`. If calls start failing with 401, run
`th_login.py` again.

## API notes (unofficial, observed 2026-11-07)

- Set types: 4 = exercise list, 5 = plain text (warm-up, metcon).
- Param types: 3 reps, 4 time mm:ss, 1 weight lb, 19 weight kg, 2 weight %, 24 rep range, 14 RPE, 18 seconds.
- Creating an exercise with a kg load in one request converts it to lb. Create with reps
  only, then update the same record with kg (two calls). `th_api.add_exercises` does this.
- `calendar/edit/{athlete}/{y}/{m}/{d}` returns roughly the surrounding 6 weeks.
- Not yet reverse-engineered: reading Eddie's logged results (loads/notes he enters).
