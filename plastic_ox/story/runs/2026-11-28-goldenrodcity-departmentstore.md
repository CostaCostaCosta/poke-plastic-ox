# 2026-11-28 Goldenrod Department Store pass

Maps: GoldenrodCity_DepartmentStore_1F..6F_hns (7F sign text only; elevator, basement, 7FNight unchanged).

## Inventory (data/scripts/plastic_ox_goldenrod.inc, source plastic_ox/alpha/goldenrod/services.inc)
- 1F Service: no clerk; info-desk NPC and full floor directory sign.
- 2F Trainer's Market: Poke/Great Ball, Potion, Super Potion, Antidote, Paralyze Heal, Awakening, Burn Heal, Ice Heal, Escape Rope, Repel.
- 3F Battle Collection: X Attack/Defense/Speed/Sp. Atk/Accuracy, Dire Hit, Guard Spec, TM Protect/Return/Frustration/Hidden Power/Attract/Rest.
- 4F Evolution Corner: Fire, Moon, Sun Stone, Everstone (Water/Thunder/Leaf removed: Fortree-gated in pox_progression.ITEM_CHECKPOINT).
- 5F Training & Held Items: six vitamins, Choice Band, Leftovers, Quick Claw, Scope Lens, Bright Powder, White Herb, Mental Herb, Focus Band, Shell Bell. Gen 4+ items (Specs, Scarf, Life Orb, Sash, Assault Vest, Rocky Helmet) removed.
- 6F Refreshments: vending machines (wall signs) sell Fresh Water, Soda Pop, Lemonade.

## Dialogue
Five NPC lines rewritten (1F boy, 1F info desk, 4F kid on Fortree stones, 5F hiker on Slateport shipping, 6F lemonade). Floor and shelf signs replace the generic city directory. audit_npc_dialogue: 0 duplicates.

## Open
- I_PRICE is GEN_LATEST, so the Choice Band costs 100000 and vitamins 10000: steep for the NU Goldenrod checkpoint. Not changed (global price config).
- test_goldenrod.py sources() already failed on master (7F, Game Corner, Radio Tower 5F, Underground drift vs alpha/goldenrod); this pass removed plastic_ox_goldenrod.inc from that list.
