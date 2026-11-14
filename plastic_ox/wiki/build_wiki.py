#!/usr/bin/env python3
"""Generate the Plastic Ox static wiki directly from ROM source data."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

WIKI = Path(__file__).resolve().parent
ROOT = WIKI.parents[1]
sys.path.insert(0, str(ROOT / "plastic_ox/story"))
import npc_roles  # noqa: E402
import region  # noqa: E402
import story_notes  # noqa: E402
import story_render  # noqa: E402
SITE = WIKI / "site"
MAP_TYPES = {"MAP_TYPE_ROUTE": "Route", "MAP_TYPE_TOWN": "Town", "MAP_TYPE_CITY": "City", "MAP_TYPE_UNDERGROUND": "Cave"}
ENCOUNTER_FIELDS = ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons", "hidden_mons")
FIELD_NAMES = {"land_mons": "Walking", "water_mons": "Surfing", "rock_smash_mons": "Rock Smash", "fishing_mons": "Fishing", "hidden_mons": "Hidden"}
def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def words(value: str) -> str:
    value = re.sub(r"^(MAP|SPECIES|ITEM|OBJ_EVENT_GFX|WEATHER|MAP_TYPE|MUS)_", "", value)
    value = re.sub(r"_(HNS|FRLG)$", "", value, flags=re.I)
    parts = value.replace("_", " ").split()
    small = {"of", "the", "and"}
    return " ".join(p if p.isdigit() else (p.lower() if p.lower() in small else p.title()) for p in parts)


def map_title(name: str) -> str:
    name = re.sub(r"_(hns|Frlg)$", "", name)
    name = re.sub(r"^PlasticOx_", "", name)
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name).replace("_", " ")
    return name.replace("Route20", "Route 20").replace("Route", "Route ").replace("  ", " ").strip()


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", map_title(name).lower()).strip("-")


def page_slug(data: dict) -> str:
    """Keep source suffixes so similarly named FRLG/HNS maps cannot collide."""
    return re.sub(r"[^a-z0-9]+", "-", data["name"].lower()).strip("-")


def source_files() -> list[Path]:
    paths = [ROOT / "plastic_ox/alpha/region_manifest.json", ROOT / "data/maps/map_groups.json",
             ROOT / "src/data/wild_encounters.json", ROOT / "src/data/trainers.party",
             ROOT / "src/data/trainers_frlg.party"]
    paths += sorted((ROOT / "data/maps").glob("*/map.json"))
    paths += sorted((ROOT / "data/maps").glob("*/scripts.inc"))
    paths += sorted((ROOT / "data/scripts").glob("*.inc"))
    paths += sorted((ROOT / "data").glob("**/*.s"))
    paths += sorted((ROOT / "plastic_ox/story/locations").glob("*.md"))
    paths += [
        ROOT / "plastic_ox/plastic_ox_topology.svg",
        WIKI / "assets/style.css",
        WIKI / "assets/wiki.js",
        WIKI / "assets/region.css",
        WIKI / "assets/region.js",
    ]
    return [p for p in paths if p.exists()]


def fingerprint(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def region_names() -> set[str]:
    manifest = load(ROOT / "plastic_ox/alpha/region_manifest.json")
    names: set[str] = set(manifest.get("native_seams", {}).keys())
    for transition in manifest.get("transitions", []):
        names.update((transition.get("source", ""), transition.get("destination", "")))
    groups = load(ROOT / "data/maps/map_groups.json")
    for group, members in groups.items():
        if group.startswith("gMapGroup_PlasticOx"):
            names.update(members)
    return names - {""}


def read_maps() -> list[dict]:
    wanted = region_names()
    maps = []
    for path in sorted((ROOT / "data/maps").glob("*/map.json")):
        data = load(path)
        if data.get("name") in wanted and data.get("map_type") in MAP_TYPES:
            data["_path"] = path
            maps.append(data)
    return sorted(maps, key=lambda m: (MAP_TYPES[m["map_type"]] != "City", MAP_TYPES[m["map_type"]] != "Town", map_title(m["name"])))


def read_script_blocks() -> dict[str, str]:
    blocks: dict[str, str] = {}
    label_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?:::|:)$", re.M)
    for path in sorted((ROOT / "data").glob("**/*.inc")) + sorted((ROOT / "data").glob("**/*.s")):
        text = path.read_text(encoding="utf-8", errors="replace")
        matches = list(label_re.finditer(text))
        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            blocks[match.group(1)] = text[match.end():end]
    return blocks


def resolve_block(label: str, blocks: dict[str, str], depth: int = 0) -> str:
    if depth > 5 or label not in blocks:
        return ""
    body = blocks[label]
    # Follow simple wrapper scripts while retaining their own commands.
    refs = re.findall(r"\b(?:goto|call)\s+([A-Za-z_][A-Za-z0-9_]*)", body)
    return body + "\n" + "\n".join(resolve_block(ref, blocks, depth + 1) for ref in refs)


def read_trainers() -> dict[str, dict]:
    trainers: dict[str, dict] = {}
    for path in (ROOT / "src/data/trainers.party", ROOT / "src/data/trainers_frlg.party"):
        text = path.read_text(encoding="utf-8")
        starts = list(re.finditer(r"^===\s+(TRAINER_[A-Z0-9_]+)\s+===$", text, re.M))
        for i, match in enumerate(starts):
            body = text[match.end(): starts[i + 1].start() if i + 1 < len(starts) else len(text)].strip()
            chunks = re.split(r"\n\s*\n", body)
            meta: dict[str, str] = {}
            mons = []
            for line in chunks[0].splitlines() if chunks else []:
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            for chunk in chunks[1:]:
                lines = [line.strip() for line in chunk.splitlines() if line.strip() and not line.lstrip().startswith("/*")]
                if not lines or ":" in lines[0] and not lines[0].startswith("SPECIES_"):
                    continue
                mon = {"species": lines[0], "moves": []}
                for line in lines[1:]:
                    if line.startswith("- "):
                        mon["moves"].append(line[2:])
                    elif ":" in line:
                        k, v = line.split(":", 1)
                        mon[k.strip().lower()] = v.strip()
                    elif line.endswith(" Nature"):
                        mon["nature"] = line[:-7]
                mons.append(mon)
            trainers[match.group(1)] = {"meta": meta, "mons": mons}
    return trainers


def read_encounters() -> tuple[dict[str, list[dict]], dict[str, dict]]:
    root = load(ROOT / "src/data/wild_encounters.json")
    by_map: dict[str, list[dict]] = defaultdict(list)
    definitions: dict[str, dict] = {}
    for group in root.get("wild_encounter_groups", []):
        field_defs = {field["type"]: field for field in group.get("fields", [])}
        for encounter in group.get("encounters", []):
            if "map" not in encounter:
                continue
            # Reused FRLG/Hoenn map IDs can have legacy encounter records in the
            # same generated file. Plastic Ox-owned tables are deliberately
            # namespaced gPox*; showing every matching ID mixes games together.
            if not encounter.get("base_label", "").startswith("gPox"):
                continue
            by_map[encounter["map"]].append(encounter)
            for field, definition in field_defs.items():
                definitions.setdefault(field, definition)
    return by_map, definitions


def time_name(label: str) -> str:
    match = re.search(r"_(Morning|Day|Night|FireRed|LeafGreen)$", label, re.I)
    if not match:
        return "All day"
    value = match.group(1)
    return {"firered": "FireRed", "leafgreen": "LeafGreen"}.get(value.lower(), value.title())


def encounter_heading(label: str) -> str:
    period = time_name(label)
    if "Route2South" in label:
        return f"South · {period}"
    if "Route2North" in label:
        return f"North · {period}"
    return period


def encounter_rows(area: dict, definition: dict) -> list[tuple[str, str, str]]:
    rates = area.get("weights", definition.get("encounter_rates", []))
    groups = definition.get("groups", {})
    rod_for_slot = {idx: words(group) for group, indices in groups.items() for idx in indices}
    rows = []
    for idx, mon in enumerate(area.get("mons", [])):
        level = str(mon["min_level"]) if mon["min_level"] == mon["max_level"] else f'{mon["min_level"]}–{mon["max_level"]}'
        method = rod_for_slot.get(idx, "")
        chance = f"{rates[idx]}%" if idx < len(rates) else "—"
        rows.append((words(mon["species"]), level, f"{method} {chance}".strip()))
    return rows


def trainer_ids_for_map(data: dict, blocks: dict[str, str]) -> list[str]:
    found = []
    for event in data.get("object_events", []):
        body = resolve_block(event.get("script", ""), blocks)
        found += re.findall(r"\b(TRAINER_[A-Z0-9_]+)\b", body)
    return list(dict.fromkeys(found))


def items_for_map(data: dict, blocks: dict[str, str]) -> list[dict]:
    items = []
    for event in data.get("bg_events", []):
        if event.get("type") == "hidden_item":
            items.append({"item": words(event["item"]), "kind": "Hidden", "location": f'({event["x"]}, {event["y"]})'})
    for event in data.get("object_events", []):
        body = resolve_block(event.get("script", ""), blocks)
        ids = re.findall(r"\b(?:finditem|giveitem)\s+(ITEM_[A-Z0-9_]+)", body)
        kind = "Poké Ball" if "ITEM_BALL" in event.get("graphics_id", "") else "Gift / scripted"
        for item in ids:
            items.append({"item": words(item), "kind": kind, "location": f'({event["x"]}, {event["y"]})'})
    unique = {(x["item"], x["kind"], x["location"]): x for x in items}
    return list(unique.values())


def table(headers: list[str], rows: list[tuple | list]) -> str:
    if not rows:
        return '<p class="empty">None found in the current game data.</p>'
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def sidebar(maps: list[dict], current: str = "") -> str:
    sections = []
    for kind in ("City", "Town", "Route", "Cave"):
        links = []
        for data in maps:
            if MAP_TYPES[data["map_type"]] == kind:
                title = map_title(data["name"])
                links.append(f'<li><a href="{page_slug(data)}.html"{" aria-current=\"page\"" if data["name"] == current else ""}>{html.escape(title)}</a></li>')
        if links:
            sections.append(f"<h2>{kind}s</h2><ul>{''.join(links)}</ul>")
    sections.append('<h2>Design</h2><ul><li><a href="region.html">Region map</a></li><li><a href="story.html">Story notes</a></li></ul>')
    return "".join(sections)


def shell(title: str, body: str, maps: list[dict], current: str = "", head: str = "") -> str:
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — Plastic Ox Wiki</title><link rel="stylesheet" href="assets/style.css">{head}</head>
<body><header class="topbar"><a class="brand" href="index.html">Plastic Ox Wiki</a><nav class="topnav"><a href="index.html">Locations</a><a href="region.html">Region map</a><a href="story.html">Story notes</a></nav></header>
<div class="layout"><nav class="sidebar"><a href="index.html">Main page</a>{sidebar(maps, current)}</nav>
<main class="content">{body}<footer>Automatically generated from the Plastic Ox ROM source. Edit the game data, then rebuild the wiki.</footer></main></div>
<script src="assets/wiki.js"></script></body></html>'''


def page_for_map(data: dict, maps: list[dict], blocks: dict[str, str], trainers: dict[str, dict], encounters: dict[str, list[dict]], definitions: dict[str, dict], notes: dict[str, story_notes.Note]) -> str:
    title = map_title(data["name"])
    kind = MAP_TYPES[data["map_type"]]
    by_id = {m["id"]: m for m in maps}
    map_connections = data.get("connections") or []
    connections = []
    for conn in map_connections:
        dest = by_id.get(conn["map"])
        name = map_title(dest["name"]) if dest else words(conn["map"])
        cell = f'<a href="{page_slug(dest)}.html">{html.escape(name)}</a>' if dest else html.escape(name)
        connections.append((conn["direction"].title(), cell))
    trainer_ids = trainer_ids_for_map(data, blocks)
    info = f'''<aside class="infobox"><h2>{html.escape(title)}</h2><dl>
<dt>Type</dt><dd>{kind}</dd><dt>Map ID</dt><dd><code>{html.escape(data["id"])}</code></dd>
<dt>Weather</dt><dd>{html.escape(words(data.get("weather", "None")))}</dd>
<dt>Music</dt><dd>{html.escape(words(data.get("music", "Unknown")))}</dd>
<dt>Cycling</dt><dd>{"Yes" if data.get("allow_cycling") else "No"}</dd></dl></aside>'''
    conn_html = '<ul>' + ''.join(f'<li><b>{html.escape(c["direction"].title())}:</b> <a href="{page_slug(by_id[c["map"]])}.html">{html.escape(map_title(by_id[c["map"]]["name"]))}</a></li>' if c["map"] in by_id else f'<li><b>{html.escape(c["direction"].title())}:</b> {html.escape(words(c["map"]))}</li>' for c in map_connections) + '</ul>'
    if not map_connections:
        conn_html = '<p class="empty">No direct map-edge connections.</p>'

    encounter_html = []
    for encounter in encounters.get(data["id"], []):
        period = encounter_heading(encounter.get("base_label", ""))
        for field in ENCOUNTER_FIELDS:
            if field not in encounter:
                continue
            area = encounter[field]
            rows = encounter_rows(area, definitions.get(field, {}))
            encounter_html.append(f'<h3>{FIELD_NAMES[field]} — {period}</h3><p>Encounter rate: {area.get("encounter_rate", "—")}%</p>' + table(["Pokémon", "Level", "Chance / method"], rows))
    if not encounter_html:
        encounter_html.append('<p class="empty">No wild encounter table is assigned to this map.</p>')

    trainer_html = []
    for trainer_id in trainer_ids:
        trainer = trainers.get(trainer_id)
        if not trainer:
            trainer_html.append(f'<p><code>{html.escape(trainer_id)}</code> (team definition not found)</p>')
            continue
        meta = trainer["meta"]
        mons = []
        for mon in trainer["mons"]:
            details = []
            if mon.get("level"): details.append("Lv. " + mon["level"])
            if "@" in mon["species"]:
                species, held = mon["species"].split("@", 1)
                species = species.strip(); details.append("holding " + held.strip())
            else: species = mon["species"]
            moves = ", ".join(mon.get("moves", [])) or "level-up moves"
            mons.append((species, "; ".join(details) or "Lv. 100 (default)", moves))
        trainer_html.append(f'<section class="trainer"><h3>{html.escape(meta.get("Class", "Trainer"))} {html.escape(meta.get("Name", trainer_id))}</h3><span class="tag">{html.escape(meta.get("Battle Type", "Singles"))}</span><span class="tag">{html.escape(meta.get("AI", "Default AI"))}</span>{table(["Pokémon", "Details", "Moves"], mons)}</section>')
    if not trainer_html:
        trainer_html.append('<p class="empty">No trainer battles are attached to this map.</p>')

    items = items_for_map(data, blocks)
    note = story_render.note_for_map(notes, data["name"])
    npc_rows = npc_roles.map_rows(data, blocks, note=note, trainers=trainers)
    key_npcs = [row for row in npc_rows if row["key"]]
    standard_npcs = [row for row in npc_rows if not row["key"]]
    story_html = story_render.render_story_section(note) if note else story_render.render_missing_section(title, page_slug(data))
    key_npc_html = table(
        ["NPC", "Interaction", "Coordinates", "Current line"],
        [(row["name"], row["role"], f'({row["x"]}, {row["y"]})', row["text"][:110]) for row in key_npcs],
    ) if key_npcs else '<p class="empty">No functional key NPC on this map.</p>'
    standard_npc_html = table(
        ["NPC", "Story note", "Coordinates", "Current line"],
        [
            (
                row["name"],
                row["story"] or "Talk only",
                f'({row["x"]}, {row["y"]})',
                row["text"][:110],
            )
            for row in standard_npcs
        ],
    ) if standard_npcs else '<p class="empty">No standard NPC on this map.</p>'
    body = f'''<h1>{html.escape(title)}</h1>{info}<p class="lede">{html.escape(title)} is a {kind.lower()} in the Plastic Ox region.</p>
<div class="source-note">This article is generated from <code>{html.escape(str(data["_path"].relative_to(ROOT)))}</code> and linked encounter, script, and trainer data.</div>
{story_html}
<h2>Connections</h2>{conn_html}
<h2>Pokémon</h2>{''.join(encounter_html)}
<h2>Trainers</h2>{''.join(trainer_html)}
<h2>Items</h2>{table(["Item", "Method", "Coordinates"], [(x["item"], x["kind"], x["location"]) for x in items])}
<h2>Key NPCs</h2>
<p class="hint">NPCs who act on the player: battles, gifts, trades, shops, gates, scene triggers, or state changes.
<a href="region.html">See the full region map</a>.</p>
{key_npc_html}
<h2>Standard NPCs</h2>
<p class="hint">Talk-only people. They carry the place's voice, but they do not change play.</p>
{standard_npc_html}'''
    return shell(title, body, maps, data["name"])


def build(out: Path, digest: str) -> tuple[int, int, int]:
    maps = read_maps()
    blocks = read_script_blocks()
    trainers = read_trainers()
    encounters, definitions = read_encounters()
    notes = story_notes.load_notes()
    note_index = story_notes.notes_by_map(notes)
    pages = {page_slug(data): data for data in maps}
    (out / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(WIKI / "assets/style.css", out / "assets/style.css")
    shutil.copy2(WIKI / "assets/wiki.js", out / "assets/wiki.js")
    shutil.copy2(WIKI / "assets/region.css", out / "assets/region.css")
    shutil.copy2(WIKI / "assets/region.js", out / "assets/region.js")
    topology = ROOT / "plastic_ox/plastic_ox_topology.svg"
    if topology.exists():
        shutil.copy2(topology, out / "assets/topology.svg")
    for data in maps:
        (out / f'{page_slug(data)}.html').write_text(page_for_map(data, maps, blocks, trainers, encounters, definitions, note_index), encoding="utf-8")
    def card(data: dict) -> str:
        note = story_render.note_for_map(note_index, data["name"])
        story_meta = (
            f'<span class="meta">Act {note.act} · {html.escape(str(note.meta.get("stage", "")))}</span>'
            if note else '<span class="meta">No story note yet</span>'
        )
        search = f' act {note.act} {note.meta.get("stage", "")} {note.title}' if note else ""
        return (f'<article class="card" data-search-item data-search="{html.escape(search)}">'
                f'<h2><a href="{page_slug(data)}.html">{html.escape(map_title(data["name"]))}</a></h2>'
                f'<span class="tag">{MAP_TYPES[data["map_type"]]}</span>'
                f'<span class="tag">{len(encounters.get(data["id"], []))} encounter table(s)</span>'
                f'{story_meta}</article>')

    cards = "".join(card(data) for data in maps)
    index_body = f'''<h1>Plastic Ox locations</h1><p class="lede">A code-synchronized guide to every route, city, and town in the connected Plastic Ox region.</p>
<div class="source-note">Generated from {len(maps)} maps. Encounter tables, trainer teams, items, and NPCs reflect the checked-out ROM source.</div>
<input class="search" type="search" data-search placeholder="Search locations, acts, or story stages…" aria-label="Search locations">
<p class="empty" data-search-empty hidden>No location matches that search.</p>
<div class="cards">{cards}</div>'''
    index_body = index_body.replace('<div class="source-note">Generated from', f'<div class="source-note">Explore the <a href="region.html">clickable region map</a> or the <a href="story.html">{len(notes)} design notes</a>. Generated from')
    (out / "index.html").write_text(shell("Main page", index_body, maps), encoding="utf-8")
    story_body = story_render.render_story_index(notes, pages, lambda slug: f"{slug}.html")
    story_body = story_body.replace(
        '<div class="story-filters">',
        '<div class="source-note">Prefer a map? '
        '<a href="region.html">Open the clickable region map</a>, which follows the same notes in story order.</div>'
        '<div class="story-filters">',
        1,
    )
    (out / "story.html").write_text(shell("Story notes", story_body, maps), encoding="utf-8")
    region_data = region.build_region_data(notes, blocks, trainers)
    (out / "region.html").write_text(
        shell(
            "Region map",
            region.render_body(region_data),
            maps,
            head='<link rel="stylesheet" href="assets/region.css">',
        ),
        encoding="utf-8",
    )
    covered = sum(1 for data in maps if data["name"] in note_index)
    metadata = {"source_sha256": digest, "pages": len(maps), "story_notes": len(notes),
                "story_coverage": f"{covered}/{len(maps)}",
                "region_stops": region_data["counts"]["stops"],
                "region_key_npcs": region_data["counts"]["key_npcs"],
                "region_standard_npcs": region_data["counts"]["standard_npcs"],
                "generator": "plastic_ox/wiki/build_wiki.py"}
    (out / "build.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return len(maps), sum(len(v) for key, v in encounters.items() if any(m["id"] == key for m in maps)), len(notes)


def directory_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(str(file.relative_to(path)).encode())
        digest.update(file.read_bytes())
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the generated site is stale")
    args = parser.parse_args()
    paths = source_files()
    digest = fingerprint(paths)
    if args.check:
        with tempfile.TemporaryDirectory(prefix="plastic-ox-wiki-") as tmp:
            temp = Path(tmp)
            pages, tables, note_count = build(temp, digest)
            if not SITE.exists() or directory_digest(temp) != directory_digest(SITE):
                print("Plastic Ox wiki is stale; run python3 plastic_ox/wiki/build_wiki.py", file=sys.stderr)
                return 1
    else:
        if SITE.exists():
            shutil.rmtree(SITE)
        pages, tables, note_count = build(SITE, digest)
    print(f"Plastic Ox wiki: {pages} location pages, {tables} encounter tables, "
          f"{note_count} story notes ({'current' if args.check else 'generated'}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
