# Nataly's CrossFit programming

Nataly writes weekly programming for individual athletes and groups. Programs are
delivered through TrainHeroic (coach app) or SugarWOD. This repo is the source of
truth: athlete profiles, gym constraints, and every week ever written.

Scope right now: Eddie only.

## Layout

- `gym.md` — equipment and loading constraints that apply to every athlete.
- `docs/format.md` — how a week file is written (blocks, notation, loads).
- `athletes/<name>/profile.md` — goals, current levels, weaknesses, Nataly's
  standing corrections. Update it whenever she corrects something about the athlete.
- `athletes/<name>/weeks/YYYY-MM-DD.md` — one file per week, named by the Sunday it
  starts. Status line at the top: `draft`, `approved`, `uploaded`, `published`.
- `tools/` — uploader and log reader (TrainHeroic). See `tools/README.md`.

## Weekly workflow (per athlete)

1. Read `gym.md`, the athlete's `profile.md`, and the last two week files.
2. Pull the athlete's latest logs (loads, notes) and add anything new to `profile.md`
   under "Recent results".
3. Draft the new week into `athletes/<name>/weeks/<sunday>.md`, status `draft`.
   Follow `docs/format.md`. Every day starts with a ~10 min warm-up matched to the
   day. Order: warm-up → skill/gymnastics → lift(s) → metcon → accessories.
4. Show Nataly the draft. Apply her corrections to the week file AND, when a
   correction is about the athlete (ability, weakness, preference), to `profile.md`.
5. When she approves, set status `approved` and run the uploader. Everything goes to
   TrainHeroic UNPUBLISHED. Nataly reviews in the coach app and presses Publish.
6. Set status `uploaded`. Never publish on her behalf.

## Rules

- Loads in kg. Only 2.5 kg steps on barbells (see `gym.md`).
- Keep heavy pulling volume (RMU, weighted pull-ups) away from pulling-heavy metcons
  on the same day unless she asks for it.
- Nataly writes in shorthand mixed Hebrew/English. Keep her Hebrew cues verbatim in
  exercise notes (fix obvious typos, say so). Ask her which language athlete-facing
  notes should be in if unclear; default to the language she wrote that block in.
- When she writes "accessory of your choice" or "TC: ?", fill it in and list what
  you chose in the summary so she can veto.
- Do not add exercises to the TrainHeroic library without saying so in the summary.
