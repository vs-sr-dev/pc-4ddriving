# 04 - Curiosities

* **The program kept its names.** `4DDFMT.EXP` carries Phar Lap's symbol
  table, 2,047 names: *Stunts*' own functions as Distinctive Software named
  them in 1990 (`opponentcompile`, `drawblimpworld`, `carsplash`,
  `getprotection`, `RayNullFunction`...), MetaWare's library, and the
  Towns team's layer (`FMT_printpoly`, `fmtspeed`, `twomicechk`,
  `cdr_mphase`, `KimG_setclient`). A recompiler rarely gets function names
  for free; this one does, and its discovery takes them as seeds.
* **A Marty rerelease that the first Towns will not show.** Four months
  after the Towns release (HMD-222, 1993-03), Electronic Arts Victor put out
  HMD-222A for the Marty (1993-07). On MAME's first Towns it runs, waits at
  its first question, and shows nothing (`01-disc-layout.md`).
* **The user disk.** The Marty has a floppy drive and no hard disk: the game
  asks to make a "user disk" in A: for the tracks you build in the editor,
  the high scores and the replays, and asks again when you say no.
* **The original team** gets a screen of its own after the title: "Original
  Team" -- design Don Mattrick, Kevin Pickell, Brad Gour, Rob Martyn, Stan
  Chow; programming Kevin Pickell; technical support Brad Gour, Rick
  Friesen; music Michael J. Sokyrka, Kris Hatlelid, Brian Plank; art Nicola
  Swaine, Kevin Pickell, Mike Smith, David Adams (the oracle at 68 s).
* **A copy-protection function survives**: `getprotection` (0x13598), from
  the PC game's copy protection (*inferred*); whether the Towns build ever calls it is
  for the next session (the descent from the entry alone does not reach it).
* **A Weitek probe on a console.** MetaWare's start-up looks for a 387 and
  for a Weitek 1167/3167 (writes at offset 0xFFC0C000) before running a racing game
  on a machine with neither.
* **The BIOS answered in protected mode.** Fujitsu's CoCo and `ADDDRV`
  load `FORRBIOS.NSD`, which takes the keyboard, KimG and CD BIOS
  interrupts in 32-bit code, so that a RUN386 program need not drop to real
  mode for them (`03-executables.md`).
