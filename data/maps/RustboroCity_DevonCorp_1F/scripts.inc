RustboroCity_DevonCorp_1F_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, RustboroCity_DevonCorp_1F_OnFrame
	.byte 0

RustboroCity_DevonCorp_1F_OnFrame:
	map_script_2 VAR_DEVON_CORP_1F_GREETING, 0, RustboroCity_DevonCorp_1F_EventScript_FirstGreeting
	.2byte 0

RustboroCity_DevonCorp_1F_EventScript_FirstGreeting::
	lockall
	msgbox RustboroCity_DevonCorp_1F_Text_MrStoneGreeting, MSGBOX_DEFAULT
	setvar VAR_DEVON_CORP_1F_GREETING, 1
	releaseall
	end

RustboroCity_DevonCorp_1F_EventScript_Employee::
	lock
	faceplayer
	msgbox RustboroCity_DevonCorp_1F_Text_ThoseShoesAreOurProduct, MSGBOX_DEFAULT
	release
	end

RustboroCity_DevonCorp_1F_EventScript_Greeter::
	lock
	faceplayer
	msgbox RustboroCity_DevonCorp_1F_Text_WelcomeToDevonCorp, MSGBOX_DEFAULT
	release
	end

RustboroCity_DevonCorp_1F_EventScript_TrainingKit::
	lock
	faceplayer
	msgbox RustboroCity_DevonCorp_1F_Text_TrainingKitDisplay, MSGBOX_DEFAULT
	release
	end

RustboroCity_DevonCorp_1F_EventScript_MrStone::
	lock
	faceplayer
	msgbox RustboroCity_DevonCorp_1F_Text_MrStoneFollowup, MSGBOX_DEFAULT
	release
	end

RustboroCity_DevonCorp_1F_EventScript_RocksMetalDisplay::
	msgbox RustboroCity_DevonCorp_1F_Text_RocksMetalDisplay, MSGBOX_SIGN
	end

RustboroCity_DevonCorp_1F_EventScript_ProductsDisplay::
	msgbox RustboroCity_DevonCorp_1F_Text_ProductDisplay, MSGBOX_SIGN
	end

RustboroCity_DevonCorp_1F_Text_WelcomeToDevonCorp:
	.string "Hello and welcome to the DEVON\n"
	.string "CORPORATION.\p"
	.string "We're proud producers of items and\n"
	.string "medicine that enhance your life.$"

RustboroCity_DevonCorp_1F_Text_MrStoneGreeting:
	.string "MR. STONE: Welcome to DEVON, {PLAYER}!\p"
	.string "I'm MR. STONE, the president.\n"
	.string "It's a pleasure to meet you.\p"
	.string "Our researchers are upstairs. Take\n"
	.string "a look around while you're here.$"

RustboroCity_DevonCorp_1F_Text_MrStoneFollowup:
	.string "MR. STONE: I hope you enjoy your\n"
	.string "visit to DEVON CORPORATION.$"

RustboroCity_DevonCorp_1F_Text_ThoseShoesAreOurProduct:
	.string "Hey, those RUNNING SHOES!\n"
	.string "They're one of our products!\p"
	.string "It makes me happy when I see someone\n"
	.string "using something we made.$"

RustboroCity_DevonCorp_1F_Text_RocksMetalDisplay:
	.string "Samples of rocks and metal are\n"
	.string "displayed in the glass case.\p"
	.string "There's a panel with some writing\n"
	.string "on it…\p"
	.string "“DEVON CORPORATION got its start as\n"
	.string "a producer of stones from quarries.\p"
	.string "“The company also produced iron from\n"
	.string "filings in the sand.\p"
	.string "“From that humble start as a producer\n"
	.string "of raw materials, DEVON developed.\p"
	.string "“DEVON is now a manufacturer of a wide\n"
	.string "range of industrial products.”$"

RustboroCity_DevonCorp_1F_Text_ProductDisplay:
	.string "Prototypes and test products fill\n"
	.string "the glass display case.\p"
	.string "There's a panel with a description…\p"
	.string "“In addition to industrial products,\n"
	.string "DEVON now markets sundries and\l"
	.string "pharmaceuticals for better lifestyles.\p"
	.string "“Recently, DEVON has begun marketing\n"
	.string "tools for POKéMON TRAINERS, including\l"
	.string "POKé BALLS and POKéNAV systems.”$"

RustboroCity_DevonCorp_1F_Text_TrainingKitDisplay:
	.string "DEVON helped develop the TRAINING KIT\n"
	.string "used at the POKéMON TRAINER'S SCHOOL.\p"
	.string "Their teacher can give you one.$"
