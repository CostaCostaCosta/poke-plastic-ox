#!/usr/bin/env python3
"""Enter Route 2 from both towns and trigger real grass encounters in mGBA."""
from test_region_walk import setup, PORTS, current, navigate, cross, KEYS, DELTAS, BEHAVIORS, ROOT


def main():
    for entrance in ['cherry_route2_a', 'route2_rustboro_b']:
        g = setup()
        g.test_water = False
        p = PORTS[entrance]
        g.warp(p['source'], *p['approach'])
        cross(g, p['direction'], 'Route2_Frlg')
        def grass(x, y):
            return g.collision_at(x, y)[0] == 0 and BEHAVIORS[g.behavior_at(x, y)[0]] == 'MB_TALL_GRASS'
        def pair(x, y):
            return grass(x, y) and any(grass(x+dx, y+dy) for dx, dy in DELTAS.values())
        navigate(g, pair)
        s = g.state()
        start = s['x'], s['y']
        direction = next(k for k, (dx, dy) in DELTAS.items() if grass(start[0]+dx, start[1]+dy))
        reverse = dict(N='S', S='N', E='W', W='E')[direction]
        g.write(g.syms['sWildEncountersDisabled'], 0)
        for step in range(300):
            g.tap(KEYS[direction if step % 2 == 0 else reverse], hold=10, wait=20)
            if g.u32(g.syms['gBattleTypeFlags']):
                break
            assert current(g) == 'Route2_Frlg'
        else:
            raise AssertionError((entrance, 'no grass encounter'))
        g.frame(120)
        species = g.box_species(g.syms['gParties'] + g.sizes['gParties']//4)
        allowed = set()
        for time in ['Morning', 'Day', 'Night']:
            symbol = 'gPoxRoute31Hns_'+time+'_LandMons'
            stride = g.sizes[symbol]//12
            allowed.update(g.u16(g.syms[symbol]+i*stride+2) for i in range(12))
        assert species in allowed, (entrance, species, allowed)
        out = ROOT/'plastic_ox/demo/shots/region_walk'
        out.mkdir(exist_ok=True)
        g.fb.to_pil().convert('RGB').save(out/(entrance+'_encounter.png'))
        print(f'PASS {entrance}: grass encounter after {step+1} steps, species {species} belongs to the authored Route 31 schedule', flush=True)


if __name__ == '__main__':
    main()
