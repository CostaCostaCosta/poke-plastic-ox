---
title: Route 16
slug: route16-hns
kind: Route
act: 3
stage: "6 — Fortree to Lavender"
depth: supporting
wiki: route16-hns
maps: [Route16_hns]
status: drafted
---

# Route 16

## Snapshot

A donor map with no road. `Route16_hns` has no warps, no connections and no encounter table; its only object is a cuttable tree at `(49,34)` whose script prints a bicycle-safety line. Nothing in the checkout targets `MAP_ROUTE16_HNS`, so the player can never stand on it. The live Kanto Route 16 is `Route16_Frlg`; this note is an audit and a keep/retire recommendation, not a story beat.

## Plot points

1. **What is actually here.** One object, `(49,34)`, `Route16_EventScript_Npc1` — a plain `msgbox` on a cuttable-tree sprite, so the tree talks and cannot be cut. The map is tagged Hoenn, plays `MUS_RG_CELADON`, and sits in the `PlasticOxJohtoKanto` group with no way in.
2. **Nothing points here.** No warp, connection, coord event or script in the repo names `MAP_ROUTE16_HNS`; `src/data/wild_encounters.json` has no entry for it; `LAYOUT_ROUTE16_HNS` is used by this map alone. It is registered and unreachable.
3. **The live twin.** `Route16_Frlg` (`MAP_ROUTE16`) is the real Kanto Route 16: Celadon's east side, the downhill drop into Route 17, a Snorlax at `(31,13)`, six bikers, Lea and Jed, a working Cut tree at `(41,11)`, and the `Route16_NorthEntrance_1F_Frlg` gatehouse at `(20,6)`/`(27,6)`. Any Route 16 beat belongs there.
4. **The gatehouse caveat.** That gatehouse stops pedestrians with coord events keyed to `VAR_TEMP_1 == 0`, and only sets `VAR_TEMP_1` to 1 when `FLAG_GOT_BICYCLE` is set. In this build `FLAG_GOT_BICYCLE` is aliased to `0` in `include/constants/flags.h` (the non-FRLG table), i.e. a temp-range flag cleared on map load — so the bicycle check cannot survive the walk into the gatehouse and the pedestrian stop fires for everyone. Verify before promising the player the ride.
5. **Why stage 6 cannot use it.** The Fortree→Lavender leg runs Route 110; Kanto's Route 16 is on the far side of Celadon and would only be reached through the Route 8 → Underground → Route 7 bypass, which is the Saffron detour, not this stage's road.

**Must not:** invent a Fortree→Lavender scene here; place Rocket, Bill or Silph; claim the Cycling Road descent as this map's beat; add a second Snorlax or a second gatehouse; wire a warp into a map that has no return.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Talking tree | `(49,34)` | always | `Route16_EventScript_Npc1` prints "Check your bicycle before a long ride. Brakes matter!" on a cuttable-tree sprite; no Cut check, no item | delete it, or move the line to a person on `Route16_Frlg` |
| Entry | whole map | — | 0 warp events, 0 connections, 0 coord events; nothing in the repo names the map | remains unreachable; do not add one door without a reason and a return |
| Encounters, signs, items | whole map | — | no table in `src/data/wild_encounters.json`, no bg events, no item balls, no NPCs beyond the tree | none required |
| Live twin, for contrast | `Route16_Frlg` `(31,13)` Snorlax, `(41,11)` cut tree | always | six bikers, Lea and Jed, a working Cut tree, gatehouses and a closed pedestrian check | where the beat and the cast should live |

## Dialogue guidance

- **One line exists, and it is in the right register** for a brake-check gate: plain advice, no joke. It is misplaced, not bad.
- **Only if this map is revived:** a brake inspector, an inner-tube kid, a courier at the bottom of the hill. Three voices, no crowd — a short approach road cannot carry more.
- **Register:** mechanical, practical, second person. People on this road talk about equipment and gradients, never about the view.

> BRAKE INSPECTOR: Everybody thinks the brakes fail on the way down. They fail because nobody looked at them on the way up.

> INNER-TUBE KID: I sell two sizes. If you need the third size, you should be walking.

> COURIER: The hill is the easy part. The hard part is the queue where the road meets the city.

- **Do not:** build a cast for a map nobody can enter; reuse the existing bicycle line verbatim in two maps; describe the Cycling Road as a shortcut to anywhere; give a Kanto route a Fortree beat.

## Inspiration

- **FRLG's Cycling Road.** A one-way descent behind a brake-check gate and a "no pedestrians" sign — worth one gatekeeper and no more.
- **Velodrome approach roads and keirin towns.** Riders warming up outside the track, a mechanic with a torque wrench, a wall of past winners' photographs. Converts to a single person with a workstand.
- **The hill-town Sunday.** Kids with inner tubes, a shop that stocks two sizes, a courier who knows every light between the top and the bottom.
- **How it converts:** because this map is dead, all of it lands on `Route16_Frlg`'s six bikers — which is also why this note recommends retirement over resurrection.

## Implementation hooks

- Wiki page `route16-hns.html`; map `Route16_hns` (`MAP_ROUTE16_HNS`, layout `LAYOUT_ROUTE16_HNS`, music `MUS_RG_CELADON`, region Hoenn, group `gMapGroup_PlasticOxJohtoKanto`).
- Scripts: `data/maps/Route16_hns/scripts.inc`, which contains only `Route16_EventScript_Npc1`.
- Live twin: `Route16_Frlg` (`MAP_ROUTE16`) with `Route16_NorthEntrance_1F_Frlg`, `Route16_NorthEntrance_2F_Frlg` and `Route16_House_Frlg`; its gatehouse bicycle check keys `VAR_TEMP_1` off `FLAG_GOT_BICYCLE`, and the flag is `0` in this build's table.
- Known gaps: unreachable in every build path; no encounters; the tree is an NPC; the region header says Hoenn; the layout is orphaned; the map is in a live group, so it is one stray warp away from being enterable.
- Recommendation: retire the directory (see the artifact-cleanup skill); if a Celadon-side approach is wanted, extend `Route16_Frlg` instead.

## Open questions

- Retire this directory, or keep it as the Celadon-side approach and repoint Celadon's exit here? The second means moving or deleting `Route16_Frlg`, and the two maps would still share one name.
- Is the gatehouse bicycle check meant to be broken — nobody rides — or is `FLAG_GOT_BICYCLE` supposed to alias a real persistent flag in this build? Either way the live Kanto chain (Celadon → 16 → 17 → 18 → Fuchsia → Route 19) has no note and only that one gate; open region by design, or unguarded edge to close?
