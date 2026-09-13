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

