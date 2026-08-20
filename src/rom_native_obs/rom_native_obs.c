#include "global.h"
#include "battle.h"
#include "battle_controllers.h"
#include "move.h"
#include "pokemon.h"
#include "rom_native_obs.h"

// ============================================================================
// Debug/test-only encoder for the canonical RomBattleState schema.
//
// Mirrors metamon/metamon/rom_native_obs/schema.py. Reads the battle
// engine globals (gBattleMons, gParties, gBattleWeather, gSideStatuses,
// gFieldStatuses, gLastMoves, gBattleTurnCounter, ...) and produces a
// deterministic, fixed-width representation.
//
// Notes:
//  - This encoder is omniscient: it reveals everything the ROM knows
//    (moves_revealed / hp_known / item_revealed / ability_revealed are set
//    for every valid slot). A knowledge model can clear those bits for
//    opponent slots if needed.
//  - Schema v2 (Gen3): adds per-mon item (u16) + ability (u8) and the
//    item_revealed / ability_revealed masks, plus SIDE_COND_SPIKES (=8,
//    derived from gBattleStruct->hazardsQueue). The side-condition single
//    enum stays lossy: only the highest-priority active condition is
//    reported per side (spikes is lowest priority, see
//    SideConditionToSchema).
// ============================================================================

// Canonical schema IDs (schema.py ID tables)
enum
{
    // Status
    RNO_STATUS_NONE = 0,
    RNO_STATUS_SLEEP = 1,
    RNO_STATUS_POISON = 2,
    RNO_STATUS_BURN = 3,
    RNO_STATUS_FREEZE = 4,
    RNO_STATUS_PARALYSIS = 5,
    RNO_STATUS_TOXIC = 6,
    RNO_STATUS_FAINT = 7,
    RNO_STATUS_UNKNOWN = 8,

    // Weather
    RNO_WEATHER_NONE = 0,
    RNO_WEATHER_RAIN = 1,
    RNO_WEATHER_SUN = 2,
    RNO_WEATHER_SANDSTORM = 3,
    RNO_WEATHER_HAIL = 4,
    RNO_WEATHER_SNOW = 5,
    RNO_WEATHER_FOG = 6,
    RNO_WEATHER_UNKNOWN = 7,

    // Side conditions
    RNO_SIDE_COND_NONE = 0,
    RNO_SIDE_COND_REFLECT = 1,
    RNO_SIDE_COND_LIGHTSCREEN = 2,
    RNO_SIDE_COND_SAFEGUARD = 3,
    RNO_SIDE_COND_MIST = 4,
    RNO_SIDE_COND_TAILWIND = 5,
    RNO_SIDE_COND_AURORA_VEIL = 6,
    RNO_SIDE_COND_UNKNOWN = 7,
    RNO_SIDE_COND_SPIKES = 8,

    // Field effects
    RNO_FIELD_NONE = 0,
    RNO_FIELD_GRAVITY = 1,
    RNO_FIELD_TRICK_ROOM = 2,
    RNO_FIELD_WONDER_ROOM = 3,
    RNO_FIELD_MAGIC_ROOM = 4,
    RNO_FIELD_MUD_SPORT = 5,
    RNO_FIELD_WATER_SPORT = 6,
    RNO_FIELD_UNKNOWN = 7,

    // Volatile effects
    RNO_EFFECT_NONE = 0,
    RNO_EFFECT_CONFUSION = 1,
    RNO_EFFECT_INFATUATION = 2,
    RNO_EFFECT_LEECH_SEED = 3,
    RNO_EFFECT_LOCK = 4,
    RNO_EFFECT_NIGHTMARE = 5,
    RNO_EFFECT_CURSE = 6,
    RNO_EFFECT_UNKNOWN = 7,

    // Move categories
    RNO_CATEGORY_NONE = 0,
    RNO_CATEGORY_PHYSICAL = 1,
    RNO_CATEGORY_SPECIAL = 2,
    RNO_CATEGORY_STATUS = 3,
    RNO_CATEGORY_UNKNOWN = 4,
};

static u32 MinU32(u32 a, u32 b)
{
    return (a < b) ? a : b;
}

static u8 ClampU8(u32 value)
{
    return (value > 255) ? 255 : (u8)value;
}

// ----------------------------------------------------------------------------
// Normalization helpers (schema float ranges mapped to 0-255)
// ----------------------------------------------------------------------------

static u8 HpToFraction(u32 hp, u32 maxHp)
{
    if (maxHp == 0)
        return 0;
    return ClampU8((hp * 255) / maxHp);
}

static u8 PpToFraction(u32 pp, u32 maxPp)
{
    if (maxPp == 0)
        return 0;
    return ClampU8((pp * 255) / maxPp);
}

static u8 LevelToNorm(u32 level)
{
    return ClampU8((level * 255) / 100);
}

// base power / 200 (schema base_power/200 clipped to 1.0) -> 0-255
static u8 PowerToU8(u32 power)
{
    return ClampU8((power * 255) / 200);
}

// accuracy percent / 100 -> 0-255; ROM stores accuracy 0 for always-hit moves
static u8 AccuracyToU8(u32 accuracy)
{
    if (accuracy == 0)
        return 255;
    return ClampU8((accuracy * 255) / 100);
}

// turn / 200 (schema turn_norm clips at 1.0) -> 0-255
static u8 TurnToNorm(u32 turn)
{
    return ClampU8((turn * 255) / 200);
}

// ----------------------------------------------------------------------------
// Categorical mappers (ROM values -> canonical schema IDs)
// ----------------------------------------------------------------------------

static u8 Status1ToSchema(u32 status1)
{
    if (status1 & STATUS1_SLEEP)
        return RNO_STATUS_SLEEP;
    if (status1 & STATUS1_TOXIC_POISON)
        return RNO_STATUS_TOXIC;
    if (status1 & STATUS1_POISON)
        return RNO_STATUS_POISON;
    if (status1 & STATUS1_BURN)
        return RNO_STATUS_BURN;
    if (status1 & STATUS1_FREEZE)
        return RNO_STATUS_FREEZE;
    if (status1 & STATUS1_PARALYSIS)
        return RNO_STATUS_PARALYSIS;
    if (status1 & STATUS1_FROSTBITE) // no canonical ID in the schema
        return RNO_STATUS_UNKNOWN;
    return RNO_STATUS_NONE;
}

static u8 WeatherToSchema(u16 battleWeather)
{
    if (battleWeather & B_WEATHER_RAIN)
        return RNO_WEATHER_RAIN;
    if (battleWeather & B_WEATHER_SUN)
        return RNO_WEATHER_SUN;
    if (battleWeather & B_WEATHER_SANDSTORM)
        return RNO_WEATHER_SANDSTORM;
    if (battleWeather & B_WEATHER_HAIL)
        return RNO_WEATHER_HAIL;
    if (battleWeather & B_WEATHER_SNOW)
        return RNO_WEATHER_SNOW;
    if (battleWeather & B_WEATHER_FOG)
        return RNO_WEATHER_FOG;
    if (battleWeather & B_WEATHER_STRONG_WINDS) // strong winds not in the schema
        return RNO_WEATHER_UNKNOWN;
    return RNO_WEATHER_NONE;
}

// Lossy single-enum: returns the highest-priority active condition; spikes is
// checked last, so screens/safeguard/mist/tailwind/aurora-veil win over spikes.
// (Spikes layers and simultaneous conditions are not representable in the schema
// and are collapsed: layers 1-3 -> RNO_SIDE_COND_SPIKES.)
static u8 SideConditionToSchema(u32 sideStatus, enum BattleSide side)
{
    if (sideStatus & SIDE_STATUS_REFLECT)
        return RNO_SIDE_COND_REFLECT;
    if (sideStatus & SIDE_STATUS_LIGHTSCREEN)
        return RNO_SIDE_COND_LIGHTSCREEN;
    if (sideStatus & SIDE_STATUS_SAFEGUARD)
        return RNO_SIDE_COND_SAFEGUARD;
    if (sideStatus & SIDE_STATUS_MIST)
        return RNO_SIDE_COND_MIST;
    if (sideStatus & SIDE_STATUS_TAILWIND)
        return RNO_SIDE_COND_TAILWIND;
    if (sideStatus & SIDE_STATUS_AURORA_VEIL)
        return RNO_SIDE_COND_AURORA_VEIL;
    if (gBattleStruct != NULL)
    {
        u32 i;
        for (i = 0; i < HAZARDS_MAX_COUNT; i++)
        {
            if (gBattleStruct->hazardsQueue[side][i] == HAZARDS_SPIKES)
                return RNO_SIDE_COND_SPIKES;
        }
    }
    return RNO_SIDE_COND_NONE;
}

static u8 FieldEffectToSchema(u32 fieldStatuses)
{
    if (fieldStatuses & STATUS_FIELD_GRAVITY)
        return RNO_FIELD_GRAVITY;
    if (fieldStatuses & STATUS_FIELD_TRICK_ROOM)
        return RNO_FIELD_TRICK_ROOM;
    if (fieldStatuses & STATUS_FIELD_WONDER_ROOM)
        return RNO_FIELD_WONDER_ROOM;
    if (fieldStatuses & STATUS_FIELD_MAGIC_ROOM)
        return RNO_FIELD_MAGIC_ROOM;
    if (fieldStatuses & STATUS_FIELD_MUDSPORT)
        return RNO_FIELD_MUD_SPORT;
    if (fieldStatuses & STATUS_FIELD_WATERSPORT)
        return RNO_FIELD_WATER_SPORT;
    return RNO_FIELD_NONE;
}

static u8 VolatilesToEffect(const struct Volatiles *volatiles)
{
    if (volatiles->confusionTurns != 0)
        return RNO_EFFECT_CONFUSION;
    if (volatiles->infatuation != 0)
        return RNO_EFFECT_INFATUATION;
    if (volatiles->leechSeed != 0)
        return RNO_EFFECT_LEECH_SEED;
    if (volatiles->lockOn != 0)
        return RNO_EFFECT_LOCK;
    if (volatiles->nightmare != 0)
        return RNO_EFFECT_NIGHTMARE;
    if (volatiles->cursed != 0)
        return RNO_EFFECT_CURSE;
    return RNO_EFFECT_NONE;
}

static u8 CategoryToSchema(enum DamageCategory category)
{
    switch (category)
    {
    case DAMAGE_CATEGORY_PHYSICAL:
        return RNO_CATEGORY_PHYSICAL;
    case DAMAGE_CATEGORY_SPECIAL:
        return RNO_CATEGORY_SPECIAL;
    case DAMAGE_CATEGORY_STATUS:
        return RNO_CATEGORY_STATUS;
    default:
        return RNO_CATEGORY_NONE;
    }
}

// Map the ROM Type enum to the canonical schema Type IDs.
// The ROM enum (pokeemerald-expansion) differs from schema.py for BUG/GHOST/STEEL:
//   ROM:   BUG=7, GHOST=8, STEEL=9, MYSTERY=10
//   schema: BIRD=7, BUG=8, GHOST=9, STEEL=10
// Types beyond the schema range (TYPE_STELLAR=20) are mapped to TYPE_NONE.
static u8 TypeToSchema(enum Type type)
{
    switch (type)
    {
    case TYPE_NORMAL:
        return 1;
    case TYPE_FIGHTING:
        return 2;
    case TYPE_FLYING:
        return 3;
    case TYPE_POISON:
        return 4;
    case TYPE_GROUND:
        return 5;
    case TYPE_ROCK:
        return 6;
    case TYPE_BUG:
        return 8;
    case TYPE_GHOST:
        return 9;
    case TYPE_STEEL:
        return 10;
    case TYPE_FIRE:
        return 11;
    case TYPE_WATER:
        return 12;
    case TYPE_GRASS:
        return 13;
    case TYPE_ELECTRIC:
        return 14;
    case TYPE_PSYCHIC:
        return 15;
    case TYPE_ICE:
        return 16;
    case TYPE_DRAGON:
        return 17;
    case TYPE_DARK:
        return 18;
    case TYPE_FAIRY:
        return 19;
    default: // TYPE_NONE, TYPE_MYSTERY, TYPE_STELLAR, ...
        return 0;
    }
}

// ----------------------------------------------------------------------------
// Move feature encoding
// ----------------------------------------------------------------------------

static void EncodeMoveFeatures(struct RomBattlePokemon *slot, u8 moveIndex, enum Move move, u32 currentPp, u8 ppBonuses)
{
    if (move == MOVE_NONE || move >= MOVES_COUNT_ALL)
    {
        slot->moves[moveIndex] = MOVE_NONE;
        slot->move_categories[moveIndex] = RNO_CATEGORY_NONE;
        slot->move_types[moveIndex] = 0;
        slot->move_bp[moveIndex] = 0;
        slot->move_acc[moveIndex] = 0;
        slot->move_pri[moveIndex] = 0;
        slot->move_pp[moveIndex] = 0;
        return;
    }

    slot->moves[moveIndex] = (u16)move;
    slot->move_categories[moveIndex] = CategoryToSchema(GetMoveCategory(move));
    slot->move_types[moveIndex] = TypeToSchema(GetMoveType(move));
    slot->move_bp[moveIndex] = PowerToU8(GetMovePower(move));
    slot->move_acc[moveIndex] = AccuracyToU8(GetMoveAccuracy(move));
    slot->move_pri[moveIndex] = (s8)GetMovePriority(move);
    slot->move_pp[moveIndex] = PpToFraction(currentPp, CalculatePPWithBonus(move, ppBonuses, moveIndex));
}

static u8 GetBaseStat(enum Species species, u8 statIndex)
{
    const struct SpeciesInfo *info;
    u32 index = (species < NUM_SPECIES) ? species : SPECIES_NONE;

    info = &gSpeciesInfo[index];
    switch (statIndex)
    {
    case 0: return info->baseAttack;
    case 1: return info->baseSpAttack;
    case 2: return info->baseDefense;
    case 3: return info->baseSpDefense;
    case 4: return info->baseSpeed;
    case 5: return info->baseHP;
    default: return 0;
    }
}

// ----------------------------------------------------------------------------
// Slot encoders
// ----------------------------------------------------------------------------

// Active battler (from gBattleMons). The slot is expected to be zeroed already.
static void EncodeActiveBattler(struct RomBattlePokemon *slot, enum BattlerId battler)
{
    const struct BattlePokemon *battleMon = &gBattleMons[battler];
    u32 i;

    slot->valid = 1;
    slot->species = (u16)battleMon->species;
    slot->type_1 = TypeToSchema(battleMon->types[0]);
    slot->type_2 = (battleMon->types[1] != battleMon->types[0]) ? TypeToSchema(battleMon->types[1]) : 0;

    slot->hp_fraction = HpToFraction(battleMon->hp, battleMon->maxHP);
    slot->level_norm = LevelToNorm(battleMon->level);

    for (i = 0; i < 6; i++)
        slot->base_stats[i] = GetBaseStat(battleMon->species, i);

    // statStages holds stage + 6 (0..12) for each battle stat, indexed by the
    // Stat enum (STAT_ATK..STAT_EVASION). Reorder to the schema's boost order
    // [atk, spa, def, spd, spe, acc, eva] (the ROM array order is
    // atk, def, spe, spa, spd, acc, eva).
    slot->stat_boosts[0] = battleMon->statStages[STAT_ATK];
    slot->stat_boosts[1] = battleMon->statStages[STAT_SPATK];
    slot->stat_boosts[2] = battleMon->statStages[STAT_DEF];
    slot->stat_boosts[3] = battleMon->statStages[STAT_SPDEF];
    slot->stat_boosts[4] = battleMon->statStages[STAT_SPEED];
    slot->stat_boosts[5] = battleMon->statStages[STAT_ACC];
    slot->stat_boosts[6] = battleMon->statStages[STAT_EVASION];

    for (i = 0; i < ROM_NATIVE_OBS_NUM_MOVES; i++)
        EncodeMoveFeatures(slot, i, battleMon->moves[i], battleMon->pp[i], battleMon->ppBonuses);

    slot->status = Status1ToSchema(battleMon->status1);
    if (battleMon->hp == 0)
        slot->status = RNO_STATUS_FAINT;

    slot->effect = VolatilesToEffect(&battleMon->volatiles);

    // Schema v2: item/ability. Debug encoder is omniscient: reveals both.
    slot->item = (u16)battleMon->item;
    slot->ability = (u8)battleMon->ability;

    slot->fainted = (battleMon->hp == 0) ? 1 : 0;
    slot->moves_revealed = 1;
    slot->hp_known = 1;
    slot->item_revealed = 1;
    slot->ability_revealed = 1;
}

// Party Pokémon (player switches / revealed opponents). Slot zeroed already.
static void EncodePartyMon(struct RomBattlePokemon *slot, struct Pokemon *partyMon)
{
    u32 species;
    u32 hp;
    u32 maxHp;
    u32 level;
    u32 status1;
    u32 ppBonuses;
    u32 i;

    if (GetMonData(partyMon, MON_DATA_SANITY_IS_EGG))
        return;
    species = GetMonData(partyMon, MON_DATA_SPECIES);
    if (species == SPECIES_NONE)
        return;

    slot->valid = 1;
    slot->species = (u16)species;
    slot->type_1 = TypeToSchema(GetSpeciesType(species, 0));
    slot->type_2 = (GetSpeciesType(species, 1) != GetSpeciesType(species, 0)) ? TypeToSchema(GetSpeciesType(species, 1)) : 0;

    hp = GetMonData(partyMon, MON_DATA_HP);
    maxHp = GetMonData(partyMon, MON_DATA_MAX_HP);
    level = GetMonData(partyMon, MON_DATA_LEVEL);

    slot->hp_fraction = HpToFraction(hp, maxHp);
    slot->level_norm = LevelToNorm(level);

    for (i = 0; i < 6; i++)
        slot->base_stats[i] = GetBaseStat(species, i);

    // Party members are at default stat stages (stage + 6 == DEFAULT_STAT_STAGE).
    for (i = 0; i < 7; i++)
        slot->stat_boosts[i] = DEFAULT_STAT_STAGE;

    ppBonuses = GetMonData(partyMon, MON_DATA_PP_BONUSES);
    for (i = 0; i < ROM_NATIVE_OBS_NUM_MOVES; i++)
        EncodeMoveFeatures(slot, i, GetMonData(partyMon, MON_DATA_MOVE1 + i), GetMonData(partyMon, MON_DATA_PP1 + i), ppBonuses);

    status1 = GetMonData(partyMon, MON_DATA_STATUS);
    slot->status = Status1ToSchema(status1);
    if (hp == 0)
        slot->status = RNO_STATUS_FAINT;

    slot->effect = RNO_EFFECT_NONE; // party mons have no volatile battle effects

    // Schema v2: item/ability from the party slot (species-default ability for
    // the mon's ability number). Debug encoder is omniscient: reveals both.
    slot->item = (u16)GetMonData(partyMon, MON_DATA_HELD_ITEM);
    slot->ability = (u8)GetMonAbility(partyMon);

    slot->fainted = (hp == 0) ? 1 : 0;
    slot->moves_revealed = 1;
    slot->hp_known = 1;
    slot->item_revealed = 1;
    slot->ability_revealed = 1;
}

// ----------------------------------------------------------------------------
// Main entry point
// ----------------------------------------------------------------------------

void EncodeRomBattleState(struct RomBattleState *out, u8 playerBattler, u8 opponentBattler)
{
    struct Pokemon *playerParty;
    struct Pokemon *opponentParty;
    u32 playerTrainer;
    u32 opponentTrainer;
    u32 playerActiveIndex;
    u32 opponentActiveIndex;
    u32 playerPartyCount;
    u32 opponentPartyCount;
    u32 remaining;
    u32 i;
    bool32 playerValid;
    bool32 opponentValid;
    u32 partyIdx;

    if (out == NULL)
        return;

    memset(out, 0, sizeof(*out));

    playerValid = (playerBattler < gBattlersCount);
    opponentValid = (opponentBattler < gBattlersCount);

    // ------------------------------------------------------------------
    // Global features
    // ------------------------------------------------------------------
    out->global.weather = WeatherToSchema(gBattleWeather);
    out->global.field_effect = FieldEffectToSchema(gFieldStatuses);
    out->global.player_side_cond = SideConditionToSchema(gSideStatuses[B_SIDE_PLAYER], B_SIDE_PLAYER);
    out->global.opponent_side_cond = SideConditionToSchema(gSideStatuses[B_SIDE_OPPONENT], B_SIDE_OPPONENT);

    if (playerValid)
    {
        out->global.player_prev_move = (gLastMoves[playerBattler] == MOVE_UNAVAILABLE) ? MOVE_NONE : gLastMoves[playerBattler];
        out->global.forced_switch = (gBattleMons[playerBattler].hp == 0) ? 1 : 0;
    }
    if (opponentValid)
        out->global.opponent_prev_move = (gLastMoves[opponentBattler] == MOVE_UNAVAILABLE) ? MOVE_NONE : gLastMoves[opponentBattler];

    out->global.turn_norm = TurnToNorm(gBattleTurnCounter);

    // ------------------------------------------------------------------
    // Pokémon slots
    // ------------------------------------------------------------------
    if (playerValid)
    {
        playerTrainer = GetBattlerTrainer(playerBattler);
        playerParty = GetBattlerParty(playerBattler);
        playerActiveIndex = gBattlerPartyIndexes[playerBattler];
        playerPartyCount = MinU32(gPartiesCount[playerTrainer], PARTY_SIZE);

        // Slot 0: player's active battler
        EncodeActiveBattler(&out->pokemon[ROM_NATIVE_OBS_SLOT_PLAYER_ACTIVE], playerBattler);

        // Slots 1-5: the rest of the player's party, in party order.
        for (i = 0; i < ROM_NATIVE_OBS_NUM_SWITCHES; i++)
        {
            partyIdx = (i < playerActiveIndex) ? i : (i + 1);
            if (partyIdx < playerPartyCount)
                EncodePartyMon(&out->pokemon[ROM_NATIVE_OBS_SLOT_SWITCH_0 + i], &playerParty[partyIdx]);
        }

        // Legal actions 0-3: move slots
        if (IsBattlerAlive(playerBattler))
        {
            const struct BattlePokemon *battleMon = &gBattleMons[playerBattler];
            for (i = 0; i < ROM_NATIVE_OBS_NUM_MOVES; i++)
            {
                if (battleMon->moves[i] != MOVE_NONE && battleMon->pp[i] > 0)
                    out->legal_action_mask[i] = 1;
            }
        }

        // Legal actions 4-8: switch slots (same party mons as slots 1-5)
        for (i = 0; i < ROM_NATIVE_OBS_NUM_SWITCHES; i++)
        {
            partyIdx = (i < playerActiveIndex) ? i : (i + 1);
            if (partyIdx < playerPartyCount
             && out->pokemon[ROM_NATIVE_OBS_SLOT_SWITCH_0 + i].valid
             && !out->pokemon[ROM_NATIVE_OBS_SLOT_SWITCH_0 + i].fainted)
                out->legal_action_mask[ROM_NATIVE_OBS_NUM_MOVES + i] = 1;
        }
    }

    if (opponentValid)
    {
        opponentTrainer = GetBattlerTrainer(opponentBattler);
        opponentParty = GetBattlerParty(opponentBattler);
        opponentActiveIndex = gBattlerPartyIndexes[opponentBattler];
        opponentPartyCount = MinU32(gPartiesCount[opponentTrainer], PARTY_SIZE);

        // Slot 6: opponent's active battler
        EncodeActiveBattler(&out->pokemon[ROM_NATIVE_OBS_SLOT_OPPONENT_ACTIVE], opponentBattler);

        // Slots 7-12: revealed opponents (rest of the opponent's party)
        for (i = 0; i < ROM_NATIVE_OBS_NUM_REVEALED; i++)
        {
            partyIdx = (i < opponentActiveIndex) ? i : (i + 1);
            if (partyIdx < opponentPartyCount)
                EncodePartyMon(&out->pokemon[ROM_NATIVE_OBS_SLOT_REVEALED_OPP_0 + i], &opponentParty[partyIdx]);
        }

        // opponents_remaining = alive party members / 6 -> 0-255
        remaining = 0;
        for (i = 0; i < opponentPartyCount; i++)
        {
            if (GetMonData(&opponentParty[i], MON_DATA_HP) > 0)
                remaining++;
        }
        out->global.opponents_remaining = ClampU8((remaining * 255) / PARTY_SIZE);
    }
}
