#!/usr/bin/env python3
"""Project Equilibrium: Route 119 crossing, two Institute trials, Director.

Static part: both research teams are re-checked against the 'fortree' (ADV RU)
checkpoint with the same legality code the trainer-team generator uses.
Emulator part (mGBA, needs pokeemerald.gba): the crossing refuses passage, the
Silph trial waits for the Devon trial, a real loss keeps a trial repeatable, a
real win records it across a map change and a native save/reset/Continue, the
Director opens the crossing, the engineer leaves the route, and Fortree's east
exit still waits for badge 4.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "plastic_ox/tools"))

DEVON = "TRAINER_PLASTIC_OX_WEATHER_DEVON"
SILPH = "TRAINER_PLASTIC_OX_WEATHER"


def static_checks() -> None:
    import pox_progression as P
    party = (ROOT / "src/data/trainers.party").read_text()
    legal = P.legal_for("fortree")
    cap = P.cap_at("fortree")
    for trainer in (DEVON, SILPH):
        block = re.search(rf"^=== {trainer} ===\n(.*?)(?=^=== |\Z)", party, re.M | re.S)[1]
        mons = [m for m in block.split("\n\n")[1:] if m.strip()]
        assert len(mons) == 6, (trainer, len(mons))
        species_seen = set()
        for mon in mons:
            lines = mon.strip().splitlines()
            name = lines[0].split(" @ ")[0].strip()
            species = "SPECIES_" + name.upper().replace("-", "_").replace("'", "")
            level = int(re.search(r"Level: (\d+)", mon)[1])
            assert species in legal, (trainer, species, P.tier_of(species))
            assert species not in species_seen, (trainer, species, "species clause")
            species_seen.add(species)
            assert 30 <= level <= cap, (trainer, species, level, cap)
            ability = re.search(r"Ability: (.+)", mon)[1]
            assert ability not in ("Drizzle", "Drought"), (trainer, species, ability)
            for move in re.findall(r"^- (.+)$", mon, re.M):
                const = "MOVE_" + move.upper().replace(" ", "_").replace("-", "_")
                ok, why = P.move_legal(species, const, level, True)
                assert ok, (trainer, species, move, why)
        print(f"  ok  {trainer}: six RU-legal species, levels <= {cap}, legal Gen 3 moves")


def emulator_checks() -> None:
    from test_cinnabar import finish_trainer, save_reload
    from test_sudowoodo_v1 import SudoGame as StoryGame
    from test_sudowoodo_v1 import talk, settle, settle_overworld, in_battle
    from test_ecruteak_gym_gate import at
    from walklib import K

    g = StoryGame()
    g.run("Pox_Treecko")
    for name in ("FLAG_POX_STORY_STARTER", "FLAG_ADVENTURE_STARTED", "FLAG_POX_STORY_ILEX",
                 "FLAG_POX_STORY_MTMOON", "FLAG_POX_STORY_BURNED_TOWER",
                 "FLAG_BADGE01_GET", "FLAG_BADGE02_GET", "FLAG_BADGE03_GET"):
        g.flag(name, True)
    assert not g.flag("FLAG_POX_STORY_WEATHER")

    def trainer_id() -> int:
        return g.u16(g.syms["gTrainerBattleParameter"] + 2)

    def enemy_count() -> int:
        return g.u8(g.u32(g.syms["gEnemyPartyCountPtr"]))

    # 1. Crossing closed; the engineer is there and points at the Institute.
    g.warp("Route119", 38, 8)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert any("crossing is" in t and "closed" in t for t in r["text"]), r["text"]
    g.shot("/tmp/pox_wi_engineer.png")
    settle(g)
    for _ in range(6):
        g.hold(K.KEY_RIGHT, 8)
        g.frame(30)
        settle(g)
    assert at(g, "Route119"), ("crossing let the player through", g.state())
    print("  ok  Route 119 crossing refuses passage; engineer explains")

    # 2. Director before any trial: no completion.
    g.warp("Route119_WeatherInstitute_1F", 10, 6)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert any("EQUILIBRIUM" in t for t in r["text"]), r["text"]
    assert not g.flag("FLAG_POX_STORY_WEATHER")
    print("  ok  Director introduces Project Equilibrium, completes nothing")

    # 3. Vale waits for the Devon trial.
    g.warp("Route119_WeatherInstitute_2F", 17, 6)
    g.frame(60)
    r = talk(g, K.KEY_RIGHT)
    assert not r["battle"] and any("DEVON" in t for t in r["text"]), r
    print("  ok  Silph trial waits for Devon's")

    # 4. Devon trial: real loss keeps it repeatable, real win records it.
    def start_devon():
        g.warp("Route119_WeatherInstitute_2F", 11, 7)
        g.frame(60)
        r = talk(g, K.KEY_UP)
        assert r["battle"], r
        g.frame(120)
        assert trainer_id() == g.const(DEVON), trainer_id()
        assert enemy_count() == 6, enemy_count()

    start_devon()
    finish_trainer(g, False)
    assert g.u8(g.syms["gBattleOutcome"]) == 2
    g.frame(600)
    assert settle_overworld(g) is not None
    assert not g.flag("FLAG_POX_TRAINER_WEATHER_DEVON")
    print("  ok  losing to LINDEN leaves trial 1 open")
    start_devon()
    finish_trainer(g, True)
    assert g.u8(g.syms["gBattleOutcome"]) == 1
    settle_overworld(g)
    assert g.flag("FLAG_POX_TRAINER_WEATHER_DEVON")
    assert not g.flag("FLAG_POX_STORY_WEATHER")
    print("  ok  beating LINDEN records trial 1 only")

    # 5. Leave and come back; crossing still closed; trial still recorded.
    g.warp("Route119", 38, 8)
    g.frame(60)
    g.hold(K.KEY_RIGHT, 8)
    g.frame(30)
    settle(g)
    assert at(g, "Route119") and g.flag("FLAG_POX_TRAINER_WEATHER_DEVON")
    r = talk(g, K.KEY_UP)
    assert not r["battle"]
    print("  ok  trial 1 persists across maps; crossing remains closed")

    # 6. Silph trial: six Pokemon, trainer 872.
    g.warp("Route119_WeatherInstitute_2F", 17, 6)
    g.frame(60)
    r = talk(g, K.KEY_RIGHT)
    assert r["battle"], r
    g.frame(120)
    assert trainer_id() == g.const(SILPH) and enemy_count() == 6
    finish_trainer(g, True)
    settle_overworld(g)
    assert g.flag(0x4A0 + g.const(SILPH) - 857)   # TRAINER_FLAG(872) == 0x4AF
    print("  ok  beating VALE records trial 2")

    # Re-talking either researcher must not start another battle.
    g.warp("Route119_WeatherInstitute_2F", 11, 7)
    g.frame(60)
    assert not talk(g, K.KEY_UP)["battle"]
    g.warp("Route119_WeatherInstitute_2F", 17, 6)
    g.frame(60)
    assert not talk(g, K.KEY_RIGHT)["battle"]
    print("  ok  neither trial repeats")

    # 7. Native save, reset, Continue: progress survives; event still open.
    g.warp("Route119_WeatherInstitute_1F", 10, 7)
    g.frame(60)
    save_reload(g)
    assert at(g, "Route119_WeatherInstitute_1F"), g.state()
    assert g.flag("FLAG_POX_TRAINER_WEATHER_DEVON")
    assert not g.flag("FLAG_POX_STORY_WEATHER")
    print("  ok  save/reset/Continue keeps both trials, event not yet concluded")

    # 8. Director concludes.
    g.warp("Route119_WeatherInstitute_1F", 10, 6)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert g.flag("FLAG_POX_STORY_WEATHER"), r["text"]
    assert any("FORTREE" in t for t in r["text"]), r["text"]
    r = talk(g, K.KEY_UP)
    assert any("habitat lines" in t for t in r["text"]), r["text"]
    print("  ok  Director concludes; post-event dialogue")

    # Engineer now indoors on 1F after a reload of the map.
    g.warp("Route119_WeatherInstitute_1F", 2, 11)
    g.frame(60)
    r = talk(g, K.KEY_LEFT)
    assert any("sensor line" in t for t in r["text"]), r["text"]
    g.warp("Route119_WeatherInstitute_2F", 11, 7)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert not r["battle"] and any("adaptable" in t for t in r["text"]), r["text"]
    print("  ok  engineer relocated indoors; researchers' post-event lines")

    # 9. Crossing open: the engineer is gone and the trigger reaches Fortree.
    g.warp("Route119", 38, 8)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert not any("closed" in t for t in r["text"]), r["text"]
    settle(g)
    for _ in range(6):
        if at(g, "FortreeCity"):
            break
        g.hold(K.KEY_RIGHT, 8)
        g.frame(60)
    assert at(g, "FortreeCity"), g.state()
    g.frame(60)
    assert g.flag("FLAG_POX_REACHED_FORTREE")
    print("  ok  crossing open; Route 119 -> Fortree sets FLAG_POX_REACHED_FORTREE")

    # 10. A research file reads without changing progression.
    g.warp("Route119_WeatherInstitute_2F", 6, 3)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert any("FILE 001" in t for t in r["text"]), r["text"]
    print("  ok  research file 001 reads")

    # 11. Fortree east exit still waits for badge 4 (Gabby, Ty, Kecleon, gate).
    assert not g.flag("FLAG_BADGE04_GET")
    g.warp("FortreeCity", 35, 10)
    g.frame(60)
    for _ in range(8):
        g.hold(K.KEY_RIGHT, 8)
        g.frame(30)
        settle(g)
    assert at(g, "FortreeCity"), g.state()
    print("  ok  Fortree's east exit still blocked before Winona")
    # 12. Mossdeep Space Center continues the thread (reveal-ladder step 11).
    assert not g.flag("FLAG_POX_STORY_SPACE_CENTER")
    g.warp("MossdeepCity_SpaceCenter_1F", 4, 4)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert any("VALE" in t for t in r["text"]), r["text"]
    assert not g.flag("FLAG_POX_STORY_SPACE_CENTER")
    g.warp("MossdeepCity_SpaceCenter_1F", 7, 3)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert not g.flag("FLAG_POX_STORY_SPACE_CENTER"), "report ran without badge 6"
    g.flag("FLAG_BADGE06_GET", True)
    r = talk(g, K.KEY_UP)
    joined = " ".join(r["text"])
    assert "WEATHER" in joined and "SILPH CO" in joined, r["text"]
    assert g.flag("FLAG_POX_STORY_SPACE_CENTER")
    r = talk(g, K.KEY_UP)
    assert any("traffic into SAFFRON" in t for t in r["text"]), r["text"]
    g.warp("MossdeepCity_SpaceCenter_1F", 4, 4)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert any("busier" in t.replace("{page}", " ").replace("<FA>", " ") for t in r["text"]), r["text"]
    g.warp("MossdeepCity_SpaceCenter_1F", 4, 2)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert any("FILE 007" in t for t in r["text"]), r["text"]
    g.warp("Route119_WeatherInstitute_1F", 10, 6)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert any("MOSSDEEP" in t for t in r["text"]), r["text"]
    print("  ok  Space Center: VALE, two-beat report on badge 6, file 007, Director callback")
    print("\nPASS: Project Equilibrium")


if __name__ == "__main__":
    static_checks()
    if "--static" not in sys.argv:
        emulator_checks()
