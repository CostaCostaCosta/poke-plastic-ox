# Wave 4/5 + Story — continuation playbook

State after wave 3 (commit 6c902ec92a): Legs A-E walkable via seams+portal
network. Deferred (documented in REGION_PLAN): NationalPark/R37/Ecruteak
map-load crash class; R14 scenic loop; MtMoon spur; Rustboro city interior
split (bridged by portal).

## Proven playbook per wave (repeat for 4 and 5)
1. `python3 plastic_ox/agent/import_wave<N>.py` — clone import_wave3.py,
   change MAPS / MUSIC / GROUP / PORTALS / NPC_DATA (json files) only.
2. Missing tilesets: copy pattern from "Re-adding tileset definitions" fix
   (see git log wave-3; struct name MUST be gTileset_<Name>).
   Then `python3 plastic_ox/agent/remap_metatile_behaviors.py`.
3. Pad any new _hns metatile_attributes.bin to 2048 B (zeros).
4. `python3 plastic_ox/agent/fix_door_behaviors.py` then build:
   rm -f .map_version && make generated && rm -f build/emerald/data/maps.o \
     build/emerald/data/event_scripts.o && make -j$(nproc) pokeemerald.gba
5. Author walk_leg<N>.py cloning walk_leg3.py; use nav()/enter_warp()/
   try_cross_up_columns(); portals at verified-open tiles (find via
   POX_DEBUG_GRID live dumps + offline BFS replication shown in probe
   patterns throughout this session's history).
6. Gates: leg harness x2 PASSED, walk_demo PASSED, both ROMs green.
7. REGION_PLAN substitutions, single commit.

## Map-load crash class (open bug)
NationalPark/R37/Ecruteak/Ilex-north crash on load: PC→0x1f8 lr 0xa4 in
LoadMapFromCameraTransition. Ruled out: callbacks (all NULL), flags, NPCs,
encounters, MAPSECs, attrs range. NEXT LEAD: byte-diff crashing maps'
MapLayout+tileset structs vs working Goldenrod_Hns; check src/tilesets.c
anim dispatch indexing; try hns repo's own field_control_avatar.c diff.
Workaround in tree: skip those maps; portals route around them.

## Wave 4 specifics (Legs F+G)
- Leg F: Ilex-south is Johto-side; Kanto Lavender chain per REGION_PLAN
  (R24/R25 spur exists imported). Simplest: portal from Route25 BillsHouse
  area -> Route7_hns -> LavenderTown_hns; Tower door retarget ->
  MAP_POKEMON_TOWER_1F (FRLG, present).
- Leg G: Lavender S <-> R12 <-> R21 water <-> CinnabarIsland_hns;
  Gym door -> MAP_CINNABAR_GYM; Mansion warp -> MAP_POKEMON_MANSION_1F.
- Water routes: walking harness can't surf — use portal pairs across water
  or mark water legs as surf-gated (document).

## Wave 5 (Legs H/I/J)
Same pattern; Indigo Plateau/FRLG League rooms already present natively.
End walk_leg5 at Champion door; final full-region harness = leg1..leg5 chained
(or single long harness) ending Hall of Fame door.

## Story phase (per STORY_TRIGGERS.md)
- gPlasticOxTriggersEnabled plumbing exists. Every coord_event gate uses the
  Special_PoxGate pattern; trainer battles via trainers.party Showdown ids
  TRAINER_PLASTIC_OX_* (start 855); five Eevee gifts (givemon SPECIES_EEVEE,5).
- Town-by-town headless tests on pokeemerald-triggers.gba using
  GBA(linker_map="pokeemerald-triggers.map") pattern from walklib.

## Gotchas that cost hours (do not repeat)
- mapjson silently DROPS connections whose dest constant isn't in
  constants/map_groups.h — verify emitted connections.inc after every json edit.
- events.inc/scripts.inc stale unless .o removed or make generated runs.
- enter_warp can exhaust taps exactly as transition fires -> post-loop state
  check added (keep it).
- hns coords-variant warps: two-arg form = x/y landing; three-arg invalid ids
  fail silently.
- Objects on 1-tile chokepoints block whole regions (check objects= list in
  navigate asserts; relocate NPC like Route30 YOUNGSTER fix).

## ADDENDUM: story-trigger investigation (session 2)
- Coord events verified LIVE-correct (position, elevation 3, trigger var,
  script pointer) on Oak's Lab / azalea gate — yet never fire on step-on,
  even with TRIGGER-var gating removed and trivial setvar bodies.
- Object A-interaction with retargeted starter ball also silent.
- Working coords for comparison: r116/fortree/plateau stones, r36 johto
  portal, gold(34,7), r36(21,21) — all fire reliably.
- Dead/alive split does NOT follow native-vs-imported (plateau_hns fires,
  lab_frlg doesn't). NEXT LEADS: (1) diff gMapHeader.events pointer chain
  between a firing map and the lab at runtime; (2) check
  RunScriptImmediatelyUntilEffect SCREFF mask handling for scripts whose
  first op is checkflag (working portals all lead with `warp`);
  (3) try a `warp`-first lab script (e.g., warp to a dummy interior and
  back) to see if effect-first ordering is the gate.
- Interim: Oak's Lab restored to native starter balls (SquirtleBall script
  retarget reverted). Starter scaffold preserved in git history
  (cc81fd59d0 + follow-ups).

## ADDENDUM 2: coord-fire investigation CLOSED for this demo (session 3)
Definitive live-RAM verification on Oak's Lab: coord event table correct at
runtime ((9,11) e=3, script ptr valid, trigger var correct), player steps
onto the tile with matching elevation — script still never runs. Tried:
var-gated (VAR_POX_PORTAL_GATE), TRIGGER_RUN_IMMEDIATELY (var=0), warp-first
body, setvar-first body, object A-interaction retarget. All silent.
Working coords (r116/fortree/plateau/r36/goldenrod/r35/blackthorn stones and
portals) use the identical emission path.
NEXT LEADS (for a real fix): (1) RunScriptImmediately implementation in this
expansion tree — verify it actually executes vs queues; (2) diff
field_control_avatar.c against upstream pokeemerald for the step-script
call chain; (3) test a coord on ANOTHER indoor FRLG map (e.g., rival house)
to isolate lab-specific vs indoor-specific.
INTERIM DESIGN: story beats that need step/interact triggers on hns/FRLG
interior maps should use DOOR-BUMP warps into purpose-built 1-tile "beat
rooms" (warp-first scripts proven to fire), or overworld object A-interactions
on OUTDOOR maps (proven firing). The starter beat ships as: Oak's Lab door
bump -> lab interior -> starter ball objects (native, working).
