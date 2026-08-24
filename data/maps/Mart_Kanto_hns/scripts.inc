Mart_Kanto_hns_MapScripts::
	.byte 0

Mart_Kanto_hns_EventScript_Clerk::
	lock
	faceplayer
	msgbox Mart_Kanto_hns_Text_Clerk, MSGBOX_DEFAULT
	release
	end

Mart_Kanto_hns_EventScript_Youngster::
	lock
	faceplayer
	msgbox Mart_Kanto_hns_Text_Youngster, MSGBOX_DEFAULT
	release
	end

Mart_Kanto_hns_Text_Clerk:
	.string "Welcome! Stock arrives from JOHTO,\n"
	.string "HOENN, and right next door now.\l"
	.string "No shipping lanes. Just... doors.$"

Mart_Kanto_hns_Text_Youngster:
	.string "I bought a POTION here and the\n"
	.string "receipt had a SILPH CO. stamp\l"
	.string "on one side and a DEVON stamp on\l"
	.string "the other.$"
