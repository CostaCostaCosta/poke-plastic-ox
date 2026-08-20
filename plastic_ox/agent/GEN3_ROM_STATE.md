# GEN3 ROM State — ec/rom-native-gen3

Repo: /home/eddie/repos/poke-plastic-ox (pokeemerald-expansion fork).
Purpose: document battle-state storage + mechanics-config deltas needed for a
production (non-omniscient) gen3 ROM-native observation encoder, implement the
schema v2 C encoder, and build the load-bearing items enum mapping for metamon.

## Task checkboxes
- [x] 1. `plastic_ox/agent/gen3_items_expansion_enum.json` (expansion items.h x Showdown items.ts, gen<=3 held items) — 96 entries, committed
- [ ] 2. Battle state storage doc (struct BattlePokemon, globals, reveal hooks)
- [ ] 3. Mechanics config audit (config/battle.h GEN_LATEST -> GEN_3 recommended patch table)
- [ ] 4. C encoder schema v2 (include/rom_native_obs.h + src/rom_native_obs/rom_native_obs.c)
- [ ] 5. metamon `rom-native/ROM_NATIVE_OBSERVATION.md` appendix (edit only, no commit there)

## Progress log
- 2026-08-: branch `ec/rom-native-gen3` created from HEAD; scaffold committed.

## Section 1 — items mapping (committed)
- 96 gen<=3 held items mapped from expansion enum + `gen<=3` in base `data/items.ts` (all base entries have explicit `gen`).
- 13 gen<=3 base items unmapped (absent from expansion items.h): gen2 obsolete berries
  (berry, bitterberry, burntberry, goldberry, iceberry, mintberry, miracleberry, mysteryberry,
  przcureberry, psncureberry), pinkbow, polkadotbow, generic mail.
- Known gen3 held items NOT mappable under the strict base-data `gen<=3` rule (documented exceptions):
  - blueorb/redorb — base items.ts says gen 6 (ORAS re-release); expansion has ITEM_RED_ORB=290, ITEM_BLUE_ORB=291.
  - soothebell, expshare, smokeball, luckincense, pureincense — absent from this Showdown's base items.ts (expansion has them).
  - fullincense, oddincense, waveincense, rockincense, roseincense — base data says gen 4 though Hoenn items.
