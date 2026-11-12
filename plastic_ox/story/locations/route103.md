---
title: Route 103
slug: route103
kind: Route
act: 3
stage: "8 — Underground bypass"
depth: full
wiki: route103
maps: [Route103]
flags: [FLAG_POX_STORY_FUJI]
trainers: [TRAINER_MAY_ROUTE_103_TREECKO, TRAINER_PLASTIC_OX_ROUTE103, TRAINER_AMY_AND_LIV_1, TRAINER_ANDREW, TRAINER_MIGUEL_1, TRAINER_RHETT, TRAINER_MARCOS, TRAINER_ISABELLE, TRAINER_PETE]
items: [ITEM_GUARD_SPEC, ITEM_PP_UP]
status: drafted
---

# Route 103

## Snapshot

A low Hoenn coastal road that has been dropped between Saffron's west gate and Cinnabar's approach: sea on one side, grass banks on the other, an eighty-tile strip that ends at a ferry-less shore. The player arrives from Route 7 at `(78,11)`, walks west past berry trees and swimmers, and leaves south-west at `(75,15)` toward Cinnabar; the `down` connection to Oldale is a real road, not a story exit. It is the only place in the game where an act-3 player walks through the *shape* of a starter route, and the emotional result should be nostalgia with a small sting.

## Plot points

1. **Out of the junction.** `(78,11)` is the Route 7 crossing, opened by `FLAG_POX_STORY_FUJI`; the player lands on Route 103 at its eastern end, with the sea already audible. Reveal-ladder **step 8** ends here: the bypass around Saffron is complete and Cinnabar's records are next.
2. **Cinnabar is the forward exit.** `(75,15)` (`PoxRegion_route103_cinnabar_a`) is the road the story actually uses. Signs at `(75,13)` and `(78,10)` must point at Cinnabar and Route 7 — not at map names.
3. **Oldale is a real road.** The `down` connection at the south edge leads to `OldaleTown` and back into the opening network. It is a traversal payoff, not a scene: no cutscene, no guide, no quest. The bible's "return through geography adjacent to earlier portions of the world" is this connection.
4. **The locals are already written.** The man at `(49,12)`, the boy at `(20,10)`, the twins at `(64,12)`/`(65,12)`, the fisherman at `(50,8)`, the swimmers at `(36,6)`/`(36,13)`, Miguel at `(56,13)`, and Rhett/Marcos at `(67,5)`/`(67,9)` all speak in a consistent, gentle POX voice. Keep those voices; they need age and specificity, not replacement.
5. **The battle content does not match the act.** May at `(10,3)` is the RSE opening rival fight with `TRAINER_MAY_ROUTE_103_TREECKO` (a Lv. 5 Torchic), and `PoxRouteTrainer_Route103` at `(71,11)` is a six-Pokémon Lv. 5 team. Both are the first thing a late-game player meets. The other seven trainers sit at Lv. 15. This is the map's central implementation problem.
6. **Must not:** reinstate May as a rival or a recurring character; use Cinnabar research or Mansion records as conversation here (Fuji's directions and the Mansion own that); explain the convergence; let the Oldale road become a story gate.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Route 7 crossing | `Route103` `(79,11)` | `FLAG_POX_STORY_FUJI` | `PoxRegion_route7_route103_b` warps to `Route7_hns` `(1,23)` | keep |
| Cinnabar crossing | `(75,15)` | always | `PoxRegion_route103_cinnabar_a` warps onward | keep; sign at `(75,13)` should name the island and the ferry |
| Oldale connection | south edge | always | walkable connection to `OldaleTown` | keep; no NPC should comment on it as unusual |
| May | `(10,3)` | none — ungated | `Route103_EventScript_May` battles `TRAINER_MAY_ROUTE_103_TREECKO`, Torchic Lv. 5 | retire, or gate behind a flag and re-cast as a local kid; do not leave a Lv. 5 rival in act 3 |
| Route trainer | `(71,11)` | none | `PoxRouteTrainer_Route103` battles a six-Pokémon Lv. 5 team — first NPC met from Route 7 | retune to act-3 levels, or convert to a non-battling local who talks about the weather |
| Twins | `(64,12)` Liv, `(65,12)` Amy | none | `TRAINER_AMY_AND_LIV_1` (Plusle/Minun Lv. 15) with a surprise-gift shtick | keep the pair and the shtick; raise levels; the joke is that they plan aloud in front of each other |
| Fisherman | `(50,8)` | none | `TRAINER_ANDREW`, Magikarp/Tentacool Lv. 5–15 | keep the untangling-a-knot voice; make the battle optional or scaled |
| Miguel | `(56,13)` | none | `TRAINER_MIGUEL_1`, Skitty Lv. 15 | keep; he is the map's best voice — a spectator who cheers both sides |
| Rhett / Marcos | `(67,5)`, `(67,9)` | none | `TRAINER_RHETT` (Makuhita) and `TRAINER_MARCOS` (Voltorb), Lv. 15, facing each other | keep the pair and the mirrored movement; they are training together, not guarding a gate |
| Swimmers | `(36,6)` Isabelle, `(36,13)` Pete | none | `TRAINER_ISABELLE` (Marill), `TRAINER_PETE` (Tentacool), Lv. 15 | keep; both should talk about the water, not the battle |
| Boy | `(20,10)` | none | snack-packed, no Potion, resting | keep; he is the route's only self-deprecating voice |
| Berry trees | `(58,5)`–`(60,5)` | `BerryTreeScript` | three working berry trees with no explanation | let a local (or a new grower NPC) own them |
| Item balls | `(50,5)` Guard Spec, `(64,7)` PP Up | `FLAG_ITEM_ROUTE_103_GUARD_SPEC`, `FLAG_ITEM_ROUTE_103_PP_UP` | two `Common_EventScript_FindItem` pickups | keep |
| Signs | `(78,10)`, `(75,13)` objects plus identical bg events; `(11,9)` vanilla route sign | always | duplicated sign events; POX texts are placeholders | one sign per tile; rewrite the POX pair in-world, keep the vanilla "ROUTE 103 ↓ OLDALE TOWN" only if it is repainted |

## Dialogue guidance

- **Who speaks:** people who live on a road that used to be a first route. They are unhurried, they know the tide, and none of them is impressed by a Trainer with seven Badges.
- **Register:** warmer and slower than Route 8 — longer sentences, more weather, more food. Hoenn texture: humidity, salt, cicadas, rice balls, a road that floods at the morning high tide.
- **Before / after:** nothing here changes with story flags, and that is the point. The same people are on the same bank when the player comes back at the end of the game.
- **A small sting:** one person should recognise that the player has come a long way and treat it as ordinary — the route's emotional beat is being treated like a passing walker.
- **Do not** give anyone a line about the merged regions, the war, or the city behind the wall.

> BERRY GROWER: These three were planted for a ferry queue that never happened. Take what is ripe and leave the green ones.

> SWIMMER: The current runs west until noon. I go out early and let it bring me home.

> SPECTATOR: I clap for the other side too. Somebody has to, and their family never comes.

> TRAINING PARTNER: He counts my footwork out loud. I have never once asked him to stop.

- **Do not:** mention Saffron, Silph, Bill, or the League; make May a rival again; reuse Route 8's gate-and-queue imagery; write a fisherman who says "patience" (that is Route 12's word).

## Inspiration

- **Hoenn's Route 103 in RSE** — the first route with a rival, sea on one side and a hedge on the other, and a battle the player is supposed to lose or barely win. Converting that memory into an act-3 corridor is the whole trick: the layout is nostalgic, the player is not the same person.
- **The Shonan / Izu coast in late summer** — a road that floods at high tide, vending machines at the seawall, cicadas loud enough to drown a conversation. Gives the swimmers and the berry grower their weather.
- **The "return to the starting town" trope** in RPGs: the late-game walk back through trivial enemies, where the point is the walk and not the fights.
- **Japanese seaside fishing culture** — fixed nets, a cooler of ice, an aunt who sells the catch at the road. Converts into Andrew's knot and the berry trees.
- **Beach-episode pacing in the anime** — nothing happens, everyone eats, one character is quietly sad. That is the register for the whole map.

## Implementation hooks

- Wiki page: `route103.html`
- Maps: `Route103` (`MAP_ROUTE103`, layout `LAYOUT_ROUTE103`, 80×22), connection `down` to `OldaleTown`
- Scripts: `data/maps/Route103/scripts.inc`, generated `data/scripts/plastic_ox_region.inc` (`PoxRegion_route7_route103_b`, `PoxRegion_route103_cinnabar_a`), `data/scripts/plastic_ox_route_trainers.inc` (`PoxRouteTrainer_Route103`)
- Gates: `FLAG_POX_STORY_FUJI` on the Route 7 crossing; `FLAG_SYS_GAME_CLEAR` opens the Altering Cave mouth on load (`Route103_EventScript_OpenAlteringCave`, metatiles at `(45,5)`/`(45,6)`), with an inbound warp from `MAP_ALTERING_CAVE` at `(18,22)`
- Trainers / items: the nine `TRAINER_*` ids above; `ITEM_GUARD_SPEC` and `ITEM_PP_UP` in item balls; three berry trees at `(58,5)`–`(60,5)`; cut trees at `(67,7)` and `(72,8)`
- Encounters: `land_mons` rate 20, Wingull/Lotad/Poochyena/Seedot/Whismur/Electrike/Cacnea/Gulpin at Lv. 3–5 (a third duplicate table swaps in Grimer), and `fishing_mons` with Magikarp, Tentacool, Carvanha, Wailmer, Sharpedo, Crawdaunt, Huntail and Wailord — starter-route levels on an act-3 map
- Known gaps: May's Lv. 5 battle is ungated and only makes sense for a Treecko player; `TRAINER_PLASTIC_OX_ROUTE103` is a six-Pokémon Lv. 5 placeholder; seven more trainers at Lv. 15; `Route103_EventScript_Daisy` (`TRAINER_DAISY`) exists with no object; Birch's object is hidden from new game by `FLAG_HIDE_ROUTE_103_BIRCH`, so `ProfBirch_EventScript_RatePokedexOrRegister` is dead; both POX sign tiles carry an object and a background event at the same coordinate; the Lv. 5 trainer's intro is generated boilerplate ("The breeze keeps us cool here. My team can battle all day!") while its post-battle text is the good writing.

## Open questions

- Retire the Hoenn trainer cast (keep only the named voices), or retune all nine parties for the act-3 band? The mixed Lv. 5 / Lv. 15 spread cannot ship as is.
- Is May's battle worth keeping as an optional flashback-style encounter behind a flag, or should it be removed with her object?
- Should the Altering Cave link survive here, or move with the postgame coast? It currently opens only after `FLAG_SYS_GAME_CLEAR`.
- Do the wild tables get an act-3 pass (higher levels, fewer starter species), or does Route 103 stay deliberately easy to preserve the "walking back through the beginning" feeling?
