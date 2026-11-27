---
title: Ruins of Alph
slug: ruinsofalph-outside-hns
kind: Route
act: 3
stage: "Act III side area — the dig reopens after Cinnabar"
depth: supporting
wiki: ruinsofalph-outside-hns
maps: [RuinsOfAlph_Outside_hns]
also_maps: [Gate_RuinsOfAlph_Route36_hns, RuinsOfAlph_Lab_hns]
flags: [FLAG_POX_STORY_MANSION, FLAG_POX_HIDE_RUINS_RESEARCHER]
status: implemented
---

# Ruins of Alph

## Snapshot

A working dig site behind Route 36, reached only through the south gatehouse. Four brick chamber doors sit on three terraces around a pond; three of them hide a Regi. The site is ordinary on purpose: survey signs, a research centre behind on its filing, staff who talk about crates and measurements. A stair in the middle of the site goes down to the statue hall under the chambers. The donor's Unown beams, wandering Pokémon, trainers, hidden items and visitor chatter are gone, and so are its seams to Route 36 and Route 32.

## Plot points

1. **Closed until Cinnabar.** The Route 36 researcher holds the gate until `FLAG_POX_STORY_MANSION`. What reopens the dig is a delivery: a crate of old site records from the Mansion. He then sits at the gatehouse desk `(3,5)` and mentions that the notes describe three walls that take a tablet. That is the only pointer the map gives toward the Regis.
2. **One chamber on foot, two across the pond.** From the gatehouse door `(20,6)` the main site reaches the north chamber `(28,11)` with no HM. The south terraces are across the pond `(24-32,33-37)`, so the south-east `(34,42)` and south-west `(7,40)` chambers need Surf, which the player has by this checkpoint. The surveyor on the north shore says so.
3. **No traps.** The donor reached the west and south terraces only from Union Cave B1F. Here two east-facing ledge tiles are plain ground, `(22,40)` and `(18,38)`, so the south terraces are two-way, and the two Union Cave mouths `(13,25)` and `(14,36)` lead to each other, which joins the west terrace (tall grass, the fourth chamber) to the rest. From any tile the gatehouse can be reached again.
4. **The research centre and the stair are real; the east gatehouse is not.** The research centre door `(36,16)` opens on `RuinsOfAlph_Lab_hns`: an archivist sorting the Cinnabar crates, a copyist of wall carvings, a table of plaster casts. There is no fossil reviver. The stair `(21,21)` goes down to the hall (`ruinsofalph-b1f-hns`). The east gatehouse `(38,27)` led to Route 32, which is not in this region; it is solid, with a sign that says the road east is washed out.
5. **Must not:** say "convergence"; explain the Regis, the tablets or why the land changed; mention Unown, the sliding puzzles or a Pokédex upgrade; name Route 32, Union Cave or Violet City as places one can walk to.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Gatehouse chain | Route 36 `(55,25)`–`(57,25)` ↔ gatehouse `(7,1)`; gatehouse `(7,9)` ↔ dig site `(20,6)` | researcher gone from Route 36 | warps both ways; the gatehouse returns to Route 36 `(56,25)` | keep |
| Desk researcher | gatehouse `(3,5)`, across the counter | always | the Cinnabar crates and "three walls that take a tablet" | keep; same man as on Route 36 |
| Measuring student | `(26,13)` | always | each back wall has a tablet-sized hollow | keep |
| Surveyor | `(27,31)` | always | the south terraces are over the pond; crates go across on a Lapras | keep; this is the Surf hint |
| Digger | `(16,37)` | always | the crawlway comes out by the west chamber | keep |
| Chamber doors | `(28,11)`, `(5,23)`, `(7,40)`, `(34,42)` | always | step in; each leads to its room in the chambers map | keep |
| Crawlway | `(13,25)` ↔ `(14,36)` | always | cave mouth to cave mouth on this map | replace with a short cave interior if Union Cave is ever imported |
| Signs | `(31,24)`, `(37,16)`/`(38,16)`, `(30,11)`, `(38,27)` | always | site board, research centre plaque, north chamber, shuttered east gatehouse | keep |
| Research centre | door `(36,16)` → `RuinsOfAlph_Lab_hns` `(2,7)` | always | archivist `(1,3)`, copyist `(8,5)`, cast table `(5-7,4)` | keep; filing complaints, no lore |
| Stair down | `(21,21)` → `RuinsOfAlph_B1F_hns` `(15,16)` | always | two-way stair to the hall | keep |
| Wild Pokémon | tall grass `(13-17,9-13)` and the west terrace; pond and lake | always | Xatu, Natu, Girafarig, Baltoy Lv. 36-39; Quagsire, Wooper on water | keep within the Cinnabar (UU) pool |

## Dialogue guidance

- **Staff, not mystics.** They measure, carry and complain. The site's strangeness is a logistics problem: no bridge, an unsafe floor, a wall nobody can open.
- **The researcher** connects the two maps. On Route 36 he minds a gate; at the desk he is surrounded by someone else's paperwork. He may name Cinnabar, the Mansion and Dr. Fuji's hand, nothing wider.
- Keep every line short enough to read standing up. Nobody here gives a lecture.

> SURVEYOR: No bridge yet. We float the crates across and swim after them.

> STUDENT: This one's rough inside, like the stone was split.

## Inspiration

- **A real excavation in the off season:** tarpaulins, numbered pegs, a locked finds hut and one person left behind to answer the gate.
- **Gen 2's Ruins of Alph:** the brick chamber fronts and the feeling that the site is older than anyone's explanation of it, without the radio signal or the Unown.

## Implementation hooks

- Converted maps from `plastic_ox/alpha/import_ruins_of_alph.py` (donor `RuinsOfAlph_Outside_hns`, `Gate_RuinsOfAlph_Route36_hns`), installed by `plastic_ox/alpha/ruins_of_alph.py`; scripts are authored in `plastic_ox/alpha/ruins_of_alph/` and copied to each map's `scripts.inc`.
- Tilesets imported with the maps: `gTileset_RuinsOfAlph_Outside_Hns`, `gTileset_RuinsOfAlphWriting_Hns`.
- Wild table `gPoxUURuinsOfAlphOutside`, counted at the `cinnabar` checkpoint in `plastic_ox/tools/pox_progression.py`.
- Region map section is `MAPSEC_RUINS_OF_ALPH` (appended after the last existing section, so no id moves), with the stone name sign on arrival and a landmark cell at `(17,3)` on the town map, under Route 36 (`plastic_ox/town_map/build_fly_map.py`). The gatehouse stays on `MAPSEC_ROUTE_36` so the sign shows when the player steps onto the site.
- Demo check: `plastic_ox/demo/test_ruins_of_alph.py`.

## Open questions

- The fourth (west) chamber is an empty room. Give it a use or leave it as flavour?
- 2026-11-27: resolved. The research centre, the hall and the Words Rooms are imported, and the dig has its own town-map section and name sign. The east gatehouse stays shuttered because Route 32 is not in this region; the four arrow tiles behind it `(45,25-28)` cannot be reached.
- The cave-mouth pair is a stand-in for Union Cave. Is a one-room crawlway interior worth building?
