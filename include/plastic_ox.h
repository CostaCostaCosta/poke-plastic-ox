#ifndef GUARD_PLASTIC_OX_H
#define GUARD_PLASTIC_OX_H

// Plastic Ox two-build runtime switch: 0 = walkable demo (no trainer LOS
// battles, no wild encounters), 1 = trigger demo (full story events).
// Set in CB2_InitPlasticOxDemo based on PLASTIC_OX_BUILD_TRIGGERS.
extern u8 gPlasticOxTriggersEnabled;

#endif // GUARD_PLASTIC_OX_H
