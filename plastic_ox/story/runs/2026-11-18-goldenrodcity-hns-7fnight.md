# 2026-11-18 — goldenrodcity-hns (pox-2ma.8)

- Note: plastic_ox/story/locations/goldenrodcity-departmentstore-7fnight-hns.md (drafted -> implemented)
- Maps: GoldenrodCity_DepartmentStore_7FNight_hns
- Decision: retire, do not wire a GetTimeOfDay branch. The bible has no night roof; the note says no new mechanics, and a branch on the 6F stair needs return-warp rework in the 6F/7F day maps that other workers are editing.
- Changed: removed the four night NPCs, three Directory signs and their scripts from the map and its generator source (`plastic_ox/alpha/goldenrod/`). The map and layout stay registered as an empty tombstone because removal would renumber later `gMapGroup_PlasticOxInteriors` maps (the import appends to keep IDs stable). Its warp now lands on the 7F day map (warp 0) instead of the one-way 6F warp 2.
- Not folded in: the night lines (the tower-light count would change the day roof's voice; left for the 7F pass).
- Still open: tombstone registration and layout could be dropped in a deliberate ID-renumbering pass; the source manifest still records the donor's original objects/warps.
- Tests: story note check, wiki --check, ROM build (see PR).
