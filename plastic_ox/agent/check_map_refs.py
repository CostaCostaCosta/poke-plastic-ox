#!/usr/bin/env python3
"""Static reference check for map wiring in poke-plastic-ox.

Catches the mistakes that otherwise only appear in a build or an emulator:
missing script labels, warps to unknown maps or out-of-range warp ids, unknown
trainer ids, unknown flags/items in map JSON, and object visibility flags that
do not exist.

    python3 plastic_ox/agent/check_map_refs.py                 # every Plastic Ox map
    python3 plastic_ox/agent/check_map_refs.py --map FortreeCity
    python3 plastic_ox/agent/check_map_refs.py --changed       # git diff maps
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "plastic_ox/wiki"))

import build_wiki as wiki  # noqa: E402

LABEL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?:::|:)$", re.M)
FLAG_RE = re.compile(r"\b(FLAG_[A-Z0-9_]+)\b")
TRAINER_RE = re.compile(r"\b(TRAINER_[A-Z0-9_]+)\b")
ITEM_RE = re.compile(r"\b(ITEM_[A-Z0-9_]+)\b")


def all_labels() -> set[str]:
    labels: set[str] = set()
    for pattern in ("**/*.inc", "**/*.s"):
        for path in (ROOT / "data").glob(pattern):
            text = path.read_text(encoding="utf-8", errors="replace")
            labels.update(LABEL_RE.findall(text))
            # pox_fruit_tree <Name>, ... emits PlasticOx_BerryTree_<Name>.
            for name in re.findall(r"^\s*pox_fruit_tree\s+([A-Za-z0-9_]+)\s*,", text, re.M):
                labels.add(f"PlasticOx_BerryTree_{name}")
    return labels


def define_set(pattern: str, *paths: str, flags: int = re.M) -> set[str]:
    found: set[str] = set()
    regex = re.compile(pattern, flags)
    for name in paths:
        path = ROOT / name
        if path.exists():
            found.update(regex.findall(path.read_text(encoding="utf-8", errors="replace")))
    return found


def load_maps() -> dict[str, dict]:
    maps = {}
    for path in (ROOT / "data/maps").glob("*/map.json"):
        try:
            maps[path.parent.name] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
    return maps


def resolve_local(label: str, text: str) -> str:
    """Follow a script label to the body that actually does the work."""
    body = re.search(rf"^{re.escape(label)}::(.*?)(?=^[A-Za-z_][A-Za-z0-9_]*::|\Z)", text, re.M | re.S)
    return body.group(1) if body else ""


def check(map_name: str, data: dict, maps: dict, labels: set[str], script_text: defaultdict[str, str],
          flags: set[str], trainers: set[str], items: set[str]) -> list[str]:
    errors: list[str] = []
    ids = {m["id"] for m in maps.values()}

    def check_ref(kind: str, label: str, where: str) -> None:
        if not label or label in ("0x0", "0"):
            return
        if label.startswith("0x"):
            return
        if label not in labels:
            errors.append(f"{where}: {kind} '{label}' is not defined in data/**/*.inc")

    for counter, obj in enumerate(data.get("object_events") or [], start=1):
        where = f"object {counter} at ({obj.get('x')},{obj.get('y')})"
        check_ref("script", obj.get("script", ""), where)
        flag = str(obj.get("flag", "0"))
        if flag.startswith("FLAG_") and flag not in flags:
            errors.append(f"{where}: visibility flag '{flag}' is not defined")
        body = script_text.get(obj.get("script", ""), "")
        for trainer_id in set(TRAINER_RE.findall(body)):
            if trainer_id not in trainers:
                errors.append(f"{where}: trainer '{trainer_id}' is not in a party file")
        for item_id in set(ITEM_RE.findall(body)):
            if item_id not in items:
                errors.append(f"{where}: item '{item_id}' is unknown")
        for flag in set(FLAG_RE.findall(body)):
            if flag not in flags:
                errors.append(f"{where}: flag '{flag}' is unknown")

    for warp_id, warp in enumerate(data.get("warp_events") or []):
        dest = warp.get("dest_map", "")
        if dest == "MAP_DYNAMIC":
            continue
        if dest not in ids:
            errors.append(f"warp {warp_id} at ({warp.get('x')},{warp.get('y')}): unknown map '{dest}'")
            continue
        target = next(m for m in maps.values() if m["id"] == dest)
        target_id = warp.get("dest_warp_id", "0")
        try:
            index = int(str(target_id), 0)
        except ValueError:
            index = 0
        if index >= len(target.get("warp_events") or []):
            errors.append(
                f"warp {warp_id} at ({warp.get('x')},{warp.get('y')}): {dest} has no warp id {target_id} "
                f"({len(target.get('warp_events') or [])} warps)"
            )

    for coord in data.get("coord_events") or []:
        where = f"coord at ({coord.get('x')},{coord.get('y')})"
        check_ref("script", coord.get("script", ""), where)
        var = str(coord.get("var", ""))
        if var and var not in ("0", "VAR_TEMP_1") and var.startswith("VAR_") and var not in VARS:
            errors.append(f"{where}: var '{var}' is unknown")

    for bg in data.get("bg_events") or []:
        where = f"bg event at ({bg.get('x')},{bg.get('y')})"
        if bg.get("type") == "sign":
            check_ref("script", bg.get("script", ""), where)
        if bg.get("type") == "hidden_item" and bg.get("item") not in items:
            errors.append(f"{where}: item '{bg.get('item')}' is unknown")
    return errors


def changed_maps() -> list[str]:
    result = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    names = set()
    for line in result.stdout.splitlines():
        match = re.match(r"data/maps/([^/]+)/", line)
        if match:
            names.add(match.group(1))
    return sorted(names)


VARS: set[str] = set()


def main() -> int:
    global VARS
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--map", action="append", help="map directory name (repeatable)")
    parser.add_argument("--changed", action="store_true", help="only maps changed in the working tree")
    parser.add_argument("--pox", action="store_true", help="only maps in gMapGroup_PlasticOx* groups")
    args = parser.parse_args()

    maps = load_maps()
    labels = all_labels()
    flags = define_set(r"#define\s+(FLAG_[A-Z0-9_]+)", "include/constants/flags.h", "include/constants/flags_frlg.h",
                       "include/constants/plastic_ox_flags.h", "include/constants/plastic_ox_story.h")
    items = define_set(r"#define\s+(ITEM_[A-Z0-9_]+)", "include/constants/items.h")
    items |= define_set(r"^\s*(ITEM_[A-Z0-9_]+)\s*=", "include/constants/items.h")
    trainers = define_set(r"^===\s+(TRAINER_[A-Z0-9_]+)\s*===$", "src/data/trainers.party", "src/data/trainers_frlg.party")
    VARS = define_set(r"#define\s+(VAR_[A-Z0-9_]+)", "include/constants/vars.h")

    script_text: defaultdict[str, str] = defaultdict(str)
    for pattern in ("**/*.inc", "**/*.s"):
        for path in (ROOT / "data").glob(pattern):
            text = path.read_text(encoding="utf-8", errors="replace")
        for label in LABEL_RE.findall(text):
            script_text[label] += "\n" + resolve_local(label, text)

    if args.pox:
        groups = json.loads((ROOT / "data/maps/map_groups.json").read_text(encoding="utf-8"))
        pox = {name for group, members in groups.items() if group.startswith("gMapGroup_PlasticOx") for name in members}
    else:
        pox = set()
    wanted = args.map or (changed_maps() if args.changed else sorted(maps))
    if pox:
        wanted = [name for name in wanted if name in pox]
    if args.map:
        wanted = [name for name in wanted if name in maps]
    if not wanted:
        print("no maps in scope")
        return 0

    total = 0
    for name in wanted:
        errors = check(name, maps[name], maps, labels, script_text, flags, trainers, items)
        if errors:
            print(f"\n{name} ({maps[name].get('id')})")
            for error in errors:
                print(f"  ERROR {error}")
            total += len(errors)
    print(f"\n{len(wanted)} map(s) checked, {total} reference error(s).")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
