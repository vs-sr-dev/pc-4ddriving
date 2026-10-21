# pc-4ddriving

A native PC port of **4D Driving** (Electronic Arts Victor, 1993; FM Towns
Marty) -- *Stunts* (Distinctive Software, 1990) on Fujitsu's console -- by
static recompilation of its 386 code to C++ on fmtownskit (a submodule at
`fmtownskit/`; `git clone --recursive`). **BYOA**: nothing from the disc
is in this repository; you bring your own.

Status: **session 3** -- the game's code and TBIOS's recompiled and running
on fmtownskit's runtime, from the first instruction through the user-disk
prompt, Electronic Arts' logo, the title and the credits, every picture held
against the oracle (MAME's FM Towns with 4 MB) the same, pixel for pixel.
Silent, and not yet played: the sound and the game itself are next.

## Building

```sh
python -m fmtownskit.disc "disc/4D Driving (Japan) (FM Towns Marty Rerelease).cue" --extract build/disc
python -m fmtownskit.recomp --out build/game \
    --exp game=build/disc/4DDFMT.EXP@0c/3a650+20518,35018,3516c,35340,35474,35866,35a3c,37a58 \
    --raw tbios=build/disc/TBIOS.BIN@110:20-1e0+166a7,169d0,16ab0,16ae9,16aec,16afc,16b64
cmake -S . -B build/rt -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/rt
build/rt/4ddriving                                     # in a window (SDL3), or:
build/rt/4ddriving --headless --frames 3600 --png-every 60 --input 100-118:a,400-418:a
```

The runtime finds the disc's cue sheet in `disc/` (`--cue` for another).
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
```

The oracle runs MAME's `fmtowns` with 4 MB by default (`--machine fmtmarty`
for the Marty); the game first asks to make a user disk in drive A:, and
`--input` answers NO (twice).

## Documents

`docs/00-sessions.md` (the log), `01-disc-layout.md`, `02-data-formats.md`,
`03-executables.md`, `04-curiosities.md`, `05-open-questions.md`,
`06-attack-plan.md`, `07-next-session.md`, `09-recompiler.md`,
`10-fmtownskit.md`, `11-runtime.md`.

## Licence

MIT (`LICENSE`). The game and its system software are their owners'.
