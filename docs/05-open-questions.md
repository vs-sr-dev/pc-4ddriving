# 05 - Open questions

1. **Why only the Marty?** On MAME's `fmtowns` the program runs and polls
   the keyboard on a black screen (`01-disc-layout.md`). What is known:
   `fmtscreenmode(n)` asks TBIOS's graphic module (fs:[0x20] AH=01h, through
   `EGB_resolution`) for screen modes **10, 12, 13, 15** (its table at
   0x46320: 12, 13, 12, 13, 10, 15), and afterwards the video registers
   differ completely between the two machines (the dumps' `ports.txt`: video
   register 0 is 0x15 on the Towns, 0x0A on the Marty; CRTC registers 0-31,
   FF81, FF82). On the Marty the TBIOS that answers is the Marty ROM's own
   build; on the Towns, the disc's `TBIOS.BIN`. *Inferred*, to check: the
   disc's TBIOS does not set those modes on the first model (refused, or
   another layout), and the Marty ROM's does. Other candidates: `fmtspeed`
   (port 0x5EC), `twomicechk`, the machine id. **This decides what the port
   runs** (`06-attack-plan.md`).
2. **The Marty ROM's TBIOS against the disc's**, module by module: the
   graphic module's mode table, and what the 8 KB of wrappers do (the first
   game's session 2 found them: `fs:[0x20]` at 0x17BE0 calling the graphic
   module's 0xD20). With the ROM in `bios/` (`MAR_EX1.ROM` at 0x19C00), read
   both.
3. **FORRBIOS.NSD**: what each of its interrupts does (8Eh, 90h, 91h, 93h,
   96h, 97h), and whether the port answers them at the interrupt, as the
   first game's runtime answers int 93h, or recompiles the NSD (a P3 image,
   28 KB; compiled C, by the prologues read at 0054:126C). Its int 93h and the CD BIOS's
   53h, 55h, 56h (the first game never made them).
4. **The program's other interrupts**: Phar Lap 2506h/2507h for which
   vectors (`SND_init`, `MOS_start`: the sound and the mouse), int 90h's
   keyboard as the Marty's pad reaches it, int 8Eh AX=CF00h (KimG),
   int 31h AX=0501h's memory.
5. **TBIOS's two modules the first game did not call**: fs:[0x1A0]
   (warikomi: AH=01h-04h and 07h, from `MOS_*`, `SND_*`,
   `SND_int_timer_a_set`) and fs:[0x1C0] (System:
   AH=30h, 31h). Recompiled with TBIOS they come free; their effect on the
   machine (timers, the PICs) is for the runtime.
6. **The 51 indirect transfers** discovery leaves: 15 jumps through tables
   placed after the jump in the drawing routines (`jmp cs:[ebx + table]`,
   `jmp cs:[edi + table]`), 15 calls through a variable, 13 `call eax`, 8
   through the stack or EDI -- the
   `keysubs` handlers (filled by `interpretsub`), MetaWare's function
   pointers (`[0x44D68]`, `[0x43D40]`, `[0x43D44]`, `[0x43C30]`, the
   `_mweach_*` callbacks). The symbols seed most targets; the runtime will
   name the rest.
7. **The user disk**: what the port does with A: (a host directory, as the
   first game's save), and whether to answer "CREATE USER DISK?" for the
   player. `TRACK.DAT`, `TRACK_nn.TRK` of 1,808 bytes against 1,802.
8. **`fmtspeed`**: what port 0x5EC's bit 0 does on a real Marty (MAME keeps
   it and nothing else); the game sets it in `initmodes` and `titles`.
9. **The CD-DA**: which of the eleven tracks plays where (the oracle, with
   `--sound-log`).
10. **The two releases**: HMD-222's audio tracks have other CRCs than
    HMD-222A's at the same sizes; the first release's program would show
    what the rerelease changed for the Marty. Not on hand.
11. **`getprotection`** (0x13598): called or not on the Towns.
12. **The interpreter's check against unicorn on this program** was stopped
    at 8 GB of memory (`i386emu --check` over 55,000 instructions with 2
    states each): to run in slices.
