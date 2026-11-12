---
title: Route 5
slug: route5-hns
kind: Route
act: 4
stage: "12 — Saffron to Blackthorn"
depth: full
wiki: route5-hns
maps: [Route5_hns]
also_maps: [Gate_SaffronCity_Route5_hns]
flags: [FLAG_POX_STORY_SPACE_CENTER, FLAG_POX_TRIGGERS_ENABLED]
status: drafted
---

# Route 5

## Snapshot

The northern road out of Saffron: sixty-eight tiles of open ground from the city's back gate to the Route 115 turn, with a checkpoint building that nobody can enter and no population at all. The player crosses it once, at `(32,38)` → `(32,0)`, on the way to Meteor Falls and Clair; nothing happens here, which is exactly the note's problem and its opportunity. Route 5 is the last ordinary road before the mountains, and it should feel like a road people use to *prepare*.

## Plot points

1. **The north gate opens with the city.** `(32,38)` (`PoxRegion_saffron_route5_b`) refuses until `FLAG_POX_STORY_SPACE_CENTER`, the same flag that opens Saffron. There is no second condition: the road to Blackthorn is available whether or not Bruno and Silph are resolved.
2. **No story beat lives here.** Route 5 carries the Act IV→V turn — the OU region and the eighth Badge — and its whole job is to move the player from a city to a mountain without a cutscene. Reveal-ladder step 12 (Saffron opens) has already happened inside the city; nothing new is revealed on this road.
3. **The gatehouse is orphaned.** `Gate_SaffronCity_Route5_hns` has zero warp events and no map references it: a policeman stands in a building the player can never enter. Either wire it as the Saffron checkpoint or retire it; do not leave it as decoration with a speaking NPC inside.
4. **Preparation, not exposition.** The road should be full of people carrying things north: supplies, luggage, a spare team, a folding chair. Dialogue must work identically before and after Silph — nobody here knows how the city's business is going.
5. **Must not:** assume the Silph crisis is resolved (or mention Silph at all); name Bill; stage Rocket; turn the checkpoint into a badge gate (the League gate is Ecruteak's, and it checks all eight Badges); put a healer here without deciding what that does to Meteor Falls' difficulty.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Saffron crossing | `Route5_hns` `(32,38)` | `FLAG_POX_STORY_SPACE_CENTER` unset | `PoxRegion_saffron_route5_b` closed text, warp back to `(31,38)` | keep; the sign at `(31,37)` should describe the north road, not a map name |
| Route 115 crossing | `(32,0)` | `FLAG_POX_STORY_SPACE_CENTER` unset | `PoxRegion_route5_route115_a` warps to `Route115` `(19,79)` | keep; this is the map's real exit and should read as a pass approach |
| Sign pair | `(31,37)` and `(31,1)` | always | "SaffronCity / Route115 / Marked passage ahead." placeholders | rewrite: distances, the last services, the mountain's name |
| Duplicate sign events | same two tiles | always | each sign exists as an object **and** a background sign event on the identical coordinate | remove one of each pair |
| Gatehouse | `Gate_SaffronCity_Route5_hns` `(3,6)` | always | `Gate_SaffronCity_Route5_EventScript_Npc1` says "Keep the doorway clear so travelers can pass safely", but the map has **no warps** and is unreachable | wire the gate into `(32,38)`/`(32,0)` as the checkpoint, or delete the map |
| Empty road | whole map | — | 0 NPCs, 0 items, 0 encounters, 0 trainers on a 68×46 route | add a checkpoint officer and two or three travellers; decide whether the route rolls wild Pokémon at all |
| Arrival hook | map load | always | `PoxRegion_Arrival_Route5_hns` is an empty stub | use it only if the checkpoint needs to change state |

## Dialogue guidance

- **Who speaks:** people moving north with more luggage than they need. A checkpoint officer who logs carts, a driver doing the pass twice a week, a Trainer who has stopped pretending the eighth Badge is not on their mind. Nobody is a gatekeeper for the plot.
- **Register:** brisk and practical — the fastest sentences in Act IV. This is a road with a schedule: the pass closes at dark, the next services are a long way up, the cart is already full.
- **Before / after:** no change with story flags. The only variation worth writing is time-of-day-flavoured filler, not a state switch.
- **The checkpoint is the comic voice:** forms, queues, a stamp that does not work, a rule about where you may park.
- **Do not** let anyone speculate about the city, Saffron's Gym, or the League gate.

> CHECKPOINT OFFICER: Nothing to declare but the queue. Keep moving — the pass road is open until dark and then it isn't.

> SUPPLY DRIVER: Two crates of Potions for the mountain. Third run this week. The mountain eats them.

> TRAVELLER: Everyone on this road is training for something they won't name. I find it restful.

> YOUNG TRAINER: I packed four jackets and one map. The map is the one I'm worried about.

- **Do not:** mention Silph, Rocket, Bill or the system; imply the player is famous; make the checkpoint a badge check; write a healer or a shop into the route without a design decision.

## Inspiration

- **The last services before a mountain pass** — the Japanese *michi-no-eki* roadside station, or the toll gate at the foot of a Fuji approach: a car park, a vending machine, a map board, a man in a booth who has said the same sentence ten thousand times.
- **Shoulder-season ski roads** — empty tarmac, chain-fitting signs, a hotel with its shutters down. Gives the route its "everyone is early for something" mood.
- **Kanto's Route 5 in FRLG** — short, suburban, the Day Care sitting in the middle of it. Convert the Day Care's function (a place people leave something behind) into the route's rest-stop idea rather than rebuilding the building.
- **Departure-lounge behaviour** — people repacking bags on the floor, comparing routes, asking the driver whether the pass is clear. That is the whole social life of the map.
- **Meteor Falls approach in Hoenn** — the road narrowing before the mountain, the first sight of rock instead of fields. Route 5 is where that silhouette should appear.

## Implementation hooks

- Wiki page: `route5-hns.html`
- Maps: `Route5_hns` (`MAP_ROUTE5_HNS`, layout `LAYOUT_ROUTE5_HNS`, 68×46), `Gate_SaffronCity_Route5_hns` (`MAP_GATE_SAFFRON_CITY_ROUTE5_HNS`, layout `LAYOUT_GATE_SAFFRON_CITY_ROUTE5_HNS`)
- Scripts: generated `data/scripts/plastic_ox_region.inc` (`PoxRegion_saffron_route5_b`, `PoxRegion_route5_route115_a`, `PoxRegion_saffron_route5_b_Sign`, `PoxRegion_route5_route115_a_Sign`), `data/maps/Gate_SaffronCity_Route5_hns/scripts.inc`
- Gates: `FLAG_POX_STORY_SPACE_CENTER` on both crossings; `FLAG_POX_TRIGGERS_ENABLED` bypasses the gate text in the walkable build
- Trainers / items: none exist; none are required by the story
- Known gaps: `Gate_SaffronCity_Route5_hns` has no warps, no background events and no inbound reference, so its one NPC can never be spoken to; both signs are duplicated (object plus background event) and use the generated `<MapName>\nMarked passage ahead.` text; the route has no wild encounters at all despite being 68×46; the arrival hook (`PoxRegion_Arrival_Route5_hns`) is an empty stub and the map has no interior of its own; the legacy `Route5_Frlg` (`MAP_ROUTE5`, group `gMapGroup_TownsAndRoutes_Frlg`) is still registered with warps into the Day Care and the legacy Underground Path north entrance, and connects only to unloadable Cerulean/Saffron FRLG maps.

## Open questions

- Wire `Gate_SaffronCity_Route5_hns` into the route's north/south crossings as a real checkpoint, or retire it and keep the crossings as portals? Recommend wiring it — a gate the player walks through is better staging than a textbox.
- Should Route 5 have wild encounters? It is currently a pure corridor; if it does, which tier band fits a road that exists between badge 6 and badge 8?
- Does the route get a rest stop (heal/PC) before Meteor Falls, or is the difficulty meant to carry the player through on supplies?
- How many NPCs does a 68×46 map need before it stops reading as empty — three, five, or a small roadside cluster with its own mini-drama?
