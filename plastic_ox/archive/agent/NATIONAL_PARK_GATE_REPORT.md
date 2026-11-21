# Route 35 / National Park / Route 36 repair

Source: `/home/eddie/repos/pokehns-expansion`, revision
`44f50eedefe58691b0444973e4138e9190d8fafc`. Source map, script, and layout
hashes are recorded in `plastic_ox/alpha/national_park/source_manifest.json`.
The original Johto schedule and gate registration behavior were also checked
against pret/pokecrystal's Route35NationalParkGate and Route36NationalParkGate.

## Travel

The donor `Gate_NationalPark_hns` layout contains two separate gate sections
in a 50 × 18 map. It is appended to `gMapGroup_PlasticOxInteriors` without
renumbering existing maps. Its unchanged blockmap and 2 × 2 border use the
already imported `gTileset_Johto_Building_Hns` and `gTileset_Gate_Standard_Hns`.
The layout retains HNS partitioning (640 primary tiles and seven primary
palettes) and explicitly includes Emerald.

| Entrance | Gate warp | Return destination |
| --- | --- | --- |
| Route 35 `(17,5)`, `(18,5)` | 0 at `(7,13)` | Route 35 warp 2 |
| Park south `(11..14,49)` | 1 at `(7,1)` | Park warp 0 |
| Park east `(40,19)` | 2 at `(34,7)` | Park warp 2 |
| Route 36 `(16,20)` | 3 at `(48,7)` | Route 36 warp 0 |

Native door and arrow behaviors activate all entrances. The old coordinate
portals and generated portal signs for `route35_park` and `park_route36` are
removed. Existing map objects, story gates, and encounter tables are retained;
the former in-park registration NPC returns to ordinary park dialogue.

The source Route 35 north connection at +16 and Route 36 south connection at
−16 align Route 35 `(31,0)` with Route 36 `(15,29)`. The existing Cut tree at
`(31,6)` blocks this path until cut. No layout changes were needed for the
shortcut. Sudowoodo and Snorlax still protect their existing junction branches.

## Contest

Both gate attendants register contestants on Tuesday, Thursday, and Saturday.
Entering the park normally requires no contest registration. Registration
selects one healthy party member and enters through the corresponding park
entrance. The existing Plastic-Ox rules remain: 20 Sport Balls, a 500-step
budget, one retained catch, replacement choice, scoring, and prizes. This is
the existing step-based variant; it does not implement Crystal's 20-minute timer.
The existing contest bug encounter table is retained instead of importing the
donor's separate contest map and story engine.

Leaving by either park exit preserves the contest until the gate's arrival
script restores the party, delivers the retained catch, presents results, and
awards the prize. Step expiry and retirement return to the registration gate
for the same judging flow. Unexpected exits elsewhere retain the existing
automatic party restoration. Entry checks run the ordinary daily clock update
so the daily entry flag resets when the date advances.

The converted gate scripts replace donor-specific contest specials and object
graphics with the existing Plastic-Ox contest API and available graphics.
Unsupported donor music is replaced with `MUS_RG_ROUTE24`.

Both gate sections now show six NPCs on Tuesday, Thursday, and Saturday:
the ordinary officer and visitor, the contest attendant, and three entrants
gathered near the park door. On Sunday, Monday, Wednesday, and Friday, only
the officer and ordinary visitor remain in each section. A map-local temporary
hide flag is recalculated on transition before object creation. Visibility
depends on the weekday, including after the player completes that day's entry.
The gate JSON and scripts in `plastic_ox/alpha/national_park` preserve the
crowds through story regeneration.

## Verification

Commands:

```sh
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py /home/eddie/repos/poke-plastic-ox
make -j$(nproc) TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_national_park.py
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_route36_junction.py
git diff --check
```

Results: ROM build passed; HNS audit passed for 102 layouts. The mGBA test
passed both Route 35 entrance lanes, all four park south exit lanes, both gate
sections in both directions, travel through the park grounds, actual Cut tool
interaction, shortcut round trip, and tree respawn. It passed all seven RTC
weekdays, interaction with both gate attendants, catch delivery, prizes, daily
entry rejection and reset, step expiry, and retirement.

A real grass encounter selected a contest bug and ran normal Pokémon combat.
The test threw a real Sport Ball, verified its consumption and the catch
callback, retained the bug, judged it at the gate, restored the six original
party members, and verified the catch in the PC. Enemy battle HP and sleep are
fixture setup to make capture reliable; ROM capture code is unmodified.
The separate Route 36 junction regression passed its collision, story gates,
and Route 37 seam checks.

Fresh captures are under `plastic_ox/demo/shots/national_park_*.png`. Gate
sections, park grounds, and shortcut arrivals were visually inspected.

The crowd regression checks actual spawned NPC IDs and coordinates in both
gate sections on all seven weekdays, verifies six versus two NPCs, checks that
every NPC stands on walkable floor, and tests visibility after daily entry.
Fresh `national_park_{south,east}_crowd_{contest,quiet}.png` captures were
visually inspected. The full National Park emulator suite, ROM build, HNS
audit, installer idempotence check, and `git diff --check` passed afterward.

`national_park.install` is idempotent and runs last in the story generator,
preserving these warps and connections on regeneration. The broader
`build_story.py --check` still reports pre-existing generation drift in other
maps/story data; its generated patch was inspected without applying unrelated
changes.
