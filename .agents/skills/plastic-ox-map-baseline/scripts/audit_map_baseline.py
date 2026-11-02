#!/usr/bin/env python3
"""Report automatic coordinate and map-script triggers in map directories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


MAP_SCRIPT_RE = re.compile(r"^\s*map_script\s+(.+)$", re.MULTILINE)


def resolve_map_json(raw_path: str) -> Path:
    path = Path(raw_path)
    return path / "map.json" if path.is_dir() else path


def audit(raw_path: str) -> bool:
    map_json = resolve_map_json(raw_path)
    try:
        data = json.loads(map_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"{map_json}: error: {error}", file=sys.stderr)
        return True

    findings = False
    print(f"{data.get('name', map_json.parent.name)} ({map_json})")
    for event in data.get("coord_events", []):
        findings = True
        print(
            "  coord trigger: "
            f"({event.get('x')}, {event.get('y')}, elevation {event.get('elevation')}) "
            f"var={event.get('var')} value={event.get('var_value')} "
            f"script={event.get('script')}"
        )

    scripts_path = map_json.with_name("scripts.inc")
    if scripts_path.exists():
        scripts = scripts_path.read_text(encoding="utf-8")
        for registration in MAP_SCRIPT_RE.findall(scripts):
            findings = True
            print(f"  map script: {registration.strip()}")

    if not findings:
        print("  baseline: no automatic triggers")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit map JSON/directories for non-baseline automatic triggers."
    )
    parser.add_argument("maps", nargs="+", help="map directories or map.json files")
    args = parser.parse_args()
    findings = [audit(path) for path in args.maps]
    return int(any(findings))


if __name__ == "__main__":
    raise SystemExit(main())
