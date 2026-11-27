---
title: Cinnabar Island
slug: cinnabarisland-frlg
kind: Town
act: 3
stage: "9 — Cinnabar and the Mansion"
depth: full
wiki: cinnabarisland-frlg
maps: [CinnabarIsland_Frlg]
also_maps: [PlasticOx_BlaineGym, PlasticOx_Mansion, CinnabarIsland_Gym_Frlg, PokemonMansion_1F_Frlg, PokemonMansion_2F_Frlg, PokemonMansion_3F_Frlg, PokemonMansion_B1F_Frlg, CinnabarIsland_PokemonCenter_1F_Frlg, CinnabarIsland_Mart_Frlg, CinnabarIsland_PokemonLab_Entrance_Frlg, CinnabarIsland_PokemonLab_Lounge_Frlg, CinnabarIsland_PokemonLab_ResearchRoom_Frlg]
flags: [FLAG_POX_STORY_FUJI, FLAG_POX_MANSION_KEY, FLAG_POX_ARCHIVE_1, FLAG_POX_ARCHIVE_2, FLAG_POX_STORY_MANSION, FLAG_POX_ENTEI, FLAG_BADGE05_GET]
badges: [5]
trainers: [TRAINER_PLASTIC_OX_BLAINE, TRAINER_PLASTIC_OX_ENTEI_SAGE]
items: [ITEM_SECRET_KEY, ITEM_HM04, ITEM_HM06, ITEM_MOON_STONE, ITEM_STRENGTH_KEY]
status: implemented
---

# Cinnabar Island

## Snapshot

A bare volcanic island at the end of the southern water road: one street, a gym, a burned mansion, a lab, and a harbour that no longer runs. The player comes in from the Route 103 passage, beats Blaine with no preamble, and uses the key he hands over to read what survived of the island's research. Stage 9 is where the game stops asking *what happened* and starts asking *who wrote it down*; the next thing the player hears is cold water.

## Plot points

1. **Arrival from Route 103.** `PoxRegion_route103_cinnabar_a` is gated on `FLAG_POX_STORY_FUJI` and puts the player at `(12,13)`, one tile under the return trigger at `(12,12)`. No cutscene, no greeter; the gym door at `(20,4)` is eight tiles east and nine north.
2. **Gym 5 is open immediately.** No lock, no gatekeeper. The live gym is the FRLG quiz-door maze — six questions, seven trainers — with Blaine at `(5,4)`. The gym guide at `(24,20)` runs `CheckCinnabarGymUURules` on the party and names any banned move or item as Blaine's house rule, as the other gyms' greeters do. It warns but does not block, and no species-tier roster exists anywhere in the game (see hooks).
3. **Blaine loses the badge but gives something better.** `Pox_Blaine` requires `FLAG_BADGE04_GET` and `FLAG_POX_STORY_FUJI`, fights `TRAINER_PLASTIC_OX_BLAINE` (fixed Lv.42 six: Omastar/Vileplume/Arcanine/Kangaskhan/Misdreavus/Solrock, none shiny), sets `FLAG_BADGE05_GET`, then runs `Pox_MansionKey`.
4. **The key comes with an errand he will not explain.** `ITEM_SECRET_KEY` plus `ITEM_HM04` and `ITEM_HM06`; his line says Fuji sent the player and the old records may explain him. He is a firefighter by temperament, not a theorist.
5. **The mansion door is locked in code.** `TryLockedMansionWarp` in `src/field_control_avatar.c` refuses the `(8,3)` warp without `ITEM_SECRET_KEY` and runs `PoxCinnabar_MansionLocked`. The woman at `(14,6)` says the same thing in fiction: statues, switches, a sage in the basement.
6. **The archives are the story and they are scattered.** `Pox_Archive1` on 2F `(25,4)`, `Pox_Archive2` on 3F `(8,16)`, `Pox_Archive3` on B1F `(21,27)`, chained by `FLAG_POX_ARCHIVE_1` / `FLAG_POX_ARCHIVE_2` and sealed with `FLAG_POX_STORY_MANSION`. Step 9: states are stored, reconciled, reconstructed — and someone once wired that to a network. Archive 3 names the Burned Tower, which is the whole point of coming here.
7. **Entei is in the basement and is not a boss.** `PoxCinnabar_EnteiSage` at `(5,7)` / `(6,7)`; the sage's six-Pokémon team ends with an Entei, then a second, scripted `SPECIES_ENTEI` appears at Lv.45 and any ball catches it. `FLAG_POX_ENTEI` removes both objects. The sage is the only NPC on the island who explains why legendaries are being followed.
8. **The sea opens last.** `PoxRegion_cinnabar_sea_a` on the east-edge water column `(23,9..11)` stays shut until `FLAG_POX_STORY_MANSION`, then warps to `MAP_PLASTIC_OX_ROUTE20_WEST` `(48,14)` — Seafoam, and no explanation. The Surf hop from the quay `(22,10)` onto `(23,10)` is not a step and fires nothing, so the column is three tiles: the first stroke along the edge crosses (fixed 2026-11-26; before, the player had to step off `(23,10)` and back).

**Must not:** name Bill, Silph, the adaptive system or "convergence"; let Blaine explain the archives; turn Entei into a Rocket operation or a Mewtwo reference; open the sea before the third archive; give the player a working ferry.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Blaine | gym `(5,4)` `Pox_Blaine` | badge 4 + Fuji | own refusal (`PoxIsles_BlaineNotReady`), firefighter challenge, "VOLCANO BADGE" line, key speech that says FUJI is the reason and that the two machines need their keys; after `FLAG_POX_STORY_MANSION` a last word (`PoxIsles_BlaineKey`) | shipped; the HM grants stay because `Pox_MansionKey` re-grants them on old saves |
| Gym quiz + guide | gym `(24,20)`, doors on `FLAG_CINNABAR_GYM_QUIZ_1`–`6` | `FLAG_DEFEATED_BLAINE` is an alias of `FLAG_BADGE05_GET` | guide (`PoxIsles_CinnabarGymGuide`) describes the real team, checks the party against the house rules (banned move or item named, else "nothing BLAINE would object to"), then congratulates; all six doors open once the badge is held; seven trainers and the quiz rules speak as the island's quiz pool; statue names the player after badge 5 | shipped; the check warns, it does not block, and species tiers are not checked (see hooks) |
| Mansion neighbour | town `(14,6)` `PoxIsles_MansionGuide` | `FLAG_POX_MANSION_KEY`, `FLAG_POX_STORY_MANSION` | three states: locked house, "SECRET KEY" + statues + the sage, then "you were in there a long time" | shipped |
| Gym regular | town `(11,11)` `PoxIsles_GymRegular` | `FLAG_BADGE05_GET`, `FLAG_POX_STORY_MANSION` | three states; bets tomatoes on the quiz | shipped |
| Mansion door | town `(8,3)` | no key | `PoxCinnabar_MansionLocked`: chained door, brass tag "KEY HELD AT THE GYM. BLAINE" | shipped |
| Archive 1–3 | 2F `(25,4)`, 3F `(8,16)`, B1F `(21,27)` | key, then flags in order | typed files in first-person plural; out of order each shelf has its own sealed line (`PoxIsles_Archive1Sealed`–`3Sealed`); a read file can be read again; file 3 ends on the Burned Tower margin note and a shipping slip "via SEAFOAM, to the observatory at MOSSDEEP" | shipped |
| Mansion staff and burglars | 1F `(22,24)`, `(8,8)`; 2F–B1F trainers; 2F log `(6,31)` | always | the `ITEM_STRENGTH_KEY` archivist is sent by Blaine; burglars find only paper; the Mew diary is a station log | shipped |
| Entei sage | B1F `(5,7)` / `(6,7)` `PoxIsles_EnteiSage` | `FLAG_POX_STORY_MANSION` (archive FILE 3) | Ecruteak-formal: Entei is a guest, "MORTY asked for patience. He did not ask for a leash." Before FILE 3 he asks the player to read all three files first | shipped; waits for archive 3 |
| Dock hand | town `(22,11)` `PoxIsles_DockHand` | `FLAG_BADGE05_GET`, `FLAG_POX_STORY_MANSION` | three states: business with Blaine first; Blaine's rule that nobody crosses with the house unread; "the east channel is yours" with directions to Seafoam's door. The closed sea column answers with his whistle (`PoxRegion_cinnabar_sea_a`) | shipped; replaces `Pox_MossdeepRoad` / `Pox_WhirlGuide` |
| Islanders | town `(17,5)` `PoxIsles_Greenhouse`, `(6,10)` `PoxIsles_LabTech`; Center, Mart and Lab interiors | always | greenhouse tomatoes in volcanic steam, the Lab's coffee pot, a stranded ferry passenger, the quiz pool, a field-team note about ice on the nets | shipped |
| Dead islanders | town Bill / Seagallop; Center Bill | — | town props deleted; the Center's One Island Bill and two journal props hidden behind `FLAG_POX_HIDE_UNUSED_ACTOR` (they were always visible and Bill's Sevii ferry script ran) | shipped |
| Signs | town `(12,14)`, `(22,9)` | always | "ROUTE 103 / The mainland road." and "EAST QUAY / ROUTE 20 - SEAFOAM ISLANDS / FERRY SERVICE SUSPENDED" | shipped; each is still an object plus a bg event on one tile |

## Dialogue guidance

- **Blaine** is a firefighter who ended up a scientist's caretaker. Short declaratives, no lectures, no mysticism. He talks about the mansion the way a man talks about a house he has been keeping locked: as a liability, not a mystery. He respects Fuji and says so once.
- **The gym guide and the quiz trainers** are the island's comic register — stubborn, quiz-obsessed, proud of a gym that has no challengers. They should talk about the tier rules as house rules, not game rules.
- **The archive is a voice, not an NPC.** First-person plural, 1970s-typed: cautious, procedural, faintly frightened of its own success. Never chatty, never a hint-dropper.
- **The sage** is Ecruteak-formal: slow, courteous, unhurried by the player's badge count. He speaks about Entei as a guest, never a prize.
- **Harbour and greenhouse people** carry the island's economy: what the boat brought, what the ash did to the crop, why the ferry stopped. Practical, bored, warm.
- After `FLAG_POX_STORY_MANSION`, the island should feel *finished with you* — the guides have less to say, the sea is the only direction left.

> GYM GUIDE: Door's been open since spring. Blaine won't lock a gym. He'll lock a house, though.

> BLAINE: Fuji's hand is on the envelope. That is the only reason you're getting this key, so don't make me regret the handwriting.

> ARCHIVE, 3F: We stored them as states, not specimens. That distinction cost us a year and it is the only part of this work I would defend.

> SAGE: It came up out of the ash on the lower floor and would not leave. I have been sitting with it since. Morty asked for patience; he did not ask for a leash.

> DOCK HAND: Sea's flat as a plate and I still can't take you anywhere. Ask the house on the hill what it's waiting for.

- **Do not:** let anyone say "convergence", "system", "Silph" or "Bill"; explain transfer theory in an NPC's own words; make the mansion a jump-scare dungeon or the archive a prophecy.

## Inspiration

- **Heimaey, Iceland, after the 1973 eruption** — a town half-buried in ash, dug out street by street, greenhouses downstream of a geothermal plant growing tomatoes in steam. Converts directly: a greenhouse worker, sulfur on the windowsills, an economy that runs on the boat schedule.
- **A 1970s marine field station** (Woods Hole, Plymouth): index cards, carbon paper, one typewriter, hand-ruled tables, a coffee pot that is never off. That is the archive's prose voice and the reason the records are fragments rather than exposition.
- **Herculaneum's carbonised scrolls** — records that survived because the place burned. The mansion is not haunted; it is *filed*. Papers too brittle to move, a caretaker who will not let you take one downstairs.
- **FRLG's own Cinnabar and an off-season onsen town** — quiz doors and the "Burning Desire" sign, but also empty inns, a caretaker sweeping a dry gutter, and a ferry timetable with the last sailing scratched out. Keep the quiz as a local ritual (residents bet on the six answers); the timetable is the harbour NPCs' whole personality.

## Implementation hooks

- Wiki page: `cinnabarisland-frlg.html`
- Maps: `CinnabarIsland_Frlg` (`MAP_CINNABAR_ISLAND`, `LAYOUT_CINNABAR_ISLAND`); live interiors `CinnabarIsland_Gym_Frlg` (`MAP_CINNABAR_ISLAND_GYM`), `PokemonMansion_1F_Frlg` … `PokemonMansion_B1F_Frlg`; story rooms `PlasticOx_BlaineGym` (`MAP_PLASTIC_OX_BLAINE_GYM`, Rustboro gym layout), `PlasticOx_Mansion` (`MAP_PLASTIC_OX_MANSION`, Rustboro Devon 2F layout)
- Scripts: `data/scripts/plastic_ox_story.inc` (`Pox_Blaine`, `Pox_MansionKey`, `Pox_Archive1`–`Pox_Archive3`, `Pox_MansionExit`, `Pox_BlaineGymExit`), `data/scripts/plastic_ox_cinnabar.inc` (`PoxCinnabar_MansionLocked`, `PoxCinnabar_MansionGuide`, `PoxCinnabar_GymGuide`, `PoxCinnabar_EnteiSage`), `data/scripts/plastic_ox_region.inc` (`PoxRegion_cinnabar_sea_a`), `data/maps/PokemonMansion_B1F_Frlg/scripts.inc`
- Gates: `ITEM_SECRET_KEY` check in `src/field_control_avatar.c`; archive chain `FLAG_POX_ARCHIVE_1` → `FLAG_POX_ARCHIVE_2` → `FLAG_POX_STORY_MANSION`; sea portal `PoxRegion_cinnabar_sea_a`; the unguarded north connection to `MAP_ROUTE21_SOUTH`
- Trainers / items: `TRAINER_PLASTIC_OX_BLAINE`, `TRAINER_PLASTIC_OX_ENTEI_SAGE`; `ITEM_SECRET_KEY`, `ITEM_HM04`, `ITEM_HM06` from Blaine, `ITEM_STRENGTH_KEY` from the 1F scientist at `(22,24)`, hidden `ITEM_MOON_STONE` at 1F `(2,21)`
- Story rooms are **orphaned**: `PlasticOx_BlaineGym` and `PlasticOx_Mansion` have zero warps and nothing warps to them. The gym's Blaine is a generic `MAN_3`; its `PlasticOx_BlaineGym_EventScript_Greeter` (UU rules via `CheckCinnabarGymUURules`, which returns `CheckRustboroGymLittleCupRules` — it bans sleep, Thunder Wave, Baton Pass and Deep Sea Tooth, not off-tier species) has no object. The live gym therefore enforces no tier rule and runs seven vanilla FRLG trainers plus Blaine.
- Dialogue for the town, gym, Mansion, Lab, Center and Mart is authored in `plastic_ox/alpha/south_isles.py` (emits `data/scripts/plastic_ox_south_isles.inc`, prefix `PoxIsles_`); the locked door and the sage's speech are in `plastic_ox/alpha/cinnabar/events.inc`. Harness: `plastic_ox/demo/test_south_isles.py`.
- Known gaps: the live gym's rules check is the shared structural one (sleep, Thunder Wave, Baton Pass, Swagger, Deep Sea Tooth and the like). It warns through the guide and does not block Blaine, and there is no species-tier table to check UU legality against; the dead `CinnabarIsland_Gym_EventScript_Blaine` still carries badge 7 and TM38 logic; the dead 3F / B1F Mewtwo diary texts remain in the map scripts, unreferenced; each region sign exists twice (object plus bg event); `CinnabarIsland_hns` is a second, unreferenced town map with zero warps (its leftover guides are now flagged unused); the trade NPCs in the Lab lounge and the fossil room still speak vanilla service text.

## Open questions

- Which gym is canonical? Keep the FRLG quiz-door gym and delete the Rustboro-layout story room, or wire `PlasticOx_BlaineGym` and rebuild the quiz there so the UU greeter finally exists?
- Has `PlasticOx_Mansion` ever been reachable, and should its three-scientist room be retired in favour of the mansion floors that already hold the archive flags — with the Mewtwo diaries giving way to archive fragments?
- ~~Should the Entei ritual wait for `FLAG_POX_STORY_MANSION`?~~ Yes: since 2026-11-27 the sage and Entei share `PoxIsles_EnteiSage`, which holds until FILE 3 is read.
- The north connection to Route 21 South is open with no check, letting a stage-9 player surf back into Pallet Town; keep it as visible geography, or seal it until the postgame?
