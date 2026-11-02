"""Konstituisaun: read the Constitution of the RDTL in Tetun, Portuguese or
both side by side, with a table of contents and a fast search by article
number ("15", "art. 59") or by words ("edukasaun", "liberdade de imprensa")."""
import html

from ...qt import Qt, QTimer, QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QFrame, QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem, QApplication, QUrl
from ... import kb
from ...constitution import load, highlight_pattern, parse_ref
from ..texts import extend
from ..widgets import Card, ClayIcon, Pill, Segmented, SearchBox, FlowLayout, label, button, tok_of

extend({
    "con_title": ("Konstituisaun RDTL", "Constituição da RDTL"),
    "con_sub": ("Lei-Inan Repúblika Demokrátika Timór-Leste · aprova 22 Marsu 2002 · tama iha vigór 20 Maiu 2002 · artigu {n}",
                "Lei fundamental da República Democrática de Timor-Leste · aprovada a 22 de março de 2002 · em vigor desde 20 de maio de 2002 · {n} artigos"),
    "con_search": ("Buka númeru artigu (ez. 15) ka liafuan (ez. edukasaun)", "Procurar o número do artigo (ex. 15) ou palavras (ex. educação)"),
    "con_both": ("Tetun + Português", "Tétum + Português"),
    "con_contents": ("Índise", "Índice"),
    "con_results": ("Rezultadu: {n}", "Resultados: {n}"),
    "con_no_results": ("La hetan artigu. Koko liafuan seluk ka númeru 1–170.", "Nenhum artigo encontrado. Tente outras palavras ou um número de 1 a 170."),
    "con_preamble": ("Preámbulu", "Preâmbulo"),
    "con_prev": ("Artigu molok", "Artigo anterior"),
    "con_next": ("Artigu tuir mai", "Artigo seguinte"),
    "con_copy": ("Kopia artigu", "Copiar artigo"),
    "con_copied": ("Kopia ona artigu {n}", "Artigo {n} copiado"),
    "con_read": ("Lee ho lian", "Ler em voz alta"),
    "con_article": ("Artigu", "Artigo"),
    "con_note": ("Testu ofisiál husi Jornal da República (portugés) no edisaun Tetun 2010. Iha divérjénsia, testu portugés mak prevalese.",
                 "Texto oficial do Jornal da República (português) e edição em tétum de 2010. Em caso de divergência, prevalece o texto em português."),
    "con_quick": ("Asesu lalais", "Acesso rápido"),
    "con_show_contents": ("Hatudu índise", "Mostrar índice"),
})

# Quick links: (Tetun, Portuguese, article)
QUICK = [("Símbolu nasionál", "Símbolos nacionais", 14), ("Lian ofisiál", "Línguas oficiais", 13), ("Direitu fundamentál", "Direitos fundamentais", 16),
         ("Edukasaun", "Educação", 59), ("Prezidente Repúblika", "Presidente da República", 74), ("Parlamentu Nasionál", "Parlamento Nacional", 92),
         ("Governu", "Governo", 103), ("Tribunál sira", "Tribunais", 118), ("Defeza no seguransa", "Defesa e segurança", 146), ("Inu nasionál", "Hino nacional", 166)]

def text_html(value, lang, pattern=None):
    """Escape, turn bullet lists into lines and mark the search words."""
    value = html.escape(kb.show(value, lang), quote=False).replace(" • ", "<br/>• ").replace(": •", ":<br/>•")
    if pattern is not None:
        value = pattern.sub(lambda m: f"<span style='background:#ffe58a; color:#3a2a00;'>{m.group(0)}</span>", value)
    return value

class ConstitutionPage(QWidget):
    route = "constitution"
    def __init__(self, win):
        super().__init__(); self.win = win; self.con = load(); self.current = 1; self.query = ""; self.preamble = False
        self.mode = "tet" if win.lang == "tet" else "pt"; self.narrow = False
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.setInterval(220); self.timer.timeout.connect(self.run_search)
        self.build()
    # ------------------------------------------------------------------ ui
    def build(self):
        win = self.win; t = win.t; lang = win.lang
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 8, 8); outer.setSpacing(12)
        head = Card(16, 24); row = QHBoxLayout(); row.setSpacing(14); row.addWidget(ClayIcon("scales", "violet", 56))
        col = QVBoxLayout(); col.setSpacing(2); col.addWidget(label(t("con_title"), "h1", wrap=True))
        col.addWidget(label(t("con_sub", n=len(self.con.articles)), "muted", wrap=True)); row.addLayout(col, 1)
        self.lang_switch = Segmented([("tet", "Tetun"), ("pt", "Português"), ("both", t("con_both"))], self.mode)
        self.lang_switch.changed.connect(self.set_mode); row.addWidget(self.lang_switch, 0, Qt.AlignVCenter); head.box.addLayout(row)
        srow = QHBoxLayout(); srow.setSpacing(10)
        self.search = SearchBox(t("con_search")); self.search.textEdited.connect(lambda _=None: self.timer.start()); self.search.returnPressed.connect(self.run_search)
        srow.addWidget(self.search, 1); self.count = label("", "caption"); srow.addWidget(self.count)
        self.quick_button = button(t("con_quick"), self.toggle_quick, "ghost", "star"); srow.addWidget(self.quick_button)
        self.toc_button = button(t("con_contents"), self.toggle_toc, "ghost", "layers"); srow.addWidget(self.toc_button)
        head.box.addLayout(srow)
        quick = QWidget(); flow = FlowLayout(quick, 6)
        pre = button(t("con_preamble"), self.show_preamble, "chip", "scroll"); flow.addWidget(pre)
        for tet, pt, n in QUICK:
            b = button(f"{tet if lang == 'tet' else pt} · {n}", lambda checked=False, n=n: self.open_article(n), "chip"); flow.addWidget(b)
        head.box.addWidget(quick); self.quick = quick; outer.addWidget(head)
        body = QHBoxLayout(); body.setSpacing(14)
        self.side = Card(10, 22); self.side.setFixedWidth(320)
        self.side.box.addWidget(label(t("con_contents"), "h3"))
        self.tree = QTreeWidget(); self.tree.setHeaderHidden(True); self.tree.setFrameShape(QFrame.NoFrame); self.tree.setIndentation(14)
        self.tree.itemClicked.connect(self.tree_clicked); self.tree.itemActivated.connect(self.tree_clicked); self.side.box.addWidget(self.tree, 1)
        self.results = QListWidget(); self.results.setFrameShape(QFrame.NoFrame); self.results.setWordWrap(True); self.results.setSpacing(2)
        self.results.itemClicked.connect(self.result_clicked); self.results.itemActivated.connect(self.result_clicked); self.results.hide(); self.side.box.addWidget(self.results, 1)
        self.empty = label(t("con_no_results"), "muted", wrap=True); self.empty.hide(); self.side.box.addWidget(self.empty)
        body.addWidget(self.side)
        reader = Card(12, 24); bar = QHBoxLayout(); bar.setSpacing(8)
        self.crumb = label("", "caption", wrap=True); bar.addWidget(self.crumb, 1)
        self.prev_b = button("", lambda: self.step(-1), "icon", "back", t("con_prev")); self.prev_b.setFixedSize(40, 40); bar.addWidget(self.prev_b)
        self.next_b = button("", self.next_clicked, "icon", "chevron-right", t("con_next")); self.next_b.setFixedSize(40, 40); bar.addWidget(self.next_b)
        copy = button("", self.copy, "icon", "copy", t("con_copy")); copy.setFixedSize(40, 40); bar.addWidget(copy)
        read = button("", self.read_aloud, "icon", "speaker", t("con_read")); read.setFixedSize(40, 40); bar.addWidget(read)
        reader.box.addLayout(bar)
        self.text = QTextBrowser(); self.text.setOpenLinks(False); self.text.setFrameShape(QFrame.NoFrame); self.text.anchorClicked.connect(self.link)
        self.text.setStyleSheet("background:transparent;"); reader.box.addWidget(self.text, 1)
        note = label(t("con_note"), "caption", wrap=True); reader.box.addWidget(note)
        body.addWidget(reader, 1); outer.addLayout(body, 1)
        self.style_lists(); self.fill_tree()
    def style_lists(self):
        tok = tok_of(self.win)
        css = (f"QTreeWidget, QListWidget {{ background:transparent; color:{tok['text']}; outline:0; }}"
               f"QTreeWidget::item, QListWidget::item {{ padding:5px 4px; border-radius:8px; }}"
               f"QTreeWidget::item:selected, QListWidget::item:selected {{ background:{tok['primary_soft']}; color:{tok['text']}; }}"
               f"QTreeWidget::item:hover, QListWidget::item:hover {{ background:{tok['card_hover']}; }}"
               f"QTreeWidget::branch, QTreeWidget::branch:selected {{ background:transparent; }}")
        self.tree.setStyleSheet(css); self.results.setStyleSheet(css)
    def fill_tree(self):
        lang = self.win.lang; con = self.con; self.tree.clear(); self.tree_items = {}
        parents = {}
        for a in con.articles:
            parent = None
            for i in a.get("path", []):
                if i not in parents:
                    h = con.headings[i]; text = f"{con.heading_label(h, lang)} · {kb.show(con.heading_title(h, lang).capitalize(), lang)}"
                    node = QTreeWidgetItem([text]); node.setData(0, Qt.UserRole, -1); f = node.font(0); f.setBold(True); node.setFont(0, f); node.setToolTip(0, text)
                    (parent.addChild(node) if parent else self.tree.addTopLevelItem(node)); parents[i] = node
                parent = parents[i]
            item = QTreeWidgetItem([f"{a['n']}. {kb.show(con.article_title(a, lang), lang)}"]); item.setData(0, Qt.UserRole, a["n"])
            (parent.addChild(item) if parent else self.tree.addTopLevelItem(item)); self.tree_items[a["n"]] = item
    # --------------------------------------------------------------- route
    def show_route(self, params):
        if params.get("q"):
            self.search.setText(str(params["q"])); self.run_search()
        n = parse_ref(params.get("article", "")) if params.get("article") is not None else None
        if n: self.open_article(n)
        elif params.get("preamble"): self.show_preamble()
        else: self.render()
        QTimer.singleShot(0, self.search.setFocus)
    def resizeEvent(self, e):
        super().resizeEvent(e)
        narrow = self.width() < 900
        if narrow != self.narrow: self.narrow = narrow; self.side.setVisible(not narrow or self.toc_open())
        self.toc_button.setVisible(narrow)
        low = self.height() < 640                     # 1024×600 screens: quick links behind a button
        self.quick_button.setVisible(low); self.quick.setVisible(not low or getattr(self, "_quick_open", False))
    def toggle_quick(self):
        self._quick_open = not getattr(self, "_quick_open", False); self.quick.setVisible(self._quick_open)
    def toc_open(self): return getattr(self, "_toc_open", False)
    def toggle_toc(self):
        self._toc_open = not self.toc_open(); self.side.setVisible(self._toc_open or not self.narrow)
    def set_mode(self, mode): self.mode = mode; self.render()
    # -------------------------------------------------------------- search
    def run_search(self):
        q = self.search.text().strip(); self.query = q; lang = self.win.lang if self.mode == "both" else self.mode
        if not q:
            self.results.hide(); self.empty.hide(); self.tree.show(); self.count.setText(""); self.render(); return
        n = parse_ref(q)
        if n is not None:
            self.results.hide(); self.empty.hide(); self.tree.show(); self.count.setText(""); self.open_article(n, keep_query=False); return
        found = self.con.search(q, lang)
        if not found and self.mode != "both":
            other = "pt" if lang == "tet" else "tet"; found = self.con.search(q, other)
        self.results.clear()
        for a, _score, snippet in found:
            item = QListWidgetItem(f"{self.win.t('con_article')} {a['n']} · {kb.show(self.con.article_title(a, lang), lang)}\n{snippet}")
            item.setData(Qt.UserRole, a["n"]); self.results.addItem(item)
        self.tree.setVisible(False); self.results.setVisible(bool(found)); self.empty.setVisible(not found)
        self.count.setText(self.win.t("con_results", n=len(found)))
        if found:
            if self.narrow and not self.toc_open(): self.toggle_toc()
            self.open_article(found[0][0]["n"], keep_query=True)
    def result_clicked(self, item): self.open_article(item.data(Qt.UserRole), keep_query=True)
    def tree_clicked(self, item, _column=0):
        n = item.data(0, Qt.UserRole)
        if n and n > 0: self.open_article(n, keep_query=bool(self.query))
        else: item.setExpanded(not item.isExpanded())
    # ------------------------------------------------------------- reading
    def open_article(self, n, keep_query=True):
        a = self.con.article(n)
        if not a: return
        self.current = a["n"]; self.preamble = False
        if not keep_query: self.query = ""
        item = self.tree_items.get(self.current)
        if item is not None:
            self.tree.blockSignals(True); self.tree.setCurrentItem(item); self.tree.scrollToItem(item); self.tree.blockSignals(False)
        self.render()
    def show_preamble(self):
        self.preamble = True; self.render()
    def next_clicked(self):
        """From the preamble the next page is article 1; otherwise the next article."""
        if self.preamble: self.open_article(1)
        else: self.step(1)
    def step(self, delta):
        n = self.current + delta
        if self.con.article(n): self.open_article(n, keep_query=bool(self.query))
    def langs(self): return ("tet", "pt") if self.mode == "both" else (self.mode,)
    def render(self):
        win = self.win; tok = win.tok; scale = win.scale(); con = self.con; langs = self.langs()
        fs = lambda px: f"{round(px * scale)}px"
        self.text.document().setDefaultStyleSheet(
            f"body {{ color:{tok['text']}; font-size:{fs(16)}; }} h2 {{ font-size:{fs(20)}; font-weight:800; margin:6px 0 2px 0; }}"
            f"h3 {{ font-size:{fs(17)}; font-weight:800; margin:14px 0 4px 0; color:{tok['text']}; }} p {{ line-height:130%; margin:2px 0 8px 0; }}"
            f".num {{ color:{tok['primary']}; font-weight:800; }} .item {{ margin-left:18px; }} .head {{ color:{tok['muted']}; font-size:{fs(13)}; font-weight:700; letter-spacing:1px; }}"
            f".lang {{ color:{tok['muted']}; font-size:{fs(12)}; font-weight:800; }} a {{ color:{tok['primary']}; text-decoration:none; }}")
        words = [w for w in self.query.replace('"', " ").split() if len(w) >= 2] if self.query and parse_ref(self.query) is None else []
        pattern = highlight_pattern(words)
        if self.preamble:
            parts = [f"<h2>{html.escape(win.t('con_preamble'))}</h2>"]
            if len(langs) == 1:
                parts += [f"<p>{text_html(p, langs[0], pattern)}</p>" for p in con.preamble(langs[0])]
            else:
                tet, pt = con.preamble("tet"), con.preamble("pt")
                parts.append("<table width='100%' cellspacing='0' cellpadding='6'><tr><td class='lang' width='50%'>TETUN</td><td class='lang'>PORTUGUÊS</td></tr>")
                for i in range(max(len(tet), len(pt))):
                    parts.append(f"<tr><td valign='top'>{text_html(tet[i] if i < len(tet) else '', 'tet', pattern)}</td><td valign='top'>{text_html(pt[i] if i < len(pt) else '', 'pt', pattern)}</td></tr>")
                parts.append("</table>")
            self.text.setHtml("".join(parts)); self.crumb.setText(con.title(win.lang)); self.prev_b.setEnabled(False); self.next_b.setEnabled(True)
            return
        a = con.article(self.current) or con.articles[0]
        lang0 = langs[0]
        crumbs = [f"{con.heading_label(h, lang0)} · {kb.show(con.heading_title(h, lang0).capitalize(), lang0)}" for h in con.path(a)]
        self.crumb.setText("  ›  ".join(crumbs))
        parts = []
        for h in con.path(a)[-1:]:
            parts.append(f"<p class='head'>{html.escape(con.heading_label(h, lang0).upper())} · {html.escape(kb.show(con.heading_title(h, lang0), lang0))}</p>")
        for x in con.group(a):
            current = x["n"] == a["n"]
            inner = self.article_html(x, langs, pattern)
            bg = tok["primary_soft"] if current else "transparent"
            parts.append(f"<a name='a{x['n']}'></a><table width='100%' cellspacing='0' cellpadding='10' style='background:{bg};'><tr><td>{inner}</td></tr></table>")
        self.text.setHtml("".join(parts))
        QTimer.singleShot(0, lambda n=a["n"]: self.text.scrollToAnchor(f"a{n}"))
        self.prev_b.setEnabled(a["n"] > 1); self.next_b.setEnabled(a["n"] < len(con.articles))
    def article_html(self, a, langs, pattern):
        con = self.con
        def block_html(b, lang):
            num = f"<span class='num'>{html.escape(b['n'])}.</span> " if b.get("n") else ""
            out = f"<p>{num}{text_html(b.get('text', ''), lang, pattern)}</p>" if (b.get("text") or num) else ""
            out += "".join(f"<p class='item'><span class='num'>{l})</span> {text_html(tx, lang, pattern)}</p>" for l, tx in b.get("items", []))
            return out
        if len(langs) == 1:
            lang = langs[0]; word = "Artigu" if lang == "tet" else "Artigo"
            head = f"<h3>{word} {a['n']}.º · {text_html(con.article_title(a, lang), lang, pattern)}</h3>"
            return head + "".join(block_html(b, lang) for b in con.blocks(a, lang))
        rows = [f"<h3>Artigu / Artigo {a['n']}.º</h3><table width='100%' cellspacing='0' cellpadding='4'>",
                f"<tr><td width='50%' valign='top'><b>{text_html(con.article_title(a, 'tet'), 'tet', pattern)}</b></td><td valign='top'><b>{text_html(con.article_title(a, 'pt'), 'pt', pattern)}</b></td></tr>"]
        tet, pt = con.blocks(a, "tet"), con.blocks(a, "pt")
        for i in range(max(len(tet), len(pt))):
            rows.append(f"<tr><td valign='top'>{block_html(tet[i], 'tet') if i < len(tet) else ''}</td><td valign='top'>{block_html(pt[i], 'pt') if i < len(pt) else ''}</td></tr>")
        return "".join(rows) + "</table>"
    def link(self, url):
        s = url.toString()
        if s.startswith("#a") and s[2:].isdigit(): self.open_article(int(s[2:]))
        elif s.startswith("https://"): self.win.open_url(s)
    def copy(self):
        lang = self.langs()[0] if self.mode != "both" else self.win.lang
        a = self.con.article(self.current)
        if not a: return
        text = self.con.plain(a, lang) + f"\n— {self.con.title(lang)}"
        QApplication.clipboard().setText(text); self.win.toast.show_text(self.win.t("con_copied", n=a["n"]))
    def read_aloud(self):
        lang = self.langs()[0] if self.mode != "both" else self.win.lang
        if self.preamble: self.win.speak(" ".join(self.con.preamble(lang)), lang); return
        a = self.con.article(self.current)
        if a: self.win.speak(self.con.plain(a, lang), lang)
    def retranslate(self): pass
