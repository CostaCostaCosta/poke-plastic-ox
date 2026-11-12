---
title: Location name
slug: location-slug
kind: Town
act: 1
stage: "0 — Opening"
depth: full
wiki: wikipage-slug
maps: [MapName_hns]
also_maps: [Interior_Map_Name, PlasticOx_StoryRoom]
flags: [FLAG_POX_STORY_EXAMPLE]
badges: []
trainers: [TRAINER_PLASTIC_OX_EXAMPLE]
items: [ITEM_EXAMPLE]
status: drafted
---

# Location name

`TEMPLATE.md` is not rendered. Copy it to `plastic_ox/story/locations/<slug>.md`
and delete this paragraph. Every `##` heading below is required by
`check_story_notes.py`; keep the order. Front matter: `slug` must equal the file
name, `wiki` must equal a generated wiki page slug (or `none` with a reason in
`## Open questions`), `maps` are the outdoor maps this node is, and `also_maps`
are the interiors, gates, and `PlasticOx_*` story rooms the node covers.

## Snapshot

Two to four sentences: what the player physically does here, where it sits in
the badge spine, and the emotional note the location should leave. No plot
summary that belongs in another section.

## Plot points

- What the player learns or accomplishes, in order.
- Which reveal-ladder step this is (number it, per `plastic_ox_story_v7.md`).
- What the scene must **not** do (e.g. "no convergence exposition"; "Bill must
  not be named next to the system").

## Key interactions

A table of the interactions an implementer must preserve or add. Ground every
row in real data — the coordinates, script labels, and flags are checked
against the checkout by `check_story_notes.py`.

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Example | map `x,y` | `FLAG_...` | vanilla text | rewritten voice |

## Dialogue guidance

- Who speaks here and what they are allowed to know.
- Voice and register (short, plain sentences; regional texture; no wink-at-the-
  player meta lines).
- Register shifts the player should notice (before/after an event).
- Sample lines, one per speaker type, in blockquotes.

> A sample line in the voice of an ordinary resident.

> A second sample line, different speaker, different concern.

- **Do not:** list the lines that would break the story.

## Inspiration

- Textural references: real-world place, season, time of day, trade, food,
  architecture, regional history.
- Pokémon-media touchstones (the original route's mood, an anime episode, a
  Gen 2 town theme) used for feeling, never copied text.
- Adjacent media or genres that give the place a specific smell, sound, or
  social rhythm.
- How each reference converts into concrete NPC jobs and overheard topics.

## Implementation hooks

- Wiki page: `<slug>.html`
- Maps: `MapName` (`MAP_...`)
- Story scripts: `data/scripts/plastic_ox_*.inc`, `data/maps/<Map>/scripts.inc`
- Gates / flags: `FLAG_...`
- Trainers / items: `TRAINER_...`, `ITEM_...`
- Known gaps: dead objects, leftover vanilla text, missing warps.

## Open questions

- Anything unresolved that a human should decide.
