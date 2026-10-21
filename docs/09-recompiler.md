# 09 - The recompiler

The game's code and TBIOS's, recompiled from 386 to C++ by fmtownskit
(`python -m fmtownskit.recomp`). What each piece was checked against on this
disc; the first game's `docs/09-recompiler.md` has the decoder's and the
interpreter's own checks.

```sh
python -m fmtownskit.recomp --out build/game \
    --exp game=build/disc/4DDFMT.EXP@0c/3a650+20518,35018,3516c,35340,35474,35866,35a3c,37a58 \
    --raw tbios=build/disc/TBIOS.BIN@110:20-1e0+166a7,169d0,16ab0,16ae9,16aec,16afc,16b64
```

`@0c/3a650`: the program runs under code selector 0x0C, and every symbol it
keeps below 0x3A650 (where its code ends, `03-executables.md`) is a seed;
the symbols also name the functions and the labels in the C++ (a comment
over each, and beside each prototype in `p_game_funcs.h`).

## Discovery

* **The game**: 1,289 functions, 68,823 instructions, 45 jump tables (22
  bounded), 0 refused, 0 conflicts; 44 indirect transfers left to the
  runtime (calls through variables and registers, MetaWare's callbacks).
* **The tables placed after their jump** (session 2's 15 sites,
  `05-open-questions.md`): the hand-written drawing routines jump through
  `cs:[ebx + table]` or `cs:[edi + table]`, the register already an index
  times 4, the table in the code right after the jump or a little further.
  The kit now reads such a table (`recomp.discover`): past its jump, inside
  the same symbol's code, ending where the first code it jumps to begins.
  Read: `drawcline`, `andcline`, `orcline`, `xorcline` (10 entries each),
  `clipline` (16, then four of 9), `intsin` (4), `intatan` (8, two sites),
  `projectc` (4 and 4, two sites each), `s1linex` (10), `s2linex` (10 and
  10) -- each table's length the distance to its lowest target, which holds
  for all 19; 0 conflicts. 1,300 more instructions reached.
* **Code addresses as immediates**, met by the runtime one at a time and
  given as seeds: MetaWare's nested helpers passed to its heap walkers
  (`push 0x3516c` in `_mwinsert_into_free_chain`, 0x35018, 0x35340,
  0x35474, 0x37A58), the timer A handler `SND_int_timer_a_set` passes
  (0x35A3C), the default handler `SND_init` stores in its table (0x35866),
  the engine sound's callback (0x20518). A scan of every immediate that
  points into the code finds 575, nearly all numbers; these eight are the
  ones a call or a table uses.
* **TBIOS**: its far-pointer table runs to 0x1E0, not 0x100: the warikomi
  module (the interrupt manager) at 0x1A0 and 0x1A8, the System module at
  0x1C0; 0x1E0 on are the font ROM's (selector 0x138). And warikomi keeps
  its handlers as addresses in its own data (`mov es:[0x368], 0x169d0`),
  called through them from its IRQ handler, with a `ret` (0x16AE9) and a
  `retf` (0x166A7) for "none": seven seeds. 411 functions, 15,221
  instructions, 36 jump tables (13 bounded), 0 refused, 0 conflicts.

## Two instructions the start needs

MetaWare's start (`_mwINIT`) takes the Phar Lap road (int 21h AH=30h answers
"DX" above the version) and asks `lsl eax, eax` for DS's limit, then
`arpl` on the PSP's and the environment's selectors (0x24, 0x2C). Both were
"system instructions" the emitter left to the runtime; now `lsl` asks the
machine's descriptors (`x86_lsl`) and `arpl` is plain arithmetic in the C++.

## The C++, its build, the self-test

* 49 files for the game (12.5 MB, 328,000 lines), 17 for TBIOS (5.7 MB);
  clang -O2 builds the port in **27 seconds** on 16 threads, every file at
  the first try, no warning.
* **The self-test, in pieces**: the vectors are the interpreter's runs
  (`i386emu`), each function now seeded by its own address, so that a slice
  (`--slice LO-HI`) or several processes (`--jobs N`) give the same vectors
  as one run; with `--jobs 16` the game, TBIOS and the optest took about 18
  minutes. **56,974 vectors replayed on the C++, 0 failures**: the optest's
  54,703 (18,259 one-instruction functions: every distinct instruction of
  the game, of TBIOS and of a random sweep), the game's 1,576 and TBIOS's
  695 (3 random states per function; 2,243 and 370 runs reached the machine
  or the step limit and are not vectors; 44 replays stop at the machine in
  the C++).
* The first game, regenerated: its C++ byte for byte the same; its optest
  and functions, 23,525 vectors, 0 failures.
* Not done: `i386emu --check` against unicorn over this program
  (`05-open-questions.md` 12): the self-test checks the emitter against the
  interpreter, not the interpreter against unicorn on these instructions.
