"""Install the Ruins of Alph and the three Regis after region generation.

The converted maps live in ruins_of_alph/ (written once by
import_ruins_of_alph.py). This module owns, on top of them:

* the gatehouse researcher, the dig-site signs and its three field staff;
* one Regi and its sage in the back room of three chambers (Regirock north,
  Registeel south-west, Regice south-east), sealed by the chamber's tablet.
  The battle scripts stay in tournament/events.inc (PoxTournament_Regirock,
  _Regice, _Registeel): same tablet check, badge gate and caught flag as when
  they stood in the Route 127 caves;
* the research centre's two staff, the surveyor in the hall under the chambers
  (B1F), and the floor holes behind each Regi, which stay shut until it is caught;
* the wild tables for the dig site and the hall.

Route 36's researcher, gate warps and step triggers are placed by region_v7.py;
his script is in data/maps/Route36_hns/scripts.inc. tournament.install, which
runs first, clears the Regis out of the old Route 127 caves.
"""
import json
from pathlib import Path

BASE = Path(__file__).with_suffix('')
GATE = 'Gate_RuinsOfAlph_Route36_hns'
OUTSIDE = 'RuinsOfAlph_Outside_hns'
CHAMBERS = 'RuinsOfAlph_PuzzleAndRewardChambers_hns'
LAB = 'RuinsOfAlph_Lab_hns'
B1F = 'RuinsOfAlph_B1F_hns'
WILD_LABEL = 'gPoxUURuinsOfAlphOutside'
WILD_LABEL_B1F = 'gPoxUURuinsOfAlphB1F'

# (species, tablet word, back-wall door, sage, Regi) per chamber. The door is
# warp 4/6/8 of the chambers map; its back room is the donor's reward room.
# The Regi sprites are four tiles big, so each sage stands two rows in front.
REGIS = [
    ('Regirock', 'Rock', (21, 1), (20, 39), (21, 37)),      # north chamber, on the main site
    ('Registeel', 'Steel', (5, 18), (4, 56), (5, 54)),      # south-west chamber
    ('Regice', 'Ice', (21, 18), (20, 56), (21, 54)),        # south-east chamber
]
# The west chamber has no Regi: its back wall stands open (import_ruins_of_alph.py)
# and the floor hole in its back room is the unguarded way down to the hall.
# Sliding-panel tiles (solid since the import), one script per chamber.
PANELS = {'North': [(20, 5), (21, 5)], 'West': [(4, 5), (5, 5)],
          'SouthWest': [(4, 22), (5, 22)], 'SouthEast': [(20, 22), (21, 22)]}


def npc(local_id, gfx, x, y, script, flag='0', movement='MOVEMENT_TYPE_FACE_DOWN', elevation=3):
    event = dict(graphics_id='OBJ_EVENT_GFX_' + gfx, x=x, y=y, elevation=elevation,
                 movement_type=movement, movement_range_x=0, movement_range_y=0,
                 trainer_type='TRAINER_TYPE_NONE', trainer_sight_or_berry_tree_id='0',
                 script=script, flag=flag)
    return dict(local_id=local_id, **event) if local_id else event


def sign(x, y, script):
    return dict(type='sign', x=x, y=y, elevation=0,
                player_facing_dir='BG_EVENT_PLAYER_FACING_ANY', script=script)


def mons(*rows):
    return [dict(min_level=lo, max_level=hi, species='SPECIES_' + species) for species, lo, hi in rows]


def wild_tables():
    """Species already obtainable by the Cinnabar checkpoint (UU), at its levels,
    plus Unown (PU) in the hall, which is found nowhere else."""
    return [{
        'map': 'MAP_RUINS_OF_ALPH_B1F_HNS',
        'base_label': WILD_LABEL_B1F,
        'land_mons': {'encounter_rate': 7, 'mons': mons(*[('UNOWN', 36, 38)] * 12)},
    }, {
        'map': 'MAP_RUINS_OF_ALPH_OUTSIDE_HNS',
        'base_label': WILD_LABEL,
        'land_mons': {'encounter_rate': 21, 'mons': mons(
            ('XATU', 37, 39), ('GIRAFARIG', 37, 39), ('NATU', 36, 38), ('BALTOY', 36, 38),
            ('XATU', 38, 39), ('GIRAFARIG', 38, 39), ('NATU', 37, 38), ('BALTOY', 37, 38),
            ('XATU', 38, 39), ('GIRAFARIG', 38, 39), ('NATU', 38, 39), ('BALTOY', 38, 39))},
        'water_mons': {'encounter_rate': 4, 'mons': mons(
            ('QUAGSIRE', 36, 38), ('WOOPER', 34, 36), ('QUAGSIRE', 37, 39),
            ('WOOPER', 35, 37), ('QUAGSIRE', 38, 39))},
    }]


def install(read, put):
    manifest = json.loads((BASE / 'source_manifest.json').read_text())
    maps = {name: json.loads((BASE / f'{name}.json').read_text()) for name in manifest['maps']}

    maps[GATE]['object_events'] = [
        npc(None, 'SCIENTIST_1', 3, 5, 'PoxRuins_GateResearcher', movement='MOVEMENT_TYPE_FACE_RIGHT'),
    ]

    maps[OUTSIDE]['object_events'] = [
        npc(None, 'LASS', 26, 13, 'PoxRuins_Student'),
        npc(None, 'HIKER', 27, 31, 'PoxRuins_Surveyor'),
        npc(None, 'MAN_3', 16, 37, 'PoxRuins_Digger', movement='MOVEMENT_TYPE_FACE_LEFT'),
    ]
    maps[OUTSIDE]['bg_events'] = [
        sign(31, 24, 'PoxRuins_SiteSign'),
        sign(37, 16, 'PoxRuins_LabSign'), sign(38, 16, 'PoxRuins_LabSign'),
        sign(30, 11, 'PoxRuins_NorthChamberSign'),
        sign(38, 27, 'PoxRuins_EastGatehouse'),
    ]

    maps[LAB]['object_events'] = [
        npc(None, 'SCIENTIST_1', 1, 3, 'PoxRuins_Archivist'),
        npc(None, 'SCIENTIST_2', 8, 5, 'PoxRuins_Epigrapher', movement='MOVEMENT_TYPE_FACE_LEFT'),
    ]
    maps[LAB]['bg_events'] = [sign(x, 4, 'PoxRuins_Casts') for x in (5, 6, 7)]
    maps[B1F]['object_events'] = [npc(None, 'HIKER', 19, 16, 'PoxRuins_HallSurveyor')]

    chambers = maps[CHAMBERS]
    for species, word, door, sage_xy, regi_xy in REGIS:
        upper = species.upper()
        script = 'PoxTournament_' + species
        flag = 'FLAG_POX_CAUGHT_' + upper
        chambers['object_events'] += [
            npc(f'LOCALID_POX_{upper}', upper, *regi_xy, script, flag),
            npc(f'LOCALID_POX_{upper}_SAGE', 'SAGE_HNS', *sage_xy, script, flag),
        ]
        chambers['bg_events'].append(sign(*door, f'PoxRuins_{word}Wall'))
    for where, tiles in PANELS.items():
        chambers['bg_events'] += [sign(x, y, f'PoxRuins_Panel{where}') for x, y in tiles]

    for name, data in maps.items():
        put(f'data/maps/{name}/map.json', json.dumps(data, indent=2) + '\n')
        put(f'data/maps/{name}/scripts.inc', (BASE / f'{name}.inc').read_text())

    text = read('data/event_scripts.s')
    for name in maps:
        line = f'\t.include "data/maps/{name}/scripts.inc"\n'
        if line not in text:
            text += '\n' + line
    put('data/event_scripts.s', text)

    # league.install keeps the Victory Road table last; slot ours in before it.
    path = 'src/data/wild_encounters.json'
    wild = json.loads(read(path))
    group = next(g for g in wild['wild_encounter_groups'] if g['label'] == 'gWildMonHeaders')
    entries = [e for e in group['encounters'] if e['base_label'] not in (WILD_LABEL, WILD_LABEL_B1F)]
    at = next((i for i, e in enumerate(entries) if e['base_label'] == 'gPoxVictoryRoadOutdoor'), len(entries))
    entries[at:at] = wild_tables()
    group['encounters'] = entries
    put(path, json.dumps(wild, indent=2) + '\n')


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    install(lambda p: (root / p).read_text(),
            lambda p, s: ((root / p).parent.mkdir(parents=True, exist_ok=True),
                          (root / p).write_text(s)))
