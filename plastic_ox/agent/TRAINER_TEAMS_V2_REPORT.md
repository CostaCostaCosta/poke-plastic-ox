# Trainer Teams v2 and Wild Encounter Audit

**Scope.** Part 1 audits every Plastic Ox wild-encounter table against the
authoritative specification and fixes the divergences. Part 2 rewrites every
reachable `TRAINER_PLASTIC_OX_*` party to a full, progression-legal six.

**Base commit.** `181e2cbc16` (branch `codex/metamon-trainer-ai`, working tree left
uncommitted as instructed).

**Tooling added by this task**

| File | Purpose |
|---|---|
| `plastic_ox/encounter_tables/audit_encounters_v55.py` | Recomputes the effective rate of every Plastic Ox table and diffs it against the v5.5 document |
| `plastic_ox/encounter_tables/test_pre_mt_moon_v5_5.py` | Regression test for the pre-Mt. Moon block (174 checks) |
| `plastic_ox/encounter_tables/apply_v55_exact_land_rates.py` | Applies the exact v5.5 authored grass rates |
| `plastic_ox/agent/pox_progression.py` | Story checkpoints, species availability, evolution legality, tier gating, move legality |
| `plastic_ox/agent/apply_trainer_teams_v2.py` | The roster table and the `.party` writer |
| `plastic_ox/agent/test_trainer_teams_v2.py` | Regression test for the rewritten parties (3,403 checks) |
| `plastic_ox/agent/trainer_teams_v2_build.json` | Machine-readable record of every generated mon |
| `plastic_ox/agent/trainer_headers_baseline.json` | Pre-overhaul trainer headers, so the test can prove no wiring moved |

---

# Part 1 — Wild encounter audit

## 1.1 Which document is authoritative for what

| Document | Areas it covers | Verdict |
|---|---|---|
| `plastic_ox/encounter_tables/plastic_ox_pre_mt_moon_encounters_v5_5_agent_ready.md` | All fifteen pre-Mt.-Moon areas (Pallet, Route 101, Oldale, Route 103, Route 29, Route 46, Cherrygrove, Route 2 South, Ilex Forest, Route 2 North, Dark Cave, Rustboro, Route 24, Route 25/Sea Cottage, Route 44) | **Authoritative.** It is explicitly the end state, it supersedes the earlier documents, and the whole pre-Mt.-Moon block in the ROM already matches it. |
| `plastic_ox/encounter_tables/plastic_ox_pu_encounters_v1.md` | Mt. Moon, Route 33, Route 35, National Park, Route 36, plus the Headbutt and contest populations | **Authoritative for the PU block, but only where v5.5 is silent.** The PU block is fully implemented by `apply_pu_v1.py` and is byte-identical to the document. Where v5.5 *also* speaks about a pre-Mt.-Moon Headbutt table (Route 29, Route 46) v5.5 wins; the PU document still carried the older Paras-bearing populations. |
| `plastic_ox/encounter_tables/nu_encounters_v1.md` | Route 37, Ecruteak City, Burned Tower 1F/B1F | **A forward specification, not implemented.** `MAP_ROUTE37_HNS`, `MAP_ECRUTEAK_CITY_HNS` and `MAP_PLASTIC_OX_BURNED_TOWER` have no encounter table at all in `wild_encounters.json`. Reported, not implemented — see 1.5. |
| `plastic_ox/plasticox_encounters_v1.md` | Not area tables: the master competitive-tier release schedule, level caps, evolution gating and evolution-item schedule | **Authoritative for tiers and caps** everywhere else in this report. It is also the source of the tier table the engine ships in `src/data/pokemon/evolution_tier_gates.h`. |
| `plastic_ox/encounter_tables/plastic_ox_pre_mt_moon_encounters_v4_4.md` | The superseded pre-v5 draft | **Superseded.** `apply_pre_mt_moon_v4_4.py` still parses it, which is why `test_pre_mt_moon_v4_4.py` had been failing since the v5.5 migration (see 1.6). |

## 1.2 Verification method

`wild_encounters.json` stores either no `weights` key (the engine then falls
back to the fixed 12 land slots `20/20/10/10/10/10/5/5/4/4/1/1`, or the rod
weights `70/30 | 60/20/20 | 40/40/15/4/1`) or an explicit `weights` array. The
audit recomputes the **effective** conditional probability of every species from
whichever of the two applies, then diffs it against the authored table. Headbutt
tables live in `src/data/plastic_ox_pu_encounters.h` rather than the JSON and are
checked there. Rates summing to 100 and every level band are checked for all
twenty-one Plastic Ox encounter headers.

### Per-area verification

| Area / method | Status | Detail |
|---|---|---|
| Pallet Town fishing (Old/Good/Super) | confirmed | exact 2/3/5 slot split, Old 70/30, Good 60/20/20, Super 40/40/15/4/1, 100% each |
| Oldale Town fishing | confirmed | exact 2/3/5 slot split, Old 70/30, Good 60/20/20, Super 40/40/15/4/1, 100% each |
| Route 103 fishing | confirmed | exact 2/3/5 slot split, Old 70/30, Good 60/20/20, Super 40/40/15/4/1, 100% each |
| Cherrygrove City fishing | confirmed | exact 2/3/5 slot split, Old 70/30, Good 60/20/20, Super 40/40/15/4/1, 100% each |
| Route 24 fishing | confirmed | exact 2/3/5 slot split, Old 70/30, Good 60/20/20, Super 40/40/15/4/1, 100% each |
| Route 25 fishing | confirmed | exact 2/3/5 slot split, Old 70/30, Good 60/20/20, Super 40/40/15/4/1, 100% each |
| Route 44 fishing | confirmed | exact 2/3/5 slot split, Old 70/30, Good 60/20/20, Super 40/40/15/4/1, 100% each |
| Route 101 grass (all hours) | confirmed | all hours: rates total 100, levels 2-4 |
| Route 103 grass (Morning) | confirmed | Morning: rates total 100, levels 3-5 |
| Route 103 grass (Day) | confirmed | Day: rates total 100, levels 3-5 |
| Route 103 grass (Night) | confirmed | Night: rates total 100, levels 3-5 |
| Route 29 grass (Morning) | confirmed | Morning: rates total 100, levels 3-5 |
| Route 29 grass (Day) | confirmed | Day: rates total 100, levels 3-5 |
| Route 29 grass (Night) | confirmed | Night: rates total 100, levels 3-5 |
| Route 46 grass (Morning) | confirmed | Morning: rates total 100, levels 4-6 |
| Route 46 grass (Day) | confirmed | Day: rates total 100, levels 4-6 |
| Route 46 grass (Night) | confirmed | Night: rates total 100, levels 4-6 |
| Route 2 South grass (Morning) | confirmed | Morning: rates total 100, levels 4-6 |
| Route 2 South grass (Day) | confirmed | Day: rates total 100, levels 4-6 |
| Route 2 South grass (Night) | confirmed | Night: rates total 100, levels 4-6 |
| Ilex Forest grass (Morning) | confirmed | Morning: rates total 100, levels 6-8 |
| Ilex Forest grass (Day) | confirmed | Day: rates total 100, levels 6-8 |
| Ilex Forest grass (Night) | confirmed | Night: rates total 100, levels 6-8 |
| Route 2 North grass (Morning) | confirmed | Morning: rates total 100, levels 7-10 |
| Route 2 North grass (Day) | confirmed | Day: rates total 100, levels 7-10 |
| Route 2 North grass (Night) | confirmed | Night: rates total 100, levels 7-10 |
| Dark Cave walking (Morning) | confirmed | Morning: rates total 100, levels 5-8 |
| Dark Cave walking (Day) | confirmed | Day: rates total 100, levels 5-8 |
| Dark Cave walking (Night) | confirmed | Night: rates total 100, levels 5-8 |
| Route 24 grass (Morning) | confirmed | Morning: rates total 100, levels 8-11 |
| Route 24 grass (Day) | confirmed | Day: rates total 100, levels 8-11 |
| Route 24 grass (Night) | confirmed | Night: rates total 100, levels 8-11 |
| Route 25 grass (Morning) | confirmed | Morning: rates total 100, levels 9-12 |
| Route 25 grass (Day) | confirmed | Day: rates total 100, levels 9-12 |
| Route 25 grass (Night) | confirmed | Night: rates total 100, levels 9-12 |
| Dark Cave Rock Smash (Morning) | confirmed | Aron 60 / Rhyhorn 30 / Geodude 5 / Onix 5 |
| Dark Cave Rock Smash (Day) | confirmed | Aron 60 / Rhyhorn 30 / Geodude 5 / Onix 5 |
| Dark Cave Rock Smash (Night) | confirmed | Aron 60 / Rhyhorn 30 / Geodude 5 / Onix 5 |
| Route 29 Headbutt (day) | confirmed | 100% |
| Route 29 Headbutt (night) | confirmed | 100% |
| Route 46 Headbutt (day) | confirmed | 100% |
| Route 46 Headbutt (night) | confirmed | 100% |
| Route 24 Headbutt (day) | confirmed | 100% |
| Route 24 Headbutt (night) | confirmed | 100% |
| Route 25 Headbutt (day) | confirmed | 100% |
| Route 25 Headbutt (night) | confirmed | 100% |
| Ilex Forest Headbutt (day) | confirmed | 100%, Pineco 15% |
| Ilex Forest Headbutt (night) | confirmed | 100%, Pineco 15% |

## 1.3 Fixes applied

All five are in `src/data/wild_encounters.json` and `src/data/plastic_ox_pu_encounters.h`,
generated by the two scripts in the tooling table.

| # | Area | Divergence from v5.5 | Fix |
|---|---|---|---|
| 1 | Route 101, Route 103, Route 29, Route 46, Route 24, Route 25 grass (16 tables) | The tables were fitted to the engine's fixed 12 land slots, which cannot express the authored rates. Surskit sat at 10% instead of 5%, Mareep at 7% instead of 10%, Cleffa at 20% instead of 15%, Magby at 20% instead of 15%, Pidgey at 20% instead of 15%, Geodude at 22% instead of 25%, Machop at 10% instead of 15%. v5.5's engine note says to use the project's custom land configuration rather than silently change the intended rates, and the weighted path was already proven by Route 2, Dark Cave and the PU block. | Each table now carries an explicit `weights` array equal to the authored rate. `apply_v55_exact_land_rates.py` performs the rewrite. |
| 2 | Route 103 grass | **Voltorb** (morning and day) and **Koffing** (night) were present at 5%; neither is in the v5.5 Route 103 table, and `plasticox_encounters_v1.md` releases both at Gym 2 (PU), not in the zero-badge block. | Removed from Route 103. Both remain obtainable pre-Gym 1 on Route 2 North, exactly where v5.5 puts them. |
| 3 | Route 46 grass | **Trapinch** was present at 4% in all three periods; it is not in the v5.5 Route 46 table and is a Gym 2 release. | Removed from Route 46. Trapinch remains on Route 2 North. |
| 4 | Route 29 and Route 46 Headbutt | The tables came from `plastic_ox_pu_encounters_v1.md` and still carried **Paras**; v5.5 drops it and re-weights Natu 25→35% and Exeggcute 15→20% on Route 46. | `apply_pu_v1.py` now carries the v5.5 populations; `plastic_ox_pu_encounters.h` regenerated. |
| 5 | Route 24 and Route 25 Headbutt | v5.5 specifies both tables (Pichu/Sunkern/Ledyba/Natu/Hoothoot/Exeggcute/Slakoth and Meowth/Pichu/Ledyba/Exeggcute/Spearow/Slakoth); neither existed in the ROM. | Added to `apply_pu_v1.py` and `GetHeadbuttTable()` in `src/wild_encounter.c`. |

The v5.5 Super Rod delta, the four Good Rod swaps, the Dark Cave walking and
Rock Smash tables, the Route 2 South/North separation, the Ilex Headbutt table
and all seven fishing tables were already correct in the ROM and are confirmed
unchanged.

## 1.4 Non-negotiable invariants — all confirmed

| Invariant | Result |
|---|---|
| Route 2 South and Route 2 North have no water or fishing | confirmed — `MAP_ROUTE2` carries six land tables and nothing else |
| Dark Cave walking excludes Aron, Geodude, Onix and Whismur | confirmed in all three periods |
| Dark Cave Rock Smash is 60/30/5/4/1 (Onix 5% effective) | confirmed in all three periods |
| Dark Cave walking is five species per period, 100% | confirmed; Snorunt 20% at night, Larvitar 5% always, Teddiursa 10% morning |
| Whismur is on Route 103 at 10% | confirmed |
| Pineco appears in exactly one table (Ilex Headbutt, 15%) | confirmed across the JSON and the Headbutt header |
| Ralts 5% and Gastly 5%-night on Route 2 North | confirmed |
| Phanpy 5% morning on Route 46 | confirmed (was 4% before fix 1) |
| Teddiursa 10% morning in Dark Cave | confirmed |
| Old Rod slot 1 is Magikarp 70% in every Plastic Ox fishing table | confirmed (8 of 8) |
| No Super Rod slot holds a UU/UUBL/OU/Uber species, an OU-only family, Magikarp or Feebas | confirmed — all seven specced wet areas plus Ilex use only the approved LC/PU/NU/RU list |
| Rod slot counts are 2 / 3 / 5 with 70/30, 60/20/20, 40/40/15/4/1 | confirmed (Route 35 is the documented exception, see 1.5) |
| Route 44 grass stays Surf-gated | confirmed — `MAP_ROUTE44_HNS` has no land table |
| Rustboro has no ordinary wild encounters | confirmed |
| Every Plastic Ox table's rates total 100 | confirmed |

## 1.5 Unresolved — reported, not guessed

1. **Ilex Forest has a fishing table that the specification does not contain.**
   `gPoxIlexForestHns_{Morning,Day,Night}` each carry a full ten-slot fishing
   table (Old Magikarp/Poliwag, Good Poliwag/Barboach/Corphish, Super
   Poliwhirl/Whiscash/Crawdaunt/Azumarill/Politoed). v5.5 lists Ilex Forest as
   grass and Headbutt only, and its checklist says "7/7 fishing areas" and "21
   Good Rod slots across seven wet areas" — the Ilex table makes it eight areas
   and twenty-four slots, and re-duplicates Poliwag, Barboach and Corphish.
   It also makes Azumarill and Politoed (RU-tier species) catchable from an
   LC-tier pond. The table was added by the same commit that wrote the v5.5
   document, so the intent is not recoverable from the history. **Left as-is and
   flagged**: removing a working fishing table is a content decision, and the
   v5.5 document itself says to report a mismatch rather than overwrite
   unrelated work.

2. **The NU block (`nu_encounters_v1.md`) is unimplemented.** Route 37,
   Ecruteak City and Burned Tower 1F/B1F have no encounter tables. The document
   is a specification for work that has not been done, not a divergence in
   existing data. This is the single biggest content gap found: it caps the
   obtainable species pool at NU (see Part 2.2).

3. **Good Rod level bands differ from the document.** Every Good Rod slot in all
   eight fishing tables is `min_level 10` with the area's own maximum, while
   the v5.5 section headings state the LC-area band (Pallet 2-5, Oldale 3-5,
   Route 103 3-6, Cherrygrove 4-6, Route 24 8-11, Route 25 9-12, Route 44 10-13).
   The pattern is uniform and reads as a deliberate "Good Rod fish are at least
   level 10" decision rather than an accident, and every value stays inside the
   LC cap of 13, so no tier gate is broken. **Left as-is and flagged** rather
   than silently downgrading eight tables to levels as low as 2.

4. **Rod award timing cannot be established statically.** The v5.5 invariants
   require the Old Rod to be unobtainable before OU progression and the Super
   Rod to be unobtainable before RU. In the ROM, Old Rod and Super Rod givers
   live on FRLG/Hoenn maps (`VermilionCity_House1_Frlg`, `Route12_FishingHouse_Frlg`,
   `MossdeepCity_House3`) that appear unreachable from the Plastic Ox region,
   while the Good Rod is given by Oak in the opening lab and by a Cherrygrove
   fisherman — which is exactly what the v5.5 Good-Rod invariant wants. Whether
   the Old/Super Rod are actually reachable needs a runtime check, which was
   not performed. Birch hands over every TM, HM and Move Compendium at the
   start, so the Rock Smash (required pre-Gym 1 for Dark Cave) is available.

5. **v5.5's own Route 2 North table conflicts with the release schedule.**
   Route 2 North is a zero-badge LC area, but its authored table includes
   Voltorb, Koffing and Trapinch, all of which `plasticox_encounters_v1.md`
   releases at Gym 2. The table is left exactly as v5.5 specifies it, and the
   same three species were removed from Route 103 and Route 46 where v5.5 does
   not list them. The conflict is between the two documents, not inside the
   data, so no reconciliation was invented.

6. **Route 35's fishing table is Old Rod only.** `apply_pu_v1.py` writes
   `Route35OldRod` into all ten slots with weights `30/25/20/15/10/0/0/0/0/0`.
   Because a table carrying an explicit `weights` array bypasses the engine's
   rod-based slot selection (`TryGenerateWildMon` returns through
   `GenerateWeightedWildMon` as soon as `weights != NULL`), the Good Rod and
   Super Rod on Route 35 also draw from that five-species pool. The PU document
   only specifies the Old Rod for Route 35, so this matches the spec, but it is
   worth knowing that Route 35 has no separate Good/Super Rod pool.

7. **Five areas have Headbutt tables but no Headbutt tree.** `GetHeadbuttTable()`
   has cases for Route 24, Route 25, Route 29, Route 44 and Route 46 and
   `apply_pu_v1.py` builds all five tables, but the only maps carrying a
   `PlasticOx_EventScript_HeadbuttTree` object are Ilex Forest, Route 33,
   Route 35, Route 36 and National Park. The five tables are therefore
   unreachable in play — three of them (Route 24, Route 25, Route 44) have water
   and could in principle be reached, the other two are landlocked. Adding the
   tree objects is a map edit and is outside this task's scope, so the tables are
   left in place and wired up in `GetHeadbuttTable()` ready for a tree to be
   placed.

## 1.6 The pre-existing failing test

`plastic_ox/encounter_tables/test_pre_mt_moon_v4_4.py` compares the live data
against `apply_pre_mt_moon_v4_4.py`, which parses the superseded v4.4 document
and maps "Route 2 South" and "Route 2 North" onto `MAP_ROUTE1` and `MAP_ROUTE2`.
It has been failing since the v5.5 migration — verified by stashing this task's
encounter changes and re-running it, which still failed on `MAP_PALLET_TOWN`.
It also asserts `2 <= len(mons) <= 4` for ten route trainers, which Part 2
invalidates by design.

It is replaced by `test_pre_mt_moon_v5_5.py`, which checks the same ground
against the document that is actually authoritative and adds the v5.5
non-negotiable invariants. The stale file is left in place rather than deleted
so the history stays discoverable; the new test is the one to run.

---

# Part 2 — Trainer teams

## 2.1 What was changed

68 of the 71 `TRAINER_PLASTIC_OX_*`
trainers were rewritten; the other 3 are untouched for stated
reasons. Every rewritten party now has exactly six Pokémon — 408 Pokémon in
total, up from 213 before.

* `src/data/trainers.party` is the only file edited for part 2. The 855
  non-Plastic-Ox trainer entries are byte-for-byte identical, and the
  `Name`/`Class`/`Pic`/`Gender`/`Music`/`Double Battle`/`AI` header block of every
  Plastic-Ox trainer is byte-for-byte identical too — `trainer_headers_baseline.json`
  records them and the test asserts against it.
* No map script, object event, or dialogue was touched. `src/data/trainers.h`
  is regenerated by trainerproc from the `.party` file.
* `TRAINER_PLASTIC_OX_LANCE` and `TRAINER_PLASTIC_OX_ROXANNE` keep their ids,
  as `sMetamonTrainers[]` in `src/metamon_trainer.c` requires.

## 2.2 The rules, and how each is enforced

| Rule | Enforcement |
|---|---|
| Exactly six Pokémon | Checked in the test by re-parsing the `.party` file. |
| Species obtainable at or before the trainer's story checkpoint | `pox_progression.obtainable_at()` walks the ordered checkpoint spine, adding each area's wild and Headbutt species plus special acquisitions, then closes it under the repo's own evolution data (`src/data/pokemon/species_info/*.h`) — level evolutions must land at or under the stage's level cap, item evolutions need a stone the stage has released, and friendship/trade/time-of-day triggers count as reachable. |
| Levels follow the story cap table | Each roster entry carries six explicit levels; the test asserts none exceeds `pox_progression.cap_at(checkpoint)`, which is the `plasticox_evolution_gating_plan_v1.md` ladder (13/20/30/36/42/50/55/60). |
| Tier gating | `pox_progression.legal_for()` drops any species whose tier in `src/data/pokemon/evolution_tier_gates.h` is still locked. The tier unlocks *during* its own gym segment, as the evolution-gating plan's as-built notes record. |
| Competitive sets | Taken from `plastic_ox/gen3_movesets.json` whenever the merged dex for the stage's tier has the species: **245 of 408**. The remaining 163 are early-route species with no tier-dex entry and are derived from the ROM's own learnset. |
| Move legality | Every move is re-checked against `src/data/pokemon/teachable_learnsets.h` (the per-species TM/HM/tutor list the repo generates from its own `tms_hms.h`) and the level-up learnsets, with the level taken into account. Because Birch hands the player the whole TM/HM/Compendium set in the opening scene, any teachable move is legal at any level; anything else must have been reached by level-up. |

### The v5.5 LC-block exception

`plasticox_encounters_v1.md` releases Voltorb, Koffing, Trapinch, Cubone, Rhyhorn,
Doduo, Slugma, Corsola, Poliwhirl, Kingler, Seadra, Seaking, Tentacool, Pineco,
Anorith, Lileep and Kabuto at Gym 2, yet the v5.5 document deliberately places
several of them in the zero-badge LC block. Since the encounter specification is
the authoritative statement of what the player can hold before Gym 1, those
species are admitted for trainers in the Gym 1 segment
(`pox_progression.legal_for()`), which is also what makes the reference
`TRAINER_PLASTIC_OX_ROXANNE` party legal. This is recorded here because it is a
deliberate reconciliation of two documents, not an oversight.

### Level-cap and NU ceiling

The story cap rises to 60 by Gym 8, but the obtainable species pool stops at
NU. That is a direct consequence of gap 1.5.2: the RU, UU, UUBL and OU encounter
lines the progression document describes (Stantler, Sneasel, Mantine, Mr. Mime,
Absol; Kangaskhan, Scyther, Pinsir, Lapras, Misdreavus, Girafarig, Gligar,
Qwilfish, Lunatone, Solrock; Chansey, Tauros, Articuno, Smeargle, Miltank,
Entei, Zangoose, Regirock; Skarmory, Blissey, Snorlax, Heracross, the legendary
birds, the Regis) have no encounter table, gift or fossil anywhere in the ROM.
Evolution covers a good deal of the gap — Clefable, Ninetales, Politoed, Rapidash,
Electrode, Magneton, Golem, Nidoqueen, Nidoking, Vileplume, Rhydon, Jumpluff,
Ampharos, Tentacruel, Lanturn, Quagsire, Alakazam, Steelix, Machamp, Dusclops,
Dragonite, Kingdra, Gengar, Metagross, Tyranitar, Salamence, Starmie, Cloyster,
Flygon, Swampert and more are all reachable by the time the player has the
badges — which is why the later rosters are legal and competitive. But the pool
top outs out at 16 OU species (Charizard, Claydol, Cloyster, Flygon,
Forretress, Gengar, Gyarados, Jolteon, Magikarp, Magneton, Medicham, Metagross,
Salamence, Starmie, Swampert, Tyranitar) and 29 UUBL. The late rosters are
therefore drawn from the best species actually obtainable, at the level caps the
task specifies. This is a content gap in the encounter data, not a trainer-data
defect, and closing it means implementing the later-tier encounter blocks.

## 2.3 Per-trainer table

Conventions: the set name in brackets is the `gen3_movesets.json` set name;
*derived* marks a set built from the ROM learnset because the tier dex has no
entry for that species. Moves are listed in set order. "Availability" gives the
checkpoint reason the species is in the player's hands.

| Trainer id | Story stage | Cap | Team (level, species, set) | Availability |
|---|---|---:|---|---|
| `TRAINER_PLASTIC_OX_BILL` | postgame (OU) | 64 | Lv64 **Metagross** — Agility [Explosion, Meteor Mash, Earthquake, HP]<br>Lv64 **Starmie** — Offensive [Surf, Ice Beam, Thunderbolt, Rapid Spin]<br>Lv63 **Cloyster** — Spiker [Spikes, Surf, Explosion, HP]<br>Lv63 **Flygon** — Choice Band [Earthquake, Rock Slide, HP, Hyper Beam]<br>Lv63 **Swampert** — Standard Defensive [Earthquake, Ice Beam, Protect, Surf]<br>Lv64 **Charizard** — Mixed Attacker [Fire Blast, HP, Substitute, Focus Punch] | Metagross: evolves from Metang at Lv45 (OU)<br>Starmie: evolves from STARYU (Water_Stone) (OU)<br>Cloyster: evolves from SHELLDER (Water_Stone) (OU)<br>Flygon: evolves from Vibrava at Lv45 (OU)<br>Swampert: evolves from Marshtomp at Lv36 (OU)<br>Charizard: evolves from Charmeleon at Lv36 (OU) |
| `TRAINER_PLASTIC_OX_BLAINE` | cinnabar (UU) | 42 | Lv42 **Ninetales** — learnset-derived *(derived)* [Flamethrower, Fire Blast, HP, Toxic]<br>Lv42 **Arcanine** — Sunny Day [Fire Blast, HP, Sunny Day, Hyper Beam]<br>Lv41 **Rapidash** — SunnyBeam [Sunny Day, Solar Beam, Flamethrower, Hyper Beam]<br>Lv40 **Electrode** — Substitute [Thunderbolt, Substitute, Explosion, HP]<br>Lv41 **Muk** — SubPunch [Sludge Bomb, Substitute, Focus Punch, HP]<br>Lv40 **Tentacruel** — Utility [Hyper Beam, Surf, Toxic, Ice Beam] | Ninetales: evolves from VULPIX (Fire_Stone) (RU)<br>Arcanine: evolves from GROWLITHE (Fire_Stone) (UU)<br>Rapidash: evolves from Ponyta at Lv36 (RU)<br>Electrode: evolves from Voltorb at Lv30 (UU)<br>Muk: evolves from Grimer at Lv38 (UU)<br>Tentacruel: evolves from Tentacool at Lv30 (UU) |
| `TRAINER_PLASTIC_OX_BLUE` | postgame (OU) | 64 | Lv64 **Tyranitar** — Bulky Dragon Dance [Hyper Beam, Rock Slide, Earthquake, HP]<br>Lv64 **Salamence** — Dragon Dance [Hyper Beam, HP, Rock Slide, Earthquake]<br>Lv64 **Metagross** — Agility [Explosion, Meteor Mash, Earthquake, HP]<br>Lv63 **Gengar** — Offensive [Thunderbolt, Ice Punch, HP, Explosion]<br>Lv64 **Gyarados** — Rest [Dragon Dance, HP, Earthquake, Rest]<br>Lv63 **Forretress** — Standard [Spikes, Rapid Spin, HP, Earthquake] | Tyranitar: evolves from Pupitar at Lv55 (OU)<br>Salamence: evolves from Shelgon at Lv50 (OU)<br>Metagross: evolves from Metang at Lv45 (OU)<br>Gengar: evolves from HAUNTER (trade) (OU)<br>Gyarados: evolves from Magikarp at Lv20 (OU)<br>Forretress: evolves from Pineco at Lv31 (OU) |
| `TRAINER_PLASTIC_OX_BRUNO` | mossdeep (UUBL) | 50 | Lv50 **Rhydon** — Substitute [Earthquake, Swords Dance, Rock Slide, Substitute]<br>Lv50 **Golem** — Choice Band [Earthquake, Rock Slide, HP, Explosion]<br>Lv49 **Machamp** — Choice Band [Cross Chop, Rock Slide, Focus Punch, HP]<br>Lv49 **Hariyama** — Defensive Knock Off [Knock Off, Brick Break, Rest, HP]<br>Lv48 **Donphan** — Tank [Earthquake, HP, Rest, Rapid Spin]<br>Lv48 **Steelix** — Choice Band [Earthquake, Iron Tail, Double-Edge, Explosion] | Rhydon: evolves from Rhyhorn at Lv42 (UUBL)<br>Golem: evolves from GRAVELER (trade) (UU)<br>Machamp: evolves from MACHOKE (trade) (UUBL)<br>Hariyama: evolves from Makuhita at Lv24 (UUBL)<br>Donphan: evolves from Phanpy at Lv25 (UUBL)<br>Steelix: evolves from ONIX (Metal_Coat) (UUBL) |
| `TRAINER_PLASTIC_OX_CLAIR` | blackthorn (OU) | 60 | Lv59 **Gyarados** — Rest [Dragon Dance, HP, Earthquake, Rest]<br>Lv58 **Jolteon** — Standard [Thunderbolt, HP, Hyper Beam, Roar]<br>Lv58 **Swampert** — Surf Defensive [Surf, Toxic, Protect, Hyper Beam]<br>Lv59 **Tyranitar** — Fast Dragon Dance [Hyper Beam, Rock Slide, Earthquake, HP]<br>Lv58 **Medicham** — All-Out Attacker [Brick Break, Focus Punch, Substitute, Shadow Ball]<br>Lv58 **Flygon** — Offensive [Earthquake, Rock Slide, HP, Substitute] | Gyarados: evolves from Magikarp at Lv20 (OU)<br>Jolteon: evolves from EEVEE (Thunder_Stone) (OU)<br>Swampert: evolves from Marshtomp at Lv36 (OU)<br>Tyranitar: evolves from Pupitar at Lv55 (OU)<br>Medicham: evolves from Meditite at Lv37 (OU)<br>Flygon: evolves from Vibrava at Lv45 (OU) |
| `TRAINER_PLASTIC_OX_GIOVANNI` | saffron (OU) | 55 | Lv55 **Tyranitar** — Fast Dragon Dance [Hyper Beam, Rock Slide, Earthquake, HP]<br>Lv55 **Salamence** — Dragon Dance [Hyper Beam, HP, Rock Slide, Earthquake]<br>Lv55 **Metagross** — Bulky Attacker [Meteor Mash, Earthquake, Protect, Explosion]<br>Lv54 **Forretress** — Standard [Spikes, Rapid Spin, HP, Earthquake]<br>Lv53 **Gengar** — Utility [Hypnosis, Explosion, Ice Punch, Thunderbolt]<br>Lv54 **Starmie** — Defensive [Rapid Spin, Recover, Surf, Thunder Wave] | Tyranitar: evolves from Pupitar at Lv55 (OU)<br>Salamence: evolves from Shelgon at Lv50 (OU)<br>Metagross: evolves from Metang at Lv45 (OU)<br>Forretress: evolves from Pineco at Lv31 (OU)<br>Gengar: evolves from HAUNTER (trade) (OU)<br>Starmie: evolves from STARYU (Water_Stone) (OU) |
| `TRAINER_PLASTIC_OX_KIMONOESPEON` | gym3 (NU) | 30 | Lv26 **Espeon** — learnset-derived *(derived)* [Psychic, Dream Eater, HP, Toxic]<br>Lv23 **Meditite** — Offensive Sub [Substitute, Brick Break, Shadow Ball, Toxic]<br>Lv23 **Meowth** — Lead [Thunder, Double-Edge, Shadow Ball, Taunt]<br>Lv24 **Kirlia** — learnset-derived *(derived)* [Psychic, Dream Eater, HP, Toxic]<br>Lv24 **Slowpoke** — learnset-derived *(derived)* [Surf, Psychic, HP, Toxic]<br>Lv23 **Natu** — learnset-derived *(derived)* [Psychic, Aerial Ace, HP, Toxic] | **Espeon: declared signature exception** (UUBL — see 2.5)<br>Meditite: wild / special acquisition (PU)<br>Meowth: wild / special acquisition (LC)<br>Kirlia: evolves from Ralts at Lv20 (PU)<br>Slowpoke: wild / special acquisition (LC)<br>Natu: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_KIMONOFLAREON` | gym3 (NU) | 30 | Lv26 **Flareon** — Special Attacker [Fire Blast, HP, Substitute, Hyper Beam]<br>Lv22 **Vulpix** — learnset-derived *(derived)* [Flamethrower, Fire Blast, HP, Toxic]<br>Lv23 **Growlithe** — learnset-derived *(derived)* [Flamethrower, Fire Blast, HP, Toxic]<br>Lv24 **Arbok** — Choice Band [Sludge Bomb, Earthquake, Rock Slide, Sleep Talk]<br>Lv23 **Meowth** — Lead [Thunder, Double-Edge, Shadow Ball, Taunt]<br>Lv24 **Delibird** — Choice Band [Ice Beam, Focus Punch, Aerial Ace, HP] | Flareon: evolves from EEVEE (Fire_Stone) (NU)<br>Vulpix: wild / special acquisition (LC)<br>Growlithe: wild / special acquisition (LC)<br>Arbok: evolves from Ekans at Lv20 (PU)<br>Meowth: wild / special acquisition (LC)<br>Delibird: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_KIMONOJOLTEON` | gym3 (NU) | 30 | Lv26 **Jolteon** — learnset-derived *(derived)* [Thunderbolt, Thunder, HP, Toxic]<br>Lv23 **Elekid** — Substitute + 3 Attacks [Thunderbolt, Ice Punch, Thief, Substitute]<br>Lv23 **Electrike** — learnset-derived *(derived)* [Thunderbolt, Thunder, HP, Toxic]<br>Lv24 **Voltorb** — Suicide Rain Lead [Rain Dance, Thunder, Light Screen, Explosion]<br>Lv23 **Magnemite** — Offensive Utility [Thunderbolt, HP, Toxic, Substitute]<br>Lv24 **Skitty** — learnset-derived *(derived)* [HP, Body Slam, Thunderbolt, Toxic] | **Jolteon: declared signature exception** (OU — see 2.5)<br>Elekid: wild / special acquisition (PU)<br>Electrike: wild / special acquisition (LC)<br>Voltorb: wild / special acquisition (PU)<br>Magnemite: wild / special acquisition (PU)<br>Skitty: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_KIMONOUMBREON` | gym3 (NU) | 30 | Lv26 **Umbreon** — learnset-derived *(derived)* [Pursuit, HP, Psychic, Toxic]<br>Lv23 **Spoink** — Lead [Thief, Psychic, Icy Wind, Taunt]<br>Lv24 **Houndour** — learnset-derived *(derived)* [Flamethrower, Fire Blast, HP, Toxic]<br>Lv24 **Duskull** — Defensive [Rest, Sleep Talk, Blizzard, Night Shade]<br>Lv23 **Meowth** — Lead [Thunder, Double-Edge, Shadow Ball, Taunt]<br>Lv24 **Nidoran♂** — learnset-derived *(derived)* [Sludge Bomb, Poison Sting, HP, Toxic] | **Umbreon: declared signature exception** (UUBL — see 2.5)<br>Spoink: wild / special acquisition (LC)<br>Houndour: wild / special acquisition (PU)<br>Duskull: wild / special acquisition (PU)<br>Meowth: wild / special acquisition (LC)<br>Nidoran♂: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_KIMONOVAPOREON` | gym3 (NU) | 30 | Lv26 **Vaporeon** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic]<br>Lv23 **Psyduck** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic]<br>Lv23 **Seel** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic]<br>Lv24 **Staryu** — Offensive Utility [Surf, Thunderbolt, Ice Beam, HP]<br>Lv24 **Slowpoke** — learnset-derived *(derived)* [Surf, Psychic, HP, Toxic]<br>Lv24 **Tentacool** — Specially Defensive [Blizzard, Surf, Toxic, HP] | **Vaporeon: declared signature exception** (UUBL — see 2.5)<br>Psyduck: wild / special acquisition (LC)<br>Seel: wild / special acquisition (LC)<br>Staryu: wild / special acquisition (LC)<br>Slowpoke: wild / special acquisition (LC)<br>Tentacool: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_LEAGUELANCE` | league (OU) | 62 | Lv62 **Gyarados** — Standard [Dragon Dance, HP, Earthquake, Double-Edge]<br>Lv62 **Starmie** — Defensive [Rapid Spin, Recover, Surf, Thunder Wave]<br>Lv62 **Charizard** — Mixed Attacker [Fire Blast, HP, Substitute, Focus Punch]<br>Lv61 **Claydol** — Utility [Rapid Spin, Earthquake, Psychic, Explosion]<br>Lv61 **Medicham** — Bulk Up [Bulk Up, Brick Break, Shadow Ball, Recover]<br>Lv62 **Swampert** — Substitute + Salac Berry [Substitute, Endeavor, Surf, Roar] | Gyarados: evolves from Magikarp at Lv20 (OU)<br>Starmie: evolves from STARYU (Water_Stone) (OU)<br>Charizard: evolves from Charmeleon at Lv36 (OU)<br>Claydol: evolves from Baltoy at Lv36 (OU)<br>Medicham: evolves from Meditite at Lv37 (OU)<br>Swampert: evolves from Marshtomp at Lv36 (OU) |
| `TRAINER_PLASTIC_OX_MOONGRUNT1` | mtmoondeep (PU) | 20 | Lv16 **Cubone** — Offensive [Focus Punch, Double-Edge, HP, Protect]<br>Lv16 **Machop** — Offensive [Bulk Up, Focus Punch, HP, Endure]<br>Lv16 **Arbok** — Choice Band [Sludge Bomb, Earthquake, HP, Rock Slide]<br>Lv15 **Aron** — learnset-derived *(derived)* [Rock Slide, Rock Tomb, HP, Toxic]<br>Lv16 **Duskull** — Defensive [Rest, Sleep Talk, Blizzard, Night Shade]<br>Lv15 **Ekans** — learnset-derived *(derived)* [Sludge Bomb, Poison Sting, HP, Toxic] | Cubone: wild / special acquisition (PU)<br>Machop: wild / special acquisition (LC)<br>Arbok: evolves from Ekans at Lv20 (PU)<br>Aron: wild / special acquisition (LC)<br>Duskull: wild / special acquisition (PU)<br>Ekans: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_MOONGRUNT2` | mtmoondeep (PU) | 20 | Lv16 **Magnemite** — Offensive Utility [Thunderbolt, HP, Toxic, Substitute]<br>Lv16 **Voltorb** — Offensive [Thunderbolt, HP, Thief, Explosion]<br>Lv16 **Onix** — All-Out Attacker [Rock Slide, Earthquake, Double-Edge, Explosion]<br>Lv16 **Rhyhorn** — learnset-derived *(derived)* [Earthquake, Rock Slide, HP, Toxic]<br>Lv16 **Gloom** — learnset-derived *(derived)* [Giga Drain, Sludge Bomb, HP, Toxic]<br>Lv16 **Mareep** — learnset-derived *(derived)* [Thunderbolt, Thunder, HP, Toxic] | Magnemite: wild / special acquisition (PU)<br>Voltorb: wild / special acquisition (PU)<br>Onix: wild / special acquisition (LC)<br>Rhyhorn: wild / special acquisition (PU)<br>Gloom: evolves from Oddish at Lv20 (PU)<br>Mareep: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_MOON_BUG_CATCHER_KENT` | mtmoon (PU) | 20 | Lv12 **Paras** — learnset-derived *(derived)* [Giga Drain, Solar Beam, HP, Toxic]<br>Lv12 **Venonat** — learnset-derived *(derived)* [Sludge Bomb, HP, Giga Drain, Toxic]<br>Lv12 **Nincada** — learnset-derived *(derived)* [Leech Life, Mud-Slap, HP, Toxic]<br>Lv12 **Oddish** — Sunny Day [Sunny Day, Solar Beam, HP, Bullet Seed]<br>Lv12 **Spinarak** — learnset-derived *(derived)* [Sludge Bomb, Poison Sting, HP, Toxic]<br>Lv12 **Exeggcute** — Sunny Day Sweeper [Explosion, Sunny Day, Solar Beam, Psychic] | Paras: wild / special acquisition (LC)<br>Venonat: wild / special acquisition (LC)<br>Nincada: wild / special acquisition (LC)<br>Oddish: wild / special acquisition (LC)<br>Spinarak: wild / special acquisition (LC)<br>Exeggcute: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_MOON_BUG_CATCHER_ROBBY` | mtmoondeep (PU) | 20 | Lv14 **Nincada** — learnset-derived *(derived)* [Leech Life, Mud-Slap, HP, Toxic]<br>Lv14 **Paras** — learnset-derived *(derived)* [Giga Drain, Solar Beam, HP, Toxic]<br>Lv14 **Venonat** — learnset-derived *(derived)* [Sludge Bomb, HP, Giga Drain, Toxic]<br>Lv14 **Oddish** — Sunny Day [Sunny Day, Solar Beam, HP, Bullet Seed]<br>Lv13 **Pineco** — learnset-derived *(derived)* [HP, Giga Drain, Toxic, Earthquake]<br>Lv14 **Exeggcute** — Sunny Day Sweeper [Explosion, Sunny Day, Solar Beam, Psychic] | Nincada: wild / special acquisition (LC)<br>Paras: wild / special acquisition (LC)<br>Venonat: wild / special acquisition (LC)<br>Oddish: wild / special acquisition (LC)<br>Pineco: wild / special acquisition (PU)<br>Exeggcute: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_MOON_HIKER_MARCOS` | mtmoon (PU) | 20 | Lv13 **Machop** — Offensive [Bulk Up, Focus Punch, HP, Endure]<br>Lv13 **Geodude** — learnset-derived *(derived)* [Earthquake, Rock Slide, HP, Toxic]<br>Lv13 **Onix** — All-Out Attacker [Rock Slide, Earthquake, Double-Edge, Explosion]<br>Lv13 **Aron** — learnset-derived *(derived)* [Rock Slide, Rock Tomb, HP, Toxic]<br>Lv12 **Sandshrew** — learnset-derived *(derived)* [Earthquake, Mud-Slap, HP, Toxic]<br>Lv12 **Numel** — Lead [Earthquake, Fire Blast, Toxic, Protect] | Machop: wild / special acquisition (LC)<br>Geodude: wild / special acquisition (LC)<br>Onix: wild / special acquisition (LC)<br>Aron: wild / special acquisition (LC)<br>Sandshrew: wild / special acquisition (LC)<br>Numel: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_MOON_LASS_IRIS` | mtmoondeep (PU) | 20 | Lv15 **Meowth** — Lead [Thunder, Double-Edge, Shadow Ball, Taunt]<br>Lv15 **Cleffa** — learnset-derived *(derived)* [HP, Flamethrower, Toxic, Psychic]<br>Lv15 **Sentret** — learnset-derived *(derived)* [HP, Body Slam, Surf, Toxic]<br>Lv14 **Taillow** — learnset-derived *(derived)* [HP, Aerial Ace, Mud-Slap, Toxic]<br>Lv15 **Skitty** — learnset-derived *(derived)* [HP, Body Slam, Thunderbolt, Toxic]<br>Lv14 **Snorunt** — Spikes [Blizzard, Ice Beam, Endure, HP] | Meowth: wild / special acquisition (LC)<br>Cleffa: wild / special acquisition (LC)<br>Sentret: wild / special acquisition (LC)<br>Taillow: wild / special acquisition (LC)<br>Skitty: wild / special acquisition (LC)<br>Snorunt: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_MOON_LASS_MIRIAM` | mtmoon (PU) | 20 | Lv13 **Cleffa** — learnset-derived *(derived)* [HP, Flamethrower, Toxic, Psychic]<br>Lv13 **Meowth** — Lead [Thunder, Double-Edge, Shadow Ball, Taunt]<br>Lv13 **Sentret** — learnset-derived *(derived)* [HP, Body Slam, Surf, Toxic]<br>Lv12 **Taillow** — learnset-derived *(derived)* [HP, Aerial Ace, Mud-Slap, Toxic]<br>Lv12 **Lotad** — learnset-derived *(derived)* [Surf, Giga Drain, HP, Toxic]<br>Lv12 **Sunkern** — learnset-derived *(derived)* [Giga Drain, Solar Beam, HP, Toxic] | Cleffa: wild / special acquisition (LC)<br>Meowth: wild / special acquisition (LC)<br>Sentret: wild / special acquisition (LC)<br>Taillow: wild / special acquisition (LC)<br>Lotad: wild / special acquisition (LC)<br>Sunkern: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_MOON_SUPER_NERD_JOVAN` | mtmoon (PU) | 20 | Lv12 **Magnemite** — Offensive Utility [Thunderbolt, HP, Toxic, Substitute]<br>Lv12 **Spoink** — Lead [Thief, Psychic, Icy Wind, Taunt]<br>Lv12 **Baltoy** — All-Out Attacker [Earthquake, Shadow Ball, Rock Tomb, Explosion]<br>Lv12 **Natu** — learnset-derived *(derived)* [Psychic, Aerial Ace, HP, Toxic]<br>Lv12 **Exeggcute** — Sunny Day Sweeper [Explosion, Sunny Day, Solar Beam, Psychic]<br>Lv11 **Elekid** — Mixed Attacker [Thunderbolt, Ice Punch, HP, Substitute] | Magnemite: wild / special acquisition (PU)<br>Spoink: wild / special acquisition (LC)<br>Baltoy: wild / special acquisition (LC)<br>Natu: wild / special acquisition (LC)<br>Exeggcute: wild / special acquisition (LC)<br>Elekid: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_MOON_SUPER_NERD_MIGUEL` | mtmoondeep (PU) | 20 | Lv15 **Magnemite** — Offensive Utility [Thunderbolt, HP, Toxic, Substitute]<br>Lv15 **Spoink** — Lead [Thief, Psychic, Icy Wind, Taunt]<br>Lv15 **Baltoy** — All-Out Attacker [Earthquake, Shadow Ball, Rock Tomb, Explosion]<br>Lv15 **Natu** — learnset-derived *(derived)* [Psychic, Aerial Ace, HP, Toxic]<br>Lv15 **Exeggcute** — Sunny Day Sweeper [Explosion, Sunny Day, Solar Beam, Psychic]<br>Lv15 **Elekid** — Substitute + 3 Attacks [Thunderbolt, Ice Punch, Thief, Substitute] | Magnemite: wild / special acquisition (PU)<br>Spoink: wild / special acquisition (LC)<br>Baltoy: wild / special acquisition (LC)<br>Natu: wild / special acquisition (LC)<br>Exeggcute: wild / special acquisition (LC)<br>Elekid: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT` | mtmoon (PU) | 20 | Lv14 **Cubone** — Offensive [Focus Punch, Double-Edge, HP, Protect]<br>Lv14 **Voltorb** — Offensive [Thunderbolt, HP, Thief, Explosion]<br>Lv13 **Koffing** — Defensive [Sludge Bomb, HP, Thief, Explosion]<br>Lv14 **Machop** — Offensive [Bulk Up, Focus Punch, HP, Endure]<br>Lv14 **Duskull** — Defensive [Rest, Sleep Talk, Blizzard, Night Shade]<br>Lv13 **Ekans** — learnset-derived *(derived)* [Sludge Bomb, Poison Sting, HP, Toxic] | Cubone: wild / special acquisition (PU)<br>Voltorb: wild / special acquisition (PU)<br>Koffing: wild / special acquisition (PU)<br>Machop: wild / special acquisition (LC)<br>Duskull: wild / special acquisition (PU)<br>Ekans: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT_2` | mtmoon (PU) | 20 | Lv13 **Magnemite** — Offensive Utility [Thunderbolt, HP, Toxic, Substitute]<br>Lv13 **Voltorb** — Offensive [Thunderbolt, HP, Thief, Explosion]<br>Lv13 **Cubone** — Offensive [Focus Punch, Double-Edge, HP, Protect]<br>Lv13 **Koffing** — Defensive [Sludge Bomb, HP, Thief, Explosion]<br>Lv12 **Drowzee** — learnset-derived *(derived)* [Psychic, Dream Eater, HP, Toxic]<br>Lv13 **Gastly** — Stallbreaker [Psychic, Thunderbolt, Taunt, Explosion] | Magnemite: wild / special acquisition (PU)<br>Voltorb: wild / special acquisition (PU)<br>Cubone: wild / special acquisition (PU)<br>Koffing: wild / special acquisition (PU)<br>Drowzee: wild / special acquisition (PU)<br>Gastly: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT_3` | mtmoondeep (PU) | 20 | Lv15 **Cubone** — Offensive [Focus Punch, Double-Edge, HP, Protect]<br>Lv15 **Machop** — Offensive [Bulk Up, Focus Punch, HP, Endure]<br>Lv15 **Rhyhorn** — learnset-derived *(derived)* [Earthquake, Rock Slide, HP, Toxic]<br>Lv14 **Aron** — learnset-derived *(derived)* [Rock Slide, Rock Tomb, HP, Toxic]<br>Lv15 **Duskull** — Defensive [Rest, Sleep Talk, Blizzard, Night Shade]<br>Lv14 **Ekans** — learnset-derived *(derived)* [Sludge Bomb, Poison Sting, HP, Toxic] | Cubone: wild / special acquisition (PU)<br>Machop: wild / special acquisition (LC)<br>Rhyhorn: wild / special acquisition (PU)<br>Aron: wild / special acquisition (LC)<br>Duskull: wild / special acquisition (PU)<br>Ekans: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT_4` | mtmoondeep (PU) | 20 | Lv15 **Voltorb** — Offensive [Thunderbolt, HP, Thief, Explosion]<br>Lv15 **Magnemite** — Offensive Utility [Thunderbolt, HP, Toxic, Substitute]<br>Lv14 **Koffing** — Defensive [Sludge Bomb, HP, Thief, Explosion]<br>Lv15 **Onix** — All-Out Attacker [Rock Slide, Earthquake, Double-Edge, Explosion]<br>Lv15 **Drowzee** — learnset-derived *(derived)* [Psychic, Dream Eater, HP, Toxic]<br>Lv15 **Duskull** — Defensive [Rest, Sleep Talk, Blizzard, Night Shade] | Voltorb: wild / special acquisition (PU)<br>Magnemite: wild / special acquisition (PU)<br>Koffing: wild / special acquisition (PU)<br>Onix: wild / special acquisition (LC)<br>Drowzee: wild / special acquisition (PU)<br>Duskull: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_MOON_YOUNGSTER_JOSH` | mtmoon (PU) | 20 | Lv12 **Mankey** — Substitute + Reversal [Focus Punch, HP, Substitute, Endure]<br>Lv12 **Meowth** — Lead [Thunder, Double-Edge, Shadow Ball, Taunt]<br>Lv12 **Snorunt** — Spikes [Blizzard, Ice Beam, Endure, HP]<br>Lv12 **Machop** — Offensive [Bulk Up, Focus Punch, HP, Endure]<br>Lv12 **Ekans** — learnset-derived *(derived)* [Sludge Bomb, Poison Sting, HP, Toxic]<br>Lv12 **Cacnea** — learnset-derived *(derived)* [Giga Drain, Solar Beam, HP, Toxic] | Mankey: wild / special acquisition (LC)<br>Meowth: wild / special acquisition (LC)<br>Snorunt: wild / special acquisition (LC)<br>Machop: wild / special acquisition (LC)<br>Ekans: wild / special acquisition (LC)<br>Cacnea: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_MORTY` | gym3 (NU) | 30 | Lv30 **Sudowoodo** — Choice Band [Rock Slide, Earthquake, Focus Punch, Explosion]<br>Lv29 **Haunter** — Standard [Psychic, Thunderbolt, Substitute, Explosion]<br>Lv28 **Gastly** — Stallbreaker [Psychic, Thunderbolt, Taunt, Explosion]<br>Lv28 **Duskull** — Defensive [Rest, Sleep Talk, Blizzard, Night Shade]<br>Lv28 **Golbat** — Bulky Leftovers [Sludge Bomb, Aerial Ace, HP, Toxic]<br>Lv27 **Wigglytuff** — Special Attacker [Ice Beam, Thunderbolt, Fire Blast, Hyper Beam] | Sudowoodo: wild / special acquisition (NU)<br>Haunter: evolves from Gastly at Lv25 (NU)<br>Gastly: wild / special acquisition (PU)<br>Duskull: wild / special acquisition (PU)<br>Golbat: evolves from Zubat at Lv22 (NU)<br>Wigglytuff: evolves from JIGGLYPUFF (Moon_Stone) (PU) |
| `TRAINER_PLASTIC_OX_PU_PARK` | park (NU) | 30 | Lv20 **Lickitung** — learnset-derived *(derived)* [HP, Body Slam, Surf, Toxic]<br>Lv20 **Jigglypuff** — learnset-derived *(derived)* [HP, Thunderbolt, Toxic, Flamethrower]<br>Lv20 **Tropius** — Swords Dance [Swords Dance, HP, Earthquake, Substitute]<br>Lv20 **Hoppip** — learnset-derived *(derived)* [Giga Drain, Aerial Ace, HP, Toxic]<br>Lv20 **Nidoran♀** — learnset-derived *(derived)* [Sludge Bomb, Poison Sting, HP, Toxic]<br>Lv19 **Ledyba** — learnset-derived *(derived)* [Aerial Ace, HP, Giga Drain, Toxic] | Lickitung: wild / special acquisition (PU)<br>Jigglypuff: wild / special acquisition (PU)<br>Tropius: wild / special acquisition (PU)<br>Hoppip: wild / special acquisition (LC)<br>Nidoran♀: wild / special acquisition (LC)<br>Ledyba: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_PU_ROUTE33` | route33 (PU) | 20 | Lv17 **Spinda** — learnset-derived *(derived)* [HP, Body Slam, Rock Slide, Toxic]<br>Lv16 **Seviper** — Mixed Breaker [Sludge Bomb, Earthquake, Giga Drain, Bite]<br>Lv17 **Zigzagoon** — learnset-derived *(derived)* [HP, Body Slam, Surf, Toxic]<br>Lv16 **Hoppip** — learnset-derived *(derived)* [Giga Drain, Aerial Ace, HP, Toxic]<br>Lv16 **Aipom** — learnset-derived *(derived)* [HP, Body Slam, Thunderbolt, Toxic]<br>Lv16 **Geodude** — learnset-derived *(derived)* [Earthquake, Rock Slide, HP, Toxic] | Spinda: wild / special acquisition (PU)<br>Seviper: wild / special acquisition (PU)<br>Zigzagoon: wild / special acquisition (PU)<br>Hoppip: wild / special acquisition (LC)<br>Aipom: wild / special acquisition (PU)<br>Geodude: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_PU_ROUTE35` | route35 (NU) | 30 | Lv19 **Abra** — Calm Mind [Calm Mind, Psychic, Fire Punch, Substitute]<br>Lv19 **Farfetch'd** — Swords Dance + Flail [Substitute, Iron Tail, HP, Swords Dance]<br>Lv19 **Yanma** — Substitute + Reversal [Substitute, Solar Beam, HP, Protect]<br>Lv19 **Minun** — learnset-derived *(derived)* [Thunderbolt, Thunder Punch, HP, Toxic]<br>Lv19 **Drowzee** — learnset-derived *(derived)* [Psychic, Dream Eater, HP, Toxic]<br>Lv19 **Corsola** — Special Attacker [Recover, Surf, Ice Beam, Toxic] | Abra: wild / special acquisition (PU)<br>Farfetch'd: wild / special acquisition (PU)<br>Yanma: wild / special acquisition (PU)<br>Minun: wild / special acquisition (PU)<br>Drowzee: wild / special acquisition (PU)<br>Corsola: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_PU_ROUTE36` | route36 (NU) | 30 | Lv21 **Tangela** — Sunny Day Sweeper [Sunny Day, Sleep Powder, Solar Beam, HP]<br>Lv21 **Vulpix** — learnset-derived *(derived)* [Flamethrower, Fire Blast, HP, Toxic]<br>Lv21 **Drowzee** — learnset-derived *(derived)* [Psychic, Dream Eater, HP, Toxic]<br>Lv21 **Bellsprout** — Sunny Day Sweeper [Sunny Day, Solar Beam, HP, Sludge Bomb]<br>Lv21 **Natu** — learnset-derived *(derived)* [Psychic, Aerial Ace, HP, Toxic]<br>Lv21 **Baltoy** — All-Out Attacker [Earthquake, Shadow Ball, Rock Tomb, Explosion] | Tangela: wild / special acquisition (PU)<br>Vulpix: wild / special acquisition (LC)<br>Drowzee: wild / special acquisition (PU)<br>Bellsprout: wild / special acquisition (LC)<br>Natu: wild / special acquisition (LC)<br>Baltoy: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE1` | route2south (LC) | 13 | Lv6 **Mankey** — Substitute + Reversal [Focus Punch, HP, Substitute, Endure]<br>Lv6 **Ekans** — learnset-derived *(derived)* [Sludge Bomb, HP, Giga Drain, Toxic]<br>Lv6 **Growlithe** — learnset-derived *(derived)* [Flamethrower, Fire Blast, HP, Toxic]<br>Lv5 **Vulpix** — learnset-derived *(derived)* [Flamethrower, Fire Blast, HP, Toxic]<br>Lv5 **Meowth** — Lead [Thunder, Double-Edge, Shadow Ball, Taunt]<br>Lv6 **Slowpoke** — learnset-derived *(derived)* [Surf, Psychic, HP, Toxic] | Mankey: wild / special acquisition (LC)<br>Ekans: wild / special acquisition (LC)<br>Growlithe: wild / special acquisition (LC)<br>Vulpix: wild / special acquisition (LC)<br>Meowth: wild / special acquisition (LC)<br>Slowpoke: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE101` | start (LC) | 13 | Lv4 **Taillow** — learnset-derived *(derived)* [HP, Aerial Ace, Mud-Slap, Toxic]<br>Lv3 **Poochyena** — learnset-derived *(derived)* [Thief, HP, Shadow Ball, Toxic]<br>Lv3 **Goldeen** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic]<br>Lv3 **Lotad** — learnset-derived *(derived)* [Surf, Giga Drain, HP, Toxic]<br>Lv3 **Surskit** — learnset-derived *(derived)* [Water Pulse, Bubble, HP, Toxic]<br>Lv3 **Poliwag** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic] | Taillow: wild / special acquisition (LC)<br>Poochyena: wild / special acquisition (LC)<br>Goldeen: wild / special acquisition (LC)<br>Lotad: wild / special acquisition (LC)<br>Surskit: wild / special acquisition (LC)<br>Poliwag: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE103` | route103 (LC) | 13 | Lv5 **Wingull** — learnset-derived *(derived)* [Aerial Ace, Water Pulse, HP, Toxic]<br>Lv5 **Whismur** — learnset-derived *(derived)* [HP, Body Slam, Flamethrower, Toxic]<br>Lv5 **Electrike** — learnset-derived *(derived)* [Thunderbolt, Thunder, HP, Toxic]<br>Lv5 **Cacnea** — learnset-derived *(derived)* [Giga Drain, Solar Beam, HP, Toxic]<br>Lv4 **Gulpin** — learnset-derived *(derived)* [Sludge Bomb, HP, Giga Drain, Toxic]<br>Lv4 **Corphish** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic] | Wingull: wild / special acquisition (LC)<br>Whismur: wild / special acquisition (LC)<br>Electrike: wild / special acquisition (LC)<br>Cacnea: wild / special acquisition (LC)<br>Gulpin: wild / special acquisition (LC)<br>Corphish: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE104` | route2north (LC) | 13 | Lv10 **Onix** — All-Out Attacker [Rock Slide, Earthquake, Double-Edge, Explosion]<br>Lv9 **Geodude** — learnset-derived *(derived)* [Earthquake, Rock Slide, HP, Toxic]<br>Lv10 **Larvitar** — Dragon Dance [Hyper Beam, Rock Slide, Earthquake, Substitute]<br>Lv9 **Aron** — learnset-derived *(derived)* [Rock Slide, Rock Tomb, HP, Toxic]<br>Lv9 **Snorunt** — Spikes [Blizzard, Ice Beam, HP, Toxic]<br>Lv9 **Zubat** — learnset-derived *(derived)* [Sludge Bomb, Aerial Ace, HP, Toxic] | Onix: wild / special acquisition (LC)<br>Geodude: wild / special acquisition (LC)<br>Larvitar: wild / special acquisition (LC)<br>Aron: wild / special acquisition (LC)<br>Snorunt: wild / special acquisition (LC)<br>Zubat: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE24` | route24 (LC) | 13 | Lv10 **Cleffa** — learnset-derived *(derived)* [HP, Flamethrower, Toxic, Psychic]<br>Lv10 **Snubbull** — Bulk Up [Double-Edge, Earthquake, Shadow Ball, Bulk Up]<br>Lv11 **Spoink** — Lead [Thief, Psychic, Icy Wind, Taunt]<br>Lv10 **Igglybuff** — learnset-derived *(derived)* [HP, Flamethrower, Toxic, Psychic]<br>Lv11 **Pichu** — learnset-derived *(derived)* [Thunderbolt, Thunder, HP, Toxic]<br>Lv10 **Elekid** — Mixed Attacker [Thunderbolt, Ice Punch, HP, Substitute] | Cleffa: wild / special acquisition (LC)<br>Snubbull: wild / special acquisition (LC)<br>Spoink: wild / special acquisition (LC)<br>Igglybuff: wild / special acquisition (LC)<br>Pichu: wild / special acquisition (LC)<br>Elekid: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_ROUTE24_ROCKET` | route24 (LC) | 13 | Lv12 **Cubone** — Offensive [Focus Punch, Double-Edge, HP, Protect]<br>Lv12 **Koffing** — Defensive [Sludge Bomb, HP, Thief, Explosion]<br>Lv12 **Voltorb** — Offensive [Thunderbolt, HP, Thief, Explosion]<br>Lv11 **Gastly** — Specially Defensive [Thunderbolt, Giga Drain, Thief, Explosion]<br>Lv12 **Ekans** — learnset-derived *(derived)* [Sludge Bomb, Poison Sting, HP, Toxic]<br>Lv11 **Drowzee** — learnset-derived *(derived)* [Psychic, Dream Eater, HP, Toxic] | Cubone: wild / special acquisition (PU)<br>Koffing: wild / special acquisition (PU)<br>Voltorb: wild / special acquisition (PU)<br>Gastly: wild / special acquisition (PU)<br>Ekans: wild / special acquisition (LC)<br>Drowzee: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_ROUTE25` | route25 (LC) | 13 | Lv12 **Magby** — Offensive Utility [Fire Blast, Focus Punch, Toxic, Substitute]<br>Lv12 **Swablu** — learnset-derived *(derived)* [HP, Aerial Ace, Ice Beam, Toxic]<br>Lv11 **Drowzee** — learnset-derived *(derived)* [Psychic, Dream Eater, HP, Toxic]<br>Lv12 **Growlithe** — learnset-derived *(derived)* [Flamethrower, Fire Blast, HP, Toxic]<br>Lv12 **Tyrogue** — learnset-derived *(derived)* [Rock Smash, Brick Break, HP, Toxic]<br>Lv11 **Meowth** — Lead [Thunder, Double-Edge, Shadow Ball, Taunt] | Magby: wild / special acquisition (LC)<br>Swablu: wild / special acquisition (LC)<br>Drowzee: wild / special acquisition (PU)<br>Growlithe: wild / special acquisition (LC)<br>Tyrogue: wild / special acquisition (LC)<br>Meowth: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE25_DUDLEY` | route25 (LC) | 13 | Lv11 **Swablu** — learnset-derived *(derived)* [HP, Aerial Ace, Ice Beam, Toxic]<br>Lv12 **Magby** — Offensive Utility [Fire Blast, Focus Punch, Toxic, Substitute]<br>Lv11 **Ponyta** — Offensive [Substitute, Overheat, Body Slam, Toxic]<br>Lv12 **Houndour** — learnset-derived *(derived)* [Flamethrower, Fire Blast, HP, Toxic]<br>Lv11 **Smoochum** — learnset-derived *(derived)* [Ice Beam, Psychic, HP, Toxic]<br>Lv11 **Meowth** — Lead [Thunder, Double-Edge, Shadow Ball, Taunt] | Swablu: wild / special acquisition (LC)<br>Magby: wild / special acquisition (LC)<br>Ponyta: wild / special acquisition (PU)<br>Houndour: wild / special acquisition (PU)<br>Smoochum: wild / special acquisition (LC)<br>Meowth: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE25_ELLEN` | route25 (LC) | 13 | Lv12 **Dratini** — learnset-derived *(derived)* [HP, Surf, Toxic, Thunderbolt]<br>Lv12 **Horsea** — Rain Sweeper [Surf, HP, Rain Dance, Toxic]<br>Lv11 **Spheal** — learnset-derived *(derived)* [Surf, Ice Beam, HP, Toxic]<br>Lv12 **Seel** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic]<br>Lv11 **Tyrogue** — learnset-derived *(derived)* [Rock Smash, Brick Break, HP, Toxic]<br>Lv12 **Mareep** — learnset-derived *(derived)* [Thunderbolt, Thunder, HP, Toxic] | Dratini: wild / special acquisition (LC)<br>Horsea: wild / special acquisition (LC)<br>Spheal: wild / special acquisition (LC)<br>Seel: wild / special acquisition (LC)<br>Tyrogue: wild / special acquisition (LC)<br>Mareep: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE25_JOE` | route25 (LC) | 13 | Lv11 **Doduo** — learnset-derived *(derived)* [HP, Aerial Ace, Mud-Slap, Toxic]<br>Lv12 **Growlithe** — learnset-derived *(derived)* [Flamethrower, Fire Blast, HP, Toxic]<br>Lv11 **Vulpix** — learnset-derived *(derived)* [Flamethrower, Fire Blast, HP, Toxic]<br>Lv12 **Drowzee** — learnset-derived *(derived)* [Psychic, Dream Eater, HP, Toxic]<br>Lv11 **Igglybuff** — learnset-derived *(derived)* [HP, Flamethrower, Toxic, Psychic]<br>Lv12 **Exeggcute** — Sunny Day Sweeper [Explosion, Sunny Day, Solar Beam, Psychic] | Doduo: wild / special acquisition (PU)<br>Growlithe: wild / special acquisition (LC)<br>Vulpix: wild / special acquisition (LC)<br>Drowzee: wild / special acquisition (PU)<br>Igglybuff: wild / special acquisition (LC)<br>Exeggcute: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE25_LAURA` | route25 (LC) | 13 | Lv11 **Cleffa** — learnset-derived *(derived)* [HP, Flamethrower, Toxic, Psychic]<br>Lv12 **Snubbull** — Bulk Up [Double-Edge, Earthquake, Shadow Ball, Bulk Up]<br>Lv12 **Togepi** — learnset-derived *(derived)* [HP, Flamethrower, Toxic, Psychic]<br>Lv11 **Azurill** — learnset-derived *(derived)* [HP, Body Slam, Surf, Toxic]<br>Lv12 **Pichu** — learnset-derived *(derived)* [Thunderbolt, Thunder, HP, Toxic]<br>Lv11 **Snorunt** — Spikes [Blizzard, Ice Beam, HP, Toxic] | Cleffa: wild / special acquisition (LC)<br>Snubbull: wild / special acquisition (LC)<br>Togepi: wild / special acquisition (LC)<br>Azurill: wild / special acquisition (LC)<br>Pichu: wild / special acquisition (LC)<br>Snorunt: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE25_LLOYD` | route25 (LC) | 13 | Lv11 **Machop** — Offensive [Bulk Up, Focus Punch, HP, Endure]<br>Lv11 **Geodude** — learnset-derived *(derived)* [Earthquake, Rock Slide, HP, Toxic]<br>Lv12 **Bagon** — Dragon Dance [Double-Edge, Brick Break, HP, Fire Blast]<br>Lv11 **Numel** — learnset-derived *(derived)* [Earthquake, Flamethrower, HP, Toxic]<br>Lv12 **Sandshrew** — learnset-derived *(derived)* [Earthquake, Mud-Slap, HP, Toxic]<br>Lv12 **Onix** — All-Out Attacker [Rock Slide, Earthquake, Double-Edge, Explosion] | Machop: wild / special acquisition (LC)<br>Geodude: wild / special acquisition (LC)<br>Bagon: wild / special acquisition (LC)<br>Numel: wild / special acquisition (LC)<br>Sandshrew: wild / special acquisition (LC)<br>Onix: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE25_PAT` | route25 (LC) | 13 | Lv12 **Dratini** — learnset-derived *(derived)* [HP, Surf, Toxic, Thunderbolt]<br>Lv12 **Horsea** — Rain Sweeper [Surf, HP, Rain Dance, Toxic]<br>Lv12 **Spheal** — learnset-derived *(derived)* [Surf, Ice Beam, HP, Toxic]<br>Lv11 **Psyduck** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic]<br>Lv11 **Swablu** — learnset-derived *(derived)* [HP, Aerial Ace, Ice Beam, Toxic]<br>Lv12 **Magby** — Offensive Utility [Fire Blast, Focus Punch, Toxic, Substitute] | Dratini: wild / special acquisition (LC)<br>Horsea: wild / special acquisition (LC)<br>Spheal: wild / special acquisition (LC)<br>Psyduck: wild / special acquisition (LC)<br>Swablu: wild / special acquisition (LC)<br>Magby: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE29` | route29 (LC) | 13 | Lv5 **Sentret** — learnset-derived *(derived)* [HP, Body Slam, Surf, Toxic]<br>Lv4 **Pidgey** — learnset-derived *(derived)* [HP, Aerial Ace, Mud-Slap, Toxic]<br>Lv4 **Nidoran♀** — learnset-derived *(derived)* [Sludge Bomb, HP, Thunderbolt, Toxic]<br>Lv4 **Nidoran♂** — learnset-derived *(derived)* [Sludge Bomb, HP, Thunderbolt, Toxic]<br>Lv5 **Mareep** — learnset-derived *(derived)* [Thunderbolt, Thunder, HP, Toxic]<br>Lv4 **Ledyba** — learnset-derived *(derived)* [Aerial Ace, HP, Giga Drain, Toxic] | Sentret: wild / special acquisition (LC)<br>Pidgey: wild / special acquisition (LC)<br>Nidoran♀: wild / special acquisition (LC)<br>Nidoran♂: wild / special acquisition (LC)<br>Mareep: wild / special acquisition (LC)<br>Ledyba: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE31` | route2north (LC) | 13 | Lv9 **Larvitar** — Dragon Dance [Hyper Beam, Rock Slide, Earthquake, Substitute]<br>Lv9 **Aron** — learnset-derived *(derived)* [Rock Slide, Rock Tomb, HP, Toxic]<br>Lv8 **Baltoy** — All-Out Attacker [Earthquake, Shadow Ball, Rock Tomb, Explosion]<br>Lv8 **Spoink** — Lead [Thief, Psychic, Icy Wind, Taunt]<br>Lv8 **Ralts** — learnset-derived *(derived)* [Psychic, Dream Eater, HP, Toxic]<br>Lv9 **Voltorb** — Offensive [Thunderbolt, HP, Thief, Explosion] | Larvitar: wild / special acquisition (LC)<br>Aron: wild / special acquisition (LC)<br>Baltoy: wild / special acquisition (LC)<br>Spoink: wild / special acquisition (LC)<br>Ralts: wild / special acquisition (LC)<br>Voltorb: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_ROUTE44` | route44 (PU) | 20 | Lv13 **Corphish** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic]<br>Lv13 **Wooper** — learnset-derived *(derived)* [Surf, Earthquake, HP, Toxic]<br>Lv13 **Barboach** — learnset-derived *(derived)* [Surf, Earthquake, HP, Toxic]<br>Lv13 **Remoraid** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic]<br>Lv13 **Clamperl** — Offensive [Surf, Ice Beam, HP, Substitute]<br>Lv12 **Poliwag** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic] | Corphish: wild / special acquisition (LC)<br>Wooper: wild / special acquisition (LC)<br>Barboach: wild / special acquisition (LC)<br>Remoraid: wild / special acquisition (LC)<br>Clamperl: wild / special acquisition (PU)<br>Poliwag: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE44_ALLEN` | route44 (PU) | 20 | Lv13 **Kingler** — Swords Dance [Swords Dance, Double-Edge, HP, Hyper Beam]<br>Lv13 **Seaking** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic]<br>Lv13 **Dragonair** — Specially Defensive [Thunder Wave, Rest, Thunderbolt, Ice Beam]<br>Lv13 **Staryu** — Offensive Utility [Surf, Thunderbolt, Ice Beam, HP]<br>Lv12 **Tentacool** — Specially Defensive [Blizzard, Surf, Toxic, HP]<br>Lv12 **Cleffa** — learnset-derived *(derived)* [HP, Flamethrower, Toxic, Psychic] | Kingler: wild / special acquisition (PU)<br>Seaking: wild / special acquisition (PU)<br>Dragonair: wild / special acquisition (PU)<br>Staryu: wild / special acquisition (LC)<br>Tentacool: wild / special acquisition (PU)<br>Cleffa: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE44_CYBIL` | route44 (PU) | 20 | Lv13 **Remoraid** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic]<br>Lv13 **Corphish** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic]<br>Lv13 **Machop** — Offensive [Bulk Up, Focus Punch, HP, Endure]<br>Lv13 **Voltorb** — Offensive [Thunderbolt, HP, Thief, Explosion]<br>Lv12 **Elekid** — Mixed Attacker [Thunderbolt, Ice Punch, HP, Substitute]<br>Lv12 **Aron** — learnset-derived *(derived)* [Rock Slide, Rock Tomb, HP, Toxic] | Remoraid: wild / special acquisition (LC)<br>Corphish: wild / special acquisition (LC)<br>Machop: wild / special acquisition (LC)<br>Voltorb: wild / special acquisition (PU)<br>Elekid: wild / special acquisition (PU)<br>Aron: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE44_EDGAR` | route44 (PU) | 20 | Lv12 **Barboach** — learnset-derived *(derived)* [Surf, Earthquake, HP, Toxic]<br>Lv12 **Wooper** — learnset-derived *(derived)* [Surf, Earthquake, HP, Toxic]<br>Lv13 **Cubone** — Offensive [Focus Punch, Double-Edge, HP, Protect]<br>Lv13 **Rhyhorn** — learnset-derived *(derived)* [Earthquake, Rock Slide, HP, Toxic]<br>Lv12 **Magnemite** — Offensive Utility [Thunderbolt, HP, Toxic, Substitute]<br>Lv12 **Pineco** — learnset-derived *(derived)* [HP, Giga Drain, Toxic, Earthquake] | Barboach: wild / special acquisition (LC)<br>Wooper: wild / special acquisition (LC)<br>Cubone: wild / special acquisition (PU)<br>Rhyhorn: wild / special acquisition (PU)<br>Magnemite: wild / special acquisition (PU)<br>Pineco: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_ROUTE44_VANCE` | route44 (PU) | 20 | Lv13 **Staryu** — Offensive Utility [Surf, Thunderbolt, Ice Beam, HP]<br>Lv12 **Horsea** — Rain Sweeper [Surf, HP, Rain Dance, Toxic]<br>Lv12 **Sealeo** — Tank [Surf, Ice Beam, HP, Substitute]<br>Lv13 **Clamperl** — Offensive [Surf, Ice Beam, HP, Substitute]<br>Lv12 **Corphish** — learnset-derived *(derived)* [Surf, Water Pulse, HP, Toxic]<br>Lv12 **Pichu** — learnset-derived *(derived)* [Thunderbolt, Thunder, HP, Toxic] | Staryu: wild / special acquisition (LC)<br>Horsea: wild / special acquisition (LC)<br>Sealeo: wild / special acquisition (PU)<br>Clamperl: wild / special acquisition (PU)<br>Corphish: wild / special acquisition (LC)<br>Pichu: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE44_WILTON` | route44 (PU) | 20 | Lv13 **Magby** — Offensive Utility [Fire Blast, Focus Punch, Toxic, Substitute]<br>Lv12 **Numel** — Lead [Earthquake, Fire Blast, Toxic, Protect]<br>Lv12 **Cubone** — Offensive [Focus Punch, Double-Edge, HP, Protect]<br>Lv13 **Trapinch** — Bulky Trapper [Earthquake, Rock Slide, HP, Protect]<br>Lv12 **Aron** — learnset-derived *(derived)* [Rock Slide, Rock Tomb, HP, Toxic]<br>Lv13 **Mareep** — learnset-derived *(derived)* [Thunderbolt, Thunder, HP, Toxic] | Magby: wild / special acquisition (LC)<br>Numel: wild / special acquisition (LC)<br>Cubone: wild / special acquisition (PU)<br>Trapinch: wild / special acquisition (PU)<br>Aron: wild / special acquisition (LC)<br>Mareep: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE44_ZACH` | route44 (PU) | 20 | Lv13 **Onix** — All-Out Attacker [Rock Slide, Earthquake, Double-Edge, Explosion]<br>Lv12 **Machop** — Offensive [Bulk Up, Focus Punch, HP, Endure]<br>Lv12 **Geodude** — learnset-derived *(derived)* [Earthquake, Rock Slide, HP, Toxic]<br>Lv13 **Snorunt** — Spikes [Blizzard, Ice Beam, Endure, HP]<br>Lv12 **Larvitar** — Dragon Dance [Hyper Beam, Rock Slide, Earthquake, Substitute]<br>Lv13 **Magnemite** — Offensive Utility [Thunderbolt, HP, Toxic, Substitute] | Onix: wild / special acquisition (LC)<br>Machop: wild / special acquisition (LC)<br>Geodude: wild / special acquisition (LC)<br>Snorunt: wild / special acquisition (LC)<br>Larvitar: wild / special acquisition (LC)<br>Magnemite: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_ROUTE46` | route46 (LC) | 13 | Lv6 **Machop** — Offensive [Bulk Up, Focus Punch, HP, Endure]<br>Lv6 **Geodude** — learnset-derived *(derived)* [Earthquake, Rock Slide, HP, Toxic]<br>Lv6 **Sandshrew** — learnset-derived *(derived)* [Earthquake, Mud-Slap, HP, Toxic]<br>Lv6 **Bagon** — Dragon Dance [Double-Edge, Brick Break, HP, Fire Blast]<br>Lv5 **Numel** — learnset-derived *(derived)* [Earthquake, Flamethrower, HP, Toxic]<br>Lv6 **Phanpy** — learnset-derived *(derived)* [Earthquake, Mud-Slap, HP, Toxic] | Machop: wild / special acquisition (LC)<br>Geodude: wild / special acquisition (LC)<br>Sandshrew: wild / special acquisition (LC)<br>Bagon: wild / special acquisition (LC)<br>Numel: wild / special acquisition (LC)<br>Phanpy: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE46_ERIN` | route46 (LC) | 13 | Lv7 **Onix** — All-Out Attacker [Rock Slide, Earthquake, Double-Edge, Explosion]<br>Lv6 **Geodude** — learnset-derived *(derived)* [Earthquake, Rock Slide, HP, Toxic]<br>Lv7 **Larvitar** — Dragon Dance [Hyper Beam, Rock Slide, Earthquake, Substitute]<br>Lv6 **Machop** — Offensive [Bulk Up, Focus Punch, HP, Endure]<br>Lv6 **Sandshrew** — learnset-derived *(derived)* [Earthquake, Mud-Slap, HP, Toxic]<br>Lv6 **Bagon** — Dragon Dance [Double-Edge, Brick Break, HP, Fire Blast] | Onix: wild / special acquisition (LC)<br>Geodude: wild / special acquisition (LC)<br>Larvitar: wild / special acquisition (LC)<br>Machop: wild / special acquisition (LC)<br>Sandshrew: wild / special acquisition (LC)<br>Bagon: wild / special acquisition (LC) |
| `TRAINER_PLASTIC_OX_ROUTE_ILEX` | ilex (LC) | 13 | Lv8 **Paras** — learnset-derived *(derived)* [Giga Drain, Solar Beam, HP, Toxic]<br>Lv8 **Venonat** — learnset-derived *(derived)* [Sludge Bomb, HP, Giga Drain, Toxic]<br>Lv8 **Nincada** — learnset-derived *(derived)* [Leech Life, Mud-Slap, HP, Toxic]<br>Lv7 **Oddish** — Sunny Day [Sunny Day, Solar Beam, HP, Bullet Seed]<br>Lv8 **Exeggcute** — Sunny Day Sweeper [Explosion, Sunny Day, Solar Beam, Psychic]<br>Lv7 **Pineco** — learnset-derived *(derived)* [HP, Giga Drain, Toxic, Earthquake] | Paras: wild / special acquisition (LC)<br>Venonat: wild / special acquisition (LC)<br>Nincada: wild / special acquisition (LC)<br>Oddish: wild / special acquisition (LC)<br>Exeggcute: wild / special acquisition (LC)<br>Pineco: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_SILPHGRUNT1` | saffron (OU) | 55 | Lv52 **Machamp** — Bulk Up [Bulk Up, Cross Chop, Rock Slide, HP]<br>Lv52 **Jynx** — Fake Tears [Lovely Kiss, Fake Tears, Psychic, Ice Beam]<br>Lv51 **Weezing** — Offensive [Sludge Bomb, Flamethrower, Haze, Explosion]<br>Lv51 **Hariyama** — Offensive [Hyper Beam, Brick Break, Knock Off, HP]<br>Lv50 **Dusclops** — RestTalk [Shadow Ball, Rest, Sleep Talk, Will-O-Wisp]<br>Lv52 **Kadabra** — learnset-derived *(derived)* [Psychic, Future Sight, HP, Toxic] | Machamp: evolves from MACHOKE (trade) (UUBL)<br>Jynx: evolves from Smoochum at Lv30 (UUBL)<br>Weezing: evolves from Koffing at Lv35 (UUBL)<br>Hariyama: evolves from Makuhita at Lv24 (UUBL)<br>Dusclops: evolves from Duskull at Lv37 (UUBL)<br>Kadabra: evolves from Abra at Lv16 (UUBL) |
| `TRAINER_PLASTIC_OX_SILPHGRUNT2` | saffron (OU) | 55 | Lv52 **Steelix** — Standard Wall [Earthquake, Toxic, Roar, Rest]<br>Lv52 **Exeggutor** — Sunnybeam [Explosion, Sunny Day, Solar Beam, HP]<br>Lv51 **Slowbro** — SubPunch [Substitute, Focus Punch, Surf, Psychic]<br>Lv52 **Magneton** — Trapper [Thunderbolt, HP, Toxic, Protect]<br>Lv50 **Dodrio** — Choice Band [Drill Peck, Return, Hyper Beam, HP]<br>Lv52 **Cloyster** — Spiker [Spikes, Surf, Explosion, HP] | Steelix: evolves from ONIX (Metal_Coat) (UUBL)<br>Exeggutor: evolves from EXEGGCUTE (Leaf_Stone) (UUBL)<br>Slowbro: evolves from Slowpoke at Lv37 (UUBL)<br>Magneton: evolves from Magnemite at Lv30 (OU)<br>Dodrio: evolves from Doduo at Lv31 (UUBL)<br>Cloyster: evolves from SHELLDER (Water_Stone) (OU) |
| `TRAINER_PLASTIC_OX_SILPHGRUNT3` | saffron (OU) | 55 | Lv53 **Dragonite** — SubPunch [Substitute, Focus Punch, Thunderbolt, Ice Beam]<br>Lv52 **Kingdra** — Rain Dance Sweeper [Rain Dance, Surf, Ice Beam, HP]<br>Lv51 **Armaldo** — learnset-derived *(derived)* [Rock Slide, Rock Tomb, HP, Toxic]<br>Lv51 **Ursaring** — Bulk Up [Bulk Up, Return, HP, Earthquake]<br>Lv50 **Linoone** — Choice Band [Return, Shadow Ball, HP, Hyper Beam]<br>Lv51 **Marowak** — Swords Dance [Swords Dance, Bonemerang, Rock Slide, Focus Punch] | Dragonite: evolves from Dragonair at Lv50 (UUBL)<br>Kingdra: evolves from SEADRA (Dragon_Scale) (UUBL)<br>Armaldo: evolves from Anorith at Lv40 (UUBL)<br>Ursaring: evolves from Teddiursa at Lv30 (UUBL)<br>Linoone: evolves from Zigzagoon at Lv20 (UUBL)<br>Marowak: evolves from Cubone at Lv28 (UUBL) |
| `TRAINER_PLASTIC_OX_STEVEN` | league (OU) | 62 | Lv62 **Metagross** — Bulky Attacker [Meteor Mash, Earthquake, Protect, Explosion]<br>Lv62 **Salamence** — Dragon Dance [Hyper Beam, HP, Rock Slide, Earthquake]<br>Lv62 **Flygon** — Offensive [Earthquake, Rock Slide, HP, Substitute]<br>Lv62 **Aggron** — Choice Band [Earthquake, Rock Slide, Double-Edge, Focus Punch]<br>Lv61 **Armaldo** — learnset-derived *(derived)* [Rock Slide, Rock Tomb, HP, Toxic]<br>Lv61 **Claydol** — Utility [Rapid Spin, Earthquake, Psychic, Explosion] | Metagross: evolves from Metang at Lv45 (OU)<br>Salamence: evolves from Shelgon at Lv50 (OU)<br>Flygon: evolves from Vibrava at Lv45 (OU)<br>Aggron: evolves from Lairon at Lv36 (RU)<br>Armaldo: evolves from Anorith at Lv40 (UUBL)<br>Claydol: evolves from Baltoy at Lv36 (OU) |
| `TRAINER_PLASTIC_OX_TATELIZA` | mossdeep (UUBL) | 50 | Lv46 **Alakazam** — Calm Mind Sweeper [Calm Mind, Psychic, Fire Punch, Thunder Punch]<br>Lv46 **Slowbro** — Defensive [Surf, Psychic, Rest, Calm Mind]<br>Lv45 **Machamp** — Bulk Up [Bulk Up, Hyper Beam, Rock Slide, HP]<br>Lv45 **Ursaring** — Bulk Up [Bulk Up, Return, HP, Earthquake]<br>Lv44 **Steelix** — Choice Band [Earthquake, Iron Tail, Double-Edge, Explosion]<br>Lv44 **Houndoom** — learnset-derived *(derived)* [Flamethrower, Fire Blast, HP, Toxic] | Alakazam: evolves from KADABRA (trade) (UUBL)<br>Slowbro: evolves from Slowpoke at Lv37 (UUBL)<br>Machamp: evolves from MACHOKE (trade) (UUBL)<br>Ursaring: evolves from Teddiursa at Lv30 (UUBL)<br>Steelix: evolves from ONIX (Metal_Coat) (UUBL)<br>Houndoom: evolves from Houndour at Lv24 (UUBL) |
| `TRAINER_PLASTIC_OX_TOWERGRUNT1` | cinnabar (UU) | 42 | Lv38 **Gastly** — Stallbreaker [Psychic, Thunderbolt, Taunt, Explosion]<br>Lv37 **Drowzee** — learnset-derived *(derived)* [Psychic, Dream Eater, HP, Toxic]<br>Lv37 **Cubone** — Offensive [Bonemerang, Double-Edge, HP, Protect]<br>Lv37 **Muk** — Standard [Sludge Bomb, Ice Punch, Explosion, HP]<br>Lv36 **Koffing** — Defensive [Sludge Bomb, HP, Thief, Explosion]<br>Lv38 **Haunter** — Offensive Utility [Thunderbolt, Psychic, Explosion, Taunt] | Gastly: wild / special acquisition (PU)<br>Drowzee: wild / special acquisition (PU)<br>Cubone: wild / special acquisition (PU)<br>Muk: evolves from Grimer at Lv38 (UU)<br>Koffing: wild / special acquisition (PU)<br>Haunter: evolves from Gastly at Lv25 (NU) |
| `TRAINER_PLASTIC_OX_TOWERGRUNT2` | cinnabar (UU) | 42 | Lv38 **Machop** — Offensive [Bulk Up, Focus Punch, HP, Endure]<br>Lv38 **Cubone** — Offensive [Bonemerang, Double-Edge, HP, Protect]<br>Lv38 **Onix** — Sunny Day Support [Sunny Day, Explosion, Iron Tail, Earthquake]<br>Lv37 **Muk** — Curse [Explosion, Sludge Bomb, Fire Blast, HP]<br>Lv37 **Rhyhorn** — learnset-derived *(derived)* [Earthquake, Rock Slide, HP, Toxic]<br>Lv38 **Haunter** — Pinch Berry [Thunderbolt, Psychic, Explosion, Endure] | Machop: wild / special acquisition (LC)<br>Cubone: wild / special acquisition (PU)<br>Onix: wild / special acquisition (LC)<br>Muk: evolves from Grimer at Lv38 (UU)<br>Rhyhorn: wild / special acquisition (PU)<br>Haunter: evolves from Gastly at Lv25 (NU) |
| `TRAINER_PLASTIC_OX_VICTORYROAD` | victoryroad (OU) | 60 | Lv58 **Flygon** — Choice Band [Earthquake, Rock Slide, HP, Hyper Beam]<br>Lv58 **Cloyster** — Spiker [Spikes, Surf, Explosion, HP]<br>Lv58 **Starmie** — Offensive [Surf, Ice Beam, Thunderbolt, Rapid Spin]<br>Lv58 **Swampert** — Standard Defensive [Earthquake, Ice Beam, Protect, Surf]<br>Lv58 **Forretress** — Standard [Spikes, Rapid Spin, HP, Earthquake]<br>Lv58 **Gengar** — Perish Trap [Mean Look, Explosion, Taunt, Destiny Bond] | Flygon: evolves from Vibrava at Lv45 (OU)<br>Cloyster: evolves from SHELLDER (Water_Stone) (OU)<br>Starmie: evolves from STARYU (Water_Stone) (OU)<br>Swampert: evolves from Marshtomp at Lv36 (OU)<br>Forretress: evolves from Pineco at Lv31 (OU)<br>Gengar: evolves from HAUNTER (trade) (OU) |
| `TRAINER_PLASTIC_OX_WALLACE` | league (OU) | 62 | Lv62 **Salamence** — Choice Band [HP, Earthquake, Rock Slide, Brick Break]<br>Lv62 **Swampert** — Standard Offensive [Surf, Ice Beam, Earthquake, Focus Punch]<br>Lv62 **Tyranitar** — Choice Band [Rock Slide, Focus Punch, Earthquake, HP]<br>Lv61 **Metagross** — Mixed [Psychic, HP, Meteor Mash, Explosion]<br>Lv61 **Forretress** — Standard [Spikes, Rapid Spin, HP, Earthquake]<br>Lv61 **Gengar** — Offensive [Thunderbolt, Ice Punch, HP, Explosion] | Salamence: evolves from Shelgon at Lv50 (OU)<br>Swampert: evolves from Marshtomp at Lv36 (OU)<br>Tyranitar: evolves from Pupitar at Lv55 (OU)<br>Metagross: evolves from Metang at Lv45 (OU)<br>Forretress: evolves from Pineco at Lv31 (OU)<br>Gengar: evolves from HAUNTER (trade) (OU) |
| `TRAINER_PLASTIC_OX_WEATHER` | fortree (RU) | 36 | Lv34 **Castform** — Sunny Day [Thunderbolt, Flamethrower, Solar Beam, Sunny Day]<br>Lv34 **Xatu** — Calm Mind [Calm Mind, Psychic, HP, Substitute]<br>Lv33 **Mawile** — Substitute + Baton Pass [Substitute, Baton Pass, Swords Dance, HP]<br>Lv33 **Meditite** — Offensive Sub [Substitute, Brick Break, Shadow Ball, Toxic]<br>Lv32 **Magnemite** — Offensive Utility [Thunderbolt, HP, Toxic, Substitute]<br>Lv32 **Elekid** — Mixed Attacker [Thunderbolt, Ice Punch, HP, Substitute] | Castform: wild / special acquisition (PU)<br>Xatu: evolves from Natu at Lv25 (RU)<br>Mawile: wild / special acquisition (PU)<br>Meditite: wild / special acquisition (PU)<br>Magnemite: wild / special acquisition (PU)<br>Elekid: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_WHITNEY` | gym2 (PU) | 20 | Lv20 **Mightyena** — Offensive Heal Bell [Hyper Beam, Return, Shadow Ball, Howl]<br>Lv19 **Wigglytuff** — Offensive Sub [Body Slam, Shadow Ball, Substitute, Brick Break]<br>Lv19 **Meowth** — Lead [Thunder, Double-Edge, Shadow Ball, Taunt]<br>Lv19 **Furret** — Wallbreaker [Double-Edge, Shadow Ball, Brick Break, Quick Attack]<br>Lv19 **Arbok** — Choice Band [Sludge Bomb, Earthquake, HP, Rock Slide]<br>Lv20 **Dragonair** — Specially Defensive [Thunder Wave, Rest, Thunderbolt, Ice Beam] | Mightyena: evolves from Poochyena at Lv18 (PU)<br>Wigglytuff: evolves from JIGGLYPUFF (Moon_Stone) (PU)<br>Meowth: wild / special acquisition (LC)<br>Furret: evolves from Sentret at Lv15 (PU)<br>Arbok: evolves from Ekans at Lv20 (PU)<br>Dragonair: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_WINONA` | fortree (RU) | 36 | Lv36 **Pidgeot** — All-out Attacker [Double-Edge, Quick Attack, Aerial Ace, HP]<br>Lv35 **Pelipper** — Defensive [Surf, Ice Beam, Rest, Sleep Talk]<br>Lv35 **Golbat** — Choice Band [Sludge Bomb, Aerial Ace, HP, Hyper Beam]<br>Lv34 **Vigoroth** — Bulk Up [Return, Earthquake, Focus Punch, Bulk Up]<br>Lv34 **Farfetch'd** — Swords Dance + Flail [Substitute, Iron Tail, HP, Swords Dance]<br>Lv33 **Doduo** — learnset-derived *(derived)* [HP, Aerial Ace, Mud-Slap, Toxic] | Pidgeot: evolves from Pidgeotto at Lv30 (NU)<br>Pelipper: evolves from Wingull at Lv25 (NU)<br>Golbat: evolves from Zubat at Lv22 (NU)<br>Vigoroth: evolves from Slakoth at Lv18 (NU)<br>Farfetch'd: wild / special acquisition (PU)<br>Doduo: wild / special acquisition (PU) |
| `TRAINER_PLASTIC_OX_LANCE` | _unchanged_ | — | Zapdos @ Leftovers, Forretress @ Leftovers, Blissey (F) @ Leftovers, Gengar @ Leftovers, Tyranitar @ Leftovers, Swampert @ Leftovers | metamon showcase trainer in Oldale Town |
| `TRAINER_PLASTIC_OX_PLAYER` | _unchanged_ | — | Skarmory @ Leftovers, Blissey (F) @ Leftovers, Claydol @ Leftovers, Dugtrio @ Choice Band, Gengar @ Leftovers, Suicune @ Leftovers | player party template, not a battled trainer |
| `TRAINER_PLASTIC_OX_ROXANNE` | _unchanged_ | — | Voltorb @ Sitrus Berry, Trapinch @ Sitrus Berry, Cacnea @ Sitrus Berry, Chinchou @ Sitrus Berry, Anorith @ Sitrus Berry, Lileep @ Sitrus Berry | designated format reference; already a legal six |

## 2.4 Move substitutions

| Substitution | Count | Example |
|---|---:|---|
| Hidden Power type Ghost dropped: trainerproc has no HP-type field in the .party format | 38 | BLAINE[4] Muk |
| Hidden Power type Grass dropped: trainerproc has no HP-type field in the .party format | 18 | BILL[5] Charizard |
| Hidden Power type Bug dropped: trainerproc has no HP-type field in the .party format | 14 | BILL[3] Flygon |
| Cross Chop -> Focus Punch (level-up move needs Lv40) | 11 | MOONGRUNT1[1] Machop |
| Dragon Dance -> Hyper Beam (egg or special-case only) | 10 | BLUE[0] Tyranitar |
| Fake Out -> Thunder (level-up move needs Lv50) | 10 | KIMONOESPEON[2] Meowth |
| Bonemerang -> Focus Punch (level-up move needs Lv25) | 7 | MOONGRUNT1[0] Cubone |
| Hidden Power type Flying dropped: trainerproc has no HP-type field in the .party format | 6 | BLUE[4] Gyarados |
| Hydro Pump -> Surf (cannot learn) | 6 | BILL[1] Starmie |
| Will O Wisp -> Blizzard (level-up move needs Lv38) | 6 | KIMONOUMBREON[3] Duskull |
| Hidden Power type Fire dropped: trainerproc has no HP-type field in the .party format | 5 | PU_ROUTE36[0] Tangela |
| Hidden Power type Ground dropped: trainerproc has no HP-type field in the .party format | 5 | MORTY[4] Golbat |
| Spikes -> Blizzard (egg or special-case only) | 5 | MOON_LASS_IRIS[5] Snorunt |
| Will O Wisp -> Explosion (egg or special-case only) | 4 | MOON_TEAM_ROCKET_GRUNT_2[5] Gastly |
| Dragon Dance -> Fire Blast (egg or special-case only) | 3 | ROUTE25_LLOYD[2] Bagon |
| Hidden Power type Ice dropped: trainerproc has no HP-type field in the .party format | 3 | BLAINE[3] Electrode |
| Hydro Pump -> Surf (level-up move needs Lv43) | 3 | ROUTE25_ELLEN[1] Horsea |
| Hydro Pump -> Surf (level-up move needs Lv46) | 3 | KIMONOVAPOREON[3] Staryu |
| Rapid Spin -> Explosion (egg or special-case only) | 3 | BILL[2] Cloyster |
| Agility -> Explosion (level-up move needs Lv66) | 2 | BILL[0] Metagross |
| Baton Pass -> Hyper Beam (cannot learn) | 2 | CLAIR[1] Jolteon |
| Flail -> Iron Tail (egg or special-case only) | 2 | PU_ROUTE35[1] Farfetch'd |
| Gust -> Hyper Beam (egg or special-case only) | 2 | BILL[3] Flygon |
| Quick Attack -> Hyper Beam (egg or special-case only) | 2 | SILPHGRUNT2[4] Dodrio |
| Rapid Spin -> Blizzard (egg or special-case only) | 2 | KIMONOVAPOREON[5] Tentacool |
| Reversal -> Focus Punch (egg or special-case only) | 2 | MOON_YOUNGSTER_JOSH[0] Mankey |
| Block -> Iron Tail (egg or special-case only) | 1 | TOWERGRUNT2[2] Onix |
| Cross Chop -> Hyper Beam (egg or special-case only) | 1 | SILPHGRUNT1[3] Hariyama |
| Cross Chop -> Hyper Beam (level-up move needs Lv46) | 1 | TATELIZA[2] Machamp |
| Crunch -> Bite (level-up move needs Lv28) | 1 | PU_ROUTE33[1] Seviper |
| Curse -> Explosion (egg or special-case only) | 1 | TOWERGRUNT2[3] Muk |
| Extreme Speed -> Hyper Beam (level-up move needs Lv49) | 1 | BLAINE[1] Arcanine |
| Heal Bell -> Hyper Beam (cannot learn) | 1 | WHITNEY[0] Mightyena |
| Hidden Power type Rock dropped: trainerproc has no HP-type field in the .party format | 1 | BRUNO[4] Donphan |
| Hidden Power type Steel dropped: trainerproc has no HP-type field in the .party format | 1 | WEATHER[2] Mawile |
| Hypnosis -> Hyper Beam (egg or special-case only) | 1 | BLAINE[2] Rapidash |
| Mud Shot -> Hyper Beam (level-up move needs Lv23) | 1 | ROUTE44_ALLEN[0] Kingler |
| Perish Song -> Explosion (egg or special-case only) | 1 | VICTORYROAD[5] Gengar |
| Quick Attack -> Focus Punch (egg or special-case only) | 1 | KIMONOFLAREON[5] Delibird |
| Rapid Spin -> Hyper Beam (egg or special-case only) | 1 | BLAINE[5] Tentacruel |
| Refresh -> Hyper Beam (egg or special-case only) | 1 | CLAIR[2] Swampert |
| Reversal -> Solar Beam (egg or special-case only) | 1 | PU_ROUTE35[2] Yanma |
| Slack Off -> Focus Punch (cannot learn) | 1 | WINONA[3] Vigoroth |
| Sleep Powder -> Explosion (cannot learn) | 1 | SILPHGRUNT2[1] Exeggutor |
| Trick -> Hyper Beam (egg or special-case only) | 1 | SILPHGRUNT3[4] Linoone |
| Wish -> Hyper Beam (egg or special-case only) | 1 | MORTY[5] Wigglytuff |

The three large groups are worth explaining:

* **Hidden Power type** — trainerproc's `.party` grammar has no HP-type field
  (it accepts `Level`, `Ball`, `Happiness`, `Nature`, `Shiny`, `Dynamax Level`,
  `Gigantamax`, `Tera Type`, `Ability`, `IVs`, `EVs`), so a dex set's `hpType`
  cannot be expressed and the ROM picks the species default. This is a format
  limitation, not a choice; a Hidden Power type would need a new trainerproc
  field.
* **Cross Chop / Hydro Pump / Fake Out / Bonemerang** — the dex sets are written
  at level 100. A level-13 Tyrogue cannot know Fake Out (it arrives at 50), a
  level-40 Horsea cannot know Hydro Pump, a level-12 Machop cannot know Cross
  Chop (46) and so on. Each was replaced by the closest legal move of the same
  role, preferring a TM the species can be taught.
* **Dragon Dance / Spikes / Will-O-Wisp / Agility** — species that simply do not
  learn them in this ROM at all (Tyranitar has no Dragon Dance, Duskull no
  Will-O-Wisp, Snorunt no Spikes), so the slot went to the strongest remaining
  legal attack or utility move.

## 2.5 Deliberate exceptions

| Trainer | Why |
|---|---|
| `TRAINER_PLASTIC_OX_ROXANNE` | The task's designated format reference. It is already a legal six: all six species are obtainable before Gym 1 (Route 2 North, Route 24, the Sea Cottage fossils) and all six sit at exactly the Gym 1 cap of 13. Rewriting it would have changed the pattern the rest of the work follows, so it is left as the reference. |
| `TRAINER_PLASTIC_OX_LANCE` | An optional Elite-Four-strength battle in **Oldale Town**, listed in `sMetamonTrainers[]`. Its Zapdos/Forretress/Blissey/Gengar/Tyranitar/Swampert roster is illegal by every progression rule — it is in the first town — but the trainer *is* the metamon showcase and its id must stay stable. Flagged rather than gutted. |
| `TRAINER_PLASTIC_OX_PLAYER` | Not an opponent. `GivePlasticOxPlayerParty()` in `src/new_game.c` builds the **player's own starting party** from this template, so rewriting it would change what the player begins with. It already has six Pokémon. |
| The four Dance Theater signature Eeveelutions | `KIMONOVAPOREON`, `KIMONOJOLTEON`, `KIMONOESPEON` and `KIMONOUMBREON` are gated on `FLAG_BADGE02_GET` (two badges, NU), but Vaporeon/Jolteon/Espeon/Umbreon are UUBL and OU and need a Thunder/Water Stone or a friendship evolution that the tier system unlocks at Gym 6/7. The trainer is named for the Eeveelution, her dialogue and her clear flag depend on it, so the signature is kept as designed and only the other five slots obey the rules. `KIMONOFLAREON` is NU and is fully legal. |

## 2.6 Trainer coverage

All 71 `TRAINER_PLASTIC_OX_*` ids in `src/data/trainers.party` are reachable and
all 71 now have six Pokémon.

`src/data/trainers_frlg.party` was **not** edited. Scanning every `*_hns` and
`PlasticOx*` map plus every `data/scripts/plastic_ox*.inc` for
`TRAINER_[A-Z0-9_]+` yields 59 distinct matches, of which 57 are
`TRAINER_PLASTIC_OX_*` and the remaining two are the object-event enums
`TRAINER_TYPE_NONE` and `TRAINER_TYPE_NORMAL`, not trainer ids — nothing from
either `.party` file. No FRLG trainer is therefore reachable in this region and
its data was correctly left alone.

Coverage was then checked across the whole tree rather than just the
Plastic-Ox-owned files: `TRAINER_PLASTIC_OX_*` appears 71 times in distinct ids
when `data/`, `src/*.c` and `include/` are scanned, and those 71 are exactly the
71 the `.party` file defines — nothing is defined-but-unwired and nothing is
wired-but-undefined. The remaining 14 (LANCE, PLAYER and the Mt. Moon and
Oldale Town trainers) live on FRLG or native-map files rather than `*_hns`, which
is why the narrower scan sees 57.

### ROM headroom

The linker reports 27,568,996 bytes (26.29 MB, 82.16%) of the 32 MB ROM, so
roughly 5.7 MB of tail padding remains. Growing 213 trainer Pokémon to 408 cost
about 11 KB of ROM (`plastic_ox/battle/metamon/ROM_SPACE_AUDIT.md` recorded
~26.34 MB before this task), so the trainer-overhaul goal is nowhere near the
wall.

---

# Verification

| Check | Command | Result |
|---|---|---|
| v5.5 encounter regression | `python3 plastic_ox/encounter_tables/test_pre_mt_moon_v5_5.py` | **PASS: 174 checks** |
| Trainer party regression | `python3 plastic_ox/agent/test_trainer_teams_v2.py` | **PASS: 3,403 checks over 71 trainers** |
| Generator self-check | `python3 plastic_ox/agent/apply_trainer_teams_v2.py --check` | 0 problems, 71 trainers described |
| Pre-existing v4.4 test | `python3 plastic_ox/encounter_tables/test_pre_mt_moon_v4_4.py` | still failing — pre-existing, superseded; see 1.6 |
| ROM build | `DEVKITARM=~/devkitpro/opt/devkitpro/devkitARM make -j8` | **exit 0, no errors.** `trainerproc` regenerated `src/data/trainers.h` cleanly. |
| ROM size | linker `--print-memory-usage` | 27,568,996 bytes (26.29 MB, 82.16% of the 32 MB ROM) |
| EWRAM / IWRAM | — | 226,560 B / 256 KB (86.43%), 28,588 B / 32 KB (87.24%) |

**Not performed:** no play-testing, no emulator run, and no `make check`
battle-test suite run. The move-level, species-level and tier-level guarantees
above come from static analysis of the ROM's own data files, not from playing
the game. Encounter *rates* are verified as the effective conditional
probability the code will produce, not as observed in-game frequencies.
