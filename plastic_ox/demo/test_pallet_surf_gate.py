#!/usr/bin/env python3
"""Prove Pallet's south connection is blocked on foot and open via Surf."""

from test_region_walk import GEOMETRY, cross, current, navigate, setup
from walklib import K
from test_camera_seam import check_view


def main():
    pallet = GEOMETRY["PalletTown_Frlg"]
    route = GEOMETRY["Route21_North_Frlg"]
    assert dict(map="MAP_ROUTE21_NORTH", offset=0, direction="down") in pallet.data["connections"]
    assert dict(map="MAP_PALLET_TOWN", offset=0, direction="up") in route.data["connections"]
    assert all(not pallet.passable(x, pallet.h - 1) for x in range(7, 11))
    assert all(pallet.passable(x, pallet.h - 1, water=True) for x in range(7, 11))
    assert all(route.passable(x, 0, water=True) for x in range(7, 11))
    assert {(e["x"], e["y"]) for e in pallet.data["coord_events"] if e["script"] == "PalletTown_SurfToRoute21"} == set()

    game = setup()
    game.flag("FLAG_POX_TRIGGERS_ENABLED", False)
    game.flag("FLAG_BADGE05_GET", True)
    game.test_water = False
    game.warp("PalletTown_Frlg", 12, 18)
    game.hold(K.KEY_DOWN, 96)
    game.frame(120)
    assert current(game) == "PalletTown_Frlg", game.state()
    assert game.state()["y"] == 19, game.state()

    assert not any(e["script"] == "Route21_North_SurfToPallet" for e in route.data["coord_events"])
    for x in range(11, 22):
        assert game.collision_at(x, 20)[0] != 0, ("open land exit", x)

    game.test_water = True
    for lane in range(7, 11):
        game.warp("PalletTown_Frlg", 12, 18)
        navigate(game, lambda x, y: (x, y) == (lane, 18))
        # The camera margin must continue the water beyond the town boundary.
        for y in range(20, 27):
            assert game.metatile_at(lane, y)[0] in (0x12A, 0x12B, 0x12C)
        game.shot(f"pallet_south_approach_{lane}.png")
        cross(game, "S", "Route21_North_Frlg")
        assert game.state()["x"] == lane, game.state()
        check_view(game, f"pallet_south_route_{lane}")
        navigate(game, lambda x, y: (x, y) == (lane, 1))
        cross(game, "N", "PalletTown_Frlg")
        assert game.state()["x"] == lane, game.state()
        check_view(game, f"pallet_south_return_{lane}")
    print("PASS: Pallet south is blocked on foot and the Surf passage works both ways")


if __name__ == "__main__":
    main()
