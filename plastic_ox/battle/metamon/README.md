# Metamon trainer AI deployment prototype

Branch: `codex/metamon-trainer-ai`, based on
`7e1251b4706dd3011eba44bfbabe619329a9ae63`. Findings measured September 24, 2026.

This branch deploys the **causal recurrent distillation student** from
`metamon/rom_native_obs/distillation/export.py` natively on the GBA. It has a
validated importer, complete C forward pass, legal argmax selection, Python
reference comparison, standalone GBA timing ROMs, and a live battle adapter
(`src/metamon_trainer.c`). **Metamon controls every ordinary single-battle
trainer in the game** (any party size on either side; doubles, link, frontier,
recorded, safari, and partner battles keep the standard AI, as does the ROM
test runner via the `gTestRunnerEnabled` guard). Battles are validated in
mGBA by `smoke.py`, `play_battle.py`, and `gym_smoke.py` (Rustboro gym,
including a three-mon player party and a smaller-than-six trainer side).

The working assumption is native GBA inference for Gen 3 singles. There is no
external server or emulator process required by the eventual game runtime.

## Measured model and performance

Artifact inspected:

```
/home/eddie/metamon/models/kakuna-gen3-causal-s0-20260924/round-3/export/
```

This is an available snapshot, not an automatic selection of the eventual final
checkpoint. The exported actor has 1,011,355 parameters, a 384-element recurrent
state, a four-event window, and nine actions. It is a different architecture from
the older `distill_gen3.py` nonrecurrent student.

| Measurement | Result |
| --- | ---: |
| Original export | 1,040,166 bytes |
| Aligned ROM tensors | 1,038,928 bytes (0.991 MiB) |
| Integer MACs per decision | 1,235,584 |
| Baseline Thumb code in ROM | **3.664 s median**, 3.624–3.667 s |
| ARM dot product in IWRAM | **3.010 s median**, 2.971–3.014 s |
| Measured reduction | 0.654 s / **17.8%** |
| IWRAM code for that optimization | 68 bytes, plus linker interworking support |
| Observation buffer | 8,900 bytes |
| Reused inference scratch | 30,144 bytes |
| Float32 recurrent state | 1,536 bytes |
| Combined buffers | **40,580 bytes (39.63 KiB)** |

These are hardware-timer measurements in mGBA across eight consecutive real
held-out decisions, including input validation and recurrent updates. The code
uses devkitARM r65/GCC 14.2.0, `-O2`, Thumb, the game's `-mabi=apcs-gnu` with
assembler EABI-5 marking, weights in ROM, inputs/scratch in EWRAM, and WAITCNT
`0x40b4`, matching `src/main.c`. Timer cycles are divided by 16,777,216, using
the [GBA timing reference](https://mgba-emu.github.io/gbatek/).

**This is inference latency, not a measured full turn in the game or a physical
cartridge measurement.** It excludes observation construction, the initial
fixture copy, music, interrupts, DMA, menus, and animations. Expect roughly
3–4 seconds of computation per ordinary decision with this initial approach;
measure actual integrated latency before promising a player-visible wait.
Forced replacements and Baton Pass can require another decision in one turn.
Emulator fast-forward changes wall time; host Python inference time does not
predict original GBA speed.

The original default-ABI experiments gave 3.90/3.24 seconds. The table above
supersedes them with the game's compiler ABI. The benchmark uses its own cartridge
ID: reusing Emerald's ID causes mGBA's game-specific idle-loop optimization to
halt unrelated benchmark instructions at Emerald's known idle-loop address.

Verification: **117 decisions across four held-out battles**, 100% legal argmax
agreement with sequential CPU `QuantizedStudent`, maximum logit error
`9.54e-7`, maximum hidden error `3.58e-7`. Both GBA builds match the host's eight
fixture logits exactly; hidden error is at most `1.79e-7`. Six importer tests and
21 existing Metamon causal/export tests passed. Malformed tokens, nonfinite
inputs, empty action masks, opponent exact stats/PP, and illegal selected actions
are checked. These are numeric and boundary checks, not playing-strength or
live-ROM privacy certification. Raw measurements are in [results.json](results.json).

## Legal-information boundary

The trainer may know its own full party and public battle history. The live
adapter must construct a fresh, immutable observation from **its own party view
plus a separate public-event reducer**, from the trainer's point of view.
`runtime.c` deliberately accepts only tensors and state; it has no engine
globals, opponent party pointer, simulator object, or RNG access.

| Input | Permitted source |
| --- | --- |
| Own party, moves, PP, held items, abilities, exact HP/stats | Trainer's own party and current request state |
| Opponent identities | Species/level actually sent out, assigned slots in first-reveal order |
| Opponent moves | Publicly executed/revealed moves; called moves are not proof of moveset membership |
| Opponent item/ability | Public activation/reveal events; unknown remains unknown |
| Opponent HP | Visible HP-bar interval; retain the last observed interval for reserves |
| Status, boosts, weather, screens, hazards | Public effects and public elapsed time |
| Action mask | Actions available to the acting trainer at this decision boundary |
| Hidden state | Previous accepted decisions in this battle only |

Forbidden inputs include unrevealed reserves or their party order, actual
opponent party size without a public announcement, reserve HP/status, exact
opponent stats/HP/PP/IVs/EVs, unrevealed moves/items/abilities, chosen player
commands, RNG state, and pre-rolled sleep/confusion/duration outcomes. Internal
party indices may identify an already-revealed individual inside the adapter,
but must never become model features or reorder the public reveal slots.

Do not reuse `gAiPartyData`/`gBattleHistory` as a privacy boundary:

* `Ai_InitPartyStruct` in `src/battle_ai_main.c` records true party counts and
  fainted reserves even without `AI_FLAG_OMNISCIENT`. Flags can additionally
  populate unrevealed species, items, abilities and moves.
* `RecordKnownMove` in `src/battle_ai_record.c` stores a move in its private
  moveset slot. The model needs public revealed moves in its canonical order.
* AI predictions and assumptions are not public reveals. A generic switch helper
  can also inspect an unrevealed trapping ability. Distinguish information shown
  to the acting side by action availability from hidden mechanical state.

The runtime rejects opponent exact-stat fields and their known masks, opponent
exact PP and PP-known flags, and opponent complete-moveset/private-side flags.
These guards are defense in depth: they cannot tell whether a supplied move or
item was actually revealed. That guarantee belongs to the event adapter and its
tests, before any trainer is opted in.

Required privacy test: keep public history and own party fixed, independently
mutate hidden player reserves, item, ability, moves/order, PP, IVs/EVs, hidden
status timers, and current command. Assert identical observation bytes, recurrent
state transitions and logits. For HP, vary private values within the same visible
bar bucket. Separately reveal each fact and verify that only permitted fields
change. Test switch-out/back, called moves, Transform, item removal, failed moves,
and battle reset. The upstream Python tests cover parts of the reducer contract;
they do not replace these engine tests.

## Schema and action compatibility that must be resolved

1. **Party-size assumptions:** `distillation/memory.py:snapshot` hardcodes a
   known six-Pokémon opponent. Ordinary trainers and player parties vary, and
   player party size is not automatically public. Add public count bounds and
   known masks to training and deployment together, then export/retrain as needed.
   Alternatively first enable explicitly announced six-versus-six encounters.
   Do not fill this feature by scanning the hidden player party.
2. **HP visibility:** training widens public Showdown percentages to sixteenth
   intervals; the cartridge exposes bar pixels. Define one interval conversion
   from visible pixels and train/evaluate that convention. Merely reading exact
   HP and rounding to sixteenths can leak differences within a visible pixel.
3. **Action order:** upstream rollout sorts active moves and available switches
   by normalized names (`consistent_move_order`/`consistent_pokemon_order`). The
   four logits do not directly mean cartridge move slots 0–3. Build explicit
   model-index-to-native-move/party maps, including fewer than four moves,
   unavailable/fainted reserves, forced replacement, Struggle and Baton Pass.
   Retain masks and both mappings with the frozen observation.
4. **IDs:** tokens distinguish padding/known-none `0`, unknown `1`, and known
   species/move/item/ability ID plus one. Use the actual exported mapping tables;
   item IDs and type/status/category order cannot be inferred from generic Gen 3
   enums. Check Hidden Power and transformed identities explicitly.
5. **Unknowns:** the pilot leaves several duration/inference fields unknown.
   Preserve values and known masks exactly; do not populate them from convenient
   engine timers. Reject unsupported generations, forms, doubles, partners,
   facilities, link/recorded battles and gimmicks in the initial opt-in path.
6. **Sampling:** this prototype chooses legal argmax to avoid a softmax/RNG cost.
   Upstream battle evaluation samples the distribution. Evaluate this policy
   change before claiming the checkpoint's published win rate.
7. **Quantization:** the export uses per-row INT8 weights but dynamic activation
   scales, FP32 biases, sigmoid/tanh and FP32 hidden state. It is not an entirely
   integer runtime. Quantization scales are shared across slots AND batch/time
   dimensions in Python. Sequential batch-one parity is the deployment target;
   batched evaluation can yield different quantization than a cartridge.

The importer currently pins the exact `1m`, window-four schema hash. It rejects
wrong dimensions, missing/duplicate tensors, mismatched manifests, invalid
scales, nonfinite values, unsupported numeric ranges and truncated exports. The
upstream binary's tensor payloads are not generally aligned; the importer
re-packs them to four-byte alignment and generates native descriptors. Do not
cast pointers directly into `student-int8.bin` on ARM7.

The upstream schema hash includes the contents of `memory.py`, so even a source
edit can require explicit review/update. The manifest also does not record the
student's `memory=False` ablation switch; require production export provenance
with memory enabled. Model weights, fixtures and generated source stay in the
ignored `build/` directory. Pin a final artifact by SHA-256 before shipping.

## Build and integration impact

The normal ROM build succeeds on this branch. These prototype files are outside
`src/`, and **no model or trainer behavior is linked into `pokeemerald.gba` yet**.
Normal development/builds gain no Python/PyTorch dependency. A future explicit
model-import step can generate the binary/descriptors with Python's standard
library; the ROM build itself should consume a pinned generated artifact.

Current linked usage is ROM **26,331,028 / 33,554,432 bytes**, EWRAM
**226,524 / 262,144 bytes**, and IWRAM **28,372 / 32,768 bytes**. The game file is
padded to 32 MiB already; use `__rom_end` from the linker map to measure capacity.
After weights there are **6,184,476 bytes** left, before inference code, alignment,
mapping tables and future content. No cartridge format expansion is needed.

Only **35,620 bytes** of unallocated static EWRAM remain. The buffers above exceed
that, before the public-event memory. Allocate one workspace from the battle heap
with explicit failure handling, or reduce/reuse buffers; never place the model
weights in RAM. `gHeap` is already 115,968 bytes inside that EWRAM usage, and
`AllocateBattleResources` consumes it for battle/graphics resources. Total heap
capacity does not establish available contiguous space. Measure the largest
free block and peak use with animations, switches, party screens and teardown.
IWRAM also includes stack needs: do not treat its apparent 4,396-byte remainder
as a safe unrestricted allocation.

The initial runtime adds `expf`/`tanhf` from libm; the game currently links libc,
libnosys and libgcc but not libm. The production linker script must collect libm
text/rodata and the ARM/Thumb veneers, and use compatible compiler/assembler ABI
settings. The standalone benchmark verifies those settings, not a fully linked
game-runtime build. Fixed-point lookup tables would remove this dependency.

Recommended live wiring:

* Add an explicit trainer opt-in plus a default-off build option. Import/schema
  errors should fail the requested model build, rather than silently ship another
  model or a stub. Check ROM/RAM budgets in the linker map.
* Capture completed public events and commit a decision snapshot at the boundary
  currently used by `HandleTurnActionSelectionState`/`ComputeAiBattlerDecisions`.
  Do not run the existing scoring/switch-prediction path first for this trainer.
* Advance a cooperative inference job across frames. Cache the decision using
  battle ID, request/phase ID, and observation generation; a turn number alone
  cannot distinguish a forced switch from an ordinary action. Commit recurrent
  state exactly once per accepted decision, never per frame/controller callback.
* Dispatch both moves and voluntary switches through the cached action and map.
  Cover mandatory switch selection separately. Prevent `AI_TrySwitchOrUseItem`
  and later heuristic scoring from overriding the model's decision.
* Revalidate legality before dispatch. Handle changed requests, allocation
  failure, unsupported data and empty masks without advancing stale hidden state.
  A fallback for an opted-in legal-information trainer must itself use only the
  public view; calling the ordinary AI is not a demonstrated privacy guarantee.
* Free/reset state at every battle end, abort, whiteout, rematch and initialization.
  Keep it out of save data initially. Emulator savestates naturally capture RAM;
  recorded-battle replay and model-version compatibility need separate design.

This branch already forces Set mode in `ClearSetBScriptingStruct`, and
`IsAllowedToUseBag` disallows player bag use in trainer battles. The ordinary
opponent `ShouldUseItem` path still exists. The model has no bag-item action;
the specialized controller must explicitly bypass that path. Broader Showdown
mechanics parity, lower-level teams, duplicate species and roster distributions
still need evaluation; Gen 3 config flags alone do not prove distribution parity.

## Improving speed

The measured ARM/IWRAM dot loop is the first small optimization. Further work,
in practical order:

1. Schedule small row blocks across frames with a measured cycle budget. Aim to
   keep menu, audio and animation service responsive. Starting from a frozen
   public snapshot while the player chooses can hide some computation. It does
   not reduce total inference cost, and must not read the player's choice.
2. Replace soft-float scaling and sigmoid/tanh with calibrated fixed-point
   multipliers and lookup tables. Preserve GRU gate order/reset placement, bound
   accumulators and saturation, and compare full recurrent trajectories. Optional
   INT16 hidden state alone saves only 768 bytes and does not remove float work.
3. Optimize the dot loop with ARM loads/unrolling and measured activation
   placement. ARM7 has no modern vector-dot accelerator; do not assume a desktop
   INT8 library's throughput or move the entire 1 MiB model into scarce RAM.
4. Evaluate the existing smaller student presets (500k/250k/100k) with the same
   gameplay tests. A smaller GRU is promising: its two matrices account for
   737,280 MACs, about 60% of this model's work. This runtime would need generated
   dimensions/support for those exports; their speed/strength is not measured here.
5. Consider skipping/caching masked slots only after accounting for the export's
   shared activation scale: even a slot whose output is later masked participates
   in the current quantization maximum. A naive skip changes model outputs.

## Reproduce

From the repository root, using the current local artifact:

```sh
python3 -m unittest discover -s plastic_ox/battle/metamon -p 'test_*.py'

/home/eddie/repos/metamon/.venv/bin/python plastic_ox/battle/metamon/verify.py \
  --metamon /home/eddie/repos/metamon \
  --export /home/eddie/metamon/models/kakuna-gen3-causal-s0-20260924/round-3/export \
  --shard /home/eddie/metamon/models/kakuna-gen3-causal-s0-20260924/data/test/shard-00000.pt

python3 plastic_ox/battle/metamon/import_model.py \
  /home/eddie/metamon/models/kakuna-gen3-causal-s0-20260924/round-3/export/student-int8.bin \
  /home/eddie/metamon/models/kakuna-gen3-causal-s0-20260924/round-3/export/export-manifest.json \
  --rom-map pokeemerald.map

LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/battle/metamon/benchmark.py

env PATH=/home/eddie/devkitpro/opt/devkitpro/devkitARM/bin:$PATH \
  make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
```

The benchmark writes separate `build/thumb-rom.gba` and `build/arm-iwram.gba`;
it reads the game header but does not overwrite the game ROM or save. Reference
verification requires trusted Metamon checkpoint shards and that repository's
environment; ordinary import, importer tests and ROM builds do not require Torch.
