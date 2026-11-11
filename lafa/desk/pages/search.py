"""Buka: one search over articles, municipalities, tourist places, national
days, the Constitution and Tetun words, in Tetun and Portuguese (accents and
apostrophes ignored)."""
from ...qt import Qt, QWidget, QVBoxLayout, QHBoxLayout
from ... import kb
from ...constitution import load as load_constitution, parse_ref
from ..texts import extend
from ..widgets import Card, Pill, ListRow, FlowLayout, label, button, scroll, section_title, clear_layout, EmptyState, clip
from .encyclopedia import thumb

extend({
    "search_title": ("Buka", "Pesquisa", "Search", "Pencarian"),
    "try_these": ("Koko buka:", "Experimente:", "Try:", "Coba cari:"),
    "words_found": ("Liafuan Tetun", "Palavras em tétum", "Tetun words", "Kata Tetun"),
    "results_count": ("rezultadu {n}", "{n} resultados", "{n} results", "{n} hasil"),
    "constitution_found": ("Iha Konstituisaun", "Na Constituição", "In the Constitution", "Dalam Konstitusi"),
    "open_constitution": ("Loke Konstituisaun", "Abrir a Constituição", "Open the Constitution", "Buka Konstitusi"),
})

SUGGESTIONS = ["bandeira", "Xanana", "Ataúro", "kafé", "tais", "Ramelau", "1999", "Santa Cruz", "Lafaek", "ASEAN", "Oe-Kusi", "Fundu Petrolíferu",
               "edukasaun", "futebol", "fósil", "F-FDTL", "Lene Hara", "inu nasionál"]
KIND_LABEL = {"article": ("kind_article", "violet"), "municipality": ("kind_municipality", "teal"), "place": ("kind_place", "cyan"), "day": ("kind_day", "rose")}

class SearchPage(QWidget):
    route = "search"
    def __init__(self, win):
        super().__init__(); self.win = win; self.query = ""
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(14)
        self.area = scroll(self.body); outer.addWidget(self.area)
    def show_route(self, params):
        self.query = str(params.get("q", self.query))[:200]
        if self.win.search.text() != self.query: self.win.search.setText(self.query)
        self.render()
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; base = win.kb; q = self.query.strip()
        self.col.addLayout(section_title(t("search_results", q=q) if q else t("search_title")))
        hits = base.search(q, lang, limit=60) if q else []
        words = base.search_words(q, win.settings.vocab_lang, limit=12) if q else []
        con = load_constitution(); articles = con.search(q, lang, limit=6) if q and (parse_ref(q) is None or q.lower().startswith("art")) else []
        if q: self.col.addWidget(label(t("results_count", n=len(hits) + len(words) + len(articles)), "caption"))
        if hits:
            card = Card(14, 24)
            for item, score in hits:
                key, acc = KIND_LABEL.get(item.kind, ("kind_article", "violet")); cat = kb.CATEGORY.get(item.category)
                pills = [(t(key), acc)] + ([(kb.text(cat.title, lang), cat.accent)] if cat and item.kind == "article" else [])
                r = ListRow(item.title(lang), clip(item.summary(lang), 180), pills, done=win.progress.is_read(item.id), thumb=thumb(item, win, (76, 52), 10))
                r.clicked.connect(lambda i=item.id: win.open_item(i)); card.box.addWidget(r)
            self.col.addWidget(card)
        if articles:
            cc = Card(14, 24); cc.box.addLayout(section_title(t("constitution_found"), button(t("open_constitution"), lambda: win.open("constitution", q=q), "ghost", "scales")))
            for a, _score, snippet in articles:
                r = ListRow(f"{'Artigu' if lang == 'tet' else 'Artigo'} {a['n']} · {kb.show(con.article_title(a, lang), lang)}", snippet, icon_name="scales", accent_key="indigo")
                r.clicked.connect(lambda n=a["n"]: win.open("constitution", article=n, q=q)); cc.box.addWidget(r)
            self.col.addWidget(cc)
        if words:
            wc = Card(14, 24); wc.box.addLayout(section_title(t("words_found"), button(t("learn_word"), lambda: win.open("language"), "ghost", "translate")))
            code = win.settings.vocab_lang
            for w in words:
                line = QHBoxLayout(); line.addWidget(label(kb.show(w.tet, "tet"), "h3"), 1)
                meaning = w.meaning(code) or w.meaning("en"); line.addWidget(label(meaning, wrap=True), 2)
                line.addWidget(Pill(code.upper() if w.meaning(code) else "EN", "mint")); wc.box.addLayout(line)
            self.col.addWidget(wc)
        if q and not hits and not words and not articles: self.col.addWidget(EmptyState("search", t("no_results")))
        tips = Card(14, 22); tips.box.addWidget(label(t("try_these"), "h3")); box = QWidget(); flow = FlowLayout(box, 6)
        for s in SUGGESTIONS:
            b = button(kb.show(s, "tet"), lambda checked=False, v=s: win.open("search", q=v), "chip"); flow.addWidget(b)
        tips.box.addWidget(box); self.col.addWidget(tips); self.col.addStretch()
    def retranslate(self): self.render()
