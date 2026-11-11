# Timing the lyrics of the national anthem

`lafa/assets/timor/anthem/patria.json` says when each line of «Pátria» is sung
in `patria.mp3`, so Lafa can light up the lyrics while the music plays. The
times were measured, not guessed.

## The recording (0.3.1)

`patria.mp3` is the **instrumental** recording supplied by the project owner on
2026-11-11 (`P_tria_timor_leste_-_instrumental.mp3`, 2:08, 48 kHz stereo,
SHA-256 `3b561a12…0ee98`). It is a whole tone lower than the Government's vocal
recording (B♭ major instead of C major) and plays the anthem once:

| time (s)      | music                     | lines |
| ------------- | ------------------------- | ----- |
| 0 – 11.7      | introduction              | –     |
| 11.7 – 39.6   | refrain                   | 1–2   |
| 39.6 – 68.4   | refrain again             | 3–4   |
| 68.4 – 72.0   | short interlude           | –     |
| 72.0 – 98.4   | verse, first time         | 5–8   |
| 98.4 – 101.9  | short interlude           | –     |
| 101.9 – 127.6 | verse music, second time  | 9–12  |

## How the times were found (2026-11-11)

1. **Refrain.** The Government's vocal recording (`patria_56.mp3`, from
   timor-leste.gov.tl › National Symbols) had its line times measured in 0.3.0
   (vocal separation with MDX-Net + Whisper teacher-forced scoring, see git
   history). Its chroma, shifted down a whole tone, was aligned to the
   instrumental with DTW (step sizes 1:1, 1:2, 2:1 so the tempo ratio stays
   between ½ and 2). Best key shift: −2 semitones (cost 0.093 against 0.118
   for the next). The second line of each refrain («Glória…») starts where the
   choir enters on the held dominant chord (beat 24 and 58).
2. **Structure.** Beat tracking (librosa, ≈ 71 bpm) and beat-synchronous chroma
   show five blocks of 34 beats after a 12-beat introduction: the two refrains
   are the same music (similarity 0.976), and so are the two halves of the
   verse (0.984); any shift by one beat drops to ≈ 0.8.
3. **Verse lines.** A chord estimate per beat shows four two-bar phrases in each
   verse block, each closing on a cadence (C7→F, C→F, Cm→F, F→B♭). One phrase
   per lyric line; lines start half a beat before the phrase (singers' pickup).
   The verse is not sung in the vocal recording, so these four-per-block times
   come from the music only (accuracy ≈ 0.7 s).

Check the cue times by ear after any change of recording.

```bash
pip install numpy scipy soundfile librosa
ffmpeg -i ../../lafa/assets/timor/anthem/patria.mp3 -ac 1 -ar 22050 instr.wav
ffmpeg -i patria_56.mp3 -ac 1 -ar 22050 vocal.wav        # the Government's vocal recording
# the 0.3.0 data (commit bf6dbd1): its cues are the measured line times of the vocal recording
git show bf6dbd1:lafa/assets/timor/anthem/patria.json > patria-0.3.0.json
python3 instrumental.py instr.wav vocal.wav patria-0.3.0.json
# chroma + DTW against the vocal recording, beat tracking and chords:
#   librosa.feature.chroma_cqt, librosa.sequence.dtw(subseq=True, step_sizes_sigma=[[1,1],[1,2],[2,1]]),
#   librosa.beat.beat_track(start_bpm=72, tightness=200), triad templates per beat
```

The scripts used for 0.3.0 (`separate.py`, `score.py`, `heat.py`) are kept in
this folder for vocal recordings.
