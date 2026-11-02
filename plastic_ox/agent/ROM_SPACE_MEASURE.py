#!/usr/bin/env python3
"""Re-derive every ROM-space number in plastic_ox/agent/ROM_SPACE_TRIM_AUDIT.md.

READ-ONLY with respect to the build. Reads pokeemerald.gba / .elf and the
generated data/ sources; writes nothing except stdout.

Usage:
    python3 plastic_ox/agent/ROM_SPACE_MEASURE.py [repo_root]
"""

import glob
import json
import os
import re
import subprocess
import sys

SIZE = "arm-none-eabi-size"
NM = "arm-none-eabi-nm"
TOOLCHAIN = "/home/eddie/devkitpro/opt/devkitpro/devkitARM/bin"

# Event macro sizes, from asm/macros/map.inc.
EVENT_SIZES = {
    "object_event": 24,
    "clone_event": 24,
    "warp_def": 8,
    "coord_event": 16,
    "bg_event": 12,
    "connection": 12,
}
MAP_EVENTS_TABLE = 20  # map_events macro
MAP_HEADER = 28        # data/maps/<name>/header.inc, aligned

# Tilesets that look dead to layout reachability but are pinned by a C reference,
# so removing the maps does NOT free them. Verified by grep, not guessed.
#   gTileset_SecretBase / _SecretBaseRedCave -> src/decoration.c:1956,1969,2011,2082,2146
#   gTileset_BattleFrontierOutsideWest/East  -> src/field_door.c:461-464,473-474
CODE_PINNED = {
    "gTileset_SecretBase",
    "gTileset_SecretBaseRedCave",
    "gTileset_BattleFrontierOutsideWest",
    "gTileset_BattleFrontierOutsideEast",
}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def tool(name):
    p = os.path.join(TOOLCHAIN, name)
    return p if os.path.exists(p) else name


def k(n):
    return f"{n} B ({n / 1024:.1f} KB)"


# ---------------------------------------------------------------- baseline


def baseline(root):
    gba = os.path.join(root, "pokeemerald.gba")
    data = open(gba, "rb").read()
    i = len(data) - 1
    while i >= 0 and data[i] == 0xFF:
        i -= 1
    used = i + 1
    print("== 1. ROM baseline ==")
    print(f"  cart size            {len(data):,} B (0x{len(data):X})")
    print(f"  last non-0xFF byte   0x{used:08X} = {used:,} B")
    print(f"  free tail            {k(len(data) - used)} (pure 0xFF padding)")
    for obj in ("maps", "map_events", "event_scripts"):
        o = os.path.join(root, "build/emerald/data", obj + ".o")
        if not os.path.exists(o):
            continue
        for line in run([tool(SIZE), "-A", o]).splitlines():
            f = line.split()
            if len(f) >= 2 and f[0] in (".rodata", "script_data"):
                print(f"  {obj + '.o':<22}{f[0]:<14}{int(f[1]):,} B")
    return len(data) - used


# ---------------------------------------------------------------- symbols


def load_symbols(root):
    syms = {}
    for line in run([tool(NM), "--size-sort", "-S", "--defined-only",
                     os.path.join(root, "pokeemerald.elf")]).splitlines():
        f = line.split()
        if len(f) < 4:
            continue
        try:
            syms[f[3]] = (int(f[0], 16), int(f[1], 16), f[2])
        except ValueError:
            pass
    return syms


def script_region_symbols(syms):
    """Sorted (addr, size, name) for script/text/movement labels, deduped by addr."""
    out, seen = [], set()
    for name, (a, s, t) in syms.items():
        if t not in "DdRr" or a in seen:
            continue
        seen.add(a)
        out.append((a, s, name))
    out.sort()
    return out


# ---------------------------------------------------------------- model


class Model:
    def __init__(self, root, syms):
        self.root = root
        self.syms = syms
        self.scripts = script_region_symbols(syms)

        txt = open(os.path.join(root, "data/layouts/layouts.inc")).read()
        self.layouts = {}
        for m in re.finditer(r"^(\w+)_Layout_Blockdata::\n\t\.incbin \"([^\"]+)\"", txt, re.M):
            self.layouts[m.group(1)] = {"block": m.group(2)}
        for m in re.finditer(
            r"^(\w+)_Layout::\n\t\.4byte (\d+)\n\t\.4byte (\d+)\n"
            r"\t\.4byte (\w+)_Layout_Border\n\t\.4byte (\w+)_Layout_Blockdata\n"
            r"\t\.4byte (gTileset_\w+|0)\n\t\.4byte (gTileset_\w+|0)", txt, re.M):
            n, w, h, _bdr, _bd, p, s = m.groups()
            if n in self.layouts:
                self.layouts[n].update(w=int(w), h=int(h), primary=p, secondary=s)
        for v in self.layouts.values():
            v.setdefault("primary", "0")
            v.setdefault("secondary", "0")
            b = v["block"]
            v["bytes"] = os.path.getsize(b) if os.path.exists(b) else 0

        layouts_json = json.load(
            open(os.path.join(root, "data/layouts/layouts.json")))["layouts"]
        self.id2name = {d["id"]: d["name"] for d in layouts_json}

        mg = json.load(open(os.path.join(root, "data/maps/map_groups.json")))
        self.maps = [m for g in mg["group_order"] for m in mg[g]]

        self.map_layout = {}
        for m in self.maps:
            p = os.path.join(root, "data/maps", m, "map.json")
            lid = json.load(open(p)).get("layout") if os.path.exists(p) else None
            nm = self.id2name.get(lid) if lid else m
            if nm and nm.endswith("_Layout"):
                nm = nm[: -len("_Layout")]
            self.map_layout[m] = nm if nm in self.layouts else None

        self.events = {}
        for m in self.maps:
            ev = 0
            p = os.path.join(root, "data/maps", m, "events.inc")
            if os.path.exists(p):
                s = open(p).read()
                for k_, v in EVENT_SIZES.items():
                    ev += len(re.findall(r"^\t" + k_ + r" ", s, re.M)) * v
                ev += MAP_EVENTS_TABLE
            conn = 0
            pc = os.path.join(root, "data/maps", m, "connections.inc")
            if os.path.exists(pc):
                conn = len(re.findall(r"^\tconnection ", open(pc).read(), re.M)) * 12
            self.events[m] = {"ev": ev, "conn": conn}

        hdr = open(os.path.join(root, "data/maps/headers.inc")).read()
        self.compiled = set(re.findall(r"data/maps/(\S+)/header\.inc", hdr))

    def tileset_bytes(self, const):
        """tiles + palettes + metatiles + metatile attributes + ANIMS + 24 B struct.

        Anims matter: gTilesetAnims_Unused1_Frame0..3 is 8,192 B of payload with no
        InitTilesetAnim_ callback at all, yet it is linked."""
        if not const.startswith("gTileset_"):
            return 0
        core = const[len("gTileset_"):]
        names = [f"gTilesetTiles_{core}", f"gTilesetPic_{core}", f"gTilesetPalettes_{core}",
                 f"gMetatiles_{core}", f"gMetatileAttributes_{core}", const]
        total = sum(self.syms[n][1] for n in names if n in self.syms)
        anims = [n for n in self.syms
                 if n.startswith(f"gTilesetAnims_{core}_") and self.syms[n][2] in "Rr"]
        return total + sum(self.syms[n][1] for n in anims)

    def live_tilesets(self, maps):
        out = set()
        for m in maps:
            l = self.map_layout.get(m)
            if l and l in self.layouts:
                for t in (self.layouts[l]["primary"], self.layouts[l]["secondary"]):
                    if t != "0":
                        out.add(t)
        return out

    def script_bytes(self, maps):
        """Exact: [label, next symbol) spans for labels belonging to these maps."""
        prefs = set()
        for m in maps:
            prefs.add(m)
            prefs.add(m[:-5] if m.endswith("_Frlg") else m)
        total = 0
        for i, (a, s, name) in enumerate(self.scripts):
            if i + 1 < len(self.scripts) and any(
                    name == p or name.startswith(p + "_") for p in prefs):
                total += self.scripts[i + 1][0] - a
        return total


# ---------------------------------------------------------------- families


def families(maps):
    def has(*subs):
        return [m for m in maps if all(s.lower() in m.lower() for s in subs)]

    return {
        "A FRLG Safari Zone interiors": [m for m in maps
                                         if m.startswith("SafariZone_") and m.endswith("_Frlg")],
        "B FRLG Safari Zone, Fuchsia City": [m for m in maps if "SafariZone" in m
                                             and m.endswith("_Frlg")
                                             and not m.startswith("SafariZone_")],
        "C Hoenn Safari Zone": [m for m in maps if m.startswith("SafariZone_")
                                and not m.endswith("_Frlg")],
        "D Battle Frontier": [m for m in maps if m.startswith("BattleFrontier_")],
        "E Trainer Tower / Hill": [m for m in maps if "TrainerTower" in m],
        "F Artisan Cave": [m for m in maps if m.startswith("ArtisanCave")],
        "G Link facilities": [m for m in maps
                              if m.startswith(("BattleColosseum", "TradeCenter", "UnionRoom"))],
        "H Contest halls / Elite Four": [m for m in maps
                                         if "Contest" in m or m.endswith("_Hall")
                                         or m.startswith("EverGrandeCity_Hall")
                                         or "HallOfFame" in m],
        "I Battle Tents": [m for m in maps if "BattleTent" in m],
        "J Secret Base": [m for m in maps if m.startswith("SecretBase_")],
    }


def report_families(model):
    print("\n== 3. Map-side audit table ==")
    print("| family | maps | compiled | blockdata | map-events | header | script+text |"
          " tileset freed | #tilesets | subtotal |")
    print("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
    base_live = model.live_tilesets(model.maps)
    tot = dict(maps=0, comp=0, blk=0, ev=0, hd=0, sb=0, tb=0)
    cascades = {}
    for name, maps in families(model.maps).items():
        ms = sorted(set(maps))
        rem = set(ms)
        newly = base_live - model.live_tilesets([m for m in model.maps if m not in rem])
        freed = [c for c in newly if c not in CODE_PINNED]
        tb = sum(model.tileset_bytes(c) for c in freed)
        blk, seen = 0, set()
        for m in ms:
            l = model.map_layout.get(m)
            if l and l in model.layouts and l not in seen:
                seen.add(l)
                blk += model.layouts[l]["bytes"]
        ev = sum(model.events[m]["ev"] + model.events[m]["conn"] for m in ms)
        hd = MAP_HEADER * len([m for m in ms if m in model.compiled])
        sb = model.script_bytes(ms)
        sub = blk + ev + hd + sb + tb
        cascades[name] = sorted(newly)
        if newly:
            pinned = [c for c in newly if c in CODE_PINNED]
            if pinned:
                print(f"  ! {name}: code-pinned tilesets (NOT freed): {pinned}")
        for key, val in (("maps", len(ms)), ("comp", hd // MAP_HEADER), ("blk", blk),
                         ("ev", ev), ("hd", hd), ("sb", sb), ("tb", tb)):
            tot[key] += val
        print(f"| {name} | {len(ms)} | {hd // MAP_HEADER} | {blk:,} | {ev:,} | {hd:,} |"
              f" {sb:,} | {tb:,} | {len(freed)} | **{sub:,}** |")
    grand = tot["blk"] + tot["ev"] + tot["hd"] + tot["sb"] + tot["tb"]
    print(f"| **TOTAL** | {tot['maps']} | {tot['comp']} | {tot['blk']:,} | {tot['ev']:,} |"
          f" {tot['hd']:,} | {tot['sb']:,} | {tot['tb']:,} | | **{grand:,}** |")
    print(f"\n  ({grand:,} B = {grand / 1024:.1f} KB map-side only)\n")
    for name, tl in cascades.items():
        print(f"  {name}: newly-dead tilesets {tl}")
    return grand


# ---------------------------------------------------------------- gates


def report_gates(model):
    print("\n== 2. Opt-in vs compiled ==")
    notc = [m for m in model.maps if m not in model.compiled]
    print(f"  opted-in maps           {len(model.maps)}")
    print(f"  compiled map headers    {len(model.compiled)}")
    print(f"  opted-in, NOT compiled  {len(notc)}  (all layout_version=frlg -> NULLed)")
    layouts_json = json.load(
        open(os.path.join(model.root, "data/layouts/layouts.json")))["layouts"]
    print(f"  layouts.json entries    {len(layouts_json)}")
    print(f"  layouts emitted .inc    {len(model.layouts)}")
    print(f"  unique blockdata files  "
          f"{len({v['block'] for v in model.layouts.values()})}")


# ---------------------------------------------------------------- tilesets


def report_unused_layouts(model):
    """Layouts emitted into layouts.inc (hence in gMapLayouts, hence linker-retained)
    but referenced by no compiled map. Free by pruning data/layouts/layouts.json."""
    print("\n== 3.1b Emitted-but-unreferenced layouts ==")
    refd = {model.map_layout[m] for m in model.compiled if model.map_layout.get(m)}
    rows, tot = [], 0
    for name, v in model.layouts.items():
        if name in refd:
            continue
        b = v["block"]
        bd = os.path.getsize(b) if os.path.exists(b) else 0
        br_p = f"data/layouts/{name}/border.bin"
        br = os.path.getsize(br_p) if os.path.exists(br_p) else 0
        rows.append((bd + br, name))
        tot += bd + br
    rows.sort(reverse=True)
    print(f"  emitted {len(model.layouts)}  used {len(refd)}  UNREFERENCED {len(rows)}")
    for t, n in rows[:12]:
        print(f"    {t:7,d}  {n}")
    if len(rows) > 12:
        print(f"    ... and {len(rows) - 12} more")
    print(f"    {tot:7,d}  TOTAL reclaimable by pruning layouts.json")


def report_tilesets(model):
    print("\n== 5. Tilesets ==")
    hdr = open(os.path.join(model.root, "src/data/tilesets/headers.h")).read()
    consts = re.findall(r"^const struct Tileset (gTileset_\w+)", hdr, re.M)
    # headers.h re-declares gTileset_ViridianCity at :839 (FRLG block, not compiled)
    # and :2068 (#if !IS_FRLG, compiled). Only one is live; dedupe so we do not
    # double-count its ROM bytes.
    consts = sorted(set(consts))
    live = model.live_tilesets(model.maps)
    dead = [(model.tileset_bytes(c), c) for c in consts if c not in live]
    dead.sort(reverse=True)
    nonzero = [(b, c) for b, c in dead if b]
    print(f"  declared {len(consts)}  live {len(live)}  dead {len(dead)}"
          f"  ({len(nonzero)} still linked)")
    for b, c in nonzero:
        print(f"    {b:7,d}  {c}")
    print(f"    {sum(b for b, _ in nonzero):7,d}  TOTAL dead tileset bytes")


# ---------------------------------------------------------------- code


FEATURE_OBJECTS = {
    "Battle Frontier": ["battle_frontier", "battle_frontier_pass", "battle_frontier_tent",
                        "frontier_util", "battle_pike", "battle_dome", "battle_factory",
                        "battle_factory_screen", "battle_arena", "battle_palace",
                        "battle_pyramid", "battle_pyramid_bag", "battle_tower",
                        "battle_transition_frontier"],
    "Contests + bard": ["contest", "contest_util", "contest_ai", "contest_link",
                        "contest_effect", "contest_link_util", "contest_painting",
                        "bard_music"],
    "Trainer slides": ["trainer_slide"],
    "Link/union/trade/record": ["union_room", "union_room_chat", "trade", "record_mixing",
                                "battle_records", "recorded_battle", "cable_club", "cable_car",
                                "battle_controller_recorded_player", "link", "mail",
                                "pokemon_storage_system"],
    "Minigames": ["dodrio_berry_picking", "pokemon_jump", "roulette", "slot_machine",
                  "berry_blender", "berry_crush", "berry_tag_screen", "minigame_countdown",
                  "match_call"],
    "Trainer Hill": ["trainer_hill"],
    "Secret Base": ["secret_base"],
    "Safari engine (KEEP)": ["safari_zone", "pokeblock", "plastic_ox_contest"],
}


def report_code(root):
    print("\n== 4. Feature code (text + rodata + data per object) ==")
    for label, names in FEATURE_OBJECTS.items():
        rows, tot = [], 0
        for n in names:
            p = os.path.join(root, "build/emerald/src", n + ".o")
            if not os.path.exists(p):
                continue
            s = 0
            for line in run([tool(SIZE), "-A", p]).splitlines():
                f = line.split()
                if len(f) >= 2 and f[0] in (".text", ".rodata", ".data"):
                    s += int(f[1])
            if s:
                rows.append((s, n))
                tot += s
        rows.sort(reverse=True)
        print(f"  {label}: {tot:,} B ({tot / 1024:.1f} KB)")
        for s, n in rows[:6]:
            print(f"      {s:7,d}  {n}")


# ---------------------------------------------------------------- data


def report_data(syms):
    print("\n== 4b. Feature-exclusive data tables ==")
    groups = {
        "Frontier mon/trainer/slide tables": ("gBattleFrontierMons", "gBattleFrontierTrainers",
                                              "sFrontierTrainerSlides", "sFrontierBrainsMons",
                                              "gFrontierBrainInfo"),
        "Bard templates": ("sBardSoundTemplates_Pokemon",),
        "Trainer slides": ("sTrainerSlides",),
        "Trainer Hill": ("gTrainerHillMons",),
        "Contest opponents": ("gContestOpponents",),
        "Trainer slides": ("sTrainerSlides",),
        "Safari Ball gfx": ("gObjectEventPic_SafariBall", "gItemIcon_SafariBall"),
        "Safari map preview (dead: MPS off)": ("sSafariZoneMapPreviewTiles",
                                                "sSafariZoneMapPreviewTilemap"),
    }
    for label, names in groups.items():
        tot = sum(syms[n][1] for n in names if n in syms)
        print(f"  {label:36s} {tot:8,d} B  {[n for n in names if n in syms]}")


# ---------------------------------------------------------------- main


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                           else "/home/eddie/repos/poke-plastic-ox")
    os.chdir(root)
    free = baseline(root)
    syms = load_symbols(root)
    model = Model(root, syms)
    report_gates(model)
    grand = report_families(model)
    report_unused_layouts(model)
    report_tilesets(model)
    report_code(root)
    report_data(syms)
    print(f"\n== Summary ==")
    print(f"  free tail now                     {free:,} B ({free / 1024 / 1024:.2f} MB)")
    print(f"  map-side trim, all 10 families   {grand:,} B ({grand / 1024:.1f} KB)")
    print("  + feature code/data cuts (ROM_SPACE_TRIM_AUDIT.md section 4)")


if __name__ == "__main__":
    main()
