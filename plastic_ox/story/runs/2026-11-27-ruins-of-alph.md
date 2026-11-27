# 2026-11-27 — ruins-of-alph

- Notes: plastic_ox/story/locations/ruinsofalph-outside-hns.md and ruinsofalph-puzzleandrewardchambers-hns.md (new, implemented); route36-hns.md item 4 and the three-clones question; mossdeepcity.md step 5a
- Maps: Route36_hns, Gate_RuinsOfAlph_Route36_hns, RuinsOfAlph_Outside_hns, RuinsOfAlph_PuzzleAndRewardChambers_hns (all three imported from the HNS donor at 44f50eedef), DesertRuins, IslandCave, AncientTomb
- Changed: Route 36's three gate men are one researcher at (56,24) with step triggers on (55,24)/(57,24); he opens on a live check of FLAG_POX_STORY_MANSION (confirmed in build_story.py: set by Pox_Archive3, the last Mansion archive), walks into the gatehouse and sets FLAG_POX_HIDE_RUINS_RESEARCHER (POX_EXT_FLAGS_START + 18)
- Changed: Regirock (north chamber), Registeel (south-west) and Regice (south-east) and their sages stand in the chamber back rooms; same PoxTournament_* scripts, tablets, badge gates 5/6/6 and FLAG_POX_CAUGHT_* flags. The Route 127 caves are empty side areas with open inner rooms
- Changed: dig-site access without Union Cave: ledge tiles (22,40) and (18,38) repainted as ground, cave mouths (13,25) and (14,36) lead to each other, the pond is crossed with Surf
- Changed: steel-tablet reward text and the Regice/Registeel home-sage lines no longer point at Route 127; new wild table gPoxUURuinsOfAlphOutside (species already in the Cinnabar pool)
- Dialogue: 4 NPC lines and 13 sign/wall lines on the Ruins maps, 2 researcher lines on Route 36, 3 cave wall lines; test_ruins_of_alph.py diffs all of them for duplicates
- Verified: see the PR for the exact commands; mGBA walk of both researcher states on all three lanes, the gatehouse chain both ways, a real Surf crossing, both ledge gaps both ways, the crawlway, each Regi's three states, the emptied caves
- Follow-up pass (same day): merged master and moved FLAG_POX_HIDE_RUINS_RESEARCHER to POX_EXT_FLAGS_START + 18 (master took +14 to +17 first; the flag had not shipped)
- Added: RuinsOfAlph_Lab_hns (archivist, copyist, cast table; no fossil reviver), RuinsOfAlph_B1F_hns (statue hall, wild Unown Lv. 36-38, one surveyor), RuinsOfAlph_WordsRoom1-4_hns (bare); tileset gTileset_RuinsOfAlph_B1F_Hns. New note ruinsofalph-b1f-hns.md
- Changed: the west chamber's back wall is open and its inner room drops through Words Room 1 into the hall; each Regi room's drop is solid until that Regi's caught flag, then opens on the next load; the hall's stair comes up at (21,21) on the dig site
- Changed: MAPSEC_RUINS_OF_ALPH appended to region_map_sections.json; stone name sign on the dig site; landmark cell (17,3) on the fly/town map
- Changed: story bible gains "Regirock, Regice and Registeel — Ruins of Alph (optional)"; plastic_ox_map_v7.md gains the Route 36 south section, a chain line and a gating-matrix row
- Fixed: tournament.install rewrote trainers.party with its parties moved to the end, so test_tournament's idempotency check failed on any tree where later generators had appended trainers; it now replaces them in place
- Dialogue: 3 new NPC lines and 1 sign in the research centre and hall; the research-centre plaque is reworded; the roped-stair sign and the west chamber's plain-wall text are removed
- Still open: the east (Route 32) gatehouse stays shuttered and the crawlway stays a cave-mouth pair, because Route 32 and Union Cave are not in the region; the statues and Words Room walls have no text; route36-hns stays `drafted` because its Sudowoodo, repairman and seam-text targets are a separate dialogue pass
