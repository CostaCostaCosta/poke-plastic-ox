# Agent guide: Pokémon Plastic Ox

This checkout is **Plastic Ox**, a ROM hack built on pokeemerald-expansion 1.16.3.
It merges Kanto (FRLG maps), Johto (Heart & Soul / "HNS" maps) and Hoenn into a
single region. Almost all of the 32k tracked files are the upstream engine; the
root `README.md`, `INSTALL.md` and `docs/` describe upstream, not Plastic Ox.
Start here instead.

## Where Plastic Ox lives

| What | Where |
|---|---|
| Docs index and source-of-truth order | `plastic_ox/README.md` |
| Story bible / map design (the law) | `plastic_ox/plastic_ox_story_v7.md`, `plastic_ox/plastic_ox_map_v7.md` |
| Per-location notes (work tickets) | `plastic_ox/story/locations/<slug>.md` (+ `plastic_ox/story/README.md`) |
| Story/region generators | `plastic_ox/alpha/` (`build_story.py`, `region_v7.py`, `league.py`, per-area modules) |
| Live audits and test helpers | `plastic_ox/tools/` |
| mGBA emulator harnesses | `plastic_ox/demo/` (`test_*.py`, `walklib.py`, `test_story.py`) |
| Map data | `data/maps/<Map>/map.json`, `data/maps/<Map>/scripts.inc`, `data/layouts/` |
| Shared Plastic Ox scripts | `data/scripts/plastic_ox_*.inc` |
| Flags | `include/constants/plastic_ox_flags.h`, ids reserved in `plastic_ox/alpha/story_flags.json` |
| Trainers | `src/data/trainers.party` |
| Engine code | `src/plastic_ox_*.c`, `src/metamon_*.c` (battle AI, see `plastic_ox/battle/metamon/`) |
| Agent skills | `.agents/skills/` (also visible to Claude Code as `.claude/skills/`) |
| History, not instructions | `plastic_ox/archive/`: do not run or follow anything there |

## Commands

```sh
make pox-help             # list the targets below
make pox-build            # build pokeemerald.gba (sources plastic_ox/bin/pox-env.sh; plain `make` also finds ~/devkitpro)
make pox-check-static     # fast gate, no ROM/emulator: notes, regression suites, audits, generator drift
make pox-check-emu TESTS="test_goldenrod test_story"   # mGBA harnesses; quote args: TESTS='"test_story gates"'
make pox-check            # all of it
make pox-generated        # which generator-owned files have drifted
```

Toolchain paths (`DEVKITARM`, `POX_MGBA_VENV`, `POX_HNS_DONOR`, `POX_HOSTLIBS`)
come from `plastic_ox/bin/pox-env.sh`. Override them in your environment or in
`plastic_ox/bin/pox-env.local.sh`, which is gitignored. Never hard-code
`/home/<user>/...` paths in committed files. Run emulator scripts through
`plastic_ox/bin/pox-mgba-python <script>`. It exits 77 when mGBA is not installed.

Builds share `build/` and the root ROM, so don't run two builds or emulator
runs in parallel in one checkout. Use a separate worktree for each agent.

## Rules

1. **Edit the source, never the generated output.**
   - Map objects, warps and connections go in `map.json`, not `events.inc`, `header.inc` or `connections.inc`.
   - Trainer parties go in `trainers.party`, not `trainers.h`.
   - Never edit `plastic_ox/wiki/site/`: it is built and untracked.
   - `plastic_ox/generated_manifest.json` says which tool owns which file.
2. **Check generator ownership before you hand-edit.** `build_story.py` and
   `region_v7.py` (with `league.py`) emit patches over map JSON and scripts.
   `make pox-check-static` fails if you make a story-owned file drift from its
   generator. When that happens, port the change into the generator. If the
   hand edit is intentional, run `python3 plastic_ox/tools/check_generated.py --update`
   and say so in the PR. Never regenerate over drift you didn't cause:
   inspect the `build_story.py` patch and apply only your part.
3. **HNS maps:** keep `"layout_version": "hns"` and
   `"include_in_versions": ["emerald"]`. HNS has 640 primary metatiles,
   Emerald-format 16-bit attributes and a 2x2 border. Never let one fall back to
   Emerald partitioning. Read the `plastic-ox-map-port` skill before touching
   layouts, tilesets or seams.
4. **Flags:** new persistent flags get a stable id in `story_flags.json`.
   Never reuse or renumber a retired id; save compatibility depends on it.
5. **Story:** if a location note disagrees with the v7 story bible, the bible wins. Fix the note.
   No two NPCs may share identical dialogue. NPCs are ordinary citizens, so
   any meta-commentary about the merged region stays subtle.
6. **Trainer teams:** must be Gen 3-legal and tier-legal for their story checkpoint
   (`plastic_ox/tools/pox_progression.py`). `test_trainer_teams_v2.py` enforces this.
7. **Verify behavior in the emulator.** Any change to gameplay, warps, scripts or gates
   needs an mGBA harness run, not only a static check. Extend or add a
   `plastic_ox/demo/test_<area>.py` (see the `plastic-ox-emulator-test` skill).
8. **Don't break** the metamon trainer-AI wiring (`plastic_ox/battle/metamon/`,
   `src/metamon_*.c`) or existing `TRAINER_PLASTIC_OX_*` ids.
9. **Known noise:** `plastic_ox/tools/check_map_refs.py` without `--changed` reports
   about 160 pre-existing errors in unused donor maps. Judge it only on the maps you
   touched (`--changed` or `--map <Name>`).

## Workflow

- Branch from `master` (`agent/<topic>`), commit, open a PR. Don't commit ROMs,
  logs, playtest JSON or screenshots; `.gitignore` covers the usual outputs.
- Story or location work: run `python3 plastic_ox/story/next_pass.py` and
  `python3 plastic_ox/story/story_context.py <slug>`, then follow the
  `plastic-ox-story-dialogue` skill. Write a run log at
  `plastic_ox/story/runs/<date>-<slug>.md`.
- Beads tickets (`DSH_SUPERAGENT_BEADS_ID` set): follow the `plastic-ox-beads` skill.
- Before the PR: `make pox-check-static`, `make pox-build`, and the emulator
  harnesses for the maps you touched. List exactly what you ran under
  **Verification** and anything left open under **Follow-ups**.

## Skills

| Skill | Use for |
|---|---|
| `plastic-ox-beads` | Start of every beads-originated ticket |
| `plastic-ox-story-dialogue` | NPC dialogue, signs and story beats from a location note |
| `plastic-ox-map-port` | Importing or repairing maps, seams, warps, tilesets |
| `plastic-ox-map-baseline` | Stripping a map back to foundational events |
| `plastic-ox-artifact-cleanup` | Removing donor maps, dead scripts, obsolete generated content |
| `plastic-ox-emulator-test` | Writing or running mGBA harnesses |
