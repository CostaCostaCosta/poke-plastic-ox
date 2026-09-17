# Plastic Ox Alpha — Version 7 implementation plan

Updated: 2026-09-12. Status: M0/M1 foundation work in progress; see the
implementation record below. The full physical v7 migration is still pending.
This replaces the old wave plan, preserved in [LEGACY_PLAN.md](LEGACY_PLAN.md).

## Sources and scope

- [Map v7](../plastic_ox_map_v7.md): progression, mandatory traversal, and unlock rules.
- [Story v7](../plastic_ox_story_v7.md): scenes, reveal timing, Gym order, and gifts.
- [Topology SVG](../plastic_ox_topology.svg): physical arrangement and route modules.
- [REGION_PLAN.md](REGION_PLAN.md): target legs, candidate assets, and old links to retire.
- [STORY_TRIGGERS.md](STORY_TRIGGERS.md): target event order and persistent gate conditions.
- [Encounter specification](../plasticox_encounters_v1.md): tier availability, caps, evolution, and items.

Implement the full main journey through Champion Bill, the four major traversal
unlocks, and a working Champion-only Lavender harbor/Frontier connection. Full
postgame island encounters, facilities, rematches, and superbosses are a separate
content milestone; opening a ferry alone does not complete that content.

Retain the walkable, trigger, and standalone battle build variants. The trigger
build is the progression acceptance target. The walkable build uses the same
physical graph with story gates relaxed and encounters/LOS disabled; its tests
must provide legitimate movement abilities for water routes. A walkable-build
pass does not prove story gating.

## Baseline established on 2026-09-12

- The previous [region notes](LEGACY_REGION_PLAN.md) mix sketches and historical
  shipped substitutions. Current map JSON and scripts determine actual behavior.
- `build_story.py --check` passes: 94 events, 28 trainers, 18 rooms. This proves
  generator consistency, not v7 compliance.
- The deterministic HNS import audit passes for 49 layouts. Existing rendering
  and cave repairs must survive the migration.
- `build_story.py` generates the checked-in story script, event manifest, room
  data, and other sources. `story_manifest.json` is generated output, not the
  authoring source. The generator emits an apply_patch patch when run without
  `--check`; review and apply that patch, then verify consistency.
- The generator still provides direct travel services between story towns,
  Fortree access/return for the Cottage, an optional synthetic Whirl room, and
  a Blackthorn-linked synthetic Victory Road. Retargeting outdoor maps alone
  would leave sequence-breaking routes or recreate them on regeneration.
- Oldale already connects to Route 103, which connects to Route 110. Rustboro
  has overlapping north links to native Route 115 and imported Route 2.
  These require explicit early-game bypass checks.
- Existing item flag definitions reuse offsets across different placements;
  Route 12/21 item offsets also exceed the header's documented reserved range.
  Audit actual uses and allocate unique, valid flags before adding new gates.
- Previous rendering checks recorded walking failures and isolated placements;
  see [rendering review](../demo/REGION_RENDERING_REVIEW.md). They are not
  evidence of an uninterrupted playable region.

## Planning decisions and unresolved source details

1. Confirmed design decision (2026-09-12): Saffron north opens with Saffron
   after the Space Center. Bruno and Silph do not gate Route5, Meteor Falls,
   Blackthorn or Clair. The late-game OU objectives are open-ended; retain
   the native Badge identities and the League's all-eight-badges check.
   Map v7 and story v7 now reflect this decision.
2. Unlock Route 36/110 on first legitimate Fortree arrival, with a persistent
   reached-Fortree flag. Do not require Winona as an extra shortcut condition.
   Winona still precedes the Lavender story segment.
3. The SVG contains Route 19, Route 20, and Hoenn Victory Road; use those
   candidates for the southern Saffron approach, southern sea, and League
   dungeon. It omits explicit Seafoam, Underground Path, Cottage interior,
   League rooms, and harbor nodes and contains no dashed gate paths. Add
   their required behavior from the written specifications. SVG coordinates
   are not ROM tile coordinates or proof of traversability.
4. Route 104 Top means the northern playable portion of native Route 104.
   Inspect whether isolated reuse is possible; if a separate map/layout is
   needed, preserve its matching tileset partition. Prevent exits into the
   native Petalburg route network.
5. Keep five gift Eevees: Cottage first available; retain family, Kimono,
   Fuji, and Space Center as the proposed remaining sites. Cottage is optional:
   skipping it must not prevent later gifts or story progression. Preserve
   gift flag identities when moving placements.
6. Story v7's Burned Tower paragraph ends with an unfinished sentence about
   Morty's sages. Do not invent its missing destination. Implement the specified
   brief restoration, no beast release, and Morty's return to the Gym; resolve
   the incomplete line during dialogue review.
7. Provide Surf before the required post-Blaine sea crossing, with no later
   badge requirement that deadlocks the journey. Inventory native HM checks
   before choosing exact acquisition. Early Surf access must not bypass the
   Oldale/Route 103, Pallet coast, or Seafoam barriers. Fly destinations,
   Teleport/whiteout respawns, Dig/Escape Rope, Dive, Waterfall, Strength and
   shared-interior exits need the same progression review.
8. Entei is UUBL in the encounter specification, available after the UU Gym
   under the tier ladder. Mansion investigation is mandatory, catching Entei
   is optional. Add the sage battle and guaranteed first-ball capture after
   winning, shared by other legendary encounters as those are implemented.
   Define retry behavior after fleeing, losing, KO, or full storage.

## Implementation milestones

The milestones below track the full migration. Complete each with focused verification and
an updated status/evidence entry; do not mark a map complete because it loads.

| Milestone | Work and primary files | Dependencies | Acceptance |
|---|---|---|---|
| M0 — Inventory and contracts | Inventory every connection, warp, coord event, map callback, travel NPC, Fly/respawn destination; reconcile SVG ports with REGION_PLAN; record donor revisions and exact map IDs; audit flags/save compatibility. Add a machine-readable directed edge/gate inventory and checks. | None | Every target leg has endpoints, direction, prerequisite, asset source, and test owner; all legacy bypasses classified. |
| M1 — Gates and generation | Update `build_story.py`, flag headers, `src/plastic_ox.c` helpers if needed, init logic and generated outputs. Implement reusable gate predicates, Fortree arrival, global Saffron lock including northern OU access, eight-badge League gate, Champion harbor. Make cleanup of obsolete generated actors explicit and regeneration repeatable. | M0 | Space Center independently enables Blackthorn/Clair; Bruno/Silph order does not restrict the north; save/reload and both build modes work; no duplicate/out-of-range flag allocation; generator check passes. |
| M2 — Opening through Gym 2 | Rewire opening, Route 1/31, Ilex/104, Rustboro, Cottage spur, Route 44/Mt. Moon/33/Goldenrod. Relocate Cottage entry/return and remove Fortree service. | M0–M1 | Fresh-start walk reaches Roxanne before Whitney, crosses Mt. Moon, and can take or skip Cottage; no early Blackthorn, Saffron, Cinnabar, Route 110, or Route 115 access. |
| M3 — Central and eastern journey | Make Park mandatory; Ecruteak east to Route 119/Weather/Fortree; Fortree to Route 110/Lavender; permanent Route 36 shortcut; reserve Ecruteak west for League. | M2 | Morty/Weather cannot be skipped; shortcut closed before arrival and bidirectional afterward; old Ecruteak-to-Kanto and west-to-Route119 bypasses absent. |
| M4 — Underground and southern sea | Route 8/Underground/7/103 to Cinnabar; Blaine key/Mansion; Route 20 and mandatory Seafoam to Mossdeep; Route 19 approach to sealed Saffron. | M3 | All Saffron entrances closed before Space Center; bypass usable; no direct Lavender/Cinnabar or Cinnabar/Mossdeep transport; continuous Surf-aware cave traversal, with safe returns. |
| M5 — Saffron, mountains, League | Open Saffron and the northern OU region after Space Center; support Bruno, Silph and Clair in open order; Route 5/115/Meteor Falls/Blackthorn; downhill 45/46; Ecruteak west/Hoenn Victory Road/League. | M4 | Clair is accessible before Bruno/Silph; all objective orders pass; eight badges open west; no early reverse climb; no Blackthorn-to-League shortcut. |
| M6 — Story, rewards, competitive integration | Revise dialogue and scene staging throughout generated/authored scripts; sage capture behavior; gift retries; tier/cap/encounter placement audit; trainer parties and double battle; Bill reveal only in Champion room and infrastructure explanation after victory. | M2–M5 | Reveal ladder, eight Gym tiers, three Rocket arcs, five gifts, no early Ubers; no early Bill explanation; no repeat rewards on revisit. |
| M7 — Champion and postgame entry | Set Champion state only after successful finale/Hall of Fame; open Lavender south, ferry to Frontier hub and return; gate every alternate postgame entry; list deferred island content. | M5–M6 | Harbor closed before Champion, persistent afterward; round-trip ferry and save/continue work; no softlock or native story leakage. |
| M8 — Integrated release verification | Fresh builds of all variants; replace stale route fixtures and add continuous v7 journey, state-dependent negative tests, screenshots, and documentation/diagram refresh. | M1–M7 | All required routes and gates proven in the trigger ROM; walkable graph and standalone battle regression pass; limitations explicitly recorded. |

Implement scene changes alongside each geographic milestone; M6 is the final
cross-region narrative and reward review. Full postgame island content follows
M7 with a separately enumerated destination/encounter plan.

## Implementation ownership and migration rules

- Outdoor topology lives in `data/maps/*/map.json`, map scripts, layout assets,
  and registrations. Update old import scripts if they remain supported;
  otherwise label them historical so rerunning them cannot masquerade as a v7
  regeneration. Remove bypass edges only after replacement routes are usable.
- Story ownership lives in `plastic_ox/alpha/build_story.py`; the authored
  `data/scripts/plastic_ox_pallet.inc` remains its included opening source.
  Change generator ownership before editing generated actors/rooms. A removed
  generator entry must also remove its old actor, coord event, or script link.
- Preserve completed Pallet work: starter choices/cancellation, perfect IVs,
  retryable supplies, Elm TMs/Move Compendium, Mom healing, and Oldale mart.
- Preserve deliberate NPCs, trainers, items, signs, warps, cave fixes, and
  ledges. Do not run a blanket map-baseline cleanup on story-bearing maps.
- Prefer physical seams, doors, gatehouses, and dungeon warps. Demo transport
  must not replace mandatory v7 geography. Resolve exact coordinates through
  layout/collision checks, not diagram scaling or assumed centered offsets.
- Retain unused legacy assets initially; disconnect them from progression and
  remove only confirmed dead assets in a separate cleanup. Existing saves need
  an explicit migration policy before IDs/flags/room destinations change.
  Default development acceptance uses fresh saves; compatibility is not yet promised.

## Verification and evidence

Baseline checks performed for this documentation change:

```sh
python3 plastic_ox/alpha/build_story.py --check
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py /home/eddie/repos/poke-plastic-ox
```

For implementation, build the normal ROM and optional battle demo sequentially with the configured toolchain:

```sh
export PATH=/home/eddie/devkitpro/opt/devkitpro/devkitARM/bin:$PATH
export CPATH=/home/eddie/toolchains/hostlibs/usr/include
export LIBRARY_PATH=/home/eddie/toolchains/hostlibs/usr/lib/x86_64-linux-gnu
export PKG_CONFIG_PATH=/home/eddie/toolchains/hostlibs/usr/lib/x86_64-linux-gnu/pkgconfig
make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM PLASTIC_OX_BUILD=battle modern
```

Extend existing `plastic_ox/demo/test_story.py` suites (starters, ivs, gifts,
gates, travel, battles, callbacks), `walk_region.py`, relevant `walk_leg*.py`,
`test_cave_connections.py`, and `test_camera_seam.py`. New v7 graph/continuous
journey checks are planned, not existing test commands.

Use the existing mGBA environment:

```sh
export LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_story.py all
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_cave_connections.py
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_camera_seam.py
```

Headless tests must use the deterministic bootstrap documented in
`plastic_ox/demo/TESTING.md`; the playable ROM now stops at the title screen.
Prefer `StoryGame(..., spawn=(map_name, x, y))` for isolated towns, maps, and
route legs. Use `boot_to_bedroom()` only for opening-flow coverage.

Test individual gates with controlled state, but also traverse the complete
journey from a fresh game without debug warps, injected completion flags, or
town-to-town service shortcuts. Include actual water movement. Prove each
bidirectional transition both ways; for one-way ledges prove the forward jump
and blocked reverse. Check landing tile, collision, elevation, screenshots,
post-transition stability, save/load, defeat, and escape paths.

Keep a table of milestone status, revision, commands, pass/fail results,
screenshots, and unresolved defects as implementation proceeds. Refresh the
implemented-layout renderer and town-map concept only after the graph is
verified. Keep the design SVG distinct from the generated ROM-layout view.

## Implementation record — 2026-09-12, first foundation slice

M0 and M1 are in progress; M2–M8 remain pending. This slice changes the
existing alpha's scripted access, not its physical route graph.

- Implemented the confirmed open-ended OU decision in the generator and
  generated scripts. BlackthornRoad, ClairGuide, and Clair's battle require
  Space Center completion only; Silph no longer toggles the obsolete north
  gate flag. Saffron dialogue presents Bruno, Silph and Clair as choices.
- Added `story_flags.json` as the permanent story-flag allocation source.
  Existing IDs, including all five Eevee gift flags, are unchanged. Moving
  events cannot renumber flags; new flags require explicit allocation, and
  retired IDs remain reserved.
- Corrected 14 item-flag definitions: seven shared wave-2 IDs and seven
  Route12/21 IDs outside the documented reserved run. All 46 item flags now
  have separate slots within 0x280–0x2BB. Existing saves cannot reconstruct
  which of two formerly aliased items was collected. Use fresh saves for v7
  item-state acceptance; this patch does not rewrite or delete save files.
- Added `audit_alpha.py`: 97 persistent flag allocations checked; inventory
  of 115 alpha/candidate maps and 51 direct generated script warp links.
  `--json` exposes connections, warp/coord events, object scripts, map-script
  source paths and lexical travel checks. It is an inspection inventory, not
  a claim of continuous reachability or complete callback/Fly/escape analysis.
- Labeled wave2–5 importers historical; they must not regenerate v7 maps.
  Their old flag allocators and routes are intentionally not a v7 toolchain.
- Runtime gate tests cover all eight Space Center/Bruno/Silph combinations,
  physical interaction with Clair's actor, no badge before battle victory,
  and the seven-versus-eight-badge League check with Clair earned before Bruno.
  Gate and gift suites pass; the latter covers duplicate gifts and full-party/
  full-PC retries. Default, trigger, and battle ROMs build successfully.
  Default-ROM new-game smoke test passes. Generator check,
  49-layout HNS audit, 97-flag audit and whitespace checks pass.
  Fresh `plastic_ox/demo/shots/story_clair_open_ou.png` shows the actual Clair
  battle introduction with Bruno and Silph incomplete (existing alpha sprite).

Reproduce the static inventory and changed runtime checks:

```sh
python3 plastic_ox/alpha/audit_alpha.py
python3 plastic_ox/alpha/audit_alpha.py --json
python3 plastic_ox/alpha/build_story.py --check
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_story.py gates
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_story.py gifts
```

Next: finish M0's measured endpoint/alternate-entry inventory, implement the
remaining physical gate contracts in M1, then rewire the opening/Cottage/Mt.
Moon section in M2. Route5/115/Meteor Falls is not yet connected by this slice;
the corrected northern access still uses the existing alpha travel service.
Route36/110, global physical Saffron entrance coverage, the Ecruteak League
approach, and Champion harbor remain migration work.
