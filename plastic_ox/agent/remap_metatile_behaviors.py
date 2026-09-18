#!/usr/bin/env python3
"""Remap H&S metatile behaviors to our pokeemerald behavior IDs.

The imported Heart & Soul tilesets carry behavior IDs from the pokehns-expansion
metatile_behaviors.h enum, which has 243 entries vs our 240. The two tables are
identical for indices 0..128; hns inserts extra entries afterwards, shifting the
rest. This script builds a full name-based mapping between both enums, then rewrites
the behavior byte of every entry of every imported *_hns* metatile_attributes.bin,
preserving all other attribute bits (collision/layer/etc).

Idempotent: on first run the original file is kept alongside as
metatile_attributes.bin.orig; if that backup already exists the tileset is skipped.
"""
import argparse
import glob
import os
import re
import shutil
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OURS = os.path.join(REPO, 'include', 'constants', 'metatile_behaviors.h')
HNS = '/home/eddie/repos/pokehns-expansion/include/constants/metatile_behaviors.h'

# hns-only names -> safe fallback in OUR enum (exact-name matches need no entry)
FALLBACKS = {
    'MB_BOOKSHELF_GREEN':               'MB_UNUSED_81',         # bookshelf-ish
    'MB_SHOP_SHELF_DEPARTMENT':         'MB_UNUSED_82',         # shop-shelf-ish
    'MB_SHOP_SHELF_DEPARTMENT_FORWARD': 'MB_UNUSED_82',         # shop-shelf-ish
    'MB_TALL_GRASS_IMPASSABLE_NORTH':   'MB_TALL_GRASS',
    'MB_CAVE_IMPASSABLE_NORTH':         'MB_CAVE',
    'MB_WATER_NORTH_ARROW_WARP':        'MB_NORTH_ARROW_WARP',
    'MB_BRIDGE_OVER_ICE':               'MB_ICE',
}

ATTR_BEHAVIOR_MASK = 0x00FF  # bits 0-7
ATTR_BEHAVIOR_SHIFT = 0


def parse_enum(path):
    names = []
    with open(path) as f:
        for line in f:
            m = re.match(r'\s*(MB_\w+)\s*,', line)
            if m:
                names.append(m.group(1))
    return names


def build_mapping():
    ours = parse_enum(OURS)
    theirs = parse_enum(HNS)
    ours_idx = {n: i for i, n in enumerate(ours)}
    our_max = len(ours) - 1

    mapping = {}
    anomalies = []
    unmapped = []
    for i, name in enumerate(theirs):
        if name in ours_idx:
            mapping[i] = (ours_idx[name], name)
            if ours_idx[name] != i:
                anomalies.append((i, name, ours_idx[name], 'renumbered'))
        elif name in FALLBACKS:
            fb = FALLBACKS[name]
            if fb not in ours_idx:
                sys.exit(f'fallback {fb} not in our enum')
            mapping[i] = (ours_idx[fb], name)
            anomalies.append((i, name, ours_idx[fb], f'unmapped -> {fb}'))
            if i > our_max:
                anomalies.append((i, name, ours_idx[fb], 'BEYOND OUR MAX INDEX'))
        else:
            unmapped.append((i, name))
            mapping[i] = (ours_idx['MB_NORMAL'], name)
            anomalies.append((i, name, 0, 'NO MAPPING -> MB_NORMAL'))

    return ours, theirs, mapping, anomalies, unmapped, our_max


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    ours, theirs, mapping, anomalies, unmapped, our_max = build_mapping()
    print(f'our enum: {len(ours)} entries (max idx {our_max}); hns enum: {len(theirs)} entries')
    print(f'identical prefix through index 128 (MB_COUNTER region); '
          f'{sum(1 for i in mapping if mapping[i][0] != i)} hns indices require translation\n')

    print('FULL MAPPING TABLE (hns_idx -> our_idx): name')
    for i in range(len(theirs)):
        dst, name = mapping[i]
        flag = ''
        if i > our_max:
            flag = '  <<< BEYOND OUR MAX'
        elif dst != i:
            flag = '  *'
        print(f'  {i:3d} -> {dst:3d}: {name}{flag}')
    if unmapped:
        print(f'\nUNMAPPED NAMES (no exact match, no fallback): {unmapped}')
    print()

    changed_total = 0
    tilesets = sorted(glob.glob(os.path.join(REPO, 'data', 'tilesets', '*', '*_hns')))
    if not tilesets:
        sys.exit('no *_hns* tilesets found')
    for tsdir in tilesets:
        path = os.path.join(tsdir, 'metatile_attributes.bin')
        orig = path + '.orig'
        if not os.path.exists(path):
            print(f'{tsdir}: NO metatile_attributes.bin, skipping')
            continue
        if os.path.exists(orig):
            print(f'{tsdir}: .orig backup exists, skipping (idempotent)')
            continue

        data = bytearray(open(path, 'rb').read())
        if not args.dry_run:
            shutil.copy2(path, orig)

        changed = 0
        oob = []
        for off in range(0, len(data), 2):
            attr = data[off] | (data[off + 1] << 8)
            beh = (attr & ATTR_BEHAVIOR_MASK) >> ATTR_BEHAVIOR_SHIFT
            if beh in mapping:
                new = mapping[beh][0]
            else:
                # beyond even the hns enum: H&S placeholder garbage (e.g. 0xFF)
                new = 0
                oob.append(off // 2)
            if new != beh:
                attr = (attr & ~ATTR_BEHAVIOR_MASK) | ((new << ATTR_BEHAVIOR_SHIFT) & ATTR_BEHAVIOR_MASK)
                data[off] = attr & 0xFF
                data[off + 1] = (attr >> 8) & 0xFF
                changed += 1
        changed_total += changed
        note = f', {len(oob)} OOB>hns entries zeroed at {oob[:8]}{"..." if len(oob) > 8 else ""}' if oob else ''
        print(f'{tsdir}: {changed} entries changed{note}')
        if not args.dry_run:
            open(path, 'wb').write(bytes(data))

    print(f'\nTOTAL: {changed_total} entries changed across {len(tilesets)} tilesets')
    print('\nANOMALIES:')
    for i, name, dst, why in anomalies:
        print(f'  hns[{i:3d}] {name:36s} -> our[{dst:3d}] ({why})')


if __name__ == '__main__':
    main()
