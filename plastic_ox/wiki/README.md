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

The generator reads:

- `plastic_ox/alpha/region_manifest.json` for Plastic Ox map membership
- `data/maps/*/map.json` for map metadata, NPC events, connections, and hidden items
- `data/maps/*/scripts.inc` and `data/scripts/*.inc` for trainers and item scripts
- `src/data/wild_encounters.json` for Plastic Ox-owned (`gPox*`) encounter slots
  and rates; legacy FRLG/Hoenn tables that share reused map IDs are excluded
- `src/data/trainers.party` for trainer metadata and teams

Run `python3 plastic_ox/wiki/build_wiki.py --check` in CI to fail when generated
pages are stale. The build is deterministic and writes a source fingerprint to
`site/build.json`.
