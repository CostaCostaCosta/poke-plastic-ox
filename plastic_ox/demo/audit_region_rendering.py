#!/usr/bin/env python3
"""Walk regional map samples and camera seams; record rendering and coverage.

Uses fresh emulator-only warps to isolate each map. Story and combat are not
under test. Reports unreachable samples rather than claiming full tile coverage.
"""
import json
import re
from pathlib import Path
import struct
import sys
import traceback

from test_story import StoryGame, ROOT
from walk_leg1 import find_path_elev
from walk_demo import step_toward, cross_connection

OUT = ROOT / 'plastic_ox/demo/shots/region_audit'
if '--only-seams' in sys.argv:
    OUT = OUT.with_name('region_seams')
if '--triggers' in sys.argv:
    OUT = OUT.with_name(OUT.name + '_triggers')
OUT.mkdir(exist_ok=True)
groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
maps = {name: json.loads((ROOT / 'data/maps' / name / 'map.json').read_text())
        for group in groups['group_order'] for name in groups[group]}
ids = {name: (i, j) for i, group in enumerate(groups['group_order'])
       for j, name in enumerate(groups[group])}
by_id = {data['id']: name for name, data in maps.items()}
for name in maps:
    by_id.setdefault('MAP_'+name.upper(), name)
for alias, original in re.findall(r'#define\s+(MAP_\w+)\s+(MAP_\w+)', (ROOT/'include/constants/maps.h').read_text()):
    if original in by_id:
        by_id[alias] = by_id[original]
layouts = {d['id']: d for d in json.loads((ROOT / 'data/layouts/layouts.json').read_text())['layouts']}


def geometry(name):
    layout = layouts[maps[name]['layout']]
    raw = (ROOT / layout['blockdata_filepath']).read_bytes()
    return layout['width'], layout['height'], struct.unpack('<' + 'H' * (len(raw)//2), raw)


def setup():
    g = StoryGame(build='triggers' if '--triggers' in sys.argv else '')
    g.flag('FLAG_POX_STORY_STARTER', True)
    g.flag('FLAG_ADVENTURE_STARTED', True)
    # Test-only completed trainers prevent sight battles during visual walks.
    for flag in range(0x500, 0x860):
        g.flag(flag, True)
    return g


def visual(g, label):
    """Independently expand live grid metatiles into the maintained BG view."""
    g.frame(20)
    g.fb.to_pil().convert('RGB').save(OUT / (label + '.png'))
    layout = g.u32(g.syms['gMapHeader'])
    version = g.u8(layout + 24)
    primary = 640 if version in (1, 2) else 512
    camera = g.syms['sFieldCameraOffset']
    tx, ty = g.u8(camera + 2), g.u8(camera + 3)
    state = g.state()
    buffers = [g.u32(g.syms[f'gOverworldTilemapBuffer_Bg{bg}']) for bg in (1, 2, 3)]
    mismatches = 0
    for y in range(15):
        for x in range(15):
            mt, block = g.metatile_at(state['x'] + x - 7, state['y'] + y - 7)
            if block == 0x03FF:  # MAPGRID_UNDEFINED, not every block with ID 1023
                # Unfilled margin resolves through the layout border at draw time.
                bx, by = state['x'] + x - 7, state['y'] + y - 7
                bw, bh = (g.u8(layout+25), g.u8(layout+26)) if version == 1 else (2, 2)
                mt = g.u16(g.u32(layout+8) + 2*((by % bh)*bw + bx % bw)) & 1023
            tileset = g.u32(layout + (16 if mt < primary else 20))
            index = mt if mt < primary else mt-primary
            tiles = [g.u16(g.u32(tileset+12)+16*index+2*i) for i in range(8)]
            attr = (g.u32(g.u32(tileset+16)+4*index) if version == 1
                    else g.u16(g.u32(tileset+16)+2*index))
            layer = (attr >> (29 if version == 1 else 12)) & (3 if version == 1 else 15)
            expected = {0: (tiles[4:], tiles[:4], [0x3014]*4),
                        2: (tiles[4:], [0]*4, tiles[:4]),
                        1: ([0]*4, tiles[4:], tiles[:4])}.get(layer)
            if expected is None:
                raise AssertionError(f'invalid metatile layer {layer}: {mt}')
            offset = ((ty+2*y)%32)*32 + (tx+2*x)%32
            for bg, values in zip(buffers, expected):
                for off, val in zip((0, 1, 32, 33), values):
                    mismatches += g.u16(bg + 2*(offset+off)) != val
    return {'position': [state['x'], state['y']], 'mismatches': mismatches, 'shot': label+'.png'}


def walk(g, target, avoid):
    for _ in range(180):
        state = g.state()
        if (state['x'], state['y']) == target:
            return True
        path = find_path_elev(g, lambda x, y, w, h: (x, y) == target, avoid)
        if not path or len(path) < 2:
            return False
        for current, nxt in zip(path[:4], path[1:5]):
            g.write(g.syms['sWildEncounterImmunitySteps'], 0)
            try:
                step_toward(g, current, nxt)
            except AssertionError:
                return False
            after = g.state()
            if (after['x'], after['y']) != nxt:
                return False
    return False


def main():
    selected = {name for group in groups['group_order'] if 'PlasticOx' in group for name in groups[group]}
    selected |= {e['map'] for e in json.loads((ROOT/'plastic_ox/alpha/story_manifest.json').read_text())['events']}
    selected |= {'Route101', 'OldaleTown', 'PalletTown_PlayersHouse_1F_Frlg', 'PalletTown_PlayersHouse_2F_Frlg'}
    # Include immediate native connection neighbors without pulling in unused regions.
    selected |= {by_id[c['map']] for name in list(selected) for c in maps[name].get('connections') or []}
    report = {'maps': [], 'connections': []}
    for name in ([] if '--only-seams' in sys.argv else sorted(selected)):
        print('MAP', name, flush=True)
        record = {'map': name, 'views': [], 'unreached': [], 'isolated_samples': []}
        try:
            g = setup()
            width, height, blocks = geometry(name)
            avoid = {(e['x'], e['y']) for e in maps[name]['warp_events']}
            avoid |= {(e['x'], e['y']) for e in maps[name]['object_events']}
            avoid |= {(e['x'], e['y']) for e in maps[name].get('coord_events', [])}
            cells = [(x, y) for y in range(height) for x in range(width)
                     if not blocks[y*width+x] & 0xC00 and (x, y) not in avoid]
            targets = list(dict.fromkeys(min(cells, key=lambda p: abs(p[0]-x)+abs(p[1]-y))
                       for y in range(3, height, 8) for x in range(3, width, 10)))
            start = min(cells, key=lambda p: abs(p[0]-width//2)+abs(p[1]-height//2))
            g.warp(name, *start)
            record['views'].append(visual(g, name+'_entry'))
            for i, target in enumerate(targets):
                if walk(g, target, avoid):
                    record['views'].append(visual(g, name+f'_{i:03}'))
                else:
                    record['unreached'].append(target)
                    # Sample disconnected elevations/water islands independently,
                    # then continue walking from that component. Record the warp
                    # explicitly; it is not evidence of a traversable route.
                    g.warp(name, *target)
                    record['isolated_samples'].append(target)
                    record['views'].append(visual(g, name+f'_{i:03}_isolated'))
        except Exception as error:
            record['error'] = str(error) or repr(error)
            traceback.print_exc()
        report['maps'].append(record)
        print('RESULT', name, len(record['views']), 'views', sum(v['mismatches'] for v in record['views']), 'mismatches', record.get('error', ''), flush=True)
        (OUT/'report.json').write_text(json.dumps(report, indent=2))
    for name in sorted(selected):
        for conn in maps[name].get('connections') or []:
            dest = by_id[conn['map']]
            record = {'source': name, 'destination': dest, 'direction': conn['direction']}
            if conn['direction'] not in ('up', 'down', 'left', 'right'):
                record['status'] = 'not_a_camera_seam'
                record['reason'] = 'dive/emerge transitions require a separate movement test'
                report['connections'].append(record)
                print('TRANSITION', record, flush=True)
                (OUT/'report.json').write_text(json.dumps(report, indent=2))
                continue
            try:
                w,h,b = geometry(name)
                dw,dh,db = geometry(dest)
                direction = conn['direction']
                off = conn['offset']
                candidates = []
                for t in range(w if direction in ('up','down') else h):
                    x,y = (t,0 if direction=='up' else h-1) if direction in ('up','down') else (0 if direction=='left' else w-1,t)
                    dx,dy = (t-off,dh-1 if direction=='up' else 0) if direction in ('up','down') else (dw-1 if direction=='left' else 0,t-off)
                    if 0 <= dx < dw and 0 <= dy < dh and not (b[y*w+x] | db[dy*dw+dx]) & 0xC00:
                        candidates.append((x,y))
                assert candidates, 'no open matching edge tiles'
                g = setup()
                x, y = candidates[len(candidates)//2]
                # Door-like arrival animations can step across an edge before
                # the explicit crossing test begins. Start one tile inland.
                ix, iy = {'up': (x, y+1), 'down': (x, y-1),
                          'left': (x+1, y), 'right': (x-1, y)}[direction]
                if 0 <= ix < w and 0 <= iy < h and not b[iy*w+ix] & 0xC00:
                    x, y = ix, iy
                g.warp(name, x, y)
                cross_connection(g, direction.upper(), ids[dest], name+'_'+dest)
                record['view'] = visual(g, 'seam_'+name+'_'+dest)
            except Exception as error:
                record['error'] = str(error) or repr(error)
            report['connections'].append(record)
            print('SEAM', record, flush=True)
            (OUT/'report.json').write_text(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
