#!/usr/bin/env python3
"""Import the HNS Mt. Silver cave interior as the post-game Cerulean Cave.

The cave is entered at its FRLG mouth in Cerulean City (CeruleanCity_Frlg,
warp 7, reached by surfing south from Route 24) once the
player has entered the Hall of Fame (FLAG_SYS_GAME_CLEAR). Inside, the HNS
Mt. Silver interior is kept as-is: waterfall room, item and side rooms,
2F, the snowfield, 3F and the summit, where RED waits with MEWTWO.

What this copies from the donor (POX_HNS_DONOR or --donor):
  * secondary tilesets cave_gray_hns and mt_silver_snow_hns (assets + C
    registrations); run plastic_ox/tools/remap_metatile_behaviors.py after;
  * the layouts (blockdata, border, layouts.json entries, HNS partitioning);
  * map.json for each room, with donor events reduced to Plastic Ox policy:
    MON_BASE decorations, item balls, NPCs, signs and triggers are dropped;
    breakable rocks are kept; warps to rooms that are not imported are
    removed; the waterfall-room exit returns to Cerulean City;
  * the donor wild tables, with UNOWN and WOBBUFFET written into every land
    table (and Morning mirrored from Day, matching the local schema).

Scripts (data/maps/<map>/scripts.inc) for the summit are authored by hand and
are never overwritten here. Idempotent: rerunning changes nothing once
imported. Run from the repository root.
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
# The entry room is the Cerulean Cave wiki page / story note; the inner rooms
# live in their own group (like the FRLG Mt. Moon floors) so they do not each
# become a wiki page of their own.
GROUP = "gMapGroup_PlasticOxDungeons"
INNER_GROUP = "gMapGroup_CeruleanCave"
MAPSEC = "MAPSEC_CERULEAN_CAVE"
CAVE_MUSIC = "MUS_RG_SEVII_CAVE"

MAPS = [
    "MtSilver_1F_WaterfallRoom_hns",
    "MtSilver_1F_ItemRoom_hns",
    "MtSilver_1F_MoltresRoom_hns",
    "MtSilver_MountainSide_hns",
    "MtSilver_2F_hns",
    "MtSilver_Snow_hns",
    "MtSilver_3F_hns",
    "MtSilver_SummitDay_hns",
]
MAP_IDS: set[str] = set()  # filled from the donor map.json ids in main()

# The waterfall room's south exit (warp 0) leads back to Cerulean City's cave mouth.
EXIT_MAP, EXIT = "MtSilver_1F_WaterfallRoom_hns", 0
CAVE_MOUTH = ("MAP_CERULEAN_CITY", "7")

TILESETS = [  # (C symbol suffix, directory)
    ("Cave_Gray_Hns", "cave_gray_hns"),
    ("MtSilverSnow_Hns", "mt_silver_snow_hns"),
]

# Encounter tables: donor base_label for (Day, Night) per imported map.
ENCOUNTERS = {
    "MtSilver_1F_WaterfallRoom_hns": ("gMtSilver_1F_WaterfallRoom_hns_Day", "gMtSilver_1F_WaterfallRoom_hns_Night"),
    "MtSilver_1F_ItemRoom_hns": ("gMtSilver_1F_ItemRoom_hns_Day", "gMtSilver_1F_ItemRoom_hns_Night"),
    "MtSilver_1F_MoltresRoom_hns": ("gMtSilver_1F_MoltresRoom_hns_Day", "gMtSilver_1F_MoltresRoom_hns_Night"),
    "MtSilver_MountainSide_hns": ("gMtSilver_MountainSide_hns_Day", "gMtSilver_MountainSide_hns_Night"),
    "MtSilver_2F_hns": ("gMtSilver_2F_hns_Day", "gMtSilver_2F_hns_Day"),
    "MtSilver_Snow_hns": ("gMtSilver_Snow_hns_Day", "gMtSilver_SnowNight_hns_Day"),
    "MtSilver_3F_hns": ("gMtSilver_3F_hns_Day", "gMtSilver_3F_hns_Day"),
}
# Super Rod slots (5-9) are rewritten to the region-wide approved LC-RU roster
# (plastic_ox/encounter_tables/test_pre_mt_moon_v5_5.py): the donor's Magikarp
# and Poliwag are not allowed on any Plastic Ox Super Rod. Old and Good Rod and
# surfing stay as the donor has them.
SUPER_ROD = ["SPECIES_SEAKING", "SPECIES_POLIWHIRL", "SPECIES_WHISCASH", "SPECIES_AZUMARILL", "SPECIES_POLITOED"]
# Land slots overwritten with the Ruins-of-Alph pair: slot 4 (10%) and slot 6
# (5%) are repeats of earlier slots in every donor table, so no species is lost.
UNOWN_SLOT, WOBBUFFET_SLOT = 4, 6


def load(path: Path):
    return json.loads(path.read_text())


def dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def insert_after(text: str, anchor_regex: str, block: str) -> str:
    """Insert block after the last line matching anchor_regex (once)."""
    if block.strip() in text:
        return text
    matches = list(re.finditer(anchor_regex, text, flags=re.M))
    assert matches, anchor_regex
    end = matches[-1].end()
    return text[:end] + block + text[end:]


def import_tilesets(donor: Path) -> None:
    for sym, d in TILESETS:
        src, dst = donor / "data/tilesets/secondary" / d, ROOT / "data/tilesets/secondary" / d
        if not dst.exists():
            dst.mkdir(parents=True)
            for f in ["tiles.png", "metatiles.bin", "metatile_attributes.bin"]:
                shutil.copyfile(src / f, dst / f)
            (dst / "palettes").mkdir()
            for pal in sorted((src / "palettes").glob("*.pal")):
                shutil.copyfile(pal, dst / "palettes" / pal.name)
        npal = len(list((dst / "palettes").glob("*.pal")))
        tilesets_h = ROOT / "include/tilesets.h"
        tilesets_h.write_text(insert_after(tilesets_h.read_text(), r"^extern const struct Tileset gTileset_\w+_Hns;\n",
                                           f"extern const struct Tileset gTileset_{sym};\n"))
        headers = ROOT / "src/data/tilesets/headers.h"
        headers.write_text(insert_after(headers.read_text(), r"^const struct Tileset gTileset_\w+_Hns =\n\{\n(?:.*\n)*?\};\n", (
            f"\nconst struct Tileset gTileset_{sym} =\n{{\n    .isCompressed = TRUE,\n    .isSecondary = TRUE,\n"
            f"    .tiles = gTilesetTiles_{sym},\n    .palettes = gTilesetPalettes_{sym},\n"
            f"    .metatiles = gMetatiles_{sym},\n    .metatileAttributes = gMetatileAttributes_{sym},\n"
            f"    .callback = NULL,\n}};\n")))
        graphics = ROOT / "src/data/tilesets/graphics.h"
        pals = "".join(f'    INCGFX_U16("data/tilesets/secondary/{d}/palettes/{i:02d}.pal", ".gbapal"),\n' for i in range(npal))
        graphics.write_text(insert_after(graphics.read_text(), r"^const u16 gTilesetPalettes_\w+_Hns\[\]\[16\] =\n\{\n(?:.*\n)*?\};\n", (
            f'\nconst u32 gTilesetTiles_{sym}[] = INCGFX_U32("data/tilesets/secondary/{d}/tiles.png", ".4bpp.fastSmol");\n\n'
            f"const u16 gTilesetPalettes_{sym}[][16] =\n{{\n{pals}}};\n")))
        metatiles = ROOT / "src/data/tilesets/metatiles.h"
        metatiles.write_text(insert_after(metatiles.read_text(), r"^const u16 gMetatileAttributes_\w+_Hns\[\] = .*\n", (
            f'\nconst u16 gMetatiles_{sym}[] = INCBIN_U16("data/tilesets/secondary/{d}/metatiles.bin");\n\n'
            f'const u16 gMetatileAttributes_{sym}[] = INCBIN_U16("data/tilesets/secondary/{d}/metatile_attributes.bin");\n')))


def import_layouts(donor: Path, maps: dict) -> None:
    path = ROOT / "data/layouts/layouts.json"
    layouts = load(path)
    have = {l.get("id") for l in layouts["layouts"]}
    donor_layouts = {l["id"]: l for l in load(donor / "data/layouts/layouts.json")["layouts"] if "id" in l}
    for name, data in maps.items():
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


def convert_map(name: str, data: dict) -> dict:
    data = copy.deepcopy(data)
    data.pop("game_version", None)
    data["region"] = "REGION_HOENN"
    data["region_map_section"] = MAPSEC
    data["music"] = "MUS_NONE" if "Summit" in name else CAVE_MUSIC
    data["connections"] = None if data.get("connections") is None else []
    data["coord_events"] = []
    data["bg_events"] = []
    warps = []
    for i, w in enumerate(data.get("warp_events", [])):
        if name == EXIT_MAP and i == EXIT:
            w = dict(w, dest_map=CAVE_MOUTH[0], dest_warp_id=CAVE_MOUTH[1])
        elif w["dest_map"] not in MAP_IDS:
            # Only trailing warps lead out of the imported set (the Snowswept
            # Cavern exit); dropping them keeps every other warp id stable.
            assert i == len(data["warp_events"]) - 1, (name, w)
            continue
        warps.append(w)
    data["warp_events"] = warps
    objects = []
    for o in data.get("object_events", []):
        if o["graphics_id"] == "OBJ_EVENT_GFX_BREAKABLE_ROCK_HNS":
            objects.append(dict(o, graphics_id="OBJ_EVENT_GFX_BREAKABLE_ROCK", script="EventScript_RockSmash",
                                trainer_type="TRAINER_TYPE_NONE", trainer_sight_or_berry_tree_id="0", flag="0"))
            objects[-1].pop("local_id", None)
    data["object_events"] = objects
    return data


def import_maps(maps: dict) -> None:
    for name, data in maps.items():
        out = ROOT / "data/maps" / name
        if (out / "map.json").exists():
            continue  # authored after import (summit objects, etc.)
        dump(out / "map.json", convert_map(name, data))
        scripts = out / "scripts.inc"
        if not scripts.exists():
            scripts.write_text(f"{name}_MapScripts::\n\t.byte 0\n")
    event_scripts = ROOT / "data/event_scripts.s"
    text = event_scripts.read_text()
    for name in maps:
        line = f'\t.include "data/maps/{name}/scripts.inc"\n'
        if line not in text:
            text = insert_after(text, r'^\t\.include "data/maps/\w+/scripts\.inc"\n', line)
    event_scripts.write_text(text)
    path = ROOT / "data/maps/map_groups.json"
    groups = load(path)
    if INNER_GROUP not in groups["group_order"]:
        groups["group_order"].append(INNER_GROUP)
    groups.setdefault(INNER_GROUP, [])
    for name in maps:
        group = GROUP if name == EXIT_MAP else INNER_GROUP
        for other in (GROUP, INNER_GROUP):
            if other != group and name in groups[other]:
                groups[other].remove(name)
        if name not in groups[group]:
            groups[group].append(name)
    dump(path, groups)


def mon(species, lo, hi):
    return {"min_level": lo, "max_level": hi, "species": species}


def import_encounters(donor: Path, maps: dict) -> None:
    path = ROOT / "src/data/wild_encounters.json"
    local = load(path)
    group = next(g for g in local["wild_encounter_groups"] if g["label"] == "gWildMonHeaders")
    group["encounters"] = [e for e in group["encounters"] if not e["base_label"].startswith("gPoxCeruleanCave")]
    have = set()
    donor_group = next(g for g in load(donor / "src/data/wild_encounters.json")["wild_encounter_groups"]
                       if g["label"] == "gWildMonHeaders")
    by_label = {e["base_label"]: e for e in donor_group["encounters"]}
    for name, (day, night) in ENCOUNTERS.items():
        stem = "gPoxCeruleanCave" + name[len("MtSilver"):-4].replace("_", "")
        for suffix, source in (("Morning", day), ("Day", day), ("Night", night)):
            label = f"{stem}_{suffix}"
            if label in have:
                continue
            entry = copy.deepcopy(by_label[source])
            entry["map"] = maps[name]["id"]
            entry["base_label"] = label
            land = entry["land_mons"]["mons"]
            lo = min(m["min_level"] for m in land if m["min_level"] >= 30)
            hi = max(m["max_level"] for m in land)
            land[UNOWN_SLOT] = mon("SPECIES_UNOWN", lo, hi)
            land[WOBBUFFET_SLOT] = mon("SPECIES_WOBBUFFET", lo, hi)
            fishing = entry.get("fishing_mons", {}).get("mons", [])
            for slot, species in zip(range(5, 10), SUPER_ROD):
                if slot < len(fishing):
                    fishing[slot]["species"] = species
            group["encounters"].append(entry)
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
    MAP_IDS.update(d["id"] for d in maps.values())
    import_tilesets(donor)
    import_layouts(donor, maps)
    import_maps(maps)
    import_encounters(donor, maps)
    print(f"imported {len(MAPS)} Cerulean Cave rooms from {donor}")


if __name__ == "__main__":
    main()
