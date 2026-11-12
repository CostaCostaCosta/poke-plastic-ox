---
title: Route 4
slug: route4-hns
kind: Route
act: 1
stage: "1 — Rustboro and Sea Cottage"
depth: supporting
wiki: route4-hns
maps: [Route4_hns]
flags: [FLAG_POX_HIDDEN_ROUTE4_1, FLAG_POX_HIDDEN_ROUTE4_5, FLAG_POX_HIDDEN_ROUTE4_22]
items: [ITEM_POKE_BALL, ITEM_BIG_MUSHROOM]
status: drafted
---

# Route 4
## Snapshot
A second donor shell, and the better-written of the pair: `Route4_hns` has four talkers, two visible item balls and a hidden Big Mushroom, and no connections, warps, coord events, or encounters. Its own best line — "after a long cave walk, this open sky feels wonderful" — describes the job it would have if anyone wired it: decompression on the far side of Mt. Moon.

## Plot points
1. **No beat, because there is no visit.** `Route4_hns` (`MAP_ROUTE4_HNS`, layout `LAYOUT_ROUTE4_HNS`) is referenced by no warp, connection, or script in the checkout. It is the dead half of a duplicate pair; `Route4_Frlg` is the copy wired between `Route3_Frlg` and Cerulean.
2. **If it is restored**, its job is the *exit* side of the mountain — the first open sky after the cave, where trainers count their losses and eat. That fits stage 2 and would move with Mt. Moon's layout, not the Sea Cottage branch.
3. **Must not** ship as-is: the Cerulean/Blackthorn joke is a geography wink, both item balls pay out the same `ITEM_POKE_BALL`, and nothing here may hint at what is inside the mountain.

## Key interactions
| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Item balls | `(94,3)` `Route4_EventScript_Item1`, `(4,4)` `Route4_EventScript_Item5` | `FLAG_POX_HIDDEN_ROUTE4_1`, `_5` | both `finditem ITEM_POKE_BALL` | give one a held item or delete it; identical payouts read as a bug, and both flags say "HIDDEN" for visible balls |
| Picnicker | `(61,17)` `Route4_EventScript_Npc4` | none | "After a long cave walk, this open sky feels wonderful." | keep; it is the map's real thesis |
| Rocker | `(57,8)` `Route4_EventScript_Npc3` | none | "Everything east of here is new since last spring. Even the mountains." | keep, but move the observation onto weather or roadwork |
| Black Belt | `(50,3)` `Route4_EventScript_Npc6` | none | "Mountains keep showing up where fields used to be. Good training though." | keep; he is the one who should mention Mt. Moon's difficulty |
| Picnicker | `(67,4)` `Route4_EventScript_Npc2` | none | "CERULEAN's east. BLACKTHORN's… also sort of east. Long story." | delete the ellipsis joke; a local gives a distance, not a shrug |
| Hidden item | `(4,10)` `FLAG_POX_HIDDEN_ROUTE4_22` | flag unset | `ITEM_BIG_MUSHROOM` | keep; mushrooms belong on a damp post-cave slope |
## Dialogue guidance
Post-cave voices: relief, appetite, laundry, blisters. Everyone here has just finished something and is not interested in explaining the world; the Rocker and Black Belt use the road, the two Picnickers underestimated it.
> PICNICKER: I have grass in my socks, crumbs in my bag, and no regrets.
> BLACK BELT: If your team came out of that cave tired, feed them before you train them. That's the whole lesson.
> ROCKER: New road, old mountain. I still take the long way round.
- **Do not:** name Cerulean or Blackthorn as nearby, stage a Rocket sighting, or use "convergence".
## Inspiration
- **Post-hike motorway service stations in the Alps** — boots off, soup, a laminated map nobody trusts: becomes the picnic pair, and the item balls are the kit somebody left on a bench.
- **Mushroom foraging season** — locals with paper bags arguing about which slope is better: gives the Black Belt a second job and earns the hidden Big Mushroom.

## Implementation hooks
- Wiki page: `route4-hns.html`; map `Route4_hns` (`MAP_ROUTE4_HNS`), group `gMapGroup_PlasticOxJohtoKanto`
- Scripts: `data/maps/Route4_hns/scripts.inc` — `Route4_EventScript_Item1`, `Npc2`, `Npc3`, `Npc4`, `Item5`, `Npc6`
- Known gaps: no connections, warps, coord events, encounters, or map script; both balls pay the same item; no sign, heal, or trainer.

## Open questions
- Keep or retire? Recommendation: **retire** `Route4_hns` unless Mt. Moon's east exit is redrawn — in which case the tone is already right and only the talkers need rewriting.
- If retired, are `FLAG_POX_HIDDEN_ROUTE4_1` / `_5` freed for reuse, or does the block stay allocated for save compatibility?
