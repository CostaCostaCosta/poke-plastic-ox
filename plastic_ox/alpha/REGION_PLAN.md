# Region Plan — Plastic Ox Alpha v7

Status: target topology, pending implementation. See [PLAN.md](PLAN.md) for
milestones, assumptions, and acceptance. Earlier wave sketches and shipped
substitutions are retained only in [LEGACY_REGION_PLAN.md](LEGACY_REGION_PLAN.md).

The [v7 map](../plastic_ox_map_v7.md) supplies traversal rules and the
[SVG](../plastic_ox_topology.svg) supplies the physical arrangement. Diagram
ports identify intent; exact ROM seams, warp indices, landing coordinates,
collision and offsets must be measured during M0 and each map milestone.

## Target legs and migration inventory

| Leg | Required journey | Asset candidates and changes |
|---|---|---|
| A — Opening | Pallet → Route 101 → Oldale → Route 29 → Cherrygrove → Route 1/31 → Ilex | Keep existing Pallet, Route101, Oldale, Route29_hns, CherrygroveCity_hns, Route31_hns, IlexForest_hns. Route1_Frlg exists on disk; verify build registration/format before reuse. Resolve the Route 1/31 seam order from SVG ports and walkable entrances. Route30 remains optional only if it cannot skip Ilex. |
| A-return — Western loop | Blackthorn → Route 45 → Route 46 → early network; Dark Cave side links | Preserve native downhill ledges and repaired DarkCave_SouthSide_hns exits. Audit all cave mouths and upper Route46 access; no early climb or cave route to Blackthorn. |
| B — Gym 1 | Ilex → Route 104 Top → Rustboro | Reuse northern Route104 and RustboroCity, isolate southern/native side exits. Replace the old Route34/116 approach and any Ilex→Goldenrod bypass. |
| B-side — Cottage | Rustboro portion → Route 24 → Route 25 → Bill's Sea Cottage, then return | Route24_hns, Route25_hns, Route25_BillsHouse_hns exist. Wire the actual branch near Rustboro; restore a local Cottage exit. Remove Fortree CottageGuide/CottageExit transport and Route24→Route7 escape. |
| C — Rocket I/Gym 2 | Rustboro → Route 44 → Mt. Moon → Route 33 → Goldenrod | Route44_hns and Route33_hns require donor import/registration (verify during M0); reuse MtMoon_Cave_hns with measured entrance/exit pairing. Retire Route2/3/4/14 mainline substitutions and town-skip travel actors. Make dungeon completion required on the forward path. |
| D — Gym 3 | Goldenrod → Route 35 → National Park → Route 36 → Route 37 → Ecruteak | Reuse HNS modules/gatehouses. Park must be on the main path, not an optional spur off Route35→36. Preserve measured working Route36/37/Ecruteak seams where compatible. |
| E — Gym 4 | Ecruteak east → Route 119 → Weather Institute → Fortree | Rewire east access; retire west Route38 route and direct Weather Institute transport. Reuse native Route119/Fortree and Institute interiors with authored callbacks. Require Morty and Weather progression. |
| E-shortcut | Route 36 east ↔ Route 110 west | Block until legitimate Fortree arrival; permanently bidirectional afterward. Remove native Route103→110 as an early bypass or gate it under the same progression contract. |
| F — Rocket II | Fortree → Route 110 → Lavender | Reuse native Route110 and LavenderTown_hns. Retire Ecruteak→Route7/Lavender and direct Fortree→Lavender transport. Tower/Fuji directs the next journey underground. |
| G — Gym 5 | Lavender → Route 8 → Underground Path → Route 7 → Route 103 → Cinnabar | Route8_Frlg, UndergroundPath_EastEntrance_Frlg, EastWestTunnel_Frlg, WestEntrance_Frlg are candidates already on disk; integrate with Route7_hns and native Route103. Audit all doors/versions. Gate Oldale-side access to the southern route until the intended segment. Remove direct Lavender→Cinnabar transport and obsolete south mainline. |
| H — Gym 6 | Cinnabar → Route 20 west coast → Seafoam → Route 20 east coast → Mossdeep | SVG specifies Route20; native FRLG Route20 and SeafoamIslands_1F/B1F/B2F/B3F/B4F_Frlg exist on disk. Select necessary floors, verify tilesets/build inclusion, currents and boulder logic. Split/isolate water halves if needed; no Surf-around path. Whirl room/service leaves the mainline. Route41 is only a documented fallback allowed by map v7. |
| I — Saffron hub | Mossdeep → Route 19/south approach → Saffron; Route 7/8 surface entrances | SVG Route19 candidate is Route19_Frlg; replace Route125/128/6 detour as needed. All surface ingress checks Space Center completion. Underground remains independent. North opens with the city; neither Bruno nor Silph gates Blackthorn or Clair. |
| J — Gym 8 | Saffron → Route 5 → Route 115 → Meteor Falls → Blackthorn | Reuse Route5_hns if registered, native Route115 and MeteorFalls floors; audit native Rustboro/Route114 access and every cave branch. No Ice Path/Route26 substitution or direct BlackthornRoad service. Blackthorn return joins leg A-return. |
| K — League | Ecruteak west → Hoenn Victory Road → League → Wallace/Steven/Lance/Blue → Bill | SVG selects native VictoryRoad_1F/B1F/B2F. Reuse alpha League rooms/Indigo service hub where suitable, checking all exits. Replace synthetic PlasticOx_VictoryRoad and Blackthorn LeagueRoad/portal as main approach. Require all eight badges at Ecruteak. |
| L — Postgame | Lavender south → harbor/ferry → Battle Frontier → later islands | Add a visible closed harbor approach and functional round-trip Frontier entry after Champion. Exact harbor map/warp endpoints and island roster are M0/M7 deliverables, not present in the SVG. |

Asset existence does not establish Emerald inclusion, safe attributes, correct
warps, or reachable entrances. Record source revision, source map/layout,
destination group, tilesets, event policy, encounters, and exact verification
commands for each import. Reuse HNS IDs where appropriate; do not rename native
maps to match a diagram label without a reason.

## Required edge conditions

| Edge | Condition in trigger build |
|---|---|
| Early world → Rustboro | Starter/opening progression and mandatory Ilex traversal |
| Rustboro → Goldenrod | Roxanne, then mandatory Mt. Moon Rocket I completion |
| Goldenrod → Ecruteak | Whitney; travel through National Park |
| Ecruteak → Route119/Fortree | Morty; Weather investigation before forward progression |
| Route36 ↔ Route110 | Reached Fortree |
| Fortree → Lavender story | Winona |
| Lavender → Cinnabar story | Fuji rescue; Underground available while Saffron closed |
| Cinnabar → mandatory Seafoam/Mossdeep passage | Blaine/key and Mansion investigation; usable Surf |
| All Saffron surface entries | Space Center complete after Gym 6 |
| Saffron north → Route5/Blackthorn/Clair | Space Center complete; independent of Bruno and Silph |
| Ecruteak west → Victory Road | All eight native badge flags |
| Lavender south → harbor | Successful Champion/Hall of Fame completion |

These conditions must cover ordinary map links and alternate entry mechanisms.
Objective NPC prerequisites alone do not prevent physical sequence breaks.

## Per-leg completion record

At implementation time append: actual map IDs and tile coordinates; seam
directions and reciprocal offsets or warp indices; removed legacy links;
required and optional story events; ability availability; valid return route;
generator/import-tool changes; tests and screenshots. Any substitution must
preserve the mandatory towns/dungeons, gate timing and return paths above.

Retain HNS 640-primary/7-palette partitioning, Emerald u16 attributes and 2×2
borders. Use the import guide and map-port verification guidance for physical
conversion. Preserve Dark Cave landing repairs and Ilex visual coherence.
