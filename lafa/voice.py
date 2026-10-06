"""Explicit microphone capture; no always-on recording or background upload."""
import shutil
import subprocess
import tempfile
from pathlib import Path

class Voice:
    def __init__(self): self.speaker=None; self.recorder=None
    def speak(self, text, language="en"):
        self.stop_speaking()
        executable=shutil.which("espeak-ng") or shutil.which("espeak")
        if not executable: raise RuntimeError("Read aloud needs espeak-ng. Install it with your package manager.")
        # Tetum voice is not bundled; use Portuguese pronunciation as an explicit fallback.
        voice={"en":"en", "id":"id", "pt":"pt", "tet":"pt"}.get(language,"en")
        proc=subprocess.Popen([executable,"-v",voice,"-s","155","--stdin"],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        self.speaker=proc
        try:
            proc.communicate(text[:20_000].encode(),timeout=240)
        finally:
            if proc.poll() is None: proc.terminate()
            if self.speaker is proc: self.speaker=None
    def stop_speaking(self):
        if self.speaker and self.speaker.poll() is None: self.speaker.terminate()
    def capture_and_transcribe(self, client, online=lambda:True):
        executable=shutil.which("arecord")
        if not executable: raise RuntimeError("Microphone capture needs alsa-utils (arecord).")
        with tempfile.TemporaryDirectory(prefix="lafa-audio-") as folder:
            path=Path(folder)/"recording.wav"
            self.recorder=subprocess.Popen([executable,"-q","-D","default","-f","S16_LE","-r","16000","-c","1","-d","8",str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            _, error=self.recorder.communicate(timeout=14)
            code=self.recorder.returncode
            self.recorder=None
            if code: raise RuntimeError("Microphone could not be opened. Check your sound device and permissions.")
            if not online(): raise RuntimeError("Internet disconnected. Recording discarded.")
            return client.transcribe(path)
    def stop(self):
        self.stop_speaking()
        if self.recorder and self.recorder.poll() is None: self.recorder.terminate()
