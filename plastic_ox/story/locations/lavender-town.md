---
title: Lavender Town
slug: lavender-town
kind: Town
act: 3
stage: "9 — Lavender / Team Rocket II"
depth: full
wiki: lavendertown-hns
maps: [LavenderTown_hns]
also_maps: [PlasticOx_PokemonTower, PlasticOx_FujiHouse, PlasticOx_Harbor]
flags: [FLAG_POX_STORY_FUJI, FLAG_POX_GIFT_FUJI, FLAG_POX_HIDE_LAVENDER_GRUNT_1, FLAG_POX_HIDE_LAVENDER_GRUNT_2]
badges: []
trainers: [TRAINER_PLASTIC_OX_TOWERGRUNT1, TRAINER_PLASTIC_OX_TOWERGRUNT2]
status: drafted
---

# Lavender Town

## Snapshot

A hillside town of tiled roofs and narrow stairways, quieter than its size
suggests. The Pokémon Tower stands above it with its door open and its
candles lit; two Rocket grunts are inside, asking the wrong questions of the
wrong man. The player rescues Mr. Fuji, is pointed at Cinnabar, and leaves
through Route 8 while the southern harbour road stays shut behind them.

Lavender is the game's pivot from *travelling through strangeness* to
*investigating it*: Rocket is no longer stealing things, it is asking the same
questions the player has been asking since Ecruteak.

## Plot points

1. **Arrival is quiet.** Fortree → Route 110 → Lavender. No cutscene at the
   town gate. The player should notice the tower before anyone explains it.
2. **Team Rocket II — Pokémon Tower.** Two grunts occupy the tower and are
   interrogating Fuji about teleportation, preservation of living states, and
   old Cinnabar research. This is the second of exactly three Rocket
   encounters. They are frightened of what they found, not triumphant.
3. **Fuji is rescued and points to Cinnabar.** He recognises the *kind* of
   research he is being asked about but not the cause. He names the Cinnabar
   archives and, crucially, the practical route: Route 8 → Underground Path →
   Route 7 → Route 103. The directions are geography, not lore.
4. **Reveal-ladder step 7.** Rocket is investigating the phenomenon. Fuji
   confirms the investigation has a paper trail. Do **not** reveal the system,
   Bill, or Silph here.
5. **Saffron stays sealed.** Lavender's west road is the way around the closed
   city, never through it.
6. **South is postgame.** The harbour road is visibly closed, with people
   standing at the barrier. After the Champion battle it opens to the Battle
   Frontier ferry. Do not spend the south exit on the Cinnabar transition.
7. **The tower is a place of grief, not a dungeon.** NPCs lower their voices.
   The player is a visitor here before they are a hero.

**Must not:** have Fuji name the cause; have Rocket monologue about a master
plan; open the harbour early; show Bill anywhere near this.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Tower lead | town `(17,7)` `Pox_TowerGuide` | Fuji not rescued | "TEAM ROCKET is holding MR. FUJI" | keep the information; give it to a mourner or a tower caretaker, not a quest-giver kid |
| Fuji guide | town `(12,10)` `Pox_FujiGuide` | Fuji rescued | "The POKéMON HOUSE welcomes everyone" | rewrite: she is Fuji's neighbour and has been worried |
| Cinnabar road | town `(15,17)` `Pox_CinnabarRoad` | after Fuji | Route 8 / Underground / Route 103 directions | keep; phrase as directions a local would actually give |
| South road barrier | town `(13,24)`–`(15,24)`, three identical `MAN_3` | always | "The southern road is closed." | three different people at the barrier: a ferry clerk, a fisherman, a kid. No two identical lines |
| Tower grunts | `PlasticOx_PokemonTower` `(6,12)`, `(7,9)` | grunt flags unset | trainers `TOWERGRUNT1/2`, hide flags after defeat | keep; add post-battle lines that are *questions*, not threats |
| Fuji rescue | Tower `(5,2)` | `FLAG_POX_STORY_FUJI` | long rescue text naming Cinnabar and Blaine | keep content; break into two beats (relief, then directions) |
| Fuji's house / Eevee | `PlasticOx_FujiHouse` `(5,2)` | `FLAG_POX_GIFT_FUJI` | gives Eevee #4 | keep; make the gift feel like a foster, not a prize |
| Tower exit | Tower `(3,12)` | always | "I'll show you back outside" | keep as a silent walk-out if possible |
| Signs | town `(15,1)`, `(1,17)`, `(18,21)` | always | "Marked passage ahead." ×3 | replace with place-specific signs: tower, Route 8, harbour |

## Dialogue guidance

- **Lavender's public voice is hushed.** Short sentences, no exclamation marks.
  People describe the tower the way you describe a church: by its hours, its
  candles, who is buried there.
- **Mr. Fuji** is gentle, tired, and precise. He does not explain more than he
  knows, and he is ashamed that his old field is being mined. He calls the
  grunts "those men", never "Rocket".
- **Rocket grunts** are rattled. They expected a haunted tower and found a
  filing cabinet. Their lines should be questions with no good answers:
  "How do you move a person without moving the room?"
- **Mourners and caretakers** carry the town's emotional weight. One person
  should be there for a Pokémon that died long ago; one should be there out of
  habit.
- **Harbour people** are bored and practical. The barrier is a schedule
  problem, not a mystery.
- After Fuji is rescued, the town's register changes: people are relieved but
  not celebratory.

> TOWER CARETAKER: We keep the candles low. The Pokémon here don't like a
> bright room.

> GRUNT: You think we wanted this? We were told to find a man, not a library.

> FUJI: I spent a life learning how to keep things. I never learned how to put
> them back.

> HARBOUR CLERK: Ferry's not running. Hasn't been since the roads moved.
> Come back when you're famous.

- **Do not:** use "convergence", "adaptive system", "Silph" or "Bill" here.
  Do not make the tower a jump-scare level; the horror is bureaucratic.

## Inspiration

- **Lavender as a real Japanese temple town:** stone stairs, grave plots on a
  hillside, a shop that sells incense and soda from the same cooler. Sound:
  wind chimes, a distant bell, a scooter idling.
- **Pokémon Tower in RBY/FRLG:** the silence before the first wild encounter,
  the Channelers who speak in fragments, the feeling of intruding.
- **Ghost-story pacing:** the tower should be read, not explained — a knocked
  chair, a candle that leans, a radio playing in an empty room.
- **Dialogue conversion:** give the town three social roles — caretaker,
  mourner, harbour worker — and let each talk about the tower from a different
  distance. That is the whole town in three voices.

## Implementation hooks

- Wiki page: `lavendertown-hns.html`
- Maps: `LavenderTown_hns` (`MAP_LAVENDER_TOWN_HNS`), `PlasticOx_PokemonTower`
  (`MAP_PLASTIC_OX_POKEMON_TOWER`), `PlasticOx_FujiHouse`, `PlasticOx_Harbor`
- Scripts: `data/maps/LavenderTown_hns/scripts.inc`,
  `data/maps/PlasticOx_PokemonTower/scripts.inc`,
  `data/scripts/plastic_ox_story.inc`
- Flags: `FLAG_POX_STORY_FUJI`, `FLAG_POX_GIFT_FUJI`,
  `FLAG_POX_HIDE_LAVENDER_GRUNT_1`, `FLAG_POX_HIDE_LAVENDER_GRUNT_2`
- Trainers: `TRAINER_PLASTIC_OX_TOWERGRUNT1` (Lv.36–38 mixed, Ghost/Poison),
  `TRAINER_PLASTIC_OX_TOWERGRUNT2` (Lv.37–38 mixed, physical)
- Known gaps: `PlasticOx_PokemonTower` has **0 warp events**, so the tower is
  entered by a scripted transport — verify both entry and exit; three identical
  `SouthRoadClosed` men; all three signs say "Marked passage ahead."

## Open questions

- Should the tower keep native wild encounters (Gastly/Cubone) or be encounter-
  free for pacing? The current map data suggests no encounters are assigned.
- Is `PlasticOx_Harbor` the postgame dock map, or should the harbour be an
  interior added later? The note assumes the former.
