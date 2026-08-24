GoldenrodCity_BillsHouse_hns_MapScripts::
	.byte 0

GoldenrodCity_BillsHouse_EventScript_Npc1::
	lock
	faceplayer
	msgbox GoldenrodCity_BillsHouse_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

GoldenrodCity_BillsHouse_EventScript_Npc2::
	lock
	faceplayer
	msgbox GoldenrodCity_BillsHouse_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

GoldenrodCity_BillsHouse_EventScript_Npc3::
	lock
	faceplayer
	msgbox GoldenrodCity_BillsHouse_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

GoldenrodCity_BillsHouse_EventScript_Npc1_Text:
	.string "...If you hit dead ends on ROUTE 25,\ncome back and tell nobody.$"

GoldenrodCity_BillsHouse_EventScript_Npc2_Text:
	.string "Our Bill's away again. Somewhere north\nof everywhere, he said. Men!$"

GoldenrodCity_BillsHouse_EventScript_Npc3_Text:
	.string "Grandpa caught an EEVEE once. I want\nseven of my own someday!$"

