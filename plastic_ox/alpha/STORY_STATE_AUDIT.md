# Plastic Ox persistent story-state audit

Audited 2026-09-14 against the Emerald build. Run
`python3 plastic_ox/alpha/audit_alpha.py --markdown` for the complete,
symbol-by-symbol table with current lexical read/write locations. The normal
mode is the collision/range gate used before builds.

| Symbols | IDs | Purpose and sites | Safety | Action |
|---|---:|---|---|---|
| `FLAG_POX_STORY_BURNED_TOWER` through `FLAG_POX_REACHED_FORTREE` | `0x020-0x03B` | Story completions, gifts, actor hiding; generated story and map objects | Safe: aliases Emerald's contiguous explicitly-unused run | Keep stable; no free IDs |
| Seafoam current, boulder, Articuno, and first item flags | `0x03C-0x04F` | FRLG Seafoam map scripts/objects/items | Safe: same explicitly-unused run | Keep stable; no free IDs |
| Four `FLAG_POX_LEGACY_GRANDPA_*` inputs | `0x054`, `0x055`, `0x068`, `0x096` | Read once by `Pox_CottageFossils` to import recent development saves | Safe while reserved. `0x096` aliases the unused R/S Contest Pass; it has no retained read/write site | Never write or reuse; remove only with an explicit save-version migration |
| `FLAG_POX_STORY_STARTER` through battle-demo hide flags | `0x264-0x27D` | Alpha story completions, build mode, gifts, actor visibility | Safe: explicitly-unused Emerald run | Keep stable |
| `FLAG_POX_HIDE_SEAFOAM_ISLANDS_B4F_ULTRA_BALL` / speedup guard | `0x27E-0x27F` | Imported item / overworld timing guard | Safe: explicitly-unused Emerald IDs | Keep stable |
| Imported item/object flags through `FLAG_POX_ROUTE2_PARALYZE_HEAL` | `0x280-0x2BB` | Map JSON object flags and `finditem` scripts | Safe: explicitly-unused Emerald run | Keep stable; run is full |
| Seven supplemental imported-item flags | `0x0E9`, `0x1AA`, `0x1DA`, `0x1DE-0x1DF`, `0x493-0x494` | Seafoam, v7, and Mansion map items | Safe: each corresponding Emerald symbol is explicitly marked unused and has no retained site; `0x493-0x494` satisfy the hidden-item minimum | Deliberate repurpose; next candidates are `0x1AB`/`0x1E0-0x1E3` for objects and `0x495` for hidden items |
| `VAR_POX_STARTER_SPECIES` through `VAR_POX_MOM_STATE` | `0x40F7-0x40FF` | Species choice, ordered story substates, portal trigger sentinel, Seafoam state, world speed, Mom, grandfather rewards | In bounds, unique; all nine top-of-range slots allocated | Keep stable; **no next variable slot** |

## Findings resolved

- Seafoam Water Stone and Big Pearl used `0x26E-0x26F`, colliding with Elm
  reward flags. They now use audited supplemental IDs.
- Five imported-item definitions continued past the reserved run into
  `0x2BC-0x2C0`; three of those alias retained Emerald object flags and the
  other two sit in the same non-reserved event region. All five now use
  audited supplemental IDs. Development saves may respawn these seven items;
  that is preferable to preserving corrupt aliases.
- Bill's grandfather consumed five booleans for a strictly ordered sequence.
  The sequence now uses `VAR_POX_GRANDPA_PROGRESS` (`0-5`) in the formerly
  unused `0x40FB` slot. Four safe old flags migrate automatically. The former
  Helix flag `0x071` was unsafe because retained Cave of Origin callbacks read
  it; saves stopped exactly after Yanma must repeat that reward step.
- `VAR_POX_PORTAL_GATE` is intentionally a persistent zero-valued trigger
  sentinel, not story state. Changing it would disable many authored portal
  coordinate events, so it remains allocated and documented.
- `FLAG_POX_HIDE_SAFFRON_GATE_NPC` is retired but stays reserved to preserve
  object visibility in development saves. No established state was renumbered
  for aesthetics.

## Allocation rules

Use a flag for an independent yes/no fact and an existing small progression
variable for a strictly ordered sequence. Do not allocate beyond `0x40FF`, in
trainer/daily flag ranges, or by continuing an arithmetic flag base past its
documented end. Before using a documented next candidate, add the symbol and intended purpose
to the checker allow-list and prove the vanilla `FLAG_UNUSED_*` symbol has no
retained read/write sites. Treat generated story scripts and maps as outputs:
update `build_story.py` / `region_v7.py` together with checked-in outputs.
