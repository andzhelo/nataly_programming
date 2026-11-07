# Tools (planned)

## Why no API key is needed

TrainHeroic has no public API, but the coach web app is itself a client of
TrainHeroic's backend. When Nataly is logged in, her browser holds a session
(cookies / bearer token) and every click in the coach app becomes an HTTP request
authenticated by that session. That session is the "key". Claude's current chat
already works this way: it drives her logged-in browser.

The uploader will do the same thing, two possible ways:

1. **Playwright UI replay** (default, robust): a script opens a persistent Chrome
   profile where Nataly logged in once, and fills the coach app's forms from a
   week file. Same actions Claude does by hand today, but in seconds and
   deterministic.
2. **Direct internal API** (faster, if simple): record the requests the coach app
   sends while adding one exercise, then have the script send the same requests
   with the session token. Unsupported by TrainHeroic and may break on their
   updates, so (1) stays as fallback.

Both leave sessions UNPUBLISHED. Nataly publishes.

## Planned scripts

- `upload_week.py <week-file>` — parses `athletes/<name>/weeks/<date>.md`, creates
  the sessions in TrainHeroic unpublished, reads them back and diffs against the
  file.
- `read_logs.py <athlete> <from-date>` — pulls logged loads/notes into
  `profile.md` "Recent results".

## Status

Not built yet. Next step: one recording session with Nataly's TrainHeroic login
in Chrome on this Mac (see the main conversation).
