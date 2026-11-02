"""Play a sound file (the national anthem) with a position for synchronised lyrics.

Backends, in order:
* Qt Multimedia — PyQt5 (Debian: python3-pyqt5.qtmultimedia + GStreamer
  "good" plugins for MP3) or PySide6;
* an external player started with QProcess — ffplay, mpv or mpg123. The
  position is then measured with a clock; pausing stops the player and
  playing again starts it at the saved position.
Without either, `available` is False and the page shows the lyrics only.
"""
import shutil

from .qt import QObject, QTimer, QElapsedTimer, QProcess, QUrl, QCoreApplication, Signal, BINDING

def _qt_multimedia():
    try:
        if BINDING == "PyQt5":
            from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
            return "qt5", QMediaPlayer, QMediaContent
        from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
        return "qt6", QMediaPlayer, QAudioOutput
    except ImportError:
        return None

def external_command(path, start=0.0):
    """argv for the first external player found, starting at `start` seconds (or None)."""
    start = max(0.0, float(start))
    if shutil.which("ffplay"): return ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-ss", f"{start:.2f}", str(path)]
    if shutil.which("mpv"): return ["mpv", "--no-video", "--really-quiet", f"--start={start:.2f}", str(path)]
    if shutil.which("mpg123"): return ["mpg123", "-q", "-k", str(int(start * 44100 / 1152)), str(path)]
    return None

class Player(QObject):
    position_changed = Signal(float)     # seconds, about 30 times a second while playing
    state_changed = Signal(str)          # "playing", "paused", "stopped"
    failed = Signal(str)
    def __init__(self, path, duration=0.0, parent=None, backend=None):
        super().__init__(parent); self.path = str(path); self.duration = float(duration or 0); self.state = "stopped"
        self._offset = 0.0; self._clock = QElapsedTimer(); self._process = None; self._qt = None
        self.tick = QTimer(self); self.tick.setInterval(33); self.tick.timeout.connect(self._poll)
        app = QCoreApplication.instance()
        if app is not None: app.aboutToQuit.connect(self.close)          # never leave a player process behind
        mm = _qt_multimedia() if backend in (None, "qt") else None
        if mm is not None:
            kind, QMediaPlayer, extra = mm
            try:
                self._qt = QMediaPlayer(self)
                if kind == "qt5":
                    self._qt.setMedia(extra(QUrl.fromLocalFile(self.path)))
                    self._qt.stateChanged.connect(self._qt_state)
                    try: self._qt.error.connect(lambda *_: self._qt_error())
                    except (AttributeError, TypeError): pass
                else:
                    self._output = extra(self); self._qt.setAudioOutput(self._output); self._qt.setSource(QUrl.fromLocalFile(self.path))
                    self._qt.playbackStateChanged.connect(self._qt_state); self._qt.errorOccurred.connect(lambda *_: self._qt_error())
                self.backend = "qt"
            except Exception:       # a broken multimedia install must not stop the page
                self._qt = None
        if self._qt is None:
            self.backend = "process" if backend in (None, "process") and external_command(self.path) else None
    @property
    def available(self): return self.backend is not None
    # ------------------------------------------------------------- control
    def play(self):
        self._asked = QElapsedTimer(); self._asked.start()
        if self.backend == "qt": self._qt.play()
        elif self.backend == "process":
            if self.state == "playing": return
            self._start_process(self._offset)
        else: self.failed.emit("no-audio"); return
        self._set_state("playing"); self.tick.start()
    def pause(self):
        if self.state != "playing": return
        self._asked = None
        if self.backend == "qt": self._qt.pause()
        elif self.backend == "process": self._offset = self.position(); self._kill()
        self._set_state("paused"); self.tick.stop(); self.position_changed.emit(self.position())
    def toggle(self): self.pause() if self.state == "playing" else self.play()
    def stop(self):
        self._asked = None                       # a stop we asked for is not a failure
        if self.backend == "qt": self._qt.stop()
        elif self.backend == "process": self._kill()
        self._offset = 0.0; self.tick.stop(); self._set_state("stopped"); self.position_changed.emit(0.0)
    def seek(self, seconds):
        seconds = max(0.0, min(float(seconds), self.duration or float(seconds)))
        if self.backend == "qt": self._qt.setPosition(int(seconds * 1000))
        elif self.backend == "process":
            self._offset = seconds
            if self.state == "playing": self._kill(); self._start_process(seconds)
        else: self._offset = seconds
        self.position_changed.emit(seconds)
    def position(self):
        if self.backend == "qt": return self._qt.position() / 1000.0
        if self.backend == "process" and self.state == "playing" and self._clock.isValid():
            return min(self._offset + self._clock.elapsed() / 1000.0, self.duration or 1e9)
        return self._offset
    def close(self):
        self._asked = None; self._closing = True; self.tick.stop()
        if self.backend == "qt": self._qt.stop()
        self._kill()
    # ------------------------------------------------------------ internal
    def _set_state(self, state):
        if state != self.state: self.state = state; self.state_changed.emit(state)
    def _poll(self):
        pos = self.position(); self.position_changed.emit(pos)
        if self.backend == "process" and self.duration and pos >= self.duration - 0.05: self.stop()
    def _qt_state(self, value):
        name = getattr(value, "name", None)
        playing = (name == "PlayingState") or (not name and int(value) == 1)
        paused = (name == "PausedState") or (not name and int(value) == 2)
        if playing: self._set_state("playing"); self.tick.start()
        elif paused: self._set_state("paused"); self.tick.stop()
        else:
            self.tick.stop()
            asked = getattr(self, "_asked", None)
            if self.state == "playing" and asked is not None and asked.isValid() and asked.elapsed() < 6000 and self.position() < 0.2:
                self._asked = None; self._qt_error(); return      # stopped at once: no sound device or decoder
            self._set_state("stopped"); self.position_changed.emit(self.position())
    def _qt_error(self):
        # Qt Multimedia without a decoder or sound device: try an external player instead.
        if getattr(self, "_closing", False): return
        if self.backend == "qt" and external_command(self.path):
            pos = self.position(); self.backend = "process"; self._offset = pos
            try: self._qt.stop()
            except RuntimeError: pass
            if self.state == "playing": self._start_process(pos); self.tick.start()
            return
        self.failed.emit("audio"); self.stop()
    def _start_process(self, start):
        argv = external_command(self.path, start)
        if not argv: self.failed.emit("no-audio"); return
        self._kill(); self._process = QProcess(self); self._process.setProgram(argv[0]); self._process.setArguments(argv[1:])
        self._process.finished.connect(self._process_finished); self._process.start()
        self._offset = start; self._clock.start()
    def _process_finished(self, code=0, *_):
        if self.state != "playing": return
        ran = self._clock.elapsed() / 1000.0 if self._clock.isValid() else 0.0
        if self.duration and self.position() >= self.duration - 1.0: self.stop()
        elif ran < 2.0:
            # The player stopped at once (no sound device or no decoder): say so instead of
            # running the lyrics in silence.
            self._process = None; self.failed.emit("audio"); self.stop()
    def _kill(self):
        p, self._process = self._process, None
        if p is not None:
            try: p.finished.disconnect()
            except (TypeError, RuntimeError): pass
            p.kill(); p.waitForFinished(500); p.deleteLater()
