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
POX_FLAG_RANGES = ((0x020, 0x04F), (0x264, 0x2BB))
POX_SUPPLEMENTAL_FLAGS = {0x054, 0x055, 0x068, 0x096, 0x0E9, 0x1AA, 0x1AB,
                          0x1DA, 0x1DE, 0x1DF, 0x1E0, 0x1E1, 0x1E2, 0x1E3,
                          0x493, 0x494, 0x495}
POX_VAR_RANGE = range(0x40F7, 0x4100)


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

    allocated = {symbol: value(symbol) for symbol in definitions
                 if symbol.startswith("FLAG_POX_") or symbol == "FLAG_PREVENT_OVERWORLD_SPEEDUP"}
    errors = []
    by_value = defaultdict(list)
    for symbol, number in allocated.items():
        by_value[number].append(symbol)
        if not (any(start <= number <= end for start, end in POX_FLAG_RANGES)
                or number in POX_SUPPLEMENTAL_FLAGS):
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
    for path in (ROOT / 'data/maps').glob('*/map.json'):
        for event in json.loads(path.read_text()).get('bg_events', []):
            symbol = event.get('flag')
            if event.get('type') == 'hidden_item' and symbol in allocated and allocated[symbol] < 0x1F4:
                errors.append(f"Hidden item flag below FLAG_HIDDEN_ITEMS_START: {symbol}=0x{allocated[symbol]:03X} ({path.parent.name})")

    # Every supplemental ID must still be an unused Emerald flag. The one
    # historical exception is 0x096, whose Contest Pass symbol is retained but
    # has no read/write sites in the Emerald project.
    vanilla = (ROOT / 'include/constants/flags.h').read_text()
    aliases = defaultdict(list)
    for symbol, value_text in re.findall(r'^#define (FLAG_\w+)\s+(0x[0-9A-Fa-f]+)', vanilla, re.M):
        aliases[int(value_text, 0)].append(symbol)
    for number in POX_SUPPLEMENTAL_FLAGS:
        unsafe = [s for s in aliases[number]
                  if not s.startswith('FLAG_UNUSED_') and
                  not (number == 0x096 and s == 'FLAG_RECEIVED_CONTEST_PASS')]
        if unsafe:
            errors.append(f"Supplemental flag 0x{number:03X} aliases retained state: {', '.join(unsafe)}")

    var_defs = {}
    var_text = (ROOT / 'include/constants/vars.h').read_text()
    for symbol, number in re.findall(r'^#define (VAR_POX_\w+)\s+(0x[0-9A-Fa-f]+)', var_text, re.M):
        var_defs[symbol] = int(number, 0)
    var_defs.update({symbol: int(number, 0) for symbol, number in
                     re.findall(r'^#define (VAR_POX_\w+)\s+(0x[0-9A-Fa-f]+)',
                                (ROOT / 'include/constants/plastic_ox_flags.h').read_text(), re.M)})
    var_values = defaultdict(list)
    for symbol, number in var_defs.items():
        var_values[number].append(symbol)
        if number not in POX_VAR_RANGE:
            errors.append(f"Persistent var outside reserved/save range: {symbol}=0x{number:04X}")
    for number, symbols in var_values.items():
        if len(symbols) > 1:
            errors.append(f"Shared persistent var 0x{number:04X}: {', '.join(symbols)}")
    return allocated, errors


def state_inventory(flags):
    """Return every POX allocation and lexical read/write locations."""
    symbols = dict(flags)
    for path in ['include/constants/vars.h', 'include/constants/plastic_ox_flags.h']:
        for symbol, number in re.findall(r'^#define (VAR_POX_\w+)\s+(0x[0-9A-Fa-f]+)',
                                         (ROOT / path).read_text(), re.M):
            symbols[symbol] = int(number, 0)
    rows = []
    sites_by_symbol = defaultdict(list)
    source_paths = list((ROOT / 'data').rglob('*')) + list((ROOT / 'src').rglob('*'))
    source_paths += list((ROOT / 'plastic_ox').rglob('*'))
    symbol_pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, symbols)) + r')\b')
    for path in source_paths:
        if not path.is_file() or path.suffix not in {'.inc', '.s', '.c', '.h', '.json', '.py'}:
            continue
        for lineno, line in enumerate(path.read_text(errors='ignore').splitlines(), 1):
            for match in symbol_pattern.finditer(line):
                op = 'W' if re.search(r'\b(setflag|clearflag|setvar)\b', line) else 'R'
                sites_by_symbol[match.group()].append(f'{path.relative_to(ROOT)}:{lineno} ({op})')
    for symbol, number in sorted(symbols.items(), key=lambda item: (item[1], item[0])):
        sites = sites_by_symbol[symbol]
        purpose = ('persistent progression/value' if symbol.startswith('VAR_') else
                   'legacy save migration' if 'LEGACY_' in symbol else
                   'item/object persistence' if any(x in symbol for x in ('HIDDEN_', 'MANSION_1F_', 'ROUTE2_')) else
                   'story/object state')
        safety = ('valid persistent var' if symbol.startswith('VAR_') else
                  'reserved legacy input' if 'LEGACY_' in symbol else 'reserved flag')
        action = ('keep; range full' if symbol.startswith('VAR_') else
                  'keep reserved; do not write' if 'LEGACY_' in symbol else 'keep')
        rows.append((symbol, f'0x{number:04X}' if symbol.startswith('VAR_') else f'0x{number:03X}',
                     purpose, '<br>'.join(sites) or 'definition only', safety, action))
    return rows


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
    parser.add_argument('--markdown', action='store_true', help='print the complete custom state allocation/site table')
    args = parser.parse_args()
    flags, errors = flag_audit()
    report = inventory()
    report['flags'] = {name: f'0x{number:03X}' for name, number in sorted(flags.items())}
    report['errors'] = errors
    if args.markdown:
        print('| Symbol | ID | Purpose | Read/write locations | Safety | Action |')
        print('|---|---:|---|---|---|---|')
        for row in state_inventory(flags):
            print('| ' + ' | '.join(row) + ' |')
    elif args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Persistent flags: {len(flags)} unique allocations checked")
        print(f"Graph inventory: {len(report['maps'])} alpha/candidate maps, {len(report['generated_script_links'])} direct generated warp links")
        print('\n'.join(errors) if errors else 'Flag allocation audit: PASS')
        print('Physical v7 reachability and callback/escape analysis remain milestone work; use --json for inventory.')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
