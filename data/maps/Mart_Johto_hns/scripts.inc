Mart_Johto_hns_MapScripts::
	.byte 0

Mart_Johto_hns_EventScript_Clerk::
	lock
	faceplayer
	msgbox Mart_Johto_hns_Text_Clerk, MSGBOX_DEFAULT
	release
	end

Mart_Johto_hns_EventScript_Youngster::
	lock
	faceplayer
	msgbox Mart_Johto_hns_Text_Youngster, MSGBOX_DEFAULT
	release
	end

Mart_Johto_hns_Text_Clerk:
	.string "Hey, welcome! Our shelves just got\n"
	.string "restocked from three different\l"
	.string "regions at once.\p"
	.string "I'm still sorting it out, honestly.$"

Mart_Johto_hns_Text_Youngster:
	.string "The clerk says the delivery trucks\n"
	.string "don't need roads anymore.\p"
	.string "How does THAT work?$"
