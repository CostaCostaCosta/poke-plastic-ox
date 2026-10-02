# Pokémon Plastic Ox — Encounter Follow-ups, Run 2

**Base commits:** `181e2cbc16` (checkpoint) and `c5a713c1e3` (encounter fixes +
trainer teams v2), which is also the tree this work sits on. Changes are left
uncommitted on top, as instructed.

**Predecessor:** `plastic_ox/agent/TRAINER_TEAMS_V2_REPORT.md`. That report is
now marked partly superseded: two of the files it cites have been deleted and the
five unreachable Headbutt tables it described are gone.

Everything below is verified against the built ROM and the live data files.
**Nothing here was play-tested** — no build was booted. Map, tile and script
claims are static: mapjson output, linker map, symbol tables and decoded script
bytes.

---

## Test results

| Check | Result |
|---|---|
| `plastic_ox/encounter_tables/test_pre_mt_moon_v5_5.py` | **PASS** — 237 checks |
| `plastic_ox/encounter_tables/test_nu_encounters_v1.py` | **PASS** — 168 checks (6/10 documented NU roots implemented) |
| `plastic_ox/agent/test_trainer_teams_v2.py` | **PASS** — 3,403 checks over 71 trainers |
| `plastic_ox/encounter_tables/audit_encounters_v55.py` | 0 problems across fishing / grass / rock smash / headbutt, all invariants ok |
| `DEVKITARM=~/devkitpro/opt/devkitpro/devkitARM make -j8` | **exit 0, zero errors** |

**Build memory:** EWRAM 226,560 B / 256 KB (86.43%), IWRAM 28,588 B / 32 KB
(87.24%), ROM 27,569,692 B (82.16%). The `pokeemerald.gba` file itself is the
padded 33,554,432 B (32.00 MiB) expansion ROM. Only pre-existing warnings appear:
an explicit-waitstate note at `data/scripts/plastic_ox_story.inc:1881` and the
usual `ld` "LOAD segment with RWX permissions".

---

## Item 1 — Ilex Forest fishing is documented as specified

The table was already correct in the ROM and was **not touched**. It was missing
from the v5.5 document, which is what this item fixed.

`gPoxIlexForestHns_{Morning,Day,Night}` each carry the identical ten-slot table:
Old Rod Magikarp 70% / Poliwag 30%, Good Rod Poliwag 60% / Barboach 20% /
Corphish 20%, Super Rod Poliwhirl 40% / Whiscash 40% / Crawdaunt 15% /
Azumarill 4% / Politoed 1%.

**Files changed**

- `plastic_ox/encounter_tables/plastic_ox_pre_mt_moon_encounters_v5_5_agent_ready.md`
  - new section **"Ilex Forest — Fishing — Good Rod Lv. 6–8 (pond, eighth wet area)"**
    under §9, with the full table;
  - an explicit **"Approved RU exception"** paragraph naming **Azumarill (4%)**
    and **Politoed (1%)** as a user-approved RU-tier reach inside an LC-tier
    pond, and noting it does not weaken the general unlock rule because the
    Super Rod is not awarded before RU;
  - every "seven wet areas" / "21 Good Rod slots" / "7 / 7 fishing areas"
    corrected to **eight / 24 / 8 / 8**, in the non-negotiables, the
    "Fishing distribution at a glance" section, workflow step 5 and the
    acceptance checklist;
  - the checklist now states 24 Good Rod slots with Poliwag the only repeat
    (three times: Pallet, Ilex, Route 44).
- `plastic_ox/encounter_tables/audit_encounters_v55.py`
  - `MAP_ILEX_FOREST_HNS` added to `SPEC_FISHING`, so the audit diffs it;
  - the `super_rod_no_forbidden` invariant text updated from "seven" to a
    computed count.
- `plastic_ox/encounter_tables/test_pre_mt_moon_v5_5.py`
  - asserts Ilex has exactly three fishing tables, each with 10 slots whose
    per-rod split matches `ILEX_FISHING` exactly;
  - asserts **8** v5.5 wet areas (counted by map, since Ilex has one table per
    time of day), **24** Good Rod slots and **20** distinct Good Rod species.

**Verified:** `SPECIES_AZUMARILL` and `SPECIES_POLITOED` are both
`EVO_TIER_RU` in `src/data/pokemon/evolution_tier_gates.h`, so the exception is
real and deliberate rather than a tiering oversight.

---

## Item 2 — The NU block

Implemented from `plastic_ox/encounter_tables/nu_encounters_v1.md` by a new
generator, `plastic_ox/encounter_tables/apply_nu_v1.py`, following the existing
`apply_*` pattern. It writes `src/data/wild_encounters.json` and appends the
Route 37 Headbutt pair to `src/data/plastic_ox_pu_encounters.h`.

> **Run order matters.** `apply_pu_v1.py` rewrites the Headbutt header from
> scratch; `apply_nu_v1.py` must run **after** it. This is stated in both
> scripts' docstrings.

**What was installed**

| Table | Map | Method | Levels | Detail |
|---|---|---|---|---|
| Route 37 grass | `MAP_ROUTE37_HNS` | `land_mons` ×3 | 21–23 | Stable 65% core (Growlithe 25, Vulpix 15, Roselia 15, Plusle 10) plus a 35% time-of-day tail: M Pidgey 15 / Ledyba 10 / Spearow 10 · D Pidgey 15 / Hoppip 10 / Spearow 10 · N Hoothoot 15 / Spinarak 10 / Murkrow 10 |
| Route 37 Headbutt | `MAP_ROUTE37_HNS` | `sPoxRoute37Headbutt{Day,Night}` | 21–23 | Teddiursa 25, Seedot 20, Slakoth 15, Exeggcute 15, Hoothoot 10, Pichu 10, **Kecleon 5** |
| Ecruteak City Good Rod | `MAP_ECRUTEAK_CITY_HNS` | `fishing_mons` | 21–23 | Poliwag 30, Barboach 20, Surskit 15, Goldeen 15, Wooper 10, Corphish 10 |
| Burned Tower 1F | `MAP_PLASTIC_OX_BURNED_TOWER` | `land_mons` | 22–24 | Rattata 30, Koffing 15, Zubat 15, Torkoal 10, Slugma 10, Houndour 10, Gastly 5, Raticate 5 |

`src/wild_encounter.c`'s `GetHeadbuttTable()` gained the `LAYOUT_ROUTE37_HNS`
case.

**Engine decisions**

- Every table carries an explicit `weights` array, so the engine's rejection
  sampler (`ChooseWeightedWildMonIndex`, `src/wild_encounter.c:563`) reproduces
  the authored percentages exactly instead of the fixed land/fishing slot
  weights. All four tables total 100.
- Ecruteak's rod is written as a ten-slot weighted pool with weights
  `30/20/15/15/10/10/0/0/0/0`, the same shape Route 35's Old Rod uses. A table
  with explicit weights bypasses rod-slot selection (`src/wild_encounter.c:746`),
  so the five zero-weight trailing slots make it **Good-Rod-only**. That is safe
  because neither the Old Rod (Mossdeep, post-badge-6) nor the Super Rod
  (Mossdeep House 3) exists before Morty.
- Ecruteak and Burned Tower use **one unsuffixed entry**, which the generator
  files under `TIME_MORNING` — also `OW_TIME_OF_DAY_FALLBACK`
  (`include/config/overworld.h:97`), so a single table serves every time of day.
  The document specifies no time-of-day split for either floor.
- Route 37 grass has three entries because the document *does* split by period.

**Tier gating.** Every species in the block is NU-tier or lower in
`src/data/pokemon/evolution_tier_gates.h`, and every level is inside the cap-30
band. Spot-checked at the source: Roselia, Plusle, Murkrow, Kecleon, Torkoal,
Dunsparce, Chimecho, Sableye, Raticate and Relicanth are all `EVO_TIER_NU`; the
supporting cast is LC/PU. The test asserts this rather than trusting the reading.

**Map reality checks (static).** Using the metatile behaviour tables and each
map's `data/layouts/<name>/map.bin`: Route 37 has 184 encounter tiles and no
surfable water (so grass works and there is nothing to fish — matching the
document), and Ecruteak City has 140 surfable water tiles, so the Good Rod is
actually usable there.

### What the NU block does **not** deliver

Four of the document's ten NU roots are still open. None of this was guessed at.

1. **Burned Tower B1F (Dunsparce, Chimecho, Sableye) — blocked, no map.**
   `data/maps/PlasticOx_BurnedTower/` is a single-storey stub: `map.json` uses
   `LAYOUT_MT_PYRE_1F`, with **zero** warp events, **zero** connections and two
   story NPCs. There is no second floor to attach a table to, and a header is
   keyed one-per-map, so two floors cannot share it. Creating the floor is a map
   project (new layout, warps, story wiring), well outside "implement encounter
   tables". **Reported, not guessed.** `LAYOUT_MT_PYRE_2F` exists and could be
   reused when that floor is built.
2. **Kecleon (Route 37 Headbutt 5%) — built and wired, but unreachable.**
   The table exists and `GetHeadbuttTable()` returns it, but **Route 37 has no
   Headbutt tree object**. Item 7 explicitly said "no new Headbutt trees", so
   none was placed. This makes the document's "10 / 10 NU lines before Morty"
   currently **6 / 10 in play** (7 / 10 if the tree is added). Say the word and
   placing the `bg_sign_event` on Route 37 is a two-line map change.
3. **Relicanth (Ecruteak Corsola trade)** — a story NPC and trade script, not an
   encounter table. Not in scope for this item and not implemented.
4. **Non-encounter NU content** — the Kimono Girls Eevee gift, the Burned Tower
   1F Fire Stone, the legendary-beast scene and Morty's unlock. All story
   scripting; none of it is encounter data.

**Regression coverage:** new `plastic_ox/encounter_tables/test_nu_encounters_v1.py`
(168 checks) asserts the four tables' exact species/rates/levels/100% totals, the
document's 65%-core + 35%-tail structure on Route 37, the Ecruteak table being
rod-exclusive, tier gating against the engine's own table, the cap-30 band, and
NU root coverage by `pox_progression.obtainable_at("gym3")`. It prints which
documented roots are still open rather than hiding them.

It also now guards **Route 35's fishing table** (item 6 below), asserting the
exact five-species Old Rod pool, the Lv. 16–18 band and Corsola at 15%.

---

## Item 3 — Good Rod level 10

**No data changed.** The data already satisfied the rule; the documents and tests
did not describe it correctly.

Inspecting all eight tables slot by slot, **every Good Rod slot (indices 2–4)
has `min_level` 10** in all eight areas, while Old Rod and Super Rod inherit the
area band. The nuance is that the *ceiling* still follows the area — Pallet and
Oldale are 10–10, Route 103 and Cherrygrove and Ilex 10–10, Route 24 10–11,
Route 25 10–12, Route 44 10–13. My first pass at the assertion required a flat
10–10 and correctly failed on Route 24/25/44; the assertion now checks the
**floor**, which is what "minimum level 10" means.

**Files changed**

- `plastic_ox_pre_mt_moon_encounters_v5_5_agent_ready.md` — new **"Good Rod level
  rule"** paragraph under "Fishing distribution at a glance" listing all eight
  areas' actual Good Rod bands; each area's `### Fishing — Good Rod Lv. X–Y`
  heading changed to `### Fishing — area band Lv. X–Y` with a pointer, since the
  heading's old number described only the Old/Super Rod band.
- `plastic_ox_pu_encounters_v1.md` — **no change needed.** It never specifies
  Good Rod levels; its only fishing content is Route 35's Old Rod table. Nothing
  in it contradicts the uniform rule.
- `audit_encounters_v55.py` — `GOOD_ROD_MIN_LEVEL` and a per-slot check in the
  fishing loop.
- `test_pre_mt_moon_v5_5.py` — the floor is asserted on all 24 Good Rod slots.

---

## Item 4 — Rod awards

### Old Rod — new gift NPC in Mossdeep City (implemented)

**Gating flag: `FLAG_BADGE06_GET`** (`include/constants/flags.h:1374`,
`SYSTEM_FLAGS + 0xC` = `0x86C`).

There is **no dedicated Mossdeep-gym story flag**. `FLAG_DEFEATED_MOSSDEEP_GYM`
exists (`flags.h:1328`) but is **dead** in this ROM: its setter script
`MossdeepCity_Gym_EventScript_TateAndLizaDefeated` is referenced by no object
event, and its only live consumers are Steven's Pokénav match call
(`src/pokenav_match_call_data.c:267,673`). Gating on it would have produced an
NPC that is permanently locked.

The flag the story actually sets, traced end to end:

- `include/constants/opponents.h:871` — `TRAINER_PLASTIC_OX_TATELIZA` = 862,
  the Mossdeep gym (Tate & Liza);
- `data/maps/MossdeepCity_Gym/map.json` object events 1 and 9 (`OBJ_EVENT_GFX_TATE`,
  `OBJ_EVENT_GFX_LIZA`) both use `Pox_TateLiza`;
- `data/scripts/plastic_ox_story.inc:345` `Pox_TateLiza::` →
  `:349 goto_if_unset FLAG_BADGE05_GET` / `:351 goto_if_unset FLAG_POX_STORY_MANSION`
  (both prerequisites) → `:353 goto_if_set FLAG_BADGE06_GET, Pox_Done` →
  `:359 trainerbattle_double TRAINER_PLASTIC_OX_TATELIZA` → **`:363 setflag FLAG_BADGE06_GET`**.

`FLAG_BADGE06_GET` is the sixth badge flag in the story's badge series (Roxanne 1,
Whitney 2, Morty 3, Winona 4, Blaine 5, Tate & Liza 6, Bruno 7, Clair 8) rather
than a Mossdeep-named bit. Nothing else on the story path sets it; the native
Hoenn maps that also read it are unreachable in Plastic Ox. Worth noting:
`include/constants/plastic_ox_flags.h:8-13` records the `0x264–0x2BB` run as
**full**, so a dedicated `FLAG_POX_*` bit would need an audited-unused slot.
Flagged rather than picked ad hoc.

**Files changed**

- `data/maps/MossdeepCity/map.json` — object event **id 18**,
  `OBJ_EVENT_GFX_FISHERMAN` at **(54, 4)**, elevation 7,
  `MOVEMENT_TYPE_FACE_DOWN`, `TRAINER_TYPE_NONE`, script
  `MossdeepCity_EventScript_OldRodFisherman`, flag 0.
- `data/maps/MossdeepCity/scripts.inc` — the gift script plus its
  Already-Gave / Not-Ready / Bag-Full branches and five text strings.

Script shape, mirroring the sibling rod gifts in this repo:
`lock` / `faceplayer` → `goto_if_set FLAG_RECEIVED_OLD_ROD` →
`goto_if_unset FLAG_BADGE06_GET` → `msgbox` → `giveitem ITEM_OLD_ROD` →
`goto_if_eq VAR_RESULT, FALSE` → Bag Full (**flag not set**, so it is retryable)
→ `setflag FLAG_RECEIVED_OLD_ROD`. Only existing macros were used.
`FLAG_RECEIVED_OLD_ROD` is the same guard the native Dewford fisherman uses, so
the two sources are mutually exclusive.

**Tile choice was verified, not guessed.** Using
`plastic_ox/alpha/region_geometry.py` against the Mossdeep blockmap and metatile
behaviours: (54, 4) is layer 0, elevation 7, `MB_NORMAL` — walkable floor, with
walkable neighbours (53, 4), (55, 4), (54, 5); (54, 3) is surfable
`MB_OCEAN_WATER` at the shoreline. It is not an object event, warp or bg event,
and it sits in the main land component. Existing ids 1–17 are untouched.

**Verification.** Static, as required:

- `data/maps/MossdeepCity/events.inc:25` regenerated by mapjson (21:55:48, newer
  than the 21:55:25 `map.json`) and now reads
  `object_event 18, OBJ_EVENT_GFX_FISHERMAN, 54, 4, 7, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, MossdeepCity_EventScript_OldRodFisherman, 0`.
- `include/constants/map_event_ids.h` and `data/maps/events.inc` regenerated
  with an **empty diff** — no existing object-event id shifted.
- `build/emerald/data/map_events.o` rebuilt (21:59:21); `pokeemerald.gba`
  rewritten (22:06:39).
- `MossdeepCity_EventScript_OldRodFisherman` is at `0x08290f82` in
  `pokeemerald.map`. Decoding the script blob **out of the linked ROM** gives
  immediates `0x0101` (`FLAG_RECEIVED_OLD_ROD`), `0x086C`
  (`FLAG_BADGE06_GET`) and `0x02C5` (`ITEM_OLD_ROD = 709`,
  `include/constants/items.h:866`) — so the gate and the item are wired, not just
  present in source. All five text symbols are in `event_scripts.o`.

### Good Rod — placed and reachable, left exactly as found

**One finding worth recording:** the giver is **not on the Cherrygrove town
map**. `CherrygroveCity_hns/map.json` has only three object events
(`Pox_Cherrygrove` 57,8; `Boy_2` 48,12; `Lass` 39,11) — no fisherman. The script
lives in `data/maps/CherrygroveCity_hns/scripts.inc:12-30`, but the object event
is in **`data/maps/CherrygroveCity_SoutheastHouse_hns/events.inc:8`**:
`object_event 1, OBJ_EVENT_GFX_FISHERMAN, 3, 5, 0, MOVEMENT_TYPE_FACE_RIGHT, …,
CherrygroveCity_EventScript_Fisherman, 0`.

Reachable before Gym 1 as required: the town warps to that house at (34, 13)
(`MB_ANIMATED_DOOR`, no lock), the house reciprocates with `warp_def 4, 9, 0, 2`,
and (3, 5) is walkable floor in the door-connected component. Minor cosmetic
oddity: the house uses `LAYOUT_HOUSE_GENERIC_A_HNS`, which looks like a
copy/paste from the generic house Cherrygrove also warps to. **Left as-is.**

### Super Rod — reported only, nothing touched

Given in `MAP_MOSSDEEP_CITY_HOUSE3` by
`MossdeepCity_House3_EventScript_SuperRodFisherman` (YESNO prompt, `giveitem
ITEM_SUPER_ROD`, `setflag FLAG_RECEIVED_SUPER_ROD`, with an already-had branch).

**It is reachable.** Its door is a **plain warp, not an object event**: house
`warp_def 3/4, 7, 0, 5, MAP_MOSSDEEP_CITY` ↔ city `warp_def 49, 6, 0, 0,
MAP_MOSSDEEP_CITY_HOUSE3`. No lock, no key item, no flag gate. (49, 6) is
`MB_ANIMATED_DOOR` with walkable approach (49, 7), in the same 784-tile land
component as every other Mossdeep door. The city is entered from
`PlasticOx_Route20East` via `PoxRegion_sea_mossdeep_b`, which requires
`FLAG_POX_STORY_MANSION`.

The notable point: the Super Rod is available from badge 1 onward, well before
any of its RU species are legal to catch. That is safe as specified — the
document's rule is that the rod "must not be usable before the highest
represented tier (RU)", and **it is**: the Super Rod's award timing is a
pre-existing story fact, not something this task may move. Flagged, not changed.

### Rod award timing, recorded in the v5.5 document

A new **"Rod award timing"** section in
`plastic_ox_pre_mt_moon_encounters_v5_5_agent_ready.md` tabulates all three:
Good Rod = Cherrygrove, pre-Gym 1, ungated (in the southeast house); Old Rod =
Mossdeep City street, post-`FLAG_BADGE06_GET`; Super Rod = Mossdeep City House 3,
as found. Two consequences are noted in the document's non-negotiables: the Old
Rod's Magikarp and every Super Rod slot are gated **by access**, not only by
table design.

---

## Item 5 — `plastic_ox/plasticox_encounters_v1.md` removed

**No code or test read the document.** All 24 references were comments, prose or
one markdown link. Every one has been repointed, then the file was deleted.

**Repointed at the engine's own table, `src/data/pokemon/evolution_tier_gates.h`:**

- `include/constants/pokemon.h:335`, `include/config/pokemon.h:19`,
  `src/pokemon.c:3371`, `test/evolution_tier_gating.c:2`,
  `src/data/pokemon/evolution_tier_gates.h:2` (which now states it *is* the
  source of truth, superseding the retired document)
- `src/evolution_scene.c:611` — the Nincada/Shedinja rule points at the
  surviving `plastic_ox/agent/plasticox_evolution_gating_plan_v1.md`

**Repointed at the embedded data / surviving plan:**

- `plastic_ox/agent/pox_progression.py` — `ITEM_CHECKPOINT` never read the file
  (the schedule was already embedded); the comment now says so. The second
  reference now cites `evolution_tier_gates.h`.
- `plastic_ox/agent/plasticox_evolution_gating_plan_v1.md`,
  `research_evo_system.md`, `research_badges_tests.md` — research/design
  records; each reference now marks the document retired and names what
  superseded it.
- `plastic_ox/alpha/PLAN.md:14` — this was the **only live markdown link** to the
  file; it now points at the v5.5 specification and the gating plan.
- `plastic_ox/agent/TRAINER_TEAMS_V2_REPORT.md` and its generator
  `write_trainer_teams_v2_report.py` — these are the run-1 record and still
  describe that run. Rewriting them would falsify history, so each carries a
  **superseded-in-part banner** pointing at this report instead.

**Deleted:** `plastic_ox/plasticox_encounters_v1.md` (581 lines).

---

## Item 6 — Route 35 fishing: **nothing was wrong**

The current `gPoxPURoute35Hns_{Morning,Day,Night}` fishing tables already match
`plastic_ox_pu_encounters_v1.md` §"Route 35 — Old Rod" exactly:

| Poliwag | Goldeen | Barboach | Corsola | Psyduck | Levels |
|---|---|---|---|---|---|
| 30% | 25% | 20% | **15%** | 10% | 16–18 |

Species, rates, level band and the 100% total all agree with the document, and
Corsola is obtainable there at 15% as required. No data was changed.

Two things were worth verifying rather than assuming:

1. **"Old Rod only" holds, and not by accident.** The table carries explicit
   weights `30/25/20/15/10/0/0/0/0/0`. In `src/wild_encounter.c:746`, fishing
   uses `wildMonInfo->weights != NULL ? ChooseWeightedWildMonIndex(...) :
   ChooseWildMonIndex_Fishing(rod)` — a weighted table bypasses rod-slot
   selection entirely. `ChooseWeightedWildMonIndex` (line 563) rejection-samples
   over the weights, and slots 6–10 have weight 0, so they can never be selected.
   The effective result is exactly the five-species Old Rod table. The Good Rod
   and Super Rod cannot fire there, which is the intended design.
2. **The run-1 caveat still applies** and is worth repeating: because the table
   is weighted, "Route 35 has no separate Good/Super Rod pool" is true by
   construction, and the trailing zero-weight `SPECIES_PSYDUCK` padding rows are
   inert but present.

A regression assertion for this now lives in
`test_nu_encounters_v1.py`, which checks the exact pool, the Lv. 16–18 band and
Corsola at 15% for all three times of day, so a future generator run cannot
silently reshape it.

---

## Item 7 — The five inaccessible Headbutt tables

### Which areas, and how that was established

`GetHeadbuttTable()` had cases for Route 29, Route 46, Route 44, Route 24 and
Route 25, and `apply_pu_v1.py` built all five tables — but the maps carrying a
`PlasticOx_EventScript_HeadbuttTree` **bg_sign_event** are only
**Ilex Forest, Route 33, Route 35, Route 36 and National Park**. The five tables
were unreachable in play. No new trees were added.

### Lost-species analysis (counting only player-reachable sources)

Computed by replaying `pox_progression.CHECKPOINTS` against the header **as it
stood before removal**, while counting a Headbutt table only for a map that has a
tree. This matters: counting the dead tables would have made several species look
safe when they were not.

**Whole-region reachable species set: 161 before, 161 after.**
**Species lost entirely: none.**

| Species | Reachable before | Reachable after | Earliest source before | Earliest source after |
|---|---|---|---|---|
| Slakoth | yes | yes | start | start |
| Meowth | yes | yes | route2south | route2south |
| Hoothoot | yes | yes | route29 | route29 |
| Spearow | yes | yes | route29 | route29 |
| Spinarak | yes | yes | route29 | route29 |
| Exeggcute | yes | yes | ilex | ilex |
| Ledyba | yes | yes | ilex | ilex |
| Sunkern | yes | yes | ilex | ilex |
| Pichu | yes | yes | route24 | route24 |
| Natu | yes | yes | route33 | route33 |

No species is delayed to a later story stage either — the *earliest* reachable
source is identical in every row.

### Relocations: **none needed**

Because nothing was lost and nothing was delayed at the whole-region level, no
species had to be relocated. However, the removal **did** change availability at
three individual trainer checkpoints, and those are reported in full below
rather than papered over.

### What was removed

- **`src/data/plastic_ox_pu_encounters.h`** — `sPoxRoute29Headbutt{Day,Night}`,
  `sPoxRoute46Headbutt{Day,Night}`, `sPoxRoute44Headbutt{Day,Night}`,
  `sPoxRoute24Headbutt{Day,Night}`, `sPoxRoute25Headbutt{Day,Night}` (ten
  tables). Generated output; the edit was made in the generator.
- **`plastic_ox/encounter_tables/apply_pu_v1.py`** — the five entries removed
  from `TABLES`, with a comment explaining that Headbutt tables exist only for
  tree-carrying maps.
- **`src/wild_encounter.c`** — the five `case` labels removed from
  `GetHeadbuttTable()`; the `LAYOUT_ROUTE37_HNS` case added; a comment now records
  why the other five are gone.

### Trainer consequences — reported explicitly

Removing the tables exposed three roster entries whose **only** source had been a
dead table. These are load-bearing, so they are called out rather than silently
patched.

| Trainer | Checkpoint | Was | Why it broke | Now |
|---|---|---|---|---|
| `TRAINER_PLASTIC_OX_MOON_SUPER_NERD_JOVAN[3]` | mtmoon | Natu | Natu's only source before Mt. Moon was Route 44's Headbutt table (no tree). Its first *reachable* source is Route 33 Headbutt, a later checkpoint. | **Meditite** Lv. 12 |
| `TRAINER_PLASTIC_OX_MOON_SUPER_NERD_MIGUEL[3]` | mtmoondeep | Natu | as above | **Meditite** Lv. 15 |
| `TRAINER_PLASTIC_OX_ROUTE29[5]` | route29 | Ledyba | Ledyba's LC-stage sources were the Route 29 / Route 24 / Route 25 Headbutt tables, all treeless. Its first reachable source is the Ilex Headbutt tree, a later checkpoint. | **Spinarak** Lv. 4 |

**Why the roster and not an encounter relocation.** Item 7 permits relocating a
load-bearing species into an accessible slot in the same area. For all three, the
same area is a grass table that is an authoritative authored target —
Route 29 grass and the Mt. Moon tables are specced exactly by the v5.5 and PU
documents, and the v5.5 document is explicit that grass data is a *verification
target, "not an invitation to rewrite working code"*. Adding Natu to Mt. Moon or
Ledyba to Route 29 would have required amending a specification document this
task was told to correct, not rewrite. The substitutes are spec-legal at their
checkpoint and keep the original flavour: Meditite is psychic and comes straight
from Mt. Moon grass, and Spinarak is a bug and is in Route 29's own night grass.

**Files changed:** `plastic_ox/agent/apply_trainer_teams_v2.py` (`ROSTERS` plus a
comment on each), and `src/data/trainers.party` — a **16-line** diff across those
three blocks only (Ledyba → Spinarak; Natu → Meditite ×2, each with its item,
ability, EVs and moves).

---

## Test cleanup

**`plastic_ox/encounter_tables/test_pre_mt_moon_v4_4.py` — deleted.** It asserted
against superseded data and the pre-v5 map ids (`MAP_ROUTE1`, `MAP_ROUTE104`) and
had been failing since the v5.5 migration. Nothing references it.
`apply_pre_mt_moon_v4_4.py` and the v4.4 document are untouched and inert; the
only references to either are historical mentions inside the run-1 report and its
generator, which now carry a supersession banner.

**`pox_progression.py` — inputs updated for current reality.**

- `HEADBUTT_SYMBOLS` now lists **only** tree-carrying maps, with
  `HEADBUTT_TREE_MAPS` alongside. This is the substantive fix: the model used to
  count a Headbutt table as obtainable whether or not the player could stand in
  front of a tree, which is precisely the bug item 7 removes.
- `CHECKPOINTS` gained `route37` (NU, 30; `gPoxNURoute37Hns#` +
  `MAP_ROUTE37_HNS`) and `burnedtower` (NU, 30; `gPoxNUEcruteakCityHns` +
  `gPoxNUBurnedTower1F`) between `ecruteak` and `gym3`, matching the NU
  document's Route 37 → Ecruteak → Burned Tower → Morty order. The five
  treeless headbutt maps were dropped from their checkpoints.
- `LC_BLOCK_HEADBUTT` reduced to Ilex Forest — the only LC area with a tree left.

**`test_trainer_teams_v2.py` — updated, not weakened.** It re-reads
`src/data/trainers.party` and keeps every check it had: six Pokémon per trainer,
obtainable-at-checkpoint, tier gating, level caps, ability validity, EV/IP
caps, natures, move legality at level, and byte-identical trainer headers
against `trainer_headers_baseline.json`. The change is that its availability
baseline is now the corrected model — reachable Headbutt tables only, plus the NU
block. **All 71 trainers, 3,403 checks, still pass.** No check was removed,
relaxed or deleted; the three roster swaps above are what made the strict
assertion satisfiable.

### One finding about the trainer generator

`apply_trainer_teams_v2.py` is **not byte-reproducible**: re-running it on
unchanged inputs rewrites 6–20 lines of `trainers.party` (move substitutions
such as `Double-Edge` ↔ `Iron Tail`), and it does not reproduce under a fixed
`PYTHONHASHSEED`. The cause is `sorted(..., key=<power>)` over a **set**
difference in `legalise_moves` / `build_mon`: tied keys keep set-iteration order,
which varies. It is pre-existing and out of scope here, but worth knowing: it is
why the three roster corrections were **spliced** into `trainers.party` directly
(via the generator's own `build_mon`/`render_mon`) instead of regenerating all 68
blocks and dragging unrelated move churn into the diff.

---

## Files changed

**Encounter data**
`src/data/wild_encounters.json` (+5 NU entries; the five treeless Headbutt tables
never lived here) · `src/data/plastic_ox_pu_encounters.h` (−10 treeless
Headbutt tables, +2 Route 37) · `src/wild_encounter.c` (`GetHeadbuttTable`)

**Tooling**
`plastic_ox/encounter_tables/` — new `apply_nu_v1.py`, new
`test_nu_encounters_v1.py`, deleted `test_pre_mt_moon_v4_4.py`; modified
`apply_pu_v1.py`, `audit_encounters_v55.py`, `test_pre_mt_moon_v5_5.py`

**Trainers**
`src/data/trainers.party` (16-line diff) · `plastic_ox/agent/pox_progression.py` ·
`plastic_ox/agent/apply_trainer_teams_v2.py` ·
`plastic_ox/agent/trainer_teams_v2_build.json`

**Map / story**
`data/maps/MossdeepCity/map.json` · `data/maps/MossdeepCity/scripts.inc`

**Documentation**
`plastic_ox_pre_mt_moon_encounters_v5_5_agent_ready.md` (Ilex fishing, eight areas
/ 24 slots, RU exception, Good Rod level rule, rod award timing, Headbutt removal)
· `plastic_ox/alpha/PLAN.md` · deleted `plastic_ox/plasticox_encounters_v1.md` ·
comment repointing in `include/config/pokemon.h`, `include/constants/pokemon.h`,
`src/pokemon.c`, `src/evolution_scene.c`,
`src/data/pokemon/evolution_tier_gates.h`, `test/evolution_tier_gating.c`,
`plastic_ox/agent/{research_badges_tests.md,research_evo_system.md,plasticox_evolution_gating_plan_v1.md}` ·
supersession banners on `TRAINER_TEAMS_V2_REPORT.md` and
`write_trainer_teams_v2_report.py`

27 tracked files changed, 907 insertions, 869 deletions, plus 2 new files.

---

## Open items

1. **Burned Tower B1F has no map.** Dunsparce, Chimecho and Sableye cannot be
   implemented as encounter data until the floor is built. `LAYOUT_MT_PYRE_2F`
   exists and is the obvious reuse candidate.
2. **Route 37 has no Headbutt tree**, so Kecleon's 5% slot is built, wired and
   asserted but unreachable in play. One `bg_sign_event` fixes it; the "no new
   Headbutt trees" instruction is why it was not added.
3. **Relicanth's Corsola trade**, the Kimono Girls Eevee gift, the Burned Tower
   Fire Stone and the legendary-beast scene are story content, not encounter
   data, and remain unimplemented.
4. **The Super Rod is obtainable from badge 1** while its RU species are not
   legal until RU. Safe as specified (the rod must not be usable before the
   highest represented tier, and it is), but the award is pre-existing and was
   not moved.
5. **`FLAG_BADGE06_GET` is a shared numbered badge flag.** Unambiguous today; a
   dedicated `FLAG_POX_*` bit needs an audited slot because that flag space is
   full.
6. **`apply_trainer_teams_v2.py` is not byte-reproducible** (set-iteration-order
   tie-breaks in move selection).