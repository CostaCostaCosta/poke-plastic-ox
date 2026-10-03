#!/usr/bin/env python3
"""Check opening trainer encounters, level floors, held items, and prize money."""
import struct

from test_goldenrod import money
from test_qol import opcode
from test_story import StoryGame
from test_trainer_recovery import item
from test_training_kit import run_code
from walklib import K


# Warp one step outside each trainer's sight line, then cross it in the ROM.
TRAINERS = (
    ("Route29_hns", 35, 26, K.KEY_UP, "TRAINER_PLASTIC_OX_ROUTE29"),
    ("Route29_hns", 56, 20, K.KEY_LEFT, "TRAINER_PLASTIC_OX_ROUTE29_ELLA"),
    ("Route2_Frlg", 10, 77, K.KEY_UP, "TRAINER_PLASTIC_OX_ROUTE2_BEN"),
    ("Route2_Frlg", 10, 12, K.KEY_LEFT, "TRAINER_PLASTIC_OX_ROUTE2_WADE"),
    ("Route2_Frlg", 12, 15, K.KEY_RIGHT, "TRAINER_PLASTIC_OX_ROUTE2_HALEY"),
    ("IlexForest_hns", 46, 8, K.KEY_LEFT, "TRAINER_PLASTIC_OX_ROUTE_ILEX"),
    ("IlexForest_hns", 20, 49, K.KEY_UP, "TRAINER_PLASTIC_OX_ROUTE_ILEX_FINN"),
    ("IlexForest_hns", 48, 20, K.KEY_RIGHT, "TRAINER_PLASTIC_OX_ROUTE_ILEX_MAYA"),
    ("Route46_hns", 6, 22, K.KEY_UP, "TRAINER_PLASTIC_OX_ROUTE46"),
    ("Route46_hns", 4, 19, K.KEY_UP, "TRAINER_PLASTIC_OX_ROUTE46_ERIN"),
)


def start_battle(g, map_name, x, y, direction, trainer):
    g.warp(map_name, x, y)
    for _ in range(4):
        g.tap(direction, hold=18, wait=40)
        if g.u32(g.syms["gBattleTypeFlags"]) & 8:
            break
    for _ in range(250):
        if g.u32(g.syms["gBattleTypeFlags"]) & 8:
            break
        g.tap(K.KEY_A, hold=2, wait=10)
    assert g.u32(g.syms["gBattleTypeFlags"]) & 8, (trainer, "battle did not start", g.state())
    assert g.u16(g.syms["gTrainerBattleParameter"] + 2) == g.const(trainer), trainer
    g.frame(180)


def check_trainer(case):
    map_name, x, y, direction, trainer = case
    g = StoryGame()
    g.run("Pox_Squirtle")
    assert not g.flag("FLAG_BADGE06_GET")

    if trainer == "TRAINER_PLASTIC_OX_ROUTE29_ELLA":
        # A second, stronger party member must set the floor before any badges.
        run_code(g, opcode(g, "callnative")
                 + struct.pack("<I", g.syms["ScrCmd_createmon"] | 1)
                 + struct.pack("<BBHHI", 0, 6, 19, 20, 0))
        assert g.count() == 2

    start_battle(g, map_name, x, y, direction, trainer)
    stride = g.sizes["gParties"] // 24
    enemy = g.syms["gParties"] + 6 * stride
    mons = [enemy + i * stride for i in range(6)]
    species = [g.box_species(mon) for mon in mons]
    levels = [g.u8(mon + stride - 16) for mon in mons]
    held = [item(g, mon) for mon in mons]
    assert all(species), (trainer, species)
    assert held == [0] * 6, (trainer, held)
    if trainer == "TRAINER_PLASTIC_OX_ROUTE29_ELLA":
        assert levels == [20] * 6, (trainer, levels)
    if trainer == "TRAINER_PLASTIC_OX_ROUTE2_HALEY":
        # Authored levels remain a floor when the player is weaker.
        assert levels == [10, 9, 10, 9, 9, 9], (trainer, levels)

    # Run the real reward command in this live trainer battle with a won outcome.
    before = money(g)
    g.write(g.syms["gBattleOutcome"], 1)
    g.write(g.syms["gBattlescriptCurrInstr"], g.syms["BattleScript_LocalBattleWonReward"], 4)
    g.write(g.syms["gBattleMainFunc"], g.syms["Cmd_getmoneyreward"] | 1, 4)
    g.frame(1)
    reward = money(g) - before
    assert reward >= 2000, (trainer, reward)
    print(trainer, "six item-free Pokemon, levels", levels, "prize", reward, "PASS", flush=True)


if __name__ == "__main__":
    for case in TRAINERS:
        check_trainer(case)
