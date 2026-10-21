"""The power of two WAV stretches band by band, where the samples cannot line up (the sound
follows the game's time, which drifts): the runtime's over the oracle's, per 2 kHz band.

    python tools/wavbands.py ORACLE.wav AT RUNTIME.wav AT LEN
"""
import sys
import wave

import numpy as np


def stretch(path, at, length):
    w = wave.open(path)
    rate = w.getframerate()
    w.setpos(int(at * rate))
    a = np.frombuffer(w.readframes(int(length * rate)), dtype='<i2').reshape(-1, 2).astype(np.float64)
    return a.mean(axis=1), rate


def psd(x, n=4096):
    win = np.hanning(n)
    segs = [x[i:i + n] * win for i in range(0, len(x) - n, n // 2)]
    return np.mean([np.abs(np.fft.rfft(s)) ** 2 for s in segs], axis=0)


def main():
    o_path, o_at, r_path, r_at, length = sys.argv[1], float(sys.argv[2]), sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
    o, rate = stretch(o_path, o_at, length)
    r, _ = stretch(r_path, r_at, length)
    po, pr = psd(o), psd(r)
    f = np.fft.rfftfreq(4096, 1 / rate)
    print(f'rms oracle {np.sqrt((o ** 2).mean()):.1f}  runtime {np.sqrt((r ** 2).mean()):.1f}')
    for lo in range(0, 24000, 2000):
        k = (f >= lo) & (f < lo + 2000)
        so, sr = po[k].sum(), pr[k].sum()
        share = so / po.sum()
        print(f'{lo / 1000:4.0f}-{(lo + 2000) / 1000:2.0f} kHz  {sr / so if so else float("nan"):6.3f}   ({100 * share:5.2f}% of the oracle)')


if __name__ == '__main__':
    main()
