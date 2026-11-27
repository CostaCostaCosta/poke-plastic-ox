#include "global.h"
#include "test/battle.h"

// Plastic Ox: B_FREEZE_CLAUSE (ADV OU Freeze Clause Mod) is always on.

ASSUMPTIONS
{
    ASSUME(B_FREEZE_CLAUSE == TRUE);
    ASSUME(MoveHasAdditionalEffect(MOVE_ICE_BEAM, MOVE_EFFECT_FREEZE_OR_FROSTBITE) == TRUE);
}

SINGLE_BATTLE_TEST("Freeze Clause: a second Pokémon can't be frozen while a teammate is frozen")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET);
        OPPONENT(SPECIES_WOBBUFFET);
        OPPONENT(SPECIES_WYNAUT) { Status1(STATUS1_FREEZE); }
    } WHEN {
        TURN { MOVE(player, MOVE_ICE_BEAM, WITH_RNG(RNG_SECONDARY_EFFECT, TRUE)); }
    } SCENE {
        ANIMATION(ANIM_TYPE_MOVE, MOVE_ICE_BEAM, player);
        HP_BAR(opponent);
        NOT FREEZE_OR_FROSTBURN_STATUS(opponent, TRUE);
    }
}

SINGLE_BATTLE_TEST("Freeze Clause: a Pokémon can be frozen when no teammate is frozen")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET);
        OPPONENT(SPECIES_WOBBUFFET);
        OPPONENT(SPECIES_WYNAUT);
    } WHEN {
        TURN { MOVE(player, MOVE_ICE_BEAM, WITH_RNG(RNG_SECONDARY_EFFECT, TRUE)); }
    } SCENE {
        ANIMATION(ANIM_TYPE_MOVE, MOVE_ICE_BEAM, player);
        HP_BAR(opponent);
        FREEZE_OR_FROSTBURN_STATUS(opponent, TRUE);
    }
}

SINGLE_BATTLE_TEST("Freeze Clause: the clause is per side; the opponent's freeze doesn't protect the player")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET);
        OPPONENT(SPECIES_WOBBUFFET) { Status1(STATUS1_FREEZE); }
        OPPONENT(SPECIES_WYNAUT);
    } WHEN {
        TURN { MOVE(opponent, MOVE_ICE_BEAM, WITH_RNG(RNG_SECONDARY_EFFECT, TRUE)); MOVE(player, MOVE_CELEBRATE); }
    } SCENE {
        FREEZE_OR_FROSTBURN_STATUS(player, TRUE);
    }
}

SINGLE_BATTLE_TEST("Sleep Clause: on by default, a second sleep move fails")
{
    GIVEN {
        ASSUME(B_SLEEP_CLAUSE == TRUE);
        ASSUME(GetMoveNonVolatileStatus(MOVE_SPORE) == MOVE_EFFECT_SLEEP);
        PLAYER(SPECIES_BRELOOM);
        OPPONENT(SPECIES_WOBBUFFET);
        OPPONENT(SPECIES_WYNAUT);
    } WHEN {
        TURN { MOVE(player, MOVE_SPORE); }
        TURN { SWITCH(opponent, 1); MOVE(player, MOVE_SPORE); }
    } SCENE {
        ANIMATION(ANIM_TYPE_MOVE, MOVE_SPORE, player);
        STATUS_ICON(opponent, sleep: TRUE);
        NONE_OF {
            ANIMATION(ANIM_TYPE_MOVE, MOVE_SPORE, player);
            STATUS_ICON(opponent, sleep: TRUE);
        }
    }
}
