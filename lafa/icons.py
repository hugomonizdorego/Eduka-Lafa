"""Lafa's own SVG icons and illustrations (lafa/assets/icons, lafa/assets/illustrations).

Icons are drawn in `currentColor`; `icon()` and `pixmap()` recolour them for
the theme. Everything ships in the package, so no system icon theme is needed.
QSvgRenderer (python3-pyqt5.qtsvg) is used when present; otherwise Qt's SVG
image plugin (libqt5svg5) loads the same data.
"""
from functools import lru_cache
from pathlib import Path
from .qt import Qt, QIcon, QPixmap, QImage, QPainter, QColor, QByteArray, QRectF, QSvgRenderer

ASSETS = Path(__file__).resolve().parent / "assets"
ICONS = ASSETS / "icons"
ILLUSTRATIONS = ASSETS / "illustrations"

def _svg(path, color=None):
    try: data = path.read_text(encoding="utf-8")
    except OSError: return None
    if color: data = data.replace("currentColor", QColor(color).name())
    return data.encode("utf-8")

def _render(data, width, height, ratio=1.0):
    width = max(1, int(round(width * ratio))); height = max(1, int(round(height * ratio)))
    image = QImage(width, height, QImage.Format_ARGB32_Premultiplied); image.fill(Qt.transparent)
    if QSvgRenderer is not None:
        renderer = QSvgRenderer(QByteArray(data))
        if renderer.isValid():
            painter = QPainter(image); painter.setRenderHint(QPainter.Antialiasing); painter.setRenderHint(QPainter.SmoothPixmapTransform)
            renderer.render(painter, QRectF(0, 0, width, height)); painter.end()
            pix = QPixmap.fromImage(image); pix.setDevicePixelRatio(ratio); return pix
    pix = QPixmap()
    if pix.loadFromData(data, "SVG"):
        pix = pix.scaled(width, height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation); pix.setDevicePixelRatio(ratio); return pix
    return QPixmap()

def exists(name):
    return (ICONS / f"{name}.svg").is_file()

@lru_cache(maxsize=512)
def pixmap(name, color="#17322b", size=24, ratio=1.0):
    data = _svg(ICONS / f"{name}.svg", color)
    return _render(data, size, size, ratio) if data else QPixmap()

@lru_cache(maxsize=256)
def icon(name, color="#17322b", active=None, size=48):
    """A QIcon (normal, plus `active` colour for selected/checked states)."""
    result = QIcon()
    normal = pixmap(name, color, size)
    if normal.isNull(): return result
    result.addPixmap(normal, QIcon.Normal, QIcon.Off)
    if active:
        hot = pixmap(name, active, size)
        result.addPixmap(hot, QIcon.Normal, QIcon.On); result.addPixmap(hot, QIcon.Active, QIcon.On); result.addPixmap(hot, QIcon.Selected, QIcon.On)
    return result

@lru_cache(maxsize=128)
def illustration(name, width, height, ratio=1.0):
    """An illustration scaled to cover width×height (cropped in the centre)."""
    data = _svg(ILLUSTRATIONS / f"{name}.svg")
    if not data: return QPixmap()
    if QSvgRenderer is not None:
        renderer = QSvgRenderer(QByteArray(data)); size = renderer.defaultSize()
        if size.width() > 0 and size.height() > 0:
            scale = max(width / size.width(), height / size.height())
            full = _render(data, size.width() * scale, size.height() * scale, ratio)
            x = int((full.width() - width * ratio) / 2); y = int((full.height() - height * ratio) / 2)
            out = full.copy(max(0, x), max(0, y), int(width * ratio), int(height * ratio)); out.setDevicePixelRatio(ratio); return out
    return _render(data, width, height, ratio)

def illustration_exists(name):
    return (ILLUSTRATIONS / f"{name}.svg").is_file()

def clear():
    pixmap.cache_clear(); icon.cache_clear(); illustration.cache_clear()
