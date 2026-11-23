FortreeCity_House2_MapScripts::
	.byte 0

@ Plastic Ox: the old Hidden Power / Sleep Talk room is now the riggers'
@ house. Birch already hands over every TM and tutor move, so the two
@ residents keep the town's walkways instead of teaching anything.

FortreeCity_House2_EventScript_SpanKeeper::
	lock
	faceplayer
	goto_if_set FLAG_BADGE04_GET, FortreeCity_House2_EventScript_SpanKeeperAfterBadge
	msgbox FortreeCity_House2_Text_SpanKeeper, MSGBOX_DEFAULT
	release
	end

FortreeCity_House2_EventScript_SpanKeeperAfterBadge::
	msgbox FortreeCity_House2_Text_SpanKeeperAfterBadge, MSGBOX_DEFAULT
	release
	end

FortreeCity_House2_EventScript_OldRigger::
	msgbox FortreeCity_House2_Text_OldRigger, MSGBOX_NPC
	end

FortreeCity_House2_Text_SpanKeeper:
	.string "This is the riggers' house.\n"
	.string "I keep the span ledger.\p"
	.string "Every walkway in FORTREE has a page:\n"
	.string "who tied it, who tested it,\l"
	.string "and how much wind it took.\p"
	.string "The east span over the gate keeps\n"
	.string "sagging. Something heavy sits there\l"
	.string "that I can't see in my ledger.$"

FortreeCity_House2_Text_SpanKeeperAfterBadge:
	.string "The east span sprang back up\n"
	.string "this morning. No more sag.\p"
	.string "I wrote it down as 'load removed,\n"
	.string "cause unknown.' Best I can do.$"

FortreeCity_House2_Text_OldRigger:
	.string "Years ago, trainers climbed up here\n"
	.string "so I could teach their POKéMON\l"
	.string "a trick or two.\p"
	.string "Now they all arrive knowing every\n"
	.string "move already. Fine by me.\p"
	.string "I teach knots now. A bowline holds\n"
	.string "a walkway better than SLEEP TALK.$"
