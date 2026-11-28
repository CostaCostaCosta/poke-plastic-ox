#!/usr/bin/env python3
"""Regression checks for the Route 34 and Route 115 (both OU) encounter tables.

Installed by plastic_ox/encounter_tables/apply_route34_115_v1.py. Asserts that
the ROM data matches the generator's tables, that every species is legal for the
route's checkpoint tier and level cap, that Chansey and Heracross are reachable
(Route 115 grass and Headbutt), and that both Headbutt tables are wired: a
GetHeadbuttTable() case per layout, and Route 115's tree bg event.

Run:  python3 plastic_ox/encounter_tables/test_route34_115_encounters_v1.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "tools"))
import apply_route34_115_v1 as A  # noqa: E402
import pox_progression as P  # noqa: E402

ROOT = P.ROOT
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


wild = json.loads((ROOT / "src/data/wild_encounters.json").read_text())
entries = {e["base_label"]: e for e in wild["wild_encounter_groups"][0]["encounters"]}
tiers = P.load_tiers()
rank = {t: i for i, t in enumerate(P.TIER_ORDER)}


def expect(label, field, data, tier, cap):
    e = entries.get(label)
    check(e is not None, f"{label} missing")
    if e is None:
        return
    lo, hi, rows = data
    got = e[field]
    live = [(w, m["species"][8:]) for m, w in zip(got["mons"], got["weights"]) if w]
    check(live == [(r, s) for r, s in rows], f"{label}.{field}: {live} != {rows}")
    check(sum(got["weights"]) == 100, f"{label}.{field} weights total {sum(got['weights'])}")
    for m in got["mons"]:
        check((m["min_level"], m["max_level"]) == (lo, hi), f"{label}.{field} level band {m}")
        check(m["max_level"] <= cap, f"{label}.{field} {m['species']} over cap {cap}")
    for _r, sp in rows:
        t = tiers.get("SPECIES_" + sp)
        check(t is not None and rank[t] <= rank[tier], f"{label}.{field} {sp} is {t}, above {tier}")


expect("gPoxOURoute34Hns", "land_mons", A.ROUTE34_GRASS, "OU", 55)
expect("gPoxOURoute34Hns", "water_mons", A.ROUTE34_SURF, "OU", 55)
expect("gPoxOURoute34Hns", "fishing_mons", A.ROUTE34_FISHING, "OU", 55)
expect("gPoxOURoute115", "land_mons", A.ROUTE115_GRASS, "OU", 55)
expect("gPoxOURoute115", "water_mons", A.ROUTE115_SURF, "OU", 55)
expect("gPoxOURoute115", "fishing_mons", A.ROUTE115_FISHING, "OU", 55)
check("gRoute115" not in entries, "vanilla gRoute115 table still present")
check(entries.get("gPoxOURoute115", {}).get("map") == "MAP_ROUTE115", "gPoxOURoute115 map")
check(entries.get("gPoxOURoute34Hns", {}).get("map") == "MAP_ROUTE34_HNS", "gPoxOURoute34Hns map")
check("SPECIES_DITTO" in {m["species"] for m in entries.get("gPoxOURoute34Hns", {}).get("land_mons", {}).get("mons", [])},
      "Route 34 grass has no Ditto")

header = (ROOT / "src/data/plastic_ox_pu_encounters.h").read_text()
for symbol, times, tier, cap in [("sPoxRoute34Headbutt", A.ROUTE34_HEADBUTT, "OU", 55),
                                 ("sPoxRoute115Headbutt", A.ROUTE115_HEADBUTT, "OU", 55)]:
    for time, (lo, hi, rows) in times.items():
        m = re.search(rf"{symbol}{time}Mons\[\] = \{{(.*?)\n\}};", header, re.S)
        check(m is not None, f"{symbol}{time} missing from header")
        if not m:
            continue
        got = re.findall(r"\{ (\d+), (\d+), SPECIES_(\w+) \}", m[1])
        check([s for *_, s in got] == [s for _r, s in rows], f"{symbol}{time} species {got}")
        check(all((int(a), int(b)) == (lo, hi) and int(b) <= cap for a, b, _ in got),
              f"{symbol}{time} levels")
        w = re.search(rf"{symbol}{time}Weights\[\] = \{{ ([\d, ]+) \}}", header)
        check(w and [int(x) for x in w[1].split(",")] == [r for r, _ in rows], f"{symbol}{time} weights")
        for _r, sp in rows:
            t = tiers.get("SPECIES_" + sp)
            check(t is not None and rank[t] <= rank[tier], f"{symbol}{time} {sp} is {t}")

src = (ROOT / "src/wild_encounter.c").read_text()
for layout, symbol in [("LAYOUT_ROUTE34_HNS", "sPoxRoute34Headbutt"),
                       ("LAYOUT_ROUTE115", "sPoxRoute115Headbutt")]:
    check(re.search(rf"case {layout}:\s*return night \? &{symbol}Night : &{symbol}Day;", src),
          f"GetHeadbuttTable has no {layout} case")

route115 = json.loads((ROOT / "data/maps/Route115/map.json").read_text())
check(any(b.get("script") == "PlasticOx_EventScript_HeadbuttTree" and (b["x"], b["y"]) == (20, 66)
          for b in route115["bg_events"]), "Route 115 headbutt tree bg event missing")

# The progression model sees the new acquisitions at the right checkpoints.
for sp in ("SPECIES_CHANSEY", "SPECIES_HERACROSS"):
    check(sp not in P.acquired_at("mossdeep"), f"{sp} credited before Saffron opens")
for sp in ("SPECIES_CHANSEY", "SPECIES_HERACROSS", "SPECIES_DITTO"):
    check(sp in P.acquired_at("saffron"), f"{sp} not credited at saffron")

if fails:
    print("FAIL route34/115 encounters:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("PASS route34/115 encounters")
