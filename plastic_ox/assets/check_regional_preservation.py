#!/usr/bin/env python3
"""Prove the regional graphics pass preserves its pre-upgrade gameplay data."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = "ff445c76c51b51a58fe5768fb77745bba32bf4a7"


def original(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def main():
    protected = ["data/maps", "data/scripts", "data/wild_encounters.json",
                 "data/layouts", "include/constants/metatile_behaviors.h"]
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", BASE, "--", *protected], cwd=ROOT, text=True
    ).splitlines()
    assert set(changed) <= {"data/layouts/layouts.json"}, changed
    before = json.loads(original("data/layouts/layouts.json"))
    after = json.loads((ROOT / "data/layouts/layouts.json").read_text())
    assert len(before["layouts"]) == len(after["layouts"])
    headers = (ROOT / "src/data/tilesets/headers.h").read_text()
    metatiles = (ROOT / "src/data/tilesets/metatiles.h").read_text()
    for name in ["hoenn_oras_headers.h", "hoenn_oras_metatiles.h"]:
        path = ROOT / "src/data/tilesets" / name
        if path.exists():
            if name.endswith("headers.h"):
                headers += path.read_text()
            else:
                metatiles += path.read_text()
    symbols = dict(re.findall(
        r"const struct Tileset (gTileset_\w+)\s*=\s*\{.*?\.metatileAttributes\s*=\s*(gMetatileAttributes_\w+)",
        headers, re.S))
    paths = dict(re.findall(
        r'const u\d+ (gMetatileAttributes_\w+)\[\] = INCBIN_U\d+\("([^"]+)"\)', metatiles))
    migrated = []
    for old, new in zip(before["layouts"], after["layouts"]):
        assert old["id"] == new["id"]
        for field in ["primary_tileset", "secondary_tileset"]:
            if old[field] != new[field]:
                a, b = paths[symbols[old[field]]], paths[symbols[new[field]]]
                assert original(a) == (ROOT / b).read_bytes(), (new["name"], "behavior changed")
        if old != new:
            migrated.append(new["name"])
        assert {k: v for k, v in old.items() if not k.endswith("_tileset")} == {
            k: v for k, v in new.items() if not k.endswith("_tileset")}, new["name"]
    # Retained tilesets must preserve every existing behavior, including the
    # previous HNS enum conversions and custom cave-exit metatiles.
    attrs = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", BASE, "data/tilesets"], cwd=ROOT, text=True
    ).splitlines()
    for path in attrs:
        if path.endswith("/metatile_attributes.bin"):
            assert original(path) == (ROOT / path).read_bytes(), path
    print(f"PASS: {len(after['layouts'])} layouts retain geometry; {len(migrated)} change only tileset pairs")
    print("PASS: map events, connections, warps, scripts, encounters and all existing behavior attributes unchanged")
    print("Migrated:", ", ".join(migrated))


if __name__ == "__main__":
    main()
