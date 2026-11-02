---
name: plastic-ox-map-baseline
description: Reduce imported Plastic-Ox routes, towns, caves, and interiors to foundational map events by removing automatic coordinate and map-script triggers while preserving intentional warp events, connections, NPCs, trainers, items, and signs. Use when starting a map's gameplay scripting from scratch or diagnosing an unexpected tile-triggered teleport; do not use when story triggers must be retained.
---

# Plastic-Ox map baseline

Make automatic behavior opt-in. A baseline map may retain layout and tilesets,
`connections`, `warp_events`, `object_events`, and `bg_events`; it has no
`coord_events` and no registered `map_script` entries. Do not confuse a warp
event (a deliberate door, cave mouth, stair, or edge transition) with a
coordinate event whose script happens to call `warp`.

## Audit the target

Work in `/home/eddie/repos/poke-plastic-ox`. Inspect `git status` first and
preserve unrelated work. Run the repository import audit, then inventory each
target map:

```sh
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py \
  /home/eddie/repos/poke-plastic-ox
python3 .agents/skills/plastic-ox-map-baseline/scripts/audit_map_baseline.py \
  data/maps/MapName
```

For each reported coordinate event, record its coordinate, variable, script,
and intended effect before removing it. Inspect the blockmap/metatile behavior
at every retained warp coordinate and check both ends of the transition. A
connection is also a foundational transition and should remain unless the
region design explicitly replaces it.

## Reduce to baseline

- Set `coord_events` to `[]` in the map JSON.
- Replace registered map scripts with an empty `<MapName>_MapScripts::` table
  (`.byte 0`). Keep that existing empty table unchanged when already present.
- Delete script blocks used only by removed coordinate or map-script events.
  Before deleting a label, search the repository for all references.
- Search import/generation tooling for the target map and removed script labels;
  remove declarations that would recreate automatic triggers on regeneration.
- Preserve object and background events, including trainers and item balls,
  even if their dialogue or battles are provisional. Preserve real
  `warp_events` and `connections`.
- Do not repurpose story variables or flags as portal controls. Do not add a
  scripted warp to compensate for an unverified door/edge transition; repair
  the warp event, connection, or metatile behavior instead.

Re-run the baseline audit. It succeeds only when no coordinate events or
registered map scripts remain.

## Verify

Validate JSON, run the deterministic import audit again, build the ROM with the
configured devkitARM command, and walk/smoke-test every retained entry and exit
in both directions. Walk across each former trigger square and confirm it is
ordinary terrain. Confirm preserved NPCs, trainers, items, and signs still
interact, and review the diff to ensure no unrelated event category changed.
