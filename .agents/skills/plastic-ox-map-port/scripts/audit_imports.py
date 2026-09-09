#!/usr/bin/env python3
"""Audit Plastic-Ox HNS layout metadata and tileset partition bounds."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path


def png_tiles(path: Path) -> int:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError(f"not a PNG: {path}")
    width, height = struct.unpack(">II", data[16:24])
    if width % 8 or height % 8:
        raise ValueError(f"tiles image is not 8px-aligned: {path}")
    return width * height // 64


def symbol_paths(text: str, declaration: str) -> dict[str, str]:
    pattern = rf"const u(?:16|32)\s+({declaration})\[.*?\]\s*=\s*INC(?:BIN|GFX)_U(?:16|32)\(\"([^\"]+)\""
    return dict(re.findall(pattern, text, re.S))


def tileset_headers(text: str) -> dict[str, dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for symbol, body in re.findall(
        r"const struct Tileset\s+(gTileset_\w+)\s*=\s*\{(.*?)\n\};", text, re.S
    ):
        values = {}
        for field in ("isCompressed", "isSecondary"):
            match = re.search(rf"\.{field}\s*=\s*(TRUE|FALSE)", body)
            values[field] = match.group(1) if match else "FALSE"
        for field in ("tiles", "palettes", "metatiles", "metatileAttributes"):
            match = re.search(rf"\.{field}\s*=\s*(g\w+)", body)
            if match:
                values[field] = match.group(1)
        found[symbol] = values
    return found


def palette_counts(text: str) -> dict[str, int]:
    counts = {}
    for symbol, body in re.findall(
        r"const u16\s+(gTilesetPalettes_\w+)\[\]\[16\]\s*=\s*\{(.*?)\n\};",
        text,
        re.S,
    ):
        counts[symbol] = body.count("INCGFX_U16(")
    return counts


def read_blocks(path: Path) -> list[int]:
    data = path.read_bytes()
    if len(data) % 2:
        raise ValueError(f"odd-length block binary: {path}")
    return list(struct.unpack(f"<{len(data) // 2}H", data))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", nargs="?", default=".")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()

    layouts = json.loads((repo / "data/layouts/layouts.json").read_text())["layouts"]
    headers_text = (repo / "src/data/tilesets/headers.h").read_text()
    graphics_text = (repo / "src/data/tilesets/graphics.h").read_text()
    metatiles_text = (repo / "src/data/tilesets/metatiles.h").read_text()
    headers = tileset_headers(headers_text)
    tile_paths = symbol_paths(graphics_text, r"gTilesetTiles_\w+")
    metatile_paths = symbol_paths(metatiles_text, r"gMetatiles_\w+")
    attribute_paths = symbol_paths(metatiles_text, r"gMetatileAttributes_\w+")
    palettes = palette_counts(graphics_text)

    errors: list[str] = []
    checked = 0
    for layout in layouts:
        is_hns = layout.get("layout_version") == "hns" or layout.get("name", "").endswith("_hns_Layout")
        if not is_hns:
            continue
        checked += 1
        label = layout.get("id", layout.get("name", "<unknown>"))
        if layout.get("layout_version") != "hns":
            errors.append(f"{label}: missing layout_version=hns")
        if "emerald" not in layout.get("include_in_versions", []):
            errors.append(f"{label}: missing include_in_versions emerald")

        map_path = repo / layout["blockdata_filepath"]
        border_path = repo / layout["border_filepath"]
        expected = layout["width"] * layout["height"] * 2
        if not map_path.is_file() or map_path.stat().st_size != expected:
            actual = map_path.stat().st_size if map_path.is_file() else "missing"
            errors.append(f"{label}: map.bin size {actual}, expected {expected}")
            continue
        if not border_path.is_file() or border_path.stat().st_size != 8:
            actual = border_path.stat().st_size if border_path.is_file() else "missing"
            errors.append(f"{label}: HNS border size {actual}, expected 8")
            continue

        block_ids = [value & 0x3FF for value in read_blocks(map_path) + read_blocks(border_path)]
        for role, tileset_symbol, start, capacity, min_pals in (
            ("primary", layout["primary_tileset"], 0, 640, 7),
            # Secondary palette arrays retain global HNS slots; the engine
            # copies slots 7..12 into destination slots 7..12.
            ("secondary", layout["secondary_tileset"], 640, 384, 13),
        ):
            header = headers.get(tileset_symbol)
            if not header:
                errors.append(f"{label}: unknown {role} tileset {tileset_symbol}")
                continue
            used = [value - start for value in block_ids if start <= value < start + capacity]
            if header["isCompressed"] != "TRUE":
                errors.append(f"{label}: {tileset_symbol} must decompress its fastSmol graphics")
            if header["isSecondary"] != ("TRUE" if role == "secondary" else "FALSE"):
                errors.append(f"{label}: {tileset_symbol} has wrong isSecondary palette offset")
            max_used = max(used, default=-1)

            tile_path = tile_paths.get(header.get("tiles", ""))
            meta_path = metatile_paths.get(header.get("metatiles", ""))
            attr_path = attribute_paths.get(header.get("metatileAttributes", ""))
            if not tile_path or not meta_path or not attr_path:
                errors.append(f"{label}: incomplete {role} asset registration for {tileset_symbol}")
                continue
            tile_count = png_tiles(repo / tile_path)
            meta_count = (repo / meta_path).stat().st_size // 16
            attr_count = (repo / attr_path).stat().st_size // 2
            pal_count = palettes.get(header.get("palettes", ""), 0)
            if max_used >= meta_count:
                errors.append(f"{label}: {role} metatile {max_used} exceeds {meta_count} definitions")
            if max_used >= attr_count:
                errors.append(f"{label}: {role} attribute {max_used} exceeds {attr_count} definitions")
            if pal_count < min_pals:
                errors.append(f"{label}: {role} has {pal_count} palettes, needs {min_pals}")
            if max_used < meta_count:
                metatile_words = read_blocks(repo / meta_path)
                referenced_tiles = []
                for metatile in used:
                    for word in metatile_words[metatile * 8 : metatile * 8 + 8]:
                        tile_id = word & 0x3FF
                        if start <= tile_id < start + capacity:
                            referenced_tiles.append(tile_id - start)
                max_tile = max(referenced_tiles, default=-1)
                if max_tile >= tile_count:
                    errors.append(
                        f"{label}: {role} tile {max_tile} exceeds {tile_count} graphics tiles"
                    )

    print(f"audited {checked} HNS layouts")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("HNS layout metadata and asset bounds: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
