# Import Guide — hns map → Plastic Ox

Source repo: `/home/eddie/repos/pokehns-expansion` (paths below relative to it).
Target: this repo. Never edit generated artifacts (`include/constants/map_groups.h`,
`src/data/wild_encounters.h`, `data/maps/groups.inc`, …) — regenerate by building.

## 0. Per-map checklist

1. `cp -r data/maps/<Name>_hns` → target `data/maps/<Name>_hns/`.
2. In `map.json`: delete `"game_version"` line; replace `"region": "REGION_JOHTO"`
   / `"REGION_KANTO"` with `"REGION_HOENN"`.
3. Connections: keep only endpoints that exist in the target (see REGION_PLAN);
   compute new offsets where a slot's occupant changed.
4. Object events: delete every object whose `graphics_id` starts with
   `OBJ_EVENT_GFX_MON_BASE`, every berry-tree object
   (`trainer_sight_or_berry_tree_id: "BERRY_TREE_*"`), and any object whose script
   references hns-only systems. Keep plain people/sign/item objects but REPOINT
   their `script:` to labels you author in step 7. Replace `_HNS` gfx per §3.
5. Warp events: retarget interiors per the shared-interior table (§5) and REGION_PLAN;
   delete warps to maps that don't exist in the target.
6. Coord events (triggers) from hns: delete all; Plastic Ox adds its own later.
7. `scripts.inc`: REPLACE ENTIRELY with a fresh file containing only the labels your
   map.json references, each with original Plastic Ox dialogue (see DIALOGUE rules).
   Include only standard headers (`#include "constants/flags.h"`,
   `"constants/items.h"`, etc. — copy the include block style from an existing map
   like `data/maps/OldaleTown/scripts.inc`).
8. `bg_events`: keep signs (rewrite text), convert hidden items to
   `FLAG_POX_HIDDEN_*` flags (§2).
9. Add the layout entry to `data/layouts/layouts.json`: copy hns entry, delete
   `game_version`, delete the `layout_version: "hns"` line (defaults to emerald).
   Copy `data/layouts/<Name>_hns/{border.bin,map.bin}` verbatim.
10. Register the map in `data/maps/map_groups.json` under the proper group
    (see §6). Build; fix errors; headless-verify the leg.

## 1. Tileset import recipe (per unique tileset)

1. `cp -r data/tilesets/{primary|secondary}/<dir>` → same path in target.
2. `include/tilesets.h`: add `extern const struct Tileset gTileset_X;`
   (alphabetical near other entries).
3. `src/data/tilesets/headers.h`: add definition following the FRLG-imported
   pattern already present (callback `NULL` unless porting animations).
4. `src/data/tilesets/graphics.h`: add tiles + palettes using the INCGFX idiom:
   ```c
   const u32 gTilesetTiles_X[] = INCGFX_U32("data/tilesets/secondary/x/tiles.png", ".4bpp.fastSmol", "-num_tiles 159 -Wnum_tiles");
   const u16 gTilesetPalettes_X[][16] = {
       INCGFX_U16("data/tilesets/secondary/x/palettes/00.pal", ".gbapal"), ...
   };
   ```
   Match `-num_tiles` to what hns used for that tileset (check its graphics.h line).
5. `src/data/tilesets/metatiles.h`: add `gMetatiles_X` / `gMetatileAttributes_X`
   INCBIN_U16 of `metatiles.bin` / `metatile_attributes.bin`.
6. Animations: alpha SKIPS tileset anim callbacks (water flowers static is fine);
   note skipped anims in commit message.

## 2. Flags & vars namespace

Add `include/constants/plastic_ox_flags.h` (+ include it from
`include/constants/flags.h`) with:

```c
#define FLAG_POX_HIDDEN_...   // item balls/hidden items, one per placement
#define FLAG_POX_HIDE_...     // NPC visibility toggles
#define FLAG_POX_STORY_...    // story beats (one per beat, see STORY_TRIGGERS.md)
```
Vars: 0x4000-0x40FF ONLY — `GetVarPointer` (src/event_data.c) maps any id in
`[VARS_START, SPECIAL_VARS_START)` onto `gSaveBlock1Ptr->vars[id - VARS_START]`
(256 entries), so ids like 0x5100 would read/write past the array and corrupt
the save block. POX vars are allocated from "Unused Var" slots at the top of
that range (`VAR_POX_*` in `include/constants/vars.h`). Badges use native
`FLAG_BADGE0x_GET`.

## 3. Object-event graphics

23 `_HNS` sprites exist (list in /tmp/opencode/recon_hns.md §5). Import ONLY those
actually referenced after object cleanup (likely: OLD_MAN, LASS, YOUNGSTER,
BUG_CATCHER, KIMONO, SILVER, KURT, ITEM_BALL fallbacks…). Recipe per sprite
(mirror how the FRLG sprites were imported):
1. copy `graphics/object_events/pics/**/*_hns.*` + palettes,
2. pic table in `src/data/object_events/object_event_pic_tables.h`,
3. info struct in `object_event_graphics_info.h`,
4. pointer slot + enum value in `include/constants/event_objects.h`
   (`OBJ_EVENT_GFX_<NAME>_HNS`) + `object_event_graphics_info_pointers.h`,
5. INCBIN in `object_event_graphics.h`.
Fallback remap when a sprite is not worth importing: use nearest vanilla
(`OBJ_EVENT_GFX_OLD_MAN`, `GIRL_3`, `BOY_2`, …).

## 4. Music remap (no audio import)

Rewrite `"music"` in imported map.json:

| hns | target |
|---|---|
| MUS_HG_PALLET | MUS_RG_PALLET |
| MUS_HG_ROUTE1 / ROUTE29 / ROUTE30 / ROUTE31 / ROUTE46 | MUS_RG_ROUTE1 |
| MUS_HG_ROUTE3/4/etc (Kanto routes) | MUS_RG_ROUTE3 |
| MUS_HG_CHERRYGROVE | MUS_RG_VIRIDIAN_FOREST |
| MUS_HG_NEW_BARK/TOWN themes | MUS_RG_PALLET |
| MUS_HG_VIOLET/AZALEA/GOLDENROD/ECRU/… city themes | nearest RG city track (MUS_RG_CELADON, MUS_RG_FUCHSIA, MUS_RG_CINNABAR…) |
| MUS_HG_UNION_CAVE / cave themes | MUS_RG_MT_MOON |
| MUS_HG_ROUTE34/35/36/37/38/… | MUS_RG_ROUTE24 |
| MUS_HG_ROUTE40/41/42 water | MUS_RG_SURF? verify exists → else MUS_RG_ROUTE11 |
| MUS_HG_LAVENDER | MUS_RG_LAVENDER |
| MUS_HG_SILPH | MUS_RG_SILPH |
| MUS_HG_VICTORY_ROAD / LEAGUE | MUS_RG_VICTORY_ROAD / MUS_RG_HALL_OF_FAME |
| anything unmapped | MUS_RG_ROUTE1 |

Verify each target symbol exists in `include/constants/songs.h` before use.

## 5. Shared interiors (retarget ALL town doors here)

| Target map (new, group 77) | Copied from hns | Used by |
|---|---|---|
| PokemonCenter_Johto_hns | CherrygroveCity_PokemonCenter_hns | every Johto-style town PC door |
| PokemonCenter_Kanto_hns | PewterCity_PokemonCenter_hns | every Kanto-style town PC door |
| Mart_Johto_hns | CherrygroveCity_Mart_hns | Johto marts |
| Mart_Kanto_hns | PewterCity_Mart_hns | Kanto marts |
| House_GenericA_hns | CherrygroveCity_House1_hns | generic houses A slots |
| House_GenericB_hns | EcruteakCity_House1_hns | generic houses B slots |

Nurse/mart scripts: write minimal fresh scripts (heal via `special HealPlayerParty`;
mart via native `Pokemart` special if trivial, else clerk NPC dialogue-only for
alpha). PC second floor optional — skip.

## 6. Map groups (append to data/maps/map_groups.json)

```
"gMapGroup_PlasticOxJohtoKanto"   // all imported outdoor maps
"gMapGroup_PlasticOxInteriors"    // shared interiors + gyms + gates + facilities
"gMapGroup_PlasticOxDungeons"     // Ilex, DarkCave, MtMoon, Park, BurnedTower, Whirl, IcePath, VictoryRoadKanto, IndigoPlateau exteriors…
```
Append names to `group_order` too. No cap issues until group 256.

## 7. Verification gate per wave

1. `make -j$(nproc) pokeemerald.gba` green.
2. Extend/author `plastic_ox/demo/walk_leg<N>.py` using walklib (`GBA()`,
   `boot_to_bedroom(g)`, `walk(...)`, `expect_map=`, battle-flag poll) walking the
   full leg both directions over seams.

## 8. Known hns porting pitfalls (learned in wave 1C)

1. **Wanderer NPCs hard-crash the ROM.** Any imported NPC with
   `MOVEMENT_TYPE_WANDER_AROUND` / `WANDER_LEFT_AND_RIGHT` / `WANDER_UP_AND_DOWN`
   reboots the game ~120-210 frames after spawning (wild jump through a corrupted
   pointer, landing in the m4a dispatch region). LOOK_AROUND / FACE_* are stable
   after hours-equivalent soak. **Policy:** pin every imported people-NPC to
   `MOVEMENT_TYPE_FACE_DOWN` (or LOOK_AROUND) at import time; only enable stepping
   movement after a headless soak test.
2. **NPCs can sit on single-tile chokepoints.** hns map data sometimes places a
   person on the only walkable tile connecting two areas (e.g. Route30 x=23,y=25),
   making whole regions unreachable. After import, BFS the live ROM grid and move
   any NPC that gates a lane.
3. **Delete cuttable trees on import.** The demo build has no Cut, so they gate
   nothing — and their tiles sit on object spawn-window edges, so they flicker
   active/inactive as the camera moves and destabilize headless pathfinding.
4. **Connection offsets: verify empirically.** Landing tile when crossing a seam
   is `dest_x = src_x - offset` for up/down seams (sign varies by which side
   declares the connection). Don't trust hand-computed targets; print
   `g.describe()` after each crossing in the leg harness.
5. **Some cave-mouth warps land inside solid rock.** DarkCave_SouthSide's R31
   mouth (warp at 14,20) deposits the player at (14,21), a solid tile — identical
   in hns's own data. Cross such seams only in the direction that works, or carve
   the landing tile in our `map.bin` copy.
6. **Elevation semantics for harness BFS:** an object's elevation always becomes
   its current tile's elevation (0 stays 0), and mismatch is rejected only when
   BOTH mover and destination elevations are nonzero and differ. e=0 transition
   tiles make every neighbor elevation legal from them.

