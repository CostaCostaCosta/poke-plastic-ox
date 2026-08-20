#ifndef GUARD_ROM_NATIVE_OBS_H
#define GUARD_ROM_NATIVE_OBS_H

// Canonical ROM-native battle state representation.
//
// This header mirrors the canonical schema defined in:
//   metamon/metamon/rom_native_obs/schema.py  (RomBattleState)
// The encoder (src/rom_native_obs/rom_native_obs.c) is DEBUG/TEST-ONLY and
// is meant to be called from test code or debug menus; it is not part of
// normal gameplay logic.
//
// All values use fixed-width integers (u8/u16/s8) and are deterministic.

#include "gba/types.h"

// ---------------------------------------------------------------------------
// Sizes
// ---------------------------------------------------------------------------
#define ROM_NATIVE_OBS_NUM_MOVES        4   // MAX_MON_MOVES
#define ROM_NATIVE_OBS_NUM_POKEMON      13  // 1 player active + 5 switches + 1 opponent active + 6 revealed
#define ROM_NATIVE_OBS_NUM_SWITCHES     5   // switch slots between player active and opponent active
#define ROM_NATIVE_OBS_NUM_REVEALED     6   // revealed opponent slots after opponent active
#define ROM_NATIVE_OBS_NUM_ACTIONS      9   // 4 move slots + 5 switch slots

// Slot ordering (must match schema.py's SLOT_* convention)
enum
{
    ROM_NATIVE_OBS_SLOT_PLAYER_ACTIVE = 0,
    ROM_NATIVE_OBS_SLOT_SWITCH_0,
    ROM_NATIVE_OBS_SLOT_SWITCH_1,
    ROM_NATIVE_OBS_SLOT_SWITCH_2,
    ROM_NATIVE_OBS_SLOT_SWITCH_3,
    ROM_NATIVE_OBS_SLOT_SWITCH_4,
    ROM_NATIVE_OBS_SLOT_OPPONENT_ACTIVE,
    ROM_NATIVE_OBS_SLOT_REVEALED_OPP_0,
    ROM_NATIVE_OBS_SLOT_REVEALED_OPP_1,
    ROM_NATIVE_OBS_SLOT_REVEALED_OPP_2,
    ROM_NATIVE_OBS_SLOT_REVEALED_OPP_3,
    ROM_NATIVE_OBS_SLOT_REVEALED_OPP_4,
    ROM_NATIVE_OBS_SLOT_REVEALED_OPP_5,
};

// ---------------------------------------------------------------------------
// Canonical categorical IDs (see schema.py)
//
// Status:   0 none, 1 sleep, 2 poison, 3 burn, 4 freeze, 5 paralysis,
//           6 toxic, 7 faint, 8 unknown
// Weather:  0 none, 1 rain, 2 sun, 3 sandstorm, 4 hail, 5 snow, 6 fog, 7 unknown
// Side:     0 none, 1 reflect, 2 light screen, 3 safeguard, 4 mist,
//           5 tailwind, 6 aurora veil, 7 unknown, 8 spikes
//           (single-enum side condition is lossy: only the highest-priority
//           active condition per side is reported; spikes is checked last,
//           so a screen/safeguard/mist/tailwind/aurora-veil wins over it)
// Field:    0 none, 1 gravity, 2 trick room, 3 wonder room, 4 magic room,
//           5 mud sport, 6 water sport, 7 unknown
// Effect:   0 none, 1 confusion, 2 infatuation, 3 leech seed, 4 lock,
//           5 nightmare, 6 curse, 7 unknown
// Category: 0 none, 1 physical, 2 special, 3 status, 4 unknown
// Type / move / species IDs use the ROM enum values, which for Gen1 match
// the schema (TYPE_* 0-19 remapped where the ROM enum differs, see encoder).
// Item IDs use the expansion ITEM_* enum values (u16; 0 = none/unknown).
// Ability IDs use the expansion Ability enum values (u8; 0 = none/unknown).
// ---------------------------------------------------------------------------

struct RomBattleGlobal
{
    u8 weather;             // canonical weather ID (0-7)
    u8 field_effect;        // canonical field effect ID (0-7)
    u8 player_side_cond;    // canonical side condition ID (0-7)
    u8 opponent_side_cond;  // canonical side condition ID (0-7)
    u16 player_prev_move;   // last move used by the player's active battler (0 = none/unknown)
    u16 opponent_prev_move; // last move used by the opponent's active battler (0 = none/unknown)
    u8 turn_norm;           // turn / 200 clamped, scaled to 0-255
    u8 opponents_remaining; // alive opponent party members / 6, scaled to 0-255
    u8 forced_switch;       // 1 if the player is forced to switch (active battler fainted)
};

struct RomBattlePokemon
{
    // Categorical
    u16 species;                    // National Dex ID (0 = unknown/empty)
    u8 type_1;                      // canonical Type ID
    u8 type_2;                      // canonical Type ID (TYPE_NONE if single-typed)
    u8 status;                      // canonical status ID (0-8)
    u8 effect;                      // canonical volatile effect ID (0-7)

    // Moves
    u16 moves[ROM_NATIVE_OBS_NUM_MOVES];            // move IDs (0 = unknown/none)
    u8 move_categories[ROM_NATIVE_OBS_NUM_MOVES];   // canonical category IDs
    u8 move_types[ROM_NATIVE_OBS_NUM_MOVES];        // canonical Type IDs

    // Item / ability (schema v2: appended after the first 9 categoricals)
    u16 item;                       // expansion ITEM_* enum value (0 = none/unknown)
    u8 ability;                     // expansion Ability enum value (0 = none/unknown)

    // Numerical (normalized to 0-255)
    u8 hp_fraction;                 // hp * 255 / maxHP
    u8 level_norm;                  // level * 255 / 100
    u8 base_stats[6];               // [atk, spatk, def, spdef, spe, hp], each 0-255
    s8 stat_boosts[7];              // [atk, spatk, def, spdef, spe, acc, eva], stage encoded as stage + 6 (0-12)

    // Move features (per move slot)
    u8 move_bp[ROM_NATIVE_OBS_NUM_MOVES];   // base power * 255 / 200, clamped (0-255)
    u8 move_acc[ROM_NATIVE_OBS_NUM_MOVES];  // accuracy percent * 255 / 100 (0-255; 0% accuracy stored as 255 = always hits)
    s8 move_pri[ROM_NATIVE_OBS_NUM_MOVES];  // raw move priority (-7..+7)
    u8 move_pp[ROM_NATIVE_OBS_NUM_MOVES];   // pp * 255 / maxPP (0-255)

    // Masks
    u8 valid;           // slot holds a real, non-egg Pokémon
    u8 fainted;         // HP is 0
    u8 moves_revealed;  // moves are known (the debug encoder always reveals)
    u8 hp_known;        // HP is observable (the debug encoder always knows)
    u8 item_revealed;   // item is known (the debug encoder always reveals)
    u8 ability_revealed;// ability is known (the debug encoder always reveals)
};

struct RomBattleState
{
    struct RomBattleGlobal global;
    struct RomBattlePokemon pokemon[ROM_NATIVE_OBS_NUM_POKEMON];
    u8 legal_action_mask[ROM_NATIVE_OBS_NUM_ACTIONS];  // 0-3 move slots, 4-8 switch slots
};

// Encode the current battle state from the battle engine globals.
// `out` is zeroed first; call only during an active battle (from test/debug code).
void EncodeRomBattleState(struct RomBattleState *out, u8 playerBattler, u8 opponentBattler);

#endif // GUARD_ROM_NATIVE_OBS_H
