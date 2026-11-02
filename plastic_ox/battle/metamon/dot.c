#include "runtime.h"
typedef uint32_t MmWord __attribute__((may_alias));

#ifdef MM_DOT_IWRAM
__attribute__((section(".iwram"), noinline))
#endif
int32_t MmDot(const int8_t *a, const int8_t *b, int count)
{
    int32_t sum = 0;
    /* All exported row widths and quantized offsets are multiples of four.
     * The alias type permits aligned word loads without aliasing violations.
     * Four ROM bytes per word avoids four separate nonsequential byte reads. */
    while (count >= 4)
    {
        uint32_t x = *(const MmWord *)a, y = *(const MmWord *)b;
        sum += (int32_t)(int8_t)x * (int8_t)y;
        sum += (int32_t)(int8_t)(x >> 8) * (int8_t)(y >> 8);
        sum += (int32_t)(int8_t)(x >> 16) * (int8_t)(y >> 16);
        sum += (int32_t)(int8_t)(x >> 24) * (int8_t)(y >> 24);
        a += 4; b += 4; count -= 4;
    }
    while (count--) sum += (int32_t)*a++ * *b++;
    return sum;
}
