#!/usr/bin/env python3
"""Exercise every regional cave warp by walking onto its mouth in both directions."""
import json
import audit_region_rendering as audit
from walklib import DIRKEY


def main():
    caves = {n for n, m in audit.maps.items()
             if m['map_type'] == 'MAP_TYPE_UNDERGROUND'
             and ('_hns' in n or n.startswith('PlasticOx_'))}
    results = []
    for source, data in audit.maps.items():
        for index, warp in enumerate(data.get('warp_events', [])):
            dest = audit.by_id.get(warp['dest_map'])
            if dest is None or not ({source, dest} & caves):
                continue
            destination_index = int(warp['dest_warp_id'])
            assert 0 <= destination_index < len(audit.maps[dest]['warp_events'])
            landing = audit.maps[dest]['warp_events'][destination_index]
            assert audit.by_id.get(landing['dest_map']) == source, (source, index, 'nonreciprocal warp')
            assert int(landing['dest_warp_id']) == index, (source, index, 'wrong return index')
            attempts = []
            for direction, dx, dy in [('UP', 0, -1), ('DOWN', 0, 1), ('LEFT', -1, 0), ('RIGHT', 1, 0)]:
                x, y = warp['x']-dx, warp['y']-dy
                w, h, blocks = audit.geometry(source)
                if not (0 <= x < w and 0 <= y < h) or blocks[y*w+x] & 0xC00:
                    continue
                g = audit.setup()
                g.warp(source, x, y)
                for _ in range(8):
                    g.tap(DIRKEY[direction], hold=8, wait=30)
                    state = g.state()
                    if (state['group'], state['num']) != audit.ids[source]:
                        break
                state = g.state()
                actual = (state['group'], state['num'])
                if actual != audit.ids[dest]:
                    attempts.append((direction, actual, state['x'], state['y']))
                    continue
                g.wait_warp_complete(audit.ids[dest])
                g.frame(300)
                state = g.state()
                assert (state['group'], state['num']) == audit.ids[dest]
                distance = abs(state['x']-landing['x'])+abs(state['y']-landing['y'])
                assert distance <= 1, (source, index, 'incorrect landing', state)
                assert g.collision_at(state['x'], state['y'])[0] == 0, (dest, 'blocked landing')
                view = audit.visual(g, f'cave_{source}_{index}_{dest}')
                assert view['mismatches'] == 0, view
                result = dict(source=source, warp=index, destination=dest,
                              destination_warp=destination_index, approach=[x,y], view=view)
                results.append(result)
                print(json.dumps(result), flush=True)
                break
            else:
                raise AssertionError((source, index, 'cave crossing failed', attempts))
    assert results, 'no cave warps tested'
    (audit.OUT/'cave_report.json').write_text(json.dumps(results, indent=2))
    print(f'PASS: {len(results)} directed cave crossings, including return warps and post-transition soak')


if __name__ == '__main__':
    main()
