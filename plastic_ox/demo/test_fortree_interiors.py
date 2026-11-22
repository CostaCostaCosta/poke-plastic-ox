#!/usr/bin/env python3
"""Fortree riggers' house and the Route 119 wild table.

Static part: every species in Route 119's land/water/fishing tables is legal
at the 'fortree' (RU) checkpoint, apart from the fishing-only Magikarp/Feebas
lines that every Plastic Ox water table carries; Linoone is in neither Route 119
nor Route 117.
Emulator part (mGBA): FortreeCity_House2 no longer runs the Hidden Power TM
coin game or the Sleep Talk tutor. The span keeper and the old rigger speak
their own lines (the keeper changes after badge 4), nothing is added to the
bag, and the door is walked out to Fortree and back in.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "plastic_ox/tools"))

FISH_EXEMPT = {"SPECIES_MAGIKARP", "SPECIES_FEEBAS"}


def static_checks() -> None:
    import pox_progression as P
    allowed = P.tiers_unlocked("fortree")
    data = json.loads((ROOT / "src/data/wild_encounters.json").read_text())
    tables = {e["base_label"]: e for e in data["wild_encounter_groups"][0]["encounters"]}
    for label in ("gRoute119", "gRoute117"):
        e = tables[label]
        for field in P.FIELDS:
            for m in e.get(field, {}).get("mons", []):
                sp = m["species"]
                assert sp != "SPECIES_LINOONE", (label, field)
                if label == "gRoute119" and not (field == "fishing_mons" and sp in FISH_EXEMPT):
                    assert P.tier_of(sp) in allowed, (label, field, sp, P.tier_of(sp))
    print("  ok  Route 119 wild species are RU-legal; no Linoone on Routes 117/119")


def emulator_checks() -> None:
    from test_sudowoodo_v1 import SudoGame, talk, settle
    from walklib import K

    groups = json.loads((ROOT / "data/maps/map_groups.json").read_text())

    def map_id(name):
        for i, group in enumerate(groups["group_order"]):
            if name in groups[group]:
                return i, groups[group].index(name)
        raise KeyError(name)

    def on(name):
        st = g.state()
        return st is not None and (st["group"], st["num"]) == map_id(name)

    g = SudoGame()
    g.run("Pox_Treecko")
    for name in ("FLAG_POX_STORY_STARTER", "FLAG_ADVENTURE_STARTED",
                 "FLAG_BADGE01_GET", "FLAG_BADGE02_GET", "FLAG_BADGE03_GET"):
        g.flag(name, True)

    g.warp("FortreeCity_House2", 2, 4)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    text = " ".join(r["text"])
    assert "span ledger" in text and "coin" not in text, r["text"]
    assert not g.flag("FLAG_RECEIVED_TM_HIDDEN_POWER")
    print("  ok  span keeper: ledger line, no Hidden Power coin game, no TM")

    g.flag("FLAG_BADGE04_GET", True)
    r = talk(g, K.KEY_UP)
    text = " ".join(r["text"])
    assert "load removed" in text, r["text"]
    print("  ok  span keeper changes after badge 4")

    settle(g)
    g.warp("FortreeCity_House2", 6, 4)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    text = " ".join(r["text"])
    assert "knots" in text and "teach" in text, r["text"]
    assert not any("Which" in t and "move" in t for t in r["text"]), r["text"]
    print("  ok  old rigger: own line, no tutor menu")

    settle(g)
    g.warp("FortreeCity_House2", 3, 4)
    g.frame(60)
    for _ in range(3):
        g.tap(K.KEY_DOWN, hold=8, wait=40)
        g.frame(60)
        if on("FortreeCity"):
            break
    g.frame(120)
    assert on("FortreeCity"), g.describe()
    print("  ok  walked out of the riggers' house:", g.describe())
    for _ in range(3):
        g.tap(K.KEY_UP, hold=8, wait=40)
        g.frame(60)
        if on("FortreeCity_House2"):
            break
    g.frame(120)
    assert on("FortreeCity_House2"), g.describe()
    print("  ok  walked back in:", g.describe())


if __name__ == "__main__":
    static_checks()
    if "--static" not in sys.argv:
        emulator_checks()
    print("PASS test_fortree_interiors")
