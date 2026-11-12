# F3 — progression gates report

## Files changed

- `data/scripts/plastic_ox_region.inc`
  - `PoxRegion_rustboro_route44_a` / `_b`: added `goto_if_unset FLAG_BADGE01_GET, …_Closed` between the demo bypass and `_Open`. Both `_Closed` arms are now live and refuse with a warp back to the tile the player came from (`_a` → Rustboro `(38,10)`, `_b` → Route44 `(1,15)`). New refusal text `PoxRegion_Route44BadgeText`.
  - `PoxRegion_Arrival_FortreeCity`: removed `setflag FLAG_HIDE_FORTREE_CITY_KECLEON` and `setflag FLAG_KECLEON_FLED_FORTREE`; it now only sets `FLAG_POX_REACHED_FORTREE` under `FLAG_POX_STORY_WEATHER` (demo bypass kept).
- `data/maps/Route44_hns/map.json`: gate hiker moved from `(68,13)` to `(69,13)` (adjacent, walkable, beside the cave mouth; no longer on the warp/trigger tile).
- `data/maps/Route44_hns/scripts.inc`: `PoxMoon_EnterFromRoute44` now checks `FLAG_BADGE01_GET` before warping. With the badge → Mt. Moon `(18,37)` as before. Without → short hiker line, then `warp` back to `(68,14)` (the tile in front of the mouth), so the tile is not a dead end.
- `data/maps/BlackthornCity_hns/map.json`: doorman moved `(16,28)` → `(15,28)` (keeps `Pox_ClairGuide`); new warp **index 2** at `(16,28)` → `MAP_PLASTIC_OX_CLAIR_GYM` warp 0; new coord trigger at `(16,28)` → `BlackthornCity_EventScript_GymDoor`.
- `data/maps/BlackthornCity_hns/scripts.inc`: new `BlackthornCity_EventScript_GymDoor` (`warp MAP_PLASTIC_OX_CLAIR_GYM, 5, 18`).
- `data/maps/PlasticOx_ClairGym/map.json`: warps **0** at `(5,19)` and **1** at `(6,19)` (the two `MB_SOUTH_ARROW_WARP` exit tiles) → `MAP_BLACKTHORN_CITY_HNS` warp 2. Reciprocal with the city door.
- `data/maps/PlasticOx_VictoryRoad/map.json`: `PoxLeague_Return` band moved from `y=49` to `y=50` (all four triggers, x 25–28).
- `data/maps/Gate_EcruteakCity_Route38_hns/map.json`: new warp **index 1** at `(1,5)` (the `MB_WEST_ARROW_WARP` door) → `MAP_ROUTE38_HNS` warp 0. `Route38_hns` warp 0 now resolves.

## Gate logic

- Route 44 seam: triggers enabled + no Stone Badge → closed (message + bounce). Badge → open. Demo build (triggers disabled) → open.
- Mt. Moon mouth: `(68,13)` is walkable and holds only the coord trigger (badge predicate) and warp 0 (the landing anchor for `MtMoon_1F` warp 3); the hiker no longer occupies it. Badge held → warp to Mt. Moon. No badge → bounced to `(68,14)`.
- Blackthorn Gym: `(16,28)` is `MB_NORMAL` in the imported layout, so a bare warp event cannot fire there; the tile trigger is the door and warp 2 is the return anchor. The Gym's arrow-warp exit (`(5,19)`/`(6,19)`) lands on warp 2. `Pox_ClairGuide` is untouched and still holds the `FLAG_POX_STORY_SPACE_CENTER` condition; the town's own arrivals (`PoxRegion_meteor_blackthorn_b`, `PoxRegion_blackthorn_route45_b`) still enforce the same flag, and no new flag was added.
- Victory Road: arrival `(27,48)` → `(27,49)` is now safe; the eject band is `y=50`, the southernmost row (layout is 39×51, y=0–50, so a two-tile move is out of bounds). The `(28,47)` trail sign still names the south checkpoint.
- Gatehouse: `(1,5)` ↔ Route38 `(43,16)` is reciprocal; the League checkpoint band inside the gate is unchanged.

## Static checks

- `python3 -m json.tool` on all six map.json files: OK.
- `python3 plastic_ox/agent/check_map_refs.py --map …(six maps)`: 0 errors.
- `python3 plastic_ox/agent/check_map_refs.py --pox`: 118 maps, 0 errors (the Route 38 gate error is gone).
- `python3 plastic_ox/story/check_story_notes.py --quiet`: 61 notes, 0 errors/0 warnings.
- `audit_map_baseline.py` on all five touched map dirs: only the expected intentional triggers; nothing stripped. `audit_warp_connections.py`: 0 bad indices, 0 missing targets; new links reciprocal.

## Emulator tests for the integration pass

1. Rustboro east `(39,9–11)` with badge 1 **unset** → message, lands Rustboro `(38,10)`; with badge 1 **set** → Route44 `(1,15)`.
2. Route44: set badge 1, warp to `(65,13)`, walk east to `(67,13)`, step right/east onto `(68,13)` → Mt. Moon `(18,37)`. Clear badge 1 (debug), repeat → refusal, lands `(68,14)`, hiker visible at `(69,13)`.
3. Blackthorn `(16,29)` walk north onto `(16,28)` → `PlasticOx_ClairGym` `(5,18)`; walk down onto `(5,19)` → Blackthorn `(16,28)`, then one step south; confirm no re-entry loop.
4. Victory Road: warp to `(27,48)`, step south once → still on the map at `(27,49)`; step south again → Gate `(5,5)`.
5. Gate/R38: Gate `(1,5)` press west → Route38 `(43,16)`; Route38 `(43,16)` press east → Gate `(1,5)`.
6. Fortree: arriving from Route119 with the Weather flag sets `FLAG_POX_REACHED_FORTREE` and leaves `FLAG_KECLEON_FLED_FORTREE` clear (Kecleon visible on the east walkway until the badge-4 interaction).

## Could not do / risks

- The Victory Road band could not move two tiles south: the layout ends at `y=50`. It now sits on the last row, which gives exactly one safe step south from the landing — the stated requirement ("stepping south once does not eject").
- The Gym door needed a tile trigger because `(16,28)` has `MB_NORMAL` behaviour; making a real door warp would require editing `data/layouts/BlackthornCity_hns/map.bin` or the tileset attributes, which is outside F3's file list.
- Tests that encode the old behaviour and need fixture/assert updates by the integration pass (none edited here):
  - `plastic_ox/demo/test_route44_transitions.py` — walks Rustboro → Route44 with no badge (lines 70–80) and the whole out-and-back before setting badge 1; needs `FLAG_BADGE01_GET` set at the start.
  - `plastic_ox/demo/test_region_walk.py` — the `early` leg includes `rustboro_route44_a`; same fixture fix.
  - `plastic_ox/demo/test_mt_moon.py` — warps to `(67,13)` and steps east onto `(68,13)` without badge 1; needs the badge set (or it will exercise the new refusal, landing at `(68,14)`).
  - `plastic_ox/demo/test_ecruteak_repairs.py` (and `test_league.py` `travel()`) — assert that one step south from Victory Road `(27,48)` ejects the player; that assertion is the bug F3 removes, so it must become "one step is safe; the second reaches the band".
