---
title: Route 38
slug: route38-hns
kind: Route
act: 2
stage: "4 — Ecruteak and the Burned Tower"
depth: supporting
wiki: route38-hns
maps: [Route38_hns]
also_maps: [Gate_EcruteakCity_Route38_hns]
items: [ITEM_HP_UP, ITEM_MAX_POTION]
status: drafted
---

# Route 38

## Snapshot

A climbing dairy road west of Ecruteak — pasture, dry-stone walls, a milk farm locals mention before they mention the mountain. Nobody can walk it: the gatehouse that should join it to `EcruteakCity_hns` became the League checkpoint and now has one warp back into town, so this map is an orphan with nine NPCs and three lines between them. Treat it as an audit, not a story node.

## Plot points

1. **Currently unreachable.** `Route38_hns` has no connections, and its only warp at `(43,16)` points at warp index 1 of `Gate_EcruteakCity_Route38_hns`, which has warp index 0 only.
2. **Why.** The gatehouse runs `PoxLeague_Checkpoint` on `(4,4)`–`(4,6)` to send eight-badge players to `MAP_PLASTIC_OX_VICTORY_ROAD`. Ecruteak's west road became the League road, and the farmland behind it lost its purpose.
3. **Keep or retire, honestly.** If kept, its identity is dairy logistics — milk runs, feed prices, a cooler that broke in summer — the correct register for scenery on the way to a locked gate. If retired, note that `plastic_ox/artifact_cleanup.md` lists this route among unprotected candidates *and* lists the gatehouse, which is wrong: the gatehouse is live.

**Must not:** invent a beat, gate, or legendary sighting here; place a quest NPC on an unreachable map; delete the gatehouse because the route beside it is unused.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Nine NPCs, three lines | `(39,7)`, `(28,12)`, `(15,6)`, `(13,28)`, `(2,7)`, `(38,29)`, `(26,4)`, `(35,4)` | always | milk-farm / rocky-ground / hikers lines repeated across eight bodies | one line each, or delete the map |
| Ball with a mouth | `(1,30)`, `OBJ_EVENT_GFX_POKE_BALL` running `Route38_EventScript_Npc9` | always | an item-ball sprite that talks like a hiker | a defect, not a hidden item: `Common_EventScript_FindItem` or remove |
| West warp | `(43,16)` → gatehouse warp 1 | always | destination warp index does not exist | repoint at the gatehouse or remove with the map |

## Dialogue guidance

- **People who work outdoors and are mildly bored:** dairy, weather, feed, a late delivery; no lore, no tower talk. Whoever speaks for the farm speaks in quantities — litres, crates, churns per truck, kept short enough to read while walking.

> TANKER DRIVER: Two runs before the light, then I'm done. The road up to the gate is easy; it's the barn lane that eats the tires.

> FARM KID: The Miltank know the truck now. They line up when they hear it. Nobody taught them that.

> WALL MENDER: Dry stone. No mortar, no cement, and every spring I put back the same six metres.

- **Do not:** mention the League gate as a mystery, the tower, or anything the player cannot reach.

## Inspiration

- **Hokkaido dairy country:** long fenced pasture, a milk-vending machine at a crossroads, fog hiding the treeline. Converts to the tanker driver and the farm kid; GSC Route 38's MooMoo farm supplies the reason to stop at all.

## Implementation hooks

- Wiki page: `route38-hns.html`; maps `Route38_hns` (`MAP_ROUTE38_HNS`) and `Gate_EcruteakCity_Route38_hns` (`MAP_GATE_ECRUTEAK_CITY_ROUTE38_HNS`).
- Scripts: `data/maps/Route38_hns/scripts.inc` (`Route38_EventScript_Npc1`–`Npc9`), `data/scripts/plastic_ox_league.inc` (`PoxLeague_Checkpoint`, `PoxLeague_GateGuide`).
- Hidden `ITEM_HP_UP` at `(41,7)` and `ITEM_MAX_POTION` at `(8,24)` are pickups on a map nobody can reach.
- Known gaps: NPC dialogue on an item-ball sprite; eight NPCs share three strings; the only warp targets a warp index the gatehouse does not have; the live gatehouse is mis-listed as deletable.

## Open questions

- Keep Route 38 as a farmland connector, or retire it and let the gatehouse be the whole west exit? Today it costs nine NPCs and two hidden items to say nothing.
