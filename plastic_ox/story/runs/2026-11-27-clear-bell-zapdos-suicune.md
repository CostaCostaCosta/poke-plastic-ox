# 2026-11-27 — Clear Bell chain: Zapdos at the Radio Tower, Morty and Suicune

**Scope:** add Zapdos (Goldenrod Radio Tower 5F) after New Mauville's generator is off, the CLEAR BELL, and Morty waiting under the Burned Tower as Suicune's sage.

## Done
- `plastic_ox/alpha/clear_bell.py` (+ `clear_bell/events.inc`, `clear_bell/trainers.party`), hooked last in `region_v7.py`.
- Radio Tower 5F: ZAPDOS `(27,7)` and sage `(27,8)`, shown when `VAR_NEW_MAUVILLE_STATE == 2` and `FLAG_POX_STORY_SPACE_CENTER` is set; engineer `(30,13)` gives `ITEM_CLEAR_BELL` once Zapdos is caught.
- Burned Tower B1F: Morty `(16,12)` after badge 3 until Suicune is caught; he rings the bell and SUICUNE `(16,11)` appears. The Gym Morty is hidden for the same span; `FLAG_POX_HIDE_STORY_NPCS` is still honored there.
- Trainers 964 `TRAINER_PLASTIC_OX_ZAPDOS_SAGE`, 965 `TRAINER_PLASTIC_OX_SUICUNE_SAGE` (Morty), Lv 55 ADV OU.
- Flags `FLAG_POX_CAUGHT_ZAPDOS` (+14), `FLAG_POX_CAUGHT_SUICUNE` (+15), `FLAG_POX_RANG_CLEAR_BELL` (+16). (+13, trainer 963 and item 891 belong to Celebi/GS Ball, merged first.)
- Tin Tower office: the Zapdos sage comes home at `(4,8)` (`FLAG_TEMP_9`).
- The Raikou sage's intro now hints that something flew north when the hum stopped.
- Story bible: Gym 3 note plus the "Zapdos" and "Suicune" sections. New location note `goldenrodcity-radiotower-5f-hns.md`; Burned Tower notes updated.
