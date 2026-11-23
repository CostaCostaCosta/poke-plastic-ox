#include "global.h"
#include "plastic_ox.h"
#include "main.h"
#include "overworld.h"
#include "trainer_card.h"

u8 gPlasticOxTriggersEnabled;
u8 gPlasticOxBattleDemoEnabled;

// Cerulean Cave finale: show the player's own trainer card, then resume the
// calling script (which goes on to the Hall of Fame and credits).
// Call after fadescreen FADE_TO_BLACK and follow with waitstate.
void PoxShowPlayerTrainerCard(void)
{
    ShowPlayerTrainerCard(CB2_ReturnToFieldContinueScriptPlayMapMusic);
}
