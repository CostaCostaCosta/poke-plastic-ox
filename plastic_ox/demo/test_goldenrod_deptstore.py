#!/usr/bin/env python3
"""Goldenrod Department Store: themed clerks, vending, floor signs, CHOICE BAND for sale.

Talks to every floor clerk (and the 6F vending machine) in the real ROM, reads
the item list the open mart is showing (sMartInfo.itemList) and checks it
against the store's themed stock in data/scripts/plastic_ox_goldenrod.inc.
"""
import json
import re
import sys
from pathlib import Path
from test_story import StoryGame, ROOT
from walklib import K

INC = (ROOT/'data/scripts/plastic_ox_goldenrod.inc').read_text()
ITEMS_H = (ROOT/'include/constants/items.h').read_text()
TMS_H = (ROOT/'include/constants/tms_hms.h').read_text()


def item_id(name):
    m = re.search(r'^\s*' + name + r'\s*=\s*(\d+)', ITEMS_H, re.M)
    if m:
        return int(m[1])
    tm = name.removeprefix('ITEM_TM_')
    if tm != name:  # ITEM_TM_<MOVE> = ITEM_TM01 + index in FOREACH_TM
        order = re.findall(r'F\((\w+)\)', TMS_H.split('FOREACH_HM')[0])
        return item_id('ITEM_TM01') + order.index(tm)
    raise KeyError(name)


def stock(label):
    body = re.search(re.escape(label) + r'_Items:\n((?:\t\.2byte \w+\n)+)', INC)[1]
    names = re.findall(r'\.2byte (\w+)', body)
    assert names[-1] == 'ITEM_NONE'
    return names[:-1]


def mart_items(g):
    ptr = g.u32(g.syms['sMartInfo'] + 8)
    out = []
    while ptr and len(out) < 64:
        v = g.u16(ptr + 2*len(out))
        if v == 0:
            break
        out.append(v)
    return out


def open_mart(g, mapname, target, facing, dist=1):
    """Stand dist tiles from target (2 = across a counter), face it, press A
    until a mart item list is loaded."""
    g.write(g.syms['sMartInfo'] + 8, 0, 4)
    dx, dy = {'UP': (0, 1), 'DOWN': (0, -1), 'LEFT': (1, 0), 'RIGHT': (-1, 0)}[facing]
    g.warp(mapname, target[0] + dx*dist, target[1] + dy*dist)
    g.tap(getattr(K, 'KEY_' + facing), hold=2, wait=12)
    for _ in range(120):
        g.tap(K.KEY_A, hold=2, wait=10)
        if g.u32(g.syms['sMartInfo'] + 8):
            break
    else:
        raise AssertionError(('mart never opened', mapname, target, facing, dist, g.state()))
    g.frame(60)
    return mart_items(g)


def close(g):
    for _ in range(80):
        g.tap(K.KEY_B, hold=2, wait=10)
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            break
    g.frame(30)


def clerk_pos(floor):
    d = json.loads((ROOT/f'data/maps/GoldenrodCity_DepartmentStore_{floor}_hns/map.json').read_text())
    return next((o['x'], o['y']) for o in d['object_events'] if o['script'] == f'PoxGoldenrod_Shop{floor}')


def free_side(g, mapname, pos):
    g.warp(mapname, 9, 5)
    for dist in (2, 1):  # clerks stand behind counters: talk across them, as a customer
        for facing in ('DOWN', 'UP', 'LEFT', 'RIGHT'):  # HNS clerks face south
            dx, dy = {'UP': (0, 1), 'DOWN': (0, -1), 'LEFT': (1, 0), 'RIGHT': (-1, 0)}[facing]
            if g.collision_at(pos[0] + dx*dist, pos[1] + dy*dist)[0] == 0:
                yield facing, dist


def static_checks():
    # Gen 3 only: no Gen 4+ held items anywhere in the store.
    banned = {'ITEM_CHOICE_SPECS', 'ITEM_CHOICE_SCARF', 'ITEM_LIFE_ORB', 'ITEM_FOCUS_SASH',
              'ITEM_ASSAULT_VEST', 'ITEM_ROCKY_HELMET'}
    sys.path.insert(0, str(ROOT/'plastic_ox/tools'))
    from pox_progression import ITEM_CHECKPOINT, CHECKPOINT_INDEX
    for label in ('PoxGoldenrod_Shop2F', 'PoxGoldenrod_Shop3F', 'PoxGoldenrod_Shop4F',
                  'PoxGoldenrod_Shop5F', 'PoxGoldenrod_Vending6F'):
        items = stock(label)
        assert not banned & set(items), (label, banned & set(items))
        for it in items:
            if it in ITEM_CHECKPOINT:
                assert CHECKPOINT_INDEX[ITEM_CHECKPOINT[it]] <= CHECKPOINT_INDEX['goldenrod'], (label, it)
    assert 'ITEM_CHOICE_BAND' in stock('PoxGoldenrod_Shop5F')
    # Floor signs name what each floor sells; no generic city directory inside.
    for floor in ('1F', '2F', '3F', '4F', '5F', '6F'):
        d = json.loads((ROOT/f'data/maps/GoldenrodCity_DepartmentStore_{floor}_hns/map.json').read_text())
        assert all(b['script'] != 'PoxGoldenrod_Directory' for b in d['bg_events']), floor
    print('Gen 3 legal, checkpoint-legal themed stock; floor signs PASS', flush=True)


def clerks():
    g = StoryGame()
    for floor in ('2F', '3F', '4F', '5F'):
        mapname = f'GoldenrodCity_DepartmentStore_{floor}_hns'
        pos = clerk_pos(floor)
        want = [item_id(n) for n in stock(f'PoxGoldenrod_Shop{floor}')]
        for facing, dist in free_side(g, mapname, pos):
            try:
                got = open_mart(g, mapname, pos, facing, dist)
                break
            except AssertionError:
                close(g)
        else:
            raise AssertionError(('no side of clerk opens the mart', floor, pos))
        assert got == want, (floor, got, want)
        if floor == '5F':
            assert item_id('ITEM_CHOICE_BAND') in got
            print('5F clerk mart lists CHOICE BAND PASS', flush=True)
        close(g)
        print('clerk mart PASS', floor, len(got), 'items', flush=True)
    # 6F vending machines are wall signs; read one from below.
    d = json.loads((ROOT/'data/maps/GoldenrodCity_DepartmentStore_6F_hns/map.json').read_text())
    vend = next((b['x'], b['y']) for b in d['bg_events'] if b['script'] == 'PoxGoldenrod_Vending6F')
    got = open_mart(g, 'GoldenrodCity_DepartmentStore_6F_hns', vend, 'UP')
    assert got == [item_id(n) for n in stock('PoxGoldenrod_Vending6F')], got
    close(g)
    print('6F vending machine mart PASS', flush=True)


def buy_band():
    """Buy one CHOICE BAND through the real 5F mart UI."""
    from test_goldenrod import money
    from test_sudowoodo_v1 import bag as bag_pocket, const
    def bag(g, item): return bag_pocket(g, item, 0)  # POCKET_ITEMS
    band = const('ITEM_CHOICE_BAND', 'items.h')
    g = StoryGame()
    before = bag(g, band)
    pos = clerk_pos('5F')
    mapname = 'GoldenrodCity_DepartmentStore_5F_hns'
    # Money must be set before the mart opens: the open mart does not pick up
    # a balance poked into the save block behind its back.
    for facing, dist in list(free_side(g, mapname, pos)):
        money(g, 150000)
        try:
            items = open_mart(g, mapname, pos, facing, dist)
            break
        except AssertionError:
            close(g)
    index = items.index(item_id('ITEM_CHOICE_BAND'))
    g.tap(K.KEY_A, hold=2, wait=60)          # BUY
    g.frame(60)
    for _ in range(index):
        g.tap(K.KEY_DOWN, hold=2, wait=8)
    for _ in range(4):                        # select, quantity 1, confirm YES, ack
        g.tap(K.KEY_A, hold=2, wait=40)
    for _ in range(20):
        if bag(g, band) > before:
            break
        g.tap(K.KEY_A, hold=2, wait=30)
    assert bag(g, band) == before + 1, ('CHOICE BAND not bought', bag(g, band))
    g.frame(120)  # the mart adds the item first and charges after its message
    price = 150000 - money(g)
    assert price > 0, ('mart did not charge for the CHOICE BAND', money(g))
    close(g)
    print('CHOICE BAND bought through the 5F mart PASS, price', price, flush=True)


if __name__ == '__main__':
    for name, check in [('static', static_checks), ('clerks', clerks), ('buy', buy_band)]:
        if len(sys.argv) == 1 or name in sys.argv:
            check()
