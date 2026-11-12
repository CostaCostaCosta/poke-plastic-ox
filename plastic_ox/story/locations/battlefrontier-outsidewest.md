---
title: Battle Frontier Outside West
slug: battlefrontier-outsidewest
kind: Route
act: 6
stage: "Postgame — Battle Frontier"
depth: supporting
wiki: battlefrontier-outsidewest
maps: [BattleFrontier_OutsideWest]
also_maps: [BattleFrontier_ReceptionGate, BattleFrontier_RankingHall]
flags: [FLAG_SYS_GAME_CLEAR, FLAG_POX_TRIGGERS_ENABLED]
items: [ITEM_SS_TICKET]
status: drafted
---

# Battle Frontier Outside West

## Snapshot

The postgame's front square: a paved resort plaza of fountains, scoreboards, and eleven doors, entered only from `PlasticOx_Harbor` at `(25,66)` once `FLAG_SYS_GAME_CLEAR` is set. Nothing here advances the badge spine — the player arrives as Champion and is immediately just another competitor with a lanyard. The emotional note is *holiday crowd*: a place built entirely for people who came to compete, and therefore a place where nobody lives.

## Plot points

1. **Champion-only arrival — reveal-ladder step 18.** `PoxRegion_harbor_frontier_a` at the harbor's `(16,14)` warps here to `(25,66)`; `PoxRegion_harbor_frontier_b` at `(26,66)` goes back. Both check `FLAG_SYS_GAME_CLEAR` (and the build's `FLAG_POX_TRIGGERS_ENABLED`), and both fall back to a "closed" message and a return warp. There is no second entrance.
2. **The square is a wayfinding problem.** Three facility signs (Dome `(15,18)`, Pike `(45,30)`, Factory `(16,43)`), a Mart at `(51,51)`, lounges, Scott's house at `(44,5)`, Artisan Cave at `(39,55)`, and the Reception Gate at `(26,61)`/`(26,65)`. The hub's only narrative job is telling 25 strangers apart and pointing at doors.
3. **The crowd is donor Emerald, unrewritten.** The Dome Ace fan trio at `(12,9)`, `(12,10)`, `(11,10)` argue about being noticed; `LOCALID_FRONTIER_MANIAC_1` and `_2` at `(13,44)`/`(14,44)` share one string verbatim; the man at `(8,5)` explains that the fans were "obliterated by this certain TRAINER at a tournament". All of it assumes a Hoenn celebrity circuit v7 does not have.
4. **The harbor still sails to Hoenn.** The attendant at `(19,68)` checks `ITEM_SS_TICKET` and offers Slateport or Lilycove; that ticket is only granted by the unused Littleroot moving-in script. The `LOCALID_FRONTIER_SS_TIDAL` body at `(20,70)` carries no script.
5. **Reception Gate and Ranking Hall are vanilla briefing rooms.** ReceptionGate's greeter, facility guide, rules guide and Frontier Pass guide (`0,11`, `8,11`, `8,4`, `0,4`) all still teach Emerald's rules; the Ranking Hall attendant at `(24,13)` still calls the records "immortal TRAINERS".

**Must not:** open before the Champion is recorded; let a Frontier NPC explain the convergence or Bill; treat Symbols as badges or as story progression; treat Slateport or Lilycove as reachable destinations without a decision; put a Rocket here; invent a Frontier Brain the rest of v7 does not support.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Harbor gate | `(26,66)` `PoxRegion_harbor_frontier_b` | `FLAG_SYS_GAME_CLEAR` | warps to `MAP_PLASTIC_OX_HARBOR`, `(15,14)`; otherwise "closed" and back to `(25,66)` | keep; the tile should read as a gangway, not a teleport |
| Harbor sign | `(25,67)` `PoxRegion_harbor_frontier_b_Sign` | always | "Harbor / Marked passage ahead." | rewrite as a sailing board: destination, time, whether it runs |
| Reception Gate doors | `(26,61)`, `(26,65)` | always | warp to `BattleFrontier_ReceptionGate` warps 1 and 0 | keep; the pair is a gate, so make one enter and one exit visually |
| Reception greeter | `BattleFrontier_ReceptionGate` `(0,11)` | always | "The front lines of POKéMON battling!" | keep the welcome, cut the slogan |
| Scott | `BattleFrontier_ReceptionGate` `(4,5)` | `FLAG_HIDE_BATTLE_FRONTIER_RECEPTION_GATE_SCOTT` | `0x0` — object exists, interacts with nothing | remove, or give him the Frontier Pass desk |
| Facility guide | `BattleFrontier_ReceptionGate` `(8,11)` | always | lists facilities | keep; he is the only NPC who should enumerate doors |
| Dome Ace fans | `(12,9)`, `(12,10)`, `(11,10)` | always | three-way celebrity quarrel | keep the quarrel, localise the idol or cut the title |
| Maniac brothers | `(13,44)`, `(14,44)` | always | identical "big scary guy said he'd lend us POKéMON" text twice | give one brother the doubt and the other the plan |
| Former trainers | `(8,5)` `LOCALID_FRONTIER_MAN_4` | always | fans were "obliterated by this certain TRAINER" | retarget: a local final they lost, not a vanished circuit |
| Fisherman | `(31,31)` | always | would rather fish; "you can't catch anything here" | keep; it is the only line that admits the plaza is sterile |
| Ferry attendant | `(19,68)` | `ITEM_SS_TICKET` | offers Slateport/Lilycove, warps to `MAP_SLATEPORT_CITY_HARBOR` | decide: rewrite to the v7 islands, or retire the counter |
| Ranking Hall attendant | `BattleFrontier_RankingHall` `(24,13)` | always | "immortal TRAINERS who left great records" | keep; add what the player's own record would look like |

## Dialogue guidance

- **Reception staff speak in catalogues**: facility, queue, rules, pass. Teala-voiced, brisk, faintly bored.
- **Competitors speak in goals and grievances** — a Symbol, a bad draw, a rival who did not show. None of them know or care that the player is Champion.
- **The fan trio** are the square's comic engine: loud, certain, and arguing about nothing. They may keep the celebrity frame only if a decision is made about who the Dome Ace is.
- **The harbor attendant** is the one person with a schedule, and therefore the one person who can say when the postgame ends.
- No one here discusses the mainland's story. This is a resort; the war is over and it never reached the island.

> RECEPTION GUIDE: Tower, Dome, Palace, Arena, Factory, Pike, Pyramid. Seven doors, seven sets of rules, one pass. I can explain any of them, but not all of them twice.

> LASS: I said one Symbol before I go home. That was nine days ago. My ferry is tomorrow.

> FAN: He looked left. Left! Do you understand what that means? Half this plaza was standing to his right.

> HARBOR ATTENDANT: Last sailing is at six. If you miss it, the lounge has chairs and the vending machine has opinions.

> FAT MAN: A girl at the Pike once told me to stop eating. I think about that every time I open a bag of crisps. Crunch.

- **Do not:** reveal anything about Bill or the system; imply the Frontier is why the region converged; let anyone call Symbols badges; write Hoenn place-lore as if the player has been there; make the plaza poor or rustic — it is maintained and staffed.

## Inspiration

- **British seaside piers and Japanese resort arcades**: everything is paid for by people queueing. Converts into ticket windows, a lost-property desk, and staff who close one counter at a time.
- **A multi-day sports convention**: lanyards, brackets taped inside glass, a scoreboard no one has updated since morning. The Reception Gate becomes registration and the Ranking Hall becomes the honours board.
- **Cricket pavilion honours boards**: names in gold by year. The Ranking Hall's whole emotional payload is a list the player is not on yet.
- **Ferry terminals with a last-sailing board**: the attendant's schedule is the postgame's clock and the natural place to ask "when do I leave".
- **Stage-door autograph hunters**: the Dome Ace trio, converted from Emerald's celebrity gag into resort regulars who have made one competitor into their entire social life.

## Implementation hooks

- Wiki page: `battlefrontier-outsidewest.html`.
- Maps: `BattleFrontier_OutsideWest` (`MAP_BATTLE_FRONTIER_OUTSIDE_WEST`), `BattleFrontier_ReceptionGate` (`MAP_BATTLE_FRONTIER_RECEPTION_GATE`), `BattleFrontier_RankingHall` (`MAP_BATTLE_FRONTIER_RANKING_HALL`); 47 `BattleFrontier_*` maps exist behind the square's doors.
- Scripts: `data/maps/BattleFrontier_OutsideWest/scripts.inc`, `data/maps/BattleFrontier_ReceptionGate/scripts.inc`, `data/maps/BattleFrontier_RankingHall/scripts.inc`, `data/scripts/plastic_ox_region.inc` (`PoxRegion_harbor_frontier_a`, `PoxRegion_harbor_frontier_b`).
- Gates: `FLAG_SYS_GAME_CLEAR` from the Hall of Fame's `GameClear`; `FLAG_POX_TRIGGERS_ENABLED` for the relaxed build.
- Items: `ITEM_SS_TICKET` is the ferry's only check and is only granted by `PlayersHouse_1F_EventScript_*` in `data/scripts/players_house.inc`.
- Known gaps: the entire crowd is unrewritten Emerald, including a duplicated Maniac string and a celebrity frame with no v7 owner; the SS Tidal still offers Slateport and Lilycove with an effectively unobtainable ticket; `LOCALID_FRONTIER_RECEPTION_SCOTT` is a scriptless object; the map's only Plastic Ox content is the harbor sign and the two gate triggers; the facilities themselves are full vanilla Emerald with Symbols, and `plastic_ox/alpha/PLAN.md` lists postgame facility content as a separate milestone.

## Open questions

- Keep the Frontier as playable legacy Emerald content (facilities, Symbols, rental stock) or re-theme it as a v7 postgame hub with its own rewards? Nothing in v7 writes new content for it today.
- Does the SS Tidal keep sailing to Slateport/Lilycove? If yes, those harbors need v7 entries; if no, the attendant must be rewritten and `ITEM_SS_TICKET` either made obtainable or the counter retired.
- Who is the Dome Ace in this world? The fan trio only works if there is a named local competitor, and no v7 character is currently cast for it.
- Remove `LOCALID_FRONTIER_RECEPTION_SCOTT`, or move the Frontier Pass desk onto him so the object earns its tile?
- Are the two Maniacs deliberately identical (twins finishing each other's sentences) or an import artefact to fix? Their text is byte-identical.
