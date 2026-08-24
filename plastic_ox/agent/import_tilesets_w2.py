#!/usr/bin/env python3
"""Import 4 missing _hns secondary tilesets (wave 2). Run from repo root."""
import json, os, shutil, sys

HNS = "/home/eddie/repos/pokehns-expansion"
TILESETS = [  # (dir, CName, npals)
    ("gate_standard_hns", "Gate_Standard_Hns", 13),
    ("viridian_city_hns", "ViridianCity_Hns", None),
    ("pewter_city_hns", "PewterCity_Hns", 16),
    ("fuchsia_hns", "Fuchsia_Hns", 17),
]

def main():
    dry = "--dry" in sys.argv
    def w(path, s):
        if dry: print("WOULD WRITE", path); return
        open(path, "a").write(s)

    for d, n, npals in TILESETS:
    if npals is None:
        npals = len(os.listdir(f"data/tilesets/secondary/{d}/palettes"))
        dst = f"data/tilesets/secondary/{d}"
        if not os.path.isdir(dst):
            shutil.copytree(f"{HNS}/data/tilesets/secondary/{d}", dst)
        # tilesets.h extern (alphabetical-ish: append after last Hns extern)
        s = open("include/tilesets.h").read()
        line = f"extern const struct Tileset gTileset_{n};"
        if line not in s:
            anchor = "extern const struct Tileset gTileset_World;"
            if anchor in s:
                s = s.replace(anchor, line + "\n" + anchor)
            else:
                i = s.rindex("extern const struct Tileset")
                j = s.index("\n", i) + 1
                s = s[:j] + line + "\n" + s[j:]
            open("include/tilesets.h", "w").write(s)
        # headers.h definition
        h = open("src/data/tilesets/headers.h").read()
        if f"gTileset_{n} =" not in h:
            block = (
                f"\nconst struct Tileset gTileset_{n} =\n{{\n"
                f"    .tiles = gTilesetTiles_{n},\n"
                f"    .palettes = gTilesetPalettes_{n},\n"
                f"    .metatiles = gMetatiles_{n},\n"
                f"    .metatileAttributes = gMetatileAttributes_{n},\n"
                f"}};\n"
            )
            h = h.rstrip() + "\n" + block
            open("src/data/tilesets/headers.h", "w").write(h)
        # graphics.h
        g = open("src/data/tilesets/graphics.h").read()
        if f"gTilesetTiles_{n}" not in g:
            pal = "\n".join(
                f'    INCGFX_U16("data/tilesets/secondary/{d}/palettes/{i:02d}.pal", ".gbapal"),'
                for i in range(npals))
            block = (
                f'\nconst u32 gTilesetTiles_{n}[] = INCGFX_U32("data/tilesets/secondary/{d}/tiles.png", ".4bpp.fastSmol");\n\n'
                f"const u16 gTilesetPalettes_{n}[][16] =\n{{\n{pal}\n}};\n"
            )
            g = g.rstrip() + "\n" + block
            open("src/data/tilesets/graphics.h", "w").write(g)
        # metatiles.h
        mt = open("src/data/tilesets/metatiles.h").read()
        if f"gMetatiles_{n}" not in mt:
            block = (
                f'\nconst u16 gMetatiles_{n}[] = INCBIN_U16("data/tilesets/secondary/{d}/metatiles.bin");\n'
                f'const u16 gMetatileAttributes_{n}[] = INCBIN_U16("data/tilesets/secondary/{d}/metatile_attributes.bin");\n'
            )
            mt = mt.rstrip() + "\n" + block
            open("src/data/tilesets/metatiles.h", "w").write(mt)
        print("tileset done:", n)

if __name__ == "__main__":
    main()
