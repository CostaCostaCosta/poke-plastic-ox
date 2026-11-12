---
title: Goldenrod City Department Store 7FNight
slug: goldenrodcity-departmentstore-7fnight-hns
kind: City
act: 1
stage: "3 — Goldenrod"
depth: supporting
wiki: goldenrodcity-departmentstore-7fnight-hns
maps: [GoldenrodCity_DepartmentStore_7FNight_hns]
status: drafted
---

# Goldenrod City Department Store 7FNight

## Snapshot
A second, complete copy of the department store roof, identical in geometry and warp to `GoldenrodCity_DepartmentStore_7F_hns`, with four different night lines. It is currently unreachable: no map, script or code path warps here. Treat this note as an audit, not a design brief.

## Plot points
1. **What the map is.** Same deck, same stair warp at `(22,5)` into `GoldenrodCity_DepartmentStore_6F_hns`, four objects at the day map's coordinates: the nerd at `(22,11)`, the fat man at `(11,6)`, the bug catcher at `(12,10)`, the woman at `(19,8)`. The day map's `LOCALID_GOLDENROD_ROOF_NERD` is not carried over, so any future script must not assume it here.
2. **Why it is unreachable.** Nothing in `data/` or `src/` warps to `MAP_GOLDENROD_CITY_DEPARTMENT_STORE_7FNIGHT_HNS`; the only references are `data/layouts/layouts.json` and `data/map_groups.json`. The game has a real time-of-day system (`GetTimeOfDay`), so the intended design was almost certainly a time-swapped twin whose branch was never written. **If it is wired, the voice is "closing time", not "second location":** tower lights, cooling roof, warm shop below, last shoppers. No new mechanics, no item, no night-only plot NPC.

**Must not:** become a place the plot hides something; introduce an NPC with world knowledge the day roof lacks; mention Saffron's seal, Silph, Bill, or the convergence.

## Key interactions
| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Nerd / fat man | `(22,11)`, `(11,6)`, `..._7FNight_hns_0`–`1` | always | tower lights counted on a break; the roof cools while the shop stays warm | keep both; the light count is the best of the four and belongs in the day map if this one is retired |
| Bug catcher / woman | `(12,10)`, `(19,8)`, `..._7FNight_hns_2`–`3` | always | lamps and moths; last shoppers hurrying home | keep both; they carry the closing-time register |

## Dialogue guidance
- Everyone is at the end of a shift or an evening: shorter sentences than the day roof, fewer questions, no small talk about the view. The woman is the only one looking outward at the city rather than down at the shop floor, and she gets the last word. Keep the lights tangible — blinking tower lights, lamps, a window going dark — because that is the whole reason the twin exists.

> NERD: Twelve lights now. There were fourteen when I came up, so two floors have gone home.

> BUG CATCHER: Moths come to the lamps, and my lot follow the moths. We leave before they get lost.

> WOMAN: The last shoppers are always in a hurry. I like the city once they've stopped.

**Do not:** give anyone new information, add a night-only shop or trainer, or let the roof become a viewpoint for anything plot-relevant.

## Inspiration
- **Depachika closing hours:** staff turning off display lights floor by floor, the warm food floor still glowing, a last escalator announcement. Converted into the tower-light count; the moths at the lamps come from any Tokyo rooftop after dark.

## Implementation hooks
- Wiki page: `goldenrodcity-departmentstore-7fnight-hns.html`; map `GoldenrodCity_DepartmentStore_7FNight_hns` (`MAP_GOLDENROD_CITY_DEPARTMENT_STORE_7FNIGHT_HNS`); scripts `data/maps/GoldenrodCity_DepartmentStore_7FNight_hns/scripts.inc` (`PoxGoldenrod_GoldenrodCity_DepartmentStore_7FNight_hns_0`–`3`)
- Known gaps: no inbound warp anywhere in the checkout; no `LOCALID_*` on this map's objects; warp target (6F, warp 2) shared with the day map; nothing references the four texts.

## Open questions
- Keep or retire? Recommendation: one map, one set of four voices. If the day roof takes the light-counting line, retire this map and its layout; if night is wanted, branch the 6F stair on `GetTimeOfDay` and delete the duplicate geometry instead of maintaining two copies.
- If wired, should the roof be night-only, or should both maps exist behind a time check? A time branch is cheap; two hand-maintained copies with one local id missing is not.
