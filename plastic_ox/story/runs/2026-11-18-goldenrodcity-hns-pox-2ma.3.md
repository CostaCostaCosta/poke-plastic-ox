# goldenrodcity-hns: pox-2ma.3 Flower Shop SquirtBottle after Sudowoodo cleared

- Pox_SquirtBottle (GoldenrodCity_FlowerShop_hns, (2,4)) now checks FLAG_POX_SUDOWOODO_CLEARED first and shows a new thank-you line instead of re-issuing the bottle (Pox_Sudowoodo_Cleared removes it on purpose).
- PoxGoldenrod_SquirtBottleNote (street woman, (27,15)) has a post-clear line that no longer says the shop lends a bottle.
- New strings: Pox_Text_SquirtBottle_Cleared, PoxGoldenrod_Text_SquirtBottleNoteCleared (unique, no lore dump).
- Tests: ROM build zero errors; check_story_notes --note goldenrodcity-hns 0 errors; build_wiki --check current (site regenerated, build.json/region.html refreshed).
- Not walked in mGBA; logic is a flag branch placed before the giveitem path.
