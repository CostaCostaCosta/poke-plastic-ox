#!/usr/bin/env python3
"""Alpha wave 2 importer: Legs B+C per REGION_PLAN.

Run from repo root: python3 plastic_ox/agent/import_wave2.py [--dry]
"""
import json, os, shutil, struct, sys

HNS = "/home/eddie/repos/pokehns-expansion"
DRY = "--dry" in sys.argv
FLAG_BASE = 14  # POX_HIDDEN_ITEMS_BASE + N; wave1 used 0..13

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
}
# nearest-vanilla fallbacks for hns archetypes we didn't import (checked below)
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
}

MAPS = [
    "Gate_AzaleaTown_IlexForest_hns", "IlexForest_hns", "Route34_hns",
    "Route2_hns", "Route3_hns", "MtMoon_Cave_hns", "Route4_hns",
    "Route14_hns", "GoldenrodCity_hns", "GoldenrodCity_BillsHouse_hns",
]
MUSIC = {
    "Gate_AzaleaTown_IlexForest_hns": "MUS_RG_VIRIDIAN_FOREST",
    "IlexForest_hns": "MUS_RG_VIRIDIAN_FOREST",
    "Route34_hns": "MUS_RG_ROUTE24",
    "Route2_hns": "MUS_RG_ROUTE3",
    "Route3_hns": "MUS_RG_ROUTE3",
    "MtMoon_Cave_hns": "MUS_RG_MT_MOON",
    "Route4_hns": "MUS_RG_ROUTE3",
    "Route14_hns": "MUS_RG_ROUTE11",
    "GoldenrodCity_hns": "MUS_RG_CELADON",
    "GoldenrodCity_BillsHouse_hns": "MUS_RG_PALLET",
}
GROUP = {
    "Gate_AzaleaTown_IlexForest_hns": "gMapGroup_PlasticOxInteriors",
    "GoldenrodCity_BillsHouse_hns": "gMapGroup_PlasticOxInteriors",
    "IlexForest_hns": "gMapGroup_PlasticOxDungeons",
    "MtMoon_Cave_hns": "gMapGroup_PlasticOxDungeons",
}
DEFAULT_GROUP = "gMapGroup_PlasticOxJohtoKanto"

SEAMS = [
    ("v", "Route34_hns", "IlexForest_hns", 39),       # verbatim hns
    # R34<->R116 is a WARP PAIR (bottom mouth), not a seam: R34's single
    # bottom edge is already claimed by the Ilex connection.
    ("v", "Route2_hns", "RustboroCity", None),        # calc
    ("h", "Route2_hns", "Route3_hns", None),            # calc elbow
    ("h", "Route4_hns", "Route14_hns", None),         # calc elbow (east slot)
    ("v", "Route14_hns", "GoldenrodCity_hns", None),  # calc
]
VERBATIM_CONNS = {
    "Route3_hns": [("MAP_ROUTE4_HNS", "up", 60)],
    "Route4_hns": [("MAP_ROUTE3_HNS", "down", -60)],
    "Route34_hns": [("MAP_GOLDENROD_CITY_HNS", "up", -7)],
    "GoldenrodCity_hns": [("MAP_ROUTE34_HNS", "down", 7)],
}

WARP_RULES = {
    "Gate_AzaleaTown_IlexForest_hns": [
        {"x": 11, "y": 5, "dest_map": "MAP_ROUTE31_HNS", "dest_warp_id": "1"},
        {"x": 1, "y": 5, "dest_map": "MAP_ILEX_FOREST_HNS", "dest_warp_id": "0"},
    ],
    "IlexForest_hns": [
        {"x": 22, "y": 63, "dest_map": "MAP_GATE_AZALEA_TOWN_ILEX_FOREST_HNS", "dest_warp_id": "1"},
    ],
    "Route34_hns": [
        {"x": 23, "y": 89, "elevation": 3, "dest_map": "MAP_ROUTE116", "dest_warp_id": "0"},
    ],
    "Route2_hns": [],
    "Route3_hns": [],  # east door appended programmatically
    "MtMoon_Cave_hns": [
        {"x": 46, "y": 31, "dest_map": "MAP_ROUTE4_HNS", "dest_warp_id": "0"},
        {"x": 4, "y": 12, "dest_map": "MAP_ROUTE3_HNS", "dest_warp_id": "0"},
    ],
    "Route4_hns": [
        {"x": 18, "y": 9, "dest_map": "MAP_MT_MOON_CAVE_HNS", "dest_warp_id": "0"},
    ],
    "Route14_hns": [],
    "GoldenrodCity_hns": [
        {"x": 28, "y": 36, "dest_map": "MAP_POKEMON_CENTER_JOHTO_HNS", "dest_warp_id": "0"},
        {"x": 14, "y": 33, "dest_map": "MAP_GOLDENROD_CITY_BILLS_HOUSE_HNS", "dest_warp_id": "0"},
    ],
    "GoldenrodCity_BillsHouse_hns": [
        {"x": 4, "y": 8, "dest_map": "MAP_DYNAMIC", "dest_warp_id": "WARP_ID_DYNAMIC"},
    ],
}

NPC_LINES = {  # per map: list of (gfx_key_or_None, text) consumed in order by gfx prefix match
}
SIGNS = {}

def npc_lines():
    return {
    "IlexForest_hns": [
        ("BLACK_BELT", "The forest paths loop past each other\nnow. Some mornings I end up in KANTO\nby accident."),
        ("LITTLE_BOY", "A BUG-CATCHER told me the bugs out\nwest count double. I'm going to catch\nso many."),
        ("PICNICKER", "This wood feels older than the map\nsays. The signposts disagree with\neach other."),
        ("FAT_MAN", "I fish where the trees let me. The\nriver doesn't care which region it's\nin."),
        ("BUG_CATCHER", "Something in these woods isn't in any\ndex I've seen. Probably nothing!"),
        ("KURT", "Name's KURT. I make BALLS from\napricorns. Hard to find good ones now\nthe roads go places they shouldn't."),
        ("KIMONO", "We dance for the forest. It has been\nvery patient with all these new\nroads."),
        ("LITTLE_BOY", "Two routes start at the north edge.\nNeither one is on Grandpa's map."),
    ],
    "Gate_AzaleaTown_IlexForest_hns": [
        ("OFFICER", "West goes back to the lake road. East\nis the forest. Past it? Don't ask me\nhow, but that way is HOENN."),
        ("OLD_WOMAN", "In my day this gate went two places,\nnot wherever you felt like walking."),
    ],
    "Route34_hns": [
        ("YOUNGSTER", "Down south the grass turns tropical.\nSame planet, apparently."),
        ("BALDING_MAN", "I train here because the wild POKEMON\nargue about which region they're in."),
        ("CAMPER", "Race you to HOENN! It's that way.\nOr that way. It's always that way."),
        ("YOUNGSTER", "My RATTATA knows a shortcut through\nthe woods that skips three towns."),
        ("COOLTRAINER_F", "They say a GYM town sits past the\nfields east of here. Different badge,\nsame league."),
        ("COOLTRAINER_F", "The DAY-CARE moved twice this year.\nIt's technically in two regions now."),
        ("COOLTRAINER_F", "Keep east for GOLDENROD... or was it\nRUSTBORO? The signs gave up."),
        ("OFFICER", "Traffic doubled overnight. Everyone's\nwalking somewhere impossible."),
        ("PICNICKER", "I nap here. The border runs right\nthrough my blanket."),
        ("OLD_MAN", "This route used to just end. Now it's\nsomebody's shortcut."),
    ],
    "Route2_hns": [
        ("BALDING_MAN", "North! VIRIDIAN's that way. Or a GYM\ntown full of stone. Both fine."),
    ],
    "Route3_hns": [
        ("YOUNGSTER", "Trainers come through the tunnel east\nspeaking UNOVAN. It's a whole thing."),
        ("YOUNGSTER", "MT.MOON's east. There's a cave in it,\nand a region somewhere in that cave."),
        ("FIREBREATHER", "I breathe fire. The geography breathes\nsomething stronger."),
        ("FIREBREATHER", "West is PEWTER. East is a moon. You\ncan't argue with a map like that."),
    ],
    "MtMoon_Cave_hns": [
        ("SILVER", "...This cave wasn't here yesterday.\nDon't slow me down."),
        ("SCIENTIST_M", "Meteorites brought this rock down.\nLately the rock seems to be moving."),
    ],
    "Route4_hns": [
        ("PICNICKER", "CERULEAN's east. BLACKTHORN's... also\nsort of east. Long story."),
        ("ROCKER", "Everything east of here is new since\nlast spring. Even the mountains."),
        ("BLACK_BELT", "Mountains keep showing up where fields\nused to be. Good training though."),
    ],
    "Route14_hns": [
        ("EUSINE", "I chase rumors of rare POKEMON. These\ndays the rumors have no borders."),
        ("JUGGLER", "I juggle three balls. The region\njuggles three maps. Mutual respect."),
        ("BIKER", "My crew rides coast to coast now.\nTook a week to learn the turns."),
        ("BALDING_MAN", "South! GOLDENROD. Bright lights, loud\ntrains, trains to nowhere."),
    ],
    "GoldenrodCity_hns": [
        ("LASS", "GOLDENROD! Everything converges here:\ntrains, radio, and apparently regions."),
        ("HIKER", "I walked here from JOHTO in an hour.\nIt used to take a week."),
        ("ROCKET_F", "We're between operations. Ask later."),
        ("OLD_MAN", "The RADIO TOWER broadcasts to every\nregion now. Feedback loops included."),
        ("BOY_2", "BILL's family lives here! His little\nsister won't stop talking about EEVEE."),
        ("YOUNGSTER", "A gym, a tower, a train... this city\neats small towns like mine."),
        ("BATTLE_GIRL", "The GYM's closed for restructuring.\nEverything's restructuring."),
        ("FAT_MAN", "Came for the DEPT. STORE. Stayed\nbecause the maps stopped making sense."),
    ],
    "GoldenrodCity_BillsHouse_hns": [
        ("WOMAN_3", "Our Bill's away again. Somewhere north\nof everywhere, he said. Men!"),
        ("TWIN", "Grandpa caught an EEVEE once. I want\nseven of my own someday!"),
        ("BILL", "...If you hit dead ends on ROUTE 25,\ncome back and tell nobody."),
    ],
    }

SIGN_TEXTS = {
    "IlexForest_hns": [
        (32, 36, "ILEX FOREST\nThe trees lean away from the new road."),
        (23, 27, "ILEX FOREST\nShrine of the forest guardian."),
    ],
    "Route34_hns": [
        (29, 8, "ROUTE 34\nNorth: ILEX FOREST. South: anywhere."),
        (27, 28, "ROUTE 34\nDAY-CARE: now serving both regions."),
        (33, 65, "ROUTE 34\nGOLDENROD CITY straight ahead."),
        (23, 50, "ROUTE 34\nWatch for trainers crossing regions."),
    ],
    "Route2_hns": [
        (14, 12, "ROUTE 2\nVIRIDIAN FOREST ahead. Probably."),
        (7, 73, "ROUTE 2\nSouth: RUSTBORO CITY. Yes, really."),
    ],
    "GoldenrodCity_hns": [
        (12, 22, "GOLDENROD CITY\nThe city where maps negotiate."),
        (30, 30, "GOLDENROD CITY\nDEPT. STORE: everything but directions."),
        (26, 22, "GOLDENROD CITY\nUNDERGROUND: entrances may vary."),
        (19, 13, "NORTH: GATE TO ROUTE 35\nand points beyond geography."),
        (19, 38, "GOLDENROD CITY\nPCs free for trainers of all regions."),
        (43, 39, "GOLDENROD CITY\nBIKE SHOP: cross-region models."),
        (41, 13, "GOLDENROD GYM\nLeader: WHITNEY. Currently 'thinking'."),
        (45, 12, "GOLDENROD CITY\nFLOWER SHOP: Johto-Hoenn hybrids."),
    ],
    "MtMoon_Cave_hns": [(15, 14, "MT.MOON\nSomewhere inside, the sky is underground.")],
}

# ---------------------------------------------------------------- geometry
HNSEL = {l["id"]: l for l in load(f"{HNS}/data/layouts/layouts.json")["layouts"]}

def edge_runs(layout_id, edge):
    ours = {l["id"]: l for l in load("data/layouts/layouts.json")["layouts"]}.get(layout_id)
    e = ours or HNSEL[layout_id]
    fp = e["blockdata_filepath"]
    repo = "." if ours else HNS
    d = open(f"{repo}/{fp}", "rb").read()
    W, H = e["width"], e["height"]
    vert = edge in ("left", "right")
    n = H if vert else W
    idx = {"top": 0, "left": 0, "bottom": H - 1, "right": W - 1}[edge]
    runs, cur = [], None
    for i in range(n):
        x, y = (idx, i) if vert else (i, idx)
        v = struct.unpack_from("<H", d, 2 * (y * W + x))[0]
        c = (v >> 10) & 3
        if c == 0:
            cur = [i, i] if cur is None else [cur[0], i]
        elif cur:
            runs.append(tuple(cur)); cur = None
    if cur: runs.append(tuple(cur))
    return runs

def ctr(runs):
    r = max(runs, key=lambda t: t[1] - t[0])
    return (r[0] + r[1]) // 2, r

def _edge_fp(layout_id):
    ours = {l["id"]: l for l in load("data/layouts/layouts.json")["layouts"]}.get(layout_id)
    e = ours or HNSEL[layout_id]
    repo = "." if ours else HNS
    return f"{repo}/{e['blockdata_filepath']}", e["width"], e["height"], ours is not None

CARVES = [
    # (layout_id, "h", rows_inclusive, cols) — always a horizontal slice
    ("LAYOUT_ROUTE34_HNS",       "h", (88, 90), range(30, 33)),  # south mouth toward R116
    ("LAYOUT_ROUTE116",          "h", (0, 2),   range(39, 42)),  # widen north door
    ("LAYOUT_ROUTE2_HNS",        "h", (76, 79), range(28, 30)),  # widen east slot
    ("LAYOUT_GOLDENROD_CITY_HNS","h", (0, 7),   range(33, 36)),  # north canyon above gate plaza
]

def apply_carve(lid, kind, fixed, moving):
    """Apply one carve to OUR layout copy (must exist already)."""
    path, W, H, ours = _edge_fp(lid)
    assert ours, f"{lid} must be imported before carving"
    d = bytearray(open(path, "rb").read())
    def blk(x, y):
        return struct.unpack_from("<H", d, 2 * (y * W + x))[0]
    if kind == "h":
        rows = list(range(fixed[0], fixed[1]))
        # source tile: any already-open block in the region, else just inside it
        srctile = None
        for r in rows:
            for c in moving:
                if ((blk(c, r) >> 10) & 3) == 0:
                    srctile = (c, r); break
            if srctile: break
        if srctile is None:
            # spiral outward from the region for any walkable donor tile
            r0, r1 = min(rows), max(rows)
            c0, c1 = min(moving), max(moving)
            for rad in range(1, 6):
                done = False
                for r in range(max(0, r0 - rad), min(H, r1 + rad + 1)):
                    for c in range(max(0, c0 - rad), min(W, c1 + rad + 1)):
                        if r0 <= r <= r1 and c0 <= c <= c1: continue
                        if ((blk(c, r) >> 10) & 3) == 0:
                            srctile = (c, r); done = True; break
                    if done: break
                if done: break
        assert srctile is not None, (lid, "no source")
        sc, sr = srctile
        for r in rows:
            for c in moving:
                struct.pack_into("<H", d, 2 * (r * W + c), blk(sc, sr))
    else:
        col = fixed[0]  # the existing open column
        srctop = None
        for r in range(H):
            if ((blk(col, r) >> 10) & 3) == 0:
                srctop = r; break
        assert srctop is not None
        for r in moving:
            for c in range(fixed[0] - 1, fixed[1]):
                struct.pack_into("<H", d, 2 * (r * W + c), blk(col, srctop))
    if DRY:
        print("WOULD CARVE", lid, kind, fixed, list(moving)[:6])
    else:
        open(path, "wb").write(bytes(d))
        print("carved", lid)

def do_carves():
    """Read-only: compute offsets from HNS data; carves applied per-map post-import."""
    pass

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

def ctr(runs):
    r = max(runs, key=lambda t: t[1] - t[0])
    return (r[0] + r[1]) // 2

# Post-carve edge centers (blockdata scans + CARVES above).
OFFS = {
    ("Route34_hns","Route116"):          23 - 40,
    ("Route2_hns","RustboroCity"):        8 - 5,
    ("Route2_hns","Route3_hns"):         10 - 77,
    ("Route4_hns","Route14_hns"):       -10,
    ("Route14_hns","GoldenrodCity_hns"): 23 - 34,
    ("Route34_hns","IlexForest_hns"):    39,   # verbatim hns
}

def connections_for(name):
    cons = []
    for kind, a, b, _off in SEAMS:
        o = OFFS[(a, b)]
        if kind == "v":
            if name == a:
                cons.append({"map": f"MAP_{b.upper()}", "direction": "down", "offset": o})
            elif name == b:
                cons.append({"map": f"MAP_{a.upper()}", "direction": "up", "offset": -o})
        else:
            if name == a:
                cons.append({"map": f"MAP_{b.upper()}", "direction": "right", "offset": -o})
            elif name == b:
                cons.append({"map": f"MAP_{a.upper()}", "direction": "left", "offset": o})
    cons += [{"map": m, "direction": dd, "offset": oo} for m, dd, oo in VERBATIM_CONNS.get(name, [])]
    return cons

def remap_gfx(g):
    if g in EVENT_OBJECTS:
        return g
    base = g[:-4] if g.endswith("_HNS") else g  # full id, prefix kept
    if base in EVENT_OBJECTS:
        return base
    short = base.replace("OBJ_EVENT_GFX_", "")
    fb = GFX_FALLBACK.get(short, EXTRA_FALLBACK.get(short))
    if fb and fb in EVENT_OBJECTS:
        return fb
    return None

# ---------------------------------------------------------------- import
flag_n = [FLAG_BASE]

def import_map(name):
    dst = f"data/maps/{name}"
    if os.path.isdir(dst): shutil.rmtree(dst)
    shutil.copytree(f"{HNS}/data/maps/{name}", dst)
    d = load(f"{dst}/map.json")
    d.pop("game_version", None)
    d["region"] = "REGION_HOENN"
    if name == "Gate_AzaleaTown_IlexForest_hns":
        d["region_map_section"] = "MAPSEC_ILEX_FOREST"
    d["music"] = MUSIC[name]
    d["connections"] = connections_for(name)
    d["coord_events"] = []

    lines = dict()  # gfx -> queue of texts
    qlist = list(npc_lines().get(name, []))
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
            item = str(o.get("script", "")).split("_")[-1] if o.get("script") else "ITEM_POTION"
            fl = f"FLAG_POX_HIDDEN_{name.split('_hns')[0].upper()}_{len(scripts)+1}"
            o["flag"] = fl
            o["script"] = f"{name.split('_hns')[0]}_EventScript_Item{len(scripts)+1}"
            scripts.append((o["script"], None, "BALL"))
            objs_new.append(o)
            continue
        # consume first queued line whose key matches gfx basekey
        txt = None
        for i, (k, t) in enumerate(qlist):
            if k == basekey or basekey.startswith(k):
                txt = t; qlist.pop(i); break
        lbl = f"{name.split('_hns')[0]}_EventScript_Npc{len(objs_new)+1}"
        o["script"] = lbl; o["flag"] = "0"
        objs_new.append(o)
        if txt is None:
            txt = "Roads keep ending somewhere they\ndidn't used to."
        scripts.append((lbl, txt, "NPC"))
    d["object_events"] = objs_new

    rules = WARP_RULES[name]
    if name == "Route3_hns":
        runs = edge_runs("LAYOUT_ROUTE3_HNS", "right")
        r = max(runs, key=lambda t: t[1]-t[0])
        ydoor = (r[0]+r[1])//2
        rules = rules + [{"x": 83, "y": ydoor, "dest_map": "MAP_MT_MOON_CAVE_HNS", "dest_warp_id": "1"}]
        print("R3 east door at (83,%d)" % ydoor)
    d["warp_events"] = [{"x": r["x"], "y": r["y"], "elevation": 0,
                         "dest_map": r["dest_map"], "dest_warp_id": r["dest_warp_id"]} for r in rules]

    bg_new, sgn = [], []
    hi = flag_n[0]
    for b in d.get("bg_events", []):
        t = b.get("type")
        if t == "sign":
            txt = next((st for sx, sy, st in SIGN_TEXTS.get(name, []) if (sx, sy) == (b.get("x"), b.get("y"))), None)
            if txt is None: continue
            lbl = f"{name.split('_hns')[0]}_EventScript_Sign{len(bg_new)+1}"
            b.pop("label", None); b.pop("height", None)
            b["script"] = lbl
            bg_new.append(b); sgn.append((lbl, txt))
        elif t == "hidden_item":
            b.pop("script", None)
            b["flag"] = f"FLAG_POX_HIDDEN_{name.split('_hns')[0].upper()}_{flag_n[0]}"
            flag_n[0] += 1
            bg_new.append(b)
    d["bg_events"] = bg_new
    save(f"{dst}/map.json", d)
    write_scripts(name, scripts, sgn, [b for b in bg_new if b.get("type") == "hidden_item"])
    return d

def write_scripts(name, scripts, signs, hidden):
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
        e.pop("game_version", None)
        e["layout_version"] = "hns"
        e["include_in_versions"] = ["emerald"]
        e["border_filepath"] = f"data/layouts/{dirbase}/border.bin"
        e["blockdata_filepath"] = f"data/layouts/{dirbase}/map.bin"
        lay["layouts"].append(e)
        save(lp, lay)

def register_group(name):
    grp = GROUP.get(name, DEFAULT_GROUP)
    p = "data/maps/map_groups.json"
    mg = load(p)
    if grp not in mg:
        idx = list(mg.keys()).index("group_order") + 1
        keys = list(mg.keys())
        pos = keys.index("gMapGroup_PlasticOxInteriors") if grp == "gMapGroup_PlasticOxDungeons" else len(keys)
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

def specials():
    # R31 west door -> our gate
    p = "data/maps/Route31_hns/map.json"
    d = load(p); ch = False
    d["warp_events"] = [w for w in d["warp_events"]
                        if w["dest_map"] != "MAP_GATE_AZALEA_TOWN_ILEX_FOREST_HNS"]
    d["warp_events"].append({"x": 10, "y": 9, "elevation": 3,
                             "dest_map": "MAP_GATE_AZALEA_TOWN_ILEX_FOREST_HNS",
                             "dest_warp_id": "0"})
    ch = True
    save(p, d); assert ch
    # native conns
    p = "data/maps/Route116/map.json"; d = load(p)
    if not any(w.get("dest_map") == "MAP_ROUTE34_HNS" for w in d["warp_events"]):
        d["warp_events"].append({"x": 40, "y": 1, "elevation": 3,
                                 "dest_map": "MAP_ROUTE34_HNS", "dest_warp_id": "0"})
        save(p, d)
    adds = [("RustboroCity", {"map": "MAP_ROUTE2_HNS", "direction": "up",
                              "offset": -OFFS[("Route2_hns","RustboroCity")]})]
    for m, conn in adds:
        p = f"data/maps/{m}/map.json"; d = load(p)
        if not any(c["map"] == conn["map"] for c in d["connections"]):
            d["connections"].append(conn); save(p, d)
    # goldenrod mapsec
    p = "src/data/region_map/region_map_sections.json"; d = load(p)
    ids = {s["id"] for s in d["map_sections"]}
    if "MAPSEC_GOLDENROD_CITY" not in ids:
        d["map_sections"].append({"id": "MAPSEC_GOLDENROD_CITY", "name": "GOLDENROD CITY",
                                  "x": 20, "y": 12, "width": 1, "height": 1})
        save(p, d)

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
    block = "\n// Wave 2 (Legs B+C) items/hidden.\n"
    n = FLAG_BASE + 100  # start after wave-1 range headroom within 0x280..0x2BB
    start = POX_MAX + 1
    for i, f in enumerate(new):
        block += f"#define {f:<40} (POX_HIDDEN_ITEMS_BASE + {start + i})\n"
    s = s.replace("#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H",
                  block + "#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H")
    w(p, s)

POX_MAX = 13  # wave-1 used BASE+0..13

CARVE_FOR_MAP = {
    "Route34_hns": [CARVES[0]],
    "GoldenrodCity_hns": [CARVES[3]],
}
# R31: open the wall isolating the west gate-door pocket (wave-1 map)
# hns seals R31's west gate-pocket behind walls its own players never walk;
# put our gate door on the reachable corridor instead.
STANDALONE_CARVES = []

def main():
    specials()
    for name in MAPS:
        print("== importing", name)
        import_map(name)
        copy_layout(name)
        for c in CARVE_FOR_MAP.get(name, []):
            if not DRY:
                apply_carve(*c)
        register_group(name)
        add_script_include(name)
    # standalone layout carves (native maps)
    if not DRY:
        apply_carve(*CARVES[1])
        apply_carve(*CARVES[2])
        for c in STANDALONE_CARVES:
            apply_carve(*c)
    flags_header()
    print("DONE")

if __name__ == "__main__":
    main()
