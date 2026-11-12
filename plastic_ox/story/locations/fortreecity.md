---
title: Fortree City
slug: fortreecity
kind: City
act: 2
stage: "5 — Route 119 and Fortree"
depth: full
wiki: fortreecity
maps: [FortreeCity]
also_maps: [FortreeCity_Gym]
flags: [FLAG_POX_REACHED_FORTREE, FLAG_POX_HIDE_STORY_NPCS, FLAG_KECLEON_FLED_FORTREE]
trainers: [TRAINER_PLASTIC_OX_WINONA]
status: drafted
---

# Fortree City

## Snapshot

A town built at canopy height: plank walkways between trunk platforms, rope and cable underfoot, and the ground only visible through gaps. Arriving from `Route119` requires `FLAG_POX_STORY_WEATHER` and sets `FLAG_POX_REACHED_FORTREE`, which permanently opens the west spur on `Route110`. The player then beats Winona for badge 4, and the east road to Lavender clears. Fortree is the game's last clean Gym before Lavender turns the story serious, so the town should feel like a holiday you are about to lose.

## Plot points

1. **Arrival from the gorge.** `(0,10)` `PoxRegion_route119_fortree_b` refuses until `FLAG_POX_STORY_WEATHER`. On arrival, `PoxRegion_Arrival_FortreeCity` sets `FLAG_POX_REACHED_FORTREE` when the Weather flag is held. That single flag is what folds the middle of the region together. It must **not** touch the Kecleon: the east walkway obstruction is a separate beat the player has to meet and clear.
2. **The town is a piece of infrastructure.** Everything the player can say about Fortree is about load, weather, and maintenance. Use the walkway as the local inconvenience: a span closed for repair, a rope replaced every spring, a queue at the ladder.
3. **Gym 4 — Winona (RU).** `FortreeCity_Gym` `(15,2)` runs `Pox_Winona`, which requires badge 3 and `FLAG_POX_STORY_WEATHER` and awards `FLAG_BADGE04_GET`. Do not confuse it with the vanilla `FortreeCity_Gym_EventScript_Winona` still sitting in the same file, which awards badge 6.
4. **A Kecleon blocks the east walkway — not the Gym.** An invisible Pokémon sits on the east walkway before the gate. Interacting with it gets a refusal ("Something invisible is in the way…") while badge 4 is unearned. On the first interaction after Winona's badge it reveals itself, flees (`FLAG_KECLEON_FLED_FORTREE`), and the walkway is clear; the east gate `(39,10)` `PoxRegion_fortree_route110_a` still checks badge 4 as the story gate. The Gym is never blocked by it — this is a road obstacle, not a Gym lock.
5. **The reporters are flavour, not a lock.** `(38,10)` GABBY and `(37,9)` TY wait for an interview and are hidden by `FLAG_BADGE04_GET`. Keep them as the last live remnant of the roaming-reporter system, with two distinct voices; the actual roadblock is the Kecleon.
6. **Bill is a signpost, not a subject.** `(7,7)` `Pox_CottageGuide` points toward the Sea Cottage near Rustboro, beyond Routes 24 and 25. That is texture; it must not sit next to reconstruction, networks, or the Weather Institute, and its geography does not currently parse.
7. **After badge 4.** The reporters go, the east road opens, and the town returns to being a place where people mend rope.

**Must not:** let Winona or anyone discuss the Institute's findings; place Bill's name near regional reconstruction or "the system"; leave the roadblock standing after the badge; treat Hoenn place names (Route 120, Route 131, Slateport) as reachable.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| West gate | `(0,10)` `PoxRegion_route119_fortree_b` | `FLAG_POX_STORY_WEATHER` | generic closed text and a bounce back | keep the gate; add a rope-mender at the barrier so the refusal has a face |
| Arrival script | `PoxRegion_Arrival_FortreeCity` | every entry | currently hides Kecleon and sets the fled flag on entry | remove both Kecleon writes; keep setting `FLAG_POX_REACHED_FORTREE` when the Weather flag is held |
| Kecleon (east walkway) | east path before `(39,10)` — pick the chokepoint tile | `FLAG_KECLEON_FLED_FORTREE` unset | object is gated by `FLAG_POX_HIDE_UNUSED_ACTOR` and never appears | place it on the walkway, hidden by `FLAG_KECLEON_FLED_FORTREE`; badge 3 + Weather still gate the Gym, badge 4 clears the roadblock |
| Kecleon interaction | same tile | badge 4 unset | — | "Something invisible is in the way." No battle, no item, no reveal of what it is |
| Kecleon cleared | same tile | badge 4 set, fled flag unset | — | short reveal, set `FLAG_KECLEON_FLED_FORTREE`, remove the object, let the gate work |
| East gate | `(39,10)` `PoxRegion_fortree_route110_a` | badge 4 | warps to `Route110` `(17,0)` | keep; the junction should look like a road, not a checkpoint |
| Reporters | `(38,10)` GABBY, `(37,9)` TY | hidden by `FLAG_BADGE04_GET` | two roadblock lines about the interview | keep; they are the only live part of the roaming-reporter system, so give them two distinct voices |
| Woman near the Gym | `(32,10)` | always | her "something's blocking the gym" branch is dead and now wrong: the Gym was never blocked | replace with a line about the Gym queue or the thing on the east walkway; no blocked-Gym branch |
| Sky watcher | `(31,3)` | always | claims a huge Pokémon flew toward Route 131, then says the player smells singed | recast: a local bearing instead of a Hoenn route, and "smoke" instead of "volcano" — the player has just come from the Burned Tower |
| Cottage guide | `(7,7)` `Pox_CottageGuide` | `FLAG_POX_HIDE_STORY_NPCS` unset | "BILL's SEA COTTAGE is near RUSTBORO, beyond ROUTES 24 and 25" | fix the geography or make it a shrug; Bill must stay ordinary texture |
| Lavender road | `(8,8)` `Pox_LavenderRoad` | `FLAG_POX_HIDE_STORY_NPCS` unset | east road joins Route 110, south to Lavender | keep; it is the only correct direction in town |
| Signs | `(0,8)`, `(38,9)` | always | both read "Marked passage ahead." | replace with a walkway load notice and a road junction sign |
| Gym guide | `(15,21)` | always | promises "rotating doors" and a leader at the back | verify the rotating-door puzzle still exists; otherwise rewrite the line |
| Gym trainers | `(4,14)`, `(10,10)`, `(5,17)`, `(9,8)`, `(4,23)`, `(1,10)` | badge 4 unset | six Flying-type trainers on vanilla text | keep the teams; give each a distinct reason to be in a Gym on stilts |

## Dialogue guidance

- **Fortree talks about maintenance.** Rope, cable, load, span, weather, who is allowed on a walkway while it is being worked on. The town's charm comes from engineering, not whimsy.
- **The Gym trainers are athletes,** proud of a leader who is genuinely strong; one should be a little bit in love with her and one should be entirely professional.
- **GABBY is broadcast-loud and TY is the technician.** They are a two-hander; neither should ever speak alone in the same register.
- **The sky watcher** is the town's unreliable narrator. He should be specific and slightly defensive: a bearing, an hour, and the fact that nobody else looked up.
- After badge 4 the town is unchanged except for the road: no cheering, no crowd, one person mentions it in passing.

> ROPE MENDER: Every walkway here is somebody's job. I get the one over the market, because that's the one the weather gets to first.

> RESIDENT: You can hear the whole town through the floorboards. That's the rent you pay for living up here.

> GABBY: We are not moving until she's beaten. A champion interview is worth more than a road, and I have the tape to prove it.

> SKY WATCHER: Third hour, west of the smoke, higher than the ridge. Nobody else was looking up. That's not my fault.

- **Do not:** say "convergence"; have anyone explain the convergence; put Bill next to the Weather Institute or networks; use Hoenn route numbers as directions; make the reporters cruel.

## Inspiration

- **Canopy walkways in Malaysian and Costa Rican rainforest parks:** steel cable, aluminium grating, a load rating stencilled at each end. This is the town's architecture and its small talk.
- **Japanese rural suspension footbridges (tanikaze-bashi):** one person wide, swaying, replaced plank by plank. Converts to the rope mender and the closed-span beat.
- **Pacific Northwest treehouse builders:** a community of people who own specific tools and argue about bracing. Gives the town three trades in one afternoon.
- **Local birdwatching culture:** a chalkboard of sightings, a patch list, the bird nobody else saw. That is the sky watcher's whole character, and it earns his tall tale.
- **RSE Fortree City:** homes on platforms, a Kecleon on the bridge, Winona's Gym above the canopy. The reference is the *vertical town* and the invisible roadblock — keep both ideas, fix the execution.

## Implementation hooks

- Wiki page: `fortreecity.html`
- Maps: `FortreeCity` (`MAP_FORTREE_CITY`), `FortreeCity_Gym` (`MAP_FORTREE_CITY_GYM`)
- Scripts: `data/maps/FortreeCity/scripts.inc` (`FortreeCity_EventScript_Man`, `_Woman`, `_OldMan`, `_GabbyRoadblock`, `_TyRoadblock`, `_Kecleon`), `data/maps/FortreeCity_Gym/scripts.inc`, `data/scripts/plastic_ox_region.inc` (`PoxRegion_Arrival_FortreeCity`, `PoxRegion_route119_fortree_b`, `PoxRegion_fortree_route110_a`), `data/scripts/plastic_ox_story.inc` (`Pox_Winona`, `Pox_CottageGuide`, `Pox_LavenderRoad`)
- Flags: `FLAG_POX_REACHED_FORTREE`, `FLAG_KECLEON_FLED_FORTREE` (set only when the Kecleon flees), `FLAG_POX_HIDE_STORY_NPCS`, `FLAG_BADGE04_GET`
- Trainers: `TRAINER_PLASTIC_OX_WINONA` (Lv.33–36, RU)
- Known gaps: the arrival script sets `FLAG_KECLEON_FLED_FORTREE` unconditionally (must be removed); the Kecleon object is gated by `FLAG_POX_HIDE_UNUSED_ACTOR`, a flag with no story meaning; the vanilla `FortreeCity_Gym_EventScript_Winona` (badge 6, `TRAINER_WINONA_1`, TM Aerial Ace) is still present but not called by the live object; the cottage guide's directions mix Hoenn and Kanto; the sky watcher references Route 131 and a volcano; both edge signs are identical; GABBY and TY are the last live remnant of the roaming reporter system.

## Open questions

- Kecleon resolution (design decision, 2026-11-11): it blocks the **east exit**, never the Gym, and clears on badge 4. Which exact walkway tile is the chokepoint, and should the reporters stand behind it or in front of it?
- Does the rotating-door Gym puzzle survive in `FortreeCity_Gym`, or should the guide stop promising it?
- Recast the sky watcher's sighting as a genuinely displaced flying Pokémon (the sages' mission), or keep it as a local tall tale that never pays off?
- Fix the Sea Cottage directions, or cut the cottage guide and let the cottage stay a discovery? Its current geography is three regions in one sentence.
