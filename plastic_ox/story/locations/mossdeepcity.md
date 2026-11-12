---
title: Mossdeep City
slug: mossdeepcity
kind: City
act: 3
stage: "11 — Mossdeep and the Space Center"
depth: full
wiki: mossdeepcity
maps: [MossdeepCity]
also_maps: [MossdeepCity_Gym, MossdeepCity_SpaceCenter_1F, MossdeepCity_SpaceCenter_2F]
flags: [FLAG_POX_STORY_SPACE_CENTER, FLAG_POX_GIFT_SPACE, FLAG_BADGE06_GET, FLAG_POX_STORY_MANSION, FLAG_RECEIVED_KINGS_ROCK, FLAG_RECEIVED_OLD_ROD]
badges: [6]
trainers: [TRAINER_PLASTIC_OX_TATELIZA]
items: [ITEM_NET_BALL, ITEM_KINGS_ROCK, ITEM_OLD_ROD]
status: drafted
---

# Mossdeep City

## Snapshot

The island at the bottom of the map: white rock and wish tags on the shore, a harbour that runs on tides, a Space Center that runs on launch windows. The player comes ashore from Seafoam's east exit, wins Tate & Liza's UUBL double battle for Badge 6, then walks into the Space Center, where a scientist reads the journey back to them as a measurement. That report is reveal-ladder step 11, and the same flag opens every Saffron surface entrance. The emotional note is **competence**: everyone here has a job with a schedule, and nobody is impressed by the player.

## Plot points

1. **Arrival is a working port.** South shore `(0,20)` (`PoxRegion_sea_mossdeep_b`) opens on `FLAG_POX_STORY_MANSION`, so the seam is Cinnabar-shaped: the player walks in off the Seafoam crossing, not out of a cutscene. North `(40,0)` goes to Route 19; the sailor at `(38,12)` says it reaches Saffron long before the gate does.
2. **Gym 6 — Tate & Liza.** `Pox_TateLiza` at `(23,7)`/`(24,7)` requires `FLAG_BADGE05_GET` and `FLAG_POX_STORY_MANSION`, refuses with fewer than two healthy Pokémon (`Pox_Text_TwoMons`), and sets `FLAG_BADGE06_GET`. UUBL double battle; the Gym is a teleport-tile and floor-switch puzzle, so the walk is the puzzle and the fight is the payoff.
3. **The report — reveal-ladder step 11.** `Pox_SpaceReport` at 1F `(7,2)` is gated on `FLAG_BADGE06_GET` and sets `FLAG_POX_STORY_SPACE_CENTER`. It may state exactly three things: the region is not arranged randomly, habitats and strong Trainers have become easier to reach, and transfer traffic converges on Saffron at Silph Co. from a source they cannot identify. Play it as a measurement, not a monologue.
4. **Saffron opens — step 12.** The same flag releases the Route 19 → Saffron gates and the Route 8, Route 7, and Route 5 gates. Nothing else is required; Bruno and Silph remain unresolved and the report must not pretend otherwise.
5. **Eevee, fifth gift.** After the report, the scientist at 1F `(5,7)` hands over `SPECIES_EEVEE` (Lv 5) under `FLAG_POX_GIFT_SPACE`. Frame it as a study animal being retired to a good home, not a prize for clearing a Gym.
6. **The town turns over.** The Old Rod fisherman `(54,4)` only parts with `ITEM_OLD_ROD` after `FLAG_BADGE06_GET`; use the badge as the signal to stop being polite to the player. The Pokéfan's "letter" rumour should point at the launch schedule, not at a threat.
7. **Must not:** stage a villain occupation of the Space Center; mention Magma, Aqua, or Rocket; name Bill; let anyone say "convergence"; explain who built anything or why; resolve the mystery. Silph may be named as a destination only.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Saffron road | city `(38,12)` `Pox_SaffronRoad` | always | "northern coast leads through ROUTE 19 to SAFFRON" | two states on `FLAG_POX_STORY_SPACE_CENTER`: shut before the report, open after; keep it as directions |
| South shore seam | city `(0,20)` `PoxRegion_sea_mossdeep_b` | `FLAG_POX_STORY_MANSION` unset | generic "This passage is still closed" and a warp back | keep the lock; name the Seafoam crossing, not "your next objective" |
| Gym leaders | Gym `(23,7)`, `(24,7)` `Pox_TateLiza` | badge 5 + Mansion; two healthy mons | badge 6, shared `Pox_Text_Badge`; refusal is global `Pox_NotReady` | own refusal line; split the badge line so "the next road" is Saffron |
| Gym trainers | Gym, twelve trainer scripts | always | vanilla RS defeat lines (dust bunny, "the indecisive lose") | keep the psychic-teen register; diff strings so no two share a line |
| The report | 1F `(7,2)` `Pox_SpaceReport` | `FLAG_BADGE06_GET`, then flag set | one long box; flag flips at the end | two beats — observation, then Saffron — with a silent walk to the window between |
| Field staff | 1F `(2,2)`,`(6,6)`,`(10,2)`,`(14,7)`; 2F `(6,2)`,`(11,8)`,`(5,6)` | always | all say "Our field researchers can explain…" | one redirect at 1F `(2,2)`; the rest get jobs: docking clerk, scheduler, school group, telemetry |
| Villain leftovers | city `(44,23)`–`(44,26)`, `(45,25)`; 1F `(10,2)`,`(11,6)`,`(12,9)`,`(13,2)`; 2F `(12,2)`,`(13,3)`,`(14,2)`,`(0,8)`,`(1,9)` | script `0x0` or the redirect | Magma grunts, Maxie, Tabitha as dead props; two objects share 1F `(10,2)` | delete, or re-skin as staff; never script them as villains |
| White rock | city `(56,21)` | always | wish-tag speech for safe launches | keep; the town's one piece of unironic ritual |
| King's Rock boy | city `(23,13)` | `FLAG_RECEIVED_KINGS_ROCK` | gives `ITEM_KINGS_ROCK`, "keep it a secret from STEVEN" | keep the secret; make it a trade of something he cannot use |
| Old Rod | city `(54,4)` | `FLAG_BADGE06_GET` | gives `ITEM_OLD_ROD`, mostly MAGNEMITE | keep the gate; he lends it once the harbour clears |
| Net Ball | city `(62,35)` | `FLAG_ITEM_MOSSDEEP_CITY_NET_BALL` | `ITEM_NET_BALL` | keep; place it on the tide line |
| Scott | city `(61,29)` | `VAR_SCOTT_STATE`; object removed after one talk | vanilla scout text about a "warning letter" | rewrite as a travelling talent scout; no Battle Frontier, no letter |

## Dialogue guidance

- **Who speaks:** harbour and range staff, Gym kids, the report scientist, Tate & Liza, the fisherman. The town may know launches, tides, ferry times, the Gym, and that the Space Center has been "counting something". Only the scientist may state the step-11 findings, and only after Badge 6.
- **Register:** island practicality. Short sentences, no exclamation marks, time measured in launch windows and tides. Nobody is awed by the player; the leaders are the local team, and the Space Center is a workplace with a queue.
- **Tate & Liza speak as one**, finishing each other's sentences. They are the only people in town who treat battle as a game rather than a job, and the only ones allowed to enjoy the player's arrival.
- **Before/after:** before the report, the center is a lobby and a deflection; after, staff are quieter, the scientist is packing, the Eevee is available, and the sailor's line flips from "shut" to "open".
- **Merged geography as logistics:** "the mainland is closer than it used to be" is allowed; an explanation of why is not.

> DOCK CLERK: Ferry's at six and six. If the wind's up, it's at six and whenever.

> SPACE CENTER SCIENTIST: We can measure the routes. We can't measure the reason. That's the part I'd like to hand to somebody else.

> TATE & LIZA: Two of us. Two of you. Everything after that is just manners.

> FISHERMAN: Thirty years off these steps. Mostly MAGNEMITE. The harbour's louder than the water now.

> SCHOOLKID: The board says the next launch is "soon". It's said "soon" since my brother was little.

- **Do not:** use "convergence", "simulation", "adaptive system", or Bill; name Magma, Aqua, or Rocket; have the report name the creator or the cause; let the Eevee gift feel like a medal; make the town a victim waiting to be saved.

## Inspiration

- **Tanegashima and Uchinoura:** a Japanese rocket island where the launch schedule is the civic calendar, schools close for a window, and fishing boats double as recovery boats. Jobs: range safety, telemetry, boat hire, an ice-cream van at the pad gate.
- **NASA launch-town rhythm:** countdown on a PA, "the window", wind holds, a diner that opens at four. Overheard: a scrub, a hold, a shipment that arrived early, a cousin on the mainland.
- **Mossdeep in RSE:** white rock and wish tags, Steven's house next door, the dive out to Sootopolis. Keep the rock as civic religion and Steven as the neighbour nobody name-drops in front of strangers.
- **A Japanese island ferry port:** salt corrosion, postcards and bait in the same cooler, a noticeboard with a date amended three times. That board is the Pokéfan's "letter", and it needs no villain.
- **Mission-control humour:** the deadpan of people who have postponed something eleven times. Give it to the scheduler and the school group, never to the director, who is the one person allowed to be tired.

## Implementation hooks

- Wiki page: `mossdeepcity.html`
- Maps: `MossdeepCity` (`MAP_MOSSDEEP_CITY`), `MossdeepCity_Gym` (`MAP_MOSSDEEP_CITY_GYM`), `MossdeepCity_SpaceCenter_1F` (`MAP_MOSSDEEP_CITY_SPACE_CENTER_1F`), `MossdeepCity_SpaceCenter_2F` (`MAP_MOSSDEEP_CITY_SPACE_CENTER_2F`)
- Scripts: `data/scripts/plastic_ox_story.inc` (`Pox_TateLiza`, `Pox_SpaceReport`, `Pox_Space`, `Pox_SaffronRoad`, `Pox_FacilityWorker`), `data/maps/MossdeepCity/scripts.inc`, `data/maps/MossdeepCity_Gym/scripts.inc`
- Trainers / items: `TRAINER_PLASTIC_OX_TATELIZA` (six mons, Lv 44–46, Leftovers-heavy), `ITEM_KINGS_ROCK`, `ITEM_OLD_ROD`, `ITEM_NET_BALL`
- Known gaps: fourteen dead Magma/Aqua objects (five in town with script `0x0`, nine in the Space Center, one overlapping pair at 1F `(10,2)`, Tabitha on a male Magma sprite); nineteen NPCs (ten on 1F, nine on 2F) share the single `Pox_FacilityWorker` redirect; legacy Hoenn flags `FLAG_MET_PROF_COZMO`, `FLAG_DEFEATED_MOSSDEEP_GYM`, and `FLAG_RECEIVED_HM_DIVE` are all defined as `0`, so the Pokéfan's and Gym guide's "after" branches can never fire; the report flag flips inside one msgbox; 2F has no content beyond duplicates; the leader record uses `Pic: Leader Roxanne` with `Gender: Male` for a two-person team.

## Open questions

- Is 2F a room or a view? Recommend one post-report scene at the window, then retire the stairs; the current nine duplicates are worse than an empty floor.
- Delete the Magma clusters, or re-skin them as Space Center staff? Recommend delete — the sprites alone spoil Act V's "no villain crisis" rule.
- Split the report at the flag, or keep one box? Recommend split: the flag currently flips mid-conversation, hiding the moment Saffron opens.
- Should Steven appear in the Space Center at all? He is a Mossdeep neighbour and a League-tier trainer; recommend one line, no League reference.
- Is the Old Rod's Badge 6 gate deliberate? It is the only gift tied to the Gym, and it makes the badge feel civic rather than heroic.
