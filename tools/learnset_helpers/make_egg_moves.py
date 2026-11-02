#!/usr/bin/env python3

"""Regenerate Egg Move arrays using Plastic Ox's Gen-III learnset policy."""

import json
import pathlib
import re
import sys

from make_learnables import LEARNSET_SOURCE_ORDER


ARRAY_RE = re.compile(
    r"(static const u16 s(?P<name>\w+)EggMoveLearnset\[\] = \{\n)"
    r"(?P<body>.*?)"
    r"(\n\};)",
    re.DOTALL,
)

EGG_MOVE_ADDITIONS = {
    "TREECKO": ("MOVE_LEAF_BLADE",),
}


def constant_name(camel_name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_name).upper()


def load_egg_moves(source_dir: pathlib.Path) -> dict[str, list[str]]:
    egg_moves = {}
    for source_name in LEARNSET_SOURCE_ORDER:
        with open(source_dir / source_name) as source_file:
            source = json.load(source_file)
        for species, learnset in source.items():
            egg_moves.setdefault(species, learnset["EggMoves"])

    for species, additions in EGG_MOVE_ADDITIONS.items():
        for move in additions:
            if move not in egg_moves[species]:
                egg_moves[species].append(move)
    return egg_moves


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(f"Usage: {sys.argv[0]} SOURCE_DIR EGG_MOVES_HEADER")

    source_dir = pathlib.Path(sys.argv[1])
    output_path = pathlib.Path(sys.argv[2])
    egg_moves = load_egg_moves(source_dir)
    old_content = output_path.read_text()

    def replace_array(match: re.Match) -> str:
        species = constant_name(match.group("name"))
        if species not in egg_moves:
            return match.group(0)
        moves = egg_moves[species] + ["MOVE_UNAVAILABLE"]
        body = "\n".join(f"    {move}," for move in moves)
        return match.group(1) + body + match.group(4)

    new_content = ARRAY_RE.sub(replace_array, old_content)
    output_path.write_text(new_content)


if __name__ == "__main__":
    main()
