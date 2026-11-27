---
title: New Mauville
slug: newmauville-inside
kind: Building
act: 3
stage: "11 — Mossdeep and the Space Center (optional, after badge 6)"
depth: supporting
wiki: newmauville-inside
maps: [NewMauville_Inside]
flags: [FLAG_POX_CAUGHT_RAIKOU, FLAG_BADGE06_GET, FLAG_POX_TOURNAMENT_REWARD_3]
trainers: [TRAINER_PLASTIC_OX_RAIKOU_SAGE]
items: [ITEM_NEW_MAUVILLE_KEY]
status: drafted
---

# New Mauville

## Snapshot

A sealed power plant under Route 110 with an old generator still running hot and nobody minding it. Raikou has settled at the generator's foot, and a sage from the Burned Tower keeps watch beside it. It's an optional legendary home after badge 6: switch the machine off, earn the sage's blessing, and Raikou can come with you. The mood is a quiet, hot, humming room that calms down once you've been through it.

## Plot points

1. **Key.** `ITEM_NEW_MAUVILLE_KEY` is REX's round-three prize at the Underground Path tournament (`PoxTournament_Reward3`, `FLAG_POX_TOURNAMENT_REWARD_3`). REX tells the player to quiet the generator, then meet the sage.
2. **Door.** `NewMauville_Entrance` (owned by the `route110` note) opens only with the key and `FLAG_BADGE06_GET`. Without both, `PoxTournament_ResetMauvilleDoor` keeps it shut.
3. **The plant.** Blue and green floor switches move the barriers. Three Voltorb sit disguised as item balls. Both are vanilla and stay that way.
4. **Sage before the switch.** `PoxTournament_Raikou` at `(31,6)` with `VAR_NEW_MAUVILLE_STATE` ≠ 2: the generator is upsetting Raikou, so find the red stop switch.
5. **Red switch.** `NewMauville_Inside_EventScript_RedButton` sets `VAR_NEW_MAUVILLE_STATE` to 2 and turns the generator tiles off.
6. **Sage battle → Raikou.** `pox_legendary_sage` runs `TRAINER_PLASTIC_OX_RAIKOU_SAGE`, then offers Raikou at Lv.55 with a guaranteed catch. `FLAG_POX_CAUGHT_RAIKOU` hides both objects, and the sage reappears in the Ecruteak sage office (`ecruteakcity-hns`) and counts toward the Bellchime Trail keeper's five.

**Must not:** make Raikou or the generator evidence for the convergence's cause; have anyone explain why a Johto legend chose a Hoenn ruin; turn the plant into a Team Rocket or Silph site; name the other beasts' homes.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Sage | `(31,6)` `PoxTournament_Raikou` | no badge 6 or no key | "The ancient power remains sealed." (shared seal text) | normally unreachable because the door enforces the same gate; keep it as a fallback |
| Sage | `(31,6)` | generator on | `PoxTournament_Text_Power`, two lines | keep the request, add one line about how long they've been keeping watch |
| Sage | `(31,6)` | generator off | `PoxTournament_Text_Raikou` → battle | an intro that says Raikou chose this place, rather than one that only names Morty |
| Raikou | `(31,7)` | same script as the sage | runs the sage script | keep; play `SPECIES_RAIKOU`'s cry on first talk before the generator is off |
| Generator | bg events `(32..35,2..4)` | `VAR_NEW_MAUVILLE_STATE` | vanilla heat / quieted text | keep the vanilla text |
| Red switch | `(33,6)` | once | stops the generator | keep |
| Voltorb ×3 | `(25,18)`, `(6,11)`, `(13,10)` | vanilla flags | wild Lv.25 | keep; they live in the plant too |

## Dialogue guidance

- **The sage** has been here a while and smells of ozone. They're patient, practical and a little proud of Raikou's choice, like a wildlife keeper. Their voice differs from the Entei sage: this one talks about weather and sound, not heat and ash.
- **REX** (tournament) only points the way; no lore.
- Nobody else speaks here. The plant is empty of people on purpose.

> SAGE: The machine roars and it answers. Neither will rest until one of them goes quiet.

> SAGE: It ran from the tower looking for a storm. This was the nearest thing.

> SAGE: It stopped pacing once the hum went out. I think it will stay, or go with someone it trusts.

- **Do not:** say "convergence" aloud; call Raikou lost or a prisoner (it chose this place); reuse the Entei sage's lines or `PoxTournament_Text_Regi` wording; explain where the generator's power goes.

## Inspiration

- **Abandoned substations and Chernobyl-era control rooms:** a machine still running with no operators. It becomes the sage's line about the hum.
- **Raikou's lore as the thunder that fell with the tower:** the beast went looking for its own weather. It becomes "looking for a storm".
- **Wildlife living in human ruins** (storks on power pylons, bats in old bunkers): the animal makes a home of what people left behind. It becomes the sage's pride in Raikou's choice.

## Implementation hooks

- Wiki page: `newmauville-inside.html` (listed in `EXTRA_PAGES` in `plastic_ox/wiki/build_wiki.py`, since no seam reaches it).
- Map: `NewMauville_Inside`. Its one warp goes back to `NewMauville_Entrance`, which belongs to `route110`.
- Objects `LOCALID_POX_RAIKOU_SAGE` / `LOCALID_POX_RAIKOU` are generator-owned: `plastic_ox/alpha/tournament.py` (`actors('NewMauville_Inside', ...)`). Edit there, not in `map.json`.
- Scripts: `data/scripts/plastic_ox_tournament.inc` (`PoxTournament_Raikou`, `PoxTournament_PowerOn`, `PoxTournament_RaikouBattle`, `PoxTournament_LegendLocked`) is emitted from `plastic_ox/alpha/tournament/events.inc`. The macro lives in `data/scripts/plastic_ox_legendary_sages.inc`.
- Trainer: `TRAINER_PLASTIC_OX_RAIKOU_SAGE` (party source `plastic_ox/alpha/tournament/trainers.party`).
- Flags/vars: `FLAG_POX_CAUGHT_RAIKOU`, `FLAG_BADGE06_GET`, `FLAG_POX_TOURNAMENT_REWARD_3`, `VAR_NEW_MAUVILLE_STATE` (0 sealed, 1 open, 2 generator off).
- Known gaps: all three sage lines are generic; the intro names Morty but not why Raikou is here; there's no harness for this map yet, so a `plastic_ox/demo/test_new_mauville.py` should cover the key → door → switch → sage → catch path.

## Open questions

- Should the sage get a post-catch line here before leaving, or does their appearance in the Ecruteak office cover it?
- Is badge 6 the right gate, given that the Raikou sage's party is Lv.55 and Raikou is Lv.55 (the same as Regice/Registeel)?
