#!/usr/bin/env python3
"""Continue Rustboro's native stone road through the Route 44 east exit.

The Route 44 link is a scripted full map load because the two maps use
different primary tilesets. Route 44 keeps its donor's authored collision:
its upper drawing layer also contains walkable roads and overhangs. A previous
blanket rule made 559 of those tiles solid and stranded the player at the west
entrance. Keep collision edits tied to specific authored geometry.
"""
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "data/layouts/RustboroCity/map.bin"
ROUTE_PATH = ROOT / "data/layouts/Route44_hns/map.bin"
WIDTH = 40
HEIGHT = 60


def main():
    data = bytearray(PATH.read_bytes())
    assert len(data) == WIDTH * HEIGHT * 2

    # Rows 8..11 are the four native phases of the eastbound stone road.
    # Replace the former end caps at x=36 and continue each phase through the
    # boundary.  The central three rows align with the portal's lane coverage.
    for y, metatile in ((8, 0x32BB), (9, 0x32F9),
                        (10, 0x3309), (11, 0x32BB)):
        for x in range(36, WIDTH):
            struct.pack_into("<H", data, 2 * (y * WIDTH + x), metatile)

    # Remove the obsolete Rusturf Tunnel placard from the new through-road.
    struct.pack_into("<H", data, 2 * (8 * WIDTH + 30), 0x32BB)

    PATH.write_bytes(data)

    # Route 44's imported west-side hint sign no longer describes this route.
    # Replace it with the route's own adjacent grass block.  Route 44 is 78x36;
    # using the old 72x39 dimensions wrote this block to (59, 15), beside the
    # Mt. Moon approach, instead of (5, 17).
    route_width, route_height = 78, 36
    route = bytearray(ROUTE_PATH.read_bytes())
    assert len(route) == route_width * route_height * 2
    struct.pack_into("<H", route, 2 * (17 * route_width + 5), 0x0473)
    struct.pack_into("<H", route, 2 * (15 * route_width + 59), 0x30D1)
    # Open the grassy eastbound throat through the obsolete sign and tree
    # blocks to the Mt. Moon trigger at (68, 13).  The imported 0x3000/0x3001
    # road pair renders as blank cyan here, so use the route's visible lower
    # dirt-road phase instead.
    for x in range(66, 69):
        struct.pack_into("<H", route, 2 * (13 * route_width + x), 0x30D8)

    ROUTE_PATH.write_bytes(route)


if __name__ == "__main__":
    main()
