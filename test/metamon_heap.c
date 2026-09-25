#include "global.h"
#include "malloc.h"
#include "test/test.h"

static u32 LargestFree(void)
{
    const struct MemBlock *head = HeapHead(), *p = head;
    u32 largest = 0;
    do {
        if (!p->allocated && p->size > largest) largest = p->size;
        p = p->next;
    } while (p != head);
    return largest;
}

TEST("Metamon heap: failed optional allocation preserves live data and heap")
{
    u32 i, before = LargestFree();
    u8 *state = AllocZeroedUnchecked(1536);
    EXPECT(state != NULL);
    for (i = 0; i < 1536; i++) state[i] = i;
    EXPECT(AllocUnchecked(HEAP_SIZE) == NULL);
    for (i = 0; i < 1536; i++) EXPECT_EQ(state[i], (u8)i);
    Free(state);
    EXPECT_EQ(LargestFree(), before);
}

TEST("Metamon heap: fragmented space fails until adjacent blocks are freed")
{
    void *fillers[32];
    u32 n = 0, before = LargestFree();
    void *a = Alloc(8192), *b = Alloc(8192), *c = Alloc(8192);
    while (LargestFree() && n < ARRAY_COUNT(fillers))
        fillers[n++] = Alloc(LargestFree());
    EXPECT_EQ(LargestFree(), 0);
    Free(a);
    Free(c);
    EXPECT_EQ(LargestFree(), 8192);
    EXPECT(AllocUnchecked(12288) == NULL);
    Free(b);
    a = AllocUnchecked(24576);
    EXPECT(a != NULL);
    Free(a);
    while (n) Free(fillers[--n]);
    EXPECT_EQ(LargestFree(), before);
}

TEST("Metamon heap: repeated decision buffers preserve recurrent state")
{
    u32 i, before = LargestFree();
    u32 *state = AllocZeroed(1536);
    for (i = 0; i < 64; ++i)
    {
        u8 *work = AllocUnchecked(39044); // observation + current scratch
        EXPECT(work != NULL);
        work[0] = i;
        work[39043] = ~i;
        EXPECT_EQ(state[0], i);
        state[0]++;
        Free(work);
    }
    Free(state);
    EXPECT_EQ(LargestFree(), before);
}
