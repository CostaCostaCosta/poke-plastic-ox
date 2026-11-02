GoldenrodCity_UndergroundStorage_hns_MapScripts::
	.byte 0

PoxGoldenrod_GoldenrodCity_UndergroundStorage_hns_0::
	finditem ITEM_ULTRA_BALL
	end

PoxGoldenrod_GoldenrodCity_UndergroundStorage_hns_1::
	finditem ITEM_MAX_ETHER
	end

PoxGoldenrod_GoldenrodCity_UndergroundStorage_hns_2::
	finditem ITEM_TM_CALM_MIND
	end

PoxGoldenrod_GoldenrodCity_UndergroundStorage_hns_6::
	msgbox PoxGoldenrod_GoldenrodCity_UndergroundStorage_hns_6_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_UndergroundStorage_hns_6_Text:
	.string "The store boxes come through here.\nKeep the narrow path clear.$"

PoxGoldenrod_UndergroundStorage_Guard::
	msgbox PoxGoldenrod_UndergroundStorage_Guard_Text, MSGBOX_NPC
	end
PoxGoldenrod_UndergroundStorage_Guard_Text:
	.string "Storage ends here. The old switch\nchamber is closed for now.$"
