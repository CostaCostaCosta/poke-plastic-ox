#ifndef GUARD_PLASTIC_OX_BORDERS_H
#define GUARD_PLASTIC_OX_BORDERS_H

// Some layouts need more than one repeating border: Route 110 is ocean to the
// east but forest on every side that joins another map. Returns TRUE and the
// metatile id to draw when (x, y), in map coordinates outside the layout,
// falls in an authored zone of the current layout.
bool32 PlasticOx_GetBorderOverride(s32 x, s32 y, u16 *metatileId);

#endif // GUARD_PLASTIC_OX_BORDERS_H
