# 06 - The attack plan

## What the port is

As the first game's: a native PC program that runs **the game's own code
and TBIOS's own code, recompiled from 386 to C++** by fmtownskit, on the
kit's runtime standing in for the machine under them (VRAM and CRTC, the
sprite controller, the YM3438 and RF5C68, the CD and its CD-DA, the
interrupts, the pad). DOS, Phar Lap and the BIOS interrupts are answered at
their boundary, from the disc image. Everything shared goes into the kit;
what is this game's stays here.

What is new, and why the shape still holds:

* **The program is ten times the first game's and compiled C**: 1,273
  functions, 67,000 instructions, against 157 and 7,900 (`03-executables.md`).
  The kit's recompiler took the first game and TBIOS with no failure; this
  one's discovery already runs clean (0 refused, 0 conflicts), and its
  **symbol table names every function** and seeds discovery. Size is the
  emitter's and the compiler's problem, not the method's.
* **No floating point to emulate**: the x87 code is MetaWare's library's,
  behind a probe that finds no coprocessor on either machine. The kit runs
  an escape as MAME's 386 does (nothing), and the library takes its
  software path. The game's own arithmetic is fixed point, as *Stunts* on
  the PC.
* **A third piece of system code**: `FORRBIOS.NSD` answers the keyboard,
  KimG and CD BIOS interrupts in protected mode. The runtime answers those
  interrupts itself, as it already answers int 93h for the first game, and
  the NSD is recompiled only if its behaviour turns out to matter.
* **The Marty is the machine, this time.** The runtime's machine data
  (the RAM size, the machine id, the CRTC's timings) are the Marty's where
  the oracle is the Marty; the program sees the same selectors on both
  (the first game's session 2), with a larger segment (all memory).

## The decision the next session makes: which TBIOS

On the Marty, the TBIOS is the Marty ROM's build; on the Towns, the disc's
`TBIOS.BIN`, and with the disc's the game shows nothing on MAME's first
Towns (`05-open-questions.md` 1). Two roads:

1. **The disc's TBIOS, with the Marty's machine under it** (the machine
   id, if that is what its graphic module reads to allow modes 10, 12, 13,
   15). No ROM needed (the kit's "Towns path"). Possible only if the disc's
   build sets those modes at all.
2. **The Marty ROM's TBIOS**, recompiled from `MAR_EX1.ROM` (at 0x19C00, the
   first game's session 2), which the user provides as they provide the disc
   (BYOA, as the other kits take a BIOS). Exactly what the oracle runs.

To read first: the graphic module's AH=01h (resolution) in both builds, and
what the Marty ROM's wrappers add. The choice goes to the user with the
evidence.

## The road

1. **The start, read on the oracle**: `--dump-write` at the program's first
   instruction on `fmtmarty` (the registers RUN386 hands over, the
   descriptors, the segment's limit, TBIOS as it lies in memory); the
   TBIOS question above; the CRTC and video registers once the title is
   up (`ports.txt`).
2. **Recompile**: the game with its symbol seeds, TBIOS (the disc's or the
   ROM's), the self-test vectors in slices (the interpreter's check on
   55,000 instructions ran out of memory in one go). The kit's recompiler
   takes the symbols for seeds and for function names in the C++.
3. **The runtime, headless**: the Marty's machine data; int 90h (the
   keyboard and pad as `KYB_*` call it), int 8Eh (KimG), the CD BIOS's 53h,
   55h, 56h; Phar Lap 2506h/2507h; TBIOS's warikomi and System modules'
   effects (the timer A interrupt for `SND_*`); the video modes 10, 12, 13,
   15. Frames against the oracle's: the Marty logo is the ROM's, so the
   first frames to match are the user-disk prompt (20 s), Electronic Arts'
   logo (32 s), the title (46 s), the credits (68 s).
4. **The sound**: the kit's RF5C68 and YM3438 (the engine's PCM, `STUNTS.PMB`,
   `STUNTS.SLB`) and the CD-DA loops, against the oracle's `--sound-log`.
5. **The window and the pad**: the kit's SDL3 window; the Marty pad (A, B,
   Run, Select, Zoom as MAME's martypad wires them); the steering as the
   game reads it.
6. **Playable**: a race, the replay, the track editor; the user disk on the
   host; then publication at the user's word, with the kit and the first
   game.

## What is new here for the kit

| Need | Where |
|---|---|
| a P3 file with symbols; the extra memory in bytes | `exp` (done, session 1) |
| tables bounded by symbols, symbols as seeds and names | `x86map`, `recomp.discover` (done); the emitter's function names (next) |
| the x87's escapes on a machine with none | `i386`, `i386emu`, `recomp.emit` (done) |
| the ports this game reads (0x24, 0x26, 0x5EC, 0xFDA0, the CMOS) | `towns` (named, done); the runtime (next) |
| the Marty as a runtime machine: its id, RAM, the CRTC modes | `runtime/towns*` |
| int 90h, 8Eh, the CD BIOS's 53h/55h/56h | `runtime/towns_dos` |
| TBIOS's warikomi and System modules | recompiled with TBIOS; their machine effects in the runtime |
| possibly: a TBIOS from the Marty ROM | the recompiler's `--raw` from a ROM file, the runtime's load |

## The risks

* **The TBIOS question** above: if neither road is clean, a third is to
  answer the graphic module's resolution call in the runtime.
* **Size and speed of the emitted C++**: 67,000 instructions at the first
  game's rate of C++ per instruction is a large build; splitting per
  function and clang's time to be measured.
* **The drawing routines**: hand-written, with inline jump tables and
  shared tails: discovery must read their tables (`cs:[ebx + table]`, the
  index pre-scaled) or the runtime will meet them one by one.
* **Timing**: a racing game's pace is its frame loop's; the Marty's 386SX
  speed is the oracle's. `fmtspeed` hints that the game cares.
