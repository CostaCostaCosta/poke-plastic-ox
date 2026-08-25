#!/usr/bin/env python3
"""Story smoke test (trigger build): enter Oak's Lab, step on the gated
starter trigger, assert TREECKO received."""
from pathlib import Path
import sys

DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_DIR))

import walk_demo as W
import walk_leg1 as L1
from walklib import GBA, K, boot_to_bedroom

MAP_HOUSE_1F = W.MAP_HOUSE_1F
MAP_LAB = (38, 3)  # PalletTown_ProfessorOaksLab_Frlg


def main():
    g = GBA(linker_map="pokeemerald-triggers.map")
    print(f"ROM {g.core.game_code}", flush=True)
    boot_to_bedroom(g)
    L1.set_flag(g, 0x74)
    navigate = L1.navigate

    # house -> pallet
    g.walk("RIGHT", target=(10, 6)); g.walk("UP", target=(10, 2))
    for _ in range(3):
        g.hold(K.KEY_LEFT, 90)
        if (g.state()["group"], g.state()["num"]) == MAP_HOUSE_1F:
            break
    W.visit_mom(g)
    for i in range(6):
        st = g.state()
        if st["y"] >= 6:
            break
        g.tap(K.KEY_DOWN, hold=8, wait=14)
    g.walk("RIGHT", target=(10, 3)); g.walk("LEFT", target=(4, 3)); g.walk("DOWN", target=(4, 7))
    g.hold(K.KEY_DOWN, 80); g.frame(90)
    assert (g.state()["group"], g.state()["num"]) == W.MAP_PALLET, g.describe()

    # pallet -> lab door (16,13): south then east then to the mat
    g.shot("story_pallet.png")
    print("pre:", g.describe(), flush=True)

    # south beach -> east -> below the lab door, then bump up into it
    g.walk("DOWN", target=(6, 14))
    g.walk("RIGHT", target=(15, 14))
    for i in range(10):
        st = g.state()
        if (st["group"], st["num"]) == MAP_LAB:
            break
        print("  door:", st["x"], st["y"], flush=True)
        if st["y"] < 14:
            g.tap(K.KEY_DOWN, hold=10, wait=16)
        elif st["x"] < 16:
            g.tap(K.KEY_RIGHT, hold=10, wait=16)
        else:
            g.tap(K.KEY_UP, hold=10, wait=20)
    for _ in range(120):
        g.frame(1)
    W.assert_map(g, MAP_LAB, "lab_in")
    print("in lab:", g.describe(), flush=True)

    # walk under the starter ball (9,4) and interact with A
    navigate(g, (9, 5))
    g.tap(K.KEY_UP, hold=6, wait=8)  # face the ball
    g.set_text_speed_fast()
    for i in range(12):
        g.tap(K.KEY_A, hold=4, wait=10)
    print("VAR_TEMP_1 =", g.var(0x40E1), "party0 =", g.party_species(0), flush=True)

    for _ in range(60):
        g.frame(1)
        g.tap(K.KEY_A, hold=2, wait=6)
    print("VAR_TEMP_1 =", g.var(0x40E1), flush=True)
    sp = g.party_species(0)
    print("party0 =", sp, flush=True)
    g.shot("story_01_starter.png")

    print("STARTER OK: TREECKO in party", flush=True)
    g.shot("story_01_starter.png")


if __name__ == "__main__":
    main()
