"""Restore fixed Gen 2 fruit trees without replacing other route events."""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRUIT_TREES = {
    "Route29_hns": [(15, 11, "Sitrus")],
    "Route46_hns": [(9, 11, "Lum"), (11, 11, "Liechi")],
    "Route44_hns": [(7, 10, "Salac"), (9, 10, "Petaya")],
}


def install():
    for name, trees in FRUIT_TREES.items():
        path = ROOT / "data/maps" / name / "map.json"
        data = json.loads(path.read_text())
        data["object_events"] = [obj for obj in data["object_events"]
                                 if not obj.get("script", "").startswith("PlasticOx_BerryTree_")]
        for x, y, berry in trees:
            data["object_events"].append(dict(
                graphics_id="OBJ_EVENT_GFX_APRICORN_TREE", x=x, y=y, elevation=3,
                movement_type="MOVEMENT_TYPE_NONE", movement_range_x=0, movement_range_y=0,
                trainer_type="TRAINER_TYPE_NONE", trainer_sight_or_berry_tree_id="0",
                script="PlasticOx_BerryTree_" + berry, flag="0"))
        path.write_text(json.dumps(data, indent=2) + "\n")
    # Route 46's imported layout has only decorative pines. Put one native
    # HNS Headbutt tree beside its fruit grove, on an otherwise open tile.
    path = ROOT / "data/layouts/Route46_hns/map.bin"
    data = bytearray(path.read_bytes())
    struct.pack_into("<H", data, 2 * (11 * 27 + 13), 0x3405)
    path.write_bytes(data)


if __name__ == "__main__":
    install()
