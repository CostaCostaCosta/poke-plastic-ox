#!/usr/bin/env python3
"""No duplicated NPC dialogue, dialogue that fits the sprite, Gabby & Ty on Kecleon.

Static part: plastic_ox/tools/audit_npc_dialogue.py finds no two NPCs sharing a
line across every Plastic Ox map and no sprite/dialogue mismatch.
Emulator part (mGBA, needs pokeemerald.gba): talks to the reworked NPCs in the
real ROM and checks what is printed: the Weather Institute child is on a field
trip, Space Center staff speak their own lines, Fortree's GABBY and TY are
filming the invisible KECLEON (not waiting to interview the Gym winner), and the
three road-closure guards in Lavender each say something different.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))


def static_checks() -> None:
    r = subprocess.run([sys.executable, "plastic_ox/tools/audit_npc_dialogue.py"], cwd=ROOT,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:]
    print("  ok  " + r.stdout.strip().splitlines()[-1])


def emulator_checks() -> None:
    from test_sudowoodo_v1 import SudoGame as StoryGame
    from test_sudowoodo_v1 import talk
    from walklib import K

    g = StoryGame()
    g.run("Pox_Treecko")
    for name in ("FLAG_POX_STORY_STARTER", "FLAG_ADVENTURE_STARTED", "FLAG_POX_TRIGGERS_ENABLED"):
        g.flag(name, True)

    stride = g.sizes['gObjectEvents'] // 16

    def obj_tile(local_id):
        for i in range(16):
            a = g.syms['gObjectEvents'] + i * stride
            if g.u8(a) & 1 and g.u8(a + 8) == local_id:
                return g.s16(a + 0x10) - 7, g.s16(a + 0x12) - 7
        return None

    DIRS = {(0, -1): K.KEY_UP, (0, 1): K.KEY_DOWN, (-1, 0): K.KEY_LEFT, (1, 0): K.KEY_RIGHT}

    def said(mapname, x, y, key, *fragments, wanderer=None):
        g.warp(mapname, x, y)
        g.frame(8 if wanderer is not None else 60)
        if wanderer is not None:
            # Wandering NPC: wait until it steps next to the player, then face it.
            for _ in range(20):
                s = g.state()
                t = obj_tile(wanderer)
                d = t and (t[0] - s["x"], t[1] - s["y"])
                if d in DIRS:
                    key = DIRS[d]
                    break
                g.warp(mapname, x, y)
                g.frame(8)
        r = talk(g, key)
        text = " ".join(r["text"]).replace("\\n", " ").replace("{page}", " ").replace("{scroll}", " ")
        text = " ".join(text.split())
        for frag in fragments:
            assert frag in text, (mapname, x, y, frag, r["text"])
        return text

    said("Route119_WeatherInstitute_1F", 14, 12, K.KEY_UP, "school field trip", "weather balloon", wanderer=5)
    print("  ok  Weather Institute child talks about a field trip, not field researchers")
    said("MossdeepCity_SpaceCenter_2F", 6, 3, K.KEY_UP, "telescope", "cookie")
    said("MossdeepCity_SpaceCenter_1F", 6, 7, K.KEY_UP, "rocket parts")
    print("  ok  Space Center visitors and staff each have their own line")

    t = said("FortreeCity", 36, 10, K.KEY_UP, "GABBY", "KECLEON", "camera")
    assert "interview" not in t.lower() and "WINONA" not in t, t
    said("FortreeCity", 37, 10, K.KEY_UP, "TY", "empty", "rope")
    print("  ok  Fortree GABBY and TY are filming the invisible KECLEON")

    lines = {said("LavenderTown_hns", x, 23, K.KEY_DOWN) for x in (13, 14, 15)}
    assert len(lines) == 3, lines
    print("  ok  Lavender road-closure guards say three different lines")


if __name__ == "__main__":
    static_checks()
    emulator_checks()
    print("test_npc_dialogue: all passed")
