#!/usr/bin/env python3
"""Static convention extras for the warp playtest.

Covers the three convention questions that are properties of the tile data
rather than of a single warp event:

* ledges (`MB_JUMP_*`) - one-way hop, must land on a walkable tile one row down,
  and must be impassable from below;
* stair/ladder behaviours with **no** warp event, which no warp-driven harness
  can reach (a bg-event ladder is a script, not a warp);
* "unexpected auto-teleports": coordinate events and registered map scripts, which
  the Plastic-Ox baseline forbids (see .agents/skills/plastic-ox-map-baseline).

    python3 plastic_ox/agent/warp_extras_static.py --json /tmp/ledges.json
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "plastic_ox/alpha"))
sys.path.insert(0, str(ROOT / "plastic_ox/demo"))

from region_geometry import Geometry  # noqa: E402
import test_warps_v1 as W  # noqa: E402

# The behaviour names the direction the player is thrown, so the hop vector is
# (approach -> ledge tile -> landing) and the ledge tile itself is the solid one.
LEDGE = {"MB_JUMP_SOUTH": (0, 1), "MB_JUMP_NORTH": (0, -1),
         "MB_JUMP_EAST": (1, 0), "MB_JUMP_WEST": (-1, 0)}
LADDERISH = ("MB_LADDER",)
STAIRISH = ("MB_UP_RIGHT_STAIR_WARP", "MB_UP_LEFT_STAIR_WARP",
            "MB_DOWN_RIGHT_STAIR_WARP", "MB_DOWN_LEFT_STAIR_WARP",
            "MB_SIDEWAYS_STAIRS", "MB_ROCK_STAIRS", "MB_UP_ESCALATOR",
            "MB_DOWN_ESCALATOR", "MB_STAIRS_OUTSIDE_ABANDONED_SHIP")
DOORISH = ("MB_ANIMATED_DOOR", "MB_NON_ANIMATED_DOOR", "MB_WATER_DOOR",
           "MB_PETALBURG_GYM_DOOR", "MB_DEEP_SOUTH_WARP")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    ap.add_argument("--only", action="append", default=[])
    args = ap.parse_args()

    catalog, by_id, reached = W.closure()
    names = sorted(n for n in reached
                   if not args.only or any(f in n for f in args.only))
    out = {"maps": names, "ledges": [], "orphan_ladders": [], "orphan_stairs": [],
           "auto_teleports": [], "door_shape": [], "warp_on_plain_tile": [],
           "counts": Counter()}
    for name in names:
        data = catalog[name]
        try:
            geom = Geometry(name, data)
        except Exception:
            geom = None

        # ---- auto teleports ------------------------------------------------
        for ev in data.get("coord_events") or []:
            script = str(ev.get("script", ""))
            out["auto_teleports"].append(
                {"map": name, "kind": "coord_event", "x": ev.get("x"), "y": ev.get("y"),
                 "variable": ev.get("variable"), "script": script,
                 "class": "authored region portal" if script.startswith("PoxRegion")
                 else "legacy vanilla trigger"})
        for ev in data.get("bg_events") or []:
            script = str(ev.get("script", ""))
            if "warp" in script.lower():
                out["auto_teleports"].append(
                    {"map": name, "kind": "bg_event", "x": ev.get("x"), "y": ev.get("y"),
                     "script": script})

        if geom is None:
            continue
        warp_tiles = {(w["x"], w["y"]) for w in data.get("warp_events", [])}

        for y in range(geom.h):
            for x in range(geom.w):
                try:
                    collision, elev, behavior = geom.tile(x, y)
                except Exception:
                    continue
                if behavior in LEDGE:
                    dx, dy = LEDGE[behavior]
                    approach = (x - dx, y - dy)
                    land = (x + dx, y + dy)
                    rec = {"map": name, "x": x, "y": y, "behavior": behavior,
                           "elevation": elev, "tile_collision": collision,
                           "on_seam_edge": (y == 0 or x == 0 or y == geom.h - 1
                                            or x == geom.w - 1),
                           "issues": []}
                    if collision == 0:
                        rec["issues"].append(
                            f"ledge tile ({x},{y}) is not solid, the player walks "
                            f"straight over it")
                    if 0 <= land[0] < geom.w and 0 <= land[1] < geom.h:
                        lc, le, lb = geom.tile(*land)
                        rec["landing"] = list(land)
                        rec["landing_behavior"] = lb
                        if lc != 0:
                            rec["issues"].append(
                                f"ledge lands on solid {lb} at {land}")
                    else:
                        rec["issues"].append(f"ledge hops off-map to {land}")
                    if 0 <= approach[0] < geom.w and 0 <= approach[1] < geom.h:
                        ac, _ae, _ab = geom.tile(*approach)
                        rec["approach"] = list(approach)
                        rec["approach_walkable"] = ac == 0
                        if ac != 0:
                            rec["issues"].append(
                                f"ledge cannot be reached: ({approach[0]},"
                                f"{approach[1]}) is not walkable")
                    else:
                        rec["approach_walkable"] = False
                        rec["issues"].append(
                            f"ledge has no approach tile (off-map at {approach})")
                    if rec["issues"]:
                        out["ledges"].append(rec)
                    out["counts"]["ledges"] += 1
                elif behavior in LADDERISH and (x, y) not in warp_tiles:
                    rec = {"map": name, "x": x, "y": y, "behavior": behavior}
                    out["orphan_ladders"].append(rec)
                elif behavior.startswith(STAIRISH) and (x, y) not in warp_tiles:
                    out["orphan_stairs"].append(
                        {"map": name, "x": x, "y": y, "behavior": behavior})

        # ---- door shape: is the interior warp one tile inside the door? ----
        for i, w in enumerate(data.get("warp_events", [])):
            wx, wy = w["x"], w["y"]
            try:
                _c, _e, beh = geom.tile(wx, wy)
            except Exception:
                continue
            if beh in DOORISH and w["dest_map"] != "MAP_DYNAMIC":
                target = by_id.get(w["dest_map"])
                if not target:
                    continue
                rec = {"map": name, "warp": i, "x": wx, "y": wy, "behavior": beh,
                       "dest": target, "issues": []}
                # the doorstep the player emerges onto must exist
                door_in = (wx, wy + 1)
                door_out = (wx, wy - 1)
                for label, tile in (("inside", door_in), ("outside", door_out)):
                    if not (0 <= tile[0] < geom.w and 0 <= tile[1] < geom.h):
                        rec["issues"].append(f"no {label} tile {tile}")
                out["door_shape"].append(rec)
            elif (x, y) in warp_tiles if False else False:
                pass
            elif beh == "MB_NORMAL":
                out["warp_on_plain_tile"].append(
                    {"map": name, "warp": i, "x": wx, "y": wy, "behavior": beh,
                     "dest": by_id.get(w["dest_map"], w["dest_map"])})

    out["counts"] = dict(out["counts"])
    out["summary"] = {
        "maps": len(names),
        "authored_region_portals": sum(
            1 for r in out["auto_teleports"] if r.get("class") == "authored region portal"),
        "legacy_vanilla_triggers": sum(
            1 for r in out["auto_teleports"] if r.get("class") == "legacy vanilla trigger"),
        "ledges_on_map_edge": sum(1 for r in out["ledges"] if r.get("on_seam_edge")),
        "ledge_tiles": out["counts"].get("ledges", 0),
        "ledges_with_issues": len(out["ledges"]),
        "orphan_ladders": len(out["orphan_ladders"]),
        "orphan_stairs": len(out["orphan_stairs"]),
        "auto_teleport_events": len(out["auto_teleports"]),
        "doors_checked": len(out["door_shape"]),
    }
    if args.json:
        args.json.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["summary"], indent=1))
    for key in ("ledges", "auto_teleports", "orphan_ladders"):
        for r in out[key][:20]:
            print(key, r)
    return out


if __name__ == "__main__":
    main()
