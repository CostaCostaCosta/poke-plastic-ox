---
title: Route 20West
slug: plasticox-route20west
kind: Route
act: 3
stage: "9 — Cinnabar and the Mansion"
depth: full
wiki: plasticox-route20west
maps: [PlasticOx_Route20West]
flags: [FLAG_POX_STORY_MANSION, FLAG_POX_TRIGGERS_ENABLED, FLAG_POX_STOPPED_SEAFOAM_B3F_CURRENT, FLAG_POX_STOPPED_SEAFOAM_B4F_CURRENT]
status: drafted
---

# Route 20West

## Snapshot

A 66×20 strip of open ocean between Cinnabar's south shore and the black rock that holds Seafoam Islands' western door. The player warps in at `(48,14)` already in the water, crosses north-east past four shoals and three bare islets, and leaves the sea at `(60,8)`, the only landing on the map. It is the doorstep of the Seafoam passage, and its emotional note is exposure: after a chapter of mansion corridors, all this map has is wind, salt, and no one to talk to.

## Plot points

1. **Leaving Cinnabar.** The island's sea exit (`CinnabarIsland_Frlg` `(23,10)`, `PoxRegion_cinnabar_sea_a`) refuses until `FLAG_POX_STORY_MANSION` is set; open, it warps here to `(48,14)`. This is the last tile of reveal-ladder **step 9** — the route itself adds no information, only distance.
2. **Arrival resets the dungeon.** `PoxRegion_Arrival_PlasticOx_Route20West` calls `Route20_EventScript_ResetSeafoamBouldersForB3F` and `...ForB4F` while `FLAG_POX_STOPPED_SEAFOAM_B3F_CURRENT` / `...B4F` are unset, clearing the boulder hide-flags (`FLAG_POX_HIDE_SEAFOAM_1F_BOULDER_1` and its neighbours). In play: leave the cave before the current is stopped and the rocks are back where they started. Once the flag is set, the reset no longer fires.
3. **One door.** The map's single warp at `(60,8)` is an `MB_NON_ANIMATED_DOOR` in the rock, landing at `MAP_SEAFOAM_ISLANDS_1F` warp 3; the rock above it is the map's only dry land.
4. **No bypass, structurally.** The map declares zero connections on every edge and everything outside the islets and the cave rock is `MB_OCEAN_WATER`; there is no surf line to `PlasticOx_Route20East` and no way back to Cinnabar except the portals. v7's "no surf-around" rule is therefore enforced — but by an invisible map edge, not by anything the player can see.
5. **The return tripwire.** `(48,13)`, one step north of the arrival tile, fires `PoxRegion_cinnabar_sea_b` on contact (`VAR_POX_PORTAL_TRIGGER` is 0) and warps to Cinnabar `(22,10)`. Its `_Closed` branch is unreachable, since the flag is already set before the player can stand there.

**Must not:** name Bill, Silph, the adaptive system, or the Weather Institute; stage a Rocket appearance; explain the current reset in system language; spoil what waits inside Seafoam or on the eastern half; or give the cave mouth a level-name sign ("SEAFOAM ISLANDS →").

## Key interactions

This map currently holds **zero objects** — no NPCs, signs, trainers, or items. One warp, one coord event, one arrival script.

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Seafoam cave mouth | `(60,8)` warp | always | silent warp to `MAP_SEAFOAM_ISLANDS_1F` warp 3, no prompt, no sign | keep; one sign or buoy so the door reads from open water |
| Cinnabar return | `(48,13)` coord | `VAR_POX_PORTAL_TRIGGER` 0, `FLAG_POX_STORY_MANSION` set | `PoxRegion_cinnabar_sea_b` → Cinnabar `(22,10)` | a jetty on the west shore, or a buoy line that marks the tile |
| Arrival reset | map load | `FLAG_POX_STOPPED_SEAFOAM_B3F_CURRENT` / `...B4F` unset | silently restores the Seafoam boulders | keep; let one line on the rocks acknowledge the water "taking the rocks back" |
| Open water | x 0–47 | always | `MB_OCEAN_WATER`, no current, no encounter table | one visible reason for the one-wayness: current, rock field, or drop |
| Shoals | `(24,6)` `(42,9)` `(16,14)` sand, `(32,13)` shallow bank | always | `MB_SAND` and `MB_SHALLOW_WATER`, decorative | two become landmarks: a bait digger's spot, a hidden find |
| Rock islets | `(2,8)` `(13,9)` `(8,13)` | always | plain `MB_NORMAL` rock, no object | one gets a marker or a nesting bird; no more |
| Donor duplicate | `Route20_Frlg` | unreachable | 120×20, eleven trainer objects, two Seafoam warps, its own copy of the reset | retire (see Open questions) |

## Dialogue guidance

- **Who speaks:** today nobody. If voices are added they belong to the rock, not the water: a bait digger on the shoals, a diver working a float line, a fisherman waiting out the swell, and one sign. No trainer taunts — no trainer type exists on this map, and a taunt would promise a battle that never starts.
- **Register:** short, practical, weathered. People talk about swell, cold, what the tide left, whether the cave is breathing in or out. Numbers and named things (hours, metres, which way the wind turned) carry the texture; nobody explains the world.
- **Before / after:** the water reads the same before and after Seafoam. The one shift is the reset — a diver describing the cave "spitting the boulders back" is saying out loud what the arrival script already does.
- **The sign is not a system message:** distance, weather, consequence — never a map name with an arrow under it.

> BAIT DIGGER: The tide leaves the crabs under the black rock. It leaves the hooks too. I take the crabs.

> DIVER: The cave pulls on the ebb. If you feel it pulling, you are already too close to the door.

> FISHERMAN: Two hours out of Cinnabar and the wind turned. My line has been dry since the turn.

> SIGN: SEAFOAM ISLANDS / West door. No landing past this rock. Watch the swell.

- **Do not:** mention the Mansion, Entei, Blaine, Bill, Silph, or "the system"; describe the reset as a mechanic; write a challenge line for a battle that cannot start; give two speakers the same warning; or make the sea haunted.

## Inspiration

- **Kagoshima Bay under Sakurajima** — black volcanic rock, warm shallows at the edge of cold water, ash in the wind, fishermen who read the mountain before the sky. Converts into the Lavaridge rock on the islets and the bait digger's trade.
- **Jeju and Pembrokeshire sea caves** — a blowhole that inhales before it spits, a swell window measured in minutes, a local rule about not entering on the push. Converts into the cave-mouth sign and the diver's tide knowledge.
- **Ama free divers** — one breath, a float line, a knife, a basket, cold that arrives in the fingers first. Converts into the diver as a worker, not a swimmer: she is not here to race the player.
- **Small-boat offshore fishing** — handlines, chum, a bonito troll, a skipper who stops talking when the birds go quiet. Converts into the fisherman and into the route's only plausible reward: something left on a rock, not handed over.
- **FireRed/LeafGreen Route 20's rhythm** — a long water road dotted with swimmers and one rock at the far end holding Seafoam. Keep the dots, lose the battles: the swimmers become two people on the shoals and one boat, and the silence is the point.

## Implementation hooks

- Wiki page `plasticox-route20west.html`; map `PlasticOx_Route20West` (`MAP_PLASTIC_OX_ROUTE20_WEST`, layout `LAYOUT_PLASTIC_OX_ROUTE20_WEST`, 66×20, HNS primary tileset with the Lavaridge secondary, `MAPSEC_ROUTE_20`, `REGION_HOENN`, `WEATHER_SUNNY`, `MUS_RG_ROUTE3`).
- Scripts: `data/maps/PlasticOx_Route20West/scripts.inc` holds only the `ON_TRANSITION` call to `PoxRegion_Arrival_PlasticOx_Route20West`; both portals and that arrival live in `data/scripts/plastic_ox_region.inc`; the reset labels `Route20_EventScript_ResetSeafoamBouldersForB3F` / `...ForB4F` are defined in the donor `data/maps/Route20_Frlg/scripts.inc`.
- Gates: `FLAG_POX_STORY_MANSION` on the Cinnabar side; `FLAG_POX_TRIGGERS_ENABLED` short-circuits every portal script for the walkable build.
- Trainers / items: none, and **no encounter table** — the map is absent from `src/data/wild_encounters.json`, so Surf and fishing return nothing.
- Known gaps: zero objects of any kind; no wild encounters on a fully aquatic map; the anti-bypass rule is an invisible border rather than a current, rock field, or one-way drop; the return portal is a mid-water tripwire at x 48 with no jetty or buoy; the arrival silently undoes Seafoam's boulder work; a `REGION_HOENN` header and Lavaridge tileset sit on a Kanto sea map; the unreachable donor `Route20_Frlg` still duplicates this route and owns the reset labels.

## Open questions

- Keep the invisible border as the bypass guard, or add a current line between the shoals and the cave mouth? Recommend the current — v7 asks for a visible reason and the shoals already anchor it.
- Retire the donor `Route20_Frlg`, or keep it as the home of the reset labels? Its only live role is holding two labels; recommend moving them into the Plastic-Ox region file and retiring the donor.
- Should leaving Seafoam really undo the boulder work, and should something say so aloud — or is the lost progress its own message?
- Encounters: reuse the donor's Tentacool water table and Magikarp/Horsea fishing, or retune for an act-3 party? The route currently pays nothing for surfing it.
