---
title: Route 34
slug: route34-hns
kind: Route
act: 1
stage: "1 — Rustboro and Sea Cottage"
depth: supporting
wiki: route34-hns
maps: [Route34_hns]
flags: [FLAG_POX_HIDDEN_ROUTE34_17, FLAG_POX_HIDDEN_ROUTE34_18]
items: [ITEM_SUPER_POTION, ITEM_RARE_CANDY]
status: drafted
---

# Route 34

## Snapshot

A 60×90 Johto route grafted onto the top of `Route116`, entered only by walking off that map's northern edge at `x 39–41` and climbing a field-and-ledge corridor toward a mountain with no door. Thirteen objects, no trainers, no warps, no day-care. It is the branch you take because you saw a gap in the treeline, and its emotional note is *bureaucratic anticlimax*: a road with signs for a country that has moved.

## Plot points

1. **One way in, no way out.** `Route116` declares the `up` connection (offset 17) and a warp at `(40,1)` pointing at this map's warp 1; `Route34_hns` declares no connections and has zero warps. The player walks up and cannot walk back. Fix the return before anyone writes a line here.
2. **Step 1 geography only.** The map's own text already does the work: "the grass turns tropical", "the border runs right through my blanket", "the signs gave up". Keep that register, cut the repeats, never explain the merge.
3. **The day-care is a fiction.** Sign 2 at `(27,28)` advertises "DAY-CARE: now serving both regions"; the old man at `(31,34)` is `LOCALID_ROUTE34_DAYCAREMAN` but only runs `Route34_EventScript_Npc12`, and the working day-care in the repo is `Route117_PokemonDayCare` (the Route 5 and Four Island rooms are FRLG legacy). Build one room and a warp, or repoint the sign.
4. **The signs describe the donor map.** `(29,8)` says "North: ILEX FOREST. South: anywhere." and `(33,65)` says "GOLDENROD CITY straight ahead." Neither is true of the live neighbours; `(23,50)` promises trainers on a map with none.
5. **Three item balls talk.** `(29,84)`, `(26,53)`, `(33,21)` use `OBJ_EVENT_GFX_POKE_BALL` for hiker lines, and two pairs of lines are identical: `(29,84)`=`(20,26)` and `(26,53)`=`(33,21)`. Replace the sprites, split the voices.

**Must not:** open an early road to Goldenrod or any Gym-2 content; claim the route reaches Ilex Forest; describe day-care breeding no script performs; explain the convergence; give the border joke to a fourth NPC.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Entry from `Route116` | `x 22–24, y 89` | `Route116` up connection, offset 17 | works inward | keep; add the reciprocal connection |
| Return | south edge `(22–24, 89)` | nothing declared | no exit, soft-lock | add a `down` connection on this map |
| Dangling warp | `Route116` `(40,1)` | `dest_warp_id 1` | this map has zero warps; tile is plain ground | delete the warp or give warp 1 a door |
| Day-care sign and man | `(27,28)`, `(31,34)` | always | advertises a day-care that does not exist | point at `Route117_PokemonDayCare` or build the room |
| Item-ball hikers | `(29,84)`, `(26,53)`, `(33,21)` | always | POKE_BALL sprite, two duplicate lines | hiker sprites, three distinct lines |
| Hidden items | `(47,38)` Super Potion, `(17,17)` Rare Candy | `FLAG_POX_HIDDEN_ROUTE34_17`, `_18` | hidden pickups | keep the potion; reconsider the candy |

## Dialogue guidance

- **Who speaks:** people loitering at a border that no longer means anything — a day-care keeper with no day-care, a policeman with no traffic, three trainers who came to race to Hoenn, a picnicker asleep on the line.
- **Register / before-after:** dry, self-interrupting, embarrassed at their own jokes; one border joke per screen, not three in a row. Nothing here changes until the route is wired — then they gain a line about the traffic, and the policeman resents it.

> PICNICKER: The line runs under the blanket. Half of me is north, half is south, and neither half is getting up.

> DAY-CARE MAN: People ask if we take eggs. We take coats. There is a hook by the door and a very good dog.

> COOLTRAINER: I race my sister to Hoenn. She wins because she stops to ask directions and I stop to argue.

- **Do not:** say "convergence"; name Ilex Forest as the north neighbour; promise Goldenrod, badges or a Gym; let the day-care man describe breeding mechanics; turn the border into a riddle.

## Inspiration

- **A downgraded border crossing.** The old customs hut, two languages on a rusting sign, one official still checking papers for a country that moved its border in 1991. Converts into the policeman, the day-care man and "South: anywhere".
- **The roadside kennel as a family business.** Chalkboard prices, a ledger, an incubator humming in the back room. This is what the day-care sign wants to be; give it one room or stop advertising it.

## Implementation hooks

- Wiki page / map: `route34-hns.html`; `Route34_hns` (`MAP_ROUTE34_HNS`, layout 60×90, `gTileset_Johto_General_Hns`, `MUS_RG_ROUTE24`); sole neighbour `Route116` (`MAP_ROUTE116`, connection `up` offset 17, dangling warp `(40,1)`).
- Scripts: `data/maps/Route34_hns/scripts.inc` — objects are `Route34_EventScript_Npc1`…`Npc13`, signs `Route34_EventScript_Sign1`…`Sign4`; no map script, no coord events.
- Flags / items: `FLAG_POX_HIDDEN_ROUTE34_17` (Super Potion `(47,38)`), `FLAG_POX_HIDDEN_ROUTE34_18` (Rare Candy `(17,17)`); no `TRAINER_*` objects anywhere on the map.
- Known gaps: zero warps and zero connections (one-way entry, soft-lock); three `OBJ_EVENT_GFX_POKE_BALL` NPCs; duplicate lines as above; all four signs describe Johto geography that no longer borders this map; `LOCALID_ROUTE34_DAYCAREMAN` has no interior; sign 4 advertises trainers that do not exist; nothing explains the mountain.

## Open questions

- Keep Route 34 as a silent dead-end branch off `Route116`, or wire it south toward a future Goldenrod approach? Recommend a working cul-de-sac until Goldenrod's act is live.
- Day-care here (new interior map and warp) or on `Route117_PokemonDayCare`, which already works?
- `plastic_ox_map_v7.md` never lists Route 34 in the progression graph: is the day-care idea enough to justify the map, or should it be retired with the other donor leftovers?
