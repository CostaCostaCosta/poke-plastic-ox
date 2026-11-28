---
title: Route 34
slug: route34-hns
kind: Route
act: 4
stage: "12 — Saffron to Blackthorn"
depth: supporting
wiki: route34-hns
maps: [Route34_hns]
flags: [FLAG_POX_STORY_SPACE_CENTER, FLAG_POX_TRIGGERS_ENABLED, FLAG_POX_HIDDEN_ROUTE34_17, FLAG_POX_HIDDEN_ROUTE34_18]
items: [ITEM_SUPER_POTION, ITEM_RARE_CANDY]
status: drafted
---

# Route 34

## Snapshot

Saffron's north road. It replaced the empty Kanto Route 5 on the way to Meteor Falls: **Saffron → Route 34 → Route 115 → Meteor Falls → Blackthorn**. The player comes through Saffron's north gate onto Route 34's old Goldenrod gatehouse throat `(31,65)`, then climbs a Johto field of grass, fences, a pond and headbutt trees to the north gap `(26–28,0)`, which drops onto Route 115's beach. Thirteen objects, no trainers, signs for a country that has moved. The emotional note is *bureaucratic anticlimax*: a border post that still checks papers for a border nobody can find, on the last ordinary road before the mountains.

## Plot points

1. **The road opens with the city.** Both crossings are `region_v7.py` trails gated on `FLAG_POX_STORY_SPACE_CENTER`, the flag that opens Saffron: `PoxRegion_saffron_route34_b` at the south throat `(30–32,66)` and `PoxRegion_route34_route115_a` at the north gap `(26–28,0)`. Bruno and Silph never gate this road.
2. **The old Act I door is shut.** `Route116` no longer has an `up` connection or a warp into Route 34. Route 34 is reached only from Saffron, so its OU encounters can't leak into Act I.
3. **The south strip is cut off.** Below the gatehouse, rows 77–89 (`x 20–29`) are a separate pocket: water and trees separate it from the road. Its objects (three cooltrainers `(20,84)`, `(22,87)`, `(25,84)` and the talking ball `(29,84)`) are now unreachable. Move them up or delete them.
4. **The day-care is a fiction.** Sign 2 at `(27,28)` advertises "DAY-CARE: now serving both regions". The old man at `(31,34)` is `LOCALID_ROUTE34_DAYCAREMAN` but only runs `Route34_EventScript_Npc12`, and the working day-care is `Route117_PokemonDayCare`. Repoint the sign or give the man a joke instead of a service.
5. **The signs describe the donor map.** `(29,8)` says "North: ILEX FOREST. South: anywhere." and `(33,65)` says "GOLDENROD CITY straight ahead." The real neighbours are Route 115 north and Saffron south. `(23,50)` promises trainers on a map with none.
6. **Item balls talk.** `(26,53)` and `(33,21)` use `OBJ_EVENT_GFX_POKE_BALL` for hiker lines and share a line. Replace the sprites and split the voices.

**Must not:** assume Silph is resolved; mention Silph, the League, the system or Bill; claim the route reaches Ilex Forest or Goldenrod; describe day-care breeding no script performs; explain the convergence; give the border joke to a fourth NPC.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Saffron crossing | `(30–32,66)` `PoxRegion_saffron_route34_b` | `FLAG_POX_STORY_SPACE_CENTER` unset | closed text, step back to `(31,65)` | keep; sign `(31,64)` should name the road, not "Marked passage ahead" |
| Route 115 crossing | `(26–28,0)` `PoxRegion_route34_route115_a` | same flag | warps to `Route115` `(19,79)` | keep; sign `(27,2)` should name the falls and the climb |
| Day-care sign and man | `(27,28)`, `(31,34)` | always | advertises a day-care that does not exist | repoint the sign or make it a joke |
| Item-ball hikers | `(26,53)`, `(33,21)` | always | POKE_BALL sprite, duplicate line | hiker sprites, distinct lines |
| Orphaned south strip | rows 77–89 | unreachable | three cooltrainers and a talking ball nobody can reach | move them onto the road or delete them |
| Hidden items | `(47,38)` Super Potion, `(17,17)` Rare Candy | `FLAG_POX_HIDDEN_ROUTE34_17`, `_18` | hidden pickups | keep both; a candy is fine in the late game |

## Dialogue guidance

- **Who speaks:** people loitering at a border that no longer means anything: a day-care keeper with no day-care, a policeman who finally has traffic and resents it, a picnicker asleep on the line, travellers carrying gear north to the falls.
- **Register:** dry, self-interrupting, embarrassed at their own jokes; one border joke per screen. The road is busy now that Saffron is open, and nobody here knows how the city's business is going.

> PICNICKER: The line runs under the blanket. Half of me is north, half is south, and neither half is getting up.

> DAY-CARE MAN: People ask if we take eggs. We take coats. There is a hook by the door and a very good dog.

> POLICEMAN: Months with nobody, and now everyone's heading for the falls at once. I liked it better when the city was shut.

- **Do not:** say "convergence"; name Ilex Forest or Goldenrod as neighbours; mention Silph, Bruno or the League; let the day-care man describe breeding mechanics; turn the border into a riddle.

## Inspiration

- **A downgraded border crossing.** The old customs hut, two languages on a rusting sign, one official still checking papers for a country that moved its border in 1991. Converts into the policeman, the day-care man and "South: anywhere".
- **Johto's Route 34.** The day-care road with wild Ditto in the grass. Keep the Ditto and the day-care's silhouette; drop Goldenrod.

## Implementation hooks

- Wiki page / map: `route34-hns.html`; `Route34_hns` (`MAP_ROUTE34_HNS`, layout 60×90, `gTileset_Johto_General_Hns`, `MUS_RG_ROUTE24`).
- Trails: `saffron_route34` and `route34_route115` in `plastic_ox/alpha/region_v7.py` (`TRAILS`, `PINNED_PORTS`, anchor `(36,40)`). Scripts are generated into `data/scripts/plastic_ox_region.inc`. `Route116`'s old connection and warp are removed there too.
- Scripts: `data/maps/Route34_hns/scripts.inc`, with objects `Route34_EventScript_Npc1`…`Npc13` and signs `Route34_EventScript_Sign1`…`Sign4`.
- Flags / items: `FLAG_POX_HIDDEN_ROUTE34_17` (Super Potion `(47,38)`), `FLAG_POX_HIDDEN_ROUTE34_18` (Rare Candy `(17,17)`); no `TRAINER_*` objects on the map.
- Encounters: OU band, owned by `plastic_ox/encounter_tables/apply_route34_115_v1.py` (`gPoxOURoute34Hns`): grass Lv 44–48 with 20% Ditto, Surf Lv 44–48, fishing Lv 40–48, and Headbutt `sPoxRoute34Headbutt` for the nine `MB_HEADBUTT_TREE` tiles (e.g. `(26,26)`).
- Known gaps: the orphaned south strip; two `OBJ_EVENT_GFX_POKE_BALL` NPCs; all four signs describe donor geography; `LOCALID_ROUTE34_DAYCAREMAN` has no interior; sign 4 advertises trainers that do not exist; the generated crossing signs use placeholder text.

## Open questions

- Should Route 34 get trainers to match Route 115's OU band, or stay a breather between Saffron and the beach dojo? Recommend a breather: Route 115 already has ten.
- Move the south-strip cooltrainers up onto the road, or delete them?
- Day-care: keep it as a joke, or wire a real one?
