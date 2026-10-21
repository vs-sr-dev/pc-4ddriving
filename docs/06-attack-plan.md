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
* **The machine is data.** The program sees the same selectors on the
  Towns and the Marty (the first game's session 2), with a segment as large
  as the RAM allows (all memory asked): which machine and how much RAM is a
  profile, below. (Session 1 had planned on the Marty; session 2 chose the
  4 MB Towns.)

## The machine: the FM Towns with 4 MB, the disc's TBIOS (decided in session 2)

Session 2 found that the game is "Marty only" in MAME by memory, not by
hardware (`05-open-questions.md` 1), and that the disc's TBIOS draws what the
Marty ROM's does (`03-executables.md`). The user chose, of three roads:

* **taken: the FM Towns with 4 MB, the disc's `TBIOS.BIN`** -- the first
  game's "Towns path", no ROM to bring. The oracle is MAME's `fmtowns
  -ramsize 4M` (`tools/oracle.py`'s default), which runs the very TBIOS the
  runtime runs, so frames can match pixel for pixel; `fmtmarty` stays as
  the cross-check (its stills are the same). Left out: the Marty's TV zoom
  and its pad-as-mouse.
* not taken: the Marty with its ROM's TBIOS and extension (`MAR_EX1.ROM`,
  BYOA), recompiled -- the target machine exactly, more work, a ROM to bring;
* not taken now: both, as profiles; the Marty's can come later if the zoom
  or the pad-as-mouse is wanted.

The kit's side: **a machine profile as data** (`runtime/towns.h` `Profile`,
`towns.PROFILES`): the RAM size, where RUN386 puts the program's segment and
how large when the P3 asks for all memory, selector 0x40's limit. The kit
ships the profile it read under the first game; this port declares its own,
read from its dumps: `towns4m+nsd` -- 4 MB, the program at 0x408000
(physical 0x49000), limit 0x368FFF, selector 0x40 to 0x3F7FFF (the NSD at
the top).

## The road

1. **The start, read on the oracle** (done, session 3): `--dump-write` at the program's first
   instruction on the 4 MB Towns (the registers RUN386 hands over, the
   descriptors, TBIOS as it lies in memory); the CRTC and video registers
   once the title is up (`ports.txt`).
2. **Recompile** (done, session 3): the game with its symbol seeds, the disc's TBIOS, the
   self-test vectors in slices (the interpreter's check on 55,000
   instructions ran out of memory in one go). The kit's recompiler takes the
   symbols for seeds and for function names in the C++.
3. **The runtime, headless** (session 3: to the credits, pixel for pixel; the timer A interrupt and the sound to come): the port's profile (`towns4m+nsd`); int 90h (the
   keyboard and pad as `KYB_*` call it), int 8Eh (KimG), the CD BIOS's 53h,
   55h, 56h; Phar Lap 2506h/2507h; TBIOS's warikomi and System modules'
   effects (the timer A interrupt for `SND_*`); the video modes 10, 12, 13,
   15. Frames against the oracle's (`fmtowns -ramsize 4M`): the user-disk
   prompt (22 s), Electronic Arts' logo (30-34 s), the title (46 s), the
   credits (70 s).
4. **The sound**: the kit's RF5C68 and YM3438 (the engine's PCM, `STUNTS.PMB`,
   `STUNTS.SLB`) and the CD-DA loops, against the oracle's `--sound-log`.
5. **The window and the pad**: the kit's SDL3 window; the Towns pad as the
   first game's (the game reads it through TBIOS's sound module, AH=40h);
   the steering as the game reads it.
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
| a machine profile as data: RAM, the program's segment, selector 0x40 | `runtime/towns.h`, `towns.PROFILES` (session 2) |
| the CRTC set-ups of modes 10, 12, 13, 15 | `runtime/towns_video` |
| int 90h, 8Eh, the CD BIOS's 53h/55h/56h | `runtime/towns_dos` |
| TBIOS's warikomi and System modules | recompiled with TBIOS; their machine effects in the runtime |

## The risks

* **Size and speed of the emitted C++**: 67,000 instructions at the first
  game's rate of C++ per instruction is a large build; splitting per
  function and clang's time to be measured.
* **The drawing routines**: hand-written, with inline jump tables and
  shared tails: discovery must read their tables (`cs:[ebx + table]`, the
  index pre-scaled) or the runtime will meet them one by one.
* **Timing**: a racing game's pace is its frame loop's; the oracle's 386DX
  at 16 MHz (`fmtowns`) is faster than the Marty's 386SX, and the game cares
  (`fmtspeed`): the pace to play at is the Marty's, the pace to compare at
  the oracle's.
