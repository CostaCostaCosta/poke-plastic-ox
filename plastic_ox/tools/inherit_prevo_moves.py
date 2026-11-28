#!/usr/bin/env python3
"""Make every evolved Pokemon able to learn every move its pre-evolutions learn.

Plastic Ox rule: a final evolution (and, cumulatively, every middle stage) must
not lose access to a move its earlier stages could learn. This mostly matters for
stone evolutions (Nidoking, Nidoqueen, Vileplume, ...) and Breloom, whose Gen 3
level-up lists drop most of the pre-evolution's moves.

Two sources are updated in place, idempotently:
  * src/data/pokemon/level_up_learnsets/gen_3.h: each move a pre-evolution
    learns by level that the evolution lacks is added at the pre-evolution's level.
  * src/data/pokemon/all_learnables.json: the evolution's learnable set gains the
    pre-evolution's (feeds TM/tutor compatibility in teachable_learnsets.h).

Run with --check to fail (exit 1) if either file would change.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
FAMILIES = sorted((ROOT / "src/data/pokemon/species_info").glob("*_families.h"))
LEVELUP = ROOT / "src/data/pokemon/level_up_learnsets/gen_3.h"
LEARNABLES = ROOT / "src/data/pokemon/all_learnables.json"

BLOCK_RE = re.compile(r"^    \[(SPECIES_\w+)\]\s*=", re.M)
LVL_SYM_RE = re.compile(r"\.levelUpLearnset\s*=\s*(s\w+LevelUpLearnset)")
EVO_RE = re.compile(r"\.evolutions\s*=\s*EVOLUTION\((.*?)\),\s*\n", re.S)
EVO_TARGET_RE = re.compile(r"\{EVO_\w+,\s*[^,{}]+,\s*(SPECIES_\w+)")
LEARNSET_RE = re.compile(r"(static const struct LevelUpMove (s\w+LevelUpLearnset)\[\] = \{\n)(.*?)(    LEVEL_UP_END\n\};)", re.S)
MOVE_RE = re.compile(r"LEVEL_UP_MOVE\(\s*(\d+),\s*(MOVE_\w+)\)")


def parse_species():
    lvl_sym, prevos = {}, {}
    for path in FAMILIES:
        text = path.read_text()
        starts = [(m.start(), m.group(1)) for m in BLOCK_RE.finditer(text)]
        for i, (pos, sp) in enumerate(starts):
            block = text[pos: starts[i + 1][0] if i + 1 < len(starts) else len(text)]
            m = LVL_SYM_RE.search(block)
            if m and sp not in lvl_sym:
                lvl_sym[sp] = m.group(1)
            for em in EVO_RE.finditer(block):
                for target in EVO_TARGET_RE.findall(em.group(1)):
                    if target != sp:
                        prevos.setdefault(target, set()).add(sp)
    return lvl_sym, prevos


def ancestors(sp, prevos, seen=None):
    seen = set() if seen is None else seen
    for p in prevos.get(sp, ()):
        if p not in seen:
            seen.add(p)
            ancestors(p, prevos, seen)
    return seen


def main():
    check = "--check" in sys.argv
    lvl_sym, prevos = parse_species()

    text = LEVELUP.read_text()
    sets = {m.group(2): [(int(a), b) for a, b in MOVE_RE.findall(m.group(3))] for m in LEARNSET_RE.finditer(text)}
    original = {k: list(v) for k, v in sets.items()}

    # Lowest level at which any pre-evolution learns each move.
    additions = {}
    for sp in prevos:
        sym = lvl_sym.get(sp)
        if sym not in sets:
            continue
        for anc in ancestors(sp, prevos):
            asym = lvl_sym.get(anc)
            for lvl, move in original.get(asym, ()):
                d = additions.setdefault(sym, {})
                d[move] = min(lvl, d.get(move, 999))
    changed_lvl = []
    for sym, moves in additions.items():
        have = {mv for _, mv in sets[sym]}
        new = [(l, mv) for mv, l in moves.items() if mv not in have]
        if not new:
            continue
        merged = sets[sym] + sorted(new)
        merged.sort(key=lambda t: t[0])  # stable: existing order kept within a level
        sets[sym] = merged
        changed_lvl.append(sym)

    def render(m):
        sym = m.group(2)
        if sym not in changed_lvl:
            return m.group(0)
        body = "".join(f"    LEVEL_UP_MOVE({l:2d}, {mv}),\n" for l, mv in sets[sym])
        return m.group(1) + body + m.group(4)
    new_text = LEARNSET_RE.sub(render, text)

    learn = json.loads(LEARNABLES.read_text())
    key = lambda sp: sp[len("SPECIES_"):]
    changed_learn = []
    for sp in prevos:
        if key(sp) not in learn:
            continue
        cur = learn[key(sp)]
        extra = set()
        for anc in ancestors(sp, prevos):
            extra |= set(learn.get(key(anc), ()))
        missing = sorted(extra - set(cur))
        if missing:
            learn[key(sp)] = sorted(set(cur) | extra)
            changed_learn.append(key(sp))
    new_json = json.dumps(learn, indent=2)

    if check:
        bad = new_text != text or json.loads(new_json) != json.loads(LEARNABLES.read_text())
        print(f"level-up learnsets needing inheritance: {len(changed_lvl)}; learnables: {len(changed_learn)}")
        sys.exit(1 if bad else 0)
    LEVELUP.write_text(new_text)
    LEARNABLES.write_text(new_json)
    print(f"updated {len(changed_lvl)} level-up learnsets, {len(changed_learn)} learnable sets")


if __name__ == "__main__":
    main()
