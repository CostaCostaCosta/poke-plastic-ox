#!/usr/bin/env python3
"""Exact replay of src/malloc.c plus counterfactual AI memory reservations.

Baseline must reproduce every pointer, failure and final block list. Alternative
policies relocate game allocations through a pointer map; they are capacity
simulations, not executions of inference or proofs of future gameplay coverage.
"""
import argparse
from dataclasses import dataclass
import json
from pathlib import Path

PHASES = ['other', 'battle-start', 'resources', 'link-buffers', 'graphics',
          'ready', 'decision', 'decision-end', 'teardown', 'resources-freed',
          'party-menu', 'summary', 'action-committed']


@dataclass
class Block:
    address: int
    size: int
    used: bool = False
    owner: str = ''


class Heap:
    HEADER = 16

    def __init__(self, base, size):
        self.blocks = [Block(base, size-self.HEADER)]
        self.base, self.size = base, size

    def alloc(self, size, owner=''):
        size = (size+3) & ~3
        for i, b in enumerate(self.blocks):
            if not b.used and b.size >= size:
                if b.size-size >= 2*self.HEADER:
                    self.blocks.insert(i+1, Block(b.address+self.HEADER+size, b.size-size-self.HEADER))
                    b.size = size
                b.used, b.owner = True, owner
                return b.address+self.HEADER
        return 0

    def free(self, address):
        if not address: return
        i = next((i for i, b in enumerate(self.blocks) if b.address+self.HEADER == address), None)
        if i is None or not self.blocks[i].used:
            raise AssertionError(f'Invalid/double free {address:#x}')
        b = self.blocks[i]
        b.used, b.owner = False, ''
        if i+1 < len(self.blocks) and not self.blocks[i+1].used:
            b.size += self.HEADER + self.blocks.pop(i+1).size
        if i and not self.blocks[i-1].used:
            self.blocks[i-1].size += self.HEADER + self.blocks.pop(i).size

    def stats(self):
        free = [b.size for b in self.blocks if not b.used]
        return dict(free=sum(free), largest=max(free, default=0),
                    allocated=sum(b.size for b in self.blocks if b.used),
                    overhead=len(self.blocks)*self.HEADER, blocks=len(self.blocks))

    def layout(self):
        return [dict(address=b.address, size=b.size, allocated=int(b.used)) for b in self.blocks]


def replay(trace, policy='baseline', compact=False, heap_extra=0, omit_link=False, history=4096):
    heap, mapping, persistent, temporary = None, {}, 0, 0
    failures, phases, snapshots = [], {}, []
    in_battle = False
    minimum_free = minimum_largest = trace['heap_bytes']+heap_extra
    peak = 0
    temp_bytes = 39044 - (6144 if compact else 0)
    state_bytes = 1536 + history
    baseline = policy == 'baseline' and not heap_extra and not omit_link
    label_at = {}
    for label in trace.get('labels', []): label_at.setdefault(label['event'], []).append(label)

    def allocate(size, owner, event):
        ptr = heap.alloc(size, owner)
        if not ptr:
            failures.append(dict(sequence=event['sequence'], scenario=event['scenario'],
                phase=PHASES[event['phase']], requested=size, owner=owner, **heap.stats()))
        return ptr

    for e in trace['events']:
        kind, address = e['kind'], e['address']
        if kind == 0:
            if persistent or temporary: raise AssertionError('Heap reset while model state is live')
            heap = Heap(address, e['size']+heap_extra)
            mapping = {}
        elif heap is None:
            raise AssertionError('Trace starts after heap initialization')
        elif kind == 1:
            owner = trace['locations'].get(str(e['location']), '<unknown>')
            skip = omit_link and in_battle and e['phase'] == 3
            actual = 0 if skip else allocate(e['size'], owner, e)
            if baseline and actual != address:
                raise AssertionError(f"Baseline pointer mismatch at {e['sequence']}: {actual:#x} != {address:#x}")
            if address: mapping[address] = actual
        elif kind == 2:
            if address not in mapping: raise AssertionError(f'Unknown traced free {address:#x}')
            heap.free(mapping.pop(address))
        elif kind == 3:
            phase = e['phase']
            if phase == 1:
                in_battle = True
                if policy != 'baseline':
                    size = state_bytes + (temp_bytes if policy == 'resident' else 0)
                    persistent = allocate(size, 'model-persistent', e)
            elif phase == 6 and policy in ('transient', 'menu-overlap'):
                if temporary: raise AssertionError('New decision while old workspace is live')
                temporary = allocate(temp_bytes, 'model-workspace', e)
            elif (phase == 7 and policy == 'transient') or (phase == 12 and policy == 'menu-overlap'):
                heap.free(temporary); temporary = 0
            elif phase == 8:
                heap.free(temporary); temporary = 0
                heap.free(persistent); persistent = 0
            elif phase == 9:
                in_battle = False
        else:
            raise AssertionError(f'Unknown event kind {kind}')
        stats = heap.stats()
        if in_battle:
            minimum_free = min(minimum_free, stats['free'])
            minimum_largest = min(minimum_largest, stats['largest'])
            peak = max(peak, stats['allocated'])
            phase = PHASES[e['phase']]
            p = phases.setdefault(phase, dict(min_free=stats['free'], min_largest=stats['largest'], peak_allocated=0))
            p['min_free'] = min(p['min_free'], stats['free'])
            p['min_largest'] = min(p['min_largest'], stats['largest'])
            p['peak_allocated'] = max(p['peak_allocated'], stats['allocated'])
        for label in label_at.get(e['sequence']+1, []):
            snapshots.append(dict(**label, **stats))
    if persistent or temporary: raise AssertionError('Model allocation leaked at end of trace')
    if baseline and 'final_layout' in trace:
        assert heap.layout() == trace['final_layout'], 'Final heap blocks disagree with emulator memory'
    # A counterfactual diverges once any request fails; only its first failure is
    # meaningful for viability. Later simulated state cannot represent a real run.
    return dict(policy=policy, compact=compact, heap_extra=heap_extra, omit_link=omit_link,
                assumed_public_history_bytes=0 if policy == 'baseline' else history,
                viable_on_trace=not failures, first_failure=failures[0] if failures else None,
                failure_count=len(failures), min_battle_free=minimum_free,
                min_battle_largest=minimum_largest, peak_battle_allocated=peak,
                phases=phases, snapshots=snapshots)


def analyze(trace):
    assert trace['status'] == 'passed', 'Cannot certify an incomplete collection'
    baseline = replay(trace)
    assert baseline['viable_on_trace'], baseline
    candidates = []
    for history in (4096, 8192):
        for policy in ('resident', 'transient', 'menu-overlap'):
            for compact in (False, True):
                for heap_extra, omit_link in ((0, False), (0, True), (16384, False), (16384, True)):
                    candidates.append(replay(trace, policy, compact, heap_extra, omit_link, history))
    return dict(baseline=baseline, candidates=candidates,
        note='Baseline checked against every native allocator address and final heap layout. Alternatives simulate capacity only. Public history budgets are assumptions; compact buffer reuse and link-buffer omission are not implemented.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('trace', type=Path)
    p.add_argument('--output', type=Path, default=Path(__file__).parent/'build/heap-simulation.json')
    a = p.parse_args()
    result = analyze(json.loads(a.trace.read_text()))
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result['baseline'], indent=2))
    print('Viable candidates:', sum(c['viable_on_trace'] for c in result['candidates']), '/', len(result['candidates']))
