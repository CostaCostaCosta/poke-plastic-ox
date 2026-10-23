# Cinnabar and legendary Sage encounters

Cinnabar's real gym is open before the Mansion. Its Blaine object invokes the
Plastic Ox Blaine battle and existing badge progression. Blaine gives the
Mansion Key (`ITEM_SECRET_KEY`, renamed in the bag); the Mansion's actual
entrance checks possession of that item. Both outdoor guides give directions.
They no longer warp into the placeholder gym/archive rooms.

The original four Mansion layouts, stairs, falls and statue-switch puzzle are
retained. The existing story archive sequence is available on the 2F, 3F and
B1F books, so the Mossdeep story gate remains reachable in the real Mansion.
Imported puzzle, gym quiz and visible item flags now have persistent storage.
Blaine no longer attempts to give HM05: this build explicitly sanitizes the
Flash HM to ITEM_NONE, which previously asserted before the key reward.

At the old B1F Secret Key location, the Sage stands at (5,7) and Entei at (6,7).
Both invoke the same encounter. The Sage has Crobat, Donphan, Vaporeon,
Hariyama, Espeon and Entei: all UUBL in `evolution_tier_gates.h`. Trainer levels
use the project's normal battle normalization; the caught Entei is level 45.

A loss leaves the trainer unbeaten. A win persists the trainer victory and
unlocks a separate wild reward encounter. Any ball thrown in that encounter
guarantees capture. Declining, running, losing or knocking Entei out leaves
the reward available; the Sage need not be beaten again. Only successful
capture hides both objects and sets `FLAG_POX_ENTEI`. A full party uses normal
PC storage. The retired placeholder room has no duplicate Entei.

## Reuse

`data/scripts/plastic_ox_legendary_sages.inc` defines:

```asm
pox_legendary_sage EntryLabel, TRAINER_ID, SPECIES_ID, LEVEL, CAUGHT_FLAG, SAGE_LOCAL_ID, LEGENDARY_LOCAL_ID, IntroText, DefeatText
```

For another legendary:

1. Add its authored trainer team and a unique trainer ID.
2. Allocate a persistent caught flag, and give both objects that hide flag.
3. Use `TRAINER_TYPE_NONE` for both objects, with `EntryLabel` as their script.
   The macro starts the trainer battle on interaction; it is not a sight script.
4. Invoke the macro with that map's generated local-ID constants. Include the
   macro definition before the invocation.

The trainer's existing victory flag is the intermediate state. Do not set the
caught flag merely for `B_OUTCOME_WON`: it is reserved for `B_OUTCOME_CAUGHT`.
`BattleSetup_StartLegendaryRewardBattle` is called after `setwildbattle`, and
its special has an implicit wait. The guarantee uses a battle-type bit, not a
saved flag. Ordinary battles initialize their own flags and receive no bonus.

Virtual event flags occupy 0xB00–0xB7F in appended SaveBlock3 storage, with an
independent initialization marker for old saves. Event slots are 0xB00–0xB3F;
trainer IDs 938–1001 use 0xB40–0xB7F. Existing save-field offsets are retained.
Always update the flag audit when extending these ranges.

`cinnabar.py` reapplies the map/script wiring and canonical team after the
region/story generator. It is idempotent. The team generator explicitly
preserves the Sage's authored team.

## Import provenance

The Sage overworld sprite, palette, battle portrait and portrait palette come
from `/home/eddie/repos/pokehns-expansion`, revision
`44f50eedefe58691b0444973e4138e9190d8fafc`:

- `graphics/object_events/pics/people/sage_hns.png` (144x32; nine 16x32 frames)
- `graphics/object_events/palettes/sage_hns.pal`
- `graphics/trainers/front_pics/sage_hns.png`
- `graphics/trainers/palettes/sage_hns.pal`

The overworld descriptor uses this engine's native 16x32 OAM, animation table,
and a dedicated palette tag, following the established Whitney conversion.
Entei uses the existing `OBJ_EVENT_GFX_ENTEI` asset. No new map layout, tileset,
connection, or encounter table is imported. The existing FRLG Cinnabar gym and
Mansion map group/layout registrations and paired tilesets remain in use.

## Verification

```sh
PATH=/home/eddie/devkitpro/opt/devkitpro/devkitARM/bin:$PATH \
  make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
python3 plastic_ox/alpha/audit_alpha.py
python3 /home/eddie/.codex/skills/plastic-ox-map-port/scripts/audit_imports.py .
python3 plastic_ox/agent/test_trainer_teams_v2.py
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 \
  /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_cinnabar.py
git diff --check
```

The emulator fixture uses the real doors, Blaine/Sage battle scripts, battle
outcome callbacks, ball bag, PC transfer, statue and save/reset/Continue flow.
It changes battle HP/stats in emulator RAM to shorten the fights; it does not
inject victory callbacks or patch the ROM. Fresh images are written under
`/tmp/pox_cinnabar_shots/`. Coverage includes lock/unlock and entry/exit, actual
Blaine reward, puzzle toggling and map reload, loss/rematch, six-opponent Sage
victory, reward KO/retry, first-throw full-HP captures with Poké/Premier/Ultra
Balls, full-party boxing, actor removal, saved state and ordinary battle reset.
It also flees the reward battle, declines the actual yes/no menu with B,
saves and reloads the unclaimed reward, then interacts directly with Entei to
confirm the Sage victory persists and no rematch is required.

## Completion verification — 2026-10-14

Resumed the existing implementation, rebuilt `pokeemerald.gba`, and passed
the complete emulator regression above, including the added deferred-reward
checks. Reviewed fresh screenshots of the gym, Mansion switch, Sage/Entei
placement, and their absence after capture and save/reload.

- Import audit: 102 HNS layouts passed.
- Persistent flag audit: 231 unique allocations passed.
- Trainer team audit: 2,684 checks over 83 trainers passed. All six Sage
  species are UUBL in the project's tier table.
- Generator replay: all 13 outputs match the working tree; a second in-memory
  application produces identical output.
- `git diff --check`: passed.

The emulator shortens battles by adjusting HP/stats in RAM and warps between
test locations. It exercises the actual entry doors and statue switch, but
does not constitute a continuous walkthrough of every Mansion floor.
The build retains the linker warning about an RWX LOAD segment.
