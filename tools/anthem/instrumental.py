#!/usr/bin/env python3
"""Find the line times of «Pátria» in an instrumental recording (see README.md).

    python instrumental.py instr.wav vocal.wav patria.json

instr.wav / vocal.wav: mono 22.05 kHz WAV of the instrumental and of the
Government's vocal recording; patria.json: the 0.3.0 data whose cues are the
measured line times of the vocal recording. Prints the key shift, the refrain
match, the 34-beat blocks, the chords per beat and proposed cues.
"""
import json
import sys

import librosa
import numpy as np
import soundfile as sf

SR, HOP = 22050, 1024
STEPS = np.array([[1, 1], [1, 2], [2, 1]])          # tempo ratio between 1/2 and 2
NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def chroma(y):
    c = librosa.feature.chroma_cqt(y=y, sr=SR, hop_length=HOP, bins_per_octave=36)
    c = librosa.decompose.nn_filter(c, aggregate=np.median, metric="cosine")
    return librosa.util.normalize(c, axis=0)


def triads():
    out = []
    for r in range(12):
        for q, ivs in (("", (0, 4, 7)), ("m", (0, 3, 7)), ("7", (0, 4, 7, 10))):
            t = np.zeros(12); t[[(r + i) % 12 for i in ivs]] = 1; out.append((NAMES[r] + q, t / np.linalg.norm(t)))
    return out


def main(instr_path, vocal_path, data_path):
    yi, _ = sf.read(instr_path); yv, _ = sf.read(vocal_path)
    fps = SR / HOP; ci, cv = chroma(yi), chroma(yv)
    cues = json.load(open(data_path, encoding="utf-8"))["cues"]
    # 1. key shift and where the first refrain of the vocal recording lies in the instrumental
    a, b = cues[0][0], cues[1][1]
    q0 = cv[:, int(a * fps):int(b * fps)]
    best = []
    for k in range(12):
        D, _ = librosa.sequence.dtw(X=np.roll(q0, k, axis=0), Y=ci, metric="cosine", subseq=True, step_sizes_sigma=STEPS)
        cost = D[-1, :] / q0.shape[1]; best.append((float(np.nanmin(cost)), k))
    best.sort(); shift = best[0][1]
    print("key shift (semitones up):", shift, " costs:", [(k, round(c, 3)) for c, k in best[:3]])
    # 2. beats, beat-synchronous chroma and 34-beat blocks
    _tempo, beats = librosa.beat.beat_track(y=yi, sr=SR, hop_length=256, units="time", start_bpm=72, tightness=200)
    H = librosa.effects.harmonic(yi, margin=3.0)
    C = librosa.feature.chroma_cqt(y=H, sr=SR, hop_length=512)
    B = librosa.util.sync(C, librosa.time_to_frames(beats, sr=SR, hop_length=512), aggregate=np.mean)
    B = B[:, 1:]                                     # column i = beat i … beat i+1 (sync adds the part before the first beat)
    B = B / (np.linalg.norm(B, axis=0, keepdims=True) + 1e-9)

    def sim(x, y, n=32):
        n = min(n, B.shape[1] - max(x, y)); return float(np.mean(np.sum(B[:, x:x + n] * B[:, y:y + n], axis=0)))
    for start, other in ((12, 46), (80, 114)):
        print(f"block #{start} vs #{other}: {sim(start, other):.3f}  (±1 beat: {sim(start, other - 1):.3f} / {sim(start, other + 1):.3f})")
    # 3. chords per beat
    T = triads()
    labels = []
    for i in range(B.shape[1]):
        v = B[:, i]; labels.append(max(T, key=lambda nt: float(v @ nt[1]))[0])
    for i in range(0, len(labels), 8):
        if i < len(beats): print(f"#{i:3d} {beats[i]:6.2f}s | " + " ".join(f"{c:>4}" for c in labels[i:i + 8]))
    # 4. proposed cues: refrain lines just before the block start (pickup ≈ 0.45 beat) and 12 beats later;
    #    verse lines half a beat before beats +3, +11.5, +19.5, +27.5 of each verse block.
    bt = lambda x: float(np.interp(x, np.arange(len(beats)), beats, right=beats[-1] + (x - len(beats) + 1) * np.median(np.diff(beats))))
    starts = [bt(11.55), bt(24), bt(45.55), bt(58)]
    for block in (80, 114):
        starts += [bt(block + 3), bt(block + 11.5), bt(block + 19.5), bt(block + 27.5)]
    print("proposed line starts:", [round(s, 2) for s in starts])


if __name__ == "__main__":
    if len(sys.argv) != 4: sys.exit(__doc__)
    main(*sys.argv[1:])
