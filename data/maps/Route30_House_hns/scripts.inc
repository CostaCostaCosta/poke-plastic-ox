Route30_House_hns_MapScripts::
	.byte 0

Route30_House_EventScript_Resident::
	lock
	faceplayer
	msgbox Route30_House_Text_Resident, MSGBOX_NPC
	release
	end

Route30_House_Text_Resident:
	.string "Travelers have been coming through\n"
	.string "ROUTE 30 from every direction.$"
