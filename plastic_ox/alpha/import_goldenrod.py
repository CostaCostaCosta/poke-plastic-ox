#!/usr/bin/env python3
"""Import Goldenrod's HNS interiors, assets and reviewed local event sources.

Run once (or deliberately refresh) with --donor; goldenrod.install reapplies
converted events after story generation without needing the donor checkout.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'plastic_ox/alpha/goldenrod'
sys.path.insert(0, str(ROOT / 'plastic_ox/agent'))
from remap_metatile_behaviors import build_mapping


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--donor', type=Path, required=True)
    args = ap.parse_args()
    donor = args.donor.resolve()
    layouts = json.loads((ROOT/'data/layouts/layouts.json').read_text())
    source_layouts = {l['id']: l for l in json.loads((donor/'data/layouts/layouts.json').read_text())['layouts']}
    groups = json.loads((ROOT/'data/maps/map_groups.json').read_text())
    gfx = (ROOT/'include/constants/event_objects.h').read_text()
    gfx_map = {'BALDING_MAN':'MAN_3', 'WORKER_M':'MAN_1', 'WORKER_F':'WOMAN_1',
        'ATTENDANT_M':'MAN_3','ATTENDANT_F':'WOMAN_2','MART_EMPLOYEE':'MART_EMPLOYEE',
        'GYM_GUY':'GYM_GUY','NURSE_CHANSEY':'CHANSEY','WHITNEY':'LASS',
        'OFFICER':'MAN_3','ENGINEER':'MAN_1','LITTLE_BOY':'BOY_1',
        'SUPER_NERD':'MAN_5','OLD_MAN_2':'OLD_MAN','ROCKER':'MAN_4',
        'TWIN':'LITTLE_GIRL','PICNICKER':'PICNICKER','CAMPER':'CAMPER',
        'SCIENTIST_M':'SCIENTIST_1','PSYCHIC_M':'PSYCHIC_M','ITEM_BALL':'ITEM_BALL',
        'POKE_BALL':'ITEM_BALL','LINK_RECEPTIONIST':'LINK_RECEPTIONIST'}
    manifest = {'donor':str(donor),'revision':subprocess.check_output(['git','-C',str(donor),'rev-parse','HEAD'],text=True).strip(),
                'group':'gMapGroup_PlasticOxInteriors','maps':{},'assets':[],
                'encounters':'None in the imported interiors; existing city encounters unchanged.',
                'events':'Local services and ambience; donor Rocket, train, rival and time-of-day stories removed. NPC movement pinned. Gates open.'}
    tilesets = set()
    flags = {}
    for path in sorted((donor/'data/maps').glob('GoldenrodCity_*_hns/map.json')):
        name = path.parent.name
        if name == 'GoldenrodCity_BillsHouse_hns': continue
        data = json.loads(path.read_text())
        source = copy.deepcopy(data)
        layout = copy.deepcopy(source_layouts[data['layout']])
        layout.pop('game_version',None)
        layout.update(layout_version='hns',include_in_versions=['emerald'])
        tilesets.update([layout['primary_tileset'],layout['secondary_tileset']])
        for key in ['border_filepath','blockdata_filepath']:
            target = ROOT/layout[key];target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(donor/layout[key],target)
        if not any(l['id']==layout['id'] for l in layouts['layouts']): layouts['layouts'].append(layout)
        data.pop('game_version',None)
        data.update(region='REGION_HOENN', music='MUS_RG_CELADON',connections=[],coord_events=[],allow_running=True)
        script = [f'{name}_MapScripts::\n\t.byte 0\n']
        objects=[]
        donor_script=(path.parent/'scripts.inc').read_text()
        for index,obj in enumerate(data['object_events']):
            old=obj['script'];g=obj['graphics_id']
            if any(s in g for s in ['ROCKET','SILVER','PROTON','ARCHER','ARIANA','PETREL','TRAIN_EAST','PUSHABLE_BOULDER']):continue
            if 'WHITNEY' in g and name != 'GoldenrodCity_Gym_hns':continue
            if 'MON_BASE' in g:continue
            if not re.search(r'\b'+re.escape(g)+r'\b',gfx):
                stem=g.removeprefix('OBJ_EVENT_GFX_').removesuffix('_HNS')
                g='OBJ_EVENT_GFX_'+gfx_map.get(stem,stem)
                if not re.search(r'\b'+re.escape(g)+r'\b',gfx):g='OBJ_EVENT_GFX_MAN_1'
            obj.update(graphics_id=g, movement_type='MOVEMENT_TYPE_FACE_DOWN',movement_range_x=0,movement_range_y=0,
                       trainer_type='TRAINER_TYPE_NONE',trainer_sight_or_berry_tree_id='0',flag='0')
            label=f'PoxGoldenrod_{name}_{index}'
            if 'BALL' in g:
                match=re.search(re.escape(old)+r'::?\s*\n\s*finditem (ITEM_\w+)',donor_script)
                assert match,(name,old)
                item=match[1].replace('ITEM_EXP_SHARE_SMALL','ITEM_EXP_SHARE')
                flag=f'FLAG_POX_GOLDENROD_ITEM_{len(flags):02d}'
                flags[flag]=0x900+len(flags)
                obj.update(flag=flag,script=label)
                script.append(f'{label}::\n\tfinditem {item}\n\tend\n')
            else:
                service=None
                if 'Brother_Haircut1' in old:service='PoxGoldenrod_OlderHaircut'
                elif 'Brother_Haircut2' in old:service='PoxGoldenrod_YoungerHaircut'
                elif 'HerbShop' in old:service=old
                elif name=='GoldenrodCity_Gym_hns' and 'Whitney' in old:service='Pox_Whitney'
                elif name=='GoldenrodCity_FlowerShop_hns' and 'Owner' in old:service='Pox_SquirtBottle'
                elif name=='GoldenrodCity_PokemonCenter_hns' and old=='OldaleTown_PokemonCenter_1F_EventScript_Nurse':service='PokemonCenter_Johto_hns_EventScript_Nurse'
                elif 'NameRater' in old:service='SlateportCity_NameRatersHouse_EventScript_NameRater'
                elif 'FriendshipRater' in old:service=old
                elif name=='GoldenrodCity_GameCorner_hns' and 'CoinsClerk' in old:service=old
                elif name=='GoldenrodCity_GameCorner_hns' and 'PrizeClerk' in old:service='POX_PU_CoinPrizes'
                elif name=='GoldenrodCity_BikeShop_hns' and old.endswith('_Clerk'):service='PoxGoldenrod_Bike'
                elif 'DepartmentStore_' in name and old.endswith('_Clerk'):service='PoxGoldenrod_Shop'+name.split('_')[-2]
                obj['script']=service or label
                if not service:
                    if 'TrainStation' in name:txt='The station is open to visitors.\\nTrain service is suspended.'
                    elif 'RadioTower' in name:txt='GOLDENROD RADIO TOWER!\\nOur voices reach every region.'
                    elif 'DepartmentStore' in name:txt='Take the stairs or elevator.\\nThere is a rooftop above the shops.'
                    elif 'Underground' in name:txt='Both brothers work here now.\\nTheir haircuts bring you closer.'
                    elif 'Gym' in name:txt='WHITNEY is waiting inside.\\nBring a team you trust!'
                    else:txt='GOLDENROD is a busy city.\\nTake a look inside its buildings!'
                    script.append(f'{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n{label}_Text:\n\t.string "{txt}$"\n')
            objects.append(obj)
        data['object_events']=objects
        for index,bg in enumerate(data['bg_events']):
            assert bg['type']=='sign',(name,bg)
            bg.pop('label',None);bg.pop('height',None)
            bg['script']='PoxGoldenrod_Directory'
            if 'GameCorner' in name and 'SlotMachine' in source['bg_events'][index].get('script',''):
                bg['script']='PoxGoldenrod_Slots'
            if 'Elevator' in name:bg['script']='PoxGoldenrod_Elevator'
        # A real control panel inside the lift; ordinary entry/exit remains a warp.
        if re.fullmatch('GoldenrodCity_DepartmentStore_[1-6]F_hns', name):
            for w in data['warp_events']:
                if w['dest_map']=='MAP_GOLDENROD_CITY_DEPARTMENT_STORE_ELEVATOR_HNS':w['y']=4
        if name=='GoldenrodCity_DepartmentStoreBasement_hns':
            data['warp_events'].append(dict(x=10,y=6,elevation=0,dest_map='MAP_GOLDENROD_CITY_DEPARTMENT_STORE_ELEVATOR_HNS',dest_warp_id='0'))
            script[0]=f'{name}_MapScripts::\n\tmap_script MAP_SCRIPT_ON_TRANSITION, PoxGoldenrod_BasementReturn\n\t.byte 0\nPoxGoldenrod_BasementReturn::\n\tsetdynamicwarp {data["id"]}, 10, 7\n\tend\n'
        if name=='GoldenrodCity_RadioTower_2F_hns':
            for o in data['object_events']:
                if (o['x'],o['y'])==(10,5):o['x']=12
        if 'Elevator' in name:
            data['warp_events'][0].update(dest_map='MAP_DYNAMIC',dest_warp_id='WARP_ID_DYNAMIC')
        if re.fullmatch('GoldenrodCity_DepartmentStore_[1-6]F_hns', name):
            label=f'PoxGoldenrod_Return{name}'
            script[0]=f'{name}_MapScripts::\n\tmap_script MAP_SCRIPT_ON_TRANSITION, {label}\n\t.byte 0\n{label}::\n\tsetdynamicwarp {data["id"]}, 9, 5\n\tend\n'
        # Source opens these gates through story callbacks. Bake the open tiles
        # into the converted map instead, using the source's own metatile IDs.
        edits=[]
        if 'UndergroundSwitches' in name:
            for n in range(1,7):
                body=re.search(rf'GoldenrodCity_UndergroundSwitches_EventScript_RemoveWall{n}::(.*?)\treturn',donor_script,re.S)[1]
                edits+=re.findall(r'setmetatile (\d+), (\d+), (0[xX][\dA-Fa-f]+), FALSE',body)
        elif 'UndergroundTunnel' in name:edits=[('12','10','0x2DD')]
        elif 'RadioTower_3F' in name:edits=re.findall(r'setmetatile (\d+), (\d+), (0[xX][\dA-Fa-f]+), FALSE',donor_script)
        if edits:
            p=ROOT/layout['blockdata_filepath'];raw=p.read_bytes();blocks=list(struct.unpack('<'+'H'*(len(raw)//2),raw))
            for x,y,mt in edits:
                i=int(y)*layout['width']+int(x);blocks[i]=(blocks[i]&0xF000)|int(mt,16)
            p.write_bytes(struct.pack('<'+'H'*len(blocks),*blocks))
        dump(BASE/f'{name}.json',data)
        (BASE/f'{name}.inc').write_text('\n'.join(script))
        if name not in groups[manifest['group']]:groups[manifest['group']].append(name)
        manifest['maps'][name]={'layout':layout,'source_warps':source['warp_events'],'source_objects':source['object_events'],
            'open_gate_tiles':edits,'source_map_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'converted_layout_sha256':{key:hashlib.sha256((ROOT/layout[key]).read_bytes()).hexdigest() for key in ['border_filepath','blockdata_filepath']},
            'source_layout_sha256':{key:hashlib.sha256((donor/layout[key]).read_bytes()).hexdigest() for key in ['border_filepath','blockdata_filepath']}}
    # Complete city door list, while keeping the current outdoor route exits.
    city=json.loads((donor/'data/maps/GoldenrodCity_hns/map.json').read_text())
    dump(BASE/'city_doors.json',city['warp_events'][2:])
    dump(BASE/'flags.json',flags)
    dump(ROOT/'data/maps/map_groups.json',groups)
    dump(ROOT/'data/layouts/layouts.json',layouts)
    donor_graphics=(donor/'src/data/tilesets/graphics.h').read_text()
    donor_mt=(donor/'src/data/tilesets/metatiles.h').read_text()
    for symbol in sorted(tilesets):
        sym=symbol.removeprefix('gTileset_')
        already_registered=bool(re.search(r'\b'+symbol+r'\s*;', (ROOT/'include/tilesets.h').read_text()))
        tilepath=re.search(rf'gTilesetTiles_{sym}\[\] = INCBIN_U32\("([^"]+)"',donor_graphics)[1]
        asset=Path(tilepath).parent
        manifest['assets'].append(str(asset))
        if already_registered:continue
        target=ROOT/asset
        shutil.copytree(donor/asset,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.4bpp*','*.gbapal','*.orig'))
        mapping=build_mapping()[2];p=target/'metatile_attributes.bin';raw=p.read_bytes()
        words=struct.unpack('<'+'H'*(len(raw)//2),raw)
        p.write_bytes(struct.pack('<'+'H'*len(words), *[(v&0xFF00)|mapping.get(v&255,(0,''))[0] for v in words]))
        additions={
            'include/tilesets.h':f'extern const struct Tileset {symbol};\n',
            'src/data/tilesets/headers.h':f'\nconst struct Tileset {symbol} = {{ .isCompressed = TRUE, .isSecondary = TRUE, .tiles = gTilesetTiles_{sym}, .palettes = gTilesetPalettes_{sym}, .metatiles = gMetatiles_{sym}, .metatileAttributes = gMetatileAttributes_{sym}, .callback = NULL }};\n',
            'src/data/tilesets/metatiles.h':'\n'+'\n'.join(l for l in donor_mt.splitlines() if f'_{sym}[]' in l)+'\n',
            'src/data/tilesets/graphics.h':f'\nconst u32 gTilesetTiles_{sym}[] = INCGFX_U32("{asset}/tiles.png", ".4bpp.fastSmol");\n'+f'const u16 gTilesetPalettes_{sym}[][16] = {{\n'+''.join(f'    INCGFX_U16("{p.relative_to(ROOT)}", ".gbapal"),\n' for p in sorted((target/'palettes').glob('*.pal')))+'};\n'}
        for rel,addition in additions.items():
            p=ROOT/rel;text=p.read_text()
            if rel=='include/tilesets.h':text=text.replace('#endif //GUARD_tilesets_H',addition+'\n#endif //GUARD_tilesets_H')
            else:
                if rel=='src/data/tilesets/headers.h':
                    addition=addition.replace(' = { ', ' =\n{\n    ').replace(', ', ',\n    ').replace(' };', ',\n};')
                text+=addition
            p.write_text(text)
    # The donor marks the interior exit mat as ANIMATED_DOOR, which makes
    # Emerald walk the arriving player south into the void. Keep its art but
    # use SOUTH_ARROW_WARP through a local primary attribute variant.
    attrs=bytearray((ROOT/'data/tilesets/primary/johto_building_hns/metatile_attributes.bin').read_bytes())
    behaviors=build_mapping()[0]
    for tile in [0x147, 0xE7]:attrs[tile*2]=behaviors.index('MB_SOUTH_ARROW_WARP')
    attrpath=ROOT/'data/tilesets/primary/johto_building_hns/goldenrod_metatile_attributes.bin'
    attrpath.write_bytes(attrs)
    declarations={
        'include/tilesets.h':'extern const struct Tileset gTileset_GoldenrodBuilding_Hns;\n',
        'src/data/tilesets/metatiles.h':'const u16 gMetatileAttributes_GoldenrodBuilding_Hns[] = INCBIN_U16("data/tilesets/primary/johto_building_hns/goldenrod_metatile_attributes.bin");\n',
        'src/data/tilesets/headers.h': 'const struct Tileset gTileset_GoldenrodBuilding_Hns =\n{\n    .isCompressed = TRUE,\n    .isSecondary = FALSE,\n    .tiles = gTilesetTiles_Johto_Building_Hns,\n    .palettes = gTilesetPalettes_Johto_Building_Hns,\n    .metatiles = gMetatiles_Johto_Building_Hns,\n    .metatileAttributes = gMetatileAttributes_GoldenrodBuilding_Hns,\n    .callback = NULL,\n};\n'}
    for rel,addition in declarations.items():
        p=ROOT/rel;text=p.read_text()
        if 'GoldenrodBuilding_Hns' not in text:
            if rel=='include/tilesets.h':text=text.replace('#endif //GUARD_tilesets_H',addition+'\n#endif //GUARD_tilesets_H')
            else:text+='\n'+addition
            p.write_text(text)
    ids={v['layout']['id'] for v in manifest['maps'].values()} | {'LAYOUT_GOLDENROD_CITY_BILLS_HOUSE_HNS'}
    for l in layouts['layouts']:
        if l['id'] in ids:l['primary_tileset']='gTileset_GoldenrodBuilding_Hns'
    dump(ROOT/'data/layouts/layouts.json',layouts)
    dump(BASE/'source_manifest.json',manifest)
    from goldenrod import install
    install(lambda p:(ROOT/p).read_text(), lambda p,s: ((ROOT/p).parent.mkdir(parents=True,exist_ok=True),(ROOT/p).write_text(s)))
    print(f'Imported {len(manifest["maps"])} Goldenrod interiors; {len(flags)} independent item flags.')


if __name__=='__main__':main()
