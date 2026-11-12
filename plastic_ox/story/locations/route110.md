---
title: Route 110
slug: route110
kind: Route
act: 2
stage: "6 — Fortree to Lavender"
depth: full
wiki: route110
maps: [Route110]
flags: [FLAG_POX_REACHED_FORTREE]
items: [ITEM_REVIVE, ITEM_GREAT_BALL, ITEM_POKE_BALL, ITEM_FULL_HEAL]
trainers: [TRAINER_JASMINE]
status: drafted
---

# Route 110

## Snapshot

Two roads stacked on one hillside: a raised cycleway on the ridge and a slow lane through the grass below it, meeting at the Lavender junction. The player arrives from `FortreeCity` after badge 4 and leaves south toward `LavenderTown_hns`; the westward spur at `(1,67)` is the region's midgame shortcut back to Route 36 and only becomes live once Fortree is reached. The route's emotional note is traffic — it is the first place in the game where the world feels *commuted through* rather than travelled.

## Plot points

1. **Arrival from Fortree.** `(18,0)` `PoxRegion_fortree_route110_b` requires badge 4, dropping the player at `(17,0)`. No cutscene; the two roads are visible from the first step and their difference is the route's whole argument.
2. **The route teaches its own shape.** The upper deck is fast, safe, and boring. The lower road holds the grass, the berry trees, the trainers, and the items. An old man at `(10,11)` already has the best line in the file about it; keep him and make him the route's thesis.
3. **The shortcut folds the middle of the world.** `(1,67)` `PoxRegion_route36_shortcut_b` gates on `FLAG_POX_REACHED_FORTREE`, opening the west spur back to `Route36_hns` permanently. This is the map's one structural story beat: Fortree stops being a far edge.
4. **The Lavender junction.** `(16,5)` `PoxRegion_route110_lavender_a` requires badge 4 and delivers the player to Lavender. The gate should read as an ordinary road junction, not a story door.
5. **Do not stage the mystery here.** Route 110 is breathing room between the Weather Institute and Rocket II. People talk about haulage, bikes, wind, and the price of a repair.

**Must not:** mention Bill, Silph, Team Rocket, or Team Aqua; reference Hoenn geography (Mauville, Slateport, Rydel) as if it were reachable; give the player a new bike mechanic; put a story gate at both ends of the same stretch.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Fortree gate | `(18,0)` `PoxRegion_fortree_route110_b` | badge 4 | closed → generic text + bounce back | keep; the closure should be wind or a closed deck, not an invisible wall |
| Lavender gate | `(16,5)` `PoxRegion_route110_lavender_a` | badge 4 | warps to `LavenderTown_hns` `(15,0)` | keep; add a junction sign with distances, not a warning |
| Route 36 shortcut | `(1,67)` `PoxRegion_route36_shortcut_b` | `FLAG_POX_REACHED_FORTREE` | opens the west spur to `Route36_hns` | keep; this is the route's only real story moment and deserves one line of acknowledgement |
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

- **Do not:** say "convergence", "anomaly", or "the region"; mention Mauville, Slateport, Rydel, or the Trick House; reuse the Burned Tower or Route 119 imagery.

## Inspiration

- **Paris's Coulée verte / Promenade Plantée:** an elevated viaduct with a working street directly beneath it. This is exactly Route 110's two-level promise, and it supplies the ramp, the railing, and the smell difference between the two roads.
- **Dutch cycle highways at rush hour:** a repair stand at the on-ramp, a bell you can hear coming, and commuters who are rude only in the first hour. Converts to the courier and the mechanic.
- **Shimanami Kaido:** rental counters, wind, a toll, and a view worth stopping for. Use it for the ridge's one scenic beat.
- **A truck-stop stall at a junction:** thermos, rice balls, a laminated price list. One vendor at the Lavender fork gives the junction a reason to exist beyond a warp.
- **RSE Route 110 / Seaside Cycling Road:** the slope that carries you, the bike-only lane, the friction when the grass wins. Keep the friction; drop the Hoenn branding.

## Implementation hooks

- Wiki page: `route110.html`
- Map: `Route110` (`MAP_ROUTE110`); no connections, 6 warps (all interiors), 36 objects, 14 trainers
- Scripts: `data/maps/Route110/scripts.inc`, `data/scripts/plastic_ox_region.inc` (`PoxRegion_fortree_route110_b`, `PoxRegion_route110_lavender_a`, `PoxRegion_route36_shortcut_b`)
- Flags: `FLAG_POX_REACHED_FORTREE` (set on Fortree arrival), badge gates use `FLAG_BADGE04_GET`
- Known gaps: four live Team Aqua grunts plus one dead one; two objects stacked on `(34,54)`; `OBJ_EVENT_GFX_PROF_BIRCH` at `(9,79)` with script `0x0`; all 14 trainers are Lv.6–16 on a stage-6 route; a cyclist shares the name of a Johto Gym Leader; the "RYDEL" bike sign text repeats eight times.

## Open questions

- Recast the Aqua grunts as what — a delivery crew, a cycle club, or hauliers on strike? Any of the three keeps the junction busy without importing a team.
- Rescale the 14 trainers to the Lv.28–33 band, or move Route 110 earlier in the story? As written the difficulty curve drops by ten levels the moment the player leaves Fortree.
- Retire the `New_Mauville_Entrance` and `Route110_Trick_House_Entrance` warps, or repurpose them as the junction's garage and a storage shed?
- Should the Route 36 shortcut announce itself, or open silently and let the player discover the west road on their own?
