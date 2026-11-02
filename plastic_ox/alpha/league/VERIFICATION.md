# Victory Road / League takeover verification

Verified 2026-10-25 on `codex/metamon-trainer-ai`, HEAD
`bc13328862ef96855e1a2570a86a700a2001d572`. No commit was made. The existing
large dirty feature diff, untracked League sources, and unrelated user work
remain in place. The reported `181e2cbc16` was not the current HEAD. No
`AGENTS.md` or `Pasted text.txt` was found in the checkout or ancestor instruction
locations. The repository map-port skill and installed ROM-build skill were read.

## Starting inventory and takeover changes

The outdoor ridge, houses, facilities, teams, scripts, flags and Hall-of-Fame
hook already existed. The interrupted full regression passed on the initial
ROM, including the previously failing house carpet step. No map replacement
or roster rewrite was necessary.

Takeover edits:

- `src/battle_main.c`: replace the contiguous-ID assumption with five explicit
  trainer identities; exclude doubles/multi-opponent, link, facilities and other
  trainer-ID namespaces from the League recovery exception.
- `plastic_ox/demo/test_league.py`: assert trainer identity and runtime species,
  order, scaled level, IVs and moves; carry burn/PP as well as HP; check restored
  held items; visit each house twice and distinguish healing from advice;
  observe Metamon decisions/faults for all eleven opponents; test full bags,
  pickup/save persistence and saved doors; verify HoF party registration,
  saved Champion ribbon and the actual Champion save's ferry access.
- `plastic_ox/demo/test_league_rules.py`: real Gym battles with injected normal
  completion callbacks in both Clair/Bruno orders, Bag-menu Potion use, ledges,
  trainer sight lines, lobby badge checks, closed forward doors, rear-exit and
  sequence restrictions, pre-Bill save, and ordinary Emerald Continue targets.
- `plastic_ox/demo/test_league_regeneration.py`: exercise the real overlay,
  region/story generators and generic trainer writer using virtual files and a
  temporary party file, preserving the dirty checkout.
- `README.md` and this record: document actual policy AI, existing level scaling,
  test evidence and remaining human playtest limits.

The pinned Route26 import and overlay were reapplied and the ROM rebuilt.
Unrelated TM/item substitutions, Fuji reward edits, Route 36/Lavender closures,
Burned Tower changes and artifact-cleanup inventory were inspected and retained.
They were present at takeover; no sweeping cleanup or regeneration patch was
applied. The new source maps/scripts/party/binary layout are not ignored; normal
build outputs, ROM and screenshots remain ignored. New source files remain
untracked until the feature is committed with the existing work.

## Commands and results

Run from `/home/eddie/repos/poke-plastic-ox`. In the table, `E` expands to:

```sh
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python
```

| Command | Final result |
| --- | --- |
| `python3 plastic_ox/alpha/league/import_layout.py` | PASS: pinned HNS donor, 39×51 dry ridge and border |
| `python3 plastic_ox/alpha/league.py` | PASS: overlay reapplied |
| `python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py "$PWD"` | PASS: 103 HNS layouts, metadata/asset bounds; run before and after changes |
| `PATH=/home/eddie/devkitpro/opt/devkitpro/devkitARM/bin:$PATH make -j12 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern` | PASS: bootable 32 MiB ROM; ROM payload 28,295,256 bytes, EWRAM 226,608 bytes, IWRAM 28,540 bytes |
| `python3 plastic_ox/agent/test_trainer_teams_v2.py` | PASS: 2,684 checks over 89 trainers |
| `E plastic_ox/demo/test_league.py --static --travel --route --ai --battles --persistence` | PASS: detailed coverage below |
| `E plastic_ox/demo/test_league_rules.py` | PASS: both Gym orders, one actual Potion use, 3 ledges, 6 sight-line cases, 8 lobby denials, 5 rear exits, 4 forward doors, 4 skipped-member denials, pre-Bill save, 2 normal Emerald Continue destinations |
| `python3 plastic_ox/demo/test_league_regeneration.py` | PASS: overlay idempotent across 34 files; 22 owned files survive region/story generation; encounters, reward flags, respawn and 11 authored parties preserved; generic team writer retains all authored sets |
| `E plastic_ox/demo/test_region_v7.py --only meteor_blackthorn` | PASS: **2 actual crossings**, without Bruno/Silph prerequisites |
| `E plastic_ox/demo/test_region_walk.py postgame` | PASS: **4 continuous transitions**, no intermediate setup warps |
| `E plastic_ox/demo/test_region_v7.py --only lavender_harbor --closed` | PASS: **2 actual denied crossings** without game clear |
| `E plastic_ox/demo/test_region_v7.py --only harbor_frontier --closed` | PASS: **2 actual denied crossings** without game clear |
| `E plastic_ox/demo/test_trainer_recovery.py` | PASS: ordinary trainer win/loss and wild control; HP/status/PP/held-item conventions |
| `E plastic_ox/demo/quick_check.py` | PASS: fresh boot, opening tremor, Pallet bedroom |
| `E plastic_ox/demo/test_story.py all` | PASS: starters, IVs, gifts, gates, travel, 10 battle starts and isolated victory callbacks; includes 8 northern OU prerequisite combinations |
| `E plastic_ox/demo/test_camera_seam.py` | PASS: Oldale/Pallet seam round trips, 5 maintained views with zero BG differences from stationary redraw |
| `git diff --check` | PASS |

Focused `test_league.py --battles` and `--ai` reruns also passed during test
extension. The first new runtime-level assertion expected authored levels
exactly and failed on Wallace (64 observed versus base 62): inspection of HEAD
confirmed existing global upward scaling. The corrected assertion checks
`max(authored level, strongest player level)`, preserving game mechanics.
Initial supplementary test failures were fixture issues: optional map JSON
without object events, repeated A presses consuming both supplied Potions, and
an already-active native Hall script. These were fixed with safe JSON defaults,
a one-Potion fixture, and an isolated non-Plastic-Ox GameClear invocation.
No final test selects zero crossings or suppresses a failing assertion.

## End-to-end evidence

- Eight badge denials at Ecruteak, four successful throat lanes, then the full
  ridge/Indigo/lobby round trip on actual D-pad inputs. This travel leg makes
  **9 successful map transitions** (four throat entries plus summit, lobby
  entry/exit, downhill, Ecruteak return), with fixture warps only between throat
  lane checks. Optional terraces and all three rewards are visited on foot.
- Both houses: **8 physical door crossings** across two visits each; walking,
  interaction, exit and re-entry pass. Western keeper heals; upper adviser does
  not. The downhill attendant adds a separately tested service transition.
- Six route battles create six Pokémon each; completion flags survive map
  reload and prevent rematches. Five sight lines activate the intended trainer;
  Helen remains interaction-only. A real grass encounter uses the authored
  level/species pool. No water or HM is needed for the walking route.
- All eleven endgame opponents instantiate the canonical party, ordered moves
  and IVs and execute an actual policy-selected move. Each reports nonzero
  Metamon decisions and zero fault. Their authored species/order/base levels
  are unchanged. The global upward level scaling and held-item restoration are
  preserved; Basic Trainer/Smart Switching/PP Stall Prevention remain configured
  fallback flags, not the active policy during these ordinary singles.
- Wallace → Steven → Lance → Blue → Bill progresses via opened forward doors;
  HP, burn and depleted PP carry between fights; consumed held items restore.
  Normal Bag-menu Potion use succeeds. All five injected losses take the normal
  blackout/nurse path, clear temporary progression, and restart at Wallace.
- Full-bag rejection, successful retry, flash save/reset/Continue and no repeat
  pickup are checked for each reward. Flash saves also preserve all four won
  Elite Four rooms and a pre-battle Bill room.
- Bill's normal completion callback reaches HoF, registers the fixture party,
  sets game clear, saves the Champion ribbon, starts credits and continues at
  Indigo. That same Champion save passes the Lavender ferry gate. The separate
  continuous postgame walk reaches the existing Frontier entrance and returns.
- Ordinary Emerald GameClear retains Brendan/May's respective Littleroot
  destinations. The Plastic Ox hook is conditional on the custom HoF map.
- Bill is identified only in his encounter; postbattle dialogue explains his
  training/transfer-system responsibility without adding a crisis or assuming
  Silph completion. His normal overworld sprite and Scientist battle portrait
  remain intentional.

## Artifacts and limits

ROM: `pokeemerald.gba`, SHA-256
`444e23484ed0bbfd55beea7e19b29f9ba71e0da3559f2e4dcbbc84499b82fd47`.

Fresh screenshots: `plastic_ox/demo/shots/league/` (approach, lower/upper ridge,
terraces, summit, both houses, Indigo/lobby/PC/shop, all battles/AI, three ledge
approaches/landings, Hall of Fame, credits, Continue and postgame ferry).
Representative route/house/League and ledge/Champion captures were visually
inspected. Test logs are copied to `plastic_ox/demo/shots/league/verification/`.
Other regressions write their existing `shots/region_v7`, `shots/region_walk`,
`story_*` and `camera_*` artifacts.

No known failing automated acceptance case remains. Battle outcomes used to
prove victory sequencing, rewards and blackouts are injected into normal engine
finish handlers. **Five complete unassisted competitive League victories have
not been demonstrated.** The 15–20 minute pacing target and full human difficulty
assessment remain unmeasured. Visual review uses fresh emulator captures; it is
not a claim of a complete human playthrough. No postgame islands or new AI/model
project were added.
