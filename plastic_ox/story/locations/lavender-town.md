---
title: Lavender Town
slug: lavender-town
kind: Town
act: 3
stage: "9 — Lavender / Team Rocket II"
depth: full
wiki: lavendertown-hns
maps: [LavenderTown_hns]
also_maps: [PokemonTower_1F_Frlg, PokemonTower_2F_Frlg, PokemonTower_3F_Frlg, PokemonTower_4F_Frlg, PokemonTower_5F_Frlg, PokemonTower_6F_Frlg, PokemonTower_7F_Frlg, LavenderTown_VolunteerPokemonHouse_Frlg, LavenderTown_House1_Frlg, PlasticOx_Harbor, PlasticOx_PokemonTower, PlasticOx_FujiHouse]
flags: [FLAG_POX_STORY_FUJI, FLAG_POX_GIFT_FUJI, FLAG_POX_FUJI_RESCUED, FLAG_POX_HIDE_HOUSE_FUJI, FLAG_POX_HIDE_LAVENDER_GRUNT_1, FLAG_POX_HIDE_LAVENDER_GRUNT_2, FLAG_POX_HIDE_LAVENDER_GRUNT_3]
badges: []
trainers: [TRAINER_PLASTIC_OX_TOWERGRUNT1, TRAINER_PLASTIC_OX_TOWERGRUNT2, TRAINER_PLASTIC_OX_TOWERGRUNT3]
status: implemented
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

Implemented 2026-11-24 (`plastic_ox/alpha/lavender.py`; run log
`plastic_ox/story/runs/2026-11-24-lavender-town.md`). Nothing in Lavender
teleports the player except FUJI walking them home after the rescue (the FRLG
original beat).

| Interaction | Where | Trigger / state | Behavior |
| --- | --- | --- | --- |
| Tower caretaker | town `(17,7)` | before / after `FLAG_POX_FUJI_RESCUED` | candles; men in black went up / FUJI is home |
| FUJI's neighbour | town `(12,10)` | before / after rescue | worried / relieved |
| Mourner | town `(8,21)` | always | visits a NIDORINO buried thirty years ago |
| Cinnabar road | town `(15,17)` `Pox_CinnabarRoad` | always | Route 8 / Underground / Route 103 directions |
| South road barrier | town `(13..15,24)` | always | ferry clerk, fisherman, kid; three different lines |
| Doors | town `(22,6)` tower, `(8,13)` FUJI's house, `(10,19)` House1, `(22,19)` Soul House | always | real warps to the interiors and back |
| Soul House | `PlasticOx_FujiHouse` (HNS generic house) | before / after `FLAG_POX_FUJI_RESCUED` | keeper (names, somewhere to sit / FUJI swept the step) and a visitor |
| Tower floors | `PokemonTower_1F..6F_Frlg` | always | mourners and channelers who speak in fragments (no channeler battles); 5F purified zone heals; item balls on their own POX_EXT flags |
| Rocket II | `PokemonTower_7F_Frlg` `(9,10)`, `(13,8)`, `(9,6)` | in order, badge 4 | `TOWERGRUNT1..3` (Team Rocket); each disappears when beaten |
| FUJI rescue | 7F `(11,4)` | after grunt 3 | relief, then walks the player to his house; sets `FLAG_POX_FUJI_RESCUED` |
| SURF KEY | FUJI's house `(3,3)` | rescued | two beats (what they asked, where the records are), SURF KEY, sets `FLAG_POX_STORY_FUJI` (opens Route 8), then the EEVEE foster |
| Signs | town `(16,4)`, `(19,7)`, `(12,13)`, `(19,18)` | always | town, tower, volunteer house, Soul House |

The SILPH SCOPE comes from VALE at the Weather Institute (`Pox_WI_Vale_Scope`), before Fortree, so every player reaches the tower with it; without it the engine turns tower wild battles into unidentifiable GHOST encounters.

Wild encounters: tower 3F–7F use `gPoxUUPokemonTower3F..7F` (Lv34–40,
Gastly, Haunter, Cubone, Shuppet, Duskull, Banette and the UU Misdreavus, rarer
low down and about 16% on 7F). `pox_progression.py` counts them at the
`cinnabar` (UU) checkpoint.

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
- Generator: `plastic_ox/alpha/lavender.py` (installed last by `region_v7.py`);
  grunts 1–2 and FUJI's EEVEE remain `build_story.py` battles/gift.
- Scripts: `data/scripts/plastic_ox_lavender.inc` (generated),
  `Pox_TowerGrunt1/2` and `Pox_Fuji` in `data/scripts/plastic_ox_story.inc`
- Retired: `PlasticOx_PokemonTower` is an empty placeholder map kept for map
  numbering; remove it with the other placeholder slots before release.
  `PlasticOx_FujiHouse` (the old FUJI teleport room) is now the Soul House.
- Test: `plastic_ox/demo/test_lavender.py`

## Open questions

- From outside, the tower is still the HNS radio-station building. Swapping
  its metatiles for a tower facade would need HNS tileset art.
- Is `PlasticOx_Harbor` the postgame dock map, or should the harbour be an
  interior added later? The note assumes the former.
