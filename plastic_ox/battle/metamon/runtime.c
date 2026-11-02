#include "runtime.h"
#include <math.h>
#include <string.h>

#include "nonlinear.inc"

static float Sigmoid(float x)
{
    float a = fabsf(x) * 64.0f, y;
    int i;
    if (a >= 768) return x < 0 ? 0 : 1;
    i = (int)a;
    y = sSigmoid[i] + (sSigmoid[i+1]-sSigmoid[i])*(a-i);
    return x < 0 ? 1.0f-y : y;
}

/* Binary fields are losslessly bit-packed. Nonbinary fields retain the
 * export's FP32 values; masks must not be rounded out of arbitrary numbers. */
static float MonNum(const MmObservation *o, int i, int j)
{
    return j < 24 ? o->mon_num[i][j] : (o->mon_flags[i][(j-24)/32] >> ((j-24)%32)) & 1;
}
static float MoveNum(const MmObservation *o, int i, int k, int j)
{
    return j < 4 ? o->move_num[i][k][j] : (o->move_flags[i][k] >> (j-4)) & 1;
}
static float EventNum(const MmObservation *o, int i, int j)
{
    return j < 24 ? o->event_num[i][j] : (o->event_flags[i] >> (j-24)) & 1;
}
static float GlobalNum(const MmObservation *o, int j)
{
    return j < 32 ? o->global_num[j] : (o->global_flags[(j-32)/32] >> ((j-32)%32)) & 1;
}

/* Match torch.round: nearest integer, ties to even (roundf is different). */
static int RoundEven(float x)
{
    int n = (int)x;
    float d = x - n;
    if (d > 0.5f || (d == 0.5f && n % 2 != 0)) ++n;
    if (d < -0.5f || (d == -0.5f && n % 2 != 0)) --n;
    return n;
}

static float *Embed(float *out, int id, int token)
{
    const MmTensor *t = &gMmModel[id];
    int j;
    for (j = 0; j < t->cols; ++j)
        *out++ = t->weight[token * t->cols + j] * t->scale[token];
    return out;
}

static int ValidTokens(const int16_t *tokens, const int *tables, int count)
{
    int i;
    for (i = 0; i < count; ++i)
        if (tokens[i] < 0 || tokens[i] >= gMmModel[tables[i]].rows) return 0;
    return 1;
}

static int ValidNumbers(const float *x, int count)
{
    int i;
    for (i = 0; i < count; ++i)
        if (!isfinite(x[i]) || fabsf(x[i]) > 16.0f) return 0;
    return 1;
}

static int Validate(const MmObservation *o, const float *hidden)
{
    static const int mon[] = {MM_SPECIES, MM_ITEM, MM_ABILITY, MM_STATUS,
                             MM_MOVE, MM_ELEMENT, MM_ELEMENT};
    static const int move[] = {MM_MOVE, MM_ELEMENT, MM_CATEGORY};
    static const int event[] = {MM_SPECIES, MM_SPECIES, MM_MOVE, MM_MOVE,
                               MM_ACTION, MM_ACTION};
    int i, j, legal = 0;
    for (i = 0; i < 12; ++i)
    {
        if (!ValidTokens(o->mon_cat[i], mon, 7)
            || !ValidNumbers(o->mon_num[i], 24)) return 0;
        for (j = 0; j < 4; ++j)
            if (!ValidTokens(o->move_cat[i][j], move, 3)
                || !ValidNumbers(o->move_num[i][j], 4)
                || o->move_valid[i] > 15 || o->move_flags[i][j] > 1023) return 0;
        if (i >= 6)
        {
            /* Defense in depth: this schema never provides opponent stats,
             * exact PP, a complete moveset, or private-side flags. These
             * checks cannot certify the provenance of public event inputs. */
            for (j = 3; j < 9; ++j)
                if (o->mon_num[i][j] != 0 || MonNum(o, i, j + 24) != 0) return 0;
            if (MonNum(o, i, 59) != 0 || MonNum(o, i, 62) != 0) return 0;
            for (j = 0; j < 4; ++j)
                if (o->move_num[i][j][3] != 0 || MoveNum(o, i, j, 4) != 0) return 0;
        }
    }
    for (i = 0; i < MM_WINDOW; ++i)
        if (!ValidTokens(o->event_cat[i], event, 6)
            || !ValidNumbers(o->event_num[i], 24)) return 0;
    for (i = 0; i < MM_ACTIONS; ++i)
    {
        if (o->legal[i] > 1 || GlobalNum(o, 87 + i) != o->legal[i]) return 0;
        legal |= o->legal[i];
    }
    if (!legal || !ValidNumbers(o->global_num, 32)) return 0;
    for (i = 0; i < MM_HIDDEN; ++i)
        if (!isfinite(hidden[i]) || fabsf(hidden[i]) > 1.0f) return 0;
    return 1;
}

/* Row evaluation also permits GRU gates to be tiled without materializing
 * either 1152-element gate tensor. The two biases remain separate: PyTorch
 * applies the reset gate to the recurrent candidate bias as well. */
static float Row(int id, int row, const int8_t *q, float scale, int relu)
{
    const MmTensor *t = &gMmModel[id];
    int32_t acc = MmDot(q, t->weight + row * t->cols, t->cols);
    float y = (float)acc * (scale * t->scale[row]) + t->bias[row];
    return relu && y < 0 ? 0 : y;
}

static void StartQuant(MmJob *j, const float *in, int8_t *out, int count)
{
    j->qin = in; j->qout = out; j->qcount = count;
    j->qindex = 0; j->qphase = 1; j->maximum = 0;
}

static void QuantStep(MmJob *j)
{
    int end = j->qindex + 32, i;
    if (end > j->qcount) end = j->qcount;
    for (i = j->qindex; i < end; ++i)
        if (j->qphase == 1)
        {
            float v = fabsf(j->qin[i]);
            if (v > j->maximum) j->maximum = v;
        }
        else
        {
            int v = RoundEven(j->qin[i] / j->scale);
            j->qout[i] = v < -127 ? -127 : v > 127 ? 127 : v;
        }
    j->qindex = end;
    if (end == j->qcount)
    {
        if (j->qphase == 1)
        {
            j->scale = j->maximum / 127.0f;
            if (j->scale < 1e-9f) j->scale = 1e-9f;
            j->qindex = 0; j->qphase = 2;
        }
        else j->qphase = 0;
    }
}

int MmBegin(MmJob *j, const MmObservation *o, float hidden[MM_HIDDEN],
            float logits[MM_ACTIONS], MmWorkspace *w)
{
    if (!j || !o || !hidden || !logits || !w || !Validate(o, hidden)) return 0;
    memset(j, 0, sizeof(*j));
    j->obs = o; j->hidden = hidden; j->logits = logits; j->work = w;
    return 1;
}

int MmStep(MmJob *job)
{
    static const int mon[] = {MM_SPECIES, MM_ITEM, MM_ABILITY, MM_STATUS,
                             MM_MOVE, MM_ELEMENT, MM_ELEMENT};
    static const int event[] = {MM_SPECIES, MM_SPECIES, MM_MOVE, MM_MOVE,
                               MM_ACTION, MM_ACTION};
    const MmObservation *o = job->obs;
    MmWorkspace *w = job->work;
    float *p, *encoded = w->a + 1248;
    int i = job->index, j, k;
    if (job->qphase) { QuantStep(job); return 0; }
    switch (job->phase)
    {
    case 0: /* Materialize one move input, including masked slots for scale. */
        p = w->a + i * 36;
        p = Embed(p, MM_MOVE, o->move_cat[i/4][i%4][0]);
        p = Embed(p, MM_ELEMENT, o->move_cat[i/4][i%4][1]);
        p = Embed(p, MM_CATEGORY, o->move_cat[i/4][i%4][2]);
        for (j = 0; j < 14; ++j) *p++ = MoveNum(o, i/4, i%4, j);
        if (++job->index != 48) return 0;
        StartQuant(job, w->a, w->quant, 48*36);
        break;
    case 1: /* Four move rows -> one pooled mon feature; retain active moves. */
        j = i % 32; k = i / 32;
        if (!j)
        {
            int t;
            p = w->a + k*196;
            for (t = 0; t < 7; ++t) p = Embed(p, mon[t], o->mon_cat[k][t]);
            for (t = 0; t < 96; ++t) w->a[k*196+100+t] = MonNum(o, k, t);
        }
        {
            float sum = 0;
            int m;
            for (m = 0; m < 4; ++m)
            {
                float y = Row(MM_MOVE_ENCODER, j, w->quant+(k*4+m)*36, job->scale, 1)
                          * ((o->move_valid[k] >> m) & 1);
                if (!k) w->a[2352+m*32+j] = y;
                sum += y;
            }
            w->a[k*196+68+j] = sum / 4.0f;
        }
        if (++job->index != 384) return 0;
        StartQuant(job, w->a, w->quant, 12*196);
        break;
    case 2:
        w->a[i] = Row(MM_MON_0, i%64, w->quant+(i/64)*196, job->scale, 1);
        if (++job->index != 768) return 0;
        StartQuant(job, w->a, w->quant, 768);
        break;
    case 3:
        w->a[i] = Row(MM_MON_2, i%64, w->quant+(i/64)*64, job->scale, 1) * MonNum(o, i/64, 48);
        if (++job->index != 768) return 0;
        memcpy(w->a+896, w->a+2352, 128*sizeof(float));
        break;
    case 4:
        p = w->a+1088+i*128;
        for (j = 0; j < 6; ++j) p = Embed(p, event[j], o->event_cat[i][j]);
        for (j = 0; j < 32; ++j) *p++ = EventNum(o, i, j);
        if (++job->index != 4) return 0;
        StartQuant(job, w->a+1088, w->quant, 512);
        break;
    case 5:
        w->a[768+i] = Row(MM_EVENT_ENCODER, i%32, w->quant+(i/32)*128, job->scale, 1) * EventNum(o, i/32, 24);
        if (++job->index != 128) return 0;
        for (j = 0; j < 96; ++j) w->a[1088+j] = GlobalNum(o, j);
        StartQuant(job, w->a+1088, w->quant, 96);
        break;
    case 6:
        w->a[1024+i] = Row(MM_GLOBAL_ENCODER, i, w->quant, job->scale, 1);
        if (++job->index != 64) return 0;
        StartQuant(job, w->a, w->quant, 1088);
        break;
    case 7:
        w->a[1088+i] = Row(MM_FUSION_0, i, w->quant, job->scale, 1);
        if (++job->index != 160) return 0;
        StartQuant(job, w->a+1088, w->quant, 160);
        break;
    case 8:
        encoded[i] = Row(MM_FUSION_2, i, w->quant, job->scale, 1);
        if (++job->index != 256) return 0;
        StartQuant(job, job->hidden, w->quant+256, MM_HIDDEN);
        break;
    case 9:
        job->hiddenScale = job->scale;
        StartQuant(job, encoded, w->quant, 256);
        break;
    case 10:
        {
            float r = Sigmoid(Row(MM_GRU_IH, i, w->quant, job->scale, 0)
                              + Row(MM_GRU_HH, i, w->quant+256, job->hiddenScale, 0));
            float z = Sigmoid(Row(MM_GRU_IH, i+384, w->quant, job->scale, 0)
                              + Row(MM_GRU_HH, i+384, w->quant+256, job->hiddenScale, 0));
            float n = 2.0f * Sigmoid(2.0f * (Row(MM_GRU_IH, i+768, w->quant, job->scale, 0)
                            + r * Row(MM_GRU_HH, i+768, w->quant+256, job->hiddenScale, 0))) - 1.0f;
            w->a[i] = (1.0f-z)*n + z*job->hidden[i];
        }
        if (++job->index != MM_HIDDEN) return 0;
        memcpy(w->a+MM_HIDDEN, encoded, 256*sizeof(float));
        StartQuant(job, w->a, w->quant, 640);
        break;
    case 11:
        /* Output stored away from staged hidden until the final commit. */
        w->a[1024+i] = Row(MM_ACTOR, i, w->quant, job->scale, 0);
        if (++job->index != MM_ACTIONS) return 0;
        if (!job->deferCommit) memcpy(job->hidden, w->a, MM_HIDDEN*sizeof(float));
        memcpy(job->logits, w->a+1024, MM_ACTIONS*sizeof(float));
        break;
    default: return 1;
    }
    ++job->phase; job->index = 0;
    return job->phase == 12;
}

int MmCommit(MmJob *job)
{
    if (job->phase != 12 || !job->deferCommit) return 0;
    memcpy(job->hidden, job->work->a, MM_HIDDEN*sizeof(float));
    job->deferCommit = 0;
    return 1;
}

int MmInfer(const MmObservation *o, float hidden[MM_HIDDEN],
            float logits[MM_ACTIONS], MmWorkspace *w)
{
    MmJob job;
    if (!MmBegin(&job, o, hidden, logits, w)) return 0;
    while (!MmStep(&job)) {}
    return 1;
}

int MmChooseLegal(const float logits[MM_ACTIONS], const uint8_t legal[MM_ACTIONS])
{
    int i, best = -1;
    for (i = 0; i < MM_ACTIONS; ++i)
    {
        if (legal[i] > 1 || !isfinite(logits[i])) return -1;
        if (legal[i] && (best < 0 || logits[i] > logits[best])) best = i;
    }
    return best;
}
