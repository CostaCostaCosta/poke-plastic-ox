---
title: Route 101
slug: route101
kind: Route
act: 1
stage: "0 — Opening network"
depth: full
wiki: route101
maps: [Route101]
status: drafted
---

# Route 101

## Snapshot

A twenty-by-twenty-tile strip of bright Hoenn meadow pinned between Pallet's north fence
and Oldale's south gate: the first place the player may walk into grass. No trainer, no
gate, no cutscene — two children, one sign, seven species in the weeds. Its job in the badge
spine is to make the player catch something before Route 29 asks them to fight with it, and
its emotional note is *permission*: the game stepping back and letting them wander.

## Plot points

1. **The first step out of Pallet.** The connection down to `PalletTown_Frlg` (offset -2) leaves
   the player at the town's north fence. Nothing checks them here; the only gate in the opening
   is Pallet's beach gate. Reveal-ladder step 1 was spoken in the lab and this route adds nothing.
2. **Grass is the first verb.** Wild table `gPoxRoute101` holds Wurmple, Poochyena, Taillow,
   Lotad, Seedot, Surskit and Slakoth at Lv. 2–4. Lotad *and* Seedot in one patch — a
   version pair in Hoenn — is the quiet evidence that the world is stitched; the player
   should notice the mix, never hear it explained.
3. **The youngster is the tutorial.** At `(16,8)` `Route101_EventScript_Youngster` says one
   Pokémon was not enough and the trainers ahead are strong. He means Route 29's two
   trainers; there is no trainer on this map. He is the replacement for the "first trainer
   battle" the human todo list asked to delete.
4. **The boy at `(2,13)` has crossed a seam without noticing.** A Poochyena followed him up
   from Pallet; he asks whether he smells different to the Pokémon here. A joke about bodies,
   not about geography.
5. **The sign at `(5,9)` only points forward.** "ROUTE 101 / OLDALE TOWN". Nothing points
   back to Pallet; the player is expected to keep walking.

**Must not:** name the convergence, Bill, Silph, Team Rocket or any system; place a rival, a
cutscene, a forced battle or a gift; imply the player is chosen; promise trainers on Route
101 that do not exist.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Youngster warning | `Route101` `(16,8)` `Route101_EventScript_Youngster` | always; no flag | two boxes: one Pokémon wasn't enough, trainers ahead are strong | keep the warning, but tie it to Route 29's two real trainers and to catching, not losing |
| Boy and the Poochyena | `Route101` `(2,13)` `Route101_EventScript_Boy` | always | "sniffed my shoes all the way up from PALLET"; "do I smell different?" | keep; swap the rhetorical second box for one smell a kid would name |
| Route sign | `Route101` `(5,9)` `Route101_EventScript_RouteSign` | always | "ROUTE 101 / {UP_ARROW} OLDALE TOWN" | keep; optional second line in walking time, which is how locals measure |
| Wild encounters | whole map, `gPoxRoute101` | `WEATHER_SUNNY`, rate 20 | 7 species, Lv. 2–4 | keep; no static encounter, no scripted battle |
| Map-load hook | map transition, `PoxRegion_Arrival_Route101` | always | empty stub (`..._End:: end`) | leave empty, or one one-time "Poké Balls work here" nudge; never exposition |

## Dialogue guidance

- Only two people speak here, both children. Their world is Pallet behind them, Oldale
  ahead, and whatever they can see from the path.
- **Youngster** at `(16,8)` is eleven or twelve and repeats adult advice with total
  confidence. Orders, one clause per box. He does not change after the player wins anywhere.
- **Small boy** at `(2,13)` talks about his own body and about animals, never about regions.
  Short sentences and one question he cannot answer.
- **The sign** is the only institutional voice on the map: plain, faintly proud.
- Register: bright, loud, unembarrassed, out of breath — a village footpath on a warm
  afternoon. There is no before/after shift, and that is the point: nothing happens here.

> YOUNGSTER: Two's not a team. Two's a hobby. Get a third before you go looking for a fight.

> BOY: It followed me the whole way and I didn't even have food. So what was it smelling?

> SIGN: ROUTE 101 — OLDALE TOWN. Twenty minutes, unless you stop in the grass.

- **Do not:** explain why Hoenn grass sits beside a Kanto town; let either child say region,
  convergence or professor; give the first route a "you must be the one" flavour.

## Inspiration

- **RSE Route 101:** the shortest route in Hoenn, the first grass, the zigzag ledges, a game
  that hands over the controls without instructions. At 20×20 this version doubles as the
  seam between FRLG Pallet's white fences and ORAS Oldale's pastel hedges.
- **A real footpath between two villages in late summer:** cut grass drying on a verge, a dog
  that follows you a mile, school bags by a gate — and the sound of cicadas, a bicycle
  freewheel, someone calling a kid in for lunch. Sun, no wind; the school holidays' last hour.
- **Conversion:** two social roles only — the child who repeats an adult warning, the child who
  asks a physical question. Overheard topics: animals, shoes, lunch. Never maps.

## Implementation hooks

- Wiki page: `route101.html`
- Maps: `Route101` (`MAP_ROUTE101`, `LAYOUT_ROUTE101`, `MUS_ROUTE101`); neighbours
  `PalletTown_Frlg` (`MAP_PALLET_TOWN`) south and `OldaleTown` (`MAP_OLDALE_TOWN`) north,
  connection offsets -2 and 0
- Scripts: `data/maps/Route101/scripts.inc` for all three labels above; the arrival hook
  `PoxRegion_Arrival_Route101` lives in `data/scripts/plastic_ox_region.inc`
- Encounters: `gPoxRoute101` in `src/data/wild_encounters.json`
- Known gaps: **0 warp events**, so a future scene here must be a map script, not a door; the
  arrival hook is an empty stub; both human-todo items for this route ("npc says grass is
  quiet", "remove first trainer battle") look already resolved. No flags, items or trainers are
  attached — keep it that way.

## Open questions

- Does Route 101 want a one-time catching hint now that Oak's Pokédex has just been handed
  over, or is wordless grass the better tutorial?
- Is the seven-species Lv. 2–4 pool with both Lotad and Seedot deliberate for the Little Cup
  phase, or should one of the pair move to Route 29?
- Keep the ORAS-style Hoenn tileset against FRLG Pallet, or retexture this seam? The human todo
  complains about Pallet's southern water, not this border.
- Slakoth at Lv. 2–4: intentional novelty, or a stalling trap for a player with no catches yet?
