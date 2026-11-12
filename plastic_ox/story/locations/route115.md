---
title: Route 115
slug: route115
kind: Route
act: 5
stage: "13 — Meteor Falls"
depth: full
wiki: route115
maps: [Route115]
flags: [FLAG_POX_STORY_SPACE_CENTER, FLAG_POX_TRIGGERS_ENABLED, FLAG_ITEM_ROUTE_115_TM_FOCUS_PUNCH]
trainers: [TRAINER_TIMOTHY_1, TRAINER_NOB_1, TRAINER_CYNDY_1, TRAINER_KOICHI, TRAINER_HECTOR, TRAINER_KYRA, TRAINER_JAIDEN, TRAINER_HELENE, TRAINER_ALIX, TRAINER_MARLENE]
items: [ITEM_SUPER_POTION, ITEM_NUGGET, ITEM_IRON, ITEM_GREAT_BALL, ITEM_PP_UP, ITEM_HEAL_POWDER, ITEM_HEART_SCALE]
status: drafted
---

# Route 115

## Snapshot

A beach at the bottom, a stair-path up a cliff, a cave mouth at the top: the last outdoor ground before the final mountain. The player enters from Route 5 at `(20,79)`, climbs past ten trainers who all train with their hands, and leaves through `(27,37)` into Meteor Falls. Act V, stage 13, the OU approach to Blackthorn. The route exists to make the player feel over-prepared for a road and under-prepared for a cave, and its emotional note is **repetition**: the same hundred metres of sand, done again, better.

## Plot points

1. **The pass is visibly locked.** Stepping on `(20,79)` runs `PoxRegion_route5_route115_b`, which refuses until `FLAG_POX_STORY_SPACE_CENTER` and warps the player back to `(19,79)` with the generic closed text. The sign at `(19,78)` is the generator's "Route5 / Marked passage ahead." The player sees the road up before they may use it.
2. **The beach is a training floor.** Cyndy `(15,50)` explains why sand is a cushion; the hidden `ITEM_HEART_SCALE` sits one tile north at `(15,49)`, on the tide line. A single breakable rock at `(29,50)` is the route's only Rock Smash obstacle, and the berry trees at `(12,5)`–`(14,5)` and `(31,64)`–`(31,65)` are the last supplies before the cave.
3. **The climb is a dojo.** Ten trainers, mostly Fighting-, Normal-, and Flying-type teams: Koichi's Machop crew `(19,15)`, Timothy `(5,15)`, Nob `(27,53)`, Kyra running `(10,15)`, Jaiden in tree disguise `(11,12)`, Helene and Alix at the top `(15,7)`/`(10,7)`, Marlene meditating `(28,62)`, Hector with his collector's pair `(24,62)`. They are the route's population; nobody here is merely travelling.
4. **No story beat lives here.** Stage 13's reveal belongs to Blackthorn's Badge, not this road. The player may take it before or after Silph, so dialogue must not assume either state and must never mention the crisis.
5. **The cave mouth is the destination.** `(27,37)` warps to `MeteorFalls_1F_1R` `(6,39)` seamlessly, with no gate and no sign. Sea air to cave air is the whole transition; do not add a cutscene.
6. **Must not:** assume Silph is resolved; mention Saffron, the League, the system, or Bill; stage Rocket; turn the beach into a resort; make the trainers mystics or gurus. The mountain's mystery is one map north, not here.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| South crossing | `(20,79)` `PoxRegion_route5_route115_b` | `FLAG_POX_STORY_SPACE_CENTER` unset | generic closed text, warp to `(19,79)` | keep the lock; make the closed line about the pass and the weather, not "your next objective" |
| Sign | `(19,78)` `PoxRegion_route5_route115_b_Sign` | always | "Route5 / Marked passage ahead." | rewrite: last water, distance to the falls, what the cliff is called |
| Cyndy and the Heart Scale | `(15,50)` / `(15,49)` | always | vanilla sand-cushion line; hidden `ITEM_HEART_SCALE` on the next tile | let her point at the tide line; the scale should feel found, not awarded |
| Breakable rock | `(29,50)` `EventScript_RockSmash` | always | one boulder, no reason given | decide what it guards — a berry path or a shortcut — or delete it |
| Berry trees | `(12,5)`–`(14,5)`, `(31,64)`, `(31,65)` | always | five `BerryTreeScript` trees, unremarked | decide planted or wild; if wild, Cyndy can say nobody tends them |
| Trainers | Koichi `(19,15)`, Timothy `(5,15)`, Hector `(24,62)`, others | always | vanilla RS intro/defeat text, mons Lv 18–28 | rewrite as one training camp with its own etiquette; rescale to Act V |
| Item balls | `(20,60)`, `(18,7)`, `(23,29)`, `(31,56)`, `(26,67)`, `(12,14)` | item flags | `(18,7)` is flagged `FLAG_ITEM_ROUTE_115_TM_FOCUS_PUNCH` but contains `ITEM_NUGGET` | fix the mismatch: restore the TM or rename the flag to match the Nugget |
| Cave mouth | `(27,37)` → Meteor Falls `(6,39)` | always | seamless warp, no sign, no framing | keep seamless; a worn board at the mouth is enough |
| Dead warps | `(21,6)`, `(36,10)` | always | each warps to its own tile | delete, or wire them as Meteor Falls' upper entrances |

## Dialogue guidance

- **Who speaks:** fighters, one coach, a runner, a collector, and one person who came to sit by the water and got recruited into counting. They know training, injuries, weather, the tide, and that the cave is cold. They know nothing about the plot.
- **Register:** counts and breath. Short imperatives — "again", "lower", "reset", "hold" — and practical talk about taping a wrist or drying a shirt. No philosophy; that belongs to Meteor Falls.
- **Cyndy** is the route's explainer for the sand and the tide; **Koichi** is the coach who never raises his voice; **Hector** is the only person who talks about Pokémon as objects, and the route should gently punish him for it.
- **No flag shift.** The only change between visits is the weather — sun on the beach, wind at the top — and the player's own team. Do not invent a state switch.
- **Do not:** name Saffron, Silph, the League, or any Badge; use "convergence"; make the Black Belts stupid; call the mountain holy; write a healer or shop without a design decision.

> BLACK BELT: Sand first, then rock. Sand teaches you to land. Rock teaches you not to.

> CYNDY: Low tide's the good hour. The sand goes hard and nobody's had breakfast yet.

> RUNNER: I came up here to train. Now I mostly run down to the ferry and back. It's the same thing, I think.

> COLLECTOR: I keep rare Pokémon. I don't battle with them. It's more like housekeeping.

> LASS: Everyone on this cliff is shouting a number. I came for the view and now I'm counting too.

## Inspiration

- **Beach training culture:** dawn sand runs, hand wraps drying on a railing, a coach with a clicker, a taping table under a tarp. Gives the route its sound: feet, breath, counting.
- **Hoenn's Route 115 in RSE:** the southern beach, the hidden Heart Scale, the climb to Meteor Falls. Keep the shape and the reward; drop the Hoenn-specific flora talk.
- **Dojo hierarchy:** kohai carrying the water, sempai counting the reps, a wall of faded photographs. Converts directly into Koichi's Machop crew and the pairs at the top.
- **A threshold in elevation:** the last sun before a cave, the light changing with height, the temperature dropping ten steps before the entrance. That is the route's only "event".
- **Small commerce at the trailhead:** a cooler of cold drinks at the foot of the stairs, a van with its tailgate down, a hand-lettered price board. Give the job to one NPC rather than a shop menu.

## Implementation hooks

- Wiki page: `route115.html`
- Maps: `Route115` (`MAP_ROUTE115`, layout `LAYOUT_ROUTE115`, music `MUS_ROUTE104`), plus the handoff to `MeteorFalls_1F_1R` (`MAP_METEOR_FALLS_1F_1R`) at `(27,37)`
- Scripts: `data/maps/Route115/scripts.inc`, `data/scripts/plastic_ox_region.inc` (`PoxRegion_route5_route115_b`)
- Gates / flags: `FLAG_POX_STORY_SPACE_CENTER` on the south crossing; `FLAG_POX_TRIGGERS_ENABLED` bypasses gate text in the walkable build
- Trainers / items: ten `TRAINER_*` ids listed in front matter, mons Lv 18–28; `ITEM_SUPER_POTION`, `ITEM_IRON`, `ITEM_GREAT_BALL`, `ITEM_PP_UP`, `ITEM_HEAL_POWDER`, `ITEM_NUGGET`, `ITEM_HEART_SCALE`
- Known gaps: trainer levels (18–28) and encounters (Lv 23–25 Swablu/Taillow/Swellow; water Tentacool/Wingull/Pelipper; fishing Magikarp/Tentacool/Wailmer) are Hoenn-native and far below the Act V OU band; two self-warps at `(21,6)` and `(36,10)`; `Route115_EventScript_RouteSignRustboro` and `Route115_EventScript_MeteorFallsSign` exist but no sign object uses them; the TM ball at `(18,7)` gives a Nugget; the only sign is the generator's route placeholder; `PoxRegion_Arrival_Route115` is an empty stub.

## Open questions

- Rescale the trainers and encounters into the Act V band, or keep Route 115 as an optional low-level area for rematches? Recommend rescale — it is the only road to the eighth Badge.
- Is `(18,7)` meant to be the Focus Punch TM or a Nugget? Restore the TM, or rename the flag; do not ship a ball whose flag and contents disagree.
- Should the self-warps at `(21,6)` and `(36,10)` become Meteor Falls' upper entrances, as in Hoenn, or be deleted outright?
- Does the route need a rest stop — berry reset or a healer — before the cave, or is the mountain meant to be entered on supplies?
- Should the Heart Scale stay hidden, or become Cyndy's small reward for listening to her?
