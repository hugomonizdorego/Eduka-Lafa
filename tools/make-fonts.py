#!/usr/bin/env python3
"""Make Lafa's static Nunito fonts from the variable font (SIL OFL 1.1).

Qt 5 cannot pick weights from a variable font, so Lafa ships four static
instances: Regular (400), SemiBold (600), Bold (700) and ExtraBold (800).

    python3 tools/make-fonts.py [path/to/Nunito[wght].ttf]

Source: https://github.com/google/fonts/tree/main/ofl/nunito (Nunito by
Vernon Adams, Cyreal and Jacques Le Bailly — SIL Open Font License 1.1).
"""
import sys
import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "lafa" / "assets" / "fonts"
URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/"
WEIGHTS = {"Regular": 400, "SemiBold": 600, "Bold": 700, "ExtraBold": 800}

def fetch(name, target):
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(URL + urllib.request.quote(name), timeout=60) as response: target.write_bytes(response.read())
    return target

def main(argv):
    cache = ROOT / "build" / "fonts"
    source = Path(argv[0]) if argv else fetch("Nunito[wght].ttf", cache / "Nunito[wght].ttf")
    OUT.mkdir(parents=True, exist_ok=True)
    licence = Path(argv[1]) if len(argv) > 1 else fetch("OFL.txt", cache / "OFL.txt")
    (OUT / "OFL.txt").write_bytes(licence.read_bytes())
    for style, weight in WEIGHTS.items():
        font = instantiateVariableFont(TTFont(source), {"wght": weight}, updateFontNames=True)
        # Keep one family name so Qt matches weights inside "Nunito".
        for record in font["name"].names:
            if record.nameID in (1, 16): record.string = "Nunito"
            if record.nameID in (2, 17): record.string = style if style in ("Regular", "Bold") else style
        font["OS/2"].usWeightClass = weight
        target = OUT / f"Nunito-{style}.ttf"; font.save(target)
        print(target.name, target.stat().st_size)

if __name__ == "__main__":
    main(sys.argv[1:])
