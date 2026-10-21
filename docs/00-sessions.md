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
