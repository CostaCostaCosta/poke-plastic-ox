# GEN3 ROM State — ec/rom-native-gen3

Repo: /home/eddie/repos/poke-plastic-ox (pokeemerald-expansion fork).
Purpose: document battle-state storage + mechanics-config deltas needed for a
production (non-omniscient) gen3 ROM-native observation encoder, implement the
schema v2 C encoder, and build the load-bearing items enum mapping for metamon.

## Task checkboxes
- [ ] 1. `plastic_ox/agent/gen3_items_expansion_enum.json` (expansion items.h x Showdown items.ts, gen<=3 held items)
- [ ] 2. Battle state storage doc (struct BattlePokemon, globals, reveal hooks)
- [ ] 3. Mechanics config audit (config/battle.h GEN_LATEST -> GEN_3 recommended patch table)
- [ ] 4. C encoder schema v2 (include/rom_native_obs.h + src/rom_native_obs/rom_native_obs.c)
- [ ] 5. metamon `rom-native/ROM_NATIVE_OBSERVATION.md` appendix (edit only, no commit there)

## Progress log
- 2026-08-: branch `ec/rom-native-gen3` created from HEAD; scaffold committed.
