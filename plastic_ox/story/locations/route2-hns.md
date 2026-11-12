---
title: Route 2
slug: route2-hns
kind: Route
act: 1
stage: "0 — Opening network"
depth: supporting
wiki: route2-hns
maps: [Route2_hns]
flags: [FLAG_POX_HIDDEN_ROUTE2_1, FLAG_POX_HIDDEN_ROUTE2_5, FLAG_POX_HIDDEN_ROUTE2_19]
items: [ITEM_REVIVE, ITEM_POKE_BALL]
status: drafted
---

# Route 2

## Snapshot

The abandoned draft of Route 2: the same 24×80 corridor the player climbs from
Cherrygrove to Rustboro, kept as a second map nothing can reach. `Route2_hns`
(`MAP_ROUTE2_HNS`) has no connections, warps or coord events, and
`plastic_ox/alpha/region_v7.py` lists it in the `retired` set; what survives is
scenery, two signs describing a replaced world, and a hidden Revive nobody can
collect. An archive record, not a scene.

## Plot points

1. **Nothing enters, and it is the pre-port draft of the live road.** No script
   or map in `data/` names `Route2_hns` except `data/maps/map_groups.json`; the
   player walks `Route2_Frlg` (`MAP_ROUTE2`), which reuses `LAYOUT_ROUTE2_HNS`
   and joins `MAP_CHERRYGROVE_CITY_HNS` to `MAP_RUSTBORO_CITY`.
2. **Its signs describe the earlier topology.** `Route2_EventScript_Sign2` at
   `(14,12)` reads "VIRIDIAN FOREST ahead. Probably."; `Route2_EventScript_Sign3`
   at `(7,73)` reads "South: RUSTBORO CITY. Yes, really." The live map puts a
   DARK CAVE sign and "CHERRYGROVE - RUSTBORO" on the same two tiles.
3. **The loot is stranded.** Item balls at `(20,55)` and `(17,72)` both run
   `finditem ITEM_POKE_BALL`; the hidden item at `(13,4)` is an `ITEM_REVIVE` on
   `FLAG_POX_HIDDEN_ROUTE2_19`. The live map carries `ITEM_ETHER` and
   `ITEM_PARALYZE_HEAL` instead, so nothing here was meant to duplicate.
4. **Retirement is half-done.** The generator empties connections, warps, coord
   events and `PoxRegion_*` objects and truncates `Route2_hns_MapScripts` to a
   bare `.byte 0`, but leaves the item balls, signs, hidden Revive and five
   unused text labels in place.

**Must not:** give this map a scene, an NPC, a quest, or an "odd presence" line.
Do not treat its sign copy as canon, and do not wire a warp here — its
coordinates sit inside the live Route 2 and the player would arrive with no way
out.

## Key interactions

No interaction here is reachable; the table exists so cleanup closes each item
deliberately.

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Item ball | `Route2_hns` `(20,55)`, `Route2_EventScript_Item1` | `FLAG_POX_HIDDEN_ROUTE2_1` | `finditem ITEM_POKE_BALL`, unreachable | delete with the map, or move the pickup to the live route |
| Item ball | `(17,72)`, `Route2_EventScript_Item5` | `FLAG_POX_HIDDEN_ROUTE2_5` | identical duplicate reward, unreachable | delete; two identical balls on one route read as a bug |
| Hidden item | `(13,4)` | `FLAG_POX_HIDDEN_ROUTE2_19` | `ITEM_REVIVE`, never findable | re-place it on the live map's north half, or drop the allocation |
| Both signs | `(14,12)` `Route2_EventScript_Sign2`, `(7,73)` `Route2_EventScript_Sign3` | none | "VIRIDIAN FOREST ahead. Probably." and "South: RUSTBORO CITY. Yes, really." — both contradict the live map | retire; if kept, name Dark Cave and Cherrygrove |

## Dialogue guidance

- **Nobody speaks here.** The only authored text is two signposts and five orphan
  labels; there is no NPC, no trigger and no way in.
- If kept as an archive loop, the register is civic and dry: people who maintain
  a road after everyone stopped using it — jobs, weather, a schedule, no
  interest in the player's errand. Sign copy names places that touch the live
  Route 2 — Ilex Forest, Cherrygrove, Rustboro, Dark Cave — never Viridian.

> SURVEYOR: Chainage ends at this post. The road goes on for another half mile,
> and so do I.

> SIGN PAINTER: They gave me one stencil for two roads. I painted the wrong name
> twice and nobody wrote in.

> CHILD: Mum says this road used to reach the sea. It doesn't reach the shop.

- **Do not:** mention convergence, Team Rocket, Bill or Silph; give the map a
  ghost, a voice-over, or an apology for cut content.

## Inspiration

- **Paper roads.** New Zealand and Ireland carry roads that were surveyed, exist
  legally, and were never built; walking one is a survey line through a paddock.
- **The A625 at Mam Tor.** A British road closed by a landslip in 1979 and left
  as a right of way: signposted, walkable, quietly wrong.
- **Bypassed main streets.** A town the highway went around keeps the wide
  pavement, the faded centre line and one shop that refused to move; the
  surveyor, the painter and the grazier using the verge staff this map.

## Implementation hooks

- Wiki page: `route2-hns.html`
- Maps: `Route2_hns` (`MAP_ROUTE2_HNS`), sharing `LAYOUT_ROUTE2_HNS` with the
  live `Route2_Frlg` (`MAP_ROUTE2`); registered in `data/maps/map_groups.json`.
- Scripts: `data/maps/Route2_hns/scripts.inc`; retirement switch in
  `plastic_ox/alpha/region_v7.py` (`retired`).
- Flags / items: `FLAG_POX_HIDDEN_ROUTE2_1`, `FLAG_POX_HIDDEN_ROUTE2_5`,
  `FLAG_POX_HIDDEN_ROUTE2_19`; `ITEM_POKE_BALL` twice, `ITEM_REVIVE` once.
- Known gaps: unreachable map kept for save and map-group numbering; stray
  objects, signs and a hidden item survive retirement; both notes share a layout.

## Open questions

- Retire or archive? Recommendation: keep the registration but strip the
  objects, signs and hidden Revive, or move the Revive to the live route.
- Should `route2-hns.html` stay a wiki page, redirect to `route2-frlg.html`, or
  keep a note titled "Route 2 (retired)"?
- If the hidden item goes, is `FLAG_POX_HIDDEN_ROUTE2_19` freed or reserved?
