#!/usr/bin/env python3
"""Shared reader for Plastic Ox story notes.

Story notes live in ``plastic_ox/story/locations/<slug>.md``. They are the
human-editable design source for a location's plot, interactions, and dialogue
inspiration; the wiki renders them and agents read them before touching a map.

This module is dependency-free on purpose: the wiki build and the validator both
import it, and neither should need PyYAML.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NOTES_DIR = HERE / "locations"
TEMPLATE = HERE / "TEMPLATE.md"

REQUIRED_SECTIONS = (
    "Snapshot",
    "Plot points",
    "Key interactions",
    "Dialogue guidance",
    "Inspiration",
    "Implementation hooks",
)

LIST_KEYS = {
    "maps",
    "also_maps",
    "flags",
    "trainers",
    "items",
    "scripts",
    "connections",
    "badges",
}

# Sections whose prose is written for designers, not shown on the wiki page.
INTERNAL_SECTIONS = {"Implementation hooks", "Open questions"}


def _scalar(value: str):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_scalar(part) for part in inner.split(",")]
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value in ("true", "false"):
        return value == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Parse the small YAML subset used by story notes.

    Supports ``key: value``, ``key: [a, b]``, quoted values, and block lists
    (``key:`` followed by ``  - item`` lines). Raises ValueError on malformed
    front matter so a broken note fails the build instead of rendering wrong.
    """
    if not text.startswith("---\n"):
        raise ValueError("missing '---' front matter opener")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing closing '---' front matter fence")
    raw = text[4:end]
    body = text[end + 5:]
    meta: dict = {}
    pending_key: str | None = None
    for number, line in enumerate(raw.splitlines(), start=2):
        if not line.strip():
            continue
        if line.lstrip().startswith("- "):
            if pending_key is None:
                raise ValueError(f"line {number}: list item without a key")
            meta.setdefault(pending_key, []).append(_scalar(line.lstrip()[2:]))
            continue
        if ":" not in line:
            raise ValueError(f"line {number}: expected 'key: value', got {line!r}")
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"line {number}: empty key")
        if value == "":
            meta.setdefault(key, [])
            pending_key = key
        else:
            meta[key] = _scalar(value)
            pending_key = None
    for key in LIST_KEYS:
        if key in meta and not isinstance(meta[key], list):
            meta[key] = [meta[key]]
    return meta, body


def split_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = ""
    buffer: list[str] = []
    for line in body.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            if current or buffer:
                sections[current] = "\n".join(buffer).strip()
            current = match.group(1).strip()
            buffer = []
        else:
            buffer.append(line)
    if current or buffer:
        sections[current] = "\n".join(buffer).strip()
    return sections


# --- minimal markdown renderer -------------------------------------------
# Deliberately small: the notes use headings, paragraphs, lists, GFM tables,
# blockquotes, fenced code, inline code, bold, italic and http(s)/relative
# links. Anything else renders as literal text, which the validator flags.

_inline_code = re.compile(r"`([^`]+)`")
_bold = re.compile(r"\*\*(.+?)\*\*")
_italic = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_link = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def inline(text: str) -> str:
    # Protect code spans first: their contents may contain *, | or HTML.
    codes: list[str] = []

    def stash(match: re.Match) -> str:
        codes.append(f"<code>{html.escape(match.group(1), quote=False)}</code>")
        return f"\x00{len(codes) - 1}\x00"

    protected = _inline_code.sub(stash, text)
    out = html.escape(protected, quote=False)
    out = _bold.sub(r"<strong>\1</strong>", out)
    out = _italic.sub(r"<em>\1</em>", out)
    out = _link.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', out)
    for index, code in enumerate(codes):
        out = out.replace(f"\x00{index}\x00", code)
    return out


def _table(lines: list[str]) -> str:
    def cells(row: str) -> list[str]:
        row = row.strip().strip("|")
        return [cell.strip() for cell in row.split("|")]

    header = cells(lines[0])
    rows = [cells(line) for line in lines[2:]]
    head = "".join(f"<th>{inline(cell)}</th>" for cell in header)
    body = "".join(
        "<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def render_markdown(text: str) -> str:
    """Render a story-note section body to HTML."""
    lines = text.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    list_tag = ""
    index = 0

    def flush_paragraph() -> None:
        if paragraph:
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        nonlocal list_tag
        if list_items:
            items = "".join(f"<li>{inline(item)}</li>" for item in list_items)
            out.append(f"<{list_tag}>{items}</{list_tag}>")
            list_items.clear()
            list_tag = ""

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_list()
            index += 1
            continue
        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            block: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                block.append(lines[index])
                index += 1
            out.append("<pre><code>" + html.escape("\n".join(block)) + "</code></pre>")
            index += 1
            continue
        if stripped.startswith("|") and index + 1 < len(lines) and re.match(
            r"^\s*\|[\s:|-]+\|\s*$", lines[index + 1]
        ):
            flush_paragraph()
            flush_list()
            table_lines = [stripped, lines[index + 1].strip()]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            out.append(_table(table_lines))
            continue
        heading = re.match(r"^(#{3,4})\s+(.*)$", stripped)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            index += 1
            continue
        bullet = re.match(r"^[-*]\s+(.*)$", stripped)
        ordered = re.match(r"^\d+\.\s+(.*)$", stripped)
        if bullet or ordered:
            flush_paragraph()
            tag = "ul" if bullet else "ol"
            if list_tag and list_tag != tag:
                flush_list()
            list_tag = tag
            list_items.append((bullet or ordered).group(1))
            index += 1
            continue
        if list_items and line[:1].isspace() and not stripped.startswith(("|", ">", "```")):
            # Indented continuation of the previous list item.
            list_items[-1] = list_items[-1] + " " + stripped
            index += 1
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            flush_list()
            quote: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote.append(lines[index].strip()[1:].strip())
                index += 1
            out.append(f"<blockquote>{inline(' '.join(quote))}</blockquote>")
            continue
        flush_list()
        paragraph.append(stripped)
        index += 1
    flush_paragraph()
    flush_list()
    return "\n".join(out)


@dataclass
class Note:
    path: Path
    meta: dict = field(default_factory=dict)
    body: str = ""
    sections: dict[str, str] = field(default_factory=dict)

    @property
    def slug(self) -> str:
        return self.path.stem

    @property
    def title(self) -> str:
        return str(self.meta.get("title") or self.slug.replace("-", " ").title())

    @property
    def maps(self) -> list[str]:
        return [str(x) for x in self.meta.get("maps", [])]

    @property
    def also_maps(self) -> list[str]:
        return [str(x) for x in self.meta.get("also_maps", [])]

    @property
    def all_maps(self) -> list[str]:
        return list(dict.fromkeys(self.maps + self.also_maps))

    @property
    def depth(self) -> str:
        return str(self.meta.get("depth") or "full")

    @property
    def act(self) -> int:
        try:
            return int(self.meta.get("act") or 0)
        except (TypeError, ValueError):
            return 0

    def section(self, name: str) -> str:
        return self.sections.get(name, "")

    def section_html(self, name: str) -> str:
        return render_markdown(self.section(name))

    @property
    def dialogue_seed(self) -> str:
        """First blockquote in the dialogue guidance, used as a teaser."""
        for line in self.section("Dialogue guidance").splitlines():
            if line.strip().startswith(">"):
                return line.strip().lstrip("> ")
        return ""


def load_note(path: Path) -> Note:
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
    return Note(path=path, meta=meta, body=body, sections=split_sections(body))


def load_notes(directory: Path | None = None, strict: bool = True) -> list[Note]:
    directory = directory or NOTES_DIR
    if not directory.is_dir():
        return []
    notes = []
    for path in sorted(directory.glob("*.md")):
        if path.name == "TEMPLATE.md":
            continue
        try:
            notes.append(load_note(path))
        except (ValueError, OSError) as error:
            if strict:
                raise
            print(f"warning: skipping {path.name}: {error}")
    return sorted(notes, key=lambda note: (note.act, note.title.lower()))


def notes_by_map(notes: list[Note] | None = None) -> dict[str, Note]:
    notes = notes if notes is not None else load_notes()
    index: dict[str, Note] = {}
    for note in notes:
        for map_name in note.all_maps:
            index.setdefault(map_name, note)
    return index


if __name__ == "__main__":  # tiny self-check: parse every note
    loaded = load_notes()
    print(f"{len(loaded)} story notes")
    for item in loaded:
        missing = [name for name in REQUIRED_SECTIONS if name not in item.sections]
        print(f"  {item.slug:<32} act={item.act:<2} depth={item.depth:<10} maps={len(item.all_maps):<2} missing={missing}")
