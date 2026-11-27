# 2026-11-27 — Celebi and the GS BALL

**Bible:** new section *Celebi — Ilex Forest (optional)*; the Ilex Forest paragraph points to it.

## What changed
- `ITEM_GS_BALL` (891), a key item: the Trick House puzzle 5 prize, replacing TM Taunt (badge 6 gate = OU unlock).
- Ilex Forest shrine: a sage (24,28) and Celebi (24,26), shown after `FLAG_POX_STORY_BURNED_TOWER` until `FLAG_POX_CAUGHT_CELEBI` (temp flag 1, set from the Ilex arrival callback).
- Without the GS BALL the sage only talks; with it, `pox_legendary_sage` runs (TRAINER_PLASTIC_OX_CELEBI_SAGE 963, six-mon ADV OU grass team, Celebi Lv 55).
- The sage comes home to the Ecruteak sage office once Celebi is caught and counts toward the Tin Tower keeper's five.
- Installer: `plastic_ox/alpha/celebi.py` (after tin_tower in region_v7). Harness: `plastic_ox/demo/test_celebi.py`.

## Notes updated
- `ilexforest-hns.md`: "Must not" now allows the post-tower, GS-BALL-gated sage.
- `route110.md`: open question resolved.
