---
title: Route 19
slug: route19-frlg
kind: Route
act: 4
stage: "10 — Saffron hub"
depth: supporting
wiki: route19-frlg
maps: [Route19_Frlg]
flags: [FLAG_POX_STORY_SPACE_CENTER, FLAG_POX_TRIGGERS_ENABLED]
trainers: [TRAINER_SWIMMER_MALE_REECE, TRAINER_SWIMMER_MALE_RICHARD, TRAINER_SWIMMER_MALE_TONY, TRAINER_SWIMMER_MALE_MATTHEW, TRAINER_SWIMMER_MALE_DOUGLAS, TRAINER_SWIMMER_MALE_DAVID, TRAINER_SWIMMER_MALE_AXLE, TRAINER_SWIMMER_FEMALE_ALICE, TRAINER_SWIMMER_FEMALE_CONNIE, TRAINER_SWIMMER_FEMALE_ANYA, TRAINER_SIS_AND_BRO_LIA_LUC]
status: drafted
---

# Route 19

## Snapshot

Open water between the southern gate of `SaffronCity_hns` and the Mossdeep approach, crossed by Surf with two marked passages and eleven people already in the sea. It sits inside stage 10: nothing is won here, and the route exists to turn Saffron from a sealed centre into a harbour. The emotional note is a road with no traffic — the water is busy because it is the only road left, and every swimmer is talking to themselves.

## Plot points

1. **The Saffron passage.** At `(12,0)` `PoxRegion_route19_saffron_a` warps to `SaffronCity_hns` `(31,44)` only after `FLAG_POX_STORY_SPACE_CENTER`; before it, the closed text plays and the player is put back at `(11,0)`. Reveal-ladder step 12 is exactly what unlocks it, so the gate must read as a queue and a shift change, not a locked door with a label.
2. **The Mossdeep passage.** At `(12,13)` `PoxRegion_mossdeep_route19_b` warps to `MossdeepCity` `(39,0)` and checks **no story flag**, only the `FLAG_POX_TRIGGERS_ENABLED` build bypass — thirteen tiles from the Saffron edge. That is the map's one real problem: the geography promises a Gym 6 approach to anyone who reaches the water.
3. **Eleven parties, zero battles, vanilla water.** Every swimmer object carries no trainer type and every live `Route19_EventScript_*` wrapper in `data/scripts/plastic_ox_region.inc` is a plain `msgbox` of the post-battle line; the battle bodies in `data/scripts/trainers_frlg.inc` sit behind `.if IS_FRLG` and never compile. Surf is Tentacool only at Lv. 5–40, fishing Lv. 5–35 with Gyarados, Horsea, Krabby, Magikarp and Psyduck. Decide combat and the tables before writing dialogue.

**Must not:** name Bill, Silph, or the adaptive system; let a swimmer explain the convergence or why Saffron was shut; open Saffron before the Space Center; stage a fourth Rocket appearance; put a current puzzle or rock maze in the water; give a swimmer a system-style objective line.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Saffron passage | `(12,0)` | `FLAG_POX_STORY_SPACE_CENTER` | open: warp to `SaffronCity_hns` `(31,44)`; closed: `PoxRegion_ClosedText`, bounce to `(11,0)` | keep both states; give the closed one a person |
| Mossdeep passage | `(12,13)` | always, except the `FLAG_POX_TRIGGERS_ENABLED` bypass | warp to `MossdeepCity` `(39,0)` | add the missing gate; the sea must not be the Gym 6 shortcut |
| Both signs | `(11,1)`, `(11,12)` | always | two generated "City / Marked passage ahead." strings | distance, crossing time, what waits at the gate; two different voices |
| Six men in the water | `(15,10)` Reece, `(10,9)` Richard, `(12,17)` Tony, `(18,33)` Matthew, `(8,27)` Douglas, `(16,22)` David | always | post-battle lines only; no battle starts | restore the Lv. 27–30 parties, or give them jobs on the shingle |
| South cluster | `(11,47)` Axle, `(14,48)` Alice, `(12,49)` Connie, `(9,48)` Anya, `(8,41)` Lia, `(9,41)` Luc | always | msgbox only; Axle's cramp and Anya's longing for Fuchsia are the best writing here, and `TRAINER_SIS_AND_BRO_LIA_LUC` (Goldeen, Seaking, Lv. 30) exists without a double battle to hold it | keep the voices, move the geography — Seafoam and Fuchsia are no longer this route's neighbours |

## Dialogue guidance

- **Who speaks:** swimmers, two of them children, one man who is not all right, and whoever is on the shingle checking a watch. They know crossing times, water temperature, the current at the point, which side the wind comes from — not why the city was shut. One voice each: Tony is grieving and never comic relief, Axle is frightened and never a cramp joke, Connie's Lapras wish is six years old and patient, the children talk past the player.
- **Register and state:** outdoor voices over water — short sentences called across distance, then one long one when the player is close enough to be spoken to; numbers do the work (minutes, metres, degrees, strokes). Before the Space Center the north end is closed water and people talk about waiting it out; after, they talk about the crossing they just made and the queue behind the gate. Nobody explains the change.

> RICHARD: Twenty minutes in, my arms stop arguing. That is when the swim gets good.

> CONNIE: A LAPRAS would keep my hair dry. I have thought about it for six years, and I am still thinking.

> TONY: I count strokes. Somewhere past four hundred I stop thinking about the thing I came out here to stop thinking about.

> AXLE: Cramp — both legs. If you are going that way, go slower than you think you need to.

- **Do not:** say "convergence", "sealed", or "the system"; let a swimmer explain the Space Center; reuse Route 8's gate-waiter grievance; make the sea mysterious or haunted; write a trainer taunt for a battle that does not exist.

## Inspiration

- **English Channel crossings and a Japanese prefectural beach in late summer.** Pilots, grease, feeding on a rope, a tide window; then net menders, a concrete breakwater, children with buckets, a radio playing baseball. The first gives the swimmer who times her crossings and the tin of grease in her bag; the second gives the land pair, and Lia and Luc, the only people here on holiday.
- **Seto Inland Sea ferries and winter swimming clubs.** A short hop, a timetable taped to a post, a service that quietly stopped; then the same dozen people every morning and a thermometer on a nail. The ferry board is the right model for "marked passage" and the fix for both sign texts; the club explains why the south cluster know each other.

## Implementation hooks

- Wiki page `route19-frlg.html`; map `Route19_Frlg` (`MAP_ROUTE19`, layout `LAYOUT_ROUTE19_HNS`, region Hoenn, vanilla `MAPSEC_ROUTE_19`); neighbours `MossdeepCity`, `SaffronCity_hns`, and the donor-connected `FuchsiaCity_Frlg` and `Route20_Frlg`.
- Scripts: `data/maps/Route19_Frlg/scripts.inc` holds only the text and `Route19_EventScript_RouteSign`; live wrappers in `data/scripts/plastic_ox_region.inc`; dead battle bodies in `data/scripts/trainers_frlg.inc` behind `.if IS_FRLG`; both passages and the empty `PoxRegion_Arrival_Route19_Frlg` stub in the region file.
- Gates: `FLAG_POX_STORY_SPACE_CENTER` on the Saffron passage only; `FLAG_POX_TRIGGERS_ENABLED` short-circuits every portal script; `VAR_POX_PORTAL_TRIGGER` is the coord-event var on both triggers and is zero, so both fire on contact.
- Known gaps: the map declares 0 warps and 0 connections while `FuchsiaCity_Frlg` (down, offset 12) and `Route20_Frlg` (right, offset -40) both declare one-way drops into it, so any Kanto-side access would be one-way in; the Mossdeep passage has no story gate at all, which makes the sea a Gym 6 approach for anything that reaches it; all eleven parties are unattached; each passage's `_Closed` branch is unreachable; a Hoenn region header sits on a Kanto sea map.

## Open questions

- Restore the eleven swimmer battles at act-4 levels, or keep the crossing quiet and make them residents? The parties exist, so silence is currently the bug.
- Cut the donor `FuchsiaCity_Frlg` / `Route20_Frlg` drops, or keep them and gate the Mossdeep passage with the Space Center flag? Either closes the shortcut; only the second keeps the old Kanto shore walkable if the Cycling Road gate is ever fixed. Fuchsia and the Cycling Road chain still have no note of their own.
- Does a full crossing earn something — a held item on the far shingle, one hidden find — or is the view of the Saffron gate the reward?
