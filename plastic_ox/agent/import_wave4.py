#!/usr/bin/env python3
"""Alpha wave 4 importer: Legs F+G per REGION_PLAN.

Imports Route7_hns, LavenderTown_hns, Route12_hns, Route21_hns,
CinnabarIsland_hns; wires the Kanto east chain seams; retargets town
interiors to the native FRLG set; adds portal pairs where hns geometry
seals seams (R24->R7, R36->R37 deterministic corridor crossing).

Idempotent like import_wave5.py. Run, then:
  python3 plastic_ox/agent/import_tilesets_auto.py
  python3 plastic_ox/agent/remap_metatile_behaviors.py
  pad new *_hns metatile_attributes.bin to 2048 B (zeros)
  python3 plastic_ox/agent/fix_door_behaviors.py
"""
import json, os, shutil, struct, sys

HNS = "/home/eddie/repos/pokehns-expansion"
DRY = "--dry" in sys.argv
FLAG_BASE = 14

def w(path, s):
    if DRY:
        print("WOULD WRITE", path, len(s)); return
    open(path, "w").write(s)

def load(p): return json.load(open(p))
def save(p, d):
    if DRY: print("WOULD WRITE", p); return
    with open(p, "w") as f:
        json.dump(d, f, indent=2); f.write("\n")

import re as _re
EVENT_OBJECTS = set(_re.findall(r"OBJ_EVENT_GFX_[A-Z0-9_]+", open("include/constants/event_objects.h").read()))

GFX_FALLBACK = {
    "BILL": "OBJ_EVENT_GFX_MAN_3",
    "WOMAN_3": "OBJ_EVENT_GFX_WOMAN_2",
    "TWIN": "OBJ_EVENT_GFX_GIRL_3",
    "LITTLE_BOY": "OBJ_EVENT_GFX_BOY_2",
    "EUSINE": "OBJ_EVENT_GFX_GENTLEMAN_FRLG",
    "KURT": "OBJ_EVENT_GFX_OLD_MAN",
    "FOSSIL": None,
    "SMALL_LIGHT": None,
    "GAMEBOY_KID": "OBJ_EVENT_GFX_BOY_2",  # park pair-crash object; use plain NPC
}
EXTRA_FALLBACK = {
    "BALDING_MAN": "OBJ_EVENT_GFX_MAN_3",
    "BLACK_BELT": "OBJ_EVENT_GFX_BLACK_BELT",
    "OFFICER": "OBJ_EVENT_GFX_POLICEMAN",
    "CAMPER": "OBJ_EVENT_GFX_CAMPER",
    "COOLTRAINER_F": "OBJ_EVENT_GFX_COOLTRAINER_F",
    "PICNICKER": "OBJ_EVENT_GFX_PICNICKER",
    "OLD_WOMAN": "OBJ_EVENT_GFX_OLD_WOMAN",
    "FIREBREATHER": "OBJ_EVENT_GFX_HIKER",
    "SCIENTIST_M": "OBJ_EVENT_GFX_SCIENTIST",
    "HIKER": "OBJ_EVENT_GFX_HIKER",
    "BIKER": "OBJ_EVENT_GFX_BIKER",
    "JUGGLER": "OBJ_EVENT_GFX_JUGGLER",
    "BATTLE_GIRL": "OBJ_EVENT_GFX_CYCLING_TRIATHLETE_F",
    "ROCKER": "OBJ_EVENT_GFX_ROCKER",
    "ROCKET_M": "OBJ_EVENT_GFX_ROCKET_GRUNT_M",
    "ROCKET_F": "OBJ_EVENT_GFX_ROCKET_GRUNT_F",
    "POKE_BALL": "OBJ_EVENT_GFX_ITEM_BALL",
    "CHANNELER": "OBJ_EVENT_GFX_HEX_MANIAC",
}

MAPS = [
    "Route7_hns", "LavenderTown_hns", "Route12_hns",
    "Route21_hns", "CinnabarIsland_hns",
]
MUSIC = {
    "Route7_hns": "MUS_RG_ROUTE3",
    "LavenderTown_hns": "MUS_RG_LAVENDER",
    "Route12_hns": "MUS_RG_ROUTE24",
    "Route21_hns": "MUS_RG_ROUTE24",
    "CinnabarIsland_hns": "MUS_RG_CINNABAR",
}
GROUP = {}
DEFAULT_GROUP = "gMapGroup_PlasticOxJohtoKanto"

# Explicit seam declarations (engine semantics: dest = src - offset).
# Offsets from edge-run center alignment (see notes in REGION_PLAN Leg F/G).
EXPLICIT_CONNS = {
    # R7<->Lavender west seam: R7's east edge is walled at the aligned rows
    # (portal pair covers the crossing). R21<->Cinnabar: offset puts the
    # crossing on walled tiles and the water is surf-gated anyway (portal).
    # Lavender<->R12 seam: elevation-severed from the town center (portal
    # covers it). R12<->R21 seam kept for post-surf play.
    "Route12_hns": [
        {"map": "MAP_ROUTE21_HNS", "direction": "down", "offset": 9},
    ],
    "Route21_hns": [
        {"map": "MAP_ROUTE12_HNS", "direction": "up", "offset": -9},
    ],
}

# hns warp dest -> our constant. Unknown dests are DROPPED (no interior).
WARP_RETARGET = {
    "MAP_LAVENDER_TOWN_MART_HNS": "MAP_LAVENDER_TOWN_MART",
    "MAP_LAVENDER_TOWN_POKEMON_CENTER_HNS": "MAP_LAVENDER_TOWN_POKEMON_CENTER_1F",
    "MAP_LAVENDER_TOWN_HOUSE1_HNS": "MAP_LAVENDER_TOWN_HOUSE1",
    "MAP_LAVENDER_TOWN_HOUSE2_HNS": "MAP_LAVENDER_TOWN_HOUSE2",
    "MAP_CINNABAR_ISLAND_POKEMON_CENTER_HNS": "MAP_CINNABAR_ISLAND_POKEMON_CENTER_1F",
}

# Extra warps on free door tiles (verified against imported layouts before use).
WARP_RULES = {m: [] for m in MAPS}
# NOTE: Tower/Gym interior warps deferred — the interiors currently load to a
# black screen (native FRLG interior load issue; see HANDOFF_WAVE4 addendum).
WARP_RULES["LavenderTown_hns"] = []
WARP_RULES["CinnabarIsland_hns"] = []

# Portal pairs appended AFTER import. Existing imported maps are patched in
# place (idempotent). (map, x, y, dest_map, dest_x, dest_y)
PORTALS = [
    # R24<->R7: R7's south edge is walled in hns (tiles verified open).
    ("Route24_hns", 10, 1, "MAP_ROUTE7_HNS", 4, 25),
    ("Route7_hns", 2, 25, "MAP_ROUTE24_HNS", 10, 3),
    # R7<->Lavender: portal (R7 east edge walled at the seam rows).
    ("Route7_hns", 4, 22, "MAP_LAVENDER_TOWN_HNS", 1, 10),
    ("LavenderTown_hns", 1, 12, "MAP_ROUTE7_HNS", 4, 23),
    # Lavender -> Cinnabar: R12/R21 water legs are surf-gated (Leg H style
    # deferral; the seams stay wired for post-surf play) so the demo crosses
    # directly.
    ("LavenderTown_hns", 15, 20, "MAP_CINNABAR_ISLAND_HNS", 8, 6),
    ("CinnabarIsland_hns", 8, 8, "MAP_LAVENDER_TOWN_HNS", 15, 22),
    # Kanto gate: the corridor (Leg D/E) reaches Ecruteak; this portal is the
    # Leg F entry into Kanto east (documented substitution in REGION_PLAN).
    ("EcruteakCity_hns", 15, 31, "MAP_ROUTE7_HNS", 4, 25),
    ("Route7_hns", 5, 25, "MAP_ECRUTEAK_CITY_HNS", 15, 31),
    # Deterministic R36->R37 corridor crossing: the north seam lands in a
    # sealed R37 pocket depending on wander; the row-0 tiles near cols 24-40
    # are blocked at runtime by the connection fill. Portal pair (on tiles
    # verified walkable live) makes the corridor deterministic.
    ("Route36_hns", 19, 19, "MAP_ROUTE37_HNS", 12, 39),
    ("Route37_hns", 18, 39, "MAP_ROUTE36_HNS", 16, 20),
    # R37 -> Ecruteak: the north seam crossing tiles are walled from the
    # reachable region; portal lands inside the town proper.
    ("Route37_hns", 16, 39, "MAP_ECRUTEAK_CITY_HNS", 15, 33),
    ("EcruteakCity_hns", 14, 33, "MAP_ROUTE37_HNS", 18, 39),
]

NPC_LINES = {}
SIGNS = {}

def npc_lines():
    return {}

def sign_texts():
    return {}

# ---------------------------------------------------------------- geometry
HNSEL = {l["id"]: l for l in load(f"{HNS}/data/layouts/layouts.json")["layouts"]}

def _edge_fp(layout_id):
    ours = {l["id"]: l for l in load("data/layouts/layouts.json")["layouts"]}.get(layout_id)
    e = ours or HNSEL[layout_id]
    repo = "." if ours else HNS
    return f"{repo}/{e['blockdata_filepath']}", e["width"], e["height"], ours is not None

def edge_runs(layout_id, edge):
    path, W, H, _ = _edge_fp(layout_id)
    d = open(path, "rb").read()
    vert = edge in ("left", "right")
    n = H if vert else W
    idx = {"top": 0, "left": 0, "bottom": H - 1, "right": W - 1}[edge]
    runs, cur = [], None
    for i in range(n):
        x, y = (idx, i) if vert else (i, idx)
        v = struct.unpack_from("<H", d, 2 * (y * W + x))[0]
        if ((v >> 10) & 3) == 0:
            cur = [i, i] if cur is None else [cur[0], i]
        elif cur:
            runs.append(tuple(cur)); cur = None
    if cur: runs.append(tuple(cur))
    return runs

def remap_gfx(g):
    if g in EVENT_OBJECTS:
        return g
    base = g[:-4] if g.endswith("_HNS") else g
    if base in EVENT_OBJECTS:
        return base
    short = base.replace("OBJ_EVENT_GFX_", "")
    fb = GFX_FALLBACK.get(short, EXTRA_FALLBACK.get(short))
    if fb and fb in EVENT_OBJECTS:
        return fb
    return None

# ---------------------------------------------------------------- import
flag_n = [FLAG_BASE]

def connections_for(name):
    return list(EXPLICIT_CONNS.get(name, []))

def import_map(name):
    dst = f"data/maps/{name}"
    if os.path.isdir(dst): shutil.rmtree(dst)
    shutil.copytree(f"{HNS}/data/maps/{name}", dst)
    d = load(f"{dst}/map.json")
    d.pop("game_version", None)
    d["region"] = "REGION_HOENN"
    d["music"] = MUSIC[name]
    d["connections"] = connections_for(name)
    d["coord_events"] = []

    objs_new, scripts = [], []
    for o in d["object_events"]:
        g = o["graphics_id"]
        berry = str(o.get("trainer_sight_or_berry_tree_id", "")).startswith("BERRY_TREE")
        if g.startswith("OBJ_EVENT_GFX_MON_BASE") or berry: continue
        ng = remap_gfx(g)
        if ng is None:
            print("  drop obj", g, o["x"], o["y"]); continue
        o["graphics_id"] = ng
        mt = o["movement_type"]
        if "WANDER" in mt: o["movement_type"] = "MOVEMENT_TYPE_FACE_DOWN"
        basekey = ng.replace("OBJ_EVENT_GFX_", "")
        if basekey in ("ITEM_BALL",):
            fl = f"FLAG_POX_HIDDEN_{name.split('_hns')[0].upper()}_{len(scripts)+1}"
            o["flag"] = fl
            o["script"] = f"{name.split('_hns')[0]}_EventScript_Item{len(scripts)+1}"
            scripts.append((o["script"], None, "BALL"))
            objs_new.append(o)
            continue
        lbl = f"{name.split('_hns')[0]}_EventScript_Npc{len(objs_new)+1}"
        o["script"] = lbl; o["flag"] = "0"
        objs_new.append(o)
        txt = "Roads keep ending somewhere they\ndidn't used to."
        scripts.append((lbl, txt, "NPC"))
    d["object_events"] = objs_new

    # warps: retarget known interiors, drop unknown hns dests
    warps_new = []
    for wr in d.get("warp_events", []):
        dest = WARP_RETARGET.get(wr["dest_map"])
        if dest is None:
            print("  drop warp", wr["x"], wr["y"], wr["dest_map"]); continue
        warps_new.append({"x": wr["x"], "y": wr["y"], "elevation": 3,
                          "dest_map": dest, "dest_warp_id": wr.get("dest_warp_id", "0")})
    warps_new += [{"x": r["x"], "y": r["y"], "elevation": r.get("elevation", 3),
                   "dest_map": r["dest_map"], "dest_warp_id": r["dest_warp_id"]}
                  for r in WARP_RULES[name]]
    d["warp_events"] = warps_new

    bg_new, sgn = [], []
    for b in d.get("bg_events", []):
        t = b.get("type")
        if t == "sign":
            lbl = f"{name.split('_hns')[0]}_EventScript_Sign{len(bg_new)+1}"
            b.pop("label", None); b.pop("height", None)
            b["script"] = lbl
            bg_new.append(b); sgn.append((lbl, "A sign from the old routes."))
        elif t == "hidden_item":
            b.pop("script", None)
            b["flag"] = f"FLAG_POX_HIDDEN_{name.split('_hns')[0].upper()}_{flag_n[0]}"
            flag_n[0] += 1
            bg_new.append(b)
    d["bg_events"] = bg_new
    save(f"{dst}/map.json", d)
    write_scripts(name, scripts, sgn)
    return d

def write_scripts(name, scripts, signs):
    out = [f"{name}_MapScripts::\n\t.byte 0\n"]
    for lbl, txt, kind in scripts:
        if kind == "NPC":
            out.append(f"{lbl}::\n\tlock\n\tfaceplayer\n\tmsgbox {lbl}_Text, MSGBOX_NPC\n\trelease\n\tend\n")
        else:
            out.append(f"{lbl}::\n\tfinditem ITEM_POKE_BALL\n\tend\n")
    for lbl, txt in signs:
        out.append(f"{lbl}::\n\tmsgbox {lbl}_Text, MSGBOX_SIGN\n\tend\n")
    for lbl, txt, kind in scripts:
        if kind != "NPC": continue
        esc = txt.replace("\n", "\\n")
        out.append(f"{lbl}_Text:\n\t.string \"{esc}$\"\n")
    for lbl, txt in signs:
        esc = txt.replace("\n", "\\n")
        out.append(f"{lbl}_Text:\n\t.string \"{esc}$\"\n")
    w(f"data/maps/{name}/scripts.inc", "\n".join(out) + "\n")

def copy_layout(name):
    lid = load(f"data/maps/{name}/map.json")["layout"]
    he = HNSEL[lid]
    dirbase = os.path.basename(os.path.dirname(he["blockdata_filepath"]))
    dst_dir = f"data/layouts/{dirbase}"
    if os.path.isdir(dst_dir): shutil.rmtree(dst_dir)
    shutil.copytree(f"{HNS}/data/layouts/{dirbase}", dst_dir)
    lp = "data/layouts/layouts.json"
    lay = load(lp)
    if not any(l["id"] == lid for l in lay["layouts"]):
        e = dict(he)
        e.pop("game_version", None); e.pop("layout_version", None)
        e["border_filepath"] = f"data/layouts/{dirbase}/border.bin"
        e["blockdata_filepath"] = f"data/layouts/{dirbase}/map.bin"
        lay["layouts"].append(e)
        save(lp, lay)

def register_group(name):
    grp = GROUP.get(name, DEFAULT_GROUP)
    p = "data/maps/map_groups.json"
    mg = load(p)
    if grp not in mg:
        mg[grp] = []
    cur = mg.get(grp, [])
    if name not in cur:
        cur.append(name)  # append-only: existing map nums must stay stable
    mg[grp] = cur
    if grp not in mg["group_order"]:
        mg["group_order"].append(grp)
    save(p, mg)

def add_script_include(name):
    p = "data/event_scripts.s"
    s = open(p).read()
    line = f"\t.include \"data/maps/{name}/scripts.inc\"\n"
    if line not in s:
        anchor = "\t.include \"data/maps/GoldenrodCity_hns/scripts.inc\"\n"
        prev = [f"\t.include \"data/maps/{m}/scripts.inc\"\n" for m in MAPS]
        inserted = False
        for a in prev:
            if a in s:
                s = s.replace(a, a + line, 1); inserted = True; break
        if not inserted:
            s = s.rstrip() + "\n" + line
        w(p, s)

def apply_portals():
    """Append portal coord events + warp scripts (idempotent per label)."""
    for (m, x, y, dest, dx, dy) in PORTALS:
        p = f"data/maps/{m}/map.json"
        d = load(p)
        lbl = f"{m.split('_hns')[0]}_EventScript_PoxPortal{len(PORTALS)}_{x}_{y}"
        d.setdefault("coord_events", [])
        if any(e.get("script") == lbl for e in d["coord_events"]):
            continue
        d["coord_events"].append({"type": "trigger", "x": x, "y": y, "elevation": 0,
                                  "var": "VAR_POX_PORTAL_GATE", "var_value": "0",
                                  "script": lbl})
        save(p, d)
        sp = f"data/maps/{m}/scripts.inc"
        s = open(sp).read()
        if f"{lbl}::" not in s:
            s += f"\n{lbl}::\n\twarp {dest}, {dx}, {dy}\n\twaitstate\n\tend\n"
            w(sp, s)
        print("portal", m, (x, y), "->", dest, (dx, dy))

def flags_header():
    p = "include/constants/plastic_ox_flags.h"
    s = open(p).read()
    import glob, re
    used = set()
    for mf in glob.glob("data/maps/*_hns/map.json"):
        used |= set(re.findall(r"FLAG_POX_HIDDEN_[A-Z0-9_]+", open(mf).read()))
    have = set(re.findall(r"#define (FLAG_POX_HIDDEN_[A-Z0-9_]+)", s))
    new = sorted(used - have)
    if not new: return
    block = "\n// Wave 4 (Legs F+G) items/hidden.\n"
    start = 200
    for i, f in enumerate(new):
        block += f"#define {f:<40} (POX_HIDDEN_ITEMS_BASE + {start + i})\n"
    s = s.replace("#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H",
                  block + "#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H")
    w(p, s)

def main():
    for name in MAPS:
        print("== importing", name)
        import_map(name)
        copy_layout(name)
        register_group(name)
        add_script_include(name)
    apply_portals()
    flags_header()
    print("DONE")

if __name__ == "__main__":
    main()
