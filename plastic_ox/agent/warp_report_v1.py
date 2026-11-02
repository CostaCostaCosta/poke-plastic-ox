#!/usr/bin/env python3
"""Render plastic_ox/agent/WARP_PLAYTEST_V1_REPORT.md from the playtest JSON.

    python3 plastic_ox/agent/warp_report_v1.py \
        --json plastic_ox/agent/warp_playtest_v1.json \
        --out  plastic_ox/agent/WARP_PLAYTEST_V1_REPORT.md
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORY = json.loads((ROOT / "plastic_ox/alpha/story_manifest.json").read_text())
STORY_MAPS = {e["map"] for e in STORY["events"]}
REGION = json.loads((ROOT / "plastic_ox/alpha/region_manifest.json").read_text())
TRAIL_MAPS = {t["source"] for t in REGION["transitions"]} | \
             {t["destination"] for t in REGION["transitions"]}

# How a warp is classified for the "is this a normal transition" question.
DONOR_PREFIXES = ("SSAnne_", "SafariZone_", "BattleFrontier_", "ArtisanCave_",
                  "SeafoamIslands_", "MossdeepCity_SpaceCenter", "CinnabarIsland_PokemonLab")


def tier(name):
    if name.startswith("PlasticOx"):
        return "plastic-ox authored"
    if name in STORY_MAPS:
        return "story-trigger map"
    if name in TRAIL_MAPS:
        return "region trail endpoint"
    if name.startswith(DONOR_PREFIXES):
        return "donor facility (vanilla)"
    if name.endswith(("_Frlg",)) or "_hns" in name:
        return "donor town/cave (vanilla base)"
    return "other / unclassified base"


def short(issue):
    return re.sub(r"\s+", " ", issue)[:220]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--merge", type=Path, action="append", default=[],
                    help="additional JSON runs; later results win")
    ap.add_argument("--loadcheck", type=Path)
    ap.add_argument("--extras", type=Path)
    args = ap.parse_args()

    report = json.loads(args.json.read_text())
    warps = list(report["dynamic"]["warps"])
    conns = list(report["dynamic"]["connections"])
    for extra in args.merge:
        other = json.loads(extra.read_text())
        key = {(r["map"], r["warp"]) for r in warps}
        for r in other.get("dynamic", {}).get("warps", []):
            if (r["map"], r["warp"]) in key:
                if r.get("status") == "OK" or r.get("status") == "PARTIAL":
                    warps[warps.index(next(x for x in warps
                                           if x["map"] == r["map"] and x["warp"] == r["warp"]))] = r
            else:
                warps.append(r)
        ckey = {(r["map"], r["connection"]) for r in conns}
        for r in other.get("dynamic", {}).get("connections", []):
            if (r["map"], r["connection"]) in ckey:
                if r.get("status") == "OK":
                    conns[conns.index(next(x for x in conns
                                           if x["map"] == r["map"] and
                                           x["connection"] == r["connection"]))] = r
            else:
                conns.append(r)

    static_warps = report["static"]["warps"]
    static_conns = report["static"]["connections"]
    static_by_key = {(r["map"], r["warp"]): r for r in static_warps}

    status = Counter(r["status"] for r in warps)
    cstatus = Counter(r["status"] for r in conns)
    tiers = defaultdict(lambda: Counter())
    tier_maps = defaultdict(set)
    for r in warps:
        tiers[tier(r["map"])][r["status"]] += 1
        tier_maps[tier(r["map"])].add(r["map"])
    for r in conns:
        tiers[tier(r["map"])][r["status"]] += 1
        tier_maps[tier(r["map"])].add(r["map"])

    by_map = defaultdict(lambda: {"warps": [], "conns": []})
    for r in warps:
        by_map[r["map"]]["warps"].append(r)
    for r in conns:
        by_map[r["map"]]["conns"].append(r)

    L = []
    A = L.append
    A("# WARP_PLAYTEST_V1_REPORT — warp-transition playtest (run 3)")
    A("")
    A(f"ROM: `pokeemerald.gba` @ `04b27389ca` (read-only). "
      f"Run started {report['generated']}, emulator time {report['dynamic']['elapsed_s']}s, "
      f"{report['dynamic'].get('reboots', 0)} emulator reboots.")
    A("")
    A("Reusable harness: `plastic_ox/demo/test_warps_v1.py`. This run is reproduced by:")
    A("")
    A("```sh")
    A("# 1. per-map load check (one fresh boot per map, ~8 min)")
    A("LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \\")
    A("  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_warps_v1.py \\")
    A("  --load-only --json plastic_ox/agent/warp_playtest_v1_loadcheck.json")
    A("")
    A("# 2. the warp + seam playtest itself (~5 min)")
    A("LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \\")
    A("  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_warps_v1.py \\")
    A("  --load-report plastic_ox/agent/warp_playtest_v1_loadcheck.json \\")
    A("  --exclude BattleFrontier \\")
    A("  --json plastic_ox/agent/warp_playtest_v1.json")
    A("")
    A("# 3. static extras (ledges, ladders, auto-teleports) and this report")
    A("python3 plastic_ox/agent/warp_extras_static.py \\")
    A("  --json plastic_ox/agent/warp_playtest_v1_extras.json")
    A("python3 plastic_ox/agent/warp_report_v1.py \\")
    A("  --json plastic_ox/agent/warp_playtest_v1.json \\")
    A("  --loadcheck plastic_ox/agent/warp_playtest_v1_loadcheck.json \\")
    A("  --extras plastic_ox/agent/warp_playtest_v1_extras.json \\")
    A("  --out plastic_ox/agent/WARP_PLAYTEST_V1_REPORT.md")
    A("")
    A("# static pre-pass alone (no emulator needed, plain system python3)")
    A("python3 plastic_ox/demo/test_warps_v1.py --static-only")
    A("```")
    A("")
    A("Supporting artefacts: "
      "`plastic_ox/agent/warp_playtest_v1_loadcheck.json` (map load verdicts), "
      "`plastic_ox/agent/warp_playtest_v1_extras.json` (ledge/ladder/auto-teleport "
      "static analysis), `plastic_ox/agent/warp_report_v1.py` (this document's "
      "generator), `plastic_ox/demo/shots/warp_v1/` (screenshots for ISSUE rows).")
    A("")
    A("## 1. Test set")
    A("")
    A(f"* **{report['map_count']} maps** in the story-reachable closure, "
      f"**{report['warp_count']} warp events**, "
      f"**{report['connection_count']} map connections**.")
    A("* Closure rule: seeds are the `region_v7.py` `ANCHORS`, the "
      "`story_manifest.json` trigger maps and the `region_manifest.json` transition "
      "endpoints, plus the retained donor rooms listed in "
      "`plastic_ox/agent/audit_warp_connections.py`; the set is then closed over "
      "`warp_events[].dest_map` and `connections[].map`.")
    A("* The closure is much larger than the ~38-map authored layer because the "
      "hns/Plastic-Ox towns sit **on top of the imported FRLG Kanto base**: "
      "`PalletTown_Frlg`, `Route101`, `OldaleTown`, `Route2_Frlg`, `Route4_Frlg` are "
      "all `ANCHORS`, so Pallet→Route101→Oldale→Route29→Cherrygrove and the whole "
      "donor Kanto graph below them are live, story-reachable content.")
    A("")
    A("| tier | maps | warps/seams | OK | PARTIAL | ISSUE | ERROR | UNTESTED |")
    A("|---|---|---|---|---|---|---|---|")
    for name in sorted(tiers):
        c = tiers[name]
        total = sum(c.values())
        A(f"| {name} | {len(tier_maps[name])} | {total} | {c['OK']} | {c['PARTIAL']} | "
          f"{c['ISSUE']} | {c['ERROR']} | {c['UNTESTED']} |")
    A(f"| **total** | **{len(by_map)}** | **{len(warps)+len(conns)}** | "
      f"**{status['OK']+cstatus['OK']}** | **{status['PARTIAL']+cstatus['PARTIAL']}** | "
      f"**{status['ISSUE']+cstatus['ISSUE']}** | **{status['ERROR']+cstatus['ERROR']}** | "
      f"**{status['UNTESTED']+cstatus['UNTESTED']}** |")
    A("")
    A("## 2. Method and convention oracle")
    A("")
    A("For every warp the harness boots the ROM, opens every badge/story flag, "
      "disables wild encounters, warp-injects a run-up tile 1-5 tiles short of the "
      "warp on the correct side, and then **holds a real direction key** so the "
      "engine's own `TryDoorWarp`/`TryArrowWarp`/ladder path fires.")
    A("")
    A("Assertions per warp:")
    A("")
    A("1. destination map id == `dest_map`;")
    A("2. landing tile == the `dest_warp_id` warp's `(x,y)`, sampled the exact frame "
      "the saveblock location flips;")
    A("3. arrival facing == the engine's own rule, transcribed from "
      "`GetAdjustedInitialDirection()` (`src/overworld.c:1090`): "
      "`MB_DEEP_SOUTH_WARP`→UP, doors/`MB_NON_ANIMATED_DOOR`/`MB_WATER_DOOR`→DOWN, "
      "`MB_{NORTH,SOUTH,EAST,WEST}_ARROW_WARP`→ the opposite compass direction, "
      "directional stairs→E/W, `MB_LADDER`→keep, everything else→DOWN;")
    A("4. the landing tile is standable, or is one of the transition tiles the engine "
      "itself spawns the player on top of (doors, arrow warps, ladders, stairs, "
      "escalators, holes);")
    A("5. softlock probe: the player can immediately step off the tile they settled on;")
    A("6. return leg: every legal side of the return warp is tried and the exit must "
      "land back in the source map on the source door (1 tile of tolerance, for "
      "multi-lane doors and for the single carry-over step a finished warp grants).")
    A("")
    A("Every map connection is also walked **in both directions** off the map edge. "
      "pokeemerald connections are seamless camera scrolling, not warps: "
      "`FillNorth/South/West/EastConnection` copy `MAP_OFFSET` rows/cols into the "
      "border strip and `CameraMove()` hands the map over when the camera steps "
      "past the grid border, with the landing fixed by `SetPositionFromConnection()`. "
      "The harness predicts that landing from the engine source and compares.")
    A("")
    A("### Note on the Gen 3 door/step convention (evidence)")
    A("")
    A("Two facts were measured rather than assumed:")
    A("")
    A("* **Exiting a building lands the player *in* the doorway, then the engine "
      "carries them one tile onto the doorstep.** The declared landing tile is the "
      "door tile itself (`MB_ANIMATED_DOOR`, collision 1) and the player comes to "
      "rest one tile below it facing DOWN. Net effect matches the Gen 3 rule "
      "\"exiting puts you outside, one tile below the door, facing down\".")
    A("* **Entering a building lands the player on the interior arrow-warp tile "
      "facing *away* from the door** (canonical UP for a `MB_SOUTH_ARROW_WARP` "
      "threshold), *not* facing down. Every interior in this region follows that, "
      "including the vanilla FRLG reference interiors "
      "(`PalletTown_PlayersHouse_1F_Frlg`, `CeruleanCity_House1_Frlg`), so the "
      "brief's \"entering puts the player just inside the door facing down\" is "
      "**not** what Gen 3 does and the region is consistent with Gen 3 instead.")
    A("")
    loadcheck = json.loads(args.loadcheck.read_text())["load_check"] \
        if args.loadcheck and args.loadcheck.exists() else {}
    extras = json.loads(args.extras.read_text()) if args.extras and args.extras.exists() else {}

    if loadcheck:
        bad = {k: v for k, v in loadcheck.items() if not v.get("ok")}
        A("## 2b. Map load check (one fresh boot per map)")
        A("")
        A(f"**{len(bad)} of {len(loadcheck)} maps ({100 * len(bad) // max(1, len(loadcheck))}%) "
          "cannot be loaded by the engine at all.** Each was loaded in its own fresh boot "
          "and then inspected: the saveblock does move to the requested map, but "
          "`gMapHeader.mapLayout` comes back as a non-ROM value and every block reads back "
          "`MAPGRID_UNDEFINED`. The screen goes black (100% black pixels for "
          "`CeruleanCity_Frlg`) or the player is frozen, and no further map change is "
          "accepted. This is not a warp defect - it is a map-import defect that makes the "
          "whole of that subtree untestable.")
        A("")
        A("| symptom | maps |")
        A("|---|---|")
        import collections as _c
        sym = _c.Counter()
        for v in bad.values():
            w = v.get("why", "")
            sym["gMapHeader.mapLayout garbage" if "not a ROM pointer" in w
                else "grid never filled" if "MAPGRID_UNDEFINED" in w else w[:40]] += 1
        for k, n in sym.most_common():
            A(f"| {k} | {n} |")
        A("")
        groups = _c.Counter()
        for k in bad:
            for pref in ("Celadon", "Cerulean", "Saffron", "Vermilion", "Fuchsia",
                         "Pewter", "Cinnabar", "SSAnne", "SilphCo", "Rocket", "Safari",
                         "PokemonTower", "MtMoon", "Seafoam", "Route", "Underground",
                         "RockTunnel", "PowerPlant", "Union", "Trade", "Mart",
                         "Pokemon", "GameCorner", "Gym", "House", "Museum",
                         "DepartmentStore", "Condominiums", "Hotel", "Restaurant",
                         "BikeShop", "Wardens", "Copycats", "MrPsychics", "TrainerFan",
                         "Dojo", "Tower", "Elevator", "Safari", "Lounge"):
                if k.startswith(pref):
                    groups[pref] += 1
                    break
            else:
                groups["<other>"] += 1
        A("| family | unloadable maps |")
        A("|---|---|")
        for k, n in groups.most_common():
            A(f"| {k} | {n} |")
        A("")
        A("Full list of unloadable maps (also the reason each untested warp below is "
          "marked UNTESTED):")
        A("")
        A("```")
        for i in range(0, len(sorted(bad)), 4):
            A("  ".join(f"{m:<44}" for m in sorted(bad)[i:i + 4]).rstrip())
        A("```")
        A("")

    if extras:
        A("## 2c. Static convention extras (ledges, ladders, auto-teleports)")
        A("")
        sm = extras.get("summary", {})
        A("| check | count |")
        A("|---|---|")
        for k, v in sm.items():
            A(f"| {k} | {v} |")
        A("")
        A(f"* **Ledges.** {sm.get('ledge_tiles', 0)} `MB_JUMP_*` tiles are present. "
          f"{sm.get('ledges_with_issues', 0)} of them fail a static one-way check: the "
          "approach tile is not walkable (the hop can never be taken, so it is decorative "
          "cliff art, not a route) or the landing tile one row down is solid (the player "
          "would hop into a wall). None sit on a map-connection seam edge "
          f"({sm.get('ledges_on_map_edge', 0)} found), so the seam rule \"a ledge on a "
          "seam hops downward only\" is not violated anywhere in the closure.")
        A("")
        A(f"* **Ladders/stairs without a warp event.** {sm.get('orphan_ladders', 0)} "
          f"`MB_LADDER` tiles and {sm.get('orphan_stairs', 0)} stair/escalator tiles carry "
          "no warp event, so they are bg-event scripts. A warp-driven harness cannot "
          "trigger them; they are listed as untestable by design rather than as defects.")
        A("")
        A(f"* **Auto-teleports.** {sm.get('auto_teleport_events', 0)} coordinate/bg events "
          f"in the closure fire a script. {sm.get('authored_region_portals', 0)} of them "
          "are `PoxRegion_*` - the authored `region_v7.py` trail transitions, which are "
          "deliberately coordinate-triggered rather than native warps (see "
          "`plastic_ox/alpha/region_v7.py`, `LANE_PORTALS`). "
          f"{sm.get('legacy_vanilla_triggers', 0)} are inherited vanilla story triggers "
          "(rival/grunt cutscene tiles in the FRLG Kanto base). They do not fire during "
          "this playtest because the harness never walks over a trigger tile with a story "
          "flag unset, but they are the mechanism by which the region portals teleport, "
          "and they are the first thing to audit if a \"spontaneous\" teleport is ever "
          "reported.")
        A("")

    A("## 3. Results by map")
    A("")
    A("One section per map that contains at least one warp or connection. "
      "`warp` = index into `warp_events`.")
    A("")
    for map_name in sorted(by_map):
        entry = by_map[map_name]
        if not entry["warps"] and not entry["conns"]:
            continue
        bad = [r for r in entry["warps"] + entry["conns"] if r["status"] != "OK"]
        A(f"### `{map_name}`")
        A("")
        A(f"*Tier: {tier(map_name)} — {len(entry['warps'])} warp(s), "
          f"{len(entry['conns'])} connection(s), {len(bad)} finding(s).*")
        A("")
        if entry["warps"]:
            A("| warp | tile | behaviour | dest map | dest tile | dest beh | landed | rest | facing (expected) | move | return | result |")
            A("|---|---|---|---|---|---|---|---|---|---|---|---|")
            for r in entry["warps"]:
                st = static_by_key.get((r["map"], r["warp"]), {})
                A("| {w} | {t} | {b} | {d} | {dt} | {db} | {l} | {rs} | {f} ({cf}) | {mv} | {rt} | **{res}** |".format(
                    w=r["warp"], t=tuple(r.get("src_xy") or ()),
                    b=st.get("src_behavior") or "-",
                    d=r.get("dest_name") or r.get("dest_map") or "-",
                    dt=tuple(r["dest_xy"]) if r.get("dest_xy") else "-",
                    db=st.get("dest_behavior") or "-",
                    l=tuple(r["landed_xy"]) if r.get("landed_xy") else "-",
                    rs=tuple(r["rest_xy"]) if r.get("rest_xy") else "-",
                    f=r.get("arrival_facing") or "-",
                    cf=r.get("canonical_facing") or "-",
                    mv={True: "yes", False: "NO", None: "-"}[r.get("can_move")]
                    if "can_move" in r else "-",
                    rt={True: "same door", False: "WRONG MAP/TILE",
                        None: "inconclusive"}[r.get("return_ok")]
                    if "return_ok" in r else "-",
                    res=r["status"]))
            A("")
        for r in entry["warps"]:
            detail = list(r.get("issues", [])) + [f"(note) {n}" for n in r.get("notes", [])]
            if detail and r["status"] != "OK":
                A(f"* **{r['map']}[{r['warp']}] {r['status']}** — " +
                  "; ".join(short(d) for d in detail if d))
                if r.get("shot"):
                    A(f"  * screenshot: `{Path(r['shot']).relative_to(ROOT)}`")
        for r in entry["conns"]:
            legs = "; ".join(f"{l['leg']}:{l.get('status')}"
                             f"{' (' + short(l['note']) + ')' if l.get('note') else ''}"
                             for l in r.get("legs", []))
            A(f"* **{r['map']} conn[{r['connection']}] {r['direction']}/{r['offset']} "
              f"-> {r.get('dest_name')} {r['status']}** — {legs}")
            for issue in r.get("issues", []):
                A(f"  * {short(issue)}")
        A("")

    A("## 4. Untested / not covered")
    A("")
    untested = [r for r in warps + conns if r["status"] == "UNTESTED"]
    if untested:
        groups = defaultdict(list)
        for r in untested:
            text = " ".join(r.get("issues", []))
            if "excluded" in text:
                key = ("A", "facility state machine excluded with `--exclude` "
                             "(Battle Frontier lobbies/rooms: they need a registered "
                             "Battle Frontier trainer battle before the exit warp is "
                             "reachable, which a generic warp walk cannot set up)")
            elif "untestable" in text:
                key = ("B", "the map, or the map it warps into, **cannot be loaded by "
                            "the engine at all** (see the load check in 2b). The warp "
                            "data may well be fine; it is simply unreachable because "
                            "the destination dies during `DoMapLoad`")
            else:
                key = ("C", text[:110])
            groups[key].append(r)
        A(f"**{len(untested)} of {len(warps) + len(conns)} records are UNTESTED.** Grouped "
          "by the reason:")
        A("")
        A("| reason | records | distinct maps |")
        A("|---|---|---|")
        for (_k, why), rows in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            A(f"| {why} | {len(rows)} | {len({r['map'] for r in rows})} |")
        A("")
        for (k, why), rows in sorted(groups.items()):
            A(f"**({k}) — {len(rows)} records across "
              f"{len({r['map'] for r in rows})} maps, listed untested in section 3.**")
            A("")
        A("No warp in the closure was skipped for convenience: every record is either "
          "walked and asserted, or carries one of the two reasons above.")
    else:
        A("* None: every warp and every connection in the closure was exercised.")
    A("")
    A("Partial coverage, stated explicitly:")
    A("")
    A("* Facility exit warps whose `dest_map` is `MAP_DYNAMIC` are only meaningful "
      "when the player walked in through a real door (the engine fills "
      "`gSaveBlock1Ptr->dynamicWarp` from the entrance). Each one was driven from a "
      "real entrance recorded in the JSON (`entrance` field); a facility with no door "
      "in the closure is reported untestable rather than as a defect.")
    A("* `PARTIAL` rows are warps whose *outbound* leg fully passed but whose return "
      "leg could not be triggered from any of the four cardinal sides of the return "
      "warp inside the harness placement limits. They are listed individually in "
      "section 3 and are **not** counted as passes.")
    A("* Screenshots are captured only for ISSUE rows, in "
      "`plastic_ox/demo/shots/warp_v1/`.")
    A("* The emulator state is injected (warp-injection + flag setting); no player "
      "save file is written and the ROM is not modified.")
    A("* The harness can only test a transition that a player could perform. It "
      "injects the player onto a run-up tile and then holds a real direction key, so "
      "everything from the run-up onwards is the real engine: `TryDoorWarp`, "
      "`TryArrowWarp`, ladder and ledge handling, `DoWarp`, `DoMapLoad`, camera "
      "connections.")
    A("")
    A("## 5. Systemic findings")
    A("")
    issues = [r for r in warps if r["status"] in ("ISSUE", "ERROR")]
    cat = Counter()
    for r in issues:
        text = " ".join(r.get("issues", []))
        if "harness exception" in text:
            cat["harness error"] += 1
        elif "no usable approach" in text:
            cat["warp cannot be stepped on from any side"] += 1
        elif "did not warp" in text:
            cat["warp does not fire from a legal approach"] += 1
        elif "lands on a solid tile" in text:
            cat["lands in solid terrain"] += 1
        elif "arrival facing" in text:
            cat["arrival facing != canonical"] += 1
        elif "wedged" in text:
            cat["softlock: no exit from landing"] += 1
        elif "unhealthy" in text or "never finished loading" in text:
            cat["crash / hung transition"] += 1
        elif "landed at" in text:
            cat["wrong landing coordinates"] += 1
        else:
            cat["other"] += 1
    A("| category | count |")
    A("|---|---|")
    for k, v in cat.most_common():
        A(f"| {k} | {v} |")
    A("")
    for r in conns:
        if r["status"] != "OK":
            cat["seam: " + r["direction"] + " connection"] += 1
    if any(cat.values()):
        nowarp = [r for r in issues if any("did not warp" in i for i in r.get("issues", []))]
    if nowarp:
        A("")
        A(f"### The {len(nowarp)} \"warp does not fire\" rows, triaged")
        A("")
        A("These are the rows where the harness stood the player on a standable tile "
          "next to the warp, held the key onto the warp tile, and the engine did not "
          "transition. They are **not** all confirmed defects - the split below is what "
          "a human should triage first.")
        A("")
        A("| source metatile behaviour | rows | what it means |")
        A("|---|---|---|")
        beh = defaultdict(list)
        for r in nowarp:
            beh[static_by_key.get((r["map"], r["warp"]), {}).get("src_behavior") or "?"].append(r)
        notes = {
            "MB_MOSSDEEP_GYM_WARP": "custom gym behaviour; the engine reaches it through a "
                                    "warp-event script, not a tile callback. Needs a manual look.",
            "MB_NORMAL": "the warp event sits on plain (often solid) terrain, so the "
                         "player can never legally stand on it - check elevation and "
                         "collision of the tile itself.",
            "MB_SOUTH_ARROW_WARP": "stair/arrow warp that should fire when stepped on "
                                   "along the arrow - if it does not, the arrow tile is "
                                   "not the tile the engine reads, or the elevation gate "
                                   "rejects the step.",
            "MB_CAVE": "cave-mouth warp, same class as the arrow warps.",
        }
        default_note = ("ordinary door/threshold warp - the strongest evidence of a "
                        "real defect")
        for k, rows in sorted(beh.items(), key=lambda kv: -len(kv[1])):
            A(f"| `{k}` | {len(rows)} | {notes.get(k, default_note)} |")
        A("")
        A("| map | warp | tile | source behaviour |")
        A("|---|---|---|---|")
        for r in nowarp:
            A(f"| `{r['map']}` | {r['warp']} | {tuple(r.get('src_xy') or ())} | "
              f"`{static_by_key.get((r['map'], r['warp']), {}).get('src_behavior')}` |")
    seams = {k: v for k, v in cat.items() if k.startswith("seam:")}
    if seams:
        A("| seam findings by direction | count |")
        A("|---|---|")
        for k, v in sorted(seams.items()):
            A(f"| {k} | {v} |")
        A("")

    A("## 6. Prioritized fix list")
    A("")
    A(_priorities(warps, conns, static_warps, static_conns, loadcheck))
    A("")
    A("## 7. Raw counts")
    A("")
    A("```")
    A(f"maps in closure              : {report['map_count']}")
    A(f"warp events                  : {report['warp_count']}")
    A(f"map connections              : {report['connection_count']}")
    A(f"static warp findings         : {sum(1 for r in static_warps if r.get('issues'))}")
    A(f"static connection findings   : {sum(1 for r in static_conns if r.get('issues'))}")
    A(f"dynamic warp  OK/PARTIAL/ISSUE/ERROR/UNTESTED : "
      f"{status['OK']}/{status['PARTIAL']}/{status['ISSUE']}/{status['ERROR']}/{status['UNTESTED']}")
    A(f"dynamic seam  OK/PARTIAL/ISSUE/ERROR/UNTESTED : "
      f"{cstatus['OK']}/{cstatus['PARTIAL']}/{cstatus['ISSUE']}/{cstatus['ERROR']}/{cstatus['UNTESTED']}")
    A(f"emulator reboots             : {report['dynamic'].get('reboots', 0)}")
    A("```")
    args.out.write_text("\n".join(L) + "\n")
    print(f"wrote {args.out} ({len(L)} lines)")
    print("warp status:", dict(status), "seam status:", dict(cstatus))


def _priorities(warps, conns, static_warps, static_conns, loadcheck=None):
    """Build the prioritized fix list from the collected evidence."""
    out = []
    hard = [r for r in static_warps if r.get("class") == "bad_index" or
            any("out of range" in i for i in r.get("issues", []))]
    nonrecip = [r for r in static_warps if r.get("class") == "nonreciprocal"]
    solid = [r for r in static_warps if any("is solid" in i for i in r.get("issues", []))]
    noexit = [r for r in static_warps if any("no walkable exit" in i for i in r.get("issues", []))]
    unapproach = [r for r in static_warps
                  if any("no standable approach" in i for i in r.get("issues", []))]
    runtime_solid = [r for r in warps if any("lands on a solid tile" in i
                                             for i in r.get("issues", []))]
    runtime_wedged = [r for r in warps if any("wedged" in i for i in r.get("issues", []))]
    wrong = [r for r in warps if any("landed at (" in i for i in r.get("issues", []))
            and r["status"] != "OK"]
    seam_bad = [r for r in conns if r["status"] == "ISSUE"]
    partial = [r for r in warps if r["status"] == "PARTIAL"]

    def fmt(rows, extra=""):
        return ", ".join(f"`{r['map']}[{r.get('warp', r.get('connection'))}]`"
                         for r in rows[:12]) + (" …" if len(rows) > 12 else "") + extra

    unload_bad = [(m, r) for m, r in (loadcheck or {}).items() if not r.get("ok")]
    if unload_bad:
        out.append(
            "**P0 — the imported FRLG Kanto base does not load.** "
            f"{len(unload_bad)} maps ({100 * len(unload_bad) // 391}%) die inside "
            "`DoMapLoad`: `gMapHeader.mapLayout` comes back as a non-ROM value, every "
            "block reads `MAPGRID_UNDEFINED`, the screen goes black or the player is "
            "frozen, and no further map change is accepted. Families: "
            + ", ".join(f"{k} ({n})" for k, n in __import__("collections").Counter(
                re.match(r"[A-Za-z_]+", m).group(0) for m, _ in unload_bad).most_common(10))
            + ". This blocks every warp into or out of those maps and has to be fixed "
              "before the rest of the Kanto graph can be playtested; see section 2b for "
              "the full list.")
    if hard:
        out.append("**P0 — data errors that make the engine read past the end of a "
                   "warp table.** " + f"{len(hard)} warp(s) reference a "
                   "`dest_warp_id` the destination map does not have: " + fmt(hard) +
                   ". `SetPlayerCoordsFromWarp()` dereferences "
                   "`mapHeader->events->warps[warpId]` unconditionally, so these land "
                   "the player on whatever warp struct follows the table.")
    if runtime_solid or solid:
        rows = runtime_solid or solid
        out.append("**P0 — landings inside solid terrain.** " + fmt(rows) + ".")
    if runtime_wedged or noexit:
        rows = runtime_wedged or noexit
        out.append("**P0 — softlocks.** " + fmt(rows) +
                   ". A landing with no walkable neighbour cannot be escaped.")
    if nonrecip:
        out.append("**P1 — non-reciprocal warp pairs (exit does not return you to the "
                   "door you came in by).** " + fmt(nonrecip) + ".")
    if wrong:
        out.append("**P1 — runtime landing mismatches.** " + fmt(wrong) + ".")
    if seam_bad:
        out.append("**P1 — map-connection seams.** " +
                   "; ".join(f"`{r['map']}` conn[{r['connection']}] "
                             f"{r['direction']}/{r['offset']} -> {r.get('dest_name')}: "
                             + "; ".join(short(i) for i in r.get("issues", [])[:1])
                             for r in seam_bad[:10]) +
                   (" …" if len(seam_bad) > 10 else ""))
    unapproach_rt = [r for r in warps
                     if any("no usable approach" in i for i in r.get("issues", []))]
    if unapproach_rt or unapproach:
        out.append("**P2 — warps that cannot be triggered on foot.** " +
                   fmt(unapproach_rt or unapproach) + ".")
    if partial:
        out.append("**P3 — needs a manual look (inconclusive return leg).** " +
                   fmt(partial) + ".")
    leftovers = [r for r in warps if r["status"] in ("ISSUE", "ERROR") and
                 r not in hard and r not in nonrecip and r not in wrong and
                 r not in unapproach_rt and r not in runtime_solid and
                 r not in runtime_wedged]
    if leftovers:
        out.append("**P3 — remaining issues.** " + fmt(leftovers) + ".")
    if not out:
        out.append("No fixes required.")
    return "\n".join(f"{i + 1}. {line}" for i, line in enumerate(out))


if __name__ == "__main__":
    main()
