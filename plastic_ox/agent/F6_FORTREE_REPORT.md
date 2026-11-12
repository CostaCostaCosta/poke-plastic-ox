# F6 — Fortree east Kecleon + Route 110 cleanup

## Files changed

**`data/maps/FortreeCity/map.json`** — Kecleon `(25,8)` → `(38,10)`, stationary `MOVEMENT_TYPE_INVISIBLE`, visibility `FLAG_KECLEON_FLED_FORTREE` (was no-op `FLAG_POX_HIDE_UNUSED_ACTOR`). GABBY `(38,10)` → `(36,9)` FACE_RIGHT; TY `(37,9)` now FACE_LEFT. Edge sign object `(38,9)` → `(39,9)` with a local script; west edge sign rewired locally. Removed the duplicate bg-sign events (each sign was placed twice). Warps, coord events and the Gym warp `(22,11)` untouched.

**`data/maps/FortreeCity/scripts.inc`** — Kecleon refuses while badge 4 is unset; with badge 4 it reveals, sets `FLAG_KECLEON_FLED_FORTREE`, removes itself. Devon Scope branch deleted. Woman has one Gym-queue line, no Gym-blocked branch. Reporters rewritten as two voices; west/east signs no longer say "Marked passage ahead".

**`data/maps/Route110/map.json`** — Deleted the two stacked `script 0x0` rival objects at `(34,54)` and the invisible `script 0x0` grunt at `(8,82)`. Four Aqua objects retyped as ordinary hauliers (`flag 0`, `Hauler1–4`). Birch `(9,79)` repurposed as a SCIENTIST route researcher with a real script (`LOCALID_ROUTE110_RESEARCHER`); the two cycling-road gate signs split into distinct signs.

**`data/maps/Route110/scripts.inc`** — Deleted the dead rival battle/Dowsing-Machine scene and dead Birch scene. Recast the hauliers, RYDEL cyclist, both boys, old woman and challenge-steward lines; sign text de-Hoennised. No trainer parties or levels changed.

## Chokepoint geometry

`(39,10)` can only be entered from `(38,10)` or `(39,9)`; `(39,11)` and `(35–39,11)` are solid and x=40 is off-map. Kecleon sits on `(38,10)`, directly before the gate; the sign object moved to `(39,9)` closes the north lane. Static BFS on `map.bin` collision shows `(39,10)` unreachable while the Kecleon exists, reachable once removed. Reporters moved to `(36,9)/(37,9)` so the row-10 road stays open and both are talkable before badge 4.

Caveat: `(38,10)` is also Route 110's return-warp landing (`PoxRegion_fortree_route110_b_Open`, in `plastic_ox_region.inc`, not F6-owned). Any legitimate eastbound departure fled the Kecleon, so returns land free; if the integration pass can reach Route 110 without fleeing, check that one-tile overlap.

## Static checks

- `python3 -m json.tool` both maps: OK.
- `check_map_refs.py --map FortreeCity --map Route110`: 0 errors.
- `check_map_refs.py --pox`: only the pre-existing Route 38 gate error; neither map reports.
- `check_story_notes.py --quiet`: 61 notes, 0 errors/warnings.
- `audit_map_baseline.py` both: all intentional triggers still listed (Fortree `(0,10)/(39,10)`; Route 110 `(18,0)/(1,67)/(16,5)`). Its exit 1 is "found intentional triggers", not a failure.
- Duplicate-string scan: none; no stacked or scriptless objects remain.

## Emulator tests

1. Fortree, no badge 4, fled flag unset: interact at `(38,10)` → refusal, no battle/item; `(39,9)` blocked by the sign; gate does not fire.
2. Badge 4, fled flag unset: interact → reveal + cry, object removed, flag set; `(38,10)` → `(39,10)` warps to Route 110 `(17,0)`.
3. Re-enter Fortree from Route 110's north gate: arrive `(38,10)`, Kecleon stays gone.
4. Both states: Gym warp `(22,11)` reachable; woman mentions only the queue.
5. Route 110: no stack at `(34,54)`, no invisible body at `(8,82)`; hauliers/researcher speak; the two cycling-road gates read differently.

## Not done

- "Jasmine": fixed only at object/script level. The displayed name is `Name: JASMINE` in `src/data/trainers.party` and her battle lines are in `data/text/trainers.inc`, both outside F6 — the party owner must rename her.
- Trainer levels (Lv.6–16) left as the briefed follow-up.
- Route 110 still warps to `MAP_NEW_MAUVILLE_ENTRANCE` and `MAP_ROUTE110_TRICK_HOUSE_ENTRANCE`; the latter's sign now reads "THE OLD SHED", making its interior a retirement/repurpose candidate. No map retired.
- `PoxRegion_Arrival_FortreeCity` still sets both Kecleon flags in `plastic_ox_region.inc`; the Kecleon stays hidden until the other agent removes them.
