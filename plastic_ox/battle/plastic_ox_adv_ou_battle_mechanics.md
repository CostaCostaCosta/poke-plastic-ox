# Plastic Ox — Pokémon Showdown ADV OU Battle Configuration

## Purpose

Configure `pokeemerald-expansion` so that **battle behavior follows Pokémon Showdown / Smogon ADV OU (Generation 3 OU)** while preserving the modern `pokeemerald-expansion` codebase for overworld systems, scripting, content, UI, progression, encounter design, and other non-battle features.

This is **not** a request to revert the repository to vanilla `pokeemerald`.

This is also **not** a request to independently reimplement or exhaustively validate obscure Generation 3 cartridge edge cases. The project will trust the existing `pokeemerald` / `pokeemerald-expansion` battle-engine implementations where they already provide Generation 3 behavior.

The coding goal is therefore:

> Use `pokeemerald-expansion` as the engine, configure all battle-relevant generation switches to Generation 3, disable post-Gen-3 battle mechanics, and globally enforce the current Smogon ADV OU competitive clauses/rules that matter to gameplay.

---

# 1. Source of truth

Use the following precedence when making decisions:

1. **Current Pokémon Showdown / Smogon ADV OU ruleset**
2. Existing `pokeemerald-expansion` Generation 3 configuration options
3. Existing `pokeemerald` / decomp battle-engine behavior
4. Custom code only when necessary to enforce ADV OU rules that expansion does not already expose

Primary references:

- Smogon ADV OU:
  - https://www.smogon.com/dex/rs/formats/ou/
- Pokémon Showdown rulesets:
  - https://github.com/smogon/pokemon-showdown/blob/master/data/rulesets.ts
- `pokeemerald-expansion` battle config:
  - https://github.com/rh-hideout/pokeemerald-expansion/blob/master/include/config/battle.h
- `pokeemerald-expansion` Pokémon config:
  - https://github.com/rh-hideout/pokeemerald-expansion/blob/master/include/config/pokemon.h
- `pokeemerald-expansion` item config:
  - https://github.com/rh-hideout/pokeemerald-expansion/blob/master/include/config/item.h

Do **not** attempt to make the ROM reproduce every Emerald cartridge bug or undocumented quirk if expansion already has a functioning Gen 3 implementation.

Do **not** build a Pokémon Showdown differential-testing harness for this task.

---

# 2. Architectural rule: do not change `GEN_LATEST`

Do **not** globally redefine:

```c
GEN_LATEST
```

to Generation 3.

`GEN_LATEST` is used by many unrelated systems in `pokeemerald-expansion`. Changing it globally could unintentionally revert:

- overworld behavior
- item usability
- menus
- catching
- experience systems
- evolution systems
- scripting
- quality-of-life features
- other expansion functionality

Instead, explicitly configure **battle-relevant settings** to their Generation 3 behavior.

Plastic Ox should remain:

```text
pokeemerald-expansion
├── modern overworld / scripting / QoL
├── custom Plastic Ox map and progression
├── custom encounter and evolution gating
└── ADV OU battle rules
```

---

# 3. Core battle mechanics

Audit `include/config/battle.h`.

For every generation-switchable option that changes actual battle behavior, select the **Generation 3 implementation** unless an exception is explicitly listed later in this document.

At minimum, ensure the following areas use Gen 3 behavior.

## Damage and move classification

- Physical/Special split must be **type-based**, not move-based.
- Critical-hit rate must use Gen 3 rules.
- Critical-hit damage must be **2×**.
- Gen 3 damage calculations and modifier behavior should use the existing expansion/decomp Gen 3 implementation.
- Gen 3 spread-move damage rules must be used.
- Gen 3 Explosion/Self-Destruct Defense interaction must be used.
- Gen 3 type chart must be used.
- No Fairy type battle interactions.
- No later-generation type-chart changes.

Relevant expansion settings include:

```c
B_PHYSICAL_SPECIAL_SPLIT
B_CRIT_CHANCE
B_CRIT_MULTIPLIER
B_MULTIPLE_TARGETS_DMG
B_EXPLOSION_DEFENSE
B_UPDATED_TYPE_MATCHUPS
```

Set these to the value that produces **Gen 3 behavior**.

---

## Status conditions

Use Gen 3 behavior for:

- paralysis Speed reduction
- confusion self-hit chance
- burn damage
- sleep duration
- binding damage and duration
- Taunt duration
- Encore duration
- Disable duration
- Uproar duration/behavior
- freeze/thaw behavior
- poison/toxic mechanics
- residual damage timing where generation-configurable

Relevant settings include:

```c
B_PARALYSIS_SPEED
B_CONFUSION_SELF_DMG_CHANCE
B_BURN_DAMAGE
B_BURN_FACADE_DMG
B_SLEEP_TURNS
B_BINDING_DAMAGE
B_BINDING_TURNS
B_TAUNT_TURNS
B_ENCORE_TURNS
B_DISABLE_TURNS
B_UPROAR_TURNS
B_UPROAR
B_HIT_THAW
```

Use existing Gen 3 implementations. Do not rewrite niche status logic unless expansion lacks a required ADV option.

---

## Move mechanics

Use Gen 3 behavior for generation-sensitive moves and move systems, including:

- Hidden Power
- Knock Off
- Protect success/failure progression
- Pursuit
- Counter
- Mirror Coat
- Rage
- multi-hit move distributions
- SolarBeam in weather
- any other move whose expansion config explicitly exposes historical behavior

Relevant settings include:

```c
B_HIDDEN_POWER_DMG
B_HIDDEN_POWER_COUNTER
B_KNOCK_OFF_DMG
B_KNOCK_OFF_REMOVAL
B_PROTECT_FAILURE_RATE
B_PURSUIT_TARGET
B_MULTI_HIT_CHANCE
B_RAGE_BUILDS
B_SANDSTORM_SOLAR_BEAM
```

If additional `B_*` settings in the current repository describe a mechanical change introduced after Gen 3, configure them for Gen 3 as well.

---

# 4. Abilities

Use **Generation 3 ability behavior**.

Important examples include:

- Sturdy only blocking OHKO moves
- Gen 3 Lightning Rod behavior
- Gen 3 Shadow Tag behavior
- Gen 3 Flash Fire behavior
- Gen 3 Synchronize behavior
- Gen 3 Plus/Minus interaction
- Gen 3 weather abilities
- Gen 3 contact-ability trigger rates
- Gen 3 Rough Skin damage

Relevant settings include:

```c
B_ABILITY_WEATHER
B_ROUGH_SKIN_DMG
B_SHADOW_TAG_ESCAPE
B_FLASH_FIRE_FROZEN
B_SYNCHRONIZE_TOXIC
B_STURDY
B_PLUS_MINUS_INTERACTION
B_REDIRECT_ABILITY_IMMUNITY
B_REDIRECT_ABILITY_ALLIES
B_ABILITY_TRIGGER_CHANCE
```

Audit all other generation-configurable ability behavior in the current `battle.h` and select Gen 3 where appropriate.

---

# 5. Pokémon battle data

Configure battle-relevant species data to its Generation 3 state.

In `include/config/pokemon.h`, ensure the effective behavior is equivalent to:

```c
#define P_UPDATED_TYPES GEN_3
#define P_UPDATED_STATS GEN_3
#define P_UPDATED_ABILITIES GEN_3
```

The purpose is to prevent later-generation changes from silently changing ADV battles.

Examples of things that must not leak into Plastic Ox battles:

- later type changes
- later base-stat buffs
- later ability replacements

Do **not** use this task to alter encounter availability or progression gating. Those are controlled separately by Plastic Ox's encounter/tier design.

---

# 6. Move data

Moves available in Plastic Ox battles should use their **Generation 3 properties**.

Audit the expansion move-data generation configs and use Gen 3 values for:

- base power
- accuracy
- PP
- type
- priority
- targeting
- relevant flags
- effect behavior when generation-configurable

Relevant settings include:

```c
B_UPDATED_MOVE_DATA
B_UPDATED_MOVE_TYPES
B_UPDATED_MOVE_FLAGS
```

Use Gen 3 values.

Disable extrapolated modern flags where they would cause older moves to inherit post-Gen-3 interactions:

```c
#define B_EXTRAPOLATED_MOVE_FLAGS FALSE
```

The project should not introduce post-Gen-3 move mechanics into the standard battle ruleset.

---

# 7. Held items

Battle-relevant held items must use their Gen 3 behavior.

At minimum:

```c
#define I_SITRUS_BERRY_HEAL GEN_3
#define I_TYPE_BOOST_POWER GEN_3
#define I_LAX_INCENSE_BOOST GEN_3
```

Expected ADV examples:

- Sitrus Berry heals 30 HP.
- Standard type-boosting held items use their Gen 3 boost.
- Sea Incense uses its Gen 3 boost.
- Lax Incense uses its Gen 3 value.

Audit any other item config that changes **held-item battle effects** across generations and select Gen 3 behavior.

Do not unnecessarily revert overworld item prices, bag behavior, fossil handling, Repels, etc.

---

# 8. Explicit modern mechanics to disable

The standard Plastic Ox battle ruleset must not contain post-Gen-3 battle systems.

Disable or ensure inaccessible:

- physical/special split by individual move
- Fairy type
- Mega Evolution
- Primal Reversion
- Z-Moves
- Dynamax / Gigantamax
- Terastallization
- Gems
- modern weather mechanics where they differ from ADV
- modern ability upgrades
- modern held-item effects
- affection-based battle survival/stat effects
- frostbite

At minimum:

```c
#define B_AFFECTION_MECHANICS FALSE
#define B_USE_FROSTBITE FALSE
```

Do not enable battle flags for Dynamax or Terastallization.

---

# 9. Important exceptions to “set everything to GEN_3”

Some Gen 3 cartridge behavior is **not** part of the desired competitive ADV OU environment.

## Disable badge stat boosts

Do not apply Emerald badge boosts during battle.

`B_BADGE_BOOST` must be configured so that badge stat bonuses are disabled.

The player's combat stats must not change because of story badge ownership.

---

## Keep expansion/decomp bug fixes

Do not globally disable:

```c
BUGFIX
```

The goal is not bug-for-bug Emerald emulation.

Keep existing bug fixes unless a specific existing expansion Gen 3 setting already implements the competitive ADV behavior.

---

# 10. Global ADV OU ruleset

Plastic Ox should use ADV OU clauses **throughout the game**, not only in a special Battle Tower or optional competitive mode.

Implement one centralized ruleset, e.g.:

```text
RULESET_ADV_OU
```

or equivalent.

All ordinary trainer battles, boss battles, Gym battles, Elite-style battles, and other competitive trainer battles should use this ruleset automatically.

Avoid duplicating clause logic across individual trainers.

---

# 11. Sleep Clause Mod

Globally enforce current ADV OU Sleep Clause behavior:

> A player may not put a second opposing Pokémon to sleep with a sleep-inducing move while a Pokémon that player previously put to sleep is still asleep.

Important:

- self-induced sleep such as Rest should not count against the opponent's Sleep Clause
- the clause should apply symmetrically to player and AI
- the AI must understand that an illegal sleep move should not be selected when possible

`pokeemerald-expansion` already exposes:

```c
B_FLAG_SLEEP_CLAUSE
```

Use the existing sleep-clause implementation rather than writing a new one if practical.

Because Plastic Ox uses this rule globally, make the ADV OU ruleset activate this behavior automatically instead of requiring every trainer script to remember a flag.

---

# 12. Freeze Clause Mod

Current ADV OU uses Freeze Clause Mod:

> A player may not freeze a second opposing Pokémon while another Pokémon that player froze remains frozen.

Implement this globally and symmetrically.

If expansion already contains a Freeze Clause implementation, reuse it.

If not, add a small centralized clause hook rather than modifying individual ice moves.

---

# 13. Species Clause

A battle-eligible party may contain only one Pokémon of each National Pokédex number.

Examples:

```text
two Tyranitar -> illegal
two Gengar -> illegal
two Pikachu -> illegal
```

Species Clause should concern the **active battle party**, not ownership.

Do not prevent the player from:

- catching duplicates
- storing duplicates
- breeding duplicates
- owning multiple copies in the PC

Implement battle-party validation centrally.

Trainer rosters must also obey Species Clause.

If a player attempts to start a trainer battle with an illegal active party, prevent the battle from beginning and give a clear message explaining the violation.

Avoid creating a permanent softlock: the validation flow must allow the player to correct the party composition.

---

# 14. OHKO Clause

The following moves are illegal under ADV OU:

- Fissure
- Guillotine
- Horn Drill
- Sheer Cold

Do not delete their engine implementations.

Instead, make them illegal under `RULESET_ADV_OU`.

They should not appear on standard trainer sets, and the player should not be allowed to enter/use them in ADV OU trainer battles.

Prefer a centralized legality mechanism over hardcoding move behavior to fail.

---

# 15. Evasion Moves Clause

The following direct evasion-boosting moves are illegal:

- Double Team
- Minimize

Treat them as format-illegal rather than deleting their move definitions.

They must not appear on trainer sets or be usable in ADV OU trainer battles.

---

# 16. Evasion Items Clause

The following held items are illegal in current ADV OU:

- BrightPowder
- Lax Incense

Do not remove them from the ROM unless the broader game design separately chooses to do so.

Instead, make them illegal held items for the ADV OU battle ruleset.

---

# 17. Switch Priority Clause Mod

Current Showdown ADV OU does **not** use Emerald link-battle player-slot switch ordering.

When both sides switch on the same turn, switching priority should follow the current ADV OU / Showdown behavior:

> The faster Pokémon switches first.

Check whether `pokeemerald-expansion` already implements or configures this behavior.

If it does, enable the existing implementation.

If not, make the smallest battle-order patch needed to match the current ADV OU rule.

This is one of the few rules in this document where current competitive ADV intentionally differs from raw Emerald link-battle behavior.

---

# 18. Baton Pass restrictions

Current ADV OU contains additional Baton Pass restrictions. Implement them as **team/set legality rules**, not by rewriting Baton Pass itself.

## One Boost Passer Clause

A team may have at most **one Baton Pass user that also has a way to boost its stats**.

Create reusable validation for this rule.

---

## Baton Pass Stat Clause

A Baton Pass user may not have a way to boost its **Speed**.

This should account for relevant Gen 3 moves/abilities/set construction according to the current Showdown ADV OU interpretation.

Prefer a data-driven validator over scattered special cases.

---

## Trapping + Baton Pass

The following combinations are illegal:

- Baton Pass + Block
- Baton Pass + Mean Look
- Baton Pass + Spider Web

---

## Smeargle + Ingrain

The following combination is illegal:

- Smeargle + Ingrain

Apply the current ADV OU legality interpretation used by Showdown/Smogon.

---

# 19. Additional ADV OU bans

Current ADV OU also bans specific abilities and moves.

## Abilities

Illegal:

- Sand Veil
- Soundproof

These should be handled by the ADV OU legality layer.

Do not globally delete the abilities from the engine.

---

## Moves

Illegal:

- Assist
- Swagger

Also enforce the Baton Pass combination restrictions listed above.

---

# 20. Uber legality

ADV OU does not permit Uber-tier Pokémon.

Plastic Ox's encounter/progression system is expected to control species availability separately, so do not rewrite the encounter system as part of this task.

However, the central ADV OU legality system should support rejecting Uber-tier species if they become battle-accessible.

Use a data table/tag rather than scattering species checks through battle code.

All lower tiers remain OU-legal unless specifically banned:

```text
PU / NU / RU / UU / UUBL / OU
```

can all participate in an OU-format battle if otherwise legal.

---

# 21. Endless Battle Clause

Current ADV OU includes Endless Battle Clause.

First inspect whether expansion already has support for preventing intentionally endless battle states.

Do not build a large Pokémon Showdown-style battle-loop detector unless necessary.

At minimum:

- trainer rosters must never be constructed around an intentionally endless battle loop
- player legality should reject any known explicitly banned endless-battle construction if one is already represented by the engine/ruleset
- Struggle and ordinary PP exhaustion must continue to resolve battles normally

Keep this implementation minimal unless existing engine support makes full enforcement straightforward.

---

# 22. Rules that do not need literal Showdown UI replication

The goal is battle-rule parity, not a web-simulator UI.

The following Showdown rules/mods do not need to be reproduced literally unless Plastic Ox already wants them:

- HP Percentage Mod
- battle timer
- Cancel Mod
- Nickname Clause
- Showdown battle-log formatting

Plastic Ox may continue to use normal ROM battle graphics and UI.

Do not change overworld UI or progression systems merely to imitate Showdown presentation.

---

# 23. Trainer battle format behavior

The important invariant is:

> Every trainer battle should resolve under one consistent ADV OU legality/mechanics layer.

Recommended implementation:

```text
Start trainer battle
    ↓
Apply RULESET_ADV_OU
    ↓
Validate player battle party
    ↓
Validate trainer roster during development/build
    ↓
Enable global clauses
    ↓
Run battle using Gen 3 mechanics
```

For trainer data, add validation during build/tests so illegal trainer parties fail loudly during development rather than failing at runtime.

At minimum validate:

- duplicate species
- banned species
- banned abilities
- banned held items
- banned moves
- banned move combinations
- Baton Pass restrictions

---

# 24. Wild battles

Wild battles are not competitive six-Pokémon OU matches, so team-construction clauses are generally irrelevant.

Do not interfere with:

- catching
- Safari-style systems
- scripted wild encounters
- encounter tables

However, the underlying battle mechanics should still use the same Gen 3 combat engine.

If a clause has no meaningful application to a normal wild battle, it does not need special enforcement there.

---

# 25. Battle bag / Shift mode

Do not silently change RPG behavior unless explicitly required by the project.

However, the coding agent should identify and report whether trainer battles currently allow:

- bag healing/items
- Shift-mode free switches after an opposing Pokémon faints

These are not part of Pokémon Showdown competitive battles.

For this task:

- do **not** change them without an explicit project decision
- isolate them as two clearly documented optional compatibility switches

Recommended names if a project-level config is added:

```c
PLASTIC_OX_DISABLE_BAG_IN_TRAINER_BATTLES
PLASTIC_OX_FORCE_SET_MODE
```

Default behavior for this task should preserve the existing game unless the repository/project already specifies otherwise.

---

# 26. Do not change progression mechanics

This task must not modify Plastic Ox's separate progression design.

Do not alter:

- gym order
- level caps
- encounter tier release
- LC / PU / NU / RU / UU / UUBL / OU gating
- custom evolution levels
- evolution-item release timing
- map design
- story
- trainer AI architecture
- custom boss AI
- overworld scripts unrelated to battle-rule activation

The ADV OU layer determines **how battles work**, not **when Pokémon become available**.

---

# 27. Recommended implementation structure

Prefer a centralized compatibility layer rather than hundreds of one-off edits.

Suggested structure:

```text
include/
    config/
        plastic_ox_battle.h

src/
    plastic_ox_battle_rules.c

include/
    plastic_ox_battle_rules.h
```

Exact filenames may be adapted to repository conventions.

Possible conceptual API:

```c
enum PlasticOxBattleRuleset
{
    RULESET_ADV_OU,
};

bool8 IsMoveLegalUnderRuleset(u16 move, enum PlasticOxBattleRuleset ruleset);
bool8 IsItemLegalUnderRuleset(u16 item, enum PlasticOxBattleRuleset ruleset);
bool8 IsAbilityLegalUnderRuleset(u16 ability, enum PlasticOxBattleRuleset ruleset);
bool8 IsSpeciesLegalUnderRuleset(u16 species, enum PlasticOxBattleRuleset ruleset);
bool8 ValidatePartyForRuleset(...);
```

Do not force this exact API if expansion already has a cleaner native mechanism.

Prefer native expansion patterns over unnecessary new abstractions.

---

# 28. Configuration audit process

The coding agent should perform this sequence.

## Step 1 — Inspect current repository version

Read:

```text
include/config/battle.h
include/config/pokemon.h
include/config/item.h
include/config/general.h
```

Identify every setting that changes battle outcomes across generations.

---

## Step 2 — Create an ADV battle configuration profile

Set all relevant generation-selectable battle options to Gen 3.

Do not globally change `GEN_LATEST`.

---

## Step 3 — Apply explicit exceptions

Ensure:

```text
badge stat boosts        OFF
affection battle effects OFF
frostbite                OFF
modern battle gimmicks   OFF
modern move flags        OFF where they alter ADV behavior
BUGFIX                    ON
```

---

## Step 4 — Add the global ADV OU legality layer

Implement:

```text
Sleep Clause Mod
Freeze Clause Mod
Species Clause
OHKO Clause
Evasion Moves Clause
Evasion Items Clause
Switch Priority Clause Mod
One Boost Passer Clause
Baton Pass Stat Clause
Baton Pass + trapping restrictions
Smeargle + Ingrain restriction
Sand Veil ban
Soundproof ban
Assist ban
Swagger ban
Uber species rejection
minimal Endless Battle Clause handling
```

---

## Step 5 — Apply rules automatically

All trainer battles should activate the same ruleset without individual trainer scripting.

---

## Step 6 — Validate trainer data

Add development-time validation so illegal trainer sets are detected.

Do not rely solely on runtime validation.

---

## Step 7 — Build and run existing tests

Run the repository's normal build and battle tests.

Fix compile errors or existing-test regressions caused by the configuration changes.

Do **not** create an exhaustive Pokémon Showdown parity suite.

The project is intentionally trusting the Gen 3 implementations already maintained by the decomp/expansion community.

---

# 29. Acceptance criteria

The task is complete when all of the following are true.

## Mechanics

- [ ] Physical/Special category is determined by type as in Gen 3.
- [ ] Gen 3 move power/type/effect data is active.
- [ ] Gen 3 Pokémon battle stats/types/abilities are active.
- [ ] Gen 3 held-item battle effects are active.
- [ ] Gen 3 critical-hit behavior is active.
- [ ] Gen 3 status mechanics are active.
- [ ] Gen 3 weather mechanics are active.
- [ ] Gen 3 ability behavior is active.
- [ ] Gen 3 switching/faint replacement mechanics are active except where current ADV OU explicitly overrides cartridge behavior.
- [ ] No post-Gen-3 battle gimmicks are usable.
- [ ] Badge boosts are disabled.
- [ ] Affection battle effects are disabled.
- [ ] Frostbite is disabled.

## ADV OU rules

- [ ] Sleep Clause Mod is globally active.
- [ ] Freeze Clause Mod is globally active.
- [ ] Species Clause is globally enforced for battle parties.
- [ ] OHKO moves are illegal.
- [ ] Double Team and Minimize are illegal.
- [ ] BrightPowder and Lax Incense are illegal.
- [ ] Faster-Pokémon switch priority is used for simultaneous switches.
- [ ] One Boost Passer Clause is enforced.
- [ ] Baton Pass Speed-boost restriction is enforced.
- [ ] Baton Pass + trapping move combinations are illegal.
- [ ] Smeargle + Ingrain is illegal.
- [ ] Sand Veil is illegal.
- [ ] Soundproof is illegal.
- [ ] Assist is illegal.
- [ ] Swagger is illegal.
- [ ] Uber species can be rejected by the ruleset.
- [ ] Trainer rosters are build-time validated against the same rules.

## Architecture

- [ ] `GEN_LATEST` was not globally changed.
- [ ] Overworld systems were not reverted to Gen 3.
- [ ] Plastic Ox encounter/evolution progression was not modified.
- [ ] Clause logic is centralized rather than duplicated across trainers.
- [ ] Existing expansion/decomp Gen 3 mechanics were reused instead of rewritten.
- [ ] No unnecessary Showdown parity harness was introduced.

---

# 30. Final deliverable expected from the coding agent

When finished, provide:

1. A summary of files changed.
2. The battle-generation configs changed to Gen 3.
3. The explicit non-Gen-3 exceptions retained and why.
4. The ADV OU clauses implemented.
5. Any ADV OU rule that could not be cleanly represented in the current engine.
6. Any existing expansion feature reused for clause enforcement.
7. Build/test results.
8. A separate note on the two optional competitive-format differences:
   - trainer-battle bag use
   - Shift mode vs Set mode

Do not expand the scope into overworld redesign or progression changes.
