# GEN3 ROM State — ec/rom-native-gen3

Repo: /home/eddie/repos/poke-plastic-ox (pokeemerald-expansion fork).
Purpose: document battle-state storage + mechanics-config deltas needed for a
production (non-omniscient) gen3 ROM-native observation encoder, implement the
schema v2 C encoder, and build the load-bearing items enum mapping for metamon.

## Task checkboxes
- [x] 1. `plastic_ox/agent/gen3_items_expansion_enum.json` (expansion items.h x Showdown items.ts, gen<=3 held items) — 96 entries, committed
- [x] 2. Battle state storage doc (struct BattlePokemon, globals, reveal hooks)
- [x] 3. Mechanics config audit (config/battle.h GEN_LATEST -> GEN_3 recommended patch table)
- [x] 4. C encoder schema v2 (include/rom_native_obs.h + src/rom_native_obs/rom_native_obs.c)
- [ ] 5. metamon `rom-native/ROM_NATIVE_OBSERVATION.md` appendix (edit only, no commit there)

## Progress log
- 2026-08-: branch `ec/rom-native-gen3` created from HEAD; scaffold committed.

## Section 1 — items mapping (committed)
- 96 gen<=3 held items mapped from expansion enum + `gen<=3` in base `data/items.ts` (all base entries have explicit `gen`).
- 13 gen<=3 base items unmapped (absent from expansion items.h): gen2 obsolete berries
  (berry, bitterberry, burntberry, goldberry, iceberry, mintberry, miracleberry, mysteryberry,
  przcureberry, psncureberry), pinkbow, polkadotbow, generic mail.
- Known gen3 held items NOT mappable under the strict base-data `gen<=3` rule (documented exceptions):
  - blueorb/redorb — base items.ts says gen 6 (ORAS re-release); expansion has ITEM_RED_ORB=290, ITEM_BLUE_ORB=291.
  - soothebell, expshare, smokeball, luckincense, pureincense — absent from this Showdown's base items.ts (expansion has them).
  - fullincense, oddincense, waveincense, rockincense, roseincense — base data says gen 4 though Hoenn items.

## Section 2 — Battle state storage (battle observation targets)

All file:line references are for the working tree of this repo (poke-plastic-ox,
fork of pokeemerald-expansion). Line numbers may drift slightly after edits; the
quoted code is authoritative.

### 2.1 struct BattlePokemon — per-active-mon battle state

Defined in `include/pokemon.h:338` (this fork; upstream expansion places it in
`include/pokemon.h` as well). Full struct quoted verbatim:

```c
struct BattlePokemon
{
    enum Species species;
    u16 attack;
    u16 defense;
    u16 speed;
    u16 spAttack;
    u16 spDefense;
    enum Move moves[MAX_MON_MOVES];
    u32 hpIV:5;
    u32 attackIV:5;
    u32 defenseIV:5;
    u32 speedIV:5;
    u32 spAttackIV:5;
    u32 spDefenseIV:5;
    u32 abilityNum:2;
    s8 statStages[NUM_BATTLE_STATS];
    enum Ability ability;
    enum Type types[3];
    u8 pp[MAX_MON_MOVES];
    u16 hp;
    u8 level;
    u8 friendship;
    u16 maxHP;
    enum Item item;
    u8 nickname[POKEMON_NAME_LENGTH + 1];
    u8 ppBonuses;
    u8 otName[PLAYER_NAME_LENGTH + 1];
    u32 experience;
    u32 personality;
    u32 status1;
    struct Volatiles volatiles;
    u32 otId;
    u8 metLevel:7;
    u8 isShiny:1;
    u8 affectionHearts;
};
```

Key fields for schema v2:
- `species` — `enum Species`; in this fork the enum is `__attribute__((packed))`
  starting at 1 (SPECIES_NONE=0) and species 1..386 are National Dex order
  (Skitty=300, Rayquaza=384, Deoxys=386; see include/constants/species.h:311,396,399).
  Width: u16.
- `moves[MAX_MON_MOVES]` — `enum Move`, u16 per move (MOVE_PSYCHO_BOOST=354 is the
  last gen3 move; MOVE ids are u16).
- `ability` — `enum Ability`, u8 in practice (ABILITIES_COUNT_GEN3=77).
- `item` — `enum Item`, u16 in practice (ITEM_ENIGMA_BERRY=574 is the last
  berry; item enum is `enum __attribute__((packed)) Item` in include/constants/items.h).
- `status1` — u32 non-volatile status bitmask (STATUS1_* in
  include/constants/battle.h:169-190; sleep uses bits 0-2 as turn counter).
- `volatiles` — volatile condition bitfield struct expanded from the
  `VOLATILE_DEFINITIONS(F)` macro list in include/constants/battle.h:202-...;
  includes confusionTurns, flinched, uproarTurns, wrapped, infatuation,
  substitute, destinyBond, nightmare, curse, leechSeed, perishSong, yawn,
  imprison, ingrain, etc.
- `statStages[NUM_BATTLE_STATS]` — s8 stat stage modifiers (NUM_BATTLE_STATS:
  include/constants/battle.h has STAT_* enum; see 2.3).
- `types[3]` — `enum Type` (Type enum in include/constants/pokemon.h:7-29;
  gen3 types end at TYPE_DARK=18; TYPE_FAIRY=19 is post-gen3 but still present
  in the enum).

### 2.2 Volatiles expansion

`struct Volatiles` (include/pokemon.h:328) is generated from
`VOLATILE_DEFINITIONS` in include/constants/battle.h:201-...; each
`F(VOLATILE_X, name, (type, bits))` line becomes a bitfield. Notable for
observation: `leechSeed`, `substitute`, `confusionTurns`, `wrapped`/
`wrappedMove` (binding), `destinyBond`, `perishSong`, `yawn`, `imprison`,
`focusEnergy`, `semiInvulnerable` (fly/dig), `waterSport`/`mudSport`,
`foresight`, `minimize`, `root` (Ingrain), `saltCure`, `torment`, `rage`.

### 2.3 stat stage / stat enum

include/constants/battle.h:91-92:
```c
    NUM_STATS,            // HP, ATK, DEF, SPD, SpAtk, SpDef
    STAT_ACC = NUM_STATS, // Only in battles.
    STAT_EVASION,         // Only in battles.
    NUM_BATTLE_STATS
```
So NUM_BATTLE_STATS = 8 (ATK..SpDef stages [0..6] + ACC + EVASION).

### 2.4 Global battle arrays (declarations, all in include/battle.h)

| Global | Type | Decl line |
|---|---|---|
| gBattleMons | `struct BattlePokemon gBattleMons[MAX_BATTLERS_COUNT]` | include/battle.h:997 |
| gBattlerPartyIndexes | `u16 gBattlerPartyIndexes[MAX_BATTLERS_COUNT]` | include/battle.h:989 |
| gBattleWeather | `u16 gBattleWeather` | include/battle.h:1038 |
| gSideStatuses | `u32 gSideStatuses[NUM_BATTLE_SIDES]` | include/battle.h:1030 |
| gFieldStatuses | `u32 gFieldStatuses` | include/battle.h:1065 |
| gBattleStruct | `struct BattleStruct *gBattleStruct` (EWRAM, init src/battle_main.c:210) | include/battle.h:1043 |
| gLastUsedItem | `u16 gLastUsedItem` | include/battle.h:1005 |
| gLastUsedAbility | `enum Ability gLastUsedAbility` | include/battle.h:1006 |
| gBattleScripting | `struct BattleScripting gBattleScripting` | include/battle.h:1042 |

Semantics:
- `gBattleMons[battler]` — active mon state (see 2.1). Updated from the party
  `struct Pokemon` on switch-in by `PokemonToBattleMon` (include/pokemon.h:843,
  implementation src/pokemon.c).
- `gBattlerPartyIndexes[battler]` — party slot index (into gPlayerParty /
  gEnemyParty) of each active battler.
- `gBattleWeather` — `u16` bitmask of active weathers (B_WEATHER_* in
  include/constants/battle.h:483-...), not a single enum value; also
  `gBattleStruct->weatherDuration`.
- `gSideStatuses[side]` — per-side u32 flags: SIDE_STATUS_REFLECT,
  LIGHTSCREEN, SAFEGUARD, MIST, TAILWIND, AURORA_VEIL, LUCKY_CHANT,
  DAMAGE_NON_TYPES, RAINBOW, SEA_OF_FIRE, SWAMP (include/constants/battle.h:392-400);
  hazards (Spikes etc.) are NOT in gSideStatuses in this fork — they live in
  `enum Hazards` (include/constants/battle.h:404-409) stored per-side in
  `gBattleStruct->hazardsQueue[NUM_BATTLE_SIDES][HAZARDS_MAX_COUNT]`
  (include/battle.h:722; queue-managed by IsHazardOnSide etc.,
  src/battle_util.c:10159-10223). Spikes presence/layers for the schema v2
  SIDE_COND_SPIKES bit = count of HAZARDS_SPIKES entries in
  gBattleStruct->hazardsQueue[side].
- `gFieldStatuses` — u32 field-wide flags (trick room, gravity, grudge, fairy
  lock, etc.).
- `gBattleStruct` — the big per-battle dynamic struct (include/battle.h:576-...) —
  contains battle flags, event states, partyState (per-trainer per-party-slot
  state incl. `usedHeldItem` u16 at include/battle.h:548), battlerState
  (include/battle.h:506, incl. `usedEjectItem`, `usedMicleBerry` bits),
  chosenItem[MAX_BATTLERS_COUNT] (u16), choicedMove, weatherDuration, etc.

### 2.5 Constants boundaries (with file:line)

| Boundary | Value (this fork) | Location |
|---|---|---|
| SPECIES_NONE | 0 | include/constants/species.h:11 |
| SPECIES_SKITTY | 300 | include/constants/species.h:311 |
| SPECIES_RAYQUAZA | 384 | include/constants/species.h:396 |
| SPECIES_DEOXYS | 386 | include/constants/species.h:399 |
| NUM_SPECIES | = SPECIES_EGG (gen3 no egg species? — egg is after deoxys forms) | include/constants/species.h:1698 |
| MOVE_NONE | 0 | include/constants/moves.h:6 |
| MOVE_PSYCHO_BOOST | 354 | include/constants/moves.h:386 |
| MOVES_COUNT_GEN3 | 355 (MOVE_PSYCHO_BOOST+1) | include/constants/moves.h:387 |
| ABILITY_NONE | 0 | include/constants/abilities.h:6 |
| ABILITY_AIR_LOCK | 76 | include/constants/abilities.h:82 |
| ABILITIES_COUNT_GEN3 | 77 | include/constants/abilities.h:83 |
| ITEM_NONE | 0 | include/constants/items.h:36 (enum Item) |
| ITEM_ENIGMA_BERRY | 574 | include/constants/items.h:704 |
| TYPE_NONE / TYPE_FAIRY / NUMBER_OF_MON_TYPES | 0 / 19 / 21 | include/constants/pokemon.h:7,26,28 |
| NUM_BATTLE_STATS | 8 | include/constants/battle.h:91-94 |
| MAX_BATTLERS_COUNT / NUM_BATTLE_SIDES | 4 / 2 | include/constants/battle.h:75,91 |

For the ROM-native observed schema the canonical ids are passed as raw enum
values: species u16 (1..386 gen3), move u16 (1..354 gen3), item u16 (expansion
enum values, e.g. leftovers=472, choiceband=442 — see
gen3_items_expansion_enum.json), ability u8 (1..76 gen3).

### 2.6 Where item/ability reveals are observable (production tracker hooks)

Debug-omniscient encoder reads gBattleMons[battler].item/.ability directly, so
it needs no reveal tracking. A production (non-omniscient) visibility tracker
would flip `item_revealed`/`ability_revealed` mask bits at these sites:

Item reveals:
- `gLastUsedItem = gBattleMons[battler].item;` — held-item/berry activation
  (src/battle_hold_effects.c:81; similar at battle_util.c:604,1518,1536,1552).
- `gLastUsedItem = item;` — berry scripts (src/battle_hold_effects.c:1239).
- `gLastUsedItem = gBattleResources->bufferB[...]<<8` — item used from bag /
  X-item (src/battle_util.c:574-580).
- `gLastUsedItem = GetBattlerPartyState(battler)->usedHeldItem;` — revealed
  held item at switch-out/Knock Off recovery (src/battle_util.c:3574,3584).
- `gLastUsedItem = gLastUsedBall;` + `gBattleMons[battler].item = gLastUsedItem;`
  — ball-throw and ball-catch (src/battle_util.c:3733-3735; also 791,801,833 safari).
- `partyState[..].usedHeldItem` (include/battle.h:548) is set when a held item
  is consumed (berry eaten, Air Balloon pop, etc.) — good "has used item" flag.

Ability reveals:
- `RecordAbilityBattle(battler, ability)` — canonical "AI now knows this
  ability" record, called when ability becomes observable (src/battle_util.c:1768
  IsAbilityAndRecord, 2920, 3014, 4829, 4868, 5469, 5799, 7419, 7513, 7915,
  7917; src/battle_hold_effects.c:68). Declared include/battle_ai_record.h:7.
- `gBattleScripting.abilityPopupOverwrite = <ability>` — on-screen ability popup
  shown to player (src/battle_script_commands.c:8984 trace/copy, 9150, 10622;
  src/battle_util.c:3558,4404,4541,4543,4629). The popup display itself is
  BS_ShowAbilityPopup (src/battle_script_commands.c:13117) and
  BS_UpdateAbilityPopup/UpdateAbilityPopup (13124, src/battle_interface.c:2636),
  driven by `BattleScript_AbilityPopUp` (src/battle_script_commands.c:10671).
- `gBattleMons[battler].ability` — current ability at switch-in = species
  default (visible to player for own mons; opponent only after reveal).
  `gBattleMons[battler].volatiles.overwrittenAbility` holds a changed ability
  (e.g. Trace/role play — see Cmd_trytrace around battle_script_commands.c:8975).

So the natural hooks for a production tracker are: `RecordAbilityBattle()`
(ability_revealed to AI) + `gBattleScripting.abilityPopupOverwrite` assignment
(ability_revealed to player) for abilities; `gLastUsedItem` assignment sites +
`partyState[x][y].usedHeldItem` for items.


## Section 3 — Mechanics config audit (GEN_LATEST → GEN_3)

### 3.1 Overview

`include/config/battle.h` has 319 `B_` config defines (this fork's count; the
older "~216" estimate predates the fork). The vast majority default to
`GEN_LATEST` (currently Gen 9-era mechanics). The ROM hack intends ORIGINAL
GEN3 RULES, so the defines below should move to `GEN_3` (or a specific value).
This section documents the materially relevant set for gen3 OU-style trainer
battles (damage formula, phys/spec split, crit, status, weather, abilities,
items, type chart, binding, confusion, paralysis, switching/turn order).

NOT APPLIED — this is a recommendation table only.

### 3.2 How the GEN_* tokens work

`GEN_1`..`GEN_9` are ordered constants (include/constants/battle.h); code does
`GetConfig(B_X) >= GEN_N` or `== GEN_N` comparisons. Setting a define to `GEN_3`
selects the gen3 branch throughout the battle engine and data tables.

### 3.3 Recommended patch table (battle engine, include/config/battle.h)

Damage formula / damage modifiers:

| Define (line) | Current | Recommended | Why (gen3 behavior) |
|---|---|---|---|
| B_CRIT_CHANCE (5) | GEN_LATEST | GEN_3 | gen3 crit chance per stage (1/16,1/8,1/4,1/3,1/2); LATEST adds gen6+ guarantees (Leek/etc.) |
| B_CRIT_MULTIPLIER (6) | GEN_LATEST | GEN_3 | gen6+ crit = 1.5x; gen3 = 2x |
| B_BURN_DAMAGE (28) | GEN_LATEST | GEN_3 | gen7+ burn = 1/16; gen3 = 1/8 |
| B_BINDING_DAMAGE (30) | GEN_LATEST | GEN_3 | gen6+ bind = 1/8; gen3 = 1/16 |
| B_PSYWAVE_DMG (31) | GEN_LATEST | GEN_3 | gen3 Psywave formula |
| B_HIDDEN_POWER_DMG (33) | GEN_LATEST | GEN_3 | gen6+ HP = 60 fixed; gen3 = IV-based 30-70 |
| B_ROUGH_SKIN_DMG (34) | GEN_LATEST | GEN_3 | gen4+ Rough Skin = 1/8; gen3 = 1/16 |
| B_KNOCK_OFF_DMG (35) | GEN_LATEST | GEN_3 | gen6+ Knock Off +50% when removing; gen3 = no boost |
| B_EXPLOSION_DEFENSE (37) | GEN_LATEST | GEN_3 | gen5+ no defense halving; gen3 Selfdestruct/Explosion halve Defense |
| B_SPORT_DMG_REDUCTION (36) | GEN_LATEST | GEN_3 | gen5+ 67%; gen3 = 50% |
| B_MULTIPLE_TARGETS_DMG (39) | GEN_LATEST | GEN_3 | gen4+ 75%; gen3 = 50% (full-field moves 100%) |
| B_SOUL_DEW_BOOST (229) | GEN_LATEST | GEN_3 | gen3-6 Soul Dew = Latis SpAtk/SpDef +; gen7+ = move power |
| B_PAYBACK_SWITCH_BOOST (32) | GEN_LATEST | GEN_3 | no Payback in gen3; harmless to set |
| B_PARENTAL_BOND_DMG (38), B_ATE_MULTIPLIER (194), B_TRANSISTOR_BOOST (181), B_GALE_WINGS (166) | GEN_LATEST | GEN_3 | abilities don't exist in gen3; no-op, set for consistency |

Move data / types / category:

| Define (line) | Current | Recommended | Why |
|---|---|---|---|
| B_PHYSICAL_SPECIAL_SPLIT (69) | GEN_LATEST | GEN_3 | **THE** gen3 mechanic: type-based physical/special (no per-move split) |
| B_UPDATED_MOVE_DATA (66) | GEN_LATEST | GEN_3 | move power/accuracy/PP/secondary chances per gen3 (gMovesInfo thresholds) |
| B_UPDATED_MOVE_TYPES (67) | GEN_LATEST | GEN_3 | move typings per gen3 (no Fairy moves; e.g. moves re-typed in gen6 revert) |
| B_UPDATED_MOVE_FLAGS (68) | GEN_LATEST | GEN_3 | move flags per gen3 |
| B_EXTRAPOLATED_MOVE_FLAGS (75) | TRUE | FALSE | TRUE adds "would-have" latest-game flags; gen3 purity wants FALSE |
| B_UPDATED_TYPE_MATCHUPS (45) | GEN_LATEST | GEN_3 | type chart per gen3 (gen2-5 chart; see 3.4) |
| B_RECOIL_IF_MISS_DMG (70) | GEN_LATEST | GEN_3 | gen5+ HJK miss = 1/2 max HP; gen3 = old recoil rule |
| B_HIDDEN_POWER_COUNTER (76) | GEN_LATEST | GEN_3 | pre-gen4 Counter/Mirror Coat treat HP as physical |
| B_BEAT_UP (116) | GEN_LATEST | GEN_3 | gen3 Beat Up formula (and announces party member names) |
| B_MULTI_HIT_CHANCE (9) | GEN_LATEST | GEN_3 | gen3 multi-hit distribution (2-5 hits, 37.5/37.5/12.5/12.5) |
| B_METRONOME_MOVES (114) | GEN_LATEST | GEN_3 | Metronome pulls only from gen3 move pool |

Status / ailment:

| Define (line) | Current | Recommended | Why |
|---|---|---|---|
| B_PARALYSIS_SPEED (7) | GEN_LATEST | GEN_3 | gen7+ speed /2; gen3 speed /4 (75% cut) |
| B_PARALYZE_ELECTRIC (43) | GEN_LATEST | GEN_3 | gen6+ Electric immune to paralysis; gen3 not |
| B_POWDER_GRASS (44) | GEN_LATEST | GEN_3 | gen6+ Grass immune to powder; gen3 not |
| B_CONFUSION_SELF_DMG_CHANCE (8) | GEN_LATEST | GEN_3 | gen7+ 33.3%; gen3 = 50% |
| B_SLEEP_TURNS (57) | GEN_LATEST | GEN_3 | gen5+ 2-4 turns; gen3 2-5 |
| B_BLIZZARD_HAIL (86) | GEN_LATEST | GEN_3 | gen4+ Blizzard never misses in hail; gen3 not |
| B_TOXIC_NEVER_MISS (84) | GEN_LATEST | GEN_3 | gen6+ Poison-type Toxic auto-hit; gen3 no |
| B_BURN_FACADE_DMG (29) | GEN_LATEST | GEN_3 | gen6+ no burn Atk drop on Facade; gen3 drop applies |
| B_HIT_THAW (118) | GEN_LATEST | GEN_3 | gen3 thaw rules (Fire move thaws) |
| B_SYNCHRONIZE_TOXIC (171) | GEN_LATEST | GEN_3 | gen5+ bad poison transfer; gen3 regular poison |
| B_FLASH_FIRE_FROZEN (170) | GEN_LATEST | GEN_3 | gen5+ Flash Fire works frozen; gen3 not |
| B_SHEER_COLD_IMMUNITY (47) | GEN_LATEST | GEN_3 | gen7+ Ice immune to Sheer Cold; gen3 not |
| B_STATUS_TYPE_IMMUNITY (49) | GEN_LATEST | GEN_3 | gen1-only; GEN_3 == GEN_LATEST (both off) — no change, noted for completeness |
| B_SKETCH_BANS (136) | GEN_LATEST | GEN_3 | gen9 sketch banlist; gen3 none (no-op for gen3 pool) |

Weather:

| Define (line) | Current | Recommended | Why |
|---|---|---|---|
| B_ABILITY_WEATHER (302) | GEN_LATEST | GEN_3 | **gen6+ ability weather 5 turns; gen3 permanent until replaced** (Drought/DD teams) |
| B_SANDSTORM_SPDEF_BOOST (303) | GEN_LATEST | GEN_3 | gen4+ Rock SpD 1.5x in sand; gen3 none |
| B_SANDSTORM_SOLAR_BEAM (304) | GEN_LATEST | GEN_3 | gen3+ SolarBeam weakened in sand (both ≥ GEN_3; no-op) |
| B_WEATHER_FORMS (176) | GEN_LATEST | GEN_3 | gen5+ Castform/Cherrim revert; gen3 stays transformed |
| B_SNOW_WARNING (307), B_OVERWORLD_SNOW (306), B_PREFERRED_ICE_WEATHER (308) | GEN_LATEST / B_ICE_WEATHER_BOTH | GEN_3 / B_ICE_WEATHER_HAIL | no Snow in gen3; hail only |

Turn order / switching / protection:

| Define (line) | Current | Recommended | Why |
|---|---|---|---|
| B_RECALC_TURN_AFTER_ACTIONS (62) | GEN_LATEST | GEN_3 | gen8+ dynamic speed; gen3 turn order fixed at turn start |
| B_FAINT_SWITCH_IN (63) | GEN_LATEST | GEN_3 | gen4+ faint-switch at end of turn; gen3 switch after each action |
| B_PROTECT_FAILURE_RATE (78) | GEN_LATEST | GEN_3 | gen5+ fail 1/3; gen2-4 fail 1/2 |
| B_TAUNT_TURNS (58) | GEN_LATEST | GEN_3 | gen3 Taunt = 2 turns |
| B_ENCORE_TURNS (59) | GEN_LATEST | GEN_3 | gen2-3 Encore = 2-6 turns |
| B_BINDING_TURNS (52) | GEN_LATEST | GEN_3 | gen5+ 4-5 turns; gen2-4 2-5 (Wrap gen3) |
| B_UPROAR_TURNS (53) | GEN_LATEST | GEN_3 | gen3-4 Uproar 2-5 turns |
| B_UPROAR (163) | GEN_LATEST | GEN_3 | gen3-4: Uproar wakes battlers before action/end of turn |
| B_DESTINY_BOND_FAIL (143) | GEN_LATEST | GEN_3 | gen7+ repeated-use fail; gen3 none |
| B_FOCUS_PUNCH_FAILURE (154) | GEN_LATEST | GEN_3 | gen4- rules: lose focus if move isn't Focus Punch |
| B_PURSUIT_TARGET (146) | GEN_LATEST | GEN_3 | gen4+ Pursuit hits any switcher; gen3 only targeted foe |
| B_BATON_PASS_TRAPPING (105) | GEN_LATEST | GEN_3 | gen5+ BP drops trapping; **gen3 BP passes Mean Look/Block** |
| B_BRICK_BREAK (108) | GEN_LATEST | GEN_3 | gen4+ breaks own screens; gen3 only target side |
| B_WISH_HP_SOURCE (109) | GEN_LATEST | GEN_3 | gen5+ Wish = user's max HP; gen3 = target's |
| B_ROOTED_GROUNDING (113) | GEN_LATEST | GEN_3 | gen4+ Ingrain grounds; gen3 not |
| B_RAGE_BUILDS (160) | GEN_LATEST | GEN_3 | gen3 Rage builds even on miss/fail; gen4+ only on hit |
| B_COUNTER_MIRROR_COAT_ALLY (158), B_COUNTER_TRY_HIT_PARTNER (159) | GEN_LATEST | GEN_3 | gen5+ ally exclusion; doubles-only nuance at GEN_4- |

Trapping / immunity / ability rules:

| Define (line) | Current | Recommended | Why |
|---|---|---|---|
| B_GHOSTS_ESCAPE (42) | GEN_LATEST | GEN_3 | gen6+ Ghost escapes traps; gen3 no |
| B_SHADOW_TAG_ESCAPE (168) | GEN_LATEST | GEN_3 | gen4+ both-Tag free escape; gen3 neither escapes (Wobbuffet) |
| B_OBLIVIOUS_TAUNT (173) | GEN_LATEST | GEN_3 | gen6+ Oblivious blocks Taunt; gen3 no |
| B_LEAF_GUARD_PREVENTS_REST (180) | GEN_LATEST | GEN_3 | gen5+ Leaf Guard blocks Rest in sun; gen3 no |
| B_UPDATED_INTIMIDATE (172) | GEN_LATEST | GEN_3 | gen8+ Inner Focus/etc. block Intimidate; gen3 no |
| B_MOODY_ACC_EVASION (169) | GEN_LATEST | GEN_3 | gen8+ Moody can't raise Acc/Eva; gen3 can (Moody not in gen3 — no-op) |
| B_STURDY (174) | GEN_LATEST | **keep ≥ GEN_5** | see 3.5 — expansion has NO pre-gen5 Sturdy branch; gen3-4 Sturdy (full-HP KO immunity) only exists at ≥ GEN_5 |
| B_ABILITY_TRIGGER_CHANCE (188) | GEN_LATEST | GEN_3 | gen3 Shed Skin/Cute Charm/etc. = 1/3 (gen4+ 30%) |
| B_MODERN_TRICK_CHOICE_LOCK (77) | GEN_LATEST | GEN_3 | gen5+ choicing after item swap; gen3 old lock |
| B_KLUTZ_FLING_INTERACTION (71), B_INFILTRATOR_SUBSTITUTE (198), B_DANCER_ORDER (199), B_STANCE_CHANGE_FAIL (167), B_DISGUISE_HP_LOSS (187), B_BATTLE_BOND (193), B_PROTEAN_LIBERO (184), B_INTREPID_SWORD (185), B_DAUNTLESS_SHIELD (186), B_WEAK_ARMOR_SPEED (183), B_TRANSISTOR_BOOST (181), B_GALE_WINGS (166), B_MIRROR_ARMOR_STICKY_WEB (196), B_DEFIANT_STICKY_WEB (195), B_ILLUMINATE_EFFECT (182), B_REDIRECT_ABILITY_ALLIES (179), B_REDIRECT_ABILITY_IMMUNITY (178), B_SYMBIOSIS_GEMS (177), B_PLUS_MINUS_INTERACTION (175), B_POWDER_OVERCOAT (197) | GEN_LATEST | GEN_3 | post-gen3 abilities; no-op with gen3 teams, set for consistency |

Items / item behavior (include/config/battle.h + item.h):

| Define (line) | Current | Recommended | Why |
|---|---|---|---|
| B_X_ITEMS_BUFF (222) | GEN_LATEST | GEN_3 | gen7+ X items +2 stages; gen3 +1 |
| B_MENTAL_HERB (224) | GEN_LATEST | GEN_3 | gen5+ cures Taunt/Encore/etc.; gen3 infatuation only |
| B_CONFUSE_BERRIES_HEAL (221) | GEN_LATEST | GEN_3 | gen3-6 Figy-type heal 1/8 at ≤50% HP (gen7+: 1/2 at 25%) |
| B_LIGHT_BALL_ATTACK_BOOST (11) | GEN_LATEST | GEN_3 | gen4+ Light Ball boosts physical too; gen3 special only |
| B_KNOCK_OFF_REMOVAL (137) | GEN_LATEST | GEN_3 | gen5+ removes item; **gen3 renders it unusable but keeps it** |
| B_SERENE_GRACE_BOOST (243) | GEN_LATEST | GEN_3 | gen5+ Serene Grace boosts King's Rock/Razor Fang flinch; gen3 not |
| B_RESTORE_HELD_BATTLE_ITEMS (228) | GEN_LATEST | GEN_3 | gen9+ restore after battle; gen3 consumed items stay consumed |
| B_STEAL_WILD_ITEMS (227) | GEN_LATEST | GEN_3 | gen9+ thief→bag; gen2-8 thief keeps the item |
| B_RETURN_STOLEN_NPC_ITEMS (226) | GEN_LATEST | GEN_3 | gen5+ return stolen NPC items; gen3 keeps |
| B_X_ITEMS_CROSSUSE (223) | TRUE | FALSE | gen3: X items only on current battler |
| B_TRAINERS_KNOCK_OFF_ITEMS (225) | TRUE | FALSE (optional) | vanilla gen3: trainers can't steal your items (design choice; recommended FALSE for purity) |
| I_TYPE_BOOST_POWER (include/config/item.h) | GEN_LATEST | GEN_3 | gen4+ 1.2x; gen3 Charcoal/etc. 1.1x, Sea Incense 1.05x |
| I_SITRUS_BERRY_HEAL (include/config/item.h) | GEN_LATEST | GEN_3 | gen3 Sitrus = +30 HP (gen4+ 25%) |
| I_LAX_INCENSE_BOOST (include/config/item.h) | GEN_LATEST | GEN_3 | gen3 Lax Incense evasion 5% (gen4+ 10%) |
| I_HEALTH_RECOVERY (include/config/item.h) | GEN_LATEST | GEN_3 | gen3 potion heal amounts |
| I_KEY_FOSSILS (include/config/item.h) | GEN_LATEST | GEN_3 | gen3 fossils are Key Items (gen4+ regular) |
| I_BERRY_EV_JUMP (include/config/item.h) | GEN_LATEST | GEN_3 | EV-lowering berries per gen3 (gen4-only special case off) |
| I_VITAMIN_EV_CAP (include/config/item.h) | GEN_LATEST | GEN_3 | gen8+ uncapped vitamins; gen3 cap 100 |
| I_GEM_BOOST_POWER (include/config/item.h) | GEN_LATEST | GEN_3 | no gems in gen3; no-op |
| I_REUSABLE_TMS (include/config/item.h) | FALSE | FALSE | already correct for gen3 (TMs one-time) |

Single-player / progression (not OU mechanics; set GEN_3 for full original feel):

| Define (line) | Current | Recommended | Why |
|---|---|---|---|
| B_WHITEOUT_MONEY (10) | GEN_LATEST | GEN_3 | gen3 RSE: half current money |
| B_BADGE_BOOST (22) | GEN_LATEST | GEN_3 | gen3 badges boost stats 1.1x (B_FLAG_BADGE_BOOST_* lines 251-255) |
| B_EXP_CATCH (14), B_TRAINER_EXP_MULTIPLIER (15), B_SPLIT_EXP (16), B_SCALED_EXP (17), B_UNEVOLVED_EXP_MULTIPLIER (18), B_MAX_LEVEL_EV_GAINS (24), B_RECALCULATE_STATS (25) | GEN_LATEST | GEN_3 | gen3 EXP/EV progression rules |
| B_MULTI_BATTLE_WHITEOUT (355), B_EVOLUTION_AFTER_WHITEOUT (356) | GEN_LATEST | GEN_3 | gen3 whiteout/evolution rules |

### 3.4 Type chart note

`gTypeEffectivenessTable` (src/data/types_info.h:11-41) is a static 21x21 table
with generation-conditional macros: STL_RS, PSN_RS, BUG_RS, PSY_RS, FIR_RS.
At `B_UPDATED_TYPE_MATCHUPS == GEN_3` the chart is the gen2-5 chart (exact gen3):
Ghost/Dark vs Steel = 0.5x, Ghost vs Psychic = 2.0x, Bug vs Poison = 0.5x,
Poison vs Bug = 1.0x, Ice vs Fire = 0.5x. Fairy/Stellar rows exist as types but
no gen3 species/move/ability yields them (Fairy row values are static in the
table; harmless). Keeping GEN_LATEST would apply gen6+ changes (Ghost/Dark vs
Steel 1.0x etc.) — wrong for gen3.

### 3.5 Sturdy deviation (important)

`B_STURDY` only has one code branch: `GetConfig(B_STURDY) >= GEN_5` →
survive 1 HP from full HP (src/battle_util.c:8039). There is NO pre-gen5
implementation in this fork. Real gen3-4 Sturdy (full-HP KO protection ≈ same
outcome) would be LOST if you set B_STURDY to GEN_3. Recommendation: leave
B_STURDY ≥ GEN_5 (e.g. GEN_LATEST) and document the deviation, or patch
battle_util.c to implement gen3-4 Sturdy explicitly.

### 3.6 Post-gen3 content gating

- **Species**: include/config/species_enabled.h — `P_GEN_1..3_POKEMON TRUE`,
  `P_GEN_4..9_POKEMON` default TRUE → set FALSE for gen3-only. Also
  `P_MEGA_EVOLUTIONS`, `P_PRIMAL_REVERSIONS`, `P_ULTRA_BURST_FORMS`,
  `P_GIGANTAMAX_FORMS`, `P_TERA_FORMS`, `P_FUSION_FORMS`, `P_REGIONAL_FORMS`
  (and P_ALOLAN/GALARIAN/HISUIAN/PALDEAN_FORMS) default TRUE → set FALSE.
  Species gating changes the saveblock (dex flags) — needs new save file.
  Note P_GEN_X gating disables whole evolution families, not just the new
  member (comment at top of file).
- **Moves**: NOT gen-gated. All expansion moves are always in `gMovesInfo`
  (src/data/moves_info.h); only `B_METRONOME_MOVES` (battle.h:114) restricts
  Metronome's pool. Post-gen3 moves remain legal on gen3 species unless the
  hack curates learnsets/TMs itself.
- **Items**: NOT gen-gated in the item enum (include/constants/items.h defines
  all 917 ITEM_ constants including gen4+ items). Gating is behavioral via
  `B_*`/`I_*` config (see 3.3) and availability (shop/wild tables, item
  importance flags). `include/config/caps.h` is only level/EV caps (EXP_CAP/
  LEVEL_CAP/EV_CAP, all NONE by default) — unrelated to gen gating.
- **Abilities**: all abilities defined in include/constants/abilities.h
  (ABILITIES_COUNT_GEN4..9 boundaries); per-gen ability behavior is driven by
  the B_* flags above, not by a gen gate. With gen3 species/moves only,
  post-gen3 abilities are unreachable except via hacked gimmicks.


## Section 4 — C encoder schema v2 (committed)
- include/rom_native_obs.h: struct RomBattlePokemon gains `u16 item` + `u8 ability`
  (appended after the 9 categoricals, before the move-feature arrays); masks gain
  `item_revealed` + `ability_revealed` (4 -> 6); side-cond comment documents
  spikes=8 lossiness.
- src/rom_native_obs/rom_native_obs.c: RNO_SIDE_COND_SPIKES=8; SideConditionToSchema
  gained an `enum BattleSide` param and reads gBattleStruct->hazardsQueue for
  HAZARDS_SPIKES (lowest priority, after screens/safeguard/mist/tailwind/aurora-veil);
  EncodeActiveBattler reads gBattleMons[battler].item/.ability;
  EncodePartyMon reads GetMonData(MON_DATA_HELD_ITEM) + GetMonAbility();
  omniscient masks set item_revealed/ability_revealed for valid slots.
- Compile check: arm-none-eabi-gcc NOT installed (per task fallback). Host syntax
  check passes: `gcc -fsyntax-only -std=gnu17 -iquote include -iquote include/gba
  -D'__attribute__(x)=' src/rom_native_obs/rom_native_obs.c` -> exit 0 (one benign
  pre-existing warning in include/data.h). Notes: -I would shadow glibc's
  <strings.h> with the project's include/strings.h, hence -iquote; attributes are
  blanked since host gcc rejects `target("arm")` (ARM_FUNC).
