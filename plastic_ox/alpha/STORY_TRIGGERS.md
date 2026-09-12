# Story Triggers & Dialogue — Plastic Ox Alpha

Builds: `gPlasticOxTriggersEnabled` (u8, src/plastic_ox.c new file; declared in
include/plastic_ox.h). Set 1 in `CB2_InitPlasticOxDemo` path when compiled with
`PLASTIC_OX_BUILD_TRIGGERS` (Makefile: `make PLASTIC_OX_BUILD=triggers` →
`pokeemerald-triggers.gba`, define via CFLAGS). Default build = 0.

When 0 (walkable):
- `src/trainer_see.c`: early-return before any LOS check.
- `src/wild_encounter.c`: early-return before encounter roll.
- Trigger-build-only NPCs (guards, story objects) hidden at new game by setting
  their FLAG_POX_HIDE_* flags inside the same init branch.

Every coord_event script begins:
```asm
Special_PoxGate::
	specialvar VAR_RESULT, PoxTriggersEnabled
	goto_if_eq VAR_RESULT, FALSE, <skip_label>
	<story logic>
<skip_label>:
	release
	end
```
(Helper macro `poxgate <label>` may be added to asm/macros/event.inc to collapse
the first three lines.)

## Flag scheme

`FLAG_POX_STORY_<BEAT>` — one per beat, set when completed. Badges native.

## Beats (town-by-town test order)

| # | Town/Map | Beat | Test assertion (headless) |
|---|---|---|---|
| 0 | Pallet bedroom | Mom heals; exit blocked until starter | walk blocked w/o flag; after event R29 guard gone |
| 1 | Oak's Lab | Oak/Elm/Birch introduction; choose a level-5 Treecko, Squirtle, or Cyndaquil from the three balls; Pokédex assignment and five Poké Balls | species, six 31 IVs, cancellation, no duplicate gifts, physical ball interaction and revisit |
| 2 | Cherrygrove | Guide Gent tour dialogue (convergence flavor) + running shoes remark | flags/text |
| 3 | Ilex Forest | Farfetch'd-style side quest simplified: lost researcher NPC → escort dialogue → FLAG_POX_STORY_ILEX; gate opens Rustboro road | flag set |
| 4 | Rustboro Gym | Roxanne LC-tier battle (trainers.party entry) → BADGE01 | battle occurs, badge flag set |
| 5 | Mt. Moon | Rocket I: 2 grunts + "that isn't one of ours" scientist; fossil NPC; FLAG_POX_STORY_MTMOON after grunts beaten | grunts hidden after |
| 6 | Goldenrod | Bill's family: mother/sister dialogue + Eevee gift #1 (`givemon SPECIES_EEVEE,5`) once; Whitney gym → BADGE02 | eevee in party/PC, badge |
| 7 | National Park | Bug-catcher flavor NPCs; optional item | traversal only |
| 8 | Ecruteak | Burned Tower cutscene (Morty dialogue, brief anomaly text), Kimono troupe optional battle → Eevee gift #2; Morty gym → BADGE03 | badges/gifts |
| 9 | Weather Institute | Scientist explains boundaries still moving; one trainer; FLAG_POX_STORY_WEATHER | flag |
| 10 | Fortree | Winona gym → BADGE04 | badge |
| 11 | Sea Cottage | Note + Eevee gift #3; caretaker line about Bill being away | gift |
| 12 | Lavender/Pokémon Tower | Rocket II: grunts on floors; Fuji rescue dialogue; Fuji house → Eevee gift #4 + points to Cinnabar | flags |
| 13 | Cinnabar | Blaine gym open immediately → BADGE05 + Mansion Key item; Mansion: archives sign chain + static Entei encounter (optional); FLAG_POX_STORY_MANSION | badge+key |
| 14 | Whirl Islands | Traversal + rare item | traversal |
| 15 | Mossdeep | Tate&Liza double battle → BADGE06; Space Center researcher Eevee gift #5 + "traffic converges on Saffron" | badge+gift |
| 16 | Saffron | Open order: Dojo Bruno → BADGE07; Silph: Rocket III grunts → Giovanni → system shutdown scene FLAG_POX_STORY_SILPH; route gates to Blackthorn need BOTH | both flags gate R26 NPC |
| 17 | Blackthorn | Clair → BADGE08 | badge |
| 18 | Victory Road | strong trainers | traversal/battles |
| 19 | League | Wallace→Steven→Lance→Blue sequential rooms → Champion Bill reveal script + battle TRAINER_PLASTIC_OX_BILL | hall of fame flow |

## Trainer parties

Author in `src/data/trainers.party` (Showdown format; IDs appended in
`include/constants/opponents.h` as TRAINER_PLASTIC_OX_*). Tier-flavored teams:
Roxanne LC (unevolved lvl5-ish), Whitney PU, Morty NU, Winona RU, Blaine UU,
Tate&Liza UUBL doubles, Bruno OU, Clair OU, Rockets themed, E4 canonical-ish,
Bill: Eeveelution-led balanced OU team.

## Dialogue voice rules

- Grounded Gen1-3 tone; no fourth wall, no exposition dumps.
- Locals remark casually on impossible geography ("A Johto coast off Kanto? My
  grandfather would have fainted.").
- Bill never named near technology/mystery; family lines domestic & warm;
  Kimono/Eevee texture without explanation.
- Rocket: annoyed criminals → curious investigators → power-hungry (3 stages).
- Each rewritten NPC keeps the SPIRIT of its hns/original line but references the
  merged region or current story beat.

## Pallet opening implementation

The story ROM is `pokeemerald-triggers.gba`. Build with:

```sh
make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM PLASTIC_OX_BUILD=triggers modern
```

`data/scripts/plastic_ox_pallet.inc` contains the authored lab dialogue and
starter flow. `build_story.py` includes it and maintains the lab placements.
Oak introduces the changed geography without revealing the central plot; Elm
and Birch introduce themselves and their research. The entrance scene runs
once, and each professor has dialogue before and after the choice. Elm uses
the existing scientist overworld sprite; Oak and Birch use their own sprites.
The left, middle and right balls contain Treecko, Squirtle and Cyndaquil.
Declining preserves the choice; a full party and PC does not consume it.
Once chosen, the three balls disappear and the northern starter gate opens.
Oak supplies five Poké Balls once, with retry dialogue if the pocket is full.
The Pokédex supports species from all three regions. Mom provides directions
before selection and healing afterward; Daisy provides local travel advice.

All Pokémon IV writes in gameplay are fixed at 31 in `SetBoxMonData`, covering
random generation, individual overrides and packed trainer IVs. This applies
across Plastic Ox builds. Battle-test fixtures retain control over their IVs.
Existing save data is not migrated by this change.

Validation:

```sh
python3 plastic_ox/alpha/build_story.py --check
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_story.py starters
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_story.py gifts
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_story.py ivs
```

### Pallet and Oldale opening fixes

On the first lab visit, the player walks up the center aisle to Oak at (6, 6) before the professors introduce themselves. Elm gives all 50 reusable TMs and the Move Compendium after starter selection; players who already chose a starter can collect them by speaking to Elm. The reusable Key Item first selects a Pokémon, then teaches any compatible level-up move regardless of its current level, along with Egg and tutor moves. The gift skips items already owned and can be retried if a pocket is full. Oldale’s mart employee explains the shop and gives a Potion in place, without an escort walk.
