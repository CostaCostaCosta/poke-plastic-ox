#!/usr/bin/env python3
"""Cerulean Cave: Cerulean City gate, Mt. Silver interior, RED and MEWTWO finale.

Static part: Cerulean City's FRLG cave mouth (reached by surfing south from
Route 24) and the waterfall room warp to each other;
the cave guard hides on FLAG_SYS_GAME_CLEAR; every imported cave table offers
UNOWN and WOBBUFFET; RED (trainer 958) carries exactly the requested team and
records his win in FLAG_POX_TRAINER_RED.
Emulator part (mGBA, needs pokeemerald.gba): before the Hall of Fame the guard
blocks the cave; after it the player walks into the cave and back out with
the D-pad; a loss to RED leaves him on the summit; a win shows the player's
trainer card, then the Hall of Fame and credits, and records the victory.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

RED = "TRAINER_PLASTIC_OX_RED"
CAVE_MAPS = ["MtSilver_1F_WaterfallRoom_hns", "MtSilver_1F_ItemRoom_hns", "MtSilver_1F_MoltresRoom_hns",
             "MtSilver_MountainSide_hns", "MtSilver_2F_hns", "MtSilver_Snow_hns", "MtSilver_3F_hns"]
TEAM = {  # species: (item, ability, nature, EVs, moves) as requested
    "Mewtwo": ("Lum Berry", "Pressure", "Mild", "4 Atk / 252 SpA / 252 Spe",
               ["Thunder", "Ice Beam", "Calm Mind", "Self-Destruct"]),
    "Kyogre": ("Leftovers", "Drizzle", "Modest", "252 HP / 252 Def / 4 SpA",
               ["Surf", "Ice Beam", "Calm Mind", "Thunder Wave"]),
    "Metagross": ("Choice Band", "Clear Body", "Adamant", "252 HP / 252 Atk / 4 SpD",
                  ["Meteor Mash", "Earthquake", "Explosion", "Rock Slide"]),
    "Snorlax": ("Leftovers", "Immunity", "Sassy", "136 HP / 120 Atk / 252 SpD",
                ["Body Slam", "Thunder", "Curse", "Self-Destruct"]),
    "Latios (M)": ("Soul Dew", "Levitate", "Modest", "4 HP / 252 SpA / 252 Spe",
                   ["Thunder", "Ice Beam", "Recover", "Refresh"]),
    "Deoxys-Attack": ("Spell Tag", "Pressure", "Hasty", "252 Atk / 4 SpA / 252 Spe",
                      ["Shadow Ball", "Superpower", "Thunder", "Extreme Speed"]),
}


def load_map(name):
    return json.loads((ROOT / "data/maps" / name / "map.json").read_text())


def static_checks() -> None:
    cer, fall = load_map("CeruleanCity_Frlg"), load_map("MtSilver_1F_WaterfallRoom_hns")
    mouth = cer["warp_events"][7]
    assert (mouth["x"], mouth["y"], mouth["dest_map"], mouth["dest_warp_id"]) == (
        1, 12, "MAP_MT_SILVER_1F_WATERFALL_ROOM_HNS", "0"), mouth
    assert fall["warp_events"][0]["dest_map"] == "MAP_CERULEAN_CITY" and fall["warp_events"][0]["dest_warp_id"] == "7"
    guard = [o for o in cer["object_events"] if o.get("script") == "CeruleanCity_EventScript_CeruleanCaveGuard"]
    assert len(guard) == 1 and (guard[0]["x"], guard[0]["y"]) == (1, 13) and guard[0]["flag"] == "FLAG_SYS_GAME_CLEAR"
    ids = {load_map(m)["id"] for m in CAVE_MAPS + ["MtSilver_SummitDay_hns", "CeruleanCity_Frlg"]}
    for m in CAVE_MAPS + ["MtSilver_SummitDay_hns"]:
        for w in load_map(m)["warp_events"]:
            assert w["dest_map"] in ids, (m, w)
    print("  ok  Cerulean City mouth <-> waterfall room; guard hides on FLAG_SYS_GAME_CLEAR; no dangling warps")

    enc = json.loads((ROOT / "src/data/wild_encounters.json").read_text())["wild_encounter_groups"][0]["encounters"]
    for m in CAVE_MAPS:
        tables = [e for e in enc if e["map"] == load_map(m)["id"]]
        assert len(tables) == 3, (m, len(tables))
        for t in tables:
            species = {s["species"] for s in t["land_mons"]["mons"]}
            assert {"SPECIES_UNOWN", "SPECIES_WOBBUFFET"} <= species, (m, t["base_label"])
    print(f"  ok  UNOWN and WOBBUFFET in all {len(CAVE_MAPS) * 3} cave land tables")

    party = (ROOT / "src/data/trainers.party").read_text()
    block = re.search(rf"^=== {RED} ===\n(.*?)(?=^=== |\Z)", party, re.M | re.S)[1]
    mons = [m.strip() for m in block.split("\n\n")[1:] if m.strip()]
    assert [m.splitlines()[0].split(" @ ")[0] for m in mons] == list(TEAM), mons
    for mon in mons:
        name, item = mon.splitlines()[0].split(" @ ")
        want_item, ability, nature, evs, moves = TEAM[name]
        assert item == want_item and f"Ability: {ability}" in mon and f"{nature} Nature" in mon, mon
        assert f"EVs: {evs}" in mon and re.findall(r"^- (.+)$", mon, re.M) == moves, mon
    opp = (ROOT / "include/constants/opponents.h").read_text()
    assert re.search(rf"^#define {RED} 958$", opp, re.M)
    flags = (ROOT / "include/constants/flags.h").read_text()
    assert "(id) == 958) ? (POX_EVENT_FLAGS_START + 52)" in flags
    assert "#define FLAG_POX_TRAINER_RED (POX_EVENT_FLAGS_START + 52)" in (
        ROOT / "include/constants/plastic_ox_flags.h").read_text()
    summit = (ROOT / "data/maps/MtSilver_SummitDay_hns/scripts.inc").read_text()
    for label, text in (("RedIntro", "……………… ………………"), ("RedDefeat", "…!"), ("RedWon", "…"),
                        ("RedAfter", "……………… ………………")):
        assert re.search(rf'^PoxCeruleanCave_Text_{label}::\n\t\.string "{text}\$"$', summit, re.M), label
    assert "trainerbattle_earlyrival TRAINER_PLASTIC_OX_RED, 0, PoxCeruleanCave_Text_RedDefeat, PoxCeruleanCave_Text_RedWon" in summit
    assert "clearflag FLAG_POX_RED_RESTING" in (ROOT / "data/scripts/plastic_ox_league.inc").read_text()
    print("  ok  RED: requested six (items, abilities, natures, EVs, moves); ID 958 -> FLAG_POX_TRAINER_RED")
    print("  ok  RED's lines: intro/after '……………… ………………', defeat '…!', win '…'; League clears his rest flag")


def callback_owner(g) -> str:
    """Object file that owns gMain.callback2 (static CB2s are not in the symbol table)."""
    cb = g.core.memory.iwram.u32[g.syms["gMain"] - 0x03000000 + 4] & ~1
    for start, size, obj in TEXT_SECTIONS:
        if start <= cb < start + size:
            return obj
    return hex(cb)


def text_sections():
    out = []
    lines = (ROOT / "pokeemerald.map").read_text(errors="replace").splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^ \.text\s+(0x[0-9a-f]+)\s+(0x[0-9a-f]+)\s+\S*/(\w+)\.o$", line)
        if not m and line.strip() == ".text" and i + 1 < len(lines):
            m = re.match(r"^\s+(0x[0-9a-f]+)\s+(0x[0-9a-f]+)\s+\S*/(\w+)\.o$", lines[i + 1])
        if m:
            out.append((int(m[1], 16), int(m[2], 16), m[3]))
    return out


TEXT_SECTIONS: list = []


def emulator_checks() -> None:
    from pox_fixtures import game, finish_trainer, at, shot
    from test_sudowoodo_v1 import talk, settle, settle_overworld, in_overworld
    from walklib import K

    TEXT_SECTIONS.extend(text_sections())
    g = game()
    assert not g.flag("FLAG_SYS_GAME_CLEAR")

    def step(key, n=1):
        """Exactly n tiles (or until blocked / warped): one short press each."""
        for _ in range(n):
            start = (g.state()["group"], g.state()["num"], g.state()["x"], g.state()["y"])
            for _ in range(3):
                g.hold(key, 4)
                g.frame(20)
                now = (g.state()["group"], g.state()["num"], g.state()["x"], g.state()["y"])
                if now != start:
                    break

    def pos():
        s = g.state()
        return s["x"], s["y"]

    # 1. Before the Hall of Fame the League guard stands in the cave mouth.
    # (test_route24_cerulean.py surfs here from Route 24 with the D-pad.)
    g.warp("CeruleanCity_Frlg", 1, 14)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert any("HALL OF FAME" in t for t in r["text"]), r["text"]
    settle(g)
    step(K.KEY_UP, 2)
    assert at(g, "CeruleanCity_Frlg") and pos() == (1, 14), (g.state(), pos())
    shot(g, "cerulean_cave_guard")
    print("  ok  guard blocks the Cerulean City cave mouth before the Hall of Fame")

    # 2. After the Hall of Fame: walk in through the mouth, then back out.
    g.flag("FLAG_SYS_GAME_CLEAR", True)
    g.warp("CeruleanCity_Frlg", 1, 14)
    g.frame(60)
    step(K.KEY_UP, 2)
    g.frame(120)
    assert at(g, "MtSilver_1F_WaterfallRoom_hns"), ("guard still there", g.state())
    arrived = pos()
    shot(g, "cerulean_cave_waterfall_room")
    print(f"  ok  Cerulean City mouth -> Cerulean Cave waterfall room at {arrived}")
    for _ in range(4):
        if at(g, "CeruleanCity_Frlg"):
            break
        step(K.KEY_DOWN)
        g.frame(60)
    g.frame(120)
    assert at(g, "CeruleanCity_Frlg"), g.state()
    assert pos() in ((1, 12), (1, 13)), pos()
    print(f"  ok  waterfall room -> Cerulean City cave mouth at {pos()}")

    # 3. Summit: RED and MEWTWO in the overworld. A loss leaves RED there.
    def trainer_id():
        return g.u16(g.syms["gTrainerBattleParameter"] + 2)

    def enemy_count():
        return g.u8(g.u32(g.syms["gEnemyPartyCountPtr"]))

    g.warp("MtSilver_SummitDay_hns", 10, 7)
    g.frame(60)
    shot(g, "cerulean_cave_summit")
    r = talk(g, K.KEY_UP)
    assert r["battle"] and any("……………… ………………" in t.replace("⋯", "…") for t in r["text"]), r
    g.frame(120)
    assert trainer_id() == g.const(RED) == 958 and enemy_count() == 6, (trainer_id(), enemy_count())
    finish_trainer(g, False)
    # Whiteout: let the respawn and its heal script finish before warping.
    for _ in range(20):
        g.frame(60)
        if settle_overworld(g) == 0:
            break
    assert not g.flag("FLAG_POX_TRAINER_RED") and not g.flag("FLAG_POX_RED_RESTING")
    print("  ok  RED ('……………… ………………') battles with six; a loss leaves the summit unchanged")

    # 4. Talking to MEWTWO starts the same battle; a win shows the trainer
    # card, then the Hall of Fame, then the credits.
    g.warp("MtSilver_SummitDay_hns", 11, 7)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert r["battle"] and any("MEWTWO" in t for t in r["text"]), r
    g.frame(120)
    assert trainer_id() == 958
    seen = []
    finish_trainer(g, True)
    for _ in range(6000):
        owner = callback_owner(g)
        if not seen or seen[-1] != owner:
            seen.append(owner)
            if owner in ("trainer_card", "hall_of_fame"):
                g.frame(150)  # past the fade-in, for the screenshot
                shot(g, "cerulean_cave_" + owner)
                if owner == "hall_of_fame":
                    g.frame(900)  # save done; the party is on display
                    shot(g, "cerulean_cave_hall_of_fame_team")
        if owner == "credits":
            g.frame(240)
            shot(g, "cerulean_cave_credits")
            break
        g.tap(K.KEY_B if owner == "trainer_card" else K.KEY_A, hold=1, wait=6)
    assert g.flag("FLAG_POX_TRAINER_RED") and g.flag("FLAG_POX_RED_RESTING"), seen
    order = [o for o in seen if o in ("trainer_card", "hall_of_fame", "credits")]
    assert order == ["trainer_card", "hall_of_fame", "credits"], seen
    print("  ok  beating RED: trainer card, Hall of Fame (team), then credits")

    # 5. Afterwards MEWTWO waits on the summit (RED is gone); any ball catches it.
    from test_sudowoodo_v1 import throw_ball, in_battle, wait_for_battle, bag, POCKET_BALLS, const
    g = game()
    g.flag("FLAG_SYS_GAME_CLEAR", True)
    g.flag("FLAG_POX_TRAINER_RED", True)
    g.flag("FLAG_POX_RED_RESTING", True)
    g.warp("MtSilver_SummitDay_hns", 10, 7)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert not r["battle"] and not r["text"], ("RED still on the summit", r)
    g.warp("MtSilver_SummitDay_hns", 11, 7)
    g.frame(60)
    r = talk(g, K.KEY_UP, stop_at="Approach")
    assert r["stopped"] and not r["battle"], r
    g.frame(90)  # let the YES/NO menu open
    g.tap(K.KEY_B, hold=2, wait=60)  # decline
    for _ in range(60):
        if g.u8(g.syms["sGlobalScriptContextStatus"]) == 2:
            break
        g.tap(K.KEY_B, hold=1, wait=6)
    assert not in_battle(g), "declining still started the battle"
    assert not g.flag("FLAG_POX_CAUGHT_MEWTWO")
    r = talk(g, K.KEY_UP, stop_at="Approach")
    assert r["stopped"], r
    for _ in range(20):  # YES (cursor default) once the menu is up
        if in_battle(g):
            break
        g.tap(K.KEY_A, hold=2, wait=60)
    for _ in range(600):
        if in_battle(g):
            break
        g.frame(10)
    assert in_battle(g), "reward battle did not start"
    assert wait_for_battle(g), "no action menu in the reward battle"
    poke_ball = const("ITEM_POKE_BALL", "items.h")
    before = bag(g, poke_ball, POCKET_BALLS)
    throw_ball(g)  # slot 0 of the balls pocket: a plain POKé BALL
    for _ in range(3000):
        if g.flag("FLAG_POX_CAUGHT_MEWTWO") and in_overworld(g):
            break
        g.tap(K.KEY_B, hold=1, wait=6)
    assert g.flag("FLAG_POX_CAUGHT_MEWTWO"), ("MEWTWO not caught", g.u8(g.syms["gBattleOutcome"]))
    assert before - bag(g, poke_ball, POCKET_BALLS) == 1, (before, bag(g, poke_ball, POCKET_BALLS))
    # The fixture party is full, so MEWTWO goes to the first PC box.
    storage = g.u32(g.syms["gPokemonStoragePtr"])
    slots = [storage + 4 + slot * 80 for slot in range(30)]
    box = [g.box_species(m) for m in slots if g.u8(m + 19) & 7 == 2]  # occupied slots only
    assert 150 in box, box  # SPECIES_MEWTWO (national dex order in the species enum)
    settle_overworld(g)
    r = talk(g, K.KEY_UP)
    assert not r["battle"] and not r["text"], ("MEWTWO still there", r)
    print("  ok  after RED: MEWTWO reward battle; declining keeps it; one POKé BALL catches it")

    # 6. Rematch: winning the League again (the real Hall of Fame script)
    # clears FLAG_POX_RED_RESTING and RED is back on the summit.
    for n in range(1, 9):
        g.flag(f"FLAG_BADGE{n:02}_GET", True)
    for f in ("WALLACE", "STEVEN", "LEAGUELANCE", "BLUE", "BILL"):
        g.flag(f"FLAG_POX_LEAGUE_{f}", True)
    assert g.flag("FLAG_POX_RED_RESTING")
    g.warp("PlasticOx_HallOfFame", 7, 12)
    for _ in range(4000):
        if callback_owner(g) == "credits":
            break
        g.tap(K.KEY_A, hold=1, wait=6)
    assert callback_owner(g) == "credits", callback_owner(g)
    assert not g.flag("FLAG_POX_RED_RESTING"), "Hall of Fame did not wake RED"
    g.core.reset()  # GameClear saved; Continue from Indigo
    for _ in range(300):
        g.tap(K.KEY_A, hold=2, wait=20)
        if in_overworld(g):
            break
    g.frame(180)
    settle(g)
    g.warp("MtSilver_SummitDay_hns", 10, 7)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert r["battle"] and any("……………… ………………" in t.replace("⋯", "…") for t in r["text"]), r
    g.frame(120)
    assert trainer_id() == 958 and enemy_count() == 6
    finish_trainer(g, True)
    for _ in range(4000):
        if callback_owner(g) == "credits":
            break
        g.tap(K.KEY_B if callback_owner(g) == "trainer_card" else K.KEY_A, hold=1, wait=6)
    assert g.flag("FLAG_POX_RED_RESTING")
    print("  ok  winning the League again brings RED back; the rematch ends in the credits again")
    print("\nPASS: Cerulean Cave")


if __name__ == "__main__":
    static_checks()
    if "--static" not in sys.argv:
        emulator_checks()
