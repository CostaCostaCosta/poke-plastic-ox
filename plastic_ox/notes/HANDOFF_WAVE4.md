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

## Map-load crash class (CLOSED — wave 4 session)
The "crash" was THREE stacked artifacts, no ROM data bug:
1. **Harness PC polling**: reading `g.core.cpu.pc`/`.lr` via mgba-python
   CORRUPTS emulation — it "crashes" ANY map, including proven-working ones
   (Route35 control test). Never poll cpu state in harnesses; use
   state()/vblank-counter (gMain+0x20) oracles instead.
2. **Mid-transition reads**: a warp updates the saveblock location at
   ApplyCurrentWarp (early) but InitMapLayoutData fills the grid only at the
   end of the transition (~200f). Reads in that window return the previous
   map's grid / MAPGRID_UNDEFINED (1023); movement is engine-locked; screens
   are mid-fade black. walklib.wait_warp_complete() (grid width match) and
   wait_grid_ready() exist for this — enter_warp() now self-waits.
3. **Timing-perturbation sensitivity**: printf instrumentation or the log
   callback shifts the race; instrumented builds "pass" runs that then fail
   clean. Never trust a fix verified only under instrumentation.
True engine-side residual: the warp destination can race (cave-mouth misfire
out the wrong exit; address-layout sensitive — leg1 failed at HEAD too after
the wave-4 address shift). enter_warp/leg1 retry on misfire. If it bites
again: gdb via `mgba-qt -g` (port 2345) + xdotool-less driving is UNSOLVED;
the IRQ-lr watchdog (patch IntrMain to stash lr @0x03007FF0) is the best
ROM-side trap built so far.
Park/corridor status: NationalPark loads and renders correctly; the R36 park
spur, R37, Ecruteak, R7, Lavender, Cinnabar chain is walkable end-to-end
(walk_leg4.py; full chain walk_region.py = leg1..leg5 REGION DEMO PASSED).

## Wave 4 specifics (Legs F+G) — SHIPPED (see REGION_PLAN Leg F/G)
- Entry: "Kanto gate" portal EcruteakCity_hns (15,31) ⇄ Route7_hns (4,25)
  (the R24/R25 spur has no walkable entry). All portal/warp tiles were
  verified against the grid with the ENGINE's bit layout: collision =
  bits 10-11, elevation = bits 12-15 (walklib.collision_at returns
  (collision, elevation) in that order — do not "fix" it again).
- Lavender⇄Cinnabar crosses the surf-gated water directly; R12⇄R21 seam
  stays wired for post-surf.
- Tower/Gym interior warps DEFERRED: the interiors load to a black screen
  with garbage saveblock coords (native FRLG interior load issue — next
  lead: compare with a working FRLG interior warp, e.g. the player house).
- import_tilesets_auto.py had a catastrophic append bug (wrote whole-file
  content per missing tileset → exponential duplication); fixed to batch
  writes. If tileset headers ever look doubled, restore the four files from
  git and re-run the fixed tool.

## Wave 5 (Legs H/I/J)
Same pattern; Indigo Plateau/FRLG League rooms already present natively.
End walk_leg5 at Champion door; final full-region harness = leg1..leg5 chained
(or single long harness) ending Hall of Fame door.

## Story phase (per STORY_TRIGGERS.md)
- gPlasticOxTriggersEnabled plumbing exists. Every coord_event gate uses the
  Special_PoxGate pattern; trainer battles via trainers.party Showdown ids
  TRAINER_PLASTIC_OX_* (start 855); five Eevee gifts (givemon SPECIES_EEVEE,5).
- Town-by-town headless tests now use pokeemerald.gba and pokeemerald.map.

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
