#include "global.h"
#include "test/battle.h"
#include "malloc.h"

/* These exercise real battle allocations/animations. The headless test runner
 * bypasses interactive menus; the separate emulator collector covers those. */
SINGLE_BATTLE_TEST("Metamon heap: singles animations and voluntary switches")
{
    u32 move = MOVE_SURF;
    PARAMETRIZE { move = MOVE_SURF; }
    PARAMETRIZE { move = MOVE_THUNDERBOLT; }
    PARAMETRIZE { move = MOVE_ICE_BEAM; }
    PARAMETRIZE { move = MOVE_EARTHQUAKE; }
    PARAMETRIZE { move = MOVE_FLAMETHROWER; }
    FORCE_MOVE_ANIM(TRUE);
    GIVEN {
        PLAYER(SPECIES_BLASTOISE) { HP(9999); MaxHP(9999); }
        PLAYER(SPECIES_SNORLAX) { HP(9999); MaxHP(9999); }
        OPPONENT(SPECIES_SNORLAX) { HP(9999); MaxHP(9999); }
        OPPONENT(SPECIES_BLISSEY) { HP(9999); MaxHP(9999); }
    } WHEN {
        TURN { MOVE(player, move); }
        TURN { SWITCH(player, 1); SWITCH(opponent, 1); }
        TURN { MOVE(player, MOVE_BODY_SLAM); }
    } SCENE {
        ANIMATION(ANIM_TYPE_MOVE, move, player);
        ANIMATION(ANIM_TYPE_MOVE, MOVE_BODY_SLAM, player);
    } THEN {
        EXPECT(!(gBattleTypeFlags & (BATTLE_TYPE_DOUBLE | BATTLE_TYPE_LINK)));
        FORCE_MOVE_ANIM(FALSE);
    }
}

SINGLE_BATTLE_TEST("Metamon heap: forced replacement and Baton Pass")
{
    FORCE_MOVE_ANIM(TRUE);
    GIVEN {
        PLAYER(SPECIES_NINJASK) { Speed(200); }
        PLAYER(SPECIES_SNORLAX) { HP(1); Speed(50); }
        PLAYER(SPECIES_BLISSEY) { Speed(60); }
        OPPONENT(SPECIES_BLASTOISE) { Speed(100); }
    } WHEN {
        TURN { MOVE(player, MOVE_BATON_PASS); SEND_OUT(player, 1); MOVE(opponent, MOVE_TACKLE); SEND_OUT(player, 2); }
        TURN { MOVE(player, MOVE_SOFT_BOILED); }
    } SCENE {
        ANIMATION(ANIM_TYPE_MOVE, MOVE_BATON_PASS, player);
    } THEN {
        FORCE_MOVE_ANIM(FALSE);
    }
}
