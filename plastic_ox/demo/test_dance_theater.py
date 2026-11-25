#!/usr/bin/env python3
"""Ecruteak Dance Theater: the Kimono troupe as one battle, played in mGBA.

Proves, walking with the D-pad between stops:
* the five dancers stand in a semicircle on the stage, open toward the
  audience, with NAOKO at its centre (static check of map.json);
* before the dance a side dancer only talks, and points the player at NAOKO;
* NAOKO, approached from inside the circle, starts ONE battle:
  TRAINER_PLASTIC_OX_KIMONO_TROUPE with EEVEE, JOLTEON, VAPOREON, FLAREON,
  UMBREON, ESPEON in that order;
* winning sets all five FLAG_POX_KIMONO_* flags; the side dancer then gives her
  after-dance line, and the mistress by the door gives the EEVEE.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pox_fixtures import ROOT, at, finish_trainer, game, shot  # noqa: E402
from test_story import StoryGame  # noqa: E402
from test_sudowoodo_v1 import settle, talk  # noqa: E402
from walk_leg1 import navigate  # noqa: E402
from walklib import K  # noqa: E402

MAP = 'PlasticOx_DanceTheater'
DANCERS = ['VAPOREON', 'JOLTEON', 'FLAREON', 'ESPEON', 'UMBREON']
# national dex ids, battle order
TROUPE = [('Eevee', 133, 27), ('Jolteon', 135, 28), ('Vaporeon', 134, 28),
          ('Flareon', 136, 28), ('Umbreon', 197, 28), ('Espeon', 196, 29)]


def static_checks():
    objs = json.loads((ROOT / f'data/maps/{MAP}/map.json').read_text())['object_events']
    stage = {o['script']: (o['x'], o['y'], o['movement_type']) for o in objs
             if o['graphics_id'] == 'OBJ_EVENT_GFX_KIMONO_HNS'}
    assert stage == {
        'Pox_KimonoJolteon': (6, 4, 'MOVEMENT_TYPE_FACE_RIGHT'),
        'Pox_KimonoEspeon': (8, 3, 'MOVEMENT_TYPE_FACE_DOWN'),
        'Pox_KimonoTroupe': (10, 2, 'MOVEMENT_TYPE_FACE_DOWN'),
        'Pox_KimonoUmbreon': (12, 3, 'MOVEMENT_TYPE_FACE_DOWN'),
        'Pox_KimonoFlareon': (14, 4, 'MOVEMENT_TYPE_FACE_LEFT'),
    }, stage
    # Symmetric arc around NAOKO's column, open toward the audience.
    xs = sorted(x for x, _, _ in stage.values())
    assert all(a + b == 20 for a, b in zip(xs, reversed(xs))), xs
    print('ok  five dancers in a semicircle, NAOKO at the centre', flush=True)


def enemy_party(g):
    count = g.u8(g.u32(g.syms['gEnemyPartyCountPtr']))
    stride = g.sizes['gParties'] // 24
    base = g.u32(g.syms['gEnemyPartyPtr']) if 'gEnemyPartyPtr' in g.syms else g.syms['gParties'] + 6 * stride
    return [(StoryGame.box_species(g, base + i * stride), g.u8(base + i * stride + 84)) for i in range(count)]


def main():
    static_checks()
    g = game()
    for name in ('FLAG_POX_STORY_STARTER', 'FLAG_ADVENTURE_STARTED', 'FLAG_BADGE01_GET', 'FLAG_BADGE02_GET'):
        g.flag(name, True)
    for s in DANCERS:
        assert not g.flag('FLAG_POX_KIMONO_' + s)
    g.warp(MAP, 10, 16)
    settle(g)
    assert at(g, MAP), g.describe()

    navigate(g, (7, 4))
    r = talk(g, K.KEY_LEFT)
    text = ' '.join(r['text'])
    assert 'NAOKO' in text and not r['battle'], r
    print('ok  SAYO talks before the dance and points at NAOKO', flush=True)

    navigate(g, (10, 3))
    shot(g, 'dance_theater_circle')
    r = talk(g, K.KEY_UP)
    assert r['battle'], r
    trainer_id = g.u16(g.syms['gTrainerBattleParameter'] + 2)
    want = re.search(r'#define TRAINER_PLASTIC_OX_KIMONO_TROUPE (\d+)',
                     (ROOT / 'include/constants/opponents.h').read_text())
    assert trainer_id == int(want[1]), trainer_id
    party = enemy_party(g)
    # Levels follow the fixture's player party (trainer level scaling), so
    # only species and order are checked here; levels are in trainers.party.
    assert [dex for dex, _ in party] == [dex for _, dex, _ in TROUPE], party
    print('ok  NAOKO starts one battle: ' + ', '.join(n for n, _, _ in TROUPE), flush=True)

    finish_trainer(g, True)
    settle(g)
    g.write(g.syms['gBattleTypeFlags'], 0, 4)
    assert at(g, MAP)
    for s in DANCERS:
        assert g.flag('FLAG_POX_KIMONO_' + s), s
    print('ok  winning sets all five KIMONO flags', flush=True)

    r = talk(g, K.KEY_UP)
    assert 'dusk' in ' '.join(r['text']) and not r['battle'], r
    navigate(g, (7, 4))
    r = talk(g, K.KEY_LEFT)
    assert 'quick step' in ' '.join(r['text']) and not r['battle'], r
    print('ok  NAOKO and SAYO give their after-dance lines', flush=True)

    navigate(g, (5, 14))
    r = talk(g, K.KEY_DOWN, max_taps=400)
    assert g.flag('FLAG_POX_GIFT_KIMONO'), r
    print('ok  the mistress gives the EEVEE', flush=True)
    print('PASS: Dance Theater troupe battle')


if __name__ == '__main__':
    main()
