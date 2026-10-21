# 10 - fmtownskit

The kit this port is built on, and what this port has brought to it. The
kit's own README lists every module and its checks; this file is the log.
fmtownskit was born with the first game (pc-thequeenofduellist, its
`docs/10-fmtownskit.md`); this is its second.

## Session 1

The submodule was added at the kit's last commit, **be56af1** (the first
game's session 4); the changes below are the kit's commit **a33c4f2**, pulled
into it at the session's end.

| Change | What this game asked of it |
|---|---|
| `exp` | **the symbol table** ("SYM1": segments, then `[len][name][u32 offset][u16 segment]`), read to its sizes' last byte; a file taken when the table reaches its end (the header's file size stops at the table's own header); `--symbols`; `Exp.names()`, `Exp.table_end()`. The "extra" fields are **bytes**, not pages (image + minimum = ESP on both discs), renamed `min_extra`, `max_extra` |
| `x86map` | a read table stops at the next symbol (`keysubs`, which the descent overran into a mid-instruction 0x20003); `--symbol-seeds END`; each site named by the function it lies in |
| `recomp.discover`, `recomp.__main__` | the same bound for read tables; `--symbol-seeds`; a P3 program's symbols bound its tables in the recompiler too |
| `i386` | **the x87's escapes** decoded as `esc N, r/m`, as a 386 with no coprocessor runs them (MAME's `i386_escape`), instead of refused; `--check` holds them against capstone's x87 reading (length and address, a 16-bit address modulo 64 KB); `--symbol-seeds`; the sweep counts the escapes capstone has no x87 reading for apart |
| `i386emu`, `recomp.emit` | `esc` does nothing (3 clocks, as MAME's); set aside in the unicorn check, which has an FPU |
| `towns` | ports 0x24, 0x26 (the microsecond counter), 0x28, 0x30, 0x32, 0x5E8, 0x5EC, 0x6C (a 1 µs wait), the palette 0xFD90-0xFD96, the digital palette, 0xFDA0 (the video sub status), the CMOS RAM at 0x3000-0x4FFF -- from MAME's driver |

Checked on this game: discovery with every code symbol a seed, 1,273
functions and 66,927 instructions, 0 refused and 0 conflicts; the decoder
on the 68,033 instructions capstone's descent reaches, 0 differences. On
the first game, unchanged: its 7,903 instructions, 0 differences. The
random sweeps: the decoder's 300,000 (the same 11 differences as before
the change, all capstone's readings of prefixes; the 8,698 x87 encodings
it refused before and capstone read, now all agreeing; 1,159 that both
refused, now escapes capstone has no reading for), the interpreter's 163,924 vectors against unicorn, 0 differences;
its ten known answers, 10 of 10. The recompiler on the first game and its
TBIOS: the C++ byte for byte what the kit at be56af1 writes; the optest, with
116 escape forms more, 7,652 functions and 22,909 vectors, built with clang
and replayed: 0 failures.

## Session 2

| Change | What this game asked of it |
|---|---|
| `runtime/towns.h` `Profile`, `towns_mem`, `towns_dos`, `towns_io` | **a machine profile as data**: the RAM size (port 0x5E8), the program's segment (linear base, physical, its limit when the P3 asks for all memory), selector 0x40's limit. `boot_run386`, Phar Lap 250Fh and port 0x5E8 read it. The kit ships `kTowns2M`, read under the first game; a program asking for all memory under a profile that has not read how much is refused. This game asks for all memory, and on MAME's 2 MB Towns runs out of it: its port runs a 4 MB Towns |
| `towns.PROFILES` | the profiles read so far, with where: `towns2m` (the first game), `towns2m+nsd`, `towns4m+nsd`, `marty2m+nsd` (this game's boot, `FORRBIOS.NSD` keeping the top 32 KB) |

Checked: the first game, built on the changed runtime, against its oracle's 15
stills: all the same, pixel for pixel, as before.

The kit's commit **9c1ccd3**, pulled into the submodule at the session's end.
