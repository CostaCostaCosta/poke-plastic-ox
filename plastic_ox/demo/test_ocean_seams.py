#!/usr/bin/env python3
"""Cross the all-ocean route seams that test_warps_v1.py deliberately skips.

`test_warps_v1.py::_try_seam` refuses lanes whose probe tile is waterish, because
an avatar injected into open ocean cannot walk.  Route 21's North/South seam is
exactly that: every column on both maps is MB_OCEAN_WATER, so the run-3 warp
playtest reported "0 lanes tried" for it in both directions.

This driver puts the avatar on the surfboard (`PLAYER_AVATAR_FLAG_SURFING`, the
first byte of `struct PlayerAvatar`) and walks the seam for real, then walks it
back, so the seam is asserted in-emulator rather than skipped.

    LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
      ~/.venvs/mgba311/bin/python plastic_ox/demo/test_ocean_seams.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "plastic_ox" / "demo"))
sys.path.insert(0, str(ROOT / "plastic_ox" / "alpha"))

import test_warps_v1 as T  # noqa: E402

PLAYER_AVATAR_FLAG_SURFING = 1 << 3
FRAME_BUDGET = 1800


def walk_off(play, name, lane, walk):
    """Hold `walk` from two tiles inside `name` until the map changes."""
    height = play.live_size()[1]
    at = (lane, height - 3) if walk == "DOWN" else (lane, 2)
    ok, note = play.goto(name, *at)
    if not ok:
        return None, f"goto({at[0]},{at[1]}) failed: {note}"
    cur = play.u8(play.symbol_address("gPlayerAvatar"))
    play.write(play.symbol_address("gPlayerAvatar"),
               cur | PLAYER_AVATAR_FLAG_SURFING)
    play.frame(30)
    start = play.state()
    key = T.DIRKEY[walk]
    play.core.set_keys(key)
    for _ in range(FRAME_BUDGET):
        play.frame(1)
        st = play.state()
        if (st["group"], st["num"]) != (start["group"], start["num"]):
            play.core.clear_keys(key)
            return (st["group"], st["num"]), ""
    play.core.clear_keys(key)
    return None, f"held {walk} from ({at[0]},{at[1]}) and stayed on {name}"


def main():
    play = T.make_playtest()
    play.core.set_keys(0)
    failures = []
    # (source map, lane, direction, expected destination map, expected landing)
    legs = [
        ("Route21_North_Frlg", 11, "DOWN", "Route21_South_Frlg", (11, 0)),
        ("Route21_South_Frlg", 11, "UP", "Route21_North_Frlg", (11, 49)),
    ]
    for name, lane, walk, want_name, want_xy in legs:
        play.warp(name, lane, 2 if walk == "UP" else play.live_size()[1] - 3)
        play.frame(60)
        landed, why = walk_off(play, name, lane, walk)
        if landed is None:
            failures.append(f"{name} {walk}: {why}")
            print(f"FAIL {name} {walk}: {why}")
            continue
        play.frame(240)
        st = play.state()
        got = (st["x"], st["y"])
        if got == want_xy:
            print(f"PASS {name} {walk} -> {want_name} at {got}")
        else:
            failures.append(f"{name} {walk}: settled at {got}, expected {want_xy}")
            print(f"FAIL {name} {walk}: settled at {got}, expected {want_xy}")
    print(f"\n{len(failures)} failure(s)")
    for line in failures:
        print("  " + line)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())