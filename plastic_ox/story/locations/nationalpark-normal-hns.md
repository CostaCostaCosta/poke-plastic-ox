---
title: National Park Normal
slug: nationalpark-normal-hns
kind: Route
act: 1
stage: "3 — Goldenrod to Ecruteak"
depth: full
wiki: nationalpark-normal-hns
maps: [NationalPark_Normal_hns]
also_maps: [Gate_NationalPark_hns]
trainers: [TRAINER_PLASTIC_OX_JOHTO_BEVERLY, TRAINER_PLASTIC_OX_JOHTO_JACK, TRAINER_PLASTIC_OX_JOHTO_KRISE, TRAINER_PLASTIC_OX_PU_PARK]
items: [ITEM_FULL_HEAL, ITEM_CONTEST_PASS]
status: drafted
---

# National Park Normal

## Snapshot

A walled meadow between two gatehouses: mown paths, flowerbeds, a fountain, bug catchers in the long grass and a class sitting under the trees. Traversal is the point — it is the mandatory Stage 3 passage and the schedule's official breath — so the map must reward dawdling rather than push. The note is a Sunday afternoon in a city park, with a contest queue on the other side of the gate.

## Plot points

1. **The breathing space (beat 5).** `STORY_TRIGGERS.md` files the park as "mandatory geographic passage, catching/trainer respite; no plot escalation". Nothing here advances the mystery, and nothing here may gate it. Four winnable trainers, one hidden item, one berry line — that is the whole content contract.
2. **The Bug-Catching Contest is a calendar, not a quest.** Tuesday and Saturday are open; Thursday needs `ITEM_CONTEST_PASS` and pays out Scyther and Pinsir. The gate crowds appear on contest days via `Gate_NationalPark_OnTransition` (hiding them with the temp flag aliased `FLAG_POX_HIDE_PARK_CONTEST_CROWD`).
3. **The pass is further away than the NPC says.** The Gameboy Kid at `(35,28)` sends players to "the tournament in the Saffron Underground", but Saffron is sealed until the Space Center; the real pass comes from the tournament host (`PoxTournament_Host`, round one gated on `FLAG_BADGE04_GET`). Fix the pointer, or the park's best side activity reads as a dead end.
4. **A Johto park with Hoenn grass.** The encounter table is Tropius-heavy alongside Hoppip, Lickitung and Jigglypuff (Hoothoot and Spinarak on the night table). That is a convergence tell, and it must stay a logistics detail — a keeper's note about a southern species overwintering, never an explanation.
5. **Dead furniture.** Two `OBJ_EVENT_GFX_POKE_BALL` objects at `(3,43)` and `(39,15)` carry flavour text and no item, and five text labels (`Npc2`, `Npc5`–`Npc8`, `Npc10`) exist with no object attached. Either is fine as writing; neither is fine as a player experience.

**Must not:** put Rocket, Silph, Bill or a researcher here; let the contest gate story progress; explain why Tropius lives in Johto; let any NPC say "convergence". The park is where the player is allowed to forget the plot.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| South gate | `(11,49)`–`(14,49)` | always | warps to `Gate_NationalPark_hns` | keep; four tiles is generous, do not narrow it |
| East gate | `(40,19)` | always | warps to the same gatehouse | keep; contest entrants arrive this way |
| Contest officials | gate `(1,6)`, `(41,2)`, `Gate_NationalPark_EventScript_Officer` | Thursday vs other days | two identical men, one schedule line | dedupe: one schedule, one queue-management voice |
| Contest attendants | gate `(3,2)`, `(38,2)` | day of week | `PlasticOxContest_EventScript_Attendant` register / enter / prize | keep; the only functioning contest UI on the map |
| Contest crowd | gate, five contestants | Tue/Thu/Sat | all five say the identical contest sentence | differentiate by the bug they are carrying and what they are worried about |
| Pass pointer | `(35,28)`, `NationalPark_Normal_EventScript_Npc3` | always | "Win one in the tournament in the Saffron Underground" | point at the real tournament host, or make the line a rumour with a shrug |
| Class under the trees | `(32,42)`, `Npc4` | always | teacher with caterpillars | keep; the best-written line in the park, build the school around it |
| Grove couple | `(17,4)`, `Npc9` | always | old woman whose husband planted the saplings | keep; she is the park's memory and should have a second line after the contest |
| Trainers | `(11,27)` Beverly, `(25,30)` Jack, `(11,13)` Krise | unbeaten | Lv. 20 Johto teams | keep; three different reasons to be in the park, not three gatekeepers |
| PU trainer | `(25,9)`, `Pox_PU_PARK` | unbeaten | `TRAINER_PLASTIC_OX_PU_PARK`, six Lv. 20 | keep; his "this meadow is for training" line is the map's thesis |
| Ball-shaped objects | `(3,43)`, `(39,15)` | always | `POKE_BALL` graphics, flavour text, no item | give each a real item or delete the objects |
| Hidden item | `(33,44)` | once | `ITEM_FULL_HEAL` | keep; put it near the flowerbeds so the teacher's line earns it |
| Cut tree | `(26,3)` | no Cut | `EventScript_CutTree` | keep; something small and optional behind it |

## Dialogue guidance

- **Park staff** speak in procedure: opening times, which gate the queue uses, where the bins are, who is allowed on the flowerbeds. They like the park and are tired of the public.
- **The teacher** is the map's heart: specific, unhurried, faintly disapproving of book-only biology. She should never mention badges.
- **Children** are confidently wrong about bugs in ways an adult would not correct. The Gameboy Kid is a child with an adult's misinformation.
- **The old woman** speaks in decades, not days. One sentence about her husband, one about the saplings, and no sentimentality beyond that.
- Before/after contest: staff switch to results talk, the crowd thins, the teacher keeps teaching. Nothing else changes, because the park does not care who won.

> TEACHER: Put the caterpillar down gently. It has spent all morning being looked at.

> OLD WOMAN: My husband planted that row the year we married. He was wrong about the spacing, and he was right about the shade.

> GAMEBOY KID: Thursday's the real one. Passes come from the tournament — ask anyone who's been.

> PARK ATTENDANT: Tuesday and Saturday you just queue. Thursday you show the pass, and then you queue anyway.

**Do not:** explain the merged geography, have a ranger mention Saffron's seal, or turn the contest into a story gate. Do not reuse the trainers' battle lines as NPC filler.

## Inspiration

- **Ueno and Yoyogi parks on a Sunday:** mown edges, a fountain people circle, a queue forming at one gate while the rest of the park ignores it. Converts directly into staff, queue and crowd NPCs.
- **The Japanese summer bug-catch (`mushi-tori`):** children with nets and cages, a parent with a cooler, a contest judged on size and health. This is the park's whole cultural engine.
- **Municipal park noticeboards:** laminated rules, a lost-and-found, a schedule with a hand-written correction. Perfect place for the contest schedule and for the "not in this build" honesty.
- **Ranger uniforms and gate logs:** two men on a gate who know exactly how many people came through and resent the question. Dedupe the two officials into one talker and one note-taker.
- **Tropius as an agricultural escapee:** in-world, a southern species that followed the seed trade north and now winters here. Keeper's note, not lore dump; the local birdwatchers are delighted and slightly alarmed.

## Implementation hooks

- Wiki page: `nationalpark-normal-hns.html`
- Maps: `NationalPark_Normal_hns` (`MAP_NATIONAL_PARK_NORMAL_HNS`), `Gate_NationalPark_hns` (`MAP_GATE_NATIONAL_PARK_HNS`)
- Scripts: `data/maps/NationalPark_Normal_hns/scripts.inc` (`NationalPark_Normal_EventScript_Npc1`, `Npc3`, `Npc4`, `Npc9`, `Npc11`, `Npc12`; `Pox_PU_PARK` in `data/scripts/plastic_ox_story.inc`); `data/maps/Gate_NationalPark_hns/scripts.inc` (`Gate_NationalPark_OnTransition`, `Gate_NationalPark_EventScript_Officer`, `_Contestant`, `_SouthAttendant`, `_EastAttendant`); `data/scripts/plastic_ox_contest.inc`
- Flags: `FLAG_POX_HIDE_PARK_CONTEST_CROWD` (an alias of `FLAG_TEMP_1`, so it must be re-derived on every map load)
- Items: hidden `ITEM_FULL_HEAL` at `(33,44)`, `ITEM_CONTEST_PASS` as the Thursday entry requirement; trainers `TRAINER_PLASTIC_OX_JOHTO_BEVERLY`, `_JACK`, `_KRISE`, `TRAINER_PLASTIC_OX_PU_PARK`
- Known gaps: two item-looking props with no item; five orphan text labels; five identical contestants and two identical officials; the Contest Pass pointer names a location that is sealed when the player first reads it.

## Open questions

- Do we want a return loop for the Thursday contest, or is "come back after badge 4" enough? Recommendation: let the Gameboy Kid say the pass comes from the tournament, and leave the return trip unsignposted.
- Should the gate crowd appear on all three contest days at full strength, or thin out for Tuesday/Saturday? Five clones look like a bug whichever day it is.
- Does the park ever connect onward (Ruins of Alph, a Johto-side exit), or is it permanently a two-gate cul-de-sac? The map currently has no onward connection, which makes it the safest place in the region.
