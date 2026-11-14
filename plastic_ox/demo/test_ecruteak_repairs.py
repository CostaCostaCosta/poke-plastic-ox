#!/usr/bin/env python3
"""Exercise repaired Ecruteak entrances and badge checkpoint in a fresh ROM."""
from pathlib import Path
from test_story import StoryGame
from test_burned_tower import at, visible_actor_ids
from test_sudowoodo_v1 import drain
from walklib import K
OUT=Path('/tmp/ecruteak-repairs');OUT.mkdir(exist_ok=True)
def shot(g,n):g.fb.to_pil().convert('RGB').save(OUT/(n+'.png'))
def main():
 g=StoryGame();g.flag('FLAG_POX_STORY_STARTER',True);g.flag('FLAG_ADVENTURE_STARTED',True)
 g.warp('EcruteakCity_hns',22,15);g.hold(K.KEY_UP,24);g.frame(180)
 assert at(g,'PlasticOx_BurnedTower'),g.state()
 g.hold(K.KEY_DOWN,40);g.frame(180)
 assert at(g,'EcruteakCity_hns') and g.state()['x']==22 and 14<=g.state()['y']<=17,g.state()
 shot(g,'tower_return');print('tower round trip PASS',flush=True)
 g.warp('EcruteakCity_hns',28,48);g.hold(K.KEY_UP,24);g.frame(180)
 assert at(g,'EcruteakCity_House2_hns'),g.state()
 print('house arrival',g.state(),flush=True)
 g.hold(K.KEY_UP,32);g.frame(60)
 assert at(g,'EcruteakCity_House2_hns') and g.state()['y']<7,g.state()
 shot(g,'house_inside');g.hold(K.KEY_DOWN,80);g.frame(180)
 assert at(g,'EcruteakCity_hns'),g.state()
 print('house walk and return PASS',flush=True)
 # The theater door must open the kimono hall (21x19 theater layout), not the
 # Rustboro Gym layout the PlasticOx room was imported on.
 g.warp('EcruteakCity_hns',39,41);g.hold(K.KEY_UP,26);g.frame(180)
 assert at(g,'PlasticOx_DanceTheater'),g.state()
 assert (g.state()['x'],g.state()['y'])==(10,17),g.state()
 header=g.mapheader_info();assert (header['w'],header['h'])==(21,19),header
 g.hold(K.KEY_UP,32);g.frame(60)
 assert at(g,'PlasticOx_DanceTheater') and g.state()['y']<17,g.state()
 shot(g,'dance_hall')
 g.hold(K.KEY_DOWN,44);g.frame(180)
 assert at(g,'EcruteakCity_hns') and g.state()['x']==39,g.state()
 print('dance theater door, theater layout, and return PASS',flush=True)
 # All five dancers stand on the stage together.
 g.warp('PlasticOx_DanceTheater',10,4);g.frame(120)
 assert {1,2,3,4,5} <= visible_actor_ids(g),visible_actor_ids(g)
 shot(g,'dance_stage')
 print('kimono troupe staged together PASS',flush=True)
 for y in range(34,38):
  g.warp('EcruteakCity_hns',9,y);g.hold(K.KEY_LEFT,24);g.frame(180)
  assert at(g,'Gate_EcruteakCity_Route38_hns'),(y,g.state())
 print('all west gate lanes PASS',flush=True)
 g.warp('Gate_EcruteakCity_Route38_hns',5,5);g.hold(K.KEY_LEFT,16);g.frame(30)
 shot(g,'badge_check')
 for _ in range(12):g.hold(K.KEY_B,4);g.frame(24)
 drain(g)
 assert at(g,'Gate_EcruteakCity_Route38_hns') and g.state()['x']==5,g.state()
 for i in range(1,9):g.flag(f'FLAG_BADGE{i:02}_GET',True)
 g.hold(K.KEY_LEFT,16);g.frame(180)
 assert at(g,'PlasticOx_VictoryRoad'),g.state()
 g.hold(K.KEY_DOWN,40);g.frame(180)
 assert at(g,'Gate_EcruteakCity_Route38_hns'),g.state()
 shot(g,'gate_return');g.hold(K.KEY_RIGHT,120);g.frame(180)
 assert at(g,'EcruteakCity_hns'),g.state()
 shot(g,'town_west');print('badge denial, approval, League return PASS',flush=True)
 g.warp('EcruteakCity_hns',36,42);shot(g,'theater_npc')
 import json
 city=json.loads((Path(__file__).resolve().parents[2]/'data/maps/EcruteakCity_hns/map.json').read_text())
 guards=[(i+1,o) for i,o in enumerate(city['object_events']) if o['flag']=='FLAG_BADGE03_GET']
 for local,o in guards:
  g.flag('FLAG_BADGE03_GET',False);g.warp('EcruteakCity_hns',o['x']-1,o['y'])
  assert local in visible_actor_ids(g)
  shot(g,'east_guard_'+str(local))
  g.flag('FLAG_BADGE03_GET',True);g.warp('EcruteakCity_hns',o['x']-1,o['y'])
  assert local not in visible_actor_ids(g)
 print('east guards follow Morty badge PASS',flush=True)
if __name__=='__main__':main()
