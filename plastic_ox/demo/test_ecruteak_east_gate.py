#!/usr/bin/env python3
"""Ecruteak east exit (Route 42 / Route 119 gate) is shut until MORTY's badge.

Column x=55, y=40..43 is the only approach to the gate door at (55,42); the
GateWatch policeman stands on (54,42). Before FLAG_BADGE03_GET every route onto
that column (from x=54, y=40..43) must bounce the player back; afterwards each
one must reach Gate_EcruteakCity_Route42_hns.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_story import StoryGame  # noqa: E402
from walklib import K  # noqa: E402

GROUPS = json.loads((ROOT / "data/maps/map_groups.json").read_text())
IDS = {m: (i, j) for i, g in enumerate(GROUPS["group_order"]) for j, m in enumerate(GROUPS[g])}
GATE = IDS["Gate_EcruteakCity_Route42_hns"]
CITY = IDS["EcruteakCity_hns"]
STARTS = [(54, 40), (54, 41), (54, 43)]


def loc(g):
    s = g.state()
    return (s["group"], s["num"]), s.get("x"), s.get("y")


def attempt(g, sx, sy):
    """Try to reach (55,42) from (sx,sy): step right, then along the column.

    The door is an arrow warp, so the player must press RIGHT while on it.
    """
    g.warp("EcruteakCity_hns", sx, sy)
    g.frame(60)
    vert = K.KEY_DOWN if sy < 42 else K.KEY_UP
    seen_gate = False
    for key in [K.KEY_RIGHT] + [vert] * abs(42 - sy) + [K.KEY_RIGHT] * 3:
        g.hold(key, 16)
        g.frame(30)
        for _ in range(6):  # dismiss any guard message
            g.hold(K.KEY_A, 4)
            g.frame(20)
        if loc(g)[0] == GATE:
            seen_gate = True
            break
    return seen_gate


def fresh(badge):
    g = StoryGame()
    g.flag("FLAG_POX_STORY_STARTER", True)
    g.flag("FLAG_ADVENTURE_STARTED", True)
    g.flag("FLAG_POX_STORY_BURNED_TOWER", True)
    g.flag("FLAG_BADGE03_GET", badge)
    return g


def main():
    g = fresh(False)
    for sx, sy in STARTS:
        assert not attempt(g, sx, sy), f"slipped past the east gate guard from {(sx, sy)}"
        where = loc(g)
        assert where[0] == CITY and where[1] is not None and where[1] <= 54, ("not bounced back", sx, sy, where)
        print(f"  ok  blocked before badge from {(sx, sy)} -> {where}")
    # Directly in front of the guard: he must not move aside.
    assert not attempt(g, 53, 42), "walked through the guard at (54,42)"
    print("  ok  guard tile (54,42) blocks")

    g = fresh(True)
    for sx, sy in STARTS + [(53, 42)]:
        assert attempt(g, sx, sy), f"east gate still shut after badge from {(sx, sy)}: {loc(g)}"
        print(f"  ok  open after badge from {(sx, sy)}")
    print("\nPASS: Ecruteak east gate is airtight before MORTY and open after")


if __name__ == "__main__":
    main()
