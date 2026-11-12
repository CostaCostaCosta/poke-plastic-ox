---
title: Cherrygrove City
slug: cherrygrovecity-hns
kind: City
act: 1
stage: "0 — Opening network"
depth: full
wiki: cherrygrovecity-hns
maps: [CherrygroveCity_hns]
also_maps: [CherrygroveCity_SoutheastHouse_hns]
flags: [FLAG_POX_STORY_STARTER, FLAG_POX_STORY_CHERRYGROVE, FLAG_POX_TRIGGERS_ENABLED]
items: [ITEM_NUGGET, ITEM_GOOD_ROD]
status: drafted
---

# Cherrygrove City

## Snapshot

Five doors, a beach, a service row and a guide who has outlived his own directions. The player arrives off `Route29_hns` on the east edge, picks up running shoes at `(57,8)` from the old guide, and leaves north on `Route2_Frlg` toward Ilex and Gym 1. It awards no badge and gates nothing; its job is to be the first place where the merged map is an ordinary inconvenience rather than a mystery. Emotional note: salt air, flattened cardboard outside the mart, a town quietly pleased to be busier.

## Plot points

1. **The shoes.** `(57,8)`, `Pox_Cherrygrove`: refuses until `FLAG_POX_STORY_STARTER`; then prints the guide's errand list, sets `FLAG_SYS_B_DASH`, and burns `FLAG_POX_STORY_CHERRYGROVE`. Nothing else on the map changes state; `FLAG_POX_TRIGGERS_ENABLED` gates the whole script and is set on new game, so the guide runs in normal play and goes silent in trigger-disabled test builds. This is the opening network's one mechanical gift and its only scripted moment.
2. **Two exits, one omission.** East returns to `Route29_hns`; north connects to `Route2_Frlg`, which reuses the HNS route layout and climbs to the Ilex gatehouses. The roads leave in directions that do not match the map the player thinks they are on; the guide's "A KANTO road on a JOHTO coast" is as close as anyone comes to saying so. Reveal-ladder **step 1** only.
3. **The shore is the town's proof.** The fisherman in `CherrygroveCity_SoutheastHouse_hns` at `(3,5)` hands over `ITEM_GOOD_ROD` once (`FLAG_RECEIVED_GOOD_ROD`) and says the tide brings Corsola. The fishing table backs him up and overreaches: Lv4–6 Dewgong, Seadra and Octillery are catchable in the opening network.
4. **Two anonymous doors.** `(42,14)` and `(50,17)` open into `House_GenericA_hns` and `House_GenericB_hns`. Their tenants are in the right register — the old man who decided not to ask questions — except B's boy, who says "merged region" and states the premise the bible keeps unspoken.
5. **The service row.** Mart `(41,7)` and Center `(47,7)` are the shared Johto interiors: the same nurse and clerk who serve `BlackthornCity_hns`. The player's first impression of civilisation is a set that will not change for eight badges.
6. **Beachcombing.** Hidden nuggets at `(55,3)` (`FLAG_POX_HIDDEN_CHERRYGROVE_NUGGET_1`) and `(26,12)` (`FLAG_POX_HIDDEN_CHERRYGROVE_NUGGET_2`), and a sign at `(51,12)` calling the town "The Town of Fiery, Now-Confusing Sunsets".

**Must not:** name Bill, Silph, Rocket, Saffron or the adaptive system; let anyone say "convergence", "merged" or "two regions" as an explanation; turn the guide into a professor; promise a ferry, a Gym or a rival; explain why the north road exists.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Guide (shoes) | `CherrygroveCity_hns` `(57,8)`, `Pox_Cherrygrove` | `FLAG_POX_STORY_STARTER`; one-shot `FLAG_POX_STORY_CHERRYGROVE` | generated four-part "GUIDE:" errand text; sets `FLAG_SYS_B_DASH` | keep the gift and flags; cut the speech to voice plus one direction |
| Dead guide script | no object | `CherrygroveCity_EventScript_GuideGent` | unreachable, and better written than the live guide ("ask me anything — except what region this is") | fold its voice into the live guide, then delete the label |
| Boy | `(48,12)`, `CherrygroveCity_EventScript_Boy` | always | north road "goes UPHILL into mountains that weren't there"; "gonna bike it one day" | keep; give him a delivery route and a bike he is too short for |
| Lass | `(39,11)`, `CherrygroveCity_EventScript_Lass` | always | smallest town you could sail to; crossroads; both regions' roads end at the beach | keep one concrete detail (the ticket window), drop the geography summary |
| Sign | `(51,12)`, `CherrygroveCity_EventScript_Sign` | always | "CHERRYGROVE CITY - The Town of Fiery, Now-Confusing Sunsets" | choose one epithet; local pride, no wink |
| Fisherman | SE house `(3,5)`, `CherrygroveCity_EventScript_Fisherman` | `FLAG_RECEIVED_GOOD_ROD`; `ITEM_GOOD_ROD`; bag-full retry | Corsola in Johto water; rod gift; retry line | keep; he is the only person allowed to name the change plainly |
| Houses A and B | `(50,17)`, `(42,14)` | warps 4 and 5 | HNS tenants; B's boy says "merged region" | rewrite B's boy; keep A's old man nearly as is |
| Nuggets | `(55,3)`, `(26,12)` | hidden items, two flags | two one-shot pickups | keep both; one can fund the bench the guide never sits on |
| Fishing table | city shore | `ITEM_GOOD_ROD` | Lv4–6 Magikarp and Slowpoke plus Lv4–6 Dewgong, Seadra, Octillery, Corsola | reseed to basics; keep Corsola as the trophy |

## Dialogue guidance

- **Who speaks:** four locals with jobs — the guide, the lass, the boy, the fisherman — plus two house tenants and the shared Center/Mart staff. Nobody has a theory about the shape of the world; everybody has an opinion about the traffic.
- **Register:** short sentences, sea wind, practical arithmetic. The guide and the lass get one dry joke each, and no more.
- **Before / after:** before the shoes, the guide is the only person who addresses the player and everyone else is scenery. Afterwards he is just a man on a bench, and the same lines should read differently because the player is finally moving. After Gym 1 the town is a return stop; the mart clerk may acknowledge the badge without a speech.
- **The shared interiors:** keep Center and Mart lines generic, because Blackthorn hears the same text.

> GUIDE: Shoes before directions. The north road takes the soles off visitors who arrive in sandals.

> LASS: My aunt sold ferry tickets from that window for thirty years. Now she rents bicycles to people who came in off the wrong sea.

> BOY: The mountain wasn't there last summer. I've measured it twice with my bike.

> FISHERMAN: Corsola. In Johto water. I've stopped arguing with the tide and started writing down what it brings.

> OLD MAN, HOUSE A: The window shows a different hill than the one I bought this house for. I water the plants anyway.

- **Do not:** say "convergence", "merged", "two regions", "Silph", "Bill" or "Rocket"; explain the roads; make the guide a professor; give the boy a Pokédex; quote the epithet as a gag; let the fisherman name a region other than Johto.

## Inspiration

- **A Shikoku fishing port with a new bridge** — the pier survives, the ticket window closes, the co-op becomes a shop. Converts into the lass inheriting a window and the guide as a retired ferryman.
- **GSC Cherrygrove's sunset-over-the-water mood and one-road plan.** "Town of Fiery Sunsets" is a real epithet; keep the pride and drop the joke. Converts into the sign, the bench, and orange light on the mart's cardboard.
- **Roadside-station volunteers (michi-no-eki)** — a high-vis vest, a stamp, a hand-drawn map, encyclopaedic knowledge of toilets. That is the guide's entire job, and why he hands out shoes first.
- **Obon return traffic** — families arriving with coolers, nobody able to park. Converts into beach traffic the boy counts and bookings the lass cannot fill.
- **The fishing co-op's morning auction** — crates, ice, a chalkboard of prices, one old man who refuses to believe the catch list. Gives the fisherman his crates, his prices and his disbelief.

## Implementation hooks

- Wiki page: `cherrygrovecity-hns.html`
- Maps: `CherrygroveCity_hns` (`MAP_CHERRYGROVE_CITY_HNS`, `LAYOUT_CHERRYGROVE_CITY_HNS`, 65×42); `CherrygroveCity_SoutheastHouse_hns` (`MAP_CHERRYGROVE_CITY_SOUTHEAST_HOUSE_HNS`)
- Scripts: `data/maps/CherrygroveCity_hns/scripts.inc`, `data/maps/CherrygroveCity_SoutheastHouse_hns/scripts.inc`. `Pox_Cherrygrove` is in `data/scripts/plastic_ox_story.inc` but generated from `plastic_ox/alpha/build_story.py` (beat line 339) — edit the manifest, not the `.inc`.
- Gates and flags: `FLAG_POX_STORY_STARTER` (guide refuses without the starter), `FLAG_POX_STORY_CHERRYGROVE` (one-shot), `FLAG_POX_TRIGGERS_ENABLED` (walkable-build bypass), `FLAG_SYS_B_DASH` (shoes), `FLAG_RECEIVED_GOOD_ROD`
- Items and encounters: `ITEM_GOOD_ROD`, `ITEM_NUGGET` twice; fishing table `gPoxCherrygroveCityHns`
- Known gaps: `CherrygroveCity_EventScript_GuideGent` is dead code with the better text; `PoxRegion_Arrival_CherrygroveCity_hns` is an empty `end`; city music is `MUS_RG_VIRIDIAN_FOREST`; the sign's "Now-Confusing" and house B's "merged region" are the two lines that break the restraint rule; Center and Mart are shared with `BlackthornCity_hns`, so town-specific lines there will be heard in both; two of five doors are unsigned houses; the map has no trainers and no coord events.

## Open questions

- Is the guide's errand list (Center, Mart, shoes, Route 2) meant to survive as dialogue, or should it move to a sign or postcard now that the town has other voices?
- The fishing table is the only act-1 source of a Lv5 Dewgong or Seadra. Is that deliberate "the sea is wrong" reward, or should it be reseeded to basics with Corsola as the only anomaly?
- Keep the two anonymous houses as HNS leftovers, or give each a Cherrygrove tenant and a door sign? They are currently the only interiors in town with no reason to knock.
- Cut "Now-Confusing" from the sign? It is the one line in town that winks at the player instead of the world.
