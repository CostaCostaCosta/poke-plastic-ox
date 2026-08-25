#!/usr/bin/env python3
"""Story smoke test (trigger build): enter Oak's Lab, step on the gated
starter trigger, assert TREECKO received + story flag set."""
from pathlib import Path
import sys

DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_DIR))

import walk_demo as W
import walk_leg1 as L1
from walklib import GBA, K, boot_to_bedroom

MAP_HOUSE_1F = W.MAP_HOUSE_1F
MAP_PALLET = W.MAP_PALLET
MAP_LAB = (38, 3)  # PalletTown_ProfessorOaksLab_Frlg


def main():
    g = GBA(linker_map="pokeemerald-triggers.map")
    print(f"ROM {g.core.game_code}", flush=True)
    boot_to_bedroom(g)
    L1.set_flag(g, 0x74)
    g.walk("RIGHT", target=(10, 6)); g.walk("UP", target=(10, 2))
    for _ in range(3):
        g.hold(K.KEY_LEFT, 90)
        if (g.state()["group"], g.state()["num"]) == MAP_HOUSE_1F:
            break
    W.visit_mom(g)
    g.walk("RIGHT", target=(10, 3)); g.walk("LEFT", target=(4, 3)); g.walk("DOWN", target=(4, 7))
    g.hold(K.KEY_DOWN, 80); g.frame(90)
    navigate = L1.navigate
    assert (g.state()["group"], g.state()["num"]) == W.MAP_PALLET, g.describe()
    for i in range(8):
        if g.state()["y"] >= 10: break
        g.tap(K.KEY_DOWN, hold=10, wait=16)
    for i in range(16):
        st = g.state()
        if st["x"] >= 15: break
        if st["x"] < 15: g.tap(K.KEY_RIGHT, hold=10, wait=16)
    for i in range(8):
        if g.state()["y"] >= 14: break
        g.tap(K.KEY_DOWN, hold=10, wait=16)
    for i in range(10):
        st = g.state()
        if (st["group"], st["num"]) == MAP_LAB:
            break
        if st["x"] != 16:
            g.tap(K.KEY_RIGHT if st["x"] < 16 else K.KEY_LEFT, hold=8, wait=14)
        else:
            g.tap(K.KEY_UP, hold=10, wait=20)
    for _ in range(120):
        g.frame(1)
    W.assert_map(g, MAP_LAB, "lab_in2")
    print("in lab:", g.describe(), flush=True)
    # walk right to x=9 on the door row, then up onto the trigger tile
    for i in range(30):
        st = g.state()
        if (st["group"], st["num"]) == MAP_LAB and st["x"] == 9 and st["y"] == 11:
            break
        dx = 9 - st["x"]; dy = 11 - st["y"]
        if abs(dx) >= abs(dy) and dx != 0:
            g.tap(K.KEY_RIGHT if dx > 0 else K.KEY_LEFT, hold=10, wait=16)
        elif dy != 0:
            g.tap(K.KEY_UP if dy < 0 else K.KEY_DOWN, hold=10, wait=16)
        else:
            g.tap(K.KEY_RIGHT, hold=8, wait=14)
    else:
        raise AssertionError("never reached trigger column")
    v = g.var(0x40E1)
    print("VAR_TEMP_1 =", v, flush=True)
    sp = g.party_species(0)
    assert sp == 252, f"expected TREECKO(252), got {sp}"
    print("STARTER OK", flush=True)

    for _ in range(60):
        g.frame(1)
        g.tap(K.KEY_A, hold=2, wait=6) if i % 3 == 0 else g.frame(1)
    sp = g.party_species(0)
    assert sp == 252, f"expected TREECKO(252), got {sp}"
    flag = g.u32(g.symbol_address("gSaveBlock1Ptr"))
    print("STARTER OK: party0=252", flush=True)


if __name__ == "__main__":
    main()
