PlasticOx_EventScript_HeadbuttTree::
	lockall
	special PlasticOx_CheckHeadbutt
	goto_if_eq VAR_RESULT, FALSE, PlasticOx_Headbutt_NoKey
	msgbox PlasticOx_Headbutt_Ask, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, PlasticOx_Headbutt_End
	closemessage
	playse SE_M_HEADBUTT
	waitse
	special PlasticOx_HeadbuttEncounter
	goto_if_eq VAR_RESULT, FALSE, PlasticOx_Headbutt_Empty
	waitstate
	releaseall
	end

PlasticOx_Headbutt_NoKey:
	msgbox PlasticOx_Headbutt_KeyText, MSGBOX_DEFAULT
	goto PlasticOx_Headbutt_End

PlasticOx_Headbutt_Empty:
	msgbox PlasticOx_Headbutt_EmptyText, MSGBOX_DEFAULT

PlasticOx_Headbutt_End:
	releaseall
	end

PlasticOx_Headbutt_Ask:
	.string "A sturdy tree! Use HEADBUTT to\n"
	.string "shake out a POKéMON?$"

PlasticOx_Headbutt_KeyText:
	.string "A POKéMON might be hiding here.\p"
	.string "Use HEADBUTT or the HEADBUTT KEY\n"
	.string "to shake it out.$"

PlasticOx_Headbutt_EmptyText:
	.string "No POKéMON can be shaken out now.$"
