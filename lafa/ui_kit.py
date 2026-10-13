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
    if dark:
        base.update(glass_top="rgba(48,92,84,0.92)", glass="rgba(29,58,54,0.82)", glass_border="rgba(255,255,255,0.10)", scroll="rgba(255,255,255,0.22)")
    else:
        base.update(glass_top="rgba(255,255,255,0.97)", glass="rgba(255,255,255,0.80)", glass_border="rgba(255,255,255,0.95)", scroll="rgba(29,58,51,0.22)")
    return base

# Tile colour pairs (start, end) — bright, friendly and readable with white text.
TILE_COLOURS = {
    "classroom": ("#12b886", "#087f5b"), "homework": ("#ffa94d", "#e8590c"), "exams": ("#9775fa", "#6741d9"),
    "timor": ("#f03e3e", "#f59f00"), "report": ("#4dabf7", "#1971c2"), "system": ("#f783ac", "#c2255c"),
    "languages": ("#3bc9db", "#0c8599"), "library": ("#a9e34b", "#5c940d"),
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
            size = min(int(r.height() * 0.70), int(r.width() * 0.42), 120); pix = self.pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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

class SourceCard(QFrame):
    """A learning website: colour stripe for its category, name, address,
    description and a status dot (green = answered at the last hourly check)."""
    opened = Signal(str)
    def __init__(self, name, url, description, colour, state=None, parent=None):
        super().__init__(parent); self.url = url; self.colour = QColor(colour); self.state = state
        self.setObjectName("sourcecard"); self.setCursor(Qt.PointingHandCursor); self.setMinimumHeight(118)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        v = QVBoxLayout(self); v.setContentsMargins(18, 12, 14, 12); v.setSpacing(3)
        head = QHBoxLayout(); title = QLabel(name); title.setObjectName("sourcetitle"); head.addWidget(title, 1)
        self.dot = QLabel("●"); self.dot.setObjectName("sourcedot"); head.addWidget(self.dot); v.addLayout(head)
        host = QLabel(url.split("//", 1)[-1].rstrip("/")); host.setObjectName("sourcehost"); v.addWidget(host)
        body = QLabel(description); body.setObjectName("sourcedesc"); body.setWordWrap(True); v.addWidget(body); v.addStretch()
        for child in self.findChildren(QLabel): child.setMinimumWidth(1); child.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.set_state(state)
    def set_state(self, state):
        self.state = state
        self.dot.setStyleSheet("color:%s;" % {"up": "#2fb344", "down": "#e03131"}.get(state, "#adb5bd"))
    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); p.setPen(Qt.NoPen); p.setBrush(self.colour)
        p.drawRoundedRect(QRectF(0, 10, 6, self.height() - 20), 3, 3)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton: self.opened.emit(self.url)

# ------------------------------------------------------- aero + 3D helpers
from .qt import QGraphicsDropShadowEffect, QObject, QEvent, QPropertyAnimation, QEasingCurve, QPixmap, QIcon

def soft_shadow(widget, blur=22, dy=5, alpha=34, dark=False):
    """A gentle drop shadow: just enough depth (3D) without standing out."""
    effect = QGraphicsDropShadowEffect(widget); effect.setBlurRadius(blur); effect.setOffset(0, dy)
    effect.setColor(QColor(0, 0, 0, alpha + 30) if dark else QColor(20, 70, 60, alpha)); widget.setGraphicsEffect(effect); return effect

class SmoothWheel(QObject):
    """Animated mouse-wheel scrolling (ease-out) for a scroll area."""
    def __init__(self, area):
        super().__init__(area); self.area = area; self.target = None
        self.animation = QPropertyAnimation(area.verticalScrollBar(), b"value", self)
        self.animation.setDuration(220); self.animation.setEasingCurve(QEasingCurve.OutCubic)
        area.viewport().installEventFilter(self)
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel and not event.modifiers():
            bar = self.area.verticalScrollBar(); delta = event.angleDelta().y()
            if not delta or bar.maximum() == 0: return False
            start = self.target if self.animation.state() == QPropertyAnimation.Running and self.target is not None else bar.value()
            self.target = max(bar.minimum(), min(bar.maximum(), start - int(delta * 0.9)))
            self.animation.stop(); self.animation.setStartValue(bar.value()); self.animation.setEndValue(self.target); self.animation.start()
            return True
        return False

def smooth_scroll(area):
    area.setFrameShape(QFrame.NoFrame); area.smooth_wheel = SmoothWheel(area); return area

class AeroBackground(QWidget):
    """Window background: soft gradient with blurred colour glows (aero glass)."""
    def __init__(self, tokens, parent=None):
        super().__init__(parent); self.tokens = tokens; self.setObjectName("root"); self.setAttribute(Qt.WA_StyledBackground, False)
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); r = QRectF(self.rect())
        g = QLinearGradient(r.topLeft(), r.bottomRight()); g.setColorAt(0, QColor(self.tokens["bg1"])); g.setColorAt(1, QColor(self.tokens["bg2"])); p.fillRect(r, g)
        for cx, cy, radius, colour, alpha in ((0.88, 0.06, 0.42, self.tokens["accent"], 55), (0.12, 0.95, 0.38, "#f2b632", 45), (0.55, 0.55, 0.30, "#4dabf7", 22)):
            glow = QRadialGradient(QPointF(r.width() * cx, r.height() * cy), max(r.width(), r.height()) * radius)
            c = QColor(colour); c.setAlpha(alpha if not self.tokens["dark"] else alpha // 2); glow.setColorAt(0, c); c2 = QColor(colour); c2.setAlpha(0); glow.setColorAt(1, c2)
            p.fillRect(r, glow)

# One colour per menu entry so the sidebar is colourful and easy to scan.
NAV_COLOURS = {"home": "#12b886", "classroom": "#20c997", "teachers": "#4dabf7", "exams": "#9775fa", "report": "#339af0", "homework": "#ff922b",
               "culture": "#f03e3e", "languages": "#e64980", "learn": "#f59f00", "coding": "#15aabf", "live": "#74c0fc", "hub": "#845ef7",
               "chat": "#38d9a9", "os_help": "#5c7cfa", "files": "#fab005", "reminders": "#ff6b6b"}

def nav_badge(icon, colour, size=26):
    """Rounded colourful badge with the theme icon (or a glyph) on top."""
    pix = QPixmap(size * 2, size * 2); pix.fill(Qt.transparent); p = QPainter(pix); p.setRenderHint(QPainter.Antialiasing)
    r = QRectF(0, 0, size * 2, size * 2).adjusted(2, 2, -2, -2); g = QLinearGradient(r.topLeft(), r.bottomRight())
    base = QColor(colour); g.setColorAt(0, mix(base, "#ffffff", 0.25)); g.setColorAt(1, mix(base, "#000000", 0.08))
    path = QPainterPath(); path.addRoundedRect(r, size * 0.55, size * 0.55); p.fillPath(path, g)
    p.setPen(QPen(QColor(255, 255, 255, 120), 2)); p.drawPath(path)
    if isinstance(icon, QIcon) and not icon.isNull():
        inner = icon.pixmap(int(size * 1.2), int(size * 1.2)); p.drawPixmap(int((size * 2 - inner.width()) / 2), int((size * 2 - inner.height()) / 2), inner)
    elif isinstance(icon, str):
        f = p.font(); f.setPixelSize(int(size * 1.0)); f.setBold(True); p.setFont(f); p.setPen(QColor("#ffffff")); p.drawText(r, Qt.AlignCenter, icon)
    p.end(); pix.setDevicePixelRatio(2.0); return QIcon(pix)
