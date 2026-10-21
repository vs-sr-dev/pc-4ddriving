# 03 - The executables

## 4DDFMT.EXP

`python -m fmtownskit.exp build/disc/4DDFMT.EXP`: a Phar Lap **P3** file,
level 1 (flat), 324,386 bytes; no relocations, no segment table.

| | |
|---|---|
| image | 290,132 bytes (0x46D54) at file offset 0x200, loaded at 0 |
| entry | **0x340A4**, the symbol `_mwINIT`: MetaWare High C's start-up |
| stack | top 0x6BD10, size 0x13880 (80,000 bytes, the header's field at 0x7C) |
| extra memory | minimum 0x24FBC bytes, maximum 0xFFFFFFFF (all there is) |
| symbols | at 0x46F54, 0x83CE bytes, to the file's end: below |

The header's "extra" fields are **bytes past the image, not pages**: image +
minimum = the initial ESP, here (0x46D54 + 0x24FBC = 0x6BD10) as in the first
game's `DUEL.EXP` (0x11F17 + 0x2009 = 0x13F20). And the maximum is honoured:
RUN386 gives the program all the memory left -- its segment's limit is
0x169FFF on MAME's `fmtowns` and 0x184FFF on `fmtmarty` (the dumps at 40 and
20 s), against the first game's 0x13FFF.

### The symbol table

Phar Lap's linker kept the symbols, at the header's symbols offset, past the
image ("SYM1"; `fmtownskit.exp` reads it since this session):

    00 'SYM1'  04 u16 14 (its header)  06 u32 44 (segments)  0a u32 33,684 (symbols)
    segments: [len][name][u32 0][u32 0xFFFFFFFF][u32 selector]   FLAT_CODE 0x0C, FLAT_DATA 0x14
    symbols:  [len][name][u32 offset][u16 1]                      2,047 of them

Read to the last byte of both sizes. The header's "file size" (290,658)
stops 14 bytes into the table, at the end of its own header: the reason the
kit refused the file before. All 2,047 symbols carry segment number 1; 1,702
lie in the image, 345 past it (the uninitialized data, to `_end`).

The names are *Stunts*' own (`opponentcompile`, `drawworld`, `carcrash`,
`trackeditor`...), MetaWare's library's (`_mw*`, `printf`, `malloc`...),
and a Towns layer the port's authors added: `FMT_*` and `fmt*` (VRAM
drawing), `EGB_*` (TBIOS graphics), `MOS_*` (the mouse), `KYB_*`, `SND_*`,
`cdr_*` (the CD BIOS), `KimG_*`, `twomicechk`, `fmtspeed`.

### Layout

| Range | What |
|---|---|
| 0x00000-0x3A650 | **code**: 1,218 symbols (1,211 addresses): the game to `ellipseh` (0x33490), then MetaWare's library (`fflush` at 0x337F8 on) with the Towns' libraries among it (`SND_*` from 0x355EC, `EGB_*`, `MOS_*`, `KYB_*`, `cdr_*`, `KimG_*` from 0x39C2C), `_strnicmp` at 0x3A554 the last |
| 0x3A650-0x46D54 | initialized data: it opens with MetaWare's marker symbols, all at 0x3A650 (`_mw387used`, `_mw87only`, `_mw1167used`, `_mw3167used`, `_fsoftonly`, `_mwfltused`...), then the colours (`Blue`, `Green`...), messages, tables; `_edata` at 0x46D54 |
| 0x46D54-0x58490 | uninitialized data, to `_end` |
| 0x58490-0x6BD10 | the stack |

The code is **compiled C** (`push ebp; mov ebp, esp` prologues, arguments
on the stack), but for the drawing routines (`fmtmovf`, `scalecf`, `drawcline`,
`intsin`, `s1linex`...), *inferred* hand-written: they jump through tables
placed right after the jump (`jmp cs:[ebx + table]`, the index already
scaled), with shared tails.

### Discovery, read

`python -m fmtownskit.recomp.discover build/disc/4DDFMT.EXP --report` (the
kit's decoder):

* from the entry alone: 721 functions, 54,509 instructions, 24 jump tables,
  0 refused, 0 conflicts;
* with every code symbol a seed (`--symbol-seeds 3a650`): **1,273 functions,
  66,927 instructions, 226,015 bytes; 25 jump tables (21 bounded by a
  compare); 51 indirect transfers left; 0 refused, 0 conflicts.**

`python -m fmtownskit.i386 ... --check --symbol-seeds 3a650`: the 68,033
instructions capstone's descent reaches, all decoded as capstone does.

Two things this game taught the kit (`10-fmtownskit.md`):

* **A table read without a bound ran into the next variable.** `interpretkey`
  calls `[ecx*4 + 0x41A48]` with ECX > 0 (a `jle` before): `keysubs`, at
  0x41A4C, 64 slots, all zero in the file (`interpretsub` fills them as it
  runs). The kit read on past it into `keyprog` (0x274CC), `joycalib`,
  `joyclock`... and took 0x20003 for a function -- the middle of an
  instruction in `opponentcompile`, the "undecodable at 0x20006" of the
  pre-analysis. With symbols, a read table stops at the next one.
* **The x87.** MetaWare's start-up (code after `_mwrestore_interrupts`,
  0x34252) probes for a coprocessor: `fninit`, the control word set to 0,
  `fnstcw`, and an FPU only if `cw & 0xF3F` reads 0x33F; then a Weitek
  (int 11h, then writes at offset 0xFFC0C000). The library's floating point has both
  paths (`_mw_87_*` and software). MAME's Towns (`I386`) and Marty
  (`I386SX`) have **no coprocessor**: an escape reads its ModRM and does
  nothing, so the probe finds none. 55 escapes and WAITs in the reached
  code, all in the library; none in the game's own. The kit now decodes the
  escapes and runs them as MAME does.

### What it touches

`python -m fmtownskit.x86map build/disc/4DDFMT.EXP --symbol-seeds 3a650`,
each site named by its function:

| What | Where |
|---|---|
| DOS (int 21h) | `savefilez`: 3Ch, 40h, 3Eh, 41h (create, write, close, delete); everything else through MetaWare's library, AH in a register (`SMALL?` at 0x34E70, `_mwcalldos`) |
| Phar Lap (21h AH=25h) | 02h/03h get a protected/real-mode vector, 04h/05h set them, **06h** (always in protected mode: `SND_init`, `MOS_start`, `criterr`, `ctrlc`), **07h** (`SND_end`, `MOS_end`) |
| DPMI-like | int 31h AX=0501h in `_mwexpand_heap` |
| int 11h | the Weitek probe (`_mwrestore_interrupts`) |
| int 90h | the keyboard: `KYB_init`, AH=01h, 02h, 05h, 06h, 07h, 09h, 0Ah (`KYB_setbuf`, `_setcode`, `_clic`, `_clrbuf`, `_inpchk`, `_read`, `_matrix`) |
| int 8Eh | AX=CF00h: `KimG_setclient`, `_getclient`, `_popclient` |
| CD BIOS (int 93h) | AH=00h, 02h, 50h, 52h, **53h, 54h, 55h, 56h** (`cdr_sdrvmd`, `_status`, `_mtplay`, `_mstop`, `_mphase`, `_cdinfo`, `_pause`, `_continue`) |
| TBIOS, far calls | fs:[0x20] graphic (`EGB_*`), fs:[0x40] mouse (`MOS_*`), fs:[0x80] sound (`SND_*`), fs:[0xA0] "ま～くん" (`putsjis`, `putsk8`, `putskana8`/`16`, `fmtspeed`), and two the first game did not use: **fs:[0x1A0] → 0x16680, the "warikomi" (interrupts) module** (`SND_init`, `SND_end`, `MOS_start`, `MOS_end`, `SND_int_timer_a_set`) and **fs:[0x1C0] → 0x160F0, the "System" module** (`SND_init`, `SND_end`, `MOS_end`). The table on the disc's `TBIOS.BIN` has 0x1A8 → 0x16900 too, and 0x1E0/0x1E8 under selector 0x138 (the font ROM) |
| ports | the palette, 0xFD90-0xFD96 (`fmtpalette`, `vgapalette`, `getpalette`...); 0xFDA0, the video sub status (`vsyncstate`: bit 0 VBLANK); **0x5EC** (`fmtspeed`, below); 0x26 the microsecond counter, 0x24, 0x6C (a 1 µs wait), 0x4D6 the pad's lines (`twomicechk`); 0x3B04/0x3B06 in the CMOS RAM (`MOS_start`) |
| selectors | 0x14 its data, 0x34 the first megabyte (`crithandler`), 0x110 TBIOS (24 loads), 0x120 VRAM layered, 0x128 VRAM single-layer, **0xF8** (only after the Weitek probe succeeds: never on these machines) |

`fmtspeed(n)` reads port 0x5EC; if bit 7 is clear it writes `n` (0 or 1) to
it, and returns bit 0. MAME calls bit 0 "compatibility mode?"; the name says
speed. Called by `initmodes` and three times by `titles`.

### The start (0x340A4)

`_mwINIT` jumps over its last lines to its set-up at 0x340FF -- the
segment's limit (`lsl`), the coprocessor and Weitek probes, ... -- and those
lines are `call main` (0x340A6), then `push eax; call 0x34CE0` (`_mwhalt`):
*inferred* the set-up comes back to them. In `main`
(+0x1D8) `checkinstall` asks for the user disk (`01-disc-layout.md`); then
the logo, the title, the credits. To read in the next session with the
oracle (`06-attack-plan.md`).

## FORRBIOS.NSD, running

The disc's `AUTOEXEC.BAT` has `ADDDRV` load `HCOPY\FORRBIOS.NSD` (a P3 image
of 0x6DE4 bytes, 28,644 in the file) into selectors 0x4C (data) and 0x54
(code), 32 KB at linear 0x1F8000, just below the program's 0x200000. Read in
the dumps (`tools/oracle.py --dump`; IDT entries):

| int | fmtmarty | fmtowns |
|---|---|---|
| 8Eh, 90h, 91h, 93h, 96h, 97h | 0054:021C, 023C, 0246, 0250, 0264, 026E | the same |
| 07h, 11h, 21h, 31h, 40h-4Fh, FDh | RUN386 (0008:...) | RUN386 |

So the program's keyboard, KimG and CD BIOS calls **never go to real mode**:
`FORRBIOS.NSD` answers them in 32-bit code (*inferred* the name: a
protected-mode stand-in, "for", the real-mode BIOS). On the Marty at 20 s,
waiting at the user-disk prompt, the CPU is in it, on the program's stack,
under `messagebox` → `mykey` → `joystate` → `keystate`.

## TBIOS.BIN, RUN386.EXE, IO.SYS

The first game's, byte for byte (`01-disc-layout.md`), read in its
`03-executables.md`. On the Marty the TBIOS that runs is the Marty ROM's
build of the same version (the first game's session 2), not the disc's.
