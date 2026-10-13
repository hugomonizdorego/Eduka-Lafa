"""Human-like movement for LAFA's character.

The drawings are single images, so LAFA is moved like a puppet with two
parts: the body above the hips and the legs below. Every frame gets:

* a walking gait: two small bounces per stride, the body leaning forward and
  shifting its weight from foot to foot, the legs stepping (sheared) in turn;
* breathing: the chest rises and falls gently when standing, slower asleep;
* attention: LAFA leans a little towards the mouse pointer when it is close;
* gestures: a wave (greeting), a jump with anticipation (crouch, stretch in
  the air, squash on landing) and a nod (yes);
* smooth changes: a new activity fades in instead of popping.

All values are small on purpose: the movement should feel alive, not busy.
"""
from dataclasses import dataclass
import math

@dataclass
class Frame:
    dx: float = 0.0          # body offset in pixels
    dy: float = 0.0
    lean: float = 0.0        # upper-body rotation around the hips (degrees)
    tilt: float = 0.0        # whole-body rotation (degrees)
    sx: float = 1.0          # scale (squash and stretch, breathing)
    sy: float = 1.0
    step: float = 0.0        # leg shear (-1 … 1 → stepping)
    shadow: float = 1.0      # ground shadow size
    split: bool = False      # draw body and legs separately

STANDING = {"idle", "talking", "thinking", "reading", "serious", "walking", "stretching", "gaming", "studying", "lecture", "motivator", "magic_show", "professor", "party"}
DANCING = {"tebe", "bidu"}

class Motion:
    """Animation clock and gestures for one character."""
    def __init__(self):
        self.t = 0.0; self.gesture = ""; self.gesture_t = 0.0; self.fade = 1.0
        self.look = 0.0          # -1 (pointer left) … 1 (pointer right)
        self.walking_speed = 1.0
    def advance(self, seconds):
        self.t += seconds
        if self.gesture:
            self.gesture_t += seconds
            if self.gesture_t >= GESTURES.get(self.gesture, 1.0): self.gesture = ""; self.gesture_t = 0.0
        if self.fade < 1.0: self.fade = min(1.0, self.fade + seconds / 0.28)
    def play(self, gesture):
        if gesture in GESTURES: self.gesture, self.gesture_t = gesture, 0.0
    def changed(self):
        """Call when the activity (drawing) changes, to fade it in."""
        self.fade = 0.35
    def attend(self, value):
        self.look += (max(-1.0, min(1.0, value)) - self.look) * 0.2
    def frame(self, pose, animated=True):
        f = Frame()
        if not animated: return f
        t = self.t
        if pose == "walking":
            stride = t * 5.2 * self.walking_speed          # steps per second ≈ 1.65
            f.split = True
            f.dy = -abs(math.sin(stride)) * 5.0 + 1.5        # two bounces per stride
            f.dx = math.sin(stride) * 1.6                    # weight shift
            f.lean = 4.0 + math.sin(stride * 2) * 1.2        # leaning forward into the walk
            f.step = math.sin(stride) * 0.16
            f.tilt = math.sin(stride) * 1.4
            f.shadow = 1.0 - abs(math.sin(stride)) * 0.08
        elif pose in DANCING:
            beat = t * 4.2
            f.split = True
            f.dy = -abs(math.sin(beat)) * 8.0; f.tilt = math.sin(beat) * 5.0
            f.step = math.sin(beat) * 0.12; f.lean = math.sin(beat * 0.5) * 6.0
            f.shadow = 1.0 - abs(math.sin(beat)) * 0.15
        elif pose == "sleeping":
            breath = math.sin(t * 1.3)
            f.sy = 1.0 + breath * 0.022; f.sx = 1.0 - breath * 0.008
        else:
            breath = math.sin(t * 2.1)
            f.split = pose in STANDING
            f.sy = 1.0 + breath * 0.014; f.dy = -breath * 0.6
            # Shifting weight now and then, like a person standing.
            f.lean = math.sin(t * 0.45) * 1.6 + self.look * 3.5
            f.tilt = math.sin(t * 0.31 + 1.0) * 0.8
            if pose == "talking": f.lean += math.sin(t * 6.0) * 1.4; f.dy -= abs(math.sin(t * 6.0)) * 1.2
        self.apply_gesture(f)
        return f
    def apply_gesture(self, f):
        if not self.gesture: return
        p = self.gesture_t / GESTURES[self.gesture]
        if self.gesture == "jump":
            if p < 0.2:                                     # anticipation: crouch
                k = p / 0.2; f.sy *= 1 - 0.10 * k; f.sx *= 1 + 0.06 * k
            elif p < 0.8:                                   # in the air: stretch
                k = (p - 0.2) / 0.6; h = math.sin(k * math.pi)
                f.dy -= h * 22; f.sy *= 1 + 0.07 * h; f.sx *= 1 - 0.04 * h; f.shadow *= 1 - 0.35 * h; f.step = 0
            else:                                           # landing: squash
                k = (p - 0.8) / 0.2; s = math.sin(k * math.pi)
                f.sy *= 1 - 0.08 * s; f.sx *= 1 + 0.05 * s
        elif self.gesture == "wave":
            f.split = True; f.lean += math.sin(p * math.pi * 6) * 7 * math.sin(p * math.pi); f.dy -= math.sin(p * math.pi) * 2
        elif self.gesture == "nod":
            f.split = True; f.lean += math.sin(p * math.pi * 4) * 5 * (1 - p) + 3
        elif self.gesture == "shake":
            f.tilt += math.sin(p * math.pi * 6) * 4 * (1 - p)

GESTURES = {"jump": 0.75, "wave": 1.4, "nod": 0.9, "shake": 0.9}
