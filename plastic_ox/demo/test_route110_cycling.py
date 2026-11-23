#!/usr/bin/env python3
"""Route 110 cycling challenge: a clean run under 12.10 s gives the Mt. Moon
tablet the player passed up (ice <-> rock), once.

    plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_route110_cycling.py

Setup writes emulator RAM only (bag, timer, collisions); never ROM or saves.
"""
import os
import subprocess

from test_story import StoryGame, ROOT
from test_sudowoodo_v1 import const, give_item, bag

ICE = const('ITEM_ANCIENT_ICE_TABLET', 'items.h')
ROCK = const('ITEM_ANCIENT_ROCK_TABLET', 'items.h')
NM = os.path.join(os.environ.get('DEVKITARM', ''), 'bin/arm-none-eabi-nm')


def static_symbol(name):
    out = subprocess.run([NM if os.path.exists(NM) else 'arm-none-eabi-nm', str(ROOT / 'pokeemerald.elf')],
                         capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[2] == name:
            return int(parts[0], 16)
    raise KeyError(name)


TIMER = static_symbol('sBikeCyclingTimer')


def finish_run(start_items, frames, collisions):
    g = StoryGame()
    g.warp('Route110', 15, 20)
    for item in start_items:
        give_item(g, item)
    g.write(g.syms['gBikeCollisions'], collisions)
    # Begin the script, then back-date the timer so the special sees ~frames.
    now = g.u32(g.syms['gMain'] + 0x20)
    g.write(TIMER, (now - frames) & 0xFFFFFFFF, 4)
    g.run('Route110_EventScript_CyclingChallengeEnd')
    return bag(g, ICE), bag(g, ROCK)


def main():
    # The challenge script reaches the special within a few frames; leave margin.
    cases = [
        ([ICE], 600, 0, (1, 1)),     # fast and clean: gets the rock tablet
        ([ROCK], 600, 0, (1, 1)),    # gets the ice tablet
        ([ICE], 600, 1, (1, 0)),     # one collision: nothing
        ([ICE], 760, 0, (1, 0)),     # 12.66 s: too slow
        ([ICE, ROCK], 600, 0, (1, 1)),  # already has both: no duplicate
        ([], 600, 0, (0, 0)),        # skipped Mt. Moon: nothing
    ]
    for items, frames, hits, expected in cases:
        got = finish_run(items, frames, hits)
        assert got == expected, (items, frames, hits, got, expected)
        print('PASS', items, frames, hits, got, flush=True)
    print('Route 110 cycling tablet reward PASS')


if __name__ == '__main__':
    main()
