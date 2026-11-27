RuinsOfAlph_Lab_hns_MapScripts::
	.byte 0

@ Plastic Ox: the research centre. No fossil reviver; two staff and a table of casts.
PoxRuins_Archivist::
	msgbox PoxRuins_Text_Archivist, MSGBOX_NPC
	end

PoxRuins_Text_Archivist:
	.string "Fourteen crates from CINNABAR and\n"
	.string "not one index among them.\p"
	.string "Whoever packed these filed the\n"
	.string "papers by weight.$"

PoxRuins_Epigrapher::
	msgbox PoxRuins_Text_Epigrapher, MSGBOX_NPC
	end

PoxRuins_Text_Epigrapher:
	.string "I copy the wall carvings. I can\n"
	.string "tell you every shape there is.\p"
	.string "What they say is another job, and\n"
	.string "nobody has applied for it.$"

PoxRuins_Casts::
	msgbox PoxRuins_Text_Casts, MSGBOX_SIGN
	end

PoxRuins_Text_Casts:
	.string "Plaster casts of shells from the\n"
	.string "pond bed. The label says the real\p"
	.string "ones are out on loan.$"
