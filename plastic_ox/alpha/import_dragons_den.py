#!/usr/bin/env python3
"""Import the HNS Dragon's Den as the post-game home of RAYQUAZA.

The Den is entered from the cave door on the north shore of Blackthorn's lake
(BlackthornCity_hns (26,12), reached by Surf). An elder stands in the doorway
until the player has entered the Hall of Fame (FLAG_SYS_GAME_CLEAR).

What this copies from the donor (POX_HNS_DONOR or --donor):
  * the Entrance and Cavern layouts (blockdata, border, layouts.json entries,
    HNS partitioning); their tilesets are already in the tree;
  * map.json for both rooms, reduced to Plastic Ox policy: donor trainers,
    story actors, MON_BASE decorations, whirlpools, triggers and hidden items
    are dropped; the shrine interior is not imported, so its warp is removed.

What it authors on top:
  * RAYQUAZA on the shrine plaza, the three plaza triggers that start its
    arrival scene, the three donor item balls on Plastic Ox flags, statue signs;
  * the Den's own wild tables (Lv.50-60 dragons; the donor's are Lv.10-40);
  * the Blackthorn door warp and the elder who blocks it before the post-game.

Scripts (data/maps/<map>/scripts.inc) are authored by hand and never
overwritten. Idempotent: rerunning changes nothing once imported. Run from the
repository root.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# The entrance is the Dragon's Den wiki page / story note; the cavern lives in
# its own group (like the Cerulean Cave rooms) so it is not a page of its own.
GROUP = "gMapGroup_PlasticOxDungeons"
INNER_GROUP = "gMapGroup_DragonsDen"
MAPSEC = "MAPSEC_DRAGONS_DEN"
MUSIC = "MUS_RG_SEVII_CAVE"
ENTRANCE, CAVERN = "DragonsDen_Entrance_hns", "DragonsDen_Cavern_hns"
MAPS = [ENTRANCE, CAVERN]
BLACKTHORN = "BlackthornCity_hns"
DEN_DOOR = (26, 12)  # donor BlackthornCity_hns warp 1


def obj(gfx, x, y, script, flag="0", movement="MOVEMENT_TYPE_FACE_DOWN", elevation=3, local_id=None):
    o = {}
    if local_id:
        o["local_id"] = local_id
    o.update(graphics_id=gfx, x=x, y=y, elevation=elevation, movement_type=movement,
             movement_range_x=0, movement_range_y=0, trainer_type="TRAINER_TYPE_NONE",
             trainer_sight_or_berry_tree_id="0", script=script, flag=flag)
    return o


CAVERN_OBJECTS = [
    # Hidden by FLAG_TEMP_1, which the map's ON_TRANSITION sets until the
    # arrival scene has played and again once RAYQUAZA is caught.
    obj("OBJ_EVENT_GFX_RAYQUAZA", 31, 40, "PoxDragonsDen_Rayquaza", "FLAG_TEMP_1",
        local_id="LOCALID_DRAGONS_DEN_RAYQUAZA"),
    obj("OBJ_EVENT_GFX_ITEM_BALL", 54, 50, "PoxDragonsDen_ItemPPMax", "FLAG_POX_HIDE_DRAGONS_DEN_PP_MAX"),
    obj("OBJ_EVENT_GFX_ITEM_BALL", 7, 35, "PoxDragonsDen_ItemMaxPotion", "FLAG_POX_HIDE_DRAGONS_DEN_MAX_POTION"),
    obj("OBJ_EVENT_GFX_ITEM_BALL", 54, 28, "PoxDragonsDen_ItemDragonFang", "FLAG_POX_HIDE_DRAGONS_DEN_DRAGON_FANG"),
]
# Stepping off the dock onto the shrine plaza; VAR_TEMP_1 is set on transition
# once the scene has played.
CAVERN_TRIGGERS = [
    {"type": "trigger", "x": x, "y": 36, "elevation": 3, "var": "VAR_TEMP_1", "var_value": "0",
     "script": "PoxDragonsDen_RayquazaArrives"} for x in (30, 31, 32)
]
STATUES = [(27, 46), (35, 46), (35, 36), (27, 36), (29, 4), (33, 4)]
SHRINE_DOOR = (31, 46)
CAVERN_SIGNS = [
    {"type": "sign", "x": x, "y": y, "elevation": 0, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
     "script": "PoxDragonsDen_Statue"} for x, y in STATUES
] + [{"type": "sign", "x": SHRINE_DOOR[0], "y": SHRINE_DOOR[1], "elevation": 0,
      "player_facing_dir": "BG_EVENT_PLAYER_FACING_NORTH", "script": "PoxDragonsDen_ShrineDoor"}]

ELDER = obj("OBJ_EVENT_GFX_OLD_MAN_HNS", DEN_DOOR[0], DEN_DOOR[1] + 1, "BlackthornCity_EventScript_DenElder",
            "FLAG_SYS_GAME_CLEAR", elevation=0, local_id="LOCALID_BLACKTHORN_DEN_ELDER")


def mon(species, lo, hi):
    return {"min_level": lo, "max_level": hi, "species": "SPECIES_" + species}


WATER = [mon("DRAGONAIR", 50, 55), mon("SEADRA", 50, 55), mon("DRATINI", 45, 50),
         mon("GYARADOS", 52, 58), mon("DRAGONAIR", 55, 60)]
FISHING = [mon("MAGIKARP", 20, 25), mon("HORSEA", 20, 25),                      # Old Rod
           mon("DRATINI", 35, 40), mon("HORSEA", 35, 40), mon("MAGIKARP", 35, 40),  # Good Rod
           mon("DRATINI", 45, 50), mon("SEADRA", 50, 55), mon("DRAGONAIR", 50, 55),  # Super Rod
           mon("GYARADOS", 52, 58), mon("DRAGONAIR", 55, 60)]


def load(path: Path):
    return json.loads(path.read_text())


def dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def import_layouts(donor: Path, maps: dict) -> None:
    path = ROOT / "data/layouts/layouts.json"
    layouts = load(path)
    have = {l.get("id") for l in layouts["layouts"]}
    donor_layouts = {l["id"]: l for l in load(donor / "data/layouts/layouts.json")["layouts"] if "id" in l}
    for data in maps.values():
        layout = copy.deepcopy(donor_layouts[data["layout"]])
        layout.pop("game_version", None)
        layout["layout_version"] = "hns"
        layout["include_in_versions"] = ["emerald"]
        for key in ("border_filepath", "blockdata_filepath"):
            dst = ROOT / layout[key]
            if not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(donor / layout[key], dst)
        if layout["id"] not in have:
            layouts["layouts"].append(layout)
    dump(path, layouts)


def convert_map(name: str, data: dict, ids: set, blackthorn_warp: int) -> dict:
    data = copy.deepcopy(data)
    data.pop("game_version", None)
    data["region"] = "REGION_HOENN"
    data["region_map_section"] = MAPSEC
    data["music"] = MUSIC
    data["connections"] = None
    warps = []
    for i, w in enumerate(data.get("warp_events", [])):
        if w["dest_map"] == "MAP_BLACKTHORN_CITY_HNS":
            w = dict(w, dest_warp_id=str(blackthorn_warp))
        elif w["dest_map"] not in ids:
            # Only the trailing shrine warp leaves the imported set.
            assert i == len(data["warp_events"]) - 1, (name, w)
            continue
        warps.append(w)
    data["warp_events"] = warps
    if name == CAVERN:
        data["object_events"] = copy.deepcopy(CAVERN_OBJECTS)
        data["coord_events"] = copy.deepcopy(CAVERN_TRIGGERS)
        data["bg_events"] = copy.deepcopy(CAVERN_SIGNS)
    else:
        data["object_events"], data["coord_events"], data["bg_events"] = [], [], []
    return data


def patch_blackthorn() -> int:
    """Add the Den door warp and its elder; returns the warp id."""
    path = ROOT / "data/maps" / BLACKTHORN / "map.json"
    data = load(path)
    warps = data["warp_events"]
    found = [i for i, w in enumerate(warps) if w["dest_map"] == "MAP_DRAGONS_DEN_ENTRANCE_HNS"]
    if not found:
        warps.append({"x": DEN_DOOR[0], "y": DEN_DOOR[1], "elevation": 0,
                      "dest_map": "MAP_DRAGONS_DEN_ENTRANCE_HNS", "dest_warp_id": "0"})
        found = [len(warps) - 1]
    if not any(o["script"] == ELDER["script"] for o in data["object_events"]):
        data["object_events"].append(copy.deepcopy(ELDER))
    dump(path, data)
    return found[0]


def import_maps(maps: dict, blackthorn_warp: int) -> None:
    ids = {d["id"] for d in maps.values()}
    for name, data in maps.items():
        out = ROOT / "data/maps" / name
        dump(out / "map.json", convert_map(name, data, ids, blackthorn_warp))
        scripts = out / "scripts.inc"
        if not scripts.exists():
            scripts.write_text(f"{name}_MapScripts::\n\t.byte 0\n")
    event_scripts = ROOT / "data/event_scripts.s"
    text = event_scripts.read_text()
    for name in maps:
        line = f'\t.include "data/maps/{name}/scripts.inc"\n'
        if line not in text:
            last = list(re.finditer(r'^\t\.include "data/maps/\w+/scripts\.inc"\n', text, flags=re.M))[-1]
            text = text[:last.end()] + line + text[last.end():]
    event_scripts.write_text(text)
    path = ROOT / "data/maps/map_groups.json"
    groups = load(path)
    if INNER_GROUP not in groups["group_order"]:
        groups["group_order"].append(INNER_GROUP)
    groups.setdefault(INNER_GROUP, [])
    for name in maps:
        group = GROUP if name == ENTRANCE else INNER_GROUP
        for other in (GROUP, INNER_GROUP):
            if other != group and name in groups[other]:
                groups[other].remove(name)
        if name not in groups[group]:
            groups[group].append(name)
    dump(path, groups)


def import_encounters(maps: dict) -> None:
    path = ROOT / "src/data/wild_encounters.json"
    local = load(path)
    group = next(g for g in local["wild_encounter_groups"] if g["label"] == "gWildMonHeaders")
    group["encounters"] = [e for e in group["encounters"] if not e["base_label"].startswith("gPoxDragonsDen")]
    for suffix in ("Morning", "Day", "Night"):
        group["encounters"].append({
            "map": maps[CAVERN]["id"],
            "base_label": f"gPoxDragonsDenCavern_{suffix}",
            "water_mons": {"encounter_rate": 7, "mons": copy.deepcopy(WATER)},
            "fishing_mons": {"encounter_rate": 30, "mons": copy.deepcopy(FISHING)},
        })
    # league.py re-appends the Victory Road table last on every regeneration;
    # keep it last so the story generator reproduces this file unchanged.
    group["encounters"].sort(key=lambda e: e["base_label"] == "gPoxVictoryRoadOutdoor")
    dump(path, local)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--donor", type=Path, default=Path(os.environ.get(
        "POX_HNS_DONOR", ROOT.parent / "pokehns-expansion")))
    donor = p.parse_args().donor.expanduser().resolve()
    maps = {m: load(donor / "data/maps" / m / "map.json") for m in MAPS}
    import_layouts(donor, maps)
    import_maps(maps, patch_blackthorn())
    import_encounters(maps)
    print(f"imported {len(MAPS)} Dragon's Den rooms from {donor}")


if __name__ == "__main__":
    main()
