#ifndef GUARD_CONSTANTS_PLASTIC_OX_CONTEST_H
#define GUARD_CONSTANTS_PLASTIC_OX_CONTEST_H

#define POX_CONTEST_ENTRY_OPEN          0
#define POX_CONTEST_ENTRY_CLOSED        1
#define POX_CONTEST_ENTRY_USED          2
#define POX_CONTEST_ENTRY_PRIZE_PENDING 3
#define POX_CONTEST_ENTRY_NO_ROOM       4
#define POX_CONTEST_ENTRY_IN_PROGRESS   5
#define POX_CONTEST_ENTRY_INVALID_MON   6
#define POX_CONTEST_ENTRY_PASS_REQUIRED 7

// PlasticOxContest_ClaimPrize results (TRUE = item prize bagged, FALSE = bag full).
#define POX_CONTEST_PRIZE_MON_PARTY     2
#define POX_CONTEST_PRIZE_MON_PC        3
#define POX_CONTEST_PRIZE_MON_NO_ROOM   4

// PlasticOxContest_Judge results: 0 no catch, 1-3 place, 4 delivery blocked.
#define POX_CONTEST_RESULT_UNPLACED     5

#define POX_CONTEST_RIVALS              5
#define POX_CONTEST_PLAYER              POX_CONTEST_RIVALS

#endif // GUARD_CONSTANTS_PLASTIC_OX_CONTEST_H
