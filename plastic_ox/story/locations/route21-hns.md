---
title: Route 21
slug: route21-hns
kind: Route
act: 3
stage: "9 — Cinnabar and the Mansion"
depth: supporting
wiki: route21-hns
maps: [Route21_hns]
flags: [FLAG_POX_HIDDEN_ROUTE21_16, FLAG_POX_HIDDEN_ROUTE21_17, FLAG_POX_HIDDEN_ROUTE21_18]
items: [ITEM_STARDUST]
status: drafted
---

# Route 21

## Snapshot

A donor HNS coastline, 24 tiles wide and 100 long, that starts at `Route12_hns`'s southern seam and ends at nothing. Three swimmers and a fisherman stand on it, three hidden Stardust lie in the rocks, and no warp, trigger or encounter table attaches any of it to the game. It is filed under act 3 stage 9 only because it occupies the same Kanto sea as the Cinnabar approach; its emotional note is mismatch — a beach whose people all talk about trees.

## Plot points

1. **A road with one end.** `Route21_hns` has exactly one neighbour, `Route12_hns` (up, offset -9), and `Route12_hns` reaches nothing either. `plastic_ox/alpha/LEGACY_REGION_PLAN.md` keeps that seam "for post-surf" and calls the Route 12/Route 21 water legs surf-gated, but nothing in the live build loads either map. No reveal-ladder step applies; step 9 belongs to Cinnabar and its Mansion.
2. **The text belongs to another map.** `Route21_EventScript_Npc1` and `Route21_EventScript_Npc3` share one string about trees sheltering small Pokémon, and `Route21_EventScript_Npc2` checks supplies "before heading into the trees". On a sea route that is donor copy-paste, not a voice, and it is the clearest sign the map was imported for its shape rather than its script.
3. **Three identical finds.** Hidden Stardust at `(8,73)`, `(17,43)` and `(7,29)` under `FLAG_POX_HIDDEN_ROUTE21_16`, `FLAG_POX_HIDDEN_ROUTE21_17` and `FLAG_POX_HIDDEN_ROUTE21_18` — numbering that continues Route 12's pair. No other reward, no fishing table, no wild table at all.
4. **Must not:** name Cinnabar, Pallet, the Mansion, Bill or the convergence; explain Surf here; stage a battle; or assume a player can arrive. This is a coast, not a beat, and the note must not invent one.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Swimmer woman | `Route21_hns` `(13,78)` | `Route21_EventScript_Npc1`, always | "The trees shelter small POKéMON. Watch the grass as you pass." | one coast line, or delete with the map |
| Swimmer man | `(8,50)` | `Route21_EventScript_Npc2`, always | "I always check my supplies before heading into the trees." | a swimmer with an errand, not a woodsman |
| Fisherman | `(16,26)` | `Route21_EventScript_Npc3`, always | the same tree line as Npc1, word for word | the only one who should mention water |
| Hidden Stardust | `(8,73)`, `(17,43)`, `(7,29)` | three hidden-item flags | three identical pickups | keep one if the coast survives; three is placeholder rhythm |
| Seam to Route 12 | north edge, offset -9 | map connection only | opens onto `Route12_hns`, itself unreachable | the pair needs one entrance or a retirement |

## Dialogue guidance

- **Who speaks:** nobody yet in any usable sense. If kept, the three are a cold-water swimmer doing a crossing, a fisherman who walked over from the Route 12 wall, and a teenager counting container ships.
- **Register:** salt, wind, boredom; short sentences about distance and temperature rather than Pokémon. These people are here because the day happens here, not because a route told them to stand.
- **Before / after:** none. The map reads identically at Hour 1 and at the League — an argument for retiring it rather than dressing it. The trees line must go even if the map stays; it is the one string that contradicts the geography.

> SWIMMER: The current runs east until the point, then it turns. You can feel it turn.

> FISHERMAN: I walked down from the wall. Nothing between here and there but the path and the gulls.

> TEENAGER: That one's been anchored since morning. Nobody on it. Nobody ever on it.

- **Do not:** mention Cinnabar, the Mansion, Pallet, the Surf Key, Bill, Silph or the convergence; describe grass or trees; add a battle; imply the player came here on purpose.

## Inspiration

- **The third coast of a harbour town** — the shingle nobody promotes, behind the container yard, where the fishing is poor and the view is a shipping lane. Converts directly into the three jobs: crossing, walking, counting.
- **HNS donor art against FRLG geography.** The layout uses the `PalletTown_Hns` secondary tileset and a Route 24 theme, so the map sounds and reads like somewhere else. Notice that mismatch before writing a line.
- **A coast with no town.** No shop, no house, no sign, no reason to stop. That absence is the only mood this map can honestly carry.

## Implementation hooks

- Wiki page: `route21-hns.html`
- Maps: `Route21_hns` (`MAP_ROUTE21_HNS`, `LAYOUT_ROUTE21_HNS`, 24×100, `Kanto_General_Hns` / `PalletTown_Hns`, music `MUS_RG_ROUTE24`)
- Scripts: `data/maps/Route21_hns/scripts.inc` — an empty `Route21_hns_MapScripts`, the three NPC labels and their strings. No map script.
- Items: `ITEM_STARDUST` ×3 through the hidden flags above; no item balls.
- Known gaps: unreachable (its only neighbour is equally orphaned); no entry in `src/data/wild_encounters.json`, so the water is empty; two of the three NPCs are flagged as ordinary trainers with sight range 4 yet own no trainer script; `Route21_EventScript_Npc1` and `_Npc3` are duplicates; the sea legs were left in the map group as a post-surf stub; no warps, coordinate events, signs or item balls exist on the layout.

## Open questions

- **Retire or reframe?** Recommend retire `Route21_hns` and its three Stardust: it duplicates `Route12_hns`'s coast, has no entrance, and every string on it is wrong. If the southern postgame coast is ever built, reframe it as that coast — but then it needs an entrance, a fishing table and one real find instead of three pickups.
- Keep the Route 12 seam if `Route21_hns` is retired, or cut both halves of the pair at once?
