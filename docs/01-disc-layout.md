# 01 - The disc

## Which disc this is

| | |
|---|---|
| Title | 4D ドライビング / 4D Driving: *Stunts* (Distinctive Software, 1990), brought to the FM Towns |
| Publisher | Electronic Arts Victor (the volume's publisher field says `ELECTRONIC_ARTS`) |
| Platform | FM Towns Marty (MAME's list: "Only works on the 386SX-based models (Marty/UX)") |
| Serial | **HMD-222A / EFT-7005**: the Marty rerelease; the first release is HMD-222 / EFT-7002 |
| Volume | `4D_DRIVING`, system id `HMD-222A`, mastered by "FUJITSU LTD HYPER MEDIA DEVELOPMENT CENTER", dated 1993-06-11 15:00 |
| Release | the list says 1993-07 for this one, 1993-03 for the first |
| The program | `4DDFMT.EXP`, linked with MetaWare High C and Phar Lap's linker, its symbols kept (`03-executables.md`) |

Checked: every track's size, CRC32 and SHA-1, and the cue sheet's, are the
ones MAME's software list (`fmtowns_cd.xml`, entry `4ddrivinm`, "4D Driving
(FM Towns Marty version)", origin redump.org) gives -- 13 of 13; and the
CHD that `tools/oracle.py` makes from the cue sheet has the list's SHA-1
(`fa4dc65e57a643b3b717454515318a3552a88f39`; the tool checks it).

### Towns or Marty?

This time the disc is a **Marty title**, and the oracle agrees:

* MAME's list has two entries: `4ddrivin` (HMD-222 / EFT-7002, 1993-03,
  "Requires 2 MB RAM") and its clone `4ddrivinm` (this disc, 1993-07, "Only
  works on the 386SX-based models (Marty/UX)"). The two have the same twelve
  track sizes, and every track's CRC differs, the eleven audio tracks' too
  (*not understood*: other audio, or the same at another write offset; we
  have only this disc).
* On MAME's `fmtmarty` it boots past the Marty's logo and asks "CREATE USER
  DISK?" at 20 s; answered NO twice, it shows Electronic Arts' logo (32 s),
  the helmet, the title (46 s), the car and the original team's credits
  (68 s) (`tools/oracle.py --at 22-70/2 --input 22-22.3:A,28-28.3:A`).
* On MAME's `fmtowns` (the first model, a 386DX) it loads the system
  (the Towns' logo and "システム読み込み中です" at 10 s), switches to a
  704x525 mode at 16 s and stays **black** to the end of the run (70 s),
  with the same two presses. It is not hung: from 20 to 40 s the program
  runs its keyboard polling (`normkey`, `KYB_read`, `testkey`, by a
  per-frame histogram of CS:EIP), *inferred*: waiting at a prompt it drew
  where the Towns does not show it. Why is `05-open-questions.md` 1.

The prompt is about the **user disk**: the game keeps its tracks, high
scores and replays on a floppy in drive A: (`a:track.dat`, `a:default.hig`,
`a:default.trk`, `a:default.rpl`, `A:TRACK_00` to `_29`; `checkinstall`,
`03-executables.md`). With none, NO is the answer, and the question comes
again once (`namedrive` calls `checkinstall` a second time, and NO is not
remembered).

## The tracks

`python -m fmtownskit.disc "disc/4D Driving (Japan) (FM Towns Marty Rerelease).cue"`:

| Track | Mode | First sector (INDEX 01) | Sectors | Length | Pregap |
|---|---|---|---|---|---|
| 01 | MODE1/2352 | 0 | 4,350 | 0:58.00 | 0 |
| 02 | AUDIO | 4,500 | 3,525 | 0:47.00 | 150 |
| 03 | AUDIO | 8,250 | 1,800 | 0:24.00 | 225 |
| 04 | AUDIO | 10,275 | 3,150 | 0:42.00 | 225 |
| 05 | AUDIO | 13,650 | 2,850 | 0:38.00 | 225 |
| 06 | AUDIO | 16,800 | 3,075 | 0:41.00 | 300 |
| 07 | AUDIO | 20,175 | 2,475 | 0:33.00 | 300 |
| 08 | AUDIO | 22,875 | 3,150 | 0:42.00 | 225 |
| 09 | AUDIO | 26,325 | 375 | 0:05.00 | 300 |
| 10 | AUDIO | 27,825 | 525 | 0:07.00 | 1,125 |
| 11 | AUDIO | 29,700 | 3,375 | 0:45.00 | 1,350 |
| 12 | AUDIO | 33,300 | 3,000 | 0:40.00 | 225 |

* The ISO volume is 4,127 blocks of the data track's 4,350.
* Every track is a whole number of seconds; the pregaps are **silent** (peak
  0, or 7-8 in tracks 6 and 9), unlike the first game's.
* Eleven short CD-DA pieces, 5 to 47 seconds: *inferred* the music, looped
  by the program (`cdr_mtplay`, `cdr_mphase`, `cdr_pause`, `cdr_continue`:
  the CD BIOS's 50h, 53h, 55h, 56h; `gCDTrackTime`); which plays where is
  for the oracle.

## The data track

196 files in 5 directories (`build/disc` after `--extract`). Sector 0 is
the IPL (`IPL4`, then a jump to +0x5B), as on the first game's disc.

The boot chain, as the files say it:

| Step | File | What it is |
|---|---|---|
| 1 | sector 0 | the IPL |
| 2 | `IO.SYS` (77,824) | Towns-DOS 3.58: **the first game's, byte for byte** |
| 3 | `CONFIG.SYS` | `SHELL=C:\COMMAND.COM C:\ /P`, `DEVICE=\SYS\CTL.SYS`, `DEVICE=TBIOS.SYS /TBIOS.BIN`, `DEVICE=TOWNS.SYS`, `BUFFERS=8`, `FILES=20` |
| 4 | `TBIOS.SYS`, `TBIOS.BIN` | "V31L31 92/11/11": **the first game's, byte for byte** (`TBIOS.BIN` CRC32 FF49BC89) |
| 5 | `AUTOEXEC.BAT` | `C:MSCDEX /D:TOWNS_CD /M:8 /L:Q`, `\T_TOOL\MS_KANJI`, `\HCOPY\COCO`, `\SYSINIT\SYSINIT`, `\HCOPY\COCO_MEM`, `\RUN386 \HCOPY\ADDDRV \HCOPY\FORRBIOS.NSD`, `\T_TOOL\DICINIT`, then `\run386 4ddfmt`; on an error, `\T_TOOL\DELVDISK` and `\T_TOOL\REIPL` |
| 6 | `HCOPY\COCO.EXE` | "CoCo (Code of Co-native os) Version 1.8 E04", Fujitsu 1990-1992 (the TownsOS DOS-Extender staff): a resident base for protected-mode drivers |
| 7 | `SYSINIT\` | "FM Towns V1.0 L20", Fujitsu 1991-1992, with `SYSTEM.FNT`, `.ICO`, `.MSG`, `.SKB`: *inferred* TownsOS's system set-up for programs that use its fonts, icons and soft keyboard |
| 8 | `HCOPY\ADDDRV.EXP` + `FORRBIOS.NSD` | "AddDrvForNSDD", Fujitsu 1990-1991, MetaWare High C: loads the NSD driver `FORRBIOS.NSD` (a P3 image) into CoCo, at **selectors 0x4C (data) and 0x54 (code)** (`NSDDLOAD.SCR`: `nsddload q:\hcopy\forrbios.nsd 4CH,54H,...`). Read running: it answers int 8Eh, 90h, 91h, 93h, 96h, 97h in protected mode (`03-executables.md`) |
| 9 | `RUN386.EXE` (78,496) | "386\|DOS-Extender Version 1.2aJ L50": **the first game's, byte for byte** |
| 10 | `4DDFMT.EXP` (324,386) | the game |

`HCOPY\FORRBIOS.EXE` is "forRBIOS Loader(CD)" (Microsoft C), which loads the
same NSD when the IPL drive is the CD; `ADDRBIOS.BAT` and `DELRBIOS.BAT`
add and remove it by hand; `DELDRV.EXP` is ADDDRV's opposite.
`DRIVE_R.IMG` (131,072 bytes) holds a "TOWNES SYSTEM V21L20" volume dated
1992-11-13 with a copy of RUN386 in it: *inferred* a system RAM disk image,
not the game's (the game's own "RAM drive" is memory, `Ram_file`).
`4DDFMT.ODR` lists 163 of the disc's files, the program first: *inferred*
the order they were laid on the disc in. `T_TOOL\` holds TownsOS tools
(`MS_KANJI`, `DICINIT`, `DICUTY`, `DELVDISK`, `REIPL`).

Everything else is the game's (`02-data-formats.md`).
