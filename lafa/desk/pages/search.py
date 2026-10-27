"""Buka: one search over articles, municipalities, tourist places, national
days and Tetun words, in all four languages (accents and apostrophes ignored)."""
from ...qt import Qt, QWidget, QVBoxLayout, QHBoxLayout
from ... import kb
from ..texts import extend
from ..widgets import Card, Pill, ListRow, FlowLayout, label, button, scroll, section_title, clear_layout, EmptyState, clip
from .encyclopedia import thumb

extend({
    "search_title": ("Buka", "Pesquisa", "Pencarian", "Search"),
    "try_these": ("Koko buka:", "Experimente:", "Coba cari:", "Try:"),
    "words_found": ("Liafuan Tetun", "Palavras em tétum", "Kata Tetun", "Tetun words"),
    "results_count": ("rezultadu {n}", "{n} resultados", "{n} hasil", "{n} results"),
})

SUGGESTIONS = ["bandeira", "Xanana", "Ataúro", "kafé", "tais", "Ramelau", "1999", "Santa Cruz", "Lafaek", "ASEAN", "Oe-Kusi", "Fundu Petrolíferu"]
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
        if q: self.col.addWidget(label(t("results_count", n=len(hits) + len(words)), "caption"))
        if hits:
            card = Card(14, 24)
            for item, score in hits:
                key, acc = KIND_LABEL.get(item.kind, ("kind_article", "violet")); cat = kb.CATEGORY.get(item.category)
                pills = [(t(key), acc)] + ([(kb.text(cat.title, lang), cat.accent)] if cat and item.kind == "article" else [])
                r = ListRow(item.title(lang), clip(item.summary(lang), 180), pills, done=win.progress.is_read(item.id), thumb=thumb(item, win, (76, 52), 10))
                r.clicked.connect(lambda i=item.id: win.open_item(i)); card.box.addWidget(r)
            self.col.addWidget(card)
        if words:
            wc = Card(14, 24); wc.box.addLayout(section_title(t("words_found"), button(t("learn_word"), lambda: win.open("language"), "ghost", "translate")))
            code = win.settings.vocab_lang
            for w in words:
                line = QHBoxLayout(); line.addWidget(label(kb.show(w.tet, "tet"), "h3"), 1)
                meaning = w.meaning(code) or w.meaning("en"); line.addWidget(label(meaning, wrap=True), 2)
                line.addWidget(Pill(code.upper() if w.meaning(code) else "EN", "mint")); wc.box.addLayout(line)
            self.col.addWidget(wc)
        if q and not hits and not words: self.col.addWidget(EmptyState("search", t("no_results")))
        tips = Card(14, 22); tips.box.addWidget(label(t("try_these"), "h3")); box = QWidget(); flow = FlowLayout(box, 6)
        for s in SUGGESTIONS:
            b = button(kb.show(s, "tet"), lambda checked=False, v=s: win.open("search", q=v), "chip"); flow.addWidget(b)
        tips.box.addWidget(box); self.col.addWidget(tips); self.col.addStretch()
    def retranslate(self): self.render()
