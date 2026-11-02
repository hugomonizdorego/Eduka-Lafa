"""Teacher-forced Whisper scoring: which lyric phrases are sung in each audio segment?

usage: python score.py audio16k.wav a-b [a-b ...]
"""
import base64
import sys

import numpy as np
import onnxruntime as ort
import scipy.io.wavfile as wavfile
import tiktoken

D = "sherpa-onnx-whisper-turbo/"   # github.com/k2-fsa/sherpa-onnx/releases (asr-models): sherpa-onnx-whisper-turbo.tar.bz2
SR, N_FFT, HOP, N_MELS = 16000, 400, 160, 128

PHRASES = ["Pátria, Pátria,", "Timor-Leste, nossa Nação.", "Glória ao povo", "e aos heróis da nossa libertação.",
           "Vencemos o colonialismo,", "gritamos:", "abaixo o imperialismo.", "Terra livre, povo livre,",
           "não, não, não à exploração.", "Avante unidos firmes e decididos.", "Na luta contra o imperialismo",
           "o inimigo dos povos,", "até à vitória final.", "Pelo caminho da revolução."]

def hz_to_mel(f):
    f = np.asarray(f, float); f_sp = 200.0 / 3; mels = f / f_sp
    min_log_hz, min_log_mel, logstep = 1000.0, 1000.0 / f_sp, np.log(6.4) / 27.0
    return np.where(f >= min_log_hz, min_log_mel + np.log(np.maximum(f, 1e-9) / min_log_hz) / logstep, mels)

def mel_to_hz(m):
    m = np.asarray(m, float); f_sp = 200.0 / 3; freqs = f_sp * m
    min_log_hz, min_log_mel, logstep = 1000.0, 1000.0 / f_sp, np.log(6.4) / 27.0
    return np.where(m >= min_log_mel, min_log_hz * np.exp(logstep * (m - min_log_mel)), freqs)

def mel_filters():
    fftfreqs = np.linspace(0, SR / 2, 1 + N_FFT // 2)
    mel_f = mel_to_hz(np.linspace(hz_to_mel(0), hz_to_mel(SR / 2), N_MELS + 2))
    fdiff = np.diff(mel_f); ramps = mel_f[:, None] - fftfreqs[None, :]
    w = np.zeros((N_MELS, len(fftfreqs)))
    for i in range(N_MELS):
        w[i] = np.maximum(0, np.minimum(-ramps[i] / fdiff[i], ramps[i + 2] / fdiff[i + 1]))
    w *= (2.0 / (mel_f[2:N_MELS + 2] - mel_f[:N_MELS]))[:, None]
    return w.astype(np.float32)

FILTERS = mel_filters()
WIN = (0.5 - 0.5 * np.cos(2 * np.pi * np.arange(N_FFT) / N_FFT)).astype(np.float32)

def log_mel(audio):
    audio = np.concatenate([audio, np.zeros(max(0, 30 * SR - len(audio)), np.float32)])[:30 * SR]
    pad = np.pad(audio, (N_FFT // 2, N_FFT // 2), mode="reflect")
    n = 1 + (len(pad) - N_FFT) // HOP
    frames = np.lib.stride_tricks.as_strided(pad, (n, N_FFT), (pad.strides[0] * HOP, pad.strides[0])) * WIN
    mag = (np.abs(np.fft.rfft(frames, axis=1)) ** 2).T[:, :-1]
    spec = np.log10(np.maximum(FILTERS @ mag, 1e-10))
    spec = np.maximum(spec, spec.max() - 8.0)
    return ((spec + 4.0) / 4.0)[None].astype(np.float32)

def encoding():
    ranks = {}
    for line in open(D + "turbo-tokens.txt", encoding="utf-8"):
        tok, idx = line.split()
        ranks[base64.b64decode(tok)] = int(idx)
    pat = r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    return tiktoken.Encoding("whisper", pat_str=pat, mergeable_ranks=ranks, special_tokens={})

class Scorer:
    def __init__(self):
        opts = ort.SessionOptions(); opts.intra_op_num_threads = 8
        self.enc = ort.InferenceSession(D + "turbo-encoder.int8.onnx", opts, providers=["CPUExecutionProvider"])
        self.dec = ort.InferenceSession(D + "turbo-decoder.int8.onnx", opts, providers=["CPUExecutionProvider"])
        meta = self.enc.get_modelmeta().custom_metadata_map
        codes = meta["all_language_codes"].split(","); toks = [int(x) for x in meta["all_language_tokens"].split(",")]
        self.sot = [int(meta["sot"]), toks[codes.index("pt")], int(meta["transcribe"]), int(meta["no_timestamps"])]
        self.eot = int(meta["eot"]); self.tok = encoding()
    def audio(self, x):
        self.k, self.v = self.enc.run(None, {"mel": log_mel(x)})
    def logprob(self, text):
        ids = self.sot + self.tok.encode(" " + text.strip())
        cache = np.zeros((4, 1, 448, 1280), np.float32)
        logits = self.dec.run(None, {"tokens": np.array([ids], np.int64), "in_n_layer_self_k_cache": cache,
                                     "in_n_layer_self_v_cache": cache.copy(), "n_layer_cross_k": self.k,
                                     "n_layer_cross_v": self.v, "offset": np.array([0], np.int64)})[0][0]
        logits = logits - logits.max(axis=1, keepdims=True)
        logp = logits - np.log(np.exp(logits).sum(axis=1, keepdims=True))
        targets = ids[len(self.sot):] + [self.eot]
        return float(sum(logp[len(self.sot) - 1 + i, t] for i, t in enumerate(targets))), len(targets)

def spans(max_len=4):
    out = []
    for i in range(len(PHRASES)):
        for j in range(i + 1, min(len(PHRASES), i + max_len) + 1):
            out.append((i, j, " ".join(PHRASES[i:j])))
    return out

if __name__ == "__main__":
    sr, x = wavfile.read(sys.argv[1]); x = x.astype(np.float32) / 32768
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    sc = Scorer(); cands = spans()
    for arg in sys.argv[2:]:
        a, b = map(float, arg.split("-"))
        sc.audio(x[int(a * SR):int(b * SR)])
        res = sorted(((sc.logprob(t)[0], i, j) for i, j, t in cands), reverse=True)[:4]
        print(f"{a:6.1f}-{b:6.1f}  " + "  |  ".join(f"{lp:7.1f} P{i + 1}-P{j}" for lp, i, j in res), flush=True)
