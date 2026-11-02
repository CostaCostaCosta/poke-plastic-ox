#ifndef PLASTIC_OX_METAMON_RUNTIME_H
#define PLASTIC_OX_METAMON_RUNTIME_H

#include <stdint.h>

/* Deployment prototype for the 1m/window=4 causal export. No battle globals,
 * opponent party pointers, allocator, RNG, or simulator dependencies here. */
enum { MM_HIDDEN = 384, MM_ACTIONS = 9, MM_WINDOW = 4 };

typedef struct {
    int16_t mon_cat[12][7];
    float mon_num[12][24];
    uint32_t mon_flags[12][3];
    int16_t move_cat[12][4][3];
    float move_num[12][4][4];
    uint16_t move_flags[12][4];
    uint8_t move_valid[12];
    int16_t event_cat[MM_WINDOW][6];
    float event_num[MM_WINDOW][24];
    uint8_t event_flags[MM_WINDOW];
    float global_num[32];
    uint32_t global_flags[2];
    uint8_t legal[MM_ACTIONS];
} MmObservation;

typedef struct {
    const int8_t *weight;
    const float *scale;
    const float *bias;
    int rows, cols;
} MmTensor;

enum {
    MM_SPECIES, MM_ITEM, MM_ABILITY, MM_STATUS, MM_MOVE, MM_ELEMENT,
    MM_CATEGORY, MM_ACTION, MM_MOVE_ENCODER, MM_MON_0, MM_MON_2,
    MM_EVENT_ENCODER, MM_GLOBAL_ENCODER, MM_FUSION_0, MM_FUSION_2,
    MM_GRU_IH, MM_GRU_HH, MM_ACTOR, MM_TENSOR_COUNT
};
extern const MmTensor gMmModel[MM_TENSOR_COUNT];

/* Caller owns scratch and state; reset hidden to zero at each battle start.
 * No implicit persistent state or heap allocation. */
typedef struct {
    /* Overlaid phases: 12x196 mon inputs + 128 active moves; then
     * fusion (1088), encoder scratch, and encoded state. Quantized
     * inputs are complete before any in-place output overwrites them. */
    float a[2496];
    int8_t quant[2496];
} MmWorkspace;

_Static_assert(sizeof(float) == 4, "Metamon requires float32");
_Static_assert(sizeof(MmObservation) == 3212, "Observation fixture ABI changed");
_Static_assert(sizeof(MmWorkspace) == 12480, "Workspace accounting changed");

/* A job owns a frozen observation and scratch until completion/cancellation.
 * Step executes one bounded tile. Hidden/logits commit only at completion;
 * abandoning a job never advances the recurrent state. No RNG is consumed. */
typedef struct {
    const MmObservation *obs;
    float *hidden, *logits;
    MmWorkspace *work;
    const float *qin;
    int8_t *qout;
    float scale, hiddenScale, maximum;
    int phase, index, qcount, qindex, qphase, deferCommit;
} MmJob;
int MmBegin(MmJob *job, const MmObservation *obs, float hidden[MM_HIDDEN],
            float logits[MM_ACTIONS], MmWorkspace *work);
int MmCommit(MmJob *job); /* Commit a completed deferred job exactly once. */
int MmStep(MmJob *job); /* 0 pending, 1 complete; completed jobs are idempotent. */

/* Returns 0 for invalid inputs without modifying hidden/logits. On success,
 * consumes exactly ONE decision and returns unmasked logits. */
int MmInfer(const MmObservation *obs, float hidden[MM_HIDDEN],
            float logits[MM_ACTIONS], MmWorkspace *work);
/* Deterministic initial policy; -1 means invalid/no legal action. */
int MmChooseLegal(const float logits[MM_ACTIONS], const uint8_t legal[MM_ACTIONS]);
int32_t MmDot(const int8_t *a, const int8_t *b, int count);

#endif
