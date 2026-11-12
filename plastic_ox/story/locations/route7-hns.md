---
title: Route 7
slug: route7-hns
kind: Route
act: 3
stage: "8 — Underground bypass"
depth: full
wiki: route7-hns
maps: [Route7_hns]
flags: [FLAG_POX_STORY_FUJI, FLAG_POX_STORY_SPACE_CENTER, FLAG_POX_TRIGGERS_ENABLED]
status: drafted
---

# Route 7

## Snapshot

Twenty tiles of open road on Saffron's western flank, with a wall on one side and nothing on the other. The player surfaces from the Underground Path at `(3,22)`, crosses it in under a minute, and leaves through the only opening the story allows — the Route 103 gate at `(1,22)`. Route 7 is a junction pretending to be a route: three crossings, no houses, no residents, and no reason to stay. Its emotional job is to make the player feel the *thinness* of the world around a city that will not open.

## Plot points

1. **Out of the tunnel.** The West Entrance stair of `UndergroundPath_WestEntrance_Frlg` at `(5,7)`–`(7,7)` returns the player here at `(3,22)`. Reveal-ladder **step 8** continues: they have now physically passed beneath Saffron and are standing on its far side.
2. **Three ways, one of them open.** Saffron at `(6,22)` refuses until `FLAG_POX_STORY_SPACE_CENTER`; Route 103 at `(1,22)` opens on `FLAG_POX_STORY_FUJI`, which is already true by the time anyone can reach this map; the Underground stair at `(4,22)` is always usable.
3. **The map is currently empty.** No NPCs, no items, no wild encounters, no trainers, no map objects beyond three signs. Nothing here is broken — but nothing here is a place yet, and the note's job is to decide what it should say.
4. **The wall is the scene.** Every sightline should end at Saffron's back wall: rooftops over it, a tannoy, traffic noise that stops at the boundary. The player may not enter, and the map's whole composition should say so without a textbox.
5. **Must not:** add a fourth exit, a hidden path or a trash-can entrance into Saffron; put Rocket, Bill, Silph or the system here; explain in dialogue why the city is closed (nobody local knows); turn the junction into a puzzle.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Saffron crossing | `Route7_hns` `(6,22)` | `FLAG_POX_STORY_SPACE_CENTER` unset | `PoxRegion_route7_saffron_a` prints the generic closed text and bumps the player to `(5,22)` | keep the lock; put a bored guard or a barrier here so the refusal is physical |
| Route 103 crossing | `(1,22)` | `FLAG_POX_STORY_FUJI` | `PoxRegion_route7_route103_a` warps to `Route103` `(78,11)` | keep; this is the map's real exit and should look like one |
| Underground stair | `(4,22)` | always | `PoxRegion_underground_west` warps to `UndergroundPath_WestEntrance_Frlg` `(6,6)` | keep |
| Three signs | `(5,23)`, `(1,24)`, `(3,23)` | always | "SaffronCity / Route103 / Underground Path / Marked passage ahead." ×3, all in the same generated voice | three place-specific signs: the city, the long road west, the stair |
| Duplicate sign events | same three tiles | always | each sign exists twice — an object **and** a background sign event at the identical coordinate | remove one of each pair; two signposts on one tile reads as a collision |
| Legacy sign posts | `(5,16)`, `(7,16)` bg events | always | `Route7_EventScript_Sign1` and `Route7_EventScript_Sign2`, both "A sign from the old routes." | delete or repurpose; the line breaks the fourth wall |
| Empty map | whole map | — | 0 NPCs, 0 items, 0 encounters, 0 trainers | add two or three people with a reason to stand at a wall, not a full cast |
| Arrival hook | map load | always | `PoxRegion_Arrival_Route7_hns` is an empty stub | use it if the gate needs to change state on the Space Center flag, otherwise leave empty |

## Dialogue guidance

- **Nobody speaks here today.** State that plainly in implementation: any voice added to Route 7 is new writing, not a rewrite, and should be kept to two or three people.
- **Who should speak:** the people a wall attracts — a gate-watcher who has run out of things to check, a courier sleeping in a parked van, a child throwing stones at the boundary. They have no information about the plot and no interest in it.
- **Register:** outdoor, windy, unimpressed. Short sentences that stop. One of the three should be friendly and one should want the player to move along.
- **Before / after:** before the Space Center, the Saffron end has a barrier and somebody posted to it; afterwards the barrier is gone and the same person is packing it into a van.
- **Do not** let these people explain the seal, mention the League, or offer directions the signs already give.

> WALL WATCHER: Nothing comes out of that gate but pigeons. I still check it every hour.

> COURIER: I sleep here because the depot opens at six and the road is quiet. Move along or don't.

> CHILD: If you throw a stone high enough you can see the roofs. I can't. My arm's no good.

- **Do not:** reuse the "Marked passage ahead" formula, name Saffron's Gym or Silph, imply a Rocket presence, or write anyone who knows what the player has been doing.

## Inspiration

- **Gen I Route 7 as the shortest route in the game** — in Red/Blue it is barely two screens wide between Celadon and Saffron, and that compression is the joke. Lean into it: this is a route you cross without noticing, and the note should make that deliberate rather than unfinished.
- **The strip between a wall and a ring road** — the dead margin outside a closed barracks or a stadium, where the pavement is wide because nobody planned for people to stop there.
- **A bus terminus at the end of a line** — a shelter, a timetable with two entries, a driver on a break. Converts into the courier and the guard's routine.
- **Sound through a wall**: a tannoy announcement you cannot make out, a lorry changing gear, a door that opens and closes all day. Use it as the map's atmosphere instead of dialogue.
- **Border-crossing limbo** (any film's neutral zone) — the feeling that the interesting country is fifty metres away and legally out of reach.

## Implementation hooks

- Wiki page: `route7-hns.html`
- Maps: `Route7_hns` (`MAP_ROUTE7_HNS`, layout `LAYOUT_ROUTE7_HNS`, 20×28), tied to `UndergroundPath_WestEntrance_Frlg` (`MAP_UNDERGROUND_PATH_WEST_ENTRANCE`)
- Scripts: `data/maps/Route7_hns/scripts.inc`, generated `data/scripts/plastic_ox_region.inc` (`PoxRegion_route7_saffron_a`, `PoxRegion_route7_route103_a`, `PoxRegion_underground_west`, and the three sign labels)
- Gates: `FLAG_POX_STORY_SPACE_CENTER` (Saffron), `FLAG_POX_STORY_FUJI` (Route 103), `FLAG_POX_TRIGGERS_ENABLED` (walkable-build bypass)
- Trainers / items: none exist and none are needed.
- Known gaps: the map has no NPCs, items or encounters at all; every sign is placed twice (object plus background event); sign text is the generated `<MapName>\nMarked passage ahead.` placeholder; two leftover bg signs say "A sign from the old routes."; `Route7_hns` has no connections and no warps, so its three crossings are the only traversal; the legacy `Route7_Frlg` (`MAP_ROUTE7`) is still registered in `gMapGroup_TownsAndRoutes_Frlg` and still holds a warp into the live `UndergroundPath_WestEntrance_Frlg` plus links to the unloadable `CeladonCity_Frlg` / `SaffronCity_Connection_Frlg` side.

## Open questions

- Keep `Route7_hns` as a 20×28 vestibule, or fold its three crossings into the Underground Path's West Entrance so the world has one fewer nearly-empty map?
- Retire the legacy `Route7_Frlg` (`MAP_ROUTE7`)? It is not referenced by any live note, still warps into the live tunnel, and connects only to maps the engine cannot load.
- Should the Saffron gate be a talking guard with a badge/flag check, or stay a silent barrier with a sign?
- Is two or three NPCs the right population, or should Route 7 be deliberately, memorably empty — one bench and a wind sound?
