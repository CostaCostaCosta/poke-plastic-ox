#!/usr/bin/env python3
"""Exercise the production trainer controllers in mGBA with emulator-only state."""
import json
from pathlib import Path
import struct
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'plastic_ox/demo'))
import test_story
from test_single_player import boot_new_game
from test_qol import begin_code, opcode
from walklib import K

class Game(test_story.StoryGame):
    def __init__(self, build=''):
        super().__init__(build=build)
        symbols = subprocess.check_output([test_story.NM, str(ROOT/('pokeemerald'+('-'+build if build else '')+'.elf'))], text=True)
        self.functions = {}
        for line in symbols.splitlines():
            parts = line.split()
            if len(parts) == 3 and parts[1] in ('t','T'):
                self.functions.setdefault(parts[2], set()).add(int(parts[0],16) & ~0x02000001)
    def controller(self, name):
        return self.u32(self.syms['gBattlerControllerFuncs']) & ~0x02000001 in self.functions[name]
    def wait_action(self):
        for i in range(3000):
            if self.controller('HandleInputChooseAction'): return
            self.tap(K.KEY_A, hold=1, wait=2)
        raise AssertionError('Action menu timed out')
    def ready(self):
        before = self.u32(self.syms['gMetamonDecisions'])
        for _ in range(1500):
            self.frame()
            if self.u32(self.syms['gMetamonDecisions']) > before: return
        raise AssertionError(('Inference timed out', self.u32(self.syms['sMetamon']), self.u32(self.syms['gMetamonFault'])))

def main():
    test_story.boot_test_game = boot_new_game
    g = Game()
    out = ROOT/'plastic_ox/battle/metamon/build'
    try:
        begin_code(g, opcode(g,'callnative')+struct.pack('<I',g.syms['GivePlasticOxPlayerParty']|1)+opcode(g,'releaseall')+opcode(g,'end'))
        g.frame(60)
        assert g.count() == 6
        g.warp('OldaleTown',6,17)
        g.begin('OldaleTown_EventScript_Lance')
        g.wait_action()
        print('Arena', hex(g.u32(g.syms['sMetamon'])), 'bytes', g.u32(g.syms['gMetamonArenaBytes']), flush=True)
        if not g.u32(g.syms['gMetamonDecisions']): g.ready()
        print('First inference',g.u32(g.syms['gMetamonDecisions']),g.u32(g.syms['gMetamonFrames']),flush=True)
        for turn in range(5):
            g.write(g.syms['gActionSelectionCursor'],0)
            g.tap(K.KEY_A,hold=1,wait=45)
            for _ in range(1500):
                if g.controller('HandleInputChooseMove'): break
                g.frame()
            assert g.controller('HandleInputChooseMove')
            g.tap(K.KEY_A,hold=1,wait=1)
            g.wait_action()
            print('Turn',turn+1,'decisions',g.u32(g.syms['gMetamonDecisions']),'frames',g.u32(g.syms['gMetamonFrames']),flush=True)
        g.fb.to_pil().convert('RGB').save(str(out/'smoke.png'))
    except:
        g.fb.to_pil().convert('RGB').save(str(out/'smoke-failed.png'))
        raise
if __name__ == '__main__': main()
