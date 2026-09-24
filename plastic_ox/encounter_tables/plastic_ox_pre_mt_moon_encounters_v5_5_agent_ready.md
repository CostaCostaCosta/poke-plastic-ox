# Pokémon Plastic Ox — Pre–Mt. Moon Encounters v5.5

**Status:** implementation-ready, standalone target specification. The implementation agent starts with the **v5 encounter implementation, including the already-migrated Route 2**. This document contains every encounter table required for this block; **do not require v5.1, v5.2, v5.3, v4.6, or an earlier encounter document**. Percentages below are conditional on an encounter occurring, not bite or Rock Smash success chances.

## Implementation handoff: apply v5 → v5.5

**Baseline and precedence.** The codebase already contains the v5 encounters and Route 2's replacement of the former Route 1, Route 31, and upper Route 104 areas. The tables in **this document** are the authoritative end state, including the revised Super Rod tables. Treat the following delta as the work to perform; treat the remaining tables as regression expectations. Where the checked-out code differs unexpectedly from v5, inspect the actual implementation and report the discrepancy rather than assuming old map identifiers or overwriting unrelated work. Historical version labels farther down describe where a table originated, **not** instructions to obtain another file.

### Required code changes (the complete delta from v5)

| Area / method | v5 currently | v5.5 required | Action |
|---|---|---|---|
| Oldale Town / Good Rod slot 3 | Wailmer, 20% | **Corphish, 20%** | Change species only. |
| Route 103 / Good Rod slot 3 | Corphish, 20% | **Wailmer, 20%** | Change species only. |
| Route 25 / Good Rod slot 3 | Clamperl, 20% | **Dratini, 20%** | Change species only. |
| Route 44 / Good Rod slot 2 | Dratini, 20% | **Clamperl, 20%** | Change species only. |
| Dark Cave Entrance 1 / ordinary walking | Nine rows/species per time period in v5 | **Five distinct species per period, exact table below** | Replace the entire ordinary walking table for morning/day/night; do not patch only one time period. |
| Sea Cottage fossil proof / documentation or event text, if present | Teddiursa described as 5% morning | **Teddiursa 10% morning** | Correct stale rate; preserve the show-not-surrender fossil interaction. |
| Seven wet areas / Super Rod | 19 UU/UUBL/OU or OU-only-family entries in v5 | **19 specific substitutions listed below** | Change only these Super Rod species; preserve each slot’s weight and all Old/Good Rod entries except the four Good Rod swaps above. |


**Super Rod — complete slot-by-slot delta from v5 (19 substitutions):**

| Area | Slot / rate | v5 species (remove) | v5.5 species (use) | Replacement tier |
|---|---|---|---|---|
| Pallet Town | 4 / 4% | Starmie | **Seadra** | PU |
| Pallet Town | 5 / 1% | Gyarados | **Corsola** | PU |
| Oldale Town | 1 / 40% | Quagsire | **Crawdaunt** | NU |
| Oldale Town | 5 / 1% | Feebas | **Politoed** | RU |
| Route 103 | 1 / 40% | Tentacruel | **Tentacool** | LC |
| Route 103 | 5 / 1% | Gorebyss | **Wailord** | NU |
| Cherrygrove City | 1 / 40% | Slowbro | **Slowpoke** | LC |
| Cherrygrove City | 3 / 15% | Cloyster | **Seadra** | PU |
| Cherrygrove City | 4 / 4% | Slowking | **Octillery** | NU |
| Cherrygrove City | 5 / 1% | Kingdra | **Corsola** | PU |
| Route 24 | 1 / 40% | Golduck | **Poliwhirl** | PU |
| Route 24 | 2 / 40% | Lanturn | **Seaking** | PU |
| Route 24 | 3 / 15% | Starmie | **Kingler** | PU |
| Route 24 | 5 / 1% | Gyarados | **Politoed** | RU |
| Route 25 | 1 / 40% | Walrein | **Sealeo** | PU |
| Route 25 | 3 / 15% | Kingdra | **Dragonair** | PU |
| Route 25 | 5 / 1% | Lapras | **Corsola** | PU |
| Route 44 | 4 / 4% | Kingdra | **Octillery** | NU |
| Route 44 | 5 / 1% | Dragonite | **Azumarill** | RU |

These replacements are restricted to **LC/PU/NU/RU** per the Plastic Ox release roster. Replace the species **in the same slot**; do not reorder slots or retune rates. The 1% entries are intentional. No Super Rod table may contain UU, UUBL, OU, Ubers, or an OU-only-family Pokémon (including Feebas or Magikarp). Magikarp in the **Old Rod** is a separate approved OU-gated exception.

**Dark Cave ordinary walking — the complete replacement (levels 5–8):**

| Rate | Morning | Day | Night |
|---|---|---|---|
| 35% | Zubat | Zubat | Zubat |
| 30% | Baltoy | Baltoy | Baltoy |
| 20% | Swinub | Swinub | Snorunt |
| 10% | Teddiursa | Makuhita | Duskull |
| 5% | Larvitar | Larvitar | Larvitar |

Remove **Onix, Geodude, Aron, and Whismur** from Dark Cave's *walking* tables. Do **not** remove them globally: Aron/Geodude/Onix remain in this cave's **already-specified Rock Smash table**, and Whismur remains in Route 103 grass at 10%. In particular, do not accidentally leave nighttime Swinub in the new walking table: the 20% slot is Snorunt at night. The Dark Cave Rock Smash slots are **unchanged from v5**: Aron 60%, Rhyhorn 30%, Geodude 5%, Onix 4%, Onix 1% (Onix 5% effective).

### Explicitly out of scope: protect the existing Route 2 migration

- **Do not re-run a Route 2 migration, recreate Route 1/31/upper Route 104 maps or encounter tables, or transplant old map IDs.** Route 2 South and Route 2 North already exist, have independent grass encounters, and have **no fishing/water**. Do not change their geometry, entrances, encounters, or progression for this update. Preserve Route 2 North's Dark Cave Entrance 1 connection, Ralts 5% at all times, and Gastly 5% at night.
- Preserve Ilex Forest's exclusive Pineco 15% Headbutt encounter and the existing Headbutt tables. Preserve Route 44's shore-accessible fishing and Surf-locked grass. All other grass, **unchanged fishing slots**, Headbutt, Rock Smash, gift, trade, fossil, and progression data in this document are **verification targets**, not an invitation to rewrite working code.
- Keep the three fishing rod slot distributions fixed at **70/30**, **60/20/20**, and **40/40/15/4/1**. The four Good Rod changes are swaps **within Good Rod slots**; the 19 additional Super Rod changes replace species **within the same Super Rod slots**. Neither requires changes to weights, levels, rod unlocks, or any Old Rod entry. Keep Old Rod Magikarp 70% everywhere and OU-only Old Rod access. The Super Rod now contains species up to **RU** only; it must not bypass the RU unlock. Its award timing is **not** approved here: check existing timing, and report any mismatch without inventing or moving a story event.

### Implementation workflow and acceptance checks

1. Locate the codebase's actual map identifiers, generated encounter files, rod slot definitions, time-of-day dispatch, and Dark Cave Rock Smash behavior. Edit the source of truth (including a generator, if the repository uses one), rather than editing only generated output or assuming standard upstream file paths. Implement only the needed delta; keep all 15 areas listed below as the end-state specification.
2. Apply the four Good Rod swaps, apply all 19 Super Rod species substitutions, and replace Dark Cave's ordinary morning/day/night encounters. If the engine uses fixed weighted slots, compose its slots to yield the **exact aggregate percentages**; do not silently round to the nearest built-in rate. Retain Dark Cave's five Rock Smash slots and the separate encounter methods.
3. Inspect fossil proof dialogue/comments if they encode catch probabilities. Update Teddiursa's morning rate to 10% without altering the actual fossil reward requirements, Devon revival, or ownership of the shown Pokémon.
4. Assert each Dark Cave time-of-day walking table sums to 100%, has exactly five distinct species, matches its column above, and never includes Aron, Geodude, Onix, or Whismur. Confirm Swinub is 20% morning/day, Snorunt 20% night, Larvitar 5% all times, and Teddiursa 10% morning. Verify Rock Smash remains 60/30/5/4/1.
5. Assert Oldale / Route 103 / Route 25 / Route 44 Good Rod species and percentages match the four target rows. Check all **seven** wet-area Good Rod tables contain exactly 3 slots and every one of the seven Old/Super Rod tables matches its **updated** table below. Assert no forbidden-tier species or OU-only family appears in any Super Rod table. Check there are no fishing entries on Route 2 North/South and no revived obsolete Route 1/31/upper Route 104 entries.
6. Check the progression invariants: Good Rod and Rock Smash usable when the player reaches the LC areas, Old Rod cannot expose Magikarp before OU, Super Rod cannot expose RU species before RU is unlocked, and Route 24/25/44 bank access meets the explicit pre-Gym-1 dependency below. If access is not established, **report the blocker**; do not silently move encounters or redesign the map.
7. Run the repository's existing encounter-data validation/build or relevant tests. Report the changed files, verified slot totals, any pre-existing divergences, tests run/results, and unresolved access/rod-award questions. Do not claim the game was play-tested if only static data was checked.

---

## Non-negotiable progression rules

- LC cap is **13**. The **Good Rod is obtainable before Gym 1**. All LC-eligible aquatic roots from the v5 baseline appear in Good Rod tables (and not solely in later rods).
- **Old Rod is not awarded until OU progression has begun.** Its first slot is Magikarp 70% in every fishing area; second slot is location-specific 30%. This preserves the Magikarp/Gyarados family's OU-only override.
- Super Rod tables are **future-facing**, not LC encounter sources. All five slots per area are restricted to species released by **RU or earlier**. The rod must not be usable before the highest represented tier (RU), unless encounter eligibility is independently gated to prevent higher-tier catches. **Do not add, relocate, or promise a Super Rod award event**; preserve existing acquisition timing and flag any mismatch to the implementer. Feebas, Magikarp, and all UU/UUBL/OU/Ubers species are excluded from Super Rod everywhere.
- Rod distributions use the Generation III encounter slots exactly: Old **70/30**, Good **60/20/20**, Super **40/40/15/4/1**. Do not create extra slots or average species percentages across a rod.
- **Route 2 South and Route 2 North have separate grass tables but NO water / fishing tables**. Route 2 replaces Route 1, Route 31, and Route 104-top; removed Route 104 fishing/Headbutt and Route 31 fishing/Headbutt tables do not survive as separate map encounters.
- **Dark Cave has Rock Smash**, in addition to ordinary cave encounters. Aron, Geodude, and Onix are Rock Smash-only *within Dark Cave* (other routes may still feature them). Its standard five Rock Smash slots are **60/30/5/4/1**; the last two slots both use Onix to make its effective rate 5%. Standard Dark Cave encounters have five distinct species at any time of day. Whismur remains available on Route 103, not in Dark Cave.
- Pineco exists exclusively at **Ilex Forest Headbutt (15%)**. No other encounter method or map can produce Pineco.
- Route 44 grass is **Surf-gated** and unavailable in this block. Route 44 fishing is shore-accessible before Surf, as specified in the v5 baseline.
- **Important access dependency:** Route 24, Route 25, and the Route 44 fishing bank must be reachable before Gym 1 *if their Good Rod species are required to be catchable for that Gym*. If those areas are instead visited only after Gym 1, the progression graph needs an additional earlier water map or some fish need alternate earlier acquisitions; slot math alone cannot solve map gating.
- The other special-only acquisitions remain special-only: nine starter species, Eevee, Kabuto, Anorith, Lileep, and Beldum. Fossils are rewarded by **Bill's grandfather at Sea Cottage** for showing the required Pokémon and revived at **Devon**. The proof Pokémon are never surrendered.

**Tier validation for Super Rod.** The allowed Super Rod species in this document and their release tiers are: LC — Tentacool, Slowpoke; PU — Kingler, Seaking, Poliwhirl, Seadra, Corsola, Dragonair, Sealeo; NU — Crawdaunt, Whiscash, Octillery, Wailord, Huntail, Dewgong; RU — Politoed, Sharpedo, Azumarill. This list is included so the coding agent does **not** need a separate tier document. A later tier retcon should be reported rather than silently changing this specification.

## Fishing distribution at a glance

Each area has its own full three-rod table below. Super Rod tables use LC–RU species only, not high-tier evolved forms. The Good Rod places **20 distinct aquatic LC roots into 21 slots**, repeating only Poliwag. Moving formerly 5% species such as Wailmer and Dratini into a fixed 20% slot increases their *conditional catch probability*; do not describe either as 5% any longer. Use encounter frequency or area access, not invented 5% slots, if more rarity is desired.

## 1. Pallet Town

### Fishing — Good Rod Lv. 2–5

| Rod | Slot 1 | Slot 2 | Slot 3 | Slot 4 | Slot 5 |
|---|---|---|---|---|---|
| Old Rod (post-OU) | Magikarp · 70% | Krabby · 30% | — | — | — |
| Good Rod (LC) | Poliwag · 60% | Goldeen · 20% | Krabby · 20% | — | — |
| Super Rod (future-facing) | Kingler · 40% | Seaking · 40% | Poliwhirl · 15% | Seadra · 4% | Corsola · 1% |



## 2. Route 101

### Grass — Lv. 2–4

| Rate | Pokémon |
|---|---|
| 30% | Wurmple |
| 25% | Poochyena |
| 15% | Taillow |
| 10% | Lotad |
| 10% | Seedot |
| 5% | Surskit |
| 5% | Slakoth |



## 3. Oldale Town

### Fishing — Good Rod Lv. 3–5

| Rod | Slot 1 | Slot 2 | Slot 3 | Slot 4 | Slot 5 |
|---|---|---|---|---|---|
| Old Rod (post-OU) | Magikarp · 70% | Wooper · 30% | — | — | — |
| Good Rod (LC) | Wooper · 60% | Barboach · 20% | Corphish · 20% | — | — |
| Super Rod (future-facing) | Crawdaunt · 40% | Whiscash · 40% | Octillery · 15% | Wailord · 4% | Politoed · 1% |



## 4. Route 103

### Grass — Lv. 3–5

| Rate | Morning | Day | Night |
|---|---|---|---|
| 25% | Wingull | Wingull | Wingull |
| 20% | Lotad | Lotad | Lotad |
| 15% | Poochyena | Poochyena | Poochyena |
| 10% | Seedot | Seedot | Seedot |
| 10% | Whismur | Whismur | Whismur |
| 10% | Electrike | Electrike | Electrike |
| 5% | Cacnea | Cacnea | Cacnea |
| 5% | Gulpin | Gulpin | Grimer |



### Fishing — Good Rod Lv. 3–6

| Rod | Slot 1 | Slot 2 | Slot 3 | Slot 4 | Slot 5 |
|---|---|---|---|---|---|
| Old Rod (post-OU) | Magikarp · 70% | Tentacool · 30% | — | — | — |
| Good Rod (LC) | Tentacool · 60% | Carvanha · 20% | Wailmer · 20% | — | — |
| Super Rod (future-facing) | Tentacool · 40% | Sharpedo · 40% | Crawdaunt · 15% | Huntail · 4% | Wailord · 1% |



## 5. Route 29

### Grass — Lv. 3–5

| Rate | Morning | Day | Night |
|---|---|---|---|
| 25% | Sentret | Sentret | Sentret |
| 15% | Pidgey | Pidgey | Hoothoot |
| 15% | Rattata | Rattata | Rattata |
| 10% | Nidoran♀ | Nidoran♀ | Nidoran♀ |
| 10% | Nidoran♂ | Nidoran♂ | Nidoran♂ |
| 10% | Mareep | Mareep | Mareep |
| 5% | Spearow | Spearow | Spearow |
| 5% | Hoppip | Hoppip | Spinarak |
| 5% | Ponyta | Ponyta | Houndour |



### Headbutt (already in v5) — Lv. 3–5

| Rate | Morning | Day | Night |
|---|---|---|---|
| 25% | Slakoth | Slakoth | Slakoth |
| 15% | Spearow | Spearow | Spearow |
| 15% | Ledyba | Ledyba | Spinarak |
| 15% | Natu | Natu | Natu |
| 15% | Exeggcute | Exeggcute | Exeggcute |
| 15% | Hoothoot | Hoothoot | Hoothoot |



## 6. Route 46

### Grass — Lv. 4–6

| Rate | Morning | Day | Night |
|---|---|---|---|
| 25% | Geodude | Geodude | Geodude |
| 15% | Rattata | Rattata | Zubat |
| 15% | Machop | Machop | Machop |
| 10% | Sandshrew | Sandshrew | Sandshrew |
| 10% | Rhyhorn | Rhyhorn | Rhyhorn |
| 10% | Cubone | Cubone | Cubone |
| 5% | Numel | Numel | Numel |
| 5% | Bagon | Bagon | Bagon |
| 5% | Phanpy | Slugma | Slugma |



### Headbutt (already in v5) — Lv. 4–6

| Rate | Pokémon |
|---|---|
| 35% | Natu |
| 20% | Exeggcute |
| 15% | Spearow |
| 15% | Hoothoot |
| 15% | Slakoth |



**Fossil proof:** Phanpy is 5% in the morning only. Cubone is 10% at all times.

## 7. Cherrygrove City

### Fishing — Good Rod Lv. 4–6

| Rod | Slot 1 | Slot 2 | Slot 3 | Slot 4 | Slot 5 |
|---|---|---|---|---|---|
| Old Rod (post-OU) | Magikarp · 70% | Slowpoke · 30% | — | — | — |
| Good Rod (LC) | Slowpoke · 60% | Seel · 20% | Shellder · 20% | — | — |
| Super Rod (future-facing) | Slowpoke · 40% | Dewgong · 40% | Seadra · 15% | Octillery · 4% | Corsola · 1% |



## 8. Route 2 South (before Ilex Forest)

### Grass (already in v5) — Lv. 4–6

| Rate | Morning | Day | Night |
|---|---|---|---|
| 25% | Mankey | Mankey | Mankey |
| 20% | Spearow | Spearow | Drowzee |
| 15% | Meowth | Meowth | Meowth |
| 10% | Ekans | Ekans | Ekans |
| 10% | Rattata | Rattata | Rattata |
| 10% | Pidgey | Pidgey | Pidgey |
| 5% | Growlithe | Growlithe | Vulpix |
| 5% | Vulpix | Vulpix | Vulpix |



**No water, fishing, or separate Headbutt table.** The former Route 1 table is removed, not added as an extra encounter area.

## 9. Ilex Forest

### Grass (already in v5) — Lv. 6–8

| Rate | Morning | Day | Night |
|---|---|---|---|
| 25% | Paras | Paras | Paras |
| 20% | Venonat | Venonat | Venonat |
| 15% | Weedle | Weedle | Weedle |
| 10% | Caterpie | Caterpie | Spinarak |
| 10% | Oddish | Oddish | Oddish |
| 10% | Nincada | Nincada | Shuppet |
| 5% | Lotad | Lotad | Lotad |
| 5% | Seedot | Seedot | Seedot |



### Headbutt — ONLY Pineco source (already in v5) — Lv. 6–8

| Rate | Morning | Day | Night |
|---|---|---|---|
| 25% | Ledyba | Ledyba | Spinarak |
| 15% | Pineco | Pineco | Pineco |
| 15% | Exeggcute | Exeggcute | Exeggcute |
| 15% | Sunkern | Sunkern | Sunkern |
| 10% | Caterpie | Caterpie | Hoothoot |
| 10% | Weedle | Weedle | Weedle |
| 10% | Paras | Paras | Paras |



## 10. Route 2 North (after Ilex Forest)

### Grass (already in v5) — Lv. 7–10

| Rate | Morning | Day | Night |
|---|---|---|---|
| 20% | Taillow | Taillow | Hoothoot |
| 15% | Skitty | Skitty | Skitty |
| 15% | Electrike | Electrike | Electrike |
| 10% | Bellsprout | Bellsprout | Bellsprout |
| 10% | Hoppip | Hoppip | Hoppip |
| 5% | Ralts | Ralts | Ralts |
| 5% | Magnemite | Magnemite | Magnemite |
| 5% | Spoink | Spoink | Spoink |
| 5% | Trapinch | Trapinch | Koffing |
| 5% | Voltorb | Voltorb | Gastly |
| 5% | Gulpin | Gulpin | Gulpin |



**No water/fishing.** The former Diglett’s Cave entrance becomes **Dark Cave Entrance 1**. Ralts is 5% at all times; Gastly is 5% at night. No surviving Route 31 or Route 104-top wild tables.

## 11. Dark Cave — Entrance 1 accessible before Gym 1

### Cave — Lv. 5–8 (simplified: five species per time period)

| Rate | Morning | Day | Night |
|---|---|---|---|
| 35% | Zubat | Zubat | Zubat |
| 30% | Baltoy | Baltoy | Baltoy |
| 20% | Swinub | Swinub | Snorunt |
| 10% | Teddiursa | Makuhita | Duskull |
| 5% | Larvitar | Larvitar | Larvitar |

**Encounter-method separation:** Aron, Geodude, and Onix are obtained through Rock Smash in Dark Cave; Whismur is already catchable in Route 103 grass (10%). Swinub is available morning/day; Snorunt is night-only. Rock Smash must be usable before Gym 1, and Teddiursa is now 10% in the morning for Bill's grandfather's Lileep fossil request.



### Rock Smash — Lv. 5–8 (new)

| Slot | Rate | Pokémon |
|---|---|---|
| 1 | 60% | Aron |
| 2 | 30% | Rhyhorn |
| 3 | 5% | Geodude |
| 4 | 4% | Onix |
| 5 | 1% | Onix |

**Effective distinct-species rates:** Aron 60%, Rhyhorn 30%, Geodude 5%, Onix 5%. The 4% and 1% slots are deliberate duplicates, not new 1%-rare LC roots. Rock Smash must be usable at the cave entrance during LC. Teddiursa is 10% *morning-only in the normal cave table*; Larvitar is 5% at all times.

## 12. Rustboro City

No ordinary wild Pokémon in this city plan. **Devon Beldum in-game trade** remains separate from encounters; **Devon fossil revival** is retained. Ralts is on Route 2 North, not an obsolete standalone Route 104-top map.

## 13. Route 24

### Grass — Lv. 8–11

| Rate | Morning | Day | Night |
|---|---|---|---|
| 20% | Pichu | Pichu | Pichu |
| 15% | Cleffa | Cleffa | Cleffa |
| 10% | Igglybuff | Igglybuff | Igglybuff |
| 10% | Togepi | Togepi | Togepi |
| 10% | Tyrogue | Tyrogue | Tyrogue |
| 10% | Azurill | Azurill | Azurill |
| 10% | Mareep | Mareep | Mareep |
| 5% | Smoochum | Smoochum | Smoochum |
| 5% | Snubbull | Snubbull | Snubbull |
| 5% | Elekid | Elekid | Smoochum |



### Fishing — Good Rod Lv. 8–11

| Rod | Slot 1 | Slot 2 | Slot 3 | Slot 4 | Slot 5 |
|---|---|---|---|---|---|
| Old Rod (post-OU) | Magikarp · 70% | Psyduck · 30% | — | — | — |
| Good Rod (LC) | Psyduck · 60% | Chinchou · 20% | Staryu · 20% | — | — |
| Super Rod (future-facing) | Poliwhirl · 40% | Seaking · 40% | Kingler · 15% | Azumarill · 4% | Politoed · 1% |



### Headbutt — Lv. 8–11

| Rate | Pokémon |
|---|---|
| 25% | Pichu |
| 20% | Sunkern |
| 15% | Ledyba |
| 15% | Natu |
| 10% | Hoothoot |
| 10% | Exeggcute |
| 5% | Slakoth |



## 14. Route 25 / Sea Cottage branch

### Grass — Lv. 9–12

| Rate | Morning | Day | Night |
|---|---|---|---|
| 20% | Swablu | Swablu | Swablu |
| 15% | Magby | Magby | Magby |
| 15% | Meowth | Meowth | Meowth |
| 10% | Drowzee | Drowzee | Drowzee |
| 10% | Growlithe | Growlithe | Growlithe |
| 10% | Tyrogue | Tyrogue | Tyrogue |
| 5% | Smoochum | Smoochum | Smoochum |
| 5% | Doduo | Doduo | Igglybuff |
| 5% | Snubbull | Snubbull | Snubbull |
| 5% | Ponyta | Ponyta | Houndour |



### Fishing — Good Rod Lv. 9–12

| Rod | Slot 1 | Slot 2 | Slot 3 | Slot 4 | Slot 5 |
|---|---|---|---|---|---|
| Old Rod (post-OU) | Magikarp · 70% | Seel · 30% | — | — | — |
| Good Rod (LC) | Spheal · 60% | Horsea · 20% | Dratini · 20% | — | — |
| Super Rod (future-facing) | Sealeo · 40% | Seadra · 40% | Dragonair · 15% | Wailord · 4% | Corsola · 1% |



### Headbutt (already in v5) — Lv. 9–12

| Rate | Pokémon |
|---|---|
| 25% | Meowth |
| 15% | Pichu |
| 15% | Ledyba |
| 15% | Exeggcute |
| 15% | Spearow |
| 15% | Slakoth |



### Sea Cottage — Bill’s grandfather and fossils

| Show Pokémon (keep it) | Where to obtain | Fossil reward |
|---|---|---|
| Ralts | Route 2 North grass · 5% all times | Kabuto |
| Phanpy | Route 46 grass · 5% morning only | Anorith |
| Teddiursa | Dark Cave cave encounter · 10% morning only | Lileep |

Bill’s grandfather rewards the fossils when the player **shows** each Pokémon; he does not take it. Devon remains the fossil-revival location. Eevee and Beldum are never ordinary wild encounters.

## 15. Route 44 — accessible fishing bank; grass locked behind Surf

### Fishing — Good Rod Lv. 10–13

| Rod | Slot 1 | Slot 2 | Slot 3 | Slot 4 | Slot 5 |
|---|---|---|---|---|---|
| Old Rod (post-OU) | Magikarp · 70% | Poliwag · 30% | — | — | — |
| Good Rod (LC) | Remoraid · 60% | Clamperl · 20% | Poliwag · 20% | — | — |
| Super Rod (future-facing) | Seaking · 40% | Dewgong · 40% | Dragonair · 15% | Octillery · 4% | Azumarill · 1% |



Clamperl is the Route 44 Good Rod 20% slot; Dratini is now available from Route 25 Good Rod at 20%, and its evolution to Dragonair still obeys the PU tier gate. Route 44’s grass is not available before Surf.

## Validation and implementation checklist

- **103 / 103** expected ordinary-wild LC roots represented somewhere in the Good Rod / grass / Headbutt / cave / Rock Smash tables; **0 missing, 0 unexpected**. The design roster audit covers *species representation*, not actual in-game map accessibility or species tier legality beyond the established v5 roster.
- **20 / 20** former aquatic LC roots remain in Good Rod; **21 Good Rod slots across seven wet areas**. The sole duplicated aquatic species is Poliwag.
- **7 / 7 fishing areas** have two Old Rod slots (70/30), three Good Rod slots (60/20/20), and five Super Rod slots (40/40/15/4/1). All **19** formerly prohibited Super Rod occurrences were replaced; no UU, UUBL, OU, Uber, Magikarp, or Feebas remains in Super Rod. Magikarp appears in Old Rod slot 1 only (OU gated); Super Rod’s highest required unlock is RU.
- **1 / 1 Rock Smash tables** total 100% using 60/30/5/4/1. Effective minimum distinct-species rate remains 5%. Dark Cave ordinary walking encounters total 100% for morning, day, and night and expose five distinct species per period (down from nine); Swinub/Snorunt has the 20% slot, and Larvitar the 5% slot. Whismur persists on Route 103, while the three removed rocky species persist in Dark Cave Rock Smash.
- Route 2 North and South have **zero fishing/water entries**. Route 31, Route 1, and Route 104-top are removed rather than double-counted. Pineco appears in exactly **one** wild encounter table (Ilex Headbutt, 15%).
- Protect **day/night grass rules** and fossil proofs: Ralts 5% on Route 2 North; Phanpy 5% morning on Route 46; Teddiursa 10% morning in Dark Cave; Gastly 5% night on Route 2 North.
- **Engine detail:** default Gen III-style `rock_smash_mons` has five entries weighted 60/30/5/4/1; `fishing_mons` has ten slots partitioned 2/3/5 among the three rods. The grass/Headbutt percentages specified in this document are retained *as design rates*; where an engine’s default land-slot weights cannot represent one of these tables, use the project’s custom land encounter configuration instead of silently changing the intended rates.

### Optional technical reference

[Pret pokeemerald wild encounter data](https://github.com/pret/pokeemerald/blob/master/src/data/wild_encounters.json) illustrates the baseline rod-slot partition and Rock Smash weights. **Inspect this project’s actual encounter configuration rather than copying upstream data paths or assuming an unmodified engine.**

**Editorial note:** Old Rod and Super Rod level ranges have intentionally not been invented. Their *species and slot probabilities* are fully specified; set their encounter levels when the actual acquisition timing and late-game level curve are finalized. Good Rod and Rock Smash inherit LC-area levels above.
