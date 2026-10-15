"""Interactive learning modules, built from light Qt widgets, SVG and QPainter.

* dinosaurs     — hotspots on a Tyrannosaurus, the three periods, a sourced size
                  comparison and a "which period?" exercise;
* earth_history — two separate timelines: geological time and human history,
                  with a picture and an explanation for every event;
* industry      — put inventions in order, match each technology with its use and
                  explain the effects of factories.

Mouse and keyboard both work: every point, event and answer is a focusable
button (Tab, Enter/Space; arrow keys move along the timelines). Results are kept
on this computer (progress.json). Numbers are rounded and sourced; a reviewer
should still check them (docs/CONTENT-REVIEW.md).
"""
import math
import random

from .qt import (Qt, QSize, QRectF, QPointF, Signal, QColor, QPainter, QPen, QFont, QPainterPath,
                 QWidget, QFrame, QLabel, QPushButton, QComboBox, QListWidget, QListWidgetItem,
                 QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QButtonGroup, QAbstractItemView)
from . import icons
from .widgets import Illustration, Badge, tokens_of

def L(en, id_, pt, tet):
    return {"en": en, "id": id_, "pt": pt, "tet": tet}

def T(value, lang):
    return value.get(lang) or value.get("en", "") if isinstance(value, dict) else str(value)

UI = {
    "zoom_in": L("Zoom in", "Perbesar", "Ampliar", "Haboot"),
    "zoom_out": L("Zoom out", "Perkecil", "Reduzir", "Haki'ik"),
    "compare": L("Compare sizes", "Bandingkan ukuran", "Comparar tamanhos", "Kompara medida"),
    "anatomy": L("Body parts", "Bagian tubuh", "Partes do corpo", 'Isin nia parte'),
    "periods": L("Choose a period", "Pilih periode", "Escolha um período", "Hili períodu ida"),
    "know": L("Get to know the dinosaurs", "Kenali dinosaurus", "Conhecer os dinossauros", 'Koñese dinosauru sira'),
    "size_note": L("Approximate adult length from snout to tail; individual fossils differ.", "Perkiraan panjang dewasa dari moncong sampai ekor; tiap fosil berbeda.",
                   "Comprimento aproximado de um adulto, do focinho à cauda; cada fóssil é diferente.", "Animál boot nia naruk maizumenus, husi ibun to'o ikun; fósil ida-idak la hanesan."),
    "human": L("Person", "Manusia", "Pessoa", "Ema"),
    "match_title": L("Which period did they live in?", "Mereka hidup di periode apa?", "Em que período viveram?", "Sira moris iha períodu saida?"),
    "check": L("Check", "Periksa", "Verificar", 'Verifika'),
    "result": L("{s} of {n} correct.", "{s} dari {n} benar.", "{s} de {n} certas.", '{s} loos husi {n}.'),
    "choose": L("— choose —", "— pilih —", "— escolher —", "— hili —"),
    "geo": L("Geological time", "Skala waktu geologi", "Tempo geológico", "Tempu jeolójiku"),
    "human_time": L("Human history", "Sejarah manusia", "História humana", "Istória ema nian"),
    "geo_note": L("Millions of years ago, on a stretched scale so that recent events fit. The age of the Earth and human history use different scales.",
                  "Juta tahun lalu, dengan skala yang diregangkan agar peristiwa terbaru muat. Umur Bumi dan sejarah manusia memakai skala berbeda.",
                  "Milhões de anos atrás, numa escala esticada para caberem os acontecimentos recentes. A idade da Terra e a história humana usam escalas diferentes.",
                  "Tinan miliaun liubá, iha eskala ne'ebé dada naruk atu eventu foin lalais bele tama. Planeta Rai nia idade no istória ema nian uza eskala la hanesan."),
    "human_note": L("Years ago and dates; this scale is separate from geological time.", "Tahun lalu dan tanggal; skala ini terpisah dari waktu geologi.",
                    "Anos atrás e datas; esta escala é separada do tempo geológico.", "Tinan liubá no data; eskala ne'e la hanesan ho tempu jeolójiku."),
    "keys": L("Use ← → to move along the line.", "Gunakan ← → untuk bergerak di garis waktu.", "Use ← → para andar na linha.", "Uza ← → atu la'o iha liña."),
    "order_title": L("Put the inventions in order (oldest first)", "Urutkan penemuan (paling tua dulu)", "Ponha as invenções por ordem (a mais antiga primeiro)", "Tau invensaun sira tuir orden (ida tuan liu uluk)"),
    "up": L("Move up", "Naikkan", "Subir", "Hasa'e"),
    "down": L("Move down", "Turunkan", "Descer", "Hatún"),
    "order_keys": L("Select an item, then use the buttons or Ctrl+↑ / Ctrl+↓.", "Pilih satu item, lalu pakai tombol atau Ctrl+↑ / Ctrl+↓.", "Selecione um item e use os botões ou Ctrl+↑ / Ctrl+↓.", "Hili item ida, depois uza butaun ka Ctrl+↑ / Ctrl+↓."),
    "match_tech": L("Match each technology with its use", "Cocokkan setiap teknologi dengan kegunaannya", "Ligue cada tecnologia à sua utilidade", "Liga teknolojia ida-idak ho ninia uzu"),
    "impact_title": L("What did factories change?", "Apa yang diubah oleh pabrik?", "O que mudaram as fábricas?", "Fábrika muda saida?"),
    "right": L("Correct.", "Benar.", "Certo.", "Loos."),
    "wrong": L("Not quite.", "Belum tepat.", "Ainda não.", "Seidauk loos."),
    "source": L("Source", "Sumber", "Fonte", "Fonte"),
}

# ----------------------------------------------------------------- dinosaurs
# Hotspots on the T. rex picture (coordinates in the 640×360 illustration).
HOTSPOTS = [
    ((118, 138), L("Skull and teeth", "Tengkorak dan gigi", "Crânio e dentes", 'Ulun-ruin no nehan'),
     L("A huge skull about 1.5 m long with thick, serrated teeth up to about 30 cm including the root. Strong jaws could crush bone.",
       "Tengkorak besar sekitar 1,5 m dengan gigi tebal bergerigi hingga sekitar 30 cm termasuk akarnya. Rahang kuatnya bisa meremukkan tulang.",
       "Um crânio enorme com cerca de 1,5 m e dentes grossos e serrilhados até cerca de 30 cm com a raiz. As mandíbulas fortes partiam ossos.",
       "Ulun-ruin boot tebes, naruk maizumenus metru 1,5, ho nehan mahar no rohan hanesan serra, naruk to'o maizumenus cm 30 inklui abut. Kaban ne'ebé forte bele tata-kotu ruin.")),
    ((230, 228), L("Small arms", "Lengan kecil", "Braços pequenos", "Liman ki'ik"),
     L("The arms were short (about 1 m) with two fingers, but muscular. Scientists still discuss how they were used.",
       "Lengannya pendek (sekitar 1 m) dengan dua jari, tetapi berotot. Ilmuwan masih membahas kegunaannya.",
       "Os braços eram curtos (cerca de 1 m) com dois dedos, mas musculados. Os cientistas ainda discutem para que serviam.",
       "Liman badak (maizumenus metru 1) ho liman-fuan rua, maibé ho múskulu forte. Sientista sira sei diskute nafatin dinosauru uza liman sira-ne'e ba saida.")),
    ((330, 268), L("Strong legs", "Kaki yang kuat", "Pernas fortes", "Ain forte"),
     L("It walked on two powerful legs with three main toes. Footprints show that big theropods walked rather than ran fast.",
       "Ia berjalan dengan dua kaki kuat dan tiga jari utama. Jejak kaki menunjukkan teropoda besar lebih sering berjalan daripada berlari cepat.",
       "Andava sobre duas pernas fortes com três dedos principais. As pegadas mostram que os grandes terópodes andavam mais do que corriam.",
       "Nia la'o ho ain forte rua, ho ain-fuan prinsipál tolu. Ain-fatin hatudu katak teropode boot sira dala barak la'o de'it, la halai lalais.")),
    ((505, 178), L("Long tail", "Ekor panjang", "Cauda longa", "Ikun naruk"),
     L("The heavy tail balanced the large head, like a see-saw, and held strong leg muscles.",
       "Ekor yang berat menyeimbangkan kepala besar, seperti jungkat-jungkit, dan menjadi tempat otot kaki yang kuat.",
       "A cauda pesada equilibrava a cabeça grande, como um baloiço, e segurava músculos fortes das pernas.",
       "Ikun todan halo balansu ba ulun boot, hanesan baloiçu, no kaer múskulu ain nian ne'ebé forte.")),
]
TREX_SOURCES = [("Natural History Museum, London · Dino Directory", "https://www.nhm.ac.uk/discover/dino-directory/tyrannosaurus.html"),
                ("Field Museum · SUE the T. rex", "https://www.fieldmuseum.org/blog/sue-t-rex")]
PERIODS = [
    ("triassic", L("Triassic", "Trias", "Triásico", "Triásiku"), "252–201", "#d9a65a",
     L("Hot and dry; all land joined in Pangaea. The first dinosaurs were small and fast.", "Panas dan kering; semua daratan menyatu dalam Pangea. Dinosaurus pertama kecil dan cepat.",
       "Quente e seco; toda a terra unida na Pangeia. Os primeiros dinossauros eram pequenos e rápidos.", "Manas no maran; rai hotu hamutuk iha Pangea. Dinosauru dahuluk ki'ik no lalais."),
     ["Coelophysis", "Plateosaurus"]),
    ("jurassic", L("Jurassic", "Jura", "Jurássico", "Jurásiku"), "201–145", "#5f9a5a",
     L("Pangaea broke apart; warm and wet forests of ferns and conifers. Giant long-necked sauropods lived.", "Pangea terpecah; hutan hangat dan lembap penuh pakis dan konifer. Sauropoda raksasa berleher panjang hidup.",
       "A Pangeia separou-se; florestas quentes e húmidas de fetos e coníferas. Viviam saurópodes gigantes de pescoço longo.", "Pangea fahe-malu; ai-laran manas no bokon ho planta feto no ai-kónifera. Saurópode boot tebes ho kakorok naruk moris iha tempu ne'e."),
     ["Stegosaurus", "Brachiosaurus"]),
    ("cretaceous", L("Cretaceous", "Kapur", "Cretácico", "Kretásiku"), "145–66", "#2f8fb5",
     L("Continents moved towards their present places and the first flowering plants appeared. It ended with the asteroid impact.", "Benua bergerak ke tempatnya sekarang dan tumbuhan berbunga pertama muncul. Periode ini berakhir dengan tumbukan asteroid.",
       "Os continentes aproximaram-se das posições atuais e surgiram as primeiras plantas com flor. Terminou com o impacto de um asteroide.", "Kontinente sira muda besik ba sira-nia fatin ohin loron no ai-horis ho ai-funan dahuluk mosu. Períodu ne'e remata bainhira asteroide ida baku planeta Rai."),
     ["Velociraptor", "Triceratops", "Tyrannosaurus"]),
]
SIZES = [("Coelophysis", 3.0, "triassic"), ("Plateosaurus", 8.0, "triassic"), ("Stegosaurus", 9.0, "jurassic"), ("Brachiosaurus", 22.0, "jurassic"),
         ("Velociraptor", 2.0, "cretaceous"), ("Triceratops", 9.0, "cretaceous"), ("Tyrannosaurus", 12.0, "cretaceous")]
SIZE_SOURCE = ("Natural History Museum, London · Dino Directory (lengths); Field Museum (SUE, about 12.3 m)", "https://www.nhm.ac.uk/discover/dino-directory.html")
PERIOD_SOURCE = ("International Commission on Stratigraphy · Chronostratigraphic Chart (ages rounded)", "https://stratigraphy.org/chart")

class TrexCanvas(QWidget):
    """The T. rex picture with numbered hotspot buttons; zoom with + and −."""
    selected = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent); self.zoom = 1.0; self.setMinimumHeight(260); self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.buttons = []
        for i, (point, title, _) in enumerate(HOTSPOTS):
            b = QPushButton(str(i + 1), self); b.setObjectName("hotspot"); b.setFixedSize(34, 34); b.setCursor(Qt.PointingHandCursor)
            b.setAccessibleName(f"{i + 1}"); b.clicked.connect(lambda checked=False, i=i: self.selected.emit(i)); self.buttons.append(b)
    def set_names(self, names):
        for b, name in zip(self.buttons, names): b.setToolTip(name); b.setAccessibleName(name)
    def geometry_for(self):
        w, h = self.width(), self.height(); scale = min(w / 640, h / 360) * self.zoom
        return scale, (w - 640 * scale) / 2, (h - 360 * scale) / 2
    def set_zoom(self, value):
        self.zoom = max(1.0, min(1.8, value)); self.place(); self.update()
    def place(self):
        scale, ox, oy = self.geometry_for()
        for b, (point, _, _) in zip(self.buttons, HOTSPOTS):
            x, y = ox + point[0] * scale, oy + point[1] * scale
            b.move(int(x - 17), int(y - 17)); b.setVisible(0 <= x <= self.width() and 0 <= y <= self.height())
    def resizeEvent(self, event):
        super().resizeEvent(event); self.place()
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        scale, ox, oy = self.geometry_for()
        path = QPainterPath(); path.addRoundedRect(QRectF(self.rect()), 16, 16); p.setClipPath(path)
        p.fillRect(self.rect(), QColor("#e6f2e6"))
        pix = icons.illustration("module-trex", int(640 * scale), int(360 * scale), self.devicePixelRatioF())
        if not pix.isNull(): p.drawPixmap(int(ox), int(oy), pix)

class SizeChart(QWidget):
    """Bars to scale, with a person (1.7 m) for comparison."""
    def __init__(self, lang, parent=None):
        super().__init__(parent); self.lang = lang; self.period = None; self.setMinimumHeight(300)
    def set_period(self, key):
        self.period = key; self.update()
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); tok = tokens_of(self)
        r = QRectF(self.rect()).adjusted(8, 8, -8, -8)
        path = QPainterPath(); path.addRoundedRect(r, 16, 16); p.fillPath(path, QColor(tok.get("surface", "#ffffff")))
        rows = [(T(UI["human"], self.lang), 1.7, None)] + SIZES
        left = r.left() + 130; right = r.right() - 60; maxlen = 22.0; step = (r.height() - 40) / len(rows)
        p.setPen(QPen(QColor(tok.get("border", "#e1e7df")), 1))
        for m in range(0, 23, 5):
            x = left + (right - left) * m / maxlen; p.drawLine(QPointF(x, r.top() + 8), QPointF(x, r.bottom() - 26))
            p.setPen(QColor(tok.get("muted", "#5b6f68"))); p.drawText(QRectF(x - 20, r.bottom() - 24, 40, 18), Qt.AlignCenter, f"{m} m"); p.setPen(QPen(QColor(tok.get("border", "#e1e7df")), 1))
        colours = {k: c for k, _, _, c, _, _ in PERIODS}
        font = p.font(); font.setPointSizeF(max(8.0, font.pointSizeF())); p.setFont(font)
        for i, (name, length, period) in enumerate(rows):
            y = r.top() + 12 + i * step; h = max(10, step * 0.55)
            dim = self.period is not None and period not in (None, self.period)
            p.setPen(QColor(tok.get("text", "#17322b") if not dim else tok.get("muted", "#5b6f68")))
            p.drawText(QRectF(r.left() + 8, y, 118, h), Qt.AlignVCenter | Qt.AlignRight, name)
            colour = QColor("#7a8a85" if period is None else colours[period]); colour.setAlpha(90 if dim else 255)
            bar = QPainterPath(); bar.addRoundedRect(QRectF(left, y, (right - left) * length / maxlen, h), h / 2, h / 2); p.fillPath(bar, colour)
            p.setPen(QColor(tok.get("text", "#17322b"))); p.drawText(QRectF(left + (right - left) * length / maxlen + 6, y, 60, h), Qt.AlignVCenter, f"{length:g} m")

class DinosaurModule(QWidget):
    def __init__(self, window, article, parent=None):
        super().__init__(parent); self.win = window; lang = window.settings.locale; self.lang = lang; tok = tokens_of(window)
        v = QVBoxLayout(self); v.setContentsMargins(0, 6, 0, 6); v.setSpacing(12)
        row = QHBoxLayout(); row.setSpacing(16)
        left = QVBoxLayout(); left.setSpacing(8)
        self.canvas = TrexCanvas(); self.canvas.set_names([T(t, lang) for _, t, _ in HOTSPOTS]); self.canvas.selected.connect(self.show_hotspot)
        self.chart = SizeChart(lang); self.chart.hide()
        left.addWidget(self.canvas, 1); left.addWidget(self.chart, 1)
        tools = QHBoxLayout(); tools.setSpacing(8)
        for name, step, key in (("minus", -0.2, "zoom_out"), ("plus", 0.2, "zoom_in")):
            b = QPushButton(); b.setObjectName("iconbutton"); b.setFixedSize(38, 38); b.setIcon(icons.icon(name, tok["text"])); b.setToolTip(T(UI[key], lang)); b.setAccessibleName(T(UI[key], lang))
            b.clicked.connect(lambda checked=False, s=step: self.canvas.set_zoom(self.canvas.zoom + s)); tools.addWidget(b)
        self.compare = QPushButton(T(UI["compare"], lang)); self.compare.setCheckable(True); self.compare.setIcon(icons.icon("ruler", tok["text"])); self.compare.toggled.connect(self.toggle_compare); tools.addWidget(self.compare)
        tools.addStretch(); left.addLayout(tools)
        row.addLayout(left, 3)
        side = QFrame(); side.setObjectName("factcard"); sv = QVBoxLayout(side); sv.setContentsMargins(16, 14, 16, 14); sv.setSpacing(8)
        head = QLabel(T(UI["know"], lang)); head.setObjectName("cardtitle"); head.setWordWrap(True); sv.addWidget(head)
        tip = QLabel(window.t("explore_hint")); tip.setObjectName("cardcaption"); tip.setWordWrap(True); sv.addWidget(tip)
        self.info_title = QLabel(); self.info_title.setObjectName("rowtitle"); self.info_title.setWordWrap(True); sv.addWidget(self.info_title)
        self.info = QLabel(); self.info.setWordWrap(True); self.info.setTextFormat(Qt.PlainText); sv.addWidget(self.info)
        self.info_source = QLabel(); self.info_source.setObjectName("cardcaption"); self.info_source.setWordWrap(True); self.info_source.setTextFormat(Qt.RichText)
        self.info_source.setOpenExternalLinks(False); self.info_source.linkActivated.connect(window.open_web); sv.addWidget(self.info_source); sv.addStretch()
        side.setMinimumWidth(240); side.setMaximumWidth(360); row.addWidget(side, 2)
        v.addLayout(row, 1)
        # Period selector.
        prow = QHBoxLayout(); prow.setSpacing(10); plabel = QLabel(T(UI["periods"], lang)); plabel.setObjectName("cardtitle"); prow.addWidget(plabel)
        self.period_group = QButtonGroup(self); self.period_group.setExclusive(True); self.period_buttons = {}
        for key, name, years, colour, _, _ in PERIODS:
            b = QPushButton(f"{T(name, lang)}  ·  {years}"); b.setCheckable(True); b.setObjectName("periodbutton"); b.setMinimumHeight(42)
            b.setToolTip(f"{years} Ma"); b.clicked.connect(lambda checked=False, k=key: self.show_period(k)); self.period_group.addButton(b); prow.addWidget(b, 1); self.period_buttons[key] = b
        v.addLayout(prow)
        # "Which period?" exercise.
        box = QFrame(); box.setObjectName("factcard"); bv = QVBoxLayout(box); bv.setContentsMargins(16, 12, 16, 12); bv.setSpacing(8)
        t = QLabel(T(UI["match_title"], lang)); t.setObjectName("cardtitle"); bv.addWidget(t)
        grid = QGridLayout(); grid.setHorizontalSpacing(12); grid.setVerticalSpacing(6); self.match = []
        rng = random.Random(7); picks = rng.sample(SIZES, 4)
        for i, (name, _, period) in enumerate(picks):
            combo = QComboBox(); combo.addItem(T(UI["choose"], lang), "")
            for key, pname, years, _, _, _ in PERIODS: combo.addItem(T(pname, lang), key)
            combo.setAccessibleName(name); grid.addWidget(QLabel(name), i // 2, (i % 2) * 2); grid.addWidget(combo, i // 2, (i % 2) * 2 + 1); self.match.append((combo, period))
        bv.addLayout(grid)
        crow = QHBoxLayout(); check = QPushButton(T(UI["check"], lang)); check.setObjectName("primary"); check.clicked.connect(self.check_match); crow.addWidget(check)
        self.match_result = QLabel(); self.match_result.setWordWrap(True); crow.addWidget(self.match_result, 1); bv.addLayout(crow)
        v.addWidget(box)
        self.show_hotspot(0); self.show_period("cretaceous")
    def show_hotspot(self, i):
        _, title, text = HOTSPOTS[i]
        self.info_title.setText(f"{i + 1}. {T(title, self.lang)}"); self.info.setText(T(text, self.lang))
        self.info_source.setText(f"{T(UI['source'], self.lang)}: " + " · ".join(f'<a href="{u}">{n}</a>' for n, u in TREX_SOURCES))
        for k, b in enumerate(self.canvas.buttons): b.setProperty("active", k == i); b.style().unpolish(b); b.style().polish(b)
    def show_period(self, key):
        self.period_buttons[key].setChecked(True); self.chart.set_period(key)
        _, name, years, _, text, examples = next(p for p in PERIODS if p[0] == key)
        self.info_title.setText(f"{T(name, self.lang)} · {years} Ma"); self.info.setText(T(text, self.lang) + "\n\n" + ", ".join(examples))
        self.info_source.setText(f"{T(UI['source'], self.lang)}: <a href='{PERIOD_SOURCE[1]}'>{PERIOD_SOURCE[0]}</a>")
    def toggle_compare(self, on):
        self.canvas.setVisible(not on); self.chart.setVisible(on)
        if on:
            self.info_title.setText(T(UI["compare"], self.lang)); self.info.setText(T(UI["size_note"], self.lang) + "\n\n" + "\n".join(f"{n}: {l:g} m" for n, l, _ in SIZES))
            self.info_source.setText(f"{T(UI['source'], self.lang)}: <a href='{SIZE_SOURCE[1]}'>{SIZE_SOURCE[0]}</a>")
    def check_match(self):
        score = sum(1 for combo, period in self.match if combo.currentData() == period)
        self.match_result.setText(T(UI["result"], self.lang).format(s=score, n=len(self.match)))
        for combo, period in self.match: combo.setProperty("state", "right" if combo.currentData() == period else "wrong"); combo.style().unpolish(combo); combo.style().polish(combo)
        try: self.win.progress.record("activity:dinosaur_periods", score, len(self.match))
        except (ValueError, OSError, AttributeError): pass

# ------------------------------------------------------------- earth history
# (age, label, title, text, picture, source) — geological ages in millions of years.
GEO = [
    (4540, "4.54 Ga", L("The Earth forms", "Bumi terbentuk", "A Terra forma-se", 'Planeta Rai mosu'),
     L("Dust and rock around the young Sun joined to make the Earth. Soon after, a collision probably made the Moon.", "Debu dan batuan di sekitar Matahari muda bergabung membentuk Bumi. Tak lama kemudian, sebuah tabrakan kemungkinan membentuk Bulan.",
       "Poeira e rocha à volta do jovem Sol juntaram-se e formaram a Terra. Pouco depois, uma colisão terá formado a Lua.", "Rai-rahun no fatuk ne'ebé haleu loro-matan foun halibur-an no forma planeta Rai. La kleur depois, baku-malu boot ida karik forma Fulan."), "world-earth"),
    (3700, "3.7 Ga", L("Early life", "Kehidupan awal", "Vida primitiva", "Moris dahuluk"),
     L("Simple microbes lived in the sea. Layered rocks called stromatolites, built by microbes, are among the oldest signs of life.", "Mikroba sederhana hidup di laut. Batuan berlapis bernama stromatolit, dibuat mikroba, adalah salah satu tanda kehidupan tertua.",
       "Micróbios simples viviam no mar. Rochas em camadas chamadas estromatólitos, feitas por micróbios, estão entre os sinais de vida mais antigos.", "Mikróbiu simples moris iha tasi. Fatuk ho kamada naran estromatólitu, ne'ebé mikróbiu halo, mak sinál moris nian tuan liu."), "world-life_environment"),
    (2400, "2.4 Ga", L("Oxygen fills the air", "Oksigen mengisi udara", "O oxigénio enche o ar", 'Oksijéniu sai barak iha anin'),
     L("Microbes that use sunlight released oxygen. Oxygen built up in the air in the 'Great Oxidation Event'.", "Mikroba yang memakai sinar matahari melepaskan oksigen. Oksigen menumpuk di udara dalam 'Peristiwa Oksidasi Besar'.",
       "Micróbios que usam a luz do Sol libertaram oxigénio, que se acumulou no ar no 'Grande Evento de Oxidação'.", "Mikróbiu ne'ebé uza loro-matan nia naroman hasai oksijéniu. Oksijéniu halibur-an neineik iha anin ('Eventu Oksidasaun Boot')."), "world-life_environment"),
    (539, "539 Ma", L("The Cambrian explosion", "Ledakan Kambrium", "A explosão do Câmbrico", "Esplozaun Kámbriku"),
     L("Many animal groups with shells and skeletons appeared in the seas over a few tens of millions of years.", "Banyak kelompok hewan bercangkang dan berkerangka muncul di laut dalam beberapa puluh juta tahun.",
       "Muitos grupos de animais com conchas e esqueletos surgiram nos mares em algumas dezenas de milhões de anos.", 'Grupu animál barak ho kulit-toos no ruin mosu iha tasi iha tinan miliaun balun nia laran.'), "world-geography_oceans"),
    (252, "252 Ma", L("The great dying", "Kepunahan besar", "A grande extinção", 'Estinsaun boot'),
     L("The largest mass extinction: most sea species and many land species died out, probably after huge volcanic eruptions.", "Kepunahan massal terbesar: sebagian besar spesies laut dan banyak spesies darat punah, kemungkinan setelah letusan gunung api raksasa.",
       "A maior extinção em massa: a maioria das espécies marinhas e muitas terrestres desapareceram, provavelmente após enormes erupções vulcânicas.", 'Estinsaun boot liu: espésie tasi barak liu no espésie rai barak lakon, karik tanba foho-ahi boot sira nakfera.'), "world-earth"),
    (230, "230 Ma", L("The first dinosaurs", "Dinosaurus pertama", "Os primeiros dinossauros", 'Dinosauru dahuluk'),
     L("Small, two-legged dinosaurs appear in the Triassic. They later became the main large land animals.", "Dinosaurus kecil berkaki dua muncul pada Trias. Kemudian mereka menjadi hewan darat besar yang utama.",
       "Pequenos dinossauros de duas patas surgem no Triásico. Mais tarde tornaram-se os principais grandes animais terrestres.", "Dinosauru ki'ik ho ain rua mosu iha Triásiku. Depois sira sai animál boot prinsipál iha rai maran."), "module-trex"),
    (66, "66 Ma", L("The asteroid impact", "Tumbukan asteroid", "O impacto do asteroide", 'Asteroide baku planeta Rai'),
     L("An asteroid about 10 km wide hit Mexico (Chicxulub). Non-bird dinosaurs died out; mammals and birds spread.", "Asteroid selebar sekitar 10 km menghantam Meksiko (Chicxulub). Dinosaurus selain burung punah; mamalia dan burung menyebar.",
       "Um asteroide com cerca de 10 km atingiu o México (Chicxulub). Os dinossauros não-aves desapareceram; mamíferos e aves espalharam-se.", "Asteroide ida ho luan maizumenus km 10 baku México (Chicxulub). Dinosauru sira (la'ós manu) lakon; mamíferu no manu sira habelar-an."), "world-dinosaurs"),
    (4, "≈ 4 Ma", L("Timor rises from the sea", "Timor muncul dari laut", "Timor sobe do mar", "Timor sa'e husi tasi"),
     L("The Australian plate pushed against the Banda arc and lifted old sea floor; the island of Timor rose a few million years ago and is still rising.", "Lempeng Australia mendorong busur Banda dan mengangkat dasar laut lama; Pulau Timor naik beberapa juta tahun lalu dan masih naik.",
       "A placa australiana empurrou o arco de Banda e levantou o antigo fundo do mar; a ilha de Timor subiu há alguns milhões de anos e continua a subir.", "Plaka Austrália dudu arku Banda no hasa'e tasi-okos tuan; illa Timor sa'e tinan miliaun balun liubá no sei sa'e nafatin."), "timor-map"),
    (0.3, "0.3 Ma", L("Homo sapiens", "Homo sapiens", "Homo sapiens", "Homo sapiens"),
     L("Our species appears in Africa about 300,000 years ago — a tiny moment on this scale.", "Spesies kita muncul di Afrika sekitar 300.000 tahun lalu — saat yang sangat singkat pada skala ini.",
       "A nossa espécie surge em África há cerca de 300 000 anos — um instante nesta escala.", "Ita-nia espésie mosu iha Áfrika maizumenus tinan rihun 300 liubá — momentu badak tebes iha eskala ne'e."), "world-human_origins"),
]
GEO_SOURCES = [("International Commission on Stratigraphy · Chronostratigraphic Chart", "https://stratigraphy.org/chart"), ("USGS · Geologic time", "https://www.usgs.gov/programs/national-cooperative-geologic-mapping-program/science/geologic-time-scale")]
HUMAN = [
    (-300000, L("300,000 years ago", "300.000 tahun lalu", "há 300 000 anos", "tinan rihun 300 liubá"), L("Our species in Africa", "Spesies kita di Afrika", "A nossa espécie em África", "Ita-nia espésie iha Áfrika"),
     L("Fossils from Jebel Irhoud (Morocco) show early Homo sapiens about 300,000 years ago.", "Fosil dari Jebel Irhoud (Maroko) menunjukkan Homo sapiens awal sekitar 300.000 tahun lalu.", "Fósseis de Jebel Irhoud (Marrocos) mostram Homo sapiens antigos com cerca de 300 000 anos.", "Fósil husi Jebel Irhoud (Marrokus) hatudu Homo sapiens dahuluk maizumenus tinan rihun 300 liubá."), "world-human_origins"),
    (-50000, L("about 50,000 years ago", "sekitar 50.000 tahun lalu", "há cerca de 50 000 anos", "maizumenus tinan rihun 50 liubá"), L("Across the sea to Sahul", "Menyeberang laut ke Sahul", "Pelo mar até Sahul", "Hakur tasi ba Sahul"),
     L("People crossed the islands of Wallacea by boat and reached New Guinea and Australia (Sahul) at least about 50,000 years ago.", "Manusia menyeberangi pulau-pulau Wallacea dengan perahu dan mencapai Papua dan Australia (Sahul) setidaknya sekitar 50.000 tahun lalu.",
       "Pessoas atravessaram as ilhas da Wallacea de barco e chegaram à Nova Guiné e à Austrália (Sahul) há pelo menos cerca de 50 000 anos.", "Ema hakur illa Wallacea nian ho beiro no to'o Papua no Austrália (Sahul) maizumenus tinan rihun 50 liubá."), "world-colonialism"),
    (-42000, L("about 42,000 years ago", "sekitar 42.000 tahun lalu", "há cerca de 42 000 anos", "maizumenus tinan rihun 42 liubá"), L("Deep-sea fishing in Timor", "Menangkap ikan laut dalam di Timor", "Pesca em mar alto em Timor", "Kaer ikan tasi kle'an iha Timor"),
     L("At Jerimalai cave (Lautém) people caught tuna and other open-sea fish — some of the oldest evidence of deep-sea fishing.", "Di gua Jerimalai (Lautém) orang menangkap tuna dan ikan laut lepas lain — salah satu bukti tertua penangkapan ikan laut dalam.",
       "Na gruta de Jerimalai (Lautém) pescavam atum e outros peixes do alto mar — das provas mais antigas de pesca em mar profundo.", "Iha fatuk-kuak Jerimalai (Lautém) ema kaer atun no ikan tasi kle'an seluk — prova tuan liu ida husi kaer ikan iha tasi kle'an."), "timor-history"),
    (-11000, L("about 11,000 years ago", "sekitar 11.000 tahun lalu", "há cerca de 11 000 anos", "maizumenus tinan rihun 11 liubá"), L("The first farmers", "Petani pertama", "Os primeiros agricultores", "To'os-na'in dahuluk"),
     L("Farming began in several places, such as the Middle East, China and New Guinea, at different times.", "Pertanian dimulai di beberapa tempat, seperti Timur Tengah, Tiongkok, dan Papua, pada waktu yang berbeda.",
       "A agricultura começou em vários lugares, como o Médio Oriente, a China e a Nova Guiné, em épocas diferentes.", "Agrikultura hahú iha fatin balun, hanesan Oriente Médiu, Xina no Papua, iha tempu la hanesan."), "world-civilizations"),
    (-5200, L("about 3200 BCE", "sekitar 3200 SM", "cerca de 3200 a.C.", "maizumenus tinan 3200 molok Kristu"), L("Writing", "Tulisan", "A escrita", "Hakerek"),
     L("Writing (cuneiform) appeared in Mesopotamia; writing was also invented independently in other places.", "Tulisan (paku) muncul di Mesopotamia; tulisan juga ditemukan secara terpisah di tempat lain.",
       "A escrita (cuneiforme) surgiu na Mesopotâmia; também foi inventada de forma independente noutros lugares.", "Hakerek (kuneiforme) mosu iha Mezopotámia; ema mós hetan hakerek iha fatin seluk."), "world-civilizations"),
    (-575, L("1450s", "1450-an", "anos 1450", 'dékada 1450'), L("Printing press in Europe", "Mesin cetak di Eropa", "A imprensa na Europa", 'Imprensa iha Europa'),
     L("Gutenberg's press spread books quickly; printing with blocks and movable type already existed in East Asia.", "Mesin cetak Gutenberg menyebarkan buku dengan cepat; cetak blok dan huruf lepas sudah ada di Asia Timur.",
       "A prensa de Gutenberg espalhou livros depressa; a impressão com blocos e tipos móveis já existia na Ásia Oriental.", "Gutenberg nia imprensa habelar livru lalais; imprime ho bloku no letra ne'ebé bele muda iha ona uluk iha Ázia Leste."), "world-inventions"),
    (-510, L("about 1515", "sekitar 1515", "cerca de 1515", "maizumenus 1515"), L("Portuguese at Lifau", "Portugis di Lifau", "Portugueses em Lifau", "Portugés iha Lifau"),
     L("Portuguese traders came for sandalwood and landed at Lifau (Oé-Cusse).", "Pedagang Portugis datang untuk cendana dan mendarat di Lifau (Oé-Cusse).",
       "Comerciantes portugueses vieram pelo sândalo e desembarcaram em Lifau (Oé-Cusse).", 'Komersiante Portugés sira mai atu buka ai-kameli no tun iha Lifau (Oé-Cusse).'), "world-colonialism"),
    (-220, L("1760–1840", "1760–1840", "1760–1840", "1760–1840"), L("Industrial Revolution", "Revolusi Industri", "Revolução Industrial", "Revolusaun Industriál"),
     L("Machines, steam power and factories changed work, first in Britain and then in many countries.", "Mesin, tenaga uap, dan pabrik mengubah pekerjaan, mula-mula di Britania lalu di banyak negara.",
       "Máquinas, vapor e fábricas mudaram o trabalho, primeiro na Grã-Bretanha e depois em muitos países.", 'Mákina, forsa vapór no fábrika muda oinsá ema servisu, uluk iha Grã-Bretanha, depois iha nasaun barak.'), "world-industrial_revolution"),
    (-80, L("1945", "1945", "1945", "1945"), L("The United Nations", "Perserikatan Bangsa-Bangsa", "As Nações Unidas", 'Nasaun Unidas'),
     L("After the Second World War, countries founded the United Nations to keep peace.", "Setelah Perang Dunia Kedua, negara-negara mendirikan PBB untuk menjaga perdamaian.",
       "Depois da Segunda Guerra Mundial, os países fundaram as Nações Unidas para manter a paz.", 'Depois Funu Mundiál Daruak, nasaun sira harii Nasaun Unidas atu hametin dame.'), "world-world_wars"),
    (-23, L("2002", "2002", "2002", "2002"), L("Timor-Leste restores independence", "Timor-Leste memulihkan kemerdekaan", "Timor-Leste restaura a independência", "Timor-Leste restaura independénsia"),
     L("After the 1999 popular consultation, independence was restored on 20 May 2002.", "Setelah jajak pendapat 1999, kemerdekaan dipulihkan pada 20 Mei 2002.",
       "Depois da consulta popular de 1999, a independência foi restaurada em 20 de maio de 2002.", 'Depois konsulta populár iha 1999, Timor-Leste restaura ninia independénsia iha 20 Maiu 2002.'), "timor-history"),
]
HUMAN_SOURCES = [("Smithsonian · Human Origins", "https://humanorigins.si.edu/"), ("O'Connor et al. 2011, Science · Jerimalai", "https://www.science.org/doi/10.1126/science.1207703")]

class TimelineCanvas(QWidget):
    """A horizontal line with one focusable button per event."""
    selected = Signal(int)
    def __init__(self, positions, colours, parent=None):
        super().__init__(parent); self.positions = positions; self.current = 0; self.setMinimumHeight(110); self.colours = colours
        self.buttons = []
        for i in range(len(positions)):
            b = QPushButton("", self); b.setObjectName("timelinedot"); b.setFixedSize(26, 26); b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda checked=False, i=i: self.select(i)); self.buttons.append(b)
        self.setFocusPolicy(Qt.StrongFocus)
    def set_names(self, names):
        for b, n in zip(self.buttons, names): b.setToolTip(n); b.setAccessibleName(n)
    def select(self, i):
        self.current = max(0, min(len(self.positions) - 1, i))
        for k, b in enumerate(self.buttons): b.setProperty("active", k == self.current); b.style().unpolish(b); b.style().polish(b)
        self.buttons[self.current].setFocus(); self.selected.emit(self.current); self.update()
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Right, Qt.Key_Down): self.select(self.current + 1)
        elif event.key() in (Qt.Key_Left, Qt.Key_Up): self.select(self.current - 1)
        elif event.key() == Qt.Key_Home: self.select(0)
        elif event.key() == Qt.Key_End: self.select(len(self.positions) - 1)
        else: super().keyPressEvent(event)
    def place(self):
        left, right = 30, self.width() - 30; y = self.height() // 2
        for b, pos in zip(self.buttons, self.positions): b.move(int(left + (right - left) * pos - 13), y - 13)
    def resizeEvent(self, event):
        super().resizeEvent(event); self.place()
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); tok = tokens_of(self)
        left, right = 30, self.width() - 30; y = self.height() // 2
        grad_pen = QPen(QColor(tok.get("accent", "#00a879")), 4); grad_pen.setCapStyle(Qt.RoundCap); p.setPen(grad_pen); p.drawLine(left, y, right, y)
        pos = self.positions[self.current]; x = left + (right - left) * pos
        p.setPen(QPen(QColor(tok.get("accent_strong", "#007252")), 2, Qt.DashLine)); p.drawLine(int(x), 6, int(x), y - 16)

class TimelineModule(QWidget):
    def __init__(self, window, article, parent=None):
        super().__init__(parent); self.win = window; self.lang = window.settings.locale; tok = tokens_of(window); lang = self.lang
        v = QVBoxLayout(self); v.setContentsMargins(0, 6, 0, 6); v.setSpacing(10)
        top = QHBoxLayout(); self.scale_group = QButtonGroup(self); self.scale_buttons = {}
        for i, (key, name) in enumerate((("geo", UI["geo"]), ("human", UI["human_time"]))):
            b = QPushButton(T(name, lang)); b.setCheckable(True); b.setObjectName("segfirst" if i == 0 else "seglast"); b.setMinimumHeight(40)
            b.setIcon(icons.icon("timeline", tok["muted"], tok["accent_strong"])); b.clicked.connect(lambda checked=False, k=key: self.set_scale(k)); self.scale_group.addButton(b); top.addWidget(b, 1); self.scale_buttons[key] = b
        v.addLayout(top)
        self.note = QLabel(); self.note.setObjectName("muted"); self.note.setWordWrap(True); v.addWidget(self.note)
        self.holder = QVBoxLayout(); v.addLayout(self.holder)
        body = QHBoxLayout(); body.setSpacing(16)
        self.picture = Illustration("world-earth", 16); self.picture.setMinimumSize(260, 160); body.addWidget(self.picture, 2)
        card = QFrame(); card.setObjectName("factcard"); cv = QVBoxLayout(card); cv.setContentsMargins(16, 12, 16, 12); cv.setSpacing(6)
        self.when = QLabel(); self.when.setObjectName("rowwhen"); cv.addWidget(self.when)
        self.title = QLabel(); self.title.setObjectName("quizquestion"); self.title.setWordWrap(True); cv.addWidget(self.title)
        self.text = QLabel(); self.text.setWordWrap(True); cv.addWidget(self.text)
        self.source = QLabel(); self.source.setObjectName("cardcaption"); self.source.setWordWrap(True); self.source.setTextFormat(Qt.RichText); self.source.linkActivated.connect(window.open_web); cv.addWidget(self.source)
        cv.addStretch(); body.addWidget(card, 3); v.addLayout(body, 1)
        keys = QLabel(T(UI["keys"], lang)); keys.setObjectName("cardcaption"); v.addWidget(keys)
        self.canvas = None; self.set_scale("geo")
    def set_scale(self, key):
        self.scale = key; self.scale_buttons[key].setChecked(True); lang = self.lang
        if self.canvas is not None: self.holder.removeWidget(self.canvas); self.canvas.hide(); self.canvas.deleteLater()
        if key == "geo":
            self.events = GEO
            # Stretched (logarithmic) scale: 4,540 Ma on the left, 0.3 Ma on the right.
            lo, hi = math.log10(0.3), math.log10(4540)
            positions = [1 - (math.log10(age) - lo) / (hi - lo) for age, *_ in GEO]
            names = [f"{label} · {T(title, lang)}" for _, label, title, _, _ in GEO]
            self.note.setText(T(UI["geo_note"], lang))
        else:
            self.events = HUMAN
            lo, hi = math.log10(23), math.log10(300000)
            positions = [1 - (math.log10(-ago) - lo) / (hi - lo) for ago, *_ in HUMAN]
            names = [f"{T(label, lang)} · {T(title, lang)}" for _, label, title, _, _ in HUMAN]
            self.note.setText(T(UI["human_note"], lang))
        self.canvas = TimelineCanvas(positions, None); self.canvas.set_names(names); self.canvas.selected.connect(self.show_event); self.holder.addWidget(self.canvas)
        self.canvas.select(0)
    def show_event(self, i):
        lang = self.lang
        if self.scale == "geo":
            _, label, title, text, picture = self.events[i]; when = label; sources = GEO_SOURCES
        else:
            _, label, title, text, picture = self.events[i]; when = T(label, lang); sources = HUMAN_SOURCES
        self.when.setText(when); self.title.setText(T(title, lang)); self.text.setText(T(text, lang)); self.picture.set_name(picture)
        self.source.setText(f"{T(UI['source'], lang)}: " + " · ".join(f'<a href="{u}">{n}</a>' for n, u in sources))
        try: self.win.progress.record(f"activity:timeline_{self.scale}", i + 1, len(self.events)) if i + 1 == len(self.events) else None
        except (ValueError, OSError, AttributeError): pass

# --------------------------------------------------------------- industry
INVENTIONS = [
    (1450, L("Printing press with movable type in Europe (Gutenberg)", "Mesin cetak huruf lepas di Eropa (Gutenberg)", "Prensa de tipos móveis na Europa (Gutenberg)", "Imprensa ho letra ne'ebé bele muda iha Europa (Gutenberg)"), "c. 1450"),
    (1712, L("Newcomen's steam engine pumps water from mines", "Mesin uap Newcomen memompa air dari tambang", "A máquina a vapor de Newcomen bombeia água das minas", 'Newcomen nia mákina vapór bomba bee husi mina'), "1712"),
    (1764, L("Spinning jenny spins many threads at once", "Spinning jenny memintal banyak benang sekaligus", "A spinning jenny fia muitos fios de uma vez", 'Spinning jenny fia kabas barak dala ida'), "c. 1764"),
    (1769, L("James Watt patents his improved steam engine", "James Watt mematenkan mesin uap yang lebih baik", "James Watt patenteia a sua máquina a vapor melhorada", "James Watt rejista patente ba ninia mákina vapór ne'ebé di'ak liu"), "1769"),
    (1825, L("Stockton and Darlington Railway opens", "Jalur kereta Stockton–Darlington dibuka", "Abre a linha férrea Stockton–Darlington", "Liña kareta-ahi Stockton–Darlington loke"), "1825"),
    (1876, L("Bell patents the telephone", "Bell mematenkan telepon", "Bell patenteia o telefone", 'Bell rejista patente ba telefone'), "1876"),
]
MATCHES = [
    (L("Steam engine", "Mesin uap", "Máquina a vapor", 'Mákina vapór'), L("Pump water and drive machines", "Memompa air dan menggerakkan mesin", "Bombear água e mover máquinas", "Bomba bee no halo mákina la'o")),
    (L("Spinning jenny", "Spinning jenny", "Spinning jenny", "Spinning jenny"), L("Spin thread for cloth", "Memintal benang untuk kain", "Fiar fio para tecido", 'Fia kabas ba hena')),
    (L("Railway locomotive", "Lokomotif kereta", "Locomotiva", "Lokomotiva"), L("Carry goods and people over land", "Mengangkut barang dan orang di darat", "Transportar mercadorias e pessoas por terra", "Lori sasán no ema iha rai")),
    (L("Telegraph", "Telegraf", "Telégrafo", "Telégrafu"), L("Send messages along wires", "Mengirim pesan lewat kabel", "Enviar mensagens por fios", 'Haruka mensajen liuhusi kabu')),
    (L("Printing press", "Mesin cetak", "Prensa", 'Imprensa'), L("Make many copies of books", "Membuat banyak salinan buku", "Fazer muitas cópias de livros", "Halo kópia livru barak")),
]
IMPACTS = [
    (L("Many people moved from farms to growing cities to work in factories.", "Banyak orang pindah dari desa ke kota yang tumbuh untuk bekerja di pabrik.", "Muitas pessoas mudaram-se do campo para cidades em crescimento para trabalhar nas fábricas.", "Ema barak muda husi foho ba sidade atu servisu iha fábrika."),
     True, L("Yes. Towns grew quickly; by 1851 about half of the people in Britain lived in towns.", "Ya. Kota tumbuh cepat; pada 1851 sekitar separuh penduduk Britania tinggal di kota.", "Sim. As cidades cresceram depressa; em 1851 cerca de metade da população britânica vivia em cidades.", 'Loos. Sidade sira sai boot lalais; iha 1851, maizumenus metade husi ema iha Grã-Bretanha hela iha sidade.')),
    (L("Factory work was always safe and children never worked there.", "Pekerjaan di pabrik selalu aman dan anak-anak tidak pernah bekerja di sana.", "O trabalho nas fábricas era sempre seguro e as crianças nunca lá trabalharam.", "Servisu iha fábrika seguru nafatin no labarik sira nunka servisu iha ne'ebá."),
     False, L("No. Hours were long and dangerous, and many children worked. Laws such as Britain's Factory Act of 1833 began to limit child labour.", "Tidak. Jam kerja panjang dan berbahaya, dan banyak anak bekerja. Undang-undang seperti Factory Act 1833 di Britania mulai membatasi pekerja anak.", "Não. Os horários eram longos e perigosos e muitas crianças trabalhavam. Leis como o Factory Act de 1833 começaram a limitar o trabalho infantil.", 'Lae. Oras servisu naruk no perigozu, no labarik barak servisu. Lei hanesan Factory Act 1833 hahú limita servisu labarik nian.')),
    (L("Burning coal for steam polluted the air in industrial cities.", "Pembakaran batu bara untuk uap mencemari udara di kota industri.", "Queimar carvão para o vapor poluiu o ar das cidades industriais.", 'Sunu fatuk-karvaun ba vapór halo anin foer iha sidade industriál.'),
     True, L("Yes. Smoke and soot made air unhealthy; the same fuels also began the long rise of carbon dioxide in the air.", "Ya. Asap dan jelaga membuat udara tidak sehat; bahan bakar yang sama juga memulai kenaikan panjang karbon dioksida di udara.", "Sim. O fumo e a fuligem tornaram o ar insalubre; os mesmos combustíveis iniciaram o longo aumento do dióxido de carbono no ar.", "Loos. Suar no ahi-rahun halo anin la di'ak ba saúde; kombustível hanesan ne'e mós hahú halo dióksidu karbonu sa'e iha anin.")),
]
TRUE_FALSE = {True: L("True", "Benar", "Verdadeiro", "Loos"), False: L("False", "Salah", "Falso", "Sala")}
INDUSTRY_SOURCES = [("Britannica · Industrial Revolution", "https://www.britannica.com/event/Industrial-Revolution"), ("Science Museum, London · Steam engines", "https://www.sciencemuseum.org.uk/")]

class IndustryModule(QWidget):
    def __init__(self, window, article, parent=None):
        super().__init__(parent); self.win = window; self.lang = window.settings.locale; lang = self.lang; tok = tokens_of(window)
        v = QVBoxLayout(self); v.setContentsMargins(0, 6, 0, 6); v.setSpacing(14)
        pic = Illustration("world-industrial_revolution", 16); pic.setMinimumHeight(150); pic.setMaximumHeight(200); v.addWidget(pic)
        # 1. Order.
        box = QFrame(); box.setObjectName("factcard"); b = QVBoxLayout(box); b.setContentsMargins(16, 12, 16, 12); b.setSpacing(8)
        h = QLabel(T(UI["order_title"], lang)); h.setObjectName("cardtitle"); h.setWordWrap(True); b.addWidget(h)
        hint = QLabel(T(UI["order_keys"], lang)); hint.setObjectName("cardcaption"); hint.setWordWrap(True); b.addWidget(hint)
        row = QHBoxLayout(); self.order = QListWidget(); self.order.setObjectName("orderlist"); self.order.setDragDropMode(QAbstractItemView.InternalMove)
        self.order.setAccessibleName(T(UI["order_title"], lang)); items = list(INVENTIONS); random.Random(3).shuffle(items)
        for year, text, label in items:
            item = QListWidgetItem(T(text, lang)); item.setData(Qt.UserRole, year); item.setData(Qt.UserRole + 1, label); self.order.addItem(item)
        self.order.setMinimumHeight(6 * 34); self.order.installEventFilter(self); row.addWidget(self.order, 1)
        buttons = QVBoxLayout()
        for name, step, key in (("arrow-up", -1, "up"), ("arrow-down", 1, "down")):
            btn = QPushButton(); btn.setObjectName("iconbutton"); btn.setFixedSize(40, 40); btn.setIcon(icons.icon(name, tok["text"])); btn.setToolTip(T(UI[key], lang)); btn.setAccessibleName(T(UI[key], lang))
            btn.clicked.connect(lambda checked=False, s=step: self.move(s)); buttons.addWidget(btn)
        buttons.addStretch(); row.addLayout(buttons); b.addLayout(row)
        crow = QHBoxLayout(); check = QPushButton(T(UI["check"], lang)); check.setObjectName("primary"); check.clicked.connect(self.check_order); crow.addWidget(check)
        self.order_result = QLabel(); self.order_result.setWordWrap(True); crow.addWidget(self.order_result, 1); b.addLayout(crow)
        v.addWidget(box)
        # 2. Match.
        box = QFrame(); box.setObjectName("factcard"); b = QVBoxLayout(box); b.setContentsMargins(16, 12, 16, 12); b.setSpacing(8)
        h = QLabel(T(UI["match_tech"], lang)); h.setObjectName("cardtitle"); b.addWidget(h)
        grid = QGridLayout(); grid.setHorizontalSpacing(12); grid.setVerticalSpacing(6); self.match = []
        uses = [T(use, lang) for _, use in MATCHES]; shuffled = list(uses); random.Random(5).shuffle(shuffled)
        for i, (tech, use) in enumerate(MATCHES):
            combo = QComboBox(); combo.addItem(T(UI["choose"], lang), "")
            for u in shuffled: combo.addItem(u, u)
            combo.setAccessibleName(T(tech, lang)); name = QLabel(T(tech, lang)); name.setObjectName("rowtitle")
            grid.addWidget(name, i, 0); grid.addWidget(combo, i, 1); self.match.append((combo, T(use, lang)))
        grid.setColumnStretch(1, 1); b.addLayout(grid)
        crow = QHBoxLayout(); check = QPushButton(T(UI["check"], lang)); check.setObjectName("primary"); check.clicked.connect(self.check_match); crow.addWidget(check)
        self.match_result = QLabel(); self.match_result.setWordWrap(True); crow.addWidget(self.match_result, 1); b.addLayout(crow)
        v.addWidget(box)
        # 3. Impact.
        box = QFrame(); box.setObjectName("factcard"); b = QVBoxLayout(box); b.setContentsMargins(16, 12, 16, 12); b.setSpacing(8)
        h = QLabel(T(UI["impact_title"], lang)); h.setObjectName("cardtitle"); b.addWidget(h)
        self.impact_feedback = []; self.impact_score = {}
        for i, (statement, truth, why) in enumerate(IMPACTS):
            line = QLabel(f"{i + 1}. {T(statement, lang)}"); line.setWordWrap(True); b.addWidget(line)
            r = QHBoxLayout()
            for value in (True, False):
                btn = QPushButton(T(TRUE_FALSE[value], lang)); btn.setObjectName("answer"); btn.clicked.connect(lambda checked=False, i=i, value=value: self.answer_impact(i, value)); r.addWidget(btn)
            r.addStretch(); b.addLayout(r)
            fb = QLabel(); fb.setWordWrap(True); fb.setObjectName("feedback"); b.addWidget(fb); self.impact_feedback.append(fb)
        src = QLabel(f"{T(UI['source'], lang)}: " + " · ".join(f'<a href="{u}">{n}</a>' for n, u in INDUSTRY_SOURCES)); src.setObjectName("cardcaption"); src.setWordWrap(True)
        src.setTextFormat(Qt.RichText); src.linkActivated.connect(window.open_web); b.addWidget(src)
        v.addWidget(box); v.addStretch(1)
    def eventFilter(self, obj, event):
        from .qt import QEvent
        if obj is self.order and event.type() == QEvent.KeyPress and event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Up: self.move(-1); return True
            if event.key() == Qt.Key_Down: self.move(1); return True
        return super().eventFilter(obj, event)
    def move(self, step):
        row = self.order.currentRow()
        if row < 0: row = 0; self.order.setCurrentRow(0)
        target = row + step
        if 0 <= target < self.order.count():
            item = self.order.takeItem(row); self.order.insertItem(target, item); self.order.setCurrentRow(target)
    def check_order(self):
        years = [self.order.item(i).data(Qt.UserRole) for i in range(self.order.count())]
        correct = sorted(years); score = sum(1 for a, b in zip(years, correct) if a == b)
        for i in range(self.order.count()):
            item = self.order.item(i); label = item.data(Qt.UserRole + 1); text = item.text().split("  ·  ")[0]
            item.setText(f"{text}  ·  {label}" + ("  ✓" if years[i] == correct[i] else "  ✗"))
        self.order_result.setText(T(UI["result"], self.lang).format(s=score, n=len(years)))
        try: self.win.progress.record("activity:inventions_order", score, len(years))
        except (ValueError, OSError, AttributeError): pass
    def check_match(self):
        score = sum(1 for combo, answer in self.match if combo.currentData() == answer)
        for combo, answer in self.match: combo.setProperty("state", "right" if combo.currentData() == answer else "wrong"); combo.style().unpolish(combo); combo.style().polish(combo)
        self.match_result.setText(T(UI["result"], self.lang).format(s=score, n=len(self.match)))
        try: self.win.progress.record("activity:technology_match", score, len(self.match))
        except (ValueError, OSError, AttributeError): pass
    def answer_impact(self, i, value):
        statement, truth, why = IMPACTS[i]; ok = value == truth; self.impact_score[i] = ok
        self.impact_feedback[i].setText((T(UI["right"], self.lang) if ok else T(UI["wrong"], self.lang)) + " " + T(why, self.lang))
        if len(self.impact_score) == len(IMPACTS):
            try: self.win.progress.record("activity:factory_impact", sum(self.impact_score.values()), len(IMPACTS))
            except (ValueError, OSError, AttributeError): pass

MODULES = {"dinosaurs": DinosaurModule, "earth_history": TimelineModule, "industry": IndustryModule}

def create(key, window, article):
    cls = MODULES.get(key)
    return cls(window, article) if cls else None
