"""Liña tempu: every dated event of the encyclopedia, from the first people
(tens of thousands of years ago) to 2026, by era, with filters and search."""
from ...qt import Qt, Signal, QRectF, QPointF, QColor, QPainter, QPen, QFont, QLinearGradient, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QLineEdit
from ... import kb
from ..texts import extend
from ..theme import accent, FONT_FAMILY
from ..widgets import Card, ClayIcon, Pill, label, button, scroll, section_title, clear_layout, EmptyState, tok_of, qcolor, FlowLayout
from ..widgets import SearchBox

extend({
    "tl_title": ("Liña tempu Timór-Leste", "Linha do tempo de Timor-Leste", "Lini masa Timor-Leste", "Timeline of Timor-Leste"),
    "tl_sub": ("Husi ema dahuluk iha tasi-le'un, tinan rihun 44 liubá, to'o 2026. Hili tempu ida ka buka eventu.", "Dos primeiros povos da ilha, há 44 mil anos, até 2026. Escolha uma época ou pesquise.",
               "Dari manusia pertama di pulau ini, 44 ribu tahun lalu, sampai 2026. Pilih masa atau cari peristiwa.", "From the island's first people 44,000 years ago to 2026. Pick an era or search for an event."),
    "all_eras": ("Tempu hotu", "Todas as épocas", "Semua masa", "All eras"),
    "filter_events": ("Buka eventu…", "Pesquisar eventos…", "Cari peristiwa…", "Search events…"),
    "n_events": ("eventu {n}", "{n} eventos", "{n} peristiwa", "{n} events"),
    "show_more": ("Haree tan", "Mostrar mais", "Tampilkan lagi", "Show more"),
    "all_topics": ("Tema hotu", "Todos os temas", "Semua tema", "All topics"),
})

class EraBar(QWidget):
    """A clickable ribbon of the eras (pastel segments, the chosen one raised)."""
    chosen = Signal(str)
    def __init__(self, eras, lang, current=None, parent=None):
        super().__init__(parent); self.eras = eras; self.lang = lang; self.current = current; self.hover = None
        self.setMinimumHeight(96); self.setMouseTracking(True); self.setFocusPolicy(Qt.StrongFocus); self.setCursor(Qt.PointingHandCursor)
        self.setAccessibleName("eras")
    def _rects(self):
        n = len(self.eras); gap = 6; w = (self.width() - gap * (n - 1)) / max(1, n)
        return [(QRectF(i * (w + gap), 6, w, self.height() - 12), e) for i, e in enumerate(self.eras)]
    def mouseMoveEvent(self, e):
        hit = next((era[0] for r, era in self._rects() if r.contains(QPointF(e.pos()))), None)
        if hit != self.hover: self.hover = hit; self.update()
    def leaveEvent(self, e): self.hover = None; self.update()
    def mousePressEvent(self, e):
        hit = next((era[0] for r, era in self._rects() if r.contains(QPointF(e.pos()))), None)
        if hit: self.current = None if hit == self.current else hit; self.update(); self.chosen.emit(self.current or "")
    def keyPressEvent(self, e):
        keys = [era[0] for era in self.eras]
        i = keys.index(self.current) if self.current in keys else -1
        if e.key() in (Qt.Key_Right, Qt.Key_Left):
            i = (i + (1 if e.key() == Qt.Key_Right else -1)) % len(keys); self.current = keys[i]; self.update(); self.chosen.emit(self.current); return
        if e.key() == Qt.Key_Escape: self.current = None; self.update(); self.chosen.emit(""); return
        super().keyPressEvent(e)
    def paintEvent(self, event):
        t = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        f = QFont(FONT_FAMILY)
        for r, (key, start, end, title, acc) in self._rects():
            strong, soft = accent(acc); on = key == self.current; hot = key == self.hover
            box = r.adjusted(0, 0 if on else 4, 0, 0 if on else -4)
            g = QLinearGradient(box.topLeft(), box.bottomRight())
            if on: g.setColorAt(0, QColor(strong).lighter(115)); g.setColorAt(1, QColor(strong))
            else:
                c = QColor(soft) if not t["dark"] else QColor(strong).darker(260); g.setColorAt(0, c); g.setColorAt(1, c.darker(104))
            p.setPen(QPen(QColor(t["focus"]), 2) if (self.hasFocus() and on) else QPen(QColor(strong) if hot else Qt.transparent, 2))
            p.setBrush(g); p.drawRoundedRect(box, 14, 14)
            p.setPen(QColor("#ffffff") if on else QColor(t["text"]))
            f.setPixelSize(12); f.setWeight(QFont.ExtraBold); p.setFont(f)
            p.drawText(box.adjusted(9, 8, -6, -24), Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, kb.text(title, self.lang))
            f.setPixelSize(11); f.setWeight(QFont.DemiBold); p.setFont(f); p.setPen(QColor("#ffffff") if on else QColor(t["muted"]))
            years = (kb.format_when(str(start), self.lang) if start < 0 else str(start)) + " – " + str(end)
            p.drawText(box.adjusted(9, box.height() - 24, -6, -6), Qt.AlignLeft | Qt.AlignVCenter, p.fontMetrics().elidedText(years, Qt.ElideRight, int(box.width() - 15)))

class EventRow(QWidget):
    """One event: date, a dot on the rail, the title and its topic; opens the article."""
    clicked = Signal()
    def __init__(self, event, lang, color, last=False, parent=None):
        super().__init__(parent); self.color = QColor(color); self.last = last; self.hover = False
        self.setFocusPolicy(Qt.StrongFocus); self.setCursor(Qt.PointingHandCursor); self.setAttribute(Qt.WA_Hover, True)
        row = QHBoxLayout(self); row.setContentsMargins(8, 9, 10, 9); row.setSpacing(12)
        when = label(kb.format_when(event["date"], lang), "eyebrow"); when.setFixedWidth(150); when.setWordWrap(True); row.addWidget(when, 0, Qt.AlignTop)
        row.addSpacing(22)
        title = label(event["title"], wrap=True); title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred); row.addWidget(title, 1)
        cat = kb.CATEGORY.get(event["category"]);
        if cat: row.addWidget(Pill(kb.text(cat.title, lang), cat.accent), 0, Qt.AlignTop)
        self.setAccessibleName(f"{kb.format_when(event['date'], lang)}: {event['title']}")
    def enterEvent(self, e): self.hover = True; self.update(); super().enterEvent(e)
    def leaveEvent(self, e): self.hover = False; self.update(); super().leaveEvent(e)
    def focusInEvent(self, e): self.update(); super().focusInEvent(e)
    def focusOutEvent(self, e): self.update(); super().focusOutEvent(e)
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton: self.clicked.emit()
    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space): self.clicked.emit(); return
        super().keyPressEvent(e)
    def paintEvent(self, e):
        t = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        if self.hover or self.hasFocus():
            p.setPen(QPen(QColor(t["focus"]), 2) if self.hasFocus() else Qt.NoPen); p.setBrush(qcolor(t["card_hover"])); p.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 14, 14)
        x = 8 + 150 + 12 + 11
        line = QColor(self.color); line.setAlpha(110); p.setPen(QPen(line, 3)); p.drawLine(QPointF(x, 0), QPointF(x, self.height() if not self.last else 20))
        p.setPen(QPen(QColor("#ffffff"), 2)); p.setBrush(self.color); p.drawEllipse(QPointF(x, 20), 7, 7)

class TimelinePage(QWidget):
    route = "timeline"
    PAGE = 120
    def __init__(self, win):
        super().__init__(); self.win = win; self.era = None; self.topic = None; self.query = ""; self.limit = self.PAGE
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(14)
        self.area = scroll(self.body); outer.addWidget(self.area)
    def show_route(self, params):
        if params.get("era") in [e[0] for e in kb.ERAS]: self.era = params["era"]
        self.render()
    def events(self):
        out = []
        q = kb.fold(self.query).strip()
        for e in self.win.kb.timeline(self.win.lang):
            e["era"] = kb.era_of(e["key"])
            if self.era and e["era"] != self.era: continue
            if self.topic and e["category"] != self.topic: continue
            if q and q not in kb.fold(e["title"]): continue
            out.append(e)
        return out
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang
        head = Card(20, 24); row = QHBoxLayout(); row.setSpacing(14); row.addWidget(ClayIcon("timeline", "peach", 60))
        c = QVBoxLayout(); c.setSpacing(2); c.addWidget(label(t("tl_title"), "h1", wrap=True)); c.addWidget(label(t("tl_sub"), "muted", wrap=True)); row.addLayout(c, 1)
        self.search = SearchBox(t("filter_events")); self.search.setText(self.query); self.search.setMaximumWidth(300)
        self.search.returnPressed.connect(self.filter_now); self.search.textEdited.connect(self.filter_live); row.addWidget(self.search, 0, Qt.AlignVCenter)
        head.box.addLayout(row)
        bar = EraBar(kb.ERAS, lang, self.era); bar.chosen.connect(self.set_era); head.box.addWidget(bar)
        chips = QWidget(); flow = FlowLayout(chips, 6)
        topics = [None] + sorted({e["category"] for e in win.kb.timeline(lang)}, key=lambda k: [c.key for c in kb.CATEGORIES].index(k) if k in kb.CATEGORY else 99)
        for key in topics:
            text_ = t("all_topics") if key is None else kb.text(kb.CATEGORY[key].title, lang)
            b = button(text_, lambda checked=False, k=key: self.set_topic(k), "chip"); b.setCheckable(True); b.setChecked(key == self.topic); flow.addWidget(b)
        head.box.addWidget(chips); self.col.addWidget(head)
        events = self.events()
        if not events:
            self.col.addWidget(EmptyState("timeline", t("no_results"))); self.col.addStretch(); return
        shown = events[:self.limit]
        # Group by era, one card each.
        for key, start, end, title, acc in kb.ERAS:
            group = [e for e in shown if e["era"] == key]
            if not group: continue
            card = Card(14, 24); years = (kb.format_when(str(start), lang) if start < 0 else str(start)) + " – " + str(end)
            card.box.addLayout(section_title(kb.text(title, lang), Pill(years, acc)))
            color = accent(acc)[0]; rows = QVBoxLayout(); rows.setSpacing(0)
            for i, e in enumerate(group):
                r = EventRow(e, lang, color, last=i == len(group) - 1); r.clicked.connect(lambda item=e["item"]: win.open_item(item)); rows.addWidget(r)
            card.box.addLayout(rows)
            self.col.addWidget(card)
        foot = QHBoxLayout(); foot.addWidget(label(t("n_events", n=len(events)), "caption")); foot.addStretch()
        if len(events) > self.limit: foot.addWidget(button(t("show_more"), self.more, "primary", "arrow-down"))
        self.col.addLayout(foot); self.col.addStretch()
    def set_era(self, key): self.era = key or None; self.limit = self.PAGE; self.render()
    def set_topic(self, key): self.topic = key; self.limit = self.PAGE; self.render()
    def filter_live(self, text_):
        self.query = text_
        if not hasattr(self, "_timer"):
            from ...qt import QTimer
            self._timer = QTimer(self); self._timer.setSingleShot(True); self._timer.setInterval(300); self._timer.timeout.connect(self.filter_now)
        self._timer.start()
    def filter_now(self):
        self.query = self.search.text(); self.limit = self.PAGE; self.render(); self.search.setFocus(); self.search.setCursorPosition(len(self.query))
    def more(self): self.limit += self.PAGE; self.render()
    def retranslate(self): self.render()
