---
title: Tin Tower Roof
slug: tintower-roofday-hns
kind: Dungeon
act: 3
stage: "Legendary sages return"
depth: supporting
wiki: tintower-roofday-hns
maps: [TinTower_RoofDay_hns]
flags: [FLAG_POX_CAUGHT_MOLTRES]
trainers: [TRAINER_PLASTIC_OX_MOLTRES_SAGE]
status: implemented
---

# Tin Tower Roof

## Snapshot

The open roof, where the last sage MORTY sent out has stayed with Moltres. The donor's Ho-Oh and Kimono scene is removed.

## Plot points

1. **The Moltres sage.** The sage at `(10,10)` (`TRAINER_PLASTIC_OX_MOLTRES_SAGE`, Lv55 ADV OU team ending in Moltres) and Moltres at `(10,8)` share `PoxTinTower_MoltresSage` (`pox_legendary_sage`). Winning lets any ball catch Moltres; the catch sets `FLAG_POX_CAUGHT_MOLTRES` and both leave.

**Must not:** say "convergence"; explain why the tower is short; let anyone reach the trail before five sages are home.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Moltres sage | `(10,10)` and Moltres `(10,8)` `PoxTinTower_MoltresSage` | `FLAG_POX_CAUGHT_MOLTRES` hides both | battle, then reward capture | keep |
| Ladder down | `(10,14)` → `TinTower_1F_hns` `(9,4)` | always | ladder | keep |

## Dialogue guidance

- The sages here are tired and relieved, not mystical. They talk about the job they just finished.

## Inspiration

- **Rooftop fire watches.** A keeper who stayed on a high roof through the season, sitting beside a bird made of fire.

## Implementation hooks

- Converted map from `plastic_ox/alpha/import_tin_tower.py` (donor `TinTower_RoofDay_hns`), installed by `plastic_ox/alpha/tin_tower.py`; scripts in `data/scripts/plastic_ox_tin_tower.inc`.
- Demo check: `plastic_ox/demo/test_tin_tower.py`.

## Open questions

- None yet.
