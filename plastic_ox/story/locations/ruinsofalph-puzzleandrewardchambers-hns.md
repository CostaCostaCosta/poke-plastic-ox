---
title: Ruins of Alph Chambers
slug: ruinsofalph-puzzleandrewardchambers-hns
kind: Dungeon
act: 3
stage: "Act III side area — the dig reopens after Cinnabar"
depth: supporting
wiki: ruinsofalph-puzzleandrewardchambers-hns
maps: [RuinsOfAlph_PuzzleAndRewardChambers_hns]
flags: [FLAG_POX_CAUGHT_REGIROCK, FLAG_POX_CAUGHT_REGICE, FLAG_POX_CAUGHT_REGISTEEL]
trainers: [TRAINER_PLASTIC_OX_REGIROCK_SAGE, TRAINER_PLASTIC_OX_REGICE_SAGE, TRAINER_PLASTIC_OX_REGISTEEL_SAGE]
items: [ITEM_ANCIENT_ROCK_TABLET, ITEM_ANCIENT_ICE_TABLET, ITEM_ANCIENT_STEEL_TABLET]
status: implemented
---

# Ruins of Alph Chambers

## Snapshot

Four brick rooms on one map, each entered from its own door on the dig site. Three have a back wall that opens for one ancient tablet, and behind it a second room where a sage keeps watch beside a Regi. These are the Regis that used to sit in the Route 127 island caves; their tablets, badge gates and caught flags are unchanged. The donor's sliding puzzles, floor holes, item balls, statue text and Words Rooms are gone.

## Plot points

1. **A wall that takes a tablet.** Each chamber's back wall is plain until the player carries its tablet; then the doorway is open when the room loads. North chamber `(21,1)`: `ITEM_ANCIENT_ROCK_TABLET`. South-west `(5,18)`: `ITEM_ANCIENT_STEEL_TABLET`. South-east `(21,18)`: `ITEM_ANCIENT_ICE_TABLET`. Examining the wall describes the hollow, or the open doorway.
2. **The sage decides, not the door.** In the back room the sage and the Regi share one script. Without the tablet, or below the badge gate (5 for Regirock, 6 for Regice and Registeel), the answer is "the ancient power remains sealed". With both, the sage battles; beating the sage earns the catch, and `FLAG_POX_CAUGHT_REGIROCK` / `_REGICE` / `_REGISTEEL` removes both for good and sends the sage home to Ecruteak.
3. **The fourth room is just a room.** The west chamber has the same panel and a plain brick back wall. It is there so the site is not a checklist.
4. **Must not:** start a sliding puzzle, drop the player through the floor, mention Unown or a report, or explain what the Regis are.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Back wall, north | `(21,1)` → back room `(20,43)` | `ITEM_ANCIENT_ROCK_TABLET` held | open doorway on load; sealed text without it | keep |
| Back wall, south-west | `(5,18)` → back room `(4,60)` | `ITEM_ANCIENT_STEEL_TABLET` held | open doorway on load; sealed text without it | keep |
| Back wall, south-east | `(21,18)` → back room `(20,60)` | `ITEM_ANCIENT_ICE_TABLET` held | open doorway on load; sealed text without it | keep |
| Regirock and sage | `(21,37)`, `(20,39)` | tablet + `FLAG_BADGE05_GET` | sage battle `TRAINER_PLASTIC_OX_REGIROCK_SAGE`, then Regirock Lv. 50 | keep |
| Registeel and sage | `(5,54)`, `(4,56)` | tablet + `FLAG_BADGE06_GET` | sage battle `TRAINER_PLASTIC_OX_REGISTEEL_SAGE`, then Registeel Lv. 55 | keep |
| Regice and sage | `(21,54)`, `(20,56)` | tablet + `FLAG_BADGE06_GET` | sage battle `TRAINER_PLASTIC_OX_REGICE_SAGE`, then Regice Lv. 55 | keep |
| West back wall | `(5,1)` | always | "plain brick, no hollow, no seam" | keep, or give the room a use |
| Tile panels | `(20,5)`/`(21,5)`, `(4,5)`/`(5,5)`, `(4,22)`/`(5,22)`, `(20,22)`/`(21,22)` | always | solid; one line each, no puzzle | keep |

## Dialogue guidance

- The walls and panels are described the way a careful visitor would: what the surface looks like, what has been done to it. No voice from the stone.
- The sages keep the lines they had on Route 127; "these inscriptions led me here" suits the ruins better than it suited the caves.

## Inspiration

- **Sealed side rooms in real tombs:** a blocked doorway with a recess cut for something that is no longer there.

## Implementation hooks

- Converted map from `plastic_ox/alpha/import_ruins_of_alph.py` (donor `RuinsOfAlph_PuzzleAndRewardChambers_hns`); actors, wall signs and scripts from `plastic_ox/alpha/ruins_of_alph.py` and `plastic_ox/alpha/ruins_of_alph/RuinsOfAlph_PuzzleAndRewardChambers_hns.inc`.
- The battle scripts are unchanged in `plastic_ox/alpha/tournament/events.inc` (`data/scripts/plastic_ox_tournament.inc`); `plastic_ox/alpha/tournament.py` now only clears the Regis out of `DesertRuins`, `IslandCave` and `AncientTomb`.
- Demo checks: `plastic_ox/demo/test_ruins_of_alph.py`; `plastic_ox/demo/test_regi_caves.py` covers the emptied Route 127 caves.

## Open questions

- Should the three tablets be spent when their wall opens, or stay key items as now?
- The west chamber and all four panels are flavour only. Is that enough?
