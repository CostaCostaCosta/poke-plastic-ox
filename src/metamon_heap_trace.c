#include "global.h"
#include "metamon_heap_trace.h"

#if METAMON_HEAP_TRACE
#include "battle.h"
#include "main.h"

/* Profiling builds only. Outside gHeap so logging never changes heap layout.
 * The host drains each frame and rejects any overwritten/unread events. */
EWRAM_DATA volatile struct MmHeapTraceEvent gMetamonHeapTrace[MM_HEAP_TRACE_CAPACITY] = {0};
EWRAM_DATA volatile u32 gMetamonHeapTraceCount = 0;
static EWRAM_DATA u32 sPhase = 0;

void MmHeapRecord(u32 kind, const void *address, u32 size, const char *location)
{
    volatile struct MmHeapTraceEvent *e = &gMetamonHeapTrace[gMetamonHeapTraceCount % MM_HEAP_TRACE_CAPACITY];
    e->kind = kind;
    e->frame = gMain.vblankCounter1;
    e->address = (uintptr_t)address;
    e->size = size;
    e->location = (uintptr_t)location;
    e->phase = sPhase;
    gMetamonHeapTraceCount++; // Publish only after the complete record is written.
}

void MmHeapMark(u32 phase)
{
    sPhase = phase;
    MmHeapRecord(MM_HEAP_MARK, (void *)gBattleTypeFlags, 0, NULL);
}
#endif
