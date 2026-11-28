---
title: Dark Cave North Side
slug: darkcave-northside-hns
kind: Cave
act: 5
stage: "15 — Blackthorn"
depth: supporting
wiki: darkcave-northside-hns
maps: [DarkCave_NorthSide_hns]
flags: [FLAG_POX_DARKCAVE_NORTH_BLACKGLASSES, FLAG_POX_DARKCAVE_NORTH_STARPIECE, FLAG_POX_DARKCAVE_NORTH_BIGMUSHROOM, FLAG_POX_DARKCAVE_NORTH_REVIVE]
items: [ITEM_BLACK_GLASSES, ITEM_STAR_PIECE, ITEM_BIG_MUSHROOM, ITEM_REVIVE]
status: implemented
---

# Dark Cave North Side

## Snapshot

The Blackthorn half of Dark Cave, a 57×44 HNS cave entered from the mouth at the top of Route 45 (`Route45_hns` `(14,4)`). It runs downhill to the door on the island platform in `DarkCave_SouthSide_hns` `(34,6)`. It is a one-way descent, following the map bible's rule that Route 45/46 is a late-game downhill return: west-facing ledges at `(10,33–36)` drop the player into the small room by the south door, and nothing climbs back up. A player who surfs to the platform from the early cave can step through the door, but only reaches that room, so it never opens an early path to Blackthorn.

## Plot points

1. **The return road.** It's a quiet way down from Blackthorn into the early world, with no NPCs and no battles.
2. **The dark is stronger here.** Time-of-day UU tables at Lv 33–37: GOLEM, SANDSLASH everywhere; GLIGAR and GRANBULL/NIDOQUEEN in the morning, GLIGAR, SOLROCK and NIDOKING by day, MISDREAVUS, LUNATONE and NIDOQUEEN at night. Surfing the lake gives QUAGSIRE, GOLDUCK, LANTURN and a rare OMASTAR. Rock Smash adds GOLEM, SANDSLASH, GLIGAR and SOLROCK/LUNATONE.
3. **Pockets.** Item balls: BLACK GLASSES `(13,33)` in the room below the ledges, STAR PIECE `(31,31)`. Hidden: BIG MUSHROOM `(31,16)`, REVIVE `(7,21)`.

**Must not:** add an uphill route from the south door to Route 45; stage a story scene; explain the merged region.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Route 45 mouth | `(45,9)` warp 0 | always | to `Route45_hns` warp 0 `(14,4)` | keep |
| South door | `(6,38)` warp 1 | always | to `DarkCave_SouthSide_hns` warp 2 `(34,6)`, the island platform | keep |
| One-way ledges | `(10,33–36)` `MB_JUMP_WEST` | always | can drop west, can't climb east | keep |
| Item balls | `(13,33)`, `(31,31)` | `FLAG_POX_DARKCAVE_NORTH_BLACKGLASSES`, `FLAG_POX_DARKCAVE_NORTH_STARPIECE` | `finditem` | keep |
| Cracked rocks | `(28,5)`, `(5,6)` | `FLAG_TEMP_1`, `FLAG_TEMP_2` | `EventScript_RockSmash` | keep |

## Dialogue guidance

- Nobody speaks here. If a voice is ever added, it belongs at the Route 45 mouth: a hiker on the way down, brief and practical, matching the South Side's register.

## Inspiration

- **Gen 2 Dark Cave's Blackthorn half:** the darker, deeper end of the same cave, with tougher wild POKéMON and nothing to explain.
- **Mountain descents:** a road you only take downhill, where ledges do the talking.

## Implementation hooks

- Maps: `DarkCave_NorthSide_hns` (`MAP_DARK_CAVE_NORTH_SIDE_HNS`), ported from pokehns-expansion with its HNS layout unchanged; neighbours `Route45_hns` warp 0 and `DarkCave_SouthSide_hns` warp 2.
- Scripts: `data/maps/DarkCave_NorthSide_hns/scripts.inc`.
- Encounters: `gPoxUUDarkCaveNorthSideHns_Morning`/`_Day`/`_Night` in `src/data/wild_encounters.json`; checkpoint `blackthorn` in `plastic_ox/tools/pox_progression.py`.
