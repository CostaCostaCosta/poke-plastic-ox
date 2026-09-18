@ Fixed Gen 2 fruit trees: one berry per tree per day, with no planting.
	.macro pox_fruit_tree name:req, berry:req, picked:req
	.global PlasticOx_BerryTree_\name
PlasticOx_BerryTree_\name\():
	lockall
	call_if_unset FLAG_SYS_CLOCK_SET, PlasticOx_BerryTree_InitClock
	goto_if_set \picked, PlasticOx_BerryTree_Empty
	bufferitemname STR_VAR_1, \berry
	msgbox PlasticOx_BerryTree_Ask, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, PlasticOx_BerryTree_End
	giveitem \berry, 1
	goto_if_eq VAR_RESULT, FALSE, PlasticOx_BerryTree_BagFull
	setflag \picked
	goto PlasticOx_BerryTree_End
	.endm

	pox_fruit_tree Sitrus, ITEM_SITRUS_BERRY, FLAG_POX_DAILY_R29_SITRUS
	pox_fruit_tree Lum, ITEM_LUM_BERRY, FLAG_POX_DAILY_R46_LUM
	pox_fruit_tree Liechi, ITEM_LIECHI_BERRY, FLAG_POX_DAILY_R46_LIECHI
	pox_fruit_tree Salac, ITEM_SALAC_BERRY, FLAG_POX_DAILY_R44_SALAC
	pox_fruit_tree Petaya, ITEM_PETAYA_BERRY, FLAG_POX_DAILY_R44_PETAYA
	.purgem pox_fruit_tree

PlasticOx_BerryTree_InitClock:
	callnative InitTimeBasedEvents
	return

PlasticOx_BerryTree_BagFull:
	msgbox PlasticOx_BerryTree_NoRoom, MSGBOX_DEFAULT
	goto PlasticOx_BerryTree_End

PlasticOx_BerryTree_Empty:
	msgbox PlasticOx_BerryTree_NotRipe, MSGBOX_DEFAULT
PlasticOx_BerryTree_End:
	releaseall
	end

PlasticOx_BerryTree_Ask:
	.string "It's a BERRY tree!\n"
	.string "Pick the {STR_VAR_1}?$"

PlasticOx_BerryTree_NotRipe:
	.string "It's a BERRY tree!\n"
	.string "More BERRIES will ripen tomorrow.$"

PlasticOx_BerryTree_NoRoom:
	.string "There's no room for this BERRY\n"
	.string "in the BAG.$"
