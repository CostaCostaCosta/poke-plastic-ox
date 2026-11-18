# 2026-11-18 — goldenrodcity-hns (Whitney Gym: pox-2ma.2, pox-2ma.4)

- Note: plastic_ox/story/locations/goldenrodcity-hns.md (status stays drafted; other beads open)
- Maps: PlasticOx_WhitneyGym, GoldenrodCity_Gym_hns
- Changed: PlasticOx_WhitneyGym gains a PU-rule greeter (7,17), exit NPC Pox_WhitneyGymExit (4,17) and the five hint NPCs (1,18) (9,4) (9,18) (1,4) (2,3), wording kept from the legacy Gym (only rewrapped). Legacy GoldenrodCity_Gym_hns is now a tombstone: no objects or scripts, one exit warp, map id kept so numeric ids and old saves stay stable. alpha/goldenrod sources and city_doors.json updated to match; goldenrod.py no longer rewrites the Whitney exit warp to the legacy room.
- Dialogue: Pox_WhitneyNeedsBadge, Pox_WhitneyNeedsMoon, Pox_WhitneyDone, Pox_Text_WhitneyDefeat replace the shared Pox_NotReady / Pox_Done / Pox_Text_Defeat for Whitney only. build_story.py battle()/start() take notready/defeat overrides.
- Decisions: the new Gym is the real Gym (door already points there). Hint NPCs sit off the Rustboro-layout walking path; a flood-fill with all NPCs as blockers still reaches Whitney. Whitney's pre-battle and post-battle lines unchanged.
- Verified: story note check, wiki --check, ROM builds with zero errors; test_review_fixes.py Goldenrod Gym door and exit pass (its later Ecruteak east-road assertion fails, unrelated). Not walked in emulator: talking to each new NPC.
- Still open: build_story.py --check already drifts on many files; room() in build_story.py cannot emit the hand-maintained Whitney room objects/scripts, so PlasticOx_WhitneyGym map.json/scripts.inc remain hand-edited. Clair Gym has the same unwired Greeter script.
