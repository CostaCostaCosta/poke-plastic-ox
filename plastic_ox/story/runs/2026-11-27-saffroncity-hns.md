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
  BLACK BELT sight battles (new ids 963, 964), two students, BRUNO refuses while a clause is
  broken, one prize fighter after the badge. Silph: lobby receptionist heals, lift guard, stairs
  chained on both floors, two corridor grunts on 11F joined by a warp pad (laid with setmetatile
  on load), GIOVANNI on a boardroom step trigger, the terminal with a yes/no, then the PRESIDENT
  and a MASTER BALL.
- Trainers: BRUNO moved from the mossdeep checkpoint (UUBL, Lv. 48–50) to saffron (OU cap 55)
  with the maintainer's requested six, hand-authored in tools/authored_trainers.party: Zapdos,
  Ludicolo (rain), Blaziken, Heracross, Regirock, Celebi; four are SIGNATURE_EXCEPTIONS. Pic is
  Elite Four Bruno Frlg. GIOVANNI is the new trainer class Rocket Boss ("BOSS").
  test_trainer_teams_v2 now uses ADV legality (pox_progression.move_legal_adv: egg moves and
  Gen 3 event/XD moves) for OU-checkpoint trainers. Silph grunts were class/pic Team Aqua; now Team Rocket Frlg.
  trainer_headers_baseline.json updated for those five headers plus the two new ones.
- Engine: CheckADVOUGymRules no longer chains the Little Cup check (it banned Thunder Wave,
  Baton Pass and every sleep move in the OU gyms; this also changes Clair's unplaced greeter).
- Flags: POX_EXT +13 FLAG_POX_DOJO_PRIZE, +14 FLAG_POX_SILPH_MASTER_BALL, +15 FLAG_POX_HIDE_SILPH_STAFF
  (renumbered, like the Dojo trainer ids 963/964, after the Jirachi PR took +12 and 962)
- Follow-up pass (same day): the two purple-door houses open onto FRLG interiors with their own
  residents; entering the city sets HEAL_LOCATION_POX_SAFFRON, so a loss whites out to (18,39).
- Gotchas: trainerbattle_single asserts when run from a coord trigger (no selected object), so
  the boardroom trigger shows the intro itself and uses trainerbattle_no_intro. DOUBLE TEAM,
  MINIMIZE, SWAGGER and BRIGHTPOWDER are removed from the ROM, so the live OU clauses are the
  OHKO moves, ASSIST and LAX INCENSE. audit_npc_dialogue follows label names inside comments.
- Verified: test_saffron.py (new; doors both ways, desk and BRUNO rule refusal, BLACK BELT,
  badge, prize, heal, stairs, three grunts in order, pad, GIOVANNI trigger, terminal, MASTER
  BALL, walk back out, dormant grunts, retired-room exits, both houses, whiteout to Saffron); test_story gates / battles /
  callbacks / travel; test_region_v7 (44 crossings); test_npc_dialogue; make pox-check-static
- Not caused by this pass: test_league_rules.py ordering() fails the same way on master
  (ae480ef170). test_npc_dialogue's Weather Institute wanderer check failed once and passed on rerun.
- Still open: the station and the closed hall stay closed doors by design; MASTER BALL as the
  Silph reward is a balance call.
