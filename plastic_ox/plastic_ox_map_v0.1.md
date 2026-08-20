# Pokémon Plastic Ox — World Map and Route Structure

## Purpose

This document defines the current overworld structure for **Pokémon Plastic Ox**.

The guiding principle is to create a curated “best of Generations I–III” region by **stapling together existing towns, routes, caves, forests, facilities, and water areas** rather than heavily redesigning map geometry.

The merged world should feel intentionally strange: recognizable locations from Kanto, Johto, and Hoenn now connect in impossible ways because the regions have converged.

---

# Core Mapping Rules

## 1. Reuse existing maps with minimal geometry edits

Imported towns, routes, dungeons, forests, caves, and facilities should remain as close to their original layouts as possible.

Prefer changing:

- map connections
- warps
- entrance destinations
- NPCs
- trainer placement
- encounter tables
- object events
- story flags
- item placement
- progression locks

Avoid:

- custom route redesigns
- tile-by-tile blending between regions
- major changes to route geometry
- building new transition maps unless technically necessary

The project should behave like a **graph of existing map modules**.

---

## 2. Towns are nodes; routes and landmarks are edges

Original-game adjacency is not sacred.

For example:

- Route 24 / Route 25 / Sea Cottage do not require Cerulean City.
- New Mauville does not require Mauville City.
- Seafoam Islands do not require Fuchsia City.
- Route 119 / Weather Institute can connect directly from a Johto town.
- Route 124 can be attached to Lavender or another arbitrary node.

The region is canonically distorted, so abrupt regional transitions are acceptable.

---

## 3. Prefer clean seams

The best connections between imported maps are places where a discontinuity is naturally hidden:

- building doors
- gatehouses
- cave mouths
- forest exits
- stairwells
- ferries
- route-transition warps
- tunnels

When possible, preserve full original route chains that already flow cleanly.

---

# Town Count

Target: **11 total towns**

- 1 merged starting town
- 8 Gym towns
- 2 non-Gym towns

This is intentionally lean.

The memorable exploration content should come primarily from routes and landmarks rather than an oversized town list.

---

# Town Roster

| Order | Town | Region | Gym | Primary Function |
|---|---|---|---|---|
| 0 | **Merged Starting Town** | Kanto / Johto / Hoenn | — | Oak, Elm, Birch, starters, regional premise |
| 1 | **Azalea Town** | Johto | **Gym 1 — Bugsy** | Small opening town; Slowpoke Well; Ilex Forest |
| 2 | **Rustboro City** | Hoenn | **Gym 2 — Roxanne** | Devon Corporation introduction |
| 3 | **Goldenrod City** | Johto | — | Bill’s hometown, family, major service hub |
| 4 | **Ecruteak City** | Johto | **Gym 3 — Morty** | Time Capsule / Bill technology history |
| 5 | **Fortree City** | Hoenn | **Gym 4 — Winona** | Weather route destination |
| 6 | **Celadon City** | Kanto | **Gym 5 — Erika** | Game Corner / Rocket Hideout / Giovanni midpoint |
| 7 | **Cinnabar Island** | Kanto | **Gym 6 — Blaine** | Volcanic island, lab history, science lore |
| 8 | **Lavender Town** | Kanto | — | Mr. Fuji, Pokémon Tower, Bill-science interpretation |
| 9 | **Mossdeep City** | Hoenn | **Gym 7 — Tate & Liza** | Space Center and late-game regional reveal |
| 10 | **Saffron City** | Kanto | **Gym 8 — Sabrina** | Silph Co. story climax, then final Gym |

### Gym distribution

- Johto: 2
- Hoenn: 3
- Kanto: 3

### Non-Gym towns

- Merged Starting Town
- Goldenrod
- Lavender

---

# Main Overworld Progression

## Opening

**Merged Starting Town**

A custom mashup of:

- Pallet Town
- New Bark Town
- Littleroot Town

This is one of the few locations expected to require substantial custom mapping.

The player receives a starter from Oak, Elm, and Birch and begins exploring the merged region.

Then:

**existing early-game route module**

→ **Azalea Town**

---

# Gym 1 — Azalea Town

Leader: **Bugsy**

The first Gym should establish ordinary Pokémon progression.

After the Gym:

### Slowpoke Well

Use the existing Slowpoke Well dungeon map.

Story purpose:

- first Team Rocket incident
- first unexplained technological signal

Then continue through:

### Ilex Forest

Keep the existing Ilex Forest map essentially intact.

This is the game’s primary early forest biome.

The far exit is rewired to the next imported region module.

---

# Gym 2 — Rustboro City

Leader: **Roxanne**

Rustboro introduces Devon Corporation.

After Rustboro, the player enters the game’s main early mountain/cave sequence.

---

# Mountain / Cave Module

Use an existing Kanto chain with minimal or no geometry changes:

**Route 3**

→ **Mt. Moon**

→ **Route 4**

This entire block should function primarily as Pokémon exploration rather than story exposition.

Key functions:

- fossils
- Clefairy
- Moon Stones
- cave encounters
- multi-floor exploration
- route trainers

Route 4’s exit is rewired into Goldenrod.

---

# Goldenrod City — Non-Gym Hub

Goldenrod serves as a large mid-early-game service city.

Use:

- Department Store
- Radio Tower
- Game Corner if desired
- Underground
- services
- Bill’s family
- Bill character lore
- Eevee references

Goldenrod’s major gameplay branch becomes:

### National Park

The National Park replaces the traditional Safari Zone.

Preserve the existing route chain where practical:

**Goldenrod**

→ **Route 35**

→ **National Park**

→ **Route 36**

→ **Route 37**

→ **Ecruteak**

---

# National Park as the Safari Zone

The National Park should take over the catching-preserve role normally associated with Fuchsia.

Do not add Fuchsia City.

Potential National Park changes:

- expanded encounter table
- rare Pokémon unavailable elsewhere
- rotating encounters
- retained or expanded Bug-Catching Contest
- badge-gated rare species
- special catching events

The map itself should remain largely unchanged.

---

# Gym 3 — Ecruteak City

Leader: **Morty**

Ecruteak contains the Time Capsule story beat.

After Ecruteak, immediately staple in a Hoenn route chain.

---

# Weather Route Module

Use:

### Route 119

Preserve as much of the original route as possible.

Route 119 already provides:

- long grass
- rain
- rivers
- bridges
- tropical vegetation
- Weather Institute
- direct approach to Fortree

Progression:

**Ecruteak exit**

→ **Route 119**

→ **Weather Institute**

→ **Fortree City**

---

# Gym 4 — Fortree City

Leader: **Winona**

Fortree provides a strong visual break from the preceding towns.

After Fortree:

### Route 120

Use Route 120 as the primary transition module.

Its far connection is rewired into Celadon.

---

# Gym 5 — Celadon City

Leader: **Erika**

Gym 5 remains a normal Gym.

Afterward, the player investigates:

### Rocket Game Corner

→ **Rocket Hideout**

→ **Giovanni**

This is the midpoint plot reversal.

The existing Rocket Hideout should be reused.

Giovanni is not the Gym Leader in Plastic Ox.

---

# New Mauville Module

After Celadon, staple in a Hoenn route/facility block.

Use:

### Route 110

Route 110 already provides:

- alternate traversal paths
- Seaside Cycling Road
- water
- Trick House
- access to New Mauville

Then:

### New Mauville

Use the existing facility map.

Narrative function:

- regional power problem
- discovery that the generator is working
- discovery of massive power drain into Bill-derived infrastructure

Mauville City itself is not required.

Wattson can be placed near the facility or otherwise incorporated without retaining his original city.

---

# Water Region I — Kanto Sea

After New Mauville, staple into the existing Kanto ocean chain.

Use:

**Route 19**

→ **Route 20**

→ **Seafoam Islands**

→ **Route 20**

→ **Cinnabar Island**

This is the first major water region.

Its identity should be:

- colder
- cave-heavy
- constrained
- ice/water focused
- island traversal

No Fuchsia City is required.

---

# Gym 6 — Cinnabar Island

Leader: **Blaine**

Cinnabar provides:

- Gym 6
- volcanic visual identity
- Pokémon Mansion
- lab history
- scientific background related to Fuji and Bill

After Cinnabar:

### Route 21

Use Route 21 as the exit route.

Instead of leading to Pallet, its far endpoint can be rewired to Lavender.

---

# Lavender Town — Non-Gym Story Hub

Lavender serves as a late-game atmospheric hub.

Functions:

- Mr. Fuji
- Pokémon Tower
- scientific interpretation
- quiet tonal contrast
- staging point for Sea Cottage investigation

---

# Bill Route Module

Staple the classic Cerulean Cape chain onto Lavender.

Use:

**Lavender side exit**

→ **Route 24**

→ **Nugget Bridge**

→ **Route 25**

→ **Sea Cottage**

Then return by the same route.

Cerulean City is not required.

The Sea Cottage is a route landmark, not a town dependency.

---

# Water Region II — Hoenn Ocean

After the Lavender / Sea Cottage sequence, transition into Hoenn’s late-game ocean.

Use:

### Route 124

Route 124 provides:

- open ocean
- Dive
- underwater sections
- reefs
- late-game Water encounters
- direct connection to Mossdeep

Optional:

### Route 125

→ **Shoal Cave**

This should remain optional unless later progression requires it.

This second water region should contrast with Seafoam:

### Kanto Water Region
- colder
- cave-centric
- linear

### Hoenn Water Region
- tropical
- open
- Dive-focused
- exploratory

---

# Gym 7 — Mossdeep City

Leaders: **Tate & Liza**

After the Gym:

### Mossdeep Space Center

The Space Center reveals that the merged geography appears intentionally optimized rather than random.

This points the story toward Saffron and Silph.

---

# Final Return to Kanto

Avoid building another custom late-game route.

Use existing Kanto maps to create the final approach.

A useful chain is:

### Route 12

→ **Lavender revisit**

→ **Route 8**

→ **Saffron Gate**

→ **Saffron City**

The Saffron Gate can remain inaccessible until the Mossdeep story flag is complete.

This creates a satisfying return to a previously visited town before the climax.

---

# Saffron City — Final Story City

Saffron is mandatory.

It should feel like the largest and most important city in the late game.

Order of events:

1. Enter Saffron after Mossdeep.
2. Complete Silph Co.
3. Resolve the regional-convergence crisis.
4. Return to normal city state.
5. Challenge Sabrina.
6. Receive the eighth Badge.

---

# Gym 8 — Saffron City

Leader: **Sabrina**

This should be a pure final Gym after the Silph crisis.

No second villain sequence should occur afterward.

---

# Post-Gym Progression

**Saffron**

→ Victory Road

→ Pokémon League

→ Elite Four

→ Champion Bill

Victory Road may reuse an existing Gen I–III layout or a lightly modified combination if necessary, but should follow the same minimal-custom-work philosophy.

---

# Full Route Graph

```text
MERGED STARTING TOWN

→ existing early route

→ AZALEA [GYM 1]
    ↳ Slowpoke Well

→ Ilex Forest

→ RUSTBORO [GYM 2]
    ↳ Devon Corporation

→ Route 3
→ Mt. Moon
→ Route 4

→ GOLDENROD
    ↳ Route 35
    ↳ National Park / Safari Zone
    ↳ Route 36
    ↳ Route 37

→ ECRUTEAK [GYM 3]
    ↳ Time Capsule

→ Route 119
    ↳ Weather Institute

→ FORTREE [GYM 4]

→ Route 120

→ CELADON [GYM 5]
    ↳ Game Corner
    ↳ Rocket Hideout
    ↳ Giovanni

→ Route 110
    ↳ New Mauville

→ Route 19
→ Route 20
→ Seafoam Islands
→ Route 20

→ CINNABAR [GYM 6]
    ↳ Pokémon Mansion / labs

→ Route 21

→ LAVENDER
    ↳ Mr. Fuji
    ↳ Pokémon Tower
    ↳ Route 24
    ↳ Nugget Bridge
    ↳ Route 25
    ↳ Sea Cottage

→ Route 124
    ↳ Dive areas
    ↳ optional Route 125 / Shoal Cave

→ MOSSDEEP [GYM 7]
    ↳ Space Center

→ Route 12
→ LAVENDER REVISIT
→ Route 8
→ Saffron Gate

→ SAFFRON
    ↳ Silph Co.
    ↳ GYM 8 — Sabrina

→ Victory Road
→ Pokémon League
```

---

# Locations Explicitly Removed from the Required Town List

The following locations are not required as towns in Plastic Ox:

- Cerulean City
- Viridian City
- Mauville City
- Fuchsia City
- Pewter City
- Violet City
- Petalburg City
- Slateport City
- Sootopolis City

Their best routes, facilities, characters, or mechanics may still be reused independently.

---

# Final Implementation Principle

The map team should treat Plastic Ox as a **directed graph of existing Pokémon maps**.

The expected custom work is primarily:

1. merged starting town
2. map connections and warps
3. object and NPC placement
4. story scripting
5. encounter tables
6. trainer remixes
7. progression flags
8. optional League/Victory Road adjustments

Do not redraw imported routes merely to make geography “realistic.”

The impossible geography is part of the premise.

The desired player experience is:

> Leave a recognizable Johto forest, emerge in Hoenn, cross a Kanto mountain, pass through Goldenrod, enter a Hoenn rainforest, and eventually realize that the strange arrangement of the world is itself part of the story.
