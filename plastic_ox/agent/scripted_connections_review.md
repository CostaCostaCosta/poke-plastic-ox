# Plastic-Ox scripted connection review

Date: 2026-09-18
Scope: `region_v7.TRAILS`, the pinned ports in `region_ports.json`, and the
explicit Underground Path / Ilex return portals emitted by `region_v7.py`.

## Changes made

* An explicit allowlist identifies the 25 reviewed outdoor portals with a
  broad throat. Those endpoints derive a bounded trigger set from the map's
  actual walkable component: the center lane and at most one immediately
  adjacent lane on either side (maximum width three). A lane is accepted only
  when both its portal tile and approach tile are passable, connected to the
  local component, and free of object, warp, or reserved-port coordinates.
  Cave/facility/one-tile endpoints stay center-only, avoiding invisible
  teleportation through a doorway or NPC.
  The width cap is deliberate: lanes beyond ±1 remain ordinary local terrain
  until a future screenshot-backed review proves they are part of the same
  throat; they are not silently redirected by this change.
* Re-running the generator removes old trigger events for that endpoint before
  adding the current set, preventing duplicate coordinate events.
* A canonical mouth containing an intentional object/warp blocker never gains
  side lanes, so Route 44's Mt. Moon gate cannot be bypassed.
* Helper return mouths without a regional `ANCHORS` entry use their approach
  as the component seed; this covers the Underground Path return endpoints.
* `cinnabar_sea_a` was corrected from an ocean tile `(23,10)` to the adjacent
  land mouth `(22,10)` with approach `(21,10)`. The prior portal required a
  Surf transition before its coordinate trigger could run; the corrected
  geometry is an ordinary land-to-dock portal and preserves the Mansion gate.

No story requirement was removed. Closed endpoints still execute the same
`requires` list and return to the local approach tile. Intentional cave,
facility, house, Seafoam, Dark Cave, Ilex, and gatehouse warps remain separate.
Native camera seams are outside this review.

## TRAILS inventory and conclusion

All 32 entries are intentional discontinuous portals (not camera seams), so
their route/cave/facility transitions remain scripted. The lane-width logic is
shared by both directions; a one-way exception remains `route45_route46_b`, as
encoded by the source generator.

| ID | Transition | Requirement |
|---|---|---|
| `rustboro_route44` | RustboroCity → Route44_hns | none |
| `route44_moon` | Route44_hns → MtMoon_Cave_hns | none |
| `moon_route33` | MtMoon_Cave_hns → Route33_hns | `FLAG_POX_STORY_MTMOON` |
| `route33_goldenrod` | Route33_hns → GoldenrodCity_hns | none |
| `goldenrod_route35` | GoldenrodCity_hns → Route35_hns | none |
| `route35_park` | Route35_hns → NationalPark_Normal_hns | none |
| `park_route36` | NationalPark_Normal_hns → Route36_hns | none |
| `route37_ecruteak` | Route37_hns → EcruteakCity_hns | none |
| `ecruteak_route119` | EcruteakCity_hns → Route119 | `FLAG_BADGE03_GET` |
| `route119_fortree` | Route119 → FortreeCity | `FLAG_POX_STORY_WEATHER` |
| `fortree_route110` | FortreeCity → Route110 | `FLAG_BADGE04_GET` |
| `route36_shortcut` | Route36_hns → Route110 | `FLAG_POX_REACHED_FORTREE` |
| `route110_lavender` | Route110 → LavenderTown_hns | `FLAG_BADGE04_GET` |
| `lavender_route8` | LavenderTown_hns → Route8_Frlg | `FLAG_POX_STORY_FUJI` |
| `route8_saffron` | Route8_Frlg → SaffronCity_hns | `FLAG_POX_STORY_SPACE_CENTER` |
| `route7_saffron` | Route7_hns → SaffronCity_hns | `FLAG_POX_STORY_SPACE_CENTER` |
| `route7_route103` | Route7_hns → Route103 | `FLAG_POX_STORY_FUJI` |
| `oldale_route103` | OldaleTown → Route103 | `FLAG_POX_STORY_FUJI` |
| `route103_cinnabar` | Route103 → CinnabarIsland_Frlg | `FLAG_POX_STORY_FUJI` |
| `cinnabar_sea` | CinnabarIsland_Frlg → PlasticOx_Route20West | `FLAG_POX_STORY_MANSION` |
| `sea_mossdeep` | PlasticOx_Route20East → MossdeepCity | `FLAG_POX_STORY_MANSION` |
| `mossdeep_route19` | MossdeepCity → Route19_Frlg | none |
| `route19_saffron` | Route19_Frlg → SaffronCity_hns | `FLAG_POX_STORY_SPACE_CENTER` |
| `saffron_route5` | SaffronCity_hns → Route5_hns | `FLAG_POX_STORY_SPACE_CENTER` |
| `route5_route115` | Route5_hns → Route115 | `FLAG_POX_STORY_SPACE_CENTER` |
| `meteor_blackthorn` | MeteorFalls_1F_1R → BlackthornCity_hns | `FLAG_POX_STORY_SPACE_CENTER` |
| `blackthorn_route45` | BlackthornCity_hns → Route45_hns | `FLAG_POX_STORY_SPACE_CENTER` |
| `route45_route46` | Route45_hns → Route46_hns | `FLAG_POX_STORY_SPACE_CENTER` |
| `ecruteak_league` | EcruteakCity_hns → VictoryRoad_1F | all eight badge flags |
| `victory_indigo` | VictoryRoad_1F → IndigoPlateau_hns | all eight badge flags |
| `lavender_harbor` | LavenderTown_hns → PlasticOx_Harbor | `FLAG_SYS_GAME_CLEAR` |
| `harbor_frontier` | PlasticOx_Harbor → BattleFrontier_OutsideWest | `FLAG_SYS_GAME_CLEAR` |

Additional scripted portals reviewed: the three-tile Underground Path return
mouths, Ilex north gate, and their preserved local warps. They retain their
existing story gate (`FLAG_POX_STORY_ILEX` for the Ilex north gate) and are not
converted into regional seams.

## Verification

Parent should regenerate the region patch with:

```sh
cd /home/eddie/repos/poke-plastic-ox
PYTHONPATH=plastic_ox/alpha python3 plastic_ox/alpha/apply_region.py > /tmp/plastic-ox-region.patch
```

After applying that patch and building the ROM, run the continuous route walk
and the prerequisite-denial checks in the configured mGBA environment:

```sh
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_region_walk.py early
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_region_walk.py central
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_region_walk.py underground
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_region_walk.py coast
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_region_walk.py north
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_region_walk.py postgame
```

Also run `plastic_ox/demo/test_story.py` and the map-port audit before the
full build. Inspect both directions of every changed portal, including the
three trigger lanes where present, and verify no blocked shoulder or unrelated
object/warp was consumed.
