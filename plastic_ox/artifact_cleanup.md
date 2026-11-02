# Plastic Ox artifact cleanup inventory

Audited 2026-10-24 against the current working tree, including uncommitted v7
story and league changes. This document inventories future work; no gameplay
content was removed. Companion: [artifact cleanup skill](../.agents/skills/plastic-ox-artifact-cleanup/SKILL.md).

## Evidence and scope

Run from the repository root:

```sh
python3 plastic_ox/agent/audit_cleanup_artifacts.py > /tmp/plastic-ox-cleanup-audit.json
```

The read-only audit seeds the current region transitions, story events, Pallet
start, and every literal map ID in `data/scripts/plastic_ox*.inc`, then follows
directed native connections and map JSON warps. It also reports external literal
map-ID references for each candidate. Its JSON includes the full protected set
and reasons. This is deliberately conservative: an unused authored label can
protect an obsolete area, while dynamic/engine-selected destinations and shared
script calls can escape this model. No flags, collision, script conditions, or
runtime traversal are simulated. Neither set proves runtime accessibility.

Snapshot: **1045 map JSON files; 419 protected/review maps; 626 unprotected candidates in 51 map groups.**

## Prioritized cleanup slices

| Priority | Candidate slice | Evidence and next action |
| --- | --- | --- |
| 1 | Gabby/Ty roaming routes: `Route111`, `Route118`, `Route120`; `SlateportCity` and its interiors | Absent from the current transition manifest and protected closure. Retained donor map events and shared reporter scripts still exist. Inspect `data/scripts/gabby_and_ty.inc`, `src/tv.c`, rematch tables and encounter data before removing their roaming system. Keep the Fortree pair. |
| 1 | Disconnected Hoenn towns and roads | Includes Dewford, Fallarbor, Lavaridge, Mauville, Petalburg, Lilycove, Sootopolis, Ever Grande and their listed routes/interiors. Remove old-world quest actors first; map deletion requires resolving engine references and save IDs. Exact candidates follow below. |
| 2 | Old Hoenn dungeon/story clusters | Abandoned Ship, Aqua/Magma hideouts, Mt. Chimney/Jagged Pass, Cave of Origin, Seafloor Cavern, Mt. Pyre, Sky Pillar, Regis/Sealed Chamber, Mirage Tower and Shoal Cave are candidates in this snapshot. Review each cluster against authored side quests before removal. Some already have unrelated dirty changes. |
| 2 | FRLG Sevii islands and original League | One–Seven Island families, Mt. Ember, Icefall Cave, Dotted Hole, Rocket Warehouse, Tanoby areas, original FRLG Elite Four and FRLG Victory Road have no protected graph attachment in this model. Shared services/assets may still be used. |
| 2 | Superseded imports and alternate map variants | Examples: `Route1_Frlg`, `Route20_Frlg`, `MtMoon_Cave_hns`, and `ViridianForest_Frlg`. Current Mt. Moon uses the FRLG floor cluster; current sea passage uses `PlasticOx_Route20West/East`. Check exact active variants rather than deleting by place name. |
| 3 | Unused labels inside retained files | Vanilla `FortreeCity_Gym_EventScript_Winona` awards badge 6, but the live object invokes `Pox_Winona` and awards badge 4. Audit similar original Gym handlers, unused callbacks and stale dialogue by label callers. File inclusion alone does not make a label live. |
| 3 | Obsolete generated compatibility paths and planning tools | `VictoryRoad_1F` and its cave floors remain protected conservatively by literal authored references, although the final league overlay routes the real checkpoint to `PlasticOx_VictoryRoad`. Review old `PoxRegion_ecruteak_league_*`, `victory_indigo_*`, prototype league labels, and the old cave map events. `LEGACY_PLAN.md` / `LEGACY_REGION_PLAN.md` are historical references, not current graph authority. |

## Explicit keep/review exceptions

- **Fortree Gabby/Ty:** live progression blockers, hidden by `FLAG_BADGE04_GET`.
  The active `Pox_Winona` sets that same flag. Do not change them to badge 6.
- **Current league:** `PlasticOx_VictoryRoad`, Indigo Plateau HNS lobby,
  `PlasticOx_LeagueRestHouse1/2`, Wallace/Steven/Lance/Blue/Bill rooms and
  `PlasticOx_HallOfFame`. The final `plastic_ox/alpha/league.py` overlay owns
  these and rewrites older manifest/compatibility transitions.
- **Postgame:** `PlasticOx_Harbor` and Battle Frontier are intentional. The harbor
  reuses Slateport Harbor as donor material in `region_v7.py`; that dependency
  survives even if the original Slateport city is unused.
- **Shared services and dynamic maps:** link rooms, trade/contest/battle rooms,
  Secret Bases, ferry interiors, dynamic return maps and facility templates need
  engine-level review. Their absence from the static graph is not sufficient.
- **Layouts, tilesets and source snapshots:** a candidate map's graphics and
  donor snapshots can still generate a live map. Do not delete by directory
  prefix, map-group membership, or an unreferenced `MAP_*` constant alone.

## Dependency work required before deletion

Search both directory names and exact map IDs. Candidate JSON reports external
literal ID references, but does not trace labels, macro aliases or resource IDs.
For Routes 111/118/120 and Slateport, actual remaining references include
`src/battle_setup.c`, `src/roamer.c`, `src/region_map.c`, `src/tv.c`,
`src/data/wild_encounters.json`, and Slateport heal locations. Route 111 also
appears in `src/mirage_tower.c` and `src/overworld.c`.

Review `data/maps/map_groups.json`, `data/layouts/layouts.json`,
`data/event_scripts.s`, source heal/encounter JSON, map event constants, C fly
and rematch tables, and generator sources. Generated headers, `events.inc` and
encounter tables are outputs, not the source of truth. Removing group entries
can renumber map IDs and break existing saves; consider preserving empty slots.

Before changing generated files, inspect `build_story.py`, `region_v7.py` and
`league.py` together. The last overlay wins. Preserve unrelated working-tree
changes and inspect emitted patches before applying them.

## Complete unprotected candidate inventory

Every name below identifies `data/maps/<name>/map.json`. Grouping follows
`data/maps/map_groups.json`; this is a triage backlog, not permission to remove
entire groups. Names may be retained for shared mechanics or other build versions.

### gMapGroup_TownsAndRoutes (48)

- `DewfordTown`
- `EverGrandeCity`
- `FallarborTown`
- `LavaridgeTown`
- `LilycoveCity`
- `LittlerootTown`
- `MauvilleCity`
- `PacifidlogTown`
- `PetalburgCity`
- `Route102`
- `Route104`
- `Route105`
- `Route106`
- `Route107`
- `Route108`
- `Route109`
- `Route111`
- `Route112`
- `Route113`
- `Route114`
- `Route116`
- `Route117`
- `Route118`
- `Route120`
- `Route121`
- `Route122`
- `Route123`
- `Route124`
- `Route125`
- `Route126`
- `Route127`
- `Route128`
- `Route129`
- `Route130`
- `Route131`
- `Route132`
- `Route133`
- `Route134`
- `SlateportCity`
- `SootopolisCity`
- `Underwater_Route105`
- `Underwater_Route124`
- `Underwater_Route125`
- `Underwater_Route126`
- `Underwater_Route127`
- `Underwater_Route128`
- `Underwater_Route129`
- `VerdanturfTown`

### gMapGroup_IndoorLittleroot (5)

- `LittlerootTown_BrendansHouse_1F`
- `LittlerootTown_BrendansHouse_2F`
- `LittlerootTown_MaysHouse_1F`
- `LittlerootTown_MaysHouse_2F`
- `LittlerootTown_ProfessorBirchsLab`

### gMapGroup_IndoorDewford (6)

- `DewfordTown_Gym`
- `DewfordTown_Hall`
- `DewfordTown_House1`
- `DewfordTown_House2`
- `DewfordTown_PokemonCenter_1F`
- `DewfordTown_PokemonCenter_2F`

### gMapGroup_IndoorLavaridge (7)

- `LavaridgeTown_Gym_1F`
- `LavaridgeTown_Gym_B1F`
- `LavaridgeTown_HerbShop`
- `LavaridgeTown_House`
- `LavaridgeTown_Mart`
- `LavaridgeTown_PokemonCenter_1F`
- `LavaridgeTown_PokemonCenter_2F`

### gMapGroup_IndoorFallarbor (8)

- `FallarborTown_BattleTentBattleRoom`
- `FallarborTown_BattleTentCorridor`
- `FallarborTown_BattleTentLobby`
- `FallarborTown_CozmosHouse`
- `FallarborTown_Mart`
- `FallarborTown_MoveRelearnersHouse`
- `FallarborTown_PokemonCenter_1F`
- `FallarborTown_PokemonCenter_2F`

### gMapGroup_IndoorVerdanturf (9)

- `VerdanturfTown_BattleTentBattleRoom`
- `VerdanturfTown_BattleTentCorridor`
- `VerdanturfTown_BattleTentLobby`
- `VerdanturfTown_FriendshipRatersHouse`
- `VerdanturfTown_House`
- `VerdanturfTown_Mart`
- `VerdanturfTown_PokemonCenter_1F`
- `VerdanturfTown_PokemonCenter_2F`
- `VerdanturfTown_WandasHouse`

### gMapGroup_IndoorPacifidlog (7)

- `PacifidlogTown_House1`
- `PacifidlogTown_House2`
- `PacifidlogTown_House3`
- `PacifidlogTown_House4`
- `PacifidlogTown_House5`
- `PacifidlogTown_PokemonCenter_1F`
- `PacifidlogTown_PokemonCenter_2F`

### gMapGroup_IndoorPetalburg (7)

- `PetalburgCity_Gym`
- `PetalburgCity_House1`
- `PetalburgCity_House2`
- `PetalburgCity_Mart`
- `PetalburgCity_PokemonCenter_1F`
- `PetalburgCity_PokemonCenter_2F`
- `PetalburgCity_WallysHouse`

### gMapGroup_IndoorSlateport (14)

- `SlateportCity_BattleTentBattleRoom`
- `SlateportCity_BattleTentCorridor`
- `SlateportCity_BattleTentLobby`
- `SlateportCity_Harbor`
- `SlateportCity_House`
- `SlateportCity_Mart`
- `SlateportCity_NameRatersHouse`
- `SlateportCity_OceanicMuseum_1F`
- `SlateportCity_OceanicMuseum_2F`
- `SlateportCity_PokemonCenter_1F`
- `SlateportCity_PokemonCenter_2F`
- `SlateportCity_PokemonFanClub`
- `SlateportCity_SternsShipyard_1F`
- `SlateportCity_SternsShipyard_2F`

### gMapGroup_IndoorMauville (8)

- `MauvilleCity_BikeShop`
- `MauvilleCity_GameCorner`
- `MauvilleCity_Gym`
- `MauvilleCity_House1`
- `MauvilleCity_House2`
- `MauvilleCity_Mart`
- `MauvilleCity_PokemonCenter_1F`
- `MauvilleCity_PokemonCenter_2F`

### gMapGroup_IndoorLilycove (23)

- `LilycoveCity_ContestHall`
- `LilycoveCity_ContestLobby`
- `LilycoveCity_CoveLilyMotel_1F`
- `LilycoveCity_CoveLilyMotel_2F`
- `LilycoveCity_DepartmentStoreElevator`
- `LilycoveCity_DepartmentStoreRooftop`
- `LilycoveCity_DepartmentStore_1F`
- `LilycoveCity_DepartmentStore_2F`
- `LilycoveCity_DepartmentStore_3F`
- `LilycoveCity_DepartmentStore_4F`
- `LilycoveCity_DepartmentStore_5F`
- `LilycoveCity_Harbor`
- `LilycoveCity_House1`
- `LilycoveCity_House2`
- `LilycoveCity_House3`
- `LilycoveCity_House4`
- `LilycoveCity_LilycoveMuseum_1F`
- `LilycoveCity_LilycoveMuseum_2F`
- `LilycoveCity_MoveDeletersHouse`
- `LilycoveCity_PokemonCenter_1F`
- `LilycoveCity_PokemonCenter_2F`
- `LilycoveCity_PokemonTrainerFanClub`
- `LilycoveCity_UnusedMart`

### gMapGroup_IndoorSootopolis (15)

- `SootopolisCity_Gym_1F`
- `SootopolisCity_Gym_B1F`
- `SootopolisCity_House1`
- `SootopolisCity_House2`
- `SootopolisCity_House3`
- `SootopolisCity_House4`
- `SootopolisCity_House5`
- `SootopolisCity_House6`
- `SootopolisCity_House7`
- `SootopolisCity_LotadAndSeedotHouse`
- `SootopolisCity_Mart`
- `SootopolisCity_MysteryEventsHouse_1F`
- `SootopolisCity_MysteryEventsHouse_B1F`
- `SootopolisCity_PokemonCenter_1F`
- `SootopolisCity_PokemonCenter_2F`

### gMapGroup_IndoorEverGrande (15)

- `EverGrandeCity_ChampionsRoom`
- `EverGrandeCity_DrakesRoom`
- `EverGrandeCity_GlaciasRoom`
- `EverGrandeCity_Hall1`
- `EverGrandeCity_Hall2`
- `EverGrandeCity_Hall3`
- `EverGrandeCity_Hall4`
- `EverGrandeCity_Hall5`
- `EverGrandeCity_HallOfFame`
- `EverGrandeCity_PhoebesRoom`
- `EverGrandeCity_PokemonCenter_1F`
- `EverGrandeCity_PokemonCenter_2F`
- `EverGrandeCity_PokemonLeague_1F`
- `EverGrandeCity_PokemonLeague_2F`
- `EverGrandeCity_SidneysRoom`

### gMapGroup_IndoorRoute104 (2)

- `Route104_MrBrineysHouse`
- `Route104_PrettyPetalFlowerShop`

### gMapGroup_IndoorRoute111 (2)

- `Route111_OldLadysRestStop`
- `Route111_WinstrateFamilysHouse`

### gMapGroup_IndoorRoute112 (2)

- `MtChimney_CableCarStation`
- `Route112_CableCarStation`

### gMapGroup_IndoorRoute114 (3)

- `Route114_FossilManiacsHouse`
- `Route114_FossilManiacsTunnel`
- `Route114_LanettesHouse`

### gMapGroup_IndoorRoute116 (1)

- `Route116_TunnelersRestHouse`

### gMapGroup_IndoorRoute117 (1)

- `Route117_PokemonDayCare`

### gMapGroup_IndoorRoute121 (1)

- `Route121_SafariZoneEntrance`

### gMapGroup_Dungeons (96)

- `AbandonedShip_CaptainsOffice`
- `AbandonedShip_Corridors_1F`
- `AbandonedShip_Corridors_B1F`
- `AbandonedShip_Deck`
- `AbandonedShip_HiddenFloorCorridors`
- `AbandonedShip_HiddenFloorRooms`
- `AbandonedShip_Room_B1F`
- `AbandonedShip_Rooms2_1F`
- `AbandonedShip_Rooms2_B1F`
- `AbandonedShip_Rooms_1F`
- `AbandonedShip_Rooms_B1F`
- `AbandonedShip_Underwater1`
- `AbandonedShip_Underwater2`
- `AlteringCave`
- `AncientTomb`
- `AquaHideout_1F`
- `AquaHideout_B1F`
- `AquaHideout_B2F`
- `AquaHideout_UnusedRubyMap1`
- `AquaHideout_UnusedRubyMap2`
- `AquaHideout_UnusedRubyMap3`
- `CaveOfOrigin_1F`
- `CaveOfOrigin_B1F`
- `CaveOfOrigin_Entrance`
- `CaveOfOrigin_UnusedRubySapphireMap1`
- `CaveOfOrigin_UnusedRubySapphireMap2`
- `CaveOfOrigin_UnusedRubySapphireMap3`
- `DesertRuins`
- `DesertUnderpass`
- `FieryPath`
- `GraniteCave_1F`
- `GraniteCave_B1F`
- `GraniteCave_B2F`
- `GraniteCave_StevensRoom`
- `IslandCave`
- `JaggedPass`
- `MagmaHideout_1F`
- `MagmaHideout_2F_1R`
- `MagmaHideout_2F_2R`
- `MagmaHideout_2F_3R`
- `MagmaHideout_3F_1R`
- `MagmaHideout_3F_2R`
- `MagmaHideout_3F_3R`
- `MagmaHideout_4F`
- `MarineCave_End`
- `MarineCave_Entrance`
- `MirageTower_1F`
- `MirageTower_2F`
- `MirageTower_3F`
- `MirageTower_4F`
- `MtChimney`
- `MtPyre_1F`
- `MtPyre_2F`
- `MtPyre_3F`
- `MtPyre_4F`
- `MtPyre_5F`
- `MtPyre_6F`
- `MtPyre_Exterior`
- `MtPyre_Summit`
- `PetalburgWoods`
- `RusturfTunnel`
- `ScorchedSlab`
- `SeafloorCavern_Entrance`
- `SeafloorCavern_Room1`
- `SeafloorCavern_Room2`
- `SeafloorCavern_Room3`
- `SeafloorCavern_Room4`
- `SeafloorCavern_Room5`
- `SeafloorCavern_Room6`
- `SeafloorCavern_Room7`
- `SeafloorCavern_Room8`
- `SeafloorCavern_Room9`
- `SealedChamber_InnerRoom`
- `SealedChamber_OuterRoom`
- `ShoalCave_HighTideEntranceRoom`
- `ShoalCave_HighTideInnerRoom`
- `ShoalCave_LowTideEntranceRoom`
- `ShoalCave_LowTideIceRoom`
- `ShoalCave_LowTideInnerRoom`
- `ShoalCave_LowTideLowerRoom`
- `ShoalCave_LowTideStairsRoom`
- `SkyPillar_1F`
- `SkyPillar_2F`
- `SkyPillar_3F`
- `SkyPillar_4F`
- `SkyPillar_5F`
- `SkyPillar_Entrance`
- `SkyPillar_Outside`
- `SkyPillar_Top`
- `TerraCave_End`
- `TerraCave_Entrance`
- `Underwater_MarineCave`
- `Underwater_Route134`
- `Underwater_SeafloorCavern`
- `Underwater_SealedChamber`
- `Underwater_SootopolisCity`

### gMapGroup_IndoorDynamic (59)

- `BattleColosseum_2P`
- `BattleColosseum_4P`
- `BattlePyramidSquare01`
- `BattlePyramidSquare02`
- `BattlePyramidSquare03`
- `BattlePyramidSquare04`
- `BattlePyramidSquare05`
- `BattlePyramidSquare06`
- `BattlePyramidSquare07`
- `BattlePyramidSquare08`
- `BattlePyramidSquare09`
- `BattlePyramidSquare10`
- `BattlePyramidSquare11`
- `BattlePyramidSquare12`
- `BattlePyramidSquare13`
- `BattlePyramidSquare14`
- `BattlePyramidSquare15`
- `BattlePyramidSquare16`
- `ContestHall`
- `ContestHallBeauty`
- `ContestHallCool`
- `ContestHallCute`
- `ContestHallSmart`
- `ContestHallTough`
- `InsideOfTruck`
- `RecordCorner`
- `SSTidalCorridor`
- `SSTidalLowerDeck`
- `SSTidalRooms`
- `SecretBase_BlueCave1`
- `SecretBase_BlueCave2`
- `SecretBase_BlueCave3`
- `SecretBase_BlueCave4`
- `SecretBase_BrownCave1`
- `SecretBase_BrownCave2`
- `SecretBase_BrownCave3`
- `SecretBase_BrownCave4`
- `SecretBase_RedCave1`
- `SecretBase_RedCave2`
- `SecretBase_RedCave3`
- `SecretBase_RedCave4`
- `SecretBase_Shrub1`
- `SecretBase_Shrub2`
- `SecretBase_Shrub3`
- `SecretBase_Shrub4`
- `SecretBase_Tree1`
- `SecretBase_Tree2`
- `SecretBase_Tree3`
- `SecretBase_Tree4`
- `SecretBase_YellowCave1`
- `SecretBase_YellowCave2`
- `SecretBase_YellowCave3`
- `SecretBase_YellowCave4`
- `UnusedContestHall1`
- `UnusedContestHall2`
- `UnusedContestHall3`
- `UnusedContestHall4`
- `UnusedContestHall5`
- `UnusedContestHall6`

### gMapGroup_SpecialArea (61)

- `BattleFrontier_BattleArenaBattleRoom`
- `BattleFrontier_BattleArenaCorridor`
- `BattleFrontier_BattleDomeBattleRoom`
- `BattleFrontier_BattleDomeCorridor`
- `BattleFrontier_BattleDomePreBattleRoom`
- `BattleFrontier_BattleFactoryBattleRoom`
- `BattleFrontier_BattleFactoryPreBattleRoom`
- `BattleFrontier_BattlePikeCorridor`
- `BattleFrontier_BattlePikeRoomFinal`
- `BattleFrontier_BattlePikeRoomNormal`
- `BattleFrontier_BattlePikeRoomWildMons`
- `BattleFrontier_BattlePikeThreePathRoom`
- `BattleFrontier_BattlePyramidFloor`
- `BattleFrontier_BattlePyramidTop`
- `BattleFrontier_BattleTowerCorridor`
- `BattleFrontier_BattleTowerElevator`
- `BattleFrontier_BattleTowerMultiBattleRoom`
- `BattleFrontier_BattleTowerMultiCorridor`
- `BattleFrontier_BattleTowerMultiPartnerRoom`
- `BirthIsland_Exterior`
- `BirthIsland_Harbor`
- `FarawayIsland_Entrance`
- `FarawayIsland_Interior`
- `NavelRock_B1F`
- `NavelRock_Bottom`
- `NavelRock_Down01`
- `NavelRock_Down02`
- `NavelRock_Down03`
- `NavelRock_Down04`
- `NavelRock_Down05`
- `NavelRock_Down06`
- `NavelRock_Down07`
- `NavelRock_Down08`
- `NavelRock_Down09`
- `NavelRock_Down10`
- `NavelRock_Down11`
- `NavelRock_Entrance`
- `NavelRock_Exterior`
- `NavelRock_Fork`
- `NavelRock_Harbor`
- `NavelRock_Top`
- `NavelRock_Up1`
- `NavelRock_Up2`
- `NavelRock_Up3`
- `NavelRock_Up4`
- `SafariZone_North`
- `SafariZone_Northeast`
- `SafariZone_Northwest`
- `SafariZone_RestHouse`
- `SafariZone_South`
- `SafariZone_Southeast`
- `SafariZone_Southwest`
- `SouthernIsland_Exterior`
- `SouthernIsland_Interior`
- `TrainerHill_1F`
- `TrainerHill_2F`
- `TrainerHill_3F`
- `TrainerHill_4F`
- `TrainerHill_Elevator`
- `TrainerHill_Entrance`
- `TrainerHill_Roof`

### gMapGroup_IndoorRoute104Prototype (2)

- `Route104_Prototype`
- `Route104_PrototypePrettyPetalFlowerShop`

### gMapGroup_IndoorRoute109 (1)

- `Route109_SeashoreHouse`

### gMapGroup_IndoorRoute110 (7)

- `Route110_TrickHousePuzzle2`
- `Route110_TrickHousePuzzle3`
- `Route110_TrickHousePuzzle4`
- `Route110_TrickHousePuzzle5`
- `Route110_TrickHousePuzzle6`
- `Route110_TrickHousePuzzle7`
- `Route110_TrickHousePuzzle8`

### gMapGroup_IndoorRoute113 (1)

- `Route113_GlassWorkshop`

### gMapGroup_IndoorRoute123 (1)

- `Route123_BerryMastersHouse`

### gMapGroup_IndoorRoute124 (1)

- `Route124_DivingTreasureHuntersHouse`

### gMapGroup_Link_Frlg (3)

- `BattleColosseum_2P_Frlg`
- `BattleColosseum_4P_Frlg`
- `RecordCorner_Frlg`

### gMapGroup_Dungeons_Frlg (37)

- `FiveIsland_RocketWarehouse_Frlg`
- `FourIsland_IcefallCave_1F_Frlg`
- `FourIsland_IcefallCave_B1F_Frlg`
- `FourIsland_IcefallCave_Back_Frlg`
- `FourIsland_IcefallCave_Entrance_Frlg`
- `MtEmber_Exterior_Frlg`
- `MtEmber_RubyPath_1F_Frlg`
- `MtEmber_RubyPath_B1F_Frlg`
- `MtEmber_RubyPath_B1F_Stairs_Frlg`
- `MtEmber_RubyPath_B2F_Frlg`
- `MtEmber_RubyPath_B2F_Stairs_Frlg`
- `MtEmber_RubyPath_B3F_Frlg`
- `MtEmber_RubyPath_B4F_Frlg`
- `MtEmber_RubyPath_B5F_Frlg`
- `MtEmber_SummitPath_1F_Frlg`
- `MtEmber_SummitPath_2F_Frlg`
- `MtEmber_SummitPath_3F_Frlg`
- `MtEmber_Summit_Frlg`
- `PokemonLeague_AgathasRoom_Frlg`
- `PokemonLeague_BrunosRoom_Frlg`
- `PokemonLeague_ChampionsRoom_Frlg`
- `PokemonLeague_HallOfFame_Frlg`
- `PokemonLeague_LancesRoom_Frlg`
- `PokemonLeague_LoreleisRoom_Frlg`
- `SixIsland_AlteringCave_Frlg`
- `SixIsland_DottedHole_1F_Frlg`
- `SixIsland_DottedHole_B1F_Frlg`
- `SixIsland_DottedHole_B2F_Frlg`
- `SixIsland_DottedHole_B3F_Frlg`
- `SixIsland_DottedHole_B4F_Frlg`
- `SixIsland_DottedHole_SapphireRoom_Frlg`
- `SixIsland_PatternBush_Frlg`
- `ThreeIsland_BerryForest_Frlg`
- `VictoryRoad_1F_Frlg`
- `VictoryRoad_2F_Frlg`
- `VictoryRoad_3F_Frlg`
- `ViridianForest_Frlg`

### gMapGroup_SpecialArea_Frlg (60)

- `BirthIsland_Exterior_Frlg`
- `BirthIsland_Harbor_Frlg`
- `FiveIsland_LostCave_Entrance_Frlg`
- `FiveIsland_LostCave_Room10_Frlg`
- `FiveIsland_LostCave_Room11_Frlg`
- `FiveIsland_LostCave_Room12_Frlg`
- `FiveIsland_LostCave_Room13_Frlg`
- `FiveIsland_LostCave_Room14_Frlg`
- `FiveIsland_LostCave_Room1_Frlg`
- `FiveIsland_LostCave_Room2_Frlg`
- `FiveIsland_LostCave_Room3_Frlg`
- `FiveIsland_LostCave_Room4_Frlg`
- `FiveIsland_LostCave_Room5_Frlg`
- `FiveIsland_LostCave_Room6_Frlg`
- `FiveIsland_LostCave_Room7_Frlg`
- `FiveIsland_LostCave_Room8_Frlg`
- `FiveIsland_LostCave_Room9_Frlg`
- `NavelRock_1F_Frlg`
- `NavelRock_B1F_Frlg`
- `NavelRock_BasePath_B10F_Frlg`
- `NavelRock_BasePath_B11F_Frlg`
- `NavelRock_BasePath_B1F_Frlg`
- `NavelRock_BasePath_B2F_Frlg`
- `NavelRock_BasePath_B3F_Frlg`
- `NavelRock_BasePath_B4F_Frlg`
- `NavelRock_BasePath_B5F_Frlg`
- `NavelRock_BasePath_B6F_Frlg`
- `NavelRock_BasePath_B7F_Frlg`
- `NavelRock_BasePath_B8F_Frlg`
- `NavelRock_BasePath_B9F_Frlg`
- `NavelRock_Base_Frlg`
- `NavelRock_Exterior_Frlg`
- `NavelRock_Fork_Frlg`
- `NavelRock_Harbor_Frlg`
- `NavelRock_SummitPath_2F_Frlg`
- `NavelRock_SummitPath_3F_Frlg`
- `NavelRock_SummitPath_4F_Frlg`
- `NavelRock_SummitPath_5F_Frlg`
- `NavelRock_Summit_Frlg`
- `OneIsland_KindleRoad_EmberSpa_Frlg`
- `SevenIsland_SevaultCanyon_TanobyKey_Frlg`
- `SevenIsland_TanobyRuins_DilfordChamber_Frlg`
- `SevenIsland_TanobyRuins_LiptooChamber_Frlg`
- `SevenIsland_TanobyRuins_MoneanChamber_Frlg`
- `SevenIsland_TanobyRuins_RixyChamber_Frlg`
- `SevenIsland_TanobyRuins_ScufibChamber_Frlg`
- `SevenIsland_TanobyRuins_ViapoisChamber_Frlg`
- `SevenIsland_TanobyRuins_WeepthChamber_Frlg`
- `ThreeIsland_DunsparceTunnel_Frlg`
- `TrainerTower_1F_Frlg`
- `TrainerTower_2F_Frlg`
- `TrainerTower_3F_Frlg`
- `TrainerTower_4F_Frlg`
- `TrainerTower_5F_Frlg`
- `TrainerTower_6F_Frlg`
- `TrainerTower_7F_Frlg`
- `TrainerTower_8F_Frlg`
- `TrainerTower_Elevator_Frlg`
- `TrainerTower_Lobby_Frlg`
- `TrainerTower_Roof_Frlg`

### gMapGroup_TownsAndRoutes_Frlg (30)

- `FiveIsland_Frlg`
- `FiveIsland_Meadow_Frlg`
- `FiveIsland_MemorialPillar_Frlg`
- `FiveIsland_ResortGorgeous_Frlg`
- `FiveIsland_WaterLabyrinth_Frlg`
- `FourIsland_Frlg`
- `IndigoPlateau_Exterior_Frlg`
- `OneIsland_Frlg`
- `OneIsland_KindleRoad_Frlg`
- `OneIsland_TreasureBeach_Frlg`
- `Route1_Frlg`
- `Route20_Frlg`
- `Route22_Frlg`
- `Route23_Frlg`
- `SevenIsland_Frlg`
- `SevenIsland_SevaultCanyon_Entrance_Frlg`
- `SevenIsland_SevaultCanyon_Frlg`
- `SevenIsland_TanobyRuins_Frlg`
- `SevenIsland_TrainerTower_Frlg`
- `SixIsland_Frlg`
- `SixIsland_GreenPath_Frlg`
- `SixIsland_OutcastIsland_Frlg`
- `SixIsland_RuinValley_Frlg`
- `SixIsland_WaterPath_Frlg`
- `ThreeIsland_BondBridge_Frlg`
- `ThreeIsland_Frlg`
- `ThreeIsland_Port_Frlg`
- `TwoIsland_CapeBrink_Frlg`
- `TwoIsland_Frlg`
- `ViridianCity_Frlg`

### gMapGroup_IndoorViridian_Frlg (6)

- `ViridianCity_Gym_Frlg`
- `ViridianCity_House_Frlg`
- `ViridianCity_Mart_Frlg`
- `ViridianCity_PokemonCenter_1F_Frlg`
- `ViridianCity_PokemonCenter_2F_Frlg`
- `ViridianCity_School_Frlg`

### gMapGroup_IndoorIndigoPlateau_Frlg (2)

- `IndigoPlateau_PokemonCenter_1F_Frlg`
- `IndigoPlateau_PokemonCenter_2F_Frlg`

### gMapGroup_IndoorRoute22_Frlg (1)

- `Route22_NorthEntrance_Frlg`

### gMapGroup_IndoorSevenIsland_Frlg (6)

- `SevenIsland_Harbor_Frlg`
- `SevenIsland_House_Room1_Frlg`
- `SevenIsland_House_Room2_Frlg`
- `SevenIsland_Mart_Frlg`
- `SevenIsland_PokemonCenter_1F_Frlg`
- `SevenIsland_PokemonCenter_2F_Frlg`

### gMapGroup_IndoorOneIsland_Frlg (5)

- `OneIsland_Harbor_Frlg`
- `OneIsland_House1_Frlg`
- `OneIsland_House2_Frlg`
- `OneIsland_PokemonCenter_1F_Frlg`
- `OneIsland_PokemonCenter_2F_Frlg`

### gMapGroup_IndoorTwoIsland_Frlg (5)

- `TwoIsland_Harbor_Frlg`
- `TwoIsland_House_Frlg`
- `TwoIsland_JoyfulGameCorner_Frlg`
- `TwoIsland_PokemonCenter_1F_Frlg`
- `TwoIsland_PokemonCenter_2F_Frlg`

### gMapGroup_IndoorThreeIsland_Frlg (8)

- `ThreeIsland_House1_Frlg`
- `ThreeIsland_House2_Frlg`
- `ThreeIsland_House3_Frlg`
- `ThreeIsland_House4_Frlg`
- `ThreeIsland_House5_Frlg`
- `ThreeIsland_Mart_Frlg`
- `ThreeIsland_PokemonCenter_1F_Frlg`
- `ThreeIsland_PokemonCenter_2F_Frlg`

### gMapGroup_IndoorFourIsland_Frlg (8)

- `FourIsland_Harbor_Frlg`
- `FourIsland_House1_Frlg`
- `FourIsland_House2_Frlg`
- `FourIsland_LoreleisHouse_Frlg`
- `FourIsland_Mart_Frlg`
- `FourIsland_PokemonCenter_1F_Frlg`
- `FourIsland_PokemonCenter_2F_Frlg`
- `FourIsland_PokemonDayCare_Frlg`

### gMapGroup_IndoorFiveIsland_Frlg (5)

- `FiveIsland_Harbor_Frlg`
- `FiveIsland_House1_Frlg`
- `FiveIsland_House2_Frlg`
- `FiveIsland_PokemonCenter_1F_Frlg`
- `FiveIsland_PokemonCenter_2F_Frlg`

### gMapGroup_IndoorSixIsland_Frlg (5)

- `SixIsland_Harbor_Frlg`
- `SixIsland_House_Frlg`
- `SixIsland_Mart_Frlg`
- `SixIsland_PokemonCenter_1F_Frlg`
- `SixIsland_PokemonCenter_2F_Frlg`

### gMapGroup_IndoorThreeIslandRoute_Frlg (1)

- `ThreeIsland_Harbor_Frlg`

### gMapGroup_IndoorFiveIslandRoute_Frlg (1)

- `FiveIsland_ResortGorgeous_House_Frlg`

### gMapGroup_IndoorTwoIslandRoute_Frlg (1)

- `TwoIsland_CapeBrink_House_Frlg`

### gMapGroup_IndoorSixIslandRoute_Frlg (2)

- `SixIsland_WaterPath_House1_Frlg`
- `SixIsland_WaterPath_House2_Frlg`

### gMapGroup_IndoorSevenIslandRoute_Frlg (1)

- `SevenIsland_SevaultCanyon_House_Frlg`

### gMapGroup_PlasticOxInteriors (8)

- `Gate_AzaleaTown_IlexForest_hns`
- `Gate_EcruteakCity_Route38_hns`
- `Gate_EcruteakCity_Route42_hns`
- `Gate_SaffronCity_Route5_hns`
- `Gate_SaffronCity_Route6_hns`
- `GoldenrodCity_DepartmentStore_7FNight_hns`
- `Route30_House_hns`
- `Route30_MrPokemonsHouse_hns`

### gMapGroup_PlasticOxJohtoKanto (13)

- `CinnabarIsland_hns`
- `Route12_hns`
- `Route14_hns`
- `Route16_hns`
- `Route21_hns`
- `Route2_hns`
- `Route30_hns`
- `Route31_hns`
- `Route34_hns`
- `Route38_hns`
- `Route3_hns`
- `Route4_hns`
- `Route6_hns`

### gMapGroup_PlasticOxDungeons (1)

- `MtMoon_Cave_hns`

## Validation and future updates

The initial audit was executed twice with identical output; the named reporter
maps are candidates and Fortree, the current league and Frontier remain
protected. The companion skill was validated with `quick_validate.py`. No ROM
source changed, so no ROM build was needed.

After actual cleanup, rerun the audit, update these counts and groups, run
`git diff --check`, and check generator consistency with
`python3 plastic_ox/alpha/build_story.py --check`. For ROM changes, rebuild using
the build skill and run the affected story, league or travel checks. Record
existing generator drift separately from regressions introduced by cleanup.
