// The recompiled modules this port runs (build/game: the recompiler's output, which may also
// hold the self-test's OPTEST module): the game under code selector 0x0C, TBIOS under 0x110.
#include "x86.h"
extern const X86Module g_mod_p_game, g_mod_p_tbios;
const X86Module* const g_x86_modules[] = {&g_mod_p_game, &g_mod_p_tbios};
const int g_x86_nmodules = 2;
