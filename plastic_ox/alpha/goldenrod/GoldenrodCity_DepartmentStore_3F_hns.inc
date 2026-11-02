GoldenrodCity_DepartmentStore_3F_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxGoldenrod_ReturnGoldenrodCity_DepartmentStore_3F_hns
	.byte 0
PoxGoldenrod_ReturnGoldenrodCity_DepartmentStore_3F_hns::
	setdynamicwarp MAP_GOLDENROD_CITY_DEPARTMENT_STORE_3F_HNS, 9, 5
	end

PoxGoldenrod_GoldenrodCity_DepartmentStore_3F_hns_0::
	msgbox PoxGoldenrod_GoldenrodCity_DepartmentStore_3F_hns_0_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_DepartmentStore_3F_hns_0_Text:
	.string "A good TM stays useful for years.\nI lend mine to my sister.$"

PoxGoldenrod_GoldenrodCity_DepartmentStore_3F_hns_1::
	msgbox PoxGoldenrod_GoldenrodCity_DepartmentStore_3F_hns_1_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_DepartmentStore_3F_hns_1_Text:
	.string "PROTECT bought me one turn against\nWHITNEY. One was enough.$"
