---
title: Route 46
slug: route46-hns
kind: Route
act: 1
stage: "0 — Opening network"
depth: supporting
wiki: route46-hns
maps: [Route46_hns]
flags: [FLAG_POX_HIDDEN_R46_REVIVE, FLAG_POX_DAILY_R46_SITRUS, FLAG_POX_DAILY_R46_LIECHI]
items: [ITEM_REVIVE, ITEM_SITRUS_BERRY, ITEM_LIECHI_BERRY]
trainers: [TRAINER_PLASTIC_OX_ROUTE46, TRAINER_PLASTIC_OX_ROUTE46_ERIN]
status: drafted
---

# Route 46

## Snapshot

A 27×46 scree slope that only goes one way: down. The player enters from the gate at `(10,40)`/`(11,40)` or from the Dark Cave mouth at `(20,11)`, and learns at the sign `(11,35)` that the ledges are descent-only. Two Lv.7 trainers hold the top of the slope, three walkers dot the way down, and a Revive plus a Sitrus and Liechi tree reward the drop. It is the first road in the game that tells the player they cannot go back; the emotional note is gravity.

## Plot points

1. **The gate is a door, not a check.** `(10,40)` and `(11,40)` both warp to `Gate_Route29_Route46_hns` (warp 0) with no flag and no officer on this side. The gatehouse belongs to Route 29's note; this note owns the slope.
2. **Descent only.** The sign at `(11,35)` states it; Ted at `(14,36)` says a short walk still counts as a hike; Bailey at `(19,25)` came down and refuses the climb. The rule is given three times by three objects and never by a tutorial. A player entering from the gate is told, three steps in, that the road above is one-way.
3. **The two trainers sit at the top.** `(6,18)` runs `TRAINER_PLASTIC_OX_ROUTE46` (Camper: Machop, Geodude, Sandshrew, Bagon, Numel, Phanpy, all Lv.7); `(4,18)` runs `TRAINER_PLASTIC_OX_ROUTE46_ERIN` (Picnicker: Onix, Larvitar, Lv.7). They are met coming down out of the cave, so the battle is the price of the shortcut, not a gate on the way in. Both are avoidable.
4. **The cave mouth is the mountain door.** `(20,11)` warps to `DarkCave_SouthSide_hns` (warp 1); that cave's other mouth is `Route2_Frlg` at `(17,11)`, in the north half of the Route 2 climb, south of the hiker gate at `(8,0)`. The loop is Route 2 → cave → Route 46 → gate → Route 29, and it cannot be walked backwards.
5. **First daily fruit.** Sitrus at `(9,11)` and Liechi at `(11,11)`, five berries a day via `pox_fruit_tree` (`FLAG_POX_DAILY_R46_SITRUS`, `FLAG_POX_DAILY_R46_LIECHI`); `ITEM_REVIVE` at `(2,21)` (`FLAG_POX_HIDDEN_R46_REVIVE`).
6. **The wild table is rock and bone.** Lv4–6 Geodude, Rattata, Machop, Sandshrew, Rhyhorn, Cubone, Numel, Bagon, plus Phanpy in the morning, Slugma by day and Zubat at night. Bagon at Lv4 is a dragon before the first badge.

**Must not:** promise Blackthorn, Victory Road or any climb; let anyone boast about the Bagon; explain the ledges or call them odd; name Bill, Rocket, Silph or the convergence; turn the slope into a trainer gauntlet (both fights stay optional).

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Gate warps | `(10,40)`, `(11,40)` | always | two tiles to gate warp 0, no lock | keep; the gate officer stays in Route 29's note |
| Cave mouth | `(20,11)` | always | warp to `DarkCave_SouthSide_hns` warp 1 | keep; add a sign, since the cave is the only landmark at the top |
| Route sign | `(11,35)`, `Route46_EventScript_Sign` | always | "Ledges allow descent only. No uphill passage." | keep; it is the route's only authority |
| Camper TED | `(6,18)`, `TRAINER_PLASTIC_OX_ROUTE46` | trainer, always | six Lv.7 rock/ground Pokémon; gear talk after | keep; make him a climbing instructor between shifts |
| Picnicker ERIN | `(4,18)`, `TRAINER_PLASTIC_OX_ROUTE46_ERIN` | trainer, always | Onix and Larvitar Lv.7; lunch and napkin lines | keep; she is the route's only warm voice |
| Bailey | `(19,25)`, `Route46_EventScript_Bailey` | always | came down from the mountains; won't go back up on these legs | keep; he states the cost of the road without explaining it |
| Ted (walker) | `(14,36)`, `Route46_EventScript_Ted` | always | a short walk still counts as a hike | keep; rename, because the trainer at `(6,18)` is also TED |
| Revive | `(2,21)` | `FLAG_POX_HIDDEN_R46_REVIVE` | one-shot item ball | keep; the only heal on the slope |
| Berry trees | `(9,11)`, `(11,11)` | `FLAG_POX_DAILY_R46_SITRUS`, `FLAG_POX_DAILY_R46_LIECHI` | Sitrus and Liechi, five a day | keep; decide whether Liechi belongs this early |

## Dialogue guidance

- **Who speaks:** people who have already accepted the hill. The campers are cheerful about gear; Bailey is the only one who names the cost; Ted has made peace with a short walk.
- **Register:** out of breath, practical, no mountain metaphors. Short clauses, gear nouns, weather only as it affects footing.
- **Before / after:** everyone is descending, so every line is about the way down. If the planned `route45_route46` link is ever cut in, these people need new lines, because "down" will no longer be the only direction.
- **The gate staff** belong to `Gate_Route29_Route46_hns` and Route 29's note; do not give them lines here.

> CAMPER TED: Pack light, walk heavy. My Machop carries the tent and I carry the snacks.

> PICNICKER ERIN: I brought lunch for four. Two of us, and the wind gets a portion.

> HIKER BAILEY: Down took forty minutes. Up would take a season, and I have a shift on Monday.

> TED: Bottom of the hill still counts as a hike if that is where you started.

- **Do not:** say "descent only" as a system message; mention Blackthorn or Victory Road; have anyone admire the Bagon; explain why the ledges exist; make the route sound dangerous when it is only steep.

## Inspiration

- **Mt. Fuji's Yoshida trail** — separate ascent and descent paths, the descent a wide, loose, joyless slope. Converts into the scree, the knee-braced walk and the sign's flat wording.
- **Japanese mountain-trail signage** — "descent only", "no uphill traffic", a stamped post at a junction. That is the sign at `(11,35)`, and the reason it talks instead of a guard.
- **Alpine club picnic culture** — onigiri in foil, a thermos, the wind taking the napkin. Gives Erin her lunch, her portions and her one grievance.
- **Volunteer mountain rescue** — a man who has walked down a hundred times and will not pretend it is a hike. Becomes Bailey, including the bad knees.
- **Rock-gym staff on their day off** — talking about gear instead of routes, carrying more than they need. Staffs Camper TED and his party of rock-lovers.
- **GSC Route 46** — short, steep, optional, Dark Cave at the top and nothing at the bottom but Route 29. Keep it a connector, not a destination.

## Implementation hooks

- Wiki page: `route46-hns.html`
- Maps: `Route46_hns` (`MAP_ROUTE46_HNS`, `LAYOUT_ROUTE46_HNS`, 27×46); transit `Gate_Route29_Route46_hns` and `DarkCave_SouthSide_hns`, neither claimed by this note
- Scripts: `data/maps/Route46_hns/scripts.inc`; `PoxRouteTrainer_Route46` in `data/scripts/plastic_ox_route_trainers.inc`; berry trees in `data/scripts/plastic_ox_berry_trees.inc` (the `Sitrus` and `Liechi` instances)
- Gates and flags: no access flag on either warp; `FLAG_POX_HIDDEN_R46_REVIVE`, `FLAG_POX_DAILY_R46_SITRUS`, `FLAG_POX_DAILY_R46_LIECHI`
- Trainers / items: `TRAINER_PLASTIC_OX_ROUTE46`, `TRAINER_PLASTIC_OX_ROUTE46_ERIN`, `ITEM_REVIVE`, `ITEM_SITRUS_BERRY`, `ITEM_LIECHI_BERRY`; encounters `gPoxRoute46Hns_Morning`, `gPoxRoute46Hns_Day`, `gPoxRoute46Hns_Night`
- Known gaps: two Campers share a sprite and a name — `TRAINER_PLASTIC_OX_ROUTE46` is TED and the walker at `(14,36)` is also Ted; the planned `route45_route46` portal in `region_v7.py` is deliberately not generated (`if key!='route45_route46'`), so the north link does not exist; no sign at the cave mouth; `MUS_RG_ROUTE1` and `MAPSEC_ROUTE_46`; `PoxRegion_Arrival_Route46_hns` is an empty stub

## Open questions

- Two Teds: same person (rename the walker) or two campers (rename the trainer)? As shipped it reads as a copy error.
- Should the cave mouth be gated until Ilex? It lands in the north half of `Route2_Frlg` at `(17,11)`, south of the hiker gate but above the south grass, so a Cherrygrove player can shortcut the climb's second half.
- Is the Liechi tree intentional this early? It is a competitive pinch berry before the first badge.
- When `route45_route46` is finally cut, this road stops being one-way. Does the sign stay, or does the badge-8 shortcut get new text?
