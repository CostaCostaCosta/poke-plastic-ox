# F5 — Goldenrod Gym room, SquirtBottle, Game Corner, herb/guard

Final state after verifying and finishing the partial pass. No build or mGBA was
run (per brief); everything below is static verification of `map.json`,
`scripts.inc`, generated `events.inc`, layout blockdata and the engine's
warp/object code.

## Files changed (final)

**`data/maps/GoldenrodCity_hns/map.json`** — Gym door warp `(39,13)` now targets
`MAP_PLASTIC_OX_WHITNEY_GYM` warp `0` (was `MAP_GOLDENROD_CITY_GYM_HNS`). Street
object `(27,15)` (WOMAN_2) now runs `PoxGoldenrod_SquirtBottleNote`, not
`Pox_SquirtBottle`.

**`data/maps/PlasticOx_WhitneyGym/map.json`** — two return warps at `(5,19)` and
`(6,19)`, both `MAP_GOLDENROD_CITY_HNS` warp `5`; Whitney `(5,2)` uses
`OBJ_EVENT_GFX_WHITNEY_HNS` with visibility `0`; dead exit NPC `(4,17)` removed.
Layout is `LAYOUT_RUSTBORO_CITY_GYM` (11×20).

**`data/maps/GoldenrodCity_GameCorner_hns/map.json` / `scripts.inc`** — coin
clerk `(3,2)` runs local `PoxGoldenrod_CoinClerk`; prize desk `(16,2)` keeps the
single `POX_PU_CoinPrizes`; the old second desk `(18,2)` is now
`PoxGoldenrod_PrizeHost` (local flavour NPC). All new text is local and unique.

**`data/maps/GoldenrodCity_UndergroundTunnel_hns/map.json` / `scripts.inc`** —
herb clerk `(6,24)` runs local `PoxGoldenrod_HerbClerk` with a four-item herb
stock; Kimono guard moved `(12,11)` → `(13,11)`, facing left, and rewritten to
describe the open stair and sealed inner chamber. One wording fix in this pass:
`"The room beyond that is sealed."` → `"The inner chamber stays sealed."` so the
line does not claim the reachable Storage corridor is sealed.

**`data/maps/GoldenrodCity_FlowerShop_hns/map.json` / `scripts.inc`** — no edit
needed; verified only.

**`data/scripts/plastic_ox_goldenrod.inc`** — added
`PoxGoldenrod_SquirtBottleNote` + its text (points at the Flower Shop counter).

## Verified state

### Gym transition (both ways)
- Goldenrod warp index `5` is exactly `(39,13)`, metatile `347`,
  `MB_ANIMATED_DOOR` (0x69), collision 1, elevation 0. The player stands at
  `(39,14)` (walkable, elevation 3) and presses up; `TryDoorWarp` reads the
  in-front door and warps, matching how every other Goldenrod door works.
- Destination: `PlasticOx_WhitneyGym` warp `0` `(5,19)` — Rustboro Gym door
  metatiles `6/7`, `MB_SOUTH_ARROW_WARP` (0x65), **collision 0**, elevation 3.
  Warp elevation is `0` = `ELEVATION_TRANSITION`, so it matches the floor
  elevation. Arrow warps only fire while a step/direction is held, and arrival
  (via `Task_ExitNonDoor`) does not step, so there is no immediate bounce; the
  player walks north into the room.
- Room exit: walking south onto `(5,19)` or `(6,19)` warps to city warp `5`;
  arrival is the animated gym door, and `Task_ExitDoor` walks the player out to
  walkable `(39,14)`. Statically this is the vanilla Rustboro Gym door pair.
- Legacy `GoldenrodCity_Gym_hns` has **no inbound warp anywhere** (grep of all
  `map.json`/`scripts.inc` for `MAP_GOLDENROD_CITY_GYM_HNS` outside its own
  directory returns nothing), so the legacy room is unreachable; its warp table
  and its second `Pox_Whitney` are untouched but dead.
- `Pox_Whitney` at `(5,2)` is reachable from `(5,3)` and sets
  `FLAG_BADGE02_GET` once (early-out when the flag is set), so badge 2 is
  awarded exactly once in the reachable room.

### SquirtBottle
- Exactly one object references `Pox_SquirtBottle`:
  `GoldenrodCity_FlowerShop_hns` `(2,4)`, flag 0, `FLAG_BADGE02_GET` gate and
  `ITEM_SQUIRT_BOTTLE` give intact.
- `GoldenrodCity_hns` `(27,15)` runs `PoxGoldenrod_SquirtBottleNote`
  (MSGBOX_NPC) and gives/no-ops nothing.
- All 42 objects across the five maps have 42 distinct scripts; no duplicate
  script assignment. String scan of the five maps' scripts: 0 exact duplicate
  strings. The new note text is unique in `data/`.

### Game Corner
- One coin clerk: `(3,2)`, local `PoxGoldenrod_CoinClerk`; prices unchanged
  (¥1,000 = 50 coins, ¥10,000 = 500 coins), `MULTI_GAME_CORNER_COINS` list is
  50/500/Exit, cap `MAX_COINS` 9999; case-less, no-money, cancel, full-case
  branches all defined.
- One prize desk: `(16,2)` `POX_PU_CoinPrizes` (four offers; special
  `PlasticOxBuyCoinPrize` implemented: ABRA 200, LUVDISC 500, CASTFORM 1,500,
  PORYGON 4,000, Lv. 15).
- One host: `(18,2)` `PoxGoldenrod_PrizeHost`, local unique text, no prize menu.
- No donor script labels: `MauvilleCity_GameCorner_EventScript_CoinsClerk` and
  `LavaridgeTown_HerbShop_EventScript_Clerk` appear nowhere in either map; the
  only remaining donor mentions are explanatory comments.
- Caveat: the host stands at the second counter window `(18,2)` (counter
  `(18,3)` is `MB_COUNTER`), not out on the open floor. Functionally he is
  talkable from `(18,4)`; if the intent is a roaming floor host, move him to
  walkable `(18,4)`.

### Herb clerk
- `(6,24)` local `PoxGoldenrod_HerbClerk`; `pokemart PoxGoldenrod_HerbStock`
  with `ITEM_ENERGY_POWDER`, `ITEM_ENERGY_ROOT`, `ITEM_HEAL_POWDER`,
  `ITEM_REVIVAL_HERB` — all defined (`include/constants/items.h:53–57`), same
  four items as the vanilla herb counter. Documented choice: real inventory,
  not a flavour NPC.

### Underground guard / stair
- Stair `(12,10)` is warp 2 to `GoldenrodCity_UndergroundSwitches_hns` warp 1;
  tile collision 0, elevation 0; warp elevation 0 (transition). It is open.
- Guard `(13,11)` no longer stands on the approach tile `(12,11)`, so the stair
  is reachable. She is visible: `FLAG_POX_KIMONO_GATE_OPEN` is a hide-when-set
  object flag, is unset at save start and nothing writes it (only the reserved
  id and the two object entries reference it).
- Text now: stair open; switch chamber just past it; inner chamber stays
  sealed. No flag or item was invented and the stair was not gated.
- Reality caveat: in the current maps the stairs lead Tunnel → Switches →
  Storage → Department Store basement, all reachable (flood-fill: 294/294
  switches tiles, 162/162 tunnel tiles reachable). The "sealed inner chamber"
  is the out-of-scope Registeel promise, not a door in these maps.

## Static checks

- `python3 -m json.tool` on all five `map.json`: OK.
- `check_map_refs.py --map GoldenrodCity_hns --map PlasticOx_WhitneyGym --map
  GoldenrodCity_GameCorner_hns --map GoldenrodCity_UndergroundTunnel_hns --map
  GoldenrodCity_FlowerShop_hns`: **5 maps, 0 errors**.
- `check_map_refs.py --pox`: 118 maps, 0 errors.
- `check_story_notes.py --quiet`: 61 notes, 0 errors/warnings.
- `audit_map_baseline.py` all five: only the intentional city `(32–35,45)`
  portal triggers and the tunnel haircut ON_TRANSITION; no warps/objects
  stripped.
- Generated `events.inc` already matches the edited `map.json` (gitignored;
  build regenerates it with `make generated`).

## Emulator tests for the integration pass

1. Goldenrod `(39,14)` face up + press up at the Gym door `(39,13)` → fade into
   `PlasticOx_WhitneyGym`, spawn `(5,19)`, no second warp, walk up to `(5,18)`.
2. Room: walk south onto `(5,19)` → Goldenrod `(39,13)` then door-exit to
   `(39,14)`; repeat via `(6,19)`. Confirm no bounce/re-entry.
3. Whitney (badge 1 + Mt. Moon set, badge 2 clear) → battle; win once → badge 2
   flag; talk again → no battle, no second badge. Confirm no path reaches the
   legacy Gym room.
4. Flower Shop `(2,4)` before badge 2 → refusal; after badge 2 with no bottle →
   receives `ITEM_SQUIRT_BOTTLE`; with bottle → reminder only, no second item.
   Street `(27,15)` → note text only, no item.
5. Game Corner `(3,2)`: no case → hint; with case, ¥1,000 → +50, ¥10,000 →
   +500; Exit hides money/coin boxes; 9,950+ coins → case-full line.
6. Prize desk `(16,2)` with case: each of the four offers deducts the right
   coins and gives the Lv. 15 mon; without case → need-case line. Host
   `(18,2)` gives dialogue only.
7. Tunnel `(6,24)`: mart opens with the four herbs; purchase and exit work.
8. Tunnel guard `(13,11)` is visible and talkable; stair `(12,10)` warps to
   Switches; no new flag/item state changes.

## Not done / follow-ups

- Legacy `GoldenrodCity_Gym_hns` still holds the five gym-floor voices and its
  own `Pox_Whitney`; they are now stranded content. Moving them into the
  Rustboro-layout room needs new coordinates and is a design follow-up, not
  part of the unreachable fix.
- `GoldenrodCity_UndergroundStorage_hns` guard `(3,11)` is still visible on the
  same reserved flag and stands **on** the Storage→Switches warp tile, while
  saying "the old switch chamber is closed for now". That map is outside F5's
  files, so the contradiction with the Tunnel guard (and the blocked return
  warp) is reported, not fixed. A switches→storage arrival lands on her tile.
- Alpha reapply sources are stale: `plastic_ox/alpha/goldenrod/city_doors.json`
  still sends the Gym door to `MAP_GOLDENROD_CITY_GYM_HNS`, and the alpha map
  JSONs still place the Mauville coin clerk, the Lavaridge herb clerk and the
  guard at `(12,11)`. `plastic_ox/alpha/goldenrod.py` is not part of `make`, so
  the ROM build is unaffected, but rerunning that import script would revert
  this pass. Not edited (outside F5's file list).
- `Pox_WhitneyGymExit` and `PlasticOx_WhitneyGym_EventScript_Greeter` are now
  unused labels (harmless, no objects reference them).
- The Game Corner host position caveat above.
- No build/mGBA run: emulator results are pending the integration pass.
