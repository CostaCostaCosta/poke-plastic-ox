#!/usr/bin/env python3
"""Build standalone GBA benchmarks; run with the local mGBA Python environment."""
import argparse
import ctypes as C
import json
from pathlib import Path
import statistics
import subprocess


class Results(C.LittleEndianStructure):
    _fields_ = [("done", C.c_uint32), ("cycles", C.c_uint32*8),
                ("status", C.c_int32*8), ("actions", C.c_int32*8),
                ("logits", (C.c_float*9)*8), ("hidden", (C.c_float*384)*8)]


def build(src, out, toolchain, header, variant):
    prefix = str(toolchain.resolve() / "bin" / "arm-none-eabi-")
    common = ["-mcpu=arm7tdmi", "-mthumb-interwork", "-mabi=apcs-gnu", "-Wa,-meabi=5", "-O2", "-ffp-contract=off",
              "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-I"+str(src)]
    objects = []
    for name in ("runtime.c", "dot.c", "model.c", "benchmark.c", "bench_start.S", "weights.S", "fixtures.S"):
        path = out / name if name in ("model.c", "weights.S", "fixtures.S") else src / name
        obj = out / (variant + "-" + Path(name).stem + ".o")
        flags = ["-mthumb"]
        if name == "dot.c" and variant == "arm-iwram":
            flags = ["-marm", "-DMM_DOT_IWRAM"]
        subprocess.run([prefix+"gcc", *common, *flags, "-c", str(path), "-o", str(obj)], cwd=out, check=True)
        objects.append(str(obj))
    elf = out / (variant + ".elf")
    subprocess.run([prefix+"gcc", "-mcpu=arm7tdmi", "-mthumb", "-mthumb-interwork", "-mabi=apcs-gnu",
                    "-nostartfiles", "--specs=nosys.specs", "-Wl,--gc-sections",
                    "-T", str(src / "bench.ld"), *objects, "-lm", "-lc", "-lgcc",
                    "-o", str(elf)], cwd=out, check=True)
    rom = elf.with_suffix(".gba")
    subprocess.run([prefix+"objcopy", "-O", "binary", str(elf), str(rom)], check=True)
    data = bytearray(rom.read_bytes())
    # Existing valid cartridge header; preserve our entry branch.
    data[4:192] = header.read_bytes()[4:192]
    # A distinct game code is essential: mGBA's Emerald-specific idle-loop
    # address can otherwise halt unrelated benchmark instructions at that PC.
    data[0xa0:0xac] = b"METAMONBENCH"
    data[0xac:0xb0] = b"MMBE"
    data[0xbd] = (-sum(data[0xa0:0xbd]) - 0x19) & 255
    rom.write_bytes(data)
    symbols = subprocess.check_output([prefix+"nm", str(elf)], text=True)
    addr = next(int(line.split()[0], 16) for line in symbols.splitlines() if line.endswith(" gMmBenchResults"))
    return rom, addr


def run(rom, addr, expected):
    import mgba.core
    import mgba.image
    import mgba.log
    mgba.log.silence()
    core = mgba.core.load_path(str(rom))
    image = mgba.image.Image(*core.desired_video_dimensions())
    core.set_video_buffer(image)
    core.reset()
    off = addr - 0x02000000
    for _ in range(12000):
        core.run_frame()
        if core.memory.wram.u32[off] == 0x4d4d444e:
            break
    else:
        raise RuntimeError("GBA benchmark timed out after 12000 emulated frames")
    data = bytes(core.memory.wram.u8[off+i] for i in range(C.sizeof(Results)))
    r = Results.from_buffer_copy(data)
    assert all(x == 1 for x in r.status), list(r.status)
    le = max(abs(r.logits[i][j]-expected[i]["logits"][j]) for i in range(8) for j in range(9))
    he = max(abs(r.hidden[i][j]-expected[i]["hidden"][j]) for i in range(8) for j in range(384))
    assert le < 0.05 and he < 0.02, (le, he)
    assert list(r.actions) == [e["action"] for e in expected]
    times = [c / 16777216 for c in r.cycles]
    return dict(cycles=list(r.cycles), seconds=times, median_seconds=statistics.median(times),
                min_seconds=min(times), max_seconds=max(times),
                host_max_logit_error=le, host_max_hidden_error=he,
                legal_actions=list(r.actions),
                caveat="Emulated GBA timer cycles; no audio/IRQ/DMA or observation extraction. Not physical-hardware or full-battle latency.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--toolchain", type=Path, default=Path("/home/eddie/devkitpro/opt/devkitpro/devkitARM"))
    p.add_argument("--header-rom", type=Path, default=Path(__file__).resolve().parents[3]/"pokeemerald.gba")
    p.add_argument("--output", type=Path, default=Path(__file__).parent/"build")
    a = p.parse_args()
    src, out = Path(__file__).resolve().parent, a.output.resolve()
    assert len((out/"fixtures.bin").read_bytes()) == 8*3212, "Run verify.py first (eight fixtures required)"
    (out/"fixtures.S").write_text('.section .rodata\n.balign 4\n.global gMmFixtures\ngMmFixtures:\n.incbin "fixtures.bin"\n')
    expected = json.loads((out/"fixtures.json").read_text())
    reports = {}
    for variant in ("thumb-rom", "arm-iwram"):
        rom, addr = build(src, out, a.toolchain, a.header_rom, variant)
        reports[variant] = run(rom, addr, expected)
        print(variant, json.dumps(reports[variant]), flush=True)
    (out/"benchmark.json").write_text(json.dumps(reports, indent=2)+"\n")
