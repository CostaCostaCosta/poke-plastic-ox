---
title: Route 3
slug: route3-hns
kind: Route
act: 1
stage: "1 — Rustboro and Sea Cottage"
depth: supporting
wiki: route3-hns
maps: [Route3_hns]
flags: [FLAG_POX_HIDDEN_ROUTE3_20]
items: [ITEM_STARDUST]
status: drafted
---

# Route 3
## Snapshot
A donor shell wearing a route's name: `Route3_hns` holds four talkers and a hidden Stardust at `(22,9)`, and no way in or out — no connections, warps, coord events, encounter table, or reference from any script in the checkout. Its only current job is proving that two Route 3s exist in the tree.

## Plot points
1. **No beat, because there is no visit.** `Route3_hns` (`MAP_ROUTE3_HNS`, layout `LAYOUT_ROUTE3_HNS`) is unreachable from every other map — a data fact, not a decision anyone made out loud. It is the dead half of a duplicate pair: `Route3_Frlg` is the copy wired from Pewter into `Route4_Frlg`, with the vanilla object set.
2. **If the pair is ever restored**, the only coherent job is the *east* face of Mt. Moon, since `Route44_hns` owns the western approach and the badge gate. Proposal only.
3. **Must not** ship as-is: the Unovan line and "a region somewhere in that cave" are fourth-region and meta jokes, the two hikers say the same thing twice, and no second Mt. Moon mouth may exist before the first one is authored.

## Key interactions
| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Youngster | `(12,5)` `Route3_EventScript_Npc1` | none | "Trainers come through the tunnel east speaking UNOVAN." | delete: Unova is not a region in this world |
| Youngster | `(30,3)` `Route3_EventScript_Npc2` | none | "MT.MOON's east. There's a cave in it, and a region somewhere in that cave." | cut the second sentence; keep the direction only |
| Hikers | `(44,6)`, `(66,10)` `Route3_EventScript_Npc3`, `Npc4` | none | "Rocky ground can wear your team down" / "The mountain draws hikers and curious trainers alike" | keep one voice; give the other the job of losing and finding the Stardust |
| Hidden item | `(22,9)` `FLAG_POX_HIDDEN_ROUTE3_20` | flag unset | `ITEM_STARDUST` placed, unobtainable while the map is cut off | keep the flag; only matters if the map is wired |

## Dialogue guidance
Two hiker voices and one child, nothing else. Boots, wind, chalk dust, a bad knee; two sentences, about the next hour, never about the region. Hikers may know a cave is far, not who is inside it or why the mountains are new. If the map stays retired, the correct guidance is "write nothing".
> HIKER: Rest on the flat rock, not the loose stuff. Loose stuff is how you lose an afternoon.
> HIKER: My knees remember this road better than I do. They start complaining before the signpost.
> YOUNGSTER: I'm allowed as far as the marker. Not one step past it. I've measured.
- **Do not:** mention Unova or other regions as regions, use "convergence", or let a child explain the geography.

## Inspiration
- **The Burren, County Clare** — limestone pavement, dry-stone walls, no shade: becomes hiker work (guiding, wall-mending, finding lost gear) and a route that reads as walked-over rather than wild.
- **Weekend sawanobori parties** — rope, helmet, a bag of onigiri: a second hiker voice, competent and slightly impatient, and the reason one hiker carries a bag the other mocks.

## Implementation hooks
- Wiki page: `route3-hns.html`; map `Route3_hns` (`MAP_ROUTE3_HNS`), group `gMapGroup_PlasticOxJohtoKanto`
- Scripts: `data/maps/Route3_hns/scripts.inc` — `Route3_EventScript_Npc1` … `Npc4`, each a plain `msgbox … MSGBOX_NPC`
- Known gaps: zero connections, warps, coord events, encounters, trainers, or signs; the map is complete-looking and inert.

## Open questions
- Keep or retire? Recommendation: **retire** `Route3_hns` and let `Route3_Frlg` own the wiki name, unless someone will wire a second mountain face and write four new talkers.
- Is `FLAG_POX_HIDDEN_ROUTE3_20` reused or dropped if the map is retired? Reusing a hidden-item flag on another tile silently moves a collectible.
