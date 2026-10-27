"""Reading page for every encyclopedia item: articles, municipalities, tourist
places and national days. One scrolling page (no nested scroll areas):
banner, actions, Read / Quiz, simple or complete text, key facts, mini map,
timeline, related pages, sources with licences and the review note."""
import html
from datetime import date
from urllib.parse import quote

from ...qt import Qt, Signal, QTimer, QSize, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTextBrowser, QFrame, QPixmap, QSizePolicy, QUrl
from ... import kb, icons
from ..texts import extend
from ..theme import accent
from ..widgets import (Card, Clickable, ClayIcon, Pill, Segmented, ProgressLine, Banner, ResponsiveGrid, FlowLayout, label, button, scroll,
                       section_title, clear_layout, tok_of, refresh_icon, EmptyState)

extend({
    "levels_label": ("Ba nível", "Para os níveis", "Untuk jenjang", "For levels"),
    "this_year": ("Tinan ne'e: {date}", "Este ano: {date}", "Tahun ini: {date}", "This year: {date}"),
    "variable_date": ("Data muda kada tinan", "Data móvel", "Tanggal berubah tiap tahun", "Date changes every year"),
    "photo_offline": ("Foto download ona", "Foto descarregada", "Foto sudah diunduh", "Downloaded photo"),
    "cite": ("Oinsá sita", "Como citar", "Cara mengutip", "How to cite"),
    "keyboard_quiz": ("Teklas 1–4 ka A–D atu hatán, Enter ba tuir mai", "Teclas 1–4 ou A–D para responder, Enter para seguir", "Tombol 1–4 atau A–D untuk menjawab, Enter untuk lanjut", "Keys 1–4 or A–D to answer, Enter for next"),
})

LEVEL_ORDER = kb.LEVELS

def level_range(levels):
    idx = sorted(LEVEL_ORDER.index(l) for l in levels if l in LEVEL_ORDER)
    if not idx: return ""
    a, b = kb.LEVEL_SHORT[LEVEL_ORDER[idx[0]]], kb.LEVEL_SHORT[LEVEL_ORDER[idx[-1]]]
    return a if a == b else f"{a}–{b}"

class AutoText(QTextBrowser):
    """Rich text that grows to its content (the page scrolls, not the text)."""
    link = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent); self.setOpenLinks(False); self.setFrameShape(QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed); self.anchorClicked.connect(lambda url: self.link.emit(url.toString()))
        self.document().setDocumentMargin(2)
    def setHtml(self, text):
        super().setHtml(text); QTimer.singleShot(0, self.fit); self.fit()
    def fit(self):
        self.document().setTextWidth(max(100, self.viewport().width()))
        self.setFixedHeight(int(self.document().size().height()) + 6)
    def resizeEvent(self, e):
        super().resizeEvent(e); self.fit()

def css(tok, scale=1.0):
    fs = lambda px: f"{round(px * scale)}px"
    return (f"body {{ color:{tok['text']}; font-size:{fs(15)}; }} h2 {{ font-size:{fs(19)}; font-weight:800; margin-top:14px; margin-bottom:4px; color:{tok['text']}; }}"
            f"h3 {{ font-size:{fs(16)}; font-weight:700; margin-top:10px; color:{tok['text']}; }} p {{ line-height:155%; margin-top:2px; margin-bottom:10px; }}"
            f"a {{ color:{tok['primary']}; text-decoration:none; font-weight:700; }} .muted {{ color:{tok['muted']}; font-size:{fs(13)}; }}"
            f"li {{ margin-bottom:6px; line-height:145%; }}")

class QuizWidget(QWidget):
    """Questions one at a time; explanation after each answer; score saved."""
    finished = Signal(int, int)
    def __init__(self, win, key, questions, parent=None):
        super().__init__(parent); self.win = win; self.key = key; self.questions = questions; self.i = 0; self.score = 0; self.answered = False
        self.col = QVBoxLayout(self); self.col.setContentsMargins(0, 0, 0, 0); self.col.setSpacing(10)
        self.setFocusPolicy(Qt.StrongFocus); self.render()
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang
        if not self.questions: self.col.addWidget(label(t("no_quiz"), "muted", wrap=True)); return
        if self.i >= len(self.questions):
            ok = self.score == len(self.questions)
            self.col.addWidget(ClayIcon("trophy" if ok else "target", "butter" if ok else "violet", 64), 0, Qt.AlignHCenter)
            s = label(t("score", s=self.score, n=len(self.questions)), "h2"); s.setAlignment(Qt.AlignCenter); self.col.addWidget(s)
            self.col.addWidget(button(t("again"), self.restart, "primary", "refresh"), 0, Qt.AlignHCenter); return
        q = self.questions[self.i]
        head = QHBoxLayout(); head.addWidget(label(t("question_n", i=self.i + 1, n=len(self.questions)), "eyebrow"), 1)
        d = q.get("difficulty", 5); head.addWidget(Pill(f"★ {d}", "butter" if d <= 5 else "peach" if d <= 10 else "coral")); self.col.addLayout(head)
        bar = ProgressLine(self.i / len(self.questions), 8); self.col.addWidget(bar)
        self.col.addWidget(label(kb.text(q["q"], lang), "h2", wrap=True))
        self.buttons = []
        for j, option in enumerate(q["options"]):
            b = button(f"{'ABCD'[j]}.  {kb.text(option, lang)}", lambda checked=False, k=j: self.choose(k), "answer"); b.setMinimumHeight(48)
            self.col.addWidget(b); self.buttons.append(b)
        self.feedback = label("", wrap=True); self.feedback.hide(); self.col.addWidget(self.feedback)
        self.next_button = button(t("next") if self.i + 1 < len(self.questions) else t("finish"), self.next, "primary", "arrow-right"); self.next_button.hide(); self.col.addWidget(self.next_button, 0, Qt.AlignRight)
        self.col.addWidget(label(t("keyboard_quiz"), "caption")); self.answered = False
    def choose(self, k):
        if self.answered or self.i >= len(self.questions): return
        self.answered = True; q = self.questions[self.i]; right = k == q["answer"]; lang = self.win.lang; t = self.win.t
        if right: self.score += 1
        for j, b in enumerate(self.buttons):
            state = "right" if j == q["answer"] else "wrong" if j == k else ""
            b.setProperty("state", state); b.style().unpolish(b); b.style().polish(b); b.setEnabled(j in (k, q["answer"]))
        tok = tok_of(self)
        self.feedback.setText(f"<b>{t('right') if right else t('wrong')}</b> {html.escape(kb.text(q.get('why'), lang))}")
        self.feedback.setStyleSheet(f"background:{tok['ok_soft'] if right else tok['bad_soft']}; border-radius:14px; padding:10px 14px;")
        self.feedback.show(); self.next_button.show(); self.next_button.setFocus()
    def next(self):
        self.i += 1
        if self.i >= len(self.questions):
            try: self.win.progress.record(self.key, self.score, len(self.questions))
            except ValueError: pass
            self.win.update_profile(); self.finished.emit(self.score, len(self.questions))
        self.render()
    def restart(self): self.i = 0; self.score = 0; self.render()
    def keyPressEvent(self, e):
        keys = {Qt.Key_1: 0, Qt.Key_2: 1, Qt.Key_3: 2, Qt.Key_4: 3, Qt.Key_A: 0, Qt.Key_B: 1, Qt.Key_C: 2, Qt.Key_D: 3}
        if e.key() in keys and not self.answered: self.choose(keys[e.key()]); return
        if e.key() in (Qt.Key_Return, Qt.Key_Enter) and self.answered: self.next(); return
        super().keyPressEvent(e)

class ItemPage(QWidget):
    route = "item"
    def __init__(self, win):
        super().__init__(); self.win = win; self.item = None; self.tab = "read"; self.depth = "complete"
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(14)
        self.area = scroll(self.body); outer.addWidget(self.area)
    def show_route(self, params):
        item = self.win.kb.get(params.get("id", ""))
        if item is not self.item: self.tab = params.get("tab", "read"); self.area.verticalScrollBar().setValue(0)
        self.item = item; self.render()
        if item: self.win.mark_opened(item)
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; item = self.item; base = win.kb
        if item is None: self.col.addWidget(EmptyState("search", t("no_results"))); return
        cat = kb.CATEGORY.get(item.category, kb.CATEGORIES[0])
        photo = win.store.photo(item.id) if getattr(win, "store", None) else None
        def picture(w, h, it=item, ph=photo):
            if ph:
                pm = QPixmap(str(ph[0]))
                if not pm.isNull(): return cover(pm, w, h)
            return icons.illustration(it.illustration(), w, h)
        self.col.addWidget(Banner(picture, 230, 26, item.title(lang), kb.text(cat.title, lang)))
        # Pills and actions.
        row = QHBoxLayout(); row.setSpacing(8)
        row.addWidget(Pill(kb.text(cat.title, lang), cat.accent))
        lr = level_range(item.levels())
        if lr: row.addWidget(Pill(f"{t('level')} {lr}", "lilac"))
        if item.kind == "day": row.addWidget(Pill(t("holiday") if item.get("type") == "holiday" else t("commemorative"), "rose"))
        if item.kind == "place" and item.get("type"): row.addWidget(Pill(str(item.get("type")).replace("_", " "), "cyan"))
        row.addWidget(Pill(t("review_ok") if item.review_status() == "reviewed" else t("review_draft"), "green" if item.review_status() == "reviewed" else "butter"))
        row.addStretch()
        fav = win.progress.is_favourite(item.kind if item.kind != "municipality" else "municipality", item.id)
        self.save_button = button(t("saved") if fav else t("save"), self.toggle_save, "chip", "star"); row.addWidget(self.save_button)
        if win.voice_available(): row.addWidget(button(t("read_aloud"), self.read_aloud, "chip", "speaker"))
        if item.kind in ("place", "municipality"): row.addWidget(button(t("show_on_map"), self.show_on_map, "chip", "map"))
        wiki = item.wiki()
        if wiki and win.online: row.addWidget(button(t("wiki_online"), self.open_wiki, "chip", "globe"))
        self.col.addLayout(row)
        tabs = QHBoxLayout(); self.tabs = Segmented([("read", t("read_tab")), ("quiz", f"{t('quiz_tab')} ({len(item.quiz())})")], self.tab)
        self.tabs.changed.connect(self.set_tab); tabs.addWidget(self.tabs)
        if self.tab == "read":
            self.depth_switch = Segmented([("simple", t("simple")), ("complete", t("complete"))], self.depth); self.depth_switch.changed.connect(self.set_depth); tabs.addSpacing(10); tabs.addWidget(self.depth_switch)
        tabs.addStretch(); self.col.addLayout(tabs)
        if self.tab == "quiz":
            card = Card(20, 24); card.box.addWidget(label(t("article_quiz"), "h2"))
            quiz = QuizWidget(win, f"quiz:{item.id}", item.quiz()); card.box.addWidget(quiz); self.col.addWidget(card); quiz.setFocus(); self.col.addStretch(); return
        # Main text and the side column.
        body = ResponsiveGrid(330, 2, 16); body.max_columns = 2
        main = Card(22, 24)
        summary = label(item.summary(lang), "body", wrap=True); summary.setStyleSheet("font-size:%dpx; font-weight:600;" % round(17 * win.scale())); main.box.addWidget(summary)
        if item.kind == "day":
            when = base.day_date(item, date.today().year)
            main.box.addWidget(Pill(t("this_year", date=kb.format_date(when, lang)) if when else t("variable_date"), "rose"))
        text = AutoText(); text.document().setDefaultStyleSheet(css(win.tok, win.scale())); text.link.connect(self.follow)
        parts = []
        if self.depth == "complete":
            for heading, para in item.sections(lang):
                if heading: parts.append(f"<h2>{html.escape(heading)}</h2>")
                parts += [f"<p>{html.escape(p)}</p>" for p in para.split("\n") if p.strip()]
            tips = kb.text(item.get("tips"), lang) if item.kind == "place" else ""
            if tips: parts.append(f"<h2>{html.escape(t('visit_tips'))}</h2><p>{html.escape(tips)}</p>")
            extract = win.store.extract(item.id, lang) if getattr(win, "store", None) else None
            if extract:
                parts.append(f"<h2>{html.escape(t('offline_extract'))}</h2><p>{html.escape(extract['text'][:2500])}</p>"
                             f"<p class='muted'>{html.escape(extract.get('source', 'Wikipedia'))} · <a href='{html.escape(extract['url'])}'>{html.escape(extract['url'])}</a></p>")
        else:
            facts = item.get("facts") or []
            if facts: parts.append("<ul>" + "".join(f"<li><b>{html.escape(kb.text(f.get('label'), lang))}:</b> {html.escape(kb.text(f.get('value'), lang) if isinstance(f.get('value'), dict) else str(f.get('value')))}</li>" for f in facts[:6]) + "</ul>")
        text.setHtml("".join(parts) or "<p></p>"); main.box.addWidget(text)
        caption = item.caption(lang)
        credit = (t("photo_credit", author=photo[1].get("author", ""), licence=photo[1].get("licence", "")) if photo else t("illustration_credit"))
        main.box.addWidget(label((caption + " · " if caption else "") + credit, "caption", wrap=True))
        body.add(main)
        side = QWidget(); scol = QVBoxLayout(side); scol.setContentsMargins(0, 0, 0, 0); scol.setSpacing(14)
        if item.kind == "municipality": scol.addWidget(self.municipality_card(item))
        if item.kind in ("municipality", "place"): scol.addWidget(self.mini_map(item))
        facts = item.get("facts") or []
        if facts and self.depth == "complete":
            fc = Card(16, 22); fc.box.addLayout(section_title(t("key_facts")))
            for f in facts[:10]:
                value = kb.text(f.get("value"), lang) if isinstance(f.get("value"), dict) else str(f.get("value"))
                line = QVBoxLayout(); line.setSpacing(0); line.addWidget(label(kb.text(f.get("label"), lang) + (f" ({f['year']})" if f.get("year") else ""), "caption", wrap=True))
                line.addWidget(label(value, "h3", wrap=True)); fc.box.addLayout(line)
            scol.addWidget(fc)
        timeline = item.get("timeline") or []
        if timeline:
            tc = Card(16, 22); tc.box.addLayout(section_title(t("timeline_title")))
            for e in sorted(timeline, key=lambda e: kb.parse_when(e.get("date")) or (0, 0, 0))[:12]:
                line = QHBoxLayout(); line.setSpacing(10); dot = QLabel(); dot.setFixedSize(10, 10); dot.setStyleSheet(f"background:{accent(cat.accent)[0]}; border-radius:5px;")
                line.addWidget(dot, 0, Qt.AlignTop); c2 = QVBoxLayout(); c2.setSpacing(0); c2.addWidget(label(kb.format_when(e.get("date"), lang), "eyebrow")); c2.addWidget(label(kb.text(e.get("title"), lang), wrap=True)); line.addLayout(c2, 1); tc.box.addLayout(line)
            scol.addWidget(tc)
        related = base.related(item)
        if related:
            rc = Card(16, 22); rc.box.addLayout(section_title(t("related")))
            for r in related[:8]:
                rr = Clickable(6, 14); line = QHBoxLayout(); rcat = kb.CATEGORY.get(r.category, cat); line.addWidget(ClayIcon(rcat.icon, rcat.accent, 30))
                line.addWidget(label(r.title(lang), wrap=True), 1); rr.box.addLayout(line); rr.clicked.connect(lambda i=r.id: win.open_item(i)); rc.box.addWidget(rr)
            scol.addWidget(rc)
        scol.addStretch(); body.add(side); self.col.addWidget(body)
        # Sources, licences and review.
        sc = Card(20, 24); sc.box.addLayout(section_title(t("sources")))
        src = AutoText(); src.document().setDefaultStyleSheet(css(win.tok, win.scale())); src.link.connect(self.follow)
        items_html = []
        for s in item.sources():
            lic = f" · {html.escape(t('licence'))}: {html.escape(s.get('licence', ''))}" if s.get("licence") else ""
            items_html.append(f"<li><b>{html.escape(s.get('title', ''))}</b> — {html.escape(s.get('publisher', ''))}{lic}<br>"
                              f"<a href='{html.escape(s['url'])}'>{html.escape(s['url'])}</a> <span class='muted'>({html.escape(t('accessed', date=s.get('accessed', '')))})</span></li>")
        review = item.get("review") if isinstance(item.get("review"), dict) else {}
        note = f"<p class='muted'>{html.escape(t('review_draft'))}{(': ' + html.escape(review.get('notes', ''))) if review.get('notes') and item.review_status() != 'reviewed' else ''}</p>" if item.review_status() != "reviewed" else ""
        cite = f"<p class='muted'><b>{html.escape(t('cite'))}:</b> Lafa – {html.escape(t('app_subtitle'))}, “{html.escape(item.title(lang))}”, {date.today().year}. CC BY-SA 4.0.</p>"
        src.setHtml("<ol>" + "".join(items_html) + "</ol>" + note + cite); sc.box.addWidget(src); self.col.addWidget(sc)
        self.col.addStretch()
    def municipality_card(self, item):
        win = self.win; t = win.t; lang = win.lang; c = Card(16, 22); c.box.addLayout(section_title(t("municipality")))
        pop = item.get("population") or {}
        for key, value in (("capital", kb.text(item.get("capital"), lang)),
                           ("area", f"{item.get('area_km2'):,} km²".replace(",", " ") if isinstance(item.get("area_km2"), (int, float)) else ""),
                           ("population", f"{pop.get('value'):,}".replace(",", " ") + f" ({pop.get('year')})" if pop.get("value") else ""),
                           ("languages_spoken", kb.text(item.get("languages"), lang)), ("products", kb.text(item.get("products"), lang))):
            if value:
                line = QVBoxLayout(); line.setSpacing(0); line.addWidget(label(t(key), "caption")); line.addWidget(label(value, "h3", wrap=True)); c.box.addLayout(line)
        posts = item.get("posts") or []
        if posts:
            c.box.addWidget(label(t("posts"), "caption")); box = QWidget(); flow = FlowLayout(box, 6)
            for p in posts: flow.addWidget(Pill(p, "teal"))
            c.box.addWidget(box)
        return c
    def mini_map(self, item):
        from .mapview import MapWidget
        win = self.win; c = Card(8, 22); m = MapWidget(win.kb, win.lang, interactive=False); m.setFixedHeight(220); m.show_labels = item.kind == "municipality"
        if item.kind == "place" and isinstance(item.get("lat"), (int, float)):
            m.pin = item.id; m.show_places = True; m.focus_on(item.get("lon"), item.get("lat"), 2.0)
        if item.kind == "municipality":
            geo = next((g for g in m.munis if g["name"] == item.get("geo")), None)
            if geo: m.selected = geo["id"]
            m.show_places = False
        c.box.addWidget(m); c.box.addWidget(button(win.t("show_on_map"), self.show_on_map, "ghost", "map"))
        return c
    def set_tab(self, key): self.tab = key; self.render()
    def set_depth(self, key): self.depth = key; self.render()
    def toggle_save(self):
        try:
            on = self.win.progress.toggle_favourite(self.item.kind, self.item.id, self.item.title(self.win.lang))
            self.save_button.setText(self.win.t("saved") if on else self.win.t("save"))
        except (ValueError, OSError) as e: self.win.toast.show_text(str(e))
    def read_aloud(self):
        lang = self.win.lang; item = self.item
        text = item.title(lang) + ". " + item.summary(lang) + " " + " ".join(p for _, p in item.sections(lang))
        self.win.speak(text, lang)
    def show_on_map(self):
        if self.item.kind == "place": self.win.open("map", place=self.item.id)
        else: self.win.open("map", municipality=self.item.id)
    def open_wiki(self):
        wiki = self.item.wiki(); lang = self.win.lang
        for code in (lang, "pt", "en", "id"):
            if wiki.get(code): self.win.open_url(f"https://{code}.wikipedia.org/wiki/" + quote(wiki[code].replace(" ", "_"))); return
    def follow(self, url):
        if url.startswith("lafa://item/"): self.win.open_item(url[len("lafa://item/"):])
        elif url.startswith("https://"): self.win.open_url(url)
    def retranslate(self): self.render()

def cover(pm, w, h):
    """Cover-crop a picture to w×h."""
    if pm.isNull() or w <= 0 or h <= 0: return pm
    scaled = pm.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    return scaled.copy((scaled.width() - w) // 2, (scaled.height() - h) // 2, w, h)
