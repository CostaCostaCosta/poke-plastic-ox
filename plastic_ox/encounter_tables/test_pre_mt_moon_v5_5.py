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
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent"))
import audit_encounters_v55 as audit  # noqa: E402
import pox_progression as P  # noqa: E402

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

# The region has EIGHT wet areas, not seven: Ilex Forest carries a full three-rod
# table alongside Pallet, Oldale, Route 103, Cherrygrove, Route 24, Route 25 and
# Route 44. Ilex is an LC pond that deliberately reaches RU with Azumarill and
# Politoed; that exception is user-approved and is asserted here rather than
# quietly accepted by the generic Super Rod check below.
WET_AREAS = 8
GOOD_ROD_SLOTS = 24           # 8 areas x 3 slots
GOOD_ROD_DISTINCT_ROOTS = 20  # Poliwag is the only repeated species (3 times)
GOOD_ROD_MIN_LEVEL = 10
ILEX_FISHING = {
    "old": {"SPECIES_MAGIKARP": 70, "SPECIES_POLIWAG": 30},
    "good": {"SPECIES_POLIWAG": 60, "SPECIES_BARBOACH": 20, "SPECIES_CORPHISH": 20},
    "super": {"SPECIES_POLIWHIRL": 40, "SPECIES_WHISCASH": 40, "SPECIES_CRAWDAUNT": 15,
              "SPECIES_AZUMARILL": 4, "SPECIES_POLITOED": 1},
}
ILEX_ROD_SLOTS = {"old": (0, 1), "good": (2, 4), "super": (5, 9)}

# Headbutt tables whose area has no Headbutt tree object anywhere on its map.
REMOVED_HEADBUTT = ("sPoxRoute29Headbutt", "sPoxRoute46Headbutt", "sPoxRoute44Headbutt",
                    "sPoxRoute24Headbutt", "sPoxRoute25Headbutt")

MAPS_DIR = ROOT / "data/maps"


def headbutt_tree_maps() -> set[str]:
    """MAP_ constants for every map whose events reference the Headbutt script.

    Headbutt trees are bg_sign_events (the player faces the trunk), so this scans
    every map's generated events.inc and resolves its layout back to the map's
    MAP_ constant through data/maps/*/map.json, the same binding the engine's
    GetHeadbuttTable() switch works from.
    """
    found = set()
    for events in MAPS_DIR.glob("*/events.inc"):
        if "PlasticOx_EventScript_HeadbuttTree" not in events.read_text():
            continue
        map_json = events.parent / "map.json"
        if not map_json.exists():
            continue
        found.add(json.loads(map_json.read_text())["id"])
    return found


def specced_headbutt_maps() -> set[str]:
    """The maps this project still builds a Headbutt table for."""
    return set(P.HEADBUTT_SYMBOLS)


# Route 37's Headbutt table is specced by nu_encounters_v1.md but the map has no
# Headbutt tree object, and this task was told not to add one. It is therefore
# built and wired but unreachable until a tree is placed -- tracked, not hidden.
KNOWN_TREELESS_HEADBUTT = {"MAP_ROUTE37_HNS"}


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

    # --- the region has eight wet areas, not seven ----------------------------
    # Scoped to the v5.5 block: the PU (Route 35) and NU (Ecruteak) blocks carry
    # their own single-rod tables and are counted in test_nu_encounters_v1.py.
    v55_fishing = [e for e in entries if e.get("fishing_mons")
                   and e["map"] in audit.SPEC_FISHING]
    # Ilex has one table per time of day, so areas are counted by map.
    one_per_area = {}
    for e in v55_fishing:
        one_per_area.setdefault(e["map"], e)
    checked += 1
    if len(one_per_area) != WET_AREAS:
        problems.append(f"{len(one_per_area)} Plastic Ox v5.5 fishing areas, want {WET_AREAS}")

    # Ilex Forest: one identical ten-slot table per time of day, exactly as
    # specified -- Old Rod Magikarp/Poliwag, Good Rod Poliwag/Barboach/Corphish,
    # Super Rod Poliwhirl/Whiscash/Crawdaunt/Azumarill/Politoed.
    ilex = [e for e in entries if e["map"] == "MAP_ILEX_FOREST_HNS" and e.get("fishing_mons")]
    checked += 1
    if len(ilex) != 3:
        problems.append(f"Ilex Forest has {len(ilex)} fishing tables, want one per time of day")
    for entry in ilex:
        table = entry["fishing_mons"]
        checked += 1
        if len(table["mons"]) != 10:
            problems.append(f"{entry['base_label']} has {len(table['mons'])} slots, want 10")
        for rod, (lo, hi) in ILEX_ROD_SLOTS.items():
            got = {}
            for i in range(lo, hi + 1):
                s = table["mons"][i]["species"]
                got[s] = got.get(s, 0) + FISHING_DEFAULT[i]
            checked += 1
            if got != ILEX_FISHING[rod]:
                problems.append(f"{entry['base_label']} {rod}: got {got} want {ILEX_FISHING[rod]}")

    # Good Rod slot count, distinct-species count and the uniform level 10 floor.
    good_slots, good_species = 0, set()
    for entry in one_per_area.values():
        table = entry["fishing_mons"]
        if table.get("weights"):
            continue                          # rod-specific table, already specced
        lo, hi = ILEX_ROD_SLOTS["good"]
        for i in range(lo, hi + 1):
            checked += 1
            if table["mons"][i]["min_level"] != GOOD_ROD_MIN_LEVEL:
                problems.append(f"{entry['base_label']} Good Rod slot {i} starts at "
                                f"Lv{table['mons'][i]['min_level']}, want Lv{GOOD_ROD_MIN_LEVEL}")
            good_slots += 1
            good_species.add(table["mons"][i]["species"])
    checked += 1
    if good_slots != GOOD_ROD_SLOTS:
        problems.append(f"{good_slots} Good Rod slots, want {GOOD_ROD_SLOTS}")
    checked += 1
    if len(good_species) != GOOD_ROD_DISTINCT_ROOTS:
        problems.append(f"{len(good_species)} distinct Good Rod species, "
                        f"want {GOOD_ROD_DISTINCT_ROOTS}")

    # --- the five unreachable Headbutt tables are gone -----------------------
    symbols = set(re.findall(
        r"static const struct WildPokemonInfo (sPox\w+) = \{", header))
    for symbol in REMOVED_HEADBUTT:
        checked += 1
        if symbol in symbols:
            problems.append(f"{symbol} still defined but its area has no Headbutt tree")

    # Every Headbutt table that survives must belong to a map that actually has
    # a Headbutt tree object; otherwise it is dead data again.
    tree_maps = headbutt_tree_maps()
    checked += 1
    if not tree_maps:
        problems.append("no map carries a PlasticOx_EventScript_HeadbuttTree object")
    for map_name in sorted(specced_headbutt_maps() - KNOWN_TREELESS_HEADBUTT):
        checked += 1
        if map_name not in tree_maps:
            problems.append(f"{map_name} has a Headbutt table but no Headbutt tree object")
    for map_name in sorted(KNOWN_TREELESS_HEADBUTT):
        checked += 1
        if map_name in tree_maps:
            continue
        print(f"note: {map_name} has a Headbutt table but no Headbutt tree object; "
              "it stays unreachable until one is placed")

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
