# Native warp connection review

Date: 2026-09-18
Scope: active `region_v7.py` anchors plus retained native cave/room closure
maps (the five Seafoam floors, Mt. Moon story floors, Underground Path rooms,
and Route 2 entrance/building rooms). Script: `audit_warp_connections.py`.

## Inventory

The closure contains 60 maps and 208 native warp events. 107 events target
another map in the active closure; 101 target ordinary facilities, dynamic
maps, or donor-world maps which are outside this region's active closure. Of
the 107 internal links, 83 are reciprocal and 24 are intentional landing
anchors (multi-lane doors, cave stair arrivals, or an arrival warp that points
at the paired door rather than forming a self-loop). There are no invalid
destination indices.

The static audit is reproducible with:

```sh
python3 plastic_ox/agent/audit_warp_connections.py --json /tmp/warp_audit.json
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py .
```

## Runtime evidence on the current ROM

These tests were run before any build or source mutation:

```sh
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_region_v7.py --warps --only DarkCave
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_cave_connections.py
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_regional_doors.py
```

Results: Dark Cave's two crossings pass; the cave harness passes all four
directed Dark Cave crossings with zero maintained-BG mismatches; and all ten
regional door cases pass animated entry. These are focused runtime samples,
not proof that every one of the 107 internal links has been traversed.

## Findings and fixes

No isolated interior source required a geometry or warp-index fix in this
review. The previously fragile Dark Cave landings are walkable and render
cleanly in both directions, and the dedicated door/room cases are stable.
The reusable audit and report are the concrete maintenance additions; no
generated manifests, engine C, exterior `region_v7.py`, or unrelated dirty
files were changed.

## Intentional exceptions

Landing anchors are not treated as broken reciprocity: multi-lane entrances
share one destination door, and stair/door arrivals deliberately point to an
inbound landing warp. Dynamic facilities (`MAP_DYNAMIC`) and donor-world
facility destinations are outside this region's closure. Seafoam's ladder and
current transitions are puzzle-directed; the generic cave harness does not
rewrite those directed floor links.

## Limitations / handoff

Collision, elevation compatibility, and post-transition rendering are
runtime properties. The focused current-ROM tests cover Dark Cave and the
regional door sample, while the static audit covers all closure indices.
Run the parent agent's complete `test_region_v7.py --warps` after its exterior
changes and rebuild; do not infer that the 101 external links are invalid from
the closure-only audit.
