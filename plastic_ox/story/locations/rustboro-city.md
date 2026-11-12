---
title: Rustboro City
slug: rustboro-city
kind: City
act: 1
stage: "1 — Rustboro and the early Cottage branch"
depth: full
wiki: rustborocity
maps: [RustboroCity]
also_maps: [RustboroCity_Gym, RustboroCity_DevonCorp_2F, RustboroCity_Flat2_3F]
flags: [FLAG_POX_STORY_ILEX, FLAG_BADGE01_GET]
badges: [1]
trainers: [TRAINER_PLASTIC_OX_ROXANNE]
items: [ITEM_QUICK_CLAW]
status: drafted
---

# Rustboro City

## Snapshot

The first real city: stone pavements, a Devon tower with tinted windows, a
Trainer's School that is mostly a hallway, and a Gym that smells of chalk dust
and wet rock. The player arrives after Ilex Forest, clears Gym 1, and can then
take the optional northern branch to Bill's Sea Cottage. Rustboro is where the
game first feels *civic* — traffic, offices, people commuting — and that
normality is the point.

## Plot points

1. **Gym 1 — Roxanne, Little Cup.** The first serious team-building check. The
   player should lose once, learn to build a full LC team on the nearby routes,
   and come back. Roxanne is a teacher first and a Leader second.
2. **Devon is ordinary.** Devon makes running shoes, PCs, and parts. Nobody
   here implies Devon built, caused, or knows about the merged geography. A
   Devon employee can be proud of a product and bored of the word "synergy".
3. **The Sea Cottage branch opens.** Route 24 north to Route 25 ends at Bill's
   cottage: grandfather caretaker, no Bill, first gift Eevee. It is optional and
   must stay optional (see `route-25.md`).
4. **Route 44 east is the Mt. Moon road.** A guide points east toward the
   mountain; the Rocket arc starts there and not before.
5. **The city remembers being a Hoenn city.** Petalburg-style woodwork, a
   Devon-sponsored school, and a coastline that is now also Johto's. Residents
   notice the mismatch in practical terms (deliveries, ferry schedules), never
   in lore terms.

**Must not:** have anyone in Rustboro explain the convergence, mention Bill's
Champion status, or treat Devon as sinister.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Gym entrance check | `RustboroCity_Gym` `(5,18)`/`(6,18)` | `FLAG_POX_STORY_ILEX` | gate script runs | keep; make refusal a schoolteacher's line, not a system message |
| Roxanne battle | Gym, `(5,2)` | badge 1 unset | `TRAINER_PLASTIC_OX_ROXANNE`, LC team, badge award | keep; add one pre-battle line about the class she cancelled |
| Roxanne after | Gym | badge 1 set | "new challenge waits" | one line about the player's team, not a quest marker |
| Route 44 guide | city `(22,34)` | always | "east road crosses ROUTE 44" | keep, but let her be going that way herself |
| Sea Cottage sign | city `(23,6)` | always | "ROUTE 24 - NORTH / BILL'S COTTAGE" | keep sign; it is foreshadowing by geography only |
| Trainer's School | school interior | always | vanilla FRLG children | rewrite: three students with three different wrong theories about type matchups |
| Devon employee | city `(13,34)` | always | vanilla transfer-student greeting | rewrite as a commuter who is late |
| Dead objects | city `(13,21)`, `(11,15)` | script `0x0` | Aqua member and scientist render with no script | remove or give one line each; a silent NPC reads as a bug |

## Dialogue guidance

- **Roxanne** is precise and encouraging, uses classroom vocabulary ("show me
  your opening", "that's a good answer") and never taunts. She should sound
  like someone who marks papers at night.
- **Devon staff** are proud of mundane things: the torque on a hinge, the
  warranty on a PC. They are the region's least mystical people.
- **Schoolchildren** are confidently wrong in specific, funny ways. They are
  the best place in the early game for type-chart comedy.
- **Commuters** talk about the day, not the world: a delayed shipment, a
  detour, a cousin visiting from "the other coast".
- Keep the register brisk. Rustboro sentences are shorter than Ecruteak's.

> ROXANNE: You built that team on the road? Then you already know more than
> half my class.

> SCHOOLBOY: Rock beats everything if you throw it hard enough. That's science.

> DEVON CLERK: The parts came in from the west coast. Don't ask me which west.

> COMMUTER: Third detour this month. At this rate I'll know the whole map before
> the city does.

- **Do not:** let any NPC say "because the regions merged" as an explanation.
  Do not mention Silph, Saffron, or Bill's research.

## Inspiration

- **Rustboro as a company town:** a mid-sized Japanese prefectural capital where
  one employer dominates — the bakery knows the shift schedule, the school has a
  Devon logo on the gym wall, the bus is always late.
- **Hoenn's Rustboro in RSE:** cut-stone streets, a Devon tower you cannot
  enter for most of the game, and a Gym that feels like a geology classroom.
- **Cottage-country England for the branch:** the north road narrowing into
  hedges, a cottage with a nameplate, a grandfather who offers tea before
  Pokémon.
- **Dialogue conversion:** give each city NPC a commute or an errand. The map's
  oddness shows up as logistics ("the lorry came from the wrong coast"), which
  is funnier and more human than lore.

## Implementation hooks

- Wiki page: `rustborocity.html`
- Maps: `RustboroCity` (`MAP_RUSTBORO_CITY`), `RustboroCity_Gym`,
  `RustboroCity_DevonCorp_2F`, `RustboroCity_Flat2_3F`; branch maps
  `Route24_hns`, `Route25_hns`, `Route25_BillsHouse_hns`
- Scripts: `data/maps/RustboroCity/scripts.inc`,
  `data/maps/RustboroCity_Gym/scripts.inc`, `data/scripts/plastic_ox_story.inc`
- Flags: `FLAG_POX_STORY_ILEX` (Gym gate), badge 1 flag
- Trainers: `TRAINER_PLASTIC_OX_ROXANNE` (LC), vanilla `TRAINER_JOSH`,
  `TRAINER_TOMMY`, `TRAINER_MARC` in the Gym
- Known gaps: two objects with script `0x0`; the school still uses vanilla
  FireRed text; `ITEM_QUICK_CLAW` is called out in the human todo list as a
  placeholder to replace with an EV/nature key item.

## Open questions

- Should the Trainer's School reward the EV/nature item mentioned in
  `plastic_ox/human_todo_list.txt`, or keep that for a later city?
