# Kanto map-art provenance

Plastic Ox keeps the Kanto maps in the `PlasticOxJohtoKanto`,
`PlasticOxDungeons`, and `PlasticOxInteriors` groups paired with the tileset
implementation that supplied their layouts.  This is deliberate: a map is not
retiled across regional art families merely because its neighbour uses another
one.

## Active Kanto HnS implementation

| Source repository | Asset implementation | Credit | Maps using it in Plastic Ox |
| --- | --- | --- | --- |
| [PokemonHnS-Development/pokehns-expansion](https://github.com/PokemonHnS-Development/pokehns-expansion) (checked at `44f50eedef`) | `kanto_general_hns`, `kanto_building_hns`, and the matching Kanto HnS secondary tilesets (`viridian_city_hns`, `pewter_city_hns`, `cerulean_city_hns`, `lavender_town_hns`, `saffron_city_hns`, `celadon_city_hns`, `fuchsia_hns`, `vermilion_hns`, `pallet_town_hns`, `indigo_plateau_hns`, `cave_mt_moon_hns`, `kanto_mart_hns`, and related interiors) | Pokémon Heart and Soul project. Its README asks downstream projects to credit Pokémon Heart and Soul and retain the upstream credit chain; see its `CREDITS.md` for contributor credits. | `Route2_hns`, `Route3_hns`, `Route4_hns`, `Route14_hns`, `Route16_hns`, `Route24_hns`, `Route25_hns`, `Route5_hns`, `Route6_hns`, `Route7_hns`, `Route12_hns`, `Route21_hns`, `SaffronCity_hns`, `LavenderTown_hns`, `CinnabarIsland_hns`, `IndigoPlateau_hns`, `MtMoon_Cave_hns`, `Mart_Kanto_hns`, `PokemonCenter_Kanto_hns`, `Route25_BillsHouse_hns`, and the Kanto gates in `PlasticOxInteriors`. |
| Nintendo / Game Freak, through the open-source `pokeemerald-expansion` and HnS decompilation asset pipeline | FireRed/LeafGreen-compatible Kanto fallback tilesets (`general_frlg`, `building_frlg`, and their matching secondary tilesets) | Retain the upstream pret, RHH, HnS, Nintendo, and Game Freak attribution chain. | `PalletTown_Frlg` remains FRLG because its currently used map geometry and events are the FRLG implementation. |

The HnS layout binaries and their matching tilesets were imported together.
Plastic Ox retains `layout_version: "hns"`; it does not reinterpret those
blockmaps as Emerald or FRLG layouts.  That preserves metatile partitions,
collision attributes, warps, and event coordinates.

This pass restores the source `InitTilesetAnim_JohtoGeneral` callback for
`kanto_general_hns`. H&S explicitly shares this callback between Kanto and
Johto; its 21 Kanto animation frames are byte-identical to Johto's. They are
deduplicated under `johto_general_hns/anim`, restoring the intended Kanto
flowers and water animation without changing its architecture or palettes.
Live VRAM checks on Saffron confirm the imported frames animate correctly.

The retained FRLG fallback also covers the active Route 2, Route 8, Route 19,
the two Route 20 halves, Seafoam and Underground Path maps, and their matching
FRLG interiors. These remain paired with the artwork that supplied their
geometry. The exact inventory distinguishes registered legacy maps from the
main V7 path.

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
