#!/usr/bin/env python3
"""Render current regional map geometry and cave warps as a standalone SVG."""
import json
import re
from collections import deque
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main():
    groups = json.loads((ROOT/'data/maps/map_groups.json').read_text())
    maps = {n: json.loads((ROOT/'data/maps'/n/'map.json').read_text())
            for g in groups['group_order'] for n in groups[g]}
    ids = {m['id']: n for n, m in maps.items()}
    for n in maps:
        ids.setdefault('MAP_'+n.upper(), n)
    for a, b in re.findall(r'#define\s+(MAP_\w+)\s+(MAP_\w+)', (ROOT/'include/constants/maps.h').read_text()):
        if b in ids:
            ids[a] = ids[b]
    layouts = {l['id']: l for l in json.loads((ROOT/'data/layouts/layouts.json').read_text())['layouts']}
    selected = {n for g in groups['group_order'] if 'PlasticOx' in g for n in groups[g]}
    selected |= {e['map'] for e in json.loads((ROOT/'plastic_ox/alpha/story_manifest.json').read_text())['events']}
    selected |= {'Route101', 'OldaleTown'}
    selected |= {ids[c['map']] for n in list(selected) for c in maps[n].get('connections') or []}
    surface = {n for n in selected if maps[n]['map_type'] in ('MAP_TYPE_TOWN', 'MAP_TYPE_CITY', 'MAP_TYPE_ROUTE', 'MAP_TYPE_OCEAN_ROUTE') or maps[n].get('connections')}
    caves = {n for n in selected if maps[n]['map_type'] == 'MAP_TYPE_UNDERGROUND'}
    shown = surface | caves
    def size(n):
        l = layouts[maps[n]['layout']]
        return l['width']*5, l['height']*5
    positions = {}
    cursor = 70
    row_y, row_height, used_width = 150, 0, 0
    conflicts = []
    for seed in sorted(surface):
        if seed in positions:
            continue
        local = {seed: (0, 0)}
        queue = deque([seed])
        while queue:
            n = queue.popleft()
            x, y = local[n]
            w, h = size(n)
            for c in maps[n].get('connections') or []:
                dst = ids[c['map']]
                if dst not in surface:
                    continue
                dw, dh = size(dst)
                off = c['offset']*5
                p = {'up': (x+off, y-dh), 'down': (x+off, y+h), 'left': (x-dw, y+off), 'right': (x+w, y+off)}[c['direction']]
                if dst in local:
                    if local[dst] != p:
                        conflicts.append((n, dst))
                elif dst not in positions:
                    local[dst] = p
                    queue.append(dst)
        minx = min(x for x, y in local.values())
        miny = min(y for x, y in local.values())
        maxx = max(x+size(n)[0] for n, (x, y) in local.items())
        component_width = maxx-minx
        component_height = max(y+size(n)[1] for n, (x, y) in local.items())-miny
        if cursor > 70 and cursor+component_width > 2600:
            cursor = 70
            row_y += row_height+130
            row_height = 0
        for n, (x, y) in local.items():
            positions[n] = (x-minx+cursor, y-miny+row_y)
        cursor += component_width+130
        used_width = max(used_width, cursor)
        row_height = max(row_height, component_height)
    bottom = max(y+size(n)[1] for n, (x, y) in positions.items())
    for i, n in enumerate(sorted(caves)):
        positions[n] = (70+i*330, bottom+260)
    width = max(used_width, 100+len(caves)*330)
    height = bottom+650
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="#101a27"/>', '<g font-family="sans-serif" fill="#eef5ff">', '<text x="50" y="45" font-size="30">Plastic Ox — current region layout</text>', '<text x="50" y="78" font-size="17">Surface maps: 5 px / tile, connection offsets preserved. Disconnected surface components packed in rows.</text>', '<text x="50" y="106" font-size="17">Orange dashed arrows: cave warps (labels show source warp index → destination index). Purple: story-script cave travel (gated). Cave cards are schematic.</text>', '<defs><marker id="story-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="#d4a0ff"/></marker><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="#ffb75d"/></marker></defs>']
    for n in sorted(shown):
        x, y = positions[n]
        w, h = (290, 130) if n in caves else size(n)
        label = re.sub(r'_(hns|Frlg)$', '', n)
        out.append(f'<g><title>{escape(n)}</title><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{"#483322" if n in caves else "#203e48"}" stroke="#8ac4d0" stroke-width="2"/><text x="{x+5}" y="{y+20}" font-size="13">{escape(label)}</text><text x="{x+5}" y="{y+38}" font-size="11">{layouts[maps[n]["layout"]]["width"]} × {layouts[maps[n]["layout"]]["height"]} tiles</text></g>')
    count = 0
    for n in sorted(shown):
        for i, warp in enumerate(maps[n]['warp_events']):
            dst = ids.get(warp['dest_map'])
            if dst not in shown or not ({n, dst} & caves):
                continue
            j = int(warp['dest_warp_id'])
            if not 0 <= j < len(maps[dst]['warp_events']):
                continue
            target = maps[dst]['warp_events'][j]
            def point(name, event, index):
                x, y = positions[name]
                return (x+25+index*30, y+70) if name in caves else (x+event['x']*5+2.5, y+event['y']*5+2.5)
            x, y = point(n, warp, i)
            dx, dy = point(dst, target, j)
            bend = 45+(count%7)*22
            out.append(f'<path d="M{x} {y} Q{(x+dx)/2+bend} {(y+dy)/2-bend} {dx} {dy}" fill="none" stroke="#ffb75d" stroke-width="2" stroke-dasharray="7 5" marker-end="url(#arrow)"><title>{escape(n)} [{i}] → {escape(dst)} [{j}]</title></path><circle cx="{x}" cy="{y}" r="4" fill="#ffb75d"/><text x="{x+5}" y="{y-6}" font-size="12" fill="#ffce8e">{i}→{j}</text>')
            count += 1
    script_text = (ROOT/'data/scripts/plastic_ox_story.inc').read_text()
    script_blocks = dict(re.findall(r'^([A-Za-z_]\w*)::\n(.*?)(?=^[A-Za-z_]\w*::|\Z)', script_text, re.M | re.S))
    story_count = 0
    for event in json.loads((ROOT/'plastic_ox/alpha/story_manifest.json').read_text())['events']:
        source = event['map']
        for dest_id, tx, ty in re.findall(r'^\s*warp\s+(MAP_\w+),\s*(\d+),\s*(\d+)', script_blocks.get(event['script'], ''), re.M):
            dest = ids.get(dest_id)
            if source not in shown or dest not in shown or not ({source, dest} & caves):
                continue
            def story_point(name, px, py):
                x, y = positions[name]
                return (x+145, y+105) if name in caves else (x+px*5+2.5, y+py*5+2.5)
            x, y = story_point(source, event['x'], event['y'])
            dx, dy = story_point(dest, int(tx), int(ty))
            out.append(f'<path d="M{x} {y} Q{(x+dx)/2+100} {(y+dy)/2} {dx} {dy}" fill="none" stroke="#d4a0ff" stroke-width="2" stroke-dasharray="3 6" marker-end="url(#story-arrow)"><title>{escape(event["script"])}: {escape(source)} → {escape(dest)} (story conditions apply)</title></path>')
            story_count += 1
    out.append(f'<text x="50" y="{height-35}" font-size="17">{len(surface)} surface maps · {len(caves)} cave maps · {count} directed cave warps · {story_count} scripted cave links · {len(set(conflicts))} inconsistent directed geometry constraints. Ordinary building interiors omitted.</text></g></svg>')
    path = ROOT/'plastic_ox/region_layout.svg'
    path.write_text('\n'.join(out))
    print(path)
    print(f'{len(surface)} surface maps, {len(caves)} caves, {count} cave warps, {story_count} scripted cave links; geometry conflicts: {conflicts}')

if __name__ == '__main__':
    main()
