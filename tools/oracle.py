"""The oracle: the game on MAME's FM Towns or FM Towns Marty, with snapshots.

MAME runs headless and unthrottled with its configuration kept under
build/oracle (never the user's own), the CD as a CHD made once from the cue
sheet, and a Lua script that saves a snapshot at each time asked for, in
emulated seconds, then quits. A contact sheet of the snapshots is written
next to them.

    python tools/oracle.py --at 5-120/5                          # fmtowns with 4 MB
    python tools/oracle.py --machine fmtmarty --at 30,60,90       # the Marty, its own 2 MB
    python tools/oracle.py --at 20-70/2 --input 22-22.3:A,28-28.3:A   # the pad, held (NO twice)

The port's machine is the FM Towns with 4 MB running the disc's TBIOS (docs/06): MAME's
fmtowns with its 2 MB leaves the program too little memory (docs/05), so --ramsize defaults
to 4M on fmtowns and to the machine's own size elsewhere.

Environment: MAME (mame.exe; default: `mame` on PATH), CHDMAN (likewise),
FMT_ROMS (a directory with fmtowns.zip / fmtmarty.zip; default bios/).
"""
import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUE = os.path.join(ROOT, 'disc', '4D Driving (Japan) (FM Towns Marty Rerelease).cue')
CHD = os.path.join(ROOT, 'build', 'oracle', '4ddrivinm.chd')
CHD_SHA1 = 'fa4dc65e57a643b3b717454515318a3552a88f39'   # MAME's software list, 4ddrivinm

LUA = """local times = {%s}
local i = 1
emu.register_frame_done(function()
    if i <= #times and manager.machine.time:as_double() >= times[i] then
        manager.machine.video:snapshot()
        i = i + 1
        if i > #times then manager.machine:exit() end
    end
end)
"""

# At the first frame after AT seconds that ends in protected mode with paging
# on (RUN386 drops to real mode for DOS), the CPU state and physical RAM.
DUMP_LUA = """local at, size, done = %g, %d, false
emu.register_frame_done(function()
    if done or manager.machine.time:as_double() < at then return end
    local cpu = manager.machine.devices[":maincpu"]
    if (cpu.state["CR0"].value & 0x80000001) ~= 0x80000001 then return end
    done = true
    local f = io.open("state.txt", "w")
    for k, v in pairs(cpu.state) do f:write(string.format("%%s=%%x\\n", k, v.value)) end
    f:write(string.format("TIME=%%x\\n", math.floor(manager.machine.time:as_double() * 1000)))
    f:close()
    local sp, r = cpu.spaces["program"], io.open("ram.bin", "wb")
    for a = 0, size - 1, 0x10000 do r:write(sp:read_range(a, a + 0xffff, 8)) end
    r:close()
    dump_items()
    dump_ports()
    manager.machine:exit()
end)
"""

# At the first write of VALUE to physical ADDR, in protected mode with paging on: the
# CPU state and physical RAM at that very instruction (a program's first `call` at its
# entry pushes its return address: the state RUN386 hands the program, but for ESP).
WRITE_LUA = """local addr, value, size, done = 0x%x, 0x%x, %d, false
local cpu = manager.machine.devices[":maincpu"]
local sp = cpu.spaces["program"]
tap = sp:install_write_tap(addr, addr + 3, "oracle", function(offset, data, mask)
    if done or offset ~= addr or (data & mask) ~= value then return end
    if (cpu.state["CR0"].value & 0x80000001) ~= 0x80000001 then return end
    done = true
    local f = io.open("state.txt", "w")
    for k, v in pairs(cpu.state) do f:write(string.format("%%s=%%x\\n", k, v.value)) end
    f:write(string.format("TIME=%%x\\n", math.floor(manager.machine.time:as_double() * 1000)))
    f:close()
    local r = io.open("ram.bin", "wb")
    for a = 0, size - 1, 0x10000 do r:write(sp:read_range(a, a + 0xffff, 8)) end
    r:close()
    dump_items()
    dump_ports()
    manager.machine:exit()
end)
"""

# Every write to the sound ports (0x4C0-0x4FF: the CD controller, the pad mask, the YM3438,
# the volumes, the PCM's control and the RF5C68) with its time in microseconds, to sound.log:
# the dword's offset, the data and the byte mask, as the 386's io space sees them; and every
# write to the RF5C68's wave RAM window (physical, the machine's own address) as "m OFFSET...".
# Replayed by the runtime (the port's --replay-sound, once it has one), it is the oracle's sound without the game.
SOUND_LUA = """
local slog = io.open("sound.log", "w")
local cpu = manager.machine.devices[":maincpu"]
local function now() return math.floor(manager.machine.time:as_double() * 1e6) end
stap = cpu.spaces["io"]:install_write_tap(0x4c0, 0x4ff, "soundlog", function(offset, data, mask)
    slog:write(string.format("%%d %%x %%x %%x\\n", now(), offset, data, mask))
end)
wtap = cpu.spaces["program"]:install_write_tap(0x%x, 0x%x, "wavelog", function(offset, data, mask)
    slog:write(string.format("%%d m %%x %%x %%x\\n", now(), offset, data, mask))
end)
emu.register_frame_done(function() slog:flush() end)
"""
WAVE_RAM = {'fmtowns': 0xC2200000, 'fmtownsux': 0xC2200000, 'fmtmarty': 0xF80000, 'fmtmarty2': 0xF80000}

# Every device's save-state items (MAME's own state of the machine: the CRTC's and video
# registers, palettes, the PICs, the sound chips...): small ones as hex in items.txt, large
# ones (VRAM, sprite RAM) each to a file of its own. Read with fmtownskit.mamedump --items.
ITEMS_LUA = """
local function dump_items()
    local f, n = io.open("items.txt", "w"), 0
    for tag, dev in pairs(manager.machine.devices) do
        for name, index in pairs(dev.items) do
            local it = emu.item(index)
            local bytes = it.size * it.count
            if bytes > 0 then
                local data = it:read_block(0, bytes)
                if bytes <= 4096 then
                    f:write(string.format("%%s/%%s %%d %%d %%s\\n", tag, name, it.size, it.count,
                        (data:gsub(".", function(ch) return string.format("%%02x", ch:byte()) end))))
                else
                    n = n + 1
                    local b = io.open(string.format("item%%d.bin", n), "wb")
                    b:write(data)
                    b:close()
                    f:write(string.format("%%s/%%s %%d %%d @item%%d.bin\\n", tag, name, it.size, it.count, n))
                end
            end
        end
    end
    f:close()
end
"""

# The video hardware's registers, read through its ports (the driver's own save items are
# under a module name with a slash, which hides them from Lua's device.items): the CRTC's 32,
# the video output's 2, the sprite controller's 8, the VRAM write mask, the FM-R registers,
# the three palettes (each selected in turn through video register 1, then put back).
PORTS_LUA = """
local function dump_ports()
    local io = manager.machine.devices[":maincpu"].spaces["io"]
    local out = {}
    local function put(s) out[#out + 1] = s end
    local sel = io:read_u8(0x440)
    for r = 0, 31 do
        io:write_u8(0x440, r)
        put(string.format("crtc %%d %%02x%%02x", r, io:read_u8(0x443), io:read_u8(0x442)))
    end
    io:write_u8(0x440, sel)
    local vsel = io:read_u8(0x448)
    local vreg = {}
    for r = 0, 1 do io:write_u8(0x448, r); vreg[r] = io:read_u8(0x44a); put(string.format("vreg %%d %%02x", r, vreg[r])) end
    local ssel = io:read_u8(0x450)
    for r = 0, 7 do io:write_u8(0x450, r); put(string.format("sprite %%d %%02x", r, io:read_u8(0x452))) end
    io:write_u8(0x450, ssel)
    local msel = io:read_u8(0x458)
    for r = 0, 1 do io:write_u8(0x458, r); put(string.format("mask %%d %%02x %%02x", r, io:read_u8(0x45a), io:read_u8(0x45b))) end
    io:write_u8(0x458, msel)
    put(string.format("ff81 %%02x", io:read_u8(0xff81)))
    put(string.format("ff82 %%02x", io:read_u8(0xff82)))
    put(string.format("ff83 %%02x", io:read_u8(0xff83)))
    local psel = io:read_u8(0xfd90)
    for _, pal in ipairs({{"pal16_0", 0x00, 16}, {"pal16_1", 0x20, 16}, {"pal256", 0x10, 256}}) do
        io:write_u8(0x448, 1); io:write_u8(0x44a, (vreg[1] & 0xcf) | pal[2])
        for i = 0, pal[3] - 1 do
            io:write_u8(0xfd90, i)
            put(string.format("%%s %%d %%02x %%02x %%02x", pal[1], i, io:read_u8(0xfd94), io:read_u8(0xfd96), io:read_u8(0xfd92)))
        end
    end
    io:write_u8(0x448, 1); io:write_u8(0x44a, vreg[1]); io:write_u8(0x448, vsel)
    io:write_u8(0xfd90, psel)
    local h = _G.io.open("ports.txt", "w")
    h:write(table.concat(out, "\\n"), "\\n")
    h:close()
end
"""


# Buttons held on player 1's pad over spans of emulated seconds (--input): the pad is the
# port whose tag starts ":pad1:" (the Marty's martypad, the Towns' townspad), its fields by
# name ("P1 A", "P1 Run", "P1 Up", ...).
INPUT_LUA = """local presses = {%s}
local pad
for tag, port in pairs(manager.machine.ioport.ports) do
    if tag:sub(1, 6) == ":pad1:" then pad = port end
end
local held = {}
emu.register_frame_done(function()
    local t = manager.machine.time:as_double()
    local want = {}
    for _, p in ipairs(presses) do
        if t >= p[1] and t < p[2] then
            for _, b in ipairs(p[3]) do want["P1 " .. b] = true end
        end
    end
    for name, field in pairs(pad.fields) do
        if want[name] and not held[name] then field:set_value(1); held[name] = true
        elseif held[name] and not want[name] then field:clear_value(); held[name] = nil end
    end
end)
"""

# Calls into the program's functions, logged by MAME's debugger with no window (-debug
# -debugger none): once the program runs (CS 0x0C), a breakpoint at each function, which
# prints the registers, the return address and four arguments from the stack, then goes on.
# The console's lines go to calls.txt as they come, frame by frame. Offsets are the program's (its code
# segment's base added at run time, whatever the machine's RAM puts it at).
TRACE_LUA = """local trace = {%s}
local cpu = manager.machine.devices[":maincpu"]
local dbg = manager.machine.debugger
local armed, last, lastline = {}, %g, nil
io.open("calls.txt", "w"):close()
emu.register_frame_done(function()
    -- the console's new lines, each frame (at the machine's stop the log is gone, and it keeps
    -- a few thousand lines: new ones are those after the last line written)
    local log = dbg.consolelog
    local from = 1
    if lastline then
        for k = #log, 1, -1 do
            if log[k] == lastline then from = k + 1 break end
        end
    end
    if from <= #log then
        local f = io.open("calls.txt", "a")
        for k = from, #log do f:write(log[k], "\\n") end
        f:close()
        lastline = log[#log]
    end
    if cpu.state["CS"].value == 0x0c then
        -- another program under 0x0C (RUN386 runs ADDDRV.EXP first): arm at its base too
        arm(cpu.state["CSBASE"].value)
    end
end)
"""
# Armed from the start at the base RUN386 gives the program on this machine (towns.PROFILES),
# so that its first calls are seen: a base met only at a frame's end comes after them.
TRACE_ARM_LUA = """
function arm(base)
    if armed[base] then return end
    armed[base] = true
    dbg:command("printf \\"trace: armed at 0x%%x\\"," .. string.format("%%x", base))
    for _, t in ipairs(trace) do
        cpu.debug:bpset(base + t[1], "1", string.format('printf "%%s t=%%%%d eax=%%%%x ebx=%%%%x ecx=%%%%x edx=%%%%x esi=%%%%x edi=%%%%x ret=%%%%x args %%%%x %%%%x %%%%x %%%%x",frame,eax,ebx,ecx,edx,esi,edi,d@(ssbase+esp),d@(ssbase+esp+4),d@(ssbase+esp+8),d@(ssbase+esp+12),d@(ssbase+esp+16); g', t[2]))
    end
end
arm(0x%x)
"""
PROG_BASE = {'4M': 0x408000}


def trace_targets(spec, exp_path):
    """'drawworld,1a2b' -> [(offset, name)]: symbols by name (the program's SYM1), or hex."""
    names = {}
    try:
        sys.path.insert(0, ROOT)
        from fmtownskit import exp as expmod
        e = expmod.Exp(open(exp_path, 'rb').read())
        names = {n: off for off, _, n in e.symbols}
    except (ImportError, OSError, ValueError):
        pass
    out = []
    for item in spec.split(','):
        if item in names:
            out.append((names[item], item))
        else:
            out.append((int(item, 16), item))
    return out


def presses(spec):
    """'T0-T1:A+Right,T2-T3:Run' -> the Lua table's entries."""
    out = []
    for part in spec.split(','):
        span, _, buttons = part.partition(':')
        t0, _, t1 = span.partition('-')
        out.append('{%g, %g, {%s}}' % (float(t0), float(t1), ', '.join('"%s"' % b for b in buttons.split('+'))))
    return ', '.join(out)


def times(spec):
    out = []
    for part in spec.split(','):
        if '-' in part:
            span, _, step = part.partition('/')
            a, b = (float(x) for x in span.split('-'))
            t = a
            while t <= b + 1e-9:
                out.append(t)
                t += float(step or 1)
        else:
            out.append(float(part))
    return sorted(out)


def tool(env, name):
    path = os.environ.get(env) or shutil.which(name)
    if not path:
        sys.exit('%s not found: set %s' % (name, env))
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--machine', default='fmtowns', help='fmtowns, fmtmarty, fmtmarty2, fmtownsux...')
    ap.add_argument('--at', default='5-120/5', help='seconds: a,b,c or a-b/step')
    ap.add_argument('--out', help='output directory (default build/oracle/<machine>, or dump_<machine>_<t>)')
    ap.add_argument('--dump', type=float, metavar='SECONDS',
                    help='instead of snapshots: state.txt and ram.bin (read with fmtownskit.mamedump)')
    ap.add_argument('--dump-write', metavar='ADDR=VALUE',
                    help='instead of snapshots: state.txt and ram.bin at the first write of VALUE to '
                         'physical ADDR (hex; a dword), in protected mode with paging on')
    ap.add_argument('--ram', type=lambda x: int(x, 0),
                    help="bytes of RAM to dump (default: the machine's RAM, -ramsize's or 2 MB)")
    ap.add_argument('--wav', metavar='FILE', help="MAME's sound output to FILE (-wavwrite, 48 kHz) up to the last --at")
    ap.add_argument('--sound-log', action='store_true',
                    help='every write to ports 0x4C0-0x4FF and to the wave RAM, timed, to sound.log '
                         'in the output directory')
    ap.add_argument('--lua', metavar='FILE', action='append', default=[],
                    help='a Lua script of your own, run after the rest')
    ap.add_argument('--ramsize', metavar='SIZE',
                    help="the machine's RAM, as MAME's -ramsize takes it (default: 4M on fmtowns, "
                         "the machine's own elsewhere)")
    ap.add_argument('--trace-calls', metavar='NAME|OFF,...',
                    help="log each call to these functions of the program (symbols or hex offsets) "
                         "to calls.txt in the output directory, through MAME's debugger")
    ap.add_argument('--input', metavar='T0-T1:BUTTONS,...',
                    help="player 1's pad held over spans of seconds, e.g. 25-25.2:A,30-31:Right+B "
                         '(A B Run Select Zoom Up Down Left Right)')
    a = ap.parse_args()
    ramsize = a.ramsize or ('4M' if a.machine == 'fmtowns' else None)
    if a.ram is None:
        a.ram = int(ramsize[:-1]) << 20 if ramsize and ramsize.upper().endswith('M') else 0x200000
    if a.dump_write:
        wa, _, wv = a.dump_write.partition('=')
        a.dump_write = (int(wa, 16), int(wv, 16))
    mame = tool('MAME', 'mame')
    work = os.path.join(ROOT, 'build', 'oracle')
    os.makedirs(work, exist_ok=True)
    if not os.path.exists(CHD):
        subprocess.check_call([tool('CHDMAN', 'chdman'), 'createcd', '-i', CUE, '-o', CHD])
        info = subprocess.check_output([tool('CHDMAN', 'chdman'), 'info', '-i', CHD], text=True)
        sha1 = next((l.split()[-1] for l in info.splitlines() if l.startswith('SHA1:')), None)
        if sha1 != CHD_SHA1:
            os.remove(CHD)
            sys.exit('the CHD made from the cue sheet has SHA-1 %s, the software list %s' % (sha1, CHD_SHA1))
    roms = os.environ.get('FMT_ROMS', os.path.join(ROOT, 'bios'))
    dumping = a.dump is not None or a.dump_write
    if a.dump_write:
        out = a.out or os.path.join(work, 'dump_%s_w%x' % (a.machine, a.dump_write[0]))
    elif a.dump is not None:
        out = a.out or os.path.join(work, 'dump_%s_%g' % (a.machine, a.dump))
    else:
        out = a.out or os.path.join(work, a.machine)
    out = os.path.abspath(out)              # MAME runs in another directory
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    lua = os.path.join(work, 'oracle.lua')
    ts = times(a.at)
    with open(lua, 'w') as f:
        if a.dump_write:
            f.write(ITEMS_LUA % () + PORTS_LUA % () + WRITE_LUA % (a.dump_write + (a.ram,)))
        elif a.dump is not None:
            f.write(ITEMS_LUA % () + PORTS_LUA % () + DUMP_LUA % (a.dump, a.ram))
        else:
            f.write(LUA % ', '.join('%g' % t for t in ts))
        if a.sound_log:
            w = WAVE_RAM[a.machine]
            f.write(SOUND_LUA % (w, w + 0xFFF))
        if a.input:
            f.write(INPUT_LUA % presses(a.input))
        if a.trace_calls:
            tl = trace_targets(a.trace_calls, os.path.join(ROOT, 'build', 'disc', '4DDFMT.EXP'))
            f.write(TRACE_LUA % (', '.join('{0x%x, "%s"}' % t for t in tl), ts[-1]))
            f.write(TRACE_ARM_LUA % PROG_BASE.get(ramsize, 0x200000))
        for extra in a.lua:
            with open(extra) as g:
                f.write('\n' + g.read())
    cmd = [mame, a.machine, '-rompath', roms, '-cdrom', CHD,
           '-inipath', work, '-cfg_directory', os.path.join(work, 'cfg'),
           '-nvram_directory', os.path.join(work, 'nvram'), '-snapshot_directory', out,
           '-video', 'none', '-sound', 'none', '-nothrottle', '-skip_gameinfo',
           '-autoboot_script', lua]
    if a.trace_calls:
        cmd += ['-debug', '-debugger', 'none']
    if ramsize:
        cmd += ['-ramsize', ramsize]
    if a.wav:
        cmd += ['-wavwrite', os.path.abspath(a.wav), '-samplerate', '48000']
    subprocess.check_call(cmd, cwd=out if (dumping or a.sound_log or a.trace_calls) else work)
    if a.trace_calls:
        print('calls in %s' % os.path.join(out, 'calls.txt'))
    if dumping:
        print('state.txt and ram.bin in %s' % out)
        return
    snaps = os.path.join(out, a.machine)
    names = sorted(n for n in os.listdir(snaps) if n.endswith('.png'))
    print('%d snapshots in %s' % (len(names), snaps))
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return
    cols, w, h = 6, 320, 240
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w, rows * (h + 14)), (40, 40, 40))
    dr = ImageDraw.Draw(sheet)
    for i, (n, t) in enumerate(zip(names, ts)):
        im = Image.open(os.path.join(snaps, n)).convert('RGB')
        x, y = (i % cols) * w, (i // cols) * (h + 14)
        sheet.paste(im.resize((w, h)), (x, y + 14))
        dr.text((x + 4, y + 1), '%gs  %dx%d' % (t, im.width, im.height), fill=(255, 255, 0))
    sheet.save(os.path.join(out, 'sheet.png'))
    print(os.path.join(out, 'sheet.png'))


if __name__ == '__main__':
    main()
