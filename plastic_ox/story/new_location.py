#!/usr/bin/env python3
"""Create a new story note for a map, with grounded front matter.

    python3 plastic_ox/story/new_location.py LavenderTown_hns
    python3 plastic_ox/story/new_location.py PlasticOx_Silph --slug silph-co

The new file copies the section skeleton from `TEMPLATE.md` and fills the front
matter from `data/maps/<Map>/map.json`. It refuses to overwrite an existing note.
The validator will fail until the sections are written, which is the point.
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

KIND = {
    "MAP_TYPE_CITY": "City",
    "MAP_TYPE_TOWN": "Town",
    "MAP_TYPE_ROUTE": "Route",
    "MAP_TYPE_UNDERGROUND": "Cave",
    "MAP_TYPE_INDOOR": "Building",
}


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("map", help="data/maps directory name, e.g. LavenderTown_hns")
    parser.add_argument("--slug", help="note file slug (default derived from the map name)")
    parser.add_argument("--act", type=int, default=1, help="story act number (default 1)")
    parser.add_argument("--stage", default="TBD", help="progression stage string")
    parser.add_argument("--depth", choices=("full", "supporting"), default="full")
    args = parser.parse_args()

    map_dir = ROOT / "data/maps" / args.map
    map_json = map_dir / "map.json"
    if not map_json.exists():
        print(f"no map named {args.map} under data/maps/", file=sys.stderr)
        return 1
    data = json.loads(map_json.read_text(encoding="utf-8"))
    title = wiki.map_title(args.map)
    kind = KIND.get(data.get("map_type", ""), "Building")

    pages = {wiki.page_slug(item): item for item in wiki.read_maps()}
    page_slug = wiki.page_slug(data)
    wiki_slug = page_slug if page_slug in pages else "none"

    slug = args.slug or slugify(title)
    path = story_notes.NOTES_DIR / f"{slug}.md"
    if path.exists():
        print(f"{path.relative_to(ROOT)} already exists; edit it instead", file=sys.stderr)
        return 1

    front = [
        "---",
        f"title: {title}",
        f"slug: {slug}",
        f"kind: {kind}",
        f"act: {args.act}",
        f'stage: "{args.stage}"',
        f"depth: {args.depth}",
        f"wiki: {wiki_slug}",
        f"maps: [{args.map}]",
        "also_maps: []",
        "flags: []",
        "badges: []",
        "trainers: []",
        "items: []",
        "status: draft",
        "---",
        "",
        f"# {title}",
        "",
    ]
    template = story_notes.TEMPLATE.read_text(encoding="utf-8")
    body = template.split("---", 2)[2].lstrip("\n")
    # Drop the template's own explanation paragraph and title line.
    body = re.sub(r"^# .*?\n", "", body, count=1)
    body = body.split("## Snapshot", 1)[-1]
    body = "## Snapshot" + body
    path.write_text("\n".join(front) + "\n" + body, encoding="utf-8")

    print(f"created {path.relative_to(ROOT)}")
    if wiki_slug == "none":
        print("note: no generated wiki page for this map; the note will render only if you add one")
    print("next: fill Snapshot / Plot points / Key interactions / Dialogue guidance / Inspiration")
    print(f"      python3 plastic_ox/story/story_context.py {args.map}")
    print(f"      python3 plastic_ox/story/check_story_notes.py --note {slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
