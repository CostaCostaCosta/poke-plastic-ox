# Pokémon Plastic Ox — Map Stitch Demo v0.1

**Date:** 2026-08-22  
**Scope:** default Emerald build proof of concept  
**Repository state:** uncommitted; do not commit as part of this demo work.

## Result

This proof of concept stitches **Pallet Town (FRLG/Gen 1)** north into
**Route 101 (Emerald/Gen 3)**, which connects north into **Oldale Town**. It
is deliberately a traversal demo, not a reproduced FRLG opening: imported
story scenes are removed so the two cross-generation seams can be exercised
without a cutscene, battle, or encounter interrupting the route.

```
Pallet Town (24 x 20, FRLG tilesets; MAP 75,0)
       | up +2 / down -2
Route 101 (20 x 20, Emerald tilesets; MAP 0,16)
       | up/down 0
Oldale Town (20 x 20, Emerald tilesets; MAP 0,10)
```

The authoritative executable verifier is
`plastic_ox/demo/walk_demo.py`. Its headless run checks the complete trip, the
no-battle condition, every transition frame for a forced-blank white flash,
and a real one-way Route 101 ledge jump; `shots/verified_01_bedroom.png`
through `shots/verified_09_pallet_return.png` are its evidence. The dedicated
ledge shots are `verified_06a_ledge_approach.png` and
`verified_06b_ledge_landing.png`.

## Verified play flow

1. From the title menu, select **NEW GAME** and complete the normal intro/name
   prompts. The moving-truck field sequence is skipped; the player appears
   directly at `(6,6)` in the Pallet bedroom,
   `MAP_PALLET_TOWN_PLAYERS_HOUSE_2F` `(38,1)`.
2. Go downstairs to `(38,0)`, speak with Mom, then leave for Pallet Town
   `(75,0)`.
3. Walk north out of Pallet into Route 101 `(0,16)`, then north into Oldale
   `(0,10)`.
4. Walk back south across both seams: Oldale -> Route 101 -> Pallet.

The verifier also makes 160 movements across a real Route 101 tall-grass pair
and fails immediately if a battle begins. It therefore checks that the route
is traversable without the vanilla encounter table as well as checking both
seam directions.

## Build and verify

Run the normal build from the repository root:

```sh
export DEVKITARM=/home/eddie/devkitpro/opt/devkitpro/devkitARM
make -j$(nproc) pokeemerald.gba
```

`make` follows ordinary JSON/script timestamps. After changing
`tools/mapjson/mapjson.cpp`, rebuild that tool first with
`make -C tools/mapjson`; because generated-map targets do not depend directly
on the generator binary, also regenerate the affected map explicitly or use
the conservative full-regeneration route (`rm -f .map_version` followed by
the normal build).

Run the authoritative headless mGBA verifier with the local mGBA Python
environment:

```sh
LD_LIBRARY_PATH="$HOME/.venvs/mgba311/lib:$HOME/.venvs/mgba311/lib64" \
  ~/.venvs/mgba311/bin/python plastic_ox/demo/walk_demo.py
```

It boots `pokeemerald.gba`, performs the sequence above, validates live map
state, validates static source/generated encounter invariants, and writes the
`verified_*.png` screenshots under `plastic_ox/demo/shots/`. The final full
`make -j$(nproc) check` run exited successfully with 4,931 passed, 13
known-failing, 595 TODO, and 8 expected-failing cases.

## Source inputs versus generated outputs

Edit the source inputs, not the generated map or encounter headers:

- Map sources: `data/maps/*/map.json`, `data/maps/*/scripts.inc`,
  `data/maps/map_groups.json`, and `data/layouts/layouts.json`.
- Encounter source: `src/data/wild_encounters.json`.
- Generators: `tools/mapjson/mapjson.cpp` and
  `tools/wild_encounters/wild_encounters_to_header.py`.

`mapjson` regenerates map headers, groups, connections, layouts, and constants
from the JSON inputs. The wild-encounter generator regenerates
`src/data/wild_encounters.h` from `src/data/wild_encounters.json`. Do not make
the same logical edit only in generated headers: the next build will replace
it. The verifier intentionally checks both the Route 101 source JSON and the
generated encounter header.

## Implementation summary

### Scene-free route

- Pallet Town, Oak's Lab, Rival's House, and Route 101 had their imported
  coordinate-event/story scenes stripped. Route 101's Birch, starter-bag, and
  Zigzagoon story objects were removed. Pallet no longer intercepts the north
  walk; the Lab and Rival's House are retained as maps with ordinary NPC
  interactions rather than starter/rival scenes.
- Mom remains available in the player's 1F and heals normally.
- Route 101's `MAP_ROUTE101` entry was removed from
  `src/data/wild_encounters.json`, so the generated build has no Route 101
  encounter table. Its remaining NPC scripts are ordinary dialogue.
- New-game code places the player in the Pallet bedroom and skips the truck
  callback. Route 101 no longer relies on story-state variables to remain
  traversable because its imported rescue scene was removed at the source.

### Map and asset integration

- Pallet and its required interiors are valid in the Emerald build; Pallet is
  in the added Plastic Ox map group `(75,0)`. The Pallet/Route 101 offsets are
  reciprocal: Pallet up `+2`, Route 101 down `-2`; Route 101/Oldale remain
  `0` in both directions.
- Required FRLG layouts, tilesets, object graphics, door assets, palettes, and
  scripts are made available to the Emerald build. Layouts preserve their FRLG
  layout format; they are not converted by changing `layout_version`.
- The normal connection margin cannot render a neighbor's metatile IDs when
  the maps use different tilesets. `fieldmap.c` detects incompatible
  `isFrlg`/primary/secondary tileset combinations and fills the camera margin
  from walkable current-map edge blocks and the current layout's phased border
  pattern for blocked terrain instead of copying foreign metatiles. Repeating
  one blocked edge row would stretch partial trees through the margin.

### Cross-primary camera transition fix

On a camera seam transition, `overworld.c` detects a change in `isFrlg` or in
the primary-tileset pointer. For that case it reloads both primary and
secondary tileset graphics through the engine's queued VBlank DMA path, then
reloads map palettes and tileset animations. It also discards the saved source
map view and redraws the destination view. This prevents source-map metatile
data or stale graphics from being reused after the cross-generation transition
without the entirely white frame produced by synchronous forced blank. The
headless verifier checks every frame of both Pallet/Route 101 crossing
directions for that regression.

The destination full redraw is requested in `CameraMove` and consumed after
`AddCameraTileOffset` in the camera update. Drawing before that offset advances
shifts the circular BG view one metatile and makes buildings appear duplicated
as subsequent scrolling replaces rows. `plastic_ox/demo/test_camera_seam.py`
checks both crossing directions, the Pallet forest border and open entrance,
and the maintained scrolling BG buffers against a stationary full redraw.
Run it in the mGBA Python environment; add `--triggers` for the story ROM.

### Route 101 ledge mechanics

Route 101's lower ledge is unchanged from the source Emerald layout. Its
south-jump behavior is on `(9,13)`, with approach `(9,12)` and landing
`(9,14)`. The engine correctly performs a one-way two-tile jump; as part of
the normal animation, the live object coordinate briefly becomes the ledge
coordinate before advancing to the landing coordinate.

The old demo pathfinder assumed every directional input moved exactly one
tile, so that normal midpoint looked like an off-by-one and ledges were treated
as ordinary blocked tiles. The pathfinder now represents matching directional
ledges as directed two-tile edges. The verifier also deliberately jumps the
lower ledge, checks the approach/midpoint/landing sequence, and confirms that
walking north from below remains blocked.

### Reusable stitching workflow

The validated local Codex skill at
`/home/eddie/.codex/skills/poke-map-stitch/` records the reusable workflow:
asset and layout inclusion, reciprocal connection math, story and encounter
neutralization, cross-primary rendering/cache handling, deterministic
regeneration, and bidirectional headless mGBA verification.

## Current limitations

- This is an Emerald-build proof of concept; it does not make the demo's
  all-build Pallet new-game warp safe for a FireRed build.
- Pallet's former south connection to Route 21 remains removed because that
  map group is not valid in this Emerald configuration.
- The player still uses the Emerald Brendan/May avatar assets. This is a
  cosmetic mismatch with the Pallet setting.
- The scene stripping is intentional for this traversal proof of concept;
  Oak's starter sequence, the rival battle, and Birch's rescue are not part of
  the verified flow.

All of these changes are in the working tree. Review `git diff` before any
future commit; no commit is made by this demo documentation.
