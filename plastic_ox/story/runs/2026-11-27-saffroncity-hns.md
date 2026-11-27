# 2026-11-27 — saffroncity-hns

- Note: plastic_ox/story/locations/saffroncity-hns.md (status drafted → implemented)
- Maps: SaffronCity_hns, SaffronCity_Dojo_Frlg, SilphCo_1F_Frlg, SilphCo_11F_Frlg;
  PlasticOx_BrunoGym / PlasticOx_Silph emptied (placeholders with a door back to the street)
- Source: new area module plastic_ox/alpha/saffron.py (installed last by region_v7.apply_region);
  the Bruno / Silph battles stay in build_story.py. Generator output applied as a delta over the
  already-drifted files (plastic_ox_story.inc, plastic_ox_region.inc, SaffronCity_hns/map.json,
  story_manifest.json); the drift baseline did not change.
- Changed: removed the three teleport guides and the two teleport rooms. Town doors (45,12) →
  FRLG Dojo, (33,30) → FRLG Silph 1F, (18,38) → shared Kanto Pokemon Center. Nine residents with
  nine lines, four building signs, four closed-door lines, two gate signs reworded; city music is
  MUS_RG_PEWTER (was MUS_RG_SILPH). Dojo: desk clerk with the OU clause check, two optional
  BLACK BELT sight battles (new ids 962, 963), two students, BRUNO refuses while a clause is
  broken, one prize fighter after the badge. Silph: lobby receptionist heals, lift guard, stairs
  chained on both floors, two corridor grunts on 11F joined by a warp pad (laid with setmetatile
  on load), GIOVANNI on a boardroom step trigger, the terminal with a yes/no, then the PRESIDENT
  and a MASTER BALL.
- Trainers: BRUNO moved from the mossdeep checkpoint (UUBL, Lv. 48–50, two Fighting-types) to
  saffron (OU cap 55): Medicham, Machamp, Hariyama, Blaziken, Hitmontop, Steelix; pic is
  Elite Four Bruno Frlg. Silph grunts were class/pic Team Aqua; now Team Rocket Frlg.
  trainer_headers_baseline.json updated for those five headers plus the two new ones.
- Engine: CheckADVOUGymRules no longer chains the Little Cup check (it banned Thunder Wave,
  Baton Pass and every sleep move in the OU gyms; this also changes Clair's unplaced greeter).
- Flags: POX_EXT +12 FLAG_POX_DOJO_PRIZE, +13 FLAG_POX_SILPH_MASTER_BALL, +14 FLAG_POX_HIDE_SILPH_STAFF
- Gotchas: trainerbattle_single asserts when run from a coord trigger (no selected object), so
  the boardroom trigger shows the intro itself and uses trainerbattle_no_intro. DOUBLE TEAM,
  MINIMIZE, SWAGGER and BRIGHTPOWDER are removed from the ROM, so the live OU clauses are the
  OHKO moves, ASSIST and LAX INCENSE. audit_npc_dialogue follows label names inside comments.
- Verified: test_saffron.py (new; doors both ways, desk and BRUNO rule refusal, BLACK BELT,
  badge, prize, heal, stairs, three grunts in order, pad, GIOVANNI trigger, terminal, MASTER
  BALL, walk back out, dormant grunts, retired-room exits); test_story gates / battles /
  callbacks / travel; test_region_v7 (44 crossings); test_npc_dialogue; make pox-check-static
- Not caused by this pass: test_league_rules.py ordering() fails the same way on master
  (ae480ef170). test_npc_dialogue's Weather Institute wanderer check failed once and passed on rerun.
- Still open: whiteout in Saffron returns to the last vanilla heal location (the shared Kanto
  Center nurse sets no respawn); the station, the closed hall and two houses have no interiors;
  GIOVANNI is still trainer class Leader; MASTER BALL as the Silph reward is a balance call.
