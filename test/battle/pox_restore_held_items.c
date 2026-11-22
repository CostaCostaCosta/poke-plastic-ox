#include "global.h"
#include "test/battle.h"
#include "battle.h"
#include "battle_util.h"
#include "malloc.h"
#include "pokemon.h"
#include "constants/battle.h"
#include "constants/items.h"

// Plastic Ox: TryRestoreHeldItems runs at the end of every battle (battle_main.c).
// These tests drive it directly with the post-battle party state.

static void SetupParty(const u16 *entered, const u16 *afterBattle, u32 battleType)
{
    ZeroPlayerPartyMons();
    for (u32 i = 0; i < 4; i++)
    {
        u16 item = afterBattle[i];
        CreateMon(&gParties[B_TRAINER_PLAYER][i], SPECIES_WOBBUFFET, 20, 0, OTID_STRUCT_PLAYER_ID);
        SetMonData(&gParties[B_TRAINER_PLAYER][i], MON_DATA_HELD_ITEM, &item);
        gBattleStruct->itemLost[B_TRAINER_PLAYER][i].originalItem = entered[i];
        gBattleStruct->itemLost[B_TRAINER_PLAYER][i].stolen = FALSE;
    }
    gBattleTypeFlags = battleType;
}

static void RunCase(u32 battleType)
{
    // 0: Oran Berry eaten. 1: Leftovers knocked off/stolen. 2: entered empty, stole Nugget via Thief.
    // 3: entered with Charcoal, stole Leftovers via Thief (swap) -> Charcoal back.
    static const u16 entered[4]     = { ITEM_ORAN_BERRY, ITEM_LEFTOVERS, ITEM_NONE,   ITEM_CHARCOAL };
    static const u16 afterBattle[4] = { ITEM_NONE,       ITEM_NONE,      ITEM_NUGGET, ITEM_LEFTOVERS };
    bool32 allocated = FALSE;
    if (gBattleStruct == NULL)
    {
        gBattleStruct = AllocZeroed(sizeof(*gBattleStruct));
        allocated = TRUE;
    }
    SetupParty(entered, afterBattle, battleType);
    TryRestoreHeldItems();
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_HELD_ITEM), ITEM_ORAN_BERRY);
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][1], MON_DATA_HELD_ITEM), ITEM_LEFTOVERS);
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][2], MON_DATA_HELD_ITEM), ITEM_NUGGET);
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][3], MON_DATA_HELD_ITEM), ITEM_CHARCOAL);
    if (allocated)
    {
        Free(gBattleStruct);
        gBattleStruct = NULL;
    }
}

TEST("Plastic Ox: held items are restored after a wild battle; Thief loot kept only by empty-handed mons")
{
    RunCase(0);
}

TEST("Plastic Ox: held items are restored after a trainer battle; Thief loot kept only by empty-handed mons")
{
    RunCase(BATTLE_TYPE_TRAINER);
}

TEST("Plastic Ox: held items are restored after a double trainer battle")
{
    RunCase(BATTLE_TYPE_TRAINER | BATTLE_TYPE_DOUBLE);
}

SINGLE_BATTLE_TEST("Plastic Ox: an Oran Berry is consumed in battle (restored by TryRestoreHeldItems)")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { MaxHP(100); HP(51); Item(ITEM_ORAN_BERRY); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(opponent, MOVE_SCRATCH); }
    } SCENE {
        MESSAGE("Wobbuffet restored its health using its Oran Berry!");
    } THEN {
        EXPECT_EQ((u32)gBattleStruct->itemLost[B_TRAINER_PLAYER][0].originalItem, ITEM_ORAN_BERRY);
        EXPECT_EQ(player->item, ITEM_NONE);
        TryRestoreHeldItems();
        EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_HELD_ITEM), ITEM_ORAN_BERRY);
    }
}
