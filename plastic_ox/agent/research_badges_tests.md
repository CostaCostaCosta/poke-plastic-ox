# Research: Badge Tracking & Test Infrastructure (poke-plastic-ox)

Repo: `/home/eddie/repos/poke-plastic-ox` (pokeemerald-expansion based, master @ `7edb3b9952`)
Date of research: 2026-08-20 (research branch state)

---

## 1. Badge storage and reading

### 1.1 Flag constants — `include/constants/flags.h`

```c
1359:#define FLAG_BADGE01_GET                      (SYSTEM_FLAGS + 0x7)
1360:#define FLAG_BADGE02_GET                      (SYSTEM_FLAGS + 0x8)
1361:#define FLAG_BADGE03_GET                      (SYSTEM_FLAGS + 0x9)
1362:#define FLAG_BADGE04_GET                      (SYSTEM_FLAGS + 0xA)
1363:#define FLAG_BADGE05_GET                      (SYSTEM_FLAGS + 0xB)
1364:#define FLAG_BADGE06_GET                      (SYSTEM_FLAGS + 0xC)
1365:#define FLAG_BADGE07_GET                      (SYSTEM_FLAGS + 0xD)
1366:#define FLAG_BADGE08_GET                      (SYSTEM_FLAGS + 0xE)
1367:#define NUM_BADGES                            (1 + FLAG_BADGE08_GET - FLAG_BADGE01_GET)
```

- `SYSTEM_FLAGS` is `TRAINER_FLAGS_END + 1` = `0x860` (`flags.h:1348`), so badges are flags `0x867..0x86E`.
- `FLAG_IS_CHAMPION` = `SYSTEM_FLAGS + 0x1F` (`flags.h:1387`), used by the level-cap flag list as the post-league milestone.
- `gBadgeFlags[]` lookup table: `src/event_data.c:39-48`, declared `include/event_data.h:51`:

```c
const u16 gBadgeFlags[NUM_BADGES] =
{
    FLAG_BADGE01_GET,
    ...
    FLAG_BADGE08_GET,
};
```

### 1.2 Flags API — `src/event_data.c` / `include/event_data.h`

```c
27:u8 FlagSet(u16 id);
29:u8 FlagClear(u16 id);
30:bool8 FlagGet(u16 id);
```

### 1.3 Is there a badge-count helper?

**No exported/shared helper exists.** The count logic is duplicated inline in at least five places, always as a loop over the 8 badge flags:

| Location | Code |
|---|---|
| `src/match_call.c:1833-1842` | `static int GetNumOwnedBadges(void)` — counts `gBadgeFlags[i]` until the first unset flag (assumes badges are obtained in order), used at `:1855` (`GetNumOwnedBadges() < 5`) |
| `src/battle_script_commands.c:9909-9913` | `u8 badgeCount = 0; for (u32 i = FLAG_BADGE01_GET; i < FLAG_BADGE01_GET + NUM_BADGES; i++) if (FlagGet(i)) badgeCount++;` (Gen 8/9 missing-badge catch malus) |
| `src/shop_criteria.c:49-62` | `static UNUSED bool32 ShopCriteriaByBadgeCount(u32 count)` — same loop; also `ShopCriteriaByFlag` (`:65-75`) for single-flag checks |
| `src/main_menu.c:2207-2221` | `MainMenu_FormatSavegameBadges()` — loop `for (i = FLAG_BADGE01_GET; i < FLAG_BADGE01_GET + NUM_BADGES; i++)` incrementing `badgeCount` |
| `src/trainer_card.c:839-858` | per-badge array of counts for the trainer-card layout |

There is **no** `GetBadgeCount()`/`GetNumBadges()`/`CountBadges()` function in `src/*.c` or `include/*.h`. A new shared helper (e.g. `u8 GetBadgeCount(void)`) would be net-new; `GetNumOwnedBadges()` in `match_call.c` is `static` and order-dependent (stops at first unset flag), so it cannot be reused as-is.

### 1.4 How the game checks badge counts today — obedience

`src/battle_util.c:5618` — `enum Obedience GetAttackerObedienceForAction(void)`:

```c
5638:    if (FlagGet(FLAG_BADGE08_GET)) // Rain Badge, ignore obedience altogether
5639:        return OBEYS;
5640:
5641:    obedienceLevel = 10;
5642:
5643:    if (FlagGet(FLAG_BADGE01_GET)) // Stone Badge
5644:        obedienceLevel = 20;
5645:    if (FlagGet(FLAG_BADGE02_GET)) // Knuckle Badge
5646:        obedienceLevel = 30;
...   // each next badge adds 10: 40, 50, 60, 70, 80
5656:    obedienceLevel = 80;
...
5664:    if (levelReferenced <= obedienceLevel)
5665:        return OBEYS;
```

- Uses `FlagGet(FLAG_BADGE0x_GET)` directly — each badge raises the obedience level cap by 10 (20→80), badge 8 disables disobedience entirely.
- Exempts link battles, AI battlers, in-game partner, Frontier, recorded battles (`:5624-5637`).
- Config-gated: `B_OBEDIENCE_MECHANICS` (`include/config/battle.h:360`, default `GEN_LATEST`; in Gen8+ obedience also applies to non-outsider mons based on met level).
- Called from `src/battle_move_resolution.c:191` (`CancelerObedience`, CANCELER_OBEDIENCE at `:2408`); disobedience strings in `src/battle_message.c:1307`.

This is the closest existing "badge → numeric threshold" mapping in the game (badge count → obedience level). A tier system could reuse/modernize this pattern (badge count → tier → level cap).

---

## 2. Existing level-cap system — YES, engine support exists (disabled by default)

### 2.1 `src/caps.c` (whole file, 100+ lines) — merged from expansion PRs #5429/#5878/#6580

```c
 8: u32 GetCurrentLevelCap(void)
 9: {
10:     static const u32 sLevelCapFlagMap[][2] =
11:     {
12:         {FLAG_BADGE01_GET, 15},
13:         {FLAG_BADGE02_GET, 19},
14:         {FLAG_BADGE03_GET, 24},
15:         {FLAG_BADGE04_GET, 29},
16:         {FLAG_BADGE05_GET, 31},
17:         {FLAG_BADGE06_GET, 33},
18:         {FLAG_BADGE07_GET, 42},
19:         {FLAG_BADGE08_GET, 46},
20:         {FLAG_IS_CHAMPION, 58},
21:     };
22:
23:     u32 i;
24:
25:     if (B_LEVEL_CAP_TYPE == LEVEL_CAP_FLAG_LIST)
26:     {
27:         for (i = 0; i < ARRAY_COUNT(sLevelCapFlagMap); i++)
28:         {
29:             if (!FlagGet(sLevelCapFlagMap[i][0]))
30:                 return sLevelCapFlagMap[i][1];   // first unset flag's level = cap
31:         }
32:     }
33:     else if (B_LEVEL_CAP_TYPE == LEVEL_CAP_VARIABLE)
34:     {
35:         return VarGet(B_LEVEL_CAP_VARIABLE);
36:     }
37:
38:     return MAX_LEVEL;
39: }
```

- `GetSoftLevelCapExpValue(u32 level, u32 expValue)` (`caps.c:41-83`): EXP scaling when below/at/above cap for `EXP_CAP_SOFT`/`EXP_CAP_HARD` (`sExpScalingDown/Up` tables).
- `GetCurrentEVCap()` (`caps.c:85-123`): same flag-list pattern for EV caps (defaults scaled by `MAX_TOTAL_EVS * n/17`).

### 2.2 Headers

- `include/caps.h` — prototypes + compile-time config validation (`#error` if invalid config combos):
  - `:21 u32 GetCurrentLevelCap(void);`
  - `:22 u32 GetSoftLevelCapExpValue(u32 level, u32 expValue);`
  - `:23 u32 GetCurrentEVCap(void);`
- `include/config/caps.h` — **all level caps are OFF in this ROM by default**:
  - `:14 #define B_EXP_CAP_TYPE  EXP_CAP_NONE` (0 = no cap enforced)
  - `:15 #define B_LEVEL_CAP_TYPE LEVEL_CAP_NONE` (0; valid: `LEVEL_CAP_FLAG_LIST=1`, `LEVEL_CAP_VARIABLE=2`)
  - `:18 #define B_RARE_CANDY_CAP FALSE`
  - `:19 #define B_LEVEL_CAP_EXP_UP FALSE`
  - EV caps: `B_EV_CAP_TYPE EV_CAP_NONE` (`:28`), `B_EV_CAP_VARIABLE 8` (`:29`), `B_EV_ITEMS_CAP FALSE` (`:31`)

> The stock flag map (`15/19/24/29/31/33/42/46/58`) does NOT match plastic-ox tiers (13/20/30/36/42/50/55/60). Plastic Ox will need to edit `sLevelCapFlagMap` (or use `LEVEL_CAP_VARIABLE`) and set `B_EXP_CAP_TYPE`/`B_LEVEL_CAP_TYPE`.

### 2.3 Where the level cap is enforced today (all callers)

| Caller | Effect |
|---|---|
| `src/pokemon.c:5070` `TryIncrementMonLevel()` — `:5080 if (nextLevel > GetCurrentLevelCap() \|\| expPoints < ...) return FALSE;` | **hard blocks level increments** (used by daycare leveling, `src/daycare.c:325`) |
| `src/pokemon.c:3547` (in `PokemonUseItemEffects`, EXP Candy handling) — clamps EXP candies to the cap when `B_RARE_CANDY_CAP && B_EXP_CAP_TYPE == EXP_CAP_HARD` | Rare Candy/EXP Candy cap clamp |
| `src/party_menu.c:5825` `ItemUseCB_RareCandy()` — `if (!(B_RARE_CANDY_CAP && sInitialLevel >= GetCurrentLevelCap()))` | blocks Rare Candy use at/over cap |
| `src/battle_script_commands.c:4019-4035` — EXP reward via `GetSoftLevelCapExpValue(...)`; `:4034-4035` hard-cap clamps `battlerExpReward` when `B_EXP_CAP_TYPE == EXP_CAP_HARD` | battle EXP grants |
| `src/daycare.c:348,361,413,414` — daycare EXP/level clamps to `GetCurrentLevelCap()` | daycare |
| `src/pokemon.c:3486` / `:4960` — `GetCurrentEVCap()` for EV items / EV gains | EV caps |

---

## 3. Test infrastructure

### 3.1 Architecture

- Tests are compiled into a special ROM (`pokemerald-test.elf`), run headless under mGBA via `mgba-rom-test-hydra` + `mgba-rom-test` (see §4). Two test styles:
  1. **Function tests** (`TEST("name") { ... }`) — plain C functions, no battle; registered in `.tests` section. E.g. `test/pokemon.c`, `test/daycare.c`, `test/species.c`. Header: `include/test/test.h`.
  2. **Battle tests** — embedded DSL (`SINGLE_BATTLE_TEST` / `WILD_BATTLE_TEST` / `DOUBLE_BATTLE_TEST` / AI variants) with `ASSUMPTIONS { }`, `GIVEN { }`, `WHEN { TURN { ... } }`, `SCENE { ... }`, `THEN { ... }`, `FINALLY { ... }`. Header: `include/test/battle.h` (1368 lines). Runner: `test/test_runner_battle.c` (3991 lines).
- Test struct registration: `test/test_runner.c:1166` lines; `TEST(_name)` macro at `include/test/test.h:117-128`; battle-test macro at `include/test/battle.h:944-983`.
- Docs: `docs/tutorials/how_to_testing_system.md` (619 lines) — exact usage patterns, DSL reference.

### 3.2 Setting flags / badges in tests

- **Raw flag API is available in tests** — `FlagSet`/`FlagClear`/`FlagGet` are plain functions (declared `include/event_data.h:27-30`) and tests include `event_data.h`. This is the *only* way to set *multiple* flags in one test.
- **Badge example — `test/battle/capture.c:69-99`** (rides `B_MISSING_BADGE_CATCH_MALUS`):

```c
WILD_BATTLE_TEST("Capture: Missing badge malus apply correcly in gen 8")
{
    u32 expectedOdds = 0;
    u32 recordedOdds;
    u32 playerLevel = 0;
    u32 numBadges = 0;

    for (u32 j = 0; j < 8; j++)
    {
        PARAMETRIZE(expectedOdds = 50, playerLevel = 100, numBadges = j);
        ...
    }
    ...
    GIVEN {
        for (u32 j = 0; j < 8; j++)
        {
            if (j < numBadges)
                FlagSet(FLAG_BADGE01_GET + j);
            else
                FlagClear(FLAG_BADGE01_GET + j);
        }
        WITH_CONFIG(B_MISSING_BADGE_CATCH_MALUS, GEN_8);
        PLAYER(SPECIES_WOBBUFFET) {Level(playerLevel);}
        OPPONENT(SPECIES_CLEFFA);
    } WHEN {
        TURN { USE_ITEM(player, ITEM_POKE_BALL); }
    } SCENE {
        CATCHING_CHANCE(&recordedOdds);
    } THEN {
        EXPECT_EQ(expectedOdds, recordedOdds);
    }
}
```

This is the canonical "give N badges" pattern for tier tests: loop `FlagSet(FLAG_BADGE01_GET + j)` for `j < numBadges`.

- There is also a **single-flag DSL macro** `FLAG_SET(flagId)` (`include/test/battle.h:1016`) → `SetFlagForTest(__LINE__, flagId)` (`test/test_runner_battle.c:2255`) which enforces "one flag per test" (`INVALID_IF(DATA.flagId != 0, ...)`) and auto-clears in teardown (`ClearFlagAfterTest`, `:2291`). Not suitable for 8 badges at once — use raw `FlagSet` in GIVEN and `FlagClear` after (as capture.c does), or improve the helper.

### 3.3 Party setup: species, level, moves, items

- `PLAYER(SPECIES_X) { ... }` → `OpenPokemon(__LINE__, B_TRAINER_PLAYER, species)` (`test/test_runner_battle.c:2309`): `CreateMon(currentMon, species, 100, 0, OTID_STRUCT_PRESET(0))`, then clears moves/PP, `CalculateMonStats`.
- `Level(level)` → `Level_(__, level)` (`:2445`): sets `MON_DATA_LEVEL`, syncs `MON_DATA_EXP` to the growth-table value, recalculates stats. Level 1..MAX_LEVEL.
- Other modifiers (all in `include/test/battle.h:1029-1051`, impls in `test_runner_battle.c`): `Item`, `Moves`, `MovesWithPP`, `Ability`, `Nature`, `Gender`, `Status1`, `MaxHP`, `HP`, `Attack/Defense/SpAttack/SpDefense/Speed`, `HPIV...SpeedIV`, `Friendship`, `OTName`, `Shiny`, `DynamaxLevel`, `GigantamaxFactor`, `TeraType`, `Environment`.
- Party sizes / defaults: `OpenPokemon` requires `IsSpeciesEnabled`; battle-test mons default to Hardy nature, male, level 100 unless overridden.
- Non-battle tests construct mons directly: `CreateMon(&mon, species, level, personality, OTID_STRUCT_PLAYER_ID)` / `CreateRandomMonWithIVs` (e.g. `test/pokemon.c:25-30`), and can run overworld-style setup scripts with `RUN_OVERWORLD_SCRIPT(...)` (e.g. `givemon ...;` — `test/daycare.c:17-19`, `test/pokemon.c:392`).

### 3.4 Triggering level-ups and evolution checks in tests

- **Battle EXP level-up**: `WILD_BATTLE_TEST` + KO + `EXPERIENCE_BAR(player, ...)` then `THEN { EXPECT(GetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_LEVEL) > 1); }` — see `test/battle/exp.c:99-119` ("Large exp gains are supported").
- **Evolution inside a battle test**: no test currently drives a *level-up evolution scene* (the battle DSL has no `EVOLUTION` scene command; `EvolutionScene` isn't awaited). Form-change/mega evolution tests assert species + messages instead — e.g. `test/battle/form_change/mega_evolution.c:5-17`:

```c
SINGLE_BATTLE_TEST("Venusaur can Mega Evolve holding Venusaurite")
{
    GIVEN {
        PLAYER(SPECIES_VENUSAUR) { Item(ITEM_VENUSAURITE); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(player, MOVE_CELEBRATE, gimmick: GIMMICK_MEGA); }
    } SCENE {
        MESSAGE("Venusaur's Venusaurite is reacting to 1's Mega Ring!");
        ANIMATION(ANIM_TYPE_GENERAL, B_ANIM_MEGA_EVOLUTION, player);
        MESSAGE("Venusaur has Mega Evolved into Mega Venusaur!");
    } THEN {
        EXPECT_EQ(player->species, SPECIES_VENUSAUR_MEGA);
    }
}
```

- **Evolution-adjacent state test** — `test/battle/evolution_tracker.c:137` lines: Bisharp/Pawniard evo-tracker tests use `EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_EVOLUTION_TRACKER), 1)` (`:21`). This is the pattern to follow for asserting per-mon gating state after battle.
- **Direct evolution-target check for unit tests**: `GetEvolutionTargetSpecies(struct Pokemon *mon, enum EvolutionMode mode, u16 evolutionItem, struct Pokemon *tradePartner, bool32 *canStopEvo, enum EvoState evoState)` (`src/pokemon.c:4436`, decl `include/pokemon.h:853`) — a function test can `CreateMon` a level-30 `SPECIES_DRATINI`, set badges via `FlagSet`, call `GetEvolutionTargetSpecies(mon, EVO_MODE_NORMAL, ITEM_NONE, NULL, &x, CHECK_EVO)`, and `EXPECT_EQ` the target species. This sidesteps the evolution scene entirely and is the cheapest tier-gate test.

### 3.5 Assertions

- Function tests: `EXPECT(c)`, `EXPECT_EQ/NE/LT/LE/GT/GE`, `EXPECT_FASTER/SLOWER`, `BENCHMARK`, `KNOWN_FAILING`, `KNOWN_CRASHING`, `TO_DO`, `PARAMETRIZE` (all in `include/test/test.h:128-270`).
- Battle tests add `EXPECT_*` plus score comparisons; `THEN` runs after battle teardown per parameter, `FINALLY` after all parameters (`include/test/battle.h:1348-1358`).
- mGBA output via `Test_MgbaPrintf` / `MgbaVPrintf_` (`test/test_runner.c`).

---

## 4. Running the tests

From `Makefile` and `docs/tutorials/how_to_testing_system.md:5-15`:

```make
# Makefile
108: TESTELF := $(ROM_NAME:.gba=-test.elf)
109: HEADLESSELF := $(ROM_NAME:.gba=-test-headless.elf)
362: check: $(TESTELF)
363:     @cp $< $(HEADLESSELF)
364:     $(PATCHELF) $(HEADLESSELF) gTestRunnerHeadless '\x01' gTestRunnerSkipIsFail "$(TEST_SKIP_IS_FAIL)"
365:     $(ROMTESTHYDRA) $(ROMTEST) $(OBJCOPY) $(HEADLESSELF)
```

Commands:

```
make check -j                       # run ALL tests (headless mGBA via mgba-rom-test-hydra)
make check TESTS="Spikes"           # tests whose name starts with "Spikes"
make check TESTS="*Spikes*"         # tests whose name contains "Spikes"
make check TESTS="test/battle/move_effect/spikes.c"   # all tests in one file (exact filename)
make pokeemerald-test.elf TESTS="Spikes"              # build a ROM to open in mGBA for inspection
```

- Prereqs: `tools/` (`mgba-rom-test-hydra/mgba-rom-test-hydra`, `mgba/mgba-rom-test[-mac]`, `patchelf`, libagbsyscall, devkitARM). Makefile resolves `ROMTEST ?= $(shell command -v mgba-rom-test ...)` (`:228-235`).
- On `rh-hideout` CI, skipped tests fail (`TEST_SKIP_IS_FAIL`); locally they pass (`:358-360`).
- `make tidycheck` removes test artifacts (`:394`).

---

## 5. FEATURES.md and plastic-ox prior work

### 5.1 `FEATURES.md` (repo root, 94 lines)

This is the **stock pokeemerald-expansion FEATURES.md** (links to `include/config/*.h` incl. `Caps config` → `include/config/caps.h`). Relevant stock features:
- "Popular features: **Level/EV Caps**, Sleep Clause, Type Indicators" (under Upgraded Battle Engine).
- "Revamped Evolution System: Multiple Evolution conditions can be stacked ... Every condition except Affection and console gyroscope is supported."
- "Integrated Testing" (developer tools), "Full Trainer customization" (Showdown import), gimmicks (Mega/Z/Dynamax/Tera), Gen IX data/mechanics.

No plastic-ox-specific content in root FEATURES.md.

### 5.2 Plastic-ox design docs — `plastic_ox/`

**`plastic_ox/plasticox_encounters_v1.md` (581 lines) is the design doc for this exact feature.** Key contents:

- **Tier ↔ gym ↔ level cap table** (`:13-27`):
  | Gym | Tier | Level cap |
  |---|---|---|
  | 1 | LC | 13 |
  | 2 | PU (NFE+ZU+ZUBL+PU) | 20 |
  | 3 | NU | 30 |
  | 4 | RU | 36 |
  | 5 | UU | 42 |
  | 6 | UUBL | 50 |
  | 7 | OU (+`(OU)`) | 55 |
  | 8 | OU | 60 |
- **Evolution gating rules** (`:32-56`): evolve iff normal condition met AND target species' tier unlocked; if normal evo level > tier cap, lower evo level to the cap (e.g. Dratini→Dragonair 30→20); if normal level < tier cap, keep normal level, just gate the unlock.
- **OU-only family overrides** (`:60-70`): Magikarp→Gyarados, Feebas→Milotic, Diglett→Dugtrio, Shroomish→Breloom unavailable until OU.
- **Ubers** (12 species: Mewtwo, Mew, Wynaut, Wobbuffet, Lugia, Ho-Oh, Latias/Latios, Kyogre, Groudon, Rayquaza, Deoxys) outside badge progression (`:97-106`).
- Per-tier species lists, encounter-line lists, **downward evolution-level change tables** (e.g. 18 changes at PU: Ekans→Arbok 22→20, Dratini→Dragonair 30→20, ...; 6 at NU: Pidgeotto→Pidgeot 36→30, ...), and evolution-item releases (Moon/Sun/etc. stones per tier) (`:107-581`).

Other `plastic_ox/` docs are map/story design (romhack overworld):
- `plastic_ox_map_v0.1/.3/.4.md` — merged Kanto/Johto/Hoenn region, gym order (Roxanne→Morty→Winona→Erika→Blaine...), badge-gated rare encounters at National Park (`map_v0.1.md:257`).
- `plastic_ox_storyV0.1/.3/.4.md` — story beats.
- `mermaid/` — map flowchart tooling (`stitch_mermaid_maps.py`, `plastic_ox_flowchart_v0.4.mmd`, port templates).

### 5.3 Code already in the repo (non-stock)

git log (`git log --oneline | head`): HEAD = `7edb3b9952 initial markdown` (CostaCostaCosta), the **only** plastic-ox commit; rest are upstream expansion merges. That commit added `plastic_ox/` docs plus two C files:

- `include/rom_native_obs.h` (117 lines) and `src/rom_native_obs/rom_native_obs.c` (557 lines) — a **debug/test-only battle-state encoder** ("canonical RomBattleState schema" mirroring `metamon/metamon/rom_native_obs/schema.py`) reading `gBattleMons`/`gParties`/weather/etc. Not badge/tier/evolution related, but confirms the repo already carries test-adjacent instrumentation.

**No tier/evolution-gating code exists in src/include.** Greps for `tier|TIER`, `EVOLUTION_GATE`, `evolv.*badge`, `badge.*evolv` in `src/` and `include/` return nothing relevant. `src/caps.c`/`include/config/caps.h` are stock, with level caps disabled by default.

---

## 6. Key hooks for implementation

1. **Badge count helper** — none exists; add e.g. `u8 GetBadgeCount(void)` (loop `FLAG_BADGE01_GET..+NUM_BADGES`, or reuse `gBadgeFlags[]` from `src/event_data.c:39`) and declare in `include/event_data.h`. Existing inline loops to unify: `match_call.c:1833`, `battle_script_commands.c:9909`, `shop_criteria.c:49`, `main_menu.c:2210`.
2. **Tier lookup table** — new table `{ requiredBadges, tier }` or `{ FLAG_BADGE0x_GET, levelCap }`; mirror `sLevelCapFlagMap` style in `src/caps.c:10-21`. Plastic-ox caps (13/20/30/36/42/50/55/60) differ from stock (15/19/24/29/31/33/42/46/58).
3. **Central gate point** — `GetEvolutionTargetSpecies()` (`src/pokemon.c:4436`) is the single funnel for level-up (`EVO_MODE_NORMAL`), items, trades, battle-special, overworld-special, and script evolutions. Add the tier check there (compare target species tier against badge count) — covers all callers automatically (`party_menu.c:5847/6037`, `battle_main.c:5629/5637`, `pokemon.c:3775/6316`, `scrcmd.c:3320`).
4. **Level-up paths that bypass GetEvolutionTargetSpecies** — `TryEvolvePokemon()` (`src/battle_main.c:5617`) calls it, `ItemUseCB_RareCandy` (`src/party_menu.c:5815`) calls it, `PartyMenuTryEvolution` (`src/party_menu.c:6027`) calls it — all funnel through hook #3.
5. **Level cap enforcement already exists and is config-disabled** — set `include/config/caps.h`: `B_EXP_CAP_TYPE` (HARD/SOFT), `B_LEVEL_CAP_TYPE` (`LEVEL_CAP_FLAG_LIST`), optionally `B_RARE_CANDY_CAP`; adjust `sLevelCapFlagMap`. Runtime blockers are already wired: `TryIncrementMonLevel` (`pokemon.c:5070`), party-menu Rare Candy check (`party_menu.c:5825`), battle EXP clamps (`battle_script_commands.c:4019-4035`), daycare (`daycare.c`).
6. **Tests** — write `test/battle/tier_evolution.c` (or function-style `test/pokemon.c` additions):
   - Give badges: raw `FlagSet(FLAG_BADGE01_GET + j)` loop in GIVEN (pattern: `test/battle/capture.c:85-92`).
   - Set mon level: `PLAYER(SPECIES_DRATINI) {Level(30);}` (`Level_` at `test_runner_battle.c:2445`).
   - Assert gate: `EXPECT_EQ(GetEvolutionTargetSpecies(&gParties[B_TRAINER_PLAYER][0], EVO_MODE_NORMAL, ITEM_NONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_NONE)` vs `SPECIES_DRAGONAIR` — the function-style test avoids the evolution scene. For end-to-end behavior, follow `test/battle/exp.c` (EXP + `MON_DATA_LEVEL`) and assert final species post-battle in `THEN` like mega_evolution.c does.
   - Run: `make check TESTS="test/battle/tier_evolution.c"` or `make check TESTS="*Tier*"`; full suite `make check -j`.
