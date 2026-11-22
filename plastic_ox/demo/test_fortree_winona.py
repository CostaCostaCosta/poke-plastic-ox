#!/usr/bin/env python3
"""Winona's fixed Fortree Gym team, checked in the running ROM.

Talks to Winona in FortreeCity_Gym with badges 1-3 and the Weather Institute
done, waits for TRAINER_PLASTIC_OX_WINONA's battle, then decodes the enemy
party from EWRAM: six Pokemon, the requested species in order, all Lv36,
none shiny, and IVs whose parity gives Hidden Power Electric (Octillery) and
Hidden Power Flying (Poliwrath). Run after building pokeemerald.gba.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_story import StoryGame  # noqa: E402
from walklib import K  # noqa: E402

TRAINER = "TRAINER_PLASTIC_OX_WINONA"
# national dex ids (pokeemerald-expansion keeps Gen 1-3 in dex order)
EXPECTED = [("Octillery", 224, 36), ("Aggron", 306, 36), ("Camerupt", 323, 36),
            ("Clefable", 36, 36), ("Poliwrath", 62, 36), ("Xatu", 178, 36)]
HP_TYPES = ("Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel",
            "Fire", "Water", "Grass", "Electric", "Psychic", "Ice", "Dragon", "Dark")
WANT_HP = {"Octillery": "Electric", "Poliwrath": "Flying"}
SHINY_ODDS = 8


def hidden_power(ivs_box_order: list[int]) -> str:
    # box order: hp, atk, def, spe, spa, spd == the Hidden Power bit order
    bits = sum((iv & 1) << i for i, iv in enumerate(ivs_box_order))
    return HP_TYPES[bits * 15 // 63]


def main() -> None:
    g = StoryGame()
    g.run("Pox_Treecko")
    for name in ("FLAG_POX_STORY_STARTER", "FLAG_ADVENTURE_STARTED", "FLAG_BADGE01_GET",
                 "FLAG_BADGE02_GET", "FLAG_BADGE03_GET", "FLAG_POX_STORY_WEATHER"):
        g.flag(name, True)
    assert not g.flag("FLAG_BADGE04_GET")
    g.warp("FortreeCity_Gym", 15, 3)
    g.frame(30)
    g.hold(K.KEY_UP, 2)
    g.frame(12)
    for _ in range(120):
        g.tap(K.KEY_A, hold=2, wait=10)
        if g.u32(g.syms["gBattleTypeFlags"]) & 8:
            break
    else:
        g.shot("/tmp/pox_winona_failed.png")
        raise AssertionError("Winona's trainer battle never started")
    g.frame(180)
    trainer_id = g.u16(g.syms["gTrainerBattleParameter"] + 2)
    assert trainer_id == g.const(TRAINER), (trainer_id, TRAINER)
    count = g.u8(g.u32(g.syms["gEnemyPartyCountPtr"]))
    assert count == 6, ("enemy party", count)
    stride = g.sizes["gParties"] // 24
    base = g.u32(g.syms["gEnemyPartyPtr"]) if "gEnemyPartyPtr" in g.syms else g.syms["gParties"] + 6 * stride
    for slot, (name, species, level) in enumerate(EXPECTED):
        mon = base + slot * stride
        got = g.box_species(mon)
        assert got == species, (slot, name, got)
        got_level = g.u8(mon + 84)
        assert got_level == level, (name, got_level, level)
        pid, otid = g.u32(mon), g.u32(mon + 4)
        value = (pid >> 16) ^ (pid & 0xFFFF) ^ (otid >> 16) ^ (otid & 0xFFFF)
        shiny = (value < SHINY_ODDS) ^ ((g.u16(mon + 30) >> 14) & 1)
        assert not shiny, (name, "unexpectedly shiny")
        ivs = g.box_ivs(mon)
        if name in WANT_HP:
            assert hidden_power(ivs) == WANT_HP[name], (name, ivs, hidden_power(ivs))
        print(f"  ok  {name} Lv{level} not shiny IVs={ivs}"
              + (f" HP {hidden_power(ivs)}" if name in WANT_HP else ""), flush=True)
    print("\nPASS: Winona battles with her fixed Lv36 non-shiny six and correct Hidden Power types")


if __name__ == "__main__":
    main()
