#!/usr/bin/env python3
"""Print the next story/dialogue work order from the location notes.

This is the autonomy hook: an agent asks "what should I improve next?" and gets
a grounded brief instead of guessing. Orders are notes that are not yet
``status: implemented``, sorted by act and story stage, with the live map facts
and known gaps that the pass must address.

    python3 plastic_ox/story/next_pass.py
    python3 plastic_ox/story/next_pass.py --act 3
    python3 plastic_ox/story/next_pass.py --slug ecruteakcity-hns
    python3 plastic_ox/story/next_pass.py --all
    python3 plastic_ox/story/next_pass.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "plastic_ox/wiki"))

import story_notes  # noqa: E402
import build_wiki as wiki  # noqa: E402


def map_facts(map_names: list[str]) -> list[dict]:
    blocks = wiki.read_script_blocks()
    facts = []
    for name in map_names:
        path = ROOT / "data/maps" / name / "map.json"
        if not path.exists():
            facts.append({"map": name, "exists": False})
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        npcs = []
        dead = 0
        pox = 0
        for event in data.get("object_events") or []:
            script = event.get("script", "")
            if "ITEM_BALL" in event.get("graphics_id", ""):
                continue
            text = ""
            if script and script in blocks:
                body = wiki.resolve_block(script, blocks)
                text = body
                if script.startswith("Pox_") or "Pox_" in script:
                    pox += 1
            if not text:
                dead += 1
            npcs.append({"script": script, "at": f'{event.get("x")},{event.get("y")}', "has_text": bool(text)})
        facts.append(
            {
                "map": name,
                "exists": True,
                "id": data.get("id"),
                "npcs": len(npcs),
                "npc_with_script": pox,
                "npc_without_text": dead,
                "warps": len(data.get("warp_events") or []),
                "connections": [f'{c.get("direction")} → {c.get("map")}' for c in data.get("connections") or []],
            }
        )
    return facts


def open_questions(note: story_notes.Note, limit: int = 4) -> list[str]:
    lines = [line.strip("- ").strip() for line in note.section("Open questions").splitlines() if line.strip().startswith("-")]
    return lines[:limit]


def work_order(note: story_notes.Note) -> dict:
    return {
        "slug": note.slug,
        "title": note.title,
        "status": note.meta.get("status"),
        "act": note.act,
        "stage": note.meta.get("stage"),
        "depth": note.depth,
        "wiki_page": f'{note.meta.get("wiki")}.html',
        "note_path": str(note.path.relative_to(ROOT)),
        "maps": map_facts(note.all_maps),
        "flags": note.meta.get("flags", []),
        "trainers": note.meta.get("trainers", []),
        "dialogue_seed": note.dialogue_seed,
        "open_questions": open_questions(note),
        "commands": [
            f'python3 plastic_ox/story/story_context.py {note.slug}',
            f'python3 plastic_ox/story/check_story_notes.py --note {note.slug}',
            "python3 plastic_ox/wiki/build_wiki.py --check",
        ],
    }


def render(order: dict) -> str:
    out = [
        f'WORK ORDER — {order["title"]}  ({order["slug"]})',
        f'  note     {order["note_path"]}',
        f'  status   {order["status"]}  act={order["act"]}  depth={order["depth"]}',
        f'  stage    {order["stage"]}',
        f'  wiki     {order["wiki_page"]}',
        "",
        "MAPS",
    ]
    for fact in order["maps"]:
        if not fact.get("exists"):
            out.append(f'  {fact["map"]}: MISSING')
            continue
        out.append(
            f'  {fact["map"]} ({fact["id"]}): {fact["npcs"]} NPCs, '
            f'{fact["npc_without_text"]} with no script text, {fact["warps"]} warps'
        )
        if fact["connections"]:
            out.append("    " + "; ".join(fact["connections"]))
    if order["flags"]:
        out += ["", "FLAGS", "  " + ", ".join(order["flags"])]
    if order["trainers"]:
        out += ["", "TRAINERS", "  " + ", ".join(order["trainers"])]
    if order["dialogue_seed"]:
        out += ["", "VOICE SEED", f'  "{order["dialogue_seed"]}"']
    if order["open_questions"]:
        out += ["", "OPEN QUESTIONS"]
        out += [f"  - {question}" for question in order["open_questions"]]
    out += ["", "START HERE", f'  {order["commands"][0]}', "  Then the plastic-ox-story-dialogue skill."]
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--act", type=int, help="only notes in this act")
    parser.add_argument("--slug", help="specific note slug")
    parser.add_argument("--all", action="store_true", help="list every open note, no brief")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    notes = story_notes.load_notes(strict=False)
    if args.slug:
        notes = [note for note in notes if note.slug == args.slug]
        if not notes:
            print(f"no note named {args.slug}", file=sys.stderr)
            return 1
    if args.act:
        notes = [note for note in notes if note.act == args.act]
    pending = [note for note in notes if note.meta.get("status") != "implemented"]
    pending.sort(key=lambda note: (note.act, str(note.meta.get("stage", "")), note.title.lower()))
    if not pending:
        print("Every note in scope is marked implemented. Run the validator and the wiki build to confirm.")
        return 0
    if args.all:
        for note in pending:
            print(f'{note.slug:<40} act={note.act}  {note.meta.get("stage", "")}')
        print(f"\n{len(pending)} note(s) awaiting implementation.")
        return 0
    orders = [work_order(note) for note in pending]
    if args.json:
        print(json.dumps(orders if len(orders) > 1 else orders[0], indent=2))
        return 0
    print(render(orders[0]))
    if len(orders) > 1:
        print(f'\n({len(orders) - 1} more note(s) queued; use --all to list them.)')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
