#!/usr/bin/env python3
"""Check live DMA destinations contain the imported regional animation frames."""
from test_story import StoryGame


def block(game, address, size):
    if 0x06000000 <= address < 0x06018000:
        return bytes(game.core.memory.vram.u8[address - 0x06000000 + i] for i in range(size))
    return bytes(game.u8(address + i) for i in range(size))


def check(game, name, point, ranges):
    game.warp(name, *point)
    game.frame(120)
    expected = []
    seen = [set() for _ in ranges]
    for tile, size, symbols, skip in ranges:
        expected.append({block(game, game.syms[s] + skip, size) for s in symbols})
    for _ in range(40):
        game.frame(4)
        for i, (tile, size, symbols, skip) in enumerate(ranges):
            value = block(game, 0x06000000 + tile * 32, size)
            assert value in expected[i], (name, tile, "foreign or misplaced animation frame")
            seen[i].add(value)
    for i, values in enumerate(seen):
        assert len(values) > 1, (name, ranges[i][0], "animation is static")
    print(name, "PASS:", [len(x) for x in seen], "distinct imported frames", flush=True)


def main():
    game = StoryGame()
    game.flag("FLAG_POX_STORY_STARTER", True)
    game.flag("FLAG_ADVENTURE_STARTED", True)
    hns = [
        (416, 18 * 32, [f"sJohtoGeneral_Edge_{i}" for i in range(8)], 0),
        (508, 4 * 32, [f"sJohtoGeneral_Flower_{i}" for i in range(5)], 0),
        (450, 12 * 32, [f"sJohtoGeneral_Water_{i}" for i in range(8)], 34 * 32),
    ]
    check(game, "CherrygroveCity_hns", (20, 20), hns)
    check(game, "SaffronCity_hns", (32, 26), hns)
    oras = [
        (432, 30 * 32, [f"gTilesetAnims_HoennOrasGeneral_Water_Frame{i}" for i in range(8)], 0),
        (464, 10 * 32, [f"gTilesetAnims_HoennOrasGeneral_SandWaterEdge_Frame{i}" for i in range(7)], 0),
        (496, 6 * 32, [f"gTilesetAnims_HoennOrasGeneral_Waterfall_Frame{i}" for i in range(4)], 0),
    ]
    check(game, "OldaleTown", (10, 10), oras)
    check(game, "RustboroCity", (26, 38), [
        (512 + 448, 4 * 32, ["sHoennOrasRustboroFountain0", "sHoennOrasRustboroFountain1"], 0),
    ])
    check(game, "NationalPark_Normal_hns", (26, 20), [
        (640 + 88, 0x100, [f"sNationalPark_LargeFountain_{i}" for i in range(4)], 0),
        (640 + 104, 0x100, [f"sNationalPark_SmallFountain_{i}" for i in range(5)], 0),
    ])


if __name__ == "__main__":
    main()
