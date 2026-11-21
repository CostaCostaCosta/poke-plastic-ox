---
name: plastic-ox-beads
description: Work a Plastic Ox bead the superagent picked up from beads (a ticket whose execution environment sets DSH_SUPERAGENT_BEADS_ID). Explains where the bead's story context comes from, which other skills to load per bead kind, and how to finish so the bead closes. Use at the start of every beads-originated ticket in poke-plastic-ox.
---

# Working a Plastic Ox bead

The director queues work with `plastic_ox/story/beads_direct.py`. Each town or
route is a beads epic labeled `loc:<slug>`, where `<slug>` is a story note in
`plastic_ox/story/locations/`. Each child bead is one pass on that location.
Your ticket's first message is the bead. It includes the epic's grounded brief:
maps, flags, trainers, voice seed, snapshot, open questions and the director's
intent.

`DSH_SUPERAGENT_BEADS_ID`, `DSH_SUPERAGENT_BEADS_PARENT` and
`DSH_SUPERAGENT_BEADS_LOCATION` (the note slug) name what you are working on.

## Do not touch beads yourself

Do not run `bd`. The `.beads/` database is not in your worktree, and the beads
Source records everything for you:

- your acknowledgement and replies become comments on the bead;
- the bead is claimed while the ticket runs;
- the bead closes when your pull request merges, or goes back to the director
  if the ticket is stopped or you report `dropped`.

If you find follow-up work outside this bead, list it under **Follow-ups** in
the PR description and in your final report. The director turns it into beads.

## Start

1. Read the latest `plastic_ox/story/runs/*-<slug>.md` log if one exists.
2. Read `plastic_ox/story/locations/<slug>.md`, then the matching section of
   `plastic_ox/plastic_ox_story_v7.md`. If they disagree, the bible wins.
3. Run the grounding commands listed in the bead.
4. Load the skill that matches the bead title:
   - *Story & dialogue pass*: `plastic-ox-story-dialogue`
   - *Connections, warps & gates*: `plastic-ox-map-port` and `plastic-ox-map-baseline`
   - anything that deletes maps or assets: `plastic-ox-artifact-cleanup`
   - *Trainer & encounter pacing*: `plastic_ox/agent/ROUTE_TRAINER_PACING.md`
     and the tier notes in `plastic_ox/encounter_tables/`
5. Read `plastic_ox/agent/STORY_PASS_PRIME_PROMPT.md` for the house rules. Find
   the toolchain path for this machine there; it is not on `PATH`.

## Scope

Stay inside the location's maps (`maps` and `also_maps` in the note), plus the
shared story scripts and data that those maps need. Open questions are yours to
decide conservatively. Record each decision in the run log. Do not stop to ask
unless a decision would change another location's story.

## Finish

Meet every acceptance criterion in the bead. Then:

- `python3 plastic_ox/story/check_story_notes.py --note <slug>` and
  `python3 plastic_ox/wiki/build_wiki.py --check` pass;
- the ROM builds with zero errors;
- write or append the run log at `plastic_ox/story/runs/<date>-<slug>.md`;
- open the PR from your ticket branch. Its title starts with the bead id, for
  example `pox-nkm.1: Route 36 story & dialogue pass`. Its body has a
  **Verification** section and a **Follow-ups** section;
- report `ready` with the PR number.
