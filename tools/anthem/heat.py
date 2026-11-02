"""Gain of each lyric phrase in 5 s windows (2.5 s hop) -> heat.npy (windows x phrases)."""
import sys, numpy as np, scipy.io.wavfile as wavfile
from score import Scorer, SR, PHRASES
sr, x = wavfile.read("vocals16.wav"); x = x.astype(np.float32) / 32768; x = x / (np.abs(x).max() + 1e-9) * 0.9
sc = Scorer(); sc.audio(np.zeros(SR * 5, np.float32)); base = [sc.logprob(p)[0] for p in PHRASES]
starts = list(np.arange(12.0, 104.0, 2.5)) + list(np.arange(132.0, 197.0, 2.5))
heat = []
for a in starts:
    sc.audio(x[int(a * SR):int((a + 5.0) * SR)])
    row = [sc.logprob(p)[0] - b for p, b in zip(PHRASES, base)]; heat.append(row)
    best = int(np.argmax(row)); print(f"{a:6.1f}  best P{best + 1:<2} {row[best]:6.1f}  " + " ".join(f"{v:5.1f}" for v in row), flush=True)
np.save("heat.npy", np.array(heat)); np.save("heat_starts.npy", np.array(starts))
