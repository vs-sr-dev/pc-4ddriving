# 07 - Next session

Where session 1 left it: the disc identified and read, the program's surface
mapped by its own symbols, the kit able to take it (the P3 symbol table,
read tables bounded by symbols, the x87's escapes), discovery clean on the
whole program, the oracle on `fmtmarty` reaching the title and the credits
with two presses.

Goal: **the start, and the TBIOS decision** (`06-attack-plan.md`).

1. **Why the Towns stays black** (`05-open-questions.md` 1): the graphic
   module's AH=01h in the disc's `TBIOS.BIN` and in the Marty ROM's build;
   what modes 10, 12, 13, 15 need; whether the machine id decides. Put the
   choice of TBIOS to the user with the evidence.
2. **The program's first instruction on `fmtmarty`** (`tools/oracle.py
   --dump-write`): the registers, the descriptors, the segment's limit,
   the TBIOS in memory, `FORRBIOS.NSD` in memory against the file.
3. **The recompiler on the game**: the C++ with the symbols as names, the
   build's size and time, the self-test vectors in slices; the
   interpreter's unicorn check in slices too.
4. **The runtime's first steps**: the Marty's machine data, int 90h/8Eh,
   until the user-disk prompt draws.

Worth doing on the way: which CD-DA track plays at the title (`--sound-log`),
and the kit's README table for this game once something runs.

Tools: `tools/oracle.py` (`--machine fmtmarty` by default; `--at`, `--input
T0-T1:BUTTONS`, `--dump`, `--dump-write`, `--wav`, `--sound-log`, `--lua`).
The user-disk prompt needs NO twice: `--input 22-22.3:A,28-28.3:A`. Kit work
runs from `D:\Homebrew6` (the submodule is the last commit):
`python -m fmtownskit.exp|x86map|i386|recomp.discover build/disc/4DDFMT.EXP
--symbol-seeds 3a650`.
