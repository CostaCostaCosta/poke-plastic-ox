---
title: Route 14
slug: route14-hns
kind: Route
act: 1
stage: "1 — Rustboro and Sea Cottage"
depth: supporting
wiki: route14-hns
maps: [Route14_hns]
flags: [FLAG_POX_HIDDEN_ROUTE14_23]
items: [ITEM_LUCKY_PUNCH]
status: drafted
---

# Route 14
## Snapshot
A coastal-road donor that was never wired: no connections, warps, coord events, or encounters, so the player cannot reach it. It holds three people and five cuttable trees, and the trees talk. `Route14_hns` is the least coherent map in the batch — a Kanto seaside stretch whose only concrete claim of geography puts Goldenrod somewhere south of it.

## Plot points
1. **No beat, because there is no visit.** `Route14_hns` (`MAP_ROUTE14_HNS`) is referenced by no warp, connection, or script in the checkout; nothing can enter or leave.
2. **Its objects are half-finished placeholders.** Five `OBJ_EVENT_GFX_CUTTABLE_TREE` objects carry NPC chatter scripts (`Route14_EventScript_Npc1`, `_Npc3`, `_Npc6`, `_Npc7`, `_Npc8`) instead of `EventScript_CutTree`, so the trees cannot be cut and speak when talked to.
3. **The named character repeats a tree.** `LOCALID_ROUTE14_EUSINE` at `(17,51)` has the same line as the trees around him, and the same character also stands on `Route25_hns` at `(99,23)` with a different line. One Eusine has to go.
4. **The geography is unsupported.** "South! GOLDENROD… trains to nowhere" describes a connection that does not exist in v7, where Goldenrod is reached from Mt. Moon and Route 35; a line like that must not ship on a map with no southern exit.
5. **Must not** be wired as a shortcut to Goldenrod, Lavender, or the postgame coast; no Rocket, no legend talk, no beast foreshadowing around Eusine.
## Key interactions
| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Cuttable trees | `(13,36)`, `(14,35)`, `(14,34)`, `(13,33)`, `(7,11)` `Route14_EventScript_Npc1`, `_Npc3`, `_Npc6`, `_Npc7`, `_Npc8` | none | two flavour lines on rotation ("Bird POKéMON ride the breeze…", "The tall grass rustles…") | `EventScript_CutTree` on all five, or delete them; at most one woodcutter NPC speaks |
| Eusine | `(17,51)` `LOCALID_ROUTE14_EUSINE`, `Route14_EventScript_Npc5` | none | repeats the tree line verbatim | remove this copy; keep the `Route25_hns` Eusine and give him one continuous thread |
| Balding Man | `(7,30)` `Route14_EventScript_Npc2` | none | "South! GOLDENROD. Bright lights, loud trains, trains to nowhere." | rewrite around the coast he can see, or cut the Goldenrod claim |
| Biker | `(18,19)` `Route14_EventScript_Npc4` | none | "My crew rides coast to coast now. Took a week to learn the turns." | keep; the only voice here that survives an audit |
| Hidden item | `(21,22)` `FLAG_POX_HIDDEN_ROUTE14_23` | flag unset | `ITEM_LUCKY_PUNCH` | keep only if the map is wired; a Chansey item on an empty road is a leftover |
## Dialogue guidance
If this coast is kept it is a road for people in motion: cyclists on a training loop, a retired man who walks the same mile, bird-watchers with binoculars and no birds. Nobody explains where the road goes; they describe wind, gears and knees.
> BIKER: Coast to coast is three turns and a headwind. Nobody warns you about the headwind.
> BIRD-WATCHER: Two of them, up there. Or the same one twice. I'm not counting anymore.
> OLD MAN: I walk to the third post and back. The third post is the whole of my day.
- **Do not:** let a tree speak, put Goldenrod within walking distance, or bring Suicune into a conversation before Ecruteak.

## Inspiration
- **The Dutch dune cycle path at Scheveningen** — headwind both ways, kiosks selling soup, birders with scopes: gives the Biker and the bird-watcher their jobs and the road its flatness.
- **Kanto Route 14 in RBY** — tall grass either side, bikers who challenge you, the sense of a road between two towns: keep the shape, discard the vanilla claims.
## Implementation hooks
- Wiki page: `route14-hns.html`; map `Route14_hns` (`MAP_ROUTE14_HNS`), group `gMapGroup_PlasticOxJohtoKanto`
- Scripts: `data/maps/Route14_hns/scripts.inc` — `Route14_EventScript_Npc1` … `Npc8`
- Known gaps: five trees with NPC scripts; `LOCALID_ROUTE14_EUSINE` duplicated from `Route25_hns`; no connections, warps, encounters, trainers, or map script.

## Open questions
- Keep or retire? Recommendation: **retire** `Route14_hns`; if a coastal road is wanted later, rewrite it from scratch with the biker and bird-watcher and give it a real connection.
- Which Eusine is canonical, `Route25_hns` `(99,23)` or this one? Decide before either is respoken, or the character appears twice with two personalities.
