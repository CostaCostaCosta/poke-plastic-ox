# 2026-11-27 — Meteor Falls: Jirachi and its sage

**Scope:** audit Meteor Falls for world building and mechanics; add JIRACHI and a sage to the Bagon chamber (`MeteorFalls_B1F_2R`).

## Done
- `plastic_ox/alpha/meteor_falls.py` (+ `meteor_falls/events.inc`, `meteor_falls/trainers.party`), hooked into `region_v7.py` after `tin_tower`. JIRACHI `(6,3)`, sage `(6,4)`, shared `pox_legendary_sage` macro, Lv 55.
- `TRAINER_PLASTIC_OX_JIRACHI_SAGE` = 962 (Sage trainer-flag range); team Milotic / Skarmory / Claydol / Blissey / Jirachi / Dugtrio (supplied Gen 3 OU stall set; Dugtrio IVs give Hidden Power Bug), Lv 55.
- `FLAG_POX_CAUGHT_JIRACHI` = `POX_EXT_FLAGS_START + 12`.
- Tin Tower: the Jirachi sage comes home to the sage office `(2,8)` and counts toward the five.
- Story bible: new "Meteor Falls — Jirachi" section. Location note: plot point 8, and the "must not hand out a legendary" rule now allows this Jirachi.
- `plastic_ox/demo/pox_fixtures.py`: `game()` now initializes the POX_EXT flag block's magic too. Before this, a flag the test wrote there was wiped on first native access.

## Audit findings left open
Dead Magma/Aqua actors on 1F 1R; Cozmo's Emerald script with a zeroed flag; Nugget under the Iron Tail flag; the self-warp at 1F 1R `(27,18)`; Lv 14-20 encounters on 1F 1R against Lv 33-40 deeper in; Zubat/Solrock surf tables; vanilla Steven in the side cave.
