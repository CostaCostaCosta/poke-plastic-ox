#!/usr/bin/env python3
"""Generate public Gen 3 move metadata and canonical action ordering from training tables."""
import argparse
from pathlib import Path
import sys
p = argparse.ArgumentParser()
p.add_argument('--metamon', type=Path, required=True)
p.add_argument('--output', type=Path, default=Path(__file__).parent/'model')
a = p.parse_args()
sys.path.insert(0, str(a.metamon))
from metamon.rom_native_obs.distillation.memory import move_info, species_types, TYPES
from metamon.rom_native_obs.mappings_gen3 import MOVE_NAME_TO_ID, SPECIES_NAME_TO_ID
out = a.output
out.mkdir(parents=True, exist_ok=True)
def canonical(table):
    names = {}
    for name, token in table.items():
        if token not in names or len(name) < len(names[token]): names[token] = name
    return sorted((name, token) for token, name in names.items())

s = ['/* Generated from the causal schema public metadata; no battle state. */',
     'static const struct MmMoveInfo { float power, accuracy, priority; u16 flags, rank; u8 type, category; } sMoveInfo[355] = {']
for rank, (name, mid) in enumerate(canonical(MOVE_NAME_TO_ID)):
    if not 0 < mid <= 354: continue
    d = move_info(name); typ = d.get('type', 'unknown'); variable = name.startswith('hiddenpower')
    t = 1 if variable or typ not in TYPES else TYPES.index(typ)
    cat = 0 if variable else 4 if d.get('category') == 'Status' else 3 if typ in ('Fire','Water','Grass','Electric','Psychic','Ice','Dragon','Dark') else 2
    flags = d.get('flags', {})
    bits = [False, not variable, bool(d), not variable, not variable, flags.get('contact',0), flags.get('protect',0), flags.get('sound',0), d.get('target') in ('allAdjacent','allAdjacentFoes'), d.get('target') == 'self']
    values = [0 if variable else d.get('basePower',0)/512, 1 if d.get('accuracy') is True else d.get('accuracy',0)/100, d.get('priority',0)/8]
    s.append(f'    [{mid}] = {{'+', '.join(float(v).hex()+'f' for v in values)+f', {sum(int(bool(v))<<i for i,v in enumerate(bits))}, {rank}, {t}, {cat}'+'},')
s.append('};\nstatic const struct MmSpeciesInfo { u16 rank; u8 types[2]; } sSpeciesInfo[387] = {')
for rank, (name, sid) in enumerate(canonical(SPECIES_NAME_TO_ID)):
    if not 0 < sid <= 386: continue
    types = (species_types(name)+[0,0])[:2]
    s.append(f'    [{sid}] = {{{rank}, {{{types[0]}, {types[1]}}}}},')
s.append('};\n')
(out/'public_data.inc').write_text('\n'.join(s))
