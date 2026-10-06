#!/usr/bin/env python3
"""Build LAFA's outfit sprite sheets from the original character art.

Developer tool (needs numpy and Pillow; not a runtime dependency).

Every pose has hand-placed garment shapes in ``POSES`` (percent of the pose
crop). The shapes only decide *which garment* a pixel of skin belongs to; the
original outlines, shading, eyes, glasses, books and props are never touched.
Small slivers of skin left between a shape and one of the original outlines are
absorbed into the garment, so clothes end at the drawn outlines and look like
one piece instead of cut bands. Where a garment really ends on skin (collar,
cuffs, shorts hem, socks, shoes) a hem line is drawn like the original art.

Garment parts per pose:
    top   chest, belly and shoulders     arm   upper arms (short sleeves)
    fore  forearms (long sleeves)        hip   hips and thighs (shorts)
    shin  lower legs (trousers)          shoe  feet
    skin  always skin: hands, tail, head (painted last, wins over the rest)

Outfits:
    tuxedo  black jacket with satin lapels, white shirt front, bow tie, pocket
            square, black trousers and polished black shoes
    casual  sky-blue button shirt, khaki shorts, white socks and red sneakers
    tais    Tais Mane wrap with white sash, bead necklace and belak, arm bands
            (only for poses that have no hand-drawn Tais Mane art)

Bathing and the toilet stay undressed; every other activity is dressed.

    python3 tools/make-outfits.py            # write lafa/assets/lafa-*.png
    python3 tools/make-outfits.py --preview  # also write build/outfits-preview.png
"""
from collections import deque
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "lafa" / "assets"
UNDRESSED = {"bathing", "toilet"}
PARTS = ["top", "arm", "fore", "hip", "shin", "shoe"]
SKIN = 255

def E(cx, cy, rx, ry):
    """Ellipse shape (centre and radii in percent)."""
    return ("ellipse", cx, cy, rx, ry)

# neck: collar / bow-tie centre. Shapes are drawn in order; later ones win.
POSES = {
    "idle": dict(neck=(50, 44), parts=[
        ("top", [(6, 45), (36, 44), (50, 45.5), (60, 43), (66, 40), (73, 41), (76, 58), (73, 81), (6, 81)]),
        ("hip", [(6, 80), (74, 80), (76, 88), (6, 88)]),
        ("shin", [(6, 86.5), (78, 86.5), (78, 91.5), (6, 91.5)]),
        ("shoe", [(6, 91), (80, 91), (80, 100), (6, 100)]),
        ("skin", E(12, 63, 7, 7.5)), ("skin", E(36.5, 68, 9, 7)),
        ("skin", [(71, 46), (100, 46), (100, 100), (80, 100), (77, 90), (73.5, 82), (74.5, 66), (73, 55)]),
    ]),
    "reading": dict(neck=(64, 43), parts=[
        ("top", [(10, 44), (55, 43), (62, 41), (70, 40), (76, 42), (78, 60), (76, 82), (10, 82)]),
        ("hip", [(10, 81), (76, 81), (76, 90), (10, 90)]),
        ("shin", [(10, 88), (78, 88), (78, 92.5), (10, 92.5)]),
        ("shoe", [(10, 92), (80, 92), (80, 100), (10, 100)]),
        ("skin", E(8, 63, 6, 7)), ("skin", E(62, 64, 7, 6.5)),
        ("skin", [(74, 50), (100, 50), (100, 100), (82, 100), (79, 90), (75, 80), (76, 62)]),
    ]),
    "thinking": dict(neck=(50, 46), parts=[
        ("top", [(8, 46), (30, 44), (45, 46), (58, 43), (66, 40), (74, 42), (78, 60), (76, 83), (8, 83)]),
        ("hip", [(8, 82), (76, 82), (76, 91), (8, 91)]),
        ("shin", [(8, 89), (78, 89), (78, 93.5), (8, 93.5)]),
        ("shoe", [(8, 93), (80, 93), (80, 100), (8, 100)]),
        ("skin", E(35, 45, 7, 7.5)), ("skin", E(62, 76, 7, 6)),
        ("skin", [(74, 48), (100, 48), (100, 100), (82, 100), (79, 90), (75, 80), (77, 62)]),
    ]),
    "walking": dict(neck=(52, 45), parts=[
        ("top", [(18, 43), (40, 41), (55, 45), (66, 44), (72, 50), (78, 56), (76, 72), (65, 78), (20, 78), (16, 60)]),
        ("top", [(64, 52), (80, 54), (80, 66), (64, 70)]),
        ("hip", [(14, 74), (70, 72), (68, 82), (58, 84), (45, 80), (36, 84), (16, 84)]),
        ("shin", [(10, 83), (42, 81), (40, 91), (10, 91)]),
        ("shin", [(56, 80), (72, 76), (82, 82), (78, 88), (70, 94), (60, 93), (56, 86)]),
        ("shoe", [(10, 90.5), (40, 90.5), (40, 100), (10, 100)]),
        ("shoe", E(77, 92, 10, 7.5)),
        ("skin", E(80, 61, 6, 6)), ("skin", E(42, 62, 6, 7)),
        ("skin", [(0, 50), (22, 52), (26, 62), (24, 75), (18, 88), (0, 90)]),
    ]),
    "sitting": dict(neck=(62, 50), parts=[
        ("top", [(30, 53), (55, 51), (64, 48), (72, 45), (78, 50), (80, 75), (72, 85), (30, 85)]),
        ("hip", [(0, 70), (30, 72), (55, 84), (75, 80), (80, 97), (40, 99), (0, 99)]),
        ("shoe", E(12, 82, 12, 13)), ("shoe", E(57, 87, 11, 11)),
        ("skin", E(9, 66, 6, 6)), ("skin", E(62, 67, 6, 5.5)),
        ("skin", [(78, 50), (100, 50), (100, 95), (78, 92), (80, 75)]),
    ]),
    "gaming": dict(neck=(48, 51), parts=[
        ("top", [(15, 52), (35, 51), (48, 52), (60, 47), (70, 44), (78, 52), (80, 75), (72, 84), (15, 84)]),
        ("hip", [(20, 80), (75, 78), (80, 98), (20, 98)]),
        ("shoe", E(12, 84, 12, 14)), ("shoe", E(62, 87, 11, 12)),
        ("skin", E(24, 61, 7, 8)), ("skin", E(52, 60, 7, 8)),
        ("skin", [(77, 52), (100, 52), (100, 95), (78, 95), (81, 78)]),
    ]),
    "serious": dict(neck=(55, 45), parts=[
        ("top", [(26, 43), (40, 41), (46, 45), (60, 46), (78, 45), (82, 60), (75, 81), (26, 82)]),
        ("hip", [(22, 80), (78, 80), (78, 90), (22, 90)]),
        ("shin", [(20, 88), (80, 88), (80, 92.5), (20, 92.5)]),
        ("shoe", [(20, 92), (82, 92), (82, 100), (20, 100)]),
        ("skin", E(45, 60, 7, 6.5)), ("skin", E(73, 61, 7, 6)),
        ("skin", [(0, 60), (27, 62), (28, 75), (26, 88), (0, 92)]),
    ]),
    "angry": dict(neck=(42, 42), tie=False, collar=False, parts=[
        ("top", [(14, 42), (40, 40), (58, 40), (68, 42), (72, 60), (70, 85), (18, 85), (13, 55)]),
        ("hip", [(18, 83), (72, 83), (72, 91), (18, 91)]),
        ("shin", [(16, 89), (74, 89), (74, 93.5), (16, 93.5)]),
        ("shoe", [(16, 93), (76, 93), (76, 100), (16, 100)]),
        ("skin", [(72, 55), (100, 55), (100, 100), (84, 100), (81, 90), (74, 84), (72, 72)]),
    ]),
    "talking": dict(neck=(45, 44), parts=[
        ("top", [(25, 44), (40, 42), (52, 44), (62, 40), (72, 40), (78, 55), (76, 84), (25, 84)]),
        ("top", [(12, 46), (30, 44), (32, 62), (14, 60)]),
        ("hip", [(25, 82), (76, 82), (76, 91), (25, 91)]),
        ("shin", [(22, 89), (80, 89), (80, 93.5), (22, 93.5)]),
        ("shoe", [(20, 93), (82, 93), (82, 100), (20, 100)]),
        ("skin", E(6, 48, 7.5, 8)), ("skin", E(60, 68, 7, 6)),
        ("skin", [(73, 48), (100, 48), (100, 100), (85, 100), (82, 90), (75, 84), (76, 65)]),
    ]),
    "sleeping": dict(neck=(52, 50), tie=False, collar=False, parts=[
        ("top", [(44, 50), (50, 42), (58, 36), (66, 34), (70, 40), (64, 50), (60, 62), (58, 80), (48, 82), (44, 70)]),
        ("top", [(30, 52), (48, 50), (52, 60), (45, 68), (30, 68)]),
        ("hip", E(75, 61, 15, 14)),
        ("shoe", E(62, 79, 8, 11)),
        ("skin", E(28, 60, 6, 6)),
        ("skin", [(60, 82), (70, 78), (90, 76), (92, 58), (100, 55), (100, 100), (55, 100)]),
    ]),
    "studying": dict(neck=(47, 42), parts=[
        ("top", [(18, 38), (35, 38), (45, 42), (56, 42), (56, 58), (18, 58)]),
        ("hip", [(28, 66), (80, 66), (80, 84), (28, 84)]),
        ("shin", [(28, 80), (80, 80), (80, 86), (28, 86)]),
        ("shoe", E(40, 89, 10, 6)), ("shoe", E(70, 85, 10, 6)),
        ("skin", E(39, 46, 6, 8)), ("skin", E(81, 53, 5, 6)),
        ("skin", [(0, 45), (17, 45), (18, 80), (0, 80)]),
    ]),
    "eating": dict(neck=(45, 47), parts=[
        ("top", [(10, 50), (25, 47), (40, 48), (50, 48), (62, 43), (70, 42), (78, 55), (76, 78), (55, 82), (30, 82), (10, 60)]),
        ("hip", [(25, 74), (75, 72), (78, 95), (25, 95)]),
        ("shoe", E(14, 84, 14, 13)), ("shoe", E(55, 87, 13, 12)),
        ("skin", E(12, 47, 8, 7)), ("skin", E(51, 68, 7, 5)),
        ("skin", [(75, 48), (100, 48), (100, 95), (76, 92), (79, 72)]),
    ]),
    "stretching": dict(neck=(40, 42), parts=[
        ("top", [(22, 40), (35, 40), (50, 40), (62, 38), (70, 42), (72, 60), (70, 86), (25, 86), (22, 60)]),
        ("top", [(5, 30), (16, 28), (30, 40), (28, 50), (20, 48), (6, 36)]),
        ("top", [(66, 40), (82, 30), (92, 32), (90, 40), (72, 52)]),
        ("hip", [(22, 84), (72, 84), (72, 91), (22, 91)]),
        ("shin", [(20, 89), (76, 89), (76, 93.5), (20, 93.5)]),
        ("shoe", [(18, 93), (80, 93), (80, 100), (18, 100)]),
        ("skin", E(9, 26, 8, 8)), ("skin", E(89, 29, 8, 8)),
        ("skin", [(72, 58), (100, 58), (100, 100), (84, 100), (81, 90), (74, 84), (74, 72)]),
    ]),
}

def load_poses():
    poses = {}
    for image, manifest in [("lafa-atlas.png", "atlas.json"), ("lafa-activities.png", "activities.json")]:
        sheet = Image.open(ASSETS / image).convert("RGBA"); meta = json.loads((ASSETS / manifest).read_text())
        for state in meta["states"]:
            x, y, w, h = meta["rects"][state]
            poses[state] = (sheet.crop((x, y, x + w, y + h)), meta["canvas"])
    return poses

def classify(rgba):
    """Light green skin, yellow belly and value (HSV based).

    Dark green back spikes and the dark outlines are not skin, so clothes never
    cover them and the original line art stays crisp."""
    rgb = rgba[..., :3].astype(np.float32) / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1); v = mx; s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    d = np.maximum(mx - mn, 1e-6)
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    alpha = rgba[..., 3] > 150
    green = alpha & (hue >= 62) & (hue <= 165) & (s > 0.28) & (v > 0.50)
    yellow = alpha & (hue >= 36) & (hue < 62) & (s > 0.12) & (v > 0.62)
    return green, yellow, v

def components(mask):
    """4-connected components of a boolean mask -> (labels, count)."""
    h, w = mask.shape; lab = np.zeros((h, w), np.int32); n = 0
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]: continue
        n += 1; lab[y0, x0] = n; queue = deque([(y0, x0)])
        while queue:
            y, x = queue.popleft()
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n; queue.append((yy, xx))
    return lab, n

def grow(mask, steps=1):
    out = mask.copy()
    for _ in range(steps):
        g = out.copy(); g[1:] |= out[:-1]; g[:-1] |= out[1:]; g[:, 1:] |= out[:, :-1]; g[:, :-1] |= out[:, 1:]; out = g
    return out

def garment_map(spec, skin, h, w):
    """Label every skin pixel with a garment part index (0 = bare skin)."""
    canvas = Image.new("L", (w, h), 0); draw = ImageDraw.Draw(canvas)
    for part, shape in spec["parts"]:
        value = SKIN if part == "skin" else PARTS.index(part) + 1
        if shape[0] == "ellipse":
            _, cx, cy, rx, ry = shape
            draw.ellipse([(cx - rx) * w / 100, (cy - ry) * h / 100, (cx + rx) * w / 100, (cy + ry) * h / 100], fill=value)
        else:
            draw.polygon([(x * w / 100, y * h / 100) for x, y in shape], fill=value)
    labels = np.array(canvas).astype(np.int32); labels[labels == SKIN] = 0; labels[~skin] = 0
    # Snap to the drawn outlines: tiny pieces of bare skin take the garment
    # around them, tiny pieces of a garment become the part next to them.
    small = 0.0035 * h * w
    for _ in range(2):
        for value in range(0, len(PARTS) + 1):
            lab, n = components(skin & (labels == value))
            if not n: continue
            sizes = np.bincount(lab.ravel())
            for c in np.nonzero(sizes[1:] < small)[0] + 1:
                piece = lab == c; ring = grow(piece, 2) & skin & ~piece
                around = labels[ring]
                if around.size: labels[piece] = np.bincount(around, minlength=len(PARTS) + 1).argmax()
    return labels

def paint(rgba, mask, colour, v, source, lo=0.55, hi=1.18):
    """Fill mask with colour; light and shade come from the original pixels.

    Shade is measured against the median of each source colour (green skin and
    yellow belly) so a garment is one even colour over both."""
    out = rgba[..., :3].astype(np.float32); shade = np.ones(v.shape, np.float32)
    for src in source:
        part = mask & src
        if part.any(): shade = np.where(part, v / max(np.median(v[part]), 1e-3), shade)
    shade = np.clip(shade, lo, hi)[..., None]
    rgba[..., :3] = np.where(mask[..., None], np.clip(np.array(colour, np.float32) * shade, 0, 255), out).astype(np.uint8)

def hems(rgba, garments, skin, v, colour, width=2):
    """Finish the garments like the original line art.

    ``garments`` holds one id per garment (0 = bare skin). A hem line is drawn
    where a garment meets bare skin or a different garment (never between two
    shapes of the same garment), and the dark green outlines around clothes
    take the outfit's line colour so clothes and outline read as one piece."""
    edge = np.zeros(garments.shape, bool)
    for value in np.unique(garments):
        if value == 0: continue
        piece = garments == value
        edge |= piece & grow(skin & (garments != value), width)
    dressed = garments > 0; bare = skin & ~dressed
    rgb = rgba[..., :3].astype(np.int32)
    tinted = (rgb[..., 1] > rgb[..., 2] + 12) | ((rgb[..., 0] > rgb[..., 2] + 30) & (rgb[..., 1] > rgb[..., 2] + 30))
    line = (rgba[..., 3] > 40) & ~skin & ((v < 0.34) | tinted) & grow(dressed, 3) & ~grow(bare, 3)
    line &= ~((v >= 0.34) & ~grow(dressed, 1))  # keep the back spikes green
    rgba[..., :3] = np.where((edge | line)[..., None], np.array(colour, np.uint8), rgba[..., :3])
    return edge

def shrink(mask, steps=1):
    return ~grow(~mask, steps)

def closed(mask, steps=3):
    """Mask with the small inner lines (toes, fingers) filled in."""
    return shrink(grow(mask, steps), steps)

def part(labels, *names):
    return np.isin(labels, [PARTS.index(n) + 1 for n in names])

def socks_and_shoes(labels, shin_like, h):
    """The part of the shin just above the shoes (sock band)."""
    shoe = part(labels, "shoe"); band = np.zeros_like(shoe); reach = max(4, h // 28)
    for dy in range(1, reach + 1): band[:-dy] |= shoe[dy:]
    return band & shin_like

def shine(draw, shoes, colour):
    """A small highlight on the toe of each shoe."""
    lab, n = components(shoes)
    for c in range(1, n + 1):
        ys, xs = np.nonzero(lab == c)
        if ys.size < 40: continue
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max(); cx = x0 + (x1 - x0) * 0.32; cy = y0 + (y1 - y0) * 0.35
        draw.ellipse([cx - (x1 - x0) * 0.12, cy - (y1 - y0) * 0.1, cx + (x1 - x0) * 0.12, cy + (y1 - y0) * 0.1], fill=colour)

def collar(rgba, top, bare, v, colour, spec, depth):
    """A collar band along the neckline (where the top meets bare skin above)."""
    h = top.shape[0]; above = np.zeros_like(top)
    for dy in range(1, depth + 1): above[dy:] |= bare[:-dy]
    neck_y = spec["neck"][1] * h / 100
    band = top & above & (np.arange(h)[:, None] < neck_y + depth * 3)
    paint(rgba, band, colour, v, (band,), 0.85, 1.05)
    return band

def on_body(image, layer, allowed):
    """Composite a detail layer only over the body (never over books or props)."""
    alpha = np.array(layer)[..., 3].astype(np.float32) * allowed
    layer = np.array(layer); layer[..., 3] = alpha.astype(np.uint8)
    out = image.copy(); out.alpha_composite(Image.fromarray(layer)); return out

def neck(spec, h, w):
    return spec["neck"][0] * w / 100, spec["neck"][1] * h / 100

def tuxedo(image, spec):
    rgba = np.array(image).copy(); h, w = rgba.shape[:2]
    green, yellow, v = classify(rgba); skin = green | yellow
    labels = garment_map(spec, skin, h, w)
    cx, cy = neck(spec, h, w); hip = part(labels, "hip")
    waist = np.nonzero(hip.any(1))[0].min() if hip.any() else int(cy + h * 0.3)
    ys, xs = np.mgrid[0:h, 0:w]; t = np.clip((ys - cy) / max(waist - cy, 1), 0, 1)
    opening = np.abs(xs - cx) <= w * (0.20 * (1 - t) + 0.025)  # the jacket closes at the waist
    shirt = yellow & part(labels, "top") & opening
    jacket = part(labels, "top", "arm", "fore") & ~shirt; trousers = part(labels, "hip", "shin")
    shoes = closed(part(labels, "shoe")) & (rgba[..., 3] > 150)
    paint(rgba, jacket, (44, 46, 56), v, (green, yellow))
    paint(rgba, shirt, (250, 250, 246), v, (yellow,), 0.82, 1.05)
    paint(rgba, trousers, (36, 38, 47), v, (green, yellow))
    paint(rgba, shoes, (26, 26, 31), v, (green, yellow), 0.9, 1.1)
    band = np.zeros_like(shirt) if spec.get("collar") is False else collar(rgba, jacket | shirt, skin & ~(jacket | shirt | trousers | shoes), v, (250, 250, 246), spec, max(4, h // 60))
    hems(rgba, jacket * 1 + (shirt | band) * 2 + trousers * 3 + shoes * 4, skin, v, (16, 18, 22))
    out = Image.fromarray(rgba); draw = ImageDraw.Draw(out); s = max(9, w // 20)
    # Satin lapels follow the edge of the shirt front.
    for y in range(int(cy), min(h, int(cy + s * 5))):
        cols = np.nonzero(shirt[y])[0]
        if cols.size > 2:
            for x in (cols.min(), cols.max()):
                draw.line([(x - 2, y), (x + 2, y)], fill=(70, 72, 84))
    if spec.get("tie") is not False:
        layer = Image.new("RGBA", out.size, (0, 0, 0, 0)); bow = ImageDraw.Draw(layer)
        bow.polygon([(cx, cy + s * .45), (cx - s * 1.25, cy - s * .15), (cx - s * 1.25, cy + s * 1.05)], fill=(18, 18, 22, 255), outline=(0, 0, 0, 255))
        bow.polygon([(cx, cy + s * .45), (cx + s * 1.25, cy - s * .15), (cx + s * 1.25, cy + s * 1.05)], fill=(18, 18, 22, 255), outline=(0, 0, 0, 255))
        bow.ellipse([cx - s * .32, cy + s * .14, cx + s * .32, cy + s * .78], fill=(40, 40, 46, 255))
        out = on_body(out, layer, grow(jacket | shirt | band, 2) | skin); draw = ImageDraw.Draw(out)
    for i in range(1, 4):
        by = int(cy + s * (1.1 + i * 1.05))
        if 0 <= by < h:
            row = np.nonzero(shirt[by])[0]
            if row.size > 6:
                bx = int(row.mean()); draw.ellipse([bx - s * .17, by - s * .17, bx + s * .17, by + s * .17], fill=(32, 32, 36))
    # Shoe shine.
    shine(draw, shoes, (112, 116, 130))
    return out

def casual(image, spec):
    rgba = np.array(image).copy(); h, w = rgba.shape[:2]
    green, yellow, v = classify(rgba); skin = green | yellow
    labels = garment_map(spec, skin, h, w)
    shirt = part(labels, "top", "arm", "fore"); shorts = part(labels, "hip")
    socks = socks_and_shoes(labels, part(labels, "shin"), h)
    shoes = closed(part(labels, "shoe")) & (rgba[..., 3] > 150)
    paint(rgba, shirt, (64, 156, 214), v, (green, yellow), 0.6, 1.12)
    paint(rgba, shorts, (196, 160, 104), v, (green, yellow), 0.6, 1.12)
    paint(rgba, socks, (250, 250, 248), v, (green, yellow), 0.8, 1.04)
    paint(rgba, shoes, (214, 66, 60), v, (green, yellow), 0.88, 1.08)
    band = np.zeros_like(shirt) if spec.get("collar") is False else collar(rgba, shirt, skin & ~(shirt | shorts | socks | shoes), v, (250, 250, 250), spec, max(4, h // 60))
    hems(rgba, (shirt & ~band) * 1 + band * 5 + shorts * 2 + socks * 3 + shoes * 4, skin, v, (30, 44, 58))
    out = Image.fromarray(rgba); draw = ImageDraw.Draw(out); cx, cy = neck(spec, h, w); s = max(9, w // 20)
    # Sneaker soles and stripe.
    if shoes.any():
        ys, xs = np.nonzero(shoes); bottom = ys.max()
        sole = shoes & (np.arange(h)[:, None] >= bottom - max(3, h // 70))
        arr = np.array(out); arr[sole, :3] = (246, 246, 244); stripe = shoes & ~sole & (np.abs(np.arange(h)[:, None] - (bottom - h // 40)) <= 1)
        arr[stripe, :3] = (250, 250, 250); out = Image.fromarray(arr); draw = ImageDraw.Draw(out)
    # Button placket.
    for i in range(1, 4):
        by = int(cy + s * (1.1 + i * 1.1))
        if 0 <= by < h and 0 <= int(cx) < w and shirt[by, int(cx)]:
            draw.ellipse([cx - s * .14, by - s * .14, cx + s * .14, by + s * .14], fill=(240, 244, 248))
    return out

def tais(image, spec):
    rgba = np.array(image).copy(); h, w = rgba.shape[:2]
    green, yellow, v = classify(rgba); skin = green | yellow
    labels = garment_map(spec, skin, h, w)
    hip = part(labels, "hip"); waist = np.nonzero(hip.any(1))[0].min() if hip.any() else h
    rows = np.arange(h)[:, None]
    wrap = hip | (part(labels, "shin") & ~socks_and_shoes(labels, part(labels, "shin"), h)) | (part(labels, "top") & (rows >= waist - h * 0.07))
    paint(rgba, wrap, (122, 24, 38), v, (green, yellow), 0.6, 1.15)
    ys = np.arange(h)[:, None] * np.ones((1, w)); period = max(8, h // 50)
    stripe = wrap & ((ys // (period // 2)) % 4 == 0); paint(rgba, stripe, (232, 186, 70), v, (green, yellow), 0.7, 1.1)
    thin = wrap & ((ys // (period // 2)) % 4 == 2); paint(rgba, thin, (26, 22, 30), v, (green, yellow), 0.7, 1.1)
    if wrap.any():
        top = np.nonzero(wrap.any(1))[0].min(); sash = wrap & (ys < top + max(6, h // 28))
        paint(rgba, sash, (248, 246, 240), v, (green, yellow), 0.8, 1.05)
    hems(rgba, wrap * 1, skin, v, (70, 18, 26))
    base = Image.fromarray(rgba); out = Image.new("RGBA", base.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(out)
    cx, cy = neck(spec, h, w); s = max(9, w // 20)
    # Bead necklace with a silver belak disc.
    beads = 11
    for i in range(beads):
        t = (i / (beads - 1) - .5) * 2.4
        bx, by = cx + np.sin(t) * s * 1.9, cy + np.cos(t) * s * 1.1 - s * .3
        draw.ellipse([bx - s * .2, by - s * .2, bx + s * .2, by + s * .2], fill=(222, 96, 34), outline=(120, 40, 20))
    draw.ellipse([cx - s * .75, cy + s * .7, cx + s * .75, cy + s * 2.0], fill=(214, 216, 222), outline=(110, 112, 120))
    draw.ellipse([cx - s * .35, cy + s * 1.05, cx + s * .35, cy + s * 1.65], outline=(160, 162, 170))
    if spec.get("tie") is False: return base
    return on_body(base, out, grow(skin, 2))

def build(name, dresser, states, poses):
    cell = 560; cols = 4; rows = (len(states) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (0, 0, 0, 0)); rects = {}; canvas = {}
    for i, state in enumerate(states):
        image, size = poses[state]
        dressed = image if state in UNDRESSED else dresser(image, POSES[state])
        x, y = (i % cols) * cell, (i // cols) * cell
        sheet.paste(dressed, (x, y)); rects[state] = [x, y, image.width, image.height]; canvas[state] = size
    sheet.save(ASSETS / f"lafa-{name}.png", optimize=True)
    (ASSETS / f"{name}.json").write_text(json.dumps({"canvas": canvas, "states": states, "rects": rects, "generator": "tools/make-outfits.py"}, indent=1))
    print(f"lafa-{name}.png: {len(states)} poses")

def preview(poses, states, path):
    tile = int(__import__("os").environ.get("TILE", 220)); dressers = [("original", None), ("tuxedo", tuxedo), ("casual", casual), ("tais", tais)]
    sheet = Image.new("RGB", (len(dressers) * tile, len(states) * tile), (236, 238, 242))
    for r, state in enumerate(states):
        for c, (_, dresser) in enumerate(dressers):
            image = poses[state][0]
            if dresser and state not in UNDRESSED: image = dresser(image, POSES[state])
            im = image.copy(); im.thumbnail((tile - 8, tile - 8))
            sheet.paste(im, (c * tile + (tile - im.width) // 2, r * tile + (tile - im.height) // 2), im)
    path.parent.mkdir(parents=True, exist_ok=True); sheet.save(path); print(path)

def main(argv):
    poses = load_poses()
    missing = [s for s in poses if s not in UNDRESSED and s not in POSES]
    if "--preview" in argv:
        only = [a for a in argv if not a.startswith("--")] or [s for s in poses if s in POSES]
        preview(poses, only, ROOT / "build" / "outfits-preview.png"); return
    if missing: raise SystemExit(f"no garment shapes for: {', '.join(missing)}")
    traditional = json.loads((ASSETS / "traditional.json").read_text())["states"]
    build("tuxedo", tuxedo, list(poses), poses)
    build("casual", casual, list(poses), poses)
    build("tais", tais, [s for s in poses if s not in traditional], poses)

if __name__ == "__main__":
    main(sys.argv[1:])
