---
title: Route 24
slug: route24-hns
kind: Route
act: 1
stage: "1 — Rustboro and Sea Cottage"
depth: full
wiki: route24-hns
maps: [Route24_hns]
flags: [FLAG_POX_ROUTE24_NUGGET, FLAG_POX_HIDDEN_ROUTE24_18]
trainers: [TRAINER_PLASTIC_OX_ROUTE24_ROCKET, TRAINER_PLASTIC_OX_ROUTE24]
items: [ITEM_NUGGET, ITEM_PECHA_BERRY]
status: drafted
---

# Route 24

## Snapshot
The short northern road out of Rustboro, running up to Route 25 and the Sea Cottage branch. `Route24_hns` connects down to `RustboroCity` and up to `Route25_hns`, so it is the only corridor the optional Eevee trip uses; skipping it costs nothing, walking it costs twenty minutes. Its encounter table is almost entirely baby Pokémon, which quietly makes it the nursery road to the house where an Eevee is waiting.

## Plot points
1. **A branch, not a gate.** The road exists to be taken or ignored. No NPC stops the player, no flag opens it, and the connection pair does all the work; the cottage trip must stay optional and short.
2. **The nursery road.** Wild land encounters are Pichu, Cleffa, Igglybuff, Togepi, Tyrogue, Azurill, Mareep, Smoochum, Snubbull and Elekid at Lv.8–11, and the fishing table adds Politoed and Azumarill. Route 24 is where the game first says "small things live here", which is exactly the road that should lead to Bill's grandfather and his Eevee.
3. **The lost grunt stays.** `Route24_EventScript_Npc1` is a `ROCKET_M` trainer (`TRAINER_PLASTIC_OX_ROUTE24_ROCKET`) who was told to find a cave and got lost. This is an approved incidental Rocket appearance, not one of the three story beats: he is comic, badly over-levelled for his own competence, and reveals nothing. Keep him, and keep his "don't tell the BOSS" line about the cave — it is a fine rumour without naming anything.
4. **The spare trainer is a later problem, not a rebrand.** `TRAINER_PLASTIC_OX_ROUTE24` (ETHAN, Youngster) is authored but unplaced. Do not use him to replace the grunt. He can be placed elsewhere on the route later if the road needs a second battle.
5. **Must not:** let the grunt name the cave's contents, fossils, Silph, or the convergence. The moved roads are a joke about getting lost, not a mystery.

## Key interactions
| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Rocket grunt (trainer) | `(18,8)` `Route24_EventScript_Npc1` | `TRAINER_PLASTIC_OX_ROUTE24_ROCKET` | battles, then "I was told to go to a cave, but I got lost… Don't tell the BOSS!" | keep the character and the battle; tighten the line so the cave is a rumour, not a destination hint |
| Worker | `(16,7)` `Route24_EventScript_Npc2` | none | walks off the day's dust, prefers a battle to sitting at home | keep; the road's one working adult |
| Woman | `(16,8)` `Route24_EventScript_Npc3` | none | "RUSTBORO is just south… the cottage lies farther north. I only meant to take a short walk." | keep; this is the branch's only signpost and it is well phrased |
| Fisherman | `(19,12)` `Route24_EventScript_Npc4` | none | lunch and bait in separate tins, checked twice | keep; small, true, and it teaches the player that the water is fishable |
| Nugget ball | `(26,20)` `Common_EventScript_FindItem` | `FLAG_POX_ROUTE24_NUGGET` | gives `ITEM_NUGGET` | keep; the only "reward" on the branch and it should feel like finding money in a coat |
| Hidden item | `(24,20)` `FLAG_POX_HIDDEN_ROUTE24_18` | flag unset | `ITEM_PECHA_BERRY` two tiles from the Nugget | move it north of the bridge; two collectibles on one screen flattens both |
| Trainer script | `data/scripts/plastic_ox_route_trainers.inc` `PoxRouteTrainer_Route24` | never called | complete battle script for `TRAINER_PLASTIC_OX_ROUTE24`, attached to no object | attach it to the recast `(18,8)` trainer or delete it |
| Encounter table | whole map | three identical `land_mons` slots | Pichu…Elekid at Lv.8–11 repeated three times | collapse to one table; the repetition looks like a copy error and hides any intended slot split |

## Dialogue guidance
- **Voices:** a young trainer who is embarrassed about being lost, a woman on a walk she keeps extending, a worker who would rather battle than go home, and a fisherman protecting his lunch from his bait.
- **Register:** plain, dry, domestic. Nothing on this road is dramatic; the only tension is whether someone admits they took a wrong turn.
- The route is a corridor between a city and a cottage, so people talk about *distance and timing* — how far, how long, whether they will be back before dark.
- After the cottage Eevee, nobody comments on it. The gift stays a private thing.

> YOUNGSTER: I know the road goes north. I just don't know which north. There are two.

> WOMAN: I said I'd go as far as the bend. The bend moved, so I kept walking.

> FISHERMAN: Lunch is in the red tin. Bait is in the blue tin. I've written it on both tins.

- **Do not:** give any NPC a Team Rocket line, name the cottage's owner as a scientist or inventor, or hint that Eevee is anything more than a Pokémon that needs a home.

## Inspiration
- **A suburban footpath at the edge of a town** — allotments, a gate that sticks, dog walkers who greet strangers: converts into the woman and worker, and gives the branch the feeling of a place locals use and visitors find by accident.
- **A pond behind a garden centre** — fathers with cheap rods, kids with nets, one enormous carp nobody catches: source of the fisherman and the Politoed/Azumarill table.
- **Gen 2's baby-Pokémon roster** (Pichu, Cleffa, Togepi, Elekid) — the route is a nursery in the most literal sense; use it to seed the cottage's trade chain rather than explaining breeding.
- **Conversion:** four adult jobs (walker, worker, angler, lost kid) and one reward; that is all a twenty-minute branch needs.

## Implementation hooks
- Wiki page: `route24-hns.html`; map `Route24_hns` (`MAP_ROUTE24_HNS`), group `gMapGroup_PlasticOxJohtoKanto`, connections down to `RustboroCity`, up to `Route25_hns`
- Scripts: `data/maps/Route24_hns/scripts.inc` — `Route24_EventScript_Npc1` … `Npc4`; unused `PoxRouteTrainer_Route24` in `data/scripts/plastic_ox_route_trainers.inc`
- Flags: `FLAG_POX_ROUTE24_NUGGET`, `FLAG_POX_HIDDEN_ROUTE24_18`
- Trainers: `TRAINER_PLASTIC_OX_ROUTE24_ROCKET` (six mons, Lv.12 — an approved incidental Rocket, deliberately stronger than his story role suggests), `TRAINER_PLASTIC_OX_ROUTE24` (authored, unplaced)
- Known gaps: orphaned trainer script; three identical encounter blocks; no sign, heal, or warp events.

## Open questions
- The grunt is approved as an incidental Rocket encounter (design decision, 2026-11-11); no move or recast. Should his six-mon Lv.12 party be trimmed so he reads as lost rather than elite?
- Should the route keep three identical `land_mons` blocks (if the engine uses them as day/night slots) or collapse to one? Nothing in the data distinguishes them today.
- Does the Nugget need a flag at all, or should it be the visible reward the player sees from the bridge? `FLAG_POX_ROUTE24_NUGGET` currently hides a ball that is not hidden.
