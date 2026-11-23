#!/usr/bin/env python3
"""Plastic Ox virtual flag storage in SaveBlock3 (GetFlagPointer routing).

Checks that the extended block (POX_EXT_FLAGS, 0xB80..0xF7F) round-trips through
the real setflag/clearflag script commands, that a save from before the block
existed (garbage bytes, no magic) reads as all-clear, and that writing it never
touches the older poxEventFlags block (0xB00..0xB7F).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_story import StoryGame  # noqa: E402
from test_training_kit import run_code  # noqa: E402
from test_qol import opcode  # noqa: E402
from walklib import pox_virtual_flag_addr, POX_EXT_FLAGS_BYTES  # noqa: E402

EXT_MAGIC = 0x504F5846


def main():
    g = StoryGame()
    sb3 = g.u32(g.syms['gSaveBlock3Ptr'])
    size = g.sizes['gSaveblock3']
    ext = sb3 + size - POX_EXT_FLAGS_BYTES
    magic = ext - 4
    old_block = (magic - 16, magic)

    def cmd(name, flag):
        run_code(g, opcode(g, name) + struct.pack('<H', flag))

    def bit(flag):
        a = pox_virtual_flag_addr(sb3, size, flag)
        return bool(g.u8(a) & (1 << (flag % 8)))

    # An upgraded save: arbitrary bytes where the new block now lives.
    before = [g.u8(a) for a in range(*old_block)]
    g.write(magic, 0x12345678, 4)
    for i in range(POX_EXT_FLAGS_BYTES):
        g.write(ext + i, 0xA5)
    run_code(g, opcode(g, 'checkflag') + struct.pack('<H', 0xC00))
    assert g.u32(magic) == EXT_MAGIC, hex(g.u32(magic))
    assert all(g.u8(ext + i) == 0 for i in range(POX_EXT_FLAGS_BYTES))
    print('Pre-existing save: extended flags initialise to clear: PASS', flush=True)

    for flag in (0xB80, 0xB81, 0xD5A, 0xF7F):
        cmd('setflag', flag)
        assert bit(flag), hex(flag)
    assert sum(bin(g.u8(ext + i)).count('1') for i in range(POX_EXT_FLAGS_BYTES)) == 4
    cmd('clearflag', 0xB81)
    assert not bit(0xB81) and bit(0xB80)
    print('setflag/clearflag round-trip at both ends of 0xB80..0xF7F: PASS', flush=True)

    assert [g.u8(a) for a in range(*old_block)] == before
    cmd('setflag', 0xB07)
    assert bit(0xB07)
    cmd('clearflag', 0xB07)
    assert [g.u8(a) for a in range(*old_block)] == before
    print('poxEventFlags (0xB00..0xB7F) untouched and still addressable: PASS', flush=True)


if __name__ == '__main__':
    main()
