#ifndef GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H
#define GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H

// Plastic Ox alpha flags (emerald build only).
//
// Allocation: the documented-unused general-flag run 0x264-0x2BB in
// constants/flags.h (FLAG_UNUSED_0x264 .. FLAG_UNUSED_0x2BB). Every value
// here MUST stay inside that range: FLAGS_COUNT (= DAILY_FLAGS_END + 1)
// sizes the save-block flag array, so anything at or above it would write
// out of bounds, and the 0x500+ / 0x920+ sub-ranges belong to trainer and
// daily flags.

#define POX_FLAGS_START 0x264

// Story beats, one per completed beat (see plastic_ox/alpha/STORY_TRIGGERS.md).
#define FLAG_POX_STORY_STARTER   (POX_FLAGS_START + 0x00)
#define FLAG_POX_STORY_ILEX      (POX_FLAGS_START + 0x01)
#define FLAG_POX_STORY_MTMOON    (POX_FLAGS_START + 0x02)
#define FLAG_POX_STORY_WEATHER   (POX_FLAGS_START + 0x03)
#define FLAG_POX_STORY_MANSION   (POX_FLAGS_START + 0x04)
#define FLAG_POX_STORY_SILPH     (POX_FLAGS_START + 0x05)
#define FLAG_POX_TRIGGERS_ENABLED (POX_FLAGS_START + 0x06)

// Trigger-build-only NPCs hidden in the walkable build (and re-hidden/removed
// by their story beats in the trigger build).
#define FLAG_POX_HIDE_R29_GUARD         (POX_FLAGS_START + 0x0C) // beat 0: R29 gate guard leaves once starter is chosen
#define FLAG_POX_HIDE_MTMOON_GRUNT_1    (POX_FLAGS_START + 0x0D) // beat 5: Rocket I
#define FLAG_POX_HIDE_MTMOON_GRUNT_2    (POX_FLAGS_START + 0x0E)
#define FLAG_POX_HIDE_MTMOON_SCIENTIST  (POX_FLAGS_START + 0x0F)
#define FLAG_POX_HIDE_LAVENDER_GRUNT_1  (POX_FLAGS_START + 0x10) // beat 12: Rocket II tower floors
#define FLAG_POX_HIDE_LAVENDER_GRUNT_2  (POX_FLAGS_START + 0x11)
#define FLAG_POX_HIDE_SILPH_GRUNT_1     (POX_FLAGS_START + 0x12) // beat 16: Rocket III
#define FLAG_POX_HIDE_SILPH_GRUNT_2     (POX_FLAGS_START + 0x13)
#define FLAG_POX_HIDE_SILPH_GRUNT_3     (POX_FLAGS_START + 0x14)
#define FLAG_POX_HIDE_SILPH_GIOVANNI    (POX_FLAGS_START + 0x15)
#define FLAG_POX_HIDE_SAFFRON_GATE_NPC  (POX_FLAGS_START + 0x16) // beat 16: Blackthorn-route gate check NPC

// Item balls / hidden items for imported maps: allocate sequentially from
// POX_HIDDEN_ITEMS_BASE, one flag per placement (IMPORT_GUIDE section 2).
#define POX_HIDDEN_ITEMS_BASE           (POX_FLAGS_START + 0x1C) // 0x280; run ends at 0x2BB

// Wave 1C (Leg A) item placements.
#define FLAG_POX_HIDDEN_R29_POTION             (POX_HIDDEN_ITEMS_BASE + 0)
#define FLAG_POX_HIDDEN_R30_POTION_1           (POX_HIDDEN_ITEMS_BASE + 1)
#define FLAG_POX_HIDDEN_R30_POTION_2           (POX_HIDDEN_ITEMS_BASE + 2)
#define FLAG_POX_HIDDEN_R31_POKEBALL           (POX_HIDDEN_ITEMS_BASE + 3)
#define FLAG_POX_HIDDEN_R31_ANTIDOTE           (POX_HIDDEN_ITEMS_BASE + 4)
#define FLAG_POX_HIDDEN_R46_REVIVE             (POX_HIDDEN_ITEMS_BASE + 5)
#define FLAG_POX_HIDDEN_DARKCAVE_POTION        (POX_HIDDEN_ITEMS_BASE + 6)
#define FLAG_POX_HIDDEN_DARKCAVE_REVIVE        (POX_HIDDEN_ITEMS_BASE + 7)
#define FLAG_POX_HIDDEN_DARKCAVE_MAXREVIVE     (POX_HIDDEN_ITEMS_BASE + 8)
#define FLAG_POX_HIDDEN_DARKCAVE_ELIXIR        (POX_HIDDEN_ITEMS_BASE + 9)
#define FLAG_POX_HIDDEN_DARKCAVE_MAXETHER      (POX_HIDDEN_ITEMS_BASE + 10)
#define FLAG_POX_HIDDEN_DARKCAVE_BLACKFLUTE    (POX_HIDDEN_ITEMS_BASE + 11)
#define FLAG_POX_HIDDEN_CHERRYGROVE_NUGGET_1   (POX_HIDDEN_ITEMS_BASE + 12)
#define FLAG_POX_HIDDEN_CHERRYGROVE_NUGGET_2   (POX_HIDDEN_ITEMS_BASE + 13)


// Wave 2 (Legs B+C) items/hidden.
#define FLAG_POX_HIDDEN_ILEXFOREST_13            (POX_HIDDEN_ITEMS_BASE + 14)
#define FLAG_POX_HIDDEN_ILEXFOREST_14            (POX_HIDDEN_ITEMS_BASE + 15)
#define FLAG_POX_HIDDEN_ILEXFOREST_15            (POX_HIDDEN_ITEMS_BASE + 16)
#define FLAG_POX_HIDDEN_ILEXFOREST_16            (POX_HIDDEN_ITEMS_BASE + 17)
#define FLAG_POX_HIDDEN_ILEXFOREST_7             (POX_HIDDEN_ITEMS_BASE + 18)
#define FLAG_POX_HIDDEN_ILEXFOREST_8             (POX_HIDDEN_ITEMS_BASE + 19)
#define FLAG_POX_HIDDEN_ILEXFOREST_9             (POX_HIDDEN_ITEMS_BASE + 20)
#define FLAG_POX_HIDDEN_MTMOON_CAVE_21           (POX_HIDDEN_ITEMS_BASE + 21)
#define FLAG_POX_HIDDEN_ROUTE14_23               (POX_HIDDEN_ITEMS_BASE + 22)
#define FLAG_POX_HIDDEN_ROUTE2_1                 (POX_HIDDEN_ITEMS_BASE + 23)
#define FLAG_POX_HIDDEN_ROUTE2_19                (POX_HIDDEN_ITEMS_BASE + 24)
#define FLAG_POX_HIDDEN_ROUTE2_5                 (POX_HIDDEN_ITEMS_BASE + 25)
#define FLAG_POX_HIDDEN_ROUTE34_17               (POX_HIDDEN_ITEMS_BASE + 26)
#define FLAG_POX_HIDDEN_ROUTE34_18               (POX_HIDDEN_ITEMS_BASE + 27)
#define FLAG_POX_HIDDEN_ROUTE3_20                (POX_HIDDEN_ITEMS_BASE + 28)
#define FLAG_POX_HIDDEN_ROUTE4_1                 (POX_HIDDEN_ITEMS_BASE + 29)
#define FLAG_POX_HIDDEN_ROUTE4_22                (POX_HIDDEN_ITEMS_BASE + 30)
#define FLAG_POX_HIDDEN_ROUTE4_5                 (POX_HIDDEN_ITEMS_BASE + 31)

// Wave 2 (Legs B+C) items/hidden.
#define FLAG_POX_HIDDEN_NATIONALPARK_NORMAL_14   (POX_HIDDEN_ITEMS_BASE + 14)
#define FLAG_POX_HIDDEN_ROUTE24_18               (POX_HIDDEN_ITEMS_BASE + 15)
#define FLAG_POX_HIDDEN_ROUTE25_19               (POX_HIDDEN_ITEMS_BASE + 16)
#define FLAG_POX_HIDDEN_ROUTE36_15               (POX_HIDDEN_ITEMS_BASE + 17)
#define FLAG_POX_HIDDEN_ROUTE38_16               (POX_HIDDEN_ITEMS_BASE + 18)
#define FLAG_POX_HIDDEN_ROUTE38_17               (POX_HIDDEN_ITEMS_BASE + 19)

// Wave 2 (Legs B+C) items/hidden.
#define FLAG_POX_HIDDEN_ROUTE6_3                 (POX_HIDDEN_ITEMS_BASE + 14)

// Wave 4 (Legs F+G) items/hidden.
#define FLAG_POX_HIDDEN_ROUTE12_14               (POX_HIDDEN_ITEMS_BASE + 200)
#define FLAG_POX_HIDDEN_ROUTE12_15               (POX_HIDDEN_ITEMS_BASE + 201)
#define FLAG_POX_HIDDEN_ROUTE12_7                (POX_HIDDEN_ITEMS_BASE + 202)
#define FLAG_POX_HIDDEN_ROUTE12_9                (POX_HIDDEN_ITEMS_BASE + 203)
#define FLAG_POX_HIDDEN_ROUTE21_16               (POX_HIDDEN_ITEMS_BASE + 204)
#define FLAG_POX_HIDDEN_ROUTE21_17               (POX_HIDDEN_ITEMS_BASE + 205)
#define FLAG_POX_HIDDEN_ROUTE21_18               (POX_HIDDEN_ITEMS_BASE + 206)
#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H
