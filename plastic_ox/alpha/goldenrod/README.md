# Goldenrod import

Donor: `/home/eddie/repos/pokehns-expansion`, revision
`44f50eedefe58691b0444973e4138e9190d8fafc`, the same HNS fork used by the
existing Johto route/town importers. `source_manifest.json` records all 28
source maps, layouts, source and converted geometry hashes, original events,
used tilesets, and the exact tiles changed to open former story gates.

The 28 interiors are appended to `gMapGroup_PlasticOxInteriors`; existing map
IDs remain stable. All 14 city doors now lead to their corresponding HNS
interiors. Bill's house and the exterior retain existing Plastic-Ox content.
The two Underground entrance rooms, tunnel, switch rooms, storage, basement,
store floors/lift/roof, radio floors, gym, houses, shops, center and station
retain their donor geometry. Both rooftop variants are registered; the normal
rooftop is active. Train travel and donor day/night story switching are not
imported. There are no wild encounters in these interiors.

Local behavior:

- Both haircut brothers are present and repeatable. Older: ¥500; younger: ¥300.
  The real party selector chooses the recipient. Each successful haircut sets
  friendship to 255. Declining, cancelling, eggs and insufficient funds do not
  consume money or change friendship. The native setter also bounds-checks the
  party index and rejects eggs/empty slots.
- Whitney uses the existing Plastic-Ox battle, prerequisites and badge reward
  inside the HNS gym. Her outdoor guide now takes the player there. The retired
  synthetic gym remains registered for existing saves.
- Center healing, name/friendship rating, bicycle gift, flower-shop bottle,
  herb sales, department-store shops, slots and Plastic-Ox coin prizes use local
  scripts/services. Donor Voltorb Flip and Rocket/rival/train stories are not
  imported. The station explicitly tells visitors trains are suspended.
- Fourteen item balls have independent persistent unused flags 0x900–0x90D.
  These are below the RTC daily flags and outside the trainer-flag range.
- The elevator has a floor menu including basement and rooftop, remembers the
  originating floor for an ordinary exit, and has a physical basement door.
- Former Rocket gates are baked open using the donor's own metatiles. Donor
  automatic story triggers are removed. People are pinned; redundant Rocket
  actors, story duplicates, train sprites and animated monster actors are
  omitted. Existing city NPCs are moved only as needed for usable doors and
  continuous access, with placements recorded in `city_npc_positions.json`.

HNS partitioning is retained (640 primary tiles/metatiles, seven primary
palettes, 16-bit attributes). Nine missing secondary tilesets were imported;
behavior IDs are translated by name. Their animation callbacks are NULL,
consistent with existing alpha imports. `gTileset_GoldenrodBuilding_Hns`
shares the original building graphics/metatiles/palettes and changes only
attributes for exit mats 0x0E7/0x147 to `MB_SOUTH_ARROW_WARP`: the donor's animated
door behavior otherwise walks an arriving player into the black border.
Store lift events move from the unusable top door tile to the real door at
(9,4); the basement door is (10,6). A radio-tower NPC is moved off a staircase.

## Reproduction

From the repository root:

```sh
python3 plastic_ox/alpha/import_goldenrod.py --donor /home/eddie/repos/pokehns-expansion
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py .
make -j$(nproc) TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
git diff --check
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_goldenrod.py
```

`goldenrod.py` reapplies the converted event sources at the end of
`region_v7.apply_region`; normal story regeneration does not require the donor.
Edit local service scripts in `services.inc` and converted map events in the
neighboring JSON/inc files, then run `python3 plastic_ox/alpha/goldenrod.py`.
Use the donor importer only for a deliberate source refresh: it regenerates
those converted per-map event files.

Verification on the rebuilt ROM: 70 fixed directed warp traversals, all eight
lift choices, lift return/cancellation from six floors, continuous Underground
travel in both directions past both brothers, and a continuous tour through
all 14 city doors. Haircut tests use actual counter interaction and party-menu
input, verify only the selected second slot changes, both prices, cancellation,
insufficient funds, egg refusal, invalid indices and already-max friendship.
Fresh screenshots are under `plastic_ox/demo/shots/goldenrod_*.png`; Underground,
store, tower, gym and entrance rendering were inspected. HNS asset audit passes
for all 89 HNS layouts; `git diff --check` passes.

The broader pre-existing alpha audit still reports six fruit-tree daily flag
allocations, the Devon guard flag and Bill-PC flag inventory. The global story
regeneration check also reports pre-existing drift across other maps/scripts;
these unrelated changes were preserved. The focused Goldenrod reapplication
is independently checked for idempotence.
