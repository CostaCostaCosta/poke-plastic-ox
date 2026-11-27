---
title: Goldenrod Radio Tower 5F
slug: goldenrodcity-radiotower-5f-hns
kind: Building
act: 4
stage: "12 — Saffron opens (optional, after New Mauville's generator and the Space Center)"
depth: supporting
wiki: none
maps: [GoldenrodCity_RadioTower_5F_hns]
flags: [FLAG_POX_CAUGHT_ZAPDOS, FLAG_POX_STORY_SPACE_CENTER, FLAG_POX_CAUGHT_SUICUNE, FLAG_POX_RANG_CLEAR_BELL]
trainers: [TRAINER_PLASTIC_OX_ZAPDOS_SAGE]
items: [ITEM_CLEAR_BELL]
status: drafted
---

# Goldenrod Radio Tower 5F

## Snapshot

The director's floor at the top of the Radio Tower: an office on the west side, a studio on the east, and the aerial overhead. For most of the game it is three people at work. Once New Mauville's generator is quiet and the OU region is open, Zapdos has moved into the closed east studio with a sage beside it. Catching it earns the CLEAR BELL, which sends the player back to Morty under the Burned Tower.

## Plot points

1. **An ordinary office.** The director `(11,9)`, the studio director `(29,5)` ("The roof aerial handles storms.") and the visitor `(20,12)` keep their Goldenrod import lines. Nothing here is a quest until the generator goes off.
2. **The static.** The engineer `PoxRadioTower_Engineer` `(30,13)` has three states: clean signal (generator running); static every night and the east studio closed (generator off, no OU); and a guest in the east studio with a man in robes (generator off and OU). He never names Zapdos and never connects it to New Mauville beyond "that old generator down south went dark."
3. **Zapdos and its sage.** ZAPDOS `(27,7)` with its sage `(27,8)` in front, both on `PoxRadioTower_ZapdosSage` (`pox_legendary_sage`, `TRAINER_PLASTIC_OX_ZAPDOS_SAGE`, Lv 55, ADV OU). They are hidden on transition by `FLAG_TEMP_1` unless `VAR_NEW_MAUVILLE_STATE == 2`, `FLAG_POX_STORY_SPACE_CENTER` is set and `FLAG_POX_CAUGHT_ZAPDOS` is clear. Beat the sage and any ball catches Zapdos. Afterwards the sage stands in the Ecruteak sage office at `(4,8)`.
4. **The CLEAR BELL.** Once Zapdos is caught, the engineer hands over `ITEM_CLEAR_BELL` (dug from the transmitter footing; it rang on its own the night Zapdos arrived; "old Ecruteak work"). He gives it once and then has an after line.
5. **Hand-off.** The bell is for Morty, who has waited under the Burned Tower since badge 3 (`plasticox-burnedtowerb1f`). Nobody here names him. The director's line about a bell tower in Ecruteak "before the fire" is the only pointer.

**Must not:** say "convergence"; explain why Zapdos chose the tower beyond the storm and the aerial; name Morty, Suicune or Raikou; make the static a Rocket plot (the Radio Tower takeover is not in v7); open the aerial or the roof, since there is no roof map.

## Key interactions

| Interaction | Where | Trigger / state | Behavior |
| --- | --- | --- | --- |
| Engineer | `(30,13)` `PoxRadioTower_Engineer` | `VAR_NEW_MAUVILLE_STATE`, `FLAG_POX_STORY_SPACE_CENTER`, `FLAG_POX_CAUGHT_ZAPDOS`, `checkitem ITEM_CLEAR_BELL` | four lines; gives the CLEAR BELL once Zapdos is caught |
| Zapdos sage | `(27,8)`, ZAPDOS `(27,7)` `PoxRadioTower_ZapdosSage` | shown by the on-transition script | sage battle, then reward capture; `FLAG_POX_CAUGHT_ZAPDOS` |
| Studio director | `(29,5)` | always | "The roof aerial handles storms." (kept: it reads differently afterwards) |
| Sage office | `EcruteakCity_SageOffice2_hns` `(4,8)` | `FLAG_POX_CAUGHT_ZAPDOS` | the Zapdos sage is home and counts toward five |

## Dialogue guidance

- **The engineer** is practical and a bit fed up. He talks about bands, gauges, inspectors and footings, and goes along with the man in robes because arguing sounds like more work.
- **The sage** is one of Morty's: courteous and unhurried, and he talks about the sky rather than the Pokémon's power.

> ENGINEER: Static on every band since that old generator down south went dark. Same hour, every night.

> SAGE: When the storm under HOENN went out, this one went looking for the next loudest sky.

## Inspiration

- **Zapdos at the Power Plant (Red/Blue):** an electric bird living in human machinery.
- **The Clear Bell (Crystal):** the Radio Tower director gives the bell that calls Suicune to the Tin Tower. Here an engineer gives it, and the Burned Tower answers it.

## Implementation hooks

- Owner: `plastic_ox/alpha/clear_bell.py` (+ `clear_bell/events.inc`, `clear_bell/trainers.party`), hooked last in `region_v7.apply_region`; writes `data/scripts/plastic_ox_clear_bell.inc`.
- Map: `GoldenrodCity_RadioTower_5F_hns`, on-transition `PoxRadioTower_OnTransition`.
- Flags: `FLAG_POX_CAUGHT_ZAPDOS` (`POX_EXT_FLAGS_START + 14`); gates `VAR_NEW_MAUVILLE_STATE`, `FLAG_POX_STORY_SPACE_CENTER`.
- Trainer: `TRAINER_PLASTIC_OX_ZAPDOS_SAGE` = 964.
- Item: `ITEM_CLEAR_BELL` = 892 (key item, Soothe Bell icon).
- Harness: `plastic_ox/demo/test_clear_bell.py`.

## Open questions

- No wiki page: the wiki only builds route, town, city and cave maps, and this is an indoor map. Its content shows on the region page through this note.
- Port a roof map so Zapdos sits on the aerial itself?
- Should the visitor `(20,12)` react to the static too?
