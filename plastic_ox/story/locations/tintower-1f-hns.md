---
title: Tin Tower 1F
slug: tintower-1f-hns
kind: Dungeon
act: 3
stage: "Legendary sages return"
depth: supporting
wiki: tintower-1f-hns
maps: [TinTower_1F_hns]
flags: [FLAG_POX_CAUGHT_MOLTRES]
status: implemented
---

# Tin Tower 1F

## Snapshot

The tower's single interior floor: a statue hall with the ladder at `(9,4)` straight to the roof. The donor's 2F–9F are not imported. The tower is kept short on purpose, and the donor's 3F–6F could not be climbed anyway.

## Plot points

1. **Straight up.** `(9,17)` returns to Bellchime Trail; the ladder `(9,4)` opens onto `TinTower_RoofDay_hns` `(10,14)`.

**Must not:** say "convergence"; explain why the tower is short; let anyone reach the trail before five sages are home.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Trail door | `(9,17)` → `BellchimeTrail_hns` `(35,41)` | always | south arrow exit | keep |
| Roof ladder | `(9,4)` → `TinTower_RoofDay_hns` `(10,14)` | always | ladder | keep |

## Dialogue guidance

- The sages here are tired and relieved, not mystical. They talk about the job they just finished.

## Inspiration

- **Pagoda ground halls.** Statues of patrons line the walls, and a plain ladder leads straight up. Nothing is hidden.

## Implementation hooks

- Converted map from `plastic_ox/alpha/import_tin_tower.py` (donor `TinTower_1F_hns`), installed by `plastic_ox/alpha/tin_tower.py`; scripts in `data/scripts/plastic_ox_tin_tower.inc`.
- Demo check: `plastic_ox/demo/test_tin_tower.py`.

## Open questions

- None yet.
