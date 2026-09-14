#!/usr/bin/env python3
"""Sample regional graphics in mGBA; assert maintained camera buffers agree.

Placements are emulator-only visual probes, not proof of continuous traversal.
Use test_region_v7.py and test_camera_seam.py for actual D-pad transitions.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw
import audit_region_rendering as audit

SAMPLES = {
    "PalletTown_Frlg": (12, 10), "Route101": (10, 10),
    "OldaleTown": (10, 10), "CherrygroveCity_hns": (20, 20),
    "GoldenrodCity_hns": (32, 30), "EcruteakCity_hns": (32, 32),
    "SaffronCity_hns": (32, 26), "LavenderTown_hns": (15, 14),
    "CinnabarIsland_hns": (35, 13), "RustboroCity": (18, 30),
    "FortreeCity": (20, 9), "MossdeepCity": (22, 20),
    "MeteorFalls_1F_1R": (14, 17), "IlexForest_hns": (14, 32),
    "BlackthornCity_hns": (20, 20), "Route2_Frlg": (10, 65),
    "Route8_Frlg": (34, 20), "Route19_Frlg": (12, 30),
    "PlasticOx_Route20West": (48, 12), "PlasticOx_Route20East": (12, 12),
    "Route103": (40, 12), "Route110": (15, 67),
    "Route115": (10, 45), "Route119": (20, 70),
    "NationalPark_Normal_hns": (26, 20), "DarkCave_SouthSide_hns": (14, 20),
    "BattleFrontier_OutsideWest": (30, 30), "BattleFrontier_OutsideEast": (30, 30),
    "VictoryRoad_1F": (20, 15), "VictoryRoad_B1F": (20, 15), "VictoryRoad_B2F": (20, 15),
    "PlasticOx_VictoryRoad": (10, 10), "PlasticOx_WhirlIslands": (10, 10),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--triggers", action="store_true")
    parser.add_argument("--label", default="after")
    parser.add_argument("--grid", action="store_true", help="sample all upgraded outdoor maps across their extent")
    args = parser.parse_args()
    out = audit.ROOT / "plastic_ox/demo/shots/regional_styles" / args.label
    out.mkdir(parents=True, exist_ok=True)
    audit.OUT = out
    game = audit.setup()
    overview = Image.new("RGB", (960, ((len(SAMPLES) + 3) // 4) * 180), "#111111")
    draw = ImageDraw.Draw(overview)
    report = []
    for i, (name, point) in enumerate(SAMPLES.items()):
        game.warp(name, *point)
        game.frame(120)
        result = audit.visual(game, name)
        assert result["mismatches"] == 0, (name, result)
        overview.paste(game.fb.to_pil().convert("RGB"), (i % 4 * 240, i // 4 * 180))
        draw.text((i % 4 * 240 + 3, i // 4 * 180 + 161), name, fill="white")
        record = {"map": name, "views": [result]}
        layout = audit.layouts[audit.maps[name]["layout"]]
        if args.grid and layout["primary_tileset"].startswith("gTileset_HoennOras"):
            w, h, blocks = audit.geometry(name)
            for y in range(5, h, 10):
                for x in range(5, w, 12):
                    # Visual placements deliberately include blocked terrain;
                    # this exposes roofs/cliffs without altering the map.
                    game.warp(name, x, y)
                    view = audit.visual(game, f"{name}_{x}_{y}")
                    assert view["mismatches"] == 0, (name, view)
                    record["views"].append(view)
        report.append(record)
        print(name, len(record["views"]), "views PASS", flush=True)
    overview.save(out / "overview.png")
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {sum(len(r['views']) for r in report)} views across {len(report)} regional maps")


if __name__ == "__main__":
    main()
