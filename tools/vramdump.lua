-- tools/oracle.py --lua tools/vramdump.lua: at the first --dump moment, VRAM (512 KB at
-- 0x80000000) and sprite RAM (128 KB at 0x81000000) as the CPU reads them, to vram.bin and
-- sprram.bin in the output directory. Its own time: VRAMDUMP_AT seconds (22 if unset).
local vd_at = tonumber(os.getenv("VRAMDUMP_AT") or "22")
local vd_done = false
emu.register_frame_done(function()
    if vd_done or manager.machine.time:as_double() < vd_at then return end
    vd_done = true
    local sp = manager.machine.devices[":maincpu"].spaces["program"]
    for _, r in ipairs({{"vram.bin", 0x80000000, 0x80000}, {"sprram.bin", 0x81000000, 0x20000}}) do
        local f = io.open(r[1], "wb")
        for a = r[2], r[2] + r[3] - 1, 0x10000 do f:write(sp:read_range(a, a + 0xffff, 8)) end
        f:close()
    end
end)
