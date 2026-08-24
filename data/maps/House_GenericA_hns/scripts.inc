House_GenericA_hns_MapScripts::
	.byte 0

House_GenericA_hns_EventScript_OldMan::
	lock
	faceplayer
	msgbox House_GenericA_hns_Text_OldMan, MSGBOX_DEFAULT
	release
	end

House_GenericA_hns_EventScript_Boy::
	lock
	faceplayer
	msgbox House_GenericA_hns_Text_Boy, MSGBOX_DEFAULT
	release
	end

House_GenericA_hns_Text_OldMan:
	.string "I've lived in this house my whole\n"
	.string "life. Last month I woke up and\l"
	.string "the view outside was different.\p"
	.string "I've decided not to ask questions.$"

House_GenericA_hns_Text_Boy:
	.string "Grandpa says the town used to be\n"
	.string "smaller. I think it got bigger!\p"
	.string "There are more doors to knock on\n"
	.string "now.$"
