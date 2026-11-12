---
title: Blackthorn City
slug: blackthorncity-hns
kind: City
act: 5
stage: "14 — Blackthorn and Clair"
depth: full
wiki: blackthorncity-hns
maps: [BlackthornCity_hns]
also_maps: [PlasticOx_ClairGym]
flags: [FLAG_POX_STORY_SPACE_CENTER, FLAG_BADGE08_GET]
badges: [8]
trainers: [TRAINER_PLASTIC_OX_CLAIR]
status: drafted
---

# Blackthorn City

## Snapshot

A 59 × 60 valley city that is the last stop on the northern road: arrived through `MeteorFalls_1F_1R` at `(30,26)`, left downhill through `Route45_hns` at `(25,59)`. Gym 8 is here, and it is the only appointment in town — Clair, six OU Pokémon at Lv.58–59, and then nothing: no villain, no machine, no reveal. The emotional note is *closing time at altitude*: a working mountain town that will finish its day whether or not the player wins.

## Plot points

1. **Arrival is a portal, not a road.** `(30,26)` runs `PoxRegion_meteor_blackthorn_b` into `MAP_BLACKTHORN_CITY_HNS` from Meteor Falls; the closed arm pushes the player to `(29,26)` rather than trapping them on the trigger. There is no cutscene and no gate dialogue — the city simply starts.
2. **The Gym door is a person.** A young trainer at `(16,28)` runs `Pox_ClairGuide`, which requires `FLAG_POX_STORY_SPACE_CENTER` and otherwise falls through to `Pox_NotReady` — "There is still something to do before you can continue. Ask the local guide." He *is* the local guide. Rewrite that refusal as a doorman with a schedule, and the joke lands as bureaucracy instead of a broken predicate.
3. **Badge 8: Clair.** `PlasticOx_ClairGym` `(5,2)` `Pox_Clair` fights `TRAINER_PLASTIC_OX_CLAIR` (Gyarados, Jolteon, Swampert, Tyranitar, Medicham, Flygon; Leftovers across the team, Lum Berry on Tyranitar), then sets `FLAG_BADGE08_GET` and prints the shared gym line `Pox_Text_Badge`. **Reveal-ladder step 15.** Nothing is explained here on purpose.
4. **Badge 8 does not finish the gate.** The League gate at Ecruteak west checks all eight badge flags, and Clair's may be earned before badge 7. If the player wins here holding seven, the doorman's revisit line (`Pox_Done`: "You've taken care of things here. Good luck on the next road!") is actively wrong — the town must send them back to Saffron's Fighting Dojo, not onward.
5. **The one line that must change state.** `Pox_LeagueRoad` at `(25,27)` tells every visitor "The LEAGUE gate is west of ECRUTEAK. Bring all eight BADGES." — including the player who just collected the eighth. Branch it on `FLAG_BADGE08_GET` (and on the seventh badge flag) so the town acknowledges the ending it is standing next to.
6. **The downhill exit.** `(25,59)` `PoxRegion_blackthorn_route45_a` warps to `Route45_hns` `(25,1)` behind the same Space Center check. This is the fast return into the early world and the only exit that is not Meteor Falls.

**Must not:** stage a Rocket appearance, a reactivated machine, or a post-Silph recap; require Bruno before Clair or assume Silph is finished; name Bill or the adaptive system; say "convergence"; tell the player the League gate is Clair's reward rather than the eighth badge's.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Gym doorman | town `(16,28)` `Pox_ClairGuide` | needs `FLAG_POX_STORY_SPACE_CENTER` | "CLAIR's challenge is this way." then warps to `MAP_PLASTIC_OX_CLAIR_GYM` `(5,17)`; otherwise the generic `Pox_NotReady` | keep the warp, replace the refusal: the door opens when the northern road does, and he says so in hours |
| League-road boy | town `(25,27)` `Pox_LeagueRoad` | always | one static line about Ecruteak and eight badges | three states: under eight, seven-with-Clair-beaten, eight |
| Four bodies, two strings | town `(27,39)`, `(44,31)`, `(12,40)`, `(33,44)` `BlackthornCity_EventScript_Npc3`–`Npc6` | always | "Dragon training takes patience…" and "The mountain air makes every morning sharp…" alternating | four people: feed merchant, guesthouse laundress, a tamer, a baker's black belt |
| Meteor Falls sign | town `(29,27)` `PoxRegion_meteor_blackthorn_b_Sign` | always | player-facing text is the map directory name, "MeteorFalls_1F_1R / Marked passage ahead." | "METEOR FALLS — north road. Closed in bad weather." |
| Meteor Falls portal | town `(30,26)` `PoxRegion_meteor_blackthorn_b` | `FLAG_POX_STORY_SPACE_CENTER` | warps to `MAP_METEOR_FALLS_1F_1R` `(25,18)`, or bumps east | keep; add nothing to it |
| Route 45 portal | town `(25,59)` `PoxRegion_blackthorn_route45_a` | `FLAG_POX_STORY_SPACE_CENTER` | warps to `Route45_hns` `(25,1)` | keep; the tile should read as a road, not a trapdoor |
| Clair | `PlasticOx_ClairGym` `(5,2)` `Pox_Clair` | `FLAG_POX_STORY_SPACE_CENTER`, then `FLAG_BADGE08_GET` | "Show me what you and your POKéMON have learned!" then `trainerbattle_single`; on win the generic badge box | give her a pre-battle line about the team she is testing, and a badge-8 specific post line |
| Gym exit | `PlasticOx_ClairGym` `(4,17)` `Pox_ClairGymExit` | always | "I'll show you back outside." warps to town `(16,29)` | keep — the only way out of a map with zero warps |
| City services | town `(27,48)` → `MAP_POKEMON_CENTER_JOHTO_HNS`; `(16,48)` → `MAP_MART_JOHTO_HNS` | always | the shared Johto Center and Mart interiors | keep; give the clerk one Blackthorn-specific complaint |

## Dialogue guidance

- **The town speaks in closing times.** The last delivery, the last bus, the feed order, the laundry. Weather is the mountain's, and it decides the road. Nobody is excited that the player arrived.
- **Clair** is young, fast, and professionally bored of being the last appointment of everyone's journey. Short sentences, no mysticism, no comfort. She tests a team, not a chosen one, and her one useful line after the badge is logistics: seven stamps is not eight.
- **The doorman** owns a queue and an hour; treat him as staff, not a gatekeeper. **The tamer** talks husbandry — weight, feed, handling — the way a falconer does. **The League-road boy** counts, and counting is his whole personality.
- After `FLAG_BADGE08_GET` the town should relax by one degree: the doorman is off duty, the tamer is less careful with his opinion, and the road boy has stopped counting.

> DOORMAN: She takes one challenger an hour and she doesn't take walk-ins. You're early. Sit, or pace — most people pace.

> CLAIR: I don't care how you got up here. I care whether your sixth Pokémon is still standing when my sixth is.

> TAMER: Dragons don't want fire and they don't want glory. Same feed, same hour, same hands. The rest is reputation.

> LEAGUE BOY: Eight stamps and the gate opens. Seven and you've got a long walk back to a GYM that isn't mine.

> LAUNDRESS: Two loads a day and every one of them smells of cave water. That's METEOR FALLS for you. Sells well, that smell, to people who've never been.

- **Do not:** explain the merge, use "convergence", imply a dragon chose the player, let Clair mention Silph or Bill, or write a Gym guide who recites the badge rule as if it were a mystery.

## Inspiration

- **Kōyasan: the temple town at the end of the cable car.** Guesthouses, one last funicular, everything shutting at five while pilgrims arrive late. Converts directly to the doorman's appointment book, the laundress, and a town whose economy is arrivals.
- **Blaenau Ffestiniog or any slate valley town.** One road in, terraced houses, chapel, weather coming off the mountain, a bus that leaves once. Gives the Mart clerk and the feed merchant their stock and their grudge about the road.
- **A raptor mews at feeding time.** Scales, hoods, jesses, a weight log on a nail. This is how the tamer talks about dragons, and why "patience" is a technical term for him.
- **A sumo stable's morning practice.** Small door, no knocking, silence, the stablemaster decides who enters. Converts to the Gym's door policy and to Clair's refusal to perform for a visitor.
- **GSC's Dragon's Den feeling, kept offscreen.** Deep still water and an elder's test exist as a thing people mention once — never as a map, never as a scene. The battle is the whole rite here.

## Implementation hooks

- Wiki page: `blackthorncity-hns.html`; maps `BlackthornCity_hns` (`MAP_BLACKTHORN_CITY_HNS`) and `PlasticOx_ClairGym` (`MAP_PLASTIC_OX_CLAIR_GYM`).
- Scripts: `data/maps/BlackthornCity_hns/scripts.inc` (`BlackthornCity_EventScript_Npc1`–`Npc6`); `data/scripts/plastic_ox_story.inc` (`Pox_Clair`, `Pox_ClairGuide`, `Pox_ClairGymExit`, `Pox_LeagueRoad`, `Pox_NotReady`, `Pox_Done`, `Pox_Text_Badge`); `data/scripts/plastic_ox_region.inc` (`PoxRegion_meteor_blackthorn_b`, `PoxRegion_blackthorn_route45_a`, empty `PoxRegion_Arrival_BlackthornCity_hns`).
- Gates: `Pox_ClairGuide` requires `FLAG_POX_STORY_SPACE_CENTER`; the badge is `FLAG_BADGE08_GET`; the League checkpoint is elsewhere and checks all eight.
- Known gaps: a 59 × 60 city with **two** warps — every other building entrance, the Gym's included, is not a warp event, and the Gym is entered only by talking to `(16,28)`. Six NPC objects share two strings, while `BlackthornCity_EventScript_Npc1` and `Npc2` exist with no object placed. Two player-facing signs and portals are labelled with raw map directory names (`Route45_hns` still shows "BlackthornCity / Marked passage ahead." at `(25,2)`). The Gym interior is `LAYOUT_RUSTBORO_CITY_GYM`, 11 × 20, with zero warps, zero Gym trainers, and an exit you must talk to. `Pox_Text_Badge` is one shared string for all eight Gyms. The map plays `MUS_RG_ROUTE11`, a Kanto route theme, rather than a Johto city theme.

## Open questions

- Should the Gym become a real warp on the building's door with the doorman as flavour, or stay an NPC teleport? Today the most important building in the city has no door, and the exit NPC is the only way out of the Gym.
- Is `FLAG_POX_STORY_SPACE_CENTER` the intended predicate for this door, or a copy-paste from the Saffron gates? The whole northern region already requires it at Meteor Falls, so the extra refusal may be redundant.
- Does Clair staff her Gym with anyone? The Rustboro layout holds one leader and one exit; a bare duel is a defensible statement for Gym 8, but then the layout should look like a dragon hall, not a rock maze.
- When badge 7 is still missing, who explains the gap — the doorman, the road boy, or the Ecruteak checkpoint on the return? Pick one and keep the other two silent.
- Repoint the city music, or is the Kanto route theme a placeholder that ships?
