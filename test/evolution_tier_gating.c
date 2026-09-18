// Plastic Ox: tests for tier-based evolution gating.
// See plastic_ox/plasticox_encounters_v1.md and
// plastic_ox/agent/plasticox_evolution_gating_plan_v1.md.
//
// Tier unlock thresholds (badges held during the tier's gym segment):
//   LC 0, PU 1, NU 2, RU 3, UU 4, UUBL 5, OU 6.
#include "global.h"
#include "event_data.h"
#include "evolution_scene.h"
#include "item.h"
#include "pokemon.h"
#include "test/test.h"

static void SetBadges(u32 numBadges)
{
    u32 j;
    for (j = 0; j < NUM_BADGES; j++)
    {
        if (j < numBadges)
            FlagSet(FLAG_BADGE01_GET + j);
        else
            FlagClear(FLAG_BADGE01_GET + j);
    }
}

TEST("Tier gating: Dratini cannot evolve into Dragonair with 0 badges")
{
    bool32 canStopEvo = TRUE;
    struct Pokemon mon;
    SetBadges(0);
    CreateMon(&mon, SPECIES_DRATINI, 20, 0, OTID_STRUCT_PLAYER_ID);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_NORMAL, ITEM_NONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_NONE);
}

TEST("Tier gating: Dratini evolves into Dragonair at level 20 with 1 badge (PU unlocked)")
{
    bool32 canStopEvo = TRUE;
    struct Pokemon mon;
    SetBadges(1);
    CreateMon(&mon, SPECIES_DRATINI, 20, 0, OTID_STRUCT_PLAYER_ID);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_NORMAL, ITEM_NONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_DRAGONAIR);
}

TEST("Tier gating: Abra cannot evolve into Kadabra before UUBL")
{
    bool32 canStopEvo = TRUE;
    struct Pokemon mon;
    SetBadges(4);
    CreateMon(&mon, SPECIES_ABRA, 16, 0, OTID_STRUCT_PLAYER_ID);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_NORMAL, ITEM_NONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_NONE);
}

TEST("Tier gating: Abra evolves into Kadabra at level 16 with 5 badges (UUBL unlocked)")
{
    bool32 canStopEvo = TRUE;
    struct Pokemon mon;
    SetBadges(5);
    CreateMon(&mon, SPECIES_ABRA, 16, 0, OTID_STRUCT_PLAYER_ID);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_NORMAL, ITEM_NONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_KADABRA);
}

TEST("Tier gating: item safety rule - Water Stone cannot force Starmie before OU")
{
    bool32 canStopEvo = TRUE;
    struct Pokemon mon;
    SetBadges(5);
    CreateMon(&mon, SPECIES_STARYU, 30, 0, OTID_STRUCT_PLAYER_ID);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_ITEM_USE, ITEM_WATER_STONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_NONE);
}

TEST("Tier gating: Water Stone evolves Staryu into Starmie with 6 badges (OU unlocked)")
{
    bool32 canStopEvo = TRUE;
    struct Pokemon mon;
    SetBadges(6);
    CreateMon(&mon, SPECIES_STARYU, 30, 0, OTID_STRUCT_PLAYER_ID);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_ITEM_USE, ITEM_WATER_STONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_STARMIE);
}

TEST("Tier gating: item safety rule - the same Water Stone evolves Poliwhirl at RU")
{
    bool32 canStopEvo = TRUE;
    struct Pokemon mon;
    SetBadges(3);
    CreateMon(&mon, SPECIES_POLIWHIRL, 30, 0, OTID_STRUCT_PLAYER_ID);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_ITEM_USE, ITEM_WATER_STONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_POLIWRATH);
}

TEST("Tier gating: Eevee evolves into Vaporeon with 5 badges (UUBL unlocked)")
{
    bool32 canStopEvo = TRUE;
    struct Pokemon mon;
    SetBadges(5);
    CreateMon(&mon, SPECIES_EEVEE, 30, 0, OTID_STRUCT_PLAYER_ID);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_ITEM_USE, ITEM_WATER_STONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_VAPOREON);
}

TEST("Tier gating: party menu item usability hint (EVO_MODE_ITEM_CHECK) is gated too")
{
    bool32 canStopEvo = TRUE;
    struct Pokemon mon;
    SetBadges(5);
    CreateMon(&mon, SPECIES_STARYU, 30, 0, OTID_STRUCT_PLAYER_ID);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_ITEM_CHECK, ITEM_WATER_STONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_NONE);
    SetBadges(6);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_ITEM_CHECK, ITEM_WATER_STONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_STARMIE);
}

TEST("Tier gating: trade evolutions are gated (Kadabra -> Alakazam, UUBL)")
{
    bool32 canStopEvo = TRUE;
    struct Pokemon mon, partner;
    SetBadges(4);
    CreateMon(&mon, SPECIES_KADABRA, 40, 0, OTID_STRUCT_PLAYER_ID);
    CreateMon(&partner, SPECIES_KADABRA, 40, 0, OTID_STRUCT_PRESET(0));
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_TRADE, ITEM_NONE, &partner, &canStopEvo, CHECK_EVO), SPECIES_NONE);
    SetBadges(5);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_TRADE, ITEM_NONE, &partner, &canStopEvo, CHECK_EVO), SPECIES_ALAKAZAM);
}

TEST("Tier gating: OU-only family - Magikarp cannot evolve into Gyarados before OU")
{
    bool32 canStopEvo = TRUE;
    struct Pokemon mon;
    SetBadges(5);
    CreateMon(&mon, SPECIES_MAGIKARP, 20, 0, OTID_STRUCT_PLAYER_ID);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_NORMAL, ITEM_NONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_NONE);
    SetBadges(6);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_NORMAL, ITEM_NONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_GYARADOS);
}

TEST("Tier gating: Nincada sheds a Shedinja without evolving when Ninjask is tier-locked (PU)")
{
    struct Pokemon *mon;
    SetBadges(1);
    ZeroPlayerPartyMons();
    CreateMon(&gParties[B_TRAINER_PLAYER][0], SPECIES_NINCADA, 20, 0, OTID_STRUCT_PLAYER_ID);
    CalculatePlayerPartyCount();
    AddBagItem(ITEM_POKE_BALL, 1);

    mon = &gParties[B_TRAINER_PLAYER][0];
    EXPECT_EQ(GetEvolutionTargetSpecies(mon, EVO_MODE_NORMAL, ITEM_NONE, NULL, NULL, CHECK_EVO), SPECIES_NONE);
    EXPECT(TryGenerateTierBlockedSplitEvolution(mon));
    EXPECT_EQ(GetMonData(mon, MON_DATA_SPECIES), SPECIES_NINCADA); // Nincada is unchanged
    EXPECT_EQ(gPartiesCount[B_TRAINER_PLAYER], 2);
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][1], MON_DATA_SPECIES), SPECIES_SHEDINJA);
    EXPECT(!CheckBagHasItem(ITEM_POKE_BALL, 1)); // the ball was consumed
}

TEST("Tier gating: Nincada does NOT shed a Shedinja with a full party")
{
    u32 i;
    SetBadges(1);
    ZeroPlayerPartyMons();
    CreateMon(&gParties[B_TRAINER_PLAYER][0], SPECIES_NINCADA, 20, 0, OTID_STRUCT_PLAYER_ID);
    for (i = 1; i < PARTY_SIZE; i++)
        CreateMon(&gParties[B_TRAINER_PLAYER][i], SPECIES_WYNAUT, 5, 0, OTID_STRUCT_PLAYER_ID);
    CalculatePlayerPartyCount();
    AddBagItem(ITEM_POKE_BALL, 1);

    EXPECT(!TryGenerateTierBlockedSplitEvolution(&gParties[B_TRAINER_PLAYER][0]));
    EXPECT_EQ(gPartiesCount[B_TRAINER_PLAYER], PARTY_SIZE);
}

TEST("Tier gating: Nincada does NOT shed a Shedinja while PU is still locked (0 badges)")
{
    SetBadges(0);
    ZeroPlayerPartyMons();
    CreateMon(&gParties[B_TRAINER_PLAYER][0], SPECIES_NINCADA, 20, 0, OTID_STRUCT_PLAYER_ID);
    CalculatePlayerPartyCount();
    AddBagItem(ITEM_POKE_BALL, 1);

    EXPECT(!TryGenerateTierBlockedSplitEvolution(&gParties[B_TRAINER_PLAYER][0]));
    EXPECT_EQ(gPartiesCount[B_TRAINER_PLAYER], 1);
}

TEST("Tier gating: Nincada evolves into Ninjask normally once UU is unlocked (4 badges)")
{
    bool32 canStopEvo = TRUE;
    struct Pokemon mon;
    SetBadges(4);
    CreateMon(&mon, SPECIES_NINCADA, 20, 0, OTID_STRUCT_PLAYER_ID);
    EXPECT_EQ(GetEvolutionTargetSpecies(&mon, EVO_MODE_NORMAL, ITEM_NONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_NINJASK);
    // The normal path handles the evolution; the split helper stays out of the way.
    EXPECT(!TryGenerateTierBlockedSplitEvolution(&mon));
}

TEST("Tier gating: Everstone blocks Shedinja until removed from Nincada")
{
    struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][0];
    enum Item heldItem = ITEM_EVERSTONE;
    SetBadges(1);
    ZeroPlayerPartyMons();
    CreateMon(mon, SPECIES_NINCADA, 20, 0, OTID_STRUCT_PLAYER_ID);
    CalculatePlayerPartyCount();
    AddBagItem(ITEM_POKE_BALL, 1);
    SetMonData(mon, MON_DATA_HELD_ITEM, &heldItem);

    EXPECT(!TryGenerateTierBlockedSplitEvolution(mon));
    EXPECT_EQ(gPartiesCount[B_TRAINER_PLAYER], 1);
    EXPECT_EQ(GetMonData(mon, MON_DATA_SPECIES), SPECIES_NINCADA);
    EXPECT(CheckBagHasItem(ITEM_POKE_BALL, 1));

    heldItem = ITEM_NONE;
    SetMonData(mon, MON_DATA_HELD_ITEM, &heldItem);
    EXPECT(TryGenerateTierBlockedSplitEvolution(mon));
    EXPECT_EQ(gPartiesCount[B_TRAINER_PLAYER], 2);
    EXPECT_EQ(GetMonData(mon, MON_DATA_SPECIES), SPECIES_NINCADA);
    EXPECT_EQ(GetMonData(&gParties[B_TRAINER_PLAYER][1], MON_DATA_SPECIES), SPECIES_SHEDINJA);
    EXPECT(!CheckBagHasItem(ITEM_POKE_BALL, 1));
}

TEST("Tier gating: Nincada cannot shed without a Poke Ball")
{
    struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][0];
    SetBadges(1);
    ZeroPlayerPartyMons();
    CreateMon(mon, SPECIES_NINCADA, 20, 0, OTID_STRUCT_PLAYER_ID);
    CalculatePlayerPartyCount();
    AddBagItem(ITEM_GREAT_BALL, 1);

    EXPECT(!TryGenerateTierBlockedSplitEvolution(mon));
    EXPECT_EQ(gPartiesCount[B_TRAINER_PLAYER], 1);
    EXPECT_EQ(GetMonData(mon, MON_DATA_SPECIES), SPECIES_NINCADA);
    EXPECT(CheckBagHasItem(ITEM_GREAT_BALL, 1));
}

TEST("Tier gating: Nincada cannot shed below level 20")
{
    struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][0];
    SetBadges(1);
    ZeroPlayerPartyMons();
    CreateMon(mon, SPECIES_NINCADA, 19, 0, OTID_STRUCT_PLAYER_ID);
    CalculatePlayerPartyCount();
    AddBagItem(ITEM_POKE_BALL, 1);

    EXPECT(!TryGenerateTierBlockedSplitEvolution(mon));
    EXPECT_EQ(gPartiesCount[B_TRAINER_PLAYER], 1);
    EXPECT_EQ(GetMonData(mon, MON_DATA_SPECIES), SPECIES_NINCADA);
    EXPECT(CheckBagHasItem(ITEM_POKE_BALL, 1));
}
