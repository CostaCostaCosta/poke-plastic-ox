#!/usr/bin/env python3
"""Drive real registration, then verify identity and the one-time earthquake."""
import subprocess
from pathlib import Path
from walklib import GBA, K

ROOT = Path(__file__).resolve().parents[2]
NM = '/home/eddie/devkitpro/opt/devkitpro/devkitARM/bin/arm-none-eabi-nm'


def check(gender):
    g = GBA()
    syms = {}
    for line in subprocess.check_output([NM, str(ROOT / 'pokeemerald.elf')], text=True).splitlines():
        fields = line.split()
        if len(fields) == 3:
            syms[fields[2]] = int(fields[0], 16)
    def task(name):
        return any(g.u8(syms['gTasks'] + i * 40 + 4)
                   and g.u32(syms['gTasks'] + i * 40) & ~1 == syms[name] & ~1
                   for i in range(16))
    def callback(name):
        return g.u32(syms['gMain'] + 4) & ~1 == syms[name] & ~1
    g.frame(600)
    chose_gender = False
    for _ in range(500):
        if task('Task_NewGameBirchSpeech_ChooseGender') and not chose_gender:
            if gender:
                g.tap(K.KEY_DOWN, wait=60)
            g.tap(K.KEY_A, wait=40)
            chose_gender = True
        elif callback('CB2_NamingScreen'):
            break
        else:
            g.tap(K.KEY_A, hold=1, wait=20)
    else:
        raise AssertionError('Naming screen not reached')
    assert chose_gender
    g.frame(90)
    if gender == 0:
        g.fb.to_pil().convert("RGB").save("/tmp/pox-registration.png")
    # First key is A. Enter a custom name through the actual keyboard.
    g.tap(K.KEY_A, wait=90)
    g.tap(K.KEY_A, wait=90)
    g.tap(K.KEY_START, wait=60)
    g.tap(K.KEY_A, wait=100)
    for _ in range(200):
        if callback('CB2_Overworld'):
            break
        g.tap(K.KEY_A, hold=1, wait=20)
    else:
        raise AssertionError('Registration did not reach the bedroom')
    save2 = g.u32(syms['gSaveBlock2Ptr'])
    name = bytes(g.u8(save2 + i) for i in range(8))
    assert name[:3] == bytes([0xBB, 0xD5, 0xFF]), name
    assert g.u8(save2 + 8) == gender
    assert (g.state()['group'], g.state()['num']) == (38, 1)
    saw_shake = False
    for _ in range(100):
        saw_shake |= task('Task_ShakeCamera')
        g.tap(K.KEY_A, hold=1, wait=10)
    if gender == 0:
        g.fb.to_pil().convert("RGB").save("/tmp/pox-bedroom.png")
    assert saw_shake, 'Opening earthquake did not run'
    assert not task('Task_ShakeCamera'), 'Camera shake never ended'
    # Re-entering the bedroom script must not replay the quake.
    g.setvar(0x4001, 0)  # VAR_TEMP_1
    for _ in range(60):
        g.frame(10)
        assert not task('Task_ShakeCamera'), 'Opening earthquake replayed'
    assert g.u8(syms['gPartiesCount']) == 0
    print(f'PASS: gender={gender}, custom Aa retained, quake completes once, no starter yet')


if __name__ == '__main__':
    check(0)
    check(1)
