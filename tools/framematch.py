"""The runtime's frames held against the oracle's snapshots, by content.

The runtime loads from the disc image at once where MAME reads its CD at the drive's pace
(and runs DOS's own code to do it), so the same picture comes at different moments: for each
oracle snapshot this finds the runtime frame closest to it and counts the pixels that differ.
A side-by-side sheet (oracle | runtime | the pixels that differ) is written too.

    python tools/oracle.py --at 16,18,20,22 --out build/oracle/cmp
    build/rt/4ddriving --frames 600 --png-every 1 --out build/frames
    python tools/framematch.py build/oracle/cmp/fmtowns build/frames --at 16,18,20,22

Frame F of the runtime is the oracle's 14.793 + F/60 s (the program's first instruction on
MAME's fmtowns -ramsize 4M): "ahead" is how much sooner the runtime showed it. Needs PIL and numpy.
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageDraw

ENTRY = 14.793


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('oracle', help="a directory of the oracle's snapshots (0000.png ...)")
    ap.add_argument('frames', help="a directory of the runtime's frames (f000123.png ...)")
    ap.add_argument('--at', required=True, help='the snapshots\' times in seconds, in order: a,b,c')
    ap.add_argument('--sheet', default='build/framematch.png')
    a = ap.parse_args()
    times = [float(x) for x in a.at.split(',')]
    snaps = sorted(n for n in os.listdir(a.oracle) if n.endswith('.png'))
    names = sorted(n for n in os.listdir(a.frames) if n.startswith('f') and n.endswith('.png'))
    frames = {n: np.asarray(Image.open(os.path.join(a.frames, n)).convert('RGB')) for n in names}
    w, h = 352, 262
    sheet = Image.new('RGB', (3 * w, len(snaps) * (h + 14)), (40, 40, 40))
    dr = ImageDraw.Draw(sheet)
    exact = 0
    for i, (t, s) in enumerate(zip(times, snaps)):
        o = np.asarray(Image.open(os.path.join(a.oracle, s)).convert('RGB'))
        same = [n for n in names if frames[n].shape == o.shape]
        best = min(same, key=lambda n: np.count_nonzero((frames[n] != o).any(axis=2)))
        diff = (frames[best] != o).any(axis=2)
        px = int(np.count_nonzero(diff))
        exact += px == 0
        f = int(best[1:-4])
        print('oracle %6.2f s: runtime frame %6d (%6.2f s ahead)  %7d pixels differ (%.2f%%)'
              % (t, f, t - ENTRY - f / 60, px, 100.0 * px / diff.size))
        y = i * (h + 14)
        for k, im in enumerate((o, frames[best], np.where(diff[..., None], 255, 0).astype(np.uint8).repeat(3, 2))):
            sheet.paste(Image.fromarray(im).resize((w, h)), (k * w, y + 14))
        dr.text((4, y + 1), 'oracle %.2f s | runtime frame %d | %d pixels differ' % (t, f, px), fill=(255, 255, 0))
    sheet.save(a.sheet)
    print('%d of %d snapshots matched exactly; %s' % (exact, len(snaps), a.sheet))


if __name__ == '__main__':
    main()
