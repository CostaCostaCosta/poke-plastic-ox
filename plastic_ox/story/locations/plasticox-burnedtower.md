---
title: Burned Tower
slug: plasticox-burnedtower
kind: Cave
act: 2
stage: "4 — Ecruteak and the Burned Tower"
depth: full
wiki: plasticox-burnedtower
maps: [PlasticOx_BurnedTower]
flags: [FLAG_POX_STORY_BURNED_TOWER]
items: [ITEM_FIRE_STONE, ITEM_ETHER]
status: drafted
---

# Burned Tower

## Snapshot

The ground floor of the tower is a roped-off ruin: a black timber frame holding up nothing, a stone floor under two fingers of ash, and a ladder at the north end going down into the part that survived. One sage minds the beams; two items sit in the debris. This is the antechamber to the anomaly, not the anomaly — its job is to make the player walk slowly and listen before `PlasticOx_BurnedTowerB1F` gives them the vision.

## Plot points

1. **Entry from Ecruteak.** Town `(22,14)` lands at `(15,22)`. No cutscene, no music sting; wind, a loose sheet of tin, and the smell of wet charcoal do the work.
2. **The sage turns you around.** At `(9,20)` `PoxBurnedTower_Sage` reports that Morty went down the ladder and that the sages are minding the old beams. He is the only person on this floor who is not a tourist, and he is not a quest-giver: he answers two questions and goes back to watching the ceiling.
3. **The shell is readable.** The ground floor's collapsed stairwell, exposed joists, and memorial make the missing stair legible *before* the restoration happens one floor below, so the vision reads as recognition rather than spectacle.
4. **Descent.** The ladder at `(24,10)` is the only way on, into `PlasticOx_BurnedTowerB1F` at `(26,7)`. Nothing gates it here; the gate is badge 2 inside the Morty scene itself.
5. **Aftermath state.** Once `FLAG_POX_STORY_BURNED_TOWER` is set, the sage's text switches to the sages' regional mission and this floor should feel closed: the site becomes a place being watched rather than explored.

**Must not:** stage the restoration here (it belongs to `PlasticOx_BurnedTowerB1F`); release Raikou, Entei, or Suicune; let the sage explain the convergence; add a second NPC who knows what the player is about to see.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Arrival | `(15,22)`, from town `(22,14)` | always | plain warp, no map script | add an on-transition map script that only sets ambience and flag-driven visibility; no dialogue |
| Beam keeper | `(9,20)` `PoxBurnedTower_Sage` | split on `FLAG_POX_STORY_BURNED_TOWER` | two good, distinct lines already written | keep both; add that a surveyor chalked the joists and he is not to let anyone stand under them |
| Ladder down | `(24,10)` → `PlasticOx_BurnedTowerB1F` `(26,7)` | always | open warp | keep; the player should be able to hear the bell faintly from here before descending |
| Fire Stone | `(23,18)` `PoxBurnedTower_FireStone` | once | `finditem ITEM_FIRE_STONE` | keep, and let the sage have a line about the shrine's fire being kept in stone, not flame |
| Ether | `(3,7)` `PoxBurnedTower_Ether` | once | `finditem ITEM_ETHER` | keep; place it in a workman's tin rather than loose on the floor |
| Memorial | `(none)` `PoxBurnedTower_Memorial` | — | script written ("Some names are lost") but **no object or sign carries it** | place it at the entrance or the north wall; it is the floor's best line and currently unreachable |
| Wild encounters | whole floor, `land_mons` rate 20, Lv.22–24 | always | 12 slots, **5 of them Raticate** | rebalance: Torkoal, Slugma, Houndour and Gastly are the thematic spawns; Raticate should not be 42% of the floor |
| Tourist clutter | none | — | no objects besides the sage and two balls | propose a donation box, a laminated floor plan, and a rope line — the site is visited, and that is how ruins are visited |

## Dialogue guidance

- **The sage is a caretaker, not a priest.** He talks about loads, beams, chalk marks, and who is allowed to stand where. He answers the tower question with a shrug and a date.
- **Nobody on this floor performs grief.** The fire is old enough to be administrative: a rota, an insurance quarrel, a school visit every spring.
- **The tower does the talking.** Keep the player's own reactions external — footsteps changing sound over ash, a pigeon in the roof, the tin sheet.
- After `FLAG_POX_STORY_BURNED_TOWER`, the sage is the only speaker and his register lifts slightly: he now has an assignment, and he is proud of it in a dry way.

> BEAM KEEPER: Surveyor chalked that joist in spring. You can stand anywhere but there, and I'd take the stairs slow anyway.

> VISITOR (proposed): My grandmother says the bell used to be rung at the fourth hour. Nobody has rung anything here since.

> BEAM KEEPER, after the story: They've gone to find the ones that got moved. I mind the beams. It isn't the same work, but it's the work I have.

- **Do not:** have anyone say "convergence"; describe the vision as a vision; use the words "haunted", "cursed", or "aura"; give the sage a mystery to solve.

## Inspiration

- **Notre-Dame after 2019:** the rope line, the scaffolding, the salvage inventory, the volunteer who repeats "don't touch the stone". Converts directly into the beam keeper, the donation box, and the floor plan.
- **York Minster, 1984 fire:** restoration craftsmen who talk about joinery and insurance rather than drama. That is the sage's whole vocabulary.
- **A Japanese castle keep burned and rebuilt as a museum:** the surviving foundation left exposed under a modern shell, with a labelled diagram of what used to stand there.
- **Charcoal and rain:** the specific smell of a fire that is decades old and still reactivates when it rains. Use it as the floor's only recurring sensory detail.
- **Pokémon GSC/HGSS Burned Tower:** the three legends absent, the floor still a landmark. The restraint is the reference — the original never explains, and this floor should not either.

## Implementation hooks

- Wiki page: `plasticox-burnedtower.html`
- Map: `PlasticOx_BurnedTower` (`MAP_PLASTIC_OX_BURNED_TOWER`); 2 warps, no connections, no coord events, no map script
- Scripts: `data/maps/PlasticOx_BurnedTower/scripts.inc` (`PoxBurnedTower_Sage`, `PoxBurnedTower_FireStone`, `PoxBurnedTower_Ether`, `PoxBurnedTower_Memorial`), `data/scripts/plastic_ox_story.inc`
- Flags: `FLAG_POX_STORY_BURNED_TOWER` (set one floor below by `Pox_BurnedTower`)
- Items: `ITEM_FIRE_STONE`, `ITEM_ETHER`
- Known gaps: `PoxBurnedTower_Memorial` is dead — no object or sign references it. `PlasticOx_BurnedTower_MapScripts` is `.byte 0`, so the floor cannot react to the story flag except through the sage's text. The encounter table gives five of twelve slots to Raticate and none to a Ghost-type beyond Gastly.

## Open questions

- Should wild encounters stop once `FLAG_POX_STORY_BURNED_TOWER` is set? A site the sages are tending probably should not still spawn Rattata at the player.
- Is the ground floor meant to be a corridor with two items, or a room the player is supposed to linger in? It currently has no reason to linger beyond the sage.
- Where should the memorial go — at the entrance so every player reads it, or by the north wall where only the curious find it?
- Keep the Raticate weighting (a deliberate "vermin in the ash" read) or rebalance toward fire and ghost species?
