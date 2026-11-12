---
title: Indigo Plateau
slug: indigoplateau-hns
kind: Town
act: 5
stage: "16 — Pokémon League"
depth: full
wiki: indigoplateau-hns
maps: [IndigoPlateau_hns]
also_maps: [PlasticOx_WallaceRoom, PlasticOx_StevenRoom, PlasticOx_LeagueLanceRoom, PlasticOx_BlueRoom, PlasticOx_BillRoom, PlasticOx_HallOfFame]
flags: [FLAG_POX_LEAGUE_WALLACE, FLAG_POX_LEAGUE_STEVEN, FLAG_POX_LEAGUE_LEAGUELANCE, FLAG_POX_LEAGUE_BLUE, FLAG_POX_LEAGUE_BILL, FLAG_SYS_GAME_CLEAR]
trainers: [TRAINER_PLASTIC_OX_WALLACE, TRAINER_PLASTIC_OX_STEVEN, TRAINER_PLASTIC_OX_LEAGUELANCE, TRAINER_PLASTIC_OX_BLUE, TRAINER_PLASTIC_OX_BILL]
items: [ITEM_LEFTOVERS, ITEM_FULL_RESTORE]
status: drafted
---

# Indigo Plateau

## Snapshot

The last dry mile: the player crests the north end of `PlasticOx_VictoryRoad` at `(12,18)`, crosses a bald, windy summit, and walks into a granite building that smells of floor polish and coffee. Inside, a lobby hands out healing, a shop, and a fixed five-match order — Wallace, Steven, Lance, Blue, then the Champion. No badge is awarded here; the badge spine ended at the Ecruteak gate, and everything from `(10,19)` upward is the exam. The emotional note is *administrative*: the League is a building where the last appointment of the day is the player, and the staff are polite because they are going home after this.

## Plot points

1. **The summit walk.** Arrival from Victory Road's north exit is silent — `PoxRegion_Arrival_IndigoPlateau_hns` is an empty stub, and that is correct. Reveal-ladder step 16 closes here: the long-shut western road has been walked, and the player now stands where the whole map was pointing.
2. **The last free U-turn.** The coordinate strip `(10,19)`–`(14,19)` (`PoxLeague_Downhill`) returns the player to Victory Road `(14,2)` with no confirmation. This is the last place where turning back costs nothing; after `(11,6)` it does not.
3. **The lobby brief.** `PoxLeague_Welcome` (`7,15`) explains the PC, the counter, and the official; `PoxLeague_Advice` (`29,10`) does the scouting; `PoxLeague_Shop` (`10,10`) stocks `ITEM_FULL_RESTORE` and `ITEM_LEFTOVERS`. The challenge itself is `PoxLeague_Entry` — the Black Belt at `(32,3)` or the trigger strip `(30,2)`–`(33,2)` — which re-checks all eight badges, calls `PoxLeague_Reset`, and warps the player to Wallace at `(6,11)`.
4. **Doors only forward.** Each room is one opponent at `(6,5)` and one exit trigger at `(6,2)`: `FLAG_POX_LEAGUE_WALLACE` → `PoxLeague_StevenNext`, and so on down the chain. A loss inside the run does not return the player to the lobby; it blacks out to Indigo and the run must be restarted from the official.
5. **Champion Bill — reveal-ladder step 17.** `PlasticOx_BillRoom`, `(6,5)`, `PoxLeague_Bill`, gated on the previous four flags. The banner line must be the flat announcement *CHAMPION BILL would like to battle* — no speech before it. Only `PoxLeague_Text_BillAfter` (which runs after the win and immediately warps to the Hall) is allowed to connect him to the transfer network and the adaptive system, and it must land as a confession of consequence, not a plan.
6. **The record.** `PlasticOx_HallOfFame`'s frame table fires `PoxLeague_Hall` on `VAR_TEMP_1 == 0`: Hall of Fame effect, `setrespawn`, `GameClear`, which sets `FLAG_SYS_GAME_CLEAR` and opens the Lavender south ferry. Bill's body at `(6,7)` (`PoxLeague_HallGuide`) speaks one line afterwards.

**Must not:** let any League staff member explain the convergence, Silph, the Weather Institute, or Bill's infrastructure before the Champion battle is won; make the Elite Four villains or conspirators; let Team Rocket appear; open Lavender south inside this node (only `FLAG_SYS_GAME_CLEAR` downstream of `GameClear` does that); turn the plateau into a temple, a ruin, or a mystery.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Summit arrival | `IndigoPlateau_hns` `(12,18)` | always | `PoxRegion_Arrival_IndigoPlateau_hns` returns immediately | keep silent; no cutscene, no guide |
| Downhill express | `(15,9)` `PoxLeague_Shortcut` | always | offers a ride to ECRUTEAK, warps to `MAP_GATE_ECRUTEAK_CITY_ROUTE38_HNS`, `(5,5)` | keep; she is the driver, and she keeps the weather log |
| Ridge walk-off | `(10,19)`–`(14,19)` `PoxLeague_Downhill` | always | silent warp to Victory Road `(14,2)` | keep no-confirm (map edge), but let the attendant warn about it |
| Building door | `(11,6)` → `IndigoPlateau_PokemonCenter_hns`, exit `(19,16)` | always | works, no sign | keep; new sign required at the door step |
| Lobby welcome | lobby `(7,15)` `PoxLeague_Welcome` | always | explains PC, counter, official, restart rules | keep; she is the only one allowed to explain procedure |
| Shop | lobby `(10,10)` `PoxLeague_Shop` | always | nine items including `ITEM_LEFTOVERS` and `ITEM_FULL_RESTORE` | keep; no gag about the price |
| Nurse | lobby `(19,10)` `PoxLeague_Nurse` | always | full heal, sets respawn to Indigo | keep; add that she has seen this queue before |
| Challenge official | lobby `(32,3)` / `(30,2)`–`(33,2)` `PoxLeague_Entry` | all eight `FLAG_BADGE0x_GET` | tally, yes/no, `PoxLeague_Reset`, warp to Wallace `(6,11)` | keep; he should log the loss, not console the player |
| Wallace | `PlasticOx_WallaceRoom` `(6,5)` `PoxLeague_Wallace` | `FLAG_POX_LEAGUE_WALLACE` unset | tempo speech, `TRAINER_PLASTIC_OX_WALLACE`, opens door `(6,2)` | keep; trim the speech to one image |
| Steven | `PlasticOx_StevenRoom` `(6,5)` `PoxLeague_Steven` | Wallace set | defensive-core speech, `TRAINER_PLASTIC_OX_STEVEN` | keep; he should talk about cover, not stone |
| Lance | `PlasticOx_LeagueLanceRoom` `(6,5)` `PoxLeague_LeagueLance` | Steven set | pressure speech, `TRAINER_PLASTIC_OX_LEAGUELANCE` | keep; shorter, blunter |
| Blue | `PlasticOx_BlueRoom` `(6,5)` `PoxLeague_Blue` | Lance set | adaptation speech, `TRAINER_PLASTIC_OX_BLUE` | keep; he watched all three, and should say one specific thing he saw |
| Bill | `PlasticOx_BillRoom` `(6,5)` `PoxLeague_Bill` | four flags set | friendly small talk, then `PoxLeague_Text_BillAfter` monologue | retime: one line, battle, then the confession |
| Shared loss text | all five rooms, `PoxLeague_Text_*Defeat` | after a player win | all five say "That was a battle to remember!" | five different lines — this is the loudest remaining vanilla seam |
| Hall guide | `PlasticOx_HallOfFame` `(6,7)` `PoxLeague_HallGuide` | after `FLAG_POX_LEAGUE_BILL` | one line: "Your partners have earned their place here." | he is the registrar; give him the plaque wording |

## Dialogue guidance

- **League staff speak in procedure.** Queue, badges verified, bag items, where the counter is. They are not awed by the player; they are near the end of a shift.
- **The attendant** is a driver with a timetable: wind, light, the last descent, who is still up on the ridge. She is the only person on the map who talks about the weather as a job.
- **The official** is a registrar. He counts, he confirms, he records outcomes. When the player loses, he does not comfort — he re-opens the book.
- **The Elite Four** each own one idea and should not borrow each other's: Wallace rhythm, Steven coverage, Lance commitment, Blue observation. No member mentions the system or the Champion's identity.
- **Bill before the battle** is ordinary, slightly awkward, pleased to see a face from the road — the Sea Cottage neighbour, not a boss. **Bill after** is precise, tired, and speaks in causes and consequences.
- After `FLAG_SYS_GAME_CLEAR`, the building's register drops: staff talk about closing up, and nobody re-explains the rules.

> ATTENDANT: Last descent is at dark. After that the ridge is yours and the wind's, and I am not coming back up for you.

> OFFICIAL: Eight verified. Four matches, then the Champion. If you fall, the book opens again and we start from the top — that is the rule, not a punishment.

> WALLACE: A battle has a beat. I will keep it, and you will have to break it.

> BLUE: Steven kept his wall up for six turns. Lance never let you breathe. I am going to do neither, and you will have to notice which.

> BILL: I built the foundations everyone trains on. Then the thing I built started moving ground I never touched. I have wanted to say that to someone who walked here.

- **Do not:** name Silph, the Weather Institute, or the adaptive system before the Champion is beaten; give Bill a villain's diction; let the Elite Four hint at a conspiracy; use "convergence"; explain why the plateau is where it is; write a heroic send-off in the Hall.

## Inspiration

- **Japanese mountain terminal stations** (Tateyama Kurobe, Koyasan cable): a timetable board, a last-descent announcement, staff who watch the cloud line. This is the attendant's entire job and the plateau's only weather talk.
- **Dan grading in kendo or a driving-test centre**: a queue of candidates, a numbered desk, examiners who each test one thing and never confer. Converts the Elite Four into four examiners, the official into the registrar, and the lobby into a waiting room with plastic chairs.
- **A regional sumo bashō's final day**: the venue is ordinary until the last bouts, then the ushers go quiet. Gives the Hall of Fame its hush and the "last appointment" feeling.
- **Alpine fell and scree**: tussock, no trees, wind that removes hats, a trig point. Justifies a bare summit map with no decoration and lets the door at `(11,6)` be the only warm thing in frame.
- **The Gen I Indigo Plateau lobby** as a shared Pokémon Center/League desk — the queue is the memory, not the architecture.

## Implementation hooks

- Wiki page: `indigoplateau-hns.html`.
- Maps: `IndigoPlateau_hns` (`MAP_INDIGO_PLATEAU_HNS`), plus the five rooms and Hall in `also_maps`; the lobby is `IndigoPlateau_PokemonCenter_hns`, which is not listed in the batch's `also_maps`.
- Scripts: `data/scripts/plastic_ox_league.inc` (`PoxLeague_Shortcut`, `PoxLeague_Downhill`, `PoxLeague_Welcome`, `PoxLeague_Entry`, `PoxLeague_Reset`, the four `PoxLeague_*Next` triggers, `PoxLeague_*After`, `PoxLeague_Hall`, `PoxLeague_HallGuide`); `data/maps/IndigoPlateau_hns/scripts.inc`; `data/scripts/plastic_ox_region.inc` (`PoxRegion_Arrival_IndigoPlateau_hns`, `PoxRegion_victory_indigo_a`).
- Gates: eight `FLAG_BADGE0x_GET` at `PoxLeague_Checkpoint` and again at `PoxLeague_Entry`; forward-only room chain via the five `FLAG_POX_LEAGUE_WALLACE`-style victory flags; `FLAG_SYS_GAME_CLEAR` set by `GameClear` in `PoxLeague_Hall`.
- Trainers: `TRAINER_PLASTIC_OX_WALLACE` .. `TRAINER_PLASTIC_OX_BILL`, levels 61–64, HP/status/PP carry between matches by design.
- Known gaps: all five rooms share the identical post-win string "That was a battle to remember!", so the finale reads as five copies of one line; Bill's `(6,5)` intro is friendly small talk that pre-empts the required flat "CHAMPION BILL would like to battle" announcement; the Hall guide reuses `OBJ_EVENT_GFX_BILL`, so two Bills stand in the same building; `IndigoPlateau_Exterior_Frlg`, `IndigoPlateau_PokemonCenter_1F_Frlg` and `..._2F_Frlg` exist with no warp, connection, or script pointing at them; the Hall scene's only guard is `VAR_TEMP_1`, set by the scene itself.

## Open questions

- Should `IndigoPlateau_PokemonCenter_hns` (the heal/shop/briefing lobby) be added to `also_maps`, or does the lobby belong to a separate note?
- Does the second Bill in the Hall represent the Champion signing the record, or should the Hall guide be a different body? Two identical sprites in one node is a visible seam.
- `PoxLeague_Reset` re-arms the whole challenge whenever the lobby loads, so the League is replayable after becoming Champion. Is that the intended rematch loop, or should a cleared save get a shorter challenge?
- Retire the three unreferenced FRLG Indigo maps (`IndigoPlateau_Exterior_Frlg`, `IndigoPlateau_PokemonCenter_1F_Frlg`, `IndigoPlateau_PokemonCenter_2F_Frlg`), or keep them as donor references? Nothing in `data/` targets them.
