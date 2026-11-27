# 2026-11-27 — dragonsden-entrance-hns

- Note: plastic_ox/story/locations/dragonsden-entrance-hns.md (new, implemented); blackthorncity-hns.md updated (the Den is now a shut door, not "never a map")
- Maps: DragonsDen_Entrance_hns, DragonsDen_Cavern_hns (imported by plastic_ox/alpha/import_dragons_den.py), BlackthornCity_hns (door warp 3 at (26,12), elder at (26,13))
- Changed: elder blocks the Den until FLAG_SYS_GAME_CLEAR; RAYQUAZA arrival scene on the shrine plaza and an ordinary legendary battle at Lv.70 or the party's top level
- Verified: plastic_ox/demo/test_dragons_den.py (static + mGBA): gate before/after, door/ladder/cavern both ways, arrival scene once, Lv.70 and Lv.80 scaling, flee keeps it, catch removes it
- Still open: the Blackthorn lake and the cavern water were checked by flood fill, not by a Surf walk; the faint branch (RAYQUAZA stays) was not driven in the emulator; shrine interior not imported
