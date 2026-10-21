# 05 - Open questions

1. **Answered in session 2: memory** (`01-disc-layout.md`, `03-executables.md`).
   The 2 MB Towns leaves the program too little; with 4 MB it runs as on the
   Marty, with the disc's TBIOS. Kept below as session 1 wrote it. Still
   open: why a real 2 MB Towns leaves less than a 2 MB Marty (MAME's boot
   of each, not checked against the hardware), and whether "Marty/UX" in
   MAME's list means the same thing.
   Session 1: On MAME's `fmtowns` the program runs and polls
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
2. **The Marty ROM's TBIOS against the disc's** (read in session 2,
   `03-executables.md`): the graphic module byte for byte the same, the mouse
   module rewritten, and an extension at TBIOS+0x17000 wrapping the graphic
   and mouse entries. Open: what the graphic wrapper's AH=02h path does with
   port 0x3BB0 (*inferred*: the Marty's TV zoom; MAME maps 0x3BB0 to the
   CMOS RAM) and what the Marty's mouse module makes of the pad.
3. **Answered in session 3, for what the start uses** (`11-runtime.md`): the
   runtime answers int 90h, 8Eh and the CD BIOS's 53h-56h at the interrupt,
   as the oracle's trace shows FORRBIOS.NSD answering them. Still open: 91h,
   96h, 97h; the key matrix's bytes and 53h's buffer (*inferred*: zeros).
   Session 2: **FORRBIOS.NSD**: what each of its interrupts does (8Eh, 90h, 91h, 93h,
   96h, 97h), and whether the port answers them at the interrupt, as the
   first game's runtime answers int 93h, or recompiles the NSD (a P3 image,
   28 KB; compiled C, by the prologues read at 0054:126C). Its int 93h and the CD BIOS's
   53h, 55h, 56h (the first game never made them).
4. **Answered in session 3** (`11-runtime.md`): 2502h, 2503h, 2506h for 4Dh
   (TBIOS's warikomi takes it), 24h and 23h; KimG answers EAX 0; no int 31h
   so far. Session 2: **The program's other interrupts**: Phar Lap 2506h/2507h for which
   vectors (`SND_init`, `MOS_start`: the sound and the mouse), int 90h's
   keyboard as the Marty's pad reaches it, int 8Eh AX=CF00h (KimG),
   int 31h AX=0501h's memory.
5. **Answered in session 3** (`09-recompiler.md`): recompiled with TBIOS
   (its table runs to 0x1E0, and warikomi's own handlers are seeds); the
   timer A interrupt and the PICs they program not yet checked against the
   oracle (the sound's session). Session 2: **TBIOS's two modules the first game did not call**: fs:[0x1A0]
   (warikomi: AH=01h-04h and 07h, from `MOS_*`, `SND_*`,
   `SND_int_timer_a_set`) and fs:[0x1C0] (System:
   AH=30h, 31h). Recompiled with TBIOS they come free; their effect on the
   machine (timers, the PICs) is for the runtime.
6. **Answered in session 3** (`09-recompiler.md`): the 15 placed tables are
   read by discovery; eight code addresses passed as immediates are seeds;
   44 indirect transfers are left, none met yet by the runtime in 80
   seconds. Session 2: **The 51 indirect transfers** discovery leaves: 15 jumps through tables
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
13. **The CMOS RAM**: the start reads 0x3B04 and 0x3B06 (the runtime answers 0;
    MAME's come from its NVRAM, which the oracle keeps between runs under
    `build/oracle/nvram`). What they hold, and whether a fresh NVRAM and a
    used one give the same pictures.
14. **Ports 0x24 and 0x5ED**: read once each (MAME answers 0x24 with 0; 0x5ED
    is mapped to nothing there). Answered 0.
15. **The mouse pointer in the corner** (`11-runtime.md`): with no movement
    MAME's mouse reads 0 every time, and still the pointer ends at (319,
    199) on both machines -- how the program or TBIOS's mouse module gets
    there is not read. The port will want the pointer where the player's
    mouse is, or none.
16. **RUN386's leftovers**: past the image, the file's symbol table to the
    end of the page; below the stack top, RUN386's `iretd` frame. The
    runtime writes neither; nothing seen depends on them so far.
17. **The keyboard poll**: in some screens the program calls KYB_read in a
    tight loop (740,000 calls before a traced run here was cut short, 3,753 in the oracle's
    first 30): its count follows the CPU's speed, which the runtime's clocks
    only approximate.
