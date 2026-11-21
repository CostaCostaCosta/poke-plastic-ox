# Gabby & Ty silph-002 1M student deployment (2026-11-17)

The production ROM now links the Gabby & Ty `r2b-1m-42m` student at update
30000. It has the same 1,011,355-parameter 1M architecture and window-four
schema as before. The student was distilled from the frozen silph-002 policy:
offline training, then DAgger rounds 1 and 2 and a 40k continuation. It replaces
the T=2 round-4 Kakuna actor from 2026-10-07. Legal argmax, an FP32 recurrent
state, lookup-table nonlinearities and the public observation adapter are
unchanged.

| Item | Value |
| --- | --- |
| Export | `gabby-and-ty/artifacts/distill/exports/r2b-1m-42m-0030000/student-int8.bin` |
| Export SHA-256 | `77b2f8e712c7fbca7fef6fa4a3f8abe90fc2901191a0077af08a3b5ad2494d61` |
| Checkpoint SHA-256 | `412a8e2ef300a54c62187b53d900b948b8449d8212ee9844e82adc4e0b0ddd05` |
| Schema | `7c511a49…d4ea` (v2 Hidden Power; the previous weights used the legacy schema) |
| `model/weights.bin` SHA-256 | `5ab872ab191224a2c2239a7bb68007c3cc8585da55c2d3dd680daacf1f58e2da` |
| ROM SHA-256 (source `aab6374116` + this change) | `bac76ed9c6a630823e85694861547381a6b9b0523d0900eef27a679a320f314f` |

## Strength (Showdown simulator only)

These are Gabby & Ty INT8-vs-INT8 panels of 512 games on fresh seeds, with 95%
intervals. The new student scored:

- 61.3% (55.7–67.0) against the previously deployed Kakuna student;
- 35.7% (31.7–39.7) against the silph-002 teacher. The previously deployed
  student scored 21.6% on the same panel.

No strength measurement has been made on the ROM's own battle engine.

## Verification

- **Native vs reference:** `verify.py` compared host-built native C against
  metamon's `QuantizedStudent` (sequential B=1). It used 32 held-out Gabby & Ty
  validation episodes (seed 20261117): 1,690 decisions and 1,688 legal argmax
  agreements (99.88%). Maximum logit error was 0.0339 and maximum hidden error
  0.0095, both within the 0.05/0.02 gates. The invalid-input and action-mask
  checks passed.
- **Importer:** all 14 importer/heap tests passed. The linked `gMmWeights` payload
  in `pokeemerald.gba` matches `model/weights.bin` byte for byte.
- **Kernel timing in mGBA (eight fixtures):** median 2.717 s with Thumb from ROM
  and 2.370 s with ARM/IWRAM. Host fixture logits and hidden state matched
  exactly. Both are unchanged from the previous model, as expected for the same
  architecture.
- **Integration in mGBA:**
  - five-turn smoke: about 227 frames per decision;
  - 10/10 privacy cases;
  - 16/16 own Hidden Power types;
  - two complete trainer battles with audio, recurrent reset and no faults:
    32 and 30 decisions at about 228 frames, roughly 3.8 s per decision;
  - Rustboro gym: 27 decisions, fault 0, badge flag set.
- ROM usage is 28,254,952 of 33,554,432 bytes.

`smoke.py`, `gym_smoke.py` and `collect_heap.py` now boot with
`walklib.boot_test_game`. The older `test_single_player.boot_new_game` does not
name the player. Since the 2026-11-11 harness change, `StoryGame` asserts the
player name, so every Metamon mGBA script failed before reaching a battle.

The previous weights, ROM, ELF and map, plus the verifier output, timing,
privacy and battle logs, are in
`gabby-and-ty/artifacts/distill/rom-deploy-r2b-1m-20261117/`.
