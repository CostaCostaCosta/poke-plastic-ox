---
title: Pallet Town
slug: pallet-town
kind: Town
act: 1
stage: "0 — Opening"
depth: full
wiki: pallettown-frlg
maps: [PalletTown_Frlg]
also_maps: [PalletTown_ProfessorOaksLab_Frlg, PalletTown_PlayersHouse_1F_Frlg, PalletTown_PlayersHouse_2F_Frlg, PalletTown_RivalsHouse_Frlg]
flags: [FLAG_POX_STORY_STARTER, FLAG_POX_TRIGGERS_ENABLED, FLAG_POX_LAB_INTRO]
badges: []
status: drafted
---

# Pallet Town

## Snapshot

A small seaside town of low roofs, white fences, and a laboratory that is far too
big for it. The player wakes here, walks to Oak's lab, and chooses between
Treecko, Squirtle, and Cyndaquil. This is the whole tutorial: no convergence
explanation, no Rocket rumor, no Bill. The only strangeness allowed is that
three professors are in one room and none of them can fully explain why.

## Plot points

1. **Oak sends the player to the lab.** Short, warm, ordinary. The player has no
   assignment yet beyond "go see what Oak wants".
2. **Three professors, one table.** Oak (Kanto), Elm (Johto), and Birch (Hoenn)
   are together, each presenting one starter. Elm and Birch are visiting, not
   resident. Nobody monologues about the merged world; the professors are
   excited about a research problem, the way academics are excited about
   grants, not apocalypses.
3. **Starter choice is permanent and quiet.** The player picks Treecko (left
   ball, Birch), Squirtle (center, Oak), or Cyndaquil (right, Elm). The two
   unpicked balls stay visible for the rest of the game.
4. **Pokédex assignment.** Oak asks the player to record what they find, not to
   save the world. This is reveal-ladder step 1: *the world converged*, stated
   once, plainly, and then dropped.
5. **Supplies, then the road.** Five Poké Balls, the Exp. Share handoff from
   Elm, a catching tip from Birch, and Oak's go-ahead. Elm leaves for his lab
   and Birch for the field; Oak stays.
6. **The water edge is a wall.** The southern beach is fenced off with the
   starter gate: without a starter the player is turned back with a plain
   "dangerous to leave without a Pokémon". Pallet's southern water relationship
   to Cinnabar is visible geography, never a route.

**Must not:** name Bill, Team Rocket, Silph, the adaptive system, or "something
is still changing the world". The first hour should read as a normal Pokémon
opening that happens to have three professors in it.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Oaks's lab intro | `PalletTown_ProfessorOaksLab_Frlg`, starter table | `FLAG_POX_LAB_INTRO` unset | Oak/Elm/Birch intro, then choose-partner prompt | keep; tighten each professor's one-line reason for being here |
| Starter: Treecko | lab, left ball | `FLAG_POX_STORY_STARTER` unset | `givemon SPECIES_TREECKO, 5`, hides ball 5 | keep |
| Starter: Squirtle | lab, center ball | same | `givemon SPECIES_SQUIRTLE, 5`, hides ball 6 | keep |
| Starter: Cyndaquil | lab, right ball | same | `givemon SPECIES_CYNDAQUIL, 5`, hides ball 7 | keep |
| Pokédex + supplies | lab, Oak after starter | `FLAG_POX_STORY_STARTER` set, supplies not given | Pokédex text, five balls, Exp. Share, TMs | keep; no new reward here |
| Starter gate | town, beach tiles `y=1` (24 coord events) | `FLAG_POX_STORY_STARTER` unset | warps player back to `(10,4)` with refusal text | keep; make the line feel like a neighbour, not a system message |
| Mom | `PalletTown_PlayersHouse_1F_Frlg` | always | vanilla mom text | rewrite to one domestic line about the professors visiting |
| Sign lady | town `(3,10)` | always | "three professors!" line | keep the pride, cut the exposition |
| Fat man | town `(13,17)` | always | Pokédex explainer | rewrite as a gadget enthusiast, not a manual |

## Dialogue guidance

- **Oak** is busy and kind, speaks in short declaratives, and never explains
  more than he is asked. He is the only person in town who is visibly tired.
- **Elm** is anxious about being a guest; he overpacks, thanks people twice, and
  talks about Cyndaquil like a nervous parent.
- **Birch** is outdoorsy and loud, treats the lab like a greenhouse, and is the
  only one who says "Hoenn" without lowering his voice.
- **Mom** is unimpressed by professors and deeply interested in whether the
  player has eaten.
- **Neighbours** know the lab has visitors and are deciding how to feel about
  it: proud, nosy, mildly inconvenienced by the parking.
- Keep sentences under two lines per textbox. Pallet should sound like a place
  where people have known each other for thirty years.

> SIGN LADY: Three professors in our little town. I keep expecting one of them
> to ask me for directions.

> FAT MAN: A machine that records every Pokémon you meet. I'd lose mine in a
> week.

> MOM: Eat something before you go. The professors can wait; they're used to it.

> BIRCH: Trecko's been restless since we got off the boat. Might be the sea air.

- **Do not:** have any NPC say the words "convergence", "merged region", or
  "Kanto, Johto and Hoenn" in one breath. Do not foreshadow the Champion.

## Inspiration

- **Pallet as a real seaside village:** a Maine or Cornish harbour town in late
  spring — cold water, white paint, one café, everybody knows the ferry
  schedule. The lab is the only building with air conditioning.
- **FireRed/LeafGreen Pallet's rhythm:** a bedroom, a short walk, a lab, one
  choice. The remake's Pallet is quiet because the game trusts silence before
  the first route.
- **Academic-visit comedy:** three specialists in one small lab, competing
  politely over desk space and the one good chair. This is where the humour
  lives — not in jokes about the map.
- **Dialogue conversion:** give each neighbour a *job* related to the visit
  (catering, laundry, the inn, the ferry) so the professors' presence is felt
  through logistics rather than exposition.

## Implementation hooks

- Wiki page: `pallettown-frlg.html`
- Maps: `PalletTown_Frlg` (`MAP_PALLET_TOWN`), `PalletTown_ProfessorOaksLab_Frlg`,
  `PalletTown_PlayersHouse_1F_Frlg`, `PalletTown_PlayersHouse_2F_Frlg`,
  `PalletTown_RivalsHouse_Frlg`
- Scripts: `data/scripts/plastic_ox_pallet.inc` (hand-authored, included by
  `plastic_ox_story.inc`), `data/maps/PalletTown_Frlg/scripts.inc`
- Flags: `FLAG_POX_STORY_STARTER`, `FLAG_POX_LAB_INTRO`, `FLAG_POX_HIDE_TREECKO_BALL`,
  `FLAG_POX_HIDE_SQUIRTLE_BALL`, `FLAG_POX_HIDE_CYNDAQUIL_BALL`
- Gate: 24 `Pox_StarterGate` coord events along `y=1`, warp to `(10,4)`
- Known gaps: `PalletTown_EventScript_ProfOakTeam` hands the player a full ADV OU
  team ("Before you head to LANCE") — debug/leftover content that contradicts
  the opening; the town's southern tree wall is reported as visually cut off
  from Route 21 in `plastic_ox/human_todo_list.txt`.

## Open questions

- Confirm whether the Oak OU-team gift is intentionally kept as a debug hook or
  should be removed from the shipped build.
- Decide whether the third professor's starter should ever be reachable later
  (e.g. a postgame gift) or left permanently on the table.
