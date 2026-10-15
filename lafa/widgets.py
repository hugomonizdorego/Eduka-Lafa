"""Shared components for Lafa Desktop (0.2.1 design).

Cards, the navigation bar (back · home · breadcrumb · context search),
illustrated category cards, topic rows, badges and empty states. They take
their colours from the theme tokens (ui_kit.palette) and their icons from
lafa/icons.py, so every page looks the same in the light and dark themes.

Keyboard: every clickable card takes focus (Tab) and opens with Enter or
Space; the focus ring and the hover state only change the border colour, so
nothing moves when the pointer passes over it.
"""
import html
from .qt import (Qt, Signal, QFrame, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy,
                 QPainter, QPainterPath, QRectF, QColor, QPixmap, QSize, QAction, QIcon)
from . import icons

def tokens_of(widget):
    """Theme tokens of the window that owns a widget (light defaults otherwise)."""
    win = widget.window() if widget else None
    tok = getattr(win, "tokens", None)
    if isinstance(tok, dict): return tok
    from .ui_kit import palette
    return palette()

def icon_colour(tokens, strong=False):
    return tokens.get("accent_strong" if strong else "text", tokens.get("text", "#17322b"))

class IconButton(QPushButton):
    """A square button with one of Lafa's icons and an accessible name."""
    def __init__(self, name, tooltip, tokens, size=36, parent=None):
        super().__init__(parent); self.setObjectName("iconbutton"); self.setFixedSize(size, size)
        self.setIcon(icons.icon(name, icon_colour(tokens))); self.setIconSize(QSize(int(size * 0.55), int(size * 0.55)))
        self.setToolTip(tooltip); self.setAccessibleName(tooltip); self.setCursor(Qt.PointingHandCursor)

class Badge(QLabel):
    """A small pill: "Offline material", "Needs internet", a status…"""
    def __init__(self, text, kind="ok", icon_name=None, tokens=None, parent=None):
        super().__init__(parent); self.setObjectName("badge_" + kind)
        tok = tokens or {}
        mark = ""
        if icon_name and icons.exists(icon_name):
            colour = {"ok": tok.get("accent_strong", "#0a7350"), "net": tok.get("warn_text", "#8a5a00"), "info": tok.get("muted", "#5d716a")}.get(kind, tok.get("text", "#17322b"))
            self.setTextFormat(Qt.RichText); mark = icon_html(icon_name, colour, 14) + "&nbsp;"
            super().setText(mark + html.escape(text))
        else: super().setText(text)
        self.setAccessibleName(text)

def icon_html(name, colour, size=16):
    """An inline icon for rich-text labels (data URI of the rendered SVG)."""
    from .qt import QBuffer, QByteArray, QIODevice
    pix = icons.pixmap(name, colour, size * 2)
    if pix.isNull(): return ""
    data = QByteArray(); buffer = QBuffer(data); buffer.open(QIODevice.WriteOnly); pix.save(buffer, "PNG"); buffer.close()
    return f'<img src="data:image/png;base64,{bytes(data.toBase64()).decode()}" width="{size}" height="{size}" style="vertical-align:middle">'

class Illustration(QWidget):
    """A Lafa illustration that fills its box (cropped in the centre), with
    rounded corners; repaints sharply at any size."""
    def __init__(self, name, radius=14, corners="all", parent=None):
        super().__init__(parent); self.name = name; self.radius = radius; self.corners = corners
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding); self.setMinimumSize(80, 45)
    def set_name(self, name):
        self.name = name; self.update()
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); r = QRectF(self.rect())
        path = QPainterPath(); rad = self.radius
        if self.corners == "top":
            path.moveTo(r.left(), r.bottom()); path.lineTo(r.left(), r.top() + rad); path.quadTo(r.left(), r.top(), r.left() + rad, r.top())
            path.lineTo(r.right() - rad, r.top()); path.quadTo(r.right(), r.top(), r.right(), r.top() + rad); path.lineTo(r.right(), r.bottom()); path.closeSubpath()
        else: path.addRoundedRect(r, rad, rad)
        p.setClipPath(path)
        pix = icons.illustration(self.name, max(1, self.width()), max(1, self.height()), self.devicePixelRatioF())
        if not pix.isNull(): p.drawPixmap(0, 0, pix)
        else: p.fillRect(r, QColor(tokens_of(self).get("accent_soft", "#e3f4ec")))

class Clickable(QFrame):
    """A focusable card that opens with a click, Enter or Space."""
    clicked = Signal()
    def __init__(self, object_name="enccard", parent=None):
        super().__init__(parent); self.setObjectName(object_name); self.setAttribute(Qt.WA_Hover, True)
        self.setFocusPolicy(Qt.StrongFocus); self.setCursor(Qt.PointingHandCursor)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rect().contains(event.pos()): self.clicked.emit()
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space): self.clicked.emit()
        else: super().keyPressEvent(event)

class CategoryCard(Clickable):
    """Picture on top, then the category icon, name, topic count and a chevron."""
    def __init__(self, illustration, icon_name, title, caption, tokens, parent=None):
        super().__init__("enccard", parent); self.setAccessibleName(title); self.setAccessibleDescription(caption)
        v = QVBoxLayout(self); v.setContentsMargins(2, 2, 2, 2); v.setSpacing(0)
        self.picture = Illustration(illustration, 14, "top"); self.picture.setMinimumHeight(110); v.addWidget(self.picture, 1)
        row = QHBoxLayout(); row.setContentsMargins(14, 10, 12, 12); row.setSpacing(10)
        mark = QLabel(); mark.setPixmap(icons.pixmap(icon_name, tokens.get("accent_strong", "#0a7350"), 26)); mark.setFixedSize(28, 28); row.addWidget(mark, 0, Qt.AlignTop)
        text = QVBoxLayout(); text.setSpacing(1)
        name = QLabel(title); name.setObjectName("cardtitle"); name.setWordWrap(True); text.addWidget(name)
        sub = QLabel(caption); sub.setObjectName("cardcaption"); sub.setWordWrap(True); text.addWidget(sub)
        row.addLayout(text, 1)
        chevron = QLabel(); chevron.setPixmap(icons.pixmap("chevron-right", tokens.get("muted", "#5d716a"), 18)); row.addWidget(chevron, 0, Qt.AlignVCenter)
        v.addLayout(row)
        self.setMinimumHeight(190); self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class Tile(Clickable):
    """A compact access tile (icon, title, small caption, optional badge)."""
    def __init__(self, icon_name, title, caption, tokens, badge=None, parent=None):
        super().__init__("enctile", parent); self.setAccessibleName(title)
        row = QHBoxLayout(self); row.setContentsMargins(14, 10, 14, 10); row.setSpacing(12)
        mark = QLabel(); mark.setPixmap(icons.pixmap(icon_name, tokens.get("accent_strong", "#0a7350"), 28)); row.addWidget(mark)
        text = QVBoxLayout(); text.setSpacing(0)
        name = QLabel(title); name.setObjectName("cardtitle"); text.addWidget(name)
        if caption: sub = QLabel(caption); sub.setObjectName("cardcaption"); sub.setWordWrap(True); text.addWidget(sub)
        row.addLayout(text, 1)
        if badge: row.addWidget(badge, 0, Qt.AlignVCenter)

class TopicRow(Clickable):
    """One topic in a list: thumbnail, title, when, summary and a chevron."""
    def __init__(self, illustration, title, summary, tokens, when="", status=None, parent=None):
        super().__init__("encrow", parent); self.setAccessibleName(title); self.setAccessibleDescription(summary)
        row = QHBoxLayout(self); row.setContentsMargins(8, 8, 12, 8); row.setSpacing(14)
        thumb = Illustration(illustration, 10); thumb.setFixedSize(112, 63); row.addWidget(thumb, 0, Qt.AlignTop)
        text = QVBoxLayout(); text.setSpacing(2)
        head = QHBoxLayout(); head.setSpacing(8)
        name = QLabel(title); name.setObjectName("rowtitle"); name.setWordWrap(True); head.addWidget(name, 1)
        if when: w = QLabel(when); w.setObjectName("rowwhen"); head.addWidget(w, 0, Qt.AlignTop)
        if status is not None: head.addWidget(status, 0, Qt.AlignTop)
        text.addLayout(head)
        short = summary if len(summary) <= 180 else summary[:177].rsplit(" ", 1)[0] + "…"
        sub = QLabel(short); sub.setObjectName("cardcaption"); sub.setWordWrap(True); text.addWidget(sub)
        row.addLayout(text, 1)
        chevron = QLabel(); chevron.setPixmap(icons.pixmap("chevron-right", tokens.get("muted", "#5d716a"), 18)); row.addWidget(chevron, 0, Qt.AlignVCenter)

class EmptyState(QWidget):
    """A calm message with an icon when there is nothing to show."""
    def __init__(self, icon_name, text, tokens, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self); v.setContentsMargins(20, 30, 20, 30); v.setSpacing(10); v.addStretch()
        mark = QLabel(); mark.setPixmap(icons.pixmap(icon_name, tokens.get("muted", "#5d716a"), 44)); mark.setAlignment(Qt.AlignCenter); v.addWidget(mark)
        msg = QLabel(text); msg.setObjectName("emptytext"); msg.setWordWrap(True); msg.setAlignment(Qt.AlignCenter); v.addWidget(msg); v.addStretch()

class NavBar(QFrame):
    """Back · Home · breadcrumb · search in this context."""
    back = Signal()
    home = Signal()
    crumb = Signal(int)
    search = Signal(str)
    def __init__(self, tokens, back_text, home_text, placeholder, parent=None):
        super().__init__(parent); self.setObjectName("navbar")
        row = QHBoxLayout(self); row.setContentsMargins(0, 0, 0, 0); row.setSpacing(8)
        self.back_button = IconButton("back", back_text, tokens); self.back_button.clicked.connect(self.back.emit); row.addWidget(self.back_button)
        self.home_button = IconButton("home", home_text, tokens); self.home_button.clicked.connect(self.home.emit); row.addWidget(self.home_button)
        self.trail = QLabel(); self.trail.setObjectName("breadcrumb"); self.trail.setTextFormat(Qt.RichText); self.trail.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.trail.setOpenExternalLinks(False); self.trail.linkActivated.connect(lambda link: self.crumb.emit(int(link)))
        self.trail.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred); self.trail.setMinimumWidth(80); row.addWidget(self.trail, 1)
        self.field = QLineEdit(); self.field.setObjectName("contextsearch"); self.field.setPlaceholderText(placeholder); self.field.setAccessibleName(placeholder)
        self.field.setMaxLength(120); self.field.setClearButtonEnabled(True); self.field.setMinimumWidth(180); self.field.setMaximumWidth(360)
        action = QAction(icons.icon("search", tokens.get("muted", "#5d716a")), "", self.field); self.field.addAction(action, QLineEdit.LeadingPosition)
        self.field.returnPressed.connect(lambda: self.search.emit(self.field.text().strip()))
        row.addWidget(self.field)
        self.tokens = tokens
    def set_trail(self, names):
        """names: list of crumbs; all but the last are links back to that level."""
        tok = self.tokens; parts = []
        for i, name in enumerate(names):
            safe = html.escape(name)
            if i < len(names) - 1: parts.append(f'<a href="{i}" style="color:{tok.get("muted", "#5d716a")};text-decoration:none">{safe}</a>')
            else: parts.append(f'<b style="color:{tok.get("text", "#17322b")}">{safe}</b>')
        sep = f' <span style="color:{tok.get("muted", "#5d716a")}">/</span> '
        self.trail.setText(sep.join(parts)); self.trail.setAccessibleName(" / ".join(names))
    def set_can_go_back(self, value):
        self.back_button.setEnabled(bool(value))
