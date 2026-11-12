# Plastic Ox story notes

One markdown file per town, route, cave, or landmark. Each note is the design
source for that place: what happens there, which interactions must exist, and
what kind of people live there — enough for an agent (or a human) to write NPC
dialogue that belongs to the world and respects the story bible.

The notes are **not** free prose. They are checked against the checkout:
every map, flag, trainer, item, species, and script label they mention must
exist in `data/`, `include/constants/`, or `src/data/`. That check is what makes
them safe to hand to an autonomous agent.

## Layout

```text
plastic_ox/story/
  README.md              this file
  TEMPLATE.md            copy for a new location
  locations/<slug>.md    one per wiki location page
  story_notes.py         parser/renderer shared with the wiki build
  story_context.py       repo-grounded dossier for a note or map
  check_story_notes.py   validator (front matter, coverage, identifiers)
```

`locations/<slug>.md` uses the wiki page slug as its file name (e.g.
`lavendertown-hns.md` renders on `site/lavendertown-hns.html`). Interior maps,
gates, and `PlasticOx_*` story rooms are listed under `also_maps` on the node
they belong to, so a town note owns its Gym, tower, and story room.

## Note contract

Front matter keys (all required except `also_maps`, `flags`, `badges`,
`trainers`, `items`):

| Key | Meaning |
| --- | --- |
| `title` | Display name, e.g. `Lavender Town` |
| `slug` | Must equal the file name |
| `kind` | `City`, `Town`, `Route`, `Cave`, `Building` |
| `act` | 1–6, matching the story bible's acts |
| `stage` | Progression stage string, e.g. `9 — Cinnabar and the Mansion` |
| `depth` | `full` for mainline nodes, `supporting` for connectors/legacy maps |
| `wiki` | Wiki page slug this note renders on (`none` with a reason if absent) |
| `maps` | The outdoor map(s) the node is, by `data/maps/` directory name |
| `also_maps` | Interiors, gates, and story rooms the node covers |
| `flags` | Persistent flags the note relies on |
| `badges` | Badge numbers awarded here, if any |
| `trainers` | `TRAINER_*` ids that fight here |
| `items` | `ITEM_*` ids that matter here |
| `status` | `draft`, `drafted`, `reviewed`, or `implemented` |

Required sections, in order:

1. `## Snapshot` — what the player does here and the emotional note.
2. `## Plot points` — beats in order, reveal-ladder step, and what the scene
   must not do.
3. `## Key interactions` — table of interactions grounded in coordinates,
   script labels, flags, and trainers.
4. `## Dialogue guidance` — who speaks, voice, register, 3–5 sample lines in
   distinct voices, and a "do not" list.
5. `## Inspiration` — concrete references (places, seasons, games, other media)
   and how each becomes NPC jobs and overheard topics.
6. `## Implementation hooks` — maps, scripts, flags, gates, known gaps.
7. `## Open questions` — decisions a human should make.

`depth: supporting` notes may be shorter, but they still need real dialogue
guidance; that is the point of the file.

## Commands

```sh
# Everything wrong with the notes right now
python3 plastic_ox/story/check_story_notes.py

# What should the superagent work on next? (grounded work order)
python3 plastic_ox/story/next_pass.py
python3 plastic_ox/story/next_pass.py --act 3
python3 plastic_ox/story/next_pass.py --all

# Everything the review found: known gaps + open questions
python3 plastic_ox/story/gaps_report.py
python3 plastic_ox/story/gaps_report.py --markdown

# One note while you edit it
python3 plastic_ox/story/check_story_notes.py --note lavendertown-hns

# Live repo facts for a note or map: NPCs, current text, flags, trainers, items
python3 plastic_ox/story/story_context.py lavendertown-hns
python3 plastic_ox/story/story_context.py PlasticOx_PokemonTower --json

# Parser/renderer self-tests (run in CI)
python3 plastic_ox/story/test_story_notes.py

# Render the wiki (the notes appear in a "Story notes" section per page)
python3 plastic_ox/wiki/build_wiki.py
python3 plastic_ox/wiki/build_wiki.py --check
```

The validator fails when a wiki page has no note, when a note claims a map that
does not exist, when an identifier is unknown, or when a required section is
missing. It also fails when a `PlasticOx_*` story room or v7 map is not claimed
by any note.

## Autonomous loop

The superagent treats a note as the ticket for a location:

1. `check_story_notes.py --note <slug>` — is the note valid and current?
2. `story_context.py <slug>` — what does the map actually contain today? Which
   NPCs still speak vanilla text, which objects are dead, which gates exist?
3. Read `plastic_ox/plastic_ox_story_v7.md` for the beat, and
   `plastic_ox/alpha/STORY_TRIGGERS.md` for the flag contract. If the note and
   the bible disagree, the bible wins; fix the note.
4. Implement in `data/maps/<Map>/map.json` (objects, warps, coord events) and
   the owning `scripts.inc`, or in `data/scripts/plastic_ox_*.inc`. Never edit
   generated `events.inc`/`connections.inc`/`trainers.h`; regenerate them.
5. Verify: rebuild, walk the map in mGBA, talk to every NPC, diff dialogue
   strings so no two NPCs share a line, check the gate in both states.
6. Update the note: `status: implemented`, adjust **Key interactions** to what
   actually shipped, and move resolved items out of **Open questions**.
7. `check_story_notes.py --note <slug>` and the wiki build must stay green.
8. Append a short run log at `plastic_ox/story/runs/<date>-<slug>.md` (what
   changed, what was tested in-emulator, what stayed open). The next pass reads
   the previous log instead of rediscovering the map.

`next_pass.py` prints step 1 for the next unimplemented note in act order, which
is how the superagent picks its own work. `gaps_report.py` is the mechanical
triage view; [`REVIEW_FINDINGS.md`](REVIEW_FINDINGS.md) is the curated list of
P0/P1/P2 issues from the first full review pass.

`.github/workflows/wiki.yml` runs the note validator and
`build_wiki.py --check` on changes to the notes, wiki, maps, scripts, or data;
a stale wiki or an unknown identifier fails the PR.

The companion skill for step 4–5 is
`.agents/skills/plastic-ox-story-dialogue/SKILL.md`.

## Writing rules

- **Ordinary people first.** Residents talk about work, weather, food, family,
  and local inconvenience. The merged world shows up as logistics, not lore.
- **One voice per NPC.** No two NPCs anywhere share a line. The validator
  cannot see this; the implementer must diff the strings.
- **Restraint on the mystery.** Bill, Silph, and the adaptive system are named
  only at their reveal ladder steps. Rocket owns three story beats (Mt. Moon,
  Pokémon Tower, Silph); incidental Rocket NPCs elsewhere are allowed.
- **Visible locks pay off.** A closed road, gate, or harbour is a promise:
  record when it opens in `## Plot points`.
- **Legacy maps get an audit, not a story.** If a map is a retired duplicate or
  donor leftover, say so in `## Snapshot` and recommend keep/retire in
  `## Open questions`; do not invent beats for it. See the
  `plastic-ox-artifact-cleanup` skill before deleting anything.
- **Do not invent identifiers.** If a flag or trainer does not exist yet, say
  "new flag required" in `## Implementation hooks` instead of writing a name
  that looks real. The validator will reject it.
