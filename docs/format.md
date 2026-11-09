# Week file format

One file per athlete-week: `athletes/<name>/weeks/YYYY-MM-DD.md` (the Sunday the
week starts). `tools/upload_week.py` turns it into TrainHeroic sessions and
`tools/download_week.py` writes one from TrainHeroic, so the format round-trips.

```
---
athlete: eddie
athlete_id: 2615164
program_id: 4414542
week_start: 2026-11-08
status: draft            # draft | approved | uploaded | published
---

## Sun 08 Nov — Squat + RMU          <- "## <Dow> <day> <Mon> — <session title>"

### A. Warm up                        <- a block = one TrainHeroic set, letters in order
2 rounds:                             <- no "- " lines => plain-text block (type 5)
250 m Row
10 Scap Pull-ups

### B. Strength                       <- has "- " lines => exercise block (type 4)
Both in 2.5 kg steps.                 <- lines before the first "- " = block instruction
- Back Squat: 5 x 3 @ 77.5 kg         <- "- <Library name>: <sets> x <reps> [@ <loads> kg|%]"
  rest 2:00                           <- indented lines = exercise notes (Hebrew welcome)
  שים לב לעומק
- High Hang Squat Snatch: 5 x 3 @ 40, 40, 42.5, 45, 45 kg
- Copenhagen Plank: 3 x 0:20          <- m:ss reps = time
- Toes to Bar: 5 x 10
  EMOM 5: 10 T2B unbroken
- Strict Press: 3 x 8
  @ 2RIR, rest 2:00                   <- RPE / RIR go in notes, not in the load field
```

Rules
- Exercise names must exist in Nataly's TrainHeroic library (case-insensitive) or in
  `tools/aliases.json` (her shorthand -> library name). The uploader refuses to run
  with an unknown name and prints the closest library matches.
- Reps may be one number (`5 x 3`) or a list per set (`4 x 5, 5, 3, 3`). Loads likewise.
  Loads are kg or %, nothing else goes in the load field.
- Barbell loads in 2.5 kg steps (see `gym.md`).
- Notes to the athlete default to Hebrew. Short technical notes (rest times, tempo,
  "@ RPE 7") may stay in English; that is how Nataly writes them.
- Everything uploads UNPUBLISHED. Nataly publishes in the coach app.

## Track weeks (Sinergy)

`tracks/<track>/weeks/YYYY-MM-DD.md` uses the same body. Frontmatter:

```
---
track: rx-club
week_start: 2026-11-15
status: draft            # draft | approved | published (in Sinergy)
---
```

Group loads go in the text as `42.5/30 kg` (men/women). Plain-text blocks are fine for metcons
and warm-ups; Sinergy reads them and keeps the text as written. `tools/publish_sinergy.py`
sends the file.
