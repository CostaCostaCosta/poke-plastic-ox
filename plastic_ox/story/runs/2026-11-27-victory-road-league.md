# 2026-11-27: Victory Road and League dialogue/mechanics pass

Slugs: `plasticox-victoryroad`, `indigoplateau-hns`. Generator: `plastic_ox/alpha/league.py`.

## Audit findings
- League text wrapped every two lines onto a new page (`\p`), so sentences broke across pages. Paragraphs now scroll with `\l`, and `|` is the only page break.
- The route trainers repeated generic encouragement. Rewrote them from the location note's voices: the greeter, rain/terraces, sand switches, the terrace advocate, summit wind, and "the door is a door".
- Rest houses: the exit warp was at `(4,9)` on a plain floor tile. The south-arrow carpet is `(4,8)`, so the player could not leave either house (this bug was on master). Fixed in `league.py` and both map.json files.
- The house keepers now use the hut-keeper register, and the advice keeper says where the heal is.
- Lobby: the welcome desk, scout, nurse and official have new lines. The official speaks as a registrar. Welcome, scout and official have post-`FLAG_SYS_GAME_CLEAR` lines for rematches.
- Elite Four speeches trimmed to one idea each: Wallace beat, Steven cover, Lance commitment, Blue observation.
- Bill: an ordinary defeat line replaces "the calculation was wrong" (villain diction). The confession is tightened. A rematch win skips the confession.
- Hall of Fame: the speech moved from an absent Bill to the registrar.
- Ported the committed return band `y=50` into `league.py`. `plastic_ox_league.inc` and `PlasticOx_VictoryRoad/map.json` no longer drift; the baseline was shrunk with `check_generated.py --update`.
- Harnesses: `test_league.py` and `test_league_rules.py` now follow the Route 38 gatehouse checkpoint from `ecruteak_repairs.py`. Added `--postgame`.

## Open
- `test_league.py --ai` stalls with a black screen during an AI battle. It does the same on clean master (stalled at RIDGE_SAND there), so this pass did not cause it.
- `CherrygroveCity_SoutheastHouse_hns` has the same `(4,9)` exit warp on the `HOUSE_GENERIC_A_HNS` layout. It probably has the same trap; not checked in the emulator.
- Legacy cave maps and the dead `_Open` arm, the FRLG Indigo maps, and the `VAR_TEMP_1` Hall guard.
