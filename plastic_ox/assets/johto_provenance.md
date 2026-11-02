# Johto visual assets

## SoulGold regional migration

Eemeliri/SoulGold revision `768612c8ebcecf69c0083e918039e083ca1a5ba4`
was evaluated as the preferred donor. It is not runtime-compatible with this
engine: SoulGold defines `NUM_METATILES_IN_PRIMARY` as 1024, while Plastic Ox
supports Emerald's 512-primary and HnS/FRLG's 640-primary layout families.
Complete imports built, but fresh mGBA inspection showed secondary art as
striped primary-tile corruption. The attempted wider transplant also failed
16 of 78 progression crossings before adaptation. Retiling or truncating the
maps would violate the map-geometry/art identity rule, so all active Johto
maps remain on their complete HnS implementations. The pinned audit/import
harness is `plastic_ox/assets/import_soulgold_johto.py`; runtime generation is
deliberately disabled until Plastic Ox gains a 1024-primary layout version.

| Plastic Ox map | Region | Donor map | Donor project | Tileset family | Status |
| --- | --- | --- | --- | --- | --- |
| CherrygroveCity_hns | Johto | CherrygroveCity_hns | Pokémon HnS | HnS Johto General / Cherrygrove | retained; SoulGold 1024-primary incompatibility |
| IlexForest_hns | Johto | IlexForest_hns | Pokémon HnS | HnS Johto South / Ilex Forest | retained; SoulGold 1024-primary incompatibility |
| Route33_hns | Johto | Route33_hns | Pokémon HnS | HnS Johto South / Azalea | retained; SoulGold broke Mt. Moon/Goldenrod crossings |
| GoldenrodCity_hns | Johto | GoldenrodCity_hns | Pokémon HnS | HnS Johto General / Goldenrod | retained; SoulGold broke both progression edges |
| Route35_hns | Johto | Route35_hns | Pokémon HnS | HnS Johto General / Goldenrod | retained; SoulGold broke park chain landings |
| NationalPark_Normal_hns | Johto | NationalPark_Normal_hns | Pokémon HnS | HnS Johto General / National Park | retained; SoulGold broke both progression edges |
| Route36_hns | Johto | Route36_hns | Pokémon HnS | HnS Johto General / Violet | retained; SoulGold edge geometry incompatible |
| Route37_hns | Johto | Route37_hns | Pokémon HnS | HnS Johto General / Ecruteak | retained; SoulGold broke Ecruteak landing |
| EcruteakCity_hns | Johto | EcruteakCity_hns | Pokémon HnS | HnS Johto NorthWest / Ecruteak | retained; SoulGold broke Route 119 and League portals |
| DarkCave_SouthSide_hns | Johto | DarkCave_SouthSide_hns | Pokémon HnS | HnS Johto General / Cave Default | retained; SoulGold 1024-primary incompatibility |
| Route44_hns | Johto | Route44_hns | Pokémon HnS | HnS Johto NorthEast / Cianwood | retained; SoulGold 1024-primary incompatibility |
| BlackthornCity_hns | Johto | BlackthornCity_hns | Pokémon HnS | HnS Johto NorthEast / Blackthorn | retained; SoulGold broke Route 45 edge |

Routes 29-46, Cherrygrove, Ilex, Goldenrod, National Park, Ecruteak, Dark
Cave, and Blackthorn therefore remain HnS. This retains Plastic Ox scripts,
objects, trainers, items, encounters, warps, connections, and collision
repairs without mixing SoulGold geometry with HnS artwork. The retained set
passes all 78 actual D-pad progression crossings.
`PlasticOx_BurnedTower` remains the existing Plastic Ox interior: it is a
story-specific map rather than the prior HnS `BurnedTower_1F`, so replacing it
would materially change authored progression. Existing gates and interiors
also remain HnS until their outdoor doorway contracts are migrated as a unit.

## Source and reuse record

| Field | Record |
| --- | --- |
| Source repository | [PokemonHnS-Development/pokehns-expansion](https://github.com/PokemonHnS-Development/pokehns-expansion) |
| Donor revision audited | `44f50eedefe58691b0444973e4138e9190d8fafc` (2026-08-23) |
| Asset family | Pokémon Heart and Soul 2.0 (HnS): Johto outdoor, town, forest, building, cave, and interior tilesets with their matching layouts |
| Reuse evidence | The donor README calls HnS “completely open source” and “intended to be a base for a new generation of Johto rom hacks,” and asks downstream users to credit Pokémon Heart and Soul and retain its credit chain. No separate repository-wide art licence file is shipped at the audited revision. |
| Credit | Pokémon Heart and Soul / PokemonHnS-Development and the donor's full [CREDITS.md](https://github.com/PokemonHnS-Development/pokehns-expansion/blob/main/CREDITS.md) contributor chain. HnS does not assign individual artists to these tilesets, so no per-tileset artist attribution can be made reliably. |

The checked-in HnS artwork is reused as donor artwork; Plastic Ox created no
pixel art. The repository should continue to retain the HnS credit chain in
releases. Do not substitute uncredited third-party tiles for these maps.

## Integrated asset sets

The following source-compatible pairs are registered by the layouts. The
primary and secondary member must travel with the map block data; replacing
either side changes the visible region and can invalidate its collision
metatiles.

| HnS primary family | HnS secondary family | Maps using the pair |
| --- | --- | --- |
| `johto_general_hns` | `new_bark_town_hns`, `cherrygrove_city_hns`, `goldenrod_hns`, `violet_city_hns`, `ecruteak_city_hns`, `route38_farmland_hns`, `national_park_hns` | Cherrygrove, Goldenrod, Routes 29–38 (where present), National Park, and their Johto town/route variants |
| `johto_south_hns` | `ilex_forest_hns`, `azalea_town_hns` | Ilex Forest and Route 33 |
| `johto_north_west_hns` | `ecruteak_city_hns` | Ecruteak City |
| `johto_north_east_hns` | `blackthorn_hns`, `cherrygrove_city_hns`, `cianwood_city_hns` | Blackthorn City and Routes 44–46 |
| `johto_building_hns` | `gate_standard_hns`, `house_lab_hns`, `johto_mart_hns`, `pokemon_center_white_hns`, `sea_cottage_hns` | Johto gates, generic houses, Goldenrod Bill's House, Johto Mart, Johto-style Pokémon Center, and Route 25 Bill's House |
| `johto_general_hns` | `cave_default_hns`, `cave_mt_moon_hns` | Dark Cave South Side and Mt. Moon Cave |

`PokemonCenter_Kanto_hns` intentionally uses the HnS `johto_building_hns` /
`kanto_pokemon_center_hns` implementation. It is retained as a compatible
source pair, not rebuilt with a different primary. Kanto map-family choices
are recorded separately.

## Current audit and migration status

The static Johto tiles and palettes were retained because the intended HnS
implementation is already present intact. Missing source animations were
restored in this pass:

* Imported the donor's 21 shared outdoor flower, sand/water-edge and
  water/current frame images, plus 15 National Park fountain/flower images.
* Restored the source callback for Johto General, South, NorthEast, NorthWest
  and Kanto General. Their donor frame sets are identical and share one copy.
* Restored National Park's large/small fountains and red/yellow flowers, with
  the secondary DMA destination based on the actual 640-tile HNS partition.
* Live mGBA checks verify that the imported frame bytes reach the intended
  VRAM ranges and change over time. No graphics outside the tileset systems,
  map blockdata, or behavior attributes were replaced.

The existing static source pairing was also verified:

* All 52 HnS layouts pass the deterministic HnS metadata and asset-bound audit.
* Every audited Johto primary/secondary tileset retains donor `tiles.png`,
  palette files, and metatile artwork exactly. The target's
  `metatile_attributes.bin` differs only because behavior IDs were translated
  by name for the Plastic Ox engine; its `*.orig` copy preserves the donor
  attributes.
* Map borders and blockmaps match the donor for the active Johto world, except
  for the documented targeted landing repairs: Dark Cave's two exit graphics
  use dedicated ladder-behavior metatiles, Ilex uses its retained exit repair,
  and shared interiors have their target-specific door layouts. These are
  collision/warp fixes, not a visual reskin.
* The donor HnS animations are also wired for the outdoor primary families
  and National Park. `johto_general_hns` supplies the shared 21 primary frame
  images, and `national_park_hns` supplies its 15 fountain/flower frames.
  Their callbacks write only source-defined visual tile ranges; map blockmaps,
  collision attributes, events, and warps are untouched.

The unchanged, source-faithful Johto outdoor maps are: Cherrygrove City,
Goldenrod City, Ecruteak City, Blackthorn City, Ilex Forest, National Park,
Dark Cave South Side, and Routes 29, 30, 31, 33, 34, 35, 36, 37, 38, 44, 45,
and 46. Their gates, houses, mart, and Pokémon Center interiors retain the
matching HnS building families listed above.

## Safe future import procedure

For another HnS Johto map, copy its layout blockmap, border, primary tileset,
secondary tileset, graphics, palettes, metatiles, attributes, and animations
as one unit from the pinned donor. Preserve `"layout_version": "hns"` and
`"include_in_versions": ["emerald"]`; HnS has a 640-primary-metatile,
seven-primary-palette partition with Emerald-format 16-bit attributes. Then
remap behavior enums by name, keep any target-specific warp landing repair,
and run:

```sh
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py "$PWD"
```

Do not reuse an HnS blockmap with a Hoenn, FRLG, or unrelated Kanto tileset.
