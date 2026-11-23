---
title: Cerulean Cave
slug: mtsilver-1f-waterfallroom-hns
kind: Cave
act: 6
stage: "17 — Post-game"
depth: supporting
wiki: mtsilver-1f-waterfallroom-hns
maps: [MtSilver_1F_WaterfallRoom_hns]
also_maps: [MtSilver_1F_ItemRoom_hns, MtSilver_1F_MoltresRoom_hns, MtSilver_MountainSide_hns, MtSilver_2F_hns, MtSilver_Snow_hns, MtSilver_3F_hns, MtSilver_SummitDay_hns]
flags: [FLAG_SYS_GAME_CLEAR, FLAG_POX_TRAINER_RED, FLAG_POX_CAUGHT_MEWTWO, FLAG_POX_RED_RESTING]
trainers: [TRAINER_PLASTIC_OX_RED]
status: implemented
---

# Cerulean Cave

## Snapshot

The post-game dungeon. A rock knoll in the grass nook on the west bank of Route 24 (`Route24_hns`, door at `(8,10)`) opens once the player is in the Hall of Fame. Behind it is the full Heart & Soul Mt. Silver interior: the waterfall room, its side rooms, the mountainside ledges, 2F, the snowfield, 3F, and a bare summit where RED stands with MEWTWO beside him. The emotional note is *quiet*: no music on the summit, no speech from RED, just the strongest trainer in the region waiting in the snow.

## Plot points

1. **Sealed until the record is made.** A League officer (`Route24_EventScript_CaveGuard`, `(8,11)`) stands in the cave mouth and is hidden by `FLAG_SYS_GAME_CLEAR`. Before the Hall of Fame he explains the closure; afterwards he is simply gone.
2. **The climb.** Wild Pokémon are the HNS Mt. Silver tables at Lv.60–69, with UNOWN (random letters) and WOBBUFFET added to every land table. Breakable rocks on 2F stay; item balls, decorative Pokémon and donor NPCs were not imported.
3. **RED and MEWTWO.** `MtSilver_SummitDay_hns` `(10,6)` RED, `(11,6)` MEWTWO, both running into `PoxCeruleanCave_RedBattle`. RED's ADV Ubers six (Mewtwo, Kyogre, Metagross, Snorlax, Latios, Deoxys-Attack) is the final battle of the game.
4. **The ending.** A win sets `FLAG_POX_TRAINER_RED`, shows the player's trainer card (`PoxShowPlayerTrainerCard`), then `GameClear`: the Hall of Fame records and displays the team, and the credits roll. A loss is an ordinary whiteout after RED's "…"; RED stays.
5. **Rematch.** A win also sets `FLAG_POX_RED_RESTING`, which hides RED. `PoxLeague_Hall` clears it on every Hall of Fame entry, so each new League win brings him back for the same battle and the same ending.
6. **MEWTWO stays behind.** While RED rests, but MEWTWO remains (hidden only by `FLAG_POX_CAUGHT_MEWTWO`). Talking to it offers the Sage-style reward battle (`BattleSetup_StartLegendaryRewardBattle`, Lv.70): any ball catches it, and declining, fleeing or fainting it leaves it there.
7. **Must not:** give RED dialogue beyond his ellipses, explain where MEWTWO came from, or tie the cave to the convergence plot.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Cave guard | `Route24_hns` `(8,11)` `Route24_EventScript_CaveGuard` | hidden by `FLAG_SYS_GAME_CLEAR` | explains the closure | keep |
| Cave door | `Route24_hns` `(8,10)` | warp 0 | to `MtSilver_1F_WaterfallRoom_hns` warp 0 `(43,46)` | keep |
| RED | `MtSilver_SummitDay_hns` `(10,6)` `PoxCeruleanCave_Red` | `TRAINER_PLASTIC_OX_RED`, hidden by `FLAG_POX_RED_RESTING` | silent battle, then trainer card, Hall of Fame, credits; returns after each new League win | keep |
| MEWTWO | `MtSilver_SummitDay_hns` `(11,6)` `PoxCeruleanCave_Mewtwo` | hidden by `FLAG_POX_CAUGHT_MEWTWO` | before RED is beaten: cry, one line, then RED's battle; after: reward battle, any ball catches it | keep |

## Dialogue guidance

- **Voices:** a League officer doing a dull job politely; RED, who says nothing; MEWTWO, described, never quoted.
- **Register:** sparse. The cave should feel like the end of the credits, not a new chapter.

> OFFICER: The POKéMON LEAGUE keeps this cave closed. Come back once your name is in the HALL OF FAME.

> RED: ……………… ……………… (before and after the battle; "…!" when beaten, "…" when he wins)

> MEWTWO's eyes fix on you. It doesn't leave the TRAINER's side.

- **Do not:** have RED speak full sentences, add NPCs who explain the cave, or reuse the officer's line elsewhere.

## Inspiration

- **Mt. Silver in Gold/Silver/HGSS** — the silent summit and a trainer who only answers with a battle; converted here into the post-game finale without new text.
- **Cerulean Cave in Red/Blue** — a post-game cave guarded until the player proves themselves, home of MEWTWO.
- **Conversion:** one guard, one trainer, one Pokémon. Everything else is the climb.

## Implementation hooks

- Import: `plastic_ox/alpha/import_cerulean_cave.py` (tilesets `cave_gray_hns`, `mt_silver_snow_hns`; layouts, maps, encounters, map group `gMapGroup_PlasticOxDungeons`).
- Scripts: `data/maps/MtSilver_SummitDay_hns/scripts.inc`; guard in `data/maps/Route24_hns/scripts.inc`; special `PoxShowPlayerTrainerCard` in `src/plastic_ox.c`.
- Flags: `FLAG_POX_TRAINER_RED` (POX event flag +52; the trainer flag of ID 958), `FLAG_POX_CAUGHT_MEWTWO` (+53), `FLAG_POX_RED_RESTING` (+54), gate `FLAG_SYS_GAME_CLEAR`.
- Test: `plastic_ox/demo/test_cerulean_cave.py`.
- Known gaps: the waterfall room's Snowswept Cavern exit was not imported; tileset animations (waterfall) are static.

## Open questions

- RED's rematch uses the same team and levels. Should rematches scale up?
- RED's levels are 70 (MEWTWO 72) against a post-game cap of 64. Raise or lower?
- Should RED return for a rematch after the credits, as in HGSS?
- Should the cave's item balls be restored (each needs a new persistent flag)?
