#!/usr/bin/env python3
"""Smoke-test the normal ROM's Pallet opening through arrival in Oldale."""

import sys
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_DIR))

from test_region_walk import cross, current, navigate
from test_story import StoryGame
from walklib import K


def main():
    game = StoryGame(build="")
    assert game.flag("FLAG_POX_TRIGGERS_ENABLED"), "normal ROM did not enable the authored story"

    game.warp("PalletTown_ProfessorOaksLab_Frlg", 6, 11)
    for _ in range(600):
        game.tap(K.KEY_A, hold=2, wait=10)
        if game.flag("FLAG_POX_LAB_INTRO") and game.u8(game.syms["sGlobalScriptContextStatus"]) == 2:
            break
    else:
        raise AssertionError("lab professor introduction did not finish")

    game.run("Pox_Squirtle")
    assert game.count() == 1 and game.party_species() == 7, "starter choice did not complete"
    assert game.flag("FLAG_POX_STARTER_SUPPLIES"), "Oak did not give supplies"
    assert game.flag("FLAG_POX_ELM_EXP_ALL"), "Elm did not give EXP Share"
    assert game.flag("FLAG_POX_ELM_TMS"), "Birch did not finish giving machines"
    pocket = game.syms["gBagPockets"] + 2 * (game.sizes["gBagPockets"] // 5)
    slots = game.u32(pocket)
    machines = {game.u16(slots + 4 * i) for i in range(64)}
    assert set(range(582, 632)).issubset(machines), "missing starter TMs"
    # HM01-HM08, except the retired HM05 (Flash).
    assert {682, 683, 684, 685, 687, 688, 689}.issubset(machines), "missing starter HMs"
    assert 686 not in machines, "retired HM Flash was granted"

    game.warp("PalletTown_Frlg", 13, 10)
    game.test_water = False
    for destination in ("Route101", "OldaleTown"):
        navigate(game, lambda x, y: y == 0 and game.collision_at(x, y)[0] == 0)
        cross(game, "N", destination)

    assert current(game) == "OldaleTown"
    print("NORMAL ROM: professor intro, starter choice, Pallet -> Route101 -> Oldale PASS", flush=True)


if __name__ == "__main__":
    main()
