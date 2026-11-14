#!/usr/bin/env python3
"""Self-tests for the story-ordered region map and NPC classification.

Run directly; exits non-zero on failure.

    python3 plastic_ox/story/test_region.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "plastic_ox/wiki"))

import build_wiki  # noqa: E402
import npc_roles  # noqa: E402
import region  # noqa: E402
import story_notes  # noqa: E402

FAILURES: list[str] = []
DATA: dict | None = None


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        FAILURES.append(f"{name}{': ' + detail if detail else ''}")


def region_data() -> dict:
    global DATA
    if DATA is None:
        DATA = region.build_region_data(
            story_notes.load_notes(),
            build_wiki.read_script_blocks(),
            build_wiki.read_trainers(),
        )
    return DATA


def test_order() -> None:
    notes = story_notes.load_notes()
    slugs = [note.slug for note in notes]
    check("no duplicate story order", len(set(region.STORY_ORDER)) == len(region.STORY_ORDER))
    check("every note is ordered", set(slugs) <= set(region.STORY_ORDER), str(set(slugs) - set(region.STORY_ORDER)))
    check("no stale story order", set(region.STORY_ORDER) == set(slugs), str(set(region.STORY_ORDER) - set(slugs)))

    data = region_data()
    stops = data["stops"]
    check("61 stops", len(stops) == 61, str(len(stops)))
    check("40 mainline", data["counts"]["mainline"] == 40, str(data["counts"]))
    check("21 supporting", data["counts"]["supporting"] == 21, str(data["counts"]))
    check("first stop", stops[0]["slug"] == "pallet-town", stops[0]["slug"])
    check("last stop", stops[-1]["slug"] == "plasticox-whirlislands", stops[-1]["slug"])
    mainline = [stop["slug"] for stop in stops if stop["mainline"]]
    check("mainline starts at Pallet", mainline[0] == "pallet-town", mainline[0])
    check("mainline ends at the League", mainline[-1] == "indigoplateau-hns", mainline[-1])
    check(
        "Ecruteak before the tower",
        mainline.index("ecruteakcity-hns") < mainline.index("plasticox-burnedtower"),
    )
    check(
        "tower before its basement",
        mainline.index("plasticox-burnedtower") < mainline.index("plasticox-burnedtowerb1f"),
    )
    check(
        "Lavender before the underground",
        mainline.index("lavender-town") < mainline.index("route8-frlg"),
    )
    check(
        "Cinnabar before Mossdeep",
        mainline.index("cinnabarisland-frlg") < mainline.index("mossdeepcity"),
    )


def test_npc_split() -> None:
    stops = {stop["slug"]: stop for stop in region_data()["stops"]}
    ecruteak = stops["ecruteakcity-hns"]
    scripts = {row["script"] for row in ecruteak["key_npcs"] + ecruteak["standard_npcs"]}
    check("Ecruteak has NPCs", bool(scripts), str(len(scripts)))
    check("key and standard are disjoint",
          not {row["script"] for row in ecruteak["key_npcs"]} &
          {row["script"] for row in ecruteak["standard_npcs"]})
    check("gate watch is key",
          any(row["script"] == "EcruteakCity_EventScript_GateWatch" for row in ecruteak["key_npcs"]))
    check("burned guide is standard",
          any(row["script"] == "Pox_BurnedGuide" for row in ecruteak["standard_npcs"]))
    check("Morty is key",
          any(row["script"] == "Pox_Morty" or "MORTY" in row["name"] for row in ecruteak["key_npcs"]),
          str([row["name"] for row in ecruteak["key_npcs"]]))

    route29 = stops["route29-hns"]
    check("Route 29 trainers are key",
          {"PoxRouteTrainer_Route29", "PoxRouteTrainer_Route29Ella"} <=
          {row["script"] for row in route29["key_npcs"]})
    check("Route 29 talkers are standard",
          {"Route29_EventScript_Boy", "Route29_EventScript_Girl"} <=
          {row["script"] for row in route29["standard_npcs"]})

    forbidden = ("ITEM_BALL", "POKE_BALL", "CUTTABLE_TREE", "BREAKABLE_ROCK", "SIGN", "TOWN_MAP", "POKEDEX")
    for stop in stops.values():
        for row in stop["key_npcs"] + stop["standard_npcs"]:
            check("no item/terrain object in NPC list",
                  not any(marker in row["graphics"] for marker in forbidden),
                  row["graphics"])


def test_roles() -> None:
    stops = region_data()["stops"]
    key_rows = [row for stop in stops for row in stop["key_npcs"]]
    check("trainer role", any("Trainer battle" in row["roles"] for row in key_rows))
    check("gift role", any("Gift" in row["roles"] for row in key_rows))
    check("shop role", any("Shop" in row["roles"] for row in key_rows))
    check("heal role", any("Heal" in row["roles"] for row in key_rows))
    check("gate role", any("Path / gate" in row["roles"] for row in key_rows))
    check("state role", any("State-gated" in row["roles"] for row in key_rows))
    check("no empty key role", all(row["roles"] for row in key_rows))

    nurse = [row for row in key_rows if row["script"] == "Pox_Heal"]
    check("nurse is a healer", bool(nurse) and "Heal" in nurse[0]["roles"], str(nurse[:1]))
    route29 = [row for row in key_rows if row["script"] == "PoxRouteTrainer_Route29"]
    check("JOEY is a trainer", bool(route29) and "Trainer battle" in route29[0]["roles"])


def test_render() -> None:
    data = region_data()
    body = region.render_body(data)
    for needle in (
        'id="prev-stop"',
        'id="next-stop"',
        'id="skip-supporting"',
        'id="region-data"',
        'id="region-map-body"',
        'id="region-detail"',
        "<noscript>",
        "Physical design map (SVG)",
    ):
        check(f"region body has {needle}", needle in body)
    check("embedded stops", '"stops":' in body)
    js = (ROOT / "plastic_ox/wiki/assets/region.js").read_text(encoding="utf-8")
    for needle in ("aria-current", "prev-stop", "next-stop", "skip-supporting", "Key NPCs", "Standard NPCs"):
        check(f"region js has {needle}", needle in js)
    css = (ROOT / "plastic_ox/wiki/assets/region.css").read_text(encoding="utf-8")
    for needle in (".region-node", ".region-detail", ".region-table", "@media"):
        check(f"region css has {needle}", needle in css)


def test_built_page() -> None:
    with tempfile.TemporaryDirectory(prefix="pox-region-build-") as temporary:
        out = Path(temporary)
        build_wiki.build(out, "test-digest")
        page = (out / "ecruteakcity-hns.html").read_text(encoding="utf-8")
        check("built page has Key NPCs", "<h2>Key NPCs</h2>" in page)
        check("built page has Standard NPCs", "<h2>Standard NPCs</h2>" in page)
        check("built page keeps talk-only guide out of key list",
              "Burned Guide" in page and "Gate Watch" in page)
        region_page = (out / "region.html").read_text(encoding="utf-8")
        check("built region page", 'id="region-data"' in region_page and "id=\"prev-stop\"" in region_page)
        metadata = json.loads((out / "build.json").read_text(encoding="utf-8"))
        check("build metadata counts region stops", metadata.get("region_stops") == 61, str(metadata))
        check("built topology asset", (out / "assets/topology.svg").is_file())


def main() -> int:
    test_order()
    test_npc_split()
    test_roles()
    test_render()
    test_built_page()
    if FAILURES:
        print(f"{len(FAILURES)} region test failure(s):")
        for failure in FAILURES:
            print(f"  FAIL {failure}")
        return 1
    print("region tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
