"""Konfigurasaun: the learner's name and school level, language, theme, text
size, motion, the vocabulary language, the quiz clock, and the Virtual
Assistant (switched on in Eduka-Settings → Lafa-Configuration)."""
from dataclasses import replace

from ...qt import Qt, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QCheckBox, QSlider, QLabel, QMessageBox
from ... import kb, outfits
from ..texts import extend
from ..widgets import Card, Clickable, ClayIcon, Segmented, ResponsiveGrid, label, button, scroll, section_title, clear_layout
from .language import ORDER
from . import millionaire  # noqa: F401  (registers the quiz words used here)

extend({
    "set_title": ("Konfigurasaun", "Definições", "Pengaturan", "Settings"),
    "set_sub": ("Muda Lafa tuir ita-nia hakarak. Buat hotu rai iha komputadór ne'e de'it.", "Ajuste o Lafa ao seu gosto. Tudo fica guardado só neste computador.",
                "Sesuaikan Lafa sesukamu. Semua tersimpan hanya di komputer ini.", "Make Lafa yours. Everything is stored on this computer only."),
    "profile": ("Perfíl", "Perfil", "Profil", "Profile"),
    "your_name": ("Ita-nia naran", "O seu nome", "Namamu", "Your name"),
    "name_hint": ("Mamuk = naran husi sistema", "Vazio = nome do sistema", "Kosong = nama dari sistem", "Empty = name from the system"),
    "school_level": ("Nível eskola", "Nível escolar", "Jenjang sekolah", "School level"),
    "look": ("Lian no aparénsia", "Língua e aspeto", "Bahasa dan tampilan", "Language and look"),
    "app_language": ("Lian aplikasaun nian", "Língua da aplicação", "Bahasa aplikasi", "App language"),
    "system_language": ("Lian sistema nian", "Língua do sistema", "Bahasa sistem", "System language"),
    "theme": ("Tema", "Tema", "Tema", "Theme"),
    "theme_auto": ("Automátiku", "Automático", "Otomatis", "Automatic"),
    "theme_light": ("Naroman", "Claro", "Terang", "Light"),
    "theme_dark": ("Nakukun", "Escuro", "Gelap", "Dark"),
    "text_size": ("Tamañu letra: {n}%", "Tamanho do texto: {n}%", "Ukuran teks: {n}%", "Text size: {n}%"),
    "reduce_motion": ("Animasaun menus (la iha movimentu boot)", "Menos animação (sem movimentos grandes)", "Kurangi animasi (tanpa gerakan besar)", "Reduce motion (no big movements)"),
    "learning": ("Aprende", "Aprendizagem", "Belajar", "Learning"),
    "vocab_language": ("Lian ba liafuan Tetun", "Língua para as palavras em tétum", "Bahasa untuk kata Tetun", "Language for Tetun words"),
    "assistant": ("Asistente Virtuál Lafa", "Assistente Virtual Lafa", "Asisten Virtual Lafa", "Lafa Virtual Assistant"),
    "assistant_text": ("Lafa mosu iha ekrã hanesan gia ba Timór-Leste no kolega estudu: hatudu faktu, loron importante, liafuan loron nian no kuis ki'ik. Liga/dezliga iha Eduka-Settings → Lafa-Configuration.",
                       "O Lafa aparece no ecrã como guia de Timor-Leste e colega de estudo: mostra factos, datas importantes, a palavra do dia e pequenos quizzes. Ligar/desligar em Eduka-Settings → Lafa-Configuration.",
                       "Lafa muncul di layar sebagai pemandu Timor-Leste dan teman belajar: menampilkan fakta, hari penting, kata hari ini dan kuis kecil. Nyalakan/matikan di Eduka-Settings → Lafa-Configuration.",
                       "Lafa appears on the screen as a Timor-Leste guide and study buddy: facts, important days, the word of the day and small quizzes. Switch it on or off in Eduka-Settings → Lafa-Configuration."),
    "open_lafa_config": ("Loke Lafa-Configuration", "Abrir Lafa-Configuration", "Buka Lafa-Configuration", "Open Lafa-Configuration"),
    "knowledge_tips": ("Lafa fahe koñesimentu (faktu, feriadu, liafuan, kuis)", "O Lafa partilha conhecimento (factos, feriados, palavras, quiz)", "Lafa berbagi pengetahuan (fakta, hari libur, kata, kuis)", "Lafa shares knowledge (facts, holidays, words, quiz)"),
    "outfit": ("Hatais Lafa nian", "Roupa do Lafa", "Pakaian Lafa", "Lafa's outfit"),
    "assistant_on": ("Asistente: liga", "Assistente: ligado", "Asisten: aktif", "Assistant: on"),
    "assistant_off": ("Asistente: dezliga", "Assistente: desligado", "Asisten: mati", "Assistant: off"),
    "save_settings": ("Rai konfigurasaun", "Guardar definições", "Simpan pengaturan", "Save settings"),
    "saved_ok": ("Rai ona.", "Guardado.", "Tersimpan.", "Saved."),
    "reset_progress": ("Hamoos progresu", "Apagar progresso", "Hapus kemajuan", "Reset progress"),
    "reset_confirm": ("Hamoos XP, artigu lee ona, rezultadu kuis no liafuan aprende ona?", "Apagar XP, artigos lidos, resultados dos quizzes e palavras aprendidas?",
                      "Hapus XP, artikel yang dibaca, hasil kuis dan kata yang dipelajari?", "Delete XP, read articles, quiz results and learned words?"),
    "privacy": ("Privasidade", "Privacidade", "Privasi", "Privacy"),
    "privacy_text": ("Lafa la haruka dadus pesoál. Internet uza de'it atu download testu, foto no dadus públiku husi fonte ne'ebé hatudu iha “Fonte no lisensa”.",
                     "O Lafa não envia dados pessoais. A internet só serve para descarregar textos, fotos e dados públicos das fontes indicadas em “Fontes e licenças”.",
                     "Lafa tidak mengirim data pribadi. Internet hanya dipakai untuk mengunduh teks, foto dan data publik dari sumber di “Sumber dan lisensi”.",
                     "Lafa sends no personal data. The internet is only used to download texts, photos and public data from the sources listed in “Sources and licences”."),
})

OUTFIT_NAMES = {"casual": ("Kazuál aprende", "Casual de estudo", "Santai belajar", "Casual study"), "traditional": ("Tais Mane", "Tais Mane", "Tais Mane", "Tais Mane"),
                "tuxedo": ("Formál", "Formal", "Formal", "Formal")}

class SettingsPage(QWidget):
    route = "settings"
    def __init__(self, win):
        super().__init__(); self.win = win
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(16)
        outer.addWidget(scroll(self.body))
    def show_route(self, params): self.render()
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; s = win.settings
        head = Card(20, 24); row = QHBoxLayout(); row.setSpacing(14); row.addWidget(ClayIcon("settings", "indigo", 64))
        c = QVBoxLayout(); c.addWidget(label(t("set_title"), "h1")); c.addWidget(label(t("set_sub"), "muted", wrap=True)); row.addLayout(c, 1)
        head.box.addLayout(row); self.col.addWidget(head)
        grid = ResponsiveGrid(380, 2, 16)
        # Profile.
        pc = Card(18, 24); pc.box.addLayout(section_title(t("profile")))
        pc.box.addWidget(label(t("your_name"), "h3")); self.name = QLineEdit(s.learner_name); self.name.setPlaceholderText(t("name_hint")); self.name.setMaxLength(40); pc.box.addWidget(self.name)
        pc.box.addWidget(label(t("school_level"), "h3")); self.level = QComboBox()
        for lv in kb.LEVELS: self.level.addItem(kb.text(kb.LEVEL_NAMES[lv], lang), lv)
        self.level.setCurrentIndex(max(0, self.level.findData(s.school_level))); pc.box.addWidget(self.level); pc.box.addStretch(); grid.add(pc)
        # Language and look.
        lc = Card(18, 24); lc.box.addLayout(section_title(t("look")))
        lc.box.addWidget(label(t("app_language"), "h3")); self.language = QComboBox()
        for code, name in (("system", t("system_language")), ("tet", "Tetun"), ("pt", "Português"), ("id", "Bahasa Indonesia"), ("en", "English")): self.language.addItem(name, code)
        self.language.setCurrentIndex(max(0, self.language.findData(s.language))); lc.box.addWidget(self.language)
        lc.box.addWidget(label(t("theme"), "h3")); self.theme = Segmented([("auto", t("theme_auto")), ("light", t("theme_light")), ("dark", t("theme_dark"))], s.theme if s.theme in ("auto", "light", "dark") else "auto")
        lc.box.addWidget(self.theme, 0, Qt.AlignLeft)
        self.size_label = label(t("text_size", n=s.text_scale), "h3"); lc.box.addWidget(self.size_label)
        self.size = QSlider(Qt.Horizontal); self.size.setRange(90, 150); self.size.setSingleStep(5); self.size.setPageStep(10); self.size.setValue(int(s.text_scale))
        self.size.valueChanged.connect(lambda v: self.size_label.setText(t("text_size", n=v))); lc.box.addWidget(self.size)
        self.motion = QCheckBox(t("reduce_motion")); self.motion.setChecked(bool(s.reduce_motion)); lc.box.addWidget(self.motion); lc.box.addStretch(); grid.add(lc)
        # Learning.
        ec = Card(18, 24); ec.box.addLayout(section_title(t("learning")))
        ec.box.addWidget(label(t("vocab_language"), "h3")); self.vocab = QComboBox()
        for code in ORDER: self.vocab.addItem(kb.VOCAB_LANG_NAMES[code], code)
        self.vocab.setCurrentIndex(max(0, self.vocab.findData(s.vocab_lang))); ec.box.addWidget(self.vocab)
        self.timer = QCheckBox(t("mil_timer")); self.timer.setChecked(bool(s.quiz_timer)); ec.box.addWidget(self.timer)
        ec.box.addWidget(label(t("privacy"), "h3")); ec.box.addWidget(label(t("privacy_text"), "muted", wrap=True))
        ec.box.addWidget(button(t("reset_progress"), self.reset, "ghost", "refresh"), 0, Qt.AlignLeft); ec.box.addStretch(); grid.add(ec)
        # Virtual Assistant.
        vc = Card(18, 24); vc.box.addLayout(section_title(t("assistant")))
        status = label(t("assistant_on") if s.companion else t("assistant_off"), "eyebrow"); vc.box.addWidget(status)
        vc.box.addWidget(label(t("assistant_text"), "muted", wrap=True))
        self.tips = QCheckBox(t("knowledge_tips")); self.tips.setChecked(bool(s.knowledge_tips)); vc.box.addWidget(self.tips)
        vc.box.addWidget(label(t("outfit"), "h3")); orow = QHBoxLayout(); self.outfit = s.costume; self.outfit_cards = {}
        for key in ("casual", "traditional", "tuxedo"):
            if key not in outfits.OUTFITS: continue
            card = Clickable(8, 18, tint=win.tok["primary_soft"] if key == s.costume else None); pic = QLabel(); pic.setPixmap(win.atlas.pose_pixmap(key, 84)); pic.setAlignment(Qt.AlignCenter)
            card.box.addWidget(pic); n = label(OUTFIT_NAMES[key][("tet", "pt", "id", "en").index(lang)] if lang in ("tet", "pt", "id", "en") else key, "caption"); n.setAlignment(Qt.AlignCenter); card.box.addWidget(n)
            card.clicked.connect(lambda k=key: self.pick_outfit(k)); orow.addWidget(card); self.outfit_cards[key] = card
        vc.box.addLayout(orow)
        vc.box.addWidget(button(t("open_lafa_config"), win.open_configuration, None, "settings"), 0, Qt.AlignLeft); vc.box.addStretch(); grid.add(vc)
        self.col.addWidget(grid)
        save = button(t("save_settings"), self.save, "primary", "check"); save.setMinimumHeight(46); self.col.addWidget(save, 0, Qt.AlignLeft)
        self.col.addStretch()
    def pick_outfit(self, key):
        self.outfit = key; tok = self.win.tok
        for k, card in self.outfit_cards.items(): card.tint = tok["primary_soft"] if k == key else None; card.update()
    def save(self):
        win = self.win; s = win.settings
        new = replace(s, learner_name=self.name.text().strip()[:40], school_level=self.level.currentData() or s.school_level,
                      language=self.language.currentData() or s.language, theme=self.theme.current or "auto", text_scale=int(self.size.value()),
                      reduce_motion=self.motion.isChecked(), vocab_lang=self.vocab.currentData() or s.vocab_lang, quiz_timer=self.timer.isChecked(),
                      knowledge_tips=self.tips.isChecked(), costume=self.outfit)
        outfit_changed = new.costume != s.costume
        win.save_settings(new)
        if outfit_changed: win.change_outfit(new.costume)
        win.toast.show_text(win.t("saved_ok"))
    def reset(self):
        win = self.win
        if QMessageBox.question(self, win.t("reset_progress"), win.t("reset_confirm")) != QMessageBox.Yes: return
        p = win.progress
        p.read = {}; p.words = {}; p.scores = {}; p.xp = 0; p.achievements = {}; p.millionaire = {}; p.streak = 0; p.last_day = ""; p.recent = []; p.last = None
        try: p.save()
        except OSError as e: win.toast.show_text(str(e)); return
        win.update_profile(); self.render()
    def retranslate(self): self.render()
