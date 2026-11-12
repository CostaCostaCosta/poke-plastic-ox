---
title: Oldale Town
slug: oldaletown
kind: Town
act: 1
stage: "0 — Opening network"
depth: full
wiki: oldaletown
maps: [OldaleTown]
status: drafted
---

# Oldale Town

## Snapshot

Four doors, four roofs and a crossroads: a 20×20 Hoenn village with a Mart, a Center, a footprint
enthusiast, and roads leaving in three directions. The player passes through once on the way west to
Route 29, takes a free Potion, and reads the north exit as "not yet" without being told. Its emotional
note is *first services* — the first hint that this map is a network, not a line.

## Plot points

1. **Arrival from Route 101.** Down-connection from `PalletTown_Frlg`; otherwise only `Route29_hns`
   west (offset -6) and `Route103` north. Nobody greets the player, and step 1 was spent at Pallet.
2. **The Potion handoff.** `OldaleTown_EventScript_MartEmployee` at `(13,7)` gives `ITEM_POTION` once
   under `FLAG_RECEIVED_POTION_OLDALE`, with a bag-full retry and a reminder afterwards — the last free
   item before the first trainers.
3. **The footprints man.** `(8,9)` `LOCALID_FOOTPRINTS_MAN` is gated on `FLAG_ADVENTURE_STARTED`:
   before it he blocks the path insisting he has found a rare Pokémon's prints; after it he admits
   they were his own. The town's single joke, and it works because he is entirely serious.
4. **The girl at `(16,11)` is a menu.** `OldaleTown_EventScript_Girl` explains saving progress — an RSE
   leftover. The Center already teaches saving; she should be a person waiting for someone.
5. **The north road is a promise the town cannot keep yet.** The up-connection opens onto `Route103`, an
   unrewritten RSE donor map with 22 objects, a vanilla May battle (`TRAINER_MAY_ROUTE_103_TREECKO`) and
   Birch's Pokédex-rating scene; it dead-ends, with no warps and no northern link. Version 7 later uses
   Route 103 for the Lavender→Cinnabar bypass, so this exit reads as "later", never as west.
6. **Two legacy actors are hidden, not deleted.** The rival at `(11,19)` (`LOCALID_OLDALE_RIVAL`), hidden
   by `FLAG_HIDE_OLDALE_TOWN_RIVAL`, still runs the Emerald May/Brendan exit scene and writes
   `VAR_OLDALE_RIVAL_STATE`. Lance at `(10,11)`, hidden by `FLAG_POX_HIDE_BATTLE_LANCE`
   (`src/new_game.c`), still holds a six-Pokémon ADV OU team (`TRAINER_PLASTIC_OX_LANCE`) and calls the
   player "P".

**Must not:** show either legacy actor in a normal file; run a rival scene; name Route 103's later role
or the Cinnabar chain; explain the convergence; make the town motto ironic.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Potion gift | `(13,7)` `OldaleTown_EventScript_MartEmployee` | `FLAG_RECEIVED_POTION_OLDALE` unset | gives `ITEM_POTION`; bag-full retry; reminder after | keep the in-place gift; a shopkeeper who also lives here |
| Footprints man | `(8,9)` `OldaleTown_EventScript_FootprintsMan` | `FLAG_ADVENTURE_STARTED` unset / set | blocks the path boasting of rare prints; later admits they were his own | keep the block and the punchline; make the evidence specific — stride, claws, wet mud |
| Girl | `(16,11)` `OldaleTown_EventScript_Girl` | always | "I want to take a rest, so I'm saving my progress" | someone waiting for a delivery, sitting because the bench is there |
| Town sign | `(11,9)` `OldaleTown_EventScript_TownSign` | always | "OLDALE TOWN — Where things start off scarce." | keep; it is the town's whole thesis |
| Legacy actors | `(11,19)` `OldaleTown_EventScript_Rival`, `(10,11)` `OldaleTown_EventScript_Lance` | `FLAG_HIDE_OLDALE_TOWN_RIVAL`, `FLAG_POX_HIDE_BATTLE_LANCE` | hidden at new game; live scenes if cleared | delete the rival; keep Lance's trainer id, never the object |

## Dialogue guidance

- **The Mart employee** is Oldale's closest thing to a narrator: he knows the delivery day, the stock,
  and which road the crates came in on. Practical, nosy, generous with a Potion.
- **The footprints man** is a hobby naturalist with a plaster cast and no self-doubt: measurements, no
  winking. **The girl** is resting and allowed to be bored.
- Register: flat, dry, domestic; sentences are short because everyone has said them before. Before the
  Potion the town is a corridor, after it a place with a person in it. Nobody knows the north road's future.

> MART EMPLOYEE: Crates came up from the coast this morning. One of them was ours. That's never
> happened before.

> FOOTPRINTS MAN: Four toes, no claw marks, and a stride like it was in a hurry. I've been sketching
> since dawn.

> GIRL: I'm not lost. I'm waiting. There's a difference, and it's mostly sitting down.

> SIGN: OLDALE TOWN — Where things start off scarce.

- **Do not:** explain the junction; guess Route 103's destination; mention Bill, Silph, Rocket or the
  convergence; resurrect the rival or the Lance battle as "a bit of fun".

## Inspiration

- **RSE Oldale:** the first town with a shop and the scarcity motto; here in ORAS-style pastel hedges.
- **A Japanese roadside station (michi-no-eki):** one shop, one bench, a noticeboard of roads you cannot
  take, vans idling, a clerk who knows every driver — and the amateur naturalist beside him with a
  footprint cast, bird list, camera bag and mud on his knees.
- **Conversion:** three jobs — shopkeeper, hobbyist, someone waiting — plus the sign. Overheard: deliveries,
  mud, timetables; the merged world reaches them only as "the crates came up from the coast".

## Implementation hooks

- Wiki page: `oldaletown.html`
- Maps: `OldaleTown` (`MAP_OLDALE_TOWN`, `LAYOUT_OLDALE_TOWN`, `MUS_OLDALE`); interior warps at
  `(14,6)` Mart, `(6,16)` Center, `(5,7)` and `(15,16)` houses — not covered here, and with no notes
- Scripts: `data/maps/OldaleTown/scripts.inc`; arrival hook `PoxRegion_Arrival_OldaleTown` in
  `data/scripts/plastic_ox_region.inc`
- Flags: `FLAG_RECEIVED_POTION_OLDALE`, `FLAG_ADVENTURE_STARTED`, `FLAG_HIDE_OLDALE_TOWN_RIVAL`,
  `FLAG_POX_HIDE_BATTLE_LANCE`; items: `ITEM_POTION`; trainer: `TRAINER_PLASTIC_OX_LANCE`
- Known gaps: dead rival and Lance objects (suppressed at new game, still scripted); the orphan string
  `OldaleTown_Text_WaitDontComeInHere` from the removed escort walk; a ten-slot fishing table (Wailord,
  Crawdaunt, Whiscash at Lv. 3–5) on a Stage-0 town square; double signs on the Center and Mart; human
  todo: "the transition north is really weird."

## Open questions

- Retire the rival object and its May/Brendan script outright, or keep it as a debug-only cameo?
- The Lance battle: gate it behind the Champion flag as a rematch, or delete the object and keep only
  the trainer id stable for the metamon harness? The alpha trainer report argues for the id.
- How should the north exit be blocked — an ordinary obstruction, or does Route 103 become a legitimate
  Act I detour once its donors are rewritten?
- Is Oldale meant to be fishable at all, or is that table donor noise? And do the four interiors belong
  here, or do the Mart and Center want one shared note, since the same maps serve every Johto town?
