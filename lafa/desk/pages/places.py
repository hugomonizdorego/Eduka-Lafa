"""Turizmu: every tourist place in the 14 municipalities (beaches, mountains,
museums, memorials, churches…) with search, filters, pictures and the map,
plus the tourism guide articles."""
from ...qt import Qt, QTimer, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
from ... import kb, icons
from ..texts import extend
from ..widgets import (Card, Clickable, ClayIcon, Pill, Banner, ResponsiveGrid, FlowLayout, SearchBox, label, button, scroll, section_title,
                       clear_layout, EmptyState, rounded, clip)
from .article import item_pixmap

extend({
    "tour_title": ("Turizmu iha Timór-Leste", "Turismo em Timor-Leste", "Wisata di Timor-Leste", "Tourism in Timor-Leste"),
    "tour_sub": ("Fatin {n} iha munisípiu 14: tasi-ibun, foho, muzeu, fatin istóriku no kultura.", "{n} lugares nos 14 municípios: praias, montanhas, museus, história e cultura.",
                 "{n} tempat di 14 munisipio: pantai, gunung, museum, sejarah dan budaya.", "{n} places in the 14 municipalities: beaches, mountains, museums, history and culture."),
    "tour_guides": ("Gia ba vizitante", "Guias para visitantes", "Panduan pengunjung", "Visitor guides"),
    "all_municipalities": ("Munisípiu hotu", "Todos os municípios", "Semua munisipio", "All municipalities"),
    "all_types": ("Tipu hotu", "Todos os tipos", "Semua jenis", "All types"),
    "filter_places": ("Buka fatin…", "Pesquisar lugares…", "Cari tempat…", "Search places…"),
    "n_places": ("fatin {n}", "{n} lugares", "{n} tempat", "{n} places"),
    "see_map_all": ("Haree fatin hotu iha mapa", "Ver todos no mapa", "Lihat semua di peta", "See all on the map"),
    "respect_note": ("Respeita fatin lulik no lisan lokál. Husu lisensa uluk antes foti foto ema ka fatin sagradu.", "Respeite os lugares sagrados e os costumes locais. Peça licença antes de fotografar pessoas ou lugares sagrados.",
                     "Hormati tempat suci dan adat setempat. Mintalah izin sebelum memotret orang atau tempat suci.", "Respect sacred places and local customs. Ask before photographing people or sacred sites."),
})

TYPE_NAMES = {
    "beach": ("Tasi-ibun", "Praia", "Pantai", "Beach"), "island": ("Tasi-le'un", "Ilha", "Pulau", "Island"),
    "mountain": ("Foho", "Montanha", "Gunung", "Mountain"), "viewpoint": ("Fatin haree paizajen", "Miradouro", "Titik pandang", "Viewpoint"),
    "church": ("Igreja", "Igreja", "Gereja", "Church"), "statue": ("Estátua", "Estátua", "Patung", "Statue"),
    "museum": ("Muzeu", "Museu", "Museum", "Museum"), "monument": ("Monumentu", "Monumento", "Monumen", "Monument"),
    "memorial": ("Memoriál", "Memorial", "Memorial", "Memorial"), "lake": ("Lagoa", "Lagoa", "Danau", "Lake"),
    "cave": ("Fatuk-kuak", "Gruta", "Gua", "Cave"), "hot_spring": ("Bee-manas", "Fonte termal", "Mata air panas", "Hot spring"),
    "waterfall": ("Kaskata", "Cascata", "Air terjun", "Waterfall"), "fort": ("Forte", "Forte", "Benteng", "Fort"),
    "market": ("Merkadu", "Mercado", "Pasar", "Market"), "park": ("Parke", "Parque", "Taman", "Park"),
    "reef": ("Ahu-ruin", "Recife de coral", "Terumbu karang", "Coral reef"), "village": ("Aldeia", "Aldeia", "Desa", "Village"),
    "town": ("Vila", "Vila", "Kota kecil", "Town"), "garden": ("Jardín", "Jardim", "Taman", "Garden"), "river": ("Mota", "Rio", "Sungai", "River"),
}
TYPE_ICON = {"beach": "umbrella", "island": "anchor", "mountain": "mountain", "viewpoint": "camera", "church": "church", "statue": "landmark",
             "museum": "landmark", "monument": "landmark", "memorial": "candle", "lake": "drop", "cave": "mountain", "hot_spring": "drop",
             "waterfall": "drop", "fort": "shield", "market": "coin", "park": "leaf", "reef": "fish", "village": "house", "town": "house",
             "garden": "leaf", "river": "drop"}

def type_name(kind, lang):
    row = TYPE_NAMES.get(kind)
    if not row: return str(kind or "").replace("_", " ").capitalize()
    return kb.show(row[("tet", "pt", "id", "en").index(lang)] if lang in ("tet", "pt", "id", "en") else row[3], lang)

class PlacesPage(QWidget):
    route = "places"
    PAGE = 24
    def __init__(self, win):
        super().__init__(); self.win = win; self.municipality = ""; self.kind = ""; self.query = ""; self.limit = self.PAGE
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(16)
        self.area = scroll(self.body); outer.addWidget(self.area)
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.setInterval(300); self.timer.timeout.connect(self.apply_query)
    def show_route(self, params):
        if "municipality" in params: self.municipality = params["municipality"] or ""
        if "type" in params: self.kind = params["type"] or ""
        self.render()
    def filtered(self):
        q = kb.fold(self.query).strip(); out = []
        for p in self.win.kb.places(self.municipality or None, self.kind or None):
            if q and q not in kb.fold(" ".join(kb.text(p.get("name"), l) for l in kb.LANGS) + " " + kb.text(p.get("summary"), self.win.lang)): continue
            out.append(p)
        return sorted(out, key=lambda p: (kb.fold(self.win.kb.get(p.get("municipality", "")).title("en")) if self.win.kb.get(p.get("municipality", "")) else "zz", kb.fold(p.title(self.win.lang))))
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; base = win.kb
        places = base.places()
        hero = Card(12, 26); hero.box.addWidget(Banner(lambda w, h: icons.illustration("beach", w, h), 210, 20, t("tour_title"), t("tour_sub", n=len(places))))
        row = QHBoxLayout(); row.setSpacing(10)
        row.addWidget(button(t("see_map_all"), lambda: win.open("map", layer="places"), "primary", "map"))
        row.addSpacing(6); row.addWidget(ClayIcon("heart", "rose", 28)); note = label(t("respect_note"), "caption", wrap=True); row.addWidget(note, 1); hero.box.addLayout(row)
        self.col.addWidget(hero)
        guides = [a for a in base.articles("tourism") if a.kind == "article"]
        if guides:
            self.col.addLayout(section_title(t("tour_guides")))
            grid = ResponsiveGrid(230, 3, 14)
            for g in sorted(guides, key=lambda a: base.plan_rank(a.id)):
                card = Clickable(10, 20); card.box.addWidget(Banner(lambda w, h, it=g: item_pixmap(win, it, w, h), 110, 14))
                card.box.addWidget(label(g.title(lang), "h3", wrap=True)); card.box.addWidget(label(clip(g.summary(lang), 170), "caption", wrap=True)); card.box.addStretch()
                card.clicked.connect(lambda i=g.id: win.open_item(i)); grid.add(card)
            self.col.addWidget(grid)
        # Filters.
        bar = Card(14, 22); top = QHBoxLayout(); top.setSpacing(10)
        self.search = SearchBox(t("filter_places")); self.search.setText(self.query); self.search.textEdited.connect(lambda _: self.timer.start()); top.addWidget(self.search, 2)
        self.muni = QComboBox(); self.muni.addItem(t("all_municipalities"), "")
        for m in base.municipalities(): self.muni.addItem(m.title(lang), m.id)
        if not base.municipalities():
            for g in base.map.get("municipalities", []): self.muni.addItem(g.get("name", g.get("id")), g.get("id"))
        idx = self.muni.findData(self.municipality); self.muni.setCurrentIndex(max(0, idx)); self.muni.currentIndexChanged.connect(self.set_municipality); top.addWidget(self.muni, 1)
        bar.box.addLayout(top)
        chips = QWidget(); flow = FlowLayout(chips, 6); kinds = sorted({p.get("type") for p in places if p.get("type")}, key=lambda k: type_name(k, lang))
        for key in [""] + kinds:
            b = button(t("all_types") if not key else type_name(key, lang), lambda checked=False, k=key: self.set_kind(k), "chip"); b.setCheckable(True); b.setChecked(key == self.kind); flow.addWidget(b)
        bar.box.addWidget(chips); self.col.addWidget(bar)
        found = self.filtered()
        self.col.addWidget(label(t("n_places", n=len(found)), "caption"))
        if not found:
            self.col.addWidget(EmptyState("umbrella", t("no_results") if places else t("empty_content"), "" if places else t("empty_content_text")))
        grid = ResponsiveGrid(250, 4, 14)
        for p in found[:self.limit]: grid.add(self.place_card(p))
        self.col.addWidget(grid)
        if len(found) > self.limit:
            self.col.addWidget(button(t("show_more"), self.more, "primary", "arrow-down"), 0, Qt.AlignHCenter)
        self.col.addStretch()
    def place_card(self, p):
        win = self.win; t = win.t; lang = win.lang; base = win.kb
        card = Clickable(10, 22); card.box.setSpacing(8)
        card.box.addWidget(Banner(lambda w, h, it=p: item_pixmap(win, it, w, h), 140, 16))
        card.box.addWidget(label(p.title(lang), "h3", wrap=True))
        tags = QHBoxLayout(); tags.setSpacing(6); mun = base.get(p.get("municipality", ""))
        if mun: tags.addWidget(Pill(mun.title(lang), "teal"))
        elif p.get("municipality"): tags.addWidget(Pill(p.get("municipality").replace("mun.", "").capitalize(), "teal"))
        if p.get("type"): tags.addWidget(Pill(type_name(p.get("type"), lang), "cyan"))
        tags.addStretch(); card.box.addLayout(tags)
        summary = label(clip(p.summary(lang), 150), "caption", wrap=True); card.box.addWidget(summary)
        card.box.addStretch()
        row = QHBoxLayout(); row.addWidget(button(t("read_more"), lambda i=p.id: win.open_item(i), "ghost", "arrow-right")); row.addStretch()
        mp = button("", lambda i=p.id: win.open("map", place=i), "icon", "map", t("show_on_map")); mp.setFixedSize(38, 38); row.addWidget(mp)
        if win.progress.is_read(p.id): row.insertWidget(1, Pill("✓", "green"))
        card.box.addLayout(row); card.clicked.connect(lambda i=p.id: win.open_item(i)); card.setAccessibleName(p.title(lang))
        return card
    def apply_query(self):
        self.query = self.search.text(); self.limit = self.PAGE; self.render(); self.search.setFocus(); self.search.setCursorPosition(len(self.query))
    def set_municipality(self, index):
        self.municipality = self.muni.itemData(index) or ""; self.limit = self.PAGE; QTimer.singleShot(0, self.render)
    def set_kind(self, key): self.kind = key; self.limit = self.PAGE; self.render()
    def more(self): self.limit += self.PAGE; self.render()
    def retranslate(self): self.render()
