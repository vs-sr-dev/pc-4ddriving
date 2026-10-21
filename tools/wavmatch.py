"""Hold the runtime's sound against the oracle's: two 16-bit stereo WAVs at the same rate.

    python tools/wavmatch.py ORACLE.wav RUNTIME.wav [--at SECONDS] [--len SECONDS] [--lag SECONDS]

The runtime's WAV starts at the program's first instruction, the oracle's at power-on, and the
runtime reads the disc sooner: the delay between them is found first (the two loudness envelopes
cross-correlated, at 100 Hz), then to the sample (the signals themselves, around the envelope's
answer). Over `--len` seconds of the oracle from `--at`: the correlation, the gain (runtime over
oracle) and the residual's share of the oracle's energy, with the best lag. --lag gives the delay
(oracle time minus runtime time) instead of searching for it.
"""
import argparse
import wave

import numpy as np


def load(path):
    w = wave.open(path)
    a = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').reshape(-1, 2).astype(np.float64)
    return a, w.getframerate()


def envelope(a, rate, hz=100):
    n = rate // hz
    m = len(a) // n
    return np.sqrt((a[:m * n].mean(axis=1) ** 2).reshape(m, n).mean(axis=1))


def xcorr_lag(x, y):
    """the shift s maximizing sum x[i] * y[i - s] (y delayed by s matches x)"""
    n = 1 << int(np.ceil(np.log2(len(x) + len(y))))
    c = np.fft.irfft(np.fft.rfft(x - x.mean(), n) * np.conj(np.fft.rfft(y - y.mean(), n)), n)
    s = int(np.argmax(c))
    return s if s < n // 2 else s - n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('oracle')
    ap.add_argument('runtime')
    ap.add_argument('--at', type=float, help='oracle seconds where the stretch starts (default: the loud start)')
    ap.add_argument('--len', type=float, default=10.0)
    ap.add_argument('--lag', type=float, help='oracle time minus runtime time, seconds')
    a = ap.parse_args()
    o, rate = load(a.oracle)
    r, rate2 = load(a.runtime)
    assert rate == rate2, 'rates differ'
    if a.lag is None:
        eo, er = envelope(o, rate), envelope(r, rate)
        coarse = xcorr_lag(eo, er) * (rate // 100)
    else:
        coarse = int(round(a.lag * rate))
    if a.at is None:
        loud = np.nonzero(envelope(o, rate) > 200)[0]
        start = int((loud[0] / 100 + 1) * rate) if len(loud) else 0
    else:
        start = int(a.at * rate)
    n = int(a.len * rate)
    x = o[start:start + n].mean(axis=1)
    # to the sample, within 30 ms of the coarse answer
    best = None
    for lag in range(coarse - rate // 33, coarse + rate // 33 + 1):
        i = start - lag
        if i < 0 or i + n > len(r):
            continue
        y = r[i:i + n].mean(axis=1)
        c = float(np.dot(x, y))
        if best is None or c > best[0]:
            best = (c, lag)
    if best is None:
        print('the stretch is outside the runtime WAV')
        return
    lag = best[1]
    i = start - lag
    xs, ys = o[start:start + n], r[i:i + n]
    gain = float((xs * ys).sum() / max((xs * xs).sum(), 1e-9))
    corr = float(np.corrcoef(xs.ravel(), ys.ravel())[0, 1])
    res = float(((ys - gain * xs) ** 2).sum() / max((xs * xs).sum(), 1e-9))
    print(f'oracle {start / rate:.3f}-{(start + n) / rate:.3f} s = runtime {i / rate:.3f} s '
          f'(lag {lag / rate:.4f} s, {lag} samples)')
    print(f'correlation {corr:.5f}  gain {gain:.4f}  residual {100 * res:.3f}% of the energy')


if __name__ == '__main__':
    main()
