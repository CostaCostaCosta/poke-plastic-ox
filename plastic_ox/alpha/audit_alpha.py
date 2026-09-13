#!/usr/bin/env python3
"""Audit persistent alpha flags and inventory the current map/script graph.

Run from any directory. --json prints the inspection inventory without writing
files. Script checks are lexical evidence, not a reachability or gating proof.
"""
import argparse
import ast
from collections import defaultdict
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
HEADERS = ["include/constants/plastic_ox_flags.h", "include/constants/plastic_ox_story.h"]


def flag_audit():
    definitions = {}
    for name in HEADERS:
        for symbol, expression in re.findall(r"^#define (\w+)\s+([^\n]+)", (ROOT / name).read_text(), re.M):
            definitions[symbol] = expression.split("//")[0].strip()

    def value(symbol, pending=()):
        if symbol in pending:
            raise ValueError(f"Circular flag definition: {symbol}")
        tree = ast.parse(definitions[symbol], mode="eval").body

        def evaluate(node):
            if isinstance(node, ast.Constant) and type(node.value) is int:
                return node.value
            if isinstance(node, ast.Name):
                return value(node.id, (*pending, symbol))
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                return evaluate(node.left) + evaluate(node.right)
            raise ValueError(f"Unsupported flag expression: {symbol}")

        return evaluate(tree)

    allocated = {symbol: value(symbol) for symbol in definitions if symbol.startswith("FLAG_POX_")}
    errors = []
    by_value = defaultdict(list)
    for symbol, number in allocated.items():
        by_value[number].append(symbol)
        if not (0x020 <= number <= 0x04F or 0x264 <= number <= 0x2BB):
            errors.append(f"Outside reserved flag runs: {symbol}=0x{number:03X}")
    for number, symbols in by_value.items():
        if len(symbols) > 1:
            errors.append(f"Shared flag 0x{number:03X}: {', '.join(symbols)}")
    for symbol, number in json.loads((ROOT / 'plastic_ox/alpha/story_flags.json').read_text()).items():
        if allocated.get(symbol) != int(number, 0):
            errors.append(f"Generated story flag differs from stable allocation: {symbol}")
    # Catch references left behind when obsolete actors/items are retired.
    used = set()
    for directory, pattern in [('data/maps', '*/map.json'), ('data/maps', '*/scripts.inc'), ('data/scripts', '*.inc')]:
        for path in (ROOT / directory).glob(pattern):
            used.update(re.findall(r'\bFLAG_POX_\w+', path.read_text()))
    for symbol in sorted(used - allocated.keys()):
        errors.append(f"Unallocated map/script flag: {symbol}")
    return allocated, errors


def inventory():
    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    registered = {name for group in groups['group_order'] for name in groups[group]}
    maps = {path.parent.name: json.loads(path.read_text()) for path in (ROOT / 'data/maps').glob('*/map.json')}
    selected = {name for group in groups['group_order'] if 'PlasticOx' in group for name in groups[group]}
    selected.update(name for name, data in maps.items() if any(o.get('script', '').startswith('Pox_') for o in data.get('object_events', [])))
    # Include native candidate connectors, including their unintended old exits.
    selected.update(['PalletTown_Frlg', 'Route101', 'OldaleTown', 'Route103', 'Route104', 'Route110', 'Route115', 'Route116', 'Route119', 'Route125', 'Route128'])
    selected.update(name for name in maps if name.startswith(('SeafoamIslands_', 'MeteorFalls_', 'VictoryRoad_', 'UndergroundPath_')))
    selected.update(['Route1_Frlg', 'Route8_Frlg', 'Route19_Frlg', 'Route20_Frlg'])
    records = []
    for name in sorted(selected):
        if name not in maps:
            records.append({'map': name, 'missing': True})
            continue
        data = maps[name]
        records.append({
            'map': name, 'listed_in_groups': name in registered,
            'layout': data['layout'], 'region': data.get('region'),
            'game_version': data.get('game_version'),
            'connections': data.get('connections') or [],
            'warp_events': data.get('warp_events') or [],
            'coord_events': data.get('coord_events') or [],
            'object_scripts': [{'x': o['x'], 'y': o['y'], 'script': o.get('script'), 'flag': o.get('flag')} for o in data.get('object_events', [])],
            'map_script_source': f'data/maps/{name}/scripts.inc',
            'allow_escaping': data.get('allow_escaping'),
        })
    script_links = []
    text = (ROOT / 'data/scripts/plastic_ox_story.inc').read_text()
    for match in re.finditer(r'^(Pox_\w+)::\n(.*?)(?=^\w+::?\n|\Z)', text, re.M | re.S):
        label, body = match.groups()
        for warp in re.finditer(r'^\s*warp (MAP_\w+), (\d+), (\d+)', body, re.M):
            script_links.append({'script': label, 'destination': warp[1], 'x': int(warp[2]), 'y': int(warp[3]),
                                 'direct_unset_checks': re.findall(r'goto_if_unset (FLAG_\w+)', body)})
    return {
        'scope': 'Current alpha and candidate v7 modules; listing is not proof of Emerald inclusion or continuous traversal.',
        'script_analysis': 'Direct generated warp statements only; branch checks are lexical, not path predicates. Follow map callbacks and referenced native scripts separately.',
        'maps': records, 'generated_script_links': script_links,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='print full current topology and flag inspection as JSON')
    args = parser.parse_args()
    flags, errors = flag_audit()
    report = inventory()
    report['flags'] = {name: f'0x{number:03X}' for name, number in sorted(flags.items())}
    report['errors'] = errors
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Persistent flags: {len(flags)} unique allocations checked")
        print(f"Graph inventory: {len(report['maps'])} alpha/candidate maps, {len(report['generated_script_links'])} direct generated warp links")
        print('\n'.join(errors) if errors else 'Flag allocation audit: PASS')
        print('Physical v7 reachability and callback/escape analysis remain milestone work; use --json for inventory.')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
