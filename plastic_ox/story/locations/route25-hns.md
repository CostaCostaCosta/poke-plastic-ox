---
title: Route 25
slug: route25-hns
kind: Route
act: 1
stage: "1 — Rustboro and Sea Cottage"
depth: full
wiki: route25-hns
maps: [Route25_hns]
also_maps: [Route25_BillsHouse_hns, Route25_SeaCottage_Frlg]
flags: [FLAG_POX_STORY_STARTER, FLAG_POX_KNOWS_BILL_PC, FLAG_POX_GIFT_COTTAGE, FLAG_POX_HIDDEN_ROUTE25_19]
trainers: [TRAINER_PLASTIC_OX_ROUTE25, TRAINER_PLASTIC_OX_ROUTE25_DUDLEY, TRAINER_PLASTIC_OX_ROUTE25_JOE, TRAINER_PLASTIC_OX_ROUTE25_LAURA, TRAINER_PLASTIC_OX_ROUTE25_LLOYD, TRAINER_PLASTIC_OX_ROUTE25_ELLEN, TRAINER_PLASTIC_OX_ROUTE25_PAT]
items: [ITEM_REVIVE]
status: drafted
---

# Route 25

## Snapshot
A seaside promenade that ends at a door. `Route25_hns` runs east from Route 24 with a warp at `(85,13)` into `Route25_BillsHouse_hns`, where an old man gives away an Eevee. It is the payoff of the game's first optional branch and the first place the player meets a crowd that is simply *out walking* — trainers, picnickers, a scientist, and two children arguing about the sea.

## Plot points
1. **The branch ends at a door, not a boss.** No trainer guards the cottage, no flag gates it, and the reward is a Lv.5 Eevee (`Pox_Cottage` → `givemon SPECIES_EEVEE, 5`) guarded only by `FLAG_POX_STORY_STARTER`. Keep it that way; the optional branch should feel like a detour that pays in character, not in power.
2. **Eevee #1 must be the player's first Eevee.** The cottage sets `FLAG_POX_GIFT_COTTAGE` once and retries on a full party via `Pox_NoRoom`; the four later gifts are all downstream of this. Do not let any other gift fire earlier.
3. **The grandfather is a collector, and that is his whole character.** After the Eevee he trades fossils for sightings, keyed on `VAR_POX_GRANDPA_PROGRESS`: Ralts → Dome, Phanpy → Claw, Teddiursa → Root, Yanma → Helix, Magikarp → Old Amber. It is a nice, dopey hobby — but it hands out Kanto fossils *before* Mt. Moon, which is a real economy problem, not a flavour one.
4. **Bill stays texture.** The cottage line is the canonical one — grandson, PC storage, away on a project — and that is all it may ever be. No reconstruction, no network, no Weather Institute, no implication that he caused anything.
5. **The duplicate cottage must be retired or sealed.** `Route25_SeaCottage_Frlg` is the untouched FRLG cottage: teleporter, Clefairy, SS Ticket quest, computer sign. Its three warps point at `MAP_ROUTE25`, not at this route, so it belongs to the legacy FRLG Kanto island, not to v7. A player who reaches it meets a second Bill and a second Eevee-adjacent story.
6. **Two Mistys and a duplicated Eusine are on this road.** `LOCALID_ROUTE25_MISTY` at `(100,17)` and `LOCALID_CAPE_MISTY` at `(81,17)` are two separate objects with two lines; `LOCALID_ROUTE25_EUSINE` at `(99,23)` duplicates the Eusine placed on `Route14_hns`. Pick one of each.
7. **Must not:** name Bill anywhere near the system, turn the cottage into a laboratory, explain the fossils' origin, or let the FRLG cottage remain reachable.

## Key interactions
| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Cottage warp | `(85,13)` → `MAP_ROUTE25_BILLS_HOUSE_HNS` | always | works, one-way door into the cottage | keep; verify the return lands on `(85,14)` and never strands the player |
| Cottage exit | `Route25_BillsHouse_hns` `Pox_CottageExit` | `FLAG_POX_TRIGGERS_ENABLED` | warps to Route 25 `(85,14)` | keep; this is the implementation of "return to Route 25, never Fortree" |
| Grandfather | `Route25_BillsHouse_hns` `(7,6)` `Pox_Cottage` | `FLAG_POX_STORY_STARTER` | Eevee once, then fossil-for-sighting chain on `VAR_POX_GRANDPA_PROGRESS` | keep the Eevee; gate the fossil chain behind something that does not undercut Mt. Moon |
| Dead FRLG cottage | `Route25_SeaCottage_Frlg` `(7,5)` `Route25_SeaCottage_EventScript_Bill` | none | vanilla SS Ticket quest with Clefairy and a PC sign | retire the map, or strip the Bill script and reuse the interior as scenery |
| Lass (trainer) | `(57,23)` `PoxRouteTrainer_Route25` | `TRAINER_PLASTIC_OX_ROUTE25` | six mons, Lv.12 | keep; the road's main optional fight |
| Youngster | `(27,19)` `Route25_EventScript_Npc1` | `TRAINER_PLASTIC_OX_ROUTE25_DUDLEY` | counts turns from the bridge, then loses count | keep; the best-written line on the route |
| Scientist Pat | `(65,18)` `Route25_EventScript_Pat` | none | "I study the POKéMON here between battles." — no battle, though `TRAINER_PLASTIC_OX_ROUTE25_PAT` exists | attach the battle or drop the trainer and keep the flavour |
| Cuttable tree | `(66,13)` `Route25_EventScript_Npc7` | none | a `CUTTABLE_TREE` with a talk script ("branches rustle") | point it at `EventScript_CutTree`; a tree that cannot be cut and speaks is a placeholder |
| Misty | `(100,17)` `LOCALID_ROUTE25_MISTY` and `(81,17)` `LOCALID_CAPE_MISTY` | none | two Mistys, two lines, no battle | collapse to one; the cape one should own the Eevee/grandfather remark |
| Eusine | `(99,23)` `LOCALID_ROUTE25_EUSINE` | none | admires his own shoes | keep only if `Route14_hns` loses its Eusine |
| Unused label | `Route25_EventScript_Npc2` | never placed | a plain talker script with no object | delete, or place it as the trainer the route is missing |
| Hidden item | `(50,12)` `FLAG_POX_HIDDEN_ROUTE25_19` | flag unset | `ITEM_REVIVE` | keep; a Revive before the first dungeon is the right generosity |

## Dialogue guidance
- **Voices:** a promenade crowd. Children running ahead, a parent who regrets the walk back, a trainer resting a tired team, a scientist who studies between battles, an old man in good shoes.
- **Register:** bright, breezy, faintly competitive. People are here because the sea is nice and because other people are here. Lines are about pace, lunch, and who is faster.
- **The grandfather** is warm, chatty, and slightly lonely; he talks about Pokémon the way people talk about grandchildren of friends. He never explains his grandson's work beyond the PC line.
- **Before/after the Eevee:** before, he is a man with a Pokémon that needs a home; after, he is a man with a hobby and a new visitor. No one else mentions the gift.

> LASS: We're taking the walk slowly now. They've earned a rest, and I like hearing their footsteps next to mine.

> PICNICKER: My son says a walk is boring. Then he races me at every turn. I'd like some of that energy for the trip home.

> GRANDFATHER: This one's been underfoot all week. Brushes my coat, sleeps in the good chair. She needs someone with a road ahead of them.

> SCIENTIST: I count what comes past the cape. Today: three trainers, one argument, and a very determined Pidgey.

- **Do not:** let anyone call Bill a genius, an inventor of the region, or a person of importance; mention the storage system outside the cottage; or hint that Eevee is special beyond being a gift.

## Inspiration
- **An English seaside promenade in early summer** — benches facing the water, a kiosk, grandparents in good shoes: gives the cape its benches, its walkers and the "I only meant a short walk" joke.
- **A cape with a car park and a signboard** — everyone photographs the same view, nobody stays long: the road's social rhythm, and where the two Mistys should stand instead of both.
- **Gen 2's Route 25 mood** (the walk to Bill's cottage) — use the anticipation, not the text; the door is more interesting than the road.
- **Conversion:** six jobs carry it — resting trainer, counting kid, racing parent, studying scientist, shoes-and-opinions gentleman, grandfather. Add one bench argument and the promenade is alive without a plot.

## Implementation hooks
- Wiki page: `route25-hns.html`; route `Route25_hns` (`MAP_ROUTE25_HNS`), group `gMapGroup_PlasticOxJohtoKanto`, connection down to `Route24_hns`
- Interiors: `Route25_BillsHouse_hns` (`MAP_ROUTE25_BILLS_HOUSE_HNS`), legacy `Route25_SeaCottage_Frlg` (`MAP_ROUTE25_SEA_COTTAGE`)
- Scripts: `data/maps/Route25_hns/scripts.inc` (`Route25_EventScript_Npc1` … `Npc12`, `Pat`), `data/maps/Route25_BillsHouse_hns/scripts.inc` (`Pox_Cottage`), `data/scripts/plastic_ox_route_trainers.inc`
- Flags and vars: `FLAG_POX_STORY_STARTER`, `FLAG_POX_KNOWS_BILL_PC`, `FLAG_POX_GIFT_COTTAGE`, `VAR_POX_GRANDPA_PROGRESS`, `FLAG_POX_HIDDEN_ROUTE25_19`
- Known gaps: two Mistys, duplicated Eusine, unplaced `Route25_EventScript_Npc2`, `TRAINER_PLASTIC_OX_ROUTE25_PAT` with no battle, cuttable tree with a talk script, ELLEN and PAT sharing an identical party, and a fully scripted vanilla cottage one island away.

## Open questions
- Should the grandfather's fossil chain stay? Five Kanto fossils before Mt. Moon competes with Rocket's fossil theft; either move the chain later or make the reward a held item rather than a fossil.
- Which Misty is canonical, `(100,17)` or `(81,17)`? The line about Bill's grandfather belongs to whichever one stands near the cottage path.
- Is `Route25_SeaCottage_Frlg` reachable in play through the FRLG Kanto island? Its warps point at `MAP_ROUTE25`, and `Route25_Frlg` is wired to `Route24_Frlg` and Cerulean, so verify before assuming it is inert.
- Are Ralts, Phanpy, Teddiursa, Yanma and Magikarp obtainable before Rustboro's Gym? If not, the fossil chain is a post-Mt. Moon reward wearing Act I clothes.
