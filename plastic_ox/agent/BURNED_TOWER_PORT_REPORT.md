# Burned Tower 1F and B1F port

## Source and conversion

- Donor: `/home/eddie/repos/pokehns-expansion` at
  `44f50eedefe58691b0444973e4138e9190d8fafc`.
- Source maps/layouts: `BurnedTower_1F_hns` (27 × 25) and
  `BurnedTower_B1F_hns` (28 × 19). All four `map.bin`/`border.bin` files are
  byte-identical to the donor (1F: 1350/8 bytes; B1F: 1064/8 bytes).
- Destination maps: `PlasticOx_BurnedTower` retains its story-group map ID;
  `PlasticOx_BurnedTowerB1F` is appended to that group to preserve existing
  room numbers. Both layouts use `layout_version: hns`, are included in the
  Emerald build, and pair `gTileset_Johto_Building_Hns` with
  `gTileset_BurnedTower_Hns`. The tilesets were already registered.
- Warps: Ecruteak `(22,14)` ↔ 1F `(15,22)`; 1F ladder `(24,10)` ↔ B1F
  ladder `(26,7)`. The donor's second B1F warp was tied to a rival-triggered
  fall event that this story does not use, so neither end is active.
- Events: donor rival, Eusine, trainers, beast release, wandering Pokémon,
  and coordinate scripts were removed. A pinned sage, four one-time pickups,
  and Morty's basement memory scene use Plastic Ox scripts. The Fire Stone
  replaces the donor's 1F HP Up, as specified for pre-Morty Eevee evolution.
  The source's Ether, Ultra Ball, and TM12 pickups remain. Pickup flags use
  audited unused persistent slots `0x918..0x91B`.
- Encounters: `plastic_ox/encounter_tables/nu_encounters_v1.md` is the source
  for 1F (Lv. 22–24) and B1F (Lv. 23–26). B1F has Koffing 30%, Gastly 20%,
  Rattata 15%, Dunsparce 10%, Chimecho 10%, Zubat 10%, Sableye 5%.
  The v7 story bible governs the scene: the tower briefly recalls an intact
  stair; Raikou, Entei, and Suicune are not released here.

## Runtime evidence

`plastic_ox/demo/test_burned_tower.py` on the rebuilt `pokeemerald.gba`
defeated the Lv. 20 Sudowoodo, confirmed its flag and bottle removal, walked
Route 36 → Route 37 → Ecruteak, entered 1F through the city door, obtained the
Fire Stone, took the ladder to B1F, saw the temporary stair and completed
Morty's event, returned through both warps, then started Morty's Gym battle.
The same test confirmed that his battle is gated beforehand and started a
real B1F wild encounter (Chimecho Lv. 24). Fresh screenshots were inspected at
`/tmp/pox_burned_tower_shots/` for city arrival, both floors, and the memory
scene; both floors render coherently.

Verification commands:

```sh
PATH=/home/eddie/devkitpro/opt/devkitpro/devkitARM/bin:$PATH \
  DEVKITARM=/home/eddie/devkitpro/opt/devkitpro/devkitARM make -s -j8 modern
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_burned_tower.py
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py .
python3 plastic_ox/alpha/audit_alpha.py
python3 plastic_ox/encounter_tables/test_pre_mt_moon_v5_5.py
python3 plastic_ox/encounter_tables/test_nu_encounters_v1.py
python3 plastic_ox/demo/test_warps_v1.py --static-only
git diff --check
```

The build and focused playthrough passed; the HNS audit checked 101 layouts,
the flag audit checked 209 unique allocations, and the encounter suites passed
238 and 189 checks. The global static warp scan reported 29 findings elsewhere
and none involving Burned Tower or Ecruteak. The broader trainer-team check
currently reports three Route 2 trainers without checkpoint assignments; this
port does not edit those trainers. `build_story.py --check` also reports
unrelated in-flight source drift, while its Burned Tower script output matches
the checked-in scene.
