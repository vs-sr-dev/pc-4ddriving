# 11 - The runtime

The game's code and TBIOS's, recompiled (`09-recompiler.md`), running on
fmtownskit's FM Towns runtime, headless or in a window: `build/rt/4ddriving`
runs the program from its first instruction.

```sh
python -m fmtownskit.recomp --out build/game ...        # 09-recompiler.md
cmake -S . -B build/rt -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/rt
build/rt/4ddriving --headless --frames 3600 --png-every 60 --input 100-118:a,400-418:a
```

Options (`src/main.cpp`): `--cue`, `--headless`, `--frames N`, `--png F,...`,
`--png-every N`, `--out DIR`, `--input F-G:BUTTONS`, `--wav`, `--mute`,
`--trace-int`, `--trace-io`, `--trace-from F`, `--vram F` (VRAM and sprite
RAM at frame F, as the oracle's `tools/vramdump.lua` writes them),
`--scale`, `--fullscreen`; since session 4 `--save DIR` (the host's floppy
drives, A: in DIR/a: the user disk, `13-game.md`), `--font FILE` (the
font ROM, `bios/fmtowns/fmt_fnt.rom` by default), `--ram F` (the program's
segment at frame F, to `prog.bin`, against the oracle's `--dump`), and
`--replay-sound LOG --seconds S --wav FILE` (the oracle's sound log through
the runtime's chips, `12-sound.md`). The recompiled modules are checked
against the disc at the start (each one's CRC32 against the file's).

The window shows the picture only, without the border MAME's frame keeps
(320x200 modes come in an 800x440 frame, 640x480 ones in 704x525), every
mode at the same scale; `--crop` saves PNGs the same way (without it they
are MAME's whole frame, for the oracle). In the window: arrows, X = A (the accelerator), Z = B (the brake), Enter =
Run (the replay menu in a race), Right Shift or Backspace = Select; a
gamepad's d-pad, East, South, Start, Back; the mouse as the Towns' mouse;
F11 or Alt+Enter full screen, Tab held unpaced, Escape quits.

## Where it starts: the program's first instruction, read

`tools/oracle.py --dump-write b4d0c=34104` stops MAME's `fmtowns -ramsize 4M`
at the first write of 0x34104 to physical 0xB4D0C: the program's first
`call` (the entry `jmp`s to 0x340FF, `call 0x347b4`) pushing its return
address. MAME has decoded the call and not yet moved ESP, so the registers
are the ones RUN386 hands over. That happens **14.793 seconds** after
power-on, and there:

* every general register 0, EFLAGS 0x202, ESP 0x6BD10; CS 0x0C, DS ES FS GS
  SS 0x14, base 0x408000, limit 0x368FFF; selector 0x40 base 0, limit
  0x3F7FFF; FORRBIOS.NSD at linear 0x400000 (physical 0x3F8000) under 0x4C
  and 0x54 -- **the profile `towns4m+nsd` as session 2 read it**;
* the program's pages: 0x408000-0x479FFF on physical 0x49000-0xBAFFF, then
  one page at a time from the top of RAM down (0x3F5000, 0x3F4000...), the
  last 256 KB on 0xC0000;
* the image in RAM **the file's byte for byte**; past it, to the end of its
  page, 684 bytes of the file's symbol table (RUN386 reads by 512-byte
  sectors: the table's first sector twice); the rest of the segment zero
  but for RUN386's frame below the stack top (EIP 0x340A4, CS 0x0C, EFLAGS
  0x202: it enters by `iretd`);
* **TBIOS in RAM the disc's `TBIOS.BIN` byte for byte**; FORRBIOS.NSD's
  image differs from its file in 799 bytes (its data, run);
* the PSP at 0xBF060 (selectors 0x04, 0x24) and the environment at 0xBF020
  (0x2C, limit 0x2B): `PATH=`, `COMSPEC=C:\COMMAND.COM`, then `4ddfmt.exp`;
  no command tail -- not where the first game's boot put them;
* the machine: the PICs as the first game's; the CRTC the same but for
  register 28 (0x801F), video register 1 0x09, the 16-colour palettes'
  half-bright colours 0xB0 (the first game's boot: 0x80); VRAM all zero.

`src/main.cpp` declares the profile and sets those differences after the
kit's `townsos()` and `boot_run386()`.

## What the program asked for, and the answers

Read on the oracle with `tools/oracle.py --trace-calls` at every `int` of
the program, the instruction after each, and `_mwint21` (0x34E70, `int 21h;
ret`) and the `ret` after it: each call's registers in and out
(`tools/intlog.py` pairs them). The breakpoints are now armed at the
program's base from power-on: a base met at a frame's end comes after the
program's first calls.

* **DOS**: AH=30h answers EAX 44580A03h (DOS 3.10, and "DX" above it,
  which is how MetaWare's start knows Phar Lap) and EBX FF00h; AH=FFh DX=78h
  (another extender's test) leaves every register as it was; files opened
  (3Dh), asked for their device word (44h AL=00h: 0050h, a file on the
  CD's drive Q:), read whole (3Fh with ECX 1 MB), sought to their end (42h);
  the start's `TRACK.DAT`, `DEFAULT.HIG`, `DEFAULT.TRK`, `DEFAULT.RPL`, then
  the title's resources. No int 21h AH=48h and no int 31h in the oracle's
  first 30 seconds, and no int 31h in the runtime's first 80 (it would stop
  the run): the program asked RUN386 for all memory, and its heap lives in
  its own segment (`_mwexpand_heap`'s int 31h AX=0501h is for when it runs
  out).
* **Phar Lap**: 2502h and 2503h (get the vectors of 4Dh, the sound, and 24h,
  the critical error), 2506h (set them: TBIOS's warikomi takes 4Dh at
  0x16900; the game 24h and 23h, Ctrl-C).
* **The keyboard BIOS, int 90h** (FORRBIOS.NSD's; the game pushes "DOSX"
  "BIOS" before each call): AH 00h, 01h, 02h, 05h at the start; then each
  frame AH=09h (a key: DX FFFFh, BX FF00h, none) and AH=0Ah (the key matrix
  at DS:EDI); AH 0 for all.
* **KimG, int 8Eh AX=CF00h** (its client set, read and put back, around
  each file the game opens): EAX 0.
* **The CD BIOS, int 93h raised in protected mode** (FORRBIOS.NSD's; the
  buffer at DS:EDI, not a real-mode one as through 2511h): 53h (where the
  play is: AL 0, nothing playing), 54h (the table of contents, twice), 55h
  (pause), 56h (go on: AH=23h when nothing was paused), 50h (play: the logo's
  music from sector 4500, `cdr_mtplay`).

## The mouse

The first comparison left 4 pixels: a 2x2 white dot at the bottom right of
the user-disk prompt, on the oracle only. It is *Stunts*' own mouse pointer
(`mousecursor`, called every frame on the oracle), the mouse at (319, 199),
the corner of the bounds `setmousebounds` sets: **MAME's fmtowns has a mouse
in its second port** (an MSX mouse, beside the Towns pad in the first); the
game finds it and shows its pointer, which ends in the corner with no
movement at all (*not understood*: how the reading drifts there; it does the
same here). The kit's machine had two pads; it now has MAME's mouse
there (`runtime/towns_io.cpp`: the nibbles of the movement, one per change
of the port's strobe, a 3 ms pause starting over), and the dot is there.

## Held against the oracle

`tools/framematch.py` (from the first game; frame F is the oracle's 14.793 +
F/60 s): for each oracle snapshot, the runtime frame closest to it. Frames
are 800x440 on both. With the oracle's `--input 22-22.3:A,28-28.3:A` and the
runtime's `--input 100-118:a,400-418:a` (NO, twice):

* **the user-disk prompt at 20 and 22 seconds: the same, pixel for pixel**
  (the goal of the session), and the black screens before it (16, 18);
* the prompt again after the first NO (27), the black after the second (29,
  30), **Electronic Arts' logo** (31-36), the *4D Driving* logo turning
  (38, 40, 42), **the title** (46), the logo fading out (60, 65), **the
  original team's credits** (68), the title again (80): **26 snapshots of
  26 the same, pixel for pixel** (the black ones match any black frame; the
  others are the real comparison).
* **Timing**: the same pictures come sooner here -- 1 to 7 seconds before the
  prompt, 8.5 at the logo, 14 to 16 at the title and the credits: the runtime
  reads the disc at once, MAME at the drive's pace.

60 seconds of the game run in 0.58 seconds headless.

## Left open (`05-open-questions.md`)

The CMOS RAM read at 0x3B04 and 0x3B06 (answered 0; MAME's comes from its
NVRAM), port 0x24 (MAME: 0) and 0x5ED (unmapped), the key matrix's bytes
(*inferred*: zeros), the CD BIOS 53h's buffer (*inferred*: zeros while
nothing plays) and the table of contents' first byte, RUN386's leftovers past
the image (not written here), the boot's bytes in sprite RAM (DOS's, not
shown: the sprites are off).
