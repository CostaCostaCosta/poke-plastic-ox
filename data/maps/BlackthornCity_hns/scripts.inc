BlackthornCity_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_BlackthornCity_hns
	.byte 0

@ The GYM door at (16,28) is a plain walkable tile in this layout (metatile
@ behaviour MB_NORMAL), so a bare warp event there would never fire; the door
@ is driven by this tile trigger instead.  Warp 2 in map.json is the matching
@ landing anchor for the GYM's arrow-warp exit.  Pox_ClairGuide is left on the
@ doorman at (15,28) as the Space-Center-gated hint/shortcut; the town itself
@ is already gated by PoxRegion_meteor_blackthorn_b / _route45_a.
BlackthornCity_EventScript_GymDoor::
	lockall
	warp MAP_PLASTIC_OX_CLAIR_GYM, 5, 18
	waitstate
	releaseall
	end

BlackthornCity_EventScript_Npc1::
	lock
	faceplayer
	msgbox BlackthornCity_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

BlackthornCity_EventScript_Npc2::
	lock
	faceplayer
	msgbox BlackthornCity_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

BlackthornCity_EventScript_Npc3::
	lock
	faceplayer
	msgbox BlackthornCity_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

BlackthornCity_EventScript_Npc4::
	lock
	faceplayer
	msgbox BlackthornCity_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

BlackthornCity_EventScript_Npc5::
	lock
	faceplayer
	msgbox BlackthornCity_EventScript_Npc5_Text, MSGBOX_NPC
	release
	end

BlackthornCity_EventScript_Npc6::
	lock
	faceplayer
	msgbox BlackthornCity_EventScript_Npc6_Text, MSGBOX_NPC
	release
	end

@ Dragon's Den door (26,12). The elder is hidden by FLAG_SYS_GAME_CLEAR, so
@ the Den opens with the Hall of Fame.
BlackthornCity_EventScript_DenElder::
	lock
	faceplayer
	msgbox BlackthornCity_EventScript_DenElder_Text, MSGBOX_NPC
	release
	end

BlackthornCity_EventScript_DenElder_Text:
	.string "This is the DRAGON'S DEN, and I\nhave kept its door for forty years.\pThe POKéMON inside are far too\npowerful. I've turned GYM LEADERS\laround on this step.\pThe only name that opens it is one\nwritten in the HALL OF FAME.$"

BlackthornCity_EventScript_Npc1_Text:
	.string "Dragon training takes patience.\nPower alone is not enough.$"

BlackthornCity_EventScript_Npc2_Text:
	.string "The mountain air makes every\nmorning feel sharp and clear.$"

BlackthornCity_EventScript_Npc3_Text:
	.string "Dragon training takes patience.\nPower alone is not enough.$"

BlackthornCity_EventScript_Npc4_Text:
	.string "The mountain air makes every\nmorning feel sharp and clear.$"

BlackthornCity_EventScript_Npc5_Text:
	.string "I cycle the switchbacks up from\nROUTE 45 every morning. My legs\phave stopped speaking to me.$"

BlackthornCity_EventScript_Npc6_Text:
	.string "I meditate under the falls\nbehind town. The cold water\psharpens the mind.$"
