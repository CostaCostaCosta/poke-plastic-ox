---
title: Bellchime Trail
slug: bellchimetrail-hns
kind: Route
act: 3
stage: "Legendary sages return"
depth: supporting
wiki: bellchimetrail-hns
maps: [BellchimeTrail_hns]
flags: [FLAG_POX_ENTEI, FLAG_POX_HIDE_ARTICUNO, FLAG_POX_CAUGHT_RAIKOU, FLAG_POX_CAUGHT_REGIROCK, FLAG_POX_CAUGHT_REGICE, FLAG_POX_CAUGHT_REGISTEEL]
status: implemented
---

# Bellchime Trail

## Snapshot

The autumn path behind the Ecruteak sage office, entered only through the office's back door at `(8,36)`–`(8,38)`. Its paved walk ends at the Tin Tower door `(35,41)`. The donor's wandering Pokémon, lamps, Morty and item ball are gone, and so is its south seam into Ecruteak.

## Plot points

1. **The walk to the tower.** The keeper in `EcruteakCity_SageOffice2_hns` steps aside once five sages are home; the trail is the reward for that, a quiet stretch before the climb.
2. **One door.** `(35,41)` leads into `TinTower_1F_hns`; the door's solid bit was cleared on import so it works as an ordinary step-in door.

**Must not:** say "convergence"; explain why the tower is short; let anyone reach the trail before five sages are home.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Office door | `(8,36)`–`(8,38)` west arrows ↔ office warp 1 `(8,5)` | five sages home | arrives at `(8,37)` | keep |
| Tower door | `(35,41)` → `TinTower_1F_hns` `(9,17)` | always | step-in door | keep |

## Dialogue guidance

- The sages here are tired and relieved, not mystical. They talk about the job they just finished.

## Inspiration

- **Temple approach paths (sandō).** A paved walk between autumn trees that slows you down before a sacred building; the quiet is the point.

## Implementation hooks

- Converted map from `plastic_ox/alpha/import_tin_tower.py` (donor `BellchimeTrail_hns`), installed by `plastic_ox/alpha/tin_tower.py`; scripts in `data/scripts/plastic_ox_tin_tower.inc`.
- Demo check: `plastic_ox/demo/test_tin_tower.py`.

## Open questions

- None yet.
