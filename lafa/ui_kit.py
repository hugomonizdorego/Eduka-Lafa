"""LAFA Desktop's visual building blocks (0.1.3 design).

The look combines a "smart care" overview (large colourful tiles with LAFA in
them and one round action button) with a dashboard layout (floating sidebar
with search, filter chips, a progress ring, an atlas map of tiles and an
inspector panel). Colours come from the Eduka-Desktop theme: light mint and
cream backgrounds with the Eduka accent, or a deep teal palette for Eduka's
dark themes — never black.
"""
import math
from .qt import (Qt, Signal, QColor, QPointF, QRectF, QPainter, QPainterPath, QPen, QLinearGradient, QRadialGradient,
                 QFrame, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QFont)

def mix(a, b, t):
    a, b = QColor(a), QColor(b)
    return QColor(round(a.red() + (b.red() - a.red()) * t), round(a.green() + (b.green() - a.green()) * t), round(a.blue() + (b.blue() - a.blue()) * t))

def palette(accent="#00a879", dark=False):
    """Colour tokens for the stylesheet and painted widgets."""
    accent = QColor(accent if QColor(accent).isValid() else "#00a879")
    if dark:
        base = dict(bg1="#12302b", bg2="#1b2d38", surface="#1d3a36", surface2="#244540", border="#2f5650", text="#e6f2ee", muted="#9db8b0", side="#183632")
    else:
        base = dict(bg1="#e8f6ef", bg2="#fcf4e6", surface="#ffffff", surface2="#f4faf7", border="#dbe8e1", text="#1d3a33", muted="#66807a", side="#ffffff")
    base.update(accent=accent.name(), accent_dark=mix(accent, "#000000", 0.18).name(), accent_soft=mix(accent, base["surface"], 0.86).name(),
                accent_text="#ffffff", dark=dark)
    return base

# Tile colour pairs (start, end) — bright, friendly and readable with white text.
TILE_COLOURS = {
    "classroom": ("#12b886", "#087f5b"), "homework": ("#ffa94d", "#e8590c"), "exams": ("#9775fa", "#6741d9"),
    "timor": ("#f03e3e", "#f59f00"), "report": ("#4dabf7", "#1971c2"), "system": ("#f783ac", "#c2255c"),
}

class GradientTile(QFrame):
    """Large rounded tile with a colour gradient, a picture of LAFA and a
    small "Open" button — the overview cards of the lobby."""
    clicked = Signal()
    def __init__(self, title, value, caption, colours, pixmap=None, action="Open", parent=None):
        super().__init__(parent); self.colours = colours; self.pixmap = pixmap
        self.setObjectName("gradienttile"); self.setCursor(Qt.PointingHandCursor); self.setMinimumHeight(150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        v = QVBoxLayout(self); v.setContentsMargins(18, 14, 18, 14); v.setSpacing(2)
        self.title = QLabel(title); self.title.setObjectName("tiletitle"); v.addWidget(self.title); v.addStretch()
        self.value = QLabel(value); self.value.setObjectName("tilevalue"); self.value.setWordWrap(True); v.addWidget(self.value)
        row = QHBoxLayout(); self.caption = QLabel(caption); self.caption.setObjectName("tilecaption"); self.caption.setWordWrap(True); row.addWidget(self.caption, 1)
        self.button = QPushButton(action.replace("&", "&&")); self.button.setObjectName("tilebutton"); self.button.clicked.connect(self.clicked.emit); row.addWidget(self.button, 0, Qt.AlignBottom)
        v.addLayout(row)
    def set_text(self, value=None, caption=None):
        if value is not None: self.value.setText(value)
        if caption is not None: self.caption.setText(caption)
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        g = QLinearGradient(r.topLeft(), r.bottomRight()); g.setColorAt(0, QColor(self.colours[0])); g.setColorAt(1, QColor(self.colours[1]))
        path = QPainterPath(); path.addRoundedRect(r, 20, 20); p.fillPath(path, g)
        p.setClipPath(path)
        glow = QRadialGradient(QPointF(r.right() - 40, r.top() + 30), r.height() * 0.9)
        glow.setColorAt(0, QColor(255, 255, 255, 90)); glow.setColorAt(1, QColor(255, 255, 255, 0)); p.fillRect(r, glow)
        if self.pixmap is not None and not self.pixmap.isNull():
            size = min(int(r.height() * 0.78), 130); pix = self.pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            p.setOpacity(0.97); p.drawPixmap(int(r.right() - pix.width() - 6), int(r.top() + 4), pix); p.setOpacity(1)
        p.setClipping(False); p.setPen(QPen(QColor(255, 255, 255, 70), 1)); p.drawPath(path)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton: self.clicked.emit()

class RoundButton(QPushButton):
    """The big round action button under the lobby tiles."""
    def __init__(self, text, accent, parent=None):
        super().__init__(text.replace("&", "&&"), parent); self.accent = QColor(accent); self.setFixedSize(112, 112); self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("roundbutton")
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); r = QRectF(self.rect()).adjusted(4, 4, -4, -4)
        p.setPen(Qt.NoPen); p.setBrush(QColor(self.accent.red(), self.accent.green(), self.accent.blue(), 60)); p.drawEllipse(r)
        inner = r.adjusted(8, 8, -8, -8); g = QLinearGradient(inner.topLeft(), inner.bottomRight())
        g.setColorAt(0, mix(self.accent, "#ffffff", 0.25)); g.setColorAt(1, mix(self.accent, "#000000", 0.2 if not self.isDown() else 0.35))
        p.setBrush(g); p.drawEllipse(inner); p.setPen(QColor("#ffffff")); f = p.font(); f.setBold(True); f.setPixelSize(17); p.setFont(f)
        p.drawText(inner, Qt.AlignCenter | Qt.TextWordWrap, self.text().replace("&&", "&"))

class Ring(QWidget):
    """Progress ring: segments [(value 0..1, colour)], big centre text."""
    def __init__(self, size=150, parent=None):
        super().__init__(parent); self.setFixedSize(size, size); self.segments = []; self.value = ""; self.caption = ""; self.track = QColor("#dbe8e1"); self.text_colour = QColor("#1d3a33")
    def set_data(self, segments, value, caption):
        self.segments, self.value, self.caption = segments, value, caption; self.update()
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); w = self.width(); pen = max(10, w // 12)
        r = QRectF(pen / 2 + 2, pen / 2 + 2, w - pen - 4, w - pen - 4)
        p.setPen(QPen(self.track, pen, Qt.SolidLine, Qt.RoundCap)); p.drawArc(r, 0, 360 * 16)
        start = 90 * 16
        for value, colour in self.segments:
            span = -int(max(0.0, min(1.0, value)) * 360 * 16)
            if span:
                p.setPen(QPen(QColor(colour), pen, Qt.SolidLine, Qt.RoundCap)); p.drawArc(r, start, span); start += span
        p.setPen(self.text_colour); f = p.font(); f.setBold(True); f.setPixelSize(max(16, w // 5)); p.setFont(f)
        p.drawText(QRectF(0, w * 0.28, w, w * 0.3), Qt.AlignCenter, self.value)
        f.setBold(False); f.setPixelSize(max(9, w // 14)); p.setFont(f); p.setPen(QColor(self.text_colour.red(), self.text_colour.green(), self.text_colour.blue(), 170))
        p.drawText(QRectF(8, w * 0.56, w - 16, w * 0.2), Qt.AlignCenter | Qt.TextWordWrap, self.caption)

class AtlasTile(QFrame):
    """A coloured tile of the Timor-Leste atlas map (sized by importance)."""
    clicked = Signal(object)
    def __init__(self, item, colour, parent=None):
        super().__init__(parent); self.item = item; self.colour = QColor(colour); self.selected = False
        self.setObjectName("atlastile"); self.setCursor(Qt.PointingHandCursor); self.setMinimumHeight(86); self.setMinimumWidth(60)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        v = QVBoxLayout(self); v.setContentsMargins(12, 10, 12, 10); v.setSpacing(2)
        self.title = QLabel(item["title"]); self.title.setObjectName("atlastitle"); self.title.setWordWrap(True); v.addWidget(self.title)
        if item.get("when"):
            when = QLabel(item["when"]); when.setObjectName("atlaswhen"); v.addWidget(when)
        v.addStretch()
        if item.get("size", 1) >= 2 and (item.get("tile") or item.get("summary")):
            summary = QLabel(item.get("tile") or item["summary"]); summary.setObjectName("atlassummary"); summary.setWordWrap(True); v.addWidget(summary)
        for child in self.findChildren(QLabel):
            child.setMinimumWidth(1); child.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
    def set_selected(self, selected):
        self.selected = selected; self.update()
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); r = QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -1.5)
        g = QLinearGradient(r.topLeft(), r.bottomRight()); g.setColorAt(0, mix(self.colour, "#ffffff", 0.08)); g.setColorAt(1, mix(self.colour, "#000000", 0.18))
        path = QPainterPath(); path.addRoundedRect(r, 14, 14); p.fillPath(path, g)
        p.setPen(QPen(QColor("#ffffff") if self.selected else QColor(255, 255, 255, 60), 3 if self.selected else 1)); p.drawPath(path)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton: self.clicked.emit(self.item)

def chip(text, colour=None, checkable=True):
    b = QPushButton(text.replace("&", "&&")); b.setObjectName("filterchip"); b.setCheckable(checkable); b.setCursor(Qt.PointingHandCursor)
    if colour: b.setProperty("dot", colour)
    return b
