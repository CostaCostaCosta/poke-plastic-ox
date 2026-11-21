# Plastic Ox Map-Stitch Demo — Handoff (2026-08-22)

## Current state

The working tree contains an Emerald-build proof of concept for this seamless
chain:

```
Pallet Town (75,0) <-> Route 101 (0,16) <-> Oldale Town (0,10)
```

The intended and headlessly verified path is:

**NEW GAME -> Pallet bedroom `(38,1)` at `(6,6)` -> Mom -> Pallet -> Route
101 -> Oldale -> Route 101 -> Pallet.**

`plastic_ox/demo/walk_demo.py` is authoritative. It validates the map IDs and
new-game position, rejects every battle, exercises 160 movements across a real
Route 101 tall-grass pair, checks every seam direction for an all-white
forced-blank frame, verifies Route 101's lower ledge as a one-way two-tile
jump, and takes
`shots/verified_01_bedroom.png` through `shots/verified_09_pallet_return.png`.
The visual output for shots 05–09 is correct.

The demo changes are **not committed**. Do not commit unless explicitly asked.
Inspect the complete work with `git status --short` and `git diff`.

## Rebuild and rerun

From `/home/eddie/repos/poke-plastic-ox`:

```sh
export DEVKITARM=/home/eddie/devkitpro/opt/devkitpro/devkitARM
make -j$(nproc) pokeemerald.gba

LD_LIBRARY_PATH="$HOME/.venvs/mgba311/lib:$HOME/.venvs/mgba311/lib64" \
  ~/.venvs/mgba311/bin/python plastic_ox/demo/walk_demo.py
```

The normal build follows JSON/script timestamps. After changing
`tools/mapjson/mapjson.cpp`, first run `make -C tools/mapjson`; then explicitly
regenerate the affected map or force a conservative full regeneration by
removing `.map_version` before the normal build. The build, headless run, and
`make -j$(nproc) check` are the recorded checks for this handoff. The full test
suite exited successfully with 4,931 passed, 13 known-failing, 595 TODO, and 8
expected-failing cases.

## What changed

- **Start and scenes:** New Game starts directly in the Pallet bedroom; the
  Emerald truck callback is bypassed. Pallet, Oak's Lab, Rival's House, and
  Route 101 are stripped of imported coordinate-event/story scenes; Route
  101's Birch, starter-bag, and Zigzagoon story objects are removed too. Mom
  still heals. Oak's interception/starter sequence, the rival battle, and
  Birch's rescue are deliberately absent from the demo flow.
- **Encounters:** the `MAP_ROUTE101` entry was removed from the source file
  `src/data/wild_encounters.json`. Route 101 therefore has no generated
  encounter table. The verifier checks both the source JSON and
  `src/data/wild_encounters.h` and walks in tall grass while rejecting battles.
- **Maps:** Pallet is in Plastic Ox group `(75,0)` and connects north to Route
  101 with offset `+2`; the reciprocal Route 101 south connection is `-2`.
  Route 101/Oldale keep their `0` offsets. The former Pallet south connection
  to Route 21 stays removed.
- **Assets/build:** the necessary FRLG layouts, tilesets, object graphics,
  palettes, door assets, and scripts are available in the Emerald build.
- **Camera transitions:** a cross-primary transition detects `isFrlg` or
  primary-tileset-pointer changes. It avoids foreign-metatile camera margins,
  queues both graphics sets through the normal VBlank DMA path, reloads all
  palettes/animations, discards the source saved view, and redraws the
  destination. The former direct-to-VRAM forced-blank path caused one entirely
  white frame and was removed.
- **Ledges:** the Route 101 map and Emerald ledge engine were already correct.
  The apparent off-by-one was in the demo pathfinder, which modeled every
  directional input as one tile. It now treats a directional ledge as a
  two-tile edge and separately verifies `(9,12) -> (9,14)` across the
  south-jump ledge at `(9,13)`, including its normal midpoint coordinate and
  one-way collision.
- **Reusable workflow:** the validated local Codex skill at
  `/home/eddie/.codex/skills/poke-map-stitch/` captures the asset/layout,
  connection, story/encounter, cross-primary cache, regeneration, and
  bidirectional headless-verification checklist used by this demo.

## Editing rule: source data, then regenerate

Map JSON/scripts, `data/maps/map_groups.json`, and `data/layouts/layouts.json`
are the sources for `mapjson`. `src/data/wild_encounters.json` is the source
for the wild-encounter generator. The map headers/groups/connections/layout
outputs and `src/data/wild_encounters.h` are generated artifacts; do not use a
generated header as the sole location of a change. Build after source edits,
and use the explicit/full regeneration route above when the generator itself
changes.

## Boundaries and limitations

- Emerald is the supported proof-of-concept build; this new-game warp is not
  safe as a FireRed demo build.
- Pallet is a south-side dead end until Route 21 or another connection is made
  valid in Emerald.
- The Emerald player avatar remains Brendan/May; that is cosmetic only.
- This handoff deliberately makes no claim about broader gameplay, story, or
  platform coverage beyond the build and headless round-trip verification.
