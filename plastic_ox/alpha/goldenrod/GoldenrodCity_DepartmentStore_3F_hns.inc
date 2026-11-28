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
	.string "A SCOPE LENS won't help if you\nnever land a hit. Trust me.$"

PoxGoldenrod_GoldenrodCity_DepartmentStore_3F_hns_1::
	msgbox PoxGoldenrod_GoldenrodCity_DepartmentStore_3F_hns_1_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_DepartmentStore_3F_hns_1_Text:
	.string "A FOCUS BAND held on against\nWHITNEY. Only once, but enough.$"
