Route44_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route44_hns
	.byte 0

PoxRoute44_MtMoonGate::
	msgbox PoxRoute44_MtMoonGate_Text, MSGBOX_NPC
	end

PoxRoute44_MtMoonGate_Text::
	.string "MT. MOON is rough going.\nI need to see the STONE BADGE.\pROXANNE runs the RUSTBORO GYM.\nBeat her, and I'll let you pass.$"

PoxRoute44_LunchFisherman::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE44_EDGAR, PoxRoute44_LunchFisherman_Challenge, PoxRoute44_LunchFisherman_Defeat
	msgbox PoxRoute44_LunchFisherman_Text, MSGBOX_AUTOCLOSE
	end

PoxRoute44_LunchFisherman_Text::
	.string "I packed lunch for a long day\nof fishing.\pThe fish aren't biting, but\nat least the lunch was good.$"

PoxRoute44_FishingSpot::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE44_WILTON, PoxRoute44_FishingSpot_Challenge, PoxRoute44_FishingSpot_Defeat
	msgbox PoxRoute44_FishingSpot_Text, MSGBOX_AUTOCLOSE
	end

PoxRoute44_FishingSpot_Text::
	.string "I keep coming back to this\nfishing spot.\pI catch more stories than\nPOKéMON, but I don't mind.$"

PoxRoute44_LostNavigator::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE44_ZACH, PoxRoute44_LostNavigator_Challenge, PoxRoute44_LostNavigator_Defeat
	msgbox PoxRoute44_LostNavigator_Text, MSGBOX_AUTOCLOSE
	end

PoxRoute44_LostNavigator_Text::
	.string "My old map has no RUSTBORO\nwest of this road.\pI'll pencil it in for now.\nNo sense throwing good paper out.$"

PoxRoute44_CaveWalker::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE44_ALLEN, PoxRoute44_CaveWalker_Challenge, PoxRoute44_CaveWalker_Defeat
	msgbox PoxRoute44_CaveWalker_Text, MSGBOX_AUTOCLOSE
	end

PoxRoute44_CaveWalker_Text::
	.string "I stop here to tie my laces\nbefore entering MT. MOON.\pI tripped in a cave once.\nThe echo made quite a fuss.$"

PoxRoute44_PebbleInBoot::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE44_CYBIL, PoxRoute44_PebbleInBoot_Challenge, PoxRoute44_PebbleInBoot_Defeat
	msgbox PoxRoute44_PebbleInBoot_Text, MSGBOX_AUTOCLOSE
	end

PoxRoute44_PebbleInBoot_Text::
	.string "There's a pebble in my boot.\nI've stopped twice to shake it.\pIf it likes traveling so much,\nit can ride in my pocket.$"

PoxRoute44_CityWalker::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE44_VANCE, PoxRoute44_CityWalker_Challenge, PoxRoute44_CityWalker_Defeat
	msgbox PoxRoute44_CityWalker_Text, MSGBOX_AUTOCLOSE
	end

PoxRoute44_CityWalker_Text::
	.string "I come out here when RUSTBORO\ngets too noisy.\pNow I can hear my knees creak.\nPerhaps I'll head back.$"

@ Run 5 warp playtest: this used to land on (18,36) while the matching return
@ warp, MtMoon_1F warp 3, sits on (18,37).  The two ends of the ROUTE 44 ->
@ MT. MOON link therefore disagreed, and the return leg could not be walked.
@ (18,37) is Mt. Moon's own entrance tile: the player arrives on it facing
@ down, (18,38) is the rock wall behind them, and stepping back down takes
@ warp 3 straight out to ROUTE 44.
@
@ (68,13) is the walkable tile in front of the cave mouth (68,12) and doubles
@ as the landing anchor for MtMoon_1F warp 3.  The gate hiker now stands at
@ (69,13), so this tile cannot be blocked: the badge check runs before the
@ warp and a refusal puts the player back at (68,14), not in a dead end.
PoxMoon_EnterFromRoute44::
	lockall
	goto_if_unset FLAG_BADGE01_GET, PoxMoon_EnterFromRoute44_NoBadge
	warp MAP_MT_MOON_1F, 18, 37
	waitstate
	releaseall
	end

PoxMoon_EnterFromRoute44_NoBadge::
	msgbox PoxMoon_EnterFromRoute44_NoBadge_Text, MSGBOX_DEFAULT
	warp MAP_ROUTE44_HNS, 68, 14
	waitstate
	releaseall
	end

PoxMoon_EnterFromRoute44_NoBadge_Text::
	.string "STONE BADGE first. Nothing\npersonal.\pI've carried people back down\nfrom up there before.$"

PoxRoute44_LunchFisherman_Challenge::
	.string "I've been out here since\nbreakfast. Battle me before my\plunch gets cold!$"

PoxRoute44_LunchFisherman_Defeat::
	.string "My sandwich and I both lost!$"

PoxRoute44_FishingSpot_Challenge::
	.string "Shh, you'll scare the fish.\nWell, since you're here, let's\pbattle!$"

PoxRoute44_FishingSpot_Defeat::
	.string "Reeled in and released!$"

PoxRoute44_LostNavigator_Challenge::
	.string "Can you point me to RUSTBORO?\nNo? Then a battle while I think.$"

PoxRoute44_LostNavigator_Defeat::
	.string "I've lost my way and the match!$"

PoxRoute44_CaveWalker_Challenge::
	.string "One battle before the cave?\nSure, I'm warmed up!$"

PoxRoute44_CaveWalker_Defeat::
	.string "Guess I'll warm up some more.$"

PoxRoute44_PebbleInBoot_Challenge::
	.string "Ow, this pebble! A battle will\ntake my mind off it!$"

PoxRoute44_PebbleInBoot_Defeat::
	.string "Lost, and the pebble's still\nthere!$"

PoxRoute44_CityWalker_Challenge::
	.string "Out here for a bit of quiet. A\nbattle's quiet enough!$"

PoxRoute44_CityWalker_Defeat::
	.string "Okay, that was loud after all.$"
