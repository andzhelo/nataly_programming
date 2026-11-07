# Week file format

File: `athletes/<name>/weeks/YYYY-MM-DD.md` (Sunday the week starts).

```
---
athlete: eddie
week_start: 2026-11-08
status: draft | approved | uploaded | published
days: [Sun, Mon, Wed, Thu]
---

## Sun 08 Nov — <focus>

### A. Warm-up (~10 min)
2 rounds: ...

### B. <Block name>
<prescription line, Nataly's notation>
Notes: <cues; Hebrew kept verbatim>
Load: <kg or RPE/RIR>

### C. Metcon — <format>
...
TC: <minutes>

### D. Accessories
...
```

Notation (as Nataly writes it; keep it):
- `Every 1:30 x 5: 3 reps` — interval sets
- `EMOM 6: 8 butterfly pull-ups`
- `3 sets of 8 reps @2RIR`, `@RPE7`, `@75%`
- `AMRAP 12`, `5 RFT`, `21-15-9`, `For time`, `TC: 24`
- `rest 1:00-1:30`
- Abbrev: RMU, BMU, HSW, HSPU, T2B, C2B, OHS, DU, PU, C&J, DL, RDL, RFT.

One block = one TrainHeroic exercise/circuit. The uploader maps `###` blocks to
TrainHeroic blocks in order; the prescription line goes to sets/reps/load fields
where it parses, and the rest goes into the exercise notes verbatim.
