# 2026-11-26 — Kanto integration (agent/kanto-integration)

Branch `agent/kanto-integration` merges four agent branches and applies the
user's follow-ups. No push, no PR.

## Merged
- `agent/lavender-kanto-seams` (fast-forward): Lavender <-> Route 8 walk-across
  seam, real Saffron gatehouses, Route 8 tunnel hut, tower crown.
- `agent/tower-and-kanto-encounters`: Executive PROTON, UU tables on Routes 8/7/21,
  Warden KANGASKHAN, Route 44 Surf-only grass. Conflict in `route7-hns.md`:
  kept the seams branch's geometry, added the UU table facts.
- `agent/devon-silph-scope`, `agent/substitute-route2-house`: clean merges.
  Route2_House_Frlg stopped drifting; baseline shrunk.

## Follow-ups
- Scyther/Pinsir only in the Warden's Thursday contest after badge 4
  (`PoxContestLandTable`); the Thursday park-grass swap is gone.
- KANGASKHAN on every Thursday-round win after badge 4 (party, PC, or held at the
  desk). `FLAG_POX_GIFT_PARK_KANGASKHAN` removed. The WARDEN hands it over on a
  Thursday; on any other day the desk attendant does, with its own lines.
- Hoenn Safari Zone deleted (7 maps + Route 121 entrance, layouts, tables);
  SpecialArea slots kept as `PoxRetired_SafariZone_*` placeholders. Route 121
  itself is untouched except for the dead warp.
- Route 21 North/South: 5 grass, 3 surf, 5 rod species (UU, evolved).
- Pokemon Tower 7F Rockets: sight-4 trainers (lavender.py), dormant until story
  mode + badge 4, never re-triggering once beaten.
- Route 7's grass is behind a Cut tree at (13,10) in a continued row-10 fence
  (`route7_cut_hedge.py`, `region_v7.py`).
- Cinnabar's sea exit is now the edge column (23,9..11): the Surf hop onto
  (23,10) is not a step and never fired the old single-tile trigger.
- Route 110: the four haulers no longer wall the lower lane at (7..10,83);
  the fourth moved to (10,85). Before this, nothing could walk south to
  Lavender on Route 110 (found by test_region_walk central).
- `story_manifest` generator keeps the TowerGrunt entries for sight trainers;
  `region_manifest.json` regenerated (no longer drifts).
- test_region_v7 walks the crossings the ROM has (see DISK_CROSSINGS in the
  test for the hand-reworked ones). test_region_walk's central leg now uses
  the real Goldenrod, National Park and Ecruteak gatehouses and clears the
  Johto trainer flags (932..937) and Route 36's story blockers.

## Dialogue written
- WARDEN (Thursday): "First place in my round! ... I don't give stones on a
  Thursday. I give family." + party / PC / no-room lines.
- Gate desk (other days): "He couldn't wait for you, so he left your prize in
  our care. She's been napping behind the desk and eating our lunches." +
  party / PC / no-room lines.

## Verification
`make pox-check-static`, `make pox-build`, and the mGBA harnesses listed in the
branch report (test_lavender, test_lavender_kanto, test_kanto_uu_encounters,
test_national_park, test_devon_silph_scope, test_weather_institute,
test_fortree_winona, test_route2_house, test_route44_transitions,
test_region_walk underground/central/postgame, test_story battles,
test_region_v7).

## Open
- `PoxRetired_*` placeholders and empty groups: remove together at release.
- Cinnabar/Goldenrod/Oldale crossings in region_v7.py still describe the old
  geometry (their maps are baselined drift); the test overrides document it.
