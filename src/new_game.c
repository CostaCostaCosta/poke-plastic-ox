#include "global.h"
#include "clock.h"
#include "new_game.h"
#include "random.h"
#include "pokemon.h"
#include "roamer.h"
#include "pokemon_size_record.h"
#include "script.h"
#include "lottery_corner.h"
#include "play_time.h"
#include "mauville_old_man.h"
#include "match_call.h"
#include "lilycove_lady.h"
#include "load_save.h"
#include "pokeblock.h"
#include "dewford_trend.h"
#include "berry.h"
#include "rtc.h"
#include "easy_chat.h"
#include "event_data.h"
#include "money.h"
#include "trainer_hill.h"
#include "trainer_tower.h"
#include "tv.h"
#include "coins.h"
#include "text.h"
#include "overworld.h"
#include "mail.h"
#include "battle_records.h"
#include "item.h"
#include "pokedex.h"
#include "apprentice.h"
#include "frontier_util.h"
#include "pokedex.h"
#include "save.h"
#include "link_rfu.h"
#include "main.h"
#include "contest.h"
#include "item_menu.h"
#include "pokemon_storage_system.h"
#include "pokemon_jump.h"
#include "decoration_inventory.h"
#include "secret_base.h"
#include "string_util.h"
#include "player_pc.h"
#include "field_specials.h"
#include "berry_powder.h"
#include "mystery_gift.h"
#include "union_room_chat.h"
#include "constants/map_groups.h"
#include "constants/items.h"
#include "difficulty.h"
#include "follower_npc.h"
#include "data.h"
#include "plastic_ox.h"
#include "constants/opponents.h"
#include "constants/flags.h"
#include "gba/m4a_internal.h"

extern const u8 EventScript_ResetAllMapFlags[];
extern const u8 EventScript_ResetAllMapFlagsFrlg[];

static void ClearFrontierRecord(void);
static void WarpToDemoStart(void);
static void ResetMiniGamesRecords(void);
static void ResetItemFlags(void);
static void ResetDexNav(void);
void GivePlasticOxPlayerParty(void);

static const u8 sPlasticOxPlayerName[] = _("P");

EWRAM_DATA bool8 gDifferentSaveFile = FALSE;
EWRAM_DATA bool8 gEnableContestDebugging = FALSE;

static const struct ContestWinner sContestWinnerPicDummy =
{
    .monName = _(""),
    .trainerName = _("")
};

void SetTrainerId(u32 trainerId, u8 *dst)
{
    dst[0] = trainerId;
    dst[1] = trainerId >> 8;
    dst[2] = trainerId >> 16;
    dst[3] = trainerId >> 24;
}

u32 GetTrainerId(u8 *trainerId)
{
    return (trainerId[3] << 24) | (trainerId[2] << 16) | (trainerId[1] << 8) | (trainerId[0]);
}

void CopyTrainerId(u8 *dst, u8 *src)
{
    s32 i;
    for (i = 0; i < TRAINER_ID_LENGTH; i++)
        dst[i] = src[i];
}

static void InitPlayerTrainerId(void)
{
    u32 trainerId = (Random() << 16) | GetGeneratedTrainerIdLower();
    SetTrainerId(trainerId, gSaveBlock2Ptr->playerTrainerId);
}

// L=A isnt set here for some reason.
static void SetDefaultOptions(void)
{
    gSaveBlock2Ptr->optionsTextSpeed = OPTIONS_TEXT_SPEED_MID;
    gSaveBlock2Ptr->optionsWindowFrameType = 0;
    gSaveBlock2Ptr->optionsSound = OPTIONS_SOUND_MONO;
    gSaveBlock2Ptr->optionsBattleStyle = OPTIONS_BATTLE_STYLE_SET;
    gSaveBlock2Ptr->optionsBattleSceneOff = FALSE;
    gSaveBlock2Ptr->regionMapZoom = FALSE;
}

static void ClearPokedexFlags(void)
{
    gUnusedPokedexU8 = 0;
    memset(&gSaveBlock1Ptr->dexCaught, 0, sizeof(gSaveBlock1Ptr->dexCaught));
    memset(&gSaveBlock1Ptr->dexSeen, 0, sizeof(gSaveBlock1Ptr->dexSeen));
}

void ClearAllContestWinnerPics(void)
{
    s32 i;

    ClearContestWinnerPicsInContestHall();

    // Clear Museum paintings
    for (i = MUSEUM_CONTEST_WINNERS_START; i < NUM_CONTEST_WINNERS; i++)
        gSaveBlock1Ptr->contestWinners[i] = sContestWinnerPicDummy;
}

static void ClearFrontierRecord(void)
{
    CpuFill32(0, &gSaveBlock2Ptr->frontier, sizeof(gSaveBlock2Ptr->frontier));

    gSaveBlock2Ptr->frontier.opponentNames[0][0] = EOS;
    gSaveBlock2Ptr->frontier.opponentNames[1][0] = EOS;
}

static void WarpToDemoStart(void)
{
    // Plastic Ox demo: start in the player's bedroom in Pallet Town.
    // Pallet Town (Gen 1) is stitched north into Route 101 (Gen 3), which
    // connects to Oldale Town. See plastic_ox/demo/DEMO_MAP_STITCH_v0.1.md.
    SetWarpDestination(MAP_GROUP(MAP_PALLET_TOWN_PLAYERS_HOUSE_2F), MAP_NUM(MAP_PALLET_TOWN_PLAYERS_HOUSE_2F), WARP_ID_NONE, 6, 6);
    WarpIntoMap();
}

void Sav2_ClearSetDefault(void)
{
    ClearSav2();
    SetDefaultOptions();
}

void ResetMenuAndMonGlobals(void)
{
    gDifferentSaveFile = FALSE;
    ResetPokedexScrollPositions();
    ZeroPlayerPartyMons();
    ZeroEnemyPartyMons();
    ResetBagScrollPositions();
    ResetPokeblockScrollPositions();
}

void NewGameInitData(void)
{
#if IS_FRLG
    u8 rivalName[PLAYER_NAME_LENGTH + 1];
#endif
    if (gSaveFileStatus == SAVE_STATUS_EMPTY || gSaveFileStatus == SAVE_STATUS_CORRUPT)
        RtcReset();

#if IS_FRLG
    StringCopy(rivalName, gSaveBlock1Ptr->rivalName);
#endif
    gDifferentSaveFile = TRUE;
    gSaveBlock2Ptr->encryptionKey = 0;
    StringCopy(gSaveBlock2Ptr->playerName, sPlasticOxPlayerName);
    gSaveBlock2Ptr->playerGender = MALE;
    ZeroPlayerPartyMons();
    ZeroEnemyPartyMons();
    ResetPokedex();
    ClearFrontierRecord();
    ClearSav1();
    ClearSav3();
    ClearAllMail();
    gSaveBlock2Ptr->specialSaveWarpFlags = 0;
    gSaveBlock2Ptr->gcnLinkFlags = 0;
    InitPlayerTrainerId();
    PlayTimeCounter_Reset();
    ClearPokedexFlags();
    InitEventData();
    ClearTVShowData();
    ResetGabbyAndTy();
    ClearSecretBases();
    ClearBerryTrees();
    SetMoney(&gSaveBlock1Ptr->money, 3000);
    SetCoins(0);
    ResetLinkContestBoolean();
    ResetGameStats();
    ClearAllContestWinnerPics();
    ClearPlayerLinkBattleRecords();
    InitSeedotSizeRecord();
    InitLotadSizeRecord();
    gPartiesCount[B_TRAINER_PLAYER] = 0;
    ZeroPlayerPartyMons();
    ResetPokemonStorageSystem();
    DeactivateAllRoamers();
    gSaveBlock1Ptr->registeredItem = ITEM_NONE;
    ClearBag();
    NewGameInitPCItems();
    ClearPokeblocks();
    ClearDecorationInventories();
    InitEasyChatPhrases();
    SetMauvilleOldMan();
    InitDewfordTrend();
    ResetFanClub();
    ResetLotteryCorner();
    UpdateDailySeed();
    WarpToDemoStart();
    if (IS_FRLG)
        RunScriptImmediately(EventScript_ResetAllMapFlagsFrlg);
    else
        RunScriptImmediately(EventScript_ResetAllMapFlags);
#if IS_FRLG
        StringCopy(gSaveBlock1Ptr->rivalName, rivalName);
#endif
    ResetMiniGamesRecords();
    InitUnionRoomChatRegisteredTexts();
    InitLilycoveLady();
    ResetAllApprenticeData();
    ClearRankingHallRecords();
    InitMatchCallCounters();
    ClearMysteryGift();
    WipeTrainerNameRecords();
    ResetTrainerHillResults();
    ResetTrainerTowerResults();
    ResetContestLinkResults();
    SetCurrentDifficultyLevel(DIFFICULTY_NORMAL);
    ResetItemFlags();
    ResetDexNav();
    ClearFollowerNPCData();

    // Hide battle-demo NPCs in walkable and trigger alpha builds.
    // The PLASTIC_OX_BUILD=battle build leaves these cleared so the NPCs appear.
#ifndef PLASTIC_OX_BUILD_BATTLE
    FlagSet(FLAG_POX_HIDE_BATTLE_OAK_PALLET);
    FlagSet(FLAG_POX_HIDE_BATTLE_OAK_LAB);
    FlagSet(FLAG_POX_HIDE_BATTLE_LANCE);
#endif

    // Plastic Ox skips the vanilla starter flow, so unblock vanilla gates that
    // expect the adventure-started flag (notably Oldale's west exit).
    FlagSet(FLAG_ADVENTURE_STARTED);
    FlagSet(FLAG_POX_HIDE_UNUSED_ACTOR);

    // Set this after the save block has been initialized, never before its
    // pointers are installed or before ResetAllMapFlags clears the flags.
#ifdef PLASTIC_OX_BUILD_TRIGGERS
    FlagSet(FLAG_POX_TRIGGERS_ENABLED);
#else
    FlagSet(FLAG_POX_HIDE_STORY_NPCS);
    FlagSet(FLAG_POX_HIDE_R29_GUARD);
    FlagSet(FLAG_POX_HIDE_MTMOON_GRUNT_1);
    FlagSet(FLAG_POX_HIDE_MTMOON_GRUNT_2);
    FlagSet(FLAG_POX_HIDE_LAVENDER_GRUNT_1);
    FlagSet(FLAG_POX_HIDE_LAVENDER_GRUNT_2);
    FlagSet(FLAG_POX_HIDE_SILPH_GRUNT_1);
    FlagSet(FLAG_POX_HIDE_SILPH_GRUNT_2);
    FlagSet(FLAG_POX_HIDE_SILPH_GRUNT_3);
    FlagSet(FLAG_POX_HIDE_SILPH_GIOVANNI);
    FlagSet(FLAG_POX_ENTEI);
#endif
}

void GivePlasticOxPlayerParty(void)
{
    const struct Trainer *trainer = GetTrainerStructFromId(TRAINER_PLASTIC_OX_PLAYER);

    // Trainer-party construction creates NPC-owned encrypted Pokémon. Rebinding
    // their OT data afterward can invalidate their box checksums, turning the
    // party into Bad Eggs. Build the same sets as player-owned Pokémon instead.
    ZeroPlayerPartyMons();
    for (u32 i = 0; i < trainer->partySize; i++)
    {
        const struct TrainerMon *partyData = &trainer->party[i];
        struct Pokemon mon;
        u32 abilityNum = 0;

        CreateMon(&mon,
                  partyData->species,
                  partyData->lvl,
                  GetMonPersonality(partyData->species, MON_GENDER_RANDOM, partyData->nature, RANDOM_UNOWN_LETTER),
                  OTID_STRUCT_PLAYER_ID);
        SetMonData(&mon, MON_DATA_HELD_ITEM, &partyData->heldItem);
        SetMonData(&mon, MON_DATA_IVS, &partyData->iv);

        for (u32 move = 0; move < MAX_MON_MOVES; move++)
            SetMonMoveSlot(&mon, partyData->moves[move], move);

        if (partyData->ev != NULL)
        {
            SetMonData(&mon, MON_DATA_HP_EV, &partyData->ev[0]);
            SetMonData(&mon, MON_DATA_ATK_EV, &partyData->ev[1]);
            SetMonData(&mon, MON_DATA_DEF_EV, &partyData->ev[2]);
            SetMonData(&mon, MON_DATA_SPATK_EV, &partyData->ev[3]);
            SetMonData(&mon, MON_DATA_SPDEF_EV, &partyData->ev[4]);
            SetMonData(&mon, MON_DATA_SPEED_EV, &partyData->ev[5]);
        }

        if (partyData->ability != ABILITY_NONE)
        {
            const struct SpeciesInfo *speciesInfo = &gSpeciesInfo[partyData->species];
            while (speciesInfo->abilities[abilityNum] != partyData->ability)
                abilityNum++;
        }
        SetMonData(&mon, MON_DATA_ABILITY_NUM, &abilityNum);
        SetMonData(&mon, MON_DATA_FRIENDSHIP, &partyData->friendship);
        CalculateMonStats(&mon);
        GiveScriptedMonToPlayer(&mon, i);
    }

    gPartiesCount[B_TRAINER_PLAYER] = CalculatePlayerPartyCount();
    // Adding party data alone does not unlock the START-menu Pokémon option.
    // The ordinary starter handoff sets this separate system flag; keep it
    // whenever this scripted Oak gift is used.
    FlagSet(FLAG_SYS_POKEMON_GET);

    // DEMO ONLY: grant every Gym Badge so this imported high-level team always
    // obeys. Remove this loop before a production/story release.
    for (u16 badge = FLAG_BADGE01_GET; badge <= FLAG_BADGE08_GET; badge++)
        FlagSet(badge);

    // The save system restores the party from SaveBlock1. Keep that persistent
    // copy in sync with the freshly generated demo team from the first frame.
    SavePlayerParty();
}

void CB2_InitPlasticOxDemo(void)
{
    // Deterministic demo boot: initialize a fresh save in memory and enter the
    // Pallet bedroom directly, bypassing copyright/title/new-game naming UI.
#ifdef PLASTIC_OX_BUILD_TRIGGERS
    gPlasticOxTriggersEnabled = TRUE;
#else
    gPlasticOxTriggersEnabled = FALSE;
#endif
#ifdef PLASTIC_OX_BUILD_BATTLE
    gPlasticOxBattleDemoEnabled = TRUE;
#else
    gPlasticOxBattleDemoEnabled = FALSE;
#endif
    SetSaveBlocksPointers(GetSaveBlocksPointersBaseOffset());
    ResetMenuAndMonGlobals();
    Save_ResetSaveCounters();
    Sav2_ClearSetDefault();
    SetPokemonCryStereo(gSaveBlock2Ptr->optionsSound);
    SetMainCallback2(CB2_NewGame);
}

static void ResetMiniGamesRecords(void)
{
    CpuFill16(0, &gSaveBlock2Ptr->berryCrush, sizeof(struct BerryCrush));
    SetBerryPowder(&gSaveBlock2Ptr->berryCrush.berryPowderAmount, 0);
    ResetPokemonJumpRecords();
    CpuFill16(0, &gSaveBlock2Ptr->berryPick, sizeof(struct BerryPickingResults));
}

static void ResetItemFlags(void)
{
#if OW_SHOW_ITEM_DESCRIPTIONS == OW_ITEM_DESCRIPTIONS_FIRST_TIME
    memset(&gSaveBlock3Ptr->itemFlags, 0, sizeof(gSaveBlock3Ptr->itemFlags));
#endif
}

static void ResetDexNav(void)
{
#if USE_DEXNAV_SEARCH_LEVELS == TRUE
    memset(gSaveBlock3Ptr->dexNavSearchLevels, 0, sizeof(gSaveBlock3Ptr->dexNavSearchLevels));
#endif
    gSaveBlock3Ptr->dexNavChain = 0;
}
