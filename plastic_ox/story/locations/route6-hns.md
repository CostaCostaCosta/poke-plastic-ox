---
title: Route 6
slug: route6-hns
kind: Route
act: 4
stage: "10 — Saffron hub"
depth: supporting
wiki: route6-hns
maps: [Route6_hns]
also_maps: [Gate_SaffronCity_Route6_hns]
flags: [FLAG_POX_STORY_SPACE_CENTER, FLAG_POX_HIDDEN_ROUTE6_3]
items: [ITEM_POKE_BALL]
status: drafted
---

# Route 6

## Snapshot

A flat lawn route with a campsite, a bench, and one item ball, sitting where a Kanto road would sit south of Saffron. In the intended graph this is the city's back porch — the last quiet grass before the gates, open only once the city opens. In the current build **the player cannot reach it**: `Route6_hns` has no warps, no connections, and no triggers, so it is dressing for a gate that has not been installed.

## Plot points

1. **Audit first.** The map holds three objects and nothing else: a camper `(41,25)`, a balding man `(30,17)`, a ball `(28,25)`. The gate interior `Gate_SaffronCity_Route6_hns` holds one policeman `(3,6)` and also has **no warps**. Nothing in `data/` references either map id.
2. **The south lock lives elsewhere.** Every working Saffron approach checks `FLAG_POX_STORY_SPACE_CENTER`; the southern one is `PoxRegion_route19_saffron_a` / `_b` on `Route19_Frlg`, not this map. If Route 6 is wired, its gate must reuse that flag and refusal, not invent a condition.
3. **Intended shape, if kept.** Grass and a rest stop before the gatehouse; the policeman checks the player before the Space Center and waves them through after. No cutscene and no new objective — Route 6 is a door, not a chapter.
4. **Step 12 of the ladder is the only one it can touch**, and even that happens at the gate, not in the grass.

**Must not:** explain why Saffron is sealed; let the player into the city early; add Rocket, Silph, or a plot item; turn the policeman into a lore NPC.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Entry | `Route6_hns` | none | no warp, connection, or trigger reaches this map | add gate and grass-mouth warps, or retire it |
| Camper | `(41,25)` | always | "Travelers heading toward SAFFRON often stop here for a breather." | someone eating lunch on the way home |
| Balding man | `(30,17)` | always | "City noise fades quickly when you walk into the grass." | a retiree who walks the loop for quiet |
| Item ball | `(28,25)` | `FLAG_POX_HIDDEN_ROUTE6_3` | `Route6_EventScript_Item3` → `ITEM_POKE_BALL` | keep; the flag is named "hidden" for a visible ball |
| Gate policeman | gate `(3,6)` | always | "Keep the doorway clear so travelers can pass safely." — byte-identical to the Route 5 gate | one gate, one line; rewrite the other |
| Saffron lock | `Route19_Frlg` | `FLAG_POX_STORY_SPACE_CENTER` | `PoxRegion_route19_saffron_a` / `_b` refuse before the Space Center | copy this contract if wiring |

## Dialogue guidance

- **The camper** is on a lunch break, not an expedition: the walk, the price of a sandwich, how the city looks from outside. **The balding man** walks the same loop daily and knows which bench stays dry; he still refuses to speculate. **The policeman** directs traffic — bored, polite, uninterested in the player's business.
- Register: unhurried small talk, no exclamation marks. This is a route people cross, not adventure on.

> CAMPER: I take the long way home through the grass. Twenty minutes longer, and nobody asks me anything.

> BALDING MAN: Third bench from the gate is the dry one. Learn the benches and you'll never need a weather report.

> POLICEMAN: Keep the doorway clear, please. Both directions.

- **Do not:** mention Silph, the Space Center, or Mossdeep; hint that the grass hides anything; give the officer a security speech.

## Inspiration

- **The green ring around a walled city:** office workers at lunch, a mown strip, a jogging loop, an always-full bin. Converts to the camper and the retiree as two kinds of break.
- **Gen 1 Route 6:** tall grass between two gates and the first sense that the city is close. Keep the betweenness; the route is a threshold.
- **Gate traffic:** a guard who waves hundreds of people through a day and remembers none. That is the policeman entire.

## Implementation hooks

- Wiki page: `route6-hns.html`
- Maps: `Route6_hns` (`MAP_ROUTE6_HNS`), `Gate_SaffronCity_Route6_hns` (`MAP_GATE_SAFFRON_CITY_ROUTE6_HNS`)
- Scripts: `data/maps/Route6_hns/scripts.inc`, `data/maps/Gate_SaffronCity_Route6_hns/scripts.inc`, `data/scripts/plastic_ox_region.inc` (Route 19 lock)
- Known gaps: **0 warps and 0 connections on both maps**; both city NPCs are set to trainer type `NORMAL` with sight 4 but only show a msgbox, so they will walk up and talk; the officer's line is identical at both Saffron gates; the populated donor `Route6_Frlg` still exists and no note claims it.

## Open questions

- Wire Route 6 as Saffron's southern pedestrian gate, or retire it and leave the role to `Route19_Frlg`?
- If wired, is the grass reachable before `FLAG_POX_STORY_SPACE_CENTER` so the player can look at the sealed city?
- Delete the donor `Route6_Frlg`?
