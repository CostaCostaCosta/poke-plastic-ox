# Wave 3 continuation notes (for finishing agent)

## Proven mechanisms (from waves 1c/2)
- Coord-warp portals work: {"type":"trigger","x","y","elevation":3,"var":"VAR_POX_PORTAL_GATE","var_value":"0","script":LBL}
  + scripts.inc body: LBL:: / warp MAP_DEST, x, y / waitstate / end
  (two-arg coords variant; single-arg = dest warp id; three-arg invalid)
- Doors need MB_ANIMATED_DOOR behavior on their metatile (fix_door_behaviors.py).
- enter_warp() tolerates mid-navigate firing; navigate() has avoid param;
  nav()/try_cross_up_columns helpers exist in walk_leg2.py / walk_leg3.py.
- After ANY data/maps json or layout bin edit: rm -f .map_version && make generated
  && make -j$(nproc) pokeemerald.gba (regenerates events.inc/connections.inc).
- mapjson DROPS connections whose dest constant isn't in constants/map_groups.h
  (native Hoenn names lack underscores: MAP_RUSTBORO_CITY not MAP_RUSTBOROCITY).

## Current wave-3 state (committed? NO - all uncommitted)
- Imported via plastic_ox/agent/import_wave3.py (run it anytime; idempotent):
  Gate_GoldenrodCity_Route35, Route35, NationalPark_Normal, Route36, Route37,
  EcruteakCity, Route38, Route16, Route24, Route25, Route25_BillsHouse.
- New tilesets imported: Ecruteak_City_Hns, Johto_NorthWest_Hns, VioletCity_Hns.
- Known-good walking chain ALREADY VERIFIED in earlier runs:
  r31_mouth -> azalea gate -> ilex -> (20,13)->R34 -> north seam -> GOLDENROD.
- BROKEN right now: IlexForest(20,13) coord -> R34. json coord exists with script
  `warp MAP_ROUTE34_HNS, 0` (lands r34 warp[0]). Suspect: r34 warp[0] tile may be
  unwalkable OR events.inc stale. Verify: make generated; grep events.inc; test.
- NOT yet wired: R38<->R119 portal (coord at R38 (1,21) elev4 exists in
  import_wave3.py PORTALS? NO - add: ("Route38_hns",1,21,"Route119_hns?",18,138)).
  R119 constant/dims: LAYOUT_ROUTE119 40x140, bottom open x16..20, left open y86.
- Fortree Return Stone coord added at FortreeCity (20,2) -> Pallet (10,4).

## Remaining tasks to finish wave 3
1. Fix Ilex->R34 step (see above).
2. Wire R38<->R119 portal (pick open tiles via live dump technique:
   POX_DEBUG_GRID env dumps collision/elev/beh grid at any navigate assert).
3. Author plastic_ox/demo/walk_leg3.py tail:
   r119_south -> traverse NORTH to fortree (native seam UP) -> Return Stone ->
   PASSED string. Reuse walk_leg2.py helpers (nav, edge_elev pattern).
4. Gates: both ROMs green; walk_leg3 passes twice; walk_demo passes once.
5. Update plastic_ox/alpha/REGION_PLAN.md Leg D/E notes with actual topology +
   portal usage. Single commit "alpha wave 3: Legs D+E stitched ...".

## Environment (verbatim)
export DEVKITARM=/home/eddie/devkitpro/opt/devkitpro/devkitARM
export DEVKITPRO=$HOME/devkitpro/opt/devkitpro
export CPATH=$HOME/toolchains/hostlibs/usr/include LIBRARY_PATH=$HOME/toolchains/hostlibs/usr/lib
make -j$(nproc) pokeemerald.gba
LD_LIBRARY_PATH="$HOME/.venvs/mgba311/lib:$HOME/.venvs/mgba311/lib64" \
  ~/.venvs/mgba311/bin/python plastic_ox/demo/walk_leg3.py

## Hard rules
- NPC movement: never WANDER_*; FACE_*/LOOK_* only. Delete CUTTABLE_TREE objects.
- Never edit generated files (events.inc, connections.inc, map_groups.h,
  region_map_sections.h, groups.inc) - regenerate instead.
- Vars only 0x4000-0x40FF. POX flags continue existing blocks.
- Demo pragmatism over authenticity: portals > seam archaeology.
