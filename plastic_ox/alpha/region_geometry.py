"""Source-layout geometry helpers for v7 port selection and static checks."""
from collections import deque
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
LAYOUTS = {l['id']: l for l in json.loads((ROOT/'data/layouts/layouts.json').read_text())['layouts']}
BEHAVIORS = [m[1] for line in (ROOT/'include/constants/metatile_behaviors.h').read_text().splitlines() if (m := re.match(r'\s*(MB_\w+)\s*,', line))]
ATTR_PATHS = dict(re.findall(r'const u\d+ (gMetatileAttributes_\w+)\[\] = INCBIN_U\d+\("([^"]+)"\)', (ROOT/'src/data/tilesets/metatiles.h').read_text()))
ATTR_SYMBOLS = dict(re.findall(r'const struct Tileset (gTileset_\w+)\s*=\s*\{.*?\.metatileAttributes\s*=\s*(gMetatileAttributes_\w+)', (ROOT/'src/data/tilesets/headers.h').read_text(), re.S))
DIRECTIONS = {'N': (0,-1), 'S': (0,1), 'E': (1,0), 'W': (-1,0)}


class Geometry:
    def __init__(self, name, data=None):
        self.data = data or json.loads((ROOT/f'data/maps/{name}/map.json').read_text())
        self.layout = LAYOUTS[self.data['layout']]
        self.w, self.h = self.layout['width'], self.layout['height']
        self.blocks = struct.unpack('<'+'H'*(self.w*self.h), (ROOT/self.layout['blockdata_filepath']).read_bytes())
        self.partition = 512 if self.layout['layout_version'] == 'emerald' else 640
        self.attrs = []
        for field in ['primary_tileset','secondary_tileset']:
            symbol = ATTR_SYMBOLS[self.layout[field]]
            raw = (ROOT/ATTR_PATHS[symbol]).read_bytes()
            size = 4 if self.layout['layout_version'] == 'frlg' else 2
            self.attrs.append(struct.unpack('<'+('I' if size == 4 else 'H')*(len(raw)//size), raw))

    def tile(self, x, y):
        value = self.blocks[y*self.w+x]
        mt = value & 1023
        attrs = self.attrs[mt >= self.partition]
        i = mt-self.partition if mt >= self.partition else mt
        behavior = attrs[i] & (511 if self.layout['layout_version'] == 'frlg' else 255)
        return (value >> 10)&3, value >> 12, BEHAVIORS[behavior]

    def passable(self, x, y, water=False):
        if not (0 <= x < self.w and 0 <= y < self.h):
            return False
        c,e,b = self.tile(x,y)
        bridge = b.startswith('MB_BRIDGE_') or b in ('MB_FORTREE_BRIDGE', 'MB_BIKE_BRIDGE_OVER_BARRIER')
        return c == 0 and (water or bridge or not any(k in b for k in ['WATER','CURRENT','OCEAN','POND','SEAWEED'])) and not any(k in b for k in ['HOLE','WARP','LADDER','DOOR','SECRET_BASE'])

    def component(self, anchor, water=False, blocked=frozenset()):
        start = min(((x,y) for y in range(self.h) for x in range(self.w) if self.passable(x,y,water) and (x,y) not in blocked), key=lambda p: abs(p[0]-anchor[0])+abs(p[1]-anchor[1]))
        seen = {start}
        todo = deque([start])
        while todo:
            x,y=todo.popleft()
            for direction,(dx,dy) in DIRECTIONS.items():
                xx,yy=x+dx,y+dy
                if 0 <= xx < self.w and 0 <= yy < self.h and self.tile(xx,yy)[2] == {'N':'MB_JUMP_NORTH','S':'MB_JUMP_SOUTH','E':'MB_JUMP_EAST','W':'MB_JUMP_WEST'}[direction]:
                    xx,yy=xx+dx,yy+dy
                if not self.passable(xx,yy,water) or (xx,yy) in seen or (xx,yy) in blocked:
                    continue
                e=self.tile(x,y)[1]; ee=self.tile(xx,yy)[1]
                if e not in (0,15) and ee not in (0,15) and e != ee and not (water and (e == 1 or ee == 1)):
                    continue
                seen.add((xx,yy)); todo.append((xx,yy))
        return seen

    def port(self, target, anchor, water=False, reserved=()):
        component = self.component(anchor, water)
        occupied = {(o['x'],o['y']) for o in self.data.get('object_events', [])} | set(reserved)
        warps = {(o['x'],o['y']) for o in self.data.get('warp_events', [])}
        options=[]
        for x,y in component-occupied-warps:
            # Coordinate warp destinations use signed bytes in WarpData.
            if x > 127 or y > 127:
                continue
            for direction,(dx,dy) in DIRECTIONS.items():
                approach=(x-dx,y-dy)
                if approach not in component or approach in occupied or approach in warps:
                    continue
                if approach[0] > 127 or approach[1] > 127:
                    continue
                score=abs(x-target[0])+abs(y-target[1])
                options.append((score,x,y,direction))
        if not options:
            raise ValueError(('No walkable port', target, anchor))
        _,x,y,direction=min(options)
        dx,dy=DIRECTIONS[direction]
        return {'tile':[x,y], 'approach':[x-dx,y-dy], 'direction':direction}
