# Port verification

## Outdoor entrance width

Rustboro's former north exit had five walkable columns but only one coordinate
warp. The replacement connects city columns 19..22 to Route 24 bridge columns
16..19 with offsets +3/-3. Test all four lanes, not just the center. The east
riverside path must terminate visibly before crossing into the city's trees.
Keep signs beside the approach and use each layout's own road/forest assets.

Reproduce geometry with `python3 plastic_ox/agent/improve_rustboro_north.py`.
Topology and sign generation live in `plastic_ox/alpha/region_v7.py`; inspect
the patch from `build_story.py` before applying unrelated regeneration drift.
Run `plastic_ox/demo/test_rustboro_north.py` in the mGBA environment below for
all-lane round trips, blocked shoulders, blank-frame checks and scrolling
redraw comparisons. Inspect its fresh `rustboro_north_*.png` screenshots.

Source comparisons inspected 2026-09-18:

- [Emerald Enhanced Route135](https://github.com/Enhanced-Projects/Emerald-Enhanced/blob/8feeffde06a160c3f7a0e94689c0fd2ed13214f7/data/maps/Route135/map.json)
  uses a south connection at +20 to Pacifidlog; the town returns at -20.
- [Wishes of Tomorrow's MunenVillage gate](https://github.com/jmaloney95/Wishes-Game/blob/343c9ff548d20f1d946433fa60e6570dc42b26df/data/maps/MunenVillage/scripts.inc)
  checks story flags and then permits walking over its ordinary connection.
  Its map data covers all three gate lanes with the check.

Inference for Plastic-Ox: prefer reciprocal connections for continuous outdoor
roads; keep story checks separate and preserve intentional warp entrances.
These examples do not validate our cross-primary renderer. Emerald Enhanced
and the expansion-based Wishes project are distinct bases; do not present
them as multiple verified Enhanced custom-region forks.

Read this reference for any new import, seam/warp change, cross-layout
transition, malformed-map repair, or ledge regression.

## Import manifest

Record:

- source repo revision, map JSON, layout entry, map/border binaries;
- source family (`emerald`, `frlg`, or `hns`);
- primary/secondary tileset symbols and every copied asset;
- destination map group and both directions of each connection or warp;
- removed/redirected scripts, object events, coordinate events, and flags;
- authoritative land/water/fishing encounter header;
- build, audit, headless traversal, screenshot, and soak commands.

HNS uses a mixed format: 640 primary tiles/metatiles, 7 primary palettes,
16-bit Emerald attributes, and an Emerald-style 2x2 border. This combination
requires `layout_version: hns` in Plastic-Ox. FRLG and HNS share a primary
partition size, but their attribute and border formats are not interchangeable.

## Geometry and mechanics

Confirm dimensions from `data/layouts/layouts.json` and binary byte size
(`width * height * 2`). Derive connection offsets using this checkout's
connection convention, then test the inverse. A graph edge is not evidence of
a walkable opening.

For warps, validate approach tile, warp tile, destination landing, elevation,
collision, and the return warp. Never accept the inherited Dark Cave landing
inside solid rock; carve or retarget it and exercise both cave mouths.

For each ledge, record:

| Role | Coordinate | Required result |
|---|---:|---|
| approach | `(x, y)` | walkable |
| ledge | `(x+dx, y+dy)` | direction behavior, collision, matching artwork |
| landing | `(x+2dx, y+2dy)` | walkable, compatible elevation |
| reverse input | landing toward ledge | blocked |

Capture approach and landing screenshots. Also log the metatile ID and
behavior at the ledge coordinate so visual and mechanical evidence refer to
the same block.

## Runtime matrix

For each direction across a seam or warp, assert:

- expected map group/number and landing coordinate;
- full primary/secondary graphics and palette partition for the destination;
- no stale source camera/map-view blocks;
- no all-white forced-blank frame;
- collision, elevation, nearby ledges, and objects agree with rendering;
- a deliberate grass/water encounter uses the selected table;
- no source-story coordinate event fires;
- no crash or hang during transition and a post-transition soak.

Fresh screenshots are mandatory for malformed-tile regressions. Compare them
to the source map or a known-good target-family map, not to an old corrupted
Plastic-Ox capture.

## Camera redraw and border phase

Pallet Town / Route 101 at revision `7fa02b70f0` exposed two independent
rendering bugs without incorrect source blockmaps or connection offsets:

- `CameraMove` changed the destination position and redrew the whole map before
  `AddCameraTileOffset` advanced the circular BG buffer. Scrolling then replaced
  rows against an offset full view, making roofs and trees appear duplicated.
  Clear the saved source view there, but request the full redraw for
  `RedrawMapSlicesForCameraUpdate`, after the tile offset advances. Both camera
  update variants must consume the request; a full draw/reset clears it.
- The incompatible-tileset margin fallback stretched one blocked edge row,
  repeating partial trees. Use `GetBorderBlockAt` for blocked edge terrain so
  the layout's border width/height and coordinate phase remain intact. Extend
  walkable edge blocks to keep the entrance open. Never copy foreign metatile
  IDs to make the neighbor visible under the current tileset.

Run the focused regression on a freshly built ROM:

```sh
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_camera_seam.py
```

The primary ROM includes the authored story. The test warps to
Route 101's south entrance, walks both seam directions, checks Pallet's border
phase and open path, checks every crossing frame for forced blank, and compares
the maintained 15x15-metatile BG view with a stationary full redraw at identical
coordinates. Exclude the unused sixteenth buffer row/column from that comparison.
Inspect `plastic_ox/demo/shots/camera_*.png`, including the view after walking
farther into Pallet. A stationary reference redraw repairs corruption, so take
the actual screenshot and buffers before invoking it.
