"""Kona-ba Lafa: what Lafa is, its version and licence, keyboard shortcuts,
the role of the Virtual Assistant, and where to report problems."""
from ...qt import Qt, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from ... import __version__, kb
from ..texts import extend
from ..widgets import Card, ClayIcon, Pill, ResponsiveGrid, label, button, scroll, section_title, clear_layout
from . import settings as _settings  # noqa: F401  (registers "open_lafa_config")

extend({
    "about_title": ("Lafa — Ensiklopédia Timór-Leste", "Lafa — Enciclopédia de Timor-Leste", "Lafa — Ensiklopedia Timor-Leste", "Lafa — Encyclopedia of Timor-Leste"),
    "about_sub": ("Software livre ba Edukasaun OS (Linux). Aprende Timór-Leste nia istória, kultura, Estadu, ekonomia, natureza no lian — ho internet ka la ho internet.",
                  "Software livre para o Edukasaun OS (Linux). Aprenda a história, a cultura, o Estado, a economia, a natureza e as línguas de Timor-Leste — com ou sem internet.",
                  "Perangkat lunak bebas untuk Edukasaun OS (Linux). Pelajari sejarah, budaya, negara, ekonomi, alam dan bahasa Timor-Leste — dengan atau tanpa internet.",
                  "Free software for Edukasaun OS (Linux). Learn Timor-Leste's history, culture, State, economy, nature and languages — online or offline."),
    "version": ("Versaun {v}", "Versão {v}", "Versi {v}", "Version {v}"),
    "inside": ("Saida mak iha laran", "O que tem", "Isinya", "What is inside"),
    "shortcuts": ("Teklas lalais", "Atalhos de teclado", "Pintasan papan ketik", "Keyboard shortcuts"),
    "sc_search": ("Buka", "Pesquisar", "Cari", "Search"),
    "sc_menu": ("Menu 1–9", "Menu 1–9", "Menu 1–9", "Menu 1–9"),
    "sc_back": ("Fila", "Voltar", "Kembali", "Back"),
    "sc_quiz": ("Hatán kuis", "Responder ao quiz", "Menjawab kuis", "Answer a quiz"),
    "sc_cards": ("Kartaun: hatene / seidauk", "Cartões: sei / ainda não", "Kartu: tahu / belum", "Cards: know / not yet"),
    "va_role_title": ("Asistente Virtuál: saida mak nia servisu?", "Assistente Virtual: para que serve?", "Asisten Virtual: untuk apa?", "Virtual Assistant: what is it for?"),
    "va_role": ("Lafa mak gia ba Timór-Leste no kolega estudu: hatudu faktu loron-loron, loron importante no feriadu, liafuan Tetun loron nian no kuis ki'ik; loke pájina loos iha Lafa Desktop; no ajuda uza komputadór (loke aplikasaun no konfigurasaun). La uza intelijénsia artifisiál no la haruka dadus.",
               "O Lafa é guia de Timor-Leste e colega de estudo: mostra factos do dia, datas importantes e feriados, a palavra tétum do dia e pequenos quizzes; abre a página certa no Lafa Desktop; e ajuda a usar o computador (abrir aplicações e definições). Não usa inteligência artificial nem envia dados.",
               "Lafa adalah pemandu Timor-Leste dan teman belajar: menampilkan fakta harian, hari penting dan hari libur, kata Tetun hari ini dan kuis kecil; membuka halaman yang tepat di Lafa Desktop; dan membantu memakai komputer (membuka aplikasi dan pengaturan). Tanpa kecerdasan buatan dan tanpa mengirim data.",
               "Lafa is a Timor-Leste guide and study buddy: daily facts, important days and holidays, the Tetun word of the day and small quizzes; it opens the right page in Lafa Desktop; and it helps with the computer (opening apps and settings). No artificial intelligence, no data sent."),
    "report": ("Hatoo problema ka ideia", "Comunicar um problema ou ideia", "Laporkan masalah atau ide", "Report a problem or idea"),
    "source_code": ("Kódigu fonte", "Código-fonte", "Kode sumber", "Source code"),
    "licence_line": ("Kódigu: lisensa MIT · Testu no ilustrasaun: CC BY-SA 4.0 · Haree “Fonte no lisensa”.", "Código: licença MIT · Textos e ilustrações: CC BY-SA 4.0 · Ver “Fontes e licenças”.",
                     "Kode: lisensi MIT · Teks dan ilustrasi: CC BY-SA 4.0 · Lihat “Sumber dan lisensi”.", "Code: MIT licence · Texts and illustrations: CC BY-SA 4.0 · See “Sources and licences”."),
    "review_call": ("Konteúdu sei iha versaun provizória. Profesór no espesialista sira, favór ajuda revee!", "O conteúdo ainda é provisório. Professores e especialistas: ajudem a rever!",
                    "Konten masih versi sementara. Guru dan ahli, mohon bantu meninjau!", "The content is still a draft. Teachers and experts: please help review it!"),
})

REPO = "https://github.com/hugomonizdorego/Eduka-Lafa"

class AboutPage(QWidget):
    route = "about"
    def __init__(self, win):
        super().__init__(); self.win = win
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(16)
        outer.addWidget(scroll(self.body))
    def show_route(self, params): self.render()
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; stats = win.kb.stats()
        hero = Card(24, 28, gradient=(win.tok["nav_a"], win.tok["primary"], win.tok["nav_b"]))
        row = QHBoxLayout(); row.setSpacing(20); pic = QLabel(); pic.setPixmap(win.atlas.pose_pixmap(win.settings.costume, 190)); row.addWidget(pic)
        c = QVBoxLayout(); c.setSpacing(8)
        for text_, name, style in ((t("about_title"), "h1", "color:white;"), (t("about_sub"), None, "color:rgba(255,255,255,0.94); font-size:16px;"),
                                   (t("version", v=__version__) + " · Edukasaun OS · Linux", "eyebrow", "color:white;"), (t("licence_line"), "caption", "color:rgba(255,255,255,0.9);")):
            l = label(text_, name, wrap=True); l.setStyleSheet(style); c.addWidget(l)
        links = QHBoxLayout()
        for text_, url, icon_name in ((t("source_code"), REPO, "document"), (t("report"), REPO + "/issues", "chat")):
            b = button(text_, lambda checked=False, u=url: win.open_url(u), None, icon_name); b.setStyleSheet("background:white; color:#3b2a8f; border:2px solid white; border-radius:16px; padding:8px 14px;")
            links.addWidget(b)
        links.addStretch(); c.addLayout(links); row.addLayout(c, 1); hero.box.addLayout(row); self.col.addWidget(hero)
        grid = ResponsiveGrid(170, 6, 12)
        for icon_name, acc, value, key in (("book-open", "violet", stats["articles"], "stat_articles"), ("map", "teal", stats["municipalities"] or 14, "stat_municipalities"),
                                           ("umbrella", "cyan", stats["places"], "stat_places"), ("calendar-check", "rose", stats["days"], "nav_calendar"),
                                           ("trophy", "butter", stats["questions"], "nav_quiz"), ("translate", "mint", stats["words"], "stat_words")):
            card = Card(12, 20); card.box.addWidget(ClayIcon(icon_name, acc, 44)); card.box.addWidget(label(f"{value:,}".replace(",", " "), "kpi")); card.box.addWidget(label(t(key), "caption", wrap=True)); grid.add(card)
        self.col.addLayout(section_title(t("inside"))); self.col.addWidget(grid)
        self.col.addWidget(label(t("review_call"), "muted", wrap=True))
        two = ResponsiveGrid(380, 2, 16)
        va = Card(18, 24); va.box.addLayout(section_title(t("va_role_title"))); va.box.addWidget(label(t("va_role"), "body", wrap=True))
        va.box.addWidget(button(t("open_lafa_config"), win.open_configuration, None, "settings"), 0, Qt.AlignLeft)
        va.box.addStretch(); two.add(va)
        sc = Card(18, 24); sc.box.addLayout(section_title(t("shortcuts"))); g = QGridLayout(); g.setHorizontalSpacing(16); g.setVerticalSpacing(8)
        for i, (keys, what) in enumerate((("Ctrl+F", t("sc_search")), ("Alt+1 … Alt+9", t("sc_menu")), ("Alt+←", t("sc_back")), ("A–D · 1–4 · Enter", t("sc_quiz")), ("← · →  ·  Espasu", t("sc_cards")))):
            g.addWidget(Pill(keys, "slate"), i, 0, Qt.AlignLeft); g.addWidget(label(what), i, 1)
        sc.box.addLayout(g); sc.box.addStretch(); two.add(sc)
        self.col.addWidget(two); self.col.addStretch()
    def retranslate(self): self.render()
