# RUN6_GOLDENROD_CITY_V1_REPORT — Goldenrod City overworld

Run: prime-agent RUN 6 of the Goldenrod-area story pass (`plastic_ox/agent/STORY_PASS_PRIME_PROMPT.md`).
Branch `codex/metamon-trainer-ai`, pokeemerald-expansion 1.16.3. **All changes left uncommitted.**
ROM after this run: `pokeemerald.gba`, ROM region **28,287,796 B / 32 MiB = 84.30 %** (build exit 0).

---

## Goal 1 — Team Rocket NPCs removed from Goldenrod City

`data/maps/GoldenrodCity_hns/map.json`: **10** object events with `OBJ_EVENT_GFX_ROCKET_M` / `OBJ_EVENT_GFX_ROCKET_F` deleted:

| tile | script (deleted) |
|---|---|
| (27,30) | `GoldenrodCity_EventScript_Npc3` (ROCKET_F) |
| (43,26) | `GoldenrodCity_EventScript_Npc5` |
| (43,25) | `GoldenrodCity_EventScript_Npc6` |
| (23,22) | `GoldenrodCity_EventScript_Npc10` |
| (18,22) | `GoldenrodCity_EventScript_Npc11` (was `LOCALID_GOLDENROD_ROCKET_SCOUT`) |
| (43,13) | `GoldenrodCity_EventScript_Npc13` |
| (45,16) | `GoldenrodCity_EventScript_Npc14` |
| (12,35) | `GoldenrodCity_EventScript_Npc15` |
| (38,14) | `GoldenrodCity_EventScript_Npc16` |
| (28,14) | `GoldenrodCity_EventScript_Npc17` |

`data/maps/GoldenrodCity_hns/scripts.inc`: the ten dead script + text blocks were deleted, together with
`GoldenrodCity_EventScript_Npc1`/`Npc2`, which were already unreferenced before this run (no object or bg event
pointed at them). Object count 21 -> 14. Verified no `ROCKET` graphics id and no `FLAG_HIDE_GOLDENROD_ROCKET_SCOUT`
or `LOCALID_GOLDENROD_ROCKET_SCOUT` reference remains in `data/`, `include/` or `src/` (the local id define in
`include/constants/map_event_ids.h` is now unused and was left alone).

Rocket presence is not part of the current story stage, so no one-for-one replacement was forced. Three ordinary
citizens were added where the removals left the street noticeably empty, all with unique dialogue:

| tile | graphics | script |
|---|---|---|
| (44,40) outside the BIKE SHOP | `OBJ_EVENT_GFX_CYCLING_TRIATHLETE_F` | `GoldenrodCity_EventScript_Npc20` |
| (23,22) Radio Tower plaza | `OBJ_EVENT_GFX_WOMAN_2` | `GoldenrodCity_EventScript_Npc21` |
| (12,35) south-west block | `OBJ_EVENT_GFX_OLD_MAN_HNS` | `GoldenrodCity_EventScript_Npc22` |

## Goal 2 — unique dialogue for every remaining city NPC and sign

`data/maps/GoldenrodCity_hns/scripts.inc` was rewritten. The old repeated line
("Roads keep ending somewhere they didn't used to.") and the on-the-nose sign jokes are gone. 10 NPCs + 8 signs
= **18 texts, all distinct**. `Pox_WhitneyGuide`, `Pox_ParkRoad` and `Pox_SquirtBottle` were not touched.

| label | tile | text |
|---|---|---|
| Npc4 | (17,36) | "My knees quit on the third floor of the DEPT. STORE. Seven floors, and not one bench." |
| Npc7 | (39,22) | "The RADIO TOWER plays a POKéMON LULLABY at eight sharp. I fall asleep before the news." |
| Npc8 | (30,21) | "The train to the coast runs twice a day. I just like watching it pull out." |
| Npc9 | (20,25) | "Downhill to the harbor is ten minutes. Getting back up is an hour." |
| Npc12 | (7,23) | "I buy flowers here for my wife. She says they smell like the town we grew up in." |
| Npc18 | (30,39) | "The store basement sells bitter herbs. The rooftop sells nothing but sky." |
| Npc19 | (39,15) | "I do my shopping before noon, while the GYM crowd is still indoors." |
| Npc20 | (44,40) | "A shipment of bikes came up from HOENN this morning. Good frames, but the MACHS are pricey." |
| Npc21 | (23,22) | "They read out the GYM results on the evening broadcast. My son listens for his own name." |
| Npc22 | (12,35) | "I walk this block every day. The shops change hands, the pavement never does." |
| Sign1 | (12,22) | "GOLDENROD CITY / Walk your bicycles downtown." |
| Sign2 | (30,30) | "DEPT. STORE AHEAD / Elevator service to all floors." |
| Sign3 | (26,22) | "UNDERGROUND / Goldenrod Tunnel - west entrance." |
| Sign4 | (19,13) | "ROUTE 35 - NORTH / Through the gatehouse." |
| Sign5 | (19,38) | "POKéMON CENTER / Heal your team and move on." |
| Sign6 | (43,39) | "BIKE SHOP / New and used. Trade-ins welcome." |
| Sign7 | (41,13) | "GOLDENROD GYM / LEADER: WHITNEY / She never lets up, and never brags." |
| Sign8 | (45,12) | "FLOWER SHOP / Cut flowers, seeds and berries." |

The bike-shop neighbour states the Hoenn bike shipment as a plain trade fact. Region-merge references are kept
light and varied (the harbor climb, the Hoenn shipment); no two NPCs share a line. Radio Tower interiors are a
separate run and were not touched.

## Goal 3 — north exit now crosses the gatehouse

The bare coordinate teleport is gone. The topology now matches the source game and the
`~/repos/pokehns-expansion` donor (`Gate_GoldenrodCity_Route35_hns`: city doors (33,7)/(34,7) -> gate warp 0,
gate warps (7,9)->city / (7,1)->Route 35, route doors (13,48)/(14,48) -> gate warp 1).

`data/maps/GoldenrodCity_hns/map.json`
* added warp events (33,7) and (34,7) -> `MAP_GATE_GOLDENROD_CITY_ROUTE35_HNS` `dest_warp_id 0`
* removed the coord trigger at (33,9) running `PoxRegion_goldenrod_route35_a`

`data/maps/Gate_GoldenrodCity_Route35_hns/map.json`
* added warp events (7,9) -> `MAP_GOLDENROD_CITY_HNS` `dest_warp_id 14` (the (33,7) door) and (7,1) ->
  `MAP_ROUTE35_HNS` `dest_warp_id 0` (the (13,48) door). The map previously had **no** warps and was never entered.

`data/maps/Route35_hns/map.json`
* added warp events (13,48) and (14,48) -> `MAP_GATE_GOLDENROD_CITY_ROUTE35_HNS` `dest_warp_id 1`
* removed the coord trigger at (16,47) running `PoxRegion_goldenrod_route35_b`

`data/scripts/plastic_ox_region.inc`
* deleted the six now-dead portal scripts `PoxRegion_goldenrod_route35_a{,_Open,_Closed}` and
  `PoxRegion_goldenrod_route35_b{,_Open,_Closed}` (42 lines)
* retargeted the Route 35 wayfinding sign text to `PoxRegion_goldenrod_route35_b_Text`
  = "GOLDENROD CITY - SOUTH / Through the gatehouse."

`data/maps/Gate_GoldenrodCity_Route35_hns/scripts.inc`: the three gatehouse NPCs previously repeated the same
city line; each now has unique text (officer: "Gate's open and the road is clear. Mind the ledges once you're out
there."; woman: "I cut through this gatehouse on my way to the park. It saves me the hill."; fisherman: "The water
is a long walk from here. I carry the rod anyway, just in case.").

**Story gating:** these two trails carry no story requirements — `plastic_ox/alpha/region_v7.py` `TRAILS` declares
`('goldenrod_route35', ..., [])` and `('route33_goldenrod', ..., [])`, so their `PoxRegion_*` scripts had only the
`FLAG_POX_TRIGGERS_ENABLED` test and the `_Closed` branch was unreachable (execution falls straight into `_Open`).
There was therefore no closed-fallback to preserve for this gate, and the door path is now the only north exit.
`PoxRegion_ClosedText` and the closed-fallback machinery are untouched for every other trail.

## Goal 4 — south exit is a road-mouth seam, not a mid-map teleport

`data/maps/GoldenrodCity_hns/map.json`: the single coord trigger at (32,45) was replaced by **four** triggers
covering the whole south road mouth at (32,45), (33,45), (34,45), (35,45) — previously only the leftmost lane
transitioned and the other three lanes were dead ends at the map edge.

`data/maps/Route33_hns/map.json`: the single coord trigger at (0,22) was replaced by **three** triggers at
(0,22), (0,23), (0,25) — the whole west road mouth. (0,24) is deliberately skipped because the Route 33
wayfinding sign object occupies that lane.

`data/scripts/plastic_ox_region.inc`: arrivals now land on the destination road mouth:
* `PoxRegion_route33_goldenrod_a` (Route 33 -> city) lands **(33,44)**, the centre lane of the city mouth
* `PoxRegion_route33_goldenrod_b` (city -> Route 33) lands **(1,23)**, on the Route 33 road band
* the unreachable `_a_Closed` return was moved off the now-triggered (0,23) to (1,23) so no fallback can bounce
* sign texts made unique: city side "ROUTE 33 - SOUTH / Follow the road down.", route side
  "GOLDENROD CITY / Follow the road up into town."

A real map connection is not possible here: Route 33's north edge (y=0..10) and Goldenrod City's east edge are
solid wall, so a `down`/`left` connection has no walkable receiving tile. The aligned portal pair is the
project's established convention for these region trails (`plastic_ox/alpha/region_v7.py` `LANE_PORTALS`) and is
what the prompt allows. Facing on arrival is the engine's own rule for `MB_NORMAL` landing tiles (DOWN), i.e. the
project's convention in `WARP_PLAYTEST_V1_REPORT.md`.

## Extra fix found by the emulator pass

The gatehouse policeman stood at (3,5), sealed inside a walled alcove (the walkable room is x=5..9, y=2..9), so no
player could ever reach him — a pre-existing import defect, not caused by this run. He was moved to **(5,8)**
inside the room, beside the city-side door lane, keeping `MOVEMENT_TYPE_FACE_RIGHT`. The other two gatehouse NPCs
((5,3) and (9,4)) were already reachable.

---

## Verification

### Build
`DEVKITARM=~/devkitpro/opt/devkitpro/devkitARM make -j8` after each batch — **exit 0, zero errors** every time.
Only the pre-existing warning `asm/macros/event.inc:322 explicit waitstate follows implicit waitstate` (from
`data/scripts/plastic_ox_story.inc:1881`) appears; it is unrelated to this run.

### Static / ROM-level checks (`plastic_ox/demo/test_run6_goldenrod.py static`)
* 0 Rocket graphics ids in the city map
* every object-event and bg-event script label in Goldenrod City, the gatehouse, Route 33 and Route 35 resolves to a
  symbol in the linked ROM (no dead script references)
* all **21** NPC/sign text labels (18 city + 3 gatehouse) read back from the **built ROM** (`nm` address + ROM
  bytes up to the 0xFF EOS) are pairwise distinct
* `GoldenrodCity_hns/map.json` still round-trips `json.dumps(..., indent=2)+"\n"` exactly, so
  `plastic_ox/alpha/goldenrod.py` regeneration stays idempotent; the gatehouse keeps its original `indent=4`
  formatting

### Map audits
* `python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py /home/eddie/repos/poke-plastic-ox`
  -> `audited 99 HNS layouts` / `HNS layout metadata and asset bounds: PASS`. No new findings.
* `python3 .agents/skills/plastic-ox-map-baseline/scripts/audit_map_baseline.py` for `GoldenrodCity_hns`,
  `Gate_GoldenrodCity_Route35_hns`, `Route33_hns`, `Route35_hns`:
  * `GoldenrodCity_hns`: only the four intended `PoxRegion_route33_goldenrod_b` road-mouth triggers and the
    `PoxRegion_Arrival_GoldenrodCity_hns` on-transition script
  * `Gate_GoldenrodCity_Route35_hns`: `baseline: no automatic triggers`
  * `Route33_hns`: only the three intended `PoxRegion_route33_goldenrod_a` road-mouth triggers
  * `Route35_hns`: only the untouched `route35_park` trigger at (17,7)
  These are the region portal convention, i.e. informational, not defects.

### mGBA playtests (`~/.venvs/mgba311/bin/python`, `plastic_ox/demo/test_run6_goldenrod.py`)
North gatehouse, both door lanes, four legs each (`gate`):
```
STAGE north gate door 33: (76,8) (76,8) at (7,9)      -> landed on the gatehouse south door
STAGE gate north door:    (77,12) (77,12) at (13,48)  -> out onto Route 35 at the gate doors
STAGE route 35 gate door: (76,8) (76,8) at (7,2)      -> back inside the gatehouse
STAGE gate south door:    (77,11) (77,11) at (33,8)   -> back into the city at the north opening
north gatehouse lane 33: city -> gate -> route 35 -> gate -> city PASS
north gatehouse lane 34: city -> gate -> route 35 -> gate -> city PASS
```
The gatehouse map loads correctly in-engine (map group 76, map 8, grid width valid, metatiles read back), so the
north exit is no longer a teleport past an interior.

South seam, every lane, both directions (`south`):
```
south seam lane 32: city -> route 33 -> city PASS
south seam lane 33: city -> route 33 -> city PASS
south seam lane 34: city -> route 33 -> city PASS
south seam lane 35: city -> route 33 -> city PASS
```
Each lane: walk down out of the city at (lane,45) -> Route 33 (1,23) on the road, standable; then walk back west
into the city and land at (33,44), standable.

Dialogue (`dialogue`, `gatedlg`): every remaining city NPC and every sign, plus the three gatehouse NPCs, was
walked to in-emulator, faced, and talked to, asserting a message window opens and the field script releases
controls. 18 city interactions PASS (`Npc4 (17,36)`, `Npc7 (39,22)`, `Npc8 (30,21)`, `Npc9 (20,25)`,
`Npc12 (7,23)`, `Npc18 (30,39)`, `Npc19 (39,15)`, `Npc20 (44,40)`, `Npc21 (23,22)`, `Npc22 (12,35)`,
`Sign1 (12,22)`, `Sign2 (30,30)`, `Sign3 (26,22)`, `Sign4 (19,13)`, `Sign5 (19,38)`, `Sign6 (43,39)`,
`Sign7 (41,13)`, `Sign8 (45,12)`); screenshots in `plastic_ox/demo/shots/run6_*.png`.

### Regression suites
| suite | result |
|---|---|
| `plastic_ox/encounter_tables/test_pre_mt_moon_v5_5.py` | PASS — 237 checks |
| `plastic_ox/encounter_tables/test_nu_encounters_v1.py` | PASS — 168 checks |
| `plastic_ox/agent/test_trainer_teams_v2.py` | **3 failures, pre-existing** |

`test_trainer_teams_v2.py` fails on `TRAINER_PLASTIC_OX_ROUTE2_BEN`, `TRAINER_PLASTIC_OX_ROUTE2_HALEY` and
`TRAINER_PLASTIC_OX_ROUTE2_WADE` ("no checkpoint assigned and not in KEEP_AS_IS"). This is **not** caused by
RUN 6: `git diff --name-only HEAD -- src/data/trainers.party src/data/trainers.h
plastic_ox/agent/test_trainer_teams_v2.py` is empty, and those three trainers already exist in the committed
tree. Left unfixed as instructed.

### Blocked / deviations
* No blocked goals. All four RUN 6 goals are implemented and verified in-emulator.
* Deviation: goal 4 uses an aligned four-lane portal pair rather than a literal `connections` entry, because no
  walkable receiving edge exists on either map (see above). Facing follows the engine rule for the landing tile.
* Deviation: the north-gate `PoxRegion_goldenrod_route35_*` scripts were deleted rather than kept, because the
  trail has no story requirements and the door warp replaces the portal entirely. If
  `plastic_ox/alpha/region_v7.py` is ever re-run it will re-emit that trail from `TRAILS`; the generator was left
  untouched because the prompt scoped this run to the city and its gate.

## Files touched (all uncommitted)
```
data/maps/GoldenrodCity_hns/map.json
data/maps/GoldenrodCity_hns/scripts.inc
data/maps/Gate_GoldenrodCity_Route35_hns/map.json
data/maps/Gate_GoldenrodCity_Route35_hns/scripts.inc
data/maps/Route33_hns/map.json
data/maps/Route35_hns/map.json
data/scripts/plastic_ox_region.inc
plastic_ox/demo/test_run6_goldenrod.py            (new harness)
plastic_ox/agent/RUN6_GOLDENROD_CITY_V1_REPORT.md (this report)
```
Unrelated in-flight work already present in the tree (`src/overworld.c`, `src/fieldmap.c`, `src/dma3_manager.c`,
`src/wild_encounter.c`, `src/data/wild_encounters.json`, `include/dma3.h`, `plastic_ox/demo/test_camera_seam.py`,
`plastic_ox/demo/walk_demo.py`) was left untouched.
