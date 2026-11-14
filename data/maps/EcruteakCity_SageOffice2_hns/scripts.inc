EcruteakCity_SageOffice2_hns_MapScripts::
	.byte 0

PoxEcruteak_SageOffice2_Caretaker::
	lock
	faceplayer
	goto_if_set FLAG_POX_STORY_BURNED_TOWER, PoxEcruteak_SageOffice2_Caretaker_After
	msgbox PoxEcruteak_SageOffice2_Caretaker_Before_Text, MSGBOX_NPC
	release
	end
PoxEcruteak_SageOffice2_Caretaker_After::
	msgbox PoxEcruteak_SageOffice2_Caretaker_After_Text, MSGBOX_NPC
	release
	end

PoxEcruteak_SageOffice2_Caretaker_Before_Text:
	.string "I dust these five and turn them to\nface the door. They were sages,\pand every one of them hated a\ndraft.\pThe tower keeps its own warm. We\nonly keep the office.$"

PoxEcruteak_SageOffice2_Caretaker_After_Text:
	.string "Two of the sages left this morning\nwith the good lamp.\pI turned the statues to face the\ndoor anyway. It is what you do\pwhen somebody might come back.$"

PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign0::
	msgbox PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign0_Text, MSGBOX_SIGN
	end

PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign0_Text:
	.string "A carved ancestor of the SAGES.\nThe stone is warm at the base.$"

PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign1::
	msgbox PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign1_Text, MSGBOX_SIGN
	end

PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign1_Text:
	.string "A carved ancestor of the SAGES.\nSomeone has left a fresh chestnut.$"

PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign2::
	msgbox PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign2_Text, MSGBOX_SIGN
	end

PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign2_Text:
	.string "A carved ancestor of the SAGES.\nThe eyes were recut later on.$"

PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign3::
	msgbox PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign3_Text, MSGBOX_SIGN
	end

PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign3_Text:
	.string "A carved ancestor of the SAGES.\nThe name on the plinth is worn.$"

PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign4::
	msgbox PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign4_Text, MSGBOX_SIGN
	end

PoxEcruteak_EcruteakCity_SageOffice2_hns_Sign4_Text:
	.string "A carved ancestor of the SAGES.\nThe chisel marks point north.$"
