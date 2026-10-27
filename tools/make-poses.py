#!/usr/bin/env python3
"""Cut the three outfit poses (waving) out of the owner's character sheet
docs/design/lafa-character-sheet.webp → lafa/assets/lafa-poses.png + .json.

The sheet has a light mint background: pixels connected to the panel border
that look like the background become transparent; the outline keeps a soft
edge (alpha from the colour distance, de-matted). Needs Pillow, numpy, scipy.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "docs" / "design" / "lafa-character-sheet.webp"
OUT = ROOT / "lafa" / "assets"
# outfit → crop box inside its panel (x0, y0, x1, y1) on the 1536×1024 sheet
BOXES = {"casual": (58, 178, 502, 636), "traditional": (552, 170, 990, 636), "tuxedo": (1030, 178, 1480, 636)}
HEIGHT = 420          # every pose is scaled to the same height
T_LO, T_HI = 14, 64   # colour distance: background … solid

def cut(img, box):
    crop = np.asarray(img.crop(box).convert("RGB")).astype(np.float32)
    h, w, _ = crop.shape
    border = np.concatenate([crop[0], crop[-1], crop[:, 0], crop[:, -1]])
    bg = np.median(border, axis=0)
    dist = np.sqrt(((crop - bg) ** 2).sum(axis=2))
    # Background = near-background pixels connected to the border.
    near = dist < T_HI
    labels, _n = ndimage.label(near)
    edge = set(np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))) - {0}
    background = np.isin(labels, list(edge))
    solid = ~background
    # Soft edge only next to the character (drops the floor shadow and stray marks).
    ring = ndimage.binary_dilation(solid, iterations=2) & background
    alpha = np.where(solid, 1.0, 0.0)
    soft = np.clip((dist - T_LO) / (T_HI - T_LO), 0, 1)
    alpha[ring] = soft[ring]
    # Keep only the biggest solid part (the character) and parts touching it.
    lab2, n2 = ndimage.label(alpha > 0.5)
    if n2 > 1:
        sizes = ndimage.sum(np.ones_like(lab2), lab2, range(1, n2 + 1)); keep = 1 + int(np.argmax(sizes))
        big = ndimage.binary_dilation(lab2 == keep, iterations=3)
        alpha[~big] = 0.0
    # De-matte the half-transparent edge: remove the background colour.
    a = alpha[..., None]
    rgb = np.where(a > 0.02, (crop - (1 - a) * bg) / np.maximum(a, 0.02), crop)
    rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    ys, xs = np.nonzero(alpha > 0.05)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return Image.fromarray(rgba[y0:y1, x0:x1], "RGBA")

def main():
    img = Image.open(SHEET)
    poses = {k: cut(img, b) for k, b in BOXES.items()}
    scaled = {}
    for k, p in poses.items():
        w = round(p.width * HEIGHT / p.height); scaled[k] = p.resize((w, HEIGHT), Image.LANCZOS)
    width = sum(p.width for p in scaled.values()) + 8 * len(scaled)
    sheet = Image.new("RGBA", (width, HEIGHT), (0, 0, 0, 0)); rects = {}; x = 0
    for k, p in scaled.items():
        sheet.paste(p, (x, 0)); rects[k] = [x, 0, p.width, HEIGHT]; x += p.width + 8
    sheet.save(OUT / "lafa-poses.png", optimize=True)
    (OUT / "lafa-poses.json").write_text(json.dumps({"source": "docs/design/lafa-character-sheet.webp (owner's design)", "pose": "wave", "rects": rects}, indent=1) + "\n")
    print("lafa-poses.png", sheet.size, rects)

if __name__ == "__main__":
    main()
