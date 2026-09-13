# Region rendering review — 2026-09-10

This is a historical pre-v7 audit. Current targets are in the
[v7 implementation plan](../alpha/PLAN.md). The previous `region_layout.svg`
has been removed; it can be regenerated as a view of implemented ROM data and
must not be confused with the authored `plastic_ox_topology.svg` design.

The audited layout was `region_layout.svg`, generated
from map JSON, layout dimensions, connection offsets, warp events, and direct
story-script cave warps by `render_region_layout.py`. It includes 46 surface
maps, four caves, eight ordinary directed cave warps, and seven story-script
cave links. Cave placement is schematic; adjoining map rectangles do not prove
a walkable opening. Ordinary building interiors are omitted from the diagram.

## Repairs

The previous Lavender/Cinnabar compression and secondary-palette header fixes
are present in base revision `2ee8ee8f3e`. Fresh screenshots show coherent assets.
The HNS reference checkout is `/home/eddie/repos/pokehns-expansion` at
`44f50eedef`; HNS layouts retain 640 primary metatiles and u16 attributes.

- Corrected the renderer audit to recognize the full `MAPGRID_UNDEFINED`
  block (`0x03FF`). Goldenrod's `0x07FF` block is valid metatile 1023 with
  collision bits, and must not be rendered as a border fallback.
- Dark Cave exits at `(14,20)` and `(56,46)` used ordinary floor behaviors.
  Cloned their exact graphics and layer attributes into dedicated secondary
  metatiles 946 and 947, using `MB_LADDER` for a warp that lands in place.
  Door arrival movement would step into the rock below the Route 31 mouth.
  The map still uses `gTileset_Johto_General_Hns` and
  `gTileset_Cave_Default_Hns`. The shared floor definitions are unchanged.
  `plastic_ox/agent/fix_cave_exit_behaviors.py` reproduces this repair and is
  idempotent; run it after reimporting this cave.
- Corrected Mt. Moon's reciprocal links: Route 3 warp 0 ↔ Mt. Moon warp 1;
  Route 4 warp 0 ↔ Mt. Moon warp 0. Updated the wave import rules too.
- Corrected the legacy door-repair utility's primary partition and HNS behavior
  mask. It is a bulk shared-attribute editor and was not run on the region.
- Seam probes start one walkable tile inland where possible so arrival
  animation cannot cross the boundary before the test starts (Route 4). Empty
  assertion messages retain their exception type in the report.
- Dive/emerge transitions are now explicitly reported as outside the camera
  seam test instead of being misinterpreted as east/west connections.

No NPC, trainer, item, story event, encounter table, or cave artwork was removed.

## Verification commands

```sh
python3 plastic_ox/demo/render_region_layout.py
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py "$PWD"
make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM PLASTIC_OX_BUILD=triggers modern
export LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/audit_region_rendering.py
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_cave_connections.py
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_cave_connections.py --triggers
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_camera_seam.py
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_camera_seam.py --triggers
git diff --check
```

Cave tests exercise all eight ordinary directed cave crossings, check reciprocal
indices, actual map identity, landing collision, rendering, and a 300-frame
post-transition soak. Both ROM variants pass. Screenshots and JSON reports are
in `shots/region_audit` and `shots/region_audit_triggers`. The seven conditional
story-script links in the SVG are statically extracted, not covered by this
ordinary-warp test.

The visual audit uses isolated warps for unreachable sample points; those are
recorded explicitly and do not prove continuous navigation. Camera-buffer
checks supplement screenshot review; they do not independently verify palette
artwork. No blanket claim of region-wide travel completeness is made.

Final default-ROM results: **87 maps, 1,660 sampled views, zero map errors,
zero buffer mismatches**. Of these samples, 796 required explicitly recorded
isolated placements. Fresh seam audit: **56 successful directed crossings,
eight failed walking checks, three dive/emerge transitions excluded**; all 56
successful crossings had zero buffer mismatches. See
`shots/region_audit/report.json` for views and `shots/region_seams/report.json`
for the updated seam classifications. Entry contact sheets `overview_0.png`
through `overview_5.png` and `cave_overview.png` were visually reviewed.

## Travel findings outside the rendering repair

The walking-only seam audit retains failures for closed terrain, water movement,
and overlapping connections. In particular:

- Ilex/Route 34 has no open edge. The source also uses a closed edge and gate
  warps; changing its geometry to make the camera connection walkable would
  redesign that entrance.
- Rustboro's north Route 115 connection takes priority over its overlapping
  imported Route 2 connection. A round trip via Route 2 is not verified.
- Route 14 and Goldenrod meet at incompatible elevations (1 and 3).
- The audit starts on foot; water-only seams need surf-aware traversal.
- The native Route 115 → Route 114 and Route 116 → Verdanturf edges have no
  matching opening for this walking test.

These remain recorded rather than hidden by a passing graphics result.
