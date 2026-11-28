#!/usr/bin/env python3
"""Route 24 / Route 25 / Cerulean City: the Rocket's exit, the cottage road
NPC, and the river into the natural Cerulean Cave mouth.

Static part: Route 24 has no cave warp or guard and two south connections
(Rustboro's road, Cerulean City's north pond); Cerulean City's FRLG cave mouth
(warp 7) leads into the post-game cave and back, and the League guard stands
there, hidden on FLAG_SYS_GAME_CLEAR; Route 25 keeps one Misty.
Emulator part (mGBA): beating the Route 24 Rocket sends him walking south out
of sight, and he stays gone after a reload of the map; the NPC near the
cottage speaks its own line; walking south on the road still reaches
Rustboro; surfing south down the river crosses into Cerulean City, where the
guard blocks the cave before the Hall of Fame and the cave opens after it;
surfing north returns to Route 24.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))


def load_map(name):
    return json.loads((ROOT / "data/maps" / name / "map.json").read_text())


def static_checks() -> None:
    r24, cer, fall, r25 = (load_map(m) for m in ("Route24_hns", "CeruleanCity_Frlg",
                                                  "MtSilver_1F_WaterfallRoom_hns", "Route25_hns"))
    assert r24["warp_events"] == [], r24["warp_events"]
    assert not any("CaveGuard" in o.get("script", "") for o in r24["object_events"])
    south = [(c["map"], c["offset"]) for c in r24["connections"] if c["direction"] == "down"]
    assert south == [("MAP_RUSTBORO_CITY", -3), ("MAP_CERULEAN_CITY", -8)], south
    assert {"map": "MAP_ROUTE24_HNS", "offset": 8, "direction": "up"} in cer["connections"]
    mouth = cer["warp_events"][7]
    assert (mouth["x"], mouth["y"], mouth["dest_map"], mouth["dest_warp_id"]) == (
        1, 12, "MAP_MT_SILVER_1F_WATERFALL_ROOM_HNS", "0"), mouth
    assert (fall["warp_events"][0]["dest_map"], fall["warp_events"][0]["dest_warp_id"]) == ("MAP_CERULEAN_CITY", "7")
    guard = [o for o in cer["object_events"] if o.get("script") == "CeruleanCity_EventScript_CeruleanCaveGuard"]
    assert len(guard) == 1 and (guard[0]["x"], guard[0]["y"], guard[0]["flag"]) == (1, 13, "FLAG_SYS_GAME_CLEAR")
    rocket = [o for o in r24["object_events"] if o.get("local_id") == "LOCALID_ROUTE24_GRUNT"]
    assert rocket and rocket[0]["flag"] == "FLAG_TEMP_11", rocket
    mistys = [(o["x"], o["y"]) for o in r25["object_events"] if o["graphics_id"] == "OBJ_EVENT_GFX_MISTY"]
    assert mistys == [(100, 17)], mistys
    print("  ok  Route 24 cave warp/guard gone; south edge -> Rustboro + Cerulean; Cerulean mouth <-> cave; one Misty")


def emulator_checks() -> None:
    from pox_fixtures import game, finish_trainer, at, shot
    from test_sudowoodo_v1 import talk, settle, in_battle
    from walklib import K

    g = game()

    def pos():
        s = g.state()
        return s["x"], s["y"]

    def step(key, n=1):
        for _ in range(n):
            start = (g.state()["group"], g.state()["num"], *pos())
            for _ in range(3):
                g.hold(key, 4)
                g.frame(24)
                if (g.state()["group"], g.state()["num"], *pos()) != start:
                    break

    def hold_until_map_change(key, frames=240):
        start = (g.state()["group"], g.state()["num"])
        g.core.set_keys(key)
        for _ in range(frames):
            g.frame(1)
            if (g.state()["group"], g.state()["num"]) != start:
                break
        g.core.clear_keys(key)
        g.frame(60)

    def rocket_visible():
        r = talk(g, K.KEY_RIGHT)
        settle(g)
        return bool(r["text"]) or r["battle"]

    # 1. Rocket spotted from below: he battles, then sidesteps and walks south.
    g.warp("Route24_hns", 18, 11)
    g.frame(60)
    step(K.KEY_UP)  # into his sight: he walks down to meet the player
    for _ in range(200):
        g.tap(K.KEY_A, hold=1, wait=6)
        if in_battle(g):
            break
    finish_trainer(g, True)
    for _ in range(8):
        g.tap(K.KEY_A, hold=1, wait=10)
    g.frame(20)
    shot(g, "route24_rocket_leaving")
    g.frame(240)
    settle(g)
    assert g.flag("FLAG_TEMP_11"), "Rocket was not removed after the battle"
    assert at(g, "Route24_hns") and pos() == (18, 10), pos()
    step(K.KEY_UP, 2)  # through where he stood: nobody there
    assert pos() == (18, 8), ("Rocket still blocks the bridge", pos())
    print("  ok  beaten Rocket walks south toward Rustboro and is removed")
    g.warp("Route24_hns", 17, 8)
    g.frame(60)
    assert g.flag("FLAG_TEMP_11") and not rocket_visible(), "Rocket back after reload"
    print("  ok  Rocket stays gone when Route 24 is loaded again")

    # 2. Rocket approached from the side: talk, battle, he walks straight down.
    g = game()
    g.warp("Route24_hns", 17, 8)
    g.frame(60)
    r = talk(g, K.KEY_RIGHT)
    assert r["battle"], r
    finish_trainer(g, True)
    for _ in range(8):
        g.tap(K.KEY_A, hold=1, wait=10)
    g.frame(240)
    settle(g)
    assert g.flag("FLAG_TEMP_11") and not rocket_visible()
    print("  ok  talking to him from the side: same exit")

    # 3. Route 25: the NPC beside the cottage path is no longer a second Misty.
    g.warp("Route25_hns", 81, 18)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    settle(g)
    text = " ".join(r["text"])
    assert "post" in text and "BILL" not in text, r["text"]
    print("  ok  Route 25 (81,17): postwoman with her own line")

    # 4. The road south still reaches Rustboro.
    g.warp("Route24_hns", 17, 19)
    g.frame(60)
    hold_until_map_change(K.KEY_DOWN)
    assert at(g, "RustboroCity"), g.state()
    print(f"  ok  Route 24 road -> Rustboro at {pos()}")

    # 5. River lanes off the pond are shut; the open lanes surf into Cerulean.
    for lane in (13, 14):
        g.warp("Route24_hns", lane, 19)
        g.frame(60)
        hold_until_map_change(K.KEY_DOWN, 150)
        assert at(g, "Route24_hns"), (lane, g.state())
    for lane in (8, 12):
        g.warp("Route24_hns", lane, 19)
        g.frame(60)
        hold_until_map_change(K.KEY_DOWN)
        assert at(g, "CeruleanCity_Frlg") and pos() == (lane + 8, 0), (lane, g.state(), pos())
    shot(g, "cerulean_from_route24_river")
    print("  ok  Route 24 river (x 8..12) surfs south into Cerulean City; x 13, 14 stay shut")

    # 6. Surf to the cave mouth. Before the Hall of Fame the guard blocks it.
    g.warp("Route24_hns", 11, 19)
    g.frame(60)
    hold_until_map_change(K.KEY_DOWN)
    assert at(g, "CeruleanCity_Frlg") and pos() == (19, 0), pos()
    step(K.KEY_DOWN, 3)
    step(K.KEY_LEFT, 14)
    step(K.KEY_DOWN, 11)
    assert pos() == (5, 14), pos()
    for _ in range(6):  # off the water onto the cave shore
        if pos()[0] <= 1:
            break
        step(K.KEY_LEFT)
    assert pos() == (1, 14), pos()
    r = talk(g, K.KEY_UP)
    assert any("HALL OF FAME" in t for t in r["text"]), r["text"]
    settle(g)
    shot(g, "cerulean_cave_guard")
    step(K.KEY_UP)
    assert pos() == (1, 14) and at(g, "CeruleanCity_Frlg"), pos()
    step(K.KEY_LEFT)
    hold_until_map_change(K.KEY_LEFT, 120)
    assert at(g, "CeruleanCity_Frlg"), ("west edge leaks into Route 4", g.state())
    print("  ok  Cerulean cave mouth reached by surfing; guard blocks it before the Hall of Fame")

    # 7. After the Hall of Fame the guard is gone; walk in and back out.
    g.flag("FLAG_SYS_GAME_CLEAR", True)
    g.warp("CeruleanCity_Frlg", 1, 14)
    g.frame(60)
    step(K.KEY_UP, 2)
    g.frame(120)
    assert at(g, "MtSilver_1F_WaterfallRoom_hns"), g.state()
    print(f"  ok  Cerulean City mouth -> Cerulean Cave at {pos()}")
    for _ in range(4):
        if at(g, "CeruleanCity_Frlg"):
            break
        step(K.KEY_DOWN)
        g.frame(60)
    g.frame(120)
    assert at(g, "CeruleanCity_Frlg") and pos() in ((1, 12), (1, 13)), (g.state(), pos())
    print(f"  ok  Cerulean Cave -> Cerulean City at {pos()}")

    # 8. Surf back north into Route 24's river.
    g.warp("CeruleanCity_Frlg", 18, 2)
    g.frame(60)
    hold_until_map_change(K.KEY_UP)
    assert at(g, "Route24_hns") and pos() == (10, 21), (g.state(), pos())
    print("  ok  Cerulean north pond -> Route 24 river")
    print("\nPASS: Route 24 / Route 25 / Cerulean")


if __name__ == "__main__":
    static_checks()
    if "--static" not in sys.argv:
        emulator_checks()
