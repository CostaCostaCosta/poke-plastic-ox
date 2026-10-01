"""Reapply converted Goldenrod interiors after region/story generation."""
import json
import re
from pathlib import Path

BASE = Path(__file__).with_suffix('')
CITY = 'GoldenrodCity_hns'


def install(read, put):
    def load(name):return json.loads(read(f'data/maps/{name}/map.json'))
    def save(name,data):put(f'data/maps/{name}/map.json',json.dumps(data,indent=2)+'\n')
    city=load(CITY)
    doors=json.loads((BASE/'city_doors.json').read_text())
    # Preserve old warp indexes for saved return warps and Bill's house.
    indices={}
    for source_index,door in enumerate(doors,2):
        index=next((i for i,w in enumerate(city['warp_events']) if (w['x'],w['y'])==(door['x'],door['y'])),None)
        if index is None:
            index=len(city['warp_events']);city['warp_events'].append(dict(door))
        else:city['warp_events'][index]=dict(door)
        indices[source_index]=index
    # Retired donor guards must not occupy restored building doorsteps.
    moved=json.loads((BASE/'city_npc_positions.json').read_text())
    for obj in city['object_events']:
        if obj['script'] in moved:obj['x'],obj['y']=moved[obj['script']]
    # Existing authored route connections, coordinate events and story NPCs stay intact.
    save(CITY,city)
    manifest=json.loads((BASE/'source_manifest.json').read_text())
    for name in manifest['maps']:
        data=json.loads((BASE/f'{name}.json').read_text())
        for warp in data['warp_events']:
            if warp['dest_map']=='MAP_GOLDENROD_CITY_HNS':warp['dest_warp_id']=str(indices[int(warp['dest_warp_id'])])
        save(name,data)
        put(f'data/maps/{name}/scripts.inc',(BASE/f'{name}.inc').read_text())
    bills=load('GoldenrodCity_BillsHouse_hns')
    bills['warp_events'][0].update(dest_map='MAP_GOLDENROD_CITY_HNS',dest_warp_id=str(indices[11]))
    save('GoldenrodCity_BillsHouse_hns',bills)
    # Retired shared Game Corner remains escapable for pre-import saves.
    corner=load('MauvilleCity_GameCorner')
    for warp in corner['warp_events']:warp.update(dest_map='MAP_GOLDENROD_CITY_HNS',dest_warp_id=str(indices[10]))
    save('MauvilleCity_GameCorner',corner)
    p='data/scripts/plastic_ox_story.inc'
    text=read(p).replace('warp MAP_PLASTIC_OX_WHITNEY_GYM, 5, 17','warp MAP_GOLDENROD_CITY_GYM_HNS, 10, 21')
    put(p,text)
    p='data/event_scripts.s';text=read(p)
    for name in manifest['maps']:
        line=f'\t.include "data/maps/{name}/scripts.inc"\n'
        if line not in text:text+='\n'+line
    line='\t.include "data/scripts/plastic_ox_goldenrod.inc"\n'
    if line not in text:text+='\n'+line
    put(p,text)
    put('data/scripts/plastic_ox_goldenrod.inc',(BASE/'services.inc').read_text())
    p='include/constants/plastic_ox_flags.h';text=read(p)
    text=re.sub(r'// Goldenrod item flags.*?// End Goldenrod item flags\.\n\n','',text,flags=re.S)
    flags=json.loads((BASE/'flags.json').read_text())
    block='// Goldenrod item flags: unused persistent slots, below DAILY_FLAGS_START.\n'
    block+=''.join(f'#define {name} 0x{value:03X}\n' for name,value in flags.items())+'// End Goldenrod item flags.\n\n'
    text=text.replace('#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H',block+'#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H')
    put(p,text)


if __name__=='__main__':
    install(lambda p:Path(p).read_text(),lambda p,s:(Path(p).parent.mkdir(parents=True,exist_ok=True),Path(p).write_text(s)))
