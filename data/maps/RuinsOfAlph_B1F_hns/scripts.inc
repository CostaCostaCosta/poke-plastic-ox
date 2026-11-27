RuinsOfAlph_B1F_hns_MapScripts::
	.byte 0

@ Plastic Ox: the hall under the chambers. Reached by the dig site's middle
@ stair or by falling from a Words Room. Wild UNOWN only; no donor visitors,
@ fossils, GS BALL or wall text.
PoxRuins_HallSurveyor::
	msgbox PoxRuins_Text_HallSurveyor, MSGBOX_NPC
	end

PoxRuins_Text_HallSurveyor:
	.string "Four holes in the ceiling, and\n"
	.string "four of us on the team who limp.\p"
	.string "That's how this hall was found.\n"
	.string "The stair got dug out afterwards.$"
