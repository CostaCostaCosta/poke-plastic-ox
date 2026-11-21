# Plastic Ox project docs

Start with the repo-root `AGENTS.md`. This file is the index for `plastic_ox/`.

## Source of truth, highest first

1. `plastic_ox_story_v7.md`: story bible (progression, reveal ladder, Gym order, Champion Bill).
2. `plastic_ox_map_v7.md` and `plastic_ox_topology.svg`: region graph and unlock rules.
3. `alpha/STORY_TRIGGERS.md`: persistent flags, gate contract, acceptance table.
4. `story/locations/<slug>.md`: per-location design notes. These are validated
   against the code and serve as the work tickets.
5. Current map JSON, scripts and `trainers.party`: what the game actually does.

When two of these disagree, the higher one wins. Fix the lower one in the same PR,
or file a follow-up.

## Current plans and specs

| Doc | Status |
|---|---|
| `alpha/PLAN.md` | Current v7 implementation plan |
| `alpha/REGION_PLAN.md` | Target region legs and assets |
| `alpha/IMPORT_GUIDE.md` | How donor maps are imported |
| `alpha/STORY_STATE_AUDIT.md` | Flag/state audit |
| `encounter_tables/plastic_ox_pre_mt_moon_encounters_v5_5_agent_ready.md` | Authoritative early encounter tables |
| `docs/plasticox_evolution_gating_plan_v1.md` | Evolution/tier gating design (engine: `src/data/pokemon/evolution_tier_gates.h`) |
| `tools/ROUTE_TRAINER_PACING.md`, `tools/TRAINER_TEAMS_V2_REPORT.md` | Trainer pacing and team rules |
| `tools/ROM_SPACE_TRIM_AUDIT.md`, `battle/metamon/ROM_SPACE_AUDIT.md` | ROM space |
| `artifact_cleanup.md` | Cleanup inventory (dated snapshot) |
| `demo/TESTING.md` | Emulator test fixtures |
| `docs/build_test_setup.md` | How the toolchain was installed on the dev machine |
| `generated_manifest.json` | Which generator owns which files |

Stale by their own admission: `town_map/` and `topology_app/` predate v7.
`human_todo_list.txt` is the maintainer's personal list, not agent instructions.

## Directories

| Dir | Contents |
|---|---|
| `alpha/` | Story/region generators and per-area modules (Goldenrod, Ecruteak, league, ...) |
| `story/` | Location notes, validator, context/next-pass/beads tooling |
| `tools/` | Live audits, trainer-team generator and test, ROM-space measurement, save helpers |
| `demo/` | mGBA harnesses (`test_*.py`) and walk/navigation libraries |
| `encounter_tables/` | Encounter specs, appliers and regression tests |
| `battle/metamon/` | On-ROM neural trainer AI |
| `wiki/` | Static wiki generator and note editor (`site/` is built, untracked) |
| `bin/` | `pox-env.sh`, `pox-mgba-python`, `pox-check-static`, `pox-check-emu` |
| `archive/` | Completed one-off migrations, dated reports and old plans: history only |
