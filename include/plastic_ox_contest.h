#ifndef GUARD_PLASTIC_OX_CONTEST_H
#define GUARD_PLASTIC_OX_CONTEST_H

struct Pokemon;

bool32 PlasticOxContest_IsActive(void);
bool32 PlasticOxContest_HasSession(void);
bool32 PlasticOxContest_TakeStep(void);
void PlasticOxContest_StageCatch(struct Pokemon *mon);
void PlasticOxContest_EndBattle(void);
void PlasticOxContest_OnMapChange(void);
void PlasticOxContest_Status(void);
void PlasticOxContest_Start(void);
void PlasticOxContest_AcceptCatch(void);
void PlasticOxContest_Judge(void);
void PlasticOxContest_ClaimPrize(void);

#endif
