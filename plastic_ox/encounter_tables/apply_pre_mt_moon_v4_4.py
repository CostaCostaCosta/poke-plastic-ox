#!/usr/bin/env python3
"""Install the supported v4.4 pre-Mt. Moon grass/cave/Old Rod tables."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = Path(__file__).with_name("plastic_ox_pre_mt_moon_encounters_v4_4.md")
JSON = ROOT / "src/data/wild_encounters.json"

MAPS = {
    "Pallet Town": "MAP_PALLET_TOWN",
    "Route 101": "MAP_ROUTE101",
    "Oldale Town": "MAP_OLDALE_TOWN",
    "Route 103": "MAP_ROUTE103",
    "Route 29": "MAP_ROUTE29_HNS",
    "Route 46": "MAP_ROUTE46_HNS",
    "Cherrygrove City": "MAP_CHERRYGROVE_CITY_HNS",
    # Route 2 is split by Ilex geographically, though the runtime map has
    # only one encounter header. The south table is retained on the legacy
    # Route 1 ID; Route 2 itself uses the northern (former Route 31) table.
    "Route 2 South (former Route 1)": "MAP_ROUTE1",
    "Route 2 North (former Route 31)": "MAP_ROUTE2",
    "Dark Cave": "MAP_DARK_CAVE_SOUTH_SIDE_HNS",
    "Ilex Forest": "MAP_ILEX_FOREST_HNS",
    "Route 104": "MAP_ROUTE104",
    "Route 24": "MAP_ROUTE24_HNS",
    "Route 25": "MAP_ROUTE25_HNS",
    "Route 44": "MAP_ROUTE44_HNS",
}
SPECIES_FIX = {"Nidoran♀": "NIDORAN_F", "Nidoran♂": "NIDORAN_M"}
LAND_WEIGHTS = (20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1)


def species(name: str) -> str:
    return "SPECIES_" + SPECIES_FIX.get(name, name.upper().replace(" ", "_"))


def parse_doc():
    area = method = None
    levels = (2, 2)
    tables = []
    lines = DOC.read_text().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"# \d+\. (.+)", line)
        if m:
            area = m.group(1)
        m = re.match(r"## (Grass|Cave|Old Rod).*Lv\. (\d+)[–-](\d+)", line)
        if m and area in MAPS:
            method, levels = m.group(1), (int(m.group(2)), int(m.group(3)))
            header = []
            rows = []
            i += 1
            while i < len(lines) and not lines[i].startswith("|"):
                i += 1
            if i < len(lines):
                header = [x.strip() for x in lines[i].strip("|").split("|")]
                i += 2
                while i < len(lines) and lines[i].startswith("|"):
                    cells = [x.strip().replace("**", "") for x in lines[i].strip("|").split("|")]
                    if cells and "Total" not in cells[0] and "100%" not in cells[0]:
                        rows.append(cells)
                    i += 1
                tables.append((area, method, levels, header, rows))
                continue
        i += 1
    return tables


def weighted_slots(weighted):
    """Expand 5%-granularity authored weights into twenty uniform slots."""
    return [name for weight, name in weighted for _ in range(weight // 5)]


def land_slots(weighted):
    """Fit authored rates to the engine's fixed 12 land slots."""
    targets = [weight for weight, _ in weighted]
    # Seed one slot per species, choosing the remaining assignments greedily
    # by the largest current deficit. This retains the complete species pool.
    assignment = list(range(len(weighted)))
    for slot in range(len(weighted), len(LAND_WEIGHTS)):
        current = [sum(LAND_WEIGHTS[i] for i, owner in enumerate(assignment) if owner == j)
                   for j in range(len(weighted))]
        assignment.append(max(range(len(weighted)), key=lambda j: targets[j] - current[j]))
    # Improve the seed by exhaustive single-slot substitutions.
    while True:
        current = [sum(LAND_WEIGHTS[i] for i, owner in enumerate(assignment) if owner == j)
                   for j in range(len(weighted))]
        score = sum(abs(current[j] - targets[j]) for j in range(len(weighted)))
        best = None
        for slot, old in enumerate(assignment):
            if assignment.count(old) == 1:
                continue
            for new in range(len(weighted)):
                trial = current.copy()
                trial[old] -= LAND_WEIGHTS[slot]
                trial[new] += LAND_WEIGHTS[slot]
                trial_score = sum(abs(trial[j] - targets[j]) for j in range(len(weighted)))
                if trial_score < score and (best is None or trial_score < best[0]):
                    best = trial_score, slot, new
        if best is None:
            break
        assignment[best[1]] = best[2]
    return [weighted[owner][1] for owner in assignment]


def mons(names, levels):
    lo, hi = levels
    return [{"min_level": lo, "max_level": hi, "species": species(name)} for name in names]


def entries():
    result = []
    for area, method, levels, header, rows in parse_doc():
        if method == "Old Rod":
            weighted = [(int(row[1].rstrip("%")), row[0]) for row in rows]
            names = weighted_slots(weighted)
            result.append({"map": MAPS[area], "base_label": f"gPox{MAPS[area][4:].title().replace('_', '')}",
                           "fishing_mons": {"encounter_rate": 20, "mons": mons(names, levels)}})
            continue
        times = ["Morning", "Day", "Night"] if "Morning" in header else [None]
        for col, time in enumerate(times, 1):
            if time:
                weighted = [(int(row[0].rstrip("%")), row[col]) for row in rows]
            else:
                weighted = [(int(row[1].rstrip("%")), row[0]) for row in rows]
            names = land_slots(weighted)
            suffix = f"_{time}" if time else ""
            result.append({"map": MAPS[area], "base_label": f"gPox{MAPS[area][4:].title().replace('_', '')}{suffix}",
                           "land_mons": {"encounter_rate": 20, "mons": mons(names, levels)}})
    return result


def main():
    data = json.loads(JSON.read_text())
    group = data["wild_encounter_groups"][0]
    target_maps = set(MAPS.values())
    group["encounters"] = [e for e in group["encounters"] if e["map"] not in target_maps]
    group["encounters"].extend(entries())
    # PU establishes Pineco as Ilex Headbutt-only, including after LC regeneration.
    from apply_pu_v1 import remove_non_ilex_pineco
    remove_non_ilex_pineco(data)
    JSON.write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    main()
