---
title: Dark Cave South Side
slug: darkcave-southside-hns
kind: Cave
act: 1
stage: "0 — Opening network"
depth: full
wiki: darkcave-southside-hns
maps: [DarkCave_SouthSide_hns]
flags: [FLAG_POX_HIDDEN_DARKCAVE_MAXETHER, FLAG_POX_HIDDEN_DARKCAVE_BLACKFLUTE, FLAG_POX_HIDDEN_DARKCAVE_POTION, FLAG_POX_HIDDEN_DARKCAVE_REVIVE]
items: [ITEM_ROCK_SMASH_KEY, ITEM_POTION, ITEM_REVIVE, ITEM_MAX_REVIVE, ITEM_ELIXIR, ITEM_MAX_ETHER, ITEM_BLACK_FLUTE]
status: drafted
---

# Dark Cave South Side

## Snapshot

A 78×50 limestone throat with two mouths: one on the north end of Route 2 at `(14,20)` and one on Route 46 at `(56,46)`. The player walks it after Ilex Forest, not before, because the Route 2 mouth sits past the forest's north gate; it loops the western network back to Cherrygrove without shortening the road to Rustboro. Nothing here is required, nobody here battles, and the whole cave is one hiker, four item balls and a very patient Larvitar. The emotional note is *quiet*: the first place in the game that does not ask the player for anything.

## Plot points

1. **A seam, not a story.** Reveal-ladder **step 1** only: a Kanto road and a Johto road share a cave. The player should register the convenience and nothing else; no one in the cave has an opinion about why the rock is where it is.
2. **The borrowed key.** The hiker at `(14,17)` (`DarkCave1_EventScript_RockSmashKeyHiker`) gives `ITEM_ROCK_SMASH_KEY`, which lets the player break cracked rocks with the key instead of a party Pokémon (`EventScript_RockSmash` checks it first). It belongs to the same family as Ilex's Headbutt Key, and should feel like a tool lent by a working man, not a Gym prize.
3. **The key currently buys nothing.** Both cracked rocks — `(18,19)` and `(43,12)` — stand in four-tile openings; a walk-reachability check from either mouth reaches the far exit with both rocks treated as walls. The hiker's line "That cracked rock blocks the way?" is false in the current build. Either a rock must actually gate a pocket or the line must stop claiming it does.
4. **The dark is the content.** Three time-of-day tables, all Lv 5–8, encounter rate 20: Zubat, Baltoy and Swinub everywhere, **Teddiursa** in the morning, **Makuhita** in the day, **Snorunt** and **Duskull** at night, and **Larvitar** in all three. Rock Smash adds Aron, Rhyhorn, Geodude and Onix. Larvitar is the cave's real reward and the reason a player bothers with an optional loop.
5. **The pockets.** Visible balls: Potion `(10,7)`, Revive `(45,8)`, Elixir `(59,47)`, Max Revive `(51,41)`. Hidden: Max Ether `(60,18)`, Black Flute `(33,20)`. The Max Revive is sealed: no walkable route from either mouth reaches its 2×3 alcove.
6. **Two mouths, one direction of use.** North mouth returns to Route 2; south mouth opens onto Route 46, which runs to the `Gate_Route29_Route46_hns` gate and the Cherrygrove side. It is a return loop for a player who has already passed Ilex, never a bypass of Roxanne.

**Must not:** stage a Team Rocket scene (their three are Mt. Moon, Pokémon Tower and Silph); explain the convergence, name Diglett's Cave, or call the seam a tunnel "between regions"; put a legendary, a shrine or a scripted gift in the dark; make the cave mandatory for the Rustboro road; name Bill, Silph or the adaptive system.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Key hiker | `(14,17)`, `DarkCave1_EventScript_RockSmashKeyHiker` | `ITEM_ROCK_SMASH_KEY` not held | gives the key, then a reminder line | keep the gift; drop "blocks the way", describe the tool honestly |
| North cracked rock | `(18,19)`, `EventScript_RockSmash` | `FLAG_TEMP_1` | vanilla smash prompt, wild encounter roll | keep; move the Revive ball behind it so the key has a first use |
| East cracked rock | `(43,12)`, `EventScript_RockSmash` | `FLAG_TEMP_3` | same | keep; leave as the second lesson, not a gate |
| Potion ball | `(10,7)`, `DarkCave1_EventScript_ItemPotion` | `FLAG_POX_HIDDEN_DARKCAVE_POTION` | `finditem ITEM_POTION` | keep |
| Revive ball | `(45,8)`, `DarkCave1_EventScript_ItemRevive` | `FLAG_POX_HIDDEN_DARKCAVE_REVIVE` | `finditem ITEM_REVIVE` | keep |
| Max Revive ball | `(51,41)`, `DarkCave1_EventScript_ItemMaxRevive` | sealed alcove | `finditem` an item nobody can reach | relocate, or open the alcove from the south side |
| Elixir ball | `(59,47)`, `DarkCave1_EventScript_ItemElixir` | near the south mouth | `finditem ITEM_ELIXIR` | keep; a reward for the long way round |
| Hidden Max Ether | `(60,18)` | `FLAG_POX_HIDDEN_DARKCAVE_MAXETHER` | hidden pickup | keep |
| Hidden Black Flute | `(33,20)` | `FLAG_POX_HIDDEN_DARKCAVE_BLACKFLUTE` | hidden pickup, never explained | keep; let one NPC mention who left it |
| North mouth | `(14,20)` | warp to `MAP_ROUTE2` | door tile has no behavior, warp never fires | repair the metatile attribute before shipping |
| South mouth | `(56,46)` | warp to `MAP_ROUTE46_HNS` | same defect | repair |
| Empty middle | whole map | no NPCs, no signs, no map script | silence | two voices at most: one at each mouth |

## Dialogue guidance

- **Who speaks:** the key hiker, and at most two new mouths — an oil-and-wick seller at the south mouth and a child counting Zubat at the north mouth. Nobody else lives here. The cave is allowed to be mostly empty.
- **Register:** short, practical, spoken while doing something else. Lamp oil, boots, a bad knee, how many bats. No awe, no geology lectures, no hint that the player is in a special place.
- **Before / after:** before Ilex the mouths are scenery. After Ilex the north mouth is where the player first realises the cave goes somewhere they have already been; the hiker should greet a returning player by asking whether the key worked, not by explaining the map.
- **The hiker's key line** is the one place the cave can be funny: he has given away the same key before and is pleased to have a second use for the story.

> HIKER: Cracked, not broken. A crack is a door somebody hasn't finished yet.

> OIL SELLER: Two wicks a week if you walk it slow. Four if you stop to look at the ceiling. Nobody looks at the ceiling.

> CHILD: Forty-one. Forty-two. The one by your boot doesn't count, it lives here.

> HIKER, on the return: Back already? Then the key worked. Good. I hate being wrong about a rock.

- **Do not:** call it a labyrinth; mention Diglett, Flash or "the old cave"; give the hiker a theory about the merged region; have anyone battle; put a voice deeper than the lamps in the dark.

## Inspiration

- **A worked limestone cave, not a fantasy cavern.** Derbyshire show caves and salt mines: handrails, a lamp every twelve paces, a guide who has said the same sentence ten thousand times. Converts into the oil seller's trade and the hiker's practical pride.
- **Quarrymen's bothies.** A dry stone hut with a kettle, a coat on a nail, a rota pencilled on the door. The key hiker lives here in spirit: his job is to keep a tool in circulation, not to guard a secret.
- **Night shift.** One lamp, one cart, one man who prefers the hours. The Black Flute hidden at `(33,20)` belongs to whoever worked the night shift and forgot it.
- **Gen 2 Dark Cave's austerity.** No trainers, no gimmick, a few good items and one rare encounter. Keep that restraint; the cave is a rest, and the rest is the design.
- **A cave that is a shortcut in local memory.** Village people who cut through the hill to the next valley and think nothing of it. Converts into the child's count and the seller's "you're the third today".

## Implementation hooks

- Wiki page: `darkcave-southside-hns.html`
- Maps: `DarkCave_SouthSide_hns` (`MAP_DARK_CAVE_SOUTH_SIDE_HNS`); neighbours `Route2_Frlg` (`MAP_ROUTE2`, warp 3) and `Route46_hns` (`MAP_ROUTE46_HNS`, warp 2).
- Scripts: `data/maps/DarkCave_SouthSide_hns/scripts.inc` (labels still carry the donor `DarkCave1_` prefix), `data/scripts/field_move_scripts.inc` (`EventScript_RockSmash`), `data/scripts/plastic_ox_items.inc` (hidden pickups).
- Flags: `FLAG_POX_HIDDEN_DARKCAVE_MAXETHER`, `FLAG_POX_HIDDEN_DARKCAVE_BLACKFLUTE`, and the four item-ball flags `FLAG_POX_HIDDEN_DARKCAVE_POTION` / `_REVIVE` / `_MAXREVIVE` / `_ELIXIR` — note that visible balls are gated by flags named "hidden".
- Encounters: three land tables (morning / day / night) and one rock-smash table, all in `src/data/wild_encounters.json`; keep the Larvitar line in all three.
- Known gaps: **both mouths are dead** — `(14,20)` and `(56,46)` use secondary-tileset metatiles 306/307 while `gTileset_Cave_Default_Hns` carries 306 attribute entries for 308 metatiles, so neither tile has door behavior; `DarkCave1_*` labels and `MAP_DARK_CAVE_SOUTH_SIDE_HNS` naming still read as donor splits; the Max Revive is unreachable; the hiker's warning is untrue; no darkness routine or map script is attached despite the cave's name; item balls reuse "hidden" flags.
- New content required: one or two NPC objects only if the mouths get voices (new local ids), and no new flag unless the Black Flute gets a giver.

## Open questions

- Should the cave actually require the key (move the Elixir or the Revive behind a rock), or stay a free walk with a convenience item? Recommend gating one pocket.
- Repair both door metatiles (pad `metatile_attributes.bin` per `plastic_ox/notes/HANDOFF_WAVE4.md`), or make the cave a one-way downhill shortcut as `plastic_ox_map_v7.md` prefers for Route 46 / Route 45?
- Is a Lv 5–8 Larvitar appropriate this early, or should the rare slot be a cave commoner once the Dark Cave is genuinely reachable?
- Keep the Max Revive alcove as a Rock Smash secret reached from the south, or delete the item?
