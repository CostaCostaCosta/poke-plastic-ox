# Kanto map-art provenance

Plastic Ox keeps the Kanto maps in the `PlasticOxJohtoKanto`,
`PlasticOxDungeons`, and `PlasticOxInteriors` groups paired with the tileset
implementation that supplied their layouts.  This is deliberate: a map is not
retiled across regional art families merely because its neighbour uses another
one.

## Active Kanto HnS implementation

| Source repository | Asset implementation | Credit | Maps using it in Plastic Ox |
| --- | --- | --- | --- |
| [PokemonHnS-Development/pokehns-expansion](https://github.com/PokemonHnS-Development/pokehns-expansion) (checked at `44f50eedef`) | `kanto_general_hns`, `kanto_building_hns`, and the matching Kanto HnS secondary tilesets (`viridian_city_hns`, `pewter_city_hns`, `cerulean_city_hns`, `lavender_town_hns`, `saffron_city_hns`, `celadon_city_hns`, `fuchsia_hns`, `vermilion_hns`, `pallet_town_hns`, `indigo_plateau_hns`, `cave_mt_moon_hns`, `kanto_mart_hns`, and related interiors) | Pokémon Heart and Soul project. Its README asks downstream projects to credit Pokémon Heart and Soul and retain the upstream credit chain; see its `CREDITS.md` for contributor credits. | Active HnS Kanto routes, cities, landmarks, and interiors, including the replacements itemized below. |
| Nintendo / Game Freak, through the open-source `pokeemerald-expansion` and HnS decompilation asset pipeline | FireRed/LeafGreen-compatible Kanto fallback tilesets (`general_frlg`, `building_frlg`, and their matching secondary tilesets) | Retain the upstream pret, RHH, HnS, Nintendo, and Game Freak attribution chain. | Legacy registered maps and inactive fallbacks only. |

The HnS layout binaries and their matching tilesets were imported together.
Plastic Ox retains `layout_version: "hns"`; it does not reinterpret those
blockmaps as Emerald or FRLG layouts.  That preserves metatile partitions,
collision attributes, warps, and event coordinates.

`PalletTown_Frlg` now deliberately keeps its stable Plastic Ox map ID, events,
Route 101 connection, and three interior destinations while selecting the
complete 24x20 `PalletTown_hns` donor layout.  HnS uses the same three doorway
coordinates, so this replacement required no geometry redraw or coordinate
compromise.  Its map/border and Kanto General/Pallet Town tileset pair are from
the pinned HnS revision above.

This pass restores the source `InitTilesetAnim_JohtoGeneral` callback for
`kanto_general_hns`. H&S explicitly shares this callback between Kanto and
Johto; its 21 Kanto animation frames are byte-identical to Johto's. They are
deduplicated under `johto_general_hns/anim`, restoring the intended Kanto
flowers and water animation without changing its architecture or palettes.
Live VRAM checks on Saffron confirm the imported frames animate correctly.

## September 2026 FRLG-leftover migration

The active Route 2, Route 8, Route 19, and Route 20 implementations now use
complete HnS donor geometry and artwork. Plastic Ox retains the stable map IDs
where scripts refer to them, then reapplies its connections, destinations,
NPCs, items, and progression gates to donor-valid coordinates. Route 20's
complete 120x20 HnS route is split at the existing Plastic Ox west/east module
boundary without changing its metatiles.

| Plastic Ox map | Region | Donor map | Donor project | Tileset family | Status |
| --- | --- | --- | --- | --- | --- |
| `Route2_Frlg` | Kanto | `Route2_hns` | Pokémon Heart & Soul 2.0 | HnS Kanto General / Viridian | imported; gameplay ports reapplied |
| `Route8_Frlg` | Kanto | `Route8_hns` | Pokémon Heart & Soul 2.0 | HnS Kanto General / Lavender | imported; tunnel and Saffron ports moved |
| `Route19_Frlg` | Kanto | `Route19_hns` | Pokémon Heart & Soul 2.0 | HnS Kanto General / Fuchsia | imported; southern approach reapplied |
| `PlasticOx_Route20West` | Kanto | west section of `Route20_hns` | Pokémon Heart & Soul 2.0 | HnS Kanto General / Lavaridge | imported; Seafoam-side module retained |
| `PlasticOx_Route20East` | Kanto | east section of `Route20_hns` | Pokémon Heart & Soul 2.0 | HnS Kanto General / Lavaridge | imported; Mossdeep-side module retained |
| `Route2_House_Frlg` | Kanto | `Route2_House_hns` | Pokémon Heart & Soul 2.0 | HnS Kanto Building / House | imported; resident events projected |
| Route 2 gate maps (3) | Kanto | matching HnS Route 2 / Viridian Forest gates | Pokémon Heart & Soul 2.0 | HnS Kanto Building / Gate | imported; Plastic Ox warp graph reapplied |
| Seafoam Islands 1F–B4F | Kanto | — | FireRed/LeafGreen fallback | FRLG General / Seafoam | retained: HnS supplies only 1F and B1F, not the complete active five-floor dungeon |
| Underground Path entrances/tunnel | Kanto | — | FireRed/LeafGreen fallback | FRLG Building / Underground | retained: no complete HnS equivalent exists at the pinned revision |

Other active FRLG interiors were compared against the pinned HnS tree. They
remain FRLG when there is no complete one-for-one HnS donor implementation;
graphics and geometry remain paired. Registered inactive legacy maps are not
claimed as migrated.

## Evaluated sources not imported

* [jschoeny/TARC2](https://github.com/jschoeny/TARC2), revision `0da79a2d`,
  packages Morlock-Liam's credited **Gen 2 Kanto Assets** in its
  `olden_times` tileset (TARC2's `HACK_CREDITS.md` credits Morlock-Liam and
  links the original asset post).  Its public project maps are authored for
  `olden_times` layouts rather than the Kanto layouts used here.  Importing
  those graphics alone would require rebuilding existing Kanto blockmaps, so
  it was intentionally not used.
* [Pawkkie/Team-Aquas-Asset-Repo](https://github.com/Pawkkie/Team-Aquas-Asset-Repo)
  was checked for supplemental Kanto assets.  No component was added because
  the relevant existing Kanto maps already have a compatible HnS tileset
  implementation.  The repository's reuse policy requires credit to each
  named original creator; no asset with incomplete per-asset provenance was
  selected.

No original pixel art was created for this work.
