---
title: Ilex Forest
slug: ilexforest-hns
kind: Route
act: 1
stage: "0 — Opening network"
depth: full
wiki: ilexforest-hns
maps: [IlexForest_hns]
also_maps: [Gate_AzaleaTown_IlexForest_hns]
flags: [FLAG_POX_STORY_ILEX, FLAG_POX_STORY_STARTER, FLAG_POX_TRIGGERS_ENABLED]
trainers: [TRAINER_PLASTIC_OX_ROUTE_ILEX, TRAINER_PLASTIC_OX_ROUTE_ILEX_FINN, TRAINER_PLASTIC_OX_ROUTE_ILEX_MAYA]
items: [ITEM_HEADBUTT_KEY, ITEM_POKE_BALL, ITEM_TINY_MUSHROOM, ITEM_BIG_MUSHROOM, ITEM_ANTIDOTE]
status: drafted
---

# Ilex Forest

## Snapshot

An 82×73 wood crossed once, south door `(22,63)` to north door `(20,15)`, on the only road from Cherrygrove to Rustboro. The player forages, takes a loaned Headbutt Key, meets three optional trainers, and finishes the Ilex objective that clears the Route 2 hiker and admits them to Roxanne. Reveal-ladder **step 1** and no further: the trees are old, the path is worn, and the forest is the last long breath before the first Gym. Emotional note: *work*, not wonder — a wood that people use every day.

## Plot points

1. **A crossing, not a dungeon.** Two doors, one road, no cutscene on entry. `PoxRegion_Arrival_IlexForest_hns` is an empty map script. The forest is the last Little Cup team-building space before Roxanne; fill it with encounters and foraging, not with a set piece.
2. **The objective is a greeting.** `Pox_Ilex` at `(26,42)` sets `FLAG_POX_STORY_ILEX` on first talk when `FLAG_POX_STORY_STARTER` is set, and every `Pox_*` script is gated by `FLAG_POX_TRIGGERS_ENABLED`. That flag does two real things: it hides the Route 2 hiker at `(8,0)` (`PoxRoute2_RustboroGate`, whose line is "RUSTBORO will have to wait. Take the ILEX FOREST trail first.") and it satisfies `Pox_Roxanne`'s prerequisite. So the forest is the toll gate to Gym 1, and the toll is a conversation with a man stretching his legs. This is the weakest link in the opening and the one beat worth moving.
3. **Headbutt is the loan.** The fat man at `(42,26)` hands over `ITEM_HEADBUTT_KEY`; the tree behind him at `(39,7)` runs `PlasticOx_EventScript_HeadbuttTree`; Wayne at `(39,8)` is the demonstration. Keep the three-part lesson: tool, tree, witness.
4. **Wayne is a difficulty cliff.** He leads six Lv 9 Pokémon (Paras, Venonat, Nincada, Oddish, Exeggcute, Pineco) at `(39,8)`, a few tiles from the north door, while Finn `(21,48)` and Maya `(49,19)` have two each. Either trim Wayne to four or move him off the exit; right now the forest's hardest fight guards the way out.
5. **Forage is the economy.** Tiny Mushroom `(56,36)`, Big Mushroom `(57,8)`, Antidote `(76,32)`, and four item balls at `(45,16)`, `(34,28)`, `(50,48)`, `(71,42)` that all give `ITEM_POKE_BALL`. The mushrooms are the good part; four identical balls are filler.
6. **The north door does not open.** The warp event at `(20,15)` sits on secondary metatile `0x3B`; that tileset ships 60 metatiles and only 59 attribute entries, so the tile has no door behavior and the warp never fires. The south door works. As built, this is a progression blocker, not a flavour bug.

**Must not:** use the forest for a convergence reveal (the fact that it exits toward Hoenn is enough); stage Celebi, a legendary or a shrine quest; let the shrine sign grant anything; name Bill, Silph or Rocket; give Kurt apricorns or a ball-making job; turn the wood into a maze.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Ilex objective | `(26,42)`, `Pox_Ilex` | `FLAG_POX_STORY_STARTER`, not yet `FLAG_POX_STORY_ILEX` | one conversation sets the flag | set it at the north threshold instead, so the forest is crossed |
| Road boy | `(27,42)`, `Pox_IlexRoad` | always | repeats the guide's directions | keep as the second opinion; shorter, less certain |
| North exit | `(20,15)` | warp 1 to the north gatehouse | dead door tile, warp never fires | repair the metatile attribute |
| South exit | `(22,63)` | warp 0 to the south gatehouse | working | keep |
| Headbutt Key | `(42,26)`, `Pox_IlexForest_EventScript_HeadbuttKey` | `ITEM_HEADBUTT_KEY` not held | gives the key, re-explains it on later talks | keep; one clear explanation, then a nod |
| Empty tree | `(39,7)`, `PlasticOx_EventScript_HeadbuttTree` | key held | headbutt encounter | keep; this is the tutorial |
| Wayne | `(39,8)`, `IlexForest_EventScript_BugcatcherWayne` | `TRAINER_PLASTIC_OX_ROUTE_ILEX` | six Lv 9, then the "never seen before" line | trim the party or move him off the exit |
| Finn | `(21,48)`, `IlexForest_EventScript_BugcatcherFinn` | `TRAINER_PLASTIC_OX_ROUTE_ILEX_FINN` | two Lv 7–8, optional | keep; he is the first trainer most players meet |
| Maya | `(49,19)`, `IlexForest_EventScript_PicnickerMaya` | `TRAINER_PLASTIC_OX_ROUTE_ILEX_MAYA` | two Lv 8–9, optional | keep; make her rest stop readable before the battle |
| Litter | `(45,16)`, `(34,28)`, `(50,48)`, `(71,42)`, `IlexForest_EventScript_Item7/8/9/13` | `FLAG_POX_HIDDEN_ILEXFOREST_7/8/9/13` | four Poke Balls from visible balls | keep two, vary two |
| Mushrooms | `(56,36)`, `(57,8)` | `FLAG_POX_HIDDEN_ILEXFOREST_14/16` | hidden pickups | keep; let an NPC price them |
| Shrine sign | `(23,27)`, `IlexForest_EventScript_Sign2` | always | "FOREST GUARDIAN'S SHRINE / keep the clearing quiet" | keep the etiquette, remove the promise of an event |
| Orphan gatehouse | `Gate_AzaleaTown_IlexForest_hns` | — | two NPCs, zero warps, unreachable | wire it or retire it |

## Dialogue guidance

- **Who speaks:** people whose day is in the wood — a guide who walks it for warm-up, an old man who thinks in roots, a dancer rehearsing on leaves, a boy counting mushrooms, three bug catchers. Each has a job here; none has a theory about the world.
- **Register:** unhurried, concrete, slightly amused. Sentences about footing, baskets, nets, dry leaves. Nobody exclaims; the wood absorbs volume.
- **Before / after:** before the Gym the talk is directions and errands ("north path, then the gate"); after `FLAG_POX_STORY_ILEX` the guide has nothing left to ask and sounds faintly disappointed by that.
- **Wayne** is the only voice allowed real excitement, and only after the battle. The old man and the dancer must never explain each other.

> GUIDE: North path is the gate. Mind the roots — they are older than the path and they know it.

> OLD MAN: Count the rings on that stump and you get a drought, a fire and a wedding. I only know the fire.

> DANCER: The leaves keep time better than my teacher. They just don't keep it for me.

> BOY: Nine hundred and six, maybe seven. The mushrooms cheat — they hide behind the trunks.

> WAYNE: It fell out of the tree and looked at me like I had interrupted something. Then it was gone.

- **Do not:** say "convergence"; call the wood sacred, haunted or a maze; let anyone foretell a legendary; give the guide a speech about Hoenn; have the shrine sign answer a question.

## Inspiration

- **Satoyama coppice.** A wood that is a crop: hazel and oak cut on rotation, standards left for shade, leaf mould raked into heaps and carted out. Every NPC gets a season and a product — baskets, hurdles, kindling, mushrooms.
- **Matsutake-foraging etiquette.** Basket, cloth, stick, low voice; a good patch is a family secret. Converts into the shrine sign's "keep the clearing quiet", the boy's count and the mushroom pricing — and needs no priest and no event.
- **Bug-catcher kit.** A jam jar, a net with twine repairs, a sandwich in wax paper. Wayne, Finn and Maya all come from that kit; the leaf-in-the-sandwich NPC at `(37,21)` is already the best line on the map.
## Implementation hooks

- Wiki page: `ilexforest-hns.html`
- Maps: `IlexForest_hns` (`MAP_ILEX_FOREST_HNS`, layout 82×73, primary `gTileset_Johto_South_Hns`); gatehouses `Route2_ViridianForest_SouthEntrance_Frlg` and `Route2_ViridianForest_NorthEntrance_Frlg` (both warp back to this map); dead interior `Gate_AzaleaTown_IlexForest_hns`.
- Scripts: `data/maps/IlexForest_hns/scripts.inc`; `data/scripts/plastic_ox_story.inc` (`Pox_Ilex`, `Pox_IlexRoad`, `Pox_Roxanne`); `data/scripts/plastic_ox_headbutt.inc`; `data/scripts/plastic_ox_region.inc` (`PoxRoute2_RustboroGate`, `PoxRegion_Arrival_IlexForest_hns`).
- Flags: `FLAG_POX_STORY_ILEX` (objective + Route 2 hiker), `FLAG_POX_STORY_STARTER` (prerequisite), `FLAG_POX_TRIGGERS_ENABLED` (walkable-build bypass); hidden-item flags `FLAG_POX_HIDDEN_ILEXFOREST_7/8/9/13` and `_14/_15/_16`.
- Trainers / items: `TRAINER_PLASTIC_OX_ROUTE_ILEX` (Wayne, six), `_FINN`, `_MAYA` (two each); `ITEM_HEADBUTT_KEY`, four `ITEM_POKE_BALL`, `ITEM_TINY_MUSHROOM`, `ITEM_BIG_MUSHROOM`, `ITEM_ANTIDOTE`.
- Known gaps: **north exit dead** (metatile `0x3B` has no attribute entry: 60 metatiles vs 59 attributes in `gTileset_IlexForest_Hns`); three unused scripts (`IlexForest_EventScript_Npc1`, `_Npc2`, `_Npc5`) plus orphan `Npc3` text — those four voices have no object; four item balls share one item; the shrine sign names a shrine with no object; `LOCALID_ILEX_FOREST_KURT` and `LOCALID_ILEX_FOREST_KIMONO` are donor slots on ordinary NPCs; the Azalea gatehouse has zero warps.

## Open questions

- Move `FLAG_POX_STORY_ILEX` to a crossing point at the north threshold, or keep the guide conversation and repair the door first? Recommend both, door first.
- Wayne: six Lv 9 at the exit — deliberate gate or accident? If deliberate, he needs a line that admits he is blocking the road.
- Retire `Gate_AzaleaTown_IlexForest_hns` (two good NPC voices, no warps, no door in the forest) or cut a south-eastern opening for it?
- Four Poke Balls: cut to two, convert to Repel and a berry, or leave as an early-stock gift?
