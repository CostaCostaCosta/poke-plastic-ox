# Plastic Ox Wiki

A generated, Bulbapedia-inspired static wiki for the routes, cities, towns, and caves in
the Plastic Ox region. Every gameplay table is read from the ROM source; do not
edit files under `site/` by hand.

## Build

From the repository root:

```sh
python3 plastic_ox/wiki/build_wiki.py
```

Then open `plastic_ox/wiki/site/index.html`, or serve it locally:

```sh
python3 -m http.server 8000 --directory plastic_ox/wiki/site
```

## Edit the story notes

For editing rather than reading, start the note editor instead:

```sh
python3 plastic_ox/wiki/editor/serve.py
# http://127.0.0.1:8765/edit/
```

It serves the same generated wiki with **Edit this note** links, validates each
note against the ROM data as you write, saves the markdown atomically, rebuilds
the wiki, and exports the uncommitted diff as a direction bundle under
`plastic_ox/story/directions/`. The editor and its keyboard/accessibility
features are documented in `plastic_ox/wiki/editor/README.md`.

## Region map

The build also writes `site/region.html`, a clickable story-ordered map of the
region. Every location is a stop; **Previous** and **Next** follow the
`STORY_ORDER` in `plastic_ox/story/region.py`. Main-line notes are numbered and
supporting/audit notes are marked and skipped by default.

Selecting a stop shows its summary, wiki link, and two separate NPC lists:

- **Key NPCs** act on the player: trainer battles, gifts, in-game trades, shops,
  healing, path/gate changes, scene triggers, dialogue choices, and state-gated
  objects.
- **Standard NPCs** are talk-only people and flavour.

Classification is grounded in the resolved scripts plus each note's Key
interactions table, and is shared by the location pages, so a page's Key NPCs
section contains only functional NPCs. The classifier lives in
`plastic_ox/story/npc_roles.py`.

The page also links the older physical design SVG as a secondary view. The SVG
is a design sketch, not a verified progression graph.

Each location page also renders its design note from
`plastic_ox/story/locations/<page-slug>.md`: plot points, key interactions,
dialogue guidance, and inspiration. Notes are validated against the ROM data by
`python3 plastic_ox/story/check_story_notes.py`. The standalone
`site/story.html` page indexes every note by act.

The generator reads:

- `plastic_ox/alpha/region_manifest.json` for Plastic Ox map membership
- `plastic_ox/story/locations/*.md` for the per-location story notes
- `data/maps/*/map.json` for map metadata, NPC events, connections, and hidden items
- `data/maps/*/scripts.inc` and `data/scripts/*.inc` for trainers and item scripts
- `src/data/wild_encounters.json` for Plastic Ox-owned (`gPox*`) encounter slots
  and rates; legacy FRLG/Hoenn tables that share reused map IDs are excluded
- `src/data/trainers.party` for trainer metadata and teams

Run `python3 plastic_ox/wiki/build_wiki.py --check` in CI to fail when generated
pages are stale. `make validate` in this directory runs both the note validator
and the freshness check; `make story` validates notes only.

The build is deterministic and writes a source fingerprint (ROM data plus story
notes) to `site/build.json`.
