#!/usr/bin/env python3
"""Aggregate the known gaps and open questions from the story notes.

Every note ends with **Known gaps** in ``## Implementation hooks`` and a list in
``## Open questions``. This tool prints them as one triage report so a human or
the superagent can see what the review actually found without opening 61 files.

    python3 plastic_ox/story/gaps_report.py
    python3 plastic_ox/story/gaps_report.py --act 2
    python3 plastic_ox/story/gaps_report.py --markdown
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import story_notes  # noqa: E402


def known_gaps(note: story_notes.Note) -> list[str]:
    gaps: list[str] = []
    for line in note.section("Implementation hooks").splitlines():
        stripped = line.strip()
        if not stripped.startswith(("- ", "* ")):
            continue
        text = stripped[2:].strip()
        if text.lower().startswith("known gaps"):
            gaps.append(text.split(":", 1)[-1].strip())
    if not gaps:
        match = re.search(r"Known gaps?:\s*(.+)", note.section("Implementation hooks"), re.I | re.S)
        if match:
            gaps.append(" ".join(match.group(1).split())[:600])
    return [gap for gap in gaps if gap]


def open_questions(note: story_notes.Note) -> list[str]:
    return [
        line.strip()[2:].strip()
        for line in note.section("Open questions").splitlines()
        if line.strip().startswith(("- ", "* "))
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--act", type=int, help="only this act")
    parser.add_argument("--markdown", action="store_true", help="emit a markdown report")
    args = parser.parse_args()

    notes = story_notes.load_notes(strict=False)
    if args.act:
        notes = [note for note in notes if note.act == args.act]
    notes = [note for note in notes if known_gaps(note) or open_questions(note)]

    if args.markdown:
        print("# Story-note gaps and open questions\n")
        print("Generated from `plastic_ox/story/locations/`. Edit the notes, not this file.\n")
    for note in notes:
        if not args.markdown:
            print(f"\n{note.title} ({note.slug}) — act {note.act}, {note.meta.get('stage', '')}")
        else:
            print(f"\n## {note.title} (`{note.slug}`)\n")
            print(f"Act {note.act} · {note.meta.get('stage', '')} · status `{note.meta.get('status')}`\n")
        for gap in known_gaps(note):
            print(f"- **Gap:** {gap}")
        for question in open_questions(note):
            print(f"- **Question:** {question}")
    if not args.markdown:
        total_gaps = sum(len(known_gaps(note)) for note in notes)
        total_questions = sum(len(open_questions(note)) for note in notes)
        print(f"\n{len(notes)} notes, {total_gaps} gap bullet(s), {total_questions} open question(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
