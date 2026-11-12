---
title: Route 20East
slug: plasticox-route20east
kind: Route
act: 3
stage: "10 — Seafoam passage"
depth: full
wiki: plasticox-route20east
maps: [PlasticOx_Route20East]
flags: [FLAG_POX_STORY_MANSION, FLAG_POX_TRIGGERS_ENABLED]
status: drafted
---

# Route 20East

## Snapshot

The eastern half of the Seafoam passage: open water from the cave's east mouth to
Mossdeep's western beach. The player surfaces at `(6,14)`, crosses 47 tiles of
empty sea, and steps onto Mossdeep at `(53,10)`. There is nothing here — no
object, no trainer, no encounter table — and that is the point: after the ice and
boulders, the route is a held breath before Mossdeep's Gym and Space Center.

## Plot points

1. **Out of the cave, not around it.** The only entrance is the Seafoam warp at
   `(6,14)` (Seafoam `1F` warp 4). The map declares no connections on any edge;
   the sea beyond the lane is `MB_OCEAN_WATER` with no surfable exit, so the
   "no surf-around" rule holds by geometry rather than by a visible obstacle.
2. **The exit is a story gate.** The coord at `(53,10)` runs
   `PoxRegion_sea_mossdeep_a`: it warps to `MossdeepCity` `(0,21)` once
   `FLAG_POX_STORY_MANSION` is set. Before the Mansion it refuses and puts the
   player back at `(52,10)` — which is one tile west, so the trigger can fire
   again on the next step east. Normal play never sees this, because Route 20
   West already requires the same flag.
3. **Reveal-ladder step 10 is a gap, not a scene.** Seafoam is the exploration
   breath between Cinnabar's archives and Mossdeep's Space Center. Nothing here
   advances the mystery; the route must not add a lore NPC or a washed-up clue.
4. **The sea is empty on purpose.** Zero objects, zero trainers, zero wild or
   fishing entries, and no signs. If encounters are added later they belong to
   the Seafoam floors, not this lane; surf fishing here would undercut the
   directed-dungeon design.
5. **Mossdeep is next.** The landing at `(0,21)` is the town's west beach, in
   front of the Gym 6 and Space Center chapter. The route's job is to deliver
   the player there with no business in between.

**Must not:** name Bill, Silph, the adaptive system, or the Space Center
findings; add a Rocket, a shipwreck, or a researcher; put an item or a trainer on
the water; explain why the sea is closed.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Seafoam east mouth | `PlasticOx_Route20East` `(6,14)` | always | warp to `MAP_SEAFOAM_ISLANDS_1F` warp 4 | keep; the cave must be the only way in |
| Mossdeep crossing | `(53,10)` `PoxRegion_sea_mossdeep_a` | `FLAG_POX_STORY_MANSION` set | warp to `MossdeepCity` `(0,21)` | keep; no message on the successful trip |
| Closed arm | `(53,10)`, same script | Mansion flag unset | message, warp to `(52,10)` | make the refusal a line a person says at the Mossdeep end, or remove the arm as unreachable |
| Empty sea | whole map | — | no objects, no encounters, no signs | keep empty; do not "fix" it with filler |
| Map identity | `map.json` | — | `REGION_HOENN`, music `MUS_RG_ROUTE3` on a Kanto sea lane | align region/music with the other Kanto sea routes |

## Dialogue guidance

- There is no one to talk to, and that is a deliberate contrast with the crowded
  Cinnabar and the staffed Space Center. Do not add a talker to make the map
  feel busy.
- If a voice is ever added, it should be a working one at the edge of the
  passage — a diver checking a marker buoy, a ferry spotter on the Mossdeep
  beach, a fisherman who cannot believe the water is this empty. One line, and
  it should be about weather or work, never the plot.
- The register is wind, distance, and a little boredom. Short lines if any.

> DIVER (proposed): Two hours down and the only thing I found was a boot. Not
> mine, either.

> FERRY SPOTTER (proposed): You came out of the cave? Then you're the first
> thing I've seen all morning.

> FISHER (proposed): Not a nibble since the water changed. I keep coming out
> anyway. It's quieter than the harbour.

- **Do not:** give the sea a mystery, a survivor, a message in a bottle, or a
  legendary silhouette. Seafoam and Mossdeep carry those beats.

## Inspiration

- **Hoenn's open-water routes (127–129):** long blue lanes where the map itself
  is the encounter, and the relief of land is the reward. The difference here is
  that Plastic Ox keeps the lane empty, so the relief is Mossdeep.
- **Real ferry passages:** the half-hour between two islands where the deck is
  cold, the water is loud, and nobody speaks. That silence is the texture.
- **Diving and marker buoys:** orange floats, a channel marker, a bell buoy —
  visual furniture that says "shipping lane" without a single NPC.
- **Lighthouse logic:** Mossdeep's Space Center should be visible on the horizon
  as a white line before the player lands; the route exists to make that
  approach feel earned.
- **Dialogue conversion:** if the map ever gets a voice, it is a job on the
  water — a diver, a spotter, a fisherman — and the topic is the day, not the
  world.

## Implementation hooks

- Wiki page: `plasticox-route20east.html`
- Maps: `PlasticOx_Route20East` (`MAP_PLASTIC_OX_ROUTE20_EAST`), 47×20, layout
  `LAYOUT_PLASTIC_OX_ROUTE20_EAST`
- Warp: `(6,14)` → `MAP_SEAFOAM_ISLANDS_1F` warp 4
- Gate: `(53,10)` `PoxRegion_sea_mossdeep_a`; success → `MossdeepCity` `(0,21)`;
  refusal → `(52,10)` with `PoxRegion_ClosedText`
- Return: `PoxRegion_sea_mossdeep_b` (Mossdeep side) warps back to `(52,10)`
- Flags: `FLAG_POX_STORY_MANSION` (open), `FLAG_POX_TRIGGERS_ENABLED` (test
  bypass)
- Known gaps: zero objects and zero encounters; `REGION_HOENN` on a Kanto sea
  lane, and `MUS_RG_ROUTE3` is the Kanto Route 3 theme; the refusal arm is
  unreachable in normal play and lands adjacent to its own trigger.

## Open questions

- Should the lane get a fishing table so the empty water still rewards a Surf
  user, or stay deliberately barren to keep Seafoam the only sea content?
- Align `REGION_HOENN` and the Route 3 music with the other Kanto sea routes, or
  treat the Hoenn metadata as harmless donor residue?
- If the Mossdeep landing is the first view of the town, should a landmark (the
  Space Center dome) be visible from the water tile instead of only after the
  warp?
