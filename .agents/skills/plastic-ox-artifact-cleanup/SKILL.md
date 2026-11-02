---
name: plastic-ox-artifact-cleanup
description: Audit or remove retained donor maps, unused story scripts, and obsolete generated content in poke-plastic-ox. Use for artifact cleanup and distinguishing current v7 gameplay from Hoenn, FRLG, or HNS leftovers; not for map porting or removing intentional progression gates.
---

# Plastic Ox artifact cleanup

Work in `/home/eddie/repos/poke-plastic-ox`. Read the paired [cleanup inventory](../../../plastic_ox/artifact_cleanup.md).
Run `python3 plastic_ox/agent/audit_cleanup_artifacts.py` for fresh JSON triage.
The inventory is a dated snapshot, not an automatic deletion allowlist.

## Establish actual use

Inspect dirty files and preserve ongoing work. Use the current region and story
manifests, `region_v7.py`, `build_story.py`, and the final `league.py` overlay.
Follow map JSON object scripts and callbacks into their actual labels before
interpreting a donor script. In particular, Fortree's active Winona is
`Pox_Winona`, awarding badge 4; the vanilla badge-6 handler is not the live NPC.
Gabby and Ty in Fortree are intentional badge-4 blockers.

The audit protects authored manifest maps, literal map references in shared
Plastic Ox scripts, and their directed warp/connection closure. Protection can
include unused compatibility code; absence can miss engine-selected maps,
shared-script warps, fly/respawn, dynamic returns, or external scripts. Resolve
those references before deciding whether a candidate is unused. Audit is
read-only; creating an inventory does not itself request deletion.

## Clean the requested slice

Separate obsolete gameplay actors/callbacks from unused map registrations and
shared assets. An unreachable map can supply a live script, layout, tileset,
trainer party, animation, or facility template. Check callers by map constant,
script label, layout and tileset ID, not just directory name. Preserve active
postgame/Frontier and multiplayer/dynamic interiors unless their replacement is
part of the requested cleanup.

Update generator sources before generated outputs, including final overlays.
Do not blindly regenerate over unrelated dirty changes: inspect the patch from
`python3 plastic_ox/alpha/build_story.py` before applying relevant changes.
Use source JSON rather than editing generated `events.inc`, map headers, or
encounter/heal headers. Search C tables, respawns, fly locations, encounters,
rematches, roamers, TV, event-script includes and other versions' map groups.
Keep numeric map IDs stable for existing saves where feasible; removing entries
can renumber subsequent maps. Stub/tombstone maps may be preferable to deletion.

## Verify and maintain the inventory

Rerun the audit and inspect the affected graph and references. Use
`git diff --check` and `python3 plastic_ox/alpha/build_story.py --check` for
source changes, distinguishing existing drift from new regressions. For ROM
changes, follow the `pokeemerald-build` skill and run relevant story/league or
map-travel checks. For documentation-only work, validate links and the skill;
a ROM rebuild is unnecessary. Update the paired inventory with what was
removed, what remains, dependency evidence, and the checks actually performed.
