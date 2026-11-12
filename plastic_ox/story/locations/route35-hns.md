---
title: Route 35
slug: route35-hns
kind: Route
act: 1
stage: "3 — Goldenrod to Ecruteak"
depth: full
wiki: route35-hns
maps: [Route35_hns]
also_maps: [Gate_GoldenrodCity_Route35_hns]
flags: [FLAG_POX_DELIBIRD_RECEIVED, FLAG_POX_DELIBIRD_DELIVERED]
trainers: [TRAINER_PLASTIC_OX_PU_ROUTE35]
status: drafted
---

# Route 35

## Snapshot

The first leg out of Goldenrod: a gatehouse at the city edge, then a long climb of rock, dry grass and picnic blankets to a second gatehouse that opens into the National Park. On the badge spine it is pure connective tissue — badge 2 is in hand, badge 3 is two maps away — so its job is to be a sociable breather. The note is a city emptying out behind you while the road fills with people who came here on purpose.

## Plot points

1. **Out of the city, through the gate.** South warps at `(13,48)`/`(14,48)` return to `Gate_GoldenrodCity_Route35_hns`; north warps at `(17,5)`/`(18,5)` reach `Gate_NationalPark_hns`. Mandatory Stage 3 corridor, one map wide, no alternate path: it must never soft-lock.
2. **Webster's bird (optional).** At `(20,6)` `POX_PU_MailGuard` offers his Delibird (Lv. 16, holding `MAIL`) for delivery to RANDY on `Route33_hns` — behind the player, back down the Mt. Moon road. Accepting sets `FLAG_POX_DELIBIRD_RECEIVED`; delivering sets `FLAG_POX_DELIBIRD_DELIVERED`. The backward errand is the point: it gives a finished road a second walk.
3. **The pasture with a trainer.** `TRAINER_PLASTIC_OX_PU_ROUTE35` at `(10,38)` fields six Lv. 20 partners; the grass is Yanma-heavy. This is the "build a PU team out of what lives here" lesson before Ecruteak.
4. **Reveal ladder: nothing here.** Step 4 at the very most (Goldenrod's domestic Bill-family texture) and this map uses none of it.
5. **The twelve-talker problem.** Twelve human-shaped objects share two alternating lines, and three are drawn as `POKE_BALL` pickups that yield nothing. Fix objects before prose: eight to ten distinct speakers, no decoys.

**Must not:** mention Rocket, Bill, Silph, the Contest, or the convergence; make Webster's errand mandatory or gate the park behind it; give the route a "the land remembers" moment (that is Ecruteak's, ladder step 5).

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| South gatehouse | `(13,48)`/`(14,48)` | always | warps to `Gate_GoldenrodCity_Route35_hns` | keep; the guard should notice a player coming back with a bird |
| Park gatehouse | `(17,5)`/`(18,5)` | always | warps to `Gate_NationalPark_hns` | keep; the contest schedule lives on the far side |
| Webster offer | `(20,6)`, `POX_PU_MailGuard` | `FLAG_POX_DELIBIRD_RECEIVED` unset | YES/NO box, `PlasticOxGiveMailDelibird`, Delibird Lv. 16 with MAIL | keep; give the NO branch a real line instead of a silent close |
| Webster retry / done | `(20,6)` | received, then `FLAG_POX_DELIBIRD_DELIVERED` | reissues bird or rewrites the letter; then "RANDY got my letter?" | keep both; add one line about the empty cage |
| Randy handoff | `Route33_hns`, `POX_PU_MailRecipient` | player holds the mail bird | delivers, sets the flag | keep; give him a reason to be near Mt. Moon that is not fossils |
| PU trainer | `(10,38)`, `Pox_PU_ROUTE35` | unbeaten | `TRAINER_PLASTIC_OX_PU_ROUTE35`, Lv. 20 | keep; her meadow line is the map's best |
| Route talkers | twelve objects, `Route35_EventScript_Npc2`–`Npc12` | always | "Rocky ground can wear your team down" / "The mountain draws hikers", alternating | one voice per band: gate approach, picnic slope, rock face, plateau |
| Ball-shaped objects | `(35,45)`, `(11,12)`, `(27,17)` | always | `OBJ_EVENT_GFX_POKE_BALL`, flavour text, no item | give each a real item or delete them |
| Cut tree / Persim tree | `(31,6)`, `(11,25)` | no Cut; daily berry | `EventScript_CutTree`, `PlasticOx_BerryTree_Persim` | keep; let a picnicker claim she planted the persim |
| South sign | `(15,46)` | always | "GOLDENROD CITY - SOUTH / Through the gatehouse." | keep; add walking time, not metres |
| Gatehouse trio | gate `(5,8)`, `(5,3)`, `(9,4)` | always | policeman, commuter, fisherman one-liners | keep all three; the best-written lines on either map |

## Dialogue guidance

- **Webster** is a man on a shift, not a quest dispenser: the bird's habits, the gate log, the wind on the hill. He accepts a no.
- **Route hobbyists** (picnicker, camper, rocker, hiker, bug catcher) talk about their own afternoon — the out-of-wind bench, what the rock face does to a training session, whether the park gate is still open. **Gate commuters** are in transit and know it: the shortcut through the gatehouse, the long walk to water, the hill they refuse to climb.
- Register: short, dry, present tense. Goldenrod irony, not Ecruteak gravity; nobody here is impressed by the player. After delivery Webster's lines shrink to practical thanks, and the picnickers never mention it, because nobody on the route knows about the errand.

> WEBSTER: She won't fly it if the wind's from the north. Walk her a bit first and she'll settle.

> PICNICKER: We claimed this blanket at nine. Half the city had the same idea by noon.

> HIKER: The rock face eats boots. These have been resoled twice since spring.

> GATE FISHERMAN: There's a pond two fields over. Two fields is a long way with a rod and a bad knee.

**Do not:** give Webster a marker, a reward speech, or knowledge of the player's badges. Do not reuse the PU trainer's "balanced team" line as generic filler. Do not let anyone explain the merged geography.

## Inspiration

- **Gen 2 Route 35:** the city-edge gatehouse, the fenced picnic lawn, the ledge drops that make the walk home different from the walk out. Keep the ledges.
- **Japanese hill parks (Ueno, Asukayama):** a thin green belt where office workers eat lunch on a slope, shared by joggers, strollers and one man with a fishing rod. Converts to commuter, restocker and "same loop every day" NPCs.
- **Postal carrier birds:** Japan Post scooters and the older pigeon tradition. Play Delibird as a work animal with a bad attitude and a favourite perch.
- **Autumn hill walking in Kansai:** dry grass, persim trees, wasps, a vending machine at the trailhead — the wasp-phobic picnicker, the machine restocker, the man who times his loop.
- **Overheard topic:** the queue at the park gate on contest mornings, and whether the hill path is worth the shortcut.

## Implementation hooks

- Wiki page: `route35-hns.html`
- Maps: `Route35_hns` (`MAP_ROUTE35_HNS`), gate `Gate_GoldenrodCity_Route35_hns`; neighbours `MAP_ROUTE36_HNS`, `MAP_GATE_NATIONAL_PARK_HNS`
- Scripts: `data/maps/Route35_hns/scripts.inc` (`Route35_EventScript_Npc2`–`Npc12`, arrival `PoxRegion_Arrival_Route35_hns`); `data/scripts/plastic_ox_pu_acquisitions.inc` (`POX_PU_MailGuard`, `POX_PU_MailRecipient`); `data/scripts/plastic_ox_region.inc` (`PoxRegion_goldenrod_route35_b_Sign`); `data/scripts/plastic_ox_story.inc` (`Pox_PU_ROUTE35`)
- Flags: `FLAG_POX_DELIBIRD_RECEIVED`, `FLAG_POX_DELIBIRD_DELIVERED`. Trainers: `TRAINER_PLASTIC_OX_PU_ROUTE35`
- Known gaps: 12 talkers sharing 2 texts; 3 `POKE_BALL`-gfx objects with no item; orphan labels `Npc1`, `Npc7`, `Npc9` with no object attached; the Delibird pair is the only state change on the map.

## Open questions

- Are the ledges real one-way drops or only the gate policeman's warning? If they are one-way, the return leg needs its own short scene.
- Should the three ball-shaped objects become the route's item finds (`ITEM_*` TBD) or be deleted? The dossier shows no item behind them.
- Keep the Delibird errand optional and give Webster one later line if the player returns without delivering, or is a delivered-or-nothing handoff cleaner? Recommendation: optional, with the extra line.
