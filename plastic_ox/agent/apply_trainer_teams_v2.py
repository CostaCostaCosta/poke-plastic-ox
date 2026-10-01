#!/usr/bin/env python3
"""Rewrite every Plastic Ox trainer party to a full, progression-legal six.

Rules implemented here (see plastic_ox/agent/TRAINER_TEAMS_V2_REPORT.md):

* exactly six Pokemon per trainer;
* every species obtainable at or before the trainer's story checkpoint
  (pox_progression.CHECKPOINTS, derived from REGION_PLAN.md, the story manifest
  and the Part 1 encounter audit);
* levels at or a couple below the story level cap for that checkpoint;
* competitive tier unlocked at that checkpoint or lower;
* moves taken from plastic_ox/gen3_movesets.json where that tier's dex has the
  species, otherwise derived from the species' legal learnset at that level.
  Every move is re-checked against src/data/pokemon/all_learnables.json and the
  level-up learnsets, and illegal moves are substituted and recorded.

Trainer ids, names, classes, pics, music, battle type and AI lines are left
untouched; only the party body is replaced.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pox_progression as P  # noqa: E402

ROOT = P.ROOT
PARTY = ROOT / "src/data/trainers.party"
REPORT = Path(__file__).resolve().parent / "trainer_teams_v2_build.json"

# ---------------------------------------------------------------------------
# Rosters: trainer id -> (story checkpoint, [(species, level)] * 6)
#
# The six-species choice per trainer is authored here. Levels follow the story
# level-cap table (13 / 20 / 30 / 36 / 42 / 50 / 55 / 60) and sit a little under
# the cap for a trainer met part-way through its own segment, with the ace on
# the cap.
# ---------------------------------------------------------------------------
ROSTERS: dict[str, tuple[str, list[tuple[str, int]]]] = {
    # ---- opening routes, zero badges, LC cap 13 --------------------------
    # Wurmple is Route 101's mascot but the ROM gives it a three-move learnset
    # and no TMs, so a trainer copy would have nothing to work with; Goldeen
    # stands in here and Wurmple stays a wild-only encounter.
    "TRAINER_PLASTIC_OX_ROUTE101": ("start", [
        ("SPECIES_TAILLOW", 4), ("SPECIES_POOCHYENA", 3), ("SPECIES_GOLDEEN", 3),
        ("SPECIES_LOTAD", 3), ("SPECIES_SURSKIT", 3), ("SPECIES_POLIWAG", 3)]),
    "TRAINER_PLASTIC_OX_ROUTE103": ("route103", [
        ("SPECIES_WINGULL", 5), ("SPECIES_WHISMUR", 5), ("SPECIES_ELECTRIKE", 5),
        ("SPECIES_CACNEA", 5), ("SPECIES_GULPIN", 4), ("SPECIES_CORPHISH", 4)]),
    "TRAINER_PLASTIC_OX_ROUTE29": ("route29", [
        ("SPECIES_SENTRET", 5), ("SPECIES_PIDGEY", 4), ("SPECIES_NIDORAN_F", 4),
        ("SPECIES_NIDORAN_M", 4), ("SPECIES_MAREEP", 5), ("SPECIES_LEDYBA", 4)]),
    "TRAINER_PLASTIC_OX_ROUTE1": ("route2south", [
        ("SPECIES_MANKEY", 6), ("SPECIES_EKANS", 6), ("SPECIES_GROWLITHE", 6),
        ("SPECIES_VULPIX", 5), ("SPECIES_MEOWTH", 5), ("SPECIES_SLOWPOKE", 6)]),
    "TRAINER_PLASTIC_OX_ROUTE31": ("route2north", [
        ("SPECIES_LARVITAR", 9), ("SPECIES_ARON", 9), ("SPECIES_BALTOY", 8),
        ("SPECIES_SPOINK", 8), ("SPECIES_RALTS", 8), ("SPECIES_VOLTORB", 9)]),
    "TRAINER_PLASTIC_OX_ROUTE_ILEX": ("ilex", [
        ("SPECIES_PARAS", 8), ("SPECIES_VENONAT", 8), ("SPECIES_NINCADA", 8),
        ("SPECIES_ODDISH", 7), ("SPECIES_EXEGGCUTE", 8), ("SPECIES_PINECO", 7)]),
    "TRAINER_PLASTIC_OX_ROUTE46": ("route46", [
        ("SPECIES_MACHOP", 6), ("SPECIES_GEODUDE", 6), ("SPECIES_SANDSHREW", 6),
        ("SPECIES_BAGON", 6), ("SPECIES_NUMEL", 5), ("SPECIES_PHANPY", 6)]),
    "TRAINER_PLASTIC_OX_ROUTE46_ERIN": ("route46", [
        ("SPECIES_ONIX", 7), ("SPECIES_GEODUDE", 6), ("SPECIES_LARVITAR", 7),
        ("SPECIES_MACHOP", 6), ("SPECIES_SANDSHREW", 6), ("SPECIES_BAGON", 6)]),
    "TRAINER_PLASTIC_OX_ROUTE104": ("route2north", [
        ("SPECIES_ONIX", 10), ("SPECIES_GEODUDE", 9), ("SPECIES_LARVITAR", 10),
        ("SPECIES_ARON", 9), ("SPECIES_SNORUNT", 9), ("SPECIES_ZUBAT", 9)]),
    "TRAINER_PLASTIC_OX_ROUTE24": ("route24", [
        ("SPECIES_CLEFFA", 10), ("SPECIES_SNUBBULL", 10), ("SPECIES_SPOINK", 11),
        ("SPECIES_IGGLYBUFF", 10), ("SPECIES_PICHU", 11), ("SPECIES_ELEKID", 10)]),
    "TRAINER_PLASTIC_OX_ROUTE24_ROCKET": ("route24", [
        ("SPECIES_CUBONE", 12), ("SPECIES_KOFFING", 12), ("SPECIES_VOLTORB", 12),
        ("SPECIES_GASTLY", 11), ("SPECIES_EKANS", 12), ("SPECIES_DROWZEE", 11)]),
    "TRAINER_PLASTIC_OX_ROUTE25": ("route25", [
        ("SPECIES_MAGBY", 12), ("SPECIES_SWABLU", 12), ("SPECIES_DROWZEE", 11),
        ("SPECIES_GROWLITHE", 12), ("SPECIES_TYROGUE", 12), ("SPECIES_MEOWTH", 11)]),
    "TRAINER_PLASTIC_OX_ROUTE25_DUDLEY": ("route25", [
        ("SPECIES_SWABLU", 11), ("SPECIES_MAGBY", 12), ("SPECIES_PONYTA", 11),
        ("SPECIES_HOUNDOUR", 12), ("SPECIES_SMOOCHUM", 11), ("SPECIES_MEOWTH", 11)]),
    "TRAINER_PLASTIC_OX_ROUTE25_ELLEN": ("route25", [
        ("SPECIES_DRATINI", 12), ("SPECIES_HORSEA", 12), ("SPECIES_SPHEAL", 11),
        ("SPECIES_SEEL", 12), ("SPECIES_TYROGUE", 11), ("SPECIES_MAREEP", 12)]),
    "TRAINER_PLASTIC_OX_ROUTE25_JOE": ("route25", [
        ("SPECIES_DODUO", 11), ("SPECIES_GROWLITHE", 12), ("SPECIES_VULPIX", 11),
        ("SPECIES_DROWZEE", 12), ("SPECIES_IGGLYBUFF", 11), ("SPECIES_EXEGGCUTE", 12)]),
    "TRAINER_PLASTIC_OX_ROUTE25_LAURA": ("route25", [
        ("SPECIES_CLEFFA", 11), ("SPECIES_SNUBBULL", 12), ("SPECIES_TOGEPI", 12),
        ("SPECIES_AZURILL", 11), ("SPECIES_PICHU", 12), ("SPECIES_SNORUNT", 11)]),
    "TRAINER_PLASTIC_OX_ROUTE25_LLOYD": ("route25", [
        ("SPECIES_MACHOP", 11), ("SPECIES_GEODUDE", 11), ("SPECIES_BAGON", 12),
        ("SPECIES_NUMEL", 11), ("SPECIES_SANDSHREW", 12), ("SPECIES_ONIX", 12)]),
    "TRAINER_PLASTIC_OX_ROUTE25_PAT": ("route25", [
        ("SPECIES_DRATINI", 12), ("SPECIES_HORSEA", 12), ("SPECIES_SPHEAL", 12),
        ("SPECIES_PSYDUCK", 11), ("SPECIES_SWABLU", 11), ("SPECIES_MAGBY", 12)]),

    # ---- PU segment: Route 44, cap 20 ------------------------------------
    "TRAINER_PLASTIC_OX_ROUTE44": ("route44", [
        ("SPECIES_CORPHISH", 13), ("SPECIES_WOOPER", 13), ("SPECIES_BARBOACH", 13),
        ("SPECIES_REMORAID", 13), ("SPECIES_CLAMPERL", 13), ("SPECIES_POLIWAG", 12)]),
    "TRAINER_PLASTIC_OX_ROUTE44_ALLEN": ("route44", [
        ("SPECIES_KINGLER", 13), ("SPECIES_SEAKING", 13), ("SPECIES_DRAGONAIR", 13),
        ("SPECIES_STARYU", 13), ("SPECIES_TENTACOOL", 12), ("SPECIES_CLEFFA", 12)]),
    "TRAINER_PLASTIC_OX_ROUTE44_CYBIL": ("route44", [
        ("SPECIES_REMORAID", 13), ("SPECIES_CORPHISH", 13), ("SPECIES_MACHOP", 13),
        ("SPECIES_VOLTORB", 13), ("SPECIES_ELEKID", 12), ("SPECIES_ARON", 12)]),
    "TRAINER_PLASTIC_OX_ROUTE44_EDGAR": ("route44", [
        ("SPECIES_BARBOACH", 12), ("SPECIES_WOOPER", 12), ("SPECIES_CUBONE", 13),
        ("SPECIES_RHYHORN", 13), ("SPECIES_MAGNEMITE", 12), ("SPECIES_PINECO", 12)]),
    "TRAINER_PLASTIC_OX_ROUTE44_VANCE": ("route44", [
        ("SPECIES_STARYU", 13), ("SPECIES_HORSEA", 12), ("SPECIES_SEALEO", 12),
        ("SPECIES_CLAMPERL", 13), ("SPECIES_CORPHISH", 12), ("SPECIES_PICHU", 12)]),
    "TRAINER_PLASTIC_OX_ROUTE44_WILTON": ("route44", [
        ("SPECIES_MAGBY", 13), ("SPECIES_NUMEL", 12), ("SPECIES_CUBONE", 12),
        ("SPECIES_TRAPINCH", 13), ("SPECIES_ARON", 12), ("SPECIES_MAREEP", 13)]),
    "TRAINER_PLASTIC_OX_ROUTE44_ZACH": ("route44", [
        ("SPECIES_ONIX", 13), ("SPECIES_MACHOP", 12), ("SPECIES_GEODUDE", 12),
        ("SPECIES_SNORUNT", 13), ("SPECIES_LARVITAR", 12), ("SPECIES_MAGNEMITE", 13)]),

    # ---- Mt. Moon, cap 20 -----------------------------------------------
    "TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT": ("mtmoon", [
        ("SPECIES_CUBONE", 14), ("SPECIES_VOLTORB", 14), ("SPECIES_KOFFING", 13),
        ("SPECIES_MACHOP", 14), ("SPECIES_DUSKULL", 14), ("SPECIES_EKANS", 13)]),
    "TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT_2": ("mtmoon", [
        ("SPECIES_MAGNEMITE", 13), ("SPECIES_VOLTORB", 13), ("SPECIES_CUBONE", 13),
        ("SPECIES_KOFFING", 13), ("SPECIES_DROWZEE", 12), ("SPECIES_GASTLY", 13)]),
    "TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT_3": ("mtmoondeep", [
        ("SPECIES_CUBONE", 15), ("SPECIES_MACHOP", 15), ("SPECIES_RHYHORN", 15),
        ("SPECIES_ARON", 14), ("SPECIES_DUSKULL", 15), ("SPECIES_EKANS", 14)]),
    "TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT_4": ("mtmoondeep", [
        ("SPECIES_VOLTORB", 15), ("SPECIES_MAGNEMITE", 15), ("SPECIES_KOFFING", 14),
        ("SPECIES_ONIX", 15), ("SPECIES_DROWZEE", 15), ("SPECIES_DUSKULL", 15)]),
    "TRAINER_PLASTIC_OX_MOONGRUNT1": ("mtmoondeep", [
        ("SPECIES_CUBONE", 16), ("SPECIES_MACHOP", 16), ("SPECIES_ARBOK", 16),
        ("SPECIES_ARON", 15), ("SPECIES_DUSKULL", 16), ("SPECIES_EKANS", 15)]),
    "TRAINER_PLASTIC_OX_MOONGRUNT2": ("mtmoondeep", [
        ("SPECIES_MAGNEMITE", 16), ("SPECIES_VOLTORB", 16), ("SPECIES_ONIX", 16),
        ("SPECIES_RHYHORN", 16), ("SPECIES_GLOOM", 16), ("SPECIES_MAREEP", 16)]),
    "TRAINER_PLASTIC_OX_MOON_YOUNGSTER_JOSH": ("mtmoon", [
        ("SPECIES_MANKEY", 12), ("SPECIES_MEOWTH", 12), ("SPECIES_SNORUNT", 12),
        ("SPECIES_MACHOP", 12), ("SPECIES_EKANS", 12), ("SPECIES_CACNEA", 12)]),
    "TRAINER_PLASTIC_OX_MOON_LASS_IRIS": ("mtmoondeep", [
        ("SPECIES_MEOWTH", 15), ("SPECIES_CLEFFA", 15), ("SPECIES_SENTRET", 15),
        ("SPECIES_TAILLOW", 14), ("SPECIES_SKITTY", 15), ("SPECIES_SNORUNT", 14)]),
    "TRAINER_PLASTIC_OX_MOON_LASS_MIRIAM": ("mtmoon", [
        ("SPECIES_CLEFFA", 13), ("SPECIES_MEOWTH", 13), ("SPECIES_SENTRET", 13),
        ("SPECIES_TAILLOW", 12), ("SPECIES_LOTAD", 12), ("SPECIES_SUNKERN", 12)]),
    # Wurmple, Caterpie and Weedle have two-move level-up learnsets and no TMs
    # in this ROM, so the other Mt. Moon bug species stand in for them.
    "TRAINER_PLASTIC_OX_MOON_BUG_CATCHER_KENT": ("mtmoon", [
        ("SPECIES_PARAS", 12), ("SPECIES_VENONAT", 12), ("SPECIES_NINCADA", 12),
        ("SPECIES_ODDISH", 12), ("SPECIES_SPINARAK", 12), ("SPECIES_EXEGGCUTE", 12)]),
    "TRAINER_PLASTIC_OX_MOON_BUG_CATCHER_ROBBY": ("mtmoondeep", [
        ("SPECIES_NINCADA", 14), ("SPECIES_PARAS", 14), ("SPECIES_VENONAT", 14),
        ("SPECIES_ODDISH", 14), ("SPECIES_PINECO", 13), ("SPECIES_EXEGGCUTE", 14)]),
    "TRAINER_PLASTIC_OX_MOON_HIKER_MARCOS": ("mtmoon", [
        ("SPECIES_MACHOP", 13), ("SPECIES_GEODUDE", 13), ("SPECIES_ONIX", 13),
        ("SPECIES_ARON", 13), ("SPECIES_SANDSHREW", 12), ("SPECIES_NUMEL", 12)]),
    "TRAINER_PLASTIC_OX_MOON_SUPER_NERD_JOVAN": ("mtmoon", [
        ("SPECIES_MAGNEMITE", 12), ("SPECIES_SPOINK", 12), ("SPECIES_BALTOY", 12),
        ("SPECIES_NATU", 12), ("SPECIES_EXEGGCUTE", 12), ("SPECIES_ELEKID", 11)]),
    "TRAINER_PLASTIC_OX_MOON_SUPER_NERD_MIGUEL": ("mtmoondeep", [
        ("SPECIES_MAGNEMITE", 15), ("SPECIES_SPOINK", 15), ("SPECIES_BALTOY", 15),
        ("SPECIES_NATU", 15), ("SPECIES_EXEGGCUTE", 15), ("SPECIES_ELEKID", 15)]),

    # ---- Route 33 and Gym 2, Goldenrod, PU cap 20 ------------------------
    "TRAINER_PLASTIC_OX_PU_ROUTE33": ("route33", [
        ("SPECIES_SPINDA", 17), ("SPECIES_SEVIPER", 16), ("SPECIES_ZIGZAGOON", 17),
        ("SPECIES_HOPPIP", 16), ("SPECIES_AIPOM", 16), ("SPECIES_GEODUDE", 16)]),
    "TRAINER_PLASTIC_OX_WHITNEY": ("gym2", [
        ("SPECIES_MIGHTYENA", 20), ("SPECIES_WIGGLYTUFF", 19), ("SPECIES_MEOWTH", 19),
        ("SPECIES_FURRET", 19), ("SPECIES_ARBOK", 19), ("SPECIES_DRAGONAIR", 20)]),

    # ---- Gym 3 segment, NU cap 30 ----------------------------------------
    "TRAINER_PLASTIC_OX_PU_ROUTE35": ("route35", [
        # Ditto knows only Transform in this ROM, so Corsola (the Route 35
        # Old Rod pool) takes the sixth slot.
        ("SPECIES_ABRA", 19), ("SPECIES_FARFETCHD", 19), ("SPECIES_YANMA", 19),
        ("SPECIES_MINUN", 19), ("SPECIES_DROWZEE", 19), ("SPECIES_CORSOLA", 19)]),
    "TRAINER_PLASTIC_OX_PU_PARK": ("park", [
        ("SPECIES_LICKITUNG", 20), ("SPECIES_JIGGLYPUFF", 20), ("SPECIES_TROPIUS", 20),
        ("SPECIES_HOPPIP", 20), ("SPECIES_NIDORAN_F", 20), ("SPECIES_LEDYBA", 19)]),
    "TRAINER_PLASTIC_OX_PU_ROUTE36": ("route36", [
        ("SPECIES_TANGELA", 21), ("SPECIES_VULPIX", 21), ("SPECIES_DROWZEE", 21),
        ("SPECIES_BELLSPROUT", 21), ("SPECIES_NATU", 21), ("SPECIES_BALTOY", 21)]),
    "TRAINER_PLASTIC_OX_KIMONOFLAREON": ("gym3", [
        ("SPECIES_FLAREON", 26), ("SPECIES_VULPIX", 22), ("SPECIES_GROWLITHE", 23),
        ("SPECIES_ARBOK", 24), ("SPECIES_MEOWTH", 23), ("SPECIES_DELIBIRD", 24)]),
    "TRAINER_PLASTIC_OX_KIMONOVAPOREON": ("gym3", [
        ("SPECIES_VAPOREON", 26), ("SPECIES_PSYDUCK", 23), ("SPECIES_SEEL", 23),
        ("SPECIES_STARYU", 24), ("SPECIES_SLOWPOKE", 24), ("SPECIES_TENTACOOL", 24)]),
    "TRAINER_PLASTIC_OX_KIMONOJOLTEON": ("gym3", [
        ("SPECIES_JOLTEON", 26), ("SPECIES_ELEKID", 23), ("SPECIES_ELECTRIKE", 23),
        ("SPECIES_VOLTORB", 24), ("SPECIES_MAGNEMITE", 23), ("SPECIES_SKITTY", 24)]),
    "TRAINER_PLASTIC_OX_KIMONOESPEON": ("gym3", [
        ("SPECIES_ESPEON", 26), ("SPECIES_MEDITITE", 23), ("SPECIES_MEOWTH", 23),
        ("SPECIES_KIRLIA", 24), ("SPECIES_SLOWPOKE", 24), ("SPECIES_NATU", 23)]),
    "TRAINER_PLASTIC_OX_KIMONOUMBREON": ("gym3", [
        ("SPECIES_UMBREON", 26), ("SPECIES_SPOINK", 23), ("SPECIES_HOUNDOUR", 24),
        ("SPECIES_DUSKULL", 24), ("SPECIES_MEOWTH", 23), ("SPECIES_NIDORAN_M", 24)]),
    "TRAINER_PLASTIC_OX_MORTY": ("gym3", [
        ("SPECIES_SUDOWOODO", 30), ("SPECIES_HAUNTER", 29), ("SPECIES_GASTLY", 28),
        ("SPECIES_DUSKULL", 28), ("SPECIES_GOLBAT", 28), ("SPECIES_WIGGLYTUFF", 27)]),

    # ---- Gym 4 and Gym 5 segments, RU cap 36 / UU cap 42 -----------------
    "TRAINER_PLASTIC_OX_WINONA": ("fortree", [
        ("SPECIES_PIDGEOT", 36), ("SPECIES_PELIPPER", 35), ("SPECIES_GOLBAT", 35),
        ("SPECIES_VIGOROTH", 34), ("SPECIES_FARFETCHD", 34), ("SPECIES_DODUO", 33)]),
    "TRAINER_PLASTIC_OX_WEATHER": ("fortree", [
        ("SPECIES_CASTFORM", 34), ("SPECIES_XATU", 34), ("SPECIES_MAWILE", 33),
        ("SPECIES_MEDITITE", 33), ("SPECIES_MAGNEMITE", 32), ("SPECIES_ELEKID", 32)]),
    "TRAINER_PLASTIC_OX_TOWERGRUNT1": ("cinnabar", [
        ("SPECIES_GASTLY", 38), ("SPECIES_DROWZEE", 37), ("SPECIES_CUBONE", 37),
        ("SPECIES_MUK", 37), ("SPECIES_KOFFING", 36), ("SPECIES_HAUNTER", 38)]),
    "TRAINER_PLASTIC_OX_TOWERGRUNT2": ("cinnabar", [
        ("SPECIES_MACHOP", 38), ("SPECIES_CUBONE", 38), ("SPECIES_ONIX", 38),
        ("SPECIES_MUK", 37), ("SPECIES_RHYHORN", 37), ("SPECIES_HAUNTER", 38)]),
    "TRAINER_PLASTIC_OX_BLAINE": ("cinnabar", [
        ("SPECIES_NINETALES", 42), ("SPECIES_ARCANINE", 42), ("SPECIES_RAPIDASH", 41),
        ("SPECIES_ELECTRODE", 40), ("SPECIES_MUK", 41), ("SPECIES_TENTACRUEL", 40)]),

    # ---- Gym 6, Mossdeep, UUBL cap 50 ------------------------------------
    "TRAINER_PLASTIC_OX_TATELIZA": ("mossdeep", [
        ("SPECIES_ALAKAZAM", 46), ("SPECIES_SLOWBRO", 46), ("SPECIES_MACHAMP", 45),
        ("SPECIES_URSARING", 45), ("SPECIES_STEELIX", 44), ("SPECIES_HOUNDOOM", 44)]),
    "TRAINER_PLASTIC_OX_BRUNO": ("mossdeep", [
        ("SPECIES_RHYDON", 50), ("SPECIES_GOLEM", 50), ("SPECIES_MACHAMP", 49),
        ("SPECIES_HARIYAMA", 49), ("SPECIES_DONPHAN", 48), ("SPECIES_STEELIX", 48)]),

    # ---- Gym 7, Saffron, OU cap 55 ---------------------------------------
    "TRAINER_PLASTIC_OX_SILPHGRUNT1": ("saffron", [
        ("SPECIES_MACHAMP", 52), ("SPECIES_JYNX", 52), ("SPECIES_WEEZING", 51),
        ("SPECIES_HARIYAMA", 51), ("SPECIES_DUSCLOPS", 50), ("SPECIES_KADABRA", 52)]),
    "TRAINER_PLASTIC_OX_SILPHGRUNT2": ("saffron", [
        ("SPECIES_STEELIX", 52), ("SPECIES_EXEGGUTOR", 52), ("SPECIES_SLOWBRO", 51),
        ("SPECIES_MAGNETON", 52), ("SPECIES_DODRIO", 50), ("SPECIES_CLOYSTER", 52)]),
    "TRAINER_PLASTIC_OX_SILPHGRUNT3": ("saffron", [
        ("SPECIES_DRAGONITE", 53), ("SPECIES_KINGDRA", 52), ("SPECIES_ARMALDO", 51),
        ("SPECIES_URSARING", 51), ("SPECIES_LINOONE", 50), ("SPECIES_MAROWAK", 51)]),
    "TRAINER_PLASTIC_OX_GIOVANNI": ("saffron", [
        ("SPECIES_TYRANITAR", 55), ("SPECIES_SALAMENCE", 55), ("SPECIES_METAGROSS", 55),
        ("SPECIES_FORRETRESS", 54), ("SPECIES_GENGAR", 53), ("SPECIES_STARMIE", 54)]),

    # ---- Gym 8, Blackthorn, OU cap 60 ------------------------------------
    "TRAINER_PLASTIC_OX_CLAIR": ("blackthorn", [
        ("SPECIES_GYARADOS", 59), ("SPECIES_JOLTEON", 58), ("SPECIES_SWAMPERT", 58),
        ("SPECIES_TYRANITAR", 59), ("SPECIES_MEDICHAM", 58), ("SPECIES_FLYGON", 58)]),
    "TRAINER_PLASTIC_OX_VICTORYROAD": ("victoryroad", [
        ("SPECIES_FLYGON", 58), ("SPECIES_CLOYSTER", 58), ("SPECIES_STARMIE", 58),
        ("SPECIES_SWAMPERT", 58), ("SPECIES_FORRETRESS", 58), ("SPECIES_GENGAR", 58)]),

    # ---- League and post-game, OU cap 62-64 ------------------------------
    "TRAINER_PLASTIC_OX_WALLACE": ("league", [
        ("SPECIES_SALAMENCE", 62), ("SPECIES_SWAMPERT", 62), ("SPECIES_TYRANITAR", 62),
        ("SPECIES_METAGROSS", 61), ("SPECIES_FORRETRESS", 61), ("SPECIES_GENGAR", 61)]),
    "TRAINER_PLASTIC_OX_STEVEN": ("league", [
        ("SPECIES_METAGROSS", 62), ("SPECIES_SALAMENCE", 62), ("SPECIES_FLYGON", 62),
        ("SPECIES_AGGRON", 62), ("SPECIES_ARMALDO", 61), ("SPECIES_CLAYDOL", 61)]),
    "TRAINER_PLASTIC_OX_LEAGUELANCE": ("league", [
        ("SPECIES_GYARADOS", 62), ("SPECIES_STARMIE", 62), ("SPECIES_CHARIZARD", 62),
        ("SPECIES_CLAYDOL", 61), ("SPECIES_MEDICHAM", 61), ("SPECIES_SWAMPERT", 62)]),
    "TRAINER_PLASTIC_OX_BLUE": ("postgame", [
        ("SPECIES_TYRANITAR", 64), ("SPECIES_SALAMENCE", 64), ("SPECIES_METAGROSS", 64),
        ("SPECIES_GENGAR", 63), ("SPECIES_GYARADOS", 64), ("SPECIES_FORRETRESS", 63)]),
    "TRAINER_PLASTIC_OX_BILL": ("postgame", [
        ("SPECIES_METAGROSS", 64), ("SPECIES_STARMIE", 64), ("SPECIES_CLOYSTER", 63),
        ("SPECIES_FLYGON", 63), ("SPECIES_SWAMPERT", 63), ("SPECIES_CHARIZARD", 64)]),
}

# Left alone on purpose, with the reason recorded in the report.
KEEP_AS_IS = {
    # The task's designated format reference. Already six LC-legal Pokemon at
    # exactly the Gym 1 cap, all obtainable before Gym 1.
    "TRAINER_PLASTIC_OX_ROXANNE": "designated format reference; already a legal six",
    # Metamon showcase battle wired into sMetamonTrainers[]; its id must stay
    # stable and its Elite-Four roster is the point of the fight.
    "TRAINER_PLASTIC_OX_LANCE": "metamon showcase trainer in Oldale Town",
    # Not an opponent: GivePlasticOxPlayerParty() builds the player's own
    # starting party from this template (src/new_game.c).
    "TRAINER_PLASTIC_OX_PLAYER": "player party template, not a battled trainer",
}

# The Dance Theater girls are named for, and gated on, their Eeveelution, but
# Vaporeon/Jolteon/Espeon/Umbreon are UUBL/OU and the fights unlock at two
# badges (NU). The signature is kept as designed and reported as an exception;
# the other five slots obey the rules strictly.
SIGNATURE_EXCEPTIONS = {
    "TRAINER_PLASTIC_OX_KIMONOVAPOREON": ["SPECIES_VAPOREON"],
    "TRAINER_PLASTIC_OX_KIMONOJOLTEON": ["SPECIES_JOLTEON"],
    "TRAINER_PLASTIC_OX_KIMONOESPEON": ["SPECIES_ESPEON"],
    "TRAINER_PLASTIC_OX_KIMONOUMBREON": ["SPECIES_UMBREON"],
}

# ---------------------------------------------------------------------------
# Set construction
# ---------------------------------------------------------------------------
MOVE_META = P.load_move_meta()
TYPES = P.load_species_types()
ABILITIES = P.load_abilities()
for _alias, _target in P.load_species_aliases().items():
    ABILITIES.setdefault(_alias, ABILITIES.get(_target, []))

# Status / utility moves worth a slot, best first. Used both to derive sets for
# species with no tier-dex entry and to substitute for a move that is not yet
# legal at the trainer's level.
UTILITY_PRIORITY = [
    "MOVE_SPIKES", "MOVE_TOXIC", "MOVE_THUNDER_WAVE", "MOVE_WILL_O_WISP",
    "MOVE_HYPNOSIS", "MOVE_SLEEP_POWDER", "MOVE_STUN_SPORE", "MOVE_CONFUSE_RAY",
    "MOVE_ENCORE", "MOVE_YAWN", "MOVE_ROAR", "MOVE_GROWL", "MOVE_LEER",
    "MOVE_TAIL_WHIP", "MOVE_SWORDS_DANCE", "MOVE_CALM_MIND", "MOVE_AGILITY",
    "MOVE_LEECH_SEED", "MOVE_REFLECT", "MOVE_LIGHT_SCREEN", "MOVE_SAFEGUARD",
    "MOVE_SUBSTITUTE", "MOVE_PROTECT", "MOVE_DOUBLE_TEAM", "MOVE_SAND_ATTACK",
    "MOVE_SWAGGER", "MOVE_SNATCH", "MOVE_BATON_PASS", "MOVE_RECOVER",
    "MOVE_SOFT_BOILED", "MOVE_REST", "MOVE_SLACK_OFF", "MOVE_SCREECH",
    "MOVE_CURSE", "MOVE_PURSUIT", "MOVE_KNOCK_OFF",
]

# Same-role replacements, tried in order when a set move is not legal yet.
ROLE_FALLBACK = {
    "MOVE_HIDDEN_POWER": ["MOVE_RETURN", "MOVE_SWIFT"],
    "MOVE_SUBSTITUTE": ["MOVE_PROTECT", "MOVE_ENDURE"],
    "MOVE_EXPLOSION": ["MOVE_SELF_DESTRUCT", "MOVE_DOUBLE_EDGE"],
    "MOVE_EARTHQUAKE": ["MOVE_ROCK_SLIDE", "MOVE_MAGNITUDE"],
    "MOVE_ROCK_SLIDE": ["MOVE_EARTHQUAKE", "MOVE_ROCK_TOMB"],
    "MOVE_BLAZE_KICK": ["MOVE_HI_JUMP_KICK", "MOVE_CLOSE_COMBAT"],
    "MOVE_HI_JUMP_KICK": ["MOVE_BLAZE_KICK", "MOVE_CLOSE_COMBAT"],
    "MOVE_GIGA_DRAIN": ["MOVE_LEECH_LIFE", "MOVE_ABSORB", "MOVE_MEGA_DRAIN"],
    "MOVE_LEECH_LIFE": ["MOVE_GIGA_DRAIN", "MOVE_ABSORB"],
    "MOVE_MEGA_DRAIN": ["MOVE_GIGA_DRAIN", "MOVE_ABSORB"],
    "MOVE_HYDRO_PUMP": ["MOVE_SURF", "MOVE_WATER_PULSE"],
    "MOVE_SURF": ["MOVE_HYDRO_PUMP", "MOVE_WATER_PULSE"],
    "MOVE_WATER_PULSE": ["MOVE_SURF", "MOVE_HYDRO_PUMP"],
    "MOVE_DRAGON_CLAW": ["MOVE_OUTRAGE", "MOVE_DRAGON_PULSE"],
    "MOVE_OUTRAGE": ["MOVE_DRAGON_CLAW", "MOVE_DRAGON_PULSE"],
    "MOVE_PSYCHIC": ["MOVE_PSYBEAM", "MOVE_CONFUSION"],
    "MOVE_PSYBEAM": ["MOVE_PSYCHIC", "MOVE_CONFUSION"],
    "MOVE_FLAMETHROWER": ["MOVE_FIRE_PUNCH", "MOVE_FIRE_SPIN"],
    "MOVE_FIRE_BLAST": ["MOVE_FLAMETHROWER", "MOVE_FIRE_PUNCH"],
    "MOVE_FIRE_PUNCH": ["MOVE_FLAMETHROWER", "MOVE_WILL_O_WISP"],
    "MOVE_SLUDGE_BOMB": ["MOVE_SLUDGE", "MOVE_POISON_JAB"],
    "MOVE_SLUDGE": ["MOVE_SLUDGE_BOMB", "MOVE_POISON_JAB"],
    "MOVE_ROCK_TOMB": ["MOVE_ROCK_SLIDE", "MOVE_EARTHQUAKE"],
    "MOVE_SHADOW_BALL": ["MOVE_PUNISH", "MOVE_BITTER_MALICE"],
    "MOVE_CRUNCH": ["MOVE_BITE", "MOVE_PURSUIT"],
    "MOVE_IRON_TAIL": ["MOVE_IRON_HEAD", "MOVE_ROCK_SMASH"],
    "MOVE_DOUBLE_EDGE": ["MOVE_RETURN", "MOVE_TAKE_DOWN"],
    "MOVE_AERIAL_ACE": ["MOVE_WING_ATTACK", "MOVE_PURSUIT"],
    "MOVE_BOOMBURST": ["MOVE_HYPER_VOICE", "MOVE_TAKE_DOWN"],
    "MOVE_HYPER_VOICE": ["MOVE_BOOMBURST", "MOVE_TAKE_DOWN"],
}


# Gen 3 attacking-move preference, best first. Used to order the derived sets
# so a Water type reaches for Surf rather than the 130-power Blizzard TM, and a
# Grass type for Giga Drain rather than Solar Beam.
MOVE_RANK = [
    "MOVE_SPITE", "MOVE_HIDDEN_POWER", "MOVE_TOXIC", "MOVE_SUBSTITUTE",
    "MOVE_SURF", "MOVE_GIGA_DRAIN", "MOVE_EARTHQUAKE", "MOVE_ROCK_SLIDE",
    "MOVE_THUNDERBOLT", "MOVE_FLAMETHROWER", "MOVE_ICE_BEAM", "MOVE_PSYCHIC",
    "MOVE_SHADOW_BALL", "MOVE_SLUDGE_BOMB", "MOVE_DRAGON_CLAW", "MOVE_CRUNCH",
    "MOVE_ROCK_TOMB", "MOVE_EARTHQUAKE", "MOVE_BLAZE_KICK", "MOVE_HI_JUMP_KICK",
    "MOVE_CLOSE_COMBAT", "MOVE_LEECH_LIFE", "MOVE_BUG_BITE", "MOVE_AERIAL_ACE",
    "MOVE_WING_ATTACK", "MOVE_PECK", "MOVE_IRON_TAIL", "MOVE_IRON_HEAD",
    "MOVE_ROCK_SMASH", "MOVE_FIRE_PUNCH", "MOVE_ICE_PUNCH", "MOVE_THUNDER_PUNCH",
    "MOVE_MUD_SHOT", "MOVE_MUD_SLAP", "MOVE_WATER_PULSE", "MOVE_HYDRO_PUMP",
    "MOVE_CROSS_CHOP", "MOVE_ROCK_SMASH", "MOVE_BODY_SLAM", "MOVE_DOUBLE_EDGE",
    "MOVE_RETURN", "MOVE_SWIFT", "MOVE_HYPER_VOICE", "MOVE_TAKEDOWN",
    "MOVE_FACADE", "MOVE_REVERSAL", "MOVE_PURSUIT", "MOVE_PURSUIT",
    "MOVE_SCRATCH", "MOVE_TACKLE", "MOVE_POUND", "MOVE_QUICK_ATTACK",
    "MOVE_SOLAR_BEAM", "MOVE_BLIZZARD", "MOVE_FIRE_BLAST", "MOVE_HYPER_BEAM",
    "MOVE_HEADBUTT", "MOVE_SWAGGER", "MOVE_THIEF", "MOVE_KNOCK_OFF",
    "MOVE_SNATCH", "MOVE_FLAMETHROWER", "MOVE_SURF", "MOVE_DIG", "MOVE_BOOMBURST",
]
MOVE_RANK_INDEX = {m: i for i, m in enumerate(dict.fromkeys(MOVE_RANK))}
DEFAULT_RANK = len(MOVE_RANK_INDEX) + 40


def _rank(move: str, power: int) -> tuple:
    return (MOVE_RANK_INDEX.get(move, DEFAULT_RANK - min(power, 40)), -power)

DEFAULT_ITEM_BY_KIND = {
    "physical": "Choice Band", "sweep": "Leftovers", "special": "Leftovers",
    "wall": "Leftovers", "status": "Lum Berry",
}


NATURES = {
    ("atk", "spa"): "Adamant", ("atk", "spd"): "Jolly", ("atk", "spe"): "Adamant",
    ("spa", "atk"): "Modest", ("spa", "spd"): "Modest", ("spa", "spe"): "Timid",
    ("spe", "atk"): "Jolly", ("spe", "spa"): "Naive", ("spe", "spd"): "Naive",
    ("def", "atk"): "Bold", ("def", "spa"): "Bold", ("def", "spe"): "Relaxed",
    ("spd", "atk"): "Impish", ("spd", "spa"): "Calm", ("spd", "spe"): "Careful",
}


def _nature_for(evs: dict) -> str:
    """The nature that matches the spread: the biggest offensive stat up, its
    partner down."""
    if not evs:
        return "Hardy"
    if evs.get("atk", 0) >= 252:
        return "Adamant"
    if evs.get("spa", 0) >= 252:
        return "Timid" if evs.get("spe", 0) >= 200 else "Modest"
    if evs.get("spe", 0) >= 252:
        return "Jolly" if evs.get("atk", 0) >= 80 else "Naive"
    if evs.get("hp", 0) >= 252:
        return "Bold" if evs.get("def", 0) else "Relaxed"
    if evs.get("spd", 0) >= 252:
        return "Careful" if evs.get("spe", 0) else "Impish"
    return "Adamant"


def _evs_for(moves: list[str], species: str) -> dict:
    """Spread EVs from the shape of the set: physical, special, mixed or wall."""
    types = set(TYPES.get(species, []))
    phys = spec = 0
    for m in moves:
        info = MOVE_META.get(m, {})
        if info.get("power", 0) <= 0 or info.get("type") not in types:
            continue
        if info.get("category") == "PHYSICAL":
            phys += 1
        else:
            spec += 1
    defensive = any(MOVE_META.get(m, {}).get("power", 0) == 0 and
                    MOVE_META.get(m, {}).get("effect") in
                    ("SUBSTITUTE", "BIDE", "RECHARGE", "SPECIAL_DEFENSE_UP", "TAUNT")
                    for m in moves)
    if phys and not spec and not defensive:
        return {"hp": 4, "atk": 252, "spe": 252}
    if spec and not phys:
        return {"hp": 4, "spa": 252, "spe": 252}
    if phys and spec:
        return {"hp": 124, "atk": 84, "spa": 84, "spe": 216}
    return {"hp": 252, "def": 252}


def _category(species: str, moves: list[str]) -> str:
    return "physical" if _evs_for(moves, species).get("atk", 0) > 128 else "special"


def derive_set(species: str, level: int) -> dict:
    """Build a legal four-move set from the species' learnset at `level`.

    Used where plastic_ox/gen3_movesets.json has no entry for the species in
    any tier the checkpoint can reach; the shape matches the dex sets the rest
    of the rosters use (STAB, coverage, one utility slot, a second attacker).
    """
    legal = sorted(P.legal_moves(species, level, gen3_only=True))
    meta = MOVE_META
    types = set(TYPES.get(species, []))
    damaging = [m for m in legal if meta.get(m, {}).get("power", 0) > 0]
    stab = sorted((m for m in damaging if meta[m]["type"] in types),
                  key=lambda m: _rank(m, meta[m]["power"]))
    other = sorted((m for m in damaging if meta[m]["type"] not in types),
                   key=lambda m: _rank(m, meta[m]["power"]))
    utility = [m for m in UTILITY_PRIORITY if m in legal]
    moves: list[str] = []
    for m in stab[:2] + other[:2]:
        if m not in moves:
            moves.append(m)
        if len(moves) == 3:
            break
    if utility:
        moves.append(utility[0])
    for m in stab + other:
        if len(moves) == 4:
            break
        if m not in moves:
            moves.append(m)
    moves = moves[:4]
    while len(moves) < 4:                      # tiny learnsets: pad with Tackle
        for m in ("MOVE_TACKLE", "MOVE_POUND"):
            if m in legal and m not in moves:
                moves.append(m)
                break
        else:
            break
    evs = _evs_for(moves, species)
    return {"moves": moves, "ability": (ABILITIES.get(species) or [""])[0],
            "item": DEFAULT_ITEM_BY_KIND[_category(species, moves)],
            "nature": _nature_for(evs), "evs": evs}


def legalise_moves(species: str, level: int, moves: list[str],
                   gen3_only: bool = False) -> tuple[list[str], list[str]]:
    """Keep the legal moves; substitute the closest legal same-role move for
    each one the species cannot legally know at `level`."""
    out: list[str] = []
    notes: list[str] = []
    for move in moves:
        ok, why = P.move_legal(species, move, level, gen3_only)
        if ok:
            out.append(move)
            continue
        replacement = None
        for cand in ROLE_FALLBACK.get(move, []):
            if P.move_legal(species, cand, level, gen3_only)[0]:
                replacement = cand
                break
        if replacement is None:
            for cand in sorted(P.legal_moves(species, level, gen3_only) - set(out),
                               key=lambda m: -MOVE_META.get(m, {}).get("power", 0)):
                if MOVE_META.get(cand, {}).get("power", 0) > 0:
                    replacement = cand
                    break
        if replacement is None:
            for cand in UTILITY_PRIORITY:
                if P.move_legal(species, cand, level, gen3_only)[0] and cand not in out:
                    replacement = cand
                    break
        if replacement is None:
            notes.append(f"dropped {move.removeprefix('MOVE_').title().replace('_', ' ')} ({why})")
            continue
        out.append(replacement)
        notes.append(f"{move.removeprefix('MOVE_').title().replace('_', ' ')} -> "
                     f"{replacement.removeprefix('MOVE_').title().replace('_', ' ')} ({why})")
    seen, uniq = set(), []
    for m in out:
        if m not in seen:
            seen.add(m)
            uniq.append(m)
    return uniq[:4], notes


def build_mon(species: str, level: int, checkpoint: str, salt: int) -> dict:
    """One party slot: a set plus its provenance and any substitutions."""
    dex = P.dex_for_tier(P.tier_at(checkpoint))
    options = P.sets_for(dex, species)
    source = "derived"
    set_name = "learnset-derived"
    scored = []
    for name, value in sorted(options, key=lambda kv: kv[0]):   # deterministic order
        named = P.resolve_set_moves(value["moves"])
        if len(named) != len(value["moves"]):
            continue                                  # a move we cannot resolve
        candidate, notes = legalise_moves(species, level, named)
        scored.append((4 - len(notes), name, value, candidate, notes))
    # Keep every set that is still competitive, then rotate through them with
    # the slot index so two trainers sharing a species do not share its set.
    best = max((row[0] for row in scored), default=0)
    usable = [row for row in scored if row[0] >= max(best - 1, 3)]
    chosen = usable[salt % len(usable)] if usable else None
    if chosen is not None and chosen[0] >= 3:
        score, set_name, value, moves, notes = chosen
        source = "gen3_movesets.json"
    else:
        value = derive_set(species, level)
        moves, notes = legalise_moves(species, level, list(value["moves"]), gen3_only=True)
        set_name = "learnset-derived"
        source = "derived from the ROM learnset (no tier-dex entry)"
    moves, extra = legalise_moves(species, level, moves)
    notes = notes + [n for n in extra if n not in notes]
    if len(moves) < 4:
        # A dex set can lose a slot to a substitution; top the set back up from
        # the same legal Gen 3 pool the derived sets use.
        for cand in sorted(P.legal_moves(species, level, gen3_only=True) - set(moves),
                           key=lambda m: _rank(m, MOVE_META.get(m, {}).get("power", 0))):
            moves.append(cand)
            if len(moves) == 4:
                break
    if value.get("hpType"):
        notes.append(f"Hidden Power type {value['hpType']} dropped: trainerproc has no "
                     "HP-type field in the .party format")
    if len(moves) < 4:
        notes.append(f"only {len(moves)} legal move(s) in this ROM's learnset; "
                     "trainerproc fills the rest from the level-up learnset")

    abilities = ABILITIES.get(species) or []
    lookup = {a.replace("_", " ").lower(): a for a in abilities}
    wanted = (value.get("ability") or "").replace("_", " ").lower()
    ability = lookup.get(wanted, "")
    if not ability:
        notes.append(f"ability {value.get('ability', '?')} -> {abilities[0] if abilities else '?'} "
                     f"(not a {species} ability)")
        ability = abilities[0] if abilities else ""
    ability = ability.replace("_", " ").title()
    nature = value.get("nature") or "Hardy"
    if nature not in P.load_natures():
        nature = "Hardy"
    evs = {k: v for k, v in (value.get("evs") or _evs_for(moves, species)).items() if v}
    if sum(evs.values()) > 510:
        keep, total = {}, 0
        for k, v in sorted(evs.items(), key=lambda kv: -kv[1]):
            take = min(v, 252, 510 - total)
            if take:
                keep[k] = take
                total += take
        evs = keep
    return {"species": species, "level": level, "moves": moves, "ability": ability,
            "item": value.get("item", "Leftovers"), "nature": nature, "evs": evs,
            "set_name": set_name, "set_source": source, "notes": notes,
            "ivs": value.get("ivs"), "hp_type": value.get("hpType")}


def render_mon(mon: dict) -> str:
    name = mon["species"].removeprefix("SPECIES_").replace("_", "-").title().replace("'", "'")
    name = {"Nidoran-F": "Nidoran♀", "Nidoran-M": "Nidoran♂", "Mr-Mime": "Mr. Mime",
            "Ho-Oh": "Ho-Oh", "Farfetchd": "Farfetch'd"}.get(name, name)
    head = f"{name} @ {mon['item']}" if mon["item"] else name
    lines = [head, f"Level: {mon['level']}"]
    if mon["ability"]:
        lines.append(f"Ability: {mon['ability']}")
    if mon["ivs"]:
        stats = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
        lines.append("IVs: " + " / ".join(
            f"{mon['ivs'].get(k, 31)} {s}" for k, s in
            zip(("hp", "atk", "def", "spa", "spd", "spe"), stats)))
    if mon["evs"]:
        stats = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
        lines.append("EVs: " + " / ".join(
            f"{mon['evs'][k]} {s}" for k, s in
            zip(("hp", "atk", "def", "spa", "spd", "spe"), stats) if k in mon["evs"]))
    lines.append(f"{mon['nature']} Nature")
    # trainerproc has no Hidden Power type field, so a dex set's hpType cannot be
    # expressed in the .party format; the ROM picks the species default.
    lines += [f"- {MOVE_META.get(m, {}).get('name', m.removeprefix('MOVE_').title().replace('_', ' '))}"
              for m in mon["moves"]]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
HEADER_FIELDS = ("Name:", "Class:", "Pic:", "Gender:", "Music:", "Double Battle:",
                 "AI:", "Battle Type:", "Items:", "Mugshot:", "Multi Party:")


def parse_party(text: str) -> dict[str, str]:
    parts = re.split(r"^=== (\w+) ===$", text, flags=re.MULTILINE)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}


def split_block(body: str) -> tuple[list[str], list[str]]:
    header, mons = [], []
    for block in re.split(r"\n\n+", body.strip()):
        if block.splitlines()[0].startswith(HEADER_FIELDS):
            header.append(block)
        else:
            mons.append(block)
    return header, mons


# A stable per-trainer salt so the set rotation differs between two trainers
# that share a species.
TRAINER_SALT = {name: i * 3 for i, name in enumerate(sorted(ROSTERS))}


def main() -> int:
    text = PARTY.read_text()
    parsed = parse_party(text)
    problems: list[str] = []
    built: dict[str, dict] = {}

    for trainer, (checkpoint, roster) in sorted(ROSTERS.items()):
        if trainer not in parsed:
            problems.append(f"{trainer}: not present in trainers.party")
            continue
        legal = P.legal_for(checkpoint)
        how = P.obtainable_at(checkpoint)
        cap = P.cap_at(checkpoint)
        allowed = set(SIGNATURE_EXCEPTIONS.get(trainer, []))
        mons = []
        for index, (species, level) in enumerate(roster):
            if len(roster) != 6:
                problems.append(f"{trainer}: {len(roster)} slots, expected 6")
            if species not in legal and species not in allowed:
                problems.append(f"{trainer}[{index}]: {species} is not obtainable at "
                                f"'{checkpoint}' (tier {P.tier_of(species)})")
            if level > cap:
                problems.append(f"{trainer}[{index}]: level {level} exceeds the "
                                f"{checkpoint} cap of {cap}")
            mon = build_mon(species, level, checkpoint, TRAINER_SALT[trainer] + index)
            mon["why_available"] = how.get(species, "signature exception")
            mon["tier"] = P.tier_of(species)
            mon["flagged"] = species not in legal
            mons.append(mon)
        built[trainer] = {"checkpoint": checkpoint, "cap": cap,
                          "tier": P.tier_at(checkpoint), "monsters": mons}

    for trainer in KEEP_AS_IS:
        if trainer not in parsed:
            problems.append(f"{trainer}: expected in trainers.party but missing")
        built[trainer] = {"checkpoint": None, "kept": KEEP_AS_IS[trainer],
                          "monsters": [m.splitlines()[0]
                                       for m in split_block(parsed[trainer])[1]]}

    if "--check" in sys.argv:
        REPORT.write_text(json.dumps({"trainers": built}, indent=1) + "\n")
        for p in problems:
            print("PROBLEM:", p)
        print(f"{len(problems)} problem(s); {len(built)} trainers described")
        return 1 if problems else 0

    # Surgical replacement: only the trainer blocks that were regenerated are
    # touched, so the other 855 entries stay byte-for-byte identical.
    out = text
    for trainer, data in built.items():
        if data.get("checkpoint") is None:
            continue
        header, _old = split_block(parsed[trainer])
        body = "\n" + "\n\n".join(header + [render_mon(m) for m in data["monsters"]]) + "\n\n"
        pattern = re.compile(rf"(^=== {trainer} ===$)(.*?)(?=^=== |\Z)", re.MULTILINE | re.S)
        out, count = pattern.subn(lambda m: m.group(1) + body, out, count=1)
        assert count == 1, f"could not rewrite {trainer}"
    PARTY.write_text(out)
    REPORT.write_text(json.dumps({"trainers": built}, indent=1) + "\n")
    for p in problems:
        print("PROBLEM:", p)
    print(f"rewrote {len(built) - len(KEEP_AS_IS)} trainer parties in {PARTY}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
