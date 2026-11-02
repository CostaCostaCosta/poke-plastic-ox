#!/usr/bin/env python3
"""Install the exact v5.5 authored land rates for the pre-Mt. Moon grass tables.

The v5.5 document requires the authored grass percentages to be realised
exactly: "where an engine's default land-slot weights cannot represent one of
these tables, use the project's custom land encounter configuration instead of
silently changing the intended rates."

The pre-Mt. Moon tables produced by apply_pre_mt_moon_v4_4.py were fitted to the
engine's fixed 12 land slots (20/20/10/10/10/10/5/5/4/4/1/1), which cannot express
rates such as 30/25/15/10/10/5/5. The tables that already carry an explicit
"weights" array (Route 2 South/North, Dark Cave, and the whole PU block) prove
the weighted path works, so this script converts the remaining tables to it and
also drops the three species that the v5.5 tables do not list (Voltorb and
Koffing on Route 103, Trapinch on Route 46).

Only pre-Mt. Moon grass tables are touched; fishing, Headbutt, Rock Smash and the
PU block are left exactly as they are.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON = ROOT / "src/data/wild_encounters.json"

# (label, levels, {time: [(species, percent), ...]})
LAND_TABLES = {
    "gPoxRoute101": ((2, 4), {
        "": [("Wurmple", 30), ("Poochyena", 25), ("Taillow", 15), ("Lotad", 10),
             ("Seedot", 10), ("Surskit", 5), ("Slakoth", 5)],
    }),
    "gPoxRoute103": ((3, 5), {
        "Morning": [("Wingull", 25), ("Lotad", 20), ("Poochyena", 15), ("Seedot", 10),
                    ("Whismur", 10), ("Electrike", 10), ("Cacnea", 5), ("Gulpin", 5)],
        "Day": [("Wingull", 25), ("Lotad", 20), ("Poochyena", 15), ("Seedot", 10),
                ("Whismur", 10), ("Electrike", 10), ("Cacnea", 5), ("Gulpin", 5)],
        "Night": [("Wingull", 25), ("Lotad", 20), ("Poochyena", 15), ("Seedot", 10),
                  ("Whismur", 10), ("Electrike", 10), ("Cacnea", 5), ("Grimer", 5)],
    }),
    "gPoxRoute29Hns": ((3, 5), {
        "Morning": [("Sentret", 25), ("Pidgey", 15), ("Rattata", 15), ("Nidoran♀", 10),
                    ("Nidoran♂", 10), ("Mareep", 10), ("Spearow", 5), ("Hoppip", 5), ("Ponyta", 5)],
        "Day": [("Sentret", 25), ("Pidgey", 15), ("Rattata", 15), ("Nidoran♀", 10),
                ("Nidoran♂", 10), ("Mareep", 10), ("Spearow", 5), ("Hoppip", 5), ("Ponyta", 5)],
        "Night": [("Sentret", 25), ("Hoothoot", 15), ("Rattata", 15), ("Nidoran♀", 10),
                  ("Nidoran♂", 10), ("Mareep", 10), ("Spearow", 5), ("Spinarak", 5), ("Houndour", 5)],
    }),
    "gPoxRoute46Hns": ((4, 6), {
        "Morning": [("Geodude", 25), ("Rattata", 15), ("Machop", 15), ("Sandshrew", 10),
                    ("Rhyhorn", 10), ("Cubone", 10), ("Numel", 5), ("Bagon", 5), ("Phanpy", 5)],
        "Day": [("Geodude", 25), ("Rattata", 15), ("Machop", 15), ("Sandshrew", 10),
                ("Rhyhorn", 10), ("Cubone", 10), ("Numel", 5), ("Bagon", 5), ("Slugma", 5)],
        "Night": [("Geodude", 25), ("Zubat", 15), ("Machop", 15), ("Sandshrew", 10),
                  ("Rhyhorn", 10), ("Cubone", 10), ("Numel", 5), ("Bagon", 5), ("Slugma", 5)],
    }),
    "gPoxRoute24Hns": ((8, 11), {
        "Morning": [("Pichu", 20), ("Cleffa", 15), ("Igglybuff", 10), ("Togepi", 10),
                    ("Tyrogue", 10), ("Azurill", 10), ("Mareep", 10), ("Smoochum", 5),
                    ("Snubbull", 5), ("Elekid", 5)],
        "Day": [("Pichu", 20), ("Cleffa", 15), ("Igglybuff", 10), ("Togepi", 10),
                ("Tyrogue", 10), ("Azurill", 10), ("Mareep", 10), ("Smoochum", 5),
                ("Snubbull", 5), ("Elekid", 5)],
        "Night": [("Pichu", 20), ("Cleffa", 15), ("Igglybuff", 10), ("Togepi", 10),
                  ("Tyrogue", 10), ("Azurill", 10), ("Mareep", 10), ("Smoochum", 10),
                  ("Snubbull", 5)],
    }),
    "gPoxRoute25Hns": ((9, 12), {
        "Morning": [("Swablu", 20), ("Magby", 15), ("Meowth", 15), ("Drowzee", 10),
                    ("Growlithe", 10), ("Tyrogue", 10), ("Smoochum", 5), ("Doduo", 5),
                    ("Snubbull", 5), ("Ponyta", 5)],
        "Day": [("Swablu", 20), ("Magby", 15), ("Meowth", 15), ("Drowzee", 10),
                ("Growlithe", 10), ("Tyrogue", 10), ("Smoochum", 5), ("Doduo", 5),
                ("Snubbull", 5), ("Ponyta", 5)],
        "Night": [("Swablu", 20), ("Magby", 15), ("Meowth", 15), ("Drowzee", 10),
                  ("Growlithe", 10), ("Tyrogue", 10), ("Smoochum", 5), ("Igglybuff", 5),
                  ("Snubbull", 5), ("Houndour", 5)],
    }),
}

SPECIES_FIX = {"Nidoran♀": "NIDORAN_F", "Nidoran♂": "NIDORAN_M"}


def species(name: str) -> str:
    return "SPECIES_" + SPECIES_FIX.get(name, name.upper())


def main():
    data = json.loads(JSON.read_text())
    group = data["wild_encounter_groups"][0]
    touched = []
    for entry in group["encounters"]:
        base = entry["base_label"]
        if "land_mons" not in entry:
            continue  # fishing-only header sharing a base label stem
        for stem, ((lo, hi), per_time) in LAND_TABLES.items():
            if base != stem and base != f"{stem}_Morning" and base != f"{stem}_Day" and base != f"{stem}_Night":
                continue
            suffix = base[len(stem) + 1:] if base != stem else ""
            rows = per_time[suffix]
            assert sum(p for _, p in rows) == 100, (base, rows)
            entry["land_mons"] = {
                "encounter_rate": 20,
                "mons": [{"min_level": lo, "max_level": hi, "species": species(n)} for n, _ in rows],
                "weights": [p for _, p in rows],
            }
            touched.append(base)
    assert len(touched) == 16, sorted(touched)  # Route 101 is a single all-hours table + 5 areas x 3 periods
    JSON.write_text(json.dumps(data, indent=2) + "\n")
    print(f"rewrote {len(touched)} land tables with exact v5.5 weights")


if __name__ == "__main__":
    main()
