---
title: Whirl Islands
slug: plasticox-whirlislands
kind: Cave
act: 6
stage: "Postgame — legacy dungeon"
depth: supporting
wiki: plasticox-whirlislands
maps: [PlasticOx_WhirlIslands]
flags: [FLAG_POX_WHIRL_ITEM, FLAG_POX_STORY_MANSION, FLAG_POX_HIDE_STORY_NPCS, FLAG_POX_TRIGGERS_ENABLED]
items: [ITEM_BIG_PEARL]
status: drafted
---

# Whirl Islands

## Snapshot

One room, 32×26, built from `LAYOUT_GRANITE_CAVE_B1F`, scored with `MUS_PETALBURG_WOODS`, filed under `MAPSEC_CINNABAR_ISLAND`, holding two NPCs who can never appear. This was the pre-Seafoam southern dungeon; v7 hands that job to Seafoam Islands and nothing in the current checkout routes the player here. The note is therefore an audit, not a scene: its job is to say plainly what the map is, what still points at it, and whether it should survive.

## Plot points

1. **The room is an orphan.** `PlasticOx_WhirlIslands` has 0 warps, 0 coordinate events, no connections, and no map script (`PlasticOx_WhirlIslands_MapScripts` is `.byte 0`). No warp anywhere under `data/` targets `MAP_PLASTIC_OX_WHIRL_ISLANDS`; the only references are its `data/maps/map_groups.json` registration and its own files.
2. **Both objects are permanently hidden.** `(5,2)` `Pox_WhirlItem` and `(3,17)` `Pox_WhirlIslandsExit` both carry the hide flag `FLAG_POX_HIDE_STORY_NPCS`, which `src/new_game.c` sets at new-game time and no script clears. Even a debug warp lands in a room with nothing to talk to.
3. **What the scripts would do if visible.** `Pox_WhirlItem` gives `ITEM_BIG_PEARL` once, recorded by `FLAG_POX_WHIRL_ITEM`, but refuses until `FLAG_POX_STORY_MANSION` is set — a Cinnabar Mansion gate with no in-room justification. `Pox_WhirlIslandsExit` says "I'll show you back outside" and warps to `MAP_CINNABAR_ISLAND` `(12,12)`.
4. **The exit is a trap.** `MAP_CINNABAR_ISLAND` is the legacy FRLG Cinnabar, and `(12,12)` is the coordinate gate `PoxRegion_route103_cinnabar_b`, which sends the player to Route 103 when `FLAG_POX_STORY_FUJI` is set and back to Cinnabar `(12,13)` otherwise. "Back outside" would drop the player onto a live trigger.
5. **Its successor already exists.** `Pox_WhirlGuide` on `CinnabarIsland_hns` `(39,28)` (and a second copy on `CinnabarIsland_Frlg` `(13,12)`, both hidden) says "SEAFOAM ISLANDS lie along the coast to MOSSDEEP." The one useful sentence the Whirl room ever carried has been moved to a signpost.

**Must not:** be re-opened into the mainline; host a legendary, a Rocket scene, or a reveal; be "repaired" with a door and an exit before someone decides what it is for. If it is kept at all it is a curiosity room, and it must not pretend to be a Johto dungeon while wearing a Hoenn cave layout.

## Key interactions

The room is functionally empty: it has two objects and both are hidden by default. The rows below record what exists and what a decision would have to add.

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Entrance | nowhere | n/a | no warp, connection, or coordinate event leads here | either a real door off the Cinnabar coast (new warp required) or retire the map |
| Pearl | `(5,2)` `Pox_WhirlItem` | hidden by `FLAG_POX_HIDE_STORY_NPCS`; needs `FLAG_POX_STORY_MANSION`; once via `FLAG_POX_WHIRL_ITEM` | silent `ITEM_BIG_PEARL` pickup | dead chain: remove, or give the pearl its own reason to be in a sea cave |
| Exit guide | `(3,17)` `Pox_WhirlIslandsExit` | same hide flag | warps to legacy `MAP_CINNABAR_ISLAND` `(12,12)` | never ship this destination; it is a gate tile, not a beach |
| Successor signpost | `CinnabarIsland_hns` `(39,28)` `Pox_WhirlGuide` | hidden by `FLAG_POX_HIDE_STORY_NPCS` | points at Seafoam → Mossdeep | unhide it if any southern-coast hint survives; it duplicates the `Pox_MossdeepRoad` neighbour at `(38,28)` |
| Room identity | map metadata | always | Granite Cave layout, Petalburg Woods music, Cinnabar map section | if kept: Whirl-specific map section and cave ambience, or it reads as Hoenn |
| Legendary hook | none | n/a | nothing in the room uses `FLAG_DEFEATED_LUGIA`, which still exists in `data/scripts/hall_of_fame.inc` | decide whether Whirl is where that encounter lives, or drop the association |

## Dialogue guidance

If the map is retired, this section is moot; if it is kept, it speaks with exactly two voices and no more. The room is a cold sea cave at low tide: sound of water in a chimney, no furniture, no staff. Keep every line short enough to echo.

> BEACHCOMBER: Tide goes out twice a day and leaves the same stones. I come down anyway. The pearl was luck, not a secret.

> CHILD: Everyone says there is a Pokémon under the whirlpool. Everyone says a lot of things about water.

> GUIDE: Mind the swell on the way out. The path back is not the path you came by, and it is not kinder.

- **Do not:** add a legendary encounter without a decision; add lore about the convergence; let anyone mention Lugia by name unless the keep decision is made; write a maze hint — the room has no puzzle and no HM gate.

## Inspiration

- **The Naruto whirlpools in Japan**: tide tables posted at a viewing platform, boats that only run at slack water, locals who are bored of the spectacle. Converts into a single working NPC who talks about tides rather than monsters.
- **The Gulf of Corryvreckan**: a real whirlpool with a shipping lane and a lighthouse; the danger is scheduled, not mythical. If the room survives, its mood is "scheduled hazard", not "legend".
- **Gen 2's Whirl Islands**: a Whirlpool-gated maze. v7 deliberately has no mandatory HMs (even Victory Road needs none), so the original dungeon's only mechanic has no footing here — which is the real reason it was replaced.
- **Sea caves at low tide**: smell of kelp, wet stone, a chimney that booms. One ambient detail is worth more than a puzzle.

## Implementation hooks

- Wiki page: `plasticox-whirlislands.html`.
- Maps: `PlasticOx_WhirlIslands` (`MAP_PLASTIC_OX_WHIRL_ISLANDS`, `LAYOUT_GRANITE_CAVE_B1F`, `MAPSEC_CINNABAR_ISLAND`, `MUS_PETALBURG_WOODS`).
- Scripts: `data/scripts/plastic_ox_story.inc` (`Pox_WhirlItem`, `Pox_WhirlIslandsExit`, `Pox_WhirlGuide`); `data/maps/PlasticOx_WhirlIslands/scripts.inc` (empty map scripts).
- Flags: `FLAG_POX_WHIRL_ITEM`, `FLAG_POX_STORY_MANSION`, `FLAG_POX_HIDE_STORY_NPCS` (set in `src/new_game.c`), `FLAG_POX_TRIGGERS_ENABLED`.
- Items: `ITEM_BIG_PEARL`.
- Known gaps: orphan map with no inbound warp; both objects hidden by a flag set at new game; exit warps into the legacy FRLG Cinnabar's Route 103 gate; donor layout, music and map section; `Pox_WhirlGuide` duplicated across two Cinnabar maps and hidden on both; `Pox_WhirlItem`'s `FLAG_POX_STORY_MANSION` check has no in-room setup; the room has no exit at all if the guide is hidden, so any warp in would soft-lock.

## Open questions

- **Recommendation: retire `PlasticOx_WhirlIslands`.** It has no entrance, no visible content, no unique art, and its one sentence already lives on Cinnabar. Keeping it costs a map slot and a soft-lock risk; retiring it means deleting the map, its two scripts, and `FLAG_POX_WHIRL_ITEM`.
- If retired, does anything still need a Whirl room? Earlier plans kept it as an optional synthetic room, and the engine still carries `FLAG_DEFEATED_LUGIA`. Assign Lugia elsewhere or drop the thread.
- If kept, what is it for — a pearl curiosity, a Lugia encounter, or a debug sandbox? All three need a door, an exit, and a map section before the first line of dialogue.
- Should the duplicate `Pox_WhirlGuide`/`Pox_MossdeepRoad` pair on `CinnabarIsland_hns` `(38,28)`–`(39,28)` be unhidden, merged, or left as dead objects?
