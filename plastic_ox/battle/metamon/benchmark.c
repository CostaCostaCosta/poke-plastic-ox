#include "runtime.h"
#include <string.h>

#define REG16(addr) (*(volatile uint16_t *)(addr))
#define COUNT 8
extern const MmObservation gMmFixtures[COUNT];
static MmObservation sObservation;
static MmWorkspace sWorkspace;
static float sHidden[MM_HIDDEN];

/* Read by the runner using the ELF symbol, not a fixed RAM address. */
volatile struct {
    uint32_t done;
    uint32_t cycles[COUNT];
    int32_t status[COUNT];
    int32_t actions[COUNT];
    float logits[COUNT][MM_ACTIONS];
    float hidden[COUNT][MM_HIDDEN];
} gMmBenchResults;

static uint32_t Clock(void)
{
    uint32_t high, low, again;
    do {
        high = REG16(0x0400010c);
        low = REG16(0x04000108);
        again = REG16(0x0400010c);
    } while (high != again);
    return (high << 16) | low;
}

int main(void)
{
    int i, j;
    float logits[MM_ACTIONS];
    /* Same prefetch and WS0/WS1 settings as src/main.c. No audio, DMA, IRQs
     * or battle observation extraction: this measures inference CPU cost. */
    REG16(0x04000204) = 0x4014 | 0x00a0;
    for (i = 0; i < COUNT; ++i)
    {
        uint32_t start, end;
        memcpy(&sObservation, &gMmFixtures[i], sizeof(sObservation));
        REG16(0x0400010a) = 0;
        REG16(0x0400010e) = 0;
        REG16(0x04000108) = 0;
        REG16(0x0400010c) = 0;
        REG16(0x0400010e) = 0x84;
        REG16(0x0400010a) = 0x80;
        start = Clock();
        gMmBenchResults.status[i] = MmInfer(&sObservation, sHidden, logits, &sWorkspace);
        end = Clock();
        REG16(0x0400010a) = 0;
        gMmBenchResults.cycles[i] = end - start;
        gMmBenchResults.actions[i] = MmChooseLegal(logits, sObservation.legal);
        for (j = 0; j < MM_ACTIONS; ++j) gMmBenchResults.logits[i][j] = logits[j];
        for (j = 0; j < MM_HIDDEN; ++j) gMmBenchResults.hidden[i][j] = sHidden[j];
    }
    gMmBenchResults.done = 0x4d4d444e;
    for (;;) {}
}
