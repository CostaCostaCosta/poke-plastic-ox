#!/usr/bin/env python3
"""Compare native inference to sequential B=1,T=1 exported Python inference.

Run with Metamon's Python environment. Also writes recurrent benchmark fixtures.
"""
import argparse
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys

from import_model import generate


class Observation(C.Structure):
    _fields_ = [("mon_cat", C.c_int16 * 84), ("mon_num", C.c_float * 288),
                ("mon_flags", C.c_uint32 * 36), ("move_cat", C.c_int16 * 144),
                ("move_num", C.c_float * 192), ("move_flags", C.c_uint16 * 48),
                ("move_valid", C.c_uint8 * 12), ("event_cat", C.c_int16 * 24),
                ("event_num", C.c_float * 96), ("event_flags", C.c_uint8 * 4),
                ("global_num", C.c_float * 32), ("global_flags", C.c_uint32 * 2),
                ("legal", C.c_uint8 * 9)]


class Workspace(C.Structure):
    _fields_ = [("a", C.c_float * 2496), ("quant", C.c_int8 * 2496)]


def observation(episode, step):
    obs = Observation()
    for key in ("mon_cat", "move_cat", "event_cat"):
        getattr(obs, key)[:] = episode[key][step].flatten().tolist()
    for prefix, rows, numeric, width, words, bits in (
        ("mon", 12, 24, 96, 3, 32), ("move", 48, 4, 14, 1, 16),
        ("event", 4, 24, 32, 1, 8), ("global", 1, 32, 96, 2, 32)):
        values = episode[prefix+"_num"][step].reshape(rows, width)
        nums, flags = getattr(obs, prefix+"_num"), getattr(obs, prefix+"_flags")
        nums[:] = values[:, :numeric].flatten().tolist()
        for i in range(rows):
            for j in range(numeric, width):
                value = values[i, j]
                assert value in (0, 1), (prefix, i, j, value)
                if value: flags[i*words+(j-numeric)//bits] |= 1 << ((j-numeric)%bits)
    for i, row in enumerate(episode["move_valid"][step]):
        for j, value in enumerate(row):
            assert value in (0, 1)
            obs.move_valid[i] |= int(value) << j
    obs.legal[:] = [int(x) for x in episode["legal_action_mask"][step]]
    return obs


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--metamon", type=Path, required=True)
    p.add_argument("--export", type=Path, required=True)
    p.add_argument("--shard", type=Path, required=True)
    p.add_argument("--battles", type=int, default=4)
    p.add_argument("--output", type=Path, default=Path(__file__).parent / "build")
    a = p.parse_args()
    src = Path(__file__).resolve().parent
    out = a.output.resolve()
    generate(a.export / "student-int8.bin", a.export / "export-manifest.json", out)
    subprocess.run(["cc", "-O2", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    "-ffp-contract=off", "-fPIC", "-shared", "-I" + str(src),
                    str(src / "runtime.c"), str(src / "dot.c"), "model.c", "weights.S",
                    "-Wl,-z,noexecstack", "-lm", "-o", "runtime.so"], cwd=out, check=True)
    sys.path.insert(0, str(a.metamon.resolve()))
    import numpy as np
    import torch
    from metamon.rom_native_obs.distillation.export import QuantizedStudent
    from metamon.rom_native_obs.distillation.model import INPUT_KEYS
    torch.set_num_threads(1)
    ref = QuantizedStudent(a.export / "student-int8.bin")
    lib = C.CDLL(str(out / "runtime.so"))
    fp = C.POINTER(C.c_float)
    lib.MmInfer.argtypes = [C.POINTER(Observation), fp, fp, C.POINTER(Workspace)]
    lib.MmInfer.restype = C.c_int
    lib.MmChooseLegal.argtypes = [fp, C.POINTER(C.c_uint8)]
    lib.MmChooseLegal.restype = C.c_int
    scratch = Workspace()
    logits = (C.c_float * 9)()
    episodes = torch.load(a.shard, map_location="cpu", weights_only=False)[:a.battles]
    errors, h_errors, kls, agree, fixtures, expected = [], [], [], 0, [], []
    with torch.no_grad():
        for episode in episodes:
            hidden = (C.c_float * 384)()
            rh = None
            for step in range(len(episode["legal_action_mask"])):
                obs = observation(episode, step)
                inputs = {k: torch.as_tensor(episode[k][step])[None, None] for k in INPUT_KEYS}
                rlogits, rh = ref(inputs, rh)
                assert lib.MmInfer(C.byref(obs), hidden, logits, C.byref(scratch)) == 1
                err = float(np.max(np.abs(np.array(logits) - rlogits.numpy().ravel())))
                herr = float(np.max(np.abs(np.array(hidden) - rh.numpy().ravel())))
                errors.append(err); h_errors.append(herr)
                legal = episode["legal_action_mask"][step].astype(bool)
                rp = torch.softmax(rlogits.flatten()[legal], 0).numpy().astype(float)
                cp = np.array(logits, dtype=float)[legal]
                cp = np.exp(cp-cp.max()); cp /= cp.sum()
                kls.append(float(np.sum(rp*np.log(rp/cp))))
                best = int(np.where(legal, rlogits.numpy().ravel(), -np.inf).argmax())
                chosen = lib.MmChooseLegal(logits, obs.legal)
                assert legal[chosen]
                agree += chosen == best
                if episode is episodes[0] and step < 8:
                    fixtures.append(bytes(obs))
                    expected.append(dict(logits=list(logits), hidden=list(hidden), action=chosen))
    # Numeric implementations can cross a dynamic-quantization rounding boundary;
    # report actual drift and action agreement, with explicit prototype gates.
    report = dict(battles=len(episodes), decisions=len(errors),
                  max_logit_error=max(errors), max_hidden_error=max(h_errors),
                  max_policy_kl=max(kls), mean_policy_kl=sum(kls)/len(kls),
                  legal_argmax_agreement=agree / len(errors),
                  observation_bytes=C.sizeof(Observation), workspace_bytes=C.sizeof(Workspace),
                  hidden_bytes=384*4, fixtures=len(fixtures),
                  reference="CPU QuantizedStudent, fp32 hidden, sequential B=1 T=1")
    assert max(errors) < 0.05 and max(h_errors) < 0.02, report
    assert agree / len(errors) >= 0.99, report
    # Rejection must not advance recurrent state or leave a usable action.
    before = bytes(hidden)
    saved = obs.mon_cat[0]; obs.mon_cat[0] = 388
    assert lib.MmInfer(C.byref(obs), hidden, logits, C.byref(scratch)) == 0
    assert bytes(hidden) == before
    obs.mon_cat[0] = saved
    obs.mon_num[6 * 24 + 3] = 0.25  # Forbidden exact opponent Attack stat.
    assert lib.MmInfer(C.byref(obs), hidden, logits, C.byref(scratch)) == 0
    obs.mon_num[6 * 24 + 3] = 0
    obs.move_flags[6 * 4] = 1  # Forbidden opponent PP-known mask.
    assert lib.MmInfer(C.byref(obs), hidden, logits, C.byref(scratch)) == 0
    obs.move_flags[6 * 4] = 0
    obs.global_num[0] = float("nan")
    assert lib.MmInfer(C.byref(obs), hidden, logits, C.byref(scratch)) == 0
    obs.global_num[0] = 0
    obs.legal[:] = [0]*9
    obs.global_flags[1] &= (1 << 23) - 1
    assert lib.MmInfer(C.byref(obs), hidden, logits, C.byref(scratch)) == 0
    assert bytes(hidden) == before
    assert lib.MmChooseLegal(logits, obs.legal) == -1
    obs.legal[7] = 1
    assert lib.MmChooseLegal(logits, obs.legal) == 7
    logits[0] = float("nan")
    assert lib.MmChooseLegal(logits, obs.legal) == -1
    report["invalid_input_and_action_mask_checks"] = "passed"
    (out / "fixtures.bin").write_bytes(b"".join(fixtures))
    (out / "fixtures.json").write_text(json.dumps(expected) + "\n")
    (out / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
