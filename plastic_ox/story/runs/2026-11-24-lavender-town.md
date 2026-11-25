# 2026-11-24 — lavender-town

- Note: plastic_ox/story/locations/lavender-town.md (status drafted → implemented)
- Maps: LavenderTown_hns, PokemonTower_1F..7F_Frlg, LavenderTown_VolunteerPokemonHouse_Frlg,
  LavenderTown_House1_Frlg; PlasticOx_PokemonTower / PlasticOx_FujiHouse emptied (placeholders)
- Changed: removed the TowerGuide/FujiGuide teleport NPCs and the Mt. Pyre stand-in
  tower. Town doors (22,6) → FRLG Pokemon Tower, (8,13) → Volunteer House (FUJI),
  (10,19) → House1. Channelers no longer battle; FRLG rival (2F) and Marowak ghost (6F)
  scenes removed (their FRLG scene vars alias live Emerald vars). Three Team Rocket
  grunts on 7F (new TRAINER_PLASTIC_OX_TOWERGRUNT3 = 960); FUJI walks the player home and
  gives the SURF KEY there. Town, tower and house dialogue rewritten. Tower encounters
  replaced with UU-capped gPoxUUPokemonTower3F..7F tables including Misdreavus.
- Flags: POX_EXT +0..+10 (FUJI_RESCUED, HIDE_HOUSE_FUJI, HIDE_LAVENDER_GRUNT_3, eight
  tower item balls)
- Verified: test_lavender.py (doors both ways, stairs 1F→7F, grunt order, rescue, SURF KEY,
  STORY_FUJI, EEVEE); test_story gifts/gates/battles; test_region_v7 route110_lavender,
  lavender_route8, lavender_harbor; test_npc_dialogue; make pox-check-static
- Still open: the tower door is on the HNS radio-station building; Soul House (22,19) has no
  interior
