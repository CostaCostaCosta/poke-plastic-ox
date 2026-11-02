GoldenrodCity_DepartmentStoreBasement_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxGoldenrod_BasementReturn
	.byte 0
PoxGoldenrod_BasementReturn::
	setdynamicwarp MAP_GOLDENROD_CITY_DEPARTMENT_STORE_BASEMENT_HNS, 10, 7
	end

PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_3::
	finditem ITEM_AMULET_COIN
	end

PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_4::
	finditem ITEM_ULTRA_BALL
	end

PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_5::
	finditem ITEM_EXP_SHARE
	end

PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_6::
	finditem ITEM_ETHER
	end

PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_7::
	msgbox PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_7_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_7_Text:
	.string "Crates from HOENN arrived at dawn.\nWe'll sort them before opening.$"

PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_8::
	msgbox PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_8_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_8_Text:
	.string "This lift groans with every load.\nThe mechanic says it's fine.$"

PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_9::
	msgbox PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_9_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_DepartmentStoreBasement_hns_9_Text:
	.string "I mark damaged boxes in red.\nThere are fewer than last week.$"
