"""Ensiklopédia: the 15 categories as illustrated tiles (grouped like the home
chart), a level filter for the school levels, and one page per category with
its articles, municipalities, tourist places or national days."""
from ...qt import Qt, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from ... import kb, icons
from ..texts import extend
from ..widgets import (Card, Clickable, ClayIcon, Pill, Segmented, ProgressLine, Banner, ResponsiveGrid, ListRow, label, button, scroll,
                       section_title, clear_layout, EmptyState, rounded)
from .home import GROUPS
from .article import level_range, item_pixmap

extend({
    "enc_counts": ("{a} artigu · {m} munisípiu · {p} fatin · {d} loron · {q} pergunta", "{a} artigos · {m} municípios · {p} lugares · {d} datas · {q} perguntas",
                   "{a} artikel · {m} munisipio · {p} tempat · {d} hari · {q} soal", "{a} articles · {m} municipalities · {p} places · {d} days · {q} questions"),
    "filter_level": ("Nível eskola", "Nível escolar", "Jenjang sekolah", "School level"),
    "recommended": ("Sujestaun ba ita", "Sugestões para si", "Saran untukmu", "Suggested for you"),
    "read_done": ("Lee ona", "Lido", "Sudah dibaca", "Read"),
    "articles_title": ("Artigu sira", "Artigos", "Artikel", "Articles"),
    "municipalities_title": ("Munisípiu sira", "Municípios", "Munisipio", "Municipalities"),
    "places_title": ("Fatin turístiku sira", "Lugares turísticos", "Tempat wisata", "Tourist places"),
    "days_title": ("Feriadu no loron nasionál", "Feriados e dias nacionais", "Hari libur dan hari nasional", "Holidays and national days"),
    "open_places": ("Loke pájina turizmu", "Abrir a página de turismo", "Buka halaman wisata", "Open the tourism page"),
    "open_map": ("Loke mapa", "Abrir o mapa", "Buka peta", "Open the map"),
    "sort_plan": ("Orden", "Ordem", "Urutan", "Order"),
    "sort_time": ("Kronolojia", "Cronologia", "Kronologi", "Chronology"),
    "sort_az": ("A–Z", "A–Z", "A–Z", "A–Z"),
    "n_read": ("{done}/{n} lee ona", "{done}/{n} lidos", "{done}/{n} dibaca", "{done}/{n} read"),
})

THUMB = (92, 64)

def thumb(item, win=None, size=THUMB, radius=12):
    """The downloaded photo of an item when there is one, else its illustration."""
    return rounded(item_pixmap(win, item, *size), radius)

def level_options(t):
    return [("all", t("all_levels"))] + [(lv, kb.LEVEL_SHORT[lv]) for lv in kb.LEVELS]

class EncyclopediaPage(QWidget):
    route = "encyclopedia"
    def __init__(self, win):
        super().__init__(); self.win = win; self.level = "all"
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(16)
        outer.addWidget(scroll(self.body))
    def show_route(self, params):
        if params.get("level") in kb.LEVELS + ["all"]: self.level = params["level"]
        self.render()
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; base = win.kb; prog = win.progress
        stats = base.stats(); level = None if self.level == "all" else self.level
        # Hero (gradient, reference image 3) with the totals.
        hero = Card(22, 26, gradient=(win.tok["nav_a"], win.tok["primary"], win.tok["nav_b"]))
        row = QHBoxLayout(); row.setSpacing(18); col = QVBoxLayout(); col.setSpacing(6)
        title = label(t("enc_title"), "h1", wrap=True); title.setStyleSheet("color:white;"); col.addWidget(title)
        sub = label(t("enc_sub"), wrap=True); sub.setStyleSheet("color:rgba(255,255,255,0.92); font-size:16px;"); col.addWidget(sub)
        counts = label(t("enc_counts", a=stats["articles"], m=stats["municipalities"], p=stats["places"], d=stats["days"], q=stats["questions"]), wrap=True)
        counts.setStyleSheet("color:white; font-weight:800; background:rgba(255,255,255,0.16); border-radius:12px; padding:6px 12px;"); col.addWidget(counts, 0, Qt.AlignLeft)
        row.addLayout(col, 1)
        pic = QLabel(); pic.setPixmap(rounded(icons.illustration("tl-overview", 300, 150), 18)); row.addWidget(pic, 0, Qt.AlignVCenter)
        hero.box.addLayout(row); self.col.addWidget(hero)
        # Level filter.
        bar = QHBoxLayout(); bar.addWidget(label(t("filter_level"), "h3"))
        seg = Segmented(level_options(t), self.level); seg.changed.connect(self.set_level); bar.addWidget(seg); bar.addStretch()
        self.col.addLayout(bar)
        # Category tiles, grouped.
        for group_key, cats, _acc in GROUPS:
            tiles = []
            for key in cats:
                cat = kb.CATEGORY[key]; items = [i for i in base.articles(key, level)]
                if not items and level: continue
                tiles.append(self.tile(cat, items))
            if not tiles: continue
            self.col.addLayout(section_title(t(group_key)))
            grid = ResponsiveGrid(250, 4, 14)
            for tile in tiles: grid.add(tile)
            self.col.addWidget(grid)
        # Suggestions: unread articles for the learner's level.
        lv = level or win.settings.school_level
        unread = [a for a in base.articles(None, lv) if a.kind == "article" and not prog.is_read(a.id)]
        if unread:
            rec = Card(18, 24); rec.box.addLayout(section_title(t("recommended"), Pill(kb.LEVEL_SHORT.get(lv, ""), "lilac")))
            pick = unread[(len(prog.read) * 7) % len(unread):] + unread
            for item in pick[:4]:
                cat = kb.CATEGORY.get(item.category, kb.CATEGORIES[0])
                r = ListRow(item.title(lang), item.summary(lang), [(kb.text(cat.title, lang), cat.accent)], thumb=thumb(item, win))
                r.clicked.connect(lambda i=item.id: win.open_item(i)); rec.box.addWidget(r)
            self.col.addWidget(rec)
        if not base.all(): self.col.addWidget(EmptyState("book-open", t("empty_content"), t("empty_content_text")))
        self.col.addStretch()
    def tile(self, cat, items):
        win = self.win; t = win.t; lang = win.lang; prog = win.progress
        card = Clickable(10, 22); card.box.setSpacing(8)
        card.box.addWidget(Banner(lambda w, h, k=cat.illustration: icons.illustration(k, w, h), 118, 16))
        head = QHBoxLayout(); head.setSpacing(10); head.addWidget(ClayIcon(cat.icon, cat.accent, 40))
        names = QVBoxLayout(); names.setSpacing(0); names.addWidget(label(kb.text(cat.title, lang), "h3", wrap=True))
        done = sum(1 for i in items if prog.is_read(i.id))
        names.addWidget(label(t("n_read", done=done, n=len(items)), "caption")); head.addLayout(names, 1); card.box.addLayout(head)
        card.box.addWidget(label(kb.text(cat.summary, lang), "muted", wrap=True))
        card.box.addStretch(); card.box.addWidget(ProgressLine(done / max(1, len(items)), 8))
        card.setAccessibleName(kb.text(cat.title, lang)); card.clicked.connect(lambda k=cat.key: win.open("category", category=k))
        return card
    def set_level(self, key): self.level = key; self.render()
    def retranslate(self): self.render()

class CategoryPage(QWidget):
    route = "category"
    def __init__(self, win):
        super().__init__(); self.win = win; self.category = None; self.level = "all"; self.sort = "plan"
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(14)
        self.area = scroll(self.body); outer.addWidget(self.area)
    def show_route(self, params):
        cat = params.get("category", self.category or "history")
        if cat not in kb.CATEGORY: cat = "history"
        if cat != self.category:
            self.category = cat; self.area.verticalScrollBar().setValue(0)
            self.sort = "time" if cat in ("history", "colonial", "conflicts", "leaders") else "plan"
        self.render()
    def ordered(self, items):
        base = self.win.kb
        if self.sort == "az": return sorted(items, key=lambda i: kb.fold(i.title(self.win.lang)))
        if self.sort == "time":
            def start(i):
                p = i.get("period") if isinstance(i.get("period"), dict) else {}
                return p.get("from") if isinstance(p.get("from"), (int, float)) else 10 ** 6 + base.plan_rank(i.id)
            return sorted(items, key=start)
        return sorted(items, key=lambda i: base.plan_rank(i.id))
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; base = win.kb; prog = win.progress
        cat = kb.CATEGORY[self.category]; level = None if self.level == "all" else self.level
        self.col.addWidget(Banner(lambda w, h, k=cat.illustration: icons.illustration(k, w, h), 200, 24, kb.text(cat.title, lang), kb.text(cat.summary, lang)))
        bar = QHBoxLayout(); bar.setSpacing(10)
        seg = Segmented(level_options(t), self.level); seg.changed.connect(self.set_level); bar.addWidget(seg); bar.addSpacing(8)
        order = Segmented([("plan", t("sort_plan")), ("time", t("sort_time")), ("az", t("sort_az"))], self.sort); order.changed.connect(self.set_sort); bar.addWidget(order)
        bar.addStretch(); self.col.addLayout(bar)
        all_items = base.articles(self.category, level)
        articles = self.ordered([i for i in all_items if i.kind == "article"])
        if articles:
            done = sum(1 for i in articles if prog.is_read(i.id))
            card = Card(16, 24); card.box.addLayout(section_title(t("articles_title"), Pill(t("n_read", done=done, n=len(articles)), cat.accent)))
            for item in articles:
                lr = level_range(item.levels())
                pills = [(f"{t('level')} {lr}", "lilac")] if lr else []
                r = ListRow(item.title(lang), item.summary(lang), pills, done=prog.is_read(item.id), thumb=thumb(item, win))
                r.clicked.connect(lambda i=item.id: win.open_item(i)); card.box.addWidget(r)
            self.col.addWidget(card)
        muns = [i for i in all_items if i.kind == "municipality"]
        if muns:
            card = Card(16, 24); card.box.addLayout(section_title(t("municipalities_title"), button(t("open_map"), lambda: win.open("map"), "ghost", "map")))
            grid = ResponsiveGrid(220, 4, 12)
            for m in sorted(muns, key=lambda m: kb.fold(m.title(lang))):
                tile = Clickable(10, 18); line = QHBoxLayout(); line.addWidget(ClayIcon("map", "teal", 36))
                c2 = QVBoxLayout(); c2.setSpacing(0); c2.addWidget(label(m.title(lang), "h3", wrap=True))
                pop = m.get("population") or {}
                if pop.get("value"): c2.addWidget(label(f"{t('population')}: {pop['value']:,}".replace(",", " "), "caption"))
                line.addLayout(c2, 1); tile.box.addLayout(line); tile.clicked.connect(lambda i=m.id: win.open_item(i)); grid.add(tile)
            card.box.addWidget(grid); self.col.addWidget(card)
        places = [i for i in all_items if i.kind == "place"]
        if places:
            card = Card(16, 24); card.box.addLayout(section_title(t("places_title"), button(t("open_places"), lambda: win.open("places"), "ghost", "umbrella")))
            for p in places[:8]:
                mun = base.get(p.get("municipality", ""))
                r = ListRow(p.title(lang), p.summary(lang), [(mun.title(lang), "teal")] if mun else [], done=prog.is_read(p.id), thumb=thumb(p, win))
                r.clicked.connect(lambda i=p.id: win.open_item(i)); card.box.addWidget(r)
            self.col.addWidget(card)
        days = [i for i in all_items if i.kind == "day"]
        if days:
            from datetime import date
            year = date.today().year; card = Card(16, 24); card.box.addLayout(section_title(t("days_title"), button(t("open_calendar"), lambda: win.open("calendar"), "ghost", "calendar-check")))
            dated = sorted(((base.day_date(d, year), d) for d in days), key=lambda x: (x[0] is None, x[0] or date(year, 12, 31)))
            for when, d in dated:
                pills = [(t("holiday") if d.get("type") == "holiday" else t("commemorative"), "rose" if d.get("type") == "holiday" else "violet")]
                r = ListRow(d.title(lang), d.summary(lang), pills, meta=kb.format_date(when, lang) if when else t("variable_date"), done=prog.is_read(d.id), icon_name="calendar-check", accent_key="rose")
                r.clicked.connect(lambda i=d.id: win.open_item(i)); card.box.addWidget(r)
            self.col.addWidget(card)
        if not all_items: self.col.addWidget(EmptyState(cat.icon, t("empty_content"), t("empty_content_text")))
        self.col.addStretch()
    def set_level(self, key): self.level = key; self.render()
    def set_sort(self, key): self.sort = key; self.render()
    def retranslate(self): self.render()
