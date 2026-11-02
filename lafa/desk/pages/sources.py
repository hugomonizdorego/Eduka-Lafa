"""Fontes, lisensa no kréditu: the sources the encyclopedia is based on (the
owner's main sources first), every source used with its licence and the
articles that use it, the licences of Lafa itself, credits and the photos
downloaded for offline use with their authors."""
import html

from ...qt import Qt, QTimer, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from ... import kb, __version__
from ..texts import extend, index
from ..widgets import Card, ClayIcon, Pill, ResponsiveGrid, FlowLayout, SearchBox, label, button, scroll, section_title, clear_layout

extend({
    "src_title": ("Fonte, lisensa no kréditu", "Fontes, licenças e créditos"),
    "src_sub": ("Lafa hakerek ninia testu rasik bazeia ba fonte sira ne'e. Obrigadu barak ba autór no organizasaun hotu ne'ebé fahe koñesimentu kona-ba Timór-Leste.",
                "O Lafa escreve os seus próprios textos com base nestas fontes. Muito obrigado a todos os autores e organizações que partilham conhecimento sobre Timor-Leste."),
    "main_sources": ("Fonte prinsipál sira", "Fontes principais"),
    "all_sources": ("Fonte hotu ({n})", "Todas as fontes ({n})"),
    "filter_sources": ("Buka fonte…", "Pesquisar fontes…"),
    "used_in": ("Uza iha: {items}", "Usada em: {items}"),
    "licences_title": ("Lisensa sira", "Licenças"),
    "credits_title": ("Kréditu", "Créditos"),
    "photos_title": ("Foto download ona ({n})", "Fotos descarregadas ({n})"),
    "no_photos": ("Seidauk iha foto. Uza “Offline no atualizasaun” atu download foto ho lisensa livre husi Wikimedia Commons.", "Ainda não há fotos. Use “Offline e atualizações” para descarregar fotos de licença livre do Wikimedia Commons."),
    "visit": ("Vizita", "Visitar"),
    "owner_more": ("Fonte foun husi na'in projetu (0.3.0)", "Novas fontes indicadas pelo responsável (0.3.0)"),
    "copyright_note": ("Fonte ho © la kopia: Lafa uza de'it faktu no hakerek ho liafuan rasik, no hatudu fonte.", "Fontes com © não são copiadas: o Lafa usa só factos, escreve com palavras próprias e cita a fonte."),
})

MAIN_SOURCES = [
    ("Wikipedia", "https://www.wikipedia.org/", "CC BY-SA 4.0", "globe", "sky",
     ("Ensiklopédia livre iha lian barak.", "Enciclopédia livre em muitas línguas.")),
    ("Wikipedia Tetun", "https://tet.wikipedia.org/wiki/P%C3%A1jina_Mahuluk", "CC BY-SA 4.0", "globe", "teal",
     ("Wikipedia iha lian Tetun.", "A Wikipédia em tétum.")),
    ("Governu Timór-Leste", "https://timor-leste.gov.tl/", "© Governo de Timor-Leste", "landmark", "violet",
     ("Portál ofisiál Governu nian: Estadu, lei no feriadu.", "Portal oficial do Governo: Estado, leis e feriados.")),
    ("Timor-Leste Tourism", "https://timorleste.tl/", "© Timor-Leste tourism", "umbrella", "cyan",
     ("Informasaun turizmu ofisiál.", "Informação turística oficial.")),
    ("MAF Timor-Leste Fact File", "https://timorleste.mafint.org/maf-timor-leste/fact-file", "© MAF", "leaf", "green",
     ("Faktu kona-ba agrikultura, rai no klima.", "Factos sobre agricultura, terra e clima.")),
    ("Timor Research", "http://timor-research.org/about-timor-leste", "© Timor Research", "scroll", "lilac",
     ("Peskiza kona-ba Timór-Leste.", "Investigação sobre Timor-Leste.")),
    ("World Bank Open Data", "https://data.worldbank.org/country/timor-leste", "CC BY 4.0", "chart", "green",
     ("Dadus populasaun, ekonomia no saúde.", "Dados de população, economia e saúde.")),
    ("Encyclopaedia Britannica", "https://www.britannica.com/place/East-Timor", "© Britannica", "book-open", "indigo",
     ("Ensiklopédia ho istória no jeografia.", "Enciclopédia com história e geografia.")),
    ("Tripadvisor Timor-Leste", "https://www.tripadvisor.com/Tourism-g295117-Timor_Leste-Vacations.html", "© Tripadvisor", "camera", "coral",
     ("Fatin turístiku no esperiénsia vizitante sira nian.", "Lugares turísticos e experiência de visitantes.")),
    ("Ministériu Edukasaun", "https://moe.gov.tl/", "© Ministério da Educação", "graduation", "pink",
     ("Nível eskola no kurríkulu nasionál.", "Níveis escolares e currículo nacional.")),
    ("Konstituisaun RDTL", "https://www.mj.gov.tl/jornal/lawsTL/RDTL-Law/RDTL-Constitution-P.pdf", "© RDTL", "scales", "rose",
     ("Testu Tetun ofisiál Lei-Inan nian: liafuan Estadu nian iha Lafa.", "Texto oficial em tétum da Constituição: termos do Estado no Lafa.")),
]

# Sources the owner added for 0.3.0 (prehistory, history, institutions, sports, tourism).
OWNER_MORE = [
    ("Badan Geologi — fósil Timor", "https://geologi.esdm.go.id/media-center/mengenal-fosil-hewan-laut-penguasa-laut-purba-pulau-timor", "© Badan Geologi", "layers", "peach",
     ("Fósil animál tasi antigu iha tasi-le'un Timor.", "Fósseis de animais marinhos antigos da ilha de Timor.")),
    ("Tatoli — pterosauru Lesululi (2026)", "https://id.tatoli.tl/2026/08/11/igtl-temukan-fosil-pterosaurus-perkuat-potensi-lesululi-sebagai-situs-geologi/", "© Tatoli", "newspaper", "peach",
     ("IGTL hetan fósil pterosauru; Lesululi nu'udar fatin jeolójiku.", "O IGTL encontra um fóssil de pterossauro; Lesululi como sítio geológico.")),
    ("National Geographic Indonesia", "https://nationalgeographic.grid.id/read/13279503/wajah-manusia-prasejarah-terpahat-di-gua-timor-leste?page=all", "© National Geographic Indonesia", "image", "peach",
     ("Oin ema pre-istória ne'ebé kesi iha fatuk-kuak.", "Rostos pré-históricos gravados numa gruta.")),
    ("Inilah — ema dahuluk", "https://www.inilah.com/manusia-purba-hidup-di-timor-leste-44000-tahun-lalu-sebelum-piramida-di-mesir", "© Inilah", "newspaper", "lilac",
     ("Ema moris iha Timór tinan 44 000 liubá.", "Pessoas viviam em Timor há 44 000 anos.")),
    ("Dinosaur Pictures", "https://dinosaurpictures.org/", "© dinosaurpictures.org", "image", "peach",
     ("Imajen animál pre-istóriku (ligasaun de'it, la kopia imajen).", "Imagens de animais pré-históricos (só ligação, sem copiar imagens).")),
    ("Animalia — animál sira", "https://animalia.bio/timor-leste-animals", "© Animalia", "leaf", "mint",
     ("Lista animál ne'ebé moris iha Timór-Leste.", "Lista de animais que vivem em Timor-Leste.")),
    ("Rezerva — gia istória", "https://rezerva.tl/id/guide/history-guide", "© Rezerva", "scroll", "lilac",
     ("Istória Timór-Leste ba vizitante sira.", "História de Timor-Leste para visitantes.")),
    ("detikBali — istória no faktu", "https://www.detik.com/bali/berita/d-6647723/sejarah-dan-fakta-timor-leste-yang-pernah-jadi-bagian-indonesia", "© detik.com", "newspaper", "sky",
     ("Istória no faktu, ho perspetiva Indonézia nian.", "História e factos, numa perspetiva indonésia.")),
    ("Kompas — tinan 23", "https://www.kompas.id/artikel/perjalanan-23-tahun-timor-timur-menjadi-bagian-dari-indonesia", "© Kompas", "newspaper", "sky",
     ("Tinan 23 Timor-Timur iha Indonézia nia ukun (1976–1999).", "Os 23 anos de Timor-Timur sob a Indonésia (1976–1999).")),
    ("Timor-Leste Merdeka — foto", "https://timorlestemerdeka.wordpress.com/2014/06/08/beberapa-foto-sejarah-dari-perjuangan-kemerdekaan-timor-leste/", "© autór sira", "camera", "coral",
     ("Foto istóriku luta ba ukun-an (ligasaun de'it).", "Fotos históricas da luta pela independência (só ligação).")),
    ("US State Department — Background Note", "https://2009-2017.state.gov/outofdate/bgn/timorleste/101181.htm", "Domíniu públiku (EUA)", "landmark", "slate",
     ("Nota istória, polítika no ekonomia (arkivu 2009–2017).", "Nota de história, política e economia (arquivo 2009–2017).")),
    ("Koryo Group", "https://koryogroup.com/country/timor-leste", "© Koryo Group", "umbrella", "cyan",
     ("Informasaun viajen no kultura.", "Informação de viagem e cultura.")),
    ("Ministériu Justisa (Jornal da República)", "https://www.mj.gov.tl/", "© RDTL", "scales", "indigo",
     ("Lei sira no Jornal da República.", "Leis e Jornal da República.")),
    ("MESCC", "https://mescc.gov.tl/", "© RDTL", "graduation", "pink",
     ("Ensinu superiór, siénsia no kultura.", "Ensino superior, ciência e cultura.")),
    ("MJDAC", "https://mjdac.gov.tl/", "© RDTL", "medal", "green",
     ("Juventude, desportu, arte no kultura.", "Juventude, desporto, arte e cultura.")),
    ("Ministériu Finansas", "https://www.mof.gov.tl/", "© RDTL", "chart", "green",
     ("Orsamentu Jerál Estadu no Fundu Petrolíferu.", "Orçamento Geral do Estado e Fundo Petrolífero.")),
    ("Administrasaun Estatál", "https://estatal.gov.tl/", "© RDTL", "map", "teal",
     ("Munisípiu, postu administrativu no suku.", "Municípios, postos administrativos e sucos.")),
    ("ABS Clearing-House (MTA)", "https://abschm.mta.gov.tl/", "© RDTL", "leaf", "green",
     ("Rekursu jenétiku no biodiversidade.", "Recursos genéticos e biodiversidade.")),
    ("PNTL", "https://pntl.tl/", "© PNTL", "shield", "indigo",
     ("Polísia Nasionál Timór-Leste.", "Polícia Nacional de Timor-Leste.")),
    ("F-FDTL", "https://f-fdtl.mil.tl/", "© F-FDTL", "shield", "slate",
     ("FALINTIL–Forsa Defeza Timór-Leste.", "FALINTIL–Forças de Defesa de Timor-Leste.")),
    ("Wikipedia — PNTL no F-FDTL", "https://en.wikipedia.org/wiki/Timor-Leste_Defence_Force", "CC BY-SA 4.0", "globe", "sky",
     ("Artigu Wikipedia kona-ba forsa defeza no polísia.", "Artigos da Wikipédia sobre as forças de defesa e a polícia.")),
    ("FFTL", "https://www.fftl.tl/", "© FFTL", "medal", "green",
     ("Federasaun Futebol Timór-Leste.", "Federação de Futebol de Timor-Leste.")),
]

LICENCES = [
    ("Lafa (kódigu / código)", "MIT License — © 2026 Hugo Moniz do Rego", "https://opensource.org/license/mit"),
    ("Testu, ilustrasaun no kuis Lafa", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    ("Wikipedia (testu download)", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    ("Wikimedia Commons (foto)", "CC0 · Public domain · CC BY · CC BY-SA (kada foto ho nia autór)", "https://commons.wikimedia.org/wiki/Commons:Licensing"),
    ("World Bank Open Data", "CC BY 4.0", "https://datacatalog.worldbank.org/public-licenses"),
    ("Mapa munisípiu no postu (geoBoundaries / OCHA ROAP, WHO)", "CC BY 3.0 IGO", "https://data.humdata.org/dataset/timor-leste-administrative-boundaries-levels-0-3"),
    ("Konstituisaun RDTL (testu ofisiál tetun no portugés)", "Testu legál ofisiál — Jornal da República", "https://www.mj.gov.tl/jornal/"),
    ("Letra Nunito (Vernon Adams, Cyreal, Jacques Le Bailly)", "SIL Open Font License 1.1", "https://openfontlicense.org/"),
    ("Letra Noto (lian ASEAN)", "SIL Open Font License 1.1", "https://fonts.google.com/noto"),
    ("Qt / PyQt5 / PySide6", "LGPL / GPL", "https://www.qt.io/licensing/"),
    ("eSpeak NG (lee ho lian maka'as)", "GPL-3.0-or-later", "https://github.com/espeak-ng/espeak-ng"),
]

CREDITS = [
    "Lafa: Hugo Moniz do Rego no kolaboradór Edukasaun OS",
    "Konteúdu ensiklopédia: Lafa contributors (versaun provizória, presiza revizaun husi espesialista no profesór sira)",
    "geoBoundaries: Runfola, D. et al. (2020), PLoS ONE 15(4): e0231866",
    "Wikipedia no Wikimedia Commons: autór sira hotu",
    "Banku Mundiál: World Development Indicators",
]

class SourcesPage(QWidget):
    route = "sources"
    PAGE = 60
    def __init__(self, win):
        super().__init__(); self.win = win; self.query = ""; self.publisher = ""; self.limit = self.PAGE
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(16)
        outer.addWidget(scroll(self.body))
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.setInterval(300); self.timer.timeout.connect(self.apply_query)
    def show_route(self, params): self.render()
    def source_card(self, row, li):
        win = self.win; t = win.t; name, url, licence, icon_name, acc, desc = row
        card = Card(14, 20); top = QHBoxLayout(); top.setSpacing(10); top.addWidget(ClayIcon(icon_name, acc, 44))
        cc = QVBoxLayout(); cc.setSpacing(0); cc.addWidget(label(name, "h3", wrap=True)); cc.addWidget(label(url.split("//", 1)[-1].split("/")[0], "caption")); top.addLayout(cc, 1)
        card.box.addLayout(top); card.box.addWidget(label(desc[li], "muted", wrap=True))
        bottom = QHBoxLayout(); bottom.addWidget(Pill(licence, "green" if licence.startswith("CC") or "públiku" in licence else "slate")); bottom.addStretch()
        if win.online: bottom.addWidget(button(t("visit"), lambda checked=False, u=url: win.open_url(u), "ghost", "globe"))
        card.box.addStretch(); card.box.addLayout(bottom); return card
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; base = win.kb; li = index(lang)
        head = Card(20, 24); row = QHBoxLayout(); row.setSpacing(14); row.addWidget(ClayIcon("shield", "slate", 64))
        c = QVBoxLayout(); c.setSpacing(2); c.addWidget(label(t("src_title"), "h1", wrap=True)); c.addWidget(label(t("src_sub"), "muted", wrap=True)); row.addLayout(c, 1)
        head.box.addLayout(row); head.box.addWidget(label(t("copyright_note"), "caption", wrap=True)); self.col.addWidget(head)
        # Main sources (named by the owner).
        self.col.addLayout(section_title(t("main_sources")))
        grid = ResponsiveGrid(280, 3, 14)
        for row in MAIN_SOURCES: grid.add(self.source_card(row, li))
        self.col.addWidget(grid)
        self.col.addLayout(section_title(t("owner_more")))
        grid = ResponsiveGrid(280, 3, 14)
        for row in OWNER_MORE: grid.add(self.source_card(row, li))
        self.col.addWidget(grid)
        # Every source used, with filter by publisher.
        sources = base.sources()
        card = Card(16, 24); card.box.addLayout(section_title(t("all_sources", n=len(sources))))
        self.search = SearchBox(t("filter_sources")); self.search.setText(self.query); self.search.textEdited.connect(lambda _: self.timer.start()); card.box.addWidget(self.search)
        pubs = {}
        for s in sources:
            key = publisher_group(s); pubs[key] = pubs.get(key, 0) + 1
        chips = QWidget(); flow = FlowLayout(chips, 6)
        for key in [""] + sorted(pubs, key=lambda k: -pubs[k])[:14]:
            b = button(f"{key or t('all')} ({pubs[key] if key else len(sources)})", lambda checked=False, k=key: self.set_publisher(k), "chip"); b.setCheckable(True); b.setChecked(key == self.publisher); flow.addWidget(b)
        card.box.addWidget(chips)
        q = kb.fold(self.query).strip()
        shown = [s for s in sources if (not self.publisher or publisher_group(s) == self.publisher) and (not q or q in kb.fold(s["title"] + " " + s["publisher"] + " " + s["url"]))]
        for s in shown[:self.limit]:
            items = [base.get(i) for i in s["items"] if base.get(i)]
            a = f"style='color:{win.tok['primary']}; text-decoration:none; font-weight:700'"
            links = ", ".join(f"<a {a} href='lafa://item/{html.escape(i.id)}'>{html.escape(i.title(lang))}</a>" for i in items[:6]) + (f" +{len(items) - 6}" if len(items) > 6 else "")
            text_ = (f"<b>{html.escape(s['title'])}</b> — {html.escape(s['publisher'])}"
                     + (f" · {html.escape(t('licence'))}: {html.escape(s['licence'])}" if s.get("licence") else "")
                     + f"<br><a {a} href='{html.escape(s['url'])}'>{html.escape(s['url'][:90])}</a>"
                     + (f" <span style='color:{win.tok['muted']}'>({html.escape(t('accessed', date=s.get('accessed', '')))})</span>" if s.get("accessed") else "")
                     + (f"<br><span style='color:{win.tok['muted']}'>{t('used_in', items=links)}</span>" if links else ""))
            l = QLabel(text_); l.setWordWrap(True); l.setTextFormat(Qt.RichText); l.setOpenExternalLinks(False); l.linkActivated.connect(self.follow)
            l.setStyleSheet(f"background:{win.tok['card_hover']}; border-radius:14px; padding:10px 12px;"); card.box.addWidget(l)
        if len(shown) > self.limit: card.box.addWidget(button(t("show_more"), self.more, "primary", "arrow-down"), 0, Qt.AlignHCenter)
        self.col.addWidget(card)
        # Licences and credits.
        two = ResponsiveGrid(360, 2, 16)
        lc = Card(16, 24); lc.box.addLayout(section_title(t("licences_title")))
        for what, licence, url in LICENCES:
            l = QLabel(f"<b>{html.escape(what)}</b><br>{html.escape(licence)} · <a style='color:{win.tok['primary']}; text-decoration:none' href='{html.escape(url)}'>{html.escape(url.split('//', 1)[-1][:60])}</a>")
            l.setWordWrap(True); l.linkActivated.connect(self.follow); lc.box.addWidget(l)
        two.add(lc)
        cr = Card(16, 24); cr.box.addLayout(section_title(t("credits_title")))
        for line in CREDITS: cr.box.addWidget(label("• " + kb.show(line, "tet"), wrap=True))
        cr.box.addWidget(label(f"Lafa {__version__}", "caption")); cr.box.addStretch(); two.add(cr)
        self.col.addWidget(two)
        # Downloaded photos and their authors.
        photos = win.store.photos() if getattr(win, "store", None) else []
        ph = Card(16, 24); ph.box.addLayout(section_title(t("photos_title", n=len(photos))))
        if not photos: ph.box.addWidget(label(t("no_photos"), "muted", wrap=True))
        for p in photos[:200]:
            item = base.get(p["item"]); title = item.title(lang) if item else p["item"]
            l = QLabel(f"<b>{html.escape(title)}</b> — {html.escape(p['title'])}<br>{html.escape(p['author'] or '?')} · {html.escape(p['licence'])}"
                       + (f" · <a style='color:{win.tok['primary']}; text-decoration:none' href='{html.escape(p['source_url'])}'>Wikimedia Commons</a>" if p.get("source_url", "").startswith("https://") else ""))
            l.setWordWrap(True); l.linkActivated.connect(self.follow); ph.box.addWidget(l)
        self.col.addWidget(ph); self.col.addStretch()
    def follow(self, url):
        if url.startswith("lafa://item/"): self.win.open_item(url[len("lafa://item/"):])
        elif url.startswith(("https://", "http://")): self.win.open_url(url)
    def set_publisher(self, key): self.publisher = key; self.limit = self.PAGE; self.render()
    def apply_query(self):
        self.query = self.search.text(); self.limit = self.PAGE; self.render(); self.search.setFocus(); self.search.setCursorPosition(len(self.query))
    def more(self): self.limit += self.PAGE; self.render()
    def retranslate(self): self.render()

NAMES = {"wikipedia.org": "Wikipedia", "wikimedia.org": "Wikimedia", "worldbank.org": "World Bank", "tatoli.tl": "Tatoli", "laohamutuk.org": "La'o Hamutuk",
         "britannica.com": "Britannica", "tripadvisor.com": "Tripadvisor", "bancocentral.tl": "Banco Central", "chegareport.net": "Chega!",
         "un.org": "UN", "undp.org": "UN", "unicef.org": "UN", "who.int": "UN", "unesco.org": "UNESCO", "nobelprize.org": "NobelPrize.org"}

def publisher_group(source):
    """Short publisher name for the filter chips: the site's domain (all Wikipedias together, all gov.tl together…)."""
    host = source["url"].split("//", 1)[-1].split("/", 1)[0].lower().split(":")[0]
    if host.endswith(".gov.tl") or host == "gov.tl": return "gov.tl"
    labels = host.split(".")
    domain = ".".join(labels[-3:]) if len(labels) >= 3 and len(labels[-1]) == 2 and labels[-2] in ("gov", "org", "com", "edu", "ac", "net", "co") else ".".join(labels[-2:])
    return NAMES.get(domain, domain)
