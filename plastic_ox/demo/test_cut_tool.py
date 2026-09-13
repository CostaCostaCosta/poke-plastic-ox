#!/usr/bin/env python3
"""Real Cutter dialogue and tree interactions with no badges or Pokemon."""
from test_story import StoryGame, ROOT
from walklib import K
from walk_demo import object_tiles

CUT = 876


def finish(g):
    for _ in range(350):
        g.tap(K.KEY_A, hold=2, wait=10)
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            g.frame(60)
            return
    raise AssertionError('Dialogue did not release controls')


def key_items(g):
    pocket = g.syms['gBagPockets'] + 4 * (g.sizes['gBagPockets']//5)
    slots = g.u32(pocket)
    return [g.u16(slots+4*i) for i in range(g.u8(pocket+4))]


def cut_quantity_raw(g):
    pocket = g.syms['gBagPockets'] + 4 * (g.sizes['gBagPockets']//5)
    slots = g.u32(pocket)
    return g.u16(slots+4*key_items(g).index(CUT)+2)


def tree(g):
    g.warp('Route2_Frlg', 11, 12)
    g.tap(K.KEY_DOWN, hold=2, wait=20)
    assert (11, 13) in object_tiles(g)


def main():
    g = StoryGame(build='')
    assert g.count() == 0
    for i in range(1, 9):
        assert not g.flag(f'FLAG_BADGE{i:02}_GET')
    tree(g)
    g.tap(K.KEY_A, hold=2, wait=20)
    finish(g)
    assert (11, 13) in object_tiles(g), 'Tree cut before tool was obtained'

    # The physical NPC interaction grants a key item even if an older save
    # already received the HM. That legacy flag must not suppress migration.
    g.flag('FLAG_RECEIVED_HM_CUT', True)
    g.warp('RustboroCity_CuttersHouse', 8, 5)
    g.tap(K.KEY_LEFT, hold=2, wait=20)
    g.tap(K.KEY_A, hold=2, wait=20)
    finish(g)
    assert key_items(g).count(CUT) == 1, key_items(g)
    before = key_items(g)
    quantity = cut_quantity_raw(g)
    g.tap(K.KEY_A, hold=2, wait=20)
    finish(g)
    assert key_items(g) == before, 'Duplicate gift'
    assert cut_quantity_raw(g) == quantity, 'Duplicate item quantity'

    tree(g)
    g.tap(K.KEY_A, hold=2, wait=60)
    for _ in range(30):
        g.tap(K.KEY_B, hold=2, wait=10)
    assert (11, 13) in object_tiles(g), 'Declining still cut the tree'
    g.tap(K.KEY_A, hold=2, wait=20)
    finish(g)
    assert (11, 13) not in object_tiles(g), 'Direct interaction failed'
    assert CUT in key_items(g), 'Tool was consumed'
    out = ROOT/'plastic_ox/demo/shots'
    g.fb.to_pil().convert('RGB').save(out/'cut_tool_direct.png')

    # Reload the map to restore its temporary tree, then exercise the normal
    # registered-item task and field callback through the Select button.
    tree(g)
    g.write(int(g.state()['ptr'], 16)+0x496, CUT, 2)
    g.tap(K.KEY_SELECT, hold=2, wait=60)
    finish(g)
    assert (11, 13) not in object_tiles(g), 'Registered item failed'
    assert CUT in key_items(g) and g.count() == 0
    assert not g.flag('FLAG_BADGE01_GET')
    g.fb.to_pil().convert('RGB').save(out/'cut_tool_registered.png')
    # Using the registered tool while facing empty ground must fail cleanly.
    g.tap(K.KEY_SELECT, hold=2, wait=60)
    finish(g)
    assert CUT in key_items(g) and (11, 13) not in object_tiles(g)
    print('PASS: Cutter gift, legacy-HM migration, no duplicate, direct and registered Cut, reusable with zero badges and zero Pokemon')


if __name__ == '__main__':
    main()
