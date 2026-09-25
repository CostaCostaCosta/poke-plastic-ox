#!/usr/bin/env python3
"""ROM noninterference tests: same public memory, own request and recurrent state.

Only emulator state is changed. Deliberately pause the battle engine before a
fresh decision so private substitutions cannot first produce new public events.
Run the native observation adapter AND tiled inference, then compare bytes.
"""
from pathlib import Path
import json
import struct
from smoke import Game, ROOT, test_story, boot_new_game, begin_code, opcode


def main():
    test_story.boot_test_game = boot_new_game
    g = Game()
    begin_code(g, opcode(g,'callnative')+struct.pack('<I',g.syms['GivePlasticOxPlayerParty']|1)+opcode(g,'releaseall')+opcode(g,'end'))
    g.frame(60); g.warp('OldaleTown',6,17); g.begin('OldaleTown_EventScript_Lance'); g.wait_action()
    if not g.u32(g.syms['gMetamonDecisions']): g.ready()
    base = g.u32(g.syms['sMetamon'])
    layout = [g.u32(g.syms['gMetamonTestLayout']+4*i) for i in range(16)]
    hidden, logits, state, decisions, action, mons, stride, moves, item, ability, hp, maxhp, pp, attack, status, personality = layout
    # A stable native decision boundary; the native public reducer stays intact.
    g.write(g.syms['gBattleMainFunc'], g.syms['BeginBattleIntroDummy']|1, 4)
    g.write(base+state, 0)
    g.write(g.syms['gBattlerControllerFuncs']+4, next(iter(g.functions['OpponentHandleChooseAction']))|1,4)
    saved = g.core.save_raw_state()
    assert saved is not None
    b = g.syms['gBattleMons']
    party = g.syms['gParties']; mon_size = g.sizes['gParties']//24
    def blob(addr,size): return bytes(g.u8(addr+i) for i in range(size))
    def words(addr, values, size=2):
        for i,v in enumerate(values): g.write(addr+i*size,v,size)
    cases = {
        'baseline': lambda: None,
        'unrevealed_reserves': lambda: words(party+mon_size,[0x5a]*(mon_size*5),1),
        'unrevealed_moves_and_order': lambda: words(b+moves,[1,2,3,4]),
        'unrevealed_item': lambda: g.write(b+item, 1, 2),
        'unrevealed_ability': lambda: g.write(b+ability, 23, 2),
        'exact_stats_and_ivs': lambda: words(b+attack,[777,666,555,444,333,222]),
        'exact_pp': lambda: words(b+pp,[1,2,3,4],1),
        'personality': lambda: g.write(b+personality, 0x12345678,4),
        'private_player_command': lambda: words(g.syms['gChosenMoveByBattler'],[354]),
    }
    before = None; result = {}
    for name, change in cases.items():
        assert g.core.load_raw_state(saved)
        change()
        count = g.u32(g.syms['gMetamonDecisions'])
        initial_hidden = blob(base+hidden,1536)
        for frame in range(1500):
            g.frame()
            if g.u32(g.syms['gMetamonDecisions']) != count: break
            assert blob(base+hidden,1536) == initial_hidden, 'Partial recurrent state became visible'
        else: raise AssertionError(name+' inference timeout')
        observed = (blob(base,3212), blob(base+3212,1536), blob(base+logits,36),g.u8(base+action))
        if before is None: before=observed
        assert observed == before, name+' changed observation/recurrent state/logits/action'
        result[name] = dict(status='passed',frames=frame+1)
        print(name, 'PASS', flush=True)
    (ROOT/'plastic_ox/battle/metamon/build/privacy.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__ == '__main__': main()
