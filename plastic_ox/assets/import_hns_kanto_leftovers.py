#!/usr/bin/env python3
"""Replace suitable active FRLG Kanto layouts with complete pinned HnS donors."""
import argparse
import copy
import json
from pathlib import Path
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
REVISION = "44f50eedefe58691b0444973e4138e9190d8fafc"

LAYOUT_MAPS = {
    "Route8_Frlg": "Route8_hns",
    "Route19_Frlg": "Route19_hns",
    "Route2_House_Frlg": "Route2_House_hns",
    "Route2_ViridianForest_NorthEntrance_Frlg": "Gate_ViridianForest_Route2_hns",
    "Route2_ViridianForest_SouthEntrance_Frlg": "Gate_Route2_ViridianForest_hns",
    "Route2_EastBuilding_Frlg": "Gate_Route2_hns",
}


def load(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def project(events, old_w, old_h, new_w, new_h):
    result = copy.deepcopy(events or [])
    for event in result:
        event["x"] = min(new_w - 1, max(0, round(event["x"] * (new_w - 1) / max(1, old_w - 1))))
        event["y"] = min(new_h - 1, max(0, round(event["y"] * (new_h - 1) / max(1, old_h - 1))))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--donor", type=Path, required=True)
    args = parser.parse_args()
    donor = args.donor.resolve()
    revision = subprocess.check_output(["git", "-C", donor, "rev-parse", "HEAD"], text=True).strip()
    if revision != REVISION:
        parser.error(f"expected HnS {REVISION}, got {revision}")

    layouts = load(ROOT / "data/layouts/layouts.json")
    ours = {x["id"]: x for x in layouts["layouts"]}
    theirs = {x["id"]: x for x in load(donor / "data/layouts/layouts.json")["layouts"]}

    for target, source in LAYOUT_MAPS.items():
        target_path = ROOT / "data/maps" / target / "map.json"
        target_map = load(target_path)
        source_map = load(donor / "data/maps" / source / "map.json")
        old = ours[target_map["layout"]]
        imported = copy.deepcopy(theirs[source_map["layout"]])
        imported.pop("game_version", None)
        imported["include_in_versions"] = ["emerald"]
        if imported["id"] not in ours:
            layouts["layouts"].append(imported)
            ours[imported["id"]] = imported
        for key in ("border_filepath", "blockdata_filepath"):
            destination = ROOT / imported[key]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(donor / imported[key], destination)
        if (old["width"], old["height"]) != (imported["width"], imported["height"]):
            for key in ("object_events", "coord_events", "bg_events"):
                target_map[key] = project(target_map.get(key), old["width"], old["height"], imported["width"], imported["height"])
        target_map["layout"] = imported["id"]
        if target == "Route8_Frlg":
            # Retain the Plastic Ox Underground Path destination at the HnS tunnel door.
            target_map["warp_events"][0].update(x=12, y=17, elevation=0)
        if target.startswith("Route2_ViridianForest_") or target == "Route2_EastBuilding_Frlg":
            for warp in target_map["warp_events"][:3]:
                warp["y"] = 9
            target_map["warp_events"][3].update(x=7, y=1, elevation=0)
        save(target_path, target_map)

    # Route 2's HnS geometry is already registered; preserve authored events
    # and destinations while moving each warp to its semantic donor doorway.
    route2_path = ROOT / "data/maps/Route2_Frlg/map.json"
    route2 = load(route2_path)
    route2["layout"] = "LAYOUT_ROUTE2_HNS"
    positions = [(5, 13), (6, 13), (5, 51), (17, 11), (17, 22),
                 (18, 46), (18, 40), (19, 40), (19, 46), (6, 51)]
    for warp, (x, y) in zip(route2["warp_events"], positions):
        warp.update(x=x, y=y, elevation=0)
    save(route2_path, route2)

    # Route 20 is active as two Plastic Ox slices. Re-slice the complete HnS
    # 120x20 blockmap and carry its HnS border and tileset pair with both halves.
    route20 = theirs["LAYOUT_ROUTE20_HNS"]
    source_raw = (donor / route20["blockdata_filepath"]).read_bytes()
    words = struct.unpack("<" + "H" * (len(source_raw) // 2), source_raw)
    for suffix, start, width in (("West", 0, 66), ("East", 66, 54)):
        layout = ours[f"LAYOUT_PLASTIC_OX_ROUTE20_{suffix.upper()}"]
        layout.update(primary_tileset=route20["primary_tileset"], secondary_tileset=route20["secondary_tileset"],
                      layout_version="hns", border_width=2, border_height=2)
        destination = ROOT / "data/layouts" / f"PlasticOx_Route20{suffix}"
        cropped = [words[y * 120 + x] for y in range(20) for x in range(start, start + width)]
        (destination / "map.bin").write_bytes(struct.pack("<" + "H" * len(cropped), *cropped))
        shutil.copy2(donor / route20["border_filepath"], destination / "border.bin")

    save(ROOT / "data/layouts/layouts.json", layouts)
    print(f"Imported HnS Route 2/8/19/20 and four Route 2 interiors from {revision}")


if __name__ == "__main__":
    main()
