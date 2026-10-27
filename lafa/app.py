"""Lafa Desktop 0.3 — Ensiklopédia Timór-Leste — and the Lafa Virtual Assistant.

Lafa Desktop teaches about Timor-Leste only: an encyclopedia from the birth of
the island to 2026, an interactive map of the municipalities, the history
timeline, tourist places, national days, a millionaire quiz, Tetun words in
fourteen languages and learning paths for the school levels of the Ministry of
Education. Everything works offline; with internet Lafa downloads texts,
pictures and data from the sources it credits (see Fontes no lisensa).

The Virtual Assistant (lafa/mascot.py) is switched on only in Eduka-Settings →
Lafa-Configuration and opens Lafa Desktop on the right page.
"""
import argparse
import os
import sys
import tempfile
import time
from datetime import date, datetime
from pathlib import Path

from .qt import (Qt, QTimer, QSize, QPoint, QRectF, QPropertyAnimation, QEasingCurve, QObject, Signal, QRunnable, QThreadPool,
                 QLockFile, QShortcut, QKeySequence, QIcon, QDesktopServices, QUrl, QColor, QPainter, QPalette, QFont,
                 QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QStackedWidget,
                 QGraphicsOpacityEffect, QMenu, QSystemTrayIcon, QMessageBox, BINDING, run, prepare_application)
from . import __version__, VERSION_LABEL, kb, eduka, icons, platform_check
from .config import Settings, config_path, data_dir, SECTIONS
from .progress import Progress
from .store import Store
from .voice import Voice
from .net import online_probe
from .instance import ActivationServer, activate_existing, server_name
from .mascot import Atlas
from .assistant import Companion
from .desk import theme
from .desk.texts import t as tr_text
from .desk.widgets import (Card, Clickable, ClayIcon, NavButton, SearchBox, Toast, label, button, refresh_icon, tok_of)
from .desk.pages import page_class

NAV = [("home", "home", "violet"), ("encyclopedia", "book-open", "pink"), ("map", "map", "teal"), ("timeline", "timeline", "peach"),
       ("places", "umbrella", "cyan"), ("calendar", "calendar-check", "rose"), ("quiz", "trophy", "butter"),
       ("language", "translate", "mint"), ("paths", "graduation", "lilac")]
FOOT = [("sources", "shield", "slate"), ("settings", "settings", "indigo"), ("about", "info", "sky")]
NAV_PARENT = {"category": "encyclopedia", "item": "encyclopedia", "search": "home", "data": "home"}

class Signals(QObject):
    done = Signal(object, object)

class Job(QRunnable):
    """Run a function in a worker thread and deliver (result, error) to the GUI thread."""
    def __init__(self, fn, callback):
        super().__init__(); self.fn = fn; self.signals = Signals(); self.signals.done.connect(callback)
    def run(self):
        try: result, error = self.fn(), None
        except Exception as e: result, error = None, e   # reported to the user, never raised in a worker thread
        try: self.signals.done.emit(result, error)
        except RuntimeError: pass

class Backdrop(QWidget):
    """Pastel gradient with soft colour blobs behind the glass cards."""
    def paintEvent(self, event):
        p = QPainter(self); theme.paint_background(p, QRectF(self.rect()), tok_of(self))

class Window(QMainWindow):
    COMPACT_WIDTH = 1180
    def __init__(self, settings=None, review=False):
        super().__init__()
        self.settings = settings or Settings.load(); self.review = review
        self.folder = Path(tempfile.mkdtemp(prefix="lafa-review-")) if review else data_dir()
        self.kb = kb.KnowledgeBase(overrides=self.folder / "updates")
        self.progress = Progress(self.folder)
        try: self.store = Store(self.folder)
        except Exception: self.store = None      # a broken database never stops the app (sqlite3.Error, OSError)
        self.voice = Voice(); self.pool = QThreadPool(self); self.pool.setMaxThreadCount(3); self.jobs = set()
        self.atlas = Atlas(); self.online = bool(review); self.history = []; self.pages = {}; self.route = None; self.params = {}
        self.settings_dialog = None; self.tray = None; self.compact = None; self.speaking = False
        self.tok = self.theme_tokens()
        self.setWindowTitle("Lafa · " + self.t("app_subtitle")); self.resize(1360, 860); self.setMinimumSize(980, 600)
        self.setWindowIcon(QIcon(self.atlas.pose_pixmap(self.settings.costume, 128)))
        self.companion = Companion(self.atlas, self.settings, kb=self.kb, progress=self.progress)
        self.companion.open_requested.connect(self.reveal)
        self.companion.quit_requested.connect(self.exit_app)
        self.companion.route_requested.connect(self.open_from_assistant)
        self.companion.settings_requested.connect(self.open_configuration)
        self.companion.outfit_requested.connect(self.change_outfit)
        self.companion.settings_changed.connect(self.save_quietly)
        self.companion.read_requested.connect(self.speak)
        self.build_ui()
        self.open(self.settings.start_page if self.settings.start_page in SECTIONS else "home", push=False)
        self.probe_timer = QTimer(self); self.probe_timer.timeout.connect(self.probe)
        self.update_timer = QTimer(self); self.update_timer.timeout.connect(self.maybe_auto_update)
        if not review:
            self.setup_tray(); self.probe_timer.start(90_000); QTimer.singleShot(400, self.probe)
            self.update_timer.start(30 * 60_000)
        self.companion.set_online(self.online)
    # ------------------------------------------------------------- basics
    @property
    def lang(self): return kb.lang_of(self.settings.locale)
    def t(self, key, **values): return tr_text(self.lang, key, **values)
    def theme_tokens(self):
        mode = self.settings.theme
        dark = mode == "dark" or (mode == "auto" and self.settings.follow_eduka_theme and eduka.theme().get("dark", False))
        return theme.tokens(dark)
    def scale(self): return self.settings.text_scale / 100.0
    def run_job(self, fn, callback):
        job = Job(fn, lambda result, error: (self.jobs.discard(job), callback(result, error)))
        self.jobs.add(job); self.pool.start(job)
    # --------------------------------------------------------------- shell
    def build_ui(self):
        app = QApplication.instance()
        if app: app.setStyleSheet(theme.style_sheet(self.tok, self.scale()))
        pal = self.palette(); pal.setColor(QPalette.Link, QColor(self.tok["primary"])); pal.setColor(QPalette.LinkVisited, QColor(self.tok["primary"])); self.setPalette(pal)
        root = Backdrop(); root.setObjectName("root"); outer = QHBoxLayout(root); outer.setContentsMargins(14, 14, 14, 14); outer.setSpacing(16)
        # Sidebar (glass): brand, pages, offline card, footer.
        side = QFrame(); side.setObjectName("sidebar"); self.sidebar = side
        col = QVBoxLayout(side); col.setContentsMargins(14, 18, 14, 14); col.setSpacing(4)
        brand = QHBoxLayout(); brand.setSpacing(10); face = QLabel(); face.setPixmap(self.atlas.pose_pixmap(self.settings.costume, 46)); face.setFixedSize(48, 48)
        brand.addWidget(face); names = QVBoxLayout(); names.setSpacing(0); self.brand_name = label("Lafa", "h2"); self.brand_sub = label(self.t("app_subtitle"), "caption", wrap=True)
        names.addWidget(self.brand_name); names.addWidget(self.brand_sub); brand.addLayout(names, 1); col.addLayout(brand); col.addSpacing(14)
        self.nav = {}
        for i, (key, icon_name, accent) in enumerate(NAV):
            b = NavButton(icon_name, accent, self.t("nav_" + key)); b.clicked.connect(lambda checked=False, k=key: self.open(k)); col.addWidget(b); self.nav[key] = b
            QShortcut(QKeySequence(f"Alt+{i + 1}"), self, activated=lambda k=key: self.open(k))
        col.addStretch(1)
        # "Upgrade" card of the references → the offline download card.
        promo = Card(12, 22); promo.box.setSpacing(6); self.promo = promo
        top = QHBoxLayout(); top.setSpacing(10); top.addWidget(ClayIcon("cloud-download", "lilac", 40))
        self.promo_title = label(self.t("offline_promo_title"), "h3", wrap=True); top.addWidget(self.promo_title, 1); promo.box.addLayout(top)
        self.promo_text = label(self.t("offline_promo_text"), "caption", wrap=True); promo.box.addWidget(self.promo_text)
        self.promo_button = button(self.t("offline_promo_button"), lambda: self.open("data"), "primary"); promo.box.addWidget(self.promo_button)
        col.addWidget(promo); col.addSpacing(8)
        for key, icon_name, accent in FOOT:
            b = NavButton(icon_name, accent, self.t("nav_" + key)); b.setMinimumHeight(40); b.setIconSize(QSize(24, 24)); b.clicked.connect(lambda checked=False, k=key: self.open(k)); col.addWidget(b); self.nav[key] = b
        outer.addWidget(side)
        # Content: top bar and pages.
        content = QWidget(); ccol = QVBoxLayout(content); ccol.setContentsMargins(0, 0, 0, 0); ccol.setSpacing(12)
        bar = QHBoxLayout(); bar.setSpacing(10)
        self.back_button = button("", self.go_back, "icon", "back", self.t("back")); self.back_button.setFixedSize(44, 44); bar.addWidget(self.back_button)
        self.search = SearchBox(self.t("search_placeholder")); self.search.setMaximumWidth(560); self.search.returnPressed.connect(self.run_search)
        self.search_timer = QTimer(self); self.search_timer.setSingleShot(True); self.search_timer.setInterval(350); self.search_timer.timeout.connect(self.live_search)
        self.search.textEdited.connect(lambda _=None: self.search_timer.start()); bar.addWidget(self.search, 1)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: (self.search.setFocus(), self.search.selectAll()))
        QShortcut(QKeySequence("Alt+Left"), self, activated=self.go_back)
        bar.addStretch(0)
        self.status_chip = QPushButton(); self.status_chip.setObjectName("chip"); self.status_chip.setCursor(Qt.PointingHandCursor); self.status_chip.clicked.connect(lambda: self.open("data"))
        bar.addWidget(self.status_chip)
        self.bell = button("", self.show_notifications, "icon", "bell", self.t("notifications")); self.bell.setFixedSize(44, 44); bar.addWidget(self.bell)
        self.profile = Clickable(6, 18); self.profile.SH = (2, 1, 2, 3); self.profile.box.setContentsMargins(10, 4, 12, 6)
        prow = QHBoxLayout(); prow.setSpacing(8); self.avatar = QLabel(); self.avatar.setPixmap(self.atlas.pose_pixmap(self.settings.costume, 34)); prow.addWidget(self.avatar)
        pcol = QVBoxLayout(); pcol.setSpacing(0); self.profile_name = label("", "h3"); self.profile_level = label("", "caption"); pcol.addWidget(self.profile_name); pcol.addWidget(self.profile_level)
        prow.addLayout(pcol); self.profile.box.addLayout(prow); self.profile.clicked.connect(lambda: self.open("settings")); bar.addWidget(self.profile)
        ccol.addLayout(bar)
        if self.review:
            note = label(self.t("review_banner"), "caption"); note.setStyleSheet(f"background:{self.tok['warn_soft']}; color:{self.tok['warn']}; border-radius:10px; padding:4px 10px;"); ccol.addWidget(note)
        self.stack = QStackedWidget(); ccol.addWidget(self.stack, 1)
        outer.addWidget(content, 1)
        self.setCentralWidget(root)
        self.toast = Toast(root)
        self.pages = {}; self.update_status(); self.update_profile(); self.apply_compact(force=True)
    def rebuild(self):
        """Language, theme or text size changed: rebuild the shell and reopen the page."""
        route, params = self.route, dict(self.params)
        self.tok = self.theme_tokens()
        self.build_ui(); self.open(route or "home", push=False, **params)
        self.companion.apply_preferences(); self.companion.retranslate()
    def apply_compact(self, force=False):
        compact = self.width() < self.COMPACT_WIDTH
        self.promo.setVisible(not compact and self.height() >= 960)
        if compact == self.compact and not force: return
        self.compact = compact; self.sidebar.setFixedWidth(84 if compact else 252)
        self.brand_name.setVisible(not compact); self.brand_sub.setVisible(not compact)
        for b in self.nav.values(): b.set_compact(compact)
        self.profile_name.setVisible(not compact); self.profile_level.setVisible(not compact)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "sidebar"): self.apply_compact()
    def update_status(self):
        on = self.online
        self.status_chip.setText("  " + self.t("online" if on else "offline")); self.status_chip.setToolTip(self.t("online_tip" if on else "offline_tip"))
        self.status_chip.setIcon(icons.icon("globe" if on else "cloud-check", self.tok["ok"] if on else self.tok["primary"])); self.status_chip.setChecked(False)
    def update_profile(self):
        name = self.settings.learner_name or first_name() or self.t("learner")
        self.profile_name.setText(name)
        self.profile_level.setText(f"{kb.LEVEL_SHORT.get(self.settings.school_level, '')} · " + self.t("xp_level", n=self.progress.level_name, xp=self.progress.xp))
    # -------------------------------------------------------------- router
    def page(self, route):
        if route not in self.pages:
            page = page_class(route)(self); page.setObjectName("page"); self.pages[route] = page; self.stack.addWidget(page)
        return self.pages[route]
    def open(self, route, push=True, **params):
        try: page = self.page(route)
        except (KeyError, ImportError) as e:
            self.toast.show_text(str(e)); return
        if push and self.route is not None: self.history.append((self.route, self.params))
        self.history = self.history[-60:]
        self.route, self.params = route, dict(params)
        page.show_route(dict(params))
        if self.stack.currentWidget() is not page: self.fade_to(page)
        active = NAV_PARENT.get(route, route)
        if route == "item":
            item = self.kb.get(params.get("id", "")); active = {"place": "places", "day": "calendar", "municipality": "map"}.get(item.kind if item else "", "encyclopedia")
        for key, b in self.nav.items(): b.setChecked(key == active)
        self.back_button.setVisible(bool(self.history))
        self.update_profile()
        # After a menu click the keyboard focus moves to the page (like "skip to content").
        focus = QApplication.focusWidget()
        if focus is None or isinstance(focus, NavButton): page.setFocus(Qt.OtherFocusReason)
    def go_back(self):
        if not self.history: return
        route, params = self.history.pop(); self.open(route, push=False, **params); self.back_button.setVisible(bool(self.history))
    def reload_content(self):
        """New content files were installed: load them and rebuild the pages."""
        self.kb = kb.KnowledgeBase(overrides=self.folder / "updates"); self.companion.kb = self.kb
        route, params = self.route, dict(self.params)
        for page in self.pages.values(): self.stack.removeWidget(page); page.deleteLater()
        self.pages = {}; self.open(route or "home", push=False, **params)
    def open_item(self, item_id):
        if self.kb.get(item_id): self.open("item", id=item_id)
    def fade_to(self, page):
        self.stack.setCurrentWidget(page)
        if self.settings.reduce_motion: return
        effect = QGraphicsOpacityEffect(page); page.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", page); anim.setDuration(180); anim.setStartValue(0.0); anim.setEndValue(1.0); anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.finished.connect(lambda: page.setGraphicsEffect(None)); anim.start(QPropertyAnimation.DeleteWhenStopped)
    # -------------------------------------------------------------- search
    def run_search(self):
        q = self.search.text().strip()
        if q: self.open("search", q=q)
    def live_search(self):
        q = self.search.text().strip()
        if len(q) >= 2:
            if self.route == "search": self.pages["search"].show_route({"q": q}); self.params = {"q": q}
            else: self.open("search", q=q)
    # ------------------------------------------------------------ progress
    def mark_opened(self, item):
        new = self.progress.opened(item.kind, item.id, item.title(self.lang))
        self.announce(new); self.update_profile()
    def announce(self, achievements):
        from .desk.pages.home import achievement_title
        for key in achievements or []:
            self.toast.show_text("★  " + achievement_title(self.lang, key))
    # --------------------------------------------------------- notifications
    def upcoming(self, days=7):
        today = date.today(); out = []
        for when, day in self.kb.upcoming(today, 10):
            if (when - today).days <= days: out.append((when, day))
        return out
    def show_notifications(self):
        menu = QMenu(self); items = self.upcoming(14)
        if not items: menu.addAction(self.t("no_notifications")).setEnabled(False)
        for when, day in items:
            delta = (when - date.today()).days
            label_ = self.t("today") if delta == 0 else self.t("tomorrow") if delta == 1 else self.t("in_days", n=delta)
            action = menu.addAction(f"{day.title(self.lang)} · {label_}"); action.triggered.connect(lambda checked=False, i=day.id: self.open_item(i))
        menu.exec_(self.bell.mapToGlobal(QPoint(0, self.bell.height() + 4))) if hasattr(menu, "exec_") else menu.exec(self.bell.mapToGlobal(QPoint(0, self.bell.height() + 4)))
    # -------------------------------------------------------------- online
    def probe(self):
        if self.review or getattr(self, "_probing", False): return
        self._probing = True
        def done(result, error):
            self._probing = False; self.set_online(bool(result) and error is None)
        self.run_job(online_probe, done)
    def set_online(self, value):
        changed = value != self.online; self.online = bool(value); self.update_status(); self.companion.set_online(self.online)
        if changed and self.route in self.pages and hasattr(self.pages[self.route], "online_changed"): self.pages[self.route].online_changed(self.online)
    def maybe_auto_update(self):
        if self.review or not self.online or not self.settings.auto_update: return
        page = self.page("data")
        if hasattr(page, "auto_update"): page.auto_update()
    def open_url(self, url):
        if str(url).startswith(("https://", "http://")): QDesktopServices.openUrl(QUrl(url))
    # ------------------------------------------------------------- reading
    def voice_available(self):
        import shutil
        return bool(shutil.which("espeak-ng") or shutil.which("espeak"))
    def speak(self, text=None, lang=None):
        if not text: return
        if self.speaking: self.voice.stop_speaking(); self.speaking = False; return
        self.speaking = True
        self.run_job(lambda: self.voice.speak(text, lang or self.lang, self.settings.speech_rate), lambda r, e: setattr(self, "speaking", False))
    # ------------------------------------------------------------- settings
    def save_settings(self, new):
        changed_look = (new.language, new.theme, new.text_scale, new.follow_eduka_theme) != (self.settings.language, self.settings.theme, self.settings.text_scale, self.settings.follow_eduka_theme)
        for field in new.__dataclass_fields__: setattr(self.settings, field, getattr(new, field))
        if not self.review:
            try: self.settings.save()
            except OSError as e: self.toast.show_text(str(e))
        if changed_look: self.rebuild()
        else: self.update_profile(); self.companion.apply_preferences()
    def save_quietly(self):
        if not self.review:
            try: self.settings.save()
            except OSError: pass
    def change_outfit(self, outfit):
        from . import outfits
        if outfit not in outfits.OUTFITS: return
        self.settings.costume = outfit; self.save_quietly(); self.companion.apply_preferences(); self.avatar.setPixmap(self.atlas.pose_pixmap(outfit, 34))
    # -------------------------------------------------- assistant and system
    def open_from_assistant(self, route, value):
        """The Virtual Assistant asks for a page: an item, the map on a place, a search…"""
        self.reveal()
        item = self.kb.get(value) if value else None
        if route == "item" and item: self.open("item", id=item.id)
        elif route == "map" and item: self.open("map", **({"place": item.id} if item.kind == "place" else {"municipality": item.id}))
        elif route == "search" and value: self.open("search", q=value)
        elif route == "language" and value in ("words", "cards", "quiz"): self.open("language", tab=value)
        elif route: self.open(route)
    def activate_mode(self, mode):
        if mode == "virtual-start": return
        if mode == "desktop": self.reveal()
        elif mode == "settings": self.reveal(); self.open("settings")
        elif mode == "configure": self.open_configuration()
        elif mode == "virtual": self.companion.show_bubble() if self.settings.companion else self.open_configuration()
        elif mode == "reload": self.reload_settings()
        elif mode in {"enable", "disable"}:
            # Used by Eduka-Settings → Lafa-Configuration (the only place to switch it).
            self.settings.companion = mode == "enable"
            if not self.review: self.save_quietly()
            self.companion.apply_preferences(); self.companion.set_online(self.online)
            if mode == "disable" and not self.isVisible() and not self.tray and not self.review: self.exit_app()
    def open_configuration(self):
        """Lafa-Configuration lives in Eduka-Settings; Lafa's own Settings page is the fallback."""
        if not self.review and eduka.settings_page_available() and eduka.open_settings_page(): return
        self.reveal(); self.open("settings")
    def reload_settings(self):
        new = Settings.load()
        look = (new.language, new.theme, new.text_scale) != (self.settings.language, self.settings.theme, self.settings.text_scale)
        for field in new.__dataclass_fields__: setattr(self.settings, field, getattr(new, field))
        if look: self.rebuild()
        self.companion.apply_preferences(); self.companion.set_online(self.online)
    def setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable(): return
        self.tray = QSystemTrayIcon(self.windowIcon(), self); menu = QMenu()
        menu.addAction("Lafa Desktop", self.reveal); menu.addAction(self.t("nav_settings"), lambda: (self.reveal(), self.open("settings")))
        menu.addSeparator(); menu.addAction(self.t("close"), self.exit_app)
        self.tray.setContextMenu(menu); self.tray.activated.connect(lambda reason: self.reveal() if reason == QSystemTrayIcon.Trigger else None); self.tray.show()
    def reveal(self):
        self.showNormal(); self.raise_(); self.activateWindow()
    def closeEvent(self, event):
        # The Virtual Assistant keeps running while it is enabled; the window only hides.
        if self.settings.companion and not self.review:
            event.ignore(); self.hide(); return
        self.exit_app(); event.accept()
    def exit_app(self):
        self.voice.stop(); self.companion.hide()
        if self.tray: self.tray.hide()
        QApplication.instance().quit()

def first_name():
    import pwd
    try:
        gecos = pwd.getpwuid(os.getuid()).pw_gecos.split(",")[0].strip()
        return (gecos or os.environ.get("USER", "")).split()[0].capitalize() if (gecos or os.environ.get("USER")) else ""
    except (KeyError, IndexError, OSError):
        return ""

def main():
    parser = argparse.ArgumentParser(description="Lafa Desktop (Ensiklopédia Timór-Leste) and the Lafa Virtual Assistant")
    parser.add_argument("--review", action="store_true", help="Visual review; no network calls or saved settings")
    parser.add_argument("--version", action="version", version=f"Lafa {VERSION_LABEL}")
    roles = parser.add_mutually_exclusive_group()
    roles.add_argument("--window", action="store_true", help="Open Lafa Desktop (default)")
    roles.add_argument("--settings", action="store_true", help="Open Lafa's settings page")
    roles.add_argument("--virtual", action="store_true", help="Show the enabled virtual assistant, or open Settings")
    roles.add_argument("--virtual-enable", action="store_true", help="Enable the virtual assistant; used by Eduka-Settings")
    roles.add_argument("--virtual-disable", action="store_true", help="Disable the virtual assistant; used by Eduka-Settings")
    roles.add_argument("--configure", action="store_true", help="Open Lafa-Configuration in Eduka-Settings (or Lafa settings)")
    roles.add_argument("--reload", action="store_true", help="Re-read preferences saved by Eduka-Settings")
    roles.add_argument("--autostart", action="store_true", help="Session start: run only when the Virtual Assistant is enabled")
    args = parser.parse_args()
    eduka.prefer_xwayland()
    if args.autostart:
        startup = Settings.load()
        if not (startup.companion and startup.start_with_session): return 0
    mode = ("virtual-start" if args.autostart else "configure" if args.configure else "settings" if args.settings else "virtual" if args.virtual
            else "enable" if args.virtual_enable else "disable" if args.virtual_disable else "reload" if args.reload else "desktop")
    prepare_application()
    app = QApplication(sys.argv); app.setApplicationName("LAFA"); app.setOrganizationName("Edukasaun"); app.setStyle("Fusion")
    theme.load_fonts(); app.setFont(theme.app_font())
    lock = None
    if not args.review:
        config_path().parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        lock = QLockFile(str(config_path().parent / "instance.lock")); lock.setStaleLockTime(0)
        if not lock.tryLock(100):
            if mode == "virtual-start": return 0  # already running
            if not activate_existing(server_name(config_path().parent), mode):
                QMessageBox.information(None, "Lafa", "Lafa is starting. Try the app icon again in a few seconds.")
            return 0
    if mode == "reload" and lock:
        lock.unlock(); return 0  # Not running: preferences load at the next start.
    app.setQuitOnLastWindowClosed(args.review)
    window = Window(review=args.review)
    if mode in ("desktop", "settings") or args.review: window.show()
    window.activate_mode(mode)
    if mode == "disable" and not args.review:
        lock.unlock(); return 0
    activation = None
    if not args.review:
        try:
            activation = ActivationServer(server_name(config_path().parent), window); activation.activated.connect(window.activate_mode); app.aboutToQuit.connect(activation.close)
        except RuntimeError: pass
    app.aboutToQuit.connect(window.voice.stop)
    code = run(app)
    if lock: lock.unlock()
    if BINDING == "PyQt5":
        # PyQt5 may crash while Python destroys Qt objects at shutdown; state is already saved.
        sys.stdout.flush(); sys.stderr.flush(); os._exit(int(code or 0))
    return code

if __name__ == "__main__":
    raise SystemExit(main())
