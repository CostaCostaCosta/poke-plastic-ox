---
title: Route 21 North
slug: route21-north-frlg
kind: Route
act: 3
stage: "9 — Cinnabar and the Mansion"
depth: supporting
wiki: route21-north-frlg
maps: [Route21_North_Frlg]
flags: [FLAG_POX_STORY_FUJI, FLAG_POX_HIDDEN_V7_60]
items: [ITEM_PEARL]
status: drafted
---

# Route 21 North

## Snapshot

A 24×50 strip of Kanto sea between Pallet Town and Route 21 South. The player crosses it leaving Pallet's southern beach or climbing back from Cinnabar, and it awards nothing for the trip. It is filed under act 3 stage 9, but its job is geography: the childhood pond turns out to open onto an ocean, and the emotional note is departure.

## Plot points

1. **The gate is water, not a flag.** Pallet's south edge at `x 7–10` (rows 17–19) is surf-elevation water, and so are this map's first two rows at `(7–10, 0–1)`. Surf needs `ITEM_SURF_KEY`, which Fuji hands over in the conversation that sets `FLAG_POX_STORY_FUJI` and names the intended road — Route 8, the Underground Path, Route 7, Route 103. The coast opens at the exact moment the Cinnabar leg does.
2. **A parallel approach, not a second scene.** No flag changes here, and the route lands on Cinnabar's north beach without passing the `FLAG_POX_STORY_FUJI` guard at Cinnabar's `(12,12)`. Nothing here carries a reveal-ladder step; step 9 is the Mansion, and it stays there.
3. **Four parties, no battles.** Ronald, Wade, Spencer and the pair Lil and Ian have trainer entries in `trainers_frlg.inc`, but the bodies sit inside `.if IS_FRLG` and the Plastic Ox build compiles them out. Every object is a plain NPC printing its own post-battle line — the same wiring failure Route 8 has.
4. **A hillside of vines.** The grass table is twelve Tangela slots, Lv 17–28 — the original Route 21 quirk kept intact. Water is Tentacool 5–40; fishing runs to Lv 35 with Magikarp, Krabby, Horsea and Gyarados, plus Seadra and Psyduck in one variant and Kingler and Slowpoke in the other.
5. **Must not:** name Bill, Silph, Rocket or the convergence; explain Surf's origin; give the coast a Cinnabar revelation; restore the battles at levels that make the sea road mandatory.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Pallet surf seam | `(7–10, 0)` against `PalletTown_Frlg` rows 17–19 | Surf, `ITEM_SURF_KEY` | water on both sides, no trigger | keep; it is the route's only gate |
| Ronald | `(7,27)` | `Route21_North_EventScript_Ronald` | "I can't catch anything good." | the local who fishes badly on purpose |
| Wade | `(16,26)` | `Route21_North_EventScript_Wade` | six Magikarp, one punchline | keep the joke, give him a reason to be here |
| Spencer | `(12,44)` | `Route21_North_EventScript_Spencer` | sea versus mountains | a swimmer training for something off-map |
| Lil and Ian | `(14,35)`, `(15,35)` | two objects, one trainer id | the exercise joke, split across two people | rewrite as siblings on one errand; drop the weight jab |

## Dialogue guidance

- **Who speaks:** three men fishing a coast with no harbour and no boat, plus two siblings sent out together — the population of a place that exists because the water goes somewhere. Register: dry, practical, self-deprecating; the day is measured in wind and bait, not badges, and Spencer alone may mention elsewhere. Before and after the Surf unlock the lines are identical, because nobody hears them until they can cross.
- **Lil and Ian** keep the double act but lose the joke about her weight; their reason for being on the water should be mundane — a delivery, a bet, a cousin's boat.

> RONALD: Two hours out here and the line has not moved. I keep coming back for the not-moving.

> WADE: You know what a Magikarp is worth? Nothing. That's why I can afford to be good at catching them.

> SPENCER: Mountains are honest. You can see how far you have left. Out here it is all the same water.

> LIL: He said it would be quick. He says that about everything.

- **Do not:** mention Bill, Silph, Rocket, the convergence, or the Mansion's research; put a trainer challenge in anyone's mouth; explain the Surf Key; or let a fisherman talk about "the pool" (that belongs to the south map).

## Inspiration

- **The long swim home, through a Tangela hillside.** Gen 1's Route 21 is the water you cross to get back to Pallet, with nothing between the towns but trainers and vines. Keep the feeling of a crossing rather than a route — no signage, no shops, no reason to stop — and treat the twelve identical grass slots as a local fact: one rise of ground, nothing else growing on it.
- **A working shore, not a postcard.** Pallet's beach is a launch point for a kid, and this map is what the kid sees first: buoys, an unread noticeboard, the back of the lab's fence.

## Implementation hooks

- Wiki page: `route21-north-frlg.html`
- Maps: `Route21_North_Frlg` (`MAP_ROUTE21_NORTH`, `LAYOUT_ROUTE21_NORTH`, 24×50, the FRLG general and Pallet Town tilesets, music `MUS_RG_ROUTE3`)
- Scripts: `data/maps/Route21_North_Frlg/scripts.inc`; entry script `PoxRegion_Arrival_Route21_North_Frlg` is an empty stub; talk wrappers live in `data/scripts/plastic_ox_region.inc`
- Trainers / items: `TRAINER_FISHERMAN_RONALD`, `TRAINER_FISHERMAN_WADE`, `TRAINER_SWIMMER_MALE_SPENCER`, `TRAINER_SIS_AND_BRO_LIL_IAN` — compiled out; `ITEM_PEARL` hidden at `(17,42)`
- Known gaps: `Route21_North_SurfToPallet` and Pallet's `PalletTown_SurfToRoute21` are both dead labels; the fat-man clone never spawns; the four trainer parties exist but cannot be fought; the hidden `ITEM_PEARL` at `(17,42)` sits under `FLAG_POX_HIDDEN_V7_60` and is the map's only pickup.

## Open questions

- Gate the Cinnabar end, or accept the sea as a legitimate second road? Recommend a single guard on Route 21 South's beach so Cinnabar's north edge stops being the island's only ungated side.
- Restore Ronald, Wade, Spencer and Lil/Ian as fights at Lv 28–33, or keep the coast quiet — and is this an act-3 shortcut or a postgame return? Pacing rule 9 ("visible locked routes should later become meaningful shortcuts") supports the second; the current data accidentally provides the first.
