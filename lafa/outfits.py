"""LAFA's outfits and the activities that suit each one.

* traditional - Tais Mane (default): school life, studying, daily life, Tebe-tebe and Bidu
* tuxedo      - formal: parties, meetings, presentations, ceremonies, gala dinners
* casual      - summer: beach, sightseeing, hanging out, shopping, snacks

An activity is a pose from the outfit's sprite sheet plus a small scene drawn
around LAFA (confetti, a meeting table, the beach…). Scenes are vector
drawings so they scale with LAFA's size and cost no extra assets.
"""
import math
from .qt import Qt, QColor, QPointF, QRectF, QPolygonF, QPen, QPainterPath, QPainter

OUTFITS = ["traditional", "tuxedo", "casual"]

# activity -> (pose, scene)
ACTIVITIES = {
    # Formal (tuxedo)
    "party": ("talking", "party"), "meeting": ("serious", "meeting"), "presentation": ("talking", "board"),
    "ceremony": ("idle", "stage"), "gala_dinner": ("eating", "dinner"), "report": ("reading", "papers"),
    "speech_prep": ("thinking", "podium"), "formal_walk": ("walking", "carpet"),
    # Casual (summer)
    "beach": ("sitting", "beach"), "sunbathing": ("sleeping", "beach"), "beach_ball": ("stretching", "beach_ball"),
    "sightseeing": ("walking", "city"), "hangout": ("talking", "cafe"), "shopping": ("walking", "shopping"),
    "snack": ("eating", "cafe"), "game_break": ("gaming", "cafe"),
}
FORMAL = ["party", "meeting", "presentation", "ceremony", "gala_dinner", "report", "speech_prep", "formal_walk"]
CASUAL = ["beach", "sunbathing", "beach_ball", "sightseeing", "hangout", "shopping", "snack", "game_break"]
TRADITIONAL = ["idle", "reading", "thinking", "walking", "sitting", "gaming", "sleeping", "bathing", "toilet",
               "studying", "eating", "stretching", "tebe", "bidu"]

def activities_for(outfit):
    return {"tuxedo": FORMAL, "casual": CASUAL}.get(outfit, TRADITIONAL)

def pose_of(activity):
    return ACTIVITIES.get(activity, (activity, ""))[0]

def scene_of(activity):
    return ACTIVITIES.get(activity, (activity, ""))[1]

# ------------------------------------------------------------------ scenes
def _ground(p, w, h, colour):
    p.setPen(Qt.NoPen); p.setBrush(QColor(colour)); p.drawEllipse(QRectF(w * 0.06, h * 0.86, w * 0.88, h * 0.12))

def paint_background(p, scene, w, h, phase=0.0):
    """Scene behind LAFA (inside the character widget, w x h)."""
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    if scene in {"beach", "beach_ball"}:
        p.setPen(Qt.NoPen); p.setBrush(QColor(255, 214, 92, 230)); p.drawEllipse(QPointF(w * 0.16, h * 0.16), w * 0.08, w * 0.08)  # sun
        sea = QPainterPath(); sea.moveTo(0, h * 0.78)
        for i in range(9): sea.quadTo(w * (i + 0.5) / 8, h * (0.75 + 0.02 * math.sin(phase + i)), w * (i + 1) / 8, h * 0.78)
        sea.lineTo(w, h * 0.88); sea.lineTo(0, h * 0.88); sea.closeSubpath()
        p.setBrush(QColor(64, 170, 222, 200)); p.drawPath(sea)
        p.setBrush(QColor(242, 214, 150, 235)); p.drawEllipse(QRectF(-w * 0.05, h * 0.84, w * 1.1, h * 0.2))  # sand
        if scene == "beach":
            p.setPen(QPen(QColor(120, 90, 60), max(2, w // 60))); p.drawLine(QPointF(w * 0.86, h * 0.92), QPointF(w * 0.86, h * 0.36))
            p.setPen(Qt.NoPen); p.setBrush(QColor(232, 76, 61, 230)); umbrella = QPainterPath(); umbrella.moveTo(w * 0.62, h * 0.42)
            umbrella.quadTo(w * 0.86, h * 0.18, w * 1.0, h * 0.42); umbrella.closeSubpath(); p.drawPath(umbrella)
    elif scene == "party":
        for i, (x, colour) in enumerate([(0.10, (239, 83, 80)), (0.22, (255, 193, 7)), (0.84, (66, 165, 245)), (0.93, (171, 71, 188))]):
            y = h * (0.20 + 0.05 * math.sin(phase + i)); p.setPen(QPen(QColor(150, 150, 150), 1)); p.drawLine(QPointF(w * x, y + w * 0.06), QPointF(w * x, h * 0.62))
            p.setPen(Qt.NoPen); p.setBrush(QColor(*colour, 230)); p.drawEllipse(QPointF(w * x, y), w * 0.05, w * 0.065)
        for i in range(26):
            x = (i * 37 % 100) / 100 * w; y = ((i * 53 + int(phase * 12)) % 70) / 100 * h
            p.setBrush(QColor(*[(239, 83, 80), (255, 193, 7), (66, 165, 245), (102, 187, 106)][i % 4])); p.drawRect(QRectF(x, y, w * 0.018, w * 0.01))
    elif scene in {"board", "podium"}:
        if scene == "board":
            p.setPen(QPen(QColor(90, 90, 96), 2)); p.setBrush(QColor(250, 250, 252, 235)); p.drawRect(QRectF(w * 0.58, h * 0.10, w * 0.38, h * 0.30))
            p.setPen(Qt.NoPen)
            for i, height in enumerate([0.10, 0.17, 0.13, 0.22]):
                p.setBrush(QColor(*[(66, 165, 245), (102, 187, 106), (255, 167, 38), (239, 83, 80)][i])); p.drawRect(QRectF(w * (0.62 + i * 0.08), h * (0.36 - height), w * 0.05, h * height))
    elif scene == "stage":
        p.setPen(Qt.NoPen); p.setBrush(QColor(156, 39, 52, 210)); p.drawRect(QRectF(0, 0, w * 0.12, h * 0.85)); p.drawRect(QRectF(w * 0.88, 0, w * 0.12, h * 0.85))
        p.setBrush(QColor(255, 236, 179, 70)); spot = QPolygonF([QPointF(w * 0.42, 0), QPointF(w * 0.58, 0), QPointF(w * 0.85, h * 0.92), QPointF(w * 0.15, h * 0.92)]); p.drawPolygon(spot)
        _ground(p, w, h, "#7b5a3a")
    elif scene == "carpet":
        p.setPen(Qt.NoPen); p.setBrush(QColor(176, 28, 40, 220)); p.drawPolygon(QPolygonF([QPointF(w * 0.30, h * 0.80), QPointF(w * 0.70, h * 0.80), QPointF(w * 0.95, h), QPointF(w * 0.05, h)]))
    elif scene == "city":
        p.setPen(Qt.NoPen)
        for i, (x, top) in enumerate([(0.0, 0.42), (0.14, 0.30), (0.74, 0.36), (0.88, 0.48)]):
            p.setBrush(QColor(*[(144, 202, 249), (179, 157, 219), (128, 203, 196), (255, 204, 128)][i], 200)); p.drawRect(QRectF(w * x, h * top, w * 0.13, h * (0.88 - top)))
        _ground(p, w, h, "#b0bec5")
    elif scene == "cafe":
        p.setPen(Qt.NoPen); p.setBrush(QColor(255, 236, 179, 140)); p.drawRoundedRect(QRectF(w * 0.05, h * 0.08, w * 0.9, h * 0.14), 8, 8)
        for i in range(6):
            p.setBrush(QColor(*[(239, 83, 80), (255, 255, 255)][i % 2], 200)); p.drawRect(QRectF(w * (0.05 + i * 0.15), h * 0.08, w * 0.15, h * 0.06))
    elif scene == "shopping":
        _ground(p, w, h, "#cfd8dc")
    p.restore()

def paint_foreground(p, scene, w, h, phase=0.0):
    """Props in front of LAFA (tables, bags, ball)."""
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    if scene in {"meeting", "dinner", "cafe"}:
        top = QColor({"meeting": "#6d4c41", "dinner": "#fafafa", "cafe": "#a1887f"}[scene])
        p.setPen(QPen(QColor(70, 50, 40), 2)); p.setBrush(top); p.drawRoundedRect(QRectF(w * 0.04, h * 0.82, w * 0.92, h * 0.07), 6, 6)
        p.setBrush(QColor(90, 70, 60)); p.drawRect(QRectF(w * 0.12, h * 0.89, w * 0.04, h * 0.11)); p.drawRect(QRectF(w * 0.84, h * 0.89, w * 0.04, h * 0.11))
        if scene == "meeting":
            p.setBrush(QColor(55, 71, 79)); p.drawRect(QRectF(w * 0.62, h * 0.73, w * 0.24, h * 0.09))  # laptop
            p.setBrush(QColor(255, 255, 255)); p.drawRect(QRectF(w * 0.12, h * 0.79, w * 0.18, h * 0.03))  # papers
        elif scene == "dinner":
            p.setBrush(QColor(255, 248, 225)); p.drawRect(QRectF(w * 0.80, h * 0.70, w * 0.03, h * 0.12))  # candle
            p.setPen(Qt.NoPen); p.setBrush(QColor(255, 167, 38)); p.drawEllipse(QPointF(w * 0.815, h * 0.68), w * 0.015, w * 0.025 + 2 * math.sin(phase * 3))
        else:
            p.setBrush(QColor(255, 255, 255)); p.drawRoundedRect(QRectF(w * 0.76, h * 0.74, w * 0.09, h * 0.08), 4, 4)  # coffee cup
            p.setPen(QPen(QColor(200, 200, 200), 2)); p.drawArc(QRectF(w * 0.84, h * 0.75, w * 0.04, h * 0.04), -90 * 16, 180 * 16)
    elif scene == "podium":
        p.setPen(QPen(QColor(62, 39, 35), 2)); p.setBrush(QColor(121, 85, 72)); p.drawPolygon(QPolygonF([QPointF(w * 0.62, h * 0.62), QPointF(w * 0.96, h * 0.62), QPointF(w * 0.92, h), QPointF(w * 0.66, h)]))
        p.setBrush(QColor(255, 213, 79)); p.drawEllipse(QPointF(w * 0.79, h * 0.75), w * 0.04, w * 0.04)
    elif scene == "papers":
        p.setPen(QPen(QColor(160, 160, 160), 1)); p.setBrush(QColor(255, 255, 255))
        for i in range(3): p.drawRect(QRectF(w * (0.70 + i * 0.02), h * (0.86 - i * 0.02), w * 0.2, h * 0.1))
    elif scene == "shopping":
        for i, (x, colour) in enumerate([(0.06, (236, 64, 122)), (0.80, (255, 167, 38))]):
            p.setPen(QPen(QColor(90, 90, 90), 2)); p.setBrush(QColor(*colour)); p.drawRect(QRectF(w * x, h * 0.76, w * 0.14, h * 0.16))
            p.setBrush(Qt.NoBrush); p.drawArc(QRectF(w * (x + 0.03), h * 0.71, w * 0.08, h * 0.08), 0, 180 * 16)
    elif scene == "beach_ball":
        y = h * (0.05 + 0.05 * abs(math.sin(phase * 1.5))); r = w * 0.09
        for i, colour in enumerate([(239, 83, 80), (255, 255, 255), (66, 165, 245), (255, 235, 59)]):
            p.setPen(Qt.NoPen); p.setBrush(QColor(*colour)); p.drawPie(QRectF(w * 0.13 - r, y + h * 0.04, 2 * r, 2 * r), i * 90 * 16, 90 * 16)
    elif scene == "stage":
        p.setPen(Qt.NoPen); p.setBrush(QColor(255, 255, 255)); p.drawRect(QRectF(w * 0.70, h * 0.66, w * 0.16, h * 0.05))  # diploma
        p.setBrush(QColor(176, 28, 40)); p.drawRect(QRectF(w * 0.77, h * 0.66, w * 0.02, h * 0.05))
    p.restore()

def flag_pixmap(size):
    """Timor-Leste flag drawn with Qt (no emoji font needed)."""
    from .qt import QPixmap, QPainter
    w, h = size, int(size * 0.66); pix = QPixmap(w, h); pix.fill(QColor("#dc241f"))
    p = QPainter(pix); p.setRenderHint(QPainter.Antialiasing); p.setPen(Qt.NoPen)
    p.setBrush(QColor("#ffc726")); p.drawPolygon(QPolygonF([QPointF(0, 0), QPointF(w * 0.5, h / 2), QPointF(0, h)]))
    p.setBrush(QColor("#000000")); p.drawPolygon(QPolygonF([QPointF(0, 0), QPointF(w * 0.33, h / 2), QPointF(0, h)]))
    p.setBrush(QColor("#ffffff")); cx, cy, r = w * 0.12, h / 2, h * 0.14
    star = QPolygonF([QPointF(cx + (r if i % 2 == 0 else r * 0.4) * math.cos(math.pi / 2 + i * math.pi / 5 - 0.35), cy - (r if i % 2 == 0 else r * 0.4) * math.sin(math.pi / 2 + i * math.pi / 5 - 0.35)) for i in range(10)])
    p.drawPolygon(star); p.end(); return pix
