"""The encyclopedia browser: category → topic list → article.

One browser serves the World Encyclopedia (Learn) and Timor-Leste. Every page
has Back (which restores the previous scroll position and tab), the start of
the encyclopedia, a breadcrumb and a search limited to that encyclopedia.

Articles open in a wide reading view (one scroll, no nested panels) with
learning objectives, a picture, the text, key facts with years, sources,
related topics and review metadata, plus "Explore" (picture or interactive
module) and "Practice" (questions with explanations; the result is kept on this
computer). Everything works offline.
"""
import html
import re
from datetime import datetime

from .qt import (Qt, QTimer, QUrl, QSize, Signal, QWidget, QFrame, QLabel, QPushButton, QScrollArea, QStackedWidget,
                 QVBoxLayout, QHBoxLayout, QGridLayout, QTextBrowser, QTextDocument, QSizePolicy, QButtonGroup, QImage)
from . import encyclopedia as enc, icons, curriculum
from .widgets import NavBar, CategoryCard, TopicRow, Tile, Badge, EmptyState, Illustration, IconButton, icon_html, tokens_of

LANG_NAMES = {"en": "English", "id": "Bahasa Indonesia", "pt": "Português", "tet": "Tetun"}

def plain_paragraphs(value):
    """Body text to HTML: blank lines → paragraphs, "• " lines → a list."""
    out = []; bullets = []
    def flush():
        if bullets: out.append("<ul>" + "".join(f"<li>{html.escape(b)}</li>" for b in bullets) + "</ul>"); bullets.clear()
    for line in str(value).split("\n"):
        line = line.strip()
        if not line: flush(); continue
        if line.startswith(("• ", "- ")): bullets.append(line[2:]); continue
        flush(); out.append(f"<p>{html.escape(line)}</p>")
    flush(); return "".join(out)

class ResponsiveGrid(QWidget):
    """Cards in as many columns as fit (never horizontal scrolling)."""
    def __init__(self, min_width=260, max_columns=3, parent=None):
        super().__init__(parent); self.items = []; self.min_width = min_width; self.max_columns = max_columns; self.columns = 0
        self.grid = QGridLayout(self); self.grid.setContentsMargins(0, 0, 0, 0); self.grid.setSpacing(16)
    def add(self, widget):
        self.items.append(widget); self.relayout(force=True)
    def relayout(self, force=False):
        columns = max(1, min(self.max_columns, (self.width() + 16) // (self.min_width + 16))) if self.width() > 50 else self.max_columns
        if columns == self.columns and not force: return
        self.columns = columns
        for w in self.items: self.grid.removeWidget(w)
        for i, w in enumerate(self.items): self.grid.addWidget(w, i // columns, i % columns)
        for c in range(self.max_columns): self.grid.setColumnStretch(c, 1 if c < columns else 0)
    def resizeEvent(self, event):
        super().resizeEvent(event); self.relayout()

def scroll_page(body):
    area = QScrollArea(); area.setWidgetResizable(True); area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); area.setFrameShape(QFrame.NoFrame)
    area.setWidget(body); return area

class QuizWidget(QWidget):
    """Practice questions, one at a time, with an explanation after each answer.
    Keyboard: Tab between answers, Enter to choose, or the keys 1–4."""
    finished = Signal(int, int)
    def __init__(self, window, key, items, parent=None):
        super().__init__(parent); self.win = window; self.key = key; self.items = items; self.i = 0; self.score = 0; self.answered = False
        t = window.t; v = QVBoxLayout(self); v.setContentsMargins(4, 8, 4, 8); v.setSpacing(12)
        if not items:
            v.addWidget(EmptyState("question", t("quiz_none"), tokens_of(window))); return
        self.progress = QLabel(); self.progress.setObjectName("muted"); v.addWidget(self.progress)
        self.question = QLabel(); self.question.setObjectName("quizquestion"); self.question.setWordWrap(True); v.addWidget(self.question)
        grid = QGridLayout(); grid.setSpacing(10); self.buttons = []
        for n in range(4):
            b = QPushButton(); b.setObjectName("answer"); b.setMinimumHeight(48); b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            b.clicked.connect(lambda checked=False, n=n: self.answer(n)); grid.addWidget(b, n // 2, n % 2); self.buttons.append(b)
        v.addLayout(grid)
        self.feedback = QLabel(); self.feedback.setObjectName("feedback"); self.feedback.setWordWrap(True); v.addWidget(self.feedback)
        row = QHBoxLayout(); self.next_button = QPushButton(t("quiz_next")); self.next_button.setObjectName("primary"); self.next_button.clicked.connect(self.next)
        row.addWidget(self.next_button); row.addStretch(); v.addLayout(row)
        self.best = QLabel(); self.best.setObjectName("muted"); self.best.setWordWrap(True); v.addWidget(self.best); v.addStretch()
        self.show_question(); self.show_best()
    def show_best(self):
        result = self.win.progress.result(self.key) if hasattr(self.win, "progress") else None
        self.best.setText(self.win.t("quiz_best").format(s=result["best"], n=result["total"]) if result else "")
    def show_question(self):
        q, options, answer, _ = self.items[self.i]; self.answered = False
        self.progress.setText(self.win.t("quiz_progress").format(i=self.i + 1, n=len(self.items)))
        self.question.setText(q)
        for n, b in enumerate(self.buttons):
            b.setText(f"{n + 1}.  {options[n]}"); b.setEnabled(True); b.setProperty("state", ""); b.style().unpolish(b); b.style().polish(b)
        self.feedback.setText(""); self.next_button.hide()
        self.buttons[0].setFocus()
    def answer(self, n):
        if self.answered or not self.items: return
        self.answered = True; q, options, answer, why = self.items[self.i]; ok = n == answer
        if ok: self.score += 1
        for k, b in enumerate(self.buttons):
            b.setEnabled(k in (n, answer)); b.setProperty("state", "right" if k == answer else ("wrong" if k == n else "")); b.style().unpolish(b); b.style().polish(b)
        text = self.win.t("quiz_right") if ok else self.win.t("quiz_wrong").format(a=options[answer])
        self.feedback.setText(text + ("\n" + why if why else ""))
        self.next_button.setText(self.win.t("quiz_next") if self.i + 1 < len(self.items) else self.win.t("quiz_again"))
        self.next_button.show(); self.next_button.setFocus()
        if self.i + 1 == len(self.items):
            self.feedback.setText(self.feedback.text() + "\n\n" + self.win.t("quiz_done").format(s=self.score, n=len(self.items)))
            try: self.win.progress.record(self.key, self.score, len(self.items))
            except (ValueError, OSError, AttributeError): pass
            self.show_best(); self.finished.emit(self.score, len(self.items))
    def next(self):
        if self.i + 1 < len(self.items): self.i += 1
        else: self.i = 0; self.score = 0
        self.show_question()
    def keyPressEvent(self, event):
        key = event.key()
        if Qt.Key_1 <= key <= Qt.Key_4 and self.items and not self.answered: self.answer(key - Qt.Key_1); return
        super().keyPressEvent(event)

class FigureView(QWidget):
    """Explore tab for articles without an interactive module: the picture large,
    its caption, and the key facts as cards."""
    def __init__(self, window, article, parent=None):
        super().__init__(parent); lang = window.settings.locale; t = window.t
        v = QVBoxLayout(self); v.setContentsMargins(0, 8, 0, 8); v.setSpacing(12)
        pic = Illustration(article.figure, 16); pic.setMinimumHeight(220); pic.setAccessibleName(enc.text(article.caption, lang) or enc.text(article.title, lang)); v.addWidget(pic, 3)
        caption = enc.text(article.caption, lang) or enc.text(article.title, lang)
        note = t("map_note") if "map" in article.figure else t("figure_note")
        cap = QLabel(f"{caption} · {note}"); cap.setObjectName("muted"); cap.setWordWrap(True); v.addWidget(cap)
        facts = [f for f in article.facts if isinstance(f, dict)]
        if facts:
            grid = ResponsiveGrid(220, 4)
            for f in facts[:8]:
                card = QFrame(); card.setObjectName("factcard"); cv = QVBoxLayout(card); cv.setContentsMargins(14, 10, 14, 10)
                value = QLabel(enc.text(f.get("value", {}), lang)); value.setObjectName("factvalue"); value.setWordWrap(True); cv.addWidget(value)
                label = QLabel(enc.text(f.get("label", {}), lang) + (f" · {f['year']}" if f.get("year") else "")); label.setObjectName("cardcaption"); label.setWordWrap(True); cv.addWidget(label)
                grid.add(card)
            v.addWidget(grid)
        v.addStretch(1)

class ArticlePage(QWidget):
    """Header, Read / Explore / Practice, a contents list on wide screens and
    the actions Read aloud · Save · Sources · Start practice."""
    TABS = ("read", "explore", "practice")
    def __init__(self, browser, article, tab="read"):
        super().__init__(); self.browser = browser; self.win = browser.win; self.article = article
        win = self.win; t = win.t; lang = win.settings.locale; tok = tokens_of(win)
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(12)
        head = QHBoxLayout(); head.setSpacing(16)
        cat = enc.category(article.area, article.category)
        mark = QLabel(); mark.setObjectName("icontile"); mark.setFixedSize(64, 64); mark.setAlignment(Qt.AlignCenter)
        mark.setPixmap(icons.pixmap(cat.icon if cat else "book-open", tok.get("accent_strong", "#0a7350"), 34)); head.addWidget(mark, 0, Qt.AlignTop)
        titles = QVBoxLayout(); titles.setSpacing(2)
        top = QHBoxLayout(); top.setSpacing(10)
        title = QLabel(enc.text(article.title, lang)); title.setObjectName("articletitle"); title.setWordWrap(True); top.addWidget(title, 1)
        top.addWidget(Badge(t("offline_material"), "ok", "cloud-check", tok), 0, Qt.AlignTop); titles.addLayout(top)
        sub = QLabel(enc.text(article.summary, lang)); sub.setObjectName("articlesub"); sub.setWordWrap(True); titles.addWidget(sub)
        full, summary_only = article.languages()
        lang_line = t("langs_full").format(langs=", ".join(LANG_NAMES[x] for x in full))
        if summary_only: lang_line += " · " + t("langs_summary").format(langs=", ".join(LANG_NAMES[x] for x in summary_only))
        self.lang_line = lang_line
        head.addLayout(titles, 1); v.addLayout(head)
        # Segmented tabs.
        seg = QHBoxLayout(); seg.setSpacing(0); self.group = QButtonGroup(self); self.group.setExclusive(True); self.tab_buttons = {}
        for i, (key, label_key, icon_name) in enumerate((("read", "art_read", "document"), ("explore", "art_explore", "compass"), ("practice", "art_practice", "puzzle"))):
            b = QPushButton(t(label_key)); b.setCheckable(True); b.setObjectName("segfirst" if i == 0 else "seglast" if i == 2 else "segment")
            b.setIcon(icons.icon(icon_name, tok.get("muted", "#5d716a"), tok.get("accent_strong", "#0a7350"))); b.setIconSize(QSize(18, 18)); b.setMinimumHeight(40)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed); b.clicked.connect(lambda checked=False, k=key: self.set_tab(k))
            self.group.addButton(b); seg.addWidget(b); self.tab_buttons[key] = b
        v.addLayout(seg)
        # Body: the reader (or explore / practice) and, on wide screens, the contents list.
        body = QHBoxLayout(); body.setSpacing(16)
        self.stack = QStackedWidget()
        self.reader = QTextBrowser(); self.reader.setObjectName("reader"); self.reader.setOpenLinks(False); self.reader.anchorClicked.connect(self.link)
        self.reader.setAccessibleName(enc.text(article.title, lang)); self.reader.setFrameShape(QFrame.NoFrame)
        self.reader.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.figure_width = 760
        self.stack.addWidget(self.reader)
        self.explore = None; self.quiz = None
        self.stack.addWidget(QWidget()); self.stack.addWidget(QWidget())
        body.addWidget(self.stack, 1)
        self.side = self.build_contents(); body.addWidget(self.side)
        v.addLayout(body, 1)
        # Actions.
        actions = QHBoxLayout(); actions.setSpacing(10)
        if win.voice_available():
            speak = QPushButton(t("read_aloud_btn")); speak.setIcon(icons.icon("speaker", tok.get("text", "#17322b"))); speak.clicked.connect(self.read_aloud); actions.addWidget(speak)
        self.save_button = QPushButton(); self.save_button.setIcon(icons.icon("bookmark", tok.get("text", "#17322b"))); self.save_button.clicked.connect(self.toggle_save); actions.addWidget(self.save_button)
        src = QPushButton(t("sources_btn")); src.setIcon(icons.icon("document", tok.get("text", "#17322b"))); src.clicked.connect(self.show_sources); actions.addWidget(src)
        actions.addStretch()
        start = QPushButton(t("start_practice")); start.setObjectName("primary"); start.setIcon(icons.icon("arrow-right", "#ffffff")); start.setLayoutDirection(Qt.RightToLeft)
        start.clicked.connect(lambda: self.set_tab("practice")); actions.addWidget(start)
        v.addLayout(actions)
        self.render(); self.update_save(); self.set_tab(tab if tab in self.TABS else "read")
        try: win.progress.opened("article", article.id, enc.text(article.title, lang))
        except (OSError, AttributeError): pass
    # -- contents list (only when there is room)
    def build_contents(self):
        lang = self.win.settings.locale; frame = QFrame(); frame.setObjectName("contents"); frame.setFixedWidth(250)
        v = QVBoxLayout(frame); v.setContentsMargins(14, 12, 14, 12); v.setSpacing(4)
        head = QLabel(self.win.t("contents_title")); head.setObjectName("cardtitle"); v.addWidget(head)
        entries = [("objectives", self.win.t("objectives"))] + [(f"s{i}", enc.text(s.get("heading", {}), lang)) for i, s in enumerate(self.article.sections)]
        if self.article.facts: entries.append(("facts", self.win.t("key_facts")))
        entries += [("related", self.win.t("related_title")), ("sources", self.win.t("sources_title"))]
        for anchor, name in entries:
            b = QPushButton(name); b.setObjectName("contentslink"); b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda checked=False, a=anchor: (self.set_tab("read"), self.reader.scrollToAnchor(a))); v.addWidget(b)
        v.addStretch(); return frame
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.side.setVisible(self.width() >= 1150)
        view = self.reader.viewport().width()
        margin = max(14, (view - 860) // 2)
        doc = self.reader.document()
        if abs(doc.documentMargin() - margin) > 2: doc.setDocumentMargin(margin)
        width = max(240, min(760, view - 2 * margin - 24))
        if abs(width - self.figure_width) > 30:
            self.figure_width = width; value = self.reader.verticalScrollBar().value(); self.render(); self.reader.verticalScrollBar().setValue(value)
    # -- tabs
    def set_tab(self, key):
        self.tab_buttons[key].setChecked(True); index = self.TABS.index(key)
        if key == "explore" and self.explore is None:
            from . import interactive
            widget = interactive.create(self.article.activity, self.win, self.article) if self.article.activity else None
            self.explore = scroll_page(widget or FigureView(self.win, self.article))
            old = self.stack.widget(1); self.stack.insertWidget(1, self.explore); self.stack.removeWidget(old); old.deleteLater()
        if key == "practice" and self.quiz is None:
            self.quiz = QuizWidget(self.win, "quiz:" + self.article.id, enc.quiz(self.article, self.win.settings.locale))
            holder = scroll_page(self.quiz); old = self.stack.widget(2); self.stack.insertWidget(2, holder); self.stack.removeWidget(old); old.deleteLater()
        self.stack.setCurrentIndex(index)
    def current_tab(self):
        return self.TABS[self.stack.currentIndex()]
    def scroll_widget(self):
        current = self.stack.currentWidget()
        return current if hasattr(current, "verticalScrollBar") else self.reader
    # -- reading view
    def render(self):
        win = self.win; t = win.t; lang = win.settings.locale; tok = tokens_of(win); a = self.article
        doc = self.reader.document(); width = self.figure_width
        pix = icons.illustration(a.figure, width, int(width * 9 / 16))
        if not pix.isNull(): doc.addResource(QTextDocument.ImageResource, QUrl("lafa-figure:main"), pix.toImage())
        text_c = tok.get("text", "#17322b"); muted = tok.get("muted", "#5d716a"); soft = tok.get("accent_soft", "#e3f4ec"); link = tok.get("accent_strong", "#0a7350"); border = tok.get("border", "#e1e7df")
        doc.setDefaultStyleSheet(f"""
            body {{ color:{text_c}; font-size:15px; }}
            h2 {{ font-size:19px; margin-top:22px; margin-bottom:6px; color:{text_c}; }}
            p {{ line-height:150%; margin-bottom:8px; }}
            a {{ color:{link}; text-decoration:none; }}
            .muted {{ color:{muted}; font-size:12px; }}
            .box {{ background:{soft}; }}
            td {{ padding:6px 10px; border-bottom:1px solid {border}; }}
            th {{ padding:6px 10px; text-align:left; color:{muted}; }}
        """)
        parts = [f'<p class="muted">{html.escape(self.lang_line)}</p>']
        if lang in ("pt", "tet") and lang not in a.languages()[0]:
            parts.append(f'<p class="muted">{html.escape(t("lang_shown_en"))}</p>')
        goals = enc.objectives(a, lang)
        parts.append(f'<a name="objectives"></a><table width="100%" cellpadding="12" class="box" style="background:{soft}"><tr><td>'
                     f'<b>{icon_html("lightbulb", link, 16)} {html.escape(t("objectives"))}</b><ul>' + "".join(f"<li>{html.escape(g)}</li>" for g in goals) + "</ul></td></tr></table>")
        if not pix.isNull():
            caption = enc.text(a.caption, lang) or enc.text(a.title, lang)
            note = t("map_note") if "map" in a.figure else t("figure_note")
            parts.append(f'<p align="center"><img src="lafa-figure:main" width="{width}"></p><p class="muted" align="center">{html.escape(caption)} · {html.escape(note)}</p>')
        photo = None
        try:
            from . import offline_pack
            photo = offline_pack.image(a.id)
        except ImportError: pass
        if photo:
            path, meta = photo; img = QImage(str(path))
            if not img.isNull():
                doc.addResource(QTextDocument.ImageResource, QUrl("lafa-figure:photo"), img)
                pw = min(width, img.width()); credit = t("offline_photo").format(licence=meta.get("licence", ""), author=meta.get("author", ""))
                parts.append(f'<p align="center"><img src="lafa-figure:photo" width="{pw}"></p><p class="muted" align="center">{html.escape(meta.get("description", "") or meta.get("title", ""))}'
                             f'<br>{html.escape(credit)} · <a href="{html.escape(meta.get("source", ""))}">Wikimedia Commons</a></p>')
        if a.when: parts.append(f'<p class="muted"><b>{html.escape(t("when_label"))}:</b> {html.escape(a.when)}</p>')
        for i, s in enumerate(a.sections):
            heading = enc.text(s.get("heading", {}), lang); body = s.get("body", {})
            content = body.get(lang) if isinstance(body, dict) and body.get(lang) else enc.text(body, "en") if lang not in ("en", "id") else enc.text(body, lang)
            parts.append(f'<a name="s{i}"></a><h2>{html.escape(heading)}</h2>{plain_paragraphs(content)}')
        if a.facts:
            rows = []
            for f in a.facts:
                if not isinstance(f, dict): continue
                src = f.get("source"); src_name = a.sources[src]["publisher"] if isinstance(src, int) and 0 <= src < len(a.sources) else ""
                rows.append(f"<tr><td><b>{html.escape(enc.text(f.get('label', {}), lang))}</b></td><td>{html.escape(enc.text(f.get('value', {}), lang))}</td>"
                            f"<td class='muted'>{html.escape(f.get('year') or '')}</td><td class='muted'>{html.escape(src_name)}</td></tr>")
            parts.append(f'<a name="facts"></a><h2>{html.escape(t("key_facts"))}</h2><table width="100%" cellspacing="0">{"".join(rows)}</table>')
        extract = win.saved_extract(a) if hasattr(win, "saved_extract") else None
        if extract:
            parts.append(f'<h2>{html.escape(t("online_extract").format(lang=extract["lang"], date=extract["fetched"]))}</h2>{plain_paragraphs(extract["text"])}'
                         f'<p class="muted">{html.escape(extract.get("source", "Wikipedia"))} · <a href="{html.escape(extract["url"])}">{html.escape(extract["url"])}</a></p>')
        rel = enc.related(a)
        parts.append(f'<a name="related"></a><h2>{html.escape(t("related_title"))}</h2>')
        if rel: parts.append("<ul>" + "".join(f'<li><a href="lafa://article/{html.escape(r.id)}">{html.escape(enc.text(r.title, lang))}</a> <span class="muted">· {html.escape(enc.text(enc.category(r.area, r.category).title, lang))}</span></li>' for r in rel) + "</ul>")
        parts.append(f'<a name="sources"></a><h2>{html.escape(t("sources_title"))}</h2><ol>')
        for s in a.sources:
            parts.append(f'<li>{html.escape(s.get("title", ""))} — {html.escape(s.get("publisher", ""))}, {html.escape(str(s.get("year", "")))}<br><a href="{html.escape(s.get("url", ""))}">{html.escape(s.get("url", ""))}</a></li>')
        parts.append("</ol>")
        r = a.review
        if r: parts.append(f'<p class="muted">{html.escape(t("review_line").format(v=r.get("version", 1), d=r.get("reviewed", ""), status=r.get("status", ""), licence=r.get("licence", "")))}</p>')
        self.reader.setHtml("<body>" + "".join(parts) + "</body>")
        self.plain = "\n".join([enc.text(a.title, lang), enc.text(a.summary, lang)] + [enc.text(s.get("body", {}), lang) for s in a.sections])
    def link(self, url):
        value = url.toString()
        if value.startswith("lafa://article/"): self.browser.open_article(value[len("lafa://article/"):]); return
        if value.startswith("#"): self.reader.scrollToAnchor(value[1:]); return
        if value.startswith("https://"): self.win.open_web(value); return
        if value.startswith("lafa://"): self.win.open_target(value)
    def read_aloud(self):
        self.win.speak_text(self.plain[:6000])
    def update_save(self):
        saved = self.win.progress.is_favourite("article", self.article.id) if hasattr(self.win, "progress") else False
        self.save_button.setText(self.win.t("saved_btn") if saved else self.win.t("save_btn"))
    def toggle_save(self):
        try: self.win.progress.toggle_favourite("article", self.article.id, enc.text(self.article.title, self.win.settings.locale))
        except (ValueError, OSError) as error: self.win.error(str(error)); return
        self.update_save()
        if hasattr(self.win, "render_favourites"): self.win.render_favourites()
    def show_sources(self):
        self.set_tab("read"); QTimer.singleShot(0, lambda: self.reader.scrollToAnchor("sources"))

class Browser(QWidget):
    """One encyclopedia (area "world" or "timor") with its own history."""
    def __init__(self, window, area):
        super().__init__(); self.win = window; self.area = area; self.history = []; self.state = {"kind": "home"}; self.page = None
        self.persistent = {}; tok = tokens_of(window); t = window.t
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(12)
        self.nav = NavBar(tok, t("nav_back"), t("nav_home"), t("search_tl" if area == "timor" else "search_enc"))
        self.nav.back.connect(self.go_back); self.nav.home.connect(lambda: self.go({"kind": "home"})); self.nav.crumb.connect(self.crumb); self.nav.search.connect(self.search)
        v.addWidget(self.nav)
        self.holder = QVBoxLayout(); self.holder.setContentsMargins(0, 0, 0, 0); v.addLayout(self.holder, 1)
        self.parking = QWidget(self); self.parking.hide()
        self.show_state(dict(getattr(window, "enc_states", {}).get(area, {"kind": "home"})), push=False)
    # ---------------------------------------------------------------- history
    def remember(self):
        state = dict(self.state)
        if self.page is not None:
            scroller = self.page.scroll_widget() if hasattr(self.page, "scroll_widget") else (self.page if hasattr(self.page, "verticalScrollBar") else None)
            if scroller is not None: state["scroll"] = scroller.verticalScrollBar().value()
            if isinstance(self.page, ArticlePage): state["tab"] = self.page.current_tab()
        return state
    def go(self, state):
        if state == {k: v for k, v in self.state.items() if k not in ("scroll", "tab")} and state.get("kind") == "home":
            self.show_state(state, push=False); return
        self.history.append(self.remember()); self.history = self.history[-40:]; self.show_state(state, push=False)
    def go_back(self):
        if not self.history: return
        self.show_state(self.history.pop(), push=False)
    def crumb(self, index):
        trail = self.trail_states()
        if 0 <= index < len(trail): self.go(trail[index])
    def show_state(self, state, push=True):
        if push: self.history.append(self.remember())
        kind = state.get("kind", "home"); page = None
        try:
            if kind == "category": page = self.category_page(state["key"])
            elif kind == "article":
                article = enc.get(state["id"])
                if article is None: raise KeyError(state["id"])
                page = ArticlePage(self, article, state.get("tab", "read"))
            elif kind == "search": page = self.search_page(state.get("q", ""))
            elif kind == "coverage": page = self.coverage_page()
            elif kind == "special": page = self.special_page(state["name"])
        except (KeyError, TypeError):
            state = {"kind": "home"}; page = None
        if page is None: state = {"kind": "home"} if kind not in ("special",) or page is None else state; page = page or self.home_page()
        old = self.page
        if old is not None:
            self.holder.removeWidget(old)
            if old in self.persistent.values(): old.setParent(self.parking); old.hide()
            else: old.hide(); old.deleteLater()
        self.page = page; self.state = {k: v for k, v in state.items() if k not in ("scroll", "tab")}
        if isinstance(page, ArticlePage): self.state["tab"] = state.get("tab", "read")
        page.show(); self.holder.addWidget(page, 1); self.nav.set_can_go_back(bool(self.history)); self.update_trail()
        if "scroll" in state:
            value = state["scroll"]
            def restore():
                scroller = page.scroll_widget() if hasattr(page, "scroll_widget") else (page if hasattr(page, "verticalScrollBar") else None)
                if scroller is not None: scroller.verticalScrollBar().setValue(value)
            QTimer.singleShot(0, restore)
        if not hasattr(self.win, "enc_states"): self.win.enc_states = {}
        self.win.enc_states[self.area] = dict(self.state)
    def trail_states(self):
        trail = [{"kind": "home"}]; s = self.state
        if s["kind"] == "article":
            a = enc.get(s["id"])
            if a and a.area == self.area: trail.append({"kind": "category", "key": a.category})
            trail.append({"kind": "article", "id": s["id"]})
        elif s["kind"] != "home": trail.append({k: v for k, v in s.items() if k != "tab"})
        return trail
    def name_of(self, state):
        t = self.win.t; lang = self.win.settings.locale; kind = state["kind"]
        if kind == "home": return t("menu_timor") if self.area == "timor" else t("enc_title")
        if kind == "category": return enc.text(enc.category(self.area, state["key"]).title, lang)
        if kind == "article":
            a = enc.get(state["id"]); return enc.text(a.title, lang) if a else "?"
        if kind == "search": return t("enc_results").format(q=state.get("q", ""))
        if kind == "coverage": return t("coverage_title")
        if kind == "special": return t({"news": "news_tile", "weather": "weather_tile"}.get(state["name"], state["name"]))
        return ""
    def update_trail(self):
        names = [self.name_of(s) for s in self.trail_states()]
        if self.area == "world": names.insert(0, self.win.t("menu_study"))
        self.nav.set_trail(names if self.area == "timor" else names)
        if self.area == "world":
            # The first crumb ("Learn") is not a link inside this browser.
            self.nav.trail.linkActivated.disconnect(); self.nav.trail.linkActivated.connect(lambda link: self.crumb(int(link) - 1) if int(link) > 0 else None)
    # ---------------------------------------------------------------- actions
    def open_article(self, article_id, tab="read"):
        a = enc.get(article_id)
        if a is None: return
        if a.area != self.area and hasattr(self.win, "open_article"):
            self.win.open_article(article_id, tab); return
        self.go({"kind": "article", "id": article_id, "tab": tab})
    def open_category(self, key):
        self.go({"kind": "category", "key": key})
    def open_special(self, name):
        self.go({"kind": "special", "name": name})
    def search(self, query):
        if query: self.go({"kind": "search", "q": query[:120]})
    # ---------------------------------------------------------------- pages
    def header(self, layout, title, subtitle, icon_name=None):
        tok = tokens_of(self.win); row = QHBoxLayout(); row.setSpacing(14)
        if icon_name:
            mark = QLabel(); mark.setObjectName("icontile"); mark.setFixedSize(56, 56); mark.setAlignment(Qt.AlignCenter)
            mark.setPixmap(icons.pixmap(icon_name, tok.get("accent_strong", "#0a7350"), 30)); row.addWidget(mark, 0, Qt.AlignTop)
        text = QVBoxLayout(); text.setSpacing(2)
        name = QLabel(title); name.setObjectName("pagetitle"); name.setWordWrap(True); text.addWidget(name)
        sub = QLabel(subtitle); sub.setObjectName("pagesub"); sub.setWordWrap(True); text.addWidget(sub)
        row.addLayout(text, 1); row.addWidget(Badge(self.win.t("offline_material"), "ok", "cloud-check", tok), 0, Qt.AlignTop)
        layout.addLayout(row)
    def home_page(self):
        t = self.win.t; lang = self.win.settings.locale; tok = tokens_of(self.win)
        body = QWidget(); v = QVBoxLayout(body); v.setContentsMargins(2, 2, 10, 10); v.setSpacing(18)
        if self.area == "timor": self.header(v, t("tl_title"), t("tl_sub"))
        else: self.header(v, t("enc_title"), t("enc_sub"))
        grid = ResponsiveGrid(250, 3)
        for c in enc.categories(self.area):
            count = len(enc.articles(self.area, c.key))
            card = CategoryCard(c.illustration, c.icon, enc.text(c.title, lang), t("topics_n").format(n=count) + " · " + enc.text(c.summary, lang), tok)
            card.clicked.connect(lambda k=c.key: self.open_category(k)); grid.add(card)
        v.addWidget(grid)
        row = QHBoxLayout(); row.setSpacing(14)
        if self.area == "timor":
            for name, icon_name, key in (("news", "newspaper", "news_tile"), ("weather", "weather", "weather_tile")):
                tile = Tile(icon_name, t(key), "", tok, Badge(t("needs_internet_tag"), "net", "globe", tok)); tile.clicked.connect(lambda n=name: self.open_special(n)); row.addWidget(tile, 1)
            other = Tile("book-open", t("open_world"), t("enc_sub"), tok); other.clicked.connect(lambda: self.win.navigate("study", "encyclopedia")); row.addWidget(other, 1)
        else:
            counts = enc.coverage_counts("world")
            cov = Tile("tasks", t("coverage_title"), f"{t('cov_available')}: {counts['available']} · {t('cov_review')}: {counts['review']} · {t('cov_planned')}: {counts['planned']}", tok)
            cov.clicked.connect(lambda: self.go({"kind": "coverage"})); row.addWidget(cov, 1)
            other = Tile("flag-tl", t("open_timor"), t("tl_sub"), tok); other.clicked.connect(lambda: self.win.navigate("timor")); row.addWidget(other, 1)
        v.addLayout(row); v.addStretch(1)
        return scroll_page(body)
    def category_page(self, key):
        c = enc.category(self.area, key)
        if c is None: raise KeyError(key)
        t = self.win.t; lang = self.win.settings.locale; tok = tokens_of(self.win)
        body = QWidget(); v = QVBoxLayout(body); v.setContentsMargins(2, 2, 10, 10); v.setSpacing(14)
        banner = Illustration(c.illustration, 18); banner.setFixedHeight(170); v.addWidget(banner)
        count = len(enc.articles(self.area, key))
        self.header(v, enc.text(c.title, lang), t("topics_n").format(n=count) + " · " + enc.text(c.summary, lang), c.icon)
        for heading, items in enc.groups(self.area, key, lang):
            if heading:
                h = QLabel(heading); h.setObjectName("grouptitle"); v.addWidget(h)
            for a in items:
                row = TopicRow(a.figure, enc.text(a.title, lang), enc.text(a.summary, lang), tok, a.when)
                row.clicked.connect(lambda i=a.id: self.open_article(i)); v.addWidget(row)
        if c.lessons:
            h = QLabel(t("related_lessons")); h.setObjectName("grouptitle"); v.addWidget(h)
            flow = ResponsiveGrid(220, 4); level = self.win.settings.learner_level if self.win.settings.learner_level in curriculum.LEVEL_KEYS else "middle"
            for subject in c.lessons:
                lesson = curriculum.lesson(f"{subject}.{level}")
                if not lesson: continue
                item = curriculum.subject(subject)
                tile = Tile("book-open", curriculum.text(lesson.title, lang), (item.icon + "  " if item else "") + curriculum.subject_name(subject, lang), tok)
                tile.clicked.connect(lambda i=lesson.id: self.win.open_target(f"lafa://lesson/age/{i}")); flow.add(tile)
            v.addWidget(flow)
        if self.area == "world":
            h = QLabel(t("coverage_title")); h.setObjectName("grouptitle"); v.addWidget(h)
            note = QLabel(t("coverage_note")); note.setObjectName("muted"); note.setWordWrap(True); v.addWidget(note)
            for topic, status, aid in enc.coverage(self.area, key):
                line = QHBoxLayout(); name = QLabel(enc.text(topic, lang)); name.setWordWrap(True); line.addWidget(name, 1)
                line.addWidget(Badge(t("cov_" + status), {"available": "ok", "review": "net"}.get(status, "info"), None, tok)); v.addLayout(line)
        v.addStretch(1)
        return scroll_page(body)
    def search_page(self, query):
        t = self.win.t; lang = self.win.settings.locale; tok = tokens_of(self.win)
        self.nav.field.setText(query)
        body = QWidget(); v = QVBoxLayout(body); v.setContentsMargins(2, 2, 10, 10); v.setSpacing(10)
        found = enc.search(query, lang, self.area)
        if not found: v.addWidget(EmptyState("search", t("enc_none").format(q=query), tok))
        for a in found:
            c = enc.category(a.area, a.category)
            row = TopicRow(a.figure, enc.text(a.title, lang), enc.text(c.title, lang) + " · " + enc.text(a.summary, lang), tok, a.when)
            row.clicked.connect(lambda i=a.id: self.open_article(i)); v.addWidget(row)
        v.addStretch(1); return scroll_page(body)
    def coverage_page(self):
        t = self.win.t; lang = self.win.settings.locale; tok = tokens_of(self.win)
        body = QWidget(); v = QVBoxLayout(body); v.setContentsMargins(2, 2, 10, 10); v.setSpacing(8)
        self.header(v, t("coverage_title"), t("coverage_note"), "tasks")
        for c in enc.categories(self.area):
            h = QLabel(enc.text(c.title, lang)); h.setObjectName("grouptitle"); v.addWidget(h)
            for topic, status, aid in enc.coverage(self.area, c.key):
                line = QHBoxLayout(); name = QLabel(enc.text(topic, lang)); name.setWordWrap(True); line.addWidget(name, 1)
                line.addWidget(Badge(t("cov_" + status), {"available": "ok", "review": "net"}.get(status, "info"), None, tok)); v.addLayout(line)
        v.addStretch(1); return scroll_page(body)
    def preload_specials(self):
        """Build News and Weather once (their widgets receive data in the background)."""
        for name in ("news", "weather"):
            page = self.special_page(name); page.setParent(self.parking); page.hide()
    def special_page(self, name):
        if name in self.persistent: return self.persistent[name]
        builder = {"news": getattr(self.win, "build_timor_news", None), "weather": getattr(self.win, "build_live", None)}.get(name)
        if builder is None: raise KeyError(name)
        t = self.win.t; tok = tokens_of(self.win)
        page = QWidget(); v = QVBoxLayout(page); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(10)
        head = QHBoxLayout(); title = QLabel(t({"news": "news_tile", "weather": "weather_tile"}[name])); title.setObjectName("pagetitle"); head.addWidget(title, 1)
        head.addWidget(Badge(t("needs_internet_tag"), "net", "globe", tok)); v.addLayout(head)
        v.addWidget(builder(), 1); self.persistent[name] = page; return page
