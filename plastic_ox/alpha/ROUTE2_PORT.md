# Route 2 replacement

Source: existing FRLG modules in poke-plastic-ox at
`8232b5fc5ee9df3e8e354618cb164502750be605`, with the user's pre-existing
working-tree changes preserved. No blockmaps or tileset binaries were copied
or edited. Route 2 replaces Route 1, Route 31, and Route 104 Top in the active
opening graph; the old map IDs remain registered for save compatibility.

Route 2 uses `LAYOUT_ROUTE2_HNS` (24 × 80), `gTileset_Kanto_General_Hns`, and
`gTileset_ViridianCity`. Its existing `viridian_city_frlg` tiles, 16 palettes,
metatiles, and 32-bit FRLG attributes are now included in Emerald. Layout
partitioning remains `frlg`. Both forest gatehouses, the house, and the east
building retain their native layouts and warp indices, with Emerald inclusion
enabled. These modules remain in their existing FRLG map groups. Ilex and
Dark Cave retain their existing HNS layouts, graphics, and behavior conversion.

| Entrance | Destination / return |
| --- | --- |
| Cherrygrove north trail | Route 2 south; reciprocal trail |
| Route 2 north trail | Rustboro south; reciprocal camera seam, Ilex objective required in story mode |
| Route 2 `(5,51)` / `(6,51)`, warps 2 / 9 | South forest gatehouse; its north exit reaches Ilex warp 0 |
| Ilex `(22,63)`, warp 0 | South gatehouse warp 3; returns to Route 2 warp 2 |
| Route 2 `(5,13)` / `(6,13)`, warps 0 / 1 | North forest gatehouse; its south exit reaches Ilex's northern plaza |
| Ilex `(20,14)`, approach `(20,15)` | North gatehouse `(7,9)`; Ilex objective required in story mode |
| Ilex `(20,15)`, warp 1 | Arrival-only anchor on ordinary cave-floor behavior, not an exit trigger |
| Route 2 `(17,11)`, warp 3 | Dark Cave South Side warp 0 `(14,20)`; returns to Route 2 warp 3 |
| Dark Cave warp 1 | Existing Route 46 connection retained |

The Cherrygrove town trail is a native reciprocal camera connection using
offsets `22` and `-22`. Route 2 and Rustboro now use a reciprocal camera seam
with offsets `-8` and `8`, aligning Route 2 `(8, 0)` with Rustboro `(16, 59)`.
An Ilex-flagged ranger blocks the Route 2 edge until the objective is complete.
The remaining trail coordinates and requirements are generated into
`region_manifest.json` and pinned in `region_ports.json`.
Route 2's Cut trees and east-side shortcut
are retained; the Rustboro trail also checks Ilex completion so the shortcut
cannot bypass that story objective. Local building warps, items, and signs
remain; Kanto-only trade/aide handlers become local dialogue. The off-map
Viridian tree clone is removed. Two item pickups use unique persistent flags
at offsets 58 and 59 of the existing item flag run.

Route 2 uses the existing authored Route 31 morning/day/night grass and fishing
tables. Their labels are retained, but their runtime map ID is `MAP_ROUTE2`.
The encounter installer also targets Route 2 for the Route 31 document section.
Ilex and Dark Cave encounter tables are unchanged.

## Regeneration and verification

`python3 plastic_ox/alpha/apply_region.py` emits an apply_patch patch for the
region alone. It preserves independent story changes and is idempotent.
The full story generator calls the same `apply_region` implementation.
`python3 plastic_ox/topology_app/build_catalog.py` regenerates the topology
catalog. Route 2 exposes N/S land, two Ilex gatehouse, and one Dark Cave port;
Ilex exposes N/E gate ports. The retired routes remain available as library
parts, not active opening connections.

Build the primary ROM:

```sh
PATH=/home/eddie/devkitpro/opt/devkitpro/devkitARM/bin:$PATH make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
```

Run the following Python checks with
`LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64`
and `/home/eddie/.venvs/mgba311/bin/python`:

- `plastic_ox/demo/test_region_v7.py --only route2`: town trails and northern Ilex return pass.
- `plastic_ox/demo/test_region_v7.py --warps --only Route2`: native gatehouse, house, east building, and cave entries/returns pass.
- `plastic_ox/demo/test_region_v7.py --warps --only IlexForest`: southern exit passes; northern arrival-only anchor excluded.
- `plastic_ox/demo/test_region_v7.py --warps --only DarkCave`: both cave mouths pass.
- `plastic_ox/demo/test_region_v7.py --only route2 --closed`: all three Ilex requirement checks reject traversal correctly.
- `plastic_ox/demo/test_region_walk.py route2`: twelve continuous D-pad transitions, Cherrygrove → Ilex → Rustboro → Ilex → Cherrygrove; no Surf or intermediate setup warps.
- `plastic_ox/demo/test_route2_encounters.py`: actual grass battles after entering Route 2 from each town; enemy species match the authored encounter pool.

Fresh screenshots in `plastic_ox/demo/shots/region_v7` and
`plastic_ox/demo/shots/region_walk` show coherent forest, gatehouse, route,
and cave tiles. The HNS import audit and `git diff --check` pass.
The separate persistent-flag audit still reports two pre-existing collisions:
the working-tree EXP ALL flags share `0x26E` and `0x26F` with Seafoam item flags.
The Route 2 item flags do not overlap these allocations.
