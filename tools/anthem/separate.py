"""Vocal separation with the UVR MDX-Net model Kim_Vocal_2 (ONNX), numpy only.

usage: python separate.py model.onnx input.wav vocals.wav
input: 44.1 kHz mono or stereo 16-bit wav.
"""
import sys
import numpy as np
import onnxruntime as ort
import scipy.io.wavfile as wavfile

N_FFT, HOP, DIM_F, DIM_T = 7680, 1024, 3072, 256
N_BINS = N_FFT // 2 + 1
CHUNK = HOP * (DIM_T - 1)
TRIM = N_FFT // 2
COMPENSATE = 1.009
WINDOW = np.hanning(N_FFT + 1)[:-1].astype(np.float32)   # periodic Hann, like torch.hann_window

def stft(x):
    """x: (2, CHUNK) -> (1, 4, DIM_F, DIM_T) like UVR's ConvTDFNet.stft."""
    out = []
    for ch in x:
        pad = np.pad(ch, (N_FFT // 2, N_FFT // 2), mode="reflect")
        frames = np.stack([pad[t * HOP:t * HOP + N_FFT] * WINDOW for t in range(DIM_T)], axis=1)   # (N_FFT, T)
        spec = np.fft.rfft(frames, axis=0)                                                          # (N_BINS, T)
        out += [spec.real, spec.imag]
    return np.stack(out)[None, :, :DIM_F, :].astype(np.float32)

def istft(spec):
    """(1, 4, DIM_F, DIM_T) -> (2, CHUNK)."""
    full = np.concatenate([spec[0], np.zeros((4, N_BINS - DIM_F, DIM_T), np.float32)], axis=1)
    out = []
    for c in range(2):
        z = full[2 * c] + 1j * full[2 * c + 1]
        frames = np.fft.irfft(z, n=N_FFT, axis=0) * WINDOW[:, None]
        length = N_FFT + HOP * (DIM_T - 1)
        y = np.zeros(length, np.float64); env = np.zeros(length, np.float64)
        for t in range(DIM_T):
            y[t * HOP:t * HOP + N_FFT] += frames[:, t]; env[t * HOP:t * HOP + N_FFT] += WINDOW ** 2
        y = y / np.where(env > 1e-8, env, 1)
        out.append(y[N_FFT // 2:N_FFT // 2 + CHUNK])
    return np.stack(out).astype(np.float32)

def main(model, src, dst):
    sr, data = wavfile.read(src)
    assert sr == 44100, sr
    x = data.astype(np.float32) / 32768.0
    mix = np.stack([x, x]) if x.ndim == 1 else x.T
    sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
    name = sess.get_inputs()[0].name
    gen = CHUNK - 2 * TRIM
    pad = gen + TRIM - (mix.shape[-1] % gen)
    mixture = np.concatenate([np.zeros((2, TRIM), np.float32), mix, np.zeros((2, pad), np.float32)], 1)
    step = int(0.75 * CHUNK)
    result = np.zeros_like(mixture); divider = np.zeros_like(mixture)
    total = (mixture.shape[-1] + step - 1) // step
    for n, start in enumerate(range(0, mixture.shape[-1], step)):
        end = min(start + CHUNK, mixture.shape[-1]); size = end - start
        part = mixture[:, start:end]
        if size < CHUNK: part = np.concatenate([part, np.zeros((2, CHUNK - size), np.float32)], 1)
        spec = stft(part); spec[:, :, :3, :] = 0
        pred = sess.run(None, {name: spec})[0]
        wave = istft(pred)
        win = np.tile(np.hanning(size)[None, :], (2, 1)).astype(np.float32)
        result[:, start:end] += wave[:, :size] * win; divider[:, start:end] += win
        print(f"chunk {n + 1}/{total}", flush=True)
    vocals = (result / np.where(divider > 1e-6, divider, 1))[:, TRIM:TRIM + mix.shape[-1]] * COMPENSATE
    wavfile.write(dst, sr, (np.clip(vocals.mean(0), -1, 1) * 32767).astype(np.int16))

if __name__ == "__main__":
    main(*sys.argv[1:4])
