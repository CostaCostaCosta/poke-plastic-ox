#!/usr/bin/env python3
"""Read-only, conservative cleanup triage; emits JSON, never deletes maps."""
import json
import re
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def audit():
    maps = {p.parent.name: json.loads(p.read_text())
            for p in sorted((ROOT / 'data/maps').glob('*/map.json'))}
    ids = {m['id']: n for n, m in maps.items()}
    reasons = {}
    def seed(name, reason):
        if name in maps:
            reasons.setdefault(name, set()).add(reason)
    seed('PalletTown_Frlg', 'new-game region root')
    region = json.loads((ROOT / 'plastic_ox/alpha/region_manifest.json').read_text())
    for edge in region['transitions']:
        for key in ('source', 'destination'):
            seed(edge[key], 'region manifest')
    story = json.loads((ROOT / 'plastic_ox/alpha/story_manifest.json').read_text())
    for event in story['events']:
        seed(event['map'], 'story manifest')
    # Protect references even inside uncalled compatibility scripts. This is a
    # review set, not a proof of runtime reachability or an automatic delete set.
    for p in sorted((ROOT / 'data/scripts').glob('plastic_ox*.inc')):
        for token in re.findall(r'\bMAP_[A-Z0-9_]+\b', p.read_text()):
            seed(ids.get(token), str(p.relative_to(ROOT)))
    graph = {}
    for name, m in maps.items():
        destinations = [w['dest_map'] for w in m.get('warp_events', [])]
        destinations += [c['map'] for c in m.get('connections') or []]
        graph[name] = {ids[d] for d in destinations if d in ids}
    protected = set(reasons)
    queue = deque(sorted(protected))
    while queue:
        for dest in sorted(graph[queue.popleft()]):
            if dest not in protected:
                protected.add(dest)
                reasons[dest] = {'physical warp/connection closure'}
                queue.append(dest)
    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    candidates = set(maps) - protected
    grouped = {g: sorted(set(groups[g]) & candidates)
               for g in groups['group_order']}
    # External literal references remain dependencies, including C, headers,
    # shared scripts, encounters, generators and tests. Count files, not hits.
    references = {n: [] for n in candidates}
    suffixes = {'.c', '.h', '.inc', '.s', '.json', '.py'}
    for base in ('src', 'include', 'data', 'plastic_ox'):
        for p in sorted((ROOT / base).rglob('*')):
            if not p.is_file() or p.suffix not in suffixes or p == Path(__file__).resolve():
                continue
            if 'data/maps' in str(p) or p.name == 'map_groups.json':
                continue
            content = p.read_text(errors='replace')
            for token in set(re.findall(r'\bMAP_[A-Z0-9_]+\b', content)):
                name = ids.get(token)
                if name in references:
                    references[name].append(str(p.relative_to(ROOT)))
    return dict(total_maps=len(maps), protected_count=len(protected),
                candidate_count=len(candidates),
                protected={n: sorted(reasons[n]) for n in sorted(protected)},
                candidate_groups={g: ns for g, ns in grouped.items() if ns},
                candidate_external_map_id_references={n: references[n] for n in sorted(candidates)})


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
