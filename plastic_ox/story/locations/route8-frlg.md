---
title: Route 8
slug: route8-frlg
kind: Route
act: 3
stage: "8 — Underground bypass"
depth: full
wiki: route8-frlg
maps: [Route8_Frlg]
also_maps: [UndergroundPath_EastEntrance_Frlg, UndergroundPath_EastWestTunnel_Frlg, UndergroundPath_WestEntrance_Frlg]
flags: [FLAG_POX_STORY_FUJI, FLAG_POX_STORY_SPACE_CENTER, FLAG_POX_TRIGGERS_ENABLED, FLAG_POX_TOURNAMENT_REWARD_1]
trainers: [TRAINER_PLASTIC_OX_TOURNAMENT_1]
items: [ITEM_RAWST_BERRY, ITEM_LUM_BERRY, ITEM_LEPPA_BERRY, ITEM_CONTEST_PASS]
status: drafted
---

# Route 8

## Snapshot

A fenced east–west road on the outside of Saffron, wide enough for two carts and lit only by the sky. The player enters from Lavender at `(66,20)`, walks its whole length with the city wall always to one side, and drops through the Underground Path stair at `(12,17)`; the route exists almost entirely as a walk. It is the first leg of the Lavender→Cinnabar bypass, and its emotional note is *waiting* — a road built for a city that has stopped letting anyone in.

## Plot points

1. **Lavender gate.** The east edge is a scripted crossing at `(67,20)` (`PoxRegion_lavender_route8_b`), opened by `FLAG_POX_STORY_FUJI`. Reveal-ladder **step 8** begins here: the player is now walking around the city instead of toward it.
2. **The road is inhabited, not hostile.** Thirteen FRLG residents stand along it and not one battles: every object is a plain NPC and its script only prints a post-battle line. Treat them as the road's population — gate-waiters, foragers, couriers — not as a trainer gauntlet.
3. **The Saffron gate is the promise.** At `(8,20)` the west crossing (`PoxRegion_route8_saffron_a`) refuses until `FLAG_POX_STORY_SPACE_CENTER`. The player should read a wall, a queue and a guard; the city stays shut for three more Badges.
4. **The stair down.** `(12,17)` warps into `UndergroundPath_EastEntrance_Frlg`; the tunnel runs beneath the city and surfaces at `UndergroundPath_WestEntrance_Frlg`, which is Route 7's problem.
5. **MR. POKéMON's sideshow.** In the tunnel at `(33,2)`, `PoxTournament_Host` opens round one to anyone holding Badge 4 — just earned at Fortree. Optional, loud, and the only cheerful person in the bypass.
6. **The berries are the reward.** Three hidden berries at `(40,21)`, `(36,23)`, `(40,31)`; two cuttable trees at `(31,31)` and `(44,25)` hide nothing story-critical. Add no quest item here.

**Must not:** name Bill, Silph, the adaptive system, or the reason Saffron is sealed; stage a Rocket appearance (their three scenes are Mt. Moon, Pokémon Tower, Silph); make residents into Gym aspirants; allow Saffron entry from this map before the Space Center.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Lavender crossing | `Route8_Frlg` `(67,20)` | `FLAG_POX_STORY_FUJI` unset | closed text, warp back to `(66,20)` | keep; give the barrier a person, not just text |
| Saffron crossing | `(8,20)` | `FLAG_POX_STORY_SPACE_CENTER` unset | `PoxRegion_route8_saffron_a` closed text, warp to `(7,20)` | keep the lock; the sign describes a city, not a map name |
| Underground stair | `(12,17)` | always | warp to `UndergroundPath_EastEntrance_Frlg` | keep |
| Dead gateway warp | `(9,20)` | always | warp to `Route8_WestEntrance_Frlg`, a legacy FRLG gate the repo's playtest records as unloadable | remove or repoint at the east entrance |
| Underground sign | `(7,19)` object | always | `PoxRegion_route8_saffron_a_Sign`: "SaffronCity / Marked passage ahead." | rewrite in-world: distance, direction, what the queue is for |
| Lavender sign | `(66,19)` object | always | `PoxRegion_lavender_route8_b_Sign`: "LavenderTown / Marked passage ahead." | same treatment, different wording |
| Gate-waiters | `(27,8)` Leslie, `(27,12)` Megan | always | both blame "the gates at SAFFRON" | keep the grievance, split the reasons: a delivery, a sister inside |
| Road residents | `(59,29)` Julia, `(52,31)` Rich, `(48,12)` Glenn, `(27,6)` Paige, `(27,10)` Andrea, `(20,6)` Stan, `(8,12)` Aidan | always, no battles | vanilla one-liners (Moon Stone rumour, "eating peanuts", Grimer mumble, "Things didn't work today") | one voice each: berry forager, gate idler, off-shift scientist, a child who has never been inside the city |
| Twins | `(38,6)` Eli, `(39,6)` Anne | always | two halves of one twin joke | keep the pair, give them a job (counting carts, selling water) |
| Bikers | `(13,33)` Ricardo, `(23,35)` Jaren | always | "grass caught up in my spokes" / "Don't think you're all special" | couriers who race the closed straight; the second is the sore loser |
| Berries | `(40,21)` Rawst, `(36,23)` Lum, `(40,31)` Leppa | hidden items | three hidden pickups | keep; let a resident say who planted them |
| Tunnel host | `UndergroundPath_EastWestTunnel_Frlg` `(33,2)` | `FLAG_POX_TOURNAMENT_REWARD_1` unset, Badge 4 | `PoxTournament_Host`, `TRAINER_PLASTIC_OX_TOURNAMENT_1` | keep; his patter is the only music down there |
| East entrance woman | `UndergroundPath_EastEntrance_Frlg` `(5,6)` | always | vanilla: "The DEPARTMENT STORE in CELADON has a great selection." | rewrite: she is going the other way, and Celadon is not on this road |
| West entrance man | `UndergroundPath_WestEntrance_Frlg` `(5,6)` | always | vanilla: "a sleepy POKéMON appeared out near CELADON CITY, too" | rewrite to a tunnel attendant's own business |

## Dialogue guidance

- **Who speaks:** people using a road that no longer reaches its destination. Nobody knows why Saffron is shut; each knows one errand and how long they have waited. The tunnel host is the exception — a collector, not a resident.
- **Register:** flat, dry, short. No exclamation marks, no theorising. Lines should sound like something said while looking at a gate.
- **Before / after:** before the Space Center the west end has a queue and everyone talks about the city; afterwards the queue is gone, the road is empty, and the same people are relieved or annoyed at the week they lost.
- **Tunnel voices** are indoor voices: echoes, merchandise, a man who has been down here too long. Keep them out of the road's weather.

> BERRY PICKER: Rawst grows right up against the fence. Nobody planted it. The road brought it.

> GATE WAITER: I have a delivery slip for a shop on the far side of that wall. Three weeks old now. I keep it in my coat.

> OFF-SHIFT SCIENTIST: I walk this stretch to think. Nobody on it asks what I am working on, which is the appeal.

> COURIER: Gate's shut, so we race the straight. Nobody official has noticed yet.

> MR. POKéMON: Four rounds, friend! A record is a collection that fights back.

- **Do not:** say "convergence", "sealed", "Silph", "Bill" or "Rocket"; explain the closure policy; give a resident a line about merged regions; let the gate refusal sound like a system message — "Return after your next objective" is already four maps' voice and must not become this road's.

## Inspiration

- **Ring road around a closed compound** — Tokyo's palace perimeter or a fenced airfield service road: kilometres of pavement that exist only to go around something you cannot enter. Converts into the queue, the guard, and the undeliverable parcel.
- **Late-autumn dry grass and a cold east wind.** The last ordinary week of the year: berries still on the bush, everyone in a coat, no shade. Gives the forager and the queue their weather.
- **FRLG Route 8's geometry** — fence lines, low ledges, an Underground Path house in the middle of nowhere. Keep the ledge rhythm; it is why the walk reads as a road and not a corridor.
- **Bicycle-courier culture** — city messengers and fixed-gear kids on an empty straight. Converts into the two bikers and the small economy of people who know the gate schedule better than the guard does.
- **The Underground Path as a retail arcade** — fluorescent light, a shuttered kiosk, a collector at a folding table. That is MR. POKéMON's entire set.

## Implementation hooks

- Wiki page: `route8-frlg.html`
- Maps: `Route8_Frlg` (`MAP_ROUTE8`, donor layout `LAYOUT_ROUTE8_HNS`), `UndergroundPath_EastEntrance_Frlg` (`MAP_UNDERGROUND_PATH_EAST_ENTRANCE`), `UndergroundPath_EastWestTunnel_Frlg` (`MAP_UNDERGROUND_PATH_EAST_WEST_TUNNEL`), `UndergroundPath_WestEntrance_Frlg` (`MAP_UNDERGROUND_PATH_WEST_ENTRANCE`)
- Scripts: `data/maps/Route8_Frlg/scripts.inc`, the three `data/maps/UndergroundPath_*/scripts.inc`, generated `data/scripts/plastic_ox_region.inc`, `data/scripts/plastic_ox_tournament.inc`
- Gates: `FLAG_POX_STORY_FUJI` (east), `FLAG_POX_STORY_SPACE_CENTER` (west), `FLAG_POX_TRIGGERS_ENABLED` (walkable-build bypass inside every portal script)
- Trainers / items: `TRAINER_PLASTIC_OX_TOURNAMENT_1` is the only battle in the whole bypass; `ITEM_RAWST_BERRY`, `ITEM_LUM_BERRY`, `ITEM_LEPPA_BERRY` hidden on the road; `ITEM_CONTEST_PASS` from round one.
- Known gaps: the dossier lists 12 `TRAINER_*` parties but every object is a plain NPC and the generated `Route8_EventScript_*` wrappers only print post-battle text — the battle bodies sit inside `.if IS_FRLG` blocks in `data/scripts/trainers_frlg.inc` and are compiled out, so the route has **zero trainer battles**; warp `(9,20)` still targets the unloadable `Route8_WestEntrance_Frlg`; both signs are generated map-name placeholders and the tunnel sign still reads "CELADON CITY - LAVENDER TOWN"; two entrance NPCs speak vanilla Celadon text; the tunnel's seven hidden items are all low-tier heals, which leaves the long walk unrewarded; `LavenderTown_Frlg`, `SaffronCity_Frlg` and `SaffronCity_Connection_Frlg` all still hold one-way connections into this map while the live route holds none.

## Open questions

- Restore the twelve FRLG battles at act-3 levels, or keep Route 8 quiet and let the tunnel be the only combat? Right now it is neither: parties exist, nobody fights.
- Retire `Route8_WestEntrance_Frlg` and the dangling legacy connections, or repoint them? Recommend retire — they are reachable only through the broken `(9,20)` warp.
- Should the tournament stay in a public tunnel, or move to a dedicated facility once the underground stops being the main road?
- Route 8 still rolls FireRed/LeafGreen wild encounters (Pidgey, Meowth, Growlithe or Vulpix, Ekans or Sandshrew, Lv 15–20). Keep as road texture, or retune for an act-3 party?
