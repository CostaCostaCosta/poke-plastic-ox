#!/usr/bin/env python3
"""Print a repo-grounded dossier for a Plastic Ox story note or map.

The story notes are design documents, but they must stay anchored to the real
ROM data. This tool is the bridge: it reads the note's front matter, resolves
every map it claims, and dumps the live objects, scripts, dialogue, trainers,
items, warps, encounters and story flags found in the checkout.

Examples:

    python3 plastic_ox/story/story_context.py pallet-town
    python3 plastic_ox/story/story_context.py LavenderTown_hns --json
    python3 plastic_ox/story/story_context.py --all --summary
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "plastic_ox/wiki"))

import story_notes  # noqa: E402
import build_wiki as wiki  # noqa: E402

FLAG_RE = re.compile(r"\bFLAG_[A-Z0-9_]+\b")
STRING_RE = re.compile(r'\.string\s+"((?:[^"\\]|\\.)*)"')


def clean_text(block: str) -> str:
    strings = STRING_RE.findall(block)
    if not strings:
        return ""
    text = " ".join(strings)
    text = text.replace("\\p", " / ").replace("\\n", " ").replace("\\l", " ")
    text = text.replace("$", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def script_text(script: str, blocks: dict[str, str]) -> str:
    """Resolve an NPC script's visible text, following goto/call and msgbox.

    Story scripts typically look like ``Pox_FujiGuide:: ... msgbox Pox_Text_X``
    where the ``.string`` lives in a separate label, so following only the
    script body misses most dialogue.
    """
    if not script or script not in blocks:
        return ""
    body = wiki.resolve_block(script, blocks)
    seen: set[str] = set()
    texts: list[str] = []
    queue = [script]
    while queue:
        label = queue.pop(0)
        if label in seen or label not in blocks:
            continue
        seen.add(label)
        block = wiki.resolve_block(label, blocks)
        text = clean_text(block)
        if text:
            texts.append(text)
        queue.extend(re.findall(r"\bmsgbox\s+([A-Za-z_][A-Za-z0-9_]*)", block))
    return " | ".join(dict.fromkeys(texts))


def resolve(name: str) -> tuple[story_notes.Note | None, list[str]]:
    notes = story_notes.load_notes(strict=False)
    for note in notes:
        if note.slug == name:
            return note, note.all_maps
    for note in notes:
        if name in note.all_maps:
            return note, note.all_maps
    return None, [name]


def map_record(name: str) -> dict | None:
    path = ROOT / "data/maps" / name / "map.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    data["_path"] = str(path.relative_to(ROOT))
    return data


def trainer_team(trainer_id: str, trainers: dict) -> list[str] | None:
    trainer = trainers.get(trainer_id)
    if not trainer:
        return None
    return [
        f'{mon["species"]} Lv.{mon.get("level", "?")}'
        for mon in trainer["mons"]
    ]


def dossier(name: str, blocks: dict[str, str], trainers: dict, encounters: dict, definitions: dict) -> dict:
    note, maps = resolve(name)
    record: dict = {
        "query": name,
        "note": None,
        "maps": [],
        "missing_maps": [],
    }
    if note:
        record["note"] = {
            "slug": note.slug,
            "title": note.title,
            "path": str(note.path.relative_to(ROOT)),
            "act": note.act,
            "depth": note.depth,
            "stage": note.meta.get("stage"),
            "status": note.meta.get("status"),
            "sections": list(note.sections),
            "missing_sections": [s for s in story_notes.REQUIRED_SECTIONS if s not in note.sections],
        }
    for map_name in maps:
        data = map_record(map_name)
        if not data:
            record["missing_maps"].append(map_name)
            continue
        entry: dict = {
            "name": map_name,
            "id": data.get("id"),
            "type": data.get("map_type", "").replace("MAP_TYPE_", ""),
            "weather": data.get("weather"),
            "music": data.get("music"),
            "connections": [
                f'{c.get("direction")} → {c.get("map")}' for c in data.get("connections") or []
            ],
            "warps": len(data.get("warp_events") or []),
            "coord_events": [
                {
                    "at": f'{c.get("x")},{c.get("y")}',
                    "script": c.get("script"),
                    "text": script_text(c.get("script", ""), blocks),
                }
                for c in data.get("coord_events") or []
            ],
            "npcs": [],
            "trainers": [],
            "items": [],
            "flags": [],
            "encounters": [],
        }
        trainer_ids: list[str] = []
        for event in data.get("object_events") or []:
            script = event.get("script", "")
            block = blocks.get(script, "")
            body = wiki.resolve_block(script, blocks)
            text = script_text(script, blocks)
            entry["npcs"].append(
                {
                    "local_id": event.get("local_id", ""),
                    "graphics": event.get("graphics_id"),
                    "at": f'{event.get("x")},{event.get("y")}',
                    "script": script,
                    "text": text,
                    "trainer_type": event.get("trainer_type"),
                }
            )
            for trainer_id in re.findall(r"\b(TRAINER_[A-Z0-9_]+)\b", body):
                if trainer_id not in trainer_ids:
                    trainer_ids.append(trainer_id)
            entry["flags"] += [f for f in FLAG_RE.findall(body) if f.startswith("FLAG_POX")]
        for trainer_id in trainer_ids:
            entry["trainers"].append({"id": trainer_id, "team": trainer_team(trainer_id, trainers)})
        for bg in data.get("bg_events") or []:
            if bg.get("type") == "hidden_item":
                entry["items"].append(f'hidden {bg.get("item")} at {bg.get("x")},{bg.get("y")}')
        for area in encounters.get(data.get("id"), []):
            for field in wiki.ENCOUNTER_FIELDS:
                if field not in area:
                    continue
                mons = area[field].get("mons", [])
                entry["encounters"].append(
                    {
                        "field": field,
                        "rate": area[field].get("encounter_rate"),
                        "mons": [f'{mon["species"]} {mon["min_level"]}-{mon["max_level"]}' for mon in mons],
                    }
                )
        entry["flags"] = list(dict.fromkeys(entry["flags"]))
        record["maps"].append(entry)
    return record


def render(record: dict) -> str:
    out: list[str] = []
    note = record["note"]
    if note:
        out.append(f'NOTE {note["slug"]}  "{note["title"]}"  act={note["act"]} depth={note["depth"]} status={note["status"]}')
        out.append(f'  file: {note["path"]}')
        if note["missing_sections"]:
            out.append(f'  MISSING SECTIONS: {note["missing_sections"]}')
    else:
        out.append(f"NO STORY NOTE for {record['query']} (create plastic_ox/story/locations/<slug>.md)")
    for missing in record["missing_maps"]:
        out.append(f"  MISSING MAP: {missing} (not in data/maps/)")
    for entry in record["maps"]:
        out.append("")
        out.append(f'== {entry["name"]} ({entry["id"]}, {entry["type"]}) ==')
        if entry["connections"]:
            out.append("  connections: " + "; ".join(entry["connections"]))
        out.append(f'  warps: {entry["warps"]}  npcs: {len(entry["npcs"])}  trainers: {len(entry["trainers"])}')
        if entry["flags"]:
            out.append("  pox flags: " + ", ".join(entry["flags"]))
        for npc in entry["npcs"]:
            text = npc["text"] or "(no text in script)"
            out.append(f'  NPC {npc["local_id"] or "-":<34} {npc["at"]:<7} {npc["graphics"]}')
            out.append(f'      script: {npc["script"]}')
            out.append(f'      says:   {text[:220]}')
        for trainer in entry["trainers"]:
            out.append(f'  TRAINER {trainer["id"]}: {trainer["team"]}')
        for item in entry["items"]:
            out.append(f"  ITEM {item}")
        for coord in entry["coord_events"]:
            out.append(f'  COORD {coord["at"]} -> {coord["script"]}: {coord["text"][:160]}')
        for encounter in entry["encounters"]:
            out.append(
                f'  ENCOUNTER {encounter["field"]} rate={encounter["rate"]} '
                f'{", ".join(encounter["mons"][:12])}'
            )
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", nargs="?", help="story-note slug or map name")
    parser.add_argument("--all", action="store_true", help="dump every story note")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--summary", action="store_true", help="dossier headers only")
    args = parser.parse_args()
    if not args.target and not args.all:
        parser.error("pass a slug/map name or --all")

    blocks = wiki.read_script_blocks()
    trainers = wiki.read_trainers()
    encounters, definitions = wiki.read_encounters()
    targets = (
        [note.slug for note in story_notes.load_notes()]
        if args.all
        else [args.target]
    )
    records = [dossier(target, blocks, trainers, encounters, definitions) for target in targets]
    if args.json:
        print(json.dumps(records if args.all else records[0], indent=2))
        return 0
    for record in records:
        if not args.summary:
            print(render(record))
            print()
            continue
        note = record["note"]
        label = note["slug"] if note else record["query"]
        maps = ", ".join(entry["name"] for entry in record["maps"]) or "-"
        print(f'{label:<34} act={note["act"] if note else "?"}  maps={maps}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
