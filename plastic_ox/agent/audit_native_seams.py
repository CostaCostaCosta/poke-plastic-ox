#!/usr/bin/env python3
"""Deterministically audit every active native camera seam.

This checks reciprocal metadata, dimensions, walkable edge overlap, and
elevation agreement.  Water-only edges are reported separately because they
require Surf runtime coverage rather than an on-foot assertion.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'plastic_ox/alpha'))
from region_geometry import Geometry


def edge(g, direction, water=False):
    if direction in ('up', 'down'):
        y = 0 if direction == 'up' else g.h - 1
        return [(x, y) for x in range(g.w) if g.passable(x, y, water)]
    x = 0 if direction == 'left' else g.w - 1
    return [(x, y) for y in range(g.h) if g.passable(x, y, water)]


def main():
    manifest = json.loads((ROOT / 'plastic_ox/alpha/region_manifest.json').read_text())
    names = set(manifest['native_seams'])
    # The manifest records the authored side; include every connected map so
    # reciprocal metadata and the far edge are audited too.
    all_maps = {p.stem for p in (ROOT / 'data/maps').iterdir()
                if (p / 'map.json').exists()}
    names.update(name for name in all_maps
                 if json.loads((ROOT / 'data/maps' / name / 'map.json').read_text()).get('id') in
                 {target for source in manifest['native_seams'].values() for target in source})
    maps = {name: json.loads((ROOT / 'data/maps' / name / 'map.json').read_text())
            for name in names}
    by_id = {d['id']: name for name, d in maps.items()}
    failures, records = [], []
    seen = set()
    for name in sorted(names):
        g = Geometry(name)
        for conn in maps[name].get('connections') or []:
            dest = by_id.get(conn['map'])
            if not dest or dest not in names or conn['direction'] not in ('up', 'down', 'left', 'right'):
                continue
            pair = tuple(sorted((name, dest)))
            if (pair, conn['direction']) in seen:
                continue
            reverse = next((c for c in maps[dest].get('connections') or []
                            if c['map'] == maps[name]['id']), None)
            if not reverse:
                failures.append(f'{name}->{dest}: missing reciprocal connection')
                continue
            seen.add((pair, conn['direction']))
            gd = Geometry(dest)
            direction, offset = conn['direction'], conn['offset']
            ours = edge(g, direction)
            opposite = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}[direction]
            theirs = edge(gd, opposite)
            def aligned_cells(source, target):
                result = []
                for x, y in source:
                    dx, dy = (x - offset, gd.h - 1) if direction == 'up' else \
                              (x - offset, 0) if direction == 'down' else \
                              (gd.w - 1, y - offset) if direction == 'left' else \
                              (0, y - offset)
                    if (dx, dy) in target:
                        result.append((x, y, dx, dy))
                return result
            aligned = aligned_cells(ours, theirs)
            surf_ours = edge(g, direction, water=True)
            surf_theirs = edge(gd, opposite, water=True)
            surf_aligned = aligned_cells(surf_ours, surf_theirs)
            elev = [(x, y, g.tile(x, y)[1], gd.tile(dx, dy)[1])
                    for x, y, dx, dy in aligned
                    if g.tile(x, y)[1] not in (0, 15) and gd.tile(dx, dy)[1] not in (0, 15)
                    and g.tile(x, y)[1] != gd.tile(dx, dy)[1]]
            land_unmatched_source = [(x, y) for x, y in ours
                                     if (x, y) not in [(a, b) for a, b, _, _ in aligned]]
            land_unmatched_destination = [(x, y) for x, y in theirs
                                         if (x, y) not in [(a, b) for _, _, a, b in aligned]]
            water_only = not aligned and bool(surf_aligned)
            rec = {'source': name, 'destination': dest, 'direction': direction,
                   'offset': offset, 'source_openings': len(ours),
                   'destination_openings': len(theirs), 'aligned_openings': len(aligned),
                   'source_surf_openings': len(surf_ours),
                   'destination_surf_openings': len(surf_theirs),
                   'aligned_surf_openings': len(surf_aligned),
                   'unaligned_source_land': land_unmatched_source,
                   'unaligned_destination_land': land_unmatched_destination,
                   'elevation_mismatches': elev, 'water_only_or_closed': water_only}
            records.append(rec)
            if not reverse or reverse.get('offset') != -offset:
                failures.append(f'{name}->{dest}: reciprocal offset {reverse and reverse.get("offset")} != {-offset}')
            if not aligned and ours and theirs:
                if not water_only:
                    failures.append(f'{name}->{dest}: no aligned land or Surf opening')
            if elev:
                failures.append(f'{name}->{dest}: elevation mismatch at {elev}')
    out = ROOT / 'plastic_ox/demo/shots/native_seams_static.json'
    out.write_text(json.dumps(records, indent=2) + '\n')
    print(json.dumps({'seams': len(records), 'failures': failures}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
