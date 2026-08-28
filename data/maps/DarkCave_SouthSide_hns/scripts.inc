DarkCave_SouthSide_hns_MapScripts::
	.byte 0

DarkCave_EventScript_ToRoute31::
	warp MAP_ROUTE31_HNS, 48, 10
	waitstate
	end

DarkCave_EventScript_ToRoute46::
	warp MAP_ROUTE46_HNS, 20, 12
	waitstate
	end

DarkCave1_EventScript_ItemPotion::
	finditem ITEM_POTION
	end

DarkCave1_EventScript_ItemRevive::
	finditem ITEM_REVIVE
	end

DarkCave1_EventScript_ItemMaxRevive::
	finditem ITEM_MAX_REVIVE
	end

DarkCave1_EventScript_ItemElixir::
	finditem ITEM_ELIXIR
	end
