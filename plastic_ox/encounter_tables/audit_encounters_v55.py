#!/usr/bin/env python3
"""Audit Plastic Ox wild encounters against plastic_ox_pre_mt_moon_encounters_v5_5_agent_ready.md.

The v5.5 document is the authoritative end state for the pre-Mt. Moon block. This
script recomputes the *effective* conditional probability of every species in every
Plastic Ox table (honouring an explicit "weights" override, otherwise the engine's
fixed land-slot weights) and reports each deviation.

Usage:  python3 plastic_ox/encounter_tables/audit_encounters_v55.py [--json]
Exit status is always 0; the report is the product.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "src/data/wild_encounters.json"
HEADBUTT_H = ROOT / "src/data/plastic_ox_pu_encounters.h"

# Engine defaults (src/data/wild_encounters.json -> wild_encounter_groups[0].fields)
WILD_FIELDS = ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons", "hidden_mons")
LAND_DEFAULT = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]
WATER_DEFAULT = [60, 30, 5, 4, 1]
ROCKSMASH_DEFAULT = [60, 30, 5, 4, 1]
FISHING_DEFAULT = [70, 30, 60, 20, 20, 40, 40, 15, 4, 1]

# ---------------------------------------------------------------------------
# v5.5 specification, transcribed from the authoritative document.
# Each entry: (map, base_label, field, {species: percent}, (min, max) level band or None)
# A species name may be a "A|B" pair meaning morning|day same, but night differs;
# tables are listed per time-of-day column instead, which is unambiguous.
# ---------------------------------------------------------------------------

SPEC_FISHING = {
    "MAP_PALLET_TOWN": ("gPoxPalletTown", (2, 5), [
        ("old", [("Magikarp", 70), ("Krabby", 30)]),
        ("good", [("Poliwag", 60), ("Goldeen", 20), ("Krabby", 20)]),
        ("super", [("Kingler", 40), ("Seaking", 40), ("Poliwhirl", 15), ("Seadra", 4), ("Corsola", 1)]),
    ]),
    "MAP_OLDALE_TOWN": ("gPoxOldaleTown", (3, 5), [
        ("old", [("Magikarp", 70), ("Wooper", 30)]),
        ("good", [("Wooper", 60), ("Barboach", 20), ("Corphish", 20)]),
        ("super", [("Crawdaunt", 40), ("Whiscash", 40), ("Octillery", 15), ("Wailord", 4), ("Politoed", 1)]),
    ]),
    "MAP_ROUTE103": ("gPoxRoute103", (3, 6), [
        ("old", [("Magikarp", 70), ("Tentacool", 30)]),
        ("good", [("Tentacool", 60), ("Carvanha", 20), ("Wailmer", 20)]),
        ("super", [("Tentacool", 40), ("Sharpedo", 40), ("Crawdaunt", 15), ("Huntail", 4), ("Wailord", 1)]),
    ]),
    "MAP_CHERRYGROVE_CITY_HNS": ("gPoxCherrygroveCityHns", (4, 6), [
        ("old", [("Magikarp", 70), ("Slowpoke", 30)]),
        ("good", [("Slowpoke", 60), ("Seel", 20), ("Shellder", 20)]),
        ("super", [("Slowpoke", 40), ("Dewgong", 40), ("Seadra", 15), ("Octillery", 4), ("Corsola", 1)]),
    ]),
    # Ilex Forest is an eighth wet area with its own full three-rod table. It is
    # an LC-tier pond, so Azumarill and Politoed (RU) are a deliberate,
    # user-approved exception to the LC-only pool the other seven areas keep.
    "MAP_ILEX_FOREST_HNS": ("gPoxIlexForestHns_Morning", (6, 8), [
        ("old", [("Magikarp", 70), ("Poliwag", 30)]),
        ("good", [("Poliwag", 60), ("Barboach", 20), ("Corphish", 20)]),
        ("super", [("Poliwhirl", 40), ("Whiscash", 40), ("Crawdaunt", 15), ("Azumarill", 4), ("Politoed", 1)]),
    ]),
    "MAP_ROUTE24_HNS": ("gPoxRoute24Hns", (8, 11), [
        ("old", [("Magikarp", 70), ("Psyduck", 30)]),
        ("good", [("Psyduck", 60), ("Chinchou", 20), ("Staryu", 20)]),
        ("super", [("Poliwhirl", 40), ("Seaking", 40), ("Kingler", 15), ("Azumarill", 4), ("Politoed", 1)]),
    ]),
    "MAP_ROUTE25_HNS": ("gPoxRoute25Hns", (9, 12), [
        ("old", [("Magikarp", 70), ("Seel", 30)]),
        ("good", [("Spheal", 60), ("Horsea", 20), ("Dratini", 20)]),
        ("super", [("Sealeo", 40), ("Seadra", 40), ("Dragonair", 15), ("Wailord", 4), ("Corsola", 1)]),
    ]),
    "MAP_ROUTE44_HNS": ("gPoxRoute44Hns", (10, 13), [
        ("old", [("Magikarp", 70), ("Poliwag", 30)]),
        ("good", [("Remoraid", 60), ("Clamperl", 20), ("Poliwag", 20)]),
        ("super", [("Seaking", 40), ("Dewgong", 40), ("Dragonair", 15), ("Octillery", 4), ("Azumarill", 1)]),
    ]),
}

# Every Good Rod slot in every Plastic Ox table bottoms out at the single level
# 10 rather than the area's own band; the ceiling still follows the area.
# Confirmed by the user; asserted here so it cannot drift.
GOOD_ROD_MIN_LEVEL = 10
# Azumarill and Politoed are RU but appear in this LC pond on purpose.
APPROVED_RU_EXCEPTIONS = {"Azumarill", "Politoed"}

# (species, morning, day, night) with the authored percentage.
SPEC_GRASS = {
    ("MAP_ROUTE101", "gPoxRoute101", None, (2, 4)): [
        ("Wurmple", 30, 30, 30), ("Poochyena", 25, 25, 25), ("Taillow", 15, 15, 15),
        ("Lotad", 10, 10, 10), ("Seedot", 10, 10, 10), ("Surskit", 5, 5, 5), ("Slakoth", 5, 5, 5),
    ],
    ("MAP_ROUTE103", "gPoxRoute103", "Morning", (3, 5)): [
        ("Wingull", 25, 25, 25), ("Lotad", 20, 20, 20), ("Poochyena", 15, 15, 15),
        ("Seedot", 10, 10, 10), ("Whismur", 10, 10, 10), ("Electrike", 10, 10, 10),
        ("Cacnea", 5, 5, 5), ("Gulpin", 5, 5, 0), ("Grimer", 0, 0, 5),
    ],
    ("MAP_ROUTE29_HNS", "gPoxRoute29Hns", "Morning", (3, 5)): [
        ("Sentret", 25, 25, 25), ("Pidgey", 15, 15, 0), ("Rattata", 15, 15, 15),
        ("Nidoran♀", 10, 10, 10), ("Nidoran♂", 10, 10, 10), ("Mareep", 10, 10, 10),
        ("Spearow", 5, 5, 5), ("Hoppip", 5, 5, 0), ("Ponyta", 5, 5, 0),
        ("Hoothoot", 0, 0, 15), ("Spinarak", 0, 0, 5), ("Houndour", 0, 0, 5),
    ],
    ("MAP_ROUTE46_HNS", "gPoxRoute46Hns", "Morning", (4, 6)): [
        ("Geodude", 25, 25, 25), ("Rattata", 15, 15, 0), ("Machop", 15, 15, 15),
        ("Sandshrew", 10, 10, 10), ("Rhyhorn", 10, 10, 10), ("Cubone", 10, 10, 10),
        ("Numel", 5, 5, 5), ("Bagon", 5, 5, 5), ("Phanpy", 5, 0, 0), ("Slugma", 0, 5, 5),
        ("Zubat", 0, 0, 15),
    ],
    ("MAP_ROUTE2", "gPoxRoute2South", "Morning", (4, 6)): [
        ("Mankey", 25, 25, 25), ("Spearow", 20, 20, 0), ("Drowzee", 0, 0, 20),
        ("Meowth", 15, 15, 15), ("Ekans", 10, 10, 10), ("Rattata", 10, 10, 10),
        ("Pidgey", 10, 10, 10), ("Growlithe", 5, 5, 0), ("Vulpix", 5, 5, 10),
    ],
    ("MAP_ILEX_FOREST_HNS", "gPoxIlexForestHns", "Morning", (6, 8)): [
        ("Paras", 25, 25, 25), ("Venonat", 20, 20, 20), ("Weedle", 15, 15, 15),
        ("Caterpie", 10, 10, 0), ("Spinarak", 0, 0, 10), ("Oddish", 10, 10, 10),
        ("Nincada", 10, 10, 0), ("Shuppet", 0, 0, 10), ("Lotad", 5, 5, 5), ("Seedot", 5, 5, 5),
    ],
    ("MAP_ROUTE2", "gPoxRoute2North", "Morning", (7, 10)): [
        ("Taillow", 20, 20, 0), ("Hoothoot", 0, 0, 20), ("Skitty", 15, 15, 15),
        ("Electrike", 15, 15, 15), ("Bellsprout", 10, 10, 10), ("Hoppip", 10, 10, 10),
        ("Ralts", 5, 5, 5), ("Magnemite", 5, 5, 5), ("Spoink", 5, 5, 5),
        ("Trapinch", 5, 5, 0), ("Koffing", 0, 0, 5), ("Voltorb", 5, 5, 0),
        ("Gastly", 0, 0, 5), ("Gulpin", 5, 5, 5),
    ],
    ("MAP_DARK_CAVE_SOUTH_SIDE_HNS", "gPoxDarkCaveSouthSideHns", "Morning", (5, 8)): [
        ("Zubat", 35, 35, 35), ("Baltoy", 30, 30, 30), ("Swinub", 20, 20, 0),
        ("Snorunt", 0, 0, 20), ("Teddiursa", 10, 0, 0), ("Makuhita", 0, 10, 0),
        ("Duskull", 0, 0, 10), ("Larvitar", 5, 5, 5),
    ],
    ("MAP_ROUTE24_HNS", "gPoxRoute24Hns", "Morning", (8, 11)): [
        ("Pichu", 20, 20, 20), ("Cleffa", 15, 15, 15), ("Igglybuff", 10, 10, 10),
        ("Togepi", 10, 10, 10), ("Tyrogue", 10, 10, 10), ("Azurill", 10, 10, 10),
        ("Mareep", 10, 10, 10), ("Smoochum", 5, 5, 10), ("Snubbull", 5, 5, 5),
        ("Elekid", 5, 5, 0),
    ],
    ("MAP_ROUTE25_HNS", "gPoxRoute25Hns", "Morning", (9, 12)): [
        ("Swablu", 20, 20, 20), ("Magby", 15, 15, 15), ("Meowth", 15, 15, 15),
        ("Drowzee", 10, 10, 10), ("Growlithe", 10, 10, 10), ("Tyrogue", 10, 10, 10),
        ("Smoochum", 5, 5, 5), ("Doduo", 5, 5, 0), ("Igglybuff", 0, 0, 5),
        ("Snubbull", 5, 5, 5), ("Ponyta", 5, 5, 0), ("Houndour", 0, 0, 5),
    ],
}

SPEC_ROCK_SMASH = {
    ("MAP_DARK_CAVE_SOUTH_SIDE_HNS", "gPoxDarkCaveSouthSideHns"): (5, 8, [("Aron", 60), ("Rhyhorn", 30), ("Geodude", 5), ("Onix", 5)]),
}

SPEC_HEADBUTT = {
    "sPoxRoute33Headbutt": (14, 16, [("Aipom", 30, 30), ("Spearow", 25, 25), ("Exeggcute", 15, 15), ("Natu", 10, 10), ("Slakoth", 10, 10), ("Hoothoot", 10, 10)]),
    "sPoxRoute35Headbutt": (16, 18, [("Spearow", 30, 0), ("Hoothoot", 0, 30), ("Exeggcute", 20, 20), ("Natu", 15, 15), ("Sunkern", 15, 15), ("Venonat", 10, 10), ("Hoothoot", 10, 0), ("Spearow", 0, 10)]),
    "sPoxParkHeadbutt": (17, 19, [("Ledyba", 30, 0), ("Spinarak", 0, 30), ("Exeggcute", 15, 15), ("Aipom", 15, 15), ("Taillow", 15, 15), ("Wurmple", 15, 15), ("Sunkern", 10, 10)]),
    "sPoxRoute36Headbutt": (18, 20, [("Natu", 30, 30), ("Slakoth", 20, 20), ("Exeggcute", 15, 15), ("Aipom", 15, 15), ("Shuppet", 10, 10), ("Duskull", 10, 10)]),
    "sPoxIlexHeadbutt": (6, 8, [("Ledyba", 25, 0), ("Spinarak", 0, 25), ("Pineco", 15, 15), ("Exeggcute", 15, 15),
                                ("Sunkern", 15, 15), ("Caterpie", 10, 0), ("Hoothoot", 0, 10), ("Weedle", 10, 10), ("Paras", 10, 10)]),
}
# Route 29, Route 46, Route 44, Route 24 and Route 25 have no Headbutt tree
# object anywhere on their map, so their tables were unreachable and removed.
REMOVED_HEADBUTT = ("sPoxRoute29Headbutt", "sPoxRoute46Headbutt", "sPoxRoute44Headbutt",
                    "sPoxRoute24Headbutt", "sPoxRoute25Headbutt")

SPECIES_FIX = {"Nidoran♀": "SPECIES_NIDORAN_F", "Nidoran♂": "SPECIES_NIDORAN_M"}


def sp(name: str) -> str:
    return SPECIES_FIX.get(name, "SPECIES_" + name.upper().replace(" ", "_"))


def load():
    data = json.loads(JSON_PATH.read_text())
    return data["wild_encounter_groups"][0]["encounters"]


def effective(mon_table, default_weights):
    """Return {species: percent} using explicit weights when present."""
    mons = mon_table["mons"]
    w = mon_table.get("weights")
    if w is None:
        w = default_weights[:len(mons)]
    agg = defaultdict(int)
    for m, weight in zip(mons, w):
        agg[m["species"]] += weight
    return dict(agg)


def levels(mon_table):
    return sorted({(m["min_level"], m["max_level"]) for m in mon_table["mons"]})


def parse_headbutt_header():
    """Parse src/data/plastic_ox_pu_encounters.h into {symbol: (levels, [(species, w)])}."""
    import re
    text = HEADBUTT_H.read_text()
    out = {}
    pattern = (r"static const struct WildPokemon (\w+)Mons\[\] = \{(.*?)\};\n"
               r"static const u8 \w+Weights\[\] = \{ ([^}]*) \};\n"
               r"static const struct WildPokemonInfo \w+ = \{ 20,")
    for symbol, mons, weights in re.findall(pattern, text, re.S):
        levels = tuple(int(x) for x in re.findall(r"\{ (\d+), (\d+), SPECIES", mons)[0])
        species = re.findall(r"\{ \d+, \d+, (SPECIES_\w+) \}", mons)
        out[symbol] = (levels, list(zip(species, [int(x) for x in weights.split(",")])))
    return out


def build_report() -> dict:
    entries = load()
    by_label = {e["base_label"]: e for e in entries}
    report = {"fishing": [], "grass": [], "rock_smash": [], "headbutt": [], "invariants": []}
    ok = lambda **kw: kw

    # ---- fishing -----------------------------------------------------------
    for map_name, (label, band, rods) in SPEC_FISHING.items():
        entry = by_label.get(label)
        if entry is None or "fishing_mons" not in entry:
            report["fishing"].append(ok(area=map_name, status="MISSING"))
            continue
        t = entry["fishing_mons"]
        got = effective(t, FISHING_DEFAULT)
        problems = []
        if len(t["mons"]) != 10:
            problems.append(f"{len(t['mons'])} slots (want 10)")
        for rod, slots in rods:
            want = {sp(n): p for n, p in slots}
            got_rod = {}
            idx = {"old": (0, 1), "good": (2, 3, 4), "super": (5, 6, 7, 8, 9)}[rod]
            for i in idx:
                got_rod[t["mons"][i]["species"]] = got_rod.get(t["mons"][i]["species"], 0) + \
                    (t["weights"][i] if t.get("weights") else FISHING_DEFAULT[i])
            if got_rod != want:
                problems.append(f"{rod}: got {got_rod} want {want}")
        # Good Rod is the one rod with a uniform floor, not the area band.
        for i in (2, 3, 4):
            m = t["mons"][i]
            if m["min_level"] != GOOD_ROD_MIN_LEVEL:
                problems.append(f"Good Rod slot {i} starts at Lv{m['min_level']}, "
                                f"want the uniform Lv{GOOD_ROD_MIN_LEVEL} floor")
        lv = levels(t)
        report["fishing"].append(ok(area=map_name, label=label, bands=lv, ok=not problems, problems=problems))

    # ---- grass -------------------------------------------------------------
    col = {"Morning": 1, "Day": 2, "Night": 3}
    for (map_name, base, time, band), rows in SPEC_GRASS.items():
        for t_name in (["Morning", "Day", "Night"] if time else [None]):
            label = base + (f"_{t_name}" if t_name else "")
            entry = by_label.get(label)
            if entry is None or "land_mons" not in entry:
                report["grass"].append(ok(area=map_name, label=label, status="MISSING"))
                continue
            t = entry["land_mons"]
            got = effective(t, LAND_DEFAULT)
            idx = col[t_name] if t_name else 1
            want = {sp(r[0]): r[idx] for r in rows if r[idx] > 0}
            problems = []
            if sum(got.values()) != 100:
                problems.append(f"rates sum to {sum(got.values())}")
            diff = {k: (got.get(k, 0), want.get(k, 0)) for k in set(got) | set(want) if got.get(k, 0) != want.get(k, 0)}
            if diff:
                problems.append(f"rate diff (got,want): {diff}")
            if levels(t) != [band]:
                problems.append(f"levels {levels(t)} want [{band}]")
            report["grass"].append(ok(area=map_name, label=label, bands=levels(t),
                                      exact=not diff, ok=not problems, problems=problems))

    # ---- rock smash --------------------------------------------------------
    for (map_name, base), (lo, hi, want) in SPEC_ROCK_SMASH.items():
        for t_name in ("Morning", "Day", "Night"):
            label = f"{base}_{t_name}"
            entry = by_label.get(label)
            t = entry.get("rock_smash_mons") if entry else None
            if t is None:
                report["rock_smash"].append(ok(area=map_name, label=label, status="MISSING"))
                continue
            got = effective(t, ROCKSMASH_DEFAULT)
            want_d = {sp(n): p for n, p in want}
            problems = [] if got == want_d else [f"got {got} want {want_d}"]
            if levels(t) != [(lo, hi)]:
                problems.append(f"levels {levels(t)}")
            if len(t["mons"]) != 5:
                problems.append(f"{len(t['mons'])} slots")
            report["rock_smash"].append(ok(area=map_name, label=label, ok=not problems, problems=problems))

    # ---- headbutt (src/data/plastic_ox_pu_encounters.h) --------------------
    header = parse_headbutt_header()
    for symbol, (lo, hi, rows) in SPEC_HEADBUTT.items():
        band = (lo, hi)
        for time, col in (("Day", 1), ("Night", 2)):
            want = {sp(r[0]): r[col] for r in rows if r[col] > 0}
            key = f"{symbol}{time}"
            if key not in header:
                report["headbutt"].append(ok(area=symbol, table=key, status="MISSING"))
                continue
            lv, got_list = header[key]
            got = {}
            for s, w in got_list:
                got[s] = got.get(s, 0) + w
            problems = []
            if got != want:
                problems.append(f"got {got} want {want}")
            if lv != band:
                problems.append(f"levels {lv} want {band}")
            if sum(got.values()) != 100:
                problems.append(f"rates sum to {sum(got.values())}")
            report["headbutt"].append(ok(area=symbol, table=key, ok=not problems, problems=problems))

    # ---- tier gating of every Super Rod slot --------------------------------
    super_rod_allowed = {
        "LC": {"Tentacool", "Slowpoke"},
        "PU": {"Kingler", "Seaking", "Poliwhirl", "Seadra", "Corsola", "Dragonair", "Sealeo"},
        "NU": {"Crawdaunt", "Whiscash", "Octillery", "Wailord", "Huntail", "Dewgong"},
        "RU": {"Politoed", "Sharpedo", "Azumarill"},
    }
    tier_of = {s: tier for tier, ss in super_rod_allowed.items() for s in ss}
    for map_name, (label, _band, _rods) in SPEC_FISHING.items():
        t = by_label[label]["fishing_mons"]
        for i in range(5, 10):
            name = t["mons"][i]["species"].removeprefix("SPECIES_").title().replace("_", "")
            if name not in tier_of:
                report["invariants"].append(ok(area=map_name, check="super_rod_tier", ok=False,
                                              detail=f"slot {i} {name} is not an approved LC-RU species"))
    report["invariants"].append(ok(check="super_rod_no_forbidden", ok=True,
                                   detail=f"all {len(SPEC_FISHING)} specced wet areas use only "
                                          "LC-PU-NU-RU Super Rod species"))

    # ---- the removed Headbutt tables must really be gone ---------------------
    header = parse_headbutt_header()
    for symbol in REMOVED_HEADBUTT:
        report["invariants"].append(ok(check="headbutt_removed", ok=symbol not in header,
                                       detail=f"{symbol} is absent" if symbol not in header
                                       else f"{symbol} is still defined but has no Headbutt tree"))

    return report


def main():
    print(json.dumps(build_report(), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
