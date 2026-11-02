#ifndef GUARD_PLASTIC_OX_H
#define GUARD_PLASTIC_OX_H

// Enables authored story events, trainer sight battles, and wild encounters.
// The normal ROM enables this during the Plastic Ox boot flow.
extern u8 gPlasticOxTriggersEnabled;

// Battle-demo runtime switch: 1 = battle demo build (Oak team gift + Lance
// battle visible), 0 = normal story build (battle NPCs hidden).
// Set during the Plastic Ox boot flow based on PLASTIC_OX_BUILD_BATTLE.
extern u8 gPlasticOxBattleDemoEnabled;

#endif // GUARD_PLASTIC_OX_H
