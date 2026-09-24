# Native camera-seam review

Audit date: 2026-09-18.  The static audit (`audit_native_seams.py`) covers 26
directed declarations / 13 reciprocal camera edges from `region_manifest.json`,
including the connected `BattleFrontier_OutsideEast` map.  It verifies map
dimensions through `Geometry`, reciprocal offsets, aligned edge openings, and
edge elevation metadata.  Result: **26/26 declarations passed; no reciprocal
or zero-overlap failures**.

## Repair

`improve_battle_frontier_seam.py` repairs the East boundary using only East's
own block IDs (the two maps have different secondary tilesets):

- rows 5–8 now use the existing East metatiles with elevation bits cleared to
  match West's elevation-0 opening;
- rows 9–14 are closed with East's existing boundary block, removing a
  one-way opening that West did not have;
- rows 40–54 were already reciprocal and remain unchanged.

The resulting Frontier edge has 19 aligned openings in both directions and
the same edge footprint.  The generated static record is
`plastic_ox/demo/shots/native_seams_static.json`.

## Audited seams

All entries below passed reciprocal metadata and had at least one aligned
opening unless marked water-only:

| Reciprocal edge | Offset pair | Result |
|---|---:|---|
| PalletTown_Frlg ↔ Route101 | +2 / -2 | pass |
| Route101 ↔ OldaleTown | 0 / 0 | pass |
| OldaleTown ↔ Route29_hns | -6 / +6 | pass |
| Route29_hns ↔ CherrygroveCity_hns | +6 / -6 | pass |
| CherrygroveCity_hns ↔ Route2_Frlg | +22 / -22 | pass; one narrow shared lane by source geometry |
| Route2_Frlg ↔ RustboroCity | -6 / +6 | pass |
| RustboroCity ↔ Route24_hns | +3 / -3 | pass; four-lane throat, verified by `test_rustboro_north.py` |
| Route24_hns ↔ Route25_hns | 0 / 0 | pass; three separated edge paths are native geometry |
| Route21_North_Frlg ↔ Route21_South_Frlg | 0 / 0 | water/closed edge; preserve Surf-only route |
| Route21_South_Frlg ↔ CinnabarIsland_Frlg | 0 / 0 | pass for aligned water/land approach |
| Route36_hns ↔ Route37_hns | +22 / -22 | pass; shared openings preserve native separated paths |
| Route37_hns ↔ EcruteakCity_hns | +16 / -16 | pass |
| BattleFrontier_OutsideWest ↔ BattleFrontier_OutsideEast | 0 / 0 | repaired; 19 reciprocal openings |

The narrow/shared-lane and separated-path cases were left intact: widening
them would change imported route geometry or consume reserved entrances.  The
Route21 closed land edge is intentional and is covered by the existing
Surf-gate policy/test; it must not be carved into an on-foot connection.

## Remaining validation

Run after the parent rebuilds the ROM:

```sh
python3 plastic_ox/agent/audit_native_seams.py
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_camera_seam.py
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_rustboro_north.py
```

The Frontier repair still needs a fresh mGBA round trip and screenshot review
after build; no build or ROM mutation was performed here.
