#ifndef GUARD_METAMON_TRAINER_H
#define GUARD_METAMON_TRAINER_H

/* Explicit opt-in table in metamon_trainer.c; ordinary controllers are retained. */
void MetamonBattleInit(void);
void MetamonBattleFree(void);
bool32 MetamonControls(u32 battler);
bool32 MetamonBusy(void);
bool32 MetamonChooseAction(u32 battler);
bool32 MetamonChooseMove(u32 battler);
bool32 MetamonChoosePokemon(u32 battler);
void MetamonPublicSwitch(u32 battler);
void MetamonPublicHP(u32 battler);
void MetamonPublicMove(u32 battler, u32 move);
void MetamonCalledMove(void);
void MetamonMoveStart(void);
void MetamonPublicAbility(u32 battler, u32 ability);
void MetamonPublicItem(u32 battler, u32 item);

#endif
