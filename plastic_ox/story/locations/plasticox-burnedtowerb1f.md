---
title: Burned Tower B1F
slug: plasticox-burnedtowerb1f
kind: Cave
act: 2
stage: "4 — Ecruteak and the Burned Tower"
depth: full
wiki: plasticox-burnedtowerb1f
maps: [PlasticOx_BurnedTowerB1F]
flags: [FLAG_POX_STORY_BURNED_TOWER]
items: [ITEM_ULTRA_BALL, ITEM_BIG_PEARL]
status: drafted
---

# Burned Tower B1F

## Snapshot

The basement landing under the tower, where the fire stopped: a single wall of dressed stone, a floor of packed ash, and two sages waiting for Morty. Talking to Morty at `(8,9)` rewrites one metatile into a whole stair, holds it for a line of text, and takes it away again. This is reveal-ladder step 5 and the birthplace of the sages' regional mission; there is no battle here, and nothing is released.

## Plot points

1. **Descent.** The only entrance is the ladder from `PlasticOx_BurnedTower` `(24,10)`, arriving at `(26,7)`. No map script; the room is already occupied, which is the point.
2. **The sages are conferring.** `LOCALID_POX_TOWER_SAGE_1` and `LOCALID_POX_TOWER_SAGE_2` at `(7,8)` and `(9,8)` came to tell Morty about legendary Pokémon reported far from their homes. This is the seed he turns into an order two minutes later; the player hears it as gossip first.
3. **Morty at the wall.** `Pox_BurnedTower` at `(8,9)` requires badge 2. He points at `(10,9)`: "A stair stood there before the fire."
4. **The anomaly — ladder step 5.** The metatile at `(10,9)` becomes a rebuilt doorway/stair (`0x6A6`), the view redraws, and the text supplies a bell ringing from an empty landing; then the tile returns to ash (`0x6F2`) and the player picks up the fallen ceremonial bell. One tile, two fades, no explanation.
5. **Morty's reading.** "Places remember what they were" — then he pivots immediately to the practical: the displaced Pokémon need help now. He orders the sages to search the region, shelter them, and stay until they feel safe. They accept and are removed; Morty is removed and returns to `PlasticOx_MortyGym`.
6. **State.** `FLAG_POX_STORY_BURNED_TOWER` sets, the scene cannot replay, and the room is left empty behind the player.

**Must not:** release Raikou, Entei, or Suicune; restore more than the one stair; name the cause or the mechanism; have Morty explain the phenomenon twice; let a sage name the legendary they will find.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Morty | `(8,9)` `Pox_BurnedTower` | badge 2; `FLAG_POX_STORY_BURNED_TOWER` unset | full five-message scene, metatile swap, flag, self-removal | keep the structure; break the last message out so the player can walk away from the mission briefing |
| The wall | `(10,9)` `setmetatile 0x6A6` / `0x6F2` | mid-scene | swaps one tile behind a fade-to-white, twice | animate or hold the redraw in place for a beat so the player *sees* the stair rather than reading that they did |
| Sages | `(7,8)`, `(9,8)` `PoxBurnedTower_AssembledSage` | until the scene runs | both say the identical line, both removed at the end | two sages who answer differently: one on logistics, one on fear |
| Ultra Ball | `(6,9)` `PoxBurnedTower_UltraBall` | once | `finditem ITEM_ULTRA_BALL` | keep; put it where the sages set down their pack |
| "TM12" | `(5,15)` `PoxBurnedTower_TM12` | once | label says TM12, script gives `ITEM_BIG_PEARL` | rename the label or change the item — this is a live mismatch |
| Ceremonial bell | scene only | mid-scene | recovered in text, recorded nowhere | make it a key item (new item required) or keep it purely narrative, but decide |
| Exit | `(26,7)` → `PlasticOx_BurnedTower` `(24,10)` | always | plain warp up | keep; the climb out is the emotional beat, so no text on the ladder |
| Wild encounters | whole floor, Lv.23–26 | always | 12 slots, **6 of them Sableye** | thin the table; the landing where a scene plays should not spawn encounters inside the conversation radius |

## Dialogue guidance

- **Morty is a priest giving instructions in a burnt basement.** Flat, concrete, unhurried; he uses "stand", "look", "go", and never says "perhaps". He does not console anyone.
- **The elder sage** thinks in rations, distances, and how long a frightened animal takes to trust a person.
- **The younger sage** is the one who asks the question the player is thinking, and gets no answer.
- **Nobody names the legendary Pokémon.** The sages are told to find whoever needs finding; naming them would turn a rescue into a checklist.
- After the scene, this floor has no speakers at all. Leave it that way — the silence is the second half of the beat.

> MORTY: Stand where I'm standing. Don't cross the ash line; the floor past it isn't floor.

> ELDER SAGE: How much do we carry? A frightened Pokémon does not eat politely, and it will not wait while we go back for more.

> YOUNGER SAGE: I've never been past the next valley. Do I go north, or do I wait to be told?

> MORTY: You'll know them when you find them. They won't be where their maps say they are.

- **Do not:** use "convergence" as a spoken noun; describe the stair as a vision, illusion, or ghost; let anyone say the tower is haunted; explain what the bell is for.

## Inspiration

- **Surveying a ruin:** a total station or laser scan snapping a missing structure back into place, then a brass witness pin left in the wall. Converts into the chalk marks one floor up and a pin the player can find at `(10,9)` after the scene.
- **Shuri Castle, burned 2019, rebuilt from photographs and measurements:** the stair exists in the record before it exists in stone. That is the entire logic of "places remember what they were", stated without mysticism.
- **The temple bell (bonshō) and its long decay:** Chion-in's bell is a landmark you hear before you see. The bell heard from an empty landing is the scene's only sound design, and it should outlast the vision.
- **Negative space as subject:** Ryoan-ji's raked gravel, a plinth with no statue. The missing stair is more legible than the restored one, which is why the tile must go back to ash.
- **Field rescue of displaced wildlife:** a team with a crate, a blanket, and a feeding schedule. The sages' mission is wildlife rehabilitation, not a legendary hunt, and their lines should sound like it.

## Implementation hooks

- Wiki page: `plasticox-burnedtowerb1f.html`
- Map: `PlasticOx_BurnedTowerB1F` (`MAP_PLASTIC_OX_BURNED_TOWER_B1F`); 1 warp, no connections, no coord events, `_MapScripts` is `.byte 0`
- Scripts: `data/maps/PlasticOx_BurnedTowerB1F/scripts.inc` (`PoxBurnedTower_AssembledSage`, `PoxBurnedTower_UltraBall`, `PoxBurnedTower_TM12`), `data/scripts/plastic_ox_story.inc` (`Pox_BurnedTower` and its five message strings from `Pox_Text_BurnedTowerBefore` to `Pox_Text_BurnedTowerFarewell`)
- Flags: `FLAG_POX_STORY_BURNED_TOWER`
- Metatiles: `0x6A6` restored stair/door, `0x6F2` burnt state, both on `(10,9)`
- Known gaps: `PoxBurnedTower_TM12` awards `ITEM_BIG_PEARL`; the two sages share one string and have no post-scene branch; the recovered bell has no item or flag; the anomaly is hidden behind `FADESCREEN FADE_TO_WHITE`, so the transition itself is never visible; Sableye holds half the encounter slots.

## Open questions

- Does the ceremonial bell become a key item (new item required) that later identifies the sage-beside-a-legendary scenes, or stay as prose?
- Should the stair be revealed in place with a short animation instead of two white fades? The current version writes a better scene than it shows.
- Do the two sages need separate lines, or should one be silent so the player notices the other is speaking for both?
- Should the landing be encounter-free after the scene, so leaving the room is quiet?
