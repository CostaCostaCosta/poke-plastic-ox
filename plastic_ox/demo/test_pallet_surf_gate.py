#!/usr/bin/env python3
"""Prove Pallet's south connection is blocked on foot and open via Surf."""

from test_region_walk import GEOMETRY, IDS, cross, current, navigate, setup
from walklib import K


def main():
    pallet = GEOMETRY["PalletTown_Frlg"]
    route = GEOMETRY["Route21_North_Frlg"]
    assert not any(c["map"] == "MAP_ROUTE21_NORTH" for c in pallet.data["connections"])
    assert not any(c["map"] == "MAP_PALLET_TOWN" for c in route.data["connections"])
    assert all(not pallet.passable(x, pallet.h - 1) for x in range(7, 11))
    assert all(pallet.passable(x, pallet.h - 1, water=True) for x in range(7, 11))
    assert all(route.passable(x, 0, water=True) for x in range(7, 11))
    assert {(e["x"], e["y"]) for e in pallet.data["coord_events"] if e["script"] == "PalletTown_SurfToRoute21"} == {(x, 19) for x in range(7, 11)}

    game = setup()
    game.flag("FLAG_POX_TRIGGERS_ENABLED", False)
    game.flag("FLAG_BADGE05_GET", True)
    game.test_water = False
    game.warp("PalletTown_Frlg", 12, 18)
    game.hold(K.KEY_DOWN, 96)
    game.frame(120)
    assert current(game) == "PalletTown_Frlg", game.state()
    assert game.state()["y"] == 19, game.state()

    game.test_water = True
    navigate(game, lambda x, y: (x, y) == (7, 18))
    cross(game, "S", "Route21_North_Frlg")
    assert current(game) == "Route21_North_Frlg"
    assert (game.state()["group"], game.state()["num"]) == IDS["Route21_North_Frlg"]
    navigate(game, lambda x, y: (x, y) == (7, 1))
    cross(game, "N", "PalletTown_Frlg")
    assert current(game) == "PalletTown_Frlg"
    print("PASS: Pallet south is blocked on foot and the Surf passage works both ways")


if __name__ == "__main__":
    main()
