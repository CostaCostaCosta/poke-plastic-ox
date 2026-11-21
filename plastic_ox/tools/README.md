# Live Plastic Ox tools

Run from the repo root. `make pox-check-static` runs the checks marked ✓.

| Tool | Purpose |
|---|---|
| `test_trainer_teams_v2.py` ✓ | Regression test for every `TRAINER_PLASTIC_OX_*` party (legality, tiers, caps, wiring) |
| `apply_trainer_teams_v2.py` | Route-trainer roster table and `.party` writer (`--check` self-test) |
| `pox_progression.py` | Story checkpoints, species availability, tier gating, move legality (library) |
| `write_trainer_teams_v2_report.py` | Regenerates `TRAINER_TEAMS_V2_REPORT.md` |
| `audit_warp_connections.py` ✓ | Static warp/connection graph audit |
| `check_map_refs.py` ✓ (`--changed`) | Unknown constants in map JSON (`--map X`, `--changed`); the full run has known donor-map noise |
| `check_generated.py` ✓ | New drift between `build_story.py` output and checked-in files |
| `audit_native_seams.py` | Native seam audit for camera connections |
| `audit_cleanup_artifacts.py` | JSON triage for the artifact-cleanup skill |
| `remap_metatile_behaviors.py` | HNS→ours metatile behavior mapping (library; needs `$POX_HNS_DONOR`) |
| `render_solidity.py` | Render a map's collision/behavior overlay |
| `warp_extras_static.py` | Ledge/ladder/auto-teleport static analysis |
| `ROM_SPACE_MEASURE.py` | Re-derive ROM-space numbers (needs a built ROM) |
| `grant_all_hms_save.py`, `grant_warp_block_save.py` | Make test saves |

Superseded one-off scripts are in `plastic_ox/archive/agent/`.
