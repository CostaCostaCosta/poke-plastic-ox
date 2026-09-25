#!/usr/bin/env python3
"""Play complete production battles with native Metamon decisions and UI inputs.

The test player's deterministic move picker uses only its own moves/PP; the
opponent is exclusively controlled by the embedded model. No HP/outcome patches.
"""
import array
import hashlib
import json
import struct
import wave
from pathlib import Path
from smoke import Game, ROOT, test_story, boot_new_game, begin_code, opcode, K

class AudioGame(Game):
    def __init__(self):
        self.audio = None
        self.samples = array.array('h')
        self.audio_counts = []
        self.pending_frames = []
        super().__init__()
        self.audio = self.core.get_audio_channels()
        self.core.set_audio_buffer_size(4096)
        self.audio.set_rate(32768)
        self.audio.clear()
    def frame(self, n=1):
        for _ in range(n):
            pending = False
            if self.audio:
                arena = self.u32(self.syms['sMetamon'])
                if arena:
                    offset = self.u32(self.syms['gMetamonTestLayout']+8)
                    pending = self.u8(arena+offset) == 1
            self.core.run_frame()
            if self.audio:
                samples = self.audio.read(self.audio.available)
                if pending:
                    self.audio_counts.append(len(samples)//2)
                    self.pending_frames.append(self.u32(self.syms['gMPlayInfo_BGM']+12))
                    if len(self.samples) < 32768*2*15: self.samples.extend(samples)
    def task(self, name):
        funcs = self.functions.get(name, set())
        return any(self.u8(self.syms['gTasks']+i*40+4) and
                   self.u32(self.syms['gTasks']+i*40)&~0x02000001 in funcs for i in range(16))


def main():
    test_story.boot_test_game = boot_new_game
    g = AudioGame()
    out = ROOT/'plastic_ox/battle/metamon/build'
    results=[]
    try:
        begin_code(g, opcode(g,'callnative')+struct.pack('<I',g.syms['GivePlasticOxPlayerParty']|1)+opcode(g,'releaseall')+opcode(g,'end'))
        g.frame(60)
        for battle in range(2):
            g.warp('OldaleTown',6,17); g.begin('OldaleTown_EventScript_Lance'); g.wait_action()
            assert g.u32(g.syms['sMetamon'])
            assert not any(g.u8(g.u32(g.syms['sMetamon'])+g.u32(g.syms['gMetamonTestLayout'])+i) for i in range(1536)), 'Recurrent state not reset'
            last = -1; menus=0
            layout=[g.u32(g.syms['gMetamonTestLayout']+i*4) for i in range(16)]
            move_off,pp_off=layout[7],layout[12]
            for step in range(50000):
                if not g.u32(g.syms['sMetamon']): break
                count=g.u32(g.syms['gMetamonCommits'])
                if count != last:
                    last=count
                    print('battle',battle,'commits',count,'moves',g.u32(g.syms['gMetamonMoves']),
                          'switches',g.u32(g.syms['gMetamonSwitches']),'replacements',g.u32(g.syms['gMetamonReplacements']),flush=True)
                if g.controller('HandleInputChooseAction'):
                    g.write(g.syms['gActionSelectionCursor'],0)
                    g.tap(K.KEY_A,hold=1,wait=2)
                elif g.controller('HandleInputChooseMove'):
                    b=g.syms['gBattleMons']; available=[]
                    for i in range(4):
                        move=g.u16(b+move_off+2*i); pp=g.u8(b+pp_off+i)
                        if move and pp:
                            # Test player: favor damaging attacks over setup/recovery.
                            power=struct.unpack('<f',bytes(g.u8(g.syms['sMoveInfo']+move*20+j) for j in range(4)))[0]
                            if move in (69,82,101): power=0.2
                            available.append((power,i))
                    slot=max(available,default=(0,0))[1]
                    g.write(g.syms['gMoveSelectionCursor'],slot)
                    g.tap(K.KEY_A,hold=1,wait=2)
                elif g.task('Task_HandleChooseMonInput'):
                    # Party UI puts Pokémon in display order. Pick a living reserve.
                    size=g.sizes['gParties']//24
                    slots=[i for i in range(1,6) if g.u16(g.syms['gParties']+i*size+size-14)>0]
                    if slots: g.write(g.syms['gPartyMenu']+9,slots[0])
                    menus+=1
                    g.tap(K.KEY_A,hold=1,wait=3)
                else:
                    g.tap(K.KEY_A,hold=1,wait=3)
                if step%2000==0: g.fb.to_pil().convert('RGB').save(str(out/'battle-progress.png'))
            else: raise AssertionError('Battle did not complete')
            result={name:g.u32(g.syms[name]) for name in ('gMetamonDecisions','gMetamonCommits','gMetamonFrames','gMetamonMoves','gMetamonSwitches','gMetamonReplacements','gMetamonFault')}
            result.update(outcome=g.u8(g.syms['gBattleOutcome']),player_party_selections=menus)
            assert not result['gMetamonFault'], result
            assert result['gMetamonCommits'] == result['gMetamonMoves']+result['gMetamonSwitches']+result['gMetamonReplacements']
            results.append(result)
            g.frame(240)
            for _ in range(1200):
                if g.u8(g.syms['sGlobalScriptContextStatus']) == 2 and not g.u32(g.syms['gBattleResources']): break
                g.tap(K.KEY_A,hold=1,wait=3)
            else: raise AssertionError('Teardown did not finish')
            print('COMPLETED',result,flush=True)
        report=dict(battles=results,rom_sha256=hashlib.sha256((ROOT/'pokeemerald.gba').read_bytes()).hexdigest(),
                    audio_inference_frames=len(g.audio_counts),audio_min_samples_per_frame=min(g.audio_counts),
                    audio_max_samples_per_frame=max(g.audio_counts),audio_peak=max(abs(v) for v in g.samples))
        (out/'battle-smoke.json').write_text(json.dumps(report,indent=2)+'\n')
        with wave.open(str(out/'inference-audio.wav'),'wb') as f:
            f.setnchannels(2);f.setsampwidth(2);f.setframerate(32768);f.writeframes(g.samples.tobytes())
        print(json.dumps(report,indent=2))
    except:
        g.fb.to_pil().convert('RGB').save(str(out/'battle-failed.png'))
        raise
if __name__ == '__main__': main()
