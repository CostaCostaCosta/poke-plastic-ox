#!/usr/bin/env python3
"""Coord-event (step trigger) registry for Plastic Ox maps.

Every `coord_events` entry on a map claimed by a story note must be explained
here: either it calls a `PoxRegion_*` crossing (described automatically from
its script), or its script label has an entry in `REGISTRY` saying what it does
for the story or mechanics. Anything else is treated as vestigial and fails
`check_story_notes.py`; the wiki renders the same rows in each location's
"Triggers" section and on `site/triggers.html`.

    python3 plastic_ox/story/triggers.py            # audit, exit 1 on unknown triggers
    python3 plastic_ox/story/triggers.py --list     # every trigger, grouped
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
import story_notes  # noqa: E402

# label -> (category, what it does). Keep these short and player-facing.
REGISTRY: dict[str, tuple[str, str]] = {
    # Story gates and scenes
    "Pox_StarterGate": ("Story gate", "Turns the player back from Pallet's north edge until the starter is chosen (FLAG_POX_STORY_STARTER)."),
    "Route21_South_EventScript_CinnabarSeam": ("Story gate", "Walking south toward Cinnabar is refused until the Mansion is cleared (FLAG_POX_STORY_MANSION)."),
    "Route36_EventScript_RuinsResearcherStep": ("Story gate", "Lanes beside the Ruins of Alph researcher: turned back until the Cinnabar archives are read (FLAG_POX_STORY_MANSION); after that he walks into the gatehouse and the lanes are open."),
    "PoxMoon_EnterFromRoute44": ("Story gate", "Cave mouth into Mt. Moon 1F; turned back without Badge 1."),
    "MtMoon_B2F_EventScript_MiguelTrigger": ("Story scene", "Super Nerd Miguel spots the player and starts the fossil battle (VAR_POX_MTMOON_STATE 0 only)."),
    "Route119_EventScript_PoxEcruteakGate": ("Region crossing", "Route 119's bottom path walks into the Ecruteak east gatehouse."),
    "PoxEcruteak_WestEntrance": ("Region crossing", "Ecruteak's west edge leads into the Route 38 League gatehouse."),
    # Gyms
    "PoxDragonsDen_RayquazaArrives": ("Story scene", "Dragon's Den shrine plaza: the first step off the dock plays RAYQUAZA's arrival (once; FLAG_POX_DEN_RAYQUAZA_ARRIVED)."),
    "BlackthornCity_EventScript_GymDoor": ("Gym", "Door tile warps into Clair's Gym (PlasticOx_ClairGym)."),
    "RustboroCity_Gym_EventScript_EntranceCheck": ("Gym", "Little Cup rules check at the Gym door; illegal moves/items are turned away until Badge 1."),
    "MossdeepCity_Gym_EventScript_RedFloorSwitch": ("Gym puzzle", "Tate & Liza Gym floor switch: rotates the arrow tiles."),
    "MossdeepCity_Gym_EventScript_BlueFloorSwitch": ("Gym puzzle", "Tate & Liza Gym floor switch: rotates the arrow tiles."),
    "MossdeepCity_Gym_EventScript_GreenFloorSwitch": ("Gym puzzle", "Tate & Liza Gym floor switch: rotates the arrow tiles."),
    "MossdeepCity_Gym_EventScript_YellowFloorSwitch": ("Gym puzzle", "Tate & Liza Gym floor switch: rotates the arrow tiles."),
    "MossdeepCity_Gym_EventScript_PurpleFloorSwitch": ("Gym puzzle", "Tate & Liza Gym floor switch: rotates the arrow tiles."),
    "MossdeepCity_Gym_EventScript_WarpToEntrance": ("Gym puzzle", "Teleport pad back to the Gym entrance."),
    # League
    "PoxLeague_Checkpoint": ("League", "Ecruteak-Route 38 gatehouse checkpoint: all eight Badges open the way to Victory Road."),
    "PoxLeague_Return": ("League", "Victory Road's south exit returns to the Ecruteak gatehouse."),
    "PoxLeague_Summit": ("League", "Victory Road's summit opens onto Indigo Plateau with all eight Badges."),
    "PoxLeague_Downhill": ("League", "Indigo Plateau's south steps lead back down to Victory Road."),
    "PoxLeague_Entry": ("League", "Lobby door to the League: confirms, sets the Indigo respawn, resets the run and enters Wallace's room."),
    "PoxLeague_WallaceNext": ("League", "Exit from Wallace's room to Steven's once Wallace is beaten."),
    "PoxLeague_StevenNext": ("League", "Exit from Steven's room to Lance's once Steven is beaten."),
    "PoxLeague_LeagueLanceNext": ("League", "Exit from Lance's room to Blue's once Lance is beaten."),
    "PoxLeague_BlueNext": ("League", "Exit from Blue's room to Bill's room (the final battle) once Blue is beaten."),
    # Dungeon and route mechanics
    "PokemonTower_5F_EventScript_PurifiedZone": ("Mechanic", "Pokemon Tower 5F purified zone: stepping in heals the party."),
    "PokemonTower_5F_EventScript_ExitPurifiedZone": ("Mechanic", "Leaving the 5F purified zone re-arms its heal."),
    "SeafoamIslands_B4F_EventScript_UpwardCurrent": ("Mechanic", "B4F current pushes the player back until it is stopped (VAR_POX_SEAFOAM_STATE)."),
    "Route110_SeasideCyclingRoadNorthEntrance_EventScript_BikeCheck": ("Mechanic", "Cycling Road gatehouse: no entry on foot; sets the cycling-road state."),
    "Route110_SeasideCyclingRoadNorthEntrance_EventScript_ClearCyclingRoad": ("Mechanic", "Leaving the Cycling Road clears its state."),
    "NewMauville_Entrance_EventScript_Door": ("Story gate", "New Mauville's locked door: opens with the NEW MAUVILLE KEY and Badge 6 (Raikou inside)."),
    "Route110_TrickHouseEntrance_EventScript_TrickMasterHiding": ("Mechanic", "Trick House entrance: stepping near the Trick Master's hiding spot starts the hide-and-seek scene."),
    "Route110_SeasideCyclingRoadSouthEntrance_EventScript_BikeCheck": ("Mechanic", "Cycling Road gatehouse: no entry on foot; sets the cycling-road state."),
    "Route110_SeasideCyclingRoadSouthEntrance_EventScript_ClearCyclingRoad": ("Mechanic", "Leaving the Cycling Road clears its state."),
    "NewMauville_Inside_EventScript_BlueButton": ("Puzzle", "New Mauville floor switch: raises the blue barriers and lowers the green ones."),
    "NewMauville_Inside_EventScript_GreenButton": ("Puzzle", "New Mauville floor switch: raises the green barriers and lowers the blue ones."),
    "NewMauville_Inside_EventScript_RedButton": ("Mechanic", "New Mauville red switch: stops the generator (VAR_NEW_MAUVILLE_STATE 2), which lets the Raikou sage battle start."),
}

_LABEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)::?\s*$", re.M)


def script_blocks() -> dict[str, str]:
    blocks: dict[str, str] = {}
    for path in sorted((ROOT / "data").glob("**/*.inc")):
        text = path.read_text(encoding="utf-8", errors="replace")
        found = list(_LABEL.finditer(text))
        for i, m in enumerate(found):
            end = found[i + 1].start() if i + 1 < len(found) else len(text)
            blocks[m.group(1)] = text[m.end():end]
    return blocks


def _resolve(label: str, blocks: dict[str, str], depth: int = 0) -> str:
    if depth > 4 or label not in blocks:
        return ""
    body = blocks[label]
    refs = re.findall(r"\b(?:goto|call)(?:_if_\w+)?\s+(?:[A-Z0-9_]+,\s*)?(?:[A-Z0-9_]+,\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*$", body, re.M)
    return body + "\n" + "\n".join(_resolve(r, blocks, depth + 1) for r in refs if r != label)


def describe(label: str, blocks: dict[str, str]) -> tuple[str, str] | None:
    if label in REGISTRY:
        return REGISTRY[label]
    if label.startswith("PoxRegion_") and label in blocks:
        body = blocks[label]
        dest = re.search(r"_Open::\s*\n\s*warp\s+(MAP_[A-Z0-9_]+)", body + "\n" + "".join(
            blocks.get(k, "") and f"\n{k}::\n{blocks[k]}" for k in (label + "_Open",)))
        dest = dest or re.search(r"warp\s+(MAP_[A-Z0-9_]+)", blocks.get(label + "_Open", "") or body)
        gates = re.findall(r"goto_if_unset\s+(FLAG_(?!POX_TRIGGERS_ENABLED)[A-Z0-9_]+),\s*" + re.escape(label) + "_Closed", body)
        where = dest.group(1) if dest else "?"
        text = f"Crossing to {where}"
        text += f"; closed until {', '.join(gates)}." if gates else "; always open."
        return ("Region crossing", text)
    return None


def _span(points: list[tuple[int, int]]) -> str:
    xs = sorted({x for x, _ in points}); ys = sorted({y for _, y in points})
    def rng(v: list[int]) -> str:
        if len(v) == 1:
            return str(v[0])
        if v == list(range(v[0], v[-1] + 1)):
            return f"{v[0]}–{v[-1]}"
        return ",".join(map(str, v))
    if len(points) == 1:
        return f"({points[0][0]}, {points[0][1]})"
    if len(xs) == 1 or len(ys) == 1:
        return f"({rng(xs)}, {rng(ys)})"
    return " ".join(f"({x}, {y})" for x, y in points)


def map_triggers(map_name: str, blocks: dict[str, str]) -> list[dict]:
    path = ROOT / "data/maps" / map_name / "map.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    groups: dict[tuple, list[tuple[int, int]]] = {}
    for ev in data.get("coord_events") or []:
        if ev.get("type") == "weather":
            key = ("weather", ev.get("weather", ""), "", "")
        else:
            key = ("trigger", ev.get("script", ""), ev.get("var", ""), str(ev.get("var_value", "")))
        groups.setdefault(key, []).append((ev["x"], ev["y"]))
    rows = []
    for (kind, label, var, value), points in groups.items():
        if kind == "weather":
            info = ("Weather", f"Changes weather to {label}.")
        else:
            info = describe(label, blocks)
        rows.append({
            "map": map_name, "kind": kind, "script": label, "var": var, "value": value,
            "tiles": _span(points), "count": len(points),
            "category": info[0] if info else "UNEXPLAINED",
            "purpose": info[1] if info else "",
            "known": info is not None and (kind != "trigger" or label in blocks),
        })
    return rows


def note_triggers(note: story_notes.Note, blocks: dict[str, str]) -> list[dict]:
    return [row for m in note.all_maps for row in map_triggers(m, blocks)]


def audit(notes: list[story_notes.Note] | None = None) -> list[str]:
    notes = notes if notes is not None else story_notes.load_notes()
    blocks = script_blocks()
    problems = []
    for note in notes:
        for row in note_triggers(note, blocks):
            if not row["known"]:
                why = "script label not defined" if row["script"] not in blocks else "not in triggers.REGISTRY"
                problems.append(f"{note.slug}: {row['map']} {row['tiles']} {row['script']} ({why})")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    notes = story_notes.load_notes()
    if args.list:
        blocks = script_blocks()
        for note in notes:
            for row in note_triggers(note, blocks):
                print(f"{note.slug:<30} {row['map']:<34} {row['tiles']:<16} {row['category']:<16} {row['script']}")
    problems = audit(notes)
    for p in problems:
        print("UNEXPLAINED", p)
    if not args.list:
        print(f"{len(problems)} unexplained trigger(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
