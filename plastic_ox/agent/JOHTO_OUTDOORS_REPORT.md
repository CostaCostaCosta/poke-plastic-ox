# Route 36, Route 37, and National Park

Implemented against the existing local layouts and dirty working tree. Donor
roster/positions: pokehns-expansion revision
`44f50eedefe58691b0444973e4138e9190d8fafc`, maps `Route36_hns`, `Route37_hns`,
and `NationalPark_Normal_hns`. No tileset imports or encounter changes.

The roster matches the original Johto arrangement, verified against
[Route 36](https://github.com/pret/pokecrystal/blob/master/maps/Route36.asm),
[Route 37](https://github.com/pret/pokecrystal/blob/master/maps/Route37.asm), and
[National Park](https://github.com/pret/pokecrystal/blob/master/maps/NationalPark.asm):

- Route 36: Mark and Alan; two battles.
- Route 37: Ann and Anne share one team/victory flag; Greg is the second battle.
- National Park: Beverly, Jack, Krise, and William; four battles.

Existing Mark/William teams and IDs remain. Six new IDs (932..937) have six-member
teams checked against the project's progression, species, level, and move rules.
New victory flags use audited unused persistent slots: 0x082, 0x4FA, 0x4FF,
0x91D, 0x91E, and 0x91F. The daily Sitrus flag is separate at 0x933.

Human NPCs now discuss gardening, local wildlife, family traditions, the orchard,
stone-wall maintenance, and Ecruteak's bells and dancers. Their text uses explicit
line/page breaks. The Route 37 tree at (33,24) grants five Sitrus Berries once
per day through the existing fruit-tree system, independently of Route 46.

Route 37 columns 16..19 connect to Ecruteak columns 32..35 with offsets -16/+16.
The stone road reaches the city's arch; the duplicate route arch and old city
western opening are removed. Both scripted teleports and their blocking signs
are retired. The native Route 37 sign at (20,13) provides directions.
`improve_ecruteak_south.py` reproduces the binary edits. `johto_outdoors.py` applies
canonical event/dialogue/trainer sources after story/region regeneration.

Normal trainer scripts begin with trainerbattle so the sight scanner honors
victory flags. Contest protection in trainer_see/battle_setup prevents both
sight and interaction battles during an active Bug-Catching Contest.

## Verification

All passed on the final ROM:

- Build: `env PATH=/home/eddie/devkitpro/opt/devkitpro/devkitARM/bin:$PATH make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern`
- `python3 plastic_ox/agent/test_trainer_teams_v2.py`: 3,612 checks over 82 trainers.
- HNS import audit: all 102 layouts pass; persistent flag audit: no collisions.
- Authored outdoor event installer is idempotent; `git diff --check` passes.
- `test_johto_outdoors.py`: all nine trainer objects start the correct six-Pokemon
  battles; twins share their victory; defeated park trainers stop approaching;
  active contest prevents trainer interruptions; real tree interaction and
  ClearDailyFlags verify harvest quantity, daily limit, reset, and independence.
- All four city seam lanes round trip with story triggers enabled and disabled.
  All sixteen scrolling/reference comparisons have zero differing BG entries;
  no forced-white frames. Continuous walk through the arch succeeds both ways.
- Existing Route 36 junction runtime checks pass, including both story blockers
  and the Route 36/37 round trip.
- Existing National Park gate, registration, judging, expiry/retirement, and real
  Sport Ball catch tests pass, including party restoration and PC delivery.

Runtime commands use `LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64`
and `/home/eddie/.venvs/mgba311/bin/python`. Fresh screenshots under
`plastic_ox/demo/shots/` include `johto_route37_entrance.png`,
`johto_ecruteak_arch.png`, `camera_johto_city_16_True.png`, and
`johto_route37_sitrus_tree.png`; entrance, seam, and berry screenshots were inspected.

ROM SHA256: `b5508a098d0cf00caed8b85e86efd8759688723b1ddb3a422c061e2b853b50e0`.
