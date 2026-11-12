#!/usr/bin/env python3
"""Self-tests for the story-note parser and renderer.

Run directly; exits non-zero on failure. No test framework needed because the
wiki build only guarantees Python 3.12.

    python3 plastic_ox/story/test_story_notes.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import story_notes  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        FAILURES.append(f"{name}{': ' + detail if detail else ''}")


def test_front_matter() -> None:
    text = (
        "---\n"
        "title: Demo Town\n"
        "slug: demo-town\n"
        "maps: [A_hns, B_hns]\n"
        "flags:\n"
        "  - FLAG_ONE\n"
        "  - FLAG_TWO\n"
        "quoted: \"a: b\"\n"
        "act: 2\n"
        "---\n\n## Snapshot\n\ntext\n"
    )
    meta, body = story_notes.parse_front_matter(text)
    check("inline list", meta["maps"] == ["A_hns", "B_hns"], str(meta["maps"]))
    check("block list", meta["flags"] == ["FLAG_ONE", "FLAG_TWO"], str(meta["flags"]))
    check("quoted colon", meta["quoted"] == "a: b", str(meta["quoted"]))
    check("int", meta["act"] == 2, str(meta["act"]))
    check("body", body.strip() == "## Snapshot\n\ntext", repr(body))


def test_sections() -> None:
    body = "## A\n\nalpha\n\n## B\n\nbeta\n"
    sections = story_notes.split_sections(body)
    check("sections", sections == {"A": "alpha", "B": "beta"}, str(sections))


def test_render_inline() -> None:
    cases = {
        "plain": ("hello", "<p>hello</p>"),
        "bold": ("**bold**", "<p><strong>bold</strong></p>"),
        "italic": ("*it*", "<p><em>it</em></p>"),
        "code": ("`a*b`", "<p><code>a*b</code></p>"),
        "bold around code with stars": (
            "**exist nowhere in `data/**/*.inc`**",
            "<p><strong>exist nowhere in <code>data/**/*.inc</code></strong></p>",
        ),
        "bold with nested italic": (
            "**The *Tale* ends.**",
            "<p><strong>The <em>Tale</em> ends.</strong></p>",
        ),
        "link": ("[x](https://e.test)", '<p><a href="https://e.test">x</a></p>'),
    }
    for name, (source, expected) in cases.items():
        actual = story_notes.render_markdown(source)
        check(f"render {name}", actual == expected, f"{actual!r} != {expected!r}")


def test_render_blocks() -> None:
    table = "| A | B |\n| --- | --- |\n| 1 | 2 |\n"
    html = story_notes.render_markdown(table)
    check("table head", "<th>A</th>" in html, html)
    check("table cell", "<td>2</td>" in html, html)

    quote = "> a line\n> continued\n"
    html = story_notes.render_markdown(quote)
    check("blockquote", "<blockquote>a line continued</blockquote>" in html, html)

    listed = "- one\n  continued here\n- two\n"
    html = story_notes.render_markdown(listed)
    check("list continuation", "<li>one continued here</li>" in html, html)
    check("two items", html.count("<li>") == 2, html)

    ordered = "1. first\n2. second\n"
    html = story_notes.render_markdown(ordered)
    check("ordered list", "<ol><li>first</li><li>second</li></ol>" in html, html)

    code = "```\na ** b\n```\n"
    html = story_notes.render_markdown(code)
    check("fenced code", "<pre><code>a ** b</code></pre>" in html, html)


def test_notes_render_clean() -> None:
    notes = story_notes.load_notes(strict=False)
    check("notes exist", len(notes) > 0)
    for note in notes:
        for section in story_notes.REQUIRED_SECTIONS:
            if section not in note.sections:
                continue
            html = note.section_html(section)
            # Unbalanced ** leaks into visible text; code spans may legitimately
            # contain ** (globs), so strip them before looking.
            stripped = re.sub(r"<code>.*?</code>", "", html, flags=re.S)
            check(f"{note.slug}/{section} balanced bold", "**" not in stripped)
            check(f"{note.slug}/{section} no table pipes", " | " not in stripped)


def main() -> int:
    test_front_matter()
    test_sections()
    test_render_inline()
    test_render_blocks()
    test_notes_render_clean()
    if FAILURES:
        print("FAILED:")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"story-note tests passed ({len(story_notes.load_notes(strict=False))} notes rendered)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
