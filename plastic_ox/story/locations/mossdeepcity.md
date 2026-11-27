---
title: Mossdeep City
slug: mossdeepcity
kind: City
act: 3
stage: "11 — Mossdeep and the Space Center"
depth: full
wiki: mossdeepcity
maps: [MossdeepCity]
also_maps: [MossdeepCity_Gym, MossdeepCity_SpaceCenter_1F, MossdeepCity_SpaceCenter_2F, MossdeepCity_PokemonCenter_1F, MossdeepCity_Mart]
flags: [FLAG_POX_STORY_SPACE_CENTER, FLAG_POX_GIFT_SPACE, FLAG_BADGE06_GET, FLAG_POX_STORY_MANSION, FLAG_RECEIVED_KINGS_ROCK, FLAG_RECEIVED_OLD_ROD]
badges: [6]
trainers: [TRAINER_PLASTIC_OX_TATELIZA]
items: [ITEM_NET_BALL, ITEM_KINGS_ROCK, ITEM_OLD_ROD]
status: implemented
---

# Mossdeep City

## Snapshot

The island at the bottom of the map: white rock and wish tags on the shore, a harbour that runs on tides, a Space Center that runs on launch windows. The player comes ashore from Seafoam's east exit, wins Tate & Liza's UUBL double battle for Badge 6, then walks into the Space Center, where a scientist reads the journey back to them as a measurement. That report is reveal-ladder step 11, and the same flag opens every Saffron surface entrance. The emotional note is **competence**: everyone here has a job with a schedule, and nobody is impressed by the player.

## Plot points

1. **Arrival is a working port.** South shore `(0,20)` (`PoxRegion_sea_mossdeep_b`) opens on `FLAG_POX_STORY_MANSION`, so the seam is Cinnabar-shaped: the player walks in off the Seafoam crossing, not out of a cutscene. North `(40,0)` goes to Route 19; the sailor at `(38,12)` says it reaches Saffron long before the gate does.
2. **Gym 6 — Tate & Liza.** `Pox_TateLiza` at `(23,7)`/`(24,7)` requires `FLAG_BADGE05_GET` and `FLAG_POX_STORY_MANSION`, refuses with fewer than two healthy Pokémon (`Pox_Text_TwoMons`), and sets `FLAG_BADGE06_GET`. UUBL double battle; the Gym is a teleport-tile and floor-switch puzzle, so the walk is the puzzle and the fight is the payoff.
3. **The report — reveal-ladder step 11, built on Project Equilibrium.** `Pox_SpaceReport` at 1F `(7,2)` (authored in `plastic_ox/alpha/weather_institute.py`) is gated on `FLAG_BADGE06_GET` and sets `FLAG_POX_STORY_SPACE_CENTER`. Two beats with a pause between (the scientist turns to the console and back): first the Weather Institute's survey held at regional scale — the region is not arranged randomly, habitats and strong Trainers are easier to reach, it looks arranged for training; then the data lines into Saffron carry far more than anyone's results — transfer traffic converges on Silph Co. from an unidentified source. Afterwards a short repeat line.
   - **VALE** (Silph, met at the Weather Institute) stands at the 1F consoles `(4,3)` (`Pox_SC_Vale`, optional): the model "was most accurate where TRAINERS battle most often. Up here, it's accurate almost everywhere." After the report VALE is unsettled for the first time — lead-in to Silph Co.
   - **Research file 007** on the 1F console row `(3-5,1)` continues the Institute's PROJECT EQUILIBRIUM files.
4. **Saffron opens — step 12.** The same flag releases the Route 19 → Saffron gates and the Route 8, Route 7, and Route 5 gates. Nothing else is required; Bruno and Silph remain unresolved and the report must not pretend otherwise.
5. **Eevee, fifth gift.** After the report, the scientist at 1F `(5,7)` hands over `SPECIES_EEVEE` (Lv 5) under `FLAG_POX_GIFT_SPACE`. Frame it as a study animal being retired to a good home, not a prize for clearing a Gym.
5a. **South shore → Route 127.** `PoxRegion_mossdeep_route127_a` at `(34,38)-(34,39)` opens with no flag onto Route 127's north edge `(39,1)`. Three islands hold the Regi caves: `DesertRuins` mouth `(28,5)`, `IslandCave` `(29,33)`, `AncientTomb` `(69,12)`. Each inner chamber is sealed unless the player carries its tablet (`ITEM_ANCIENT_ROCK_TABLET` / `_ICE_` from Mt. Moon, `_STEEL_` from the second round of the Underground tournament); the braille, Sealed Chamber and Wailord/Relicanth chain play no part. The sage beside each Regi keeps its badge gate (5 for Regirock, 6 for Regice/Registeel).
6. **The town turns over.** The Old Rod fisherman `(54,4)` only parts with `ITEM_OLD_ROD` after `FLAG_BADGE06_GET`; use the badge as the signal to stop being polite to the player. The Pokéfan's "letter" rumour should point at the launch schedule, not at a threat.
7. **Must not:** stage a villain occupation of the Space Center; mention Magma, Aqua, or Rocket; name Bill; let anyone say "convergence"; explain who built anything or why; resolve the mystery. Silph may be named as a destination only.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Saffron road | city `(38,12)` `PoxIsles_SaffronSailor` | `FLAG_POX_STORY_SPACE_CENTER` | two states: "the water gets you there long before the gate lets you in", then "SAFFRON is open… the gate is the easy part" | shipped |
| Launch board | city `(32,12)` `PoxIsles_LaunchBoard` | `FLAG_POX_STORY_SPACE_CENTER` | the date pasted over three times; after the report the board is taken down. No letter, no threat | shipped |
| Arrival | city `(4,21)` `PoxIsles_DockClerk` | always | logs the player off the Seafoam crossing, gives ferry times and points at the Gym and the white roof | shipped |
| South shore seam | city `(0,20)` `PoxRegion_sea_mossdeep_b` | `FLAG_POX_STORY_MANSION` unset | "The crossing to SEAFOAM is running hard" and a warp back | shipped (unreachable in normal play) |
| Gym leaders | Gym `(23,7)`, `(24,7)` `Pox_TateLiza` | badge 5 + Mansion; two healthy mons | duet challenge ("…is just manners"), own refusal, own two-Pokémon line, "MIND BADGE" line that sends the player to the Space Center, own repeat line | shipped |
| Gym guide and statues | Gym `(5,33)`, statues | `FLAG_BADGE06_GET` | describes a double battle and a mixed team, not the Hoenn psychic gym; post-victory branch and statue now key off badge 6 | shipped |
| Gym trainers | Gym, twelve trainer scripts | always | vanilla RS psychic-teen lines, all distinct | keep |
| The report | 1F `(7,2)` `Pox_SpaceReport` | `FLAG_BADGE06_GET`, then flag set | two beats with a turn to the console between; before badge 6 the chief waves the player off in his own words (`PoxIsles_ReportBusy`) | shipped |
| Field staff | 1F and 2F, e.g. `Pox_Facility_MossdeepCity_SpaceCenter_1F_9` | always | one line each by job; the child who wants to ride a rocket is now a visible child at 1F `(1,6)` (it was an invisible object on the plan table) | shipped |
| Eevee | 1F `(5,7)` `Pox_Space` | `FLAG_POX_STORY_SPACE_CENTER`, `FLAG_POX_GIFT_SPACE` | a study animal retired to the road; busy with feeding time before the report (`PoxIsles_SpaceBusy`) | shipped |
| Villain leftovers | city `(44,23)`–`(44,26)`, `(45,25)`; Space Center 1F / 2F | `FLAG_POX_HIDE_UNUSED_ACTOR` | never on screen; the objects and their dead Hoenn scripts remain in the data | delete with their scripts (artifact cleanup) |
| White rock | city `(56,21)`, sign `(57,21)` | always | wish tags every launch window; the rock reads "SAFE FLIGHT" and one tag hoping it is not a Monday | shipped |
| School kid | city `(65,16)` `PoxIsles_SchoolKid` | always | reads the Space Center sign: the board has said "soon" since his brother was little | shipped |
| King's Rock boy | city `(23,13)` | `FLAG_RECEIVED_KINGS_ROCK` | Steven's neighbour hands over a rock he cannot use; "don't tell him what for" | shipped |
| Old Rod | city `(54,4)` | `FLAG_BADGE06_GET` | gives `ITEM_OLD_ROD`, mostly MAGNEMITE | keep |
| Net Ball | city `(62,35)` | `FLAG_ITEM_MOSSDEEP_CITY_NET_BALL` | `ITEM_NET_BALL` | keep |
| Townspeople | city, Center, Mart | always | tide-watcher, Wailmer counter, ferry passenger, black belt training against the tide, mart regulars: island register, no vanilla Hoenn lines | shipped |
| Scott | city `(61,29)` | `VAR_SCOTT_STATE`; object removed after one talk | a travelling talent scout who came to see the twins; no Battle Frontier, no letter | shipped |

## Dialogue guidance

- **Who speaks:** harbour and range staff, Gym kids, the report scientist, Tate & Liza, the fisherman. The town may know launches, tides, ferry times, the Gym, and that the Space Center has been "counting something". Only the scientist may state the step-11 findings, and only after Badge 6.
- **Register:** island practicality. Short sentences, no exclamation marks, time measured in launch windows and tides. Nobody is awed by the player; the leaders are the local team, and the Space Center is a workplace with a queue.
- **Tate & Liza speak as one**, finishing each other's sentences. They are the only people in town who treat battle as a game rather than a job, and the only ones allowed to enjoy the player's arrival.
- **Before/after:** before the report, the center is a lobby and a deflection; after, staff are quieter, the scientist is packing, the Eevee is available, and the sailor's line flips from "shut" to "open".
- **Merged geography as logistics:** "the mainland is closer than it used to be" is allowed; an explanation of why is not.

> DOCK CLERK: Ferry's at six and six. If the wind's up, it's at six and whenever.

> SPACE CENTER SCIENTIST: We can measure the routes. We can't measure the reason. That's the part I'd like to hand to somebody else.

> TATE & LIZA: Two of us. Two of you. Everything after that is just manners.

> FISHERMAN: Thirty years off these steps. Mostly MAGNEMITE. The harbour's louder than the water now.

> SCHOOLKID: The board says the next launch is "soon". It's said "soon" since my brother was little.

- **Do not:** use "convergence", "simulation", "adaptive system", or Bill; name Magma, Aqua, or Rocket; have the report name the creator or the cause; let the Eevee gift feel like a medal; make the town a victim waiting to be saved.

## Inspiration

- **Tanegashima and Uchinoura:** a Japanese rocket island where the launch schedule is the civic calendar, schools close for a window, and fishing boats double as recovery boats. Jobs: range safety, telemetry, boat hire, an ice-cream van at the pad gate.
- **NASA launch-town rhythm:** countdown on a PA, "the window", wind holds, a diner that opens at four. Overheard: a scrub, a hold, a shipment that arrived early, a cousin on the mainland.
- **Mossdeep in RSE:** white rock and wish tags, Steven's house next door, the dive out to Sootopolis. Keep the rock as civic religion and Steven as the neighbour nobody name-drops in front of strangers.
- **A Japanese island ferry port:** salt corrosion, postcards and bait in the same cooler, a noticeboard with a date amended three times. That board is the Pokéfan's "letter", and it needs no villain.
- **Mission-control humour:** the deadpan of people who have postponed something eleven times. Give it to the scheduler and the school group, never to the director, who is the one person allowed to be tired.

## Implementation hooks

- Wiki page: `mossdeepcity.html`
- Maps: `MossdeepCity` (`MAP_MOSSDEEP_CITY`), `MossdeepCity_Gym` (`MAP_MOSSDEEP_CITY_GYM`), `MossdeepCity_SpaceCenter_1F` (`MAP_MOSSDEEP_CITY_SPACE_CENTER_1F`), `MossdeepCity_SpaceCenter_2F` (`MAP_MOSSDEEP_CITY_SPACE_CENTER_2F`)
- Scripts: `data/scripts/plastic_ox_story.inc` (`Pox_TateLiza`, `Pox_SpaceReport`, `Pox_Space`, `Pox_SaffronRoad`, `Pox_FacilityWorker`), `data/maps/MossdeepCity/scripts.inc`, `data/maps/MossdeepCity_Gym/scripts.inc`
- Trainers / items: `TRAINER_PLASTIC_OX_TATELIZA` (six mons, Lv 44–46, Leftovers-heavy), `ITEM_KINGS_ROCK`, `ITEM_OLD_ROD`, `ITEM_NET_BALL`
- Town, Gym, Center, Mart and Space Center wording for this pass is authored in `plastic_ox/alpha/south_isles.py` (emits `data/scripts/plastic_ox_south_isles.inc`, prefix `PoxIsles_`). Harness: `plastic_ox/demo/test_south_isles.py`.
- Magma removed (2026-11-27): the fourteen Magma objects (five in town, nine in the Space Center) are gone from the map data. `south_isles.prune` also drops every block of the town and Space Center scripts that nothing reaches any more, including the Magma/Aqua sailor text. The debug menu's Steven multi battle still reaches one 2F block, which keeps its lines minus the Magma movements.
- Interiors (2026-11-27): the houses (taster, Fortree mail, Super Rod, hideout family), Steven's house (Steven, rock display, postgame letter) and the Game Corner (two people beside the dark link cabinets) speak their own lines. Mechanics are unchanged.
- Gym guide: `PoxIsles_MossdeepGymGuide` runs `CheckMossdeepGymUUBLRules` and names a banned move or item as the twins' rule. It warns but does not block.
- Known gaps: `FLAG_DEFEATED_MOSSDEEP_GYM` and `FLAG_RECEIVED_HM_DIVE` are never set here, so anything still keyed on them is dead (the Gym guide and statues now use `FLAG_BADGE06_GET`); 2F Steven is hidden from a new game, so only the 1F Steven is met; the leader record uses `Pic: Leader Roxanne` with `Gender: Male` for a two-person team.

## Open questions

- Is 2F a room or a view? Recommend one post-report scene at the window, then retire the stairs; the current nine duplicates are worse than an empty floor.
- ~~Delete the Magma clusters, or re-skin them as Space Center staff?~~ Deleted on 2026-11-27.
- Split the report at the flag, or keep one box? Recommend split: the flag currently flips mid-conversation, hiding the moment Saffron opens.
- Should Steven appear in the Space Center at all? He is a Mossdeep neighbour and a League-tier trainer; recommend one line, no League reference.
- Is the Old Rod's Badge 6 gate deliberate? It is the only gift tied to the Gym, and it makes the badge feel civic rather than heroic.
