#!/usr/bin/env python3
"""Validate Plastic Ox story notes against the checkout.

This is the contract that keeps the markdown honest. It checks that every wiki
location has a note, that front matter is complete, that each note claims maps
that exist, and that every identifier a note mentions (map, flag, trainer, item,
species, script label) is real. Run it after editing notes, or in CI.

    python3 plastic_ox/story/check_story_notes.py
    python3 plastic_ox/story/check_story_notes.py --quiet
    python3 plastic_ox/story/check_story_notes.py --note lavendertown-hns
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "plastic_ox/wiki"))

import story_notes  # noqa: E402
import build_wiki as wiki  # noqa: E402

FRONT_KEYS = ("title", "slug", "kind", "act", "stage", "depth", "wiki", "maps", "status")
DEPTHS = {"full", "supporting"}
STATUSES = {"draft", "drafted", "reviewed", "implemented"}
IDENT_RE = re.compile(r"\b(?:MAP|FLAG|TRAINER|ITEM|SPECIES|VAR)_[A-Z0-9_]+\b")
MAP_DIR_RE = re.compile(r"\b(?:[A-Z][A-Za-z0-9]*(?:_hns|_Frlg|_FRLG)|PlasticOx_[A-Za-z0-9]+)\b")
SCRIPT_RE = re.compile(r"\b(?:Pox_[A-Za-z0-9_]+|[A-Za-z0-9_]+_EventScript_[A-Za-z0-9_]+)\b")


class Index:
    """Lazy indexes over the checkout; built once per run."""

    def __init__(self) -> None:
        self._maps: set[str] | None = None
        self._map_ids: set[str] | None = None
        self._flags: set[str] | None = None
        self._trainers: set[str] | None = None
        self._items: set[str] | None = None
        self._species: set[str] | None = None
        self._vars: set[str] | None = None
        self._scripts: set[str] | None = None

    @staticmethod
    def _defines(*paths: Path, prefix: str) -> set[str]:
        found: set[str] = set()
        define_re = re.compile(rf"#define\s+({prefix}[A-Z0-9_]+)")
        enum_re = re.compile(rf"^\s*({prefix}[A-Z0-9_]+)\s*[=,]", re.M)
        for path in paths:
            if path.exists():
                text = path.read_text(encoding="utf-8", errors="replace")
                found.update(define_re.findall(text))
                found.update(enum_re.findall(text))
        return found

    @property
    def maps(self) -> set[str]:
        if self._maps is None:
            self._maps = {path.name for path in (ROOT / "data/maps").iterdir() if path.is_dir()}
        return self._maps

    @property
    def map_ids(self) -> set[str]:
        if self._map_ids is None:
            ids = set()
            for path in (ROOT / "data/maps").glob("*/map.json"):
                try:
                    ids.add(json.loads(path.read_text(encoding="utf-8")).get("id", ""))
                except json.JSONDecodeError:
                    pass
            self._map_ids = ids
        return self._map_ids

    @property
    def flags(self) -> set[str]:
        if self._flags is None:
            const = ROOT / "include/constants"
            self._flags = self._defines(
                const / "flags.h",
                const / "flags_frlg.h",
                const / "plastic_ox_flags.h",
                const / "plastic_ox_story.h",
                prefix="FLAG_",
            )
        return self._flags

    @property
    def trainers(self) -> set[str]:
        if self._trainers is None:
            found: set[str] = set()
            for name in ("trainers.party", "trainers_frlg.party"):
                path = ROOT / "src/data" / name
                if path.exists():
                    found.update(re.findall(r"^===\s+(TRAINER_[A-Z0-9_]+)\s*===$", path.read_text(encoding="utf-8"), re.M))
            self._trainers = found | self._defines(ROOT / "include/constants/opponents.h", prefix="TRAINER_")
        return self._trainers

    @property
    def items(self) -> set[str]:
        if self._items is None:
            self._items = self._defines(ROOT / "include/constants/items.h", prefix="ITEM_")
        return self._items

    @property
    def species(self) -> set[str]:
        if self._species is None:
            self._species = self._defines(ROOT / "include/constants/species.h", prefix="SPECIES_")
        return self._species

    @property
    def vars(self) -> set[str]:
        if self._vars is None:
            self._vars = self._defines(ROOT / "include/constants/vars.h", prefix="VAR_")
        return self._vars

    @property
    def scripts(self) -> set[str]:
        if self._scripts is None:
            labels = set()
            label_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?:::|:)$", re.M)
            for path in (ROOT / "data").glob("**/*.inc"):
                labels.update(label_re.findall(path.read_text(encoding="utf-8", errors="replace")))
            self._scripts = labels
        return self._scripts


def check_note(note: story_notes.Note, index: Index, wiki_pages: dict[str, dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    meta = note.meta
    text = note.body

    for key in FRONT_KEYS:
        if key not in meta:
            errors.append(f"front matter missing '{key}'")
    if meta.get("slug") != note.slug:
        errors.append(f"slug '{meta.get('slug')}' does not match filename '{note.slug}'")
    if note.meta.get("depth") not in DEPTHS:
        warnings.append(f"depth '{note.depth}' not in {sorted(DEPTHS)}")
    if meta.get("status") not in STATUSES:
        warnings.append(f"status '{meta.get('status')}' not in {sorted(STATUSES)}")

    if not note.maps:
        errors.append("'maps' is empty")
    for map_name in note.all_maps:
        if map_name not in index.maps:
            errors.append(f"map '{map_name}' is not a directory under data/maps/")

    wiki_slug = str(meta.get("wiki", ""))
    if wiki_slug in ("none", ""):
        if "## Open questions" not in text:
            errors.append("wiki is 'none' but there is no '## Open questions' explaining why")
    elif wiki_slug not in wiki_pages:
        errors.append(f"wiki slug '{wiki_slug}' is not a generated wiki page")
    else:
        page_map = wiki_pages[wiki_slug]["name"]
        if page_map not in note.all_maps:
            errors.append(f"wiki page map '{page_map}' is not listed in maps/also_maps")

    headings = list(note.sections)
    missing = [name for name in story_notes.REQUIRED_SECTIONS if name not in note.sections]
    if missing:
        errors.append(f"missing sections: {', '.join(missing)}")
    present = [name for name in headings if name in story_notes.REQUIRED_SECTIONS]
    expected = [name for name in story_notes.REQUIRED_SECTIONS if name in present]
    if present != expected:
        errors.append(f"section order: {present} should be {expected}")
    for name in story_notes.REQUIRED_SECTIONS:
        if name in note.sections and not note.sections[name].strip():
            errors.append(f"section '{name}' is empty")

    front_matter_sets = (
        ("flags", "FLAG_", index.flags),
        ("trainers", "TRAINER_", index.trainers),
        ("items", "ITEM_", index.items),
    )
    for key, prefix, known in front_matter_sets:
        for value in meta.get(key, []) or []:
            value = str(value)
            if not value.startswith(prefix):
                errors.append(f"front matter {key}: '{value}' is not a {prefix}* identifier")
            elif value not in known:
                errors.append(f"front matter {key}: unknown {value}")
    for badge in meta.get("badges", []) or []:
        if not isinstance(badge, int) or not 1 <= badge <= 8:
            errors.append(f"front matter badges: '{badge}' is not 1-8")

    for ident in sorted(set(IDENT_RE.findall(text))):
        if ident.startswith("MAP_"):
            if ident not in index.map_ids:
                errors.append(f"unknown map id {ident}")
        elif ident.startswith("FLAG_"):
            if ident not in index.flags:
                errors.append(f"unknown flag {ident}")
        elif ident.startswith("TRAINER_"):
            if ident not in index.trainers:
                errors.append(f"unknown trainer {ident}")
        elif ident.startswith("ITEM_"):
            if ident not in index.items:
                errors.append(f"unknown item {ident}")
        elif ident.startswith("SPECIES_"):
            if ident not in index.species:
                errors.append(f"unknown species {ident}")
        elif ident.startswith("VAR_"):
            if ident not in index.vars:
                errors.append(f"unknown var {ident}")

    known_maps = index.maps
    for token in sorted(set(MAP_DIR_RE.findall(text))):
        if token.startswith(("OBJ_EVENT_", "MOVEMENT_TYPE_", "MAP_TYPE_", "MAPSEC_", "MAP_BATTLE_")):
            continue
        if token in {"IS_FRLG", "IS_HNS", "IS_EMERALD", "IS_RUBY", "IS_SAPPHIRE"}:
            continue
        if token not in known_maps:
            warnings.append(f"map-like name '{token}' is not a map directory (fine if it is prose)")

    for label in sorted(set(SCRIPT_RE.findall(text))):
        if label not in index.scripts:
            warnings.append(f"script label '{label}' not found in data/**/*.inc")
    return errors, warnings


def dialogue_seeds(note: story_notes.Note) -> list[str]:
    quotes = []
    for line in note.section("Dialogue guidance").splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            quote = " ".join(stripped[1:].split())
            if len(quote) > 40:
                quotes.append(quote)
    return quotes


def story_map_coverage(notes: list[story_notes.Note]) -> list[str]:
    groups = json.loads((ROOT / "data/maps/map_groups.json").read_text(encoding="utf-8"))
    wanted = set()
    for group in ("gMapGroup_PlasticOxStory", "gMapGroup_PlasticOxV7"):
        wanted.update(groups.get(group, []))
    claimed = {map_name for note in notes for map_name in note.all_maps}
    return sorted(wanted - claimed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--note", help="check one note by slug")
    parser.add_argument("--quiet", action="store_true", help="only print failures")
    args = parser.parse_args()

    if args.note:
        path = story_notes.NOTES_DIR / f"{args.note}.md"
        if not path.exists():
            print(f"no note named {args.note}", file=sys.stderr)
            return 1
        notes = [story_notes.load_note(path)]
    else:
        notes = story_notes.load_notes()
    pages = {wiki.page_slug(data): data for data in wiki.read_maps()}
    index = Index()

    total_errors = 0
    total_warnings = 0
    report: list[str] = []
    claimed: dict[str, str] = {}
    for note in notes:
        errors, warnings = check_note(note, index, pages)
        for map_name in note.all_maps:
            if map_name in claimed and claimed[map_name] != note.slug:
                warnings.append(f"map '{map_name}' is also claimed by {claimed[map_name]}")
            claimed.setdefault(map_name, note.slug)
        if errors or warnings or not args.quiet:
            report.append(f"\n[{note.slug}] {note.title}  ({len(note.all_maps)} maps, depth={note.depth})")
            report.extend(f"  ERROR   {item}" for item in errors)
            report.extend(f"  warning {item}" for item in warnings)
        total_errors += len(errors)
        total_warnings += len(warnings)

    if not args.note:
        uncovered_pages = sorted(slug for slug in pages if not any(
            str(note.meta.get("wiki")) == slug for note in story_notes.load_notes()
        ))
        if uncovered_pages:
            total_errors += len(uncovered_pages)
            report.append(f"\nWiki pages without a story note ({len(uncovered_pages)}):")
            report.extend(f"  ERROR   {slug}.html" for slug in uncovered_pages)
        all_notes = story_notes.load_notes()
        owners: dict[str, list[str]] = {}
        for note in all_notes:
            for quote in dialogue_seeds(note):
                owners.setdefault(quote, []).append(note.slug)
        duplicate_seeds = {quote: slugs for quote, slugs in owners.items() if len(slugs) > 1}
        if duplicate_seeds:
            report.append(f"\nDuplicate dialogue seeds across notes ({len(duplicate_seeds)}):")
            for quote, slugs in duplicate_seeds.items():
                report.append(f"  warning {quote[:70]}… used by {', '.join(slugs)}")
        uncovered_story = story_map_coverage(all_notes)
        if uncovered_story:
            total_errors += len(uncovered_story)
            report.append(f"\nStory maps not claimed by any note ({len(uncovered_story)}):")
            report.extend(f"  ERROR   {map_name}" for map_name in uncovered_story)

    print("\n".join(report).strip("\n"))
    print(
        f"\n{len(notes)} notes checked, {len(pages)} wiki pages, "
        f"{total_errors} error(s), {total_warnings} warning(s)."
    )
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
