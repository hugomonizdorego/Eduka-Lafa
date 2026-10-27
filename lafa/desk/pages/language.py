"""Aprende lian: Tetun words with their meaning in Portuguese, Indonesian,
English and the other ASEAN and CPLP languages. Word list with categories,
flash cards with spaced repetition (Leitner boxes) and a short quiz."""
import random

from ...qt import (Qt, Signal, QTimer, QRectF, QColor, QPainter, QPen, QFont, QLinearGradient, QVariantAnimation, QEasingCurve,
                   QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QSizePolicy)
from ... import kb
from ..texts import extend
from ..theme import FONT_FAMILY
from ..widgets import (Card, ClayIcon, Pill, Segmented, ProgressRing, FlowLayout, SearchBox, label, button, scroll, section_title, clear_layout,
                       EmptyState, tok_of, qcolor)

extend({
    "lang_title": ("Aprende Tetun", "Aprender Tetun", "Belajar Tetun", "Learn Tetun"),
    "lang_sub": ("Liafuan {n} ho nia signifikadu iha lian {m}: Portugés, Indonéziu, Inglés no lian ASEAN no CPLP sira.", "{n} palavras com o significado em {m} línguas: português, indonésio, inglês e as línguas da ASEAN e da CPLP.",
                 "{n} kata dengan arti dalam {m} bahasa: Portugis, Indonesia, Inggris dan bahasa ASEAN serta CPLP.", "{n} words with their meaning in {m} languages: Portuguese, Indonesian, English and the ASEAN and CPLP languages."),
    "target_lang": ("Tradús ba", "Traduzir para", "Terjemahkan ke", "Translate to"),
    "tab_words": ("Liafuan", "Palavras", "Kata", "Words"),
    "tab_cards": ("Kartaun", "Cartões", "Kartu", "Flash cards"),
    "tab_quiz": ("Kuis", "Quiz", "Kuis", "Quiz"),
    "all_categories": ("Hotu", "Todas", "Semua", "All"),
    "word_level": ("Nível {n}", "Nível {n}", "Level {n}", "Level {n}"),
    "learned": ("Aprende ona", "Aprendidas", "Sudah dipelajari", "Learned"),
    "due_today": ("Atu repete ohin", "Para rever hoje", "Diulang hari ini", "Due today"),
    "flip": ("Klik ka Espasu atu haree signifikadu", "Clique ou Espaço para ver o significado", "Klik atau Spasi untuk melihat arti", "Click or Space to see the meaning"),
    "know": ("Hatene ona", "Já sei", "Sudah tahu", "I know it"),
    "dont_know": ("Seidauk hatene", "Ainda não sei", "Belum tahu", "Not yet"),
    "deck_done": ("Di'ak tebes! Kartaun ba ohin remata ona.", "Muito bem! Terminou os cartões de hoje.", "Bagus! Kartu hari ini selesai.", "Well done! Today's cards are finished."),
    "new_deck": ("Kartaun foun", "Novos cartões", "Kartu baru", "New cards"),
    "quiz_word": ("Saida mak “{w}” iha {language}?", "O que significa “{w}” em {language}?", "Apa arti “{w}” dalam {language}?", "What is “{w}” in {language}?"),
    "translation_note": ("Tradusaun ba lian ASEAN no CPLP sira: versaun provizória, presiza revizaun husi falante natív.", "Traduções para as línguas da ASEAN e da CPLP: versão provisória, a rever por falantes nativos.",
                         "Terjemahan ke bahasa ASEAN dan CPLP: versi sementara, perlu ditinjau penutur asli.", "Translations into ASEAN and CPLP languages: draft, to be reviewed by native speakers."),
    "missing_lang": ("Seidauk iha tradusaun {language}; hatudu Inglés.", "Ainda sem tradução em {language}; mostra-se o inglês.", "Belum ada terjemahan {language}; ditampilkan bahasa Inggris.", "No {language} translation yet; showing English."),
    "example": ("Ezemplu", "Exemplo", "Contoh", "Example"),
    "box": ("Kaixa {n}/5", "Caixa {n}/5", "Kotak {n}/5", "Box {n}/5"),
})

ORDER = ["pt", "es", "fr", "id", "ms", "fil", "th", "vi", "km", "lo", "my", "en", "zh", "ta"]
GROUP = {"pt": "CPLP", "es": "CPLP", "fr": "CPLP", "en": "ASEAN"}

def meaning(word, code):
    """The meaning in `code`, else English (returns text, used language)."""
    value = word.meaning(code)
    if value: return value, code
    return word.meaning("en") or word.meaning("pt"), "en"

class FlashCard(QWidget):
    """A card that flips (horizontal squeeze) between the Tetun word and its meaning."""
    clicked = Signal()
    def __init__(self, parent=None):
        super().__init__(parent); self.front = ("", ""); self.back = ("", "", ""); self.flipped = False; self.scale = 1.0
        self.setMinimumHeight(260); self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed); self.setFocusPolicy(Qt.StrongFocus); self.setCursor(Qt.PointingHandCursor)
        self.anim = QVariantAnimation(self); self.anim.setDuration(320); self.anim.setStartValue(0.0); self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.InOutCubic); self.anim.valueChanged.connect(self._step); self.animate = True
    def set_word(self, front, back):
        self.front = front; self.back = back; self.flipped = False; self.scale = 1.0; self.update()
    def flip(self):
        if not self.animate: self.flipped = not self.flipped; self.update(); return
        if self.anim.state() == QVariantAnimation.Running: return
        self._swapped = False; self.anim.start()
    def _step(self, v):
        v = float(v); self.scale = abs(1 - 2 * v)
        if v >= 0.5 and not self._swapped: self._swapped = True; self.flipped = not self.flipped
        self.update()
    def mouseReleaseEvent(self, e): self.clicked.emit()
    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter): self.clicked.emit(); return
        super().keyPressEvent(e)
    def paintEvent(self, e):
        t = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w = self.width() * max(0.02, self.scale); rect = QRectF((self.width() - w) / 2, 8, w, self.height() - 16)
        g = QLinearGradient(rect.topLeft(), rect.bottomRight())
        if self.flipped: g.setColorAt(0, QColor(t["glass_solid"])); g.setColorAt(1, QColor(t["primary_soft"]))
        else: g.setColorAt(0, QColor(t["nav_a"])); g.setColorAt(1, QColor(t["nav_b"]))
        p.setPen(QPen(QColor(t["focus"]), 3) if self.hasFocus() else Qt.NoPen); p.setBrush(g); p.drawRoundedRect(rect, 28, 28)
        if self.scale < 0.25: return
        f = QFont(FONT_FAMILY); inner = rect.adjusted(24, 20, -24, -20)
        if not self.flipped:
            word, sub = self.front; p.setPen(QColor("#ffffff"))
            f.setPixelSize(44 if len(word) < 18 else 32); f.setWeight(QFont.ExtraBold); p.setFont(f); p.drawText(inner.adjusted(0, 0, 0, -40), Qt.AlignCenter | Qt.TextWordWrap, word)
            f.setPixelSize(14); f.setWeight(QFont.DemiBold); p.setFont(f); p.setPen(QColor(255, 255, 255, 220)); p.drawText(inner, Qt.AlignHCenter | Qt.AlignBottom, sub)
        else:
            main, others, example = self.back; p.setPen(QColor(t["text"]))
            f.setPixelSize(34 if len(main) < 24 else 24); f.setWeight(QFont.ExtraBold); p.setFont(f); p.drawText(inner.adjusted(0, 0, 0, -90), Qt.AlignCenter | Qt.TextWordWrap, main)
            f.setPixelSize(15); f.setWeight(QFont.DemiBold); p.setFont(f); p.setPen(QColor(t["text2"])); p.drawText(inner.adjusted(0, inner.height() - 90, 0, -44), Qt.AlignCenter | Qt.TextWordWrap, others)
            f.setPixelSize(14); f.setItalic(True); p.setFont(f); p.setPen(QColor(t["muted"])); p.drawText(inner.adjusted(0, inner.height() - 44, 0, 0), Qt.AlignCenter | Qt.TextWordWrap, example)

class WordRow(QWidget):
    """One vocabulary line: Tetun, meaning, other languages, level and Leitner box."""
    def __init__(self, word, code, box, lang, parent=None):
        super().__init__(parent); self.box_ = box
        row = QHBoxLayout(self); row.setContentsMargins(12, 8, 12, 8); row.setSpacing(14)
        left = QVBoxLayout(); left.setSpacing(0); left.addWidget(label(kb.show(word.tet, "tet"), "h3", wrap=True)); left.addWidget(label(word.pos, "caption"))
        row.addLayout(left, 2)
        text_, used = meaning(word, code); mid = QVBoxLayout(); mid.setSpacing(0)
        m = label(text_, wrap=True); m.setStyleSheet("font-weight:800;"); mid.addWidget(m)
        others = " · ".join(f"{c.upper()}: {word.meaning(c)}" for c in ("pt", "id", "en") if c != code and word.meaning(c))
        mid.addWidget(label(others, "caption", wrap=True)); row.addLayout(mid, 3)
        row.addWidget(Pill(f"{word.level}", ("mint", "butter", "coral")[max(1, min(3, word.level)) - 1]), 0, Qt.AlignVCenter)
        self.setToolTip(kb.show(word.ex.get("tet", ""), "tet") + (" — " + word.ex.get("en", "") if word.ex.get("en") else "") if word.ex else "")
        self.setMinimumHeight(54)
    def paintEvent(self, e):
        t = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen); p.setBrush(qcolor(t["card_hover"])); p.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 14, 14)
        # Five dots = Leitner box.
        for i in range(5):
            p.setBrush(QColor(t["ok"]) if i < self.box_ else qcolor(t["track"])); p.drawEllipse(QRectF(self.width() - 16, 10 + i * 7, 5, 5))

class LanguagePage(QWidget):
    route = "language"
    PAGE = 60
    def __init__(self, win):
        super().__init__(); self.win = win; self.tab = "words"; self.cat = ""; self.level = 0; self.query = ""; self.limit = self.PAGE
        self.deck = []; self.quiz = []; self.qi = 0; self.score = 0; self.rng = random.Random()
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(14)
        self.area = scroll(self.body); outer.addWidget(self.area)
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.setInterval(300); self.timer.timeout.connect(self.apply_query)
    @property
    def code(self):
        c = self.win.settings.vocab_lang
        return c if c in kb.VOCAB_LANGS else "pt"
    def show_route(self, params):
        if params.get("tab") in ("words", "cards", "quiz"): self.tab = params["tab"]
        if params.get("cat") in kb.VOCAB_CATEGORIES: self.cat = params["cat"]
        self.render()
    def words(self):
        q = kb.fold(self.query).strip(); out = []
        source = self.win.kb.search_words(self.query, self.code, limit=5000) if q else self.win.kb.words
        for w in source:
            if self.cat and w.cat != self.cat: continue
            if self.level and w.level != self.level: continue
            out.append(w)
        return out
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; base = win.kb; prog = win.progress
        head = Card(20, 24); row = QHBoxLayout(); row.setSpacing(14); row.addWidget(ClayIcon("translate", "mint", 64))
        c = QVBoxLayout(); c.setSpacing(2); c.addWidget(label(t("lang_title"), "h1"))
        c.addWidget(label(t("lang_sub", n=len(base.words), m=len(kb.VOCAB_LANGS)), "muted", wrap=True)); row.addLayout(c, 1)
        pick = QVBoxLayout(); pick.addWidget(label(t("target_lang"), "caption")); self.combo = QComboBox()
        for code in ORDER: self.combo.addItem(f"{kb.VOCAB_LANG_NAMES[code]}" + (f"  ·  {GROUP[code]}" if code in GROUP else "  ·  ASEAN" if code not in ("pt", "es", "fr") else ""), code)
        self.combo.setCurrentIndex(max(0, self.combo.findData(self.code))); self.combo.currentIndexChanged.connect(self.set_code); pick.addWidget(self.combo)
        row.addLayout(pick); head.box.addLayout(row)
        # Stats.
        ids = [w.id for w in base.words]; learned = prog.words_learned(); due = len([i for i in prog.due_words(ids, 10 ** 6) if i in prog.words])
        stats = QHBoxLayout(); stats.setSpacing(18)
        ring = ProgressRing(learned / max(1, len(ids)), 86, 9, f"{learned}"); stats.addWidget(ring)
        for title, value in ((t("learned"), learned), (t("due_today"), due), (t("stat_words"), len(ids))):
            cc = QVBoxLayout(); cc.setSpacing(0); cc.addWidget(label(title, "muted")); cc.addWidget(label(str(value), "kpi")); stats.addLayout(cc)
        stats.addStretch(); head.box.addLayout(stats)
        missing = sum(1 for w in base.words if not w.meaning(self.code))
        if missing and base.words: head.box.addWidget(label(t("missing_lang", language=kb.VOCAB_LANG_NAMES[self.code]), "caption"))
        if self.code not in ("pt", "id", "en"): head.box.addWidget(label(t("translation_note"), "caption", wrap=True))
        tabs = Segmented([("words", t("tab_words")), ("cards", t("tab_cards")), ("quiz", t("tab_quiz"))], self.tab); tabs.changed.connect(self.set_tab)
        head.box.addWidget(tabs, 0, Qt.AlignLeft); self.col.addWidget(head)
        if not base.words:
            self.col.addWidget(EmptyState("translate", t("empty_content"), t("empty_content_text"))); self.col.addStretch(); return
        # Categories.
        chips = QWidget(); flow = FlowLayout(chips, 6); counts = {}
        for w in base.words: counts[w.cat] = counts.get(w.cat, 0) + 1
        b = button(f"{t('all_categories')} ({len(base.words)})", lambda checked=False: self.set_cat(""), "chip"); b.setCheckable(True); b.setChecked(not self.cat); flow.addWidget(b)
        for key, title in kb.VOCAB_CATEGORIES.items():
            if not counts.get(key): continue
            b = button(f"{kb.text(title, lang)} ({counts[key]})", lambda checked=False, k=key: self.set_cat(k), "chip"); b.setCheckable(True); b.setChecked(key == self.cat); flow.addWidget(b)
        self.col.addWidget(chips)
        getattr(self, "render_" + self.tab)()
        self.col.addStretch()
    # ---------------------------------------------------------------- list
    def render_words(self):
        win = self.win; t = win.t; prog = win.progress
        card = Card(14, 24); bar = QHBoxLayout()
        self.search = SearchBox(t("search_placeholder")); self.search.setText(self.query); self.search.textEdited.connect(lambda _: self.timer.start()); bar.addWidget(self.search, 1)
        lv = Segmented([("0", t("all_levels"))] + [(str(n), t("word_level", n=n)) for n in (1, 2, 3)], str(self.level)); lv.changed.connect(lambda k: self.set_level(int(k))); bar.addWidget(lv)
        card.box.addLayout(bar)
        words = self.words(); card.box.addWidget(label(f"{len(words)}", "caption"))
        rows = QVBoxLayout(); rows.setSpacing(6)
        for w in words[:self.limit]: rows.addWidget(WordRow(w, self.code, prog.word_box(w.id), win.lang))
        card.box.addLayout(rows)
        if not words: card.box.addWidget(EmptyState("search", t("no_results")))
        if len(words) > self.limit: card.box.addWidget(button(t("show_more"), self.more, "primary", "arrow-down"), 0, Qt.AlignHCenter)
        self.col.addWidget(card)
    # --------------------------------------------------------------- cards
    def new_deck(self):
        pool = [w.id for w in self.words()]
        self.deck = self.win.progress.due_words(pool, 20)
    def render_cards(self):
        win = self.win; t = win.t
        if not self.deck: self.new_deck()
        card = Card(20, 26)
        if not self.deck:
            card.box.addWidget(EmptyState("trophy", t("deck_done"))); card.box.addWidget(button(t("new_deck"), self.restart_deck, "primary", "refresh"), 0, Qt.AlignHCenter)
            self.col.addWidget(card); return
        word = win.kb.word_by_id.get(self.deck[0])
        if word is None: self.deck.pop(0); self.render(); return
        head = QHBoxLayout(); head.addWidget(Pill(kb.text(kb.VOCAB_CATEGORIES.get(word.cat, kb.VOCAB_CATEGORIES["phrases"]), win.lang), "mint"))
        head.addWidget(Pill(t("box", n=win.progress.word_box(word.id)), "lilac")); head.addStretch(); head.addWidget(label(f"{len(self.deck)}", "caption")); card.box.addLayout(head)
        self.flash = FlashCard(); self.flash.animate = not win.settings.reduce_motion
        text_, used = meaning(word, self.code)
        others = " · ".join(f"{c.upper()}: {word.meaning(c)}" for c in ("pt", "id", "en") if c != used and word.meaning(c))
        example = (kb.show(word.ex.get("tet", ""), "tet") + (" — " + word.ex.get("en", "") if word.ex.get("en") else "")) if word.ex else ""
        self.flash.set_word((kb.show(word.tet, "tet"), word.pos + " · " + t("flip")), (text_, others, example))
        self.flash.clicked.connect(self.flash.flip); card.box.addWidget(self.flash)
        row = QHBoxLayout(); row.addStretch()
        no = button(t("dont_know"), lambda: self.answer_card(False), None, "refresh"); no.setMinimumHeight(46); row.addWidget(no)
        yes = button(t("know"), lambda: self.answer_card(True), "primary", "check"); yes.setMinimumHeight(46); row.addWidget(yes); row.addStretch()
        card.box.addLayout(row); self.col.addWidget(card); QTimer.singleShot(0, self.flash.setFocus)
    def answer_card(self, correct):
        if not self.deck: return
        wid = self.deck.pop(0); self.win.progress.word_seen(wid, correct)
        if not correct: self.deck.append(wid) if len(self.deck) < 40 else None
        self.win.announce(self.win.progress._check_achievements()); self.win.update_profile(); self.render()
    def restart_deck(self): self.deck = []; self.new_deck(); self.render()
    # ---------------------------------------------------------------- quiz
    def new_quiz(self):
        words = self.words() or self.win.kb.words
        picks = self.rng.sample(words, min(10, len(words))); self.quiz = []
        for w in picks:
            same = [x for x in self.win.kb.words if x.cat == w.cat and x.id != w.id and meaning(x, self.code)[0] != meaning(w, self.code)[0]]
            pool = same if len(same) >= 3 else [x for x in self.win.kb.words if x.id != w.id]
            options = self.rng.sample(pool, 3) + [w]; self.rng.shuffle(options); self.quiz.append((w, options))
        self.qi = 0; self.score = 0
    def render_quiz(self):
        win = self.win; t = win.t
        if not self.quiz: self.new_quiz()
        card = Card(20, 26)
        if self.qi >= len(self.quiz):
            card.box.addWidget(ClayIcon("trophy", "butter", 72), 0, Qt.AlignHCenter)
            s = label(t("score", s=self.score, n=len(self.quiz)), "h2"); s.setAlignment(Qt.AlignCenter); card.box.addWidget(s)
            card.box.addWidget(button(t("again"), self.restart_quiz, "primary", "refresh"), 0, Qt.AlignHCenter); self.col.addWidget(card)
            try: win.progress.record(f"words:{self.cat or 'all'}", self.score, len(self.quiz))
            except ValueError: pass
            return
        word, options = self.quiz[self.qi]
        head = QHBoxLayout(); head.addWidget(label(t("question_n", i=self.qi + 1, n=len(self.quiz)), "eyebrow")); head.addStretch(); card.box.addLayout(head)
        q = label(t("quiz_word", w=kb.show(word.tet, "tet"), language=kb.VOCAB_LANG_NAMES[meaning(word, self.code)[1]]), "h2", wrap=True); card.box.addWidget(q)
        grid = QGridLayout(); grid.setSpacing(10); self.answers = []
        for j, o in enumerate(options):
            b = button(f"{'ABCD'[j]}.  {meaning(o, self.code)[0]}", lambda checked=False, k=j: self.answer_quiz(k), "answer"); b.setMinimumHeight(52)
            grid.addWidget(b, j // 2, j % 2); self.answers.append(b)
        card.box.addLayout(grid)
        self.quiz_feedback = label("", wrap=True); self.quiz_feedback.hide(); card.box.addWidget(self.quiz_feedback)
        self.quiz_next = button(t("next"), self.next_quiz, "primary", "arrow-right"); self.quiz_next.hide(); card.box.addWidget(self.quiz_next, 0, Qt.AlignRight)
        self.col.addWidget(card)
    def answer_quiz(self, k):
        word, options = self.quiz[self.qi]; right = options[k].id == word.id; t = self.win.t
        if not self.quiz_next.isHidden(): return
        if right: self.score += 1
        for j, b in enumerate(self.answers):
            b.setProperty("state", "right" if options[j].id == word.id else "wrong" if j == k else ""); b.style().unpolish(b); b.style().polish(b); b.setEnabled(False)
        self.win.progress.word_seen(word.id, right)
        extra = " · ".join(f"{c.upper()}: {word.meaning(c)}" for c in ("pt", "id", "en") if word.meaning(c))
        self.quiz_feedback.setText(f"<b>{t('right') if right else t('wrong')}</b> {kb.show(word.tet, 'tet')} = {extra}")
        self.quiz_feedback.setStyleSheet(f"background:{self.win.tok['ok_soft'] if right else self.win.tok['bad_soft']}; border-radius:14px; padding:10px 14px;")
        self.quiz_feedback.show(); self.quiz_next.show(); self.quiz_next.setFocus()
    def next_quiz(self): self.qi += 1; self.render()
    def restart_quiz(self): self.quiz = []; self.render()
    # ------------------------------------------------------------- filters
    def set_tab(self, key): self.tab = key; self.render()
    def set_cat(self, key): self.cat = key; self.limit = self.PAGE; self.deck = []; self.quiz = []; self.render()
    def set_level(self, n): self.level = n; self.limit = self.PAGE; self.deck = []; self.quiz = []; self.render()
    def set_code(self, index):
        code = self.combo.itemData(index)
        if code and code != self.win.settings.vocab_lang:
            self.win.settings.vocab_lang = code; self.win.save_quietly(); self.quiz = []; QTimer.singleShot(0, self.render)
    def apply_query(self):
        self.query = self.search.text(); self.limit = self.PAGE; self.render(); self.search.setFocus(); self.search.setCursorPosition(len(self.query))
    def more(self): self.limit += self.PAGE; self.render()
    def keyPressEvent(self, e):
        if self.tab == "quiz" and getattr(self, "answers", None) and e.key() in (Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4):
            self.answer_quiz(e.key() - Qt.Key_1); return
        if self.tab == "cards" and e.key() == Qt.Key_Right: self.answer_card(True); return
        if self.tab == "cards" and e.key() == Qt.Key_Left: self.answer_card(False); return
        super().keyPressEvent(e)
    def retranslate(self): self.render()
