"""Símbolu Nasionál: the national anthem «Pátria» with lyrics that follow the
music (karaoke), the flag (Constitution art. 15) and the emblem (Lei n.º 2/2007)
explained part by part, with links to the articles and the Constitution."""
import html

from ...qt import (Qt, QTimer, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPainter, QColor, QFont, QFontMetrics, QRectF, QPointF,
                  QLinearGradient, QCheckBox, QPixmap, QPen, QSize, QSizePolicy, Signal)
from ...icons import ASSETS
from ... import kb, icons
from ...anthem import load as load_anthem, at, next_time, clock
from ...audio import Player
from ...constitution import load as load_constitution
from ..texts import extend
from ..widgets import Card, Clickable, ClayIcon, Pill, Banner, ResponsiveGrid, label, button, scroll, section_title, clear_layout, tok_of, clip

extend({
    "sym_title": ("Símbolu Nasionál", "Símbolos Nacionais", "National Symbols", "Simbol Nasional"),
    "sym_sub": ("Bandeira, emblema no inu nasionál — Konstituisaun artigu 14 no 15, Lei n.º 2/2007.", "Bandeira, emblema e hino nacional — Constituição, artigos 14.º e 15.º, Lei n.º 2/2007.", "Flag, emblem and national anthem — Constitution, articles 14 and 15, Law no. 2/2007.", "Bendera, lambang dan lagu kebangsaan — Konstitusi, pasal 14 dan 15, Undang-Undang No. 2/2007."),
    "anthem_credits": ("Múzika: {music} · Letra: {lyrics}", "Música: {music} · Letra: {lyrics}", "Music: {music} · Words: {lyrics}", "Musik: {music} · Lirik: {lyrics}"),
    "anthem_play": ("Rona inu", "Ouvir o hino", "Play the anthem", "Putar lagu kebangsaan"),
    "anthem_pause": ("Para", "Pausa", "Pause", "Jeda"),
    "anthem_restart": ("Hahú fali", "Recomeçar", "Start again", "Mulai lagi"),
    "anthem_repeat": ("Repete", "Repetir", "Repeat", "Ulangi"),
    "anthem_translation": ("Hatudu tradusaun Tetun", "Mostrar a tradução em tétum", "Show the translation", "Tampilkan terjemahan"),
    "anthem_intro": ("♪ Múzika introdusaun", "♪ Introdução musical", "♪ Musical introduction", "♪ Pembukaan musik"),
    "anthem_interlude": ("♪ Interlúdiu múzika", "♪ Interlúdio musical", "♪ Musical interlude", "♪ Selingan musik"),
    "anthem_outro": ("♪ Final", "♪ Final", "♪ Ending", "♪ Penutup"),
    "anthem_ready": ("Prima «Rona inu» no hananu hamutuk", "Prima «Ouvir o hino» e cante connosco", "Press «Play the anthem» and sing along", "Tekan «Putar lagu kebangsaan» dan bernyanyilah bersama"),
    "anthem_refrain": ("Refraun", "Refrão", "Refrain", "Refrein"),
    "anthem_verse": ("Estrofe", "Estrofe", "Verse", "Bait"),
    "anthem_lyrics": ("Letra kompletu", "Letra completa", "Full lyrics", "Lirik lengkap"),
    "anthem_no_audio": ("Atu rona inu, instala «python3-pyqt5.qtmultimedia», «libqt5multimedia5-plugins» no «gstreamer1.0-plugins-good» (ka ffmpeg / mpg123). Letra iha okos.", "Para ouvir o hino, instale «python3-pyqt5.qtmultimedia», «libqt5multimedia5-plugins» e «gstreamer1.0-plugins-good» (ou ffmpeg / mpg123). A letra está abaixo.", "To hear the anthem, install «python3-pyqt5.qtmultimedia», «libqt5multimedia5-plugins» and «gstreamer1.0-plugins-good» (or ffmpeg / mpg123). The lyrics are below.", "Untuk mendengar lagu kebangsaan, pasang «python3-pyqt5.qtmultimedia», «libqt5multimedia5-plugins» dan «gstreamer1.0-plugins-good» (atau ffmpeg / mpg123). Liriknya ada di bawah."),
    "anthem_failed": ("La bele toka audio iha komputadór ida-ne'e.", "Não foi possível tocar o áudio neste computador.", "The audio could not be played on this computer.", "Audio tidak dapat diputar di komputer ini."),
    "anthem_respect": ("Bainhira inu toka: hamriik, nonook no haree ba bandeira.", "Quando o hino toca: de pé, em silêncio, a olhar para a bandeira.", "When the anthem plays: stand up, keep silent and look at the flag.", "Saat lagu kebangsaan diputar: berdiri, diam dan pandanglah bendera."),
    "sym_flag": ("Bandeira Nasionál", "Bandeira Nacional", "National Flag", "Bendera Nasional"),
    "sym_flag_text": ("Konstituisaun artigu 15 deskreve bandeira no nia kór sira:", "O artigo 15.º da Constituição descreve a bandeira e as suas cores:", "Article 15 of the Constitution describes the flag and its colours:", "Pasal 15 Konstitusi menjelaskan bendera dan warnanya:"),
    "sym_emblem": ("Emblema Nasionál (Belak)", "Emblema Nacional (Belak)", "National Emblem", "Lambang Negara"),
    "sym_emblem_note": ("Imajen ofisiál emblema RDTL nian. Esplikasaun tuir Governu Timór-Leste (timor-leste.gov.tl › Símbolu Nasionál).", "Imagem oficial do emblema da RDTL. Explicação segundo o Governo de Timor-Leste (timor-leste.gov.tl › Símbolos Nacionais).", "The official emblem of the RDTL. Explanation after the Government of Timor-Leste (timor-leste.gov.tl › National Symbols).", "Lambang resmi RDTL. Penjelasan menurut Pemerintah Timor-Leste (timor-leste.gov.tl › Simbol Nasional)."),
    "sym_emblem_hint": ("Klik iha númeru ida iha emblema ka iha lista atu hatene parte ida-idak.", "Clique num número do emblema ou na lista para conhecer cada parte.", "Click a number on the emblem or a row in the list to learn about each part.", "Klik nomor pada lambang atau baris di daftar untuk mengenal setiap bagian."),
    "sym_colours": ("Kór sira iha emblema: mutin = dame · kinur = riku-soin · metan = nakukun atu halakon · mean = domin ba pátria no luta libertasaun.", "Cores do emblema: branco = paz · amarelo = riqueza · preto = obscurantismo a vencer · vermelho = amor à pátria e luta de libertação.", "Colours of the emblem: white = peace · yellow = wealth · black = obscurantism to be overcome · red = love of the homeland and the liberation struggle.", "Warna lambang: putih = perdamaian · kuning = kekayaan · hitam = kebodohan yang harus diatasi · merah = cinta tanah air dan perjuangan pembebasan."),
    "sym_read_article": ("Lee artigu kompletu", "Ler o artigo completo", "Read the full article", "Baca artikel lengkap"),
    "sym_constitution": ("Konstituisaun art. {n}", "Constituição art. {n}", "Constitution art. {n}", "Konstitusi pasal {n}"),
    "sym_more": ("Símbolu no identidade seluk", "Outros símbolos e identidade", "Other symbols and identity", "Simbol dan identitas lainnya"),
    "recording_credit": ("Gravasaun", "Gravação", "Recording", "Rekaman"),
})

# The emblem part by part, after the official description of the Government of
# Timor-Leste (timor-leste.gov.tl, "Símbolos Nacionais"): (marker x, y on the
# image 0–1), name and meaning in (tet, pt, en, id).
EMBLEM_PARTS = [
    ((0.155, 0.155), ("Belak (sírkulu)", "Belak (o círculo)", "Belak (the circle)", "Belak (lingkaran)"),
     ("Emblema nia naran mak Belak. Sírkulu reprezenta mundu kabuar ne'ebé Timór-Leste mós iha laran, no nu'udar sinál unidade nasionál. Iha ninin hakerek «República Democrática de Timor-Leste» no «RDTL».",
      "O emblema chama-se Belak. O círculo representa o globo terrestre, onde se inclui Timor-Leste, e é o símbolo da unidade nacional. À volta lê-se «República Democrática de Timor-Leste» e «RDTL».",
      "The emblem is called Belak. The circle stands for the globe, which includes Timor-Leste, and is the symbol of national unity. Around it you read «República Democrática de Timor-Leste» and «RDTL».",
      "Lambang ini bernama Belak. Lingkarannya melambangkan bola dunia tempat Timor-Leste berada dan menjadi simbol persatuan nasional. Di tepinya tertulis «República Democrática de Timor-Leste» dan «RDTL».")),
    ((0.27, 0.47), ("Insígnia Foho Ramelau", "Insígnia do Monte Ramelau", "Mount Ramelau insignia", "Lambang Gunung Ramelau"),
     ("Iha klaran iha forma Foho Ramelau (Tatamailau), foho aas liu iha rai: ninin mean-rubí, klaran metan no liña kinur-osan ida hadulas klaran.",
      "No centro está a insígnia do Monte Ramelau (Tatamailau), a montanha mais alta do país: periferia vermelho-rubi, centro preto e uma linha amarelo-dourada à volta do centro.",
      "In the centre is the insignia of Mount Ramelau (Tatamailau), the country's highest mountain: a ruby-red outer part, a black centre and a golden-yellow line around the centre.",
      "Di tengah ada lambang Gunung Ramelau (Tatamailau), gunung tertinggi di negeri ini: bagian luar merah delima, bagian tengah hitam dan garis kuning keemasan di sekeliling bagian tengah.")),
    ((0.5, 0.135), ("Ángulu haat", "Os quatro ângulos", "The four angles", "Empat sudut"),
     ("Ángulu haat insígnia Ramelau nian simboliza separasaun podér no relasaun entre órgaun soberania Estadu nian (Konstituisaun artigu 67): Prezidente Repúblika, Parlamentu Nasionál, Governu no Tribunál sira.",
      "Os quatro ângulos da insígnia do Ramelau simbolizam a separação de poderes e a interdependência dos órgãos de soberania do Estado (Constituição, artigo 67.º): Presidente da República, Parlamento Nacional, Governo e Tribunais.",
      "The four angles of the Ramelau insignia stand for the separation of powers and the interdependence of the organs of sovereignty (Constitution, article 67): the President of the Republic, the National Parliament, the Government and the courts.",
      "Empat sudut lambang Ramelau melambangkan pemisahan kekuasaan dan saling ketergantungan lembaga-lembaga kedaulatan negara (Konstitusi, pasal 67): Presiden Republik, Parlemen Nasional, Pemerintah dan pengadilan.")),
    ((0.545, 0.232), ("Fitun mutin", "Estrela branca", "White star", "Bintang putih"),
     ("Fitun ho rohan lima: naroman laran-luak no laran-moos nian ne'ebé hatudu dalan ba povu to'o dame.",
      "Estrela de cinco pontas: a luz da generosidade e da honestidade que guia o povo para a paz.",
      "A five-pointed star: the light of generosity and honesty that guides the people towards peace.",
      "Bintang berujung lima: cahaya kemurahan hati dan kejujuran yang menuntun rakyat menuju perdamaian.")),
    ((0.445, 0.285), ("Naroman mutin", "Raios brancos", "White rays", "Sinar putih"),
     ("Naroman fitun nian: solidariedade no determinasaun atu lori dame ba mundu tomak. Kór mutin iha emblema simboliza dame.",
      "Os raios da estrela: a luz da solidariedade e a determinação de levar a paz a todo o mundo. O branco do emblema simboliza a paz.",
      "The star's rays: the light of solidarity and the determination to bring peace to the whole world. White in the emblem means peace.",
      "Sinar bintang: cahaya solidaritas dan tekad membawa perdamaian ke seluruh dunia. Warna putih pada lambang berarti perdamaian.")),
    ((0.50, 0.352), ("Livru loke", "Livro aberto", "Open book", "Buku terbuka"),
     ("Livru, roda-dente, batar no hare hamutuk: matenek no kbiit povu nian atu dezenvolve edukasaun, kultura, justisa sosiál, agrikultura no indústria. Letra metan livru nian mak nakukun ne'ebé tenke halakon.",
      "O livro, a roda dentada, o milho e o arroz juntos: a sabedoria e a capacidade do povo para desenvolver a educação, a cultura, a justiça social, a agricultura e a indústria. As letras pretas do livro são o obscurantismo a vencer.",
      "The book, the toothed wheel, the maize and the rice together: the wisdom and ability of the people to develop education, culture, social justice, farming and industry. The book's black letters are the obscurantism to be overcome.",
      "Buku, roda gigi, jagung dan padi bersama-sama: kebijaksanaan dan kemampuan rakyat untuk memajukan pendidikan, budaya, keadilan sosial, pertanian dan industri. Huruf hitam pada buku adalah kebodohan yang harus diatasi.")),
    ((0.572, 0.428), ("Roda-dente", "Roda dentada", "Toothed wheel", "Roda gigi"),
     ("Indústria no servisu. Ninia kór kinur simboliza riku-soin.",
      "A indústria e o trabalho. O seu amarelo simboliza a riqueza.",
      "Industry and work. Its yellow colour stands for wealth.",
      "Industri dan kerja. Warna kuningnya melambangkan kekayaan.")),
    ((0.38, 0.375), ("Batar fulin", "Batar fulin (espiga de milho)", "Batar fulin (maize cob)", "Batar fulin (tongkol jagung)"),
     ("Batar, ai-han prinsipál ida: agrikultura no riku-soin rai nian.",
      "O milho, um dos alimentos principais: a agricultura e a riqueza da terra.",
      "Maize, one of the main foods: farming and the wealth of the land.",
      "Jagung, salah satu makanan pokok: pertanian dan kekayaan tanah.")),
    ((0.62, 0.370), ("Háre fulin", "Háre fulin (espiga de arroz)", "Háre fulin (ear of rice)", "Háre fulin (bulir padi)"),
     ("Hare: agrikultura no ai-han ba povu tomak.",
      "O arroz: a agricultura e o alimento de todo o povo.",
      "Rice: farming and food for the whole people.",
      "Padi: pertanian dan pangan bagi seluruh rakyat.")),
    ((0.50, 0.516), ("Kilat automátiku", "Espingarda automática", "Automatic rifle", "Senapan otomatis"),
     ("Kilat (modelu AK-47/Galaxi), diman no rama-inan hamutuk: luta rezisténsia povu nian iha sékulu barak ba libertasaun nasionál, no autodefeza ba onra no dignidade soberania Estadu nian. Kilat nia kór metan mak nakukun ne'ebé tenke halakon.",
      "A espingarda (modelo AK-47/Galaxi), a flecha e o arco juntos: os séculos de luta de resistência do povo pela libertação nacional e a autodefesa pela honra e dignidade da soberania do Estado. O preto da espingarda é o obscurantismo a vencer.",
      "The rifle (AK-47/Galaxi model), the arrow and the bow together: the people's centuries of resistance for national liberation and self-defence for the honour and dignity of the State's sovereignty. The rifle's black is the obscurantism to be overcome.",
      "Senapan (model AK-47/Galaxi), anak panah dan busur bersama-sama: perjuangan perlawanan rakyat selama berabad-abad demi pembebasan nasional dan pertahanan diri demi kehormatan dan martabat kedaulatan negara. Warna hitam senapan adalah kebodohan yang harus diatasi.")),
    ((0.37, 0.472), ("Diman", "Diman (flecha)", "Diman (arrow)", "Diman (anak panah)"),
     ("Diman, arma tradisionál: rezisténsia povu nian iha sékulu barak nia laran. Ninia kór kinur simboliza riku-soin.",
      "O diman, arma tradicional: os séculos de resistência do povo. O seu amarelo simboliza a riqueza.",
      "The diman, a traditional weapon: the people's centuries of resistance. Its yellow colour stands for wealth.",
      "Diman, senjata tradisional: perlawanan rakyat selama berabad-abad. Warna kuningnya melambangkan kekayaan.")),
    ((0.50, 0.597), ("Rama-inan", "Rama-inan (arco)", "Rama-inan (bow)", "Rama-inan (busur)"),
     ("Rama-inan, arma tradisionál hamutuk ho diman: tradisaun no rezisténsia povu nian. Ninia kór kinur simboliza riku-soin.",
      "O rama-inan, arma tradicional com o diman: a tradição e a resistência do povo. O seu amarelo simboliza a riqueza.",
      "The rama-inan, a traditional weapon used with the diman: the tradition and resistance of the people. Its yellow colour stands for wealth.",
      "Rama-inan, senjata tradisional bersama diman: tradisi dan perlawanan rakyat. Warna kuningnya melambangkan kekayaan.")),
    ((0.50, 0.737), ("Lema", "Lema", "Motto", "Semboyan"),
     ("«Unidade, Acção, Progresso» (Unidade, Asaun, Progresu): valór báziku polítika no morál nian ne'ebé hatuur moris nasaun no povu nian.",
      "«Unidade, Acção, Progresso»: os valores básicos da política e da moral em que assenta a vida da nação e do povo.",
      "«Unidade, Acção, Progresso» (Unity, Action, Progress): the basic political and moral values on which the life of the nation and the people rests.",
      "«Unidade, Acção, Progresso» (Persatuan, Tindakan, Kemajuan): nilai-nilai dasar politik dan moral yang menjadi landasan kehidupan bangsa dan rakyat.")),
]
EMBLEM_IMAGE = ASSETS / "timor" / "symbols" / "emblem.png"

class EmblemView(QWidget):
    """The official emblem with numbered markers; hover or click a marker to pick that part."""
    picked = Signal(int)
    def __init__(self, parts, parent=None):
        super().__init__(parent); self.parts = parts; self.selected = -1; self.hover = -1
        self.image = QPixmap(str(EMBLEM_IMAGE)); self._scaled = None
        self.setMouseTracking(True); self.setMinimumSize(240, 240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    MAX_SIDE = 460             # the explanation under the picture stays on screen at 1366x768
    def hasHeightForWidth(self): return True
    def heightForWidth(self, width): return min(width, self.MAX_SIDE)
    def sizeHint(self): return QSize(400, 400)
    def square(self):
        side = min(self.width(), self.height()); return QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)
    def radius(self): return max(9.0, self.square().width() * 0.024)
    def centre(self, i):
        r = self.square(); x, y = self.parts[i][0]; return QPointF(r.x() + x * r.width(), r.y() + y * r.height())
    def marker_at(self, pos):
        best, best_d = -1, (self.radius() * 1.5) ** 2
        for i in range(len(self.parts)):
            c = self.centre(i); d = (c.x() - pos.x()) ** 2 + (c.y() - pos.y()) ** 2
            if d <= best_d: best, best_d = i, d
        return best
    def set_selected(self, i):
        if i != self.selected: self.selected = i; self.update()
    def mouseMoveEvent(self, e):
        i = self.marker_at(e.pos())
        if i != self.hover:
            self.hover = i; self.setCursor(Qt.PointingHandCursor if i >= 0 else Qt.ArrowCursor); self.update()
    def leaveEvent(self, e):
        self.hover = -1; self.update(); super().leaveEvent(e)
    def mousePressEvent(self, e):
        i = self.marker_at(e.pos())
        if i >= 0: self.set_selected(i); self.picked.emit(i)
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
        r = self.square(); side = int(r.width())
        if self.image.isNull():
            p.drawText(self.rect(), Qt.AlignCenter, "Belak"); return
        if self._scaled is None or self._scaled.width() != side:
            self._scaled = self.image.scaled(side, side, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        p.drawPixmap(int(r.x()), int(r.y()), self._scaled)
        tok = tok_of(self); primary = QColor(tok.get("primary", "#6d4aff")); rad = self.radius()
        font = QFont(self.font()); font.setBold(True); font.setPixelSize(max(9, int(rad * 1.05))); p.setFont(font)
        for i in range(len(self.parts)):
            c = self.centre(i); active = i in (self.selected, self.hover)
            if active:
                halo = QColor(primary); halo.setAlpha(70); p.setPen(Qt.NoPen); p.setBrush(halo); p.drawEllipse(c, rad * 1.8, rad * 1.8)
            fill = QColor(primary) if active else QColor(31, 26, 61, 215)
            p.setBrush(fill); p.setPen(QPen(QColor("white"), 2)); p.drawEllipse(c, rad * (1.15 if active else 1.0), rad * (1.15 if active else 1.0))
            p.setPen(QColor("white")); p.drawText(QRectF(c.x() - rad, c.y() - rad, rad * 2, rad * 2), Qt.AlignCenter, str(i + 1))
        p.end()

def translation_lang(lang):
    """The language of the translation under the official Portuguese words: Tetun for Portuguese readers."""
    return "tet" if lang in ("pt", "tet") else lang

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
        self.scroll_area = scroll(self.body); outer.addWidget(self.scroll_area); self.render()
    def show_route(self, params):
        if params.get("play") and self.player.available and self.player.state != "playing": self.player.play()
    def hideEvent(self, e):
        super().hideEvent(e)
        player = getattr(self, "player", None)      # gone already when a window is destroyed at exit
        if player is not None and player.state == "playing": player.pause()
    # ------------------------------------------------------------------ ui
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; self.line_rows = {}
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
        self.col.addWidget(self.emblem_card()); self.col.addWidget(self.flag_card())
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
        opts = QHBoxLayout(); self.show_tet = QCheckBox(t("anthem_translation")); self.show_tet.setChecked(lang != "pt"); self.show_tet.toggled.connect(lambda _=None: self.on_position(self.player.position()))
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
                tr_lang = translation_lang(lang)
                if line.get(tr_lang): rl.addWidget(label(kb.show(line[tr_lang], tr_lang), "caption", wrap=True))
                r.box.addLayout(rl); r.clicked.connect(lambda i=i: self.jump_to(i)); pc.box.addWidget(r); self.line_rows[i] = r
            pc.box.addStretch(); lyr.add(pc)
        card.box.addWidget(lyr)
        card.box.addWidget(label(kb.text(data.get("note"), lang), "caption", wrap=True))
        if data.get("translations"): card.box.addWidget(label(kb.text(data.get("translations"), lang), "caption", wrap=True))
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
        grid = ResponsiveGrid(340, 2, 18)
        left = QWidget(); lc = QVBoxLayout(left); lc.setContentsMargins(0, 0, 0, 0); lc.setSpacing(10)
        self.emblem_view = EmblemView(EMBLEM_PARTS); lc.addWidget(self.emblem_view)
        # The part chosen on the picture is explained right under it (no scrolling needed).
        self.emblem_detail = label(t("sym_emblem_hint"), wrap=True)
        self.emblem_detail.setStyleSheet(f"background:{win.tok['primary_soft']}; border-radius:14px; padding:10px 14px;"); lc.addWidget(self.emblem_detail)
        lc.addWidget(label(t("sym_colours"), "caption", wrap=True)); lc.addWidget(label(t("sym_emblem_note"), "caption", wrap=True)); lc.addStretch()
        grid.add(left)
        right = QWidget(); rc = QVBoxLayout(right); rc.setContentsMargins(0, 0, 0, 0); rc.setSpacing(6); self.emblem_rows = []
        for n, (_pos, name, meaning) in enumerate(EMBLEM_PARTS):
            row = Clickable(10, 16); h = QHBoxLayout(); h.setSpacing(10)
            badge = label(str(n + 1), "h3"); badge.setFixedSize(26, 26); badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(f"background:{win.tok['primary']}; color:white; border-radius:13px;")
            h.addWidget(badge, 0, Qt.AlignTop)
            text = QVBoxLayout(); text.setSpacing(2)
            text.addWidget(label(kb.show(kb.pick(name, lang), lang), "h3", wrap=True))
            text.addWidget(label(kb.show(kb.pick(meaning, lang), lang), "caption", wrap=True))
            h.addLayout(text, 1); row.box.addLayout(h)
            row.clicked.connect(lambda i=n: self.pick_emblem_part(i)); rc.addWidget(row); self.emblem_rows.append(row)
        rc.addStretch(); grid.add(right); card.box.addWidget(grid)
        self.emblem_view.picked.connect(lambda i: self.pick_emblem_part(i, from_picture=True))
        buttons = QHBoxLayout(); buttons.addWidget(button(t("sym_read_article"), lambda: win.open_item("tl.symbols.emblem"), "ghost", "book-open"))
        buttons.addWidget(button(t("sym_constitution", n=14), lambda: win.open("constitution", article=14), "ghost", "scales")); buttons.addStretch(); card.box.addLayout(buttons)
        return card
    def pick_emblem_part(self, i, from_picture=False):
        self.emblem_view.set_selected(i)
        for n, row in enumerate(self.emblem_rows): row.set_selected(n == i)
        if 0 <= i < len(EMBLEM_PARTS):
            lang = self.win.lang; _pos, name, meaning = EMBLEM_PARTS[i]
            self.emblem_detail.setText(f"<b>{i + 1}. {html.escape(kb.show(kb.pick(name, lang), lang))}</b><br>{html.escape(kb.show(kb.pick(meaning, lang), lang))}")
            # A number clicked on the picture: scroll just enough to show its explanation. (A row of the
            # list already shows the whole text, so a click there does not move the page.)
            if from_picture: QTimer.singleShot(0, self.show_emblem_detail)       # after the new text is laid out
    def show_emblem_detail(self):
        try: self.scroll_area.ensureWidgetVisible(self.emblem_detail, 0, 16)
        except RuntimeError: pass        # the page was rebuilt meanwhile (new language or theme)
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
        tr_lang = translation_lang(lang)
        if line is None:
            self.karaoke.set_line(t({"intro": "anthem_intro", "interlude": "anthem_interlude", "outro": "anthem_outro"}.get(section, "anthem_ready")) if section or seconds == 0 else "", 0.0)
            # Show the line that comes next, so singers are ready.
            upcoming = next((i for start, _end, i in data.get("cues", []) if start >= seconds), None)
            self.section_label.setText(""); self.prev_line.setText("")
            self.next_line.setText(lines[upcoming]["pt"] if upcoming is not None and upcoming < len(lines) and section != "outro" else "")
            self.translation.setText("")
        else:
            self.section_label.setText(t("anthem_refrain" if lines[line].get("part") == "refrain" else "anthem_verse").upper())
            self.karaoke.set_line(lines[line]["pt"], progress)
            self.translation.setText(kb.show(lines[line].get(tr_lang, ""), tr_lang) if self.show_tet.isChecked() else "")
            self.prev_line.setText(lines[line - 1]["pt"] if line > 0 else "")
            self.next_line.setText(lines[line + 1]["pt"] if line + 1 < len(lines) else "")
        if line != self.current_line:
            tok = self.win.tok
            for i, row in self.line_rows.items(): row.tint = tok["primary_soft"] if i == line else None; row.update()
            self.current_line = line
    def retranslate(self): self.render()
