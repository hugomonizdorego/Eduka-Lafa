"""Instituisaun Estadu: a catalog of the State institutions of Timor-Leste.

It starts with the four organs of sovereignty of the Constitution (art. 67):
the President of the Republic, the National Parliament, the Government and the
courts, then the Government's ministries, justice, defence and security, the
independent bodies, agencies, local power and the leaders. Each card opens the
encyclopedia article; sections show only articles that exist.
"""
from ...qt import Qt, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from ... import kb, icons
from ..texts import extend
from ..widgets import Card, Clickable, ClayIcon, Pill, ResponsiveGrid, label, button, scroll, section_title, clear_layout, rounded, clip

extend({
    "inst_title": ("Instituisaun Estadu Timór-Leste nian", "As instituições do Estado de Timor-Leste", "The State institutions of Timor-Leste", "Lembaga-lembaga negara Timor-Leste"),
    "inst_sub": ("Husi órgaun soberania haat — Prezidente Repúblika, Parlamentu Nasionál, Governu no Tribunál sira (Konstituisaun artigu 67) — to'o ministériu, F-FDTL, PNTL no órgaun independente.",
                 "Dos quatro órgãos de soberania — Presidente da República, Parlamento Nacional, Governo e Tribunais (Constituição, artigo 67.º) — aos ministérios, às F-FDTL, à PNTL e aos órgãos independentes.",
                 "From the four organs of sovereignty — the President of the Republic, the National Parliament, the Government and the courts (Constitution, article 67) — to the ministries, the F-FDTL, the PNTL and the independent bodies.",
                 "Dari empat lembaga kedaulatan — Presiden Republik, Parlemen Nasional, Pemerintah dan pengadilan (Konstitusi, pasal 67) — hingga kementerian, F-FDTL, PNTL dan lembaga independen."),
    "inst_organs": ("Órgaun soberania haat", "Os quatro órgãos de soberania", "The four organs of sovereignty", "Empat lembaga kedaulatan"),
    "inst_organs_note": ("Sira ketak no hala'o servisu hamutuk: separasaun no interdependénsia podér (Konstituisaun artigu 69).",
                         "São separados e interdependentes: separação e interdependência de poderes (Constituição, artigo 69.º).",
                         "They are separate and depend on one another: separation and interdependence of powers (Constitution, article 69).",
                         "Lembaga-lembaga ini terpisah dan saling bergantung: pemisahan dan saling ketergantungan kekuasaan (Konstitusi, pasal 69)."),
    "organ_president": ("Prezidente Repúblika", "Presidente da República", "President of the Republic", "Presiden Republik"),
    "organ_president_text": ("Xefe Estadu; povu hili kada tinan lima.", "Chefe de Estado; eleito pelo povo por cinco anos.", "Head of State, elected by the people for five years.", "Kepala negara; dipilih rakyat untuk lima tahun."),
    "organ_parliament": ("Parlamentu Nasionál", "Parlamento Nacional", "National Parliament", "Parlemen Nasional"),
    "organ_parliament_text": ("Deputadu 65 halo lei no kontrola Governu.", "65 deputados fazem as leis e fiscalizam o Governo.", "65 members make the laws and oversee the Government.", "65 anggota membuat undang-undang dan mengawasi Pemerintah."),
    "organ_government": ("Governu", "Governo", "Government", "Pemerintah"),
    "organ_government_text": ("Primeiru-Ministru no ministru sira ukun polítika jerál nasaun nian.", "O Primeiro-Ministro e os ministros conduzem a política geral do país.", "The Prime Minister and ministers run the country's general policy.", "Perdana Menteri dan para menteri menjalankan kebijakan umum negara."),
    "organ_courts": ("Tribunál sira", "Tribunais", "Courts", "Pengadilan"),
    "organ_courts_text": ("Hala'o justisa ho povu nia naran; Tribunál Rekursu mak aas liu agora.", "Administram a justiça em nome do povo; o Tribunal de Recurso é hoje o mais alto.", "They administer justice in the name of the people; the Court of Appeal is the highest today.", "Mengadili atas nama rakyat; Pengadilan Banding kini yang tertinggi."),
    "inst_sec_sovereignty": ("Órgaun soberania", "Órgãos de soberania", "Organs of sovereignty", "Lembaga kedaulatan"),
    "inst_sec_government": ("Governu no ministériu sira", "Governo e ministérios", "Government and ministries", "Pemerintah dan kementerian"),
    "inst_sec_justice": ("Justisa", "Justiça", "Justice", "Peradilan"),
    "inst_sec_security": ("Defeza no seguransa", "Defesa e segurança", "Defence and security", "Pertahanan dan keamanan"),
    "inst_sec_independent": ("Órgaun independente", "Órgãos independentes", "Independent bodies", "Lembaga independen"),
    "inst_sec_agencies": ("Ajénsia no servisu públiku", "Agências e serviços públicos", "Agencies and public services", "Badan dan layanan publik"),
    "inst_sec_local": ("Podér lokál", "Poder local", "Local power", "Pemerintahan lokal"),
    "inst_sec_leaders": ("Lider sira", "Dirigentes", "Leaders", "Para pemimpin"),
    "inst_sec_more": ("Artigu seluk", "Outros artigos", "More articles", "Artikel lainnya"),
    "inst_open_constitution": ("Lee Konstituisaun artigu 67", "Ler a Constituição, artigo 67.º", "Read the Constitution, article 67", "Baca Konstitusi pasal 67"),
})

# (title key, icon, accent, article ids in reading order)
SECTIONS = [
    ("inst_sec_sovereignty", "landmark", "violet", ["tl.politics.system", "tl.politics.president_office", "tl.politics.parliament", "tl.politics.government",
                                                     "tl.politics.courts", "tl.institutions.court_of_appeal", "tl.politics.council_state"]),
    ("inst_sec_government", "people", "teal", ["tl.institutions.overview", "tl.institutions.ministries", "tl.institutions.education_ministry", "tl.institutions.higher_education",
                                                "tl.institutions.finance", "tl.institutions.justice", "tl.institutions.state_administration",
                                                "tl.institutions.youth_sport_culture", "tl.institutions.environment_tourism", "tl.institutions.transport_communications"]),
    ("inst_sec_justice", "scales", "rose", ["tl.institutions.court_of_appeal", "tl.institutions.public_prosecution", "tl.institutions.public_defender", "tl.politics.rights_duties"]),
    ("inst_sec_security", "shield", "slate", ["tl.institutions.ffdtl", "tl.institutions.pntl", "tl.institutions.security_agencies", "tl.politics.defence_security"]),
    ("inst_sec_independent", "ballot", "coral", ["tl.institutions.independent_bodies", "tl.institutions.pdhj", "tl.institutions.civil_service", "tl.politics.elections"]),
    ("inst_sec_agencies", "monitor", "sky", ["tl.institutions.tic_timor"]),
    ("inst_sec_local", "map", "mint", ["tl.politics.local_government", "tl.geography.administrative_divisions"]),
    ("inst_sec_leaders", "crown", "butter", ["tl.leaders.presidents", "tl.leaders.prime_ministers", "tl.leaders.governments", "tl.leaders.parliament_presidents"]),
]
# The four organs of sovereignty (Constitution art. 67): (key, icon, accent, article).
ORGANS = [("president", "crown", "violet", "tl.politics.president_office"), ("parliament", "landmark", "teal", "tl.politics.parliament"),
          ("government", "people", "peach", "tl.politics.government"), ("courts", "scales", "rose", "tl.politics.courts")]


class InstitutionsPage(QWidget):
    route = "institutions"

    def __init__(self, win):
        super().__init__(); self.win = win
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(16)
        outer.addWidget(scroll(self.body))

    def show_route(self, params): self.render()
    def retranslate(self): self.render()

    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; base = win.kb
        hero = Card(22, 26, gradient=(win.tok["nav_a"], win.tok["primary"], win.tok["nav_b"]))
        row = QHBoxLayout(); row.setSpacing(18); col = QVBoxLayout(); col.setSpacing(6)
        title = label(t("inst_title"), "h1", wrap=True); title.setStyleSheet("color:white;"); col.addWidget(title)
        sub = label(t("inst_sub"), wrap=True); sub.setStyleSheet("color:rgba(255,255,255,0.92); font-size:15px;"); col.addWidget(sub)
        links = QHBoxLayout(); links.addWidget(button(t("inst_open_constitution"), lambda: win.open("constitution", article=67), "chip", "scales")); links.addStretch(); col.addLayout(links)
        row.addLayout(col, 1)
        pic = QLabel(); pic.setPixmap(rounded(icons.illustration("government-palace", 280, 140), 18)); row.addWidget(pic, 0, Qt.AlignVCenter)
        hero.box.addLayout(row); self.col.addWidget(hero)
        # The four organs of sovereignty as big tiles.
        self.col.addLayout(section_title(t("inst_organs")))
        grid = ResponsiveGrid(220, 4, 14)
        for key, icon, acc, article in ORGANS:
            card = Clickable(16, 22); top = QHBoxLayout(); top.setSpacing(12); top.addWidget(ClayIcon(icon, acc, 52))
            top.addWidget(label(t("organ_" + key), "h3", wrap=True), 1); card.box.addLayout(top)
            card.box.addWidget(label(t(f"organ_{key}_text"), "caption", wrap=True))
            if base.get(article): card.clicked.connect(lambda a=article: win.open_item(a))
            grid.add(card)
        self.col.addWidget(grid)
        self.col.addWidget(label(t("inst_organs_note"), "muted", wrap=True))
        shown = set()
        for key, icon, acc, ids in SECTIONS:
            items = [base.get(i) for i in ids if base.get(i) and i not in shown]
            if not items: continue
            shown.update(i.id for i in items)
            self.col.addLayout(self.section_head(t(key), icon, acc, len(items)))
            g = ResponsiveGrid(300, 3, 14)
            for item in items: g.add(self.item_card(item))
            self.col.addWidget(g)
        # Articles of the category (or marked "also institutions") not placed above.
        more = [i for i in base.all("article") if (i.category == "institutions" or "institutions" in (i.get("also") or [])) and i.id not in shown]
        if more:
            self.col.addLayout(self.section_head(t("inst_sec_more"), "grid", "lilac", len(more)))
            g = ResponsiveGrid(300, 3, 14)
            for item in more: g.add(self.item_card(item))
            self.col.addWidget(g)
        self.col.addStretch()

    def section_head(self, text, icon, acc, n):
        row = QHBoxLayout(); row.setSpacing(10); row.addWidget(ClayIcon(icon, acc, 36)); row.addWidget(label(text, "h2"), 1)
        row.addWidget(Pill(str(n), acc)); return row

    def item_card(self, item):
        win = self.win; lang = win.lang
        card = Clickable(14, 20); row = QHBoxLayout(); row.setSpacing(12)
        from .encyclopedia import thumb
        pic = QLabel(); pic.setPixmap(thumb(item, win)); row.addWidget(pic, 0, Qt.AlignTop)
        cc = QVBoxLayout(); cc.setSpacing(3); cc.addWidget(label(item.title(lang), "h3", wrap=True))
        cc.addWidget(label(clip(item.summary(lang), 120), "caption", wrap=True)); row.addLayout(cc, 1); card.box.addLayout(row)
        if win.progress and win.progress.is_read(item.id): card.box.addWidget(Pill(win.t("read_done"), "mint"), 0, Qt.AlignLeft)
        card.clicked.connect(lambda i=item.id: win.open_item(i)); return card
