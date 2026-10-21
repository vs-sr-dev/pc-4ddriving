# 00 - Sessions

## Session 1 (2026-10-21): the disc, the program's surface, the plan

* **The disc identified**: Redump's "4D Driving (Japan) (FM Towns Marty
  Rerelease)", serial HMD-222A / EFT-7005, *Stunts* by Distinctive Software
  for Electronic Arts Victor; every track and the cue sheet match MAME's
  software list (`4ddrivinm`), and the CHD the oracle makes has the list's
  SHA-1 (`01-disc-layout.md`).
* **A Marty title, confirmed on the oracle**: on `fmtmarty` it asks for a
  user disk at 20 s and, answered NO twice, shows Electronic Arts' logo,
  the title and the original team's credits; on `fmtowns` it runs, polling
  the keyboard, on a black screen. The screen modes it asks TBIOS for (10,
  12, 13, 15) and the video registers that follow differ between the two:
  the first question of the next session (`05-open-questions.md` 1).
* **The boot chain**: Towns-DOS, `TBIOS.BIN`, `RUN386.EXE` the first game's
  byte for byte; Fujitsu's CoCo and `ADDDRV` load **`FORRBIOS.NSD`**, which
  answers int 8Eh, 90h, 91h, 93h, 96h, 97h in protected mode (read in the
  IDT of both machines' dumps).
* **The program read by its own names** (`03-executables.md`): `4DDFMT.EXP`
  keeps Phar Lap's symbol table, 2,047 symbols; MetaWare High C, `_mwINIT`;
  code to 0x3A650, data, the stack to 0x6BD10. Discovery with the symbols as
  seeds: 1,273 functions, 66,927 instructions, 0 refused, 0 conflicts. Its
  surface: TBIOS's graphic, mouse, sound, "ま～くん", and the warikomi and
  System modules the first game never called; int 90h, 8Eh, the CD BIOS (00h, 02h, 50h, 52h-56h);
  ports 0x5EC (`fmtspeed`), 0x26, 0xFDA0, the palette.
* **The formats at a glance** (`02-data-formats.md`): *Stunts*' resource
  files (`.RES`, `.RVS`, `.RFS`, `.3SH`, `.SLB`), its tracks, eleven CD-DA
  loops.
* **fmtownskit** (`10-fmtownskit.md`): the P3 symbol table; read jump
  tables bounded by symbols (the "undecodable at 0x20006" of the
  pre-analysis was a table overrun, not the decoder); the x87's escapes
  run as on a 386 with no coprocessor; the ports this game touches.
* **The oracle**: `tools/oracle.py` from the first game, `fmtmarty` by
  default, the CHD checked against the list, and `--input` to press the
  Marty pad's buttons at given seconds.
* The plan (`06-attack-plan.md`): the game and TBIOS recompiled as for the
  first game -- which TBIOS, the disc's or the Marty ROM's, is the next
  session's to settle.

The repository put under git, fmtownskit a submodule at a33c4f2 (the session's kit commit, on be56af1).

## Session 2 (2026-10-21): why "Marty only"; the machine chosen

* **The black Towns explained: memory.** MAME's debugger, driven from Lua
  with no window (`tools/oracle.py --trace-calls`), followed TBIOS's graphic
  calls and the game's: screen mode 13 is set on both machines; then on the
  2 MB Towns `windowdef` gets NULL from a 74-byte `malloc` and
  `abortmessage("windowdef - OUT OF ROW TABLE SPACE")` resets the screen and
  waits for a key. RUN386 leaves the program 1,482,752 bytes there, 1,593,344
  on the Marty. **With 4 MB the Towns runs the game as the Marty does, with
  the disc's TBIOS**: 13 of 15 stills the same pixel for pixel, the other
  two an animation frame and a blinking cursor (`01-disc-layout.md`,
  `03-executables.md`).
* **The Marty's TBIOS read** against the disc's: its ROM (`MAR_EX1.ROM`)
  holds the same version and an extension that wraps the graphic and mouse
  entries; the graphic module is byte for byte the disc's, the mouse module
  rewritten, the wrapper adds what *inferred* is the TV zoom (port 0x3BB0).
  The game reads the pad through the sound module, the same in both.
* **The machine chosen** (the user's choice): the FM Towns with 4 MB and the
  disc's TBIOS, no ROM; the oracle `fmtowns -ramsize 4M`, `fmtmarty` the
  cross-check (`06-attack-plan.md`).
* **fmtownskit**: a machine profile as data -- the RAM, where RUN386 puts a
  program asking for all memory, selector 0x40 -- in `runtime/towns.h` and
  `towns.PROFILES`, the first game's the default (its 15 stills still the
  same pixel for pixel) (`10-fmtownskit.md`).
* **The oracle**: `fmtowns` with 4 MB by default, `--ramsize`, and
  `--trace-calls` (breakpoints by symbol, re-armed for each program RUN386
  runs under 0x0C: `ADDDRV.EXP` comes first).

fmtownskit at 9c1ccd3 (the submodule pulled at the session's end).
