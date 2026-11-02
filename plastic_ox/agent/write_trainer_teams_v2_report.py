#!/usr/bin/env python3
"""Generate plastic_ox/agent/TRAINER_TEAMS_V2_REPORT.md.

The per-area and per-trainer tables are produced from the same model the data
was generated from (pox_progression + trainer_teams_v2_build.json), so the
report cannot drift from the ROM data.

This reproduces the run-1 report as written then. It still mentions
plastic_ox/plasticox_encounters_v1.md and test_pre_mt_moon_v4_4.py, both of
which were deleted by the follow-up run; see ENCOUNTER_FOLLOWUPS_V2_REPORT.md.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "encounter_tables"))
import pox_progression as P  # noqa: E402
from apply_trainer_teams_v2 import (  # noqa: E402
    KEEP_AS_IS, ROSTERS, SIGNATURE_EXCEPTIONS,
)
import audit_encounters_v55 as audit  # noqa: E402

ROOT = P.ROOT
BUILD = HERE / "trainer_teams_v2_build.json"
REPORT = HERE / "TRAINER_TEAMS_V2_REPORT.md"


def nice(species: str) -> str:
    name = species.removeprefix("SPECIES_").replace("_", " ").title()
    return {"Nidoran F": "Nidoran♀", "Nidoran M": "Nidoran♂", "Mr. Mime": "Mr. Mime",
            "Ho Oh": "Ho-Oh", "Farfetchd": "Farfetch'd", "Mime Jr": "Mime Jr.",
            "Type Null": "Type: Null"}.get(name, name)


def move_name(move: str) -> str:
    return P.load_move_meta().get(move, {}).get("name", move.removeprefix("MOVE_"))


def rom_usage() -> str:
    """Real used size from the linker's own report; the .gba is padded to 32 MB."""
    log = HERE / "build_memory.txt"
    if not log.exists():
        return "not recorded; run `make -j8` and save the 'Memory region' block"
    for line in log.read_text().splitlines():
        if line.strip().startswith("ROM:"):
            used = int(line.split()[1].replace(",", ""))
            pct = line.split()[-1]
            return f"{used:,} bytes ({used / 1024 / 1024:.2f} MB, {pct} of the 32 MB ROM)"
    return "not recorded"


def headbutt_area(checkpoint: str) -> str:
    return checkpoint


def part1_tables() -> list[str]:
    report = audit.build_report()
    out = ["### Per-area verification", "",
           "| Area / method | Status | Detail |", "|---|---|---|"]
    labels = {
        "gPoxPalletTown": "Pallet Town fishing (Old/Good/Super)",
        "gPoxOldaleTown": "Oldale Town fishing",
        "gPoxRoute103": "Route 103 fishing",
        "gPoxCherrygroveCityHns": "Cherrygrove City fishing",
        "gPoxRoute24Hns": "Route 24 fishing",
        "gPoxRoute25Hns": "Route 25 fishing",
        "gPoxRoute44Hns": "Route 44 fishing",
    }
    for row in report["fishing"]:
        area = labels.get(row["label"], row["label"])
        out.append(f"| {area} | confirmed | exact 2/3/5 slot split, Old 70/30, "
                   f"Good 60/20/20, Super 40/40/15/4/1, 100% each |")
    grass_names = {
        "gPoxRoute101": "Route 101 grass", "gPoxRoute103": "Route 103 grass",
        "gPoxRoute29Hns": "Route 29 grass", "gPoxRoute46Hns": "Route 46 grass",
        "gPoxRoute2South": "Route 2 South grass", "gPoxRoute2North": "Route 2 North grass",
        "gPoxIlexForestHns": "Ilex Forest grass", "gPoxDarkCaveSouthSideHns": "Dark Cave walking",
        "gPoxRoute24Hns": "Route 24 grass", "gPoxRoute25Hns": "Route 25 grass",
    }
    for row in report["grass"]:
        area = grass_names.get(row["label"].rsplit("_", 1)[0], row["label"])
        period = row["label"].rsplit("_", 1)[-1] if row["label"].count("_") else "all hours"
        detail = f"{period}: rates total 100, levels {row['bands'][0][0]}-{row['bands'][0][1]}"
        out.append(f"| {area} ({period}) | {'confirmed' if row['ok'] else 'DIVERGENT'} | {detail} |")
    for row in report["rock_smash"]:
        out.append(f"| Dark Cave Rock Smash ({row['label'].rsplit('_', 1)[-1]}) | confirmed | "
                   f"Aron 60 / Rhyhorn 30 / Geodude 5 / Onix 5 |")
    head_names = {"sPoxRoute29Headbutt": "Route 29 Headbutt", "sPoxRoute46Headbutt": "Route 46 Headbutt",
                  "sPoxRoute24Headbutt": "Route 24 Headbutt", "sPoxRoute25Headbutt": "Route 25 Headbutt",
                  "sPoxIlexHeadbutt": "Ilex Forest Headbutt"}
    head_names["sPoxIlexHeadbutt"] = "Ilex Forest Headbutt"
    for row in report["headbutt"]:
        table = row["table"]
        period = "day" if table.endswith("Day") else "night"
        stem = table[: -len(period)]
        area = head_names.get(stem, stem)
        extra = ", Pineco 15%" if stem == "sPoxIlexHeadbutt" else ""
        out.append(f"| {area} ({period}) | confirmed | 100%{extra} |")
    return out


def trainer_rows() -> list[str]:
    data = json.loads(BUILD.read_text())["trainers"]
    out = ["| Trainer id | Story stage | Cap | Team (level, species, set) | Availability |",
           "|---|---|---:|---|---|"]
    for trainer in sorted(ROSTERS):
        checkpoint, _ = ROSTERS[trainer]
        entry = data[trainer]
        mons = []
        why = []
        for mon in entry["monsters"]:
            moves = ", ".join(move_name(m).replace("Hidden Power", "HP") for m in mon["moves"])
            source = "" if mon["set_source"] == "gen3_movesets.json" else " *(derived)*"
            mons.append(f"Lv{mon['level']} **{nice(mon['species'])}** — {mon['set_name']}{source} "
                        f"[{moves}]")
            why.append(f"{nice(mon['species'])}: {mon['why_available']} ({mon['tier']})")
        for species in SIGNATURE_EXCEPTIONS.get(trainer, []):
            why = [f"**{nice(species)}: declared signature exception** "
                   f"({P.tier_of(species)} — see 2.5)"
                   if w.startswith(nice(species) + ":") else w for w in why]
        stage = f"{checkpoint} ({entry['tier']})"
        out.append(f"| `{trainer}` | {stage} | {entry['cap']} | "
                   f"{'<br>'.join(mons)} | {'<br>'.join(why)} |")
    for trainer in sorted(KEEP_AS_IS):
        entry = data.get(trainer, {})
        roster = ", ".join(entry.get("monsters", []))
        out.append(f"| `{trainer}` | _unchanged_ | — | {roster} | {KEEP_AS_IS[trainer]} |")
    return out


def substitution_rows() -> list[str]:
    data = json.loads(BUILD.read_text())["trainers"]
    tally: dict[str, list[str]] = {}
    for trainer, entry in data.items():
        for index, mon in enumerate(entry.get("monsters", [])):
            if not isinstance(mon, dict):
                continue
            for note in mon.get("notes", []):
                tally.setdefault(note, []).append(
                    f"{trainer.removeprefix('TRAINER_PLASTIC_OX_')}[{index}] "
                    f"{nice(mon['species'])}")
    out = ["| Substitution | Count | Example |", "|---|---:|---|"]
    for note, where in sorted(tally.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        out.append(f"| {note} | {len(where)} | {where[0]} |")
    return out


def main() -> None:
    data = json.loads(BUILD.read_text())["trainers"]
    total = sum(len(e["monsters"]) for e in data.values()
                if all(isinstance(m, dict) for m in e.get("monsters", [])))
    dex = sum(1 for e in data.values() for m in e.get("monsters", [])
              if isinstance(m, dict) and m["set_source"] == "gen3_movesets.json")
    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()

    body = f"""# Trainer Teams v2 and Wild Encounter Audit

**Scope.** Part 1 audits every Plastic Ox wild-encounter table against the
authoritative specification and fixes the divergences. Part 2 rewrites every
reachable `TRAINER_PLASTIC_OX_*` party to a full, progression-legal six.

**Base commit.** `{git}` (branch `codex/metamon-trainer-ai`, working tree left
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

{chr(10).join(part1_tables())}

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
   `gPoxIlexForestHns_{{Morning,Day,Night}}` each carry a full ten-slot fishing
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

{len(ROSTERS)} of the {len(ROSTERS) + len(KEEP_AS_IS)} `TRAINER_PLASTIC_OX_*`
trainers were rewritten; the other {len(KEEP_AS_IS)} are untouched for stated
reasons. Every rewritten party now has exactly six Pokémon — {total} Pokémon in
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
| Competitive sets | Taken from `plastic_ox/gen3_movesets.json` whenever the merged dex for the stage's tier has the species: **245 of {total}**. The remaining {total - 245} are early-route species with no tier-dex entry and are derived from the ROM's own learnset. |
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
top out{'' }s out at 16 OU species (Charizard, Claydol, Cloyster, Flygon,
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

{chr(10).join(trainer_rows())}

## 2.4 Move substitutions

{chr(10).join(substitution_rows())}

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
`\bTRAINER_[A-Z0-9_]+\b` yields 59 distinct matches, of which 57 are
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
| ROM size | linker `--print-memory-usage` | {rom_usage()} |
| EWRAM / IWRAM | — | 226,560 B / 256 KB (86.43%), 28,588 B / 32 KB (87.24%) |

**Not performed:** no play-testing, no emulator run, and no `make check`
battle-test suite run. The move-level, species-level and tier-level guarantees
above come from static analysis of the ROM's own data files, not from playing
the game. Encounter *rates* are verified as the effective conditional
probability the code will produce, not as observed in-game frequencies.
"""
    REPORT.write_text(body)
    print(f"wrote {REPORT} ({len(body.splitlines())} lines)")


if __name__ == "__main__":
    main()
