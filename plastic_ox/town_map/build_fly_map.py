#!/usr/bin/env python3
"""Generate the Plastic Ox fly/town map.

The cell layout below places towns, the League, landmarks and route chains on
the 28x15 region-map grid. Positions follow plastic_ox/plastic_ox_topology.svg
(the 2600x1800 topology canvas scaled onto the grid) and the route list follows
the maps that are actually wired up in data/maps. Terrain (coast, sea, hills)
is derived from the layout itself, so moving a cell moves the land with it.

Outputs (all generator-owned):
  graphics/pokenav/region_map/map.png / map.bin / map.pal
  src/data/region_map/region_map_layout.h
  src/data/region_map/region_map_sections.json   (x/y/width/height only)
  src/data/region_map/plastic_ox_fly_spots.h
  plastic_ox/town_map/fly_map_preview.png        (labelled review image)

Run: python3 plastic_ox/town_map/build_fly_map.py [--check]
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
GRID_W, GRID_H = 28, 15
CURSOR_X0, CURSOR_Y0 = 1, 2          # MAPCURSOR_X_MIN / MAPCURSOR_Y_MIN
PAL_BASE = 112                       # region map palette loads at BG_PLTT_ID(7)

# --- v7 layout ---------------------------------------------------------------
# Fly destinations: towns + the Pokemon League, in story order (the save
# backfill in src/region_map.c relies on that order). (mapsec, cell, kind,
# visited flag, landing map, landing x, y, gym badge flag or None). Landing
# tiles sit outside each Pokemon Center.
# Windows cover two corners: the fly map's name box hides cells with x >= 15 on
# rows 13-14, the Town Map's title hides x >= 20 on rows 0-1. Keep them empty.
TOWNS = [
    ('MAPSEC_PALLET_TOWN',      (10, 12), 'town',  'FLAG_POX_VISITED_PALLET',      'MAP_PALLET_TOWN',            6,  8, None),
    ('MAPSEC_OLDALE_TOWN',      (10, 10), 'town',  'FLAG_VISITED_OLDALE_TOWN',     'MAP_OLDALE_TOWN',            6, 17, None),
    ('MAPSEC_CHERRYGROVE_CITY', (2, 11),  'city',  'FLAG_POX_VISITED_CHERRYGROVE', 'MAP_CHERRYGROVE_CITY_HNS',  47,  8, None),
    ('MAPSEC_RUSTBORO_CITY',    (2, 3),   'city',  'FLAG_VISITED_RUSTBORO_CITY',   'MAP_RUSTBORO_CITY',         16, 39, 'FLAG_BADGE01_GET'),
    ('MAPSEC_GOLDENROD_CITY',   (14, 4),  'city',  'FLAG_POX_VISITED_GOLDENROD',   'MAP_GOLDENROD_CITY_HNS',    28, 37, 'FLAG_BADGE02_GET'),
    ('MAPSEC_ECRUTEAK_CITY',    (15, 0),  'city',  'FLAG_POX_VISITED_ECRUTEAK',    'MAP_ECRUTEAK_CITY_HNS',     39, 48, 'FLAG_BADGE03_GET'),
    ('MAPSEC_FORTREE_CITY',     (19, 0),  'city',  'FLAG_VISITED_FORTREE_CITY',    'MAP_FORTREE_CITY',           5,  7, 'FLAG_BADGE04_GET'),
    ('MAPSEC_LAVENDER_TOWN',    (23, 9),  'town',  'FLAG_POX_VISITED_LAVENDER',    'MAP_LAVENDER_TOWN_HNS',      9,  7, None),
    ('MAPSEC_CINNABAR_ISLAND',  (10, 14), 'city',  'FLAG_POX_VISITED_CINNABAR',    'MAP_CINNABAR_ISLAND',       14, 12, 'FLAG_BADGE05_GET'),
    ('MAPSEC_MOSSDEEP_CITY',    (18, 12), 'city',  'FLAG_VISITED_MOSSDEEP_CITY',   'MAP_MOSSDEEP_CITY',         28, 17, 'FLAG_BADGE06_GET'),
    ('MAPSEC_SAFFRON_CITY',     (18, 9),  'city',  'FLAG_POX_VISITED_SAFFRON',     'MAP_SAFFRON_CITY_HNS',      16, 23, 'FLAG_BADGE07_GET'),
    ('MAPSEC_BLACKTHORN_CITY',  (7, 7),   'city',  'FLAG_POX_VISITED_BLACKTHORN',  'MAP_BLACKTHORN_CITY_HNS',   27, 49, 'FLAG_BADGE08_GET'),
    ('MAPSEC_INDIGO_PLATEAU',   (9, 0),   'league', 'FLAG_POX_VISITED_INDIGO',     'MAP_INDIGO_PLATEAU_HNS',    11,  7, None),
]

# Named places you can hover but not fly to.
LANDMARKS = [
    ('MAPSEC_CERULEAN_CAVE',   (1, 1)),
    ('MAPSEC_ILEX_FOREST',     (2, 7)),
    ('MAPSEC_DARK_CAVE',       (4, 9)),
    ('MAPSEC_MT_MOON',         (9, 3)),
    ('MAPSEC_NATIONAL_PARK',   (14, 2)),
    ('MAPSEC_RUINS_OF_ALPH',   (17, 3)),
    ('MAPSEC_METEOR_FALLS',    (10, 7)),
    ('MAPSEC_SEAFOAM_ISLANDS', (14, 13)),
]
# Hills are drawn around these cells.
MOUNTAINS = [(1, 1), (4, 9), (9, 3), (10, 7), (7, 7), (7, 8), (10, 0), (11, 0), (12, 0), (13, 0)]
# Islands: places that sit in the sea rather than on the mainland.
ISLANDS = {(10, 14), (14, 13), (18, 12)}
# Interiors with their own map section: the player icon shows on the host cell.
INSIDE = {
    'MAPSEC_BURNED_TOWER': (15, 0),
    'MAPSEC_POKEMON_TOWER': (23, 9),
    'MAPSEC_POKEMON_MANSION': (10, 14),
    'MAPSEC_UNDERGROUND_PATH_2': (18, 9),
}

# Route chains: ordered cells, each tagged with its mapsec. 'sea' routes are
# drawn as sea lanes.
L, S = 'land', 'sea'


def run(x0, y0, x1, y1):
    """Cells from (x0, y0) to (x1, y1) inclusive along one axis."""
    if x0 == x1:
        step = 1 if y1 >= y0 else -1
        return [(x0, y) for y in range(y0, y1 + step, step)]
    step = 1 if x1 >= x0 else -1
    return [(x, y0) for x in range(x0, x1 + step, step)]


ROUTES = [
    # West: Pallet - Oldale - Cherrygrove - Ilex - Rustboro, and the cape.
    [(L, 'MAPSEC_ROUTE_101', [(10, 11)])],
    [(L, 'MAPSEC_ROUTE_29', run(3, 11, 7, 11) + run(7, 10, 9, 10))],
    [(L, 'MAPSEC_ROUTE_46', [(7, 9)]), (L, 'MAPSEC_ROUTE_45', [(7, 8)])],
    [(L, 'MAPSEC_ROUTE_2', run(2, 10, 2, 8))],
    [(L, 'MAPSEC_ROUTE_2', run(2, 6, 2, 4))],
    [(L, 'MAPSEC_ROUTE_24', run(2, 2, 2, 1)), (L, 'MAPSEC_ROUTE_25', run(3, 1, 4, 1))],
    # Centre: Rustboro - Mt. Moon - Goldenrod - National Park - Ecruteak.
    [(L, 'MAPSEC_ROUTE_44', run(3, 3, 8, 3))],
    [(L, 'MAPSEC_ROUTE_33', run(10, 3, 11, 3) + run(11, 4, 11, 5) + run(12, 5, 14, 5))],
    [(L, 'MAPSEC_ROUTE_35', [(14, 3)])],
    [(L, 'MAPSEC_ROUTE_37', [(15, 1)]), (L, 'MAPSEC_ROUTE_36', run(15, 2, 18, 2))],
    [(L, 'MAPSEC_VICTORY_ROAD', run(14, 0, 10, 0))],
    # North-east: Ecruteak - Fortree - Lavender.
    [(L, 'MAPSEC_ROUTE_38', [(16, 0)]), (L, 'MAPSEC_ROUTE_119', run(17, 0, 18, 0))],
    [(L, 'MAPSEC_ROUTE_110', run(19, 1, 19, 2) + run(20, 2, 23, 2) + run(23, 3, 23, 8))],
    # East and south: Lavender - Saffron - Route 103, and the sea loop.
    [(L, 'MAPSEC_ROUTE_8', run(22, 9, 19, 9))],
    [(L, 'MAPSEC_ROUTE_7', run(17, 9, 11, 9)), (L, 'MAPSEC_ROUTE_103', [(10, 9)])],
    [(S, 'MAPSEC_ROUTE_21', [(10, 13)])],
    [(S, 'MAPSEC_ROUTE_20', run(11, 14, 14, 14))],
    [(S, 'MAPSEC_ROUTE_20', run(14, 12, 17, 12))],
    [(S, 'MAPSEC_ROUTE_127', run(19, 12, 20, 12))],
    [(S, 'MAPSEC_ROUTE_19', run(18, 10, 18, 11))],
    # Saffron - Meteor Falls - Blackthorn.
    [(L, 'MAPSEC_ROUTE_5', [(18, 8)]), (L, 'MAPSEC_ROUTE_115', [(18, 7)] + run(17, 7, 11, 7))],
]
# Extra links between places that are next to each other (or share a row or
# column) but sit in different chains.
LINKS = [((10, 12), (10, 11)), ((10, 11), (10, 10)), ((10, 10), (9, 10)), ((10, 10), (10, 9)),
         ((2, 11), (3, 11)), ((2, 11), (2, 10)), ((7, 10), (7, 9)), ((7, 8), (7, 7)),
         ((2, 8), (2, 7)), ((2, 7), (2, 6)), ((2, 9), (4, 9)), ((4, 9), (7, 9)),
         ((2, 4), (2, 3)), ((2, 3), (2, 2)), ((2, 1), (1, 1)), ((2, 3), (3, 3)),
         ((8, 3), (9, 3)), ((9, 3), (10, 3)), ((14, 5), (14, 4)), ((14, 4), (14, 3)),
         ((14, 3), (14, 2)), ((14, 2), (15, 2)), ((18, 2), (19, 2)),
         ((15, 1), (15, 0)), ((15, 0), (14, 0)), ((10, 0), (9, 0)), ((15, 0), (16, 0)),
         ((18, 0), (19, 0)), ((19, 0), (19, 1)), ((23, 8), (23, 9)), ((23, 9), (22, 9)),
         ((19, 9), (18, 9)), ((18, 9), (17, 9)), ((18, 9), (18, 8)), ((11, 7), (10, 7)),
         ((10, 7), (7, 7)), ((10, 12), (10, 13)), ((10, 13), (10, 14)), ((10, 14), (11, 14)),
         ((14, 14), (14, 13)), ((14, 13), (14, 12)), ((17, 12), (18, 12)), ((18, 12), (19, 12)),
         ((18, 9), (18, 10)), ((18, 11), (18, 12))]

# --- palette -----------------------------------------------------------------
COLORS = {
    'sea': 'b8e4ec', 'sea_dark': '9fd3e0', 'land': 'cfeeaf', 'coast': '4f8a73',
    'mountain': 'e2b98f', 'mount_dark': 'b88a63', 'route': 'fffbe9', 'route_edge': '929d8d',
    'lane': '658dcc', 'town': 'e96350', 'town_edge': '7a2a20', 'league': '826bb6',
    'league_edge': '3f2f63', 'mark': '66b77c', 'mark_edge': '2f5e3d', 'black': '000000',
}
NAMES = list(COLORS)
IDX = {n: i for i, n in enumerate(NAMES)}


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def terrain(land_cells, sea_cells, place_cells):
    """Classify each 4px quad as sea / deep / land / mountain from the layout."""
    QW, QH = 60, 40

    def qc(c):  # cell centre in quad units
        return (c[0] + CURSOR_X0) * 2 + 1, (c[1] + CURSOR_Y0) * 2 + 1

    def wobble(x, y):  # deterministic, smooth, about -1..1
        return 0.55 * math.sin(x * 0.83 + y * 0.47) + 0.45 * math.sin(x * 0.31 - y * 1.07 + 1.3)

    land_src = [(qc(c), 1.9 if c in ISLANDS else 3.6) for c in land_cells]
    sea_src = [qc(c) for c in sea_cells]
    hills = [qc(c) for c in MOUNTAINS]

    def dist(p, q):
        return math.hypot(p[0] - q[0], p[1] - q[1])

    q = [['sea'] * QW for _ in range(QH)]
    for y in range(QH):
        for x in range(QW):
            p = (x + 0.5, y + 0.5)
            land = min(dist(p, s) / r for s, r in land_src)
            sea = min(dist(p, s) / 2.4 for s in sea_src)
            if land + 0.16 * wobble(x, y) < 1 and land < sea:
                q[y][x] = 'land'
    # Sea that cannot reach the map edge is not sea: fill it in.
    seen = set()
    stack = [(x, y) for x in range(QW) for y in (0, QH - 1)] + [(x, y) for y in range(QH) for x in (0, QW - 1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < QW and 0 <= y < QH) or q[y][x] != 'sea':
            continue
        seen.add((x, y))
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for y in range(QH):
        for x in range(QW):
            if q[y][x] == 'sea' and (x, y) not in seen:
                q[y][x] = 'land'
    for y in range(QH):
        for x in range(QW):
            p = (x + 0.5, y + 0.5)
            if q[y][x] == 'land':
                if min(dist(p, h) for h in hills) + 0.9 * wobble(x + 7, y + 3) < 2.7:
                    q[y][x] = 'mountain'
            else:
                near = min((abs(x - a) + abs(y - b) for b in range(max(0, y - 4), min(QH, y + 5))
                            for a in range(max(0, x - 4), min(QW, x + 5)) if q[b][a] != 'sea' and q[b][a] != 'deep'),
                           default=9)
                if near > 4:
                    q[y][x] = 'deep'
    return q


def build():
    W, H = 240, 160

    route_cells = {}
    sea_cells = set()
    for chain in ROUTES:
        for kind, mapsec, cells in chain:
            for c in cells:
                assert c not in route_cells, f'cell {c} used twice'
                route_cells[c] = mapsec
                if kind == S:
                    sea_cells.add(c)
    place_cells = {c: (m, k) for m, c, k, *_ in TOWNS}
    place_cells.update({c: (m, 'mark') for m, c in LANDMARKS})
    assert not set(place_cells) & set(route_cells), set(place_cells) & set(route_cells)
    for c in list(route_cells) + list(place_cells):
        assert 0 <= c[0] < GRID_W and 0 <= c[1] < GRID_H, c

    land_cells = [c for c in route_cells if c not in sea_cells] + list(place_cells)
    q = terrain(land_cells, sea_cells, place_cells)

    img = Image.new('P', (W, H))
    img.putpalette(sum((list(hexrgb(COLORS[n])) for n in NAMES), []) + [0] * (768 - 3 * len(NAMES)))
    px = img.load()
    wet = ('sea', 'deep')
    for y in range(H):
        for x in range(W):
            qx, qy = x // 4, y // 4
            t = q[qy][qx]
            col = {'sea': 'sea', 'deep': 'sea_dark', 'land': 'land', 'mountain': 'mountain'}[t]
            if t not in wet:
                # coast: 1px where a land quad meets sea
                for dx, dy, edge in ((-1, 0, x % 4 == 0), (1, 0, x % 4 == 3), (0, -1, y % 4 == 0), (0, 1, y % 4 == 3)):
                    nx, ny = qx + dx, qy + dy
                    if edge and 0 <= nx < W // 4 and 0 <= ny < H // 4 and q[ny][nx] in wet:
                        col = 'coast'
                # ridge: 1px shadow along the foot of the hills
                if t == 'mountain' and col != 'coast' and y % 4 == 3 and qy + 1 < H // 4 and q[qy + 1][qx] == 'land':
                    col = 'mount_dark'
            px[x, y] = IDX[col]

    d = ImageDraw.Draw(img)

    def centre(c):
        return (c[0] + CURSOR_X0) * 8 + 4, (c[1] + CURSOR_Y0) * 8 + 4

    links = list(LINKS)
    for chain in ROUTES:
        flat = [c for _, _, cells in chain for c in cells]
        links += list(zip(flat, flat[1:]))
    for a, b in links:
        (ax, ay), (bx, by) = centre(a), centre(b)
        lane = a in sea_cells or b in sea_cells or (a in place_cells and b in sea_cells)
        if lane:
            d.line([(ax, ay), (bx, by)], fill=IDX['lane'], width=1)
        else:
            d.rectangle([min(ax, bx) - 2, min(ay, by) - 2, max(ax, bx) + 1, max(ay, by) + 1], fill=IDX['route_edge'])
    for a, b in links:
        (ax, ay), (bx, by) = centre(a), centre(b)
        if not (a in sea_cells or b in sea_cells):
            d.rectangle([min(ax, bx) - 1, min(ay, by) - 1, max(ax, bx), max(ay, by)], fill=IDX['route'])
    for c, (_, kind) in place_cells.items():
        x, y = centre(c)
        fill, edge = {'town': ('town', 'town_edge'), 'city': ('town', 'town_edge'),
                      'league': ('league', 'league_edge'), 'mark': ('mark', 'mark_edge')}[kind]
        r = 3 if kind != 'mark' else 2
        d.rectangle([x - r - 1, y - r - 1, x + r, y + r], fill=IDX[edge])
        d.rectangle([x - r, y - r, x + r - 1, y + r - 1], fill=IDX[fill])

    # --- tiles ---------------------------------------------------------------
    sea_tile = bytes([IDX['sea']] * 64)
    tiles = [sea_tile]
    lookup = {sea_tile: 0}
    tilemap = bytearray(64 * 64)
    for ty in range(H // 8):
        for tx in range(W // 8):
            t = bytes(px[tx * 8 + x, ty * 8 + y] for y in range(8) for x in range(8))
            if t not in lookup:
                lookup[t] = len(tiles)
                tiles.append(t)
            tilemap[ty * 64 + tx] = lookup[t]
    if len(tiles) > 256:
        raise SystemExit(f'too many unique tiles: {len(tiles)}')
    rows = (len(tiles) + 15) // 16
    sheet = Image.new('P', (128, rows * 8))
    pal = [0] * 768
    for i, n in enumerate(NAMES):
        pal[(PAL_BASE + i) * 3:(PAL_BASE + i) * 3 + 3] = hexrgb(COLORS[n])
    sheet.putpalette(pal)
    sp = sheet.load()
    for i in range(rows * 16):
        t = tiles[i] if i < len(tiles) else sea_tile
        for j, v in enumerate(t):
            sp[(i % 16) * 8 + j % 8, (i // 16) * 8 + j // 8] = PAL_BASE + v

    # --- mapsec layout + entries ---------------------------------------------
    grid = [['MAPSEC_NONE'] * GRID_W for _ in range(GRID_H)]
    cells_by_sec = {}
    for c, m in list(route_cells.items()) + [(c, m) for c, (m, _) in place_cells.items()]:
        grid[c[1]][c[0]] = m
        cells_by_sec.setdefault(m, []).append(c)
    boxes = {}
    for m, cells in cells_by_sec.items():
        xs, ys = [c[0] for c in cells], [c[1] for c in cells]
        boxes[m] = (min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)
    for m, c, *_ in TOWNS:
        boxes[m] = (c[0], c[1], 1, 1)
    for m, c in INSIDE.items():
        assert m not in boxes, m
        boxes[m] = (c[0], c[1], 1, 1)
    return img, sheet, tilemap, grid, boxes, len(tiles)


def outputs():
    img, sheet, tilemap, grid, boxes, ntiles = build()
    out = {}
    lines = ['// Generated by plastic_ox/town_map/build_fly_map.py. Do not edit.',
             'static const mapsec_u8_t sRegionMap_MapSectionLayout[MAP_HEIGHT][MAP_WIDTH] = {']
    lines += ['    {' + ', '.join(r) + '},' for r in grid]
    lines += ['};', '']
    out['src/data/region_map/region_map_layout.h'] = '\n'.join(lines)

    secs = json.loads((ROOT / 'src/data/region_map/region_map_sections.json').read_text())
    for s in secs['map_sections']:
        if s['id'] in boxes:
            s['x'], s['y'], s['width'], s['height'] = boxes[s['id']]
    out['src/data/region_map/region_map_sections.json'] = json.dumps(secs, indent=2, ensure_ascii=False) + '\n'

    fly = ['// Generated by plastic_ox/town_map/build_fly_map.py. Do not edit.',
           '// Fly destinations: Plastic Ox towns and the Pokemon League, in story order.',
           'static const struct PoxFlySpot sPoxFlySpots[] =', '{']
    for m, c, kind, flag, mp, x, y, badge in TOWNS:
        fly.append(f'    {{ {m}, {flag}, {badge or 0}, MAP_GROUP({mp}), MAP_NUM({mp}), {x}, {y} }},')
    fly += ['};', '']
    out['src/data/region_map/plastic_ox_fly_spots.h'] = '\n'.join(fly)

    pal = ['JASC-PAL', '0100', '48'] + [' '.join(map(str, hexrgb(COLORS[n]))) for n in NAMES]
    pal += ['0 0 0'] * (48 - len(NAMES))
    out['graphics/pokenav/region_map/map.pal'] = '\r\n'.join(pal) + '\r\n'
    return out, img, sheet, tilemap, ntiles


def main():
    out, img, sheet, tilemap, ntiles = outputs()
    check = '--check' in sys.argv
    stale = []
    for rel, text in out.items():
        p = ROOT / rel
        if check:
            if not p.exists() or p.read_bytes() != text.encode():
                stale.append(rel)
        else:
            p.write_bytes(text.encode())
    binp = ROOT / 'graphics/pokenav/region_map/map.bin'
    if check:
        if binp.read_bytes() != bytes(tilemap):
            stale.append(str(binp.relative_to(ROOT)))
        if stale:
            raise SystemExit('fly map out of date: ' + ', '.join(stale))
        print('fly map: up to date')
        return
    binp.write_bytes(bytes(tilemap))
    sheet.save(ROOT / 'graphics/pokenav/region_map/map.png')
    prev = img.convert('RGB').resize((720, 480), Image.NEAREST)
    d = ImageDraw.Draw(prev)
    for m, c, *_ in TOWNS + LANDMARKS:
        x, y = ((c[0] + CURSOR_X0) * 8 + 9) * 3, ((c[1] + CURSOR_Y0) * 8 - 2) * 3
        d.text((x, y), m.replace('MAPSEC_', '').replace('_', ' ').title(), fill=(0, 0, 0))
    prev.save(ROOT / 'plastic_ox/town_map/fly_map_preview.png')
    print(f'fly map: {ntiles} tiles written')


if __name__ == '__main__':
    main()
