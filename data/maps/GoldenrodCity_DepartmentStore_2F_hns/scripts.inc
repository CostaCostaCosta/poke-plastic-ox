GoldenrodCity_DepartmentStore_2F_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxGoldenrod_ReturnGoldenrodCity_DepartmentStore_2F_hns
	.byte 0
PoxGoldenrod_ReturnGoldenrodCity_DepartmentStore_2F_hns::
	setdynamicwarp MAP_GOLDENROD_CITY_DEPARTMENT_STORE_2F_HNS, 9, 5
	end

PoxGoldenrod_GoldenrodCity_DepartmentStore_2F_hns_1::
	msgbox PoxGoldenrod_GoldenrodCity_DepartmentStore_2F_hns_1_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_DepartmentStore_2F_hns_1_Text:
	.string "The BALL counter runs out on\ncontest days at the park.$"

PoxGoldenrod_GoldenrodCity_DepartmentStore_2F_hns_2::
	msgbox PoxGoldenrod_GoldenrodCity_DepartmentStore_2F_hns_2_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_DepartmentStore_2F_hns_2_Text:
	.string "I keep ANTIDOTES for the tunnel.\nThose bugs don't respect shoes.$"

PoxGoldenrod_GoldenrodCity_DepartmentStore_2F_hns_3::
	msgbox PoxGoldenrod_GoldenrodCity_DepartmentStore_2F_hns_3_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_DepartmentStore_2F_hns_3_Text:
	.string "My shopping list says POTIONS.\nMy wallet says one POTION.$"
