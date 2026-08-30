#ifndef GUARD_PLASTIC_OX_H
#define GUARD_PLASTIC_OX_H

// Plastic Ox two-build runtime switch: 0 = walkable demo (no trainer LOS
// battles, no wild encounters), 1 = trigger demo (full story events).
// Set in CB2_InitPlasticOxDemo based on PLASTIC_OX_BUILD_TRIGGERS.
extern u8 gPlasticOxTriggersEnabled;

// Battle-demo runtime switch: 1 = battle demo build (Oak team gift + Lance
// battle visible), 0 = walkable/trigger alpha build (battle NPCs hidden).
// Set in CB2_InitPlasticOxDemo based on PLASTIC_OX_BUILD_BATTLE.
extern u8 gPlasticOxBattleDemoEnabled;

#endif // GUARD_PLASTIC_OX_H
