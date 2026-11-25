# 2026-11-25 — Ecruteak Dance Theater: Kimono troupe as one battle

Location: `ecruteakcity-hns` (`PlasticOx_DanceTheater`).

## Change

- The five one-dancer Kimono battles are now one battle,
  `TRAINER_PLASTIC_OX_KIMONO_TROUPE` (id 961), fought by NAOKO at the centre of
  the stage. Party: EEVEE Lv27, JOLTEON 28, VAPOREON 28, FLAREON 28,
  UMBREON 28, ESPEON 29 (gym3 / NU, cap 30; four Eeveelutions are the declared
  signature exception).
- Staging: the dancers stand in a semicircle open toward the audience —
  SAYO (6,4) facing right, KUNI (8,3), NAOKO (10,2), MIKI (12,3), ZUKI (14,4)
  facing left. The player steps into the circle to (10,3) to talk to NAOKO.
- The four side dancers only talk: a before-line naming their step in the
  dance order and pointing at NAOKO, and their existing after-line.
- Winning sets all five `FLAG_POX_KIMONO_*` flags, so the EEVEE gift
  (`Pox_Kimono`) is unchanged, and old saves with some dancers already beaten
  still reach it. The gift text now ties the gift EEVEE to the troupe's lead.
- The old `TRAINER_PLASTIC_OX_KIMONO<SPECIES>` ids keep their numbers (save
  data) and headers; nothing battles them.
- Source of truth: `plastic_ox/alpha/build_story.py` (scripts, objects, the
  id/header), `plastic_ox/tools/authored_trainers.party` (the party).

## Verification

- `plastic_ox/demo/test_dance_theater.py` (new) in mGBA.
