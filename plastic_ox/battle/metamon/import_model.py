#!/usr/bin/env python3
"""Validate an MG3SINT8 export and pack aligned, read-only native tensors.

Standard library only; training/PyTorch is not a ROM build dependency.
Never changes an export in the Metamon repository.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct

SCHEMA = "dfd5b2755d72052bbcd86cbd97a0c8dff63f6e3c51349e03ca947861bbf864d4"
EMBEDDINGS = {
    "species": (388, 24), "item": (800, 8), "ability": (78, 8),
    "status": (10, 4), "move": (356, 16), "element": (20, 4),
    "category": (5, 2), "action": (12, 8),
}
LAYERS = {
    "move_encoder.0": (32, 36, 48),
    "pokemon_encoder.0": (64, 196, 12),
    "pokemon_encoder.2": (64, 64, 12),
    "event_encoder.0": (32, 128, 4),
    "global_encoder.0": (64, 96, 1),
    "fusion.0": (160, 1088, 1), "fusion.2": (256, 160, 1),
    "gru.weight_ih_l0": (1152, 256, 1),
    "gru.weight_hh_l0": (1152, 384, 1), "actor": (9, 640, 1),
}


def expected_tensors():
    result = {}
    for name, (rows, cols) in EMBEDDINGS.items():
        result["embed." + name] = ("i1", (rows, cols))
        result["embed." + name + "/scale"] = ("f4", (rows,))
    for name, (rows, cols, _) in LAYERS.items():
        result[name] = ("i1", (rows, cols))
        result[name + "/scale"] = ("f4", (rows,))
        bias = name.replace("weight", "bias") if name.startswith("gru.") else name + "/bias"
        result[bias] = ("f4", (rows,))
    return result


def read_export(binary, manifest):
    data = Path(binary).read_bytes()
    man = json.loads(Path(manifest).read_text())
    for key, value in dict(format="MG3SINT8", version=1, preset="1m",
                           window=4, hidden=384, schema=SCHEMA,
                           parameters=1011355).items():
        if man.get(key) != value:
            raise ValueError(f"Unsupported {key}: {man.get(key)!r}; expected {value!r}")
    if len(data) < 20 or data[:8] != b"MG3SINT8":
        raise ValueError("Invalid binary header")
    version, size = struct.unpack_from("<IQ", data, 8)
    if version != 1 or size != len(data) - 20:
        raise ValueError("Invalid version or body length")
    expected = expected_tensors()
    records = {}
    pos = 20
    while pos < len(data):
        if pos + 2 > len(data): raise ValueError("Truncated record")
        nlen, = struct.unpack_from("<H", data, pos); pos += 2
        if pos + nlen + 3 > len(data): raise ValueError("Truncated name")
        name = data[pos:pos+nlen].decode("ascii"); pos += nlen
        code = data[pos:pos+2].decode("ascii"); pos += 2
        ndim = data[pos]; pos += 1
        if ndim not in (1, 2) or pos + ndim * 4 > len(data):
            raise ValueError("Invalid tensor dimensions")
        shape = struct.unpack_from("<" + "I" * ndim, data, pos); pos += ndim * 4
        if name in records or expected.get(name) != (code, shape):
            raise ValueError(f"Unexpected, duplicate, or wrong-shaped tensor: {name}")
        count = math.prod(shape)
        nbytes = count * (4 if code == "f4" else 1)
        payload = data[pos:pos+nbytes]; pos += nbytes
        if len(payload) != nbytes: raise ValueError(f"Truncated tensor: {name}")
        if code == "f4":
            values = struct.unpack("<" + "f" * count, payload)
            # Bound the supported numeric envelope for the soft-float runtime.
            # Arbitrarily huge finite scales can overflow intermediate layers.
            if not all(math.isfinite(x) and abs(x) <= 16 for x in values):
                raise ValueError(f"Non-finite or excessive tensor: {name}")
            if name.endswith("/scale") and not all(x > 0 for x in values):
                raise ValueError(f"Nonpositive scale: {name}")
        elif b"\x80" in payload:
            raise ValueError(f"Weight outside symmetric [-127,127] range: {name}")
        if man.get("tensors", {}).get(name) != dict(code=code, shape=list(shape), bytes=nbytes):
            raise ValueError(f"Manifest mismatch: {name}")
        records[name] = payload
    if records.keys() != expected.keys() or man["tensors"].keys() != expected.keys():
        raise ValueError("Missing or extra tensors")
    return data, man, records


def generate(binary, manifest, output, rom_map=None):
    data, man, tensors = read_export(binary, manifest)
    out = Path(output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    packed = bytearray()
    offsets = {}
    for name, payload in tensors.items():
        packed.extend(b"\0" * (-len(packed) % 4))
        offsets[name] = len(packed)
        packed.extend(payload)
    (out / "weights.bin").write_bytes(packed)
    # Relative incbin; compile from the generated output directory.
    (out / "weights.S").write_text('.section .rodata\n.balign 4\n.global gMmWeights\ngMmWeights:\n.incbin "weights.bin"\n')
    lines = ['#include "runtime.h"', 'extern const unsigned char gMmWeights[];',
             'const MmTensor gMmModel[MM_TENSOR_COUNT] = {']
    names = [("embed." + n, r, c, None) for n, (r, c) in EMBEDDINGS.items()]
    names += [(n, r, c, n.replace("weight", "bias") if n.startswith("gru.") else n + "/bias")
              for n, (r, c, _) in LAYERS.items()]
    for name, rows, cols, bias in names:
        bp = f"(const float *)(gMmWeights + {offsets[bias]})" if bias else "0"
        lines.append(f"    {{(const int8_t *)(gMmWeights + {offsets[name]}), "
                     f"(const float *)(gMmWeights + {offsets[name + '/scale']}), {bp}, {rows}, {cols}}},")
    lines.append('};\n')
    (out / "model.c").write_text("\n".join(lines))
    macs = {n: r*c*b for n, (r, c, b) in LAYERS.items()}
    report = dict(source_sha256=hashlib.sha256(data).hexdigest(), schema=man["schema"],
                  export_bytes=len(data), aligned_tensor_bytes=len(packed),
                  parameters=man["parameters"], macs_by_layer=macs,
                  macs_per_decision=sum(macs.values()),
                  note="MAC counts exclude embeddings, quantization, nonlinearities and observation encoding.")
    if rom_map:
        match = re.search(r"(0x[0-9a-fA-F]+)\s+__rom_end\s*=", Path(rom_map).read_text())
        if not match: raise ValueError("__rom_end not found in linker map")
        used = int(match[1], 16) - 0x08000000
        report["rom"] = dict(current_used_bytes=used, limit_bytes=32*1024*1024,
                             headroom_after_weights=32*1024*1024-used-len(packed))
        if report["rom"]["headroom_after_weights"] < 0:
            raise ValueError("Weights exceed ROM address space")
    (out / "import-report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("binary", type=Path)
    p.add_argument("manifest", type=Path)
    p.add_argument("--output", type=Path, default=Path(__file__).parent / "build")
    p.add_argument("--rom-map", type=Path)
    args = p.parse_args()
    print(json.dumps(generate(args.binary, args.manifest, args.output, args.rom_map), indent=2))
