---
name: plastic-ox-emulator-test
description: Run or write mGBA emulator harnesses (plastic_ox/demo/test_*.py) that verify Plastic Ox gameplay in the real ROM - warps, seams, NPC dialogue, gates, trainers, story flags. Use whenever a change affects runtime behavior and needs in-emulator evidence, or when a harness fails and you must tell a fixture failure from a gameplay regression.
---

# Plastic Ox emulator tests

Static checks can't show that a warp lands correctly or that a gate opens.
Any change to gameplay, warps, scripts or gates needs a harness run.

## Run

```sh
make pox-build                                   # tests read ./pokeemerald.gba and .map
make pox-check-emu TESTS="test_goldenrod"        # one or more harness names
plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_story.py gates   # direct, with args
```

`pox-mgba-python` sets the mGBA library path from `$POX_MGBA_VENV`. It exits 77
(skip) when mGBA isn't installed. If that happens, say in your report that you
skipped emulator verification. Don't claim the change is verified. Run one
emulator at a time per checkout.

Pick existing harnesses by area: `ls plastic_ox/demo/test_*.py` (e.g.
`test_goldenrod`, `test_league`, `test_region_v7 --only <leg>`,
`test_region_walk <leg>`, `test_camera_seam`, `test_cave_connections`).
`test_story.py` takes a suite name: `starters`, `ivs`, `gifts`, `gates`, `travel`,
`battles`, `callbacks` or `all`.

## Write a harness

Read `plastic_ox/demo/TESTING.md` first. Then create `plastic_ox/demo/test_<area>.py`:

```python
#!/usr/bin/env python3
"""What this proves, in one paragraph."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_story import StoryGame, ROOT          # fresh deterministic save + field warp
from walklib import K                           # key constants
from walk_leg1 import navigate, enter_warp      # A* walking and door entry

g = StoryGame(spawn=("GoldenrodCity_hns", 28, 37))   # (map dir name, x, y)
g.flag("FLAG_POX_TRIGGERS_ENABLED", 1)                # set state after construction
navigate(g, (33, 10))                                 # walk; never warp to the thing under test
assert g.describe().startswith(...), g.describe()
print("ok  north gate")
```

Reusable helpers, by where they already live:

- `walklib.py`: `GBA`, `K`, `DIRKEY`, `boot_test_game`, `boot_to_bedroom` (only for opening-sequence tests).
- `test_story.py`: `StoryGame` with `flag()`, `const()`, `warp()`, `write()`, `party_species()`, `symbol_address()`.
- `walk_leg1.py`: `navigate`, `find_path_elev`, `enter_warp`, `set_flag`.
- `walk_demo.py`: `cross_connection`. `test_region_walk.py`: `navigate`, `cross`.
- `test_sudowoodo_v1.py`: `talk`, `settle`, `settle_overworld`, `in_battle`, `fight`, `give_item`, `bag`, `throw_ball`.
- `pox_fixtures.py`: `Game`, `game`, `finish_trainer`, `save_reload`. `test_camera_seam.py`: `check_view`.
- `test_qol.py`: `opcode`, `begin_code`. `test_training_kit.py`: `run_code`.

Conventions:

- Use the spawn warp only for setup. Every transition under test must be
  walked with the D-pad, in both directions, and through all lanes of a wide exit.
- Print one `ok  <claim>` line per assertion group and exit non-zero on failure.
- Static assertions (party legality, JSON shape) can go in the same file and
  run before the emulator part, as `test_weather_institute.py` does.
- Screenshots go to `plastic_ox/demo/shots/`, which is gitignored. Never commit
  logs or playtest JSON.

## Reading failures

"Test new-game fixture never reached the overworld" is a boot-fixture problem:
check that the ROM is fresh and matches its `.map`. Once the harness has printed
its starting map, any later path, collision, warp or seam failure is a gameplay
regression in the code under test.
