GoldenrodCity_DepartmentStore_4F_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxGoldenrod_ReturnGoldenrodCity_DepartmentStore_4F_hns
	.byte 0
PoxGoldenrod_ReturnGoldenrodCity_DepartmentStore_4F_hns::
	setdynamicwarp MAP_GOLDENROD_CITY_DEPARTMENT_STORE_4F_HNS, 9, 5
	end

PoxGoldenrod_GoldenrodCity_DepartmentStore_4F_hns_0::
	msgbox PoxGoldenrod_GoldenrodCity_DepartmentStore_4F_hns_0_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_DepartmentStore_4F_hns_0_Text:
	.string "I found a FIRE STONE for a friend.\nNow I have to keep the secret.$"

PoxGoldenrod_GoldenrodCity_DepartmentStore_4F_hns_1::
	msgbox PoxGoldenrod_GoldenrodCity_DepartmentStore_4F_hns_1_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_DepartmentStore_4F_hns_1_Text:
	.string "The stones glow under this light.\nI don't know how they do it.$"

PoxGoldenrod_GoldenrodCity_DepartmentStore_4F_hns_2::
	msgbox PoxGoldenrod_GoldenrodCity_DepartmentStore_4F_hns_2_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_DepartmentStore_4F_hns_2_Text:
	.string "My partner wants to evolve.\nI'm still deciding when.$"
