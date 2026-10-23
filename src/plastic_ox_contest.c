#include "global.h"
#include "battle.h"
#include "clock.h"
#include "event_data.h"
#include "item.h"
#include "load_save.h"
#include "main.h"
#include "overworld.h"
#include "pokemon.h"
#include "random.h"
#include "rtc.h"
#include "safari_zone.h"
#include "script.h"
#include "string_util.h"
#include "plastic_ox_contest.h"
#include "constants/items.h"
#include "constants/maps.h"
#include "constants/plastic_ox_contest.h"
#include "constants/plastic_ox_flags.h"

#define CONTEST_BALLS 20
#define CONTEST_STEPS 500

enum { PENDING_NONE = 0, PENDING_AFTER_BATTLE, PENDING_FINISH };

extern const u8 PlasticOxContest_EventScript_AfterBattle[];
extern const u8 PlasticOxContest_EventScript_Finish[];

// Saving is unavailable while the party is reduced or a catch awaits delivery.
static EWRAM_DATA bool8 sRunning = FALSE;
static EWRAM_DATA bool8 sPartyReduced = FALSE;
static EWRAM_DATA bool8 sHasCatch = FALSE;
static EWRAM_DATA bool8 sNewCatch = FALSE;
static EWRAM_DATA u8 sPendingScript = PENDING_NONE;
static EWRAM_DATA u8 sChosenPartyIndex = 0;
static EWRAM_DATA u8 sEntrySide = 0;
static EWRAM_DATA u16 sOriginalSportBalls = 0;
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

static bool32 HasPendingPrize(void)
{
    return FlagGet(FLAG_POX_CONTEST_PRIZE_PENDING)
        || FlagGet(FLAG_POX_CONTEST_EVERSTONE_PENDING)
        || FlagGet(FLAG_POX_CONTEST_SITRUS_PENDING)
        || FlagGet(FLAG_POX_CONTEST_ORAN_PENDING);
}

void PlasticOxContest_CheckEntry(void)
{
    DoTimeBasedEvents();
    if (HasPendingPrize())
        gSpecialVar_Result = POX_CONTEST_ENTRY_PRIZE_PENDING;
    else if (PlasticOxContest_HasSession())
        gSpecialVar_Result = POX_CONTEST_ENTRY_IN_PROGRESS;
    else if (FlagGet(FLAG_POX_DAILY_PARK_CONTEST))
        gSpecialVar_Result = POX_CONTEST_ENTRY_USED;
    else if (GetDayOfWeek() != WEEKDAY_TUE && GetDayOfWeek() != WEEKDAY_THU && GetDayOfWeek() != WEEKDAY_SAT)
        gSpecialVar_Result = POX_CONTEST_ENTRY_CLOSED;
    else if (IsPlayerPartyAndPokemonStorageFull() || !CheckBagHasSpace(ITEM_SPORT_BALL, CONTEST_BALLS))
        gSpecialVar_Result = POX_CONTEST_ENTRY_NO_ROOM;
    else
        gSpecialVar_Result = POX_CONTEST_ENTRY_OPEN;
}

static void RestorePartyAndBalls(void)
{
    u16 currentBalls;

    if (!sPartyReduced)
        return;

    SavePlayerPartyMon(sChosenPartyIndex, &gParties[B_TRAINER_PLAYER][0]);
    LoadPlayerParty();
    sPartyReduced = FALSE;

    currentBalls = CountTotalItemQuantityInBag(ITEM_SPORT_BALL);
    if (currentBalls > sOriginalSportBalls)
        RemoveBagItem(ITEM_SPORT_BALL, currentBalls - sOriginalSportBalls);
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
    u8 chosen = gSpecialVar_0x8004;
    struct Pokemon mon;

    PlasticOxContest_CheckEntry();
    if (gSpecialVar_Result != POX_CONTEST_ENTRY_OPEN)
        return;
    if (chosen >= gPartiesCount[B_TRAINER_PLAYER]
     || GetMonData(&gParties[B_TRAINER_PLAYER][chosen], MON_DATA_SPECIES_OR_EGG) == SPECIES_EGG
     || GetMonData(&gParties[B_TRAINER_PLAYER][chosen], MON_DATA_HP) == 0)
    {
        gSpecialVar_Result = POX_CONTEST_ENTRY_INVALID_MON;
        return;
    }
    sOriginalSportBalls = CountTotalItemQuantityInBag(ITEM_SPORT_BALL);
    if (!AddBagItem(ITEM_SPORT_BALL, CONTEST_BALLS))
    {
        gSpecialVar_Result = POX_CONTEST_ENTRY_NO_ROOM;
        return;
    }

    mon = gParties[B_TRAINER_PLAYER][chosen];
    SavePlayerParty();
    memset(gParties[B_TRAINER_PLAYER], 0, sizeof(gParties[B_TRAINER_PLAYER]));
    gParties[B_TRAINER_PLAYER][0] = mon;
    gPartiesCount[B_TRAINER_PLAYER] = 1;
    sChosenPartyIndex = chosen;
    sEntrySide = gSpecialVar_0x8007;
    sPartyReduced = TRUE;
    sRunning = TRUE;
    sHasCatch = FALSE;
    sNewCatch = FALSE;
    sPendingScript = PENDING_NONE;
    gNumSafariBalls = CONTEST_BALLS;
    gSafariZoneStepCounter = CONTEST_STEPS;
    sRivalScore = 300 + Random() % 41;
    FlagSet(FLAG_POX_DAILY_PARK_CONTEST);
    gSpecialVar_Result = POX_CONTEST_ENTRY_OPEN;
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
    else if (gNumSafariBalls == 0 || gBattleOutcome == B_OUTCOME_LOST)
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
    RestorePartyAndBalls();
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
        else if (gSpecialVar_Result == 2)
            FlagSet(FLAG_POX_CONTEST_EVERSTONE_PENDING);
        else
            FlagSet(FLAG_POX_CONTEST_SITRUS_PENDING);
    }
    else
        FlagSet(FLAG_POX_CONTEST_ORAN_PENDING);
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
    // The gate's arrival script presents the results after loading. Preserve
    // the session until then so leaving by either real warp cannot lose them.
    if (PlasticOxContest_IsActive()
     && GetDestinationWarpMapHeader() != Overworld_GetMapHeaderByGroupAndId(
            MAP_GROUP(MAP_GATE_NATIONAL_PARK_HNS), MAP_NUM(MAP_GATE_NATIONAL_PARK_HNS)))
        PlasticOxContest_Judge();
}

void PlasticOxContest_GetEntrySide(void)
{
    gSpecialVar_Result = sEntrySide;
}

void PlasticOxContest_ClaimPrize(void)
{
    u16 item;
    u16 flag;

    gSpecialVar_Result = FALSE;
    if (FlagGet(FLAG_POX_CONTEST_PRIZE_PENDING))
    {
        item = ITEM_SUN_STONE;
        flag = FLAG_POX_CONTEST_PRIZE_PENDING;
    }
    else if (FlagGet(FLAG_POX_CONTEST_EVERSTONE_PENDING))
    {
        item = ITEM_EVERSTONE;
        flag = FLAG_POX_CONTEST_EVERSTONE_PENDING;
    }
    else if (FlagGet(FLAG_POX_CONTEST_SITRUS_PENDING))
    {
        item = ITEM_SITRUS_BERRY;
        flag = FLAG_POX_CONTEST_SITRUS_PENDING;
    }
    else if (FlagGet(FLAG_POX_CONTEST_ORAN_PENDING))
    {
        item = ITEM_ORAN_BERRY;
        flag = FLAG_POX_CONTEST_ORAN_PENDING;
    }
    else
        return;

    CopyItemName(item, gStringVar2);
    if (AddBagItem(item, 1))
    {
        FlagClear(flag);
        gSpecialVar_Result = TRUE;
    }
}
