#!/usr/bin/env python3
"""Generate Lafa's illustrations into lafa/assets/illustrations/ (+ manifest.json).

    python3 tools/make-illustrations.py

Flat vector scenes in Lafa's own style (no photos, no third-party art): one
picture per encyclopedia category and diagrams for articles and interactive
modules. All are original work for Lafa, licensed CC BY-SA 4.0 like the
lessons. Scenes are 640×360 (16:9) unless noted; diagrams carry their labels in
the article text, not in the picture, so one picture serves every language.
"""
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "lafa/assets/illustrations"
W, H = 640, 360

# ------------------------------------------------------------------ helpers
def svg(body, w=W, h=H, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<defs>{defs}</defs>{body}</svg>\n')

def lin(id_, *stops, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'

def rad(id_, *stops, cx=0.5, cy=0.5, r=0.5):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'

def rect(x, y, w, h, fill, rx=0, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {extra}/>'

def circle(cx, cy, r, fill, extra=""):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" {extra}/>'

def ellipse(cx, cy, rx, ry, fill, extra=""):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>'

def path(d, fill="none", stroke=None, width=0, extra=""):
    st = f' stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"' if stroke else ""
    return f'<path d="{d}" fill="{fill}"{st} {extra}/>'

def poly(points, fill, extra=""):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" fill="{fill}" {extra}/>'

def hills(y, amp, color, seed, n=5, w=W, h=H):
    rnd = random.Random(seed); pts = [(0, y)]
    step = w / n
    d = f"M0 {h} L0 {y} "
    for i in range(n):
        x1 = i * step + step / 2; y1 = y - amp * (0.5 + rnd.random() * 0.8); x2 = (i + 1) * step; y2 = y + amp * (rnd.random() - 0.5) * 0.6
        d += f"Q{x1:.0f} {y1:.0f} {x2:.0f} {y2:.0f} "
    return path(d + f"L{w} {h} Z", color)

def cloud(x, y, s=1.0, color="#ffffff", opacity=0.9):
    return (f'<g opacity="{opacity}" fill="{color}">' + ellipse(x, y, 34 * s, 14 * s, color) + circle(x - 14 * s, y - 8 * s, 14 * s, color)
            + circle(x + 10 * s, y - 12 * s, 18 * s, color) + "</g>")

def stars(n, seed, w=W, h=H * 0.6, color="#ffffff"):
    rnd = random.Random(seed)
    return "".join(circle(rnd.uniform(0, w), rnd.uniform(0, h), rnd.choice([0.8, 1.1, 1.5]), color, f'opacity="{rnd.uniform(0.4, 1):.2f}"') for _ in range(n))

def palm(x, y, s=1.0, trunk="#7a5230", leaf="#2f8f4e"):
    out = path(f"M{x} {y} Q{x + 6 * s} {y - 50 * s} {x + 2 * s} {y - 100 * s}", stroke=trunk, width=7 * s)
    tx, ty = x + 2 * s, y - 100 * s
    for a in (-160, -120, -60, -20, 200):
        r = math.radians(a); ex, ey = tx + math.cos(r) * 52 * s, ty + math.sin(r) * 26 * s + 18 * s
        cx, cy = tx + math.cos(r) * 30 * s, ty - 18 * s
        out += path(f"M{tx:.0f} {ty:.0f} Q{cx:.0f} {cy:.0f} {ex:.0f} {ey:.0f} Q{(cx + ex) / 2:.0f} {cy + 14 * s:.0f} {tx:.0f} {ty:.0f}Z", leaf)
    return out

def fern(x, y, s=1.0, color="#3d8c40", flip=1):
    out = ""
    for i in range(7):
        a = math.radians(-90 + flip * (i - 3) * 18); l = (60 - abs(i - 3) * 8) * s
        ex, ey = x + math.cos(a) * l, y + math.sin(a) * l
        out += path(f"M{x} {y} Q{x + (ex - x) * 0.4 - 6 * s:.0f} {y + (ey - y) * 0.6:.0f} {ex:.0f} {ey:.0f} Q{x + (ex - x) * 0.6 + 6 * s:.0f} {y + (ey - y) * 0.4:.0f} {x} {y}Z", color)
    return out

def tree(x, y, s=1.0, trunk="#6b4a2b", crown="#3f9a52", crown2="#2f7f42"):
    return (rect(x - 4 * s, y - 40 * s, 8 * s, 40 * s, trunk, 2) + circle(x, y - 58 * s, 26 * s, crown2)
            + circle(x - 14 * s, y - 50 * s, 18 * s, crown) + circle(x + 12 * s, y - 64 * s, 18 * s, crown))

def frame(body, defs="", w=W, h=H):
    # A soft vignette so cards look calm and the title area stays readable.
    vign = rad("vig", (0, "#000000"), (1, "#000000"), r=0.75).replace('stop-color="#000000"/></radialGradient>', 'stop-color="#000000" stop-opacity="0.18"/></radialGradient>').replace('<stop offset="0" stop-color="#000000"/>', '<stop offset="0" stop-color="#000000" stop-opacity="0"/>')
    return svg(body + rect(0, 0, w, h, "url(#vig)"), w, h, defs + vign)

# ------------------------------------------------------------- Tyrannosaurus
# A side view facing left, used on the dinosaur card and in the hotspot module.
TREX = ("M70 132 C78 112 104 100 134 100 C160 100 186 104 204 116 C226 130 246 138 270 140 "
        "C320 144 372 148 420 152 C470 156 530 166 600 190 C540 186 480 184 430 186 "
        "C410 196 396 210 384 222 C376 252 372 280 376 306 L394 318 C396 324 388 328 378 326 L350 324 "
        "C346 300 344 276 344 252 C336 248 326 246 316 246 C312 268 306 290 302 306 L318 318 C320 324 312 328 302 326 L276 324 "
        "C274 300 276 272 280 246 C262 238 248 226 238 210 C232 216 226 222 222 230 L230 238 C228 242 222 242 218 238 L210 230 "
        "C214 220 220 210 226 200 C214 188 204 176 196 166 C184 170 170 172 154 172 L128 168 C114 168 96 166 84 160 "
        "C74 154 68 144 70 132 Z")
TREX_JAW = "M84 152 C100 158 122 162 150 164 C170 165 186 162 196 158"
TREX_EYE = (152, 120)

def trex(fill="#7a6a3a", shade="#5e522c", belly="#b9a46a", stroke="#3f361d"):
    teeth = "".join(path(f"M{x} 152 l3 7 l3 -7", "#fffaf0") for x in range(92, 150, 9))
    stripes = "".join(path(f"M{x} {y} q10 6 22 2", stroke=shade, width=4, extra='opacity="0.7"') for x, y in [(250, 146), (300, 150), (350, 154), (400, 158), (452, 164), (500, 172)])
    return (path(TREX, fill, stroke, 3) + path("M216 150 C250 166 296 176 340 178 C380 180 410 180 430 186 C400 200 390 210 384 222 C350 230 300 232 262 222 C240 210 224 186 216 150Z", belly, extra='opacity="0.55"')
            + stripes + teeth + path(TREX_JAW, stroke=stroke, width=3) + circle(*TREX_EYE, 6, "#fff8e0") + circle(TREX_EYE[0] - 1, TREX_EYE[1], 3, "#1d1d1d")
            + path("M136 112 q14 -6 28 0", stroke=stroke, width=3) + circle(80, 128, 2.5, stroke))

def sauropod(x, y, s=1.0, fill="#6f8f5a", stroke="#3e5532"):
    d = (f"M{x} {y} c{20*s} {-6*s} {40*s} {-30*s} {48*s} {-80*s} c{4*s} {-20*s} {14*s} {-30*s} {30*s} {-28*s} c{10*s} {2*s} {12*s} {10*s} {4*s} {14*s} "
         f"c{-10*s} {4*s} {-16*s} {12*s} {-18*s} {30*s} c{-4*s} {28*s} {10*s} {50*s} {40*s} {58*s} c{40*s} {10*s} {90*s} {6*s} {130*s} {20*s} "
         f"c{-30*s} {6*s} {-60*s} {6*s} {-80*s} {8*s} l{0} {30*s} l{-16*s} 0 l{-2*s} {-26*s} c{-14*s} {2*s} {-30*s} 0 {-42*s} {-2*s} l{-2*s} {28*s} l{-16*s} 0 l{0} {-36*s} c{-10*s} {-6*s} {-20*s} {-6*s} {-26*s} {-10*s} Z")
    return path(d, fill, stroke, 2.5)

# ------------------------------------------------------------------ Timor map
# Schematic outline (not an official map) from approximate coastal points.
def lonlat(points, x0=60, y0=40, w=520, h=230, lon=(124.0, 127.4), lat=(-8.1, -9.55)):
    return [(x0 + (a - lon[0]) / (lon[1] - lon[0]) * w, y0 + (b - lat[0]) / (lat[1] - lat[0]) * h) for a, b in points]

TIMOR = [(125.07, -8.96), (125.13, -8.80), (125.22, -8.65), (125.33, -8.58), (125.47, -8.56), (125.57, -8.55), (125.72, -8.54),
         (125.90, -8.52), (126.03, -8.50), (126.20, -8.46), (126.45, -8.46), (126.62, -8.44), (126.85, -8.41), (127.05, -8.37),
         (127.22, -8.38), (127.31, -8.43), (127.20, -8.52), (127.02, -8.62), (126.83, -8.73), (126.60, -8.83), (126.37, -8.93),
         (126.10, -9.02), (125.85, -9.10), (125.62, -9.18), (125.40, -9.27), (125.20, -9.37), (125.08, -9.44), (125.12, -9.27),
         (125.05, -9.15), (125.12, -9.05)]
OECUSSE = [(124.05, -9.20), (124.25, -9.18), (124.45, -9.20), (124.48, -9.32), (124.38, -9.45), (124.20, -9.48), (124.08, -9.38)]
ATAURO = [(125.57, -8.13), (125.62, -8.16), (125.64, -8.26), (125.62, -8.33), (125.57, -8.30), (125.55, -8.20)]
WEST = [(124.0, -9.12), (124.05, -9.20), (124.08, -9.38), (124.20, -9.48), (124.38, -9.45), (124.48, -9.32), (124.45, -9.20),
        (124.7, -9.08), (125.07, -8.96), (125.12, -9.05), (125.05, -9.15), (125.12, -9.27), (125.08, -9.44), (124.6, -9.55), (124.0, -9.55)]

def timor_map(sea="#9fd3e8", land="#7cbf6a", coast="#3e7a4a", west="#d8e6cf"):
    body = rect(0, 0, W, H, sea)
    body += "".join(path(f"M0 {y} q40 -6 80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0", stroke="#ffffff", width=1.4, extra='opacity="0.35"') for y in range(30, 360, 42))
    body += poly(lonlat(WEST), west, f'stroke="#9fb592" stroke-width="1.5"')
    for shape in (TIMOR, OECUSSE, ATAURO): body += poly(lonlat(shape), land, f'stroke="{coast}" stroke-width="2.5" stroke-linejoin="round"')
    jaco = lonlat([(127.34, -8.43)])[0]; body += circle(jaco[0], jaco[1], 3.5, land, f'stroke="{coast}" stroke-width="1.5"')
    rm = lonlat([(125.50, -8.91)])[0]
    body += poly([(rm[0] - 14, rm[1] + 8), (rm[0], rm[1] - 12), (rm[0] + 14, rm[1] + 8)], "#5a8f4c", 'stroke="#2f5e33" stroke-width="1.5"')
    dili = lonlat([(125.57, -8.555)])[0]; body += circle(dili[0], dili[1] + 2, 5, "#c0392b", 'stroke="#ffffff" stroke-width="2"')
    # compass rose
    cx, cy = 585, 300
    body += circle(cx, cy, 26, "#ffffff", 'opacity="0.8"') + poly([(cx, cy - 22), (cx + 6, cy), (cx, cy + 22), (cx - 6, cy)], "#3b5b6b") + poly([(cx, cy - 22), (cx + 6, cy), (cx - 6, cy)], "#c0392b")
    return body

def flag_tl(x, y, w):
    h = w / 2
    star = []
    cx, cy, r = x + w * 0.11, y + h / 2, h * 0.14
    for i in range(10):
        a = math.radians(-90 + i * 36 - 30); rr = r if i % 2 == 0 else r * 0.4
        star.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return (rect(x, y, w, h, "#dc241f") + poly([(x, y), (x + w / 2, y + h / 2), (x, y + h)], "#ffc726")
            + poly([(x, y), (x + w / 3, y + h / 2), (x, y + h)], "#000000") + poly(star, "#ffffff"))

def tais_band(x, y, w, h, colours=("#7a1426", "#b52a2a", "#1f1a17", "#e8b33a", "#f4ead8")):
    """A woven band with ikat-like diamonds (decorative, not a specific regional motif)."""
    out = rect(x, y, w, h, colours[0])
    stripe = h / 9
    out += rect(x, y + stripe, w, stripe * 0.6, colours[2]) + rect(x, y + h - stripe * 1.6, w, stripe * 0.6, colours[2])
    out += rect(x, y + stripe * 0.2, w, stripe * 0.35, colours[3]) + rect(x, y + h - stripe * 0.55, w, stripe * 0.35, colours[3])
    size = h * 0.42; cy = y + h / 2; n = int(w // (size * 1.3)) + 1
    for i in range(n):
        cx = x + i * size * 1.3 + size * 0.65
        out += poly([(cx, cy - size / 2), (cx + size / 2, cy), (cx, cy + size / 2), (cx - size / 2, cy)], colours[1], f'stroke="{colours[4]}" stroke-width="2"')
        out += poly([(cx, cy - size / 5), (cx + size / 5, cy), (cx, cy + size / 5), (cx - size / 5, cy)], colours[4])
    return out

# --------------------------------------------------------------------- scenes
def scene_earth():
    defs = lin("sky", (0, "#0b1d3a"), (1, "#1e3a6a")) + rad("glow", (0, "#3d7bd9"), (1, "#0b1d3a"), r=0.6)
    b = rect(0, 0, W, H, "url(#sky)") + stars(70, 1) + circle(320, 200, 175, "url(#glow)", 'opacity="0.5"')
    cx, cy = 320, 205
    # Earth with a quarter cut away to show the layers.
    b += circle(cx, cy, 140, "#2e7bc4") + path(f"M{cx-120} {cy-40} q40 -50 90 -40 q30 10 20 50 q-30 40 -70 30 q-30 -10 -40 -40Z", "#4caf50")
    b += path(f"M{cx-60} {cy+60} q30 -20 60 0 q20 30 -10 50 q-40 10 -50 -20Z", "#4caf50")
    for r, c in [(140, "#8d6e4a"), (122, "#e2733a"), (84, "#f2a93b"), (40, "#ffd75e")]:
        b += path(f"M{cx} {cy} L{cx} {cy - r} A{r} {r} 0 0 1 {cx + r} {cy} Z", c)
    b += path(f"M{cx} {cy-140} L{cx} {cy} L{cx+140} {cy}", stroke="#ffffff", width=2, extra='opacity="0.6"')
    b += circle(540, 80, 26, "#d9d9d9") + circle(532, 72, 6, "#bdbdbd") + circle(548, 88, 4, "#bdbdbd")
    return frame(b, defs)

def scene_dinosaurs():
    defs = lin("sky", (0, "#f6c98a"), (0.6, "#fbe6bf"), (1, "#e9f1d6"))
    b = rect(0, 0, W, H, "url(#sky)") + circle(520, 80, 38, "#ffe7a3", 'opacity="0.9"')
    b += path("M380 250 L450 120 L470 130 L490 115 L560 250Z", "#8a6a5a") + path("M450 120 q15 -40 40 -5", "#c9b8b0", extra='opacity="0.7"')
    b += cloud(470, 70, 1.2, "#fff6e6") + hills(260, 40, "#9bbf72", 3) + hills(290, 30, "#7aa85a", 4)
    b += sauropod(430, 262, 0.9) + palm(600, 300, 1.0) + palm(40, 310, 1.1)
    b += f'<g transform="translate(40 40) scale(0.62)">{trex()}</g>'
    b += rect(0, 300, W, 60, "#5f8f45") + fern(110, 330, 1.1) + fern(560, 340, 0.9, flip=-1) + fern(330, 345, 0.8)
    return frame(b, defs)

def scene_trex_module():
    """The T. rex for the hotspot module (also used as the article figure)."""
    defs = lin("sky", (0, "#cfe8d8"), (1, "#f4f1df"))
    b = rect(0, 0, W, H, "url(#sky)") + hills(300, 30, "#b8d7a0", 7) + rect(0, 318, W, 42, "#9cc17f")
    b += fern(40, 330, 1.0) + fern(610, 336, 0.9, flip=-1) + ellipse(330, 322, 150, 8, "#000000", 'opacity="0.12"')
    b += trex()
    return svg(b, defs=defs)

def scene_human_origins():
    defs = lin("sky", (0, "#f4a259"), (0.55, "#f9d78b"), (1, "#f3e1b6"))
    b = rect(0, 0, W, H, "url(#sky)") + circle(470, 150, 60, "#fff1c1", 'opacity="0.85"') + hills(250, 30, "#d9a65a", 9) + rect(0, 262, W, 98, "#c99446")
    b += path("M120 262 C120 220 110 190 100 170", stroke="#5a3d22", width=8) + ellipse(100, 160, 80, 18, "#5d7a3a") + ellipse(70, 150, 40, 12, "#6b8a44")
    for i, (x, s) in enumerate([(330, 1.0), (380, 0.85)]):
        y = 300
        b += circle(x, y - 92 * s, 10 * s, "#3b2a1e") + path(f"M{x} {y-80*s} l0 {38*s}", stroke="#3b2a1e", width=9 * s)
        b += path(f"M{x} {y-42*s} l{-12*s} {40*s} M{x} {y-42*s} l{12*s} {38*s}", stroke="#3b2a1e", width=8 * s)
        b += path(f"M{x} {y-72*s} l{-14*s} {22*s} M{x} {y-72*s} l{16*s} {18*s}", stroke="#3b2a1e", width=6 * s)
    for i in range(6): b += ellipse(200 + i * 22, 330 - (i % 2) * 8, 5, 8, "#8a6232", 'opacity="0.7"')
    return frame(b, defs)

def scene_civilizations():
    defs = lin("sky", (0, "#7cc4e8"), (1, "#f6e3b4"))
    b = rect(0, 0, W, H, "url(#sky)") + circle(110, 80, 34, "#fff3c4") + rect(0, 250, W, 110, "#e3c07a")
    b += poly([(250, 250), (370, 110), (490, 250)], "#d9a85b") + poly([(370, 110), (490, 250), (430, 250)], "#b8863f")
    b += poly([(470, 250), (540, 170), (610, 250)], "#cf9d52") + poly([(540, 170), (610, 250), (575, 250)], "#ad7d3a")
    for i in range(4): b += rect(60 + i * 12, 250 - 22 * (i + 1), 140 - i * 24, 22, ["#c98f4f", "#bd844a", "#b07843", "#a36d3d"][i])
    b += path("M0 300 C120 290 220 320 330 305 C450 290 540 320 640 300 L640 330 C540 345 430 315 330 332 C220 348 110 318 0 330Z", "#3c8dbc")
    b += palm(30, 300, 0.7) + palm(600, 300, 0.75)
    return frame(b, defs)

def scene_inventions():
    defs = lin("bg", (0, "#1f3b4d"), (1, "#2c5364")) + rad("bulb", (0, "#fff6c2"), (1, "#f9c74f"), r=0.6)
    b = rect(0, 0, W, H, "url(#bg)") + circle(320, 140, 120, "#f9c74f", 'opacity="0.18"')
    def gear(cx, cy, r, teeth, color):
        pts = []
        for i in range(teeth * 2):
            a = math.pi * i / teeth; rr = r if i % 2 == 0 else r * 0.8
            pts += [(cx + rr * math.cos(a - 0.12), cy + rr * math.sin(a - 0.12)), (cx + rr * math.cos(a + 0.12), cy + rr * math.sin(a + 0.12))]
        return poly(pts, color) + circle(cx, cy, r * 0.35, "#1f3b4d")
    b += gear(140, 250, 70, 10, "#7fa7bf") + gear(225, 300, 42, 8, "#a9c6d6") + gear(510, 260, 60, 9, "#7fa7bf")
    b += circle(320, 140, 64, "url(#bulb)") + rect(296, 196, 48, 22, "#cfd8dc", 4) + rect(300, 218, 40, 14, "#9aa8ae", 3) + rect(306, 232, 28, 8, "#7b8a90", 3)
    b += path("M300 150 q10 -24 20 0 q10 24 20 0", stroke="#e07a1f", width=4)
    b += rect(400, 300, 120, 18, "#e9e2cf", 3) + rect(404, 284, 112, 18, "#c94f4f", 3) + rect(408, 268, 104, 18, "#3f7fbf", 3)
    return frame(b, defs)

def ship(x, y, s=1.0):
    hull = path(f"M{x-90*s} {y} L{x+90*s} {y} L{x+70*s} {y+34*s} L{x-70*s} {y+34*s}Z", "#6b3f22") + rect(x - 90 * s, y - 4 * s, 180 * s, 8 * s, "#8a5a33")
    masts = path(f"M{x} {y} L{x} {y-150*s} M{x-50*s} {y} L{x-50*s} {y-110*s} M{x+50*s} {y} L{x+50*s} {y-100*s}", stroke="#4a2c16", width=5 * s)
    sails = (path(f"M{x-4*s} {y-140*s} Q{x+34*s} {y-110*s} {x-4*s} {y-70*s}Z", "#f6efe0") + path(f"M{x-4*s} {y-64*s} Q{x+40*s} {y-40*s} {x-4*s} {y-14*s}Z", "#f6efe0")
             + path(f"M{x-54*s} {y-100*s} Q{x-20*s} {y-74*s} {x-54*s} {y-40*s}Z", "#efe4cf") + path(f"M{x+46*s} {y-92*s} Q{x+80*s} {y-66*s} {x+46*s} {y-30*s}Z", "#efe4cf")
             + path(f"M{x} {y-150*s} l{22*s} {6*s} l{-22*s} {6*s}Z", "#c0392b"))
    return masts + sails + hull

def scene_colonialism():
    defs = lin("sky", (0, "#f7b267"), (0.5, "#f8d49a"), (1, "#a6d8e8")) + lin("sea", (0, "#3f8fb5"), (1, "#22577a"))
    b = rect(0, 0, W, H, "url(#sky)") + circle(500, 170, 50, "#fff0c7", 'opacity="0.9"') + rect(0, 240, W, 120, "url(#sea)")
    b += path("M430 240 q50 -60 110 -30 q40 10 100 20 L640 240Z", "#6a8f5a") + palm(560, 236, 0.5) + palm(600, 238, 0.45)
    b += ship(250, 250, 0.95)
    b += "".join(path(f"M{x} {y} q15 -6 30 0", stroke="#ffffff", width=2, extra='opacity="0.6"') for x, y in [(60, 280), (140, 310), (380, 300), (470, 330), (560, 290)])
    return frame(b, defs)

def scene_industrial():
    defs = lin("sky", (0, "#9aa5b1"), (1, "#e7dfd0"))
    b = rect(0, 0, W, H, "url(#sky)")
    for x, y, r in [(150, 70, 30), (190, 50, 36), (240, 60, 28), (420, 40, 32), (460, 30, 26)]: b += circle(x, y, r, "#cfd3d8", 'opacity="0.85"')
    b += rect(120, 90, 26, 130, "#7a4b3a") + rect(420, 70, 24, 150, "#7a4b3a") + rect(80, 170, 420, 110, "#9c5a43") + poly([(80, 170), (150, 130), (150, 170)], "#8a4f3a")
    b += poly([(150, 170), (220, 130), (220, 170)], "#8a4f3a") + poly([(220, 170), (290, 130), (290, 170)], "#8a4f3a")
    for i in range(6): b += rect(100 + i * 64, 205, 34, 40, "#f6d27a", 3)
    b += rect(0, 300, W, 60, "#6c6f73") + rect(0, 296, W, 6, "#4b4e52")
    for x in range(10, W, 36): b += rect(x, 300, 20, 6, "#8d6e63")
    b += rect(470, 240, 120, 50, "#2f3e4a", 6) + rect(560, 210, 30, 40, "#2f3e4a") + rect(470, 220, 18, 24, "#2f3e4a") + circle(495, 295, 14, "#1d262d") + circle(560, 295, 14, "#1d262d")
    b += circle(478, 200, 14, "#dfe3e8") + circle(468, 180, 18, "#e9ecef")
    return frame(b, defs)

def scene_peace():
    defs = lin("sky", (0, "#bfe3f5"), (1, "#f4f9fb"))
    b = rect(0, 0, W, H, "url(#sky)") + cloud(150, 90, 1.2) + cloud(520, 120, 1.0)
    b += circle(320, 420, 210, "#7fb6d9") + path("M180 300 q60 -40 120 -10 q40 20 80 -10 q60 -40 120 10 L520 360 L160 360Z", "#8bc28a", extra='opacity="0.8"')
    def dove(x, y, s):
        return (path(f"M{x} {y} c{20*s} {-10*s} {40*s} {-10*s} {60*s} {4*s} l{20*s} {-6*s} l{-10*s} {14*s} c{-10*s} {20*s} {-40*s} {30*s} {-70*s} {18*s} l{-30*s} {10*s} l{12*s} {-18*s} c{-6*s} {-6*s} {-6*s} {-14*s} {8*s} {-22*s}Z", "#ffffff", "#9fb3c0", 2)
                + path(f"M{x+16*s} {y-4*s} c{10*s} {-40*s} {40*s} {-60*s} {70*s} {-58*s} c{-14*s} {20*s} {-30*s} {40*s} {-50*s} {54*s}Z", "#f4f8fa", "#9fb3c0", 2)
                + circle(x + 70 * s, y - 1 * s, 2.2 * s, "#1d3a4d") + path(f"M{x+82*s} {y+0*s} q{20*s} {10*s} {34*s} {2*s}", stroke="#5a8f3c", width=3 * s)
                + ellipse(x + 104 * s, y - 2 * s, 7 * s, 3.5 * s, "#6ba84f") + ellipse(x + 94 * s, y + 6 * s, 7 * s, 3.5 * s, "#6ba84f"))
    b += dove(250, 170, 1.4)
    return frame(b, defs)

def scene_oceans():
    defs = lin("sea", (0, "#59b4d9"), (1, "#1f6f9f"))
    b = rect(0, 0, W, H, "url(#sea)")
    b += "".join(path(f"M{-40 + (r % 2) * 40} {y} q40 -12 80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0", stroke="#ffffff", width=2, extra='opacity="0.25"') for r, y in enumerate(range(20, 360, 34)))
    b += circle(320, 180, 130, "#2b8ac4") + circle(320, 180, 130, "none", 'stroke="#ffffff" stroke-width="3" opacity="0.6"')
    b += path("M230 120 q30 -30 70 -10 q20 20 0 40 q-30 20 -60 10 q-20 -10 -10 -40Z", "#7cc576") + path("M330 90 q40 -10 60 20 q10 30 -10 60 q-20 30 -40 0 q-20 -40 -10 -80Z", "#7cc576")
    b += path("M280 210 q30 -10 50 10 q10 30 -20 50 q-30 10 -40 -20Z", "#7cc576") + path("M380 230 q30 0 40 20 q0 20 -30 20 q-20 -10 -10 -40Z", "#7cc576")
    for a in range(0, 360, 30):
        r = math.radians(a); b += path(f"M{320 + 130*math.cos(r):.0f} {180 + 130*math.sin(r):.0f} L{320 + 142*math.cos(r):.0f} {180 + 142*math.sin(r):.0f}", stroke="#ffffff", width=2, extra='opacity="0.6"')
    cx, cy = 560, 290
    b += circle(cx, cy, 38, "#ffffff", 'opacity="0.85"') + poly([(cx, cy - 32), (cx + 8, cy), (cx, cy + 32), (cx - 8, cy)], "#2c3e50") + poly([(cx, cy - 32), (cx + 8, cy), (cx - 8, cy)], "#c0392b")
    b += poly([(cx - 32, cy), (cx, cy - 8), (cx + 32, cy), (cx, cy + 8)], "#7f8c8d", 'opacity="0.7"')
    return frame(b, defs)

def scene_life():
    defs = lin("sky", (0, "#a8dadc"), (1, "#f1faee"))
    b = rect(0, 0, W, H, "url(#sky)") + circle(540, 70, 32, "#ffd166") + hills(200, 50, "#7fb069", 11) + hills(250, 30, "#5c9a4f", 12)
    b += tree(80, 270, 1.3) + tree(170, 260, 1.0) + tree(470, 265, 1.2) + tree(560, 275, 1.0)
    b += path("M0 300 C150 280 250 330 400 300 C500 280 560 300 640 290 L640 360 L0 360Z", "#4aa3c7")
    for x in (300, 340, 380):  # mangroves
        b += path(f"M{x} 300 l-10 22 M{x} 300 l0 24 M{x} 300 l10 22", stroke="#5b3d23", width=3) + ellipse(x, 290, 24, 14, "#3f8f4a")
    b += path("M220 90 q8 -8 16 0 q8 -8 16 0", stroke="#2d3a3a", width=2.5) + path("M260 120 q6 -6 12 0 q6 -6 12 0", stroke="#2d3a3a", width=2.5)
    return frame(b, defs)

def scene_space():
    defs = lin("sky", (0, "#0b0c2a"), (1, "#2a1f5c")) + rad("planet", (0, "#f2c879"), (1, "#c98a3d"), cx=0.4, cy=0.4, r=0.7)
    b = rect(0, 0, W, H, "url(#sky)") + stars(120, 4, h=H) + circle(150, 260, 160, "#4a3f8c", 'opacity="0.25"')
    b += ellipse(330, 170, 150, 34, "none", 'stroke="#e9d3a8" stroke-width="10" opacity="0.8" transform="rotate(-14 330 170)"')
    b += circle(330, 170, 80, "url(#planet)") + path("M262 150 q70 -16 136 0", stroke="#b97b35", width=6, extra='opacity="0.6"')
    b += path("M180 172 A150 34 0 0 0 480 168", stroke="#e9d3a8", width=10, extra='transform="rotate(-14 330 170)" opacity="0.9"')
    b += circle(520, 80, 24, "#d6dde8") + circle(510, 74, 24, "#2a1f5c") + circle(90, 70, 12, "#9ec5ff")
    b += path("M520 330 L560 250 M560 250 l20 8 l-10 -40 l-20 -8 Z", stroke="#cfd6e6", width=6) + path("M548 330 L560 250 L572 330", stroke="#cfd6e6", width=4)
    return frame(b, defs)

def scene_culture_world():
    defs = lin("bg", (0, "#fbe8d3"), (1, "#f4d1ae"))
    b = rect(0, 0, W, H, "url(#bg)") + tais_band(0, 250, W, 70)
    b += ellipse(170, 170, 64, 28, "#8a4b2b") + rect(106, 170, 128, 70, "#a35d34") + ellipse(170, 240, 64, 22, "#7a4126") + ellipse(170, 170, 60, 24, "#e9cfa8")
    b += path("M118 180 L222 230 M222 180 L118 230", stroke="#5a2d16", width=4)
    b += path("M300 70 c-40 0 -70 30 -70 70 c0 40 30 60 60 60 c12 0 16 -8 16 -16 s-8 -12 -8 -20 8 -16 20 -16 h14 c26 0 40 -16 40 -36 c0 -26 -30 -42 -72 -42Z", "#fff8ec", "#c9a57a", 2)
    b += circle(275, 110, 9, "#e63946") + circle(300, 90, 9, "#457b9d") + circle(330, 98, 9, "#2a9d8f") + circle(262, 145, 9, "#f4a261")
    for x, y in [(450, 80), (500, 120), (540, 70)]:
        b += path(f"M{x} {y} l0 50", stroke="#3d2c5e", width=4) + ellipse(x - 8, y + 50, 10, 7, "#3d2c5e") + path(f"M{x} {y} q14 6 18 22", stroke="#3d2c5e", width=4)
    return frame(b, defs)

# Timor-Leste categories
def scene_tl_history():
    defs = lin("bg", (0, "#f3e1c0"), (1, "#e6c896"))
    b = rect(0, 0, W, H, "url(#bg)")
    b += path("M120 60 h330 a20 20 0 0 1 20 20 v200 a20 20 0 0 1 -20 20 h-330 a20 20 0 0 1 -20 -20 v-200 a20 20 0 0 1 20 -20Z", "#fbf1dc", "#b98a4e", 3)
    for i in range(7): b += path(f"M150 {100 + i * 26} q{120} -6 {260} 0", stroke="#8a6a44", width=3, extra='opacity="0.55"')
    b += path("M430 70 c40 40 50 100 30 160", stroke="#4a3a2a", width=4) + path("M430 70 c30 10 40 40 30 70 c-20 -10 -30 -40 -30 -70Z", "#6f8f8a")
    b += circle(510, 250, 70, "#b5873f") + circle(510, 250, 58, "#fff7e6") + path("M510 250 L510 205 M510 250 L540 262", stroke="#3d2b1f", width=5)
    for a in range(0, 360, 30):
        r = math.radians(a); b += circle(510 + 48 * math.cos(r), 250 + 48 * math.sin(r), 3, "#3d2b1f")
    b += flag_tl(60, 250, 90)
    return frame(b, defs)

def scene_tl_flag():
    defs = lin("sky", (0, "#bfe3f5"), (1, "#eef7fb"))
    b = rect(0, 0, W, H, "url(#sky)") + cloud(520, 70, 1.0) + rect(0, 320, W, 40, "#9cc58a")
    b += path("M150 330 L150 40", stroke="#6b6b6b", width=8) + circle(150, 36, 7, "#c9a227")
    b += f'<g transform="translate(154 52)">' + flag_tl(0, 0, 360) + '</g>'
    return frame(b, defs)

def scene_tl_map():
    return frame(timor_map())

def scene_tl_culture():
    defs = lin("bg", (0, "#f7e6d0"), (1, "#efd2b0"))
    b = rect(0, 0, W, H, "url(#bg)") + tais_band(40, 40, 360, 280)
    b += path("M40 320 l-6 26 M60 320 l-4 26 M80 320 l-2 26 M100 320 l0 26 M120 320 l2 26", stroke="#f4ead8", width=3)
    b += ellipse(500, 170, 60, 24, "#8a4b2b") + rect(440, 170, 120, 110, "#a35d34") + ellipse(500, 280, 60, 20, "#7a4126") + ellipse(500, 170, 56, 20, "#d9b98a")
    for i in range(5): b += path(f"M{446 + i*27} 190 l0 80", stroke="#e8b33a", width=3, extra='opacity="0.8"')
    b += path("M455 300 l-20 40 M545 300 l20 40", stroke="#5a2d16", width=6)
    return frame(b, defs)

def scene_tl_nature():
    defs = lin("sky", (0, "#9ad1e6"), (1, "#e8f4ea")) + lin("sea", (0, "#2f9cc4"), (1, "#1c6f93"))
    b = rect(0, 0, W, H, "url(#sky)") + circle(110, 70, 30, "#ffe08a") + path("M200 250 L330 70 L380 120 L430 90 L560 250Z", "#5f8c5a") + path("M310 98 L330 70 L352 98 L340 92 L330 104 L320 92Z", "#e8efe6")
    b += hills(230, 40, "#4f9a50", 21) + rect(0, 260, W, 100, "url(#sea)")
    for x in range(20, W, 60): b += path(f"M{x} 300 q12 -18 24 0 q12 -14 22 0", stroke="#ff9f80", width=6, extra='opacity="0.85"')
    b += path("M420 160 c10 -16 30 -20 44 -10 l14 2 -10 8 c0 18 -16 28 -34 26 l-20 8 6 -12 c-6 -6 -4 -16 0 -22Z", "#e07a2e", "#7a3a12", 2)
    b += path("M430 168 c10 4 20 2 26 -8", stroke="#7a3a12", width=2) + circle(462, 154, 2.2, "#1d1d1d")
    b += path("M60 330 q30 -14 60 0 q-8 10 -30 12 q-20 0 -30 -12Z M118 330 l14 -8 l0 16Z", "#f4d35e")
    return frame(b, defs)

def scene_tl_leaders():
    defs = lin("sky", (0, "#bfe3f5"), (1, "#f6f3ea"))
    b = rect(0, 0, W, H, "url(#sky)") + cloud(120, 80, 1.1) + rect(0, 290, W, 70, "#9cc58a")
    b += rect(150, 150, 340, 140, "#f6f1e7") + poly([(140, 150), (320, 90), (500, 150)], "#e9e2d2") + rect(140, 146, 360, 10, "#d9d0bd")
    for i in range(8): b += rect(170 + i * 40, 160, 14, 120, "#e3dccb")
    b += rect(290, 220, 60, 70, "#7a5a3a") + rect(140, 282, 360, 12, "#d9d0bd")
    b += path("M560 290 L560 80", stroke="#6b6b6b", width=5) + flag_tl(562, 82, 70)
    b += tree(80, 292, 1.0) + tree(600, 300, 0.7)
    return frame(b, defs)

def scene_tl_economy():
    defs = lin("bg", (0, "#e9f5e1"), (1, "#f9eedb"))
    b = rect(0, 0, W, H, "url(#bg)")
    b += path("M60 60 C160 90 220 160 250 320", stroke="#6b4a2b", width=8)
    for x, y in [(110, 90), (160, 120), (200, 170), (225, 220)]:
        b += ellipse(x - 30, y - 10, 34, 14, "#3f8f4a", f'transform="rotate(-30 {x-30} {y-10})"') + ellipse(x + 30, y - 4, 34, 14, "#4fa35a", f'transform="rotate(25 {x+30} {y-4})"')
        b += circle(x - 4, y + 6, 9, "#c1121f") + circle(x + 10, y + 10, 9, "#d62828") + circle(x + 2, y + 20, 9, "#a4161a")
    b += path("M300 330 q-10 -80 30 -110 h60 q40 30 30 110Z", "#c8a26b", "#8a6a3a", 3) + ellipse(360, 222, 40, 10, "#6b4a2b")
    for i in range(12): b += ellipse(340 + (i % 4) * 12, 214 + (i // 4) * 5, 5, 3.5, "#4a2f1a")
    for i, h in enumerate([60, 90, 120, 170]):
        b += rect(470 + i * 36, 320 - h, 24, h, ["#90be6d", "#43aa8b", "#277da1", "#f9844a"][i], 4)
    b += path("M460 320 h160", stroke="#55606a", width=3)
    return frame(b, defs)

# ------------------------------------------------------------- module diagrams
def diagram_size_compare():
    """Background grid for the size comparison (bars are painted live)."""
    b = rect(0, 0, W, H, "#f8faf5") + "".join(path(f"M40 {y} H620", stroke="#dfe7da", width=1) for y in range(40, 330, 40))
    return svg(b)

def scene_timeline():
    defs = lin("bg", (0, "#0f2a3d"), (0.5, "#245a5a"), (1, "#f2d49b"), x2=1, y2=0)
    b = rect(0, 0, W, H, "url(#bg)") + stars(40, 9, w=200, h=H)
    b += path("M30 200 H610", stroke="#ffffff", width=4, extra='opacity="0.85"')
    for i, x in enumerate([60, 150, 250, 350, 450, 560]):
        b += circle(x, 200, 12, ["#f94144", "#f3722c", "#f9c74f", "#90be6d", "#43aa8b", "#577590"][i], 'stroke="#ffffff" stroke-width="3"')
    b += circle(60, 120, 30, "#ff8c42", 'opacity="0.9"') + path("M240 140 q30 -50 60 0Z", "#6d597a") + sauropod(320, 160, 0.4, "#90be6d", "#2d5a3a")
    b += circle(560, 120, 18, "#3b2a1e") + path("M560 138 v40", stroke="#3b2a1e", width=8)
    return frame(b, defs)

def scene_industry_module():
    return scene_industrial()

# --------------------------------------------------------------- the registry
SCENES = {
    "world-earth": scene_earth, "world-dinosaurs": scene_dinosaurs, "world-human_origins": scene_human_origins,
    "world-civilizations": scene_civilizations, "world-inventions": scene_inventions, "world-colonialism": scene_colonialism,
    "world-industrial_revolution": scene_industrial, "world-world_wars": scene_peace, "world-geography_oceans": scene_oceans,
    "world-life_environment": scene_life, "world-science_space": scene_space, "world-culture_arts": scene_culture_world,
    "timor-history": scene_tl_history, "timor-flag": scene_tl_flag, "timor-map": scene_tl_map, "timor-culture": scene_tl_culture, "timor-nature": scene_tl_nature,
    "timor-leaders": scene_tl_leaders, "timor-economy": scene_tl_economy,
    "module-trex": scene_trex_module, "module-size": diagram_size_compare, "module-timeline": scene_timeline,
}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, make in SCENES.items(): (OUT / f"{name}.svg").write_text(make(), encoding="utf-8")
    manifest = {"generator": "tools/make-illustrations.py", "licence": "CC BY-SA 4.0 (original work for Lafa)",
                "note": "Flat vector illustrations drawn in code; the Timor-Leste map is schematic, not an official map.",
                "illustrations": sorted(SCENES)}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(f"{len(SCENES)} illustrations in {OUT}")

if __name__ == "__main__":
    main()
