---
title: Victory Road
slug: plasticox-victoryroad
kind: Route
act: 5
stage: "15 — Victory Road"
depth: full
wiki: plasticox-victoryroad
maps: [PlasticOx_VictoryRoad]
also_maps: [PlasticOx_LeagueRestHouse1, PlasticOx_LeagueRestHouse2]
flags: [FLAG_POX_LEAGUE_REWARD_0, FLAG_POX_LEAGUE_REWARD_1, FLAG_POX_LEAGUE_REWARD_2]
trainers: [TRAINER_PLASTIC_OX_VICTORYROAD, TRAINER_PLASTIC_OX_RIDGE_RAIN, TRAINER_PLASTIC_OX_RIDGE_SAND, TRAINER_PLASTIC_OX_RIDGE_STALL, TRAINER_PLASTIC_OX_RIDGE_OFFENSE, TRAINER_PLASTIC_OX_RIDGE_BALANCE]
items: [ITEM_LEFTOVERS, ITEM_MAX_ELIXIR, ITEM_RARE_CANDY]
status: drafted
---

# Victory Road

## Snapshot

An outdoor 39 × 51 ridge, entered from the Ecruteak gatehouse at `(27,48)` and left at `(13..15,1)` for `IndigoPlateau_hns`. Two ways up: the eastern ridge is the direct climb through four Lv.58 trainers, the western terraces are optional and hold the only healer, three pickups and an interaction-only stall specialist. This is the payoff for the west gate that has been shut since Gym 3 — the emotional note is *thin air and no more errands*: nothing here is a puzzle, and the only thing between the player and the League is six people who came up early to train.

## Plot points

1. **The gate finally opens.** Ecruteak's west throat `(8,34)`–`(8,37)` runs `PoxLeague_Checkpoint`, which checks `FLAG_BADGE01_GET` through `FLAG_BADGE08_GET` and warps here to `(27,48)`. No cutscene, no speech: eight badges buy a tile transition. **Reveal-ladder step 16**, and the last map that can carry an explanation — it must carry none.
2. **A greeting and a hazard on the same two tiles.** `(26,43)` is the first trainer, five tiles up from the landing; the south return band `(25..28,49)` sits immediately below the landing tile, so one step south on arrival throws the player back to the gatehouse. Fix the proximity, not the text.
3. **The direct climb is a diagnostic.** Rain `(24,33)` on the eastern path, sand `(26,25)`, offense `(22,13)`, then balance `(13,5)` on the narrow summit. Each intro names the thing it tests. They are the last teaching surface before the League, and they teach matchups, not lore.
4. **The terraces are optional and load-bearing.** The stall specialist `(9,26)` has sight range 0 and must be talked to; `ITEM_LEFTOVERS` sits at `(9,34)`, `ITEM_MAX_ELIXIR` at `(15,28)`, `ITEM_RARE_CANDY` at `(20,11)`; the healing house is at `(9,31)`. A player who takes the direct line reaches the summit with no heal stop.
5. **The summit re-checks the badges.** `(13..15,1)` `PoxLeague_Summit` re-runs all eight checks, then warps to Indigo `(12,18)`. Redundant, harmless, and worth keeping as a belt-and-braces door.
6. **The grass is the last recruitment window.** `gPoxVictoryRoadOutdoor` offers Lv.52–56 Dodrio, Sandslash, Tauros, Donphan, Skarmory, Heracross, Medicham, Breloom, Girafarig, Ditto, and Bagon and Beldum in the 1% slots — a pseudo-legendary line available for the last grind before five fixed rosters.

**Must not:** stage a Rocket, a Silph recap, or a reactivated machine; name Bill or the adaptive system; use "convergence"; require Surf, Cut, Strength, Rock Smash, Waterfall, Flash, or a cave; pretend the ridge is a trial with a judge.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| South return band | `(25,49)`, `(26,49)`, `(27,49)`, `(28,49)` `PoxLeague_Return` | always, `VAR_TEMP_0` | instant warp to `Gate_EcruteakCity_Route38_hns` `(5,5)`, one tile below the landing | move the band two tiles south or add a confirmation; do not bounce a player who just arrived |
| Trail sign | `(28,47)` `PoxLeague_TrailSign` | always | names north/south, the optional terraces, the direct eastern climb | keep verbatim — it is the route's only orienting voice |
| First trainer | `(26,43)` `PoxLeague_VICTORYROAD`, `TRAINER_PLASTIC_OX_VICTORYROAD` | sight 2 | "Six partners, one last test." | keep, and make him the greeter: six of us, nobody works for the League |
| Rain specialist | `(24,33)` `PoxLeague_RIDGE_RAIN` | sight 4, direct path | weather intro, then "You earned that victory!" | keep the intro; give her a post-battle line about the weather turning |
| Sand specialist | `(26,25)` `PoxLeague_RIDGE_SAND` | sight 2 | sand intro, shared defeat and after text | keep the intro; his after-line should be about switches, not encouragement |
| Offense specialist | `(22,13)` `PoxLeague_RIDGE_OFFENSE` | sight 2 | "One free turn is all a sweeper needs." | keep; add a warning about the summit's wind |
| Terraces stall | `(9,26)` `PoxLeague_RIDGE_STALL` | sight 0, interaction-only | patience intro, shared after text | make her the terraces' advocate; she is the only person who explains why the long way exists |
| Summit balance | `(13,5)` `PoxLeague_RIDGE_BALANCE` | sight 2, narrow summit | "Every team has a weakness." | keep, and let him be the one who says the door is a door |
| Healer house | `(9,31)` → `PlasticOx_LeagueRestHouse2` `(4,4)` `PoxLeague_RestKeeper` | always | full party heal plus "Rest a while" | keep; the only heal on the ridge and it is on the optional side |
| Advice house | `(24,11)` → `PlasticOx_LeagueRestHouse1` `(4,4)` `PoxLeague_RestAdvice` | always | hazard and held-item lecture | trim to two sentences; no heal here is a choice, not an oversight |
| Three pickups | `(9,34)`, `(15,28)`, `(20,11)` `PoxLeague_Item0`–`Item2` | `FLAG_POX_LEAGUE_REWARD_0`–`_2` | `finditem` `ITEM_LEFTOVERS`, `ITEM_MAX_ELIXIR`, `ITEM_RARE_CANDY` | keep the flags; re-time the Rare Candy or accept it as a grind reward |

## Dialogue guidance

- **Register:** thin air, wind, dry grass, no trees, a building on the skyline that is not getting closer fast enough. Everyone here is a competitor on their own training camp, not staff — except the two house keepers, who are staff and know it.
- **The six trainers** speak in matchups and conditions: hazard layers, rain turns, the free turn a sweeper needs. They respect the player's badges and never mention the story. Before the League they are the last people who will tell the truth about a team.
- **The house keepers** carry the human register: boots, tea, sleep, a bench. The healer refuses to hurry anyone; the advice keeper is trying to be useful and slightly over-prepared.
- After a trainer is beaten they stay on the ridge, so each needs a **distinct** after-line; today all six print "The LEAGUE is close. Trust the team you raised." and the route loses its six voices in the last thirty seconds of each fight.

> FIRST TRAINER: Six of us up here and not one of us works for the LEAGUE. We got here early, we liked the wind, and we stayed.

> RAIN SPECIALIST: It rains on this side most afternoons. If your team only works in the sun, take the terraces and think about it.

> TERRACE STALL: You came up the quiet side. Good. Nobody has ever learned anything from a straight line.

> HUT KEEPER: Boots off. There's a bench, there's tea, and there's no hurry — the mountain isn't going anywhere and neither is the LEAGUE.

> SUMMIT TRAINER: Last one. Past me it's a door, a lobby, and five people better than me. Try to arrive with something left.

- **Do not:** name Bill, Silph, the adaptive system, or the convergence; explain the merged geography; tell the player they were chosen; promise a twist at Indigo; make any terrace mandatory.

## Inspiration

- **The Pennine Way and Cape Wrath Trail.** Flagstone slabs over bog, cairns, wind with nothing to stop it, a bothy every few hours. Converts to the trail sign, the optional terraces, and the two rest houses as bothies rather than shops.
- **Japanese mountain huts (*yamagoya*).** A keeper, tea, blankets, a kerosene lamp, a reservations board, and a rule about boots. That is the healing house verbatim, and it is why the keeper talks about rest instead of Pokémon.
- **The Bob Graham Round and fell-race support crews.** Pacers who join for one leg, test you, and drop out; a schedule on a wet piece of paper. Converts to six trainers who each test one weakness and then stand in the wind.
- **An Alpine col road — Stelvio, Galibier.** Switchbacks, a stone marker at the pass, cyclists, weather arriving from the wrong side. Explains the direct climb versus the terraces and gives the sign its phrasing.
- **A föhn wind and a cloud inversion.** The ridge above a sea of cloud, Indigo's roof breaking through. This is how the League becomes visible without a cutscene or an NPC pointing at it.
- **GSC Route 26's two houses and its guard.** Feeling only, already ported: two doors on a ridge, one of them warm.

## Implementation hooks

- Wiki page: `plasticox-victoryroad.html`; maps `PlasticOx_VictoryRoad` (`MAP_PLASTIC_OX_VICTORY_ROAD`), `PlasticOx_LeagueRestHouse1` (`MAP_PLASTIC_OX_LEAGUE_REST_HOUSE1`), `PlasticOx_LeagueRestHouse2` (`MAP_PLASTIC_OX_LEAGUE_REST_HOUSE2`).
- Scripts: `data/scripts/plastic_ox_league.inc` (`PoxLeague_Checkpoint`, `PoxLeague_Return`, `PoxLeague_Summit`, `PoxLeague_VICTORYROAD`, `PoxLeague_RIDGE_*`, `PoxLeague_Item0`–`Item2`, `PoxLeague_TrailSign`, `PoxLeague_RestAdvice`, `PoxLeague_RestKeeper`); `data/scripts/plastic_ox_region.inc` (`PoxRegion_ecruteak_league_a`, dead `_Open` arm).
- Data: `gPoxVictoryRoadOutdoor` in `src/data/wild_encounters.json`; layout `LAYOUT_PLASTIC_OX_VICTORY_ROAD`, 39 × 51, `gTileset_Johto_General_Hns`.
- Known gaps: the return band sits directly under the landing tile; all six trainers share `PoxLeague_Text_RouteDefeat` and `PoxLeague_Text_RouteAfter`; the only heal is on the optional west path while the advice house is on the direct climb; `PoxLeague_Summit` re-checks eight badges already checked at the gate; the legacy cave maps `VictoryRoad_1F`, `VictoryRoad_B1F`, `VictoryRoad_B2F` and the FRLG versions still exist and the dead `PoxRegion_ecruteak_league_a_Open` arm still warps to `MAP_VICTORY_ROAD_1F`; both rest houses reuse `LAYOUT_HOUSE_GENERIC_A_HNS` and the generic house music.

## Open questions

- Should stepping onto the return band be instant and silent, or should the sign's "south: ECRUTEAK checkpoint" tile ask first? Today a new arrival can be ejected in one step.
- Is one heal on the optional side deliberate scarcity, or should the advice house also heal now that the level cap is gone?
- Do the six trainers get six distinct after-lines, or is the repeated "the LEAGUE is close" a deliberate chorus? If the latter, say so in the note and leave it alone.
- Retire the legacy Victory Road caves and the dangling `_Open` arm, or keep them for postgame? Nothing currently reaches them.
- Is `ITEM_RARE_CANDY` at `(20,11)` the intended terrace reward now that six Lv.58 fights sit between the player and the League?
