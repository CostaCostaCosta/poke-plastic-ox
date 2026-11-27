---
title: Dragon's Den
slug: dragonsden-entrance-hns
kind: Cave
act: 6
stage: "17 — Post-game"
depth: supporting
wiki: dragonsden-entrance-hns
maps: [DragonsDen_Entrance_hns]
also_maps: [DragonsDen_Cavern_hns]
flags: [FLAG_SYS_GAME_CLEAR, FLAG_POX_DEN_RAYQUAZA_ARRIVED, FLAG_POX_CAUGHT_RAYQUAZA, FLAG_POX_HIDE_DRAGONS_DEN_PP_MAX, FLAG_POX_HIDE_DRAGONS_DEN_MAX_POTION, FLAG_POX_HIDE_DRAGONS_DEN_DRAGON_FANG]
items: [ITEM_PP_MAX, ITEM_MAX_POTION, ITEM_DRAGON_FANG]
status: implemented
---

# Dragon's Den

## Snapshot

A post-game cave behind Blackthorn. The door sits on the north shore of the town's lake (`BlackthornCity_hns` `(26,12)`, reached by Surf), and an elder stands in it until the player is in the Hall of Fame. Inside, a short entrance room and a ladder lead to the flooded cavern; the player surfs south to the shrine plaza, where RAYQUAZA comes down out of the dark. The emotional note is *still water, then weather*: a quiet cave that turns out to have a sky in it.

## Plot points

1. **Kept shut.** The elder (`BlackthornCity_EventScript_DenElder`, `(26,13)`) is hidden by `FLAG_SYS_GAME_CLEAR`. Before the Hall of Fame he says the POKéMON inside are far too powerful and turns the player around; afterwards he is gone and the door is open.
2. **The water.** `DragonsDen_Cavern_hns` has no land encounters. Surfing and fishing give DRATINI, DRAGONAIR, HORSEA, SEADRA, MAGIKARP and GYARADOS at Lv.45–60. Three item balls sit on the outer ledges: PP MAX, MAX POTION, DRAGON FANG.
3. **The arrival.** Stepping off the dock onto the shrine plaza (`(30–32,36)`, `PoxDragonsDen_RayquazaArrives`) plays once: the cavern shakes, a cry comes from overhead, the screen whites out, and RAYQUAZA is on the plaza, uncoiling and roaring. It sets `FLAG_POX_DEN_RAYQUAZA_ARRIVED`.
4. **The battle.** Talking to RAYQUAZA (`PoxDragonsDen_Rayquaza`, `(31,40)`) wakes it (roar, camera shake, white flash) and starts an ordinary legendary battle with its own transition and theme. It is Lv.70, or the level of the party's strongest POKéMON when that is higher. There is no guaranteed capture. Fleeing, fainting it or losing leaves it on the plaza; only a catch sets `FLAG_POX_CAUGHT_RAYQUAZA` and removes it for good.
5. **Must not:** explain why a Hoenn legend is in a Johto cave, connect it to the convergence, bring CLAIR or LANCE into the Den, or add a sage: this one is not a reward battle.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Den elder | `BlackthornCity_hns` `(26,13)` `BlackthornCity_EventScript_DenElder` | hidden by `FLAG_SYS_GAME_CLEAR` | explains the closure and blocks the door | keep |
| Den door | `BlackthornCity_hns` `(26,12)` | warp 3 | to `DragonsDen_Entrance_hns` warp 0 `(4,5)` | keep |
| Arrival scene | `DragonsDen_Cavern_hns` `(30–32,36)` `PoxDragonsDen_RayquazaArrives` | `VAR_TEMP_1` 0, i.e. `FLAG_POX_DEN_RAYQUAZA_ARRIVED` unset | one-time scene, then RAYQUAZA stays on the plaza | keep |
| RAYQUAZA | `DragonsDen_Cavern_hns` `(31,40)` `PoxDragonsDen_Rayquaza` | hidden until arrival and after `FLAG_POX_CAUGHT_RAYQUAZA` | wake animation, then a normal wild battle at Lv.70 or the party's top level | keep |
| Item balls | `DragonsDen_Cavern_hns` `(54,50)`, `(7,35)`, `(54,28)` | `FLAG_POX_HIDE_DRAGONS_DEN_PP_MAX`, `FLAG_POX_HIDE_DRAGONS_DEN_MAX_POTION`, `FLAG_POX_HIDE_DRAGONS_DEN_DRAGON_FANG` | PP MAX, MAX POTION, DRAGON FANG | keep |
| Statues, shrine door | `DragonsDen_Cavern_hns` `PoxDragonsDen_Statue`, `PoxDragonsDen_ShrineDoor` `(31,46)` | always | one line each; the shrine is barred | keep until the shrine interior is imported |

## Dialogue guidance

- **Voices:** one elder who has kept a door for forty years and is bored of being argued with; RAYQUAZA, described, never quoted. Nobody else is in the Den.
- **Register:** plain and short. The elder states a rule and its one exception. The cavern's own text is narration in a single sentence.

> ELDER: The POKéMON inside are far too powerful. I've turned GYM LEADERS around on this step.

> ELDER: The only name that opens it is one written in the HALL OF FAME.

> RAYQUAZA came down out of the dark and settled in front of the shrine!

> The water went still. The DEN is quiet again.

- **Do not:** give the elder prophecy or a test of character, name RAYQUAZA before the player has seen it, or reuse the Route 24 officer's wording.

## Inspiration

- **Dragon's Den in Gold/Silver/HGSS** — the flooded cave behind Blackthorn with a shrine on an island; kept as geography, without the elder's quiz.
- **Sky Pillar in Emerald** — RAYQUAZA's coiled sprite, its stir and roar; reused here as the arrival and wake animations.
- **A shrine keeper at a closed gate** — one person, one rule, no ceremony. Converts to the elder and to the barred shrine door.

## Implementation hooks

- Import: `plastic_ox/alpha/import_dragons_den.py` (layouts, both maps, the cavern's wild tables, the Blackthorn warp and elder; map groups `gMapGroup_PlasticOxDungeons` and `gMapGroup_DragonsDen`).
- Scripts: `data/maps/DragonsDen_Cavern_hns/scripts.inc`; elder in `data/maps/BlackthornCity_hns/scripts.inc`; special `PoxRaiseWildMonToPartyLevel` in `src/battle_setup.c`.
- Flags: `FLAG_POX_CAUGHT_RAYQUAZA` (POX ext +18), `FLAG_POX_DEN_RAYQUAZA_ARRIVED` (+19), item balls +20 to +22, gate `FLAG_SYS_GAME_CLEAR`.
- Test: `plastic_ox/demo/test_dragons_den.py`.
- Known gaps: the shrine interior, the donor's whirlpools, decorative POKéMON and hidden items were not imported; music is `MUS_RG_SEVII_CAVE` because the HGSS Den theme is not in this ROM; tileset animations are static.

## Open questions

- The bible puts Uber-tier POKéMON on the post-game islands. RAYQUAZA in the Den is an exception by request; should KYOGRE and GROUDON follow the same pattern or wait for the islands?
- Should RAYQUAZA come back after a new Hall of Fame entry if the player faints it, or is staying put until caught right?
- Import the shrine interior, and if so, who is in it?
