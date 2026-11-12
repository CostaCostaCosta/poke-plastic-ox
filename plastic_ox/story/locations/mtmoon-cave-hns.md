---
title: Mt Moon Cave
slug: mtmoon-cave-hns
kind: Cave
act: 1
stage: "2 — Mt. Moon"
depth: full
wiki: mtmoon-cave-hns
maps: [MtMoon_Cave_hns]
also_maps: [MtMoon_B2F_Frlg]
flags: [FLAG_POX_STORY_MTMOON, FLAG_POX_MOON_HIDE_DOME_FOSSIL]
trainers: [TRAINER_PLASTIC_OX_MOON_SUPER_NERD_MIGUEL, TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT, TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT_2, TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT_3, TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT_4]
items: [ITEM_ANCIENT_ICE_TABLET, ITEM_ANCIENT_ROCK_TABLET, ITEM_MOON_STONE, ITEM_ETHER, ITEM_STAR_PIECE, ITEM_REVIVE, ITEM_ANTIDOTE]
status: drafted
---

# Mt Moon Cave

## Snapshot

The player crosses Mt. Moon between Rustboro and Route 33: wet ladders, a stalled
hoist, Zubat in the roof, and a field scientist arguing with four looters over two
stone tablets. The playable dungeon is the imported chain `MtMoon_1F_Frlg` →
`MtMoon_B1F_Frlg` → `MtMoon_B2F_Frlg`; this note's own map, `MtMoon_Cave_hns`, is
a retired HNS shell kept only to catch saves made in the old cave. This is Rocket
I of exactly three appearances — theft, not conspiracy. Leave the player cramped
and slightly reverent: the mountain is older than the argument inside it.

## Plot points

1. **The mouth.** `Route44_hns` `(68,13)` fires `PoxMoon_EnterFromRoute44` and
   warps to `MtMoon_1F_Frlg` `(18,37)`. No badge check, no Rocket sighting.
2. **The descent.** 1F and B1F are corridors of ladders, ledges, and dead side
   rooms; let the player get lost once. The 12–14 wild table is the cave teaching
   its own type mix.
3. **Miguel at the tablets.** Trigger `(14,11)` runs
   `MtMoon_B2F_EventScript_MiguelTrigger`: Miguel walks in, battles
   (`TRAINER_PLASTIC_OX_MOON_SUPER_NERD_MIGUEL`, Lv.15 Magnemite/Spoink/Baltoy),
   and sets `FLAG_POX_STORY_MTMOON`. His demand is domestic: *we each take one,
   no being greedy*.
4. **Two tablets, one each.** Taking the ICE TABLET `(13,7)` or the ROCK TABLET
   `(14,7)` grants `ITEM_ANCIENT_ICE_TABLET` / `ITEM_ANCIENT_ROCK_TABLET`, removes
   both balls, moves Miguel onto the other pedestal, and sets the flag.
   Re-talking at `VAR_POX_MTMOON_STATE` 2 gives the seal line: ICE to REGICE, ROCK
   to REGIROCK.
5. **Rocket I.** Four grunts — `(12,20)`, `(18,27)`, `(35,12)`, `(37,21)` — are
   prying relics off the walls to sell. Competent, tired, and entirely
   uninterested in what the tablets mean: theft plus one wrong conclusion.
6. **Step 3 is missing.** The beat needs Rocket equipment receiving a signal that
   is not theirs. Proposed, new flag required: one scanner in the camp that hisses
   when examined, and a grunt who insists *it isn't ours*. No explanation, no
   name, no second read.
7. **Out.** `MtMoon_B1F_Frlg` warp 7 lands on `Route33_hns` `(27,17)`; no gate on
   the way out (see `route33-hns.md`).

**Must not:** name Silph, Bill, the adaptive system, or "convergence"; explain the
signal or name its sender; give the grunts a boss, plan, or speech; turn the
tablets into fossil revival (they are seal keys, not specimens); claim the seals
relate to the region's geography.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Legacy entry | `MtMoon_Cave_hns`, any tile | map load | on-frame table → `PoxMoon_LegacyTable` → warps to `MtMoon_1F_Frlg` `(18,36)` | keep as a save stub; it is all this map does |
| Miguel ambush | `MtMoon_B2F_Frlg` `(14,11)` | `VAR_POX_MTMOON_STATE` 0 | trigger → battle → "we each take a tablet" | keep; note the tablets predate the mine |
| Miguel talk | `(13,11)` `LOCALID_MIGUEL` | state 0 / 1 / 2 | battle if undefeated; "pick one"; at 2 the REGI explanation | seals only once he holds his own tablet |
| Ice tablet | `(13,7)` `LOCALID_DOME_FOSSIL` | state 1 | yes/no → `ITEM_ANCIENT_ICE_TABLET`, hides both balls, sets the flag | keep; prompt as reaching, not a menu |
| Rock tablet | `(14,7)` `LOCALID_HELIX_FOSSIL` | state 1 | yes/no → `ITEM_ANCIENT_ROCK_TABLET`, same | keep |
| Grunt 4 | `(37,21)` | undefeated | `TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT_4`; "POKéMON lived here long before people came" | the one who is awed; he seeds the receiver beat |
| Grunt 1 | `(12,20)` | undefeated | six Lv.16 mons, hardest fight; vanilla threats | keep the fight; threat about work, not a slogan |
| Grunt 2 | `(18,27)` | undefeated | Magnemite/Drowzee/Gastly; "my associates won't stand for this" | let him mention the receiver without understanding it |
| Receiver (proposed) | camp near `(35,12)` | new flag required, one-shot | nothing exists | static burst and a denial; no battle, no gift |
| Items | `(20,16)` `ITEM_MOON_STONE`, `(39,11)` `ITEM_ETHER`, balls at `(30,26)`–`(3,11)` | hidden / always | the `(35,5)` ball grants a second `ITEM_STAR_PIECE` | make `(35,5)` a real TM or rename its script |

## Dialogue guidance

- **Miguel** is a field scientist with a numbering system and no funding: labels,
  crates, who has the better trowel. A colleague who arrived first, not a rival.
- **The grunts** are four people on a night shift — awed, angry, thinking about
  resale, complaining about dust. None says "Rocket" twice in a scene, and the
  cave has no narrator: scale is carried by the pedestals and by every grunt line
  mentioning the rock. Voices stay down; only Grunt 1 raises his.

> MIGUEL: I labelled both pedestals before you arrived. That is what field work
> is — arriving early and writing things down.

> GRUNT 4: You feel that? The ceiling is older than the town you came from. I'm
> not supposed to think about it. I'm supposed to carry it out.

> GRUNT 2: Our scanner keeps spitting out a burst that isn't ours. The boss says
> interference. Interference doesn't know our call sign.

> GRUNT 1: Blacklist you? Kid, I can't even get a transfer out of this cave.

- **Do not:** explain the signal; say "convergence", "network", "Silph", or
  "adaptive"; make Miguel a Rocket plant; let the tablets talk about cloning.

## Inspiration

- **Real caving:** carbide-smelling air, surveyor's tape on rock, a chalk arrow at
  a junction, the temperature drop three steps in. Item placement and Miguel's
  labelling habit come from here.
- **Museum collection splits:** two institutions dividing a find, accession
  numbers, foam cradles, a crate marked fragile — the one-tablet-each rule.
- **Gen I Mt. Moon:** cramped ladder rooms and the sense of a maze with a prize.
  Keep the maze, cut the expository NPCs.
- **Night-shift labour and awe:** a crew that wants to finish before dawn, paid by
  the crate, plus one worker who cannot stop touching the rock. That worker is
  Grunt 4, the only person allowed near step 3.

## Implementation hooks

- Wiki page: `mtmoon-cave-hns.html`
- Maps: `MtMoon_Cave_hns` (`MAP_MT_MOON_CAVE_HNS`), `MtMoon_B2F_Frlg`
  (`MAP_MT_MOON_B2F`); approach floors `MtMoon_1F_Frlg`, `MtMoon_B1F_Frlg`
- Scripts: `data/maps/MtMoon_B2F_Frlg/scripts.inc`,
  `data/maps/MtMoon_Cave_hns/scripts.inc`, `data/scripts/plastic_ox_story.inc`,
  `plastic_ox/alpha/mt_moon.py`
- Flags: `FLAG_POX_STORY_MTMOON`, `FLAG_POX_MOON_HIDE_DOME_FOSSIL`; **new flag
  required** for the one-shot receiver read
- Trainers: `TRAINER_PLASTIC_OX_MOON_SUPER_NERD_MIGUEL`,
  `TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT` through `_GRUNT_4`; items above
- Known gaps: `MtMoon_Cave_hns` has **0 warps, 0 objects, 0 coord events** yet
  keeps three 12–14 wild tables, so nobody can enter it. The alpha Town Map beat
  (`Pox_MoonGrunt1`, `Pox_MoonGrunt2`, `Pox_MoonRocketMap`,
  `TRAINER_PLASTIC_OX_MOONGRUNT1/2`, `FLAG_POX_HIDE_MTMOON_GRUNT_1/2`) exists in
  `plastic_ox_story.inc` but **no map object calls it**; the live B2F uses the
  tablet version. Grunt 1 and Grunt 2 share an intro string, and all four speak
  vanilla FireRed lines.

## Open questions

- Keep `MtMoon_Cave_hns` as a save stub, or delete it and accept that old saves
  land nowhere? It costs a map slot, three wild tables, and a misleading page.
- Put the receiver on the live B2F, or finish the unused alpha Town Map beat? The
  two versions of Rocket I cannot both ship.
- Is the tablet choice exclusive per save, or may a reload yield both?
- Should `Route44_hns` → `MtMoon_1F_Frlg` require badge 1, or is the mountain
  walkable before Roxanne with Whitney's flag check as the only backstop?
- Do the REGI seal lines belong here, or in the Cinnabar archives?
