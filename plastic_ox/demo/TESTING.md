# Headless overworld testing

The playable ROM boots through the title screen so players can continue saved
games. Headless tests must not wait for the old direct-to-bedroom boot or drive
the title UI. Use the deterministic fixtures in `walklib.py` and
`test_story.py` instead.

## Choose the fixture that matches the test

- Use `boot_test_game(g)` for a raw `GBA` test that needs a fresh game in the
  overworld. It selects the normal `CB2_NewGame` callback after title
  initialization and does not depend on emulator save data.
- Use `StoryGame(build, spawn=(map_name, x, y))` when testing a map, town,
  route leg, script, screenshot, or isolated transition. This is the preferred
  setup for tests whose subject is not the opening journey.
- Use `boot_to_bedroom(g)` only when the test intentionally verifies the
  bedroom, Mom, Pallet opening, or a continuous fresh-game journey beginning
  there. It is a compatibility wrapper around `boot_test_game(g)`.

Example of an isolated map test:

```python
from test_story import StoryGame

game = StoryGame(spawn=("GoldenrodCity_hns", 28, 37))
assert game.describe().startswith("(77,11)")
```

`spawn` is `(map directory name, x, y)`. `StoryGame` resolves the map group and
number from `data/maps/map_groups.json`, initializes a fresh deterministic
player, then uses the engine's field-script warp command. Tests may establish
flags, vars, party state, or story state after construction.

For continuous region coverage, add a named entry to `LEGS` in
`test_region_walk.py`. Each leg's map and coordinates are now passed to the
same spawn fixture automatically. All subsequent transitions in that test
must still use ordinary D-pad movement; the setup warp does not count as
transition coverage.

## Running tests

Use the repository's mGBA Python environment:

```sh
export LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_story.py starters
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_region_walk.py postgame
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/walk_leg1.py
```

Interpret failures after setup carefully. “Test new-game fixture never reached
the overworld” is a boot-fixture failure. Once a test prints or reports its
starting map, later path, collision, warp, or seam failures belong to the
gameplay under test and should not be described as bedroom boot failures.
