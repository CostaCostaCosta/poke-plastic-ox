#!/usr/bin/env python3
"""Regression checks for the Plastic Ox trainer parties.

Re-reads src/data/trainers.party (the file trainerproc actually compiles, not
the generator's in-memory model) and asserts, for every TRAINER_PLASTIC_OX_*
entry:

  * exactly six Pokemon;
  * every species is obtainable at or before the trainer's story checkpoint and
    sits in a competitive tier that is unlocked by then (the Dance Theater
    signature Eeveelutions are the one declared exception);
  * no level exceeds the story level cap for that checkpoint;
  * every move is one the species can legally know at that level, and every
    ability is really one of that species' abilities;
  * EV totals stay inside the 510 cap and no stat exceeds 252;
  * trainer ids, names, classes, pics, music, battle type and AI lines are
    unchanged from the pre-overhaul baseline, so no wiring moved.

Run:  python3 plastic_ox/agent/test_trainer_teams_v2.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pox_progression as P  # noqa: E402
from apply_trainer_teams_v2 import (  # noqa: E402
    KEEP_AS_IS, ROSTERS, SIGNATURE_EXCEPTIONS, split_block,
)

PARTY = P.ROOT / "src/data/trainers.party"
BASELINE = HERE / "trainer_headers_baseline.json"
HEADER_FIELDS = ("Name:", "Class:", "Pic:", "Gender:", "Music:", "Double Battle:",
                 "AI:", "Battle Type:", "Items:", "Mugshot:", "Multi Party:")
STAT_ORDER = ("hp", "atk", "def", "spa", "spd", "spe")

ABILITIES = P.load_abilities()
for alias, target in P.load_species_aliases().items():
    ABILITIES.setdefault(alias, ABILITIES.get(target, []))


def display(species: str) -> str:
    name = species.removeprefix("SPECIES_").replace("_", " ").title()
    return {"Nidoran F": "Nidoran♀", "Nidoran M": "Nidoran♂", "Mr. Mime": "Mr. Mime",
            "Ho Oh": "Ho-Oh", "Farfetchd": "Farfetch'd", "Mime Jr": "Mime Jr."}.get(name, name)


DISPLAY_FIX = {"Nidoran♀": "NIDORAN_F", "Nidoran♂": "NIDORAN_M", "Farfetch'd": "FARFETCHD",
               "Mr. Mime": "MR_MIME", "Ho-Oh": "HO_OH", "Mime Jr.": "MIME_JR",
               "Type: Null": "TYPE_NULL"}


def species_const(display_name: str) -> str:
    """The .party writes the species the way the game does; map it back."""
    if display_name in DISPLAY_FIX:
        return "SPECIES_" + DISPLAY_FIX[display_name]
    return "SPECIES_" + re.sub(r"[^A-Za-z0-9]", "", display_name).upper()


def parse(text: str) -> dict[str, str]:
    parts = re.split(r"^=== (\w+) ===$", text, flags=re.MULTILINE)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}


def parse_mon(block: str) -> dict:
    lines = block.splitlines()
    head = lines[0]
    name = head.split(" @ ")[0]
    mon = {"name": name.strip(), "species": species_const(name.split(" (")[0]),
           "item": head.split(" @ ")[1].strip() if " @ " in head else "",
           "level": 0, "moves": [], "ability": "", "evs": {}, "ivs": {}, "nature": ""}
    for line in lines[1:]:
        if line.startswith("- "):
            mon["moves"].append(P.move_id(line[2:].strip()) or line[2:].strip())
        elif line.startswith("Level:"):
            mon["level"] = int(line.split(":", 1)[1])
        elif line.startswith("Ability:"):
            mon["ability"] = line.split(":", 1)[1].strip()
        elif line.startswith("Nature"):
            mon["nature"] = line.split(" ", 1)[0].strip()
        elif line.startswith(("EVs:", "IVs:")):
            key, _, rest = line.partition(":")
            stats = {}
            for chunk in rest.split("/"):
                value, _, stat = chunk.strip().partition(" ")
                stats[{"HP": "hp", "Atk": "atk", "Def": "def",
                       "SpA": "spa", "SpD": "spd", "Spe": "spe"}[stat.strip()]] = int(value)
            mon["evs" if key == "EVs" else "ivs"] = stats
    return mon


def main() -> int:
    text = PARTY.read_text()
    parsed = parse(text)
    problems: list[str] = []
    checked = 0

    pox = sorted(k for k in parsed if k.startswith("TRAINER_PLASTIC_OX"))
    for trainer in pox:
        if trainer not in ROSTERS and trainer not in KEEP_AS_IS:
            problems.append(f"{trainer}: no checkpoint assigned and not in KEEP_AS_IS")
    for trainer in ROSTERS:
        if trainer not in parsed:
            problems.append(f"{trainer}: missing from trainers.party")

    for trainer in sorted(ROSTERS):
        checkpoint, _roster = ROSTERS[trainer]
        legal = P.legal_for(checkpoint)
        cap = P.cap_at(checkpoint)
        allowed = set(SIGNATURE_EXCEPTIONS.get(trainer, []))
        header, blocks = split_block(parsed[trainer])
        checked += 1
        if len(blocks) != 6:
            problems.append(f"{trainer}: {len(blocks)} Pokemon, expected 6")
            continue
        for index, block in enumerate(blocks):
            mon = parse_mon(block)
            species = mon["species"]
            checked += 1
            if species not in legal and species not in allowed:
                problems.append(f"{trainer}[{index}] {species} is not obtainable at "
                                f"'{checkpoint}' (tier {P.tier_of(species)})")
            checked += 1
            if mon["level"] > cap:
                problems.append(f"{trainer}[{index}] level {mon['level']} exceeds the "
                                f"{checkpoint} cap of {cap}")
            if not 1 <= mon["level"] <= 100:
                problems.append(f"{trainer}[{index}] level {mon['level']} out of range")
            abilities = {a.replace("_", " ").lower() for a in ABILITIES.get(species, [])}
            checked += 1
            if mon["ability"] and mon["ability"].lower() not in abilities:
                problems.append(f"{trainer}[{index}] {display(species)} has no ability "
                                f"'{mon['ability']}'")
            ev_total = sum(mon["evs"].values())
            checked += 1
            if ev_total > 510:
                problems.append(f"{trainer}[{index}] EVs total {ev_total} (> 510)")
            if any(v > 252 for v in mon["evs"].values()):
                problems.append(f"{trainer}[{index}] an EV exceeds 252")
            if any(v > 31 or v < 0 for v in mon["ivs"].values()):
                problems.append(f"{trainer}[{index}] an IV is out of range")
            if mon["nature"] and mon["nature"] not in P.load_natures():
                problems.append(f"{trainer}[{index}] unknown nature {mon['nature']}")
            for move in mon["moves"]:
                checked += 1
                ok, why = P.move_legal(species, move, mon["level"])
                if not ok:
                    problems.append(f"{trainer}[{index}] {display(species)} cannot know "
                                    f"{move} at Lv{mon['level']} ({why})")

    # wiring: the trainer header block must be byte-identical to the baseline
    if BASELINE.exists():
        baseline = json.loads(BASELINE.read_text())
        for trainer, expected in baseline.items():
            if trainer not in parsed:
                problems.append(f"{trainer}: present in the baseline but gone now")
                continue
            header, _ = split_block(parsed[trainer])
            actual = "\n\n".join(header)
            checked += 1
            if actual != expected:
                problems.append(f"{trainer}: header block changed")
    else:
        print(f"note: {BASELINE.name} not present, skipping the header-stability check")

    for problem in problems:
        print("FAIL:", problem)
    if problems:
        print(f"{len(problems)} failure(s) across {checked} checks")
        return 1
    print(f"PASS: {checked} trainer-party checks over {len(pox)} Plastic Ox trainers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
