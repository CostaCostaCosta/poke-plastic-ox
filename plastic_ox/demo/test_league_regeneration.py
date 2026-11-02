#!/usr/bin/env python3
"""Exercise real generators in memory/temp files, preserving the dirty checkout."""
import contextlib
import io
import json
import re
import runpy
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'plastic_ox/alpha'))
sys.path.insert(0,str(ROOT/'plastic_ox/agent'))
from league import install
from region_v7 import apply_region
import apply_trainer_teams_v2 as teams


def main():
    changes={}
    def read(p):return changes[p] if p in changes else ((ROOT/p).read_text() if (ROOT/p).exists() else '')
    def put(p,s):changes[p]=s
    install(read,put)
    expected=dict(changes)
    assert all((ROOT/p).read_text()==s for p,s in expected.items()), 'overlay is not applied'
    install(read,put)
    assert changes==expected,'overlay is not idempotent'
    apply_region(read,put)
    # Shared region/story files legitimately have non-League regeneration drift.
    owned=[p for p in expected if ('PlasticOx_' in p or 'IndigoPlateau' in p or p=='data/scripts/plastic_ox_league.inc')]
    for p in owned:assert changes[p]==expected[p],('region reverted',p)
    assert 'gPoxVictoryRoadOutdoor' in changes['src/data/wild_encounters.json']
    with contextlib.redirect_stdout(io.StringIO()):
        story=runpy.run_path(str(ROOT/'plastic_ox/alpha/build_story.py'))
    for p in owned:assert story['changes'][p]==expected[p],('story reverted',p)
    def encounter(source):
        return [e for e in json.loads(source)['wild_encounter_groups'][0]['encounters'] if e['map']=='MAP_PLASTIC_OX_VICTORY_ROAD']
    for generated in [changes,story['changes']]:
        assert encounter(generated['src/data/wild_encounters.json'])==encounter(expected['src/data/wild_encounters.json'])
        assert generated['include/constants/plastic_ox_flags.h']==expected['include/constants/plastic_ox_flags.h']
        assert generated['src/data/heal_locations.json']==expected['src/data/heal_locations.json']
    canonical=(ROOT/'plastic_ox/alpha/league/trainers.party').read_text()
    blocks=re.split(r'(?=^=== )',canonical,flags=re.M)
    for source in [changes['src/data/trainers.party'],story['changes']['src/data/trainers.party']]:
        for block in blocks:
            if block.strip():assert block.strip() in source,block.splitlines()[0]
    with tempfile.TemporaryDirectory() as tmp:
        teams.PARTY=Path(tmp)/'trainers.party';teams.REPORT=Path(tmp)/'report.json'
        teams.PARTY.write_text(expected['src/data/trainers.party'])
        with contextlib.redirect_stdout(io.StringIO()):assert teams.main()==0
        for block in blocks:
            if block.strip():assert block.strip() in teams.PARTY.read_text(),block.splitlines()[0]
    print(f'PASS: overlay idempotent ({len(expected)} files), region/story preserve {len(owned)} owned files and all 11 parties; actual generic team writer preserves authored sets')


if __name__=='__main__':main()
