# Review fix pass — 2026-11-11

Eight scoped agents patched the findings from `plastic_ox/story/REVIEW_FINDINGS.md`
in disjoint file sets; one integration pass (this report) built the ROM and ran
the harnesses. Design decisions from the user are recorded in the findings file.

## Shipped

| Area | Change |
| --- | --- |
| Ilex north exit | `ilex_forest_hns` metatile 0x3B now has `MB_NORTH_ARROW_WARP` (`0x0064`); attributes 60/60. |
| Dark Cave mouths | `cave_default_hns` metatiles 306/307 now `MB_SOUTH_ARROW_WARP` (`0x0065`); attributes 308/308. |
| House doors | `house_lab_hns` was one attribute short (216/217); metatile 216 used by `Route2_House_Frlg` now has `MB_ANIMATED_DOOR`. |
| Surf skip | Route 21 South's Cinnabar seam is gated on `FLAG_POX_STORY_MANSION`, southbound only (facing check), so Cinnabar→sea still works. Route 20 West's mid-water return tripwire moved to the real west edge `(0,10)`. |
| Route 44 | Badge 1 required in both directions; `_Closed` arms reachable; hiker moved off the warp tile; coord gate before Mt. Moon. |
| Blackthorn Gym | Real door trigger at `(16,28)` into `PlasticOx_ClairGym`, reciprocal warp, guide is a hint NPC. |
| Goldenrod Gym | City door retargeted to `PlasticOx_WhitneyGym` (badge 2 only once); legacy gym unreachable. |
| Ecruteak rooms | Gym/theater doors retargeted to `PlasticOx_MortyGym` / `PlasticOx_DanceTheater`; both rooms have exits; legacy rooms unreachable. |
| Route 119 | Ecruteak east road opens after Morty; lands at `(5,124)` (script warps cannot address y>127 — see limit below); return gate at `(4,124)`. |
| Victory Road | Return band moved off the landing row; arrival no longer ejects on the first south step. |
| Fortree | Kecleon blocks the east walkway at `(38,10)` until badge 4, then reveals/flees; Gym is never blocked; arrival script no longer pre-clears it. |
| Kimono girls | Five distinct female dancers with themed Gen-3 teams (Vaporeon/Chinchou/Marill/Corphish; Jolteon/Electrike/Minun; Flareon/Vulpix/Numel/Slugma; Espeon/Kirlia/Spoink; Umbreon/Sableye/Duskull/Poochyena), unique intro/defeat/after lines, Eevee gift framed as fostering a partner. |
| Tier checks | Saffron/Blackthorn OU specials now add OHKO, Evasion move/item, Assist and Swagger clauses; lower tiers still share the base check until a species-tier table exists. |
| Text/items | Burned Tower TM12 gives `ITEM_TM12`; Route 115/Meteor Falls item balls match their flags; Route 35/45 dialogue unique; League rooms and Bill have distinct lines; Bill intro is `CHAMPION BILL would like to battle.`; Hall guide no longer uses Bill's sprite. |
| Goldenrod extras | One SquirtBottle source (Flower Shop), one coin clerk/prize host, herb stock, honest Underground guard text. |
| Map metadata | `MAPSEC_ROUTE_33` was missing from `region_map_sections.json`, which broke the link; added. |

Also: `check_map_refs.py` (new static wiring checker), `walklib.py` paths made
worktree-relative, Route 44/Sudowoodo/League expectations updated where the
design intentionally changed.

## Verification

- `make -j16 pokeemerald.gba` — clean build; ROM 28.2 MB used (33,554,432 B padded).
- `plastic_ox/demo/test_review_fixes.py` — **PASS** 8/8: Ilex north exit, Dark
  Cave east mouth, Route 44 with/without badge, Blackthorn Gym in/out,
  Goldenrod Gym in/out, Ecruteak east + return, Victory Road first step,
  Fortree Kecleon block + reveal + Route 110 exit.
- `test_warps_v1.py --static-only` — no findings on any changed map (remaining
  findings are pre-existing donor maps: Seafoam B2–B4, FRLG Lavender interiors,
  Route 115 self-warps, Route 4, SS Anne).
- `test_pre_mt_moon_v5_5.py` — PASS 239.
- `test_nu_encounters_v1.py` — PASS 189.
- `test_trainer_teams_v2.py` — PASS 2,588 checks / 97 trainers.
- `test_sudowoodo_v1.py` — all scenarios pass (single bottle source).
- `test_route44_transitions.py` — PASS full walk both approaches.
- `check_story_notes.py --quiet` — 61 notes, 0 errors, 0 warnings.

## Known limits and follow-ups

- **Script `warp` coordinates are `s8`** (`SetWarpDestination(..., s8 x, s8 y)`),
  so a script cannot warp to y>127. Route 119's gate therefore sits at y=124;
  the rest of the southern route is reached on foot. Do not move that link
  below y=127 without a connection instead.
- `plastic_ox/alpha/build_story.py` still holds the old Kimono generator block;
  a comment marks it, but regeneration would revert the hand-tuned teams/text.
  `plastic_ox/alpha/league.py` was updated for the new League/Bill lines.
- Demo fixtures `test_region_walk.py` / `test_league.py` still encode some old
  assumptions (Route 44 badge, Victory Road one-step eject) and were not all
  re-run; the changed behaviour is covered by `test_review_fixes.py`.
- Deferred: species-tier rosters, Route 110 trainer levels, Route 37 twin
  trainer id, Storage guard text, legacy map retirement decisions, and the
  Route 35 item-ball flags (decoys restyled instead).
