# Story note editor

A local, accessible editor for the Plastic Ox wiki and its design notes. Browse
the generated wiki, edit the markdown note behind a location, check it against
the ROM source, and export the diff as a direction bundle for an implementing
agent.

It uses only the Python standard library. It runs on `127.0.0.1`, writes with a
per-process token and same-origin checks, and never commits anything.

## Start

From the repository root:

```sh
python3 plastic_ox/wiki/editor/serve.py
# http://127.0.0.1:8765/edit/
```

Options:

```sh
python3 plastic_ox/wiki/editor/serve.py --port 9000
python3 plastic_ox/wiki/editor/serve.py --open      # open the browser
python3 plastic_ox/wiki/editor/serve.py --port 0    # pick a free port
```

The wiki at `http://127.0.0.1:8765/wiki/index.html` gains two links on every
page: **Edit notes** in the top bar and **Edit this note** in that location's
Story notes section. The story index gets an **edit** link per row. The editor
can also be reached directly at `/edit/<slug>`.

The generated **Region map** at `/wiki/region.html` is part of the same wiki:
click any stop, or use Previous/Next to follow the story. It shows each
location's Key NPCs separately from its standard talk-only NPCs.

## The workflow

1. **Navigate.** Use the wiki normally, or use the editor's filterable note
   sidebar. Notes are grouped by story act.
2. **Edit.** The Write tab holds the whole markdown file, including front
   matter. Section jumps put the caret on `## Snapshot`, `## Key interactions`,
   and the rest. **Add interaction row** appends a blank row to the Key
   interactions table.
3. **Check.** The validator runs in-process against `data/`, `include/`, and
   `src/data/`; it reports unknown maps, flags, trainers, items, species, script
   labels, missing sections, and section-order problems. Checking does not save.
4. **Save.** `Ctrl`/`Cmd` + `S`, or the Save button. The note is written
   atomically, and the wiki is rebuilt by default so the page you came from is
   current. The status bar reports whether the rebuild succeeded.
5. **Compare.** The Diff tab shows the note's uncommitted diff against git
   `HEAD`, including the `+` and `-` markers in text, not just color.
6. **Direct.** The Direction tab asks what should improve and writes a bundle
   under `plastic_ox/story/directions/`. The bundle contains the note diff,
   the Key interactions table, grounded map facts, validation, and your brief.
   **Copy hand-off message** puts a ready-to-paste instruction on the clipboard.

Nothing is committed. Review and commit the note changes yourself, or hand the
direction bundle to the superagent and let it implement from the note.

To add a note for a new location, copy `plastic_ox/story/TEMPLATE.md` to
`plastic_ox/story/locations/<slug>.md`, fill in the front matter, and reload
the editor. The sidebar reads the directory on every request.

## Accessibility

The editor is built around native controls: links, buttons, inputs, a textarea,
`<fieldset>`, `<details>`, and `<dialog>`.

- Skip link to the main editor; landmark regions (`header`, `nav`, `main`) and a
  labelled note navigation.
- Proper ARIA tabs with roving tabindex, Left/Right/Home/End, `aria-selected`,
  and labelled tab panels.
- Visible focus rings on every control; text and diff status are never conveyed
  by color alone.
- `role="status"` and `aria-live="polite"` for saves, checks, exports, and
  filter results; validation errors are normal list items with the word
  "Error" in text.
- Display panel: Normal/Large/Larger text, high contrast, underlined links, and
  reduced motion, all persisted in the browser. The page also respects
  `prefers-reduced-motion`.
- Draft recovery: unsaved text is kept in `localStorage`; if you navigate away,
  the editor offers to restore the draft rather than silently discarding it.
- Unsaved-change guard on leaving the page, plus an optimistic-concurrency check
  that refuses a save if the file changed on disk since it was loaded.

Keyboard shortcuts:

| Keys | Action |
| --- | --- |
| `Ctrl`/`Cmd` + `S` | Save |
| `Ctrl`/`Cmd` + `Enter` | Check without saving |
| `Alt` + `1`…`4` | Write, Preview, Diff, Direction |
| `/` | Focus the note filter (when not typing) |
| `?` | Open the shortcut dialog |
| `Esc` | Close the display panel or dialog |

Deep links: `/edit/<slug>#preview`, `#diff`, and `#direction` open that tab.

## Routes

| Route | Purpose |
| --- | --- |
| `/` | Redirect to the wiki |
| `/wiki/…` | Generated wiki, with edit links injected at serve time |
| `/edit/` | Note index |
| `/edit/<slug>` | Note editor |
| `/api/notes` | Note index JSON |
| `/api/note/<slug>` | Note + validation + diff + map facts |
| `POST /api/note/<slug>` | Save (`markdown`, `rebuild`, `base_mtime`) |
| `POST /api/parse` | Validate/preview unsaved markdown |
| `POST /api/direction` | Write a direction bundle |
| `POST /api/rebuild` | Rebuild the wiki |
| `/directions/…` | Exported bundles |

The injected edit links exist only in the served HTML; `plastic_ox/wiki/site/`
is never rewritten by the server.

## Direction bundles

The editor calls `plastic_ox/story/direction.py`, which is also a standalone
CLI:

```sh
python3 plastic_ox/story/direction.py --slug ecruteakcity-hns \
  --intent "Give each gym attendant a distinct pre-battle line."
python3 plastic_ox/story/direction.py --all-dirty
python3 plastic_ox/story/direction.py --slug route29-hns --stdout
```

Each bundle is `<timestamp>-<slug>.md` plus a `.json` sidecar. See
`plastic_ox/story/directions/README.md` for the hand-off contract.

## Tests

```sh
python3 plastic_ox/wiki/editor/test_editor.py
```

The suite covers note parsing, preview payloads, wiki-link injection, path
traversal, direction bundle contents in a temporary git repo, token-protected
saves, stale-save conflicts, malformed front matter, and bundle export over
HTTP. It creates a temporary note and removes it and its bundle afterwards.

## Notes on safety

- The server binds to `127.0.0.1` by default. Do not expose it on a network.
- Writes require the token embedded in the editor page and a same-origin
  request; cross-origin `POST`s are refused.
- Slugs are validated, paths are resolved under their allowed directory, and
  note writes are atomic.
- The server serves only the generated wiki, the two editor assets, and
  direction bundles.
