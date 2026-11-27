---
title: Saffron City
slug: saffroncity-hns
kind: City
act: 4
stage: "10 — Saffron hub"
depth: full
wiki: saffroncity-hns
maps: [SaffronCity_hns]
also_maps: [SaffronCity_Dojo_Frlg, SilphCo_1F_Frlg, SilphCo_11F_Frlg, SaffronCity_House_Frlg, SaffronCity_MrPsychicsHouse_Frlg, PlasticOx_BrunoGym, PlasticOx_Silph]
flags: [FLAG_POX_STORY_SPACE_CENTER, FLAG_POX_STORY_SILPH, FLAG_POX_HIDE_SILPH_GRUNT_1, FLAG_POX_HIDE_SILPH_GRUNT_2, FLAG_POX_HIDE_SILPH_GRUNT_3, FLAG_POX_HIDE_SILPH_GIOVANNI, FLAG_POX_DOJO_PRIZE, FLAG_POX_SILPH_MASTER_BALL, FLAG_POX_HIDE_SILPH_STAFF]
badges: [7]
trainers: [TRAINER_PLASTIC_OX_BRUNO, TRAINER_PLASTIC_OX_DOJO_KENJI, TRAINER_PLASTIC_OX_DOJO_NOB, TRAINER_PLASTIC_OX_SILPHGRUNT1, TRAINER_PLASTIC_OX_SILPHGRUNT2, TRAINER_PLASTIC_OX_SILPHGRUNT3, TRAINER_PLASTIC_OX_GIOVANNI]
status: implemented
---

# Saffron City

## Snapshot

A grey, dense city centre that has been shut for most of the game and now stands open at four corners: Route 8 east, Route 7 west, Route 19 south, Route 5 north. The player walks in from the Mossdeep road and finds a mart, a Pokémon Center, nine residents with nine jobs, and two objectives that can be taken in either order: the Fighting Dojo's OU challenge and the Silph Co. seizure. Both are real buildings with real doors. Saffron is the game's late hub and its loudest place: crowds on the street, silence inside the Dojo, and a lift-shaft hum under Silph.

## Plot points

1. **The city opens.** Every surface crossing (`(61,27)`, `(2,26)`, `(32,44)`, `(30,6)`) checks `FLAG_POX_STORY_SPACE_CENTER`; completing Mossdeep is the only key. Reveal-ladder **step 12**: the sealed centre becomes the late-game hub, and the roads the player has been routing around finally meet.
2. **Two objectives, either order.** The Dojo doorway `(45,12)` (Gym 7, OU) and the Silph door `(33,30)` are independent. Neither gates Clair, Route 5, or the other. The north-road walker says so plainly.
3. **Gym 7 — Bruno.** The wooden hall at `(45,12)` is `SaffronCity_Dojo_Frlg`. `Pox_Bruno` at `(6,5)` requires Badge 6 and the Space Center flag, refuses to begin while the party breaks an ADV OU clause, then awards Badge 7 and offers one of two prize fighters. Bruno is a former Elite Four member and a world-class Trainer, not a villain and not a gatekeeper for the plot.
4. **Rocket III — Silph.** Three grunts in order: the lobby lift `SilphCo_1F_Frlg (22,4)`, the east corridor `SilphCo_11F_Frlg (16,12)`, the west corridor `(0,12)`. Then Giovanni in the boardroom `(6,11)`, then the President's terminal `(5,7)`. **Step 13:** Rocket did not cause the convergence; it followed the noise and Mr. Fuji's notes. **Step 14:** the adaptive Trainer system caused it while optimising training conditions; the creator is never named.
5. **The world stays merged.** The terminal ends with `EXISTING GEOGRAPHY: RETAINED` and the boundaries no longer moving. Nothing un-merges, in the tower or on the street.
6. **The north road.** `(30,6)` opens with the city, not with Bruno or Silph, and leads to `Route5_hns` and Blackthorn (see `route5-hns.md`).
7. **Must not:** name Bill anywhere in this city, say Rocket created the convergence, name or hint at the system's creator, have civilians know what is inside Silph before the player does, or let the Gym/Silph objectives gate each other.

## Key interactions

| Interaction | Where | Trigger / state | Behavior |
| --- | --- | --- | --- |
| Nine residents | `SaffronCity_hns`: queue `(43,13)`, Silph clerk `(35,31)`, north-road walker `(27,12)`, grocer `(49,23)`, courier `(43,34)`, schoolkid `(53,32)`, train kid `(11,15)`, overtime clerk `(20,39)`, old-hall kid `(50,13)` | always; the Silph clerk switches on `FLAG_POX_STORY_SILPH` | nine scripts, nine lines (`PoxSaffron_*`, `Pox_BlackthornRoad`). Nobody teleports the player. After Silph the clerk is relieved and cannot say why |
| Dojo door | `(45,12)` → `SaffronCity_Dojo_Frlg` | always | open doorway, walks in and out |
| Silph door | `(33,30)` → `SilphCo_1F_Frlg` | always | walks in and out |
| Pokémon Center | `(18,38)` → `PokemonCenter_Kanto_hns` | always | the shared Kanto interior with a dynamic exit; the hub can heal |
| Mart | `(44,21)` | always | `MAP_MART_KANTO_HNS` |
| Building signs | Dojo `(47,14)`, old hall `(54,14)`, Silph `(30,31)`, station `(20,15)` | always | one sign each. The GYM-plated hall next to the Dojo is closed and says League challenges are held next door |
| Houses | `(21,21)` → `SaffronCity_House_Frlg`, `(47,38)` → `SaffronCity_MrPsychicsHouse_Frlg` | always | a sister, a brother, their PIDGEY and a letter; a man at his piano |
| Closed doors | old hall `(52,12)`, station `(17,14)` | always | a short line each; both are closed in the fiction (hall shut, trains not stopping) |
| Whiteout point | entering `SaffronCity_hns` | always | `setrespawn HEAL_LOCATION_POX_SAFFRON`: a loss in the Dojo or Silph returns to `(18,39)`, healed, in front of the Center |
| Four crossings | `(61,27)`, `(2,26)`, `(32,44)`, `(30,6)` | `FLAG_POX_STORY_SPACE_CENTER` | `PoxRegion_*_saffron_*` (region_v7.py). The north and south gate signs name the gate and the road |
| Dojo desk | `SaffronCity_Dojo_Frlg` `(8,13)` `PoxSaffron_DojoDesk` | `CheckSaffronGymOURules`; `FLAG_BADGE07_GET` | welcomes, states the OU clauses, names the first banned move or item in the party; after the badge, the logbook line |
| Black Belts | `(1,10)` KENJI, `(11,10)` NOB | sight 3 | optional: the middle of the mat (x 5–7) is clear, their halves are not |
| Students | `(1,8)`, `(11,8)` | always | etiquette lines, no battle |
| Gym battle | `(6,5)` `Pox_Bruno` | Badge 6 + Space Center; OU clauses clean; `FLAG_BADGE07_GET` unset | OU single battle, Badge 7, then the prize offer |
| Prize fighters | item balls `(5,3)` HITMONLEE, `(7,3)` HITMONCHAN | `FLAG_BADGE07_GET`; `FLAG_POX_DOJO_PRIZE` | one of the two at Lv. 45; taking either hides both |
| Lobby desk | `SilphCo_1F_Frlg` `(3,7)` `PoxSaffron_LobbyDesk` | `FLAG_POX_STORY_SILPH` | hid under the desk; heals the party before and after |
| Lift guard | `(22,4)` `Pox_SilphGrunt1` | Space Center; hide flag 1 | sight battle; he stands on the only tile that reaches the lift |
| Stairs | 1F `(31,2)`, 11F `(7,2)` | always | chained; a line and a step back. The lift `(22,3)` ↔ `(13,3)` is the way up |
| Corridor grunts | `SilphCo_11F_Frlg` `(16,12)`, `(0,12)` | hide flags 1→2→3 | sight battles covering each corridor; dormant until the one before is beaten |
| Warp pad | `(16,19)` ↔ `(2,5)` | always | joins the lift side of 11F to the boardroom side |
| Giovanni | `(6,11)` `Pox_Giovanni`; triggers `(5,14)`, `(6,14)` | after grunt 3 | stepping into the boardroom walks the player up to him; he denies moving anything, names Fuji's notes, battles, and leaves |
| Silph core | terminal `(5,7)` `Pox_SilphCore` | after Giovanni; sets `FLAG_POX_STORY_SILPH` | status read-out naming the ADAPTIVE TRAINER SYSTEM; a yes/no isolates the environmental controls; the geography is retained |
| President | `(9,9)`, secretary `(11,9)` | `FLAG_POX_HIDE_SILPH_STAFF` cleared by the core | MASTER BALL, once (`FLAG_POX_SILPH_MASTER_BALL`); he does not ask what was on his terminal |
| Retired rooms | `PlasticOx_BrunoGym`, `PlasticOx_Silph` | — | empty placeholders that keep their map numbers; each has a door back to its real building for a save made inside |

## Dialogue guidance

- **Two registers, one city.** The street is loud, commercial and entirely ignorant of the plot: shopkeepers, couriers, a dojo queue, someone complaining about the tram. Inside the Dojo the register drops to etiquette — short bows, no boasting. Inside Silph it drops again, to fear and hardware.
- **Dojo staff** speak in invitations and corrections ("hands lower", "again"), not threats. Bruno himself is calm, formal, and interested in the player's team rather than their badge count.
- **Rocket grunts** are technicians who expected a server room and found a mind. Each of the three should want a different thing: to be paid, to be safe, to be right.
- **Giovanni** is the only person in the city who speaks in complete, confident paragraphs. He never raises his voice and never says "convergence".
- **Civilians** must not know what Silph contains. After `FLAG_POX_STORY_SILPH` they can be relieved, but nobody should be able to summarise what happened.
- **The terminal** is not a character; keep its lines as labels and status, never as taunts.

> DOJO RECEPTIONIST: Sign here, leave your bag, and mind the floor. The Master has been waiting since the morning bell.

> SHOPKEEPER: You picked a good week. Last month the trucks couldn't get in at all and we sold nothing but rice.

> GRUNT: They told us it was a server room. Nobody said it would answer back.

> GIOVANNI: I have spent three years following a rumour through other people's ruins. You will forgive me if I am not polite about it.

> TERMINAL: BATTLE PROFILES LOGGED. TRAINING CONDITIONS: IMPROVED.

- **Do not:** put Bill's name in this city; let a civilian describe the adaptive system; have anyone thank the player for "saving Saffron" before Silph is resolved; write Rocket as cartoon thugs; mention Sabrina or a Psychic Gym (there isn't one here).

## Inspiration

- **A Japanese city centre in the middle of a construction cordon** — Osaka's Umeda or the streets around Tokyo Station: hoardings, a station concourse, a department store basement, everybody walking fast and looking at their phone. The sealed months are why the streets feel *reopened* rather than festive.
- **The dojo inside an office block** — a kendo hall on the fourth floor, shoes at the door, a wooden floor that carries sound, a receptionist with a clipboard. Converts directly into the guide-as-door and the queue.
- **Corporate lobby as dungeon** — a reception desk, a lift with no power, a floor plan with three names on it; the Pokémon-media touchstone is the Silph climb in RBY/FRLG, compressed into one room here (see gaps).
- **Heist-film geography** — the crew that got in first, the boss who arrives late, the vault that turns out to be a person. Use it for pacing inside Silph, not for dialogue.
- **Office overtime culture** — the shopkeeper's week, the guides' shifts, the person who has not been home. Converts into the street's six jobs.

## Implementation hooks

- Wiki page: `saffroncity-hns.html`
- Source of truth: `plastic_ox/alpha/saffron.py` (maps, doors, residents, signs, Dojo and Silph scripts, flags, Dojo trainer ids) and the Bruno / Silph battles in `plastic_ox/alpha/build_story.py`. Edit those, not the generated files.
- Maps: `SaffronCity_hns` (`MAP_SAFFRON_CITY_HNS`, layout `LAYOUT_SAFFRON_CITY_HNS`, 66×55), `SaffronCity_Dojo_Frlg` (`MAP_SAFFRON_CITY_DOJO`), `SilphCo_1F_Frlg` (`MAP_SILPH_CO_1F`), `SilphCo_11F_Frlg` (`MAP_SILPH_CO_11F`). The other FRLG Silph floors are unused donors and nothing warps into them.
- Scripts: `data/scripts/plastic_ox_saffron.inc` (`PoxSaffron_*`, `Pox_SilphCore`), `data/scripts/plastic_ox_story.inc` (`Pox_Bruno`, `Pox_SilphGrunt1`–`3`, `Pox_Giovanni`, `Pox_BlackthornRoad`), `data/scripts/plastic_ox_region.inc` (the four edge crossings and two gate signs)
- Gates: `FLAG_POX_STORY_SPACE_CENTER` (city and all four edges), `FLAG_POX_STORY_SILPH`, the four Silph hide flags, `FLAG_BADGE06_GET` (Bruno's prerequisite), `FLAG_BADGE07_GET` (awarded), `CheckSaffronGymOURules` (OHKO moves, Assist, Lax Incense; the evasion moves and BrightPowder are removed from the ROM)
- Trainers / items: `TRAINER_PLASTIC_OX_BRUNO` (OU, Lv. 53–55; hand-authored in `tools/authored_trainers.party`: Zapdos, Ludicolo, Blaziken, Heracross, Regirock, Celebi), `TRAINER_PLASTIC_OX_DOJO_KENJI` and `TRAINER_PLASTIC_OX_DOJO_NOB` (Lv. 51–52), `TRAINER_PLASTIC_OX_SILPHGRUNT1`–`3` (Team Rocket, Lv. 50–53), `TRAINER_PLASTIC_OX_GIOVANNI` (class `Rocket Boss`, Lv. 53–55). HITMONLEE or HITMONCHAN from the Dojo; a MASTER BALL from the President.
- Harness: `plastic_ox/demo/test_saffron.py`
- Known gaps: the station and the closed training hall are doors with a line and no interior, on purpose; Silph is two floors, not a climb.

## Open questions

- Does the closed training hall next to the Dojo ever open, and as what?
- Is a MASTER BALL the right Silph reward for this region's legendaries, or should the President give something else?
