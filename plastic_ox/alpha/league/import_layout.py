#!/usr/bin/env python3
"""Reproduce the compact outdoor route from the pinned HNS source geometry."""
import argparse
from pathlib import Path
import struct
import subprocess

REVISION='44f50eedefe58691b0444973e4138e9190d8fafc'
ROOT=Path(__file__).resolve().parents[3]

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=Path('/home/eddie/repos/pokehns-expansion'));a=p.parse_args()
    def original(name):
        return subprocess.check_output(['git','-C',str(a.source),'show',REVISION+':data/layouts/Route26_hns/'+name])
    blocks=list(struct.unpack('<'+'H'*(39*81),original('map.bin')))[:39*51]
    blocks[50*39:51*39]=blocks[49*39:50*39]
    out=ROOT/'data/layouts/PlasticOx_VictoryRoad';out.mkdir(parents=True,exist_ok=True)
    (out/'map.bin').write_bytes(struct.pack('<'+'H'*len(blocks),*blocks))
    (out/'border.bin').write_bytes(original('border.bin'))
    print('Route26 northern dry ridge: 39 x 51, HNS border preserved')

if __name__=='__main__':main()
