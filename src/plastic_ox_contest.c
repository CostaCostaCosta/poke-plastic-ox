#include "global.h"
#include "battle.h"
#include "event_data.h"
#include "item.h"
#include "main.h"
#include "overworld.h"
#include "pokemon.h"
#include "random.h"
#include "safari_zone.h"
#include "script.h"
#include "string_util.h"
#include "plastic_ox_contest.h"
#include "constants/items.h"
#include "constants/maps.h"
#include "constants/plastic_ox_flags.h"

#define CONTEST_BALLS 20
#define CONTEST_STEPS 500

enum { PENDING_NONE = 0, PENDING_AFTER_BATTLE, PENDING_FINISH };

extern const u8 PlasticOxContest_EventScript_AfterBattle[];
extern const u8 PlasticOxContest_EventScript_Finish[];

// A contest never removes or replaces a member of the player's normal party.
// Saving is unavailable until the exact retained specimen has been delivered.
static EWRAM_DATA bool8 sRunning = FALSE;
static EWRAM_DATA bool8 sHasCatch = FALSE;
static EWRAM_DATA bool8 sNewCatch = FALSE;
static EWRAM_DATA u8 sPendingScript = PENDING_NONE;
static EWRAM_DATA struct Pokemon sRetained = {0};
static EWRAM_DATA struct Pokemon sCandidate = {0};
static EWRAM_DATA u16 sRivalScore = 0;

bool32 PlasticOxContest_IsActive(void)
{
    return sRunning
        && gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_NATIONAL_PARK_NORMAL_HNS)
        && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_NATIONAL_PARK_NORMAL_HNS);
}

bool32 PlasticOxContest_HasSession(void)
{
    return sRunning || sHasCatch;
}

static u16 ScoreMon(struct Pokemon *mon)
{
    u32 species = GetMonData(mon, MON_DATA_SPECIES);
    const struct SpeciesInfo *info = &gSpeciesInfo[species];
    u32 stats = info->baseHP + info->baseAttack + info->baseDefense
              + info->baseSpeed + info->baseSpAttack + info->baseSpDefense;
    u32 ivs = GetMonData(mon, MON_DATA_HP_IV) + GetMonData(mon, MON_DATA_ATK_IV)
            + GetMonData(mon, MON_DATA_DEF_IV) + GetMonData(mon, MON_DATA_SPEED_IV)
            + GetMonData(mon, MON_DATA_SPATK_IV) + GetMonData(mon, MON_DATA_SPDEF_IV);
    u32 maxHp = GetMonData(mon, MON_DATA_MAX_HP);
    return stats / 2 + GetMonData(mon, MON_DATA_LEVEL) * 4 + ivs / 3
         + (maxHp ? 40 * GetMonData(mon, MON_DATA_HP) / maxHp : 0);
}

void PlasticOxContest_Status(void)
{
    gSpecialVar_Result = sRunning ? 1 : sHasCatch ? 2 : 0;
    gSpecialVar_0x8006 = gNumSafariBalls;
    ConvertIntToDecimalStringN(gStringVar1, gNumSafariBalls, STR_CONV_MODE_LEFT_ALIGN, 2);
}

void PlasticOxContest_Start(void)
{
    gSpecialVar_Result = FALSE;
    if (PlasticOxContest_HasSession() || FlagGet(FLAG_POX_CONTEST_PRIZE_PENDING)
     || IsPlayerPartyAndPokemonStorageFull())
        return;
    sRunning = TRUE;
    sHasCatch = FALSE;
    sNewCatch = FALSE;
    gNumSafariBalls = CONTEST_BALLS;
    gSafariZoneStepCounter = CONTEST_STEPS;
    sRivalScore = 300 + Random() % 41;
    gSpecialVar_Result = TRUE;
}

void PlasticOxContest_StageCatch(struct Pokemon *mon)
{
    sCandidate = *mon;
    sNewCatch = TRUE;
}

void PlasticOxContest_AcceptCatch(void)
{
    if (sNewCatch && (gSpecialVar_0x8004 || !sHasCatch))
    {
        sRetained = sCandidate;
        sHasCatch = TRUE;
    }
    sNewCatch = FALSE;
}

void PlasticOxContest_EndBattle(void)
{
    // Battle-end teardown reclaims the global script context, so the catch
    // dialog cannot be scripted here. Defer to the next field step, matching
    // CB2_EndSafariBattle's plain CB2_ReturnToField shape.
    if (sNewCatch)
        sPendingScript = PENDING_AFTER_BATTLE;
    else if (gNumSafariBalls == 0)
        sPendingScript = PENDING_FINISH;
    SetMainCallback2(CB2_ReturnToField);
}

bool32 PlasticOxContest_TakeStep(void)
{
    if (!PlasticOxContest_IsActive())
        return FALSE;
    if (sPendingScript != PENDING_NONE)
    {
        const u8 *script = (sPendingScript == PENDING_AFTER_BATTLE)
            ? PlasticOxContest_EventScript_AfterBattle
            : PlasticOxContest_EventScript_Finish;
        sPendingScript = PENDING_NONE;
        if (script == PlasticOxContest_EventScript_AfterBattle)
        {
            GetMonData(&sCandidate, MON_DATA_NICKNAME, gStringVar1);
            if (sHasCatch)
                GetMonData(&sRetained, MON_DATA_NICKNAME, gStringVar2);
            gSpecialVar_0x8005 = sHasCatch;
        }
        ScriptContext_SetupScript(script);
        return TRUE;
    }
    if (gSafariZoneStepCounter != 0)
        gSafariZoneStepCounter--;
    if (gSafariZoneStepCounter != 0 && gNumSafariBalls != 0)
        return FALSE;
    ScriptContext_SetupScript(PlasticOxContest_EventScript_Finish);
    return TRUE;
}

void PlasticOxContest_Judge(void)
{
    u16 score = sHasCatch ? ScoreMon(&sRetained) : 0;
    gSpecialVar_Result = 0;
    if (!PlasticOxContest_HasSession())
        return;
    // Capacity was checked on entry. Retain the specimen and prohibit saves if
    // another script has nevertheless filled the last space during the event.
    if (sHasCatch && GiveCapturedMonToPlayer(&sRetained) == MON_CANT_GIVE)
    {
        sRunning = FALSE;
        gSpecialVar_Result = 4;
        return;
    }
    if (sHasCatch)
    {
        gSpecialVar_Result = score >= sRivalScore ? 1 : score + 40 >= sRivalScore ? 2 : 3;
        if (gSpecialVar_Result == 1)
            FlagSet(FLAG_POX_CONTEST_PRIZE_PENDING);
    }
    ConvertIntToDecimalStringN(gStringVar1, score, STR_CONV_MODE_LEFT_ALIGN, 3);
    sRunning = FALSE;
    sHasCatch = FALSE;
    sNewCatch = FALSE;
    sPendingScript = PENDING_NONE;
    gNumSafariBalls = 0;
    gSafariZoneStepCounter = 0;
}

void PlasticOxContest_OnMapChange(void)
{
    if (PlasticOxContest_HasSession())
        PlasticOxContest_Judge();
}

void PlasticOxContest_ClaimPrize(void)
{
    gSpecialVar_Result = FALSE;
    if (FlagGet(FLAG_POX_CONTEST_PRIZE_PENDING) && AddBagItem(ITEM_SUN_STONE, 1))
    {
        FlagClear(FLAG_POX_CONTEST_PRIZE_PENDING);
        gSpecialVar_Result = TRUE;
    }
}
