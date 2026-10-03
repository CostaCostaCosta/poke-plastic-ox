# ROM space trim audit + Safari Zone → National Park rewiring plan

**Date:** 2026-10-02
**Status:** ⚠ **SUPERSEDED IN PART.** One cut from this audit has been executed on user
approval (the FRLG Safari Zone family, §7); every other cut is POSTPONED by the user.
See the **Decision log** below before reading anything else in this document.
**Scope of the original audit:** audit only. No build, no source edits, no
map_groups.json changes were made for it.
**Measured against:** `pokeemerald.gba` / `.elf` / `.map`, all dated 2026-10-02 08:54
(`rom_sha256` of the deployed build is recorded in `warp_playtest_v1_unblocked.json`).
**Companion notes:** `plastic_ox/battle/metamon/ROM_SPACE_AUDIT.md` (metamon model sizing),
`plastic_ox/agent/WARP_PLAYTEST_V1_REPORT.md` (warp closure + the "facility state machine"
UNTESTED reason this audit has to resolve), `plastic_ox/agent/ROM_SPACE_MEASURE.py` (the
re-runnable measurement harness described in §9).

---

# 🛑 DECISION LOG

## D1 — FRLG Safari Zone family (audit §7, families A + B) — **REMOVED, user-approved 2026-10-02**

**Decision:** remove the Kanto (FRLG) Safari Zone **entirely** — all 11 maps — on explicit
user approval. The user directed that this family be cut in full rather than partially.

**Executed.** Result:

| metric | before | after | delta |
|---|--:|--:|--:|
| `pokeemerald.gba` sha256 | `21cfd4a224d40e129c7ed5a3eef14a1d93f15ec47eff4118d2d9633da05eb9b5` | `c1fb0b62922ac24e028c3ca59cf103d38a71b0d3bd3592eb87c3ed975e7ba2e9` | — |
| last non-`0xFF` byte | 28,301,300 (`0x01AFD7F4`) | 28,273,228 | **−28,072 B (−27.4 KiB)** |
| free tail | 5,253,132 B | 5,281,204 B | **+28,072 B** |
| maps in the warp closure | 417 | **406** | −11 |
| warp events in the closure | 1,278 | 1,211 | −67 |

The audit predicted **27,644 B** (§7.5); the build delivered **28,072 B**.

**What was removed (11 maps):**

| map | group | layout |
|---|---|---|
| `SafariZone_Center_Frlg` | `gMapGroup_Dungeons_Frlg` | `SafariZone_Center_Layout` |
| `SafariZone_East_Frlg` | `gMapGroup_Dungeons_Frlg` | `SafariZone_East_Layout` |
| `SafariZone_North_Frlg` | `gMapGroup_Dungeons_Frlg` | `SafariZone_North_FRLG_Layout` |
| `SafariZone_West_Frlg` | `gMapGroup_Dungeons_Frlg` | `SafariZone_West_Layout` |
| `SafariZone_Center_RestHouse_Frlg` | `gMapGroup_Dungeons_Frlg` | `SafariZone_RestHouse_FRLG_Layout` |
| `SafariZone_East_RestHouse_Frlg` | `gMapGroup_Dungeons_Frlg` | `SafariZone_RestHouse_FRLG_Layout` |
| `SafariZone_North_RestHouse_Frlg` | `gMapGroup_Dungeons_Frlg` | `SafariZone_RestHouse_FRLG_Layout` |
| `SafariZone_West_RestHouse_Frlg` | `gMapGroup_Dungeons_Frlg` | `SafariZone_RestHouse_FRLG_Layout` |
| `SafariZone_SecretHouse_Frlg` | `gMapGroup_Dungeons_Frlg` | `SafariZone_SecretHouse_Layout` |
| `FuchsiaCity_SafariZone_Entrance_Frlg` | `gMapGroup_IndoorFuchsia_Frlg` | `FuchsiaCity_SafariZone_Entrance_Layout` |
| `FuchsiaCity_SafariZone_Office_Frlg` | `gMapGroup_IndoorFuchsia_Frlg` | `FuchsiaCity_SafariZone_Office_Layout` |

**Files touched** (following the §7.4 cleanup order):

1. `data/maps/FuchsiaCity_Frlg/map.json` — dropped the two `warp_events` that pointed at
   `MAP_FUCHSIA_CITY_SAFARI_ZONE_{ENTRANCE,OFFICE}` (audit step 8) and **remapped 20 inbound
   `dest_warp_id`s** across 7 Fuchsia interiors
   (old→new: `1→0, 2→1, 4→2, 5→3, 6→4, 7→5, 8→6, 9→7, 10→8`). ⚠ This renumbering is
   **not** in the audit's dependency list; see "New finding" below.
2. `data/maps/map_groups.json` — 11 entries removed.
3. `data/layouts/layouts.json` — 8 layout entries removed (the 4 rest houses share one).
4. `data/maps/{SafariZone_*_Frlg,FuchsiaCity_SafariZone_*_Frlg}/` and
   `data/layouts/{SafariZone_{Center,East,North,West,RestHouse,SecretHouse}_Frlg,FuchsiaCity_SafariZone_{Entrance,Office}_Frlg}/`
   deleted.
5. `data/scripts/plastic_ox_kanto_maps.inc` — 11 live `.include`s removed.
6. `data/event_scripts.s` — the 11 already-dead `.if IS_FRLG` `.include`s removed as well,
   so no dangling include survives.
7. `data/scripts/safari_zone.inc` — the dead `#if IS_FRLG` arms of
   `SafariZone_EventScript_OutOfBallsMidBattle` / `_Exit` removed; the Hoenn arm is now
   unconditional. This retires the `MAP_FUCHSIA_CITY_SAFARI_ZONE_ENTRANCE` target from
   §7.4 step 4. The Pokéblock section is untouched (audit step 14).
8. `data/scripts/item_ball_scripts_frlg.inc` — 13 orphan `SafariZone_*_EventScript_Item*`
   labels removed.
9. `data/scripts/fame_checker_frlg.inc` — orphan
   `SafariZone_North_RestHouse_EventScript_BaldingMan` removed.
10. `tools/mapjson/required_map_defines.json` — 11 `MAP_*` defines dropped.
11. `src/data/wild_encounters.json` — the 8 dead `#ifdef FIRERED`/`LEAFGREEN` Kanto safari
    tables removed (0 slots were ever linked, so this is source hygiene only).
12. `src/data/tilesets/plastic_ox_kanto_additions.h` — `gTileset_SafariZoneBuilding` plus its
    4 graphics symbols deleted from the **live** `#if !IS_FRLG` path. This is the §3.2
    lesson in action: `--gc-sections` cannot drop it out of LTO's merged `.rodata` blob, so
    the definitions themselves had to go. The mirrored dead copies inside the `#if IS_FRLG`
    blocks of `src/data/tilesets/{graphics,metatiles,headers}.h` were removed too, and
    `data/tilesets/secondary/safari_zone_building_frlg/` was deleted.
13. **Warden preservation (audit step 10):** the `ITEM_GOLD_TEETH` ball was **relocated**,
    not retired — it now sits at `(9,7)` in `FuchsiaCity_WardensHouse_Frlg` under the
    unchanged `FLAG_HIDE_SAFARI_ZONE_WEST_GOLD_TEETH`, driven by a new
    `FuchsiaCity_WardensHouse_EventScript_ItemGoldTeeth`. The tile was validated as
    `collision 0 / elevation 3 / MB_NORMAL` via `plastic_ox/alpha/region_geometry.py`.
    The Warden's HM04 (STRENGTH) exchange therefore still works. (HM04 was never
    load-bearing anyway: `data/scripts/plastic_ox_story.inc:492-496` also grants it from the
    Plastic Ox mansion key.)
14. `data/layouts/layouts.json` — `FourIsland_LoreleisHouse_Layout` named
    `gTileset_SafariZoneBuilding` as its secondary tileset. That Sevii layout is
    FRLG-gated and never emitted, so nothing broke, but step 12 left the reference
    dangling; its secondary was retargeted to `gTileset_BuildingFrlg` (its own primary).
    Confirmed a no-op for the ROM — the rebuild after this edit reproduces `c1fb0b62`
    byte-for-byte.

**Deliberately NOT done** (outside the approved scope):

* `data/scripts/safari_zone.inc`'s Pokéblock section, `src/safari_zone.c`,
  `gNumSafariBalls`, `gSafariZoneStepCounter`, `SafariZoneTakeStep`, `CB2_EndSafariBattle`,
  `ITEM_SAFARI_BALL`, `gObjectEventPic_SafariBall`, `src/pokeblock.c`,
  `src/plastic_ox_contest.c` — audit §7.4 step 14, untouched.
* The Hoenn Safari Zone (7 maps + `Route121_SafariZoneEntrance`) — kept.
* `MAPSEC_KANTO_SAFARI_ZONE` (`include/constants/region_map_sections.h:145`) is now unused by
  any map, but it is still referenced by `src/region_map.c:482`, `src/map_preview_screen.c:131`
  and the generated `src/data/region_map/*`. Removing it would renumber every later MAPSEC —
  a save-file surface — so it was left alone. §7.4 step 11 (flag reclamation) was likewise
  skipped for the same reason: the `FLAG_HIDE_SAFARI_ZONE_*` names stay as they are.
* `graphics/map_preview/safari_zone/` (14,718 B on disk, 0 B linked) — §7.4 step 13, left.
* `FuchsiaCity_Frlg`'s "POKéMON PARADISE / SAFARI ZONE" sign at `(26,18)` and
  `FuchsiaCity_Text_SafariZoneZooInFront` still exist and now describe nothing. Cosmetic
  follow-up, not a break.

### New finding: 26 surviving maps got new `(mapGroup, mapNum)` ids

Expected, and exactly what §2.4 predicted — recorded here because it is a live
save-file compatibility surface. Dropping the 11 entries from `map_groups.json`
shifts every later entry in the same group, and group indices are positional:

| group | what was removed | maps renumbered |
|---|---|--:|
| `gMapGroup_Dungeons_Frlg` (35) | the 9 `SafariZone_*_Frlg` | 18 |
| `gMapGroup_IndoorFuchsia_Frlg` (45) | `FuchsiaCity_SafariZone_{Entrance,Office}_Frlg` | 8 |

Full list: `CeruleanCave_{1F,2F,B1F}_Frlg`, `RockTunnel_{1F,B1F}_Frlg`,
`SeafoamIslands_{1F,B1F,2F,B3F,4F}_Frlg`, `PokemonTower_{1..7}F_Frlg`,
`PowerPlant_Frlg` (group 35); `FuchsiaCity_{Gym,House1,House2,House3,Mart,
PokemonCenter_1F,PokemonCenter_2F,WardensHouse}_Frlg` (group 45).

**Any save file written by `21cfd4a2` or earlier is invalid for these 26 maps** and
for the whole region graph after it. The 11 removed maps are simply unreachable.
This is unavoidable for a de-opt and is the reason §8 step 15 (the 186-map hygiene
de-opt) is explicitly "do last, or skip".

### New finding: removing a `warp_def` renumbers every later `dest_warp_id`

§2.4 warns about `MAP_*` renumbering but says nothing about **warp-id** renumbering inside a
surviving map. Removing the two `warp_events` from `FuchsiaCity_Frlg` shifted every later
warp in that map down by 0–2, and 7 interiors store those indices as `dest_warp_id`.
Nothing in the C/asm build catches this: the `warp_def … MAP_FUCHSIA_CITY_HOUSE3` row still
assembles cleanly and silently warps the player to the wrong tile. The static pre-pass
(`python3 plastic_ox/demo/test_warps_v1.py --static-only`) found it in seconds
(`FuchsiaCity_House3_Frlg 0 … dest_warp_id 10 out of range (target has 9)`). Run it after
**any** `warp_def` deletion. This is the biggest gap in §7.4's dependency list.

## D2 — every other cut in this audit — **POSTPONED by the user, 2026-10-02**

**Decision:** the user reviewed this audit and **postponed all remaining cuts** until they
are actually necessary and after additional testing. Specifically **do not** remove,
de-opt, or `NULL` any of:

* Battle Frontier (47 Hoenn maps + ~343 KB of feature code) — §3 row D, §6.1, §8 step 2
* Secret Base (24 maps) — §3 row J, §6.2, §8 step 6
* Contest halls / Elite Four halls (22 maps) and the contest/bard code — §3 row H, §6.3, §8 steps 5, 8
* Link / union / trade / record facilities (8 maps) — §3 row G, §6.5, §8 step 9
* Battle Tents (9 maps) — §3 row I, §6.4, §8 step 7
* Artisan Cave (2 maps) — §3 row F, §6.7
* Trainer Tower / Trainer Hill de-opt (`TrainerTower_*_Frlg`, `src/trainer_hill.c`) — §3 row E, §6.6, §8 step 12
* The 42 emitted-but-unreferenced layouts (55,482 B) — §3.1b, §8 step 1
* Feature-code cuts: trainer slide banners (~364 KB), bard sound templates (~241 KB),
  minigames (~162 KB), recorded battle, `src/safari_zone.c` — §4, §8 steps 4, 5, 13, 14
* The 15 dead-but-linked tilesets (177,100 B) — §3.2, §8 step 11
* The 186 `layout_version: "frlg"` de-opt hygiene pass — §2.2, §8 step 15
* The Hoenn Safari Zone — §8 step 10

**How to read the rest of this document now:** §1–§6 and §8 are a **reference list of
candidate levers with measured costs and dependency notes**, not a to-do list. §7 is
historical: families A + B are executed (see D1); the National Park rewiring steps 1–7 and
10–13 of §7.4 are **not** approved and **not** scheduled. The §7.0 bug where
`PlasticOxContest_TakeStep()` runs before the safari countdown in `SafariZoneTakeStep()` is
still live and still unfixed — it is no longer reachable from the removed maps, but the two
functions still share the step counter wherever the National Park is used.

---

## 0. Executive summary

| Question | Answer |
|---|---|
| What is actually in the ROM today? | 28,301,300 B used of 33,554,432 B; **5,253,132 B (5.01 MB) free tail**. `maps.o` = 1,204,664 B, `map_events.o` = 162,796 B, `event_scripts.o` script_data = 1,329,486 B. |
| How many maps are opted in? | 1,037 entries in `data/maps/map_groups.json`, but **only 851 actually compile**. 186 are `layout_version: "frlg"` and are silently NULLed out of `gMapLayouts`. |
| Biggest single win | **Battle Frontier**, 47 maps: 305,782 B of map data + ~343 KB of feature code/tables = **~630 KB**. |
| Next biggest | Trainer slide banners (~364 KB code+data), Contest halls + bard music (46,736 B map + ~275 KB code/data), Link facilities (39,693 B), Battle Tents (27,581 B), Secret Base (33,212 B). |
| Best risk/reward | **Prune the 42 emitted-but-unreferenced layouts** (§3.1b) — **55,482 B with zero map, script, tileset or code references.** Nothing else comes close. |
| Tilesets are *not* the lever | 208 tilesets declared, **177 live, 31 dead**, but only 177,100 B of dead tileset bytes are linked. LTO merges `src/tilesets.o` into one 1.93 MB `.rodata` blob, so `--gc-sections` cannot drop them — you must delete the `const struct Tileset` block. Tilesets also free themselves automatically once their maps leave `map_groups.json` (cascade simulated per family, §3). |
| Trainer Hill / FRLG `TrainerTower_*` | **Already costs 0 bytes.** All 12 maps fail the `layout_version` gate and never compile. `src/trainer_hill.c` (~45 KB) is live but unreachable. |
| FRLG Safari Zone → National Park | The mechanic engine is the **Emerald-native** `src/safari_zone.c` and is **map-agnostic** (no hard-coded Hoenn map ids). The 9 FRLG `SafariZone_*_Frlg` interiors are plain field maps with **zero encounters in the ROM** (their tables sit behind `#ifdef FIRERED`). They can be dropped. Full plan in §7. |
| 🔴 Two live bugs found | `IS_FRLG == 0` in this build, so the Safari exit scripts take the **Hoenn** branch and warp the player to `MAP_ROUTE121_SAFARI_ZONE_ENTRANCE` — a map outside the warp closure. And `PlasticOxContest_TakeStep()` runs **before** the safari countdown in `SafariZoneTakeStep()`, so a park contest and a park safari session would fight over the same step counter. |
| Headline trap | `PlasticOxContest` (`src/plastic_ox_contest.c`) **reuses `gNumSafariBalls` / `gSafariZoneStepCounter` and is hard-scoped to `MAP_NATIONAL_PARK_NORMAL_HNS`**. Any Safari Zone removal must preserve that path. |

---

## 1. Baseline ROM state

Measured exactly, not estimated.

### 1.1 Post-cut state (`c1fb0b62`, current — supersedes the table below)

| Metric | Value |
|---|--:|
| `pokeemerald.gba` sha256 | `c1fb0b62922ac24e028c3ca59cf103d38a71b0d3bd3592eb87c3ed975e7ba2e9` |
| Last non-`0xFF` byte | 28,273,228 B (26.97 MB) |
| **Free tail** | **5,281,204 B (5.04 MB)** |
| `.text` | 2,388,536 B |
| `.rodata` | 23,935,252 B |
| `data/maps.o` `.rodata` | 1,187,296 B |
| `data/map_events.o` `.rodata` | 161,060 B |
| `data/event_scripts.o` `script_data` | 1,324,846 B |
| warp closure | 406 maps / 1,211 warps / 86 connections |

### 1.2 Pre-cut state (`21cfd4a2`, the audit's original measurement)

| Metric | Value |
|---|--:|
| Cart size | 33,554,432 B (0x02000000) |
| Last non-`0xFF` byte in `pokeemerald.gba` | `0x01AFD7F4` = 28,301,300 B (26.99 MB) |
| **Free tail** | **5,253,132 B (5.01 MB), pure `0xFF` padding** |
| `.text` | `0x247240` = 2,388,032 B |
| `.rodata` | `0x16D9494` = 24,013,460 B |
| `data/maps.o` `.rodata` (blockdata + borders + headers + connections + group tables) | 1,204,664 B |
| `data/map_events.o` `.rodata` (NPCs, warps, coord events, bg events) | 162,796 B |
| `data/event_scripts.o` `script_data` (all field + battle scripts) | 1,329,486 B |
| `src/data/wild_encounters.h` source | 887,705 B |

This supersedes the 5.66 MB figure in `ROM_SPACE_AUDIT.md` §1, which was taken on an older build
(2026-09-25, `5b21ca882b`). The current build is ~0.65 MB fuller but the ordering of the levers is
unchanged.

---

## 2. What is actually opted in, and what actually compiles

### 2.1 `map_groups.json` = 1,037 maps across 81 groups

The opt-in table is the single gate for map-side ROM content. Three additional gates apply
afterwards, and they matter a lot:

1. **`map_groups.json`** — is the map emitted into `data/maps/{name}/header.inc` /
   `events.inc` / `scripts.inc` and therefore into `data/maps/groups.inc` + `data/maps/headers.inc`?
2. **`MAP_VERSION`** — `Makefile:5` sets `MAP_VERSION ?= emerald`. `tools/mapjson/mapjson.cpp:876-881`
   compares each layout's `layout_version` against it and emits `.4byte NULL` on mismatch. A layout
   with `"layout_version": "frlg"` is therefore **never emitted** in `data/layouts/layouts.inc`, its
   `data/layouts/<name>/map.bin` is never `.incbin`'d, and its map header/events are never emitted.
3. **`--gc-sections`** (`Makefile:595`, `Makefile:603`) — anything not referenced by a live
   `gTileset*`, script label, or event is dropped by the linker. This is why dead tilesets and
   unreferenced encounter tables cost 0 B.

### 2.2 The 186 opted-in maps that cost nothing

All 186 have `layout_version: "frlg"` and are NULLed. They are pure source-tree weight.

| Group | Count | Examples |
|---|--:|---|
| `gMapGroup_SpecialArea_Frlg` (Trainer Tower) | 12 | `TrainerTower_1F_Frlg` … `TrainerTower_Elevator_Frlg` |
| `gMapGroup_Dungeons_Frlg` (post-game) | ~50 | `NavelRock_*`, `MtEmber_*`, `FiveIsland_LostCave_*`, `SixIsland_DottedHole_*`, `TanobyRuins_*` |
| `gMapGroup_TownsAndRoutes_Frlg` (Sevii / Viridian) | ~60 | `OneIsland_*`, `TwoIsland_*`, `SevenIsland_*`, `ViridianCity_Frlg`, `Route20/22/23_Frlg` |
| `gMapGroup_Link_Frlg` | 2 | `BattleColosseum_2P_Frlg`, `BattleColosseum_4P_Frlg` |
| `gMapGroup_Dungeons_Frlg` | 1 | `PokemonLeague_HallOfFame_Frlg` |
| misc | ~61 | `RecordCorner_Frlg`, `ViridianForest_Frlg`, `VictoryRoad_*`, `IndigoPlateau_*`, `BirthIsland_*` |

**Recommendation:** de-opt them from `map_groups.json` as pure hygiene (see §8, step 0). They free
**0 bytes**, so do this last or not at all — but they are the reason a naive "count the maps"
estimate is 20% wrong.

### 2.3 Layout accounting

| Metric | Value |
|---|--:|
| Layouts in `data/layouts/layouts.json` | 866 (**was 874**, −8 for the FRLG Safari Zone) |
| Layouts emitted into `data/layouts/layouts.inc` | 685 (**was 693**) |
| Layouts NULLed in `gMapLayouts` | 180 (**was 181**) |
| `gMapLayouts` table entries (`layouts_table.inc`) | 686 (**was 694**) |
| Unique `map.bin` + `border.bin` files `.incbin`'d | 1,372 (**was 1,388**) |
| Total linked blockdata + border bytes | 1,132,826 B (**was 1,149,548 B**, −16,722) |
| Opted-in maps with a resolvable emitted layout | 840 compiled map headers (**was 851**) |

Post-cut figures are measured from the `c1fb0b62` build; see Decision log D1. The
`map_groups.json` opt-in total moved from 1,118 to **1,107** entries.

### 2.4 Required-map-define hygiene

`tools/mapjson/required_map_defines.json` currently pins 988 `MAP_*` constants. Every candidate
family below is pinned there (e.g. `MAP_ARTISAN_CAVE_1F` = 114, `MAP_SAFARI_ZONE_NORTH_FRLG` = 118,
all 47 `MAP_BATTLE_FRONTIER_*` = 116). When a map is de-opted, its `MAP_*` define is only preserved
if it stays in this table. **This is a save-file compatibility surface**: map ids are
`(mapNum | mapGroup << 8)` and the group table order is positional, so de-opting renumbers every
later map in the same group. Do it as one deliberate pass before saves matter, exactly as
`ROM_SPACE_AUDIT.md` §4 warns.

---

## 3. Map-side audit table (the core deliverable)

Per-family, measured. Columns:

- **blockdata** — exact bytes of the family's `data/layouts/*/map.bin` + `border.bin` (deduped across
  shared layouts), from `data/layouts/layouts.inc`.
- **map-events** — exact bytes from counting `object_event` (24 B) / `clone_event` (24 B) /
  `warp_def` (8 B) / `coord_event` (16 B) / `bg_event` (12 B) / `connection` (12 B) / `map_events`
  table (20 B) per `asm/macros/map.inc`. Model total 172,084 B vs actual `map_events.o` 162,796 B
  (5.7% over, from padding).
- **header** — 28 B per compiled map header (`data/maps/{name}/header.inc`).
- **script+text** — exact bytes attributed by taking the address span from each family symbol to
  the next symbol in `pokeemerald.elf` (`EventScript_*`, `Text_*`, `Movement_*` labels are all
  exported in `script_data`/`.rodata`). This is the most reliable column in the table.
- **tileset freed** — cascade: after removing the family, which additional `gTileset*` symbols stop
  being referenced and are therefore GC'd (measured from `.elf` symbol sizes).

| family | maps | compiled | blockdata B | map-events B | header B | script+text B | tileset freed B | #tilesets | **subtotal B** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| A · FRLG Safari Zone interiors | 9 | 9 | 16,040 | 1,252 | 252 | 2,681 | 0 | 0 | **20,225** — ✅ removed (D1) |
| B · FRLG Safari Zone, Fuchsia City | 2 | 2 | 602 | 288 | 56 | 2,161 | 4,312 | 1 | **3,107** + 4,312 cascade — ✅ removed (D1) |
| C · Hoenn Safari Zone (Emerald) | 7 | 7 | 19,380 | 1,204 | 196 | 2,953 | 0 | 0 | **23,733** |
| D · Battle Frontier (Hoenn) | 47 | 47 | 33,018 | 7,940 | 1,316 | 162,742 | 100,766 | 9 | **305,782** |
| E · Trainer Tower / Hill (FRLG) | 12 | **0** | 0 | 2,044 ² | 0 | 644 | 0 | 0 | **2,688** ² |
| F · Artisan Cave | 2 | 2 | 5,892 | 120 | 56 | 11 | 0 | 0 | **6,079** |
| G · Link facilities (Hoenn + Frlg) | 8 | 6 | 1,656 | 1,096 | 168 | 723 | 36,050 | 3 | **39,693** |
| H · Contest halls / Elite Four halls | 22 | 21 | 7,952 | 2,672 | 588 | 28,458 | 7,066 | 1 | **46,736** |
| I · Battle Tents | 9 | 9 | 754 | 900 | 252 | 17,121 | 8,554 | 1 | **27,581** |
| J · Secret Base | 24 | 24 | 6,268 | 9,312 | 672 | 0 | 15,960 ³ | 5 | **33,212** |
| **TOTAL** | **142** | **127** | **91,562** | **26,828** | **3,556** | **217,494** | **168,396** | **21** | **507,836** (of which A+B = 27,644 is **already banked**, D1) |
| K · 42 emitted-but-unused layouts | — | 0 | 55,482 | 0 | 0 | 0 | 0 | 0 | **55,482** |
| **GRAND TOTAL** | | | **147,044** | **26,828** | **3,556** | **217,494** | **168,396** | **21** | **563,318** |

¹ Each row is measured **independently**. Two cascades only fire when families are removed
*together*:
- **A + B together** (the whole Kanto Safari Zone) additionally frees
  `gTileset_SafariZoneBuilding` (4,312 B), bringing the combined saving to **532,260 B**.
- A alone frees 0 B of tileset because `gTileset_General_Frlg` (75 maps),
  `gTileset_FuchsiaCity` (6 maps) and `gTileset_Lilycove` (10 maps) are all shared.
- D alone does **not** free `gTileset_BattleFrontier` or `gTileset_BattlePyramid` — see §3.1.
² E is a special case: **all 12 Trainer Tower maps are NULLed by the `layout_version` gate, so their
blockdata, headers and map events are already not in the ROM.** The 2,044 B "map-events" figure is
the on-disk `events.inc` payload that is *not* linked; only the 644 B of shared trainer-hill script
labels are live. Net real-world saving for E is **0 B**.
³ **Correction worth knowing about:** `gTileset_SecretBase` (16,920 B) and
`gTileset_SecretBaseRedCave` (3,192 B) are *code-pinned* by `src/decoration.c:1956, 1969, 2011, 2082,
2146` (`gTilesetPointer_SecretBase` / `_SecretBaseRedCave`). Deleting the 24 Secret Base maps frees
only the **5** variant tilesets (15,960 B). Freeing the other 20,112 B additionally requires
stripping secret-base decoration placement from `src/decoration.c`.

### 3.1 Tilesets that die with each family

| family removed | newly-unreferenced tilesets | bytes |
|---|---|--:|
| A + B (FRLG Safari Zone, together) | `gTileset_SafariZoneBuilding` | 4,312 — ✅ **realised**, D1. Required deleting the struct + its 4 graphics symbols from `plastic_ox_kanto_additions.h`; `--gc-sections` alone would not have freed it. |
| C (Hoenn Safari Zone) | — | 0 |
| D (Battle Frontier, 47 maps) | `gTileset_BattleArena`, `BattleDome`, `BattleFactory`, `BattleFrontierRankingHall`, `BattlePalace`, `BattlePike`, `gTileset_HoennOrasFrontierGeneral`, `gTileset_HoennOrasBattleFrontierOutsideEast`, `gTileset_HoennOrasBattleFrontierOutsideWest` — **9 tilesets** | 100,766 |
| F (Artisan Cave) | — (`gTileset_Cave` + `gTileset_General` are shared) | 0 |
| G (Link facilities) | `gTileset_CableClub_Frlg`, `gTileset_UnionRoom`, `gTileset_HallOfFame` | 36,050 |
| H (Contest halls) | `gTileset_Contest` | 7,066 |
| I (Battle Tents) | `gTileset_BattleTent` | 8,554 |
| J (Secret Base) | `gTileset_SecretBaseBlueCave`, `BrownCave`, `YellowCave`, `Tree`, `Shrub` — **5 tilesets** (`SecretBase` + `SecretBaseRedCave` are code-pinned, see footnote ³) | 15,960 |

### 3.1b Bonus: 42 emitted-but-unreferenced layouts (55,482 B)

`data/layouts/layouts.inc` emits 693 layouts and `gMapLayouts` has an entry for each, so every one
of them is linker-referenced and survives `--gc-sections` — but only 651 are actually used by a
compiled map. The other **42 cost 55,482 B for nothing**. They are removed by deleting the entries
from `data/layouts/layouts.json` (they are already absent from `map_groups.json`).

| layout | bytes | | layout | bytes |
|---|--:|---|---|--:|
| `Route111_NoMirageTower` | 11,208 | | `SkyPillar_Top_Clean` | 1,304 |
| `SootopolisCity_LegendsBattle` | 7,208 | | `PalletTown` | 960 |
| `Route130_MirageIsland` | 6,408 | | `FallarborTown_LeftoverRSContestHall` | 764 |
| `Route131_SkyPillar` | 4,808 | | `CaveOfOrigin_Unused_B4F_Lava` | 732 |
| `Route2` | 3,840 | | `SkyPillar_1F..5F_Clean` | 400 × 5 |
| `UnusedOutdoorArea` | 3,024 | | `Route2_Entrance` | 360 |
| `Route8` | 2,888 | | `LittlerootTown_ProfessorBirchsLabWithTable` | 348 |
| `Route19` | 2,880 | | `FallarborTown_LeftoverRSContestLobby` | 218 |
| `SeafloorCavern_Room9_Lava` | 2,492 | | `SootopolisCity_MysteryEventsHouse_1F_StairsUnblocked` | 184 |
| `SeafoamIslands_B3F/B4F_CurrentStopped` | 1,824 × 2 | | `UnusedCave1..14` / `UnusedContestRoom1..3` / `BattleFrontier_BattlePikeRoomUnused` | 12 × 18 |
| | | | **total** | **55,482** |

**Lowest-risk win in the whole audit**: no map, no script, no tileset, no code reference. Just prune
`layouts.json`. ⚠ Caveat: check `required_map_defines.json` and any `warp MAP_*`/`connections.inc`
that still names one of these before deleting — `Route2` and `Route19` are Hoenn originals and are
probably safe, but `BattlePyramidSquare01-16` (§3.1) are *not* in this list and are separately live.

`gTileset_BattleFrontierOutsideWest` (18,360 B) and `…OutsideEast` (15,124 B) are **already dead**
— the live Frontier maps use the `HoennOras` variants instead.

### 3.2 Already-dead tilesets (no map change needed)

31 of 208 unique declared tilesets are unreferenced by any live layout. 15 still cost bytes. The figures
below **include** `gTilesetAnims_*` payload and the 24 B `struct Tileset`, which a naive
`gTilesetTiles_*` measurement misses.

| tileset | tiles | palettes | metatiles+attrs | anims | **total B** | why dead |
|---|--:|--:|--:|--:|--:|---|
| `gTileset_BattleFrontierOutsideWest` | 8,644 | 512 | 9,180 | 784 | **19,144** | superseded by `gTileset_HoennOrasBattleFrontierOutsideWest` |
| `gTileset_WhirlIslands_Hns` | 9,244 | 416 | 8,192 | 0 | **17,876** | HNS map not imported |
| `gTileset_BattleFrontierOutsideEast` | 5,408 | 512 | 9,180 | 784 | **15,908** | superseded by the HoennOras variant |
| `gTileset_Cave_Ice_Hns` | 7,188 | 416 | 8,192 | 0 | **15,820** | HNS ice cave not imported |
| `gTileset_BlackthornGym_Hns` | 7,680 | 416 | 7,328 | 0 | **15,448** | not imported |
| `gTileset_EcruteakTheater_Hns` | 6,580 | 416 | 8,192 | 0 | **15,212** | not imported |
| `gTileset_SilphCo_Hns` | 6,080 | 512 | 8,176 | 0 | **14,792** | not imported |
| `gTileset_Cave_DragonsDen_Hns` | 8,152 | 416 | 6,064 | 0 | **14,656** | not imported |
| `gTileset_BurnedTower_Hns` | 6,476 | 512 | 6,176 | 0 | **13,188** | not imported |
| `gTileset_EcruteakCity_Gym_Hns` | 3,332 | 416 | 8,192 | 0 | **11,964** | not imported |
| `gTileset_Unused1` | 20 | 512 | 36 | **8,192** | **8,784** | no map; its 4 anim frames have **no** `InitTilesetAnim_` callback and are fully orphaned |
| `gTileset_SaffronCity_Gym_Hns` | 1,288 | 416 | 2,784 | 0 | **4,512** | not imported |
| `gTileset_ViridianCity` | 1,720 | 512 | 1,900 | 0 | **4,156** | FRLG-layout gate. ⚠ declared **twice** — `headers.h:839` (FRLG block, not compiled) and `headers.h:2068` (`#if !IS_FRLG`, compiled). Only one is live. `gTileset_ViridianCity_Hns` is the Kanto one that is actually used. |
| `gTileset_Unused2` | 1,456 | 512 | 1,044 | 160 | **3,196** | no map. Like `Unused1`, its anim frames have no `InitTilesetAnim_` callback. |
| `gTileset_Mart` | 20 | 512 | 1,888 | 0 | **2,444** | no live map. Also declared twice: `headers.h:949` (FRLG, not compiled) and `plastic_ox_kanto_additions.h:1057` (compiled). |
| **total** | | | | | **177,100** | |

**Counting note:** 208 unique `const struct Tileset` definitions (215 textual, minus 2 duplicate
declarations: `gTileset_ViridianCity` and `gTileset_Mart` each appear once in a non-compiled
`IS_FRLG` block and once compiled). 177 live, **31 dead, 15 of which still cost bytes**. The other
16 dead tilesets are inside the `#else // IS_FRLG` block of `src/data/tilesets/headers.h:835-1469`
and have **no ELF symbols at all** — already 0 B: `gTileset_TrainerTower`, `SeviiIslands45/67/123`,
`HoennBuilding`, `PokemonLeague`, `NavelRock_Frlg`, `MtEmber`, `BerryForest`, `IndigoPlateau`,
`IslandHarbor_Frlg`, `SilphCo`, `TanobyRuins`, `ViridianForest`, `ViridianGym`,
`UnusedGatehouse1/2`.

**Sanity check — the linker is NOT already dropping these.** `nm -S` shows them all at real
addresses, e.g. `gTilesetTiles_BattleFrontierOutsideWest` at `0x08FE5A34`, size 8,644. `pokeemerald.map`
line 73413 shows `src/tilesets.o` as **one 1,933,396-byte `.rodata` blob** — LTO merges the whole
translation unit's constant data, so `--gc-sections` cannot drop individual tilesets. Deleting the
`const struct Tileset gTileset_X = {…}` block from `headers.h` is what actually frees the bytes.

⚠ **`gTileset_BattleFrontierOutsideWest/East` are the only two dead tilesets still referenced from
C code**: `src/field_door.c:461-464, 473-474` (duplicate `METATILE_BattleFrontierOutside*_Door*`
door-table rows; the live HoennOras rows are at `:418-423`). Deleting these two tilesets also
requires deleting those 6 rows plus the `sDoorAnimTiles_BattleDome/Factory/BattleFrontier/
BattleFrontierSliding` arrays and their palettes (a further ~3,088 B).

**The other 171 KB is small potatoes next to §4.** Do not spend effort here before the map work.
Note that 123,468 B of it is HNS/Johto content you may legitimately want later — treat the HNS
orphans as "parked", not "deleted".

---

## 4. Code + data cuts (feature level)

No config gates exist for any of this. `include/config/general.h:5` has only
`#define POX_LINK_ENABLED 0`, and even that does **not** gate object inclusion — `trade.o`,
`union_room.o` etc. still link in. There is no `P_BATTLE_FRONTIER`, `P_TRAINER_HILL`,
`P_CONTEST`, or `P_ARTISAN_CAVE` anywhere in `include/`. **All of this code is unconditionally
compiled, and every byte must be removed by deleting objects or wrapping them in `#if`.**

Per-object sizes from `arm-none-eabi-size -A build/emerald/**/*.o` (`.text + .rodata + .data`);
data tables from `arm-none-eabi-nm -S` on `pokeemerald.elf`.

| feature | code B | key objects | exclusive data/graphics B | **total B** | risk |
|---|--:|---|--:|--:|---|
| **Battle Frontier** | 226,862 | `battle_tower` 106,554; `battle_dome` 31,448; `battle_factory_screen` 25,688; `frontier_util` 18,924; `battle_pyramid` 13,368; `battle_pyramid_bag` 8,112; `battle_pike` 6,640; `battle_transition_frontier` 4,784; `battle_factory` 4,656; `battle_arena` 3,040; `battle_frontier` 2,484; `battle_palace` 1,164 | `gBattleFrontierMons` 31,752; `sFrontierTrainerSlides` 50,400; `gBattleFrontierTrainers` 15,600; `sFrontierBrainsMons` 840; `gFrontierBrainInfo` 196; logo/pass/squares/palette graphics 17,343 | **~343,000** | **Medium** — see §6.1 |
| **Contests + bard music** | 256,805 | `bard_music` 165,678; `contest` 39,239; `contest_painting` 15,872; `contest_util` 13,968; `contest_ai` 11,012; `contest_effect` 6,428; `contest_link` 2,900; `contest_link_util` 1,708 | `sBardSoundTemplates_Pokemon` 75,504 + other bard templates 160,680 total; `gContestOpponents` 5,760; audience/painting tables 17,604 total | **~275,000** | **High** — `plastic_ox_contest.c` is a *different* system; do not confuse them |
| **Trainer slide banners** | 208,432 | `trainer_slide` 208,432 | `sTrainerSlides` 155,904 | **~364,000** | **Low** — purely decorative, no script references it in the region |
| **Link / union / trade / record** | 228,191 | `pokemon_storage_system` 79,928; `trade` 73,854; `union_room` 18,877; `union_room_chat` 12,160; `link` 9,204; `record_mixing` 7,268; `cable_club` 6,028; `cable_car` 5,788; `recorded_battle` 5,104; `battle_records` 4,868; `battle_controller_recorded_player` 2,560; `mail` 2,552 | `gTrade*` tables 23,721; `gUnionRoom*` 1,404 | **~253,000** | **High** — `pokemon_storage_system` is the **PC**, which the game needs. Only `trade`/`union_room`/`record_mixing` are safe; see §6.5 |
| **Minigames** | 161,587 | `slot_machine` 30,938; `pokemon_jump` 21,208; `dodrio_berry_picking` 20,839; `roulette` 17,344; `berry_blender` 16,647; `berry_crush` 12,891; `match_call` 4,996; `berry_tag_screen` 2,935; `minigame_countdown` 2,424 | — | **~162,000** | **Medium** — Pokéblock-adjacent; check `pokeblock` deps |
| **Trainer Hill** | 20,736 | `trainer_hill` 20,736 | `TrainerHill*` rodata 24,745 (incl. `gTrainerHillMons`) | **~45,000** | **Low** — but its 12 maps are already NULLed, so it is unreachable dead code today |
| **Secret Base** | 11,748 | `secret_base` 11,748 | 194 | **~12,000** | **Low** |
| **Safari Zone engine** | 1,016 | `safari_zone` 1,016 (`pokeblock` 7,031, `plastic_ox_contest` 1,056) | `gSafari*`/`sSafari*`/`SafariZone*` rodata+data 21,431; `gObjectEventPic_SafariBall` 1,792; `gItemIcon_SafariBall` 172; map-preview tiles/tilemap 5,136 | **~36,000** | **Keep** — this is the mechanic you are keeping |

### 4.1 Objects that are *not* facility costs

`battle_anim_*` totals ~180 KB across 30 objects. These are battle animation effects, unrelated to
the Frontier. Do not include them in a facility cut.

---

## 5. Object event graphics

Object event pics are almost entirely **shared**. Only 5 symbols in the whole candidate set are
used by exactly one map family:

| symbol | used only by | on-disk |
|---|---|---|
| `OBJ_EVENT_GFX_BRANDON` | Battle Frontier (Pyramid King) | frontier brain trainer pic |
| `OBJ_EVENT_GFX_DUSCLOPS` | Battle Frontier | Frontier Brain sprite |
| `OBJ_EVENT_GFX_KIRLIA` | Battle Frontier | Frontier Brain sprite |
| `OBJ_EVENT_GFX_UNION_ROOM_NURSE` | Link facilities | shared `nurse` sheet |
| `OBJ_EVENT_GFX_SCIENTIST_2` | Contest halls | shared `scientist` sheet |

Family object-graphics usage: A = 10, B = 1, C = 16, D = 77, E = 11, F = 1, G = 11, H = 50, I = 15,
J = 15. **Savings from object-graphics pruning within the candidate families: effectively 0 B.**
Every graphic is in a shared spritesheet. Do not bother.

**One object-graphics win does exist, outside the families above.** 13 `gObjectEventPic_*` are
referenced *only* by opted-in maps whose layout is FRLG-only — i.e. they are dead in this build:
`AGATHA` 768, `BRUNO` 768, `CELIO` 2,304, `LAPRAS_DOLL` 512, `LORELEI` 2,304, `METEORITE` 512,
`MOLTRES` 512, `RUBY` 128, `SAPPHIRE` 128, `SPEAROW` 384, `SWIMMER_F_LAND` 2,560,
`TRAINER_TOWER_DUDE` 768, `TUBER_F_FRLG` 1,152 = **12,800 B of pics + 13 × 36 B info structs =
13,268 B**. Their metatile/tileset counterparts (`PokemonLeague`, `MtEmber`, `SeviiIslands*`,
`TrainerTower`, `NavelRock_Frlg`) are already FRLG-only, so this is a coherent removal set.

⚠ A further **21 `OBJ_EVENT_GFX_*` ids are referenced by neither map nor code** — but they are the
dynamic/avatar/follower set (`BRENDAN_NORMAL/FIELD_MOVE/MACH_BIKE/SURFING/ACRO_BIKE`, `RED_*`,
`BIRCHS_BAG`, `TEACHY_TV_HOST`, `TRAINER_TIPS`, `OW_MON`, `QUINTY_PLUMP`, `FOSSIL_FRLG`, …).
Only 756 B of info structs; their pics are shared with live graphics. **Verify individually before
touching — do not bulk-delete.**

---

## 6. Per-candidate detail: dependencies and risk

### 6.1 Battle Frontier — HIGH VALUE, MEDIUM RISK

**What it is:** 47 Hoenn maps (`gMapGroup_SpecialArea`) plus the complete Frontier battle-mode
code and the Frontier facility battle scripts (`BattleArena`, `BattleDome`, `BattleFactory`,
`BattlePalace`, `BattlePike`, `BattlePyramid`, `BattleTower`).

**Why it is safe-ish:** Plastic Ox is Kanto/Johto. `warp_playtest_v1_unblocked.json` reaches **28**
Battle Frontier maps, but the warp walk explicitly **excluded 28 of them** as "facility state
machine — untestable". The Frontier has no story trigger anywhere in `plastic_ox/alpha/`.

**Dependencies to clean:**
1. `data/maps/map_groups.json` — remove all 47 `BattleFrontier_*` entries from `gMapGroup_SpecialArea`.
2. `tools/mapjson/required_map_defines.json` — drop the 47 `MAP_BATTLE_FRONTIER_*` defines unless
   something still references them.
3. `data/event_scripts.s` lines 79 matches — remove the `.include "data/maps/BattleFrontier_*/scripts.inc"`
   lines.
4. `data/scripts/plastic_ox_kanto_maps.inc` — no Frontier entries (it is Kanto-only), so untouched.
5. `src/data/trainers.h` — check for `TRAINER_FRONTIER_*` and the Frontier Brain battle definitions
   that call `BattleFrontier_…` specials.
6. `data/specials.inc` — Frontier specials (`gSpecialVar_0x8004` challenge, `SetFrontierData`,
   `GetFrontierData`, `SaveGameFrontier`, `CB2_ReshowFrontierPass`, `HideFrontierPass`).
7. `src/battle_frontier*.c`, `battle_tower.c`, `battle_dome.c`, `battle_factory*.c`,
   `battle_arena.c`, `battle_palace.c`, `battle_pike.c`, `battle_pyramid.c`,
   `battle_transition_frontier.c`, `frontier_util.c`, `battle_frontier_pass.c` — remove from the
   `Makefile` OBJ list, plus `src/battle_main.c` / `src/battle_setup.c` / `src/battle_util.c`
   hook points, plus the `BattleFrontier_` battle scripts in `data/battle_scripts_1.s`.
8. Data tables: `src/data/battle_frontier_mons.h`, `battle_frontier_trainers.h`,
   `frontier_trainer_slides.h`.
9. `src/tv.c` — `TryPutFrontierTVShowOnAir`, `gTVPokemonNewsBattleFrontierText00-18`.
10. `include/constants/battle_transition.h` — `B_TRANSITION_GROUP_BATTLE_FRONTIER` and friends.
11. TV / Match Call data referencing the Frontier (`MatchCall_BattleFrontierStreakText*`).
12. `src/data/object_events.h` — Frontier Brain trainer pics (`gObjectEventPic_Dusclops`,
    `gObjectEventPic_Kirlia`, `gObjectEventPic_Brandon`); they are in shared sheets so removal is
    mostly a table edit.

**Risk: Medium.** Large and mechanical, but the Frontier touches battle setup, TV, the Frontier Pass
save-block field (`gSaveBlock1Ptr->frontier`), and `SaveGameFrontier`. The save-block field is the
real landmine: removing it mid-project renumbers the save struct. Budget a day.

### 6.2 Secret Base — LOW VALUE, LOW RISK

24 maps in `gMapGroup_IndoorDynamic`, 52,324 B map-side + ~12 KB code. `SecretBase_*` are **not in
the warp closure** (`warp_playtest_v1_unblocked.json` shows 0). `gSecretBase*` data is only 194 B, so
the win is almost entirely blockdata + tilesets. Nice-to-have; do it if you need bytes, not before.

### 6.3 Contest halls — MEDIUM VALUE, HIGH RISK OF CONFUSION

22 maps, 46,736 B map-side. **But** the ~275 KB code/data column is the *vanilla Emerald contest
system*, not the Plastic Ox one. `src/plastic_ox_contest.c` is a 182-line custom "catch-and-judge"
mini-game that runs **in the National Park** and shares only the ball/step globals. If you cut
`contest*.c`/`bard_music.c`, `plastic_ox_contest.c` is unaffected — but `NationalPark_Normal_hns`
hosts `PlasticOxContest_EventScript_Attendant` as an object event, so removing the *contest halls*
maps is fine while removing the *contest code* needs its own audit. `sBardSoundTemplates_Pokemon`
(75,504 B) is the single largest easy win inside this family and is referenced by nothing in
`plastic_ox/`.

### 6.4 Battle Tents — MEDIUM VALUE, LOW RISK

9 maps (3 towns × 3 rooms), 27,581 B map-side + 8,554 B `gTileset_BattleTent`. Reached 0 times in
the warp closure. `src/battle_tent.c` reuses `battle_tower.c` machinery, so cutting tents alone
saves the maps but not the code.

### 6.5 Link facilities — MEDIUM RISK, DO NOT CUT BLINDLY

Map side is only 39,693 B but it cascades 36,050 B of tilesets. **However** the code column
(228,191 B) is dominated by `pokemon_storage_system` (79,928 B), which is the **PC / item storage
the game depends on**. `POX_LINK_ENABLED 0` does not remove it. Only these are genuinely
facility-shaped and safe to consider:
- `trade` 73,854 B + `gTrade*` 23,721 B — verify no in-game trade scripts first.
- `union_room` + `union_room_chat` 31,037 B + `gUnionRoom*` 1,404 B. Note: `UnionRoom` and
  `UnionRoom_Frlg` **are** in the warp closure (2 maps), so removing them needs a warp repoint.
- `record_mixing` / `recorded_battle` / `battle_records` / `battle_controller_recorded_player`
  19,796 B + `RecordedBattle` CB2.
- `cable_club` 6,028 B, `cable_car` 5,788 B — `cable_car` is used by `MtChimney_CableCarStation`,
  so it is **not** dead.

### 6.6 Trainer Hill / FRLG Trainer Tower — ZERO VALUE, ZERO RISK

All 12 `TrainerTower_*_Frlg` + `SevenIsland_TrainerTower_Frlg` maps have
`layout_version: "frlg"` and are NULLed out of `gMapLayouts`. Their `data/layouts/*/map.bin` is
never `.incbin`'d, their headers and events are never emitted, and `TrainerTower_1F_Layout` does not
exist as a label in the built ROM. `gTileset_TrainerTower` and `gTileset_SeviiIslands67` are
already GC'd to 0 B.

`src/trainer_hill.c` (20,736 B) + `gTrainerHillMons` (~24,745 B of rodata) *are* live in the ROM
but are unreachable — nothing can warp into a NULL-layout map. So cutting them saves ~45 KB, but
only if you also add a real `#if` around `src/trainer_hill.c` and every reference
(`InTrainerHillChallenge`, `IsTrainerHillChallengeActive`, `TrainerHillStartChallenge`,
`GiveChallengePrize`, `B_TRANSITION_GROUP_TRAINER_HILL`). The playtest excluded these 12 maps for
"facility state machine", which is why nobody noticed they were already NULL.

### 6.7 Artisan Cave — LOW VALUE, LOW RISK

2 maps, 6,079 B. `ArtisanCave_1F/scripts.inc` is a bare `.byte 0` — no mechanic. `gArtisanCave_1F_LandMonsInfo`
is 16 B of rodata; the whole `Artisan` symbol family is 149 B. `ArtisanCave_1F` **is** in the warp
closure (excluded as "facility state machine"), so removing it requires repointing the route that
leads to it. Given 6 KB, that is a bad trade. Leave it.

### 6.8 FRLG Safari Zone — see §7

---

## 7. Safari Zone → National Park

### 7.0 The single most important fact: `IS_FRLG == 0`

`Makefile:1` sets `GAME_VERSION ?= EMERALD`, so `include/constants/global.h:67-78` resolves
`IS_FRLG = 0`. Everything gated on `IS_FRLG` is **compiled out**:

| gated thing | consequence |
|---|---|
| `src/safari_zone.c:63-66` | step budget is **500** (Hoenn), never the FRLG 600 |
| `data/event_scripts.s:633-1075` (`.if IS_FRLG` … `.endif`) | **the 11 `SafariZone_*_Frlg/scripts.inc` includes at `:704-712, 943, 945` are DEAD.** The live copy is `data/scripts/plastic_ox_kanto_maps.inc:57-65, 156, 158`, inside the `.if !IS_FRLG` block at `:1077-1099` |
| `data/scripts/safari_zone.inc:1-28` | the `#else` (**Hoenn**) branch is the live one → every exit path warps to `MAP_ROUTE121_SAFARI_ZONE_ENTRANCE, 2, 5` |
| `src/battle_util.c:739-900` | no BAIT/ROCK throw actions |
| `src/battle_controller_safari.c:301` | Emerald menu (`BALL / POKéBLOCK / GO NEAR / RUN`); `gText_SafariZoneMenuFrlg` is dead data |

**Net effect: the Kanto Safari Zone's run-out-of-balls / run-out-of-time exit teleports the player to
`Route121_SafariZoneEntrance` — a Hoenn building that is not in the 417-map warp closure.** The
facility cannot be exited correctly. This is a live bug, not a trim opportunity.

### 7.1 How the Safari Zone is wired today

**The mechanic engine is Emerald-native and completely map-agnostic.**
`src/safari_zone.c` (265 lines, 1,016 B of compiled code, ~21 KB of associated rodata):

- `EnterSafariMode()` / `ExitSafariMode()` → `FLAG_SYS_SAFARI_MODE` (`include/constants/flags.h:1414`),
  `gNumSafariBalls = 30`, `gSafariZoneStepCounter = 500` (see §7.0).
- `SafariZoneTakeStep()` (`:80-97`) — called from `src/field_control_avatar.c:829`; decrements the
  step counter every field step, fires `SafariZone_EventScript_TimesUp` at zero.
- `SafariZoneRetirePrompt()` (`:99-103`) — fired by `src/start_menu.c:819`.
- `CB2_EndSafariBattle()` (`:105-127`) — run-out-of-balls teardown; warps on
  `B_OUTCOME_NO_SAFARI_BALLS`.
- Pokéblock feeder array `sPokeblockFeeders[10]`, keyed on
  `gSaveBlock1Ptr->location.mapNum` + x/y (**no map-id constant anywhere**).

There is **no** `sSafariZoneState` / `SAFARI_MODE_*` / `areaId` struct in this fork — those are
pokehns-expansion symbols. **The National Park can be the safari-equivalent with no engine changes.**

Consumers: `src/battle_setup.c:334-339` (`GetSafariZoneFlag() || PlasticOxContest_IsActive()` →
`DoSafariBattle()`), `:411-418` (sets `BATTLE_TYPE_SAFARI`), `src/battle_main.c:434,437`
(`B_ACTION_SAFARI_BALL` / `B_ACTION_SAFARI_RUN`), `src/battle_util.c:787-796, 910-917`,
`src/start_menu.c:303,370-457,478,542,815-822`, `src/wild_encounter.c:534-546, 1438`,
`src/overworld.c:1661-1664, 1930, 2017, 2046, 2203`, `src/tv.c` (`TryPutSafariFanClubOnAir`).

**The FRLG (Kanto) Safari Zone is a thin script layer on top of that engine:**

| Piece | File | Role |
|---|---|---|
| Ticket building | `data/maps/FuchsiaCity_SafariZone_Entrance_Frlg/scripts.inc` (280 lines) | the real facility. `TryEnterSafariZone` `:112-134`: `ScriptCheckFreePokemonStorageSpace`, `checkmoney 500`, `removemoney 500`, `special EnterSafariMode` `:130`, `warp MAP_SAFARI_ZONE_CENTER, 255, 26, 30` `:132` |
| Exit building | same file, `MAP_SCRIPT_ON_FRAME_TABLE` `:2` keyed on `VAR_MAP_SCENE_FUCHSIA_CITY_SAFARI_ZONE_ENTRANCE` (`include/constants/vars_frlg.h:124` = 0x406E) | `ExitWarpIn` `:27` / `ExitEarly` `:40` / `ExitWalkIn` `:12` → `special ExitSafariMode`; `ReturnToSafariZone` `:54-61` warps back to `MAP_SAFARI_ZONE_CENTER, 26, 30` |
| Decoration building | `data/maps/FuchsiaCity_SafariZone_Office_Frlg/scripts.inc` (44 lines) | 4 flavour NPCs, **no mechanic at all** |
| 9 field interiors | `data/maps/SafariZone_{Center,East,North,West}[_RestHouse]_Frlg`, `SafariZone_SecretHouse_Frlg` | **plain field maps.** `SafariZone_Center_Frlg/scripts.inc` is 31 lines: a `setworldmapflag` + 3 signs. The only functional one is `SafariZone_SecretHouse_Frlg:7-15`, which gives `ITEM_HM03` (Surf) on first visit. |
| Hoenn originals | `data/maps/SafariZone_{North,South,Northwest,Northeast,Southeast,Southwest,RestHouse}` + `Route121_SafariZoneEntrance` | `SafariZone_South/scripts.inc` is the **full Hoenn state machine** (139 lines, `VAR_SAFARI_ZONE_STATE` 1/2 protocol, attendant choreography); `Route121_SafariZoneEntrance/scripts.inc` is the Hoenn ticket building. Both compiled, both **structurally unreachable** (Route 120/121/122/123, Lilycove and Slateport are not in the closure). |

**Encounters — the decisive finding:**

| zone | encounter slots in ROM | why |
|---|---|---|
| Hoenn `SafariZone_*` (6 route maps) | **88 slots** (12-25 levels, 38 species) | `#ifdef EMERALD` blocks at `src/data/wild_encounters.h:12772, 14784, 14824, 15698, 15736` compile fine |
| Kanto `SafariZone_*_Frlg` (4 route maps) | **0 slots** | the FRLG tables `sSafariZone{Center,East,North,West}_{FireRed,LeafGreen}` sit behind `#ifdef FIRERED` / `#ifdef LEAFGREEN` from `src/data/wild_encounters.h:4109`. `grep -c "sSafariZoneCenter_FireRed" pokeemerald.map` → **0** |
| `NationalPark_Normal_hns` | **36 slots** (12 × 3 time-of-day, rate 20, weighted, lv 17-19, 8 species) + a contest-only table | `gPoxPUNationalParkNormalHns_{Morning,Day,Night}_LandMonsInfo` at `src/data/wild_encounters.h:11895, 11916, 11937` |

**So: the Hoenn Safari Zone is fully compiled with Pokémon but unreachable; the Kanto Safari Zone is
reachable but empty.** A player walks up to the Fuchsia City counter, pays ¥500, receives 30 Safari
Balls and 500 steps, and finds nothing — then, on running out, is teleported to an unreachable Hoenn
building. **The National Park is the only one of the three that is both reachable and populated.**

**Flags:** 28 `*SAFARI*` flags. Only **two** are mechanically live: `FLAG_SYS_SAFARI_MODE`
(C code) and `FLAG_GOOD_LUCK_SAFARI_ZONE` (Hoenn entrance script). The 11 Kanto
`FLAG_HIDE_SAFARI_ZONE_*` names in `include/constants/flags.h:1855-1865` are all `0`, and all 11
`FLAG_HIDDEN_ITEM_SAFARI_ZONE_*` are Hoenn-park item flags. No `F_SAFARI_*` flags exist. None of
these cost ROM bytes. One cross-map dependency to preserve:
`FuchsiaCity_WardensHouse_Frlg/scripts.inc:8,28` trades `ITEM_GOLD_TEETH` for
`FLAG_HIDE_SAFARI_ZONE_WEST_GOLD_TEETH` — deleting `SafariZone_West_Frlg` silently kills the
Warden's exchange (no build break).

**Pokéblock feeders are dead:** `EventScript_PokeBlockFeeder` and
`EventScript_ChoosePokeblock` in `data/scripts/safari_zone.inc:58-88` are referenced by **zero**
map events (`grep -rl EventScript_PokeBlockFeeder data/maps/*/events.inc` → nothing). The
`SafariZone_EventScript_OutOfBallsMidBattle` / `_OutOfBalls` pair *is* live via `CB2_EndSafariBattle`.

### 7.2 The National Park today

`NationalPark_Normal_hns` (in `gMapGroup_PlasticOxDungeons`, `MAPSEC_NATIONAL_PARK`, group 78) is
the region's designated safari-equivalent per `plastic_ox/alpha/REGION_PLAN.md:21` ("D — Gym 3 …
Goldenrod → Route 35 → National Park → Route 36 → Route 37 → Ecruteak … Park must be on the main
path") and `plastic_ox/alpha/STORY_TRIGGERS.md:64` ("Mandatory geographic passage, catching/trainer
respite").

Its current state:

- 48 × 56, `MAP_TYPE_ROUTE`, `gTileset_Johto_General_Hns` + `gTileset_NationalPark_Hns`
  (12,356 B tileset), `MUS_RG_VIRIDIAN_FOREST`, 5,376 B blockdata.
- **0 warps, 0 connections, but a full encounter set** (3 time-of-day tables + the contest override).
  It is reached via `VAR_POX_PORTAL_TRIGGER` coord events (`PoxRegion_route35_park_b` /
  `PoxRegion_park_route36_a`), not warps.
- 11 object events, including:
  - `PlasticOxContest_EventScript_Attendant` at (12,42) — the Plastic Ox Contest,
  - `Pox_PU_PARK` at (25,30) — a PU-format park battle,
  - `Pox_EcruteakRoad` at (22,39),
  - 8 flavour NPCs, 1 hidden item, 1 sign.
- **In the 417-map warp closure** (unlike the Hoenn Safari Zone).

### 7.3 The critical interdependency

`src/plastic_ox_contest.c` is a **second, independent** facility mode that runs **inside the
National Park** and **borrows the Safari Zone globals**:

- `PlasticOxContest_Start()` sets `gNumSafariBalls = CONTEST_BALLS (20)` and
  `gSafariZoneStepCounter = CONTEST_STEPS (500)`.
- `PlasticOxContest_TakeStep()` is called at the top of `SafariZoneTakeStep()` in
  `src/safari_zone.c:71` and short-circuits the real safari countdown.
- `PlasticOxContest_IsActive()` hard-checks
  `gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_NATIONAL_PARK_NORMAL_HNS)`.
- `PlasticOxContest_Judge()` zeroes `gNumSafariBalls` / `gSafariZoneStepCounter`.
- `SafariZoneRetirePrompt()` branches to `PlasticOxContest_EventScript_Retire` when
  `PlasticOxContest_HasSession()`.

**Consequence:** you cannot rip out `src/safari_zone.c`, `safari_zone.h`, `gNumSafariBalls`,
`gSafariZoneStepCounter`, `SafariZoneTakeStep()`, `CB2_EndSafariBattle()`, `ITEM_SAFARI_BALL`, or
`gObjectEventPic_SafariBall` without breaking the National Park contest. The **Kanto Safari Zone
maps** are droppable; the **engine** is not.

### 7.4 What has to change to make the National Park the safari-equivalent

Ordered, with the file each step touches:

| # | Change | Files | Risk |
|---|---|---|---|
| 1 | **Give the National Park a gate.** Add a safari-ranger building (new FRLG-style interior or an HNS interior) adjacent to `NationalPark_Normal_hns`, or reuse an existing `gMapGroup_PlasticOxInteriors` building. The building hosts the attendant NPC. | new `data/maps/<Park>_SafariRanger/map.json` + `events.inc` + `scripts.inc`; `data/maps/map_groups.json` | Low |
| 2 | **Port the ticket script.** Copy the `TryEnterSafariZone` flow from `FuchsiaCity_SafariZone_Entrance_Frlg/scripts.inc:112-134`: PC-space check, `checkmoney 500`, `removemoney 500`, `special EnterSafariMode`, then warp into the park. Price/ball count is a design choice — `EnterSafariMode` hard-codes 30 balls / 500 steps (`src/safari_zone.c:57-69`). | new building `scripts.inc` | Low |
| 3 | **Add the exit building + on-frame exit table.** Copy `FuchsiaCity_SafariZone_Entrance_Frlg/scripts.inc:9-61` (`ExitWarpIn` / `ExitEarly` / `ExitWalkIn` / `ReturnToSafariZone`, all `special ExitSafariMode`) onto a park gate. Use a spare `VAR_` for the scene var; **do not** reuse `VAR_MAP_SCENE_FUCHSIA_CITY_SAFARI_ZONE_ENTRANCE` (0x406E) if you intend to reclaim that FRLG var. | new building `scripts.inc`; `include/constants/vars.h` | Low |
| 4 | **Repoint `data/scripts/safari_zone.inc` — this is the actual bug fix.** Because `IS_FRLG == 0`, the **live** branch at `:11` and `:25` is `warp MAP_ROUTE121_SAFARI_ZONE_ENTRANCE, 2, 5`, an unreachable Hoenn building. Rewrite the whole `#if IS_FRLG / #else` pair to a single target (the park gate), or delete the Hoenn branch and flip the guard. | `data/scripts/safari_zone.inc:1-28` | **High — this is the exit path** |
| 5 | **Decide: park = safari, or park = safari *and* contest?** `PlasticOxContest_IsActive()` keys off the park's map id (`src/plastic_ox_contest.c:38-39`) and `SafariZoneTakeStep()` consults the contest **first** (`src/safari_zone.c:82-83`). Running both on one map makes the step counter ambiguous. Cleanest: the park becomes the safari facility and the contest relocates, or the contest's step decrement is gated on `GetSafariZoneFlag() == FALSE`. | `src/plastic_ox_contest.c`, `src/safari_zone.c:80-83` | **High — design decision** |
| 6 | **Author a park safari encounter table.** The park already has `gPoxPUNationalParkNormalHns_{Morning,Day,Night}` (36 slots, lv 17-19) and a contest override `sPoxParkContestDay` (`src/data/plastic_ox_pu_encounters.h:47`) swapped in at `src/wild_encounter.c:922-927`. A safari-specific table reusing that same override hook is the template. The 88 dead-ish Hoenn `gSafariZone_*` tables are a balance reference. | `src/data/wild_encounters.{json,h}`, `src/wild_encounter.c:922-927` | Medium (balance) |
| 7 | **Connect the park to Route 35 / Route 36.** The map has 0 warps and 0 connections; entry is via `VAR_POX_PORTAL_TRIGGER` coord events. `plastic_ox/alpha/LEGACY_REGION_PLAN.md:108-109` specifies the intended portal pair (`NationalPark_Normal (39,20)/(39,26) ⇄ Route36_hns (16,19)/(16,20)`). | `connections.inc`, `map.json` | Medium (seam work — see the map-port skill's `references/port-verification.md`) |
| 8 | **Rewire the 11 Kanto safari maps, then delete them.** Remove `warp_def 24,5 → MAP_FUCHSIA_CITY_SAFARI_ZONE_ENTRANCE` and `warp_def 28,16 → MAP_FUCHSIA_CITY_SAFARI_ZONE_OFFICE` from `FuchsiaCity_Frlg/events.inc` (lines 26 and 29). **This is a hard build break if skipped** — the `dest_map` constants would be undefined. | `data/maps/FuchsiaCity_Frlg/events.inc` | Low |
| 9 | **Delete the 11 FRLG Safari Zone maps.** From `map_groups.json`: the 9 `SafariZone_*_Frlg` in `gMapGroup_Dungeons_Frlg`, the 2 `FuchsiaCity_SafariZone_*_Frlg` in `gMapGroup_IndoorFuchsia_Frlg`. Then remove `plastic_ox_kanto_maps.inc:57-65, 156, 158` (the **live** include path — `event_scripts.s:704-712, 943, 945` are already dead inside `.if IS_FRLG`), plus the orphan labels they leave behind: `item_ball_scripts_frlg.inc:197-240, 523` (13 `SafariZone_*_EventScript_Item*`) and `fame_checker_frlg.inc:115-119`. Drop their `MAP_*` defines from `required_map_defines.json`. | see §8 step 2 | Low |
| 10 | **Preserve the Warden trade.** `FuchsiaCity_WardensHouse_Frlg/scripts.inc:8,28` gates a `ITEM_GOLD_TEETH` exchange on `FLAG_HIDE_SAFARI_ZONE_WEST_GOLD_TEETH`, set only by `SafariZone_West_Frlg`. Deleting the map silently kills the trade — either move the item ball to a surviving map or retire the NPC. | `data/maps/FuchsiaCity_WardensHouse_Frlg/` | Low |
| 11 | **Reclaim the 11 Kanto `FLAG_HIDE_SAFARI_ZONE_*` names** (`include/constants/flags.h:1855-1865`, mirrored at `flags_frlg.h:364-374, 446`). No ROM saving, but they are a save-file surface if you renumber flags. | `include/constants/flags.h` | Low |
| 12 | **Delete the Hoenn Safari Zone maps (optional, separate pass).** ⚠ `src/pokedex_area_screen.c:45` hard-codes `#define MAP_GROUP_SPECIAL_AREA MAP_GROUP(MAP_SAFARI_ZONE_NORTHWEST)` — **this will not compile** if `SafariZone_Northwest` leaves `map_groups.json`. Repoint it first. Also `src/item_use.c:1616-1621` (`IsValidLocationForVsSeeker`) lists all 6 Hoenn safari maps, and `src/landmark.c:39,238` has `Landmark_SafariZoneEntrance` on the Route 121 list. | `src/pokedex_area_screen.c:45`, `src/item_use.c`, `src/landmark.c`, `data/event_scripts.s:491-504` | **High — build-breaking** |
| 13 | **Delete the dead `graphics/map_preview/safari_zone/` (14,718 B on disk).** `include/config/map_preview_screen.h:4` sets `MPS_ENABLE_MAP_PREVIEWS IS_FRLG` = 0, so the whole map-preview screen is already off; `sSafariZoneMapPreviewTiles` (4,772 B) + tilemap (364 B) are linked but unreachable. `MUS_SAFARI_ZONE` and `graphics/door_anims/safari_zone{,_frlg}.png` become removable with the maps. | `src/data/graphics/`, `sound/` | Low |
| 14 | **Do NOT touch** `src/safari_zone.c`, `include/safari_zone.h`, `gNumSafariBalls`, `gSafariZoneStepCounter`, `SafariZoneTakeStep`, `SafariZoneRetirePrompt`, `CB2_EndSafariBattle`, `DoSafariBattle`, `BATTLE_TYPE_SAFARI`, `HandleAction_SafariZoneBallThrow/Run`, `data/scripts/safari_zone.inc`'s Pokéblock section, `ITEM_SAFARI_BALL`, `gObjectEventPic_SafariBall`, `src/pokeblock.c`, `src/plastic_ox_contest.c`. | — | — |

### 7.5 Verdict: can the FRLG Safari Zone maps be dropped entirely?

> **STATUS: EXECUTED 2026-10-02 (Decision log D1).** The answer below was "yes"; the user
> approved it and all 11 maps are gone. See D1 for what was actually deleted, the measured
> saving (28,072 B vs the 27,644 B predicted here) and the fourth breakage — **warp-id
> renumbering** — that this section failed to enumerate.

**Yes — and the evidence is stronger than "it is safe".** Three independent reasons:

1. **The engine does not care.** It is Emerald-native and map-agnostic (§7.1). No FRLG map id
   appears in `src/safari_zone.c`, `src/battle_setup.c`, `src/battle_util.c`, or anywhere else in
   the C layer.
2. **They carry no content.** The 4 route maps have **0 encounter slots in the ROM** (tables behind
   `#ifdef FIRERED`). The 4 rest houses share one 13×11 layout. The 9 interiors total 16,644 B of
   blockdata and ~2.7 KB of script text.
3. **The facility is already broken.** Running out of balls or time warps the player to
   `MAP_ROUTE121_SAFARI_ZONE_ENTRANCE`, outside the closure (§7.0).

The only true breakages on removal are mechanical, and all three are enumerable:

| # | breakage | fix |
|---|---|---|
| 1 | **Build error:** `FuchsiaCity_Frlg/map.json` names 2 deleted `dest_map`s | remove `warp_def`s at `events.inc:26, 29` (step 8) |
| 2 | **Build error:** `plastic_ox_kanto_maps.inc:57-65, 156, 158` `.include` deleted `scripts.inc` | delete the 11 include lines (step 9) |
| 3 | **Silent:** `FuchsiaCity_WardensHouse_Frlg` Gold Teeth trade dies | relocate the item or retire the NPC (step 10) |
| 4 | **Silent, NOT enumerated when this section was written:** removing breakage 1's two `warp_def`s renumbers every later `FuchsiaCity_Frlg` warp, invalidating 20 `dest_warp_id`s in 7 interiors | remap `1→0, 2→1, 4→2, 5→3, 6→4, 7→5, 8→6, 9→7, 10→8`. See D1. |

Plus 2 unrelated-but-easy extras: the dead `graphics/map_preview/safari_zone/` (14,718 B disk) and
`data/scripts/safari_zone.inc`'s dead Pokéblock feeder scripts (`:58-88`, ~1.5 KB).

**Savings: 27,644 B** (20,225 for the 9 interiors + 3,107 for the 2 Fuchsia buildings + 4,312
`gTileset_SafariZoneBuilding` cascade) — **0.5% of the free tail.** The reason to do it is
*design coherence*: it removes the region's second, competing, non-functional facility, fixes a
live soft-lock, and clears the "facility state machine" blind spot from the warp playtest. It is
**not** a ROM-space play. If the objective is bytes, the Battle Frontier is **11× larger for the same
amount of work**.

**Sequencing note:** steps 4 and 5 (§7.4) are gameplay fixes that are worth doing **regardless** of
whether you ever delete the maps. The broken exit warp and the contest/safari step-counter collision
are live bugs in the current build.

---

## 8. Recommended execution order

> ⚠ **This table is a reference list, not a schedule.** Per Decision log **D2** the user
> postponed every step except **step 3**, which was executed on 2026-10-02 (D1). Read the
> "frees" column as a *measured potential*, not an approved plan.

| step | action | frees | risk | notes |
|---|---|--:|---|---|
| **0** | Fix the Safari exit bug + the contest/safari step collision (§7.4 steps 4-5) | 0 B | Medium | Gameplay fixes worth doing regardless of trimming. Still open: the exit-warp half was made moot by D1 (the `#if IS_FRLG` arm is gone); the contest/safari step-counter collision is **still live**. |
| **1** | Prune the 42 emitted-but-unreferenced layouts from `layouts.json` (§3.1b) | **55,482** | **Low** | No map, script, tileset or code reference. Best risk/reward in the audit. |
| **2** | Battle Frontier: drop 47 maps from `map_groups.json`, then gate the code | 305,782 (map) + ~343,000 (code) | Medium | Biggest single win, ~630 KB. Touches the save block (`frontier` field) and TV. |
| **3** | Safari Zone → National Park (§7.4) | 27,644 (map) + 14,718 (disk art) | Low | ✅ **DONE 2026-10-02** (D1). Measured 28,072 B. Closure 417 → 406 maps. |
| **4** | Trainer slide banners: `#if`-out `src/trainer_slide.c` + `sTrainerSlides` | ~364,000 | Low | Purely decorative; verify no story script uses a slide-in. |
| **5** | `sBardSoundTemplates_Pokemon` + `bard_music.c` | ~241,000 | Low | `plastic_ox_contest.c` is unrelated and unaffected. |
| **6** | Secret Base: drop 24 maps (free 15,960 of tileset) | 33,212 | Low | To also free `gTileset_SecretBase`/`RedCave` (20,112 B) you must strip `src/decoration.c:1956-2146`. |
| **7** | Battle Tents: drop 9 maps | 27,581 | Low | Not in the warp closure. |
| **8** | Contest halls: drop 22 maps | 46,736 | Medium | Keep `plastic_ox_contest.c` — it is the National Park's, not the Contest Hall's. |
| **9** | Link facilities: drop 8 maps, cascade tilesets | 39,693 | Medium | `UnionRoom`/`UnionRoom_Frlg` *are* in the warp closure — needs a warp repoint. Do **not** touch `pokemon_storage_system`. |
| **10** | Hoenn Safari Zone: drop 7 maps + `Route121_SafariZoneEntrance` | 23,733 | **High** | **Build-breaking**: `src/pokedex_area_screen.c:45` hard-codes `MAP_GROUP(MAP_SAFARI_ZONE_NORTHWEST)`. Repoint first. |
| **11** | Dead tilesets already linked (§3.2) | 177,100 | Low | 123,468 B of it is HNS/Johto content you may still want — treat as "parked", not "deleted". |
| **12** | Trainer Hill: `#if`-out `src/trainer_hill.c` | ~45,000 | Low | Its 12 maps are already NULL; the code is live but unreachable. |
| **13** | Minigames (`dodrio`, `slot`, `roulette`, `pokemon_jump`, `berry_blender/crush`) | ~162,000 | Medium | Pokéblock-adjacent. |
| **14** | Trade / union room / recorded battle | ~148,000 | High | Verify in-game trades first. |
| **15** | De-opt the 186 `layout_version: "frlg"` maps from `map_groups.json` | **0 B** | Low | Hygiene only. It is a map-id renumbering for no gain — do last, or skip. |

**Steps 1-5 alone: ~1.64 MB**, which is a third of the current 5.01 MB free tail. Steps 1-9 add
another ~0.47 MB. Steps 1-14 reach roughly **2.1 MB**.

For reference, the much larger `ROM_SPACE_AUDIT.md` §2 lever (disabling `P_GEN_4..9_POKEMON`,
~8.7 MB from cries and sprites) remains untouched by this audit and dwarfs everything here — but
it is a content decision, not a trim.

---

## 9. Measurement method (reproducible)

`plastic_ox/agent/ROM_SPACE_MEASURE.py` re-derives every number in this document. Method:

1. **Free tail** — scan `pokeemerald.gba` backwards for the last non-`0xFF` byte. No linker map
   parsing needed.
2. **Per-object code** — `arm-none-eabi-size -A build/emerald/**/*.o`, summing `.text + .rodata + .data`
   per object. (This is the method `ROM_SPACE_AUDIT.md` §7 recommends.)
3. **Per-symbol data** — `arm-none-eabi-nm --size-sort -S pokeemerald.elf`.
4. **Blockdata** — parse `data/layouts/layouts.inc` for the `<name>_Layout_Blockdata::` /
   `.incbin` pairs that are *actually emitted*, dedupe by path, and stat the file. Cross-check:
   693 emitted layouts, 1,388 `.incbin`s, 1,149,548 B — matches `maps.o`'s 1,204,664 B once
   borders, 851 map headers (23,828 B) and 3,072 B of connections are added.
5. **Map events** — count macros per `data/maps/*/events.inc` and multiply by the sizes in
   `asm/macros/map.inc` (object_event 24, warp_def 8, coord_event 16, bg_event 12, connection 12,
   map_events 20). Model 172,084 B vs actual 162,796 B → 5.7% over, treat as ±6%.
6. **Scripts** — do **not** estimate from source bytes. Every `EventScript_*` / `Text_*` /
   `Movement_*` label is an exported ELF symbol, so attributing `[label, next_symbol)` spans is
   exact. This is how the 162,742 B Battle Frontier figure and the 20,225 B FRLG Safari Zone
   figure were obtained.
7. **Tilesets** — a tileset is live iff it is the `primary_tileset` or `secondary_tileset` of a
   layout that is (a) in `layouts.json`, (b) passes the `MAP_VERSION` gate, and (c) emitted in
   `layouts.inc`. `--gc-sections` then guarantees the rest cost 0 B. Cascade per family by
   re-running reachability with the family removed.
8. **Compile gate** — `data/maps/headers.inc` lists exactly which opted-in maps produced a
   compiled header. 851 of 1,037.

**Known uncertainties:**
- Map-event column is ±6% (padding).
- Feature code/data columns assume clean object removal; in practice a few shared helpers
  (`battle_anim_*`, `field_door.c` references `gTileset_BattleArena` at
  `src/field_door.c` per `include/constants/metatile_labels.h`) will resist full removal.
- "newly-dead tileset" cascades assume no other map later re-adopts the tileset. Verify with a
  rebuild + `audit_imports.py` after each step.

**Per the map-port skill, re-run the deterministic import audit after any edit:**
```sh
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py \
  /home/eddie/repos/poke-plastic-ox
```
