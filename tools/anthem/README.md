# Timing the lyrics of the national anthem

`lafa/assets/timor/anthem/patria.json` says when each line of «Pátria» is sung
in `patria.mp3`, so Lafa can light up the lyrics while the music plays. The
times were measured, not guessed, in three steps (2026-11-02):

1. **Vocal separation** — `separate.py` runs the UVR MDX-Net model
   `Kim_Vocal_2.onnx` (https://github.com/TRvlvr/model_repo/releases) with
   onnxruntime and writes the singing alone (`vocals.wav`).
2. **Which words are sung where** — `score.py` and `heat.py` load Whisper
   large-v3-turbo (ONNX export of sherpa-onnx, GitHub release `asr-models`)
   and compute, for 5-second windows, how much more likely each lyric phrase
   is with the audio than with silence (teacher-forced decoding).
3. **Exact starts** — the melody (chroma of the vocal track) of every refrain
   is matched against the clearest one to find each line's start.

Result: in this recording the choir sings the refrain «Pátria, Pátria… da
nossa libertação» five times (0:13–1:43 three times, then an instrumental
interlude, then 2:14–3:19 twice); the verse is not sung. Lafa shows the whole
text for learning and highlights the refrain lines as they are sung.

```bash
pip install onnxruntime numpy scipy sherpa-onnx tiktoken
ffmpeg -i ../../lafa/assets/timor/anthem/patria.mp3 -ac 1 -ar 44100 mix44.wav
python separate.py Kim_Vocal_2.onnx mix44.wav vocals.wav
ffmpeg -i vocals.wav -ac 1 -ar 16000 vocals16.wav
python heat.py          # phrase × time table
```

Check the cue times by ear after any change of recording.
