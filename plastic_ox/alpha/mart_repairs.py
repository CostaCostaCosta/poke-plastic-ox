"""Restore imported clerks and include affordable Leftovers in ordinary shops."""
import json,re
from pathlib import Path
from local_dialogue import replace
ROOT=Path(__file__).resolve().parents[2]

def stock(m):
    block=m[2]
    if 'ITEM_LEFTOVERS' not in block:
        if 'ITEM_NONE' in block:
            block=block.replace('.2byte ITEM_NONE','.2byte ITEM_LEFTOVERS\n\t.2byte ITEM_NONE')
        else:
            block += '\t.2byte ITEM_LEFTOVERS\n'
    return m[1]+block

def install(read,put):
    for path in sorted((ROOT/'data/maps').glob('*/scripts.inc')):
        p=str(path.relative_to(ROOT));s=read(p);s=replace(s,path.parent.name)
        # Existing marts retain their stock; append Leftovers to item tables only.
        for label in (re.findall(r'^\s*pokemart (\w+)',s,re.M) if ('Mart' in path.parent.name or 'DepartmentStore' in path.parent.name) else []):
            pattern=r'('+re.escape(label)+r':+\n)((?:\s*\.2byte[^\n]+\n)+)'
            s=re.sub(pattern,stock,s)
        if 'Mart' in path.parent.name:
            mp=str((path.parent/'map.json').relative_to(ROOT));d=json.loads(read(mp));changed=False
            for o in d['object_events']:
                if 'MART_EMPLOYEE' in o['graphics_id'] and 'pokemart' not in s:
                    o['script']='PoxRegionalMart';changed=True
            if changed:put(mp,json.dumps(d,indent=2)+'\n')
        if s!=read(p):put(p,s)
    for p in ['data/scripts/plastic_ox_goldenrod.inc','data/scripts/plastic_ox_league.inc']:
        s=read(p)
        for label in re.findall(r'^\s*pokemart (\w+)',s,re.M):
            s=re.sub(r'('+label+r':+\n)((?:\s*\.2byte[^\n]+\n)+)',stock,s)
        put(p,s)
    p='data/scripts/plastic_ox_regional_mart.inc'
    put(p,'''PoxRegionalMart::
\tlock
\tfaceplayer
\tmessage gText_HowMayIServeYou
\twaitmessage
\tpokemart PoxRegionalMart_Stock
\tmsgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
\trelease
\tend
\t.align 2
PoxRegionalMart_Stock:
\t.2byte ITEM_POKE_BALL
\t.2byte ITEM_GREAT_BALL
\t.2byte ITEM_SUPER_POTION
\t.2byte ITEM_HYPER_POTION
\t.2byte ITEM_REVIVE
\t.2byte ITEM_FULL_HEAL
\t.2byte ITEM_REPEL
\t.2byte ITEM_LEFTOVERS
\t.2byte ITEM_NONE
''')
    p='data/event_scripts.s';s=read(p);line='\t.include "data/scripts/plastic_ox_regional_mart.inc"\n'
    if line not in s:put(p,s+'\n'+line)
if __name__=='__main__':install(lambda p:(ROOT/p).read_text(),lambda p,s:(ROOT/p).write_text(s))
