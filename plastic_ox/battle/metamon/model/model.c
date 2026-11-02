#include "../runtime.h"
extern const unsigned char gMmWeights[];
const MmTensor gMmModel[MM_TENSOR_COUNT] = {
    {(const int8_t *)(gMmWeights + 23788), (const float *)(gMmWeights + 33100), 0, 388, 24},
    {(const int8_t *)(gMmWeights + 7068), (const float *)(gMmWeights + 13468), 0, 800, 8},
    {(const int8_t *)(gMmWeights + 5796), (const float *)(gMmWeights + 6420), 0, 78, 8},
    {(const int8_t *)(gMmWeights + 34652), (const float *)(gMmWeights + 34692), 0, 10, 4},
    {(const int8_t *)(gMmWeights + 16668), (const float *)(gMmWeights + 22364), 0, 356, 16},
    {(const int8_t *)(gMmWeights + 6908), (const float *)(gMmWeights + 6988), 0, 20, 4},
    {(const int8_t *)(gMmWeights + 6876), (const float *)(gMmWeights + 6888), 0, 5, 2},
    {(const int8_t *)(gMmWeights + 6732), (const float *)(gMmWeights + 6828), 0, 12, 8},
    {(const int8_t *)(gMmWeights + 1008556), (const float *)(gMmWeights + 1009708), (const float *)(gMmWeights + 1038288), 32, 36},
    {(const int8_t *)(gMmWeights + 1009836), (const float *)(gMmWeights + 1022380), (const float *)(gMmWeights + 1038416), 64, 196},
    {(const int8_t *)(gMmWeights + 1022636), (const float *)(gMmWeights + 1026732), (const float *)(gMmWeights + 1038672), 64, 64},
    {(const int8_t *)(gMmWeights + 34732), (const float *)(gMmWeights + 38828), (const float *)(gMmWeights + 1027024), 32, 128},
    {(const int8_t *)(gMmWeights + 255660), (const float *)(gMmWeights + 261804), (const float *)(gMmWeights + 1028816), 64, 96},
    {(const int8_t *)(gMmWeights + 38956), (const float *)(gMmWeights + 213036), (const float *)(gMmWeights + 1027152), 160, 1088},
    {(const int8_t *)(gMmWeights + 213676), (const float *)(gMmWeights + 254636), (const float *)(gMmWeights + 1027792), 256, 160},
    {(const int8_t *)(gMmWeights + 709036), (const float *)(gMmWeights + 1003948), (const float *)(gMmWeights + 1033680), 1152, 256},
    {(const int8_t *)(gMmWeights + 262060), (const float *)(gMmWeights + 704428), (const float *)(gMmWeights + 1029072), 1152, 384},
    {(const int8_t *)(gMmWeights + 0), (const float *)(gMmWeights + 5760), (const float *)(gMmWeights + 1026988), 9, 640},
};
