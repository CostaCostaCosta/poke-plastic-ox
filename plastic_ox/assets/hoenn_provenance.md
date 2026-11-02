# Hoenn ORAS-style tileset provenance

## Imported implementation

The `hoenn_oras_*` tileset variants are a collision-preserving technical
adaptation of the Hoenn tileset implementation from
[`lbsbezerra/pokeemerald-modern-oras`](https://github.com/lbsbezerra/pokeemerald-modern-oras),
revision `d271db57c21ac71cd009ecbfdb0562008674382c` (2026-06-28).
That project describes these as its ORAS-style tilesets.  It supplies the
primary `general` set and the Petalburg, Rustboro, Dewford, Slateport,
Mauville, Fallarbor, Lavaridge, Fortree, Lilycove, Mossdeep, Sootopolis, and
Ever Grande secondary sets, including their palettes and animation frames.

The artwork's upstream public asset package is
[`TeamAquasHideout/Team-Aquas-Asset-Repo`](https://github.com/TeamAquasHideout/Team-Aquas-Asset-Repo),
revision `d1b3b396175548f93128ca2e88f32e3188c8e453` (2026-08-09), under
`Tilesets/The Great Tileset Exchange/Full Tilesets/LeoB ORAS`.
`credits.md` identifies **leob0505** as the main creator and credits
**TheDeadHeroAlistair** as inspiration, alongside Pokémon Omega Ruby/Alpha
Sapphire.  The package explicitly invites use in ROM hacks and asks users to
include the creator credit; Team Aqua's repository policy accepts assets only
when they are free to use with their original creator credited.  Plastic Ox
therefore retains this attribution.

No original pixel art was created for this import.  The ORAS donor and Team
Aqua package do not declare an SPDX license; their included reuse/credit
statements are the permission evidence recorded here.

## Plastic Ox adaptation

`import_leob_oras_tilesets.py` copies the donor graphics, palettes and
animation frames into dedicated Hoenn variant directories.  It derives donor
metatile graphics records from matching donor/current map cells, writes those
records at the current metatile IDs, and copies the existing Plastic Ox
metatile attributes unchanged.  It does not write map blockdata, borders,
events, scripts, encounters, warps, or connections.  The generated
`hoenn_oras_mapping_report.json` records the coverage used by the adaptation.

The variants are intended for maps whose existing layout pairs
`gTileset_General` with the corresponding Hoenn secondary family:

| Variant secondary family | Existing maps using the source family |
| --- | --- |
| Petalburg | Petalburg, Littleroot, Oldale, Routes 101–103 |
| Rustboro | Rustboro, Routes 104/116, Petalburg Woods, Southern Island, Faraway Island entrance |
| Dewford | Dewford, Routes 105–107, Birth Island, Navel Rock exterior |
| Slateport | Slateport, Routes 108–109 |
| Mauville | Mauville, Verdanturf, Routes 110/111/117/118 |
| Fallarbor | Fallarbor, Routes 113–115, Fossil Maniac's Tunnel |
| Lavaridge | Lavaridge, Route 112, Mt. Chimney, Jagged Pass, Fiery Path, Magma Hideout floors |
| Fortree | Fortree, Routes 119–120, Faraway Island interior |
| Lilycove | Lilycove, Routes 121–123, Safari Zone sectors |
| Mossdeep | Mossdeep, Routes 124–129 |
| Sootopolis | Sootopolis and Legends Battle |
| Ever Grande | Ever Grande City |

Meteor Falls remains on its native Hoenn `meteor_falls` secondary family.  It
is deliberately not assigned a Kanto or Johto tileset: its source geometry
and cave identity remain Hoenn, including the approach to Blackthorn.

## September 2026 validation

The importer now resolves every observed multi-candidate correspondence
deterministically: greatest positional support wins, then identity mapping,
then the lowest donor ID. It also installs an identity donor fallback for any
metatile used by an active ORAS layout that has no positional observation.
The report keeps all 76 observed multi-candidate records for review while
reporting zero unresolved ambiguities and zero unmapped active records.

Coverage is complete for every metatile actually used by active converted
Hoenn layouts: primary 414/414, Petalburg 99/99, Rustboro 269/269, Mauville
400/400, Fallarbor 263/263, Fortree 229/229, Mossdeep 324/324, Frontier West
423/423, and Frontier East 405/405. A fresh 280-view mGBA grid inspection over
33 maps passed with zero camera-buffer mismatches, including 43 Route 119
views, 7 Fortree views, 29 Mossdeep views, and 19 Rustboro views. Shorelines,
waterfalls, Fortree structures, Rustboro architecture/fountain behavior, and
the existing ORAS animation callbacks remain intact. Meteor Falls remains
native Hoenn at its intentional cross-region exit.

| Plastic Ox map | Region | Donor map | Donor project | Tileset family | Status |
| --- | --- | --- | --- | --- | --- |
| RustboroCity | Hoenn | RustboroCity | Modern ORAS Emerald | LeoB ORAS General / Rustboro | validated |
| Route119 | Hoenn | Route119 | Modern ORAS Emerald | LeoB ORAS General / Fortree | validated |
| FortreeCity | Hoenn | FortreeCity | Modern ORAS Emerald | LeoB ORAS General / Fortree | validated |
| MossdeepCity | Hoenn | MossdeepCity | Modern ORAS Emerald | LeoB ORAS General / Mossdeep | validated |
| MeteorFalls_1F_1R | Hoenn | MeteorFalls_1F_1R | pokeemerald + LeoB direction | Hoenn General / Meteor Falls | retained Hoenn; validated |
