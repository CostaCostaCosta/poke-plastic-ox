#!/usr/bin/env python3
"""Regression checks for the Plastic Ox opening NU encounter block.

plastic_ox/encounter_tables/nu_encounters_v1.md is the forward spec; the tables
are installed by plastic_ox/encounter_tables/apply_nu_v1.py into
src/data/wild_encounters.json (grass / fishing) and
src/data/plastic_ox_pu_encounters.h (Headbutt, which the engine selects by
layout in src/wild_encounter.c rather than through the JSON).

The test asserts the real data against the document:

  * Route 37 grass, per time of day: exact species, exact rates, Lv. 21-23,
    rates totalling 100, and the document's "stable 65% core + 35% Johto
    time-of-day tail" structure;
  * Route 37 Headbutt, Lv. 21-23, exactly the seven authored slots;
  * Ecruteak City Good Rod, Lv. 21-23, and rod-exclusive by construction;
  * Burned Tower 1F, Lv. 22-24;
  * tier gating: every species is NU-tier or lower in the engine's own table
    (src/data/pokemon/evolution_tier_gates.h) and no level exceeds the NU
    block's cap of 30;
  * NU root coverage before Morty's Gym, as far as it is implemented;
  * Route 35's Old-Rod-only fishing table, which the PU document specifies and
    which this run verified rather than changed.

Run:  python3 plastic_ox/encounter_tables/test_nu_encounters_v1.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "agent"))
import audit_encounters_v55 as audit  # noqa: E402
import pox_progression as P  # noqa: E402

ROOT = P.ROOT
JSON_PATH = ROOT / "src/data/wild_encounters.json"
HEADBUTT_H = ROOT / "src/data/plastic_ox_pu_encounters.h"
NU_CAP = 30

# The document's stable 65% core, shared by all three periods.
ROUTE37_CORE = [("GROWLITHE", 25), ("VULPIX", 15), ("ROSELIA", 15), ("PLUSLE", 10)]
ROUTE37_GRASS = {
    "Morning": ROUTE37_CORE + [("PIDGEY", 15), ("LEDYBA", 10), ("SPEAROW", 10)],
    "Day":     ROUTE37_CORE + [("PIDGEY", 15), ("HOPPIP", 10), ("SPEAROW", 10)],
    "Night":   ROUTE37_CORE + [("HOOTHOOT", 15), ("SPINARAK", 10), ("MURKROW", 10)],
}
ROUTE37_GRASS_BAND = (21, 23)
ROUTE37_HEADBUTT = [("TEDDIURSA", 25), ("SEEDOT", 20), ("SLAKOTH", 15),
                    ("EXEGGCUTE", 15), ("HOOTHOOT", 10), ("PICHU", 10), ("KECLEON", 5)]
ROUTE37_HEADBUTT_BAND = (21, 23)

ECRUTEAK_ROD = [("POLIWAG", 30), ("BARBOACH", 20), ("SURSKIT", 15),
                ("GOLDEEN", 15), ("WOOPER", 10), ("CORPHISH", 10)]
ECRUTEAK_BAND = (21, 23)

BURNED_TOWER_1F = [("RATTATA", 30), ("KOFFING", 15), ("ZUBAT", 15), ("TORKOAL", 10),
                   ("SLUGMA", 10), ("HOUNDOUR", 10), ("GASTLY", 5), ("RATICATE", 5)]
BURNED_TOWER_1F_BAND = (22, 24)

# The PU document's Route 35 table: Old Rod only, Lv. 16-18, Corsola at 15%.
ROUTE35_OLD_ROD = [("POLIWAG", 30), ("GOLDEEN", 25), ("BARBOACH", 20),
                   ("CORSOLA", 15), ("PSYDUCK", 10)]
ROUTE35_BAND = (16, 18)

OU_ONLY_FAMILIES = {"Magikarp", "Gyarados", "Feebas", "Milotic", "Diglett", "Dugtrio",
                    "Shroomish", "Breloom"}

# Document section 6. "done" marks the lines this run implemented; the two that
# are not are reported in ENCOUNTER_FOLLOWUPS_V2_REPORT.md rather than faked.
NU_ROOT_COVERAGE = {
    "Sudowoodo":  ("Route 36 odd tree", True),
    "Roselia":    ("Route 37 grass 15%", "route37" in P.CHECKPOINT_NAMES),
    "Plusle":     ("Route 37 grass 10%", "route37" in P.CHECKPOINT_NAMES),
    "Murkrow":    ("Route 37 night grass 10%", "route37" in P.CHECKPOINT_NAMES),
    "Kecleon":    ("Route 37 Headbutt 5%", "route37" in P.CHECKPOINT_NAMES),
    "Relicanth":  ("Ecruteak Corsola NPC trade", False),   # trade not implemented
    "Torkoal":    ("Burned Tower 1F wild 10%", "burnedtower" in P.CHECKPOINT_NAMES),
    "Dunsparce":  ("Burned Tower B1F wild 10%", False),   # B1F map does not exist
    "Chimecho":   ("Burned Tower B1F wild 10%", False),   # B1F map does not exist
    "Sableye":    ("Burned Tower B1F wild 5%", False),    # B1F map does not exist
}


def sp(name: str) -> str:
    return "SPECIES_" + name.upper()


def weighted(mon_table):
    """{species: percent}, honouring the explicit weights the engine uses."""
    mons = mon_table["mons"]
    weights = mon_table.get("weights") or audit.FISHING_DEFAULT[:len(mons)]
    out: dict[str, int] = {}
    for mon, w in zip(mons, weights):
        out[mon["species"]] = out.get(mon["species"], 0) + w
    return out


def main() -> int:
    entries = json.loads(JSON_PATH.read_text())["wild_encounter_groups"][0]["encounters"]
    by_label = {e["base_label"]: e for e in entries}
    tiers = P.load_tiers()
    problems: list[str] = []
    checked = 0

    def table_matches(label, field, want, band, defaults):
        nonlocal checked
        entry = by_label.get(label)
        checked += 1
        if entry is None or field not in entry:
            problems.append(f"{label}: no {field} table")
            return set()
        t = entry[field]
        got = weighted(t) if field == "fishing_mons" else audit.effective(t, defaults)
        want_d = {sp(n): p for n, p in want}
        if got != want_d:
            problems.append(f"{label} {field}: got {got} want {want_d}")
        checked += 1
        if sum(got.values()) != 100:
            problems.append(f"{label} {field} rates total {sum(got.values())}, want 100")
        checked += 1
        if audit.levels(t) != [band]:
            problems.append(f"{label} {field} levels {audit.levels(t)}, want [{band}]")
        return set(got)

    species_in_block: set[str] = set()

    # --- Route 37 grass -----------------------------------------------------
    for time, want in ROUTE37_GRASS.items():
        species_in_block |= table_matches(f"gPoxNURoute37Hns_{time}", "land_mons",
                                         want, ROUTE37_GRASS_BAND, audit.LAND_DEFAULT)
    # the document's structural rule: a 65% core plus a 35% time-of-day tail
    core = {sp(n): p for n, p in ROUTE37_CORE}
    checked += 1
    if sum(core.values()) != 65:
        problems.append(f"Route 37 core totals {sum(core.values())}%, the document says 65%")
    for time, want in ROUTE37_GRASS.items():
        tail = {sp(n): p for n, p in want if sp(n) not in core}
        checked += 1
        if sum(tail.values()) != 35:
            problems.append(f"Route 37 {time} tail totals {sum(tail.values())}%, want 35%")

    # --- Ecruteak City Good Rod --------------------------------------------
    species_in_block |= table_matches("gPoxNUEcruteakCityHns", "fishing_mons",
                                     ECRUTEAK_ROD, ECRUTEAK_BAND, audit.FISHING_DEFAULT)
    # A weighted ten-slot table bypasses rod selection, so the five trailing
    # slots must carry weight 0 or the Good Rod pool would leak into other rods.
    ecruteak = by_label["gPoxNUEcruteakCityHns"]["fishing_mons"]
    checked += 1
    if sum(ecruteak["weights"][len(ECRUTEAK_ROD):]) != 0:
        problems.append("Ecruteak's trailing fishing slots have non-zero weight; "
                        "the table is not Good-Rod-only")

    # --- Burned Tower 1F ---------------------------------------------------
    species_in_block |= table_matches("gPoxNUBurnedTower1F", "land_mons",
                                     BURNED_TOWER_1F, BURNED_TOWER_1F_BAND,
                                     audit.LAND_DEFAULT)

    # --- Route 37 Headbutt --------------------------------------------------
    header_text = HEADBUTT_H.read_text()
    for time in ("Day", "Night"):
        checked += 1
        m = re.search(
            r"static const u8 sPoxRoute37Headbutt%sWeights\[\] = \{([^}]*)\};" % time,
            header_text)
        rows = re.search(
            r"static const struct WildPokemon sPoxRoute37Headbutt%sMons\[\] = \{(.*?)\n\};" % time,
            header_text, re.S)
        if not m or not rows:
            problems.append(f"sPoxRoute37Headbutt{time} is not defined in the Headbutt header")
            continue
        got = {}
        for name, weight in zip(re.findall(r"\{ \d+, \d+, SPECIES_(\w+) \}", rows.group(1)),
                                (int(x) for x in m.group(1).split(","))):
            got[sp(name)] = got.get(sp(name), 0) + weight
        want_d = {sp(n): p for n, p in ROUTE37_HEADBUTT}
        checked += 1
        if got != want_d:
            problems.append(f"Route 37 Headbutt {time}: got {got} want {want_d}")
        levels = {(int(a), int(b)) for a, b in
                  re.findall(r"\{ (\d+), (\d+), SPECIES", rows.group(1))}
        checked += 1
        if levels != {ROUTE37_HEADBUTT_BAND}:
            problems.append(f"Route 37 Headbutt {time} levels {levels}, "
                            f"want {ROUTE37_HEADBUTT_BAND}")
        species_in_block |= set(got)

    # --- Route 35 Old Rod (PU document; verified, unchanged) ----------------
    for time in ("Morning", "Day", "Night"):
        entry = by_label.get(f"gPoxPURoute35Hns_{time}")
        checked += 1
        if entry is None or "fishing_mons" not in entry:
            problems.append(f"gPoxPURoute35Hns_{time}: no fishing table")
            continue
        t = entry["fishing_mons"]
        got = weighted(t)
        want_d = {sp(n): p for n, p in ROUTE35_OLD_ROD}
        checked += 1
        if got != want_d:
            problems.append(f"Route 35 {time} Old Rod: got {got} want {want_d}")
        checked += 1
        if audit.levels(t) != [ROUTE35_BAND]:
            problems.append(f"Route 35 {time} levels {audit.levels(t)}, want [{ROUTE35_BAND}]")
        checked += 1
        if "SPECIES_CORSOLA" not in got or got["SPECIES_CORSOLA"] != 15:
            problems.append(f"Route 35 {time} does not offer Corsola at 15%")

    # --- tier gating and the NU cap ----------------------------------------
    unlocked = {"NONE", "LC", "PU", "NU"}
    for species in sorted(species_in_block):
        checked += 1
        tier = tiers.get(species)
        if tier is not None and tier not in unlocked:
            problems.append(f"{species} is {tier} and does not belong in the NU block")

    for label, entry in by_label.items():
        if not label.startswith("gPoxNU"):
            continue
        for field in ("land_mons", "fishing_mons"):
            for mon in entry.get(field, {}).get("mons", []):
                checked += 1
                if mon["min_level"] < 1 or mon["max_level"] > NU_CAP:
                    problems.append(f"{label} {mon['species']} is Lv{mon['min_level']}-"
                                    f"{mon['max_level']}, outside the NU cap of {NU_CAP}")
    for species in sorted(species_in_block):
        checked += 1
        if species.removeprefix("SPECIES_").title() in OU_ONLY_FAMILIES:
            problems.append(f"{species} is an OU-only family and must not appear in the NU block")

    # --- NU root coverage ---------------------------------------------------
    reachable = P.obtainable_at("gym3")
    for species, (where, implemented) in sorted(NU_ROOT_COVERAGE.items()):
        checked += 1
        if implemented and sp(species) not in reachable:
            problems.append(f"{species} ({where}) is implemented but not obtainable by Morty's Gym")

    for problem in problems:
        print("FAIL:", problem)
    if problems:
        print(f"{len(problems)} failure(s) across {checked} checks")
        return 1
    missing = sorted(s for s, (_w, ok) in NU_ROOT_COVERAGE.items() if not ok)
    print(f"PASS: {checked} NU-block encounter checks "
          f"({sum(1 for _w, ok in NU_ROOT_COVERAGE.values() if ok)}/{len(NU_ROOT_COVERAGE)} "
          f"documented NU roots implemented; still open: {', '.join(missing)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())