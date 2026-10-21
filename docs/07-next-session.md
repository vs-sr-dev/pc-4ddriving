# 07 - Next session

Where session 3 left it: the program and TBIOS recompiled and running on the
kit's runtime, from the first instruction through the user-disk prompt,
Electronic Arts' logo, the title and the credits, **every oracle snapshot the
same, pixel for pixel** (`11-runtime.md`); the self-test 56,974 vectors, 0
failures (`09-recompiler.md`). Committed: fmtownskit 959818b, this port's
"Session 3" on it.

Goal: **the sound, then the game played** -- the title's music and the
engine heard as the oracle plays them, then the menus and a race driven with
the pad.

## TODO

### 1. The sound

- [ ] The oracle's `--sound-log` and `--wav` over the logo and the title
      (the CD-DA from sector 4500 at the logo; which track, `01-disc-layout.md`).
- [ ] TBIOS's warikomi and the timer A interrupt (`SND_int_timer_a_set`,
      `timerint`, `timerintb`: the game's handlers through `call eax`): the
      YM3438's timer A raising IRQ13 as MAME's, and the handlers run at the
      oracle's rate.
- [ ] The engine's PCM (`STUNTS.PMB`, `SND_pcm_bank_load`) and the FM
      (`STUNTS.SLB`): `--wav` against the oracle's, as the first game's
      `12-sound.md`.
- [ ] The CD BIOS's 53h buffer while a track plays (where the play is:
      the game may loop the music by it), read on the oracle.

### 2. The game

- [ ] The pad through the title and the menus (the oracle with `--input`):
      the car selection, the track selection, a race started; frames held
      against the oracle where the pictures are still.
- [ ] The race: the 3D world (`drawworld`, `projectc`, the placed tables),
      the replay, the track editor; where the computer's timing makes the
      pictures drift, held by eye.
- [ ] The user disk (`05-open-questions.md` 7): A: as a host directory; the
      prompt answered YES makes one.
- [ ] The CMOS RAM read at 0x3B04/0x3B06 (`05-open-questions.md` 13).
- [ ] The mouse: the pointer where the host's mouse is, or hidden
      (`05-open-questions.md` 15).

### 3. The window

- [ ] The kit's SDL3 window and the pad (it opens already: `4ddriving`
      without `--headless`); the pace of the Marty against the Towns' 16 MHz
      (`06-attack-plan.md`, risks).

## Tools

`tools/oracle.py` (`fmtowns` with 4 MB by default; `--trace-calls` armed
from power-on at the program's base, its log written frame by frame;
`--dump-write`, `--dump`, `--lua tools/vramdump.lua` for VRAM and sprite
RAM; `--input 22-22.3:A,28-28.3:A` answers NO twice). `tools/intlog.py`
pairs a trace of every `int` site and the instruction after it into calls
with their registers in and out. `tools/framematch.py` holds the runtime's
frames against the oracle's snapshots (frame F is the oracle's 14.793 + F/60
s). The runtime: `build/rt/4ddriving --headless --input 100-118:a,400-418:a`
(NO twice), `--trace-int` (to a file: the keyboard poll is busy),
`--vram F`. Python that holds a backslash goes in a file written whole,
never in a shell heredoc; MSYS2's PATH puts its own Python first: run the
tools with `C:/Python314/python.exe`.
