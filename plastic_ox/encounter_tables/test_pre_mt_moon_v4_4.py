#!/usr/bin/env python3
"""Static regression checks for Plastic Ox pre-Mt. Moon encounters/trainers."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import apply_pre_mt_moon_v4_4 as source

ROOT = Path(__file__).resolve().parents[2]
TRAINERS = {
    "TRAINER_PLASTIC_OX_ROUTE101": "MAP_ROUTE101",
    "TRAINER_PLASTIC_OX_ROUTE103": "MAP_ROUTE103",
    "TRAINER_PLASTIC_OX_ROUTE29": "MAP_ROUTE29_HNS",
    "TRAINER_PLASTIC_OX_ROUTE46": "MAP_ROUTE46_HNS",
    "TRAINER_PLASTIC_OX_ROUTE1": "MAP_ROUTE1",
    "TRAINER_PLASTIC_OX_ROUTE31": "MAP_ROUTE31_HNS",
    "TRAINER_PLASTIC_OX_ROUTE104": "MAP_ROUTE104",
    "TRAINER_PLASTIC_OX_ROUTE24": "MAP_ROUTE24_HNS",
    "TRAINER_PLASTIC_OX_ROUTE25": "MAP_ROUTE25_HNS",
    "TRAINER_PLASTIC_OX_ROUTE44": "MAP_ROUTE44_HNS",
}


def main():
    expected = source.entries()
    data = json.loads(source.JSON.read_text())["wild_encounter_groups"][0]["encounters"]
    actual = defaultdict(list)
    for entry in data:
        actual[(entry["map"], entry["base_label"])].append(entry)
    for wanted in expected:
        key = wanted["map"], wanted["base_label"]
        assert key in actual, f"missing encounter table {key}"
        field = "land_mons" if "land_mons" in wanted else "fishing_mons"
        matching = [entry for entry in actual[key] if field in entry]
        assert len(matching) == 1, f"expected one {field} table for {key}"
        got_mons = matching[0][field]["mons"]
        want_mons = wanted[field]["mons"]
        assert got_mons == want_mons, f"table mismatch for {key}"
        expected_slots = 12 if field == "land_mons" else 20
        assert len(got_mons) == expected_slots, f"{key} has the wrong slot count"

    available = defaultdict(set)
    for entry in expected:
        for field in ("land_mons", "fishing_mons"):
            for mon in entry.get(field, {}).get("mons", []):
                available[entry["map"]].add(mon["species"].removeprefix("SPECIES_").title().replace("_", ""))

    party_text = (ROOT / "src/data/trainers.party").read_text()
    sections = re.split(r"^=== (\w+) ===$", party_text, flags=re.MULTILINE)
    parsed = {sections[i]: sections[i + 1] for i in range(1, len(sections), 2)}
    for trainer, map_name in TRAINERS.items():
        body = parsed[trainer]
        mons = []
        for block in re.split(r"\n\n+", body.strip()):
            first = block.splitlines()[0]
            if first.startswith(("Name:", "Class:", "Pic:", "Gender:", "Music:", "Double Battle:", "AI:")):
                continue
            mons.append(first.split(" @ ")[0].split(" (")[0].replace(" ", ""))
        assert 2 <= len(mons) <= 4, f"{trainer} has {len(mons)} Pokémon"
        missing = [mon for mon in mons if mon not in available[map_name]]
        assert not missing, f"{trainer} uses unavailable Pokémon: {missing}"

    print(f"PASS: {len(expected)} encounter tables and {len(TRAINERS)} local route trainers")


if __name__ == "__main__":
    main()
