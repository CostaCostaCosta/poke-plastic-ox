from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets" / "images"
OUT = ROOT / "parts_catalog.json"

# Route inventory from the project's Gen I-III route inventory.
ROUTE_ROWS = r'''region,generation,route,ports,shape,traversal,theme,status,notes
Kanto,1,1,N/S,vertical,land,starter meadow; grass and ledges,filler,
Kanto,1,2,N/S,vertical,land,forest-edge corridor; Ilex Forest and Dark Cave,story-route,Replaces Route 1 / Route 31 / Route 104 Top. South reaches Cherrygrove; north reaches Rustboro. Two forest gatehouses lead to Ilex; the former Diglett mouth leads to Dark Cave. Cut trees retain the native eastern shortcut.
Kanto,1,3,E/W,horizontal,land,rocky foothills; trainer-heavy open road,filler,
Kanto,1,4,E/W,horizontal,land,mountain plateau; Mt. Moon exit,avoid,split by Mt. Moon in source
Kanto,1,5,N/S,vertical,land,suburban slope; daycare,filler,
Kanto,1,6,N/S,vertical,land,urban meadow; water and gate approach,filler,
Kanto,1,7,E/W,horizontal,land,short urban connector; Saffron/Celadon gate,filler,
Kanto,1,8,E/W,horizontal,land,fenced grass; urban gate; Underground Path,filler,
Kanto,1,9,E/W,horizontal,land,rocky ledges and eastern highland,filler,
Kanto,1,10,N/S,vertical,mixed,river canyon; Rock Tunnel/Power Plant,dark-port,candidate Kanto Dark Cave mouth
Kanto,1,11,N/E/W,3-way,land,grassland gate route; Diglett's Cave,filler,
Kanto,1,12,N/W/S,3-way,mixed,bridge/coast/fishing corridor,story-junction,Lavender south junction
Kanto,1,13,E/W,horizontal,land,fence maze and coastal grass,filler,
Kanto,1,14,N/S,vertical,land,narrow fenced north-south route,filler,
Kanto,1,15,E/W,horizontal,land,broad fenced grassland,filler,
Kanto,1,16,E/W,horizontal,land,Cycling Road gateway; overlook,filler,
Kanto,1,17,N/S,vertical,land,long Cycling Road descent,filler,
Kanto,1,18,E/W,horizontal,land,short Cycling Road exit,filler,
Kanto,1,19,N/S,vertical,mixed,beach-to-ocean transition,filler,
Kanto,1,20,E/W,horizontal,water,open sea; Seafoam corridor,avoid,Whirl Islands replace Seafoam in current concept
Kanto,1,21,N/S,vertical,water,Pallet-Cinnabar coastal water,story,continuity loop
Kanto,1,22,E/W,horizontal,land,western meadow; rival/League gate,filler,
Kanto,1,23,N/S,vertical,land,badge-gate League approach,league,candidate League approach
Kanto,1,24,N/S,vertical,mixed,Nugget Bridge; river and trainers,story,Sea Cottage approach
Kanto,1,25,E/W,horizontal,land,cape road; trainer gauntlet,story,Sea Cottage destination
Kanto,1,26,N/S,vertical,land,wooded late-game mountain road,filler,
Kanto,1,27,E/W,horizontal,mixed,Tohjo Falls river/coast transition,filler,
Kanto,1,28,E/W,horizontal,land,mountain meadow; Mt. Silver approach,filler,
Johto,2,29,N/E/W,3-way,land,starter grassland; ledges and branching,filler,
Johto,2,30,N/S,vertical,land,wooded stream; berry houses,filler,
Johto,2,31,S/W,elbow,land,grassland junction; cave mouth,filler,
Johto,2,32,N/E/S,3-way,mixed,long coastal road; fishing; ruins/cave approaches,filler,
Johto,2,33,W,horizontal,land,short rainy valley; Union Cave exit,filler,
Johto,2,34,N/S,vertical,land,open grassland; daycare,filler,
Johto,2,35,N/S,vertical,land,city fringe; National Park gate,filler,
Johto,2,36,N/E/S/W,4-way,land,four-way wooded junction; ruins/Sudowoodo,filler,
Johto,2,37,N/S,vertical,land,short wooded apricorn route,filler,
Johto,2,38,E/W,horizontal,land,farm meadow and gentle rolling road,filler,
Johto,2,39,N/S,vertical,land,ranch/coastal approach,filler,
Johto,2,40,N/S,vertical,water,open sea south of Olivine,filler,
Johto,2,41,E/W,horizontal,water,whirlpool ocean; island maze,story,Whirl Islands host route
Johto,2,42,N/E/W,3-way,mixed,mountain lakes; Mt. Mortar mouths,dark-port,candidate Johto Dark Cave mouth
Johto,2,43,N/S,vertical,land,lake road; checkpoint/toll identity,filler,
Johto,2,44,E/W,horizontal,mixed,ponds and Ice Path approach,filler,
Johto,2,45,N/S,vertical,land,steep mountain ledges; downhill route,filler,
Johto,2,46,N/S,vertical,land,foothills and one-way ledges,filler,
Hoenn,3,101,N/S,vertical,land,starter woodland and simple grass,filler,
Hoenn,3,102,E/W,horizontal,land,farm route; pond and early grass,filler,
Hoenn,3,103,E/S,elbow,mixed,coastal/river elbow; early rival route,filler,
Hoenn,3,104,N/E/S,3-way,mixed,beach + forest-edge transition,story-adapter,excellent land-to-water adapter
Hoenn,3,105,N/S,vertical,water,coastal channels and small islands,filler,
Hoenn,3,106,N/S,vertical,water,island coast; Granite Cave access,filler,
Hoenn,3,107,E/W,horizontal,water,open sea,filler,
Hoenn,3,108,E/W,horizontal,water,open sea; Abandoned Ship,filler,
Hoenn,3,109,N/W,elbow,mixed,beach resort coast,filler,
Hoenn,3,110,N/W/S,3-way,mixed,cycling road; river; urban corridor,story,New Mauville host route
Hoenn,3,111,N/W/S,3-way,land,desert-edge highway; rocky junction,filler,excellent 3-way adapter
Hoenn,3,112,E/W,horizontal,land,volcanic foothills; Fiery Path/Jagged Pass,filler,
Hoenn,3,113,E/W,horizontal,land,ash-covered fields; distinctive visual biome,filler,
Hoenn,3,114,E/S,elbow,mixed,river/falls/mountain meadow,filler,
Hoenn,3,115,N/S,vertical,mixed,beach cliffs; Meteor Falls mouth,filler,
Hoenn,3,116,E/W,horizontal,land,rocky grass; Rusturf Tunnel mouth,dark-port,candidate Hoenn Dark Cave mouth
Hoenn,3,117,E/W,horizontal,land,flower meadow; daycare,filler,
Hoenn,3,118,N/E/W,3-way,mixed,river crossing; strong 3-way junction,filler,
Hoenn,3,119,E/S,elbow,mixed,rain; tall grass; river; Weather Institute,story,Weather Institute host route
Hoenn,3,120,N/S,vertical,mixed,rainforest bridges; Scorched Slab,filler,
Hoenn,3,121,N/E/S,3-way,mixed,Safari grassland; coast junction,filler,
Hoenn,3,122,N/S,vertical,water,river around Mt. Pyre,filler,
Hoenn,3,123,N/W,elbow,land,berry route; ledges and farmland,filler,
Hoenn,3,124,E/W/S,3-way,water,open ocean; reefs and Dive,story,Mossdeep approach
Hoenn,3,125,N/S,vertical,water,cold ocean; Shoal Cave,filler,
Hoenn,3,126,N/E,elbow,water,circular ocean; Dive; Sootopolis basin,story,Mossdeep water elbow
Hoenn,3,127,N/W/S,3-way,water,open ocean; Dive; 3-way sea junction,filler,
Hoenn,3,128,N/E/S,3-way,water,open ocean; Seafloor Cavern/League side,filler,
Hoenn,3,129,N/W,elbow,water,wide open ocean,filler,
Hoenn,3,130,E/W,horizontal,water,open ocean; Mirage Island,filler,
Hoenn,3,131,E/W,horizontal,water,open ocean; Sky Pillar,filler,
Hoenn,3,132,E/W,horizontal,water,westbound current route,filler,
Hoenn,3,133,E/W,horizontal,water,westbound current route,filler,
Hoenn,3,134,E/W,horizontal,water,westbound current route; Sealed Chamber,filler,
'''

STORY_REQUIRED_ROUTE_IDS = {"R2", "R35", "R36", "R37", "R41", "R119"}
STORY_LINKED_OPTIONAL_ROUTE_IDS = {"R21", "R24", "R25"}

# Physical transition types at source-route endpoints. These are separate
# from progression gates such as badges or story flags.
# A cave mouth or gatehouse replaces the corresponding seamless map edge in
# the high-level topology. The direction is therefore removed and represented
# below as a typed transition endpoint.
ROUTE_PORT_REMOVALS = {
    "R3": {"E"},
    "R4": {"W"},
    "R5": {"S"},
    "R6": {"N"},
    "R7": {"E"},
    "R8": {"W"},
    "R15": {"W"},
    "R19": {"N"},
    "R35": {"N", "S"},
    "R36": {"W"},
    "R44": {"E"},
}

# Additional route-local cave mouths. Unlike facility/building warps, these
# count as regional endpoints when routes are classified in the editor.
ROUTE_TRANSITION_PORTS = {
    "R2": [("DARK", "Dark Cave", "cave"), ("ILEX_SOUTH", "Ilex South Gate", "gate"), ("ILEX_NORTH", "Ilex North Gate", "gate")],
    "R10": [("ROCK", "Rock Tunnel", "cave")],
    "R11": [("DIGLETT", "Diglett's Cave", "cave")],
    "R3": [("MT_MOON", "Mt. Moon", "cave")],
    "R4": [("MT_MOON", "Mt. Moon", "cave")],
    "R5": [("SAFFRON", "Saffron Gate", "gate")],
    "R6": [("SAFFRON", "Saffron Gate", "gate")],
    "R7": [("SAFFRON", "Saffron Gate", "gate")],
    "R8": [("SAFFRON", "Saffron Gate", "gate")],
    "R15": [("R15_WEST_GATE", "Route 15 West Gate", "gate")],
    "R19": [("R19_NORTH_GATE", "Route 19 North Gate", "gate")],
    "R31": [("DARK", "Dark Cave", "cave")],
    "R32": [("UNION", "Union Cave", "cave")],
    "R33": [("UNION", "Union Cave", "cave")],
    "R35": [("GOLDENROD", "Goldenrod Gate", "gate"), ("PARK", "National Park Gate", "gate")],
    "R36": [("PARK", "National Park Gate", "gate")],
    "R42": [("MORTAR_W", "Mt. Mortar West", "cave"), ("MORTAR_E", "Mt. Mortar East", "cave"), ("MORTAR_C", "Mt. Mortar Center", "cave")],
    "R44": [("ICE_PATH", "Ice Path", "cave")],
    "R45": [("DARK", "Dark Cave", "cave")],
    "R46": [("DARK", "Dark Cave", "cave")],
    "R106": [("GRANITE", "Granite Cave", "cave")],
    "R112": [("FIERY_W", "Fiery Path West", "cave"), ("FIERY_E", "Fiery Path East", "cave")],
    "R115": [("METEOR", "Meteor Falls", "cave")],
    "R116": [("RUSTURF", "Rusturf Tunnel", "cave")],
    "R120": [("SCORCHED", "Scorched Slab", "cave")],
    "R125": [("SHOAL", "Shoal Cave", "cave")],
}

# v0.6.1 required towns and their source-map ports.
TOWNS = [
    dict(id="PAL", name="Pallet Town", region="Kanto", kind="town", ports={"N":"land", "S":"water"}, asset="PAL.png", required=True, story_order=1, notes="Start. North land; south water continuity route."),
    dict(id="CHERRY", name="Cherrygrove City", region="Johto", kind="town", ports={"N":"land", "E":"land", "W":"water"}, asset="CHERRY.png", required=True, story_order=2, notes="Two native land seams plus natural west coast."),
    dict(id="RUST", name="Rustboro City", region="Hoenn", kind="town", ports={"N":"land", "E":"land", "S":"land"}, asset="RUST.png", required=True, story_order=4, notes="High-value three-port land city."),
    dict(id="GOLD", name="Goldenrod City", region="Johto", kind="town", ports={"N":"gate", "S":"land"}, special_ports=[{"id":"TRAIN","label":"Train","type":"transit"}], asset="GOLD.png", required=True, story_order=6, notes="North/south overworld; Magnet Train is a late transit edge."),
    dict(id="ECRU", name="Ecruteak City", region="Johto", kind="town", ports={"E":"gate", "S":"land", "W":"gate"}, special_ports=[{"id":"BURNED","label":"Burned Tower","type":"warp"}], asset="ECRU.png", required=True, story_order=8, notes="East and west use gatehouses; south is a land seam; north is reserved for Bell Tower context."),
    dict(id="FORT", name="Fortree City", region="Hoenn", kind="town", ports={"E":"land", "W":"land"}, asset="FORT.png", required=True, story_order=10, notes="Clean east-west pass-through town."),
    dict(id="LAV", name="Lavender Town", region="Kanto", kind="town", ports={"N":"land", "S":"land", "W":"land"}, special_ports=[{"id":"PKTOWER","label":"Pokémon Tower","type":"warp"}], asset="LAV.png", required=True, story_order=12, notes="Three useful land ports."),
    dict(id="CINN", name="Cinnabar Island", region="Kanto", kind="town", ports={"N":"water", "E":"water"}, special_ports=[{"id":"MANSION","label":"Mansion","type":"warp"}], asset="CINN.png", required=True, story_order=13, notes="Island. Use only proven north/east water seams."),
    dict(id="MOSS", name="Mossdeep City", region="Hoenn", kind="town", ports={"N":"water", "S":"water", "W":"water"}, asset="MOSS.png", required=True, story_order=15, notes="Three proven water seams; no invented east exit."),
    dict(id="SAFF", name="Saffron City", region="Kanto", kind="town", ports={"N":"gate", "E":"gate", "S":"gate", "W":"gate"}, special_ports=[{"id":"TRAIN","label":"Train","type":"transit"},{"id":"SILPH","label":"Silph","type":"warp"},{"id":"DOJO","label":"Dojo","type":"warp"}], asset="SAFF.png", required=True, story_order=16, notes="Use all four gatehouse ports when possible; late-game gating is encouraged."),
    dict(id="BLACK", name="Blackthorn City", region="Johto", kind="town", ports={"N":"cave", "S":"land"}, port_labels={"N":"Dragon's Den", "S":"Route 45"}, special_ports=[{"id":"ICE_PATH","label":"Ice Path","type":"cave","regional":True}], asset="BLACK.png", required=True, story_order=17, notes="North opens to the Dragon's Den cave; the explicit Ice Path cave link remains available; south descends to Route 45."),
    dict(id="OLDALE", name="Oldale Town", region="Hoenn", kind="town", ports={"N":"land", "S":"land", "W":"land"}, asset="OLDALE.png", required=False, notes="Optional Hoenn starter-area town. South connects to Route 101; west to Route 102; north to Route 103."),
    dict(id="PACIF", name="Pacifidlog Town", region="Hoenn", kind="town", ports={"E":"water", "W":"water"}, asset="PACIF.png", required=False, notes="Optional Hoenn water town on the southern ocean. West connects to Route 131; east to Route 132."),
]

# Required non-town story areas. Some are landmarks/facilities rather than literal caves.
REQUIRED_DUNGEONS = [
    dict(id="ILEX", name="Ilex Forest", region="Johto", kind="dungeon", subtype="forest", ports={"N":"gate", "E":"gate"}, asset="ILEX.png", required=True, story_order=3, notes="Mandatory pre-Roxanne exploration. North gate returns to Route 2 north after the Ilex objective; the native east-facing lower exit joins Route 2 south through its south gatehouse. Replaces Viridian Forest; no Route 31 or Route 104 Top link."),
    dict(id="MTMOON", name="Mt. Moon", region="Kanto", kind="dungeon", subtype="cave", ports={"W":"cave", "E":"cave"}, asset="MTMOON.png", required=True, story_order=5, notes="Rocket I; through-dungeon between mountain routes."),
    dict(id="PARK", name="National Park", region="Johto", kind="dungeon", subtype="landmark", ports={"S":"gate", "E":"gate"}, asset="PARK.png", required=True, story_order=7, notes="Mandatory breathing-space traversal between Goldenrod and Ecruteak."),
    dict(id="BURNED", name="Burned Tower", region="Johto", kind="dungeon", subtype="tower", ports={}, special_ports=[{"id":"ENTRY","label":"Entry","type":"warp"}], asset="BURNED.png", required=True, story_order=8.5, notes="Local Ecruteak story dungeon; usually attached to Ecruteak rather than used as a regional through-edge."),
    dict(id="WEATHER", name="Weather Institute", region="Hoenn", kind="dungeon", subtype="facility", ports={}, special_ports=[{"id":"ENTRY","label":"Entry","type":"warp"}], asset="WEATHER.png", required=True, story_order=9, notes="Located on Route 119; local facility attachment is usually preferable."),
    dict(id="PKTOWER", name="Pokémon Tower", region="Kanto", kind="dungeon", subtype="tower", ports={}, special_ports=[{"id":"ENTRY","label":"Entry","type":"warp"}], asset="PKTOWER.png", required=True, story_order=12.5, notes="Rocket II; local Lavender attachment."),
    dict(id="MANSION", name="Pokémon Mansion", region="Kanto", kind="dungeon", subtype="building", ports={}, special_ports=[{"id":"ENTRY","label":"Entry","type":"warp"}], asset="MANSION.png", required=True, story_order=13.5, notes="Unlocked after Blaine; Entei encounter inside."),
    dict(id="WHIRL", name="Whirl Islands", region="Johto", kind="dungeon", subtype="cave", ports={"W":"cave", "E":"cave"}, asset="WHIRL.png", required=True, story_order=14, notes="Treat as the dungeon module embedded in the Route 41 water corridor."),
    dict(id="SILPH", name="Silph Co.", region="Kanto", kind="dungeon", subtype="facility", ports={}, special_ports=[{"id":"ENTRY","label":"Entry","type":"warp"}], asset="SILPH.png", required=True, story_order=16.5, notes="Rocket III / Giovanni / world-crisis climax; local Saffron attachment."),
    dict(id="ICEPATH", name="Ice Path", region="Johto", kind="dungeon", subtype="cave", ports={"W":"cave", "E":"cave"}, asset="ICEPATH.png", required=True, story_order=16.8, notes="Final approach dungeon before Blackthorn."),
    dict(id="COTTAGE", name="Sea Cottage", region="Kanto", kind="dungeon", subtype="facility", ports={}, special_ports=[{"id":"ENTRY","label":"Entry","type":"warp"}], asset="COTTAGE.png", required=False, story_order=11, notes="Optional story branch / Eevee; should not become a mandatory regional dead end."),
]

# Reusable dungeon / landmark inventory. Exterior connection counts are topology aids; local building doors
# are represented as generic warp ports rather than pretending they are cardinal map seams.
DUNGEON_LIBRARY = [
    # Kanto
    ("VIRIDIAN_FOREST","Viridian Forest","Kanto","forest",2),
    ("DIGLETTS_CAVE","Diglett's Cave","Kanto","cave",2),
    ("ROCK_TUNNEL","Rock Tunnel","Kanto","cave",2),
    ("POWER_PLANT","Power Plant","Kanto","facility",1),
    ("SEAFOAM","Seafoam Islands","Kanto","cave",2),
    ("SAFARI_ZONE","Safari Zone","Kanto","landmark",1),
    ("CERULEAN_CAVE","Cerulean Cave","Kanto","cave",1),
    ("KANTO_VR","Kanto Victory Road","Kanto","cave",2),
    # Johto
    ("DARK","Dark Cave","Johto","cave",3),
    ("UNION","Union Cave","Johto","cave",3),
    ("SLOWPOKE_WELL","Slowpoke Well","Johto","cave",1),
    ("SPROUT_TOWER","Sprout Tower","Johto","tower",1),
    ("RUINS_ALPH","Ruins of Alph","Johto","ruins",4),
    ("LIGHTHOUSE","Olivine Lighthouse","Johto","tower",1),
    ("MT_MORTAR","Mt. Mortar","Johto","cave",3),
    ("LAKE_RAGE","Lake of Rage","Johto","landmark",2),
    ("BELL_TOWER","Bell Tower","Johto","tower",1),
    ("DRAGONS_DEN","Dragon's Den","Johto","cave",1),
    ("TOHJO_FALLS","Tohjo Falls","Johto","cave",2),
    ("MT_SILVER","Mt. Silver Cave","Johto","cave",1),
    # Hoenn
    ("PETALBURG_WOODS","Petalburg Woods","Hoenn","forest",2),
    ("RUSTURF","Rusturf Tunnel","Hoenn","cave",2),
    ("GRANITE","Granite Cave","Hoenn","cave",1),
    ("FIERY_PATH","Fiery Path","Hoenn","cave",2),
    ("METEOR_FALLS","Meteor Falls","Hoenn","cave",3),
    ("JAGGED_PASS","Jagged Pass","Hoenn","landmark",2),
    ("NEW_MAUVILLE","New Mauville","Hoenn","facility",1),
    ("ABANDONED_SHIP","Abandoned Ship","Hoenn","facility",1),
    ("MT_PYRE","Mt. Pyre","Hoenn","tower",1),
    ("SHOAL","Shoal Cave","Hoenn","cave",1),
    ("SEAFLOOR","Seafloor Cavern","Hoenn","cave",1),
    ("CAVE_ORIGIN","Cave of Origin","Hoenn","cave",1),
    ("SKY_PILLAR","Sky Pillar","Hoenn","tower",1),
    ("HOENN_VR","Hoenn Victory Road","Hoenn","cave",2),
]

ASSET_ALIASES = {
    "DARK": "DARK.png",
    "SLOWPOKE_WELL": "WELL.png",
    "NEW_MAUVILLE": "NM.png",
    "SHOAL": "SHOAL.png",
    "KANTO_VR": "VR.png",
    "HOENN_VR": "VR.png",
}


def route_dimensions(shape: str) -> tuple[int, int]:
    return {
        "vertical": (88, 168),
        "horizontal": (168, 88),
        "elbow": (126, 126),
        "3-way": (138, 138),
        "4-way": (148, 148),
    }.get(shape, (126, 126))


def port_type_for_route(traversal: str) -> str:
    return "water" if traversal == "water" else "mixed" if traversal == "mixed" else "land"


def topology_class(port_count: int) -> str:
    if port_count <= 1:
        return "terminal"
    if port_count == 2:
        return "corridor"
    if port_count == 3:
        return "junction"
    return "hub"


def make_route(row: dict[str, str]) -> dict:
    route = row["route"]
    rid = f"R{route}"
    ports = [p.strip() for p in row["ports"].split("/") if p.strip()]
    ptype = port_type_for_route(row["traversal"])
    port_map = {p: ptype for p in ports}
    for port in ROUTE_PORT_REMOVALS.get(rid, set()):
        port_map.pop(port, None)
    asset = f"R{route}.png"
    required_status = "required" if rid in STORY_REQUIRED_ROUTE_IDS else "optional-story" if rid in STORY_LINKED_OPTIONAL_ROUTE_IDS else "library"
    special_ports = [
        {"id": port_id, "label": label, "type": transition_type, "regional": True}
        for port_id, label, transition_type in ROUTE_TRANSITION_PORTS.get(rid, [])
    ]
    if rid == "R119": special_ports.append({"id":"WEATHER","label":"Weather Institute","type":"warp"})
    if rid == "R41": special_ports.append({"id":"WHIRL","label":"Whirl Islands","type":"warp"})
    if rid == "R25": special_ports.append({"id":"COTTAGE","label":"Sea Cottage","type":"warp"})
    if rid == "R110": special_ports.append({"id":"NEW_MAUVILLE","label":"New Mauville","type":"warp"})
    regional_port_count = len(port_map) + sum(bool(p.get("regional")) for p in special_ports)
    return {
        "id": rid,
        "name": f"Route {route}",
        "region": row["region"],
        "generation": int(row["generation"]),
        "kind": "route",
        "ports": port_map,
        "special_ports": special_ports,
        "regional_port_count": regional_port_count,
        "topology_class": topology_class(regional_port_count),
        "shape": row["shape"],
        "traversal": row["traversal"],
        "theme": row["theme"],
        "status": row["status"],
        "notes": row["notes"],
        "asset": asset,
        "required_status": required_status,
        "required": required_status == "required",
        "dimensions": route_dimensions(row["shape"]),
    }


def make_route_variant(
    row: dict[str, str],
    route_id: str,
    name: str,
    ports: dict[str, str],
    shape: str,
    theme: str,
    notes: str,
) -> dict:
    route = make_route(row)
    route.update({
        "id": route_id,
        "name": name,
        "ports": ports,
        "regional_port_count": len(ports) + sum(bool(p.get("regional")) for p in route["special_ports"]),
        "topology_class": topology_class(len(ports) + sum(bool(p.get("regional")) for p in route["special_ports"])),
        "shape": shape,
        "theme": theme,
        "notes": notes,
        "dimensions": route_dimensions(shape),
    })
    return route


def make_library_dungeon(spec: tuple[str, str, str, str, int]) -> dict:
    did, name, region, subtype, count = spec
    asset = ASSET_ALIASES.get(did, f"{did}.png")
    transition_type = "cave" if subtype == "cave" else "warp"
    specials = [
        {
            "id": f"P{i+1}",
            "label": f"Entrance {i+1}",
            "type": transition_type,
            "regional": subtype == "cave",
        }
        for i in range(count)
    ]
    return {
        "id": did,
        "name": name,
        "region": region,
        "kind": "dungeon",
        "subtype": subtype,
        "ports": {},
        "special_ports": specials,
        "asset": asset,
        "required": False,
        "entrance_count": count,
        "notes": "Reusable Gen I-III location. Entrance count is a topology aid; verify exact source-map warp geometry before implementation.",
    }


def main() -> None:
    route_rows = list(csv.DictReader(ROUTE_ROWS.splitlines()))
    routes = []
    for row in route_rows:
        if row["route"] == "10":
            routes.append(make_route_variant(row, "R10_TOP", "Route 10 Top", {"N": "mixed"}, "vertical", "river canyon; Rock Tunnel", "North segment; north exit and Rock Tunnel cave link."))
            routes.append(make_route_variant(row, "R10_SOUTH", "Route 10 South", {"S": "mixed"}, "vertical", "river canyon; Rock Tunnel", "South segment; Rock Tunnel cave link and south exit."))
        elif row["route"] == "104":
            routes.append(make_route_variant(row, "R104_TOP", "Route 104 Top", {"N": "land", "S": "land"}, "vertical", "forest-edge route", "Top segment; north and south land exits."))
            routes.append(make_route_variant(row, "R104_BOTTOM", "Route 104 Bottom", {"N": "land", "E": "land", "S": "water"}, "3-way", "beach and forest-edge adapter", "Bottom segment; north and east land exits with a south water exit."))
        else:
            routes.append(make_route(row))
    required_ids = {d["id"] for d in REQUIRED_DUNGEONS}
    dungeon_library = [make_library_dungeon(x) for x in DUNGEON_LIBRARY if x[0] not in required_ids]

    # Add asset availability metadata; the app will create abstract topology previews when absent.
    all_parts = TOWNS + routes + REQUIRED_DUNGEONS + dungeon_library
    for p in all_parts:
        p["asset_available"] = bool(p.get("asset") and (ASSETS / p["asset"]).exists())
        if "dimensions" not in p:
            p["dimensions"] = (132, 112) if p["kind"] == "town" else (126, 112)

    catalog = {
        "version": "plastic-ox-topology-editor-v0.1",
        "design_basis": "Plastic Ox story v0.6.1 + Gen I-III route inventory",
        "towns": TOWNS,
        "routes": routes,
        "required_dungeons": REQUIRED_DUNGEONS,
        "dungeon_library": dungeon_library,
        "story_required_route_ids": sorted(STORY_REQUIRED_ROUTE_IDS),
        "story_linked_optional_route_ids": sorted(STORY_LINKED_OPTIONAL_ROUTE_IDS),
    }
    OUT.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} with {len(routes)} routes, {len(TOWNS)} required towns, "
          f"{len(REQUIRED_DUNGEONS)} story areas, and {len(dungeon_library)} reusable dungeons.")


if __name__ == "__main__":
    main()
