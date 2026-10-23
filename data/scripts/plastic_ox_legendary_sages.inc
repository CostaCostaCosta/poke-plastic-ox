@ Reusable legendary encounter. Both overworld actors invoke `entry` and use
@ caught_flag as their hide flag. The trainer's own victory flag persists the
@ unlocked capture. Losses retry; fleeing/KO/declining never consume the reward.
@ Keep this macro before all invocations in event_scripts.s.
.macro pox_legendary_sage entry:req, trainer:req, species:req, level:req, caught_flag:req, sage_id:req, legendary_id:req, intro:req, defeat:req
.global \entry
\entry:
	lockall
	goto_if_set \caught_flag, \entry\()_End
	goto_if_defeated \trainer, \entry\()_Reward
	trainerbattle_single \trainer, \intro, \defeat, \entry\()_Reward
	goto \entry\()_Reward
\entry\()_Reward:
	msgbox PoxLegendary_Text_Reward, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, \entry\()_End
	closemessage
	setwildbattle \species, \level, ITEM_NONE
	special BattleSetup_StartLegendaryRewardBattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, \entry\()_End
	setflag \caught_flag
	removeobject \sage_id
	removeobject \legendary_id
\entry\()_End:
	releaseall
	end
.endm

PoxLegendary_Text_Reward::
	.string "You have earned this POKéMON's trust.\n"
	.string "Throw any BALL and it will join you.\p"
	.string "You may return if you need supplies.\n"
	.string "Approach the POKéMON now?$"
