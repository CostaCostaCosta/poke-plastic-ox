GoldenrodCity_BillsHouse_hns_MapScripts::
	.byte 0

@ BILL's father. BILL himself is never at home; he is out doing field work.
@ The mother (8,4) runs Pox_Family in data/scripts/plastic_ox_story.inc and
@ hands over the family EEVEE; the little sister is Npc3 below.
Pox_BillsHouse_Father::
	lock
	faceplayer
	msgbox Pox_BillsHouse_Text_Father, MSGBOX_NPC
	release
	end

Pox_BillsHouse_Text_Father:
	.string "Our son BILL sends gadgets home\ninstead of letters.\pThe last one hums all night.\nI unplug it before bed.$"

GoldenrodCity_BillsHouse_EventScript_Npc3::
	lock
	faceplayer
	msgbox GoldenrodCity_BillsHouse_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

GoldenrodCity_BillsHouse_EventScript_Npc3_Text:
	.string "Grandpa keeps the cottage by the\nsea. He has an EEVEE there.\pI want seven of my own someday!$"
