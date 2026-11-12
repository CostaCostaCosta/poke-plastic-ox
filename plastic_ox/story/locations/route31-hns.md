---
title: Route 31
slug: route31-hns
kind: Route
act: 1
stage: "0 — Opening network"
depth: supporting
wiki: route31-hns
maps: [Route31_hns]
flags: [FLAG_POX_HIDDEN_R31_POKEBALL, FLAG_POX_HIDDEN_R31_ANTIDOTE]
items: [ITEM_POKE_BALL, ITEM_ANTIDOTE]
trainers: [TRAINER_PLASTIC_OX_ROUTE31]
status: drafted
---

# Route 31

## Snapshot

A 60×23 hillside road that used to lead to Dark Cave, now a retired map with no warps, no connections and no wild encounters. Four people still stand on it — a bug catcher with foreign pollen in his nets, a night worker asleep at the wrong sunrise, a boy repeating a friend's cave story — and they are the strongest opening-network writing in the repo. This note is an audit and a salvage plan, not a scene; nothing on it is reachable today.

## Plot points

1. **The seam is one-way and dead.** `Route30_hns` still declares `up` to `Route31_hns` (offset -10); `Route31_hns` declares nothing back, holds zero warps and zero coord events, and `plastic_ox/alpha/region_v7.py` lists it in the `retired` set, which strips warps and truncates `Route31_hns_MapScripts` to a bare `.byte 0`. Walking in from Route 30 strands the player with no exit.
2. **The residents are already written.** Wade `(23,17)`, the sleepy man `(18,11)` and the boy `(9,9)` each make one observation about a road that arrived from elsewhere, each with a job attached. That is reveal-ladder **step 1** at its ceiling; nobody connects anything.
3. **The fourth man is a duplicate.** `(50,13)` runs `PoxRouteTrainer_Route31` — `TRAINER_PLASTIC_OX_ROUTE31`, Bug Catcher WADE, six Lv.9: the same name, class and party as `TRAINER_PLASTIC_OX_ROUTE2_WADE`, the live Wade on `Route2_Frlg` at `(9,8)`. The copy wears a Youngster sprite and speaks the shared generic trainer lines.
4. **The cave sign promises nobody.** `(50,10)` reads "DARK CAVE - southern entrance", but there is no warp on this map. The real southern mouth is `Route46_hns` at `(20,11)`, into `DarkCave_SouthSide_hns`.
5. **Two orphan scripts and two orphan items.** `Route31_EventScript_Youngster` exists with no object using it and carries the best text on the map; the sign at `(8,8)` says "ROUTE 30 - south, toward CHERRYGROVE CITY". `ITEM_POKE_BALL` at `(44,8)` (`FLAG_POX_HIDDEN_R31_POKEBALL`) and `ITEM_ANTIDOTE` at `(13,14)` (`FLAG_POX_HIDDEN_R31_ANTIDOTE`) are stranded.

**Must not:** invent a scene, NPC or quest for this map; wire a Dark Cave warp to make the sign true; present it as live in the wiki; name Bill, Rocket, Silph or the convergence; give Wade a lecture on Bug types.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Wade | `(23,17)`, `Route31_EventScript_Wade` | no object state | Hoenn pollen in his nets; "bugs don't carry maps" | salvage the line to `Route2_Frlg` or the Dark Cave mouth |
| Sleepy man | `(18,11)`, `Route31_EventScript_SleepyMan` | always | sunrise on the wrong side of the mountain; "don't tell the sun I complained" | salvage as a night-shift worker, not a witness |
| Boy | `(9,9)`, `Route31_EventScript_Boy` | always | friend entered Dark Cave, exited elsewhere; "caves can't move. Right?" | salvage to Route 46's cave mouth |
| Duplicate Wade | `(50,13)`, `TRAINER_PLASTIC_OX_ROUTE31` | trainer, always | identical to the live Wade; shared "local POKéMON" text | delete with the map, or rename and move |
| Orphan youngster text | no object, `Route31_EventScript_Youngster` | unreachable | "the signs agree with each other. Nobody else does." | give to a Route 46 NPC or drop |
| Dark Cave sign | `(50,10)`, `Route31_EventScript_DarkCaveSign` | always | promises a southern cave entrance that does not exist | delete; Route 46 already has the mouth |
| Seam | `Route30_hns` up edge | connection offset -10 | one-way step into a dead end | remove `Route31_hns` from the connection, or rebuild both maps |

## Dialogue guidance

- **Who speaks if salvaged:** three people whose road no longer needs them. Wade mends nets for insects that do not belong; the sleeper works nights; the boy is repeating a friend's story badly and knows it.
- **Register:** plain, dry, one image per speaker. Nobody theorises, nobody shivers, nobody says "odd".
- **Before / after:** no state survives retirement. If the map is restored, the only shift is that the cave sign becomes true.

> WADE: Hoenn pollen. My nets are for moths, not weather.

> SLEEPY MAN: I work nights. The morning keeps arriving on the wrong ridge, and nobody will take a complaint.

> BOY: He went in at the top and came out a day's walk from where he started. He's not a liar, so the cave is.

> YOUNGSTER, UNUSED SCRIPT: The signs agree with each other. Nobody else does.

- **Do not:** explain the road; make the cave "move"; give anyone a theory about regions; turn the sleeper into comic relief; let Wade name a species he is not carrying.

## Inspiration

- **GSC Route 31** — the first bug catcher, the Dark Cave mouth, a road that is mostly a corridor to somewhere else. That is the net-mender's whole job.
- **Japanese cedar-pollen season** — masks, nets, symptoms, everyone with an opinion. Converts into Wade's "foreign pollen" line and his ruined equipment.
- **A rural bus stop whose route was cancelled** — pole, timetable, shelter, no bus. This map *is* that stop; the sign is the timetable.
- **A landslide that moved the skyline** — farmers reading a sunrise over a ridge that was not there last year. That is the sleeper, if he is kept.

## Implementation hooks

- Wiki page: `route31-hns.html`
- Maps: `Route31_hns` (`MAP_ROUTE31_HNS`, `LAYOUT_ROUTE31_HNS`, 60×23); no interiors, no warps
- Scripts: `data/maps/Route31_hns/scripts.inc`; `PoxRouteTrainer_Route31` in `data/scripts/plastic_ox_route_trainers.inc`
- Retirement: `plastic_ox/alpha/region_v7.py` `retired` set; no `PoxRegion_*` objects survive, and `MAPSEC_ROUTE_31` still renders on the region map
- Trainers / items: `TRAINER_PLASTIC_OX_ROUTE31` (duplicate of `TRAINER_PLASTIC_OX_ROUTE2_WADE`), `ITEM_POKE_BALL`, `ITEM_ANTIDOTE`
- Known gaps: no wild encounters at all; no warps or connections; one-way connection from `Route30_hns`; duplicate trainer; unused youngster text; cave sign without a cave; music `MUS_RG_ROUTE1`

## Open questions

- Keep or retire? Recommend retire the map and salvage the three voices into `Route46_hns` and `Route2_Frlg`; restoring it means rebuilding the Route 30 seam and inventing a second Dark Cave mouth that Route 46 already owns.
- If kept, the duplicate Wade must be renamed or folded into the live Route 2 Wade — two identical trainers with the same name is a data smell.
- Move the two hidden items to Route 46, or retire them with the map?
