#!/usr/bin/env python3
"""Import complete SoulGold Johto layouts while retaining Plastic Ox logic.

The generated assets are intentionally namespaced.  Blockmaps, borders,
tiles, palettes, metatiles, and attributes always come from the same donor.
"""
import argparse
import copy
import json
from pathlib import Path
import re
import shutil
import struct

ROOT = Path(__file__).resolve().parents[2]
DONOR_REVISION = "768612c8ebcecf69c0083e918039e083ca1a5ba4"

MAPS = {}


def load(path):
    return json.loads(path.read_text())


def symbol_path(symbol):
    words = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", symbol.removeprefix("gTileset_")).lower()
    return words


def project_events(events, old_w, old_h, new_w, new_h):
    result = copy.deepcopy(events)
    for event in result:
        if "x" in event:
            event["x"] = min(new_w - 1, max(0, round(event["x"] * (new_w - 1) / max(1, old_w - 1))))
        if "y" in event:
            event["y"] = min(new_h - 1, max(0, round(event["y"] * (new_h - 1) / max(1, old_h - 1))))
    return result


def tileset_definition(symbol, primary, asset_dir, callback, palette_count):
    suffix = symbol.removeprefix("gTileset_") + "_SoulGold"
    pal_lines = "\n".join(
        f'    INCGFX_U16("{asset_dir}/palettes/{i:02d}.pal", ".gbapal"),' for i in range(palette_count)
    )
    return f'''const u32 gTilesetTiles_{suffix}[] = INCGFX_U32("{asset_dir}/tiles.png", ".4bpp.fastSmol");
const u16 gTilesetPalettes_{suffix}[][16] = {{
{pal_lines}
}};
const u16 gMetatiles_{suffix}[] = INCBIN_U16("{asset_dir}/metatiles.bin");
const u16 gMetatileAttributes_{suffix}[] = INCBIN_U16("{asset_dir}/metatile_attributes.bin");
const struct Tileset gTileset_{suffix} = {{
    .isCompressed = TRUE,
    .isSecondary = {"FALSE" if primary else "TRUE"},
    .tiles = gTilesetTiles_{suffix},
    .palettes = gTilesetPalettes_{suffix},
    .metatiles = gMetatiles_{suffix},
    .metatileAttributes = gMetatileAttributes_{suffix},
    .callback = {callback},
}};
''', suffix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--donor", type=Path, required=True)
    args = parser.parse_args()
    donor = args.donor.resolve()
    import subprocess
    revision = subprocess.check_output(["git", "-C", donor, "rev-parse", "HEAD"], text=True).strip()
    if revision != DONOR_REVISION:
        parser.error(f"expected SoulGold {DONOR_REVISION}, got {revision}")

    ours = load(ROOT / "data/layouts/layouts.json")
    ours["layouts"] = [x for x in ours["layouts"] if not x["id"].endswith("_SOULGOLD")]
    for parent in (ROOT / "data/layouts", ROOT / "data/tilesets/primary", ROOT / "data/tilesets/secondary"):
        for stale in parent.glob("*_soulgold"):
            shutil.rmtree(stale)
    donor_layouts = {x["id"]: x for x in load(donor / "data/layouts/layouts.json")["layouts"]}
    ours_by_id = {x["id"]: x for x in ours["layouts"]}
    donor_headers = (donor / "src/data/tilesets/headers.h").read_text()
    definitions, declarations, registered = [], [], {}

    if not MAPS:
        (ROOT / "data/layouts/layouts.json").write_text(json.dumps(ours, indent=2) + "\n")
        generated = ROOT / "src/data/tilesets/soulgold_johto.h"
        if generated.exists():
            generated.unlink()
        print("SoulGold runtime import disabled: donor requires a 1024-primary-metatile engine")
        return

    for target, source in MAPS.items():
        target_map_path = ROOT / "data/maps" / target / "map.json"
        target_map = load(target_map_path)
        source_map = load(donor / "data/maps" / source / "map.json")
        old_layout = ours_by_id[target_map["layout"]]
        source_layout = donor_layouts[source_map["layout"]]

        for field, primary in (("primary_tileset", True), ("secondary_tileset", False)):
            symbol = source_layout[field]
            if symbol not in registered:
                stem = symbol_path(symbol)
                donor_dir = donor / "data/tilesets" / ("primary" if primary else "secondary") / stem
                if not donor_dir.is_dir():
                    raise SystemExit(f"cannot resolve {symbol}: {donor_dir}")
                dest_rel = Path("data/tilesets") / ("primary" if primary else "secondary") / f"{stem}_soulgold"
                dest = ROOT / dest_rel
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(donor_dir, dest)
                match = re.search(rf"const struct Tileset {symbol}\s*=\s*\{{(.*?)\n\}};", donor_headers, re.S)
                callback = "NULL"
                if match:
                    cb = re.search(r"\.callback\s*=\s*([^,]+)", match.group(1))
                    if cb and cb.group(1).strip() == "InitTilesetAnim_General":
                        callback = "InitTilesetAnim_General"
                palette_count = len(list((dest / "palettes").glob("[0-9][0-9].pal")))
                definition, suffix = tileset_definition(symbol, primary, dest_rel.as_posix(), callback, palette_count)
                definitions.append(definition)
                declarations.append(f"extern const struct Tileset gTileset_{suffix};")
                registered[symbol] = f"gTileset_{suffix}"

        new_id = old_layout["id"].removesuffix("_HNS") + "_SOULGOLD"
        dest_layout = ROOT / "data/layouts" / f"{source}_soulgold"
        dest_layout.mkdir(parents=True, exist_ok=True)
        shutil.copy2(donor / source_layout["border_filepath"], dest_layout / "border.bin")
        shutil.copy2(donor / source_layout["blockdata_filepath"], dest_layout / "map.bin")
        # SoulGold relies on source-side cave arrival movement at these mouths.
        # Plastic Ox lands directly, so retain the art but open the landing cells.
        if source == "DarkCave_SouthSide":
            raw = bytearray((dest_layout / "map.bin").read_bytes())
            for x, y in ((14, 20), (14, 21), (56, 46), (56, 47)):
                offset = 2 * (y * source_layout["width"] + x)
                word = struct.unpack_from("<H", raw, offset)[0] & ~0x0C00
                struct.pack_into("<H", raw, offset, word)
            # Metatile 511 is unused by the imported active maps. Duplicate
            # the donor entrance art there with Plastic Ox's ladder behavior,
            # avoiding a global behavior change to ordinary donor tile 7.
            general = ROOT / "data/tilesets/primary/johto_general_soulgold"
            metatiles = bytearray((general / "metatiles.bin").read_bytes())
            attrs = bytearray((general / "metatile_attributes.bin").read_bytes())
            metatiles[511 * 16:512 * 16] = metatiles[7 * 16:8 * 16]
            ladder = next(i for i, line in enumerate(
                x for x in (ROOT / "include/constants/metatile_behaviors.h").read_text().splitlines()
                if re.match(r"\s*MB_\w+\s*,", x)
            ) if "MB_LADDER" in line)
            old_attr = struct.unpack_from("<H", attrs, 7 * 2)[0]
            struct.pack_into("<H", attrs, 511 * 2, (old_attr & 0xFF00) | ladder)
            (general / "metatiles.bin").write_bytes(metatiles)
            (general / "metatile_attributes.bin").write_bytes(attrs)
            for x, y in ((14, 20), (56, 46)):
                offset = 2 * (y * source_layout["width"] + x)
                word = struct.unpack_from("<H", raw, offset)[0]
                struct.pack_into("<H", raw, offset, (word & ~0x03FF) | 511)
            (dest_layout / "map.bin").write_bytes(raw)
        new_layout = {
            "id": new_id,
            "name": f"{source}_SoulGold_Layout",
            "width": source_layout["width"], "height": source_layout["height"],
            "primary_tileset": registered[source_layout["primary_tileset"]],
            "secondary_tileset": registered[source_layout["secondary_tileset"]],
            "border_filepath": f"data/layouts/{source}_soulgold/border.bin",
            "blockdata_filepath": f"data/layouts/{source}_soulgold/map.bin",
            "include_in_versions": ["emerald"],
        }
        ours["layouts"] = [x for x in ours["layouts"] if x["id"] != new_id]
        ours["layouts"].append(new_layout)

        old_w, old_h = old_layout["width"], old_layout["height"]
        new_w, new_h = source_layout["width"], source_layout["height"]
        for key in ("object_events", "coord_events", "bg_events"):
            target_map[key] = project_events(target_map.get(key, []), old_w, old_h, new_w, new_h)
        old_warps = copy.deepcopy(target_map.get("warp_events", []))
        donor_warps = source_map.get("warp_events", [])
        if len(donor_warps) < len(old_warps):
            raise SystemExit(f"{source} has fewer warps ({len(donor_warps)}) than {target} ({len(old_warps)})")
        donor_warp_indices = [0, 2] if source == "DarkCave_SouthSide" else range(len(old_warps))
        for index, warp in enumerate(old_warps):
            for key in ("x", "y", "elevation"):
                warp[key] = donor_warps[donor_warp_indices[index]][key]
            if source == "DarkCave_SouthSide" and index == 1:
                warp["y"] = 46
        target_map["warp_events"] = old_warps
        donor_by_direction = {x["direction"]: x for x in (source_map.get("connections") or [])}
        for connection in (target_map.get("connections") or []):
            if connection["direction"] in donor_by_direction:
                connection["offset"] = donor_by_direction[connection["direction"]]["offset"]
        target_map["layout"] = new_id
        target_map_path.write_text(json.dumps(target_map, indent=2) + "\n")

    (ROOT / "data/layouts/layouts.json").write_text(json.dumps(ours, indent=2) + "\n")
    generated = ROOT / "src/data/tilesets/soulgold_johto.h"
    generated.write_text("/* Generated by plastic_ox/assets/import_soulgold_johto.py. */\n\n" + "\n".join(definitions))
    headers = ROOT / "src/data/tilesets/headers.h"
    text = headers.read_text()
    marker = '#include "soulgold_johto.h"'
    if marker not in text:
        headers.write_text(text + "\n" + marker + "\n")
    include = ROOT / "include/tilesets.h"
    text = include.read_text()
    block = "\n".join(declarations) + "\n"
    if declarations[0] not in text:
        include.write_text(text.replace("#endif //GUARD_tilesets_H", block + "\n#endif //GUARD_tilesets_H"))
    print(f"Imported {len(MAPS)} Johto maps and {len(registered)} SoulGold tilesets from {revision}")


if __name__ == "__main__":
    main()
