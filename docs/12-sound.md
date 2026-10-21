# 12 - The sound

Session 4. What the game plays, read on the oracle, and the runtime's sound
held against it (fmtownskit's `runtime/towns_sound.cpp`, the first game's
`12-sound.md`: the RF5C68, ymfm's YM3438, the CD's audio, MAME's mix).

```sh
python tools/oracle.py --at 30,46,68,100 --sound-log --wav build/oracle/sound/towns.wav \
    --out build/oracle/sound/towns --input 22-22.3:A,28-28.3:A
build/rt/4ddriving --replay-sound build/oracle/sound/towns/sound.log --seconds 100 --wav build/sound/replay.wav
build/rt/4ddriving --headless --frames 5100 --input 100-118:a,400-418:a --wav build/sound/rt.wav
python tools/wavmatch.py build/oracle/sound/towns.wav build/sound/rt.wav --at 40 --len 10
python tools/wavbands.py build/sound/replay_nocd.wav 55.3 build/sound/rt_nocd.wav 26.28 3.6
```

`tools/wavmatch.py` finds the delay between two WAVs (their loudness
envelopes, then the samples) and gives the correlation, the gain and the
residual; `--lag` when the envelopes would lock onto another piece.
`tools/wavbands.py` compares the power band by band, where the samples
cannot line up.

## What the game plays

The oracle's sound log over the logo, the title, the menus and a race
(`--sound-log`: every write to ports 0x4C0-0x4FF and to the wave RAM):

* **The FM is never keyed on.** TBIOS's `SND_init` writes every channel's
  registers at 15.34 s and keys them off; in the logs of the logo, the
  title, the menus (to 160 s) and a race driven (to 140 s), no key-on. **The YM3438 is the game's clock**:
  timer A every 10.008 ms (registers 0x24/0x25: 468) and timer B every
  10.080 ms (0x26 = 0xDD), register 0x27 written 0x3F at each interrupt
  (16,785 times in the first 100 s), TBIOS's warikomi calling the game's
  `timerint` (Stunts' `ticks`, at 100 Hz). `STUNTS.SLB` is not FM voices:
  `startcarsfx` loads it as data and hands it to `initengine` (*inferred*:
  the engines' tables); `STUNTS.PMB` is the PCM bank (`SND_pcm_bank_load`).
* **The PCM**: the engine (`engineon`, `updateengine`: `SND_key_on`,
  `SND_pitch_change`, channel 0), the skids (`startskid`, channel 7: heard
  where the car lands after a jump, *inferred*); the crashes, bumps,
  scrapes and splashes only change a volume. In the intro, the red car's
  engine revs (channels 0 and 1, 50.2-54.4 s and 55.1-59.1 s); in a race the
  engine from the start line on.
* **The music is CD-DA** (`01-disc-layout.md`'s tracks): from 4,500 to 8,249
  with the logo (track 2, to the end of track 3's pregap; the command at
  36.57 s); from 8,250 to 10,274 in the menus (track 3), **played once**,
  then silence; in a race the CD stopped.
* TBIOS sets the CD's left and right volumes (0x4E3/0x4E2 selectors 4 and
  5) to 0x3F; the game fades them in and out in steps of 0x0C-0x0D, one per
  timer tick (`cdupdatefade`, `SND_elevol_set`).

## Held against the oracle

| Stretch | Against MAME's WAV |
|---|---|
| the oracle's log replayed (`--replay-sound`), 40-70 s: the title's CD-DA and the engine's PCM | correlation 0.9987, gain 0.9988, residual 0.26% (MAME's 2-sample lag) |
| the game, the title's CD-DA (oracle 40-50 and 60-75 s) | correlation 0.99998, gain 1.0000, residual 0.003%; 14.02 s sooner (the loads) |
| the game, the menu's CD-DA (oracle 70-90 s) | correlation 0.997, residual 0.6%, even across the stretch (*inferred*: the play starts at another fraction of a 48 kHz sample) |
| the game, the intro's engine (the CD muted, 3.6 s) | RMS 1,908.6 against 1,911.6; 99.4% of the energy under 2 kHz, the bands 0.76-1.09 of the oracle's |
| the game, a race driven (18 s from the start line) | RMS 1,964.2 against 1,963.5; the bands to 10 kHz 0.997-1.002 |

The engine's PCM cannot line up sample by sample: its pitch follows the
game's own time. In the intro the oracle's and the runtime's pitch writes
(0x4F2/0x4F3) are the same values for 337 writes, then a frame shifted
here and there; the two engine sounds last 4.28 and 4.15 s, then 4.01 and
4.01, with the same gap.

## The CD BIOS while a track plays

The game asks where the play is (`cdisbusy` → `cdr_mphase`, int 93h 53h)
before reading a file (`loadfileata`: if busy, `cdfadeto` and `cdpause`),
in the title (`while (cdisbusy())`) and in the menus' `songover`. Read on
the oracle at every int 93h of `cdr_*` and the instruction after it:

* **53h**: AL **1 while a track plays, 0 paused or stopped**; the buffer
  [1] the track, [3..5] the position from the play's first sector, [7..9]
  the sector as a binary MSF with no lead-in (MAME's CD answers so: its own
  comment calls it incorrect), while it plays or is paused; all zero once a
  track has ended or before any (before the first play, the bytes the last
  data read left: 03 01 0C 08 06 00 80 02 00 01).
* **55h** (pause): AH 0, even with nothing playing; **AH=22h when paused
  already**.
* **56h** (go on): AH=23h when nothing is paused.

The title to the menu, on both now: 53h → 1, 55h, 55h → 22h, 56h, 53h → 1,
55h, 53h → 0, 50h (the menu's track). The runtime answered 0 always before;
nothing the snapshots showed had changed, the order of the calls had.

## The pace

The game draws a 3D picture every 5 or 6 VSYNCs in a race on both
machines (two seconds of driving: 19 pictures on the oracle, 20 here, with
partial updates between them: 17 and 9 of one VSYNC; `tools/fps.py`): the
kit's clock for the 386 (the datasheet's figures per instruction) keeps
this game at MAME's pace.
