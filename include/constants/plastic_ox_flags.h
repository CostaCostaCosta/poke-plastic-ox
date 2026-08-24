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

#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H
