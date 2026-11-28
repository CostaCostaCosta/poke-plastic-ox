#!/usr/bin/env python3
"""Install the Route 34 (Little Cup) and Route 115 (OU) encounter tables.

Route 34 is the OU road north out of Saffron (it replaced the empty Route 5):
Saffron -> Route 34 -> Route 115 -> Meteor Falls -> Blackthorn, open once the
Space Center flag opens Saffron. Its grass carries the late game's wild Ditto,
and its nine MB_HEADBUTT_TREE tiles get their own Headbutt table.

Route 115 is the post-Mossdeep OU road to Meteor Falls and Blackthorn. Its
tables were vanilla Emerald (Lv. 23-26); this rescales them to the OU band and
adds the late game's Chansey (grass, 5%) and Heracross (Headbutt, 10%).
Route 115 has no Headbutt tiles, so region_v7.py places a
PlasticOx_EventScript_HeadbuttTree bg event on one tree.

Headbutt tables go in src/data/plastic_ox_pu_encounters.h (selected by layout
in GetHeadbuttTable(), src/wild_encounter.c). Every table carries explicit
weights, so the rates below are exact.

Run after apply_pu_v1.py and apply_nu_v1.py (apply_pu_v1 rewrites the header).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON = ROOT / "src/data/wild_encounters.json"
HEADER = ROOT / "src/data/plastic_ox_pu_encounters.h"

OWNED_MAPS = ("MAP_ROUTE34_HNS", "MAP_ROUTE115")

# ------------------------------------------------------------------ Route 34
ROUTE34_GRASS = (44, 48, [(20, "DITTO"), (15, "GRANBULL"), (15, "HYPNO"),
                          (10, "KADABRA"), (10, "RATICATE"), (10, "PIDGEOT"),
                          (10, "FURRET"), (5, "NIDORINA"), (5, "NIDORINO")])
ROUTE34_SURF = (44, 48, [(40, "TENTACRUEL"), (25, "QUAGSIRE"), (20, "PELIPPER"),
                         (15, "LANTURN")])
ROUTE34_FISHING = (40, 48, [(25, "OCTILLERY"), (20, "QWILFISH"), (15, "GYARADOS"),
                            (15, "SEAKING"), (15, "KINGLER"), (10, "CORSOLA")])
ROUTE34_HEADBUTT = {
    "Day":   (44, 48, [(30, "LEDIAN"), (25, "FEAROW"), (15, "NOCTOWL"),
                       (15, "BEAUTIFLY"), (15, "ARIADOS")]),
    "Night": (44, 48, [(30, "NOCTOWL"), (25, "ARIADOS"), (15, "LEDIAN"),
                       (15, "DUSTOX"), (15, "FEAROW")]),
}

# ----------------------------------------------------------------- Route 115
ROUTE115_GRASS = (46, 50, [(20, "SWELLOW"), (15, "MACHOKE"), (15, "ALTARIA"),
                           (15, "WIGGLYTUFF"), (10, "TAUROS"), (10, "HARIYAMA"),
                           (10, "PELIPPER"), (5, "CHANSEY")])
ROUTE115_SURF = (45, 50, [(40, "TENTACRUEL"), (30, "PELIPPER"), (20, "MANTINE"),
                          (10, "WAILORD")])
# One weighted pool for every rod (the weights bypass rod-slot selection).
ROUTE115_FISHING = (40, 50, [(25, "TENTACRUEL"), (20, "SHARPEDO"), (15, "WAILORD"),
                             (15, "GYARADOS"), (10, "CORSOLA"), (10, "SEADRA"),
                             (5, "LANTURN")])
ROUTE115_HEADBUTT = {
    "Day":   (46, 50, [(25, "EXEGGUTOR"), (20, "LEDIAN"), (20, "AIPOM"),
                       (15, "KECLEON"), (10, "NOCTOWL"), (10, "HERACROSS")]),
    "Night": (46, 50, [(30, "NOCTOWL"), (20, "ARIADOS"), (15, "EXEGGUTOR"),
                       (15, "KECLEON"), (10, "AIPOM"), (10, "HERACROSS")]),
}

HEADBUTT = {"sPoxRoute34Headbutt": ROUTE34_HEADBUTT,
            "sPoxRoute115Headbutt": ROUTE115_HEADBUTT}


def table(data, slots):
    """A weighted table in the engine's JSON shape, padded out to `slots`."""
    lo, hi, rows = data
    assert sum(r for r, _ in rows) == 100, rows
    mons = [{"min_level": lo, "max_level": hi, "species": "SPECIES_" + sp} for _r, sp in rows]
    weights = [r for r, _sp in rows]
    while len(mons) < slots:               # legacy consumers index all slots
        mons.append(dict(mons[-1]))
        weights.append(0)
    return {"encounter_rate": 20, "mons": mons, "weights": weights}


def install(data):
    group = data["wild_encounter_groups"][0]
    entries = [e for e in group["encounters"] if e["map"] not in OWNED_MAPS]
    # No time-of-day suffix: one table serves every time of day (fallback).
    ours = [{"map": "MAP_ROUTE34_HNS",
             "base_label": "gPoxOURoute34Hns",
             "land_mons": table(ROUTE34_GRASS, 12),
             "water_mons": table(ROUTE34_SURF, 5),
             "fishing_mons": table(ROUTE34_FISHING, 10)},
            {"map": "MAP_ROUTE115",
             "base_label": "gPoxOURoute115",
             "land_mons": table(ROUTE115_GRASS, 12),
             "water_mons": table(ROUTE115_SURF, 5),
             "fishing_mons": table(ROUTE115_FISHING, 10)}]
    # build_story keeps Ruins of Alph then Victory Road at the tail
    # (ruins_of_alph.install, league.install); slot ours in before both.
    at = next((i for i, e in enumerate(entries)
               if e["base_label"].startswith("gPoxUURuinsOfAlph")
               or e["base_label"] == "gPoxVictoryRoadOutdoor"), len(entries))
    entries[at:at] = ours
    group["encounters"] = entries
    return data


def headbutt_lines(symbol, data):
    lo, hi, rows = data
    assert sum(r for r, _ in rows) == 100, rows
    yield f"static const struct WildPokemon {symbol}Mons[] = {{"
    for _r, sp in rows:
        yield f"    {{ {lo}, {hi}, SPECIES_{sp} }},"
    yield "};"
    yield f"static const u8 {symbol}Weights[] = {{ " + ", ".join(str(r) for r, _ in rows) + " };"
    yield (f"static const struct WildPokemonInfo {symbol} = {{ 20, {symbol}Mons, "
           f"{symbol}Weights, ARRAY_COUNT({symbol}Mons) }};")


def write_headbutt_tables():
    """Append (or leave in place) each Headbutt pair in the shared header."""
    text = HEADER.read_text()
    lines = []
    for base, times in HEADBUTT.items():
        for time, data in times.items():
            block = "\n".join(headbutt_lines(base + time, data))
            # Replace an existing table in place (Route 34 moved LC -> OU).
            pat = re.compile(rf"static const struct WildPokemon {base}{time}Mons\[\] = \{{.*?"
                             rf"static const struct WildPokemonInfo {base}{time} = [^\n]*\n", re.S)
            if pat.search(text):
                text = pat.sub(lambda _m: block + "\n", text)
            else:
                lines.append(block)
    HEADER.write_text(text.rstrip("\n") + "\n" + "".join(l + "\n" for l in lines))


def main():
    JSON.write_text(json.dumps(install(json.loads(JSON.read_text())), indent=2) + "\n")
    write_headbutt_tables()


if __name__ == "__main__":
    main()
