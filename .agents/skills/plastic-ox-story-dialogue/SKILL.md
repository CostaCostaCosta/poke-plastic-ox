---
name: plastic-ox-story-dialogue
description: Implement or revise NPC dialogue, signs, and story beats in poke-plastic-ox from the per-town/route notes under plastic_ox/story/locations. Use when a location's markdown note should become real map objects and script text, when dialogue needs to match the v7 story bible, or when a map still speaks vanilla FRLG/HNS text; not for map geometry, tileset imports, or encounter-table tuning.
---

# Plastic Ox story and dialogue passes

Work in the `poke-plastic-ox` checkout. The location note is the ticket; the
story bible is the law; the validator is the gate.

## Pick the next pass

`python3 plastic_ox/story/next_pass.py` prints the next unimplemented note as a
grounded work order (maps, NPC counts, flags, voice seed, open questions).
`--act N` narrows it, `--all` lists the queue. Read the latest
`plastic_ox/story/runs/*-<slug>.md` log before starting.

## Read in this order

1. `plastic_ox/story/locations/<slug>.md` — the location's beats, interactions,
   voice, and dialogue seeds.
2. `plastic_ox/plastic_ox_story_v7.md` — progression, reveal ladder, Rocket
   count, Bill restraint. If the note contradicts it, fix the note first.
3. `plastic_ox/alpha/STORY_TRIGGERS.md` — persistent flags, gate contract, and
   acceptance table.
4. `python3 plastic_ox/story/story_context.py <slug>` — live objects, current
   text, trainers, items, flags, and connections for every map the note owns.
5. `plastic_ox/agent/STORY_PASS_PRIME_PROMPT.md` — environment facts and the
   house rules for a story pass (build command, mGBA harnesses, HNS rules).

## Implement

- Objects, warps, coord events, and signs live in `data/maps/<Map>/map.json`;
  edit the JSON, never the generated `events.inc`/`connections.inc`.
- Text and scripts live in `data/maps/<Map>/scripts.inc` or
  `data/scripts/plastic_ox_*.inc`. Story-wide beats belong in the shared POX
  scripts and their generator (`plastic_ox/alpha/build_story.py`).
- Trainer parties go in `src/data/trainers.party`; `trainers.h` is generated.
- New persistent flags need a stable id in `plastic_ox/alpha/story_flags.json`
  and the POX flag header. Never reuse or renumber retired ids.
- HNS maps keep `"layout_version": "hns"` and `["emerald"]` inclusion.
- Generated content is regenerated: `rm -f .map_version && make generated`
  after map JSON or script edits, then rebuild with the devkitARM on PATH.

## Dialogue rules

- Ordinary residents talk about work, weather, food, transport, and family.
  The merged region appears as logistics and inconvenience, never as lore
  dump. Never say "convergence" in NPC dialogue.
- Every NPC and sign gets unique text. Diff the emitted strings across the map
  (and the neighbouring maps in the same leg) before declaring done.
- Keep the reveal ladder: no Bill, Silph, or adaptive-system mention before its
  step; Rocket owns three story beats (Mt. Moon, Pokémon Tower, Silph), while
  incidental Rocket NPCs elsewhere are allowed and must not steal a beat.
- A closed route, gate, or harbour is a promise; when it opens, the same NPC
  gets new text rather than disappearing.
- Match the note's sample lines in voice, not verbatim; the note's seeds are
  meant to be varied.

## Verify

1. Rebuild with zero errors.
2. Walk the map in mGBA (`~/.venvs/mgba311/bin/python`, harnesses under
   `plastic_ox/demo/`), talk to every NPC, read every sign, and exercise both
   states of any gate.
3. Diff all dialogue strings for duplicates; the same line twice is a bug even
   if the validator passes.
4. Run the regression suites named in `STORY_PASS_PRIME_PROMPT.md`, and
   `python3 plastic_ox/story/check_story_notes.py --note <slug>`.
5. Update the note: set `status: implemented`, make **Key interactions** match
   what shipped, and resolve **Open questions** that the pass answered. Then
   run `python3 plastic_ox/wiki/build_wiki.py --check`.

Leave unrelated dirty work untouched. Write the pass log at
`plastic_ox/story/runs/<date>-<slug>.md`, then report the note slug, maps
touched, dialogue counts, tests run, and anything the note still leaves open.
