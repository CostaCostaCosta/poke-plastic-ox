---
title: Cinnabar Island
slug: cinnabarisland-frlg
kind: Town
act: 3
stage: "9 — Cinnabar and the Mansion"
depth: full
wiki: cinnabarisland-frlg
maps: [CinnabarIsland_Frlg]
also_maps: [PlasticOx_BlaineGym, PlasticOx_Mansion, CinnabarIsland_Gym_Frlg, PokemonMansion_1F_Frlg]
flags: [FLAG_POX_STORY_FUJI, FLAG_POX_MANSION_KEY, FLAG_POX_ARCHIVE_1, FLAG_POX_ARCHIVE_2, FLAG_POX_STORY_MANSION, FLAG_POX_ENTEI, FLAG_BADGE05_GET]
badges: [5]
trainers: [TRAINER_PLASTIC_OX_BLAINE, TRAINER_PLASTIC_OX_ENTEI_SAGE]
items: [ITEM_SECRET_KEY, ITEM_HM04, ITEM_HM06, ITEM_MOON_STONE, ITEM_STRENGTH_KEY]
status: drafted
---

# Cinnabar Island

## Snapshot

A bare volcanic island at the end of the southern water road: one street, a gym, a burned mansion, a lab, and a harbour that no longer runs. The player comes in from the Route 103 passage, beats Blaine with no preamble, and uses the key he hands over to read what survived of the island's research. Stage 9 is where the game stops asking *what happened* and starts asking *who wrote it down*; the next thing the player hears is cold water.

## Plot points

1. **Arrival from Route 103.** `PoxRegion_route103_cinnabar_a` is gated on `FLAG_POX_STORY_FUJI` and puts the player at `(12,13)`, one tile under the return trigger at `(12,12)`. No cutscene, no greeter; the gym door at `(20,4)` is eight tiles east and nine north.
2. **Gym 5 is open immediately.** No lock, no gatekeeper. The live gym is the FRLG quiz-door maze — six questions, seven trainers — with Blaine at `(5,4)`. His "UU" tier is supposed to be checked; the greeter that would do it is on an orphan map (see hooks).
3. **Blaine loses the badge but gives something better.** `Pox_Blaine` requires `FLAG_BADGE04_GET` and `FLAG_POX_STORY_FUJI`, fights `TRAINER_PLASTIC_OX_BLAINE` (Lv.40–42 Arcanine/Ninetales/Rapidash/Electrode/Muk/Tentacruel), sets `FLAG_BADGE05_GET`, then runs `Pox_MansionKey`.
4. **The key comes with an errand he will not explain.** `ITEM_SECRET_KEY` plus `ITEM_HM04` and `ITEM_HM06`; his line says Fuji sent the player and the old records may explain him. He is a firefighter by temperament, not a theorist.
5. **The mansion door is locked in code.** `TryLockedMansionWarp` in `src/field_control_avatar.c` refuses the `(8,3)` warp without `ITEM_SECRET_KEY` and runs `PoxCinnabar_MansionLocked`. The woman at `(14,6)` says the same thing in fiction: statues, switches, a sage in the basement.
6. **The archives are the story and they are scattered.** `Pox_Archive1` on 2F `(25,4)`, `Pox_Archive2` on 3F `(8,16)`, `Pox_Archive3` on B1F `(21,27)`, chained by `FLAG_POX_ARCHIVE_1` / `FLAG_POX_ARCHIVE_2` and sealed with `FLAG_POX_STORY_MANSION`. Step 9: states are stored, reconciled, reconstructed — and someone once wired that to a network. Archive 3 names the Burned Tower, which is the whole point of coming here.
7. **Entei is in the basement and is not a boss.** `PoxCinnabar_EnteiSage` at `(5,7)` / `(6,7)`; the sage's six-Pokémon team ends with an Entei, then a second, scripted `SPECIES_ENTEI` appears at Lv.45 and any ball catches it. `FLAG_POX_ENTEI` removes both objects. The sage is the only NPC on the island who explains why legendaries are being followed.
8. **The sea opens last.** `PoxRegion_cinnabar_sea_a` at `(23,10)` stays shut until `FLAG_POX_STORY_MANSION`, then warps to `MAP_PLASTIC_OX_ROUTE20_WEST` `(48,14)` — Seafoam, and no explanation.

**Must not:** name Bill, Silph, the adaptive system or "convergence"; let Blaine explain the archives; turn Entei into a Rocket operation or a Mewtwo reference; open the sea before the third archive; give the player a working ferry.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Blaine | gym `(5,4)` `Pox_Blaine` | badge 4 + Fuji | badge text is the shared generic "You received a GYM BADGE!" | name the Volcano Badge; cut the HM grants, keep only the key |
| Gym quiz + guide | gym `(24,20)`, doors on `FLAG_CINNABAR_GYM_QUIZ_1`–`6` | `FLAG_DEFEATED_BLAINE` never set | vanilla "BURN HEALS" advice; doors reopen only from quiz flags | one UU warning; open all six doors once `FLAG_BADGE05_GET` is set |
| Mansion guide | town `(14,6)` `PoxCinnabar_MansionGuide` | `ITEM_SECRET_KEY` | three-line hint; good content | keep, but stop calling it a "MANSION KEY" in one line and `ITEM_SECRET_KEY` in code |
| Mansion door | town `(8,3)` | no key | `PoxCinnabar_MansionLocked` correctly refuses | keep; add a line after the key is used |
| Archive 1–3 | 2F `(25,4)`, 3F `(8,16)`, B1F `(21,27)` | key, then flags in order | three "ARCHIVE:" monologues read by bookshelves | keep the order behaviour, rewrite as documents in period voice, add an explicit "sea road" line on 3 |
| Entei sage | B1F `(5,7)` / `(6,7)` | none beyond the key | full legendary ritual already implemented | decide whether it waits for archive 3; vary the reward text |
| Seafoam directions | town `(11,12)` `Pox_MossdeepRoad`, `(13,12)` `Pox_WhirlGuide` | always | two near-identical lines that ignore the closed sea | one tells the truth ("not till the mansion's read"), one talks about the water |
| Dead islanders | town `(20,7)` Bill, `(23,7)` Seagallop | hidden from new game | objects with script `0x0`, mute if ever shown | delete both; Bill must not stand on this island |
| Signs | town `(12,14)`, `(22,9)` | always | "Marked passage ahead." twice, each doubled by a bg event on the same tile | place names: Route 103, Route 20 / Seafoam |

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
- Known gaps: `FLAG_DEFEATED_BLAINE` is never set, so the gym guide's post-victory branch is dead and the six doors never auto-open after a win; the dead `CinnabarIsland_Gym_EventScript_Blaine` still carries badge 7 and TM38 logic; 3F's diary says Mew gave birth to Mewtwo and B1F's says Mewtwo is too powerful — both contradict the archive story; Blaine gives HMs 04/06 whose field use is actually gated by `ITEM_STRENGTH_KEY` / `ITEM_ROCK_SMASH_KEY`, so his "these will help you" line is false; Bill and Seagallop are hidden, scriptless objects; each sign exists twice (object plus bg event); "I'll show you back outside." is used verbatim by two ushers; `Pox_WhirlGuide` is a legacy name for a Seafoam NPC; `CinnabarIsland_hns` is a second, unreferenced town map with zero warps.

## Open questions

- Which gym is canonical? Keep the FRLG quiz-door gym and delete the Rustboro-layout story room, or wire `PlasticOx_BlaineGym` and rebuild the quiz there so the UU greeter finally exists?
- Has `PlasticOx_Mansion` ever been reachable, and should its three-scientist room be retired in favour of the mansion floors that already hold the archive flags — with the Mewtwo diaries giving way to archive fragments?
- Should the Entei ritual wait for `FLAG_POX_STORY_MANSION`, so the legendary cannot arrive before the reveal it is meant to illustrate?
- The north connection to Route 21 South is open with no check, letting a stage-9 player surf back into Pallet Town; keep it as visible geography, or seal it until the postgame?
