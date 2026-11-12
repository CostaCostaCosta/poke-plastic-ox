---
title: Saffron City
slug: saffroncity-hns
kind: City
act: 4
stage: "10 — Saffron hub"
depth: full
wiki: saffroncity-hns
maps: [SaffronCity_hns]
also_maps: [PlasticOx_BrunoGym, PlasticOx_Silph, SaffronCity_Dojo_Frlg]
flags: [FLAG_POX_STORY_SPACE_CENTER, FLAG_POX_STORY_SILPH, FLAG_POX_HIDE_SILPH_GRUNT_1, FLAG_POX_HIDE_SILPH_GRUNT_2, FLAG_POX_HIDE_SILPH_GRUNT_3, FLAG_POX_HIDE_SILPH_GIOVANNI]
badges: [7]
trainers: [TRAINER_PLASTIC_OX_BRUNO, TRAINER_PLASTIC_OX_SILPHGRUNT1, TRAINER_PLASTIC_OX_SILPHGRUNT2, TRAINER_PLASTIC_OX_SILPHGRUNT3, TRAINER_PLASTIC_OX_GIOVANNI]
status: drafted
---

# Saffron City

## Snapshot

A grey, dense city centre that has been shut for most of the game and now stands open at four corners: Route 8 east, Route 7 west, Route 19 south, Route 5 north. The player walks in from the Mossdeep road, finds a mart, three guides, and two objectives that can be taken in either order — the Fighting Dojo's OU challenge and the Silph Co. seizure. Saffron is the game's late hub and its loudest place: crowds on the street, silence inside the Dojo, and a lift-shaft hum under Silph.

## Plot points

1. **The city opens.** Every surface crossing (`(61,27)`, `(2,26)`, `(32,44)`, `(30,6)`) checks `FLAG_POX_STORY_SPACE_CENTER`; completing Mossdeep is the only key. Reveal-ladder **step 12**: the sealed centre becomes the late-game hub, and the roads the player has been routing around finally meet.
2. **Two objectives, either order.** Bruno at `(16,22)` (Gym 7, OU) and Silph at `(26,15)` are independent. Neither gates Clair, Route 5, or the other. The guides must keep saying this plainly.
3. **Gym 7 — Bruno.** The Dojo is entered by talking to the guide, who warps the player to `PlasticOx_BrunoGym` `(5,17)`; `Pox_Bruno` requires Badge 6 and the Space Center flag, then awards Badge 7. Bruno is a former Elite Four member and a world-class Trainer — not a villain and not a gatekeeper for the plot.
4. **Rocket III — Silph.** Three grunts in sequence (`(3,8)`, `(7,8)`, `(3,9)`), then Giovanni at `(7,9)`, then the core terminal at `(5,2)`. **Step 13:** Rocket did not cause the convergence — it followed a signal and old research. **Step 14:** the adaptive Trainer system caused it while optimising training conditions; the creator is never named.
5. **The world stays merged.** The core text ends with the region intact and its boundaries no longer moving. Do not describe the city returning to normal or the geography un-merging.
6. **The north road.** `(30,6)` opens with the city, not with Bruno or Silph, and leads to `Route5_hns` and Blackthorn (see `route5-hns.md`).
7. **Must not:** name Bill anywhere in this city, say Rocket created the convergence, name or hint at the system's creator, have civilians know what is inside Silph before the player does, or let the Gym/Silph objectives gate each other.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Dojo guide | `SaffronCity_hns` `(16,22)` `Pox_BrunoGuide` | `FLAG_POX_TRIGGERS_ENABLED` | "BRUNO's challenge is this way." then warps to `PlasticOx_BrunoGym` `(5,17)` | keep the warp; make her a dojo receptionist with a queue, not a signpost |
| Silph guide | `(26,15)` `Pox_SilphGuide` | Space Center flag | explains both objectives and the northern road, warps to `PlasticOx_Silph` `(5,9)` | keep the information; cut it to two textboxes and one honest worry |
| North-road guide | `(56,15)` `Pox_BlackthornRoad` | always | "Take SAFFRON's north exit through ROUTES 5 and 115 and METEOR FALLS to BLACKTHORN." | keep; he should be leaving that way himself |
| Six street NPCs | `(49,23)`, `(43,34)`, `(53,32)`, `(32,39)`, `(11,15)`, `(19,32)` | always | two lines shared three ways: "Trainers come from far away to test themselves at the DOJO." and "The busy streets make the DOJO feel wonderfully quiet." | six people with six jobs and six opinions; no repeated line anywhere |
| Unused NPC scripts | `SaffronCity_EventScript_Npc1`–`Npc3` | — | three labelled NPC scripts with text but no object on the map | delete or place them; dead labels read as broken content |
| Signs | `(60,26)`, `(31,43)`, `(29,7)` | always | objects **and** identical background sign events on the same tiles; texts are "Route8 / Route19 / Route5 / Marked passage ahead." | one sign per tile; rewrite each to name a district or a direction, not a map constant |
| Four crossings | `(61,27)`, `(2,26)`, `(32,44)`, `(30,6)` | `FLAG_POX_STORY_SPACE_CENTER` | `PoxRegion_*_saffron_*` warps; closed state bumps the player one tile back with generic text | keep; each edge should have a visible landmark (arch, checkpoint, tram stop) |
| Mart | `(44,21)` | always | only interior warp in the city, to `MAP_MART_KANTO_HNS` | keep; the city still has **no Pokémon Center**, which is a real hub problem |
| Gym battle | `PlasticOx_BrunoGym` `(5,2)` `Pox_Bruno` | Badge 6 + Space Center; `FLAG_BADGE07_GET` unset | OU single battle, awards Badge 7 | keep; add the pre-battle line about the class/dojo he left |
| Gym exit | `PlasticOx_BrunoGym` `(4,17)` `Pox_BrunoGymExit` | always | "I'll show you back outside." warps to Saffron `(16,23)` | keep, or make it a silent walk-out |
| OU rules greeter | `PlasticOx_BrunoGym` script only | — | `PlasticOx_BrunoGym_EventScript_Greeter` checks `CheckSaffronGymOURules`, but **no object uses it**, and the special is a stub that calls the Little Cup check | place a greeter object and implement the documented ADV OU clauses, or drop the pretence |
| Silph grunts | `PlasticOx_Silph` `(3,8)`, `(7,8)`, `(3,9)` | hide flags 1–3, sequential | three battles, all three share one line: "These terminals won't obey us. But the BOSS will make this system his!" | three different people: one frightened, one greedy, one who has read too much |
| Giovanni | `PlasticOx_Silph` `(7,9)` | after grunt 3 | "We did not make this world… the old man's research… Stand aside!" | keep the denial; resolve who "the old man" is (Fuji's archives) or cut the phrase |
| Silph core | `PlasticOx_Silph` `(5,2)` | after Giovanni; `FLAG_POX_STORY_SILPH` | terminal text naming the ADAPTIVE TRAINER SYSTEM, its battle profiles and objective; player isolates the environmental controls | keep the reveal; it is step 14 and the only place the system is named |
| Silph exit | `PlasticOx_Silph` `(4,9)` | always | warps to Saffron `(26,16)` | keep |
| Legacy Dojo | `SaffronCity_Dojo_Frlg` | — | vanilla FRLG Dojo: Koichi, five Black Belts, Hitmonlee/Hitmonchan gift balls, door warps to `MAP_SAFFRON_CITY` | unreachable — no warp or script enters it; recommend retire (see Open questions) |

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
- Maps: `SaffronCity_hns` (`MAP_SAFFRON_CITY_HNS`, layout `LAYOUT_SAFFRON_CITY_HNS`, 66×55), `PlasticOx_BrunoGym` (`MAP_PLASTIC_OX_BRUNO_GYM`, borrowing `LAYOUT_RUSTBORO_CITY_GYM`), `PlasticOx_Silph` (`MAP_PLASTIC_OX_SILPH`, borrowing `LAYOUT_MOSSDEEP_CITY_SPACE_CENTER_1F`), `SaffronCity_Dojo_Frlg` (`MAP_SAFFRON_CITY_DOJO`)
- Scripts: `data/scripts/plastic_ox_story.inc` (`Pox_Bruno`, `Pox_BrunoGuide`, `Pox_BrunoGymExit`, `Pox_SilphGrunt1`–`3`, `Pox_Giovanni`, `Pox_SilphCore`, `Pox_SilphGuide`, `Pox_SilphExit`, `Pox_BlackthornRoad`), `data/scripts/plastic_ox_region.inc` (the four edge crossings and three sign texts), `data/maps/SaffronCity_hns/scripts.inc`, `data/maps/PlasticOx_BrunoGym/scripts.inc`
- Gates: `FLAG_POX_STORY_SPACE_CENTER` (city and all four edges), `FLAG_POX_STORY_SILPH`, the four Silph hide flags, `FLAG_BADGE06_GET` (Bruno's prerequisite in `Pox_Bruno`), `FLAG_BADGE07_GET` (awarded)
- Trainers / items: `TRAINER_PLASTIC_OX_BRUNO` (OU, Lv. 48–50), the three `TRAINER_PLASTIC_OX_SILPHGRUNT1`, `TRAINER_PLASTIC_OX_SILPHGRUNT2` and `TRAINER_PLASTIC_OX_SILPHGRUNT3`, `TRAINER_PLASTIC_OX_GIOVANNI` (Lv. 53–55). No items are given in the city; the legacy Dojo's Hitmonlee/Hitmonchan gift belongs to a map that cannot be reached.
- Known gaps: **no Pokémon Center** anywhere in Saffron (one mart warp only), so a hub city cannot heal; both objective buildings have **zero warps** and are entered by scripted transport from a guide NPC, so the doors are decorative; `PlasticOx_BrunoGym` reuses Rustboro's Gym interior and `PlasticOx_Silph` reuses Mossdeep Space Center 1F, so the "tower climb" is a single room with four NPCs in a 2×2 cluster; all three grunt battles share one line; `SaffronCity_EventScript_Npc1`–`Npc3` are dead; six street NPCs share two lines; every sign is doubled as object plus background event; `SaffronCity_Dojo_Frlg` is a fully-populated vanilla Dojo (Koichi, five Black Belts, two gift balls) with no inbound warp — unreachable duplicate content; `CheckSaffronGymOURules` is a stub and its greeter script has no object.

## Open questions

- Retire `SaffronCity_Dojo_Frlg`? It duplicates Gym 7 with vanilla Black Belts and an unreachable Hitmon gift. Recommend retire or convert it into the Dojo's back room with no battles.
- Should the Dojo and Silph get real door warps instead of guide-initiated teleports, and what happens to the three guide NPCs then?
- Keep the single-room Silph, or build a short multi-floor climb? The bible wants a climax, not a maze, but one room with four NPCs undersells Rocket's last stand.
- Where does Saffron's healing go — a Pokémon Center interior, a nurse placed in the mart, or a rest house attached to the Dojo?
- Implement the documented ADV OU clauses in `CheckSaffronGymOURules` and place the greeter, or drop the OU-rules framing from the Gym's dialogue?
