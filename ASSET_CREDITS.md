# Plastic Ox regional map assets

Map geometry determines visual identity. Kanto, Johto, and Hoenn deliberately
retain different trees, architecture, terrain, and water at their boundaries.
No original pixel art was created for this migration.

| Source repository / asset | Original credit | Maps using it |
| --- | --- | --- |
| [lbsbezerra/pokeemerald-modern-oras](https://github.com/lbsbezerra/pokeemerald-modern-oras/tree/d271db57c21ac71cd009ecbfdb0562008674382c): LeoB ORAS general, Petalburg, Rustboro, Mauville, Fallarbor, Fortree, Mossdeep tilesets, palettes, water/flower/fountain and door animations | **leob0505 / lbsbezerra (LeoB)**; inspiration: **TheDeadHeroAlistair** and Pokémon Omega Ruby / Alpha Sapphire. Implementation built on **resetes12's Modern Emerald**. | **Oldale, Rustboro, Fortree, Mossdeep, Routes 101, 103, 110, 115, 119**. Compatible metatile variants preserve Plastic Ox's map geometry and behavior attributes. |
| [Team Aqua's Asset Repo](https://github.com/TeamAquasHideout/Team-Aquas-Asset-Repo/tree/d1b3b396175548f93128ca2e88f32e3188c8e453), `Tilesets/The Great Tileset Exchange/Full Tilesets/LeoB ORAS` | Same LeoB credit chain; the included creator statement and repository policy allow credited reuse in ROM hacks. [Original credit statement](plastic_ox/assets/upstream/leob_oras_credits.md). | The nine Hoenn maps above; used to verify the asset set's attribution and reuse permission. |
| [PokemonHnS-Development/pokehns-expansion](https://github.com/PokemonHnS-Development/pokehns-expansion/tree/44f50eedefe58691b0444973e4138e9190d8fafc): existing H&S Johto/Kanto map-and-tileset pairs, restored outdoor and National Park animations | **Pokémon Heart and Soul** and its [full credit chain](https://pokemonhns-development.github.io/pokehns-expansion-documentation/credits.html). Tileset credits include **Crystal Advance / Kertra, Ekat99, TheDeadHeroAlistair, Johto Redrawn Team, zatavares852, lbsbezerra, WesleyFG, Kalarie**. Map credits include **Crystal Advance / Kertra, Fire Gold / blackfragrant, SkidMarc25**. These are project-level credits; individual tileset authors are not assigned where upstream does not specify them. | Johto: **Cherrygrove, Goldenrod, Ecruteak, Blackthorn, Ilex, National Park, Dark Cave, Routes 29–31, 33–38, 44–46**, and their H&S interiors. Kanto: **Saffron, Lavender, Cinnabar, Indigo Plateau, Mt. Moon, H&S Routes 2–7, 12, 14, 16, 21, 24–25**, and their H&S interiors. Exact registered maps and pairs: [inventory](plastic_ox/assets/map_visual_families.csv). |
| Existing Emerald / FRLG asset implementations through **pret**, **RHH / pokeemerald-expansion**, and the H&S import pipeline | **Game Freak / Nintendo / The Pokémon Company**, pret contributors, RHH contributors; existing [CREDITS.md](CREDITS.md) and [docs/CREDITS.md](docs/CREDITS.md) remain applicable. | Compatible FRLG fallbacks including **Pallet, Route 2, Route 8, Route 19, split Route 20, Seafoam, Underground Path**; retained Hoenn caves/interiors including **Meteor Falls, Victory Road, Mt. Pyre-derived tower rooms, Rustboro-derived Gym rooms, Space Center-derived Silph, Devon-derived Mansion, League rooms, Harbor, Battle Frontier**. |

The H&S README explicitly invites downstream hacks with attribution. Neither
H&S nor the LeoB package provides a blanket SPDX art license; their stated
reuse conditions and original credit chains are retained here.

[jschoeny/TARC2](https://github.com/jschoeny/TARC2/tree/0da79a2d) and its
**Morlock-Liam Gen 2 Kanto Assets** were evaluated, not imported. Their
`olden_times` implementation accompanies different custom maps. Retiling the
existing Kanto maps around it would discard their compatible source pairing;
its broader repository also supplies no clear asset-wide license. Existing
H&S Kanto architecture is retained, with its source animations restored.

See [migration and validation notes](plastic_ox/assets/README.md) and the
[Hoenn](plastic_ox/assets/hoenn_provenance.md),
[Johto](plastic_ox/assets/johto_provenance.md), and
[Kanto](plastic_ox/assets/kanto_provenance.md) source records.
