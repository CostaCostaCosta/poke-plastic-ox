---
title: Ecruteak City
slug: ecruteakcity-hns
kind: City
act: 2
stage: "4 — Ecruteak and the Burned Tower"
depth: full
wiki: ecruteakcity-hns
maps: [EcruteakCity_hns]
also_maps: [PlasticOx_MortyGym, PlasticOx_DanceTheater, EcruteakCity_Theater_hns, EcruteakCity_Gym_hns, EcruteakCity_SageOffice1_hns, EcruteakCity_SageOffice2_hns]
flags: [FLAG_POX_STORY_BURNED_TOWER, FLAG_POX_KIMONO_VAPOREON, FLAG_POX_KIMONO_JOLTEON, FLAG_POX_KIMONO_FLAREON, FLAG_POX_KIMONO_ESPEON, FLAG_POX_KIMONO_UMBREON, FLAG_POX_GIFT_KIMONO]
badges: [3]
trainers: [TRAINER_PLASTIC_OX_MORTY, TRAINER_PLASTIC_OX_KIMONOVAPOREON, TRAINER_PLASTIC_OX_KIMONOJOLTEON, TRAINER_PLASTIC_OX_KIMONOFLAREON, TRAINER_PLASTIC_OX_KIMONOESPEON, TRAINER_PLASTIC_OX_KIMONOUMBREON]
status: drafted
---

# Ecruteak City

## Snapshot

Dark timber houses at the foot of a burnt tower, entered from `Route37_hns` in the south. The player is steered through the Dance Theater, down under the tower, and back up to `PlasticOx_MortyGym` for badge 3, while the western gatehouse stays visibly shut. Ecruteak is where the region stops being damaged geography and becomes damaged *history*: the town is custodial rather than haunted, and it is tired.

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
| Tower lead | town `(19,22)` `Pox_BurnedGuide` | before `FLAG_POX_STORY_BURNED_TOWER` | "MORTY went below the BURNED TOWER" | keep, and give her a job: she trims the tower lamps and has not slept well |
| Tower aphorism | town `(36,41)` `EcruteakCity_EventScript_Npc2` | always | "The BURNED TOWER remembers the fire. The fire remembers nothing." | keep as the town's one good line; give it to the bell-founder |
| Three identical bodies | town `(22,42)`, `(53,32)`, `(55,42)`, all `EcruteakCity_EventScript_Npc3` | always | the same "still stands / keep its history alive" text three times | three distinct people: fire watch, carpenter, market stall |
| League gate lore | town `(19,15)` `EcruteakCity_EventScript_Npc5` | always | "The west gate leads toward the LEAGUE. The guard checks BADGES there." | keep; add that the guard has never had to refuse twice politely |
| Old houses | town `(52,49)` `EcruteakCity_EventScript_Npc6` | always | "Our old wooden houses have heard generations of POKéMON stories." | rewrite as joinery, smoke, rooflines — a boy who knows every loose board |
| Silver cameo | town `(41,41)` `LOCALID_ECRUTEK_SILVER` | always | a dusk-shadow line on an `OBJ_EVENT_GFX_SILVER_HNS` body | recast or retire; v7 has no Ecruteak rival beat |
| West gate | town `(8,34)`–`(8,37)` `PoxEcruteak_WestEntrance` | eight badges | warps into the gatehouse; `PoxLeague_Checkpoint` sends you to `MAP_PLASTIC_OX_VICTORY_ROAD` | keep; make the refusal read as a schedule, not a mystery |
| Kimono troupe | `PlasticOx_DanceTheater` `(3,9)`,`(5,2)`,`(7,8)`,`(3,12)`,`(7,14)` | badge 2 held | five trainers, one shared intro string | five dancers, each naming a different part of the rite |
| Eevee gift | `PlasticOx_DanceTheater` `(5,15)` `Pox_Kimono` | all five Kimono flags | gives EEVEE, Lv.5 | keep; frame it as fostering a dance partner, not a trophy |
| Gym entry | town `(20,48)` → `EcruteakCity_Gym_hns` | always | opens the **legacy** HNS gym (107 warps, its own `Pox_Morty` at `(4,4)`) | should reach `PlasticOx_MortyGym`; `Pox_MortyGuide` exists but no object carries it |
| Sages' office | town `(39,22)` → `EcruteakCity_SageOffice1_hns` | before / after the tower | three old men, two sharing one line | before: the sages are out; after: one desk is packed up |

## Dialogue guidance

- **The town speaks in maintenance, not mystery.** Sentence one touches the tower; sentence two is about a ladder, a lamp, a delivery, or a roof.
- **Morty** is a working priest: short, declarative, no adjectives about ghosts. He says what he saw, gives the order, and leaves. He never theorises.
- **The Kimono troupe** are professionals mid-season — feet, bells, and who dances which figure. The fire is context, not content.
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
- Scripts: `data/maps/EcruteakCity_hns/scripts.inc`; `data/scripts/plastic_ox_story.inc` (`Pox_BurnedTower`, `Pox_Kimono`, `Pox_Kimono*`, `Pox_Morty`, `Pox_MortyGuide`, `Pox_DanceGuide`); `data/scripts/plastic_ox_region.inc`; `data/scripts/plastic_ox_league.inc`.
- Gates: `Pox_BurnedTower` needs badge 2 and sets `FLAG_POX_STORY_BURNED_TOWER`; `PoxLeague_Checkpoint` needs all eight badges.
- Known gaps: both town doors open **legacy HNS interiors** (`EcruteakCity_Gym_hns` with 107 warps and a second `Pox_Morty`; `EcruteakCity_Theater_hns` with ten NPCs sharing four lines). The real `PlasticOx_MortyGym` and `PlasticOx_DanceTheater` have **0 warps** and are reachable only via `Pox_MortyGuide` / `Pox_DanceGuide`, which no object carries. All five Kimono trainers share one intro string. `EcruteakCity_SageOffice2_hns` is empty. `LOCALID_ECRUTEK_SILVER` is a typo'd local id, and `Route38_hns`'s warp targets a gatehouse warp index that does not exist.

## Open questions

- Retire `EcruteakCity_Gym_hns`, or keep its layout as the Gym 3 maze and move `Pox_Morty` into it? Today badge 3 can be won twice.
- Should the theater door warp straight into `PlasticOx_DanceTheater`, or is a placed guide object the intended flow? That decides whether `EcruteakCity_Theater_hns` survives as a lobby.
- Is `LOCALID_ECRUTEK_SILVER` a deliberate rival cameo needing an arc, or a donor sprite left standing in the street?
- The League checkpoint sits in the Route 38 gatehouse whose west warp is dangling. Does the gatehouse stay the checkpoint, or does Ecruteak west need its own map and Route 38 a real connection?
