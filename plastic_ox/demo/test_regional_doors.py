#!/usr/bin/env python3
"""Enter upgraded buildings and require the ordinary animated-door task."""
import json
from test_story import StoryGame, ROOT
from walklib import K

CASES = [
    ("OldaleTown", 5, 7, "OldaleTown_House1"),
    ("OldaleTown", 6, 16, "OldaleTown_PokemonCenter_1F"),
    ("OldaleTown", 14, 6, "OldaleTown_Mart"),
    ("RustboroCity", 13, 30, "RustboroCity_Flat1_1F"),
    ("RustboroCity", 33, 19, "RustboroCity_House1"),
    ("MossdeepCity", 28, 9, "MossdeepCity_House1"),
    ("MossdeepCity", 64, 15, "MossdeepCity_SpaceCenter_1F"),
    ("Route119", 33, 109, "Route119_House"),
    ("BattleFrontier_OutsideWest", 11, 38, "BattleFrontier_BattleFactoryLobby"),
    ("BattleFrontier_OutsideEast", 16, 14, "BattleFrontier_BattleTowerLobby"),
]


def main():
    game = StoryGame()
    game.flag("FLAG_POX_STORY_STARTER", True)
    game.flag("FLAG_ADVENTURE_STARTED", True)
    game.flag("FLAG_SYS_GAME_CLEAR", True)
    groups = json.loads((ROOT / "data/maps/map_groups.json").read_text())
    ids = {name: (i, j) for i, group in enumerate(groups["group_order"]) for j, name in enumerate(groups[group])}
    out = ROOT / "plastic_ox/demo/shots/regional_styles/doors"
    out.mkdir(parents=True, exist_ok=True)
    for name, x, y, destination in CASES:
        game.warp(name, x, y + 1)
        animated = False
        game.core.set_keys(K.KEY_UP)
        for frame in range(100):
            game.frame()
            tasks = game.syms["gTasks"]
            active = any(game.u8(tasks + i * 40 + 4) and
                         game.u32(tasks + i * 40) & ~1 == game.syms["Task_AnimateDoor"] & ~1
                         for i in range(16))
            if active and not animated:
                game.fb.to_pil().convert("RGB").save(out / f"{name}_{x}_{y}.png")
            animated |= active
        game.core.clear_keys(K.KEY_UP)
        game.frame(180)
        state = game.state()
        assert (state["group"], state["num"]) == ids[destination], (name, state)
        assert animated, (name, x, y, "door opened without an animation")
        print(name, x, y, "animated entry PASS", flush=True)


if __name__ == "__main__":
    main()
