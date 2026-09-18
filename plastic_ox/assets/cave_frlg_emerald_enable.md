# Cave_Frlg secondary tileset — Emerald activation

Source: pokefrlg secondary tileset already present in this checkout at
`data/tilesets/secondary/cave_frlg/` (tiles, palettes, metatiles,
metatile_attributes). No binary assets were copied, edited, or re-rendered;
only source inclusion changed.

- `src/data/tilesets/headers.h`: moved the `gTileset_Cave_Frlg` definition out
  of the FRLG-only branch to the shared tail; single definition remains.
- `src/data/tilesets/graphics.h`: moved the Cave_Frlg tiles/palette INCBINs to
  the shared tail (outside `#if IS_FRLG`).
- `src/data/tilesets/metatiles.h`: moved the Cave_Frlg metatile/attribute
  INCBINs to the shared tail (outside `#if !IS_FRLG`).

Purpose: native FRLG MtMoon B1F/B2F layouts (keep `layout_version: frlg`,
32-bit attributes, `include_in_versions: ["emerald"]`) can activate for the
PU block without new geometry.
