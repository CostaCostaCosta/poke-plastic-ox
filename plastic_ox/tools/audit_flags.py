#!/usr/bin/env python3
"""Event-flag audit for the Emerald (Plastic Ox) build.

Answers "which flag IDs can I use?" and fails when two live allocations share
an ID. Read-only; it never edits headers.

  python3 plastic_ox/tools/audit_flags.py            # summary + collisions
  python3 plastic_ox/tools/audit_flags.py --free     # every usable ID, by pool
  python3 plastic_ox/tools/audit_flags.py --id 0x2D3 # who owns / references one ID
  python3 plastic_ox/tools/audit_flags.py --json     # machine-readable
  python3 plastic_ox/tools/audit_flags.py --check    # exit 1 on collisions (pox-check-static)

Pools, most preferred first (see the plastic-ox-flags skill):
  pox_ext      appended SaveBlock3 block (POX_EXT_FLAGS_START..), unused offsets
  pox_general  POX_EVENT_FLAGS_START +0..+63, unused offsets
  unused       vanilla IDs named FLAG_UNUSED_* (or undefined) with no live use
  reclaimable  vanilla IDs whose names are only referenced from maps that are
               unreachable in Plastic Ox (or not referenced at all)
  daily        unused daily flags (cleared every in-game day by the RTC)

"Live" means referenced from src/, include/ (outside the flag definitions),
data/ outside unreachable map folders, or Plastic Ox Python/tests. Map
reachability comes from audit_cleanup_artifacts.audit().
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_cleanup_artifacts import audit as map_audit  # noqa: E402

FLAGS_H = ROOT / 'include/constants/flags.h'
POX_HEADERS = sorted((ROOT / 'include/constants').glob('plastic_ox*.h'))
STORY_FLAGS = ROOT / 'plastic_ox/alpha/story_flags.json'

# Persistent vanilla ranges in SaveBlock1 (Emerald build). 0x00-0x1F are temp
# flags (cleared on map load) and 0x500-0x85F are ordinary trainer flags.
GENERAL = range(0x20, 0x500)
SYSTEM = range(0x860, 0x920)
DAILY = range(0x920, 0x960)

# IDs that include/constants/flags.h TRAINER_FLAG() remaps trainers onto.
# Keep in sync with that macro.
TRAINER_REMAP = {0x082: 'TRAINER_FLAG(932)', 0x4FA: 'TRAINER_FLAG(933)',
                 0x4FF: 'TRAINER_FLAG(934)', 0x4F9: 'TRAINER_FLAG(931)'}
TRAINER_REMAP.update({0x91D + i: f'TRAINER_FLAG({935 + i})' for i in range(3)})
TRAINER_REMAP.update({0x4EB + i: f'TRAINER_FLAG({926 + i})' for i in range(5)})
# 857..925 use the arithmetic run; 926..937 are overridden above.
TRAINER_REMAP.update({0x4A0 + i: f'TRAINER_FLAG({857 + i})' for i in range(925 - 857 + 1)})

# Vanilla runs that C code indexes arithmetically (base + i), so individual
# members show no by-name reference. Never hand these out.
INDEXED_RUNS = (
    ('TRAINER_REGISTERED_FLAGS_START', 0x15C, 0x1A9, 'Match Call registry (base + REMATCH_*)'),
    ('FLAG_DECORATION_1', 'FLAG_DECORATION_1', 'FLAG_DECORATION_14', 'decoration flags (base + i)'),
    ('FLAG_BADGE01_GET', 'FLAG_BADGE01_GET', 'FLAG_BADGE08_GET', 'badges (base + i)'),
    ('FLAG_SYS_TOWER_SILVER', 'FLAG_SYS_TOWER_SILVER', 'FLAG_SYS_PYRAMID_GOLD', 'Frontier symbols (base + i)'),
)

DEFINE = re.compile(r'^\s*#define\s+(\w+)\s+([^/\n]+?)\s*(?://.*)?$', re.M)


def parse_defines():
    """Macros as the Emerald build sees them (conditionals resolved by cpp)."""
    with tempfile.NamedTemporaryFile('w', suffix='.c', delete=False) as t:
        t.write('#include "constants/flags.h"\n')
    out = subprocess.run(['cpp', '-dM', '-DMODERN=1', '-DEMERALD', '-I', str(ROOT / 'include'), t.name],
                         capture_output=True, text=True, check=True).stdout
    Path(t.name).unlink()
    defs = {}
    for line in out.splitlines():
        m = re.match(r'#define\s+(\w+)\s+(.*)$', line)
        if m:
            defs[m.group(1)] = m.group(2).strip()
    pox = set()
    for p in POX_HEADERS:
        pox |= {m.group(1) for m in DEFINE.finditer(p.read_text())}
    return defs, pox


class Evaluator:
    def __init__(self, defs):
        self.defs, self.cache = defs, {}
        self.defs.setdefault('IS_FRLG', '0')

    def __call__(self, name, depth=0):
        if name in self.cache:
            return self.cache[name]
        expr = self.defs.get(name)
        if expr is None or depth > 40:
            return None
        def sub(m):
            v = self(m.group(0), depth + 1)
            return str(v) if v is not None else m.group(0)
        text = re.sub(r'\b[A-Za-z_]\w*\b', sub, expr)
        try:
            value = int(eval(text, {'__builtins__': {}}))
        except Exception:
            value = None
        self.cache[name] = value
        return value


def live_files(reachable):
    dead_dirs = {p.parent for p in (ROOT / 'data/maps').glob('*/map.json')
                 if p.parent.name not in reachable}
    flag_defs = {FLAGS_H, ROOT / 'include/constants/flags_frlg.h', *POX_HEADERS}
    me = Path(__file__).resolve()
    live, dead = [], []
    for base, sufs in (('src', {'.c', '.h'}), ('include', {'.h'}),
                       ('data', {'.inc', '.s', '.json', '.pory'}),
                       ('plastic_ox', {'.py', '.json'})):
        for p in (ROOT / base).rglob('*'):
            if not p.is_file() or p.suffix not in sufs or p in flag_defs or p == me:
                continue
            rel = p.relative_to(ROOT).as_posix()
            if rel.startswith(('plastic_ox/archive/', 'plastic_ox/wiki/')):
                continue
            if p.parent in dead_dirs:
                dead.append(p)
            elif base == 'data' and rel.startswith('data/maps/') and p.name in ('events.inc', 'header.inc', 'connections.inc'):
                continue  # generated from map.json in the same folder
            else:
                live.append(p)
    return live, dead


def build():
    reachable = set(map_audit()['protected'])
    defs, pox_names = parse_defines()
    ev = Evaluator(defs)
    story = json.loads(STORY_FLAGS.read_text())

    owners = defaultdict(set)           # id -> flag names that evaluate to it
    for name in defs:
        if not name.startswith('FLAG_'):
            continue
        v = ev(name)
        if v is not None:
            owners[v].add(name)
    for name, hexid in story.items():
        owners[int(hexid, 16)].add(name)
        pox_names.add(name)

    # A define whose value is just another name is an alias, not an
    # allocation (e.g. FLAG_CINNABAR_GYM_QUIZ_1 FLAG_POX_CINNABAR_QUIZ_1).
    aliases = {n for n in defs if re.fullmatch(r'\(?[A-Za-z_]\w*\)?', defs[n])}

    live, dead = live_files(reachable)
    names = {n for s in owners.values() for n in s}
    token = re.compile(r'\b(FLAG_\w+)\b')
    rawnum = re.compile(r'Flag(?:Set|Clear|Get|Toggle)\w*\(\s*(0x[0-9A-Fa-f]+|\d+)\s*\)')
    live_refs, dead_refs, raw_ids = defaultdict(set), defaultdict(set), defaultdict(set)
    tool_refs = defaultdict(set)
    tools = [p for p in live if p.relative_to(ROOT).parts[0] == 'plastic_ox']
    live = [p for p in live if p not in tools]
    for bucket, files in ((live_refs, live), (dead_refs, dead), (tool_refs, tools)):
        for p in files:
            text = p.read_text(errors='replace')
            rel = p.relative_to(ROOT).as_posix()
            for n in set(token.findall(text)) & names:
                bucket[n].add(rel)
            if bucket is live_refs:
                for num in rawnum.findall(text):
                    raw_ids[int(num, 0)].add(rel)

    def info(i):
        ns = sorted(owners.get(i, ()))
        return dict(id=f'0x{i:03X}', names=ns,
                    live={n: sorted(live_refs[n]) for n in ns if live_refs[n]},
                    dead={n: sorted(dead_refs[n]) for n in ns if dead_refs[n]},
                    tools={n: sorted(tool_refs[n]) for n in ns if tool_refs[n]},
                    indexed=indexed.get(i),
                    raw=sorted(raw_ids.get(i, ())), trainer=TRAINER_REMAP.get(i))

    indexed = {}
    for _, lo, hi, why in INDEXED_RUNS:
        lo = lo if isinstance(lo, int) else ev(lo)
        hi = hi if isinstance(hi, int) else ev(hi)
        for i in range(lo, hi + 1):
            indexed[i] = why

    pools = defaultdict(list)
    collisions = []
    for i in list(GENERAL) + list(SYSTEM) + list(DAILY):
        ns = owners.get(i, set())
        pox = sorted(n for n in ns if n in pox_names and n not in aliases)
        other_live = sorted(n for n in ns if n not in pox_names and n not in aliases
                            and not n.startswith('FLAG_UNUSED') and live_refs[n])
        claims = pox + other_live + ([TRAINER_REMAP[i]] if i in TRAINER_REMAP else [])
        if len(set(claims)) > 1 and not (len(pox) > 1 and len({defs.get(n) for n in pox}) == 1):
            collisions.append(dict(info(i), claims=claims))
        if claims or raw_ids.get(i) or i in indexed or any(tool_refs[n] for n in ns):
            continue
        if i in DAILY:
            pools['daily'].append(info(i))
        elif not ns or all(n.startswith('FLAG_UNUSED') for n in ns):
            pools['unused'].append(info(i))
        else:
            pools['reclaimable'].append(info(i))

    # Appended Plastic Ox blocks (virtual IDs stored in SaveBlock3).
    def block(start_name, count_name, lo=0, hi=None):
        start, count = ev(start_name), ev(count_name)
        if start is None or count is None:
            return []
        hi = count if hi is None else hi
        out = []
        for i in range(start + lo, start + hi):
            ns = sorted(n for n in owners.get(i, ()) if n not in aliases)
            if len(ns) > 1:
                collisions.append(dict(info(i), claims=ns))
            if not ns:
                out.append(dict(id=f'0x{i:03X}', offset=f'{start_name} + {i - start}'))
        return out
    pools['pox_general'] = block('POX_EVENT_FLAGS_START', 'POX_EVENT_FLAGS_COUNT', 0, 64)
    block('POX_EVENT_FLAGS_START', 'POX_EVENT_FLAGS_COUNT', 64, None)  # Sage trainers: collisions only
    pools['pox_ext'] = block('POX_EXT_FLAGS_START', 'POX_EXT_FLAGS_COUNT')
    return dict(pools=pools, collisions=collisions, info=info, reachable=len(reachable))


def ranges(ids):
    ids = sorted(int(x['id'], 16) for x in ids)
    out, i = [], 0
    while i < len(ids):
        j = i
        while j + 1 < len(ids) and ids[j + 1] == ids[j] + 1:
            j += 1
        out.append(f'0x{ids[i]:03X}' + (f'-0x{ids[j]:03X}' if j > i else ''))
        i = j + 1
    return ', '.join(out) or '(none)'


ORDER = ('pox_ext', 'pox_general', 'unused', 'reclaimable', 'daily')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--free', action='store_true', help='list every usable ID per pool')
    ap.add_argument('--id', help='show owners and references of one flag ID')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--check', action='store_true', help='exit 1 on collisions')
    a = ap.parse_args()
    r = build()
    if a.id:
        print(json.dumps(r['info'](int(a.id, 0)), indent=2))
        return 0
    if a.json:
        print(json.dumps(dict(pools=r['pools'], collisions=r['collisions']), indent=2))
        return 1 if r['collisions'] else 0
    if not a.check:
        print(f'reachable maps: {r["reachable"]}')
        for k in ORDER:
            ps = r['pools'].get(k, [])
            print(f'{k:12} {len(ps):4}  {ranges(ps)}')
        if a.free:
            for k in ('unused', 'reclaimable'):
                print(f'\n## {k}')
                for x in r['pools'].get(k, []):
                    dead = sorted({f.split('/')[2] for fs in x['dead'].values() for f in fs})
                    print(f"{x['id']}  {', '.join(x['names']) or '-'}" + (f"  (dead refs: {', '.join(dead)})" if dead else ''))
    for c in r['collisions']:
        print(f"COLLISION {c['id']}: {', '.join(c['claims'])}")
    if r['collisions']:
        print(f'{len(r["collisions"])} flag collision(s)', file=sys.stderr)
        return 1
    if a.check:
        print('audit_flags: no collisions')
    return 0


if __name__ == '__main__':
    sys.exit(main())
