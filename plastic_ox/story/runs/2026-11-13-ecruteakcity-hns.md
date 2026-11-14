# 2026-11-13 — ecruteakcity-hns

- Note: `plastic_ox/story/locations/ecruteakcity-hns.md` (status drafted → implemented)
- Maps: `EcruteakCity_hns`, `EcruteakCity_Gym_hns`, `PlasticOx_DanceTheater`, `EcruteakCity_SageOffice1_hns`, `EcruteakCity_SageOffice2_hns`, `EcruteakCity_Theater_hns`, `Gate_EcruteakCity_Route42_hns`, `Gate_EcruteakCity_Route38_hns` (text only)
- Answer to the ticket question: the gym NPCs had **no** parties — all five interior NPCs were TALK-only donor bodies. They are now four real trainers plus a guide.

## Trainers

- Added `TRAINER_PLASTIC_OX_ECRUTEAK_KADO` (Chimecho 25 / Duskull 24 / Murkrow 24, 3),
  `..._YUI` (Venomoth 26 / Golbat 25, 2),
  `..._GENZO` (Pupitar 27 / Sableye 26 / Torkoal 25, 3),
  `..._RIN` (Gastly 27 / Duskull 26 / Pidgeot 27, 3), all in `src/data/trainers.party`.
- Tier: the request said RU, but the designer corrected it in-session — **Morty and all Gym staff are NU; only the Kimono troupe may break the tier ladder.** Every staff species is NU or lower in `src/data/pokemon/evolution_tier_gates.h` (Duskull/Gastly are PU, the rest NU). Genzo and Rin deliberately field nothing from Morty's own six (Sudowoodo, Haunter, Gastly, Duskull, Golbat, Wigglytuff); Kado and Yui still share Duskull and Golbat with him, unchanged by request. The Kimono parties are untouched.
- IDs 953–956 with victory flags in appended POX event-flag bytes (`POX_EVENT_FLAGS_START + 36..39`); the 0x4A0 trainer-flag run is exactly full at 952 and the Sage block was left alone. `TRAINERS_COUNT_EMERALD` 953 → 957.
- Staff battles are talk-triggered (`TRAINER_TYPE_NONE`), like the existing PU route trainers; the shadow maze has no sight cones to trip.
- `plastic_ox/agent/test_trainer_teams_v2.py` learned the four checkpoints (`gym3`) and now covers 101 trainers / 2680 checks.

## Dialogue

- Town: 9 NPCs + 2 stateful gate/watch scripts, all unique. Bell-founder keeps the "fire remembers nothing" line; the three identical bodies became market stall / fire rota / door watch; the Silver cameo is recast as an old woman at her washing line (sprite changed); the carpenter's boy carries the tower measurement ledger; the lamp-trimmer has before/after-tower text.
- Gym: guide (maze + staff names), 4 trainer intro/defeat/post sets, 2 distinct plaques, and Morty's intro now answers the tower rather than reciting a stock line.
- Dance Theater: only the moon-step after-line changed (it now faces the tower); teams/flags untouched.
- Sages: 3 distinct office sages with before/after text; Sage Office 2 gained a caretaker and five distinct statue inscriptions (it was empty).
- Legacy `EcruteakCity_Theater_hns`: 10 unique lines + 2 distinct signs (unreachable, kept consistent).
- Neighbours' houses, mart and Pokémon Center: House 1's two scripts finally have bodies (almanac grandfather, shutter-mender), House 2's duplicate book passages split, the mart talks rope/lamp oil and deliveries, and the Center drops the "bell rings by itself" ghost hook for the hand-rung ninth-hour bell.
- East gate now opens on **badge 3**, not the tower flag: the `(54,42)` door watch is hidden by `FLAG_BADGE03_GET`, the `(64,41)` watch speaks after the badge. The fire watch no longer disappears with the badge.
- League checkpoint text rewritten as a schedule ("the list is on the wall if you want to count them").
- All new `.string` lines are ≤34 columns; a diff of the emitted strings across the Ecruteak leg shows no duplicates (remaining duplicates are pre-existing lines outside Ecruteak). 66 `.string` blocks were added or rewritten across the city, gym, theater, sage offices, gates and the three service interiors.

## Verified

- `make -j8`: zero errors (ROM 28,248,164 B).
- `plastic_ox/demo/test_ecruteak_gym_trainers.py` (new): each of the four staff starts its own battle with the expected 2–3 party members.
- `plastic_ox/demo/test_ecruteak_gym_gate.py`: gym door both ways, city→gate→Route 119→city, and the door watch still blocks without badge 3.
- `plastic_ox/demo/test_ecruteak_repairs.py`: tower, house, theater, west gate lanes, badge denial/approval, east guards all PASS.
- Screenshots checked by eye: bell-founder page, lamp-trimmer before/after tower, and Kado's intro line all wrap inside the box.
- `test_trainer_teams_v2.py` PASS 2680; `test_nu_encounters_v1.py` PASS 189; `test_pre_mt_moon_v5_5.py` PASS 239; `check_story_notes.py` 61/61 clean; wiki rebuilt and `--check` current.
- Tests were corrected for `gEnemyPartyCountPtr` (the count is a pointer in this build).

## Still open

- `Route38_hns`'s warp still targets a gatehouse warp index that does not exist.
- `LOCALID_ECRUTEK_SILVER` retains its typo as a local id even though the body is now an old woman.
- `build_story.py --check` already reports large pre-existing drift across the region; this pass edited the checked-in `.inc` outputs and mirrored the authored sources at `plastic_ox/alpha/ecruteak/*.inc`, `build_story.py`, `league.py`, so a future regeneration keeps these texts.
