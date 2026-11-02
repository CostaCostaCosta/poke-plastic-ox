# WARP_PLAYTEST_V1_REPORT — warp-transition playtest (run 3)

**Current handoff:** see the **RUN 7 (POST-CUT)** section at the end of this file — it
covers the ROM built after the FRLG Safari Zone removal (`c1fb0b62`). Runs 3, 5 and 6
below are historical results from earlier ROM builds.

ROM: `pokeemerald.gba` @ `04b27389ca` (read-only). Run started 2026-10-02 02:11:20, emulator time 291.5s, 19 emulator reboots.

Reusable harness: `plastic_ox/demo/test_warps_v1.py`. This run is reproduced by:

```sh
# 1. per-map load check (one fresh boot per map, ~8 min)
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_warps_v1.py \
  --load-only --json plastic_ox/agent/warp_playtest_v1_loadcheck.json

# 2. the warp + seam playtest itself (~5 min)
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_warps_v1.py \
  --load-report plastic_ox/agent/warp_playtest_v1_loadcheck.json \
  --exclude BattleFrontier \
  --json plastic_ox/agent/warp_playtest_v1.json

# 3. static extras (ledges, ladders, auto-teleports) and this report
python3 plastic_ox/agent/warp_extras_static.py \
  --json plastic_ox/agent/warp_playtest_v1_extras.json
python3 plastic_ox/agent/warp_report_v1.py \
  --json plastic_ox/agent/warp_playtest_v1.json \
  --loadcheck plastic_ox/agent/warp_playtest_v1_loadcheck.json \
  --extras plastic_ox/agent/warp_playtest_v1_extras.json \
  --out plastic_ox/agent/WARP_PLAYTEST_V1_REPORT.md

# static pre-pass alone (no emulator needed, plain system python3)
python3 plastic_ox/demo/test_warps_v1.py --static-only
```

Supporting artefacts: `plastic_ox/agent/warp_playtest_v1_loadcheck.json` (map load verdicts), `plastic_ox/agent/warp_playtest_v1_extras.json` (ledge/ladder/auto-teleport static analysis), `plastic_ox/agent/warp_report_v1.py` (this document's generator), `plastic_ox/demo/shots/warp_v1/` (screenshots for ISSUE rows).

## 1. Test set

* **417 maps** in the story-reachable closure, **1278 warp events**, **86 map connections**.
* Closure rule: seeds are the `region_v7.py` `ANCHORS`, the `story_manifest.json` trigger maps and the `region_manifest.json` transition endpoints, plus the retained donor rooms listed in `plastic_ox/agent/audit_warp_connections.py`; the set is then closed over `warp_events[].dest_map` and `connections[].map`.
* The closure is much larger than the ~38-map authored layer because the hns/Plastic-Ox towns sit **on top of the imported FRLG Kanto base**: `PalletTown_Frlg`, `Route101`, `OldaleTown`, `Route2_Frlg`, `Route4_Frlg` are all `ANCHORS`, so Pallet→Route101→Oldale→Route29→Cherrygrove and the whole donor Kanto graph below them are live, story-reachable content.

| tier | maps | warps/seams | OK | PARTIAL | ISSUE | ERROR | UNTESTED |
|---|---|---|---|---|---|---|---|
| donor facility (vanilla) | 74 | 240 | 29 | 2 | 14 | 0 | 195 |
| donor town/cave (vanilla base) | 218 | 818 | 116 | 0 | 20 | 0 | 682 |
| other / unclassified base | 62 | 163 | 137 | 3 | 23 | 0 | 0 |
| plastic-ox authored | 2 | 2 | 2 | 0 | 0 | 0 | 0 |
| region trail endpoint | 14 | 54 | 29 | 0 | 13 | 0 | 12 |
| story-trigger map | 21 | 87 | 77 | 0 | 1 | 0 | 9 |
| **total** | **391** | **1364** | **390** | **5** | **71** | **0** | **898** |

## 2. Method and convention oracle

For every warp the harness boots the ROM, opens every badge/story flag, disables wild encounters, warp-injects a run-up tile 1-5 tiles short of the warp on the correct side, and then **holds a real direction key** so the engine's own `TryDoorWarp`/`TryArrowWarp`/ladder path fires.

Assertions per warp:

1. destination map id == `dest_map`;
2. landing tile == the `dest_warp_id` warp's `(x,y)`, sampled the exact frame the saveblock location flips;
3. arrival facing == the engine's own rule, transcribed from `GetAdjustedInitialDirection()` (`src/overworld.c:1090`): `MB_DEEP_SOUTH_WARP`→UP, doors/`MB_NON_ANIMATED_DOOR`/`MB_WATER_DOOR`→DOWN, `MB_{NORTH,SOUTH,EAST,WEST}_ARROW_WARP`→ the opposite compass direction, directional stairs→E/W, `MB_LADDER`→keep, everything else→DOWN;
4. the landing tile is standable, or is one of the transition tiles the engine itself spawns the player on top of (doors, arrow warps, ladders, stairs, escalators, holes);
5. softlock probe: the player can immediately step off the tile they settled on;
6. return leg: every legal side of the return warp is tried and the exit must land back in the source map on the source door (1 tile of tolerance, for multi-lane doors and for the single carry-over step a finished warp grants).

Every map connection is also walked **in both directions** off the map edge. pokeemerald connections are seamless camera scrolling, not warps: `FillNorth/South/West/EastConnection` copy `MAP_OFFSET` rows/cols into the border strip and `CameraMove()` hands the map over when the camera steps past the grid border, with the landing fixed by `SetPositionFromConnection()`. The harness predicts that landing from the engine source and compares.

### Note on the Gen 3 door/step convention (evidence)

Two facts were measured rather than assumed:

* **Exiting a building lands the player *in* the doorway, then the engine carries them one tile onto the doorstep.** The declared landing tile is the door tile itself (`MB_ANIMATED_DOOR`, collision 1) and the player comes to rest one tile below it facing DOWN. Net effect matches the Gen 3 rule "exiting puts you outside, one tile below the door, facing down".
* **Entering a building lands the player on the interior arrow-warp tile facing *away* from the door** (canonical UP for a `MB_SOUTH_ARROW_WARP` threshold), *not* facing down. Every interior in this region follows that, including the vanilla FRLG reference interiors (`PalletTown_PlayersHouse_1F_Frlg`, `CeruleanCity_House1_Frlg`), so the brief's "entering puts the player just inside the door facing down" is **not** what Gen 3 does and the region is consistent with Gen 3 instead.

## 2b. Map load check (one fresh boot per map)

**204 of 391 maps (52%) cannot be loaded by the engine at all.** Each was loaded in its own fresh boot and then inspected: the saveblock does move to the requested map, but `gMapHeader.mapLayout` comes back as a non-ROM value and every block reads back `MAPGRID_UNDEFINED`. The screen goes black (100% black pixels for `CeruleanCity_Frlg`) or the player is frozen, and no further map change is accepted. This is not a warp defect - it is a map-import defect that makes the whole of that subtree untestable.

| symptom | maps |
|---|---|
| gMapHeader.mapLayout garbage | 203 |
| grid never filled | 1 |

| family | unloadable maps |
|---|---|
| Route | 39 |
| SSAnne | 26 |
| Celadon | 21 |
| Cerulean | 14 |
| Saffron | 12 |
| SilphCo | 12 |
| <other> | 11 |
| Fuchsia | 11 |
| Pewter | 9 |
| Safari | 9 |
| Vermilion | 9 |
| Cinnabar | 8 |
| PokemonTower | 7 |
| Rocket | 5 |
| Pokemon | 3 |
| Underground | 3 |
| RockTunnel | 2 |
| PowerPlant | 1 |
| Trade | 1 |
| Union | 1 |

Full list of unloadable maps (also the reason each untested warp below is marked UNTESTED):

```
CeladonCity_Condominiums_1F_Frlg              CeladonCity_Condominiums_2F_Frlg              CeladonCity_Condominiums_3F_Frlg              CeladonCity_Condominiums_RoofRoom_Frlg
CeladonCity_Condominiums_Roof_Frlg            CeladonCity_DepartmentStore_1F_Frlg           CeladonCity_DepartmentStore_2F_Frlg           CeladonCity_DepartmentStore_3F_Frlg
CeladonCity_DepartmentStore_4F_Frlg           CeladonCity_DepartmentStore_5F_Frlg           CeladonCity_DepartmentStore_Elevator_Frlg     CeladonCity_DepartmentStore_Roof_Frlg
CeladonCity_Frlg                              CeladonCity_GameCorner_Frlg                   CeladonCity_GameCorner_PrizeRoom_Frlg         CeladonCity_Gym_Frlg
CeladonCity_Hotel_Frlg                        CeladonCity_House1_Frlg                       CeladonCity_PokemonCenter_1F_Frlg             CeladonCity_PokemonCenter_2F_Frlg
CeladonCity_Restaurant_Frlg                   CeruleanCave_1F_Frlg                          CeruleanCave_2F_Frlg                          CeruleanCave_B1F_Frlg
CeruleanCity_BikeShop_Frlg                    CeruleanCity_Frlg                             CeruleanCity_Gym_Frlg                         CeruleanCity_House1_Frlg
CeruleanCity_House2_Frlg                      CeruleanCity_House3_Frlg                      CeruleanCity_House4_Frlg                      CeruleanCity_House5_Frlg
CeruleanCity_Mart_Frlg                        CeruleanCity_PokemonCenter_1F_Frlg            CeruleanCity_PokemonCenter_2F_Frlg            CinnabarIsland_Gym_Frlg
CinnabarIsland_Mart_Frlg                      CinnabarIsland_PokemonCenter_1F_Frlg          CinnabarIsland_PokemonCenter_2F_Frlg          CinnabarIsland_PokemonLab_Entrance_Frlg
CinnabarIsland_PokemonLab_ExperimentRoom_Frlg  CinnabarIsland_PokemonLab_Lounge_Frlg         CinnabarIsland_PokemonLab_ResearchRoom_Frlg   DiglettsCave_B1F_Frlg
DiglettsCave_NorthEntrance_Frlg               DiglettsCave_SouthEntrance_Frlg               FuchsiaCity_Frlg                              FuchsiaCity_Gym_Frlg
FuchsiaCity_House1_Frlg                       FuchsiaCity_House2_Frlg                       FuchsiaCity_House3_Frlg                       FuchsiaCity_Mart_Frlg
FuchsiaCity_PokemonCenter_1F_Frlg             FuchsiaCity_PokemonCenter_2F_Frlg             FuchsiaCity_SafariZone_Entrance_Frlg          FuchsiaCity_SafariZone_Office_Frlg
FuchsiaCity_WardensHouse_Frlg                 GoldenrodCity_UndergroundSwitches_hns         LavenderTown_Frlg                             LavenderTown_House1_Frlg
LavenderTown_House2_Frlg                      LavenderTown_Mart_Frlg                        LavenderTown_PokemonCenter_1F_Frlg            LavenderTown_PokemonCenter_2F_Frlg
LavenderTown_VolunteerPokemonHouse_Frlg       PewterCity_Frlg                               PewterCity_Gym_Frlg                           PewterCity_House1_Frlg
PewterCity_House2_Frlg                        PewterCity_Mart_Frlg                          PewterCity_Museum_1F_Frlg                     PewterCity_Museum_2F_Frlg
PewterCity_PokemonCenter_1F_Frlg              PewterCity_PokemonCenter_2F_Frlg              PokemonMansion_2F_Frlg                        PokemonMansion_3F_Frlg
PokemonMansion_B1F_Frlg                       PokemonTower_1F_Frlg                          PokemonTower_2F_Frlg                          PokemonTower_3F_Frlg
PokemonTower_4F_Frlg                          PokemonTower_5F_Frlg                          PokemonTower_6F_Frlg                          PokemonTower_7F_Frlg
PowerPlant_Frlg                               RockTunnel_1F_Frlg                            RockTunnel_B1F_Frlg                           RocketHideout_B1F_Frlg
RocketHideout_B2F_Frlg                        RocketHideout_B3F_Frlg                        RocketHideout_B4F_Frlg                        RocketHideout_Elevator_Frlg
Route10_Frlg                                  Route10_PokemonCenter_1F_Frlg                 Route10_PokemonCenter_2F_Frlg                 Route11_EastEntrance_1F_Frlg
Route11_EastEntrance_2F_Frlg                  Route11_Frlg                                  Route12_FishingHouse_Frlg                     Route12_Frlg
Route12_NorthEntrance_1F_Frlg                 Route12_NorthEntrance_2F_Frlg                 Route13_Frlg                                  Route14_Frlg
Route15_Frlg                                  Route15_WestEntrance_1F_Frlg                  Route15_WestEntrance_2F_Frlg                  Route16_Frlg
Route16_House_Frlg                            Route16_NorthEntrance_1F_Frlg                 Route16_NorthEntrance_2F_Frlg                 Route17_Frlg
Route18_EastEntrance_1F_Frlg                  Route18_EastEntrance_2F_Frlg                  Route18_Frlg                                  Route24_Frlg
Route25_Frlg                                  Route25_SeaCottage_Frlg                       Route3_Frlg                                   Route4_Frlg
Route4_PokemonCenter_1F_Frlg                  Route4_PokemonCenter_2F_Frlg                  Route5_Frlg                                   Route5_PokemonDayCare_Frlg
Route5_SouthEntrance_Frlg                     Route6_Frlg                                   Route6_NorthEntrance_Frlg                     Route7_EastEntrance_Frlg
Route7_Frlg                                   Route8_WestEntrance_Frlg                      Route9_Frlg                                   SSAnne_1F_Corridor_Frlg
SSAnne_1F_Room1_Frlg                          SSAnne_1F_Room2_Frlg                          SSAnne_1F_Room3_Frlg                          SSAnne_1F_Room4_Frlg
SSAnne_1F_Room5_Frlg                          SSAnne_1F_Room6_Frlg                          SSAnne_1F_Room7_Frlg                          SSAnne_2F_Corridor_Frlg
SSAnne_2F_Room1_Frlg                          SSAnne_2F_Room2_Frlg                          SSAnne_2F_Room3_Frlg                          SSAnne_2F_Room4_Frlg
SSAnne_2F_Room5_Frlg                          SSAnne_2F_Room6_Frlg                          SSAnne_3F_Corridor_Frlg                       SSAnne_B1F_Corridor_Frlg
SSAnne_B1F_Room1_Frlg                         SSAnne_B1F_Room2_Frlg                         SSAnne_B1F_Room3_Frlg                         SSAnne_B1F_Room4_Frlg
SSAnne_B1F_Room5_Frlg                         SSAnne_CaptainsOffice_Frlg                    SSAnne_Deck_Frlg                              SSAnne_Exterior_Frlg
SSAnne_Kitchen_Frlg                           SafariZone_Center_Frlg                        SafariZone_Center_RestHouse_Frlg              SafariZone_East_Frlg
SafariZone_East_RestHouse_Frlg                SafariZone_North_Frlg                         SafariZone_North_RestHouse_Frlg               SafariZone_SecretHouse_Frlg
SafariZone_West_Frlg                          SafariZone_West_RestHouse_Frlg                SaffronCity_Connection_Frlg                   SaffronCity_CopycatsHouse_1F_Frlg
SaffronCity_CopycatsHouse_2F_Frlg             SaffronCity_Dojo_Frlg                         SaffronCity_Frlg                              SaffronCity_Gym_Frlg
SaffronCity_House_Frlg                        SaffronCity_Mart_Frlg                         SaffronCity_MrPsychicsHouse_Frlg              SaffronCity_PokemonCenter_1F_Frlg
SaffronCity_PokemonCenter_2F_Frlg             SaffronCity_PokemonTrainerFanClub_Frlg        SilphCo_10F_Frlg                              SilphCo_11F_Frlg
SilphCo_1F_Frlg                               SilphCo_2F_Frlg                               SilphCo_3F_Frlg                               SilphCo_4F_Frlg
SilphCo_5F_Frlg                               SilphCo_6F_Frlg                               SilphCo_7F_Frlg                               SilphCo_8F_Frlg
SilphCo_9F_Frlg                               SilphCo_Elevator_Frlg                         TradeCenter_Frlg                              UndergroundPath_NorthEntrance_Frlg
UndergroundPath_NorthSouthTunnel_Frlg         UndergroundPath_SouthEntrance_Frlg            UnionRoom_Frlg                                VermilionCity_Frlg
VermilionCity_Gym_Frlg                        VermilionCity_House1_Frlg                     VermilionCity_House2_Frlg                     VermilionCity_House3_Frlg
VermilionCity_Mart_Frlg                       VermilionCity_PokemonCenter_1F_Frlg           VermilionCity_PokemonCenter_2F_Frlg           VermilionCity_PokemonFanClub_Frlg
```

## 2c. Static convention extras (ledges, ladders, auto-teleports)

| check | count |
|---|---|
| maps | 417 |
| authored_region_portals | 63 |
| legacy_vanilla_triggers | 160 |
| ledges_on_map_edge | 0 |
| ledge_tiles | 1366 |
| ledges_with_issues | 200 |
| orphan_ladders | 17 |
| orphan_stairs | 227 |
| auto_teleport_events | 223 |
| doors_checked | 322 |

* **Ledges.** 1366 `MB_JUMP_*` tiles are present. 200 of them fail a static one-way check: the approach tile is not walkable (the hop can never be taken, so it is decorative cliff art, not a route) or the landing tile one row down is solid (the player would hop into a wall). None sit on a map-connection seam edge (0 found), so the seam rule "a ledge on a seam hops downward only" is not violated anywhere in the closure.

* **Ladders/stairs without a warp event.** 17 `MB_LADDER` tiles and 227 stair/escalator tiles carry no warp event, so they are bg-event scripts. A warp-driven harness cannot trigger them; they are listed as untestable by design rather than as defects.

* **Auto-teleports.** 223 coordinate/bg events in the closure fire a script. 63 of them are `PoxRegion_*` - the authored `region_v7.py` trail transitions, which are deliberately coordinate-triggered rather than native warps (see `plastic_ox/alpha/region_v7.py`, `LANE_PORTALS`). 160 are inherited vanilla story triggers (rival/grunt cutscene tiles in the FRLG Kanto base). They do not fire during this playtest because the harness never walks over a trigger tile with a story flag unset, but they are the mechanism by which the region portals teleport, and they are the first thing to audit if a "spontaneous" teleport is ever reported.

## 3. Results by map

One section per map that contains at least one warp or connection. `warp` = index into `warp_events`.

### `ArtisanCave_1F`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 17) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (28, 7) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 5) | MB_LADDER | ArtisanCave_B1F | (38, 5) | MB_LADDER | (38, 5) | (38, 5) | UP (KEEP) | yes | same door | **OK** |

* **ArtisanCave_1F[0] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `ArtisanCave_B1F`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (8, 48) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (39, 55) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (38, 5) | MB_LADDER | ArtisanCave_1F | (6, 5) | MB_LADDER | (6, 5) | (6, 5) | UP (KEEP) | yes | same door | **OK** |

* **ArtisanCave_B1F[0] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_BattleArenaLobby`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 12) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (39, 29) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_BattleArenaLobby[0] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_BattleDomeLobby`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (11, 16) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (19, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (12, 16) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (19, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_BattleDomeLobby[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattleDomeLobby[1] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_BattleFactoryLobby`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (9, 11) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (11, 38) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (10, 11) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (11, 38) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_BattleFactoryLobby[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattleFactoryLobby[1] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_BattlePalaceBattleRoom`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (0, 9) | MB_NORMAL | BattleFrontier_BattlePalaceCorridor | (6, 3) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (1, 9) | MB_NORMAL | BattleFrontier_BattlePalaceCorridor | (6, 3) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_BattlePalaceBattleRoom[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattlePalaceBattleRoom[1] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_BattlePalaceCorridor`

*Tier: donor facility (vanilla) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (8, 13) | MB_SOUTH_ARROW_WARP | BattleFrontier_BattlePalaceLobby | (5, 4) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (9, 13) | MB_SOUTH_ARROW_WARP | BattleFrontier_BattlePalaceLobby | (5, 4) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (6, 3) | MB_ANIMATED_DOOR | BattleFrontier_BattlePalaceBattleRoom | (0, 9) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (10, 3) | MB_ANIMATED_DOOR | BattleFrontier_BattlePalaceBattleRoom | (0, 9) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_BattlePalaceCorridor[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattlePalaceCorridor[1] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattlePalaceCorridor[2] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattlePalaceCorridor[3] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_BattlePalaceLobby`

*Tier: donor facility (vanilla) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (12, 11) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (45, 56) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (13, 11) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (45, 56) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 4) | MB_ANIMATED_DOOR | BattleFrontier_BattlePalaceCorridor | (8, 13) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_BattlePalaceLobby[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattlePalaceLobby[1] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattlePalaceLobby[2] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_BattlePikeLobby`

*Tier: donor facility (vanilla) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 12) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (42, 27) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 12) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (42, 27) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (6, 12) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (42, 27) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_BattlePikeLobby[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattlePikeLobby[1] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattlePikeLobby[2] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_BattlePyramidLobby`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 17) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (58, 14) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_BattlePyramidLobby[0] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_BattleTowerBattleRoom`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_SOUTH_ARROW_WARP | BattleFrontier_BattleTowerLobby | (6, 1) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 8) | MB_NORMAL | BattleFrontier_BattleTowerLobby | (6, 1) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_BattleTowerBattleRoom[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattleTowerBattleRoom[1] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_BattleTowerLobby`

*Tier: donor facility (vanilla) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (12, 9) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (16, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (13, 9) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (16, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (6, 1) | MB_ANIMATED_DOOR | BattleFrontier_BattleTowerBattleRoom | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_BattleTowerLobby[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattleTowerLobby[1] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_BattleTowerLobby[2] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_ExchangeServiceCorner`

*Tier: donor facility (vanilla) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 10) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (10, 28) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 10) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (10, 28) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 10) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (10, 28) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_ExchangeServiceCorner[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_ExchangeServiceCorner[1] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_ExchangeServiceCorner[2] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_Lounge1`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 9) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (4, 44) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_Lounge1[0] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_Lounge2`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 7) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (45, 44) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (2, 7) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (45, 44) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_Lounge2[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_Lounge2[1] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_Lounge3`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 9) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (65, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_Lounge3[0] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_Lounge4`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 9) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (53, 44) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_Lounge4[0] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_Lounge5`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 7) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (22, 51) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (2, 7) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (22, 51) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_Lounge5[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_Lounge5[1] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_Lounge6`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 9) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (5, 8) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_Lounge6[0] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_Lounge7`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 9) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (5, 20) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_Lounge7[0] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_Lounge8`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 9) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (14, 51) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_Lounge8[0] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_Lounge9`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 9) | MB_NORMAL | BattleFrontier_OutsideEast | (21, 45) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (2, 9) | MB_NORMAL | BattleFrontier_OutsideEast | (21, 45) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_Lounge9[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_Lounge9[1] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_Mart`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (51, 51) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (51, 51) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_Mart[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_Mart[1] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_OutsideEast`

*Tier: donor facility (vanilla) — 14 warp(s), 1 connection(s), 15 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (16, 14) | MB_ANIMATED_DOOR | BattleFrontier_BattleTowerLobby | (12, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (39, 29) | MB_ANIMATED_DOOR | BattleFrontier_BattleArenaLobby | (7, 12) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (45, 56) | MB_NON_ANIMATED_DOOR | BattleFrontier_BattlePalaceLobby | (12, 11) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (58, 14) | MB_NON_ANIMATED_DOOR | BattleFrontier_BattlePyramidLobby | (7, 17) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (35, 12) | MB_NON_ANIMATED_DOOR | BattleFrontier_RankingHall | (26, 14) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (4, 44) | MB_ANIMATED_DOOR | BattleFrontier_Lounge1 | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (10, 28) | MB_ANIMATED_DOOR | BattleFrontier_ExchangeServiceCorner | (7, 10) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (22, 51) | MB_ANIMATED_DOOR | BattleFrontier_Lounge5 | (1, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (5, 8) | MB_ANIMATED_DOOR | BattleFrontier_Lounge6 | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (65, 31) | MB_ANIMATED_DOOR | BattleFrontier_Lounge3 | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 10 | (14, 51) | MB_ANIMATED_DOOR | BattleFrontier_Lounge8 | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 11 | (21, 45) | MB_NORMAL | BattleFrontier_Lounge9 | (1, 9) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 12 | (3, 51) | MB_ANIMATED_DOOR | BattleFrontier_PokemonCenter_1F | (7, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 13 | (28, 7) | MB_NON_ANIMATED_DOOR | ArtisanCave_1F | (10, 17) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_OutsideEast[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[1] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[2] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[3] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[4] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[5] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[6] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[7] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[8] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[9] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[10] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[11] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[12] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast[13] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideEast conn[0] left/0 -> BattleFrontier_OutsideWest UNTESTED** — 
  * untestable: excluded facility state machine

### `BattleFrontier_OutsideWest`

*Tier: region trail endpoint — 11 warp(s), 1 connection(s), 12 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (42, 27) | MB_NON_ANIMATED_DOOR | BattleFrontier_BattlePikeLobby | (5, 12) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (19, 17) | MB_ANIMATED_DOOR | BattleFrontier_BattleDomeLobby | (11, 16) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (11, 38) | MB_ANIMATED_DOOR | BattleFrontier_BattleFactoryLobby | (9, 11) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (45, 44) | MB_ANIMATED_DOOR | BattleFrontier_Lounge2 | (1, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (51, 51) | MB_ANIMATED_DOOR | BattleFrontier_Mart | (3, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (44, 5) | MB_ANIMATED_DOOR | BattleFrontier_ScottsHouse | (2, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (53, 44) | MB_ANIMATED_DOOR | BattleFrontier_Lounge4 | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (5, 20) | MB_ANIMATED_DOOR | BattleFrontier_Lounge7 | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (26, 65) | MB_NON_ANIMATED_DOOR | BattleFrontier_ReceptionGate | (4, 13) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (26, 61) | MB_SOUTH_ARROW_WARP | BattleFrontier_ReceptionGate | (4, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 10 | (39, 55) | MB_NON_ANIMATED_DOOR | ArtisanCave_B1F | (8, 48) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_OutsideWest[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideWest[1] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideWest[2] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideWest[3] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideWest[4] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideWest[5] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideWest[6] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideWest[7] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideWest[8] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideWest[9] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideWest[10] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_OutsideWest conn[0] right/0 -> BattleFrontier_OutsideEast UNTESTED** — 
  * untestable: excluded facility state machine

### `BattleFrontier_PokemonCenter_1F`

*Tier: donor facility (vanilla) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 8) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (3, 51) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (3, 51) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (1, 6) | MB_UP_ESCALATOR | BattleFrontier_PokemonCenter_2F | (1, 6) | MB_DOWN_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_PokemonCenter_1F[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_PokemonCenter_1F[1] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_PokemonCenter_1F[2] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_PokemonCenter_2F`

*Tier: donor facility (vanilla) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | BattleFrontier_PokemonCenter_1F | (1, 6) | MB_UP_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom | (7, 11) | MB_BRIDGE_OVER_OCEAN | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_PokemonCenter_2F[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_PokemonCenter_2F[1] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_PokemonCenter_2F[2] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_RankingHall`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (26, 14) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (35, 12) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (27, 14) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideEast | (35, 12) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_RankingHall[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_RankingHall[1] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_ReceptionGate`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 13) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (26, 65) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 1) | MB_NON_ANIMATED_DOOR | BattleFrontier_OutsideWest | (26, 61) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_ReceptionGate[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_ReceptionGate[1] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BattleFrontier_ScottsHouse`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 7) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (44, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (3, 7) | MB_SOUTH_ARROW_WARP | BattleFrontier_OutsideWest | (44, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **BattleFrontier_ScottsHouse[0] UNTESTED** — untestable: facility state machine; excluded with --exclude
* **BattleFrontier_ScottsHouse[1] UNTESTED** — untestable: facility state machine; excluded with --exclude

### `BlackthornCity_hns`

*Tier: story-trigger map — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (27, 48) | MB_ANIMATED_DOOR | PokemonCenter_Johto_hns | (7, 8) | MB_SOUTH_ARROW_WARP | (7, 8) | (7, 8) | UP (UP) | yes | same door | **OK** |
| 1 | (16, 48) | MB_ANIMATED_DOOR | Mart_Johto_hns | (4, 7) | MB_SOUTH_ARROW_WARP | (4, 7) | (4, 7) | UP (UP) | yes | same door | **OK** |


### `CeladonCity_Condominiums_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 6 warp(s), 0 connection(s), 6 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (11, 19) | MB_NORMAL | CeladonCity_Frlg | (30, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (12, 18) | MB_SOUTH_ARROW_WARP | CeladonCity_Frlg | (30, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (13, 19) | MB_NORMAL | CeladonCity_Frlg | (30, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (4, 2) | MB_UP_RIGHT_STAIR_WARP | CeladonCity_Condominiums_2F_Frlg | (4, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (12, 2) | MB_UP_RIGHT_STAIR_WARP | CeladonCity_Condominiums_2F_Frlg | (12, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (2, 1) | MB_NON_ANIMATED_DOOR | CeladonCity_Frlg | (30, 4) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_Condominiums_1F_Frlg[0] UNTESTED** — untestable: CeladonCity_Condominiums_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_1F_Frlg[1] UNTESTED** — untestable: CeladonCity_Condominiums_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_1F_Frlg[2] UNTESTED** — untestable: CeladonCity_Condominiums_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_1F_Frlg[3] UNTESTED** — untestable: CeladonCity_Condominiums_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_1F_Frlg[4] UNTESTED** — untestable: CeladonCity_Condominiums_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_1F_Frlg[5] UNTESTED** — untestable: CeladonCity_Condominiums_1F_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_Condominiums_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 2) | MB_DOWN_RIGHT_STAIR_WARP | CeladonCity_Condominiums_1F_Frlg | (4, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (2, 2) | MB_UP_LEFT_STAIR_WARP | CeladonCity_Condominiums_3F_Frlg | (2, 2) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (11, 2) | MB_UP_LEFT_STAIR_WARP | CeladonCity_Condominiums_3F_Frlg | (11, 2) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (12, 2) | MB_DOWN_RIGHT_STAIR_WARP | CeladonCity_Condominiums_1F_Frlg | (12, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_Condominiums_2F_Frlg[0] UNTESTED** — untestable: CeladonCity_Condominiums_2F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_2F_Frlg[1] UNTESTED** — untestable: CeladonCity_Condominiums_2F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_2F_Frlg[2] UNTESTED** — untestable: CeladonCity_Condominiums_2F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_2F_Frlg[3] UNTESTED** — untestable: CeladonCity_Condominiums_2F_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_Condominiums_3F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 2) | MB_DOWN_LEFT_STAIR_WARP | CeladonCity_Condominiums_2F_Frlg | (2, 2) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 2) | MB_UP_RIGHT_STAIR_WARP | CeladonCity_Condominiums_Roof_Frlg | (4, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (12, 2) | MB_UP_RIGHT_STAIR_WARP | CeladonCity_Condominiums_Roof_Frlg | (10, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (11, 2) | MB_DOWN_LEFT_STAIR_WARP | CeladonCity_Condominiums_2F_Frlg | (11, 2) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_Condominiums_3F_Frlg[0] UNTESTED** — untestable: CeladonCity_Condominiums_3F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_3F_Frlg[1] UNTESTED** — untestable: CeladonCity_Condominiums_3F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_3F_Frlg[2] UNTESTED** — untestable: CeladonCity_Condominiums_3F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_3F_Frlg[3] UNTESTED** — untestable: CeladonCity_Condominiums_3F_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_Condominiums_RoofRoom_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 8) | MB_NORMAL | CeladonCity_Condominiums_Roof_Frlg | (2, 12) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | CeladonCity_Condominiums_Roof_Frlg | (2, 12) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 8) | MB_NORMAL | CeladonCity_Condominiums_Roof_Frlg | (2, 12) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_Condominiums_RoofRoom_Frlg[0] UNTESTED** — untestable: CeladonCity_Condominiums_RoofRoom_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_RoofRoom_Frlg[1] UNTESTED** — untestable: CeladonCity_Condominiums_RoofRoom_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_RoofRoom_Frlg[2] UNTESTED** — untestable: CeladonCity_Condominiums_RoofRoom_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_Condominiums_Roof_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 2) | MB_DOWN_RIGHT_STAIR_WARP | CeladonCity_Condominiums_3F_Frlg | (4, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (10, 2) | MB_DOWN_RIGHT_STAIR_WARP | CeladonCity_Condominiums_3F_Frlg | (12, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (2, 12) | MB_NON_ANIMATED_DOOR | CeladonCity_Condominiums_RoofRoom_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_Condominiums_Roof_Frlg[0] UNTESTED** — untestable: CeladonCity_Condominiums_Roof_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_Roof_Frlg[1] UNTESTED** — untestable: CeladonCity_Condominiums_Roof_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Condominiums_Roof_Frlg[2] UNTESTED** — untestable: CeladonCity_Condominiums_Roof_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_DepartmentStore_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 8 warp(s), 0 connection(s), 8 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 15) | MB_NORMAL | CeladonCity_Frlg | (11, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (2, 14) | MB_SOUTH_ARROW_WARP | CeladonCity_Frlg | (11, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (3, 15) | MB_NORMAL | CeladonCity_Frlg | (11, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (9, 15) | MB_NORMAL | CeladonCity_Frlg | (15, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (10, 14) | MB_SOUTH_ARROW_WARP | CeladonCity_Frlg | (15, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (11, 15) | MB_NORMAL | CeladonCity_Frlg | (15, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (6, 1) | MB_ANIMATED_DOOR | CeladonCity_DepartmentStore_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (4, 2) | MB_UP_LEFT_STAIR_WARP | CeladonCity_DepartmentStore_2F_Frlg | (3, 2) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_DepartmentStore_1F_Frlg[0] UNTESTED** — untestable: CeladonCity_DepartmentStore_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_1F_Frlg[1] UNTESTED** — untestable: CeladonCity_DepartmentStore_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_1F_Frlg[2] UNTESTED** — untestable: CeladonCity_DepartmentStore_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_1F_Frlg[3] UNTESTED** — untestable: CeladonCity_DepartmentStore_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_1F_Frlg[4] UNTESTED** — untestable: CeladonCity_DepartmentStore_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_1F_Frlg[5] UNTESTED** — untestable: CeladonCity_DepartmentStore_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_1F_Frlg[6] UNTESTED** — untestable: CeladonCity_DepartmentStore_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_1F_Frlg[7] UNTESTED** — untestable: CeladonCity_DepartmentStore_1F_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_DepartmentStore_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 1) | MB_ANIMATED_DOOR | CeladonCity_DepartmentStore_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (3, 2) | MB_DOWN_LEFT_STAIR_WARP | CeladonCity_DepartmentStore_1F_Frlg | (4, 2) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 2) | MB_UP_RIGHT_STAIR_WARP | CeladonCity_DepartmentStore_3F_Frlg | (9, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_DepartmentStore_2F_Frlg[0] UNTESTED** — untestable: CeladonCity_DepartmentStore_2F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_2F_Frlg[1] UNTESTED** — untestable: CeladonCity_DepartmentStore_2F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_2F_Frlg[2] UNTESTED** — untestable: CeladonCity_DepartmentStore_2F_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_DepartmentStore_3F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 1) | MB_ANIMATED_DOOR | CeladonCity_DepartmentStore_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (9, 2) | MB_DOWN_RIGHT_STAIR_WARP | CeladonCity_DepartmentStore_2F_Frlg | (9, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (3, 2) | MB_UP_LEFT_STAIR_WARP | CeladonCity_DepartmentStore_4F_Frlg | (3, 2) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_DepartmentStore_3F_Frlg[0] UNTESTED** — untestable: CeladonCity_DepartmentStore_3F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_3F_Frlg[1] UNTESTED** — untestable: CeladonCity_DepartmentStore_3F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_3F_Frlg[2] UNTESTED** — untestable: CeladonCity_DepartmentStore_3F_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_DepartmentStore_4F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 1) | MB_ANIMATED_DOOR | CeladonCity_DepartmentStore_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (3, 2) | MB_DOWN_LEFT_STAIR_WARP | CeladonCity_DepartmentStore_3F_Frlg | (3, 2) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 2) | MB_UP_RIGHT_STAIR_WARP | CeladonCity_DepartmentStore_5F_Frlg | (9, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_DepartmentStore_4F_Frlg[0] UNTESTED** — untestable: CeladonCity_DepartmentStore_4F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_4F_Frlg[1] UNTESTED** — untestable: CeladonCity_DepartmentStore_4F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_4F_Frlg[2] UNTESTED** — untestable: CeladonCity_DepartmentStore_4F_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_DepartmentStore_5F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 1) | MB_ANIMATED_DOOR | CeladonCity_DepartmentStore_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (9, 2) | MB_DOWN_RIGHT_STAIR_WARP | CeladonCity_DepartmentStore_4F_Frlg | (9, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (3, 2) | MB_UP_LEFT_STAIR_WARP | CeladonCity_DepartmentStore_Roof_Frlg | (15, 6) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_DepartmentStore_5F_Frlg[0] UNTESTED** — untestable: CeladonCity_DepartmentStore_5F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_5F_Frlg[1] UNTESTED** — untestable: CeladonCity_DepartmentStore_5F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_5F_Frlg[2] UNTESTED** — untestable: CeladonCity_DepartmentStore_5F_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_DepartmentStore_Elevator_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 5) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (2, 6) | MB_NORMAL | MAP_DYNAMIC | - | - | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_DepartmentStore_Elevator_Frlg[0] UNTESTED** — untestable: CeladonCity_DepartmentStore_Elevator_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_DepartmentStore_Elevator_Frlg[1] UNTESTED** — untestable: CeladonCity_DepartmentStore_Elevator_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_DepartmentStore_Roof_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (15, 6) | MB_EAST_ARROW_WARP | CeladonCity_DepartmentStore_5F_Frlg | (3, 2) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_DepartmentStore_Roof_Frlg[0] UNTESTED** — untestable: CeladonCity_DepartmentStore_Roof_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_Frlg`

*Tier: donor town/cave (vanilla base) — 13 warp(s), 2 connection(s), 15 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (34, 21) | MB_ANIMATED_DOOR | CeladonCity_GameCorner_Frlg | (9, 13) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (11, 14) | MB_ANIMATED_DOOR | CeladonCity_DepartmentStore_1F_Frlg | (2, 14) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (15, 14) | MB_ANIMATED_DOOR | CeladonCity_DepartmentStore_1F_Frlg | (10, 14) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (30, 11) | MB_ANIMATED_DOOR | CeladonCity_Condominiums_1F_Frlg | (12, 18) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (48, 11) | MB_ANIMATED_DOOR | CeladonCity_PokemonCenter_1F_Frlg | (7, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (39, 20) | MB_ANIMATED_DOOR | CeladonCity_GameCorner_PrizeRoom_Frlg | (4, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (11, 30) | MB_ANIMATED_DOOR | CeladonCity_Gym_Frlg | (6, 18) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (37, 29) | MB_ANIMATED_DOOR | CeladonCity_Restaurant_Frlg | (6, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (41, 29) | MB_ANIMATED_DOOR | CeladonCity_House1_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (49, 29) | MB_ANIMATED_DOOR | CeladonCity_Hotel_Frlg | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 10 | (29, 5) | MB_NORMAL | CeladonCity_Condominiums_1F_Frlg | (2, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 11 | (30, 4) | MB_SOUTH_ARROW_WARP | CeladonCity_Condominiums_1F_Frlg | (2, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 12 | (31, 5) | MB_NORMAL | CeladonCity_Condominiums_1F_Frlg | (2, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_Frlg[0] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg[1] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg[2] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg[3] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg[4] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg[5] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg[6] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg[7] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg[8] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg[9] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg[10] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg[11] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg[12] UNTESTED** — untestable: CeladonCity_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg conn[0] left/10 -> Route16_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **CeladonCity_Frlg conn[1] right/10 -> Route7_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `CeladonCity_GameCorner_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (9, 13) | MB_SOUTH_ARROW_WARP | CeladonCity_Frlg | (34, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (10, 13) | MB_NORMAL | CeladonCity_Frlg | (34, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (11, 13) | MB_NORMAL | CeladonCity_Frlg | (34, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (15, 2) | MB_DOWN_RIGHT_STAIR_WARP | RocketHideout_B1F_Frlg | (12, 2) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_GameCorner_Frlg[0] UNTESTED** — untestable: CeladonCity_GameCorner_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_GameCorner_Frlg[1] UNTESTED** — untestable: CeladonCity_GameCorner_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_GameCorner_Frlg[2] UNTESTED** — untestable: CeladonCity_GameCorner_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_GameCorner_Frlg[3] UNTESTED** — untestable: CeladonCity_GameCorner_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_GameCorner_PrizeRoom_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 9) | MB_NORMAL | CeladonCity_Frlg | (39, 20) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 8) | MB_SOUTH_ARROW_WARP | CeladonCity_Frlg | (39, 20) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 9) | MB_NORMAL | CeladonCity_Frlg | (39, 20) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_GameCorner_PrizeRoom_Frlg[0] UNTESTED** — untestable: CeladonCity_GameCorner_PrizeRoom_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_GameCorner_PrizeRoom_Frlg[1] UNTESTED** — untestable: CeladonCity_GameCorner_PrizeRoom_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_GameCorner_PrizeRoom_Frlg[2] UNTESTED** — untestable: CeladonCity_GameCorner_PrizeRoom_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_Gym_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 18) | MB_NORMAL | CeladonCity_Frlg | (11, 30) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 18) | MB_SOUTH_ARROW_WARP | CeladonCity_Frlg | (11, 30) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (7, 18) | MB_NORMAL | CeladonCity_Frlg | (11, 30) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_Gym_Frlg[0] UNTESTED** — untestable: CeladonCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Gym_Frlg[1] UNTESTED** — untestable: CeladonCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Gym_Frlg[2] UNTESTED** — untestable: CeladonCity_Gym_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_Hotel_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 10) | MB_NORMAL | CeladonCity_Frlg | (49, 29) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 9) | MB_SOUTH_ARROW_WARP | CeladonCity_Frlg | (49, 29) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 10) | MB_NORMAL | CeladonCity_Frlg | (49, 29) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_Hotel_Frlg[0] UNTESTED** — untestable: CeladonCity_Hotel_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Hotel_Frlg[1] UNTESTED** — untestable: CeladonCity_Hotel_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Hotel_Frlg[2] UNTESTED** — untestable: CeladonCity_Hotel_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_House1_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | CeladonCity_Frlg | (41, 29) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | CeladonCity_Frlg | (41, 29) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | CeladonCity_Frlg | (41, 29) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_House1_Frlg[0] UNTESTED** — untestable: CeladonCity_House1_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_House1_Frlg[1] UNTESTED** — untestable: CeladonCity_House1_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_House1_Frlg[2] UNTESTED** — untestable: CeladonCity_House1_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_PokemonCenter_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 8) | MB_NORMAL | CeladonCity_Frlg | (48, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (7, 8) | MB_SOUTH_ARROW_WARP | CeladonCity_Frlg | (48, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 8) | MB_NORMAL | CeladonCity_Frlg | (48, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (1, 6) | MB_UP_ESCALATOR | CeladonCity_PokemonCenter_2F_Frlg | (1, 6) | MB_DOWN_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_PokemonCenter_1F_Frlg[0] UNTESTED** — untestable: CeladonCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_PokemonCenter_1F_Frlg[1] UNTESTED** — untestable: CeladonCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_PokemonCenter_1F_Frlg[2] UNTESTED** — untestable: CeladonCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_PokemonCenter_1F_Frlg[3] UNTESTED** — untestable: CeladonCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_PokemonCenter_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | CeladonCity_PokemonCenter_1F_Frlg | (1, 6) | MB_UP_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom_Frlg | (7, 11) | MB_BRIDGE_OVER_OCEAN | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter_Frlg | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_PokemonCenter_2F_Frlg[0] UNTESTED** — untestable: CeladonCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_PokemonCenter_2F_Frlg[1] UNTESTED** — untestable: CeladonCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_PokemonCenter_2F_Frlg[2] UNTESTED** — untestable: CeladonCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)

### `CeladonCity_Restaurant_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 9) | MB_NORMAL | CeladonCity_Frlg | (37, 29) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 9) | MB_SOUTH_ARROW_WARP | CeladonCity_Frlg | (37, 29) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (7, 9) | MB_NORMAL | CeladonCity_Frlg | (37, 29) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeladonCity_Restaurant_Frlg[0] UNTESTED** — untestable: CeladonCity_Restaurant_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Restaurant_Frlg[1] UNTESTED** — untestable: CeladonCity_Restaurant_Frlg cannot be loaded by the engine (see load check)
* **CeladonCity_Restaurant_Frlg[2] UNTESTED** — untestable: CeladonCity_Restaurant_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCave_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 8 warp(s), 0 connection(s), 8 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (33, 21) | MB_SOUTH_ARROW_WARP | CeruleanCity_Frlg | (1, 12) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (34, 2) | MB_LADDER | CeruleanCave_2F_Frlg | (33, 4) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (1, 7) | MB_LADDER | CeruleanCave_B1F_Frlg | (5, 7) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (10, 2) | MB_LADDER | CeruleanCave_2F_Frlg | (13, 4) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (5, 15) | MB_LADDER | CeruleanCave_2F_Frlg | (7, 14) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (30, 10) | MB_LADDER | CeruleanCave_2F_Frlg | (26, 9) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (24, 11) | MB_LADDER | CeruleanCave_2F_Frlg | (23, 10) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (2, 4) | MB_LADDER | CeruleanCave_2F_Frlg | (5, 6) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCave_1F_Frlg[0] UNTESTED** — untestable: CeruleanCave_1F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCave_1F_Frlg[1] UNTESTED** — untestable: CeruleanCave_1F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCave_1F_Frlg[2] UNTESTED** — untestable: CeruleanCave_1F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCave_1F_Frlg[3] UNTESTED** — untestable: CeruleanCave_1F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCave_1F_Frlg[4] UNTESTED** — untestable: CeruleanCave_1F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCave_1F_Frlg[5] UNTESTED** — untestable: CeruleanCave_1F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCave_1F_Frlg[6] UNTESTED** — untestable: CeruleanCave_1F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCave_1F_Frlg[7] UNTESTED** — untestable: CeruleanCave_1F_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCave_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 6 warp(s), 0 connection(s), 6 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (33, 4) | MB_LADDER | CeruleanCave_1F_Frlg | (34, 2) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (13, 4) | MB_LADDER | CeruleanCave_1F_Frlg | (10, 2) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (7, 14) | MB_LADDER | CeruleanCave_1F_Frlg | (5, 15) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (26, 9) | MB_LADDER | CeruleanCave_1F_Frlg | (30, 10) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (23, 10) | MB_LADDER | CeruleanCave_1F_Frlg | (24, 11) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (5, 6) | MB_LADDER | CeruleanCave_1F_Frlg | (2, 4) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCave_2F_Frlg[0] UNTESTED** — untestable: CeruleanCave_2F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCave_2F_Frlg[1] UNTESTED** — untestable: CeruleanCave_2F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCave_2F_Frlg[2] UNTESTED** — untestable: CeruleanCave_2F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCave_2F_Frlg[3] UNTESTED** — untestable: CeruleanCave_2F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCave_2F_Frlg[4] UNTESTED** — untestable: CeruleanCave_2F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCave_2F_Frlg[5] UNTESTED** — untestable: CeruleanCave_2F_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCave_B1F_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 7) | MB_LADDER | CeruleanCave_1F_Frlg | (1, 7) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCave_B1F_Frlg[0] UNTESTED** — untestable: CeruleanCave_B1F_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCity_BikeShop_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 9) | MB_NORMAL | CeruleanCity_Frlg | (13, 28) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 8) | MB_SOUTH_ARROW_WARP | CeruleanCity_Frlg | (13, 28) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (6, 9) | MB_NORMAL | CeruleanCity_Frlg | (13, 28) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCity_BikeShop_Frlg[0] UNTESTED** — untestable: CeruleanCity_BikeShop_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_BikeShop_Frlg[1] UNTESTED** — untestable: CeruleanCity_BikeShop_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_BikeShop_Frlg[2] UNTESTED** — untestable: CeruleanCity_BikeShop_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCity_Frlg`

*Tier: donor town/cave (vanilla base) — 14 warp(s), 4 connection(s), 18 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 11) | MB_ANIMATED_DOOR | CeruleanCity_House1_Frlg | (3, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (30, 11) | MB_ANIMATED_DOOR | CeruleanCity_House2_Frlg | (3, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (15, 17) | MB_ANIMATED_DOOR | CeruleanCity_House3_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (22, 19) | MB_ANIMATED_DOOR | CeruleanCity_PokemonCenter_1F_Frlg | (7, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (31, 21) | MB_ANIMATED_DOOR | CeruleanCity_Gym_Frlg | (8, 18) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (13, 28) | MB_NON_ANIMATED_DOOR | CeruleanCity_BikeShop_Frlg | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (29, 28) | MB_ANIMATED_DOOR | CeruleanCity_Mart_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (1, 12) | MB_NON_ANIMATED_DOOR | CeruleanCave_1F_Frlg | (33, 21) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (10, 8) | MB_SOUTH_ARROW_WARP | CeruleanCity_House1_Frlg | (3, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (31, 8) | MB_SOUTH_ARROW_WARP | CeruleanCity_House2_Frlg | (4, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 10 | (31, 9) | MB_NORMAL | CeruleanCity_House2_Frlg | (4, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 11 | (14, 28) | MB_NON_ANIMATED_DOOR | CeruleanCity_BikeShop_Frlg | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 12 | (23, 28) | MB_ANIMATED_DOOR | CeruleanCity_House4_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 13 | (17, 11) | MB_ANIMATED_DOOR | CeruleanCity_House5_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCity_Frlg[0] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[1] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[2] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[3] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[4] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[5] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[6] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[7] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[8] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[9] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[10] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[11] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[12] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg[13] UNTESTED** — untestable: CeruleanCity_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg conn[0] up/12 -> Route24_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg conn[1] down/0 -> Route5_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg conn[2] left/10 -> Route4_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **CeruleanCity_Frlg conn[3] right/10 -> Route9_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `CeruleanCity_Gym_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 18) | MB_NORMAL | CeruleanCity_Frlg | (31, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (8, 18) | MB_SOUTH_ARROW_WARP | CeruleanCity_Frlg | (31, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 18) | MB_NORMAL | CeruleanCity_Frlg | (31, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCity_Gym_Frlg[0] UNTESTED** — untestable: CeruleanCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Gym_Frlg[1] UNTESTED** — untestable: CeruleanCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Gym_Frlg[2] UNTESTED** — untestable: CeruleanCity_Gym_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCity_House1_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 9) | MB_NORMAL | CeruleanCity_Frlg | (10, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (3, 8) | MB_SOUTH_ARROW_WARP | CeruleanCity_Frlg | (10, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (4, 9) | MB_NORMAL | CeruleanCity_Frlg | (10, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (3, 1) | MB_NON_ANIMATED_DOOR | CeruleanCity_Frlg | (10, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCity_House1_Frlg[0] UNTESTED** — untestable: CeruleanCity_House1_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_House1_Frlg[1] UNTESTED** — untestable: CeruleanCity_House1_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_House1_Frlg[2] UNTESTED** — untestable: CeruleanCity_House1_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_House1_Frlg[3] UNTESTED** — untestable: CeruleanCity_House1_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCity_House2_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 7) | MB_NORMAL | CeruleanCity_Frlg | (30, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (3, 7) | MB_SOUTH_ARROW_WARP | CeruleanCity_Frlg | (30, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (4, 7) | MB_NORMAL | CeruleanCity_Frlg | (30, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (4, 1) | MB_NON_ANIMATED_DOOR | CeruleanCity_Frlg | (31, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCity_House2_Frlg[0] UNTESTED** — untestable: CeruleanCity_House2_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_House2_Frlg[1] UNTESTED** — untestable: CeruleanCity_House2_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_House2_Frlg[2] UNTESTED** — untestable: CeruleanCity_House2_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_House2_Frlg[3] UNTESTED** — untestable: CeruleanCity_House2_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCity_House3_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | CeruleanCity_Frlg | (15, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | CeruleanCity_Frlg | (15, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | CeruleanCity_Frlg | (15, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCity_House3_Frlg[0] UNTESTED** — untestable: CeruleanCity_House3_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_House3_Frlg[1] UNTESTED** — untestable: CeruleanCity_House3_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_House3_Frlg[2] UNTESTED** — untestable: CeruleanCity_House3_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCity_House4_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | CeruleanCity_Frlg | (23, 28) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCity_House4_Frlg[0] UNTESTED** — untestable: CeruleanCity_House4_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCity_House5_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | CeruleanCity_Frlg | (17, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCity_House5_Frlg[0] UNTESTED** — untestable: CeruleanCity_House5_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCity_Mart_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | CeruleanCity_Frlg | (29, 28) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | CeruleanCity_Frlg | (29, 28) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | CeruleanCity_Frlg | (29, 28) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCity_Mart_Frlg[0] UNTESTED** — untestable: CeruleanCity_Mart_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Mart_Frlg[1] UNTESTED** — untestable: CeruleanCity_Mart_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_Mart_Frlg[2] UNTESTED** — untestable: CeruleanCity_Mart_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCity_PokemonCenter_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 8) | MB_NORMAL | CeruleanCity_Frlg | (22, 19) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (7, 8) | MB_SOUTH_ARROW_WARP | CeruleanCity_Frlg | (22, 19) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 8) | MB_NORMAL | CeruleanCity_Frlg | (22, 19) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (1, 6) | MB_UP_ESCALATOR | CeruleanCity_PokemonCenter_2F_Frlg | (1, 6) | MB_DOWN_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCity_PokemonCenter_1F_Frlg[0] UNTESTED** — untestable: CeruleanCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_PokemonCenter_1F_Frlg[1] UNTESTED** — untestable: CeruleanCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_PokemonCenter_1F_Frlg[2] UNTESTED** — untestable: CeruleanCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_PokemonCenter_1F_Frlg[3] UNTESTED** — untestable: CeruleanCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)

### `CeruleanCity_PokemonCenter_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | CeruleanCity_PokemonCenter_1F_Frlg | (1, 6) | MB_UP_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom_Frlg | (7, 11) | MB_BRIDGE_OVER_OCEAN | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter_Frlg | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CeruleanCity_PokemonCenter_2F_Frlg[0] UNTESTED** — untestable: CeruleanCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_PokemonCenter_2F_Frlg[1] UNTESTED** — untestable: CeruleanCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **CeruleanCity_PokemonCenter_2F_Frlg[2] UNTESTED** — untestable: CeruleanCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)

### `CherrygroveCity_SoutheastHouse_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 9) | MB_SOUTH_ARROW_WARP | CherrygroveCity_hns | (34, 13) | MB_ANIMATED_DOOR | (34, 13) | (34, 14) | DOWN (DOWN) | yes | same door | **OK** |


### `CherrygroveCity_hns`

*Tier: story-trigger map — 5 warp(s), 2 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (41, 7) | MB_ANIMATED_DOOR | Mart_Johto_hns | (4, 7) | MB_SOUTH_ARROW_WARP | (4, 7) | (4, 7) | UP (UP) | yes | same door | **OK** |
| 1 | (47, 7) | MB_ANIMATED_DOOR | PokemonCenter_Johto_hns | (7, 8) | MB_SOUTH_ARROW_WARP | (7, 8) | (7, 8) | UP (UP) | yes | same door | **OK** |
| 2 | (34, 13) | MB_ANIMATED_DOOR | CherrygroveCity_SoutheastHouse_hns | (4, 9) | MB_SOUTH_ARROW_WARP | (4, 9) | (4, 9) | UP (UP) | yes | same door | **OK** |
| 3 | (42, 14) | MB_ANIMATED_DOOR | House_GenericB_hns | (4, 9) | MB_SOUTH_ARROW_WARP | (4, 9) | (4, 9) | UP (UP) | yes | same door | **OK** |
| 4 | (50, 17) | MB_ANIMATED_DOOR | House_GenericA_hns | (4, 9) | MB_SOUTH_ARROW_WARP | (4, 9) | (4, 9) | UP (UP) | yes | same door | **OK** |

* **CherrygroveCity_hns conn[0] right/-6 -> Route29_hns OK** — outward:OK (handed over to Route29_hns at (0,17)); inward:OK (returned to CherrygroveCity_hns at (64,11))
* **CherrygroveCity_hns conn[1] up/25 -> Route2_Frlg OK** — outward:OK (handed over to Route2_Frlg at (10,79)); inward:OK (returned to CherrygroveCity_hns at (35,0))

### `CinnabarIsland_Frlg`

*Tier: story-trigger map — 5 warp(s), 1 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (8, 3) | MB_NON_ANIMATED_DOOR | PokemonMansion_1F_Frlg | (8, 33) | MB_SOUTH_ARROW_WARP | (8, 33) | (8, 33) | UP (UP) | yes | same door | **OK** |
| 1 | (20, 4) | MB_ANIMATED_DOOR | CinnabarIsland_Gym_Frlg | (25, 23) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 9) | MB_ANIMATED_DOOR | CinnabarIsland_PokemonLab_Entrance_Frlg | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (14, 11) | MB_ANIMATED_DOOR | CinnabarIsland_PokemonCenter_1F_Frlg | (7, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (19, 11) | MB_ANIMATED_DOOR | CinnabarIsland_Mart_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CinnabarIsland_Frlg[1] UNTESTED** — untestable: CinnabarIsland_Gym_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_Frlg[2] UNTESTED** — untestable: CinnabarIsland_PokemonLab_Entrance_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_Frlg[3] UNTESTED** — untestable: CinnabarIsland_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_Frlg[4] UNTESTED** — untestable: CinnabarIsland_Mart_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_Frlg conn[0] up/0 -> Route21_South_Frlg OK** — outward:OK (handed over to Route21_South_Frlg at (12,49)); inward:OK (returned to CinnabarIsland_Frlg at (12,0))

### `CinnabarIsland_Gym_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (24, 23) | MB_NORMAL | CinnabarIsland_Frlg | (20, 4) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (25, 23) | MB_SOUTH_ARROW_WARP | CinnabarIsland_Frlg | (20, 4) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (26, 23) | MB_NORMAL | CinnabarIsland_Frlg | (20, 4) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CinnabarIsland_Gym_Frlg[0] UNTESTED** — untestable: CinnabarIsland_Gym_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_Gym_Frlg[1] UNTESTED** — untestable: CinnabarIsland_Gym_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_Gym_Frlg[2] UNTESTED** — untestable: CinnabarIsland_Gym_Frlg cannot be loaded by the engine (see load check)

### `CinnabarIsland_Mart_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | CinnabarIsland_Frlg | (19, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | CinnabarIsland_Frlg | (19, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | CinnabarIsland_Frlg | (19, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CinnabarIsland_Mart_Frlg[0] UNTESTED** — untestable: CinnabarIsland_Mart_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_Mart_Frlg[1] UNTESTED** — untestable: CinnabarIsland_Mart_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_Mart_Frlg[2] UNTESTED** — untestable: CinnabarIsland_Mart_Frlg cannot be loaded by the engine (see load check)

### `CinnabarIsland_PokemonCenter_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 8) | MB_SOUTH_ARROW_WARP | CinnabarIsland_Frlg | (14, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 8) | MB_NORMAL | CinnabarIsland_Frlg | (14, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 8) | MB_NORMAL | CinnabarIsland_Frlg | (14, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (1, 6) | MB_UP_ESCALATOR | CinnabarIsland_PokemonCenter_2F_Frlg | (1, 6) | MB_DOWN_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |

* **CinnabarIsland_PokemonCenter_1F_Frlg[0] UNTESTED** — untestable: CinnabarIsland_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_PokemonCenter_1F_Frlg[1] UNTESTED** — untestable: CinnabarIsland_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_PokemonCenter_1F_Frlg[2] UNTESTED** — untestable: CinnabarIsland_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_PokemonCenter_1F_Frlg[3] UNTESTED** — untestable: CinnabarIsland_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)

### `CinnabarIsland_PokemonCenter_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | CinnabarIsland_PokemonCenter_1F_Frlg | (1, 6) | MB_UP_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom_Frlg | (7, 11) | MB_BRIDGE_OVER_OCEAN | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter_Frlg | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CinnabarIsland_PokemonCenter_2F_Frlg[0] UNTESTED** — untestable: CinnabarIsland_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_PokemonCenter_2F_Frlg[1] UNTESTED** — untestable: CinnabarIsland_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_PokemonCenter_2F_Frlg[2] UNTESTED** — untestable: CinnabarIsland_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)

### `CinnabarIsland_PokemonLab_Entrance_Frlg`

*Tier: donor facility (vanilla) — 6 warp(s), 0 connection(s), 6 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 9) | MB_NORMAL | CinnabarIsland_Frlg | (8, 9) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 9) | MB_SOUTH_ARROW_WARP | CinnabarIsland_Frlg | (8, 9) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 9) | MB_NORMAL | CinnabarIsland_Frlg | (8, 9) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (13, 5) | MB_NON_ANIMATED_DOOR | CinnabarIsland_PokemonLab_Lounge_Frlg | (7, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (19, 5) | MB_NON_ANIMATED_DOOR | CinnabarIsland_PokemonLab_ResearchRoom_Frlg | (7, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (25, 5) | MB_NON_ANIMATED_DOOR | CinnabarIsland_PokemonLab_ExperimentRoom_Frlg | (7, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **CinnabarIsland_PokemonLab_Entrance_Frlg[0] UNTESTED** — untestable: CinnabarIsland_PokemonLab_Entrance_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_PokemonLab_Entrance_Frlg[1] UNTESTED** — untestable: CinnabarIsland_PokemonLab_Entrance_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_PokemonLab_Entrance_Frlg[2] UNTESTED** — untestable: CinnabarIsland_PokemonLab_Entrance_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_PokemonLab_Entrance_Frlg[3] UNTESTED** — untestable: CinnabarIsland_PokemonLab_Entrance_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_PokemonLab_Entrance_Frlg[4] UNTESTED** — untestable: CinnabarIsland_PokemonLab_Entrance_Frlg cannot be loaded by the engine (see load check)
* **CinnabarIsland_PokemonLab_Entrance_Frlg[5] UNTESTED** — untestable: CinnabarIsland_PokemonLab_Entrance_Frlg cannot be loaded by the engine (see load check)

### `CinnabarIsland_PokemonLab_ExperimentRoom_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 9) | MB_SOUTH_ARROW_WARP | CinnabarIsland_PokemonLab_Entrance_Frlg | (25, 5) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CinnabarIsland_PokemonLab_ExperimentRoom_Frlg[0] UNTESTED** — untestable: CinnabarIsland_PokemonLab_ExperimentRoom_Frlg cannot be loaded by the engine (see load check)

### `CinnabarIsland_PokemonLab_Lounge_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 9) | MB_SOUTH_ARROW_WARP | CinnabarIsland_PokemonLab_Entrance_Frlg | (13, 5) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CinnabarIsland_PokemonLab_Lounge_Frlg[0] UNTESTED** — untestable: CinnabarIsland_PokemonLab_Lounge_Frlg cannot be loaded by the engine (see load check)

### `CinnabarIsland_PokemonLab_ResearchRoom_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 9) | MB_SOUTH_ARROW_WARP | CinnabarIsland_PokemonLab_Entrance_Frlg | (19, 5) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **CinnabarIsland_PokemonLab_ResearchRoom_Frlg[0] UNTESTED** — untestable: CinnabarIsland_PokemonLab_ResearchRoom_Frlg cannot be loaded by the engine (see load check)

### `DarkCave_SouthSide_hns`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (14, 20) | MB_LADDER | Route2_Frlg | (17, 11) | MB_ANIMATED_DOOR | (17, 11) | (17, 12) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (56, 46) | MB_LADDER | Route46_hns | (20, 11) | MB_ANIMATED_DOOR | (20, 11) | (20, 12) | UP (DOWN) | yes | same door | **OK** |


### `DiglettsCave_B1F_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 3) | MB_LADDER | DiglettsCave_NorthEntrance_Frlg | (6, 4) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (82, 71) | MB_LADDER | DiglettsCave_SouthEntrance_Frlg | (6, 4) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |

* **DiglettsCave_B1F_Frlg[0] UNTESTED** — untestable: DiglettsCave_B1F_Frlg cannot be loaded by the engine (see load check)
* **DiglettsCave_B1F_Frlg[1] UNTESTED** — untestable: DiglettsCave_B1F_Frlg cannot be loaded by the engine (see load check)

### `DiglettsCave_NorthEntrance_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 4) | MB_LADDER | DiglettsCave_B1F_Frlg | (3, 3) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 6) | MB_SOUTH_ARROW_WARP | Route2_Frlg | (17, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **DiglettsCave_NorthEntrance_Frlg[0] UNTESTED** — untestable: DiglettsCave_NorthEntrance_Frlg cannot be loaded by the engine (see load check)
* **DiglettsCave_NorthEntrance_Frlg[1] UNTESTED** — untestable: DiglettsCave_NorthEntrance_Frlg cannot be loaded by the engine (see load check)

### `DiglettsCave_SouthEntrance_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 6) | MB_SOUTH_ARROW_WARP | Route11_Frlg | (6, 7) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 4) | MB_LADDER | DiglettsCave_B1F_Frlg | (82, 71) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |

* **DiglettsCave_SouthEntrance_Frlg[0] UNTESTED** — untestable: DiglettsCave_SouthEntrance_Frlg cannot be loaded by the engine (see load check)
* **DiglettsCave_SouthEntrance_Frlg[1] UNTESTED** — untestable: DiglettsCave_SouthEntrance_Frlg cannot be loaded by the engine (see load check)

### `EcruteakCity_hns`

*Tier: story-trigger map — 3 warp(s), 1 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (39, 47) | MB_ANIMATED_DOOR | PokemonCenter_Johto_hns | (7, 8) | MB_SOUTH_ARROW_WARP | (7, 8) | (7, 8) | UP (UP) | yes | same door | **OK** |
| 1 | (48, 40) | MB_ANIMATED_DOOR | Mart_Johto_hns | (4, 7) | MB_SOUTH_ARROW_WARP | (4, 7) | (4, 7) | UP (UP) | yes | same door | **OK** |
| 2 | (19, 40) | MB_ANIMATED_DOOR | House_GenericA_hns | (4, 9) | MB_SOUTH_ARROW_WARP | (4, 9) | (4, 9) | UP (UP) | yes | same door | **OK** |

* **EcruteakCity_hns conn[0] down/-16 -> Route37_hns ISSUE** — outward:ISSUE (walking DOWN off the EcruteakCity_hns edge did not change map on any of 2 lanes tried: lane 18: held DOWN from (18,58) and stayed on EcruteakCity_hns at (18,59); lane 19: held DOWN from (19,58) and stayed on EcruteakCity)
  * down seam: walking DOWN off the EcruteakCity_hns edge did not change map on any of 2 lanes tried: lane 18: held DOWN from (18,58) and stayed on EcruteakCity_hns at (18,59); lane 19: held DOWN from (19,58) and stayed on E

### `FortreeCity`

*Tier: story-trigger map — 9 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 6) | MB_ANIMATED_DOOR | FortreeCity_PokemonCenter_1F | (7, 8) | MB_SOUTH_ARROW_WARP | (7, 8) | (7, 8) | UP (UP) | yes | same door | **OK** |
| 1 | (10, 3) | MB_NON_ANIMATED_DOOR | FortreeCity_House1 | (3, 5) | MB_SOUTH_ARROW_WARP | (3, 5) | (3, 5) | UP (UP) | yes | same door | **OK** |
| 2 | (22, 11) | MB_ANIMATED_DOOR | FortreeCity_Gym | (15, 24) | MB_SOUTH_ARROW_WARP | (15, 24) | (15, 24) | UP (UP) | yes | same door | **OK** |
| 3 | (4, 14) | MB_ANIMATED_DOOR | FortreeCity_Mart | (3, 7) | MB_SOUTH_ARROW_WARP | (3, 7) | (3, 7) | UP (UP) | yes | same door | **OK** |
| 4 | (17, 3) | MB_NON_ANIMATED_DOOR | FortreeCity_House2 | (3, 5) | MB_SOUTH_ARROW_WARP | (3, 5) | (3, 5) | UP (UP) | yes | same door | **OK** |
| 5 | (25, 3) | MB_NON_ANIMATED_DOOR | FortreeCity_House3 | (3, 5) | MB_SOUTH_ARROW_WARP | (3, 5) | (3, 5) | UP (UP) | yes | same door | **OK** |
| 6 | (32, 2) | MB_NON_ANIMATED_DOOR | FortreeCity_House4 | (3, 5) | MB_SOUTH_ARROW_WARP | (3, 5) | (3, 5) | UP (UP) | yes | same door | **OK** |
| 7 | (12, 13) | MB_NON_ANIMATED_DOOR | FortreeCity_House5 | (3, 5) | MB_SOUTH_ARROW_WARP | (3, 5) | (3, 5) | UP (UP) | yes | same door | **OK** |
| 8 | (37, 13) | MB_NON_ANIMATED_DOOR | FortreeCity_DecorationShop | (3, 5) | MB_SOUTH_ARROW_WARP | (3, 5) | (3, 5) | UP (UP) | yes | same door | **OK** |


### `FortreeCity_DecorationShop`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 5) | MB_SOUTH_ARROW_WARP | FortreeCity | (37, 13) | MB_NON_ANIMATED_DOOR | (37, 13) | (37, 14) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 5) | MB_SOUTH_ARROW_WARP | FortreeCity | (37, 13) | MB_NON_ANIMATED_DOOR | (37, 13) | (37, 14) | DOWN (DOWN) | yes | same door | **OK** |


### `FortreeCity_Gym`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (15, 24) | MB_SOUTH_ARROW_WARP | FortreeCity | (22, 11) | MB_ANIMATED_DOOR | (22, 11) | (22, 12) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (16, 24) | MB_SOUTH_ARROW_WARP | FortreeCity | (22, 11) | MB_ANIMATED_DOOR | (22, 11) | (22, 12) | DOWN (DOWN) | yes | same door | **OK** |


### `FortreeCity_House1`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 5) | MB_SOUTH_ARROW_WARP | FortreeCity | (10, 3) | MB_NON_ANIMATED_DOOR | (10, 3) | (10, 4) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 5) | MB_SOUTH_ARROW_WARP | FortreeCity | (10, 3) | MB_NON_ANIMATED_DOOR | (10, 3) | (10, 4) | DOWN (DOWN) | yes | same door | **OK** |


### `FortreeCity_House2`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 5) | MB_SOUTH_ARROW_WARP | FortreeCity | (17, 3) | MB_NON_ANIMATED_DOOR | (17, 3) | (17, 4) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 5) | MB_SOUTH_ARROW_WARP | FortreeCity | (17, 3) | MB_NON_ANIMATED_DOOR | (17, 3) | (17, 4) | DOWN (DOWN) | yes | same door | **OK** |


### `FortreeCity_House3`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 5) | MB_SOUTH_ARROW_WARP | FortreeCity | (25, 3) | MB_NON_ANIMATED_DOOR | (25, 3) | (25, 4) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 5) | MB_SOUTH_ARROW_WARP | FortreeCity | (25, 3) | MB_NON_ANIMATED_DOOR | (25, 3) | (25, 4) | DOWN (DOWN) | yes | same door | **OK** |


### `FortreeCity_House4`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 5) | MB_SOUTH_ARROW_WARP | FortreeCity | (32, 2) | MB_NON_ANIMATED_DOOR | (32, 2) | (32, 3) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 5) | MB_SOUTH_ARROW_WARP | FortreeCity | (32, 2) | MB_NON_ANIMATED_DOOR | (32, 2) | (32, 3) | DOWN (DOWN) | yes | same door | **OK** |


### `FortreeCity_House5`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 5) | MB_SOUTH_ARROW_WARP | FortreeCity | (12, 13) | MB_NON_ANIMATED_DOOR | (12, 13) | (12, 14) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 5) | MB_SOUTH_ARROW_WARP | FortreeCity | (12, 13) | MB_NON_ANIMATED_DOOR | (12, 13) | (12, 14) | DOWN (DOWN) | yes | same door | **OK** |


### `FortreeCity_Mart`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_SOUTH_ARROW_WARP | FortreeCity | (4, 14) | MB_ANIMATED_DOOR | (4, 14) | (4, 15) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | FortreeCity | (4, 14) | MB_ANIMATED_DOOR | (4, 14) | (4, 15) | DOWN (DOWN) | yes | same door | **OK** |


### `FortreeCity_PokemonCenter_1F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 8) | MB_SOUTH_ARROW_WARP | FortreeCity | (5, 6) | MB_ANIMATED_DOOR | (5, 6) | (5, 7) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | FortreeCity | (5, 6) | MB_ANIMATED_DOOR | (5, 6) | (5, 7) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (1, 6) | MB_UP_ESCALATOR | FortreeCity_PokemonCenter_2F | (1, 6) | MB_DOWN_ESCALATOR | (1, 6) | (2, 6) | LEFT (DOWN) | yes | same door | **OK** |


### `FortreeCity_PokemonCenter_2F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | FortreeCity_PokemonCenter_1F | (1, 6) | MB_UP_ESCALATOR | (1, 6) | (2, 6) | LEFT (DOWN) | yes | same door | **OK** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom | (7, 11) | MB_BRIDGE_OVER_OCEAN | (7, 11) | (7, 11) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter | (5, 8) | MB_SOUTH_ARROW_WARP | (5, 8) | (5, 8) | UP (UP) | yes | same door | **OK** |


### `FuchsiaCity_Frlg`

*Tier: donor town/cave (vanilla base) — 11 warp(s), 3 connection(s), 14 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (24, 5) | MB_ANIMATED_DOOR | FuchsiaCity_SafariZone_Entrance_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (33, 31) | MB_ANIMATED_DOOR | FuchsiaCity_WardensHouse_Frlg | (6, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (11, 15) | MB_ANIMATED_DOOR | FuchsiaCity_Mart_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (28, 16) | MB_ANIMATED_DOOR | FuchsiaCity_SafariZone_Office_Frlg | (6, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (9, 32) | MB_ANIMATED_DOOR | FuchsiaCity_Gym_Frlg | (7, 21) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (14, 31) | MB_ANIMATED_DOOR | FuchsiaCity_House1_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (25, 31) | MB_ANIMATED_DOOR | FuchsiaCity_PokemonCenter_1F_Frlg | (7, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (38, 31) | MB_ANIMATED_DOOR | FuchsiaCity_House2_Frlg | (3, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (39, 28) | MB_SOUTH_ARROW_WARP | FuchsiaCity_House2_Frlg | (3, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (39, 29) | MB_NORMAL | FuchsiaCity_House2_Frlg | (3, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 10 | (19, 31) | MB_ANIMATED_DOOR | FuchsiaCity_House3_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **FuchsiaCity_Frlg[0] UNTESTED** — untestable: FuchsiaCity_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg[1] UNTESTED** — untestable: FuchsiaCity_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg[2] UNTESTED** — untestable: FuchsiaCity_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg[3] UNTESTED** — untestable: FuchsiaCity_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg[4] UNTESTED** — untestable: FuchsiaCity_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg[5] UNTESTED** — untestable: FuchsiaCity_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg[6] UNTESTED** — untestable: FuchsiaCity_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg[7] UNTESTED** — untestable: FuchsiaCity_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg[8] UNTESTED** — untestable: FuchsiaCity_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg[9] UNTESTED** — untestable: FuchsiaCity_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg[10] UNTESTED** — untestable: FuchsiaCity_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg conn[0] down/12 -> Route19_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg conn[1] left/10 -> Route18_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **FuchsiaCity_Frlg conn[2] right/10 -> Route15_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `FuchsiaCity_Gym_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 21) | MB_NORMAL | FuchsiaCity_Frlg | (9, 32) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (7, 21) | MB_SOUTH_ARROW_WARP | FuchsiaCity_Frlg | (9, 32) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 21) | MB_NORMAL | FuchsiaCity_Frlg | (9, 32) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **FuchsiaCity_Gym_Frlg[0] UNTESTED** — untestable: FuchsiaCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Gym_Frlg[1] UNTESTED** — untestable: FuchsiaCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Gym_Frlg[2] UNTESTED** — untestable: FuchsiaCity_Gym_Frlg cannot be loaded by the engine (see load check)

### `FuchsiaCity_House1_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | FuchsiaCity_Frlg | (14, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | FuchsiaCity_Frlg | (14, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | FuchsiaCity_Frlg | (14, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **FuchsiaCity_House1_Frlg[0] UNTESTED** — untestable: FuchsiaCity_House1_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_House1_Frlg[1] UNTESTED** — untestable: FuchsiaCity_House1_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_House1_Frlg[2] UNTESTED** — untestable: FuchsiaCity_House1_Frlg cannot be loaded by the engine (see load check)

### `FuchsiaCity_House2_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 9) | MB_NORMAL | FuchsiaCity_Frlg | (38, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (3, 8) | MB_SOUTH_ARROW_WARP | FuchsiaCity_Frlg | (38, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (4, 9) | MB_NORMAL | FuchsiaCity_Frlg | (38, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (3, 1) | MB_NON_ANIMATED_DOOR | FuchsiaCity_Frlg | (39, 28) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **FuchsiaCity_House2_Frlg[0] UNTESTED** — untestable: FuchsiaCity_House2_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_House2_Frlg[1] UNTESTED** — untestable: FuchsiaCity_House2_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_House2_Frlg[2] UNTESTED** — untestable: FuchsiaCity_House2_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_House2_Frlg[3] UNTESTED** — untestable: FuchsiaCity_House2_Frlg cannot be loaded by the engine (see load check)

### `FuchsiaCity_House3_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | FuchsiaCity_Frlg | (19, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **FuchsiaCity_House3_Frlg[0] UNTESTED** — untestable: FuchsiaCity_House3_Frlg cannot be loaded by the engine (see load check)

### `FuchsiaCity_Mart_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | FuchsiaCity_Frlg | (11, 15) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | FuchsiaCity_Frlg | (11, 15) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | FuchsiaCity_Frlg | (11, 15) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **FuchsiaCity_Mart_Frlg[0] UNTESTED** — untestable: FuchsiaCity_Mart_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Mart_Frlg[1] UNTESTED** — untestable: FuchsiaCity_Mart_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_Mart_Frlg[2] UNTESTED** — untestable: FuchsiaCity_Mart_Frlg cannot be loaded by the engine (see load check)

### `FuchsiaCity_PokemonCenter_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 8) | MB_NORMAL | FuchsiaCity_Frlg | (25, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (7, 8) | MB_SOUTH_ARROW_WARP | FuchsiaCity_Frlg | (25, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 8) | MB_NORMAL | FuchsiaCity_Frlg | (25, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (1, 6) | MB_UP_ESCALATOR | FuchsiaCity_PokemonCenter_2F_Frlg | (1, 6) | MB_DOWN_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |

* **FuchsiaCity_PokemonCenter_1F_Frlg[0] UNTESTED** — untestable: FuchsiaCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_PokemonCenter_1F_Frlg[1] UNTESTED** — untestable: FuchsiaCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_PokemonCenter_1F_Frlg[2] UNTESTED** — untestable: FuchsiaCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_PokemonCenter_1F_Frlg[3] UNTESTED** — untestable: FuchsiaCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)

### `FuchsiaCity_PokemonCenter_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | FuchsiaCity_PokemonCenter_1F_Frlg | (1, 6) | MB_UP_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom_Frlg | (7, 11) | MB_BRIDGE_OVER_OCEAN | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter_Frlg | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **FuchsiaCity_PokemonCenter_2F_Frlg[0] UNTESTED** — untestable: FuchsiaCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_PokemonCenter_2F_Frlg[1] UNTESTED** — untestable: FuchsiaCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_PokemonCenter_2F_Frlg[2] UNTESTED** — untestable: FuchsiaCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)

### `FuchsiaCity_SafariZone_Entrance_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 1) | MB_NON_ANIMATED_DOOR | SafariZone_Center_Frlg | (26, 30) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 7) | MB_NORMAL | FuchsiaCity_Frlg | (24, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (4, 7) | MB_SOUTH_ARROW_WARP | FuchsiaCity_Frlg | (24, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (3, 7) | MB_NORMAL | FuchsiaCity_Frlg | (24, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **FuchsiaCity_SafariZone_Entrance_Frlg[0] UNTESTED** — untestable: FuchsiaCity_SafariZone_Entrance_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_SafariZone_Entrance_Frlg[1] UNTESTED** — untestable: FuchsiaCity_SafariZone_Entrance_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_SafariZone_Entrance_Frlg[2] UNTESTED** — untestable: FuchsiaCity_SafariZone_Entrance_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_SafariZone_Entrance_Frlg[3] UNTESTED** — untestable: FuchsiaCity_SafariZone_Entrance_Frlg cannot be loaded by the engine (see load check)

### `FuchsiaCity_SafariZone_Office_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 9) | MB_NORMAL | FuchsiaCity_Frlg | (28, 16) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 9) | MB_SOUTH_ARROW_WARP | FuchsiaCity_Frlg | (28, 16) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (7, 9) | MB_NORMAL | FuchsiaCity_Frlg | (28, 16) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **FuchsiaCity_SafariZone_Office_Frlg[0] UNTESTED** — untestable: FuchsiaCity_SafariZone_Office_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_SafariZone_Office_Frlg[1] UNTESTED** — untestable: FuchsiaCity_SafariZone_Office_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_SafariZone_Office_Frlg[2] UNTESTED** — untestable: FuchsiaCity_SafariZone_Office_Frlg cannot be loaded by the engine (see load check)

### `FuchsiaCity_WardensHouse_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 10) | MB_NORMAL | FuchsiaCity_Frlg | (33, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 9) | MB_SOUTH_ARROW_WARP | FuchsiaCity_Frlg | (33, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (7, 10) | MB_NORMAL | FuchsiaCity_Frlg | (33, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **FuchsiaCity_WardensHouse_Frlg[0] UNTESTED** — untestable: FuchsiaCity_WardensHouse_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_WardensHouse_Frlg[1] UNTESTED** — untestable: FuchsiaCity_WardensHouse_Frlg cannot be loaded by the engine (see load check)
* **FuchsiaCity_WardensHouse_Frlg[2] UNTESTED** — untestable: FuchsiaCity_WardensHouse_Frlg cannot be loaded by the engine (see load check)

### `Gate_Route29_Route46_hns`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 1) | MB_NON_ANIMATED_DOOR | Route46_hns | (10, 40) | MB_SOUTH_ARROW_WARP | (10, 40) | (10, 40) | UP (UP) | yes | same door | **OK** |
| 1 | (7, 9) | MB_SOUTH_ARROW_WARP | Route29_hns | (34, 10) | MB_NON_ANIMATED_DOOR | (34, 10) | (34, 11) | DOWN (DOWN) | yes | same door | **OK** |


### `GoldenrodCity_BikeShop_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (44, 38) | MB_ANIMATED_DOOR | (44, 38) | (44, 39) | DOWN (DOWN) | yes | same door | **OK** |


### `GoldenrodCity_BillsHouse_hns`

*Tier: story-trigger map — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 8) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (14, 33) | MB_ANIMATED_DOOR | (14, 33) | (14, 34) | DOWN (DOWN) | yes | same door | **OK** |


### `GoldenrodCity_DepartmentStoreBasement_hns`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (20, 2) | MB_WEST_ARROW_WARP | GoldenrodCity_UndergroundStorage_hns | (19, 2) | MB_EAST_ARROW_WARP | (19, 2) | (19, 2) | LEFT (LEFT) | yes | same door | **OK** |
| 1 | (10, 6) | MB_ANIMATED_DOOR | GoldenrodCity_DepartmentStoreElevator_hns | (2, 5) | MB_SOUTH_ARROW_WARP | (2, 5) | (2, 5) | UP (UP) | yes | same door | **OK** |


### `GoldenrodCity_DepartmentStoreElevator_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 5) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | (2, 5) | (2, 5) | UP (UP) | yes | same door | **OK** |


### `GoldenrodCity_DepartmentStore_1F_hns`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (15, 11) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (39, 36) | MB_ANIMATED_DOOR | (39, 36) | (39, 37) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (22, 5) | MB_EAST_ARROW_WARP | GoldenrodCity_DepartmentStore_2F_hns | (24, 5) | MB_WEST_ARROW_WARP | (24, 5) | (24, 5) | RIGHT (RIGHT) | yes | same door | **OK** |
| 2 | (9, 4) | MB_ANIMATED_DOOR | GoldenrodCity_DepartmentStoreElevator_hns | (2, 5) | MB_SOUTH_ARROW_WARP | (2, 5) | (2, 5) | UP (UP) | yes | same door | **OK** |


### `GoldenrodCity_DepartmentStore_2F_hns`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (17, 5) | MB_EAST_ARROW_WARP | GoldenrodCity_DepartmentStore_3F_hns | (22, 5) | MB_WEST_ARROW_WARP | (22, 5) | (22, 5) | RIGHT (RIGHT) | yes | same door | **OK** |
| 1 | (24, 5) | MB_WEST_ARROW_WARP | GoldenrodCity_DepartmentStore_1F_hns | (22, 5) | MB_EAST_ARROW_WARP | (22, 5) | (22, 5) | LEFT (LEFT) | yes | same door | **OK** |
| 2 | (9, 4) | MB_ANIMATED_DOOR | GoldenrodCity_DepartmentStoreElevator_hns | (2, 5) | MB_SOUTH_ARROW_WARP | (2, 5) | (2, 5) | UP (UP) | yes | same door | **OK** |


### `GoldenrodCity_DepartmentStore_3F_hns`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (24, 5) | MB_EAST_ARROW_WARP | GoldenrodCity_DepartmentStore_4F_hns | (24, 5) | MB_WEST_ARROW_WARP | (24, 5) | (24, 5) | RIGHT (RIGHT) | yes | same door | **OK** |
| 1 | (22, 5) | MB_WEST_ARROW_WARP | GoldenrodCity_DepartmentStore_2F_hns | (17, 5) | MB_EAST_ARROW_WARP | (17, 5) | (17, 5) | LEFT (LEFT) | yes | same door | **OK** |
| 2 | (9, 4) | MB_ANIMATED_DOOR | GoldenrodCity_DepartmentStoreElevator_hns | (2, 5) | MB_SOUTH_ARROW_WARP | (2, 5) | (2, 5) | UP (UP) | yes | same door | **OK** |


### `GoldenrodCity_DepartmentStore_4F_hns`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (17, 5) | MB_EAST_ARROW_WARP | GoldenrodCity_DepartmentStore_5F_hns | (22, 5) | MB_WEST_ARROW_WARP | (22, 5) | (22, 5) | RIGHT (RIGHT) | yes | same door | **OK** |
| 1 | (24, 5) | MB_WEST_ARROW_WARP | GoldenrodCity_DepartmentStore_3F_hns | (24, 5) | MB_EAST_ARROW_WARP | (24, 5) | (24, 5) | LEFT (LEFT) | yes | same door | **OK** |
| 2 | (9, 4) | MB_ANIMATED_DOOR | GoldenrodCity_DepartmentStoreElevator_hns | (2, 5) | MB_SOUTH_ARROW_WARP | (2, 5) | (2, 5) | UP (UP) | yes | same door | **OK** |


### `GoldenrodCity_DepartmentStore_5F_hns`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (24, 5) | MB_EAST_ARROW_WARP | GoldenrodCity_DepartmentStore_6F_hns | (24, 5) | MB_WEST_ARROW_WARP | (24, 5) | (24, 5) | RIGHT (RIGHT) | yes | same door | **OK** |
| 1 | (22, 5) | MB_WEST_ARROW_WARP | GoldenrodCity_DepartmentStore_4F_hns | (17, 5) | MB_EAST_ARROW_WARP | (17, 5) | (17, 5) | LEFT (LEFT) | yes | same door | **OK** |
| 2 | (9, 4) | MB_ANIMATED_DOOR | GoldenrodCity_DepartmentStoreElevator_hns | (2, 5) | MB_SOUTH_ARROW_WARP | (2, 5) | (2, 5) | UP (UP) | yes | same door | **OK** |


### `GoldenrodCity_DepartmentStore_6F_hns`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (24, 5) | MB_WEST_ARROW_WARP | GoldenrodCity_DepartmentStore_5F_hns | (24, 5) | MB_EAST_ARROW_WARP | (24, 5) | (24, 5) | LEFT (LEFT) | yes | same door | **OK** |
| 1 | (9, 4) | MB_ANIMATED_DOOR | GoldenrodCity_DepartmentStoreElevator_hns | (2, 5) | MB_SOUTH_ARROW_WARP | (2, 5) | (2, 5) | UP (UP) | yes | same door | **OK** |
| 2 | (17, 5) | MB_EAST_ARROW_WARP | GoldenrodCity_DepartmentStore_7F_hns | (22, 5) | MB_WEST_ARROW_WARP | (22, 5) | (22, 5) | RIGHT (RIGHT) | yes | same door | **OK** |


### `GoldenrodCity_DepartmentStore_7F_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (22, 5) | MB_WEST_ARROW_WARP | GoldenrodCity_DepartmentStore_6F_hns | (17, 5) | MB_EAST_ARROW_WARP | (17, 5) | (17, 5) | LEFT (LEFT) | yes | same door | **OK** |


### `GoldenrodCity_FlowerShop_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 9) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (44, 11) | MB_ANIMATED_DOOR | (44, 11) | (44, 12) | DOWN (DOWN) | yes | same door | **OK** |


### `GoldenrodCity_GameCorner_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 12) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (28, 29) | MB_ANIMATED_DOOR | (28, 29) | (28, 30) | DOWN (DOWN) | yes | same door | **OK** |


### `GoldenrodCity_Gym_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (9, 22) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (39, 13) | MB_ANIMATED_DOOR | (39, 13) | (39, 14) | DOWN (DOWN) | yes | same door | **OK** |


### `GoldenrodCity_House1_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 8) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (29, 13) | MB_ANIMATED_DOOR | (29, 13) | (29, 14) | DOWN (DOWN) | yes | same door | **OK** |


### `GoldenrodCity_House2_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 8) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (48, 15) | MB_ANIMATED_DOOR | (48, 15) | (48, 16) | DOWN (DOWN) | yes | same door | **OK** |


### `GoldenrodCity_House3_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 8) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (46, 28) | MB_ANIMATED_DOOR | (46, 28) | (46, 29) | DOWN (DOWN) | yes | same door | **OK** |


### `GoldenrodCity_PokemonCenter_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (9, 9) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (28, 36) | MB_ANIMATED_DOOR | (28, 36) | (28, 37) | DOWN (DOWN) | yes | same door | **OK** |


### `GoldenrodCity_RadioTower_1F_hns`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (9, 10) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (16, 22) | MB_ANIMATED_DOOR | (16, 22) | (16, 23) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (22, 5) | MB_EAST_ARROW_WARP | GoldenrodCity_RadioTower_2F_hns | (27, 5) | MB_WEST_ARROW_WARP | (27, 5) | (27, 5) | RIGHT (RIGHT) | yes | same door | **OK** |


### `GoldenrodCity_RadioTower_2F_hns`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (27, 5) | MB_WEST_ARROW_WARP | GoldenrodCity_RadioTower_1F_hns | (22, 5) | MB_EAST_ARROW_WARP | (22, 5) | (22, 5) | LEFT (LEFT) | yes | same door | **OK** |
| 1 | (10, 5) | MB_EAST_ARROW_WARP | GoldenrodCity_RadioTower_3F_hns | (9, 5) | MB_WEST_ARROW_WARP | (9, 5) | (9, 5) | RIGHT (RIGHT) | yes | same door | **OK** |


### `GoldenrodCity_RadioTower_3F_hns`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (19, 5) | MB_EAST_ARROW_WARP | GoldenrodCity_RadioTower_4F_hns | (9, 5) | MB_WEST_ARROW_WARP | (9, 5) | (9, 5) | RIGHT (RIGHT) | yes | same door | **OK** |
| 1 | (29, 5) | MB_EAST_ARROW_WARP | GoldenrodCity_RadioTower_4F_hns | (27, 5) | MB_WEST_ARROW_WARP | (27, 5) | (27, 5) | RIGHT (RIGHT) | yes | same door | **OK** |
| 2 | (9, 5) | MB_WEST_ARROW_WARP | GoldenrodCity_RadioTower_2F_hns | (10, 5) | MB_EAST_ARROW_WARP | (10, 5) | (10, 5) | LEFT (LEFT) | yes | same door | **OK** |


### `GoldenrodCity_RadioTower_4F_hns`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (19, 5) | MB_EAST_ARROW_WARP | GoldenrodCity_RadioTower_5F_hns | (11, 5) | MB_WEST_ARROW_WARP | (11, 5) | (11, 5) | RIGHT (RIGHT) | yes | same door | **OK** |
| 1 | (27, 5) | MB_WEST_ARROW_WARP | GoldenrodCity_RadioTower_3F_hns | (29, 5) | MB_EAST_ARROW_WARP | (29, 5) | (29, 5) | LEFT (LEFT) | yes | same door | **OK** |
| 2 | (9, 5) | MB_WEST_ARROW_WARP | GoldenrodCity_RadioTower_3F_hns | (19, 5) | MB_EAST_ARROW_WARP | (19, 5) | (19, 5) | LEFT (LEFT) | yes | same door | **OK** |
| 3 | (29, 5) | MB_EAST_ARROW_WARP | GoldenrodCity_RadioTower_5F_hns | (24, 5) | MB_WEST_ARROW_WARP | (24, 5) | (24, 5) | RIGHT (RIGHT) | yes | same door | **OK** |


### `GoldenrodCity_RadioTower_5F_hns`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (11, 5) | MB_WEST_ARROW_WARP | GoldenrodCity_RadioTower_4F_hns | (19, 5) | MB_EAST_ARROW_WARP | (19, 5) | (19, 5) | LEFT (LEFT) | yes | same door | **OK** |
| 1 | (24, 5) | MB_WEST_ARROW_WARP | GoldenrodCity_RadioTower_4F_hns | (29, 5) | MB_EAST_ARROW_WARP | (29, 5) | (29, 5) | LEFT (LEFT) | yes | same door | **OK** |


### `GoldenrodCity_TrainStation_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (16, 26) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (24, 21) | MB_ANIMATED_DOOR | (24, 21) | (24, 22) | DOWN (DOWN) | yes | same door | **OK** |


### `GoldenrodCity_UndergroundEntrance_hns`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (23, 3) | MB_WEST_ARROW_WARP | GoldenrodCity_UndergroundTunnel_hns | (2, 3) | MB_EAST_ARROW_WARP | (2, 3) | (2, 3) | LEFT (LEFT) | yes | same door | **OK** |
| 1 | (4, 3) | MB_EAST_ARROW_WARP | GoldenrodCity_UndergroundTunnel_hns | (3, 33) | MB_WEST_ARROW_WARP | (3, 33) | (3, 33) | RIGHT (RIGHT) | yes | same door | **OK** |
| 2 | (22, 7) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (20, 12) | MB_ANIMATED_DOOR | (20, 12) | (20, 13) | DOWN (DOWN) | yes | same door | **OK** |
| 3 | (5, 7) | MB_SOUTH_ARROW_WARP | GoldenrodCity_hns | (21, 38) | MB_ANIMATED_DOOR | (21, 38) | (21, 39) | DOWN (DOWN) | yes | same door | **OK** |


### `GoldenrodCity_UndergroundStorage_hns`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (19, 2) | MB_EAST_ARROW_WARP | GoldenrodCity_DepartmentStoreBasement_hns | (20, 2) | MB_WEST_ARROW_WARP | (20, 2) | (20, 2) | RIGHT (RIGHT) | yes | same door | **OK** |
| 1 | (3, 11) | MB_WEST_ARROW_WARP | GoldenrodCity_UndergroundSwitches_hns | (30, 11) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **GoldenrodCity_UndergroundStorage_hns[1] UNTESTED** — untestable: GoldenrodCity_UndergroundSwitches_hns cannot be loaded by the engine (see load check)

### `GoldenrodCity_UndergroundSwitches_hns`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (30, 11) | MB_WEST_ARROW_WARP | GoldenrodCity_UndergroundStorage_hns | (3, 11) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (34, 2) | MB_EAST_ARROW_WARP | GoldenrodCity_UndergroundTunnel_hns | (12, 10) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **GoldenrodCity_UndergroundSwitches_hns[0] UNTESTED** — untestable: GoldenrodCity_UndergroundSwitches_hns cannot be loaded by the engine (see load check)
* **GoldenrodCity_UndergroundSwitches_hns[1] UNTESTED** — untestable: GoldenrodCity_UndergroundSwitches_hns cannot be loaded by the engine (see load check)

### `GoldenrodCity_UndergroundTunnel_hns`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 33) | MB_WEST_ARROW_WARP | GoldenrodCity_UndergroundEntrance_hns | (4, 3) | MB_EAST_ARROW_WARP | (4, 3) | (4, 3) | LEFT (LEFT) | yes | same door | **OK** |
| 1 | (2, 3) | MB_EAST_ARROW_WARP | GoldenrodCity_UndergroundEntrance_hns | (23, 3) | MB_WEST_ARROW_WARP | (23, 3) | (23, 3) | RIGHT (RIGHT) | yes | same door | **OK** |
| 2 | (12, 10) | MB_ANIMATED_DOOR | GoldenrodCity_UndergroundSwitches_hns | (34, 2) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **GoldenrodCity_UndergroundTunnel_hns[2] UNTESTED** — untestable: GoldenrodCity_UndergroundSwitches_hns cannot be loaded by the engine (see load check)

### `GoldenrodCity_hns`

*Tier: story-trigger map — 14 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (28, 36) | MB_ANIMATED_DOOR | GoldenrodCity_PokemonCenter_hns | (9, 9) | MB_SOUTH_ARROW_WARP | (9, 9) | (9, 9) | UP (UP) | yes | same door | **OK** |
| 1 | (14, 33) | MB_ANIMATED_DOOR | GoldenrodCity_BillsHouse_hns | (4, 8) | MB_SOUTH_ARROW_WARP | (4, 8) | (4, 8) | UP (UP) | yes | same door | **OK** |
| 2 | (21, 38) | MB_ANIMATED_DOOR | GoldenrodCity_UndergroundEntrance_hns | (5, 7) | MB_SOUTH_ARROW_WARP | (5, 7) | (5, 7) | UP (UP) | yes | same door | **OK** |
| 3 | (20, 12) | MB_ANIMATED_DOOR | GoldenrodCity_UndergroundEntrance_hns | (22, 7) | MB_SOUTH_ARROW_WARP | (22, 7) | (22, 7) | UP (UP) | yes | same door | **OK** |
| 4 | (29, 13) | MB_ANIMATED_DOOR | GoldenrodCity_House1_hns | (4, 8) | MB_SOUTH_ARROW_WARP | (4, 8) | (4, 8) | UP (UP) | yes | same door | **OK** |
| 5 | (39, 13) | MB_ANIMATED_DOOR | GoldenrodCity_Gym_hns | (9, 22) | MB_SOUTH_ARROW_WARP | (9, 22) | (9, 22) | UP (UP) | yes | same door | **OK** |
| 6 | (44, 11) | MB_ANIMATED_DOOR | GoldenrodCity_FlowerShop_hns | (6, 9) | MB_SOUTH_ARROW_WARP | (6, 9) | (6, 9) | UP (UP) | yes | same door | **OK** |
| 7 | (48, 15) | MB_ANIMATED_DOOR | GoldenrodCity_House2_hns | (4, 8) | MB_SOUTH_ARROW_WARP | (4, 8) | (4, 8) | UP (UP) | yes | same door | **OK** |
| 8 | (16, 22) | MB_ANIMATED_DOOR | GoldenrodCity_RadioTower_1F_hns | (9, 10) | MB_SOUTH_ARROW_WARP | (9, 10) | (9, 10) | UP (UP) | yes | same door | **OK** |
| 9 | (24, 21) | MB_ANIMATED_DOOR | GoldenrodCity_TrainStation_hns | (16, 26) | MB_SOUTH_ARROW_WARP | (16, 26) | (16, 26) | UP (UP) | yes | same door | **OK** |
| 10 | (46, 28) | MB_ANIMATED_DOOR | GoldenrodCity_House3_hns | (4, 8) | MB_SOUTH_ARROW_WARP | (4, 8) | (4, 8) | UP (UP) | yes | same door | **OK** |
| 11 | (28, 29) | MB_ANIMATED_DOOR | GoldenrodCity_GameCorner_hns | (2, 12) | MB_SOUTH_ARROW_WARP | (2, 12) | (2, 12) | UP (UP) | yes | same door | **OK** |
| 12 | (39, 36) | MB_ANIMATED_DOOR | GoldenrodCity_DepartmentStore_1F_hns | (15, 11) | MB_SOUTH_ARROW_WARP | (15, 11) | (15, 11) | UP (UP) | yes | same door | **OK** |
| 13 | (44, 38) | MB_ANIMATED_DOOR | GoldenrodCity_BikeShop_hns | (5, 8) | MB_SOUTH_ARROW_WARP | (5, 8) | (5, 8) | UP (UP) | yes | same door | **OK** |


### `House_GenericA_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 9) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | (4, 9) | (4, 9) | UP (UP) | yes | same door | **OK** |


### `House_GenericB_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 9) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | (4, 9) | (4, 9) | UP (UP) | yes | same door | **OK** |


### `IlexForest_hns`

*Tier: story-trigger map — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (22, 63) | MB_EAST_ARROW_WARP | Route2_ViridianForest_SouthEntrance_Frlg | (7, 1) | MB_NON_ANIMATED_DOOR | (7, 1) | (7, 2) | RIGHT (DOWN) | yes | same door | **OK** |
| 1 | (20, 15) | MB_NORTH_ARROW_WARP | Route2_ViridianForest_NorthEntrance_Frlg | (7, 9) | MB_SOUTH_ARROW_WARP | (7, 9) | (7, 9) | UP (UP) | yes | same door | **OK** |


### `IndigoPlateau_PokemonCenter_hns`

*Tier: story-trigger map — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (19, 16) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | (19, 16) | (19, 16) | UP (UP) | yes | same door | **OK** |


### `IndigoPlateau_hns`

*Tier: region trail endpoint — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (11, 6) | MB_ANIMATED_DOOR | IndigoPlateau_PokemonCenter_hns | (19, 16) | MB_SOUTH_ARROW_WARP | (19, 16) | (19, 16) | UP (UP) | yes | same door | **OK** |


### `LavenderTown_Frlg`

*Tier: donor town/cave (vanilla base) — 6 warp(s), 3 connection(s), 9 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (18, 6) | MB_NON_ANIMATED_DOOR | PokemonTower_1F_Frlg | (11, 18) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 5) | MB_ANIMATED_DOOR | LavenderTown_PokemonCenter_1F_Frlg | (7, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (10, 11) | MB_ANIMATED_DOOR | LavenderTown_VolunteerPokemonHouse_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (5, 16) | MB_ANIMATED_DOOR | LavenderTown_House1_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (10, 16) | MB_ANIMATED_DOOR | LavenderTown_House2_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (20, 15) | MB_ANIMATED_DOOR | LavenderTown_Mart_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **LavenderTown_Frlg[0] UNTESTED** — untestable: LavenderTown_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_Frlg[1] UNTESTED** — untestable: LavenderTown_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_Frlg[2] UNTESTED** — untestable: LavenderTown_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_Frlg[3] UNTESTED** — untestable: LavenderTown_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_Frlg[4] UNTESTED** — untestable: LavenderTown_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_Frlg[5] UNTESTED** — untestable: LavenderTown_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_Frlg conn[0] up/0 -> Route10_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **LavenderTown_Frlg conn[1] down/0 -> Route12_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **LavenderTown_Frlg conn[2] left/0 -> Route8_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `LavenderTown_House1_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | LavenderTown_Frlg | (5, 16) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | LavenderTown_Frlg | (5, 16) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | LavenderTown_Frlg | (5, 16) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **LavenderTown_House1_Frlg[0] UNTESTED** — untestable: LavenderTown_House1_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_House1_Frlg[1] UNTESTED** — untestable: LavenderTown_House1_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_House1_Frlg[2] UNTESTED** — untestable: LavenderTown_House1_Frlg cannot be loaded by the engine (see load check)

### `LavenderTown_House2_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | LavenderTown_Frlg | (10, 16) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | LavenderTown_Frlg | (10, 16) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | LavenderTown_Frlg | (10, 16) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **LavenderTown_House2_Frlg[0] UNTESTED** — untestable: LavenderTown_House2_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_House2_Frlg[1] UNTESTED** — untestable: LavenderTown_House2_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_House2_Frlg[2] UNTESTED** — untestable: LavenderTown_House2_Frlg cannot be loaded by the engine (see load check)

### `LavenderTown_Mart_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | LavenderTown_Frlg | (20, 15) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | LavenderTown_Frlg | (20, 15) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | LavenderTown_Frlg | (20, 15) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **LavenderTown_Mart_Frlg[0] UNTESTED** — untestable: LavenderTown_Mart_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_Mart_Frlg[1] UNTESTED** — untestable: LavenderTown_Mart_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_Mart_Frlg[2] UNTESTED** — untestable: LavenderTown_Mart_Frlg cannot be loaded by the engine (see load check)

### `LavenderTown_PokemonCenter_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 8) | MB_NORMAL | LavenderTown_Frlg | (6, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (7, 8) | MB_SOUTH_ARROW_WARP | LavenderTown_Frlg | (6, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 8) | MB_NORMAL | LavenderTown_Frlg | (6, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (1, 6) | MB_UP_ESCALATOR | LavenderTown_PokemonCenter_2F_Frlg | (1, 6) | MB_UP_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |

* **LavenderTown_PokemonCenter_1F_Frlg[0] UNTESTED** — untestable: LavenderTown_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_PokemonCenter_1F_Frlg[1] UNTESTED** — untestable: LavenderTown_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_PokemonCenter_1F_Frlg[2] UNTESTED** — untestable: LavenderTown_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_PokemonCenter_1F_Frlg[3] UNTESTED** — untestable: LavenderTown_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)

### `LavenderTown_PokemonCenter_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_UP_ESCALATOR | LavenderTown_PokemonCenter_1F_Frlg | (1, 6) | MB_UP_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 1) | MB_NORMAL | UnionRoom_Frlg | (7, 11) | MB_BRIDGE_OVER_OCEAN | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 1) | MB_NORMAL | TradeCenter_Frlg | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **LavenderTown_PokemonCenter_2F_Frlg[0] UNTESTED** — untestable: LavenderTown_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_PokemonCenter_2F_Frlg[1] UNTESTED** — untestable: LavenderTown_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_PokemonCenter_2F_Frlg[2] UNTESTED** — untestable: LavenderTown_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)

### `LavenderTown_VolunteerPokemonHouse_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | LavenderTown_Frlg | (10, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | LavenderTown_Frlg | (10, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | LavenderTown_Frlg | (10, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **LavenderTown_VolunteerPokemonHouse_Frlg[0] UNTESTED** — untestable: LavenderTown_VolunteerPokemonHouse_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_VolunteerPokemonHouse_Frlg[1] UNTESTED** — untestable: LavenderTown_VolunteerPokemonHouse_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_VolunteerPokemonHouse_Frlg[2] UNTESTED** — untestable: LavenderTown_VolunteerPokemonHouse_Frlg cannot be loaded by the engine (see load check)

### `LavenderTown_hns`

*Tier: story-trigger map — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 6) | MB_ANIMATED_DOOR | LavenderTown_Mart_Frlg | (3, 7) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (9, 6) | MB_ANIMATED_DOOR | LavenderTown_PokemonCenter_1F_Frlg | (6, 8) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 13) | MB_ANIMATED_DOOR | LavenderTown_House1_Frlg | (3, 7) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (5, 19) | MB_ANIMATED_DOOR | LavenderTown_House2_Frlg | (3, 7) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |

* **LavenderTown_hns[0] UNTESTED** — untestable: LavenderTown_Mart_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_hns[1] UNTESTED** — untestable: LavenderTown_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_hns[2] UNTESTED** — untestable: LavenderTown_House1_Frlg cannot be loaded by the engine (see load check)
* **LavenderTown_hns[3] UNTESTED** — untestable: LavenderTown_House2_Frlg cannot be loaded by the engine (see load check)

### `Mart_Johto_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | (4, 7) | (4, 7) | UP (UP) | yes | same door | **OK** |


### `Mart_Kanto_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | (4, 7) | (4, 7) | UP (UP) | yes | same door | **OK** |


### `MeteorFalls_1F_1R`

*Tier: region trail endpoint — 6 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (27, 18) | MB_SOUTH_ARROW_WARP | MeteorFalls_1F_1R | (27, 18) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 1 | (6, 39) | MB_SOUTH_ARROW_WARP | Route115 | (27, 37) | MB_NON_ANIMATED_DOOR | (27, 37) | (27, 38) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (10, 3) | MB_NON_ANIMATED_DOOR | MeteorFalls_1F_2R | (10, 29) | MB_SOUTH_ARROW_WARP | (10, 29) | (10, 29) | UP (UP) | yes | same door | **OK** |
| 3 | (5, 4) | MB_LADDER | MeteorFalls_B1F_1R | (3, 23) | MB_LADDER | (3, 23) | (3, 23) | UP (KEEP) | yes | same door | **OK** |
| 4 | (26, 28) | MB_NON_ANIMATED_DOOR | MeteorFalls_B1F_1R | (20, 36) | MB_SOUTH_ARROW_WARP | (20, 36) | (20, 36) | UP (UP) | yes | same door | **OK** |
| 5 | (4, 2) | MB_NORMAL | MeteorFalls_StevensCave | (10, 29) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |

* **MeteorFalls_1F_1R[0] ISSUE** — stepping DOWN from (27,17) onto (27,18) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MeteorFalls_1F_1R_0_nowarp.png`
* **MeteorFalls_1F_1R[5] ISSUE** — stepping UP from (4,3) onto (4,2) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MeteorFalls_1F_1R_5_nowarp.png`

### `MeteorFalls_1F_2R`

*Tier: other / unclassified base — 4 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 29) | MB_SOUTH_ARROW_WARP | MeteorFalls_1F_1R | (10, 3) | MB_NON_ANIMATED_DOOR | (10, 3) | (10, 4) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 14) | MB_LADDER | MeteorFalls_B1F_1R | (5, 6) | MB_LADDER | (5, 6) | (5, 6) | UP (KEEP) | yes | same door | **OK** |
| 2 | (7, 20) | MB_LADDER | MeteorFalls_B1F_1R | (7, 11) | MB_LADDER | (7, 11) | (7, 11) | UP (KEEP) | yes | same door | **OK** |
| 3 | (21, 23) | MB_LADDER | MeteorFalls_B1F_1R | (18, 15) | MB_LADDER | (18, 15) | (18, 15) | UP (KEEP) | yes | same door | **OK** |


### `MeteorFalls_B1F_1R`

*Tier: other / unclassified base — 6 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 6) | MB_LADDER | MeteorFalls_1F_2R | (4, 14) | MB_LADDER | (4, 14) | (4, 14) | UP (KEEP) | yes | same door | **OK** |
| 1 | (7, 11) | MB_LADDER | MeteorFalls_1F_2R | (7, 20) | MB_LADDER | (7, 20) | (7, 20) | UP (KEEP) | yes | same door | **OK** |
| 2 | (18, 15) | MB_LADDER | MeteorFalls_1F_2R | (21, 23) | MB_LADDER | (21, 23) | (21, 23) | UP (KEEP) | yes | same door | **OK** |
| 3 | (17, 3) | MB_NON_ANIMATED_DOOR | MeteorFalls_B1F_2R | (5, 15) | MB_SOUTH_ARROW_WARP | (5, 15) | (5, 15) | UP (UP) | yes | same door | **OK** |
| 4 | (3, 23) | MB_LADDER | MeteorFalls_1F_1R | (5, 4) | MB_LADDER | (5, 4) | (5, 4) | UP (KEEP) | yes | same door | **OK** |
| 5 | (20, 36) | MB_SOUTH_ARROW_WARP | MeteorFalls_1F_1R | (26, 28) | MB_NON_ANIMATED_DOOR | (26, 28) | (26, 29) | DOWN (DOWN) | yes | same door | **OK** |


### `MeteorFalls_B1F_2R`

*Tier: other / unclassified base — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 15) | MB_SOUTH_ARROW_WARP | MeteorFalls_B1F_1R | (17, 3) | MB_NON_ANIMATED_DOOR | (17, 3) | (17, 4) | DOWN (DOWN) | yes | same door | **OK** |


### `MeteorFalls_StevensCave`

*Tier: other / unclassified base — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 29) | MB_SOUTH_ARROW_WARP | MeteorFalls_1F_1R | (4, 2) | MB_NORMAL | (4, 2) | (4, 2) | DOWN (DOWN) | yes | inconclusive | **ISSUE** |

* **MeteorFalls_StevensCave[0] ISSUE** — lands on a solid tile (MB_NORMAL) at (4,2); (note) INCONCLUSIVE return: no side of the return warp MeteorFalls_1F_1R[5] at (4,2) triggered a warp (tried ['UP'])
  * screenshot: `plastic_ox/demo/shots/warp_v1/MeteorFalls_StevensCave_0_issue.png`

### `MossdeepCity`

*Tier: story-trigger map — 10 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (28, 9) | MB_ANIMATED_DOOR | MossdeepCity_House1 | (3, 7) | MB_SOUTH_ARROW_WARP | (3, 7) | (3, 7) | UP (UP) | yes | same door | **OK** |
| 1 | (38, 9) | MB_ANIMATED_DOOR | MossdeepCity_Gym | (6, 35) | MB_SOUTH_ARROW_WARP | (6, 35) | (6, 35) | UP (UP) | yes | same door | **OK** |
| 2 | (28, 16) | MB_ANIMATED_DOOR | MossdeepCity_PokemonCenter_1F | (7, 8) | MB_SOUTH_ARROW_WARP | (7, 8) | (7, 8) | UP (UP) | yes | same door | **OK** |
| 3 | (67, 25) | MB_ANIMATED_DOOR | MossdeepCity_House2 | (3, 8) | MB_SOUTH_ARROW_WARP | (3, 8) | (3, 8) | UP (UP) | yes | same door | **OK** |
| 4 | (37, 18) | MB_ANIMATED_DOOR | MossdeepCity_Mart | (3, 7) | MB_SOUTH_ARROW_WARP | (3, 7) | (3, 7) | UP (UP) | yes | same door | **OK** |
| 5 | (49, 6) | MB_ANIMATED_DOOR | MossdeepCity_House3 | (3, 7) | MB_SOUTH_ARROW_WARP | (3, 7) | (3, 7) | UP (UP) | yes | same door | **OK** |
| 6 | (19, 10) | MB_ANIMATED_DOOR | MossdeepCity_StevensHouse | (3, 7) | MB_SOUTH_ARROW_WARP | (3, 7) | (3, 7) | UP (UP) | yes | same door | **OK** |
| 7 | (18, 16) | MB_ANIMATED_DOOR | MossdeepCity_House4 | (3, 7) | MB_SOUTH_ARROW_WARP | (3, 7) | (3, 7) | UP (UP) | yes | same door | **OK** |
| 8 | (64, 15) | MB_ANIMATED_DOOR | MossdeepCity_SpaceCenter_1F | (7, 9) | MB_SOUTH_ARROW_WARP | (7, 9) | (7, 9) | UP (UP) | yes | same door | **OK** |
| 9 | (36, 24) | MB_ANIMATED_DOOR | MossdeepCity_GameCorner_1F | (5, 9) | MB_SOUTH_ARROW_WARP | (5, 9) | (5, 9) | UP (UP) | yes | same door | **OK** |


### `MossdeepCity_GameCorner_1F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 9) | MB_SOUTH_ARROW_WARP | MossdeepCity | (36, 24) | MB_ANIMATED_DOOR | (36, 24) | (36, 25) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 9) | MB_SOUTH_ARROW_WARP | MossdeepCity | (36, 24) | MB_ANIMATED_DOOR | (36, 24) | (36, 25) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (2, 0) | MB_NORMAL | MossdeepCity_GameCorner_B1F | (3, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |

* **MossdeepCity_GameCorner_1F[2] ISSUE** — stepping UP from (2,4) onto (2,0) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_GameCorner_1F_2_nowarp.png`

### `MossdeepCity_GameCorner_B1F`

*Tier: other / unclassified base — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 1) | MB_NON_ANIMATED_DOOR | MossdeepCity_GameCorner_1F | (2, 0) | MB_NORMAL | (2, 0) | (2, 0) | UP (DOWN) | NO | inconclusive | **ISSUE** |

* **MossdeepCity_GameCorner_B1F[0] ISSUE** — lands on a solid tile (MB_NORMAL) at (2,0); player is wedged on the landing tile (2,0); (note) arrival facing reads as the travel direction UP; the player is still completing the warp step off a MB_NORMAL; (note) arrival facing DOWN points into a blocked tile (2,1); (note) INCONCLUSIVE return: no side of the return warp MossdeepCity_GameCorner_1F[2] at (2,0) triggered a warp (tried ['UP', 'LEFT'])
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_GameCorner_B1F_0_issue.png`

### `MossdeepCity_Gym`

*Tier: other / unclassified base — 14 warp(s), 0 connection(s), 12 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 35) | MB_SOUTH_ARROW_WARP | MossdeepCity | (38, 9) | MB_ANIMATED_DOOR | (38, 9) | (38, 10) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (7, 35) | MB_SOUTH_ARROW_WARP | MossdeepCity | (38, 9) | MB_ANIMATED_DOOR | (38, 9) | (38, 10) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (3, 28) | MB_MOSSDEEP_GYM_WARP | MossdeepCity_Gym | (1, 23) | MB_MOSSDEEP_GYM_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 3 | (1, 23) | MB_MOSSDEEP_GYM_WARP | MossdeepCity_Gym | (3, 28) | MB_MOSSDEEP_GYM_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 4 | (7, 18) | MB_MOSSDEEP_GYM_WARP | MossdeepCity_Gym | (8, 12) | MB_MOSSDEEP_GYM_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 5 | (8, 12) | MB_MOSSDEEP_GYM_WARP | MossdeepCity_Gym | (7, 18) | MB_MOSSDEEP_GYM_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 6 | (9, 18) | MB_MOSSDEEP_GYM_WARP | MossdeepCity_Gym | (23, 20) | MB_MOSSDEEP_GYM_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 7 | (23, 20) | MB_MOSSDEEP_GYM_WARP | MossdeepCity_Gym | (9, 18) | MB_MOSSDEEP_GYM_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 8 | (1, 33) | MB_MOSSDEEP_GYM_WARP | MossdeepCity_Gym | (20, 24) | MB_MOSSDEEP_GYM_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 9 | (20, 24) | MB_MOSSDEEP_GYM_WARP | MossdeepCity_Gym | (1, 33) | MB_MOSSDEEP_GYM_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 10 | (11, 3) | MB_MOSSDEEP_GYM_WARP | MossdeepCity_Gym | (11, 35) | MB_MOSSDEEP_GYM_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 11 | (11, 35) | MB_MOSSDEEP_GYM_WARP | MossdeepCity_Gym | (11, 3) | MB_MOSSDEEP_GYM_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 12 | (13, 32) | MB_MOSSDEEP_GYM_WARP | MossdeepCity_Gym | (21, 10) | MB_MOSSDEEP_GYM_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 13 | (21, 10) | MB_MOSSDEEP_GYM_WARP | MossdeepCity_Gym | (13, 32) | MB_MOSSDEEP_GYM_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |

* **MossdeepCity_Gym[2] ISSUE** — stepping UP from (3,29) onto (3,28) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_Gym_2_nowarp.png`
* **MossdeepCity_Gym[3] ISSUE** — stepping DOWN from (1,22) onto (1,23) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_Gym_3_nowarp.png`
* **MossdeepCity_Gym[4] ISSUE** — stepping LEFT from (8,18) onto (7,18) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_Gym_4_nowarp.png`
* **MossdeepCity_Gym[5] ISSUE** — stepping DOWN from (8,11) onto (8,12) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_Gym_5_nowarp.png`
* **MossdeepCity_Gym[6] ISSUE** — stepping RIGHT from (8,18) onto (9,18) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_Gym_6_nowarp.png`
* **MossdeepCity_Gym[7] ISSUE** — stepping UP from (23,21) onto (23,20) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_Gym_7_nowarp.png`
* **MossdeepCity_Gym[8] ISSUE** — stepping DOWN from (1,32) onto (1,33) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_Gym_8_nowarp.png`
* **MossdeepCity_Gym[9] ISSUE** — stepping LEFT from (21,24) onto (20,24) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_Gym_9_nowarp.png`
* **MossdeepCity_Gym[10] ISSUE** — stepping UP from (11,4) onto (11,3) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_Gym_10_nowarp.png`
* **MossdeepCity_Gym[11] ISSUE** — stepping DOWN from (11,34) onto (11,35) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_Gym_11_nowarp.png`
* **MossdeepCity_Gym[12] ISSUE** — stepping UP from (13,33) onto (13,32) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_Gym_12_nowarp.png`
* **MossdeepCity_Gym[13] ISSUE** — stepping DOWN from (21,9) onto (21,10) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/MossdeepCity_Gym_13_nowarp.png`

### `MossdeepCity_House1`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_SOUTH_ARROW_WARP | MossdeepCity | (28, 9) | MB_ANIMATED_DOOR | (28, 9) | (28, 10) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | MossdeepCity | (28, 9) | MB_ANIMATED_DOOR | (28, 9) | (28, 10) | DOWN (DOWN) | yes | same door | **OK** |


### `MossdeepCity_House2`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 8) | MB_SOUTH_ARROW_WARP | MossdeepCity | (67, 25) | MB_ANIMATED_DOOR | (67, 25) | (67, 26) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 8) | MB_SOUTH_ARROW_WARP | MossdeepCity | (67, 25) | MB_ANIMATED_DOOR | (67, 25) | (67, 26) | DOWN (DOWN) | yes | same door | **OK** |


### `MossdeepCity_House3`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_SOUTH_ARROW_WARP | MossdeepCity | (49, 6) | MB_ANIMATED_DOOR | (49, 6) | (49, 7) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | MossdeepCity | (49, 6) | MB_ANIMATED_DOOR | (49, 6) | (49, 7) | DOWN (DOWN) | yes | same door | **OK** |


### `MossdeepCity_House4`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | MossdeepCity | (18, 16) | MB_ANIMATED_DOOR | (18, 16) | (18, 17) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (3, 7) | MB_SOUTH_ARROW_WARP | MossdeepCity | (18, 16) | MB_ANIMATED_DOOR | (18, 16) | (18, 17) | DOWN (DOWN) | yes | same door | **OK** |


### `MossdeepCity_Mart`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_SOUTH_ARROW_WARP | MossdeepCity | (37, 18) | MB_ANIMATED_DOOR | (37, 18) | (37, 19) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | MossdeepCity | (37, 18) | MB_ANIMATED_DOOR | (37, 18) | (37, 19) | DOWN (DOWN) | yes | same door | **OK** |


### `MossdeepCity_PokemonCenter_1F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 8) | MB_SOUTH_ARROW_WARP | MossdeepCity | (28, 16) | MB_ANIMATED_DOOR | (28, 16) | (28, 17) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | MossdeepCity | (28, 16) | MB_ANIMATED_DOOR | (28, 16) | (28, 17) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (1, 6) | MB_UP_ESCALATOR | MossdeepCity_PokemonCenter_2F | (1, 6) | MB_DOWN_ESCALATOR | (1, 6) | (2, 6) | LEFT (DOWN) | yes | same door | **OK** |


### `MossdeepCity_PokemonCenter_2F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | MossdeepCity_PokemonCenter_1F | (1, 6) | MB_UP_ESCALATOR | (1, 6) | (2, 6) | LEFT (DOWN) | yes | same door | **OK** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom | (7, 11) | MB_BRIDGE_OVER_OCEAN | (7, 11) | (7, 11) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter | (5, 8) | MB_SOUTH_ARROW_WARP | (5, 8) | (5, 8) | UP (UP) | yes | same door | **OK** |


### `MossdeepCity_SpaceCenter_1F`

*Tier: story-trigger map — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 9) | MB_SOUTH_ARROW_WARP | MossdeepCity | (64, 15) | MB_ANIMATED_DOOR | (64, 15) | (64, 16) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (8, 9) | MB_SOUTH_ARROW_WARP | MossdeepCity | (64, 15) | MB_ANIMATED_DOOR | (64, 15) | (64, 16) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (13, 1) | MB_NON_ANIMATED_DOOR | MossdeepCity_SpaceCenter_2F | (13, 1) | MB_NON_ANIMATED_DOOR | (13, 1) | (13, 2) | UP (DOWN) | yes | same door | **OK** |


### `MossdeepCity_SpaceCenter_2F`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (13, 1) | MB_NON_ANIMATED_DOOR | MossdeepCity_SpaceCenter_1F | (13, 1) | MB_NON_ANIMATED_DOOR | (13, 1) | (13, 2) | UP (DOWN) | yes | same door | **OK** |


### `MossdeepCity_StevensHouse`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_SOUTH_ARROW_WARP | MossdeepCity | (19, 10) | MB_ANIMATED_DOOR | (19, 10) | (19, 11) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | MossdeepCity | (19, 10) | MB_ANIMATED_DOOR | (19, 10) | (19, 11) | DOWN (DOWN) | yes | same door | **OK** |


### `MtMoon_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 6) | MB_LADDER | MtMoon_B1F_Frlg | (3, 3) | MB_LADDER | (3, 3) | (3, 3) | UP (KEEP) | yes | same door | **OK** |
| 1 | (19, 14) | MB_LADDER | MtMoon_B1F_Frlg | (25, 4) | MB_LADDER | (25, 4) | (25, 4) | UP (KEEP) | yes | same door | **OK** |
| 2 | (31, 16) | MB_LADDER | MtMoon_B1F_Frlg | (43, 21) | MB_LADDER | (43, 21) | (43, 21) | UP (KEEP) | yes | same door | **OK** |
| 3 | (18, 37) | MB_SOUTH_ARROW_WARP | Route44_hns | (68, 13) | MB_NORMAL | (68, 13) | (68, 13) | DOWN (DOWN) | yes | same door | **OK** |


### `MtMoon_B1F_Frlg`

*Tier: donor town/cave (vanilla base) — 8 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 3) | MB_LADDER | MtMoon_1F_Frlg | (5, 6) | MB_LADDER | (5, 6) | (5, 6) | UP (KEEP) | yes | same door | **OK** |
| 1 | (25, 4) | MB_LADDER | MtMoon_1F_Frlg | (19, 14) | MB_LADDER | (19, 14) | (19, 14) | UP (KEEP) | yes | same door | **OK** |
| 2 | (43, 21) | MB_LADDER | MtMoon_1F_Frlg | (31, 16) | MB_LADDER | (31, 16) | (31, 16) | UP (KEEP) | yes | same door | **OK** |
| 3 | (22, 18) | MB_LADDER | MtMoon_B2F_Frlg | (25, 21) | MB_LADDER | (25, 21) | (25, 21) | DOWN (KEEP) | yes | same door | **OK** |
| 4 | (17, 5) | MB_LADDER | MtMoon_B2F_Frlg | (31, 11) | MB_LADDER | (31, 11) | (31, 11) | DOWN (KEEP) | yes | same door | **OK** |
| 5 | (26, 36) | MB_LADDER | MtMoon_B2F_Frlg | (17, 31) | MB_LADDER | (17, 31) | (17, 31) | DOWN (KEEP) | yes | same door | **OK** |
| 6 | (39, 4) | MB_LADDER | MtMoon_B2F_Frlg | (5, 10) | MB_LADDER | (5, 10) | (5, 10) | UP (KEEP) | yes | same door | **OK** |
| 7 | (45, 4) | MB_LADDER | Route33_hns | (27, 17) | MB_NON_ANIMATED_DOOR | (27, 17) | (27, 18) | UP (DOWN) | yes | same door | **OK** |


### `MtMoon_B2F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (25, 21) | MB_LADDER | MtMoon_B1F_Frlg | (22, 18) | MB_LADDER | (22, 18) | (22, 18) | UP (KEEP) | yes | same door | **OK** |
| 1 | (31, 11) | MB_LADDER | MtMoon_B1F_Frlg | (17, 5) | MB_LADDER | (17, 5) | (17, 5) | UP (KEEP) | yes | same door | **OK** |
| 2 | (17, 31) | MB_LADDER | MtMoon_B1F_Frlg | (26, 36) | MB_LADDER | (26, 36) | (26, 36) | UP (KEEP) | yes | same door | **OK** |
| 3 | (5, 10) | MB_LADDER | MtMoon_B1F_Frlg | (39, 4) | MB_LADDER | (39, 4) | (39, 4) | UP (KEEP) | yes | same door | **OK** |


### `NewMauville_Entrance`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 6) | MB_SOUTH_ARROW_WARP | Route110 | (35, 24) | MB_NON_ANIMATED_DOOR | (35, 24) | (35, 25) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 1) | MB_NON_ANIMATED_DOOR | NewMauville_Inside | (32, 33) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |

* **NewMauville_Entrance[1] ISSUE** — stepping UP from (4,2) onto (4,1) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/NewMauville_Entrance_1_nowarp.png`

### `NewMauville_Inside`

*Tier: other / unclassified base — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (32, 33) | MB_NON_ANIMATED_DOOR | NewMauville_Entrance | (4, 1) | MB_NON_ANIMATED_DOOR | (4, 1) | (4, 1) | UP (DOWN) | yes | inconclusive | **ISSUE** |

* **NewMauville_Inside[0] ISSUE** — lands on a solid tile (MB_NORMAL) at (4,1); (note) arrival facing reads as the travel direction UP; the player is still completing the warp step off a MB_NORMAL; (note) INCONCLUSIVE return: no side of the return warp NewMauville_Entrance[1] at (4,1) triggered a warp (tried ['UP'])
  * screenshot: `plastic_ox/demo/shots/warp_v1/NewMauville_Inside_0_issue.png`

### `OldaleTown`

*Tier: region trail endpoint — 4 warp(s), 3 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 7) | MB_ANIMATED_DOOR | OldaleTown_House1 | (3, 8) | MB_SOUTH_ARROW_WARP | (3, 8) | (3, 8) | UP (UP) | yes | same door | **OK** |
| 1 | (15, 16) | MB_ANIMATED_DOOR | OldaleTown_House2 | (3, 7) | MB_SOUTH_ARROW_WARP | (3, 7) | (3, 7) | UP (UP) | yes | same door | **OK** |
| 2 | (6, 16) | MB_ANIMATED_DOOR | OldaleTown_PokemonCenter_1F | (7, 8) | MB_SOUTH_ARROW_WARP | (7, 8) | (7, 8) | UP (UP) | yes | same door | **OK** |
| 3 | (14, 6) | MB_ANIMATED_DOOR | OldaleTown_Mart | (3, 7) | MB_SOUTH_ARROW_WARP | (3, 7) | (3, 7) | UP (UP) | yes | same door | **OK** |

* **OldaleTown conn[0] down/0 -> Route101 OK** — outward:OK (handed over to Route101 at (9,0)); inward:OK (returned to OldaleTown at (9,19))
* **OldaleTown conn[1] left/-6 -> Route29_hns OK** — outward:OK (handed over to Route29_hns at (69,16)); inward:OK (returned to OldaleTown at (0,10))
* **OldaleTown conn[2] up/0 -> Route103 OK** — outward:OK (handed over to Route103 at (9,21)); inward:OK (returned to OldaleTown at (9,0))

### `OldaleTown_House1`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 8) | MB_SOUTH_ARROW_WARP | OldaleTown | (5, 7) | MB_ANIMATED_DOOR | (5, 7) | (5, 8) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 8) | MB_SOUTH_ARROW_WARP | OldaleTown | (5, 7) | MB_ANIMATED_DOOR | (5, 7) | (5, 8) | DOWN (DOWN) | yes | same door | **OK** |


### `OldaleTown_House2`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_SOUTH_ARROW_WARP | OldaleTown | (15, 16) | MB_ANIMATED_DOOR | (15, 16) | (15, 17) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | OldaleTown | (15, 16) | MB_ANIMATED_DOOR | (15, 16) | (15, 17) | DOWN (DOWN) | yes | same door | **OK** |


### `OldaleTown_Mart`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_SOUTH_ARROW_WARP | OldaleTown | (14, 6) | MB_ANIMATED_DOOR | (14, 6) | (14, 7) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | OldaleTown | (14, 6) | MB_ANIMATED_DOOR | (14, 6) | (14, 7) | DOWN (DOWN) | yes | same door | **OK** |


### `OldaleTown_PokemonCenter_1F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 8) | MB_SOUTH_ARROW_WARP | OldaleTown | (6, 16) | MB_ANIMATED_DOOR | (6, 16) | (6, 17) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | OldaleTown | (6, 16) | MB_ANIMATED_DOOR | (6, 16) | (6, 17) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (1, 6) | MB_UP_ESCALATOR | OldaleTown_PokemonCenter_2F | (1, 6) | MB_DOWN_ESCALATOR | (1, 6) | (2, 6) | LEFT (DOWN) | yes | same door | **OK** |


### `OldaleTown_PokemonCenter_2F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | OldaleTown_PokemonCenter_1F | (1, 6) | MB_UP_ESCALATOR | (1, 6) | (2, 6) | LEFT (DOWN) | yes | same door | **OK** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom | (7, 11) | MB_BRIDGE_OVER_OCEAN | (7, 11) | (7, 11) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter | (5, 8) | MB_SOUTH_ARROW_WARP | (5, 8) | (5, 8) | UP (UP) | yes | same door | **OK** |


### `PalletTown_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 1 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 7) | MB_ANIMATED_DOOR | PalletTown_PlayersHouse_1F_Frlg | (4, 8) | MB_SOUTH_ARROW_WARP | (4, 8) | (4, 8) | UP (UP) | yes | same door | **OK** |
| 1 | (15, 7) | MB_ANIMATED_DOOR | PalletTown_RivalsHouse_Frlg | (4, 8) | MB_SOUTH_ARROW_WARP | (4, 8) | (4, 8) | UP (UP) | yes | same door | **OK** |
| 2 | (16, 13) | MB_ANIMATED_DOOR | PalletTown_ProfessorOaksLab_Frlg | (6, 12) | MB_SOUTH_ARROW_WARP | (6, 12) | (6, 12) | UP (UP) | yes | same door | **OK** |

* **PalletTown_Frlg conn[0] up/2 -> Route101 OK** — outward:OK (handed over to Route101 at (10,19)); inward:OK (returned to PalletTown_Frlg at (12,0))

### `PalletTown_PlayersHouse_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_NORMAL | PalletTown_Frlg | (6, 7) | MB_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |
| 1 | (4, 8) | MB_SOUTH_ARROW_WARP | PalletTown_Frlg | (6, 7) | MB_ANIMATED_DOOR | (6, 7) | (6, 8) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (10, 2) | MB_UP_RIGHT_STAIR_WARP | PalletTown_PlayersHouse_2F_Frlg | (10, 2) | MB_DOWN_LEFT_STAIR_WARP | (10, 2) | (10, 2) | RIGHT (RIGHT) | yes | same door | **OK** |
| 3 | (3, 9) | MB_NORMAL | PalletTown_Frlg | (6, 7) | MB_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |

* **PalletTown_PlayersHouse_1F_Frlg[0] ISSUE** — stepping DOWN from (5,7) onto (5,8) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/PalletTown_PlayersHouse_1F_Frlg_0_nowarp.png`
* **PalletTown_PlayersHouse_1F_Frlg[3] ISSUE** — stepping DOWN from (3,8) onto (3,9) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/PalletTown_PlayersHouse_1F_Frlg_3_nowarp.png`

### `PalletTown_PlayersHouse_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 2) | MB_DOWN_LEFT_STAIR_WARP | PalletTown_PlayersHouse_1F_Frlg | (10, 2) | MB_UP_RIGHT_STAIR_WARP | (10, 2) | (10, 2) | LEFT (LEFT) | yes | same door | **OK** |


### `PalletTown_ProfessorOaksLab_Frlg`

*Tier: story-trigger map — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 12) | MB_SOUTH_ARROW_WARP | PalletTown_Frlg | (16, 13) | MB_ANIMATED_DOOR | (16, 13) | (16, 14) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (7, 12) | MB_SOUTH_ARROW_WARP | PalletTown_Frlg | (16, 13) | MB_ANIMATED_DOOR | (16, 13) | (16, 14) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (5, 12) | MB_SOUTH_ARROW_WARP | PalletTown_Frlg | (16, 13) | MB_ANIMATED_DOOR | (16, 13) | (16, 14) | DOWN (DOWN) | yes | same door | **OK** |


### `PalletTown_RivalsHouse_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 8) | MB_SOUTH_ARROW_WARP | PalletTown_Frlg | (15, 7) | MB_ANIMATED_DOOR | (15, 7) | (15, 8) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (5, 8) | MB_NORMAL | PalletTown_Frlg | (15, 7) | MB_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |
| 2 | (3, 8) | MB_NORMAL | PalletTown_Frlg | (15, 7) | MB_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |

* **PalletTown_RivalsHouse_Frlg[1] ISSUE** — stepping DOWN from (5,7) onto (5,8) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/PalletTown_RivalsHouse_Frlg_1_nowarp.png`
* **PalletTown_RivalsHouse_Frlg[2] ISSUE** — stepping DOWN from (3,7) onto (3,8) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/PalletTown_RivalsHouse_Frlg_2_nowarp.png`

### `PewterCity_Frlg`

*Tier: donor town/cave (vanilla base) — 7 warp(s), 2 connection(s), 9 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (17, 6) | MB_NON_ANIMATED_DOOR | PewterCity_Museum_1F_Frlg | (14, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (25, 4) | MB_ANIMATED_DOOR | PewterCity_Museum_1F_Frlg | (21, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (15, 16) | MB_ANIMATED_DOOR | PewterCity_Gym_Frlg | (6, 14) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (28, 18) | MB_ANIMATED_DOOR | PewterCity_Mart_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (33, 11) | MB_ANIMATED_DOOR | PewterCity_House1_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (17, 25) | MB_ANIMATED_DOOR | PewterCity_PokemonCenter_1F_Frlg | (7, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (9, 30) | MB_ANIMATED_DOOR | PewterCity_House2_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PewterCity_Frlg[0] UNTESTED** — untestable: PewterCity_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Frlg[1] UNTESTED** — untestable: PewterCity_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Frlg[2] UNTESTED** — untestable: PewterCity_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Frlg[3] UNTESTED** — untestable: PewterCity_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Frlg[4] UNTESTED** — untestable: PewterCity_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Frlg[5] UNTESTED** — untestable: PewterCity_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Frlg[6] UNTESTED** — untestable: PewterCity_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Frlg conn[0] down/12 -> Route2_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **PewterCity_Frlg conn[1] right/10 -> Route3_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `PewterCity_Gym_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 14) | MB_NORMAL | PewterCity_Frlg | (15, 16) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 14) | MB_SOUTH_ARROW_WARP | PewterCity_Frlg | (15, 16) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (7, 14) | MB_NORMAL | PewterCity_Frlg | (15, 16) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **PewterCity_Gym_Frlg[0] UNTESTED** — untestable: PewterCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Gym_Frlg[1] UNTESTED** — untestable: PewterCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Gym_Frlg[2] UNTESTED** — untestable: PewterCity_Gym_Frlg cannot be loaded by the engine (see load check)

### `PewterCity_House1_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | PewterCity_Frlg | (33, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | PewterCity_Frlg | (33, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | PewterCity_Frlg | (33, 11) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **PewterCity_House1_Frlg[0] UNTESTED** — untestable: PewterCity_House1_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_House1_Frlg[1] UNTESTED** — untestable: PewterCity_House1_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_House1_Frlg[2] UNTESTED** — untestable: PewterCity_House1_Frlg cannot be loaded by the engine (see load check)

### `PewterCity_House2_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | PewterCity_Frlg | (9, 30) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | PewterCity_Frlg | (9, 30) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | PewterCity_Frlg | (9, 30) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **PewterCity_House2_Frlg[0] UNTESTED** — untestable: PewterCity_House2_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_House2_Frlg[1] UNTESTED** — untestable: PewterCity_House2_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_House2_Frlg[2] UNTESTED** — untestable: PewterCity_House2_Frlg cannot be loaded by the engine (see load check)

### `PewterCity_Mart_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | PewterCity_Frlg | (28, 18) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | PewterCity_Frlg | (28, 18) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | PewterCity_Frlg | (28, 18) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **PewterCity_Mart_Frlg[0] UNTESTED** — untestable: PewterCity_Mart_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Mart_Frlg[1] UNTESTED** — untestable: PewterCity_Mart_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Mart_Frlg[2] UNTESTED** — untestable: PewterCity_Mart_Frlg cannot be loaded by the engine (see load check)

### `PewterCity_Museum_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 6 warp(s), 0 connection(s), 6 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (13, 9) | MB_NORMAL | PewterCity_Frlg | (17, 6) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (14, 9) | MB_SOUTH_ARROW_WARP | PewterCity_Frlg | (17, 6) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (15, 9) | MB_NORMAL | PewterCity_Frlg | (17, 6) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (21, 9) | MB_SOUTH_ARROW_WARP | PewterCity_Frlg | (25, 4) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (22, 9) | MB_NORMAL | PewterCity_Frlg | (25, 4) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (8, 8) | MB_UP_RIGHT_STAIR_WARP | PewterCity_Museum_2F_Frlg | (11, 8) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PewterCity_Museum_1F_Frlg[0] UNTESTED** — untestable: PewterCity_Museum_1F_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Museum_1F_Frlg[1] UNTESTED** — untestable: PewterCity_Museum_1F_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Museum_1F_Frlg[2] UNTESTED** — untestable: PewterCity_Museum_1F_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Museum_1F_Frlg[3] UNTESTED** — untestable: PewterCity_Museum_1F_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Museum_1F_Frlg[4] UNTESTED** — untestable: PewterCity_Museum_1F_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_Museum_1F_Frlg[5] UNTESTED** — untestable: PewterCity_Museum_1F_Frlg cannot be loaded by the engine (see load check)

### `PewterCity_Museum_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (11, 8) | MB_DOWN_LEFT_STAIR_WARP | PewterCity_Museum_1F_Frlg | (8, 8) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PewterCity_Museum_2F_Frlg[0] UNTESTED** — untestable: PewterCity_Museum_2F_Frlg cannot be loaded by the engine (see load check)

### `PewterCity_PokemonCenter_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 8) | MB_NORMAL | PewterCity_Frlg | (17, 25) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (7, 8) | MB_SOUTH_ARROW_WARP | PewterCity_Frlg | (17, 25) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 8) | MB_NORMAL | PewterCity_Frlg | (17, 25) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (1, 6) | MB_UP_ESCALATOR | PewterCity_PokemonCenter_2F_Frlg | (1, 6) | MB_DOWN_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |

* **PewterCity_PokemonCenter_1F_Frlg[0] UNTESTED** — untestable: PewterCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_PokemonCenter_1F_Frlg[1] UNTESTED** — untestable: PewterCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_PokemonCenter_1F_Frlg[2] UNTESTED** — untestable: PewterCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_PokemonCenter_1F_Frlg[3] UNTESTED** — untestable: PewterCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)

### `PewterCity_PokemonCenter_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | PewterCity_PokemonCenter_1F_Frlg | (1, 6) | MB_UP_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom_Frlg | (7, 11) | MB_BRIDGE_OVER_OCEAN | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter_Frlg | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PewterCity_PokemonCenter_2F_Frlg[0] UNTESTED** — untestable: PewterCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_PokemonCenter_2F_Frlg[1] UNTESTED** — untestable: PewterCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **PewterCity_PokemonCenter_2F_Frlg[2] UNTESTED** — untestable: PewterCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)

### `PlasticOx_Route20East`

*Tier: plastic-ox authored — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 14) | MB_ANIMATED_DOOR | SeafoamIslands_1F_Frlg | (32, 21) | MB_SOUTH_ARROW_WARP | (32, 21) | (32, 21) | UP (UP) | yes | same door | **OK** |


### `PlasticOx_Route20West`

*Tier: plastic-ox authored — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (60, 8) | MB_ANIMATED_DOOR | SeafoamIslands_1F_Frlg | (6, 21) | MB_SOUTH_ARROW_WARP | (6, 21) | (6, 21) | UP (UP) | yes | same door | **OK** |


### `PokemonCenter_Johto_hns`

*Tier: story-trigger map — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 8) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | (7, 8) | (7, 8) | UP (UP) | yes | same door | **OK** |


### `PokemonCenter_Kanto_hns`

*Tier: story-trigger map — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 8) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | - | - | - (-) | - | inconclusive | **UNTESTED** |

* **PokemonCenter_Kanto_hns[0] UNTESTED** — MAP_DYNAMIC exit with no reachable door in the closure

### `PokemonMansion_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 10 warp(s), 0 connection(s), 9 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 33) | MB_CAVE | CinnabarIsland_Frlg | (8, 3) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |
| 1 | (8, 33) | MB_SOUTH_ARROW_WARP | CinnabarIsland_Frlg | (8, 3) | MB_NON_ANIMATED_DOOR | (8, 3) | (8, 4) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (9, 33) | MB_CAVE | CinnabarIsland_Frlg | (8, 3) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |
| 3 | (10, 13) | MB_UP_RIGHT_STAIR_WARP | PokemonMansion_2F_Frlg | (6, 14) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (25, 27) | MB_DOWN_LEFT_STAIR_WARP | PokemonMansion_B1F_Frlg | (34, 29) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (34, 33) | MB_SOUTH_ARROW_WARP | CinnabarIsland_Frlg | (8, 3) | MB_NON_ANIMATED_DOOR | (8, 3) | (8, 4) | DOWN (DOWN) | yes | WRONG MAP/TILE | **ISSUE** |
| 6 | (35, 34) | MB_NORMAL | CinnabarIsland_Frlg | (8, 3) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |
| 7 | (19, 22) | MB_CAVE | PokemonMansion_3F_Frlg | (18, 18) | MB_MT_PYRE_HOLE | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (20, 22) | MB_CAVE | PokemonMansion_3F_Frlg | (19, 18) | MB_MT_PYRE_HOLE | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (11, 13) | MB_NORMAL | PokemonMansion_2F_Frlg | (6, 14) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PokemonMansion_1F_Frlg[0] ISSUE** — stepping DOWN from (7,32) onto (7,33) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/PokemonMansion_1F_Frlg_0_nowarp.png`
* **PokemonMansion_1F_Frlg[2] ISSUE** — stepping DOWN from (9,32) onto (9,33) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/PokemonMansion_1F_Frlg_2_nowarp.png`
* **PokemonMansion_1F_Frlg[3] UNTESTED** — untestable: PokemonMansion_2F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_1F_Frlg[4] UNTESTED** — untestable: PokemonMansion_B1F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_1F_Frlg[5] ISSUE** — (note) return landed in PokemonMansion_1F_Frlg at (8,33), expected PokemonMansion_1F_Frlg at (34,33)
  * screenshot: `plastic_ox/demo/shots/warp_v1/PokemonMansion_1F_Frlg_5_return.png`
* **PokemonMansion_1F_Frlg[6] ISSUE** — stepping DOWN from (35,33) onto (35,34) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/PokemonMansion_1F_Frlg_6_nowarp.png`
* **PokemonMansion_1F_Frlg[7] UNTESTED** — untestable: PokemonMansion_3F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_1F_Frlg[8] UNTESTED** — untestable: PokemonMansion_3F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_1F_Frlg[9] UNTESTED** — untestable: PokemonMansion_2F_Frlg cannot be loaded by the engine (see load check)

### `PokemonMansion_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 5 warp(s), 0 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (9, 3) | MB_UP_RIGHT_STAIR_WARP | PokemonMansion_3F_Frlg | (8, 3) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (34, 22) | MB_UP_RIGHT_STAIR_WARP | PokemonMansion_3F_Frlg | (34, 18) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (6, 14) | MB_DOWN_LEFT_STAIR_WARP | PokemonMansion_1F_Frlg | (10, 13) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (9, 14) | MB_UP_RIGHT_STAIR_WARP | PokemonMansion_3F_Frlg | (11, 11) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (27, 17) | MB_CAVE | PokemonMansion_3F_Frlg | (23, 18) | MB_MT_PYRE_HOLE | - | - | - (-) | - | - | **UNTESTED** |

* **PokemonMansion_2F_Frlg[0] UNTESTED** — untestable: PokemonMansion_2F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_2F_Frlg[1] UNTESTED** — untestable: PokemonMansion_2F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_2F_Frlg[2] UNTESTED** — untestable: PokemonMansion_2F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_2F_Frlg[3] UNTESTED** — untestable: PokemonMansion_2F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_2F_Frlg[4] UNTESTED** — untestable: PokemonMansion_2F_Frlg cannot be loaded by the engine (see load check)

### `PokemonMansion_3F_Frlg`

*Tier: donor town/cave (vanilla base) — 8 warp(s), 0 connection(s), 8 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (8, 3) | MB_DOWN_LEFT_STAIR_WARP | PokemonMansion_2F_Frlg | (9, 3) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (34, 18) | MB_DOWN_LEFT_STAIR_WARP | PokemonMansion_2F_Frlg | (34, 22) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (11, 11) | MB_DOWN_LEFT_STAIR_WARP | PokemonMansion_2F_Frlg | (9, 14) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (18, 18) | MB_MT_PYRE_HOLE | PokemonMansion_1F_Frlg | (19, 22) | MB_CAVE | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (19, 18) | MB_MT_PYRE_HOLE | PokemonMansion_1F_Frlg | (20, 22) | MB_CAVE | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (23, 18) | MB_MT_PYRE_HOLE | PokemonMansion_2F_Frlg | (27, 17) | MB_CAVE | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (20, 18) | MB_MT_PYRE_HOLE | PokemonMansion_1F_Frlg | (20, 22) | MB_CAVE | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (24, 18) | MB_MT_PYRE_HOLE | PokemonMansion_2F_Frlg | (27, 17) | MB_CAVE | - | - | - (-) | - | - | **UNTESTED** |

* **PokemonMansion_3F_Frlg[0] UNTESTED** — untestable: PokemonMansion_3F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_3F_Frlg[1] UNTESTED** — untestable: PokemonMansion_3F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_3F_Frlg[2] UNTESTED** — untestable: PokemonMansion_3F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_3F_Frlg[3] UNTESTED** — untestable: PokemonMansion_3F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_3F_Frlg[4] UNTESTED** — untestable: PokemonMansion_3F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_3F_Frlg[5] UNTESTED** — untestable: PokemonMansion_3F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_3F_Frlg[6] UNTESTED** — untestable: PokemonMansion_3F_Frlg cannot be loaded by the engine (see load check)
* **PokemonMansion_3F_Frlg[7] UNTESTED** — untestable: PokemonMansion_3F_Frlg cannot be loaded by the engine (see load check)

### `PokemonMansion_B1F_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (34, 29) | MB_UP_RIGHT_STAIR_WARP | PokemonMansion_1F_Frlg | (25, 27) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PokemonMansion_B1F_Frlg[0] UNTESTED** — untestable: PokemonMansion_B1F_Frlg cannot be loaded by the engine (see load check)

### `PokemonTower_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 19) | MB_NORMAL | LavenderTown_Frlg | (18, 6) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (11, 18) | MB_SOUTH_ARROW_WARP | LavenderTown_Frlg | (18, 6) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (12, 19) | MB_NORMAL | LavenderTown_Frlg | (18, 6) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (18, 9) | MB_UP_RIGHT_STAIR_WARP | PokemonTower_2F_Frlg | (18, 10) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PokemonTower_1F_Frlg[0] UNTESTED** — untestable: PokemonTower_1F_Frlg cannot be loaded by the engine (see load check)
* **PokemonTower_1F_Frlg[1] UNTESTED** — untestable: PokemonTower_1F_Frlg cannot be loaded by the engine (see load check)
* **PokemonTower_1F_Frlg[2] UNTESTED** — untestable: PokemonTower_1F_Frlg cannot be loaded by the engine (see load check)
* **PokemonTower_1F_Frlg[3] UNTESTED** — untestable: PokemonTower_1F_Frlg cannot be loaded by the engine (see load check)

### `PokemonTower_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 10) | MB_UP_LEFT_STAIR_WARP | PokemonTower_3F_Frlg | (4, 10) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (18, 10) | MB_DOWN_RIGHT_STAIR_WARP | PokemonTower_1F_Frlg | (18, 9) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PokemonTower_2F_Frlg[0] UNTESTED** — untestable: PokemonTower_2F_Frlg cannot be loaded by the engine (see load check)
* **PokemonTower_2F_Frlg[1] UNTESTED** — untestable: PokemonTower_2F_Frlg cannot be loaded by the engine (see load check)

### `PokemonTower_3F_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 10) | MB_DOWN_LEFT_STAIR_WARP | PokemonTower_2F_Frlg | (4, 10) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (18, 10) | MB_UP_RIGHT_STAIR_WARP | PokemonTower_4F_Frlg | (18, 10) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PokemonTower_3F_Frlg[0] UNTESTED** — untestable: PokemonTower_3F_Frlg cannot be loaded by the engine (see load check)
* **PokemonTower_3F_Frlg[1] UNTESTED** — untestable: PokemonTower_3F_Frlg cannot be loaded by the engine (see load check)

### `PokemonTower_4F_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 10) | MB_UP_LEFT_STAIR_WARP | PokemonTower_5F_Frlg | (4, 10) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (18, 10) | MB_DOWN_RIGHT_STAIR_WARP | PokemonTower_3F_Frlg | (18, 10) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PokemonTower_4F_Frlg[0] UNTESTED** — untestable: PokemonTower_4F_Frlg cannot be loaded by the engine (see load check)
* **PokemonTower_4F_Frlg[1] UNTESTED** — untestable: PokemonTower_4F_Frlg cannot be loaded by the engine (see load check)

### `PokemonTower_5F_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 10) | MB_DOWN_LEFT_STAIR_WARP | PokemonTower_4F_Frlg | (4, 10) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (18, 10) | MB_UP_RIGHT_STAIR_WARP | PokemonTower_6F_Frlg | (18, 10) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PokemonTower_5F_Frlg[0] UNTESTED** — untestable: PokemonTower_5F_Frlg cannot be loaded by the engine (see load check)
* **PokemonTower_5F_Frlg[1] UNTESTED** — untestable: PokemonTower_5F_Frlg cannot be loaded by the engine (see load check)

### `PokemonTower_6F_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (11, 16) | MB_UP_LEFT_STAIR_WARP | PokemonTower_7F_Frlg | (11, 16) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (18, 10) | MB_DOWN_RIGHT_STAIR_WARP | PokemonTower_5F_Frlg | (18, 10) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PokemonTower_6F_Frlg[0] UNTESTED** — untestable: PokemonTower_6F_Frlg cannot be loaded by the engine (see load check)
* **PokemonTower_6F_Frlg[1] UNTESTED** — untestable: PokemonTower_6F_Frlg cannot be loaded by the engine (see load check)

### `PokemonTower_7F_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (11, 16) | MB_DOWN_LEFT_STAIR_WARP | PokemonTower_6F_Frlg | (11, 16) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **PokemonTower_7F_Frlg[0] UNTESTED** — untestable: PokemonTower_7F_Frlg cannot be loaded by the engine (see load check)

### `PowerPlant_Frlg`

*Tier: donor town/cave (vanilla base) — 5 warp(s), 0 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 39) | MB_CAVE | Route10_Frlg | (7, 40) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 38) | MB_SOUTH_ARROW_WARP | Route10_Frlg | (7, 40) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (6, 39) | MB_CAVE | Route10_Frlg | (7, 40) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (1, 11) | MB_WEST_ARROW_WARP | Route10_Frlg | (2, 37) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (0, 13) | MB_CAVE | Route10_Frlg | (7, 40) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **PowerPlant_Frlg[0] UNTESTED** — untestable: PowerPlant_Frlg cannot be loaded by the engine (see load check)
* **PowerPlant_Frlg[1] UNTESTED** — untestable: PowerPlant_Frlg cannot be loaded by the engine (see load check)
* **PowerPlant_Frlg[2] UNTESTED** — untestable: PowerPlant_Frlg cannot be loaded by the engine (see load check)
* **PowerPlant_Frlg[3] UNTESTED** — untestable: PowerPlant_Frlg cannot be loaded by the engine (see load check)
* **PowerPlant_Frlg[4] UNTESTED** — untestable: PowerPlant_Frlg cannot be loaded by the engine (see load check)

### `RockTunnel_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 6 warp(s), 0 connection(s), 6 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (17, 2) | MB_LADDER | Route10_Frlg | (8, 19) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (45, 2) | MB_LADDER | RockTunnel_B1F_Frlg | (38, 28) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (4, 2) | MB_LADDER | RockTunnel_B1F_Frlg | (33, 3) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (20, 13) | MB_LADDER | RockTunnel_B1F_Frlg | (27, 12) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (45, 21) | MB_LADDER | RockTunnel_B1F_Frlg | (2, 3) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (18, 37) | MB_SOUTH_ARROW_WARP | Route10_Frlg | (8, 57) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **RockTunnel_1F_Frlg[0] UNTESTED** — untestable: RockTunnel_1F_Frlg cannot be loaded by the engine (see load check)
* **RockTunnel_1F_Frlg[1] UNTESTED** — untestable: RockTunnel_1F_Frlg cannot be loaded by the engine (see load check)
* **RockTunnel_1F_Frlg[2] UNTESTED** — untestable: RockTunnel_1F_Frlg cannot be loaded by the engine (see load check)
* **RockTunnel_1F_Frlg[3] UNTESTED** — untestable: RockTunnel_1F_Frlg cannot be loaded by the engine (see load check)
* **RockTunnel_1F_Frlg[4] UNTESTED** — untestable: RockTunnel_1F_Frlg cannot be loaded by the engine (see load check)
* **RockTunnel_1F_Frlg[5] UNTESTED** — untestable: RockTunnel_1F_Frlg cannot be loaded by the engine (see load check)

### `RockTunnel_B1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (38, 28) | MB_LADDER | RockTunnel_1F_Frlg | (45, 2) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (33, 3) | MB_LADDER | RockTunnel_1F_Frlg | (4, 2) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (27, 12) | MB_LADDER | RockTunnel_1F_Frlg | (20, 13) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (2, 3) | MB_LADDER | RockTunnel_1F_Frlg | (45, 21) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |

* **RockTunnel_B1F_Frlg[0] UNTESTED** — untestable: RockTunnel_B1F_Frlg cannot be loaded by the engine (see load check)
* **RockTunnel_B1F_Frlg[1] UNTESTED** — untestable: RockTunnel_B1F_Frlg cannot be loaded by the engine (see load check)
* **RockTunnel_B1F_Frlg[2] UNTESTED** — untestable: RockTunnel_B1F_Frlg cannot be loaded by the engine (see load check)
* **RockTunnel_B1F_Frlg[3] UNTESTED** — untestable: RockTunnel_B1F_Frlg cannot be loaded by the engine (see load check)

### `RocketHideout_B1F_Frlg`

*Tier: donor town/cave (vanilla base) — 6 warp(s), 0 connection(s), 6 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (12, 2) | MB_UP_LEFT_STAIR_WARP | CeladonCity_GameCorner_Frlg | (15, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (17, 2) | MB_DOWN_RIGHT_STAIR_WARP | RocketHideout_B2F_Frlg | (28, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (15, 30) | MB_DOWN_RIGHT_STAIR_WARP | RocketHideout_B2F_Frlg | (23, 12) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (23, 25) | MB_NORMAL | RocketHideout_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (24, 25) | MB_ANIMATED_DOOR | RocketHideout_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (25, 25) | MB_NORMAL | RocketHideout_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **RocketHideout_B1F_Frlg[0] UNTESTED** — untestable: RocketHideout_B1F_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_B1F_Frlg[1] UNTESTED** — untestable: RocketHideout_B1F_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_B1F_Frlg[2] UNTESTED** — untestable: RocketHideout_B1F_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_B1F_Frlg[3] UNTESTED** — untestable: RocketHideout_B1F_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_B1F_Frlg[4] UNTESTED** — untestable: RocketHideout_B1F_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_B1F_Frlg[5] UNTESTED** — untestable: RocketHideout_B1F_Frlg cannot be loaded by the engine (see load check)

### `RocketHideout_B2F_Frlg`

*Tier: donor town/cave (vanilla base) — 5 warp(s), 0 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (21, 2) | MB_DOWN_RIGHT_STAIR_WARP | RocketHideout_B3F_Frlg | (18, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (28, 2) | MB_UP_RIGHT_STAIR_WARP | RocketHideout_B1F_Frlg | (17, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (23, 12) | MB_UP_RIGHT_STAIR_WARP | RocketHideout_B1F_Frlg | (15, 30) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (28, 16) | MB_ANIMATED_DOOR | RocketHideout_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (29, 16) | MB_NORMAL | RocketHideout_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **RocketHideout_B2F_Frlg[0] UNTESTED** — untestable: RocketHideout_B2F_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_B2F_Frlg[1] UNTESTED** — untestable: RocketHideout_B2F_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_B2F_Frlg[2] UNTESTED** — untestable: RocketHideout_B2F_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_B2F_Frlg[3] UNTESTED** — untestable: RocketHideout_B2F_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_B2F_Frlg[4] UNTESTED** — untestable: RocketHideout_B2F_Frlg cannot be loaded by the engine (see load check)

### `RocketHideout_B3F_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (18, 2) | MB_UP_RIGHT_STAIR_WARP | RocketHideout_B2F_Frlg | (21, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (15, 18) | MB_DOWN_LEFT_STAIR_WARP | RocketHideout_B4F_Frlg | (11, 15) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **RocketHideout_B3F_Frlg[0] UNTESTED** — untestable: RocketHideout_B3F_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_B3F_Frlg[1] UNTESTED** — untestable: RocketHideout_B3F_Frlg cannot be loaded by the engine (see load check)

### `RocketHideout_B4F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (11, 15) | MB_UP_RIGHT_STAIR_WARP | RocketHideout_B3F_Frlg | (15, 18) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (20, 23) | MB_ANIMATED_DOOR | RocketHideout_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (21, 23) | MB_NORMAL | RocketHideout_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **RocketHideout_B4F_Frlg[0] UNTESTED** — untestable: RocketHideout_B4F_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_B4F_Frlg[1] UNTESTED** — untestable: RocketHideout_B4F_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_B4F_Frlg[2] UNTESTED** — untestable: RocketHideout_B4F_Frlg cannot be loaded by the engine (see load check)

### `RocketHideout_Elevator_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 5) | MB_NORMAL | MAP_DYNAMIC | - | - | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (2, 5) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | - | - | - (-) | - | - | **UNTESTED** |

* **RocketHideout_Elevator_Frlg[0] UNTESTED** — untestable: RocketHideout_Elevator_Frlg cannot be loaded by the engine (see load check)
* **RocketHideout_Elevator_Frlg[1] UNTESTED** — untestable: RocketHideout_Elevator_Frlg cannot be loaded by the engine (see load check)

### `Route101`

*Tier: other / unclassified base — 0 warp(s), 2 connection(s), 0 finding(s).*

* **Route101 conn[0] up/0 -> OldaleTown OK** — outward:OK (handed over to OldaleTown at (9,19)); inward:OK (returned to Route101 at (9,0))
* **Route101 conn[1] down/-2 -> PalletTown_Frlg OK** — outward:OK (handed over to PalletTown_Frlg at (12,0)); inward:OK (returned to Route101 at (10,19))

### `Route103`

*Tier: region trail endpoint — 0 warp(s), 1 connection(s), 0 finding(s).*

* **Route103 conn[0] down/0 -> OldaleTown OK** — outward:OK (handed over to OldaleTown at (9,0)); inward:OK (returned to Route103 at (9,21))

### `Route10_Frlg`

*Tier: donor town/cave (vanilla base) — 5 warp(s), 2 connection(s), 7 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (8, 19) | MB_NON_ANIMATED_DOOR | RockTunnel_1F_Frlg | (17, 2) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (8, 57) | MB_NON_ANIMATED_DOOR | RockTunnel_1F_Frlg | (18, 37) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (7, 40) | MB_NON_ANIMATED_DOOR | PowerPlant_Frlg | (5, 38) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (13, 20) | MB_ANIMATED_DOOR | Route10_PokemonCenter_1F_Frlg | (7, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (2, 37) | MB_EAST_ARROW_WARP | PowerPlant_Frlg | (1, 11) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route10_Frlg[0] UNTESTED** — untestable: Route10_Frlg cannot be loaded by the engine (see load check)
* **Route10_Frlg[1] UNTESTED** — untestable: Route10_Frlg cannot be loaded by the engine (see load check)
* **Route10_Frlg[2] UNTESTED** — untestable: Route10_Frlg cannot be loaded by the engine (see load check)
* **Route10_Frlg[3] UNTESTED** — untestable: Route10_Frlg cannot be loaded by the engine (see load check)
* **Route10_Frlg[4] UNTESTED** — untestable: Route10_Frlg cannot be loaded by the engine (see load check)
* **Route10_Frlg conn[0] down/0 -> LavenderTown_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route10_Frlg conn[1] left/0 -> Route9_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route10_PokemonCenter_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 8) | MB_NORMAL | Route10_Frlg | (13, 20) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (7, 8) | MB_SOUTH_ARROW_WARP | Route10_Frlg | (13, 20) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 8) | MB_NORMAL | Route10_Frlg | (13, 20) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (1, 6) | MB_UP_ESCALATOR | Route10_PokemonCenter_2F_Frlg | (1, 6) | MB_DOWN_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |

* **Route10_PokemonCenter_1F_Frlg[0] UNTESTED** — untestable: Route10_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **Route10_PokemonCenter_1F_Frlg[1] UNTESTED** — untestable: Route10_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **Route10_PokemonCenter_1F_Frlg[2] UNTESTED** — untestable: Route10_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **Route10_PokemonCenter_1F_Frlg[3] UNTESTED** — untestable: Route10_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)

### `Route10_PokemonCenter_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | Route10_PokemonCenter_1F_Frlg | (1, 6) | MB_UP_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom_Frlg | (7, 11) | MB_BRIDGE_OVER_OCEAN | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter_Frlg | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route10_PokemonCenter_2F_Frlg[0] UNTESTED** — untestable: Route10_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **Route10_PokemonCenter_2F_Frlg[1] UNTESTED** — untestable: Route10_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **Route10_PokemonCenter_2F_Frlg[2] UNTESTED** — untestable: Route10_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)

### `Route110`

*Tier: region trail endpoint — 6 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (35, 24) | MB_NON_ANIMATED_DOOR | NewMauville_Entrance | (4, 6) | MB_SOUTH_ARROW_WARP | (4, 6) | (4, 6) | UP (UP) | yes | same door | **OK** |
| 1 | (11, 66) | MB_ANIMATED_DOOR | Route110_TrickHouseEntrance | (5, 7) | MB_SOUTH_ARROW_WARP | (5, 7) | (5, 7) | UP (UP) | yes | same door | **OK** |
| 2 | (15, 16) | MB_ANIMATED_DOOR | Route110_SeasideCyclingRoadNorthEntrance | (1, 5) | MB_SOUTH_ARROW_WARP | (1, 5) | (1, 5) | UP (UP) | yes | same door | **OK** |
| 3 | (18, 16) | MB_ANIMATED_DOOR | Route110_SeasideCyclingRoadNorthEntrance | (12, 5) | MB_SOUTH_ARROW_WARP | (12, 5) | (12, 5) | UP (UP) | yes | same door | **OK** |
| 4 | (16, 88) | MB_ANIMATED_DOOR | Route110_SeasideCyclingRoadSouthEntrance | (1, 5) | MB_SOUTH_ARROW_WARP | (1, 5) | (1, 5) | UP (UP) | yes | same door | **OK** |
| 5 | (19, 88) | MB_ANIMATED_DOOR | Route110_SeasideCyclingRoadSouthEntrance | (12, 5) | MB_SOUTH_ARROW_WARP | (12, 5) | (12, 5) | UP (UP) | yes | same door | **OK** |


### `Route110_SeasideCyclingRoadNorthEntrance`

*Tier: other / unclassified base — 4 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 5) | MB_SOUTH_ARROW_WARP | Route110 | (15, 16) | MB_ANIMATED_DOOR | (15, 16) | (15, 17) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (2, 5) | MB_SOUTH_ARROW_WARP | Route110 | (15, 16) | MB_ANIMATED_DOOR | (15, 16) | (15, 17) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (12, 5) | MB_SOUTH_ARROW_WARP | Route110 | (18, 16) | MB_ANIMATED_DOOR | (18, 16) | (18, 17) | DOWN (DOWN) | yes | same door | **OK** |
| 3 | (13, 5) | MB_SOUTH_ARROW_WARP | Route110 | (18, 16) | MB_ANIMATED_DOOR | (18, 16) | (18, 17) | DOWN (DOWN) | yes | same door | **OK** |


### `Route110_SeasideCyclingRoadSouthEntrance`

*Tier: other / unclassified base — 4 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 5) | MB_SOUTH_ARROW_WARP | Route110 | (16, 88) | MB_ANIMATED_DOOR | (16, 88) | (16, 89) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (2, 5) | MB_SOUTH_ARROW_WARP | Route110 | (16, 88) | MB_ANIMATED_DOOR | (16, 88) | (16, 89) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (12, 5) | MB_SOUTH_ARROW_WARP | Route110 | (19, 88) | MB_ANIMATED_DOOR | (19, 88) | (19, 89) | DOWN (DOWN) | yes | same door | **OK** |
| 3 | (13, 5) | MB_SOUTH_ARROW_WARP | Route110 | (19, 88) | MB_ANIMATED_DOOR | (19, 88) | (19, 89) | DOWN (DOWN) | yes | same door | **OK** |


### `Route110_TrickHouseCorridor`

*Tier: other / unclassified base — 4 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (13, 3) | MB_NORMAL | Route110_TrickHouseEnd | (2, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |
| 1 | (14, 3) | MB_NORMAL | Route110_TrickHouseEnd | (2, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |
| 2 | (4, 23) | MB_SOUTH_ARROW_WARP | Route110_TrickHouseEntrance | (5, 2) | MB_NORMAL | (5, 2) | (5, 2) | DOWN (DOWN) | yes | inconclusive | **OK** |
| 3 | (5, 23) | MB_SOUTH_ARROW_WARP | Route110_TrickHouseEntrance | (5, 2) | MB_NORMAL | (5, 2) | (5, 2) | DOWN (DOWN) | yes | inconclusive | **OK** |

* **Route110_TrickHouseCorridor[0] ISSUE** — stepping DOWN from (13,2) onto (13,3) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route110_TrickHouseCorridor_0_nowarp.png`
* **Route110_TrickHouseCorridor[1] ISSUE** — stepping DOWN from (14,2) onto (14,3) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route110_TrickHouseCorridor_1_nowarp.png`

### `Route110_TrickHouseEnd`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 1) | MB_NON_ANIMATED_DOOR | Route110_TrickHousePuzzle1 | (13, 1) | MB_TRICK_HOUSE_PUZZLE_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |
| 1 | (2, 1) | MB_NON_ANIMATED_DOOR | Route110_TrickHouseCorridor | (13, 3) | MB_NORMAL | (13, 3) | (13, 3) | DOWN (DOWN) | yes | inconclusive | **PARTIAL** |

* **Route110_TrickHouseEnd[0] ISSUE** — stepping UP from (10,2) onto (10,1) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route110_TrickHouseEnd_0_nowarp.png`
* **Route110_TrickHouseEnd[1] PARTIAL** — (note) arrival facing DOWN points into a blocked tile (13,4); (note) INCONCLUSIVE return: no side of the return warp Route110_TrickHouseCorridor[0] at (13,3) triggered a warp (tried ['DOWN', 'LEFT', 'RIGHT'])

### `Route110_TrickHouseEntrance`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 7) | MB_SOUTH_ARROW_WARP | Route110 | (11, 66) | MB_ANIMATED_DOOR | (11, 66) | (11, 67) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 7) | MB_SOUTH_ARROW_WARP | Route110 | (11, 66) | MB_ANIMATED_DOOR | (11, 66) | (11, 67) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (5, 2) | MB_NORMAL | Route110_TrickHousePuzzle1 | (0, 21) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |

* **Route110_TrickHouseEntrance[2] ISSUE** — stepping LEFT from (6,2) onto (5,2) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route110_TrickHouseEntrance_2_nowarp.png`

### `Route110_TrickHousePuzzle1`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (0, 21) | MB_SOUTH_ARROW_WARP | Route110_TrickHouseEntrance | (5, 2) | MB_NORMAL | (5, 2) | (5, 2) | DOWN (DOWN) | yes | inconclusive | **PARTIAL** |
| 1 | (1, 21) | MB_SOUTH_ARROW_WARP | Route110_TrickHouseEntrance | (5, 2) | MB_NORMAL | (5, 2) | (5, 2) | DOWN (DOWN) | yes | inconclusive | **PARTIAL** |
| 2 | (13, 1) | MB_TRICK_HOUSE_PUZZLE_DOOR | Route110_TrickHouseEnd | (10, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |

* **Route110_TrickHousePuzzle1[0] PARTIAL** — (note) arrival facing DOWN points into a blocked tile (5,3); (note) INCONCLUSIVE return: no side of the return warp Route110_TrickHouseEntrance[2] at (5,2) triggered a warp (tried ['LEFT', 'RIGHT', 'UP'])
* **Route110_TrickHousePuzzle1[1] PARTIAL** — (note) arrival facing DOWN points into a blocked tile (5,3); (note) INCONCLUSIVE return: no side of the return warp Route110_TrickHouseEntrance[2] at (5,2) triggered a warp (tried ['LEFT', 'RIGHT', 'UP'])
* **Route110_TrickHousePuzzle1[2] ISSUE** — stepping UP from (13,2) onto (13,1) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route110_TrickHousePuzzle1_2_nowarp.png`

### `Route115`

*Tier: region trail endpoint — 3 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (27, 37) | MB_NON_ANIMATED_DOOR | MeteorFalls_1F_1R | (6, 39) | MB_SOUTH_ARROW_WARP | (6, 39) | (6, 39) | UP (UP) | yes | same door | **OK** |
| 1 | (21, 6) | MB_MOUNTAIN_TOP | Route115 | (21, 6) | MB_MOUNTAIN_TOP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 2 | (36, 10) | MB_MOUNTAIN_TOP | Route115 | (36, 10) | MB_MOUNTAIN_TOP | - | - | - (-) | - | inconclusive | **ISSUE** |

* **Route115[1] ISSUE** — stepping UP from (21,7) onto (21,6) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route115_1_nowarp.png`
* **Route115[2] ISSUE** — stepping UP from (36,11) onto (36,10) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route115_2_nowarp.png`

### `Route119`

*Tier: region trail endpoint — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 32) | MB_NON_ANIMATED_DOOR | Route119_WeatherInstitute_1F | (9, 12) | MB_SOUTH_ARROW_WARP | (9, 12) | (9, 12) | UP (UP) | yes | same door | **OK** |
| 1 | (33, 109) | MB_ANIMATED_DOOR | Route119_House | (3, 8) | MB_SOUTH_ARROW_WARP | (3, 8) | (3, 8) | UP (UP) | yes | same door | **OK** |


### `Route119_House`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 8) | MB_SOUTH_ARROW_WARP | Route119 | (33, 109) | MB_ANIMATED_DOOR | (33, 109) | (33, 110) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 8) | MB_SOUTH_ARROW_WARP | Route119 | (33, 109) | MB_ANIMATED_DOOR | (33, 109) | (33, 110) | DOWN (DOWN) | yes | same door | **OK** |


### `Route119_WeatherInstitute_1F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (9, 12) | MB_SOUTH_ARROW_WARP | Route119 | (6, 32) | MB_NON_ANIMATED_DOOR | (6, 32) | (6, 33) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (10, 12) | MB_SOUTH_ARROW_WARP | Route119 | (6, 32) | MB_NON_ANIMATED_DOOR | (6, 32) | (6, 33) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (17, 1) | MB_NON_ANIMATED_DOOR | Route119_WeatherInstitute_2F | (17, 1) | MB_NON_ANIMATED_DOOR | (17, 1) | (17, 2) | UP (DOWN) | yes | same door | **OK** |


### `Route119_WeatherInstitute_2F`

*Tier: story-trigger map — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (17, 1) | MB_NON_ANIMATED_DOOR | Route119_WeatherInstitute_1F | (17, 1) | MB_NON_ANIMATED_DOOR | (17, 1) | (17, 2) | UP (DOWN) | yes | same door | **OK** |


### `Route11_EastEntrance_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 5 warp(s), 0 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_WEST_ARROW_WARP | Route11_Frlg | (58, 10) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (1, 7) | MB_NORMAL | Route11_Frlg | (58, 10) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (11, 6) | MB_EAST_ARROW_WARP | Route11_Frlg | (65, 10) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (11, 7) | MB_NORMAL | Route11_Frlg | (65, 10) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (9, 10) | MB_UP_RIGHT_STAIR_WARP | Route11_EastEntrance_2F_Frlg | (10, 9) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route11_EastEntrance_1F_Frlg[0] UNTESTED** — untestable: Route11_EastEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route11_EastEntrance_1F_Frlg[1] UNTESTED** — untestable: Route11_EastEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route11_EastEntrance_1F_Frlg[2] UNTESTED** — untestable: Route11_EastEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route11_EastEntrance_1F_Frlg[3] UNTESTED** — untestable: Route11_EastEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route11_EastEntrance_1F_Frlg[4] UNTESTED** — untestable: Route11_EastEntrance_1F_Frlg cannot be loaded by the engine (see load check)

### `Route11_EastEntrance_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 9) | MB_DOWN_LEFT_STAIR_WARP | Route11_EastEntrance_1F_Frlg | (9, 10) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route11_EastEntrance_2F_Frlg[0] UNTESTED** — untestable: Route11_EastEntrance_2F_Frlg cannot be loaded by the engine (see load check)

### `Route11_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 2 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 7) | MB_NON_ANIMATED_DOOR | DiglettsCave_SouthEntrance_Frlg | (4, 6) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (58, 10) | MB_EAST_ARROW_WARP | Route11_EastEntrance_1F_Frlg | (1, 6) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (65, 10) | MB_WEST_ARROW_WARP | Route11_EastEntrance_1F_Frlg | (11, 6) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route11_Frlg[0] UNTESTED** — untestable: Route11_Frlg cannot be loaded by the engine (see load check)
* **Route11_Frlg[1] UNTESTED** — untestable: Route11_Frlg cannot be loaded by the engine (see load check)
* **Route11_Frlg[2] UNTESTED** — untestable: Route11_Frlg cannot be loaded by the engine (see load check)
* **Route11_Frlg conn[0] left/-10 -> VermilionCity_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route11_Frlg conn[1] right/-60 -> Route12_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route12_FishingHouse_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 8) | MB_NORMAL | Route12_Frlg | (12, 86) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (3, 7) | MB_SOUTH_ARROW_WARP | Route12_Frlg | (12, 86) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (4, 8) | MB_NORMAL | Route12_Frlg | (12, 86) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **Route12_FishingHouse_Frlg[0] UNTESTED** — untestable: Route12_FishingHouse_Frlg cannot be loaded by the engine (see load check)
* **Route12_FishingHouse_Frlg[1] UNTESTED** — untestable: Route12_FishingHouse_Frlg cannot be loaded by the engine (see load check)
* **Route12_FishingHouse_Frlg[2] UNTESTED** — untestable: Route12_FishingHouse_Frlg cannot be loaded by the engine (see load check)

### `Route12_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 3 connection(s), 7 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (12, 86) | MB_ANIMATED_DOOR | Route12_FishingHouse_Frlg | (3, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (14, 15) | MB_SOUTH_ARROW_WARP | Route12_NorthEntrance_1F_Frlg | (5, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (15, 15) | MB_NORMAL | Route12_NorthEntrance_1F_Frlg | (6, 1) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (14, 21) | MB_NON_ANIMATED_DOOR | Route12_NorthEntrance_1F_Frlg | (5, 11) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route12_Frlg[0] UNTESTED** — untestable: Route12_Frlg cannot be loaded by the engine (see load check)
* **Route12_Frlg[1] UNTESTED** — untestable: Route12_Frlg cannot be loaded by the engine (see load check)
* **Route12_Frlg[2] UNTESTED** — untestable: Route12_Frlg cannot be loaded by the engine (see load check)
* **Route12_Frlg[3] UNTESTED** — untestable: Route12_Frlg cannot be loaded by the engine (see load check)
* **Route12_Frlg conn[0] up/0 -> LavenderTown_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route12_Frlg conn[1] down/-48 -> Route13_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route12_Frlg conn[2] left/60 -> Route11_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route12_NorthEntrance_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 5 warp(s), 0 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 1) | MB_NON_ANIMATED_DOOR | Route12_Frlg | (14, 15) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 1) | MB_NORMAL | Route12_Frlg | (15, 15) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 11) | MB_SOUTH_ARROW_WARP | Route12_Frlg | (14, 21) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (6, 11) | MB_NORMAL | Route12_Frlg | (14, 21) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (8, 10) | MB_UP_RIGHT_STAIR_WARP | Route12_NorthEntrance_2F_Frlg | (10, 9) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route12_NorthEntrance_1F_Frlg[0] UNTESTED** — untestable: Route12_NorthEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route12_NorthEntrance_1F_Frlg[1] UNTESTED** — untestable: Route12_NorthEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route12_NorthEntrance_1F_Frlg[2] UNTESTED** — untestable: Route12_NorthEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route12_NorthEntrance_1F_Frlg[3] UNTESTED** — untestable: Route12_NorthEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route12_NorthEntrance_1F_Frlg[4] UNTESTED** — untestable: Route12_NorthEntrance_1F_Frlg cannot be loaded by the engine (see load check)

### `Route12_NorthEntrance_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 9) | MB_DOWN_LEFT_STAIR_WARP | Route12_NorthEntrance_1F_Frlg | (8, 10) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route12_NorthEntrance_2F_Frlg[0] UNTESTED** — untestable: Route12_NorthEntrance_2F_Frlg cannot be loaded by the engine (see load check)

### `Route13_Frlg`

*Tier: donor town/cave (vanilla base) — 0 warp(s), 2 connection(s), 2 finding(s).*

* **Route13_Frlg conn[0] up/48 -> Route12_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route13_Frlg conn[1] left/0 -> Route14_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route14_Frlg`

*Tier: donor town/cave (vanilla base) — 0 warp(s), 2 connection(s), 2 finding(s).*

* **Route14_Frlg conn[0] left/40 -> Route15_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route14_Frlg conn[1] right/0 -> Route13_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route15_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 2 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (9, 11) | MB_EAST_ARROW_WARP | Route15_WestEntrance_1F_Frlg | (1, 6) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (16, 11) | MB_WEST_ARROW_WARP | Route15_WestEntrance_1F_Frlg | (11, 6) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route15_Frlg[0] UNTESTED** — untestable: Route15_Frlg cannot be loaded by the engine (see load check)
* **Route15_Frlg[1] UNTESTED** — untestable: Route15_Frlg cannot be loaded by the engine (see load check)
* **Route15_Frlg conn[0] left/-10 -> FuchsiaCity_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route15_Frlg conn[1] right/-40 -> Route14_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route15_WestEntrance_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 5 warp(s), 0 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_WEST_ARROW_WARP | Route15_Frlg | (9, 11) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (1, 7) | MB_NORMAL | Route15_Frlg | (9, 11) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (11, 6) | MB_EAST_ARROW_WARP | Route15_Frlg | (16, 11) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (11, 7) | MB_NORMAL | Route15_Frlg | (16, 11) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (9, 10) | MB_UP_RIGHT_STAIR_WARP | Route15_WestEntrance_2F_Frlg | (10, 9) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route15_WestEntrance_1F_Frlg[0] UNTESTED** — untestable: Route15_WestEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route15_WestEntrance_1F_Frlg[1] UNTESTED** — untestable: Route15_WestEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route15_WestEntrance_1F_Frlg[2] UNTESTED** — untestable: Route15_WestEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route15_WestEntrance_1F_Frlg[3] UNTESTED** — untestable: Route15_WestEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route15_WestEntrance_1F_Frlg[4] UNTESTED** — untestable: Route15_WestEntrance_1F_Frlg cannot be loaded by the engine (see load check)

### `Route15_WestEntrance_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 9) | MB_DOWN_LEFT_STAIR_WARP | Route15_WestEntrance_1F_Frlg | (9, 10) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route15_WestEntrance_2F_Frlg[0] UNTESTED** — untestable: Route15_WestEntrance_2F_Frlg cannot be loaded by the engine (see load check)

### `Route16_Frlg`

*Tier: donor town/cave (vanilla base) — 5 warp(s), 2 connection(s), 7 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 5) | MB_ANIMATED_DOOR | Route16_House_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (20, 6) | MB_EAST_ARROW_WARP | Route16_NorthEntrance_1F_Frlg | (1, 3) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (27, 6) | MB_WEST_ARROW_WARP | Route16_NorthEntrance_1F_Frlg | (11, 3) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (20, 13) | MB_EAST_ARROW_WARP | Route16_NorthEntrance_1F_Frlg | (1, 12) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (27, 13) | MB_WEST_ARROW_WARP | Route16_NorthEntrance_1F_Frlg | (11, 12) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route16_Frlg[0] UNTESTED** — untestable: Route16_Frlg cannot be loaded by the engine (see load check)
* **Route16_Frlg[1] UNTESTED** — untestable: Route16_Frlg cannot be loaded by the engine (see load check)
* **Route16_Frlg[2] UNTESTED** — untestable: Route16_Frlg cannot be loaded by the engine (see load check)
* **Route16_Frlg[3] UNTESTED** — untestable: Route16_Frlg cannot be loaded by the engine (see load check)
* **Route16_Frlg[4] UNTESTED** — untestable: Route16_Frlg cannot be loaded by the engine (see load check)
* **Route16_Frlg conn[0] down/0 -> Route17_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route16_Frlg conn[1] right/-10 -> CeladonCity_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route16_House_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | Route16_Frlg | (10, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | Route16_Frlg | (10, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | Route16_Frlg | (10, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **Route16_House_Frlg[0] UNTESTED** — untestable: Route16_House_Frlg cannot be loaded by the engine (see load check)
* **Route16_House_Frlg[1] UNTESTED** — untestable: Route16_House_Frlg cannot be loaded by the engine (see load check)
* **Route16_House_Frlg[2] UNTESTED** — untestable: Route16_House_Frlg cannot be loaded by the engine (see load check)

### `Route16_NorthEntrance_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 5 warp(s), 0 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 3) | MB_WEST_ARROW_WARP | Route16_Frlg | (20, 6) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (11, 3) | MB_EAST_ARROW_WARP | Route16_Frlg | (27, 6) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (1, 12) | MB_WEST_ARROW_WARP | Route16_Frlg | (20, 13) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (11, 12) | MB_EAST_ARROW_WARP | Route16_Frlg | (27, 13) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (9, 16) | MB_UP_RIGHT_STAIR_WARP | Route16_NorthEntrance_2F_Frlg | (10, 9) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route16_NorthEntrance_1F_Frlg[0] UNTESTED** — untestable: Route16_NorthEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route16_NorthEntrance_1F_Frlg[1] UNTESTED** — untestable: Route16_NorthEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route16_NorthEntrance_1F_Frlg[2] UNTESTED** — untestable: Route16_NorthEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route16_NorthEntrance_1F_Frlg[3] UNTESTED** — untestable: Route16_NorthEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route16_NorthEntrance_1F_Frlg[4] UNTESTED** — untestable: Route16_NorthEntrance_1F_Frlg cannot be loaded by the engine (see load check)

### `Route16_NorthEntrance_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 9) | MB_DOWN_LEFT_STAIR_WARP | Route16_NorthEntrance_1F_Frlg | (9, 16) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route16_NorthEntrance_2F_Frlg[0] UNTESTED** — untestable: Route16_NorthEntrance_2F_Frlg cannot be loaded by the engine (see load check)

### `Route17_Frlg`

*Tier: donor town/cave (vanilla base) — 0 warp(s), 2 connection(s), 2 finding(s).*

* **Route17_Frlg conn[0] up/0 -> Route16_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route17_Frlg conn[1] down/0 -> Route18_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route18_EastEntrance_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_WEST_ARROW_WARP | Route18_Frlg | (41, 9) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (11, 6) | MB_EAST_ARROW_WARP | Route18_Frlg | (48, 9) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 10) | MB_UP_RIGHT_STAIR_WARP | Route18_EastEntrance_2F_Frlg | (10, 9) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route18_EastEntrance_1F_Frlg[0] UNTESTED** — untestable: Route18_EastEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route18_EastEntrance_1F_Frlg[1] UNTESTED** — untestable: Route18_EastEntrance_1F_Frlg cannot be loaded by the engine (see load check)
* **Route18_EastEntrance_1F_Frlg[2] UNTESTED** — untestable: Route18_EastEntrance_1F_Frlg cannot be loaded by the engine (see load check)

### `Route18_EastEntrance_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 9) | MB_DOWN_LEFT_STAIR_WARP | Route18_EastEntrance_1F_Frlg | (9, 10) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route18_EastEntrance_2F_Frlg[0] UNTESTED** — untestable: Route18_EastEntrance_2F_Frlg cannot be loaded by the engine (see load check)

### `Route18_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 2 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (41, 9) | MB_EAST_ARROW_WARP | Route18_EastEntrance_1F_Frlg | (1, 6) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (48, 9) | MB_WEST_ARROW_WARP | Route18_EastEntrance_1F_Frlg | (11, 6) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route18_Frlg[0] UNTESTED** — untestable: Route18_Frlg cannot be loaded by the engine (see load check)
* **Route18_Frlg[1] UNTESTED** — untestable: Route18_Frlg cannot be loaded by the engine (see load check)
* **Route18_Frlg conn[0] up/0 -> Route17_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route18_Frlg conn[1] right/-10 -> FuchsiaCity_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route21_North_Frlg`

*Tier: donor town/cave (vanilla base) — 0 warp(s), 1 connection(s), 1 finding(s).*

* **Route21_North_Frlg conn[0] down/0 -> Route21_South_Frlg ISSUE** — outward:ISSUE (walking DOWN off the Route21_North_Frlg edge did not change map on any of 0 lanes tried: )
  * down seam: walking DOWN off the Route21_North_Frlg edge did not change map on any of 0 lanes tried: 

### `Route21_South_Frlg`

*Tier: donor town/cave (vanilla base) — 0 warp(s), 2 connection(s), 1 finding(s).*

* **Route21_South_Frlg conn[0] up/0 -> Route21_North_Frlg ISSUE** — outward:ISSUE (walking UP off the Route21_South_Frlg edge did not change map on any of 0 lanes tried: )
  * up seam: walking UP off the Route21_South_Frlg edge did not change map on any of 0 lanes tried: 
* **Route21_South_Frlg conn[1] down/0 -> CinnabarIsland_Frlg OK** — outward:OK (handed over to CinnabarIsland_Frlg at (12,0)); inward:OK (returned to Route21_South_Frlg at (12,49))

### `Route24_Frlg`

*Tier: donor town/cave (vanilla base) — 0 warp(s), 2 connection(s), 2 finding(s).*

* **Route24_Frlg conn[0] down/-12 -> CeruleanCity_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route24_Frlg conn[1] right/0 -> Route25_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route24_hns`

*Tier: donor town/cave (vanilla base) — 0 warp(s), 2 connection(s), 0 finding(s).*

* **Route24_hns conn[0] up/0 -> Route25_hns OK** — outward:OK (handed over to Route25_hns at (16,34)); inward:OK (returned to Route24_hns at (16,0))
* **Route24_hns conn[1] down/-3 -> RustboroCity OK** — outward:OK (handed over to RustboroCity at (19,0)); inward:OK (returned to Route24_hns at (16,21))

### `Route25_BillsHouse_hns`

*Tier: story-trigger map — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 9) | MB_SOUTH_ARROW_WARP | Route25_hns | (85, 13) | MB_ANIMATED_DOOR | (85, 13) | (85, 14) | DOWN (DOWN) | yes | same door | **OK** |


### `Route25_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 1 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (51, 4) | MB_ANIMATED_DOOR | Route25_SeaCottage_Frlg | (7, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route25_Frlg[0] UNTESTED** — untestable: Route25_Frlg cannot be loaded by the engine (see load check)
* **Route25_Frlg conn[0] left/0 -> Route24_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route25_SeaCottage_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 9) | MB_NORMAL | Route25_Frlg | (51, 4) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (7, 9) | MB_SOUTH_ARROW_WARP | Route25_Frlg | (51, 4) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 9) | MB_NORMAL | Route25_Frlg | (51, 4) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **Route25_SeaCottage_Frlg[0] UNTESTED** — untestable: Route25_SeaCottage_Frlg cannot be loaded by the engine (see load check)
* **Route25_SeaCottage_Frlg[1] UNTESTED** — untestable: Route25_SeaCottage_Frlg cannot be loaded by the engine (see load check)
* **Route25_SeaCottage_Frlg[2] UNTESTED** — untestable: Route25_SeaCottage_Frlg cannot be loaded by the engine (see load check)

### `Route25_hns`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 1 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (85, 13) | MB_ANIMATED_DOOR | Route25_BillsHouse_hns | (7, 9) | MB_SOUTH_ARROW_WARP | (7, 9) | (7, 9) | UP (UP) | yes | same door | **OK** |

* **Route25_hns conn[0] down/0 -> Route24_hns OK** — outward:OK (handed over to Route24_hns at (16,0)); inward:OK (returned to Route25_hns at (16,34))

### `Route29_hns`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 2 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (34, 10) | MB_NON_ANIMATED_DOOR | Gate_Route29_Route46_hns | (7, 9) | MB_SOUTH_ARROW_WARP | (7, 9) | (7, 9) | UP (UP) | yes | same door | **OK** |
| 1 | (35, 10) | MB_NON_ANIMATED_DOOR | Gate_Route29_Route46_hns | (7, 9) | MB_SOUTH_ARROW_WARP | (7, 9) | (7, 9) | UP (UP) | yes | same door | **OK** |

* **Route29_hns conn[0] left/6 -> CherrygroveCity_hns OK** — outward:OK (handed over to CherrygroveCity_hns at (64,11)); inward:OK (returned to Route29_hns at (0,17))
* **Route29_hns conn[1] right/6 -> OldaleTown OK** — outward:OK (handed over to OldaleTown at (0,10)); inward:OK (returned to Route29_hns at (69,16))

### `Route2_EastBuilding_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 9) | MB_NORMAL | Route2_Frlg | (18, 46) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |
| 1 | (7, 9) | MB_SOUTH_ARROW_WARP | Route2_Frlg | (18, 46) | MB_NON_ANIMATED_DOOR | (18, 46) | (18, 47) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (8, 9) | MB_NORMAL | Route2_Frlg | (18, 46) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |
| 3 | (7, 1) | MB_NON_ANIMATED_DOOR | Route2_Frlg | (18, 40) | MB_SOUTH_ARROW_WARP | (18, 40) | (18, 40) | UP (UP) | yes | same door | **OK** |

* **Route2_EastBuilding_Frlg[0] ISSUE** — stepping DOWN from (6,8) onto (6,9) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route2_EastBuilding_Frlg_0_nowarp.png`
* **Route2_EastBuilding_Frlg[2] ISSUE** — stepping DOWN from (8,8) onto (8,9) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route2_EastBuilding_Frlg_2_nowarp.png`

### `Route2_Frlg`

*Tier: donor town/cave (vanilla base) — 10 warp(s), 2 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 13) | MB_SOUTH_ARROW_WARP | Route2_ViridianForest_NorthEntrance_Frlg | (7, 1) | MB_NON_ANIMATED_DOOR | (7, 1) | (7, 2) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 13) | MB_SOUTH_ARROW_WARP | Route2_ViridianForest_NorthEntrance_Frlg | (7, 1) | MB_NON_ANIMATED_DOOR | (7, 1) | (7, 2) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (5, 51) | MB_NON_ANIMATED_DOOR | Route2_ViridianForest_SouthEntrance_Frlg | (7, 9) | MB_SOUTH_ARROW_WARP | (7, 9) | (7, 9) | UP (UP) | yes | same door | **OK** |
| 3 | (17, 11) | MB_ANIMATED_DOOR | DarkCave_SouthSide_hns | (14, 20) | MB_LADDER | (14, 20) | (14, 20) | UP (KEEP) | yes | same door | **OK** |
| 4 | (17, 22) | MB_ANIMATED_DOOR | Route2_House_Frlg | (4, 7) | MB_HOLDS_LARGE_DECORATION | (4, 7) | (4, 7) | UP (DOWN) | yes | inconclusive | **OK** |
| 5 | (18, 46) | MB_NON_ANIMATED_DOOR | Route2_EastBuilding_Frlg | (7, 9) | MB_SOUTH_ARROW_WARP | (7, 9) | (7, 9) | UP (UP) | yes | same door | **OK** |
| 6 | (18, 40) | MB_SOUTH_ARROW_WARP | Route2_EastBuilding_Frlg | (7, 1) | MB_NON_ANIMATED_DOOR | (7, 1) | (7, 2) | DOWN (DOWN) | yes | same door | **OK** |
| 7 | (19, 40) | MB_SOUTH_ARROW_WARP | Route2_EastBuilding_Frlg | (7, 1) | MB_NON_ANIMATED_DOOR | (7, 1) | (7, 2) | DOWN (DOWN) | yes | same door | **OK** |
| 8 | (19, 46) | MB_NON_ANIMATED_DOOR | Route2_EastBuilding_Frlg | (7, 9) | MB_SOUTH_ARROW_WARP | (7, 9) | (7, 9) | UP (UP) | yes | same door | **OK** |
| 9 | (6, 51) | MB_NON_ANIMATED_DOOR | Route2_ViridianForest_SouthEntrance_Frlg | (7, 9) | MB_SOUTH_ARROW_WARP | (7, 9) | (7, 9) | UP (UP) | yes | same door | **OK** |

* **Route2_Frlg conn[0] up/-6 -> RustboroCity OK** — outward:OK (handed over to RustboroCity at (17,59)); inward:OK (returned to Route2_Frlg at (11,0))
* **Route2_Frlg conn[1] down/-25 -> CherrygroveCity_hns OK** — outward:OK (handed over to CherrygroveCity_hns at (35,0)); inward:OK (returned to Route2_Frlg at (10,79))

### `Route2_House_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_HOLDS_LARGE_DECORATION | Route2_House_Frlg | (4, 7) | MB_HOLDS_LARGE_DECORATION | (17, 22) | (17, 23) | DOWN (DOWN) | yes | WRONG MAP/TILE | **ISSUE** |
| 1 | (4, 8) | MB_ANIMATED_DOOR | Route2_Frlg | (17, 22) | MB_ANIMATED_DOOR | (17, 22) | (17, 23) | DOWN (DOWN) | yes | same door | **OK** |

* **Route2_House_Frlg[0] ISSUE** — arrived in Route2_Frlg (37,19), expected Route2_House_Frlg (49, 1); landed at (17,22), expected (4,7); (note) arrival facing sampled after the transition finished, not on the landing tile; (note) return landed in Route2_Frlg at (17,22), expected Route2_House_Frlg at (4,7)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route2_House_Frlg_0_issue.png`

### `Route2_ViridianForest_NorthEntrance_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 9) | MB_NORMAL | IlexForest_hns | (20, 15) | MB_NORTH_ARROW_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 1 | (7, 9) | MB_SOUTH_ARROW_WARP | IlexForest_hns | (20, 15) | MB_NORTH_ARROW_WARP | (20, 15) | (20, 15) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (8, 9) | MB_NORMAL | IlexForest_hns | (20, 15) | MB_NORTH_ARROW_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 3 | (7, 1) | MB_NON_ANIMATED_DOOR | Route2_Frlg | (5, 13) | MB_SOUTH_ARROW_WARP | (5, 13) | (5, 13) | UP (UP) | yes | same door | **OK** |

* **Route2_ViridianForest_NorthEntrance_Frlg[0] ISSUE** — stepping DOWN from (6,8) onto (6,9) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route2_ViridianForest_NorthEntrance_Frlg_0_nowarp.png`
* **Route2_ViridianForest_NorthEntrance_Frlg[2] ISSUE** — stepping DOWN from (8,8) onto (8,9) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route2_ViridianForest_NorthEntrance_Frlg_2_nowarp.png`

### `Route2_ViridianForest_SouthEntrance_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 9) | MB_NORMAL | Route2_Frlg | (5, 51) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |
| 1 | (7, 9) | MB_SOUTH_ARROW_WARP | Route2_Frlg | (5, 51) | MB_NON_ANIMATED_DOOR | (5, 51) | (5, 52) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (8, 9) | MB_NORMAL | Route2_Frlg | (5, 51) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | inconclusive | **ISSUE** |
| 3 | (7, 1) | MB_NON_ANIMATED_DOOR | IlexForest_hns | (22, 63) | MB_EAST_ARROW_WARP | (22, 63) | (22, 63) | LEFT (LEFT) | yes | same door | **OK** |

* **Route2_ViridianForest_SouthEntrance_Frlg[0] ISSUE** — stepping DOWN from (6,8) onto (6,9) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route2_ViridianForest_SouthEntrance_Frlg_0_nowarp.png`
* **Route2_ViridianForest_SouthEntrance_Frlg[2] ISSUE** — stepping DOWN from (8,8) onto (8,9) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route2_ViridianForest_SouthEntrance_Frlg_2_nowarp.png`

### `Route33_hns`

*Tier: story-trigger map — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (27, 17) | MB_NON_ANIMATED_DOOR | MtMoon_B1F_Frlg | (45, 4) | MB_LADDER | (45, 4) | (45, 4) | UP (KEEP) | yes | same door | **OK** |


### `Route36_hns`

*Tier: story-trigger map — 0 warp(s), 1 connection(s), 0 finding(s).*

* **Route36_hns conn[0] up/22 -> Route37_hns OK** — outward:OK (handed over to Route37_hns at (15,40)); inward:OK (returned to Route36_hns at (43,0))

### `Route37_hns`

*Tier: region trail endpoint — 0 warp(s), 2 connection(s), 2 finding(s).*

* **Route37_hns conn[0] down/-22 -> Route36_hns ISSUE** — outward:OK (handed over to Route36_hns at (43,0)); outward_continue:ISSUE (blocked at [43, 0]); inward:OK (returned to Route37_hns at (15,40))
  * Route37_hns down seam: player cannot continue DOWN past the handover tile (43,0) in Route36_hns
* **Route37_hns conn[1] up/16 -> EcruteakCity_hns ISSUE** — outward:ISSUE (walking UP off the Route37_hns edge did not change map on any of 0 lanes tried: )
  * up seam: walking UP off the Route37_hns edge did not change map on any of 0 lanes tried: 

### `Route3_Frlg`

*Tier: donor town/cave (vanilla base) — 0 warp(s), 2 connection(s), 2 finding(s).*

* **Route3_Frlg conn[0] up/60 -> Route4_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route3_Frlg conn[1] left/-10 -> PewterCity_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route44_hns`

*Tier: region trail endpoint — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (68, 13) | MB_NORMAL | MtMoon_1F_Frlg | (18, 37) | MB_SOUTH_ARROW_WARP | (18, 36) | (18, 36) | DOWN (DOWN) | yes | same door | **ISSUE** |

* **Route44_hns[0] ISSUE** — landed at (18,36), expected (18,37)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route44_hns_0_issue.png`

### `Route46_hns`

*Tier: region trail endpoint — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 40) | MB_SOUTH_ARROW_WARP | Gate_Route29_Route46_hns | (7, 1) | MB_NON_ANIMATED_DOOR | (7, 1) | (7, 2) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (11, 40) | MB_ANIMATED_DOOR | Gate_Route29_Route46_hns | (7, 1) | MB_NON_ANIMATED_DOOR | (7, 1) | (7, 2) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (20, 11) | MB_ANIMATED_DOOR | DarkCave_SouthSide_hns | (56, 46) | MB_LADDER | (56, 46) | (56, 46) | UP (KEEP) | yes | same door | **OK** |


### `Route4_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 2 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (19, 5) | MB_NON_ANIMATED_DOOR | MtMoon_1F_Frlg | (18, 37) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (32, 5) | MB_NON_ANIMATED_DOOR | MtMoon_B1F_Frlg | (45, 4) | MB_LADDER | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (12, 5) | MB_ANIMATED_DOOR | Route4_PokemonCenter_1F_Frlg | (7, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route4_Frlg[0] UNTESTED** — untestable: Route4_Frlg cannot be loaded by the engine (see load check)
* **Route4_Frlg[1] UNTESTED** — untestable: Route4_Frlg cannot be loaded by the engine (see load check)
* **Route4_Frlg[2] UNTESTED** — untestable: Route4_Frlg cannot be loaded by the engine (see load check)
* **Route4_Frlg conn[0] down/-60 -> Route3_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route4_Frlg conn[1] right/-10 -> CeruleanCity_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route4_PokemonCenter_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 8) | MB_NORMAL | Route4_Frlg | (12, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (7, 8) | MB_SOUTH_ARROW_WARP | Route4_Frlg | (12, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 8) | MB_NORMAL | Route4_Frlg | (12, 5) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (1, 6) | MB_UP_ESCALATOR | Route4_PokemonCenter_2F_Frlg | (1, 6) | MB_DOWN_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |

* **Route4_PokemonCenter_1F_Frlg[0] UNTESTED** — untestable: Route4_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **Route4_PokemonCenter_1F_Frlg[1] UNTESTED** — untestable: Route4_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **Route4_PokemonCenter_1F_Frlg[2] UNTESTED** — untestable: Route4_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **Route4_PokemonCenter_1F_Frlg[3] UNTESTED** — untestable: Route4_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)

### `Route4_PokemonCenter_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | Route4_PokemonCenter_1F_Frlg | (1, 6) | MB_UP_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom_Frlg | (7, 11) | MB_BRIDGE_OVER_OCEAN | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter_Frlg | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route4_PokemonCenter_2F_Frlg[0] UNTESTED** — untestable: Route4_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **Route4_PokemonCenter_2F_Frlg[1] UNTESTED** — untestable: Route4_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **Route4_PokemonCenter_2F_Frlg[2] UNTESTED** — untestable: Route4_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)

### `Route5_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 2 connection(s), 6 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (31, 31) | MB_ANIMATED_DOOR | UndergroundPath_NorthEntrance_Frlg | (6, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (23, 25) | MB_ANIMATED_DOOR | Route5_PokemonDayCare_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (24, 32) | MB_SOUTH_ARROW_WARP | Route5_SouthEntrance_Frlg | (4, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (25, 32) | MB_SOUTH_ARROW_WARP | Route5_SouthEntrance_Frlg | (4, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **Route5_Frlg[0] UNTESTED** — untestable: Route5_Frlg cannot be loaded by the engine (see load check)
* **Route5_Frlg[1] UNTESTED** — untestable: Route5_Frlg cannot be loaded by the engine (see load check)
* **Route5_Frlg[2] UNTESTED** — untestable: Route5_Frlg cannot be loaded by the engine (see load check)
* **Route5_Frlg[3] UNTESTED** — untestable: Route5_Frlg cannot be loaded by the engine (see load check)
* **Route5_Frlg conn[0] up/0 -> CeruleanCity_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route5_Frlg conn[1] down/0 -> SaffronCity_Connection_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route5_PokemonDayCare_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | Route5_Frlg | (23, 25) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | Route5_Frlg | (23, 25) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | Route5_Frlg | (23, 25) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **Route5_PokemonDayCare_Frlg[0] UNTESTED** — untestable: Route5_PokemonDayCare_Frlg cannot be loaded by the engine (see load check)
* **Route5_PokemonDayCare_Frlg[1] UNTESTED** — untestable: Route5_PokemonDayCare_Frlg cannot be loaded by the engine (see load check)
* **Route5_PokemonDayCare_Frlg[2] UNTESTED** — untestable: Route5_PokemonDayCare_Frlg cannot be loaded by the engine (see load check)

### `Route5_SouthEntrance_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 9) | MB_NORMAL | SaffronCity_Frlg | (34, 5) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 1) | MB_NON_ANIMATED_DOOR | Route5_Frlg | (24, 32) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (4, 9) | MB_SOUTH_ARROW_WARP | SaffronCity_Frlg | (34, 5) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (5, 1) | MB_NORMAL | Route5_Frlg | (25, 32) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route5_SouthEntrance_Frlg[0] UNTESTED** — untestable: Route5_SouthEntrance_Frlg cannot be loaded by the engine (see load check)
* **Route5_SouthEntrance_Frlg[1] UNTESTED** — untestable: Route5_SouthEntrance_Frlg cannot be loaded by the engine (see load check)
* **Route5_SouthEntrance_Frlg[2] UNTESTED** — untestable: Route5_SouthEntrance_Frlg cannot be loaded by the engine (see load check)
* **Route5_SouthEntrance_Frlg[3] UNTESTED** — untestable: Route5_SouthEntrance_Frlg cannot be loaded by the engine (see load check)

### `Route6_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 2 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (19, 13) | MB_ANIMATED_DOOR | UndergroundPath_SouthEntrance_Frlg | (6, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (12, 5) | MB_NON_ANIMATED_DOOR | Route6_NorthEntrance_Frlg | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (13, 5) | MB_NON_ANIMATED_DOOR | Route6_NorthEntrance_Frlg | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route6_Frlg[0] UNTESTED** — untestable: Route6_Frlg cannot be loaded by the engine (see load check)
* **Route6_Frlg[1] UNTESTED** — untestable: Route6_Frlg cannot be loaded by the engine (see load check)
* **Route6_Frlg[2] UNTESTED** — untestable: Route6_Frlg cannot be loaded by the engine (see load check)
* **Route6_Frlg conn[0] up/0 -> SaffronCity_Connection_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route6_Frlg conn[1] down/-12 -> VermilionCity_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route6_NorthEntrance_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 1) | MB_NON_ANIMATED_DOOR | SaffronCity_Frlg | (34, 46) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 1) | MB_NORMAL | SaffronCity_Frlg | (34, 46) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (4, 9) | MB_SOUTH_ARROW_WARP | Route6_Frlg | (12, 5) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (5, 9) | MB_NORMAL | Route6_Frlg | (12, 5) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **Route6_NorthEntrance_Frlg[0] UNTESTED** — untestable: Route6_NorthEntrance_Frlg cannot be loaded by the engine (see load check)
* **Route6_NorthEntrance_Frlg[1] UNTESTED** — untestable: Route6_NorthEntrance_Frlg cannot be loaded by the engine (see load check)
* **Route6_NorthEntrance_Frlg[2] UNTESTED** — untestable: Route6_NorthEntrance_Frlg cannot be loaded by the engine (see load check)
* **Route6_NorthEntrance_Frlg[3] UNTESTED** — untestable: Route6_NorthEntrance_Frlg cannot be loaded by the engine (see load check)

### `Route7_EastEntrance_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 5) | MB_WEST_ARROW_WARP | Route7_Frlg | (15, 10) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (1, 6) | MB_NORMAL | Route7_Frlg | (15, 10) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (11, 5) | MB_EAST_ARROW_WARP | SaffronCity_Frlg | (8, 27) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (11, 6) | MB_NORMAL | SaffronCity_Frlg | (8, 27) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route7_EastEntrance_Frlg[0] UNTESTED** — untestable: Route7_EastEntrance_Frlg cannot be loaded by the engine (see load check)
* **Route7_EastEntrance_Frlg[1] UNTESTED** — untestable: Route7_EastEntrance_Frlg cannot be loaded by the engine (see load check)
* **Route7_EastEntrance_Frlg[2] UNTESTED** — untestable: Route7_EastEntrance_Frlg cannot be loaded by the engine (see load check)
* **Route7_EastEntrance_Frlg[3] UNTESTED** — untestable: Route7_EastEntrance_Frlg cannot be loaded by the engine (see load check)

### `Route7_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 2 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 14) | MB_ANIMATED_DOOR | UndergroundPath_WestEntrance_Frlg | (6, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (15, 10) | MB_EAST_ARROW_WARP | Route7_EastEntrance_Frlg | (1, 5) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **Route7_Frlg[0] UNTESTED** — untestable: Route7_Frlg cannot be loaded by the engine (see load check)
* **Route7_Frlg[1] UNTESTED** — untestable: Route7_Frlg cannot be loaded by the engine (see load check)
* **Route7_Frlg conn[0] left/-10 -> CeladonCity_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route7_Frlg conn[1] right/-10 -> SaffronCity_Connection_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `Route8_Frlg`

*Tier: region trail endpoint — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (12, 17) | MB_NORMAL | UndergroundPath_EastEntrance_Frlg | (6, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |

* **Route8_Frlg[0] ISSUE** — stepping UP from (12,19) onto (12,17) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/Route8_Frlg_0_nowarp.png`

### `Route8_WestEntrance_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 4) | MB_NORMAL | SaffronCity_Frlg | (58, 27) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (1, 5) | MB_WEST_ARROW_WARP | SaffronCity_Frlg | (58, 27) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (11, 5) | MB_EAST_ARROW_WARP | Route8_Frlg | - | - | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (11, 6) | MB_NORMAL | Route8_Frlg | - | - | - | - | - (-) | - | - | **UNTESTED** |

* **Route8_WestEntrance_Frlg[0] UNTESTED** — untestable: Route8_WestEntrance_Frlg cannot be loaded by the engine (see load check)
* **Route8_WestEntrance_Frlg[1] UNTESTED** — untestable: Route8_WestEntrance_Frlg cannot be loaded by the engine (see load check)
* **Route8_WestEntrance_Frlg[2] UNTESTED** — untestable: Route8_WestEntrance_Frlg cannot be loaded by the engine (see load check)
* **Route8_WestEntrance_Frlg[3] UNTESTED** — untestable: Route8_WestEntrance_Frlg cannot be loaded by the engine (see load check)

### `Route9_Frlg`

*Tier: donor town/cave (vanilla base) — 0 warp(s), 2 connection(s), 2 finding(s).*

* **Route9_Frlg conn[0] left/-10 -> CeruleanCity_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **Route9_Frlg conn[1] right/0 -> Route10_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `RustboroCity`

*Tier: story-trigger map — 12 warp(s), 2 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (27, 19) | MB_ANIMATED_DOOR | RustboroCity_Gym | (5, 19) | MB_SOUTH_ARROW_WARP | (5, 19) | (5, 19) | UP (UP) | yes | same door | **OK** |
| 1 | (13, 30) | MB_ANIMATED_DOOR | RustboroCity_Flat1_1F | (6, 7) | MB_SOUTH_ARROW_WARP | (6, 7) | (6, 7) | UP (UP) | yes | same door | **OK** |
| 2 | (16, 45) | MB_ANIMATED_DOOR | RustboroCity_Mart | (3, 7) | MB_SOUTH_ARROW_WARP | (3, 7) | (3, 7) | UP (UP) | yes | same door | **OK** |
| 3 | (16, 38) | MB_ANIMATED_DOOR | RustboroCity_PokemonCenter_1F | (7, 8) | MB_SOUTH_ARROW_WARP | (7, 8) | (7, 8) | UP (UP) | yes | same door | **OK** |
| 4 | (27, 34) | MB_ANIMATED_DOOR | RustboroCity_PokemonSchool | (5, 10) | MB_SOUTH_ARROW_WARP | (5, 10) | (5, 10) | UP (UP) | yes | same door | **OK** |
| 5 | (11, 15) | MB_NON_ANIMATED_DOOR | RustboroCity_DevonCorp_1F | (5, 8) | MB_SOUTH_ARROW_WARP | (5, 8) | (5, 8) | UP (UP) | yes | same door | **OK** |
| 6 | (12, 15) | MB_NON_ANIMATED_DOOR | RustboroCity_DevonCorp_1F | (6, 8) | MB_SOUTH_ARROW_WARP | (6, 8) | (6, 8) | UP (UP) | yes | same door | **OK** |
| 7 | (33, 19) | MB_ANIMATED_DOOR | RustboroCity_House1 | (5, 7) | MB_SOUTH_ARROW_WARP | (5, 7) | (5, 7) | UP (UP) | yes | same door | **OK** |
| 8 | (9, 38) | MB_ANIMATED_DOOR | RustboroCity_CuttersHouse | (5, 8) | MB_SOUTH_ARROW_WARP | (5, 8) | (5, 8) | UP (UP) | yes | same door | **OK** |
| 9 | (30, 28) | MB_ANIMATED_DOOR | RustboroCity_House2 | (5, 8) | MB_SOUTH_ARROW_WARP | (5, 8) | (5, 8) | UP (UP) | yes | same door | **OK** |
| 10 | (5, 51) | MB_ANIMATED_DOOR | RustboroCity_Flat2_1F | (2, 8) | MB_SOUTH_ARROW_WARP | (2, 8) | (2, 8) | UP (UP) | yes | same door | **OK** |
| 11 | (26, 46) | MB_ANIMATED_DOOR | RustboroCity_House3 | (5, 8) | MB_SOUTH_ARROW_WARP | (5, 8) | (5, 8) | UP (UP) | yes | same door | **OK** |

* **RustboroCity conn[0] down/6 -> Route2_Frlg OK** — outward:OK (handed over to Route2_Frlg at (11,0)); inward:OK (returned to RustboroCity at (17,59))
* **RustboroCity conn[1] up/3 -> Route24_hns OK** — outward:OK (handed over to Route24_hns at (16,21)); inward:OK (returned to RustboroCity at (19,0))

### `RustboroCity_CuttersHouse`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_SOUTH_ARROW_WARP | RustboroCity | (9, 38) | MB_ANIMATED_DOOR | (9, 38) | (9, 39) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | RustboroCity | (9, 38) | MB_ANIMATED_DOOR | (9, 38) | (9, 39) | DOWN (DOWN) | yes | same door | **OK** |


### `RustboroCity_DevonCorp_1F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_SOUTH_ARROW_WARP | RustboroCity | (11, 15) | MB_NON_ANIMATED_DOOR | (11, 15) | (11, 16) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | RustboroCity | (12, 15) | MB_NON_ANIMATED_DOOR | (12, 15) | (12, 16) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (14, 1) | MB_NON_ANIMATED_DOOR | RustboroCity_DevonCorp_2F | (14, 1) | MB_NON_ANIMATED_DOOR | (14, 1) | (14, 2) | UP (DOWN) | yes | same door | **OK** |


### `RustboroCity_DevonCorp_2F`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (14, 1) | MB_NON_ANIMATED_DOOR | RustboroCity_DevonCorp_1F | (14, 1) | MB_NON_ANIMATED_DOOR | (14, 1) | (14, 2) | UP (DOWN) | yes | same door | **OK** |
| 1 | (2, 1) | MB_NON_ANIMATED_DOOR | RustboroCity_DevonCorp_3F | (2, 1) | MB_NON_ANIMATED_DOOR | (2, 1) | (2, 2) | UP (DOWN) | yes | same door | **OK** |


### `RustboroCity_DevonCorp_3F`

*Tier: other / unclassified base — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 1) | MB_NON_ANIMATED_DOOR | RustboroCity_DevonCorp_2F | (2, 1) | MB_NON_ANIMATED_DOOR | (2, 1) | (2, 2) | UP (DOWN) | yes | same door | **OK** |


### `RustboroCity_Flat1_1F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 7) | MB_SOUTH_ARROW_WARP | RustboroCity | (13, 30) | MB_ANIMATED_DOOR | (13, 30) | (13, 31) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (7, 7) | MB_SOUTH_ARROW_WARP | RustboroCity | (13, 30) | MB_ANIMATED_DOOR | (13, 30) | (13, 31) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (2, 1) | MB_NON_ANIMATED_DOOR | RustboroCity_Flat1_2F | (2, 1) | MB_NON_ANIMATED_DOOR | (2, 1) | (2, 2) | UP (DOWN) | yes | same door | **OK** |


### `RustboroCity_Flat1_2F`

*Tier: other / unclassified base — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 1) | MB_NON_ANIMATED_DOOR | RustboroCity_Flat1_1F | (2, 1) | MB_NON_ANIMATED_DOOR | (2, 1) | (2, 2) | UP (DOWN) | yes | same door | **OK** |


### `RustboroCity_Flat2_1F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 8) | MB_SOUTH_ARROW_WARP | RustboroCity | (5, 51) | MB_ANIMATED_DOOR | (5, 51) | (5, 52) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (3, 8) | MB_SOUTH_ARROW_WARP | RustboroCity | (5, 51) | MB_ANIMATED_DOOR | (5, 51) | (5, 52) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (3, 1) | MB_NON_ANIMATED_DOOR | RustboroCity_Flat2_2F | (3, 1) | MB_NON_ANIMATED_DOOR | (3, 1) | (3, 2) | UP (DOWN) | yes | same door | **OK** |


### `RustboroCity_Flat2_2F`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 1) | MB_NON_ANIMATED_DOOR | RustboroCity_Flat2_1F | (3, 1) | MB_NON_ANIMATED_DOOR | (3, 1) | (3, 2) | UP (DOWN) | yes | same door | **OK** |
| 1 | (1, 1) | MB_NON_ANIMATED_DOOR | RustboroCity_Flat2_3F | (1, 1) | MB_NON_ANIMATED_DOOR | (1, 1) | (1, 2) | UP (DOWN) | yes | same door | **OK** |


### `RustboroCity_Flat2_3F`

*Tier: other / unclassified base — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 1) | MB_NON_ANIMATED_DOOR | RustboroCity_Flat2_2F | (1, 1) | MB_NON_ANIMATED_DOOR | (1, 1) | (1, 2) | UP (DOWN) | yes | same door | **OK** |


### `RustboroCity_Gym`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 19) | MB_SOUTH_ARROW_WARP | RustboroCity | (27, 19) | MB_ANIMATED_DOOR | (27, 19) | (27, 20) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 19) | MB_SOUTH_ARROW_WARP | RustboroCity | (27, 19) | MB_ANIMATED_DOOR | (27, 19) | (27, 20) | DOWN (DOWN) | yes | same door | **OK** |


### `RustboroCity_House1`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 7) | MB_SOUTH_ARROW_WARP | RustboroCity | (33, 19) | MB_ANIMATED_DOOR | (33, 19) | (33, 20) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 7) | MB_SOUTH_ARROW_WARP | RustboroCity | (33, 19) | MB_ANIMATED_DOOR | (33, 19) | (33, 20) | DOWN (DOWN) | yes | same door | **OK** |


### `RustboroCity_House2`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_SOUTH_ARROW_WARP | RustboroCity | (30, 28) | MB_ANIMATED_DOOR | (30, 28) | (30, 29) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | RustboroCity | (30, 28) | MB_ANIMATED_DOOR | (30, 28) | (30, 29) | DOWN (DOWN) | yes | same door | **OK** |


### `RustboroCity_House3`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_SOUTH_ARROW_WARP | RustboroCity | (26, 46) | MB_ANIMATED_DOOR | (26, 46) | (26, 47) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | RustboroCity | (26, 46) | MB_ANIMATED_DOOR | (26, 46) | (26, 47) | DOWN (DOWN) | yes | same door | **OK** |


### `RustboroCity_Mart`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_SOUTH_ARROW_WARP | RustboroCity | (16, 45) | MB_ANIMATED_DOOR | (16, 45) | (16, 46) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | RustboroCity | (16, 45) | MB_ANIMATED_DOOR | (16, 45) | (16, 46) | DOWN (DOWN) | yes | same door | **OK** |


### `RustboroCity_PokemonCenter_1F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 8) | MB_SOUTH_ARROW_WARP | RustboroCity | (16, 38) | MB_ANIMATED_DOOR | (16, 38) | (16, 39) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | RustboroCity | (16, 38) | MB_ANIMATED_DOOR | (16, 38) | (16, 39) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (1, 6) | MB_UP_ESCALATOR | RustboroCity_PokemonCenter_2F | (1, 6) | MB_DOWN_ESCALATOR | (1, 6) | (2, 6) | LEFT (DOWN) | yes | same door | **OK** |


### `RustboroCity_PokemonCenter_2F`

*Tier: other / unclassified base — 3 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | RustboroCity_PokemonCenter_1F | (1, 6) | MB_UP_ESCALATOR | (1, 6) | (2, 6) | LEFT (DOWN) | yes | same door | **OK** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom | (7, 11) | MB_BRIDGE_OVER_OCEAN | (7, 11) | (7, 11) | DOWN (DOWN) | yes | same door | **OK** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter | (5, 8) | MB_SOUTH_ARROW_WARP | (5, 8) | (5, 8) | UP (UP) | yes | same door | **OK** |


### `RustboroCity_PokemonSchool`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 10) | MB_SOUTH_ARROW_WARP | RustboroCity | (27, 34) | MB_ANIMATED_DOOR | (27, 34) | (27, 35) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (6, 10) | MB_SOUTH_ARROW_WARP | RustboroCity | (27, 34) | MB_ANIMATED_DOOR | (27, 34) | (27, 35) | DOWN (DOWN) | yes | same door | **OK** |


### `SSAnne_1F_Corridor_Frlg`

*Tier: donor facility (vanilla) — 13 warp(s), 0 connection(s), 13 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 8) | MB_UP_LEFT_STAIR_WARP | SSAnne_2F_Corridor_Frlg | (2, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (2, 18) | MB_SOUTH_ARROW_WARP | SSAnne_Kitchen_Frlg | (7, 1) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (19, 1) | MB_ANIMATED_DOOR | SSAnne_Exterior_Frlg | (32, 14) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (20, 0) | MB_NORMAL | SSAnne_Exterior_Frlg | (33, 15) | MB_OCEAN_WATER | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (3, 20) | MB_NORMAL | SSAnne_Kitchen_Frlg | (7, 1) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (28, 17) | MB_DOWN_LEFT_STAIR_WARP | SSAnne_B1F_Corridor_Frlg | (19, 3) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (5, 10) | MB_SOUTH_ARROW_WARP | SSAnne_1F_Room1_Frlg | (2, 1) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (8, 10) | MB_SOUTH_ARROW_WARP | SSAnne_1F_Room2_Frlg | (2, 1) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (11, 10) | MB_SOUTH_ARROW_WARP | SSAnne_1F_Room3_Frlg | (2, 1) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (14, 10) | MB_SOUTH_ARROW_WARP | SSAnne_1F_Room4_Frlg | (2, 1) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 10 | (17, 10) | MB_SOUTH_ARROW_WARP | SSAnne_1F_Room5_Frlg | (2, 1) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 11 | (23, 10) | MB_SOUTH_ARROW_WARP | SSAnne_1F_Room7_Frlg | (2, 1) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 12 | (20, 10) | MB_SOUTH_ARROW_WARP | SSAnne_1F_Room6_Frlg | (2, 1) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_1F_Corridor_Frlg[0] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_1F_Corridor_Frlg[1] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_1F_Corridor_Frlg[2] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_1F_Corridor_Frlg[3] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_1F_Corridor_Frlg[4] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_1F_Corridor_Frlg[5] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_1F_Corridor_Frlg[6] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_1F_Corridor_Frlg[7] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_1F_Corridor_Frlg[8] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_1F_Corridor_Frlg[9] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_1F_Corridor_Frlg[10] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_1F_Corridor_Frlg[11] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_1F_Corridor_Frlg[12] UNTESTED** — untestable: SSAnne_1F_Corridor_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_1F_Room1_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 1) | MB_ANIMATED_DOOR | SSAnne_1F_Corridor_Frlg | (5, 10) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_1F_Room1_Frlg[0] UNTESTED** — untestable: SSAnne_1F_Room1_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_1F_Room2_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 1) | MB_ANIMATED_DOOR | SSAnne_1F_Corridor_Frlg | (8, 10) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_1F_Room2_Frlg[0] UNTESTED** — untestable: SSAnne_1F_Room2_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_1F_Room3_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 1) | MB_ANIMATED_DOOR | SSAnne_1F_Corridor_Frlg | (11, 10) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_1F_Room3_Frlg[0] UNTESTED** — untestable: SSAnne_1F_Room3_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_1F_Room4_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 1) | MB_ANIMATED_DOOR | SSAnne_1F_Corridor_Frlg | (14, 10) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_1F_Room4_Frlg[0] UNTESTED** — untestable: SSAnne_1F_Room4_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_1F_Room5_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 1) | MB_ANIMATED_DOOR | SSAnne_1F_Corridor_Frlg | (17, 10) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_1F_Room5_Frlg[0] UNTESTED** — untestable: SSAnne_1F_Room5_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_1F_Room6_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 1) | MB_ANIMATED_DOOR | SSAnne_1F_Corridor_Frlg | (20, 10) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_1F_Room6_Frlg[0] UNTESTED** — untestable: SSAnne_1F_Room6_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_1F_Room7_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 1) | MB_ANIMATED_DOOR | SSAnne_1F_Corridor_Frlg | (23, 10) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_1F_Room7_Frlg[0] UNTESTED** — untestable: SSAnne_1F_Room7_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_2F_Corridor_Frlg`

*Tier: donor facility (vanilla) — 9 warp(s), 0 connection(s), 9 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 2) | MB_DOWN_RIGHT_STAIR_WARP | SSAnne_1F_Corridor_Frlg | (3, 8) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (3, 12) | MB_UP_LEFT_STAIR_WARP | SSAnne_3F_Corridor_Frlg | (18, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (30, 2) | MB_UP_RIGHT_STAIR_WARP | SSAnne_CaptainsOffice_Frlg | (3, 7) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (6, 10) | MB_ANIMATED_DOOR | SSAnne_2F_Room1_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (10, 10) | MB_ANIMATED_DOOR | SSAnne_2F_Room2_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (14, 10) | MB_ANIMATED_DOOR | SSAnne_2F_Room3_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (18, 10) | MB_ANIMATED_DOOR | SSAnne_2F_Room4_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (22, 10) | MB_ANIMATED_DOOR | SSAnne_2F_Room5_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (26, 10) | MB_ANIMATED_DOOR | SSAnne_2F_Room6_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_2F_Corridor_Frlg[0] UNTESTED** — untestable: SSAnne_2F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_2F_Corridor_Frlg[1] UNTESTED** — untestable: SSAnne_2F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_2F_Corridor_Frlg[2] UNTESTED** — untestable: SSAnne_2F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_2F_Corridor_Frlg[3] UNTESTED** — untestable: SSAnne_2F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_2F_Corridor_Frlg[4] UNTESTED** — untestable: SSAnne_2F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_2F_Corridor_Frlg[5] UNTESTED** — untestable: SSAnne_2F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_2F_Corridor_Frlg[6] UNTESTED** — untestable: SSAnne_2F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_2F_Corridor_Frlg[7] UNTESTED** — untestable: SSAnne_2F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_2F_Corridor_Frlg[8] UNTESTED** — untestable: SSAnne_2F_Corridor_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_2F_Room1_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | SSAnne_2F_Corridor_Frlg | (6, 10) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_2F_Room1_Frlg[0] UNTESTED** — untestable: SSAnne_2F_Room1_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_2F_Room2_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | SSAnne_2F_Corridor_Frlg | (10, 10) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_2F_Room2_Frlg[0] UNTESTED** — untestable: SSAnne_2F_Room2_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_2F_Room3_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | SSAnne_2F_Corridor_Frlg | (14, 10) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_2F_Room3_Frlg[0] UNTESTED** — untestable: SSAnne_2F_Room3_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_2F_Room4_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | SSAnne_2F_Corridor_Frlg | (18, 10) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_2F_Room4_Frlg[0] UNTESTED** — untestable: SSAnne_2F_Room4_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_2F_Room5_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | SSAnne_2F_Corridor_Frlg | (22, 10) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_2F_Room5_Frlg[0] UNTESTED** — untestable: SSAnne_2F_Room5_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_2F_Room6_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | SSAnne_2F_Corridor_Frlg | (26, 10) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_2F_Room6_Frlg[0] UNTESTED** — untestable: SSAnne_2F_Room6_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_3F_Corridor_Frlg`

*Tier: donor facility (vanilla) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 4) | MB_WEST_ARROW_WARP | SSAnne_Deck_Frlg | (16, 8) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (18, 2) | MB_DOWN_RIGHT_STAIR_WARP | SSAnne_2F_Corridor_Frlg | (3, 12) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (0, 5) | MB_NORMAL | SSAnne_Deck_Frlg | (16, 8) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_3F_Corridor_Frlg[0] UNTESTED** — untestable: SSAnne_3F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_3F_Corridor_Frlg[1] UNTESTED** — untestable: SSAnne_3F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_3F_Corridor_Frlg[2] UNTESTED** — untestable: SSAnne_3F_Corridor_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_B1F_Corridor_Frlg`

*Tier: donor facility (vanilla) — 6 warp(s), 0 connection(s), 6 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (19, 3) | MB_UP_RIGHT_STAIR_WARP | SSAnne_1F_Corridor_Frlg | (28, 17) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (2, 2) | MB_ANIMATED_DOOR | SSAnne_B1F_Room1_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (6, 2) | MB_ANIMATED_DOOR | SSAnne_B1F_Room2_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (10, 2) | MB_ANIMATED_DOOR | SSAnne_B1F_Room3_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (14, 2) | MB_ANIMATED_DOOR | SSAnne_B1F_Room4_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (18, 2) | MB_ANIMATED_DOOR | SSAnne_B1F_Room5_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_B1F_Corridor_Frlg[0] UNTESTED** — untestable: SSAnne_B1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_B1F_Corridor_Frlg[1] UNTESTED** — untestable: SSAnne_B1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_B1F_Corridor_Frlg[2] UNTESTED** — untestable: SSAnne_B1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_B1F_Corridor_Frlg[3] UNTESTED** — untestable: SSAnne_B1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_B1F_Corridor_Frlg[4] UNTESTED** — untestable: SSAnne_B1F_Corridor_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_B1F_Corridor_Frlg[5] UNTESTED** — untestable: SSAnne_B1F_Corridor_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_B1F_Room1_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | SSAnne_B1F_Corridor_Frlg | (2, 2) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_B1F_Room1_Frlg[0] UNTESTED** — untestable: SSAnne_B1F_Room1_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_B1F_Room2_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | SSAnne_B1F_Corridor_Frlg | (6, 2) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_B1F_Room2_Frlg[0] UNTESTED** — untestable: SSAnne_B1F_Room2_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_B1F_Room3_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | SSAnne_B1F_Corridor_Frlg | (10, 2) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_B1F_Room3_Frlg[0] UNTESTED** — untestable: SSAnne_B1F_Room3_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_B1F_Room4_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | SSAnne_B1F_Corridor_Frlg | (14, 2) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_B1F_Room4_Frlg[0] UNTESTED** — untestable: SSAnne_B1F_Room4_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_B1F_Room5_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 7) | MB_SOUTH_ARROW_WARP | SSAnne_B1F_Corridor_Frlg | (18, 2) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_B1F_Room5_Frlg[0] UNTESTED** — untestable: SSAnne_B1F_Room5_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_CaptainsOffice_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_DOWN_LEFT_STAIR_WARP | SSAnne_2F_Corridor_Frlg | (30, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_CaptainsOffice_Frlg[0] UNTESTED** — untestable: SSAnne_CaptainsOffice_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_Deck_Frlg`

*Tier: donor facility (vanilla) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (16, 8) | MB_EAST_ARROW_WARP | SSAnne_3F_Corridor_Frlg | (1, 4) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (16, 9) | MB_EAST_ARROW_WARP | SSAnne_3F_Corridor_Frlg | (1, 4) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_Deck_Frlg[0] UNTESTED** — untestable: SSAnne_Deck_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_Deck_Frlg[1] UNTESTED** — untestable: SSAnne_Deck_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_Exterior_Frlg`

*Tier: donor facility (vanilla) — 5 warp(s), 0 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (31, 5) | MB_NORMAL | VermilionCity_Frlg | (22, 34) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (32, 5) | MB_NORTH_ARROW_WARP | VermilionCity_Frlg | (23, 34) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (32, 14) | MB_SOUTH_ARROW_WARP | SSAnne_1F_Corridor_Frlg | (19, 1) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (33, 15) | MB_OCEAN_WATER | SSAnne_1F_Corridor_Frlg | (20, 0) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (33, 5) | MB_NORMAL | VermilionCity_Frlg | (24, 34) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_Exterior_Frlg[0] UNTESTED** — untestable: SSAnne_Exterior_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_Exterior_Frlg[1] UNTESTED** — untestable: SSAnne_Exterior_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_Exterior_Frlg[2] UNTESTED** — untestable: SSAnne_Exterior_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_Exterior_Frlg[3] UNTESTED** — untestable: SSAnne_Exterior_Frlg cannot be loaded by the engine (see load check)
* **SSAnne_Exterior_Frlg[4] UNTESTED** — untestable: SSAnne_Exterior_Frlg cannot be loaded by the engine (see load check)

### `SSAnne_Kitchen_Frlg`

*Tier: donor facility (vanilla) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 1) | MB_ANIMATED_DOOR | SSAnne_1F_Corridor_Frlg | (2, 18) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SSAnne_Kitchen_Frlg[0] UNTESTED** — untestable: SSAnne_Kitchen_Frlg cannot be loaded by the engine (see load check)

### `SafariZone_Center_Frlg`

*Tier: donor facility (vanilla) — 13 warp(s), 0 connection(s), 13 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (25, 30) | MB_SOUTH_ARROW_WARP | FuchsiaCity_SafariZone_Entrance_Frlg | (4, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (26, 30) | MB_SOUTH_ARROW_WARP | FuchsiaCity_SafariZone_Entrance_Frlg | (4, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (27, 30) | MB_NORMAL | FuchsiaCity_SafariZone_Entrance_Frlg | (4, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (25, 5) | MB_NORTH_ARROW_WARP | SafariZone_North_Frlg | (30, 34) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (26, 5) | MB_NORTH_ARROW_WARP | SafariZone_North_Frlg | (31, 34) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (27, 5) | MB_NORMAL | SafariZone_North_Frlg | (32, 34) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (8, 17) | MB_WEST_ARROW_WARP | SafariZone_West_Frlg | (40, 26) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (8, 18) | MB_WEST_ARROW_WARP | SafariZone_West_Frlg | (40, 27) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (8, 19) | MB_NORMAL | SafariZone_West_Frlg | (40, 28) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (43, 15) | MB_EAST_ARROW_WARP | SafariZone_East_Frlg | (8, 26) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 10 | (43, 16) | MB_EAST_ARROW_WARP | SafariZone_East_Frlg | (8, 27) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 11 | (43, 17) | MB_NORMAL | SafariZone_East_Frlg | (8, 28) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 12 | (29, 25) | MB_ANIMATED_DOOR | SafariZone_Center_RestHouse_Frlg | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SafariZone_Center_Frlg[0] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_Frlg[1] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_Frlg[2] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_Frlg[3] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_Frlg[4] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_Frlg[5] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_Frlg[6] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_Frlg[7] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_Frlg[8] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_Frlg[9] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_Frlg[10] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_Frlg[11] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_Frlg[12] UNTESTED** — untestable: SafariZone_Center_Frlg cannot be loaded by the engine (see load check)

### `SafariZone_Center_RestHouse_Frlg`

*Tier: donor facility (vanilla) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 9) | MB_NORMAL | SafariZone_Center_Frlg | (29, 25) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 9) | MB_SOUTH_ARROW_WARP | SafariZone_Center_Frlg | (29, 25) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 9) | MB_NORMAL | SafariZone_Center_Frlg | (29, 25) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SafariZone_Center_RestHouse_Frlg[0] UNTESTED** — untestable: SafariZone_Center_RestHouse_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_RestHouse_Frlg[1] UNTESTED** — untestable: SafariZone_Center_RestHouse_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_Center_RestHouse_Frlg[2] UNTESTED** — untestable: SafariZone_Center_RestHouse_Frlg cannot be loaded by the engine (see load check)

### `SafariZone_East_Frlg`

*Tier: donor facility (vanilla) — 7 warp(s), 0 connection(s), 7 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (8, 9) | MB_WEST_ARROW_WARP | SafariZone_North_Frlg | (48, 31) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (8, 10) | MB_WEST_ARROW_WARP | SafariZone_North_Frlg | (48, 32) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 11) | MB_NORMAL | SafariZone_North_Frlg | (48, 33) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (8, 26) | MB_WEST_ARROW_WARP | SafariZone_Center_Frlg | (43, 15) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (8, 27) | MB_WEST_ARROW_WARP | SafariZone_Center_Frlg | (43, 16) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (8, 28) | MB_NORMAL | SafariZone_Center_Frlg | (43, 17) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (40, 14) | MB_ANIMATED_DOOR | SafariZone_East_RestHouse_Frlg | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SafariZone_East_Frlg[0] UNTESTED** — untestable: SafariZone_East_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_East_Frlg[1] UNTESTED** — untestable: SafariZone_East_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_East_Frlg[2] UNTESTED** — untestable: SafariZone_East_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_East_Frlg[3] UNTESTED** — untestable: SafariZone_East_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_East_Frlg[4] UNTESTED** — untestable: SafariZone_East_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_East_Frlg[5] UNTESTED** — untestable: SafariZone_East_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_East_Frlg[6] UNTESTED** — untestable: SafariZone_East_Frlg cannot be loaded by the engine (see load check)

### `SafariZone_East_RestHouse_Frlg`

*Tier: donor facility (vanilla) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 9) | MB_NORMAL | SafariZone_East_Frlg | (40, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 9) | MB_SOUTH_ARROW_WARP | SafariZone_East_Frlg | (40, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 9) | MB_NORMAL | SafariZone_East_Frlg | (40, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SafariZone_East_RestHouse_Frlg[0] UNTESTED** — untestable: SafariZone_East_RestHouse_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_East_RestHouse_Frlg[1] UNTESTED** — untestable: SafariZone_East_RestHouse_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_East_RestHouse_Frlg[2] UNTESTED** — untestable: SafariZone_East_RestHouse_Frlg cannot be loaded by the engine (see load check)

### `SafariZone_North_Frlg`

*Tier: donor facility (vanilla) — 13 warp(s), 0 connection(s), 13 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 34) | MB_SOUTH_ARROW_WARP | SafariZone_West_Frlg | (30, 5) | MB_NORTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (11, 34) | MB_SOUTH_ARROW_WARP | SafariZone_West_Frlg | (31, 5) | MB_NORTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (12, 34) | MB_NORMAL | SafariZone_West_Frlg | (32, 5) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (20, 34) | MB_SOUTH_ARROW_WARP | SafariZone_West_Frlg | (37, 5) | MB_NORTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (21, 34) | MB_SOUTH_ARROW_WARP | SafariZone_West_Frlg | (38, 5) | MB_NORTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (22, 34) | MB_NORMAL | SafariZone_West_Frlg | (39, 5) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (48, 31) | MB_EAST_ARROW_WARP | SafariZone_East_Frlg | (8, 9) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (48, 32) | MB_EAST_ARROW_WARP | SafariZone_East_Frlg | (8, 10) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (48, 33) | MB_NORMAL | SafariZone_East_Frlg | (8, 11) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (30, 34) | MB_SOUTH_ARROW_WARP | SafariZone_Center_Frlg | (25, 5) | MB_NORTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 10 | (31, 34) | MB_SOUTH_ARROW_WARP | SafariZone_Center_Frlg | (26, 5) | MB_NORTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 11 | (32, 34) | MB_NORMAL | SafariZone_Center_Frlg | (27, 5) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 12 | (43, 8) | MB_ANIMATED_DOOR | SafariZone_North_RestHouse_Frlg | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SafariZone_North_Frlg[0] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_Frlg[1] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_Frlg[2] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_Frlg[3] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_Frlg[4] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_Frlg[5] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_Frlg[6] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_Frlg[7] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_Frlg[8] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_Frlg[9] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_Frlg[10] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_Frlg[11] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_Frlg[12] UNTESTED** — untestable: SafariZone_North_Frlg cannot be loaded by the engine (see load check)

### `SafariZone_North_RestHouse_Frlg`

*Tier: donor facility (vanilla) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 9) | MB_NORMAL | SafariZone_North_Frlg | (43, 8) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 9) | MB_SOUTH_ARROW_WARP | SafariZone_North_Frlg | (43, 8) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 9) | MB_NORMAL | SafariZone_North_Frlg | (43, 8) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SafariZone_North_RestHouse_Frlg[0] UNTESTED** — untestable: SafariZone_North_RestHouse_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_RestHouse_Frlg[1] UNTESTED** — untestable: SafariZone_North_RestHouse_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_North_RestHouse_Frlg[2] UNTESTED** — untestable: SafariZone_North_RestHouse_Frlg cannot be loaded by the engine (see load check)

### `SafariZone_SecretHouse_Frlg`

*Tier: donor facility (vanilla) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 9) | MB_NORMAL | SafariZone_West_Frlg | (12, 7) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 9) | MB_SOUTH_ARROW_WARP | SafariZone_West_Frlg | (12, 7) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 9) | MB_NORMAL | SafariZone_West_Frlg | (12, 7) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SafariZone_SecretHouse_Frlg[0] UNTESTED** — untestable: SafariZone_SecretHouse_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_SecretHouse_Frlg[1] UNTESTED** — untestable: SafariZone_SecretHouse_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_SecretHouse_Frlg[2] UNTESTED** — untestable: SafariZone_SecretHouse_Frlg cannot be loaded by the engine (see load check)

### `SafariZone_West_Frlg`

*Tier: donor facility (vanilla) — 11 warp(s), 0 connection(s), 11 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (30, 5) | MB_NORTH_ARROW_WARP | SafariZone_North_Frlg | (10, 34) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (31, 5) | MB_NORTH_ARROW_WARP | SafariZone_North_Frlg | (11, 34) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (32, 5) | MB_NORMAL | SafariZone_North_Frlg | (12, 34) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (37, 5) | MB_NORTH_ARROW_WARP | SafariZone_North_Frlg | (20, 34) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (38, 5) | MB_NORTH_ARROW_WARP | SafariZone_North_Frlg | (21, 34) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (39, 5) | MB_NORMAL | SafariZone_North_Frlg | (22, 34) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (40, 26) | MB_EAST_ARROW_WARP | SafariZone_Center_Frlg | (8, 17) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (40, 27) | MB_EAST_ARROW_WARP | SafariZone_Center_Frlg | (8, 18) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (40, 28) | MB_NORMAL | SafariZone_Center_Frlg | (8, 19) | MB_NORMAL | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (12, 7) | MB_ANIMATED_DOOR | SafariZone_SecretHouse_Frlg | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 10 | (19, 18) | MB_ANIMATED_DOOR | SafariZone_West_RestHouse_Frlg | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SafariZone_West_Frlg[0] UNTESTED** — untestable: SafariZone_West_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_West_Frlg[1] UNTESTED** — untestable: SafariZone_West_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_West_Frlg[2] UNTESTED** — untestable: SafariZone_West_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_West_Frlg[3] UNTESTED** — untestable: SafariZone_West_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_West_Frlg[4] UNTESTED** — untestable: SafariZone_West_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_West_Frlg[5] UNTESTED** — untestable: SafariZone_West_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_West_Frlg[6] UNTESTED** — untestable: SafariZone_West_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_West_Frlg[7] UNTESTED** — untestable: SafariZone_West_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_West_Frlg[8] UNTESTED** — untestable: SafariZone_West_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_West_Frlg[9] UNTESTED** — untestable: SafariZone_West_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_West_Frlg[10] UNTESTED** — untestable: SafariZone_West_Frlg cannot be loaded by the engine (see load check)

### `SafariZone_West_RestHouse_Frlg`

*Tier: donor facility (vanilla) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 9) | MB_NORMAL | SafariZone_West_Frlg | (19, 18) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 9) | MB_SOUTH_ARROW_WARP | SafariZone_West_Frlg | (19, 18) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 9) | MB_NORMAL | SafariZone_West_Frlg | (19, 18) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SafariZone_West_RestHouse_Frlg[0] UNTESTED** — untestable: SafariZone_West_RestHouse_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_West_RestHouse_Frlg[1] UNTESTED** — untestable: SafariZone_West_RestHouse_Frlg cannot be loaded by the engine (see load check)
* **SafariZone_West_RestHouse_Frlg[2] UNTESTED** — untestable: SafariZone_West_RestHouse_Frlg cannot be loaded by the engine (see load check)

### `SaffronCity_Connection_Frlg`

*Tier: donor town/cave (vanilla base) — 0 warp(s), 4 connection(s), 4 finding(s).*

* **SaffronCity_Connection_Frlg conn[0] up/0 -> Route5_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **SaffronCity_Connection_Frlg conn[1] down/12 -> Route6_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **SaffronCity_Connection_Frlg conn[2] left/10 -> Route7_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **SaffronCity_Connection_Frlg conn[3] right/10 -> Route8_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `SaffronCity_CopycatsHouse_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 8) | MB_NORMAL | SaffronCity_Frlg | (22, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 8) | MB_SOUTH_ARROW_WARP | SaffronCity_Frlg | (22, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 8) | MB_NORMAL | SaffronCity_Frlg | (22, 14) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (10, 2) | MB_UP_RIGHT_STAIR_WARP | SaffronCity_CopycatsHouse_2F_Frlg | (10, 2) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SaffronCity_CopycatsHouse_1F_Frlg[0] UNTESTED** — untestable: SaffronCity_CopycatsHouse_1F_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_CopycatsHouse_1F_Frlg[1] UNTESTED** — untestable: SaffronCity_CopycatsHouse_1F_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_CopycatsHouse_1F_Frlg[2] UNTESTED** — untestable: SaffronCity_CopycatsHouse_1F_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_CopycatsHouse_1F_Frlg[3] UNTESTED** — untestable: SaffronCity_CopycatsHouse_1F_Frlg cannot be loaded by the engine (see load check)

### `SaffronCity_CopycatsHouse_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 2) | MB_DOWN_LEFT_STAIR_WARP | SaffronCity_CopycatsHouse_1F_Frlg | (10, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SaffronCity_CopycatsHouse_2F_Frlg[0] UNTESTED** — untestable: SaffronCity_CopycatsHouse_2F_Frlg cannot be loaded by the engine (see load check)

### `SaffronCity_Dojo_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 14) | MB_NORMAL | SaffronCity_Frlg | (40, 12) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 14) | MB_SOUTH_ARROW_WARP | SaffronCity_Frlg | (40, 12) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (7, 14) | MB_NORMAL | SaffronCity_Frlg | (40, 12) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SaffronCity_Dojo_Frlg[0] UNTESTED** — untestable: SaffronCity_Dojo_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Dojo_Frlg[1] UNTESTED** — untestable: SaffronCity_Dojo_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Dojo_Frlg[2] UNTESTED** — untestable: SaffronCity_Dojo_Frlg cannot be loaded by the engine (see load check)

### `SaffronCity_Frlg`

*Tier: donor town/cave (vanilla base) — 15 warp(s), 4 connection(s), 19 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (33, 30) | MB_ANIMATED_DOOR | SilphCo_1F_Frlg | (8, 20) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (22, 14) | MB_ANIMATED_DOOR | SaffronCity_CopycatsHouse_1F_Frlg | (4, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (40, 12) | MB_NON_ANIMATED_DOOR | SaffronCity_Dojo_Frlg | (6, 14) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (46, 12) | MB_ANIMATED_DOOR | SaffronCity_Gym_Frlg | (14, 23) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (27, 21) | MB_ANIMATED_DOOR | SaffronCity_House_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (40, 21) | MB_ANIMATED_DOOR | SaffronCity_Mart_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (24, 38) | MB_ANIMATED_DOOR | SaffronCity_PokemonCenter_1F_Frlg | (7, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (43, 38) | MB_ANIMATED_DOOR | SaffronCity_MrPsychicsHouse_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (8, 27) | MB_WEST_ARROW_WARP | Route7_EastEntrance_Frlg | (11, 5) | MB_EAST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (34, 5) | MB_NON_ANIMATED_DOOR | Route5_SouthEntrance_Frlg | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 10 | (58, 27) | MB_EAST_ARROW_WARP | Route8_WestEntrance_Frlg | (1, 5) | MB_WEST_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 11 | (34, 46) | MB_SOUTH_ARROW_WARP | Route6_NorthEntrance_Frlg | (4, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 12 | (35, 46) | MB_SOUTH_ARROW_WARP | Route6_NorthEntrance_Frlg | (4, 1) | MB_NON_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 13 | (35, 5) | MB_NON_ANIMATED_DOOR | Route5_SouthEntrance_Frlg | (4, 9) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 14 | (47, 21) | MB_ANIMATED_DOOR | SaffronCity_PokemonTrainerFanClub_Frlg | (5, 15) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SaffronCity_Frlg[0] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[1] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[2] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[3] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[4] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[5] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[6] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[7] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[8] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[9] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[10] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[11] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[12] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[13] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg[14] UNTESTED** — untestable: SaffronCity_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg conn[0] up/0 -> Route5_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg conn[1] down/12 -> Route6_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg conn[2] left/10 -> Route7_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **SaffronCity_Frlg conn[3] right/10 -> Route8_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `SaffronCity_Gym_Frlg`

*Tier: donor town/cave (vanilla base) — 33 warp(s), 0 connection(s), 33 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (13, 23) | MB_NORMAL | SaffronCity_Frlg | (46, 12) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (14, 23) | MB_SOUTH_ARROW_WARP | SaffronCity_Frlg | (46, 12) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (15, 23) | MB_NORMAL | SaffronCity_Frlg | (46, 12) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (18, 20) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (28, 23) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (0, 4) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (20, 7) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (0, 7) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (18, 15) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (0, 12) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (28, 15) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (0, 15) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (8, 7) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (0, 20) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (28, 7) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (0, 23) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (16, 7) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 10 | (8, 4) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (16, 4) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 11 | (8, 7) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (0, 15) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 12 | (8, 12) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (12, 7) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 13 | (8, 15) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (8, 23) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 14 | (8, 20) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (20, 23) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 15 | (8, 23) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (8, 15) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 16 | (12, 4) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (20, 15) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 17 | (12, 7) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (8, 12) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 18 | (16, 4) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (8, 4) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 19 | (16, 7) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (0, 23) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 20 | (18, 15) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (0, 7) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 21 | (20, 4) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (20, 12) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 22 | (20, 7) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (0, 4) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 23 | (20, 12) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (20, 4) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 24 | (20, 15) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (12, 4) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 25 | (20, 20) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (28, 4) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 26 | (20, 23) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (8, 20) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 27 | (28, 4) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (20, 20) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 28 | (28, 7) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (0, 20) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 29 | (28, 12) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (28, 20) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 30 | (28, 15) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (0, 12) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 31 | (28, 20) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (28, 12) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 32 | (28, 23) | MB_AQUA_HIDEOUT_WARP | SaffronCity_Gym_Frlg | (18, 20) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SaffronCity_Gym_Frlg[0] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[1] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[2] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[3] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[4] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[5] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[6] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[7] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[8] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[9] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[10] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[11] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[12] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[13] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[14] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[15] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[16] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[17] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[18] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[19] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[20] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[21] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[22] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[23] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[24] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[25] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[26] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[27] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[28] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[29] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[30] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[31] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Gym_Frlg[32] UNTESTED** — untestable: SaffronCity_Gym_Frlg cannot be loaded by the engine (see load check)

### `SaffronCity_House_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | SaffronCity_Frlg | (27, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | SaffronCity_Frlg | (27, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | SaffronCity_Frlg | (27, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SaffronCity_House_Frlg[0] UNTESTED** — untestable: SaffronCity_House_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_House_Frlg[1] UNTESTED** — untestable: SaffronCity_House_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_House_Frlg[2] UNTESTED** — untestable: SaffronCity_House_Frlg cannot be loaded by the engine (see load check)

### `SaffronCity_Mart_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | SaffronCity_Frlg | (40, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | SaffronCity_Frlg | (40, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | SaffronCity_Frlg | (40, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SaffronCity_Mart_Frlg[0] UNTESTED** — untestable: SaffronCity_Mart_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Mart_Frlg[1] UNTESTED** — untestable: SaffronCity_Mart_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_Mart_Frlg[2] UNTESTED** — untestable: SaffronCity_Mart_Frlg cannot be loaded by the engine (see load check)

### `SaffronCity_MrPsychicsHouse_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | SaffronCity_Frlg | (43, 38) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | SaffronCity_Frlg | (43, 38) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | SaffronCity_Frlg | (43, 38) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SaffronCity_MrPsychicsHouse_Frlg[0] UNTESTED** — untestable: SaffronCity_MrPsychicsHouse_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_MrPsychicsHouse_Frlg[1] UNTESTED** — untestable: SaffronCity_MrPsychicsHouse_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_MrPsychicsHouse_Frlg[2] UNTESTED** — untestable: SaffronCity_MrPsychicsHouse_Frlg cannot be loaded by the engine (see load check)

### `SaffronCity_PokemonCenter_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 8) | MB_NORMAL | SaffronCity_Frlg | (24, 38) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (7, 8) | MB_SOUTH_ARROW_WARP | SaffronCity_Frlg | (24, 38) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 8) | MB_NORMAL | SaffronCity_Frlg | (24, 38) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (1, 6) | MB_UP_ESCALATOR | SaffronCity_PokemonCenter_2F_Frlg | (1, 6) | MB_DOWN_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |

* **SaffronCity_PokemonCenter_1F_Frlg[0] UNTESTED** — untestable: SaffronCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_PokemonCenter_1F_Frlg[1] UNTESTED** — untestable: SaffronCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_PokemonCenter_1F_Frlg[2] UNTESTED** — untestable: SaffronCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_PokemonCenter_1F_Frlg[3] UNTESTED** — untestable: SaffronCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)

### `SaffronCity_PokemonCenter_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | SaffronCity_PokemonCenter_1F_Frlg | (1, 6) | MB_UP_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom_Frlg | (7, 11) | MB_BRIDGE_OVER_OCEAN | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter_Frlg | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SaffronCity_PokemonCenter_2F_Frlg[0] UNTESTED** — untestable: SaffronCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_PokemonCenter_2F_Frlg[1] UNTESTED** — untestable: SaffronCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **SaffronCity_PokemonCenter_2F_Frlg[2] UNTESTED** — untestable: SaffronCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)

### `SaffronCity_PokemonTrainerFanClub_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 15) | MB_SOUTH_ARROW_WARP | SaffronCity_Frlg | (47, 21) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **SaffronCity_PokemonTrainerFanClub_Frlg[0] UNTESTED** — untestable: SaffronCity_PokemonTrainerFanClub_Frlg cannot be loaded by the engine (see load check)

### `SaffronCity_hns`

*Tier: story-trigger map — 1 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (44, 21) | MB_ANIMATED_DOOR | Mart_Kanto_hns | (4, 7) | MB_SOUTH_ARROW_WARP | (4, 7) | (4, 7) | UP (UP) | yes | same door | **OK** |


### `SeafoamIslands_1F_Frlg`

*Tier: donor facility (vanilla) — 7 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 6) | MB_LADDER | SeafoamIslands_B1F_Frlg | (10, 6) | MB_LADDER | (10, 6) | (10, 6) | UP (KEEP) | yes | same door | **OK** |
| 1 | (31, 4) | MB_LADDER | SeafoamIslands_B1F_Frlg | (31, 4) | MB_LADDER | (31, 4) | (31, 4) | UP (KEEP) | yes | same door | **OK** |
| 2 | (28, 19) | MB_LADDER | SeafoamIslands_B1F_Frlg | (28, 19) | MB_LADDER | (28, 19) | (28, 19) | DOWN (KEEP) | yes | same door | **OK** |
| 3 | (6, 21) | MB_SOUTH_ARROW_WARP | PlasticOx_Route20West | (60, 8) | MB_ANIMATED_DOOR | (60, 8) | (60, 9) | DOWN (DOWN) | yes | same door | **OK** |
| 4 | (32, 21) | MB_SOUTH_ARROW_WARP | PlasticOx_Route20East | (6, 14) | MB_ANIMATED_DOOR | (6, 14) | (6, 15) | DOWN (DOWN) | yes | same door | **OK** |
| 5 | (21, 8) | MB_MT_PYRE_HOLE | SeafoamIslands_B1F_Frlg | (21, 8) | MB_CAVE | (21, 8) | (21, 8) | UP (DOWN) | yes | inconclusive | **PARTIAL** |
| 6 | (30, 8) | MB_MT_PYRE_HOLE | SeafoamIslands_B1F_Frlg | (29, 8) | MB_CAVE | (29, 8) | (29, 8) | UP (DOWN) | yes | WRONG MAP/TILE | **ISSUE** |

* **SeafoamIslands_1F_Frlg[5] PARTIAL** — (note) arrival facing reads as the travel direction UP; the player is still completing the warp step off a MB_CAVE; (note) INCONCLUSIVE return: no side of the return warp SeafoamIslands_B1F_Frlg[9] at (21,8) triggered a warp (tried ['UP', 'DOWN', 'LEFT', 'RIGHT'])
* **SeafoamIslands_1F_Frlg[6] ISSUE** — (note) arrival facing reads as the travel direction UP; the player is still completing the warp step off a MB_CAVE; (note) return landed in SeafoamIslands_B2F_Frlg at (29,8), expected SeafoamIslands_1F_Frlg at (30,8)
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_1F_Frlg_6_return.png`

### `SeafoamIslands_B1F_Frlg`

*Tier: donor facility (vanilla) — 11 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (10, 6) | MB_LADDER | SeafoamIslands_1F_Frlg | (10, 6) | MB_LADDER | (10, 6) | (10, 6) | UP (KEEP) | yes | same door | **OK** |
| 1 | (31, 4) | MB_LADDER | SeafoamIslands_1F_Frlg | (31, 4) | MB_LADDER | (31, 4) | (31, 4) | UP (KEEP) | yes | same door | **OK** |
| 2 | (28, 19) | MB_LADDER | SeafoamIslands_1F_Frlg | (28, 19) | MB_LADDER | (28, 19) | (28, 19) | LEFT (KEEP) | yes | same door | **OK** |
| 3 | (7, 3) | MB_LADDER | SeafoamIslands_B2F_Frlg | (7, 4) | MB_LADDER | (7, 4) | (7, 4) | UP (KEEP) | yes | same door | **OK** |
| 4 | (17, 9) | MB_LADDER | SeafoamIslands_B2F_Frlg | (17, 9) | MB_LADDER | (17, 9) | (17, 9) | UP (KEEP) | yes | same door | **OK** |
| 5 | (25, 19) | MB_LADDER | SeafoamIslands_B2F_Frlg | (25, 19) | MB_LADDER | (25, 19) | (25, 19) | DOWN (KEEP) | yes | same door | **OK** |
| 6 | (32, 14) | MB_LADDER | SeafoamIslands_B2F_Frlg | (32, 14) | MB_LADDER | (32, 14) | (32, 14) | UP (KEEP) | yes | same door | **OK** |
| 7 | (23, 8) | MB_MT_PYRE_HOLE | SeafoamIslands_B2F_Frlg | (22, 7) | MB_CAVE | (22, 7) | (22, 7) | UP (DOWN) | yes | inconclusive | **PARTIAL** |
| 8 | (28, 8) | MB_MT_PYRE_HOLE | SeafoamIslands_B2F_Frlg | (29, 8) | MB_CAVE | (29, 8) | (29, 8) | UP (DOWN) | yes | WRONG MAP/TILE | **ISSUE** |
| 9 | (21, 8) | MB_CAVE | SeafoamIslands_1F_Frlg | (21, 8) | MB_MT_PYRE_HOLE | - | - | - (-) | - | inconclusive | **ISSUE** |
| 10 | (29, 8) | MB_CAVE | SeafoamIslands_1F_Frlg | (30, 8) | MB_MT_PYRE_HOLE | - | - | - (-) | - | inconclusive | **ISSUE** |

* **SeafoamIslands_B1F_Frlg[7] PARTIAL** — (note) arrival facing reads as the travel direction UP; the player is still completing the warp step off a MB_CAVE; (note) INCONCLUSIVE return: no side of the return warp SeafoamIslands_B2F_Frlg[7] at (22,7) triggered a warp (tried ['UP', 'DOWN', 'LEFT', 'RIGHT'])
* **SeafoamIslands_B1F_Frlg[8] ISSUE** — (note) arrival facing reads as the travel direction UP; the player is still completing the warp step off a MB_CAVE; (note) return landed in SeafoamIslands_B4F_Frlg at (24,9), expected SeafoamIslands_B1F_Frlg at (28,8)
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B1F_Frlg_8_return.png`
* **SeafoamIslands_B1F_Frlg[9] ISSUE** — stepping UP from (21,9) onto (21,8) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B1F_Frlg_9_nowarp.png`
* **SeafoamIslands_B1F_Frlg[10] ISSUE** — stepping UP from (29,9) onto (29,8) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B1F_Frlg_10_nowarp.png`

### `SeafoamIslands_B2F_Frlg`

*Tier: donor facility (vanilla) — 11 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 17) | MB_LADDER | SeafoamIslands_B3F_Frlg | (8, 14) | MB_LADDER | (8, 14) | (8, 14) | UP (KEEP) | yes | same door | **OK** |
| 1 | (32, 4) | MB_LADDER | SeafoamIslands_B3F_Frlg | (31, 4) | MB_LADDER | (31, 4) | (31, 4) | UP (KEEP) | yes | same door | **OK** |
| 2 | (31, 17) | MB_LADDER | SeafoamIslands_B3F_Frlg | (31, 16) | MB_LADDER | (31, 16) | (31, 16) | UP (KEEP) | yes | same door | **OK** |
| 3 | (7, 4) | MB_LADDER | SeafoamIslands_B1F_Frlg | (7, 3) | MB_LADDER | (7, 3) | (7, 3) | UP (KEEP) | yes | same door | **OK** |
| 4 | (17, 9) | MB_LADDER | SeafoamIslands_B1F_Frlg | (17, 9) | MB_LADDER | (17, 9) | (17, 9) | UP (KEEP) | yes | same door | **OK** |
| 5 | (25, 19) | MB_LADDER | SeafoamIslands_B1F_Frlg | (25, 19) | MB_LADDER | (25, 19) | (25, 19) | LEFT (KEEP) | yes | same door | **OK** |
| 6 | (32, 14) | MB_LADDER | SeafoamIslands_B1F_Frlg | (32, 14) | MB_LADDER | (32, 14) | (32, 14) | UP (KEEP) | yes | same door | **OK** |
| 7 | (22, 7) | MB_CAVE | SeafoamIslands_B1F_Frlg | (23, 8) | MB_MT_PYRE_HOLE | - | - | - (-) | - | inconclusive | **ISSUE** |
| 8 | (29, 8) | MB_CAVE | SeafoamIslands_B1F_Frlg | (28, 8) | MB_MT_PYRE_HOLE | - | - | - (-) | - | inconclusive | **ISSUE** |
| 9 | (24, 8) | MB_MT_PYRE_HOLE | SeafoamIslands_B3F_Frlg | (23, 9) | MB_SOUTHWARD_CURRENT | (23, 9) | (26, 17) | DOWN (DOWN) | NO | inconclusive | **ISSUE** |
| 10 | (27, 8) | MB_MT_PYRE_HOLE | SeafoamIslands_B3F_Frlg | (24, 9) | MB_SOUTHWARD_CURRENT | (24, 9) | (26, 18) | UP (DOWN) | NO | inconclusive | **ISSUE** |

* **SeafoamIslands_B2F_Frlg[7] ISSUE** — stepping UP from (22,8) onto (22,7) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B2F_Frlg_7_nowarp.png`
* **SeafoamIslands_B2F_Frlg[8] ISSUE** — stepping UP from (29,9) onto (29,8) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B2F_Frlg_8_nowarp.png`
* **SeafoamIslands_B2F_Frlg[9] ISSUE** — player slid 11 tiles from the landing (23,9) to (26,17); player is wedged on the landing tile (26,17); (note) INCONCLUSIVE return: no side of the return warp SeafoamIslands_B3F_Frlg[5] at (23,9) triggered a warp (tried ['UP', 'DOWN', 'LEFT', 'RIGHT'])
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B2F_Frlg_9_issue.png`
* **SeafoamIslands_B2F_Frlg[10] ISSUE** — player slid 11 tiles from the landing (24,9) to (26,18); player is wedged on the landing tile (26,18); (note) arrival facing reads as the travel direction UP; the player is still completing the warp step off a MB_OCEAN_WATER; (note) INCONCLUSIVE return: no side of the return warp SeafoamIslands_B3F_Frlg[6] at (24,9) triggered a warp (tried ['UP', 'DOWN', 'LEFT', 'RIGHT'])
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B2F_Frlg_10_issue.png`

### `SeafoamIslands_B3F_Frlg`

*Tier: donor facility (vanilla) — 9 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (8, 14) | MB_LADDER | SeafoamIslands_B2F_Frlg | (7, 17) | MB_LADDER | (7, 17) | (7, 17) | LEFT (KEEP) | yes | same door | **OK** |
| 1 | (31, 4) | MB_LADDER | SeafoamIslands_B2F_Frlg | (32, 4) | MB_LADDER | (32, 4) | (32, 4) | UP (KEEP) | yes | same door | **OK** |
| 2 | (31, 16) | MB_LADDER | SeafoamIslands_B2F_Frlg | (31, 17) | MB_LADDER | (31, 17) | (31, 17) | LEFT (KEEP) | yes | same door | **OK** |
| 3 | (12, 9) | MB_LADDER | SeafoamIslands_B4F_Frlg | (15, 9) | MB_LADDER | (15, 9) | (15, 9) | UP (KEEP) | yes | same door | **OK** |
| 4 | (29, 5) | MB_LADDER | SeafoamIslands_B4F_Frlg | (32, 5) | MB_LADDER | (32, 5) | (32, 5) | UP (KEEP) | yes | same door | **OK** |
| 5 | (23, 9) | MB_SOUTHWARD_CURRENT | SeafoamIslands_B2F_Frlg | (22, 7) | MB_CAVE | - | - | - (-) | - | inconclusive | **ISSUE** |
| 6 | (24, 9) | MB_SOUTHWARD_CURRENT | SeafoamIslands_B2F_Frlg | (29, 8) | MB_CAVE | - | - | - (-) | - | inconclusive | **ISSUE** |
| 7 | (6, 18) | MB_MT_PYRE_HOLE | SeafoamIslands_B4F_Frlg | (8, 17) | MB_NORTHWARD_CURRENT | (8, 17) | (11, 14) | UP (DOWN) | yes | inconclusive | **ISSUE** |
| 8 | (9, 18) | MB_MT_PYRE_HOLE | SeafoamIslands_B4F_Frlg | (9, 17) | MB_NORTHWARD_CURRENT | (9, 17) | (9, 15) | UP (DOWN) | yes | inconclusive | **ISSUE** |

* **SeafoamIslands_B3F_Frlg[5] ISSUE** — stepping UP from (23,10) onto (23,9) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B3F_Frlg_5_nowarp.png`
* **SeafoamIslands_B3F_Frlg[6] ISSUE** — stepping UP from (24,10) onto (24,9) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B3F_Frlg_6_nowarp.png`
* **SeafoamIslands_B3F_Frlg[7] ISSUE** — player slid 6 tiles from the landing (8,17) to (11,14); (note) arrival facing reads as the travel direction UP; the player is still completing the warp step off a MB_OCEAN_WATER; (note) INCONCLUSIVE return: no side of the return warp SeafoamIslands_B4F_Frlg[2] at (8,17) triggered a warp (tried ['UP', 'DOWN', 'LEFT'])
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B3F_Frlg_7_issue.png`
* **SeafoamIslands_B3F_Frlg[8] ISSUE** — player slid 2 tiles from the landing (9,17) to (9,15); (note) arrival facing sampled after the transition finished, not on the landing tile; (note) arrival facing reads as the travel direction UP; the player is still completing the warp step off a MB_OCEAN_WATER; (note) INCONCLUSIVE return: no side of the return warp SeafoamIslands_B4F_Frlg[3] at (9,17) triggered a warp (tried ['UP', 'DOWN', 'LEFT', 'RIGHT'])
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B3F_Frlg_8_issue.png`

### `SeafoamIslands_B4F_Frlg`

*Tier: donor facility (vanilla) — 4 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (15, 9) | MB_LADDER | SeafoamIslands_B3F_Frlg | (12, 9) | MB_LADDER | (12, 9) | (12, 9) | UP (KEEP) | yes | same door | **OK** |
| 1 | (32, 5) | MB_LADDER | SeafoamIslands_B3F_Frlg | (29, 5) | MB_LADDER | (29, 5) | (29, 5) | LEFT (KEEP) | yes | same door | **OK** |
| 2 | (8, 17) | MB_NORTHWARD_CURRENT | SeafoamIslands_B3F_Frlg | (6, 18) | MB_MT_PYRE_HOLE | - | - | - (-) | - | inconclusive | **ISSUE** |
| 3 | (9, 17) | MB_NORTHWARD_CURRENT | SeafoamIslands_B3F_Frlg | (9, 18) | MB_MT_PYRE_HOLE | - | - | - (-) | - | inconclusive | **ISSUE** |

* **SeafoamIslands_B4F_Frlg[2] ISSUE** — stepping UP from (8,18) onto (8,17) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B4F_Frlg_2_nowarp.png`
* **SeafoamIslands_B4F_Frlg[3] ISSUE** — stepping UP from (9,18) onto (9,17) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/SeafoamIslands_B4F_Frlg_3_nowarp.png`

### `SilphCo_10F_Frlg`

*Tier: donor town/cave (vanilla base) — 6 warp(s), 0 connection(s), 6 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 2) | MB_UP_LEFT_STAIR_WARP | SilphCo_11F_Frlg | (7, 2) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (10, 14) | MB_AQUA_HIDEOUT_WARP | SilphCo_4F_Frlg | (12, 9) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (14, 9) | MB_AQUA_HIDEOUT_WARP | SilphCo_4F_Frlg | (18, 14) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (8, 2) | MB_DOWN_RIGHT_STAIR_WARP | SilphCo_9F_Frlg | (18, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (14, 17) | MB_AQUA_HIDEOUT_WARP | SilphCo_4F_Frlg | (2, 20) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (13, 3) | MB_ANIMATED_DOOR | SilphCo_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SilphCo_10F_Frlg[0] UNTESTED** — untestable: SilphCo_10F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_10F_Frlg[1] UNTESTED** — untestable: SilphCo_10F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_10F_Frlg[2] UNTESTED** — untestable: SilphCo_10F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_10F_Frlg[3] UNTESTED** — untestable: SilphCo_10F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_10F_Frlg[4] UNTESTED** — untestable: SilphCo_10F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_10F_Frlg[5] UNTESTED** — untestable: SilphCo_10F_Frlg cannot be loaded by the engine (see load check)

### `SilphCo_11F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 2) | MB_DOWN_LEFT_STAIR_WARP | SilphCo_10F_Frlg | (6, 2) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (2, 5) | MB_AQUA_HIDEOUT_WARP | SilphCo_7F_Frlg | (5, 8) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (13, 3) | MB_ANIMATED_DOOR | SilphCo_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SilphCo_11F_Frlg[0] UNTESTED** — untestable: SilphCo_11F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_11F_Frlg[1] UNTESTED** — untestable: SilphCo_11F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_11F_Frlg[2] UNTESTED** — untestable: SilphCo_11F_Frlg cannot be loaded by the engine (see load check)

### `SilphCo_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 5 warp(s), 0 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 21) | MB_NORMAL | SaffronCity_Frlg | (33, 30) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (8, 20) | MB_SOUTH_ARROW_WARP | SaffronCity_Frlg | (33, 30) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 20) | MB_NORMAL | SaffronCity_Frlg | (33, 30) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (31, 2) | MB_UP_RIGHT_STAIR_WARP | SilphCo_2F_Frlg | (30, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (22, 3) | MB_ANIMATED_DOOR | SilphCo_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SilphCo_1F_Frlg[0] UNTESTED** — untestable: SilphCo_1F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_1F_Frlg[1] UNTESTED** — untestable: SilphCo_1F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_1F_Frlg[2] UNTESTED** — untestable: SilphCo_1F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_1F_Frlg[3] UNTESTED** — untestable: SilphCo_1F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_1F_Frlg[4] UNTESTED** — untestable: SilphCo_1F_Frlg cannot be loaded by the engine (see load check)

### `SilphCo_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 7 warp(s), 0 connection(s), 7 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (28, 2) | MB_UP_LEFT_STAIR_WARP | SilphCo_3F_Frlg | (28, 2) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (2, 6) | MB_AQUA_HIDEOUT_WARP | SilphCo_3F_Frlg | (33, 5) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (15, 6) | MB_AQUA_HIDEOUT_WARP | SilphCo_8F_Frlg | (2, 17) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (30, 2) | MB_DOWN_RIGHT_STAIR_WARP | SilphCo_1F_Frlg | (31, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (7, 19) | MB_AQUA_HIDEOUT_WARP | SilphCo_6F_Frlg | (29, 5) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (33, 19) | MB_AQUA_HIDEOUT_WARP | SilphCo_8F_Frlg | (10, 6) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (22, 3) | MB_ANIMATED_DOOR | SilphCo_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SilphCo_2F_Frlg[0] UNTESTED** — untestable: SilphCo_2F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_2F_Frlg[1] UNTESTED** — untestable: SilphCo_2F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_2F_Frlg[2] UNTESTED** — untestable: SilphCo_2F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_2F_Frlg[3] UNTESTED** — untestable: SilphCo_2F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_2F_Frlg[4] UNTESTED** — untestable: SilphCo_2F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_2F_Frlg[5] UNTESTED** — untestable: SilphCo_2F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_2F_Frlg[6] UNTESTED** — untestable: SilphCo_2F_Frlg cannot be loaded by the engine (see load check)

### `SilphCo_3F_Frlg`

*Tier: donor town/cave (vanilla base) — 10 warp(s), 0 connection(s), 10 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (28, 2) | MB_DOWN_LEFT_STAIR_WARP | SilphCo_2F_Frlg | (28, 2) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 6) | MB_AQUA_HIDEOUT_WARP | SilphCo_5F_Frlg | (15, 7) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (13, 14) | MB_AQUA_HIDEOUT_WARP | SilphCo_7F_Frlg | (5, 4) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (30, 2) | MB_UP_RIGHT_STAIR_WARP | SilphCo_4F_Frlg | (30, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (2, 14) | MB_AQUA_HIDEOUT_WARP | SilphCo_9F_Frlg | (9, 4) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (3, 20) | MB_AQUA_HIDEOUT_WARP | SilphCo_5F_Frlg | (2, 20) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (29, 14) | MB_AQUA_HIDEOUT_WARP | SilphCo_3F_Frlg | (32, 20) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (32, 20) | MB_AQUA_HIDEOUT_WARP | SilphCo_3F_Frlg | (29, 14) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (33, 5) | MB_AQUA_HIDEOUT_WARP | SilphCo_2F_Frlg | (2, 6) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (22, 3) | MB_ANIMATED_DOOR | SilphCo_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SilphCo_3F_Frlg[0] UNTESTED** — untestable: SilphCo_3F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_3F_Frlg[1] UNTESTED** — untestable: SilphCo_3F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_3F_Frlg[2] UNTESTED** — untestable: SilphCo_3F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_3F_Frlg[3] UNTESTED** — untestable: SilphCo_3F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_3F_Frlg[4] UNTESTED** — untestable: SilphCo_3F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_3F_Frlg[5] UNTESTED** — untestable: SilphCo_3F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_3F_Frlg[6] UNTESTED** — untestable: SilphCo_3F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_3F_Frlg[7] UNTESTED** — untestable: SilphCo_3F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_3F_Frlg[8] UNTESTED** — untestable: SilphCo_3F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_3F_Frlg[9] UNTESTED** — untestable: SilphCo_3F_Frlg cannot be loaded by the engine (see load check)

### `SilphCo_4F_Frlg`

*Tier: donor town/cave (vanilla base) — 7 warp(s), 0 connection(s), 7 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (28, 2) | MB_UP_LEFT_STAIR_WARP | SilphCo_5F_Frlg | (28, 2) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (18, 6) | MB_AQUA_HIDEOUT_WARP | SilphCo_6F_Frlg | (2, 6) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (30, 2) | MB_DOWN_RIGHT_STAIR_WARP | SilphCo_3F_Frlg | (30, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (12, 9) | MB_AQUA_HIDEOUT_WARP | SilphCo_10F_Frlg | (10, 14) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (2, 20) | MB_AQUA_HIDEOUT_WARP | SilphCo_10F_Frlg | (14, 17) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (18, 14) | MB_AQUA_HIDEOUT_WARP | SilphCo_10F_Frlg | (14, 9) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (22, 3) | MB_ANIMATED_DOOR | SilphCo_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SilphCo_4F_Frlg[0] UNTESTED** — untestable: SilphCo_4F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_4F_Frlg[1] UNTESTED** — untestable: SilphCo_4F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_4F_Frlg[2] UNTESTED** — untestable: SilphCo_4F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_4F_Frlg[3] UNTESTED** — untestable: SilphCo_4F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_4F_Frlg[4] UNTESTED** — untestable: SilphCo_4F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_4F_Frlg[5] UNTESTED** — untestable: SilphCo_4F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_4F_Frlg[6] UNTESTED** — untestable: SilphCo_4F_Frlg cannot be loaded by the engine (see load check)

### `SilphCo_5F_Frlg`

*Tier: donor town/cave (vanilla base) — 7 warp(s), 0 connection(s), 7 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (28, 2) | MB_DOWN_LEFT_STAIR_WARP | SilphCo_4F_Frlg | (28, 2) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (15, 7) | MB_AQUA_HIDEOUT_WARP | SilphCo_3F_Frlg | (4, 6) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (30, 2) | MB_UP_RIGHT_STAIR_WARP | SilphCo_6F_Frlg | (26, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (10, 20) | MB_AQUA_HIDEOUT_WARP | SilphCo_9F_Frlg | (22, 18) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (2, 20) | MB_AQUA_HIDEOUT_WARP | SilphCo_3F_Frlg | (3, 20) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (33, 5) | MB_AQUA_HIDEOUT_WARP | SilphCo_7F_Frlg | (25, 17) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (22, 3) | MB_ANIMATED_DOOR | SilphCo_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SilphCo_5F_Frlg[0] UNTESTED** — untestable: SilphCo_5F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_5F_Frlg[1] UNTESTED** — untestable: SilphCo_5F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_5F_Frlg[2] UNTESTED** — untestable: SilphCo_5F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_5F_Frlg[3] UNTESTED** — untestable: SilphCo_5F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_5F_Frlg[4] UNTESTED** — untestable: SilphCo_5F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_5F_Frlg[5] UNTESTED** — untestable: SilphCo_5F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_5F_Frlg[6] UNTESTED** — untestable: SilphCo_5F_Frlg cannot be loaded by the engine (see load check)

### `SilphCo_6F_Frlg`

*Tier: donor town/cave (vanilla base) — 5 warp(s), 0 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (14, 2) | MB_UP_LEFT_STAIR_WARP | SilphCo_7F_Frlg | (19, 2) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (29, 5) | MB_AQUA_HIDEOUT_WARP | SilphCo_2F_Frlg | (7, 19) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (26, 2) | MB_DOWN_RIGHT_STAIR_WARP | SilphCo_5F_Frlg | (30, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (2, 6) | MB_AQUA_HIDEOUT_WARP | SilphCo_4F_Frlg | (18, 6) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (20, 3) | MB_ANIMATED_DOOR | SilphCo_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SilphCo_6F_Frlg[0] UNTESTED** — untestable: SilphCo_6F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_6F_Frlg[1] UNTESTED** — untestable: SilphCo_6F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_6F_Frlg[2] UNTESTED** — untestable: SilphCo_6F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_6F_Frlg[3] UNTESTED** — untestable: SilphCo_6F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_6F_Frlg[4] UNTESTED** — untestable: SilphCo_6F_Frlg cannot be loaded by the engine (see load check)

### `SilphCo_7F_Frlg`

*Tier: donor town/cave (vanilla base) — 6 warp(s), 0 connection(s), 6 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (19, 2) | MB_DOWN_LEFT_STAIR_WARP | SilphCo_6F_Frlg | (14, 2) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 8) | MB_AQUA_HIDEOUT_WARP | SilphCo_11F_Frlg | (2, 5) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (25, 17) | MB_AQUA_HIDEOUT_WARP | SilphCo_5F_Frlg | (33, 5) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (27, 2) | MB_UP_RIGHT_STAIR_WARP | SilphCo_8F_Frlg | (28, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (5, 4) | MB_AQUA_HIDEOUT_WARP | SilphCo_3F_Frlg | (13, 14) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (23, 3) | MB_ANIMATED_DOOR | SilphCo_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SilphCo_7F_Frlg[0] UNTESTED** — untestable: SilphCo_7F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_7F_Frlg[1] UNTESTED** — untestable: SilphCo_7F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_7F_Frlg[2] UNTESTED** — untestable: SilphCo_7F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_7F_Frlg[3] UNTESTED** — untestable: SilphCo_7F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_7F_Frlg[4] UNTESTED** — untestable: SilphCo_7F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_7F_Frlg[5] UNTESTED** — untestable: SilphCo_7F_Frlg cannot be loaded by the engine (see load check)

### `SilphCo_8F_Frlg`

*Tier: donor town/cave (vanilla base) — 7 warp(s), 0 connection(s), 7 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (16, 2) | MB_UP_LEFT_STAIR_WARP | SilphCo_9F_Frlg | (16, 2) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (11, 10) | MB_AQUA_HIDEOUT_WARP | SilphCo_8F_Frlg | (2, 12) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (10, 6) | MB_AQUA_HIDEOUT_WARP | SilphCo_2F_Frlg | (33, 19) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (28, 2) | MB_DOWN_RIGHT_STAIR_WARP | SilphCo_7F_Frlg | (27, 2) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (2, 12) | MB_AQUA_HIDEOUT_WARP | SilphCo_8F_Frlg | (11, 10) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (2, 17) | MB_AQUA_HIDEOUT_WARP | SilphCo_2F_Frlg | (15, 6) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (22, 3) | MB_ANIMATED_DOOR | SilphCo_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SilphCo_8F_Frlg[0] UNTESTED** — untestable: SilphCo_8F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_8F_Frlg[1] UNTESTED** — untestable: SilphCo_8F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_8F_Frlg[2] UNTESTED** — untestable: SilphCo_8F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_8F_Frlg[3] UNTESTED** — untestable: SilphCo_8F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_8F_Frlg[4] UNTESTED** — untestable: SilphCo_8F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_8F_Frlg[5] UNTESTED** — untestable: SilphCo_8F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_8F_Frlg[6] UNTESTED** — untestable: SilphCo_8F_Frlg cannot be loaded by the engine (see load check)

### `SilphCo_9F_Frlg`

*Tier: donor town/cave (vanilla base) — 5 warp(s), 0 connection(s), 5 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (16, 2) | MB_DOWN_LEFT_STAIR_WARP | SilphCo_8F_Frlg | (16, 2) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (22, 18) | MB_AQUA_HIDEOUT_WARP | SilphCo_5F_Frlg | (10, 20) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 4) | MB_AQUA_HIDEOUT_WARP | SilphCo_3F_Frlg | (2, 14) | MB_AQUA_HIDEOUT_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (18, 2) | MB_UP_RIGHT_STAIR_WARP | SilphCo_10F_Frlg | (8, 2) | MB_DOWN_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (24, 3) | MB_ANIMATED_DOOR | SilphCo_Elevator_Frlg | (2, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **SilphCo_9F_Frlg[0] UNTESTED** — untestable: SilphCo_9F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_9F_Frlg[1] UNTESTED** — untestable: SilphCo_9F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_9F_Frlg[2] UNTESTED** — untestable: SilphCo_9F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_9F_Frlg[3] UNTESTED** — untestable: SilphCo_9F_Frlg cannot be loaded by the engine (see load check)
* **SilphCo_9F_Frlg[4] UNTESTED** — untestable: SilphCo_9F_Frlg cannot be loaded by the engine (see load check)

### `SilphCo_Elevator_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (2, 5) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | - | - | - (-) | - | - | **UNTESTED** |

* **SilphCo_Elevator_Frlg[0] UNTESTED** — untestable: SilphCo_Elevator_Frlg cannot be loaded by the engine (see load check)

### `TradeCenter`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | (5, 8) | (5, 8) | UP (UP) | yes | same door | **OK** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | (5, 8) | (5, 8) | UP (UP) | yes | same door | **OK** |


### `TradeCenter_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | MAP_DYNAMIC | - | - | - | - | - (-) | - | - | **UNTESTED** |

* **TradeCenter_Frlg[0] UNTESTED** — untestable: TradeCenter_Frlg cannot be loaded by the engine (see load check)
* **TradeCenter_Frlg[1] UNTESTED** — untestable: TradeCenter_Frlg cannot be loaded by the engine (see load check)

### `UndergroundPath_EastEntrance_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_NORMAL | Route8_Frlg | (12, 17) | MB_NORMAL | - | - | - (-) | - | inconclusive | **ISSUE** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | Route8_Frlg | (12, 17) | MB_NORMAL | (12, 17) | (12, 17) | DOWN (DOWN) | NO | inconclusive | **ISSUE** |
| 2 | (7, 8) | MB_NORMAL | Route8_Frlg | (12, 17) | MB_NORMAL | - | - | - (-) | - | inconclusive | **ISSUE** |
| 3 | (7, 4) | MB_DOWN_LEFT_STAIR_WARP | UndergroundPath_EastWestTunnel_Frlg | (76, 3) | MB_UP_RIGHT_STAIR_WARP | (76, 3) | (76, 3) | LEFT (LEFT) | yes | same door | **OK** |

* **UndergroundPath_EastEntrance_Frlg[0] ISSUE** — stepping DOWN from (5,7) onto (5,8) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/UndergroundPath_EastEntrance_Frlg_0_nowarp.png`
* **UndergroundPath_EastEntrance_Frlg[1] ISSUE** — lands on a solid tile (MB_NORMAL) at (12,17); player is wedged on the landing tile (12,17); (note) arrival facing DOWN points into a blocked tile (12,18); (note) INCONCLUSIVE return: no side of the return warp Route8_Frlg[0] at (12,17) triggered a warp (tried ['UP', 'LEFT'])
  * screenshot: `plastic_ox/demo/shots/warp_v1/UndergroundPath_EastEntrance_Frlg_1_issue.png`
* **UndergroundPath_EastEntrance_Frlg[2] ISSUE** — stepping DOWN from (7,7) onto (7,8) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/UndergroundPath_EastEntrance_Frlg_2_nowarp.png`

### `UndergroundPath_EastWestTunnel_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (76, 3) | MB_UP_RIGHT_STAIR_WARP | UndergroundPath_EastEntrance_Frlg | (7, 4) | MB_DOWN_LEFT_STAIR_WARP | (7, 4) | (7, 4) | RIGHT (RIGHT) | yes | same door | **OK** |
| 1 | (3, 4) | MB_UP_LEFT_STAIR_WARP | UndergroundPath_WestEntrance_Frlg | (7, 4) | MB_DOWN_LEFT_STAIR_WARP | (7, 4) | (7, 4) | LEFT (RIGHT) | yes | same door | **OK** |


### `UndergroundPath_NorthEntrance_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_NORMAL | Route5_Frlg | (31, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | Route5_Frlg | (31, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (7, 8) | MB_NORMAL | Route5_Frlg | (31, 31) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (7, 4) | MB_DOWN_LEFT_STAIR_WARP | UndergroundPath_NorthSouthTunnel_Frlg | (4, 3) | MB_UP_RIGHT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **UndergroundPath_NorthEntrance_Frlg[0] UNTESTED** — untestable: UndergroundPath_NorthEntrance_Frlg cannot be loaded by the engine (see load check)
* **UndergroundPath_NorthEntrance_Frlg[1] UNTESTED** — untestable: UndergroundPath_NorthEntrance_Frlg cannot be loaded by the engine (see load check)
* **UndergroundPath_NorthEntrance_Frlg[2] UNTESTED** — untestable: UndergroundPath_NorthEntrance_Frlg cannot be loaded by the engine (see load check)
* **UndergroundPath_NorthEntrance_Frlg[3] UNTESTED** — untestable: UndergroundPath_NorthEntrance_Frlg cannot be loaded by the engine (see load check)

### `UndergroundPath_NorthSouthTunnel_Frlg`

*Tier: donor town/cave (vanilla base) — 2 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 3) | MB_UP_RIGHT_STAIR_WARP | UndergroundPath_NorthEntrance_Frlg | (7, 4) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (3, 60) | MB_UP_LEFT_STAIR_WARP | UndergroundPath_SouthEntrance_Frlg | (7, 4) | MB_DOWN_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **UndergroundPath_NorthSouthTunnel_Frlg[0] UNTESTED** — untestable: UndergroundPath_NorthSouthTunnel_Frlg cannot be loaded by the engine (see load check)
* **UndergroundPath_NorthSouthTunnel_Frlg[1] UNTESTED** — untestable: UndergroundPath_NorthSouthTunnel_Frlg cannot be loaded by the engine (see load check)

### `UndergroundPath_SouthEntrance_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_NORMAL | Route6_Frlg | (19, 13) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | Route6_Frlg | (19, 13) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (7, 8) | MB_NORMAL | Route6_Frlg | (19, 13) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (7, 4) | MB_DOWN_LEFT_STAIR_WARP | UndergroundPath_NorthSouthTunnel_Frlg | (3, 60) | MB_UP_LEFT_STAIR_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **UndergroundPath_SouthEntrance_Frlg[0] UNTESTED** — untestable: UndergroundPath_SouthEntrance_Frlg cannot be loaded by the engine (see load check)
* **UndergroundPath_SouthEntrance_Frlg[1] UNTESTED** — untestable: UndergroundPath_SouthEntrance_Frlg cannot be loaded by the engine (see load check)
* **UndergroundPath_SouthEntrance_Frlg[2] UNTESTED** — untestable: UndergroundPath_SouthEntrance_Frlg cannot be loaded by the engine (see load check)
* **UndergroundPath_SouthEntrance_Frlg[3] UNTESTED** — untestable: UndergroundPath_SouthEntrance_Frlg cannot be loaded by the engine (see load check)

### `UndergroundPath_WestEntrance_Frlg`

*Tier: region trail endpoint — 4 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (5, 8) | MB_NORMAL | UndergroundPath_WestEntrance_Frlg | (5, 8) | MB_NORMAL | - | - | - (-) | - | inconclusive | **ISSUE** |
| 1 | (6, 8) | MB_SOUTH_ARROW_WARP | UndergroundPath_WestEntrance_Frlg | (5, 8) | MB_NORMAL | - | - | - (-) | - | inconclusive | **ISSUE** |
| 2 | (7, 8) | MB_NORMAL | UndergroundPath_WestEntrance_Frlg | (5, 8) | MB_NORMAL | - | - | - (-) | - | inconclusive | **ISSUE** |
| 3 | (7, 4) | MB_DOWN_LEFT_STAIR_WARP | UndergroundPath_EastWestTunnel_Frlg | (3, 4) | MB_UP_LEFT_STAIR_WARP | (3, 4) | (3, 4) | LEFT (RIGHT) | yes | same door | **OK** |

* **UndergroundPath_WestEntrance_Frlg[0] ISSUE** — stepping DOWN from (5,7) onto (5,8) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/UndergroundPath_WestEntrance_Frlg_0_nowarp.png`
* **UndergroundPath_WestEntrance_Frlg[1] ISSUE** — stepping DOWN from (6,7) onto (6,8) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/UndergroundPath_WestEntrance_Frlg_1_nowarp.png`
* **UndergroundPath_WestEntrance_Frlg[2] ISSUE** — stepping DOWN from (7,7) onto (7,8) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/UndergroundPath_WestEntrance_Frlg_2_nowarp.png`

### `UnionRoom`

*Tier: other / unclassified base — 2 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 11) | MB_BRIDGE_OVER_OCEAN | MAP_DYNAMIC | - | - | (7, 11) | (7, 11) | DOWN (DOWN) | yes | same door | **OK** |
| 1 | (8, 11) | MB_NORMAL | MAP_DYNAMIC | - | - | (7, 11) | (7, 11) | DOWN (DOWN) | yes | WRONG MAP/TILE | **ISSUE** |

* **UnionRoom[1] ISSUE** — (note) stepping the facility exit warp at (8,11) did not warp

### `UnionRoom_Frlg`

*Tier: donor town/cave (vanilla base) — 1 warp(s), 0 connection(s), 1 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (7, 11) | MB_BRIDGE_OVER_OCEAN | MAP_DYNAMIC | - | - | - | - | - (-) | - | - | **UNTESTED** |

* **UnionRoom_Frlg[0] UNTESTED** — untestable: UnionRoom_Frlg cannot be loaded by the engine (see load check)

### `VermilionCity_Frlg`

*Tier: donor town/cave (vanilla base) — 10 warp(s), 2 connection(s), 12 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (22, 34) | MB_SOUTH_ARROW_WARP | SSAnne_Exterior_Frlg | (32, 5) | MB_NORTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (23, 34) | MB_SOUTH_ARROW_WARP | SSAnne_Exterior_Frlg | (32, 5) | MB_NORTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (24, 34) | MB_SOUTH_ARROW_WARP | SSAnne_Exterior_Frlg | (32, 5) | MB_NORTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (9, 6) | MB_ANIMATED_DOOR | VermilionCity_House1_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 4 | (15, 6) | MB_ANIMATED_DOOR | VermilionCity_PokemonCenter_1F_Frlg | (7, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 5 | (12, 17) | MB_ANIMATED_DOOR | VermilionCity_PokemonFanClub_Frlg | (5, 10) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 6 | (19, 17) | MB_ANIMATED_DOOR | VermilionCity_House2_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 7 | (29, 17) | MB_ANIMATED_DOOR | VermilionCity_Mart_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 8 | (28, 24) | MB_ANIMATED_DOOR | VermilionCity_House3_Frlg | (4, 7) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |
| 9 | (14, 25) | MB_ANIMATED_DOOR | VermilionCity_Gym_Frlg | (5, 19) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **VermilionCity_Frlg[0] UNTESTED** — untestable: VermilionCity_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Frlg[1] UNTESTED** — untestable: VermilionCity_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Frlg[2] UNTESTED** — untestable: VermilionCity_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Frlg[3] UNTESTED** — untestable: VermilionCity_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Frlg[4] UNTESTED** — untestable: VermilionCity_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Frlg[5] UNTESTED** — untestable: VermilionCity_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Frlg[6] UNTESTED** — untestable: VermilionCity_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Frlg[7] UNTESTED** — untestable: VermilionCity_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Frlg[8] UNTESTED** — untestable: VermilionCity_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Frlg[9] UNTESTED** — untestable: VermilionCity_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Frlg conn[0] up/12 -> Route6_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)
* **VermilionCity_Frlg conn[1] right/10 -> Route11_Frlg UNTESTED** — 
  * untestable: the map (or its partner) cannot be loaded by the engine (see load check)

### `VermilionCity_Gym_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 19) | MB_NORMAL | VermilionCity_Frlg | (14, 25) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 19) | MB_SOUTH_ARROW_WARP | VermilionCity_Frlg | (14, 25) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (6, 19) | MB_NORMAL | VermilionCity_Frlg | (14, 25) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **VermilionCity_Gym_Frlg[0] UNTESTED** — untestable: VermilionCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Gym_Frlg[1] UNTESTED** — untestable: VermilionCity_Gym_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Gym_Frlg[2] UNTESTED** — untestable: VermilionCity_Gym_Frlg cannot be loaded by the engine (see load check)

### `VermilionCity_House1_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | VermilionCity_Frlg | (9, 6) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | VermilionCity_Frlg | (9, 6) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | VermilionCity_Frlg | (9, 6) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **VermilionCity_House1_Frlg[0] UNTESTED** — untestable: VermilionCity_House1_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_House1_Frlg[1] UNTESTED** — untestable: VermilionCity_House1_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_House1_Frlg[2] UNTESTED** — untestable: VermilionCity_House1_Frlg cannot be loaded by the engine (see load check)

### `VermilionCity_House2_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | VermilionCity_Frlg | (19, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | VermilionCity_Frlg | (19, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | VermilionCity_Frlg | (19, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **VermilionCity_House2_Frlg[0] UNTESTED** — untestable: VermilionCity_House2_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_House2_Frlg[1] UNTESTED** — untestable: VermilionCity_House2_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_House2_Frlg[2] UNTESTED** — untestable: VermilionCity_House2_Frlg cannot be loaded by the engine (see load check)

### `VermilionCity_House3_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | VermilionCity_Frlg | (28, 24) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | VermilionCity_Frlg | (28, 24) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | VermilionCity_Frlg | (28, 24) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **VermilionCity_House3_Frlg[0] UNTESTED** — untestable: VermilionCity_House3_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_House3_Frlg[1] UNTESTED** — untestable: VermilionCity_House3_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_House3_Frlg[2] UNTESTED** — untestable: VermilionCity_House3_Frlg cannot be loaded by the engine (see load check)

### `VermilionCity_Mart_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (3, 7) | MB_NORMAL | VermilionCity_Frlg | (29, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (4, 7) | MB_SOUTH_ARROW_WARP | VermilionCity_Frlg | (29, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (5, 7) | MB_NORMAL | VermilionCity_Frlg | (29, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **VermilionCity_Mart_Frlg[0] UNTESTED** — untestable: VermilionCity_Mart_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Mart_Frlg[1] UNTESTED** — untestable: VermilionCity_Mart_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_Mart_Frlg[2] UNTESTED** — untestable: VermilionCity_Mart_Frlg cannot be loaded by the engine (see load check)

### `VermilionCity_PokemonCenter_1F_Frlg`

*Tier: donor town/cave (vanilla base) — 4 warp(s), 0 connection(s), 4 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (6, 8) | MB_NORMAL | VermilionCity_Frlg | (15, 6) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (7, 8) | MB_SOUTH_ARROW_WARP | VermilionCity_Frlg | (15, 6) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (8, 8) | MB_NORMAL | VermilionCity_Frlg | (15, 6) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 3 | (1, 6) | MB_UP_ESCALATOR | VermilionCity_PokemonCenter_2F_Frlg | (1, 6) | MB_DOWN_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |

* **VermilionCity_PokemonCenter_1F_Frlg[0] UNTESTED** — untestable: VermilionCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_PokemonCenter_1F_Frlg[1] UNTESTED** — untestable: VermilionCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_PokemonCenter_1F_Frlg[2] UNTESTED** — untestable: VermilionCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_PokemonCenter_1F_Frlg[3] UNTESTED** — untestable: VermilionCity_PokemonCenter_1F_Frlg cannot be loaded by the engine (see load check)

### `VermilionCity_PokemonCenter_2F_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (1, 6) | MB_DOWN_ESCALATOR | VermilionCity_PokemonCenter_1F_Frlg | (1, 6) | MB_UP_ESCALATOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 1) | MB_ANIMATED_DOOR | UnionRoom_Frlg | (7, 11) | MB_BRIDGE_OVER_OCEAN | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (9, 1) | MB_ANIMATED_DOOR | TradeCenter_Frlg | (5, 8) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | - | **UNTESTED** |

* **VermilionCity_PokemonCenter_2F_Frlg[0] UNTESTED** — untestable: VermilionCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_PokemonCenter_2F_Frlg[1] UNTESTED** — untestable: VermilionCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_PokemonCenter_2F_Frlg[2] UNTESTED** — untestable: VermilionCity_PokemonCenter_2F_Frlg cannot be loaded by the engine (see load check)

### `VermilionCity_PokemonFanClub_Frlg`

*Tier: donor town/cave (vanilla base) — 3 warp(s), 0 connection(s), 3 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (4, 10) | MB_NORMAL | VermilionCity_Frlg | (12, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 1 | (5, 10) | MB_SOUTH_ARROW_WARP | VermilionCity_Frlg | (12, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |
| 2 | (6, 10) | MB_NORMAL | VermilionCity_Frlg | (12, 17) | MB_ANIMATED_DOOR | - | - | - (-) | - | - | **UNTESTED** |

* **VermilionCity_PokemonFanClub_Frlg[0] UNTESTED** — untestable: VermilionCity_PokemonFanClub_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_PokemonFanClub_Frlg[1] UNTESTED** — untestable: VermilionCity_PokemonFanClub_Frlg cannot be loaded by the engine (see load check)
* **VermilionCity_PokemonFanClub_Frlg[2] UNTESTED** — untestable: VermilionCity_PokemonFanClub_Frlg cannot be loaded by the engine (see load check)

### `VictoryRoad_1F`

*Tier: region trail endpoint — 5 warp(s), 0 connection(s), 2 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (15, 40) | MB_SOUTH_ARROW_WARP | VictoryRoad_1F | (15, 40) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 1 | (39, 5) | MB_SOUTH_ARROW_WARP | VictoryRoad_1F | (39, 5) | MB_SOUTH_ARROW_WARP | - | - | - (-) | - | inconclusive | **ISSUE** |
| 2 | (21, 32) | MB_LADDER | VictoryRoad_B1F | (20, 21) | MB_LADDER | (20, 21) | (20, 21) | DOWN (KEEP) | yes | same door | **OK** |
| 3 | (42, 38) | MB_LADDER | VictoryRoad_B1F | (42, 25) | MB_LADDER | (42, 25) | (42, 25) | UP (KEEP) | yes | same door | **OK** |
| 4 | (9, 14) | MB_LADDER | VictoryRoad_B1F | (8, 3) | MB_LADDER | (8, 3) | (8, 3) | UP (KEEP) | yes | same door | **OK** |

* **VictoryRoad_1F[0] ISSUE** — stepping DOWN from (15,39) onto (15,40) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/VictoryRoad_1F_0_nowarp.png`
* **VictoryRoad_1F[1] ISSUE** — stepping DOWN from (39,4) onto (39,5) did not warp (timeout)
  * screenshot: `plastic_ox/demo/shots/warp_v1/VictoryRoad_1F_1_nowarp.png`

### `VictoryRoad_B1F`

*Tier: other / unclassified base — 7 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (30, 25) | MB_LADDER | VictoryRoad_B2F | (30, 25) | MB_LADDER | (30, 25) | (30, 25) | UP (KEEP) | yes | same door | **OK** |
| 1 | (17, 16) | MB_LADDER | VictoryRoad_B2F | (19, 12) | MB_LADDER | (19, 12) | (19, 12) | UP (KEEP) | yes | same door | **OK** |
| 2 | (42, 25) | MB_LADDER | VictoryRoad_1F | (42, 38) | MB_LADDER | (42, 38) | (42, 38) | UP (KEEP) | yes | same door | **OK** |
| 3 | (42, 2) | MB_LADDER | VictoryRoad_B2F | (43, 2) | MB_LADDER | (43, 2) | (43, 2) | UP (KEEP) | yes | same door | **OK** |
| 4 | (8, 3) | MB_LADDER | VictoryRoad_1F | (9, 14) | MB_LADDER | (9, 14) | (9, 14) | UP (KEEP) | yes | same door | **OK** |
| 5 | (20, 21) | MB_LADDER | VictoryRoad_1F | (21, 32) | MB_LADDER | (21, 32) | (21, 32) | LEFT (KEEP) | yes | same door | **OK** |
| 6 | (5, 26) | MB_LADDER | VictoryRoad_B2F | (5, 26) | MB_LADDER | (5, 26) | (5, 26) | UP (KEEP) | yes | same door | **OK** |


### `VictoryRoad_B2F`

*Tier: other / unclassified base — 4 warp(s), 0 connection(s), 0 finding(s).*

| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (30, 25) | MB_LADDER | VictoryRoad_B1F | (30, 25) | MB_LADDER | (30, 25) | (30, 25) | UP (KEEP) | yes | same door | **OK** |
| 1 | (43, 2) | MB_LADDER | VictoryRoad_B1F | (42, 2) | MB_LADDER | (42, 2) | (42, 2) | UP (KEEP) | yes | same door | **OK** |
| 2 | (19, 12) | MB_LADDER | VictoryRoad_B1F | (17, 16) | MB_LADDER | (17, 16) | (17, 16) | UP (KEEP) | yes | same door | **OK** |
| 3 | (5, 26) | MB_LADDER | VictoryRoad_B1F | (5, 26) | MB_LADDER | (5, 26) | (5, 26) | LEFT (KEEP) | yes | same door | **OK** |


## 4. Untested / not covered

**898 of 1364 records are UNTESTED.** Grouped by the reason:

| reason | records | distinct maps |
|---|---|---|
| the map, or the map it warps into, **cannot be loaded by the engine at all** (see the load check in 2b). The warp data may well be fine; it is simply unreachable because the destination dies during `DoMapLoad` | 816 | 209 |
| facility state machine excluded with `--exclude` (Battle Frontier lobbies/rooms: they need a registered Battle Frontier trainer battle before the exit warp is reachable, which a generic warp walk cannot set up) | 81 | 30 |
| MAP_DYNAMIC exit with no reachable door in the closure | 1 | 1 |

**(A) — 81 records across 30 maps, listed untested in section 3.**

**(B) — 816 records across 209 maps, listed untested in section 3.**

**(C) — 1 records across 1 maps, listed untested in section 3.**

No warp in the closure was skipped for convenience: every record is either walked and asserted, or carries one of the two reasons above.

Partial coverage, stated explicitly:

* Facility exit warps whose `dest_map` is `MAP_DYNAMIC` are only meaningful when the player walked in through a real door (the engine fills `gSaveBlock1Ptr->dynamicWarp` from the entrance). Each one was driven from a real entrance recorded in the JSON (`entrance` field); a facility with no door in the closure is reported untestable rather than as a defect.
* `PARTIAL` rows are warps whose *outbound* leg fully passed but whose return leg could not be triggered from any of the four cardinal sides of the return warp inside the harness placement limits. They are listed individually in section 3 and are **not** counted as passes.
* Screenshots are captured only for ISSUE rows, in `plastic_ox/demo/shots/warp_v1/`.
* The emulator state is injected (warp-injection + flag setting); no player save file is written and the ROM is not modified.
* The harness can only test a transition that a player could perform. It injects the player onto a run-up tile and then holds a real direction key, so everything from the run-up onwards is the real engine: `TryDoorWarp`, `TryArrowWarp`, ladder and ledge handling, `DoWarp`, `DoMapLoad`, camera connections.

## 5. Systemic findings

| category | count |
|---|---|
| warp does not fire from a legal approach | 52 |
| other | 6 |
| lands in solid terrain | 4 |
| wrong landing coordinates | 2 |
| softlock: no exit from landing | 2 |


### The 52 "warp does not fire" rows, triaged

These are the rows where the harness stood the player on a standable tile next to the warp, held the key onto the warp tile, and the engine did not transition. They are **not** all confirmed defects - the split below is what a human should triage first.

| source metatile behaviour | rows | what it means |
|---|---|---|
| `MB_NORMAL` | 21 | the warp event sits on plain (often solid) terrain, so the player can never legally stand on it - check elevation and collision of the tile itself. |
| `MB_MOSSDEEP_GYM_WARP` | 12 | custom gym behaviour; the engine reaches it through a warp-event script, not a tile callback. Needs a manual look. |
| `MB_CAVE` | 6 | cave-mouth warp, same class as the arrow warps. |
| `MB_SOUTH_ARROW_WARP` | 4 | stair/arrow warp that should fire when stepped on along the arrow - if it does not, the arrow tile is not the tile the engine reads, or the elevation gate rejects the step. |
| `MB_NON_ANIMATED_DOOR` | 2 | ordinary door/threshold warp - the strongest evidence of a real defect |
| `MB_MOUNTAIN_TOP` | 2 | ordinary door/threshold warp - the strongest evidence of a real defect |
| `MB_SOUTHWARD_CURRENT` | 2 | ordinary door/threshold warp - the strongest evidence of a real defect |
| `MB_NORTHWARD_CURRENT` | 2 | ordinary door/threshold warp - the strongest evidence of a real defect |
| `MB_TRICK_HOUSE_PUZZLE_DOOR` | 1 | ordinary door/threshold warp - the strongest evidence of a real defect |

| map | warp | tile | source behaviour |
|---|---|---|---|
| `MeteorFalls_1F_1R` | 0 | (27, 18) | `MB_SOUTH_ARROW_WARP` |
| `MeteorFalls_1F_1R` | 5 | (4, 2) | `MB_NORMAL` |
| `MossdeepCity_GameCorner_1F` | 2 | (2, 0) | `MB_NORMAL` |
| `MossdeepCity_Gym` | 2 | (3, 28) | `MB_MOSSDEEP_GYM_WARP` |
| `MossdeepCity_Gym` | 3 | (1, 23) | `MB_MOSSDEEP_GYM_WARP` |
| `MossdeepCity_Gym` | 4 | (7, 18) | `MB_MOSSDEEP_GYM_WARP` |
| `MossdeepCity_Gym` | 5 | (8, 12) | `MB_MOSSDEEP_GYM_WARP` |
| `MossdeepCity_Gym` | 6 | (9, 18) | `MB_MOSSDEEP_GYM_WARP` |
| `MossdeepCity_Gym` | 7 | (23, 20) | `MB_MOSSDEEP_GYM_WARP` |
| `MossdeepCity_Gym` | 8 | (1, 33) | `MB_MOSSDEEP_GYM_WARP` |
| `MossdeepCity_Gym` | 9 | (20, 24) | `MB_MOSSDEEP_GYM_WARP` |
| `MossdeepCity_Gym` | 10 | (11, 3) | `MB_MOSSDEEP_GYM_WARP` |
| `MossdeepCity_Gym` | 11 | (11, 35) | `MB_MOSSDEEP_GYM_WARP` |
| `MossdeepCity_Gym` | 12 | (13, 32) | `MB_MOSSDEEP_GYM_WARP` |
| `MossdeepCity_Gym` | 13 | (21, 10) | `MB_MOSSDEEP_GYM_WARP` |
| `NewMauville_Entrance` | 1 | (4, 1) | `MB_NON_ANIMATED_DOOR` |
| `PalletTown_PlayersHouse_1F_Frlg` | 0 | (5, 8) | `MB_NORMAL` |
| `PalletTown_PlayersHouse_1F_Frlg` | 3 | (3, 9) | `MB_NORMAL` |
| `PalletTown_RivalsHouse_Frlg` | 1 | (5, 8) | `MB_NORMAL` |
| `PalletTown_RivalsHouse_Frlg` | 2 | (3, 8) | `MB_NORMAL` |
| `PokemonMansion_1F_Frlg` | 0 | (7, 33) | `MB_CAVE` |
| `PokemonMansion_1F_Frlg` | 2 | (9, 33) | `MB_CAVE` |
| `PokemonMansion_1F_Frlg` | 6 | (35, 34) | `MB_NORMAL` |
| `Route110_TrickHouseCorridor` | 0 | (13, 3) | `MB_NORMAL` |
| `Route110_TrickHouseCorridor` | 1 | (14, 3) | `MB_NORMAL` |
| `Route110_TrickHouseEnd` | 0 | (10, 1) | `MB_NON_ANIMATED_DOOR` |
| `Route110_TrickHouseEntrance` | 2 | (5, 2) | `MB_NORMAL` |
| `Route110_TrickHousePuzzle1` | 2 | (13, 1) | `MB_TRICK_HOUSE_PUZZLE_DOOR` |
| `Route115` | 1 | (21, 6) | `MB_MOUNTAIN_TOP` |
| `Route115` | 2 | (36, 10) | `MB_MOUNTAIN_TOP` |
| `Route2_EastBuilding_Frlg` | 0 | (6, 9) | `MB_NORMAL` |
| `Route2_EastBuilding_Frlg` | 2 | (8, 9) | `MB_NORMAL` |
| `Route2_ViridianForest_NorthEntrance_Frlg` | 0 | (6, 9) | `MB_NORMAL` |
| `Route2_ViridianForest_NorthEntrance_Frlg` | 2 | (8, 9) | `MB_NORMAL` |
| `Route2_ViridianForest_SouthEntrance_Frlg` | 0 | (6, 9) | `MB_NORMAL` |
| `Route2_ViridianForest_SouthEntrance_Frlg` | 2 | (8, 9) | `MB_NORMAL` |
| `Route8_Frlg` | 0 | (12, 17) | `MB_NORMAL` |
| `SeafoamIslands_B1F_Frlg` | 9 | (21, 8) | `MB_CAVE` |
| `SeafoamIslands_B1F_Frlg` | 10 | (29, 8) | `MB_CAVE` |
| `SeafoamIslands_B2F_Frlg` | 7 | (22, 7) | `MB_CAVE` |
| `SeafoamIslands_B2F_Frlg` | 8 | (29, 8) | `MB_CAVE` |
| `SeafoamIslands_B3F_Frlg` | 5 | (23, 9) | `MB_SOUTHWARD_CURRENT` |
| `SeafoamIslands_B3F_Frlg` | 6 | (24, 9) | `MB_SOUTHWARD_CURRENT` |
| `SeafoamIslands_B4F_Frlg` | 2 | (8, 17) | `MB_NORTHWARD_CURRENT` |
| `SeafoamIslands_B4F_Frlg` | 3 | (9, 17) | `MB_NORTHWARD_CURRENT` |
| `UndergroundPath_EastEntrance_Frlg` | 0 | (5, 8) | `MB_NORMAL` |
| `UndergroundPath_EastEntrance_Frlg` | 2 | (7, 8) | `MB_NORMAL` |
| `UndergroundPath_WestEntrance_Frlg` | 0 | (5, 8) | `MB_NORMAL` |
| `UndergroundPath_WestEntrance_Frlg` | 1 | (6, 8) | `MB_SOUTH_ARROW_WARP` |
| `UndergroundPath_WestEntrance_Frlg` | 2 | (7, 8) | `MB_NORMAL` |
| `VictoryRoad_1F` | 0 | (15, 40) | `MB_SOUTH_ARROW_WARP` |
| `VictoryRoad_1F` | 1 | (39, 5) | `MB_SOUTH_ARROW_WARP` |
| seam findings by direction | count |
|---|---|
| seam: down connection | 17 |
| seam: left connection | 17 |
| seam: right connection | 17 |
| seam: up connection | 14 |

## 6. Prioritized fix list

1. **P0 — the imported FRLG Kanto base does not load.** 204 maps (52%) die inside `DoMapLoad`: `gMapHeader.mapLayout` comes back as a non-ROM value, every block reads `MAPGRID_UNDEFINED`, the screen goes black or the player is frozen, and no further map change is accepted. Families: Route (39), SSAnne_ (16), SilphCo_ (11), PokemonTower_ (7), SSAnne_B (6), CeladonCity_DepartmentStore_ (5), CeruleanCity_House (5), RocketHideout_B (4), CeladonCity_Condominiums_ (3), FuchsiaCity_House (3). This blocks every warp into or out of those maps and has to be fixed before the rest of the Kanto graph can be playtested; see section 2b for the full list.
2. **P0 — data errors that make the engine read past the end of a warp table.** 2 warp(s) reference a `dest_warp_id` the destination map does not have: `Route8_WestEntrance_Frlg[2]`, `Route8_WestEntrance_Frlg[3]`. `SetPlayerCoordsFromWarp()` dereferences `mapHeader->events->warps[warpId]` unconditionally, so these land the player on whatever warp struct follows the table.
3. **P0 — landings inside solid terrain.** `MeteorFalls_StevensCave[0]`, `MossdeepCity_GameCorner_B1F[0]`, `NewMauville_Inside[0]`, `UndergroundPath_EastEntrance_Frlg[1]`.
4. **P0 — softlocks.** `MossdeepCity_GameCorner_B1F[0]`, `SeafoamIslands_B2F_Frlg[9]`, `SeafoamIslands_B2F_Frlg[10]`, `UndergroundPath_EastEntrance_Frlg[1]`. A landing with no walkable neighbour cannot be escaped.
5. **P1 — non-reciprocal warp pairs (exit does not return you to the door you came in by).** `DiglettsCave_NorthEntrance_Frlg[1]`, `LavenderTown_hns[0]`, `LavenderTown_hns[1]`, `LavenderTown_hns[2]`, `LavenderTown_hns[3]`, `Route110_TrickHouseCorridor[2]`, `Route110_TrickHouseCorridor[3]`, `Route2_Frlg[4]`, `Route4_Frlg[0]`, `Route4_Frlg[1]`, `Route7_Frlg[0]`, `SeafoamIslands_B3F_Frlg[5]` ….
6. **P1 — runtime landing mismatches.** `Route2_House_Frlg[0]`, `Route44_hns[0]`.
7. **P1 — map-connection seams.** `EcruteakCity_hns` conn[0] down/-16 -> Route37_hns: down seam: walking DOWN off the EcruteakCity_hns edge did not change map on any of 2 lanes tried: lane 18: held DOWN from (18,58) and stayed on EcruteakCity_hns at (18,59); lane 19: held DOWN from (19,58) and stayed on E; `Route21_North_Frlg` conn[0] down/0 -> Route21_South_Frlg: down seam: walking DOWN off the Route21_North_Frlg edge did not change map on any of 0 lanes tried: ; `Route21_South_Frlg` conn[0] up/0 -> Route21_North_Frlg: up seam: walking UP off the Route21_South_Frlg edge did not change map on any of 0 lanes tried: ; `Route37_hns` conn[0] down/-22 -> Route36_hns: Route37_hns down seam: player cannot continue DOWN past the handover tile (43,0) in Route36_hns; `Route37_hns` conn[1] up/16 -> EcruteakCity_hns: up seam: walking UP off the Route37_hns edge did not change map on any of 0 lanes tried: 
8. **P2 — warps that cannot be triggered on foot.** `LavenderTown_PokemonCenter_2F_Frlg[1]`, `LavenderTown_PokemonCenter_2F_Frlg[2]`, `MossdeepCity_GameCorner_1F[2]`, `Route8_Frlg[0]`, `SSAnne_1F_Corridor_Frlg[3]`, `SSAnne_1F_Corridor_Frlg[4]`, `SSAnne_Exterior_Frlg[3]`, `SeafoamIslands_B3F_Frlg[5]`, `SeafoamIslands_B3F_Frlg[6]`, `SeafoamIslands_B4F_Frlg[2]`, `SeafoamIslands_B4F_Frlg[3]`.
9. **P3 — needs a manual look (inconclusive return leg).** `Route110_TrickHouseEnd[1]`, `Route110_TrickHousePuzzle1[0]`, `Route110_TrickHousePuzzle1[1]`, `SeafoamIslands_1F_Frlg[5]`, `SeafoamIslands_B1F_Frlg[7]`.
10. **P3 — remaining issues.** `MeteorFalls_1F_1R[0]`, `MeteorFalls_1F_1R[5]`, `MossdeepCity_GameCorner_1F[2]`, `MossdeepCity_Gym[2]`, `MossdeepCity_Gym[3]`, `MossdeepCity_Gym[4]`, `MossdeepCity_Gym[5]`, `MossdeepCity_Gym[6]`, `MossdeepCity_Gym[7]`, `MossdeepCity_Gym[8]`, `MossdeepCity_Gym[9]`, `MossdeepCity_Gym[10]` ….

## 7. Raw counts

```
maps in closure              : 417
warp events                  : 1278
map connections              : 86
static warp findings         : 51
static connection findings   : 8
dynamic warp  OK/PARTIAL/ISSUE/ERROR/UNTESTED : 369/5/66/0/838
dynamic seam  OK/PARTIAL/ISSUE/ERROR/UNTESTED : 21/0/5/0/60
emulator reboots             : 19
```

---

# Fix pass (run 5)

ROM after the fix pass: `pokeemerald.gba`, 33 554 432 bytes (ROM segment
27 569 892 B, 82.16 % of 32 MB), built with
`DEVKITARM=~/devkitpro/opt/devkitpro/devkitARM make -j8`, zero errors.

## R5.0 Headline

| | run 3 (before) | run 5 (after) |
|---|---|---|
| ISSUE rows | **71** | **27** |
| PARTIAL rows | 5 | 8 |
| OK rows | 390 | **431** |
| maps the engine cannot load | 204 / 391 | 204 / 391 (unchanged) |

Every remaining ISSUE/PARTIAL row is listed in **R5.5 Blocked** with the reason
it could not be closed with a data-level fix. Nothing is claimed here as fixed
that was not re-walked in mGBA.

Reproduce:

```sh
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  ~/.venvs/mgba311/bin/python plastic_ox/demo/test_warps_v1.py --load-only \
  --json plastic_ox/agent/warp_playtest_v1_run5_loadcheck.json
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  ~/.venvs/mgba311/bin/python plastic_ox/demo/test_warps_v1.py \
  --load-report plastic_ox/agent/warp_playtest_v1_run5_loadcheck.json \
  --exclude BattleFrontier --json plastic_ox/agent/warp_playtest_v1_run5.json
```

Raw logs: `plastic_ox/agent/warp_playtest_v1_run5.log` (7 min 19 s, 25 reboots)
and `plastic_ox/agent/warp_playtest_v1_run5_loadcheck.log`.

## R5.1 Harness corrections first (16 of the 71 ISSUE rows were harness artefacts)

Run 3's harness decided a warp had fired only when the **map id** changed:

```python
if (st["group"], st["num"]) != (start["group"], start["num"]):
```

Several perfectly ordinary warps stay on the map they started on - Mossdeep
City Gym's six switch-tile pairs, Victory Road 1F's two end warps, Route 115's
two summit warps, Route 44's cave link. All twelve `MossdeepCity_Gym[2..13]`
rows, `VictoryRoad_1F[0]`, `VictoryRoad_1F[1]` and `Route115[1]`, `Route115[2]`
were therefore reported "did not warp (timeout)" although the engine warps
correctly. Every map load in pokeemerald, including a same-map one, runs through
one of `gMain`'s transient callbacks (`CB2_LoadMap2` / `CB2_ReturnToField...`),
so the harness now watches `gMain.callback` as well
(`WarpPlaytestMixin.callback()`), which is what actually distinguishes "the
player walked one tile" from "the engine swapped the map under the player's
feet". `step_into()` also takes an `expect_xy` for the declared landing.

`_try_seam()`'s lane sweep was raised from 10 to 32 lanes: it walks outward from
the middle of a connection's lane range, and Ecruteak City's usable seam lanes
are at the far end of theirs.

Re-test: `--only MossdeepCity_Gym --only VictoryRoad_1F` on the fresh ROM -
`MossdeepCity_Gym` 14/14 OK (was 2 OK / 12 ISSUE), `VictoryRoad_1F` 6/6 OK.

## R5.2 Fixed: authored-layer seams (ECRUTEAK CITY - ROUTE 37 - ROUTE 36)

These are the story spine, and all three connections were broken. Walking them
out revealed that the offsets were not the only fault: `ROUTE 37`'s road is cut
into three pieces, and both of its gates are wider than the roads they meet.

### What was wrong

| seam | run 3 | cause |
|---|---|---|
| `EcruteakCity_hns` down -> `Route37_hns` | "did not change map on any of 2 lanes tried" | city's south gate is 2 tiles (x=0,1 on the last row), route's north gate is 4 (x=16..19); 2 of the 4 lanes handed over into rock |
| `Route37_hns` up -> `EcruteakCity_hns` | "0 lanes tried" | same, seen from the route side |
| `Route37_hns` down -> `Route36_hns` | handover OK, then "blocked at (43,0)" | route's south exit is 14 lanes, ROUTE 36's north gate is 9, and 4 of ROUTE 36's 9 gate columns are solid on the next row |
| (not reported) | - | `ROUTE 37` rows 5 and 9 repeat the road metatiles with the collision and elevation bits overwritten, severing the route into three pieces; arriving from ECRUTEAK CITY put the player in a 5-row dead end |

### Fixes

* `data/maps/EcruteakCity_hns/map.json`, `data/maps/Route37_hns/map.json`,
  `data/maps/Route36_hns/map.json` - `Route37_hns` conn[0] offset `-22` -> `-20`,
  `Route36_hns` conn[0] `22` -> `20`, so ROUTE 37's x=13..17 exit lands exactly
  on ROUTE 36's x=33..37 gate.
* `data/layouts/EcruteakCity_hns/map.bin` - widened the city's south exit from
  x=0,1 to x=0..3 at rows 59 and 60 (blocks copied from the x=0/1 lanes) so all
  four of ROUTE 37's gate lanes are usable, and closed the unreachable two-tile
  pocket at (18,59)/(19,59), which sits at elevation 4 inside solid rock and
  acted as a phantom seam lane.
* `data/layouts/Route37_hns/map.bin` - rows 5 and 9 at x=16..19 take the blocks
  from rows 6 and 8 (same road metatiles, intact collision/elevation), which
  reconnects the route; the south exit was narrowed to x=13..17 at rows 39 and
  40.
* `data/layouts/Route36_hns/map.bin` - closed (38,0)..(41,0), the four gate
  columns whose next row is rock.
* All of the above is applied by `plastic_ox/agent/fix_warp_metatiles.py`'s
  `PATCH` table, so it is reproducible and idempotent.

### Dynamic re-test

```
$ ... test_warps_v1.py --connections-only --only Route36 --only Route37 --only Ecruteak
dynamic: {'OK': 7, 'ISSUE': 0} elapsed=2.7s reboots=0
```

All four connections pass in both directions, including the
`outward_continue` leg that walks on past the handover tile. Before the fix the
same command reported 4 OK / 3 ISSUE.

## R5.3 Fixed: Route 44 <-> Mt. Moon landing mismatch

`Route44_hns[0]` declared `MAP_MT_MOON_1F` warp 3 at (18,37), but the coordinate
event at (68,13) shadowed the warp event and ran
`PoxMoon_EnterFromRoute44`, which landed on (18,36) - one tile short of the door
that takes you back out.

* `data/maps/Route44_hns/scripts.inc` - `PoxMoon_EnterFromRoute44` now warps to
  `MAP_MT_MOON_1F, 18, 37`.

Checked in-emulator that this does not create a re-entry loop: warping to Mt.
Moon (18,37) and holding DOWN hands the player over to ROUTE 44 at (68,13) and
they walk on to (68,18); the coordinate event does not re-fire.

Re-test: `test_warps_v1.py --only Route44_hns` -> `dynamic: {'OK': 1}`.

## R5.4 Fixed: warps that can never fire (warp event on a non-warp metatile)

The single largest family. A warp event only fires if the metatile under it has
a behaviour the engine's warp triggers accept (`IsArrowWarpMetatileBehavior`,
`IsDirectionalStairWarpMetatileBehavior` in `TryArrowWarp`, or
`IsWarpMetatileBehavior` in `TryStartWarpEventScript`,
`src/field_control_avatar.c`). Almost every one of these was a door whose middle
lane worked and whose flanking lanes were plain floor, `MB_CAVE` or rock, so the
lanes silently did nothing.

`plastic_ox/agent/fix_warp_metatiles.py` clones the *working* lane's metatile
into the map's own secondary tileset, rewrites only the behaviour field of the
clone's attribute entry and repoints the blockmap entry - so artwork, collision
and elevation are identical to the lane that already worked and no shared
metatile is modified. A first pass also turned out to need the offending tiles
opened (they were solid rock in the import) before they could carry a
behaviour; those are the `CARVE` entries.

| map / warp | tile behaviour before | fix |
|---|---|---|
| `Route2_ViridianForest_NorthEntrance_Frlg[0]`,`[2]` | `MB_NORMAL` | clone of the working (7,9) lane, `MB_SOUTH_ARROW_WARP` |
| `Route2_ViridianForest_SouthEntrance_Frlg[0]`,`[2]` | `MB_NORMAL` | same |
| `Route2_EastBuilding_Frlg[0]`,`[2]` | `MB_NORMAL` | same |
| `Route2_House_Frlg[0]` | `MB_HOLDS_LARGE_DECORATION` | clone of the house door (4,8), `MB_SOUTH_ARROW_WARP` |
| `PalletTown_PlayersHouse_1F_Frlg[0]`,`[3]` | `MB_NORMAL` / warp sat on the solid (3,9) | clone of (4,8); warp[3] moved (3,9) -> (3,8) so the house has three working exit lanes |
| `PalletTown_RivalsHouse_Frlg[1]`,`[2]` | `MB_NORMAL` | clone of (4,8) |
| `UndergroundPath_EastEntrance_Frlg[0]`,`[2]` | `MB_NORMAL` | clone of (6,8) |
| `PokemonMansion_1F_Frlg[0]`,`[2]` | `MB_CAVE` | clone of (8,33) |
| `Route8_Frlg[0]` | `MB_NORMAL` on solid rock, the whole approach walled off | carved (12,14),(12,15),(12,16),(12,18) from the road lane (12,20) and made (12,17) an `MB_SOUTH_ARROW_WARP` with that lane's collision |
| `MeteorFalls_1F_1R[5]` | `MB_NORMAL` on solid rock | carved (4,2) from the cave floor (4,3) and made it `MB_NORTH_ARROW_WARP`; this also unblocks `MeteorFalls_StevensCave[0]`, whose landing (4,2) was a wall the player was wedged on |
| `UnionRoom[1]` | `MB_NORMAL` (only the left bridge tile had `MB_BRIDGE_OVER_OCEAN`, which `MetatileBehavior_IsUnionRoomWarp` keys the spin exit off) | clone of (7,11) |

### Dynamic re-test

```
--only Route2_ViridianForest --only Route2_EastBuilding --only Route2_House \
--only PalletTown_PlayersHouse --only PalletTown_RivalsHouse   ->  {'OK': 22}
--only UndergroundPath_EastEntrance_Frlg                       ->  {'OK': 4}
--only MeteorFalls_1F_1R                                       ->  {'OK': 6}
--only MeteorFalls_StevensCave                                 ->  {'OK': 1}
--only Route8_Frlg                                             ->  {'OK': 1}
--only MossdeepCity_GameCorner                                 ->  {'OK': 4}
--only Route44_hns                                             ->  {'OK': 1}
```

Every one of those was a row in run 3's ISSUE list (16 warp rows) and is now OK.

### Mossdeep City Game Corner B1F (wedge)

`MossdeepCity_GameCorner_1F[2]` sat on (2,0), a wall, and the B1F door it pairs
with opens onto rock on both sides.

* `data/maps/MossdeepCity_GameCorner_1F/map.json` - warp[2] (2,0) -> (5,1), the
  room's own `MB_NON_ANIMATED_DOOR`.
* `data/layouts/MossdeepCity_GameCorner_1F_Frlg/map.bin` - (2,1) and (4,1) on
  B1F opened up from the walkable lane at (1,1), so the player can step off the
  door they arrive on.

Re-test: `--only MossdeepCity_GameCorner` -> `{'OK': 4}` (both directions of
both floors).

## R5.5 Blocked

**Route21_North_Frlg <-> Route21_South_Frlg seam (2 rows, `0 lanes tried`).**
Not a game defect - a harness limitation. Every column on both maps is
`MB_OCEAN_WATER`, and `_try_seam` skips waterish lanes because an avatar
injected into open ocean cannot walk. Verified in-emulator by putting the avatar
on the surfboard (`PLAYER_AVATAR_FLAG_SURFING`, byte 0 of `struct
PlayerAvatar`) and walking the seam for real:
`plastic_ox/demo/test_ocean_seams.py` -> `PASS Route21_North_Frlg DOWN ->
Route21_South_Frlg at (11, 0)`, `PASS Route21_South_Frlg UP -> Route21_North_Frlg
at (11, 49)`. No game-data change was made; the harness was extended instead.

**Seafoam Islands (12 ISSUE + 2 PARTIAL rows).** These are FRLG's undersea cave
floors. The transitions run through water: the landing tiles are
`MB_OCEAN_WATER` / `MB_SOUTHWARD_CURRENT`, so the player drifts ("slid 11
tiles"), and the way back needs SURF, which this harness does not drive
("no standable approach", "INCONCLUSIVE return"). One real data fault was found
and fixed inside this family - `SeafoamIslands_B3F_Frlg[5]` and `[6]` pointed at
`SeafoamIslands_B2F_Frlg` warps 7 and 8, which lead on to B1F, so the pairs were
not reciprocal at all (`data/maps/SeafoamIslands_B3F_Frlg/map.json`: dest warp
`7` -> `9`, `8` -> `10`). The rest needs a surfing/diving harness to assert, not
a map edit.

**Route110 Trick House (5 ISSUE + 3 PARTIAL rows).** The declared warp
coordinates sit in open floor, not on doors: `Route110_TrickHouseCorridor[0]/[1]`
at (13,3)/(14,3) and `Route110_TrickHouseEntrance[2]` at (5,2) are all
`MB_NORMAL` mid-corridor, and `Route110_TrickHousePuzzle1[2]` is the puzzle door
(`MB_TRICK_HOUSE_PUZZLE_DOOR`), which is deliberately locked until the puzzle is
solved. Deciding where a door belongs inside the puzzle rooms is a map-design
call. Note also that `LAYOUT_ROUTE110_TRICK_HOUSE_CORRIDOR`'s secondary tileset
(`generic_building`) is full at 512/512 metatiles, so a behaviour-variant
metatile cannot simply be added to it.

**UndergroundPath_WestEntrance_Frlg[0],[1],[2] (3 PARTIAL rows).** These three
warps point at their own map (`dest_warp_id` 0 = themselves); in FRLG they are
the mouth of the west Underground Path onto ROUTE 12. `Route12_Frlg` declares no
warp back to `UndergroundPath_WestEntrance` and has no Underground Path entrance
tile anywhere on its 24x120 grid (its only warp behaviours are one
`MB_SOUTH_ARROW_WARP` at (14,15) feeding the North Entrance and one
`MB_NON_ANIMATED_DOOR` at (14,21)). The reciprocal side of this link is simply
not in the imported closure, so the destination cannot be chosen without
inventing it. Note the consequence of the shared layout
(`LAYOUT_UNDERGROUND_PATH_ENTRANCE` is used by both entrances): the R5.4 repair
made these lanes real arrow warps, so they now fade and return the player to the
same tile instead of doing nothing. Previously they were inert; the correct fix
is a ROUTE 12 entrance.

**Route115[1],[2] (2 rows).** Degenerate self-warps placed on solid
`MB_MOUNTAIN_TOP` tiles at the summit ((21,6) and (36,10) are collision 1; the
tiles below them at (21,7)/(36,11) are the walkable approach). The summit gate
is walled off in this region and nothing in the closure declares where those two
warps should lead, so any destination would be a guess. Left as-is and reported
rather than deleted.

**PokemonMansion_1F_Frlg[5],[6] (2 rows, reduced from 3).** The forward leg is
fixed (both now fire; `[6]` used to be a warp event on the solid tile (35,34) and
was moved to (35,33), and (33,33) joined the exit as a third lane). What remains
is the return: `CinnabarIsland_Frlg` has a single door, warp 0 at (8,3), and it
maps back to `PokemonMansion_1F` warp 1 at (8,33), so leaving from (34,33) or
(35,33) brings the player back at the other end of the building. Giving the
Mansion's side exit its own door in Cinnabar is a map-design call.

**NewMauville_Entrance[1] / NewMauville_Inside[0] (2 rows).** The blockmap
declares (4,1) as metatile 716 with `MB_NON_ANIMATED_DOOR` and collision 0, but
the engine resolves that live tile to `MB_NORMAL` with collision set - verified
directly against the ROM in mGBA, not just from map data. The door tile's
behaviour cannot be corrected from the map files alone, and the New Mauville
Battle Factory entrance is donor Hoenn content outside the story closure.

## R5.6 New tooling

* `plastic_ox/agent/fix_pass5_static.py` - reads live metatile behaviour and
  collision straight out of `data/layouts/*/map.bin` and
  `data/tilesets/*/*/metatile_attributes.bin` and prints, per warp, whether the
  engine's warp triggers can ever fire there, whether the elevation matches, and
  whether the pair is reciprocal. This is what turned "12 different-looking
  failures" into "one root cause", and it honours `layout_version` when resolving
  a tileset directory (`gTileset_LavenderTown_Hns` and
  `gTileset_LavenderTown_Frlg` are different art).
* `plastic_ox/agent/fix_warp_metatiles.py` - the `PATCH`/`CARVE`/`REPAIRS` repair
  tables described above. Idempotent; re-running prints `0 block(s) repointed`.
* `plastic_ox/demo/test_ocean_seams.py` - drives the all-ocean seams with the
  avatar on the surfboard.

---

# Run 6 — Kanto load blocker removed (2026-10-02)

This section supersedes the map-load verdict in section 2b and the run 5
headline. Source changes are in the working tree on `07fa6a3a36`. The final
Emerald ROM was built with:

```sh
make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
```

Its SHA-256 is
`21cfd4a224d40e129c7ed5a3eef14a1d93f15ec47eff4118d2d9633da05eb9b5`
(ROM segment 28,301,300 bytes, 84.34% of 32 MiB).

## R6.1 Map-load result

| Check | Run 5 | Run 6 |
|---|---:|---:|
| Kanto maps in the closure with a usable live grid | 0 / 203 | **203 / 203** |
| Entries in each run's load check with a usable live grid or intentional redirect | 187 / 391 | **417 / 417** |
| Direct loads in each check | 187 | **416** |

The earlier 203 Kanto failures had one shared cause: `mapjson` excluded every
`REGION_KANTO` map header from the Emerald map-group table, leaving null slots
even when the map was in the story closure. `tools/mapjson/mapjson.cpp` now
honours a map-level `include_in_versions` opt-in. All 203 Kanto closure maps
have that Emerald opt-in, and 137 FRLG layouts gained the matching opt-in. The
new script manifest includes all 203 map scripts. Shared FRLG scripts needed
252 text labels from off-closure maps and 54 duplicate donor script blocks
guarded so the Plastic Ox versions win. The build also links the 34 FRLG
tileset headers and associated assets that those maps need. Hidden-item flags
that previously compiled to zero now use a separate 191-bit SaveBlock3 allocation;
the one name shared with a Hoenn hidden item has a Kanto-specific alias. This
keeps the existing SaveBlock1 offsets intact.

When adding another Kanto map, keep its `map.json` opt-in, layout opt-in,
`data/scripts/plastic_ox_kanto_maps.inc`, and
`src/data/tilesets/plastic_ox_kanto_additions.h` aligned. The extra shared
script text is in `data/scripts/plastic_ox_kanto_extra_text.inc`.

The prior `GoldenrodCity_UndergroundSwitches_hns` failure was a probe error:
the fixed sample tile (2,2) is intentionally metatile 1023. The load check now
chooses a defined tile from each source blockmap; Goldenrod passes at (3,2).
`MtMoon_Cave_hns` is a retired map retained for old saves and intentionally
redirects to `MtMoon_1F_Frlg` on load. The harness verifies the target's live
grid and records the redirect separately. In a fresh boot, `CeruleanCity_Frlg`
also renders terrain, buildings and NPCs; a blank screenshot from an aborted
run followed an unhealthy Battle Frontier field script and was not a tileset
failure.

Evidence: `plastic_ox/agent/warp_playtest_v1_unblocked_loadcheck.json` contains
all 417 per-map verdicts and the ROM hash. The import audit passed for 89 HNS
layouts, and `git diff --check` passed.

## R6.2 Route 8 gate safety

`Route8_WestEntrance_Frlg[2]` and `[3]` referenced Route 8 warp 1 when Route 8
had only warp 0. Route 8 now has warp 1 at a walkable road tile (9,20), so both
gate exits have a valid, safe landing. The two formerly inert gate lanes at
(1,4) and (11,6) now have matching west/east arrow warp metatiles, preserving
their artwork. The repair table in `plastic_ox/agent/fix_warp_metatiles.py` is
idempotent (`0 block(s) repointed` on a second run). A focused mGBA walk found
both gate exits toward Saffron working, and both exits toward Route 8 landing
at (9,20) with room to move.

The earlier P0 wording claimed that an invalid destination warp ID reads past
the target warp table. `src/overworld.c::SetPlayerCoordsFromWarp` actually
bounds-checks the ID and falls back to supplied coordinates or the map center.
The old link could still land at an unrelated position, which the new warp
entry fixes. Route 8 warp 1 is an arrival anchor on normal road. Walking west
from it takes the existing authored portal to `SaffronCity_hns`, so the generic
reciprocity test still marks the two gate-to-Route-8 rows as ISSUE. Resolving
that requires a topology decision about the donor FRLG gate versus the
authored Saffron portal.

## R6.3 Validation and next repair pass

The Emerald build succeeded. An in-emulator script set and cleared the first
and last virtual Kanto hidden-item flags independently, confirming that they
write separate SaveBlock3 bits. Static analysis now finds **zero out-of-range
destination warp IDs** and 41 warp findings overall; the two Route 8 gate
out-of-range findings are gone. The import audit passed:

```sh
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py /home/eddie/repos/poke-plastic-ox
```

The new loadable Kanto rooms expose door lanes that the old run could not
walk. A source-data scan found 179 Kanto warp events on `MB_NORMAL` tiles; 158
are within two tiles of a functioning warp event with the same destination.
Of those, 122 have walkable source tiles and 36 have solid source tiles. That
is a strong candidate for a shared door-lane repair pass, with the solid lanes
checked against their artwork before carving. Existing run 5 notes about
water-driven Seafoam transitions, Trick House puzzle doors, and donor facility
state machines still apply.

## R7.1 Surf expansion (harness-side movement, no data or ROM changes)

The on-foot walker could not follow the Seafoam Islands' water-driven
transitions, so `plastic_ox/demo/test_warps_v1.py` now mounts Surf and
climbs waterfalls for real. Nothing in `data/` or `src/` was touched: the
expansion is entirely in the playtest harness.

**What it does.** The fixture boots a fresh game, so there is no battery save
to edit. The harness grants a Surf kit through the engine's own field-script
commands instead (`grant_surf_kit`): a party mon via `ScrCmd_createmon` that is
taught Surf and Waterfall with `ScrCmd_setmonmove` (both
`IsFieldMoveUnlocked_Surf` and `PartyHasMonWithSurf()` must be true for the A
prompt), plus `ITEM_SURF_KEY` in the bag via `ScrCmd_additem`, because with
`FLAG_POX_TRIGGERS_ENABLED` this ROM unlocks Surf from the key item rather than
from the Surf Badge. It then verifies the grant with the engine's own
`ScrCmd_checkfieldmove` and records the result in the report's `surf.granted`
field. On top of that:

* `mount_surf` presses A on the engine's own YES/NO prompt, retrying with the
  cursor nudged in case the box opened on NO, and waits for the one-tile step
  onto the water rather than trusting `PLAYER_AVATAR_FLAG_SURFING` alone.
* `use_waterfall` does the same for `MB_WATERFALL` facing north, which is the
  only way the engine offers that field effect.
* `place_in_water` / `swim_to` / `_next_step_toward` put the player on a water
  run-up the way a player would: injected on the nearest dry tile, mounted from
  the shore, and swum there over the live block grid.
* A warp that sits on water is tried surf-first; `static_needs_surf` detects a
  warp with no dry run-up at all and only those rows get the surf retry, so the
  dry pass still covers everything else. A row whose surf path cannot be built
  is reported `UNTESTED` with the engine's own reason
  (`surf path needed but not reachable: ...`) rather than a bare timeout.
* Water-to-water map connections are retried on the board when every dry lane
  fails.

**`--no-surf`** restores the pure on-foot walk, so any row in this report can be
re-checked against the pre-expansion behaviour.

**Bug found and fixed while reviewing the expansion.** `dismount_surf` derived
its direction with an unguarded `next(d for d, v in DIRS.items() if v == (dx, dy))`,
but `nearest_dry_tile` is a 4-way flood fill and can return a *diagonal* shore.
The generator then raised `StopIteration`, which propagated out of
`test_one_connection` and turned every seam tested after a surf row into a
`harness exception: StopIteration()` ERROR. In the sanity run below this
silently destroyed all three Route 12 seam rows. Diagonal and multi-tile
deltas now go through the cardinal-only pathfinder, and the `next()` calls in
`dismount_surf` and `swim_to` have defaults, so the degenerate case can never
raise again. The fix is harness-only.

**Sanity run.** Targeted, not the full 1279-warp walk — the Seafoam Islands
family plus one exterior water route, interiors excluded:

```sh
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_warps_v1.py \
  --only SeafoamIslands --only Route12_Frlg --exclude BattleFrontier \
  --json /tmp/pox_surf_sanity.json
```

6 maps (`SeafoamIslands_1F` and `B1F`–`B4F`, `Route12_Frlg`), 46 warps and
3 seams, 121 s wall clock, 11 emulator reboots. Surf was granted
(`surf holder=party[0] waterfall holder=0`).

* **Warps: 29 OK, 13 ISSUE, 2 PARTIAL, 2 UNTESTED. Seams: 2 OK, 1 ISSUE.**
* **Warps reaching an OK verdict with `via_surf` / `approach_via_surf` set: 0.**
* **Warps whose run-up was genuinely reached on the board: 2** —
  `SeafoamIslands_B4F_Frlg[2]` and `[3]`, the northbound whirlpool returns. The
  harness swam to the run-up on the board, stepped onto the warp tile, and the
  warp did not fire.
* **Warps left UNTESTED with `surf path needed but not reachable`: 0.**
  2 warps are UNTESTED, both `SeafoamIslands_B3F_Frlg[5]` and `[6]` at (23,9)
  and (24,9), and the reason is not the surf machinery: the tile is
  `MB_SOUTHWARD_CURRENT`, and their surf run-ups also fail with
  `no walkable path from (29,4) to (23,10)` — the upper pool on B3F is not
  connected to a dry shore the flood fill can start from.

**Why no warp fires on surf, honestly.** This is a data finding, not a harness
limit. `IsWarpMetatileBehavior` and `IsArrowWarpMetatileBehavior` in
`src/field_control_avatar.c` accept only warp doors, ladders, escalators, the
Lavaridge/Aqua Hideout/Union Room/Mossdeep/Mt. Pyre Hole warps and the four
arrow-warp metatiles (`MetatileBehavior_IsNorthArrowWarp` accepts only
`MB_NORTH_ARROW_WARP` and `MB_STAIRS_OUTSIDE_ABANDONED_SHIP`;
`MetatileBehavior_IsSouthArrowWarp` only `MB_SOUTH_ARROW_WARP`,
`MB_WATER_SOUTH_ARROW_WARP` and `MB_SHOAL_CAVE_ENTRANCE` — confirmed in
`src/metatile_behavior.c`). `MB_NORTHWARD_CURRENT` and `MB_SOUTHWARD_CURRENT`
are in none of those lists, so the Seafoam whirlpool warp events at
`SeafoamIslands_B3F_Frlg` (23,9)/(24,9) and `SeafoamIslands_B4F_Frlg`
(8,17)/(9,17) can never fire, on foot or on the surfboard. The harness
confirms this empirically as well as statically: it stood on the board and
stepped onto (8,17) and nothing happened. These four rows are the same class
of defect as R5.4 (warp event on a metatile the engine never triggers) and
need a metatile repair, not a better walk.

**Coverage versus the earlier runs.** The prior full run
(`warp_playtest_v1_unblocked.json`) had the whole Seafoam family excluded with
`--exclude`, so 32 of these 46 rows were UNTESTED for lack of a walk rather
than for lack of a result. Against the on-foot run 5
(`warp_playtest_v1_run5.json`, 26 OK / 14 ISSUE / 2 PARTIAL / 4 UNTESTED here),
the expansion changes six rows: `Route12_Frlg[0]`, `[1]` and `[3]` move from
UNTESTED to OK — but only because Route 12 now loads under the current build,
not because of surf — and `SeafoamIslands_B3F_Frlg[5]` and `[6]` move from ISSUE
to UNTESTED, which is the more honest verdict once the harness knows the
metatile can never fire. **The Seafoam Islands warps that previously stalled the
walk are now all exercised** (44 of 46 reach a real verdict), but the surfboard
itself is still not what carries a player through this set.

**Honest limits of the expansion.**

* Waterfalls in a separate upper pool are unreachable: `nearest_dry_tile`
  floods from the player's own tile and `swim_to` only follows a cardinal
  path over the live grid, so a pool the player cannot swim to from a shore
  they can already reach is simply out of reach. B3F's upper pool is the live
  example — every surf run-up reports `no walkable path`.
* Only the metatiles in `SURFACE_BEHAVIORS` offer the Surf prompt. A tile that
  is merely wet (`MB_SHALLOW_WATER`, bridges) never triggers it, and the
  harness reports that as a real reason rather than timing out.
* Surf is offered from `ELEVATION_DEFAULT` only, and the engine dismounts onto
  `ELEVATION_DEFAULT` only, so a shore search cannot land on any other level.
* The expansion changes no data. A water-locked warp that sits on a metatile
  the engine rejects is still broken after this work; it is reported, not
  fixed.

---

# RUN 7 (POST-CUT) — FRLG Safari Zone removal, 2026-10-02

**Current handoff: this run.** Everything above it is historical. The full
1,279-warp walk was deliberately **not** re-run (the user asked for a targeted
subset only); what follows is the post-cut verification that was actually
performed.

**ROM under test:** `pokeemerald.gba` @ `c1fb0b62922ac24e028c3ca59cf103d38a71b0d3bd3592eb87c3ed975e7ba2e9`
(previous build: `21cfd4a224d40e129c7ed5a3eef14a1d93f15ec47eff4118d2d9633da05eb9b5`).
`plastic_ox/agent/warp_playtest_v1_unblocked.json` refers to the **pre-cut** hash and is
left untouched as a historical checkpoint — do not re-run anything against it.

**Why the ROM changed:** the FRLG Safari Zone family (11 maps) was removed on user
approval. See the **Decision log D1** in `plastic_ox/agent/ROM_SPACE_TRIM_AUDIT.md`.

## R7.1 Per-map load check — 406 / 406 PASS

```sh
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_warps_v1.py \
  --load-only --json plastic_ox/agent/warp_playtest_v2_postcut_loadcheck.json
```

| metric | run 6 (`warp_playtest_v1_unblocked.json`) | run 7 (post-cut) |
|---|--:|--:|
| maps in the closure | 417 | **406** |
| warp events | 1,278 | 1,211 |
| connections | 86 | 86 |
| maps that load and yield a usable grid | 406 / 406 | **406 / 406** |

The closure lost exactly the 11 removed maps and **nothing else** — the set difference
is precisely `SafariZone_{Center,East,North,West}[_RestHouse]_Frlg`,
`SafariZone_SecretHouse_Frlg`, `FuchsiaCity_SafariZone_{Entrance,Office}_Frlg`.
No map was added, and no previously-loading map regressed to unloadable.

**Artefacts:** `warp_playtest_v2_postcut_loadcheck.json` (load verdicts),
`warp_playtest_v2_postcut_fuchsia.json` + `_fuchsia_maps.json` (targeted walk),
`warp_playtest_v2_postcut_unionroom.json` (UnionRoom re-check).

## R7.2 Targeted warp sanity — Fuchsia City and neighbours

```sh
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_warps_v1.py \
  --load-report plastic_ox/agent/warp_playtest_v2_postcut_loadcheck.json \
  --exclude BattleFrontier \
  --only Fuchsia --only Route2_ --only Route19 --only Route15 --only Route14 --only Cinnabar \
  --json plastic_ox/agent/warp_playtest_v2_postcut_fuchsia.json \
  --maps plastic_ox/agent/warp_playtest_v2_postcut_fuchsia_maps.json
```

28 maps, 92 static warps, 10 seams. Static findings: **0**. Dynamic:
**77 OK / 23 ISSUE / 2 PARTIAL**, 2 emulator reboots, 54.3 s.

**Every one of the 92 rows was diffed against run 6 by `(map, warp_index)`.**

| change | rows | verdict |
|---|--:|---|
| unchanged | 88 | identical status |
| `FuchsiaCity_Frlg[0]` and `[3]`: `UNTESTED` → `OK` | 2 | **expected improvement.** These were the two Safari Zone warps; the indices now belong to the Warden's House and the Mart, and both walk correctly |
| `FuchsiaCity_PokemonCenter_2F_Frlg[1]`, `CinnabarIsland_PokemonCenter_2F_Frlg[1]`: `OK` → `PARTIAL` | 2 | **not a regression — see below** |

### The 23 ISSUE rows are pre-existing and unrelated

All 23 are the same FRLG door-exit defect already on record:
*"the warp tile (x,y) is MB_NORMAL, which the engine's warp trigger
(`IsWarpMetatileBehavior` / `TryArrowWarp`) does not accept"* — e.g.
`FuchsiaCity_WardensHouse_Frlg[0]`/`[2]`, `FuchsiaCity_Mart_Frlg[0]`/`[2]`,
`FuchsiaCity_Gym_Frlg[0]`/`[2]`, `FuchsiaCity_House{1,2}_Frlg[0]`/`[2]`,
`FuchsiaCity_PokemonCenter_1F_Frlg[0]`/`[2]`, `Route15_WestEntrance_1F_Frlg[1]`/`[3]`,
`CinnabarIsland_PokemonLab_Entrance_Frlg[0]`/`[2]`,
`CinnabarIsland_PokemonCenter_1F_Frlg[1]`/`[2]`, and the
`FuchsiaCity_Frlg` ↔ `Route19_Frlg` south seam.

**Every one of these rows has the identical status in run 6.** The Safari Zone cut did
not create, move or fix any of them; none of their maps, layouts or warp data were
touched. This is the same class as run 6's R5.4 — a warp event sitting on a metatile the
engine never triggers — and it needs a metatile repair, not a better walk.

### The 2 PARTIAL rows are a harness-side INCONCLUSIVE on an untouched map

Both rows land in `UnionRoom_Frlg[0]`, a `MAP_DYNAMIC` facility exit on the **last row**
of the map (y = 11 of 12). The harness drops the player onto (7,11), then tries DOWN /
LEFT / RIGHT (and UP via surf); (7,12), (7,13) and (7,14) are all off-map, so no step
ever re-enters the warp tile and the row is scored `INCONCLUSIVE` rather than a result.
Reproduced deterministically on a dedicated 4-map re-run
(`warp_playtest_v2_postcut_unionroom.json`).

This is **not** attributable to the cut:

* `data/maps/UnionRoom_Frlg/` and `data/maps/UnionRoom/` are untouched (their `map.json`
  shows as modified only because of the repo-wide pre-existing
  `include_in_versions: ["emerald"]` line, which predates this work).
* `data/layouts/UnionRoom_Frlg/` is untouched.
* The load check reports an identical probe for `UnionRoom_Frlg` in both ROMs:
  grid `[30, 26]`, metatile `730`, state `[34, 4, 2, 2]`.
* Run 6's JSON has no `via_surf` / `notes` / `retried_after_reboot` fields at all — the
  harness gained surf support after that run, and the new surf expansion is what
  generates this note. Run 6 simply had no vocabulary for "INCONCLUSIVE".
* `UnionRoom_Frlg` is a facility state machine, the class run 6 already excluded from
  generic walking.

## R7.3 What the cut deliberately did *not* fix

* The `MB_NORMAL` door-exit metatiles in §R7.2 above. Out of scope.
* `UnionRoom_Frlg`'s `MAP_DYNAMIC` exit on a last-row tile. Out of scope; note that
  `UnionRoom` / `UnionRoom_Frlg` are in the closure and would need a warp repoint if the
  link facilities are ever cut (audit §6.5, §8 step 9 — postponed).
* §7.0's `PlasticOxContest_TakeStep()` / `SafariZoneTakeStep()` shared step counter. Still
  live; it is just no longer reachable from the deleted Kanto maps.
* `MAPSEC_KANTO_SAFARI_ZONE` and the 11 `FLAG_HIDE_SAFARI_ZONE_*` names are now unused
  but retained — reclaiming either renumbers a save-file surface.
