#!/usr/bin/env python3
"""Static native-warp audit for the active Plastic-Ox region closure.

This deliberately audits source map JSON only.  Runtime landing/collision and
rendering evidence is supplied by test_cave_connections.py,
test_region_v7.py --warps, and test_regional_doors.py.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGION = ROOT / "plastic_ox/alpha/region_v7.py"


def active_names():
    text = REGION.read_text()
    block = text.split("ANCHORS = {", 1)[1].split("\n}", 1)[0]
    names = set(re.findall(r"'([^']+)'\s*:\s*\(", block))
    names |= {f"SeafoamIslands_{x}_Frlg" for x in ("1F", "B1F", "B2F", "B3F", "B4F")}
    names |= {
        "UndergroundPath_EastEntrance_Frlg", "UndergroundPath_WestEntrance_Frlg",
        "UndergroundPath_EastWestTunnel_Frlg", "PokemonMansion_1F_Frlg",
        "MtMoon_1F_Frlg", "MtMoon_B1F_Frlg", "MtMoon_B2F_Frlg",
        "Route2_ViridianForest_NorthEntrance_Frlg",
        "Route2_ViridianForest_SouthEntrance_Frlg", "Route2_House_Frlg",
        "Route2_EastBuilding_Frlg",
    }
    return names


def load_maps():
    """Load the complete catalog, then close over native warps/connections."""
    catalog = {p.parent.name: json.loads(p.read_text())
               for p in (ROOT / "data/maps").glob("*/map.json")}
    by_id = {d["id"]: n for n, d in catalog.items()}
    seeds = {n for n in active_names() if n in catalog}
    reached = set(seeds)
    queue = list(seeds)
    while queue:
        name = queue.pop()
        data = catalog[name]
        targets = [w.get("dest_map") for w in data.get("warp_events", [])]
        targets += [c.get("map") for c in (data.get("connections") or [])]
        for target_id in targets:
            target = by_id.get(target_id)
            if target and target not in reached:
                reached.add(target)
                queue.append(target)
    return {n: catalog[n] for n in reached}, by_id, catalog


def audit():
    maps, by_id, catalog = load_maps()
    records, external = [], []
    for source in sorted(maps):
        data = maps[source]
        for index, warp in enumerate(data.get("warp_events", [])):
            target = by_id.get(warp.get("dest_map"))
            if target is None:
                status = "dynamic" if warp.get("dest_map") == "MAP_DYNAMIC" else "missing_target"
                external.append({"source": source, "warp": index, "status": status,
                                 "destination_id": warp.get("dest_map"),
                                 "destination_warp": warp.get("dest_warp_id")})
                continue
            try:
                target_index = int(warp["dest_warp_id"])
            except (KeyError, TypeError, ValueError):
                records.append({"source": source, "warp": index, "status": "bad_index",
                                "destination": target, "destination_warp": warp.get("dest_warp_id")})
                continue
            target_warps = maps[target].get("warp_events", [])
            if not 0 <= target_index < len(target_warps):
                records.append({"source": source, "warp": index, "status": "bad_index",
                                "destination": target, "destination_warp": target_index,
                                "target_count": len(target_warps)})
                continue
            back = target_warps[target_index]
            reciprocal = (back.get("dest_map") == data["id"] and
                          int(back.get("dest_warp_id", -1)) == index)
            # Arrival/landing anchors intentionally point at a paired door's
            # inbound warp rather than forming a reciprocal self-loop.
            target_scope = "active_seed_closure" if target in active_names() else "transitive_donor"
            records.append({"source": source, "warp": index, "destination": target,
                            "destination_warp": target_index,
                            "source_xy": [warp.get("x"), warp.get("y")],
                            "target_xy": [back.get("x"), back.get("y")],
                            "elevation": [warp.get("elevation"), back.get("elevation")],
                            "reciprocal": reciprocal,
                            "target_scope": target_scope,
                            "status": "reciprocal" if reciprocal else "nonreciprocal"})
    # Camera connections are part of the reached graph even when they have no
    # warp event. Validate their IDs separately and expose them in the report.
    connections = []
    for source in sorted(maps):
        for conn in maps[source].get("connections", []) or []:
            target_id = conn.get("map")
            target = by_id.get(target_id)
            connections.append({"source": source, "destination_id": target_id,
                                "destination": target,
                                "status": "resolved" if target else "missing_target"})
    return {"seed_count": len(active_names()), "map_count": len(maps),
            "internal_link_count": len(records), "external_link_count": len(external),
            "links": records, "external": external, "connections": connections}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, help="write the full audit JSON")
    args = parser.parse_args()
    report = audit()
    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n")
    reciprocal = sum(r.get("reciprocal", False) for r in report["links"])
    nonreciprocal = len(report["links"]) - reciprocal
    bad = [r for r in report["links"] if r["status"] == "bad_index"]
    missing = [r for r in report["external"] if r["status"] == "missing_target"]
    print(f"maps={report['map_count']} internal={report['internal_link_count']} "
          f"external={report['external_link_count']} reciprocal={reciprocal} "
          f"nonreciprocal={nonreciprocal} bad_indices={len(bad)} "
          f"missing_targets={len(missing)} connections={len(report['connections'])}")
    if bad or missing or any(c["status"] == "missing_target" for c in report["connections"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
