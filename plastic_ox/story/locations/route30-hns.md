---
title: Route 30
slug: route30-hns
kind: Route
act: 1
stage: "0 — Opening network"
depth: supporting
wiki: route30-hns
maps: [Route30_hns]
also_maps: [Route30_House_hns, Route30_MrPokemonsHouse_hns]
flags: [FLAG_POX_HIDDEN_R30_POTION_1, FLAG_POX_HIDDEN_R30_POTION_2]
items: [ITEM_POTION]
status: drafted
---

# Route 30

## Snapshot

A reservoir road that used to be the way north out of Cherrygrove: a lake at the
top, a lane bending past it, two houses that take in walkers, and five people
with reasons to stand still. It awards no badge, and that is the point — here the
widened world shows up as traffic, water levels and a full kettle, not as a
story. The map is currently orphaned (audit below), so this note is the design
for the route as it should read once the seam is restored.

## Plot points

1. **The lake, then the lane.** The player comes up from Cherrygrove with the
   water on one side and the hill on the other. The road visibly continues past
   the lake; nobody treats that as remarkable. This is the route's whole
   introduction and it should take ten seconds.
2. **Two houses with two jobs.** The rest house at `(26,39)` is a bench, a
   kettle and a woodpile; the surveyor's house at `(35,4)` is a front room full
   of old notebooks. Both are reasons to knock, not quest stops.
3. **The local chorus.** Don counts bugs, Joey brags about a Rattata, the woman
   at `(20,13)` times her day by the Cherrygrove market, and the boy at
   `(26,31)` counts lorries. They are the first NPCs in the game who are simply
   busy; let the player overhear rather than interview.
4. **No reveal.** Reveal-ladder step 1 (the opening world) was spent in Pallet
   and is this route's ceiling. A resident may notice that the lane is busier
   and that a sign points somewhere they have not been; nobody connects it to
   anything larger.
5. **Seam audit — the map cannot be entered.** `Route30_hns` declares `up` to
   `Route31_hns` and `down` to `MAP_CHERRYGROVE_CITY_HNS`, but Cherrygrove's
   north edge now belongs to `Route2_Frlg`, and `Route31_hns` declares no south
   connection back. Nothing warps in and the only reciprocals are the two house
   doors. A debug warp that lands the player here strands them at
   `Route31_hns` if they walk north.

**Must not:** explain why the lane exists, promise a visitable Violet City, or
put Rocket, Bill, Silph or a region theory in anyone's mouth. Do not add a
climbable shortcut to `Route31_hns` to "fix" the seam.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Boy counting traffic | `Route30_hns` `(26,31)` | `Route30_EventScript_Boy` | lake used to be the north end; a road now goes "somewhere called VIOLET" | keep the observation and the lorry-counting; drop "never heard of it", since no Violet City map exists in the build |
| Joey | `(20,28)` | `Route30_EventScript_Joey` | trains a Rattata; a traveller showed him a Treecko | keep as bragging, never as a theory about where Treecko came from; one "top percentage" joke is enough |
| Woman by the water | `(20,13)` | `Route30_EventScript_Girl` | south is Cherrygrove; the sea "smells different" | rewrite to market logistics: the catch, the ice, the ferry timetable |
| Don the bug catcher | `(20,8)` | `Route30_EventScript_Don` | foreign bugs; a leaf-necked Pokémon not in his guide | keep; he should be cross about the blank page, not amazed by the world |
| Second youngster | `(21,26)` | `Route30_EventScript_JoeyDayOff` | even trainers need days off; might walk to Cherrygrove | two tiles from Joey with the same sprite: merge into Joey or re-cast as a cousin waiting for a lift with a different line |
| Route sign | `(31,29)` | `Route30_EventScript_Sign` | "ROUTE 30 - CHERRYGROVE CITY straight ahead" | keep the sign; face it down the Cherrygrove lane and name Route 31 on the reverse if signs get two sides |
| Trainer Tips board | `(20,19)` | `Route30_EventScript_TrainerTips` | "Routes no longer end where the map says they do... impossible geography" | replace: winking meta. A plain maintenance notice about loose gravel and spring flooding does the job |
| Rest house | `(26,39)` → `Route30_House_hns` `(4,4)` | `Route30_House_EventScript_Resident` | old man: travellers come through Route 30 from every direction | keep the line; give him a bench, a kettle and no directions |
| Surveyor's house | `(35,4)` → `Route30_MrPokemonsHouse_hns` `(5,4)` | `Route30_MrPokemonsHouse_EventScript_Resident` | gentleman: "I study the POKéMON that gather where the regions overlap." | rewrite as a retired surveyor whose elevation notes no longer match the hills; no overlap lecture, no egg |
| Hidden Potions | `(24,2)`, `(35,30)` | `FLAG_POX_HIDDEN_R30_POTION_1`, `FLAG_POX_HIDDEN_R30_POTION_2` | two hidden `ITEM_POTION` | keep; put one under the boat and one behind the woodpile |

## Dialogue guidance

- **The boy** narrates vehicles and water levels. He is the only person on the
  route who talks to the player first; keep him at one idea per line.
- **Joey** is a small-town competitor: confident, specific, faintly ridiculous.
  He should never say the word "region" twice in a conversation.
- **The woman** works; her sentences are about prices, ice and the ferry, and
  she is the one who mentions Cherrygrove without being asked.
- **Don** speaks in field notes: dates, weather, page numbers. The joke is the
  guidebook, not the Pokémon.
- **The old man** is unhurried and slightly deaf; **the surveyor** is precise
  and embarrassed that his instruments lie.
- Register: short declaratives, no exclamation marks except the boy's. If the
  seam is restored after Ilex, these people talk like commuters; before Ilex,
  like neighbours.

> BOY: Two lorries before lunch. Neither stopped. That's how you know it's a
> real road now.

> JOEY: Top percentage of this route. It's a small route. It still counts.

> DON: Rain on Tuesday, sun on Wednesday, and a bug on Thursday I've drawn on
> the back page because there isn't a front one for it.

> OLD MAN: Kettle's on. The bench is dry if you're quick about sitting.

> SURVEYOR: Every hill on this map is forty metres off where I wrote it. I've
> stopped blaming the ink.

- **Do not:** use "convergence", name Bill/Silph/Rocket, explain the lake as
  unnatural, or let anyone say "Violet City" as if the player can go there.

## Inspiration

- **Johto Route 30 in GSC:** the lake, the fork, Mr. Pokémon's kitchen-table
  research, and the feeling that Johto's routes are lived-in before they are
  dangerous. Convert the kitchen table into the surveyor's front room and the
  lake into a working reservoir with a valve house.
- **A reservoir lane in the Japanese hills, rainy season:** frogs in the
  overflow channel, gravel washed onto the tarmac, a tarp over a woodpile, one
  vending machine at the rest house. Jobs: reservoir keeper, bait and ice
  seller, part-time post runner.
- **The two households as small businesses:** a tea-and-bench rest stop and a
  retired surveyor who takes in odd jobs. Their talk is about customers,
  deliveries and the cost of ice, which is how the widened world should arrive
  here.
- **GSC's Route 30 theme (the slow Johto route music):** long gaps between
  events, a screen of tall grass, one trainer who is a kid. Let the silences do
  the work; this is the route to walk, not to clear.
- **Slice-of-life pacing (a summer-vacation comic, not an adventure one):**
  observations are the plot. The boy's lorry count and Don's back page are the
  equivalent of chapter titles.
- **Conversion:** give every NPC a route-adjacent job — water, ice, post,
  surveying, school run — and let each mention one inconvenience caused by
  traffic. No one needs to mention the map.

## Implementation hooks

- Wiki page: `route30-hns.html`
- Maps: `Route30_hns` (`MAP_ROUTE30_HNS`), `Route30_House_hns`
  (`MAP_ROUTE30_HOUSE_HNS`), `Route30_MrPokemonsHouse_hns`
  (`MAP_ROUTE30_MR_POKEMONS_HOUSE_HNS`)
- Scripts: `data/maps/Route30_hns/scripts.inc`,
  `data/maps/Route30_House_hns/scripts.inc`,
  `data/maps/Route30_MrPokemonsHouse_hns/scripts.inc`
- Flags / items: `FLAG_POX_HIDDEN_R30_POTION_1/2`, `ITEM_POTION`
- Known gaps: no reciprocal connection from Cherrygrove (its `up` is
  `Route2_Frlg`) and none from `Route31_hns`; no wild encounters at all; no map
  script; `Route30_Text_Boy` names Violet, which has no map; two Youngster
  objects two tiles apart; the Trainer Tips sign is meta; the surveyor's house
  has no gift; music is `MUS_RG_ROUTE1`, a Kanto route theme.

## Open questions

- Keep, rewire or retire? Recommended: keep only if a Violet-side branch is
  actually planned; otherwise retire `Route30_hns` and `Route31_hns` together
  and move the five NPC texts to a route that can be reached.
- Should the surveyor's house carry a once-only gift (new flag and item
  required), or be renamed so "Mr. Pokémon" is not a promise the map cannot
  keep?
- Add a wild table (currently none) so the route can carry the LC team-building
  phase, or leave it trainer-free and quiet?
