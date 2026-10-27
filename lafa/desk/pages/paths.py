"""Nível eskola: learning paths for the school levels of the Ministry of
Education (Ensinu Báziku cycles 1–3, Ensinu Sekundáriu, Ensinu Superiór and
adults). Each level has units (one per topic) with articles and a unit quiz."""
import random

from ...qt import Qt, QWidget, QVBoxLayout, QHBoxLayout
from ... import kb
from ..texts import extend
from ..widgets import Card, Clickable, ClayIcon, Pill, ProgressLine, ResponsiveGrid, ListRow, label, button, scroll, section_title, clear_layout, EmptyState
from .article import QuizWidget, level_range
from .encyclopedia import thumb

extend({
    "paths_title": ("Aprende tuir nível eskola", "Aprender por nível escolar", "Belajar sesuai jenjang sekolah", "Learn by school level"),
    "paths_sub": ("Nível sira tuir Ministériu Edukasaun (moe.gov.tl). Hili ita-nia nível: Lafa hatudu artigu no kuis ne'ebé loos ba ita.",
                  "Níveis do Ministério da Educação (moe.gov.tl). Escolha o seu nível: o Lafa mostra os artigos e quizzes certos para si.",
                  "Jenjang menurut Kementerian Pendidikan (moe.gov.tl). Pilih jenjangmu: Lafa menampilkan artikel dan kuis yang cocok.",
                  "Levels of the Ministry of Education (moe.gov.tl). Pick your level: Lafa shows the right articles and quizzes for you."),
    "my_level": ("Ha'u-nia nível", "O meu nível", "Jenjang saya", "My level"),
    "choose_level": ("Hili nível ne'e", "Escolher este nível", "Pilih jenjang ini", "Choose this level"),
    "units": ("Unidade sira", "Unidades", "Unit", "Units"),
    "unit_quiz": ("Kuis unidade", "Quiz da unidade", "Kuis unit", "Unit quiz"),
    "unit_done": ("Unidade remata ona!", "Unidade concluída!", "Unit selesai!", "Unit complete!"),
    "unit_pass": ("Hatán loos 70% ka liu atu remata unidade.", "Acerte 70% ou mais para concluir a unidade.", "Jawab benar 70% atau lebih untuk menyelesaikan unit.", "Get 70% or more to complete the unit."),
    "start_unit": ("Hahú", "Começar", "Mulai", "Start"),
    "system_title": ("Sistema edukasaun Timór-Leste nian", "O sistema educativo de Timor-Leste", "Sistem pendidikan Timor-Leste", "Timor-Leste's education system"),
    "system_text": ("Lei-Inan Artigu 59: Estadu harii sistema ensinu báziku universál, obrigatóriu no, wainhira bele, saugati. Lei Bázika Edukasaun (Lei n.º 14/2008) organiza: edukasaun pré-eskolár; Ensinu Báziku tinan 9 (siklu 1: klase 1–4, siklu 2: klase 5–6, siklu 3: klase 7–9); Ensinu Sekundáriu tinan 3 (jerál ka tékniku-vokasionál); no Ensinu Superiór (universidade no politékniku).",
                    "Constituição, artigo 59: o Estado garante um ensino básico universal, obrigatório e, na medida do possível, gratuito. A Lei de Bases da Educação (Lei n.º 14/2008) organiza: educação pré-escolar; Ensino Básico de 9 anos (1.º ciclo: 1.º–4.º anos, 2.º ciclo: 5.º–6.º, 3.º ciclo: 7.º–9.º); Ensino Secundário de 3 anos (geral ou técnico-vocacional); e Ensino Superior (universitário e politécnico).",
                    "Konstitusi Pasal 59: negara menjamin pendidikan dasar yang universal, wajib dan, sejauh mungkin, gratis. Undang-Undang Dasar Pendidikan (UU No. 14/2008) mengatur: pendidikan prasekolah; Pendidikan Dasar 9 tahun (siklus 1: kelas 1–4, siklus 2: kelas 5–6, siklus 3: kelas 7–9); Pendidikan Menengah 3 tahun (umum atau teknik-kejuruan); dan Pendidikan Tinggi (universitas dan politeknik).",
                    "Constitution, Article 59: the State provides universal and compulsory basic education, free of charge as far as possible. The Education System Framework Law (Law No. 14/2008) sets out: pre-school education; 9 years of Basic Education (cycle 1: grades 1–4, cycle 2: grades 5–6, cycle 3: grades 7–9); 3 years of Secondary Education (general or technical-vocational); and Higher Education (university and polytechnic)."),
    "open_moe": ("Loke moe.gov.tl", "Abrir moe.gov.tl", "Buka moe.gov.tl", "Open moe.gov.tl"),
})

LEVEL_LOOK = {"eb1": ("sun", "butter"), "eb2": ("star", "peach"), "eb3": ("book-open", "violet"), "es": ("graduation", "pink"), "sup": ("crown", "indigo")}

class PathsPage(QWidget):
    route = "paths"
    def __init__(self, win):
        super().__init__(); self.win = win; self.level = None; self.focus_cat = None; self.quiz_for = None
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(16)
        self.area = scroll(self.body); outer.addWidget(self.area)
    def show_route(self, params):
        if self.level is None: self.level = self.win.settings.school_level if self.win.settings.school_level in kb.LEVELS else "eb3"
        if params.get("level") in kb.LEVELS: self.level = params["level"]
        self.focus_cat = params.get("category") if params.get("category") in kb.CATEGORY else None
        self.quiz_for = None; self.render()
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; base = win.kb; prog = win.progress
        head = Card(20, 24); row = QHBoxLayout(); row.setSpacing(14); row.addWidget(ClayIcon("graduation", "lilac", 64))
        c = QVBoxLayout(); c.setSpacing(2); c.addWidget(label(t("paths_title"), "h1", wrap=True)); c.addWidget(label(t("paths_sub"), "muted", wrap=True)); row.addLayout(c, 1)
        head.box.addLayout(row); self.col.addWidget(head)
        # The five levels.
        grid = ResponsiveGrid(190, 5, 12)
        for lv in kb.LEVELS:
            icon_name, acc = LEVEL_LOOK[lv]; items = [a for a in base.articles(None, lv) if a.kind == "article"]
            done = sum(1 for a in items if prog.is_read(a.id)); chosen = lv == self.level
            card = Clickable(12, 22, gradient=(win.tok["nav_a"], win.tok["nav_b"]) if chosen else None)
            card.box.addWidget(ClayIcon(icon_name, acc, 52))
            name = label(kb.LEVEL_SHORT[lv], "h2"); full = label(kb.text(kb.LEVEL_NAMES[lv], lang), "caption", wrap=True)
            card.box.addWidget(name); card.box.addWidget(full); card.box.addStretch()
            bar = ProgressLine(done / max(1, len(items)), 8, colors=("#ffffff", "#ffe4f2") if chosen else None); card.box.addWidget(bar)
            if chosen:
                for l in (name, full): l.setStyleSheet("color:white;")
            if lv == win.settings.school_level: card.box.addWidget(Pill(t("my_level"), "green"))
            card.clicked.connect(lambda k=lv: self.set_level(k)); card.setAccessibleName(kb.text(kb.LEVEL_NAMES[lv], lang)); grid.add(card)
        self.col.addWidget(grid)
        if self.level != win.settings.school_level:
            self.col.addWidget(button(t("choose_level"), self.make_mine, "primary", "check"), 0, Qt.AlignLeft)
        # Units of the chosen level.
        units = base.path(self.level)
        if self.focus_cat: units.sort(key=lambda u: u["category"] != self.focus_cat)
        self.col.addLayout(section_title(f"{t('units')} · {kb.LEVEL_SHORT[self.level]}"))
        if not units: self.col.addWidget(EmptyState("graduation", t("empty_content"), t("empty_content_text")))
        for unit in units: self.col.addWidget(self.unit_card(unit))
        # The school system (Constitution art. 59 and the education law).
        sysc = Card(18, 24); sysc.box.addLayout(section_title(t("system_title"), button(t("open_moe"), lambda: win.open_url("https://moe.gov.tl/"), "ghost", "globe") if win.online else None))
        sysc.box.addWidget(label(t("system_text"), "body", wrap=True))
        sysc.box.addWidget(label(f"{t('sources')}: Konstituisaun RDTL (Artigu 59) · Lei n.º 14/2008 (Lei de Bases da Educação) · moe.gov.tl", "caption", wrap=True))
        self.col.addWidget(sysc); self.col.addStretch()
    def unit_card(self, unit):
        win = self.win; t = win.t; lang = win.lang; prog = win.progress; cat = kb.CATEGORY[unit["category"]]
        items = unit["items"]; done = sum(1 for i in items if prog.is_read(i.id)); key = f"{self.level}:{unit['category']}"
        finished = f"unit:{key}" in prog.achievements
        card = Card(16, 24); head = QHBoxLayout(); head.setSpacing(12); head.addWidget(ClayIcon(cat.icon, cat.accent, 48))
        c = QVBoxLayout(); c.setSpacing(2); c.addWidget(label(kb.text(cat.title, lang), "h2")); c.addWidget(label(kb.text(cat.summary, lang), "caption", wrap=True)); head.addLayout(c, 1)
        head.addWidget(Pill(t("unit_progress", done=done, n=len(items)), cat.accent))
        if finished: head.addWidget(Pill("✓ " + t("unit_done"), "green"))
        card.box.addLayout(head); card.box.addWidget(ProgressLine(done / max(1, len(items)), 8))
        for item in items[:8 if unit["category"] != self.focus_cat else 30]:
            lr = level_range(item.levels())
            r = ListRow(item.title(lang), "", [(f"{t('level')} {lr}", "lilac")] if lr else [], done=prog.is_read(item.id), thumb=thumb(item, win, (64, 44), 10))
            r.clicked.connect(lambda i=item.id: win.open_item(i)); card.box.addWidget(r)
        if len(items) > 8 and unit["category"] != self.focus_cat:
            card.box.addWidget(button(t("see_all") + f" ({len(items)})", lambda k=unit["category"]: self.win.open("paths", category=k, level=self.level), "ghost", "arrow-down"), 0, Qt.AlignLeft)
        actions = QHBoxLayout()
        first = next((i for i in items if not prog.is_read(i.id)), items[0] if items else None)
        if first: actions.addWidget(button(t("start_unit"), lambda i=first.id: win.open_item(i), "primary", "play"))
        actions.addWidget(button(t("unit_quiz"), lambda k=unit["category"]: self.open_quiz(k), None, "trophy")); actions.addStretch(); card.box.addLayout(actions)
        if self.quiz_for == unit["category"]:
            lo, hi = kb.LEVEL_DIFFICULTY[self.level]; ids = {i.id for i in items}
            pool = [q for q in win.kb.questions(unit["category"], lo, hi) if q["item"] in ids] or [q for q in win.kb.questions(unit["category"]) if q["item"] in ids]
            picks = random.sample(pool, min(8, len(pool)))
            card.box.addWidget(label(t("unit_pass"), "caption"))
            quiz = QuizWidget(win, f"unit:{key}", [p["q"] for p in picks]); quiz.finished.connect(lambda s, n, k=key: self.quiz_done(k, s, n)); card.box.addWidget(quiz)
        return card
    def open_quiz(self, category): self.quiz_for = None if self.quiz_for == category else category; self.render()
    def quiz_done(self, key, score, total):
        if total and score / total >= 0.7:
            self.win.progress.unit_done(key); self.win.toast.show_text("★  " + self.win.t("unit_done")); self.win.update_profile()
    def set_level(self, lv): self.level = lv; self.quiz_for = None; self.focus_cat = None; self.render()
    def make_mine(self):
        self.win.settings.school_level = self.level; self.win.save_quietly(); self.win.update_profile(); self.render()
    def retranslate(self): self.render()
