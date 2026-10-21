"""The oracle's interrupt log, read: each call's registers in and out, by service.

tools/oracle.py --trace-calls with every `int` site of the program and the instruction after
it (and 34e70/34e72, `_mwint21`: `int 21h; ret`) writes a line at each; this pairs them.

    python tools/intlog.py build/oracle/trace_ints/calls.txt [--all] [--from FRAME] [--to FRAME]
"""
import argparse
import collections
import re
import sys

LINE = re.compile(r'^([0-9a-f]+) t=(\d+) eax=(\w+) ebx=(\w+) ecx=(\w+) edx=(\w+) esi=(\w+) edi=(\w+)')


def calls(path, x86map=None):
    """[(frame, site, regs_in, regs_out)]; a site is the `int` instruction's offset."""
    out, pending = [], {}
    for line in open(path, errors='replace'):
        m = LINE.match(line)
        if not m:
            continue
        site, t = int(m.group(1), 16), int(m.group(2))
        regs = tuple(int(x, 16) for x in m.groups()[2:])
        if site - 2 in pending:                 # the instruction after an int
            t0, r0 = pending.pop(site - 2)
            out.append((t0, site - 2, r0, regs))
        else:
            pending[site] = (t, regs)
    return out


def service(site, r):
    eax = r[0]
    if site == 0x34E70:
        return 'int 21h AH=%02X%s' % ((eax >> 8) & 0xFF, ' AL=%02X' % (eax & 0xFF) if (eax >> 8) & 0xFF in (0x25, 0x44, 0x42, 0x3D) else '')
    return 'site %05x AX=%04X' % (site, eax & 0xFFFF)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('log')
    ap.add_argument('--all', action='store_true', help='every call, in order')
    ap.add_argument('--from', dest='lo', type=int, default=0)
    ap.add_argument('--to', dest='hi', type=int, default=1 << 30)
    a = ap.parse_args()
    cs = [c for c in calls(a.log) if a.lo <= c[0] <= a.hi]
    names = ('eax', 'ebx', 'ecx', 'edx', 'esi', 'edi')
    if a.all:
        for t, site, r0, r1 in cs:
            diff = ' '.join('%s %x->%x' % (n, x, y) if x != y else '%s %x' % (n, x) for n, x, y in zip(names, r0, r1))
            print('%5d %-24s %s' % (t, service(site, r0), diff))
        return
    first, count = {}, collections.Counter()
    for c in cs:
        k = service(c[1], c[2])
        count[k] += 1
        first.setdefault(k, c)
    for k, (t, site, r0, r1) in sorted(first.items(), key=lambda kv: kv[1][0]):
        diff = ' '.join('%s %x->%x' % (n, x, y) if x != y else '%s %x' % (n, x) for n, x, y in zip(names, r0, r1))
        print('%5d x%-5d %-24s %s' % (t, count[k], k, diff))


if __name__ == '__main__':
    main()
