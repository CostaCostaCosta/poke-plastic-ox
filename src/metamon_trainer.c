#include "global.h"
#include "battle.h"
#include "battle_setup.h"
#include "battle_controllers.h"
#include "battle_interface.h"
#include "battle_util.h"
#include "battle_script_commands.h"
#include "malloc.h"
#include "metamon_trainer.h"
#include "pokemon.h"
#include "party_menu.h"
#include "constants/party_menu.h"
#include "constants/abilities.h"
#include "constants/moves.h"
#include "test_runner.h"
#include "../plastic_ox/battle/metamon/runtime.h"
#include "../plastic_ox/battle/metamon/model/public_data.inc"

/* The policy controls every ordinary single-battle trainer in the game.
 * The game is Gen 3 only (species, moves, items, abilities), so the export's
 * vocab windows (species 386, moves 354, items 799, abilities 76) always hold.
 * Any extra battle-type bits (doubles, link, frontier, recorded, safari,
 * partner) keep the standard AI. */
struct MmPublicMon {
    u16 species, item, ability, moves[4], lastMove;
    u16 first, lastActive, lastMoveTurn, switches, hpTurn;
    float hp[2];
    u16 volatileKnown, volatileValue;
    u8 key, level, status, active, seen, fainted, moved, transformed;
    u8 hpKnown, removed, consumed, pp[4], maxpp[4];
    s8 boosts[7];
    u8 types[2];
};
struct MmEvent { s16 cat[6]; float num[24]; u8 flags; };
struct MmBattleArena {
    MmObservation obs;
    MmWorkspace work;
    float hidden[MM_HIDDEN], logits[MM_ACTIONS];
    MmJob job;
    struct MmPublicMon mons[12];
    struct MmEvent events[4], pending;
    u16 decisions, turn, lastSwitch[2], switchCount[2], lastReveal, lastKO, weatherTurn;
    u8 revealed, active[2], moveMap[4], switchMap[5];
    u8 state, action, forced, called, eventsCount, weather, spikes[2], screens[2], blocked, retry;
    u32 guard;
};
static EWRAM_DATA struct MmBattleArena *sMetamon = NULL;
/* Emulator-readable counters; never consulted by policy or stored in save data. */
EWRAM_DATA u32 gMetamonDecisions = 0;
EWRAM_DATA u32 gMetamonFrames = 0;
const u32 gMetamonArenaBytes = sizeof(struct MmBattleArena);
EWRAM_DATA u32 gMetamonFault = 0;
EWRAM_DATA u32 gMetamonCommits = 0;
EWRAM_DATA u32 gMetamonMoves = 0;
EWRAM_DATA u32 gMetamonSwitches = 0;
EWRAM_DATA u32 gMetamonReplacements = 0;
/* Read-only ABI for emulator validation. Derive every offset from this build. */
const u32 gMetamonTestLayout[] = {
    offsetof(struct MmBattleArena, hidden), offsetof(struct MmBattleArena, logits),
    offsetof(struct MmBattleArena, state), offsetof(struct MmBattleArena, decisions),
    offsetof(struct MmBattleArena, action), offsetof(struct MmBattleArena, mons),
    sizeof(struct BattlePokemon), offsetof(struct BattlePokemon, moves),
    offsetof(struct BattlePokemon, item), offsetof(struct BattlePokemon, ability),
    offsetof(struct BattlePokemon, hp), offsetof(struct BattlePokemon, maxHP),
    offsetof(struct BattlePokemon, pp), offsetof(struct BattlePokemon, attack),
    offsetof(struct BattlePokemon, status1), offsetof(struct BattlePokemon, personality),
};

_Static_assert(sizeof(struct MmBattleArena) < 20*1024, "Metamon arena exceeds budget");

static void MonNum(MmObservation *o, u32 mon, u32 index, float value)
{
    if (index < 24) o->mon_num[mon][index] = value;
    else if (value) o->mon_flags[mon][(index-24)/32] |= 1u << ((index-24)%32);
}
static void GlobalNum(MmObservation *o, u32 index, float value)
{
    if (index < 32) o->global_num[index] = value;
    else if (value) o->global_flags[(index-32)/32] |= 1u << ((index-32)%32);
}
static u32 Side(u32 battler) { return IsOnPlayerSide(battler) ? 1 : 0; }
static u32 Status(u32 flags)
{
    if (flags & STATUS1_SLEEP) return 2;
    if (flags & STATUS1_TOXIC_POISON) return 7;
    if (flags & STATUS1_POISON) return 3;
    if (flags & STATUS1_BURN) return 4;
    if (flags & STATUS1_FREEZE) return 5;
    if (flags & STATUS1_PARALYSIS) return 6;
    return 0;
}
static struct MmPublicMon *Active(u32 battler)
{
    u32 side = Side(battler), index = sMetamon->active[side];
    return index < 12 && sMetamon->mons[index].seen ? &sMetamon->mons[index] : NULL;
}

bool32 MetamonControls(u32 battler) { return sMetamon && !IsOnPlayerSide(battler); }
bool32 MetamonBusy(void) { return sMetamon && sMetamon->state == 1; }

void MetamonBattleInit(void)
{
    sMetamon = NULL;
    gMetamonFault = gMetamonDecisions = gMetamonFrames = 0;
    gMetamonMoves = gMetamonSwitches = gMetamonReplacements = gMetamonCommits = 0;
    if ((gBattleTypeFlags & ~BATTLE_TYPE_IS_MASTER) != BATTLE_TYPE_TRAINER) return;
    /* Keep the deterministic standard AI under the ROM test runner. */
    if (gTestRunnerEnabled) return;
    sMetamon = AllocZeroed(sizeof(*sMetamon));
    sMetamon->active[0] = sMetamon->active[1] = 255;
    sMetamon->lastKO = sMetamon->lastReveal = 65535;
    sMetamon->lastSwitch[0] = sMetamon->lastSwitch[1] = 65535;
    sMetamon->guard = 0x4D4D314D;
}
void MetamonBattleFree(void)
{
    if (sMetamon) {
        fatal_assertf(sMetamon->guard == 0x4D4D314D);
        FREE_AND_SET_NULL(sMetamon);
    }
}

void MetamonPublicSwitch(u32 battler)
{
    struct MmPublicMon *m;
    u32 i, side, key;
    if (!sMetamon || battler >= 2) return;
    side = Side(battler); key = gBattlerPartyIndexes[battler];
    if (key >= 6 || gBattleMons[battler].species > 386) return;
    if (!side) i = key;
    else {
        for (i = 6; i < 6+sMetamon->revealed; ++i)
            if (sMetamon->mons[i].key == key) break;
        if (i == 12) { gMetamonFault = 1; return; }
        if (i == 6+sMetamon->revealed) {
            ++sMetamon->revealed;
            sMetamon->lastReveal = sMetamon->turn;
            sMetamon->pending.flags |= 128;
        }
    }
    m = &sMetamon->mons[i];
    if (m->active && sMetamon->active[side] == i) return;
    if (!m->seen) {
        m->first = sMetamon->turn;
        m->item = m->ability = 1;
        m->lastMove = 1;
    }
    for (u32 j = side*6; j < side*6+6; ++j) {
        if (sMetamon->mons[j].active) sMetamon->mons[j].lastActive = sMetamon->turn;
        sMetamon->mons[j].active = FALSE;
    }
    m->seen = m->active = TRUE; m->key = key;
    m->species = gBattleMons[battler].species;
    m->level = gBattleMons[battler].level;
    m->types[0] = sSpeciesInfo[m->species].types[0];
    m->types[1] = sSpeciesInfo[m->species].types[1];
    m->lastActive = sMetamon->turn;
    m->volatileKnown = m->volatileValue = 0;
    memset(m->boosts, 0, sizeof(m->boosts));
    sMetamon->blocked = 0;
    ++m->switches; ++sMetamon->switchCount[side];
    sMetamon->lastSwitch[side] = sMetamon->turn;
    sMetamon->active[side] = i;
    sMetamon->pending.flags |= 1u << (3+side);
    sMetamon->pending.cat[4+side] = 3;
    MetamonPublicHP(battler);
}
void MetamonPublicHP(u32 battler)
{
    struct MmPublicMon *m;
    float lo, hi, delta;
    u32 side, pixels, hp, maxhp;
    if (!sMetamon || battler >= 2 || !(m = Active(battler))) return;
    side = Side(battler);
    hp = gBattleMons[battler].hp; maxhp = gBattleMons[battler].maxHP;
    if (!maxhp) return;
    if (!side) lo = hi = (float)hp / maxhp;
    else {
        /* Match the displayed 48-pixel bar, then conservatively widen to
         * sixteenths. No exact opposing HP is stored or used downstream. */
        pixels = GetScaledHPFraction(hp, maxhp, 48);
        lo = pixels <= 1 ? 0 : (float)(pixels/3)/16;
        hi = pixels == 0 ? 0 : pixels >= 48 ? 1 : (float)((pixels+3)/3)/16;
    }
    delta = (lo+hi-m->hp[0]-m->hp[1])*0.5f;
    if (m->hpKnown && delta != 0) {
        u32 index = side + (delta > 0 ? 2 : 0);
        sMetamon->pending.num[index] += delta > 0 ? delta : -delta;
        sMetamon->pending.num[index+12] = 1;
    }
    m->hp[0] = lo; m->hp[1] = hi; m->hpTurn = sMetamon->turn; m->hpKnown = TRUE;
    u32 status = Status(gBattleMons[battler].status1);
    if (status != m->status) {
        sMetamon->pending.num[11] = (status+(side ? 10 : 0))/20.0f;
        sMetamon->pending.num[23] = 1;
    }
    m->status = status;
    if (!hp && !m->fainted) {
        m->fainted = TRUE; m->status = 8;
        sMetamon->lastKO = sMetamon->turn;
        sMetamon->pending.flags |= 1u << (1+side);
    }
}
void MetamonPublicMove(u32 battler, u32 move)
{
    struct MmPublicMon *m;
    u32 side, i;
    if (!sMetamon || battler >= 2 || move > 354 || !(m = Active(battler))) return;
    side = Side(battler);
    m->lastMove = move+1; m->lastMoveTurn = sMetamon->turn; m->moved = TRUE;
    sMetamon->pending.cat[2+side] = move+1;
    sMetamon->pending.cat[4+side] = 2;
    if (!sMetamon->called && !m->transformed) {
        for (i = 0; i < 4 && m->moves[i] && m->moves[i] != move; ++i) {}
        if (i < 4 && !m->moves[i]) {
            m->moves[i] = move;
            sMetamon->pending.flags |= 128;
        }
    }
}
void MetamonMoveStart(void) { if (sMetamon) sMetamon->called = FALSE; }
void MetamonCalledMove(void) { if (sMetamon) sMetamon->called = TRUE; }
void MetamonPublicAbility(u32 battler, u32 ability)
{
    struct MmPublicMon *m;
    if (sMetamon && battler < 2 && ability <= 76 && (m = Active(battler))) {
        m->ability = ability+1; sMetamon->pending.flags |= 128;
    }
}
void MetamonPublicItem(u32 battler, u32 item)
{
    struct MmPublicMon *m;
    if (sMetamon && battler < 2 && item < 799 && (m = Active(battler))) {
        m->item = item ? item+1 : 0;
        if (!item) m->removed = TRUE;
        sMetamon->pending.flags |= 128;
    }
}

static void SortMoves(u16 moves[4], u8 *map)
{
    for (u32 i = 0; i < 4; ++i) {
        if (map) map[i] = i;
        if (moves[i] > 354) moves[i] = 0;
    }
    for (u32 i = 0; i < 4; ++i)
        for (u32 j = i+1; j < 4; ++j)
            if (moves[j] && (!moves[i] || sMoveInfo[moves[j]].rank < sMoveInfo[moves[i]].rank)) {
                u16 temp = moves[i]; moves[i] = moves[j]; moves[j] = temp;
                if (map) { u8 x = map[i]; map[i] = map[j]; map[j] = x; }
            }
}

static void EncodeMon(u32 slot, struct MmPublicMon *m, u32 nativeIndex, u32 battler)
{
    MmObservation *o = &sMetamon->obs;
    struct Pokemon *own = slot < 6 ? &gParties[B_TRAINER_OPPONENT_A][nativeIndex] : NULL;
    u16 moves[4];
    u32 active = own && nativeIndex == gBattlerPartyIndexes[battler];
    static const u8 stats[] = {MON_DATA_ATK, MON_DATA_SPATK, MON_DATA_DEF, MON_DATA_SPDEF, MON_DATA_SPEED, MON_DATA_MAX_HP};
    if (own) {
        m->species = GetMonData(own, MON_DATA_SPECIES);
        if (!m->species || m->species > 386) return;
        m->level = GetMonData(own, MON_DATA_LEVEL);
        m->item = active ? gBattleMons[battler].item : GetMonData(own, MON_DATA_HELD_ITEM);
        m->item = m->item ? m->item+1 : 0;
        m->ability = (active ? gBattleMons[battler].ability : GetMonAbility(own))+1;
        m->status = Status(active ? gBattleMons[battler].status1 : GetMonData(own, MON_DATA_STATUS));
        m->hp[0] = m->hp[1] = (float)(active ? gBattleMons[battler].hp : GetMonData(own, MON_DATA_HP)) / GetMonData(own, MON_DATA_MAX_HP);
        m->fainted = m->hp[0] == 0; if (m->fainted) m->status = 8;
        m->hpTurn = sMetamon->turn;
        m->types[0] = sSpeciesInfo[m->species].types[0];
        m->types[1] = sSpeciesInfo[m->species].types[1];
        for (u32 i = 0; i < 4; ++i) moves[i] = active ? gBattleMons[battler].moves[i] : GetMonData(own, MON_DATA_MOVE1+i);
        u16 currentStats[] = {gBattleMons[battler].attack, gBattleMons[battler].spAttack,
            gBattleMons[battler].defense, gBattleMons[battler].spDefense,
            gBattleMons[battler].speed, gBattleMons[battler].maxHP};
        for (u32 i = 0; i < 6; ++i) {
            MonNum(o, slot, 3+i, (float)(active ? currentStats[i] : GetMonData(own, stats[i]))/1024);
            MonNum(o, slot, 27+i, 1);
        }
    } else {
        if (!m->seen) return;
        memcpy(moves, m->moves, sizeof(moves));
    }
    SortMoves(moves, slot == 0 ? sMetamon->moveMap : NULL);
    o->mon_cat[slot][0] = m->species+1;
    o->mon_cat[slot][1] = m->item; o->mon_cat[slot][2] = m->ability;
    o->mon_cat[slot][3] = m->status; o->mon_cat[slot][4] = m->lastMove ? m->lastMove : 1;
    o->mon_cat[slot][5] = m->types[0]; o->mon_cat[slot][6] = m->types[1];
    MonNum(o, slot, 0, m->hp[0]); MonNum(o, slot, 1, m->hp[1]);
    MonNum(o, slot, 2, m->level/100.0f);
    for (u32 i = 24; i < 27; ++i) MonNum(o, slot, i, 1);
    for (u32 i = 0; i < 7; ++i) {
        MonNum(o, slot, 9+i, m->boosts[i]/6.0f);
        MonNum(o, slot, 33+i, m->active);
    }
    MonNum(o, slot, 16, m->first/1024.0f); MonNum(o, slot, 40, 1);
    MonNum(o, slot, 17, m->active ? 0 : (sMetamon->turn-m->lastActive)/1024.0f); MonNum(o, slot, 41, 1);
    if (m->moved) { MonNum(o, slot, 18, (sMetamon->turn-m->lastMoveTurn)/1024.0f); MonNum(o, slot, 42, 1); }
    MonNum(o, slot, 19, m->switches/1024.0f); MonNum(o, slot, 43, 1);
    MonNum(o, slot, 22, (sMetamon->turn-m->hpTurn)/1024.0f); MonNum(o, slot, 46, 1);
    MonNum(o, slot, 48, 1); MonNum(o, slot, 49, 1); MonNum(o, slot, 50, 1);
    MonNum(o, slot, 51, m->fainted); MonNum(o, slot, 52, m->active);
    MonNum(o, slot, 53, m->item != 1); MonNum(o, slot, 54, m->ability != 1);
    MonNum(o, slot, 55, m->removed); MonNum(o, slot, 56, m->removed);
    MonNum(o, slot, 57, m->consumed); MonNum(o, slot, 58, m->consumed);
    MonNum(o, slot, 59, own != NULL); MonNum(o, slot, 60, m->transformed);
    MonNum(o, slot, 61, !own && !m->active); MonNum(o, slot, 62, own != NULL); MonNum(o, slot, 63, 1);
    for (u32 i = 0; i < 16; ++i) {
        MonNum(o, slot, 64+i, (m->volatileValue >> i)&1);
        MonNum(o, slot, 80+i, (m->volatileKnown >> i)&1);
    }
    for (u32 i = 0; i < 4; ++i) {
        u32 move = moves[i];
        if (!move) continue;
        const struct MmMoveInfo *info = &sMoveInfo[move];
        o->move_cat[slot][i][0] = move+1;
        o->move_cat[slot][i][1] = info->type; o->move_cat[slot][i][2] = info->category;
        o->move_num[slot][i][0] = info->power; o->move_num[slot][i][1] = info->accuracy; o->move_num[slot][i][2] = info->priority;
        o->move_flags[slot][i] = info->flags;
        if (slot == 0) {
            u32 native = sMetamon->moveMap[i];
            u32 maxpp = CalculatePPWithBonus(move, gBattleMons[battler].ppBonuses, native);
            m->pp[i] = gBattleMons[battler].pp[native]; m->maxpp[i] = maxpp ? maxpp : 1;
        }
        if (own && m->maxpp[i]) {
            o->move_num[slot][i][3] = (float)m->pp[i]/m->maxpp[i];
            o->move_flags[slot][i] |= 1;
        }
        o->move_valid[slot] |= 1u << i;
    }
}

static void SnapshotPublic(u32 battler)
{
    static const u8 stats[] = {STAT_ATK, STAT_SPATK, STAT_DEF, STAT_SPDEF, STAT_SPEED, STAT_ACC, STAT_EVASION};
    for (u32 b = 0; b < 2; ++b) {
        struct MmPublicMon *m = Active(b);
        if (!m) continue;
        /* Only public on-field effects: no item/ability/moveset reads here. */
        for (u32 i = 0; i < 7; ++i) m->boosts[i] = (s32)gBattleMons[b].statStages[stats[i]]-6;
        m->status = m->fainted ? 8 : Status(gBattleMons[b].status1);
        if (!m->transformed && gBattleMons[b].volatiles.transformed && Side(b))
            memset(m->moves, 0, sizeof(m->moves));
        m->transformed = gBattleMons[b].volatiles.transformed;
        u16 values = (!!gBattleMons[b].volatiles.confusionTurns << 0)
                   | (!!gBattleMons[b].volatiles.infatuation << 1)
                   | (!!gBattleMons[b].volatiles.leechSeed << 2)
                   | (!!gBattleMons[b].volatiles.cursed << 3)
                   | (!!gBattleMons[b].volatiles.nightmare << 4)
                   | (!!gBattleMons[b].volatiles.substitute << 5)
                   | (!!gBattleMons[b].volatiles.tauntTimer << 6)
                   | (!!gBattleMons[b].volatiles.encoreTimer << 7)
                   | (!!gBattleMons[b].volatiles.disabledMove << 8)
                   | (!!gBattleMons[b].volatiles.torment << 9)
                   | (!!gBattleMons[b].volatiles.root << 10)
                   | (!!gBattleMons[b].volatiles.perishSong << 11)
                   | (!!gProtectStructs[b].protected << 12)
                   | (!!gBattleMons[b].volatiles.semiInvulnerable << 13)
                   | (!!gBattleMons[b].volatiles.rechargeTimer << 14)
                   | (!!gBattleMons[b].volatiles.escapePrevention << 15);
        m->volatileKnown |= values | m->volatileValue;
        m->volatileValue = values;
    }
    u32 weather = 0;
    if (gBattleWeather & B_WEATHER_RAIN) weather = 1;
    else if (gBattleWeather & B_WEATHER_SUN) weather = 2;
    else if (gBattleWeather & B_WEATHER_SANDSTORM) weather = 3;
    else if (gBattleWeather & B_WEATHER_HAIL) weather = 4;
    if (weather != sMetamon->weather) {
        sMetamon->weatherTurn = sMetamon->turn; sMetamon->pending.flags |= 32;
    }
    sMetamon->weather = weather;
    for (u32 side = 0; side < 2; ++side) {
        u32 nativeSide = side ? B_SIDE_PLAYER : B_SIDE_OPPONENT;
        u32 spikes = gSideTimers[nativeSide].spikesAmount;
        if (spikes != sMetamon->spikes[side]) {
            sMetamon->pending.num[8+side] += ((s32)spikes-sMetamon->spikes[side])/3.0f;
            sMetamon->pending.flags |= 64;
        }
        sMetamon->spikes[side] = spikes;
        sMetamon->screens[side] = gSideStatuses[nativeSide] & 15;
    }
}

static bool32 BeginDecision(u32 battler, bool32 forced)
{
    MmObservation *o = &sMetamon->obs;
    struct Pokemon *party = gParties[B_TRAINER_OPPONENT_A];
    u8 order[6], n = 1, live = 0, fainted = 0;
    u32 limitations;
    if (sMetamon->retry) {
        sMetamon->retry = 0;
        for (u32 i = 4; i < 9; ++i) o->legal[i] = 0;
        o->global_flags[1] &= (1u << 27)-1;
        goto infer;
    }
    sMetamon->turn = gBattleTurnCounter+1;
    sMetamon->forced = forced;
    if (sMetamon->active[0] == 255) MetamonPublicSwitch(battler);
    if (sMetamon->active[1] == 255) MetamonPublicSwitch(B_POSITION_PLAYER_LEFT);
    SnapshotPublic(battler);
    if (sMetamon->decisions) {
        struct MmEvent *e = &sMetamon->pending;
        for (u32 i = 0; i < 2; ++i) e->cat[i] = sMetamon->mons[sMetamon->active[i]].species+1;
        e->flags |= 1;
        memmove(sMetamon->events, sMetamon->events+1, 3*sizeof(*e));
        sMetamon->events[3] = *e;
        if (sMetamon->eventsCount < 4) ++sMetamon->eventsCount;
    }
    memset(&sMetamon->pending, 0, sizeof(sMetamon->pending));
    ++sMetamon->decisions;
    memset(o, 0, sizeof(*o));
    memset(sMetamon->switchMap, 255, sizeof(sMetamon->switchMap));
    order[0] = gBattlerPartyIndexes[battler];
    /* Own legal switch candidates come first, in canonical species-name order. */
    for (u32 i = 0; i < 6; ++i) {
        if (GetMonData(&party[i], MON_DATA_SPECIES) && GetMonData(&party[i], MON_DATA_HP)) {
            ++live;
            if (i != order[0]) order[n++] = i;
        }
    }
    for (u32 i = 1; i < n; ++i)
        for (u32 j = i+1; j < n; ++j)
            if (sSpeciesInfo[GetMonData(&party[order[j]], MON_DATA_SPECIES)].rank < sSpeciesInfo[GetMonData(&party[order[i]], MON_DATA_SPECIES)].rank) {
                u8 tmp = order[i]; order[i] = order[j]; order[j] = tmp;
            }
    for (u32 i = 1; i < n; ++i) {
        sMetamon->switchMap[i-1] = order[i];
        o->legal[3+i] = forced || (!sMetamon->blocked && CanBattlerEscape(battler));
    }
    for (u32 i = 0; i < 6; ++i) {
        u32 j;
        for (j = 0; j < n && order[j] != i; ++j) {}
        if (j == n) order[n++] = i;
    }
    for (u32 i = 0; i < 6; ++i) EncodeMon(i, &sMetamon->mons[order[i]], order[i], battler);
    for (u32 i = 6; i < 12; ++i) {
        EncodeMon(i, &sMetamon->mons[i], 0, battler);
        fainted += sMetamon->mons[i].fainted;
    }
    limitations = forced ? 15 : CheckMoveLimitations(battler, 0, MOVE_LIMITATIONS_ALL);
    for (u32 i = 0; i < 4; ++i) o->legal[i] = !forced && o->move_cat[0][i][0] && !(limitations & (1u << sMetamon->moveMap[i]));
    if (!forced && limitations == 15) {
        /* Engine's Struggle request has one action. The move controller ignores
         * the chosen slot once no usable moves remains. */
        o->legal[0] = 1;
    }
    for (u32 i = 0; i < 4; ++i) {
        memcpy(o->event_cat[i], sMetamon->events[i].cat, sizeof(o->event_cat[i]));
        memcpy(o->event_num[i], sMetamon->events[i].num, sizeof(o->event_num[i]));
        o->event_flags[i] = sMetamon->events[i].flags;
    }
    GlobalNum(o, 0, sMetamon->turn/1024.0f); GlobalNum(o, 32, 1);
    GlobalNum(o, 1, sMetamon->decisions/1024.0f); GlobalNum(o, 33, 1);
    GlobalNum(o, 2, (sMetamon->turn-sMetamon->weatherTurn)/1024.0f); GlobalNum(o, 34, 1);
    GlobalNum(o, 4, sMetamon->spikes[0]/3.0f); GlobalNum(o, 36, 1);
    GlobalNum(o, 5, sMetamon->spikes[1]/3.0f); GlobalNum(o, 37, 1);
    GlobalNum(o, 6, live/6.0f); GlobalNum(o, 38, 1);
    GlobalNum(o, 7, fainted/6.0f); GlobalNum(o, 39, 1);
    GlobalNum(o, 8, 1); GlobalNum(o, 9, 1);
    GlobalNum(o, 10, sMetamon->revealed/6.0f);
    GlobalNum(o, 11, (6-sMetamon->revealed)/6.0f); GlobalNum(o, 12, (6-sMetamon->revealed)/6.0f);
    for (u32 i = 40; i < 45; ++i) GlobalNum(o, i, 1);
    u16 times[] = {sMetamon->lastKO, sMetamon->lastSwitch[0], sMetamon->lastSwitch[1], sMetamon->lastReveal};
    for (u32 i = 0; i < 4; ++i) if (times[i] != 65535) {
        GlobalNum(o, 13+i, (sMetamon->turn-times[i])/1024.0f); GlobalNum(o, 45+i, 1);
    }
    for (u32 side = 0; side < 2; ++side) {
        GlobalNum(o, 17+side, sMetamon->switchCount[side]/1024.0f); GlobalNum(o, 49+side, 1);
        for (u32 i = 0; i < 4; ++i) GlobalNum(o, 70+2*i+side, (sMetamon->screens[side] >> i)&1);
    }
    GlobalNum(o, 31, sMetamon->eventsCount/4.0f); GlobalNum(o, 63, 1);
    GlobalNum(o, 64+sMetamon->weather, 1);
    GlobalNum(o, 80, forced); GlobalNum(o, 83, 1); GlobalNum(o, 84, 1); GlobalNum(o, 85, 1);
    for (u32 i = 0; i < 9; ++i) GlobalNum(o, 87+i, o->legal[i]);
infer:
    if (!MmBegin(&sMetamon->job, o, sMetamon->hidden, sMetamon->logits, &sMetamon->work)) {
        gMetamonFault = 2;
        assertf(FALSE, "Invalid Metamon observation");
        return FALSE;
    }
    sMetamon->job.deferCommit = TRUE;
    sMetamon->state = 1;
    return TRUE;
}

static bool32 Decide(u32 battler, bool32 forced)
{
    u32 line;
    if (!sMetamon->state && !BeginDecision(battler, forced)) return FALSE;
    if (sMetamon->state == 2) return TRUE;
    fatal_assertf(sMetamon->guard == 0x4D4D314D);
    line = REG_VCOUNT;
    ++gMetamonFrames;
    /* One tile is at most six 384-wide dot products. Limit each callback
     * to 128 scanlines plus one tile, leaving time for sound and presentation. */
    do {
        if (MmStep(&sMetamon->job)) {
            sMetamon->action = MmChooseLegal(sMetamon->logits, sMetamon->obs.legal);
            fatal_assertf(sMetamon->action < 9);
            sMetamon->state = 2;
            ++gMetamonDecisions;
            return TRUE;
        }
    } while ((REG_VCOUNT+228-line)%228 < 128);
    return FALSE;
}

bool32 MetamonChooseAction(u32 battler)
{
    if (!MetamonControls(battler)) return FALSE;
    if (!Decide(battler, FALSE)) return TRUE;
    if (sMetamon->action >= 4) {
        u32 party = sMetamon->switchMap[sMetamon->action-4];
        fatal_assertf(party < 6);
        gBattleStruct->AI_monToSwitchIntoId[battler] = party;
        gBattleStruct->monToSwitchIntoId[battler] = party;
        BtlController_EmitTwoReturnValues(battler, B_COMM_TO_ENGINE, B_ACTION_SWITCH, 0);
        /* ChoosePokemon consumes this cached switch without another decision. */
    } else BtlController_EmitTwoReturnValues(battler, B_COMM_TO_ENGINE, B_ACTION_USE_MOVE, 0);
    BtlController_Complete(battler);
    return TRUE;
}
bool32 MetamonChooseMove(u32 battler)
{
    u32 slot, target, move;
    if (!MetamonControls(battler)) return FALSE;
    fatal_assertf(sMetamon->state == 2 && sMetamon->action < 4);
    slot = sMetamon->moveMap[sMetamon->action];
    move = gBattleMons[battler].moves[slot];
    target = GetBattlerMoveTargetType(battler, move) == TARGET_USER ? battler : B_POSITION_PLAYER_LEFT;
    BtlController_EmitTwoReturnValues(battler, B_COMM_TO_ENGINE, B_ACTION_EXEC_SCRIPT, slot | (target << 8));
    BtlController_Complete(battler);
    fatal_assertf(MmCommit(&sMetamon->job));
    ++gMetamonCommits;
    ++gMetamonMoves;
    sMetamon->state = 0; sMetamon->called = 0;
    return TRUE;
}
bool32 MetamonChoosePokemon(u32 battler)
{
    u32 party;
    if (!MetamonControls(battler)) return FALSE;
    if (gBattleResources->bufferA[battler][1] == PARTY_ACTION_CANT_SWITCH
     || gBattleResources->bufferA[battler][1] == PARTY_ACTION_ABILITY_PREVENTS) {
        /* This is the acting trainer's own rejected switch request. Preserve
         * its previous recurrent state and rerun the same snapshot with the
         * newly known switch unavailability; never inspect the hidden ability. */
        sMetamon->blocked = sMetamon->retry = 1;
        sMetamon->state = 0;
        BtlController_EmitChosenMonReturnValue(battler, B_COMM_TO_ENGINE, PARTY_SIZE, NULL);
        BtlController_Complete(battler);
        return TRUE;
    }
    if (!Decide(battler, TRUE)) return TRUE;
    fatal_assertf(sMetamon->action >= 4);
    party = sMetamon->switchMap[sMetamon->action-4];
    fatal_assertf(MmCommit(&sMetamon->job));
    ++gMetamonCommits;
    if (sMetamon->forced) ++gMetamonReplacements;
    else ++gMetamonSwitches;
    fatal_assertf(party < 6);
    gBattleStruct->monToSwitchIntoId[battler] = party;
    gBattleStruct->AI_monToSwitchIntoId[battler] = PARTY_SIZE;
    BtlController_EmitChosenMonReturnValue(battler, B_COMM_TO_ENGINE, party, NULL);
    BtlController_Complete(battler);
    sMetamon->state = 0; sMetamon->called = 0;
    return TRUE;
}
