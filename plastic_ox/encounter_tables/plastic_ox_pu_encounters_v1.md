# Pokémon Plastic Ox — PU Encounter Tables v1.0

## Scope

This document defines the **PU encounter progression immediately after the LC block**.

Player progression:

**Mt. Moon → Route 33 → Goldenrod City → Route 35 → National Park → Route 36 → Static Sudowoodo**

This block corresponds to **Gym 2 — PU**, with a level cap of **20**.  
The Route 36 Sudowoodo is intentionally treated as the **transition into NU** because Sudowoodo is NU-legal rather than PU-legal in the project tier progression.

This document is designed to continue the encounter philosophy established in the current LC encounter document:

- every percentage table sums to exactly 100%;
- ordinary encounter rates do not fall below 5%;
- a species should normally be a `>=20%` primary species in only one distinct area;
- adjacent areas should have recognizable identities rather than recycling the same anchors;
- time-of-day substitutions affect only a minority of slots;
- Headbutt populations are area-specific;
- Old Rod is the early fishing method;
- evolved Pokémon are generally obtained by raising earlier catches rather than being inserted into wild tables merely because they become tier-legal;
- strong or lore-rare Pokémon may remain uncommon even when their tier permits them.

## Hard constraints carried forward

1. **Pineco is an Ilex Forest Headbutt exclusive.**
   - Do not place Pineco in any PU Headbutt, grass, cave, gift, or special table.
2. **Unown is skipped in this progression.**
   - PU legality does not require a forced Ruins of Alph encounter here.
3. **Magikarp, Feebas, Diglett, and Shroomish families remain withheld until OU.**
4. **Sudowoodo is not a random Route 36 encounter.**
5. **Sudowoodo only becomes catchable after Whitney, marking the PU → NU handoff.**
6. **Castform and Luvdisc are Goldenrod Game Corner prizes.**
7. **Corsola is obtainable with the Old Rod on Route 35.**
8. **Delibird is obtained through the Route 35 mail event rather than as a random wild encounter.**

---

# 1. Mt. Moon

Mt. Moon carries more of the new-PU distribution burden than the small outdoor maps that follow it.

The recognizable ecological core remains:

- Zubat
- Geodude
- Paras
- Clefairy

The new emphasis is on **minerals, strange cave fauna, and Moon-associated species**, distinguishing Mt. Moon from the earlier Dark Cave.

## Mt. Moon 1F — Cave

**Levels: 12–14**

| Pokémon | Rate |
|---|---:|
| **Nosepass** | **25%** |
| Zubat | 15% |
| Geodude | 15% |
| Paras | 15% |
| **Meditite** | 10% |
| Clefairy | 10% |
| **Mawile** | 5% |
| **Shuckle** | 5% |
| **Total** | **100%** |

### Design rationale

**Nosepass** is the defining upper-floor species rather than making Zubat or Geodude the primary encounter yet again.

Mawile is deliberately rare because it is one of the stronger PU additions. Shuckle is also kept rare because its unusual ecology makes it feel more like a discovery than ordinary cave fauna.

---

## Mt. Moon B1F / B2F — Cave

**Levels: 14–16**

| Pokémon | Rate |
|---|---:|
| **Clefairy** | **20%** |
| Nosepass | 15% |
| Zubat | 15% |
| Geodude | 15% |
| Paras | 10% |
| **Mawile** | 10% |
| **Shuckle** | 10% |
| **Meditite** | 5% |
| **Total** | **100%** |

### Design rationale

The deeper cave becomes the stranger, more Moon-associated portion of the dungeon.

Clefairy is one of the few evolved-from-an-LC-root Pokémon that deserves a direct wild encounter because **Mt. Moon is its iconic habitat**.

The two Mt. Moon tables share the same ecological family but shift their anchors and rarities enough to make deeper exploration meaningful.

---

## Mt. Moon — Helix Fossil

A **Helix Fossil** is obtained in Mt. Moon.

It should **not** be mutually exclusive with another fossil.

The player can return to Devon in Rustboro to revive:

**Omanyte — Lv. 15**

If fossil revival is not already active by this point, Devon revival should be enabled when the player obtains the Helix Fossil so that Omanyte is genuinely available during PU.

---

## Mt. Moon — Moon Stones

Mt. Moon should contain **at least two obtainable Moon Stones** during the PU block.

These support newly legal PU evolutions such as:

- Wigglytuff
- Delcatty

Higher-tier Moon Stone evolutions remain blocked by the tier-gating system.

---

# 2. Route 33

Route 33 is a small mountain-foot route and should remain compact.

Its identity is:

- scruffy foothill mammals;
- light carryover from cave fauna;
- Aipom-dominated Headbutt trees;
- a rare Seviper hunt.

## Route 33 — Grass

**Levels: 14–16**

| Rate | Morning | Day | Night |
|---:|---|---|---|
| **25%** | **Zigzagoon** | **Zigzagoon** | **Zigzagoon** |
| 20% | Spearow | Spearow | Rattata |
| 15% | Hoppip | Hoppip | Spinarak |
| 10% | Geodude | Geodude | Geodude |
| 10% | Ekans | Ekans | Ekans |
| 10% | **Spinda** | **Spinda** | **Spinda** |
| 5% | **Seviper** | **Seviper** | **Seviper** |
| 5% | Zubat | Zubat | Zubat |
| **100%** |  |  |  |

### Design rationale

Zigzagoon becomes the area's defining new PU species.

The Spearow → Rattata and Hoppip → Spinarak substitutions provide recognizable Johto day/night flavor without replacing the whole table.

**Seviper is 5%** because it is one of the strongest PU Pokémon in the supplied viability ranking.

---

## Route 33 — Headbutt

**Levels: 14–16**

| Pokémon | Rate |
|---|---:|
| **Aipom** | **30%** |
| Spearow | 25% |
| Exeggcute | 15% |
| Natu | 10% |
| Slakoth | 10% |
| Hoothoot | 10% |
| **Total** | **100%** |

### Design rationale

Route 33 is the **Aipom Headbutt area**.

This preserves Aipom's recognizable Johto tree association and makes it easy enough to intentionally hunt without turning it into ordinary grass filler.

**Pineco does not appear here.** It remains exclusive to Ilex Forest Headbutt.

---

# 3. Goldenrod City

Goldenrod does **not** receive an artificial grass encounter table.

The city instead introduces unusual Pokémon through deliberate urban acquisition methods.

## Goldenrod Game Corner

Suggested prize roster:

| Pokémon | Level | Suggested cost | Role |
|---|---:|---:|---|
| Abra | 15 | 200 coins | Cheap classic psychic prize; also available wild on Route 35 |
| **Luvdisc** | 15 | 500 coins | Novelty / imported rare Pokémon |
| **Castform** | 15 | 1,500 coins | Special regional prize |
| **Porygon** | 15 | 4,000 coins | Premium technical prize |

### Design rationale

These should feel like **rare Pokémon acquired through Goldenrod's cosmopolitan Game Corner**, not species arbitrarily stuffed into nearby wild tables.

Porygon is the premium reward.

Castform and Luvdisc solve otherwise awkward early-game habitat problems without compromising encounter ecology.

Abra is intentionally duplicated later on Route 35 so that players are never forced to engage with the Game Corner to use Abra.

---

# 4. Route 35

Route 35 should retain the recognizable Gen II mix of:

- Abra
- Ditto
- Yanma
- Nidoran
- Drowzee

while adding PU species that fit its park-edge / meadow ecology.

Its water receives the first PU-accessible Corsola population.

## Route 35 — Grass

**Levels: 16–18**

| Pokémon | Rate |
|---|---:|
| **Farfetch'd** | **30%** |
| Drowzee | 15% |
| Nidoran♀ | 15% |
| Nidoran♂ | 15% |
| **Abra** | 10% |
| **Minun** | 5% |
| **Ditto** | 5% |
| **Yanma** | 5% |
| **Total** | **100%** |

### Design rationale

Farfetch'd is the Route 35 grass anchor.

The three 5% encounters are intentional:

- **Minun** — extremely strong within PU;
- **Ditto** — inherently unusual and canonically rare on Route 35;
- **Yanma** — an iconic rare Route 35 hunt.

This is one of the few tables where three separate 5% encounters are justified.

---

## Route 35 — Headbutt

**Levels: 16–18**

| Rate | Morning / Day | Night |
|---:|---|---|
| **30%** | **Spearow** | **Hoothoot** |
| 20% | Exeggcute | Exeggcute |
| 15% | Natu | Natu |
| 15% | Sunkern | Sunkern |
| 10% | Venonat | Venonat |
| 10% | Hoothoot | Spearow |
| **100%** |  |  |

### Design rationale

Route 35 trees are **roadside bird trees**, distinct from:

- Route 33's Aipom trees;
- National Park's Bug canopy;
- Route 36's old / psychic trees.

**Pineco is intentionally absent.**

---

## Route 35 — Old Rod

**Levels: 16–18**

| Pokémon | Rate |
|---|---:|
| Poliwag | **30%** |
| Goldeen | 25% |
| Barboach | 20% |
| **Corsola** | 15% |
| Psyduck | 10% |
| **Total** | **100%** |

### Design rationale

This is a freshwater / park-corridor fishing table rather than a universal early-game fishing population.

Corsola is uncommon but practical to hunt at 15%.

**Magikarp does not appear** because the Gyarados family is explicitly OU-gated.

Corphish is intentionally omitted here so that later swampier or Hoenn-style waters can have a stronger identity.

---

## Route 35 — Delibird mail event

Adapt the familiar Johto mail-delivery event.

Instead of loaning the player Spearow, the gate guard gives:

**Delibird — Lv. 16 — holding Mail**

The player delivers the Mail to the intended NPC.

After completing the delivery, the recipient tells the player to keep Delibird.

### Design rationale

This is much stronger than putting Delibird into temperate roadside grass at 5%.

It makes Delibird memorable, preserves a recognizable Johto event, and solves the species' awkward habitat fit.

---

# 5. National Park

National Park should be one of the strongest encounter identities in the PU block.

Use:

**normal exploration table + separate Bug-Catching Contest table**

The normal park remains a cultivated meadow / preserve.

The Contest becomes the concentrated Bug acquisition event.

---

## National Park — Normal grass

**Levels: 17–19**

| Rate | Morning | Day | Night |
|---:|---|---|---|
| **25%** | **Hoppip** | **Hoppip** | **Hoppip** |
| 15% | Nidoran♀ | Nidoran♀ | Nidoran♀ |
| 15% | Nidoran♂ | Nidoran♂ | Nidoran♂ |
| 10% | **Lickitung** | **Lickitung** | **Lickitung** |
| 10% | Jigglypuff | Jigglypuff | Jigglypuff |
| 10% | Pidgey | Pidgey | Hoothoot |
| 10% | Ledyba | Ledyba | Spinarak |
| 5% | **Tropius** | **Tropius** | **Tropius** |
| **100%** |  |  |  |

### Design rationale

National Park functions as Plastic Ox's preserve / Safari-style location.

Lickitung fits the idea of a rare park animal better than an ordinary roadside encounter.

Tropius is competitively modest but remains 5% because its size and exotic appearance should make it feel unusual.

Night changes only two 10% slots, keeping the core population stable.

---

## National Park — Bug-Catching Contest

**Levels: 17–20**

| Pokémon | Rate |
|---|---:|
| Caterpie | **20%** |
| Weedle | **20%** |
| Metapod | 10% |
| Kakuna | 10% |
| Paras | 10% |
| Venonat | 10% |
| Butterfree | 5% |
| Beedrill | 5% |
| **Volbeat** | 5% |
| **Illumise** | 5% |
| **Total** | **100%** |

### Design rationale

This intentionally resembles the original Bug-Catching Contest structure.

Scyther and Pinsir are withheld because they do not unlock until UU.

Their rare slots are replaced by the newly PU-available Volbeat and Illumise.

### Contest availability

The Contest mechanics should remain recognizable, but **PU Pokédex completion should not depend on a real-world weekday**.

Recommended implementation:

- Contest available every in-game day after the player first reaches National Park.
- Normal park encounters remain separate from Contest encounters.

### First-place prize

**Sun Stone**

This naturally supports the newly PU-legal Sunflora evolution.

---

## National Park — Headbutt

**Levels: 17–19**

| Rate | Morning / Day | Night |
|---:|---|---|
| **30%** | **Ledyba** | **Spinarak** |
| 15% | Exeggcute | Exeggcute |
| 15% | Aipom | Aipom |
| 15% | Taillow | Taillow |
| 15% | Wurmple | Wurmple |
| 10% | Sunkern | Sunkern |
| **100%** |  |  |

### Design rationale

This is the **Bug-canopy tree population**.

It is intentionally distinct from Route 33 and Route 35.

**Pineco does not appear.**

---

# 6. Route 36

Route 36 transitions from the cultivated park environment toward older, stranger Johto terrain.

Its identity is:

- dense plants;
- psychic / unusual fauna;
- subtle old-tree / ruins atmosphere;
- the Sudowoodo obstruction.

No Unown side table is required.

## Route 36 — Grass

**Levels: 18–20**

| Rate | Morning | Day | Night |
|---:|---|---|---|
| **25%** | **Bellsprout** | **Bellsprout** | **Bellsprout** |
| **20%** | **Natu** | **Natu** | **Natu** |
| 10% | **Tangela** | **Tangela** | **Tangela** |
| 10% | Vulpix | Vulpix | Gastly |
| 10% | Pidgey | Pidgey | Hoothoot |
| 10% | Hoppip | Hoppip | Hoppip |
| 10% | Drowzee | Drowzee | Drowzee |
| 5% | Baltoy | Baltoy | Baltoy |
| **100%** |  |  |  |

### Design rationale

Bellsprout gives the route an overgrown identity.

Natu is the second major species and hints at the stranger terrain beyond the park without requiring Unown.

Tangela is kept at 10% because of its competitive strength and because a Tangela encounter feels more noteworthy than ordinary roadside flora.

The night table replaces only Vulpix and Pidgey with Gastly and Hoothoot.

---

## Route 36 — Headbutt

**Levels: 18–20**

| Pokémon | Rate |
|---|---:|
| **Natu** | **30%** |
| Slakoth | 20% |
| Exeggcute | 15% |
| Aipom | 15% |
| Shuppet | 10% |
| Duskull | 10% |
| **Total** | **100%** |

### Design rationale

Route 36 is the **old / psychic tree population**.

Its unusual ghostly secondary encounters distinguish it from the park trees immediately before it.

Again, **Pineco is absent by design**.

---

# 7. Static Sudowoodo — PU → NU transition

Sudowoodo remains the recognizable Route 36 progression obstacle.

**Species:** Sudowoodo  
**Level:** 20  
**Encounter type:** Static  
**Trigger:** SquirtBottle  
**Catchable:** Yes  
**Random Route 36 encounter:** No

## Suggested moveset

- Rock Throw
- Mimic
- Flail
- Low Kick

## Progression behavior

- Before Whitney is defeated, the player cannot permanently resolve the Sudowoodo obstruction.
- After Whitney, the SquirtBottle can trigger the encounter.
- **Catching or defeating Sudowoodo permanently clears the obstruction.**
- Running from the battle leaves Sudowoodo in place so the player cannot accidentally lose the encounter or clear the route without resolving it.

### Tier rationale

Sudowoodo is an **NU** species in Plastic Ox.

Therefore this battle functions as the clean mechanical handoff:

**PU exploration → Whitney → SquirtBottle → Sudowoodo → NU progression**

---

# PU new-encounter-line coverage audit

The PU tier introduces 25 encounter lines that were not already obtainable during LC.

Unown is deliberately skipped, leaving **24 intended PU lines** to place in this progression.

| New PU line | First obtainable | Method | Notes |
|---|---|---|---|
| Abra | Goldenrod | Game Corner prize | Also Route 35 grass at 10% |
| Farfetch'd | Route 35 | Wild grass | 30% area anchor |
| Lickitung | National Park | Wild grass | 10% |
| Tangela | Route 36 | Wild grass | 10% |
| Ditto | Route 35 | Wild grass | 5% |
| Porygon | Goldenrod | Game Corner prize | Premium prize |
| Omanyte | Mt. Moon / Devon | Fossil revival | Helix Fossil from Mt. Moon |
| Aipom | Route 33 | Headbutt | 30% tree anchor |
| Yanma | Route 35 | Wild grass | 5% |
| Unown | — | Intentionally skipped | No forced Ruins encounter |
| Shuckle | Mt. Moon | Cave | 5–10% |
| Corsola | Route 35 | Old Rod | 15% |
| Delibird | Route 35 | Gift / event | Mail-delivery event |
| Zigzagoon | Route 33 | Wild grass | 25% area anchor |
| Nosepass | Mt. Moon | Cave | 15–25% |
| Mawile | Mt. Moon | Cave | 5–10% |
| Meditite | Mt. Moon | Cave | 5–10% |
| Minun | Route 35 | Wild grass | 5%; strong PU species |
| Volbeat | National Park | Bug-Catching Contest | 5% |
| Illumise | National Park | Bug-Catching Contest | 5% |
| Spinda | Route 33 | Wild grass | 10% |
| Seviper | Route 33 | Wild grass | 5%; strong PU species |
| Castform | Goldenrod | Game Corner prize | Imported / special prize |
| Tropius | National Park | Wild grass | 5% |
| Luvdisc | Goldenrod | Game Corner prize | Imported / novelty prize |

## Coverage result

- New PU encounter lines in tier document: **25**
- Intentionally skipped: **1 — Unown**
- Intended new PU lines: **24**
- Intended new PU lines obtainable by end of Route 36: **24 / 24**
- Coverage of intended roster: **100%**

---

# Evolution-based PU availability

Most newly legal PU Pokémon should be obtained by raising Pokémon already caught during LC.

## Standard level evolutions

- Ivysaur — Lv. 16
- Charmeleon — Lv. 16
- Wartortle — Lv. 16
- Metapod — Lv. 7
- Butterfree — Lv. 10
- Kakuna — Lv. 7
- Beedrill — Lv. 10
- Pidgeotto — Lv. 18
- Nidorina — Lv. 16
- Nidorino — Lv. 16
- Bayleef — Lv. 16
- Quilava — Lv. 14
- Croconaw — Lv. 18
- Furret — Lv. 15
- Noctowl — Lv. 20
- Ledian — Lv. 18
- Flaaffy — Lv. 15
- Skiploom — Lv. 18
- Grovyle — Lv. 16
- Combusken — Lv. 16
- Marshtomp — Lv. 16
- Mightyena — Lv. 18
- Silcoon — Lv. 7
- Beautifly — Lv. 10
- Cascoon — Lv. 7
- Dustox — Lv. 10
- Lombre — Lv. 14
- Nuzleaf — Lv. 14
- Kirlia — Lv. 20
- Loudred — Lv. 20

## Friendship evolutions

The existing tier system permits these once PU is unlocked:

- Clefairy
- Jigglypuff
- Togetic
- Marill

## Item evolutions

### Moon Stone

- Wigglytuff
- Delcatty

### Sun Stone

- Sunflora

Higher-tier outcomes using these same items remain tier-blocked.

---

# Downward evolution-level changes for PU

The following evolutions are lowered to the PU cap of **Lv. 20**:

| Evolution | Vanilla | Plastic Ox |
|---|---:|---:|
| Ekans → Arbok | 22 | **20** |
| Oddish → Gloom | 21 | **20** |
| Paras → Parasect | 24 | **20** |
| Poliwag → Poliwhirl | 25 | **20** |
| Bellsprout → Weepinbell | 21 | **20** |
| Geodude → Graveler | 25 | **20** |
| Krabby → Kingler | 28 | **20** |
| Horsea → Seadra | 32 | **20** |
| Goldeen → Seaking | 33 | **20** |
| Dratini → Dragonair | 30 | **20** |
| Spinarak → Ariados | 22 | **20** |
| Slugma → Magcargo | 38 | **20** |
| Surskit → Masquerain | 22 | **20** |
| Aron → Lairon | 32 | **20** |
| Gulpin → Swalot | 26 | **20** |
| Trapinch → Vibrava | 35 | **20** |
| Spheal → Sealeo | 32 | **20** |
| Bagon → Shelgon | 30 | **20** |

**Total downward PU evolution changes: 18**

---

# Shedinja implementation note

Shedinja becomes legal in PU while Ninjask is not legal until UU.

Vanilla Gen III normally produces Shedinja only when Nincada evolves into Ninjask.

Recommended Plastic Ox behavior:

At **Lv. 20**, if the player has:

- Nincada;
- an empty party slot;
- a spare Poké Ball;

then **Shedinja is created while Nincada remains Nincada**.

Later, once UU is unlocked, Nincada can evolve normally into Ninjask.

This preserves both tier gates without requiring a wild Shedinja encounter.

---

# Special / non-wild PU acquisitions

| Pokémon | Location | Method |
|---|---|---|
| Omanyte | Mt. Moon → Devon | Helix Fossil revival |
| Abra | Goldenrod | Game Corner prize |
| Luvdisc | Goldenrod | Game Corner prize |
| Castform | Goldenrod | Game Corner prize |
| Porygon | Goldenrod | Game Corner prize |
| Delibird | Route 35 | Mail-delivery gift |
| Sunflora | National Park | Sun Stone from Contest prize + evolution |

---

# Mechanical table audit

## Percentage totals

All percentage-based tables sum to exactly **100%**.

| Area | Method | Total |
|---|---|---:|
| Mt. Moon 1F | Cave | 100% |
| Mt. Moon B1F/B2F | Cave | 100% |
| Route 33 | Grass | 100% |
| Route 33 | Headbutt | 100% |
| Route 35 | Grass | 100% |
| Route 35 | Headbutt | 100% |
| Route 35 | Old Rod | 100% |
| National Park | Normal grass | 100% |
| National Park | Bug-Catching Contest | 100% |
| National Park | Headbutt | 100% |
| Route 36 | Grass | 100% |
| Route 36 | Headbutt | 100% |

**Percentage tables:** 12  
**Tables below / above 100%:** 0

---

## Encounters below 5%

**None.**

5% is the minimum ordinary encounter rate.

---

# Primary-species repetition audit

A primary species is defined as approximately `>=20%`.

## Primary anchors by area / method

| Area / method | Primary species |
|---|---|
| Mt. Moon 1F | Nosepass 25% |
| Mt. Moon B1F/B2F | Clefairy 20% |
| Route 33 grass | Zigzagoon 25%; Spearow/Rattata 20% |
| Route 33 Headbutt | Aipom 30%; Spearow 25% |
| Route 35 grass | Farfetch'd 30% |
| Route 35 Headbutt | Spearow/Hoothoot 30%; Exeggcute 20% |
| Route 35 Old Rod | Poliwag 30%; Goldeen 25%; Barboach 20% |
| National Park grass | Hoppip 25% |
| National Park Contest | Caterpie 20%; Weedle 20% |
| National Park Headbutt | Ledyba/Spinarak 30% |
| Route 36 grass | Bellsprout 25%; Natu 20% |
| Route 36 Headbutt | Natu 30%; Slakoth 20% |

## Cross-area `>=20%` repeats

### Spearow

Spearow reaches `>=20%` in:

- Route 33 grass / Headbutt;
- Route 35 Headbutt during Morning / Day.

This is an intentional exception because Spearow acts as a recognizable Johto roadside / tree bird between the two adjacent routes.

Its **encounter method and role change**:

- Route 33: mountain foothill bird;
- Route 35: tree-canopy daytime bird.

If a stricter one-primary-area rule is desired, reduce Route 35 daytime Spearow to 15% and move the extra 15% into Exeggcute / Natu.

### Natu

Natu reaches:

- Route 36 grass — 20%;
- Route 36 Headbutt — 30%.

These are the **same physical area**, so this does not violate the cross-area primary rule.

No other species is a `>=20%` primary encounter in more than one different area.

---

# Species-frequency / duplication audit

## Species intentionally recurring across several tables

### Exeggcute

Appears in several Headbutt populations as connective Johto tree ecology.

It is never used as the defining species of every area.

### Aipom

Appears strongly on Route 33 and secondarily in later trees.

Route 33 remains its clear signature location.

### Natu

Appears as minor tree fauna before becoming a defining Route 36 species.

This creates progression rather than repetitive filler.

### Hoppip / Hoothoot / Spearow / common bugs

These recur as regional connective tissue and receive different roles by area and time of day.

---

# Pineco exclusivity audit

**Pineco appears in zero PU tables.**

Global rule:

> **Pineco is obtainable only through Headbutt in Ilex Forest.**

Any older table that places Pineco outside Ilex Forest should be revised to preserve this exclusivity.

---

# Fishing repetition audit

Only Route 35 receives a PU-accessible Old Rod table in this sequence.

This avoids creating multiple nearly identical early fishing populations.

Route 35's identity:

- Poliwag
- Goldeen
- Barboach
- Corsola
- Psyduck

Later bodies of water should deliberately use different anchors.

---

# Headbutt identity audit

| Area | Tree identity |
|---|---|
| Ilex Forest | **Pineco-exclusive home** |
| Route 33 | **Aipom trees** |
| Route 35 | **roadside bird trees** |
| National Park | **Bug canopy** |
| Route 36 | **old / psychic trees** |

This progression is intentionally non-universal.

---

# Canonical placement changes

## Farfetch'd → Route 35

Moved earlier from its later Johto habitat so that it is usable during PU.

The park-edge meadow remains ecologically appropriate.

## Lickitung → National Park

Moved earlier from Route 44.

National Park's preserve role makes Lickitung feel like a rare park animal rather than ordinary roadside filler.

## Tangela → Route 36

Moved earlier from Route 44.

Route 36's overgrown identity and existing Johto Tangela association make this a strong early placement.

## Porygon → Goldenrod Game Corner

Uses a classic Game Corner acquisition identity instead of forcing a wild habitat.

## Castform → Goldenrod Game Corner

Deliberately moved away from its canonical Weather Institute acquisition because the project wants the full intended PU roster obtainable during this block.

It is framed as a rare imported / special prize rather than a local wild species.

## Luvdisc → Goldenrod Game Corner

Avoids placing a marine species into inappropriate freshwater merely for coverage.

## Volbeat / Illumise → National Park Contest

Use the rare Bug-Contest niche while Scyther and Pinsir remain tier-gated until UU.

## Corsola → Route 35 Old Rod

Moved inland relative to its usual marine identity in order to give Route 35 fishing a distinct PU unlock.

Its 15% rate makes it a deliberate target rather than an ultra-rare catch.

## Unown

Intentionally omitted despite PU legality.

No Ruins detour is added solely to satisfy mathematical coverage.

---

# Second design review

## Mt. Moon

**Status: strong**

The dungeon supports two related but distinct tables and carries an appropriate share of the PU additions.

No individual table is overloaded.

## Route 33

**Status: strong**

Compact grass table, memorable Aipom trees, rare Seviper, and a clear foothill identity.

## Goldenrod

**Status: strong**

No artificial wild table.

Four Game Corner prizes are enough to make the location interesting without turning it into a Pokédex vending machine.

## Route 35

**Status: intentionally dense**

The grass table contains three 5% species, but each has a strong reason.

Fishing gives Corsola a practical home without adding another grass slot.

The Delibird event removes another awkward species from the wild table.

## National Park

**Status: strongest identity in the block**

Separating normal exploration from the Bug-Catching Contest prevents the park from becoming one giant Bug table.

The Contest is the correct place for Volbeat and Illumise.

## Route 36

**Status: strong**

The grass table transitions naturally toward stranger Johto terrain.

The old-tree Headbutt population feels different from National Park.

Unown is correctly omitted.

## Sudowoodo

**Status: strong progression gate**

The static encounter preserves one of Johto's signature progression moments while cleanly introducing the next competitive tier.

---

# Final recommended PU progression

**Mt. Moon**
- Nosepass
- Mawile
- Meditite
- Shuckle
- Omanyte fossil
- Moon Stones

→ **Route 33**
- Zigzagoon
- Spinda
- Seviper
- Aipom

→ **Goldenrod**
- Abra
- Luvdisc
- Castform
- Porygon

→ **Route 35**
- Farfetch'd
- Minun
- Ditto
- Yanma
- Corsola
- Delibird event

→ **National Park**
- Lickitung
- Tropius
- Volbeat
- Illumise
- Sun Stone

→ **Route 36**
- Tangela

→ **Whitney**
- PU Gym / Lv. 20 cap

→ **Static Sudowoodo**
- NU transition

---

# Implementation checklist

- [ ] Add Mt. Moon 1F encounter table.
- [ ] Add Mt. Moon B1F/B2F encounter table.
- [ ] Place Helix Fossil in Mt. Moon.
- [ ] Ensure Devon can revive Omanyte during PU.
- [ ] Place at least two PU-accessible Moon Stones in Mt. Moon.
- [ ] Add Route 33 grass table.
- [ ] Add Route 33 Headbutt table.
- [ ] Remove Pineco from any non-Ilex encounter tables.
- [ ] Add Goldenrod Game Corner prizes: Abra, Luvdisc, Castform, Porygon.
- [ ] Add Route 35 grass table.
- [ ] Add Route 35 Headbutt table.
- [ ] Add Route 35 Old Rod table with Corsola.
- [ ] Replace / adapt the Route 35 mail event with Delibird.
- [ ] Add National Park normal table.
- [ ] Add National Park Bug-Catching Contest table.
- [ ] Make Bug-Catching Contest accessible without real-world weekday dependency.
- [ ] Award Sun Stone for first place.
- [ ] Add National Park Headbutt table.
- [ ] Add Route 36 grass table.
- [ ] Add Route 36 Headbutt table.
- [ ] Do not add Unown for PU coverage.
- [ ] Gate the Route 36 Sudowoodo trigger behind Whitney.
- [ ] Make Sudowoodo catchable at Lv. 20.
- [ ] Running from Sudowoodo leaves the obstruction in place.
- [ ] Catching or defeating Sudowoodo permanently clears the obstruction.
- [ ] Implement the PU evolution-level reductions.
- [ ] Implement the tier-safe Shedinja behavior.
