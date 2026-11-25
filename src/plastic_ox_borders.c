#include "global.h"
#include "fieldmap.h"
#include "plastic_ox_borders.h"
#include "constants/layouts.h"

// A rectangle of camera margin, in map coordinates (inclusive), and the
// metatiles to draw there on even and odd columns. First match wins.
// plastic_ox/alpha/route110_seams.py documents the seams these dress.
struct BorderZone
{
    u16 layoutId;
    s16 left, right, top, bottom;
    u16 evenColumn, oddColumn;
};

#define LO (-0x4000)
#define HI 0x4000
#define ONE(id) id, id

static const struct BorderZone sBorderZones[] =
{
    // Route 110, north-west: forest around the Fortree corridor (rows 2..5).
    {LAYOUT_ROUTE110, LO, -1,   1,   1, ONE(0x017)}, // tree bases over the corridor
    {LAYOUT_ROUTE110, LO, -1,  19,  19, ONE(0x017)},
    {LAYOUT_ROUTE110, LO, -1,  20,  20, ONE(0x189)}, // shore under the forest
    {LAYOUT_ROUTE110, LO, -1,  LO,  18, ONE(0x0C7)},
    {LAYOUT_ROUTE110,  0, 35,  LO,  -1, ONE(0x0C7)},
    {LAYOUT_ROUTE110, 36, 36,  LO,  -1, ONE(0x190)}, // east shoreline
    // Route 110, west spur to Route 36: the ridge, then forest.
    {LAYOUT_ROUTE110, LO, -1,  59,  59, ONE(0x173)},
    {LAYOUT_ROUTE110, LO, -1,  60,  60, ONE(0x071)},
    {LAYOUT_ROUTE110, LO, -1,  61,  61, ONE(0x06C)},
    {LAYOUT_ROUTE110, LO, -1,  62,  62, ONE(0x071)},
    {LAYOUT_ROUTE110, LO, -1,  63,  63, ONE(0x07C)},
    {LAYOUT_ROUTE110, LO, -1,  64,  64, ONE(0x0CE)},
    {LAYOUT_ROUTE110, LO, -1,  65,  65, ONE(0x0C6)},
    {LAYOUT_ROUTE110, LO, -1,  66,  66, ONE(0x016)},
    {LAYOUT_ROUTE110, LO, -1,  67,  HI, ONE(0x0C7)},
    // Route 110, south: forest either side of the Lavender road.
    {LAYOUT_ROUTE110,  0, 35, 100,  HI, ONE(0x0C7)},
    {LAYOUT_ROUTE110, 36, 36, 100,  HI, ONE(0x190)},
    // Fortree City, east: tree bases over the Route 110 corridor.
    {LAYOUT_FORTREE_CITY, 40, HI, 6, 6, ONE(0x017)},
    // Lavender Town, north: cliff faces either side of the Route 110 road.
    {LAYOUT_LAVENDER_TOWN_HNS, 11, 11, LO, -1, ONE(0x072)},
    {LAYOUT_LAVENDER_TOWN_HNS, 17, 17, LO, -1, ONE(0x070)},
    // Route 36, east: finish the tree rows above and below the road.
    {LAYOUT_ROUTE36_HNS, 66, HI, 17, 17, 0x024, 0x025},
    {LAYOUT_ROUTE36_HNS, 66, HI, 23, 23, 0x020, 0x021},
    {LAYOUT_ROUTE36_HNS, 66, HI, 24, 24, 0x01A, 0x01B},
};

bool32 PlasticOx_GetBorderOverride(s32 x, s32 y, u16 *metatileId)
{
    u32 i;
    u16 layoutId = gMapHeader.mapLayoutId;

    for (i = 0; i < ARRAY_COUNT(sBorderZones); i++)
    {
        const struct BorderZone *zone = &sBorderZones[i];

        if (zone->layoutId == layoutId
         && x >= zone->left && x <= zone->right
         && y >= zone->top && y <= zone->bottom)
        {
            *metatileId = (x & 1) ? zone->oddColumn : zone->evenColumn;
            return TRUE;
        }
    }
    return FALSE;
}
