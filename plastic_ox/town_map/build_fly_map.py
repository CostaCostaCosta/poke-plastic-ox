#!/usr/bin/env python3
"""Generate the Plastic Ox fly/town map from the v7 town-map concept.

Inputs: plastic_ox/town_map/plastic_ox_town_map_unlabeled.png (terrain art) and
the v7 cell layout below (towns, League, landmarks and route chains on the
28x15 region-map grid).

Outputs (all generator-owned):
  graphics/pokenav/region_map/map.png / map.bin / map.pal
  src/data/region_map/region_map_layout.h
  src/data/region_map/region_map_sections.json   (x/y/width/height only)
  src/data/region_map/plastic_ox_fly_spots.h
  plastic_ox/town_map/fly_map_preview.png        (labelled review image)

Run: python3 plastic_ox/town_map/build_fly_map.py [--check]
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
GRID_W, GRID_H = 28, 15
CURSOR_X0, CURSOR_Y0 = 1, 2          # MAPCURSOR_X_MIN / MAPCURSOR_Y_MIN
PAL_BASE = 112                       # region map palette loads at BG_PLTT_ID(7)

# Concept canvas (1600x1100) -> grid cell centre.
def concept_xy(gx, gy):
    return 150 + 50 * gx, 100 + 64 * gy

# --- v7 layout ---------------------------------------------------------------
# Fly destinations: towns + the Pokemon League. (mapsec, cell, kind, flag,
# landing map, landing x, y). Landing tiles sit outside each Pokemon Center.
TOWNS = [
    ('MAPSEC_PALLET_TOWN',      (2, 12), 'town',   'FLAG_POX_VISITED_PALLET',            'MAP_PALLET_TOWN',            6,  8),
    ('MAPSEC_OLDALE_TOWN',      (2, 10), 'town',   'FLAG_VISITED_OLDALE_TOWN',              'MAP_OLDALE_TOWN',            6, 17),
    ('MAPSEC_CHERRYGROVE_CITY', (6, 10), 'city',   'FLAG_POX_VISITED_CHERRYGROVE',          'MAP_CHERRYGROVE_CITY_HNS',  47,  8),
    ('MAPSEC_RUSTBORO_CITY',    (11, 11), 'city',  'FLAG_VISITED_RUSTBORO_CITY',            'MAP_RUSTBORO_CITY',         16, 39),
    ('MAPSEC_GOLDENROD_CITY',   (14, 7), 'city',   'FLAG_POX_VISITED_GOLDENROD',            'MAP_GOLDENROD_CITY_HNS',    28, 37),
    ('MAPSEC_ECRUTEAK_CITY',    (14, 3), 'city',   'FLAG_POX_VISITED_ECRUTEAK',             'MAP_ECRUTEAK_CITY_HNS',     39, 48),
    ('MAPSEC_FORTREE_CITY',     (19, 4), 'city',   'FLAG_VISITED_FORTREE_CITY',             'MAP_FORTREE_CITY',           5,  7),
    ('MAPSEC_LAVENDER_TOWN',    (21, 7), 'town',   'FLAG_POX_VISITED_LAVENDER',          'MAP_LAVENDER_TOWN_HNS',      9,  7),
    ('MAPSEC_CINNABAR_ISLAND',  (19, 12), 'city',  'FLAG_POX_VISITED_CINNABAR',        'MAP_CINNABAR_ISLAND',       14, 12),
    ('MAPSEC_MOSSDEEP_CITY',    (25, 11), 'city',  'FLAG_VISITED_MOSSDEEP_CITY',            'MAP_MOSSDEEP_CITY',         28, 17),
    ('MAPSEC_SAFFRON_CITY',     (25, 7), 'city',   'FLAG_POX_VISITED_SAFFRON',           'MAP_SAFFRON_CITY_HNS',      16, 23),
    ('MAPSEC_BLACKTHORN_CITY',  (25, 2), 'city',   'FLAG_POX_VISITED_BLACKTHORN',           'MAP_BLACKTHORN_CITY_HNS',   27, 49),
    ('MAPSEC_INDIGO_PLATEAU',   (9, 3), 'league',  'FLAG_POX_VISITED_INDIGO', 'MAP_INDIGO_PLATEAU_HNS',    11,  7),
]

# Named places you can hover but not fly to.
LANDMARKS = [
    ('MAPSEC_DARK_CAVE',       (6, 7)),
    ('MAPSEC_ILEX_FOREST',     (9, 8)),
    ('MAPSEC_MT_MOON',         (14, 10)),
    ('MAPSEC_NATIONAL_PARK',   (11, 5)),
    ('MAPSEC_SEAFOAM_ISLANDS', (22, 12)),
    ('MAPSEC_METEOR_FALLS',    (25, 3)),
]

# Route chains: ordered cells, each tagged with its mapsec. 'sea' routes are
# drawn as sea lanes.
L, S = 'land', 'sea'
ROUTES = [
    [(L, 'MAPSEC_ROUTE_101', [(2, 11)])],
    [(L, 'MAPSEC_ROUTE_29', [(3, 10), (4, 10), (5, 10)])],
    [(L, 'MAPSEC_ROUTE_46', [(6, 9), (6, 8)])],
    [(L, 'MAPSEC_ROUTE_2', [(7, 10), (8, 10), (9, 10), (9, 9)])],
    [(L, 'MAPSEC_ROUTE_2', [(10, 8), (11, 8), (11, 9), (11, 10)])],
    [(L, 'MAPSEC_ROUTE_24', [(11, 12), (11, 13)]), (L, 'MAPSEC_ROUTE_25', [(12, 13), (13, 13)])],
    [(L, 'MAPSEC_ROUTE_44', [(12, 11), (13, 11), (14, 11)])],
    [(L, 'MAPSEC_ROUTE_33', [(14, 9), (14, 8)])],
    [(L, 'MAPSEC_ROUTE_35', [(14, 6), (13, 6), (12, 6), (11, 6)])],
    [(L, 'MAPSEC_ROUTE_36', [(12, 5), (13, 5)]), (L, 'MAPSEC_ROUTE_37', [(14, 5), (14, 4)])],
    [(L, 'MAPSEC_VICTORY_ROAD', [(13, 3), (12, 3), (11, 3), (10, 3)])],
    [(L, 'MAPSEC_ROUTE_119', [(15, 3), (16, 3), (17, 3), (18, 3), (19, 3)])],
    [(L, 'MAPSEC_ROUTE_110', [(20, 4), (21, 4), (21, 5), (21, 6)])],
    [(L, 'MAPSEC_ROUTE_8', [(21, 8)]), (L, 'MAPSEC_ROUTE_7', [(21, 9), (21, 10)]),
     (S, 'MAPSEC_ROUTE_103', [(20, 10), (19, 10), (19, 11)])],
    [(S, 'MAPSEC_ROUTE_21', [(19, 13)])],
    [(S, 'MAPSEC_ROUTE_20', [(20, 12), (21, 12)])],
    [(S, 'MAPSEC_ROUTE_20', [(23, 12), (24, 12), (25, 12)])],
    [(S, 'MAPSEC_ROUTE_19', [(25, 10), (25, 9), (25, 8)])],
    [(L, 'MAPSEC_ROUTE_5', [(25, 6)]), (L, 'MAPSEC_ROUTE_115', [(25, 5), (25, 4)])],
]
# Extra links between places that are adjacent but in different chains.
LINKS = [((2, 12), (2, 11)), ((2, 11), (2, 10)), ((2, 10), (3, 10)), ((5, 10), (6, 10)),
         ((6, 10), (6, 9)), ((6, 8), (6, 7)), ((6, 10), (7, 10)), ((9, 9), (9, 8)),
         ((9, 8), (10, 8)), ((11, 10), (11, 11)), ((11, 11), (11, 12)), ((11, 11), (12, 11)),
         ((14, 11), (14, 10)), ((14, 10), (14, 9)), ((14, 8), (14, 7)), ((14, 7), (14, 6)),
         ((11, 6), (11, 5)), ((11, 5), (12, 5)), ((14, 4), (14, 3)), ((14, 3), (13, 3)),
         ((10, 3), (9, 3)), ((14, 3), (15, 3)), ((19, 3), (19, 4)), ((19, 4), (20, 4)),
         ((21, 6), (21, 7)), ((21, 7), (21, 8)), ((19, 11), (19, 12)), ((19, 12), (19, 13)),
         ((19, 12), (20, 12)), ((21, 12), (22, 12)), ((22, 12), (23, 12)), ((25, 12), (25, 11)),
         ((25, 11), (25, 10)), ((25, 8), (25, 7)), ((25, 7), (25, 6)), ((25, 4), (25, 3)),
         ((25, 3), (25, 2))]

# --- palette -----------------------------------------------------------------
COLORS = {
    'sea': 'b8e4ec', 'sea_dark': '91c9d6', 'land': 'cfeeaf', 'coast': '4f8a73',
    'mountain': 'e2b98f', 'mount_dark': 'b88a63', 'route': 'fffbe9', 'route_edge': '929d8d',
    'lane': '658dcc', 'town': 'e96350', 'town_edge': '7a2a20', 'league': '826bb6',
    'league_edge': '3f2f63', 'mark': '66b77c', 'mark_edge': '2f5e3d', 'black': '000000',
}
NAMES = list(COLORS)
IDX = {n: i for i, n in enumerate(NAMES)}


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def terrain_sampler():
    im = Image.open(ROOT / 'plastic_ox/town_map/plastic_ox_town_map_unlabeled.png').convert('RGB')
    sea = [hexrgb(c) for c in ('b8e4ec', '91c9d6', '69adbd')]
    mount = [hexrgb('e2b98f')]

    def near(c, ref):
        return min(sum((a - b) ** 2 for a, b in zip(c, r)) for r in ref)

    def classify(px, py):
        # px, py: screen pixel -> concept canvas
        gx = (px - CURSOR_X0 * 8) / 8 - 0.5
        gy = (py - CURSOR_Y0 * 8) / 8 - 0.5
        cx, cy = concept_xy(gx, gy)
        votes = {'sea': 0, 'land': 0, 'mountain': 0}
        for dx in (-12, 0, 12):
            for dy in (-12, 0, 12):
                x = min(max(int(cx + dx), 0), im.width - 1)
                y = min(max(int(cy + dy), 0), im.height - 1)
                c = im.getpixel((x, y))
                if near(c, sea) < 900:
                    votes['sea'] += 1
                elif near(c, mount) < 900:
                    votes['mountain'] += 1
                else:
                    votes['land'] += 1
        return max(votes, key=votes.get)
    return classify


def build():
    classify = terrain_sampler()
    W, H = 240, 160
    # Terrain at 4px resolution.
    q = [[classify(x * 4 + 2, y * 4 + 2) for x in range(W // 4)] for y in range(H // 4)]

    route_cells = {}
    sea_cells = set()
    for chain in ROUTES:
        for kind, mapsec, cells in chain:
            for c in cells:
                route_cells[c] = mapsec
                if kind == S:
                    sea_cells.add(c)
    place_cells = {c: (m, k) for m, c, k, *_ in TOWNS}
    place_cells.update({c: (m, 'mark') for m, c in LANDMARKS})

    def cell_quads(c):
        gx, gy = c
        x0, y0 = (gx + CURSOR_X0) * 2, (gy + CURSOR_Y0) * 2
        return [(x0 + i, y0 + j) for i in (0, 1) for j in (0, 1)]

    # Land under land routes/places, sea under sea lanes.
    for c in list(route_cells) + list(place_cells):
        for qx, qy in cell_quads(c):
            if c in sea_cells:
                q[qy][qx] = 'sea'
            elif q[qy][qx] == 'sea' or c in place_cells:
                q[qy][qx] = 'land'
    for c in place_cells:  # islands/coastal towns keep a little land around them
        pass

    img = Image.new('P', (W, H))
    img.putpalette(sum((list(hexrgb(COLORS[n])) for n in NAMES), []) + [0] * (768 - 3 * len(NAMES)))
    px = img.load()
    for y in range(H):
        for x in range(W):
            t = q[y // 4][x // 4]
            col = {'sea': 'sea', 'land': 'land', 'mountain': 'mountain'}[t]
            # coast/ridge outline: 1px where a land quad meets sea
            if t != 'sea':
                qx, qy = x // 4, y // 4
                for dx, dy, edge in ((-1, 0, x % 4 == 0), (1, 0, x % 4 == 3), (0, -1, y % 4 == 0), (0, 1, y % 4 == 3)):
                    nx, ny = qx + dx, qy + dy
                    if edge and 0 <= nx < W // 4 and 0 <= ny < H // 4 and q[ny][nx] == 'sea':
                        col = 'coast'
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
           '// Fly destinations: Plastic Ox towns and the Pokemon League.',
           'static const struct PoxFlySpot sPoxFlySpots[] =', '{']
    for m, c, kind, flag, mp, x, y in TOWNS:
        fly.append(f'    {{ {m}, {flag}, MAP_GROUP({mp}), MAP_NUM({mp}), {x}, {y} }},')
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
    for m, c, *_ in TOWNS:
        x, y = ((c[0] + CURSOR_X0) * 8 + 9) * 3, ((c[1] + CURSOR_Y0) * 8 - 2) * 3
        d.text((x, y), m.replace('MAPSEC_', '').replace('_', ' ').title(), fill=(0, 0, 0))
    prev.save(ROOT / 'plastic_ox/town_map/fly_map_preview.png')
    print(f'fly map: {ntiles} tiles written')


if __name__ == '__main__':
    main()
