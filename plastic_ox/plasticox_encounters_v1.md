# Plastic Ox Encounter & Evolution Progression v1

## Purpose

This document defines the Pokémon encounter, evolution, level-cap, and evolution-item progression for Plastic Ox.

The progression is organized around competitive tiers:

1. **Gym 1 — LC**
2. **Gym 2 — PU**
3. **Gym 3 — NU**
4. **Gym 4 — RU**
5. **Gym 5 — UU**
6. **Gym 6 — UUBL**
7. **Gym 7 — OU**
8. **Gym 8 — OU**

The design goal is to make each badge unlock a meaningful increase in team-building power while minimizing dependence on direct encounters for evolved Pokémon.

---

# Core Rules

## Tier Progression

| Game Stage | Included Competitive Buckets | Level Cap |
|---|---|---:|
| Gym 1 | LC | **13** |
| Gym 2 | NFE + ZU + ZUBL + PU | **20** |
| Gym 3 | PUBL + NU | **30** |
| Gym 4 | NUBL + RU | **36** |
| Gym 5 | RUBL + UU | **42** |
| Gym 6 | UUBL | **50** |
| Gym 7 | OU + `(OU)` | **55** |
| Gym 8 | OU | **60** |

## Evolution Gating

A Pokémon may evolve only when:

1. Its normal evolution condition is satisfied, **and**
2. The tier of the resulting Pokémon has been unlocked.

If the normal evolution level is higher than the level cap for the tier where the evolved Pokémon becomes legal, the evolution level is lowered to that tier's level cap.

If the normal evolution level is lower than the tier where the evolved Pokémon becomes legal, the normal level is retained. The tier gate simply prevents evolution until that stage is unlocked.

### Example

- Dratini is available in LC.
- Dragonair is legal in PU.
- Dratini normally evolves at level 30.
- PU has a cap of 20.
- Therefore:

**Dratini → Dragonair: level 30 → level 20**

By contrast:

- Abra is usable before UUBL.
- Kadabra is not legal until UUBL.
- Abra still has its normal low evolution level internally.
- The evolution is simply blocked until UUBL becomes legal.

---

# Special OU-Only Family Overrides

The following families are unavailable entirely until OU, regardless of the lower-tier legality of their unevolved forms:

- **Magikarp → Gyarados**
- **Feebas → Milotic**
- **Diglett → Dugtrio**
- **Shroomish → Breloom**

These are explicit progression overrides.

---

# Overall Release Distribution

| Tier | New Pokémon Species | New Encounter / Evolutionary Lines | Evolution-Derived Species | Cumulative Species |
|---|---:|---:|---:|---:|
| **LC** | **98** | **98** | 0 | 98 |
| **PU** | **100** | **44** | **56** | 198 |
| **NU** | **32** | **10** | **22** | 230 |
| **RU** | **27** | **5** | **22** | 257 |
| **UU** | **40** | **10** | **30** | 297 |
| **UUBL** | **41** | **8** | **33** | 338 |
| **OU** | **36** | **16** | **20** | 374 |
| **Gym 8 OU** | 0 by tier | 0 | 0 | 374 |

The remaining 12 Gen 1–3 Pokémon are treated as Ubers and are outside normal badge progression:

- Mewtwo
- Mew
- Wynaut
- Wobbuffet
- Lugia
- Ho-Oh
- Latias
- Latios
- Kyogre
- Groudon
- Rayquaza
- Deoxys

---

# Gym 1 — LC

**Level cap: 13**

**98 species / 98 new encounter lines**

All species at this tier are encounter roots.

## Released Pokémon

Bulbasaur, Charmander, Squirtle, Caterpie, Weedle, Pidgey, Rattata, Spearow, Ekans, Pichu, Sandshrew, Nidoran♀, Nidoran♂, Cleffa, Vulpix, Igglybuff, Zubat, Oddish, Paras, Venonat, Meowth, Psyduck, Mankey, Growlithe, Poliwag, Machop, Bellsprout, Geodude, Slowpoke, Seel, Grimer, Shellder, Onix, Krabby, Exeggcute, Tyrogue, Horsea, Goldeen, Staryu, Smoochum, Magby, Eevee, Kabuto, Dratini, Chikorita, Cyndaquil, Totodile, Sentret, Hoothoot, Ledyba, Spinarak, Togepi, Natu, Mareep, Azurill, Hoppip, Sunkern, Wooper, Snubbull, Teddiursa, Slugma, Swinub, Remoraid, Phanpy, Larvitar, Treecko, Torchic, Mudkip, Poochyena, Wurmple, Lotad, Seedot, Taillow, Wingull, Ralts, Surskit, Slakoth, Nincada, Whismur, Makuhita, Skitty, Aron, Electrike, Gulpin, Carvanha, Wailmer, Numel, Spoink, Cacnea, Swablu, Barboach, Corphish, Baltoy, Shuppet, Snorunt, Spheal, Bagon, Beldum.

## Evolution Changes

None.

Low-level evolutions that would normally occur during LC remain blocked if their evolved form is not legal yet.

## Evolution Items

None.

## Explicitly Excluded Until OU

- Magikarp
- Feebas
- Diglett
- Shroomish

---

# Gym 2 — PU

**Level cap: 20**

**100 new species / 44 new encounter lines / 56 evolution-derived species**

## Released Pokémon

Ivysaur, Charmeleon, Wartortle, Metapod, Butterfree, Kakuna, Beedrill, Pidgeotto, Arbok, Nidorina, Nidorino, Clefairy, Jigglypuff, Wigglytuff, Gloom, Parasect, Poliwhirl, Abra, Weepinbell, Tentacool, Graveler, Ponyta, Magnemite, Farfetch'd, Doduo, Gastly, Drowzee, Kingler, Voltorb, Cubone, Lickitung, Koffing, Rhyhorn, Tangela, Seadra, Seaking, Elekid, Ditto, Porygon, Omanyte, Dragonair, Bayleef, Quilava, Croconaw, Furret, Noctowl, Ledian, Ariados, Chinchou, Togetic, Flaaffy, Marill, Skiploom, Aipom, Sunflora, Yanma, Unown, Pineco, Shuckle, Magcargo, Corsola, Delibird, Houndour, Grovyle, Combusken, Marshtomp, Mightyena, Zigzagoon, Silcoon, Beautifly, Cascoon, Dustox, Lombre, Nuzleaf, Kirlia, Masquerain, Shedinja, Loudred, Nosepass, Delcatty, Mawile, Lairon, Meditite, Minun, Volbeat, Illumise, Swalot, Spinda, Trapinch, Vibrava, Seviper, Lileep, Anorith, Castform, Duskull, Tropius, Sealeo, Clamperl, Luvdisc, Shelgon.

## New Encounter Lines

Abra, Tentacool, Ponyta, Magnemite, Farfetch'd, Doduo, Gastly, Drowzee, Voltorb, Cubone, Lickitung, Koffing, Rhyhorn, Tangela, Elekid, Ditto, Porygon, Omanyte, Chinchou, Aipom, Yanma, Unown, Pineco, Shuckle, Corsola, Delibird, Houndour, Zigzagoon, Nosepass, Mawile, Meditite, Minun, Volbeat, Illumise, Spinda, Trapinch, Seviper, Lileep, Anorith, Castform, Duskull, Tropius, Clamperl, Luvdisc.

## Downward Evolution-Level Changes

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

**18 downward level changes**

## Evolution Items Released

- **Moon Stone**
  - Wigglytuff
  - Delcatty
- **Sun Stone**
  - Sunflora

Higher-tier evolutions using these items remain blocked by the tier system.

---

# Gym 3 — NU

**Level cap: 30**

**32 new species / 10 new encounter lines / 22 evolution-derived species**

## Released Pokémon

Pidgeot, Raticate, Pikachu, Golbat, Bellossom, Venomoth, Machoke, Dewgong, Haunter, Hitmonchan, Flareon, Sudowoodo, Murkrow, Dunsparce, Piloswine, Octillery, Pupitar, Pelipper, Vigoroth, Sableye, Plusle, Roselia, Wailord, Torkoal, Cacturne, Whiscash, Crawdaunt, Kecleon, Chimecho, Huntail, Relicanth, Metang.

## New Encounter Lines

Sudowoodo, Murkrow, Dunsparce, Sableye, Plusle, Roselia, Torkoal, Kecleon, Chimecho, Relicanth.

## Downward Evolution-Level Changes

| Evolution | Vanilla | Plastic Ox |
|---|---:|---:|
| Pidgeotto → Pidgeot | 36 | **30** |
| Venonat → Venomoth | 31 | **30** |
| Seel → Dewgong | 34 | **30** |
| Swinub → Piloswine | 33 | **30** |
| Wailmer → Wailord | 40 | **30** |
| Cacnea → Cacturne | 32 | **30** |

**6 downward level changes**

## Evolution Items Released

- **Fire Stone**
  - Flareon
- **Deep Sea Tooth**
  - Huntail

Previously available:

- **Sun Stone**
  - Bellossom

### Notable Family Progression

**Pichu → Pikachu → Raichu**

- Pichu: LC
- Pikachu: NU
- Raichu: RU

---

# Gym 4 — RU

**Level cap: 36**

**27 new species / 5 new encounter lines / 22 evolution-derived species**

## Released Pokémon

Raichu, Clefable, Ninetales, Persian, Primeape, Poliwrath, Politoed, Victreebel, Rapidash, Hypno, Mr. Mime, Magmar, Kabutops, Meganium, Xatu, Azumarill, Sneasel, Mantine, Stantler, Shiftry, Exploud, Aggron, Sharpedo, Camerupt, Banette, Absol, Glalie.

## New Encounter Lines

Mr. Mime, Sneasel, Mantine, Stantler, Absol.

## Downward Evolution-Level Changes

| Evolution | Vanilla | Plastic Ox |
|---|---:|---:|
| Ponyta → Rapidash | 40 | **36** |
| Kabuto → Kabutops | 40 | **36** |
| Loudred → Exploud | 40 | **36** |
| Lairon → Aggron | 42 | **36** |
| Shuppet → Banette | 37 | **36** |
| Snorunt → Glalie | 42 | **36** |

**6 downward level changes**

## Evolution Items Released

- **Thunder Stone**
  - Raichu
- **Water Stone**
  - Poliwrath
- **Leaf Stone**
  - Victreebel
  - Shiftry
- **King's Rock**
  - Politoed

Previously available items additionally enable:

- Moon Stone → Clefable
- Fire Stone → Ninetales

---

# Gym 5 — UU

**Level cap: 42**

**40 new species / 10 new encounter lines / 30 evolution-derived species**

## Released Pokémon

Blastoise, Fearow, Sandslash, Nidoqueen, Nidoking, Vileplume, Golduck, Arcanine, Tentacruel, Golem, Slowking, Muk, Electrode, Hitmonlee, Hitmontop, Kangaskhan, Scyther, Electabuzz, Pinsir, Lapras, Omastar, Feraligatr, Lanturn, Ampharos, Jumpluff, Quagsire, Misdreavus, Girafarig, Gligar, Granbull, Qwilfish, Ninjask, Manectric, Grumpig, Altaria, Lunatone, Solrock, Cradily, Walrein, Gorebyss.

## New Encounter Lines

Kangaskhan, Scyther, Pinsir, Lapras, Misdreavus, Girafarig, Gligar, Qwilfish, Lunatone, Solrock.

## Downward Evolution-Level Changes

| Evolution | Vanilla | Plastic Ox |
|---|---:|---:|
| Sealeo → Walrein | 44 | **42** |

**1 downward level change**

## Evolution Items Released

- **Linking Cord**
  - Golem
- **Deep Sea Scale**
  - Gorebyss

Previously available items additionally enable:

- Fire Stone → Arcanine
- Moon Stone → Nidoqueen
- Moon Stone → Nidoking
- Leaf Stone → Vileplume
- King's Rock → Slowking

---

# Gym 6 — UUBL

**Level cap: 50**

**41 new species / 8 new encounter lines / 33 evolution-derived species**

## Released Pokémon

Venusaur, Crobat, Kadabra, Alakazam, Machamp, Slowbro, Dodrio, Steelix, Exeggutor, Marowak, Weezing, Rhydon, Chansey, Kingdra, Scizor, Jynx, Tauros, Vaporeon, Espeon, Umbreon, Articuno, Dragonite, Typhlosion, Ursaring, Houndoom, Donphan, Smeargle, Miltank, Entei, Sceptile, Blaziken, Linoone, Ludicolo, Swellow, Gardevoir, Slaking, Hariyama, Zangoose, Armaldo, Dusclops, Regirock.

## New Encounter Lines

Chansey, Tauros, Articuno, Smeargle, Miltank, Entei, Zangoose, Regirock.

## Downward Evolution-Level Changes

| Evolution | Vanilla | Plastic Ox |
|---|---:|---:|
| Dragonair → Dragonite | 55 | **50** |

**1 downward level change**

## Evolution Items Released

- **Metal Coat**
  - Steelix
  - Scizor
- **Dragon Scale**
  - Kingdra

Previously available items additionally enable:

- Linking Cord → Alakazam
- Linking Cord → Machamp
- Water Stone → Vaporeon
- Water Stone → Ludicolo
- Leaf Stone → Exeggutor

Friendship evolutions that were tier-blocked are now permitted where applicable, including Crobat, Espeon, and Umbreon.

---

# Gym 7 — OU

**Level cap: 55**

**36 new species / 16 new encounter lines / 20 evolution-derived species**

## Released Pokémon

Charizard, Diglett, Dugtrio, Magneton, Cloyster, Gengar, Blissey, Starmie, Magikarp, Gyarados, Jolteon, Porygon2, Aerodactyl, Snorlax, Zapdos, Moltres, Forretress, Heracross, Skarmory, Raikou, Suicune, Tyranitar, Celebi, Swampert, Shroomish, Breloom, Medicham, Flygon, Claydol, Feebas, Milotic, Salamence, Metagross, Regice, Registeel, Jirachi.

## New Encounter Lines

Diglett, Magikarp, Aerodactyl, Snorlax, Zapdos, Moltres, Heracross, Skarmory, Raikou, Suicune, Celebi, Shroomish, Feebas, Regice, Registeel, Jirachi.

## Special OU-Only Families

The following families become available for the first time here:

- Diglett → Dugtrio
- Magikarp → Gyarados
- Shroomish → Breloom
- Feebas → Milotic

## Downward Evolution-Level Changes

None required.

Important natural thresholds already fit the OU cap:

- Pupitar → Tyranitar: level 55
- Shelgon → Salamence: level 50
- Metang → Metagross: level 45
- Vibrava → Flygon: level 45

## Evolution Items Released

- **Up-Grade**
  - Porygon2

Previously available items additionally enable:

- Thunder Stone → Jolteon
- Water Stone → Cloyster
- Water Stone → Starmie
- Linking Cord → Gengar

### Feebas → Milotic

Preferred implementation:

- Retain the Beauty-based evolution.
- Tier-gate Milotic until OU.

Optional alternative:

- Replace Beauty with a **Prism Scale**.
- If used, Prism Scale should be OU-only.

---

# Gym 8 — OU

**Level cap: 60**

No new competitive tier is unlocked.

Gym 8 is a harder OU boss encounter rather than a new legality stage.

OU Pokémon and evolutions should already be legal after Gym 6 / before Gym 7 so that investment in previously caught Pokémon pays off before the first OU Gym.

A second geographic wave of OU encounters may still be reserved for the Gym 7 → Gym 8 section, but this should be a map-distribution decision rather than an evolution-legality restriction.

---

# Special Evolution Handling

## Nincada / Shedinja / Ninjask

This family requires a custom exception because its competitive tiers split the normal evolution event:

- Nincada: LC
- Shedinja: PU
- Ninjask: UU

Normally, Shedinja is generated when Nincada evolves into Ninjask at level 20.

To preserve tier legality while avoiding direct Shedinja encounters:

### At PU

If a level-20+ Nincada levels up while:

- the player has an empty party slot, and
- the player has the required Poké Ball,

then:

- generate Shedinja,
- keep Nincada unchanged.

### At UU

Nincada becomes eligible to evolve normally into Ninjask.

This preserves both tier assignments without requiring Shedinja or Ninjask to be distributed as artificial direct encounters.

---

# Final Evolution Item Schedule

| Tier | Newly Released Evolution Tools |
|---|---|
| **LC** | None |
| **PU** | Moon Stone, Sun Stone |
| **NU** | Fire Stone, Deep Sea Tooth |
| **RU** | Thunder Stone, Water Stone, Leaf Stone, King's Rock |
| **UU** | Linking Cord, Deep Sea Scale |
| **UUBL** | Metal Coat, Dragon Scale |
| **OU** | Up-Grade; Prism Scale only if Beauty evolution is replaced |

## Item Safety Rule

Evolution items do **not** override tier legality.

For example:

- Water Stone may exist in RU for Poliwrath.
- Vaporeon remains blocked until UUBL.
- Starmie remains blocked until OU.

The tier of the resulting species always controls whether the evolution is currently legal.

---

# Summary of Required Level Changes

| Tier | Number of Downward Evolution-Level Changes |
|---|---:|
| PU | 18 |
| NU | 6 |
| RU | 6 |
| UU | 1 |
| UUBL | 1 |
| OU | 0 |
| **Total** | **32** |

## Full Change List

### PU — Cap 20

- Ekans → Arbok: 22 → **20**
- Oddish → Gloom: 21 → **20**
- Paras → Parasect: 24 → **20**
- Poliwag → Poliwhirl: 25 → **20**
- Bellsprout → Weepinbell: 21 → **20**
- Geodude → Graveler: 25 → **20**
- Krabby → Kingler: 28 → **20**
- Horsea → Seadra: 32 → **20**
- Goldeen → Seaking: 33 → **20**
- Dratini → Dragonair: 30 → **20**
- Spinarak → Ariados: 22 → **20**
- Slugma → Magcargo: 38 → **20**
- Surskit → Masquerain: 22 → **20**
- Aron → Lairon: 32 → **20**
- Gulpin → Swalot: 26 → **20**
- Trapinch → Vibrava: 35 → **20**
- Spheal → Sealeo: 32 → **20**
- Bagon → Shelgon: 30 → **20**

### NU — Cap 30

- Pidgeotto → Pidgeot: 36 → **30**
- Venonat → Venomoth: 31 → **30**
- Seel → Dewgong: 34 → **30**
- Swinub → Piloswine: 33 → **30**
- Wailmer → Wailord: 40 → **30**
- Cacnea → Cacturne: 32 → **30**

### RU — Cap 36

- Ponyta → Rapidash: 40 → **36**
- Kabuto → Kabutops: 40 → **36**
- Loudred → Exploud: 40 → **36**
- Lairon → Aggron: 42 → **36**
- Shuppet → Banette: 37 → **36**
- Snorunt → Glalie: 42 → **36**

### UU — Cap 42

- Sealeo → Walrein: 44 → **42**

### UUBL — Cap 50

- Dragonair → Dragonite: 55 → **50**

---

# Design Outcome

The revised tier ladder creates a more gradual competitive-power curve:

**LC → PU → NU → RU → UU → UUBL → OU → OU**

The key structural advantage is that later badge rewards rely heavily on the player's existing roster evolving rather than forcing repeated replacement with newly encountered stronger Pokémon.

In particular:

- PU introduces 100 newly legal species, but only 44 new encounter lines.
- NU introduces 32 species, but only 10 new encounter lines.
- RU introduces 27 species, but only 5 new encounter lines.
- UU introduces 40 species, but only 10 new encounter lines.
- UUBL introduces 41 species, but only 8 new encounter lines.

This gives the middle and late game a strong sense of payoff for raising Pokémon caught earlier in the adventure.
