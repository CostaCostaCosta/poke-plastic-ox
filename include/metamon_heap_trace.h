#ifndef GUARD_METAMON_HEAP_TRACE_H
#define GUARD_METAMON_HEAP_TRACE_H

#ifndef METAMON_HEAP_TRACE
#define METAMON_HEAP_TRACE 0
#endif

enum MmHeapEvent { MM_HEAP_RESET, MM_HEAP_ALLOC, MM_HEAP_FREE, MM_HEAP_MARK };
enum MmHeapPhase {
    MM_HEAP_OTHER, MM_HEAP_BATTLE_START, MM_HEAP_RESOURCES,
    MM_HEAP_LINK_BUFFERS, MM_HEAP_GRAPHICS, MM_HEAP_READY,
    MM_HEAP_DECISION, MM_HEAP_DECISION_END, MM_HEAP_TEARDOWN,
    MM_HEAP_RESOURCES_FREED, MM_HEAP_PARTY_MENU, MM_HEAP_SUMMARY,
    MM_HEAP_ACTION_COMMITTED,
};

#if METAMON_HEAP_TRACE
#define MM_HEAP_TRACE_CAPACITY 512
struct MmHeapTraceEvent {
    u32 kind, frame, address, size, location, phase;
};
extern volatile struct MmHeapTraceEvent gMetamonHeapTrace[MM_HEAP_TRACE_CAPACITY];
extern volatile u32 gMetamonHeapTraceCount;
void MmHeapRecord(u32 kind, const void *address, u32 size, const char *location);
void MmHeapMark(u32 phase);
#else
#define MmHeapRecord(...) ((void)0)
#define MmHeapMark(...) ((void)0)
#endif

#endif
