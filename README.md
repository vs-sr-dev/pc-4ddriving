# pc-4ddriving

A native PC port of **4D Driving** (Electronic Arts Victor, 1993; FM Towns
Marty) -- *Stunts* (Distinctive Software, 1990) on Fujitsu's console -- by
static recompilation of its 386 code to C++ on fmtownskit (a submodule at
`fmtownskit/`; `git clone --recursive`). **BYOA**: nothing from the disc
is in this repository; you bring your own.

Status: **session 2** -- the disc identified and read, the program mapped
by its own symbol table (1,273 functions, discovery clean), and the machine
chosen: a "Marty only" title that MAME's FM Towns runs as the Marty does once
it has 4 MB (the 2 MB Towns runs out of memory), with the disc's own TBIOS.
Nothing runs yet.

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
```

The oracle runs MAME's `fmtowns` with 4 MB by default (`--machine fmtmarty`
for the Marty); the game first asks to make a user disk in drive A:, and
`--input` answers NO (twice).

## Documents

`docs/00-sessions.md` (the log), `01-disc-layout.md`, `02-data-formats.md`,
`03-executables.md`, `04-curiosities.md`, `05-open-questions.md`,
`06-attack-plan.md`, `07-next-session.md`, `10-fmtownskit.md`.

## Licence

MIT (`LICENSE`). The game and its system software are their owners'.
