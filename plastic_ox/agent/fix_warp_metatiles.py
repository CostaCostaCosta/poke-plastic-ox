#!/usr/bin/env python3
"""Run-5 warp repair: give broken warp tiles a metatile the engine can warp on.

The run-3 warp playtest found a family of warps that never fire: the map JSON
declares a warp event, but the metatile under the coordinate has a behaviour the
engine's warp triggers ignore (`MB_NORMAL`, `MB_CAVE`, ...), so
`TryArrowWarp` / `TryStartWarpEventScript` in src/field_control_avatar.c can
never act on it.  Nearly all of them are a door whose middle lane still worked,
so the flanking lanes of the same door were left with a dead behaviour.

The repair clones the working lane's metatile into the map's secondary
tileset, rewrites only the behaviour field of the clone's attribute entry, and
repoints the blockmap entry.  Artwork, collision and elevation are therefore
identical to the lane that already works; no shared metatile is modified, so no
other map changes.

`CARVE` handles the two doors whose approach is solid rock in the FRLG import:
those tiles first copy the metatile of the walkable lane in front of them.

Re-running is a no-op once a coordinate already carries the wanted behaviour.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "plastic_ox/agent"))

from fix_pass5_static import BEH, load_catalog, tileset_dir  # noqa: E402

# metatile_attributes.bin layout per layout_version: (entry size, behavior mask)
ATTR = {"emerald": (2, 0x00FF), "hns": (2, 0x00FF), "frlg": (4, 0x000001FF)}

# Plain block copies with no behaviour change: seam continuations that the
# authored hns layer got wrong.  Each entry is (target x, y, source x, y).
PATCH = {
    # ECRUTEAK CITY -> ROUTE 37.  The city's south gate is only two tiles wide
    # (x=0,1 on the last row) while ROUTE 37's north gate is four (x=16..19),
    # so the two lanes on the far side of the seam dead-ended in rock.
    # Widen the city's exit to the four lanes the connection actually has.
    "EcruteakCity_hns": [(2, 59, 0, 59), (3, 59, 1, 59),
                         (2, 60, 0, 60), (3, 60, 1, 60),
                         # An unreachable two-tile pocket at elevation 4 inside
                         # the rock, which also acted as a phantom seam lane.
                         (18, 59, 17, 59), (19, 59, 17, 59)],
    # ROUTE 36's north gate is nine tiles wide on its first row but the road
    # below it is only open from x=32, so the last four columns hand the player
    # over into rock.  Narrow the gate to the road it actually feeds.
    "Route36_hns": [(38, 0, 42, 0), (39, 0, 42, 0),
                    (40, 0, 42, 0), (41, 0, 42, 0)],
    # ROUTE 37's road.  Rows 5 and 9 repeat the road metatiles with the
    # collision and elevation bits overwritten, which cut the route into three
    # pieces; rows 6 and 8 are the same road, intact.
    "Route37_hns": [(16, 5, 16, 6), (17, 5, 17, 6), (18, 5, 18, 6), (19, 5, 19, 6),
                    (16, 9, 16, 8), (17, 9, 17, 8), (18, 9, 18, 8), (19, 9, 19, 8),
                    # The south exit is fourteen lanes wide but ROUTE 36's north
                    # gate is five, and ROUTE 36's own row 1 is solid outside
                    # x=32..37, so only x=13..17 can be walked through.
                    (12, 39, 28, 39), (18, 39, 28, 39), (19, 39, 28, 39),
                    (20, 39, 28, 39), (21, 39, 28, 39), (22, 39, 28, 39),
                    (23, 39, 28, 39), (24, 39, 28, 39), (25, 39, 28, 39),
                    (26, 39, 28, 39), (27, 39, 28, 39),
                    (12, 40, 26, 40), (18, 40, 26, 40), (19, 40, 26, 40),
                    (20, 40, 26, 40), (21, 40, 26, 40), (22, 40, 26, 40),
                    (23, 40, 26, 40), (24, 40, 26, 40), (25, 40, 26, 40)],
}

# map -> (behaviour name, [(target x, y, (artwork source x, y)), ...])
REPAIRS = {
    # Three-wide hns gate houses: the middle lane of the south exit is an
    # arrow warp, the two flanking lanes were plain floor.
    "Route2_ViridianForest_NorthEntrance_Frlg":
        ("MB_SOUTH_ARROW_WARP", [(6, 9, (7, 9)), (8, 9, (7, 9))]),
    "Route2_ViridianForest_SouthEntrance_Frlg":
        ("MB_SOUTH_ARROW_WARP", [(6, 9, (7, 9)), (8, 9, (7, 9))]),
    "Route2_EastBuilding_Frlg":
        ("MB_SOUTH_ARROW_WARP", [(6, 9, (7, 9)), (8, 9, (7, 9))]),
    # The Union Room's south exit is two bridge tiles wide; only the left one
    # carried MB_BRIDGE_OVER_OCEAN, which is the behaviour
    # MetatileBehavior_IsUnionRoomWarp() keys the spin exit off.
    "UnionRoom": ("MB_BRIDGE_OVER_OCEAN", [(8, 11, (7, 11))]),
    # Route 2's north house: the bottom lane is the house door.
    "Route2_House_Frlg": ("MB_SOUTH_ARROW_WARP", [(4, 7, (4, 8))]),
    # FRLG interiors whose south exit is three tiles wide.
    "PalletTown_PlayersHouse_1F_Frlg":
        ("MB_SOUTH_ARROW_WARP", [(3, 8, (4, 8)), (5, 8, (4, 8))]),
    "PalletTown_RivalsHouse_Frlg":
        ("MB_SOUTH_ARROW_WARP", [(3, 8, (4, 8)), (5, 8, (4, 8))]),
    "UndergroundPath_EastEntrance_Frlg":
        ("MB_SOUTH_ARROW_WARP", [(5, 8, (6, 8)), (7, 8, (6, 8))]),
    "PokemonMansion_1F_Frlg":
        ("MB_SOUTH_ARROW_WARP", [(7, 33, (8, 33)), (9, 33, (8, 33)),
                                (33, 33, (34, 33)), (35, 33, (34, 33))]),
    # Mt. Moon's stairless south mouth and Route 8's Underground Path mouth are
    # both solid rock in the import; see CARVE.
    "Route8_Frlg": ("MB_SOUTH_ARROW_WARP", [(12, 17, (12, 20))]),
    "MeteorFalls_1F_1R": ("MB_NORTH_ARROW_WARP", [(4, 2, (4, 3))]),
}

# Solid tiles that must become walkable floor before they can carry a warp
# behaviour.  Each entry copies the whole block (metatile + collision +
# elevation) of the walkable lane in front of the door.
CARVE = {
    "Route8_Frlg": [(12, 14, (12, 20)), (12, 15, (12, 20)),
                    (12, 16, (12, 20)), (12, 18, (12, 20))],
    "MeteorFalls_1F_1R": [(4, 2, (4, 3))],
    # The Game Corner's B1F door opens onto solid rock on both sides, so a
    # player who takes it lands on the door and is wedged.
    "MossdeepCity_GameCorner_B1F": [(2, 1, (1, 1)), (4, 1, (1, 1))],
}


def primary_count(version):
    return 512 if version == "emerald" else 640


class Tileset:
    """One data/tilesets/<kind>/<name> directory, with the maps patched so far."""

    def __init__(self, directory, version):
        self.dir = directory
        self.version = version
        self.size, self.mask = ATTR[version]
        self.metatiles = bytearray((directory / "metatiles.bin").read_bytes())
        self.attrs = bytearray((directory / "metatile_attributes.bin").read_bytes())
        self.dirty = False

    def attr(self, index):
        return struct.unpack_from("<I" if self.size == 4 else "<H", self.attrs,
                                  index * self.size)[0]

    def set_attr(self, index, value):
        struct.pack_into("<I" if self.size == 4 else "<H", self.attrs,
                         index * self.size, value)

    def clone(self, source, source_index, behavior):
        """Metatile id carrying `source`'s artwork and `behavior`."""
        want = source.metatiles[source_index * 16:(source_index + 1) * 16]
        new_attr = (source.attr(source_index) & ~self.mask) | (behavior & self.mask)
        count = len(self.metatiles) // 16
        for index in range(count):
            if (self.metatiles[index * 16:(index + 1) * 16] == want
                    and self.attr(index) == new_attr):
                return primary_count(self.version) + index
        if primary_count(self.version) + count >= 1024:
            raise SystemExit(f"{self.dir.name}: secondary tileset is full")
        self.metatiles.extend(want)
        while len(self.attrs) < (count + 1) * self.size:
            self.attrs.extend(b"\0" * self.size)
        self.set_attr(count, new_attr)
        self.dirty = True
        return primary_count(self.version) + count

    def save(self):
        (self.dir / "metatiles.bin").write_bytes(self.metatiles)
        (self.dir / "metatile_attributes.bin").write_bytes(self.attrs)


class Blocks:
    def __init__(self, layout):
        self.layout = layout
        self.path = ROOT / layout["blockdata_filepath"]
        self.data = bytearray(self.path.read_bytes())

    def offset(self, x, y):
        return 2 * (y * self.layout["width"] + x)

    def get(self, x, y):
        return struct.unpack_from("<H", self.data, self.offset(x, y))[0]

    def set(self, x, y, value):
        struct.pack_into("<H", self.data, self.offset(x, y), value)

    def save(self):
        self.path.write_bytes(self.data)


def main():
    layouts, maps, _ = load_catalog()
    tilesets = {}
    log = []

    for name in sorted(set(PATCH) | set(REPAIRS)):
        data = maps[name]
        layout = layouts[data["layout"]]
        version = layout.get("layout_version", "emerald")
        behavior = BEH[REPAIRS[name][0]] if name in REPAIRS else None
        targets = REPAIRS.get(name, (None, ()))[1]
        blocks = Blocks(layout)

        def get(key):
            # Keyed by the resolved directory: two maps can share the
            # "primary_tileset"/"secondary_tileset" slot with completely
            # different tilesets behind it.
            directory = tileset_dir(layout[key], version)
            if directory not in tilesets:
                tilesets[directory] = Tileset(directory, version)
            return tilesets[directory]

        def cell(x, y):
            """(metatile id, owning Tileset, index within it)."""
            metatile = blocks.get(x, y) & 0x03FF
            if metatile < primary_count(version):
                return metatile, get("primary_tileset"), metatile
            return metatile, get("secondary_tileset"), metatile - primary_count(version)

        for x, y, sx, sy in PATCH.get(name, []):
            source = blocks.get(sx, sy)
            if blocks.get(x, y) == source:
                continue
            blocks.set(x, y, source)
            log.append(f"{name} ({x},{y}): block copied from ({sx},{sy}) "
                       f"(metatile {source & 0x03FF}, collision {source >> 10 & 3}, "
                       f"elevation {source >> 12}) - seam continuity")
        if PATCH.get(name):
            blocks.save()

        for x, y, (sx, sy) in CARVE.get(name, []):
            if blocks.get(x, y) & 0x0C00 == 0:
                continue  # already walkable
            block = blocks.get(sx, sy)
            blocks.set(x, y, block)
            log.append(f"{name} ({x},{y}): carved solid tile -> the walkable lane "
                       f"at ({sx},{sy}) (metatile {block & 0x03FF})")
        if CARVE.get(name):
            blocks.save()

        for x, y, (sx, sy) in targets:
            metatile, owner, index = cell(x, y)
            art_block = blocks.get(sx, sy)
            if owner.attr(index) & owner.mask == behavior:
                # Already the right behaviour; still copy the source lane's
                # collision bits, which is what makes a carved-out wall tile
                # standable on a re-run.
                fixed = (blocks.get(x, y) & ~0x0C00) | (art_block & 0x0C00)
                if fixed != blocks.get(x, y):
                    blocks.set(x, y, fixed)
                    log.append(f"{name} ({x},{y}): collision bits taken from "
                               f"({sx},{sy})")
                continue
            _src_mt, source, source_index = cell(sx, sy)
            # Always clone into the secondary tileset: an hns/frlg primary is
            # fixed at 640 metatiles, so a clone there would shift every
            # secondary metatile id in the layout.
            try:
                new_id = get("secondary_tileset").clone(source, source_index, behavior)
            except struct.error:
                raise SystemExit(
                    f"{name} ({x},{y}): cannot clone - source tileset "
                    f"{source.dir.name} attr entry width {source.size} into "
                    f"{get('secondary_tileset').dir.name} width "
                    f"{get('secondary_tileset').size}")
            old_behavior = owner.attr(index) & owner.mask
            # A tile carved out of a wall keeps the wall's collision bits unless
            # they are copied from the lane whose artwork it now uses.
            # Only the metatile id changes; collision and elevation are taken
            # from the lane whose artwork the tile now uses.  Building the block
            # from scratch keeps the old metatile's bits from being OR-ed back
            # in (709 | 710 == 711).
            blocks.set(x, y, (art_block & 0xFC00) | new_id)
            log.append(f"{name} ({x},{y}): metatile {metatile} -> {new_id}, "
                       f"behaviour {old_behavior} -> {behavior:#x} "
                       f"(artwork copied from ({sx},{sy}))")
        blocks.save()

    for ts in tilesets.values():
        if ts.dirty:
            ts.save()
    print("\n".join(log))
    print(f"{len(log)} block(s) repointed")


if __name__ == "__main__":
    main()