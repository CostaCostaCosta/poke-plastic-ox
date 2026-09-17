#!/usr/bin/env python3
"""Check connection scrolling against a stationary full redraw of the same view.

Run with the mGBA Python environment. Optional --capture-only records the old
failure without stopping, so both directions can be inspected before a fix.
"""
import struct
import sys

from test_story import StoryGame
from walk_demo import cross_connection, MAP_PALLET, MAP_ROUTE101


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
    g = StoryGame()
    # Isolate rendering with the north-exit story gate already completed.
    g.flag('FLAG_POX_STORY_STARTER', True)
    g.warp('Route101', 10, 19)
    cross_connection(g, 'DOWN', MAP_PALLET, 'camera_pallet_return')
    # Pallet's two-row forest border must retain its phase through the entire
    # north margin, with the two-tile entrance still open.
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
    cross_connection(g, 'UP', MAP_ROUTE101, 'camera_route_return')
    check_view(g, 'route_return')
    print('CAMERA SEAM CAPTURE COMPLETE' if '--capture-only' in sys.argv
          else 'CAMERA SEAM VERIFICATION PASSED', flush=True)


if __name__ == '__main__':
    main()
