# Hidden Power training, serving and display

The production adapter now supplies the trainer's own Hidden Power type and
Gen 3 damage category for active and reserve Pokémon. It reads only its own
IVs. Opponent Hidden Power stays unknown after the move is seen. The new inputs
use existing type/category embeddings and known masks; power remains unknown
in the policy, matching the Python causal encoder.

The importer accepts the original schema and the new explicitly pinned v2
schema, retaining the export's original schema in its report. Production
weights were not replaced by the small validation fine tune.

The battle type label and summary move icons display the actual Hidden Power
type. Battle descriptions and summary details show IV-based power and the
matching physical/special icon. `GetHiddenPowerBasePower` is shared with actual
damage calculation. Summary displays resolve each selected party member's own
IVs, including reserves and move-learning previews.

Rebuilt ordinary ROM: `pokeemerald.gba`.

## Verification

```sh
make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
python3 -m unittest discover -s plastic_ox/battle/metamon -p test_import_model.py
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/battle/metamon/hidden_power.py
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/battle/metamon/privacy.py
```

Completed: 7 importer tests; all 16 own Hidden Power types/categories in native
inference; all 64 power bit patterns through the battle description; 10 privacy
cases, including hidden player IV changes. Summary Fighting/Ice screens and
battle Ice/Fighting screens were inspected in mGBA. All use disposable emulator
state and preserve player save files.

Screenshots and native type results: `build/hidden-power/`.
Native reference comparisons: `build/hidden-power-verify/verification.json`
(production weights with corrected inputs) and
`build/hidden-power-v2-verify/verification.json` (small v2 fine tune).
Both achieved 1,530/1,531 legal argmax agreement across 32 held-out battles.

The Metamon changes, reconstruction commands, training results and production
promotion requirements are documented in
`/home/eddie/repos/metamon/docs/hidden_power_v2_20261021.md`.
