# GEN3 ROM State — ec/rom-native-gen3

Repo: /home/eddie/repos/poke-plastic-ox (pokeemerald-expansion fork).
Purpose: document battle-state storage + mechanics-config deltas needed for a
production (non-omniscient) gen3 ROM-native observation encoder, implement the
schema v2 C encoder, and build the load-bearing items enum mapping for metamon.

## Task checkboxes
- [x] 1. `plastic_ox/agent/gen3_items_expansion_enum.json` (expansion items.h x Showdown items.ts, gen<=3 held items) — 96 entries, committed
- [x] 2. Battle state storage doc (struct BattlePokemon, globals, reveal hooks)
- [ ] 3. Mechanics config audit (config/battle.h GEN_LATEST -> GEN_3 recommended patch table)
- [ ] 4. C encoder schema v2 (include/rom_native_obs.h + src/rom_native_obs/rom_native_obs.c)
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

