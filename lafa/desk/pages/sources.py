"""Fontes, lisensa no kréditu: the sources the encyclopedia is based on (the
owner's main sources first), every source used with its licence and the
articles that use it, the licences of Lafa itself, credits and the photos
downloaded for offline use with their authors."""
import html

from ...qt import Qt, QTimer, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from ... import kb, __version__
from ..texts import extend
from ..widgets import Card, ClayIcon, Pill, ResponsiveGrid, FlowLayout, SearchBox, label, button, scroll, section_title, clear_layout

extend({
    "src_title": ("Fonte, lisensa no kréditu", "Fontes, licenças e créditos", "Sumber, lisensi dan kredit", "Sources, licences and credits"),
    "src_sub": ("Lafa hakerek ninia testu rasik bazeia ba fonte sira ne'e. Obrigadu barak ba autór no organizasaun hotu ne'ebé fahe koñesimentu kona-ba Timór-Leste.",
                "O Lafa escreve os seus próprios textos com base nestas fontes. Muito obrigado a todos os autores e organizações que partilham conhecimento sobre Timor-Leste.",
                "Lafa menulis teksnya sendiri berdasarkan sumber-sumber ini. Terima kasih kepada semua penulis dan lembaga yang berbagi pengetahuan tentang Timor-Leste.",
                "Lafa writes its own texts based on these sources. Many thanks to all the authors and organisations who share knowledge about Timor-Leste."),
    "main_sources": ("Fonte prinsipál sira", "Fontes principais", "Sumber utama", "Main sources"),
    "all_sources": ("Fonte hotu ({n})", "Todas as fontes ({n})", "Semua sumber ({n})", "All sources ({n})"),
    "filter_sources": ("Buka fonte…", "Pesquisar fontes…", "Cari sumber…", "Search sources…"),
    "used_in": ("Uza iha: {items}", "Usada em: {items}", "Dipakai di: {items}", "Used in: {items}"),
    "licences_title": ("Lisensa sira", "Licenças", "Lisensi", "Licences"),
    "credits_title": ("Kréditu", "Créditos", "Kredit", "Credits"),
    "photos_title": ("Foto download ona ({n})", "Fotos descarregadas ({n})", "Foto yang diunduh ({n})", "Downloaded photos ({n})"),
    "no_photos": ("Seidauk iha foto. Uza “Offline no atualizasaun” atu download foto ho lisensa livre husi Wikimedia Commons.", "Ainda não há fotos. Use “Offline e atualizações” para descarregar fotos de licença livre do Wikimedia Commons.",
                  "Belum ada foto. Gunakan “Luring dan pembaruan” untuk mengunduh foto berlisensi bebas dari Wikimedia Commons.", "No photos yet. Use “Offline and updates” to download free-licence photos from Wikimedia Commons."),
    "visit": ("Vizita", "Visitar", "Kunjungi", "Visit"),
    "copyright_note": ("Fonte ho © la kopia: Lafa uza de'it faktu no hakerek ho liafuan rasik, no hatudu fonte.", "Fontes com © não são copiadas: o Lafa usa só factos, escreve com palavras próprias e cita a fonte.",
                       "Sumber ber-© tidak disalin: Lafa hanya memakai fakta, menulis dengan kata-kata sendiri, dan mencantumkan sumber.", "Sources marked © are not copied: Lafa only uses facts, writes in its own words and cites the source."),
})

MAIN_SOURCES = [
    ("Wikipedia", "https://www.wikipedia.org/", "CC BY-SA 4.0", "globe", "sky",
     ("Ensiklopédia livre iha lian barak.", "Enciclopédia livre em muitas línguas.", "Ensiklopedia bebas dalam banyak bahasa.", "The free encyclopedia in many languages.")),
    ("Wikipedia Tetun", "https://tet.wikipedia.org/wiki/P%C3%A1jina_Mahuluk", "CC BY-SA 4.0", "globe", "teal",
     ("Wikipedia iha lian Tetun.", "A Wikipédia em tétum.", "Wikipedia berbahasa Tetun.", "Wikipedia in Tetun.")),
    ("Governu Timór-Leste", "https://timor-leste.gov.tl/", "© Governo de Timor-Leste", "landmark", "violet",
     ("Portál ofisiál Governu nian: Estadu, lei no feriadu.", "Portal oficial do Governo: Estado, leis e feriados.", "Portal resmi pemerintah: negara, hukum dan hari libur.", "Official Government portal: State, laws and holidays.")),
    ("Timor-Leste Tourism", "https://timorleste.tl/", "© Timor-Leste tourism", "umbrella", "cyan",
     ("Informasaun turizmu ofisiál.", "Informação turística oficial.", "Informasi pariwisata resmi.", "Official tourism information.")),
    ("MAF Timor-Leste Fact File", "https://timorleste.mafint.org/maf-timor-leste/fact-file", "© MAF", "leaf", "green",
     ("Faktu kona-ba agrikultura, rai no klima.", "Factos sobre agricultura, terra e clima.", "Fakta pertanian, lahan dan iklim.", "Facts on farming, land and climate.")),
    ("Timor Research", "http://timor-research.org/about-timor-leste", "© Timor Research", "scroll", "lilac",
     ("Peskiza kona-ba Timór-Leste.", "Investigação sobre Timor-Leste.", "Riset tentang Timor-Leste.", "Research about Timor-Leste.")),
    ("World Bank Open Data", "https://data.worldbank.org/country/timor-leste", "CC BY 4.0", "chart", "green",
     ("Dadus populasaun, ekonomia no saúde.", "Dados de população, economia e saúde.", "Data penduduk, ekonomi dan kesehatan.", "Population, economy and health data.")),
    ("Encyclopaedia Britannica", "https://www.britannica.com/place/East-Timor", "© Britannica", "book-open", "indigo",
     ("Ensiklopédia ho istória no jeografia.", "Enciclopédia com história e geografia.", "Ensiklopedia sejarah dan geografi.", "Encyclopedia of history and geography.")),
    ("Tripadvisor Timor-Leste", "https://www.tripadvisor.com/Tourism-g295117-Timor_Leste-Vacations.html", "© Tripadvisor", "camera", "coral",
     ("Fatin turístiku no esperiénsia vizitante sira nian.", "Lugares turísticos e experiência de visitantes.", "Tempat wisata dan pengalaman pengunjung.", "Tourist places and visitors' experience.")),
    ("Ministériu Edukasaun", "https://moe.gov.tl/", "© Ministério da Educação", "graduation", "pink",
     ("Nível eskola no kurríkulu nasionál.", "Níveis escolares e currículo nacional.", "Jenjang sekolah dan kurikulum nasional.", "School levels and the national curriculum.")),
    ("Konstituisaun RDTL", "https://www.mj.gov.tl/jornal/lawsTL/RDTL-Law/RDTL-Constitution-P.pdf", "© RDTL", "scales", "rose",
     ("Testu Tetun ofisiál Lei-Inan nian: liafuan Estadu nian iha Lafa.", "Texto oficial em tétum da Constituição: termos do Estado no Lafa.", "Teks resmi Konstitusi berbahasa Tetun: istilah negara di Lafa.", "Official Tetun text of the Constitution: State terms in Lafa.")),
]

LICENCES = [
    ("Lafa (kódigu / código / kode / code)", "MIT License — © 2026 Hugo Moniz do Rego", "https://opensource.org/license/mit"),
    ("Testu, ilustrasaun no kuis Lafa", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    ("Wikipedia (testu download)", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    ("Wikimedia Commons (foto)", "CC0 · Public domain · CC BY · CC BY-SA (kada foto ho nia autór)", "https://commons.wikimedia.org/wiki/Commons:Licensing"),
    ("World Bank Open Data", "CC BY 4.0", "https://datacatalog.worldbank.org/public-licenses"),
    ("Mapa munisípiu (geoBoundaries / OpenStreetMap)", "ODbL 1.0 — © OpenStreetMap contributors", "https://www.openstreetmap.org/copyright"),
    ("Mapa postu (geoBoundaries / OCHA, WHO)", "CC BY 3.0 IGO", "https://data.humdata.org/dataset/timor-leste-administrative-boundaries-levels-0-3"),
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
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; base = win.kb; li = ("tet", "pt", "id", "en").index(lang) if lang in ("tet", "pt", "id", "en") else 3
        head = Card(20, 24); row = QHBoxLayout(); row.setSpacing(14); row.addWidget(ClayIcon("shield", "slate", 64))
        c = QVBoxLayout(); c.setSpacing(2); c.addWidget(label(t("src_title"), "h1", wrap=True)); c.addWidget(label(t("src_sub"), "muted", wrap=True)); row.addLayout(c, 1)
        head.box.addLayout(row); head.box.addWidget(label(t("copyright_note"), "caption", wrap=True)); self.col.addWidget(head)
        # Main sources (named by the owner).
        self.col.addLayout(section_title(t("main_sources")))
        grid = ResponsiveGrid(280, 3, 14)
        for name, url, licence, icon_name, acc, desc in MAIN_SOURCES:
            card = Card(14, 20); top = QHBoxLayout(); top.setSpacing(10); top.addWidget(ClayIcon(icon_name, acc, 44))
            cc = QVBoxLayout(); cc.setSpacing(0); cc.addWidget(label(name, "h3", wrap=True)); cc.addWidget(label(url.split("//", 1)[-1].split("/")[0], "caption")); top.addLayout(cc, 1)
            card.box.addLayout(top); card.box.addWidget(label(desc[li], "muted", wrap=True))
            bottom = QHBoxLayout(); bottom.addWidget(Pill(licence, "green" if licence.startswith("CC") else "slate")); bottom.addStretch()
            if win.online: bottom.addWidget(button(t("visit"), lambda checked=False, u=url: win.open_url(u), "ghost", "globe"))
            card.box.addStretch(); card.box.addLayout(bottom); grid.add(card)
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
