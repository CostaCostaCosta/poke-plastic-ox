# Pokémon Plastic Ox — World Map and Progression

**Version: 7**

## Purpose

This document defines the authoritative Version 7 overworld progression and gating plan for **Pokémon Plastic Ox**.

The current SVG topology is the structural basis. The world should behave as a directed graph of mostly existing Generation I–III map modules, with progression controlled primarily through connections, warps, one-way terrain, NPC blockers, story flags, and existing traversal mechanics rather than extensive remapping.

The core design principle is:

> **The first trip through the world is guided and mostly linear; later unlocks fold the map back onto itself and make traversal dramatically easier.**

---

# Core Mapping Rules

## 1. Reuse recognizable maps

Prefer changes to:

- map connections
- warps
- entrance destinations
- NPC blockers
- progression flags
- object events
- encounter tables
- trainer placement
- one-way terrain

Avoid unnecessary redrawing of imported maps.

## 2. Preserve useful native traversal constraints

Native ledges, cave directionality, water barriers, currents, and one-way drops are useful progression tools.

In particular, the early Route 29 / Route 46 / Dark Cave area must not accidentally create an early path to Blackthorn.

## 3. Locked paths should usually pay off later

Version 7 intentionally exposes several routes before they are usable:

- Route 36 east → Route 110
- Saffron City's surface entrances
- Ecruteak west → Victory Road
- Lavender south → postgame harbor

These should feel like parts of the same physical world rather than invisible story warps.

---

# Main Progression Graph

```text
PALLET TOWN
  ↓
Route 101
  ↓
OLDALE TOWN
  ↔ Route 29 / early western network
  ↓
CHERRYGROVE CITY
  ↓
Route 2 (south)
  ↓
ILEX FOREST
  ↓
Route 2 (north; Dark Cave at the former Diglett's Cave mouth)
  ↓
RUSTBORO CITY [GYM 1 — ROXANNE]
  ↳ Route 24 → Route 25 → BILL'S SEA COTTAGE [optional; Eevee #1]
  ↓
Route 44
  ↓
MT. MOON [TEAM ROCKET I]
  ↓
Route 33
  ↓
GOLDENROD CITY [GYM 2 — WHITNEY]
  ↓
Route 35
  ↓
NATIONAL PARK
  ↓
Route 36
  ↓
Route 37
  ↓
ECRUTEAK CITY [GYM 3 — MORTY]
  → east: Route 119 → Weather Institute → FORTREE [GYM 4 — WINONA]
  → west: LOCKED until 8 Badges → Victory Road / League

FORTREE
  → Route 110
  → LAVENDER TOWN [TEAM ROCKET II]

After Fortree is reached:
Route 110 west ↔ Route 36 east SHORTCUT UNLOCKS

LAVENDER
  → Route 8
  → Underground Path
  → Route 7
  → Route 103
  ↓
CINNABAR ISLAND [GYM 5 — BLAINE]
  → Pokémon Mansion [Blaine key; Entei]
  → southern coast
  → SEAFOAM ISLANDS
  → eastern coast
  → MOSSDEEP CITY [GYM 6 — TATE & LIZA]

MOSSDEEP
  → Space Center event
  → unlock SAFFRON CITY globally

SAFFRON CITY
  ↳ Fighting Dojo / Bruno [GYM 7]
  ↳ Silph Co. / Giovanni / system core
  → north exit opens with Saffron; Bruno and Silph do not gate Blackthorn

After the Space Center opens Saffron:
SAFFRON
  ↑ Route 5
  ↑ Route 115
  ↑ METEOR FALLS
  ↑ BLACKTHORN CITY [GYM 8 — CLAIR]

After all eight Badges (Bruno and Clair may be beaten in either order):
ECRUTEAK west gate unlocks
  → VICTORY ROAD
  → POKÉMON LEAGUE
  → ELITE FOUR
  → CHAMPION BILL

Postgame:
LAVENDER south gate opens
  → HARBOR / FERRY
  → BATTLE FRONTIER
  → POSTGAME ISLANDS / UBER POKÉMON
```

---

# Stage-by-Stage Traversal Specification

## Stage 0 — Opening Network

### Pallet Town

Primary exit leads into the early western route network.

Recommended progression from the current topology:

**Pallet → Route 101 → Oldale → Route 29 → Cherrygrove**

Pallet's southern/water relationship to Cinnabar may remain visible as geography, but it must not provide an early bypass to Cinnabar.

### Oldale

Oldale functions as a small non-Gym service node and later reconnects into the broader western/Saffron-side network through Route 103.

### Route 29 / Route 46 / Dark Cave

Preserve native directionality wherever possible.

The Route 46 / Route 45 chain should work primarily as a **late-game downhill return path** from Blackthorn into the early world, not as an early climb toward Blackthorn.

Use ledges, elevation, cave barriers, or progression flags to preserve this directionality.

### Cherrygrove → Ilex → Rustboro

The first mandatory dungeon-like area is Ilex Forest.

The player should reach Rustboro only after enough route space exists to support the large LC encounter pool.

---

# Stage 1 — Rustboro and Early Sea Cottage

## Rustboro

**Gym 1 — Roxanne**

Rustboro is the first major city.

## Route 24 / Route 25 / Sea Cottage Branch

The current topology's early Route 24 / Route 25 branch is retained.

This branch is **optional** and should terminate at **Bill's Sea Cottage**.

Primary reward:

- **Gift Eevee #1**

Do not place central-plot-required information here.

The branch should be short enough that an early player can explore it without derailing pacing before Mt. Moon.

---

# Stage 2 — Mt. Moon to Goldenrod

Progression:

**Rustboro → Route 44 → Mt. Moon → Route 33 → Goldenrod**

Mt. Moon is the first mandatory Team Rocket dungeon.

Goldenrod is Gym 2 and the first large service hub.

---

# Stage 3 — Goldenrod to Ecruteak

Preserve the Johto-like chain:

**Goldenrod → Route 35 → National Park → Route 36 → Route 37 → Ecruteak**

This is one of the most coherent native-feeling sections of the region and should remain largely intact.

## Route 36 East Shortcut — Locked

Route 36 has an eastward connection to the west side of Route 110.

On the player's first visit, this connection is blocked.

**Required rule:** the player cannot use Route 36 → Route 110 to bypass Ecruteak, Morty, Route 119, Weather Institute, or the intended first arrival at Fortree.

Recommended implementation:

- barrier controlled by `FLAG_REACHED_FORTREE` or equivalent
- obstruction is removed/opened from the Route 110 side after Fortree is reached

After unlocking:

**Route 36 ↔ Route 110**

becomes permanently bidirectional.

This is a traversal shortcut, not a new story sequence.

---

# Stage 4 — Ecruteak as Midgame and Endgame Junction

Ecruteak has three meaningful directional roles.

## South

Returns toward Route 37 / National Park / Goldenrod.

## East — Main Midgame Progression

**Ecruteak east → Route 119 → Weather Institute → Fortree**

This is the canonical route after Gym 3.

Do not route the player's first Route 119 access through Route 36.

## West — League Route

Ecruteak's west exit is reserved for:

**Victory Road → Pokémon League**

It remains locked until the player has all eight Badges.

Recommended presentation:

- visible League gate
- guard checking Badges
- closed mountain pass
- inaccessible gatehouse

The player should be able to understand its future importance on the first Ecruteak visit.

---

# Stage 5 — Route 119 / Fortree / Route 110

Progression:

**Ecruteak → Route 119 → Weather Institute → Fortree**

Fortree is Gym 4.

After entering Fortree or defeating Winona, unlock the Route 110 ↔ Route 36 shortcut.

The forward route continues through Route 110 toward Lavender.

This gives Route 110 two roles:

1. forward connection from Fortree toward Lavender
2. later shortcut back to Route 36 / National Park / Goldenrod side of the world

---

# Stage 6 — Lavender and Locked Saffron

## Lavender

Lavender is the mandatory Pokémon Tower / Team Rocket II story node.

Its westward/main-story exit leads to Route 8.

Its **south exit remains closed for the entire main game** and is reserved for the postgame harbor.

## Saffron Lock

Before Mossdeep, **all surface entrances into Saffron are blocked**.

This applies even though Route 7 and Route 8 lie on opposite sides of the city.

The player must not enter Saffron during the Lavender-to-Cinnabar trip.

## Underground Bypass

Main-story progression after Lavender:

**Lavender → Route 8 → Underground Path → Route 7 → Route 103 → south to Cinnabar**

This is a core Version 7 traversal beat.

It deliberately recreates the classic idea of bypassing inaccessible Saffron while making the city physically central to Plastic Ox.

The Underground Path should remain usable before Saffron itself opens.

---

# Stage 7 — Route 103 to Cinnabar

Route 103 is reused as a cross-region connector.

The player emerges from the Route 7 side of the underground bypass, crosses Route 103, and takes its southward connection toward Cinnabar.

This route intentionally brings the player back through geography adjacent to earlier portions of the world without requiring a full retrace.

## Cinnabar

**Gym 5 — Blaine**

The Gym is open immediately.

Defeating Blaine grants the key to Pokémon Mansion.

### Pokémon Mansion

Mandatory after Blaine for the Cinnabar story investigation.

Includes:

- archival research
- Entei encounter
- exit back to Cinnabar / southern sea progression

---

# Stage 8 — Directed Southern Sea Passage

The post-Cinnabar route should be strongly directed eastward toward Mossdeep.

Use:

**Cinnabar → coastal route → Seafoam Islands → coastal route → Mossdeep**

The current topology's southern connector can retain Route 41 as the external route module if desired, but **Seafoam Islands replace Whirl Islands as the mandatory dungeon**.

## Seafoam Traversal Rule

The player must not be able to simply Surf around Seafoam.

Use one or more of:

- currents
- rocks
- blocked open-water edge
- cave-only connection between west/east map halves
- elevation changes
- one-way drops

The intended behavior is:

> enter Seafoam from Cinnabar side → traverse dungeon → exit on Mossdeep side

This keeps the southern pass visually and mechanically directed.

---

# Stage 9 — Mossdeep and the Saffron Unlock

## Mossdeep

**Gym 6 — Tate & Liza**

After Gym 6, the player completes the Space Center story event.

## Global Saffron Unlock

The Space Center completion flag opens Saffron's surface entrances.

Recommended flag:

`FLAG_MOSSDEEP_SPACE_CENTER_COMPLETE`

Before this flag:

- Saffron inaccessible
- Underground Path Route 8 ↔ Route 7 usable

After this flag:

- Route 7 ↔ Saffron opens
- Route 8 ↔ Saffron opens
- southern/Mossdeep approach ↔ Saffron opens
- Saffron becomes the primary late-game hub
- Saffron north exit opens toward the northern OU region

---

# Stage 10 — Saffron Hub and Two Objectives

Saffron contains:

1. **Fighting Dojo / Bruno — Gym 7**
2. **Silph Co. / Team Rocket III / Giovanni / system core**

These may be completed in either order, before or after exploring the northern
OU region and challenging Clair. Bruno and Silph do not gate the eighth Gym.

Track separate flags:

- `FLAG_BRUNO_DEFEATED`
- `FLAG_SILPH_CORE_RESOLVED`

## North Gate

Saffron's north exit toward Route 5 opens when the Space Center opens the city.
Neither Bruno's Badge nor Silph completion is required to explore Meteor Falls,
reach Blackthorn, or challenge Clair. This is an open-ended OU region.

The access condition is:

```text
MOSSDEEP_SPACE_CENTER_COMPLETE
```

The available route is:

**Saffron → Route 5 → Route 115 → Meteor Falls → Blackthorn**

---

# Stage 11 — Meteor Falls to Blackthorn

This is the final Gym approach.

Progression:

**Route 5 → Route 115 → Meteor Falls → Blackthorn**

Meteor Falls replaces Ice Path functionally:

- major mountain dungeon
- late-game encounters
- vertical navigation
- strong trainers / optional branches
- clear arrival into isolated Blackthorn

## Blackthorn

**Gym 8 — Clair**

After defeating Clair:

- award Clair's eighth-slot Badge independently of Bruno's seventh-slot Badge
- unlock Ecruteak west only if all eight native Badge flags are set; earning Clair's Badge first does not satisfy this check
- preserve Blackthorn's southward Route 45 / Route 46 path as a fast downhill return toward the earlier world

If Bruno is the last Gym defeated, his victory supplies the remaining Badge
and makes the same League gate check succeed. Prefer deriving all-Badges state
from the eight Badge flags rather than setting it unconditionally on Clair.

---

# Stage 12 — League Return Through Ecruteak

The main League approach is intentionally **not** attached directly to Blackthorn.

The player returns to Ecruteak and finally uses the west exit that has been visible since Gym 3.

Progression:

**Ecruteak west → Victory Road → Pokémon League → Elite Four → Champion Bill**

This gives Ecruteak a satisfying second major role and closes a long-standing map promise.

---

# Postgame — Lavender South / Battle Frontier / Uber Islands

Lavender's southern exit remains unavailable until the player becomes Champion.

Recommended condition:

`FLAG_BECAME_CHAMPION`

Afterward:

**Lavender south → harbor / ferry → Battle Frontier → postgame island network**

The postgame island network is the preferred home for:

- Uber-tier Pokémon
- legendary encounters excluded from main progression
- extreme-level trainers
- Battle Frontier facilities
- rematch content
- superbosses
- rare tutors/items

This prevents Uber availability from interfering with the main game's LC→PU→NU→RU→UU→UUBL→OU progression.

---

# Important Gating Matrix

| Connection / Area | Initial State | Unlock Condition | Purpose |
|---|---|---|---|
| Route 36 east ↔ Route 110 west | Blocked | Reach Fortree | Midgame shortcut; prevents Morty/Route119 skip |
| Ecruteak east → Route 119 | Open after Morty progression | Gym/story progression | Canonical path to Weather Institute/Fortree |
| Saffron surface entrances | Blocked | Complete Mossdeep Space Center | Keeps Saffron late-game while allowing underground bypass |
| Route 8 ↔ Route 7 Underground Path | Open | Available during Lavender segment | Main Lavender→Cinnabar bypass |
| Saffron north → Route 5 | Blocked with Saffron | Complete Mossdeep Space Center | Opens the northern OU region independently of Bruno and Silph |
| Ecruteak west → Victory Road | Blocked | 8 Badges | League finale |
| Lavender south → harbor | Blocked | Become Champion | Postgame Frontier/Uber islands |
| Blackthorn → Route 45/46 return | Directionally constrained | Reach Blackthorn | Fast late-game return; no early Blackthorn bypass |
| Seafoam west→east passage | Mandatory dungeon | Reach Cinnabar segment | Directed southern progression to Mossdeep |

---

# World-Folding Payoffs

Version 7 should deliberately reward progression by shortening travel.

## After Fortree

**Route 110 ↔ Route 36** opens.

The eastern and central halves of the midgame become directly connected.

## After Mossdeep

**Saffron opens.**

Routes previously separated by the sealed city become part of a central hub.

## After Blackthorn

The downhill Route 45 / Route 46 path gives a fast return into the early region.
Ecruteak's west League gate becomes available once all eight Badges are held;
Bruno may still be outstanding when the player first returns from Blackthorn.

## After Champion

Lavender's unused south edge transforms into the postgame transportation hub.

The player should repeatedly experience the same idea:

> **A place that used to be a barrier becomes a shortcut or destination later.**

---

# Main-Story Geographic Shape

The final macro-flow is:

### Act I — Western / early region

**Pallet → Oldale → Cherrygrove → Ilex → Rustboro → Mt. Moon → Goldenrod**

### Act II — Central / northern region

**Goldenrod → National Park → Ecruteak**

### Act III — Eastern region

**Ecruteak → Route 119 → Fortree → Route 110 → Lavender**

### Act IV — Beneath the locked center and into the south

**Lavender → Route 8 Underground → Route 7 → Route 103 → Cinnabar → Seafoam → Mossdeep**

### Act V — Central convergence

**Mossdeep → Saffron opens → Bruno, Silph, and the northern OU region in open order**

### Act VI — Northern mountains

**Saffron → Route 5 → Route 115 → Meteor Falls → Blackthorn**

### Finale — Return to a familiar crossroads

**return to Ecruteak → west gate → Victory Road → League**

### Postgame

**Lavender south → ferry → Battle Frontier / Uber islands**

---

# Implementation Principle

The map team should treat Version 7 as a **directed progression graph layered onto recognizable existing maps**.

The most important implementation work is not new map art. It is:

1. correct connection endpoints
2. story flags
3. one-way constraints
4. blockers that disappear at meaningful times
5. safe handling of Fly / Surf / cave shortcuts
6. preventing sequence breaks into Saffron, Blackthorn, Victory Road, and the postgame
7. preserving convenient late-game return paths once their corresponding story content is complete

The player should feel that the world was always connected this way—even when the game did not yet allow them to use every connection.
