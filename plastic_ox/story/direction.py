#!/usr/bin/env python3
"""Turn edited story notes into a direction bundle for an implementing agent.

The wiki editor lets a designer change the markdown notes in
``plastic_ox/story/locations/``. Those diffs are the design intent; this tool
packages them with the grounded facts an agent needs so the hand-off is one
file instead of a conversation:

    python3 plastic_ox/story/direction.py --slug ecruteakcity-hns \
        --intent "Give the gym staff distinct pre-battle lines."

    python3 plastic_ox/story/direction.py --all-dirty
    python3 plastic_ox/story/direction.py --all-dirty --stdout
    python3 plastic_ox/story/direction.py --slug route29-hns --json

The bundle is written to ``plastic_ox/story/directions/<timestamp>-<slug>.md``
with a ``.json`` sidecar for tools. It is deliberately self-contained: the
agent can start from the bundle without reading this script.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import npc_roles  # noqa: E402
import region  # noqa: E402
import story_notes  # noqa: E402

DIRECTIONS = HERE / "directions"


def git(*args: str, root: Path = ROOT) -> str:
    """Run git in the checkout; an empty string means "not available"."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return ""
    return result.stdout


def dirty_slugs(root: Path = ROOT) -> list[str]:
    """Story-note slugs with uncommitted changes (staged, unstaged, or new)."""
    output = git("status", "--porcelain", "--untracked-files=all", "--",
                 "plastic_ox/story/locations", root=root)
    slugs: list[str] = []
    for line in output.splitlines():
        path = line[3:].strip()
        if " -> " in path:  # renamed entry: "old -> new"
            path = path.split(" -> ", 1)[1]
        if path.endswith(".md"):
            slugs.append(Path(path).stem)
    return sorted(set(slugs))


def note_diff(note: story_notes.Note, root: Path = ROOT) -> str:
    """Unified diff of one note against HEAD, including brand-new notes."""
    relative = _relative(note.path, root)
    diff = git("diff", "--no-color", "--unified=3", "HEAD", "--", relative, root=root)
    if diff.strip():
        return diff.rstrip()
    tracked = git("ls-files", "--error-unmatch", "--", relative, root=root)
    if not tracked.strip():
        # New, untracked file: show it as an all-added diff.
        diff = git("diff", "--no-color", "--unified=3", "--no-index", "--",
                   "/dev/null", relative, root=root)
        return diff.rstrip()
    return ""


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def interactions(note: story_notes.Note) -> tuple[list[str], list[list[str]]]:
    """The Key interactions table as headers plus rows, if it has one."""
    lines = [line for line in note.section("Key interactions").splitlines() if line.strip()]
    table = [line for line in lines if line.strip().startswith("|")]
    if not table:
        return [], []
    header = table_cells(table[0])
    rows = [table_cells(line) for line in table[2:]]
    return header, rows


def open_questions(note: story_notes.Note) -> list[str]:
    return [
        line.strip()[2:].strip()
        for line in note.section("Open questions").splitlines()
        if line.strip().startswith(("- ", "* "))
    ]


def map_facts(map_names: list[str], root: Path = ROOT) -> list[dict]:
    facts = []
    for name in map_names:
        path = root / "data/maps" / name / "map.json"
        if not path.exists():
            facts.append({"map": name, "exists": False})
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            facts.append({"map": name, "exists": False})
            continue
        objects = data.get("object_events") or []
        facts.append(
            {
                "map": name,
                "exists": True,
                "id": data.get("id", ""),
                "objects": len(objects),
                "objects_without_script": sum(1 for event in objects if not event.get("script")),
                "warps": len(data.get("warp_events") or []),
                "connections": [
                    f'{conn.get("direction", "?")} → {conn.get("map", "?")}'
                    for conn in data.get("connections") or []
                ],
            }
        )
    return facts


def validator_context(root: Path = ROOT):
    """Build the expensive map/index context once per export."""
    if root.resolve() != ROOT.resolve():
        return None
    try:
        sys.path.insert(0, str(ROOT / "plastic_ox/wiki"))
        import build_wiki as wiki  # noqa: WPS433 (local import keeps this tool light)
        import check_story_notes
    except ImportError:
        return None
    pages = {wiki.page_slug(data): data for data in wiki.read_maps()}
    return pages, check_story_notes.Index()


def validation_for(
    note: story_notes.Note,
    root: Path = ROOT,
    context=None,
) -> dict | None:
    """Run the note validator in-process when pointed at the real checkout."""
    if root.resolve() != ROOT.resolve():
        return None
    try:
        import check_story_notes
    except ImportError:
        return None
    context = context or validator_context(root)
    if context is None:
        return None
    pages, index = context
    try:
        errors, warnings = check_story_notes.check_note(note, index, pages)
    except Exception as error:  # a broken repo must not hide the diff
        return {"errors": [f"validator crashed: {error}"], "warnings": []}
    return {"errors": errors, "warnings": warnings}


def npc_context(
    selected: list[story_notes.Note],
    root: Path = ROOT,
    blocks: dict[str, str] | None = None,
    trainers: dict | None = None,
) -> dict:
    """Key NPCs per note, using the same classifier as the region map."""
    blocks = blocks if blocks is not None else npc_roles.read_script_blocks(root)
    if trainers is None:
        try:
            sys.path.insert(0, str(ROOT / "plastic_ox/wiki"))
            import build_wiki

            trainers = build_wiki.read_trainers()
        except Exception:
            trainers = {}
    context = {}
    for note in selected:
        rows: list[dict] = []
        for map_name in note.all_maps:
            if map_name in region.RETIRED_MAPS:
                continue
            path = root / "data/maps" / map_name / "map.json"
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            rows.extend(npc_roles.map_rows(data, blocks, note=note, trainers=trainers))
        for row in rows:
            row["text"] = row["text"][:160]
        key = [row for row in rows if row["key"]]
        context[note.slug] = {
            "key_npcs": key,
            "key_count": len(key),
            "standard_count": sum(1 for row in rows if not row["key"]),
        }
    return context


def _slug_label(notes: list[story_notes.Note]) -> str:
    if len(notes) == 1:
        return notes[0].slug
    return "multiple" if len(notes) > 4 else "-".join(note.slug for note in notes[:3]) + "-and-more"


def _table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_No rows in the note's Key interactions table._"
    width = max(len(row) for row in rows)
    headers = headers + [""] * (width - len(headers))
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        row = row + [""] * (width - len(row))
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")
    return "\n".join(lines)


def direction_markdown(
    selected: list[story_notes.Note],
    intent: str,
    created: datetime,
    diffs: dict[str, str],
    validations: dict[str, dict | None],
    facts: dict[str, list[dict]],
    npcs: dict | None = None,
    root: Path = ROOT,
) -> tuple[str, dict]:
    identifier = f'{created:%Y-%m-%d-%H%M%S}-{_slug_label(selected)}'
    title = selected[0].title if len(selected) == 1 else f"{len(selected)} story notes"
    out = [
        f"# Direction — {title}",
        "",
        f"- **Bundle:** `{identifier}`",
        f"- **Created:** {created:%Y-%m-%d %H:%M %Z}",
        f"- **Notes:** {len(selected)}",
        f"- **Scope:** {', '.join(note.slug for note in selected)}",
        "",
        "## How to use this bundle",
        "",
        "This bundle is direction, not code. The story notes it quotes are the design",
        "source; the unified diffs show exactly what the designer changed. Read the",
        "full note files before touching a map.",
        "",
        "1. Treat `plastic_ox/plastic_ox_story_v7.md` as the story bible. If a note",
        "   disagrees with it, the bible wins and the note should be corrected in the",
        "   same change.",
        "2. Implement the **target behavior** in each Key interactions row. Preserve",
        "   every explicit **must not** and every identifier the note names.",
        "3. Edit map and script sources, never generated `events.inc`,",
        "   `connections.inc`, or `trainers.h`; regenerate those with the build.",
        "4. Do not edit `plastic_ox/wiki/site/`; rebuild it instead.",
        "5. Before finishing, update the note (`status`, Current behavior), write a",
        "   run log in `plastic_ox/story/runs/YYYY-MM-DD-<slug>.md`, and run the",
        "   verification commands at the bottom of this bundle.",
        "",
    ]
    if intent.strip():
        out += ["## Direction from the designer", "", intent.strip(), ""]
    else:
        out += [
            "## Direction from the designer",
            "",
            "_No extra intent was supplied. Implement the changed note sections and the",
            "target behavior below._",
            "",
        ]

    for note in selected:
        diff = diffs.get(note.slug, "")
        out += [f"## Note — {note.title} (`{note.slug}`)", ""]
        wiki = str(note.meta.get("wiki") or "none")
        wiki_label = "none" if wiki in ("", "none") else f"{wiki}.html"
        out += [
            f"- **Path:** `{_relative(note.path, root)}`",
            f"- **Wiki page:** `{wiki_label}`",
            f"- **Act / stage:** {note.act} · {note.meta.get('stage', '—')}",
            f"- **Status:** {note.meta.get('status', '—')} · depth {note.depth}",
            f"- **Maps:** {', '.join(f'`{name}`' for name in note.all_maps) or '—'}",
        ]
        flags = note.meta.get("flags") or []
        trainers = note.meta.get("trainers") or []
        items = note.meta.get("items") or []
        if flags:
            out.append("- **Flags:** " + ", ".join(f"`{flag}`" for flag in flags))
        if trainers:
            out.append("- **Trainers:** " + ", ".join(f"`{trainer}`" for trainer in trainers))
        if items:
            out.append("- **Items:** " + ", ".join(f"`{item}`" for item in items))
        out += ["", "### What changed in the note", ""]
        if diff:
            out += ["````diff", diff, "````", ""]
        else:
            out += [
                "_No uncommitted diff for this note. The direction above and the target",
                "behavior below are still the brief._",
                "",
            ]

        headers, rows = interactions(note)
        out += ["### Key interactions to implement or preserve", ""]
        out.append(_table(headers, rows))
        out.append("")

        npc_data = (npcs or {}).get(note.slug) or {}
        key_npcs = npc_data.get("key_npcs") or []
        out += ["### Key NPCs on these maps", ""]
        if key_npcs:
            out.append(
                "These NPCs act on the player. Preserve or rewrite them according to the "
                "interaction target, and keep the standard talkers separate."
            )
            out.append("")
            out.append(_table(
                ["NPC", "Where", "Interaction", "Current line"],
                [
                    [
                        row["name"],
                        f'{row["map"]} ({row["x"]}, {row["y"]})',
                        row["role"],
                        row["text"][:120],
                    ]
                    for row in key_npcs
                ],
            ))
            out.append("")
            out.append(
                f"{npc_data.get('standard_count', 0)} standard talk-only NPCs are not listed here."
            )
            out.append("")
        else:
            out += ["_No functional key NPC found for these maps._", ""]

        questions = open_questions(note)
        if questions:
            out += ["### Open questions", ""]
            out += [f"- {question}" for question in questions]
            out.append("")

        note_facts = facts.get(note.slug, [])
        if note_facts:
            out += ["### Grounded map context", ""]
            out += [
                "| Map | Map ID | Objects | Objects without script | Warps | Connections |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
            for fact in note_facts:
                if not fact.get("exists"):
                    out.append(f'| `{fact["map"]}` | _missing_ |  |  |  |  |')
                    continue
                connections = "; ".join(fact["connections"]) or "—"
                out.append(
                    f'| `{fact["map"]}` | `{fact["id"]}` | {fact["objects"]} | '
                    f'{fact["objects_without_script"]} | {fact["warps"]} | {connections} |'
                )
            out.append("")

        if validations.get(note.slug) is not None:
            validation = validations[note.slug] or {}
            errors = validation.get("errors") or []
            warnings = validation.get("warnings") or []
            out += ["### Note validation at export time", ""]
            if errors:
                out += [f"- **ERROR** {error}" for error in errors]
            if warnings:
                out += [f"- warning: {warning}" for warning in warnings]
            if not errors and not warnings:
                out.append("- Clean: 0 errors, 0 warnings.")
            out.append("")

    out += [
        "## Verification",
        "",
        "```sh",
        "python3 plastic_ox/story/check_story_notes.py",
        "python3 plastic_ox/wiki/build_wiki.py",
        "python3 plastic_ox/wiki/build_wiki.py --check",
        "# plus the demo/regression tests for the maps you touched",
        "```",
        "",
        "## Definition of done",
        "",
        "- Every changed note's Key interactions target behavior is either implemented",
        "  or explicitly deferred in that note's Open questions.",
        "- Dialogue is unique per speaker and matches the note's voice constraints.",
        "- The note's `status` reflects reality, and the run log records maps changed,",
        "  tests run, screenshots walked, and anything still open.",
        "- `check_story_notes.py` is clean and the wiki generated pages are current.",
        "",
    ]
    markdown = "\n".join(out)

    payload = {
        "bundle": identifier,
        "created": created.isoformat(),
        "title": title,
        "intent": intent.strip(),
        "scope": [note.slug for note in selected],
        "notes": [
            {
                "slug": note.slug,
                "title": note.title,
                "path": _relative(note.path, root),
                "wiki": note.meta.get("wiki"),
                "act": note.act,
                "stage": note.meta.get("stage"),
                "depth": note.depth,
                "status": note.meta.get("status"),
                "maps": note.all_maps,
                "flags": note.meta.get("flags") or [],
                "trainers": note.meta.get("trainers") or [],
                "items": note.meta.get("items") or [],
                "diff": diffs.get(note.slug, ""),
                "interactions": {
                    "headers": interactions(note)[0],
                    "rows": interactions(note)[1],
                },
                "open_questions": open_questions(note),
                "validation": validations.get(note.slug),
                "map_facts": facts.get(note.slug, []),
                "key_npcs": (npcs or {}).get(note.slug, {}).get("key_npcs", []),
                "key_npc_count": (npcs or {}).get(note.slug, {}).get("key_count", 0),
                "standard_npc_count": (npcs or {}).get(note.slug, {}).get("standard_count", 0),
            }
            for note in selected
        ],
        "markdown": markdown,
    }
    return markdown, payload


def build_direction(
    slugs: list[str] | None = None,
    all_dirty: bool = False,
    intent: str = "",
    out_dir: Path | None = None,
    root: Path = ROOT,
    validate: bool = True,
    created: datetime | None = None,
) -> dict:
    """Write one markdown bundle plus a JSON sidecar; return their paths."""
    available = {
        note.slug: note
        for note in story_notes.load_notes(directory=root / "plastic_ox/story/locations", strict=False)
    }
    if all_dirty:
        selected_slugs = dirty_slugs(root)
    else:
        selected_slugs = list(dict.fromkeys(slugs or []))
    if not selected_slugs:
        raise ValueError("nothing selected: pass --slug or --all-dirty")
    missing = [slug for slug in selected_slugs if slug not in available]
    if missing:
        raise ValueError(f"unknown note slug(s): {', '.join(missing)}")
    selected = [available[slug] for slug in selected_slugs]

    diffs = {note.slug: note_diff(note, root) for note in selected}
    context = validator_context(root) if validate else None
    validations = {
        note.slug: validation_for(note, root, context=context) if validate else None
        for note in selected
    }
    facts = {note.slug: map_facts(note.all_maps, root) for note in selected}
    npcs = npc_context(selected, root)
    created = created or datetime.now().astimezone()
    markdown, payload = direction_markdown(
        selected, intent, created, diffs, validations, facts, npcs=npcs, root=root
    )

    directory = out_dir or (root / "plastic_ox/story/directions")
    directory.mkdir(parents=True, exist_ok=True)
    stem = payload["bundle"]
    markdown_path = directory / f"{stem}.md"
    json_path = directory / f"{stem}.json"
    suffix = 2
    while markdown_path.exists() or json_path.exists():
        markdown_path = directory / f"{stem}-{suffix}.md"
        json_path = directory / f"{stem}-{suffix}.json"
        suffix += 1
    markdown_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "bundle": markdown_path.stem,
        "path": markdown_path,
        "json_path": json_path,
        "markdown": markdown,
        "payload": payload,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--slug", action="append", default=[], help="note slug to include (repeatable)")
    parser.add_argument("--all-dirty", action="store_true", help="include every uncommitted story note")
    parser.add_argument("--intent", default="", help="designer direction, as markdown")
    parser.add_argument("--intent-file", help="read designer direction from a file")
    parser.add_argument("--stdout", action="store_true", help="print the bundle instead of writing files")
    parser.add_argument("--json", action="store_true", help="print the JSON sidecar instead of markdown")
    parser.add_argument("--out-dir", help="write bundles here (default plastic_ox/story/directions)")
    args = parser.parse_args()

    intent = args.intent
    if args.intent_file:
        intent = Path(args.intent_file).read_text(encoding="utf-8")
    try:
        if args.stdout or args.json:
            available = {
                note.slug: note
                for note in story_notes.load_notes(strict=False)
            }
            slugs = dirty_slugs() if args.all_dirty else list(dict.fromkeys(args.slug))
            if not slugs:
                parser.error("pass --slug or --all-dirty")
            missing = [slug for slug in slugs if slug not in available]
            if missing:
                parser.error(f"unknown note slug(s): {', '.join(missing)}")
            selected = [available[slug] for slug in slugs]
            diffs = {note.slug: note_diff(note) for note in selected}
            context = validator_context()
            validations = {
                note.slug: validation_for(note, context=context) for note in selected
            }
            facts = {note.slug: map_facts(note.all_maps) for note in selected}
            npcs = npc_context(selected)
            created = datetime.now().astimezone()
            markdown, payload = direction_markdown(
                selected, intent, created, diffs, validations, facts, npcs=npcs
            )
            print(json.dumps(payload, indent=2) if args.json else markdown)
            return 0
        result = build_direction(
            slugs=args.slug or None,
            all_dirty=args.all_dirty,
            intent=intent,
            out_dir=Path(args.out_dir) if args.out_dir else None,
        )
    except ValueError as error:
        print(f"direction: {error}", file=sys.stderr)
        return 1
    print(result["path"])
    print(result["json_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
