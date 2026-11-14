EcruteakCity_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_EcruteakCity_hns
	.byte 0

EcruteakCity_EventScript_Npc2::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc2_Text:
	.string "You can't cast a bell twice.\nThe second one always has a seam\nin the ring, and the whole street\ncan hear it.\pThey pulled the old ceremonial\nbell out of the ash. I know its\npnote. I would know it anywhere.\pThe BURNED TOWER remembers the\nfire. The fire remembers nothing.\pThat sounds fine until you try to\nsell a bell with a seam in it.$"

EcruteakCity_EventScript_MarketStall::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_MarketStall_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_MarketStall_Text:
	.string "Chestnuts, roasted in the brazier,\nstill in the shell.\pSlit the shell and go slow, or\nthey go off like firecrackers and\ptake the roof with them.\pNo charge for the smell. The tower\nroad is cold this time of year.$"

EcruteakCity_EventScript_FireWatch::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_FireWatch_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_FireWatch_Text:
	.string "Ninth hour I walk the tower, then\nthe roof lines, then the bridge.\pForty years of that and nothing\nhas ever burned.\pWell. Once. That was before my\ntime, and the rota learned.\pNow there are two of us, a\nhand-cranked siren, and a water\npbarrel on every corner.\pIt is a dull job. I would like it\nto stay dull.$"

EcruteakCity_EventScript_GateWatch::
	lock
	faceplayer
	goto_if_set FLAG_POX_STORY_BURNED_TOWER, EcruteakCity_EventScript_GateWatch_Open
	msgbox EcruteakCity_EventScript_GateWatch_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_GateWatch_Open::
	msgbox EcruteakCity_EventScript_GateWatch_Open_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_GateWatch_Text:
	.string "I keep the east door. The road\npast it stays shut until MORTY\npcomes back up.\pThat is a schedule, not a mystery.\nThe tower bell rings for evening,\pand the door opens after it.$"

EcruteakCity_EventScript_GateWatch_Open_Text:
	.string "Door is open. ROUTE 119 runs\neast, then down to the water.\pMind the decks. The river has been\nhigher since the spring.$"

EcruteakCity_EventScript_Npc5::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc5_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc5_Text:
	.string "West of here the road runs to the\nLEAGUE. The gatehouse guard\npcounts your BADGES there.\pEight. All of them. He has never\nhad to refuse twice politely,\pwhich is a kind of manners.\pThe rest of us use the gatehouse\nto get out of the rain.$"

EcruteakCity_EventScript_Npc6::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc6_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc6_Text:
	.string "My father measured the tower every\nspring. Every beam, every stair,\pdown to the gap where the old one\nfell.\pHe says a building is a set of\nmeasurements that agrees with\npitself. When the tower came back\nfor a heartbeat, he was furious\nphe had missed it.\pI know every loose board in this\nstreet. I could show you all of\pthem, but you would fall through\nthree.$"

EcruteakCity_EventScript_Npc7::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc7_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc7_Text:
	.string "At dusk the tower throws its\nshadow all the way to my washing\pline.\pI have moved the line twice. The\nshadow follows.\pA joke, child. The tower has stood\nthere longer than the line has.\pBut I do hang the washing early\nnow.$"

PoxEcruteak_WestEntrance::
	lockall
	warp MAP_GATE_ECRUTEAK_CITY_ROUTE38_HNS, 10, 5
	waitstate
	releaseall
	end

PoxEcruteak_EastExit::
	lockall
	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, PoxEcruteak_EastExit_Open
	goto_if_unset FLAG_BADGE03_GET, PoxEcruteak_EastExit_Closed
PoxEcruteak_EastExit_Open::
	warp MAP_ROUTE119, 5, 124
	waitstate
	releaseall
	end
PoxEcruteak_EastExit_Closed::
	msgbox PoxEcruteak_Text_EastExitClosed, MSGBOX_DEFAULT
	releaseall
	end

PoxEcruteak_Text_EastExitClosed::
	.string "The east road is shut.\nNo one goes past the last lamp\npwhile MORTY is under the tower.$"

PoxEcruteak_EastWatch::
	lock
	faceplayer
	goto_if_set FLAG_BADGE03_GET, PoxEcruteak_EastWatch_Open
	msgbox PoxEcruteak_Text_EastWatch, MSGBOX_NPC
	release
	end

PoxEcruteak_EastWatch_Open::
	msgbox PoxEcruteak_Text_EastWatchOpen, MSGBOX_NPC
	release
	end

PoxEcruteak_Text_EastWatch::
	.string "ROUTE 119 is east, past the last\nlamp. The watch keeps it shut\npwhile MORTY is under the tower.\pNot a lockdown. Ask anyone on\nthis street. The road is shut\npbecause the man who reads the\ntower is under it.$"

PoxEcruteak_Text_EastWatchOpen::
	.string "ROUTE 119 is open. The decks are\nwet and the river is loud, so\pmind your footing on the way down.\pTell the gate on the other side\nthat ECRUTEAK sent you.$"
