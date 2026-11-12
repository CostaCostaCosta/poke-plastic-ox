#!/usr/bin/env python3
"""Render story notes into the static Plastic Ox wiki.

Kept separate from ``build_wiki.py`` so the note format and its presentation can
change without touching the ROM-data scraping. The wiki build imports this.
"""

from __future__ import annotations

import html

import story_notes

DISPLAY_SECTIONS = ("Plot points", "Key interactions", "Dialogue guidance", "Inspiration")
APPENDIX_SECTIONS = ("Implementation hooks", "Open questions")
ACT_LABELS = {
    1: "Act I — a familiar journey through an impossible region",
    2: "Act II — places remember what they used to be",
    3: "Act III — Team Rocket starts asking the same questions",
    4: "Act IV — Saffron finally opens",
    5: "Act V — back to Pokémon",
    6: "Postgame — the frontier and the islands",
}


def esc(value: object) -> str:
    return html.escape(str(value))


def note_for_map(index: dict[str, story_notes.Note], map_name: str) -> story_notes.Note | None:
    return index.get(map_name)


def meta_line(note: story_notes.Note) -> str:
    parts = []
    if note.meta.get("act"):
        parts.append(f"Act {note.act}")
    if note.meta.get("stage"):
        parts.append(str(note.meta["stage"]))
    if note.meta.get("depth"):
        parts.append(str(note.meta["depth"]))
    if note.meta.get("status"):
        parts.append(str(note.meta["status"]))
    return " · ".join(esc(part) for part in parts)


def render_body(note: story_notes.Note, sections: tuple[str, ...], title: str | None = None) -> str:
    out: list[str] = []
    if title:
        out.append(f"<h3>{esc(title)}</h3>")
    for name in sections:
        body = note.section(name)
        if not body:
            continue
        out.append(f"<h3>{esc(name)}</h3>")
        rendered = note.section_html(name)
        if name == "Snapshot":
            rendered = rendered.replace("<p>", '<p class="story-snapshot">', 1)
        out.append(rendered)
    return "\n".join(out)


def render_story_section(note: story_notes.Note) -> str:
    """Full story block embedded on a location page."""
    seed = note.dialogue_seed
    seeds_html = ""
    if seed:
        seeds_html = f'<div class="story-seeds"><blockquote><p>{esc(seed)}</p></blockquote></div>'
    appendix = render_body(note, APPENDIX_SECTIONS)
    appendix_html = (
        f'<details class="story-appendix"><summary>Implementation hooks and open questions</summary>{appendix}</details>'
        if appendix
        else ""
    )
    return f'''<section class="story" id="story">
<div class="story-head"><h2>Story notes</h2><span class="story-meta">{meta_line(note)}</span></div>
<div class="note-source">Design source: <code>{esc(note.path.relative_to(story_notes.ROOT))}</code></div>
<div class="story-note">{render_body(note, ("Snapshot", "Plot points", "Key interactions"))}</div>
<h2>Dialogue seeds</h2>
{seeds_html}
<div class="story-note">{render_body(note, ("Dialogue guidance", "Inspiration"))}</div>
{appendix_html}
</section>'''


def render_missing_section(map_title: str, wiki_slug: str) -> str:
    return f'''<section class="story" id="story"><h2>Story notes</h2>
<div class="source-note">No story note for {esc(map_title)} yet. Add
<code>plastic_ox/story/locations/{esc(wiki_slug)}.md</code> using
<code>plastic_ox/story/TEMPLATE.md</code>; it will appear here on the next build.</div></section>'''


def first_sentence(note: story_notes.Note, limit: int = 220) -> str:
    text = note.section("Snapshot").replace("\n", " ").replace("`", "").replace("**", "").strip()
    cut = text.find(". ")
    if cut != -1 and cut < limit:
        text = text[: cut + 1]
    return text[:limit] + ("…" if len(text) > limit else "")


def render_story_index(notes: list[story_notes.Note], wiki_pages: dict[str, dict], page_href) -> str:
    """A standalone story index page grouped by act."""
    by_act: dict[int, list[story_notes.Note]] = {}
    for note in notes:
        by_act.setdefault(note.act, []).append(note)

    buttons = ['<button class="active" data-story-filter="all">All acts</button>']
    for act in sorted(by_act):
        buttons.append(f'<button data-story-filter="{act}">Act {act}</button>')

    groups: list[str] = []
    for act in sorted(by_act):
        rows = []
        for note in by_act[act]:
            wiki_slug = str(note.meta.get("wiki", ""))
            href = page_href(wiki_slug) if wiki_slug in wiki_pages else None
            title_cell = (
                f'<h2><a href="{esc(href)}">{esc(note.title)}</a></h2>'
                if href
                else f"<h2>{esc(note.title)}</h2>"
            )
            seed = note.dialogue_seed
            seed_html = f'<blockquote><p>{esc(seed)}</p></blockquote>' if seed else ""
            rows.append(
                f'<article class="story-row"><div>{esc(note.meta.get("stage", ""))}</div>'
                f'<div>{title_cell}<span class="slug">{esc(note.slug)} · {esc(note.depth)} · {len(note.all_maps)} map(s)</span></div>'
                f'<p>{esc(first_sentence(note))}</p>{seed_html}</article>'
            )
        groups.append(
            f'<section data-story-act="{act}"><h2>{esc(ACT_LABELS.get(act, f"Act {act}"))}</h2>'
            f'<div class="story-index">{"".join(rows)}</div></section>'
        )

    return f'''<h1>Story notes</h1>
<p class="lede">One design note per town, route, cave, and landmark: the beats that happen there,
the interactions that must exist, and the voices that should carry the dialogue.
The notes live in <code>plastic_ox/story/locations/</code> and are validated against the ROM data.</p>
<div class="source-note">{len(notes)} notes covering {len(wiki_pages)} location pages. Edit a note,
run <code>python3 plastic_ox/wiki/build_wiki.py</code>, and this page and the location pages update.</div>
<div class="story-filters">{"".join(buttons)}</div>
{"".join(groups)}'''
