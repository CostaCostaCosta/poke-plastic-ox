---
name: plastic-ox-map-port
description: Port, repair, or verify maps from pokehns-expansion, FRLG, or other Pokémon Gen 3 projects in the local poke-plastic-ox region. Use for malformed imported tiles, cross-generation map crashes, Ilex/Dark Cave regressions, seam offsets, warps, ledges, or new Plastic-Ox route imports; do not use for original map art or unrelated ROM mechanics.
---

# Plastic-Ox map porting

Treat a port as an engine-data conversion, not a blockmap copy. Preserve the
source geometry, but make layout partitioning, tilesets, behaviors, events,
connections, encounters, and runtime transitions explicit in Plastic-Ox.

## Establish the port

Work in `/home/eddie/repos/poke-plastic-ox` unless the user supplies another
checkout. Record the source checkout/revision, source map/layout, destination
map group, intended ports, tilesets, event policy, encounter source, and exact
verification commands. Inspect dirty files before editing and preserve
unrelated changes.

Identify the source layout family before copying assets:

- Emerald: 512 primary metatiles/tiles and 6 primary palettes, 16-bit attrs.
- FRLG: 640 primary metatiles/tiles and 7 primary palettes, 32-bit attrs.
- Heart & Soul (`hns`): 640 primary metatiles/tiles and 7 primary palettes,
  but Emerald-format 16-bit attrs and a 2x2 border.

For HNS layouts, preserve `"layout_version": "hns"` and add
`"include_in_versions": ["emerald"]`. Never default HNS to Emerald: that
shifts secondary IDs by 128 and corrupts visuals, collision, and VRAM copies.

Run the deterministic audit before and after edits:

```sh
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py \
  /home/eddie/repos/poke-plastic-ox
```

## Convert and connect

Use the destination layout's own primary and secondary tilesets together.
Copy blockmaps only with their matching tileset graphics, metatiles,
attributes, palettes, and animations. Remap behavior enums by name with
`plastic_ox/agent/remap_metatile_behaviors.py`; numeric behavior IDs are not
portable across forks.

Keep generated files generated. Update `data/layouts/layouts.json`, map JSON,
map groups, source assets, and import tooling, then let the normal build
regenerate registrations. Rewrite imported story scripts and explicitly choose
encounters. Pin HNS wanderer NPCs unless a soak test proves their movement safe.

For a new seam, cave transition, or ledge, read
[references/port-verification.md](references/port-verification.md) before
editing. It contains the required coordinate and runtime assertions.

## Prove the result

Build with the repository's configured devkitARM command. Re-run the relevant
headless leg in both directions and inspect fresh screenshots; map identity and
reachability alone do not catch tileset-partition corruption. Dark Cave must be
entered and exited without a crash. Ilex must show coherent forest tiles, not
merely remain traversable.

Treat a ledge as approach → behavior/art tile → landing. Assert behavior,
collision, the two-coordinate jump, blocked reverse traversal, and that the
ledge metatile ID at the reported behavior coordinate is the artwork shown in
the screenshot. Do not diagnose the animation midpoint as the landing.
