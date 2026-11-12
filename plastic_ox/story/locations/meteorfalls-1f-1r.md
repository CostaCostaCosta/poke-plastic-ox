---
title: Meteor Falls 1F 1R
slug: meteorfalls-1f-1r
kind: Cave
act: 5
stage: "13 — Meteor Falls"
depth: full
wiki: meteorfalls-1f-1r
maps: [MeteorFalls_1F_1R]
also_maps: [MeteorFalls_1F_2R, MeteorFalls_B1F_1R]
flags: [FLAG_POX_STORY_SPACE_CENTER, FLAG_MET_PROF_COZMO, FLAG_DEFEATED_METEOR_FALLS_STEVEN]
trainers: [TRAINER_NICOLAS_1, TRAINER_JOHN_AND_JAY_1, TRAINER_STEVEN]
items: [ITEM_NUGGET, ITEM_MOON_STONE, ITEM_FULL_HEAL, ITEM_PP_UP]
status: drafted
---

# Meteor Falls 1F 1R

## Snapshot

The wet first hall of the final mountain, entered from Route 115 at `(6,39)`: a meteor-strewn floor, an underground river, four item balls, a scientist who has stopped talking to people, and a north passage to Blackthorn. The player crosses it once, in Act V, on the way to the eighth Badge; `MeteorFalls_1F_2R` holds the only two trainer fights in the cave and `MeteorFalls_B1F_1R` is empty. The emotional note is **scale**: water, rock, and cold that do not care whether the player is ready.

## Plot points

1. **A threshold, not a lesson.** Enter at `(6,39)`; 1F 1R is a junction with `(10,3)` to 1F 2R, `(5,4)` and `(26,28)` to B1F 1R, and `(4,2)` to `MeteorFalls_StevensCave`. Nothing here explains the mountain, and nothing should.
2. **The north passage is the stage gate.** Coord `(26,18)` runs `PoxRegion_meteor_blackthorn_a`, gated on `FLAG_POX_STORY_SPACE_CENTER`; the sign at `(25,17)` is the generator's "BlackthornCity / Marked passage ahead.", and the closed branch warps back to `(25,18)` with generic text. This is the real Act V handoff, redundant with Saffron but visible.
3. **Cozmo is a legacy scene.** `MeteorFalls_1F_1R_EventScript_ProfCozmo` at `(13,23)` is still Emerald's Magma/Meteorite/Aqua exposition, and `FLAG_MET_PROF_COZMO` is defined as `0` in `flags_frlg.h`, so his second branch can never fire. In v7 there is no Magma and no meteorite plot: rewrite him as a field geologist who has been here too long, or retire him.
4. **The standoff is already dead.** Magma grunts `(12,20)`/`(14,21)`, Archie `(6,20)`, Aqua grunts `(6,20)`/`(6,21)` all have script `0x0`; Archie and one Aqua grunt share `(6,20)`. Nothing triggers, and the sprites are the only thing left of the cutscene. Delete them.
5. **Nothing new is revealed here.** Reveal-ladder step 15 is Blackthorn's Gym; Act V must not assume Silph is resolved and must not open a new mystery. The falls are a place, never an explanation.
6. **1F 2R is the cave's human room.** Nicolas `(13,2)` and the married pair John & Jay at `(6,12)`/`(7,12)` — a fifty-year double battle — are vanilla text but the right note for a cold dungeon. Keep the marriage; rewrite the lines so they are not merely cute.
7. **Must not:** stage Magma, Aqua, or Rocket; mention the Meteorite, Mt. Chimney, or Sootopolis; connect the falls to the Space Center; hand out a legendary; let a sign or NPC explain the convergence.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Cozmo | 1F `(13,23)` `MeteorFalls_1F_1R_EventScript_ProfCozmo` | `FLAG_MET_PROF_COZMO` is `0` | vanilla Magma/Meteorite/Aqua speech; second branch unreachable | rewrite as one exchange about water and stone, no villains; or retire the object |
| Dead standoff | 1F `(12,20)`, `(14,21)`, `(6,20)`, `(6,21)` | script `0x0` | five silent objects; Archie and an Aqua grunt overlap at `(6,20)` | delete all five |
| North passage | 1F `(26,18)` `PoxRegion_meteor_blackthorn_a` | `FLAG_POX_STORY_SPACE_CENTER` unset | generic closed text, warp to `(25,18)` | keep; the closed line should name the pass, not "your next objective" |
| Passage sign | 1F `(25,17)` `PoxRegion_meteor_blackthorn_a_Sign` | always | "BlackthornCity / Marked passage ahead." | rewrite: distance, the last water, the cold |
| Item balls | 1F `(2,4)`, `(2,14)`, `(27,5)`, `(26,32)` | item flags | `ITEM_NUGGET` under the TM Iron Tail flag; Moon Stone, Full Heal, PP Up | fix the TM mismatch; set the Moon Stone in the rockfall, not on a path |
| Steven's Cave | 1F `(4,2)` → `MeteorFalls_StevensCave` | none | optional Lv 75–77 `TRAINER_STEVEN` fight, Emerald's "Sootopolis Space Center" text | gate to postgame or retire; it must not sit on the Act V path |
| Self-warp | 1F `(27,18)` | always | warps to its own tile | delete |
| 1F 2R trainers | `(13,2)` Nicolas; `(6,12)`, `(7,12)` John & Jay | always | vanilla RS text, mons Lv 37–39 | rewrite; keep the double battle and the marriage; rescale |
| B1F 1R | whole map | none | 0 NPCs, 0 items, 6 warps | keep as traversal, or retire; no beat belongs here |

## Dialogue guidance

- **Who speaks:** Cozmo, the married couple, Nicolas. There are no residents, no shop, and no one to explain the cave; the silence is the point.
- **Register:** voices drop. Short lines with pauses in them, and water underneath. People repeat themselves because the cave repeats them. No line that needs a laugh.
- **Cozmo** may know rock, water, the shape of the falls, and that he has been here too long. He may not know Magma, the Meteorite, the Space Center, or anything about the world's arrangement.
- **John & Jay** are competitive affection: they finish each other's sentences only when arguing about a battle, and their double battle is the dungeon's one warm room.
- **Nicolas** came to the mountain to become strong and found it mostly cold; his line is the note's one piece of vanity, deflated. No flag shift anywhere in the cave: the only states are before and after the eighth Badge, and the dialogue must not care which.

> COZMO: The water's been at this longer than the mountain. I keep meaning to leave, and then it rains.

> JAY: Fifty years. He still counts my switches like he's keeping score of something else.

> JOHN: She leads with the same Pokémon she had when we met. I've never once been ready for it.

> NICOLAS: Everyone said the mountain would make me stronger. It mostly made me cold. I stayed anyway.

- **Do not:** mention Magma, Aqua, Rocket, or the Meteorite; name Sootopolis, the Space Center, or Bill; turn the cave into a lore dump; make Cozmo a guide; make the couple a joke.

## Inspiration

- **Postojna and Luray caverns:** a river running through a hall, a temperature that is a fact rather than a mood, lighting that only shows the next ten metres. Convert to sound design and pacing, not set dressing.
- **Meteor Crater, Arizona:** a hole with a visitor centre and a rock that travelled; the scale is the story. Convert to one open chamber and the meteorite fragments, and resist giving them a plot.
- **Mountain-hut culture:** a kettle, a visitor book, a thermos, someone who reads the weather by ear. Convert to Cozmo's camp and the couple's picnic — the only domestic objects in the cave.
- **Hoenn's Meteor Falls in RSE:** the waterfall, the deep Bagon room, the sense that the cave continues past the route's needs. Keep the depth; drop dragons-as-destiny.
- **Ice Path's function in GSC:** the last dungeon before the eighth Badge. Steal its pacing — one-way drops, a slow middle, a short exit — and none of its ice.

## Implementation hooks

- Wiki page: `meteorfalls-1f-1r.html`
- Maps: `MeteorFalls_1F_1R` (`MAP_METEOR_FALLS_1F_1R`), `MeteorFalls_1F_2R` (`MAP_METEOR_FALLS_1F_2R`), `MeteorFalls_B1F_1R` (`MAP_METEOR_FALLS_B1F_1R`); 1F `(4,2)` also warps to `MeteorFalls_StevensCave` (`MAP_METEOR_FALLS_STEVENS_CAVE`), which no note claims
- Scripts: `data/maps/MeteorFalls_1F_1R/scripts.inc`, `data/maps/MeteorFalls_1F_2R/scripts.inc`, `data/scripts/plastic_ox_region.inc`
- Flags: `FLAG_POX_STORY_SPACE_CENTER`; `FLAG_MET_PROF_COZMO`, `FLAG_DEFEATED_METEOR_FALLS_STEVEN` (both `0` in `flags_frlg.h`, so their branches are dead)
- Trainers / items: `TRAINER_NICOLAS_1`, `TRAINER_JOHN_AND_JAY_1`, `TRAINER_STEVEN` (Lv 75–77, four Full Restores); `ITEM_NUGGET`, `ITEM_MOON_STONE`, `ITEM_FULL_HEAL`, `ITEM_PP_UP`
- Known gaps: five dead villain objects with an overlapping pair at `(6,20)`; Cozmo's Emerald script with a zeroed flag; two item balls whose flags and contents disagree (Nugget under TM Iron Tail); self-warp `(27,18)`; `MeteorFalls_B1F_1R` empty with six warps; wild encounters Lv 14–18 and a surfing table of Zubat/Solrock rather than fish; 1F 2R trainers Lv 37–39; the unclaimed Steven side cave.

## Open questions

- Rewrite Cozmo or remove him? Recommend rewrite — he is the only speaking NPC on 1F, and the cave needs one human voice.
- Delete the Magma/Aqua cluster outright, or re-skin the sprites as researchers? Recommend delete; two objects on one tile is not a scene.
- Is `MeteorFalls_StevensCave` intended for Act V? Recommend a postgame gate: a Lv 77 team with four Full Restores and a zeroed defeat flag reads as unfinished Emerald content.
- Rescale encounters (Lv 14–18) and 1F 2R trainers (Lv 37–39) into the OU band, or keep the cave easy and let Blackthorn carry the difficulty?
- Should `MeteorFalls_B1F_1R` stay empty as pure traversal, or earn one item or trainer to justify its six warps?
