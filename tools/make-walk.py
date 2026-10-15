#!/usr/bin/env python3
"""Build Lafa's 8-frame walk cycle (lafa/assets/lafa-walk.png + .json).

Source: the walk-cycle row of the LAFA character sheet supplied by the
project owner for the 0.2.1 redesign (docs/design/lafa-character-sheet.webp,
"Arah animasi berjalan", frames 1–8, Casual Belajar outfit, facing right).

The tool cuts each frame out of the sheet, removes the paper background and
the ground shadow, aligns every frame on the same baseline (the lowest foot
pixel) and the same body anchor (the middle of the shirt), and writes:

* lafa-walk.png      one row per outfit (casual, tuxedo, tais) × 8 frames
* lafa-walk.json     frame size, baseline, anchor, stride, frame order

The Formal and Tais Mane rows are recoloured from the Casual frames (shirt →
charcoal jacket with a white shirt front and a small bow tie; trousers → a
tais wrap with woven stripes), so the clothes stay consistent with each step.

    python3 tools/make-walk.py [--preview]
"""
import json
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / "docs/design/lafa-character-sheet.webp"
OUT = ROOT / "lafa/assets"
CENTRES = [130, 312, 494, 672, 850, 1032, 1212, 1394]   # frame centres on the sheet
TOP, BOTTOM, HALF = 735, 930, 100                        # walk row bounds on the 1536×1024 sheet
PAD = 6

def cut(sheet, cx):
    box = np.array(sheet.crop((cx - HALF, TOP, cx + HALF, BOTTOM)).convert("RGB")).astype(int)
    h, w = box.shape[:2]
    r, g, b = box[..., 0], box[..., 1], box[..., 2]
    hi, lo = box.max(2), box.min(2)
    # Paper, card and ground shadow: light and almost grey.
    paper = (lo > 196) & (hi - lo < 26)
    shadow = (lo > 150) & (hi - lo < 34) & (np.arange(h)[:, None] > h * 0.72)
    open_ = paper | shadow
    bg = np.zeros((h, w), bool); q = deque()
    for y in range(h):
        for x in (0, w - 1):
            if open_[y, x] and not bg[y, x]: bg[y, x] = True; q.append((y, x))
    for x in range(w):
        for y in (0, h - 1):
            if open_[y, x] and not bg[y, x]: bg[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and open_[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True; q.append((ny, nx))
    # Keep only the largest blob (the character): drops the frame number and stray dots.
    body = ~bg; lab = np.zeros((h, w), int); best, best_n, n = 0, 0, 0
    for y in range(h):
        for x in range(w):
            if body[y, x] and not lab[y, x]:
                n += 1; lab[y, x] = n; q = deque([(y, x)]); count = 0
                while q:
                    cy, cx2 = q.popleft(); count += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx2 + dx
                        if 0 <= ny < h and 0 <= nx < w and body[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n; q.append((ny, nx))
                if count > best_n: best, best_n = n, count
    alpha = (lab == best).astype(np.uint8) * 255
    a = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.6))
    alpha = np.minimum(np.array(a), alpha.astype(int) + 0)   # soften only inwards
    alpha = np.where(lab == best, np.maximum(alpha, 150), 0).astype(np.uint8)
    rgba = np.dstack([box.astype(np.uint8), alpha])
    return rgba

def biggest(mask, keep=1, min_size=20):
    """The largest connected parts of a mask (drops spikes, glasses, specks)."""
    from scipy import ndimage
    lab, n = ndimage.label(mask)
    if not n: return mask
    sizes = ndimage.sum(mask, lab, range(1, n + 1)); order = np.argsort(sizes)[::-1][:keep]
    return np.isin(lab, [i + 1 for i in order if sizes[i] >= min_size])

def masks(rgba):
    rgb = rgba[..., :3].astype(int); r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]; a = rgba[..., 3] > 0
    hi, lo = rgb.max(2), rgb.min(2); h = rgb.shape[0]; ys = np.arange(h)[:, None]
    body = a & (ys > h * 0.36) & (ys < h * 0.80)
    # Dark green shirt (the spikes and glasses sit outside the torso rows or are separate parts).
    dark = fill_holes(body & (g > r + 25) & (g < 130) & (r < 80) & (b < 110), 1) & a
    # Open the mask so the back spikes, joined to the shirt by thin bridges, fall away.
    from scipy import ndimage
    core = biggest(ndimage.binary_erosion(dark, iterations=3))
    shirt = ndimage.binary_dilation(core, iterations=4) & dark
    collar = a & (r > 110) & (r > g + 45) & (ys > h * 0.30) & (ys < h * 0.62)
    collar = biggest(fill_holes(collar, 1) & a, keep=2, min_size=4)
    # Cream trousers including their grey-beige shading.
    legs = a & (ys > h * 0.55) & (lo > 118) & (r - b > 4) & (r - b < 66) & (abs(r - g) < 22)
    trousers = biggest(fill_holes(legs, 2) & a & ~shirt, keep=2, min_size=40)
    shoes = biggest(a & (hi < 95) & (ys > h * 0.80) & ~trousers, keep=2, min_size=10)
    shoes = fill_holes(shoes, 1) & a
    return shirt, trousers, shoes, collar

def fill_holes(mask, grow=1):
    img = Image.fromarray(mask.astype(np.uint8) * 255)
    img = img.filter(ImageFilter.MaxFilter(1 + 2 * grow)).filter(ImageFilter.MinFilter(1 + 2 * grow))
    return np.array(img) > 127

def recolour(rgba, mask, colour, gain=1.0):
    rgb = rgba[..., :3].astype(float)
    lum = (rgb[..., 0] * .3 + rgb[..., 1] * .59 + rgb[..., 2] * .11)
    ref = np.median(lum[mask]) if mask.any() else 128
    shade = np.clip(lum / max(ref, 1), 0.45, 1.35) ** gain
    out = rgba.copy()
    for c in range(3): out[..., c] = np.where(mask, np.clip(colour[c] * shade, 0, 255), rgba[..., c])
    return out

def formal(rgba):
    shirt, trousers, shoes, collar = masks(rgba)
    out = recolour(rgba, shirt, (52, 55, 62), 1.1)
    out = recolour(out, collar, (246, 246, 242), 0.6)
    out = recolour(out, trousers, (40, 42, 50), 1.1)
    out = recolour(out, shoes, (22, 22, 26), 1.0)
    img = Image.fromarray(out); d = ImageDraw.Draw(img)
    if collar.any():
        ys, xs = np.nonzero(collar); cy = int(np.percentile(ys, 80)); cx = int(np.percentile(xs, 70))
        s = 3.2   # small bow tie under the collar
        d.polygon([(cx, cy), (cx - s * 1.6, cy - s), (cx - s * 1.6, cy + s)], fill=(16, 16, 20))
        d.polygon([(cx, cy), (cx + s * 1.6, cy - s), (cx + s * 1.6, cy + s)], fill=(16, 16, 20))
        # White shirt front below the bow tie.
        front = [(cx - 2, cy + s), (cx + 3, cy + s), (cx + 2, cy + s * 6), (cx - 1, cy + s * 6)]
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(layer).polygon(front, fill=(246, 246, 242, 255))
        keep = Image.fromarray((shirt * 255).astype(np.uint8))
        img.paste(layer, (0, 0), Image.fromarray(np.minimum(np.array(layer)[..., 3], np.array(keep))))
        d = ImageDraw.Draw(img); d.ellipse([cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5], fill=(40, 40, 46))
    return np.array(img)

def tais(rgba):
    shirt, trousers, shoes, collar = masks(rgba)
    a = rgba[..., 3] > 0; h = rgba.shape[0]
    rows = np.arange(h)[:, None] * np.ones((1, rgba.shape[1]), int)
    out = rgba.copy()
    # Bare torso like the Tais Mane outfit: the shirt becomes Lafa's own skin.
    out = recolour(out, shirt | collar, (126, 196, 58), 0.6)
    # Woven tais wrap: red and black bands with thin gold lines.
    wrap = trousers
    bands = (rows // 4) % 4
    colours = {0: (150, 30, 38), 1: (24, 20, 22), 2: (150, 30, 38), 3: (220, 170, 60)}
    for k, c in colours.items(): out = recolour(out, wrap & (bands == k), c, 0.8)
    out = recolour(out, shoes, (120, 78, 44), 1.0)   # brown leather sandals
    # Bead necklace (belak-style disc) at the neck.
    img = Image.fromarray(out); d = ImageDraw.Draw(img)
    if collar.any():
        ys, xs = np.nonzero(collar); cy = int(np.percentile(ys, 60)); x0, x1 = int(xs.min()), int(xs.max())
        for i, x in enumerate(range(x0, x1 + 1, 3)):
            d.ellipse([x - 1.3, cy - 1.3, x + 1.3, cy + 1.3], fill=(230, 180, 60) if i % 2 else (180, 36, 40))
        mx = (x0 + x1) // 2; d.ellipse([mx - 3, cy + 2, mx + 3, cy + 8], fill=(232, 210, 120), outline=(150, 110, 40))
    return np.array(img)

def align(frames):
    """Common baseline and anchor: lowest foot pixel and the shirt's median x."""
    info = []
    for f in frames:
        a = f[..., 3] > 0; ys, xs = np.nonzero(a)
        shirt = masks(f)[0]; sx = int(np.median(np.nonzero(shirt)[1])) if shirt.any() else int(np.median(xs))
        info.append((ys.min(), ys.max(), xs.min(), xs.max(), sx))
    left = max(i[4] - i[2] for i in info) + PAD; right = max(i[3] - i[4] for i in info) + PAD
    up = max(i[1] - i[0] for i in info) + PAD
    W, H = left + right, up + PAD
    out = []
    for f, (y0, y1, x0, x1, sx) in zip(frames, info):
        canvas = np.zeros((H, W, 4), np.uint8)
        oy = (H - PAD) - y1; ox = left - sx
        sub = f[y0:y1 + 1, x0:x1 + 1]
        canvas[y0 + oy:y1 + 1 + oy, x0 + ox:x1 + 1 + ox] = sub
        out.append(canvas)
    return out, int(W), int(H), int(left)

def main(argv):
    sheet = Image.open(SHEET)
    if sheet.size != (1536, 1024): sheet = sheet.resize((1536, 1024), Image.LANCZOS)
    casual = [cut(sheet, cx) for cx in CENTRES]
    casual, W, H, anchor = align(casual)
    rows = {"casual": casual, "tuxedo": [formal(f) for f in casual], "tais": [tais(f) for f in casual]}
    order = ["casual", "tuxedo", "tais"]
    atlas = Image.new("RGBA", (W * 8, H * len(order)), (0, 0, 0, 0))
    for r, key in enumerate(order):
        for c, f in enumerate(rows[key]): atlas.paste(Image.fromarray(f), (c * W, r * H))
    atlas.save(OUT / "lafa-walk.png", optimize=True)
    # Stride: how far the body travels in one full cycle, measured from the
    # concept's foot positions (the planted foot moves back about one shoe
    # length per two frames); Lafa moves this many frame-pixels per cycle.
    meta = {"frame": [W, H], "frames": 8, "rows": order, "baseline": H - PAD, "anchor_x": anchor,
            "facing": "right", "stride": round(W * 0.62), "default_row": "casual",
            "source": "docs/design/lafa-character-sheet.webp (walk row, frames 1-8), owner-supplied design; Formal and Tais rows recoloured by tools/make-walk.py",
            "licence": "Same as the Lafa artwork (see docs/ASSETS.md)"}
    (OUT / "lafa-walk.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"lafa-walk.png: {len(order)} rows × 8 frames of {W}×{H}")
    if "--preview" in argv:
        bgc = Image.new("RGBA", atlas.size, (236, 240, 236, 255)); bgc.alpha_composite(atlas)
        (ROOT / "build").mkdir(exist_ok=True); bgc.resize((atlas.width * 2, atlas.height * 2), Image.NEAREST).save(ROOT / "build/walk-preview.png")
        print(ROOT / "build/walk-preview.png")

if __name__ == "__main__":
    main(sys.argv[1:])
