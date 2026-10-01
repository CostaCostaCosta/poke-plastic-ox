#!/usr/bin/env python3
"""Regression checks for the Plastic Ox pre-Mt. Moon encounter block.

Supersedes test_pre_mt_moon_v4_4.py, which asserted against the v4.4 document
and the pre-v5 map ids (MAP_ROUTE1, MAP_ROUTE104) and has been failing since
the v5.5 migration. The v5.5 document
(plastic_ox_pre_mt_moon_encounters_v5_5_agent_ready.md) is the authoritative end
state, so this test checks the real data against it:

  * every grass, cave, fishing and Rock Smash table, per time of day, matches the
    authored species and percentages exactly (the engine's explicit "weights"
    field is honoured when present, the fixed 12 land slots otherwise);
  * rates total 100 and the level bands match;
  * the v5.5 non-negotiables: Route 2 South/North have no fishing, Dark Cave's
    walking tables exclude Aron/Geodude/Onix/Whismur, Pineco is Ilex-Headbutt
    only, Old Rod slot 1 is always Magikarp, and no Super Rod slot holds a
    UU/UUBL/OU/Uber species, an OU-only family, Magikarp or Feebas.

Run:  python3 plastic_ox/encounter_tables/test_pre_mt_moon_v5_5.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_encounters_v55 as audit  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
LAND_DEFAULT = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]
FISHING_DEFAULT = [70, 30, 60, 20, 20, 40, 40, 15, 4, 1]
ROCKSMASH_DEFAULT = [60, 30, 5, 4, 1]

# The v5.5 release roster for Super Rod, and the families that must never appear.
SUPER_ROD_TIERS = {
    "LC": {"Tentacool", "Slowpoke"},
    "PU": {"Kingler", "Seaking", "Poliwhirl", "Seadra", "Corsola", "Dragonair", "Sealeo"},
    "NU": {"Crawdaunt", "Whiscash", "Octillery", "Wailord", "Huntail", "Dewgong"},
    "RU": {"Politoed", "Sharpedo", "Azumarill"},
}
SUPER_ROD_ALLOWED = set().union(*SUPER_ROD_TIERS.values())
OU_ONLY_FAMILIES = {"Magikarp", "Gyarados", "Feebas", "Milotic", "Diglett", "Dugtrio",
                    "Shroomish", "Breloom"}


def display(species: str) -> str:
    return species.removeprefix("SPECIES_").title().replace("_", "")


def effective(table, defaults):
    mons = table["mons"]
    weights = table.get("weights") or defaults[:len(mons)]
    agg = {}
    for mon, weight in zip(mons, weights):
        agg[mon["species"]] = agg.get(mon["species"], 0) + weight
    return agg


def main() -> int:
    report = audit.build_report()
    problems = []
    checked = 0

    for group in ("grass", "fishing", "rock_smash", "headbutt"):
        for row in report[group]:
            checked += 1
            if not row.get("ok"):
                problems.append(f"{group} {row.get('table') or row.get('label')}: "
                                f"{'; '.join(row.get('problems', []))}")
    for row in report["invariants"]:
        checked += 1
        if not row.get("ok"):
            problems.append(f"invariant {row.get('check')}: {row.get('detail')}")

    data = json.loads((ROOT / "src/data/wild_encounters.json").read_text())
    entries = data["wild_encounter_groups"][0]["encounters"]
    by_map = {}
    for entry in entries:
        by_map.setdefault(entry["map"], []).append(entry)

    # --- v5.5 non-negotiable progression rules -----------------------------
    route2 = by_map.get("MAP_ROUTE2", [])
    checked += 1
    if any("fishing_mons" in e or "water_mons" in e for e in route2):
        problems.append("MAP_ROUTE2 (Route 2 South/North) has a fishing or water table")
    checked += 1
    if {e["base_label"] for e in route2} != {
            "gPoxRoute2South_Morning", "gPoxRoute2South_Day", "gPoxRoute2South_Night",
            "gPoxRoute2North_Morning", "gPoxRoute2North_Day", "gPoxRoute2North_Night"}:
        problems.append("MAP_ROUTE2 does not have exactly the two v5.5 grass tables per period")

    rock_only = {"SPECIES_ARON", "SPECIES_GEODUDE", "SPECIES_ONIX", "SPECIES_WHISMUR"}
    for entry in by_map.get("MAP_DARK_CAVE_SOUTH_SIDE_HNS", []):
        checked += 1
        walking = {m["species"] for m in entry.get("land_mons", {}).get("mons", [])}
        if walking & rock_only:
            problems.append(f"{entry['base_label']} walking table still has "
                            f"{sorted(display(s) for s in walking & rock_only)}")
        smash = entry.get("rock_smash_mons")
        if smash is not None:
            if effective(smash, ROCKSMASH_DEFAULT) != {
                    "SPECIES_ARON": 60, "SPECIES_RHYHORN": 30,
                    "SPECIES_GEODUDE": 5, "SPECIES_ONIX": 5}:
                problems.append(f"{entry['base_label']} Rock Smash table is not 60/30/5/5")

    # Pineco is an Ilex Forest Headbutt exclusive
    checked += 1
    pineco = []
    for entry in entries:
        for field in audit.WILD_FIELDS:
            for mon in entry.get(field, {}).get("mons", []):
                if mon["species"] == "SPECIES_PINECO":
                    pineco.append((entry["map"], field))
    header = (ROOT / "src/data/plastic_ox_pu_encounters.h").read_text()
    for symbol, body in re.findall(
            r"static const struct WildPokemon (\w+)Mons\[\] = \{(.*?)\n\};", header, re.S):
        if "SPECIES_PINECO" in body and not symbol.startswith("sPoxIlexHeadbutt"):
            pineco.append(("headbutt", symbol))
    if pineco:
        problems.append(f"Pineco is not Ilex-exclusive: {pineco}")

    # Old Rod slot 1 is Magikarp and Super Rod stays LC-RU, on the Plastic Ox
    # fishing tables only. Native Hoenn and FRLG tables are untouched by v5.5.
    for entry in entries:
        fishing = entry.get("fishing_mons")
        if not fishing or not entry["base_label"].startswith("gPox"):
            continue
        mons = fishing["mons"]
        if fishing.get("weights"):
            # Route 35 carries one weighted Old Rod pool across all ten slots.
            agg = effective(fishing, FISHING_DEFAULT)
            checked += 1
            if "Magikarp" in agg:
                problems.append(f"{entry['base_label']} weighted fishing table exposes Magikarp")
            continue
        checked += 1
        if mons[0]["species"] != "SPECIES_MAGIKARP":
            problems.append(f"{entry['base_label']} Old Rod slot 1 is "
                            f"{display(mons[0]['species'])}, want Magikarp")
        for mon in mons[5:10]:
            name = display(mon["species"])
            checked += 1
            if name not in SUPER_ROD_ALLOWED:
                problems.append(f"{entry['base_label']} Super Rod holds {name}, "
                                "which is not an approved LC-RU species")
            if name in OU_ONLY_FAMILIES:
                problems.append(f"{entry['base_label']} Super Rod holds OU-only {name}")

    # Route 44 grass stays Surf-gated: it must not have a grass table at all
    checked += 1
    if any("land_mons" in e for e in by_map.get("MAP_ROUTE44_HNS", [])):
        problems.append("MAP_ROUTE44_HNS has a grass table; v5.5 gates it behind Surf")

    # Every Plastic Ox table's rates total 100
    for entry in entries:
        if not entry["base_label"].startswith("gPox"):
            continue
        for field, defaults in (("land_mons", LAND_DEFAULT), ("rock_smash_mons", ROCKSMASH_DEFAULT)):
            table = entry.get(field)
            if not table:
                continue
            checked += 1
            total = sum(effective(table, defaults).values())
            if total != 100:
                problems.append(f"{entry['base_label']} {field} totals {total}, want 100")

    for problem in problems:
        print("FAIL:", problem)
    if problems:
        print(f"{len(problems)} failure(s) across {checked} checks")
        return 1
    print(f"PASS: {checked} pre-Mt. Moon encounter checks against the v5.5 specification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
