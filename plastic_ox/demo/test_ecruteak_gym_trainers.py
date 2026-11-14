#!/usr/bin/env python3
"""Verify the four Ecruteak Gym staff NPCs are real trainer battles.

Each NPC in the shadow maze must start a battle with its own trainer id and a
two-or-three Pokemon NU-ceiling party. Run after building pokeemerald.gba.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_story import StoryGame  # noqa: E402
from walklib import K  # noqa: E402

# (script, approach x/y, facing key, trainer constant, expected party size)
CASES = [
    ("Pox_GymKado", 12, 33, K.KEY_RIGHT, "TRAINER_PLASTIC_OX_ECRUTEAK_KADO", 3),
    ("Pox_GymYui", 13, 26, K.KEY_UP, "TRAINER_PLASTIC_OX_ECRUTEAK_YUI", 2),
    ("Pox_GymGenzo", 7, 24, K.KEY_DOWN, "TRAINER_PLASTIC_OX_ECRUTEAK_GENZO", 3),
    ("Pox_GymRin", 5, 15, K.KEY_UP, "TRAINER_PLASTIC_OX_ECRUTEAK_RIN", 3),
]


def main() -> None:
    for script, x, y, facing, trainer, party_size in CASES:
        game = StoryGame()
        game.run("Pox_Treecko")
        game.warp("EcruteakCity_Gym_hns", x, y)
        game.frame(30)
        game.hold(facing, 2)
        game.frame(12)
        for _ in range(120):
            game.tap(K.KEY_A, hold=2, wait=10)
            if game.u32(game.syms["gBattleTypeFlags"]) & 8:
                break
        else:
            game.shot("ecruteak_gym_" + script + "_failed.png")
            raise AssertionError(f"{script}: trainer battle never started")
        game.frame(180)
        trainer_id = game.u16(game.syms["gTrainerBattleParameter"] + 2)
        assert trainer_id == game.const(trainer), (script, trainer_id, trainer)
        party_ptr = game.u32(game.syms["gEnemyPartyCountPtr"])
        count = game.u8(party_ptr)
        assert count == party_size, (script, "enemy party", count, party_size)
        print(f"  ok  {script}: {trainer} with {count} Pokemon", flush=True)
    print("\nPASS: Ecruteak Gym staff all battle with their own parties")


if __name__ == "__main__":
    main()
