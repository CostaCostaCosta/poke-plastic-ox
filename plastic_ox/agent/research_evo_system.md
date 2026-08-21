# Plastic Ox — Evolution System Research

Research for the **tier-based evolution gating** feature:
a Pokémon may evolve only when its normal evolution condition is met AND
the trainer's badge count has unlocked the competitive tier of the target species.

All line numbers verified against branch `master` (HEAD 7edb3b9952).

Plastic Ox design source (already written): `plastic_ox/plasticox_encounters_v1.md`
contains the "Evolution Gating" rule set and tier→level-cap table (Gym1 LC-13,
Gym2 PU-20, Gym3 NU-30, Gym4 RU-36, Gym5 UU-42, Gym6 UUBL-50, Gym7 OU-55, Gym8 OU-60).

---

## 1. Core structures and constants

### `struct EvolutionParam` and `struct Evolution` — include/pokemon.h:376-390

```c
struct EvolutionParam
{
    u16 condition;
    u16 arg1;
    u16 arg2;
    u16 arg3;
};

struct Evolution
{
    u16 method;
    u16 param;
    enum Species targetSpecies;
    const struct EvolutionParam *params;
};
```

- `method` is one of `enum EvolutionMethods` (see below).
- `param` is the method argument: level for `EVO_LEVEL`/`EVO_LEVEL_BATTLE_ONLY`,
  item id for `EVO_ITEM`, trade partner species for `EVO_TRADE` (unused via
  `IF_TRADE_PARTNER_SPECIES`), post-evolution species for `EVO_SPLIT_FROM_EVO`,
  etc.
- `params` points to a `CONDITIONS_END`-terminated array of
  `struct EvolutionParam` extra conditions.
- `targetSpecies` is the species resulting from this evolution entry.

### Method constants — include/constants/pokemon.h:322-331

```c
enum EvolutionMethods {
    EVO_NONE,                   // Not an actual evolution, used to generate offspring that can't evolve into the specified species, like regional forms.
    EVO_LEVEL,                  // Pokémon reaches the specified level
    EVO_TRADE,                  // Pokémon is traded
    EVO_ITEM,                   // specified item is used on Pokémon
    EVO_SPLIT_FROM_EVO,         // A clone is generated and evolved when another evolution happens
    EVO_SCRIPT_TRIGGER,         // Player interacts with an overworld trigger
    EVO_LEVEL_BATTLE_ONLY,      // Pokémon reaches the specified level, in battle only
    EVO_BATTLE_END,             // Battle ends, doesn't need to level up
    EVO_SPIN                    // The player spins in the overworld
};
```

### Modes — include/constants/pokemon.h:334-342

```c
enum EvolutionMode {
    EVO_MODE_NORMAL,
    EVO_MODE_TRADE,
    EVO_MODE_ITEM_USE,
    EVO_MODE_ITEM_CHECK,         // If an Everstone is being held, still want to show that the stone *could* be used on that Pokémon to evolve
    EVO_MODE_BATTLE_SPECIAL,
    EVO_MODE_OVERWORLD_SPECIAL,
    EVO_MODE_SCRIPT_TRIGGER,
    EVO_MODE_BATTLE_ONLY,        // This mode is only used in battles to support Tandemaus' unique requirement
};
```

Note: **there is no `EVO_MODE_BATTLE_ITEM`** — battle item evolutions use
`EVO_MODE_ITEM_USE` (see §3). `EVO_MODE_BATTLE_SPECIAL` covers `EVO_BATTLE_END`
(first in a non-leveling battle context, e.g. Sirfetch'd/Farigiraf), and
`EVO_MODE_BATTLE_ONLY` makes `EVO_LEVEL_BATTLE_ONLY` evolutions (Tandemaus)
evaluable only during the battle level-up flow.

### Additional-condition types — include/constants/pokemon.h:272-319

`enum EvolutionConditions` spans lines 272-319 (ends with `CONDITIONS_END`).
Notable entries and their meanings (quoted from the header):

```c
enum EvolutionConditions {
    // Gen 2
    IF_GENDER,                          // The Pokémon is of specific gender.
    IF_TIME,                            // It is currently the specific time of day.
    IF_NOT_TIME,                        // It is NOT currently the specific time of day.
    IF_MIN_FRIENDSHIP,                  // The Pokémon has the defined amount of Friendship.
    IF_ATK_GT_DEF,                      // ...
    ...
    // Gen 4
    IF_SPECIES_IN_PARTY,                // ...
    IF_IN_MAP,                          // The player is currently in the specific map.
    IF_IN_MAPSEC,                       // ...
    IF_KNOWS_MOVE,                      // ...
    // Gen 5
    IF_TRADE_PARTNER_SPECIES,           // The Pokémon is traded for a specific species.
    // Gen 6
    IF_TYPE_IN_PARTY,                   // ...
    IF_WEATHER,                         // It is currently the specific weather in the current map.
    IF_KNOWS_MOVE_TYPE,                 // ...
    // Gen 8
    IF_NATURE, ...
    IF_RECOIL_DAMAGE_GE, ...
    IF_CRITICAL_HITS_GE, ...
    IF_USED_MOVE_X_TIMES, ...
    // Gen 9
    IF_DEFEAT_X_WITH_ITEMS, ...
    IF_PID_MODULO_100_GT, ...
    IF_MIN_OVERWORLD_STEPS, ...
    IF_BAG_ITEM_COUNT, ...
    IF_REGION,                          // The Player is in the specific region.
    IF_NOT_REGION,                      // ...
    CONDITIONS_END
};
```

- `IF_BAG_ITEM_COUNT` (line ~316) is the Shedinja ball check and the best
  precedent for a "stateful" condition; a badge gate could be implemented as
  either a new `IF_*` condition or a tier-per-target-species check.
- Length used to edit: no enum member is tied to a generated file; appending
  `IF_TIER_GATE` before `CONDITIONS_END` is safe.
- Sentinel defines: `EVOLUTIONS_END` = `0xFFFF` (include/constants/pokemon.h:270);
  `CONDITIONS_END` is the final enum value (line 319).

### `GetSpeciesEvolutions` — src/pokemon.c:3326-3335

```c
const struct Evolution *GetSpeciesEvolutions(enum Species species)
{
    const struct Evolution *evolutions = gSpeciesInfo[SanitizeSpeciesId(species)].evolutions;
    if (evolutions == NULL)
        return gSpeciesInfo[SPECIES_NONE].evolutions;
    return evolutions;
}
```

Declared in include/pokemon.h:836. Every consumer gets the `SPECIES_NONE`-fallback
empty table if the species has no `.evolutions` field.

---

## 2. Per-species evolution tables

Generated at compile time from hand-written C headers:

- Include order: `src/data/pokemon/species_info.h:153-161` includes
  `species_info/gen_1_families.h` … `species_info/gen_9_families.h`, all
  entries inside the `const struct SpeciesInfo gSpeciesInfo[] = { ... }`
  initializer (SPECIES_NONE entry at the top, lines ~86-148).
- There is **no JSON/porygon source** for species info. Only learnsets are
  JSON-driven (`src/data/pokemon/*.json` consumed by
  `tools/learnset_helpers/make_teachables.py` / `make_learnables.py` via
  Makefile rules around Makefile:540-565). Species stats/evolutions are edited
  directly in these `.h` files.
- Macros that wrap the tables (src/data/pokemon/species_info.h:12-14):

```c
#define EVOLUTION(...) (const struct Evolution[]) { __VA_ARGS__, { EVOLUTIONS_END }, }
#define CONDITIONS(...) ((const struct EvolutionParam[]) { __VA_ARGS__, {CONDITIONS_END} })
```

### Concrete examples

Abra → Kadabra (src/data/pokemon/species_info/gen_1_families.h:8642):

```c
        .evolutions = EVOLUTION({EVO_LEVEL, 16, SPECIES_KADABRA}),
```

Kadabra → Alakazam (gen_1_families.h:8725-8726):

```c
        .evolutions = EVOLUTION({EVO_TRADE, 0, SPECIES_ALAKAZAM},
                                {EVO_ITEM, ITEM_LINKING_CORD, SPECIES_ALAKAZAM}),
```

Dratini (gen_1_families.h:20353):
```c
        .evolutions = EVOLUTION({EVO_LEVEL, 30, SPECIES_DRAGONAIR}),
```
Dragonair (gen_1_families.h:20423):
```c
        .evolutions = EVOLUTION({EVO_LEVEL, 55, SPECIES_DRAGONITE}),
```

Nincada (gen_3_families.h:3739-3743) — the special split flow (§7):
```c
        .evolutions = EVOLUTION({EVO_LEVEL, 20, SPECIES_NINJASK},
                            #if P_SHEDINJA_BALL >= GEN_4
                                {EVO_SPLIT_FROM_EVO, SPECIES_NINJASK, SPECIES_SHEDINJA, CONDITIONS({IF_BAG_ITEM_COUNT, ITEM_POKE_BALL, 1})}),
                            #else
                                {EVO_SPLIT_FROM_EVO, SPECIES_NINJASK, SPECIES_SHEDINJA}),
                            #endif
```

---

## 3. `GetEvolutionTargetSpecies` flow — src/pokemon.c:4436-4631

Signature and setup (4436-4462):

```c
enum Species GetEvolutionTargetSpecies(struct Pokemon *mon, enum EvolutionMode mode, u16 evolutionItem, struct Pokemon *tradePartner, bool32 *canStopEvo, enum EvoState evoState)
{
    int i;
    enum Species targetSpecies = SPECIES_NONE;
    enum Species species = GetMonData(mon, MON_DATA_SPECIES, 0);
    enum Item heldItem = GetMonData(mon, MON_DATA_HELD_ITEM, 0);
    u32 level = GetMonData(mon, MON_DATA_LEVEL, 0);
    enum HoldEffect holdEffect;
    const struct Evolution *evolutions = GetSpeciesEvolutions(species);

    if (evolutions == NULL)
        return SPECIES_NONE;
    ...
    // Prevent evolution with Everstone, unless we're just viewing the party menu with an evolution item
    if (holdEffect == HOLD_EFFECT_PREVENT_EVOLVE
        && mode != EVO_MODE_ITEM_CHECK
        && (P_KADABRA_EVERSTONE < GEN_4 || species != SPECIES_KADABRA))
        return SPECIES_NONE;

    switch (mode)
```

### Mode → method mapping and gate insertion points

Every mode is a `for` loop over `evolutions[i]` that:
1. filters methods valid for the mode,
2. checks `conditionsMet`,
3. calls `DoesMonMeetAdditionalConditions(...)` (the shared per-entry condition gate),
4. on success sets `targetSpecies = evolutions[i].targetSpecies; break;` (first match wins — expansion comment explicitly says evolutions are ordered, first match stops).

| Mode (src/pokemon.c) | Valid methods | DoesMonMeetAdditionalConditions call | Best place for a tier/badge gate |
|---|---|---|---|
| `EVO_MODE_NORMAL` / `EVO_MODE_BATTLE_ONLY` (4466-4495) | `EVO_LEVEL` (param<=level), `EVO_LEVEL_BATTLE_ONLY` (mode==BATTLE_ONLY) | 4487 | after `conditionsMet`, parallel to 4487, before target assigned |
| `EVO_MODE_TRADE` (4497-4519) | `EVO_TRADE` | 4511 | between 4511 and target assignment |
| `EVO_MODE_ITEM_USE` / `EVO_MODE_ITEM_CHECK` (4521-4547) | `EVO_ITEM` (param==evolutionItem) | 4537 | after 4537 check; note ITEM_CHECK is the "show party menu hint" path that also (optionally) should be gated |
| `EVO_MODE_BATTLE_SPECIAL` (4550-4572) | `EVO_BATTLE_END` (party slot passed via evolutionItem arg) | 4564 | between condition check and assignment |
| `EVO_MODE_OVERWORLD_SPECIAL` (4575-4597) | `EVO_SPIN` (param matched against `gSpecialVar_0x8000`) | 4590 | between condition check and assignment |
| `EVO_MODE_SCRIPT_TRIGGER` (4600-4611) | `EVO_SCRIPT_TRIGGER` (param==evolutionItem) | 4609 | between condition check and assignment |

Because **each mode loop is separate**, a badge/tier check must be inserted once
per loop (6 sites), or refactored into a small inline helper, e.g.:

```c
static bool32 CanMonEvolveToSpecies(enum Species targetSpecies, enum EvolutionMode mode, enum EvoState evoState)
```

applied at each `if (conditionsMet && DoesMonMeetAdditionalConditions(...))`.

### All-modes convergence — the single choke point

After the `switch` (line 4618-4631):

```c
    // Pikachu, Meowth, Eevee and Duraludon cannot evolve if they have the
    // Gigantamax Factor. We assume that is because their evolutions
    // do not have a Gigantamax Form.
    if (GetMonData(mon, MON_DATA_GIGANTAMAX_FACTOR)
     && GetGMaxTargetSpecies(species) != species
     && GetGMaxTargetSpecies(targetSpecies) == targetSpecies)
    {
        return SPECIES_NONE;
    }

    return targetSpecies;
}
```

This is the one place every mode funnels through before returning — a single
`targetSpecies`-based tier check here would gate ALL modes at once with one edit
(badge count lookup + per-species tier lookup). The per-mode loops would then
only need the same check if ITEM_CHECK must keep "stone could be used" hints
while the tier is locked (see §4).

`evoState` (`CHECK_EVO` vs `DO_EVO`, include/constants/pokemon.h:358-362)
distinguishes "probe" from "commit"; side effects (bag item / held item removal
for e.g. `IF_BAG_ITEM_COUNT`, `IF_HOLD_ITEM`) happen inside
`DoesMonMeetAdditionalConditions` only in the `DO_EVO` branch
(src/pokemon.c:4413-4427). A tier gate inserted at the convergence point runs
identically for both probe and commit — which is correct, since the commit call
always directly follows a successful probe in every caller.

### Callers (all use the CHECK_EVO then DO_EVO pattern)

| Caller | Mode | Location |
|---|---|---|
| Battle end / level-up evolution | `EVO_MODE_BATTLE_SPECIAL`, then `EVO_MODE_BATTLE_ONLY` | src/battle_main.c:5617-5657 (`TryEvolvePokemon`; CHECK at 5629/5641, DO at 5649, `EvolutionScene` at 5650) |
| Rare Candy in party menu | `EVO_MODE_NORMAL` | src/party_menu.c:5847 (CHECK), 5852 (DO) |
| `PartyMenuTryEvolution` (level-up candy / forced evo) | `EVO_MODE_NORMAL` | src/party_menu.c:6037 (CHECK), 6041 (DO) |
| Stone use in party menu | `EVO_MODE_ITEM_USE` | src/pokemon.c:3775 (CHECK), 3779 (DO) — inside `ITEM4_EVO_STONE` effect handler |
| Stone "usable?" hint in party menu | `EVO_MODE_ITEM_CHECK` | src/party_menu.c:1183 |
| In-game trade evolution | `EVO_MODE_TRADE` | src/trade.c:3875/3878, 4380/4383, 4426/4429 |
| Script event evolution (`evolevent`-style) | `EVO_MODE_SCRIPT_TRIGGER` | src/scrcmd.c:3312/3319 (`EventEvolution`; sets `gSpecialVar_Result = EVO_EVENT_IMPOSSIBLE` on `SPECIES_NONE`) |
| Overworld spin evolutions | `EVO_MODE_OVERWORLD_SPECIAL` | src/pokemon.c:6316/6320 (`TrySpecialOverworldEvo`) |

All these call `BeginEvolutionScene`/`EvolutionScene` only when
`targetSpecies != SPECIES_NONE` — so **if the tier gate collapses the target to
SPECIES_NONE, no evolution scene ever starts**, and the existing
"no effect / can't evolve" fallbacks fire instead (see §4).

---

## 4. Evolution scene UI and cancellation — src/evolution_scene.c

### Entry points

```c
void BeginEvolutionScene(struct Pokemon *mon, enum Species postEvoSpecies, bool32 canStopEvo, u8 partyId)   // evolution_scene.c:200
void EvolutionScene(struct Pokemon *mon, enum Species postEvoSpecies, bool32 canStopEvo, u8 partyId)         // evolution_scene.c:210
void TradeEvolutionScene(struct Pokemon *mon, enum Species postEvoSpecies, u8 preEvoSpriteId, u8 partyId)    // evolution_scene.c:517 (used by trade.c)
```

`canStopEvo` is folded into task data: `#define tBits data[3]` and
`TASK_BIT_CAN_STOP (1 << 0)` (evolution_scene.c:161-169); in
`Task_EvolutionScene` the B-button is checked at lines 658-666:

```c
    // check if B Button was held, so the evolution gets stopped
    if (gMain.heldKeys == B_BUTTON
        && gTasks[taskId].tState == EVOSTATE_WAIT_CYCLE_MON_SPRITE
        && gTasks[sEvoGraphicsTaskId].isActive
        && gTasks[taskId].tBits & TASK_BIT_CAN_STOP)
    {
        gTasks[taskId].tState = EVOSTATE_CANCEL;
        gSpecialVar_Result = EVO_EVENT_INTERRUPTED;
        ...
```

### "stopped evolving" / cancel message

State machine `EVOSTATE_CANCEL → EVOSTATE_CANCEL_MON_ANIM → EVOSTATE_CANCEL_MSG`
(849-875):

```c
    case EVOSTATE_CANCEL_MSG:
        if (EvoScene_IsMonAnimFinished(sEvoStructPtr->preEvoSpriteId))
        {
            if (gTasks[taskId].tEvoWasStopped) // FRLG auto cancellation
                StringExpandPlaceholders(gStringVar4, gText_EllipsisQuestionMark);
            else
                StringExpandPlaceholders(gStringVar4, gText_PkmnStoppedEvolving);

            BattlePutTextOnWindow(gStringVar4, B_WIN_MSG);
            gTasks[taskId].tEvoWasStopped = TRUE;
            gTasks[taskId].tState = EVOSTATE_TRY_LEARN_MOVE;
        }
        break;
```

Texts (src/battle_message.c:1452-1455):

```c
const u8 gText_PkmnIsEvolving[] = _("What?\n{STR_VAR_1} is evolving!");
const u8 gText_PkmnStoppedEvolving[] = _("Huh? {STR_VAR_1}\nstopped evolving!\p");
const u8 gText_EllipsisQuestionMark[] = _("……?\p");
```

### Hooks for a "blocked evolution" message

- The scene itself is only entered after a successful `GetEvolutionTargetSpecies`
  probe. A tier-blocked mon **never reaches the scene**; the caller shows the
  generic fallback instead:
  - party menu Rare Candy / stone: `gText_WontHaveEffect` — used at
    src/party_menu.c:5862 (`DisplayPartyMenuMessage(gText_WontHaveEffect, TRUE)`
    when `targetSpecies == SPECIES_NONE`) and item-use default branch
    src/party_menu.c:4824-4825; also item_use.c:1371;
  - script event: `gSpecialVar_Result = EVO_EVENT_IMPOSSIBLE`
    (src/scrcmd.c:3314-3317);
  - battle: mon simply stays unevolved after `TryEvolvePokemon` returns
    (src/battle_main.c:5654-5657).
- **Cleanest UX hook:** a new message (e.g. `gText_CantEvolveYet` with a "needs
  N badges" line) shown in the callers' `SPECIES_NONE` fallback branches, or a
  dedicated `GetEvolutionTargetSpecies` out-parameter / small
  `GetEvolutionTargetSpeciesBlockedReason(mon, mode, …)` query used by those
  fallbacks.
- Second hook: `EVOSTATE_INTRO_MSG` (evolution_scene.c:682-687) prints
  `gText_PkmnIsEvolving`; the scene has no notion of "blocked" internally.

### Note: there is NO `src/evolution_tracker.c` UI in this repo

The parent brief asked about "evolution tracker UI". Evolution tracking here is
**not a UI**: it is a per-mon counter (2× 5-bit fields in the save substruct).

- `MON_DATA_EVOLUTION_TRACKER` accessors: include/pokemon.h:127 (enum), 149-151
  (substruct fields `evolutionTracker1/2`), src/pokemon.c:2439-2446 /
  2871-2878.
- Consumed by `DoesMonMeetAdditionalConditions` for
  `IF_RECOIL_DAMAGE_GE`, `IF_USED_MOVE_X_TIMES`, `IF_DEFEAT_X_WITH_ITEMS`
  (src/pokemon.c:4355, 4370, 4375).
- Test coverage pattern: `test/battle/evolution_tracker.c` (asserts
  `GetMonData(..., MON_DATA_EVOLUTION_TRACKER)`).
- There is no summary-screen/party-menu UI listing evolution conditions in
  `src/pokemon_summary_screen.c` (grep finds no evolution handling there), so
  "display badge requirement" is greenfield UI work if the tier gate should be
  visible pre-evolution.

---

## 5. Config switches: naming conventions and location

- Feature flags in expansion live in `include/config/*.h`, `#define`d with a
  one-letter domain prefix: `B_` battle (include/config/battle.h), `P_` Pokémon
  species/data (include/config/pokemon.h), `OW_` overworld (include/config/overworld.h),
  plus caps (include/config/caps.h), item, ai, etc. `GEN_*` constants
  (`GEN_1`..`GEN_LATEST`) are used for generation-sensitive values.
- Example evolution/species-related configs (include/config/pokemon.h):
  - line 23: `#define P_EVOLUTION_LEVEL_1_LEARN GEN_LATEST`
  - line 26: `#define P_FRIENDSHIP_EVO_THRESHOLD GEN_LATEST`
  - line 39: `#define P_SHEDINJA_BALL GEN_LATEST`
  - line 40: `#define P_KADABRA_EVERSTONE GEN_LATEST`
- `P_` prefix is the right fit for a species/tier feature: new config
  `P_EVOLUTION_TIER_GATING` (bool) belongs in include/config/pokemon.h under the
  "Evolution settings" section, following the comment+`#define` style; constant
  tables (e.g. tier→badge map) also live near where they are used, mirroring
  `static const u32 sLevelCapFlagMap[][2]` in src/caps.c:10-21.
- Config philosophy (docs/STYLEGUIDE.md:442-454): features that can alter saves
  must be config-gated and **off by default** unless they reflect GF-consistent
  behavior or champion content. Tier gating changes evolution outcomes, so gate
  it behind `P_EVOLUTION_TIER_GATING` defaulting to `FALSE`, and check it inside
  normal control flow, not `#ifdef` (docs/STYLEGUIDE.md:271-280).
- `include/constants/config_changes.h` defines the `BATTLE_CONFIG_DEFINITIONS(F)`
  X-macro table used for test config introspection (`WITH_CONFIG` in tests).
  It currently only lists `B_*` configs; a `P_EVOLUTION_TIER_GATING` enum entry
  could be added to a similar table if tests want
  `WITH_CONFIG(P_EVOLUTION_TIER_GATING, TRUE/FALSE)` parametrization, following
  the `F(CONFIG_NAME, memberName, (type, default))` pattern (line 6+).

---

## 6. `struct SpeciesInfo` and adding a per-species field

- Definition: include/pokemon.h:391-520, comment marks total size `/*0xC4*/`
  (~196 bytes without form/overworld-data pointers). Key fields for this
  feature:
  - base stats (391-397), types (398), catchRate (399), expYield (401),
    EV yields bitfield (402-408), items (409-410), genderRatio (411),
    eggCycles (412), friendship (413), growthRate (414), eggGroups (415),
    abilities (416), pokédex fields (420-428), graphics (429-467), flags
    bitfield `u32 isRestrictedLegendary:1; ... padding4:8` (469-491),
    shadow settings (492-495), move data pointers (497-501):
    ```c
    const struct LevelUpMove *levelUpLearnset;
    const u16 *teachableLearnset;
    const u16 *eggMoveLearnset;
    const struct Evolution *evolutions;
    const u16 *formSpeciesIdTable;
    const struct FormChange *formChangeTable;
    ```
- Feasibility of adding `.tier`/`.evoGateTier`:
  - **Struct space is not the problem.** There are plenty of spare bits —
    `padding4:8` (line 490) or the 4 unused `evYield_...:2` padding bits
    (line 407-408) could hold a 4-bit tier tag, or a plain `u8` field added
    with zero ROM-cost concerns (GBA struct, `gSpeciesInfo` is rodata).
  - **Maintenance is the problem.** Species data is hand-written C in 9
    generation files; adding a field means editing every species entry (or at
    least the ones that can be evolution targets) in
    `src/data/pokemon/species_info/gen_*_families.h`. There is no codegen for
    these files (unlike learnsets, which are generated from JSON via
    `tools/learnset_helpers/make_*` — see §2).
  - Alternatives that avoid touching every entry:
    1. Reuse the existing `struct Evolution` entry: add a new method
       (`EVO_TIER_GATE`) or encode the tier in an existing field — not
       recommended, it pollutes the "what triggers evolution" data.
    2. Add a small static lookup table keyed by target species
       (`static const struct TierGate sEvoTierGates[] = { {SPECIES_DRAGONAIR, TIER_PU}, ... }`)
       next to the gate logic, mirroring `sLevelCapFlagMap` in src/caps.c. This
       is the least invasive and keeps modification to one file.
    3. Add `u8 tier:4` to `struct SpeciesInfo` and set `.tier = TIER_PU,` per
       species entry (bulk edit across gen files). More discoverable in data,
       more diff churn; also note the ROM's `gSpeciesInfo` is indexed by species
       including forms, so form-species entries would need tier tags too
       (`SPECIES_*_ALOLA` etc. live in the same tables).
  - Because `gSpeciesInfo` is indexed by `SanitizeSpeciesId(species)` (used by
    all accessors like `GetSpeciesEvolutions`), a per-species `.tier` read via
    `gSpeciesInfo[SanitizeSpeciesId(targetSpecies)].tier` is trivial.
  - Design docs (`plastic_ox/plasticox_encounters_v1.md`) already define the
    tier list: LC, PU, NU, RU, UU, UUBL, OU with badge counts 1-8.

## 7. Nincada → Ninjask + Shedinja special flow

Two pieces:

### Data (gen_3_families.h:3739-3743) — shown in §2
`EVO_SPLIT_FROM_EVO` with `param = SPECIES_NINJASK` (the "trigger" post-evo
species) and `targetSpecies = SPECIES_SHEDINJA`.

### Runtime: `CreateShedinja` (src/evolution_scene.c:551-599)

Called only from `EVOSTATE_END` of the normal (non-trade) evolution task, and
only if the evolution was not cancelled (evolution_scene.c:839-840):

```c
            if (!gTasks[taskId].tEvoWasStopped)
                CreateShedinja(gTasks[taskId].tPreEvoSpecies, gTasks[taskId].tPostEvoSpecies, mon);
```

Core loop (evolution_scene.c:557-569):

```c
    for (u32 i = 0; evolutions[i].method != EVOLUTIONS_END; i++)
    {
        if (evolutions[i].method == EVO_SPLIT_FROM_EVO
         && evolutions[i].param == postEvoSpecies
         && gPartiesCount[B_TRAINER_PLAYER] < PARTY_SIZE
         && DoesMonMeetAdditionalConditions(mon, evolutions[i].params, NULL, PARTY_SIZE, NULL, CHECK_EVO))
        {
            struct Pokemon *shedinja = &gParties[B_TRAINER_PLAYER][gPartiesCount[B_TRAINER_PLAYER]];
            CopyMon(...); SetMonData(..., MON_DATA_SPECIES, &evolutions[i].targetSpecies); ...
```

Key facts for tier-gating:
- `EVO_SPLIT_FROM_EVO` entries are **not** returned by `GetEvolutionTargetSpecies`
  in any mode (no mode's switch handles that method) — Shedinja is generated as
  a side effect of the Ninjask evolution completing, through
  `DoesMonMeetAdditionalConditions` (which is where `IF_BAG_ITEM_COUNT` ball
  consumption happens; bag removal actually occurs at src/pokemon.c:4418-4424
  during `DO_EVO`, but `CreateShedinja` calls with `CHECK_EVO` so only the check
  branch runs here — the ball is a bag item, not held item, and is removed by
  `RemoveBagItem(ball, 1)` inside `CreateShedinja` itself at line 578).
- **Tier-gate implication:** if Shedinja has its own tier (LC/PU/etc.), the gate
  must be applied in `CreateShedinja` too — otherwise a badge-locked Shedinja
  appears for free as a side effect. Cleanest: reuse the same
  `CanMonEvolveToSpecies(SPECIES_SHEDINJA, ...)` helper inside the
  `EVO_SPLIT_FROM_EVO` branch (before `CopyMon`), or add a `CONDITIONS`-style
  `IF_*` condition for the split entry.
- The split evo is also skipped if the party is full (`gPartiesCount < PARTY_SIZE`).

---

## Key hooks for implementation

1. **Single choke point:** the post-switch tail of `GetEvolutionTargetSpecies`
   (src/pokemon.c:4619-4631, before `return targetSpecies;`) — a
   `targetSpecies`-based `CanMonEvolveToSpecies()` check gates every mode at
   once. Second best: one check per mode loop next to
   `DoesMonMeetAdditionalConditions` calls at src/pokemon.c:4487, 4511, 4537,
   4564, 4590, 4609 (needed separately if `EVO_MODE_ITEM_CHECK` should keep
   reporting "usable" for locked tiers).
2. **New `IF_*`-style condition or helper:** add `IF_TIER_UNLOCKED` to
   `enum EvolutionConditions` (include/constants/pokemon.h:272-319) evaluated in
   `DoesMonMeetAdditionalConditions` (src/pokemon.c:4107-4434), or a standalone
   `CanMonEvolveToSpecies(targetSpecies)` helper; either plugs into all modes
   and `CreateShedinja`.
3. **Badge count:** reuse the pattern in src/shop_criteria.c:49-58
   (`FlagGet(FLAG_BADGE01_GET + i)`) or the flag-map pattern in
   src/caps.c:10-21 (`sLevelCapFlagMap`, `FLAG_BADGE01_GET`…`FLAG_BADGE08_GET`,
   flags defined include/constants/flags.h:1359-1367).
4. **Per-species tier data:** add a `static const sEvoTierGateMap[]` lookup
   table keyed by target species (least invasive, single file) or add
   `u8 tier`/bitfield to `struct SpeciesInfo` (include/pokemon.h:391-520) and
   edit `src/data/pokemon/species_info/gen_*_families.h` per species (no codegen
   exists for these files).
5. **Config:** `#define P_EVOLUTION_TIER_GATING FALSE` in
   include/config/pokemon.h "Evolution settings" section; default OFF per
   docs/STYLEGUIDE.md:442-454; check in normal control flow per
   docs/STYLEGUIDE.md:271-280. (Optionally add to an X-macro config table in
   include/constants/config_changes.h for `WITH_CONFIG` test parametrization.)
6. **Blocked-evolution UX:** replace the `SPECIES_NONE` fallbacks in callers
   (party_menu.c:5862 / 4824-4825, scrcmd.c:3312-3317, item_use.c:1371)
   with a gated-reason message; `gText_PkmnStoppedEvolving` /
   `gText_PkmnIsEvolving` live in src/battle_message.c:1452-1455 and the
   cancellation flow in src/evolution_scene.c:849-875.
7. **Shedinja special case:** apply the same gate inside `CreateShedinja`
   (src/evolution_scene.c:551-599, split branch at 557-568).
8. **Level lowering rule:** the design doc says "if normal evolution level >
   unlocked tier cap, lower the evolution level to the cap" — this is a
   per-species data change in the `.evolutions` tables (e.g. Dratini 30→20 for
   PU, gen_1_families.h:20353) that could be automated by a script, since the
   tables are plain text with `{EVO_LEVEL, N, SPECIES_X}` patterns.
9. **Tests:** existing evolution tests use `test/battle/evolution_tracker.c`
   patterns; badge flags can be set in tests with `FlagSet(...)` (test/battle/badge_boost.c:15-17
   shows badge-flag tests; `FLAG_SET` macro in include/test/battle.h:1016).
