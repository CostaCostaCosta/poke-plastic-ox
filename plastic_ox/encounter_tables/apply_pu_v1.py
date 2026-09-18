#!/usr/bin/env python3
"""Install exact PU encounter tables and area-specific Headbutt populations."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON = ROOT / "src/data/wild_encounters.json"

# (percentage, day species, optional night species). Morning uses the day table.
TABLES = {
    # LC trees: v4.4 populations, with Pineco kept exclusive to Ilex by
    # the later PU habitat rule. Route 44 has an early, shoreline tree pool.
    "Route29Headbutt": (3, 5, [(25, "SLAKOTH"), (15, "SPEAROW"), (15, "LEDYBA", "SPINARAK"), (15, "NATU"), (10, "EXEGGCUTE"), (10, "PARAS"), (10, "HOOTHOOT")]),
    "Route46Headbutt": (4, 6, [(25, "NATU"), (15, "SPEAROW"), (15, "HOOTHOOT"), (15, "SLAKOTH"), (15, "EXEGGCUTE"), (15, "PARAS")]),
    "Route44Headbutt": (10, 13, [(25, "SPEAROW", "HOOTHOOT"), (20, "MEOWTH"), (15, "NATU"), (15, "EXEGGCUTE"), (15, "SLAKOTH"), (10, "LEDYBA", "SPINARAK")]),
    "MtMoon1F": (12, 14, [(25, "NOSEPASS"), (15, "ZUBAT"), (15, "GEODUDE"), (15, "PARAS"), (10, "MEDITITE"), (10, "CLEFAIRY"), (5, "MAWILE"), (5, "SHUCKLE")]),
    "MtMoonDeep": (14, 16, [(20, "CLEFAIRY"), (15, "NOSEPASS"), (15, "ZUBAT"), (15, "GEODUDE"), (10, "PARAS"), (10, "MAWILE"), (10, "SHUCKLE"), (5, "MEDITITE")]),
    "Route33Grass": (14, 16, [(25, "ZIGZAGOON"), (20, "SPEAROW", "RATTATA"), (15, "HOPPIP", "SPINARAK"), (10, "GEODUDE"), (10, "EKANS"), (10, "SPINDA"), (5, "SEVIPER"), (5, "ZUBAT")]),
    "Route33Headbutt": (14, 16, [(30, "AIPOM"), (25, "SPEAROW"), (15, "EXEGGCUTE"), (10, "NATU"), (10, "SLAKOTH"), (10, "HOOTHOOT")]),
    "Route35Grass": (16, 18, [(30, "FARFETCHD"), (15, "DROWZEE"), (15, "NIDORAN_F"), (15, "NIDORAN_M"), (10, "ABRA"), (5, "MINUN"), (5, "DITTO"), (5, "YANMA")]),
    "Route35Headbutt": (16, 18, [(30, "SPEAROW", "HOOTHOOT"), (20, "EXEGGCUTE"), (15, "NATU"), (15, "SUNKERN"), (10, "VENONAT"), (10, "HOOTHOOT", "SPEAROW")]),
    "Route35OldRod": (16, 18, [(30, "POLIWAG"), (25, "GOLDEEN"), (20, "BARBOACH"), (15, "CORSOLA"), (10, "PSYDUCK")]),
    "ParkGrass": (17, 19, [(25, "HOPPIP"), (15, "NIDORAN_F"), (15, "NIDORAN_M"), (10, "LICKITUNG"), (10, "JIGGLYPUFF"), (10, "PIDGEY", "HOOTHOOT"), (10, "LEDYBA", "SPINARAK"), (5, "TROPIUS")]),
    "ParkContest": (17, 20, [(20, "CATERPIE"), (20, "WEEDLE"), (10, "METAPOD"), (10, "KAKUNA"), (10, "PARAS"), (10, "VENONAT"), (5, "BUTTERFREE"), (5, "BEEDRILL"), (5, "VOLBEAT"), (5, "ILLUMISE")]),
    "ParkHeadbutt": (17, 19, [(30, "LEDYBA", "SPINARAK"), (15, "EXEGGCUTE"), (15, "AIPOM"), (15, "TAILLOW"), (15, "WURMPLE"), (10, "SUNKERN")]),
    "Route36Grass": (18, 20, [(25, "BELLSPROUT"), (20, "NATU"), (10, "TANGELA"), (10, "VULPIX", "GASTLY"), (10, "PIDGEY", "HOOTHOOT"), (10, "HOPPIP"), (10, "DROWZEE"), (5, "BALTOY")]),
    "Route36Headbutt": (18, 20, [(30, "NATU"), (20, "SLAKOTH"), (15, "EXEGGCUTE"), (15, "AIPOM"), (10, "SHUPPET"), (10, "DUSKULL")]),
}
# LC tree population retained independently of PU; Pineco has no other habitat.
ILEX = (6, 8, [(25, "LEDYBA", "SPINARAK"), (15, "PINECO"), (15, "EXEGGCUTE"), (15, "SUNKERN"), (10, "CATERPIE", "HOOTHOOT"), (10, "WEEDLE"), (10, "PARAS")])
MAPS = {
    "MAP_MT_MOON_CAVE_HNS": "MtMoon1F",
    "MAP_MT_MOON_1F": "MtMoon1F",
    "MAP_MT_MOON_B1F": "MtMoonDeep",
    "MAP_MT_MOON_B2F": "MtMoonDeep",
    "MAP_ROUTE33_HNS": "Route33Grass",
    "MAP_ROUTE35_HNS": "Route35Grass",
    "MAP_NATIONAL_PARK_NORMAL_HNS": "ParkGrass",
    "MAP_ROUTE36_HNS": "Route36Grass",
}


def table(data, night=False, slots=12):
    lo, hi, rows = data
    mons = [{"min_level": lo, "max_level": hi, "species": "SPECIES_" + row[2 if night and len(row) > 2 else 1]} for row in rows]
    weights = [row[0] for row in rows]
    # Legacy consumers may index all twelve slots. Padding is safe, never selected.
    while len(mons) < slots:
        mons.append(dict(mons[-1]))
        weights.append(0)
    return {"encounter_rate": 20, "mons": mons, "weights": weights}


def remove_non_ilex_pineco(data):
    for group in data["wild_encounter_groups"]:
        for entry in group.get("encounters", []):
            for method in ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons", "hidden_mons"):
                for mon in entry.get(method, {}).get("mons", []):
                    if mon["species"] == "SPECIES_PINECO":
                        mon["species"] = "SPECIES_PARAS"


def install(data):
    group = data["wild_encounter_groups"][0]
    group["encounters"] = [entry for entry in group["encounters"] if entry["map"] not in MAPS and entry["map"] != "MAP_GOLDENROD_CITY_HNS"]
    for map_name, name in MAPS.items():
        for time in ("Morning", "Day", "Night"):
            entry = {"map": map_name, "base_label": "gPoxPU" + map_name[4:].title().replace("_", "") + "_" + time,
                     "land_mons": table(TABLES[name], time == "Night")}
            if map_name == "MAP_ROUTE35_HNS":
                entry["fishing_mons"] = table(TABLES["Route35OldRod"], slots=10)
            group["encounters"].append(entry)
    remove_non_ilex_pineco(data)
    return data


def write_special_tables():
    lines = ["// Generated by plastic_ox/encounter_tables/apply_pu_v1.py; edit its source tables."]
    specials = {name: data for name, data in TABLES.items() if "Headbutt" in name or "Contest" in name}
    specials["IlexHeadbutt"] = ILEX
    for name, data in specials.items():
        for time in ("Day", "Night"):
            entry = table(data, time == "Night", slots=0)
            symbol = "sPox" + name + time
            lines.append(f"static const struct WildPokemon {symbol}Mons[] = {{")
            for mon in entry["mons"]:
                lines.append(f'    {{ {mon["min_level"]}, {mon["max_level"]}, {mon["species"]} }},')
            lines += ["};", f"static const u8 {symbol}Weights[] = {{ " + ", ".join(map(str, entry["weights"])) + " };",
                      f"static const struct WildPokemonInfo {symbol} = {{ 20, {symbol}Mons, {symbol}Weights, ARRAY_COUNT({symbol}Mons) }};"]
    (ROOT / "src/data/plastic_ox_pu_encounters.h").write_text("\n".join(lines) + "\n")


def main():
    JSON.write_text(json.dumps(install(json.loads(JSON.read_text())), indent=2) + "\n")
    write_special_tables()


if __name__ == "__main__":
    main()
