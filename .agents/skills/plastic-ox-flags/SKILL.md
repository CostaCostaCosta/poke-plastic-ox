---
name: plastic-ox-flags
description: Allocate, find, reclaim or debug event flags in poke-plastic-ox. Use before adding any new FLAG_ (story beat, hidden item, NPC hide flag, trainer win, caught legendary), when a flag seems to collide or to be set unexpectedly, or when pox-check-static reports a flag COLLISION. Covers which ID pools are free, how to pick one, and save-compatibility rules.
---

# Plastic Ox event flags

The Emerald save has no spare general flags left in the obvious places, and
several Plastic Ox features already reuse vanilla IDs. Guessing a "free" ID is
how the Tin Tower Moltres flag ended up on top of another flag. Always ask the
audit tool instead.

## Find a free ID

```sh
python3 plastic_ox/tools/audit_flags.py            # pools + collisions (summary)
python3 plastic_ox/tools/audit_flags.py --free     # every unused/reclaimable ID with its old name
python3 plastic_ox/tools/audit_flags.py --id 0x2C7 # owners and every reference to one ID
python3 plastic_ox/tools/audit_flags.py --check    # what pox-check-static runs
```

The tool reads the flag headers the way the Emerald build does (through `cpp`),
works out which maps are reachable in Plastic Ox (`audit_cleanup_artifacts.py`),
and scans src/, include/, data/ and plastic_ox/ for references. Its results
change as maps are connected or removed, so run it at the moment you allocate.
Don't copy a list of free IDs into a note.

## Which pool to use (in order)

| Pool | IDs | Use for |
|---|---|---|
| `pox_ext` | `POX_EXT_FLAGS_START + n` (0xB80–0xF7F, 1024 flags) | **Default for every new persistent flag.** |
| `pox_general` | `POX_EVENT_FLAGS_START + 0..63` | Nearly full. Leave the rest for fixes to existing features. |
| `unused` | vanilla `FLAG_UNUSED_*` with no live use | Only when a flag must be a low SaveBlock1 ID, e.g. it's read by vanilla C code that indexes SaveBlock1 directly or by a harness that can't use the virtual blocks. |
| `reclaimable` | vanilla flags referenced only from maps that are unreachable in Plastic Ox (Battle Frontier, Mauville Gym, Hoenn-only story, etc.) | Same as `unused`, once that pool runs short. |
| `daily` | 0x920–0x95F unused | Only for things that should reset every in-game day (the RTC clears them). |

Never use: temp flags 0x00–0x1F (cleared on map load); 0x500–0x85F (trainer
flags); anything `TRAINER_FLAG()` remaps (0x082, 0x4A0–0x4E4, 0x4EB–0x4EF,
0x4F9, 0x4FA, 0x4FF, 0x91D–0x91F); `POX_SAGE_TRAINER_FLAGS_START` (+64..+127,
Sage trainer wins); and vanilla runs indexed as base + i (Match Call
registry 0x15C–0x1A9, decorations, badges, Frontier symbols). The tool already
leaves all of these out of its pools.

## Add the flag

1. Run `audit_flags.py` and take the **lowest** free ID in the pool.
2. Define it in `include/constants/plastic_ox_flags.h` with a one-line comment
   saying what sets it:
   ```c
   // Tin Tower roof: Moltres caught after its sage.
   #define FLAG_POX_CAUGHT_MOLTRES (POX_EXT_FLAGS_START + 0)
   ```
   For a reclaimed vanilla ID, write the number and name what it replaces:
   `#define FLAG_POX_X 0x2C7 // reclaimed: FLAG_HIDE_BATTLE_TOWER_MULTI_BATTLE_PARTNER_1 (unreachable)`.
   Don't rename or delete the vanilla define: dead map scripts still assemble against it.
3. If `build_story.py` or another generator owns the flag, also add it to
   `plastic_ox/alpha/story_flags.json` or to that generator; the generators emit
   their own defines, and `check_generated.py` will catch drift.
4. Run `python3 plastic_ox/tools/audit_flags.py --check`. A COLLISION means
   two live owners share an ID: pick another ID, don't silence the check.
5. Verify in mGBA (rule 7). Harness `flag()` helpers handle the virtual blocks
   through `walklib.pox_virtual_flag_addr`; `test_flag_storage.py` covers the
   storage itself.

## Save-compatibility rules

- Once a flag ID ships on master, never renumber it or give it a new meaning.
  Old saves keep the bit. To retire a flag, leave its define with a
  `// retired` comment, or clear it once in the save migration in
  `src/overworld.c` (bump `POX_SAVE_MIGRATION_VERSION`) before reusing it, as
  was done for 0x082/0x2D3.
- A reclaimed vanilla ID is only safe because the old map never ran on any
  save. If you reconnect a map whose flag was reclaimed, `--check` reports a
  collision; move the Plastic Ox flag rather than reconnecting around it.
- The SaveBlock3 blocks (`kantoHiddenItems`, `poxEventFlags`, `poxExtFlags`)
  each have a magic number and zero themselves on first use. To add another
  block, append it to the end of `struct SaveBlock3` with its own magic. Don't
  insert it before the existing blocks, because that shifts saved bytes. Then
  update `walklib.pox_virtual_flag_addr`, which assumes the existing blocks
  sit at the end of the struct.
