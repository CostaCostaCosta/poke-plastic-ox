#!/usr/bin/env python3
"""Audit NPC dialogue across every Plastic Ox map.

Two checks:

* duplicates (gate): no two NPCs may speak identical text. An NPC is an object
  event's script label; its text is every message reachable from that script
  (msgbox, trainerbattle texts, branches) that is defined in a map scripts.inc
  or a shared data/scripts/plastic_ox_*.inc file. Engine-wide shared text
  (nurse, mart clerk, Common_*) is out of scope.
* sprites (report, or gate with --strict): heuristics that flag dialogue which
  does not fit the speaker's graphics_id, e.g. a child talking as a working
  professional, or a sailor-free sprite talking like a deckhand. Accepted
  exceptions live in plastic_ox/tools/npc_dialogue_allow.json.

    python3 plastic_ox/tools/audit_npc_dialogue.py                # duplicate gate + sprite gate
    python3 plastic_ox/tools/audit_npc_dialogue.py --sprites      # list sprite flags (report only)
    python3 plastic_ox/tools/audit_npc_dialogue.py --map FortreeCity --dump

"Plastic Ox maps" are the region maps (region_manifest.json + gMapGroup_PlasticOx*)
plus every map reachable from them through warps.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOW = ROOT / "plastic_ox/tools/npc_dialogue_allow.json"
LABEL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?:::|:)\s*$", re.M)
TOKEN_RE = re.compile(r"\b([A-Z][A-Za-z0-9]*_[A-Za-z0-9_]+)\b")
STRING_RE = re.compile(r'^\s*\.string\s+"(.*)"\s*$', re.M)
# Objects behind these flags never appear in play (hidden donor actors).
NEVER_VISIBLE = {"FLAG_POX_HIDE_UNUSED_ACTOR"}
SKIP_PREFIXES = ("Common_", "EventScript_", "Std_", "gText_", "Text_")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def region_maps(maps: dict[str, dict]) -> set[str]:
    manifest = load(ROOT / "plastic_ox/alpha/region_manifest.json")
    names = set(manifest.get("native_seams", {}).keys())
    for t in manifest.get("transitions", []):
        names.update((t.get("source", ""), t.get("destination", "")))
    for group, members in load(ROOT / "data/maps/map_groups.json").items():
        if group.startswith("gMapGroup_PlasticOx"):
            names.update(members)
    by_id = {d.get("id"): n for n, d in maps.items()}
    todo = [n for n in names if n in maps]
    seen = set(todo)
    while todo:
        data = maps[todo.pop()]
        for warp in data.get("warp_events", []) or []:
            dest = by_id.get(warp.get("dest_map"))
            if dest and dest not in seen:
                seen.add(dest)
                todo.append(dest)
        for conn in data.get("connections") or []:
            dest = by_id.get(conn.get("map"))
            if dest and dest not in seen:
                seen.add(dest)
                todo.append(dest)
    return seen


def read_blocks() -> tuple[dict[str, str], dict[str, Path]]:
    blocks: dict[str, str] = {}
    origin: dict[str, Path] = {}
    files = sorted((ROOT / "data/maps").glob("*/scripts.inc")) + sorted((ROOT / "data/scripts").glob("plastic_ox_*.inc"))
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        matches = list(LABEL_RE.finditer(text))
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            blocks[m.group(1)] = text[m.end():end]
            origin[m.group(1)] = path
    return blocks, origin


def text_of(body: str) -> str:
    return "".join(STRING_RE.findall(body))


def normalise(raw: str) -> str:
    s = re.sub(r"\{[^}]*\}", " ", raw)
    s = re.sub(r"\\[nlp]", " ", s).replace("$", " ")
    return re.sub(r"\s+", " ", s).strip().lower()


def reachable_texts(label: str, blocks: dict[str, str]) -> list[str]:
    out: list[str] = []
    seen = {label}
    todo = [label]
    while todo:
        cur = todo.pop()
        body = blocks.get(cur, "")
        if STRING_RE.search(body):
            out.append(cur)
            continue
        for tok in TOKEN_RE.findall(body):
            if tok in blocks and tok not in seen and not tok.startswith(SKIP_PREFIXES):
                seen.add(tok)
                todo.append(tok)
    return out


def collect(map_filter: set[str] | None = None):
    maps = {}
    for path in (ROOT / "data/maps").glob("*/map.json"):
        try:
            maps[path.parent.name] = load(path)
        except json.JSONDecodeError:
            pass
    wanted = region_maps(maps)
    blocks, origin = read_blocks()
    npcs = []  # dicts: map, script, gfx, local_id, texts{label: raw}
    for name in sorted(wanted):
        if map_filter and name not in map_filter:
            continue
        for obj in maps[name].get("object_events", []) or []:
            if obj.get("flag") in NEVER_VISIBLE:
                continue
            script = obj.get("script", "")
            if not script or script in ("0x0", "NULL") or script not in blocks:
                continue
            texts = {lab: text_of(blocks[lab]) for lab in reachable_texts(script, blocks)}
            npcs.append({"map": name, "script": script, "gfx": obj.get("graphics_id", ""),
                         "local_id": obj.get("local_id", ""), "x": obj.get("x"), "y": obj.get("y"),
                         "texts": texts, "file": str(origin[script].relative_to(ROOT))})
    return npcs


def find_duplicates(npcs, allow) -> list[str]:
    by_text: dict[str, set[tuple[str, str]]] = defaultdict(set)
    sample: dict[str, str] = {}
    for npc in npcs:
        for lab, raw in npc["texts"].items():
            norm = normalise(raw)
            if len(norm) < 12:  # "...", "Hm?", yes/no prompts
                continue
            by_text[norm].add((npc["script"], lab))
            sample[norm] = f"{npc['map']}"
    errors = []
    allowed = set(allow.get("shared_scripts", {}))
    shared_texts = set(allow.get("shared_texts", {}))
    for norm, users in sorted(by_text.items()):
        users = {(s, l) for s, l in users if l not in shared_texts}
        scripts = {s for s, _ in users if s not in allowed}
        if len(scripts) > 1:
            where = ", ".join(sorted(f"{s} ({l})" for s, l in users))
            errors.append(f'duplicate NPC text "{norm[:70]}" spoken by: {where}')
    # One script attached to several visible NPCs on different maps is one line said twice.
    users_by_script: dict[str, set[str]] = defaultdict(set)
    for npc in npcs:
        if any(normalise(t) for t in npc["texts"].values()):
            users_by_script[npc["script"]].add(npc["map"])
    # The same script on several visible NPCs of one map is one line said twice.
    per_map: dict[tuple[str, str], int] = defaultdict(int)
    for npc in npcs:
        if any(len(normalise(t)) >= 12 for t in npc["texts"].values()):
            per_map[(npc["map"], npc["script"])] += 1
    for (mapname, script), count in sorted(per_map.items()):
        if count > 1 and script not in allowed:
            errors.append(f"script {script} is used by {count} NPCs on {mapname}")
    for script, where in sorted(users_by_script.items()):
        if len(where) > 1 and script not in allowed:
            errors.append(f"script {script} is shared by NPCs on {len(where)} maps: {', '.join(sorted(where))}")
    return errors


# ---- sprite plausibility -------------------------------------------------
CHILD = re.compile(r"OBJ_EVENT_GFX_(YOUNGSTER|LITTLE_BOY|LITTLE_GIRL|BOY|GIRL|NINJA_BOY|TWIN|SCHOOL_KID|BUG_CATCHER|LASS|PICNICKER|CAMPER|TUBER|RICH_BOY|POKEFAN_KID|BOY_\d|GIRL_\d|BUG_CATCHER_\d|SWIMMER_KID|KID)")
ELDER = re.compile(r"OBJ_EVENT_GFX_(OLD_MAN|OLD_WOMAN|EXPERT|GRANNY|ELDER|SAGE)")
SCIENTIST = re.compile(r"OBJ_EVENT_GFX_(SCIENTIST|PROF|BIRCH|OAK|ELM|MAXIE|ARCHIE)")
SAILOR = re.compile(r"OBJ_EVENT_GFX_(SAILOR|FISHERMAN|SWIMMER|CAPT|TUBER|BEAUTY_SWIM|SURF)")
GROWNUP_CLAIMS = [
    (re.compile(r"\b(my (wife|husband|grandson|granddaughter|grandchild|grandkids?|son|daughter|kids|employees|staff|crew|shift|boss|pension|mortgage|salary|paycheck))\b"), "speaks as a parent/employee"),
    (re.compile(r"\b(i (work|worked|research|researched|study the|lecture|supervise|manage|run the|captain|have been working)|we researchers|our (lab|team of researchers|field researchers)|field researchers?|in my day|when i was young|years ago, i|back in my day|i retired|my career|my research|my lab|my colleagues?|my customers|my employees)\b"), "speaks as a working adult/elder"),
]
INANIMATE = re.compile(r"OBJ_EVENT_GFX_(CUTTABLE_TREE|POKE_BALL|ITEM_BALL|BREAKABLE_ROCK|PUSHABLE_BOULDER|SIGN|MAIL|BIRTH_ISLAND_STONE)")
FIRST_PERSON = re.compile(r"(?:^|[.!?] )(i|i'm|i've|i'll|my|we|we're|our|me)\b")
CHILD_ONLY = re.compile(r"\b(my (mom|mommy|dad|daddy) (says|said|told)|homework|my teacher|at school|field trip|recess|when i grow up)\b")


def sprite_flags(npcs, allow) -> list[str]:
    allowed = set(allow.get("sprite_ok", {}))
    flags = []
    for npc in npcs:
        if npc["script"] in allowed:
            continue
        gfx = npc["gfx"]
        text = " ".join(normalise(t) for t in npc["texts"].values())
        if not text:
            continue
        reasons = []
        if INANIMATE.search(gfx):
            m = FIRST_PERSON.search(text)
            if m:
                reasons.append(f"object sprite speaks in the first person ('{m.group(0).strip()}')")
            for r in reasons:
                flags.append(f"{npc['map']} {npc['script']} [{gfx.replace('OBJ_EVENT_GFX_', '')}]: {r}")
            continue
        if CHILD.search(gfx):
            for rx, why in GROWNUP_CLAIMS:
                m = rx.search(text)
                if m:
                    reasons.append(f"child sprite {why} ('{m.group(0)}')")
        else:
            m = CHILD_ONLY.search(text)
            if m and not ELDER.search(gfx) and "MOM" not in gfx:
                reasons.append(f"adult sprite talks like a child ('{m.group(0)}')")
        if ELDER.search(gfx):
            m = re.search(r"\b(when i grow up|my (mom|dad) (says|said)|at school)\b", text)
            if m:
                reasons.append(f"elder sprite talks like a child ('{m.group(0)}')")
        for r in reasons:
            flags.append(f"{npc['map']} {npc['script']} [{gfx.replace('OBJ_EVENT_GFX_', '')}]: {r}")
    return flags


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--map", action="append")
    ap.add_argument("--dump", action="store_true", help="print every NPC with its sprite and text")
    ap.add_argument("--sprites", action="store_true", help="only report sprite flags, never fail")
    args = ap.parse_args()
    allow = load(ALLOW) if ALLOW.exists() else {}
    npcs = collect(set(args.map) if args.map else None)
    if args.dump:
        for npc in npcs:
            print(f"== {npc['map']} {npc['script']} [{npc['gfx']}] ({npc['x']},{npc['y']})")
            for lab, raw in npc["texts"].items():
                print(f"   {lab}: {normalise(raw)}")
        return 0
    flags = sprite_flags(npcs, allow)
    if args.sprites:
        print("\n".join(flags))
        print(f"{len(flags)} sprite flag(s) across {len(npcs)} NPCs")
        return 0
    dups = find_duplicates(npcs, allow)
    for line in dups + flags:
        print("ERROR:", line)
    print(f"audit_npc_dialogue: {len(npcs)} NPCs, {len(dups)} duplicate(s), {len(flags)} sprite flag(s)")
    return 1 if dups or flags else 0


if __name__ == "__main__":
    sys.exit(main())
