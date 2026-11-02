#!/usr/bin/env python3
"""Static pass-5 helper: read live metatile behaviour/collision for map warps.

Run 5 of the Plastic-Ox playtesters reported warp/seam defects.  This helper
turns the emulator's live readings back into plain map-data facts so a fix can
be chosen before rebuilding:

* for every warp event of a map: the source metatile behaviour (which decides
  whether the engine's TryArrowWarp / TryDoorWarp / TryStartWarpEventScript can
  ever fire), and the reciprocal destination warp;
* for every connection: the walkable lane columns on both sides of the seam.

Everything is read from data/maps/*/map.json, data/layouts/layouts.json,
data/layouts/*/map.bin and data/tilesets/*/*/metatile_attributes.bin, i.e. the
same inputs the build itself consumes.
"""
from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DIRECTIONS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

# Behaviours that make the engine perform a warp when the player steps onto the
# tile (TryStartStepBasedScript -> TryStartWarpEventScript, src/field_control_avatar.c).
STEP_WARP = [
    "MB_ANIMATED_DOOR", "MB_NON_ANIMATED_DOOR", "MB_WATER_DOOR", "MB_LADDER",
    "MB_ESCALATOR", "MB_MOSSDEEP_GYM_WARP", "MB_UNION_ROOM_WARP",
    "MB_LAVARIDGE_GYM_1F_WARP", "MB_LAVARIDGE_GYM_B1F_WARP",
    "MB_AQUA_HIDEOUT_WARP", "MB_MT_PYRE_HOLD1_WARP",
]
# Behaviours that make the engine warp while the player *holds* a direction.
HELD_WARP = [
    "MB_NORTH_ARROW_WARP", "MB_SOUTH_ARROW_WARP", "MB_EAST_ARROW_WARP",
    "MB_WEST_ARROW_WARP", "MB_DEEP_SOUTH_WARP", "MB_CAVE_EXIT",
    "MB_STAIRS_UP_LEFT", "MB_STAIRS_UP_RIGHT", "MB_STAIRS_DOWN_LEFT",
    "MB_STAIRS_DOWN_RIGHT",
]


def behavior_values():
    values, cur = {}, 0
    for line in (ROOT / "include/constants/metatile_behaviors.h").read_text().splitlines():
        m = re.match(r"\s*(MB_\w+)\s*(?:=\s*(0x[0-9a-fA-F]+|\d+))?\s*,", line)
        if m:
            cur = int(m[2], 0) if m[2] else cur
            values[m[1]] = cur
            cur += 1
    return values


BEH = behavior_values()
BEH_NAME = {v: k for k, v in BEH.items()}
WARPISH = {BEH[n] for n in STEP_WARP + HELD_WARP if n in BEH}
ARROW = {BEH[n]: d for n, d in zip(
    ("MB_NORTH_ARROW_WARP", "MB_SOUTH_ARROW_WARP", "MB_EAST_ARROW_WARP", "MB_WEST_ARROW_WARP"),
    ("up", "down", "right", "left")) if n in BEH}
# Directional stairs (src/field_screen_effect.c IsDirectionalStairWarpMetatileBehavior).
STAIRS = {}
for _name in ("MB_UP_LEFT_STAIR_WARP", "MB_UP_RIGHT_STAIR_WARP",
              "MB_DOWN_LEFT_STAIR_WARP", "MB_DOWN_RIGHT_STAIR_WARP"):
    if _name not in BEH:
        continue
    # Only WEST/EAST can fire a stair warp; which of the two depends on the
    # left/right variant.
    STAIRS[BEH[_name]] = ["left"] if _name.endswith("LEFT_STAIR_WARP") else ["right"]
def trigger(behavior):
    """How the engine can possibly fire a warp on a tile with this behavior."""
    if behavior in ARROW:
        return "hold-" + ARROW[behavior]
    if behavior in STAIRS:
        return "hold-" + "/".join(sorted(set(STAIRS[behavior])))
    if behavior in WARPISH:
        return "step"
    return "NEVER-FIRES"


def _tileset_index():
    """Normalized tileset name -> {family: directory}.

    A tileset directory is either `name`, `name_frlg` or `name_hns`, and the
    same stem exists in more than one family (lavender_town_frlg and
    lavender_town_hns are different art), so the layout's `layout_version`
    decides which one a layout means.
    """
    index = {}
    for kind in ("secondary", "primary"):
        for d in sorted((ROOT / "data/tilesets" / kind).iterdir()):
            family = None
            stem = d.name
            for suffix in ("_frlg", "_hns"):
                if d.name.endswith(suffix):
                    family = suffix[1:]
                    stem = d.name[: -len(suffix)]
                    break
            index.setdefault(stem.replace("_", "").lower(), {})[family] = d
    return index


_TILESETS = _tileset_index()


def tileset_dir(cname, family="emerald"):
    base = cname[len("gTileset_"):]
    if base.endswith("_Hns"):
        base = base[:-4]
    if base.endswith("_Frlg"):
        base = base[:-4]
    if base.endswith("Frlg"):
        base = base[:-4]
    if base.endswith("Hns"):
        base = base[:-3]
    candidates = _TILESETS.get(base.replace("_", "").lower()) or {}
    if family in candidates:
        return candidates[family]
    return candidates.get(None) or next(iter(candidates.values()), None)


class MapGeom:
    """Lazily decoded blockmap + metatile attribute reader for one layout."""

    def __init__(self, layout, cache):
        self.layout = layout
        self.w = layout["width"]
        self.h = layout["height"]
        self.blocks = (ROOT / layout["blockdata_filepath"]).read_bytes()
        self.version = layout.get("layout_version", "emerald")
        self.cache = cache
        self.primary = tileset_dir(layout["primary_tileset"], self.version)
        self.secondary = tileset_dir(layout["secondary_tileset"], self.version)

    def _attrs(self, directory, count):
        if directory is None:
            return b""
        key = (str(directory), count)
        if key not in self.cache:
            path = directory / "metatile_attributes.bin"
            self.cache[key] = path.read_bytes() if path.exists() else b""
        return self.cache[key]

    def tile(self, x, y):
        if not (0 <= x < self.w and 0 <= y < self.h):
            return None
        off = 2 * (y * self.w + x)
        if off + 2 > len(self.blocks):
            return None
        block = struct.unpack_from("<H", self.blocks, off)[0]
        mt = block & 0x03FF
        collision = (block >> 10) & 3
        elevation = (block >> 12) & 0xF
        primary_count = 512 if self.version == "emerald" else 640
        directory, index = ((self.primary, mt) if mt < primary_count
                            else (self.secondary, mt - primary_count))
        raw = self._attrs(directory, index)
        width = 4 if self.version == "frlg" else 2
        if len(raw) >= (index + 1) * width:
            attr = struct.unpack_from("<I" if width == 4 else "<H", raw, index * width)[0]
            behavior = attr & (0x1FF if width == 4 else 0xFF)
        else:
            behavior = 0
        return {"metatile": mt, "collision": collision, "elevation": elevation,
                "behavior": behavior, "behavior_name": BEH_NAME.get(behavior, f"?{behavior}")}


def load_catalog():
    layouts = {l["id"]: l for l in json.loads((ROOT / "data/layouts/layouts.json").read_text())["layouts"]}
    maps, by_id = {}, {}
    for p in sorted((ROOT / "data/maps").glob("*/map.json")):
        d = json.loads(p.read_text())
        maps[p.parent.name] = d
        by_id[d["id"]] = p.parent.name
    return layouts, maps, by_id


def dump(name, x0, y0, x1, y1, layouts, maps):
    cache = {}
    lay = layouts[maps[name]["layout"]]
    g = MapGeom(lay, cache)
    print(f"\n--- {name} rows {y0}..{y1} cols {x0}..{x1} (C=collision, /=walkable)")
    print("    " + "".join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in range(y0, y1 + 1):
        row = ""
        for x in range(x0, x1 + 1):
            t = g.tile(x, y)
            row += "." if t is None else ("#" if t["collision"] else "/")
        print(f"{y:3d} {row}")


def main(argv):
    cache = {}
    layouts, maps, by_id = load_catalog()
    dumpit = [a for a in argv if a.startswith("dump:")]
    for spec in dumpit:
        name, box = spec[5:].split(":")
        x0, y0, x1, y1 = (int(v) for v in box.split(","))
        dump(name, x0, y0, x1, y1, layouts, maps)
    wanted = [a for a in argv if not a.startswith("-") and not a.startswith("dump:")]
    for name in wanted:
        data = maps.get(name)
        if data is None:
            print(f"!! unknown map {name}")
            continue
        lay = layouts.get(data["layout"])
        geom = MapGeom(lay, cache) if lay else None
        print(f"\n### {name}  layout={data['layout']} {lay['width']}x{lay['height']}"
              f" ({lay.get('layout_version','emerald')})" if lay else f"\n### {name} NO LAYOUT")
        for c in data.get("connections") or []:
            print(f"  conn -> {c['map']} {c['direction']} offset {c['offset']}")
        for i, w in enumerate(data.get("warp_events") or []):
            t = geom.tile(w["x"], w["y"]) if geom else None
            trig = trigger(t["behavior"]) if t else "?"
            line = (f"  warp[{i}] ({w['x']},{w['y']}) elev{w['elevation']} -> "
                    f"{w['dest_map']}#{w['dest_warp_id']}  tile={t['behavior_name'] if t else '?'}"
                    f" coll={t['collision'] if t else '?'} gridelev={t['elevation'] if t else '?'}"
                    f" [{trig}]")
            # ELEVATION_TRANSITION (0) in a warp event is a wildcard:
            # GetWarpEventAtPosition() accepts it on any elevation.
            if t and t["elevation"] != w["elevation"] and w["elevation"] != 0:
                line += " !!ELEV-MISMATCH-NO-WARP-FIRE"
            back = maps.get(by_id.get(w["dest_map"], ""))
            if back is not None:
                try:
                    bw = back["warp_events"][int(w["dest_warp_id"])]
                except (KeyError, IndexError, ValueError):
                    bw = None
                if bw is None:
                    line += f"  !! dest warp id {w['dest_warp_id']} missing"
                else:
                    line += f"  back=({bw['x']},{bw['y']}) -> {bw['dest_map']}"
                    if bw["dest_map"] != data["id"]:
                        line += " !!NOT-RECIPROCAL"
                    bgeom = None
                    if geom and lay:
                        blay = layouts.get(back["layout"])
                        bgeom = MapGeom(blay, cache) if blay else None
                    if bgeom:
                        bt = bgeom.tile(bw["x"], bw["y"])
                        line += (f" desttile={bt['behavior_name']} coll={bt['collision']}"
                                 + (" !!SOLID-LANDING" if bt["collision"] != 0
                                    and bt["behavior"] not in WARPISH else ""))
            print(line)


if __name__ == "__main__":
    main(sys.argv[1:])