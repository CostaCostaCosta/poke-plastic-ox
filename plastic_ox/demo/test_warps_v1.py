#!/usr/bin/env python3
"""Exhaustive warp-transition playtest for the Plastic-Ox story region (run 3).

Playtest only: this script never edits game data, maps, scripts, or ROM code.
It boots ``pokeemerald.gba`` in headless mGBA, injects a fully-unlocked
player state, and walks the player through every warp event and every outdoor
map-connection seam in the story-reachable closure, in both directions.

For every warp it records, against the map JSON as the oracle:

* destination map id and landing coordinates,
* arrival facing, compared with the engine's own canonical rule
  (``GetAdjustedInitialDirection`` in ``src/overworld.c``) applied to the
  metatile behaviour of the landing tile,
* whether the landing tile is standable / the door tile,
* whether the player can immediately step away (softlock probe),
* the reverse leg, which must land back on the originating warp tile.

Water
-----
Some warps can only be reached on the surfboard: the Seafoam Islands
whirlpools (``MB_*_CURRENT`` tiles that carry the warp event itself) and the
S.S. Anne's ocean dock sit on water, and some seams are water-to-water.  The
walker therefore mounts Surf for real when the dry run-up does not exist: it
grants a party mon that knows Surf and Waterfall plus ``ITEM_SURF_KEY``
through the engine's own field-script commands (the fixture is a fresh game,
not a battery save), swims to the run-up tile, steps onto the warp from the
board and climbs waterfalls by facing ``MB_WATERFALL`` north.  Rows whose surf
path cannot be built are reported ``UNTESTED`` with the engine's own reason
(``surf path needed but not reachable: ...``) instead of a bare timeout.
``--no-surf`` restores the pure on-foot walk.

Usage
-----
    LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
      /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_warps_v1.py \
      --json /tmp/warps.json --report /tmp/warps.md

    ... --static-only          # no emulator, JSON/map-data pre-pass only
    ... --only Goldenrod       # substring filter on map dir names
    ... --limit 40             # first N warps (smoke runs)
    ... --connections-only
    ... --no-surf              # on-foot only: no Surf/Waterfall expansion
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import struct
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "plastic_ox/alpha"))

# mGBA GBA key bit masks (mgba.gba.GBA.KEY_*).  Duplicated here so the static
# pre-pass can run with a plain system python that has no mGBA bindings.
DIRKEY = {"UP": 0x06, "DOWN": 0x07, "LEFT": 0x05, "RIGHT": 0x04}
K_A, K_B = 0x00, 0x01

SHOTS = ROOT / "plastic_ox/demo/shots/warp_v1"

# ---------------------------------------------------------------------------
# Orientation helpers
# ---------------------------------------------------------------------------
DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
DIR_NAME = {1: "DOWN", 2: "UP", 3: "LEFT", 4: "RIGHT"}

# Transcribed from GetAdjustedInitialDirection() in src/overworld.c.  "KEEP"
# means the engine carries the pre-warp facing across (ladders only).
CANONICAL_FACING = {
    "MB_DEEP_SOUTH_WARP": "UP",
    "MB_NON_ANIMATED_DOOR": "DOWN",
    "MB_WATER_DOOR": "DOWN",
    "MB_PETALBURG_GYM_DOOR": "DOWN",
    "MB_ANIMATED_DOOR": "DOWN",
    "MB_SOUTH_ARROW_WARP": "UP",
    "MB_WATER_SOUTH_ARROW_WARP": "UP",
    "MB_SHOAL_CAVE_ENTRANCE": "UP",
    "MB_NORTH_ARROW_WARP": "DOWN",
    "MB_STAIRS_OUTSIDE_ABANDONED_SHIP": "DOWN",
    "MB_WEST_ARROW_WARP": "RIGHT",
    "MB_EAST_ARROW_WARP": "LEFT",
    "MB_UP_RIGHT_STAIR_WARP": "LEFT",
    "MB_DOWN_RIGHT_STAIR_WARP": "LEFT",
    "MB_UP_LEFT_STAIR_WARP": "RIGHT",
    "MB_DOWN_LEFT_STAIR_WARP": "RIGHT",
    "MB_LADDER": "KEEP",
}
# Behaviours the player is allowed to *stand on* right after a warp even when
# the collision bits are set: these are exactly the tiles the vanilla engine
# spawns the player on top of (doorways, stairs, ladders).
STANDABLE_TRANSITION = {
    "MB_ANIMATED_DOOR", "MB_NON_ANIMATED_DOOR", "MB_WATER_DOOR",
    "MB_PETALBURG_GYM_DOOR", "MB_SOUTH_ARROW_WARP", "MB_NORTH_ARROW_WARP",
    "MB_WEST_ARROW_WARP", "MB_EAST_ARROW_WARP", "MB_LADDER",
    "MB_UP_RIGHT_STAIR_WARP", "MB_UP_LEFT_STAIR_WARP",
    "MB_DOWN_RIGHT_STAIR_WARP", "MB_DOWN_LEFT_STAIR_WARP",
    "MB_SHOAL_CAVE_ENTRANCE", "MB_STAIRS_OUTSIDE_ABANDONED_SHIP",
    "MB_DEEP_SOUTH_WARP", "MB_WATER_SOUTH_ARROW_WARP",
    "MB_ROCK_STAIRS", "MB_SIDEWAYS_STAIRS_RIGHT_SIDE", "MB_SIDEWAYS_STAIRS_LEFT_SIDE",
    "MB_SIDEWAYS_STAIRS_RIGHT_SIDE_TOP", "MB_SIDEWAYS_STAIRS_LEFT_SIDE_TOP",
    "MB_SIDEWAYS_STAIRS_RIGHT_SIDE_BOTTOM", "MB_SIDEWAYS_STAIRS_LEFT_SIDE_BOTTOM",
    "MB_UP_ESCALATOR", "MB_DOWN_ESCALATOR",
    "MB_CRACKED_FLOOR_HOLE", "MB_AQUA_HIDEOUT_WARP", "MB_LAVARIDGE_GYM_1F_WARP",
}
DOORISH = {"MB_ANIMATED_DOOR", "MB_NON_ANIMATED_DOOR", "MB_WATER_DOOR",
           "MB_PETALBURG_GYM_DOOR"}
# Solid behaviours that are still a legal landing (a hole you fall through is
# not; these are the ones the engine explicitly supports landing on).
HOLEISH = {"MB_CRACKED_FLOOR_HOLE", "MB_AQUA_HIDEOUT_WARP", "MB_LAVARIDGE_GYM_1F_WARP"}


# ---------------------------------------------------------------------------
# Surf / Waterfall / whirlpool movement
# ---------------------------------------------------------------------------
# The engine numbers (include/constants/moves.h, field_move.h, items.h and
# global.fieldmap.h):
MOVE_SURF, MOVE_WATERFALL = 57, 127
FIELD_MOVE_SURF, FIELD_MOVE_WATERFALL = 4, 7
ITEM_SURF_KEY = 878
PARTY_SIZE = 6
PLAYER_AVATAR_FLAG_SURFING = 1 << 3
# include/global.fieldmap.h: this port numbers the walkable level 3, not 0.
# The engine offers Surf from ELEVATION_DEFAULT only, and CanStopSurfing
# dismounts onto ELEVATION_DEFAULT only, so both the harness's pre-check and
# its shore search have to use the same number.
ELEVATION_DEFAULT = 3
# Metatile behaviours the engine offers the Surf prompt on, transcribed from
# IsPlayerFacingSurfableFishableWater() (src/field_player_avatar.c).  A tile
# that is merely "water" (MB_SHALLOW_WATER, bridges) never triggers it.
SURFACE_BEHAVIORS = {"MB_POND_WATER", "MB_OCEAN_WATER", "MB_INTERIOR_DEEP_WATER",
                     "MB_DEEP_WATER", "MB_NORTHWARD_CURRENT", "MB_SOUTHWARD_CURRENT"}
# MB_WATERFALL is climbed with the same A press while surfing north, and the
# FRLG whirlpools are MB_*_CURRENT tiles that carry the warp event itself, so
# they are traversed by mounting Surf and stepping onto them.
WATERFALL_BEHAVIORS = {"MB_WATERFALL"}


def is_surface(behavior):
    return behavior in SURFACE_BEHAVIORS


# Metatile behaviours whose warp event the engine actually runs, transcribed
# from IsWarpMetatileBehavior / IsArrowWarpMetatileBehavior /
# IsDirectionalStairWarpMetatileBehavior in src/field_control_avatar.c.  A warp
# event on anything else can never fire, on foot or on the surfboard, so the
# harness says so instead of blaming the walk.
WARP_FIRING_BEHAVIORS = {
    "MB_ANIMATED_DOOR", "MB_NON_ANIMATED_DOOR", "MB_WATER_DOOR",
    "MB_PETALBURG_GYM_DOOR", "MB_LADDER", "MB_UP_ESCALATOR", "MB_DOWN_ESCALATOR",
    "MB_LAVARIDGE_B1F_WARP", "MB_LAVARIDGE_GYM_1F_WARP", "MB_AQUA_HIDEOUT_WARP",
    "MB_MT_PYRE_HOLE", "MB_MOSSDEEP_GYM_WARP", "MB_UNION_ROOM_WARP",
    "MB_NORTH_ARROW_WARP", "MB_SOUTH_ARROW_WARP", "MB_EAST_ARROW_WARP",
    "MB_WEST_ARROW_WARP", "MB_DEEP_SOUTH_WARP", "MB_WATER_SOUTH_ARROW_WARP",
    "MB_UP_RIGHT_STAIR_WARP", "MB_DOWN_RIGHT_STAIR_WARP",
    "MB_UP_LEFT_STAIR_WARP", "MB_DOWN_LEFT_STAIR_WARP",
    "MB_ROCK_STAIRS", "MB_SHOAL_CAVE_ENTRANCE", "MB_STAIRS_OUTSIDE_ABANDONED_SHIP",
}


def warp_metatile_can_fire(behavior):
    return behavior in WARP_FIRING_BEHAVIORS


# ---------------------------------------------------------------------------
# Static catalogue / closure
# ---------------------------------------------------------------------------
def load_catalogue():
    """Return (catalog, by_id, group_ids) for every map directory in the ROM."""
    catalog = {p.parent.name: json.loads(p.read_text())
               for p in (ROOT / "data/maps").glob("*/map.json")}
    by_id = {d["id"]: n for n, d in catalog.items()}
    groups = json.loads((ROOT / "data/maps/map_groups.json").read_text())
    group_ids = {name: (gi, mi)
                 for gi, key in enumerate(groups["group_order"])
                 for mi, name in enumerate(groups[key])}
    layouts = {l["id"]: l for l in
               json.loads((ROOT / "data/layouts/layouts.json").read_text())["layouts"]}
    return catalog, by_id, group_ids, layouts


def seed_maps():
    """Story seeds: region_v7 anchors, story triggers, region transitions."""
    text = (ROOT / "plastic_ox/alpha/region_v7.py").read_text()
    block = text.split("ANCHORS = {", 1)[1].split("\n}", 1)[0]
    seeds = set(re.findall(r"'([^']+)'\s*:\s*\(", block))
    story = json.loads((ROOT / "plastic_ox/alpha/story_manifest.json").read_text())
    seeds |= {e["map"] for e in story["events"]}
    region = json.loads((ROOT / "plastic_ox/alpha/region_manifest.json").read_text())
    for t in region["transitions"]:
        seeds |= {t["source"], t["destination"]}
    # Retained donor rooms kept outside the authored graph (see
    # plastic_ox/agent/audit_warp_connections.py).
    seeds |= {f"SeafoamIslands_{x}_Frlg" for x in ("1F", "B1F", "B2F", "B3F", "B4F")}
    seeds |= {
        "UndergroundPath_EastEntrance_Frlg", "UndergroundPath_WestEntrance_Frlg",
        "UndergroundPath_EastWestTunnel_Frlg", "PokemonMansion_1F_Frlg",
        "MtMoon_1F_Frlg", "MtMoon_B1F_Frlg", "MtMoon_B2F_Frlg",
        "Route2_ViridianForest_NorthEntrance_Frlg",
        "Route2_ViridianForest_SouthEntrance_Frlg", "Route2_House_Frlg",
        "Route2_EastBuilding_Frlg",
    }
    return seeds


def closure():
    catalog, by_id, _, _ = load_catalogue()
    seeds = {m for m in seed_maps() if m in catalog}
    reached, queue = set(seeds), list(seeds)
    while queue:
        name = queue.pop()
        data = catalog[name]
        targets = [w.get("dest_map") for w in data.get("warp_events", [])]
        targets += [c.get("map") for c in (data.get("connections") or [])]
        for target_id in targets:
            target = by_id.get(target_id)
            if target and target not in reached:
                reached.add(target)
                queue.append(target)
    return catalog, by_id, reached


# ---------------------------------------------------------------------------
# Static pre-pass
# ---------------------------------------------------------------------------
_GEOM = {}


def geometry(name, catalog):
    if name not in _GEOM:
        from region_geometry import Geometry
        try:
            _GEOM[name] = Geometry(name, catalog[name])
        except Exception:
            _GEOM[name] = None
    return _GEOM[name]


def static_warp_findings(name, index, warp, catalog, by_id, reached):
    """Static expectations + anomaly flags for one warp event."""
    data = catalog[name]
    out = {
        "map": name, "warp": index,
        "src_xy": [warp.get("x"), warp.get("y")],
        "src_elevation": warp.get("elevation"),
        "dest_map": warp.get("dest_map"),
        "dest_warp_id": warp.get("dest_warp_id"),
        "issues": [],
    }
    geom = geometry(name, catalog)
    if geom is not None:
        try:
            out["src_behavior"] = geom.tile(warp["x"], warp["y"])[2]
        except Exception:
            out["src_behavior"] = None

    dest_id = warp.get("dest_map")
    if dest_id == "MAP_DYNAMIC":
        out["class"] = "dynamic"
        return out
    target = by_id.get(dest_id)
    if target is None:
        out["class"] = "missing_target"
        out["issues"].append("destination map id not in the ROM")
        return out
    if target not in reached:
        out["class"] = "outside_closure"
        out["dest_name"] = target
        return out
    out["class"] = "internal"
    out["dest_name"] = target
    try:
        target_index = int(warp["dest_warp_id"])
    except (KeyError, TypeError, ValueError):
        out["class"] = "bad_index"
        out["issues"].append(f"unparseable dest_warp_id {warp.get('dest_warp_id')!r}")
        return out
    out["dest_warp"] = target_index
    target_warps = catalog[target].get("warp_events", [])
    if not 0 <= target_index < len(target_warps):
        out["class"] = "bad_index"
        out["issues"].append(
            f"dest_warp_id {target_index} out of range (target has {len(target_warps)})")
        return out
    back = target_warps[target_index]
    out["dest_xy"] = [back.get("x"), back.get("y")]
    out["mutual"] = (back.get("dest_map") == data["id"] and
                     str(back.get("dest_warp_id")) == str(index))
    if not out["mutual"]:
        if back.get("dest_map") == data["id"]:
            out["class"] = "landing_anchor"
        elif back.get("dest_map") == "MAP_DYNAMIC":
            # Facility interiors (Pokemon Center / Mart / generic house) exit
            # through gSaveBlock1Ptr->dynamicWarp, which the engine fills with
            # the door the player walked in through.  Not a broken pair.
            out["class"] = "dynamic_return"
        elif returns_within(catalog, by_id, target, target_index, data["id"], index):
            # A chained landing: Route2 -> DarkCave -> DiglettsCave ladders.
            out["class"] = "chained_landing"
        else:
            out["class"] = "nonreciprocal"
            out["issues"].append(
                f"landing warp {target}[{target_index}] points at {back.get('dest_map')}, "
                f"not back to {data['id']}")
    tgeom = geometry(target, catalog)
    if tgeom is not None:
        try:
            lx, ly = back["x"], back["y"]
            if not (0 <= lx < tgeom.w and 0 <= ly < tgeom.h):
                out["issues"].append(f"landing ({lx},{ly}) outside {target} "
                                     f"{tgeom.w}x{tgeom.h}")
            collision, elev, behavior = tgeom.tile(lx, ly)
            out["dest_behavior"] = behavior
            out["dest_elevation"] = elev
            if collision != 0 and behavior not in STANDABLE_TRANSITION:
                out["issues"].append(
                    f"landing ({lx},{ly}) is solid ({behavior}) and not a transition tile")
            # Is there anywhere to step away to?  The engine's only collision
            # test is the block's bits 10-11 (MapGridGetCollisionAt), so a
            # doorway tile counts as walkable even though the metatile looks
            # like a door.
            exits = []
            for d, (dx, dy) in DIRS.items():
                nx, ny = lx + dx, ly + dy
                if not (0 <= nx < tgeom.w and 0 <= ny < tgeom.h):
                    continue
                c2, e2, b2 = tgeom.tile(nx, ny)
                if c2 != 0 or waterish(b2):
                    continue
                if elev not in (0, 15) and e2 not in (0, 15) and e2 != elev:
                    continue
                exits.append(d)
            out["dest_exits"] = exits
            if not exits:
                out["issues"].append(f"landing ({lx},{ly}) has no walkable exit -- softlock")
        except Exception as exc:  # pragma: no cover - defensive
            out["issues"].append(f"landing geometry unreadable: {exc}")
    # Approach availability on the source side.
    if geom is not None:
        approaches = []
        wx, wy = warp["x"], warp["y"]
        try:
            welev = geom.tile(wx, wy)[1]
        except Exception:
            welev = 0
        for d, (dx, dy) in DIRS.items():
            ax, ay = wx - dx, wy - dy
            if not (0 <= ax < geom.w and 0 <= ay < geom.h):
                continue
            c2, e2, b2 = geom.tile(ax, ay)
            if c2 != 0 or waterish(b2):
                continue
            if welev not in (0, 15) and e2 not in (0, 15) and e2 != welev:
                continue
            approaches.append(d)
        out["approaches"] = approaches
        if not approaches:
            out["issues"].append(f"no standable approach to warp ({wx},{wy})")
    return out


def behavior_name(value):
    """Metatile behaviour id -> MB_* name, using the ROM's own ordering."""
    from region_geometry import BEHAVIORS
    if value is None or not (0 <= value < len(BEHAVIORS)):
        return None
    return BEHAVIORS[value]


def waterish(behavior):
    return any(k in behavior for k in ("WATER", "CURRENT", "OCEAN", "POND", "SEAWEED"))


def returns_within(catalog, by_id, map_name, index, want_map, want_index, hops=4):
    """True when following dest links from (map_name,index) lands back on the
    originating warp within `hops` steps (multi-hop ladder/door chains)."""
    seen = {(map_name, index)}
    for _ in range(hops):
        data = catalog[map_name]
        warp = data.get("warp_events", [])[index]
        dest_id = warp.get("dest_map")
        if dest_id == "MAP_DYNAMIC" or dest_id is None:
            return False
        target = by_id.get(dest_id)
        if target is None:
            return False
        try:
            next_index = int(warp["dest_warp_id"])
        except (KeyError, TypeError, ValueError):
            return False
        if (target, next_index) == (want_map, want_index):
            return True
        if (target, next_index) in seen:
            return False
        seen.add((target, next_index))
        warps = catalog[target].get("warp_events", [])
        if not 0 <= next_index < len(warps):
            return False
        map_name, index = target, next_index
    return False



def static_connection_findings(name, index, conn, catalog, by_id, layouts):
    """Seam model for one map connection.

    pokeemerald connections do not paste a neighbour over the map interior:
    src/fieldmap.c FillNorth/South/West/EastConnection copy MAP_OFFSET rows or
    columns into the border strip just outside the layout, and CameraMove()
    switches maps when the camera would step past the grid border.  Walking
    outward therefore has to change map, and SetPositionFromConnection() fixes
    the landing coordinates:

        south -> (px - offset, 0)          north -> (px - offset, B.height-1)
        west  -> (0, py - offset)          east  -> (B.width-1, py - offset)
    """
    data = catalog[name]
    target = by_id.get(conn.get("map"))
    out = {"map": name, "connection": index, "direction": conn.get("direction"),
           "offset": conn.get("offset"), "dest_map": conn.get("map"),
           "dest_name": target, "issues": []}
    if target is None:
        out["class"] = "missing_target"
        out["issues"].append("connection target map id not in the ROM")
        return out
    out["class"] = "internal"
    src = layouts[data["layout"]]
    dst = layouts[catalog[target]["layout"]]
    out["self_size"] = [src["width"], src["height"]]
    out["dest_size"] = [dst["width"], dst["height"]]
    d, off = conn["direction"], conn["offset"]
    w, h = src["width"], src["height"]
    if d in ("up", "down"):
        # lanes are columns; a lane belongs to this connection when
        # (lane - offset) is a column of the connected map.
        span = dst["width"]
        limit = w
    else:
        span = dst["height"]
        limit = h
    out["lane_range"] = [max(0, off), min(limit, off + span) - 1]
    if out["lane_range"][1] < out["lane_range"][0]:
        out["issues"].append(
            f"{d} connection to {target} shares no lane with {name} "
            f"({w}x{h} vs {dst['width']}x{dst['height']})")
    # reciprocal connection declared on the other side?
    back = None
    for j, c in enumerate(catalog[target].get("connections") or []):
        if c.get("map") == data["id"]:
            opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}
            if c.get("direction") == opposite[d]:
                back = j
                break
    out["reciprocal_index"] = back
    if back is None:
        out["issues"].append(
            f"no reciprocal { {'up':'down','down':'up','left':'right','right':'left'}[d] }"
            f" connection on {target} back to {name}")
    return out


# ---------------------------------------------------------------------------
# Emulator session
# ---------------------------------------------------------------------------
class WarpPlaytestMixin:
    """StoryGame + unlocked player state + warp introspection helpers.

    Mixed into test_story.StoryGame lazily by make_playtest() so that the
    static pre-pass can run with a plain system python (no mGBA bindings).
    """

    def __init__(self, spawn=None):
        super().__init__(spawn=spawn)
        self.reboots = 0
        self.reboot_budget = 40
        self.unlock()
        self._obj_stride = self.sizes["gObjectEvents"] // 16
        self._main = self.symbol_address("gMain")
        self._overworld = self.symbol_address("CB2_Overworld") & ~1
        self._ok_callbacks = {self._overworld}
        for transient in ("CB2_LoadMap2", "CB2_ReturnToField", "CB2_ReturnToFieldLocal",
                          "CB2_ReturnToFieldContinueScript"):
            try:
                self._ok_callbacks.add(self.symbol_address(transient) & ~1)
            except KeyError:
                pass
        self._avatar = self.symbol_address("gPlayerAvatar")
        self._events = self.symbol_address("gObjectEvents")
        self.last_facing_sample = "landing"
        # Surf kit state, or None when it has not been granted yet.
        self.surf_kit = None
        self.last_surf_note = ""

    # -- setup ------------------------------------------------------------
    def unlock(self):
        """Open every gate so region_v7/story-gated geometry is reachable."""
        names = set()
        for header in ("flags.h", "plastic_ox_flags.h", "plastic_ox_story.h"):
            path = ROOT / "include/constants" / header
            if path.exists():
                names |= set(re.findall(r"^#define (FLAG_\w+)", path.read_text(), re.M))
        wanted = [n for n in names
                  if n.startswith("FLAG_POX_STORY") or n.startswith("FLAG_POX_REACHED")
                  or n.startswith("FLAG_POX_") and "UNUSED" not in n]
        wanted += [f"FLAG_BADGE0{i}_GET" for i in range(1, 9)]
        wanted += ["FLAG_SYS_POKEDEX_GET", "FLAG_SYS_POKEMON_GET",
                  "FLAG_SYS_USE_FLASH", "FLAG_SYS_CRUISE_MODE"]
        wanted += [n for n in names if n.startswith("FLAG_OCARINA") or
                   n.startswith("FLAG_DAYCARE") or n.startswith("FLAG_POKEMON_") is False
                   and n.startswith("FLAG_SYS_") and n not in wanted]
        for name in wanted:
            try:
                self.flag(name, True)
            except (KeyError, AssertionError):
                pass
        # Deterministic geometry tests must not be interrupted by encounters.
        if "sWildEncountersDisabled" in self.syms:
            self.write(self.syms["sWildEncountersDisabled"], 1)

    def reboot(self):
        """Recover the core after a crash/hang without re-parsing symbols.

        A soft core.reset() is not always enough: a map that kills the engine
        leaves gMapHeader unusable, and the boot fixture then cannot get back
        to the overworld.  If the soft path does not restore a usable core, a
        brand new mGBA core is loaded instead."""
        import walklib
        if self.health() is not None or not self._soft_reboot():
            self._hard_reboot()
        self.reboots += 1
        # A reboot wipes the fixture, so the granted Surf kit has to go too.
        self.surf_kit = None
        return self.health()

    def _soft_reboot(self):
        import walklib
        from mgba.image import Image
        self.core.reset()
        self.fb = Image(*self.core.desired_video_dimensions())
        self.core.set_video_buffer(self.fb)
        try:
            walklib.boot_test_game(self)
        except Exception:
            return False
        self.set_text_speed_fast()
        self.unlock()
        return self.health() is None

    def _hard_reboot(self):
        import mgba.core
        import walklib
        from mgba.image import Image
        self.core = mgba.core.load_path(str(ROOT / "pokeemerald.gba"))
        self.fb = Image(*self.core.desired_video_dimensions())
        self.core.set_video_buffer(self.fb)
        self.core.reset()
        self.fb = Image(*self.core.desired_video_dimensions())
        self.core.set_video_buffer(self.fb)
        try:
            walklib.boot_test_game(self)
        except Exception:
            pass
        self.set_text_speed_fast()
        self.unlock()

    def run(self, name, limit=3600):
        """test_story.run() builds its failure message with string
        concatenation and the script pointer is an int, so a script that never
        finishes surfaces as a TypeError instead of the real failure."""
        try:
            return super().run(name, limit)
        except TypeError as exc:
            raise AssertionError(
                f"injected field script never finished ({exc})") from exc

    # -- introspection ----------------------------------------------------
    def facing(self):
        object_id = self.u8(self._avatar + 5)
        return self.u16(self._events + object_id * self._obj_stride + 0x18) & 0xF

    def health(self):
        """None when the core is usable.

        CB2_LoadMap2 / CB2_ReturnToField are the engine's own transient
        map-load callbacks, not a crash: a warp that is still resolving sits in
        one of them for a few hundred frames."""
        try:
            if self.state() is None:
                return "no-saveblock"
            cb = self.core.memory.iwram.u32[self._main - 0x03000000 + 4] & ~1
            if cb in self._ok_callbacks:
                return None
            return f"callback {hex(cb)} != overworld"
        except Exception as exc:  # pragma: no cover - defensive
            return f"exception {exc}"

    def callback(self):
        """gMain.callback, i.e. which top-level state the engine is in."""
        try:
            return self.core.memory.iwram.u32[self._main - 0x03000000 + 4] & ~1
        except Exception:  # pragma: no cover - defensive
            return None

    def grid_walkable(self, x, y):
        """(walkable, elevation) for a live-grid map coordinate."""
        try:
            collision, elev = self.collision_at(x, y)
            return collision == 0, elev
        except Exception:
            return False, 0

    def live_size(self):
        """(width, height) of the live map layout, from the loaded grid."""
        g = self.mapgrid_info()
        return g["width"] - 14, g["height"] - 14

    def live_behavior(self, x, y):
        try:
            return behavior_name(self.behavior_at(x, y)[0])
        except Exception:
            return None

    def shot(self, name):
        SHOTS.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
        return self._shot(str(SHOTS / (safe + ".png")))

    def _shot(self, path):
        try:
            self.fb.to_pil().convert("RGB").save(path)
            return path
        except Exception:
            return None

    # -- movement ---------------------------------------------------------
    def release_scripts(self):
        """Return the field script context to idle.

        Never mash A here: pressing A on the current tile *starts* scripts and
        locks field controls.  B cancels dialog; if a script is still running
        afterwards the context is reset the same way StoryGame.begin() does."""
        status = self.syms["sGlobalScriptContextStatus"]
        if self.u8(status) == 2:
            return True
        for _ in range(8):
            self.tap(K_B, hold=1, wait=6)
            self.frame(6)
            if self.u8(status) == 2:
                return True
        ctx = self.syms["sGlobalScriptContext"]
        for i in range(self.sizes["sGlobalScriptContext"]):
            self.write(ctx + i, 0)
        self.write(status, 2)
        self.write(self.syms["sLockFieldControls"], 0)
        self.frame(20)
        return self.u8(status) == 2

    def goto(self, mapname, x, y, tries=3, reboot_budget=3):
        """Warp-inject to (mapname,x,y).  Returns (ok, note).

        An injection that fails mid-script can leave the field-script context
        busy, which poisons every later injection, so an *injection* failure
        buys a clean reboot.  Landing one tile away from the request is not a
        harness fault (some maps slide the player) and never reboots; the total
        reboot budget is bounded so a pathological map cannot stall the run."""
        for attempt in range(tries):
            if not self.release_scripts() or self.health():
                # Some facilities start a looping field script that the context
                # reset cannot stop; only a clean boot gets injection working.
                if self.reboot_budget > 0:
                    self.reboot_budget -= 1
                    self.reboot()
                    continue
                return False, "field script will not release / emulator unhealthy"
            try:
                self.warp(mapname, x, y)
                st = self.state()
                bad = self.health()
                if bad:
                    return False, bad
                if (st["x"], st["y"]) != (x, y):
                    return False, f"landed at ({st['x']},{st['y']}) not ({x},{y})"
                # The saveblock flips ~200 frames before InitMapLayoutData
                # fills the grid; reading the grid before then yields
                # MAPGRID_UNDEFINED and every tile looks solid.
                if not self.grid_ready(x, y, 1200):
                    return False, f"grid for ({x},{y}) never filled"
                self.frame(10)
                bad = self.health()
                return (not bad), bad or ""
            except AssertionError as exc:
                note = f"warp injection failed: {exc}"
                if attempt == tries - 1:
                    return False, note
                if self.reboot_budget > 0:
                    self.reboot_budget -= 1
                    self.reboot()
        return False, "warp injection failed"

    def step_into(self, direction, expect_key=None, timeout=900, watch=1200,
                  expect_xy=None, via_surf=False):
        """Hold `direction` until the map changes, then watch the arrival.

        Returns (outcome, landed, arrival_facing, rest).
          outcome        'warped' | 'blocked' | 'timeout' | 'surf-blocked'
          landed         the engine's warp landing tile, sampled the frame the
                         saveblock location flips
          arrival_facing avatar direction captured on the first frame after the
                         destination grid is real
          rest           where the player settles; Gen 3 lets a finished
                         door/stair warp carry the player one tile off the
                         landing, so landing and rest can differ

        `expect_xy` is the declared landing tile.  A handful of legitimate
        warps are mutual pairs inside one map (Mossdeep City Gym's switch
        warps, Victory Road's short cut, the Route 44 / Mt. Moon cave link),
        where the map id never changes; without the landing tile the harness
        could only ever report those as timeouts.

        `via_surf` makes the step itself a Surf mount: a warp that sits on
        water (the Seafoam whirlpools, the S.S. Anne's ocean dock) can only be
        entered from the board, and the engine performs the one-tile step
        itself when the player confirms the prompt.
        """
        key = DIRKEY[direction]
        start = self.state()
        start_xy = (start["x"], start["y"]) if start else None
        start_cb = self.callback()
        if via_surf:
            st = self.state()
            ahead = ((st["x"], st["y"] - 1) if direction == "UP" else None)
            if ahead is not None and self.live_behavior(*ahead) in WATERFALL_BEHAVIORS:
                ok, note = self.use_waterfall()
            else:
                ok, note = self.mount_surf(direction)
            self.last_surf_note = note
            if not ok:
                return "surf-blocked", None, None, None
        else:
            self.core.set_keys(key)
        frames = 0
        outcome = "timeout"
        landed = None
        # A map load always runs through one of gMain's transient callbacks, even
        # when the destination is the map you are already standing on (Mossdeep
        # City Gym's switch warps, Victory Road's short cut).  Watching for it is
        # what lets a same-map warp be told apart from ordinary walking.
        saw_load = False
        while frames < timeout:
            self.frame(1)
            frames += 1
            st = self.state()
            if st is None:
                outcome = "blocked"
                break
            if (st["group"], st["num"]) != (start["group"], start["num"]):
                outcome = "warped"
                landed = (st["x"], st["y"])
                break
            cb = self.callback()
            if cb is not None and cb != start_cb:
                saw_load = True
                continue
            if saw_load and (st["x"], st["y"]) != start_xy:
                outcome = "warped"
                landed = (st["x"], st["y"])
                break
        self.core.clear_keys(key)
        self.frame(1)
        if landed is None:
            self.settle(None)
            return outcome, None, None, None
        # InitObjectEventsLocal() fills the grid a few frames before it sets the
        # avatar, and the player may already be walking off the landing tile, so
        # the arrival facing is sampled a few frames after the grid goes real
        # while the player is still standing on the landing.
        facing = None
        ready_frames = 0
        for _ in range(watch):
            st = self.state()
            if st is None:
                break
            if not (0 <= st["x"] < 400 and 0 <= st["y"] < 400):
                # mid-handover sentinel (ApplyCurrentWarp/SetPositionFromConnection
                # briefly store -1); not a real position
                self.frame(1)
                continue
            if (st["x"], st["y"]) != tuple(landed):
                self.core.clear_keys(key)
                self.settle(expect_key)
                st = self.state()
                if facing is None:
                    facing = self.facing()
                    self.last_facing_sample = "post-settle"
                else:
                    self.last_facing_sample = "landing"
                return outcome, landed, facing, (st["x"], st["y"])
            if self._grid_ready(st, expect_key):
                ready_frames += 1
                if facing is None and ready_frames >= 4:
                    facing = self.facing()
            self.frame(1)
        self.settle(expect_key)
        st = self.state()
        if facing is None:
            # The player was already moving when the transition finished, so the
            # pre-move facing is gone; sample what is visible and say so.
            facing = self.facing()
            res_flag = "post-settle"
        else:
            res_flag = "landing"
        rest = (st["x"], st["y"]) if st else tuple(landed)
        self.last_facing_sample = res_flag
        return outcome, landed, facing, rest

    def settle(self, expect_key, timeout=1800):
        """Wait out any running map transition so the next script injection
        cannot land in the middle of a fade and corrupt the field state."""
        if expect_key is not None:
            self.wait_warp_complete(tuple(expect_key), timeout=timeout)
        for _ in range(40):
            self.frame(2)
        return self.health()

    def grid_ready(self, x, y, frames=1200):
        """Wait until the live block grid really holds data at (x,y).

        walklib.wait_grid_ready() indexes gBackupMapLayout.map without guarding
        the pointer, which is still garbage mid-transition; every read here is
        therefore guarded."""
        for _ in range(frames):
            self.frame(1)
            try:
                mt, _ = self.metatile_at(x, y)
            except Exception:
                continue
            if mt is not None and mt != 1023:
                return True
        return False

    def _grid_ready(self, st, expect_key):
        """True once the destination map's block grid is really filled."""
        if expect_key is not None and (st["group"], st["num"]) != tuple(expect_key):
            return False
        try:
            mt, _ = self.metatile_at(st["x"], st["y"])
        except Exception:
            return False
        return mt is not None and mt != 1023

    def step_one_tile(self, direction, timeout=600):
        """Hold `direction` until the player has moved exactly one tile.

        Returns (ok, before, after)."""
        key = DIRKEY[direction]
        before = self.state()
        self.core.set_keys(key)
        frames = 0
        moved = None
        while frames < timeout:
            self.frame(1)
            frames += 1
            st = self.state()
            if st is None:
                break
            if (st["x"], st["y"]) != (before["x"], before["y"]):
                moved = st
                break
        self.core.clear_keys(key)
        self.frame(2)
        return moved is not None, before, moved or self.state()

    # -- surf / waterfall kit --------------------------------------------
    # The harness boots a fresh-game fixture (walklib.boot_test_game), so the
    # player starts with an empty party and an empty bag: there is no battery
    # save to edit.  Surf is granted in memory the same way the story scripts
    # grant it -- through the engine's own field-script commands, so the bag
    # encryption and the Gen 3 substruct layout stay the engine's business:
    #
    #   * a party mon (ScrCmd_createmon) that is taught Surf and Waterfall
    #     (ScrCmd_setmonmove), because IsFieldMoveUnlocked_Surf *and*
    #     PartyHasMonWithSurf() both have to be true for the A prompt,
    #   * ITEM_SURF_KEY in the bag (ScrCmd_additem), because with
    #     FLAG_POX_TRIGGERS_ENABLED set this ROM unlocks Surf from the key
    #     item rather than from the Surf Badge (src/field_move.c),
    #   * FLAG_BADGE07_GET, already set by unlock(), for Waterfall.
    def script_opcode(self, native):
        """Index of `native` in gScriptCmdTable (test_story does the same)."""
        if native not in self.syms:
            raise KeyError(f"{native} not in the ROM symbol table")
        table = self.syms["gScriptCmdTable"]
        end = self.syms["gScriptCmdTableEnd"]
        for i in range((end - table) // 4):
            if self.u32(table + i * 4) & ~0x02000001 == self.syms[native] & ~1:
                return i
        raise KeyError(f"no script opcode for {native}")

    def run_bytecode(self, code):
        """Run a short field-script byte string and return when it ends."""
        ptr = self.syms["gStringVar4"]
        for i, b in enumerate(bytes(code) + bytes([2])):  # 2 == ScrCmd_end
            self.write(ptr + i, b)
        return self.run(ptr)

    def fieldmove_holder(self, field_move):
        """Party index of a mon that knows the field move, or PARTY_SIZE.

        This is exactly the engine's own `checkfieldmove` test, so a nonzero
        result means the A prompt will really appear."""
        self.write(self.syms["gSpecialVar_Result"], 0xFFFF)
        opcode = self.script_opcode("ScrCmd_checkfieldmove")
        self.run_bytecode(bytes([opcode, field_move, 1]))
        return self.u16(self.syms["gSpecialVar_Result"])

    def grant_surf_kit(self):
        """Give the fixture player Surf (and Waterfall).  Returns (ok, note)."""
        if self.surf_kit is not None:
            return self.surf_kit
        try:
            if not self.release_scripts():
                return False, "field script will not release"
            if self.u8(self.syms["gPartiesCount"]) == 0:
                opcode = self.script_opcode("ScrCmd_callnative")
                code = bytes([opcode]) + struct.pack(
                    "<I", self.syms["ScrCmd_createmon"] | 1)
                # side=player, slot=6 (append), species=Squirtle, level=12,
                # then six fixed IVs (all zero).
                code += struct.pack("<BBHHI", 0, 6, 7, 12, sum(1 << i for i in range(11, 17)))
                code += struct.pack("<6H", 0, 0, 0, 0, 0, 0)
                self.run_bytecode(code)
            if self.u8(self.syms["gPartiesCount"]) == 0:
                self.surf_kit = (False, "the ROM refused to build a party mon")
                return self.surf_kit
            setmove = self.script_opcode("ScrCmd_setmonmove")
            moves = [MOVE_SURF, MOVE_WATERFALL, MOVE_SURF, MOVE_SURF]
            self.run_bytecode(b"".join(bytes([setmove, 0, slot]) + struct.pack("<H", move)
                                      for slot, move in enumerate(moves)))
            additem = self.script_opcode("ScrCmd_additem")
            self.run_bytecode(bytes([additem]) + struct.pack("<HH", ITEM_SURF_KEY, 1))
            surf = self.fieldmove_holder(FIELD_MOVE_SURF)
            fall = self.fieldmove_holder(FIELD_MOVE_WATERFALL)
            if surf >= PARTY_SIZE:
                self.surf_kit = (False, "Surf is still locked after granting "
                                        f"ITEM_SURF_KEY and a Surf mon (holder={surf})")
            else:
                self.surf_kit = (True, f"surf holder=party[{surf}] waterfall holder={fall}")
        except Exception as exc:  # pragma: no cover - defensive
            self.surf_kit = (False, f"could not grant Surf: {exc!r}")
        return self.surf_kit

    # -- surf state --------------------------------------------------------
    def surfing(self):
        """True when the avatar is on the board (PLAYER_AVATAR_FLAG_SURFING)."""
        try:
            return bool(self.u8(self._avatar) & PLAYER_AVATAR_FLAG_SURFING)
        except Exception:
            return False

    def player_elevation(self):
        """PlayerGetElevation(): the avatar's previousElevation nibble."""
        try:
            object_id = self.u8(self._avatar + 5)
            return self.u8(self._events + object_id * self._obj_stride + 0x0B) >> 4
        except Exception:
            return ELEVATION_DEFAULT

    def mount_surf(self, direction=None, timeout=1500):
        """Put the player on the surfboard.  Returns (ok, note).

        The engine offers the prompt only when the tile in front is surfable
        water *and* the player stands at ELEVATION_DEFAULT (IsPlayerFacing-
        SurfableFishableWater), so the pre-check reports the real reason
        instead of a silent "did not warp" timeout.  Confirming the Gen 3
        YES/NO box is done by mashing A, then retrying with the cursor nudged
        in case the box opened on NO."""
        if self.surfing():
            return True, "already surfing"
        ok, note = self.grant_surf_kit()
        if not ok:
            return False, note
        if not self.release_scripts():
            return False, "field script will not release"
        st = self.state()
        if st is None:
            return False, "no saveblock"
        if direction is None:
            direction = DIR_NAME.get(self.facing())
        if direction not in DIRS:
            return False, "the player is not facing a cardinal direction"
        dx, dy = DIRS[direction]
        fx, fy = st["x"] + dx, st["y"] + dy
        behavior = self.live_behavior(fx, fy)
        if not is_surface(behavior):
            return False, f"tile ({fx},{fy}) is {behavior}, not surfable water"
        elevation = self.player_elevation()
        if elevation != ELEVATION_DEFAULT:
            return False, (f"the player stands at elevation {elevation}; the engine "
                           f"only offers Surf from ELEVATION_DEFAULT "
                           f"({ELEVATION_DEFAULT})")
        self.tap(DIRKEY[direction], hold=2, wait=4)
        status = self.syms["sGlobalScriptContextStatus"]
        start = (st["x"], st["y"])
        for attempt in range(4):
            if attempt:
                # The box can be left on NO; nudge the cursor left and retry.
                self.tap(DIRKEY["LEFT"], hold=2, wait=6)
            self.tap(K_A, hold=2, wait=24)
            boarded = False
            for _ in range(24):
                self.frame(30)
                if self.surfing():
                    boarded = True
                    break
                if self.state() is None or self.u8(status) == 2:
                    break
            if not boarded:
                continue
            # SurfFieldEffect_Init sets PLAYER_AVATAR_FLAG_SURFING before the
            # hop, so the flag alone is not "the player is on the board": wait
            # for the one-tile step onto the water the engine is about to make.
            for _ in range(30):
                self.frame(10)
                now = self.state()
                if now is None or (now["x"], now["y"]) != start:
                    break
            now = self.state()
            if now is not None and (now["x"], now["y"]) == start:
                return False, (f"the player mounted but never left ({start[0]},{start[1]})")
            return True, f"surfing at ({now['x']},{now['y']})"
        self.release_scripts()
        return False, (f"the Surf prompt at ({start[0]},{start[1]}) facing {direction} "
                       f"never put the player on the board")

    def use_waterfall(self, timeout=2400):
        """Climb an MB_WATERFALL tile from the board.  Returns (ok, note).

        The engine only offers the Waterfall prompt to a player who is already
        surfing and facing north at a waterfall tile
        (GetInteractedWaterScript), so this is the Surf prompt's sibling: A,
        the YES/NO box, then the climb field effect, which is itself the step
        that carries the player up (and onto whatever warp the climb ends on)."""
        ok, note = self.grant_surf_kit()
        if not ok:
            return False, note
        if not self.release_scripts():
            return False, "field script will not release"
        st = self.state()
        if st is None:
            return False, "no saveblock"
        if not self.surfing():
            # Waterfall needs the board: mount on any side that offers the
            # prompt, then climb from wherever the engine put the player.
            here = (st["x"], st["y"])
            for d in ("UP", "DOWN", "LEFT", "RIGHT"):
                dx, dy = DIRS[d]
                if is_surface(self.live_behavior(here[0] + dx, here[1] + dy) or ""):
                    ok, note = self.mount_surf(d)
                    if ok:
                        break
            else:
                return False, (f"the player is not on the board and no neighbouring "
                               f"tile offers the Surf prompt at {here}")
            st = self.state()
            if st is None:
                return False, "the emulator lost the saveblock"
        behavior = self.live_behavior(st["x"], st["y"] - 1)
        if behavior not in WATERFALL_BEHAVIORS:
            return False, f"the tile north of ({st['x']},{st['y']}) is {behavior}, not a waterfall"
        self.tap(DIRKEY["UP"], hold=2, wait=4)
        start = (st["x"], st["y"])
        status = self.syms["sGlobalScriptContextStatus"]
        for attempt in range(4):
            if attempt:
                self.tap(DIRKEY["LEFT"], hold=2, wait=6)
            self.tap(K_A, hold=2, wait=24)
            for _ in range(timeout // 30):
                self.frame(30)
                now = self.state()
                if now is None:
                    return False, "the emulator lost the saveblock"
                if (now["x"], now["y"]) != start:
                    return True, f"climbed to ({now['x']},{now['y']})"
                if self.u8(status) == 2:
                    break
        self.release_scripts()
        return False, f"the waterfall north of ({start[0]},{start[1]}) never lifted the player"

    def dismount_surf(self, timeout=1200):
        """Walk back onto ELEVATION_DEFAULT land; the engine does the dismount.

        CanStopSurfing() fires whenever a surfing player is about to step onto
        an ELEVATION_DEFAULT tile, so the harness only has to hold a direction
        towards dry ground."""
        if not self.surfing():
            return True, ""
        here = self.state()
        if here is None:
            return False, "no saveblock"
        shore = self.nearest_dry_tile()
        if shore is None:
            return False, "no dry land reachable from the surfboard"
        dx, dy = shore[0] - here["x"], shore[1] - here["y"]
        # The shore search is a 4-way flood fill, so the tile it returns can be
        # diagonal from the player, which no single direction key can reach.
        # Only a cardinally adjacent shore is worth a direct tap; everything
        # else (multi-tile or diagonal) goes through the live pathfinder, which
        # only ever emits cardinal steps.
        if abs(dx) > 1 or abs(dy) > 1 or (dx != 0 and dy != 0):
            ok, note = self.swim_to(shore[0], shore[1])
            if ok:
                return True, "stepped ashore"
            return False, note
        direction = next((d for d, v in DIRS.items() if v == (dx, dy)), None)
        if direction is None:
            return False, (f"the shore tile {shore} is not one cardinal step from "
                           f"({here['x']},{here['y']})")
        self.tap(DIRKEY[direction], hold=2, wait=8)
        for _ in range(timeout // 20):
            self.frame(20)
            if not self.surfing():
                return True, f"dismounted at {self.state()['x']},{self.state()['y']}"
        return False, "the player stayed on the surfboard"

    def ensure_footed(self):
        """Never step into a warp or an injection while still on the board."""
        if self.surfing():
            ok, note = self.dismount_surf()
            if not ok:
                # A forced dismount is better than a stale surfing flag: the
                # next injection re-derives the avatar state anyway.
                self.write(self._avatar, self.u8(self._avatar) & ~PLAYER_AVATAR_FLAG_SURFING)
                return False, note
        return True, ""

    # -- grid walking that tolerates water --------------------------------
    def live_passable(self, x, y, allow_water, elevation=None):
        walk, elev = self.grid_walkable(x, y)
        if not walk:
            return False
        behavior = self.live_behavior(x, y)
        if waterish(behavior) and not allow_water:
            return False
        if elevation is not None and elevation not in (0, 15) and elev not in (0, 15) \
                and elev != elevation:
            return False
        return True

    def nearest_dry_tile(self):
        """Closest standable, non-water ELEVATION_DEFAULT tile on the live map.

        ELEVATION_DEFAULT is the only level the engine will let a surfing
        player step onto (CanStopSurfing), so it is also the only level a
        dismount target can be on."""
        st = self.state()
        if st is None:
            return None
        w, h = self.live_size()
        seen = {(st["x"], st["y"])}
        queue = collections.deque([(st["x"], st["y"])])
        while queue:
            x, y = queue.popleft()
            behavior = self.live_behavior(x, y)
            if (x, y) != (st["x"], st["y"]) and not waterish(behavior or "") \
                    and self.live_passable(x, y, False) \
                    and self.grid_walkable(x, y)[1] == ELEVATION_DEFAULT:
                return x, y
            for dx, dy in DIRS.values():
                nx, ny = x + dx, y + dy
                if (nx, ny) in seen or not (0 <= nx < w and 0 <= ny < h):
                    continue
                if not self.live_passable(nx, ny, True):
                    continue
                seen.add((nx, ny))
                queue.append((nx, ny))
        return None

    def _next_step_toward(self, tx, ty):
        """First tile of a live-grid path to (tx,ty), or None."""
        st = self.state()
        if st is None:
            return None
        w, h = self.live_size()
        start = (st["x"], st["y"])
        if start == (tx, ty):
            return ()
        previous = {start: None}
        queue = collections.deque([start])
        while queue:
            x, y = queue.popleft()
            for direction, (dx, dy) in DIRS.items():
                nxt = (x + dx, y + dy)
                if nxt in previous or not (0 <= nxt[0] < w and 0 <= nxt[1] < h):
                    continue
                if nxt != (tx, ty) and not self.live_passable(nxt[0], nxt[1], True):
                    continue
                previous[nxt] = (x, y)
                if nxt == (tx, ty):
                    node = nxt
                    while previous[node] is not None and previous[node] != start:
                        node = previous[node]
                    return None if node == start and nxt == start else (node[0] - start[0],
                                                                        node[1] - start[1])
                queue.append(nxt)
        return None

    def swim_to(self, tx, ty, budget=14):
        """Walk or surf the player onto (tx,ty).  Returns (ok, note)."""
        for _ in range(budget):
            st = self.state()
            if st is None:
                return False, "no saveblock"
            if (st["x"], st["y"]) == (tx, ty):
                return True, ""
            delta = self._next_step_toward(tx, ty)
            if delta is None:
                return False, f"no walkable path from ({st['x']},{st['y']}) to ({tx},{ty})"
            direction = next((d for d, v in DIRS.items() if v == delta), None)
            if direction is None:
                return False, f"no cardinal step towards ({tx},{ty}) from ({st['x']},{st['y']})"
            nx, ny = st["x"] + delta[0], st["y"] + delta[1]
            behavior = self.live_behavior(nx, ny)
            if waterish(behavior) and not self.surfing():
                ok, note = self.mount_surf(direction)
                if not ok:
                    return False, f"surf needed for ({nx},{ny}): {note}"
                continue
            ok, before, after = self.step_one_tile(direction)
            if not ok or (after["x"], after["y"]) == (before["x"], before["y"]):
                if waterish(behavior):
                    ok, note = self.mount_surf(direction)
                    if ok:
                        continue
                return False, (f"blocked walking {direction} from "
                               f"({before['x']},{before['y']}) onto {behavior} "
                               f"({nx},{ny})")
        return False, f"did not reach ({tx},{ty}) within {budget} steps"

    def place_in_water(self, x, y, tries=3):
        """Get the player onto a water tile (x,y) the way a player would.

        Injects on the nearest dry tile, mounts Surf from the shore and swims
        the rest of the way, so the run-up is a real mount-and-swim rather than
        a warp-injection onto water."""
        if not ALLOW_SURF:
            return False, "surf expansion disabled (--no-surf)"
        self.ensure_footed()
        shore = self.nearest_dry_tile()
        if shore is None:
            return False, "no dry land to mount Surf from"
        st = self.state()
        here = MAP_NAMES.get((st["group"], st["num"])) if st else None
        if shore != (x, y):
            ok, note = self.goto(here, shore[0], shore[1])
            if not ok:
                return False, f"goto shore {shore} failed ({note})"
        ok, note = self.swim_to(x, y)
        if not ok:
            return False, note
        return True, f"surfing at ({x},{y})"



# ---------------------------------------------------------------------------
# Dynamic per-warp test
# ---------------------------------------------------------------------------
# Arrow warps only trigger when they are stepped on along the arrow, so the
# harness has to approach them from the correct side or it reports a warp that
# "does not fire" when the data is fine.
APPROACH_FOR_BEHAVIOR = {
    "MB_SOUTH_ARROW_WARP": "DOWN", "MB_WATER_SOUTH_ARROW_WARP": "DOWN",
    "MB_SHOAL_CAVE_ENTRANCE": "DOWN", "MB_DEEP_SOUTH_WARP": "DOWN",
    "MB_NORTH_ARROW_WARP": "UP", "MB_STAIRS_OUTSIDE_ABANDONED_SHIP": "UP",
    "MB_EAST_ARROW_WARP": "RIGHT", "MB_WEST_ARROW_WARP": "LEFT",
    "MB_UP_RIGHT_STAIR_WARP": "RIGHT", "MB_DOWN_RIGHT_STAIR_WARP": "RIGHT",
    "MB_UP_LEFT_STAIR_WARP": "LEFT", "MB_DOWN_LEFT_STAIR_WARP": "LEFT",
    "MB_ROCK_STAIRS": "DOWN", "MB_AQUA_HIDEOUT_WARP": "DOWN",
    "MB_LAVARIDGE_GYM_1F_WARP": "DOWN",
}


def static_approaches(name, wx, wy, catalog, allow_water=False):
    """Cardinal directions from which the player can legally stand next to a warp.

    `allow_water` adds the sides whose approach tile is water: those are only
    reachable on the surfboard, so they are only tried by the surf pass."""
    geom = geometry(name, catalog)
    if geom is None:
        return ["UP", "DOWN", "LEFT", "RIGHT"]
    out = []
    try:
        welev = geom.tile(wx, wy)[1]
    except Exception:
        welev = 0
    for d, (dx, dy) in DIRS.items():
        ax, ay = wx - dx, wy - dy
        if not (0 <= ax < geom.w and 0 <= ay < geom.h):
            continue
        c2, e2, b2 = geom.tile(ax, ay)
        if c2 != 0 or (waterish(b2) and not allow_water):
            continue
        if welev not in (0, 15) and e2 not in (0, 15) and e2 != welev:
            continue
        out.append(d)
    if not out:
        return out
    try:
        preferred = APPROACH_FOR_BEHAVIOR.get(geom.tile(wx, wy)[2])
    except Exception:
        preferred = None
    if preferred in out:
        out = [preferred] + [d for d in out if d != preferred]
    return out


def static_warp_is_wet(name, wx, wy, catalog):
    """True when the warp tile itself is water (a whirlpool / ocean dock).

    A warp on MB_*_CURRENT or MB_OCEAN_WATER cannot be entered on foot at
    all, so the surf pass has to run before the on-foot one."""
    geom = geometry(name, catalog)
    if geom is None:
        return False
    try:
        return waterish(geom.tile(wx, wy)[2])
    except Exception:
        return False


def static_needs_surf(name, wx, wy, catalog):
    """True when a dry approach does not exist, so only Surf can reach the warp."""
    if static_warp_is_wet(name, wx, wy, catalog):
        return True
    return not static_approaches(name, wx, wy, catalog, allow_water=False)


def on_approach_line(ax, ay, wx, wy, direction):
    """True when (ax,ay) is on the correct side of the warp to walk onto it."""
    if direction == "UP":
        return ax == wx and ay >= wy + 1
    if direction == "DOWN":
        return ax == wx and ay <= wy - 1
    if direction == "LEFT":
        return ay == wy and ax >= wx + 1
    return ay == wy and ax <= wx - 1


def place_for_warp(play, name, wx, wy, direction, distances=(1, 2, 3, 4, 5),
                   via_surf=False):
    """Stand the player where they can walk `direction` onto the warp.

    A script warp makes the engine carry the player one tile in the arrival
    facing, so an injected position does not always stick: the player drifts,
    usually one tile along the canonical arrival direction.  Walking in from
    further back is what a real player does, so the harness tries a short run-up
    and accepts any landing that is still on the correct side of the warp on the
    correct axis.

    `via_surf` reaches the run-up tile on the surfboard when the run-up itself
    is water: the player is dropped on the nearest dry tile, mounts Surf from
    the shore and swims the rest of the way.  The fifth element,
    `step_via_surf`, is True when the step *into* the warp is a Surf mount as
    well (the warp tile is water entered from dry land); the sixth,
    `swam`, is True when the run-up itself was reached on the board.
    """
    dx, dy = DIRS[direction]
    width, height = MAP_SIZES.get(name, (128, 128))
    notes = []
    for dist in distances:
        ax, ay = wx - dx * dist, wy - dy * dist
        # WarpData stores the landing position as two u16 fields, and the run-up
        # tile has to be inside the map: the grid beyond the layout is
        # MAPGRID_UNDEFINED, so injecting there reads as solid terrain.
        if not (0 <= ax <= 127 and 0 <= ay <= 127):
            continue
        if not (0 <= ax < width and 0 <= ay < height):
            notes.append(f"{direction}@{dist}: ({ax},{ay}) is off-map")
            continue
        if via_surf:
            ok, note = play.place_in_water(ax, ay)
            if not ok:
                notes.append(f"{direction}@{dist}: surf run-up failed ({note})")
                continue
        else:
            play.ensure_footed()
            ok, note = play.goto(name, ax, ay)
            if not ok:
                notes.append(f"{direction}@{dist}: goto failed ({note})")
                continue
        st = play.state()
        if not on_approach_line(st["x"], st["y"], wx, wy, direction):
            notes.append(f"{direction}@{dist}: injected at ({ax},{ay}) but the "
                         f"player ended at ({st['x']},{st['y']})")
            continue
        if not play.grid_walkable(st["x"], st["y"])[0]:
            notes.append(f"{direction}@{dist}: ({st['x']},{st['y']}) is not walkable")
            continue
        # A water warp entered from dry land can only be stepped onto by
        # mounting Surf: a player standing on land cannot be on the board, and
        # on foot the engine refuses the water tile.  From another water tile
        # the ordinary direction hold is enough, because a surfing player
        # already ignores water collision.
        on_water = waterish(play.live_behavior(st["x"], st["y"]) or "")
        warp_wet = waterish(play.live_behavior(wx, wy) or "")
        warp_behavior = play.live_behavior(wx, wy) or ""
        step_via_surf = dist == 1 and (
            (warp_wet and not on_water) or warp_behavior in WATERFALL_BEHAVIORS)
        return direction, st["x"], st["y"], "", step_via_surf, via_surf
    return None, None, None, "; ".join(notes[:3]), False, False


def pick_approach(play, name, wx, wy, record, direction_order=None, via_surf=False):
    """Standable run-up for warp (wx,wy).

    Returns (direction, ax, ay, note, step_via_surf, swam)."""
    order = direction_order or record.get("approaches") or ["UP", "DOWN", "LEFT", "RIGHT"]
    order = list(order) + [o for o in ("UP", "DOWN", "LEFT", "RIGHT") if o not in order]
    notes = []
    for d in order:
        direction, ax, ay, note, surf, swam = place_for_warp(play, name, wx, wy, d,
                                                             via_surf=via_surf)
        if direction is None:
            notes.append(f"{d}: {note}")
            continue
        if play.live_behavior(wx, wy) is None:
            notes.append(f"{d}: destination grid not readable at ({wx},{wy})")
            continue
        return direction, ax, ay, "", surf, swam
    return None, None, None, "; ".join(notes[:3]), False, False


def arrival_checks(play, res, landed, facing, rest, expect_key=None, expect_xy=None,
                   travel=None):
    """Post-arrival convention + softlock checks.  Mutates `res`.

    `landed` is the engine's warp landing tile, `facing` the avatar direction
    set by GetInitialPlayerAvatarState, `rest` where the player settles after
    the single step of travel the engine grants a finished door/stair warp."""
    st = play.state()
    res["arrived"] = [st["group"], st["num"]]
    res["arrived_map"] = MAP_NAMES.get((st["group"], st["num"]), f"({st['group']},{st['num']})")
    res["landed_xy"] = list(landed)
    res["rest_xy"] = list(rest)
    if expect_key is not None and (st["group"], st["num"]) != tuple(expect_key):
        res["issues"].append(
            f"arrived in {res['arrived_map']} ({st['group']},{st['num']}), "
            f"expected {res.get('expect_name', expect_key)} {tuple(expect_key)}")
    if expect_xy is not None and tuple(landed) != tuple(expect_xy):
        res["issues"].append(
            f"landed at ({landed[0]},{landed[1]}), expected "
            f"({expect_xy[0]},{expect_xy[1]})")
    # A finished Gen 3 door/stair warp carries the player one tile off the
    # landing.  Record which way and flag anything beyond a single tile.
    res["post_warp_step"] = None
    if getattr(play, "last_facing_sample", "landing") != "landing":
        res.setdefault("notes", []).append(
            "arrival facing sampled after the transition finished, not on the "
            "landing tile")
    if 0 <= rest[0] < 200 and 0 <= rest[1] < 200 and tuple(rest) != tuple(landed):
        delta = (rest[0] - landed[0], rest[1] - landed[1])
        if abs(delta[0]) + abs(delta[1]) == 1:
            res["post_warp_step"] = next(d for d, v in DIRS.items() if v == delta)
        else:
            res["issues"].append(
                f"player slid {abs(delta[0]) + abs(delta[1])} tiles from the landing "
                f"({landed[0]},{landed[1]}) to ({rest[0]},{rest[1]})")

    lx, ly = landed
    behavior = play.live_behavior(lx, ly)
    res["landing_behavior"] = behavior
    walk, elev = play.grid_walkable(lx, ly)
    res["landing_walkable"] = bool(walk)
    res["arrival_facing"] = DIR_NAME.get(facing, str(facing)) if facing is not None else None
    canonical = CANONICAL_FACING.get(behavior, "DOWN")
    res["canonical_facing"] = canonical
    if not walk and behavior not in STANDABLE_TRANSITION:
        res["issues"].append(f"lands on a solid tile ({behavior}) at ({lx},{ly})")
    allowed = {canonical}
    if travel in DIRS:
        # A finished Gen 3 warp keeps walking the player one tile; on stairs and
        # escalators the avatar is still facing the way they were travelling
        # when the arrival is sampled, so that reading is not a data fault.
        allowed.add(travel)
    if canonical == "KEEP":
        if DIR_NAME.get(facing) is None:
            res["issues"].append(f"arrival facing value {facing} is not cardinal")
    elif facing is None or DIR_NAME.get(facing) not in allowed:
        res["issues"].append(
            f"arrival facing {DIR_NAME.get(facing, facing)} != canonical {canonical} "
            f"for {behavior} at ({lx},{ly})")
    elif canonical in allowed and DIR_NAME.get(facing) == travel and canonical != travel:
        res.setdefault("notes", []).append(
            f"arrival facing reads as the travel direction {travel}; the player is "
            f"still completing the warp step off a {behavior}")
    if canonical in DIRS:
        fx, fy = lx + DIRS[canonical][0], ly + DIRS[canonical][1]
        fwalk, _ = play.grid_walkable(fx, fy)
        if not fwalk:
            res.setdefault("notes", []).append(
                f"arrival facing {canonical} points into a blocked tile ({fx},{fy})")

    # Immediate mobility (softlock probe) from the resting tile.
    rx, ry = rest
    moved = False
    order = [canonical] if canonical in DIRS else []
    order += [d for d in ("DOWN", "UP", "LEFT", "RIGHT") if d != canonical]
    for d in order:
        dx, dy = DIRS[d]
        nx, ny = rx + dx, ry + dy
        nwalk, nelev = play.grid_walkable(nx, ny)
        if not nwalk:
            continue
        if elev not in (0, 15) and nelev not in (0, 15) and nelev != elev:
            continue
        before = (rx, ry)
        play.release_scripts()
        play.core.set_keys(DIRKEY[d])
        for _ in range(150):
            play.frame(1)
            cur = play.state()
            if cur is None or (cur["x"], cur["y"]) != before:
                moved = True
                break
        play.core.clear_keys(DIRKEY[d])
        play.frame(8)
        if moved:
            res["moved_dir"] = d
            break
    res["can_move"] = moved
    if not moved:
        res["issues"].append(f"player is wedged on the landing tile ({rx},{ry})")
    return st


def try_warp_from_any_side(play, name, wx, wy, catalog, expect_key, expect_xy=None):
    """Walk onto a warp from every legal side until one fires.

    Each side is tried on foot first and, when the side or the warp tile is
    water, again from the surfboard.  Returns
    (ok, direction, approach, landed, rest, tried, via_surf, note)."""
    dry = static_approaches(name, wx, wy, catalog)
    wet = static_approaches(name, wx, wy, catalog, allow_water=True)
    is_wet = static_warp_is_wet(name, wx, wy, catalog)
    if ALLOW_SURF and is_wet:
        # No dry side can work: the warp tile itself is water.
        order = wet + [d for d in dry if d not in wet]
    else:
        order = dry + [d for d in wet if d not in dry]
    order += [d for d in ("UP", "DOWN", "LEFT", "RIGHT") if d not in order]
    tried = []
    last_note = ""
    for d in order:
        passes = [False]
        if ALLOW_SURF and (is_wet or (static_needs_surf(name, wx, wy, catalog)
                                      and d in wet)):
            passes.append(True)
        for pass_surf in passes:
            direction, ax, ay, note, via_surf, swam = place_for_warp(
                play, name, wx, wy, d, via_surf=pass_surf)
            if direction is None:
                if pass_surf:
                    last_note = note
                continue
            if d not in tried:
                tried.append(d)
            outcome, landed, _f, rest = play.step_into(direction, expect_key=expect_key,
                                                       expect_xy=expect_xy,
                                                       via_surf=via_surf)
            if outcome == "warped" and landed is not None:
                return (True, direction, (ax, ay), landed, rest, tried,
                        via_surf or swam, "")
            if outcome == "surf-blocked":
                last_note = play.last_surf_note
            play.ensure_footed()
    return False, None, None, None, None, tried, False, last_note


def test_one_warp(play, name, index, record, catalog, by_id):
    """Walk one warp out and back.  Returns a result dict."""
    res = {
        "map": name, "warp": index, "class": record.get("class"),
        "src_xy": record["src_xy"], "src_behavior": record.get("src_behavior"),
        "dest_map": record.get("dest_map"),
        "dest_name": record.get("dest_name"), "dest_warp": record.get("dest_warp"),
        "dest_xy": record.get("dest_xy"), "mutual": record.get("mutual"),
        "static_issues": record.get("issues", []),
        "issues": [], "status": "OK", "approach": None,
        "arrived": None, "arrival_facing": None, "canonical_facing": None,
        "landing_behavior": None, "landing_walkable": None, "can_move": None,
        "return_ok": None, "shot": None,
    }
    if record.get("class") == "missing_target":
        res["status"] = "UNTESTED"
        res["issues"] = record.get("issues", []) or ["static-only class"]
        return res

    dest_name = record.get("dest_name")
    group_ids = GROUP_IDS
    src_key = group_ids[name]

    # --- facility exit warps (MAP_DYNAMIC) are only meaningful when the player
    # --- actually walked in through a door, so drive them from a real entrance.
    if record.get("class") == "dynamic":
        return test_facility_exit(play, name, index, record, res, catalog)

    dx, dy = record["dest_xy"]
    res["expect_name"] = dest_name
    wx, wy = record["src_xy"]
    wet_warp = static_warp_is_wet(name, wx, wy, catalog)
    needs_surf = static_needs_surf(name, wx, wy, catalog)
    # A warp the engine's own trigger list does not accept can never fire, so
    # the harness says that instead of blaming the walk (or the surfboard).
    dead_metatile = record.get("src_behavior")
    if dead_metatile is not None and not warp_metatile_can_fire(dead_metatile):
        dead_reason = (f"the warp tile ({wx},{wy}) is {dead_metatile}, which the "
                       f"engine's warp trigger (IsWarpMetatileBehavior / TryArrowWarp) "
                       f"does not accept, so no walk or surf can fire it")
    else:
        dead_reason = ""
    # A warp on water has no dry run-up at all, so the surf pass goes first;
    # otherwise it is the fallback for the water-locked sides.
    order = static_approaches(name, wx, wy, catalog, allow_water=wet_warp and ALLOW_SURF)
    direction, ax, ay, note, via_surf, swam = pick_approach(
        play, name, wx, wy, {"approaches": order}, via_surf=wet_warp and ALLOW_SURF)
    if direction is None and ALLOW_SURF and needs_surf and not wet_warp:
        # Only water-locked warps get the surf retry: for everything else the
        # dry pass already covered every legal side.
        direction, ax, ay, note, via_surf, swam = pick_approach(
            play, name, wx, wy,
            {"approaches": static_approaches(name, wx, wy, catalog, allow_water=True)},
            via_surf=True)
    if direction is None:
        if dead_reason:
            res["status"] = "UNTESTED"
            res["issues"].append(f"{dead_reason}; approach search also failed: {note}")
        elif needs_surf and ALLOW_SURF:
            res["status"] = "UNTESTED"
            res["issues"].append(
                f"surf path needed but not reachable for ({wx},{wy}) on {name}: {note}")
        else:
            res["status"] = "ISSUE"
            res["issues"].append(f"no usable approach tile for ({wx},{wy}): {note}")
        res["shot"] = play.shot(f"{name}_{index}_noapproach")
        return res
    res["approach"] = [direction, ax, ay]
    res["via_surf"] = bool(via_surf)
    res["approach_via_surf"] = bool(swam)

    dst_key = group_ids[dest_name] if dest_name else None
    outcome, landed, afacing, rest = play.step_into(direction, expect_key=dst_key,
                                                    expect_xy=(dx, dy),
                                                    via_surf=via_surf)
    if outcome == "surf-blocked":
        res["status"] = "UNTESTED"
        res["issues"].append(
            f"surf path needed but not reachable: {play.last_surf_note}")
        res["shot"] = play.shot(f"{name}_{index}_surffail")
        return res
    if outcome != "warped" or landed is None:
        if dead_reason:
            # A warp on a metatile the engine never fires is a data defect, not
            # a harness limitation: keep it an ISSUE and name the metatile.
            res["status"] = "ISSUE"
            res["issues"].append(
                f"stepping {direction} from ({ax},{ay}) onto ({wx},{wy}) did not warp "
                f"({outcome}): {dead_reason}")
        elif needs_surf and ALLOW_SURF:
            res["status"] = "UNTESTED"
            res["issues"].append(
                f"surf path needed but not reachable: stepping {direction} from "
                f"({ax},{ay}) onto ({wx},{wy}) did not warp ({outcome})")
        else:
            res["status"] = "ISSUE"
            res["issues"].append(
                f"stepping {direction} from ({ax},{ay}) onto ({wx},{wy}) "
                f"did not warp ({outcome})")
        res["shot"] = play.shot(f"{name}_{index}_nowarp")
        return res
    play.frame(10)
    bad = play.health()
    if bad:
        res["status"] = "ISSUE"
        res["issues"].append(f"emulator unhealthy after arrival: {bad}")
        res["shot"] = play.shot(f"{name}_{index}_unhealthy")
        return res
    if record.get("class") == "bad_index":
        # Out-of-range dest_warp_id: record where the engine actually puts the
        # player instead of asserting a destination.
        arrival_checks(play, res, landed, afacing, rest, travel=direction)
    else:
        arrival_checks(play, res, landed, afacing, rest, expect_key=dst_key,
                       expect_xy=(dx, dy), travel=direction)
    if res["issues"]:
        res["status"] = "ISSUE"
        res["shot"] = res["shot"] or play.shot(f"{name}_{index}_issue")

    # --- return leg ------------------------------------------------------
    if dest_name and record.get("class") in ("internal", "landing_anchor",
                                             "dynamic_return", "chained_landing"):
        rok, rdir, rapp, rlanded, _rrest, rtried, rsurf, rnote = try_warp_from_any_side(
            play, dest_name, dx, dy, catalog, src_key,
            expect_xy=(res["src_xy"][0], res["src_xy"][1]))
        if rdir is not None:
            res["return_approach"] = [rdir, rapp[0], rapp[1]]
        if rsurf:
            res["return_via_surf"] = True
        if not rok:
            res["return_ok"] = None
            res.setdefault("notes", []).append(
                f"INCONCLUSIVE return: no side of the return warp "
                f"{dest_name}[{record['dest_warp']}] at ({dx},{dy}) triggered a warp "
                f"(tried {rtried}"
                + (f"; surf: {rnote}" if rnote else "") + ")")
            if res["status"] == "OK":
                res["status"] = "PARTIAL"
        else:
            want = (res["src_xy"][0], res["src_xy"][1])
            same_map = (play.state()["group"], play.state()["num"]) == src_key
            offset = abs(rlanded[0] - want[0]) + abs(rlanded[1] - want[1])
            res["return_offset"] = offset
            # A multi-lane door has several interior warps pointing at the same
            # exterior door, and a finished arrow-warp carries the player one
            # tile off the landing, so a one-tile miss is still "you came back
            # through the door you went in by".
            res["return_ok"] = same_map and offset <= 1
            b = play.state()
            res["return_landed"] = [MAP_NAMES.get((b["group"], b["num"]), "?"),
                                    rlanded[0], rlanded[1]]
            if not res["return_ok"]:
                res.setdefault("notes", []).append(
                    f"return landed in {MAP_NAMES.get((b['group'], b['num']), '?')} at "
                    f"({rlanded[0]},{rlanded[1]}), expected {name} at "
                    f"({want[0]},{want[1]})")
                if res["status"] == "OK":
                    res["status"] = "ISSUE"
                    res["shot"] = res["shot"] or play.shot(f"{name}_{index}_return")
    return res


def test_facility_exit(play, facility, index, record, res, catalog):
    """Pokemon Center / Mart / generic-house exits resolve through dynamicWarp.

    Walk in through a real door (which is what fills dynamicWarp), then step on
    the facility's exit warp and require to be put back on that door tile."""
    entrances = ENTRANCES.get(facility) or []
    if not entrances:
        res["status"] = "UNTESTED"
        res["issues"] = ["MAP_DYNAMIC exit with no reachable door in the closure"]
        return res
    e_name, e_index, e_record = entrances[0]
    res["entrance"] = [e_name, e_index]
    direction, ax, ay, note, esurf, eswam = pick_approach(
        play, e_name, e_record["src_xy"][0], e_record["src_xy"][1],
        {"approaches": static_approaches(e_name, e_record["src_xy"][0],
                                         e_record["src_xy"][1], catalog)})
    if direction is None:
        res["status"] = "ISSUE"
        res["issues"].append(f"could not reach the entrance warp of {e_name}: {note}")
        return res
    outcome, landed, afacing, rest = play.step_into(direction,
                                                    expect_key=GROUP_IDS[facility],
                                                    via_surf=esurf)
    if outcome != "warped":
        res["status"] = "ISSUE"
        res["issues"].append(f"entering {facility} through {e_name} did not warp")
        return res
    play.frame(10)
    arrival_checks(play, res, landed, afacing, rest, expect_key=GROUP_IDS[facility],
                   expect_xy=tuple(e_record["dest_xy"]), travel=direction)
    if res["issues"]:
        res["status"] = "ISSUE"

    fx, fy = record["src_xy"]
    rdir, rax, ray, rnote, rsurf, rswam = pick_approach(
        play, facility, fx, fy,
        {"approaches": static_approaches(facility, fx, fy, catalog)})
    if rdir is None:
        res["return_ok"] = False
        res.setdefault("notes", []).append(
            f"no approach to the facility exit warp at ({fx},{fy})")
        if res["status"] == "OK":
            res["status"] = "PARTIAL"
        return res
    rout2, rlanded, _f, _r = play.step_into(rdir, expect_key=GROUP_IDS[e_name],
                                            via_surf=rsurf)
    if rout2 != "warped" or rlanded is None:
        res["return_ok"] = False
        res.setdefault("notes", []).append(
            f"stepping the facility exit warp at ({fx},{fy}) did not warp")
        if res["status"] == "OK":
            res["status"] = "ISSUE"
        return res
    play.frame(20)
    b = play.state()
    want = (e_record["src_xy"][0], e_record["src_xy"][1])
    res["return_ok"] = ((b["group"], b["num"]) == GROUP_IDS[e_name] and
                        rlanded is not None and tuple(rlanded) == want)
    rl = rlanded or (b["x"], b["y"])
    res["return_landed"] = [MAP_NAMES.get((b["group"], b["num"]), "?"), rl[0], rl[1]]
    if not res["return_ok"]:
        res["issues"].append(
            f"facility exit did not return to the entry door: landed in "
            f"{MAP_NAMES.get((b['group'], b['num']), '?')} ({b['x']},{b['y']}), "
            f"expected {e_name} ({want[0]},{want[1]})")
        res["status"] = "ISSUE"
        res["shot"] = res["shot"] or play.shot(f"{facility}_{index}_facilityreturn")
    return res


# ---------------------------------------------------------------------------
# Connection seam test
# ---------------------------------------------------------------------------
def test_one_connection(play, name, index, conn, record, group_ids, catalog, layouts):
    """Walk a camera seam in both directions and check the map handover.

    A Gen 3 connection is seamless scrolling, not a warp: the player walks to
    the map edge, the camera steps past the grid border and the map changes
    under the player's feet.  Both directions are asserted against
    SetPositionFromConnection()'s arithmetic."""
    res = {"map": name, "connection": index, "direction": conn["direction"],
           "offset": conn["offset"], "dest_name": record.get("dest_name"),
           "static_issues": record.get("issues", []),
           "issues": [], "status": "OK", "legs": []}
    if record.get("class") != "internal" or "lane_range" not in record:
        res["status"] = "UNTESTED"
        res["issues"] = record.get("issues", ["connection target unresolved"])
        return res
    d = conn["direction"]
    off = conn["offset"]
    dest = record["dest_name"]
    w, h = record["self_size"]
    dw, dh = record["dest_size"]
    lo, hi = record["lane_range"]
    opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}[d]
    walk = {"up": "UP", "down": "DOWN", "left": "LEFT", "right": "RIGHT"}[d]
    if hi < lo:
        res["status"] = "ISSUE"
        res["issues"].append(
            f"{d} connection to {dest} shares no lane with {name}")
        return res

    # ---- outward leg: this map -> connected map ------------------------
    lane, walk_ok, walk_note, walk_surf = _try_seam(play, name, d, lo, hi, layouts)
    if not walk_ok:
        res["status"] = "ISSUE"
        res["issues"].append(f"{d} seam: {walk_note}")
        res["legs"].append({"leg": "outward", "status": "ISSUE", "note": walk_note})
        return res
    landed, rest = walk_ok[0], walk_ok[1]
    leg = {"leg": "outward", "lane": lane, "direction": walk,
           "landed": list(landed) if landed else None}
    if walk_surf:
        leg["surf"] = True
        res["via_surf"] = True
    if landed is None:
        leg["status"] = "ISSUE"
        leg["note"] = f"walked {walk} off the {d} edge and the map never changed"
        leg["shot"] = play.shot(f"{name}_conn{index}_outward_stuck")
        res["legs"].append(leg)
        res["status"] = "ISSUE"
        res["issues"].append(
            f"{name} {d} seam to {dest}: walking {walk} off the map edge does not "
            f"change map (lane {lane}) -- the connection is not walkable")
        return res
    if d == "down":
        want = (lane - off, 0)
    elif d == "up":
        want = (lane - off, dh - 1)
    elif d == "left":
        want = (dw - 1, lane - off)
    else:
        want = (0, lane - off)
    leg["expected"] = list(want)
    if tuple(landed) not in (tuple(want), (want[0] + DIRS[walk][0], want[1] + DIRS[walk][1])):
        leg["status"] = "ISSUE"
        leg["note"] = (f"handed over to {dest} at ({landed[0]},{landed[1]}), "
                       f"SetPositionFromConnection predicts ({want[0]},{want[1]})")
        res["status"] = "ISSUE"
        res["issues"].append(
            f"{name} {d} seam: handover landed at ({landed[0]},{landed[1]}) in {dest}, "
            f"expected ({want[0]},{want[1]})")
        res["legs"].append(leg)
    else:
        leg["status"] = "OK"
        leg["note"] = f"handed over to {dest} at ({landed[0]},{landed[1]})"
        res["legs"].append(leg)
        # the player must be able to keep walking on the far side
        step_ok, _b, after = play.step_one_tile(walk)
        if not step_ok or (after["x"], after["y"]) == tuple(landed):
            res["status"] = "ISSUE"
            res["issues"].append(
                f"{name} {d} seam: player cannot continue {walk} past the handover "
                f"tile ({want[0]},{want[1]}) in {dest}")
            res["legs"].append({"leg": "outward_continue", "status": "ISSUE",
                                "note": f"blocked at {list(want)}"})

    # ---- inward leg: connected map -> this map -------------------------
    back = record.get("reciprocal_index")
    if back is None:
        res["legs"].append({"leg": "inward", "status": "UNTESTED",
                            "note": f"{dest} declares no reciprocal {opposite} "
                                    f"connection back to {name}"})
        if res["status"] == "OK":
            res["status"] = "PARTIAL"
    else:
        bconn = (catalog[dest].get("connections") or [])[back]
        boff = bconn["offset"]
        blo, bhi = _lane_range_for(dest, bconn, layouts)
        owalk = {"up": "UP", "down": "DOWN", "left": "LEFT", "right": "RIGHT"}[opposite]
        plane, bwalk, bnote, bsurf = _try_seam(play, dest, opposite, blo, bhi, layouts)
        if not bwalk:
            res["status"] = "ISSUE"
            res["issues"].append(f"{dest} {opposite} seam: {bnote}")
            res["legs"].append({"leg": "inward", "status": "ISSUE", "note": bnote})
        else:
            back_landed = bwalk[0]
            ileg = {"leg": "inward", "lane": plane, "direction": owalk,
                    "landed": list(back_landed) if back_landed else None}
            if bsurf:
                ileg["surf"] = True
                res["via_surf"] = True
            if back_landed is None:
                ileg["status"] = "ISSUE"
                ileg["note"] = f"walked {owalk} off {dest} and the map never changed"
                ileg["shot"] = play.shot(f"{name}_conn{index}_inward_stuck")
                res["status"] = "ISSUE"
                res["issues"].append(
                    f"{dest} {opposite} seam back to {name}: walking {owalk} off the "
                    f"edge does not change map (lane {plane})")
            else:
                if opposite == "down":
                    bwant = (plane - boff, 0)
                elif opposite == "up":
                    bwant = (plane - boff, h - 1)
                elif opposite == "left":
                    bwant = (w - 1, plane - boff)
                else:
                    bwant = (0, plane - boff)
                ileg["expected"] = list(bwant)
                bstep = (bwant[0] + DIRS[owalk][0], bwant[1] + DIRS[owalk][1])
                if tuple(back_landed) in (tuple(bwant), bstep):
                    ileg["status"] = "OK"
                    ileg["note"] = f"returned to {name} at ({back_landed[0]},{back_landed[1]})"
                else:
                    ileg["status"] = "ISSUE"
                    ileg["note"] = (f"returned at ({back_landed[0]},{back_landed[1]}), "
                                    f"predicted ({bwant[0]},{bwant[1]})")
                    res["status"] = "ISSUE"
                    res["issues"].append(
                        f"{dest} {opposite} seam: handover landed at "
                        f"({back_landed[0]},{back_landed[1]}) in {name}, expected "
                        f"({bwant[0]},{bwant[1]})")
            res["legs"].append(ileg)
    if record.get("issues"):
        res["status"] = "ISSUE" if res["status"] != "OK" else "ISSUE"
        res["issues"] += record["issues"]
    return res


def _lane_range_for(name, conn, layouts):
    d = conn["direction"]
    catalog = CATALOG
    w, h = layouts[catalog[name]["layout"]]["width"], layouts[catalog[name]["layout"]]["height"]
    dst = layouts[catalog[by_id_lookup(conn["map"])]["layout"]]
    off = conn["offset"]
    if d in ("up", "down"):
        return [max(0, off), min(w, off + dst["width"]) - 1]
    return [max(0, off), min(h, off + dst["height"]) - 1]


def by_id_lookup(map_id):
    for name, data in CATALOG.items():
        if data["id"] == map_id:
            return name
    return None


def _try_seam(play, name, direction, lo, hi, layouts, attempts=32):
    """Try walking off `name`'s `direction` edge on a few lanes.

    `attempts` walks outward from the middle of the lane range, so a seam whose
    usable lanes sit at one end of its range (Ecruteak City's two-tile south
    gate at x=0,1) is only reachable with a wide enough sweep.

    Returns (lane, (landed, rest), note, via_surf).  Each candidate lane is really
    walked, because a lane can be statically walkable and still blocked at run
    time by an object event or by terrain one tile further out.

    When every dry lane fails and the surf expansion is on, the lanes whose
    probe tile is water are retried from the surfboard: a beach-to-beach
    connection (Pallet's south shore into ROUTE 21) is a water seam, and the
    on-foot walk can never cross it."""
    catalog = CATALOG
    w, h = layouts[catalog[name]["layout"]]["width"], layouts[catalog[name]["layout"]]["height"]
    geom = geometry(name, catalog)
    walk = {"up": "UP", "down": "DOWN", "left": "LEFT", "right": "RIGHT"}[direction]
    base = (lo + hi) // 2
    tried = []
    wet_lanes = []

    def probe_tile(lane):
        if direction in ("up", "down"):
            return (lane, 1 if direction == "up" else h - 2)
        return (1 if direction == "left" else w - 2, lane)

    for offset in range(0, attempts):
        for lane in ((base + offset), (base - offset)) if offset else (base,):
            if not (lo <= lane <= hi):
                continue
            if geom is not None:
                probe = probe_tile(lane)
                if not (0 <= probe[0] < geom.w and 0 <= probe[1] < geom.h):
                    continue
                c, _e, b = geom.tile(*probe)
                if c != 0:
                    continue
                if waterish(b):
                    wet_lanes.append(lane)
                    continue
            ok, landed, rest, why = _walk_off_edge(play, name, lane, walk, h, w)
            if ok:
                return lane, (landed, rest), "", False
            tried.append((lane, why))
    if ALLOW_SURF and wet_lanes:
        for lane in wet_lanes:
            ok, landed, rest, why = _walk_off_edge(play, name, lane, walk, h, w,
                                                   via_surf=True)
            if ok:
                return lane, (landed, rest), "", True
            tried.append((lane, "surf: " + why))
    return None, None, (f"walking {walk} off the {name} edge did not change map on "
                        f"any of {len(tried)} lanes tried: "
                        + "; ".join(f"lane {l}: {why}" for l, why in tried[:3])), False


def _walk_off_edge(play, name, lane, walk, height, width, timeout=1500,
                   via_surf=False):
    """Hold `walk` until the map changes; returns (ok, landed_xy, rest_xy).

    The player is placed two tiles in from the edge on `lane` so the camera
    still has room to scroll, exactly like a player walking out of town.  With
    `via_surf` that starting tile is water, so it is reached the way a player
    would reach it: mounted on the board and swum there."""
    d = walk.lower()
    if d == "up":
        at = (lane, 2)
    elif d == "down":
        at = (lane, height - 3)
    elif d == "left":
        at = (2, lane)
    else:
        at = (width - 3, lane)
    if via_surf:
        ok, note = play.place_in_water(at[0], at[1])
    else:
        play.ensure_footed()
        ok, note = play.goto(name, at[0], at[1])
    if not ok:
        return False, None, None, f"reaching ({at[0]},{at[1]}) failed: {note}"
    start = play.state()
    key = DIRKEY[walk]
    play.core.set_keys(key)
    frames = 0
    landed = None
    while frames < timeout:
        play.frame(1)
        frames += 1
        st = play.state()
        if st is None:
            break
        if (st["group"], st["num"]) != (start["group"], start["num"]):
            landed = (st["x"], st["y"])
            break
    play.core.clear_keys(key)
    if landed is None:
        play.settle(None)
        st = play.state()
        return False, None, None, (f"held {walk} from ({at[0]},{at[1]}) and stayed on "
                                   f"{MAP_NAMES.get((st['group'], st['num']), '?')} "
                                   f"at ({st['x']},{st['y']})")
    cur = play.state()
    play.settle((cur["group"], cur["num"]))
    rest = play.state()
    # SetPositionFromConnection briefly stores -1/0 in the s16 position while the
    # handover runs, so the settled coordinate is the only readable one.
    return True, (rest["x"], rest["y"]), (rest["x"], rest["y"]), ""


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
GROUP_IDS = {}
MAP_NAMES = {}
ENTRANCES = {}
CATALOG = {}
BY_ID = {}
# Surf / Waterfall movement expansion.  On by default; --no-surf restores the
# pure on-foot walk of the earlier runs.
ALLOW_SURF = True
MAP_SIZES = {}   # map dir -> (width, height) of its own layout


def make_playtest(spawn=None):
    """Instantiate the emulator playtest session (needs the mGBA venv)."""
    import test_story
    cls = type("WarpPlaytest", (WarpPlaytestMixin, test_story.StoryGame), {})
    return cls(spawn=spawn)


def main():
    global GROUP_IDS, MAP_NAMES, ENTRANCES, CATALOG, BY_ID, ALLOW_SURF
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, help="write full result JSON")
    ap.add_argument("--static-only", action="store_true")
    ap.add_argument("--connections-only", action="store_true")
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--exclude", action="append", default=[],
                    help="substring filter for maps to mark untestable (facilities "
                         "whose state machine a generic warp walk cannot drive)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tier", choices=["all", "story", "rest"], default="all")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--resume", type=Path, help="reuse a previous run's JSON and "
                                                 "only test the warps it has not covered")
    ap.add_argument("--maps", type=Path, help="write a per-map result index")
    ap.add_argument("--load-only", action="store_true",
                    help="only check that every map in the closure loads and "
                         "produces a usable block grid (one fresh boot per map)")
    ap.add_argument("--load-report", type=Path,
                    help="load-check JSON the warp run consults to skip maps the "
                         "engine cannot load")
    ap.add_argument("--no-surf", action="store_true",
                    help="disable the Surf/Waterfall movement expansion and walk "
                         "every warp on foot, as the earlier runs did")
    args = ap.parse_args()
    ALLOW_SURF = not args.no_surf

    catalog, by_id, reached = closure()
    _, group_ids, layouts = (None, None, None)
    catalog_all, by_id_all, group_ids, layouts = load_catalogue()
    assert catalog_all == catalog and by_id_all == by_id
    GROUP_IDS = group_ids
    CATALOG, BY_ID = catalog, by_id
    MAP_SIZES.clear()
    for _name, _data in catalog.items():
        _lay = layouts.get(_data.get("layout"))
        if _lay:
            MAP_SIZES[_name] = (_lay["width"], _lay["height"])
    MAP_NAMES = {(v[0], v[1]): k for k, v in group_ids.items()}

    names = sorted(reached)
    if args.only:
        names = [n for n in names if any(f in n for f in args.only)]
    excluded = sorted({n for n in names
                       if any(f in n for f in args.exclude)})
    if args.tier == "story":
        story_maps = {e["map"] for e in json.loads(
            (ROOT / "plastic_ox/alpha/story_manifest.json").read_text())["events"]}
        names = [n for n in names if n in story_maps or n.startswith("PlasticOx")]
    elif args.tier == "rest":
        story_maps = {e["map"] for e in json.loads(
            (ROOT / "plastic_ox/alpha/story_manifest.json").read_text())["events"]}
        names = [n for n in names if not (n in story_maps or n.startswith("PlasticOx"))]

    warp_records, conn_records = [], []
    for name in names:
        data = catalog[name]
        for index, warp in enumerate(data.get("warp_events", [])):
            warp_records.append(static_warp_findings(name, index, warp, catalog, by_id, reached))
        for index, conn in enumerate(data.get("connections") or []):
            conn_records.append(static_connection_findings(name, index, conn, catalog, by_id, layouts))

    # Reverse index: which map+index warps *into* each interior.  Facility
    # exits (MAP_DYNAMIC) are only meaningful when the player walked in through
    # a real door, so they are driven from one of these.
    for name in names:
        for index, record in enumerate(warp_records):
            if record["map"] != name:
                continue
            if record.get("class") in ("internal", "landing_anchor",
                                       "dynamic_return", "chained_landing"):
                ENTRANCES.setdefault(record["dest_name"], []).append(
                    (name, record["warp"], record))

    report = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "head": subprocess.check_output(
            ["git", "rev-parse", "--short=10", "HEAD"], cwd=ROOT, text=True).strip(),
        "rom": str(ROOT / "pokeemerald.gba"),
        "rom_sha256": hashlib.sha256((ROOT / "pokeemerald.gba").read_bytes()).hexdigest(),
        "maps": names,
        "map_count": len(names),
        "warp_count": len(warp_records),
        "connection_count": len(conn_records),
        "static": {"warps": warp_records, "connections": conn_records},
        "excluded": excluded,
        "surf": {"enabled": ALLOW_SURF,
                 "granted": None,
                 "warps_walked_on_surf": 0,
                 "returns_walked_on_surf": 0,
                 "seams_walked_on_surf": 0},
        "dynamic": {"warps": [], "connections": [], "reboots": 0,
                    "elapsed_s": 0, "untested": []},
    }

    if args.static_only:
        emit(report, args)
        return

    if args.load_only:
        report["load_check"] = load_check(args, report, layouts)
        emit(report, args)
        return

    unloadable = set()
    if args.load_report and args.load_report.exists():
        prev = json.loads(args.load_report.read_text())
        unloadable = {name for name, rec in prev.get("load_check", {}).items()
                      if not rec.get("ok")}
        report["dynamic"]["unloadable"] = sorted(unloadable)

    done = set()
    if args.resume and args.resume.exists():
        old = json.loads(args.resume.read_text())
        if old.get("rom_sha256") != report["rom_sha256"] or old.get("maps") != report["maps"]:
            raise SystemExit("resume report was produced from a different ROM or map closure")
        report["dynamic"]["warps"] = list(old.get("dynamic", {}).get("warps", []))
        report["dynamic"]["connections"] = list(old.get("dynamic", {}).get("connections", []))
        report["dynamic"]["untested"] = list(old.get("dynamic", {}).get("untested", []))
        for r in old.get("dynamic", {}).get("warps", []):
            done.add((r["map"], r["warp"]))
        for r in old.get("dynamic", {}).get("connections", []):
            done.add((r["map"], -1 - r["connection"]))
        print(f"resuming: {len(done)} results already recorded", flush=True)

    play = make_playtest()
    start = time.time()
    processed = 0
    for name in names:
        data = catalog[name]
        for index, warp in enumerate(data.get("warp_events", [])):
            record = next(r for r in warp_records
                          if r["map"] == name and r["warp"] == index)
            if (name, index) in done:
                continue
            processed += 1
            if args.limit and processed > args.limit:
                break
            if any(f in name or f in (record.get("dest_name") or "")
                   for f in args.exclude):
                result = {"map": name, "warp": index, "class": record.get("class"),
                          "status": "UNTESTED", "src_xy": record["src_xy"],
                          "dest_map": record.get("dest_map"),
                          "dest_name": record.get("dest_name"),
                          "dest_xy": record.get("dest_xy"),
                          "mutual": record.get("mutual"),
                          "issues": ["untestable in the generic on-foot walk; "
                                     "excluded with --exclude"],
                          "static_issues": record.get("issues", [])}
            elif unloadable and (name in unloadable or
                                 (record.get("dest_name") in unloadable)):
                blocked = name if name in unloadable else record.get("dest_name")
                result = {"map": name, "warp": index, "class": record.get("class"),
                          "status": "UNTESTED", "src_xy": record["src_xy"],
                          "dest_map": record.get("dest_map"),
                          "dest_name": record.get("dest_name"),
                          "dest_xy": record.get("dest_xy"),
                          "mutual": record.get("mutual"),
                          "issues": [f"untestable: {blocked} cannot be loaded by the "
                                     f"engine (see load check)"],
                          "static_issues": record.get("issues", [])}
            elif record.get("class") in ("dynamic", "internal", "landing_anchor",
                                        "dynamic_return", "chained_landing",
                                        "nonreciprocal", "missing_target", "bad_index"):
                result = _attempt(play, name, index, record, catalog, by_id)
                if result["status"] in ("ISSUE", "ERROR", "PARTIAL") and \
                        any("no usable approach" in i or "INCONCLUSIVE" in i
                            for i in result.get("issues", []) + result.get("notes", [])):
                    # A stale field-script state can make warp injection fail.
                    # One clean reboot plus a retry separates that from a real
                    # data fault; a second failure is reported as-is.
                    if play.reboot_budget > 0:
                        play.reboot_budget -= 1
                        play.reboot()
                    retry = _attempt(play, name, index, record, catalog, by_id)
                    retry["retried_after_reboot"] = True
                    if retry["status"] in ("OK", "PARTIAL") or \
                            len(retry.get("issues", [])) < len(result.get("issues", [])):
                        result = retry
            else:
                result = {"map": name, "warp": index, "class": record.get("class"),
                          "status": "UNTESTED", "src_xy": record["src_xy"],
                          "dest_map": record.get("dest_map"),
                          "issues": [f"class {record.get('class')}"],
                          "static_issues": record.get("issues", [])}
            report["dynamic"]["warps"].append(result)
            if result["status"] != "OK":
                detail = list(result.get("issues", [])) + \
                    [f"(note) {n}" for n in result.get("notes", [])] + \
                    ([] if result.get("return_ok") in (True, None)
                     else ["return leg failed"])
                print(f"[{result['status']}] {name}[{index}] "
                      f"{result.get('src_xy')} -> {result.get('dest_name')}"
                      f"{result.get('dest_xy')}: {'; '.join(detail)}", flush=True)
            elif args.verbose:
                print(f"OK {name}[{index}] {result.get('src_xy')} -> "
                      f"{result.get('dest_name')}{result.get('dest_xy')} "
                      f"face={result.get('arrival_facing')}", flush=True)
            bad = play.health()
            if bad:
                report["dynamic"]["untested"].append({"after": [name, index], "reason": bad})
                print(f"!! rebooting after {name}[{index}]: {bad}", flush=True)
                if args.json:
                    args.json.write_text(json.dumps(report, indent=1) + "\n")
                play.reboot()
            if args.json and processed % 100 == 0:
                args.json.write_text(json.dumps(report, indent=1) + "\n")
                print(f"... {processed} warps, {time.time()-start:.0f}s", flush=True)
        if args.limit and processed > args.limit:
            break

    for name in names:
        data = catalog[name]
        for index, conn in enumerate(data.get("connections") or []):
            if (name, -1 - index) in done:
                continue
            record = next(r for r in conn_records
                          if r["map"] == name and r["connection"] == index)
            if (any(f in name or f in (record.get("dest_name") or "")
                    for f in args.exclude) or
                    (unloadable and (name in unloadable or
                                     record.get("dest_name") in unloadable))):
                report["dynamic"]["connections"].append(
                    {"map": name, "connection": index, "direction": conn["direction"],
                     "offset": conn["offset"], "dest_name": record.get("dest_name"),
                     "status": "UNTESTED", "legs": [],
                     "issues": ["untestable in the generic on-foot walk; excluded with --exclude" if
                                any(f in name or f in (record.get("dest_name") or "")
                                    for f in args.exclude) else
                                "untestable: the map (or its partner) cannot be loaded "
                                "by the engine (see load check)"]})
                continue
            elif unloadable and (name in unloadable or
                               (record.get("dest_name") in unloadable)):
                report["dynamic"]["connections"].append(
                    {"map": name, "connection": index, "direction": conn["direction"],
                     "offset": conn["offset"], "dest_name": record.get("dest_name"),
                     "status": "UNTESTED", "legs": [],
                     "issues": ["untestable: the map (or its partner) cannot be "
                                "loaded by the engine (see load check)"]})
                continue
            try:
                result = test_one_connection(play, name, index, conn, record,
                                            group_ids, catalog, layouts)
            except Exception as exc:
                result = {"map": name, "connection": index, "status": "ERROR",
                          "issues": [f"harness exception: {exc!r}"]}
            report["dynamic"]["connections"].append(result)
            if result["status"] != "OK":
                print(f"[{result['status']}] seam {name}[{index}] "
                      f"{conn['direction']}/{conn['offset']} -> {record.get('dest_name')}: "
                      f"{'; '.join(result.get('issues', []))}", flush=True)
            bad = play.health()
            if bad:
                report["dynamic"]["untested"].append({"after_seam": [name, index], "reason": bad})
                print(f"!! rebooting after seam {name}[{index}]: {bad}", flush=True)
                play.reboot()

    report["dynamic"]["reboots"] = play.reboots
    report["dynamic"]["elapsed_s"] = round(time.time() - start, 1)
    report["surf"]["granted"] = play.surf_kit
    report["surf"]["warps_walked_on_surf"] = sum(
        1 for r in report["dynamic"]["warps"]
        if r.get("via_surf") or r.get("approach_via_surf"))
    report["surf"]["returns_walked_on_surf"] = sum(
        1 for r in report["dynamic"]["warps"] if r.get("return_via_surf"))
    report["surf"]["seams_walked_on_surf"] = sum(
        1 for c in report["dynamic"]["connections"]
        for leg in c.get("legs", []) if leg.get("surf"))
    emit(report, args)


def load_check(args, report, layouts):
    """Boot once per map and check its live layout or intentional redirect.

    A broken map can leave the engine unable to change maps again, so each map
    is checked in its own fresh boot."""
    # This retired map stays registered for old saves. Its on-frame script
    # immediately sends the player to the active Mt. Moon 1F map.
    expected_redirects = {"MtMoon_Cave_hns": "MtMoon_1F_Frlg"}
    out = {}
    names = report["maps"]
    for n, name in enumerate(names):
        width, height = MAP_SIZES.get(name, (8, 8))
        xy = (min(2, max(0, width - 1)), min(2, max(0, height - 1)))
        geom = geometry(name, CATALOG)
        if geom is not None:
            # Some imported layouts use metatile 1023 as intentional solid
            # filler. Probing one of those tiles reports an unloaded grid even
            # when the engine copied the rest of the map correctly.
            candidates = ((x, y) for x in range(min(width, 128)) for y in range(min(height, 128))
                          if (geom.blocks[y * width + x] & 1023) != 1023)
            xy = min(candidates, key=lambda p: (
                (geom.blocks[p[1] * width + p[0]] >> 10) & 3 != 0,
                abs(p[0] - 2) + abs(p[1] - 2), p[1], p[0]), default=xy)
        play = make_playtest()
        rec = {"xy": list(xy), "ok": False, "why": ""}
        try:
            try:
                play.warp(name, xy[0], xy[1])
            except AssertionError:
                actual = MAP_NAMES.get((play.state()["group"], play.state()["num"]))
                if expected_redirects.get(name) != actual:
                    raise
                rec["redirected_to"] = actual
            play.frame(240)
            mh = play.symbol_address("gMapHeader")
            layout = play.core.memory.wram.u32[mh - 0x02000000]
            rec["layout_ptr"] = hex(layout)
            if not 0x08000000 <= layout < 0x0A000000:
                rec["why"] = (f"gMapHeader.mapLayout is {hex(layout)} after load "
                              f"(not a ROM pointer); the engine is dead")
            else:
                grid = play.mapgrid_info()
                rec["grid"] = [grid["width"], grid["height"]]
                probe_xy = xy
                if "redirected_to" in rec:
                    state = play.state()
                    probe_xy = (state["x"], state["y"])
                    rec["probe_xy"] = list(probe_xy)
                try:
                    mt = play.metatile_at(*probe_xy)[0]
                except Exception:
                    mt = None
                rec["metatile"] = mt
                if mt is None or mt == 1023:
                    rec["why"] = "block grid never filled (MAPGRID_UNDEFINED)"
                else:
                    st = play.state()
                    rec["state"] = [st["group"], st["num"], st["x"], st["y"]]
                    rec["ok"] = True
        except Exception as exc:
            rec["why"] = f"injection failed: {exc!r}"
        out[name] = rec
        del play
        if (n + 1) % 25 == 0:
            print(f"... load-check {n + 1}/{len(names)} "
                  f"({sum(1 for r in out.values() if not r['ok'])} failed)", flush=True)
    return out


def _attempt(play, name, index, record, catalog, by_id):
    try:
        return test_one_warp(play, name, index, record, catalog, by_id)
    except Exception as exc:  # keep going, record harness failures
        import traceback
        return {"map": name, "warp": index, "class": record.get("class"),
                "status": "ERROR",
                "issues": [f"harness exception: {exc!r}",
                           " <- ".join(l.strip() for l in
                                       traceback.format_exc().strip().splitlines()[-6:-1])],
                "src_xy": record["src_xy"], "dest_map": record.get("dest_map"),
                "dest_name": record.get("dest_name"), "dest_xy": record.get("dest_xy"),
                "shot": play.shot(f"{name}_{index}_error")}


def emit(report, args):
    if args.json:
        args.json.write_text(json.dumps(report, indent=1) + "\n")
        print(f"wrote {args.json}")
    dw = report["dynamic"]["warps"]
    dc = report["dynamic"]["connections"]
    print(f"maps={report['map_count']} static_warps={report['warp_count']} "
          f"static_seams={report['connection_count']}")
    if dw or dc:
        counts = {}
        for r in dw + dc:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        print("dynamic:", counts, f"elapsed={report['dynamic']['elapsed_s']}s "
              f"reboots={report['dynamic']['reboots']}")
    issues = [r for r in report["static"]["warps"] if r.get("issues")]
    print(f"static warp findings: {len(issues)}")
    for r in issues[:40]:
        print("  ", r["map"], r["warp"], r["src_xy"], "->", r.get("dest_name"), r["issues"])


if __name__ == "__main__":
    main()
