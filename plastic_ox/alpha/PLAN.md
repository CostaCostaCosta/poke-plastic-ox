# Plastic Ox Alpha 0.1 — Plan of Record

Story basis: `plastic_ox/plastic_ox_story_v0.6.1.md`. Topology inspiration:
`plastic_ox/plastic_ox_topology.svg` + `plastic_ox/topology_app/parts_catalog.json`.
Map assets: `/home/eddie/repos/pokehns-expansion` (Kanto+Johto, Emerald-format, `_hns`
suffix) plus native Emerald Hoenn maps already in this repo.

## Deliverables

1. **Walkable demo** (`make`, default): whole region stitched end to end, no story
   triggers, no trainer line-of-sight battles, no wild encounters. A headless harness
   walks Pallet → … → Indigo Plateau.
2. **Trigger demo** (`make PLASTIC_OX_BUILD=triggers` → `pokeemerald-triggers.gba`):
   same region with story events, gates, trainers, gifts. Tested town-by-town
   headlessly.
3. Custom NPC dialogue everywhere (new-region flavor per story v0.6.1).
4. Frequent commits; each wave lands only when it builds green + headless check passes.

## Architecture decisions

- **Keep `_hns` map/layout/symbol names** when importing (mechanical, collision-free).
- **Region gating**: imported maps set `"region": "REGION_HOENN"` and drop
  `game_version`; layouts preserve `layout_version: "hns"` and opt into the
  Emerald build with `include_in_versions: ["emerald"]`. HNS has its own
  640-primary/7-palette partition and must not be decoded as Emerald.
- **Shared interiors**: one Johto PC, one Kanto PC, one Johto Mart, one Kanto Mart,
  two generic houses. Every town's doors retarget to these (hns interiors are
  byte-identical duplicates anyway). Unique interiors only for: Pallet set, 8 gyms,
  story dungeons/gates/facilities listed in REGION_PLAN.
- **Scripts are rewritten fresh** for every imported map (custom Plastic Ox dialogue).
  Never copy hns scripts.inc wholesale. Berry-tree objects, time-of-day objects and
  wild-mon overworld objects are deleted on import.
- **Runtime trigger gate**: global `gPlasticOxTriggersEnabled` (see TRIGGERS doc).
  Walkable build = 0, trigger build = 1. Gates trainer LOS (`src/trainer_see.c`) and
  wild encounters (`src/wild_encounter.c`) when 0.
- **Music**: remap MUS_HG_* → existing RG/Emerald tracks (IMPORT_GUIDE table).
  No audio import in alpha.
- **Encounters**: tables exist where native maps already have them; they are simply
  unreachable in the walkable build via the runtime gate. Tier-based tables are a
  post-alpha task.

## Waves (each ends with commit)

| Wave | Content |
|---|---|
| 1 | Plumbing: flags/vars header, music remap infra, runtime gates, triggers build target, MAPSEC merge tooling. Leg A maps (Pallet→R101→Oldale→R29→R46→DarkCave→R31→R30→Cherrygrove loop incl. shared interiors). Headless walk Leg A. |
| 2 | Leg B (Ilex↔R34↔R116↔Rustboro) + Leg C (Rustboro→R2/R3→Mt.Moon→R4→R14→Goldenrod). |
| 3 | Leg D (Goldenrod gate→R35→Park→R36→R37→Ecruteak) + Leg E (Ecru→R38→R119→Fortree; cottage spur R16/R24/R25→Sea Cottage). |
| 4 | Leg F (Fortree→R16? see plan→Lavender) + Leg G (Lavender→R12→R19→R21→Cinnabar; Tower+Mansion+Gym warps). |
| 5 | Leg H (Cinnabar→R41/Whirl→Mossdeep), Leg I (Mossdeep→R125→R128→R6→Saffron gates), Leg J (Saffron→R5/R44/R45→IcePath→Blackthorn→VictoryRoad→Indigo Plateau→League). |
| 6 | Dialogue polish pass all towns. |
| 7 | Story triggers + town-by-town tests (trigger build). |
| 8 | End-to-end walk test (walkable build) + stretch features (overworld speedup) + docs/tag. |

## Build & verify (verbatim)

```sh
export DEVKITARM=/home/eddie/devkitpro/opt/devkitpro/devkitARM
export DEVKITPRO=$HOME/devkitpro/opt/devkitpro
make -j$(nproc) pokeemerald.gba            # walkable build
make -j$(nproc) pokeemerald-triggers.gba   # trigger build (after wave 1)
LD_LIBRARY_PATH="$HOME/.venvs/mgba311/lib:$HOME/.venvs/mgba311/lib64" \
  ~/.venvs/mgba311/bin/python plastic_ox/demo/<test>.py
```

After changing anything under `tools/mapjson/`: `make -C tools/mapjson` then
`rm -f .map_version` before the next build.

## Reference material for agents

- `/tmp/opencode/recon_hns.md` — hns asset/format recon (tileset closure, connection
  graph, interior sharing, risks). Recreate with the explore agent if missing.
- `/tmp/opencode/recon_infra.md` — this repo's new-game flow, walklib API, build
  system, script macro inventory.
- `plastic_ox/demo/walklib.py` — headless mGBA harness.
