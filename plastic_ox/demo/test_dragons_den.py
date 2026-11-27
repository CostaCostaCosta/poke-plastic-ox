#!/usr/bin/env python3
"""Dragon's Den: Blackthorn elder gate, the two Den rooms, RAYQUAZA.

Static part: the Blackthorn door and the Den rooms warp to each other; the
elder stands in the doorway and hides on FLAG_SYS_GAME_CLEAR; the door is cut
off from town by water, and the shrine plaza from the cavern door likewise;
RAYQUAZA's script is an ordinary legendary battle (no reward capture).
Emulator part (mGBA, needs pokeemerald.gba): before the Hall of Fame the elder
blocks the door and says why; after it the player walks in, down to the cavern
and back out with the D-pad; stepping onto the shrine plaza plays the arrival
scene once; RAYQUAZA is Lv.70, or the party's highest level when that is
higher; fleeing leaves it there; catching it removes it for good.
"""
from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

TOWN, ENTRANCE, CAVERN = "BlackthornCity_hns", "DragonsDen_Entrance_hns", "DragonsDen_Cavern_hns"
DOOR, ELDER = (26, 12), (26, 13)
RAYQUAZA_XY, PLAZA_STEP = (31, 40), (31, 36)


def load_map(name):
    return json.loads((ROOT / "data/maps" / name / "map.json").read_text())


def grid(name):
    """(width, height, walkable set, water set) from the layout and its tilesets' attributes."""
    data = load_map(name)
    layout = next(l for l in json.loads((ROOT / "data/layouts/layouts.json").read_text())["layouts"]
                  if l.get("id") == data["layout"])
    assert layout["layout_version"] == "hns" and layout["include_in_versions"] == ["emerald"], layout
    names = re.findall(r"^\s*(MB_\w+),", (ROOT / "include/constants/metatile_behaviors.h").read_text(), re.M)
    header = (ROOT / "src/data/tilesets/metatiles.h").read_text()

    def attrs(tileset):
        path = re.search(r'gMetatileAttributes_%s\[\] = INCBIN_U16\("([^"]+)"\)' % tileset[len("gTileset_"):], header)[1]
        raw = (ROOT / path).read_bytes()
        return struct.unpack("<%dH" % (len(raw) // 2), raw)

    primary, secondary = attrs(layout["primary_tileset"]), attrs(layout["secondary_tileset"])
    w, h = layout["width"], layout["height"]
    blocks = struct.unpack("<%dH" % (w * h), (ROOT / layout["blockdata_filepath"]).read_bytes())
    walk, water = set(), set()
    for i, block in enumerate(blocks):
        metatile, solid = block & 0x3FF, (block >> 10) & 3
        attr = primary[metatile] if metatile < 640 else secondary[metatile - 640]
        behavior = names[attr & 0xFF]
        if "WATER" in behavior and "WATERFALL" not in behavior:
            water.add((i % w, i // w))
        elif not solid:
            walk.add((i % w, i // w))
    return w, h, walk, water


def reach(start, open_tiles, blocked=()):
    seen, todo = {start}, [start]
    while todo:
        x, y = todo.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in open_tiles and n not in seen and n not in blocked:
                seen.add(n)
                todo.append(n)
    return seen


def static_checks() -> None:
    town, entrance, cavern = load_map(TOWN), load_map(ENTRANCE), load_map(CAVERN)
    door = [i for i, w in enumerate(town["warp_events"]) if w["dest_map"] == entrance["id"]]
    assert len(door) == 1 and (town["warp_events"][door[0]]["x"], town["warp_events"][door[0]]["y"]) == DOOR
    assert town["warp_events"][door[0]]["dest_warp_id"] == "0"
    assert entrance["warp_events"][0]["dest_map"] == town["id"] and entrance["warp_events"][0]["dest_warp_id"] == str(door[0])
    assert entrance["warp_events"][3]["dest_map"] == cavern["id"] and entrance["warp_events"][3]["dest_warp_id"] == "0"
    assert cavern["warp_events"] == [dict(cavern["warp_events"][0], dest_map=entrance["id"], dest_warp_id="3")]
    elder = [o for o in town["object_events"] if o["script"] == "BlackthornCity_EventScript_DenElder"]
    assert len(elder) == 1 and (elder[0]["x"], elder[0]["y"]) == ELDER and elder[0]["flag"] == "FLAG_SYS_GAME_CLEAR"
    print("  ok  Blackthorn door <-> Den entrance <-> cavern; elder in the doorway hides on FLAG_SYS_GAME_CLEAR")

    _, _, walk, water = grid(TOWN)
    shore = reach(ELDER, walk)
    around = {(DOOR[0] + dx, DOOR[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    assert around & (walk | water) == {ELDER}, "the door must only be entered from the elder's tile"
    centre = (town["warp_events"][0]["x"], town["warp_events"][0]["y"] + 1)  # outside the Pokémon Center
    assert centre in walk and centre not in shore, "the Den shore is joined to town by land"
    assert centre in reach(ELDER, walk | water), "the Den shore cannot be reached by Surf"
    _, _, walk, water = grid(CAVERN)
    arrive = (cavern["warp_events"][0]["x"], cavern["warp_events"][0]["y"] + 1)
    assert RAYQUAZA_XY not in reach(arrive, walk) and RAYQUAZA_XY in reach(arrive, walk | water)
    # Every way onto the plaza crosses one of the three arrival triggers.
    triggers = {(c["x"], c["y"]) for c in cavern["coord_events"]}
    assert triggers == {(30, 36), (31, 36), (32, 36)} and {c["script"] for c in cavern["coord_events"]} == {
        "PoxDragonsDen_RayquazaArrives"}
    assert RAYQUAZA_XY not in reach(arrive, walk | water, blocked=triggers)
    print("  ok  Surf is needed to reach the Den door and the shrine plaza; the plaza is only entered over the triggers")

    ray = [o for o in cavern["object_events"] if o["graphics_id"] == "OBJ_EVENT_GFX_RAYQUAZA"]
    assert len(ray) == 1 and (ray[0]["x"], ray[0]["y"]) == RAYQUAZA_XY and ray[0]["script"] == "PoxDragonsDen_Rayquaza"
    script = (ROOT / "data/maps" / CAVERN / "scripts.inc").read_text()
    body = script[script.index("PoxDragonsDen_Rayquaza::"):script.index("PoxDragonsDen_RayquazaFainted:")]
    assert "setwildbattle SPECIES_RAYQUAZA, 70\n\tspecial PoxRaiseWildMonToPartyLevel\n\tspecial BattleSetup_StartLegendaryBattle\n" in body
    assert "LegendaryRewardBattle" not in script
    flags = (ROOT / "include/constants/plastic_ox_flags.h").read_text()
    ids = [re.search(rf"^#define {f} \(POX_EXT_FLAGS_START \+ (\d+)\)$", flags, re.M)[1] for f in (
        "FLAG_POX_CAUGHT_RAYQUAZA", "FLAG_POX_DEN_RAYQUAZA_ARRIVED", "FLAG_POX_HIDE_DRAGONS_DEN_PP_MAX",
        "FLAG_POX_HIDE_DRAGONS_DEN_MAX_POTION", "FLAG_POX_HIDE_DRAGONS_DEN_DRAGON_FANG")]
    assert len(set(ids)) == 5, ids
    enc = json.loads((ROOT / "src/data/wild_encounters.json").read_text())["wild_encounter_groups"][0]["encounters"]
    tables = [e for e in enc if e["map"] == cavern["id"]]
    assert len(tables) == 3 and all(min(m["min_level"] for m in t["water_mons"]["mons"]) >= 45 for t in tables)
    print("  ok  RAYQUAZA: Lv.70 raised to the party, ordinary legendary battle; five flags; Lv.45+ surf tables")


def emulator_checks() -> None:
    from pox_fixtures import game, at, shot
    from test_sudowoodo_v1 import (talk, settle, settle_overworld, in_overworld, in_battle, wait_for_battle,
                                   battle_mon, throw_ball, give_item, run_code, opcode, const, script_running)
    from walklib import K

    g = game()
    stride = g.sizes["gParties"] // 24
    rayquaza = const("SPECIES_RAYQUAZA", "species.h")
    assert not g.flag("FLAG_SYS_GAME_CLEAR")

    def pos():
        s = g.state()
        return s["x"], s["y"]

    def step(key, n=1):
        """Exactly n tiles (or until blocked / warped): one short press each."""
        for _ in range(n):
            start = (g.state()["group"], g.state()["num"], pos())
            for _ in range(3):
                g.hold(key, 4)
                g.frame(20)
                if (g.state()["group"], g.state()["num"], pos()) != start:
                    break

    def party_level(i, value=None):
        addr = g.syms["gParties"] + i * stride + stride - 16
        if value is not None:
            g.write(addr, value)
        return g.u8(addr)

    def back_on_the_map():
        """After a battle: no A presses, which would talk to RAYQUAZA again."""
        for _ in range(1200):
            if in_overworld(g) and g.u8(g.syms["sGlobalScriptContextStatus"]) == 2:
                return
            g.tap(K.KEY_B, hold=1, wait=4)
        shot(g, "dragons_den_stuck")
        raise AssertionError(("never returned to the map", g.describe(), in_battle(g), in_overworld(g),
                              g.u8(g.syms["sGlobalScriptContextStatus"]), g.text()))

    # 1. Before the Hall of Fame the elder stands in the Den doorway.
    g.warp(TOWN, 26, 14)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    text = " ".join(r["text"])
    assert "powerful" in text and "HALL OF FAME" in text, r["text"]
    settle(g)
    shot(g, "dragons_den_elder")
    step(K.KEY_UP, 2)
    assert at(g, TOWN) and pos() == (26, 14), (g.describe(), pos())
    print("  ok  elder blocks the Den door before the Hall of Fame: 'far too powerful'")

    # 2. After it: in through the door, back out, then down to the cavern and back.
    g.flag("FLAG_SYS_GAME_CLEAR", True)
    g.warp(TOWN, 26, 14)
    g.frame(60)
    step(K.KEY_UP)
    assert pos() == ELDER, ("elder still there", pos())
    step(K.KEY_UP)
    g.frame(120)
    assert at(g, ENTRANCE), g.describe()
    shot(g, "dragons_den_entrance")
    print(f"  ok  Blackthorn door -> Den entrance at {pos()}")
    for _ in range(3):
        if at(g, TOWN):
            break
        step(K.KEY_DOWN)
        g.frame(90)
    assert at(g, TOWN) and pos() in (DOOR, ELDER), (g.describe(), pos())
    print(f"  ok  Den entrance -> Blackthorn at {pos()}")
    step(K.KEY_UP, 2)
    g.frame(120)
    assert at(g, ENTRANCE), g.describe()
    step(K.KEY_UP)          # (4,4)
    step(K.KEY_RIGHT)       # (5,4)
    step(K.KEY_UP)          # ladder (5,3)
    g.frame(120)
    assert at(g, ENTRANCE) and pos()[1] >= 12, ("ladder down", pos())
    lower = pos()
    for key in (K.KEY_DOWN, K.KEY_RIGHT, K.KEY_DOWN, K.KEY_DOWN, K.KEY_DOWN):
        if at(g, CAVERN):
            break
        step(key)
        g.frame(60)
    g.frame(120)
    assert at(g, CAVERN), g.describe()
    arrived = pos()
    shot(g, "dragons_den_cavern")
    print(f"  ok  entrance ladder {lower} -> cavern at {arrived}")
    for _ in range(3):
        if at(g, ENTRANCE):
            break
        step(K.KEY_UP)
        g.frame(90)
    assert at(g, ENTRANCE) and pos()[1] >= 12, (g.describe(), pos())
    print(f"  ok  cavern -> entrance at {pos()}")

    # 3. The arrival scene: first step onto the shrine plaza.
    g.warp(CAVERN, 31, 34)
    g.frame(60)
    shot(g, "dragons_den_plaza_empty")
    step(K.KEY_DOWN)
    assert not script_running(g) and pos() == (31, 35)
    step(K.KEY_DOWN)
    assert pos() == PLAZA_STEP, pos()
    seen, frames = [], 0
    for frames in range(0, 4000, 10):
        g.frame(10)
        if frames % 60 == 0:
            shot(g, f"dragons_den_arrival_{frames // 60:02d}")
        t = g.text()
        if t and (not seen or seen[-1] != t):
            seen.append(t)
        if frames > 120 and g.u8(g.syms["sGlobalScriptContextStatus"]) == 2:
            break
        if frames % 30 == 0:
            g.tap(K.KEY_A, hold=1, wait=1)
    assert g.u8(g.syms["sGlobalScriptContextStatus"]) == 2, "arrival scene never ended"
    assert frames > 400, ("scene too short to have played", frames)
    assert any("RAYQUAZA" in t for t in seen), seen
    assert g.flag("FLAG_POX_DEN_RAYQUAZA_ARRIVED") and not g.flag("FLAG_POX_CAUGHT_RAYQUAZA")
    assert at(g, CAVERN) and pos() == PLAZA_STEP and in_overworld(g)
    shot(g, "dragons_den_arrived")
    print(f"  ok  arrival scene plays on the plaza step ({frames} frames) and sets FLAG_POX_DEN_RAYQUAZA_ARRIVED")

    # 4. First battle: Lv.70 for a party below that; fleeing leaves it there.
    for i in range(6):  # the fixture party is Lv.100
        party_level(i, 50)
    top = max(party_level(i) for i in range(6))
    step(K.KEY_DOWN, 3)
    assert pos() == (31, 39), pos()
    r = talk(g, K.KEY_DOWN, max_taps=400)
    assert r["battle"], r
    assert wait_for_battle(g), "no action menu"
    foe = battle_mon(g, 1)
    assert foe["species"] == rayquaza and foe["level"] == 70, foe
    types = g.u32(g.syms["gBattleTypeFlags"])
    legendary, reward = (int(re.search(rf"#define {n}\s+\(1 << (\d+)\)", (ROOT / "include/constants/battle.h").read_text())[1])
                         for n in ("BATTLE_TYPE_LEGENDARY", "BATTLE_TYPE_LEGENDARY_REWARD"))
    assert types & (1 << legendary) and not types & (1 << reward), hex(types)
    shot(g, "dragons_den_battle")
    for _ in range(40):  # RUN can fail; never press A outside the action menu (it would talk to RAYQUAZA again)
        if not in_battle(g):
            break
        if g.controller("HandleInputChooseAction"):
            g.write(g.syms["gActionSelectionCursor"], 3)
            g.tap(K.KEY_A, hold=1, wait=2)
        for _ in range(400):
            g.tap(K.KEY_B, hold=1, wait=3)
            if not in_battle(g) or g.controller("HandleInputChooseAction"):
                break
    assert not in_battle(g), "could not flee"
    assert g.u8(g.syms["gBattleOutcome"]) == 4, g.u8(g.syms["gBattleOutcome"])  # B_OUTCOME_RAN
    back_on_the_map()
    assert at(g, CAVERN) and not g.flag("FLAG_POX_CAUGHT_RAYQUAZA")
    print(f"  ok  RAYQUAZA Lv.70 against a Lv.{top} party, ordinary legendary battle; fleeing keeps it on the plaza")

    # 5. Return visit: no second scene, RAYQUAZA waiting; Lv.80 party -> Lv.80; catch it.
    g.warp(CAVERN, 31, 35)
    g.frame(60)
    step(K.KEY_DOWN)
    g.frame(30)
    assert pos() == PLAZA_STEP and not script_running(g), "arrival scene replayed"
    party_level(0, 80)
    step(K.KEY_DOWN, 3)
    assert pos() == (31, 39), pos()
    poke_ball, master_ball = const("ITEM_POKE_BALL", "items.h"), const("ITEM_MASTER_BALL", "items.h")
    assert run_code(g, opcode(g, "removeitem") + struct.pack("<HH", poke_ball, 20))
    give_item(g, master_ball, 1)
    r = talk(g, K.KEY_DOWN, max_taps=400)
    assert r["battle"], r
    assert wait_for_battle(g), "no action menu"
    foe = battle_mon(g, 1)
    assert foe["species"] == rayquaza and foe["level"] == 80, foe
    assert throw_ball(g) == 1
    for _ in range(3000):
        if g.flag("FLAG_POX_CAUGHT_RAYQUAZA") and in_overworld(g):
            break
        g.tap(K.KEY_B, hold=1, wait=6)
    assert g.flag("FLAG_POX_CAUGHT_RAYQUAZA"), ("not caught", g.u8(g.syms["gBattleOutcome"]))
    back_on_the_map()
    storage = g.u32(g.syms["gPokemonStoragePtr"])
    box = [g.box_species(storage + 4 + slot * 80) for slot in range(30) if g.u8(storage + 4 + slot * 80 + 19) & 7 == 2]
    assert rayquaza in box, box
    shot(g, "dragons_den_after_catch")
    r = talk(g, K.KEY_DOWN)
    assert not r["battle"] and not r["text"], ("RAYQUAZA still there", r)
    g.warp(CAVERN, 31, 35)
    g.frame(60)
    step(K.KEY_DOWN, 4)
    assert pos() == (31, 39) and not script_running(g)
    r = talk(g, K.KEY_DOWN)
    assert not r["battle"] and not r["text"], ("RAYQUAZA came back", r)
    print("  ok  Lv.80 party -> Lv.80 RAYQUAZA; caught, sent to the PC, and gone from the plaza for good")
    print("\nPASS: Dragon's Den")


if __name__ == "__main__":
    static_checks()
    if "--static" not in sys.argv:
        emulator_checks()
