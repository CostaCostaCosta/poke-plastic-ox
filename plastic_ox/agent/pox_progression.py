#!/usr/bin/env python3
"""Plastic Ox trainer-team progression model.

Shared by the team generator and the report writer. Answers four questions for
any story checkpoint:

* which wild and special acquisitions the player has made by then;
* which evolutions of those the player can legally make by then (level cap,
  released stones, unlocked competitive tier);
* which competitive tier is unlocked (src/data/pokemon/evolution_tier_gates.h);
* which moves a species can legally have (src/data/pokemon/all_learnables.json
  plus the level-up learnset, because Birch hands over every TM, HM and tutor
  move in the opening scene).

Story order follows plastic_ox/alpha/REGION_PLAN.md, plastic_ox/alpha/
story_manifest.json and the encounter tables audited in Part 1.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TIER_ORDER = ["LC", "PU", "NU", "RU", "UU", "UUBL", "OU"]

# --------------------------------------------------------------------------
# Tiers (the engine's own table, so the model cannot drift from the ROM)
# --------------------------------------------------------------------------
def load_tiers() -> dict[str, str]:
    """SPECIES_X -> tier, from src/data/pokemon/evolution_tier_gates.h."""
    text = (ROOT / "src/data/pokemon/evolution_tier_gates.h").read_text()
    return {"SPECIES_" + sp: tier
            for sp, tier in re.findall(r"\[SPECIES_(\w+)\]\s*=\s*EVO_TIER_(\w+)", text)}


# --------------------------------------------------------------------------
# Wild species per area
# --------------------------------------------------------------------------
FIELDS = ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons", "hidden_mons")


def load_wild() -> dict[str, set[str]]:
    """base_label -> set of SPECIES_, for every Plastic Ox encounter header."""
    data = json.loads((ROOT / "src/data/wild_encounters.json").read_text())
    out: dict[str, set[str]] = {}
    for e in data["wild_encounter_groups"][0]["encounters"]:
        if not e["base_label"].startswith("gPox"):
            continue
        bag = out.setdefault(e["base_label"], set())
        for field in FIELDS:
            for m in e.get(field, {}).get("mons", []):
                bag.add(m["species"])
    return out


# Headbutt tables live in a C header rather than the JSON; symbol -> species.
# Only these maps carry a PlasticOx_EventScript_HeadbuttTree object, so only
# these tables are reachable in play. Route 29, Route 46, Route 44, Route 24
# and Route 25 had tables with no tree and were dropped from the header.
HEADBUTT_SYMBOLS = {
    "MAP_ILEX_FOREST_HNS": "sPoxIlexHeadbutt",
    "MAP_ROUTE33_HNS": "sPoxRoute33Headbutt",
    "MAP_ROUTE35_HNS": "sPoxRoute35Headbutt",
    "MAP_NATIONAL_PARK_NORMAL_HNS": "sPoxParkHeadbutt",
    "MAP_ROUTE36_HNS": "sPoxRoute36Headbutt",
    "MAP_ROUTE37_HNS": "sPoxRoute37Headbutt",
}
# Kept separately so the NU-block analysis can say "reachable" vs "defined".
HEADBUTT_TREE_MAPS = frozenset(HEADBUTT_SYMBOLS)


def load_headbutt() -> dict[str, set[str]]:
    """symbol -> set of SPECIES_ (day and night pooled)."""
    text = (ROOT / "src/data/plastic_ox_pu_encounters.h").read_text()
    out: dict[str, set[str]] = {}
    for symbol, body in re.findall(
            r"static const struct WildPokemon (\w+)Mons\[\] = \{(.*?)\n\};", text, re.S):
        if symbol.endswith(("Day", "Night")):
            out[symbol] = {f"SPECIES_{m}" for m in re.findall(r"\{ \d+, \d+, SPECIES_(\w+) \}", body)}
    return out


# --------------------------------------------------------------------------
# Story order.
#
# CHECKPOINTS is the ordered story spine. Each entry is
#   (name, tier, level cap, wild headers added, headbutt maps added)
# A header of the form "PREFIX#Tag" matches every gPox header starting with
# PREFIX, so Route 2 South and Route 2 North stay separate even though they
# share MAP_ROUTE2.
# --------------------------------------------------------------------------
CHECKPOINTS = [
    ("start",       "LC",   13, ["gPoxPalletTown", "gPoxRoute101"], []),
    ("oldale",      "LC",   13, ["gPoxOldaleTown"], []),
    ("route103",    "LC",   13, ["gPoxRoute103#"], []),
    ("route29",     "LC",   13, ["gPoxRoute29Hns#"], []),
    ("cherrygrove", "LC",   13, ["gPoxCherrygroveCityHns"], []),
    ("route2south", "LC",   13, ["gPoxRoute2South#"], []),
    ("ilex",        "LC",   13, ["gPoxIlexForestHns#"], ["MAP_ILEX_FOREST_HNS"]),
    ("route2north", "LC",   13, ["gPoxRoute2North#", "gPoxDarkCaveSouthSideHns#"], []),
    ("route46",     "LC",   13, ["gPoxRoute46Hns#"], []),
    ("route24",     "LC",   13, ["gPoxRoute24Hns#"], []),
    ("route25",     "LC",   13, ["gPoxRoute25Hns#"], []),
    ("gym1",        "LC",   13, [], []),                                    # Roxanne, Rustboro
    ("route44",     "PU",   20, ["gPoxRoute44Hns"], []),
    ("mtmoon",      "PU",   20, ["gPoxPUMtMoonCaveHns#", "gPoxPUMtMoon1F#"], []),
    ("mtmoondeep",  "PU",   20, ["gPoxPUMtMoonB1F#", "gPoxPUMtMoonB2F#"], []),
    ("route33",     "PU",   20, ["gPoxPURoute33Hns#"], ["MAP_ROUTE33_HNS"]),
    ("gym2",        "PU",   20, [], []),                                    # Whitney, Goldenrod
    ("route35",     "NU",   30, ["gPoxPURoute35Hns#"], ["MAP_ROUTE35_HNS"]),
    ("park",        "NU",   30, ["gPoxPUNationalParkNormalHns#"], ["MAP_NATIONAL_PARK_NORMAL_HNS"]),
    ("route36",     "NU",   30, ["gPoxPURoute36Hns#"], ["MAP_ROUTE36_HNS"]),
    ("goldenrod",   "NU",   30, [], []),          # Bill's Eevee, Beldum trade, Game Corner, mail Delibird
    ("ecruteak",    "NU",   30, [], []),          # Kimono Girls; Route 36 odd-tree Sudowoodo
    ("route37",     "NU",   30, ["gPoxNURoute37Hns#"], ["MAP_ROUTE37_HNS"]),
    ("burnedtower", "NU",   30, ["gPoxNUEcruteakCityHns", "gPoxNUBurnedTower1F",
                                "gPoxNUBurnedTowerB1F"], []),
    ("gym3",        "NU",   30, [], []),          # Morty, Dance Theater
    ("fortree",     "RU",   36, [], []),          # Route 119, Weather Institute, Fortree
    ("cinnabar",    "UU",   42, [], []),          # Lavender tower, Cinnabar
    ("mossdeep",    "UUBL", 50, [], []),          # Mossdeep gym
    ("saffron",     "OU",   55, [], []),          # Silph
    ("blackthorn",  "OU",   60, [], []),          # Clair
    ("victoryroad", "OU",   60, [], []),
    ("league",      "OU",   62, [], []),          # Wallace, Steven, Lance
    ("postgame",    "OU",   64, [], []),          # Blue, Bill
]

# Non-wild acquisitions, keyed by the checkpoint that unlocks them.
SPECIALS = {
    "start": ["SPECIES_BULBASAUR", "SPECIES_CHARMANDER", "SPECIES_SQUIRTLE",
              "SPECIES_CHIKORITA", "SPECIES_CYNDAQUIL", "SPECIES_TOTODILE",
              "SPECIES_TREECKO", "SPECIES_TORCHIC", "SPECIES_MUDKIP"],
    "route25": ["SPECIES_KABUTO", "SPECIES_ANORITH", "SPECIES_LILEEP"],  # Sea Cottage fossils
    "goldenrod": ["SPECIES_EEVEE", "SPECIES_BELDUM",         # Bill's family / Devon trade
                  "SPECIES_CASTFORM", "SPECIES_LUVDISC", "SPECIES_DELIBIRD"],
    "ecruteak": ["SPECIES_SUDOWOODO"],                                # Route 36 odd tree
}

# Evolution items and the checkpoint that distributes them. The source document
# that used to own this schedule, plastic_ox/plasticox_encounters_v1.md, has been
# retired; the table is embedded here so the model stays self-contained.
ITEM_CHECKPOINT = {
    "ITEM_MOON_STONE": "gym2", "ITEM_SUN_STONE": "gym2",
    "ITEM_FIRE_STONE": "route35", "ITEM_DEEP_SEA_TOOTH": "route35",
    "ITEM_THUNDER_STONE": "fortree", "ITEM_WATER_STONE": "fortree",
    "ITEM_LEAF_STONE": "fortree", "ITEM_KINGS_ROCK": "fortree",
    "ITEM_LINKING_CORD": "cinnabar", "ITEM_DEEP_SEA_SCALE": "cinnabar",
    "ITEM_METAL_COAT": "mossdeep", "ITEM_DRAGON_SCALE": "mossdeep",
    "ITEM_UP_GRADE": "saffron",
}

CHECKPOINT_NAMES = [c[0] for c in CHECKPOINTS]
CHECKPOINT_INDEX = {c[0]: i for i, c in enumerate(CHECKPOINTS)}


def _match_wild(wild: dict[str, set[str]], spec: str) -> set[str]:
    if "#" in spec:
        prefix = spec.split("#", 1)[0]
        return {s for label, bag in wild.items() if label.startswith(prefix) for s in bag}
    return set(wild.get(spec, set()))


def acquired_at(checkpoint: str) -> set[str]:
    """Species the player has in hand at `checkpoint`: wild tables so far,
    their Headbutt tables, and every special acquisition released so far."""
    upto = CHECKPOINT_INDEX[checkpoint]
    wild = load_wild()
    headbutt = load_headbutt()
    have: set[str] = set()
    for name, _tier, _cap, wild_specs, hb_maps in CHECKPOINTS[: upto + 1]:
        for spec in wild_specs:
            have |= _match_wild(wild, spec)
        for hb_map in hb_maps:
            symbol = HEADBUTT_SYMBOLS[hb_map]
            have |= headbutt.get(symbol + "Day", set()) | headbutt.get(symbol + "Night", set())
        have |= set(SPECIALS.get(name, []))
    return have


def tier_at(checkpoint: str) -> str:
    return CHECKPOINTS[CHECKPOINT_INDEX[checkpoint]][1]


def cap_at(checkpoint: str) -> int:
    return CHECKPOINTS[CHECKPOINT_INDEX[checkpoint]][2]


def tiers_unlocked(checkpoint: str) -> set[str]:
    return set(TIER_ORDER[: TIER_ORDER.index(tier_at(checkpoint)) + 1])


# --------------------------------------------------------------------------
# Evolution-derived availability
# --------------------------------------------------------------------------
def _evolution_specs(body: str) -> list[str]:
    """Every `EVOLUTION({...}, {...})` argument list in a species entry.

    The macro takes a comma-separated list of brace initialisers, so the span
    runs to the parenthesis that balances the one after EVOLUTION.
    """
    out = []
    i = 0
    while True:
        start = body.find("EVOLUTION(", i)
        if start < 0:
            return out
        depth = 0
        j = start + len("EVOLUTION")
        while j < len(body):
            if body[j] == "(":
                depth += 1
            elif body[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(body[start:j + 1])
        i = j + 1


def _initialisers(spec: str) -> list[str]:
    """The individual `{...}` argument initialisers inside one EVOLUTION(...) call."""
    out = []
    depth = 0
    begin = 0
    for idx, ch in enumerate(spec):
        if ch == "{":
            if depth == 0:
                begin = idx
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append(spec[begin:idx + 1])
    return out


def load_evolutions() -> dict[str, list[tuple[str, str, int, str]]]:
    """target SPECIES_X -> [(source, method, level, full-spec-text)]."""
    out: dict[str, list[tuple[str, str, int, str]]] = {}
    for path in sorted((ROOT / "src/data/pokemon/species_info").glob("*.h")):
        text = path.read_text()
        for name, body in re.findall(r"\[SPECIES_(\w+)\]\s*=\s*\{(.*?)\n    \},", text, re.S):
            source = "SPECIES_" + name
            for spec in _evolution_specs(body):
                for init in _initialisers(spec):
                    m = re.search(r"EVO_(\w+),\s*([^,]+),\s*SPECIES_(\w+)", init)
                    if not m:
                        continue
                    method = "EVO_" + m.group(1)
                    arg, target = m.group(2).strip(), "SPECIES_" + m.group(3)
                    level = int(arg) if method == "EVO_LEVEL" and arg.isdigit() else 0
                    out.setdefault(target, []).append((source, method, level, init))
    return out


def _pretty(species: str) -> str:
    return species.removeprefix("SPECIES_").replace("_", " ").title()


def obtainable_at(checkpoint: str) -> dict[str, str]:
    """SPECIES_X -> how the player can hold it at `checkpoint`.

    A species counts when it is a wild/special acquisition, or when a species
    already held evolves into it under a requirement the checkpoint has met:
    level evolutions must land at or under the level cap, non-level evolutions
    need any released stone, and friendship / trade / time-of-day triggers
    count as always reachable.
    """
    upto = CHECKPOINT_INDEX[checkpoint]
    cap = cap_at(checkpoint)
    tiers = tiers_unlocked(checkpoint)
    tier_table = load_tiers()

    reason = {s: "wild / special acquisition" for s in acquired_at(checkpoint)}
    evolutions = load_evolutions()
    changed = True
    while changed:
        changed = False
        for target, sources in evolutions.items():
            if target in reason:
                continue
            target_tier = tier_table.get(target)
            if target_tier and target_tier not in tiers:
                continue                       # the evolution is still tier-locked
            for source, method, level, spec in sources:
                if source not in reason:
                    continue
                if method == "EVO_LEVEL":
                    if level and level > cap:
                        continue               # would need to break the level cap
                    reason[target] = f"evolves from {_pretty(source)} at Lv{level or 1}"
                else:
                    gated = next((f"ITEM_{i}" for i in re.findall(r"ITEM_(\w+)", spec)
                                  if f"ITEM_{i}" in ITEM_CHECKPOINT), None)
                    if gated and CHECKPOINT_INDEX[ITEM_CHECKPOINT[gated]] > upto:
                        continue               # stone not distributed yet
                    how = (gated.removeprefix("ITEM_").title() if gated
                           else method.removeprefix("EVO_").lower())
                    reason[target] = f"evolves from {source.removeprefix('SPECIES_')} ({how})"
                changed = True
                break
    return reason


def legal_at(checkpoint: str) -> dict[str, str]:
    """obtainable_at, minus anything whose competitive tier is still locked."""
    tiers = tiers_unlocked(checkpoint)
    tier_table = load_tiers()
    return {s: how for s, how in obtainable_at(checkpoint).items()
            if tier_table.get(s) is None or tier_table[s] in tiers}


# The v5.5 pre-Mt. Moon block deliberately places a number of PU-tier species in
# the zero-badge LC areas (Voltorb and Koffing on Route 2 North, Trapinch on
# Route 46, Cubone and Rhyhorn and Slugma on Route 46, Cubone's line via Route
# 25, Doduo on Route 25, and so on). plastic_ox/encounter_tables/
# plastic_ox_pre_mt_moon_encounters_v5_5_agent_ready.md is the authoritative
# end state for those tables, so the same species are legal for trainers in the
# Gym 1 block even though the shipped release schedule in
# src/data/pokemon/evolution_tier_gates.h gates them at Gym 2.
LC_BLOCK = ("start", "oldale", "route103", "route29", "cherrygrove", "route2south",
            "ilex", "route2north", "route46", "route24", "route25", "gym1")
LC_BLOCK_WILD = ["gPoxPalletTown", "gPoxRoute101", "gPoxOldaleTown", "gPoxRoute103#",
                 "gPoxRoute29Hns#", "gPoxCherrygroveCityHns", "gPoxRoute2South#",
                 "gPoxIlexForestHns#", "gPoxRoute2North#", "gPoxDarkCaveSouthSideHns#",
                 "gPoxRoute46Hns#", "gPoxRoute24Hns#", "gPoxRoute25Hns#"]
# Ilex Forest is the only LC area left with a Headbutt tree; Route 29, Route 46,
# Route 24 and Route 25 lost their unreachable tables.
LC_BLOCK_HEADBUTT = ["MAP_ILEX_FOREST_HNS"]


def lc_block_exceptions() -> set[str]:
    """PU-tier species the v5.5 LC block itself puts in the player's hands:
    its wild and Headbutt tables plus the three Sea Cottage fossil rewards."""
    wild = load_wild()
    headbutt = load_headbutt()
    tier_table = load_tiers()
    pool: set[str] = set()
    for spec in LC_BLOCK_WILD:
        pool |= _match_wild(wild, spec)
    for hb_map in LC_BLOCK_HEADBUTT:
        symbol = HEADBUTT_SYMBOLS[hb_map]
        pool |= headbutt.get(symbol + "Day", set()) | headbutt.get(symbol + "Night", set())
    pool |= set(SPECIALS["route25"])            # Kabuto / Anorith / Lileep
    return {s for s in pool if tier_table.get(s) == "PU"}


def legal_for(checkpoint: str) -> dict[str, str]:
    """The pool a trainer at `checkpoint` may draw from, with the v5.5 LC
    block's own PU species admitted during the Gym 1 segment."""
    out = legal_at(checkpoint)
    if checkpoint in LC_BLOCK:
        for s in lc_block_exceptions():
            if s in obtainable_at(checkpoint):
                out[s] = "v5.5 LC-block wild table"
    return out


def tier_of(species: str) -> str:
    return load_tiers().get(species, "?")


def load_abilities() -> dict[str, list[str]]:
    """SPECIES_X -> its real ability names, in slot order.

    A few species (Gengar, Giratina, ...) name their ability list with a macro,
    so those are resolved against the file's own #defines.
    """
    out: dict[str, list[str]] = {}
    for path in sorted((ROOT / "src/data/pokemon/species_info").glob("*.h")):
        text = path.read_text()
        defines = dict(re.findall(r"#define\s+(\w+_ABILITIES)\s+\{([^}]*)\}", text))
        for name, body in re.findall(r"\[SPECIES_(\w+)\]\s*=\s*\{(.*?)\n    \},", text, re.S):
            m = re.search(r"\.abilities\s*=\s*(\{[^}]*\}|\w+)", body)
            if not m:
                continue
            raw = m.group(1)
            if not raw.startswith("{"):
                raw = defines.get(raw, "")
            out["SPECIES_" + name] = [a for a in
                                      (x.strip("{} \t").removeprefix("ABILITY_")
                                       for x in raw.split(","))
                                      if a and a != "NONE"]
    return out


def load_natures() -> list[str]:
    text = (ROOT / "include/constants/pokemon.h").read_text()
    return [n.removeprefix("NATURE_").title() for n in re.findall(r"#define NATURE_(\w+)", text)
            if n not in ("NUM_NATURES", "NUM_NATURES_WITH_MOVES")]


def load_species_types() -> dict[str, list[str]]:
    """SPECIES_X -> its elemental types."""
    out: dict[str, list[str]] = {}
    for path in sorted((ROOT / "src/data/pokemon/species_info").glob("*.h")):
        for name, body in re.findall(r"\[SPECIES_(\w+)\]\s*=\s*\{(.*?)\n    \},", path.read_text(), re.S):
            m = re.search(r"\.types\s*=\s*MON_TYPES\(([^)]*)\)", body)
            if m:
                out["SPECIES_" + name] = [t.strip().removeprefix("TYPE_")
                                          for t in m.group(1).split(",")]
    return out


MOVE_META: dict[str, dict] = {}


def load_move_meta() -> dict[str, dict]:
    """MOVE_X -> {'name', 'type', 'power'} from src/data/moves_info.h."""
    if MOVE_META:
        return MOVE_META
    text = (ROOT / "src/data/moves_info.h").read_text()
    for name, body in re.findall(r"\[MOVE_(\w+)\]\s*=\s*\{(.*?)\n    \},", text, re.S):
        disp = re.search(r'\.name\s*=\s*COMPOUND_STRING\("([^"]+)"', body)
        typ = re.search(r"\.type\s*=\s*TYPE_(\w+)", body)
        power = re.search(r"\.power\s*=\s*([^,\n]+)", body)
        effect = re.search(r"\.effect\s*=\s*EFFECT_(\w+)", body)
        category = re.search(r"\.category\s*=\s*DAMAGE_CATEGORY_(\w+)", body)
        # `.power = COND ? new : old`; the old value is the one this ROM plays.
        nums = re.findall(r"\d+", power.group(1)) if power else []
        MOVE_META["MOVE_" + name] = {
            "name": disp.group(1) if disp else name.replace("_", " ").title(),
            "type": typ.group(1) if typ else "",
            "power": int(nums[-1]) if nums else 0,
            "effect": effect.group(1) if effect else "",
            "category": category.group(1) if category else "",
        }
    return MOVE_META


# --------------------------------------------------------------------------
# Move legality
# --------------------------------------------------------------------------
def load_learnables() -> dict[str, set[str]]:
    """Species -> every move it can learn in any generation.

    This is the cross-generation union the repo uses to build the teachable
    header; it is deliberately *not* what a trainer may know. Use
    `teachable_learnsets.h` for the real, per-ROM learnset.
    """
    return {k: set(v) for k, v in
            json.loads((ROOT / "src/data/pokemon/all_learnables.json").read_text()).items()}


def _species_learnset_symbols(field: str) -> dict[str, str]:
    """SPECIES_X -> the learnset array symbol species_info points that species at.

    Going through species_info keeps the awkward names (Nidoran_F, Farfetch'd)
    attached to the right array; deriving the symbol from the array name would
    not.
    """
    out: dict[str, str] = {}
    for path in sorted((ROOT / "src/data/pokemon/species_info").glob("*.h")):
        for name, body in re.findall(r"\[SPECIES_(\w+)\]\s*=\s*\{(.*?)\n    \},", path.read_text(), re.S):
            m = re.search(rf"\.{field}\s*=\s*s(\w+)\s*,?", body)
            if m:
                out["SPECIES_" + name] = m.group(1)
    return out


def load_teachable_by_species() -> dict[str, set[str]]:
    """Species -> the TM/HM/tutor moves it can actually be taught in this ROM.

    src/data/pokemon/teachable_learnsets.h is generated from the repo's own
    tms_hms.h and tutor list, so it is the authoritative "can a TM/tutor teach
    this to this species" answer.
    """
    text = (ROOT / "src/data/pokemon/teachable_learnsets.h").read_text()
    arrays = {name: {f"MOVE_{m}" for m in re.findall(r"MOVE_(\w+)", body) if m != "UNAVAILABLE"}
              for name, body in re.findall(r"s(\w+)\[\] = \{(.*?)\};", text, re.S)}
    out: dict[str, set[str]] = {}
    for species, symbol in _species_learnset_symbols("teachableLearnset").items():
        if symbol in arrays:
            out[species] = arrays[symbol]
    return out


def load_gen3_moves() -> set[str]:
    """Moves that existed in Generation 3.

    include/constants/moves.h numbers the moves in generation order, so every
    constant below MOVES_COUNT_GEN3 is a Gen 3 move. The dex sets in
    plastic_ox/gen3_movesets.json are Gen 3 sets, so derived sets stay in the
    same generation.
    """
    text = (ROOT / "include/constants/moves.h").read_text()
    gen3 = set(re.findall(r"MOVE_(\w+)\s*=", text[:text.index("MOVES_COUNT_GEN3")]))
    return {f"MOVE_{m}" for m in gen3}


def load_teachables() -> set[str]:
    """Every TM/HM and Move Tutor move.

    Birch hands the player the complete TM, HM and Move Compendium in the
    opening scene (data/scripts/plastic_ox_pallet.inc, Pox_ElmTMs), so a move
    on a TM, HM or tutor is in every trainer's hands at any story point.
    """
    tms = re.findall(r"F\((\w+)\)", (ROOT / "include/constants/tms_hms.h").read_text())
    tutors = re.findall(r"MOVE_(\w+)", (ROOT / "src/data/tutor_moves.h").read_text())
    return {f"MOVE_{m}" for m in tms} | {f"MOVE_{m}" for m in tutors}


def load_level_up() -> dict[str, dict[str, int]]:
    """SPECIES_X -> {MOVE_X: earliest level-up level}."""
    arrays: dict[str, str] = {}
    for path in sorted((ROOT / "src/data/pokemon/level_up_learnsets").glob("*.h")):
        for name, body in re.findall(
                r"LevelUpMove s(\w+)\[\] = \{(.*?)\n\};", path.read_text(), re.S):
            arrays[name] = body
    out: dict[str, dict[str, int]] = {}
    for species, symbol in _species_learnset_symbols("levelUpLearnset").items():
        body = arrays.get(symbol)
        if body is None:
            continue
        moves: dict[str, int] = {}
        for level, move in re.findall(r"LEVEL_UP_MOVE\(\s*(\d+),\s*MOVE_(\w+)\)", body):
            lvl, const = int(level), f"MOVE_{move}"
            if const not in moves or lvl < moves[const]:
                moves[const] = lvl
        out[species] = moves
    return out


def load_species_aliases() -> dict[str, str]:
    """SPECIES_X = SPECIES_Y aliases from include/constants/species.h.

    Several species are declared under a form name and re-exported under the
    bare name (SPECIES_CASTFORM is SPECIES_CASTFORM_NORMAL), so the learnset
    tables have to be reachable under both.
    """
    text = (ROOT / "include/constants/species.h").read_text()
    aliases: dict[str, str] = {}
    for name, target in re.findall(r"(SPECIES_\w+)\s*=\s*(SPECIES_\w+)\s*,", text):
        if name != target:
            aliases[name] = target
    for _ in range(4):                       # follow chains, defensively
        for name, target in list(aliases.items()):
            if target in aliases:
                aliases[name] = aliases[target]
    return aliases


def _with_aliases(table: dict) -> dict:
    """Return `table` with every alias key pointing at its target's entry."""
    out = dict(table)
    for alias, target in load_species_aliases().items():
        if target in table and alias not in table:
            out[alias] = table[target]
    return out


_CACHE: dict = {}


def _data(key):
    if key not in _CACHE:
        _CACHE[key] = {"learnables": load_learnables(), "level_up": load_level_up(),
                       "teachable": load_teachables(), "tiers": load_tiers(),
                       "by_species": load_teachable_by_species(),
                       "gen3": load_gen3_moves()}[key]
    return _CACHE[key]


def move_legal(species: str, move: str, level: int, gen3_only: bool = False) -> tuple[bool, str]:
    """Can `species` legally know `move` at `level` in Plastic Ox?

    Birch hands over every TM, HM and Move Tutor move in the opening scene, so
    anything the species can be taught is available at any level; otherwise the
    move has to be one it has reached by level-up.
    """
    if gen3_only and move not in _data("gen3"):
        return False, "not a Generation 3 move"
    taught = _with_aliases(_data("by_species")).get(species)
    if taught is None:
        return False, "no learnset"
    if move in taught or move in _data("teachable"):
        return True, "TM/HM/tutor"
    lvl = _with_aliases(_data("level_up")).get(species, {}).get(move)
    if lvl is None:
        if move in _data("learnables").get(species.removeprefix("SPECIES_"), set()):
            return False, "egg or special-case only"
        return False, "cannot learn"
    if lvl > level:
        return False, f"level-up move needs Lv{lvl}"
    return True, "level-up"


def legal_moves(species: str, level: int, gen3_only: bool = False) -> set[str]:
    taught = _with_aliases(_data("by_species"))
    learnt = _with_aliases(_data("level_up"))
    pool = (taught.get(species) or set()) | set(learnt.get(species, {}))
    return {m for m in pool if move_legal(species, m, level, gen3_only)[0]}


# --------------------------------------------------------------------------
# Competitive sets (plastic_ox/gen3_movesets.json)
# --------------------------------------------------------------------------
def load_movesets() -> dict[str, dict]:
    data = json.loads((ROOT / "plastic_ox/gen3_movesets.json").read_text())
    return {tier: data[tier]["dex"] for tier in data if "dex" in data[tier]}


DEX_NAME_FIX = {
    "FARFETCHD": "FARFETCHD", "NIDORANF": "NIDORAN_F", "NIDORANM": "NIDORAN_M",
    "MRMIME": "MR_MIME", "HOOH": "HO_OH", "TYPENULL": "TYPE_NULL",
    "MIMEJR": "MIME_JR", "FLABEBE": "FLABEBE", "FARFETCHD_": "FARFETCHD",
}
for _form in ("ATTACK", "DEFENSE", "SPEED"):
    DEX_NAME_FIX[f"DEOXYS_{_form}"] = f"DEOXYS_{_form}"


def dex_key(name: str) -> str:
    """gen3_movesets.json display name -> the repo's SPECIES_ constant."""
    squashed = re.sub(r"[^A-Za-z0-9]", "", name).upper()
    return "SPECIES_" + DEX_NAME_FIX.get(squashed, squashed)


TIER_DEX_ORDER = ["gen3lc", "gen3pu", "gen3nu", "gen3ru", "gen3uu", "gen3ubers", "gen3ou"]
# gen3ubers and gen3ou are the two endgame dexes; both are drawn on from UUBL
# onward. The twelve classic Ubers inside them have no pre-evolution and appear
# in no Plastic Ox encounter table, so `legal_for` keeps them out regardless.
TIER_OF_DEX = {"gen3lc": "LC", "gen3pu": "PU", "gen3nu": "NU", "gen3ru": "RU",
               "gen3uu": "UU", "gen3ubers": "UUBL", "gen3ou": "UUBL"}


def dex_for_tier(tier: str) -> dict:
    """Merged set dex for every tier at or below `tier`; the higher tier wins."""
    idx = TIER_ORDER.index(tier)
    dexes = load_movesets()
    merged: dict = {}
    for name in TIER_DEX_ORDER:               # low tier first so higher tiers win
        if TIER_ORDER.index(TIER_OF_DEX[name]) <= idx:
            merged.update({dex_key(k): v for k, v in dexes.get(name, {}).items()})
    return merged


def sets_for(dex: dict, species: str) -> list[tuple[str, dict]]:
    entry = dex.get(species) or {}
    return [(n, v) for n, v in entry.items() if isinstance(v, dict) and "moves" in v]


MOVE_IDS: dict[str, str] = {}


def move_id(display_name: str) -> str | None:
    """gen3_movesets.json move name -> MOVE_ constant, or None if unknown.

    The dex writes moves the way the game does ("Double-Edge", "Will-O-Wisp",
    "Hidden Power Grass"), so the lookup squashes punctuation and collapses
    Hidden Power's type suffix.
    """
    if not MOVE_IDS:
        for const, info in load_move_meta().items():
            MOVE_IDS.setdefault(re.sub(r"[^A-Za-z0-9]", "", info["name"]).upper(), const)
    squashed = re.sub(r"[^A-Za-z0-9]", "", display_name).upper()
    if squashed.startswith("HIDDENPOWER") and len(squashed) > len("HIDDENPOWER"):
        return "MOVE_HIDDEN_POWER"
    return MOVE_IDS.get(squashed)


def resolve_set_moves(names: list[str]) -> list[str]:
    return [m for m in (move_id(n) for n in names) if m]
