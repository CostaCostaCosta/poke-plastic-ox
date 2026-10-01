# FireRed Mt. Moon restoration

## Ancient tablet rewards

The former left/Dome choice now awards **Ancient Ice Tablet**
(`ITEM_ANCIENT_ICE_TABLET`, 885), intended for Regice. The former right/Helix
choice awards **Ancient Rock Tablet** (`ITEM_ANCIENT_ROCK_TABLET`, 886),
intended for Regirock. Both are protected Key Items, use existing plate icons
with ice/rock palettes, and have no field-use action yet. Legendary unlock
events will be implemented later. Miguel still takes the unchosen reward.
The choice objects use item-ball graphics and all local dialogue refers to
tablets. Original fossil script labels and save flags are retained internally
for source-coordinate comparisons and save-state stability; the original
fossil item definitions elsewhere in the game are unchanged.


Rebuilt 2026-09-30. `../mt_moon.py` installs the converted event sources here,
called last by `region_v7.apply_region`. Run it directly to restore only Mt. Moon.
`build_story.py` retains legacy trainer IDs but no longer places the old Rocket
quest in the retired HNS cave. No full-region generated patch was applied:
existing unrelated working changes and regeneration drift were preserved.

## Sources and assets

- Geometry/events: pret/pokefirered revision
  `037335f4c725d7c9aecdac87066f2002b4bd7e14`, maps/layouts `MtMoon_1F`,
  `MtMoon_B1F`, `MtMoon_B2F`. `source_manifest.json` pins binary hashes and
  every warp, actor, and background-event coordinate independently of templates.
- Engine donor: `/home/eddie/repos/pokehns-expansion`, revision
  `44f50eedefe58691b0444973e4138e9190d8fafc`, corresponding `_Frlg` maps.
- Destination: existing `gMapGroup_Dungeons_Frlg` FireRed floors (runtime group 35).
  Exact FireRed map/border binaries already matched; copied/reverified them.
- Retained matched `gTileset_General_Frlg` / `gTileset_Cave_Frlg` graphics,
  palettes, metatiles, converted behaviors, and primary animation. No mismatched
  HNS cave assets were substituted. Layout family remains `frlg` (640 primary
  partition, 32-bit attributes), enabled for Emerald. Graphics are FireRed,
  not a newly drawn or remastered tileset.
- Encounters retain the authored Plastic Ox PU morning/day/night tables in
  `src/data/wild_encounters.json` for all three floor map IDs.

## Routing and interactions

Route 44's existing east mouth `(68,13)` enters original 1F entrance `(18,36)`;
1F warp 3 returns to Route 44. The existing badge gate remains in place.
All fourteen internal directed warps retain their exact FireRed coordinates,
destinations, and indices. B1F warp 7 exits at Route 33's Union Cave doorway
`(27,17)`, landing `(27,18)`; walking back through that door returns to B1F.
Route 33's west passage continues into Goldenrod.

All source trainer/item/sign/hidden-item/fossil coordinates are restored:
seven 1F trainers, four Rocket grunts, Super Nerd Miguel, the excavator,
ten item balls, six B1F hidden mushrooms, two B2F hidden items, the Zubat sign,
and both fossils. Parties, levels, classes, and portraits use the source
`trainers_frlg.party` entries copied into the Emerald table under IDs 914–925.
TM09 and TM46 are converted by move name to Bullet Seed and Thief.
The route-direction dialogue names Goldenrod instead of Cerulean.

Miguel's original `(14,11)` trigger starts his battle. Victory sets
`VAR_POX_MTMOON_STATE=1` and the regional Mt. Moon completion flag. Choosing
one fossil gives the item before removing objects; a full bag leaves the
choice available. Miguel walks to the other fossil, both disappear, and state
becomes 2. On revisits Miguel stays clear of the path and fossils remain hidden.
FRLG quest/world-map flags are not used in the Emerald save. Item flags use
independently audited unused Emerald slots; IDs 0x4E5–0x4EA are now reserved
for Mt. Moon items, so future trainer allocations must not overlap them.
The old HNS map redirects to 1F on its first frame, supporting saves left there.

## Verification

```sh
PATH=/home/eddie/devkitpro/opt/devkitpro/devkitARM/bin:$PATH \
  make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_mt_moon.py
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_route44_transitions.py
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py .
git diff --check
```

Passed: source geometry/event parity, standalone generator idempotence, all 16
floor warp directions plus both outdoor approaches, walkable landings and
post-transition soak, Rocket/Miguel battle starts, both fossil branches,
full-bag failure/retry, prerequisite and duplicate-reward checks, revisit exit,
continuous traversal of both side branches and main path to Goldenrod, and
retired-cave relocation. Battle outcomes are injected into the real battle
finish handler; these tests do not claim to play every combat turn. Continuous
geometry tests mark trainers defeated and fossils chosen as explicit fixtures.
Fresh screenshots in `plastic_ox/demo/shots/moon_*.png` were inspected for
coherent FireRed cave art, fossil clearing, and arrival in Goldenrod.

The global `audit_alpha.py` still reports pre-existing daily-flag allocations,
Devon guard 0x497, and the unallocated `FLAG_POX_KNOWS_BILL_PC` symbol. No new
Mt. Moon allocation errors were reported. Full story regeneration also has
unrelated existing drift; its Mt. Moon floor outputs match the restored files.
