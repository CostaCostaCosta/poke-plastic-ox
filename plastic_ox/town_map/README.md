# Plastic Ox town-map concept

**In-game fly map:** `build_fly_map.py` turns this concept's terrain into the
ROM's region map (Fly, Town Map). It holds the v7 grid layout: the 13 fly
destinations (towns plus the Pokémon League at Indigo Plateau), landmarks and
route chains on the 28×15 region-map grid, plus each destination's visited flag
and landing tile. Edit the layout there and rerun it; never hand-edit its
outputs (listed in `../generated_manifest.json`). `fly_map_preview.png` is a
labelled review image. Visited flags are set automatically on entering a town
(`PoxFlyMap_MarkVisited` in `src/region_map.c`).

Version status: these rendered assets predate the v7 implementation plan and
must be refreshed after its topology is verified. Current design references
are [map v7](../plastic_ox_map_v7.md), [topology](../plastic_ox_topology.svg), and
the [alpha implementation plan](../alpha/PLAN.md).

A high-level visual based on the current Plastic Ox region and the supplied
Johto town-map reference. Land shapes and diagram coordinates are authored for
legibility, not geographic or map-tile accuracy. This is a presentation asset;
it has not replaced the ROM's region-map tilemap or location lookup tables.

- `plastic_ox_town_map.svg`: editable, labeled 1600×1100 master.
- `plastic_ox_town_map.png`: labeled image for review or sharing.
- `plastic_ox_town_map_unlabeled.svg` / `.png`: terrain, paths, and markers
  without title, labels, route badges, or legend.
- `town_map_240x160.png`: 4-bit indexed, 16-color, unlabeled GBA-size concept.
- `town_map_240x160_preview.png`: nearest-neighbor enlargement of that asset.
- `layout.json`: marker positions at master and GBA-preview sizes, plus
  authored route corridors and guided passages.

The map emphasizes towns and the main journey. Route corridors simplify gates,
portals, and intermediate maps; secondary disconnected routes and ordinary
interiors are omitted. Dotted lines summarize guided travel and can require
story progression. Ecruteak–Fortree represents the regional journey via the
Route 38/Route 119 leg, not a claim of a direct seamless connection. For exact
map boundaries, cave warp endpoints, and directed connections regenerate an
implemented-layout view with `../demo/render_region_layout.py` (the previous
`region_layout.svg` has been removed); for historical navigation findings see
`../demo/REGION_RENDERING_REVIEW.md`.

Regenerate all assets with Python, Pillow, and Chrome/Chromium:

```sh
python3 plastic_ox/town_map/export_town_map.py
```

For SVG and master coordinates only:

```sh
python3 plastic_ox/town_map/render_town_map.py
```

Colors follow the reference's convention: red cities, blue towns, green
landmarks, and a purple League marker. Cave circles contain an entrance icon.
The GBA preview uses a fixed palette to preserve marker colors. A final in-game
implementation still needs UI-space fitting, tile conversion, map-section
coordinate assignments, and selection/highlight behavior.
