# Port verification

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
