#!/usr/bin/env python3
"""Route 36 Sudowoodo x SquirtBottle end-to-end playtest (read-only on the ROM).

Drives the real field scripts through the ordinary engine in headless mGBA.
Only emulator RAM is written (flags / badge / party / bag for test setup); no ROM
data, map or script file is modified, and nothing is compiled.

Scenarios (numbered to match SUDOWOODO_PLAYTEST_V1_REPORT.md):
  1  gift gate before FLAG_BADGE02_GET, at both NPC placements
  2  gift with the badge, obtained by talking to the real NPC; idempotence
  3  tree interaction with the badge but no bottle
  4  tree interaction with the bottle: the prompt, and the unusable "No"
  5  full chain: accept -> wild battle -> win -> persistence / no respawn
  6  run from the battle -> tree and flag survive
  7  real Master Ball catch -> B_OUTCOME_CAUGHT clears the obstruction
  8  FLAG_POX_TRIGGERS_ENABLED off -> both scripts are inert
  9  6-mon party + all eight badges -> still a plain wild battle
 10  control: the same B-button measurement on a vanilla YES/NO dialog

Run:  ~/.venvs/mgba311/bin/python plastic_ox/demo/test_sudowoodo_v1.py [1..10]
Results are written to plastic_ox/demo/sudowoodo_results.json.
"""
import json
import re
import struct
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'plastic_ox/demo'))
sys.path.insert(0, str(ROOT / 'plastic_ox/battle/metamon'))

from test_qol import begin_code, opcode
from walklib import K
from smoke import Game

RESULTS = []


# ---------------------------------------------------------------- text decode
CHARMAP = {0x00: ' ', 0xBB: '\\n', 0xFC: '{dyn}', 0xFD: '{scroll}',
           0xFE: '{page}', 0xFF: '\\0'}
for _line in (ROOT / 'charmap.txt').read_text(errors='replace').splitlines():
    _m = re.match(r"""^'(.+?)'\s*=\s*([0-9A-Fa-f]{2})$""", _line)
    if _m:
        CHARMAP[int(_m[2], 16)] = _m[1]
        continue
    _m = re.match(r'^([0-9A-Fa-f]{2})\s*=\s*\{(.+)\}\s*$', _line)
    if _m:
        CHARMAP[int(_m[1], 16)] = _m[2].strip('"')
# charmap.txt maps 0x00 twice; keep the plain ASCII space.
CHARMAP = {k: v.replace('　', ' ') for k, v in CHARMAP.items()}


class SudoGame(Game):
    """smoke.Game plus the task-table probe from gym_smoke.GymGame."""

    def task(self, name):
        funcs = self.functions.get(name, set())
        return any(self.u8(self.syms['gTasks'] + i * 40 + 4) and
                   self.u32(self.syms['gTasks'] + i * 40) & ~0x02000001 in funcs
                   for i in range(16))

    def clear_text(self):
        """Blank the message buffer so 'no dialogue' is distinguishable."""
        self.write(self.syms['gStringVar4'], 0xFF)

    def text(self):
        addr = self.syms['gStringVar4']
        out = []
        for i in range(400):
            b = self.u8(addr + i)
            if b == 0xFF:
                break
            out.append(CHARMAP.get(b, '<%02X>' % b))
        return ''.join(out)


# ---------------------------------------------------------------- bag helpers
# struct BagPocket { struct ItemSlot *itemSlots; u16 capacity:10; enum Pocket id:6; }
POCKET_ITEMS, POCKET_BALLS, POCKET_TM_HM, POCKET_BERRIES, POCKET_KEY_ITEMS = range(5)


def pocket(g, index):
    a = g.syms['gBagPockets'] + index * (g.sizes['gBagPockets'] // 5)
    return g.u32(a), g.u16(a + 4) & 0x3FF


def bag(g, item, index=POCKET_KEY_ITEMS):
    """Quantity of `item` in a bag pocket (slot counts are XOR-encrypted)."""
    slots, capacity = pocket(g, index)
    if not slots or not capacity:
        return 0
    n = min(capacity, 64)
    ids = [g.u16(slots + 4 * i) for i in range(n)]
    qty = [g.u16(slots + 4 * i + 2) for i in range(n)]
    if 0 not in ids:
        return -1                                   # no empty slot to key off
    key = qty[ids.index(0)]
    return sum(q ^ key for i, q in zip(ids, qty) if i == item)


def const(name, header):
    m = re.search(r'\b' + name + r'\s*=\s*(\d+)', (ROOT / 'include/constants' / header).read_text())
    return int(m[1])


ITEM_SQUIRT_BOTTLE = const('ITEM_SQUIRT_BOTTLE', 'items.h')
ITEM_MASTER_BALL = const('ITEM_MASTER_BALL', 'items.h')
SPECIES_SUDOWOODO = const('SPECIES_SUDOWOODO', 'species.h')
SPECIES_MIMIC_MONS = tuple(const('MOVE_' + n, 'moves.h')
                           for n in ('ROCK_THROW', 'MIMIC', 'FLAIL', 'LOW_KICK'))
# Run 5 (P6): PlasticOx_PrepareSudowoodoMoves now pins the ability slot, so the
# scripted encounter is always the same Pokemon.  gBattleMons stores the
# ability *id* (the entry in gAbilitiesInfo for that species/num), not the
# abilityNum that the enum names; for Sudowoodo slot 1 that id is 69.
ABILITY_STURDY = const('ABILITY_STURDY', 'abilities.h')
ABILITY_STURDY_ID = 69


# ------------------------------------------------------------ field-script IO
def script_running(g):
    return g.u8(g.syms['sGlobalScriptContextStatus']) == 1


def in_battle(g):
    """True while the battle main callback owns the screen.

    gBattleTypeFlags is 0 for a scripted wild battle, and gBattleMons keeps
    stale data after the battle, so the callback is the reliable signal.
    """
    main = g.syms['gMain']
    cb = g.core.memory.iwram.u32[main - 0x03000000 + 4] & ~1
    return cb == (g.syms['BattleMainCB2'] & ~1)


def run_code(g, code, frames=120):
    begin_code(g, code + opcode(g, 'end'))
    for _ in range(frames // 10):
        g.frame(10)
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            return True
    return False


def give_item(g, item, count=1):
    assert run_code(g, opcode(g, 'additem') + struct.pack('<HH', item, count)), \
        'additem script did not finish'


def finished(g, frames=60):
    """Wait for the field script to run to its `end` (or for a battle to start)."""
    for _ in range(frames):
        g.frame(1)
        if in_battle(g) or g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            return True
    return False


def settle(g, taps=200):
    """Clear any running field script so warp() may start a new one."""
    for _ in range(taps):
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            return True
        g.tap(K.KEY_A, hold=1, wait=6)
    return g.u8(g.syms['sGlobalScriptContextStatus']) == 2


def context(g):
    """Field-script context: 0 RUNNING, 1 WAITING, 2 SHUTDOWN (src/script.c)."""
    ctx = g.syms['sGlobalScriptContext']
    return dict(status=g.u8(ctx), pc=hex(g.u32(ctx + 8)),
                locked=g.u8(g.syms['sLockFieldControls']))


def talk(g, key, stop_at=None, max_taps=200, after_b=0):
    """Face `key`, press A, then drive the object script to completion.

    `stop_at` (a text fragment) pauses the driver as soon as a box containing
    it is on screen so a specific prompt can be inspected; `after_b` then
    presses B that many times.  The message buffer is blanked first, so an
    empty `text` list means the script printed nothing at all.
    """
    settle(g)
    g.clear_text()
    g.tap(key, hold=2, wait=16)
    seen, stopped = [], False
    for _ in range(max_taps):
        t = g.text()
        if t and (not seen or seen[-1] != t):
            seen.append(t)
        if in_battle(g):
            break
        if stop_at and stop_at in t:
            stopped = True
            break
        g.tap(K.KEY_A, hold=2, wait=16)
        if finished(g):
            break
    for _ in range(after_b):
        g.tap(K.KEY_B, hold=2, wait=30)
    t = g.text()
    if t and (not seen or seen[-1] != t):
        seen.append(t)
    return dict(dialogue=bool(seen), battle=in_battle(g), text=seen,
                stopped=stopped, ctx=context(g))


def battle_mon(g, index):
    """Active battle mon, using this build's own struct offsets."""
    lay = [g.u32(g.syms['gMetamonTestLayout'] + i * 4) for i in range(16)]
    stride, moves, item = lay[6], lay[7], lay[8]
    ability, hp, maxhp, pp, attack = lay[9], lay[10], lay[11], lay[12], lay[13]
    base = g.syms['gBattleMons'] + index * stride
    ivs = g.u32(base + 20)
    return dict(species=g.u16(base), level=g.u8(base + 44), hp=g.u16(base + hp),
                maxhp=g.u16(base + maxhp), item=g.u16(base + item),
                ability=g.u16(base + ability), attack=g.u16(base + attack),
                moves=[g.u16(base + moves + 2 * i) for i in range(4)],
                pp=[g.u8(base + pp + i) for i in range(4)],
                ivs=[(ivs >> (5 * s)) & 31 for s in range(6)])


def best_move_slot(g):
    layout = [g.u32(g.syms['gMetamonTestLayout'] + i * 4) for i in range(16)]
    move_off, pp_off = layout[7], layout[12]
    base = g.syms['gBattleMons']
    best, power = 0, -1.0
    for i in range(4):
        move = g.u16(base + move_off + 2 * i)
        if not move or not g.u8(base + pp_off + i):
            continue
        p = struct.unpack('<f', bytes(g.u8(g.syms['sMoveInfo'] + move * 20 + j)
                                      for j in range(4)))[0]
        if p > power:
            best, power = i, p
    return best


def throw_ball(g, pocket=1):
    """Open the in-battle bag, switch to the balls pocket and throw slot 0.

    The bag registers its stacks a few frames after the pocket switch, and the
    first A after the switch is swallowed by the redraw.  Returns the number
    of balls thrown.
    """
    battle_cb = g.core.memory.iwram.u32[g.syms['gMain'] - 0x03000000 + 4] & ~1
    g.write(g.syms['gActionSelectionCursor'], 1)          # BAG
    g.tap(K.KEY_A, hold=1, wait=4)
    for _ in range(600):                                   # wait for the bag
        g.frame(1)
        if g.core.memory.iwram.u32[g.syms['gMain'] - 0x03000000 + 4] & ~1 != battle_cb:
            break
    before = bag(g, ITEM_MASTER_BALL, POCKET_BALLS)
    g.write(g.syms['gBagPosition'] + 5, pocket)            # switch pocket
    g.write(g.syms['gBagPosition'] + 8 + 2 * pocket, 0)    # first slot
    g.frame(60)
    for _ in range(8):
        g.tap(K.KEY_A, hold=2, wait=30)
        if bag(g, ITEM_MASTER_BALL, POCKET_BALLS) < before:
            return before - bag(g, ITEM_MASTER_BALL, POCKET_BALLS)
    return 0


def wait_for_battle(g, timeout=6000):
    """Wait until the player controller is live (action or move selection).

    The "Wild SUDOWOODO appeared!" text waits for input, so keep pressing A.
    """
    for _ in range(timeout):
        if g.controller('HandleInputChooseAction') or g.controller('HandleInputChooseMove'):
            return True
        g.tap(K.KEY_A, hold=1, wait=3)
    return False


def fight(g, mode='attack', limit=60000):
    """Play out the battle. mode: 'attack' | 'run' | 'ball'."""
    for step in range(limit):
        if g.controller('HandleInputChooseAction'):
            if mode == 'run':
                g.write(g.syms['gActionSelectionCursor'], 3)
                g.tap(K.KEY_A, hold=1, wait=2)
            elif mode == 'ball':
                g.write(g.syms['gActionSelectionCursor'], 1)   # BAG
                g.tap(K.KEY_A, hold=1, wait=2)
                g.tap(K.KEY_RIGHT, hold=1, wait=2)            # BALLS pocket
                g.tap(K.KEY_A, hold=1, wait=2)
                g.tap(K.KEY_A, hold=1, wait=2)                # first ball
            else:
                g.write(g.syms['gActionSelectionCursor'], 0)
                g.tap(K.KEY_A, hold=1, wait=2)
        elif g.controller('HandleInputChooseMove'):
            g.write(g.syms['gMoveSelectionCursor'], best_move_slot(g))
            g.tap(K.KEY_A, hold=1, wait=2)
        elif g.task('Task_HandleChooseMonInput'):
            g.write(g.syms['gPartyMenu'] + 9, 1)
            g.tap(K.KEY_A, hold=1, wait=3)
        else:
            g.tap(K.KEY_A, hold=1, wait=3)
        if not in_battle(g) and step > 120:
            return step
    raise AssertionError('battle did not end (%s)' % mode)


def return_to_field(g, taps=400):
    """Dismiss the post-battle result text so the field script resumes.

    After a scripted wild battle the battle screen waits for a button press
    (e.g. "Got away safely!"); the field script only resumes afterwards.
    """
    for i in range(taps):
        if not in_battle(g):
            return i
        g.tap(K.KEY_A, hold=1, wait=4)
    return None


def walk(g, key):
    """Tap a direction and then hold it: a bare hold does not re-trigger a
    movement edge, which is how a locked field used to look like a soft-lock."""
    before = (g.state()['x'], g.state()['y'])
    g.tap(key, hold=2, wait=10)
    g.hold(key, 150)
    g.frame(60)
    return before, (g.state()['x'], g.state()['y'])


def in_overworld(g):
    main = g.syms['gMain']
    cb = g.core.memory.iwram.u32[main - 0x03000000 + 4] & ~1
    return cb == (g.syms['CB2_Overworld'] & ~1)


def settle_overworld(g, taps=2000):
    """Tap A until the game is back on the map and the field script has run."""
    for i in range(taps):
        if in_overworld(g) and g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            return i
        g.tap(K.KEY_A, hold=1, wait=4)
    return None


def drain(g, frames=900):
    """Let the resumed field script run to completion without touching input."""
    for _ in range(frames):
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            return True
        g.frame(1)
    return False


def record(name, ok, detail):
    RESULTS.append(dict(scenario=name, ok=bool(ok), detail=detail))
    print(('PASS ' if ok else 'FAIL ') + name + ' :: ' + json.dumps(detail)[:1200], flush=True)


# ------------------------------------------------------------------ fixtures
def new_game(badge02=True, triggers=True, party=False):
    g = SudoGame()
    g.flag('FLAG_POX_TRIGGERS_ENABLED', triggers)
    g.flag('FLAG_BADGE02_GET', badge02)
    if party:
        run_code(g, opcode(g, 'callnative')
                 + struct.pack('<I', g.syms['GivePlasticOxPlayerParty'] | 1)
                 + opcode(g, 'releaseall'))
        g.frame(60)
        for b in range(1, 9):
            g.flag('FLAG_BADGE%02d_GET' % b, False)
        g.flag('FLAG_BADGE02_GET', True)
    return g


def go_tree(g):
    g.warp('Route36_hns', 39, 21)
    g.frame(90)


def go_flowershop(g):
    g.warp('GoldenrodCity_FlowerShop_hns', 2, 5)
    g.frame(90)


def go_street(g):
    g.warp('GoldenrodCity_hns', 27, 16)
    g.frame(90)


def armed(g):
    """Badge 02 + a bottle obtained by really talking to the flower grower."""
    go_flowershop(g)
    r = talk(g, K.KEY_UP)
    assert bag(g, ITEM_SQUIRT_BOTTLE) == 1, ('gift failed', r)
    return r


# ----------------------------------------------------------------- scenarios
def scenario_1():
    detail = {}
    for name, setup in (('flower_shop', go_flowershop), ('goldenrod_street', go_street)):
        g = new_game(badge02=False)
        setup(g)
        r = talk(g, K.KEY_UP)
        r['bottle'] = bag(g, ITEM_SQUIRT_BOTTLE)
        detail[name] = r
        record('1 gift refused before badge (%s)' % name,
               r['dialogue'] and not r['battle'] and r['bottle'] == 0
               and any('Beat WHITNEY' in t for t in r['text']), r)
    return detail


def scenario_2():
    g = new_game(badge02=True)
    go_flowershop(g)
    first = talk(g, K.KEY_UP)
    b1 = bag(g, ITEM_SQUIRT_BOTTLE)
    second = talk(g, K.KEY_UP)
    b2 = bag(g, ITEM_SQUIRT_BOTTLE)
    detail = dict(first=first, bottle_after_1=b1, second=second, bottle_after_2=b2)
    record('2 bottle gifted by the real Flower Shop NPC, idempotent',
           first['dialogue'] and b1 == 1 and b2 == 1
           and any('Use my SQUIRTBOTTLE' in t for t in first['text']), detail)
    g2 = new_game(badge02=True)
    go_street(g2)
    r = talk(g2, K.KEY_UP)
    record('2b duplicate outdoor NPC also gifts the bottle',
           bool(r['dialogue']) and bag(g2, ITEM_SQUIRT_BOTTLE) == 1,
           dict(text=r['text'], bottle=bag(g2, ITEM_SQUIRT_BOTTLE)))


def scenario_3():
    g = new_game(badge02=True)
    go_tree(g)
    r = talk(g, K.KEY_UP)
    r['cleared'] = g.flag('FLAG_POX_SUDOWOODO_CLEARED')
    record('3 tree with badge but no bottle refuses', bool(r['dialogue']) and not r['battle']
           and any('feels like stone' in t for t in r['text']) and not r['cleared'], r)


def scenario_4():
    """Run 5: there is no YES/NO box any more, so nothing can wedge the player.

    The engine cannot answer NO on a field YES/NO box (scenario 10 is the
    control), so the tree now follows the Gen 2/4 convention: watering it
    starts the battle and asks nothing.
    """
    g = new_game(badge02=True, party=True)
    armed(g)
    go_tree(g)
    g.clear_text()
    g.tap(K.KEY_UP, hold=2, wait=16)
    g.frame(20)
    before = context(g)
    seen = []
    for _ in range(200):
        t = g.text()
        if t and (not seen or seen[-1] != t):
            seen.append(t)
        if in_battle(g):
            break
        g.tap(K.KEY_A, hold=2, wait=16)
        if finished(g):
            break
    detail = dict(seen=seen, before=before, after=context(g),
                  battle=in_battle(g),
                  cleared=g.flag('FLAG_POX_SUDOWOODO_CLEARED'),
                  bottle=bag(g, ITEM_SQUIRT_BOTTLE))
    detail['no_yesno_prompt'] = not any('Sprinkle it with the' in t for t in seen)
    detail['plain_message'] = any('spray' in t for t in seen)
    record('4a the tree shows a plain message, never a YES/NO box',
           detail['no_yesno_prompt'] and detail['plain_message'], detail)
    # A plain message box advances on either button, so B is no longer a trap.
    g.tap(K.KEY_B, hold=2, wait=30)
    g.frame(120)
    detail['after_b'] = context(g)
    detail['battle_after_b'] = wait_for_battle(g)
    record('4b FIXED (was: B cannot answer No): the message clears on B and the '
           'battle follows', detail['battle_after_b'], detail)
    return g


def scenario_5():
    g = new_game(badge02=True, party=True)
    armed(g)
    go_tree(g)
    g.frame(30)
    tree_screen = g.hash()                # the tree sprite, before the battle
    r = talk(g, K.KEY_UP)
    prompt = [t for t in r['text'] if 'spray' in t]
    assert wait_for_battle(g), 'the wild battle never started'
    enemy = battle_mon(g, 1)
    detail = dict(prompt=prompt, enemy=enemy,
                  battle_type_flags=g.u32(g.syms['gBattleTypeFlags']),
                  metamon_arena=g.u32(g.syms['sMetamon']),
                  metamon_fault=g.u32(g.syms['gMetamonFault']),
                  metamon_decisions=g.u32(g.syms['gMetamonDecisions']),
                  party_size=g.count())
    ok = (bool(prompt) and r['battle']
          and enemy['species'] == SPECIES_SUDOWOODO and enemy['level'] == 20
          and enemy['moves'] == list(SPECIES_MIMIC_MONS) and enemy['ivs'] == [31] * 6
          and enemy.get('ability') == ABILITY_STURDY_ID
          and not (detail['battle_type_flags'] & 0x0B)
          and detail['metamon_arena'] == 0 and detail['metamon_fault'] == 0
          and detail['metamon_decisions'] == 0)
    record('5a accept -> wild battle, species/level/moves/IVs/no Metamon', ok, detail)
    g.shot('sudowoodo_battle.png')
    steps = fight(g, 'attack')
    outcome = g.u8(g.syms['gBattleOutcome'])
    drain(g)
    cleared = g.flag('FLAG_POX_SUDOWOODO_CLEARED')
    bottle = bag(g, ITEM_SQUIRT_BOTTLE)
    g.warp('GoldenrodCity_hns', 27, 16)
    g.frame(120)
    go_tree(g)
    g.frame(30)
    cleared_screen = g.hash()
    revisit = talk(g, K.KEY_UP)
    detail2 = dict(outcome=outcome, cleared=cleared, steps=steps, bottle_after=bottle,
                   revisit=revisit, post_battle_text=g.text(),
                   tree_sprite_removed=tree_screen != cleared_screen,
                   screen_with_tree=tree_screen[:8], screen_after=cleared_screen[:8])
    g.shot('sudowoodo_cleared.png')
    record('5b win clears the tree, flag persists, no respawn on re-entry, '
           'bottle taken back (P3)',
           outcome == 1 and cleared and not revisit['dialogue'] and not revisit['battle']
           and g.flag('FLAG_POX_SUDOWOODO_CLEARED') and bottle == 0, detail2)


def scenario_6():
    g = new_game(badge02=True, party=True)
    armed(g)
    go_tree(g)
    talk(g, K.KEY_UP)
    assert wait_for_battle(g), 'the wild battle never started'
    try:
        fight(g, 'run', limit=8000)
        outcome = g.u8(g.syms['gBattleOutcome'])
    except AssertionError as exc:
        outcome = 'timeout %s' % exc
    steps = dict(after_fight=context(g))
    back = return_to_field(g)
    steps['after_return'] = context(g)
    g.frame(300)
    steps['after_300_idle'] = context(g)
    settled = drain(g)
    g.frame(400)                       # let the post-battle fade finish
    steps['after_drain'] = context(g)
    steps['before_reprompt'] = context(g)
    moved_down = walk(g, K.KEY_DOWN)
    walk(g, K.KEY_UP)
    again = talk(g, K.KEY_UP, stop_at='spray')
    detail = dict(outcome=outcome, back_to_field_after=back, settled=settled, steps=steps,
                  cleared=g.flag('FLAG_POX_SUDOWOODO_CLEARED'),
                  moved_down=moved_down,
                  bottle=bag(g, ITEM_SQUIRT_BOTTLE),
                  re_prompt=again['text'], re_prompt_stopped=again['stopped'])
    record('6 running away keeps the Sudowoodo, the flag unset and the player free',
           outcome == 4 and detail['cleared'] is False
           and moved_down[0] != moved_down[1] and again['stopped'],
           detail)


def scenario_7():
    """Real Master Ball catch: B_OUTCOME_CAUGHT must clear the obstruction."""
    g = new_game(badge02=True, party=True)
    give_item(g, ITEM_MASTER_BALL, 1)
    armed(g)
    go_tree(g)
    talk(g, K.KEY_UP)
    assert wait_for_battle(g), 'the wild battle never started'
    thrown = 0
    for _ in range(3):
        if g.controller('HandleInputChooseAction'):
            thrown = throw_ball(g)
        if thrown:
            break
        for _ in range(300):
            g.frame(1)
            if g.controller('HandleInputChooseAction'):
                break
    back = settle_overworld(g)
    outcome = g.u8(g.syms['gBattleOutcome'])
    cleared = g.flag('FLAG_POX_SUDOWOODO_CLEARED')
    stride = g.sizes['gParties'] // 24

    def safe(addr):
        try:
            return g.box_species(addr)
        except AssertionError:
            return -1
    party = [safe(g.syms['gParties'] + i * stride) for i in range(g.count())]
    storage = g.u32(g.syms['gPokemonStoragePtr'])
    boxsize = g.sizes['gParties'] // 24 - 20
    in_box = any(safe(storage + 4 + boxsize * i) == SPECIES_SUDOWOODO for i in range(30))
    revisit = talk(g, K.KEY_UP)
    detail = dict(balls_thrown=thrown, back_to_overworld_after=back, outcome=outcome,
                  cleared=cleared, party=party, in_storage=in_box,
                  bottle=bag(g, ITEM_SQUIRT_BOTTLE), revisit=revisit['text'])
    g.shot('sudowoodo_caught.png')
    record('7 catching Sudowoodo (B_OUTCOME_CAUGHT) clears the obstruction and '
           'takes the bottle back (P3)',
           thrown == 1 and outcome == 7 and cleared and not revisit['dialogue']
           and (SPECIES_SUDOWOODO in party or in_box) and detail['bottle'] == 0, detail)


def scenario_8():
    g = new_game(badge02=False, triggers=False)
    go_flowershop(g)
    shop = talk(g, K.KEY_UP)
    b1 = bag(g, ITEM_SQUIRT_BOTTLE)
    go_tree(g)
    tree = talk(g, K.KEY_UP)
    moved = walk(g, K.KEY_DOWN)      # Route 36 has open tiles below the tree
    detail = dict(shop=shop, shop_bottle=b1, tree=tree, battle=in_battle(g),
                  controls_locked=g.u8(g.syms['sLockFieldControls']),
                  walked=moved[0] != moved[1], walk=moved)
    record('8 triggers disabled: scripts inert, no soft-lock',
           b1 == 0 and not in_battle(g) and detail['walked']
           and not any(t.strip() for t in shop['text'])
           and not any(t.strip() for t in tree['text']), detail)


def scenario_9():
    g = new_game(badge02=True, party=True)
    for b in range(1, 9):
        g.flag('FLAG_BADGE%02d_GET' % b, True)
    armed(g)
    go_tree(g)
    talk(g, K.KEY_UP)
    assert wait_for_battle(g), 'the wild battle never started'
    detail = dict(flags=g.u32(g.syms['gBattleTypeFlags']),
                  arena=g.u32(g.syms['sMetamon']),
                  fault=g.u32(g.syms['gMetamonFault']),
                  party=g.count(), enemy=battle_mon(g, 1))
    for _ in range(900):
        g.frame(1)
        if g.u32(g.syms['gMetamonDecisions']):
            break
    detail['decisions'] = g.u32(g.syms['gMetamonDecisions'])
    detail['fault_after_turn'] = g.u32(g.syms['gMetamonFault'])
    record('9 6 mons + 8 badges is still a plain wild battle (no Metamon)',
           detail['arena'] == 0 and detail['decisions'] == 0
           and detail['fault_after_turn'] == 0 and detail['party'] == 6
           and detail['enemy']['species'] == SPECIES_SUDOWOODO, detail)
    fight(g, 'attack')
    drain(g)
    record('9b post-battle flag with 8 badges',
           g.flag('FLAG_POX_SUDOWOODO_CLEARED'),
           dict(cleared=g.flag('FLAG_POX_SUDOWOODO_CLEARED'), outcome=g.u8(g.syms['gBattleOutcome'])))


def scenario_10():
    """Control: is the unusable B button specific to the Sudowoodo prompt?

    PalletTown_EventScript_ProfOakTeam is a plain (non-Plastic Ox) YES/NO
    dialog, so the same measurement isolates the engine's button handling.
    """
    g = new_game(badge02=True)
    g.flag('FLAG_POX_HIDE_BATTLE_OAK_PALLET', False)
    g.warp('PalletTown_Frlg', 10, 9)
    g.frame(120)
    r = talk(g, K.KEY_UP, stop_at='head to LANCE')
    before = context(g)
    g.tap(K.KEY_B, hold=2, wait=30)
    g.frame(60)
    after = context(g)
    detail = dict(text=r['text'], stopped=r['stopped'], before_b=before, after_b=after)
    record('10 CONTROL: B is equally inert on a vanilla YES/NO box',
           before['status'] == 1 and after['status'] == 1 and after['locked'] == 1, detail)


def scenario_11():
    """Run 5 (P6): the scripted Sudowoodo must be the same mon every time.

    Before the fix the ability was re-rolled from a random personality, so two
    attempts could produce different ability ids (RUN AWAY and STURDY were both
    observed in run 4).
    """
    abilities = []
    for _ in range(3):
        g = new_game(badge02=True, party=True)
        armed(g)
        go_tree(g)
        talk(g, K.KEY_UP)
        assert wait_for_battle(g), 'the wild battle never started'
        abilities.append(battle_mon(g, 1))
    detail = dict(ability_ids=[m['ability'] for m in abilities],
                  species=[m['species'] for m in abilities],
                  moves=[m['moves'] for m in abilities],
                  levels=[m['level'] for m in abilities])
    ok = (len({m['ability'] for m in abilities}) == 1
          and {m['species'] for m in abilities} == {SPECIES_SUDOWOODO}
          and {tuple(m['moves']) for m in abilities} == {tuple(SPECIES_MIMIC_MONS)})
    record('11 FIXED (was: ability re-rolled): three attempts give one Sudowoodo',
           ok, detail)


SCENARIOS = {1: scenario_1, 2: scenario_2, 3: scenario_3, 4: scenario_4, 5: scenario_5,
             6: scenario_6, 7: scenario_7, 8: scenario_8, 9: scenario_9,
             10: scenario_10, 11: scenario_11}


if __name__ == '__main__':
    want = [int(a) for a in sys.argv[1:]] or sorted(SCENARIOS)
    t0 = time.time()
    for n in want:
        print('--- scenario %d ---' % n, flush=True)
        try:
            SCENARIOS[n]()
        except Exception as exc:
            traceback.print_exc()
            record('scenario %d crashed' % n, False, repr(exc))
    out = ROOT / 'plastic_ox/demo/sudowoodo_results.json'
    out.write_text(json.dumps(RESULTS, indent=1))
    print('wrote %s in %.1fs' % (out, time.time() - t0), flush=True)
    print('failures:', [r['scenario'] for r in RESULTS if not r['ok']], flush=True)
