"""AI Hub: sign in to the AI services you already use, inside LAFA.

Inspired by Noi (github.com/lencx/noi): each AI website opens in its own tab
with a private, persistent LAFA profile, so you sign in once (Google, Microsoft,
e-mail…) and stay signed in. "Ask the selected AIs" types the same question
into every selected tab and presses send, so you can compare answers.

* Sign-in happens on the AI company's own page; LAFA never sees passwords,
  never reads cookies or tokens and never copies answers out of the pages.
* Only HTTPS pages open; camera, microphone, location and notifications are
  refused. Links to other sites open in the normal web browser.
* Without Qt WebEngine (Debian: python3-pyqt5.qtwebengine) the services open
  in the web browser instead.
"""
from dataclasses import dataclass
import json
import os
from pathlib import Path

from . import qt
from .qt import (Qt, Signal, QUrl, QTimer, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget,
                 QLabel, QLineEdit, QPushButton, QFrame, QDesktopServices)

@dataclass(frozen=True)
class Site:
    key: str
    name: str
    url: str
    icon: str
    note: dict
    input: str = ""      # CSS selector of the prompt box (generic fallbacks are tried too)
    send: str = ""       # CSS selector of the send button (Enter is pressed when missing)
    hosts: tuple = ()    # extra hosts used for sign-in

def N(en, id_, pt, tet): return {"en": en, "id": id_, "pt": pt, "tet": tet}

GOOGLE = ("accounts.google.com", "google.com", "gstatic.com", "googleusercontent.com", "youtube.com")
MICROSOFT = ("login.live.com", "login.microsoftonline.com", "microsoft.com", "live.com", "bing.com")
SITES = [
    Site("gemini", "Gemini", "https://gemini.google.com/app", "✦", N("Google · free with a Google account", "Google · gratis dengan akun Google", "Google · grátis com conta Google", "Google · gratuitu ho konta Google"),
         "rich-textarea div[contenteditable='true'], div.ql-editor", "button.send-button, button[aria-label*='Send' i], button[aria-label*='Kirim' i]", GOOGLE),
    Site("chatgpt", "ChatGPT", "https://chatgpt.com/", "◎", N("OpenAI · free account", "OpenAI · akun gratis", "OpenAI · conta grátis", "OpenAI · konta gratuitu"),
         "#prompt-textarea", "button[data-testid='send-button'], #composer-submit-button", ("auth.openai.com", "openai.com") + GOOGLE + MICROSOFT),
    Site("claude", "Claude", "https://claude.ai/new", "✳", N("Anthropic · free account", "Anthropic · akun gratis", "Anthropic · conta grátis", "Anthropic · konta gratuitu"),
         "div[contenteditable='true']", "button[aria-label*='Send' i]", ("anthropic.com",) + GOOGLE),
    Site("copilot", "Copilot", "https://copilot.microsoft.com/", "❖", N("Microsoft · free", "Microsoft · gratis", "Microsoft · grátis", "Microsoft · gratuitu"),
         "textarea", "button[aria-label*='Submit' i], button[title*='Submit' i]", MICROSOFT),
    Site("deepseek", "DeepSeek", "https://chat.deepseek.com/", "◈", N("Free · strong at maths", "Gratis · kuat di matematika", "Grátis · forte em matemática", "Gratuitu · di'ak ba matemátika"),
         "textarea", "", GOOGLE),
    Site("perplexity", "Perplexity", "https://www.perplexity.ai/", "✺", N("Answers with web sources", "Jawaban dengan sumber web", "Respostas com fontes da web", "Resposta ho fonte web"),
         "textarea, div[contenteditable='true']", "button[aria-label*='Submit' i]", GOOGLE),
    Site("mistral", "Le Chat", "https://chat.mistral.ai/chat", "▲", N("Mistral · European, free", "Mistral · Eropa, gratis", "Mistral · europeu, grátis", "Mistral · Europa, gratuitu"),
         "textarea, div[contenteditable='true']", "button[type='submit']", GOOGLE + MICROSOFT),
    Site("qwen", "Qwen", "https://chat.qwen.ai/", "◐", N("Alibaba · free, many languages", "Alibaba · gratis, banyak bahasa", "Alibaba · grátis, muitas línguas", "Alibaba · gratuitu, lian barak"),
         "textarea", "button#send-message-button, button[type='submit']", GOOGLE),
    Site("kimi", "Kimi", "https://www.kimi.com/", "◑", N("Moonshot · long documents", "Moonshot · dokumen panjang", "Moonshot · documentos longos", "Moonshot · dokumentu naruk"),
         "div[contenteditable='true'], textarea", "", GOOGLE),
    Site("huggingchat", "HuggingChat", "https://huggingface.co/chat/", "🤗", N("Open-source models", "Model open-source", "Modelos de código aberto", "Modelu open-source"),
         "textarea", "button[type='submit']", ("huggingface.co",)),
    Site("grok", "Grok", "https://grok.com/", "✕", N("xAI · free account", "xAI · akun gratis", "xAI · conta grátis", "xAI · konta gratuitu"),
         "textarea, div[contenteditable='true']", "button[type='submit']", ("x.ai", "x.com") + GOOGLE),
    Site("meta", "Meta AI", "https://www.meta.ai/", "∞", N("Meta · free", "Meta · gratis", "Meta · grátis", "Meta · gratuitu"),
         "textarea, div[contenteditable='true']", "", ("facebook.com", "meta.com", "instagram.com")),
    Site("notebooklm", "NotebookLM", "https://notebooklm.google.com/", "📓", N("Google · study your documents", "Google · pelajari dokumenmu", "Google · estuda os teus documentos", "Google · estuda ita-nia dokumentu"), "", "", GOOGLE),
    Site("aistudio", "AI Studio", "https://aistudio.google.com/apikey", "🔑", N("Google · free Gemini key for LAFA", "Google · kunci Gemini gratis untuk LAFA", "Google · chave Gemini grátis para o LAFA", "Google · xave Gemini gratuitu ba LAFA"), "", "", GOOGLE),
]
BY_KEY = {s.key: s for s in SITES}
ASKABLE = [s.key for s in SITES if s.key not in {"notebooklm", "aistudio"}]

def inject_script(prompt, site):
    """JavaScript that types `prompt` into the page's prompt box and sends it."""
    return """(function(text, inputSel, sendSel){
  function find(sel){ if(!sel) return null; try { var all=document.querySelectorAll(sel); for (var i=all.length-1;i>=0;i--){ var e=all[i]; if(e.offsetParent!==null) return e; } } catch(e){} return null; }
  var box = find(inputSel) || find("textarea") || find("div[contenteditable='true']") || find("input[type='text']");
  if(!box) return "no-input";
  box.focus();
  if (box.isContentEditable) {
    document.execCommand('selectAll', false, null);
    document.execCommand('insertText', false, text);
  } else {
    var proto = box.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto, 'value').set.call(box, text);
  }
  box.dispatchEvent(new InputEvent('input', {bubbles:true, data:text, inputType:'insertText'}));
  setTimeout(function(){
    var button = find(sendSel) || find("button[aria-label*='Send' i]") || find("button[type='submit']");
    if (button && !button.disabled) { button.click(); return; }
    ['keydown','keypress','keyup'].forEach(function(t){ box.dispatchEvent(new KeyboardEvent(t, {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true})); });
  }, 450);
  return "sent";
})(%s, %s, %s);""" % (json.dumps(prompt), json.dumps(site.input), json.dumps(site.send))

def allowed_host(site, host):
    host = (host or "").lower(); main = qt_host(site.url)
    hosts = (main,) + site.hosts
    return any(host == h or host.endswith("." + h) for h in hosts) or (main.count(".") >= 2 and host.endswith("." + main.split(".", 1)[1]))

def qt_host(url):
    from urllib.parse import urlsplit
    return (urlsplit(url).hostname or "").lower()

def chrome_agent(default):
    """A normal Chrome user agent: some sign-in pages refuse 'QtWebEngine'."""
    import re
    match = re.search(r"Chrome/([\d.]+)", default or "")
    version = match.group(1) if match else "120.0.0.0"
    return f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"

def profile_folder():
    root = os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return Path(root) / "lafa" / "aihub"

if qt.WEBENGINE:
    from .qt import QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings

    class HubPage(QWebEnginePage):
        """Keeps each tab on its AI service; everything else opens in the browser."""
        def __init__(self, site, profile, hub, view):
            # The page belongs to its view, so it is deleted before the profile.
            super().__init__(profile, view); self.site = site; self.hub = hub; self.popups = []
            self.featurePermissionRequested.connect(self.refuse)
        def refuse(self, origin, feature):
            self.setFeaturePermission(origin, feature, QWebEnginePage.PermissionDeniedByUser)
        def acceptNavigationRequest(self, url, kind, main_frame):
            if url.scheme() in ("about", "data", "blob"): return True
            if url.scheme() != "https": return False
            if not main_frame or allowed_host(self.site, url.host()): return True
            QDesktopServices.openUrl(url); return False
        def createWindow(self, kind):
            # Sign-in pop-ups (Google, Microsoft) open in a small LAFA window.
            view = QWebEngineView(); page = HubPage(self.site, self.profile(), self.hub, view); view.setPage(page)
            view.setAttribute(Qt.WA_DeleteOnClose); view.resize(520, 680); view.setWindowTitle("LAFA · " + self.site.name)
            page.windowCloseRequested.connect(view.close); view.show(); self.popups.append(view)
            return page

class AIHub(QWidget):
    """The web tabs and the 'ask every AI' bar."""
    asked = Signal(list)
    def __init__(self, lang="en", texts=None, parent=None, folder=None):
        super().__init__(parent)
        self.lang = lang; self.texts = texts or {}; self.views = {}; self.pending = {}; self.loaded = set()
        self.folder = Path(folder) if folder else profile_folder(); self.profile = None
        outer = QHBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(12)
        self.list = QListWidget(); self.list.setObjectName("aihublist"); self.list.setFixedWidth(270); self.list.setWordWrap(True)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        for site in SITES:
            item = QListWidgetItem(f"{site.icon}  {site.name}\n{site.note.get(lang, site.note['en'])}"); item.setData(Qt.UserRole, site.key); item.setToolTip(site.url)
            if site.key in ASKABLE:
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable); item.setCheckState(Qt.Checked if site.key in ("gemini", "chatgpt") else Qt.Unchecked)
            self.list.addItem(item)
        self.list.currentItemChanged.connect(lambda item, _: item and self.open_site(item.data(Qt.UserRole)))
        outer.addWidget(self.list)
        right = QVBoxLayout(); right.setSpacing(8); outer.addLayout(right, 1)
        bar = QHBoxLayout()
        self.title = QLabel(self.t("aihub_pick")); self.title.setObjectName("aihubtitle"); bar.addWidget(self.title, 1)
        self.back_button = self.small("←", self.back); self.reload_button = self.small("⟳", self.reload); self.browser_button = self.small("↗", self.open_in_browser)
        for b, tip in ((self.back_button, "back"), (self.reload_button, "reload"), (self.browser_button, "open_browser")):
            b.setToolTip(self.t(tip)); bar.addWidget(b)
        right.addLayout(bar)
        self.stack = QStackedWidget(); right.addWidget(self.stack, 1)
        self.placeholder = QLabel(self.t("aihub_intro") if qt.WEBENGINE else self.t("aihub_no_webengine")); self.placeholder.setWordWrap(True)
        self.placeholder.setAlignment(Qt.AlignCenter); self.placeholder.setObjectName("aihubintro"); self.stack.addWidget(self.placeholder)
        ask = QHBoxLayout()
        self.prompt = QLineEdit(); self.prompt.setMaxLength(4000); self.prompt.setPlaceholderText(self.t("aihub_ask_hint")); self.prompt.returnPressed.connect(self.ask_selected)
        self.ask_button = QPushButton(self.t("aihub_ask")); self.ask_button.setObjectName("primary"); self.ask_button.clicked.connect(self.ask_selected)
        ask.addWidget(self.prompt, 1); ask.addWidget(self.ask_button); right.addLayout(ask)
        self.status = QLabel(""); self.status.setObjectName("muted"); self.status.setWordWrap(True); right.addWidget(self.status)
    def t(self, key): return self.texts.get(key, key)
    def small(self, text, slot):
        b = QPushButton(text); b.setFixedSize(38, 34); b.clicked.connect(slot); return b
    def selected(self):
        return [self.list.item(i).data(Qt.UserRole) for i in range(self.list.count())
                if self.list.item(i).flags() & Qt.ItemIsUserCheckable and self.list.item(i).checkState() == Qt.Checked]
    def make_profile(self):
        if self.profile is None:
            self.folder.mkdir(parents=True, exist_ok=True)
            try: os.chmod(self.folder, 0o700)
            except OSError: pass
            # One profile for the whole app; it outlives every page.
            self.profile = QWebEngineProfile("lafa-ai-hub", QApplication.instance())
            self.profile.setPersistentStoragePath(str(self.folder / "storage")); self.profile.setCachePath(str(self.folder / "cache"))
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
            self.profile.setHttpUserAgent(chrome_agent(self.profile.httpUserAgent()))
            settings = self.profile.settings()
            for name in ("LocalContentCanAccessRemoteUrls", "LocalContentCanAccessFileUrls"):
                attribute = getattr(QWebEngineSettings, name, None)
                if attribute is not None: settings.setAttribute(attribute, False)
            QApplication.instance().aboutToQuit.connect(self.release)
        return self.profile
    def release(self):
        """Delete the web pages before their profile when LAFA quits."""
        from .qt import QEvent
        for view in self.views.values():
            for popup in getattr(view.page(), "popups", []):
                try: popup.page().deleteLater()
                except RuntimeError: pass
            try: view.page().deleteLater()
            except RuntimeError: pass
        QApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        if self.profile is not None: self.profile.deleteLater(); QApplication.sendPostedEvents(None, QEvent.DeferredDelete); self.profile = None
        self.views = {}
    def view(self, key):
        """The web view of a service, created on first use (lazy: fast start)."""
        if key not in self.views:
            site = BY_KEY[key]; view = QWebEngineView(); page = HubPage(site, self.make_profile(), self, view); view.setPage(page)
            view.loadFinished.connect(lambda ok, k=key: self.page_loaded(k, ok)); view.load(QUrl(site.url))
            self.views[key] = view; self.stack.addWidget(view)
        return self.views[key]
    def open_site(self, key):
        site = BY_KEY.get(key)
        if not site: return
        self.title.setText(f"{site.icon}  {site.name}")
        if not qt.WEBENGINE:
            QDesktopServices.openUrl(QUrl(site.url)); self.status.setText(self.t("aihub_opened_browser").replace("{name}", site.name)); return
        self.stack.setCurrentWidget(self.view(key))
        for i in range(self.list.count()):
            if self.list.item(i).data(Qt.UserRole) == key and self.list.currentRow() != i: self.list.setCurrentRow(i)
    def page_loaded(self, key, ok):
        if not ok: self.status.setText(self.t("aihub_load_failed").replace("{name}", BY_KEY[key].name)); return
        self.loaded.add(key)
        prompt = self.pending.pop(key, None)
        # Give single-page apps a moment to draw their prompt box.
        if prompt: QTimer.singleShot(1800, lambda: self.inject(key, prompt))
    def inject(self, key, prompt):
        view = self.views.get(key)
        if view: view.page().runJavaScript(inject_script(prompt, BY_KEY[key]))
    def ask(self, prompt, keys=None):
        """Type the prompt into each selected AI tab and send it."""
        prompt = prompt.strip()[:4000]; keys = [k for k in (keys or self.selected()) if k in BY_KEY]
        if not prompt or not keys: return []
        if not qt.WEBENGINE:
            QDesktopServices.openUrl(QUrl(BY_KEY[keys[0]].url)); self.status.setText(self.t("aihub_no_webengine")); return keys
        for key in keys:
            self.view(key)
            if key in self.loaded: self.inject(key, prompt)
            else: self.pending[key] = prompt
        self.open_site(keys[0]); self.asked.emit(keys)
        self.status.setText(self.t("aihub_sent").replace("{names}", ", ".join(BY_KEY[k].name for k in keys)))
        return keys
    def ask_selected(self):
        text = self.prompt.text().strip()
        if not text:
            self.status.setText(self.t("type_first")); self.prompt.setFocus(); return
        if not self.selected():
            self.status.setText(self.t("aihub_choose")); return
        if self.ask(text): self.prompt.clear()
    def current_view(self):
        widget = self.stack.currentWidget()
        return widget if widget is not self.placeholder else None
    def back(self):
        view = self.current_view()
        if view: view.back()
    def reload(self):
        view = self.current_view()
        if view: view.reload()
    def open_in_browser(self):
        view = self.current_view()
        item = self.list.currentItem()
        url = view.url() if view else (QUrl(BY_KEY[item.data(Qt.UserRole)].url) if item else None)
        if url: QDesktopServices.openUrl(url)
