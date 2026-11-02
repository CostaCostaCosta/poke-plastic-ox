Route44_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route44_hns
	.byte 0

PoxRoute44_MtMoonGate::
	msgbox PoxRoute44_MtMoonGate_Text, MSGBOX_NPC
	end

PoxRoute44_MtMoonGate_Text::
	.string "MT. MOON is rough going.\nI need to see the STONE BADGE.\pROXANNE runs the RUSTBORO GYM.\nBeat her, and I'll let you pass.$"

PoxRoute44_LunchFisherman::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE44_EDGAR, PoxRoute44_Challenge_Text, PoxRoute44_Defeat_Text
	msgbox PoxRoute44_LunchFisherman_Text, MSGBOX_AUTOCLOSE
	end

PoxRoute44_LunchFisherman_Text::
	.string "I packed lunch for a long day\nof fishing.\pThe fish aren't biting, but\nat least the lunch was good.$"

PoxRoute44_FishingSpot::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE44_WILTON, PoxRoute44_Challenge_Text, PoxRoute44_Defeat_Text
	msgbox PoxRoute44_FishingSpot_Text, MSGBOX_AUTOCLOSE
	end

PoxRoute44_FishingSpot_Text::
	.string "I keep coming back to this\nfishing spot.\pI catch more stories than\nPOKéMON, but I don't mind.$"

PoxRoute44_LostNavigator::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE44_ZACH, PoxRoute44_Challenge_Text, PoxRoute44_Defeat_Text
	msgbox PoxRoute44_LostNavigator_Text, MSGBOX_AUTOCLOSE
	end

PoxRoute44_LostNavigator_Text::
	.string "My old map has no RUSTBORO\nwest of this road.\pI'll pencil it in for now.\nNo sense throwing good paper out.$"

PoxRoute44_CaveWalker::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE44_ALLEN, PoxRoute44_Challenge_Text, PoxRoute44_Defeat_Text
	msgbox PoxRoute44_CaveWalker_Text, MSGBOX_AUTOCLOSE
	end

PoxRoute44_CaveWalker_Text::
	.string "I stop here to tie my laces\nbefore entering MT. MOON.\pI tripped in a cave once.\nThe echo made quite a fuss.$"

PoxRoute44_PebbleInBoot::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE44_CYBIL, PoxRoute44_Challenge_Text, PoxRoute44_Defeat_Text
	msgbox PoxRoute44_PebbleInBoot_Text, MSGBOX_AUTOCLOSE
	end

PoxRoute44_PebbleInBoot_Text::
	.string "There's a pebble in my boot.\nI've stopped twice to shake it.\pIf it likes traveling so much,\nit can ride in my pocket.$"

PoxRoute44_CityWalker::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE44_VANCE, PoxRoute44_Challenge_Text, PoxRoute44_Defeat_Text
	msgbox PoxRoute44_CityWalker_Text, MSGBOX_AUTOCLOSE
	end

PoxRoute44_CityWalker_Text::
	.string "I come out here when RUSTBORO\ngets too noisy.\pNow I can hear my knees creak.\nPerhaps I'll head back.$"

PoxRoute44_Challenge_Text::
	.string "I train with the POKéMON from\nthis stretch of river. Battle?$"

PoxRoute44_Defeat_Text::
	.string "You know this road well!$"

@ Run 5 warp playtest: this used to land on (18,36) while the matching return
@ warp, MtMoon_1F warp 3, sits on (18,37).  The two ends of the ROUTE 44 ->
@ MT. MOON link therefore disagreed, and the return leg could not be walked.
@ (18,37) is Mt. Moon's own entrance tile: the player arrives on it facing
@ down, (18,38) is the rock wall behind them, and stepping back down takes
@ warp 3 straight out to ROUTE 44.
PoxMoon_EnterFromRoute44::
	lockall
	warp MAP_MT_MOON_1F, 18, 37
	waitstate
	releaseall
	end
