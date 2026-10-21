# pc-4ddriving

A native PC port of **4D Driving** (Electronic Arts Victor, 1993; FM Towns
Marty) -- *Stunts* (Distinctive Software, 1990) on Fujitsu's console -- by
static recompilation of its 386 code to C++ on fmtownskit (a submodule at
`fmtownskit/`; `git clone --recursive`). **BYOA**: nothing from the disc
is in this repository; you bring your own.

Status: **session 4** -- the game's code and TBIOS's recompiled and running
on fmtownskit's runtime, in a window or headless: the logo, the title, the
menus, races, the replay menu and the track editor, with the CD's music and
the engine's sound, held against the oracle (MAME's FM Towns with 4 MB):
the still pictures the same pixel for pixel, a race driven the same, the
music the same to a correlation of 0.997 and better. The user disk is a
directory on the host (`save/a/`). Being played.

## Building

```sh
python -m fmtownskit.disc "disc/4D Driving (Japan) (FM Towns Marty Rerelease).cue" --extract build/disc
python -m fmtownskit.recomp --out build/game \
    --exp game=build/disc/4DDFMT.EXP@0c/3a650+20518,35018,3516c,35340,35474,35866,35a3c,37a58 \
    --raw tbios=build/disc/TBIOS.BIN@110:20-1e0+166a7,169d0,16ab0,16ae9,16aec,16afc,16b64
cmake -S . -B build/rt -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/rt
build/rt/4ddriving                                     # in a window (SDL3): X accelerates, Z brakes
build/rt/4ddriving --headless --frames 3600 --png-every 60 --input 100-118:a,400-418:a
```

The runtime finds the disc's cue sheet in `disc/` (`--cue` for another), the
font ROM in `bios/fmtowns/fmt_fnt.rom` (MAME's `fmtowns` set; `--font`), and
keeps the user disk in `save/a/` (`--save`).
`docs/09-recompiler.md` and `docs/11-runtime.md` have what each step was
checked against.

## The disc

Redump's *4D Driving (Japan) (FM Towns Marty Rerelease)* (HMD-222A): a
cue sheet and twelve track files, in `disc/`. `docs/01-disc-layout.md` has
how they were checked.

## Tools

```sh
python -m fmtownskit.disc "disc/4D Driving (Japan) (FM Towns Marty Rerelease).cue"
python -m fmtownskit.disc "disc/4D Driving (Japan) (FM Towns Marty Rerelease).cue" --extract build/disc
python -m fmtownskit.exp build/disc/4DDFMT.EXP [--symbols]
python -m fmtownskit.x86map build/disc/4DDFMT.EXP --symbol-seeds 3a650
python -m fmtownskit.recomp.discover build/disc/4DDFMT.EXP --symbol-seeds 3a650 --report
python tools/oracle.py --at 20-70/2 --input 22-22.3:A,28-28.3:A   # MAME, CHDMAN, FMT_ROMS
python tools/oracle.py --machine fmtmarty --at 20-70/2 --input 22-22.3:A,28-28.3:A
python tools/oracle.py --dump 20 --ram 0x400000                    # CPU state and RAM, for fmtownskit.mamedump
python tools/oracle.py --at 16 --trace-calls windowdef,EGB_init    # the program's calls, by MAME's debugger
python tools/intlog.py build/oracle/.../calls.txt                   # a trace of int sites, paired into calls
python tools/framematch.py build/oracle/cmp/fmtowns build/frames --at 16,18,20,22   # frames against the oracle
python tools/oracle.py --at 100 --sound-log --wav build/oracle/towns.wav --input 22-22.3:A,28-28.3:A
python tools/wavmatch.py build/oracle/towns.wav build/sound/rt.wav --at 40 --len 10     # sound against the oracle
python tools/wavbands.py ORACLE.wav AT RUNTIME.wav AT LEN                                # band by band
python tools/fps.py build/oracle/fps/fmtowns build/frames/fps                           # pictures a second
```

The oracle runs MAME's `fmtowns` with 4 MB by default (`--machine fmtmarty`
for the Marty); the game first asks to make a user disk in drive A:, and
`--input` answers NO (twice).

## Documents

`docs/00-sessions.md` (the log), `01-disc-layout.md`, `02-data-formats.md`,
`03-executables.md`, `04-curiosities.md`, `05-open-questions.md`,
`06-attack-plan.md`, `07-next-session.md`, `09-recompiler.md`,
`10-fmtownskit.md`, `11-runtime.md`, `12-sound.md`, `13-game.md`.

## Licence

MIT (`LICENSE`). The game and its system software are their owners'.
