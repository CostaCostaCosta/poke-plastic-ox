---
title: Ruins of Alph Hall
slug: ruinsofalph-b1f-hns
kind: Dungeon
act: 3
stage: "Act III side area — the dig reopens after Cinnabar"
depth: supporting
wiki: ruinsofalph-b1f-hns
maps: [RuinsOfAlph_B1F_hns]
status: implemented
---

# Ruins of Alph Hall

## Snapshot

One long hall of statues under the four chambers, in five aisles joined by gaps in the dividing walls. Unown drift here and nowhere else in the region. It is reached by the stair in the middle of the dig site or by falling from a Words Room, and the stair is the only way out. The donor's visitors, wandering Unown sprites, fossils, GS Ball and wall text are gone.

## Plot points

1. **A place to end up.** Every floor hole in the chambers lands here: Words Room 1 at `(5,6)`, Words Room 4 at `(21,6)`, Words Room 3 at `(5,23)`, Words Room 2 at `(21,23)`. The stair `(15,16)` returns to the dig site at `(21,21)`, so nobody is trapped.
2. **Unown, and nothing said about them.** The hall has a wild table of Unown only (`gPoxUURuinsOfAlphB1F`, Lv. 36-38). No report, no Pokédex mode, no count.
3. **One member of staff.** A surveyor by the stair `(19,16)` explains how the hall was found: people fell into it.
4. **Must not:** explain the statues, the carvings or the Unown; mention the Regis; place an item ball or a fossil (the GS BALL comes from the Trick House in this region).

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Stair | `(15,16)` | always | warps to the dig site `(21,21)` | keep |
| Surveyor | `(19,16)`, `PoxRuins_HallSurveyor` | always | "four holes in the ceiling, four of us who limp" | keep; dry, practical |
| Wild Unown | every aisle | always | `gPoxUURuinsOfAlphB1F`, Unown Lv. 36-38 | keep |

## Dialogue guidance

- The surveyor talks like someone who has filled in the accident form. The hall is a workplace hazard that turned out to be a find.

## Inspiration

- **Undercrofts found by accident:** a floor gives way during a survey and the survey has a new chapter.

## Implementation hooks

- Converted map from `plastic_ox/alpha/import_ruins_of_alph.py` (donor `RuinsOfAlph_B1F_hns`, tileset `gTileset_RuinsOfAlph_B1F_Hns`); the surveyor and the wild table from `plastic_ox/alpha/ruins_of_alph.py`; script in `plastic_ox/alpha/ruins_of_alph/RuinsOfAlph_B1F_hns.inc`.
- Demo check: `plastic_ox/demo/test_ruins_of_alph.py`.

## Open questions

- Should the statues carry a line of description, or stay silent as now?
