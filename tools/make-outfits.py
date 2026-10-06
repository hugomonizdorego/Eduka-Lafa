#!/usr/bin/env python3
"""Build LAFA's outfit sprite sheets from the original character art.

Developer tool (needs numpy and Pillow; not a runtime dependency). It dresses
every pose of the original atlases by recolouring body regions while keeping
the original outlines and shading, then draws small details:

* tuxedo  - black jacket and trousers, white shirt, bow tie, buttons, pocket
            square, black shoes (formal: parties, meetings, ceremonies)
* casual  - summer shirt with flower print over a white T-shirt, khaki
            shorts (beach, walks, shopping, hanging out)
* tais    - Tais Mane wrap for the poses that have no traditional drawing yet

Output (committed): lafa/assets/lafa-<outfit>.png + <outfit>.json in the same
format LAFA already loads. A professional illustrator can replace any sheet
with hand-drawn art in the same format; LAFA needs no code change.

    python3 tools/make-outfits.py
"""
import colorsys
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "lafa" / "assets"

# Body regions as fractions of each pose crop:
#   neck  - top of the chest (just under the snout)
#   hip   - waist line (bottom of the jacket / top of trousers or shorts)
#   foot  - top of the feet (shoes start here)
#   tail  - (x_from, x_to, y_from): the tail keeps its green skin
#   body  - (x_from, x_to): horizontal extent of the clothes
#   side  - how far clothes reach sideways from the belly (fraction of width);
#           the edge follows the belly row by row, so there are no straight seams
#   tie   - optional (x, y) bow-tie / collar position when the chest is hidden
#   keep  - optional rectangles (x0, y0, x1, y1) whose colours never change
# Poses listed in UNDRESSED stay as drawn (bath, toilet, sleep).
REGIONS = {
    "idle":       dict(neck=0.40, hip=0.80, foot=0.92, tail=(0.74, 1.0, 0.55), body=(0.0, 1.0)),
    "reading":    dict(neck=0.42, hip=0.81, foot=0.92, tail=(0.76, 1.0, 0.55), body=(0.0, 1.0)),
    "thinking":   dict(neck=0.41, hip=0.82, foot=0.93, tail=(0.72, 1.0, 0.60), body=(0.0, 1.0)),
    "walking":    dict(neck=0.42, hip=0.76, foot=0.90, tail=(0.0, 0.24, 0.50), body=(0.0, 1.0)),
    "sitting":    dict(neck=0.48, hip=0.78, foot=0.90, tail=(0.80, 1.0, 0.55), body=(0.0, 1.0)),
    "gaming":     dict(neck=0.46, hip=0.78, foot=0.90, tail=(0.82, 1.0, 0.55), body=(0.0, 1.0)),
    "serious":    dict(neck=0.43, hip=0.82, foot=0.93, tail=(0.0, 0.22, 0.60), body=(0.0, 1.0)),
    "angry":      dict(neck=0.41, hip=0.83, foot=0.93, tail=(0.76, 1.0, 0.60), body=(0.0, 1.0)),
    "talking":    dict(neck=0.43, hip=0.83, foot=0.93, tail=(0.76, 1.0, 0.60), body=(0.0, 1.0)),
    "studying":   dict(neck=0.50, hip=0.72, foot=0.93, tail=(1.0, 1.0, 1.0), body=(0.10, 0.80), tie=(0.36, 0.52)),
    "eating":     dict(neck=0.46, hip=0.84, foot=0.94, tail=(0.78, 1.0, 0.55), body=(0.0, 0.80), keep=[(0.06, 0.58, 0.58, 0.80), (0.08, 0.30, 0.28, 0.56)]),
    "stretching": dict(neck=0.42, hip=0.82, foot=0.93, tail=(0.76, 1.0, 0.62), body=(0.0, 1.0)),
}
UNDRESSED = {"sleeping", "bathing", "toilet"}

def load_poses():
    poses = {}
    for image, manifest in [("lafa-atlas.png", "atlas.json"), ("lafa-activities.png", "activities.json")]:
        sheet = Image.open(ASSETS / image).convert("RGBA"); meta = json.loads((ASSETS / manifest).read_text())
        for state in meta["states"]:
            x, y, w, h = meta["rects"][state]
            poses[state] = (sheet.crop((x, y, x + w, y + h)), meta["canvas"])
    return poses

def classify(rgba):
    """Masks for green skin, yellow belly and dark outlines (HSV based)."""
    rgb = rgba[..., :3].astype(np.float32) / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1); v = mx; s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    hue = np.zeros_like(v); d = np.maximum(mx - mn, 1e-6)
    hue = np.where(mx == r, ((g - b) / d) % 6, hue); hue = np.where(mx == g, (b - r) / d + 2, hue); hue = np.where(mx == b, (r - g) / d + 4, hue)
    hue = hue * 60
    alpha = rgba[..., 3] > 210  # soft anti-aliased edges keep their colour
    green = alpha & (hue >= 62) & (hue <= 165) & (s > 0.28) & (v > 0.22)
    yellow = alpha & (hue >= 36) & (hue < 62) & (s > 0.15) & (v > 0.62)
    return green, yellow, v

def recolour(rgba, mask, colour, v, reference=0.80, floor=0.35):
    """Paint mask with colour, keeping the original light and shade."""
    target = np.array(colour, np.float32)
    shade = np.clip(v / reference, floor, 1.25)[..., None]
    rgba[..., :3] = np.where(mask[..., None], np.clip(target * shade, 0, 255), rgba[..., :3])

def follow_belly(yellow, region, h, w):
    """Per-row horizontal limits of the clothes, following the belly outline."""
    x0, x1 = (int(f * w) for f in region["body"]); side = int(region.get("side", 0.20) * w)
    top, hip, bottom = int(region["neck"] * h), int(region["hip"] * h), h
    left = np.full(h, w, dtype=int); right = np.full(h, -1, dtype=int)
    known = []
    for y in range(top, bottom):
        cols = np.nonzero(yellow[y, x0:x1])[0]
        if cols.size >= 4: left[y], right[y] = cols.min() + x0, cols.max() + x0; known.append(y)
    if not known: return np.zeros((h, w), bool)
    known = np.array(known)
    for y in range(top, bottom):
        if right[y] < 0:
            near = known[np.abs(known - y).argmin()]; left[y], right[y] = left[near], right[near]
    # Smooth the limits so the edge is a gentle curve, and widen legs a little.
    kernel = np.ones(15) / 15
    left = np.convolve(np.pad(left, 7, mode="edge"), kernel, mode="valid").astype(int)
    right = np.convolve(np.pad(right, 7, mode="edge"), kernel, mode="valid").astype(int)
    xs = np.arange(w)[None, :]; rows = np.arange(h)[:, None]
    extra = np.where(rows >= hip, int(0.06 * w), 0)
    return (xs >= (left[:, None] - side - extra)) & (xs <= (right[:, None] + side + extra)) & (rows >= top)

def bands(h, w, region, yellow=None, centre=None, whole_tail=False):
    ys, xs = np.mgrid[0:h, 0:w]; fy, fx = ys / h, xs / w
    x0, x1 = region["body"]; tx0, tx1, ty = region["tail"]
    # A tailcoat may cover the tail base; casual clothes never cover the tail.
    tail_from = ty if whole_tail else max(ty, region["hip"])
    inside = (fx >= x0) & (fx <= x1) & ~((fx >= tx0) & (fx <= tx1) & (fy >= tail_from))
    if yellow is not None: inside &= follow_belly(yellow, region, h, w)
    for kx0, ky0, kx1, ky1 in region.get("keep", []): inside &= ~((fx >= kx0) & (fx <= kx1) & (fy >= ky0) & (fy <= ky1))
    # Shoulders curve down away from the collar instead of a straight cut.
    cxf = centre if centre is not None else sum(region["body"]) / 2
    neckline = region["neck"] + 0.05 * np.minimum(1.0, ((fx - cxf) / 0.34) ** 2)
    torso = inside & (fy >= neckline) & (fy < region["hip"])
    legs = inside & (fy >= region["hip"]) & (fy < region["foot"])
    feet = inside & (fy >= region["foot"])
    return torso, legs, feet, fy, fx

def outline(rgba, changed, skin, colour=(24, 52, 30), width=2):
    """Draw a hem line where clothes meet skin, like the original outlines."""
    near = skin.copy()
    for _ in range(width):
        grown = near.copy()
        grown[1:] |= near[:-1]; grown[:-1] |= near[1:]; grown[:, 1:] |= near[:, :-1]; grown[:, :-1] |= near[:, 1:]
        near = grown
    edge = changed & near & (rgba[..., 3] > 40)
    rgba[..., :3] = np.where(edge[..., None], np.array(colour, np.uint8), rgba[..., :3])

def neck_point(yellow, region, h, w):
    """Centre of the belly just under the snout (bow tie / collar position)."""
    if "tie" in region: return int(region["tie"][0] * w), int(region["tie"][1] * h)
    y0 = int(region["neck"] * h); rows = yellow[y0:y0 + max(6, h // 14)]
    cols = np.nonzero(rows.any(0))[0]
    x = int(cols.mean()) if cols.size else int(w * sum(region["body"]) / 2)
    ys = np.nonzero(yellow[:, x])[0]; ys = ys[ys >= y0]
    return x, int(ys[0]) if ys.size else y0 + 6

def tuxedo(image, region):
    rgba = np.array(image).copy(); h, w = rgba.shape[:2]
    green, yellow, v = classify(rgba); cx, cy = neck_point(yellow, region, h, w)
    torso, legs, feet, fy, fx = bands(h, w, region, centre=cx / w)
    jacket, shirt, trousers = green & torso, yellow & torso, green & legs
    shoes = (green | yellow) & feet & (fy < region["foot"] + 0.035)
    recolour(rgba, jacket, (40, 42, 50), v)                  # jacket and sleeves
    recolour(rgba, shirt, (250, 250, 247), v, 0.92, 0.82)    # shirt
    recolour(rgba, trousers, (34, 36, 43), v)                # trousers
    recolour(rgba, shoes, (22, 22, 26), v, 0.9, 0.5)         # shoes
    changed = jacket | shirt | trousers | shoes; outline(rgba, changed, (green | yellow) & ~changed)
    out = Image.fromarray(rgba); draw = ImageDraw.Draw(out); s = max(10, w // 18)
    draw.polygon([(cx, cy + s * 0.45), (cx - s * 1.25, cy - s * 0.15), (cx - s * 1.25, cy + s * 1.05)], fill=(18, 18, 22), outline=(0, 0, 0))
    draw.polygon([(cx, cy + s * 0.45), (cx + s * 1.25, cy - s * 0.15), (cx + s * 1.25, cy + s * 1.05)], fill=(18, 18, 22), outline=(0, 0, 0))
    draw.ellipse([cx - s * 0.32, cy + s * 0.15, cx + s * 0.32, cy + s * 0.78], fill=(40, 40, 46))
    belly = yellow & torso
    for i in range(1, 4):
        by = cy + int(s * (1.2 + i * 1.1)); bx = cx
        row = np.nonzero(belly[min(h - 1, by)])[0]
        if row.size: bx = int(row.mean()); draw.ellipse([bx - s * 0.18, by - s * 0.18, bx + s * 0.18, by + s * 0.18], fill=(30, 30, 34))
    jacket = green & torso
    px, py = cx + int(s * 2.6), cy + int(s * 3.2)
    if 0 <= py < h and 0 <= px < w and jacket[max(0, py - s):py + s, max(0, px - s):px + s].mean() > 0.9:
        draw.polygon([(px - s * 0.6, py), (px + s * 0.6, py), (px - s * 0.2, py - s * 0.7), (px + s * 0.3, py - s * 0.6)], fill=(205, 30, 45))  # pocket square
    return out

def casual(image, region):
    """Summer casual: solid short-sleeve shirt with white collar, khaki shorts."""
    rgba = np.array(image).copy(); h, w = rgba.shape[:2]
    green, yellow, v = classify(rgba); cx, cy = neck_point(yellow, region, h, w)
    torso, legs, feet, fy, fx = bands(h, w, region, centre=cx / w, whole_tail=True)
    shirt, tee = green & torso, yellow & torso
    recolour(rgba, shirt, (58, 150, 214), v)                 # sky-blue shirt
    recolour(rgba, tee, (252, 252, 250), v, 0.92, 0.8)       # white T-shirt under the open shirt
    shorts = (green | yellow) & legs & (fy < region["hip"] + (region["foot"] - region["hip"]) * 0.55)
    recolour(rgba, shorts, (199, 164, 108), v, 0.85)        # khaki shorts
    changed = shirt | tee | shorts; outline(rgba, changed, (green | yellow) & ~changed)
    out = Image.fromarray(rgba); draw = ImageDraw.Draw(out); s = max(10, w // 18)
    # White collar points either side of the neck and a coral shirt pocket.
    draw.polygon([(cx - s * 0.2, cy), (cx - s * 1.9, cy - s * 0.2), (cx - s * 1.0, cy + s * 1.2)], fill=(255, 255, 255), outline=(150, 170, 185))
    draw.polygon([(cx + s * 0.2, cy), (cx + s * 1.9, cy - s * 0.2), (cx + s * 1.0, cy + s * 1.2)], fill=(255, 255, 255), outline=(150, 170, 185))
    px, py = cx + int(s * 2.6), cy + int(s * 2.6)
    if 0 <= py < h and 0 <= px < w and shirt[max(0, py - s):py + s, max(0, px - s):px + s].mean() > 0.9:
        draw.rounded_rectangle([px - s * 0.7, py - s * 0.6, px + s * 0.7, py + s * 0.7], radius=3, fill=(240, 120, 90))
    return out

def tais(image, region):
    """Tais Mane wrap (red with yellow/black stripes) and a white sash."""
    rgba = np.array(image).copy(); h, w = rgba.shape[:2]
    green, yellow, v = classify(rgba); torso, legs, feet, fy, fx = bands(h, w, region)
    top = region["hip"] - 0.06; bottom = region["hip"] + (region["foot"] - region["hip"]) * 0.75
    wrap = (green | yellow) & (fy >= top) & (fy < bottom) & ~((fx >= region["tail"][0]) & (fx <= region["tail"][1]) & (fy >= region["tail"][2]))
    recolour(rgba, wrap, (176, 28, 40), v, 0.8, 0.55)
    ys = np.arange(h)[:, None] * np.ones((1, w)); stripe = ((ys // max(6, h // 60)) % 4 == 0) & wrap
    recolour(rgba, stripe, (238, 190, 60), v, 0.8, 0.6)
    belt = wrap & (fy < top + 0.025); recolour(rgba, belt, (250, 248, 240), v, 0.9, 0.85)
    outline(rgba, wrap, (green | yellow) & ~wrap, (70, 20, 24))
    return Image.fromarray(rgba)

def build(name, dresser, states, poses):
    cell = 560; cols = 4; rows = (len(states) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (0, 0, 0, 0)); rects = {}; canvas = {}
    for i, state in enumerate(states):
        image, size = poses[state]
        dressed = image if state in UNDRESSED else dresser(image, REGIONS[state])
        x, y = (i % cols) * cell, (i // cols) * cell
        sheet.paste(dressed, (x, y)); rects[state] = [x, y, image.width, image.height]; canvas[state] = size
    sheet.save(ASSETS / f"lafa-{name}.png", optimize=True)
    (ASSETS / f"{name}.json").write_text(json.dumps({"canvas": canvas, "states": states, "rects": rects, "generator": "tools/make-outfits.py"}, indent=1))
    print(f"lafa-{name}.png: {len(states)} poses")

def main():
    poses = load_poses()
    traditional = json.loads((ASSETS / "traditional.json").read_text())["states"]
    build("tuxedo", tuxedo, list(poses), poses)
    build("casual", casual, list(poses), poses)
    build("tais", tais, [s for s in poses if s not in traditional], poses)

if __name__ == "__main__":
    main()
