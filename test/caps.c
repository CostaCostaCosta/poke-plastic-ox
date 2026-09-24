#include "global.h"
#include "caps.h"
#include "event_data.h"
#include "test/test.h"

static void SetBadgeCount(u32 badgeCount)
{
    u32 i;

    for (i = 0; i < NUM_BADGES; i++)
    {
        if (i < badgeCount)
            FlagSet(FLAG_BADGE01_GET + i);
        else
            FlagClear(FLAG_BADGE01_GET + i);
    }
}

TEST("Plastic Ox level caps advance after each of the first six Gyms")
{
    static const u8 sExpectedCaps[] = {13, 20, 30, 36, 42, 50};
    u32 badgeCount;

    for (badgeCount = 0; badgeCount < ARRAY_COUNT(sExpectedCaps); badgeCount++)
    {
        SetBadgeCount(badgeCount);
        EXPECT_EQ(GetCurrentLevelCap(), sExpectedCaps[badgeCount]);
    }

    SetBadgeCount(6);
    EXPECT_EQ(GetCurrentLevelCap(), MAX_LEVEL);
}

TEST("Plastic Ox hard level cap prevents EXP gain at the current cap")
{
    SetBadgeCount(0);
    EXPECT_EQ(GetSoftLevelCapExpValue(12, 100), 100);
    EXPECT_EQ(GetSoftLevelCapExpValue(13, 100), 0);
    EXPECT_EQ(GetSoftLevelCapExpValue(14, 100), 0);
}
