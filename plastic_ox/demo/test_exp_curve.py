#!/usr/bin/env python3
"""Every species shares one exp curve, and level-ups wait until the battle ends.

1. All gExperienceTables rows in the ROM must match the Medium Fast (n^3) row.
2. Fight a real trainer battle by mashing A. The lead's level must not change
   while the battle is undecided; it must rise once the battle is won.
"""
from test_opening_trainers import start_battle
from test_story import StoryGame
from walklib import K

MAX_LEVEL = 100
NUM_ROWS = 8


def check_tables(g):
    base = g.syms["gExperienceTables"]
    row = (MAX_LEVEL + 1) * 4
    first = [g.u32(base + 4 * n) for n in range(MAX_LEVEL + 1)]
    assert first[:5] == [0, 1, 8, 27, 64], first[:5]
    assert first[MAX_LEVEL] == 1_000_000, first[MAX_LEVEL]
    for r in range(1, NUM_ROWS):
        other = [g.u32(base + r * row + 4 * n) for n in range(MAX_LEVEL + 1)]
        assert other == first, ("growth row differs", r)
    print("all", NUM_ROWS, "growth rows use n^3 PASS", flush=True)


def check_postbattle_levelup(g):
    stride = g.sizes["gParties"] // 24
    lead_level = g.syms["gParties"] + stride - 16
    start_level = g.u8(lead_level)
    start_battle(g, "Route29_hns", 35, 26, K.KEY_UP, "TRAINER_PLASTIC_OX_ROUTE29")
    outcome = g.syms["gBattleOutcome"]
    lay = [g.u32(g.syms["gMetamonTestLayout"] + i * 4) for i in range(16)]
    foe_hp = g.syms["gBattleMons"] + lay[6] + lay[10]
    for _ in range(6000):
        if g.u8(outcome):
            break
        assert g.u8(lead_level) == start_level, ("levelled mid-battle", start_level, g.u8(lead_level))
        # Shorten the fixture only: the foe on the field drops to the first
        # hit, so exp is still earned and banked through the real getexp path.
        if g.u16(foe_hp) > 1:
            g.write(foe_hp, 1, 2)
        g.write(g.syms["gActionSelectionCursor"], 0)
        g.write(g.syms["gMoveSelectionCursor"], 0)
        g.tap(K.KEY_A, hold=1, wait=4)
    if g.u8(outcome) != 1:
        from pox_fixtures import shot
        shot(g, "exp_curve_stuck")
    assert g.u8(outcome) == 1, ("battle not won", g.u8(outcome), g.u32(g.syms["gBattleTypeFlags"]), g.u8(lead_level))
    for _ in range(600):
        if not g.u32(g.syms["gBattleTypeFlags"]) & 8 and g.u8(lead_level) != start_level:
            break
        g.tap(K.KEY_A, hold=2, wait=8)
    end_level = g.u8(lead_level)
    assert end_level > start_level, ("no post-battle level-up", start_level, end_level)
    print("level", start_level, "held during battle, rose to", end_level, "after win PASS", flush=True)


if __name__ == "__main__":
    g = StoryGame()
    g.run("Pox_Squirtle")
    check_tables(g)
    check_postbattle_levelup(g)
