/* ARM mode is required for the hot multiply loop on ARM7TDMI. */
#pragma GCC push_options
#pragma GCC target("arm")
#define MM_DOT_IWRAM
#include "../plastic_ox/battle/metamon/dot.c"
#pragma GCC pop_options
