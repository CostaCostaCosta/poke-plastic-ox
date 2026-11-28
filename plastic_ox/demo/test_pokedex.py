#!/usr/bin/env python3
"""Pokedex area and evolution pages.

Area page: it draws the Plastic Ox region map and lights map sections from
every map group. For a species found on a Johto route (a Plastic Ox map group
the vanilla screen ignored) the route's cell glows; for one found in the Burned
Tower, which has no cell of its own, a marker is shown. Nothing is lit outside
the maps listed in plastic_ox_dex_area_maps.h. Dragon's Den is marked on
Blackthorn and New Mauville has a cell beside Route 110.

Evolution page: only Gen 3 species are listed. Koffing shows Weezing without a
region condition and without Galarian Weezing; Magneton has no evolution.
Forms page: Weezing has no forms (Galarian Weezing is gone), Castform keeps its.

Engine: GetEvolutionTargetSpecies is called in the ROM. A Thunder Stone does
nothing for Magneton (Magnezone), still evolves Pikachu, and Koffing still
levels into Weezing.

Screenshots go to plastic_ox/demo/shots/pokedex_*.png.
"""
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_story import StoryGame, ROOT
from test_qol import opcode, begin_code
from walklib import K

ROM_SIZE = 0x2000000
FLAG_SET_CAUGHT = 3


def enum_values(path, prefix):
    """Values of a C enum whose members start with prefix (no expressions)."""
    out, nxt = {}, 0
    for name, value in re.findall(r'^\s*(' + prefix + r'\w+)(?:\s*=\s*(\w+))?,', path.read_text(), re.M):
        if value:
            nxt = int(value, 0) if value[0].isdigit() else out[value]
        out[name] = nxt
        nxt += 1
    return out


SPECIES = enum_values(ROOT / 'include/constants/species.h', 'SPECIES_')
MAPSEC = enum_values(ROOT / 'include/constants/region_map_sections.h', 'MAPSEC_')
EVO = enum_values(ROOT / 'include/constants/pokemon.h', 'EVO_MODE_')
EVO.update(enum_values(ROOT / 'include/constants/pokemon.h', '(?:CHECK|DO)_EV'))


def static_expectations():
    """(species -> map sections any of its shown tables sit in, placed cells)."""
    shown = set(re.findall(r'MAP_GROUP\((\w+)\)',
                           (ROOT / 'src/data/region_map/plastic_ox_dex_area_maps.h').read_text()))
    assert shown, 'no maps in plastic_ox_dex_area_maps.h'
    cells = set(re.findall(r'MAPSEC_\w+', (ROOT / 'src/data/region_map/region_map_layout.h').read_text()))
    section = {}
    for path in (ROOT / 'data/maps').glob('*/map.json'):
        data = json.loads(path.read_text())
        section[data['id']] = data.get('region_map_section')
    where, tables = {}, {}
    wild = json.loads((ROOT / 'src/data/wild_encounters.json').read_text())
    for enc in wild['wild_encounter_groups'][0]['encounters']:
        if enc['map'] not in shown:
            continue
        found = {m['species'] for v in enc.values() if isinstance(v, dict) for m in v.get('mons', [])}
        tables.setdefault(enc['map'], []).append(found)
        for s in found:
            where.setdefault(s, set()).add(section[enc['map']])
    # Donor maps that were replaced must not be listed.
    for dead in ('MAP_ROUTE24', 'MAP_ROUTE25', 'MAP_CERULEAN_CAVE_1F'):
        assert dead not in shown, dead
    return where, cells, tables, shown


def always_on(tables, map_id):
    """A Gen 3 species in every time-of-day table of a map."""
    common = set.intersection(*tables[map_id])
    return sorted(s for s in common if SPECIES[s] <= SPECIES['SPECIES_DEOXYS'])[0]


def text(s):
    return bytes(0xBB + ord(c) - 65 if c.isupper() else 0xD5 + ord(c) - 97 if c.islower() else 0 for c in s)


def string_var4(g):
    a = g.syms['gStringVar4']
    return bytes(g.u8(a + i) for i in range(200)).split(b'\xff')[0]


def set_caught(g, species):
    code = b''.join(opcode(g, 'callnative') + struct.pack('<IHH', (g.syms['Scrcmd_getsetpokedexflag'] | 1) + ROM_SIZE,
                                                          SPECIES[s], FLAG_SET_CAUGHT) for s in species)
    # The player gets the National Dex with the Pokedex (plastic_ox_pallet.inc).
    code += opcode(g, 'callnative') + struct.pack('<I', g.syms['EnableNationalPokedex'] | 1)
    begin_code(g, code + opcode(g, 'releaseall') + opcode(g, 'end'))
    g.frame(30)
    assert g.u8(g.syms['sGlobalScriptContextStatus']) == 2


def open_dex(g):
    main = g.syms['gMain']
    g.write(main + 8, g.syms['CB2_ReturnToField'] | 1, 4)
    g.write(main + 0x438, 0)
    g.write(main + 4, g.syms['CB2_OpenPokedexPlusHGSS'] | 1, 4)
    g.frame(150)


def close_dex(g):
    g.tap(K.KEY_B)
    g.frame(150)


def list_index(g, species):
    view = g.u32(g.syms['sPokedexView'])
    for i in range(1100):
        if g.u16(view + 4 * i) == SPECIES[species] and g.u16(view + 4 * i + 2) & 3 == 3:
            return i
    raise AssertionError(species + ' is not caught in the Pokedex list')


def area_page(g, species):
    """Open species' area page; return [(glowing sections, marked sections)] for each time-of-day tab."""
    open_dex(g)
    index = list_index(g, species)
    close_dex(g)
    g.write(g.syms['sLastSelectedPokemon'], index, 2)
    open_dex(g)
    g.tap(K.KEY_A)
    g.frame(150)
    g.tap(K.KEY_RIGHT)
    g.frame(240)
    area = g.u32(g.syms['sPokedexAreaScreen'])
    assert area, 'area screen did not open'
    g.shot('pokedex_area_' + species.replace('SPECIES_', '').lower())
    tabs, times = [], set()
    for _ in range(3):                    # morning, day, night: DOWN moves to the next tab
        times.add(g.u8(g.syms['gAreaTimeOfDay']))
        glow = {g.u16(area + 0x10 + 4 * i + 2) for i in range(g.u16(area + 0x110))}
        marks = {g.u16(area + 0x620 + 2 * i) for i in range(g.u16(area + 0x112))}
        tabs.append((glow, marks))
        g.tap(K.KEY_DOWN)
        g.frame(120)
    assert len(times) == 3, times
    return tabs


def evolution_page(g, species):
    """From the area page: stats, then evolutions. Returns the last printed line."""
    g.tap(K.KEY_RIGHT)
    g.frame(200)
    g.tap(K.KEY_RIGHT)
    g.frame(200)
    g.shot('pokedex_evo_' + species.replace('SPECIES_', '').lower())
    return string_var4(g)


def forms_page(g, species):
    """From the evolution page: START opens the forms page."""
    g.tap(K.KEY_START)
    g.frame(240)
    g.shot('pokedex_forms_' + species.replace('SPECIES_', '').lower())
    return string_var4(g)


def evolution_target(g, slot, mode, item=0):
    """GetEvolutionTargetSpecies(party[slot], mode, item, NULL, NULL, CHECK_EVO), run in the ROM."""
    base = (g.syms['gStringVar3'] + 3) & ~3
    mon = g.syms['gParties'] + slot * (g.sizes['gParties'] // 24)
    thumb = [0xB510, 0xB082, 0x2300, 0x9300, 0x2400 | EVO['CHECK_EVO'], 0x9401,   # push; args 5 and 6 on the stack
             0x4806, 0x4907, 0x4A07, 0x4C08,                                     # r0-r2, r4 from the pool
             0xF000, 0xF806,                                                     # bl to "bx r4"
             0x4907, 0x8008, 0x2000, 0xB002, 0xBD10, 0x46C0,                     # store result; return FALSE
             0x4720, 0x46C0]                                                     # bx r4
    pool = [mon, EVO[mode], item, g.syms['GetEvolutionTargetSpecies'] | 1, base + 0x3C, 0xFFFF]
    for i, b in enumerate(struct.pack('<20H6I', *thumb, *pool)):
        g.write(base + i, b)
    begin_code(g, opcode(g, 'callnative') + struct.pack('<I', base | 1) + opcode(g, 'end'))
    g.frame(30)
    assert g.u8(g.syms['sGlobalScriptContextStatus']) == 2
    return g.u16(base + 0x3C)


def give_mon(g, species, level):
    begin_code(g, opcode(g, 'callnative') + struct.pack('<I', g.syms['ScrCmd_createmon'] | 1)
               + struct.pack('<BBHHI', 0, 6, SPECIES[species], level, 0) + opcode(g, 'end'))
    g.frame(30)
    assert g.u8(g.syms['sGlobalScriptContextStatus']) == 2
    return g.count() - 1


def engine_tests(g):
    for n in range(1, 9):                 # evolution tiers unlock with badges
        g.flag(f'FLAG_BADGE0{n}_GET', 1)
    # The Pikachu check below also proves this is the right item id.
    stone = enum_values(ROOT / 'include/constants/items.h', '')['ITEM_THUNDER_STONE']
    magneton = give_mon(g, 'SPECIES_MAGNETON', 40)
    pikachu = give_mon(g, 'SPECIES_PIKACHU', 40)
    koffing = give_mon(g, 'SPECIES_KOFFING', 40)
    assert g.party_species(magneton) == SPECIES['SPECIES_MAGNETON']
    got = evolution_target(g, magneton, 'EVO_MODE_ITEM_CHECK', stone)
    assert got == 0, f'Magneton + Thunder Stone -> species {got}'
    got = evolution_target(g, pikachu, 'EVO_MODE_ITEM_CHECK', stone)
    assert got == SPECIES['SPECIES_RAICHU'], f'Pikachu + Thunder Stone -> species {got}'
    got = evolution_target(g, koffing, 'EVO_MODE_NORMAL')
    assert got == SPECIES['SPECIES_WEEZING'], f'Koffing level 40 -> species {got}'
    print('ok  engine: Magneton cannot become Magnezone; Pikachu and Koffing still evolve')


def leave(g):
    # Page -> info screen -> list -> field.
    for _ in range(3):
        close_dex(g)
    assert g.u32(g.syms['gMain'] + 4) & ~1 == g.syms['CB2_Overworld'] & ~1, g.shot('pokedex_stuck')


def main():
    where, cells, tables, shown = static_expectations()
    route = always_on(tables, 'MAP_ROUTE29_HNS')
    tower = always_on(tables, 'MAP_PLASTIC_OX_BURNED_TOWER')
    den = always_on(tables, 'MAP_DRAGONS_DEN_CAVERN_HNS')
    mauville = always_on(tables, 'MAP_NEW_MAUVILLE_INSIDE')
    print('ok  area maps list is generated and skips replaced donor maps')

    g = StoryGame()
    engine_tests(g)
    set_caught(g, [route, tower, den, mauville, 'SPECIES_KOFFING', 'SPECIES_MAGNETON', 'SPECIES_WEEZING',
                   'SPECIES_CASTFORM'])

    for species, sec, kind in ((route, 'MAPSEC_ROUTE_29', 'glow'), (tower, 'MAPSEC_BURNED_TOWER', 'mark'),
                               (den, 'MAPSEC_DRAGONS_DEN', 'mark'), (mauville, 'MAPSEC_NEW_MAUVILLE', 'glow'),
                               ('SPECIES_KOFFING', None, None)):
        for glow, marks in area_page(g, species):
            want = {MAPSEC[s] for s in where.get(species, set())}
            assert glow | marks <= want, (species, glow, marks, want)
            assert glow <= {MAPSEC[s] for s in cells}, (species, glow)
            assert not marks & {MAPSEC[s] for s in cells}, (species, marks)
            if kind == 'glow':
                assert MAPSEC[sec] in glow, (species, glow)
            elif kind == 'mark':
                assert MAPSEC[sec] in marks, (species, marks)
        print(f'ok  area page {species}: {len(glow)} cells, {len(marks)} markers at every time of day')
        if species != 'SPECIES_KOFFING':
            leave(g)

    line = evolution_page(g, 'SPECIES_KOFFING')
    assert bytes([0xA4, 0xA6]) in line, line.hex()           # "35"
    assert text('Galar') not in line and text('out of') not in line, line.hex()
    leave(g)
    print('ok  Koffing evolves into Weezing only, with no region condition')

    area_page(g, 'SPECIES_MAGNETON')
    line = evolution_page(g, 'SPECIES_MAGNETON')
    assert text('has no evolution') in line, line.hex()
    leave(g)
    print('ok  Magneton lists no evolution')

    area_page(g, 'SPECIES_WEEZING')
    evolution_page(g, 'SPECIES_WEEZING')
    line = forms_page(g, 'SPECIES_WEEZING')
    assert text('has no alternate forms') in line, line.hex()
    for _ in range(4):
        close_dex(g)
    area_page(g, 'SPECIES_CASTFORM')
    evolution_page(g, 'SPECIES_CASTFORM')
    line = forms_page(g, 'SPECIES_CASTFORM')
    assert text('has no alternate forms') not in line, line.hex()
    print('ok  forms page: Weezing has none, Castform keeps its forms')


if __name__ == '__main__':
    main()
