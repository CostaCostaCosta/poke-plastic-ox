#!/usr/bin/env python3
"""Assign local trainers on the active pre-Mt. Moon routes.

Dialogue is authored in data/scripts/plastic_ox_route_trainers.inc; this tool
only assigns actors and never regenerates their scripts or team data.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSIGNMENTS = {
    "Route103": ("Route103_EventScript_Daisy", "PoxRouteTrainer_Route103"),
    "Route29_hns": ("Route29_EventScript_Youngster", "PoxRouteTrainer_Route29"),
    "Route46_hns": ("Route46_EventScript_Ted", "PoxRouteTrainer_Route46"),
    "Route1_Frlg": ("Route1_EventScript_Boy", "PoxRouteTrainer_Route1"),
    "Route31_hns": ("Route31_EventScript_Youngster", "PoxRouteTrainer_Route31"),
    "Route104": ("Route104_EventScript_Haley", "PoxRouteTrainer_Route104"),
    "Route24_hns": ("Route24_EventScript_Npc2", "PoxRouteTrainer_Route24"),
    "Route25_hns": ("Route25_EventScript_Npc2", "PoxRouteTrainer_Route25"),
    "Route44_hns": ("PoxRegion_TrailHint", "PoxRouteTrainer_Route44"),
}

for map_name, (old_script, new_script) in ASSIGNMENTS.items():
    path = ROOT / "data/maps" / map_name / "map.json"
    data = json.loads(path.read_text())
    if any(obj['script'] == new_script for obj in data['object_events']):
        continue
    actor = next(obj for obj in data["object_events"] if obj["script"] == old_script)
    actor.update(script=new_script, trainer_type="TRAINER_TYPE_NORMAL",
                 trainer_sight_or_berry_tree_id="3", movement_type="MOVEMENT_TYPE_FACE_DOWN")
    path.write_text(json.dumps(data, indent=2) + "\n")
