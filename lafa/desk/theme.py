"""Lafa 0.3 look: soft pastel gradients, white "glass" cards and 3-D "clay" icons.

The style combines three references chosen by the project owner: a lavender
task dashboard (rounded white cards, clay icons, pill tags, charts and a
calendar), a pink "claymorphism" panel (soft extruded shapes) and a pink–violet
learning dashboard (gradient navigation pill, course cards with progress bars,
achievement badges). Everything is painted by Qt — no web view.

Contrast: body text on cards is ≥ 7:1, muted text ≥ 4.5:1 (checked in tests).
"""
from functools import lru_cache
from pathlib import Path

from ..qt import (QColor, QFont, QFontDatabase, QLinearGradient, QRadialGradient, QPainter, QPainterPath, QPixmap,
                  QPointF, QRectF, Qt, QApplication)
from .. import icons

ASSETS = Path(__file__).resolve().parents[1] / "assets"
FONT_FAMILY = "Nunito"

# Pastel accents used for clay icons, stat cards and charts: (strong, soft).
ACCENTS = {
    "violet": ("#7c5cfc", "#efeaff"), "pink": ("#ec4899", "#ffe4f1"), "mint": ("#14b88c", "#dcf7ef"),
    "butter": ("#f2a516", "#fff1d3"), "coral": ("#f25f6f", "#ffe4e7"), "sky": ("#3b93ec", "#e1f0ff"),
    "peach": ("#f77f3a", "#ffeadc"), "teal": ("#0fa5a0", "#d8f4f2"), "lilac": ("#a855f7", "#f3e8ff"),
    "indigo": ("#5b5bd6", "#e7e7fc"), "green": ("#22a35a", "#dcf5e5"), "rose": ("#e11d48", "#ffe1e7"),
    "slate": ("#5b6b84", "#e6ebf2"), "cyan": ("#0891b2", "#d9f3f9"),
}
TIMOR = {"red": "#dc241f", "yellow": "#ffc726", "black": "#000000", "white": "#ffffff"}

def tokens(dark=False):
    if dark:
        return {
            "dark": True, "bg_a": "#151129", "bg_b": "#211638", "bg_c": "#0f1d36",
            "blob_a": "#7c3aed", "blob_b": "#db2777", "blob_c": "#2563eb", "blob_alpha": 70,
            "glass": "rgba(255,255,255,0.075)", "glass_solid": "#231d3f", "glass_border": "rgba(255,255,255,0.12)",
            "card": "#231d3f", "card_hover": "#2c2550", "sidebar": "rgba(20,16,40,0.78)", "shadow": QColor(0, 0, 0, 90),
            "text": "#f3f0ff", "text2": "#d5d0f0", "muted": "#a8a3c8", "line": "rgba(255,255,255,0.10)",
            "primary": "#a48dff", "primary_text": "#ffffff", "primary_hover": "#b8a6ff", "primary_soft": "#352b66",
            "pink": "#ff7cc3", "nav_a": "#9b5cff", "nav_b": "#ff5fae", "focus": "#c4b5ff",
            "ok": "#4ade80", "ok_soft": "#16382a", "warn": "#fbbf24", "warn_soft": "#3d3115", "bad": "#fb7185", "bad_soft": "#3f1b27",
            "input": "rgba(255,255,255,0.08)", "track": "rgba(255,255,255,0.12)",
        }
    return {
        "dark": False, "bg_a": "#efeaff", "bg_b": "#fdeef6", "bg_c": "#e6f3ff",
        "blob_a": "#c4b5fd", "blob_b": "#f9a8d4", "blob_c": "#93c5fd", "blob_alpha": 110,
        "glass": "rgba(255,255,255,0.80)", "glass_solid": "#ffffff", "glass_border": "rgba(255,255,255,0.95)",
        "card": "#ffffff", "card_hover": "#faf8ff", "sidebar": "rgba(255,255,255,0.72)", "shadow": QColor(91, 70, 190, 34),
        "text": "#1f1a3d", "text2": "#4a4668", "muted": "#6e6a8e", "line": "#ece8f8",
        "primary": "#6d4aff", "primary_text": "#ffffff", "primary_hover": "#5b37f0", "primary_soft": "#efeaff",
        "pink": "#e23d93", "nav_a": "#a35cff", "nav_b": "#f0509c", "focus": "#6d4aff",
        "ok": "#15803d", "ok_soft": "#dcfce7", "warn": "#a16207", "warn_soft": "#fef3c7", "bad": "#be123c", "bad_soft": "#ffe4e6",
        "input": "rgba(255,255,255,0.92)", "track": "#ece8f8",
    }

def load_fonts():
    """Nunito (SIL OFL 1.1) is packaged with Lafa; system fonts fill in other scripts."""
    loaded = []
    for style in ("Regular", "SemiBold", "Bold", "ExtraBold"):
        path = ASSETS / "fonts" / f"Nunito-{style}.ttf"
        if path.is_file() and QFontDatabase.addApplicationFont(str(path)) >= 0: loaded.append(style)
    return loaded

def app_font(scale=1.0):
    font = QFont(FONT_FAMILY); font.setPointSizeF(10.5 * scale); font.setStyleStrategy(QFont.PreferAntialias)
    return font

def lighten(color, amount):
    c = QColor(color); h, s, l, a = c.hslHueF(), c.hslSaturationF(), c.lightnessF(), c.alphaF()
    return QColor.fromHslF(max(h, 0), s, min(1.0, l + (1 - l) * amount), a)

def darken(color, amount):
    c = QColor(color); h, s, l, a = c.hslHueF(), c.hslSaturationF(), c.lightnessF(), c.alphaF()
    return QColor.fromHslF(max(h, 0), s, max(0.0, l * (1 - amount)), a)

def rgba(color, alpha):
    c = QColor(color); return f"rgba({c.red()},{c.green()},{c.blue()},{alpha})"

def paint_background(painter, rect, tok):
    """Pastel gradient with three soft colour blobs (reference images 2 and 3)."""
    g = QLinearGradient(rect.topLeft(), rect.bottomRight())
    g.setColorAt(0, QColor(tok["bg_a"])); g.setColorAt(0.55, QColor(tok["bg_b"])); g.setColorAt(1, QColor(tok["bg_c"]))
    painter.fillRect(rect, g)
    w, h = rect.width(), rect.height()
    for (fx, fy, fr, key) in ((0.92, 0.05, 0.42, "blob_b"), (0.05, 0.95, 0.45, "blob_c"), (0.30, 0.25, 0.30, "blob_a")):
        c = QColor(tok[key]); c.setAlpha(tok["blob_alpha"])
        rg = QRadialGradient(QPointF(rect.left() + w * fx, rect.top() + h * fy), max(w, h) * fr)
        rg.setColorAt(0, c); c2 = QColor(c); c2.setAlpha(0); rg.setColorAt(1, c2)
        painter.fillRect(rect, rg)

@lru_cache(maxsize=512)
def _clay(name, color, size, ratio, radius_factor, glyph_factor, flat):
    px = int(size * ratio); pm = QPixmap(px, px); pm.fill(Qt.transparent); pm.setDevicePixelRatio(ratio)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
    base = QColor(color); s = float(size); pad = s * 0.06
    body = QRectF(pad, pad * 0.6, s - 2 * pad, s - 2 * pad - pad * 0.6); r = body.width() * radius_factor
    if not flat:
        # Soft contact shadow under the tile.
        for i in range(6):
            sh = QColor(darken(base, 0.35)); sh.setAlpha(16 - 2 * i)
            p.setPen(Qt.NoPen); p.setBrush(sh); grow = i * s * 0.012
            p.drawRoundedRect(body.adjusted(-grow, pad * 0.9 - grow * 0.2, grow, pad * 0.9 + grow), r + grow, r + grow)
    g = QLinearGradient(body.topLeft(), body.bottomRight())
    g.setColorAt(0, lighten(base, 0.38)); g.setColorAt(0.55, base); g.setColorAt(1, darken(base, 0.12))
    p.setPen(Qt.NoPen); p.setBrush(g); p.drawRoundedRect(body, r, r)
    if not flat:
        # Clay highlight: a soft white sheen on the upper-left edge.
        hl = QLinearGradient(body.topLeft(), QPointF(body.left(), body.center().y()))
        hl.setColorAt(0, QColor(255, 255, 255, 120)); hl.setColorAt(1, QColor(255, 255, 255, 0))
        path = QPainterPath(); path.addRoundedRect(body.adjusted(s * 0.05, s * 0.04, -s * 0.05, -body.height() * 0.45), r * 0.8, r * 0.8)
        p.setBrush(hl); p.drawPath(path)
        rim = QColor(255, 255, 255, 70); p.setBrush(Qt.NoBrush)
        from ..qt import QPen
        pen = QPen(rim); pen.setWidthF(max(1.0, s * 0.02)); p.setPen(pen); p.drawRoundedRect(body.adjusted(1, 1, -1, -1), r, r)
    gs = s * glyph_factor
    if name == "flag-tl":
        glyph = icons.pixmap(name, "#ffffff", int(gs), ratio)
    else:
        shadow = icons.pixmap(name, darken(base, 0.45).name(), int(gs), ratio)
        p.setOpacity(0.35); p.drawPixmap(QPointF(body.center().x() - gs / 2 + s * 0.015, body.center().y() - gs / 2 + s * 0.03), shadow); p.setOpacity(1)
        glyph = icons.pixmap(name, "#ffffff", int(gs), ratio)
    p.drawPixmap(QPointF(body.center().x() - gs / 2, body.center().y() - gs / 2), glyph)
    p.end()
    return pm

def clay_icon(name, color, size=48, ratio=None, radius=0.32, glyph=0.5, flat=False):
    """A 3-D clay tile with a white glyph (cached)."""
    if ratio is None:
        app = QApplication.instance(); ratio = app.devicePixelRatio() if app else 1.0
    if not icons.exists(name): name = "star"
    return _clay(name, QColor(color).name(), int(size), float(ratio), radius, glyph, flat)

def accent(key):
    return ACCENTS.get(key, ACCENTS["violet"])

def _chevron_file(color):
    """A small chevron for combo boxes (style sheets need a file; kept in the user's cache)."""
    import os
    folder = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "lafa"
    path = folder / f"chevron-{QColor(color).name()[1:]}.svg"
    if not path.exists():
        try:
            folder.mkdir(parents=True, exist_ok=True)
            path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path d="M6 9l6 6 6-6" fill="none" '
                            f'stroke="{QColor(color).name()}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>', encoding="utf-8")
        except OSError: return ""
    return path.as_posix()

def style_sheet(tok, scale=1.0):
    """The application style sheet. Borders are always 2 px so focus/hover never move the layout."""
    t = tok; fs = lambda px: f"{round(px * scale)}px"
    chevron = _chevron_file(t["muted"])
    arrow = f"QComboBox::down-arrow {{{{ image: url({chevron}); width: 14px; height: 14px; }}}}" if chevron else ""
    return f"""
* {{ font-family: '{FONT_FAMILY}', 'Noto Sans', 'DejaVu Sans', sans-serif; }}
QWidget {{ color: {t['text']}; font-size: {fs(14)}; }}
QMainWindow, QDialog {{ background: {t['bg_a']}; }}
QWidget#root, QWidget#page, QStackedWidget, QStackedWidget > QWidget, QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: 0; }}
QToolTip {{ background: {t['glass_solid']}; color: {t['text']}; border: 1px solid {t['line']}; border-radius: 8px; padding: 6px 8px; }}
QLabel {{ background: transparent; }}
QLabel#h1 {{ font-size: {fs(28)}; font-weight: 800; }}
QLabel#h2 {{ font-size: {fs(20)}; font-weight: 800; }}
QLabel#h3 {{ font-size: {fs(16)}; font-weight: 700; }}
QLabel#kpi {{ font-size: {fs(28)}; font-weight: 800; }}
QLabel#muted, QLabel#caption {{ color: {t['muted']}; }}
QLabel#caption {{ font-size: {fs(12)}; }}
QLabel#body {{ font-size: {fs(15)}; line-height: 150%; }}
QLabel#eyebrow {{ color: {t['primary']}; font-size: {fs(12)}; font-weight: 800; letter-spacing: 1px; }}
QLabel#pill {{ border-radius: 10px; padding: 3px 10px; font-size: {fs(12)}; font-weight: 700; }}
QLabel#link {{ color: {t['primary']}; font-weight: 700; }}
QFrame#sidebar {{ background: {t['sidebar']}; border: 2px solid {t['glass_border']}; border-radius: 26px; }}
QPushButton#nav {{ background: transparent; border: 2px solid transparent; border-radius: 16px; padding: 8px 10px; text-align: left;
    color: {t['text2']}; font-size: {fs(14)}; font-weight: 700; }}
QPushButton#nav:hover {{ background: {rgba(t['primary'], 0.10)}; color: {t['text']}; }}
QPushButton#nav:checked {{ color: #ffffff; border: 2px solid transparent;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {t['nav_a']}, stop:1 {t['nav_b']}); }}
QPushButton#nav:focus {{ border-color: {t['focus']}; }}
QPushButton {{ background: {t['card']}; color: {t['text']}; border: 2px solid {t['line']}; border-radius: 14px; padding: 8px 16px; font-weight: 700; }}
QPushButton:hover {{ border-color: {rgba(t['primary'], 0.55)}; background: {t['card_hover']}; }}
QPushButton:focus {{ border-color: {t['focus']}; }}
QPushButton:disabled {{ color: {t['muted']}; background: {t['track']}; border-color: {t['track']}; }}
QPushButton#primary {{ color: {t['primary_text']}; border: 2px solid transparent;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {t['nav_a']}, stop:1 {t['primary']}); }}
QPushButton#primary:hover {{ background: {t['primary_hover']}; }}
QPushButton#primary:focus {{ border-color: {t['focus']}; }}
QPushButton#primary:disabled {{ background: {t['track']}; color: {t['muted']}; }}
QPushButton#ghost {{ background: transparent; border: 2px solid transparent; color: {t['primary']}; padding: 6px 10px; }}
QPushButton#ghost:hover {{ background: {rgba(t['primary'], 0.10)}; }}
QPushButton#ghost:focus {{ border-color: {t['focus']}; }}
QPushButton#chip {{ background: {t['input']}; border: 2px solid {t['line']}; border-radius: 15px; padding: 5px 13px; font-weight: 700; color: {t['text2']}; }}
QPushButton#chip:checked {{ background: {t['primary_soft']}; color: {t['primary']}; border-color: {rgba(t['primary'], 0.5)}; }}
QPushButton#chip:hover {{ border-color: {rgba(t['primary'], 0.5)}; }}
QPushButton#chip:focus {{ border-color: {t['focus']}; }}
QPushButton#chip:disabled, QPushButton#ghost:disabled {{ color: {t['muted']}; background: {t['track']}; border-color: transparent; }}
QPushButton#icon {{ background: {t['input']}; border: 2px solid {t['line']}; border-radius: 14px; padding: 0; }}
QPushButton#icon:hover {{ border-color: {rgba(t['primary'], 0.55)}; }}
QPushButton#icon:focus {{ border-color: {t['focus']}; }}
QPushButton#answer {{ text-align: left; padding: 12px 16px; border-radius: 18px; font-size: {fs(15)}; }}
QPushButton#answer[state="right"] {{ background: {t['ok_soft']}; border-color: {t['ok']}; color: {t['text']}; }}
QPushButton#answer[state="wrong"] {{ background: {t['bad_soft']}; border-color: {t['bad']}; color: {t['text']}; }}
QPushButton#answer[state="locked"] {{ background: {t['warn_soft']}; border-color: {t['warn']}; color: {t['text']}; }}
QPushButton#answer[state="hidden"] {{ color: transparent; background: {t['track']}; border-color: {t['track']}; }}
QPushButton#segment {{ background: transparent; border: 2px solid transparent; border-radius: 14px; padding: 6px 16px; color: {t['text2']}; font-weight: 700; }}
QPushButton#segment:checked {{ background: {t['card']}; color: {t['text']}; border-color: {t['line']}; }}
QPushButton#segment:focus {{ border-color: {t['focus']}; }}
QFrame#segmented {{ background: {t['track']}; border-radius: 17px; }}
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {{ background: {t['input']}; border: 2px solid {t['line']}; border-radius: 16px; padding: 8px 12px;
    selection-background-color: {t['primary']}; selection-color: #ffffff; color: {t['text']}; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus {{ border-color: {t['focus']}; }}
QLineEdit#search {{ border-radius: 20px; padding: 9px 14px; font-size: {fs(14)}; }}
QComboBox::drop-down {{ border: 0; width: 30px; subcontrol-origin: padding; subcontrol-position: center right; }}
""" + (arrow.replace("{{", "{").replace("}}", "}") + "\n") + f"""QComboBox QAbstractItemView {{ background: {t['glass_solid']}; color: {t['text']}; border: 1px solid {t['line']}; selection-background-color: {t['primary_soft']}; selection-color: {t['text']}; }}
QCheckBox {{ spacing: 10px; }}
QCheckBox:focus {{ color: {t['primary']}; }}
QTextBrowser {{ background: transparent; border: 0; color: {t['text']}; font-size: {fs(15)}; }}
QListWidget {{ background: transparent; border: 0; outline: 0; }}
QListWidget::item {{ border-radius: 12px; padding: 8px; }}
QListWidget::item:selected {{ background: {t['primary_soft']}; color: {t['text']}; }}
QTabWidget::pane {{ border: 0; }}
QTabBar::tab {{ background: transparent; color: {t['text2']}; padding: 8px 14px; border: 2px solid transparent; border-radius: 12px; font-weight: 700; }}
QTabBar::tab:selected {{ background: {t['card']}; color: {t['text']}; border-color: {t['line']}; }}
QTabBar::tab:focus {{ border-color: {t['focus']}; }}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 4px 2px; }}
QScrollBar::handle:vertical {{ background: {rgba(t['primary'], 0.28)}; border-radius: 4px; min-height: 40px; }}
QScrollBar::handle:vertical:hover {{ background: {rgba(t['primary'], 0.55)}; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px 4px; }}
QScrollBar::handle:horizontal {{ background: {rgba(t['primary'], 0.28)}; border-radius: 4px; min-width: 40px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; border: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
QProgressBar {{ background: {t['track']}; border: 0; border-radius: 5px; height: 10px; max-height: 10px; text-align: center; color: transparent; }}
QProgressBar::chunk {{ border-radius: 5px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t['nav_a']}, stop:1 {t['nav_b']}); }}
QMenu {{ background: {t['glass_solid']}; border: 1px solid {t['line']}; color: {t['text']}; border-radius: 12px; padding: 6px; }}
QMenu::item {{ padding: 8px 18px; border-radius: 8px; }}
QMenu::item:selected {{ background: {t['primary_soft']}; }}
"""
