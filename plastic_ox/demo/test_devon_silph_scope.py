#!/usr/bin/env python3
"""Devon Scope after Winona, Silph Scope from VALE, and what each one unlocks.

Static part: the generators own the new scripts (no drift), Route 119's Kecleon
are live with their own hide flags, and the old scope sources stay unreachable.
Emulator part (mGBA, needs pokeemerald.gba):
  * Pokemon Tower 3F wild battles are unidentifiable GHOST battles without the
    SILPH SCOPE (the engine's tower gate), and normal battles once VALE has
    handed it over after his Weather Institute trial;
  * the invisible Fortree Kecleon refuses to move before the DEVON SCOPE;
  * beating Winona brings LINDEN up to the player with the DEVON SCOPE, from
    each of the three tiles facing Winona (the repeat talk resumes a lost gift);
  * with the scope the Fortree Kecleon reveals itself and flees, and a Route
    119 Kecleon offers the Emerald DEVON SCOPE prompt and starts its battle.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

BATTLE_TYPE_GHOST = 1 << 28


def static_checks() -> None:
    story = (ROOT / "data/scripts/plastic_ox_story.inc").read_text()
    assert "goto_if_set FLAG_BADGE04_GET, Pox_WinonaDone" in story
    assert re.search(r"Pox_DevonScope_Give::.*?giveitem ITEM_DEVON_SCOPE\n\tsetflag FLAG_RECEIVED_DEVON_SCOPE",
                     story, re.S)
    wi = (ROOT / "data/scripts/plastic_ox_weather_institute.inc").read_text()
    assert re.search(r"Pox_WI_Vale_Won::\n.*?goto Pox_WI_Vale_Scope", wi, re.S)
    assert "giveitem ITEM_SILPH_SCOPE" in wi
    gym = json.loads((ROOT / "data/maps/FortreeCity_Gym/map.json").read_text())
    linden = [o for o in gym["object_events"] if o.get("local_id") == "LOCALID_FORTREE_GYM_LINDEN"]
    assert len(linden) == 1 and linden[0]["flag"] == "FLAG_POX_HIDE_UNUSED_ACTOR", linden
    r119 = json.loads((ROOT / "data/maps/Route119/map.json").read_text())
    flags = {o["script"]: o["flag"] for o in r119["object_events"] if "Kecleon" in o["script"]}
    assert flags == {"Route119_EventScript_Kecleon1": "FLAG_HIDE_ROUTE_119_KECLEON_1",
                     "Route119_EventScript_Kecleon2": "FLAG_HIDE_ROUTE_119_KECLEON_2"}, flags
    fortree = (ROOT / "data/maps/FortreeCity/scripts.inc").read_text()
    assert "checkitem ITEM_DEVON_SCOPE" in fortree.split("FortreeCity_EventScript_KecleonReveal::")[0]
    print("  ok  static: scope scripts, Linden object, Route 119 Kecleon flags")


def emulator_checks() -> None:
    from pox_fixtures import finish_trainer
    from test_sudowoodo_v1 import SudoGame, talk, settle, settle_overworld, in_battle, bag, const
    from test_sudowoodo_v1 import POCKET_KEY_ITEMS
    from test_ecruteak_gym_gate import at
    from walklib import K

    devon_scope = const("ITEM_DEVON_SCOPE", "items.h")
    silph_scope = const("ITEM_SILPH_SCOPE", "items.h")
    g = SudoGame()
    g.run("Pox_Treecko")
    for name in ("FLAG_POX_STORY_STARTER", "FLAG_ADVENTURE_STARTED", "FLAG_POX_STORY_ILEX",
                 "FLAG_POX_STORY_MTMOON", "FLAG_POX_STORY_BURNED_TOWER",
                 "FLAG_BADGE01_GET", "FLAG_BADGE02_GET", "FLAG_BADGE03_GET"):
        g.flag(name, True)
    assert bag(g, silph_scope) == 0 and bag(g, devon_scope) == 0

    def tower_wild_battle() -> int:
        """Pace Tower 3F until a wild battle starts; return gBattleTypeFlags.
        The emulator state is restored afterwards, so the battle never ends."""
        snap = g.core.save_raw_state()
        g.warp("PokemonTower_3F_Frlg", 12, 11)
        g.frame(60)
        # The test fixture boots with wild encounters off (new_game.c).
        g.write(g.syms["gPlasticOxTriggersEnabled"], 1)
        g.write(g.syms["sWildEncountersDisabled"], 0)
        for i in range(400):
            g.hold(K.KEY_RIGHT if i % 2 == 0 else K.KEY_LEFT, 16)
            g.frame(20)
            if in_battle(g):
                g.frame(60)
                flags = g.u32(g.syms["gBattleTypeFlags"])
                assert g.core.load_raw_state(snap)
                g.frame(2)
                return flags
        raise AssertionError("no wild battle on Pokemon Tower 3F")

    # 1. Without the SILPH SCOPE the tower's wild POKeMON are GHOSTs.
    flags = tower_wild_battle()
    assert flags & BATTLE_TYPE_GHOST, hex(flags)
    print("  ok  Tower 3F wild battle is an unidentified GHOST without the SILPH SCOPE")

    # 2. VALE gives the SILPH SCOPE after his trial.
    def institute_trial(x, y, key, trainer):
        g.warp("Route119_WeatherInstitute_2F", x, y)
        g.frame(60)
        r = talk(g, key)
        assert r["battle"], r
        g.frame(120)
        assert g.u16(g.syms["gTrainerBattleParameter"] + 2) == g.const(trainer)
        finish_trainer(g, True)
        g.clear_text()
        seen = []
        for _ in range(400):
            t = g.text()
            if t and (not seen or seen[-1] != t):
                seen.append(t)
            if g.u8(g.syms["sGlobalScriptContextStatus"]) == 2 and not in_battle(g):
                break
            g.tap(K.KEY_A, hold=2, wait=16)
        settle_overworld(g)
        return seen

    institute_trial(11, 7, K.KEY_UP, "TRAINER_PLASTIC_OX_WEATHER_DEVON")
    assert bag(g, silph_scope) == 0, "LINDEN's trial must not give the SILPH SCOPE"
    seen = institute_trial(17, 6, K.KEY_RIGHT, "TRAINER_PLASTIC_OX_WEATHER")
    assert bag(g, silph_scope) == 1, ("SILPH SCOPE", bag(g, silph_scope), seen)
    assert any("SILPH SCOPE" in t for t in seen), seen
    g.warp("Route119_WeatherInstitute_2F", 17, 6)
    g.frame(60)
    r = talk(g, K.KEY_RIGHT)
    assert not r["battle"] and bag(g, silph_scope) == 1, (r, bag(g, silph_scope))
    print("  ok  VALE hands over the SILPH SCOPE once, after his trial")

    # 3. With it the tower's wild battles are ordinary.
    flags = tower_wild_battle()
    assert not flags & BATTLE_TYPE_GHOST, hex(flags)
    print("  ok  Tower 3F wild battle is identified with the SILPH SCOPE")

    # 4. Director concludes; before Winona the Fortree Kecleon will not move.
    g.flag("FLAG_POX_STORY_WEATHER", True)
    g.warp("FortreeCity", 37, 10)
    g.frame(60)
    r = talk(g, K.KEY_RIGHT)
    assert any("invisible" in t for t in r["text"]), r["text"]
    assert not g.flag("FLAG_KECLEON_FLED_FORTREE")
    print("  ok  Fortree Kecleon blocks the walkway without the DEVON SCOPE")

    # 5. Winona -> LINDEN walks up with the DEVON SCOPE.
    def linden_scene(x, y, key):
        g.warp("FortreeCity_Gym", x, y)
        g.frame(60)
        r = talk(g, key)
        if r["battle"]:
            g.frame(120)
            finish_trainer(g, True)
        g.clear_text()
        seen = list(r["text"])
        for _ in range(600):
            t = g.text()
            if t and (not seen or seen[-1] != t):
                seen.append(t)
            if g.u8(g.syms["sGlobalScriptContextStatus"]) == 2 and not in_battle(g):
                break
            g.tap(K.KEY_A, hold=2, wait=16)
        settle_overworld(g)
        assert at(g, "FortreeCity_Gym"), g.state()
        return seen

    seen = linden_scene(15, 3, K.KEY_UP)
    assert g.flag("FLAG_BADGE04_GET")
    assert g.flag("FLAG_RECEIVED_DEVON_SCOPE"), seen
    assert bag(g, devon_scope) == 1, bag(g, devon_scope)
    assert any("LINDEN" in t for t in seen) and any("DEVON SCOPE" in t for t in seen), seen
    print("  ok  after Winona, LINDEN walks up (from below) and gives the DEVON SCOPE")
    seen = linden_scene(15, 3, K.KEY_UP)
    assert bag(g, devon_scope) == 1 and not any("LINDEN" in t for t in seen), seen
    for x, y, key in ((14, 2, K.KEY_RIGHT), (16, 2, K.KEY_LEFT)):
        g.flag("FLAG_RECEIVED_DEVON_SCOPE", False)
        seen = linden_scene(x, y, key)
        assert g.flag("FLAG_RECEIVED_DEVON_SCOPE") and any("LINDEN" in t for t in seen), (x, seen)
    print("  ok  LINDEN reaches the player from (14,2) and (16,2); repeat talk only resumes a lost gift")

    # 6. Fortree Kecleon: reveal with the scope, flee, walkway clear.
    g.warp("FortreeCity", 37, 10)
    g.frame(60)
    r = talk(g, K.KEY_RIGHT)
    assert any("DEVON SCOPE" in t for t in r["text"]), r["text"]
    assert g.flag("FLAG_KECLEON_FLED_FORTREE")
    settle(g)
    g.hold(K.KEY_RIGHT, 16)
    g.frame(30)
    st = g.state()
    assert not at(g, "FortreeCity") or st["x"] >= 38, ("walkway still blocked", st)
    print("  ok  Fortree Kecleon revealed through the DEVON SCOPE and fled")

    # 7. Route 119 Kecleon: the Emerald DEVON SCOPE prompt, then the battle.
    g.warp("Route119", 31, 7)
    g.frame(60)
    r = talk(g, K.KEY_UP, stop_at="DEVON SCOPE")
    assert r["stopped"], r["text"]
    for _ in range(200):
        if in_battle(g):
            break
        g.tap(K.KEY_A, hold=2, wait=16)
    assert in_battle(g), "Route 119 Kecleon battle never started"
    print("  ok  Route 119 Kecleon: DEVON SCOPE prompt starts the battle")
    print("\nPASS: Devon Scope and Silph Scope")


if __name__ == "__main__":
    static_checks()
    if "--static" not in sys.argv:
        emulator_checks()
