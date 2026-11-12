---
title: Route 33
slug: route33-hns
kind: Route
act: 1
stage: "2 — Mt. Moon"
depth: full
wiki: route33-hns
maps: [Route33_hns]
flags: [FLAG_POX_DELIBIRD_DELIVERED, FLAG_POX_DELIBIRD_RECEIVED, FLAG_POX_STORY_MTMOON]
trainers: [TRAINER_PLASTIC_OX_PU_ROUTE33]
status: drafted
---

# Route 33

## Snapshot

The first daylight after Mt. Moon: a short green shelf of switchbacks, one hiker,
one man waiting for a letter, and a road that drops into Goldenrod. The player
walks out of the cave mouth at `(27,17)`, fights the only trainer on the map, and
takes the western edge into the city. Route 33 is a decompression route — its job
is to let a cave-battered team breathe before Whitney — so its emotional note is
relief with an undertow: the city is close, and it is much bigger than the cave.

## Plot points

1. **Out of the mountain.** `MtMoon_B1F_Frlg` warp 7 lands here at `(27,17)`. No
   cutscene, no guide. Give the player three steps of grass and sky before anyone
   speaks; the light change is the beat.
2. **Anthony's exam.** The hiker at `(17,20)` has sight 3 and
   `TRAINER_PLASTIC_OX_PU_ROUTE33` (six Lv.17 mons). He is the route's only fight
   and its real function: a full party check on the way out of a cave where it is
   easy to arrive with four usable Pokémon. He must be beatable, not a wall.
3. **The road to Goldenrod.** Three trigger tiles at `x=0` (`y=22`, `y=23`,
   `y=25`) run `PoxRegion_route33_goldenrod_a` and warp to `GoldenrodCity_hns`
   `(33,44)`. The authored requirement list for this trail is empty, so the road
   is open in every state; the only objective check on the Goldenrod side is
   Whitney's own `FLAG_POX_STORY_MTMOON` gate at the Gym.
4. **Randy and the letter.** The hiker at `(25,27)` runs `POX_PU_MailRecipient`.
   Before Webster's errand exists he only says he is expecting mail; once the
   player carries Delibird with the MAIL, he takes the delivery, sets
   `FLAG_POX_DELIBIRD_DELIVERED`, and gives the bird away for good. This is the
   route's only warm beat and it rewards a return trip, not a first visit.
5. **The headbutt tree.** A sign-posted tree at `(8,17)` runs
   `PlasticOx_EventScript_HeadbuttTree`; keep it, it is the only reason to walk the
   east side of the map.
6. **No reveal.** Nothing here advances the ladder. Rocket stays inside the
   mountain; the letter has nothing to do with the mountain.

**Must not:** put a Rocket grunt, a fossil, or a signal on this route; make Randy
a quest board or a mail-system tutorial; let Anthony's defeat line be shared with
every other trainer in the build; make the road a story gate it is not.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Cave mouth | `Route33_hns` `(27,17)` | always | warp to `MAP_MT_MOON_B1F` warp 7 | keep; add a small sign naming MT. MOON, not a guide NPC |
| Goldenrod road | `x=0`, `y=22`/`23`/`25` | `FLAG_POX_TRIGGERS_ENABLED` | `PoxRegion_route33_goldenrod_a` → `GoldenrodCity_hns` `(33,44)`; its `_Closed` branch is emitted but unreachable | decide whether the road itself should check `FLAG_POX_STORY_MTMOON` |
| Anthony | `(17,20)` | undefeated | `Pox_PU_ROUTE33` sight 3 → `TRAINER_PLASTIC_OX_PU_ROUTE33`, then `Pox_Text_PU_ROUTE33_After` ("a steady pace gets you up any mountain") | keep; give him his own defeat line instead of `Pox_Text_Defeat` |
| Randy, waiting | `(25,27)` | `FLAG_POX_DELIBIRD_RECEIVED` unset | "I'm RANDY. I moved here from ROUTE 31…" then a mail prompt the player cannot satisfy yet | rewrite as a homesick settler with no quest reference until the errand exists |
| Randy, delivery | same | Delibird in party holding the mail | takes the letter, `FLAG_POX_DELIBIRD_DELIVERED`, Delibird stays | keep; make the handover feel like a favour, not a reward screen |
| Randy, after | same | flag set | "Thanks again for WEBSTER's letter!" | one line, then silence; do not re-explain the quest |
| Sign | `(0,24)` | always | sign object **and** a bg sign on the same tile, both `PoxRegion_route33_goldenrod_a_Sign` | delete the object, keep the bg sign |
| Headbutt tree | `(8,17)` | headbutt key | `PlasticOx_EventScript_HeadbuttTree` | keep |

## Dialogue guidance

- **Randy** moved here from Route 31 for the quiet and has not settled in. He
  over-explains, thanks people twice, and talks about the letter before he talks
  about himself. He is lonely, not pitiful, and he never asks the player to fetch
  anything.
- **Anthony** is a fell runner with a stopwatch and strong opinions about pacing.
  He respects preparation, not talent, and he corrects himself mid-sentence. After
  the battle he stops coaching and starts gossiping.
- **The sign** is the third voice: municipal, cheerful, slightly out of date. It
  should read like paint, not a quest marker.
- Register: open air, long vowels, people who are in no hurry. Sentences are
  shorter after the cave than in Goldenrod, where everyone talks over each other.

> RANDY: I moved up from ROUTE 31 for the quiet. The cave hums at night — I've
> decided I like it. Ask me again in winter.

> ANTHONY: Steady pace. The mountain doesn't care how strong you are. It cares
> how early you started.

> ANTHONY: You came out with six standing. Most people lose one on the ladders.
> Eat something before the city.

> SIGN: GOLDENROD CITY — follow the road up into town. Mind the gravel on the
> last bend.

- **Do not:** have anyone mention Team Rocket here; explain where Delibird came
  from; use the words "convergence" or "region"; turn the sign into a tutorial.

## Inspiration

- **A mountain pass road:** stone retaining walls, a spring box, a cattle grid, a
  post with reflective paint. Converts to the road's geometry and to Anthony's
  pacing obsession.
- **Rural postal relay:** a red postbox, a carrier's scooter, a redelivery slip.
  Converts to Randy as a man who checks the box twice a day and admits it.
- **Gen 2 Route 33:** short, green, ledge-heavy, a breather between a cave and a
  town. Keep the length; cut the temptation to add a second story NPC.
- **Fell running:** a club that times itself uphill on Sundays and talks about
  weather the way other people talk about sport. That is Anthony's whole voice.
- **The city lights over a crest at dusk:** a one-time line, not an arrival
  cutscene. One passer-by, one sentence, and the road keeps going.

## Implementation hooks

- Wiki page: `route33-hns.html`
- Maps: `Route33_hns` (`MAP_ROUTE33_HNS`); the mouth connects to
  `MtMoon_B1F_Frlg`, the west edge to `GoldenrodCity_hns`
- Scripts: `data/maps/Route33_hns/scripts.inc` (arrival stub only),
  `data/scripts/plastic_ox_region.inc` (`PoxRegion_route33_goldenrod_a`),
  `data/scripts/plastic_ox_story.inc` (`Pox_PU_ROUTE33`, `Pox_ParkRoad`),
  `data/scripts/plastic_ox_pu_acquisitions.inc` (`POX_PU_MailRecipient`)
- Flags: `FLAG_POX_DELIBIRD_RECEIVED`, `FLAG_POX_DELIBIRD_DELIVERED`,
  `FLAG_POX_STORY_MTMOON` (checked at the Gym, not on this road)
- Trainers: `TRAINER_PLASTIC_OX_PU_ROUTE33` (ANTHONY, Lv.17 Spinda/Seviper/
  Zigzagoon/Hoppip/Aipom/Geodude)
- Known gaps: the sign object at `(0,24)` duplicates the bg sign on the same tile;
  `PoxRegion_Arrival_Route33_hns` is an empty stub; Anthony uses the shared
  `Pox_Text_Defeat` line; Randy's waiting text assumes a quest the player may not
  have been offered, because Webster stands in `Route35_hns`, one town later.
- Encounter table: 14–16 ZIGZAGOON, SPEAROW, HOPPIP, GEODUDE, EKANS, SPINDA,
  SEVIPER, ZUBAT.

## Open questions

- Should the Goldenrod road check `FLAG_POX_STORY_MTMOON`? Today only Whitney's
  Gym script enforces the Mt. Moon completion, which means the badge is gated but
  the road is not.
- Move Randy's letter hook behind the Delibird gift so a first-time player is not
  asked about mail that does not exist yet, or leave the foreshadowing?
- Retire the duplicate sign object, or move it a tile so the tile has one
  interaction?
- Does the route need a third voice (a porter, a sign painter) or is one hiker
  plus one settler the right population for a 20-second walk?
