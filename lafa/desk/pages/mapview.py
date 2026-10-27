"""Mapa — the interactive map of Timor-Leste.

Municipalities (geoBoundaries / © OpenStreetMap contributors, ODbL; Ataúro
shown as its own municipality since 2022), administrative posts (OCHA,
CC BY 3.0 IGO) and the tourist places of the encyclopedia. Hover shows names,
click opens details, the wheel zooms, dragging pans; keyboard: arrows pan,
+/− zoom, 0 resets. Colour modes: municipalities, population, density.
"""
import math

from ...qt import (Qt, Signal, QPointF, QRectF, QPoint, QColor, QPainter, QPainterPath, QPen, QLinearGradient, QFont, QFontMetrics,
                   QWidget, QLabel, QVBoxLayout, QHBoxLayout, QToolTip, QPushButton, QSizePolicy, QLineEdit, QCompleter, QStringListModel)
from ... import kb, icons
from ..texts import extend
from ..theme import ACCENTS, accent, lighten, darken, FONT_FAMILY
from ..widgets import (Card, Clickable, ClayIcon, Pill, Segmented, SearchBox, label, button, scroll, section_title, clear_layout, tok_of,
                       ResponsiveGrid, Banner, FlowLayout)

extend({
    "map_title": ("Mapa Timór-Leste", "Mapa de Timor-Leste", "Peta Timor-Leste", "Map of Timor-Leste"),
    "map_sub": ("Munisípiu 14, postu administrativu no fatin turístiku. Klik iha mapa atu hatene liu tan.",
                "Os 14 municípios, postos administrativos e lugares turísticos. Clique no mapa para saber mais.",
                "14 munisipio, pos administratif dan tempat wisata. Klik peta untuk tahu lebih banyak.",
                "The 14 municipalities, administrative posts and tourist places. Click the map to learn more."),
    "layer_posts": ("Postu", "Postos", "Pos", "Posts"), "layer_places": ("Fatin turístiku", "Lugares turísticos", "Tempat wisata", "Tourist places"),
    "layer_labels": ("Naran", "Nomes", "Nama", "Names"),
    "colour_municipality": ("Munisípiu", "Municípios", "Munisipio", "Municipalities"), "colour_population": ("Populasaun", "População", "Penduduk", "Population"),
    "colour_density": ("Densidade", "Densidade", "Kepadatan", "Density"),
    "map_search": ("Buka munisípiu, postu ka fatin…", "Procurar município, posto ou lugar…", "Cari munisipio, pos atau tempat…", "Find a municipality, post or place…"),
    "reset_zoom": ("Mapa tomak", "Mapa inteiro", "Seluruh peta", "Whole map"),
    "map_pick": ("Hili munisípiu ka fatin ida iha mapa.", "Escolha um município ou lugar no mapa.", "Pilih munisipio atau tempat di peta.", "Pick a municipality or place on the map."),
    "per_km2": ("ema/km²", "hab./km²", "jiwa/km²", "people/km²"),
    "map_credit": ("Mapa: geoBoundaries · © OpenStreetMap (ODbL) · OCHA (CC BY 3.0 IGO)", "Mapa: geoBoundaries · © OpenStreetMap (ODbL) · OCHA (CC BY 3.0 IGO)",
                   "Peta: geoBoundaries · © OpenStreetMap (ODbL) · OCHA (CC BY 3.0 IGO)", "Map: geoBoundaries · © OpenStreetMap (ODbL) · OCHA (CC BY 3.0 IGO)"),
    "keyboard_map": ("Teklas: seta = muda, + / − = zoom, 0 = mapa tomak", "Teclas: setas = mover, + / − = zoom, 0 = mapa inteiro", "Tombol: panah = geser, + / − = zoom, 0 = seluruh peta", "Keys: arrows = pan, + / − = zoom, 0 = whole map"),
})

PALETTE = ["#b9a7ff", "#ffb3cf", "#9fe0c4", "#ffd88a", "#9fd0ff", "#ffbf9f", "#c8f0a0", "#f5b0ff", "#a0e8ec", "#ffc8a8", "#b8c8ff", "#e8d0a8", "#a8f0d0", "#ffd0e8"]
TYPE_ICON = {"beach": ("umbrella", "cyan"), "island": ("waves", "sky"), "mountain": ("mountain", "peach"), "viewpoint": ("compass", "violet"),
             "church": ("church", "lilac"), "statue": ("star", "violet"), "museum": ("landmark", "indigo"), "monument": ("flag", "rose"),
             "memorial": ("candle", "slate"), "lake": ("drop", "sky"), "cave": ("mountain", "slate"), "hot_spring": ("drop", "coral"),
             "waterfall": ("drop", "teal"), "fort": ("shield", "peach"), "market": ("coin", "butter"), "park": ("leaf", "green"),
             "reef": ("fish", "cyan"), "village": ("house", "butter"), "town": ("house", "indigo"), "garden": ("plant", "green"), "river": ("waves", "teal")}

def point_in_ring(x, y, ring):
    inside = False; n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1: inside = not inside
    return inside

class MapWidget(QWidget):
    """Painted map. Signals: municipality_clicked(id), place_clicked(id)."""
    municipality_clicked = Signal(str)
    place_clicked = Signal(str)
    def __init__(self, base, lang="en", interactive=True, parent=None):
        super().__init__(parent); self.base = base; self.lang = lang; self.interactive = interactive
        self.munis = base.map.get("municipalities", []); self.posts = base.posts.get("posts", [])
        bbox = base.map.get("bbox") or [124.0, -9.5, 127.4, -8.1]; self.bbox = (bbox[0] - 0.08, bbox[1] - 0.08, bbox[2] + 0.08, bbox[3] + 0.08)
        self.zoom = 1.0; self.center = ((self.bbox[0] + self.bbox[2]) / 2, (self.bbox[1] + self.bbox[3]) / 2)
        self.hover = None; self.selected = None; self.selected_place = None; self.pin = None
        self.show_posts = False; self.show_places = True; self.show_labels = True; self.mode = "municipality"
        self.drag = None; self._paths = None
        self.info = {m.get("geo"): m for m in base.municipalities()}
        self.setMinimumSize(320, 200)
        if interactive: self.setMouseTracking(True); self.setFocusPolicy(Qt.StrongFocus); self.setCursor(Qt.OpenHandCursor)
    # ---------------------------------------------------------- projection
    def _scale(self):
        w, h = max(1, self.width() - 24), max(1, self.height() - 24)
        sx = w / (self.bbox[2] - self.bbox[0]); sy = h / (self.bbox[3] - self.bbox[1])
        return min(sx, sy) * self.zoom
    def to_screen(self, lon, lat):
        s = self._scale(); return QPointF(self.width() / 2 + (lon - self.center[0]) * s, self.height() / 2 - (lat - self.center[1]) * s)
    def to_geo(self, p):
        s = self._scale(); return (self.center[0] + (p.x() - self.width() / 2) / s, self.center[1] - (p.y() - self.height() / 2) / s)
    def invalidate(self): self._paths = None; self.update()
    def resizeEvent(self, e): self.invalidate(); super().resizeEvent(e)
    def paths(self):
        if self._paths is None:
            out = {}
            for m in self.munis:
                path = QPainterPath(); path.setFillRule(Qt.OddEvenFill)
                for poly in m["polygons"]:
                    for ring in poly:
                        pts = [self.to_screen(lon, lat) for lon, lat in ring]
                        if pts: path.moveTo(pts[0]); [path.lineTo(p) for p in pts[1:]]; path.closeSubpath()
                out[m["name"]] = path
            posts = []
            if self.show_posts:
                for p in self.posts:
                    path = QPainterPath()
                    for poly in p["polygons"]:
                        for ring in poly:
                            pts = [self.to_screen(lon, lat) for lon, lat in ring]
                            if pts: path.moveTo(pts[0]); [path.lineTo(q) for q in pts[1:]]; path.closeSubpath()
                    posts.append((p, path))
            self._paths = (out, posts)
        return self._paths
    # ------------------------------------------------------------ data
    def muni_item(self, name): return self.info.get(name)
    def value_of(self, name):
        item = self.muni_item(name)
        if not item: return None
        pop = (item.get("population") or {}).get("value"); area = item.get("area_km2")
        if self.mode == "population": return pop
        if self.mode == "density" and pop and area: return pop / area
        return None
    def fill_for(self, i, name, tok):
        if self.mode == "municipality": return QColor(PALETTE[i % len(PALETTE)])
        values = [v for v in (self.value_of(m["name"]) for m in self.munis) if v]
        v = self.value_of(name)
        if not values or v is None: return QColor(tok["track"]) if not tok["dark"] else QColor("#3a3360")
        lo, hi = min(values), max(values); f = 0 if hi == lo else (math.log(v) - math.log(lo)) / (math.log(hi) - math.log(lo))
        a, b = QColor("#e9e3ff"), QColor("#6d4aff")
        return QColor(int(a.red() + (b.red() - a.red()) * f), int(a.green() + (b.green() - a.green()) * f), int(a.blue() + (b.blue() - a.blue()) * f))
    def place_points(self):
        out = []
        for p in self.base.places():
            lat, lon = p.get("lat"), p.get("lon")
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)): out.append((p, self.to_screen(lon, lat)))
        return out
    # ----------------------------------------------------------- painting
    def paintEvent(self, e):
        tok = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        g = QLinearGradient(0, 0, 0, self.height())
        if tok["dark"]: g.setColorAt(0, QColor("#1c2a52")); g.setColorAt(1, QColor("#14203f"))
        else: g.setColorAt(0, QColor("#d6efff")); g.setColorAt(1, QColor("#a9d8f5"))
        clip = QPainterPath(); clip.addRoundedRect(QRectF(self.rect()), 20, 20); p.setClipPath(clip); p.fillRect(self.rect(), g)
        wave = QColor(255, 255, 255, 60 if not tok["dark"] else 25); p.setPen(QPen(wave, 1.2))
        for y in range(20, self.height(), 34):
            path = QPainterPath(QPointF(0, y))
            for x in range(0, self.width() + 40, 40): path.quadTo(QPointF(x + 10, y - 4), QPointF(x + 20, y)); path.quadTo(QPointF(x + 30, y + 4), QPointF(x + 40, y))
            p.drawPath(path)
        munis, posts = self.paths()
        for i, m in enumerate(self.munis):
            path = munis[m["name"]]; color = self.fill_for(i, m["name"], tok)
            if tok["dark"] and self.mode == "municipality": color = darken(color, 0.45)
            if m["name"] == self.hover: color = lighten(color, 0.25)
            if m["id"] == self.selected: color = QColor("#ff8fc0")
            p.setPen(Qt.NoPen); p.setBrush(QColor(40, 20, 90, 30)); p.drawPath(path.translated(2, 3))
            p.setBrush(color); p.setPen(QPen(QColor("#ffffff"), 1.6 if m["name"] != self.hover else 2.6)); p.drawPath(path)
        if self.show_posts:
            p.setBrush(Qt.NoBrush); p.setPen(QPen(QColor(90, 70, 160, 120), 0.9, Qt.DashLine))
            for _post, path in posts: p.drawPath(path)
        f = QFont(FONT_FAMILY); f.setPixelSize(max(10, min(14, int(11 * self.zoom ** 0.35)))); f.setWeight(QFont.Bold); p.setFont(f); fm = QFontMetrics(f)
        if self.show_labels:
            for m in self.munis:
                item = self.muni_item(m["name"]); name = item.title(self.lang) if item else m["name"]
                c = self.to_screen(*m["centroid"]); w = fm.horizontalAdvance(name) if hasattr(fm, "horizontalAdvance") else fm.width(name)
                r = QRectF(c.x() - w / 2 - 6, c.y() - 10, w + 12, 20)
                p.setPen(Qt.NoPen); p.setBrush(QColor(255, 255, 255, 190) if not tok["dark"] else QColor(20, 16, 40, 190)); p.drawRoundedRect(r, 9, 9)
                p.setPen(QColor(tok["text"])); p.drawText(r, Qt.AlignCenter, name)
            if self.show_posts and self.zoom >= 1.8:
                f2 = QFont(FONT_FAMILY); f2.setPixelSize(10); p.setFont(f2); p.setPen(QColor(tok["text2"]))
                for post, _path in posts:
                    c = self.to_screen(*post["centroid"]); p.drawText(QRectF(c.x() - 60, c.y() + 10, 120, 14), Qt.AlignCenter, post["name"])
        if self.show_places:
            for place, pt in self.place_points():
                icon_name, acc = TYPE_ICON.get(place.get("type"), ("pin", "violet")); col = QColor(ACCENTS[acc][0])
                big = place.id in (self.selected_place, self.pin); r = 11 if big else 7
                p.setPen(QPen(QColor("#ffffff"), 2)); p.setBrush(col); p.drawEllipse(pt, r, r)
                if big or self.zoom >= 2.2:
                    p.drawPixmap(QPointF(pt.x() - 6, pt.y() - 6), icons.pixmap(icon_name, "#ffffff", 12))
                if big:
                    name = place.title(self.lang); w = (fm.horizontalAdvance(name) if hasattr(fm, "horizontalAdvance") else fm.width(name)) + 16
                    box = QRectF(pt.x() - w / 2, pt.y() - 40, w, 24); p.setPen(Qt.NoPen); p.setBrush(QColor(tok["glass_solid"])); p.drawRoundedRect(box, 10, 10)
                    p.setPen(QColor(tok["text"])); p.setFont(f); p.drawText(box, Qt.AlignCenter, name)
        self.paint_scale(p, tok)
        if self.hasFocus() and self.interactive:
            p.setClipping(False); p.setPen(QPen(QColor(tok["focus"]), 2)); p.setBrush(Qt.NoBrush); p.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 20, 20)
    def paint_scale(self, p, tok):
        s = self._scale(); km_per_px = 111.0 * math.cos(math.radians(self.center[1])) / s
        target = 120 * km_per_px; nice = next((v for v in (1, 2, 5, 10, 20, 25, 50, 100, 200) if v >= target * 0.5), 200)
        px = nice / km_per_px; x0, y0 = 18, self.height() - 22
        p.setPen(QPen(QColor(tok["text"]), 2)); p.drawLine(QPointF(x0, y0), QPointF(x0 + px, y0)); p.drawLine(QPointF(x0, y0 - 5), QPointF(x0, y0 + 1)); p.drawLine(QPointF(x0 + px, y0 - 5), QPointF(x0 + px, y0 + 1))
        f = QFont(FONT_FAMILY); f.setPixelSize(11); f.setWeight(QFont.Bold); p.setFont(f); p.drawText(QPointF(x0 + px + 6, y0 + 4), f"{nice} km")
        # North arrow.
        cx, cy = self.width() - 26, 30; path = QPainterPath(QPointF(cx, cy - 14)); path.lineTo(cx + 7, cy + 8); path.lineTo(cx, cy + 3); path.lineTo(cx - 7, cy + 8); path.closeSubpath()
        p.setPen(Qt.NoPen); p.setBrush(QColor(tok["primary"])); p.drawPath(path); p.setPen(QColor(tok["text"])); p.drawText(QRectF(cx - 8, cy + 9, 16, 14), Qt.AlignCenter, "N")
    # ------------------------------------------------------------ hit test
    def hit(self, pos):
        if self.show_places:
            best = None
            for place, pt in self.place_points():
                d = math.hypot(pt.x() - pos.x(), pt.y() - pos.y())
                if d <= 12 and (best is None or d < best[0]): best = (d, place)
            if best: return ("place", best[1])
        lon, lat = self.to_geo(QPointF(pos))
        for m in self.munis:
            for poly in m["polygons"]:
                if point_in_ring(lon, lat, poly[0]) and not any(point_in_ring(lon, lat, hole) for hole in poly[1:]): return ("muni", m)
        return None
    def mouseMoveEvent(self, e):
        if not self.interactive: return
        if self.drag is not None:
            s = self._scale(); d = e.pos() - self.drag[0]; c = self.drag[1]
            self.center = (c[0] - d.x() / s, c[1] + d.y() / s); self.invalidate(); return
        h = self.hit(e.pos()); name = h[1]["name"] if h and h[0] == "muni" else None
        if name != self.hover: self.hover = name; self.update()
        if h:
            if h[0] == "place": QToolTip.showText(e.globalPos(), h[1].title(self.lang), self)
            else:
                item = self.muni_item(h[1]["name"]); text = item.title(self.lang) if item else h[1]["name"]
                if item and (item.get("population") or {}).get("value"): text += f"\n{(item.get('population') or {}).get('value'):,}".replace(",", " ")
                QToolTip.showText(e.globalPos(), text, self)
    def leaveEvent(self, e): self.hover = None; self.update()
    def mousePressEvent(self, e):
        if self.interactive and e.button() == Qt.LeftButton: self.drag = (e.pos(), self.center, e.pos()); self.setCursor(Qt.ClosedHandCursor)
    def mouseReleaseEvent(self, e):
        if not self.interactive: return
        moved = self.drag and (e.pos() - self.drag[2]).manhattanLength() > 4; self.drag = None; self.setCursor(Qt.OpenHandCursor)
        if moved or e.button() != Qt.LeftButton: return
        h = self.hit(e.pos())
        if h and h[0] == "place": self.selected_place = h[1].id; self.update(); self.place_clicked.emit(h[1].id)
        elif h:
            item = self.muni_item(h[1]["name"]); self.selected = h[1]["id"]; self.selected_place = None; self.update(); self.municipality_clicked.emit(item.id if item else h[1]["id"])
    def mouseDoubleClickEvent(self, e):
        if self.interactive: self.zoom_at(e.pos(), 1.6)
    def wheelEvent(self, e):
        if not self.interactive: return
        self.zoom_at(e.pos() if hasattr(e, "pos") else e.position().toPoint(), 1.2 if e.angleDelta().y() > 0 else 1 / 1.2)
    def zoom_at(self, pos, factor):
        before = self.to_geo(QPointF(pos)); self.zoom = max(0.8, min(12.0, self.zoom * factor)); after = self.to_geo(QPointF(pos))
        self.center = (self.center[0] + before[0] - after[0], self.center[1] + before[1] - after[1]); self.invalidate()
    def reset(self):
        self.zoom = 1.0; self.center = ((self.bbox[0] + self.bbox[2]) / 2, (self.bbox[1] + self.bbox[3]) / 2); self.invalidate()
    def focus_on(self, lon, lat, zoom=3.0):
        self.center = (lon, lat); self.zoom = zoom; self.invalidate()
    def keyPressEvent(self, e):
        step = 40 / self._scale(); k = e.key()
        if k == Qt.Key_Left: self.center = (self.center[0] - step, self.center[1])
        elif k == Qt.Key_Right: self.center = (self.center[0] + step, self.center[1])
        elif k == Qt.Key_Up: self.center = (self.center[0], self.center[1] + step)
        elif k == Qt.Key_Down: self.center = (self.center[0], self.center[1] - step)
        elif k in (Qt.Key_Plus, Qt.Key_Equal): self.zoom_at(QPoint(self.width() // 2, self.height() // 2), 1.25); return
        elif k == Qt.Key_Minus: self.zoom_at(QPoint(self.width() // 2, self.height() // 2), 0.8); return
        elif k == Qt.Key_0: self.reset(); return
        else: super().keyPressEvent(e); return
        self.invalidate()

class MapPage(QWidget):
    route = "map"
    def __init__(self, win):
        super().__init__(); self.win = win; t = win.t
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 8, 0); outer.setSpacing(12)
        head = Card(16, 24); top = QHBoxLayout(); top.setSpacing(12); top.addWidget(ClayIcon("map", "teal", 52))
        tc = QVBoxLayout(); tc.setSpacing(2); tc.addWidget(label(t("map_title"), "h1")); tc.addWidget(label(t("map_sub"), "muted", wrap=True)); top.addLayout(tc, 1)
        self.find = SearchBox(t("map_search")); self.find.setMaximumWidth(320); self.find.returnPressed.connect(self.find_target); top.addWidget(self.find)
        head.box.addLayout(top)
        tools = QHBoxLayout(); tools.setSpacing(8)
        self.mode = Segmented([("municipality", t("colour_municipality")), ("population", t("colour_population")), ("density", t("colour_density"))])
        self.mode.changed.connect(self.set_mode); tools.addWidget(self.mode)
        self.layer_buttons = {}
        for key, text in (("places", t("layer_places")), ("posts", t("layer_posts")), ("labels", t("layer_labels"))):
            b = QPushButton(text); b.setObjectName("chip"); b.setCheckable(True); b.setChecked(key != "posts"); b.setCursor(Qt.PointingHandCursor)
            b.toggled.connect(lambda on, k=key: self.set_layer(k, on)); tools.addWidget(b); self.layer_buttons[key] = b
        tools.addStretch(); tools.addWidget(button(t("reset_zoom"), lambda: self.map.reset(), None, "zoom-out"))
        head.box.addLayout(tools); outer.addWidget(head)
        body = QHBoxLayout(); body.setSpacing(14)
        mapcard = Card(10, 26); self.map = MapWidget(win.kb, win.lang); self.map.municipality_clicked.connect(self.show_municipality); self.map.place_clicked.connect(self.show_place)
        self.map.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding); mapcard.box.addWidget(self.map, 1)
        foot = QHBoxLayout(); foot.addWidget(label(t("map_credit"), "caption", wrap=True), 1); foot.addWidget(label(t("keyboard_map"), "caption")); mapcard.box.addLayout(foot)
        body.addWidget(mapcard, 1)
        self.side_card = Card(16, 24); self.side_card.setFixedWidth(360); self.side_body = QWidget(); self.side = QVBoxLayout(self.side_body); self.side.setContentsMargins(0, 0, 0, 0); self.side.setSpacing(10)
        self.side_card.box.addWidget(scroll(self.side_body), 1); body.addWidget(self.side_card)
        outer.addLayout(body, 1)
        names = [i.title(win.lang) for i in win.kb.municipalities()] + [p.title(win.lang) for p in win.kb.places()] + [p["name"] for p in win.kb.posts.get("posts", [])]
        completer = QCompleter(sorted(set(names))); completer.setCaseSensitivity(Qt.CaseInsensitive); completer.setFilterMode(Qt.MatchContains); self.find.setCompleter(completer)
        self.show_hint()
    def show_route(self, params):
        if params.get("place") and self.win.kb.get(params["place"]):
            place = self.win.kb.get(params["place"]); self.map.pin = place.id; self.map.selected_place = place.id
            if isinstance(place.get("lat"), (int, float)): self.map.focus_on(place.get("lon"), place.get("lat"), 3.0)
            self.show_place(place.id)
        elif params.get("municipality"): self.select_municipality(params["municipality"])
    def set_mode(self, mode): self.map.mode = mode; self.map.update()
    def set_layer(self, key, on):
        if key == "places": self.map.show_places = on
        elif key == "posts": self.map.show_posts = on; self.map._paths = None
        else: self.map.show_labels = on
        self.map.update()
    def show_hint(self):
        clear_layout(self.side); self.side.addWidget(ClayIcon("pin", "pink", 56)); self.side.addWidget(label(self.win.t("map_pick"), "h3", wrap=True))
        # Legend of municipalities (map shapes; names from the encyclopedia when written).
        for idx, geo in enumerate(self.map.munis):
            m = self.map.muni_item(geo["name"])
            row = Clickable(6, 14); line = QHBoxLayout(); dot = QLabel(); dot.setFixedSize(14, 14)
            dot.setStyleSheet(f"background:{PALETTE[idx % len(PALETTE)]}; border-radius:7px;"); line.addWidget(dot); line.addWidget(label(m.title(self.win.lang) if m else geo["name"]), 1)
            pop = (m.get("population") or {}).get("value") if m else None
            if pop: line.addWidget(label(f"{pop:,}".replace(",", " "), "caption"))
            row.box.addLayout(line); row.clicked.connect(lambda i=(m.id if m else geo["id"]): self.select_municipality(i)); self.side.addWidget(row)
        self.side.addStretch()
    def select_municipality(self, item_id):
        item = self.win.kb.get(item_id)
        geo = next((g for g in self.map.munis if (item and g["name"] == item.get("geo")) or g["id"] == item_id), None)
        if geo: self.map.selected = geo["id"]; self.map.focus_on(*geo["centroid"], 2.2 if item.get("geo") not in ("Atauro", "Oecusse") else 3.5)
        self.show_municipality(item_id)
    def show_municipality(self, item_id):
        win = self.win; t = win.t; lang = win.lang; item = win.kb.get(item_id); clear_layout(self.side)
        if not item:
            geo = next((g for g in self.map.munis if g["id"] == item_id), None)
            self.side.addWidget(label(geo["name"] if geo else item_id, "h2")); self.side.addWidget(label(t("empty_content_text"), "muted", wrap=True)); self.side.addStretch(); return
        self.side.addWidget(Banner(lambda w, h, k=item.illustration(): __import__("lafa.icons", fromlist=["x"]).illustration(k, w, h), 120, 18))
        self.side.addWidget(label(item.title(lang), "h2", wrap=True)); self.side.addWidget(label(item.summary(lang), "muted", wrap=True))
        grid = ResponsiveGrid(140, 2, 8)
        pop = item.get("population") or {}
        for key, value in (("capital", kb.text(item.get("capital"), lang)), ("area", f"{item.get('area_km2', '—'):,} km²".replace(",", " ") if isinstance(item.get("area_km2"), (int, float)) else "—"),
                           ("population", (f"{pop.get('value'):,}".replace(",", " ") + f" ({pop.get('year')})") if pop.get("value") else "—"),
                           ("colour_density", f"{pop.get('value') / item.get('area_km2'):.0f} {t('per_km2')}" if pop.get("value") and item.get("area_km2") else "—")):
            c = Card(8, 16); c.box.setSpacing(2); c.box.addWidget(label(t(key), "caption")); c.box.addWidget(label(value, "h3", wrap=True)); grid.add(c)
        self.side.addWidget(grid)
        posts = item.get("posts") or []
        if posts:
            self.side.addWidget(label(t("posts"), "h3")); box = QWidget(); flow = FlowLayout(box, 6)
            for p in posts: flow.addWidget(Pill(p, "teal"))
            self.side.addWidget(box)
        places = win.kb.places(item.id)
        if places:
            self.side.addWidget(label(t("places_here"), "h3"))
            for p in places[:8]:
                row = Clickable(6, 14); line = QHBoxLayout(); icon_name, acc = TYPE_ICON.get(p.get("type"), ("pin", "violet")); line.addWidget(ClayIcon(icon_name, acc, 30))
                line.addWidget(label(p.title(lang), wrap=True), 1); row.box.addLayout(line); row.clicked.connect(lambda i=p.id: self.focus_place(i)); self.side.addWidget(row)
        self.side.addWidget(button(t("read_more"), lambda i=item.id: win.open_item(i), "primary", "book-open")); self.side.addStretch()
    def focus_place(self, place_id):
        place = self.win.kb.get(place_id)
        if place and isinstance(place.get("lat"), (int, float)):
            self.map.selected_place = place_id; self.map.focus_on(place.get("lon"), place.get("lat"), max(self.map.zoom, 3.0)); self.show_place(place_id)
    def show_place(self, place_id):
        win = self.win; t = win.t; lang = win.lang; item = win.kb.get(place_id); clear_layout(self.side)
        if not item: return
        self.side.addWidget(Banner(lambda w, h, k=item.illustration(): __import__("lafa.icons", fromlist=["x"]).illustration(k, w, h), 140, 18))
        self.side.addWidget(label(item.title(lang), "h2", wrap=True))
        tags = QHBoxLayout(); mun = win.kb.get(item.get("municipality", ""))
        if mun: tags.addWidget(Pill(mun.title(lang), "teal"))
        tags.addWidget(Pill(str(item.get("type", "")).replace("_", " "), "cyan")); tags.addStretch(); self.side.addLayout(tags)
        self.side.addWidget(label(item.summary(lang), wrap=True))
        tips = kb.text(item.get("tips"), lang)
        if tips: self.side.addWidget(label(t("visit_tips"), "h3")); self.side.addWidget(label(tips, "muted", wrap=True))
        if isinstance(item.get("lat"), (int, float)): self.side.addWidget(label(f"{t('coordinates')}: {abs(item.get('lat')):.4f}° S, {item.get('lon'):.4f}° E", "caption"))
        self.side.addWidget(button(t("read_more"), lambda i=item.id: win.open_item(i), "primary", "book-open")); self.side.addStretch()
    def find_target(self):
        q = kb.fold(self.find.text().strip())
        if not q: return
        for m in self.win.kb.municipalities():
            if q in kb.fold(m.title(self.win.lang)) or q in kb.fold(m.title("en")): self.select_municipality(m.id); return
        for p in self.win.kb.places():
            if q in kb.fold(p.title(self.win.lang)): self.focus_place(p.id); return
        for post in self.map.posts:
            if q in kb.fold(post["name"]):
                self.map.show_posts = True; self.layer_buttons["posts"].setChecked(True); self.map.focus_on(*post["centroid"], 4.0)
                item = self.win.kb.get(post["municipality"])
                if item: self.show_municipality(item.id)
                return
    def retranslate(self): pass
