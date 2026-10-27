"""Lafa Virtual Assistant — a Timor-Leste guide, study buddy and computer helper.

Lafa stands on the Eduka-Panel (X11) or in a screen corner, walks now and then
and does small activities (reading, studying, the tebe dance…). It helps by:

* sharing knowledge often but politely (tips.py): holidays coming up, this
  day in history, facts, a Tetun word, a mini quiz to answer in the balloon,
  a place to visit, words to review, the next article for the school level;
* answering questions offline: the popup searches the encyclopedia and the
  vocabulary and opens Lafa Desktop on the result;
* opening the right page of Lafa Desktop (quick tiles) and, as a computer
  helper, safe applications from a fixed list (files, browser, settings…).

Quiet mode, the hourly limit and full-screen apps stop spontaneous messages.
Nothing is sent anywhere; no artificial intelligence is used.
"""
import math
import random
import shutil
import time
from datetime import datetime

from .qt import (Qt, QTimer, QPointF, QRectF, QRect, QEvent, Signal, QColor, QPainter, QPainterPath, QPen, QGuiApplication, QApplication,
                 QWidget, QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QMenu, QSize, QProcess, global_point)
from . import kb, eduka, outfits, icons, actions
from .tips import TipChooser, Tip, welcome
from .desk import theme
from .desk.texts import t as tr_text, extend
from .desk.widgets import Card, ClayIcon, SearchBox, label, button, tok_of, clear_layout, clip
from .mascot import Character

extend({
    "va_hello": ("{greet}, {name}!", "{greet}, {name}!", "{greet}, {name}!", "{greet}, {name}!"),
    "va_role": ("Ita-nia gia Timór-Leste no kolega estudu", "O seu guia de Timor-Leste e colega de estudo", "Pemandu Timor-Leste dan teman belajarmu", "Your Timor-Leste guide and study buddy"),
    "va_ask": ("Husu Lafa: artigu, fatin, liafuan…", "Pergunte ao Lafa: artigos, lugares, palavras…", "Tanya Lafa: artikel, tempat, kata…", "Ask Lafa: articles, places, words…"),
    "va_more_tips": ("Seluk", "Outra", "Lainnya", "Another"),
    "va_open_desktop": ("Loke Lafa Desktop", "Abrir o Lafa Desktop", "Buka Lafa Desktop", "Open Lafa Desktop"),
    "va_quiet": ("Modu kalma", "Modo calmo", "Mode tenang", "Quiet mode"),
    "va_read": ("Lee ho lian", "Ler em voz alta", "Bacakan", "Read aloud"),
    "va_settings": ("Lafa-Configuration", "Lafa-Configuration", "Lafa-Configuration", "Lafa-Configuration"),
    "va_tile_continue": ("Kontinua", "Continuar", "Lanjutkan", "Continue"),
    "va_tile_quiz": ("Kuis", "Quiz", "Kuis", "Quiz"),
    "va_tile_words": ("Liafuan", "Palavras", "Kata", "Words"),
    "va_tile_map": ("Mapa", "Mapa", "Peta", "Map"),
    "va_tile_calendar": ("Kalendáriu", "Calendário", "Kalender", "Calendar"),
    "va_tile_pc": ("Ajuda PC", "Ajuda PC", "Bantuan PC", "PC help"),
    "va_no_results": ("Lafa la hetan. Koko liafuan seluk ka loke Lafa Desktop.", "O Lafa não encontrou. Tente outras palavras ou abra o Lafa Desktop.", "Lafa tidak menemukan. Coba kata lain atau buka Lafa Desktop.", "Lafa found nothing. Try other words or open Lafa Desktop."),
    "va_see_all": ("Haree rezultadu hotu", "Ver todos os resultados", "Lihat semua hasil", "See all results"),
    "va_right": ("Loos! ", "Certo! ", "Benar! ", "Right! "),
    "va_wrong": ("La loos. Resposta: {a}. ", "Errado. Resposta: {a}. ", "Salah. Jawaban: {a}. ", "Not quite. Answer: {a}. "),
    "va_hover": ("Klik ha'u! Ha'u bele hatudu buat foun kona-ba Timór-Leste.", "Clique em mim! Posso mostrar algo novo sobre Timor-Leste.", "Klik saya! Saya bisa menunjukkan hal baru tentang Timor-Leste.", "Click me! I can show you something new about Timor-Leste."),
    "va_pc_apps": ("Loke aplikasaun", "Abrir aplicação", "Buka aplikasi", "Open an app"),
    "va_pc_missing": ("Aplikasaun ne'e la iha iha komputadór ne'e.", "Esta aplicação não está instalada.", "Aplikasi ini tidak terpasang.", "This app is not installed."),
    "va_outfit": ("Hatais", "Roupa", "Pakaian", "Outfit"),
    "va_pause": ("Para movimentu", "Pausa", "Jeda", "Pause"),
    "va_close_app": ("Taka Lafa", "Fechar o Lafa", "Tutup Lafa", "Close Lafa"),
    "app_browser": ("Navegadór internet", "Navegador", "Peramban", "Web browser"), "app_files": ("Ficheiru sira", "Ficheiros", "Berkas", "Files"),
    "app_settings": ("Konfigurasaun sistema", "Definições do sistema", "Pengaturan sistem", "System settings"), "app_calculator": ("Kalkuladora", "Calculadora", "Kalkulator", "Calculator"),
    "app_editor": ("Editór testu", "Editor de texto", "Editor teks", "Text editor"), "app_writer": ("LibreOffice", "LibreOffice", "LibreOffice", "LibreOffice"),
    "app_screenshot": ("Foti ekrã", "Captura de ecrã", "Tangkapan layar", "Screenshot"), "app_sound": ("Som / volume", "Som / volume", "Suara / volume", "Sound / volume"),
    "app_network": ("Wi-Fi / rede", "Wi-Fi / rede", "Wi-Fi / jaringan", "Wi-Fi / network"), "app_printer": ("Imprimidora", "Impressora", "Pencetak", "Printer"),
})

OUTFIT_NAMES = {"casual": ("Kazuál aprende", "Casual de estudo", "Santai belajar", "Casual study"), "traditional": ("Tais Mane", "Tais Mane", "Tais Mane", "Tais Mane"),
                "tuxedo": ("Formál", "Formal", "Formal", "Formal")}
PET_SIZES = {"small": 132, "normal": 176, "large": 220}
WALK_SPEED = {"slow": 38.0, "normal": 58.0, "fast": 92.0}          # pixels per second
ANIMATION_RATES = {"slow": 0.6, "normal": 1.0, "fast": 1.6}
POPUP_WIDTH = 392
# Calm, useful activities (the Timor-Leste guide studies, reads, thinks and dances tebe).
CALM = {"idle", "reading", "thinking", "studying", "sitting", "stretching", "tebe", "bidu", "talking", "lecture", "professor", "report",
        "presentation", "speech_prep", "sightseeing", "hangout", "snack", "eating", "gaming", "ceremony", "meeting"}
PC_APPS = ["browser", "files", "settings", "calculator", "editor", "writer", "screenshot", "sound", "network", "printer"]

def greeting_key(hour):
    return "greet_morning" if 4 <= hour < 12 else "greet_afternoon" if 12 <= hour < 18 else "greet_evening"

class TipCard(QFrame):
    """One tip: clay icon, title, text, a mini quiz and up to two actions."""
    action = Signal(str, str)
    answered = Signal(bool)
    def __init__(self, lang, compact=False, parent=None):
        super().__init__(parent); self.lang = lang; self.compact = compact; self.tip = None
        self.col = QVBoxLayout(self); self.col.setContentsMargins(0, 0, 0, 0); self.col.setSpacing(8)
    def set_tip(self, tip):
        self.tip = tip; clear_layout(self.col); lang = self.lang
        head = QHBoxLayout(); head.setSpacing(10); head.addWidget(ClayIcon(tip.icon, tip.accent, 34 if self.compact else 42), 0, Qt.AlignTop)
        title = label(tip.title, "h3", wrap=True); head.addWidget(title, 1); self.col.addLayout(head)
        if tip.text:
            body = label(clip(tip.text, 210 if self.compact else 420), wrap=True); body.setObjectName("body"); self.col.addWidget(body)
        self.option_buttons = []
        if tip.quiz:
            q = label(tip.quiz["q"], wrap=True); q.setStyleSheet("font-weight:800;"); self.col.addWidget(q)
            grid = QGridLayout(); grid.setSpacing(6)
            for i, option in enumerate(tip.quiz["options"]):
                b = button(f"{'ABCD'[i]}. {clip(option, 60)}", lambda checked=False, k=i: self.answer(k), "answer"); b.setMinimumHeight(36)
                b.setStyleSheet("padding:6px 10px; font-size:13px;"); grid.addWidget(b, i // 2 if not self.compact else i, i % 2 if not self.compact else 0); self.option_buttons.append(b)
            self.col.addLayout(grid)
            self.feedback = label("", wrap=True); self.feedback.hide(); self.col.addWidget(self.feedback)
        self.actions_row = QHBoxLayout(); self.actions_row.setSpacing(6)
        for text_, route, item_id in tip.actions[:2]:
            b = button(text_, lambda checked=False, r=route, i=item_id: self.action.emit(r, i), "chip"); self.actions_row.addWidget(b)
        self.actions_row.addStretch(); self.col.addLayout(self.actions_row)
        if tip.quiz:
            for i in range(self.actions_row.count()):
                w = self.actions_row.itemAt(i).widget()
                if w: w.hide()
    def answer(self, k):
        quiz = self.tip.quiz if self.tip else None
        if not quiz or not self.option_buttons or not self.option_buttons[0].isEnabled(): return
        right = k == quiz["answer"]
        for i, b in enumerate(self.option_buttons):
            b.setProperty("state", "right" if i == quiz["answer"] else "wrong" if i == k else ""); b.style().unpolish(b); b.style().polish(b); b.setEnabled(False)
        tok = tok_of(self); lang = self.lang
        text_ = (tr_text(lang, "va_right") if right else tr_text(lang, "va_wrong", a="ABCD"[quiz["answer"]])) + clip(quiz.get("why", ""), 220)
        self.feedback.setText(text_); self.feedback.setStyleSheet(f"background:{tok['ok_soft'] if right else tok['bad_soft']}; border-radius:12px; padding:8px 10px;"); self.feedback.show()
        for i in range(self.actions_row.count()):
            w = self.actions_row.itemAt(i).widget()
            if w: w.show()
        self.answered.emit(right)

class Balloon(QWidget):
    """A pastel card above Lafa's head with a tip; it stays while the pointer is on it."""
    action = Signal(str, str)
    answered = Signal(bool)
    clicked = Signal()
    def __init__(self, owner):
        super().__init__(None, Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus)
        self.owner = owner; self.setAttribute(Qt.WA_TranslucentBackground); self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.kind = ""; self.tail_x = 0.75
        self.box = QVBoxLayout(self); self.box.setContentsMargins(16, 14, 16, 26); self.box.setSpacing(6)
        self.card = None; self.setFixedWidth(300)
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.timeout.connect(self.hide)
    @property
    def tok(self): return self.owner.tok
    def present(self, tip, anchor, seconds, lang):
        if self.card is not None: self.box.removeWidget(self.card); self.card.deleteLater()
        self.card = TipCard(lang, compact=True, parent=self); self.card.set_tip(tip)
        self.card.action.connect(self.action); self.card.answered.connect(self.answered); self.card.answered.connect(lambda _: self.timer.start(9000))
        self.box.addWidget(self.card); self.kind = tip.kind
        self.adjustSize(); self.setFixedHeight(self.sizeHint().height())
        screen = (QGuiApplication.screenAt(anchor) or QGuiApplication.primaryScreen()).availableGeometry()
        x = max(screen.left() + 4, min(anchor.x() - int(self.width() * self.tail_x), screen.right() - self.width() - 4))
        y = max(screen.top() + 4, anchor.y() - self.height() + 10)
        self.tail_x = min(0.9, max(0.1, (anchor.x() - x) / max(1, self.width())))
        self.move(x, y); self.show(); self.raise_()
        if seconds: self.timer.start(int(seconds * 1000))
        else: self.timer.stop()
    def enterEvent(self, e): self.timer.stop(); super().enterEvent(e)
    def leaveEvent(self, e):
        if not self.timer.isActive(): self.timer.start(2500)
        super().leaveEvent(e)
    def paintEvent(self, event):
        t = self.tok; p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        body = QRectF(3, 3, self.width() - 6, self.height() - 19); path = QPainterPath(); path.addRoundedRect(body, 20, 20)
        tail = QPainterPath(); x = self.width() * self.tail_x
        tail.moveTo(x - 11, body.bottom() - 1); tail.lineTo(x + 11, body.bottom() - 1); tail.lineTo(x + 3, self.height() - 3); tail.closeSubpath()
        path = path.united(tail)
        for i in range(4):
            c = QColor(t["shadow"]); c.setAlpha(max(0, int(c.alpha() * (0.7 - i * 0.16)))); p.setPen(Qt.NoPen); p.setBrush(c); p.drawPath(path.translated(0, 1 + i))
        p.setPen(QPen(QColor(t["glass_border"]), 2)); p.setBrush(QColor(t["glass_solid"])); p.drawPath(path)
        accent = QColor(t["primary"]); accent.setAlpha(170); p.setPen(Qt.NoPen); p.setBrush(accent); p.drawRoundedRect(QRectF(body.left() + 18, body.top() + 1, 46, 4), 2, 2)
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton: self.clicked.emit()

class Companion(QWidget):
    open_requested = Signal()
    quit_requested = Signal()
    route_requested = Signal(str, str)
    settings_requested = Signal()
    outfit_requested = Signal(str)
    settings_changed = Signal()
    read_requested = Signal(str, str)
    def __init__(self, atlas, settings, clock=time.monotonic, kb=None, progress=None):
        super().__init__(); self.atlas = atlas; self.settings = settings; self.clock = clock; self.kb = kb; self.progress = progress
        self.online = False; self.paused = False; self.drag = None; self.moved = False; self.hovered = False; self.walk_target = None; self.pos_x = None
        self.direction = 1; self.introduced = False; self.fullscreen_ahead = False; self.spontaneous = []
        now = clock(); self.last_activity = now; self.last_idle_change = now; self.last_tip = now; self.popup_deadline = 0; self.last_step = now
        self.chooser = TipChooser(); self.tip = None
        self.tok = theme.tokens(self.dark())
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint); self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Lafa Virtual Assistant")
        layout = QVBoxLayout(self); layout.setContentsMargins(8, 8, 8, 8); layout.setSpacing(10)
        self.popup = Card(14, 26); self.popup.setFixedWidth(POPUP_WIDTH); layout.addWidget(self.popup); self.build_popup()
        self.pet = Character(atlas, self, size=PET_SIZES.get(settings.character_size, 176)); self.pet.costume = settings.costume
        layout.addWidget(self.pet, 0, Qt.AlignRight)
        self.balloon = Balloon(self); self.balloon.action.connect(self.follow); self.balloon.clicked.connect(lambda: self.show_bubble())
        self.balloon.answered.connect(self.quiz_answered)
        self.idle_timer = QTimer(self); self.idle_timer.setInterval(1000); self.idle_timer.timeout.connect(self.choose_idle)
        self.walk_timer = QTimer(self); self.walk_timer.setInterval(16); self.walk_timer.timeout.connect(self.walk)
        self.fullscreen_timer = QTimer(self); self.fullscreen_timer.setInterval(10_000); self.fullscreen_timer.timeout.connect(self.check_fullscreen)
        self.popup.hide(); self.setFixedSize(*self.compact_size()); self.pet.animate(False); self.apply_preferences()
        rect = QGuiApplication.primaryScreen().availableGeometry(); self.move(rect.right() - self.width() - 20, rect.bottom() - self.height() - 30)
        self.pet.installEventFilter(self); QApplication.instance().installEventFilter(self)
    # ---------------------------------------------------------------- basics
    @property
    def lang(self): return kb.lang_of(self.settings.locale)
    def t(self, key, **values): return tr_text(self.lang, key, **values)
    def dark(self):
        mode = getattr(self.settings, "theme", "auto")
        return mode == "dark" or (mode == "auto" and getattr(self.settings, "follow_eduka_theme", True) and eduka.theme().get("dark", False))
    @property
    def state(self): return self.pet.state
    @property
    def timer(self): return self.pet.timer
    def compact_size(self): return (self.pet.width() + 16, self.pet.height() + 16)
    def expanded_size(self):
        """Popup + Lafa, sized for the wrapped texts at the popup's width (never squashed), within the screen."""
        screen = (self.screen().availableGeometry() if hasattr(self, "screen") and self.screen() else QGuiApplication.primaryScreen().availableGeometry())
        self.popup.layout().activate()
        h = self.popup.heightForWidth(POPUP_WIDTH) if self.popup.hasHeightForWidth() else -1
        if h <= 0: self.popup.adjustSize(); h = self.popup.sizeHint().height()
        return (max(POPUP_WIDTH + 16, self.pet.width() + 16), min(h + 10 + self.pet.height() + 16 + 4, screen.height() - 8))
    def mark_activity(self): self.popup_deadline = 0; self.last_activity = self.clock(); self.last_idle_change = self.last_activity
    # ----------------------------------------------------------------- popup
    def build_popup(self):
        box = self.popup.box; box.setSpacing(10)
        self.header = Card(12, 20, gradient=(self.tok["nav_a"], self.tok["primary"], self.tok["nav_b"]))
        row = QHBoxLayout(); row.setSpacing(10); self.face = QLabel(); row.addWidget(self.face, 0, Qt.AlignBottom)
        names = QVBoxLayout(); names.setSpacing(0); self.hello = label("", "h3", wrap=True); self.hello.setStyleSheet("color:white;")
        self.role = label("", "caption", wrap=True); self.role.setStyleSheet("color:rgba(255,255,255,0.9);"); names.addWidget(self.hello); names.addWidget(self.role)
        self.status = label("", "caption"); self.status.setStyleSheet("color:white; background:rgba(255,255,255,0.2); border-radius:9px; padding:2px 8px;"); names.addWidget(self.status, 0, Qt.AlignLeft)
        row.addLayout(names, 1)
        close = button("", self.collapse, "icon", "close", "×"); close.setFixedSize(32, 32); row.addWidget(close, 0, Qt.AlignTop); self.close_button = close
        self.header.box.addLayout(row); box.addWidget(self.header)
        self.ask = SearchBox(""); self.ask.textEdited.connect(self.search_live); self.ask.returnPressed.connect(self.search_all); box.addWidget(self.ask)
        self.results = QVBoxLayout(); self.results.setSpacing(4); box.addLayout(self.results)
        self.tip_card = TipCard(self.lang); self.tip_card.action.connect(self.follow); self.tip_card.answered.connect(self.quiz_answered); box.addWidget(self.tip_card)
        tiprow = QHBoxLayout(); tiprow.addStretch(); self.more_button = button("", self.next_tip, "ghost", "shuffle"); tiprow.addWidget(self.more_button); box.addLayout(tiprow)
        grid = QGridLayout(); grid.setSpacing(8); self.tiles = {}
        for i, (key, icon_name, accent_key) in enumerate((("continue", "book-open", "violet"), ("quiz", "trophy", "butter"), ("words", "translate", "mint"),
                                                          ("map", "map", "teal"), ("calendar", "calendar-check", "rose"), ("pc", "monitor-help", "sky"))):
            tile = QPushButton(); tile.setObjectName("chip"); tile.setCursor(Qt.PointingHandCursor); tile.setMinimumHeight(58)
            tile.setIcon(icons.icon(icon_name, theme.accent(accent_key)[0])); tile.setIconSize(QSize(22, 22))
            tile.clicked.connect(lambda checked=False, k=key: self.tile(k)); grid.addWidget(tile, i // 3, i % 3); self.tiles[key] = tile
        box.addLayout(grid)
        foot = QHBoxLayout(); foot.setSpacing(6)
        self.desk_button = button("", self.open_requested.emit, "primary", "monitor"); foot.addWidget(self.desk_button, 1)
        self.voice_button = button("", self.read_tip, "icon", "speaker"); self.voice_button.setFixedSize(38, 38); foot.addWidget(self.voice_button)
        self.voice_button.setVisible(bool(shutil.which("espeak-ng") or shutil.which("espeak")))
        self.quiet_button = button("", None, "icon", "moon"); self.quiet_button.setCheckable(True); self.quiet_button.setFixedSize(38, 38); self.quiet_button.toggled.connect(self.set_quiet); foot.addWidget(self.quiet_button)
        self.config_button = button("", self.settings_requested.emit, "icon", "settings"); self.config_button.setFixedSize(38, 38); foot.addWidget(self.config_button)
        box.addLayout(foot)
    def retranslate(self):
        t = self.t; name = self.settings.learner_name or first_name() or t("learner")
        self.hello.setText(t("va_hello", greet=t(greeting_key(datetime.now().hour)), name=name)); self.role.setText(t("va_role"))
        self.status.setText("● " + (t("online") if self.online else t("offline")))
        self.face.setPixmap(self.atlas.pose_pixmap(self.settings.costume, 64)); self.close_button.setToolTip(t("close"))
        self.ask.setPlaceholderText(t("va_ask")); self.ask.setAccessibleName(t("va_ask")); self.more_button.setText(t("va_more_tips"))
        for key, b in self.tiles.items(): b.setText(t("va_tile_" + key)); b.setAccessibleName(t("va_tile_" + key))
        self.desk_button.setText(t("va_open_desktop")); self.voice_button.setToolTip(t("va_read")); self.quiet_button.setToolTip(t("va_quiet")); self.config_button.setToolTip(t("va_settings"))
        self.quiet_button.blockSignals(True); self.quiet_button.setChecked(bool(self.settings.quiet_mode)); self.quiet_button.blockSignals(False)
        self.tip_card.lang = self.lang
        if self.tip: self.tip_card.set_tip(self.tip)
    def apply_preferences(self):
        """Lafa-Configuration (Eduka-Settings): size, speed, outfit, theme — applied live."""
        size = PET_SIZES.get(self.settings.character_size, 176)
        if self.pet.width() != size: self.pet.setFixedSize(size, size + 16)
        self.pet.rate = ANIMATION_RATES.get(self.settings.animation_speed, 1.0); self.pet.reduce_motion = self.settings.reduce_motion
        if self.pet.costume != self.settings.costume:
            self.pet.costume = self.settings.costume
            if self.state not in self.activity_choices() + ["walking", "talking", "idle", "greeting"]: self.set_state("idle")
        self.tok = theme.tokens(self.dark()); self.header.gradient = (self.tok["nav_a"], self.tok["primary"], self.tok["nav_b"]); self.header.update(); self.popup.update()
        self.setFixedSize(*(self.expanded_size() if self.popup.isVisible() else self.compact_size()))
        if self.isVisible() and not self.popup.isVisible(): self.snap_to_panel()
        self.retranslate(); self.update_mask()
    def set_state(self, state):
        self.pet.set_state(state); self.update_mask()
    def update_mask(self):
        """Compact Lafa only takes clicks on the character; the rest passes to the windows below."""
        if self.popup.isVisible(): self.clearMask(); return
        region = self.pet.mask_region().translated(self.pet.pos())
        if region.isEmpty(): self.clearMask()
        else: self.setMask(region)
    # ------------------------------------------------------------------ tips
    def next_tip(self):
        if not self.kb: return
        self.tip = self.chooser.next(self.kb, self.progress, self.settings, self.lang); self.tip_card.set_tip(self.tip)
        if self.popup.isVisible(): self.setFixedSize(*self.expanded_size())
    def read_tip(self):
        if self.tip: self.read_requested.emit(self.tip.speech(), self.lang)
    def quiz_answered(self, right):
        self.pet.gesture("jump" if right else "shake"); self.mark_activity()
        if self.progress:
            try: self.progress.record("assistant:quiz", 1 if right else 0, 1)
            except ValueError: pass
    def follow(self, route, item_id):
        """A tip or result button: open Lafa Desktop on that page."""
        self.balloon.hide()
        if route == "map" and item_id: self.route_requested.emit("map", item_id)
        else: self.route_requested.emit(route, item_id)
    def tile(self, key):
        self.mark_activity()
        if key == "continue":
            last = self.progress.last if self.progress else None
            if last and self.kb and self.kb.get(last.get("key", "")): self.route_requested.emit("item", last["key"])
            else: self.route_requested.emit("paths", "")
        elif key == "quiz": self.route_requested.emit("quiz", "")
        elif key == "words": self.route_requested.emit("language", "")
        elif key == "map": self.route_requested.emit("map", "")
        elif key == "calendar": self.route_requested.emit("calendar", "")
        elif key == "pc": self.pc_menu()
    def pc_menu(self):
        menu = QMenu(self); t = self.t
        for key in PC_APPS:
            app = actions.APP_BY_KEY.get(key)
            if not app: continue
            path = actions.which_app(app); a = menu.addAction(icons.icon("monitor", self.tok["primary"]), t("app_" + key)); a.setEnabled(bool(path))
            a.triggered.connect(lambda checked=False, p=path: QProcess.startDetached(p, []) if p else None)
        menu.addSeparator(); menu.addAction(t("va_settings"), self.settings_requested.emit)
        b = self.tiles["pc"]; menu.exec_(b.mapToGlobal(b.rect().bottomLeft())) if hasattr(menu, "exec_") else menu.exec(b.mapToGlobal(b.rect().bottomLeft()))
    # ---------------------------------------------------------------- search
    def search_live(self, text_):
        clear_layout(self.results); q = text_.strip()
        if len(q) < 2 or not self.kb:
            self.tip_card.show(); self.more_button.show(); self.setFixedSize(*self.expanded_size()); return
        self.tip_card.hide(); self.more_button.hide(); lang = self.lang
        hits = self.kb.search(q, lang, limit=5); words = self.kb.search_words(q, self.settings.vocab_lang, limit=3)
        for item, _score in hits:
            cat = kb.CATEGORY.get(item.category); row = QPushButton(f"  {item.title(lang)}"); row.setObjectName("chip"); row.setCursor(Qt.PointingHandCursor)
            row.setIcon(icons.icon(cat.icon if cat else "book-open", theme.accent(cat.accent if cat else "violet")[0])); row.setStyleSheet("text-align:left; padding:8px 10px;")
            row.clicked.connect(lambda checked=False, i=item.id: self.follow("item", i)); self.results.addWidget(row)
        for w in words:
            meaning = w.meaning(self.settings.vocab_lang) or w.meaning("en")
            l = label(f"<b>{kb.show(w.tet, 'tet')}</b> = {meaning}", wrap=True); l.setStyleSheet(f"background:{self.tok['card_hover']}; border-radius:12px; padding:6px 10px;"); self.results.addWidget(l)
        if not hits and not words: self.results.addWidget(label(self.t("va_no_results"), "muted", wrap=True))
        more = button(self.t("va_see_all"), self.search_all, "ghost", "search"); self.results.addWidget(more, 0, Qt.AlignLeft)
        self.setFixedSize(*self.expanded_size())
    def search_all(self):
        q = self.ask.text().strip()
        if q: self.route_requested.emit("search", q)
    # ------------------------------------------------------------- show/hide
    def show_bubble(self, text=None):
        if not self.settings.companion: return
        if self.tip is None: self.next_tip()
        self.balloon.hide(); self.walk_target = None
        if self.state == "walking": self.set_state("idle")
        anchor = self.geometry().bottomRight(); self.popup.show(); self.setFixedSize(*self.expanded_size())
        self.place_near(anchor); self.update_mask(); self.mark_activity(); self.show(); self.raise_(); self.pet.gesture("wave")
    def collapse(self):
        anchor = self.geometry().bottomRight(); self.popup.hide(); self.setFixedSize(*self.compact_size()); self.place_near(anchor)
        self.snap_to_panel(); self.update_mask(); self.mark_activity()
    def toggle_bubble(self):
        if self.popup.isVisible(): self.collapse()
        else: self.show_bubble()
    def place_near(self, anchor):
        if QGuiApplication.platformName() != "xcb": return
        rect = (QGuiApplication.screenAt(anchor) or QGuiApplication.primaryScreen()).availableGeometry()
        self.move(max(rect.left(), min(anchor.x() - self.width(), rect.right() - self.width())), max(rect.top(), min(anchor.y() - self.height(), rect.bottom() - self.height())))
    def show_tip_balloon(self, tip, seconds=None):
        if not self.settings.companion or not self.isVisible() or self.popup.isVisible(): return
        top = self.pet.mapToGlobal(self.pet.rect().topLeft()); anchor = top + QPointF(self.pet.width() * 0.62, 18).toPoint()
        self.set_state("greeting"); self.pet.gesture("wave")
        self.balloon.present(tip, anchor, seconds if seconds is not None else max(10, self.settings.balloon_seconds * 2), self.lang)
    # ------------------------------------------------------------- behaviour
    def set_online(self, online):
        self.online = bool(online); self.retranslate()
        if self.settings.companion:
            was_visible = self.isVisible(); self.show(); self.pet.animate(not self.paused)
            if not was_visible: self.snap_to_panel()
            if not self.paused:
                for timer in (self.idle_timer, self.walk_timer): timer.start() if not timer.isActive() else None
                if QGuiApplication.platformName() == "xcb" and not self.fullscreen_timer.isActive(): self.fullscreen_timer.start()
                if not self.introduced:
                    self.introduced = True; self.set_state("greeting")
                    QTimer.singleShot(900, lambda: self.show_tip_balloon(welcome(self.lang), 14))
            else: self.idle_timer.stop(); self.walk_timer.stop(); self.balloon.hide()
        else:
            self.hide(); self.balloon.hide(); self.pet.animate(False); self.idle_timer.stop(); self.walk_timer.stop(); self.fullscreen_timer.stop()
            self.introduced = False
    def can_auto_popup(self):
        """Spontaneous tips: never in quiet mode, while paused, behind a full-screen app,
        while the learner is busy with Lafa, or above the hourly limit."""
        if self.settings.quiet_mode or self.fullscreen_ahead or not getattr(self.settings, "knowledge_tips", True): return False
        recent = [x for x in self.spontaneous if self.clock() - x < 3600]; self.spontaneous = recent
        if len(recent) >= max(1, self.settings.messages_per_hour): return False
        return (self.settings.companion and not self.paused and self.drag is None and not self.hovered and not self.popup.isVisible()
                and not self.balloon.isVisible() and self.clock() - self.last_activity >= 30)
    def activity_choices(self):
        allowed = CALM | ({"bathing", "toilet", "sleeping"} if self.settings.personal_activities else set())
        choices = [s for s in outfits.activities_for(self.settings.costume) if s in allowed and s != self.state]
        if self.settings.reduce_motion: choices = [s for s in choices if s not in {"tebe", "bidu", "stretching"}]
        return choices or ["idle"]
    def can_roam(self):
        return QGuiApplication.platformName() == "xcb" and self.settings.roam and self.settings.companion and not self.settings.reduce_motion
    def choose_idle(self):
        now = self.clock()
        if self.paused or self.drag: return
        if self.popup_deadline and now >= self.popup_deadline: self.popup_deadline = 0; self.collapse()
        if self.popup.isVisible() or self.hovered: return
        # Share knowledge regularly (default every 10–15 minutes, at most N per hour).
        if now - self.last_tip >= max(2, self.settings.card_minutes) * 60 and self.can_auto_popup() and self.kb:
            self.last_tip = now; self.spontaneous.append(now)
            tip = self.chooser.next(self.kb, self.progress, self.settings, self.lang); self.show_tip_balloon(tip); return
        if self.walk_target is not None or self.balloon.isVisible(): return
        if now - max(self.last_activity, self.last_idle_change) < self.settings.idle_seconds: return
        if self.can_roam() and self.state != "walking" and random.random() < 0.55: self.start_walk()
        else: self.start_activity()
    def start_activity(self):
        self.walk_target = None; self.set_state(random.choice(self.activity_choices())); self.last_idle_change = self.clock()
    def start_walk(self):
        self.snap_to_panel(); rect = self.panel_rect(); left, right = rect.left(), rect.right() - self.width()
        if right - left < 60: self.start_activity(); return
        target = random.randint(left, right)
        if abs(target - self.x()) < 120: target = left if self.x() - left > right - self.x() else right
        self.walk_target = target; self.pos_x = float(self.x()); self.direction = 1 if target > self.x() else -1; self.pet.direction = self.direction
        self.set_state("walking"); self.last_idle_change = self.clock(); self.last_step = self.clock()
    def walk(self):
        """Smooth walking: moves by speed × time (60 updates a second), easing out at the end."""
        now = self.clock(); dt = min(0.1, max(0.0, now - self.last_step)); self.last_step = now
        if (self.paused or not self.settings.companion or self.state != "walking" or not self.settings.roam or self.drag or self.hovered
                or self.popup.isVisible() or QGuiApplication.platformName() != "xcb" or self.walk_target is None): return
        rect = self.panel_rect(); speed = WALK_SPEED.get(self.settings.walk_speed, 58.0) * ANIMATION_RATES.get(self.settings.animation_speed, 1.0)
        if self.pos_x is None: self.pos_x = float(self.x())
        left = self.walk_target - self.pos_x; distance = abs(left)
        step = min(distance, speed * dt * (0.35 + 0.65 * min(1.0, distance / 60.0)))     # slow down for the last steps
        self.direction = 1 if left > 0 else -1; self.pet.direction = self.direction
        self.pos_x += self.direction * step; nx = int(round(self.pos_x))
        y = self.panel_y(rect) if self.settings.panel_roam else self.y()
        old = self.x(); self.move(max(rect.left(), min(nx, rect.right() - self.width() + 1)), y)
        if self.x() != old: self.pet.advance(self.x() - old); self.update_mask()
        if self.balloon.isVisible(): self.balloon.hide()
        if distance <= 0.6: self.pos_x = None; self.start_activity()
    # ------------------------------------------------------------- panel/X11
    def eduka_panel(self): return eduka.panel() if self.settings.follow_eduka_panel else None
    def panel_rect(self):
        screen = QGuiApplication.screenAt(self.geometry().center()) or QGuiApplication.primaryScreen()
        info = self.eduka_panel(); geometry = screen.geometry()
        if info and info["edge"] in {"bottom", "top"}:
            x0, x1 = eduka.panel_span(geometry.left(), geometry.width(), info)
            return QRect(x0, geometry.top(), max(self.width(), x1 - x0), geometry.height())
        return geometry if self.settings.panel_roam else screen.availableGeometry()
    def panel_y(self, rect=None):
        rect = rect or self.panel_rect(); info = self.eduka_panel()
        if info:
            if info["edge"] == "bottom": return rect.bottom() + 1 - info["gap"] - info["height"] - self.height()
            if info["edge"] == "top": return rect.top() + info["gap"] + info["height"]
            available = (QGuiApplication.screenAt(self.geometry().center()) or QGuiApplication.primaryScreen()).availableGeometry()
            return available.bottom() + 1 - self.height()
        if self.settings.panel_edge == "bottom": return rect.bottom() - self.settings.panel_height - self.height() + 1
        return rect.top() + self.settings.panel_height
    def snap_to_panel(self):
        if QGuiApplication.platformName() != "xcb" or not self.settings.panel_roam or self.popup.isVisible(): return
        rect = self.panel_rect(); self.move(max(rect.left(), min(self.x(), rect.right() - self.width() + 1)), self.panel_y(rect))
    def check_fullscreen(self):
        ahead = eduka.fullscreen_active() if self.settings.companion and QGuiApplication.platformName() == "xcb" else False
        if ahead != self.fullscreen_ahead:
            self.fullscreen_ahead = ahead
            if ahead: self.balloon.hide(); self.hide()
            elif self.settings.companion: self.show(); self.snap_to_panel()
    def set_quiet(self, quiet):
        self.settings.quiet_mode = bool(quiet); self.balloon.hide(); self.settings_changed.emit()
    def toggle_pause(self, paused): self.paused = bool(paused); self.set_online(self.online)
    # ----------------------------------------------------------------- input
    def eventFilter(self, obj, event):
        if not hasattr(self, "pet"): return False
        if event.type() in {QEvent.MouseButtonPress, QEvent.KeyPress} and (obj is self or obj is self.pet or isinstance(obj, QWidget) and obj.window() is self): self.mark_activity()
        if obj is self.pet:
            if event.type() == QEvent.Enter: self.on_hover(True)
            elif event.type() == QEvent.Leave: self.on_hover(False)
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.drag = global_point(event) - self.pos(); self.moved = False; return True
            if event.type() == QEvent.MouseMove and self.drag is not None and event.buttons() & Qt.LeftButton:
                self.moved = True; self.balloon.hide()
                if QGuiApplication.platformName().startswith("wayland"):
                    if self.windowHandle(): self.windowHandle().startSystemMove()
                else: self.move(global_point(event) - self.drag)
                return True
            if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                if not self.moved: self.toggle_bubble()
                self.drag = None; return True
        return super().eventFilter(obj, event)
    def on_hover(self, inside):
        self.hovered = inside
        if inside:
            self.walk_target = None
            if self.state == "walking": self.set_state("idle")
            if not self.paused and not self.popup.isVisible() and not self.balloon.isVisible() and self.settings.hover_questions and not self.settings.quiet_mode:
                self.show_tip_balloon(Tip("hover", "sparkle", "violet", "Lafa", self.t("va_hover")), 4)
    def contextMenuEvent(self, event):
        self.mark_activity(); self.balloon.hide(); menu = QMenu(self); t = self.t; lang = self.lang
        menu.addAction(t("va_open_desktop"), self.open_requested.emit); menu.addAction(t("va_more_tips"), lambda: self.show_tip_balloon(self.chooser.next(self.kb, self.progress, self.settings, lang)) if self.kb else None)
        quiet = menu.addAction(t("va_quiet")); quiet.setCheckable(True); quiet.setChecked(bool(self.settings.quiet_mode)); quiet.triggered.connect(self.set_quiet)
        wardrobe = menu.addMenu(t("va_outfit"))
        for outfit in outfits.OUTFITS:
            name = OUTFIT_NAMES.get(outfit, (outfit,) * 4)[kb.LANGS.index(lang) if lang in kb.LANGS else 3]
            a = wardrobe.addAction(name); a.setCheckable(True); a.setChecked(self.settings.costume == outfit); a.triggered.connect(lambda checked=False, o=outfit: self.outfit_requested.emit(o))
        pause = menu.addAction(t("va_pause")); pause.setCheckable(True); pause.setChecked(self.paused); pause.triggered.connect(self.toggle_pause)
        menu.addSeparator(); menu.addAction(t("va_settings"), self.settings_requested.emit); menu.addAction(t("va_close_app"), self.quit_requested.emit)
        menu.exec_(event.globalPos()) if hasattr(menu, "exec_") else menu.exec(event.globalPos())
    def paintEvent(self, event):
        if not self.popup.isVisible(): return
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); p.setPen(Qt.NoPen); p.setBrush(QColor(self.tok["glass_solid"]))
        y = self.popup.geometry().bottom() - 8; x = self.width() - self.pet.width() * 0.45
        path = QPainterPath(); path.moveTo(x - 12, y); path.lineTo(x + 12, y); path.lineTo(x + 2, y + 16); path.closeSubpath(); p.drawPath(path)
    def hideEvent(self, event): self.balloon.hide(); super().hideEvent(event)
    def closeEvent(self, event):
        app = QApplication.instance()
        if app: app.removeEventFilter(self)
        self.balloon.hide(); self.balloon.close(); super().closeEvent(event)

def first_name():
    import os, pwd
    try:
        gecos = pwd.getpwuid(os.getuid()).pw_gecos.split(",")[0].strip()
        value = gecos or os.environ.get("USER", "")
        return value.split()[0].capitalize() if value else ""
    except (KeyError, IndexError, OSError):
        return ""
