#!/usr/bin/env python3
"""Exercise fruit harvests and real Headbutt interactions in the rebuilt ROM.

Only emulator RAM is changed; player saves are never written.
"""
import re
import struct

from test_story import StoryGame, ROOT
from test_qol import opcode, begin_code
from test_cut_tool import finish
from walklib import K

SHOTS = ROOT / "plastic_ox/demo/shots/gen2_trees"


def item_id(name):
    return int(re.search(r"\bITEM_" + name + r"\s*=\s*(\d+)",
                        (ROOT / "include/constants/items.h").read_text())[1])


def run_code(g, code):
    begin_code(g, code + opcode(g, "end"))
    g.frame(5)
    assert g.u8(g.syms["sGlobalScriptContextStatus"]) == 2


def pocket(g, index):
    address = g.syms["gBagPockets"] + index * (g.sizes["gBagPockets"] // 5)
    return g.u32(address), g.u8(address + 4)


def quantity(g, item, index=3):
    slots, count = pocket(g, index)
    # Empty slots retain an encrypted zero, which reveals the bag XOR key.
    key = next(g.u16(slots + 4*i + 2) for i in range(count)
               if g.u16(slots + 4*i) == 0)
    return sum(g.u16(slots + 4*i + 2) ^ key for i in range(count)
               if g.u16(slots + 4*i) == item)


def face(g, name, x, y):
    g.warp(name, x, y + 1)
    g.tap(K.KEY_UP, hold=2, wait=20)
    assert (g.state()["x"], g.state()["y"]) == (x, y + 1)


def interact(g, accept=True):
    g.tap(K.KEY_A, hold=2, wait=60)
    if accept:
        finish(g)
    else:
        for _ in range(30):
            g.tap(K.KEY_B, hold=2, wait=10)
        assert g.u8(g.syms["sGlobalScriptContextStatus"]) == 2


def fruit_tests():
    g = StoryGame()
    trees = [("Route29_hns", 15, 11, "SITRUS", "R29_SITRUS"),
             ("Route46_hns", 9, 11, "LUM", "R46_LUM"),
             ("Route46_hns", 11, 11, "LIECHI", "R46_LIECHI"),
             ("Route44_hns", 7, 10, "SALAC", "R44_SALAC"),
             ("Route44_hns", 9, 10, "PETAYA", "R44_PETAYA")]
    for name, x, y, berry, flag in trees:
        item = item_id(berry + "_BERRY")
        flag = "FLAG_POX_DAILY_" + flag
        face(g, name, x, y)
        interact(g, accept=False)
        assert quantity(g, item) == 0 and not g.flag(flag)
        interact(g)
        assert quantity(g, item) == 1 and g.flag(flag), berry
        assert g.flag("FLAG_SYS_CLOCK_SET")
        face(g, name, x, y)  # Leaving and returning cannot bypass the daily limit.
        interact(g)
        assert quantity(g, item) == 1, berry
        g.fb.to_pil().convert("RGB").save(SHOTS / (berry.lower() + ".png"))

    # Run the real RTC day update with the saved day deliberately one day old.
    assert g.var(0x4040) > 0
    g.setvar(0x4040, g.var(0x4040) - 1)
    run_code(g, opcode(g, "callnative") + struct.pack("<I", g.syms["DoTimeBasedEvents"] | 1))
    for _, _, _, _, flag in trees:
        assert not g.flag("FLAG_POX_DAILY_" + flag)

    face(g, "Route29_hns", 15, 11)
    slots, count = pocket(g, 3)
    saved = [g.u32(slots + 4*i) for i in range(count)]
    key = next(g.u16(slots + 4*i + 2) for i in range(count) if g.u16(slots + 4*i) == 0)
    for i in range(count):
        g.write(slots + 4*i, item_id("SITRUS_BERRY"), 2)
        g.write(slots + 4*i + 2, 999 ^ key, 2)
    interact(g)
    assert not g.flag("FLAG_POX_DAILY_R29_SITRUS"), "Full bag consumed harvest"
    for i, value in enumerate(saved):
        g.write(slots + 4*i, value, 4)
    interact(g)
    assert quantity(g, item_id("SITRUS_BERRY")) == 2
    print("PASS: all five berries; decline; daily limit across map reload; RTC regrowth; full bag retry", flush=True)


def battle(g, label):
    for _ in range(200):
        g.tap(K.KEY_A, hold=2, wait=10)
        if g.u32(g.syms["gBattleTypeFlags"]):
            break
    else:
        g.fb.to_pil().convert("RGB").save(SHOTS / (label + "_failure.png"))
        raise AssertionError("Headbutt did not start battle: " + label)
    g.frame(180)
    enemy = g.syms["gParties"] + g.sizes["gParties"] // 4
    species = g.box_species(enemy)
    table = "Ilex" if label.startswith("IlexForest") else label.split("_")[0]
    level = g.u8(enemy + g.sizes["gParties"] // 24 - 16)
    allowed = []
    for time in ("Day", "Night"):
        symbol = "sPox" + table + "Headbutt" + time + "Mons"
        for offset in range(0, g.sizes[symbol], 4):
            row = g.syms[symbol] + offset
            allowed.append((g.u16(row + 2), g.u8(row), g.u8(row + 1)))
    assert any(species == mon and lo <= level <= hi for mon, lo, hi in allowed), (species, level, allowed)
    assert species != 204 or table == "Ilex", "Pineco must remain exclusive to Ilex"
    g.fb.to_pil().convert("RGB").save(SHOTS / (label + ".png"))
    print("PASS:", label, "wild species", species, flush=True)


def headbutt_tests():
    cases = [("Route29_hns", 3, 12, "direct"),
             ("Route46_hns", 13, 11, "registered"),
             ("Route44_hns", 54, 19, "move"),
             ("Route29_hns", 3, 12, "bag"),
             ("IlexForest_hns", 66, 4, "direct"),
             ("Route33_hns", 8, 17, "legacy")]
    for name, x, y, mode in cases:
        g = StoryGame()
        face(g, name, x, y)
        if mode != "legacy":
            assert g.behavior_at(x, y)[0] == 240
        interact(g)  # No key and no Pokemon: must return control safely.
        assert not g.u32(g.syms["gBattleTypeFlags"])
        run_code(g, opcode(g, "additem") + struct.pack("<HH", item_id("HEADBUTT_KEY"), 1))
        g.write(g.syms["sWildEncountersDisabled"], 0)
        interact(g)  # Possessing the key with an empty party must also be safe.
        assert not g.u32(g.syms["gBattleTypeFlags"])
        g.write(g.syms["sWildEncountersDisabled"], 1)
        run_code(g, opcode(g, "removeitem") + struct.pack("<HH", item_id("HEADBUTT_KEY"), 1))
        g.run("Pox_Squirtle")
        face(g, name, x, y)
        if mode == "move":
            run_code(g, opcode(g, "setmonmove") + bytes([0, 0]) + struct.pack("<H", 29))
        else:
            run_code(g, opcode(g, "additem") + struct.pack("<HH", item_id("HEADBUTT_KEY"), 1))
        interact(g, accept=False)
        assert not g.u32(g.syms["gBattleTypeFlags"])
        g.write(g.syms["sWildEncountersDisabled"], 0)
        if mode == "registered":
            g.write(int(g.state()["ptr"], 16) + 0x496, item_id("HEADBUTT_KEY"), 2)
            g.tap(K.KEY_RIGHT, hold=2, wait=20)
            g.tap(K.KEY_SELECT, hold=2, wait=60)
            finish(g)
            assert not g.u32(g.syms["gBattleTypeFlags"]), "Headbutt worked on empty ground"
            face(g, name, x, y)
            g.tap(K.KEY_SELECT, hold=2, wait=60)
        elif mode == "bag":
            # Open the real Bag at the key's slot, then use its ordinary menu.
            slots, count = pocket(g, 4)
            index = next(i for i in range(count) if g.u16(slots + 4*i) == item_id("HEADBUTT_KEY"))
            pos = g.syms["gBagPosition"]
            g.write(pos + 5, 4)
            g.write(pos + 8 + 4*2, index, 2)
            g.write(pos + 18 + 4*2, 0, 2)
            g.write(g.syms["gMain"] + 4, g.syms["CB2_BagMenuFromStartMenu"] | 1, 4)
            g.frame(90)
            g.tap(K.KEY_A, hold=2, wait=30)
            g.tap(K.KEY_A, hold=2, wait=90)
        else:
            g.tap(K.KEY_A, hold=2, wait=60)
        battle(g, name + "_" + mode)
        if mode != "move":
            assert quantity(g, item_id("HEADBUTT_KEY"), 4) == 1


if __name__ == "__main__":
    SHOTS.mkdir(parents=True, exist_ok=True)
    fruit_tests()
    headbutt_tests()
