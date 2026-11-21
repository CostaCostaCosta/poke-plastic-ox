# Route 36 Sudowoodo × SquirtBottle — end-to-end playtest (run 4)

**Build:** `04b27389ca` (`codex/metamon-trainer-ai`), `pokeemerald.gba` used read-only.
**Harness:** `plastic_ox/demo/test_sudowoodo_v1.py` (reusable; `~/.venvs/mgba311/bin/python
plastic_ox/demo/test_sudowoodo_v1.py [1..10]`, ~16 s for all ten scenarios).
**Machine-readable results:** `plastic_ox/demo/sudowoodo_results.json`.
**Mode:** playtest only — no game data, map, script or code was modified; nothing was compiled.
Only emulator RAM was written (flags/badges/party/bag for fixture setup). Screenshots:
`plastic_ox/demo/shots/sudowoodo_{battle,cleared,caught}.png`.

**Result: 11 of 12 checks pass. One reproducible gameplay defect (the "No" answer on the
SquirtBottle prompt cannot be chosen), plus four design/robustness observations.**

---

## 1. Static wiring trace

### 1.1 The SquirtBottle gift

| Item | Value |
|---|---|
| Script | `Pox_SquirtBottle` — `data/scripts/plastic_ox_story.inc:2110-2134` |
| Emitter | `plastic_ox/alpha/build_story.py:707-719` (generated file — edit the manifest, not the `.inc`) |
| NPC A (interior, canonical) | `GoldenrodCity_FlowerShop_hns` (2,4) `OBJ_EVENT_GFX_GIRL_1`, `data/maps/GoldenrodCity_FlowerShop_hns/map.json:16-29` |
| NPC B (outdoor duplicate) | `GoldenrodCity_hns` (27,15) elev 3 `OBJ_EVENT_GFX_WOMAN_2`, `data/maps/GoldenrodCity_hns/map.json:265-279` |
| Manifest entry | only NPC B is in `plastic_ox/alpha/story_manifest.json:565` (the interior one is not) |
| Gate | `goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End` → `lockall` → `goto_if_unset FLAG_BADGE02_GET, Pox_SquirtBottle_Wait` → `checkitem ITEM_SQUIRT_BOTTLE` → `goto_if_eq VAR_RESULT, TRUE, Pox_SquirtBottle_Have` → `giveitem ITEM_SQUIRT_BOTTLE` |
| Item | `ITEM_SQUIRT_BOTTLE = 882` (`include/constants/items.h:1062`), `src/data/items.h:14181-14195` |
| Flags | `FLAG_BADGE02_GET = 0x868` (`include/constants/flags.h:1370`), `FLAG_POX_TRIGGERS_ENABLED = POX_FLAGS_START+6 = 0x26A` (`include/constants/plastic_ox_flags.h:35`), `POX_FLAGS_START = 0x264` |

`FLAG_POX_TRIGGERS_ENABLED` is set once at new-game (`src/new_game.c:274`, non-`PLASTIC_OX_BUILD_BATTLE`)
and read in 101 story scripts — it is a master kill-switch, not a dead flag.

### 1.2 The Route 36 Sudowoodo

| Item | Value |
|---|---|
| Map | `Route36_hns`, 81×44 layout, **no warps**, one connection (up → `Route37_hns`, offset 22) |
| Object | `data/maps/Route36_hns/map.json:102-114` — `OBJ_EVENT_GFX_SUDOWOODO` at (39,20) **elevation 3**, `script: Pox_Sudowoodo`, `flag: FLAG_POX_SUDOWOODO_CLEARED` |
| Script | `data/scripts/plastic_ox_story.inc:2136-2168` |
| Persistence flag | `FLAG_POX_SUDOWOODO_CLEARED = 0x1AB` (`include/constants/plastic_ox_flags.h:168`) — used **twice**: as the object-event visibility flag *and* as the script's early-out; the script additionally calls `removeobject VAR_LAST_TALKED` |
| Encounter | `setwildbattle SPECIES_SUDOWOODO(185), 20, ITEM_NONE` → `special PlasticOx_PrepareSudowoodoMoves` → `dowildbattle` |
| Moves | `src/wild_encounter.c:663-669` — `SetMonMoveSlot` overrides slots 0-3 with Rock Throw(88), Mimic(102), Flail(175), Low Kick(67) **after** `setwildbattle` has already created the mon in `gParties[B_TRAINER_OPPONENT_A][0]` (`src/script_pokemon_util.c:117-134`), so the override is correctly ordered |
| Outcome handling | `specialvar VAR_RESULT, GetBattleOutcome`; `goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Pox_Sudowoodo_Cleared`; `goto_if_ne VAR_RESULT, B_OUTCOME_WON, Pox_Release` |
| Wild tables | Route 36 land tables contain Bellsprout/Natu/Tangela/Gastly/Hoothoot/Hoppip/Drowzee/Baltoy only — **no Sudowoodo**, matching “Random Route 36 encounter: No” |

Compiled-byte sanity check (dumped from `Pox_Sudowoodo @ 0x08383f5d`, decoded against
`include/constants/script_commands.h` and `asm/macros/event.inc`):
`checkflag 0x26A / goto_if 0x0837dfbc / lockall / checkflag 0x1AB / goto_if 0x0837dfbd(Pox_Release) /
checkflag 0x868 / goto_if 0x08383fce(Wait) / checkitem 882,1 / cmp VAR_RESULT,0 / goto_if Wait /
loadword Pox_Text_Sudowoodo + callstd 5(MSGBOX_YESNO) / cmp VAR_RESULT,0 / goto_if 0x0837dfbd(Pox_Release) /
setwildbattle 185,20,NONE / special 0x276 / dowildbattle / specialvar VAR_RESULT,GetBattleOutcome / … /
0x08383fc6 Pox_Sudowoodo_Cleared / 0x08383fce Pox_Sudowoodo_Wait`. The script assembles correctly;
the stray leading tabs on the `goto_if_*` lines in the generated `.inc` are cosmetic.

### 1.3 Dead / ambiguous wiring

* No flag is orphaned: `FLAG_POX_SUDOWOODO_CLEARED` is written once and read twice; `FLAG_BADGE02_GET` is
  read by both chain scripts.
* **Duplicate giver.** The same `Pox_SquirtBottle` script is bound to two NPCs (interior + city street).
  Only the street one is in the story manifest. Behaviourally harmless (`checkitem` blocks a second gift)
  but it means the player can receive the bottle without ever entering the Flower Shop, and the manifest
  under-describes the chain.
* **Manifest gap.** The Route 36 tree itself is not a manifest event (only `Pox_PU_ROUTE36` at (24,24) is),
  so the manifest cannot be used to validate the encounter.
* **Metamon.** `MetamonBattleInit` (`src/metamon_trainer.c:101-111`) returns early unless
  `(gBattleTypeFlags & ~BATTLE_TYPE_IS_MASTER) == BATTLE_TYPE_TRAINER`, so the Sudowoodo battle can never
  enter the arena. Confirmed at runtime (§2, scenarios 5a/9).
* **No “watering”.** There is no watering animation or message: the flow is
  `msgbox “…Sprinkle it with the SQUIRTBOTTLE?”` → battle. Traditional Gen 2/4 has no YES/NO at all.

---

## 2. Dynamic playtest

Fixture: fresh game via `CB2_NewGame`, fast text, wild encounters disabled. `FLAG_BADGE02_GET` is set
directly in RAM rather than earned by beating Whitney (see *Untested*).

| # | Scenario | Expected | Observed | Verdict |
|---|---|---|---|---|
| 1 | Talk to either giver **without** badge 2 | “Beat WHITNEY…” refusal, no item | Exact text; `bottle = 0` at both placements | PASS |
| 2 | Talk to the Flower Shop giver **with** badge 2 | one bottle, then idempotent | “Obtained the SquirtBottle!”, “P put away the SquirtBottle in the KEY ITEMS POCKET”, hint text; key-items qty 1 → still 1 on a second talk. Street NPC behaves identically (2b) | PASS |
| 3 | Tree with badge 2 but **no** bottle | “weird tree” refusal, no battle | “This tree feels like stone! The flower grower near WHITNEY's GYM might know what to do.”; no battle; flag unset | PASS |
| 4a | Tree **with** bottle | prompt appears | “The odd tree blocks the path. Sprinkle it with the SQUIRTBOTTLE?”; context WAITING, `sLockFieldControls = 1` | PASS |
| 4b | Answer **No** (B) | script returns, controls free | **B is inert**: context stays `CONTEXT_WAITING`, `sLockFieldControls = 1`, prompt still up; only A advances (as YES) | **FAIL — defect** |
| 5a | Accept (A) | wild battle, Sudowoodo L20, 4 specified moves | `species 185, level 20, moves [88,102,175,67], IVs 31×6, ability 69/5, hp 64/64, item NONE`; `gBattleTypeFlags = 0x4` (`BATTLE_TYPE_IS_MASTER` only — no TRAINER/LINK/DOUBLE); `sMetamon = 0`, `gMetamonDecisions = 0`, `gMetamonFault = 0` | PASS |
| 5b | Win the battle | tree gone, flag set, no respawn | `gBattleOutcome = B_OUTCOME_WON(1)`; `FLAG_POX_SUDOWOODO_CLEARED` set; **screen hash at (39,21) changes** (sprite removed); leave to Goldenrod, return → pressing A yields no dialogue and no battle; flag still set | PASS |
| 6 | Run from the battle | tree and flag survive | `B_OUTCOME_RAN(4)`; flag unset; bottle kept; player can walk ((39,21)→(39,27)); the tree re-prompts with the same YES/NO text | PASS |
| 7 | Throw a real Master Ball | `B_OUTCOME_CAUGHT` clears the tree | ball consumed, `gBattleOutcome = 7`, Sudowoodo in storage (party was full), `FLAG_POX_SUDOWOODO_CLEARED` set, bottle kept, re-interaction silent | PASS |
| 8 | `FLAG_POX_TRIGGERS_ENABLED` cleared | both scripts inert, no soft-lock | no dialogue at either NPC or the tree, no item, no battle, `sLockFieldControls = 0`, player walks normally | PASS |
| 9 | 6-mon party + all 8 badges | still a plain wild battle | `gBattleTypeFlags = 0x4`, `sMetamon = 0`, decisions 0, fault 0, same mon/level/moves, `gPartiesCount = 6`; victory still sets the flag | PASS |
| 10 | **Control**: B on a vanilla YES/NO box (`PalletTown_EventScript_ProfOakTeam`) | isolates defect 4b | identical: `CONTEXT_WAITING` + locked before and after B | control PASS |

### 2.1 Post-encounter state of the SquirtBottle

Observed: quantity **1**, still `ITEM_SQUIRT_BOTTLE` (882) in the KEY ITEMS pocket after winning
(5b) *and* after catching (7); the tree re-interaction is what consumes nothing — the script only
`checkitem`s. Item data (`src/data/items.h:14181-14195`): `.type = ITEM_USE_BAG_MENU`,
`.fieldUseFunc = ItemUseOutOfBattle_CannotUse`, `.pocket = POCKET_KEY_ITEMS`, icon/palette borrowed
from `gItemIcon_WailmerPail`.

**Divergence from traditional behaviour.** In Gen 2 (and Crystal's successor design) the SquirtBottle is
*not* consumed by the tree but remains a working watering can afterwards; in FRLG its successor is the
Wailmer Pail. Here the item is a dead key item forever: it can never be selected for anything, so after
the encounter it is pure clutter. Using the item from the bag was **not** driven dynamically (see
*Untested*); the "cannot be used" conclusion is from the item data plus the fact that no code path
consumes or transforms it (grep: the only references to `ITEM_SQUIRT_BOTTLE` in the tree are
`checkitem`).

### 2.2 Ordering / gating matrix (all observed)

| badge 2 | bottle | giver says | tree says | battle |
|---|---|---|---|---|
| no | – | “Beat WHITNEY, then I can lend you my SQUIRTBOTTLE.” | “This tree feels like stone!…” | no |
| yes | no | hint text | “This tree feels like stone!…” | no |
| yes | yes | hint text | “Sprinkle it with the SQUIRTBOTTLE?” (B does nothing) | yes, on A |
| – | yes, triggers flag off | *nothing* | *nothing* | no |

Party size and badges do **not** affect the chain: 1 and 6 members both work, 0–8 badges both work, and
the battle is always a wild battle (never the policy-based metamon trainer path, never a `gMetamonFault`).

---

## 3. Issues (prioritized)

### P1 — `B` cannot answer “No” on any field YES/NO box (blocks the designed decline path)

* **Where:** the SquirtBottle prompt `msgbox Pox_Text_Sudowoodo, MSGBOX_YESNO`
  (`plastic_ox_story.inc:2144`), but the cause is engine-wide (scenario 10 control).
* **What:** pressing **B** on a field YES/NO box has no effect. The script context stays
  `CONTEXT_WAITING` (1) with `sLockFieldControls = 1`; the message box is still up; the only way forward
  is **A**, which selects YES. Measured: `status 1 → 1`, `locked 1 → 1`, script PC stuck at `0x08321e0e`
  (message-box engine) before and after B; after A the PC jumps to `0x08383fab` (past the prompt).
  Reproduced identically on the vanilla `PalletTown_EventScript_ProfOakTeam` dialog.
* **Impact:** the player *cannot* decline. The prompt is a lie: choosing not to battle is impossible, and
  the design note “Running from the battle leaves Sudowoodo in place so the player cannot accidentally
  lose the encounter” is the only remaining escape valve (and that path does work). Any other YES/NO in
  the game has the same defect, so this is not specific to this chain.
* **Note:** B is delivered correctly to the emulator (verified by opening and closing the pause menu with
  START/B), so this is an engine/input-handling bug, not a harness artifact.
* **Suggested direction (not implemented — playtest only):** make the prompt a plain
  `MSGBOX_DEFAULT` message that starts the battle (traditional behaviour, no question to answer), or fix
  the B handling in the field message box.

### P2 — The “odd tree” does not block anything; the PU→NU transition is not gated

The dialog says “The odd tree blocks the path”, but Route 36 has no warps and only one connection
(north → Route 37). A BFS over the 81×44 live map grid from the tree shows **558 tiles north of the tree
(y ≤ 19) reachable with the Sudowoodo tile blocked** — the same count as with it passable. The player can
simply walk around the tree and enter Route 37 (the NU transition) without ever obtaining the bottle or
resolving the encounter. If the tree is meant to be the PU→NU handoff, it needs real collision or a warp
gate; otherwise the flavor text should change.

### P3 — The SquirtBottle is a dead key item after the encounter

Never consumed, never usable (`ItemUseOutOfBattle_CannotUse`, `ITEM_USE_BAG_MENU`), it just occupies a
key-item slot forever, and it reuses the Wailmer Pail icon. Traditional behaviour keeps a usable watering
item. Either give it a field use (water plants / a one-line “the tree is already watered” message) or
remove it on clear.

### P4 — Silent failure when the key-items pocket is full

`giveitem ITEM_SQUIRT_BOTTLE` → `goto_if_eq VAR_RESULT, FALSE, Pox_Release` releases with **no message**,
so a full pocket silently denies the quest item and the player has no idea why the tree refuses. (Static
observation; not driven dynamically.)

### P5 — Duplicate gift NPC, manifest under-describes the chain

The same script is bound to the Flower Shop interior (2,4) and to Goldenrod City street (27,15); only the
street NPC appears in `story_manifest.json`, and the Route 36 tree is not a manifest event at all. The
manifest therefore cannot be used to validate this chain.

### P6 — Static encounter rolls ability/nature/gender

`CreateScriptedWildMon` uses a random personality, so the Sudowoodo's ability is re-rolled on every
attempt (observed `ABIL_RUN_AWAY(5)` and `ABIL_STURDY(69)` across runs). For a story encounter a fixed
ability would be expected; with Run Away the AI's escape behaviour differs. Minor.

### P7 — Cosmetic: `gText_...` / message text

`Pox_Text_Sudowoodo_Wait` says “the flower grower near WHITNEY's GYM”, which is correct for the Flower
Shop, but the gift can equally come from the street NPC. No functional impact.

---

## 4. Untested / caveats (no coverage claimed)

* **Whitney as the real gate.** `FLAG_BADGE02_GET` was set in RAM instead of by defeating Whitney. The
  gate is the same flag, but the *path* through the Whitney battle → `Pox_Whitney_Won` → badge flag was
  not exercised in this run.
* **Using the SquirtBottle from the bag menu.** Not driven: the field pause-menu navigation (START →
  BAG) could not be automated reliably, and an attempt to reach it accidentally selected SAVE (the game
  began a save). No save file was written or modified (`pokeemerald.sav` mtime unchanged), and the ROM
  was opened read-only. The “cannot be used” conclusion rests on the item data plus the absence of any
  code path that consumes the item.
* **Walking to Route 37 / through the tree tile** was not driven with the d-pad (only a static/BFS
  analysis of the map grid supports issue P2). Walking *around* the tree on the map was exercised in
  scenarios 6 and 8 (player moves freely on Route 36).
* **Full-bag gift denial (P4)** is static only.
* Screenshots were captured but could not be visually inspected in this session (no image-capable model);
  all visual claims above rest on framebuffer hashes, memory-state probes and decoded message text.
* Scenarios 5a/7 used `GivePlasticOxPlayerParty` (level-100 mons) to win quickly; battle *balance* of the
  L20 Sudowoodo was not assessed.

---

# Fix pass (run 5)

ROM after the fix pass: `pokeemerald.gba`, 33 554 432 bytes, built with
`DEVKITARM=~/devkitpro/opt/devkitpro/devkitARM make -j8`, zero errors.

```sh
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  ~/.venvs/mgba311/bin/python plastic_ox/demo/test_sudowoodo_v1.py
# 16 checks, 0 failures
```

The harness was updated for the changed prompt (scenarios 4, 5, 6, 7) and a new
scenario 11 was added that asserts the P6 determinism directly. `plastic_ox/demo/sudowoodo_results.json`
holds the full detail.

## Result

| check | run 4 | run 5 |
|---|---|---|
| 1 gift refused before badge (both givers) | PASS | PASS |
| 2 / 2b bottle gifted, idempotent | PASS | PASS |
| 3 tree refuses without the bottle | PASS | PASS |
| 4a prompt appears | PASS | PASS (now a plain message) |
| **4b B cannot answer "No"** | **FAIL** | **PASS - fixed** |
| 5a wild battle, species/level/moves/IVs | PASS | PASS (+ ability now pinned) |
| 5b win clears, no respawn | PASS | PASS (+ bottle taken back) |
| 6 run away keeps the Sudowoodo | PASS | PASS |
| 7 catch clears the obstruction | PASS | PASS (+ bottle taken back) |
| 8 triggers disabled, no soft-lock | PASS | PASS |
| 9 6 mons + 8 badges is a plain wild battle | PASS | PASS |
| 10 CONTROL: vanilla YES/NO box | PASS (defect reproduced) | PASS (defect **still** reproduced) |
| 11 NEW: three attempts give one Sudowoodo | - | PASS |

## P1 - FIXED: the "No" answer is gone, following Gen 2/4

* `data/scripts/plastic_ox_story.inc`, `Pox_Sudowoodo` - the
  `msgbox Pox_Text_Sudowoodo, MSGBOX_YESNO` + `goto_if_eq VAR_RESULT, NO` pair
  is replaced by `msgbox Pox_Text_Sudowoodo, MSGBOX_DEFAULT`, and the text is
  now "You spray the odd tree with the SQUIRTBOTTLE. It shivers!"
* Mirrored in the generator, `plastic_ox/alpha/build_story.py`, so a regeneration
  keeps it (the generator was **not** re-run).

Gen 2 and Gen 4 ask nothing at all at the tree: using the bottle waters it and
the battle starts. Running away still leaves the tree in place (scenario 6
re-verified), so the escape valve the run-4 report relied on is intact.

Evidence: scenario 4a records
`"no_yesno_prompt": true, "plain_message": true` and the seen text is
`You spray the odd tree with the SQUIRTBOTTLE.`; 4b presses **B** and the
message clears and the battle starts (`"battle_after_b": true`).

**Still open, and not fixed here:** the underlying engine behaviour. Scenario 10
still shows B inert on a vanilla field YES/NO box
(`PalletTown_EventScript_ProfOakTeam`, `status 1 -> 1`, `locked 1 -> 1`). That is
an input-handling bug in the fork, not in this chain, and it is outside a
game-data fix pass - the chain no longer depends on it.

## P2 - PARTLY fixed: the tree no longer claims to block the path

The BFS finding stands: ROUTE 36 has one connection (north to ROUTE 37) with a
14-lane road, so the single tile at (39,20) can be walked around and the NU
transition is not gated by the encounter.

* `data/scripts/plastic_ox_story.inc`, `Pox_Text_Sudowoodo` - "The odd tree
  blocks the path. Sprinkle it with the SQUIRTBOTTLE?" is gone; the new text
  does not assert a blockage the map does not have.

**Blocked:** actually gating ROUTE 36's north exit means closing a 14-lane road
behind `FLAG_POX_SUDOWOODO_CLEARED` (a flag-gated coordinate script plus carved
walls). That is a map/story decision, not a data-level fix, so it is left for a
design call. The text no longer lies in the meantime.

## P3 - FIXED: the SquirtBottle is no longer a dead key item

* `data/scripts/plastic_ox_story.inc`, `Pox_Sudowoodo_Cleared` -
  `removeitem ITEM_SQUIRT_BOTTLE` before `removeobject VAR_LAST_TALKED`.

Observed quantity in the KEY ITEMS pocket after the encounter: **1 -> 0** on both
paths (5b win, 7 catch). Note this diverges from Gen 2, where the SquirtBottle
survives as a working watering can: in this region nothing can consume or use
it after the tree is watered (`ItemUseOutOfBattle_CannotUse`,
`ITEM_USE_BAG_MENU`, and the only reference in the chain is `checkitem`), so
keeping it means a key-item slot occupied forever.

## P4 - FIXED: a full KEY ITEMS pocket no longer fails silently

* `data/scripts/plastic_ox_story.inc` - `giveitem`'s failure branch now goes to a
  new `Pox_SquirtBottle_Full` label with
  `Pox_Text_SquirtBottle_Full`: "There is no room in your KEY ITEMS POCKET right
  now. Come back once you have made some space." It replaces the jump to the
  shared, silent `Pox_Release`.

Still static-only evidence: the harness does not fill the key-items pocket, so
the branch is asserted by reading the compiled script rather than by filling 20
slots.

## P5 - FIXED: the manifest can now describe the chain

* `plastic_ox/alpha/story_manifest.json` - two events added:
  `{"map": "GoldenrodCity_FlowerShop_hns", "x": 2, "y": 4, "script": "Pox_SquirtBottle"}`
  (the interior giver, which run 4 noted was missing) and
  `{"map": "Route36_hns", "x": 39, "y": 20, "script": "Pox_Sudowoodo"}`
  (the tree itself).
* `plastic_ox/alpha/build_story.py` - new `manifest_event()` helper plus the two
  calls, so a regeneration keeps them.

Both givers remain (the Flower Shop grower and the Goldenrod City street
npc); `checkitem` still makes the second gift idempotent, and scenario 2/2b
re-verifies both.

## P6 - FIXED: the encounter is now the same Pokémon every time

* `src/wild_encounter.c`, `PlasticOx_PrepareSudowoodoMoves` - the existing POX
  special (already called by the script after `setwildbattle`) now also pins
  `MON_DATA_ABILITY_NUM` to `ABILITY_STURDY` before setting the four moves.
  `CreateScriptedWildMon` draws a random personality, and the ability slot is
  read out of it, so run 4 saw both `ABIL_RUN_AWAY` and `ABIL_STURDY`.

Evidence: scenario 11 runs three independent encounters -
`"ability_ids": [69, 69, 69], "species": [185, 185, 185],
"moves": [[88,102,175,67] x3], "levels": [20, 20, 20]`. Scenario 5a additionally
asserts the ability id is STURDY's 69.

## P7 - FIXED: the hint no longer names a single giver

* `data/scripts/plastic_ox_story.inc`, `Pox_Text_Sudowoodo_Wait` - "This tree
  feels like stone! Someone near WHITNEY's GYM has a SQUIRTBOTTLE that might
  help."

Observed verbatim in scenario 3.

## Not addressed

* **P2's PU -> NU gating** and **P1's engine-wide YES/NO B bug**, for the reasons
  given above.
* The run-4 caveats still stand: `FLAG_BADGE02_GET` is set in RAM rather than
  earned from Whitney, battle *balance* of the L20 Sudowoodo was not assessed,
  and no framebuffer screenshots were inspected (no image-capable model in this
  session) - every claim above rests on decoded message text, memory-state
  probes and battle-struct readings.

## 2026-10-06 follow-up: P2 resolved

The original 66×30 HNS Route 36 layout from `pokehns-expansion` revision
`44f50eedefe58691b0444973e4138e9190d8fafc` uses the Johto General and
Violet City tilesets and places Sudowoodo at `(39,19)`,
the south/north/east junction. The prior Plastic-Ox lower lane at `(40..44,20)`
let players walk around it. That lane is a tree line again, and the donor road
at `(43,18..19)` is restored. Sudowoodo now occupies `(39,19)`; Snorlax guards
only the east branch at `(43,19)`. Route 36 keeps the National Park arrival at
`(16,21)`, Route 37's north connection at offset 20, the Route 110 east portal
at `(65,18)`, existing event scripts, and the encounter table. The four
previously closed tiles on the north seam remain closed.

`plastic_ox/agent/open_route36_snorlax_pass.py` reproduces the seven tile
edits. `plastic_ox/demo/test_route36_junction.py` proves that the occupied
junction blocks the north and east roads from the park, including Surf
reachability, and checks the reverse approach. It also checks the three gate
states and walks Route 36 → Route 37 → Route 36 in the built ROM. Fresh
screenshots under `plastic_ox/demo/shots/route36_*.png` show the junction and
both sides of the route seam. The full Sudowoodo and Burned Tower emulator
playthroughs pass after this change.
