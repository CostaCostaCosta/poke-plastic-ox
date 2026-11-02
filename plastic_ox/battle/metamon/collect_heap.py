#!/usr/bin/env python3
"""Collect every heap event in real, interactive single trainer battles in mGBA.

Uses a separate profiling ROM and fresh emulator RAM, never a user's save.
Existing fixture helpers inject new-game initialization and a field script;
battle controllers, party/summary menus and teardown then execute normally.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "plastic_ox/demo"))
import test_story
from test_single_player import boot_new_game
from test_qol import begin_code, opcode
from walklib import K


class TraceGame(test_story.StoryGame):
    def __init__(self):
        self.events, self.cursor, self.labels = [], 0, []
        self.locations = {}
        self.scenario = "boot"
        self.functions = {}
        # Several battle controllers define static functions with the same name.
        # A name -> single address dictionary silently selects the wrong one.
        symbols = subprocess.check_output([test_story.NM, str(ROOT/'pokeemerald-metamon-heap.elf')], text=True)
        for line in symbols.splitlines():
            parts = line.split()
            if len(parts) == 3 and parts[1] in ('t', 'T'):
                self.functions.setdefault(parts[2], set()).add(int(parts[0], 16) & ~0x02000001)
        super().__init__(build="metamon-heap")

    def frame(self, n=1):
        for _ in range(n):
            self.core.run_frame()
            self.drain()

    def drain(self):
        count = self.u32(self.syms["gMetamonHeapTraceCount"])
        if not self.cursor <= count <= self.cursor + 512:
            raise AssertionError(f"Trace overwritten/reset: {self.cursor} -> {count}")
        base = self.syms["gMetamonHeapTrace"]
        while self.cursor < count:
            address = base + (self.cursor % 512) * 24
            values = [self.u32(address + j * 4) for j in range(6)]
            e = dict(zip(("kind", "frame", "address", "size", "location", "phase"), values))
            e["sequence"], e["scenario"] = self.cursor, self.scenario
            loc = e["location"]
            if loc and loc not in self.locations:
                chars = []
                for i in range(256):
                    c = self.u8(loc+i)
                    if c == 0: break
                    chars.append(c)
                self.locations[loc] = bytes(chars).decode("ascii")
            if e["kind"] == 3 and e["phase"] == 5:
                assert e["address"] & 8 and not e["address"] & 3, "Not an offline single trainer battle"
            self.events.append(e)
            self.cursor += 1

    def label(self, name):
        self.labels.append(dict(name=name, event=len(self.events), scenario=self.scenario))
        print(self.scenario, name, "events", len(self.events), flush=True)

    def heap_layout(self):
        head = self.u32(self.syms['sHeapStart'])
        result, p = [], head
        while True:
            assert head <= p < head + 115968 and self.u16(p+2) == 0xa3a3
            result.append(dict(address=p, size=self.u32(p+4) & 0x3ffff, allocated=self.u16(p) & 1))
            p = self.u32(p+12)
            if p == head: return result
            assert len(result) < 7248, 'Broken heap block chain'

    def controller(self, name):
        return self.u32(self.syms["gBattlerControllerFuncs"]) & ~0x02000001 in self.functions[name]

    def wait_action(self, key=K.KEY_A):
        for _ in range(2000):
            if self.controller("HandleInputChooseAction"):
                self.frame(500)
                return
            # A advances text. Stop before sending a new action command.
            self.tap(key, hold=1, wait=2)
        current = self.u32(self.syms["gBattlerControllerFuncs"]) & ~0x02000001
        names = [n for n, v in self.syms.items() if v & ~0x02000001 == current]
        raise AssertionError(f"Did not reach battle action menu: {names}, flags={self.u32(self.syms['gBattleTypeFlags']):x}")

    def choose_action(self, action):
        assert self.controller("HandleInputChooseAction")
        self.write(self.syms["gActionSelectionCursor"], action)
        self.tap(K.KEY_A, hold=1, wait=45)

    def battle(self, index, menus=True):
        self.scenario = f"lance-{index}"
        self.warp("OldaleTown", 6, 17)
        self.begin("OldaleTown_EventScript_Lance")
        self.wait_action()
        self.label("first-decision")
        if menus:
            self.choose_action(2)
            self.frame(90)
            self.label("party-open")
            assert any(e["phase"] == 10 for e in self.events[-200:])
            self.tap(K.KEY_A, hold=1, wait=30)
            self.tap(K.KEY_DOWN, hold=1, wait=10)
            self.tap(K.KEY_A, hold=1, wait=120)
            self.label("summary-open")
            assert any(e["phase"] == 11 for e in self.events[-200:]), "Summary did not open"
            self.tap(K.KEY_RIGHT, hold=1, wait=30)
            self.tap(K.KEY_RIGHT, hold=1, wait=30)
            self.wait_action(K.KEY_B)
            self.label("menus-closed")
        for turn in range(3):
            self.choose_action(0)
            assert self.controller("HandleInputChooseMove")
            self.tap(K.KEY_A, hold=1, wait=1)
            self.wait_action()
            self.label(f"turn-{turn+1}")
        self.choose_action(3)
        # Normal trainer forfeit confirmation and return to the field.
        for _ in range(2000):
            # The engine defaults to No. Select Yes only once the actual
            # confirmation controller is ready; A alone cancels forfeiting.
            if self.controller("PlayerHandleYesNoInput"):
                self.tap(K.KEY_UP, hold=1, wait=2)
            self.tap(K.KEY_A, hold=1, wait=3)
            if self.u32(self.syms["gMain"]+4) & ~0x02000001 == self.syms["CB2_Overworld"] & ~0x02000001:
                if self.u8(self.syms["sGlobalScriptContextStatus"]) == 2:
                    break
        else:
            raise AssertionError("Trainer forfeit did not finish")
        # Forfeits may warp home and run a whiteout dialogue after the first
        # return to CB2_Overworld. Finish those scripts before the next battle.
        self.frame(240)
        for _ in range(600):
            if self.u8(self.syms["sGlobalScriptContextStatus"]) == 2:
                break
            self.tap(K.KEY_A, hold=1, wait=3)
        assert self.u8(self.syms["sGlobalScriptContextStatus"]) == 2
        assert self.u32(self.syms["gBattleResources"]) == 0
        self.label("battle-released")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=Path(__file__).parent/"build/heap-trace.json")
    p.add_argument("--battles", type=int, default=3)
    a = p.parse_args()
    test_story.boot_test_game = boot_new_game
    g = TraceGame()
    try:
        begin_code(g, opcode(g, "callnative") + struct.pack("<I", g.syms["GivePlasticOxPlayerParty"] | 1)
                   + opcode(g, "releaseall") + opcode(g, "end"))
        g.frame(60)
        assert g.count() == 6
        for i in range(a.battles): g.battle(i)
        status = "passed"
    except Exception:
        status = "failed"
        a.output.parent.mkdir(parents=True, exist_ok=True)
        g.fb.to_pil().convert('RGB').save(str(a.output.with_suffix(".png")))
        raise
    finally:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        rom = ROOT/"pokeemerald-metamon-heap.gba"
        a.output.write_text(json.dumps(dict(status=status, rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
            heap_bytes=115968, header_bytes=16, trace_capacity=512, trace_events=len(g.events),
            instrumentation_ewram_bytes=12296, locations=g.locations, labels=g.labels,
            final_layout=g.heap_layout() if status == "passed" else None, events=g.events), indent=1)+"\n")
        print("Wrote", a.output, status, flush=True)


if __name__ == "__main__": main()
