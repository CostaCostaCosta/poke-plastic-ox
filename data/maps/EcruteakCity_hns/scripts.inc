EcruteakCity_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_EcruteakCity_hns
	.byte 0

EcruteakCity_EventScript_Npc2::
	lock
	faceplayer
	goto_if_unset FLAG_POX_STORY_BURNED_TOWER, EcruteakCity_EventScript_Npc2_Before
	msgbox EcruteakCity_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc2_Before::
	msgbox EcruteakCity_EventScript_Npc2_Before_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc2_Before_Text:
	.string "You can't cast a bell twice.\nThe second one always has a seam\nin the ring, and the whole street\ncan hear it.\pThe old ceremonial bell went down\nwith the tower. Nobody has found\pit in the ash, and I have stopped\nasking the sages to look.\pThe BURNED TOWER remembers the\nfire. The fire remembers nothing.$"

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
	.string "MORTY is back up. The door opens\nonce he signs your BADGE.\pPast it, ROUTE 119 runs east and\ndown to the water. Mind the decks.\pThe river has been higher since\nthe spring.$"

EcruteakCity_EventScript_Npc5::
	lock
	faceplayer
	goto_if_set FLAG_POX_STORY_BURNED_TOWER, EcruteakCity_EventScript_Npc5_After
	msgbox EcruteakCity_EventScript_Npc5_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc5_After::
	msgbox EcruteakCity_EventScript_Npc5_After_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc5_Text:
	.string "That door is the BURNED TOWER.\nI swept its steps as a boy, the\pyear before the fire took the top\nfloors in a single night.\pMind the boards if you go in.\nHalf of them are charcoal\pthat somebody painted brown.$"

EcruteakCity_EventScript_Npc5_After_Text:
	.string "The sages went out with packs on\ntheir backs. Somebody still has\pto sweep the tower steps.\pAsh comes up through the boards\nevery time it rains. I sweep it\pback out. The tower and I have\nan understanding.$"

EcruteakCity_EventScript_Npc6::
	lock
	faceplayer
	goto_if_unset FLAG_POX_STORY_BURNED_TOWER, EcruteakCity_EventScript_Npc6_Before
	msgbox EcruteakCity_EventScript_Npc6_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc6_Before::
	msgbox EcruteakCity_EventScript_Npc6_Before_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc6_Before_Text:
	.string "My father measured the tower every\nspring. Every beam, every stair,\pdown to the gap where the old one\nfell.\pHe says a building is a set of\nmeasurements that agrees with\pitself. The tower stopped agreeing\nthe night it burned.\pHe still writes the numbers down.\nNobody has asked for his ledger.$"

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

PoxEcruteak_EastGateBlock::
	goto_if_set FLAG_BADGE03_GET, PoxEcruteak_EastGateBlock_End
	lockall
	msgbox PoxEcruteak_EastGateBlock_Text, MSGBOX_DEFAULT
	applymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkLeft
	waitmovement 0
	releaseall
PoxEcruteak_EastGateBlock_End::
	end

PoxEcruteak_EastGateBlock_Text:
	.string "Hold it. The east door stays shut\nuntil MORTY signs your BADGE.$"
