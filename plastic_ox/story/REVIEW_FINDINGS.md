# Story review findings — Plastic Ox

A consolidated triage of what the town/route review found while writing
`plastic_ox/story/locations/`. Every item below was checked against the
checkout (map JSON, scripts, constants, tileset binaries) or is explicitly
attributed to the note that documents it. Each note carries the full context,
coordinates, and suggested fix.

Priority: **P0** blocks mainline progression or enables a sequence break;
**P1** breaks a stated story rule; **P2** is dead content, placeholder text, or
wiring that no longer resolves.

**Status (2026-11-11):** a scoped fix pass addressed most P0/P1 items and
several P2 wiring/text issues. What shipped, what was verified in-emulator, and
what remains are in
[`plastic_ox/agent/REVIEW_FIX_PASS_2026-11-11.md`](../agent/REVIEW_FIX_PASS_2026-11-11.md).
The sections below stay as the original review record.

## P0 — progression blockers and sequence breaks

| # | Where | Finding | Evidence |
| --- | --- | --- | --- |
| 1 | Ilex Forest north exit | The north door metatile (`0x3B`) has no attribute: `ilex_forest_hns` has 60 metatiles but 59 attribute entries (118 B). The exit does not fire, so the forest is one-way in. Because `FLAG_POX_STORY_ILEX` (the forest conversation) opens Route 2 north, the live mainline cannot reach Rustboro. | `data/tilesets/secondary/ilex_forest_hns/metatiles.bin` (960 B), `metatile_attributes.bin` (118 B) |
| 2 | Dark Cave South Side | Both mouths use secondary metatiles `306`/`307`, but the cave tileset has 308 metatiles and 306 attributes (612 B), so neither exit has behavior. The cave is traversable inside; the doors are dead. Same padding bug family as `HANDOFF_WAVE4.md`. | `data/tilesets/secondary/cave_default_hns/` |
| 3 | Pallet ↔ Route 21 ↔ Cinnabar | Pallet's south edge is surf-elevation water and the Route 21 North/South/Cinnabar seams are walkable. Surf is granted as `ITEM_SURF_KEY` with Fuji, which is exactly when the intended Route 8 → Underground → Route 7 → Route 103 road opens — so the player can skip it. Cinnabar's north beach is the only ungated edge (`PoxRegion_Arrival_CinnabarIsland_Frlg` is an empty stub). | `route21-north-frlg.md`, `cinnabarisland-frlg.md` |
| 4 | Route 44 gate | There is no badge check. `PoxRegion_rustboro_route44_a` does `goto_if_unset FLAG_POX_TRIGGERS_ENABLED, ..._Open` and then *falls through* to the same `_Open` label; both `_Closed` arms are unreachable. The gate hiker, the Mt. Moon warp, and the `PoxMoon_EnterFromRoute44` trigger all sit on `(68,13)`, so a blocking NPC there could also make Mt. Moon unenterable. | `data/scripts/plastic_ox_region.inc:191-203` |
| 5 | Blackthorn Gym | The city has two warps (shared Center/Mart) and no Gym door. `Pox_ClairGuide` teleports the player into a room laid out on `LAYOUT_RUSTBORO_CITY_GYM`, with zero Gym trainers and an NPC exit. Access is checked against `FLAG_POX_STORY_SPACE_CENTER` (the Saffron seal), not badges. | `blackthorncity-hns.md` |
| 6 | Victory Road arrival | The entry landing tile `(27,48)` sits directly above the return band `(25..28,49)` wired to `PoxLeague_Return`, so one step south on arrival ejects the player back to the Ecruteak gatehouse. | `data/maps/PlasticOx_VictoryRoad/map.json` warp/coord events |
| 7 | Ecruteak and Goldenrod rooms | The v7 rooms `PlasticOx_MortyGym`, `PlasticOx_DanceTheater`, and `PlasticOx_WhitneyGym` have **0 warps**. The town doors open the legacy HNS gyms, which contain their own `Pox_Morty` / `Pox_Whitney` and award badges 2 and 3: so each badge is winnable twice, and the authored v7 rooms are unreachable. `EcruteakCity_Gym_hns` alone carries 107 warp events. `Route38_hns` is orphaned behind the League-checkpoint gatehouse, whose warp index it targets. | `ecruteakcity-hns.md`, `goldenrodcity-hns.md`, `route38-hns.md` |
| 8 | Route 20 West | Arrival lands at `(48,14)`, and the tile one step north `(48,13)` fires `PoxRegion_cinnabar_sea_b`, which warps straight back to Cinnabar `(22,10)`. A player who moves north from the arrival point is bounced out of the Seafoam approach; the `_Closed` arm is unreachable because the Mansion flag is already set. | `data/maps/PlasticOx_Route20West/map.json`, `plasticox-route20west.md` |
| 9 | Ecruteak east → Route 119 | The canonical stage-5 leg does not exist. `EcruteakCity_hns` has one connection (south → Route 37); the only map referencing `MAP_ROUTE119` is `Route118` (a Hoenn chain). The Fortree gate is closed until `FLAG_POX_STORY_WEATHER`, so the Weather Institute is not reachable from the Johto side. | `route119.md` |

## P1 — story-rule breaches

| # | Where | Finding |
| --- | --- | --- |
| 1 | Burned Tower / Weather Institute | NPCs say "convergence" aloud (`plastic_ox_story.inc:827`, `:873`; `PlasticOx_BurnedTower/scripts.inc:17`). It is a design term; the dialogue rule is to keep it out of characters' mouths. |
| 2 | National Park | Every park/gate NPC points at a Contest Pass "in the tournament in the Saffron Underground", but Saffron is sealed until the Space Center. The pass is actually awarded by `PoxTournament_Host` round one, gated on `FLAG_BADGE04_GET`. |
| 3 | Fortree | `PoxRegion_Arrival_FortreeCity` sets `FLAG_KECLEON_FLED_FORTREE` on entry, so the east-walkway Kecleon is pre-cleared and the roadblock is invisible. The roadblock belongs on the east exit (not the Gym) and must clear only on badge 4. |
| 4 | Cherrygrove | The house-B boy says "merged region" — the premise stated aloud in the first town; the better-written `CherrygroveCity_EventScript_GuideGent` is dead code. |
| 5 | Indigo Plateau | All five League rooms share the post-win line "That was a battle to remember!", and Bill's intro is friendly small talk instead of the required flat `CHAMPION BILL would like to battle`. The Hall guide reuses `OBJ_EVENT_GFX_BILL`, so two Bill sprites stand in one building. |
| 6 | Victory Road | All six Lv.58 trainers share one defeat line and one after-line; the only heal is on the optional western terraces while the advice house is on the direct climb. |
| 7 | All Gyms | The badge-tier checks do not exist. `CheckGoldenrodGymPURules`, `CheckEcruteakGymNURules`, `CheckFortreeGymRURules`, `CheckCinnabarGymUURules`, `CheckMossdeepGymUUBLRules`, `CheckSaffronGymOURules`, and `CheckBlackthornGymOURules` all `return CheckRustboroGymLittleCupRules()` — one Little Cup legality check (sleep/Thunder Wave/Baton Pass bans) applied to every badge. The OU/UU roster rules described in the story bible are not enforced anywhere. | `src/field_specials.c:150-173` |

## Design decisions applied (2026-11-11)

- **Route 24 Rocket: approved.** The lost grunt stays as an incidental Rocket
  encounter; he is not one of the three story beats. `route24-hns.md` and the
  story bible's pacing rule now say so.
- **Snorlax on Route 36: approved.** Keep both the visible block and the
  `FLAG_POX_REACHED_FORTREE` seam lock.
- **Kecleon: east exit, not the Gym.** It blocks the Fortree walkway to Route
  110, refuses before badge 4, reveals and flees on the first interaction
  afterward, and never affects Gym access. `fortreecity.md` and
  `plastic_ox_map_v7.md` now specify this.
- **Kimono girls: improve.** Their five battles and all dialogue are in scope
  for this pass (better teams, distinct voices, post-battle lines, the Eevee
  gift framed as fostering a dance partner).

## P2 — dead content, placeholders, and unresolved wiring

**Dialogue and actors**
- Route 35: 12 talker objects alternate between exactly two lines (6 + 5 of 12 strings), three of them `OBJ_EVENT_GFX_POKE_BALL` props with flavour text and no item.
- Route 37: both twin trainers use `TRAINER_PLASTIC_OX_JOHTO_ANN_ANNE`, so one sister never battles; the city-sign script has no object.
- Route 45: zero encounters, trainers, or items; eight hikers run the same `MSGBOX_SIGN` script and do not face the player.
- Mossdeep cluster: 14 dead Magma/Aqua objects (including Maxie and Tabitha) with `script 0x0`; 19 NPCs share one `Pox_FacilityWorker` line.
- Battle Frontier: 25-NPC square is unrewritten Emerald; two Maniacs are byte-identical; ReceptionGate's Scott has `script 0x0`.
- Route 110: two objects stacked on `(34,54)`, a script-less Birch at `(9,79)`, a cyclist named Jasmine, and vanilla Lv.6–16 trainers at a stage-6 route.

**Items and objects**
- `PoxBurnedTower_TM12` awards `ITEM_BIG_PEARL`.
- Route 115 `(18,7)` is flagged as TM Focus Punch but contains a Nugget; Meteor Falls `(2,4)` is flagged as TM Iron Tail and also contains a Nugget.
- Route 25: two Misty objects, duplicated Eusine, `TRAINER_PLASTIC_OX_ROUTE25_PAT` with no battle, a `CUTTABLE_TREE` wired to a talk script; the cottage fossil chain hands out Kanto fossils before Mt. Moon.
- `Route25_SeaCottage_Frlg` is an intact duplicate of Bill's cottage (teleporter, Clefairy, SS Ticket quest) on the legacy FRLG Kanto chain.

**Maps and wiring**
- `GoldenrodCity_DepartmentStore_7FNight_hns` has no inbound warp anywhere; it is a complete duplicate of the day roof, though the engine has real time-of-day.
- `PlasticOx_WhirlIslands`: 0 warps, 0 coord events, no inbound warp, both objects hidden by `FLAG_POX_HIDE_STORY_NPCS` (set in `src/new_game.c`, never cleared). Decide whether Lugia needs a home before retiring it.
- Retired but still populated and still in the wiki: `Route2_hns`, `Route3_hns`, `Route4_hns`, `Route14_hns`, `Route16_hns`, `Route31_hns`, `Route34_hns`, `Route38_hns` (per `region_v7.py`'s `retired` set). Route 34 is a one-way trap: Route 116 declares an up connection and a dangling warp to warp index 1, but Route 34 has 0 warps and no exit.
- `EcruteakCity_Gym_hns` carries 107 warp events and a second `Pox_Morty`; the League checkpoint lives in the Route 38 gatehouse whose west warp is dangling.
- `PlasticOx_BlaineGym` and `PlasticOx_Mansion` are orphaned (0 warps, nothing routes to them); live play uses `CinnabarIsland_Gym_Frlg` and the FRLG Mansion floors, so the authored UU gate is unreachable. `FLAG_DEFEATED_BLAINE` is never set, leaving the FRLG gym doors permanently quiz-gated after a win.
- Entei is gated by the Mansion door only, not by the archives, so it is catchable before the step-9 reveal; the reachable Mansion still carries vanilla "Mew gave birth to Mewtwo" diaries.
- `CinnabarIsland_hns` is a second, unreferenced Cinnabar town map (0 warps); Blaine hands out `ITEM_HM04`/`ITEM_HM06` while field use is actually gated by `ITEM_STRENGTH_KEY`/`ITEM_ROCK_SMASH_KEY`.
- Route 8, Route 19, and Route 21 trainer parties are inside `.if IS_FRLG` and compile out on the Emerald build, leaving those roads with no battles.
- `Route16_hns` is registered but unreachable (0 warps/connections/coords, no encounter entry); the live Kanto Route 16 is `Route16_Frlg`, whose Cycling Road gatehouse keys the pedestrian stop to `FLAG_GOT_BICYCLE`, aliased to `0` in this build — the check cannot survive one map load.
- Goldenrod ships duplicate reward wiring: two identical `Pox_SquirtBottle` dispensers (street `(27,15)` and Flower Shop `(2,4)`), two identical Game Corner prize desks, a `MauvilleCity` coin clerk, and a Kimono guard who calls the switch chamber closed while the `(12,10)` stair is open and stocked before badge 2.

## What is already in good shape

- The badge spine, reveal ladder, and flag contract in `STORY_TRIGGERS.md` match the notes; `check_story_notes.py` finds no unknown identifiers in 61 notes.
- The seven fruit trees are not broken: `plastic_ox_berry_trees.inc` generates their `PlasticOx_BerryTree_*` labels through the `pox_fruit_tree` macro and `data/event_scripts.s` includes it. The earlier "missing label" claim was a source-scan false positive; `check_map_refs.py` now expands the macro.
- Lavender's Rocket II, Fuji, and the Cinnabar directions are implemented coherently; the harbour is correctly reserved for postgame.
- Seafoam/Routes 20 are genuinely directed; Silph, the League rooms, and the Mansion have real scripts to build on.
- The wiki generator and story-note validator now run in CI, so this list cannot silently rot.

## Suggested next order

1. Tile-attribute padding for Ilex and Dark Cave (unblocks the mainline).
2. Cinnabar north-beach gate on `FLAG_POX_STORY_MANSION` (closes the Surf bypass).
3. Route 44 gate repair and Blackthorn Gym door.
4. Ecruteak room warps and the Route 119 west link.
5. Story-rule wording fixes ("convergence", Fortree Kecleon, park contest pointer).
6. Placeholder dialogue sweeps (Route 35, Route 110, Route 45, Mossdeep, Frontier) and the Kimono girls' teams/dialogue.
7. Retire-or-wire pass for the retired maps, the night roof, Whirl Islands, and the duplicate cottage.