#!/usr/bin/env python3
"""Give imported hns warp tiles a door/warp metatile behavior.

hns (expansion) triggers warps without a behavior gate; our pret engine
requires MB_ANIMATED_DOOR / MB_NON_ANIMATED_DOOR / cave-exit-style behaviors.
For every *_hns warp tile whose metatile behavior isn't already warp-ish,
rewrite that metatile's attribute entry (emerald u16 format) in place.
"""
import json, os, re, struct, sys

DRY = "--dry" in sys.argv
WARPISH = set()
for name in ("MB_ANIMATED_DOOR", "MB_NON_ANIMATED_DOOR", "MB_CAVE_EXIT",
             "MB_LADDER", "MB_ESCALATOR", "MB_WATER_DOOR",
             "MB_NORTH_ARROW_WARP", "MB_SOUTH_ARROW_WARP",
             "MB_EAST_ARROW_WARP", "MB_WEST_ARROW_WARP"):
    pass  # resolved after reading enum below

# parse behavior enum values from the header (handles explicit values too)
beh_vals = {}
cur = 0
for line in open("include/constants/metatile_behaviors.h"):
    m = re.match(r"\s*MB_([A-Z0-9_]+)\s*(?:=\s*(\d+))?\s*,", line)
    if m:
        cur = int(m.group(2)) if m.group(2) else cur
        beh_vals["MB_" + m.group(1)] = cur
        cur += 1
DOOR = beh_vals.get("MB_ANIMATED_DOOR")
NONANIM = beh_vals.get("MB_NON_ANIMATED_DOOR")
WARPISH = {DOOR, NONANIM,
           beh_vals.get("MB_CAVE_EXIT"), beh_vals.get("MB_LADDER"),
           beh_vals.get("MB_ESCALATOR"), beh_vals.get("MB_STAIRS_UP_LEFT"),
           beh_vals.get("MB_STAIRS_UP_RIGHT"),
           beh_vals.get("MB_NORTH_ARROW_WARP"),
           beh_vals.get("MB_SOUTH_ARROW_WARP"),
           beh_vals.get("MB_EAST_ARROW_WARP"),
           beh_vals.get("MB_WEST_ARROW_WARP")} - {None}
print("door behaviors:", sorted(hex(v) for v in WARPISH))

layouts = {l["id"]: l for l in json.load(open("data/layouts/layouts.json"))["layouts"]}

_DIR_INDEX = None
def _dir_index():
    global _DIR_INDEX
    if _DIR_INDEX is None:
        _DIR_INDEX = {}
        for kind in ("secondary", "primary"):
            for d in os.listdir(f"data/tilesets/{kind}"):
                key = d.replace("_", "").lower()
                if key.endswith("hns"):
                    key = key[:-3]
                _DIR_INDEX[key] = f"data/tilesets/{kind}/{d}"
                _DIR_INDEX[key + "hns"] = f"data/tilesets/{kind}/{d}"
    return _DIR_INDEX

def attrs_path(tileset_cname):
    m = re.match(r"gTileset_(.+)", tileset_cname)
    base = m.group(1)
    base = base[:-4] if base.endswith("_Hns") else base
    key = base.replace("_", "").lower()
    d = _dir_index().get(key)
    return f"{d}/metatile_attributes.bin" if d else None

def main():
    fixed = {}
    for mp in sorted(os.listdir("data/maps")):
        if not mp.endswith("_hns"):
            continue
        jf = f"data/maps/{mp}/map.json"
        if not os.path.isfile(jf):
            continue
        d = json.load(open(jf))
        lay = layouts.get(d["layout"])
        if not lay:
            continue
        W, H = lay["width"], lay["height"]
        bp = lay["blockdata_filepath"]
        blocks = open(bp, "rb").read()
        prim = lay["primary_tileset"]; sec = lay["secondary_tileset"]
        for wpe in d.get("warp_events", []):
            x, y = wpe["x"], wpe["y"]
            if not (0 <= x < W and 0 <= y < H):
                continue
            v = struct.unpack_from("<H", blocks, 2 * (y * W + x))[0]
            mt = v & 0x03FF
            assert lay.get("layout_version") != "frlg", "FRLG attributes require u32 conversion"
            primary_count = 640 if lay.get("layout_version") == "hns" else 512
            cname = prim if mt < primary_count else sec
            idx = mt if mt < primary_count else mt - primary_count
            ap = attrs_path(cname)
            if not ap:
                print("no attrs file for", cname); continue
            data = bytearray(open(ap, "rb").read())
            n = len(data) // 2
            if idx >= n:
                continue
            old = struct.unpack_from("<H", data, 2 * idx)[0]
            beh = old & 0xFF
            if beh in WARPISH:
                continue
            new = (old & ~0xFF) | DOOR  # animated door: required by IsWarpDoor
            data[2 * idx:2 * idx + 2] = struct.pack("<H", new)
            key = ap
            if key not in fixed:
                fixed[key] = bytearray(open(ap, "rb").read())
            fixed[key][2 * idx:2 * idx + 2] = struct.pack("<H", new)
            print(f"{mp}: ({x},{y}) mt{mt} [{cname} #{idx}] beh {hex(beh)} -> {hex(DOOR)}")
    for ap, data in fixed.items():
        if DRY:
            print("WOULD WRITE", ap); continue
        open(ap, "wb").write(bytes(data))
    print("done")

if __name__ == "__main__":
    main()
