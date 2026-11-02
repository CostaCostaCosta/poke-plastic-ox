# Plastic Ox endgame — outdoor Victory Road

Implemented 2026-10-23. This specification supersedes the older cave-based
League approach and the alpha's NPC-teleport League prototype. Story v7 and
regional topology v7 remain authoritative elsewhere.

## Map and asset provenance

- Donor: `/home/eddie/repos/pokehns-expansion`, revision
  `44f50eedefe58691b0444973e4138e9190d8fafc`.
- Source map/layout: `Route26_hns`, 39 × 81. The new
  `LAYOUT_PLASTIC_OX_VICTORY_ROAD` keeps rows 0–49 plus a final copy of row 49
  (39 × 51), removing the southern water/bridge approach. The original
  `border.bin` is retained. Reproduce with `import_layout.py` in this directory.
- Matching, already imported tilesets: `gTileset_Johto_General_Hns` and
  `gTileset_Blackthorn_Hns`. Their local graphics, metatiles, remapped behavior
  attributes, palettes and animations are reused without alteration. Layout
  metadata explicitly uses `hns` and includes Emerald: 640 primary metatiles,
  seven primary palettes, 16-bit attributes, 2 × 2 border.
- Stable destination map: `PlasticOx_VictoryRoad` in `gMapGroup_PlasticOxStory`.
  Existing map and opponent IDs are preserved. New maps append to that group.
- Native Route 26 doors `(24,11)` and `(9,31)` lead to two copies of the existing
  `House_GenericA_hns` layout. The western house heals; the upper house offers
  battle advice. Both have explicit reciprocal exit warps.
- Existing `IndigoPlateau_hns` exterior and Pokémon Center are retained.
  The lobby retains its working PC metatile, gets a shop and League official,
  and uses a fixed exterior exit instead of an uninitialized dynamic warp.
- Wallace, Steven, Lance and Blue reuse Emerald's Sidney/Phoebe/Glacia/Drake
  rooms, with their proper character sprites. Bill reuses the Champion room
  and Bill's existing overworld sprite. Hall of Fame reuses Emerald's layout.
  Bill uses the existing FRLG Scientist battle portrait; no Bill battle portrait
  is present in the asset library. This is the one remaining art substitution.

## Traversal and events

Ecruteak's full western throat `(8,34..37)` checks **each** of the eight badge
flags. Missing badges return the player one tile east. No Silph or Bruno-order
assumption is added: Clair can be defeated before Bruno, but both badges are
required at the gate.

| Source | Trigger/door | Landing |
| --- | --- | --- |
| Ecruteak west | `(8,34..37)` | Victory Road `(27,48)` |
| Victory Road south | `(25..28,49)` | Ecruteak `(9,35)` |
| Victory Road north | `(13..15,1)` | Indigo `(12,18)` |
| Indigo south | `(10..14,19)` | Victory Road `(14,2)` |
| Indigo building | `(11,6)` | lobby's native entrance |
| Lobby exit | `(19,16)` | Indigo building entrance |
| Indigo return attendant | `(15,9)` | Ecruteak `(9,35)` |

All route objects and both ends share a dry, bidirectionally walkable component.
The eastern ridge is the direct climb; the western terraces, rest house,
Leftovers, Max Elixir and Rare Candy reward exploration. Pickups use normal
bag-full-safe item scripts and independent persistent SaveBlock3 flags
`POX_EVENT_FLAGS_START + 21..23`, not trainer/daily flags.

Six level-58 trainers cover mixed offense/hazards (the existing ACE roster),
rain, sand, stall, offense and balance. The rain specialist covers the direct eastern path, and the final balance
trainer covers the narrow summit. The remaining encounters are avoidable; the
western stall opponent is interaction-only. No puzzle, Surf, Cut, Strength,
Rock Smash, Waterfall, Flash or cave traversal is required.

The authoritative encounter header is `gPoxVictoryRoadOutdoor` in
`src/data/wild_encounters.json`: level 52–56 Dodrio, Sandslash, Tauros, Donphan,
Skarmory, Heracross, Medicham, Breloom, Girafarig, Ditto, Bagon and Beldum.
Standard slot weights are 20/20/10/10/10/10/5/5/4/4/1/1. There are no water,
fishing, Rock Smash or Uber encounters on the new route.

## League teams

Species, order and per-Pokémon levels are preserved from the existing
`ROSTERS` in `plastic_ox/agent/apply_trainer_teams_v2.py`, which takes precedence
over the earlier alpha stub and narrative suggestions. Consequently Bill's
already specified roster is retained rather than replaced with Alakazam,
Porygon2 or an Eeveelution. `trainers.party` beside this document is the
canonical complete set definition.

| Opponent | Team, in order | Role |
| --- | --- | --- |
| Wallace | Salamence 62, Swampert 62, Tyranitar 62, Metagross 61, Forretress 61, Gengar 61 | Choice Band pressure, Intimidate, Spikes/spin and disruptive Gengar control switches and tempo. |
| Steven | Metagross 62, Salamence 62, Flygon 62, Aggron 62, Armaldo 61, Claydol 61 | Wish/Protect Salamence supports a defensive core; Toxic, Knock Off and two spinners manage attrition. Aggron supplies a deliberate offensive opening. His fixed roster has no Spikes user, so hazard control is defensive. |
| Lance | Gyarados 62, Starmie 62, Charizard 62, Claydol 61, Medicham 61, Swampert 62 | Dragon Dance, Choice Band Medicham, mixed Charizard/Swampert and Explosion maintain pressure. |
| Blue | Tyranitar 64, Salamence 64, Metagross 64, Gengar 63, Gyarados 64, Forretress 63 | Sand balance with multiple setup threats, mixed coverage, status, Spikes and Rapid Spin. |
| Bill | Metagross 64, Starmie 64, Cloyster 63, Flygon 63, Swampert 63, Charizard 64 | Spikes offense creates an Agility Metagross endgame, with Choice Band Flygon, mixed Charizard, offensive spin support and Swampert as a stabilizer. |

All 66 authored Pokémon have four Gen III moves, standard Gen III abilities,
held items, natures, legal EV totals and explicit 30/31 IVs. Hidden Power types
are encoded through IV parity, not discarded string suffixes. Canonical
ADV references are the repository's `plastic_ox/gen3_movesets.json`, including
[Metagross](https://www.smogon.com/dex/rs/pokemon/metagross/),
[Salamence](https://www.smogon.com/dex/rs/pokemon/salamence/), and
[Claydol](https://www.smogon.com/dex/rs/pokemon/claydol/).
Steven's Wish Salamence uses the Gen III NYPC event move; see the contemporary
[Wish-Mence description](https://www.serebii.net/potw/373.shtml).
Egg moves and inherited moves are intentional (e.g. Metang's Agility,
Mudkip's Hydro Pump, Shroomish's Spore and Eevee's Baton Pass). The generic
trainer generator's fallback cannot model these and must not overwrite them.
The current checkout's existing Metamon policy controls ordinary trainer singles,
including all eleven endgame opponents. Emulator checks observe actual moves,
nonzero `gMetamonDecisions`, and zero `gMetamonFault` for each. The authored
Basic Trainer / Smart Switching / PP Stall Prevention flags remain the fallback
configuration for engine modes where policy inference is disabled. No new
inference integration or model change is introduced by this feature.

The engine removes the level cap after badge six. The current checkout also
already scales every ordinary trainer Pokémon to the greater of its authored
level and the player's strongest non-Egg. Thus the table records preserved
**base levels**, not an exemption from existing level scaling (the level-64
fixture meets level-64 opponents). No new League level cap, scaling rule or
species restriction has been introduced.

## Challenge lifecycle

Entering the lobby sets `HEAL_LOCATION_POX_INDIGO` and clears the five temporary
challenge victory flags and their trainer flags. The official verifies all
eight badges again, explains the rules, asks whether to start, resets the
challenge and enters Wallace's room. Doors close behind the player. Winning
opens the forward door; the next room checks every earlier victory. Players
can save and use ordinary bag items between matches. There is no in-challenge
PC, nurse, escape warp or free return to the lobby.

League wins preserve HP, status and PP. This exception names the five trainer
IDs explicitly and excludes doubles, multi-opponent, link and facility ID
namespaces; it does not depend on contiguous numeric opponent constants. Held items still restore
under Plastic Ox's global trainer-battle convention. Defeat takes the normal
blackout/nurse path to Indigo and resets the sequence. Existing overworld
trainer recovery is otherwise unchanged.

Only the Champion encounter identifies Bill. His responsibility for the
adaptive training/transfer infrastructure is explained **after** the battle,
with no additional crisis or assumption that the player already cleared Silph.
The Hall of Fame calls the existing `GameClear` implementation: party record,
Champion ribbons, first-clear time, `FLAG_SYS_GAME_CLEAR`, save and credits.
The saved continuation destination is Indigo rather than unrelated Littleroot.
The five `FLAG_POX_LEAGUE_*` flags describe the current challenge;
`FLAG_SYS_GAME_CLEAR` is permanent Champion completion and already unlocks the
Lavender south ferry/Frontier path. Postgame content itself is unchanged.

## Regeneration and verification

`python3 plastic_ox/alpha/league.py` reapplies just this feature. The same
installer runs last in `region_v7.apply_region`, preserving the new endgame
when the older story generator is used. The general trainer generator protects
these canonical parties. Generated `.h`, map registration and event files are
still produced by the normal build.

```sh
python3 plastic_ox/alpha/league/import_layout.py
python3 plastic_ox/alpha/league.py
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py "$PWD"
PATH=/home/eddie/devkitpro/opt/devkitpro/devkitARM/bin:$PATH \
  make -j12 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
python3 plastic_ox/agent/test_trainer_teams_v2.py
export LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_league.py \
  --static --travel --route --ai --battles --persistence
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_league_rules.py
python3 plastic_ox/demo/test_league_regeneration.py
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_region_v7.py --only meteor_blackthorn
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_region_walk.py postgame
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_trainer_recovery.py
/home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/quick_check.py
git diff --check
```

Screenshots are written under `plastic_ox/demo/shots/league/`. The suite walks
actual map transitions and interacts with NPCs, items, PC and shop. It checks
all badge prerequisites, each route opponent, a real wild encounter, each
League team's party creation and an AI-selected move, sequential doors,
loss/retry at all five stages, damage retention, Hall of Fame, credits, an
actual in-memory flash save and Continue. Outcomes used for progression and
blackout tests are injected through the normal battle finish handler; these
are not claims of five complete unassisted competitive battle victories.
Human playtesting remains useful for overall difficulty and pacing.

## Takeover verification (2026-10-25)

The interrupted house regression passes. The test now explicitly walks off the
native entry carpet, visits each house twice (eight door crossings), and checks
that only the western keeper heals. The general pathfinder still avoids warps.
Additional checks cover all three full-bag reward retries and persistence through
real flash saves, HP/status/PP retention, held-item restoration, Bag-menu Potion
use, all eleven policy-controlled opponents, actual Clair/Bruno battle callbacks
in both orders, three ledges, every route sight line, saved room progression,
Hall-of-Fame registration/ribbon, and ferry access using the Champion save.
Normal Emerald GameClear destinations are checked for both player genders.

[Verification record](VERIFICATION.md) records commands, counts, limitations,
and screenshot locations. Five full unassisted competitive victories and the
15–20 minute human pacing target remain playtest work; injected outcomes only
verify normal completion/reset handlers. Bill's Scientist portrait remains the
intentional existing-art substitution.
