# 07 - Next session

Where session 2 left it: why the game is "Marty only" in MAME (memory: the
2 MB Towns leaves the program too little, `03-executables.md`), the disc's
TBIOS against the Marty ROM's (the graphic module the same; the Marty adds a
zoom and a pad-as-mouse), and the machine chosen: **the FM Towns with 4 MB,
the disc's TBIOS** (`06-attack-plan.md`). The kit has a machine profile; the
oracle runs `fmtowns -ramsize 4M` by default and traces the program's calls
(`--trace-calls`).

Goal: **the start, recompiled** -- from the program's first instruction to the
user-disk prompt drawn as the oracle draws it.

## TODO

### 1. The start, read on the oracle

- [ ] `tools/oracle.py --dump-write ADDR=VALUE` at the program's first
      instruction on the 4 MB Towns (as the first game's session 3: the
      first push of `_mwINIT`'s `call main` at 0x340A6, or the entry's
      `jmp`): the registers RUN386 hands over (ESP 0x6BD10?), EFLAGS, the
      segment registers.
- [ ] TBIOS in memory against `TBIOS.BIN` at that instruction (the first
      game found it the file's byte for byte); `FORRBIOS.NSD` in memory
      (0x400000, selectors 0x4C/0x54) against its file's image.
- [ ] The machine's state there (`items.txt`, `ports.txt`): the CRTC, video
      registers, palettes, PICs, for the runtime's `townsos()`.
- [ ] Confirm the profile `towns4m+nsd` from that dump (base 0x408000, limit
      0x368FFF, selector 0x40 0x3F7FFF) and how RUN386 lays out
      `int 31h AX=0501h`'s blocks (`_mwexpand_heap`).

### 2. The kit's recompiler on this program

- [ ] `python -m fmtownskit.recomp` takes the symbols: a way to say "every
      symbol below 0x3A650 is a seed" in `--exp` (today only
      `recomp.discover --symbol-seeds`), and the symbols' names in the
      emitted C++ (comments, or the function's name beside its offset).
- [ ] The tables placed after their jump in the drawing routines
      (`jmp cs:[ebx + table]`, `jmp cs:[edi + table]`: 15 sites, the index
      already scaled, `05-open-questions.md` 6): discovery should read them,
      or the runtime will meet them one at a time.
- [ ] Generate: the game (`--exp game=build/disc/4DDFMT.EXP@0c+...`) and the
      disc's TBIOS (`--raw tbios=build/disc/TBIOS.BIN@110:20-100`, as the
      first game's); note the C++'s size, clang's time, the split per file.
- [ ] The self-test vectors **in slices** (the interpreter's unicorn check on
      55,000 instructions took 8 GB in one go): a `--selftest` that takes a
      range of functions, or several runs; then `selftest` on the C++.
- [ ] The `esc` forms in the game's own reached code (MetaWare's FPU probe):
      the probe must find no coprocessor in the runtime as in MAME.

### 3. The runtime's first steps

- [ ] `src/main.cpp` and `CMakeLists.txt` from the first game's (`tqod`):
      the port's profile `towns4m+nsd` declared there, from the dumps;
      the CD image, `--headless`, `--frames`, `--png-every`.
- [ ] int 90h (`KYB_*`: AH 01h, 02h, 05h-07h, 09h, 0Ah), int 8Eh AX=CF00h
      (`KimG_*`), the CD BIOS's 00h, 02h, 53h, 55h, 56h, int 31h AX=0501h,
      Phar Lap 2502h-2507h: answered in `towns_dos` (as int 93h is), each
      checked against the oracle with `--trace-calls` on the game's callers.
- [ ] TBIOS's warikomi (fs:[0x1A0]) and System (fs:[0x1C0]) modules,
      recompiled with TBIOS: their effect on the machine (the timer A
      interrupt for `SND_*`, the PICs).
- [ ] Screen mode 13 (and 10, 12, 15) drawn by the runtime's video as MAME
      does: the CRTC set-up the graphic module writes from 0x1AD0.
- [ ] The goal's check: the user-disk prompt (oracle 22 s) the same pixel
      for pixel; then NO twice and Electronic Arts' logo (30-34 s).

## Tools

`tools/oracle.py` (`fmtowns` with 4 MB by default; `--machine fmtmarty` for
the cross-check; `--at`, `--input T0-T1:BUTTONS`, `--trace-calls
NAME|OFF,...`, `--dump`, `--dump-write`, `--ramsize`, `--wav`, `--sound-log`,
`--lua`). The user-disk prompt needs NO twice: `--input
22-22.3:A,28-28.3:A`. The first game's `tools/framematch.py` will come over
with the runtime. Kit work runs from `D:\Homebrew6` until the kit's commit is
pulled into the submodule. Python that holds a backslash goes in a file
written whole, never in a shell heredoc.
