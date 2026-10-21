# 02 - The data, at a glance

The game's files are *Stunts*' (the 1990 PC game) in the Towns' versions.
Session 1 read their headers only; the port runs the program's own code
over them, so a format matters here when a tool needs it, or when the
oracle and the runtime disagree.

## Resources: `.RES`, `.RVS`, `.RFS`, `.3SH`, `.VSH`, `.SLB`

One container for most things, *Stunts*' resource file:

    u32 the file's size     u16 n     n x 4-character names     n x u32 offsets

the offsets counted from the end of that table. The size field is the
file's size in every one of the 116 files of these six kinds (checked);
the names and offsets were read in four (`MAIN.RES` 34 entries, `CARANSX.RES`
4, `SDMAIN.RVS` 5, `STUNTS.SLB` 6), each offset inside its file.

| Kind | Files | Bytes | What, from the names (*inferred*) |
|---|---|---|---|
| `.RES` | 22 | 60,357 | text and tables: `MAIN`, `MAIN360`, `GAME`, `MISC`, `TEDIT` (the track editor), `OPP1`-`OPP6` (the six opponents), `CAR*` (eleven cars: `edes`, `gnam`, `gsna`, `simd` -- description, names, the car's simulation data) |
| `.RVS` | 52 | 2,183,915 | pictures with palettes (`!pal`, `!cg0`, `!eg0`, then the pieces): screens (`SDMAIN`, `SDTITL`, `SDMSEL`...), the car dealer's pictures (`STDA*`, `STDB*`), the scenery (`ALPINE`, `CITY`, `COUNTRY`, `DESERT`, `TROPICAL`), `EALOGO`, `TITLES`, `FINISH` |
| `.RFS` | 25 | 4,308,144 | more pictures, the big ones: the opponents (`ADR`, `ATH`, `CHR`, `KEV`, `LAR`, `MAS`, each `L`, `S`, `W`: ~280-400 KB for `L` and `W`), `3DBOX`, `3DBUT`, `EVALUE`, `SDMAIN`... The PC game's `.PVS`/`.PES` are packed; these are not |
| `.3SH` | 15 | 159,726 | 3D shapes: the track pieces (`GAME1`, `GAME2`: `bank`, `barr`, `btur`, `cfen`, ...), each car (`ST` + the car's code), `TITLE`, `STUFOO` |
| `.VSH` | 1 | 18,102 | `KEYBORD.VSH`: *inferred* a picture of the keyboard (the PC version's key help) |
| `.SLB` | 1 | 100,454 | `STUNTS.SLB`: the sound effects, `BLOW`, `CRAS`, `BUMP`, `SCRA`, `SPLA`, `BUBB` (the game's `carcrash`, `carbump`, `carscrape`, `carsplash`, `carbubble`, `blowengine`) |

## The others

| File | What |
|---|---|
| `.TRK` (38) | the tracks, 30x30: 10 of 1,802 bytes (*Stunts*' size: `DEFAULT` and ten `TRACK_nn`), 28 of 1,808 (six more bytes, zeros in the two read). The opponents' (`CHERRI`, `HELEN`, `HERROTTO`, `JOE`, `MASAHIKO`, `SKID`) and `VANCOUVR`; `TRACK_00` to `_29` are what the user disk gets |
| `DEFAULT.HIG` | high scores (starts `EAV`) |
| `DEFAULT.RPL` | a replay (starts `COUN`: the Countach) |
| `STUNTS.PMB` | 24,684 bytes, not a resource file (starts with eight zeros, then `ENGINE`): *inferred* the engine's PCM |
| `SDMTITL.PVS` | 11,180 bytes, not a resource file: *inferred* packed as the PC's `.PVS` |
| `FONTDEF.FNT`, `FONTLED.FNT`, `FONTN.FNT` | the game's fonts |
| `TRACK.DAT` | 33 bytes of `0`: *inferred* which tracks the user disk holds |
| `OAK2USR.DIC` | the kana-kanji dictionary's user part (TownsOS's; `DICINIT`) |

The CD-DA is the music (`01-disc-layout.md`).
