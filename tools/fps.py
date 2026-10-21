"""How many different pictures a stretch of consecutive frames holds: the game's own frame rate
(a 3D frame drawn takes several VSYNCs on the 386), for the runtime's frames against the
oracle's snapshots taken at every VSYNC.

    python tools/fps.py DIR [DIR...]     (each: consecutive frames, *.png in name order)
"""
import os
import sys

import numpy as np
from PIL import Image

for d in sys.argv[1:]:
    names = sorted(n for n in os.listdir(d) if n.endswith('.png'))
    prev, changes, runs, run = None, 0, [], 0
    for n in names:
        a = np.asarray(Image.open(os.path.join(d, n)).convert('RGB'))
        if prev is not None and (a != prev).any():
            changes += 1
            runs.append(run)
            run = 0
        run += 1
        prev = a
    secs = len(names) / 60
    hist = {k: runs.count(k) for k in sorted(set(runs[1:]))}
    print(f'{d}: {len(names)} frames, {changes} changes, {changes / secs:.1f} pictures a second; '
          f'VSYNCs each: {hist}')
