GoldenrodCity_UndergroundTunnel_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxGoldenrod_UndergroundTunnel_OnTransition
	.byte 0

@ Gen 2 haircut schedule. The older brother works Tue/Thu/Sat, the younger
@ brother works Sun/Mon/Wed. Neither works on Friday, so the off-duty brother
@ is hidden before the map's object events are created.
PoxGoldenrod_UndergroundTunnel_OnTransition::
	specialvar VAR_0x8004, PoxGetDayOfWeek
	switch VAR_0x8004
	case WEEKDAY_TUE, PoxGoldenrod_UndergroundTunnel_OlderOnDuty
	case WEEKDAY_THU, PoxGoldenrod_UndergroundTunnel_OlderOnDuty
	case WEEKDAY_SAT, PoxGoldenrod_UndergroundTunnel_OlderOnDuty
	case WEEKDAY_SUN, PoxGoldenrod_UndergroundTunnel_YoungerOnDuty
	case WEEKDAY_MON, PoxGoldenrod_UndergroundTunnel_YoungerOnDuty
	case WEEKDAY_WED, PoxGoldenrod_UndergroundTunnel_YoungerOnDuty
	setflag FLAG_POX_HIDE_HAIRCUT_OLDER
	setflag FLAG_POX_HIDE_HAIRCUT_YOUNGER
	return

PoxGoldenrod_UndergroundTunnel_OlderOnDuty::
	clearflag FLAG_POX_HIDE_HAIRCUT_OLDER
	setflag FLAG_POX_HIDE_HAIRCUT_YOUNGER
	return

PoxGoldenrod_UndergroundTunnel_YoungerOnDuty::
	setflag FLAG_POX_HIDE_HAIRCUT_OLDER
	clearflag FLAG_POX_HIDE_HAIRCUT_YOUNGER
	return

PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_0::
	msgbox PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_0_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_0_Text:
	.string "The tunnels stay warm all year.\nThat's why the barbers like it here.$"

PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_4::
	msgbox PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_4_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_4_Text:
	.string "Rain or shine, this path is dry.\nI walk it to work every morning.$"

PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_5::
	msgbox PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_5_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_5_Text:
	.string "My grandmother says these halls\nwere dug before the radio tower.$"

PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_6::
	msgbox PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_6_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_6_Text:
	.string "You can hear the repair crews\nthrough the wall. Just faintly.$"

PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_7::
	finditem ITEM_COIN_CASE
	end

PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_8::
	finditem ITEM_PARALYZE_HEAL
	end

PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_9::
	finditem ITEM_ANTIDOTE
	end

PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_10::
	finditem ITEM_SUPER_POTION
	end

PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_11::
	msgbox PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_11_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_UndergroundTunnel_hns_11_Text:
	.string "The old switch chamber is closed.\nI'll keep watch until the city\pneeds it again.$"
