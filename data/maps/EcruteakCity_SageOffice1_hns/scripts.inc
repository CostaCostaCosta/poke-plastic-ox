EcruteakCity_SageOffice1_hns_MapScripts::
	.byte 0

PoxEcruteak_EcruteakCity_SageOffice1_hns_0::
	lock
	faceplayer
	goto_if_set FLAG_POX_STORY_BURNED_TOWER, PoxEcruteak_SageOffice1_Sage0_After
	msgbox PoxEcruteak_SageOffice1_Sage0_Before_Text, MSGBOX_NPC
	release
	end
PoxEcruteak_SageOffice1_Sage0_After::
	msgbox PoxEcruteak_SageOffice1_Sage0_After_Text, MSGBOX_NPC
	release
	end

PoxEcruteak_SageOffice1_Sage0_Before_Text:
	.string "We walk the hill every morning and\ncome back arguing about the far\npside.\pToday it is my turn to walk. I am\nreading instead. Do not tell the\npother two.$"

PoxEcruteak_SageOffice1_Sage0_After_Text:
	.string "The two have gone. They took the\nblankets, the kettle and the good\nplamp.\pThe desk by the window is mine.\nI did not ask for the window.$"

PoxEcruteak_EcruteakCity_SageOffice1_hns_1::
	lock
	faceplayer
	goto_if_set FLAG_POX_STORY_BURNED_TOWER, PoxEcruteak_SageOffice1_Sage1_After
	msgbox PoxEcruteak_SageOffice1_Sage1_Before_Text, MSGBOX_NPC
	release
	end
PoxEcruteak_SageOffice1_Sage1_After::
	msgbox PoxEcruteak_SageOffice1_Sage1_After_Text, MSGBOX_NPC
	release
	end

PoxEcruteak_SageOffice1_Sage1_Before_Text:
	.string "Three of us share this office, and\none desk between us. The tower\npkeeps the rest.\pMORTY asks for what the tower\nneeds, not what we want. That is\npwhy the desk is small.$"

PoxEcruteak_SageOffice1_Sage1_After_Text:
	.string "They said to stay until it feels\nsafe. Nobody said how we would\npknow.\pSo we packed for a season and\nwrote everything down.$"

PoxEcruteak_EcruteakCity_SageOffice1_hns_2::
	lock
	faceplayer
	goto_if_set FLAG_POX_STORY_BURNED_TOWER, PoxEcruteak_SageOffice1_Sage2_After
	msgbox PoxEcruteak_SageOffice1_Sage2_Before_Text, MSGBOX_NPC
	release
	end
PoxEcruteak_SageOffice1_Sage2_After::
	msgbox PoxEcruteak_SageOffice1_Sage2_After_Text, MSGBOX_NPC
	release
	end

PoxEcruteak_SageOffice1_Sage2_Before_Text:
	.string "MORTY has been under the tower\nsince the last observance. We keep\pthe office and wait.\pWaiting is a skill.\nI am bad at it.$"

PoxEcruteak_SageOffice1_Sage2_After_Text:
	.string "The orders came before breakfast.\nShelter what was moved. Stay until\pit feels safe. Write down\peverything.\pI asked how long. He said,\nuntil.$"

PoxEcruteak_EcruteakCity_SageOffice1_hns_Sign0::
	msgbox PoxEcruteak_EcruteakCity_SageOffice1_hns_Sign0_Text, MSGBOX_SIGN
	end

PoxEcruteak_EcruteakCity_SageOffice1_hns_Sign0_Text:
	.string "ECRUTEAK SAGE OFFICES.\nPlease keep your voice down.$"
