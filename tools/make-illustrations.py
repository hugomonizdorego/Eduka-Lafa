#!/usr/bin/env python3
"""Generate Lafa's illustrations into lafa/assets/illustrations/ (+ manifest.json).

    python3 tools/make-illustrations.py            # all
    python3 tools/make-illustrations.py flag map   # only these keys

Soft "clay" vector scenes in Lafa's own style — pastel gradients, rounded
shapes, gentle shadows — one per key in docs/CONTENT-SCHEMA.md. They are
original work for Lafa (CC BY-SA 4.0). The Timor-Leste outline comes from the
packaged map data (geoBoundaries / © OpenStreetMap contributors, ODbL). The
flag follows Artigu 15 of the Konstituisaun. Real photographs are downloaded by
the learner (free licences only) and are not part of these files.
Scenes are 640×360 (16:9) and carry no words, so they serve all languages.
"""
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "lafa/assets/illustrations"
W, H = 640, 360
_uid = [0]

def uid(prefix="g"):
    _uid[0] += 1; return f"{prefix}{_uid[0]}"

# ------------------------------------------------------------------ basics
class Scene:
    def __init__(self): self.defs = []; self.body = []
    def add(self, *parts): self.body.extend(p for p in parts if p); return self
    def grad(self, *stops, x1=0, y1=0, x2=0, y2=1):
        i = uid(); s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in [(st + (1,))[:3] if len(st) == 2 else st for st in stops])
        self.defs.append(f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'); return f"url(#{i})"
    def radial(self, *stops, cx=0.5, cy=0.5, r=0.5):
        i = uid(); s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in [(st + (1,))[:3] if len(st) == 2 else st for st in stops])
        self.defs.append(f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'); return f"url(#{i})"
    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
                f'<defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>\n')

def rect(x, y, w, h, fill, rx=0, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" {extra}/>'

def circle(cx, cy, r, fill, extra=""):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" {extra}/>'

def ellipse(cx, cy, rx, ry, fill, extra=""):
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" {extra}/>'

def path(d, fill="none", stroke=None, width=0, extra=""):
    st = f' stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"' if stroke else ""
    return f'<path d="{d}" fill="{fill}"{st} {extra}/>'

def poly(points, fill, extra=""):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" fill="{fill}" {extra}/>'

def group(content, transform="", opacity=1):
    return f'<g transform="{transform}" opacity="{opacity}">{content}</g>'

def shadow(cx, cy, rx, ry=None, alpha=0.16):
    return ellipse(cx, cy, rx, ry or rx * 0.22, "#2a1d5c", f'opacity="{alpha}"')

# ------------------------------------------------------------------ palettes
SKIES = {
    "day": ("#bfe3ff", "#e9f5ff", "#fdf2fb"), "dawn": ("#d9ccff", "#fbd7ea", "#fff1e3"), "sunset": ("#ffc6a8", "#ffb3cf", "#d7c5ff"),
    "night": ("#2b2468", "#4b3a8f", "#7b5ab5"), "mint": ("#c9f2e6", "#eefcf6", "#fdf6ff"), "paper": ("#fff4e0", "#ffeef3", "#f1ebff"),
    "lilac": ("#e4d9ff", "#f6eeff", "#ffeef6"), "sea": ("#bde6ff", "#e2f6ff", "#f2fbff"),
}

def sky(s, kind="day"):
    a, b, c = SKIES[kind]; s.add(rect(0, 0, W, H, s.grad((0, a), (0.6, b), (1, c))))

def sun(s, x, y, r=34, color="#ffd36b"):
    s.add(circle(x, y, r * 1.9, s.radial((0, color, 0.55), (1, color, 0)))); s.add(circle(x, y, r, s.grad((0, "#fff2b8"), (1, color))))

def moon(s, x, y, r=26):
    s.add(circle(x, y, r * 1.8, s.radial((0, "#fff7d6", 0.35), (1, "#fff7d6", 0)))); s.add(circle(x, y, r, "#fff3c4")); s.add(circle(x + r * 0.4, y - r * 0.25, r * 0.9, SKIES["night"][1]))

def cloud(s, x, y, k=1.0, color="#ffffff", opacity=0.95):
    s.add(group(ellipse(x, y, 40 * k, 15 * k, color) + circle(x - 16 * k, y - 8 * k, 16 * k, color) + circle(x + 12 * k, y - 13 * k, 20 * k, color), opacity=opacity))

def stars(s, n, seed, color="#ffffff"):
    rnd = random.Random(seed)
    for _ in range(n): s.add(circle(rnd.uniform(0, W), rnd.uniform(0, H * 0.55), rnd.choice([0.9, 1.3, 1.8]), color, f'opacity="{rnd.uniform(0.4, 1):.2f}"'))

def hills(s, y, amp, c1, c2, seed, n=5):
    rnd = random.Random(seed); step = W / n; d = f"M0 {H} L0 {y} "
    for i in range(n):
        x1 = i * step + step / 2; y1 = y - amp * (0.5 + rnd.random() * 0.8); x2 = (i + 1) * step; y2 = y + amp * (rnd.random() - 0.5) * 0.6
        d += f"Q{x1:.0f} {y1:.0f} {x2:.0f} {y2:.0f} "
    s.add(path(d + f"L{W} {H} Z", s.grad((0, c1), (1, c2))))

def mountain(s, x, base, w, h, c1="#8fb5e8", c2="#6c8fd1", snow=False, peak_shift=0):
    px = x + w / 2 + peak_shift; d = f"M{x} {base} Q{x + w * 0.25} {base - h * 0.55} {px - w * 0.06} {base - h * 0.97} Q{px} {base - h * 1.04} {px + w * 0.06} {base - h * 0.96} Q{x + w * 0.75} {base - h * 0.5} {x + w} {base} Z"
    s.add(path(d, s.grad((0, c1), (1, c2), x2=0.4, y2=1)))
    s.add(path(f"M{px - w * 0.06} {base - h * 0.97} Q{px} {base - h * 1.04} {px + w * 0.06} {base - h * 0.96} Q{x + w * 0.62} {base - h * 0.55} {x + w * 0.58} {base - h * 0.2}", "#ffffff", extra='opacity="0.18"'))
    if snow: s.add(path(f"M{px - w * 0.1} {base - h * 0.86} Q{px} {base - h * 1.04} {px + w * 0.1} {base - h * 0.86} Q{px} {base - h * 0.8} {px - w * 0.1} {base - h * 0.86}Z", "#ffffff", extra='opacity="0.9"'))

def sea(s, y, c1="#7fd0ee", c2="#4aa3d6", waves=True):
    s.add(rect(0, y, W, H - y, s.grad((0, c1), (1, c2))))
    if waves:
        for i, wy in enumerate((y + 14, y + 34, y + 58)):
            d = "M0 %.0f " % wy + " ".join(f"q20 -6 40 0 t40 0" for _ in range(17))
            s.add(path(d, stroke="#ffffff", width=2, extra=f'opacity="{0.35 - i * 0.08:.2f}"'))

def sand(s, y, c1="#fbe6bd", c2="#f3d39a"):
    s.add(path(f"M0 {y + 10} Q{W * 0.3} {y - 12} {W * 0.6} {y + 4} T{W} {y - 4} L{W} {H} L0 {H} Z", s.grad((0, c1), (1, c2))))

def ground(s, y, c1="#bfe6a5", c2="#8fcf7e"):
    s.add(path(f"M0 {y} Q{W * 0.5} {y - 18} {W} {y} L{W} {H} L0 {H} Z", s.grad((0, c1), (1, c2))))

def palm(s, x, y, k=1.0, trunk="#a77449", leaf=("#5fc28a", "#2f9a63")):
    s.add(path(f"M{x} {y} Q{x + 8 * k} {y - 55 * k} {x + 2 * k} {y - 110 * k}", stroke=trunk, width=8 * k))
    tx, ty = x + 2 * k, y - 110 * k; g = s.grad((0, leaf[0]), (1, leaf[1]))
    for a in (-165, -125, -60, -15, 205):
        r = math.radians(a); ex, ey = tx + math.cos(r) * 58 * k, ty + math.sin(r) * 26 * k + 22 * k; cx, cy = tx + math.cos(r) * 32 * k, ty - 20 * k
        s.add(path(f"M{tx:.0f} {ty:.0f} Q{cx:.0f} {cy:.0f} {ex:.0f} {ey:.0f} Q{(cx + ex) / 2:.0f} {cy + 16 * k:.0f} {tx:.0f} {ty:.0f}Z", g))
    s.add(circle(tx - 4 * k, ty + 6 * k, 5 * k, "#8a5a32")); s.add(circle(tx + 5 * k, ty + 7 * k, 5 * k, "#7a4e2a"))

def tree(s, x, y, k=1.0, c1="#7fd49a", c2="#3fa66a", trunk="#9a6a43"):
    s.add(shadow(x, y + 2, 26 * k)); s.add(rect(x - 5 * k, y - 34 * k, 10 * k, 36 * k, trunk, 4))
    g = s.grad((0, c1), (1, c2)); s.add(circle(x, y - 52 * k, 28 * k, g)); s.add(circle(x - 20 * k, y - 38 * k, 18 * k, g)); s.add(circle(x + 20 * k, y - 38 * k, 18 * k, g))
    s.add(circle(x - 8 * k, y - 62 * k, 9 * k, "#ffffff", 'opacity="0.25"'))

def bush(s, x, y, k=1.0, c1="#8ddca6", c2="#4bb070"):
    g = s.grad((0, c1), (1, c2)); s.add(ellipse(x, y, 30 * k, 16 * k, g)); s.add(circle(x - 12 * k, y - 8 * k, 13 * k, g)); s.add(circle(x + 10 * k, y - 10 * k, 15 * k, g))

def flower(s, x, y, k=1.0, petal="#ff8fb8", center="#ffd36b"):
    for a in range(0, 360, 60):
        r = math.radians(a); s.add(ellipse(x + math.cos(r) * 7 * k, y + math.sin(r) * 7 * k, 6 * k, 6 * k, petal))
    s.add(circle(x, y, 5 * k, center))

# --------------------------------------------------------------- people & co
SKIN = ["#c98b5e", "#a96f45", "#8c5a37", "#d29b6c"]

def person(s, x, y, k=1.0, shirt="#7c5cfc", skin=SKIN[0], hair="#2b1d14", skirt=None, arms_up=False, hat=None, holding=None):
    """A friendly round figure standing on (x, y)."""
    s.add(shadow(x, y, 20 * k))
    if skirt: s.add(path(f"M{x - 15 * k} {y - 34 * k} L{x + 15 * k} {y - 34 * k} L{x + 19 * k} {y - 2 * k} L{x - 19 * k} {y - 2 * k}Z", skirt))
    else:
        s.add(rect(x - 11 * k, y - 34 * k, 9 * k, 34 * k, "#3d3a5c", 4)); s.add(rect(x + 2 * k, y - 34 * k, 9 * k, 34 * k, "#3d3a5c", 4))
    s.add(rect(x - 16 * k, y - 72 * k, 32 * k, 42 * k, s.grad((0, shirt), (1, shirt)), 13 * k))
    s.add(rect(x - 12 * k, y - 70 * k, 10 * k, 30 * k, "#ffffff", 6, 'opacity="0.15"'))
    if arms_up:
        s.add(path(f"M{x - 14 * k} {y - 64 * k} Q{x - 32 * k} {y - 84 * k} {x - 30 * k} {y - 98 * k}", stroke=shirt, width=8 * k))
        s.add(path(f"M{x + 14 * k} {y - 64 * k} Q{x + 32 * k} {y - 84 * k} {x + 30 * k} {y - 98 * k}", stroke=shirt, width=8 * k))
        s.add(circle(x - 30 * k, y - 100 * k, 5 * k, skin)); s.add(circle(x + 30 * k, y - 100 * k, 5 * k, skin))
    else:
        s.add(path(f"M{x - 15 * k} {y - 62 * k} Q{x - 22 * k} {y - 46 * k} {x - 19 * k} {y - 34 * k}", stroke=shirt, width=8 * k))
        s.add(path(f"M{x + 15 * k} {y - 62 * k} Q{x + 22 * k} {y - 46 * k} {x + 19 * k} {y - 34 * k}", stroke=shirt, width=8 * k))
        s.add(circle(x - 19 * k, y - 32 * k, 4.5 * k, skin)); s.add(circle(x + 19 * k, y - 32 * k, 4.5 * k, skin))
    s.add(circle(x, y - 86 * k, 15 * k, skin)); s.add(path(f"M{x - 15 * k} {y - 88 * k} Q{x - 14 * k} {y - 104 * k} {x} {y - 103 * k} Q{x + 15 * k} {y - 104 * k} {x + 15 * k} {y - 88 * k} Q{x + 6 * k} {y - 96 * k} {x - 15 * k} {y - 88 * k}Z", hair))
    s.add(circle(x - 5 * k, y - 86 * k, 1.6 * k, "#2b1d14")); s.add(circle(x + 5 * k, y - 86 * k, 1.6 * k, "#2b1d14"))
    s.add(path(f"M{x - 4 * k} {y - 80 * k} Q{x} {y - 77 * k} {x + 4 * k} {y - 80 * k}", stroke="#5a2e1d", width=1.4 * k))
    if hat == "straw": s.add(path(f"M{x - 26 * k} {y - 96 * k} Q{x} {y - 128 * k} {x + 26 * k} {y - 96 * k}Z", "#e9c46a"))
    if hat == "cap": s.add(path(f"M{x - 15 * k} {y - 94 * k} Q{x} {y - 112 * k} {x + 15 * k} {y - 94 * k}Z", "#3b82f6")); s.add(rect(x, y - 96 * k, 20 * k, 4 * k, "#2563eb", 2))
    if hat == "helmet": s.add(path(f"M{x - 17 * k} {y - 90 * k} Q{x} {y - 118 * k} {x + 17 * k} {y - 90 * k}Z", "#5aa9ff"))
    if hat == "headdress":
        s.add(path(f"M{x - 13 * k} {y - 98 * k} L{x - 6 * k} {y - 124 * k} L{x} {y - 102 * k} L{x + 6 * k} {y - 124 * k} L{x + 13 * k} {y - 98 * k}Z", "#e9b949"))
        s.add(path(f"M{x} {y - 104 * k} Q{x + 4 * k} {y - 140 * k} {x + 16 * k} {y - 150 * k}", stroke="#1f1a17", width=3 * k))
    if holding == "book": s.add(rect(x - 12 * k, y - 52 * k, 24 * k, 16 * k, "#3b82f6", 3)); s.add(rect(x - 1 * k, y - 52 * k, 2 * k, 16 * k, "#ffffff", 0, 'opacity="0.7"'))
    if holding == "flag": flag_shape(s, x + 22 * k, y - 120 * k, 44 * k, pole=True)

def crowd(s, x, y, n=5, k=0.8, seed=3):
    rnd = random.Random(seed); colors = ["#7c5cfc", "#ec4899", "#14b88c", "#f2a516", "#3b93ec", "#f77f3a"]
    for i in range(n):
        person(s, x + i * 40 * k + rnd.uniform(-6, 6), y + rnd.uniform(-4, 6), k * rnd.uniform(0.85, 1.05), shirt=rnd.choice(colors), skin=rnd.choice(SKIN))

def flag_shape(s, x, y, w, pole=False, wave=True):
    """Bandeira nasionál (Artigu 15): red field, yellow and black triangles, white star."""
    h = w / 2
    if pole: s.add(rect(x - 3, y - 4, 4, h * 3.2, "#8a6a4a", 2))
    d = f"M{x} {y} Q{x + w * 0.25} {y - h * 0.08} {x + w * 0.5} {y} T{x + w} {y} L{x + w} {y + h} Q{x + w * 0.75} {y + h * 1.08} {x + w * 0.5} {y + h} T{x} {y + h}Z" if wave else f"M{x} {y}h{w}v{h}h{-w}Z"
    s.add(path(d, "#dc241f")); s.add(poly([(x, y), (x + w * 0.5, y + h / 2), (x, y + h)], "#ffc726")); s.add(poly([(x, y), (x + w / 3, y + h / 2), (x, y + h)], "#1a1a1a"))
    cx, cy, r = x + w * 0.11, y + h / 2, h * 0.17; pts = []
    for i in range(10):
        a = math.radians(-114 + i * 36); rr = r if i % 2 == 0 else r * 0.42; pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    s.add(poly(pts, "#ffffff"))
    s.add(path(d, "#ffffff", extra='opacity="0.08"'))

def crocodile(s, x, y, k=1.0, c1="#7fcf6e", c2="#4aa356"):
    g = s.grad((0, c1), (1, c2)); s.add(shadow(x + 40 * k, y + 4 * k, 110 * k, 10 * k))
    s.add(path(f"M{x - 70 * k} {y} Q{x - 20 * k} {y - 34 * k} {x + 60 * k} {y - 30 * k} L{x + 140 * k} {y - 22 * k} Q{x + 160 * k} {y - 14 * k} {x + 140 * k} {y - 6 * k} L{x + 60 * k} {y - 4 * k} Q{x + 10 * k} {y + 6 * k} {x - 70 * k} {y}Z", g))
    s.add(path(f"M{x - 70 * k} {y} Q{x - 110 * k} {y - 6 * k} {x - 150 * k} {y + 4 * k} Q{x - 110 * k} {y + 6 * k} {x - 70 * k} {y + 2 * k}Z", g))
    for i in range(8): s.add(poly([(x - 60 * k + i * 15 * k, y - 22 * k + i * 0.5 * k), (x - 53 * k + i * 15 * k, y - 32 * k), (x - 46 * k + i * 15 * k, y - 22 * k)], c2))
    s.add(circle(x + 66 * k, y - 32 * k, 7 * k, "#ffffff")); s.add(circle(x + 68 * k, y - 32 * k, 3.5 * k, "#1f1a3d"))
    for lx in (-30, 30): s.add(rect(x + lx * k, y - 6 * k, 10 * k, 14 * k, c2, 4))
    s.add(path(f"M{x + 80 * k} {y - 12 * k} L{x + 140 * k} {y - 12 * k}", stroke="#2e6b33", width=1.6 * k))

def bird(s, x, y, k=1.0, body="#ffffff", crest="#ffd36b", wing="#e8e8f5"):
    s.add(ellipse(x, y, 20 * k, 13 * k, body)); s.add(circle(x + 16 * k, y - 10 * k, 9 * k, body))
    s.add(path(f"M{x + 12 * k} {y - 18 * k} Q{x + 8 * k} {y - 34 * k} {x + 20 * k} {y - 30 * k} Q{x + 14 * k} {y - 22 * k} {x + 22 * k} {y - 18 * k}", crest))
    s.add(poly([(x + 24 * k, y - 11 * k), (x + 31 * k, y - 8 * k), (x + 24 * k, y - 6 * k)], "#3a3a3a")); s.add(circle(x + 18 * k, y - 12 * k, 1.8 * k, "#1f1a3d"))
    s.add(path(f"M{x - 4 * k} {y - 4 * k} Q{x - 18 * k} {y - 22 * k} {x - 30 * k} {y - 2 * k}Z", wing)); s.add(path(f"M{x - 18 * k} {y + 4 * k} L{x - 34 * k} {y + 12 * k} L{x - 20 * k} {y + 10 * k}Z", body))

def fish(s, x, y, k=1.0, c="#ffb35c", stripe="#ffffff"):
    s.add(path(f"M{x - 18 * k} {y} Q{x} {y - 12 * k} {x + 16 * k} {y} Q{x} {y + 12 * k} {x - 18 * k} {y}Z", c)); s.add(poly([(x - 16 * k, y), (x - 28 * k, y - 9 * k), (x - 28 * k, y + 9 * k)], c))
    s.add(rect(x - 4 * k, y - 8 * k, 3 * k, 16 * k, stripe, 1, 'opacity="0.8"')); s.add(circle(x + 9 * k, y - 2 * k, 1.8 * k, "#1f1a3d"))

def whale(s, x, y, k=1.0, c1="#7aa6ee", c2="#4f7fd6"):
    g = s.grad((0, c1), (1, c2))
    s.add(path(f"M{x - 90 * k} {y} Q{x - 60 * k} {y - 48 * k} {x + 40 * k} {y - 38 * k} Q{x + 92 * k} {y - 30 * k} {x + 96 * k} {y} Q{x + 60 * k} {y + 22 * k} {x - 40 * k} {y + 14 * k}Z", g))
    s.add(path(f"M{x - 86 * k} {y} Q{x - 120 * k} {y - 28 * k} {x - 132 * k} {y - 12 * k} Q{x - 110 * k} {y + 4 * k} {x - 130 * k} {y + 22 * k} Q{x - 108 * k} {y + 18 * k} {x - 86 * k} {y + 4 * k}Z", g))
    s.add(path(f"M{x - 30 * k} {y + 8 * k} Q{x + 30 * k} {y + 18 * k} {x + 86 * k} {y + 6 * k}", stroke="#e4eeff", width=6 * k, extra='opacity="0.7"'))
    s.add(circle(x + 56 * k, y - 12 * k, 3 * k, "#1f1a3d"))

def coral(s, x, y, k=1.0, c="#ff8fa3"):
    for dx, h, a in ((-14, 40, -18), (0, 54, 0), (14, 36, 20)):
        s.add(path(f"M{x + dx * k} {y} Q{x + (dx + a * 0.3) * k} {y - h * 0.6 * k} {x + (dx + a) * k} {y - h * k}", stroke=c, width=7 * k))
        s.add(circle(x + (dx + a) * k, y - h * k, 5 * k, c))

def buffalo(s, x, y, k=1.0, c="#6d6a7a"):
    s.add(shadow(x, y, 50 * k)); s.add(ellipse(x, y - 30 * k, 48 * k, 26 * k, c))
    for lx in (-32, -14, 16, 32): s.add(rect(x + lx * k - 5 * k, y - 14 * k, 10 * k, 16 * k, c, 3))
    s.add(ellipse(x + 50 * k, y - 36 * k, 18 * k, 15 * k, c)); s.add(path(f"M{x + 40 * k} {y - 48 * k} Q{x + 20 * k} {y - 70 * k} {x + 34 * k} {y - 76 * k}", stroke="#e8e0cf", width=5 * k))
    s.add(path(f"M{x + 60 * k} {y - 48 * k} Q{x + 82 * k} {y - 70 * k} {x + 68 * k} {y - 76 * k}", stroke="#e8e0cf", width=5 * k)); s.add(circle(x + 56 * k, y - 38 * k, 2 * k, "#1f1a3d"))

def horse(s, x, y, k=1.0, c="#a8714a"):
    s.add(shadow(x, y, 44 * k)); s.add(ellipse(x, y - 34 * k, 40 * k, 18 * k, c))
    for lx in (-26, -10, 14, 28): s.add(rect(x + lx * k - 4 * k, y - 20 * k, 8 * k, 22 * k, c, 3))
    s.add(path(f"M{x + 30 * k} {y - 44 * k} L{x + 48 * k} {y - 78 * k} L{x + 64 * k} {y - 70 * k} L{x + 44 * k} {y - 38 * k}Z", c))
    s.add(path(f"M{x + 46 * k} {y - 80 * k} Q{x + 34 * k} {y - 60 * k} {x + 30 * k} {y - 46 * k}", stroke="#5a3a24", width=5 * k)); s.add(circle(x + 54 * k, y - 72 * k, 2 * k, "#1f1a3d"))

# ------------------------------------------------------------------ buildings
def uma_lulik(s, x, y, k=1.0, roof=("#c99b5c", "#8d6534"), wall="#a0784c"):
    """Tall thatched sacred house on stilts (Fataluku-style silhouette, simplified)."""
    s.add(shadow(x, y + 2, 70 * k, 10 * k))
    for px in (-40, -14, 14, 40): s.add(rect(x + px * k - 4 * k, y - 48 * k, 8 * k, 50 * k, "#6b4a2b", 2))
    s.add(rect(x - 46 * k, y - 66 * k, 92 * k, 22 * k, wall, 4)); s.add(rect(x - 46 * k, y - 50 * k, 92 * k, 6 * k, "#5c3d22", 2))
    s.add(path(f"M{x - 62 * k} {y - 62 * k} Q{x - 30 * k} {y - 120 * k} {x} {y - 186 * k} Q{x + 30 * k} {y - 120 * k} {x + 62 * k} {y - 62 * k}Z", s.grad((0, roof[0]), (1, roof[1]))))
    for i in range(6): s.add(path(f"M{x - 54 * k + i * 4 * k} {y - 70 * k - i * 18 * k} Q{x} {y - 84 * k - i * 18 * k} {x + 54 * k - i * 4 * k} {y - 70 * k - i * 18 * k}", stroke="#7a5428", width=1.5 * k, extra='opacity="0.5"'))
    s.add(path(f"M{x} {y - 186 * k} L{x - 8 * k} {y - 206 * k} M{x} {y - 186 * k} L{x + 8 * k} {y - 206 * k}", stroke="#5c3d22", width=3 * k))
    s.add(rect(x - 10 * k, y - 64 * k, 20 * k, 18 * k, "#e7c36a", 3))

def house(s, x, y, k=1.0, wall="#fff4e6", roof="#e56b6f"):
    s.add(shadow(x, y + 1, 46 * k)); s.add(rect(x - 36 * k, y - 46 * k, 72 * k, 46 * k, wall, 4)); s.add(poly([(x - 44 * k, y - 44 * k), (x, y - 78 * k), (x + 44 * k, y - 44 * k)], roof))
    s.add(rect(x - 8 * k, y - 26 * k, 16 * k, 26 * k, "#b07a52", 3)); s.add(rect(x - 28 * k, y - 34 * k, 14 * k, 12 * k, "#9fd3f5", 2)); s.add(rect(x + 14 * k, y - 34 * k, 14 * k, 12 * k, "#9fd3f5", 2))

def church(s, x, y, k=1.0, wall="#fffaf0", roof="#c0607a"):
    s.add(shadow(x, y + 2, 70 * k, 10 * k)); s.add(rect(x - 54 * k, y - 70 * k, 108 * k, 70 * k, wall, 6)); s.add(poly([(x - 62 * k, y - 66 * k), (x, y - 110 * k), (x + 62 * k, y - 66 * k)], roof))
    s.add(rect(x - 16 * k, y - 150 * k, 32 * k, 84 * k, wall, 4)); s.add(poly([(x - 20 * k, y - 148 * k), (x, y - 182 * k), (x + 20 * k, y - 148 * k)], roof))
    s.add(rect(x - 2 * k, y - 204 * k, 4 * k, 24 * k, "#e9b949")); s.add(rect(x - 9 * k, y - 196 * k, 18 * k, 4 * k, "#e9b949"))
    s.add(path(f"M{x - 12 * k} {y} L{x - 12 * k} {y - 30 * k} Q{x} {y - 44 * k} {x + 12 * k} {y - 30 * k} L{x + 12 * k} {y}Z", "#9b6b4a")); s.add(circle(x, y - 116 * k, 8 * k, "#9fd3f5"))
    for wx in (-38, 30): s.add(path(f"M{x + wx * k} {y - 22 * k} v-20 q4 -8 8 0 v20z", "#9fd3f5"))

def mosque(s, x, y, k=1.0, wall="#f4fbff", dome="#5cc6a8"):
    s.add(shadow(x, y + 2, 66 * k, 10 * k)); s.add(rect(x - 50 * k, y - 60 * k, 100 * k, 60 * k, wall, 6)); s.add(path(f"M{x - 34 * k} {y - 60 * k} Q{x - 34 * k} {y - 112 * k} {x} {y - 116 * k} Q{x + 34 * k} {y - 112 * k} {x + 34 * k} {y - 60 * k}Z", dome))
    s.add(rect(x + 56 * k, y - 140 * k, 16 * k, 140 * k, wall, 4)); s.add(path(f"M{x + 56 * k} {y - 140 * k} Q{x + 64 * k} {y - 162 * k} {x + 72 * k} {y - 140 * k}Z", dome))
    s.add(path(f"M{x - 3 * k} {y - 126 * k} a8 8 0 1 0 8 -6 a6 6 0 1 1 -8 6z", "#e9b949"))
    s.add(path(f"M{x - 10 * k} {y} v-24 q10 -14 20 0 v24z", "#7fbfae"))

def columns_building(s, x, y, k=1.0, wall="#fffaf2", roof="#c9b6ff", n=6, w=200, h=90, flag=False, dome=False):
    s.add(shadow(x, y + 2, w * 0.6 * k, 12 * k)); s.add(rect(x - w / 2 * k, y - 10 * k, w * k, 10 * k, "#e8dcc8", 2))
    s.add(rect(x - w / 2 * k + 8 * k, y - h * k, (w - 16) * k, (h - 10) * k, wall, 4))
    for i in range(n):
        cx = x - w / 2 * k + 22 * k + i * (w - 44) * k / (n - 1); s.add(rect(cx - 5 * k, y - (h - 14) * k, 10 * k, (h - 24) * k, "#ffffff")); s.add(rect(cx - 6 * k, y - (h - 14) * k, 12 * k, 5 * k, "#efe6d6"))
    s.add(poly([(x - w / 2 * k, y - (h - 2) * k), (x, y - (h + 38) * k), (x + w / 2 * k, y - (h - 2) * k)], s.grad((0, lighten_hex(roof, 0.2)), (1, roof))))
    if dome: s.add(path(f"M{x - 30 * k} {y - (h + 30) * k} Q{x} {y - (h + 80) * k} {x + 30 * k} {y - (h + 30) * k}Z", "#f3d38a"))
    if flag: s.add(rect(x - 1.5 * k, y - (h + 96) * k, 3 * k, 60 * k, "#8a6a4a")); flag_shape(s, x + 1.5 * k, y - (h + 96) * k, 44 * k)

def lighten_hex(c, t):
    c = c.lstrip("#"); r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(int(v + (255 - v) * t) for v in (r, g, b))

def fort(s, x, y, k=1.0, wall="#e9d8b8", shade="#cdb48e"):
    s.add(shadow(x, y + 2, 120 * k, 12 * k)); s.add(rect(x - 110 * k, y - 60 * k, 220 * k, 60 * k, s.grad((0, wall), (1, shade)), 4))
    for i in range(11): s.add(rect(x - 110 * k + i * 21 * k, y - 72 * k, 12 * k, 14 * k, wall, 2))
    for bx in (-110, 92): s.add(rect(x + bx * k, y - 92 * k, 18 * k, 92 * k, shade, 3)); s.add(rect(x + bx * k - 3 * k, y - 98 * k, 24 * k, 8 * k, wall, 2))
    s.add(path(f"M{x - 16 * k} {y} v-30 q16 -20 32 0 v30z", "#7a5a3a")); s.add(rect(x + 40 * k, y - 40 * k, 16 * k, 4 * k, "#5a4630", 2))

def statue_cristo(s, x, y, k=1.0):
    """A statue with open arms on a globe and pedestal on a hill-top (Cristo Rei style)."""
    s.add(rect(x - 16 * k, y - 40 * k, 32 * k, 40 * k, "#d9d2ee", 3)); s.add(circle(x, y - 56 * k, 20 * k, "#b8c4ea"))
    s.add(path(f"M{x - 18 * k} {y - 56 * k} q18 -10 36 0", stroke="#aab8de", width=2 * k))
    stone = s.grad((0, "#ffffff"), (1, "#cfc8e6"), x2=1, y2=0)
    s.add(path(f"M{x - 7 * k} {y - 74 * k} L{x + 7 * k} {y - 74 * k} L{x + 9 * k} {y - 140 * k} L{x - 9 * k} {y - 140 * k}Z", stone, stroke="#a9a0cc", width=1.2))
    s.add(path(f"M{x - 44 * k} {y - 128 * k} Q{x} {y - 136 * k} {x + 44 * k} {y - 128 * k} L{x + 44 * k} {y - 122 * k} Q{x} {y - 128 * k} {x - 44 * k} {y - 122 * k}Z", stone, stroke="#a9a0cc", width=1.2))
    s.add(circle(x, y - 148 * k, 9 * k, "#ffffff", 'stroke="#a9a0cc" stroke-width="1.2"'))

def obelisk(s, x, y, k=1.0, c="#efe9ff"):
    s.add(shadow(x, y + 2, 40 * k)); s.add(rect(x - 30 * k, y - 14 * k, 60 * k, 14 * k, "#ddd3f3", 3))
    s.add(poly([(x - 14 * k, y - 14 * k), (x + 14 * k, y - 14 * k), (x + 9 * k, y - 140 * k), (x, y - 156 * k), (x - 9 * k, y - 140 * k)], s.grad((0, "#ffffff"), (1, c))))

def market_stall(s, x, y, k=1.0, awning=("#ff8fa3", "#ffffff"), goods=("#ffb35c", "#7fd49a", "#ff6b6b")):
    s.add(shadow(x, y + 2, 60 * k)); s.add(rect(x - 52 * k, y - 34 * k, 104 * k, 34 * k, "#c79a6a", 4))
    for i in range(6): s.add(rect(x - 60 * k + i * 20 * k, y - 82 * k, 20 * k, 22 * k, awning[i % 2], 0))
    s.add(path(f"M{x - 60 * k} {y - 60 * k} " + " ".join(f"q5 8 10 0" for _ in range(12)), awning[0]))
    for px in (-52, 48): s.add(rect(x + px * k, y - 82 * k, 4 * k, 48 * k, "#8a6a4a"))
    for i in range(7): s.add(circle(x - 40 * k + i * 13 * k, y - 40 * k, 7 * k, goods[i % 3]))

def boat_outrigger(s, x, y, k=1.0, hull="#e07a5f", sail="#fdf3e7"):
    s.add(path(f"M{x - 70 * k} {y - 10 * k} Q{x} {y + 16 * k} {x + 70 * k} {y - 10 * k} L{x + 54 * k} {y + 4 * k} Q{x} {y + 22 * k} {x - 54 * k} {y + 4 * k}Z", hull))
    s.add(path(f"M{x - 30 * k} {y - 4 * k} L{x - 40 * k} {y + 26 * k} M{x + 30 * k} {y - 4 * k} L{x + 40 * k} {y + 26 * k}", stroke="#8a6a4a", width=3 * k))
    s.add(rect(x - 70 * k, y + 24 * k, 140 * k, 5 * k, "#a8714a", 2)); s.add(rect(x - 2 * k, y - 96 * k, 4 * k, 90 * k, "#8a6a4a"))
    s.add(path(f"M{x + 2 * k} {y - 92 * k} Q{x + 52 * k} {y - 60 * k} {x + 46 * k} {y - 14 * k} L{x + 2 * k} {y - 14 * k}Z", sail))

def caravel(s, x, y, k=1.0, hull=("#b5835a", "#7f5634")):
    s.add(path(f"M{x - 100 * k} {y - 40 * k} L{x + 100 * k} {y - 40 * k} Q{x + 92 * k} {y + 4 * k} {x + 60 * k} {y + 10 * k} L{x - 70 * k} {y + 10 * k} Q{x - 96 * k} {y} {x - 100 * k} {y - 40 * k}Z", s.grad((0, hull[0]), (1, hull[1]))))
    s.add(rect(x - 100 * k, y - 52 * k, 50 * k, 14 * k, hull[1], 3)); s.add(rect(x + 64 * k, y - 50 * k, 36 * k, 12 * k, hull[1], 3))
    for mx, h in ((-40, 150), (20, 170), (70, 120)):
        s.add(rect(x + mx * k - 2 * k, y - (h + 40) * k, 4 * k, h * k, "#6b4a2b"))
        s.add(path(f"M{x + mx * k} {y - (h + 30) * k} Q{x + (mx + 38) * k} {y - (h * 0.7 + 30) * k} {x + mx * k} {y - (h * 0.4 + 40) * k}Z", "#fbf5ea"))
        s.add(path(f"M{x + (mx + 8) * k} {y - (h * 0.75 + 30) * k} h12 M{x + (mx + 14) * k} {y - (h * 0.75 + 36) * k} v12", stroke="#d64045", width=3 * k))

def cargo_ship(s, x, y, k=1.0):
    s.add(path(f"M{x - 120 * k} {y - 30 * k} L{x + 120 * k} {y - 30 * k} L{x + 100 * k} {y + 6 * k} L{x - 110 * k} {y + 6 * k}Z", s.grad((0, "#4a6fd8"), (1, "#334fb0"))))
    colors = ["#ff8fa3", "#ffd36b", "#7fd49a", "#7fbfff", "#c9a7ff", "#ffb35c"]
    for row in range(2):
        for i in range(8): s.add(rect(x - 96 * k + i * 22 * k, y - 52 * k - row * 20 * k, 20 * k, 18 * k, colors[(i + row * 3) % 6], 2))
    s.add(rect(x + 84 * k, y - 76 * k, 26 * k, 46 * k, "#ffffff", 3)); s.add(rect(x + 88 * k, y - 70 * k, 18 * k, 6 * k, "#9fd3f5", 1))

def oil_platform(s, x, y, k=1.0):
    for lx in (-50, -18, 18, 50): s.add(rect(x + lx * k - 4 * k, y - 60 * k, 8 * k, 90 * k, "#9aa3b8"))
    s.add(path(f"M{x - 50 * k} {y - 30 * k} L{x + 50 * k} {y + 10 * k} M{x + 50 * k} {y - 30 * k} L{x - 50 * k} {y + 10 * k}", stroke="#b6bdd0", width=3 * k))
    s.add(rect(x - 70 * k, y - 76 * k, 140 * k, 18 * k, "#ffb35c", 3)); s.add(rect(x - 60 * k, y - 110 * k, 50 * k, 34 * k, "#ffffff", 3)); s.add(rect(x - 54 * k, y - 104 * k, 38 * k, 8 * k, "#9fd3f5", 1))
    s.add(path(f"M{x + 20 * k} {y - 76 * k} L{x + 34 * k} {y - 170 * k} L{x + 48 * k} {y - 76 * k}", stroke="#e0566b", width=4 * k)); s.add(path(f"M{x + 26 * k} {y - 120 * k} h16 M{x + 23 * k} {y - 98 * k} h22", stroke="#e0566b", width=3 * k))
    s.add(path(f"M{x + 34 * k} {y - 170 * k} q8 -16 -2 -28 q14 6 10 26", "#ff9f5a"))

def crane(s, x, y, k=1.0):
    s.add(rect(x - 6 * k, y - 160 * k, 12 * k, 160 * k, "#ffb35c")); s.add(rect(x - 70 * k, y - 160 * k, 160 * k, 10 * k, "#ffb35c", 2))
    s.add(path(f"M{x - 6 * k} {y - 150 * k} L{x - 60 * k} {y - 150 * k} M{x + 6 * k} {y - 150 * k} L{x + 84 * k} {y - 150 * k}", stroke="#e8902f", width=2))
    s.add(rect(x + 60 * k, y - 150 * k, 2 * k, 60 * k, "#5a5a6a")); s.add(rect(x + 50 * k, y - 92 * k, 22 * k, 16 * k, "#7fbfff", 2))

def coin(s, x, y, r, c1="#ffe08a", c2="#e9b949", mark="$"):
    s.add(circle(x, y + r * 0.12, r, "#b8892e")); s.add(circle(x, y, r, s.grad((0, c1), (1, c2)))); s.add(circle(x, y, r * 0.78, "none", f'stroke="#fff6cc" stroke-width="{r * 0.08:.1f}"'))
    if mark: s.add(f'<text x="{x:.1f}" y="{y + r * 0.34:.1f}" font-family="Nunito, sans-serif" font-weight="800" font-size="{r:.0f}" text-anchor="middle" fill="#b8892e">{mark}</text>')

def banknote(s, x, y, w=150, h=72, c1="#b9f0c8", c2="#7fd49a"):
    s.add(rect(x, y + 6, w, h, "#2a1d5c", 10, 'opacity="0.12"')); s.add(rect(x, y, w, h, s.grad((0, c1), (1, c2), x2=1, y2=1), 10))
    s.add(circle(x + w / 2, y + h / 2, h * 0.3, "none", 'stroke="#3fa66a" stroke-width="4"')); s.add(rect(x + 10, y + 10, w - 20, h - 20, "none", 8, 'stroke="#ffffff" stroke-width="2" opacity="0.6"'))

def book(s, x, y, w=110, h=80, c="#7c5cfc"):
    s.add(shadow(x + w / 2, y + h + 4, w * 0.55)); s.add(rect(x, y, w, h, s.grad((0, lighten_hex(c, 0.25)), (1, c)), 8)); s.add(rect(x + 8, y + 6, w - 22, h - 12, "#ffffff", 4, 'opacity="0.92"'))
    for i in range(4): s.add(rect(x + 16, y + 16 + i * 13, w - 40, 4, "#d9d1ff", 2))

def scroll_doc(s, x, y, w=150, h=110):
    s.add(shadow(x + w / 2, y + h + 6, w * 0.5)); s.add(rect(x, y, w, h, s.grad((0, "#fff8e8"), (1, "#f5e6c4")), 6))
    for cy in (y, y + h): s.add(ellipse(x + w / 2, cy, w / 2 + 8, 9, "#e9d2a0"))
    for i in range(5): s.add(rect(x + 20, y + 20 + i * 16, w - 40 - (i % 2) * 24, 4, "#d8c39a", 2))

def ballot_box(s, x, y, k=1.0):
    s.add(shadow(x, y + 4, 70 * k)); s.add(rect(x - 64 * k, y - 80 * k, 128 * k, 80 * k, s.grad((0, "#e9f2ff"), (1, "#bcd4ff")), 10))
    s.add(rect(x - 30 * k, y - 84 * k, 60 * k, 8 * k, "#4a6fd8", 3)); s.add(rect(x - 20 * k, y - 130 * k, 40 * k, 52 * k, "#ffffff", 4))
    s.add(path(f"M{x - 8 * k} {y - 108 * k} l6 6 l12 -14", stroke="#14b88c", width=4 * k)); s.add(rect(x - 40 * k, y - 44 * k, 80 * k, 14 * k, "#4a6fd8", 4, 'opacity="0.25"'))

def finger_ink(s, x, y, k=1.0):
    s.add(rect(x - 12 * k, y - 70 * k, 24 * k, 70 * k, "#c98b5e", 12)); s.add(rect(x - 12 * k, y - 70 * k, 24 * k, 22 * k, "#5b4bd6", 12))

def medal(s, x, y, k=1.0, c1="#ffe08a", c2="#e9b949", ribbon=("#7c5cfc", "#ec4899")):
    s.add(poly([(x - 30 * k, y - 120 * k), (x - 8 * k, y - 120 * k), (x + 6 * k, y - 50 * k), (x - 12 * k, y - 50 * k)], ribbon[0])); s.add(poly([(x + 30 * k, y - 120 * k), (x + 8 * k, y - 120 * k), (x - 6 * k, y - 50 * k), (x + 12 * k, y - 50 * k)], ribbon[1]))
    coin(s, x, y - 26 * k, 34 * k, c1, c2, mark="")
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36); rr = 18 * k if i % 2 == 0 else 8 * k; pts.append((x + math.cos(a) * rr, y - 26 * k + math.sin(a) * rr))
    s.add(poly(pts, "#fff6cc"))

def dove(s, x, y, k=1.0, c="#ffffff"):
    s.add(path(f"M{x - 40 * k} {y} Q{x - 10 * k} {y - 20 * k} {x + 20 * k} {y - 10 * k} Q{x + 34 * k} {y - 22 * k} {x + 44 * k} {y - 14 * k} L{x + 54 * k} {y - 10 * k} L{x + 42 * k} {y - 4 * k} Q{x + 30 * k} {y + 18 * k} {x - 4 * k} {y + 14 * k} L{x - 40 * k} {y + 20 * k} L{x - 28 * k} {y + 6 * k}Z", c))
    s.add(path(f"M{x - 6 * k} {y - 6 * k} Q{x - 30 * k} {y - 60 * k} {x + 10 * k} {y - 64 * k} Q{x + 10 * k} {y - 30 * k} {x + 14 * k} {y - 10 * k}Z", "#eef0ff"))
    s.add(path(f"M{x + 52 * k} {y - 10 * k} q10 4 16 -2", stroke="#4bb070", width=3 * k)); s.add(ellipse(x + 64 * k, y - 16 * k, 5 * k, 3 * k, "#7fd49a"))
    s.add(circle(x + 40 * k, y - 15 * k, 1.8 * k, "#1f1a3d"))

def candle(s, x, y, k=1.0, c="#fff4dc"):
    s.add(circle(x, y - 64 * k, 22 * k, s.radial((0, "#ffd36b", 0.6), (1, "#ffd36b", 0)))); s.add(rect(x - 9 * k, y - 50 * k, 18 * k, 50 * k, c, 4))
    s.add(path(f"M{x} {y - 74 * k} q8 12 0 22 q-8 -10 0 -22z", "#ffb347")); s.add(path(f"M{x} {y - 66 * k} q4 6 0 12 q-4 -6 0 -12z", "#fff2b8"))

def carnation(s, x, y, k=1.0, c="#e63950"):
    s.add(path(f"M{x} {y} Q{x - 6 * k} {y - 60 * k} {x} {y - 110 * k}", stroke="#4bb070", width=5 * k)); s.add(ellipse(x - 14 * k, y - 56 * k, 14 * k, 6 * k, "#5fc28a", f'transform="rotate(-30 {x - 14 * k} {y - 56 * k})"'))
    for i in range(9):
        a = math.radians(i * 40); s.add(circle(x + math.cos(a) * 14 * k, y - 122 * k + math.sin(a) * 10 * k, 13 * k, c if i % 2 else lighten_hex(c, 0.2)))
    s.add(circle(x, y - 124 * k, 12 * k, lighten_hex(c, 0.3)))

def scales(s, x, y, k=1.0, c="#e9b949"):
    s.add(rect(x - 3 * k, y - 140 * k, 6 * k, 140 * k, c)); s.add(rect(x - 40 * k, y - 6 * k, 80 * k, 8 * k, c, 3)); s.add(rect(x - 70 * k, y - 132 * k, 140 * k, 6 * k, c, 3))
    for side in (-1, 1):
        cx = x + side * 66 * k; s.add(path(f"M{cx} {y - 128 * k} L{cx - 22 * k} {y - 76 * k} M{cx} {y - 128 * k} L{cx + 22 * k} {y - 76 * k}", stroke=c, width=2 * k))
        s.add(path(f"M{cx - 28 * k} {y - 76 * k} Q{cx} {y - 52 * k} {cx + 28 * k} {y - 76 * k}Z", c))

def globe(s, x, y, r, sea_c=("#8fd0ff", "#4a9be8"), land="#7fd49a"):
    s.add(circle(x, y, r, s.grad((0, sea_c[0]), (1, sea_c[1]))))
    s.add(path(f"M{x - r * 0.6} {y - r * 0.4} q{r * 0.3} {-r * 0.3} {r * 0.6} {-r * 0.1} q{r * 0.1} {r * 0.3} {-r * 0.2} {r * 0.4} q{-r * 0.3} {r * 0.1} {-r * 0.4} {-r * 0.3}z", land))
    s.add(path(f"M{x + r * 0.1} {y + r * 0.1} q{r * 0.4} {-r * 0.2} {r * 0.6} {r * 0.1} q{-r * 0.1} {r * 0.4} {-r * 0.4} {r * 0.5} q{-r * 0.2} {-r * 0.3} {-r * 0.2} {-r * 0.6}z", land))
    s.add(circle(x, y, r, "none", f'stroke="#ffffff" stroke-width="2" opacity="0.5"')); s.add(ellipse(x - r * 0.35, y - r * 0.4, r * 0.3, r * 0.18, "#ffffff", 'opacity="0.35"'))

def drum(s, x, y, k=1.0, body="#b5835a"):
    s.add(shadow(x, y + 2, 36 * k)); s.add(rect(x - 30 * k, y - 70 * k, 60 * k, 70 * k, s.grad((0, lighten_hex(body, 0.2)), (1, body)), 10))
    s.add(ellipse(x, y - 70 * k, 30 * k, 10 * k, "#f4e4c8"))
    for i in range(5): s.add(path(f"M{x - 30 * k + i * 15 * k} {y - 64 * k} L{x - 22 * k + i * 15 * k} {y - 6 * k}", stroke="#6b4a2b", width=2 * k))

def tais_cloth(s, x, y, w, h, colors=("#7a1426", "#b52a2a", "#1f1a17", "#e8b33a", "#f4ead8")):
    s.add(rect(x, y, w, h, colors[0], 6)); stripe = h / 9
    for i in range(9):
        if i % 2: s.add(rect(x, y + i * stripe, w, stripe * 0.5, colors[1 + (i // 2) % 3]))
    for j in range(int(w // 28)):
        cx = x + 14 + j * 28; cy = y + h / 2
        s.add(poly([(cx, cy - h * 0.18), (cx + 10, cy), (cx, cy + h * 0.18), (cx - 10, cy)], colors[3])); s.add(poly([(cx, cy - h * 0.08), (cx + 4, cy), (cx, cy + h * 0.08), (cx - 4, cy)], colors[4]))
    for j in range(int(w // 10)): s.add(rect(x + j * 10 + 2, y + h, 3, 10, colors[3]))

def loom(s, x, y, k=1.0):
    s.add(rect(x - 90 * k, y - 4 * k, 180 * k, 8 * k, "#8a6a4a", 3)); s.add(rect(x - 90 * k, y - 120 * k, 180 * k, 8 * k, "#8a6a4a", 3))
    for i in range(30): s.add(rect(x - 86 * k + i * 6 * k, y - 112 * k, 2 * k, 108 * k, ["#b52a2a", "#1f1a17", "#e8b33a"][i % 3], 0, 'opacity="0.9"'))
    tais_cloth(s, x - 86 * k, y - 60 * k, 172 * k, 56 * k)

def belak(s, x, y, r, c1="#fff1c2", c2="#e2b951"):
    s.add(circle(x, y + r * 0.08, r, "#a88433")); s.add(circle(x, y, r, s.grad((0, c1), (1, c2)))); s.add(circle(x, y, r * 0.55, "none", f'stroke="#c99a35" stroke-width="{r * 0.06:.1f}"'))
    s.add(circle(x, y - r * 1.25, r * 0.12, "none", f'stroke="#c99a35" stroke-width="{r * 0.06:.1f}"'))

def calendar_page(s, x, y, w=150, h=150, top="#ec4899", mark=None):
    s.add(shadow(x + w / 2, y + h + 6, w * 0.55)); s.add(rect(x, y, w, h, "#ffffff", 16)); s.add(path(f"M{x} {y + 16} q0 -16 16 -16 h{w - 32} q16 0 16 16 v26 h{-w}z", top))
    for i in range(4):
        for j in range(5): s.add(rect(x + 14 + j * 26, y + 54 + i * 22, 18, 14, "#efeaff" if (i, j) != (1, 2) else (mark or "#7c5cfc"), 4))
    for px in (x + 34, x + w - 34): s.add(rect(px - 4, y - 10, 8, 22, "#4a3a8f", 4))

def firework(s, x, y, r, c):
    for i in range(12):
        a = math.radians(i * 30); s.add(path(f"M{x + math.cos(a) * r * 0.3:.1f} {y + math.sin(a) * r * 0.3:.1f} L{x + math.cos(a) * r:.1f} {y + math.sin(a) * r:.1f}", stroke=c, width=3))
        s.add(circle(x + math.cos(a) * r * 1.1, y + math.sin(a) * r * 1.1, 3, c))

def tent(s, x, y, k=1.0, c="#7fbfff"):
    s.add(shadow(x, y + 2, 50 * k)); s.add(poly([(x - 50 * k, y), (x, y - 60 * k), (x + 50 * k, y)], s.grad((0, lighten_hex(c, 0.25)), (1, c)))); s.add(poly([(x - 12 * k, y), (x, y - 40 * k), (x + 12 * k, y)], "#3d5a8a"))

def plane(s, x, y, k=1.0, c="#ffffff"):
    s.add(path(f"M{x - 70 * k} {y} Q{x - 60 * k} {y - 10 * k} {x + 50 * k} {y - 8 * k} Q{x + 70 * k} {y - 6 * k} {x + 74 * k} {y} Q{x + 70 * k} {y + 6 * k} {x + 50 * k} {y + 6 * k} L{x - 60 * k} {y + 6 * k}Z", c))
    s.add(poly([(x - 10 * k, y - 4 * k), (x + 20 * k, y - 4 * k), (x - 30 * k, y - 46 * k), (x - 44 * k, y - 46 * k)], lighten_hex("#9fb6ff", 0.2))); s.add(poly([(x - 10 * k, y + 4 * k), (x + 20 * k, y + 4 * k), (x - 30 * k, y + 40 * k), (x - 44 * k, y + 40 * k)], "#9fb6ff"))
    s.add(poly([(x - 60 * k, y - 4 * k), (x - 48 * k, y - 4 * k), (x - 66 * k, y - 26 * k), (x - 74 * k, y - 26 * k)], "#9fb6ff"))
    for i in range(5): s.add(circle(x + 4 * k + i * 10 * k, y - 2 * k, 2.2 * k, "#7fbfff"))

def un_helmet(s, x, y, k=1.0):
    s.add(path(f"M{x - 60 * k} {y} Q{x - 60 * k} {y - 70 * k} {x} {y - 74 * k} Q{x + 60 * k} {y - 70 * k} {x + 60 * k} {y}Z", s.grad((0, "#8cc8ff"), (1, "#4a9be8"))))
    s.add(rect(x - 70 * k, y - 6 * k, 140 * k, 12 * k, "#4a9be8", 6)); s.add(ellipse(x - 20 * k, y - 50 * k, 18 * k, 10 * k, "#ffffff", 'opacity="0.35"'))

def chart_bars(s, x, y, k=1.0, values=(0.3, 0.5, 0.45, 0.7, 0.9), colors=("#c9a7ff", "#ff8fb8", "#7fd49a", "#7fbfff", "#ffd36b")):
    for i, v in enumerate(values): s.add(rect(x + i * 34 * k, y - 120 * k * v, 24 * k, 120 * k * v, colors[i % len(colors)], 8))
    s.add(rect(x - 10 * k, y, (len(values) * 34 + 10) * k, 4 * k, "#4a3a8f", 2))

def road_scene(s, y):
    s.add(path(f"M{W * 0.42} {y} L{W * 0.58} {y} L{W * 0.85} {H} L{W * 0.15} {H}Z", s.grad((0, "#8e8aa6"), (1, "#5d5878"))))
    for i in range(4):
        t0 = 0.15 + i * 0.22; t1 = t0 + 0.1; y0 = y + (H - y) * t0; y1 = y + (H - y) * t1
        s.add(poly([(W / 2 - 2 - 8 * t0, y0), (W / 2 + 2 + 8 * t0, y0), (W / 2 + 2 + 8 * t1, y1), (W / 2 - 2 - 8 * t1, y1)], "#fff4c2"))

def power_lines(s, y):
    for x in (100, 330, 560):
        s.add(rect(x - 3, y - 150, 6, 150, "#7b7896")); s.add(rect(x - 30, y - 140, 60, 5, "#7b7896", 2)); s.add(rect(x - 22, y - 116, 44, 5, "#7b7896", 2))
    for dy in (-140, -116):
        s.add(path(f"M70 {y + dy} Q215 {y + dy + 30} 330 {y + dy} T590 {y + dy}", stroke="#5c5a78", width=1.5))

def map_outline(s, x0=40, y0=60, w=560, h=230, land=("#9fe0b7", "#57b98a"), sea=None, highlight=None, labels=False, posts=False):
    """Timor-Leste from the packaged map data (geoBoundaries/OSM), with the Indonesian half of Timor in grey."""
    data = json.loads((ROOT / "lafa/assets/timor/map/municipalities.json").read_text(encoding="utf-8"))
    lon0, lat0, lon1, lat1 = data["bbox"]
    sx = w / (lon1 - lon0); sy = h / (lat1 - lat0); scale = min(sx, sy)
    ox = x0 + (w - (lon1 - lon0) * scale) / 2; oy = y0 + (h - (lat1 - lat0) * scale) / 2
    P = lambda lon, lat: (ox + (lon - lon0) * scale, oy + (lat1 - lat) * scale)
    fill = s.grad((0, land[0]), (1, land[1]), x2=1, y2=1)
    for m in data["municipalities"]:
        color = fill if highlight is None or m["id"] != highlight else s.grad((0, "#ffb3d1"), (1, "#ec4899"))
        for poly_ in m["polygons"]:
            d = ""
            for ring in poly_:
                pts = [P(lon, lat) for lon, lat in ring]; d += "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in pts) + "Z "
            s.add(path(d, color, stroke="#ffffff", width=1.2, extra='fill-rule="evenodd"'))
    return P

def sparkle(s, x, y, r, c="#ffffff"):
    s.add(path(f"M{x} {y - r} Q{x + r * 0.15} {y - r * 0.15} {x + r} {y} Q{x + r * 0.15} {y + r * 0.15} {x} {y + r} Q{x - r * 0.15} {y + r * 0.15} {x - r} {y} Q{x - r * 0.15} {y - r * 0.15} {x} {y - r}Z", c))

# ------------------------------------------------------------------- scenes
SCENES = {}

def scene(*names):
    def wrap(fn):
        for n in names: SCENES[n] = fn
        return fn
    return wrap

@scene("tl-overview")
def s_overview(s):
    sky(s, "sea"); s.add(rect(0, 0, W, H, s.grad((0, "#bfe6ff"), (1, "#7fc8ee"))))
    map_outline(s, 30, 70, 580, 230); flag_shape(s, 520, 40, 80, pole=False); cloud(s, 120, 50, 0.8); cloud(s, 380, 40, 0.6)
    for lon, lat in ((125.57, -8.56),): pass

@scene("island-formation")
def s_island_formation(s):
    sky(s, "dawn"); sea(s, 190, "#8fd0f0", "#4f9fd8")
    s.add(path("M0 260 L250 230 L330 300 L0 360Z", s.grad((0, "#d8b98f"), (1, "#a8845c"))))   # Australian plate
    s.add(path("M640 250 L380 225 L330 300 L640 360Z", s.grad((0, "#c4a6e8"), (1, "#8f74c9"))))   # Banda arc plate
    s.add(path("M210 205 Q300 120 380 200 Q340 230 300 236 Q250 238 210 205Z", s.grad((0, "#9fe0b7"), (1, "#4fa678"))))
    for x in (230, 300, 360): s.add(path(f"M{x} 300 l0 -40", stroke="#ffffff", width=4, extra='opacity="0.7"'))
    s.add(path("M150 300 l60 -20 M500 300 l-60 -20", stroke="#ffffff", width=6, extra='opacity="0.8"')); s.add(poly([(212, 274), (196, 270), (205, 286)], "#ffffff")); s.add(poly([(438, 274), (454, 270), (445, 286)], "#ffffff"))
    sun(s, 540, 70, 26)

@scene("geology", "minerals")
def s_geology(s):
    sky(s, "paper")
    layers = [("#f1d6a8", "#e3bd84"), ("#e4b7a0", "#cf9a82"), ("#cbb6e6", "#a990d1"), ("#a9c8e8", "#7fa6d1"), ("#b9a28a", "#957d66")]
    for i, (a, b) in enumerate(layers):
        y = 120 + i * 48; s.add(path(f"M0 {y} Q160 {y - 18} 320 {y} T640 {y - 6} L640 {y + 52} Q480 {y + 40} 320 {y + 52} T0 {y + 50}Z", s.grad((0, a), (1, b))))
    s.add(path("M200 205 a26 26 0 1 1 1 0z", "none", stroke="#fff6e0", width=3)); s.add(path("M200 205 a16 16 0 1 1 1 0z", "none", stroke="#fff6e0", width=3))
    s.add(path("M430 260 q10 -30 30 -10 q14 -26 30 0", stroke="#fff6e0", width=3))
    for x, c in ((470, "#ffffff"), (510, "#d9f2ff"), (540, "#ffe0ef")): s.add(poly([(x, 100), (x + 18, 70), (x + 34, 100), (x + 18, 118)], c, 'opacity="0.95"'))

@scene("mountain")
def s_mountain(s):
    sky(s, "day"); sun(s, 520, 80); cloud(s, 140, 70); cloud(s, 400, 100, 0.7)
    mountain(s, -40, 300, 360, 200, "#b4a4ef", "#8a76d8"); mountain(s, 220, 300, 460, 240, "#9db8f0", "#6d8ed8", snow=False); hills(s, 290, 30, "#a8e3b6", "#5fbf86", 4)
    tree(s, 90, 330, 0.8); tree(s, 560, 335, 0.9)

@scene("mountain-ramelau", "trekking")
def s_ramelau(s):
    sky(s, "sunset"); sun(s, 120, 200, 40, "#ffd08a")
    mountain(s, 80, 330, 520, 260, "#c7a7e8", "#8a6cc8", peak_shift=10); cloud(s, 200, 230, 1.2, opacity=0.8); cloud(s, 470, 250, 1.0, opacity=0.8)
    px = 80 + 260 + 10; s.add(rect(px - 3, 70 - 6, 6, 18, "#ffffff")); s.add(circle(px, 60, 6, "#ffffff"))
    hills(s, 320, 26, "#9fd7b2", "#4f9f78", 7, 3); person(s, 520, 352, 0.6, shirt="#ec4899", hat="cap")

@scene("river")
def s_river(s):
    sky(s, "mint"); hills(s, 170, 40, "#b8e6c4", "#79c99a", 11); mountain(s, 360, 180, 300, 110, "#a8c4ee", "#7c9ad8")
    s.add(path("M300 180 Q260 240 330 270 Q420 310 360 360 L470 360 Q520 300 420 260 Q350 230 330 180Z", s.grad((0, "#9fe3ff"), (1, "#4aa8e0"))))
    tree(s, 150, 300); tree(s, 560, 290, 0.9); bush(s, 250, 330, 0.8); flower(s, 120, 330)

@scene("lake")
def s_lake(s):
    sky(s, "day"); hills(s, 200, 30, "#b8e6c4", "#79c99a", 4); s.add(ellipse(320, 280, 300, 70, s.grad((0, "#a8e6ff"), (1, "#5ab3e6"))))
    for x in (90, 130, 520, 560): s.add(path(f"M{x} 300 q-4 -40 4 -70 M{x + 8} 300 q4 -30 -2 -56", stroke="#5fae6f", width=3))
    bird(s, 300, 140, 0.7, body="#ffffff"); cloud(s, 470, 80); sun(s, 130, 80, 24)

@scene("sea-coast", "seas")
def s_coast(s):
    sky(s, "sea"); sun(s, 520, 70); sea(s, 200); s.add(path("M0 180 Q120 150 230 200 Q300 240 360 360 L0 360Z", s.grad((0, "#bfe6a5"), (1, "#7fc56f"))))
    s.add(path("M0 220 Q120 200 220 240 Q280 270 320 360 L300 360 Q250 280 0 250Z", "#fbe6bd")); palm(s, 120, 250, 0.9); boat_outrigger(s, 470, 250, 0.8)

@scene("beach")
def s_beach(s):
    sky(s, "day"); sun(s, 540, 70); cloud(s, 160, 60); sea(s, 175); sand(s, 255); palm(s, 520, 300, 1.0); palm(s, 590, 290, 0.8)
    s.add(path("M150 270 Q190 230 230 270Z", "#ff8fb8")); s.add(rect(188, 250, 3, 50, "#8a6a4a")); s.add(ellipse(260, 300, 40, 8, "#ffffff", 'opacity="0.6"'))

@scene("coral-reef", "diving")
def s_reef(s):
    s.add(rect(0, 0, W, H, s.grad((0, "#7fd6f5"), (1, "#2f7fc4"))))
    for i in range(6): s.add(path(f"M{60 + i * 110} 0 L{20 + i * 110} 360", stroke="#ffffff", width=26, extra='opacity="0.06"'))
    s.add(path("M0 300 Q160 270 320 300 T640 290 L640 360 L0 360Z", "#f5dcb0"))
    for x, c in ((80, "#ff8fa3"), (170, "#ffb35c"), (420, "#c9a7ff"), (540, "#ff8fa3"), (300, "#7fd49a")): coral(s, x, 305, 1.1, c)
    fish(s, 230, 160, 1.2); fish(s, 400, 120, 1.0, "#ffd36b"); fish(s, 470, 200, 0.9, "#7fbfff"); fish(s, 160, 230, 0.8, "#ff8fa3")
    if True:
        person_x = 520; s.add(ellipse(person_x, 120, 34, 12, "#3b3a5c")); s.add(circle(person_x + 32, 116, 10, "#c98b5e")); s.add(rect(person_x + 24, 108, 18, 8, "#7fd6f5", 3))
        for i in range(4): s.add(circle(person_x + 48 + i * 6, 96 - i * 16, 3 + i, "#ffffff", 'opacity="0.6"'))

@scene("whale")
def s_whale(s):
    s.add(rect(0, 0, W, H, s.grad((0, "#bfe8ff"), (0.35, "#7cc8ee"), (1, "#2f6fb8"))))
    whale(s, 320, 210, 1.2); whale(s, 520, 300, 0.6, "#9cc0f5", "#6a96e0")
    for i in range(6): s.add(circle(170 + i * 14, 150 - i * 10, 3 + i * 0.6, "#ffffff", 'opacity="0.5"'))
    s.add(path("M0 50 " + " ".join("q20 -6 40 0 t40 0" for _ in range(17)), stroke="#ffffff", width=2, extra='opacity="0.6"'))

@scene("climate")
def s_climate(s):
    s.add(rect(0, 0, W / 2, H, s.grad((0, "#ffe2b8"), (1, "#ffd0e1")))); s.add(rect(W / 2, 0, W / 2, H, s.grad((0, "#b8c8f5"), (1, "#c8e6ff"))))
    sun(s, 160, 130, 46); hills(s, 290, 20, "#e8d39a", "#cdb06a", 2)
    cloud(s, 470, 110, 1.6, "#f4f6ff"); cloud(s, 520, 140, 1.2, "#e6ebff")
    for i in range(14): x = 400 + (i * 37) % 200; y = 170 + (i * 53) % 110; s.add(path(f"M{x} {y} l-6 14", stroke="#4a8ad8", width=3))
    s.add(path("M320 0 L320 360", stroke="#ffffff", width=3, extra='opacity="0.7"'))

@scene("flood")
def s_flood(s):
    sky(s, "lilac"); cloud(s, 200, 70, 1.6, "#d9d9f0"); cloud(s, 450, 60, 1.4, "#cfd3ee")
    for i in range(30): x = (i * 61) % 640; y = 100 + (i * 37) % 120; s.add(path(f"M{x} {y} l-6 14", stroke="#7f9be0", width=2.5))
    house(s, 180, 300, 1.0); house(s, 420, 310, 0.8, roof="#7c5cfc")
    s.add(path("M0 270 " + " ".join("q30 -10 60 0 t60 0" for _ in range(6)) + " L640 360 L0 360Z", s.grad((0, "#9ec7e8", 0.9), (1, "#6a9cc8"))))

@scene("earthquake")
def s_quake(s):
    sky(s, "paper"); ground(s, 230, "#e8d3b0", "#cdb08a")
    s.add(path("M0 250 L180 260 L230 300 L300 250 L360 320 L420 260 L640 270", stroke="#7a5a3a", width=6)); house(s, 150, 240, 0.9); house(s, 480, 250, 0.9, roof="#4a9be8")
    for x in (260, 320, 380): s.add(path(f"M{x} 140 q10 -10 0 -20 q-10 -10 0 -20", stroke="#a08ae8", width=3))

@scene("forest")
def s_forest(s):
    sky(s, "mint"); hills(s, 230, 30, "#b8e6c4", "#79c99a", 12)
    for i, x in enumerate(range(30, 660, 70)): tree(s, x, 320 - (i % 2) * 20, 1.1 - (i % 3) * 0.12)
    bird(s, 470, 110, 0.6); sun(s, 560, 60, 20)

@scene("mangrove")
def s_mangrove(s):
    sky(s, "day"); sea(s, 230, "#9fd8e8", "#5aaed0")
    for x in (100, 230, 380, 520):
        for r in (-30, -12, 10, 28): s.add(path(f"M{x} 220 Q{x + r} 240 {x + r * 1.4} 270", stroke="#7a5a3a", width=4))
        s.add(circle(x, 190, 40, s.grad((0, "#8ddca6"), (1, "#3fa66a")))); s.add(circle(x - 26, 205, 26, "#5fc28a")); s.add(circle(x + 26, 205, 26, "#4bb070"))
    fish(s, 300, 300, 0.8, "#ffd36b")

@scene("sandalwood")
def s_sandalwood(s):
    sky(s, "paper"); ground(s, 290, "#e8d3b0", "#d0b089"); tree(s, 320, 300, 1.8, "#8fd1a0", "#4f9f72", "#8a5a32")
    for i in range(5): s.add(path(f"M{430 + i * 24} {180 - i * 10} q10 -14 0 -28 q-10 -14 0 -28", stroke="#d8a7ff", width=3, extra='opacity="0.7"'))
    for x in (110, 170): s.add(rect(x - 40, 300, 80, 20, "#c7905c", 10)); s.add(circle(x + 40, 310, 10, "#e8c08a"))

@scene("crocodile", "legend")
def s_croc(s):
    sky(s, "sea"); sea(s, 210); s.add(path("M380 220 Q480 170 640 190 L640 240 Q520 236 380 220Z", s.grad((0, "#9fe0b7"), (1, "#57b98a"))))
    crocodile(s, 220, 250, 1.1); sun(s, 540, 70); cloud(s, 140, 70)

@scene("birds")
def s_birds(s):
    sky(s, "mint"); tree(s, 150, 360, 2.4, "#9fe0b7", "#4fa678"); bird(s, 360, 180, 1.4); bird(s, 470, 120, 0.9, body="#ffffff", crest="#ffb35c")
    s.add(path("M250 300 L560 260", stroke="#8a6a4a", width=8)); bird(s, 470, 255, 1.0, body="#7fd49a", crest="#ff6b6b", wing="#5fc28a")

@scene("animals")
def s_animals(s):
    sky(s, "day"); ground(s, 250); buffalo(s, 180, 320, 1.0); horse(s, 440, 320, 1.1); tree(s, 590, 300, 0.9); bird(s, 300, 110, 0.6)

@scene("national-park")
def s_park(s):
    sky(s, "day"); sea(s, 230); s.add(path("M0 210 Q200 160 400 210 Q470 230 520 360 L0 360Z", s.grad((0, "#9fe0b7"), (1, "#4fa678"))))
    tree(s, 90, 290); tree(s, 180, 270, 1.2); tree(s, 290, 300); s.add(rect(360, 250, 8, 70, "#8a6a4a")); s.add(rect(330, 236, 70, 34, "#f4e4c8", 6))
    s.add(path("M345 253 h40 M345 262 h28", stroke="#8a6a4a", width=3)); s.add(path("M520 200 Q560 180 600 200 Q580 215 520 200Z", "#9fe0b7"))

@scene("environment")
def s_environment(s):
    sky(s, "mint"); globe(s, 320, 210, 110)
    s.add(path("M320 120 q-4 -30 10 -50", stroke="#4bb070", width=6)); s.add(ellipse(300, 82, 22, 11, "#7fd49a", 'transform="rotate(-30 300 82)"')); s.add(ellipse(346, 72, 22, 11, "#5fc28a", 'transform="rotate(20 346 72)"'))
    for x, y in ((120, 90), (520, 100), (540, 300)): sparkle(s, x, y, 14, "#ffffff")

@scene("cave", "prehistory")
def s_cave(s):
    s.add(rect(0, 0, W, H, s.grad((0, "#5b4a8a"), (1, "#3a2d63"))))
    s.add(path("M0 0 L640 0 L640 360 L0 360Z M160 360 Q160 120 320 110 Q480 120 480 360Z", s.grad((0, "#a58e74"), (1, "#7a6550")), extra='fill-rule="evenodd"'))
    s.add(path("M160 360 Q160 120 320 110 Q480 120 480 360Z", s.grad((0, "#ffd6a8"), (1, "#ffb1c8"))))
    for x, y in ((70, 120), (110, 200), (540, 150)): s.add(path(f"M{x} {y} c-6 -16 6 -30 14 -18 c6 -12 22 0 10 14 c10 6 0 22 -12 14 c-2 12 -18 10 -12 -10z", "#d8664e", extra='opacity="0.85"'))
    s.add(path("M560 250 l20 -40 l20 40 M570 236 h20", stroke="#d8664e", width=4)); fish(s, 80, 290, 1.0, "#d8664e", "#d8664e")
    s.add(path("M300 300 q20 -30 40 0", stroke="#ffffff", width=3, extra='opacity="0.8"'))

@scene("austronesian-boat")
def s_austro(s):
    sky(s, "sunset"); sun(s, 500, 120, 40, "#ffd08a"); sea(s, 220, "#8ac6e8", "#4f8fcf"); boat_outrigger(s, 280, 240, 1.4); boat_outrigger(s, 520, 230, 0.6, "#c86b4f")
    bird(s, 160, 100, 0.5)

@scene("kingdom")
def s_kingdom(s):
    sky(s, "paper"); hills(s, 260, 40, "#cfe8b8", "#93c77a", 5); uma_lulik(s, 200, 320, 0.95); person(s, 420, 330, 1.2, shirt="#b52a2a", hat="headdress", skirt="#7a1426")
    belak(s, 420, 268, 10)

@scene("trade-ships")
def s_trade(s):
    sky(s, "dawn"); sea(s, 210); s.add(path("M380 300 Q300 230 220 236 Q140 240 60 300Z", "#e8c08a", extra='opacity="0"'))
    s.add(path("M160 230 L300 230 L280 262 L180 262Z", "#b5835a")); s.add(rect(228, 120, 4, 112, "#6b4a2b")); s.add(path("M232 128 L300 150 L300 214 L232 214Z", "#e8573f", extra='opacity="0.9"'))
    for i in range(5): s.add(path(f"M236 {140 + i * 15} L298 {150 + i * 13}", stroke="#b8402d", width=2))
    for x in (420, 470, 520): s.add(rect(x, 300, 60, 16, "#c7905c", 8))
    sun(s, 560, 70, 24)

@scene("caravel")
def s_caravel(s):
    sky(s, "day"); cloud(s, 120, 70); cloud(s, 460, 60, 0.7); sea(s, 250); caravel(s, 320, 255, 1.1)

@scene("fort")
def s_fort(s):
    sky(s, "day"); ground(s, 290, "#d9e8b8", "#b5d08a"); fort(s, 330, 300, 1.2); flag_shape(s, 420, 120, 50, pole=False, wave=True); cloud(s, 120, 80)

@scene("colonial-town")
def s_colonial(s):
    sky(s, "paper"); ground(s, 300, "#efe0c4", "#d9c39b")
    for i, x in enumerate((90, 230, 390, 540)): columns_building(s, x, 310, 0.6, wall=["#fff6e6", "#ffeedd", "#fff1f5", "#f4f0ff"][i], roof=["#e9b6a0", "#c9b6ff", "#ffb3cf", "#b6d6ff"][i], n=4, w=200, h=90)
    palm(s, 320, 330, 0.7)

@scene("treaty")
def s_treaty(s):
    sky(s, "lilac"); scroll_doc(s, 220, 110, 200, 150); s.add(circle(380, 230, 22, "#d8463c")); s.add(circle(380, 230, 12, "#b02c24"))
    s.add(path("M150 300 L230 230", stroke="#3b2d63", width=6)); s.add(path("M230 230 l8 -10 l4 14z", "#3b2d63"))

@scene("revolt")
def s_revolt(s):
    sky(s, "sunset"); hills(s, 260, 50, "#c8a8e8", "#8e72c8", 6); mountain(s, 360, 280, 300, 150, "#b79ce8", "#8064c4")
    for i, x in enumerate((140, 220, 300)): person(s, x, 330, 1.0, shirt=["#7a1426", "#1f1a17", "#b52a2a"][i], skirt="#e8b33a", hat="headdress" if i == 1 else None)

@scene("ww2")
def s_ww2(s):
    sky(s, "lilac"); cloud(s, 140, 80, 1.2, "#e9e4ff"); plane(s, 380, 110, 1.0, "#d9dbe8"); sea(s, 240, "#9db4d8", "#6c86b8")
    s.add(path("M120 250 L260 250 L240 280 L140 280Z", "#7d86a8")); s.add(rect(180, 214, 30, 36, "#9aa1c0", 3)); s.add(rect(192, 190, 6, 26, "#7d86a8"))

@scene("carnation")
def s_carnation(s):
    sky(s, "dawn"); carnation(s, 280, 340, 1.4); carnation(s, 380, 330, 1.1, "#ff5b7a"); sparkle(s, 140, 100, 16); sparkle(s, 520, 120, 12)

@scene("proclamation", "independence")
def s_independence(s):
    sky(s, "night"); stars(s, 60, 7)
    firework(s, 140, 90, 40, "#ffd36b"); firework(s, 520, 80, 46, "#ff8fb8"); firework(s, 340, 60, 30, "#7fd6f5")
    s.add(rect(318, 90, 5, 230, "#d8cfe8")); flag_shape(s, 323, 100, 150)
    crowd(s, 120, 360, 8, 0.75, 4)

@scene("resistance")
def s_resistance(s):
    sky(s, "dusk" if False else "sunset"); mountain(s, -60, 320, 380, 230, "#9a7cc8", "#6a52a8"); mountain(s, 240, 320, 460, 260, "#8a6cc0", "#5a4598")
    hills(s, 300, 30, "#5d8a6a", "#3f6a50", 9); s.add(circle(520, 110, 40, s.radial((0, "#ffe9b8"), (1, "#ffd08a"))))
    s.add(rect(178, 150, 4, 120, "#3a2d4a")); flag_shape(s, 182, 150, 56)

@scene("memorial")
def s_memorial(s):
    sky(s, "night"); stars(s, 40, 3); candle(s, 230, 320, 1.2); candle(s, 320, 330, 1.5); candle(s, 410, 320, 1.1)
    for x in (170, 470): flower(s, x, 330, 1.4, "#ffffff", "#ffd36b")

@scene("nobel", "veterans", "heroes")
def s_nobel(s):
    sky(s, "lilac"); medal(s, 320, 320, 1.6)
    for x, y in ((150, 110), (500, 90), (520, 260), (130, 250)): sparkle(s, x, y, 14, "#ffd36b")

@scene("ballot")
def s_ballot(s):
    sky(s, "day"); ballot_box(s, 260, 320, 1.4); finger_ink(s, 470, 330, 1.4); cloud(s, 520, 80); flag_shape(s, 70, 60, 70)

@scene("un-peace")
def s_un(s):
    sky(s, "sea"); un_helmet(s, 220, 300, 1.4); dove(s, 440, 160, 1.4)
    for x, y in ((520, 280), (110, 90)): sparkle(s, x, y, 12)

@scene("constitution")
def s_constitution(s):
    sky(s, "paper"); book(s, 200, 110, 240, 170, "#7c5cfc"); flag_shape(s, 250, 150, 90, wave=False); scales(s, 520, 320, 0.7)

@scene("camp")
def s_camp(s):
    sky(s, "dawn"); ground(s, 270, "#e8dcc0", "#cdb898"); tent(s, 160, 320, 1.2); tent(s, 320, 330, 1.4, "#ffb3cf"); tent(s, 490, 320, 1.2, "#b6e8c8"); cloud(s, 480, 80)

@scene("reconciliation", "diplomacy")
def s_reconcile(s):
    sky(s, "mint"); globe(s, 320, 170, 90)
    s.add(path("M140 300 Q220 250 300 270 L330 290 L300 312 Q220 320 140 330Z", "#c98b5e")); s.add(path("M500 300 Q420 250 340 270 L310 290 L340 312 Q420 320 500 330Z", "#a96f45"))
    s.add(rect(90, 290, 60, 50, "#7c5cfc", 10)); s.add(rect(490, 290, 60, 50, "#14b88c", 10)); dove(s, 520, 90, 0.7)

@scene("maritime")
def s_maritime(s):
    sky(s, "sea"); sea(s, 120, "#8fd0f0", "#3f8fd0"); s.add(path("M0 240 Q160 220 320 250 T640 230", stroke="#ffffff", width=4, extra='stroke-dasharray="14 10"'))
    oil_platform(s, 470, 230, 0.8); boat_outrigger(s, 150, 190, 0.6); map_pin(s, 300, 200, "#ec4899")

def map_pin(s, x, y, c="#ec4899"):
    s.add(path(f"M{x} {y} q-24 -30 -24 -48 a24 24 0 1 1 48 0 q0 18 -24 48z", c)); s.add(circle(x, y - 48, 9, "#ffffff"))

@scene("asean")
def s_asean(s):
    sky(s, "lilac"); s.add(circle(320, 180, 110, s.grad((0, "#ffe9a8"), (1, "#ffc94a"))))
    for i in range(11):
        a = math.radians(-90 + i * 360 / 11); x = 320 + math.cos(a) * 150; y = 180 + math.sin(a) * 120
        s.add(circle(x, y, 18, ["#7c5cfc", "#ec4899", "#14b88c", "#3b93ec", "#f77f3a", "#e11d48"][i % 6])); s.add(circle(x, y, 7, "#ffffff", 'opacity="0.5"'))
    for i in range(10): s.add(path(f"M{290 + i * 6} 240 q-8 -60 {6 - i} -110", stroke="#c98a12", width=3))
    flag_shape(s, 296, 150, 48)

@scene("church-crowd", "procession")
def s_church_crowd(s):
    sky(s, "day"); ground(s, 300, "#e8f0d8", "#cfe0b0"); church(s, 320, 300, 0.95); crowd(s, 60, 360, 4, 0.7, 5); crowd(s, 450, 360, 4, 0.7, 9); cloud(s, 120, 70)

@scene("parliament")
def s_parliament(s):
    sky(s, "dawn"); ground(s, 300, "#e8f0d8", "#cfe0b0"); columns_building(s, 320, 310, 1.1, roof="#c9b6ff", n=8, w=300, h=110, flag=True); tree(s, 70, 320); tree(s, 580, 320)

@scene("palace")
def s_palace(s):
    sky(s, "day"); ground(s, 300, "#e8f0d8", "#cfe0b0"); columns_building(s, 320, 310, 1.1, wall="#ffffff", roof="#ffd36b", n=6, w=280, h=120, dome=False, flag=True)
    for x in (70, 580): palm(s, x, 320, 0.8)

@scene("government-palace")
def s_govpalace(s):
    sky(s, "sea"); ground(s, 300, "#e8f0d8", "#cfe0b0"); columns_building(s, 320, 310, 1.15, wall="#fffaf2", roof="#e9b6a0", n=10, w=380, h=96, flag=True); palm(s, 50, 330, 0.7)

@scene("justice")
def s_justice(s):
    sky(s, "lilac"); scales(s, 320, 320, 1.6); book(s, 80, 240, 120, 80, "#14b88c")

@scene("police")
def s_police(s):
    sky(s, "sea"); s.add(path("M320 60 L420 100 Q420 230 320 300 Q220 230 220 100Z", s.grad((0, "#6fa8ff"), (1, "#3a6fd8"))))
    s.add(path("M320 100 l12 26 28 3 -21 19 6 28 -25 -14 -25 14 6 -28 -21 -19 28 -3z", "#ffd36b")); s.add(rect(250, 250, 140, 14, "#ffffff", 7, 'opacity="0.6"'))

@scene("military")
def s_military(s):
    sky(s, "mint"); hills(s, 280, 30, "#9fc8a0", "#5f9a6a", 13); s.add(path("M320 70 L410 110 Q410 220 320 290 Q230 220 230 110Z", s.grad((0, "#8fb58a"), (1, "#557a50"))))
    sparkle(s, 320, 170, 40, "#ffd36b"); flag_shape(s, 470, 70, 80)

@scene("village-council")
def s_village(s):
    sky(s, "paper"); ground(s, 280); tree(s, 320, 300, 2.0, "#9fe0b7", "#4fa678")
    for i, x in enumerate((180, 250, 390, 460)): person(s, x, 330, 0.8, shirt=["#7c5cfc", "#b52a2a", "#14b88c", "#f2a516"][i], skin=SKIN[i % 4])
    uma_lulik(s, 560, 330, 0.5)

@scene("flag")
def s_flag(s):
    sky(s, "sea"); s.add(rect(150, 40, 8, 300, "#cfc6e8", 4)); flag_shape(s, 158, 50, 330)
    cloud(s, 560, 300, 0.9); cloud(s, 90, 290, 0.6)

@scene("emblem")
def s_emblem(s):
    sky(s, "lilac"); s.add(circle(320, 180, 120, s.grad((0, "#fff3c4"), (1, "#f2c94c")))); s.add(circle(320, 180, 100, "#ffffff", 'opacity="0.35"'))
    flag_shape(s, 250, 140, 140, wave=False); s.add(circle(320, 180, 120, "none", 'stroke="#e9b949" stroke-width="6"'))
    for i in range(16):
        a = math.radians(i * 22.5); s.add(circle(320 + math.cos(a) * 132, 180 + math.sin(a) * 132, 6, "#e9b949"))

@scene("anthem", "music")
def s_anthem(s):
    sky(s, "dawn"); drum(s, 160, 320, 1.4); flag_shape(s, 380, 60, 140)
    for i, (x, y) in enumerate(((300, 220), (360, 180), (430, 230), (500, 190))):
        s.add(circle(x, y, 12, ["#7c5cfc", "#ec4899", "#14b88c", "#f2a516"][i])); s.add(rect(x + 9, y - 54, 4, 56, ["#7c5cfc", "#ec4899", "#14b88c", "#f2a516"][i]))

@scene("currency", "money")
def s_currency(s):
    sky(s, "mint"); banknote(s, 150, 110, 220, 110); banknote(s, 190, 150, 220, 110, "#d6f7e0", "#9fe0b7")
    coin(s, 470, 240, 52, mark="¢"); coin(s, 540, 170, 36, mark="¢"); coin(s, 420, 150, 30, mark="$")

@scene("languages")
def s_languages(s):
    sky(s, "lilac")
    for i, (x, y, c) in enumerate(((180, 120, "#7c5cfc"), (420, 100, "#ec4899"), (300, 230, "#14b88c"), (500, 240, "#f2a516"), (120, 250, "#3b93ec"))):
        s.add(rect(x - 70, y - 40, 140, 80, c, 24)); s.add(poly([(x - 20, y + 38), (x - 34, y + 64), (x + 4, y + 38)], c))
        for j in range(3): s.add(rect(x - 46, y - 18 + j * 16, 92 - j * 20, 6, "#ffffff", 3, 'opacity="0.85"'))

@scene("dili-city", "city", "town")
def s_dili(s):
    sky(s, "sunset"); sea(s, 260, "#8ac6e8", "#4f8fcf"); s.add(path("M420 260 Q500 140 640 120 L640 260Z", s.grad((0, "#a8d8a0"), (1, "#5f9f6a"))))
    statue_cristo(s, 590, 140, 0.45)
    for i, (x, w, h, c) in enumerate(((40, 60, 80, "#fff1f5"), (110, 70, 120, "#f4f0ff"), (190, 50, 70, "#fff6e6"), (250, 80, 100, "#eaf6ff"), (340, 60, 140, "#fff1f5"))):
        s.add(rect(x, 260 - h, w, h, c, 6))
        for r in range(int(h // 24)): s.add(rect(x + 10, 260 - h + 12 + r * 24, w - 20, 8, "#c9b6ff", 3, 'opacity="0.7"'))
    palm(s, 60, 290, 0.6); palm(s, 400, 290, 0.6)

@scene("tais")
def s_tais(s):
    sky(s, "paper"); tais_cloth(s, 60, 60, 520, 120); loom(s, 320, 330, 1.2)

@scene("uma-lulik")
def s_uma(s):
    sky(s, "dawn"); hills(s, 280, 30, "#cfe8b8", "#93c77a", 8); uma_lulik(s, 320, 330, 1.25); tree(s, 110, 320); tree(s, 540, 320, 0.9)

@scene("dance", "festival")
def s_dance(s):
    sky(s, "sunset"); ground(s, 300, "#f0d9b8", "#e0bf92")
    for i in range(6):
        a = math.radians(i * 60); x = 320 + math.cos(a) * 170; y = 330 + math.sin(a) * 20
        person(s, x, y, 0.9, shirt=["#b52a2a", "#1f1a17", "#7a1426"][i % 3], skirt=["#e8b33a", "#b52a2a", "#f4ead8"][i % 3], arms_up=i % 2 == 0)
    sparkle(s, 320, 100, 18, "#ffd36b")

@scene("likurai")
def s_likurai(s):
    sky(s, "dawn"); ground(s, 300, "#f0d9b8", "#e0bf92"); person(s, 240, 330, 1.3, shirt="#b52a2a", skirt="#1f1a17", arms_up=True); drum(s, 420, 330, 1.2)
    s.add(path("M210 210 Q160 160 200 120", stroke="#e8b33a", width=10))

@scene("food")
def s_food(s):
    sky(s, "paper"); s.add(ellipse(320, 290, 240, 50, "#2a1d5c", 'opacity="0.1"')); s.add(ellipse(320, 260, 220, 60, s.grad((0, "#ffffff"), (1, "#efe8ff"))))
    s.add(ellipse(230, 250, 70, 28, "#fff8e6")); s.add(ellipse(400, 250, 80, 30, "#ffd8a8"))
    for i in range(8): s.add(circle(200 + i * 9, 246 - (i % 2) * 6, 6, "#fff3c4"))
    fish(s, 400, 246, 1.6, "#f4a35c", "#ffd36b"); s.add(path("M150 120 q20 -30 0 -60 M180 120 q20 -30 0 -60", stroke="#c9b6ff", width=4, extra='opacity="0.6"'))
    s.add(rect(470, 160, 70, 80, "#a8714a", 14)); s.add(ellipse(505, 162, 35, 10, "#6b4a2b"))

@scene("crafts")
def s_crafts(s):
    sky(s, "paper"); s.add(path("M160 320 Q110 260 150 200 L250 200 Q290 260 240 320Z", s.grad((0, "#e8a07a"), (1, "#c26a42")))); s.add(ellipse(200, 200, 50, 12, "#a8583a"))
    s.add(path("M330 320 L320 220 L460 220 L450 320Z", s.grad((0, "#f1d38a"), (1, "#d2a54a"))))
    for i in range(6): s.add(path(f"M{322 + i * 2} {230 + i * 15} L{458 - i * 2} {230 + i * 15}", stroke="#b8862e", width=3))
    belak(s, 540, 200, 40)

@scene("adornment")
def s_adornment(s):
    sky(s, "lilac"); belak(s, 320, 210, 80)
    s.add(path("M200 120 L230 60 L260 110 L290 50 L320 110 L350 50 L380 110 L410 60 L440 120Z", s.grad((0, "#fff1c2"), (1, "#e2b951"))))
    for i in range(14): s.add(circle(170 + i * 22, 312 + math.sin(i) * 6, 7, ["#e8573f", "#ffd36b", "#ffffff"][i % 3]))

@scene("church")
def s_church(s):
    sky(s, "day"); ground(s, 300, "#e8f0d8", "#cfe0b0"); church(s, 320, 310, 1.05); tree(s, 90, 320); palm(s, 560, 330, 0.8); cloud(s, 140, 70)

@scene("mosque", "eid")
def s_mosque(s):
    sky(s, "night"); stars(s, 50, 11); moon(s, 520, 80, 30); ground(s, 300, "#5a6b9a", "#46557d"); mosque(s, 300, 310, 1.15)
    for x in (120, 460): s.add(rect(x - 12, 230, 24, 34, "#ffd36b", 8)); s.add(rect(x - 2, 210, 4, 22, "#d8cfe8"))

@scene("football", "sports")
def s_football(s):
    sky(s, "day"); ground(s, 240, "#9fe0a8", "#5fbf72"); s.add(rect(80, 250, 480, 4, "#ffffff", 2)); s.add(path("M320 250 a60 18 0 1 1 1 0", stroke="#ffffff", width=3))
    s.add(rect(520, 170, 6, 90, "#ffffff")); s.add(rect(600, 170, 6, 90, "#ffffff")); s.add(rect(520, 170, 86, 6, "#ffffff"))
    person(s, 260, 330, 1.0, shirt="#dc241f"); s.add(circle(330, 316, 16, "#ffffff")); s.add(circle(330, 316, 6, "#1f1a3d"))

@scene("literature")
def s_literature(s):
    sky(s, "paper"); book(s, 140, 150, 160, 120, "#ec4899"); book(s, 330, 120, 160, 140, "#7c5cfc")
    s.add(path("M520 90 L560 250 L548 254 Z", "#3b2d63")); s.add(path("M520 90 q20 -10 30 20", stroke="#ffd36b", width=4)); sparkle(s, 110, 90, 12, "#ffd36b")

@scene("people", "population")
def s_people(s):
    sky(s, "dawn"); ground(s, 300, "#f0e6fa", "#ddd0f3"); crowd(s, 90, 340, 6, 1.0, 21); crowd(s, 150, 300, 5, 0.75, 8)

@scene("oil-gas")
def s_oil(s):
    sky(s, "sunset"); sea(s, 240, "#8ac6e8", "#4f8fcf"); oil_platform(s, 330, 250, 1.3); cargo_ship(s, 130, 300, 0.45)

@scene("fund", "bank")
def s_fund(s):
    sky(s, "mint"); s.add(ellipse(300, 230, 130, 90, s.grad((0, "#ffc4dd"), (1, "#f58bbf")))); s.add(circle(390, 190, 26, "#f58bbf")); s.add(rect(250, 150, 60, 10, "#c95a92", 5))
    for x in (230, 340): s.add(rect(x, 300, 22, 30, "#f58bbf", 8))
    s.add(path("M470 120 q-30 40 -30 62 a30 30 0 0 0 60 0 q0 -22 -30 -62z", "#4a3a8f")); coin(s, 300, 90, 30, mark="$")

@scene("exports", "port")
def s_exports(s):
    sky(s, "day"); sea(s, 230); cargo_ship(s, 300, 260, 1.1); crane(s, 560, 260, 0.9); cloud(s, 120, 70)

@scene("imports")
def s_imports(s):
    sky(s, "dawn"); plane(s, 220, 110, 1.2); ground(s, 290, "#e0e4f0", "#c4cadf")
    colors = ["#ff8fa3", "#ffd36b", "#7fd49a", "#7fbfff", "#c9a7ff"]
    for i in range(5): s.add(rect(330 + (i % 3) * 64, 250 - (i // 3) * 46, 60, 42, colors[i], 6))

@scene("coffee")
def s_coffee(s):
    sky(s, "paper"); hills(s, 290, 40, "#bfe0a8", "#7fbf6f", 14)
    for x in (120, 200, 280): tree(s, x, 300, 0.9, "#7fd49a", "#3f9a52")
    for x, y in ((110, 240), (130, 256), (190, 236), (210, 250), (270, 244)): s.add(circle(x, y, 6, "#d93a3a"))
    s.add(rect(400, 170, 120, 120, "#ffffff", 30)); s.add(rect(410, 180, 100, 30, "#7a4e2a", 14)); s.add(path("M520 200 q40 0 40 30 q0 30 -40 30", stroke="#ffffff", width=12))
    for x in (430, 460, 490): s.add(path(f"M{x} 150 q10 -16 0 -32", stroke="#c9b6ff", width=4, extra='opacity="0.6"'))

@scene("rice", "crops", "plan")
def s_rice(s):
    sky(s, "day"); hills(s, 200, 30, "#cfe8b8", "#93c77a", 17)
    for i in range(5): s.add(path(f"M0 {220 + i * 28} Q320 {204 + i * 28} 640 {220 + i * 28} L640 {246 + i * 28} Q320 {230 + i * 28} 0 {246 + i * 28}Z", ["#a8e6a0", "#8fd88a", "#bfe8a8", "#9fe09a", "#86d080"][i]))
    person(s, 420, 300, 1.0, shirt="#3b93ec", hat="straw"); sun(s, 540, 70)

@scene("maize")
def s_maize(s):
    sky(s, "paper"); ground(s, 300, "#e8d3b0", "#d0b089")
    for x in range(80, 600, 70):
        s.add(path(f"M{x} 300 L{x} 150", stroke="#5fae6f", width=6)); s.add(path(f"M{x} 200 q-30 -20 -40 10 M{x} 240 q30 -20 40 10", stroke="#7fc77f", width=6))
        s.add(ellipse(x + 10, 190, 9, 22, "#ffd36b"))

@scene("livestock")
def s_livestock(s):
    sky(s, "mint"); ground(s, 250); buffalo(s, 220, 320, 1.1); s.add(ellipse(470, 300, 40, 24, "#ffc4c4")); s.add(circle(505, 290, 18, "#ffc4c4")); s.add(ellipse(518, 294, 8, 6, "#f5a0a0"))
    for x in (440, 480): s.add(rect(x, 312, 8, 16, "#ffb0b0", 3))

@scene("fishing")
def s_fishing(s):
    sky(s, "dawn"); sun(s, 520, 120, 40, "#ffd08a"); sea(s, 220); boat_outrigger(s, 300, 230, 1.2)
    s.add(path("M380 200 Q440 260 420 320", stroke="#ffffff", width=2, extra='opacity="0.8"')); fish(s, 430, 320, 1.0, "#ffd36b")

@scene("tourism")
def s_tourism(s):
    sky(s, "day"); sea(s, 200); sand(s, 260); palm(s, 520, 300); s.add(rect(160, 220, 90, 70, "#ff8fb8", 14)); s.add(rect(186, 206, 38, 18, "none", 8, 'stroke="#c95a92" stroke-width="6"'))
    s.add(path("M330 280 Q370 240 410 280Z", "#ffd36b")); s.add(rect(368, 260, 3, 40, "#8a6a4a")); sun(s, 560, 70, 24)

@scene("road")
def s_road(s):
    sky(s, "day"); hills(s, 200, 50, "#bfe6a5", "#7fc56f", 19); road_scene(s, 190); tree(s, 90, 320); tree(s, 560, 320); cloud(s, 470, 70)

@scene("electricity")
def s_electricity(s):
    sky(s, "dawn"); ground(s, 300); power_lines(s, 300); s.add(path("M320 60 L280 150 L318 150 L296 230 L366 120 L326 120 L350 60Z", "#ffd36b")); sun(s, 560, 70, 20)

@scene("workers")
def s_workers(s):
    sky(s, "sea"); plane(s, 420, 90, 1.0); crowd(s, 120, 340, 4, 0.95, 31); s.add(path("M380 300 q60 -80 160 -150", stroke="#ffffff", width=4, extra='stroke-dasharray="10 10"'))

@scene("school", "youth")
def s_school(s):
    sky(s, "day"); ground(s, 300); columns_building(s, 320, 300, 0.9, wall="#fff6e6", roof="#ff8fb8", n=5, w=260, h=90, flag=True)
    person(s, 140, 340, 0.8, shirt="#ffffff", holding="book"); person(s, 520, 340, 0.8, shirt="#ffffff", skirt="#3b5bd6", holding="book")

@scene("university")
def s_university(s):
    sky(s, "lilac"); s.add(poly([(320, 60), (520, 140), (320, 220), (120, 140)], s.grad((0, "#5b4bd6"), (1, "#3b2d8f")))); s.add(path("M200 170 L200 250 Q320 310 440 250 L440 170 L320 220Z", "#4a3cb0"))
    s.add(path("M520 140 L520 240", stroke="#ffd36b", width=5)); s.add(circle(520, 248, 10, "#ffd36b")); sparkle(s, 100, 90, 14, "#ffd36b"); sparkle(s, 560, 80, 10, "#ffd36b")

@scene("health")
def s_health(s):
    sky(s, "mint"); s.add(rect(200, 110, 240, 190, "#ffffff", 22)); s.add(rect(290, 140, 60, 130, "#f25f6f", 12)); s.add(rect(255, 175, 130, 60, "#f25f6f", 12))
    s.add(path("M480 220 q30 -30 60 0 q-30 40 -30 40 q0 0 -30 -40z", "#ff8fb8"))

@scene("women")
def s_women(s):
    sky(s, "dawn"); ground(s, 300, "#f6e6f6", "#e6d0ee")
    for i, x in enumerate((200, 320, 440)): person(s, x, 340, 1.1, shirt=["#ec4899", "#7c5cfc", "#14b88c"][i], skirt=["#7a1426", "#1f1a17", "#e8b33a"][i], hair="#2b1d14", arms_up=i == 1)

@scene("media")
def s_media(s):
    sky(s, "lilac"); s.add(rect(150, 120, 200, 140, "#3b2d63", 18)); s.add(rect(165, 135, 170, 100, s.grad((0, "#9fd3ff"), (1, "#c9a7ff")), 10)); flag_shape(s, 210, 160, 80, wave=False)
    s.add(rect(400, 150, 120, 110, "#ffffff", 14)); s.add(circle(460, 205, 34, "none", 'stroke="#7c5cfc" stroke-width="6"')); s.add(rect(455, 120, 4, 32, "#7c5cfc"))

@scene("island")
def s_island(s):
    sky(s, "day"); sea(s, 200); s.add(path("M140 240 Q240 140 380 160 Q500 180 520 240 Q330 270 140 240Z", s.grad((0, "#9fe0b7"), (1, "#4fa678")))); s.add(path("M140 240 Q330 270 520 240 Q330 262 140 246Z", "#fbe6bd"))
    palm(s, 300, 230, 0.6); mountain(s, 330, 200, 160, 80, "#9fd8b0", "#5fae7a"); sun(s, 540, 70, 24); cloud(s, 150, 70)

@scene("viewpoint")
def s_viewpoint(s):
    sky(s, "sunset"); sun(s, 470, 190, 40, "#ffd08a"); sea(s, 230, "#a4b8ee", "#6f88d8"); s.add(path("M0 260 Q160 200 300 260 L300 360 L0 360Z", s.grad((0, "#9fd7b2"), (1, "#4f9f78"))))
    person(s, 180, 250, 0.8, shirt="#ec4899", arms_up=True)

@scene("statue")
def s_statue(s):
    sky(s, "sunset"); sea(s, 250, "#8ac6e8", "#4f8fcf"); s.add(path("M150 360 Q320 170 490 360Z", s.grad((0, "#a8d8a0"), (1, "#5f9f6a")))); statue_cristo(s, 320, 270, 1.25); cloud(s, 110, 80); cloud(s, 540, 70, 0.8)

@scene("museum")
def s_museum(s):
    sky(s, "paper"); ground(s, 300, "#ece4f6", "#d8cdee"); columns_building(s, 320, 310, 1.05, wall="#fffaf2", roof="#c9b6ff", n=6, w=300, h=110)
    for x in (240, 400): s.add(rect(x - 16, 236, 32, 50, "#ffd36b", 6, 'opacity="0.7"'))

@scene("monument")
def s_monument(s):
    sky(s, "dawn"); ground(s, 300); obelisk(s, 320, 310, 1.3); flower(s, 240, 320, 1.4); flower(s, 400, 320, 1.4, "#ffd36b", "#ff8fb8")

@scene("hot-spring")
def s_hot(s):
    sky(s, "lilac"); hills(s, 220, 40, "#c8e6c8", "#8fc8a0", 23); s.add(ellipse(320, 290, 220, 50, s.grad((0, "#9fe8e0"), (1, "#4fc0b8"))))
    for x in (240, 320, 400): s.add(path(f"M{x} 270 q12 -20 0 -40 q-12 -20 0 -40", stroke="#ffffff", width=5, extra='opacity="0.7"'))
    for x in (120, 520): s.add(circle(x, 300, 26, "#b8a8c8"))

@scene("waterfall")
def s_waterfall(s):
    sky(s, "mint"); s.add(path("M180 0 L460 0 L460 360 L180 360Z", s.grad((0, "#7f9a8a"), (1, "#5f7a6a")))); s.add(path("M290 40 Q300 200 270 320 L370 320 Q340 200 350 40Z", s.grad((0, "#e4f7ff"), (1, "#8fd6f5"))))
    s.add(ellipse(320, 320, 120, 26, "#8fd6f5")); tree(s, 140, 340, 1.2); tree(s, 520, 340, 1.1)

@scene("market")
def s_market(s):
    sky(s, "day"); ground(s, 300, "#f0e6d8", "#e0cfb8"); market_stall(s, 180, 320, 1.2); market_stall(s, 450, 320, 1.1, ("#7fbfff", "#ffffff")); person(s, 320, 340, 0.8, shirt="#14b88c")

@scene("village")
def s_village2(s):
    sky(s, "dawn"); hills(s, 260, 30, "#cfe8b8", "#93c77a", 29); uma_lulik(s, 170, 320, 0.7); uma_lulik(s, 330, 330, 0.85); house(s, 500, 320, 1.0); tree(s, 600, 330, 0.8)

@scene("garden")
def s_garden(s):
    sky(s, "mint"); ground(s, 280)
    for i, x in enumerate(range(60, 620, 60)): flower(s, x, 300 + (i % 2) * 14, 1.4, ["#ff8fb8", "#ffd36b", "#c9a7ff", "#7fbfff"][i % 4]); s.add(path(f"M{x} {310 + (i % 2) * 14} v40", stroke="#5fae6f", width=3))
    tree(s, 320, 260, 1.4)

@scene("calendar")
def s_calendar(s):
    sky(s, "lilac"); calendar_page(s, 245, 90, 150, 170); flag_shape(s, 440, 90, 80); sparkle(s, 160, 110, 14, "#ffd36b")

@scene("new-year")
def s_newyear(s):
    sky(s, "night"); stars(s, 60, 5); firework(s, 200, 120, 50, "#ffd36b"); firework(s, 440, 100, 60, "#ff8fb8"); firework(s, 320, 200, 40, "#7fd6f5"); dili_skyline(s)

def dili_skyline(s):
    for i, (x, w, h) in enumerate(((20, 70, 60), (100, 60, 90), (170, 80, 70), (260, 60, 110), (330, 90, 80), (430, 70, 100), (510, 110, 70))):
        s.add(rect(x, 360 - h, w, h, "#2f2a5a", 4))
        for r in range(int(h // 24)): s.add(rect(x + 10, 360 - h + 10 + r * 24, w - 20, 6, "#ffd36b", 2, 'opacity="0.5"'))

@scene("labour")
def s_labour(s):
    sky(s, "dawn"); ground(s, 300); person(s, 200, 330, 1.1, shirt="#3b93ec", hat="helmet"); person(s, 330, 330, 1.1, shirt="#14b88c", hat="straw"); person(s, 460, 330, 1.1, shirt="#f2a516", holding="book")

@scene("christmas")
def s_christmas(s):
    sky(s, "night"); stars(s, 50, 13); sparkle(s, 320, 60, 22, "#ffd36b")
    s.add(poly([(320, 80), (420, 300), (220, 300)], s.grad((0, "#7fd49a"), (1, "#2f9a63")))); s.add(rect(306, 300, 28, 30, "#8a5a32", 4))
    for x, y, c in ((300, 180, "#ff6b6b"), (350, 220, "#ffd36b"), (280, 260, "#7fbfff"), (370, 270, "#ff8fb8")): s.add(circle(x, y, 8, c))

@scene("easter")
def s_easter(s):
    sky(s, "dawn"); sun(s, 320, 220, 60, "#ffe0a0"); hills(s, 280, 30, "#cfe8b8", "#93c77a", 31); s.add(rect(312, 120, 16, 150, "#f4f0fb")); s.add(rect(282, 160, 76, 16, "#f4f0fb"))
    for x in (180, 460): flower(s, x, 300, 1.6, "#ffffff", "#ffd36b")

@scene("map")
def s_map(s):
    s.add(rect(0, 0, W, H, s.grad((0, "#c8ecff"), (1, "#86c8ee")))); map_outline(s, 20, 40, 600, 280)

for _key, _fn in list(SCENES.items()):
    pass

def manifest_entry(key):
    return {"key": key, "file": f"{key}.svg", "licence": "CC BY-SA 4.0", "author": "Lafa contributors (tools/make-illustrations.py)",
            "note": "Timor-Leste outline: geoBoundaries / © OpenStreetMap contributors (ODbL 1.0)" if key in ("tl-overview", "map") else ""}

def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    keys = argv or sorted(SCENES)
    for key in keys:
        if key not in SCENES: print("unknown:", key); continue
        s = Scene(); SCENES[key](s); (OUT / f"{key}.svg").write_text(s.svg(), encoding="utf-8")
    if not argv:
        for old in OUT.glob("*.svg"):
            if old.stem not in SCENES: old.unlink()
        (OUT / "manifest.json").write_text(json.dumps({"generator": "tools/make-illustrations.py", "licence": "CC BY-SA 4.0",
            "illustrations": [manifest_entry(k) for k in sorted(SCENES)]}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(keys)} illustrations in {OUT}")

if __name__ == "__main__":
    main(sys.argv[1:])
