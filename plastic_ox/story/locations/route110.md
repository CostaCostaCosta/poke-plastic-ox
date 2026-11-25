---
title: Route 110
slug: route110
kind: Route
act: 2
stage: "6 — Fortree to Lavender"
depth: full
wiki: route110
maps: [Route110]
also_maps: [Route110_SeasideCyclingRoadNorthEntrance, Route110_SeasideCyclingRoadSouthEntrance, Route110_TrickHouseEntrance, NewMauville_Entrance]
flags: [FLAG_POX_REACHED_FORTREE]
items: [ITEM_REVIVE, ITEM_GREAT_BALL, ITEM_POKE_BALL, ITEM_FULL_HEAL]
trainers: [TRAINER_JASMINE]
status: drafted
---

# Route 110

## Snapshot

Two roads stacked on one hillside: a raised cycleway on the ridge and a slow lane through the grass below it, meeting at the Lavender junction. The player arrives from `FortreeCity` after badge 4 and leaves south toward `LavenderTown_hns`; the westward spur at rows `67..71` is the region's midgame shortcut back to Route 36 and only becomes live once Fortree is reached. The route's emotional note is traffic — it is the first place in the game where the world feels *commuted through* rather than travelled.

## Plot points

1. **Arrival from Fortree.** Fortree's east clearing and a forest corridor on Route 110 rows `2..5` are one native connection: the player walks across with no fade and comes out of the trees above the two roads. Fortree's edge tiles (`PoxRegion_fortree_route110_a`) hold the badge 4 check. No cutscene; the two roads' difference is the route's whole argument.
2. **The route teaches its own shape.** The upper deck is fast, safe, and boring. The lower road holds the grass, the berry trees, the trainers, and the items. An old man at `(10,11)` already has the best line in the file about it; keep him and make him the route's thesis.
3. **The shortcut folds the middle of the world.** The west spur's sand road (rows `67..71`) is a native connection to `Route36_hns`. From this side it is always open; on Route 36 a sleeping hiker and `FLAG_POX_REACHED_FORTREE` hold it. This is the map's one structural story beat: Fortree stops being a far edge.
4. **The Lavender junction.** The south road (`15..19,99`) is a native connection into Lavender's north meadow (`12..16,0`); `PoxRegion_route110_lavender_a` on the edge tiles checks badge 4. It should read as an ordinary road, not a story door.
5. **Do not stage the mystery here.** Route 110 is breathing room between the Weather Institute and Rocket II. People talk about haulage, bikes, wind, and the price of a repair.

**Must not:** mention Bill, Silph, Team Rocket, or Team Aqua; reference Hoenn geography (Mauville, Slateport, Rydel) as if it were reachable; give the player a new bike mechanic; put a story gate at both ends of the same stretch.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Fortree road | west edge `(0,2..5)` | always | walk west into `FortreeCity` `(39,7..10)` | keep; the badge check lives on Fortree's side |
| Lavender road | south edge `(15..19,99)` `PoxRegion_route110_lavender_a` | badge 4 | walk south into `LavenderTown_hns` `(12..16,0)`; closed: generic text and a step back | keep; add a junction sign with distances, not a warning |
| Route 36 shortcut | west edge `(0,67..71)` | always | walk west into `Route36_hns` `(65,18..22)` | keep; this is the route's only real story moment and deserves one line of acknowledgement |
| Aqua grunts | `(7,83)`, `(8,83)`, `(9,83)`, `(10,83)` | always | four `TEAM AQUA` lines about Slateport and "kicking up a ruckus" | recast: a delivery crew, a cycle club, or striking hauliers. There is no Team Aqua in this story |
| Fifth grunt | `(8,82)` | — | object with script `0x0` | delete; it is an invisible body under the four above |
| Duplicate rivals | `(34,54)` twice (`LOCALID_ROUTE110_RIVAL`, `LOCALID_ROUTE110_RIVAL_ON_BIKE`) | — | two objects, same tile, both script `0x0` | delete both or place one properly; stacked objects are a save and collision hazard |
| Professor Birch | `(9,79)` | — | `OBJ_EVENT_GFX_PROF_BIRCH` with script `0x0` | delete or repurpose as a route researcher with a real line |
| Jasmine | `(16,73)` `TRAINER_JASMINE` | always | a cyclist named after a Johto Gym Leader, Lv.14 team | rename or retype; players will read the name as the Olivine leader |
| Two-roads old man | `(10,11)` `Route110_EventScript_OldMan` | always | "A road each for people and POKéMON. Perhaps that is right and fair." | keep almost verbatim; it is the route's theme |
| Rydel bike chatter | `(9,57)` `Route110_EventScript_CyclingGuy1` | always | eight repetitions of "RYDEL" on the player's bike | rewrite; Rydel is a Hoenn shop that does not exist here |
| Trainer levels | 14 trainers, `(17,90)`–`(36,40)` | always | Lv.6–16 teams (Magnemite, Abra, Voltorb) | rescale to the Lv.28–33 band; this route sits after badge 4 and reads as Route 3 |
| Hidden items | `(35,39)` `ITEM_REVIVE`, `(33,45)` `ITEM_GREAT_BALL`, `(4,35)` `ITEM_POKE_BALL`, `(37,67)` `ITEM_FULL_HEAL` | once | hidden pickups | keep; the `ITEM_FULL_HEAL` at the junction reads as a dropped commuter's bag |

## Dialogue guidance

- **Two registers, one route.** Upper-road people are in a hurry and talk about time; lower-road people are not and talk about what they can see. Every NPC should pick a lane and stay in it.
- **Work is the subject:** haulage, repairs, wind, a load that shifted, a bell that needs replacing. Nobody here has an opinion about the region.
- **No Hoenn place names.** If a line needs a destination, use a place the player can reach or a direction ("the junction", "the coast road").
- **After the shortcut opens,** the west spur gets one local who is pleased and one who is annoyed about the traffic.
- Keep trainer lines short and physical; these are people mid-ride, not philosophers.

> COURIER: Upper road's for anyone in a hurry. I take the lower one — the loads shift less and the dogs don't chase.

> MECHANIC: Everyone brings me a bike with the same problem. Nobody brings me a chain.

> WALKER: I walked this before there were two roads. I still walk it. Slower, but I know where the puddles are.

> KID: Up top you can see the sea. Down low you can see the Pokémon. I always go low.

- **Do not:** say "convergence", "anomaly", or "the region"; mention Mauville, Slateport or Rydel; reuse the Burned Tower or Route 119 imagery.

## Inspiration

- **Paris's Coulée verte / Promenade Plantée:** an elevated viaduct with a working street directly beneath it. This is exactly Route 110's two-level promise, and it supplies the ramp, the railing, and the smell difference between the two roads.
- **Dutch cycle highways at rush hour:** a repair stand at the on-ramp, a bell you can hear coming, and commuters who are rude only in the first hour. Converts to the courier and the mechanic.
- **Shimanami Kaido:** rental counters, wind, a toll, and a view worth stopping for. Use it for the ridge's one scenic beat.
- **A truck-stop stall at a junction:** thermos, rice balls, a laminated price list. One vendor at the Lavender fork gives the junction a reason to exist beyond a warp.
- **RSE Route 110 / Seaside Cycling Road:** the slope that carries you, the bike-only lane, the friction when the grass wins. Keep the friction; drop the Hoenn branding.

## Implementation hooks

- Wiki page: `route110.html`
- Map: `Route110` (`MAP_ROUTE110`); connections `left` to `MAP_FORTREE_CITY` (offset -5) and `MAP_ROUTE36_HNS` (offset 49), `down` to `MAP_LAVENDER_TOWN_HNS` (offset 3); the forest beyond the land edges comes from `src/plastic_ox_borders.c`; 6 warps (the two Cycling Road gatehouses, New Mauville `(35,24)` as warp 4, the Trick House `(11,66)` as warp 5), 36 objects, 14 trainers
- Scripts: `data/maps/Route110/scripts.inc`, `data/scripts/plastic_ox_region.inc` (`PoxRegion_route110_lavender_a`)
- Flags: `FLAG_POX_REACHED_FORTREE` (set on Fortree arrival), badge gates use `FLAG_BADGE04_GET`
- Known gaps: four live Team Aqua grunts plus one dead one; two objects stacked on `(34,54)`; `OBJ_EVENT_GFX_PROF_BIRCH` at `(9,79)` with script `0x0`; all 14 trainers are Lv.6–16 on a stage-6 route; a cyclist shares the name of a Johto Gym Leader; the "RYDEL" bike sign text repeats eight times.

## Open questions

- Recast the Aqua grunts as what — a delivery crew, a cycle club, or hauliers on strike? Any of the three keeps the junction busy without importing a team.
- Rescale the 14 trainers to the Lv.28–33 band, or move Route 110 earlier in the story? As written the difficulty curve drops by ten levels the moment the player leaves Fortree.
- The New Mauville and Trick House doors, retired in the 2026-11-21 trigger audit, are restored (2026-11-23): New Mauville holds Raikou behind the NEW MAUVILLE KEY, and the Trick House is playable. Should Route 110 locals acknowledge the Trick House now that it is open?
- Should the Route 36 shortcut announce itself, or open silently and let the player discover the west road on their own?
