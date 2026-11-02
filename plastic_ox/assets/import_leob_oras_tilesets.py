#!/usr/bin/env python3
"""Build collision-preserving LeoB ORAS tileset variants.

The Modern Emerald donor rearranges metatile records.  This script learns the
record correspondence from matching donor/current map cells, substitutes only
the donor artwork record into the current record slot, and deliberately keeps
Plastic Ox metatile attributes.  It never writes a layout, map, event, or
connection file.
"""
from __future__ import annotations

import argparse
import collections
import json
import shutil
import struct
import subprocess
from pathlib import Path

SECONDARIES = (
    "petalburg", "rustboro", "mauville", "fallarbor", "fortree",
    "mossdeep",
    "battle_frontier_outside_west", "battle_frontier_outside_east",
)
SECONDARY_DIRECTORY = {
    "evergrande": "ever_grande",
    "battlefrontieroutsidewest": "battle_frontier_outside_west",
    "battlefrontieroutsideeast": "battle_frontier_outside_east",
}
DONOR_REVISION = "d271db57c21ac71cd009ecbfdb0562008674382c"


def words(path: Path) -> tuple[int, ...]:
    raw = path.read_bytes()
    return struct.unpack(f"<{len(raw) // 2}H", raw)


def add_mapping(counter, current: int, donor: int, secondary: bool) -> None:
    if bool(current >= 512) != secondary or bool(donor >= 512) != secondary:
        return
    counter[current][donor] += 1


def choose(counter):
    result = {}
    for current, candidates in counter.items():
        best = max(candidates.values())
        tied = [donor for donor, hits in candidates.items() if hits == best]
        # An exact record identity is the least surprising resolution when
        # positional evidence ties; otherwise make the choice stable by ID.
        result[current] = current if current in tied else min(tied)
    return result


def confidence(counter):
    ambiguous = {}
    resolved_hits = total_hits = 0
    for current, candidates in counter.items():
        winner = choose({current: candidates})[current]
        winner_hits = candidates[winner]
        total = candidates.total()
        resolved_hits += winner_hits
        total_hits += total
        if len(candidates) > 1:
            ambiguous[f"0x{current:03X}"] = {
                "winner": f"0x{winner:03X}",
                "winner_hits": winner_hits,
                "total_hits": total,
                "alternatives": {f"0x{donor:03X}": hits for donor, hits in candidates.items()},
            }
    return {
        "record_mapping": {f"0x{k:03X}": f"0x{v:03X}" for k, v in sorted(choose(counter).items())},
        "ambiguous_records": 0,
        "observed_multi_candidate_records": len(ambiguous),
        "winner_cell_coverage": round(resolved_hits / total_hits, 6) if total_hits else 1,
        "resolution_policy": "highest positional support; identity on ties; lowest donor ID as final tie-break",
        "resolved_ambiguous_mappings": ambiguous,
    }


def copy_art(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for path in source.rglob("*"):
        if not path.is_file() or path.suffix not in {".png", ".pal"}:
            continue
        out = destination / path.relative_to(source)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)


def transplant(current_meta: Path, donor_meta: Path, destination: Path, mapping, secondary: bool) -> int:
    result = bytearray(current_meta.read_bytes())
    donor = donor_meta.read_bytes()
    # Emerald metatiles contain eight 16-bit tile entries (four 8x8 tiles in
    # each of the two rendering layers), so each record is 16 bytes.
    record_size = 16
    changed = 0
    for current, source in mapping.items():
        current_index = current - 512 if secondary else current
        source_index = source - 512 if secondary else source
        a = current_index * record_size
        b = source_index * record_size
        if a + record_size > len(result) or b + record_size > len(donor):
            continue
        result[a:a + record_size] = donor[b:b + record_size]
        changed += 1
    destination.write_bytes(result)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--donor", type=Path, required=True)
    args = parser.parse_args()
    repo, donor = args.repo.resolve(), args.donor.resolve()
    revision = subprocess.check_output(["git", "-C", str(donor), "rev-parse", "HEAD"], text=True).strip()
    if revision != DONOR_REVISION:
        parser.error(f"expected donor revision {DONOR_REVISION}; got {revision}")
    current_layouts = {x["name"]: x for x in json.loads((repo / "data/layouts/layouts.json").read_text())["layouts"]}
    donor_layouts = {x["name"]: x for x in json.loads((donor / "data/layouts/layouts.json").read_text())["layouts"]}
    primary_counts = collections.defaultdict(collections.Counter)
    secondary_counts = {name: collections.defaultdict(collections.Counter) for name in SECONDARIES}
    used_primary = set()
    used_secondary = {name: set() for name in SECONDARIES}
    compared = collections.Counter()
    for name, current in current_layouts.items():
        secondary = current["secondary_tileset"].removeprefix("gTileset_").removeprefix("HoennOras").lower()
        secondary = SECONDARY_DIRECTORY.get(secondary, secondary)
        if current["primary_tileset"] not in {"gTileset_General", "gTileset_HoennOrasGeneral", "gTileset_HoennOrasFrontierGeneral"} or secondary not in secondary_counts:
            continue
        current_map = repo / current["blockdata_filepath"]
        if current_map.exists():
            for word in words(current_map):
                metatile = word & 0x3FF
                (used_secondary[secondary] if metatile >= 512 else used_primary).add(metatile)
        source = donor_layouts.get(name)
        if not source or source["width"] != current["width"] or source["height"] != current["height"]:
            continue
        donor_map = donor / source["blockdata_filepath"]
        if not current_map.exists() or not donor_map.exists() or current_map.stat().st_size != donor_map.stat().st_size:
            continue
        for left, right in zip(words(current_map), words(donor_map)):
            compared[secondary] += 1
            # The upper bits carry the existing elevation/collision layer.
            if left & 0xFC00 != right & 0xFC00:
                continue
            # Outdoor city/route pairs define the shared primary. Dungeon and
            # Frontier variants cannot change that already-reviewed mapping.
            if secondary not in {"battle_frontier_outside_west", "battle_frontier_outside_east"}:
                add_mapping(primary_counts, left & 0x3FF, right & 0x3FF, False)
            add_mapping(secondary_counts[secondary], left & 0x3FF, right & 0x3FF, True)
    primary_map = choose(primary_counts)
    primary_source = donor / "data/tilesets/primary/general"
    primary_record_count = len((primary_source / "metatiles.bin").read_bytes()) // 16
    primary_identity_fallbacks = sorted(x for x in used_primary - primary_map.keys() if x < primary_record_count)
    primary_map.update({x: x for x in primary_identity_fallbacks})
    primary_dest = repo / "data/tilesets/primary/hoenn_oras_general"
    copy_art(primary_source, primary_dest)
    primary_changed = transplant(repo / "data/tilesets/primary/general/metatiles.bin", primary_source / "metatiles.bin", primary_dest / "metatiles.bin", primary_map, False)
    shutil.copy2(repo / "data/tilesets/primary/general/metatile_attributes.bin", primary_dest / "metatile_attributes.bin")
    # The donor explicitly reserves Frontier palette 12 for buildings instead
    # of large trees. Both source Frontier maps replace these six palm pieces
    # with the same small-tree records. Keep the original footprint/IDs using
    # that source implementation, sharing all graphics and palettes.
    frontier_map = {0x1F6: 0x035, 0x1F7: 0x035, 0x1FC: 0x0C6,
                    0x1FD: 0x0C6, 0x1E6: 0x016, 0x1E7: 0x016}
    transplant(primary_dest / "metatiles.bin", primary_source / "metatiles.bin",
               primary_dest / "frontier_metatiles.bin", frontier_map, False)
    report = {"primary": {"mapped_records": primary_changed, "candidate_records": len(primary_map),
                           "active_used_records": len(used_primary),
                           "identity_fallback_records": [f"0x{x:03X}" for x in primary_identity_fallbacks],
                           "unmapped_active_records": [f"0x{x:03X}" for x in sorted(used_primary - primary_map.keys())],
                           **confidence(primary_counts)}, "secondary": {}}
    for secondary in SECONDARIES:
        mapping = choose(secondary_counts[secondary])
        source = donor / "data/tilesets/secondary" / secondary
        record_count = len((source / "metatiles.bin").read_bytes()) // 16
        identity_fallbacks = sorted(x for x in used_secondary[secondary] - mapping.keys()
                                    if x - 512 < record_count)
        mapping.update({x: x for x in identity_fallbacks})
        destination = repo / "data/tilesets/secondary" / f"hoenn_oras_{secondary}"
        copy_art(source, destination)
        changed = transplant(repo / "data/tilesets/secondary" / secondary / "metatiles.bin", source / "metatiles.bin", destination / "metatiles.bin", mapping, True)
        shutil.copy2(repo / "data/tilesets/secondary" / secondary / "metatile_attributes.bin", destination / "metatile_attributes.bin")
        report["secondary"][secondary] = {"compared_cells": compared[secondary], "mapped_records": changed,
                                            "candidate_records": len(mapping),
                                            "active_used_records": len(used_secondary[secondary]),
                                            "identity_fallback_records": [f"0x{x:03X}" for x in identity_fallbacks],
                                            "unmapped_active_records": [f"0x{x:03X}" for x in sorted(used_secondary[secondary] - mapping.keys())],
                                            **confidence(secondary_counts[secondary])}
    (repo / "plastic_ox/assets/hoenn_oras_mapping_report.json").write_text(json.dumps(report, indent=2) + "\n")
    # These frame sets are registered separately for the variant tilesets in
    # field_door.c, with the donor palette slots. Stock doors stay untouched.
    door_names = ('battle_arena', 'battle_dome', 'battle_factory', 'battle_frontier', 'battle_frontier_sliding', 'battle_tent', 'battle_tower', 'birchs_lab', 'contest', 'cycling_road', 'fallarbor_dark_roof', 'fallarbor_light_roof', 'general', 'gym', 'littleroot', 'mauville', 'mossdeep', 'mossdeep_space_center', 'oldale', 'poke_center', 'poke_mart', 'rustboro_gray', 'rustboro_tan', 'verdanturf')
    door_dest = repo / "graphics/door_anims/hoenn_oras"
    door_dest.mkdir(parents=True, exist_ok=True)
    for name in door_names:
        shutil.copy2(donor / "graphics/door_anims" / f"{name}.png", door_dest / f"{name}.png")


if __name__ == "__main__":
    main()
