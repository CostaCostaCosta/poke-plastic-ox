#!/usr/bin/env python3
"""Species-clause and under-evolution audit for every trainer in trainers.party.

Two rules, applied to *all* trainers (vanilla Hoenn/FRLG/HNS entries as well as
TRAINER_PLASTIC_OX_*):

  * species clause: no species appears twice on one team;
  * no under-evolved Pokemon: a Pokemon whose Gen 3 evolution happens by plain
    level-up (EVO_LEVEL with a real level, so not friendship/stone/trade) must
    not sit at or above that evolution level. For Plastic Ox trainers that have
    a story checkpoint (apply_trainer_teams_v2.ROSTERS) the evolved form must
    also be legal at that checkpoint (pox_progression.legal_for) for it to
    count, so an LC-block Abra or a tier-locked middle stage stays allowed.

Run:  python3 plastic_ox/tools/audit_trainer_species.py   (exit 1 on findings)
test_trainer_teams_v2.py imports audit() and fails on any finding.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pox_progression as P  # noqa: E402

PARTY = P.ROOT / "src/data/trainers.party"

# (trainer, species) pairs deliberately kept below their evolution level.
UNDEREVOLVED_EXCEPTIONS: set[tuple[str, str]] = set()

# Authored (KEEP_AS_IS) Plastic Ox teams that still have a story checkpoint.
EXTRA_CHECKPOINTS = {
    "TRAINER_PLASTIC_OX_WEATHER": "fortree",        # Magneton is OU, Magnemite stays
    "TRAINER_PLASTIC_OX_WEATHER_DEVON": "fortree",
    # Retired one-dancer Kimono battles (superseded by KIMONO_TROUPE); their
    # Ecruteak checkpoint still decides which evolutions count.
    **{f"TRAINER_PLASTIC_OX_KIMONO{s}": "gym3"
       for s in ("VAPOREON", "JOLTEON", "FLAREON", "ESPEON", "UMBREON")},
}


@lru_cache(maxsize=None)
def level_evolutions() -> dict[str, list[tuple[str, int]]]:
    """species -> [(Gen 3 evolution, level)] for plain level-up evolutions."""
    gen3 = P.load_tiers()
    out: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for target, sources in P.load_evolutions().items():
        if target not in gen3:
            continue
        for source, method, level, _raw in sources:
            if method == "EVO_LEVEL" and level > 0:
                out[source].append((target, level))
    return dict(out)


def underevolved(species: str, level: int, legal: set[str] | None = None) -> list[tuple[str, int]]:
    """The evolutions this Pokemon should already have taken."""
    return [(t, lv) for t, lv in level_evolutions().get(species, [])
            if level >= lv and (legal is None or t in legal)]


def audit(parsed: dict[str, str] | None = None) -> list[str]:
    from test_trainer_teams_v2 import parse, parse_mon
    from apply_trainer_teams_v2 import ROSTERS, split_block
    if parsed is None:
        parsed = parse(PARTY.read_text())
    legal_cache: dict[str, set[str]] = {}
    problems: list[str] = []
    for trainer, body in parsed.items():
        _header, blocks = split_block(body)
        mons = [parse_mon(b) for b in blocks]
        seen: set[str] = set()
        for index, mon in enumerate(mons):
            if mon["species"] in seen:
                problems.append(f"{trainer}[{index}] duplicate species {mon['species']} (species clause)")
            seen.add(mon["species"])
        legal = None
        checkpoint = ROSTERS[trainer][0] if trainer in ROSTERS else EXTRA_CHECKPOINTS.get(trainer)
        if checkpoint:
            if checkpoint not in legal_cache:
                legal_cache[checkpoint] = set(P.legal_for(checkpoint))
            legal = legal_cache[checkpoint]
        for index, mon in enumerate(mons):
            if (trainer, mon["species"]) in UNDEREVOLVED_EXCEPTIONS:
                continue
            for target, lv in underevolved(mon["species"], mon["level"], legal):
                problems.append(f"{trainer}[{index}] {mon['species']} Lv{mon['level']} is "
                                f"under-evolved ({target} at Lv{lv})")
    return problems


def main() -> int:
    problems = audit()
    for p in problems:
        print("FAIL:", p)
    print(f"{len(problems)} species-clause / under-evolution finding(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
