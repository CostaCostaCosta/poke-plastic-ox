---
title: Ecruteak City
slug: ecruteakcity-hns
kind: City
act: 2
stage: "4 — Ecruteak and the Burned Tower"
depth: full
wiki: ecruteakcity-hns
maps: [EcruteakCity_hns]
also_maps: [PlasticOx_MortyGym, PlasticOx_DanceTheater, EcruteakCity_Theater_hns, EcruteakCity_Gym_hns, EcruteakCity_SageOffice1_hns, EcruteakCity_SageOffice2_hns, EcruteakCity_House1_hns, EcruteakCity_House2_hns, EcruteakCity_Mart_hns, EcruteakCity_PokemonCenter_hns, Gate_EcruteakCity_Route42_hns]
flags: [FLAG_POX_STORY_BURNED_TOWER, FLAG_POX_KIMONO_VAPOREON, FLAG_POX_KIMONO_JOLTEON, FLAG_POX_KIMONO_FLAREON, FLAG_POX_KIMONO_ESPEON, FLAG_POX_KIMONO_UMBREON, FLAG_POX_GIFT_KIMONO]
badges: [3]
trainers: [TRAINER_PLASTIC_OX_MORTY, TRAINER_PLASTIC_OX_ECRUTEAK_KADO, TRAINER_PLASTIC_OX_ECRUTEAK_YUI, TRAINER_PLASTIC_OX_ECRUTEAK_GENZO, TRAINER_PLASTIC_OX_ECRUTEAK_RIN, TRAINER_PLASTIC_OX_KIMONOVAPOREON, TRAINER_PLASTIC_OX_KIMONOJOLTEON, TRAINER_PLASTIC_OX_KIMONOFLAREON, TRAINER_PLASTIC_OX_KIMONOESPEON, TRAINER_PLASTIC_OX_KIMONOUMBREON]
status: implemented
---

# Ecruteak City

## Snapshot

Dark timber houses at the foot of a burnt tower, entered from `Route37_hns` in the south. The player is steered through the Dance Theater, down under the tower, and back up to the spooky `EcruteakCity_Gym_hns` shadow maze for badge 3, while the western gatehouse stays visibly shut. The east gatehouse is a real through-passage to `Route119`, not a decorative dead door: the door watch stands aside once Morty signs the badge. The gym is staffed by four working attendants with NU teams of two or three, then Morty. Ecruteak is where the region stops being damaged geography and becomes damaged *history*: the town is custodial rather than haunted, and it is tired.

## Plot points

1. **Arrival from the south.** No cutscene. The tower's charred top is on the skyline before anyone names it, and locals discuss the fire the way people discuss a flood — by year, by street, by what was lost.
2. **Dance Theater lead.** The troupe performs the tower's rite and points at Morty, who went below after the last observance. Five optional Kimono battles each set their own `FLAG_POX_KIMONO_VAPOREON`-style completion flag; beating all five unlocks one EEVEE (`FLAG_POX_GIFT_KIMONO`) — Eevee #3, character texture, not a clue.
3. **Burned Tower anomaly — reveal-ladder step 5.** In `PlasticOx_BurnedTowerB1F` at `(8,9)` `Pox_BurnedTower` restores one wall and its stair for a heartbeat, then returns ash and a fallen ceremonial bell. Morty's reading stays spiritual: "Places remember what they were."
4. **The sages' mission.** Morty sends the two assembled sages out to find legendary Pokémon displaced by the convergence, shelter them, and stay until they feel safe. Every later sage-beside-a-legendary scene descends from this order. They depart; a caretaker stays.
5. **Morty returns to the Gym.** `FLAG_POX_STORY_BURNED_TOWER` sets, Morty is removed from the tower, and badge 3 (`TRAINER_PLASTIC_OX_MORTY`, NU) becomes the objective. Eastward, `Route119` is the canonical next leg.
6. **West gate stays shut.** `(8,34)`–`(8,37)` `PoxEcruteak_WestEntrance` reaches the gatehouse and `PoxLeague_Checkpoint`, which demands all eight badges; it reopens only in the League return (ladder step 16). Do not spend it here.

**Must not:** release Raikou, Entei, or Suicune; let Morty explain a mechanism; name Bill, Silph, or the Weather Institute; put an exposition NPC at the tower door; open the west gate early.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Tower lead | town `(19,22)` `Pox_BurnedGuide` | `FLAG_POX_STORY_BURNED_TOWER` | "MORTY went below the BURNED TOWER" | lamp-trimmer: before, the ninth-hour lamps and the way down past the last lamp; after, "he came up before dawn and did not say what he found" |
| Tower aphorism | town `(36,41)` `EcruteakCity_EventScript_Npc2` | always | "The BURNED TOWER remembers the fire. The fire remembers nothing." | kept as the town's one good line, spoken by the bell-founder who can hear a seam in a cast bell |
| Three identical bodies | town `(22,42)` `EcruteakCity_EventScript_MarketStall`, `(53,32)` `EcruteakCity_EventScript_FireWatch`, `(54,42)` `EcruteakCity_EventScript_GateWatch` | GateWatch hidden by `FLAG_BADGE03_GET` | the same "still stands / keep its history alive" text three times | market stall (roast chestnuts), fire watch (rota, siren, water barrels), east-door schedule |
| League gate lore | town `(19,15)` `EcruteakCity_EventScript_Npc5` | always | "The west gate leads toward the LEAGUE. The guard checks BADGES there." | keep, plus the guard who has never had to refuse twice politely |
| Old houses | town `(52,49)` `EcruteakCity_EventScript_Npc6` | always | "Our old wooden houses have heard generations of POKéMON stories." | the carpenter's boy: spring measurements, the tower's old footprint, every loose board in the street |
| Silver cameo | town `(41,41)` `EcruteakCity_EventScript_Npc7` | always | a dusk-shadow line on an `OBJ_EVENT_GFX_SILVER_HNS` body | recast as an old woman and her washing line; the Silver sprite is gone, v7 has no Ecruteak rival beat |
| West gate | town `(8,34)`–`(8,37)` `PoxEcruteak_WestEntrance` | eight badges | warps into the gatehouse; `PoxLeague_Checkpoint` sends you to `MAP_PLASTIC_OX_VICTORY_ROAD` | keep; the refusal reads as a schedule ("the list is on the wall if you want to count them") |
| Gym staff | gym `(13,33)` `Pox_GymKado`, `(13,25)` `Pox_GymYui`, `(7,25)` `Pox_GymGenzo`, `(5,14)` `Pox_GymRin` | always; talk to battle | five flavour NPCs, no parties | four trainers with NU teams of two or three, Lv24–27: wicks, chalk, brazier, last door |
| Gym guide | gym `(12,44)` `PoxEcruteak_EcruteakCity_Gym_hns_0` | always | donor "shadows move on their own" line | explains the maze, names the four attendants, points at the top of the stairs |
| Gym plaques | gym `(7,44)`, `(13,44)` | always | two identical leader plaques | a rules plaque ("the floor is not always floor") and a leader-lineage plaque |
| Kimono troupe | `PlasticOx_DanceTheater` stage `(5,3)`,`(7,2)`,`(10,3)`,`(13,2)`,`(15,3)` | badge 2 held | all five trainers on the stage, with distinct teams and intro lines | keep; each dancer names a different part of the rite, and the moon step now ends facing the tower |
| Eevee gift | `PlasticOx_DanceTheater` `(5,15)` `Pox_Kimono` | all five Kimono flags | gives EEVEE, Lv.5 | keep; framed as fostering a dance partner, not a trophy |
| Gym entry | town `(20,48)` → `EcruteakCity_Gym_hns` | always | the HNS shadow maze (107 warps, `Pox_Morty` at `(4,4)`); badge 3 is won here | keep; `PlasticOx_MortyGym` is retired |
| East gate | town `(55,42)` west face / `(62,42)` east face ↔ `Gate_EcruteakCity_Route42_hns` ↔ `Route119` `(5,124)` | both faces after badge 3; the `(54,42)` door watch is hidden by `FLAG_BADGE03_GET` | both arrow-warp doors had no warp events, so the east strip was a softlock | both doors wired; the watch keeps the door until the badge, then steps out of the object list; `(64,41)` `PoxEcruteak_EastWatch` warns about the wet decks |
| Dance Theater entry | town `(39,40)` → `PlasticOx_DanceTheater` `(10,17)` | always | v7 room on `LAYOUT_ECRUTEAK_CITY_THEATER_HNS` | keep; the hall must never reuse a Gym tileset |
| Sages' office | town `(39,22)` → `EcruteakCity_SageOffice1_hns` | before / after the tower | three old men, two sharing one line | three distinct sages with before/after text; `EcruteakCity_SageOffice2_hns` gains a caretaker and five distinct statue inscriptions |
| Legacy theater | `EcruteakCity_Theater_hns` | unreachable | ten NPCs sharing four lines, two identical signs | ten unique rehearsal lines and two distinct signs, kept for any future lobby use |
| Neighbours' houses | `EcruteakCity_House1_hns` `(3,4)`,`(7,4)`; `EcruteakCity_House2_hns` `(5,4)` + two shelves | always | House 1 was empty; House 2 had two identical book texts | the almanac grandfather and the shutter-mender; a granddaughter's history books with two distinct shelf passages |
| Mart | `EcruteakCity_Mart_hns` `(7,5)`,`(5,2)` | always | both clerks shared "train GHOST types" | rope-and-lamp-oil trade, and a delivery driver who says the road moved |
| Pokémon Center | `EcruteakCity_PokemonCenter_hns` `(8,2)`,`(14,6)`,`(11,5)`,`(2,5)` | always | one bell-ghost line, rest generic | heater sitters, the ninth-hour bell rung by hand, sage-family visitors, a genealogy book |

## Dialogue guidance

- **The town speaks in maintenance, not mystery.** Sentence one touches the tower; sentence two is about a ladder, a lamp, a delivery, or a roof.
- **Morty** is a working priest: short, declarative, no adjectives about ghosts. He says what he saw, gives the order, and leaves. He never theorises.
- **The Kimono troupe** are professionals mid-season — feet, bells, and who dances which figure. The fire is context, not content.
- **The gym staff** are maintenance, not mystery: wicks, chalk, a coal brazier, the last door. They use the gym's NU ceiling and never explain the shadow maze as a ghost trick.
- **The sages** are old, polite, and frightened of getting the assignment wrong; they ask practical questions (how much food, how long, what if it refuses).
- After `FLAG_POX_STORY_BURNED_TOWER` the relief is quiet, tower talk stops, and nobody asks the player what they saw.

> BELL-FOUNDER: You can't cast the same bell twice. The second one always has a seam in the ring, and the whole street can hear it.

> FIRE WATCH: Ninth hour I walk the tower, then the roof lines, then the bridge. Forty years of that and nothing has ever burned.

> KIMONO DANCER: The last figure turns toward a wall that isn't there any more. We still turn. The music doesn't care.

> SAGE: They said to stay until it feels safe. Nobody said how we would know.

> CARPENTER: My ledger has the old footprint of that tower in it. Somebody measured it every spring. Nobody has asked me for it since the fire.

- **Do not:** say "convergence" in dialogue; explain the restoration; turn the tower into a ghost-house; hint that the west road matters.

## Inspiration

- **Ise Jingu's twenty-year rebuilding.** Shrine carpenters keep the old measurements in ledgers and rebuild on schedule — hence the carpenter above, a spring measurement day, and a town that finds the anomaly *familiar* rather than impossible.
- **Kinkaku-ji, burned 1950 and rebuilt.** The quarrel in the street is not "was it magic" but "do we rebuild the stair or leave the gap". Give each side a voice: an alderman and the caretaker.
- **The opening of the *Tale of the Heike*.** The bell of impermanence. A working foundry is why the fallen ceremonial bell can be identified by its ring, and why it is worth carrying out of the ash.
- **Japanese fire lookouts and neighbourhood fire drills.** The two policemen become a rota, a hand-cranked siren, and a water barrel on every corner — the least mystical possible response to a burnt tower.
- **Late-autumn temple towns.** First frost, roasted chestnuts, buckwheat noodles, charcoal braziers in shopfronts. Three vendors with those details give the town a season without one line of lore.

## Implementation hooks

- Wiki page: `ecruteakcity-hns.html`; maps listed in `also_maps` above (`PlasticOx_MortyGym`, `PlasticOx_DanceTheater`, `EcruteakCity_Theater_hns`, `EcruteakCity_Gym_hns`, `EcruteakCity_SageOffice1_hns`, `EcruteakCity_SageOffice2_hns`, `Gate_EcruteakCity_Route38_hns`).
- Scripts: `data/maps/EcruteakCity_hns/scripts.inc`; `data/maps/EcruteakCity_Gym_hns/scripts.inc` (mirrored at `plastic_ox/alpha/ecruteak/EcruteakCity_Gym_hns.inc`); `data/scripts/plastic_ox_story.inc` (`Pox_BurnedTower`, `Pox_Kimono`, `Pox_Kimono*`, `Pox_Morty`, `Pox_MortyGuide`, `Pox_DanceGuide`); `data/scripts/plastic_ox_region.inc`; `data/scripts/plastic_ox_league.inc`.
- Gym staff parties: `TRAINER_PLASTIC_OX_ECRUTEAK_KADO/YUI/GENZO/RIN` in `src/data/trainers.party`; victory flags `FLAG_POX_TRAINER_ECRUTEAK_KADO`, `FLAG_POX_TRAINER_ECRUTEAK_YUI`, `FLAG_POX_TRAINER_ECRUTEAK_GENZO` and `FLAG_POX_TRAINER_ECRUTEAK_RIN` at `POX_EVENT_FLAGS_START + 36..39` (`include/constants/flags.h` mapping).
- Demo checks: `plastic_ox/demo/test_ecruteak_gym_gate.py` (gym door, east gate both ways, badge gate) and `plastic_ox/demo/test_ecruteak_gym_trainers.py` (each staff NPC starts its own battle with 2–3 party members).
- Interiors: the house, mart and Pokémon Center scripts live in `data/maps/<Map>/scripts.inc` and mirror `plastic_ox/alpha/ecruteak/<Map>.inc`; `EcruteakCity_House1_hns` finally carries the two NPCs its scripts always described.
- Gates: `Pox_BurnedTower` needs badge 2 and sets `FLAG_POX_STORY_BURNED_TOWER`; `PoxLeague_Checkpoint` needs all eight badges.
- Interiors: `PlasticOx_DanceTheater` uses `LAYOUT_ECRUTEAK_CITY_THEATER_HNS` (21×19, `gTileset_Johto_Building_Hns` + `gTileset_EcruteakTheater_Hns`), entered at `(10,17)` from the town door at `(39,40)`. `EcruteakCity_Gym_hns` is the badge-3 shadow maze; the bright `PlasticOx_MortyGym` room is retired. The legacy `EcruteakCity_Theater_hns` map is retained but unreachable.
- Known gaps: the `LOCALID_ECRUTEK_SILVER` local id still carries its typo even though the body is now an old woman. `Route38_hns`'s warp targets a gatehouse warp index that does not exist. `PlasticOx_MortyGym` and `EcruteakCity_Theater_hns` stay in the ROM but are unreachable by design.

## Open questions

- Resolved: `EcruteakCity_Gym_hns` is the Gym 3 shadow maze and carries `Pox_Morty`; `PlasticOx_MortyGym` is retired. The east gatehouse is wired as a two-way passage.
- Resolved: `LOCALID_ECRUTEK_SILVER` was a donor Silver sprite, not a rival beat. The body is now an old woman at her washing line.
- Resolved for this pass: the League checkpoint stays in the Route 38 gatehouse. Its dangling west warp is recorded as a known gap, not fixed here.
