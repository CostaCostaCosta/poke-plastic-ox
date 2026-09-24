# Rustboro north / Route 24

Target baseline: `2fc27b914d`. Reuses the existing Plastic-Ox layouts; no new
donor assets or engine changes.

| Map | Layout | Tilesets | Entrance | Connection |
| --- | --- | --- | --- | --- |
| RustboroCity | 40 x 60, Emerald | HoennOrasGeneral / HoennOrasRustboro | x=19..22, y=0 | north, +3, MAP_ROUTE24_HNS |
| Route24_hns | 30 x 22, HNS | Kanto_General_Hns / CeruleanCity_Hns | x=16..19, y=21 | south, -3, MAP_RUSTBORO_CITY |

Offsets use metatiles: northbound `route_x = city_x - 3`; southbound
`city_x = route_x + 3`. Both road surfaces have elevation 3. The north Route 25
connection and south Route 2 connection remain available.

`improve_rustboro_north.py` owns the layout changes: continue Rustboro's brick
road, narrow its eastern forest edge, and close Route 24's unrelated riverside
path with local fence blocks. `region_v7.py` owns reciprocal connections and
the sign beside the city approach. Remove the obsolete `rustboro_cottage`
coordinate triggers, scripts, port records, and transition records; this
passage had no story prerequisites. Other story events remain in place.

The existing cross-primary renderer extends each map's edge into the camera
margin and reloads the destination tilesets on crossing. This retains each
map's visual style; it does not preview the foreign tileset across the border.

Encounter source remains the `MAP_ROUTE24_HNS` registration and
`gPoxRoute24Hns_{Morning,Day,Night}_LandMons` in the generated wild table.
Rustboro has no grass encounter surface at this exit. The route's grass bank
is reached via Route 25, around the river.

Verification:

```sh
python3 plastic_ox/agent/improve_rustboro_north.py
python3 plastic_ox/alpha/build_story.py
# Inspect/apply only the relevant emitted patch; baseline regeneration also
# proposes unrelated sign/actor changes elsewhere in the region.
make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_rustboro_north.py
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py .
git diff --check
```

The focused emulator test walks all four lanes both ways, checks exact landing
coordinates and collision, rejects white frames, compares scrolling buffers
against a stationary redraw, checks the blocked east bank, and walks onward
through Route 25 to trigger a Route 24 encounter from its authored table.
Fresh images are under `plastic_ox/demo/shots/rustboro_north_*.png` and
`camera_rustboro_north_*.png`.

Research sources and reusable conclusions are in
`.agents/skills/plastic-ox-map-port/references/port-verification.md` and the
personal `poke-map-stitch/references/city-route-transitions.md` skill reference.
