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
