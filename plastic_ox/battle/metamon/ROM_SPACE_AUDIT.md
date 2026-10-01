# ROM space audit for a larger metamon model

Measured 2026-09-25 on the deployed build (`pokeemerald.gba` / `.elf` / `.map`,
branch state as of `codex/metamon-trainer-ai` 5b21ca882b). Companion to
`MODEL_CAPACITY.md`. All numbers are in-ROM bytes from the linker map and
symbol tables, not on-disk asset sizes, unless marked *disk*.

## 1. Where the ROM stands today

| Region | Size |
|---|---:|
| `.text` (code) | 2,332 KB |
| `script_data` (battle/field scripts) | 1,294 KB |
| `.rodata` (tables, graphics, audio, strings) | 22,779 KB |
| EWRAM/IWRAM load images at ROM tail | ~227 KB |
| **Used total** | **26.34 MB** (ends `0x09A57E50`) |
| 0xFF padding to the 32 MB cart wall | **5.66 MB free today** |

`gMmWeights` (current 1M-param student) is 1,014.6 KB inside `.rodata`.
The free tail is immediately usable: any bigger `weights.bin` drops into it
via `src/metamon_model.c` with no linker changes.

So the model can grow to ~6.5M int8 params **before any trimming**. To go
past that, here is what can be cut, in order of value.

## 2. Tier 1 - disable gen 4-9 species: ~8.7 MB (flags only)

`include/config/species_enabled.h` currently sets `P_GEN_1..9_POKEMON` all
TRUE. The region only uses Kanto/Johto/Hoenn mons, and the metamon adapter
already clamps to Gen 3 vocab. Cost of the enabled gen 4-9 species, measured
per symbol group:

| Asset group | Gen 1-3 (keep) | Gen 4-9 (removable) |
|---|---:|---:|
| Cries (`sound_data.o`) | 1,970 KB | **5,919 KB** |
| Battle front/back pics, icons, palettes, footprints (`pokemon.o`) | 1,596 KB | **2,138 KB** |
| Overworld/follower species sprites (`gObjectEventPic_*`, `pokemon.o`) | 387 KB | **612 KB** |
| Species learnsets/strings/misc | small | ~100-300 KB |

Per-generation cry cost (the single biggest lever): gen4 615 KB, gen5 1,163 KB,
gen6 642 KB, gen7 950 KB, gen8 1,037 KB, gen9 1,513 KB (sum 5,919 KB).

Also set in the same file:
- `P_CROSS_GENERATION_EVOS FALSE` - removes gen 4-9 evolutions of kept
  families (Rhyperior, Tangrowth, Mamoswine, Gliscor, Electivire, Magmortar,
  Leafeon, Glaceon, Sylveon, Annihilape, Clodsire, Farigiraf, Ursaluna, ...).
  Their sprites/cries are counted in the gen 4-9 columns above.
- `P_MEGA_EVOLUTIONS FALSE` (and Gmax) if unwanted: only ~50-150 KB extra
  (54 form front pics measured at 49 KB), but also frees `gFusionTablePointers`
  and related paths.

Mechanism: everything is already `#if`-gated (`sound/direct_sound_data.inc`,
`src/data/graphics/pokemon.h`, `src/data/pokemon/*`, follower sprite tables),
so this is a config-only change. `gSpeciesInfo` (406 KB) and `gMovesInfo` /
`gItemsInfo` stay the same size - they are fixed-size arrays - so don't count
them as savings.

Caveat: nothing in Plastic Ox may reference a disabled species. Wild
encounters, trainer parties (`TRAINING_PLASTIC_OX_*` in `src/data/trainers.h`),
gifts, and story scripts are all Gen 3 already, so this holds today; re-run
the grep after any future content edit.

## 3. Tier 2 - cut facilities Plastic Ox never uses: ~1.2 MB

POX is single-player (`POX_LINK_ENABLED 0` already in
`include/config/general.h`), no frontier, no contests planned. Removable
code+data (map-file contributions measured):

| Feature | ROM cost |
|---|---:|
| Battle Frontier (tower/dome/pike/pyramid/palace/arena/factory/tent/pass) | 213 KB code + 31 KB `gBattleFrontierMons` + 15 KB `gBattleFrontierTrainers` + 49 KB `sFrontierTrainerSlides` + facility maps/tilesets |
| Contests + bard music (`contest*`, `bard_music`) | 222 KB code + 74 KB `sBardSoundTemplates_Pokemon` + contest halls/maps/tilesets |
| Minigames (dodrio, slots, roulette, pokemon jump, berry blender/crush) | ~224 KB |
| Link/record/EReader/mystery gift (`trade.o`, union room, record mixing, ereader) | ~134 KB - verify no in-game trade scripts reference `trade.o` UI before cutting |
| Trainer slide-in banners (`trainer_slide.o` + `sTrainerSlides`) | 202 KB - decorative; cut if the story does not use slide-ins |
| Frontier facility maps (145 maps) + facility-only tilesets | 89 KB blockdata + ~294 KB tileset art *disk* (~0.2 MB in ROM) |

Total Tier 2: **~1.2-1.5 MB**. Mechanism: remove the `.c` files from the
build or wrap them behind a `POX_*` config flag. Note that `POX_LINK_ENABLED`
today gates runtime paths but not object inclusion - `trade.o`,
`union_room.o`, etc. still link in - so they need build exclusion or `#if`
guards to actually shrink the ROM. Facility maps then drop out of
`map_groups.json`.

## 4. Tier 3 - prune unreachable maps/tilesets: ~1.5-2.5 MB

Of 1,013 map directories, a warp/connection walk from Pallet Town plus all
story-referenced maps reaches **38 maps today**. Even if the finished region
keeps every imported Kanto/Johto/Hoenn map planned for the story (~150), most
of Hoenn's original 900 maps, plus all frontier/contest/secret-base/link
maps, are dead weight:

- Layout blockdata (`data/maps.o`): 1,307 KB *disk*, only 83 KB used by
  reachable maps -> **~1.2 MB** in ROM.
- Tilesets (`src/tilesets.o` 1,573 KB ROM + `tileset_anims` 141 KB): only 30
  tilesets are referenced by reachable layouts, of 192 on disk (2,283 KB
  *disk*, 492 KB used) -> **~1.0-1.2 MB** in ROM.
- Map events (116 KB) and per-map scripts (part of `event_scripts.o`
  1,033 KB + `data/maps.o`).

Mechanism (already used for earlier imports): remove map entries from
`data/maps/map_groups.json`, keep their `MAP_*` constants via
`tools/mapjson/required_map_defines.json` (mapjson emits them as "unused
maps" constants and NULLs the layout rows), and prune `data/layouts/`
entries. Re-run `audit_imports.py` (map-port skill) after edits.

Caveat: this renumbers map ids (they are `(index | group << 8)`), so do it
once, before save files matter. Base the keep-list on the planned story
map list, not today's reachable set.

## 5. Tier 4 - polish: ~0.3-0.5 MB

- Japanese fonts: 130 KB (`gFont*Japanese*`, 6 fonts) - game is English-only.
- Redundant Latin font variants (`Short/Small/Narrow/Narrower` x FRLG/base):
  up to ~160 KB of the 292 KB Latin fonts; audit which the text engine
  actually selects first.
- `map_preview_screen` 108 KB (has its own config file - feature choice),
  TV/interviews 46 KB, easy chat 47 KB, HGSS Pokedex 68 KB (currently wanted),
  decorations/secret bases ~50 KB.

## 6. Bottom line

| Plan | Freed ROM | Weight budget (free tail + savings) | int8 params at ~1.03 B/param |
|---|---:|---:|---:|
| Do nothing | 0 | 5.66 MB | ~5.8M (matches MODEL_CAPACITY.md) |
| Tier 1 only | ~8.7 MB | ~14.4 MB | ~14.9M |
| Tiers 1+2 | ~10 MB | ~15.7 MB | ~16.3M |
| Tiers 1+2+3 | ~12 MB | ~17.7 MB | ~18.3M |

Tier 1 alone (five flags set to FALSE in `species_enabled.h`) lifts the
weight budget ~2.5x, to ~15M int8 params, or supports ~15M int4 /
~23M ternary params (packing per MODEL_CAPACITY.md). That is past the
schema ceiling described there (~6M) and past the EWRAM wall, so kernel
work (IWRAM staging, tiling) and schema work remain the binding limits
once ROM is freed - but ROM stops being the first wall.

Recommended order:
1. Flip `P_GEN_4..9_POKEMON` + `P_CROSS_GENERATION_EVOS` to FALSE, rebuild,
   run `gym_smoke.py` + `smoke.py` (Lance fixture) to confirm no regression,
   and re-measure the `.map` free tail.
2. Cut Tier 2 features behind `POX_*` flags; keep `trade.o` until the story's
   in-game trades are audited.
3. Do the Tier 3 map pruning as one deliberate renumbering pass.
4. Tier 4 opportunistically.

## 7. Measurement notes

- Tooling: `pokeemerald.map` per-object section contributions;
  `arm-none-eabi-nm --size-sort` on `build/emerald/**/*.o` (per-symbol sizes
  via address diffs for INCBIN symbols); `.gba` tail scan confirmed the free
  tail is pure `0xFF` padding.
- ROM sections end at `0x09A1FFDC`; EWRAM/IWRAM load images extend used ROM
  to `0x09A57E50`. MODEL_CAPACITY.md's 26.13 MB figure counts `.rodata` only;
  the load images cost the extra ~0.21 MB.
- Numbers were taken on the plain `emerald` build dir; the sibling builds
  (`emerald-battle`, `emerald-metamon-heap`, ...) share the same sources.
