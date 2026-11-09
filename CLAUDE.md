# Nataly's CrossFit programming

Nataly writes weekly programming for individual athletes and groups. Programs are
delivered through TrainHeroic (coach app) or SugarWOD. This repo is the source of
truth: athlete profiles, gym constraints, and every week ever written.

Scope right now: Eddie (TrainHeroic) and the Rx Club group track (Sinergy).

## Tracks (group programming → Sinergy)

- `tracks/<track>/weeks/YYYY-MM-DD.md` — one file per week, same format as athlete weeks with
  `track:` instead of `athlete:` in the frontmatter. `tracks/rx-club/weeks/` holds every Rx Club
  week since 2019, written from the SugarWOD export (plain-text blocks, exactly as Nataly wrote
  them; status `published`). New weeks are drafted here the same way as athlete weeks.
- Publish a week into Sinergy with `.venv/bin/python tools/publish_sinergy.py <week-file>`
  (UNPUBLISHED in Sinergy until Nataly presses Publish in the console; `--publish` to do it at
  once, `--dry-run` to only parse). Repeating a week updates the same days in place.
- Loads for a group are written `@ 42.5/30 kg` (men/women) inside the text; Sinergy's reader
  understands that. Exercise blocks (`- Name: S x R @ load`) become structured rows.

## Layout

- `gym.md` — equipment and loading constraints that apply to every athlete.
- `docs/format.md` — how a week file is written (blocks, notation, loads).
- `athletes/<name>/profile.md` — goals, current levels, weaknesses, Nataly's
  standing corrections. Update it whenever she corrects something about the athlete.
- `athletes/<name>/weeks/YYYY-MM-DD.md` — one file per week, named by the Sunday it
  starts. Status line at the top: `draft`, `approved`, `uploaded`, `published`.
- `tools/` — TrainHeroic scripts. See `tools/README.md`. Run them with `.venv/bin/python`.

## Weekly workflow (per athlete)

1. Read `gym.md`, the athlete's `profile.md`, and the last two week files.
2. Pull the athlete's latest logs (loads, notes) and add anything new to `profile.md`
   under "Recent results". (Log reading is not scripted yet; ask Nataly or read the
   coach app.)
3. Draft the new week into `athletes/<name>/weeks/<sunday>.md`, status `draft`.
   Follow `docs/format.md`. Every day starts with a ~10 min warm-up matched to the
   day. Order: warm-up → skill/gymnastics → lift(s) → metcon → accessories.
4. Show Nataly the draft. Apply her corrections to the week file AND, when a
   correction is about the athlete (ability, weakness, preference), to `profile.md`.
5. When she approves, set status `approved` and run
   `.venv/bin/python tools/upload_week.py <week-file>` (use `--dry-run` first if unsure).
   Everything goes to TrainHeroic UNPUBLISHED and is verified by read-back; the script
   sets status `uploaded`. Nataly reviews in the coach app and presses Publish.
6. Never publish on her behalf. To redo a week before she publishes: `--replace`.

## Rules

- Loads in kg. Only 2.5 kg steps on barbells (see `gym.md`).
- Keep heavy pulling volume (RMU, weighted pull-ups) away from pulling-heavy metcons
  on the same day unless she asks for it.
- Notes to the athlete default to Hebrew. Short technical notes (rest times, tempo,
  "@ RPE 7", "EMOM 5") may stay in English, that is how Nataly writes them. Keep her
  Hebrew cues verbatim (fix obvious typos, say so).
- Exercise names in week files must be TrainHeroic library names (or `tools/aliases.json`).
  When drafting, check with `tools/weekfile.py` and `upload_week.py --dry-run`.
- When she writes "accessory of your choice" or "TC: ?", fill it in and list what
  you chose in the summary so she can veto.
- Do not add exercises to the TrainHeroic library without saying so in the summary.
