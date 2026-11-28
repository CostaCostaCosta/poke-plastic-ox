#include "global.h"
#include "fieldmap.h"
#include "plastic_ox_borders.h"
#include "constants/layouts.h"

// A rectangle of camera margin, in map coordinates (inclusive), and the
// metatiles to draw there on even and odd columns. First match wins.
// plastic_ox/alpha/route110_seams.py documents the seams these dress;
// plastic_ox/alpha/lavender_tower_crown.py the Lavender tower crown.
struct BorderZone
{
    u16 layoutId;
    s16 left, right, top, bottom;
    u16 evenColumn, oddColumn;
};

#define LO (-0x4000)
#define HI 0x4000
#define ONE(id) id, id
#define TOWER(x, y, id) {LAYOUT_LAVENDER_TOWN_HNS, x, x, y, y, ONE(id)}

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
    // Lavender Town, north: the tower's dome, spire and roof ledge, which
    // the layout crops (plastic_ox/alpha/lavender_tower_crown.py).
    TOWER(21, -6, 0x3CB), TOWER(22, -6, 0x3CC), TOWER(23, -6, 0x3CD),
    TOWER(19, -5, 0x3CE), TOWER(20, -5, 0x3CF), TOWER(21, -5, 0x3D0), TOWER(22, -5, 0x3D1), TOWER(23, -5, 0x3D2), TOWER(24, -5, 0x3D3), TOWER(25, -5, 0x3D4),
    TOWER(19, -4, 0x3D5), TOWER(20, -4, 0x3D6), TOWER(21, -4, 0x3D7), TOWER(22, -4, 0x3D8), TOWER(23, -4, 0x3D9), TOWER(24, -4, 0x3DA), TOWER(25, -4, 0x3DB),
    TOWER(19, -3, 0x3DC), TOWER(20, -3, 0x2BA), TOWER(21, -3, 0x2BB), TOWER(22, -3, 0x2BC), TOWER(23, -3, 0x2BD), TOWER(24, -3, 0x2BE), TOWER(25, -3, 0x3DD),
    TOWER(19, -2, 0x2C1), TOWER(20, -2, 0x2C2), TOWER(21, -2, 0x2C3), TOWER(22, -2, 0x2C4), TOWER(23, -2, 0x2C5), TOWER(24, -2, 0x2C6), TOWER(25, -2, 0x2C7),
    TOWER(19, -1, 0x2C9), TOWER(20, -1, 0x2CA), TOWER(21, -1, 0x2CB), TOWER(22, -1, 0x2CC), TOWER(23, -1, 0x2CD), TOWER(24, -1, 0x2CE), TOWER(25, -1, 0x2CF),
    // Lavender Town, north: cliff faces either side of the Route 110 road.
    {LAYOUT_LAVENDER_TOWN_HNS, 11, 11, LO, -1, ONE(0x072)},
    {LAYOUT_LAVENDER_TOWN_HNS, 17, 17, LO, -1, ONE(0x070)},
    // Route 36, east: finish the tree rows above and below the road.
    {LAYOUT_ROUTE36_HNS, 66, HI, 17, 17, 0x024, 0x025},
    {LAYOUT_ROUTE36_HNS, 66, HI, 23, 23, 0x020, 0x021},
    {LAYOUT_ROUTE36_HNS, 66, HI, 24, 24, 0x01A, 0x01B},
    // Route 103, east: the sand road (rows 9..10) runs on toward Route 7
    // between grass verges, instead of ending in the forest border. Rows
    // 8..11 are one whole border tree pair, so no tree is sliced.
    {LAYOUT_ROUTE103, 80, HI,  8,  8, ONE(0x001)},
    {LAYOUT_ROUTE103, 80, HI,  9,  9, ONE(0x119)},
    {LAYOUT_ROUTE103, 80, HI, 10, 10, ONE(0x129)},
    {LAYOUT_ROUTE103, 80, HI, 11, 11, ONE(0x001)},
    // Route 7, west: the road (rows 4..7) runs on toward Route 103 under
    // the tree line, whose bottom row (3) keeps the layout's own edge.
    {LAYOUT_ROUTE7_HNS, LO, -1,  3,  3, 0x024, 0x025},
    {LAYOUT_ROUTE7_HNS, LO, -1,  4,  4, 0x008, 0x009},
    {LAYOUT_ROUTE7_HNS, LO, -1,  5,  5, 0x010, 0x011},
    {LAYOUT_ROUTE7_HNS, LO, -1,  6,  6, 0x008, 0x009},
    {LAYOUT_ROUTE7_HNS, LO, -1,  7,  7, 0x010, 0x011},
    // Goldenrod City, south: the avenue (columns 31..34) runs on toward
    // Route 33 through the forest border, with a verge where a tree pair
    // would be sliced (30, 35).
    {LAYOUT_GOLDENROD_CITY_HNS, 30, 30, 46, HI, ONE(0x008)},
    {LAYOUT_GOLDENROD_CITY_HNS, 31, 31, 46, HI, ONE(0x3D0)},
    {LAYOUT_GOLDENROD_CITY_HNS, 32, 33, 46, HI, ONE(0x3D1)},
    {LAYOUT_GOLDENROD_CITY_HNS, 34, 34, 46, HI, ONE(0x3D2)},
    {LAYOUT_GOLDENROD_CITY_HNS, 35, 35, 46, HI, ONE(0x009)},
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
