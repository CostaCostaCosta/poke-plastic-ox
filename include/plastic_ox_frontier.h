#ifndef GUARD_PLASTIC_OX_FRONTIER_H
#define GUARD_PLASTIC_OX_FRONTIER_H

// Plastic Ox Battle Frontier: each house runs seven-battle rounds in one ADV tier,
// against teams from plastic_ox/frontier/ (compiled by
// plastic_ox/tools/build_frontier_teams.py). Scripts pass the tier in VAR_0x8004;
// the numbers must match plastic_ox/alpha/frontier.py.
enum PoxFrontierTier
{
    POX_FRONTIER_TIER_LC,
    POX_FRONTIER_TIER_PU,
    POX_FRONTIER_TIER_NU,
    POX_FRONTIER_TIER_RU,
    POX_FRONTIER_TIER_UU,
    POX_FRONTIER_TIER_UBERS,  // BATTLE DOME
    POX_FRONTIER_TIER_OU,     // BATTLE TOWER
    POX_FRONTIER_TIER_COUNT,
};

#define POX_FRONTIER_ROUND_BATTLES 7

// True while a round is running: losses return to the script instead of whiting out.
bool32 PoxFrontier_IsActive(void);
// True for the seven TRAINER_PLASTIC_OX_FRONTIER_* opponents.
bool32 PoxFrontier_IsTrainer(u16 trainerNum);
// Fills party with the team chosen by PoxFrontier_NextOpponent; returns its size.
u8 PoxFrontier_CreateParty(struct Pokemon *party);

#endif // GUARD_PLASTIC_OX_FRONTIER_H
