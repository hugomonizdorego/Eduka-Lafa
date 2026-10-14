"""Read aloud on this computer with espeak-ng (works offline).

LAFA does not record the microphone and sends no audio anywhere."""
import shutil
import subprocess

class Voice:
    def __init__(self): self.speaker=None
    def speak(self, text, language="en", rate=155):
        self.stop_speaking()
        executable=shutil.which("espeak-ng") or shutil.which("espeak")
        if not executable: raise RuntimeError("Read aloud needs espeak-ng. Install it with your package manager.")
        # Tetum voice is not bundled; use Portuguese pronunciation as an explicit fallback.
        # Course languages pass their espeak-ng voice code directly (es, fr, de, cmn, ja, ko, ar, th, vi, tl).
        voice={"en":"en", "id":"id", "pt":"pt", "tet":"pt"}.get(language, language if str(language).isalpha() and len(str(language)) <= 3 else "en")
        proc=subprocess.Popen([executable,"-v",voice,"-s",str(max(80,min(260,int(rate)))),"--stdin"],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        self.speaker=proc
        try:
            proc.communicate(text[:20_000].encode(),timeout=240)
        finally:
            if proc.poll() is None: proc.terminate()
            if self.speaker is proc: self.speaker=None
    def stop_speaking(self):
        if self.speaker and self.speaker.poll() is None: self.speaker.terminate()
    def stop(self):
        self.stop_speaking()
