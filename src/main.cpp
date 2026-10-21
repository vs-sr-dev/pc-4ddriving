// 4D Driving, natively: the game's code and TBIOS's, recompiled, on fmtownskit's FM Towns
// runtime. In a window (SDL3: the picture, the sound, the keyboard and gamepads as the Towns
// pad), or headless, saving frames and the sound.
//
//     4ddriving [--cue "disc/....cue"] [--save DIR] [--font FILE] [--scale N] [--fullscreen] [--frames N]
//     4ddriving --headless [--frames N] [--png F,F,...] [--png-every N] [--out DIR] [--wav FILE]
//               [--input F-G:BUTTONS,...] [--trace-int] [--trace-io] [--trace-from F] [--vram F]
//     4ddriving --replay-sound LOG --seconds S --wav FILE [--mute ...]
//
// --save: the host directory holding the floppy drives (A: is DIR/a; default save). The user
// disk the game makes when asked (docs/13-game.md) lives there; with it there, no prompt.
// --font: the Towns' font ROM (FMT_FNT.ROM, 256 KB; by default the one in MAME's fmtowns set,
// bios/fmtowns/fmt_fnt.rom), which the opponents' screen reads for its text.
// --frames: stop after N frames (headless: 600 if not given; in the window: never).
// --png, --png-every: the frames to save (they imply --headless); MAME's whole frame, as the
// oracle's snapshots, or with --crop the picture only, as the window shows it.
// --wav: the sound (the FM, the PCM and the CD's audio mixed as MAME's fmtowns mixes them), 16-bit
// stereo at 48 kHz, from the program's first instruction to the last frame.
// --mute fm,pcm,cd: leave sources out of the mix.
// --vram F: VRAM and sprite RAM at frame F, to vram.bin and sprram.bin in --out (as the oracle's
// tools/vramdump.lua writes them).
// --ram F: the program's segment at frame F (its first 0x6BD10 bytes, to the stack's top), to
// prog.bin in --out.
// --input: buttons held from frame F to frame G (both included), headless: up down left right a b
// run select, joined by '+' (e.g. 433-450:a).
// --replay-sound: no game, the oracle's sound log (tools/oracle.py --sound-log) played into the
// runtime's chips from power-on for S seconds: the WAV lines up with MAME's own -wavwrite.
//
// The machine is MAME's fmtowns with 4 MB, booted from this disc (docs/06-attack-plan.md).
// Frames are counted in VSYNCs from the program's first instruction; on the oracle that
// instruction runs 14.793 seconds after power-on, so frame F here is MAME's 14.793 + F/60 s.
#include "towns.h"
#ifdef FOURD_SDL
#include "towns_sdl.h"
#endif
#include <algorithm>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <set>
#include <string>
#include <vector>

// The machine as this disc's boot leaves it to 4DDFMT.EXP (CONFIG.SYS loads TBIOS; AUTOEXEC.BAT
// runs CoCo, then RUN386 with ADDDRV and FORRBIOS.NSD, then RUN386 4DDFMT): read on MAME's
// fmtowns -ramsize 4M at the program's first instruction (tools/oracle.py --dump-write
// b4d0c=34104, docs/11-runtime.md). The program asks RUN386 for all memory: its segment is
// 0x408000-0x770FFF (physical 0x49000 for its first 456 KB), selector 0x40 all of RAM but the
// 32 KB FORRBIOS.NSD keeps at the top (towns.PROFILES' towns4m+nsd).
static const towns::Profile kTowns4MNsd = {"towns4m+nsd", 4, 0x408000, 0x49000, 0x368FFF, 0x3F7FFF};

// What differs from the state the kit's townsos() sets (the first game's boot): CRTC register
// 28, video register 1, and the 16-colour palettes' half-bright colours (0xB0, not 0x80).
static void townsos_4dd(towns::Machine& m) {
    m.video.crtc[28] = 0x801F;
    m.video.vreg[1] = 0x09;
    for (int l = 0; l < 2; ++l)
        for (int i = 1; i < 8; ++i)
            for (int k = 0; k < 3; ++k)
                if (m.video.pal16[l][i][k] == 0x80) m.video.pal16[l][i][k] = 0xB0;
}

// The PSP and the environment DOS made for RUN386 4DDFMT (selectors 0x24 and 0x2C, as the dump
// has them): no command tail; the environment PATH= and COMSPEC (CONFIG.SYS's SHELL=), then the
// program's name as RUN386 passes it.
static void psp_4dd(towns::Machine& m) {
    const uint32_t psp = 0xBF060, env = 0xBF020;
    m.set_desc(0x04, psp, 0xFF);
    m.set_desc(0x24, psp, 0xFF);
    static const char e[] = "PATH=\0COMSPEC=C:\\COMMAND.COM\0\0\x01\0" "4ddfmt.exp";
    m.set_desc(0x2C, env, 0x2B);
    m.write_block(env, (const uint8_t*)e, sizeof e);
    static const uint8_t head[2] = {0xCD, 0x20}, tail[2] = {0x00, 0x0D};
    m.write_block(psp, head, 2);
    m.write_block(psp + 0x80, tail, 2);
}

struct Press { long from, to; unsigned held; };

static unsigned buttons(const std::string& s) {
    static const std::pair<const char*, unsigned> names[] = {
        {"up", towns::kPadUp}, {"down", towns::kPadDown}, {"left", towns::kPadLeft}, {"right", towns::kPadRight},
        {"a", towns::kPadA}, {"b", towns::kPadB}, {"run", towns::kPadRun}, {"select", towns::kPadSelect}};
    unsigned v = 0;
    for (size_t p = 0; p <= s.size();) {
        size_t q = s.find('+', p);
        std::string n = s.substr(p, q == std::string::npos ? std::string::npos : q - p);
        bool found = false;
        for (auto& [name, bit] : names) if (n == name) { v |= bit; found = true; }
        if (!found) { std::fprintf(stderr, "--input: no button %s\n", n.c_str()); std::exit(2); }
        if (q == std::string::npos) break;
        p = q + 1;
    }
    return v;
}

int main(int argc, char** argv) {
    std::string cue = "disc/4D Driving (Japan) (FM Towns Marty Rerelease).cue", out = "build/frames", save = "save", font = "bios/fmtowns/fmt_fnt.rom";
    std::string wav, replay;
    long frames = -1, every = 0, trace_from = 0, vram_at = -1, ram_at = -1;
    double seconds = 60;
    uint8_t mute = 0;
    std::set<long> at;
    std::vector<Press> presses;
    bool trace_int = false, trace_io = false, headless = false, crop = false;
#ifdef FOURD_SDL
    towns::SdlOptions win;
    win.title = "4D Driving";
#endif
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        auto next = [&]() -> std::string { if (i + 1 >= argc) { std::fprintf(stderr, "%s: a value\n", a.c_str()); std::exit(2); } return argv[++i]; };
        if (a == "--cue") cue = next();
        else if (a == "--save") save = next();
        else if (a == "--font") font = next();
        else if (a == "--frames") frames = std::atol(next().c_str());
        else if (a == "--out") out = next();
        else if (a == "--headless") headless = true;
        else if (a == "--png-every") { every = std::atol(next().c_str()); headless = true; }
        else if (a == "--png") {
            std::string s = next();
            for (size_t p = 0; p < s.size();) {
                size_t q = s.find(',', p);
                at.insert(std::atol(s.substr(p, q - p).c_str()));
                p = q == std::string::npos ? s.size() : q + 1;
            }
            headless = true;
        }
        else if (a == "--input") {
            std::string s = next();
            for (size_t p = 0; p < s.size();) {
                size_t q = s.find(',', p);
                std::string item = s.substr(p, q == std::string::npos ? std::string::npos : q - p);
                Press pr{};
                size_t colon = item.find(':'), dash = item.find('-');
                if (colon == std::string::npos) { std::fprintf(stderr, "--input: F-G:BUTTONS\n"); return 2; }
                pr.from = std::atol(item.c_str());
                pr.to = dash != std::string::npos && dash < colon ? std::atol(item.c_str() + dash + 1) : pr.from;
                pr.held = buttons(item.substr(colon + 1));
                presses.push_back(pr);
                p = q == std::string::npos ? s.size() : q + 1;
            }
        }
        else if (a == "--wav") wav = next();
        else if (a == "--replay-sound") replay = next();
        else if (a == "--seconds") seconds = std::atof(next().c_str());
        else if (a == "--mute") {
            std::string s = next();
            mute = (uint8_t)((s.find("fm") != std::string::npos ? 1 : 0) | (s.find("pcm") != std::string::npos ? 2 : 0)
                             | (s.find("cd") != std::string::npos ? 4 : 0));
        }
#ifdef FOURD_SDL
        else if (a == "--scale") win.scale = std::atoi(next().c_str());
        else if (a == "--fullscreen") win.fullscreen = true;
#endif
        else if (a == "--trace-int") trace_int = true;
        else if (a == "--trace-io") trace_io = true;
        else if (a == "--trace-from") trace_from = std::atol(next().c_str());
        else if (a == "--vram") { vram_at = std::atol(next().c_str()); headless = true; }
        else if (a == "--ram") { ram_at = std::atol(next().c_str()); headless = true; }
        else if (a == "--crop") crop = true;
        else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); return 2; }
    }
#ifndef FOURD_SDL
    headless = true;                    // built without SDL3: no window
#endif
    if (frames < 0) frames = headless ? 600 : 0;

    towns::Machine m;
    m.profile = &kTowns4MNsd;
    townsos_4dd(m);
    std::string err;
    if (!m.disc.open(cue, err)) { std::fprintf(stderr, "%s\n", err.c_str()); return 1; }
    m.audio_mute = mute;
    m.save_dir = save;
    if (!replay.empty()) {
        towns::WavWriter w;
        if (wav.empty() || !w.open(wav)) { std::fprintf(stderr, "--replay-sound needs --wav FILE\n"); return 2; }
        if (!towns::replay_sound_log(m, replay, seconds, w, err)) { std::fprintf(stderr, "%s\n", err.c_str()); return 1; }
        return 0;
    }
    std::vector<uint8_t> exe, tbios;
    if (!m.disc.file("4DDFMT.EXP", exe) || !m.disc.file("TBIOS.BIN", tbios)) {
        std::fprintf(stderr, "4DDFMT.EXP or TBIOS.BIN not on the disc\n");
        return 1;
    }
    towns::P3 p;
    if (!towns::parse_p3(exe, p, err)) { std::fprintf(stderr, "4DDFMT.EXP: %s\n", err.c_str()); return 1; }
    // the recompiled code is this disc's code
    for (auto [name, img] : {std::pair<const char*, const std::vector<uint8_t>*>{"GAME", &p.image}, {"TBIOS", &tbios}}) {
        const X86Module* mod = x86_module(name);
        uint32_t crc = x86_crc32(img->data(), img->size());
        if (!mod || mod->crc != crc || mod->size != img->size()) {
            std::fprintf(stderr, "%s on this disc is not the one recompiled (crc %08x)\n", name, crc);
            return 1;
        }
    }
    if (FILE* f = std::fopen(font.c_str(), "rb")) {
        m.font.resize(0x40000);
        m.font.resize(std::fread(m.font.data(), 1, m.font.size(), f));
        std::fclose(f);
    } else {
        std::fprintf(stderr, "no font ROM (%s): the opponents' screen will have no text\n", font.c_str());
    }
    m.trace_int = trace_int && !trace_from;
    m.trace_io = trace_io && !trace_from;
    if (every || !at.empty()) std::filesystem::create_directories(out);
    towns::WavWriter wavw;
    if (!wav.empty() && !wavw.open(wav)) { std::fprintf(stderr, "cannot write %s\n", wav.c_str()); return 1; }
#ifdef FOURD_SDL
    towns::SdlHost host;
    if (!headless && !host.open(win, err)) { std::fprintf(stderr, "no window: %s\n", err.c_str()); return 1; }
#endif
    std::vector<int16_t> audio;
    m.on_vsync = [&](towns::Machine& mm) {
        long f = (long)mm.frame;
        if (trace_from && f == trace_from) { mm.trace_int = trace_int; mm.trace_io = trace_io; }
        if (f == ram_at) {
            // the program's segment, from its base to the stack's top (the oracle's RAM at
            // physical 0x49000 on: tools/oracle.py --dump)
            std::vector<uint8_t> seg(0x6BD10);
            mm.read_block(kTowns4MNsd.prog_base, seg.data(), (uint32_t)seg.size());
            std::filesystem::create_directories(out);
            if (FILE* fo = std::fopen((out + "/prog.bin").c_str(), "wb")) { std::fwrite(seg.data(), 1, seg.size(), fo); std::fclose(fo); }
        }
        if (f == vram_at) {
            std::filesystem::create_directories(out);
            for (auto [name, mem] : {std::pair<const char*, const std::vector<uint8_t>*>{"/vram.bin", &mm.vram}, {"/sprram.bin", &mm.sprram}})
                if (FILE* fo = std::fopen((out + name).c_str(), "wb")) { std::fwrite(mem->data(), 1, mem->size(), fo); std::fclose(fo); }
        }
        if (at.count(f) || (every && f % every == 0)) {
            std::vector<uint32_t> rgb;
            int w, h;
            mm.render(rgb, w, h);
            if (crop) {                 // the picture only, as the window shows it
                int x, y, cw, ch;
                mm.display_area(x, y, cw, ch);
                std::vector<uint32_t> part((size_t)cw * ch);
                for (int r = 0; r < ch; ++r)
                    std::copy_n(rgb.begin() + (long)(y + r) * w + x, cw, part.begin() + (long)r * cw);
                rgb.swap(part);
                w = cw; h = ch;
            }
            char name[64];
            std::snprintf(name, sizeof name, "/f%06ld.png", f);
            towns::write_png(out + name, rgb, w, h);
        }
        if (headless) {
            unsigned held = 0;
            for (const Press& pr : presses) if (f + 1 >= pr.from && f + 1 <= pr.to) held |= pr.held;
            mm.set_pad(0, held);
            if (!wav.empty()) {
                mm.audio_take(audio);
                wavw.write(audio);
            }
        }
#ifdef FOURD_SDL
        else host.vsync(mm);
#endif
        if (frames && f >= frames) throw towns::Stop{0};
    };

    X86Cpu c;
    towns::boot_run386(m, c, p, tbios);
    psp_4dd(m);
    X86Func entry = x86_lookup_cs(0x0C, c.eip);
    if (!entry) { std::fprintf(stderr, "no recompiled function at the entry %x\n", c.eip); return 1; }
    int code = 0;
    try {
        entry(c);
        std::fprintf(stderr, "the program returned from its entry\n");
    } catch (const towns::Stop& s) {
        code = s.code;
    }
    std::fprintf(stderr, "%s after %llu frames, %.2f s of the guest (the last safe point %04x:%08x)\n",
                 m.exited ? "exit" : "stopped", (unsigned long long)m.frame, (double)c.clocks / towns::kClock,
                 c.sreg[1], c.eip);
    return m.exited ? 0 : code;
}
