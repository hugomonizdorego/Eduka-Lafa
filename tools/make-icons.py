#!/usr/bin/env python3
"""Generate Lafa's own SVG icon set into lafa/assets/icons/ (+ manifest.json).

    python3 tools/make-icons.py

One consistent style: 24×24 grid, 1.8 px rounded strokes in `currentColor`
(Lafa recolours them for the light and dark themes). The Timor-Leste flag
icon keeps the flag's colours. All icons are original work for Lafa (MIT,
same as the code), so they work without any system icon theme.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "lafa/assets/icons"

def gear():
    """A gear outline with 8 teeth, computed so it stays symmetric."""
    pts = []
    for i in range(16):
        a0 = math.radians(i * 22.5 - 6); a1 = math.radians(i * 22.5 + 6)
        r = 9.2 if i % 2 == 0 else 7.2
        pts += [(12 + r * math.cos(a0), 12 + r * math.sin(a0)), (12 + r * math.cos(a1), 12 + r * math.sin(a1))]
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"

ICONS = {
    # --- the six menus and the sidebar footer
    "home": ["M3.5 10.5 12 3.5l8.5 7", "M5.5 9v11h4.5v-6h4v6h4.5V9"],
    "book-open": ["M12 6.6C10 5 7 4.6 3.5 5.1v13c3.5-.5 6.5 0 8.5 1.5 2-1.5 5-2 8.5-1.5v-13C17 4.6 14 5 12 6.6Z", "M12 6.6v13"],
    "bookshelf": ["M4 3.5h16v17H4z", "M4 12h16", "M7 5.5v4.5", "M9.6 5.5v4.5", "M12.6 6.2l2 3.8", "M7 14v4.5", "M10 14v4.5", "M14.5 14v4.5", "M17 14v4.5"],
    "calendar-check": ["M4 5.5h16v14.5H4z", "M4 9.5h16", "M8 3.5v4", "M16 3.5v4", "M8.5 14.5l2.4 2.4 4.6-4.8"],
    "monitor-help": ["M3 4.5h18v11.5H3z", "M9 20h6", "M12 16v4", "M10 8.4a2.1 2.1 0 1 1 2.7 2c-.5.2-.7.6-.7 1.1v.5", "M12 13.6v.1"],
    "settings": [gear(), "M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"],
    "info": ["M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z", "M12 11v5.5", "M12 7.6v.1"],
    # --- navigation and actions
    "back": ["M15 5l-7 7 7 7"],
    "chevron-right": ["M9 5l7 7-7 7"],
    "search": ["M17 10.5a6.5 6.5 0 1 1-13 0 6.5 6.5 0 0 1 13 0Z", "M20 20l-4.8-4.8"],
    "close": ["M6 6l12 12", "M18 6 6 18"],
    "plus": ["M12 5v14", "M5 12h14"],
    "minus": ["M5 12h14"],
    "check": ["M5 12.5l4.5 4.5L19 7.5"],
    "arrow-right": ["M4.5 12h15", "M13 5.5l6.5 6.5-6.5 6.5"],
    "arrow-up": ["M12 19.5v-15", "M5.5 11 12 4.5l6.5 6.5"],
    "arrow-down": ["M12 4.5v15", "M5.5 13l6.5 6.5 6.5-6.5"],
    "speaker": ["M4 9.5v5h3.5l5 4v-13l-5 4H4z", "M16 9a4 4 0 0 1 0 6", "M18.5 6.5a7.5 7.5 0 0 1 0 11"],
    "bookmark": ["M6.5 3.5h11v17l-5.5-4-5.5 4z"],
    "star": ["M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.8L12 16.8l-5.2 2.8 1-5.8-4.3-4.1 5.9-.8z"],
    "document": ["M6 3.5h8.5l4 4v13H6z", "M14.5 3.5v4h4", "M9 12h6.5", "M9 15.5h6.5"],
    "compass": ["M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z", "M15.5 8.5l-2 5-5 2 2-5z"],
    "tasks": ["M9 6.5h11", "M9 12h11", "M9 17.5h11", "M3.8 6.5l1.2 1.2 2-2.2", "M3.8 12l1.2 1.2 2-2.2", "M3.8 17.5l1.2 1.2 2-2.2"],
    "moon": ["M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z"],
    "monitor": ["M3 4.5h18v11.5H3z", "M9 20h6", "M12 16v4"],
    "play": ["M7 4.5v15l12-7.5z"],
    "ruler": ["M3.5 15.5 15.5 3.5l5 5-12 12z", "M7 12l2 2", "M9.5 9.5l1.5 1.5", "M12 7l2 2", "M14.5 4.5l1.5 1.5"],
    "lightbulb": ["M9 18h6", "M10 21h4", "M12 3a6 6 0 0 0-4 10.5c.7.7 1 1.5 1 2.5h6c0-1 .3-1.8 1-2.5A6 6 0 0 0 12 3Z"],
    "cloud-check": ["M7 18.5a4.5 4.5 0 0 1-.4-9 6 6 0 0 1 11.6 1.5 3.8 3.8 0 0 1-.2 7.5z", "M9.3 13.6l2 2 3.6-3.8"],
    "download": ["M12 4v11", "M7 10.5l5 5 5-5", "M4.5 19.5h15"],
    "globe": ["M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z", "M3 12h18", "M12 3c2.5 2.5 3.6 5.5 3.6 9S14.5 18.5 12 21c-2.5-2.5-3.6-5.5-3.6-9S9.5 5.5 12 3Z"],
    "newspaper": ["M4 5h13v14.5H5.5A1.5 1.5 0 0 1 4 18z", "M17 9h3v9a1.5 1.5 0 0 1-3 0", "M7 8.5h7", "M7 12h7", "M7 15.5h4"],
    "weather": ["M8.5 3.5v1.5", "M3.5 8.5H5", "M5 5l1 1", "M12 5l-1 1", "M6 10.2A3 3 0 0 1 11.2 7", "M8 19.5a3.5 3.5 0 0 1-.3-7 5 5 0 0 1 9.6 1.3 3 3 0 0 1-.3 5.7z"],
    "folder": ["M3.5 6.5a1.5 1.5 0 0 1 1.5-1.5h4.5l2 2.5H19a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 1 19 19.5H5A1.5 1.5 0 0 1 3.5 18z"],
    "image": ["M3.5 5h17v14h-17z", "M3.5 16l5-5 4 4 2.5-2.5 5.5 5.5", "M16 9a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z"],
    "question": ["M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z", "M9.6 9.2a2.5 2.5 0 1 1 3.3 2.4c-.6.2-.9.7-.9 1.3v.6", "M12 16.5v.1"],
    "timeline": ["M3.5 12h17", "M8 12a1.8 1.8 0 1 1-3.6 0 1.8 1.8 0 0 1 3.6 0Z", "M13.8 12a1.8 1.8 0 1 1-3.6 0 1.8 1.8 0 0 1 3.6 0Z", "M19.6 12a1.8 1.8 0 1 1-3.6 0 1.8 1.8 0 0 1 3.6 0Z", "M6.2 10.2V6", "M17.8 10.2V6", "M12 13.8V18"],
    "puzzle": ["M5 8h3.5a2 2 0 1 1 4 0H16v3.5a2 2 0 1 1 0 4V19H5z"],
    "refresh": ["M19.5 8A8 8 0 0 0 5 9", "M4.5 16a8 8 0 0 0 14.5-1", "M19.5 4v4h-4", "M4.5 20v-4h4"],
    "pin": ["M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11Z", "M14.5 10a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0Z"],
    "clock": ["M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z", "M12 7v5l3.5 2"],
    "accessibility": ["M13.5 4.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z", "M5 8.5l7 1.5 7-1.5", "M12 10v4.5", "M8.5 21l3.5-6.5 3.5 6.5"],
    # --- encyclopedia categories (world)
    "cat-earth": ["M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z", "M17.5 12a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0Z", "M14.5 12a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0Z"],
    "cat-dinosaur": ["M3 19.5c1.5-.3 3-1.5 4-3.5", "M7 16c-1-3 1-6 4-6.5l2.5-3c1-1.4 3-1.8 4.6-.7l2.4 1.8-1.4 1.4h-2.3l-1 2.4c1.4 1.8 1.6 4.4.2 6.4", "M9.5 16v3.5", "M14 16.5v3", "M7 16c2 .6 5 .8 9 .4", "M17.2 7.4h.01"],
    "cat-human": ["M14.5 5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0Z", "M7 21v-5.5a5 5 0 0 1 10 0V21", "M12 15.5V21"],
    "cat-pyramid": ["M2.5 20 12 4.5 21.5 20z", "M7.5 12.5h9", "M12 4.5v15.5", "M5 16.5h14"],
    "cat-invention": ["M9 18h6", "M10 21h4", "M12 3a6 6 0 0 0-4 10.5c.7.7 1 1.5 1 2.5h6c0-1 .3-1.8 1-2.5A6 6 0 0 0 12 3Z", "M10.5 13.5 12 9l1.5 4.5"],
    "cat-ship": ["M3 16h18l-2.5 4h-13z", "M12 3.5V16", "M12 4.5l6 9h-6", "M12 6.5 7 13.5h5"],
    "cat-factory": ["M3 20.5V10l5 3v-3l5 3v-3l5 3V4.5h3v16z", "M7 17h2", "M12 17h2", "M17 17h1"],
    "cat-dove": ["M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z", "M12 3v18", "M12 12l-6.4 6.4", "M12 12l6.4 6.4"],
    "cat-waves": ["M3 8c2-2 4-2 6 0s4 2 6 0 4-2 6 0", "M3 13c2-2 4-2 6 0s4 2 6 0 4-2 6 0", "M3 18c2-2 4-2 6 0s4 2 6 0 4-2 6 0"],
    "cat-leaf": ["M5 19.5C5 10.5 11 4.5 20 4.5c0 9-6 15-15 15Z", "M5 19.5l9-9"],
    "cat-planet": ["M16.5 12a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0Z", "M5.3 15.5C2.8 17.5 2.4 19.3 4 19.8c2.3.7 7.5-1.4 11.5-4.7 4-3.3 6.2-6.9 4.8-8-.8-.7-2.6-.3-4.6.9"],
    "cat-palette": ["M12 3.5a8.5 8.5 0 1 0 0 17c1.4 0 1.9-.9 1.9-1.8s-.9-1.4-.9-2.3 1-1.9 2.4-1.9h1.7a3.4 3.4 0 0 0 3.4-3.4c0-4.3-3.8-7.6-8.5-7.6Z", "M7.5 12h.01", "M9.5 8h.01", "M14 7.5h.01"],
    # --- encyclopedia categories (Timor-Leste)
    "cat-scroll": ["M7 4h11a2 2 0 0 1 2 2v1.5h-4", "M7 4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2V7.5", "M8.5 9h6", "M8.5 12.5h6", "M8.5 16h4"],
    "cat-map": ["M3.5 6.5l5.5-2 6 2 5.5-2v13l-5.5 2-6-2-5.5 2z", "M9 4.5v13", "M15 6.5v13"],
    "cat-culture": ["M4 5h16v10.5H9.5L4.5 19.5z", "M7 10.5l1.8-2 1.8 2 1.8-2 1.8 2 1.8-2 1.8 2"],
    "cat-bird": ["M4.5 14c1.4-4 4.8-6.5 8.6-6.5 2.2 0 3.8 1 4.8 2.5l3 .6-2.6 1.5c-.4 4-3.8 6.3-8 6.3H5.5", "M8.5 13.5c2.5.4 4.6-.7 5.7-2.8", "M16.4 10.2h.01", "M5.5 18.4 3 20.5"],
    "cat-landmark": ["M3 9.5l9-5 9 5z", "M5.5 9.5v8.5", "M9.5 9.5v8.5", "M14.5 9.5v8.5", "M18.5 9.5v8.5", "M3 20.5h18"],
    "cat-chart": ["M4 20.5h16", "M6.5 20.5v-6", "M10.5 20.5V9", "M14.5 20.5v-8", "M18.5 20.5V5.5"],
}

FLAG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
<path d="M5 3v18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
<path d="M6 4h14v10H6z" fill="#dc241f" stroke="#7a140f" stroke-width="0.8" stroke-linejoin="round"/>
<path d="M6 4l9 5-9 5z" fill="#ffc726"/>
<path d="M6 4l6 5-6 5z" fill="#1a1a1a"/>
<path d="M8.4 7.9l.35.9.95.05-.75.6.25.9-.8-.55-.8.55.25-.9-.75-.6.95-.05z" fill="#ffffff"/>
</svg>
"""

def svg(paths):
    body = "".join(f'<path d="{d}"/>' for d in paths)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{body}</svg>\n')

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, paths in ICONS.items(): (OUT / f"{name}.svg").write_text(svg(paths), encoding="utf-8")
    (OUT / "flag-tl.svg").write_text(FLAG, encoding="utf-8")
    manifest = {"generator": "tools/make-icons.py", "licence": "MIT (original work for Lafa)", "style": "24px grid, 1.8px round strokes, currentColor",
                "icons": sorted(list(ICONS) + ["flag-tl"])}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(f"{len(manifest['icons'])} icons in {OUT}")

if __name__ == "__main__":
    main()
