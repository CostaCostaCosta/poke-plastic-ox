#!/usr/bin/env python3
"""Ensure every gTileset_*_Hns referenced by data/layouts/layouts.json exists:
copies the dir from hns and appends extern/definition/graphics/metatiles blocks."""
import json, os, re, sys

HNS = "/home/eddie/repos/pokehns-expansion"
DRY = "--dry" in sys.argv

lay_ours = {l["id"]: l for l in json.load(open("data/layouts/layouts.json"))["layouts"]}.values()
need = set()
for l in lay_ours:
    for k in ("primary_tileset", "secondary_tileset"):
        t = l.get(k)
        if t and t.endswith("_Hns"):
            need.add(t)

def find_dir(cname):
    base = cname.replace("gTileset_", "")
    key = base.replace("_", "").lower()
    for repo_root, marker in ((".", False), (HNS, True)):
        for kind in ("primary", "secondary"):
            p = f"{repo_root}/data/tilesets/{kind}"
            if not os.path.isdir(p):
                continue
            for d in os.listdir(p):
                if d.replace("_", "").lower() == key:
                    return kind, d, os.path.join(repo_root, p, d)
    return None

def main():
    inc = open("include/tilesets.h").read()
    h = open("src/data/tilesets/headers.h").read()
    g = open("src/data/tilesets/graphics.h").read()
    mt = open("src/data/tilesets/metatiles.h").read()
    for cname in sorted(need):
        info = find_dir(cname)
        if info is None:
            print("!! source missing for", cname); continue
        kind, d, srcpath = info
        dst = f"data/tilesets/{kind}/{d}"
        ours_exists = os.path.isdir(dst)
        if not ours_exists and not DRY:
            shutil.copytree(srcpath, dst)
        name = cname.replace("gTileset_", "")
        paldir = f"{dst}/palettes"
        npals = len([f for f in os.listdir(paldir) if f.endswith(".pal")]) if os.path.isdir(paldir) else 0

        line = f"extern const struct Tileset {cname};"
        if line not in inc:
            anchor = "extern const struct Tileset gTileset_World;"
            if anchor in inc:
                inc = inc.replace(anchor, line + "\n" + anchor)
            else:
                i = inc.rindex("extern const struct Tileset"); j = inc.index("\n", i) + 1
                inc = inc[:j] + line + "\n" + inc[j:]

        if f"{cname} =" not in h:
            h += (f"\nconst struct Tileset {cname} =\n{{\n"
                  f"    .tiles = gTilesetTiles_{name},\n"
                  f"    .palettes = gTilesetPalettes_{name},\n"
                  f"    .metatiles = gMetatiles_{name},\n"
                  f"    .metatileAttributes = gMetatileAttributes_{name},\n}};\n")

        if f"gTilesetTiles_{name}" not in g:
            pal = "\n".join(
                f'    INCGFX_U16("data/tilesets/{kind}/{d}/palettes/{i:02d}.pal", ".gbapal"),'
                for i in range(npals))
            g += (f'\nconst u32 gTilesetTiles_{name}[] = INCGFX_U32("data/tilesets/{kind}/{d}/tiles.png", ".4bpp.fastSmol");\n\n'
                  f'const u16 gTilesetPalettes_{name}[][16] =\n{{\n{pal}\n}};\n')

        if f"gMetatiles_{name}" not in mt:
            mt += (f'\nconst u16 gMetatiles_{name}[] = INCBIN_U16("data/tilesets/{kind}/{d}/metatiles.bin");\n'
                   f'const u16 gMetatileAttributes_{name}[] = INCBIN_U16("data/tilesets/{kind}/{d}/metatile_attributes.bin");\n')
        print("tileset ready:", name, f"({npals} palettes)")
    if not DRY:
        open("include/tilesets.h", "w").write(inc)
        open("src/data/tilesets/headers.h", "w").write(h)
        open("src/data/tilesets/graphics.h", "w").write(g)
        open("src/data/tilesets/metatiles.h", "w").write(mt)

import shutil
main()
