---
title: Route 21 South
slug: route21-south-frlg
kind: Route
act: 3
stage: "9 — Cinnabar and the Mansion"
depth: supporting
wiki: route21-south-frlg
maps: [Route21_South_Frlg]
flags: [FLAG_POX_STORY_FUJI, FLAG_POX_STORY_MANSION]
status: drafted
---

# Route 21 South

## Snapshot

The second 24×50 panel of the Pallet–Cinnabar water line, from Route 21 North's southern seam onto Cinnabar Island's north beach. It is the sunniest map in the act — five swimmers and fishermen, no items, no signs, no shade — and it ends at the back door of the island the chapter is about. Its emotional note is arrival: the sea stops being scenery and becomes ground you can walk on.

## Plot points

1. **Cinnabar's only ungated side.** The beach connection at `x 12–15` is a bare map connection. The island's other two edges are scripted: the Route 103 approach is refused without `FLAG_POX_STORY_FUJI`, and the Route 20 sea exit without `FLAG_POX_STORY_MANSION`. So a surfer can walk onto Cinnabar here with no scene, no flag, and no text — `PoxRegion_Arrival_CinnabarIsland_Frlg` is an empty stub.
2. **Surf sets the clock.** Surf needs `ITEM_SURF_KEY`, handed over by Fuji together with `FLAG_POX_STORY_FUJI` in the same conversation that names Route 8, the Underground Path, Route 7 and Route 103. The sea road is not a pre-Fuji bypass — it is a second way into the same leg, one that quietly skips the road Fuji describes.
3. **A triathlon coast with no race.** Jerome trains for a triathlon, Roland is sunburnt, Jack asks where the player caught their Pokémon, Claude suspects the sea is a giant pool, Nolan has one bite. Their parties (Lv 31–37) sit in `trainers_frlg.inc` inside `.if IS_FRLG` and compile out, so every object prints only its post-battle line: nobody here can fight, and nobody explains the island.
4. **Must not:** stage the Mansion's research, name Entei, pre-empt Blaine's key, or let the beach arrival speak in portal language. This is the last quiet water before the chapter's science; keep it quiet.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Cinnabar beach | `(12–13, 49)` to Cinnabar's `(12–15, 0)` | map connection, no coordinate event | open seam, no text, no gate | one guard, one greeting, or a deliberate silence — but decide |
| Claude | `(11,8)` | `Route21_South_EventScript_Claude` | "Could this place actually be a giant pool?" | the man who has fished here since dawn and has nothing |
| Nolan | `(14,15)` | `Route21_South_EventScript_Nolan` | "Oh wait! I got a bite! Yeah!" | keep; he is the only one who catches anything |
| Jerome | `(15,38)` | `Route21_South_EventScript_Jerome` | triathlon, bike race and marathon still to go | keep; the coast's only athlete and its only calendar |
| Roland | `(10,29)` | `Route21_South_EventScript_Roland` | "I'm sunburnt to a crisp!" | keep the burn; let him be the one who warns about the beach |

## Dialogue guidance

- **Who speaks:** five people at different stages of one long day in the sun, here because the water is warm and the island is close, not because a plot stations them.
- **Register:** friendly, slowed-down, a little sun-stupid. Short observations, no theorising about the island or the Mansion. The sea is a fact of the afternoon, not a metaphor.
- **Before / after:** the coast reads the same whether the player arrives before Blaine or after the Mansion; the island's flags do not reach the water. That stability is the point — this is the map you cross twice and recognise the second time.
- **Jerome is the exception:** he is the only one with a schedule, and the only one who can honestly say the sea is a distance to be covered.

> CLAUDE: It is a pool. A very large pool with a tide and no shallow end.

> ROLAND: Do not sit down. The sand is hotter than the path. I have made that mistake for you.

> JACK: You came from the north? Then you crossed the deep part. What was it like?

> JEROME: Bike tomorrow, run the day after. Today is only the water, and the water is going well.

- **Do not:** mention Blaine, the Gym, the Mansion, Entei, Bill, Silph or the convergence; turn any swimmer into a challenger; or let a line suggest the player has arrived "early".

## Inspiration

- **An open-water triathlon on a volcanic island.** Buoys, a start line on black sand, one athlete training alone because the race is months away, a town that smells of sulphur and salt. Converts into Jerome and into the local knowledge the others give away for free; the tileset and `WEATHER_SUNNY` already say black sand, so no line should contradict them with lush greenery.

## Implementation hooks

- Wiki page: `route21-south-frlg.html`
- Maps: `Route21_South_Frlg` (`MAP_ROUTE21_SOUTH`, `LAYOUT_ROUTE21_SOUTH`, 24×50, FRLG general and Cinnabar Island tilesets, music `MUS_RG_ROUTE3`)
- Scripts: `data/maps/Route21_South_Frlg/scripts.inc`; `PoxRegion_Arrival_Route21_South_Frlg` is an empty stub; talk wrappers in `data/scripts/plastic_ox_region.inc`
- Trainers / items: `TRAINER_FISHERMAN_CLAUDE`, `TRAINER_FISHERMAN_NOLAN`, `TRAINER_SWIMMER_MALE_JACK`, `TRAINER_SWIMMER_MALE_JEROME`, `TRAINER_SWIMMER_MALE_ROLAND` — all compiled out; the map carries no items
- Known gaps: the Cinnabar seam has no coordinate trigger while the island's other two edges do; the arrival script does nothing; the five parties cannot be fought; no signs, no hidden items, no item balls.

## Open questions

- Guard the beach with `FLAG_POX_STORY_FUJI` or `FLAG_POX_STORY_MANSION`? Recommend the second: it keeps Pallet's water visible, denies Cinnabar a back door, and matches pacing rule 9.
- Should the triathlon cast get one real event, or stay five people passing an afternoon?
- Is the silent beach arrival intentional, or an unfinished stub? Say which in the map notes.
