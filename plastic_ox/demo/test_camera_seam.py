#!/usr/bin/env python3
"""Check Route 101's Hoenn and Pallet camera connections in mGBA.

Run with the mGBA Python environment. Optional --capture-only records visual
differences without stopping, so the crossings can be inspected.
"""
import json
import struct
import sys
from pathlib import Path

from PIL import ImageChops, ImageStat

from test_story import StoryGame
from walk_demo import cross_connection, MAP_OLDALE, MAP_PALLET, MAP_ROUTE101


ROOT = Path(__file__).resolve().parents[2]


class SmoothFrames:
    def __init__(self, g, max_allowed=None):
        self.previous = g.fb.to_pil().convert('RGB').copy()
        self.max_change = 0
        self.max_allowed = max_allowed

    def __call__(self, g, stage, frame):
        current = g.fb.to_pil().convert('RGB').copy()
        delta = ImageChops.difference(self.previous, current)
        change = sum(ImageStat.Stat(delta).mean) / 3
        self.max_change = max(self.max_change, change)
        if self.max_allowed is not None and '--capture-only' not in sys.argv:
            assert change < self.max_allowed, (
                f'{stage}: abrupt full-screen cut at frame {frame} ({change:.1f})'
            )
        self.previous = current


def map_blocks(layout_name):
    layouts = json.loads((ROOT / 'data/layouts/layouts.json').read_text())['layouts']
    layout = next(layout for layout in layouts if layout['id'] == layout_name)
    raw = (ROOT / layout['blockdata_filepath']).read_bytes()
    return layout, struct.unpack('<' + 'H' * (len(raw) // 2), raw)


def buffers(g):
    camera = g.syms['sFieldCameraOffset']
    tile_x, tile_y = g.u8(camera + 2), g.u8(camera + 3)
    # Slice scrolling maintains 15x15 metatiles; the spare sixteenth row and
    # column in the circular buffer are outside the maintained camera view.
    indices = [((tile_y + y) % 32) * 32 + (tile_x + x) % 32
               for y in range(30) for x in range(30)]
    return tuple(
        tuple(g.u16(g.u32(g.syms[f'gOverworldTilemapBuffer_Bg{bg}']) + 2 * i)
              for i in indices)
        for bg in (1, 2, 3)
    )


def check_view(g, stage):
    g.frame(30)
    g.shot(f'camera_{stage}.png')
    before = buffers(g)
    # callnative DrawWholeMapView; releaseall; end. This leaves the map,
    # position and camera offsets unchanged and rebuilds all three BG buffers.
    ptr = g.syms['gStringVar4']
    code = bytes([0x23]) + struct.pack('<I', g.syms['DrawWholeMapView'] | 1) + bytes([0x6C, 2])
    for i, value in enumerate(code):
        g.write(ptr + i, value)
    g.run(ptr)
    after = buffers(g)
    changed = sum(a != b for old, new in zip(before, after) for a, b in zip(old, new))
    g.shot(f'camera_{stage}_reference.png')
    print(f'{stage}: {changed} BG entries differ from stationary redraw', flush=True)
    if '--capture-only' not in sys.argv:
        assert changed == 0, f'{stage}: stale or shifted scrolling tilemap'


def main():
    route, route_blocks = map_blocks('LAYOUT_ROUTE101')
    oldale, oldale_blocks = map_blocks('LAYOUT_OLDALE_TOWN')
    pallet, _ = map_blocks('LAYOUT_PALLET_TOWN_HNS')
    assert (route['layout_version'], route['primary_tileset'], route['secondary_tileset']) == (
        oldale['layout_version'], oldale['primary_tileset'], oldale['secondary_tileset'])
    assert (route['primary_tileset'], route['secondary_tileset']) != (
        pallet['primary_tileset'], pallet['secondary_tileset'])
    g = StoryGame()
    # Isolate rendering with the north-exit story gate already completed.
    g.flag('FLAG_POX_STORY_STARTER', True)
    g.warp('Route101', 10, 0)
    # The normal Hoenn connection exposes Oldale's actual bottom seven rows.
    for y in range(-7, 0):
        for x in range(route['width']):
            expected = oldale_blocks[(oldale['height'] + y) * oldale['width'] + x]
            assert g.metatile_at(x, y)[1] == expected, ('route north margin', x, y)
    oldale_forward = SmoothFrames(g, max_allowed=45)
    cross_connection(g, 'UP', MAP_OLDALE, 'camera_oldale', on_frame=oldale_forward)
    for y in range(oldale['height'], oldale['height'] + 7):
        for x in range(route['width']):
            expected = route_blocks[(y - oldale['height']) * route['width'] + x]
            assert g.metatile_at(x, y)[1] == expected, ('oldale south margin', x, y)
    check_view(g, 'oldale')
    oldale_reverse = SmoothFrames(g, max_allowed=45)
    cross_connection(g, 'DOWN', MAP_ROUTE101, 'camera_route_from_oldale', on_frame=oldale_reverse)
    check_view(g, 'route_from_oldale')

    g.warp('Route101', 10, 19)
    forward = SmoothFrames(g)
    cross_connection(g, 'DOWN', MAP_PALLET, 'camera_pallet_return', on_frame=forward)
    # Pallet still uses its own border pattern around the open north path.
    for y in range(-7, 0):
        for x in (2, 3, 20, 21):
            expected = ((0x1C, 0x1D), (0x14, 0x15))[y % 2][x % 2]
            metatile, block = g.metatile_at(x, y)
            assert metatile == expected and block & 0xC00, (x, y, hex(block))
        for x in (12, 13):
            assert g.collision_at(x, y)[0] == 0, ('blocked north opening', x, y)
    check_view(g, 'pallet_return')
    g.walk('DOWN', target=(12, 5))
    check_view(g, 'pallet_buildings')
    g.walk('UP', target=(12, 0))
    reverse = SmoothFrames(g)
    cross_connection(g, 'UP', MAP_ROUTE101, 'camera_route_return', on_frame=reverse)
    check_view(g, 'route_return')
    print(f'Oldale frame changes: {oldale_forward.max_change:.1f} / {oldale_reverse.max_change:.1f}', flush=True)
    print(f'Pallet frame changes: {forward.max_change:.1f} / {reverse.max_change:.1f}', flush=True)
    print('CAMERA SEAM CAPTURE COMPLETE' if '--capture-only' in sys.argv
          else 'CAMERA SEAM VERIFICATION PASSED', flush=True)


if __name__ == '__main__':
    main()
