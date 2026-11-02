"""Símbolu Nasionál: the national anthem «Pátria» with lyrics that follow the
music (karaoke), the flag (Constitution art. 15) and the emblem (Lei n.º 2/2007)
explained part by part, with links to the articles and the Constitution."""
from ...qt import Qt, QTimer, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPainter, QColor, QFont, QFontMetrics, QRectF, QLinearGradient, QCheckBox
from ... import kb, icons
from ...anthem import load as load_anthem, at, next_time, clock
from ...audio import Player
from ...constitution import load as load_constitution
from ..texts import extend
from ..widgets import Card, Clickable, ClayIcon, Pill, Banner, ResponsiveGrid, label, button, scroll, section_title, clear_layout, tok_of, clip

extend({
    "sym_title": ("Símbolu Nasionál", "Símbolos Nacionais"),
    "sym_sub": ("Bandeira, emblema no inu nasionál — Konstituisaun artigu 14 no 15, Lei n.º 2/2007.", "Bandeira, emblema e hino nacional — Constituição, artigos 14.º e 15.º, Lei n.º 2/2007."),
    "anthem_credits": ("Múzika: {music} · Letra: {lyrics}", "Música: {music} · Letra: {lyrics}"),
    "anthem_play": ("Rona inu", "Ouvir o hino"),
    "anthem_pause": ("Para", "Pausa"),
    "anthem_restart": ("Hahú fali", "Recomeçar"),
    "anthem_repeat": ("Repete", "Repetir"),
    "anthem_translation": ("Hatudu tradusaun Tetun", "Mostrar a tradução em tétum"),
    "anthem_intro": ("♪ Múzika introdusaun", "♪ Introdução musical"),
    "anthem_interlude": ("♪ Interlúdiu múzika", "♪ Interlúdio musical"),
    "anthem_outro": ("♪ Final", "♪ Final"),
    "anthem_ready": ("Prima «Rona inu» no hananu hamutuk", "Prima «Ouvir o hino» e cante connosco"),
    "anthem_refrain": ("Refraun", "Refrão"),
    "anthem_verse": ("Estrofe", "Estrofe"),
    "anthem_lyrics": ("Letra kompletu", "Letra completa"),
    "anthem_no_audio": ("Atu rona inu, instala «python3-pyqt5.qtmultimedia» no «gstreamer1.0-plugins-good» (ka ffmpeg / mpg123). Letra iha okos.",
                        "Para ouvir o hino, instale «python3-pyqt5.qtmultimedia» e «gstreamer1.0-plugins-good» (ou ffmpeg / mpg123). A letra está abaixo."),
    "anthem_failed": ("La bele toka audio iha komputadór ida-ne'e.", "Não foi possível tocar o áudio neste computador."),
    "anthem_respect": ("Bainhira inu toka: hamriik, nonook no haree ba bandeira.", "Quando o hino toca: de pé, em silêncio, a olhar para a bandeira."),
    "sym_flag": ("Bandeira Nasionál", "Bandeira Nacional"),
    "sym_flag_text": ("Konstituisaun artigu 15 deskreve bandeira no nia kór sira:", "O artigo 15.º da Constituição descreve a bandeira e as suas cores:"),
    "sym_emblem": ("Emblema Nasionál (Belak)", "Emblema Nacional (Belak)"),
    "sym_emblem_note": ("Ilustrasaun esplikativu Lafa nian, tuir deskrisaun iha Lei n.º 2/2007 — la'ós dezeñu ofisiál. Imajen ofisiál: Jornal da República.",
                        "Ilustração explicativa do Lafa, segundo a descrição da Lei n.º 2/2007 — não é o desenho oficial. Imagem oficial: Jornal da República."),
    "sym_colours": ("Kór sira iha emblema: mutin = dame · kinur = riku-soin · metan = nakukun atu halakon · mean = domin ba pátria no luta libertasaun.",
                    "Cores do emblema: branco = paz · amarelo = riqueza · preto = obscurantismo a vencer · vermelho = amor à pátria e luta de libertação."),
    "sym_read_article": ("Lee artigu kompletu", "Ler o artigo completo"),
    "sym_constitution": ("Konstituisaun art. {n}", "Constituição art. {n}"),
    "sym_more": ("Símbolu no identidade seluk", "Outros símbolos e identidade"),
    "recording_credit": ("Gravasaun", "Gravação"),
})

EMBLEM_PARTS = [
    ("Belak: sírkulu ho aro mean-rubí rua; reprezenta mundu ne'ebé Timór-Leste mós iha laran — sinál unidade nasionál.", "Belak: círculo com dois aros vermelho-rubi; representa o globo onde se inclui Timor-Leste — símbolo da unidade nacional."),
    ("Foho Ramelau (Tatamailau), foho aas liu iha rai: mean ho klaran metan no ninin kinur.", "Monte Ramelau (Tatamailau), a montanha mais alta do país: vermelho, com o centro preto e uma borda amarela."),
    ("Fitun mutin ho raiu mutin lima: naroman dame no onestidade nian, no solidariedade ho mundu tomak.", "Estrela branca com cinco raios brancos: a luz da paz e da honestidade e a solidariedade com o mundo inteiro."),
    ("Livru loke: koñesimentu, edukasaun no kultura.", "Livro aberto: o saber, a educação e a cultura."),
    ("Roda-dente: indústria no servisu ba dezenvolvimentu.", "Roda dentada: a indústria e o trabalho para o desenvolvimento."),
    ("Hare no batar: agrikultura no riku-soin povu nian.", "Arroz e milho: a agricultura e a riqueza do povo."),
    ("Kilat, diman no rama-inan: rezisténsia sékulu barak nian ba libertasaun nasionál no defeza.", "Espingarda, lança e arco: os séculos de resistência pela libertação nacional e a autodefesa."),
    ("Fita mutin ho lema «Unidade, Acção, Progresso» iha letra mean.", "Fita branca com o lema «Unidade, Acção, Progresso» em letras vermelhas."),
]

class KaraokeLine(QWidget):
    """One sung line, filled with colour from left to right as it is sung."""
    def __init__(self, parent=None):
        super().__init__(parent); self.text = ""; self.progress = 0.0; self.base = 30; self.setMinimumHeight(64)
    def set_line(self, text, progress):
        if text != self.text or abs(progress - self.progress) > 0.002: self.text = text; self.progress = max(0.0, min(1.0, progress)); self.update()
    def paintEvent(self, event):
        if not self.text: return
        t = tok_of(self); p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.TextAntialiasing)
        size = self.base; f = QFont(self.font()); f.setPixelSize(size)
        while size > 15:
            f = QFont(self.font()); f.setPixelSize(size); f.setWeight(QFont.Black if hasattr(QFont, "Black") else 87)
            if QFontMetrics(f).horizontalAdvance(self.text) <= self.width() - 8: break
            size -= 1
        p.setFont(f); fm = QFontMetrics(f); w = fm.horizontalAdvance(self.text); x = max(0, (self.width() - w) // 2); y = (self.height() + fm.ascent() - fm.descent()) // 2
        p.setPen(QColor(t["muted"])); p.drawText(x, y, self.text)
        if self.progress > 0:
            g = QLinearGradient(x, 0, x + w, 0); g.setColorAt(0, QColor(t["nav_a"])); g.setColorAt(1, QColor(t["nav_b"]))
            p.save(); p.setClipRect(QRectF(x, 0, w * self.progress, self.height())); p.setPen(Qt.NoPen)
            from ...qt import QPainterPath
            path = QPainterPath(); path.addText(x, y, f, self.text); p.fillPath(path, g); p.restore()

class SymbolsPage(QWidget):
    route = "symbols"
    def __init__(self, win):
        super().__init__(); self.win = win; self.data = load_anthem(); self.line_rows = {}; self.current_line = None; self.repeat = False
        self.player = Player(self.data["path"], self.data.get("duration", 0), self)
        self.player.position_changed.connect(self.on_position); self.player.state_changed.connect(self.on_state)
        self.player.failed.connect(lambda _reason: self.win.toast.show_text(self.win.t("anthem_failed")))
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(16)
        outer.addWidget(scroll(self.body)); self.render()
    def show_route(self, params):
        if params.get("play") and self.player.available and self.player.state != "playing": self.player.play()
    def hideEvent(self, e):
        super().hideEvent(e)
        if self.player.state == "playing": self.player.pause()
    # ------------------------------------------------------------------ ui
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; data = self.data; self.line_rows = {}
        hero = Card(18, 26, gradient=(win.tok["nav_a"], win.tok["primary"], win.tok["nav_b"]))
        row = QHBoxLayout(); row.setSpacing(18)
        flag = Banner(lambda w, h: icons.illustration("flag", w, h), 120, 18); flag.setFixedWidth(210); row.addWidget(flag)
        col = QVBoxLayout(); col.setSpacing(4)
        for text_, name in ((t("sym_title"), "h1"), (t("sym_sub"), "h3")):
            l = label(text_, name, wrap=True); l.setStyleSheet("color:white;"); col.addWidget(l)
        links = QHBoxLayout(); links.setSpacing(8)
        for n in (14, 15, 166):
            b = button(t("sym_constitution", n=n), lambda checked=False, n=n: win.open("constitution", article=n), "chip", "scales"); links.addWidget(b)
        links.addStretch(); col.addLayout(links); row.addLayout(col, 1); hero.box.addLayout(row); self.col.addWidget(hero)
        self.col.addWidget(self.anthem_card())
        two = ResponsiveGrid(420, 2, 16); two.add(self.flag_card()); two.add(self.emblem_card()); self.col.addWidget(two)
        more = [i for i in win.kb.category_items("symbols") if i.id not in ("tl.symbols.flag", "tl.symbols.emblem", "tl.symbols.anthem")] if hasattr(win.kb, "category_items") else \
               [i for i in win.kb.all("article") if i.category == "symbols" and i.id not in ("tl.symbols.flag", "tl.symbols.emblem", "tl.symbols.anthem")]
        if more:
            self.col.addLayout(section_title(t("sym_more")))
            grid = ResponsiveGrid(260, 3, 14)
            for item in more:
                c = Clickable(14, 22); r = QHBoxLayout(); r.setSpacing(12); r.addWidget(ClayIcon("flag-tl" if item.id.endswith("motto") else "star", "rose", 44))
                cc = QVBoxLayout(); cc.setSpacing(2); cc.addWidget(label(item.title(lang), "h3", wrap=True)); cc.addWidget(label(clip(item.summary(lang), 110), "caption", wrap=True))
                r.addLayout(cc, 1); c.box.addLayout(r); c.clicked.connect(lambda i=item.id: win.open_item(i)); grid.add(c)
            self.col.addWidget(grid)
        self.col.addStretch(); self.on_position(self.player.position())
    def anthem_card(self):
        win = self.win; t = win.t; lang = win.lang; data = self.data
        card = Card(20, 26); top = QHBoxLayout(); top.setSpacing(16)
        self.play_button = button(t("anthem_play"), self.player.toggle, "primary", "play"); self.play_button.setMinimumHeight(52); self.play_button.setMinimumWidth(170)
        top.addWidget(ClayIcon("music", "rose", 64))
        head = QVBoxLayout(); head.setSpacing(2); head.addWidget(label(kb.text(data.get("title"), lang), "h1", wrap=True))
        head.addWidget(label(t("anthem_credits", music=data.get("music", ""), lyrics=data.get("lyrics_by", "")), "muted", wrap=True)); top.addLayout(head, 1)
        top.addWidget(self.play_button, 0, Qt.AlignVCenter); card.box.addLayout(top)
        stage = Card(14, 22, tint=win.tok["primary_soft"]); self.section_label = label("", "eyebrow"); self.section_label.setAlignment(Qt.AlignCenter)
        self.prev_line = label("", "muted"); self.prev_line.setAlignment(Qt.AlignCenter)
        self.karaoke = KaraokeLine(); self.translation = label("", "h3", wrap=True); self.translation.setAlignment(Qt.AlignCenter)
        self.next_line = label("", "muted"); self.next_line.setAlignment(Qt.AlignCenter)
        for w in (self.section_label, self.prev_line, self.karaoke, self.translation, self.next_line): stage.box.addWidget(w)
        card.box.addWidget(stage)
        bar = QHBoxLayout(); bar.setSpacing(10); self.time_label = label("0:00", "caption"); bar.addWidget(self.time_label)
        self.slider = QSlider(Qt.Horizontal); self.slider.setRange(0, int(data.get("duration", 0) * 10)); self.slider.sliderMoved.connect(lambda v: self.time_label.setText(clock(v / 10)))
        self.slider.sliderReleased.connect(lambda: self.player.seek(self.slider.value() / 10))
        self.slider.actionTriggered.connect(lambda _a: QTimer.singleShot(0, self.keyboard_seek))     # arrow keys, Page Up/Down
        self.slider.setAccessibleName(t("anthem_play")); bar.addWidget(self.slider, 1); bar.addWidget(label(clock(data.get("duration", 0)), "caption"))
        restart = button("", lambda: (self.player.seek(0), self.player.play()), "icon", "refresh", t("anthem_restart")); restart.setFixedSize(40, 40); bar.addWidget(restart)
        self.repeat_button = button("", self.toggle_repeat, "icon", "repeat", t("anthem_repeat")); self.repeat_button.setFixedSize(40, 40); self.repeat_button.setCheckable(True); bar.addWidget(self.repeat_button)
        card.box.addLayout(bar)
        opts = QHBoxLayout(); self.show_tet = QCheckBox(t("anthem_translation")); self.show_tet.setChecked(lang == "tet"); self.show_tet.toggled.connect(lambda _=None: self.on_position(self.player.position()))
        opts.addWidget(self.show_tet); opts.addStretch(); opts.addWidget(Pill(t("anthem_respect"), "butter")); card.box.addLayout(opts)
        if not self.player.available:
            note = label(t("anthem_no_audio"), "caption", wrap=True); card.box.addWidget(note); self.play_button.setEnabled(False)
        # Full lyrics: refrain and verse; a click on a sung line jumps to it.
        card.box.addLayout(section_title(t("anthem_lyrics")))
        lyr = ResponsiveGrid(340, 2, 14)
        for part in ("refrain", "verse"):
            pc = Card(12, 20); pc.box.addWidget(label(t("anthem_" + part).upper(), "eyebrow"))
            for i, line in enumerate(data.get("lines", [])):
                if line.get("part") != part: continue
                r = Clickable(6, 14); rl = QVBoxLayout(); rl.setSpacing(0)
                main = label(line["pt"], "h3", wrap=True); rl.addWidget(main)
                if line.get("tet"): rl.addWidget(label(kb.show(line["tet"], "tet"), "caption", wrap=True))
                r.box.addLayout(rl); r.clicked.connect(lambda i=i: self.jump_to(i)); pc.box.addWidget(r); self.line_rows[i] = r
            pc.box.addStretch(); lyr.add(pc)
        card.box.addWidget(lyr)
        card.box.addWidget(label(kb.text(data.get("note"), lang), "caption", wrap=True))
        rec = data.get("recording", {})
        card.box.addWidget(label(f"{t('recording_credit')}: {kb.text(rec.get('origin'), lang)} {kb.text(rec.get('licence'), lang)}", "caption", wrap=True))
        return card
    def flag_card(self):
        win = self.win; t = win.t; lang = win.lang
        card = Card(18, 24); card.box.addLayout(section_title(t("sym_flag")))
        card.box.addWidget(Banner(lambda w, h: icons.illustration("flag", w, h), 190, 18))
        card.box.addWidget(label(t("sym_flag_text"), "muted", wrap=True))
        con = load_constitution(); a = con.article(15)
        if a:
            blocks = con.blocks(a, lang)
            colours = blocks[1]["text"] if len(blocks) > 1 else ""
            for part in [p.strip() for p in colours.split("•")[1:]]:
                row = QHBoxLayout(); row.setSpacing(10); name = part.split("-")[0].strip().lower()
                swatch = {"kinur": "#f2b632", "amarelo": "#f2b632", "metan": "#1d1b22", "preto": "#1d1b22", "mean": "#d62839", "vermelho": "#d62839", "mutin": "#ffffff", "branco": "#ffffff"}.get(name.split()[0] if name else "", "#cccccc")
                dot = label(""); dot.setFixedSize(22, 22); dot.setStyleSheet(f"background:{swatch}; border:2px solid {win.tok['line']}; border-radius:11px;")
                row.addWidget(dot); row.addWidget(label(kb.show(part.rstrip('.'), lang), wrap=True), 1); card.box.addLayout(row)
        buttons = QHBoxLayout(); buttons.addWidget(button(t("sym_read_article"), lambda: win.open_item("tl.symbols.flag"), "ghost", "book-open"))
        buttons.addWidget(button(t("sym_constitution", n=15), lambda: win.open("constitution", article=15), "ghost", "scales")); buttons.addStretch(); card.box.addLayout(buttons)
        card.box.addStretch(); return card
    def emblem_card(self):
        win = self.win; t = win.t; lang = win.lang
        card = Card(18, 24); card.box.addLayout(section_title(t("sym_emblem")))
        card.box.addWidget(Banner(lambda w, h: icons.illustration("emblem", w, h), 240, 18))
        for n, (tet, pt) in enumerate(EMBLEM_PARTS, 1):
            row = QHBoxLayout(); row.setSpacing(10); badge = label(str(n), "h3"); badge.setFixedSize(26, 26); badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(f"background:{win.tok['primary']}; color:white; border-radius:13px;")
            row.addWidget(badge, 0, Qt.AlignTop); row.addWidget(label(kb.show(tet if lang == "tet" else pt, lang), wrap=True), 1); card.box.addLayout(row)
        card.box.addWidget(label(t("sym_colours"), "caption", wrap=True)); card.box.addWidget(label(t("sym_emblem_note"), "caption", wrap=True))
        buttons = QHBoxLayout(); buttons.addWidget(button(t("sym_read_article"), lambda: win.open_item("tl.symbols.emblem"), "ghost", "book-open"))
        buttons.addWidget(button(t("sym_constitution", n=14), lambda: win.open("constitution", article=14), "ghost", "scales")); buttons.addStretch(); card.box.addLayout(buttons)
        card.box.addStretch(); return card
    # -------------------------------------------------------------- player
    def keyboard_seek(self):
        if not self.slider.isSliderDown(): self.player.seek(self.slider.value() / 10)
    def toggle_repeat(self): self.repeat = self.repeat_button.isChecked()
    def jump_to(self, line):
        when = next_time(self.data, line, self.player.position())
        if when is None: return
        self.player.seek(when)
        if self.player.available and self.player.state != "playing": self.player.play()
    def on_state(self, state):
        t = self.win.t; playing = state == "playing"
        self.play_button.setText(t("anthem_pause") if playing else t("anthem_play")); self.play_button.setProperty("icon_name", "pause" if playing else "play")
        from ..widgets import refresh_icon
        refresh_icon(self.play_button)
        if state == "stopped" and getattr(self, "_ended", False):
            self._ended = False
            if self.repeat: self.player.seek(0); self.player.play()
    def on_position(self, seconds):
        data = self.data; lines = data.get("lines", []); lang = self.win.lang; t = self.win.t
        if not hasattr(self, "karaoke"): return
        if self.player.state == "playing" and data.get("duration") and seconds >= data["duration"] - 0.3:
            self._ended = True
        line, progress, section = at(data, seconds)
        self.time_label.setText(clock(seconds))
        if not self.slider.isSliderDown(): self.slider.setValue(int(seconds * 10))
        if line is None:
            self.karaoke.set_line(t({"intro": "anthem_intro", "interlude": "anthem_interlude", "outro": "anthem_outro"}.get(section, "anthem_ready")) if section or seconds == 0 else "", 0.0)
            self.section_label.setText(""); self.prev_line.setText(""); self.next_line.setText(lines[0]["pt"] if lines and (section == "intro" or seconds == 0) else "")
            self.translation.setText("")
        else:
            self.section_label.setText(t("anthem_refrain" if lines[line].get("part") == "refrain" else "anthem_verse").upper())
            self.karaoke.set_line(lines[line]["pt"], progress)
            self.translation.setText(kb.show(lines[line].get("tet", ""), "tet") if self.show_tet.isChecked() else "")
            prev_line = (line - 1) % 4 if lines[line].get("part") == "refrain" else line - 1
            nxt = (line + 1) % 4 if lines[line].get("part") == "refrain" else line + 1
            self.prev_line.setText(lines[prev_line]["pt"] if 0 <= prev_line < len(lines) else "")
            self.next_line.setText(lines[nxt]["pt"] if 0 <= nxt < len(lines) else "")
        if line != self.current_line:
            tok = self.win.tok
            for i, row in self.line_rows.items(): row.tint = tok["primary_soft"] if i == line else None; row.update()
            self.current_line = line
    def retranslate(self): self.render()
