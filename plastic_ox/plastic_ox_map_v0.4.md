# Pokémon Plastic Ox — World Map and Route Structure

**Version: 0.4**

## Purpose

This document defines the canonical overworld structure for **Pokémon Plastic Ox**. It supersedes `plastic_ox_map_v0.3.md` and incorporates the physical-port layout pass, junction inventory, Whirl Islands substitution, and revised Saffron Gym 8 structure.

The region remains a curated “best of Generations I–III” world built by **stapling together existing maps with minimal geometry edits**. The global geography may be impossible; the local geometry should still respect the natural exits of each imported map.

Version 0.3 adds one core rule:

> **Choose connections that fit the existing land, water, gate, forest, cave, and facility junctions of the source maps. If a connection does not fit, change the route module rather than inventing a new town exit.**

---

# Version 0.4 Changes

- **Whirl Islands replace Seafoam Islands** as the contained dungeon in the first major water region.
- **Route 41 replaces Route 20** in required progression so the Whirl Islands remain embedded in their native surrounding water route.
- **Bruno becomes Gym Leader 8 at the Saffron Fighting Dojo.**
- The official **Saffron Gym remains inaccessible during the main story** for a reason intentionally left TBD for a later story pass.
- **Mt. Moon is removed entirely.**
- **Route 4 is removed from required progression.**
- Route 46 returns to its natural role as a branch from Route 29 rather than a Cherrygrove connection.
- Cherrygrove uses its natural east Route 29 and north Route 30 land exits.
- **Dark Cave is the single general-purpose connector cave**, using its existing internal map and exactly three exterior ports.
- Route 34 is restored between Ilex Forest and Goldenrod.
- Route 118 is inserted between Ecruteak and Route 119.
- Route 121 becomes the late-game land/water junction.
- southern Route 104, Route 126, and Route 124 provide the Hoenn-ocean approach to Mossdeep.
- Route 11 replaces Route 8 for the final Lavender-to-Saffron approach.
- Route 23 is made explicit between Saffron and Victory Road.
- Cinnabar and Mossdeep are hard-constrained as water-accessed islands.
- Reserved cave/facility entrances are not free regional connection points.
- Routes should be represented as graph nodes during layout work, not merely edge labels.

---

# Core Mapping Rules

## 1. Reuse existing maps with minimal geometry edits

Prefer changing:

- map connections and warps
- entrance destinations
- NPCs and trainers
- encounter tables
- object events
- story flags
- item placement
- progression locks

Avoid:

- custom route redesigns
- tile-by-tile blending between regions
- major changes to imported map geometry
- inventing extra town exits
- new transition maps unless technically necessary

## 2. Physical ports constrain graph edges

Useful junction types are:

- **LAND** — walkable map boundary
- **WATER** — Surfable shoreline/boundary
- **GATE** — gatehouse connection
- **CAVE** — cave mouth / warp
- **FOREST** — forest entrance/exit
- **FACILITY** — building entrance
- **TRANSIT** — special travel infrastructure
- **DIVE** — underwater transition

Direct seams should normally pair opposite-facing compatible ports:

- north ↔ south
- east ↔ west
- land ↔ land
- water ↔ water

Cave mouths, gates, buildings, and transit warps may hide larger geographic discontinuities.

## 3. Original destination is not sacred

The map geometry is preserved, but the destination behind a junction may change. A Route 31 west exit can lead to Rustboro instead of Violet; a Route 121 south water exit can lead to Route 21 instead of Route 122.

## 4. Reserved entrances remain reserved

Do not consume these as generic regional links:

- Slowpoke Well
- Weather Institute
- New Mauville
- Whirl Islands
- Sea Cottage
- Shoal Cave
- Victory Road

## 5. Dark Cave is the only regional connector cave

The **existing Dark Cave interior** is preserved. Do not meld it with Mt. Moon, Union Cave, Meteor Falls, Granite Cave, Rusturf Tunnel, or other cave interiors.

Dark Cave has exactly three regional cave ports:

1. **Route 31** — early optional pocket; later full-network access
2. **Route 115** — Rustboro-side late access
3. **Route 120** — Fortree/Celadon-corridor late access

The Route 115 Meteor Falls mouth and Route 120 Scorched Slab mouth are reused only as overworld cave-mouth locations; their destinations are rewired into Dark Cave.

Full Dark Cave traversal should open later when its existing field-move requirements are appropriate. It is not an unrestricted early teleport hub.

---

# Town Roster

Target: **12 towns**.

| Order | Town | Region | Gym | Primary Function |
|---|---|---|---|---|
| 0 | **Merged Starting Town** | Kanto / Johto / Hoenn | — | Oak, Elm, Birch, starters, regional premise |
| 1 | **Cherrygrove City** | Johto | — | Early service town and orientation point |
| 2 | **Rustboro City** | Hoenn | **Gym 1 — Roxanne** | Little Cup Gym; Devon introduction |
| 3 | **Azalea Town** | Johto | **Gym 2 — Bugsy** | Slowpoke Well gate; first Rocket event; NU Gym |
| 4 | **Goldenrod City** | Johto | — | Bill's hometown; major service hub |
| 5 | **Ecruteak City** | Johto | **Gym 3 — Morty** | Time Capsule / Bill technology history |
| 6 | **Fortree City** | Hoenn | **Gym 4 — Winona** | Weather route destination |
| 7 | **Celadon City** | Kanto | **Gym 5 — Erika** | Game Corner / Rocket Hideout / Giovanni midpoint |
| 8 | **Cinnabar Island** | Kanto | **Gym 6 — Blaine** | Island Gym; lab history; science lore |
| 9 | **Lavender Town** | Kanto | — | Mr. Fuji; Pokémon Tower; Sea Cottage staging hub |
| 10 | **Mossdeep City** | Hoenn | **Gym 7 — Tate & Liza** | Space Center reveal |
| 11 | **Saffron City** | Kanto | **Gym 8 — Bruno (Fighting Dojo)** | Silph Co. climax; official Saffron Gym inaccessible |

Gym distribution: Johto 2, Hoenn 3, Kanto 3.

---

# Canonical Main Progression

## Opening — Little Cup Phase

### Merged Starting Town → Route 29

The custom starting town should use a west-facing land exit into Route 29, preserving New Bark-like opening geometry.

### Route 29

Use its natural three-way structure:

- east → Starting Town
- west → Cherrygrove
- north → lower Route 46 branch

### Route 46 — Optional Early Spur

The lower Route 46 pocket is an optional encounter/trainer module branching from Route 29. It is **not** a third Cherrygrove land exit.

### Cherrygrove → Route 30 → Route 31

Cherrygrove uses:

- east LAND → Route 29
- north LAND → Route 30

Its western coast is not required by current progression.

Route 31 provides the first Dark Cave mouth and then exits west into Rustboro.

### Early Dark Cave pocket

Before Gym 1, only a limited portion of Dark Cave needs to be useful. It provides cave encounters, items, and exploration variety without granting full cross-region traversal.

### Rustboro — Gym 1

Leader: **Roxanne**.

Gym 1 caps the Little Cup phase:

- level cap 13
- Little Cup legality
- broad pre-Gym encounter roster
- team construction emphasized over a single counter

Devon Corporation is introduced here as ordinary infrastructure. No major mystery reveal occurs before or during Gym 1.

---

# Post-Gym 1 — NU Expansion

Mandatory progression:

**Rustboro → Route 3 → Azalea → Slowpoke Well → Bugsy**

Rustboro's south port connects to Route 3's north side. Route 3's west land exit connects to Azalea's east land exit.

## Route 115 — Optional NU branch

Removing Mt. Moon substantially shortens the Gym 1 → Gym 2 mandatory path, so Route 115 becomes optional post-Gym-1 team-building space from Rustboro's north side.

Purposes:

- additional NU encounters
- trainers and items
- optional exploration
- later Dark Cave port

The Route 115 cave mouth remains progression-locked until the full Dark Cave network is intended to open.

## Azalea / Slowpoke Well / Gym 2

Azalea's regional structure remains:

- east LAND → Route 3
- west FOREST → Ilex Forest
- Slowpoke Well entrance → reserved local dungeon

The Gym is blocked until Slowpoke Well is cleared.

Leader: **Bugsy**.

Afterward:

**Azalea → Ilex Forest → Route 34 → Goldenrod**

Route 34 is restored because it naturally connects the Ilex Forest exit to Goldenrod's south port.

---

# Goldenrod → Ecruteak

Goldenrod remains the large non-Gym hub.

Main progression:

**Goldenrod → Route 35 → National Park → Route 36 → Route 37 → Ecruteak**

National Park retains the Safari/catching-preserve role. Do not add Fuchsia.

The Magnet Train remains a late Goldenrod ↔ Saffron transit shortcut and should not bypass first-time story progression.

---

# Gym 3 — Ecruteak

Leader: **Morty**.

Ecruteak's Time Capsule supplies the story beat.

Physical progression leaves Ecruteak through its east land port:

**Ecruteak → Route 118 → Route 119 → Weather Institute → Fortree**

Route 118 is the adapter that makes the Ecruteak-to-Hoenn transition physically clean.

---

# Gym 4 — Fortree

Leader: **Winona**.

Fortree remains a clean west/east pass-through:

- west → Route 119
- east → Route 120

Then:

**Fortree → Route 120 → Celadon**

The existing Scorched Slab cave-mouth location on Route 120 becomes Dark Cave Port 3. Scorched Slab itself is not part of the connector network.

---

# Gym 5 — Celadon

Leader: **Erika**.

Celadon uses its west/east land axis:

- west → Route 120
- east → Route 110

After the Gym:

**Game Corner → Rocket Hideout → Giovanni**

Then:

**Celadon → Route 110 → New Mauville**

New Mauville remains a reserved internal facility on Route 110.

After New Mauville:

**Route 110 south → Route 19 north**

---

# Water Region I — Whirl Islands / Cinnabar

Progression:

**Route 110 south → Route 19 north**

Route 19 remains the land-to-water transition.

Then:

**Route 19 south → Route 41 north → Whirl Islands → Route 41 west → Cinnabar east**

Route 41 replaces Route 20 in required progression because the **Whirl Islands are natively embedded inside Route 41**.

### Route 41

Use the existing Route 41 water-route geometry:

- north WATER → Route 19
- west WATER → Cinnabar
- four island cave mouths → Whirl Islands

The route should retain its defining whirlpool/island structure.

### Whirl Islands

Whirl Islands replace Seafoam Islands as the contained dungeon in Water Region I.

Use the **existing Whirl Islands interior**. Do not merge it with Dark Cave or any other cave.

The Whirl Islands are a local dungeon, not a regional connector cave.

The exact entrance/exit pair used for mandatory progression may be chosen during implementation after checking field-move requirements and internal traversal. The preferred implementation should preserve the original dungeon topology rather than flattening it into a simple tunnel.

Water Region I identity:

- rough open water
- whirlpool-gated islands
- rocky cave exploration
- constrained navigation around multiple island entrances
- a stronger Johto nautical identity than the former Seafoam sequence


# Gym 6 — Cinnabar

Leader: **Blaine**.

Cinnabar is an island and remains water-accessed.

Use:

- east WATER → Route 41 arrival
- north WATER → Route 21 departure

After Gym 6:

**Cinnabar → Route 21 → Route 121**

Route 21's north-facing water endpoint is rewired to Route 121's south-facing water/pier junction.

---

# Route 121 — Late-Game Junction

Route 121 is the key adapter because it provides:

- west LAND
- east LAND
- south WATER

Plastic Ox allocations:

- south WATER → Route 21 / Cinnabar
- east LAND → Lavender west
- west LAND → southern Route 104 east

The Hoenn Safari Zone entrance on Route 121 is unused because National Park fills that role. Close it, leave it inaccessible, or repurpose it for a minor non-Safari function.

---

# Lavender / Sea Cottage

Lavender's useful ports are allocated deliberately:

- west → Route 121
- north → Route 24 / Route 25 / Sea Cottage
- south → Route 12 / final Saffron approach

Sea Cottage module:

**Lavender → Route 24 → Route 25 → Sea Cottage → backtrack**

Route 25 remains a dead-end destination route. Cerulean is not required.

---

# Water Region II — Hoenn Ocean

After Sea Cottage, return to Route 121 and take its west land exit.

Progression:

**Route 121 → southern Route 104 → Route 126 → Route 124 → Mossdeep**

Port logic:

- Route 121 west LAND ↔ southern Route 104 east LAND
- Route 104 south WATER ↔ Route 126 north WATER
- Route 126 east WATER ↔ Route 124 west WATER
- Route 124 east WATER ↔ Mossdeep west WATER

The destinations are rewired, but direction and traversal type remain compatible.

### southern Route 104

Only the southern/coastal module is needed. Petalburg and Petalburg Woods are not required destinations. Unused exits should be blocked/inactive.

### Route 126

Route 126 is used as a water elbow. Sootopolis-related access remains unavailable unless explicitly added later.

### Route 124

Route 124 is the final open-ocean approach to Mossdeep.

Optional branch:

**Mossdeep → Route 125 → Shoal Cave**

Shoal Cave remains optional and contained.

---

# Gym 7 — Mossdeep

Leaders: **Tate & Liza**.

Mossdeep remains an island and should only be reached by water.

After the Gym, the **Mossdeep Space Center** supplies the final major clue before Saffron.

The physical return path is:

**Mossdeep → Route 124 → Route 126 → Route 104 → Route 121 → Lavender**

By this stage Fly can make the return painless. If Fly is restricted, revisit late-game transit pacing.

---

# Final Saffron Approach

After Mossdeep:

**Lavender → Route 12 → Route 11 → Saffron east gate → Saffron**

Route 8 is no longer required.

Route 11's Diglett's Cave entrance remains closed/inactive because Dark Cave is the only general connector cave.

The Saffron gate remains story-locked until the Mossdeep Space Center flag is complete.

---

# Gym 8 — Saffron Fighting Dojo

Saffron contains two adjacent battle institutions:

1. the official Psychic-type **Saffron Gym**
2. the historically unofficial Fighting-type **Fighting Dojo**

For Plastic Ox, the final badge comes from the Fighting Dojo.

Order:

1. Enter Saffron after Mossdeep.
2. Complete Silph Co.
3. Resolve the regional-convergence crisis.
4. Return Saffron to normal.
5. Attempt to enter the official Saffron Gym.
6. Discover that something prevents entry.
7. Challenge **Bruno** at the Fighting Dojo.
8. Receive Badge 8.

Leader: **Bruno — Fighting specialist**.

### Official Saffron Gym

The actual Saffron Gym remains present on the map but is inaccessible during the main-story Gym Challenge.

**The exact cause of the obstruction is intentionally TBD.**

Do not invent a permanent explanation in implementation scripts until the story pass defines it.

Possible future story work may decide whether the obstruction is:

- environmental
- technological
- character-driven
- post-Silph fallout
- or reserved for postgame content

Those are not yet canonical.

### Fighting Dojo as Gym 8

The Fighting Dojo becomes the functional eighth Gym for the player's League challenge.

This is a particularly natural reuse because the source city already contains the Fighting Dojo immediately beside the official Saffron Gym.

Bruno should feel like a true final-badge boss, not a substitute miniboss.

No second villain sequence occurs after this battle.


# League Approach

**Saffron north gate → Route 23 → Victory Road → Pokémon League → Elite Four → Champion Bill**

Victory Road remains its own endgame dungeon and is not part of the Dark Cave network.

---

# Canonical Full Route Graph

```text
MERGED STARTING TOWN
|
Route 29
|\
| \-- Route 46 [optional lower pocket]
|
CHERRYGROVE
|
Route 30
|
Route 31
|\
| \-- Dark Cave [early pocket; later network]
|
RUSTBORO [GYM 1 — LITTLE CUP]
|\
| \-- Route 115 [optional NU branch; later Dark Cave port]
|
Route 3
|
AZALEA
|\
| \-- Slowpoke Well [MANDATORY]
|    GYM 2 — Bugsy
|
Ilex Forest
|
Route 34
|
GOLDENROD
|
Route 35
|
National Park
|
Route 36
|
Route 37
|
ECRUTEAK [GYM 3]
|
Route 118
|
Route 119
|-- Weather Institute
|
FORTREE [GYM 4]
|
Route 120
|-- Dark Cave late port
|
CELADON [GYM 5]
|-- Game Corner / Rocket Hideout / Giovanni
|
Route 110
|-- New Mauville
|
Route 19
|
Route 41
|-- Whirl Islands
|
CINNABAR [GYM 6]
|
Route 21
|
Route 121
|\
| \-- east → LAVENDER
|              |
|              Route 24 → Route 25 → Sea Cottage
|
\-- west → southern Route 104
             |
          Route 126
             |
          Route 124
             |
          MOSSDEEP [GYM 7]
             |
          Space Center
             |
        return to Lavender
             |
          Route 12
             |
          Route 11
             |
       Saffron East Gate
             |
         SAFFRON
         |-- Silph Co.
         |-- official Saffron Gym [INACCESSIBLE — cause TBD]
         |-- Fighting Dojo — GYM 8 — Bruno
             |
          Route 23
             |
        Victory Road
             |
       Pokémon League
```

---

# Dark Cave Network

```text
               Route 115
                  |
             [DARK CAVE]
              /        \
             /          \
        Route 31      Route 120
```

Early game: Route 31 pocket only.

Later game: Route 115 and Route 120 become useful once the original Dark Cave traversal is appropriately unlocked.

There is **no fourth Dark Cave port** in the current plan.

---

# Early Tier Progression

## Before Gym 1 — Little Cup

Mandatory:

**Starting Town → Route 29 → Cherrygrove → Route 30 → Route 31 → Rustboro**

Optional:

- lower Route 46
- early Dark Cave pocket

## Between Gym 1 and Gym 2 — NU

Mandatory:

**Rustboro → Route 3 → Azalea → Slowpoke Well → Bugsy**

Optional:

- Route 115

### Open gameplay question

The physical layout is resolved, but the **amount of NU team-building space** between Roxanne and Bugsy should be playtested. If Route 3 + Route 115 + Slowpoke Well are insufficient, add another optional land-route module rather than another mandatory cave.

---

# Locations Explicitly Removed from the Required Town List

- Cerulean City
- Viridian City
- Mauville City
- Fuchsia City
- Pewter City
- Violet City
- Petalburg City
- Slateport City
- Sootopolis City
- Lilycove City

Their routes, facilities, characters, or mechanics may still be reused independently.

# Locations Explicitly Removed from the Required Map

- **Route 20** — replaced by Route 41 so Whirl Islands retain their native surrounding route

- **Mt. Moon**
- **Route 4**

Mt. Moon should not be reintroduced as a second central cave.

---

# Source-Map Baseline

Unless implementation constraints say otherwise:

- Johto modules: Crystal / Generation II topology
- Hoenn modules: Emerald / Generation III topology
- Kanto modules: FireRed/LeafGreen / Generation III topology

Before implementation, verify each port against the exact asset imported into `pokeemerald-expansion`.

---

# Final Implementation Principle

Plastic Ox is a **port-constrained directed graph of existing Pokémon maps**.

Expected custom work is primarily:

1. merged starting town
2. map connections and warps
3. destination rewiring at existing junctions
4. object/NPC placement
5. story scripting
6. encounter tables
7. trainer remixes
8. progression flags
9. locks on unused exits
10. optional League/Victory Road adjustments

When a connection does not fit an imported map:

> **change the route module before changing the map geometry.**

The global geography may be impossible. The local geography should still feel like Pokémon.
