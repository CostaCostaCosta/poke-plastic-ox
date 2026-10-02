#!/usr/bin/env python3
"""Install the opening NU encounter block.

Source of truth: plastic_ox/encounter_tables/nu_encounters_v1.md (NU level cap
30). The document specifies four tables that had no data in the ROM:

  * Route 37 grass, Lv. 21-23, a different species per time of day;
  * Route 37 Headbutt, Lv. 21-23 (Kecleon 5%);
  * Ecruteak City Good Rod, Lv. 21-23;
  * Burned Tower 1F, Lv. 22-24.

Burned Tower B1F is specified in the document but the map does not exist yet
(data/maps/PlasticOx_BurnedTower is a single-storey stub on LAYOUT_MT_PYRE_1F
with no warps or connections), so there is nothing to attach a second floor
table to. That gap is reported, not guessed at.

Route 37's Headbutt population goes in src/data/plastic_ox_pu_encounters.h, the
same header the PU generator writes, because Headbutt tables are selected by
layout in src/wild_encounter.c's GetHeadbuttTable() rather than through the
wild-encounter JSON (which has no Headbutt field).

Rates are exact: every table carries an explicit `weights` array, so the engine's
rejection sampler (ChooseWeightedWildMonIndex) reproduces the authored
percentages instead of the fixed land/fishing slot weights.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON = ROOT / "src/data/wild_encounters.json"
HEADER = ROOT / "src/data/plastic_ox_pu_encounters.h"

# Maps this generator owns. Entries for these maps are rebuilt on every run.
NU_MAPS = ("MAP_ROUTE37_HNS", "MAP_ECRUTEAK_CITY_HNS", "MAP_PLASTIC_OX_BURNED_TOWER")

# ---------------------------------------------------------------- Route 37 grass
# The stable 65% population is shared by all three periods; only the last three
# slots change, which is the document's "65% population + 35% Johto times" rule.
ROUTE37_STABLE = [(25, "GROWLITHE"), (15, "VULPIX"), (15, "ROSELIA"), (10, "PLUSLE")]
ROUTE37 = {
    "Morning": (21, 23, ROUTE37_STABLE + [(15, "PIDGEY"), (10, "LEDYBA"), (10, "SPEAROW")]),
    "Day":     (21, 23, ROUTE37_STABLE + [(15, "PIDGEY"), (10, "HOPPIP"), (10, "SPEAROW")]),
    "Night":   (21, 23, ROUTE37_STABLE + [(15, "HOOTHOOT"), (10, "SPINARAK"), (10, "MURKROW")]),
}

# ------------------------------------------------------------- Ecruteak Good Rod
# A single Good Rod table. Like Route 35's Old Rod table it is written as an
# explicit ten-slot weighted pool, which bypasses rod-slot selection; the five
# trailing slots carry weight 0 so only the Good Rod can ever fire. The Old Rod
# is not awarded until Mossdeep and the Super Rod not until the Mossdeep house,
# both long after Morty, so nothing else reaches this water before then.
ECRUTEAK_ROD = (21, 23, [(30, "POLIWAG"), (20, "BARBOACH"), (15, "SURSKIT"),
                        (15, "GOLDEEN"), (10, "WOOPER"), (10, "CORPHISH")])

# ---------------------------------------------------------- Burned Tower 1F
BURNED_TOWER_1F = (22, 24, [(30, "RATTATA"), (15, "KOFFING"), (15, "ZUBAT"), (10, "TORKOAL"),
                           (10, "SLUGMA"), (10, "HOUNDOUR"), (5, "GASTLY"), (5, "RATICATE")])

# ------------------------------------------------------------- Route 37 Headbutt
ROUTE37_HEADBUTT = (21, 23, [(25, "TEDDIURSA"), (20, "SEEDOT"), (15, "SLAKOTH"),
                            (15, "EXEGGCUTE"), (10, "HOOTHOOT"), (10, "PICHU"),
                            (5, "KECLEON")])

HEADBUTT_SYMBOL = "sPoxRoute37Headbutt"


def table(data, slots=12):
    """A weighted table in the engine's JSON shape, padded out to `slots`."""
    lo, hi, rows = data
    mons = [{"min_level": lo, "max_level": hi, "species": "SPECIES_" + sp} for _rate, sp in rows]
    weights = [rate for rate, _sp in rows]
    while len(mons) < slots:               # legacy consumers index all slots
        mons.append(dict(mons[-1]))
        weights.append(0)
    return {"encounter_rate": 20, "mons": mons, "weights": weights}


def install(data):
    group = data["wild_encounter_groups"][0]
    group["encounters"] = [e for e in group["encounters"] if e["map"] not in NU_MAPS]
    add = []

    for time in ("Morning", "Day", "Night"):
        add.append({"map": "MAP_ROUTE37_HNS",
                    "base_label": "gPoxNURoute37Hns_" + time,
                    "land_mons": table(ROUTE37[time])})

    # No time-of-day suffix: the generator files these under TIME_MORNING, which
    # is also OW_TIME_OF_DAY_FALLBACK, so one table serves every time of day.
    add.append({"map": "MAP_ECRUTEAK_CITY_HNS",
                "base_label": "gPoxNUEcruteakCityHns",
                "fishing_mons": table(ECRUTEAK_ROD, slots=10)})

    add.append({"map": "MAP_PLASTIC_OX_BURNED_TOWER",
                "base_label": "gPoxNUBurnedTower1F",
                "land_mons": table(BURNED_TOWER_1F)})

    group["encounters"].extend(add)
    return data


def write_headbutt_table():
    """Append the Route 37 Headbutt pair to the shared Headbutt header."""
    text = HEADER.read_text()
    lines = []
    for time in ("Day", "Night"):         # one table; the document has no time split
        symbol = HEADBUTT_SYMBOL + time
        if symbol in text:
            continue
        lo, hi, rows = ROUTE37_HEADBUTT
        lines.append(f"static const struct WildPokemon {symbol}Mons[] = {{")
        for _rate, sp in rows:
            lines.append(f"    {{ {lo}, {hi}, SPECIES_{sp} }},")
        lines.append("};")
        lines.append(f"static const u8 {symbol}Weights[] = {{ "
                     + ", ".join(str(r) for r, _ in rows) + " };")
        lines.append(f"static const struct WildPokemonInfo {symbol} = {{ 20, {symbol}Mons, "
                     f"{symbol}Weights, ARRAY_COUNT({symbol}Mons) }};")
    if lines:
        HEADER.write_text(text.rstrip("\n") + "\n" + "\n".join(lines) + "\n")


def main():
    JSON.write_text(json.dumps(install(json.loads(JSON.read_text())), indent=2) + "\n")
    write_headbutt_table()


if __name__ == "__main__":
    main()