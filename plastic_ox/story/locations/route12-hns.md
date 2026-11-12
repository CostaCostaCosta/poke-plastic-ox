---
title: Route 12
slug: route12-hns
kind: Route
act: 3
stage: "8 — Underground bypass"
depth: supporting
wiki: route12-hns
maps: [Route12_hns]
flags: [FLAG_POX_HIDDEN_ROUTE12_14, FLAG_POX_HIDDEN_ROUTE12_15]
items: [ITEM_YELLOW_FLUTE, ITEM_CALCIUM, ITEM_POKE_BALL]
status: drafted
---

# Route 12

## Snapshot

A sea-wall road, thirty-eight tiles wide and ninety long, running north–south above open water with nothing on it but fishermen. It is a supporting Kanto coastal leg, not a story node — a player would walk it for the quiet, two hidden items and the view. Today it is also **orphaned**: no warp, portal or script anywhere in the game reaches it, and its only neighbour is `Route21_hns`, which is equally unreachable.

## Plot points

1. **A road with no entrance.** `Route12_hns` has no warps, no coordinate triggers and one connection (down, to `Route21_hns`, offset 9); `Route21_hns` connects only back up. Nothing else in `data/maps` or `data/scripts` references either map, so the pair is a closed island inside the live map group — keep that in mind before writing anything that assumes the player can get here.
2. **Five fishermen, two lines, no fish.** The five `FISHERMAN_HNS` objects share two strings ("Fishing takes patience…" ×3, "The water brings a cool breeze…" ×2), and the map has neither `fishing_mons` nor `land_mons`: a route themed entirely around fishing has nothing to catch. It is also visibly unfinished — two fishermen stand above the layout at negative `y` (`(13,-14)`, `(7,-25)`), both cuttable trees run NPC dialogue instead of `EventScript_CutTree`, both item balls grant `ITEM_POKE_BALL`, and one sign sits off-map at `(16,-28)`.
3. **Must not:** attach story here, mention Lavender's harbour or the postgame islands, or assume the route is reachable in the current build. It is a coast, not a beat.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Fishermen | `Route12_hns` `(23,14)`, `(23,43)`, `(21,66)` on-map; `(13,-14)`, `(7,-25)` off-map | always | five objects cycling two shared lines, two of them outside the 38×90 layout | two or three distinct voices on the road; delete the out-of-bounds pair |
| Cut trees and signs | trees `(7,72)`, `(7,73)`; signs `(6,43)`, `(16,-28)` | `Route12_EventScript_Npc6`, `Route12_EventScript_Npc8`, `Route12_EventScript_Sign3`, `Route12_EventScript_Sign4` | trees print fisherman lines; both signs say "A sign from the old routes.", one off-map | repoint trees at `EventScript_CutTree`; one real sea-wall sign |
| Item balls and hidden items | balls `(22,41)`, `(4,74)`; hidden `(20,26)` Yellow Flute, `(9,13)` Calcium | `Route12_EventScript_Item7`, `Route12_EventScript_Item9`, `FLAG_POX_HIDDEN_ROUTE12_14`, `FLAG_POX_HIDDEN_ROUTE12_15` | two `finditem ITEM_POKE_BALL` pickups plus two working hidden items | keep the hidden pair; make at least one ball worth opening |

## Dialogue guidance

- **Who speaks:** people who fish a wall, not a boat. Not competing, not selling. Five concerns: bait, tide, a thermos, a bird, a son who stopped coming.
- **Register:** quiet and lateral — they answer questions nobody asked, and nobody explains the map. **No battle talk:** none of the five challenges the player, and the road reads identically at the start and the end of the game.

> EEL FISHER: They come up the wall at dusk. You can set a line, go home, and they will still be on it at dawn.

> BIRDWATCHER: I am not here for the fish. The gulls follow the trawlers, and the trawlers follow the weather.

> THERMOS WOMAN: My husband fished this wall for thirty years. I still bring two cups.

- **Do not:** use "patience" as a punchline, name Cinnabar, Lavender, Saffron or the League, or write a fisherman who wants a battle.

## Inspiration

- **A sea-wall road in Shonan or Enoshima at dawn**, crossed with Kanto Route 12's RBY/FRLG pier: tetrapods, a vending machine, a bicycle on the rail, a catch noticeboard, old men with fixed lines who do not expect to catch much. Converts straight into the five jobs — bait, tide, thermos, bird, the absent son — and keeps the *silence*; the Snorlax and trainers belong to the legacy `Route12_Frlg` map.

## Implementation hooks

- Wiki page: `route12-hns.html`; maps `Route12_hns` (`MAP_ROUTE12_HNS`, layout `LAYOUT_ROUTE12_HNS`, 38×90) and partner `Route21_hns`; scripts `data/maps/Route12_hns/scripts.inc` (all eleven labels), no map script; no gates or trainers; `ITEM_POKE_BALL` ×2 from item balls, `ITEM_YELLOW_FLUTE` and `ITEM_CALCIUM` hidden
- Known gaps: the `Route12_hns`/`Route21_hns` pair is unreachable; no wild or fishing encounters; two NPCs and one sign lie outside the layout bounds; two "cuttable trees" run NPC scripts; five fishermen share two strings; the legacy `Route12_Frlg` (`MAP_ROUTE12`) still holds the coastline's only Snorlax and full trainer set

## Open questions

- Retire the `Route12_hns`/`Route21_hns` pair, or connect it? If connected it belongs to a southern-coast plan — the Act III Cinnabar→Seafoam leg or the postgame harbour road, not both.
- Should the legacy `Route12_Frlg` supply this coast's Snorlax and trainers, and is five fishermen the right population for a 90-tile map?
