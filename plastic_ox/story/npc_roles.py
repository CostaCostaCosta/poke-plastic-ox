#!/usr/bin/env python3
"""Classify map object events into key NPCs and standard NPCs.

A key NPC changes play: a trainer battle, an item or Pokémon gift, an in-game
trade, a shop or heal service, a path/gate state change, a scene trigger, a
dialogue choice, or a story-gated object. A standard NPC only talks.

The classifier is intentionally evidence-based. It reads the resolved script
commands and cross-references the location note's Key interactions table, so a
silent blocker or a guide named by the design note is not lost just because its
script is a single `msgbox`.

Used by the wiki build (location pages) and the region map.
"""

from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

SKIP_GRAPHICS = (
    "ITEM_BALL",
    "POKE_BALL",
    "BERRY_TREE",
    "APRICORN_TREE",
    "CUTTABLE_TREE",
    "BREAKABLE_ROCK",
    "SIGN",
    "TOWN_MAP",
    "POKEDEX",
)
ROLE_ORDER = (
    "Trainer battle",
    "In-game trade",
    "Gift",
    "Shop",
    "Heal",
    "Path / gate",
    "Scene trigger",
    "Dialogue choice",
    "State-gated",
)
TEXT_CACHE: dict[str, str] = {}
BODY_CACHE: dict[str, str] = {}


def read_script_blocks(root: Path = ROOT) -> dict[str, str]:
    blocks: dict[str, str] = {}
    label_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?:::|:)$", re.M)
    for path in sorted((root / "data").glob("**/*.inc")) + sorted((root / "data").glob("**/*.s")):
        text = path.read_text(encoding="utf-8", errors="replace")
        matches = list(label_re.finditer(text))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            blocks[match.group(1)] = text[match.end():end]
    return blocks


def resolve_block(label: str, blocks: dict[str, str], depth: int = 0, seen=None) -> str:
    if depth > 6 or label not in blocks:
        return ""
    seen = seen or set()
    if label in seen:
        return ""
    seen.add(label)
    body = blocks[label]
    refs = re.findall(r"\b(?:goto|call)\s+([A-Za-z_][A-Za-z0-9_]*)", body)
    return body + "\n" + "\n".join(
        resolve_block(ref, blocks, depth + 1, seen) for ref in refs
    )


def resolved(script: str, blocks: dict[str, str]) -> str:
    body = BODY_CACHE.get(script)
    if body is None:
        body = resolve_block(script, blocks)
        BODY_CACHE[script] = body
    return body


def clean_text(value: str) -> str:
    value = value.replace("\\p", " / ").replace("\\n", " ").replace("\\l", " ")
    value = value.replace("$", "").replace("{PLAYER}", "you")
    return re.sub(r"\s+", " ", value).strip()


def script_text(script: str, blocks: dict[str, str]) -> str:
    """Visible text from a script, following msgbox labels and goto/call."""
    cached = TEXT_CACHE.get(script)
    if cached is not None:
        return cached
    queue = [script]
    seen: set[str] = set()
    texts: list[str] = []
    while queue:
        label = queue.pop(0)
        if label in seen or label not in blocks:
            continue
        seen.add(label)
        body = resolved(label, blocks)
        strings = re.findall(r'\.string\s+"((?:[^"\\]|\\.)*)"', body)
        if strings:
            texts.append(clean_text(" ".join(strings)))
        queue.extend(re.findall(r"\bmsgbox\s+([A-Za-z_][A-Za-z0-9_]*)", body))
    text = " | ".join(dict.fromkeys(item for item in texts if item))
    TEXT_CACHE[script] = text
    return text


def command(body: str, *names: str) -> bool:
    return any(re.search(rf"^\s*{name}(?:_|\b)", body, re.M) for name in names)


def has_yes_no(body: str) -> bool:
    return bool(re.search(r"^\s*msgbox\s+[A-Za-z_][A-Za-z0-9_]*(?:,\s*MSGBOX_YESNO|\s*$)", body, re.M)
                and "MSGBOX_YESNO" in body)


def words(value: str) -> str:
    value = re.sub(r"^(OBJ_EVENT_GFX|MAP|SPECIES|ITEM|FLAG|VAR|MUS)_", "", value)
    value = re.sub(r"_(HNS|FRLG|Frlg)$", "", value, flags=re.I)
    parts = value.replace("_", " ").split()
    small = {"of", "the", "and"}
    return " ".join(
        part if part.isdigit() else (part.lower() if part.lower() in small else part.title())
        for part in parts
    )


def pretty_script(script: str, graphics: str) -> str:
    label = re.sub(r"^(?:[A-Za-z0-9]+_)*EventScript_", "", script)
    label = re.sub(r"^Pox[A-Za-z]*_", "", label)
    label = re.sub(r"^Pox(?=[A-Z])", "", label)
    label = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", label).replace("_", " ")
    label = re.sub(r"\s+", " ", label).strip()
    if (
        not label
        or re.fullmatch(r"(Npc|Object|EventScript)\d*", label, re.I)
        or "_hns_" in label.lower()
        or len(label) > 30
        or label.lower() in {"heal", "shop", "mart"}
    ):
        label = words(graphics)
    return label


def effect_roles(body: str, event: dict) -> tuple[set[str], dict]:
    roles: set[str] = set()
    details: dict = {}
    if command(body, "trainerbattle"):
        roles.add("Trainer battle")
    if command(body, "ingame_trade"):
        roles.add("In-game trade")
        details["trades"] = re.findall(r"\bINGAME_TRADE_[A-Z0-9_]+\b", body)
    if command(body, "giveitem", "givepokemon", "giveegg", "finditem"):
        roles.add("Gift")
        details["items"] = re.findall(r"\bITEM_[A-Z0-9_]+\b", body)
        details["species"] = re.findall(r"\bSPECIES_[A-Z0-9_]+\b", body)
    if command(body, "pokemart"):
        roles.add("Shop")
    if "HealPlayerParty" in body:
        roles.add("Heal")
    if command(body, "setflag", "clearflag", "removeobject", "addobject", "setwarp", "warp"):
        roles.add("Path / gate")
    elif re.search(r"^\s*setvar\s+VAR_(?:POX_|[A-Z0-9_]*STORY)", body, re.M):
        roles.add("Path / gate")
    if command(body, "fadescreen", "playbgm", "playfanfare"):
        roles.add("Scene trigger")
    if command(body, "multichoice") or "MSGBOX_YESNO" in body:
        roles.add("Dialogue choice")
    if str(event.get("flag", "0")) not in ("0", "", "None"):
        roles.add("State-gated")
    details["flags"] = re.findall(r"\bFLAG_[A-Z0-9_]+\b", body)
    return roles, details


def role_keywords(text: str) -> set[str]:
    """Functional words in a note's Key interactions row.

    Deliberately narrow: "gate" or "guard" alone is usually geography prose, not
    an NPC action. A row only adds a role when it describes blocking, a gate
    check, a trade, a cutscene, or a battle.
    """
    roles: set[str] = set()
    lower = text.lower()
    if re.search(r"\b(block|blocks|blocked|barrier|gate check|entrance check|locked|closed|lock|door watch)\b", lower):
        roles.add("Path / gate")
    if re.search(r"\b(cutscene|trigger)\b", lower):
        roles.add("Scene trigger")
    return roles


def note_rows(note) -> list[list[str]]:
    lines = [line.strip() for line in note.section("Key interactions").splitlines() if line.strip()]
    table = [line for line in lines if line.startswith("|")]
    if len(table) < 2:
        return []
    return [
        [cell.strip() for cell in row.strip().strip("|").split("|")]
        for row in table[2:]
    ]


def infer_maps(note, text: str) -> list[str]:
    explicit = [name for name in note.all_maps if name in text]
    if explicit:
        return explicit
    lower = text.lower()
    if "gym" in lower:
        matches = [name for name in note.all_maps if "Gym" in name]
        if matches:
            return matches
    for floor in ("b1f", "2f", "1f"):
        if floor in lower:
            matches = [name for name in note.all_maps if floor.upper() in name.upper()]
            if matches:
                return matches
    if re.search(r"\b(town|city|route)\b", lower):
        return note.maps
    if len(note.all_maps) == 1:
        return note.all_maps
    return []


def note_targets(note, blocks: dict[str, str]) -> dict:
    """Script and coordinate targets from the note's Key interactions table."""
    targets = {"scripts": {}, "coords": {}}
    for cells in note_rows(note):
        interaction = cells[0] if cells else ""
        where = cells[1] if len(cells) > 1 else ""
        text = " | ".join(cells)
        roles = role_keywords(text)
        scripts = [token for token in re.findall(r"`([^`]+)`", text) if token in blocks]
        for script in scripts:
            entry = targets["scripts"].setdefault(script, {"roles": set(), "story": set()})
            entry["roles"].update(roles)
            if interaction:
                entry["story"].add(interaction)
        maps = infer_maps(note, text)
        coords = re.findall(r"\((\d+),\s*(\d+)\)", where)
        for map_name in maps:
            for x, y in coords:
                key = (int(x), int(y))
                entry = targets["coords"].setdefault(map_name, {}).setdefault(
                    key, {"roles": set(), "story": set()}
                )
                entry["roles"].update(roles)
                if interaction:
                    entry["story"].add(interaction)
    return targets


def trainer_label(body: str, trainers: dict | None) -> tuple[str, list[str]]:
    ids = re.findall(r"\bTRAINER_[A-Z0-9_]+\b", body)
    if not ids:
        return "", []
    trainers = trainers or {}
    for trainer_id in ids:
        meta = (trainers.get(trainer_id) or {}).get("meta") or {}
        name = " ".join(part for part in (meta.get("Class"), meta.get("Name")) if part).strip()
        if name:
            return name, ids
    return ids[0], ids


def map_rows(
    data: dict,
    blocks: dict[str, str],
    note=None,
    trainers: dict | None = None,
) -> list[dict]:
    """Every real NPC on a map, classified as key or standard."""
    targets = note_targets(note, blocks) if note is not None else {"scripts": {}, "coords": {}}
    map_targets = targets["coords"].get(data["name"], {})
    rows: list[dict] = []
    for event in data.get("object_events", []):
        graphics = event.get("graphics_id", "")
        script = event.get("script", "")
        if any(marker in graphics for marker in SKIP_GRAPHICS):
            continue
        if not script or script in ("0x0", "0"):
            continue
        body = resolved(script, blocks)
        if not body:
            continue
        roles, details = effect_roles(body, event)

        script_target = targets["scripts"].get(script)
        coord_target = map_targets.get((event.get("x", -1), event.get("y", -1)))
        story: set[str] = set()
        for target in (script_target, coord_target):
            if not target:
                continue
            roles.update(target["roles"])
            story.update(target["story"])

        trainer_name, trainer_ids = trainer_label(body, trainers)
        if trainer_ids:
            roles.add("Trainer battle")
        text = script_text(script, blocks)
        if not roles and not story and not text:
            continue
        name = trainer_name or pretty_script(script, graphics)
        ordered_roles = [role for role in ROLE_ORDER if role in roles]
        row = {
            "name": name,
            "graphics": graphics,
            "script": script,
            "map": data["name"],
            "map_id": data.get("id", ""),
            "x": event.get("x", 0),
            "y": event.get("y", 0),
            "key": bool(roles),
            "roles": ordered_roles,
            "role": " · ".join(ordered_roles) if ordered_roles else "Talk only",
            "story": " · ".join(sorted(story)),
            "text": text,
            "items": details.get("items", []),
            "species": details.get("species", []),
            "trades": details.get("trades", []),
            "flags": list(dict.fromkeys(details.get("flags", []))),
            "trainers": trainer_ids,
        }
        rows.append(row)
    return rows
