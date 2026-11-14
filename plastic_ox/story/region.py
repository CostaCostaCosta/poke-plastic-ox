#!/usr/bin/env python3
"""Build the clickable Plastic Ox story map.

The region is not a conventional connected overworld: it is a convergence of
Kanto, Johto, and Hoenn, with optional donor maps and a few deliberate orphans.
This module turns the location notes into a story-ordered map. The order below
is the main-line traversal used by the wiki's Region map page and its
Previous/Next controls; supporting/audit notes remain clickable but are skipped
by the default sequence.

To reorder the story, edit ``STORY_ORDER``. Notes missing from the list are
appended after it in act/title order, so a new note still appears.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import npc_roles  # noqa: E402
import story_notes  # noqa: E402
import story_render  # noqa: E402

RETIRED_MAPS = {"PlasticOx_MortyGym"}

STORY_ORDER = [
    # Act I — the opening network and Gym 1
    "pallet-town",
    "route101",
    "oldaletown",
    "route29-hns",
    "route46-hns",
    "darkcave-southside-hns",
    "route30-hns",
    "route31-hns",
    "route2-frlg",
    "route2-hns",
    "cherrygrovecity-hns",
    "ilexforest-hns",
    "rustboro-city",
    "route3-hns",
    "route4-hns",
    "route14-hns",
    "route24-hns",
    "route25-hns",
    "route34-hns",
    # Act I — Mt. Moon, Goldenrod, the road to Ecruteak
    "route44-hns",
    "mtmoon-cave-hns",
    "route33-hns",
    "goldenrodcity-hns",
    "goldenrodcity-departmentstore-7f-hns",
    "goldenrodcity-departmentstore-7fnight-hns",
    "route35-hns",
    "nationalpark-normal-hns",
    "route36-hns",
    "route37-hns",
    # Act II — Ecruteak, the tower, and the eastward turn
    "ecruteakcity-hns",
    "plasticox-burnedtower",
    "plasticox-burnedtowerb1f",
    "route38-hns",
    "route119",
    "fortreecity",
    "route110",
    "route16-hns",
    # Act III — Lavender, the underground bypass, Cinnabar, Seafoam, Mossdeep
    "lavender-town",
    "route8-frlg",
    "route7-hns",
    "route103",
    "route12-hns",
    "cinnabarisland-frlg",
    "plasticox-route20west",
    "route21-north-frlg",
    "route21-south-frlg",
    "route21-hns",
    "plasticox-route20east",
    "mossdeepcity",
    # Act IV — Saffron
    "saffroncity-hns",
    "route19-frlg",
    "route6-hns",
    "route5-hns",
    # Act V — Meteor Falls, Blackthorn, Victory Road, the League
    "route115",
    "meteorfalls-1f-1r",
    "route45-hns",
    "blackthorncity-hns",
    "plasticox-victoryroad",
    "indigoplateau-hns",
    # Postgame
    "battlefrontier-outsidewest",
    "plasticox-whirlislands",
]


def page_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def map_title(name: str) -> str:
    name = re.sub(r"_(hns|Frlg)$", "", name)
    name = re.sub(r"^PlasticOx_", "", name)
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name).replace("_", " ")
    name = re.sub(r"(Route)(\d+)([A-Z])", r"\1 \2 \3", name)
    name = re.sub(r"(Route)(\d+)$", r"\1 \2", name)
    return name.replace("Route20", "Route 20").replace("  ", " ").strip()


def ordered_notes(notes: list[story_notes.Note] | None = None) -> list[story_notes.Note]:
    notes = notes if notes is not None else story_notes.load_notes()
    index = {slug: position for position, slug in enumerate(STORY_ORDER)}
    return sorted(
        notes,
        key=lambda note: (
            index.get(note.slug, len(STORY_ORDER) + 10_000),
            note.act,
            str(note.meta.get("stage", "")),
            note.title.lower(),
        ),
    )


def load_map(name: str, root: Path = ROOT) -> dict | None:
    path = root / "data/maps" / name / "map.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def map_facts(name: str, root: Path = ROOT) -> dict:
    data = load_map(name, root)
    if data is None:
        return {"map": name, "exists": False}
    objects = data.get("object_events") or []
    return {
        "map": name,
        "title": map_title(name),
        "retired": name in RETIRED_MAPS,
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


def build_region_data(
    notes: list[story_notes.Note] | None = None,
    blocks: dict[str, str] | None = None,
    trainers: dict | None = None,
    root: Path = ROOT,
) -> dict:
    notes = ordered_notes(notes)
    blocks = blocks if blocks is not None else npc_roles.read_script_blocks(root)
    mainline = [note.slug for note in notes if note.depth == "full"]
    mainline_index = {slug: position for position, slug in enumerate(mainline)}
    stops = []
    stages: list[dict] = []
    stage_seen: set[tuple[int, str]] = set()

    for position, note in enumerate(notes):
        rows: list[dict] = []
        facts: list[dict] = []
        for map_name in note.all_maps:
            data = load_map(map_name, root)
            facts.append(map_facts(map_name, root))
            if data is None or map_name in RETIRED_MAPS:
                continue
            rows.extend(
                npc_roles.map_rows(data, blocks, note=note, trainers=trainers)
            )
        rows.sort(
            key=lambda row: (
                note.all_maps.index(row["map"]) if row["map"] in note.all_maps else 999,
                row["y"],
                row["x"],
                row["name"].lower(),
            )
        )
        for row in rows:
            row["text"] = row["text"][:180]
        key_npcs = [row for row in rows if row["key"]]
        standard_npcs = [row for row in rows if not row["key"]]
        try:
            summary = story_render.first_sentence(note)
        except Exception:
            summary = ""
        wiki = str(note.meta.get("wiki") or "")
        stage = str(note.meta.get("stage") or "Unstaged")
        if (note.act, stage) not in stage_seen:
            stage_seen.add((note.act, stage))
            stages.append({"act": note.act, "stage": stage})
        stops.append(
            {
                "slug": note.slug,
                "title": note.title,
                "act": note.act,
                "stage": stage,
                "depth": note.depth,
                "status": note.meta.get("status", ""),
                "wiki": f"{wiki}.html" if wiki and wiki != "none" else "",
                "note_path": str(note.path.relative_to(root)) if root in note.path.parents else str(note.path),
                "summary": summary,
                "maps": note.all_maps,
                "map_facts": facts,
                "flags": note.meta.get("flags") or [],
                "trainers": note.meta.get("trainers") or [],
                "items": note.meta.get("items") or [],
                "key_npcs": key_npcs,
                "standard_npcs": standard_npcs,
                "key_count": len(key_npcs),
                "standard_count": len(standard_npcs),
                "order": position,
                "mainline": note.depth == "full",
                "mainline_index": mainline_index.get(note.slug),
            }
        )

    return {
        "version": 1,
        "stops": stops,
        "stages": stages,
        "acts": story_render.ACT_LABELS,
        "counts": {
            "stops": len(stops),
            "mainline": len(mainline),
            "supporting": len(stops) - len(mainline),
            "key_npcs": sum(stop["key_count"] for stop in stops),
            "standard_npcs": sum(stop["standard_count"] for stop in stops),
        },
    }


def render_body(data: dict) -> str:
    counts = data["counts"]
    noscript = "".join(
        f'<li><a href="{html.escape(stop["wiki"])}">{html.escape(stop["title"])}</a>'
        f' — Act {stop["act"]} · {html.escape(stop["stage"])}'
        f' · {stop["key_count"]} key NPCs</li>'
        for stop in data["stops"]
        if stop["wiki"]
    )
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f'''<section class="region-page">
<header class="region-head">
  <p class="eyebrow">Design navigation</p>
  <h1>Plastic Ox region map</h1>
  <p class="lede">Every location in the storyline, in order. Click a stop to inspect it,
  or follow the route with <strong>Previous</strong> and <strong>Next</strong>.
  Key NPCs are separated from the people who only talk.</p>
  <p class="region-legend">
    <span><b>{counts["mainline"]}</b> main-line stops</span>
    <span><b>{counts["supporting"]}</b> supporting / audit notes</span>
    <span><b>{counts["key_npcs"]}</b> key NPCs</span>
    <span><b>{counts["standard_npcs"]}</b> standard NPCs</span>
    <a href="assets/topology.svg">Open the physical design SVG</a>
  </p>
  <details class="region-physical">
    <summary>Physical design map (SVG)</summary>
    <p class="hint">The older v0.6.1 layout sketch, kept as a geography view. It is not a
      verified progression graph; the clickable storyline map below is current.</p>
    <a href="assets/topology.svg"><img src="assets/topology.svg"
      alt="Physical design map of the Plastic Ox region with towns, routes, and caves"></a>
  </details>
</header>

<div class="region-toolbar">
  <div class="region-nav">
    <button type="button" id="prev-stop" class="primary" aria-keyshortcuts="Alt+ArrowLeft">← Previous stop</button>
    <button type="button" id="next-stop" class="primary" aria-keyshortcuts="Alt+ArrowRight">Next stop →</button>
  </div>
  <p id="region-position" class="region-position" role="status" aria-live="polite">Loading map…</p>
  <label class="inline-check"><input type="checkbox" id="skip-supporting" checked>
    Skip supporting / audit locations</label>
</div>

<div class="region-layout">
  <section class="region-map" aria-labelledby="region-map-title">
    <div class="region-map-head">
      <h2 id="region-map-title">Storyline map</h2>
      <p class="hint">The map is a scrollable pane; the selected stop stays in view.</p>
    </div>
    <div id="region-map-body" class="region-map-scroll" tabindex="0"
      aria-label="Scrollable storyline map"></div>
  </section>
  <aside id="region-detail" class="region-detail" aria-labelledby="region-detail-title">
    <p class="empty">Loading the region…</p>
  </aside>
</div>

<p id="region-announce" class="sr-only" role="status" aria-live="polite"></p>

<noscript>
  <style>.region-toolbar, .region-layout {{ display: none; }}</style>
  <h2>All stops</h2>
  <p>This map needs JavaScript. The same locations are listed here in story order.</p>
  <ol class="region-noscript">{noscript}</ol>
</noscript>
</section>
<script id="region-data" type="application/json">{payload}</script>
<script src="assets/region.js"></script>'''


if __name__ == "__main__":
    data = build_region_data()
    print(json.dumps(data["counts"], indent=2))
    print(f'{len(data["stops"])} stops, {len(data["stages"])} stage groups')
