# Metamon policy on Plastic Ox: deployment, capacity, and options

For the model development team. Written from the ROM-deployment side.
Branch `codex/metamon-trainer-ai`, deployment commit `5b21ca882b`
("Deploy metamon 1M policy to all single-battle trainers"), 2026-09-25.
All numbers are measured on hardware-accurate mGBA (cycle-accurate) unless
marked *estimated*.

## 1. What is deployed today

- The **causal recurrent distillation student** from
  `metamon/rom_native_obs/distillation/export.py`
  (snapshot: `~/metamon/models/kakuna-gen3-causal-s0-20260924/round-3/export/`)
  runs natively on the GBA, in every ordinary single-battle trainer battle
  (gym leaders, story bosses, route trainers). Doubles, link, frontier,
  recorded, safari, and partner battles keep the standard expansion AI.
- Inference is cooperative: the decision is spread across frames
  (at most 128 scanlines + one tile per callback), so the game keeps
  rendering and playing sound while thinking. There is no server or
  emulator dependency.
- The policy is the only decision maker for the trainers it controls
  (`OpponentHandleChooseAction/ChooseMove/ChoosePokemon` short-circuit the
  standard AI, including item use - see section 9).
- Live validation: `smoke.py` (Lance fixture), `gym_smoke.py` (Rustboro
  gym leader, story Roxanne, her existing team, 3-mon player party):
  11 decisions, commits consistent, `gMetamonFault == 0`, battle completes.

## 2. Current model (exact shapes)

Export: **1,011,355 parameters**, aligned ROM tensor blob **1,038,928 B**
(int8 weights + per-tensor float32 scale/bias vectors, ~1.03 B/param).
Hidden size 384, action space 9, event window 4.

Dense layers (these cost MACs every decision):

| Layer | Shape (in→out) | Params | MACs/decision |
|---|---|---:|---:|
| move_encoder.0 | 36→32 | 1,152 | 55,296 (48 moves) |
| pokemon_encoder.0 | 196→64 | 12,544 | 150,528 (12 mons) |
| pokemon_encoder.2 | 64→64 | 4,096 | 49,152 |
| event_encoder.0 | 128→32 | 4,096 | 16,384 (4 events) |
| global_encoder.0 | 96→64 | 6,144 | 6,144 |
| fusion.0 | 1088→160 | 174,080 | 174,080 |
| fusion.2 | 160→256 | 40,960 | 40,960 |
| gru.weight_ih_l0 | 256→1152 | 294,912 | 294,912 |
| gru.weight_hh_l0 | 384→1152 | 442,368 | 442,368 |
| actor | 640→9 | 5,760 | 5,760 |
| **Total** | | **986,112** | **1,235,584** |

Embedding tables (lookup only, no MACs): species 388x24, item 800x8,
ability 78x8, status 10x4, move 356x16, element 20x4, category 5x2,
action 12x8 = 22,258 params.

Scaling law: widen all dims by factor s and params and MACs both grow
~s^2. Embeddings are 2% of params, so **params ≈ MACs ≈ s^2** for any
proportional resize of this family.

## 3. Measured performance

| Configuration | Median | MAC/s | cycles/MAC |
|---|---:|---:|---:|
| Thumb code in ROM | 3.664 s/decision | 337,223 | 49.8 |
| **ARM dot in IWRAM (shipped)** | **3.010 s/decision** | **410,493** | **40.9** |

- ARM7TDMI at 16.777216 MHz, WAITCNT `0x40b4`, devkitARM r65 / GCC 14.2,
  `-O2`. The shipped kernel (`dot.c`, ARM state, placed in IWRAM) streams
  weights from ROM as 32-bit words (4 int8 MACs per iteration) and reads
  the quantized operand from EWRAM.
- Integrated (in-battle) number, not kernel-only: the Rustboro gym smoke
  played 11 decisions in 2,499 inference frames ≈ **3.8 s/decision**
  including observation build, quantization, and glue.
- Numeric parity: 117 decisions across 4 held-out battles, 100% legal
  argmax agreement vs sequential `QuantizedStudent`, max logit error
  9.5e-7, max hidden error 3.6e-7.

## 4. The four hardware walls

| Resource | Budget | Current use | Headroom |
|---|---|---|---|
| ROM (cart) | **32 MiB, hard ceiling** (GBA maps only 32 MiB) | 26.13 MiB game | **5.87 MiB for weights** |
| EWRAM | 256 KiB total; dynamic heap `gHeap` = 113 KiB (0x1C500) | arena 18,748 B (obs + workspace + hidden + logits + job + 12-mon public state), validated by heap trace | moderate growth (KiB-scale) revalidated via `collect_heap.py`; anything ~4x needs tiling (see 6) |
| IWRAM | 32 KiB, shared with game state | 68-B dot kernel | room for a small operand staging buffer (KiB scale) |
| CPU | 16.78 MHz, no SIMD, no cache | 40.9 cycles/MAC measured | kernel floor ~10-15 cycles/MAC (2 loads + MLA + add), so **2-4x total headroom, not 10x** |

The single biggest measured inefficiency: the quantized operand streams
from EWRAM (2 wait states, 16-bit bus). Staging it in IWRAM per dot row
is the first optimization to try, then unrolled ARM and DMA weight
prefetch.

## 5. Size ceiling: how big a model fits

ROM is the binding constraint. 5.87 MiB of weights at current packing:

| Quantization | Params in 5.87 MiB | vs today | MACs/decision (proportional) | s/decision today | s/decision, optimized kernel |
|---|---:|---:|---:|---:|---:|
| int8 (today, ~1.03 B/param) | **~6.0M** | 5.9x | ~7.3M | 18 | **4.5-9** |
| int4 (~0.55 B/param) *e* | ~11.2M | 11x | ~13.7M | 33 | 8.5-17 |
| ternary ±1 (~0.35 B/param) *e* | ~17.6M | 17x | ~21.5M | 30-50 (add/sub kernel) | **9-18** |

*Optimized kernel = 2-4x throughput (820k-1.6M MAC/s), the realistic
engineering ceiling from section 4. Ternary needs a new dot kernel
(add/sub instead of MLA) and retraining/export support - see section 7.*

Absolute ceiling if game content is stripped/compressed to give weights
~12 MiB: ~12M int8 / ~23M int4 / ~36M ternary params, at 9-27 s/decision
(optimized kernels). Past that there is no more address space: **32 MiB
is the wall that no amount of waiting moves.**

## 6. EWRAM: the second wall for big exports

The shipped workspace is monolithic: 12,480 B (`MmWorkspace`) covering
all 12 mon slots + fusion scratch in one buffer. Proportional 2.4x width
scaling makes that ~75 KiB, which does not fit the 113 KiB battle heap
alongside battle allocations. Any export wider than ~1.5x today requires
**per-mon tiled inference** (process one mon slot at a time, reuse a
single-slot scratch, accept some re-streaming). That is ROM-side
engineering we own; it does not constrain the export itself, but plan for
it before a >2.5M-param student.

## 7. Drop-in contract for the next export

What the ROM runtime requires today (all enforced by asserts or the
importer):

- Per-tensor **int8 symmetric quantization** with float32 scale and bias
  vectors; row-major, sequential, 4-byte-aligned rows ("all exported row
  widths and quantized offsets are multiples of four").
- Constants that regenerate with the export: `MM_HIDDEN`, `MM_ACTIONS`
  (9), `MM_WINDOW` (4); observation fixture ABI is asserted
  (`sizeof(MmObservation) == 3212`, `sizeof(MmWorkspace) == 12480`).
- Vocab windows the adapter assumes (the game is **Gen 3 only** by
  design, so these hold): species ≤ 386, moves ≤ 354, items < 799,
  abilities ≤ 76. The adapter clamps or ignores anything beyond.
- Privacy boundary is fixed: the model sees only public battle state
  (own party view + public-event reducer, HP as displayed 48-pixel bar
  intervals, reveal-order opponent slots). No exact opponent HP/stats,
  no unrevealed reserves, no RNG. Do not add features that require more.
- One decision per action request, recurrent state carried across
  decisions within a battle, hidden reset at battle start. T=1 stepping
  (a longer in-battle history window is free in ROM but costs event
  encoder MACs linearly).

Tooling that must be regenerated together with a new shape:
`import_model.py` (alignment + `public_data.inc`/`weights.bin`),
`verify.py` (host parity), `gMetamonTestLayout` ABI table in
`src/metamon_trainer.c`, smoke/heap-trace fixtures.

## 8. Recommendations (deployment-side view)

1. **Next student: ~2.4x width (≈6M params).** It fits today's ROM
   headroom exactly, with zero new weight-side engineering. Expected
   ~18 s/decision today, ~4.5-9 s after our kernel work.
2. Anything in the 2.5M-6M range drops in after the workspace tiling
   rework (section 6); anything above ~6M needs sub-byte quantization
   (int4/ternary) and a new kernel on our side.
3. We will do, in order: IWRAM operand staging, unrolled ARM dot, DMA
   weight prefetch, per-mon workspace tiling. Happy to coordinate on a
   ternary export experiment if the distillation quality holds.

## 9. Open model-side questions

- **Doubles**: the 9-action space and singles observation schema are
  baked into the adapter. A doubles policy needs a wider action space
  (target selection) and a doubles-trained export; the ROM side excludes
  doubles until then.
- **Item use**: 9 actions = 4 moves + 5 switches, so metamon-controlled
  trainers never use held battle items. If item play matters, the action
  space must grow and the adapter must learn item-in-bag state.
- **Schema ceiling**: past ~6M params the student is likely bounded by
  what the observation exposes (12 public mons, 4-event window, Gen-3
  vocab, displayed HP intervals). If the teacher is much stronger, it may
  be carrying information the schema cannot express - worth checking
  before sizing up the student.
- Emulator note: on mGBA, fast-forward changes wall time only; the
  numbers above are real-GBA time.

*Estimated values are marked `*e`; everything else is measured or
asserted in-repo. Raw measurements: `results.json`; live checks:
`smoke.py`, `gym_smoke.py`, `play_battle.py`, `verify.py`,
`collect_heap.py`.*
