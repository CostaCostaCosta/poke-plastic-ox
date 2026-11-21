# ECRUTEAK CITY import — completion report

Finishes the interrupted ECRUTEAK CITY port: validates the ten rooms the previous
session imported, fixes four defects it left behind, rebuilds the ROM and
re-runs both emulator verification legs.

* **ROM under test:** `pokeemerald.gba` @
  `202f8e119f12bbb9fdab0800692d91b442e0a712163eba10027e3e060979a0b3`
  (32 MiB, head `07fa6a3a36`)
* **Previous ROM:** `c1fb0b62922ac24e028c3ca59cf103d38a71b0d3bd3592eb87c3ed975e7ba2e9`
* **Donor:** `/home/eddie/repos/pokehns-expansion` @ `44f50eedefe58691b0444973e4138e9190d8fafc`
* **Importer:** `plastic_ox/alpha/import_ecruteak.py` + `plastic_ox/alpha/ecruteak.py`
  (idempotent — re-running reproduces the tree exactly)

## 1. What was imported

Ten interiors and gatehouses into `gMapGroup_PlasticOxInteriors` (now 55 entries),
plus the city door rewiring in `EcruteakCity_hns`:

| map | warps | objects | notes |
|---|--:|--:|---|
| `EcruteakCity_Gym_hns` | 107 | 6 | donor has 108; one duplicated tile deduped |
| `EcruteakCity_House1_hns` | 1 | 0 | both donor NPCs stand on furniture metatiles |
| `EcruteakCity_House2_hns` | 1 | 1 | |
| `EcruteakCity_Mart_hns` | 1 | 3 | |
| `EcruteakCity_PokemonCenter_hns` | 1 | 5 | nurse reuses `Pox_Heal` |
| `EcruteakCity_SageOffice1_hns` | 2 | 3 | exit + donor link into OFFICE 2 |
| `EcruteakCity_SageOffice2_hns` | 1 | 0 | donor warp 0 dropped (BELLCHIME TRAIL absent) |
| `EcruteakCity_Theater_hns` | 1 | 10 | donor `ROCKET_M` and `PSYDUCK` dropped |
| `Gate_EcruteakCity_Route38_hns` | 2 | 1 | mutual pair with `Route38_hns` |
| `Gate_EcruteakCity_Route42_hns` | 1 | 1 | **ROUTE 42 is not in this ROM** |

Layout binaries are byte-identical to the donor; all ten keep
`"layout_version": "hns"` and `"include_in_versions": ["emerald"]`.
`region` is `REGION_HOENN`, `game_version` is stripped, music is remapped per
`IMPORT_GUIDE.md` §4, and every object-event `graphics_id` resolves in
`include/constants/event_objects.h`.

## 2. Defects found and fixed

### 2.1 Gym warps pointed at a city warp index that does not exist

`EcruteakCity_Gym_hns` warp 0 still carried the donor's
`dest_warp_id = "13"` into `EcruteakCity_hns`. Wave 3 had already reduced the
city to 10 warps, so id 13 was out of bounds — landing in the gym would have
teleported the player through uninitialised memory. The same class of bug hit
`EcruteakCity_SageOffice1_hns` warp 1, which pointed at `SAGE_OFFICE2` warp 1
when that room's leading warp had been dropped and only index 0 survived.

`ecruteak.install()` now translates donor warp ids by **coordinate** rather than
by index: the donor city warp table and each room's
`donor_index_to_converted` map are recorded in
`plastic_ox/alpha/ecruteak/source_manifest.json`, and any warp still carrying a
donor id is retargeted onto the tile the donor meant. Result: gym → city warp 4
(`20,48`), OFFICE 1 → OFFICE 2 warp 0. An unresolvable destination is now a hard
`SystemExit` instead of a silent bad index.

### 2.2 `MB_MT_PYRE_HOLE` in the gym would have fired a FALLARBOR story beat

This is the real "merge error" behind the 107 warp events. hns reuses
`MB_MT_PYRE_HOLE` for the gym's shadow floor — 590 of the gym's 816 metatiles.
In this ROM that behaviour is hijacked:
`TryStartWarpEventScript` (`src/field_control_avatar.c:983`) runs
`EventScript_FallDownHoleMtPyre` for it, ignoring the map's warp event. Every
step inside the gym would have fired an unrelated Hoenn story script.

The gym tileset is used by no other layout, so the fix is local and idempotent
(`BEHAVIOR_PATCH` in the importer): all 27 `MB_MT_PYRE_HOLE` entries of
`gTileset_EcruteakCity_Gym_Hns` become `MB_NON_ANIMATED_DOOR` — the engine's
plain "step onto me and warp" behaviour, with no door animation and no special
script. The 106 shadow warps now fire exactly as the donor intends.

A sweep of all 99 HNS layouts confirms the gym was the **only** user of a
story-hijacking behaviour (`MB_MT_PYRE_HOLE`, `MB_MOSSDEEP_GYM_WARP`,
`MB_BATTLE_PYRAMID_WARP`, `MB_LAVARIDGE_GYM_*`, `MB_AQUA_HIDEOUT_WARP`,
`MB_UNION_ROOM_WARP`).

### 2.3 The reachability guard deleted the nurse

`WALKABLE` omitted door and arrow-warp behaviours, so every interior's exit tile
read as solid and the "an NPC must never gate a room" check (IMPORT_GUIDE
pitfall 2) stripped NPCs until the room passed. It deleted the **Pokémon Center
nurse and Chansey** (they stand against a solid counter) and both gate officers.
Two corrections:

* door and arrow-warp metatiles are walkable for pathing — the engine lets the
  player stand on them, it just warps them the moment they step;
* the "can the player talk to this NPC" test now accepts *any* reachable
  neighbour instead of only the tile directly below.

Recovered: PC nurse + Chansey, both gate officers, `HOUSE2`'s resident, and the
mart's clerk. `HOUSE1` still loses both of its NPCs — in the donor they stand on
`MB_HOLDS_LARGE_DECORATION` / `MB_IMPASSABLE_WEST` furniture with no walkable
neighbour at all.

### 2.4 An NPC was parked on the theatre door

`EcruteakCity_hns` warp 3 (theatre, `39,40`) had `OBJ_EVENT_GFX_SILVER_HNS`
standing on the door metatile. Object events block movement, so the door was
sealed in both directions — this is a donor placement, not a port bug. `SILVER`
moves one tile north to `39,39`, facing back into the door (`NPC_SHIFTS`).

### 2.5 Two build-blocking data errors

* `DIALOGUE` strings were written into `.string "..."` with **literal** newlines
  instead of `\n`, so `preproc` aborted on every Ecruteak `scripts.inc`. Now
  escaped.
* `Gate_EcruteakCity_Route42_hns` kept `region_map_section: MAPSEC_ROUTE_42`,
  which does not exist here (ROUTE 42 is not in this ROM) — `MAPSEC_ECRUTEAK_CITY`
  via `REGION_MAP_SECTION`.

## 3. Deliberate omissions (with reasons)

| item | decision |
|---|---|
| ROUTE 42 | **Not in this ROM** — no `Route42_hns`, no `MAPSEC_ROUTE_42`. The ROUTE 42 gatehouse keeps only its city-facing door and charts under ECRUTEAK CITY. Its ROUTE 38 twin is fully wired: `Route38_hns (43,16) ↔ gate (1,5)`, both `MB_EAST_ARROW_WARP`, verified mutual. |
| City → SAGE OFFICE 2 door `(36,16)` | **Dropped.** In our copy of the city this tile is a wall metatile with all four neighbours solid, so nothing can stand next to it and `MB_NORMAL` can never fire a warp — the verifier confirms "no standable approach to warp (36,16)". hns fires warps on plain tiles; this ROM does not. OFFICE 2 stays reachable through the donor's own interior link from OFFICE 1 (verified in the emulator: city → OFFICE 1 `(13,8)`, OFFICE 1 → OFFICE 2 `(4,15)`, OFFICE 2 → OFFICE 1). |
| Burned Tower `(22,14)` / Tin Tower `(37,16)` | Already absent from this region; not part of this import. |
| Gym warps 1–106 | Kept — these are the donor's shadow-maze reset tiles, not an artefact. |

## 4. Verification

### 4.1 Build

```
make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
```

Green. ROM region 28,283,676 / 33,554,432 B used (84.29 %), EWRAM 86.44 %,
IWRAM 87.24 %.

### 4.2 Deterministic HNS audit

```
python3 .agents/skills/plastic-ox-map-port/scripts/audit_imports.py .
audited 99 HNS layouts
HNS layout metadata and asset bounds: PASS
```

### 4.3 Static checks (no emulator)

* Every donor warp **tile** survives except the two documented drops; every
  cross-map `dest_warp_id` is in range for its destination.
* Live-grid BFS: all 11 Ecruteak maps plus `Route38_hns` — every warp reachable
  from an entry warp, every NPC reachable from a walkable neighbour. **0
  problems.**
* `test_warps_v1.py --static-only`: **static warp findings: 0** (was 1).

### 4.4 Map-load check

```
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_warps_v1.py \
  --load-only --json plastic_ox/agent/warp_playtest_ecruteak_loadcheck.json
```

| metric | run 7 (post-cut baseline) | this run |
|---|--:|--:|
| maps in the closure | 406 | **417** |
| maps that load and yield a usable grid | 406 / 406 | **417 / 417** |
| load failures | 0 | **0** |

The +11 is the ten new interiors plus `Route38_hns`, which was **not reachable at
all** before this change — the gatehouse is what puts ROUTE 38 back on the map.
All eleven Ecruteak maps are present in the closure with `ok: true`.

### 4.5 Targeted warp sanity (`--only Ecruteak`, `--exclude BattleFrontier`)

```
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_warps_v1.py \
  --only Ecruteak --exclude BattleFrontier \
  --load-report plastic_ox/agent/warp_playtest_ecruteak_loadcheck.json \
  --json plastic_ox/agent/warp_playtest_ecruteak.json
```

maps 11 · warp events 127 · connections 1 · Surf expansion enabled ·
elapsed 136 s · 11 reboots · **dynamic: OK 21, ISSUE 102, PARTIAL 4**

Breakdown:

| leg | result |
|---|---|
| all 9 `EcruteakCity_hns` doors (PC, mart, house 1/2, theatre, gym, office 1, both gates) | **9 / 9 OK** |
| every `MAP_DYNAMIC` interior exit (house 1/2, mart, PC, theatre, both gates) | **7 / 7 OK** |
| `EcruteakCity_Gym_hns (10,46) ↔ EcruteakCity_hns (20,48)` | **mutual, OK** |
| `Gate_EcruteakCity_Route38_hns (1,5) ↔ Route38_hns (43,16)` | **OK** |
| OFFICE 1 `(16,1)` → OFFICE 2 `(4,15)` → OFFICE 1 | **OK** |
| gym warps 1–106 (shadow reset → `(10,43)`) | 101 ISSUE + 4 PARTIAL — **by design**, see below |
| `EcruteakCity_SageOffice1_hns (13,8)` MAP_DYNAMIC return | 1 ISSUE — **harness artefact**, see below |

**Gym shadow warps (105 non-OK rows).** These are the donor's own mechanic: 106
floor metatiles carry a warp back to `(10,43)`. The harness classifies a warp as
a failure when the return leg does not put the player back on the *origin* tile —
impossible here, because the destination *is* `(10,43)`. Every one of them
demonstrably fires (the harness logs the player being moved to `(10,43)`), which
is exactly the donor behaviour. The 4 PARTIAL rows are the same self-loop at
`(10,43)`, where no approach direction can re-trigger it.

**Sage Office 1 MAP_DYNAMIC row.** The harness enters a map by warp-injection,
which does not set `gSaveBlock1Ptr->dynamicWarp`, so `MAP_DYNAMIC` resolved a
stale destination left by the previous test. Real play is unaffected:
`SetupWarp` (`src/field_control_avatar.c:1098`) calls `SetDynamicWarp` whenever
the destination warp points back with `MAP_DYNAMIC`. Confirmed by hand in the
emulator — city `(39,23)` → UP onto the OFFICE 1 door `(39,22)` lands the player
in `EcruteakCity_SageOffice1_hns` at `(13,8)`, i.e. the door fires.

### 4.6 Round trips walked by hand (mGBA)

| leg | result |
|---|---|
| `EcruteakCity_hns (39,23)` → UP `(39,22)` | `EcruteakCity_SageOffice1_hns (13,8)` ✓ |
| OFFICE 1 `(16,2)` → UP `(16,1)` | `EcruteakCity_SageOffice2_hns (4,15)` ✓ |
| gym `(10,46)` ↔ city `(20,48)` | mutual ✓ (harness) |

## 5. Artefacts

| file | what |
|---|---|
| `plastic_ox/alpha/import_ecruteak.py` | donor → Plastic-Ox converter (now with behaviour patch, warp retargeting, corrected reachability) |
| `plastic_ox/alpha/ecruteak.py` | idempotent `install()`: city doors, NPC shift, dead-door drop, cross-map warp retargeting, script includes |
| `plastic_ox/alpha/ecruteak/source_manifest.json` | donor revision, per-map source/converted warps + objects, layout SHA-256s, `donor_city_warps`, `donor_index_to_converted`, `behavior_patches` |
| `plastic_ox/agent/warp_playtest_ecruteak_loadcheck.json` | 417 per-map load verdicts |
| `plastic_ox/agent/warp_playtest_ecruteak.json` | 127 targeted warp results |
| `plastic_ox/agent/warp_playtest_ecruteak{,_loadcheck}.log` | harness stdout |

## 6. Reproduce

```sh
cd /home/eddie/repos/poke-plastic-ox
python3 plastic_ox/alpha/import_ecruteak.py
make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
sha256sum pokeemerald.gba   # 202f8e119f12bbb9fdab0800692d91b442e0a712163eba10027e3e060979a0b3
```