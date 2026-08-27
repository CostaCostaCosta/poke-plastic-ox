House_GenericB_hns_MapScripts::
	.byte 0

House_GenericB_hns_EventScript_Man::
	lock
	faceplayer
	msgbox House_GenericB_hns_Text_Man, MSGBOX_DEFAULT
	release
	end

House_GenericB_hns_EventScript_Boy::
	lock
	faceplayer
	msgbox House_GenericB_hns_Text_Boy, MSGBOX_DEFAULT
	release
	end

House_GenericB_hns_Text_Man:
	.string "My cousin lives in a town with the\n"
	.string "same houses and the same people.\p"
	.string "Or maybe I live THERE and he lives\n"
	.string "here. The mail gets confused.$"

House_GenericB_hns_Text_Boy:
	.string "I'm collecting stories about the\n"
	.string "merged region!\p"
	.string "You're a trainer, right? Tell me\n"
	.string "one someday!$"
