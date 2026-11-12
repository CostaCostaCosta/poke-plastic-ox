---
title: Goldenrod City Department Store 7F
slug: goldenrodcity-departmentstore-7f-hns
kind: City
act: 1
stage: "3 — Goldenrod"
depth: supporting
wiki: goldenrodcity-departmentstore-7f-hns
maps: [GoldenrodCity_DepartmentStore_7F_hns]
status: drafted
---

# Goldenrod City Department Store 7F

## Snapshot
The store's roof terrace, reached by one stair from 6F: a railed deck, four people, no shop, no item, nothing to trigger. It exists so the player can stand above Goldenrod and see the city at once, station and empty tracks included — a view, not a beat.

## Plot points
1. **The city from above.** Warp `(22,5)` returns to the 6F stair; the roof is a dead end by design. **Empty tracks, infrastructure only:** the nerd at `(22,11)` says the station looks tiny and the empty tracks look longer — the correct dose, because the player may notice later that Saffron is sealed. Nobody may explain the line, the seal, or who built it.
2. **Four fixed voices, no state.** Every script is one `MSGBOX_NPC` with no flag check. Fine for a supporting map, but one line should change after badge 2 so the city feels like it moved on.

**Must not:** mention Silph, the Space Center, Saffron's seal, Bill, or the convergence; put an item, trainer or shop on the roof; let the nerd's line become an explanation.

## Key interactions
| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Rooftop nerd | `(22,11)`, `PoxGoldenrod_GoldenrodCity_DepartmentStore_7F_hns_0` | always | "the station looks tiny, the empty tracks look longer" | keep; the only line on the roof carrying weight |
| Quiet woman / park watcher / bug catcher | `(19,8)`, `(11,6)`, `(12,10)`, `..._7F_hns_1`–`3` | always | quiet, ginkgoes turning gold, a bug that likes wind | keep all three; give the woman the badge-2 variant so the terrace has a second reading |

## Dialogue guidance
- **Nerd:** the city as a model whose flaws he can see — stations, tracks, wind off the hills. Observant, not a researcher. **Quiet woman:** on a break, mildly annoyed to be spoken to. **Park watcher:** brings a snack, stays an hour, measures the year by which trees turn first. **Bug catcher:** a child with a leash-like grip and a lost-Butterfree story he will not repeat.
- Register: indoor-city voices, softer than street level, because everyone is above the traffic.

> ROOFTOP NERD: Four tracks and nothing on any of them. I've counted since spring.

> QUIET WOMAN: If you're going to talk, talk quietly. That's the entire fee for standing here.

> PARK WATCHER: The ginkgoes at the west gate go first. Then the park. Then everything at once, and the city smells like a bonfire.

**Do not:** explain the empty tracks, name a destination, or offer a service. Do not reuse the park watcher's line in the night variant.

## Inspiration
- **Japanese department-store rooftops:** a planted deck, vending machines, families, rail lines below — Nihonbashi and Ikebukuro both do this. Hence a floor with no shop that still reads as commercial.

## Implementation hooks
- Wiki page: `goldenrodcity-departmentstore-7f-hns.html`; map `GoldenrodCity_DepartmentStore_7F_hns` (`MAP_GOLDENROD_CITY_DEPARTMENT_STORE_7F_HNS`), stair `MAP_GOLDENROD_CITY_DEPARTMENT_STORE_6F_HNS`; scripts `data/maps/GoldenrodCity_DepartmentStore_7F_hns/scripts.inc` (`PoxGoldenrod_GoldenrodCity_DepartmentStore_7F_hns_0`–`3`). Known gaps: no state, items or events; a complete night twin (`GoldenrodCity_DepartmentStore_7FNight_hns`) exists but nothing warps to it; the four lines never change.

## Open questions
- Should one line check badge 2 so the terrace acknowledges progress, or is a wholly static retreat the point? Recommendation: one line, the quiet woman's.
- Keep the roof shop-free, or add a vending machine as convenience? It is the only floor of the store with nothing on it.
