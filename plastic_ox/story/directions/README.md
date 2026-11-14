# Direction bundles

One markdown bundle per hand-off, plus a JSON sidecar with the same facts. These
are written by the editor's Direction tab or by
`python3 plastic_ox/story/direction.py`.

```text
2026-11-13-103126-ecruteakcity-hns.md
2026-11-13-103126-ecruteakcity-hns.json
```

## What a bundle contains

- **How to use this bundle** — the agent contract: story bible wins, implement
  target behavior, never edit generated files, finish the note and run log.
- **Direction from the designer** — the brief typed in the editor.
- **Per note** — path, wiki page, act/stage, status, maps, flags, trainers,
  items, the unified diff against `HEAD`, the Key interactions table, open
  questions, grounded map facts, and validation at export time.
- **Verification and definition of done** — the commands and the closure
  criteria.

The diff is the design intent; the note is the context; the story bible
(`plastic_ox/plastic_ox_story_v7.md`) is authoritative on lore.

## Hand-off

Point the implementing agent at one file:

```text
Read plastic_ox/story/directions/2026-11-13-103126-ecruteakcity-hns.md and
implement it as direction for the game. Treat the note diff as design intent;
the v7 story bible is authoritative on lore. Update the note status and add a
run log when done.
```

The JSON sidecar has the same note list, diff text, interaction rows, map facts,
and validation in a form a script or agent tool can parse.

## Housekeeping

Bundles are cheap and intentionally kept as a trail. Delete old ones when they
are fully implemented and logged in `plastic_ox/story/runs/`. Do not hand-edit a
bundle after export; write a new one from the updated note instead.
