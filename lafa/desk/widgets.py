"""Shared painted widgets for Lafa Desktop 0.3 (glass cards, clay icons, charts).

All widgets read the theme tokens of their window (`window().tok`) so light and
dark themes switch without rebuilding. Keyboard: every clickable widget takes
focus, shows a focus ring and reacts to Enter/Space.
"""
import math
from datetime import date, timedelta

from ..qt import (Qt, Signal, QTimer, QSize, QRectF, QPointF, QRect, QPoint, QColor, QPainter, QPainterPath, QPen, QLinearGradient,
                  QFont, QFontMetrics, QPixmap, QWidget, QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout,
                  QLineEdit, QSizePolicy, QScrollArea, QToolTip, QLayout, QStyle, QApplication)
from .. import icons
from .theme import tokens as theme_tokens, clay_icon, accent, lighten, darken, ACCENTS, FONT_FAMILY

def tok_of(widget):
    win = widget.window() if widget is not None else None
    t = getattr(win, "tok", None)
    return t if isinstance(t, dict) else theme_tokens(False)

def qcolor(value):
    if isinstance(value, QColor): return QColor(value)
    s = str(value)
    if s.startswith("rgba("):
        parts = [p.strip() for p in s[5:-1].split(",")]
        c = QColor(int(parts[0]), int(parts[1]), int(parts[2])); c.setAlphaF(float(parts[3])); return c
    return QColor(s)

def label(text="", name=None, wrap=False, selectable=False):
    w = QLabel(text)
    if name: w.setObjectName(name)
    w.setWordWrap(wrap)
    if selectable: w.setTextInteractionFlags(Qt.TextSelectableByMouse)
    return w

def button(text, slot=None, kind=None, icon_name=None, tip=None):
    b = QPushButton(text)
    if kind: b.setObjectName(kind)
    b.setCursor(Qt.PointingHandCursor)
    if slot: b.clicked.connect(slot)
    if icon_name: b.setProperty("icon_name", icon_name); refresh_icon(b)
    if tip: b.setToolTip(tip); b.setAccessibleName(tip if not text else text)
    return b

def refresh_icon(b, color=None):
    name = b.property("icon_name")
    if not name: return
    t = tok_of(b)
    col = color or ("#ffffff" if b.objectName() == "primary" else t["primary"] if b.objectName() in ("ghost", "chip", "icon") else t["text"])
    b.setIcon(icons.icon(name, col)); b.setIconSize(QSize(18, 18))

def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0); w = item.widget()
        if w is not None: w.hide(); w.setParent(None); w.deleteLater()
        elif item.layout() is not None: clear_layout(item.layout())

# ------------------------------------------------------------------- cards
class Card(QFrame):
    """White glass card with a soft painted shadow (inside its own rect, so
    nothing is clipped) and 2 px border that changes colour on hover/focus."""
    SH = (6, 3, 6, 10)   # shadow room left, top, right, bottom
    def __init__(self, padding=18, radius=22, parent=None, clickable=False, tint=None, gradient=None):
        super().__init__(parent); self.radius = radius; self.clickable = clickable; self.tint = tint; self.gradient = gradient; self._hover = False
        self.setAttribute(Qt.WA_Hover, True)
        l, t, r, b = self.SH
        self.box = QVBoxLayout(self); self.box.setContentsMargins(l + padding, t + padding, r + padding, b + padding); self.box.setSpacing(10)
        if clickable: self.setFocusPolicy(Qt.StrongFocus); self.setCursor(Qt.PointingHandCursor)
    def card_rect(self):
        l, t, r, b = self.SH; return QRectF(self.rect()).adjusted(l, t, -r, -b)
    def enterEvent(self, e): self._hover = True; self.update(); super().enterEvent(e)
    def leaveEvent(self, e): self._hover = False; self.update(); super().leaveEvent(e)
    def focusInEvent(self, e): self.update(); super().focusInEvent(e)
    def focusOutEvent(self, e): self.update(); super().focusOutEvent(e)
    def paintEvent(self, event):
        t = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        rect = self.card_rect(); r = self.radius
        shadow = QColor(t["shadow"])
        for i in range(7):
            c = QColor(shadow); c.setAlpha(max(0, int(shadow.alpha() * (0.9 - i * 0.12))))
            p.setPen(Qt.NoPen); p.setBrush(c); g = i * 1.0
            p.drawRoundedRect(rect.adjusted(-g * 0.6 + 2, 2 + g * 0.5, g * 0.6 - 2, 2 + g * 0.9), r + g, r + g)
        if self.gradient:
            g = QLinearGradient(rect.topLeft(), rect.bottomRight())
            for i, c in enumerate(self.gradient): g.setColorAt(i / max(1, len(self.gradient) - 1), QColor(c))
            p.setBrush(g); p.setPen(Qt.NoPen); p.drawRoundedRect(rect, r, r)
            p.setBrush(QColor(255, 255, 255, 40)); p.drawEllipse(QPointF(rect.right() - rect.width() * 0.12, rect.top() + rect.height() * 0.1), rect.height() * 0.55, rect.height() * 0.55)
            if self.clickable and (self._hover or self.hasFocus()):
                pen = QPen(QColor(255, 255, 255, 200)); pen.setWidthF(2.0); p.setPen(pen); p.setBrush(Qt.NoBrush); p.drawRoundedRect(rect.adjusted(1, 1, -1, -1), r, r)
            return
        fill = qcolor(t["glass"])
        if self.tint:
            tint = QColor(self.tint); tint.setAlpha(255 if not t["dark"] else 60); fill = tint
        if self.clickable and self._hover: fill = qcolor(t["card_hover"]) if not self.tint else lighten(fill, 0.25)
        p.setBrush(fill)
        border = qcolor(t["glass_border"])
        if self.clickable and (self._hover or self.hasFocus()): border = QColor(t["focus"] if self.hasFocus() else t["primary"]); border.setAlpha(255 if self.hasFocus() else 140)
        pen = QPen(border); pen.setWidthF(2.0); p.setPen(pen)
        p.drawRoundedRect(rect.adjusted(1, 1, -1, -1), r, r)

class Clickable(Card):
    clicked = Signal()
    def __init__(self, padding=16, radius=22, parent=None, tint=None, gradient=None):
        super().__init__(padding, radius, parent, clickable=True, tint=tint, gradient=gradient)
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.rect().contains(e.pos()): self.clicked.emit()
        super().mouseReleaseEvent(e)
    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space): self.clicked.emit(); return
        super().keyPressEvent(e)

class ClayIcon(QLabel):
    def __init__(self, name, accent_key="violet", size=48, parent=None):
        super().__init__(parent); self.name = name; self.accent_key = accent_key; self.size_ = size
        self.setFixedSize(size, size); self.setAttribute(Qt.WA_TransparentForMouseEvents); self.refresh()
    def refresh(self):
        color = ACCENTS.get(self.accent_key, (self.accent_key,))[0]
        self.setPixmap(clay_icon(self.name, color, self.size_))

class Pill(QLabel):
    def __init__(self, text, accent_key="violet", parent=None):
        super().__init__(text, parent); self.setObjectName("pill"); self.accent_key = accent_key; self.restyle()
    def restyle(self):
        strong, soft = accent(self.accent_key); t = tok_of(self)
        if t["dark"]: soft = darken(QColor(strong), 0.62).name(); strong = lighten(QColor(strong), 0.35).name()
        self.setStyleSheet(f"background:{soft}; color:{darken(QColor(strong), 0.18).name() if not t['dark'] else strong};")

class ProgressLine(QWidget):
    """Rounded progress bar with a violet→pink gradient (reference image 3)."""
    def __init__(self, value=0.0, height=10, parent=None, colors=None):
        super().__init__(parent); self.value = value; self.colors = colors; self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    def set_value(self, v): self.value = max(0.0, min(1.0, float(v))); self.update()
    def paintEvent(self, e):
        t = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); r = self.height() / 2
        p.setPen(Qt.NoPen); p.setBrush(qcolor(t["track"])); p.drawRoundedRect(QRectF(self.rect()), r, r)
        if self.value > 0:
            w = max(self.height(), self.width() * self.value); g = QLinearGradient(0, 0, w, 0)
            a, b = self.colors or (t["nav_a"], t["nav_b"]); g.setColorAt(0, QColor(a)); g.setColorAt(1, QColor(b))
            p.setBrush(g); p.drawRoundedRect(QRectF(0, 0, w, self.height()), r, r)

class ProgressRing(QWidget):
    def __init__(self, value=0.0, size=120, width=12, text="", caption="", parent=None, colors=None):
        super().__init__(parent); self.value = value; self.width_ = width; self.text = text; self.caption = caption; self.colors = colors
        self.setFixedSize(size, size)
    def set_value(self, v, text=None):
        self.value = max(0.0, min(1.0, float(v)))
        if text is not None: self.text = text
        self.update()
    def paintEvent(self, e):
        t = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        m = self.width_ / 2 + 2; rect = QRectF(self.rect()).adjusted(m, m, -m, -m)
        pen = QPen(qcolor(t["track"])); pen.setWidthF(self.width_); pen.setCapStyle(Qt.RoundCap); p.setPen(pen); p.drawArc(rect, 0, 360 * 16)
        if self.value > 0:
            a, b = self.colors or (t["nav_a"], t["nav_b"]); g = QLinearGradient(rect.topLeft(), rect.bottomRight()); g.setColorAt(0, QColor(a)); g.setColorAt(1, QColor(b))
            pen = QPen(g, self.width_); pen.setCapStyle(Qt.RoundCap); p.setPen(pen); p.drawArc(rect, 90 * 16, -int(360 * 16 * self.value))
        p.setPen(QColor(t["text"])); f = QFont(FONT_FAMILY); f.setPixelSize(max(12, int(self.height() * 0.2))); f.setWeight(QFont.ExtraBold); p.setFont(f)
        p.drawText(rect.adjusted(0, -8 if self.caption else 0, 0, 0), Qt.AlignCenter, self.text or f"{round(self.value * 100)}%")
        if self.caption:
            f.setPixelSize(max(10, int(self.height() * 0.09))); f.setWeight(QFont.DemiBold); p.setFont(f); p.setPen(QColor(t["muted"]))
            p.drawText(rect.adjusted(0, self.height() * 0.22, 0, 0), Qt.AlignCenter, self.caption)

class CountLabel(QLabel):
    """A number that counts up when shown (skipped with reduce motion)."""
    def __init__(self, value=0, suffix="", parent=None, animate=True):
        super().__init__(parent); self.setObjectName("kpi"); self.target = value; self.suffix = suffix; self.shown = 0
        self.timer = QTimer(self); self.timer.setInterval(16); self.timer.timeout.connect(self.step); self.animate = animate
        self.setText(self.fmt(value if not animate else 0))
    def fmt(self, v):
        return (f"{int(round(v)):,}".replace(",", " ") if isinstance(self.target, int) else f"{v:.1f}") + self.suffix
    def set_value(self, v):
        self.target = v
        if self.animate and self.isVisible(): self.shown = 0; self.timer.start()
        else: self.setText(self.fmt(v))
    def showEvent(self, e):
        super().showEvent(e)
        if self.animate and self.shown != self.target: self.shown = 0; self.timer.start()
    def step(self):
        diff = self.target - self.shown
        if abs(diff) < max(1, abs(self.target) * 0.01): self.shown = self.target; self.timer.stop()
        else: self.shown += diff * 0.18
        self.setText(self.fmt(self.shown))

class StatCard(Clickable):
    """Clay icon, title, big number and a small note (reference image 1)."""
    def __init__(self, icon_name, accent_key, title, value, note="", parent=None, animate=True):
        super().__init__(14, 22, parent, tint=None)
        row = QHBoxLayout(); row.setSpacing(14); self.icon = ClayIcon(icon_name, accent_key, 56); row.addWidget(self.icon, 0, Qt.AlignTop)
        col = QVBoxLayout(); col.setSpacing(0); self.title = label(title, "muted"); col.addWidget(self.title)
        self.value = CountLabel(value, animate=animate); col.addWidget(self.value)
        self.note = label(note, "caption", wrap=True); col.addWidget(self.note); col.addStretch(); row.addLayout(col, 1)
        self.box.addLayout(row)
        self.setAccessibleName(f"{title}: {value}")

class Segmented(QFrame):
    """Pill segmented control (Loron / Semana / Fulan style, reference image 3)."""
    changed = Signal(str)
    def __init__(self, options, current=None, parent=None):
        super().__init__(parent); self.setObjectName("segmented"); self.buttons = {}
        row = QHBoxLayout(self); row.setContentsMargins(3, 3, 3, 3); row.setSpacing(2)
        for key, text in options:
            b = QPushButton(text); b.setObjectName("segment"); b.setCheckable(True); b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda checked=False, k=key: self.select(k, emit=True)); row.addWidget(b); self.buttons[key] = b
        self.current = None; self.select(current or (options[0][0] if options else None))
    def select(self, key, emit=False):
        if key not in self.buttons: return
        self.current = key
        for k, b in self.buttons.items(): b.setChecked(k == key)
        if emit: self.changed.emit(key)

class SearchBox(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent); self.setObjectName("search"); self.setPlaceholderText(placeholder); self.setClearButtonEnabled(True)
        self.setAccessibleName(placeholder); self._action = None; self.refresh()
    def refresh(self):
        if self._action is not None: self.removeAction(self._action)
        self._action = self.addAction(icons.icon("search", tok_of(self)["muted"]), QLineEdit.LeadingPosition)

class NavButton(QPushButton):
    def __init__(self, icon_name, accent_key, text, parent=None):
        super().__init__(text, parent); self.setObjectName("nav"); self.setCheckable(True); self.setCursor(Qt.PointingHandCursor)
        self.icon_name = icon_name; self.accent_key = accent_key; self.full = text; self.setAccessibleName(text); self.setToolTip(text)
        self.setIconSize(QSize(30, 30)); self.setMinimumHeight(48); self.refresh()
        self.toggled.connect(lambda _=False: self.refresh())
    def refresh(self):
        self.setIcon(icons_from_pixmap(clay_icon(self.icon_name, ACCENTS[self.accent_key][0], 30)))
    def set_compact(self, compact):
        self.setText("" if compact else "  " + self.full); self.setStyleSheet("text-align:center; padding:8px 4px;" if compact else "")

def icons_from_pixmap(pm):
    from ..qt import QIcon
    icon = QIcon(); icon.addPixmap(pm); return icon

class ListRow(Clickable):
    """A list row like the task list in reference image 1: status, title, pills, meta, chevron."""
    def __init__(self, title, subtitle="", pills=(), meta="", done=False, icon_name=None, accent_key="violet", parent=None, thumb=None):
        super().__init__(10, 18, parent)
        row = QHBoxLayout(); row.setSpacing(12)
        if thumb is not None:
            pic = QLabel(); pic.setPixmap(thumb); pic.setFixedSize(thumb.width() / max(1, thumb.devicePixelRatio()), thumb.height() / max(1, thumb.devicePixelRatio())); row.addWidget(pic)
        elif icon_name: row.addWidget(ClayIcon(icon_name, accent_key, 40))
        status = QLabel(); status.setFixedSize(22, 22); status.setPixmap(icons.pixmap("check", "#ffffff", 14) if done else QPixmap())
        status.setAlignment(Qt.AlignCenter)
        t = tok_of(self)
        status.setStyleSheet(f"border-radius:11px; background:{t['ok'] if done else 'transparent'}; border:2px solid {t['ok'] if done else t['line']};")
        status.setToolTip("✓" if done else ""); self.status = status
        col = QVBoxLayout(); col.setSpacing(2); self.title_label = label(title, "h3", wrap=True); col.addWidget(self.title_label)
        if subtitle: col.addWidget(label(subtitle, "caption", wrap=True))
        row.addLayout(col, 1)
        for text, key in pills: row.addWidget(Pill(text, key), 0, Qt.AlignVCenter)
        if meta: m = label(meta, "caption"); row.addWidget(m, 0, Qt.AlignVCenter)
        row.addWidget(status, 0, Qt.AlignVCenter)
        chev = QLabel(); chev.setPixmap(icons.pixmap("chevron-right", t["muted"], 18)); row.addWidget(chev, 0, Qt.AlignVCenter)
        self.box.addLayout(row); self.setAccessibleName(title)

class CourseCard(Clickable):
    """Course card with a big clay tile, title, meta and progress bar (reference image 3)."""
    def __init__(self, icon_name, accent_key, title, meta, value, parent=None):
        super().__init__(14, 22, parent)
        row = QHBoxLayout(); row.setSpacing(16); row.addWidget(ClayIcon(icon_name, accent_key, 64))
        col = QVBoxLayout(); col.setSpacing(6); col.addWidget(label(title, "h3", wrap=True)); col.addWidget(label(meta, "caption", wrap=True))
        self.bar = ProgressLine(value, 8); col.addWidget(self.bar); row.addLayout(col, 1); self.box.addLayout(row)
        self.setAccessibleName(title)

class Banner(QWidget):
    """An illustration, cover-cropped with rounded corners, optional dark fade and title."""
    def __init__(self, pixmap_fn, height=180, radius=22, title="", subtitle="", parent=None):
        super().__init__(parent); self.pixmap_fn = pixmap_fn; self.radius = radius; self.title = title; self.subtitle = subtitle
        self.setFixedHeight(height); self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed); self._cache = None
    def resizeEvent(self, e): self._cache = None; super().resizeEvent(e)
    def paintEvent(self, e):
        if self._cache is None or self._cache.size() != self.size() * self.devicePixelRatioF():
            self._cache = self.pixmap_fn(self.width(), self.height())
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); path = QPainterPath(); path.addRoundedRect(QRectF(self.rect()), self.radius, self.radius)
        p.setClipPath(path)
        if self._cache is not None and not self._cache.isNull(): p.drawPixmap(self.rect(), self._cache)
        if self.title:
            g = QLinearGradient(0, self.height() * 0.35, 0, self.height()); g.setColorAt(0, QColor(20, 10, 50, 0)); g.setColorAt(1, QColor(20, 10, 50, 170))
            p.fillRect(self.rect(), g); p.setPen(QColor("#ffffff"))
            f = QFont(FONT_FAMILY); f.setPixelSize(26); f.setWeight(QFont.ExtraBold); p.setFont(f)
            p.drawText(QRectF(22, 0, self.width() - 44, self.height() - (40 if self.subtitle else 18)), Qt.AlignLeft | Qt.AlignBottom | Qt.TextWordWrap, self.title)
            if self.subtitle:
                f.setPixelSize(14); f.setWeight(QFont.DemiBold); p.setFont(f)
                p.drawText(QRectF(22, 0, self.width() - 44, self.height() - 16), Qt.AlignLeft | Qt.AlignBottom, self.subtitle)

# ------------------------------------------------------------------ charts
class Donut(QWidget):
    """Donut chart (reference images 1 and 2): segments [(label, value, colour)]."""
    def __init__(self, segments=(), center="", caption="", size=170, parent=None):
        super().__init__(parent); self.segments = list(segments); self.center = center; self.caption = caption; self.setFixedSize(size, size)
        self.setMouseTracking(True); self.hover = -1
    def set_segments(self, segments, center=None):
        self.segments = list(segments)
        if center is not None: self.center = center
        self.update()
    def _angles(self):
        total = sum(max(0, v) for _, v, _ in self.segments) or 1; start = 90.0; out = []
        for lbl, v, c in self.segments:
            span = 360.0 * max(0, v) / total; out.append((start, span, lbl, v, c)); start -= span
        return out
    def mouseMoveEvent(self, e):
        c = QPointF(self.width() / 2, self.height() / 2); d = e.pos() - c; ang = (math.degrees(math.atan2(-d.y(), d.x())) + 360) % 360
        r = math.hypot(d.x(), d.y()); outer = self.width() / 2 - 4; inner = outer * 0.58; idx = -1
        if inner <= r <= outer:
            for i, (start, span, lbl, v, col) in enumerate(self._angles()):
                a0 = (start - span) % 360; a1 = start % 360
                inside = (a0 <= ang <= a1) if a0 <= a1 else (ang >= a0 or ang <= a1)
                if inside and span > 0: idx = i; QToolTip.showText(e.globalPos(), f"{lbl}: {v:g}", self)
        if idx != self.hover: self.hover = idx; self.update()
    def leaveEvent(self, e): self.hover = -1; self.update()
    def paintEvent(self, e):
        t = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        outer = QRectF(self.rect()).adjusted(6, 6, -6, -6); w = outer.width() * 0.2
        for i, (start, span, lbl, v, col) in enumerate(self._angles()):
            if span <= 0: continue
            rect = outer.adjusted(w / 2, w / 2, -w / 2, -w / 2)
            if i == self.hover: rect = rect.adjusted(-3, -3, 3, 3)
            g = QLinearGradient(rect.topLeft(), rect.bottomRight()); g.setColorAt(0, lighten(QColor(col), 0.25)); g.setColorAt(1, QColor(col))
            pen = QPen(g, w); pen.setCapStyle(Qt.FlatCap); p.setPen(pen)
            p.drawArc(rect, int(start * 16), int(-max(0.5, span - 1.2) * 16))
        p.setPen(QColor(t["text"])); f = QFont(FONT_FAMILY); f.setPixelSize(int(self.height() * 0.15)); f.setWeight(QFont.ExtraBold); p.setFont(f)
        p.drawText(QRectF(self.rect()).adjusted(0, -10 if self.caption else 0, 0, 0), Qt.AlignCenter, self.center)
        if self.caption:
            f.setPixelSize(max(10, int(self.height() * 0.075))); f.setWeight(QFont.DemiBold); p.setFont(f); p.setPen(QColor(t["muted"]))
            p.drawText(QRectF(self.rect()).adjusted(10, self.height() * 0.2, -10, 0), Qt.AlignCenter, self.caption)

def legend(segments, fmt=lambda v: f"{v:g}"):
    w = QWidget(); col = QVBoxLayout(w); col.setContentsMargins(0, 0, 0, 0); col.setSpacing(6)
    for lbl, v, c in segments:
        row = QHBoxLayout(); dot = QLabel(); dot.setFixedSize(12, 12); dot.setStyleSheet(f"background:{c}; border-radius:6px;")
        row.addWidget(dot); row.addWidget(label(lbl), 1); row.addWidget(label(fmt(v), "caption")); col.addLayout(row)
    return w

class AreaChart(QWidget):
    """Smooth area chart with points and a hover bubble (reference image 1)."""
    def __init__(self, points=(), color=None, parent=None, fmt=None, height=200):
        super().__init__(parent); self.points = list(points); self.color = color; self.fmt = fmt or (lambda v: f"{v:,.0f}".replace(",", " "))
        self.setMinimumHeight(height); self.setMouseTracking(True); self.hover = -1
    def set_points(self, points): self.points = list(points); self.update()
    def _geometry(self):
        m = (44, 16, 16, 28); r = QRectF(self.rect()).adjusted(m[0], m[1], -m[2], -m[3])
        vals = [v for _, v in self.points] or [0]; lo = 0 if min(vals) >= 0 else min(vals); hi = max(vals) or 1
        n = len(self.points); xs = [r.left() + (r.width() * i / max(1, n - 1)) for i in range(n)]
        ys = [r.bottom() - (v - lo) / ((hi - lo) or 1) * r.height() for _, v in self.points]
        return r, xs, ys, lo, hi
    def mouseMoveEvent(self, e):
        if not self.points: return
        r, xs, ys, lo, hi = self._geometry(); idx = min(range(len(xs)), key=lambda i: abs(xs[i] - e.pos().x()))
        if idx != self.hover: self.hover = idx; self.update()
    def leaveEvent(self, e): self.hover = -1; self.update()
    def paintEvent(self, e):
        if len(self.points) < 2: return
        t = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        r, xs, ys, lo, hi = self._geometry(); col = QColor(self.color or t["primary"])
        f = QFont(FONT_FAMILY); f.setPixelSize(11); f.setWeight(QFont.DemiBold); p.setFont(f)
        grid = qcolor(t["line"])
        for i in range(4):
            y = r.bottom() - r.height() * i / 3; p.setPen(QPen(grid, 1, Qt.DashLine)); p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))
            p.setPen(QColor(t["muted"])); v = lo + (hi - lo) * i / 3; p.drawText(QRectF(0, y - 8, r.left() - 6, 16), Qt.AlignRight | Qt.AlignVCenter, compact_number(v))
        path = QPainterPath(QPointF(xs[0], ys[0]))
        for i in range(1, len(xs)):
            x0, y0, x1, y1 = xs[i - 1], ys[i - 1], xs[i], ys[i]; cx = (x1 - x0) / 2
            path.cubicTo(QPointF(x0 + cx, y0), QPointF(x1 - cx, y1), QPointF(x1, y1))
        fill = QPainterPath(path); fill.lineTo(xs[-1], r.bottom()); fill.lineTo(xs[0], r.bottom()); fill.closeSubpath()
        g = QLinearGradient(0, r.top(), 0, r.bottom()); top = QColor(col); top.setAlpha(110); bot = QColor(col); bot.setAlpha(8)
        g.setColorAt(0, top); g.setColorAt(1, bot); p.fillPath(fill, g)
        p.setPen(QPen(col, 3)); p.setBrush(Qt.NoBrush); p.drawPath(path)
        step = max(1, len(xs) // 8)
        for i, (x, y) in enumerate(zip(xs, ys)):
            if i % step == 0 or i == len(xs) - 1:
                p.setPen(QColor(t["muted"])); p.drawText(QRectF(x - 30, r.bottom() + 6, 60, 18), Qt.AlignCenter, str(self.points[i][0]))
            p.setPen(QPen(QColor("#ffffff"), 2)); p.setBrush(col); rad = 6 if i == self.hover else 4; p.drawEllipse(QPointF(x, y), rad, rad)
        if 0 <= self.hover < len(xs):
            x, y = xs[self.hover], ys[self.hover]; txt = f"{self.points[self.hover][0]}: {self.fmt(self.points[self.hover][1])}"
            fm = QFontMetrics(f); w = fm.horizontalAdvance(txt) + 18 if hasattr(fm, "horizontalAdvance") else fm.width(txt) + 18
            box = QRectF(min(max(r.left(), x - w / 2), r.right() - w), max(0, y - 40), w, 28)
            p.setPen(Qt.NoPen); p.setBrush(qcolor(t["glass_solid"])); p.drawRoundedRect(box, 10, 10)
            p.setPen(QColor(t["text"])); p.drawText(box, Qt.AlignCenter, txt)

def compact_number(v):
    a = abs(v)
    if a >= 1e9: return f"{v / 1e9:.1f}B"
    if a >= 1e6: return f"{v / 1e6:.1f}M"
    if a >= 1e3: return f"{v / 1e3:.0f}k"
    return f"{v:.0f}"

class BarChart(QWidget):
    """Rounded gradient bars (reference image 3)."""
    def __init__(self, bars=(), parent=None, height=180, fmt=None):
        super().__init__(parent); self.bars = list(bars); self.setMinimumHeight(height); self.setMouseTracking(True); self.hover = -1
        self.fmt = fmt or (lambda v: f"{v:g}")
    def set_bars(self, bars): self.bars = list(bars); self.update()
    def _rects(self):
        r = QRectF(self.rect()).adjusted(8, 10, -8, -26); n = len(self.bars) or 1; slot = r.width() / n; w = min(26, slot * 0.5)
        hi = max([v for _, v in self.bars] or [1]) or 1
        return [(QRectF(r.left() + slot * i + (slot - w) / 2, r.bottom() - r.height() * v / hi, w, r.height() * v / hi), r, i) for i, (_, v) in enumerate(self.bars)]
    def mouseMoveEvent(self, e):
        idx = next((i for rect, r, i in self._rects() if rect.adjusted(-8, -400, 8, 0).contains(QPointF(e.pos()))), -1)
        if idx != self.hover:
            self.hover = idx; self.update()
            if idx >= 0: QToolTip.showText(e.globalPos(), f"{self.bars[idx][0]}: {self.fmt(self.bars[idx][1])}", self)
    def leaveEvent(self, e): self.hover = -1; self.update()
    def paintEvent(self, e):
        t = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        f = QFont(FONT_FAMILY); f.setPixelSize(11); f.setWeight(QFont.DemiBold); p.setFont(f)
        for rect, area, i in self._rects():
            track = QRectF(rect.left(), area.top(), rect.width(), area.height()); p.setPen(Qt.NoPen); p.setBrush(qcolor(t["track"]))
            p.drawRoundedRect(track, rect.width() / 2, rect.width() / 2)
            g = QLinearGradient(rect.topLeft(), rect.bottomLeft()); g.setColorAt(0, QColor(t["nav_b"])); g.setColorAt(1, QColor(t["nav_a"]))
            p.setBrush(g)
            if rect.height() > 0: p.drawRoundedRect(rect, rect.width() / 2, rect.width() / 2)
            p.setPen(QColor(t["text"] if i == self.hover else t["muted"])); p.drawText(QRectF(rect.center().x() - 30, area.bottom() + 6, 60, 18), Qt.AlignCenter, str(self.bars[i][0]))

class CalendarCard(QWidget):
    """Month calendar with marked days (reference image 1). marks: {date: (accent, tooltip)}."""
    day_clicked = Signal(object)
    def __init__(self, lang="en", parent=None):
        super().__init__(parent); self.lang = lang; self.month = date.today().replace(day=1); self.marks = {}; self.selected = date.today()
        self.setMinimumSize(280, 260); self.setMouseTracking(True); self.hover = None; self.setFocusPolicy(Qt.StrongFocus)
    def set_marks(self, marks): self.marks = dict(marks); self.update()
    def go(self, step):
        y, m = self.month.year, self.month.month + step
        while m < 1: m += 12; y -= 1
        while m > 12: m -= 12; y += 1
        self.month = date(y, m, 1); self.update()
    def _cells(self):
        top = 44; w = self.width() / 7; h = (self.height() - top - 26) / 6; first = self.month - timedelta(days=self.month.weekday())
        return [(first + timedelta(days=i), QRectF((i % 7) * w, top + 26 + (i // 7) * h, w, h)) for i in range(42)]
    def mouseMoveEvent(self, e):
        hit = next((d for d, r in self._cells() if r.contains(QPointF(e.pos()))), None)
        if hit != self.hover:
            self.hover = hit; self.update()
            if hit in self.marks: QToolTip.showText(e.globalPos(), self.marks[hit][1], self)
    def mousePressEvent(self, e):
        if e.pos().y() < 40:
            if e.pos().x() > self.width() - 40: self.go(1)
            elif e.pos().x() > self.width() - 80: self.go(-1)
            return
        hit = next((d for d, r in self._cells() if r.contains(QPointF(e.pos()))), None)
        if hit: self.selected = hit; self.update(); self.day_clicked.emit(hit)
    def keyPressEvent(self, e):
        moves = {Qt.Key_Left: -1, Qt.Key_Right: 1, Qt.Key_Up: -7, Qt.Key_Down: 7}
        if e.key() in moves:
            self.selected += timedelta(days=moves[e.key()])
            if self.selected.month != self.month.month or self.selected.year != self.month.year: self.month = self.selected.replace(day=1)
            self.update(); return
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space): self.day_clicked.emit(self.selected); return
        if e.key() == Qt.Key_PageUp: self.go(-1); return
        if e.key() == Qt.Key_PageDown: self.go(1); return
        super().keyPressEvent(e)
    def paintEvent(self, e):
        from ..kb import month_name, WEEKDAYS
        t = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        f = QFont(FONT_FAMILY); f.setPixelSize(16); f.setWeight(QFont.ExtraBold); p.setFont(f); p.setPen(QColor(t["text"]))
        p.drawText(QRectF(4, 4, self.width() - 90, 32), Qt.AlignLeft | Qt.AlignVCenter, f"{month_name(self.month.month, self.lang).capitalize()} {self.month.year}")
        for i, name in enumerate(("back", "chevron-right")):
            r = QRectF(self.width() - 76 + i * 38, 6, 30, 30); p.setPen(Qt.NoPen); p.setBrush(qcolor(t["track"])); p.drawRoundedRect(r, 10, 10)
            p.drawPixmap(QPointF(r.center().x() - 8, r.center().y() - 8), icons.pixmap(name, t["text"], 16))
        f.setPixelSize(11); f.setWeight(QFont.Bold); p.setFont(f); p.setPen(QColor(t["muted"])); w = self.width() / 7
        for i, name in enumerate(WEEKDAYS.get(self.lang, WEEKDAYS["en"])):
            p.drawText(QRectF(i * w, 44, w, 22), Qt.AlignCenter, name[:3])
        f.setPixelSize(13); f.setWeight(QFont.DemiBold); p.setFont(f); today = date.today()
        for d, r in self._cells():
            inside = d.month == self.month.month; c = r.center(); rad = min(r.width(), r.height()) * 0.40
            if d in self.marks:
                strong, soft = accent(self.marks[d][0]); p.setPen(Qt.NoPen); p.setBrush(QColor(soft if not t["dark"] else darken(QColor(strong), 0.55)))
                p.drawEllipse(c, rad, rad)
            if d == today:
                g = QLinearGradient(c - QPointF(rad, rad), c + QPointF(rad, rad)); g.setColorAt(0, QColor(t["nav_a"])); g.setColorAt(1, QColor(t["primary"]))
                p.setPen(Qt.NoPen); p.setBrush(g); p.drawEllipse(c, rad, rad)
            if d == self.selected and self.hasFocus() or d == self.hover:
                p.setPen(QPen(QColor(t["focus"]), 2)); p.setBrush(Qt.NoBrush); p.drawEllipse(c, rad + 1, rad + 1)
            p.setPen(QColor("#ffffff") if d == today else QColor(t["text"] if inside else t["muted"]))
            p.drawText(r, Qt.AlignCenter, str(d.day))
            if d in self.marks and d != today:
                strong, _ = accent(self.marks[d][0]); p.setPen(Qt.NoPen); p.setBrush(QColor(strong)); p.drawEllipse(QPointF(c.x(), c.y() + rad * 0.72), 2.2, 2.2)

# ------------------------------------------------------------------- layout
class ResponsiveGrid(QWidget):
    """Cards in as many columns as fit (no sideways scrolling)."""
    def __init__(self, min_width=260, max_columns=4, spacing=14, parent=None):
        super().__init__(parent); self.items = []; self.min_width = min_width; self.max_columns = max_columns; self.columns = 0
        self.grid = QGridLayout(self); self.grid.setContentsMargins(0, 0, 0, 0); self.grid.setSpacing(spacing); self.setMinimumWidth(min_width)
    def add(self, widget): self.items.append(widget); self.relayout(True)
    def clear(self):
        for w in self.items: self.grid.removeWidget(w); w.hide(); w.setParent(None); w.deleteLater()
        self.items = []; self.columns = 0
    def relayout(self, force=False):
        columns = max(1, min(self.max_columns, (self.width() + self.grid.spacing()) // (self.min_width + self.grid.spacing()))) if self.width() > 50 else self.max_columns
        if columns == self.columns and not force: return
        self.columns = columns
        for w in self.items: self.grid.removeWidget(w)
        for i, w in enumerate(self.items): self.grid.addWidget(w, i // columns, i % columns)
        for c in range(self.max_columns): self.grid.setColumnStretch(c, 1 if c < columns else 0)
    def resizeEvent(self, e): super().resizeEvent(e); self.relayout()

class FlowLayout(QLayout):
    """Wrapping row for chips and tags."""
    def __init__(self, parent=None, spacing=8):
        super().__init__(parent); self.items = []; self.setSpacing(spacing); self.setContentsMargins(0, 0, 0, 0)
    def addItem(self, item): self.items.append(item)
    def count(self): return len(self.items)
    def itemAt(self, i): return self.items[i] if 0 <= i < len(self.items) else None
    def takeAt(self, i): return self.items.pop(i) if 0 <= i < len(self.items) else None
    def expandingDirections(self): return Qt.Orientations(0)
    def hasHeightForWidth(self): return True
    def heightForWidth(self, width): return self._layout(QRect(0, 0, width, 0), True)
    def setGeometry(self, rect): super().setGeometry(rect); self._layout(rect, False)
    def sizeHint(self): return self.minimumSize()
    def minimumSize(self):
        size = QSize()
        for item in self.items: size = size.expandedTo(item.minimumSize())
        return size + QSize(2, 2)
    def _layout(self, rect, test):
        x, y, line = rect.x(), rect.y(), 0; sp = self.spacing()
        for item in self.items:
            w = item.sizeHint()
            if x + w.width() > rect.right() + 1 and line > 0: x = rect.x(); y += line + sp; line = 0
            if not test: item.setGeometry(QRect(QPoint(x, y), w))
            x += w.width() + sp; line = max(line, w.height())
        return y + line - rect.y()

def scroll(body, horizontal=False):
    area = QScrollArea(); area.setWidgetResizable(True); area.setFrameShape(QFrame.NoFrame)
    if not horizontal: area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    area.setWidget(body); return area

def section_title(text, action=None):
    row = QHBoxLayout(); row.setSpacing(8); row.addWidget(label(text, "h2"), 1)
    if action is not None: row.addWidget(action)
    return row

class EmptyState(QWidget):
    def __init__(self, icon_name, title, text="", parent=None):
        super().__init__(parent); col = QVBoxLayout(self); col.setAlignment(Qt.AlignCenter); col.setSpacing(8)
        col.addWidget(ClayIcon(icon_name, "lilac", 72), 0, Qt.AlignHCenter)
        t = label(title, "h3", wrap=True); t.setAlignment(Qt.AlignCenter); col.addWidget(t)
        if text: s = label(text, "muted", wrap=True); s.setAlignment(Qt.AlignCenter); col.addWidget(s)

class Toast(QLabel):
    """A short message at the bottom of the window (achievements, saved…)."""
    def __init__(self, parent):
        super().__init__(parent); self.setObjectName("toast"); self.hide(); self.setWordWrap(True); self.setAlignment(Qt.AlignCenter)
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.timeout.connect(self.hide)
    def show_text(self, text, ms=3200):
        t = tok_of(self)
        self.setStyleSheet(f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {t['nav_a']}, stop:1 {t['nav_b']}); color:white; border-radius:18px; padding:12px 18px; font-weight:800;")
        self.setText(text); self.setFixedWidth(min(460, self.parent().width() - 40)); self.adjustSize()
        self.move((self.parent().width() - self.width()) // 2, self.parent().height() - self.height() - 28); self.show(); self.raise_(); self.timer.start(ms)
