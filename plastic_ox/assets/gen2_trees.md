# Gen 2 fruit and Headbutt trees

The HNS source checkout is `/home/eddie/repos/pokehns-expansion`, revision
`44f50eedefe58691b0444973e4138e9190d8fafc`. Destination maps retain their HNS
layouts and tilesets (640 primary metatiles, 16-bit attributes).

Fixed fruit trees use the existing Gen 2 Apricorn-tree sprite, with berry
scripts instead of Apricorn rewards. No planting is required. Each tree gives
one berry per RTC day; unused daily flags 0x923–0x927 track harvesting without
changing the save structure. The first interaction initializes the daily clock
if an existing save has never set it. A full Bag does not consume the harvest.

| Map | Position | Berry |
| --- | --- | --- |
| Route 29 | 15, 11 | Sitrus |
| Route 46 | 9, 11 | Lum |
| Route 46 | 11, 11 | Liechi |
| Route 44 | 7, 10 | Salac |
| Route 44 | 9, 10 | Petaya |

The first tree on each route restores the donor's fruit-tree location. The
other two occupy open ground. `plastic_ox/alpha/trees.py` installs these events
and is also called by the region generator. Existing events are preserved.
Route 46 had no native Headbutt tiles, so a small Headbutt tree is placed beside
the fruit grove at (13, 11), using its own primary tileset's metatile 0x005.

The imported `MB_HEADBUTT_TREE` attributes had been mapped to `MB_NORMAL`.
Their behavior bytes are restored from the original donor attributes where the
current behavior is normal; other attribute bits and the existing northeast
tileset's waterfall override at 0x22B are preserved. Future imports match the
new behavior by name.
A-button interaction and Bag/registered Headbutt Key use share the same tree
selection, including existing scripted trees. A party Pokemon knowing Headbutt
also permits direct interaction. An empty or fully fainted party cannot start
a battle.

Route 29 and 46 use the documented v4.4 Headbutt populations, with Paras replacing
Pineco according to the later PU requirement that Pineco remain exclusive to
Ilex Forest. Route 44 adds an early Lv. 10–13 tree population. Existing Ilex and
PU tables remain intact. Edit `apply_pu_v1.py` and call `write_special_tables()`
to regenerate the special encounter header without changing grass encounters.

Verification commands:

```sh
make -j$(nproc) TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py /home/eddie/repos/poke-plastic-ox
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_gen2_trees.py
git diff --check
```

The emulator test covers all five fruit trees, declining, map reloads, RTC day
rollover, full-Bag retry, no-key and empty-party use, direct/registered/Bag key
use, learned Headbutt, empty-ground rejection, native Ilex trees, and legacy
scripted trees. Encounter species and levels are checked against the ROM's
linked tables. Screenshots are saved under `plastic_ox/demo/shots/gen2_trees`.
