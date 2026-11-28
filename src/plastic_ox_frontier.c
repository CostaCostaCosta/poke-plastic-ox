// Plastic Ox Battle Frontier rounds. See include/plastic_ox_frontier.h.
#include "global.h"
#include "battle_main.h"
#include "event_data.h"
#include "plastic_ox_frontier.h"
#include "pokemon.h"
#include "random.h"
#include "string_util.h"
#include "constants/abilities.h"
#include "constants/items.h"
#include "constants/moves.h"
#include "constants/opponents.h"
#include "constants/species.h"

struct PoxFrontierSet
{
    u16 species;
    u16 item;
    u16 ability;
    u8 nature;
    u8 evs[NUM_STATS];   // HP, Atk, Def, SpA, SpD, Spe (Showdown order)
    u8 ivs[NUM_STATS];
    u16 moves[MAX_MON_MOVES];
};

struct PoxFrontierPool
{
    const u16 (*teams)[PARTY_SIZE];
    u16 count;
};

#include "data/plastic_ox_frontier_teams.h"

// Showdown stat order mapped onto the box data fields.
static const u8 sEvFields[NUM_STATS] = {
    MON_DATA_HP_EV, MON_DATA_ATK_EV, MON_DATA_DEF_EV,
    MON_DATA_SPATK_EV, MON_DATA_SPDEF_EV, MON_DATA_SPEED_EV,
};
static const u8 sIvFields[NUM_STATS] = {
    MON_DATA_HP_IV, MON_DATA_ATK_IV, MON_DATA_DEF_IV,
    MON_DATA_SPATK_IV, MON_DATA_SPDEF_IV, MON_DATA_SPEED_IV,
};

static const u8 sTierName_LC[] = _("LITTLE CUP");
static const u8 sTierName_PU[] = _("PU");
static const u8 sTierName_NU[] = _("NU");
static const u8 sTierName_RU[] = _("RU");
static const u8 sTierName_UU[] = _("UU");
static const u8 sTierName_UUBL[] = _("UUBL");
static const u8 sTierName_Ubers[] = _("UBERS");
static const u8 *const sTierNames[POX_FRONTIER_TIER_COUNT] = {
    [POX_FRONTIER_TIER_LC] = sTierName_LC,
    [POX_FRONTIER_TIER_PU] = sTierName_PU,
    [POX_FRONTIER_TIER_NU] = sTierName_NU,
    [POX_FRONTIER_TIER_RU] = sTierName_RU,
    [POX_FRONTIER_TIER_UU] = sTierName_UU,
    [POX_FRONTIER_TIER_UUBL] = sTierName_UUBL,
    [POX_FRONTIER_TIER_UBERS] = sTierName_Ubers,
};

// Round state. Lives in RAM only: a round runs inside one attendant script, and
// the player cannot save until that script ends.
static EWRAM_DATA bool8 sActive = FALSE;
static EWRAM_DATA u8 sTier = 0;
static EWRAM_DATA u8 sWins = 0;
static EWRAM_DATA u16 sTeam = 0;
static EWRAM_DATA u16 sUsedTeams[POX_FRONTIER_ROUND_BATTLES] = {0};

u16 CheckRustboroGymLittleCupRules(void);
u16 CheckGoldenrodGymPURules(void);
u16 CheckEcruteakGymNURules(void);
u16 CheckFortreeGymRURules(void);
u16 CheckCinnabarGymUURules(void);
u16 CheckMossdeepGymUUBLRules(void);
u16 CheckFrontierUbersRules(void);

static u8 ScriptTier(void)
{
    return gSpecialVar_0x8004 < POX_FRONTIER_TIER_COUNT ? gSpecialVar_0x8004 : POX_FRONTIER_TIER_UBERS;
}

bool32 PoxFrontier_IsActive(void)
{
    return sActive;
}

bool32 PoxFrontier_IsTrainer(u16 trainerNum)
{
    return trainerNum >= TRAINER_PLASTIC_OX_FRONTIER_LC && trainerNum <= TRAINER_PLASTIC_OX_FRONTIER_UBERS;
}

// Special: the house's party rules for the tier in VAR_0x8004, with the gym codes
// (0 legal; 1 move, 2 item, 3 species, 4 duplicate, 5 ability, 6/7 Baton Pass).
u16 PoxFrontier_CheckRules(void)
{
    switch (ScriptTier())
    {
    case POX_FRONTIER_TIER_LC:   return CheckRustboroGymLittleCupRules();
    case POX_FRONTIER_TIER_PU:   return CheckGoldenrodGymPURules();
    case POX_FRONTIER_TIER_NU:   return CheckEcruteakGymNURules();
    case POX_FRONTIER_TIER_RU:   return CheckFortreeGymRURules();
    case POX_FRONTIER_TIER_UU:   return CheckCinnabarGymUURules();
    case POX_FRONTIER_TIER_UUBL: return CheckMossdeepGymUUBLRules();
    default:                     return CheckFrontierUbersRules();
    }
}

// Special: gStringVar3 = the name of the tier in VAR_0x8004.
void PoxFrontier_BufferTierName(void)
{
    StringCopy(gStringVar3, sTierNames[ScriptTier()]);
}

// Special: start a round in the tier in VAR_0x8004.
void PoxFrontier_Begin(void)
{
    sTier = ScriptTier();
    sWins = 0;
    sTeam = 0;
    sActive = TRUE;
}

// Special: pick this battle's team (never one already met this round) and put
// the battle number in gStringVar1.
void PoxFrontier_NextOpponent(void)
{
    const struct PoxFrontierPool *pool = &sPoxFrontierPools[sTier];
    u32 i, team;

    do
    {
        team = Random() % pool->count;
        for (i = 0; i < sWins; i++)
        {
            if (sUsedTeams[i] == team)
                break;
        }
    } while (i < sWins && pool->count > POX_FRONTIER_ROUND_BATTLES);
    sTeam = team;
    sUsedTeams[sWins] = team;
    ConvertIntToDecimalStringN(gStringVar1, sWins + 1, STR_CONV_MODE_LEFT_ALIGN, 1);
}

// Special: count a win. Returns TRUE once the round is complete; puts the wins so
// far in gStringVar1.
bool8 PoxFrontier_RecordWin(void)
{
    if (sWins < POX_FRONTIER_ROUND_BATTLES)
        sWins++;
    ConvertIntToDecimalStringN(gStringVar1, sWins, STR_CONV_MODE_LEFT_ALIGN, 1);
    return sWins >= POX_FRONTIER_ROUND_BATTLES;
}

// Special: the round is over (cleared, lost or retired).
void PoxFrontier_End(void)
{
    sActive = FALSE;
}

static u8 HighestPlayerLevel(void)
{
    u32 i;
    u8 highest = 1;

    for (i = 0; i < PARTY_SIZE; i++)
    {
        struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][i];
        u32 species = GetMonData(mon, MON_DATA_SPECIES_OR_EGG);

        if (species != SPECIES_NONE && species != SPECIES_EGG && GetMonData(mon, MON_DATA_LEVEL) > highest)
            highest = GetMonData(mon, MON_DATA_LEVEL);
    }
    return highest;
}

// The opponent meets the strongest POKéMON in the player's party, as every other
// Plastic Ox trainer does; the sets themselves are the tier's standard ADV sets.
u8 PoxFrontier_CreateParty(struct Pokemon *party)
{
    const u16 *team = sPoxFrontierPools[sTier].teams[sTeam];
    u8 level = HighestPlayerLevel();
    u32 i, j;

    ZeroPartyMons(party);
    for (i = 0; i < PARTY_SIZE; i++)
    {
        const struct PoxFrontierSet *set = &sPoxFrontierSets[team[i]];
        const struct SpeciesInfo *info = &gSpeciesInfo[set->species];
        u32 personality = Random32();
        u32 abilityNum = 0;
        u16 item = set->item;

        ModifyPersonalityForNature(&personality, set->nature);
        CreateMon(&party[i], set->species, level, personality, OTID_STRUCT_RANDOM_NO_SHINY);
        SetMonData(&party[i], MON_DATA_HELD_ITEM, &item);
        for (j = 0; j < MAX_MON_MOVES; j++)
            SetMonMoveSlot(&party[i], set->moves[j], j);
        for (j = 0; j < NUM_STATS; j++)
        {
            u32 ev = set->evs[j], iv = set->ivs[j];
            SetMonData(&party[i], sEvFields[j], &ev);
            SetMonData(&party[i], sIvFields[j], &iv);
        }
        for (j = 0; j < ARRAY_COUNT(info->abilities); j++)
        {
            if (info->abilities[j] == set->ability)
            {
                abilityNum = j;
                break;
            }
        }
        SetMonData(&party[i], MON_DATA_ABILITY_NUM, &abilityNum);
        CalculateMonStats(&party[i]);
    }
    return PARTY_SIZE;
}
