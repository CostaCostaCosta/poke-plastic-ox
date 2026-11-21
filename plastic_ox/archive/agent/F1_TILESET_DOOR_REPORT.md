# F1 — tileset door attributes (Ilex north exit, Dark Cave mouths)

Scope: `ilex_forest_hns` and `cave_default_hns` `metatile_attributes.bin` only.
No maps, scripts, metatiles, or other agents' files touched. No build run.

## Files and sizes

| File | Before | After | Entries | Metatiles | Headroom |
| --- | --- | --- | --- | --- | --- |
| `data/tilesets/secondary/ilex_forest_hns/metatile_attributes.bin` | 118 B | 120 B | 60 | 60 | 0 (exact) |
| `data/tilesets/secondary/cave_default_hns/metatile_attributes.bin` | 612 B | 616 B | 308 | 308 | 0 (exact) |

md5 before/after: `342a800d…` → `a5d7a9c0…` (Ilex), `2af8cc72…` → `d84bab15…` (cave).

## Values written

| Tileset | Index | u16 written | Behavior | Layer |
| --- | --- | --- | --- | --- |
| ilex_forest_hns | 59 (0x3B) | `0x0064` | `MB_NORTH_ARROW_WARP` | 0 |
| cave_default_hns | 306 | `0x0065` | `MB_SOUTH_ARROW_WARP` | 0 |
| cave_default_hns | 307 | `0x0065` | `MB_SOUTH_ARROW_WARP` | 0 |

Format: one little-endian u16 per metatile, bits 0–7 behavior, bits 12–15 layer
type (`include/global.fieldmap.h:39-42`); hns layouts hold 640 primary metatiles,
so secondary index = `(block & 0x3FF) - 640`. Layer 0 was kept because the
attribute of the source metatile art is `0x0008` (layer 0) in both tilesets.

## Evidence

**Ilex 59** — `fix_ilex_north_gate.py` cloned local `0x1C` (28) art into slot 59;
donor `IlexForest_hns (20,15)` is `0x329C` = secondary 28 with attribute
`0x0008` (plain `MB_CAVE`, layer 0), so the donor offers no door behaviour for
this cell (its authored north exit is at `(19,13)/(20,13)`, primary 401,
`MB_NON_ANIMATED_DOOR`, no warp event in our map). Chosen from the walk
direction: the player crosses `(20,15)` heading north, and the map's working
south threshold (primary 312) is a direction-matching arrow warp
(`MB_EAST_ARROW_WARP`, 0x1062) — this map's thresholds are arrow warps along the
walked lane. Vanilla forest-north-threshold precedent: `PetalburgWoods (14,5)`
and `(15,5)` = `MB_NORTH_ARROW_WARP`. Returning from
`Route2_ViridianForest_NorthEntrance` lands the player on `(20,15)` holding
south, which does not match, so no bounce-back.

**Cave 306/307** — both appended metatiles are byte-identical to the cave-mouth
art at indices 1/7/89/136/139/194. The donor's own mouth cells are secondary 7:
donor `DarkCave_SouthSide_hns (14,20)` is `0x3287` (=7) with attribute `0x0065`,
and donor `(56,47)` is also `0x3287`; our still-untouched cell `(56,47)` likewise
reads `0x0065`. FRLG cave mouths agree: `MtMoon_1F_Frlg (18,37)`,
`VictoryRoad_1F_Frlg (11,20)`, `ThreeIsland_DunsparceTunnel_Frlg (3,4)` are all
`MB_SOUTH_ARROW_WARP`, and `Route4 (19,5)` warps the arriving player onto
`MtMoon_1F` warp 3, i.e. onto that arrow tile — the same arrive-on-the-arrow
pattern used here. Geometry fixes the direction: inside the cave both mouths are
approached walking south (`(14,19)` walkable / `(14,21)` solid; `(56,45)`
walkable / `(56,48)` solid).

## Padding convention

Peer hns tilesets ship exactly 2 bytes per metatile: 46 of 51 secondary dirs and
7 of 7 primary dirs. Only `lavaridge_hns` and `lavender_town_hns` are padded to
2048 B (the `HANDOFF_WAVE4.md` step), and three files were short — the bug
pattern, including these two. Files are therefore exact-sized, which also
satisfies the engine (`INCBIN_U16`; no fixed-size reader).

## Read-back (script run against the written files)

```
=== raw entry read-back (changed indices) ===
data/tilesets/secondary/ilex_forest_hns: 60 entries / 60 metatiles -> OK
  [ 59] 0x0064  MB_NORTH_ARROW_WARP(0x64) layer=0
data/tilesets/secondary/cave_default_hns: 308 entries / 308 metatiles -> OK
  [306] 0x0065  MB_SOUTH_ARROW_WARP(0x65) layer=0
  [307] 0x0065  MB_SOUTH_ARROW_WARP(0x65) layer=0
=== end-to-end: warp tile -> block -> tileset index -> behavior ===
IlexForest_hns  layout=LAYOUT_ILEX_FOREST_HNS (82x73) secondary=gTileset_IlexForest_Hns
  warp 0 (22,63) elev=0 -> MAP_ROUTE2_VIRIDIAN_FOREST_SOUTH_ENTRANCE warp 3
      block=0x3138 mt=312 primary#312 collision=0 elevation=3
      attribute=0x1062 behaviour=MB_EAST_ARROW_WARP(0x62) layer=1
  warp 1 (20,15) elev=0 -> MAP_ROUTE2_VIRIDIAN_FOREST_NORTH_ENTRANCE warp 1
      block=0x32BB mt=699 secondary#59 collision=0 elevation=3
      attribute=0x0064 behaviour=MB_NORTH_ARROW_WARP(0x64) layer=0
DarkCave_SouthSide_hns  layout=LAYOUT_DARK_CAVE_SOUTH_SIDE_HNS (78x50) secondary=gTileset_Cave_Default_Hns
  warp 0 (14,20) elev=0 -> MAP_ROUTE2 warp 3
      block=0x33B2 mt=946 secondary#306 collision=0 elevation=3
      attribute=0x0065 behaviour=MB_SOUTH_ARROW_WARP(0x65) layer=0
  warp 1 (56,46) elev=0 -> MAP_ROUTE46_HNS warp 2
      block=0x33B3 mt=947 secondary#307 collision=0 elevation=3
      attribute=0x0065 behaviour=MB_SOUTH_ARROW_WARP(0x65) layer=0
```

Warp events carry elevation 0 (`ELEVATION_TRANSITION`), so the ground elevation
3 on these tiles does not block `GetWarpEventAtPosition`.

Collateral: 306/307 are used only at the two Dark Cave mouths and 59 only at
`IlexForest_hns (20,15)`; the other maps that share `gTileset_Cave_Default_Hns`
never reference the appended ids, so no other map's behavior changes.

## Static checks

- `python3 -m json.tool` on `IlexForest_hns/map.json`, `DarkCave_SouthSide_hns/map.json`: valid (neither edited).
- `plastic_ox/agent/check_map_refs.py --pox`: 118 maps, **1 pre-existing error** — `Route38_hns warp 0 (43,16)` points at a non-existent gate warp id (out of scope; the seven `PlasticOx_BerryTree_*` errors from BRIEF.md are already gone).
- `plastic_ox/story/check_story_notes.py --quiet`: 61 notes, 0 errors, 0 warnings.
- baseline audit: `IlexForest_hns` only `MAP_SCRIPT_ON_TRANSITION` (`PoxRegion_Arrival_IlexForest_hns`), `DarkCave_SouthSide_hns` "no automatic triggers" — unchanged; no map edits made.
- `git diff --stat` for my paths: only the two `.bin` files (bin 118→120, 612→616).

## Emulator tests for the integration pass

1. **Ilex south→north.** Enter Ilex from the south gatehouse, walk the road north to `(20,16)`, hold UP onto `(20,15)`: expect a fade to `MAP_ROUTE2_VIRIDIAN_FOREST_NORTH_ENTRANCE` (warp 1). Then leave that gatehouse southbound and confirm the player lands on `(20,15)` and walks away south instead of bouncing straight back north.
2. **Route 46 → Dark Cave → Route 2.** `Route46_hns (20,11)` → cave `(56,46)`; walk north through the cave to `(14,20)`: expect a warp to `MAP_ROUTE2` warp 3 (lands `(17,11)`). Step north onto `(17,11)` to re-enter, confirm no immediate return warp, then walk to `(56,46)` and hold DOWN: expect a warp to `MAP_ROUTE46_HNS` warp 2 (`(20,11)`).
3. **Corner case.** While in the cave, try to walk past `(56,46)` south — the tile must warp before `(56,47)` is reached. If the player ever stands on `(56,47)`, the warp coordinate is off by one row (donor authored the mouth at `(56,47)`); that is a `map.json` change outside F1.
4. Flag state: none required — all four doors are flag-independent. Verify with `FLAG_POX_TRIGGERS_ENABLED` both set and clear.

## Not done / for others

- `DarkCave_SouthSide_hns` warp 1 sits at `(56,46)` while the donor's authored mouth tile is `(56,47)` (which still carries `MB_SOUTH_ARROW_WARP`). Behavior now covers `(56,46)`, so test 3 matters; moving the warp event is `map.json`, outside F1.
- `IlexForest_hns` warp 1 sits on the threshold `(20,15)`; the donor's gate doors `(19,13)/(20,13)` (primary 401, `MB_NON_ANIMATED_DOOR`) still have no warp event. Left unchanged (map scope).
- `house_lab_hns/metatile_attributes.bin` is also short (432 B for 434 metatiles) — same class of bug, not in F1 scope.
- `.orig` backups for both tilesets were left untouched so `remap_metatile_behaviors.py` stays idempotent.
