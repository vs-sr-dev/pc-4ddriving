# 07 - Next session

Where session 4 left it: the sound held against the oracle (`12-sound.md`:
no FM in this game; the CD-DA at correlation 0.99998 and 0.997, the
engine's PCM with the oracle's loudness and spectrum); the game played
headless (`13-game.md`): the menus, the opponents' cards the same pixel for
pixel, a race driven for 28 seconds the same as the oracle's but for the
clouds, the replay menu, the track editor opened, the user disk made on the
host and found again. The window has the pad and the mouse.

Goal: **played by the user** -- the window, the eyes and the ears -- and
the game's other roads to their ends.

## TODO

### 1. Played

- [x] The user played in the window, from the pad: everything works, a
      race finished and a best time saved as SAM; the window showed the
      3D a scale smaller than the menus (MAME's 800x440 frame), now the
      picture only, at one scale.
- [ ] The mouse in the menus and the editor (not tried by the user).
- [ ] The gears (up and down) and the car screen's AUTO
      (`05-open-questions.md` 19); DRIVING DEVICE in the options (the
      mouse as the wheel: `mousesteer`, `mousedrive`).

### 2. To the ends

- [ ] A race to the finish held against the oracle (the user finished one
      and saved a best time to A:): the end screens, the CD-DA that plays
      there (`05-open-questions.md` 9).
- [ ] The replay: played, saved to A: and loaded back (the replay menu's
      SAVE and LOAD, the options' LOAD REPLAY; `floadreq`'s file list by
      4Eh/4Fh on A:).
- [ ] The track editor: a track made, saved, raced.
- [ ] An opponent's race (not the time trial); the tournament
      (PRACTICE/TOURNAMENT); GRAPHIC LEVEL.
- [ ] Held against the oracle where the pictures are still; the oracle with
      a floppy image in A: if a road needs it (`05-open-questions.md` 7).

### 3. Then

- [ ] At the user's word: the commit of this session (fmtownskit first).
- [ ] Publication, when the user says it is playable: the kit and both
      games together (`workflow-rules`).

## Tools

`tools/oracle.py` (`fmtowns` with 4 MB; `--sound-log`, `--wav`,
`--trace-calls` -- each line with 12 bytes at DS:EDI and 16 at DS:EDX --,
`--dump`; **one run at a time**: the NVRAM is shared). The menus on the
oracle: `--input 22-22.3:A,28-28.3:A,62-62.3:A` reaches the main menu at
68 s; A on GO! at 90 s starts a race, A held from 110 s drives. On the
runtime: `--input 100-118:a,400-418:a,1980-1998:a` reaches it at frame
2220, GO! at 2400, A from 3349 is the oracle's 110 s; **`--save` an empty
directory for these times** (with a user disk there, no prompt, and the
times move); presses of 6 frames move the menus one place.
`tools/framematch.py` (frames against snapshots), `tools/wavmatch.py`,
`tools/wavbands.py`, `tools/fps.py`. Python that holds a backslash goes in
a file written whole, never in a shell heredoc; run the tools with
`C:/Python314/python.exe`.
