# 13 - The game, played

Session 4. The menus, a race, the replay, the track editor and the user
disk, on the runtime and on the oracle, with the pad (`--input` on both;
the window's keyboard, gamepad and mouse: `towns_sdl.h`).

## The way in

On both machines, answered NO twice at the user-disk prompt: the logo, the
intro (the red car, the helmet, the *4D Driving* logo), the credits, the
title; the title gives way to the main menu by itself after about 18
seconds ("Towns-PAD ON", "PLEASE WAIT"). **A on the *4D Driving* logo goes
straight to the menu** (the oracle at 62 s, the runtime at frame 1980).

The main menu's five icons: the opponent, the car, **GO!** (the cursor's
place), the track, the options; left and right move the cursor, a held
button repeats every 0.2 s on both, A chooses. Presses of 6 frames (0.1 s)
move it one place on both.

| Screen | What it holds | Held against the oracle |
|---|---|---|
| the car | the car turning on its stand, its figures and power curve, EXIT, NEXT, LAST, AUTO (the gearbox), COLOR; NEXT from the Countach (`DEFAULT.RPL`'s `COUN`) to the Ferrari GTO | the panels the same; the car's angle differs (it turns with the time, and each machine draws other steps of it) |
| the opponent | "タイム・トライアル" with the stopwatch, then each driver's card (Skid Vicious: name, age, height, years, his story) from the font ROM's kanji | **9 snapshots of 9 the same, pixel for pixel** |
| the track | the track's name, its fastest time and car, its map; SELECT, EDIT, EXIT; it needs the user disk (the tracks live on A:) | runtime only |
| the track editor | the grid, the pieces, HORIZON, LOAD, NEW, SAVE, EXIT; the cursor moves | runtime only |
| the options | "4D DRIVING Version 1.0 (Jan 18 1993)": PRACTICE/TOURNAMENT, GRAPHIC LEVEL, DATA DRIVE, LOAD REPLAY, DRIVING DEVICE, EXIT | runtime only |

The opponents' screen reads the Towns' font ROM at 0xC2100000 on (MAME's
`fmtowns` set's `fmt_fnt.rom`, BYOA in `bios/fmtowns/`, the first game's;
another dump's `FMT_FNT.ROM` differs from it): without it, the cards have
no text.

## A race

GO! loads the default track and car: the camera flies in from the start
gate, then "FASTEN YOUR SEATBELT!" until the player moves. **On the pad, A
is the accelerator, B the brake, up and down the gears** (the gears read in
the code, not yet driven: up held alone races the engine and the car stays;
`moveeverything`:
the pad's branch with `joycalib` set, 1 accelerate, 2 brake, 0x10 and 0x20
the gears; the keyboard's is `kbdjoystate`), left and right the steering;
**Run opens the replay menu** (REPLAY, STATUS, RE-START, CONTINUE, LOAD,
SAVE, DISPLAY, MAIN MENU) over the replay's controls.

Held against the oracle (A held for 20 s from the same moment of the race,
`tools/framematch.py`): the fly-in the same pixel for pixel where both
draw the same step, the runtime 39.39 s sooner; then **28 seconds of
driving, the same road, the same places, the same clock**, out of the
track at 0:21 and the arrow pointing back, on both; 2 snapshots of 14 the
same pixel for pixel, the others differing **only in the clouds** (0.55-0.9%
of the pixels; a 15th fell past the frames saved): `game` places them by `cloudfudge = myrandom() << 3`, the
random generator seeded from the clock, and the race starts 39 seconds
sooner here.

## The user disk

The game keeps its tracks, best times and replays on a floppy in A:
(`checkinstall`): if `a:track.dat`, `a:default.hig`, `a:default.trk` and
`a:default.rpl` are there (`allexist`), it uses A: and asks nothing;
otherwise "CREATE USER DISK?" and "SET USER DISK ON DRIVE A:", and YES to
both makes one (`installa`: `diskaexist` opens `a:dummy`, "not found"
meaning a disk is there; `diskspace` wants 90,000 bytes free; then the four
files and the 30 tracks with their best times copied from the CD,
`copyq2a`, `installhigtrk`).

Here A: is a directory on the host (`--save DIR`, `save/a/` by default):
answered YES twice it holds `track.dat`, the `default.*` files and the
tracks (`track_00.trk` to `track_29.trk`, `cherri.trk`, `skid.trk`...); the
next start finds them and goes straight to the logo. On the oracle (no
floppy in MAME) only the prompts were seen.

What the game asked of DOS for it, new in the kit: **4Eh/4Fh** (find a
file: `loadshapea` tries a shape's names `.PVS`, `.PVX`, `.VSH` in turn
when a race loads; `installhigtrk`, `selectcar`, `floadreq`), **1Ah/2Fh**
(the DTA), **36h** (the free space). The DTA as the Towns' DOS fills it,
read in the oracle's RAM after a find on the CD: the drive ('Q' | 80h), the
name searched as 8.3, the attributes found (01h, read-only), the ISO
record's time and date, the size, the name; not found: AX=12h.

## The mouse

With no movement MAME's mouse reads zero every time, and the game's pointer
still sits at (319, 199): *inferred*, its first place is outside the
bounds `setmousebounds` sets and is brought to their corner. In the window
the host's mouse now moves the mouse in the second port (its movement in
the frame's pixels, the left and right buttons as its two), and the host's
pointer is hidden over the window: the game's pointer is the one seen.

## Played

The user played it in the window from the pad: "everything works",
"very playable" at its 15-20 pictures a second (the Towns' pace, the same
as MAME's: `12-sound.md`); a race finished and a best time saved as SAM
(`save/a/default.hig` rewritten). The corkscrews are still their
nightmare.

## A trap in the oracle

Two oracle runs at once shared one Lua script (`build/oracle/oracle.lua`):
both ran the later one's input, and a race "with up held" was in fact A
held (the pad read 0xAF there, A, not 0xBE, up). Each run now writes its
own script in its `--out`; the NVRAM (the CMOS RAM) is still shared, so
runs are made one at a time.
