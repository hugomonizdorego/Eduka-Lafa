"""Offline no atualiza: download texts and free pictures for use without
internet, check for new Lafa content, refresh the World Bank data, and see or
clear what is stored on this computer."""
from ...qt import Qt, Signal, QObject, QRunnable, QTimer, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QProgressBar, QMessageBox
from ... import kb, sync
from ...net import NetworkError
from ..texts import extend
from ..widgets import Card, ClayIcon, Pill, ResponsiveGrid, label, button, scroll, section_title, clear_layout

extend({
    "data_title": ("Offline no atualizasaun", "Offline e atualizações", "Luring dan pembaruan", "Offline and updates"),
    "data_sub": ("Ensiklopédia, mapa, kuis no liafuan hotu servisu ona la ho internet. Ho internet, Lafa bele download testu Wikipedia no foto ho lisensa livre, no atualiza dadus.",
                 "A enciclopédia, o mapa, os quizzes e as palavras já funcionam sem internet. Com internet, o Lafa pode descarregar textos da Wikipédia e fotos de licença livre, e atualizar os dados.",
                 "Ensiklopedia, peta, kuis dan kosakata sudah berfungsi tanpa internet. Dengan internet, Lafa dapat mengunduh teks Wikipedia dan foto berlisensi bebas, serta memperbarui data.",
                 "The encyclopedia, map, quizzes and words already work without internet. Online, Lafa can download Wikipedia texts and free-licence photos, and update the data."),
    "offline_pack": ("Pakote offline", "Pacote offline", "Paket luring", "Offline pack"),
    "offline_pack_text": ("Download introdusaun Wikipedia (Tetun, Portugés, Indonéziu, Inglés) ba artigu hotu, no foto ida ba kada artigu (só lisensa livre: CC0, domíniu públiku, CC BY, CC BY-SA).",
                          "Descarrega a introdução da Wikipédia (tétum, português, indonésio, inglês) de cada artigo e uma foto por artigo (só licenças livres: CC0, domínio público, CC BY, CC BY-SA).",
                          "Mengunduh pengantar Wikipedia (Tetun, Portugis, Indonesia, Inggris) untuk setiap artikel dan satu foto per artikel (hanya lisensi bebas: CC0, domain publik, CC BY, CC BY-SA).",
                          "Downloads the Wikipedia introduction (Tetun, Portuguese, Indonesian, English) of every article and one photo per article (free licences only: CC0, public domain, CC BY, CC BY-SA)."),
    "with_photos": ("Download foto mós", "Descarregar também fotos", "Unduh foto juga", "Also download photos"),
    "download_all": ("Download hotu", "Descarregar tudo", "Unduh semua", "Download everything"),
    "cancel": ("Kansela", "Cancelar", "Batal", "Cancel"),
    "content_updates": ("Konteúdu foun", "Conteúdo novo", "Konten baru", "New content"),
    "content_updates_text": ("Lafa buka artigu, korresaun no liafuan foun iha repozitóriu públiku projetu nian (GitHub). Ficheiru hotu verifika ho SHA-256.",
                             "O Lafa procura artigos, correções e palavras novas no repositório público do projeto (GitHub). Cada ficheiro é verificado com SHA-256.",
                             "Lafa mencari artikel, koreksi dan kata baru di repositori publik proyek (GitHub). Setiap berkas diperiksa dengan SHA-256.",
                             "Lafa looks for new articles, corrections and words in the project's public repository (GitHub). Every file is checked with SHA-256."),
    "check_now": ("Buka agora", "Verificar agora", "Periksa sekarang", "Check now"),
    "install_updates": ("Instala {n} atualizasaun", "Instalar {n} atualizações", "Pasang {n} pembaruan", "Install {n} updates"),
    "up_to_date": ("Konteúdu atualizadu ona (versaun {v}).", "O conteúdo está atualizado (versão {v}).", "Konten sudah terbaru (versi {v}).", "Content is up to date (version {v})."),
    "updates_found": ("Iha ficheiru {n} foun (versaun {v}).", "Há {n} ficheiros novos (versão {v}).", "Ada {n} berkas baru (versi {v}).", "{n} new files (version {v})."),
    "updates_done": ("Atualiza ona: ficheiru {n}.", "Atualizado: {n} ficheiros.", "Diperbarui: {n} berkas.", "Updated: {n} files."),
    "world_bank": ("Dadus Banku Mundiál", "Dados do Banco Mundial", "Data Bank Dunia", "World Bank data"),
    "world_bank_text": ("Populasaun, ekonomia, saúde, eletrisidade no internet: seri foun husi data.worldbank.org (CC BY 4.0).", "População, economia, saúde, eletricidade e internet: séries novas de data.worldbank.org (CC BY 4.0).",
                        "Penduduk, ekonomi, kesehatan, listrik dan internet: seri terbaru dari data.worldbank.org (CC BY 4.0).", "Population, economy, health, electricity and internet: fresh series from data.worldbank.org (CC BY 4.0)."),
    "refresh_data": ("Atualiza dadus", "Atualizar dados", "Perbarui data", "Refresh data"),
    "stored": ("Rai iha komputadór ne'e", "Guardado neste computador", "Tersimpan di komputer ini", "Stored on this computer"),
    "stored_text": ("Testu {e} · Foto {p} · {mb} MB", "{e} textos · {p} fotos · {mb} MB", "{e} teks · {p} foto · {mb} MB", "{e} texts · {p} photos · {mb} MB"),
    "last_download": ("Download ikus: {d}", "Última transferência: {d}", "Unduhan terakhir: {d}", "Last download: {d}"),
    "never": ("seidauk", "nunca", "belum pernah", "never"),
    "clear_data": ("Hamoos dadus download", "Apagar dados descarregados", "Hapus data unduhan", "Clear downloaded data"),
    "clear_confirm": ("Hamoos testu no foto download hotu? Konteúdu Lafa nian la lakon.", "Apagar todos os textos e fotos descarregados? O conteúdo do Lafa fica.",
                      "Hapus semua teks dan foto unduhan? Konten Lafa tetap ada.", "Delete all downloaded texts and photos? Lafa's own content stays."),
    "auto_update": ("Buka atualizasaun automátiku bainhira iha internet", "Procurar atualizações automaticamente com internet", "Periksa pembaruan otomatis saat ada internet", "Check for updates automatically when online"),
    "need_online": ("Presiza internet ba ne'e.", "É preciso internet para isto.", "Ini memerlukan internet.", "This needs internet."),
    "done_download": ("Remata: testu {t}, foto {p}.", "Concluído: {t} textos, {p} fotos.", "Selesai: {t} teks, {p} foto.", "Done: {t} texts, {p} photos."),
    "errors_some": ("Problema balun: {e}", "Alguns problemas: {e}", "Beberapa masalah: {e}", "Some problems: {e}"),
    "content_version": ("Versaun konteúdu: {v}", "Versão do conteúdo: {v}", "Versi konten: {v}", "Content version: {v}"),
    "indicators_done": ("Indikadór {n} atualiza ona.", "{n} indicadores atualizados.", "{n} indikator diperbarui.", "{n} indicators updated."),
})

class Signals(QObject):
    progress = Signal(int, int, str)
    done = Signal(object, object)

class Task(QRunnable):
    """A background job with progress; `cancel()` stops it between steps."""
    def __init__(self, fn):
        super().__init__(); self.fn = fn; self.signals = Signals(); self.stop = False; self.setAutoDelete(False)
    def cancel(self): self.stop = True
    def run(self):
        try: result, error = self.fn(lambda d, n, text="": self.signals.progress.emit(int(d), int(n), str(text)), lambda: self.stop), None
        except Exception as e: result, error = None, e
        try: self.signals.done.emit(result, error)
        except RuntimeError: pass

class DataPage(QWidget):
    route = "data"
    def __init__(self, win):
        super().__init__(); self.win = win; self.task = None; self.pending = []; self.remote = None; self.message = ""
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(16)
        outer.addWidget(scroll(self.body))
    def show_route(self, params): self.render()
    def online_changed(self, online): self.render()
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; store = getattr(win, "store", None); busy = self.task is not None
        head = Card(20, 24); row = QHBoxLayout(); row.setSpacing(14); row.addWidget(ClayIcon("cloud-download", "lilac", 64))
        c = QVBoxLayout(); c.setSpacing(2); c.addWidget(label(t("data_title"), "h1")); c.addWidget(label(t("data_sub"), "muted", wrap=True)); row.addLayout(c, 1)
        row.addWidget(Pill(t("online") if win.online else t("offline"), "green" if win.online else "slate"), 0, Qt.AlignTop); head.box.addLayout(row)
        if self.message: head.box.addWidget(label(self.message, "body", wrap=True))
        self.bar = QProgressBar(); self.bar.setVisible(busy); self.status = label("", "caption"); self.status.setVisible(busy)
        head.box.addWidget(self.bar); head.box.addWidget(self.status)
        if busy: head.box.addWidget(button(t("cancel"), self.cancel, "ghost", "close"), 0, Qt.AlignLeft)
        self.col.addWidget(head)
        grid = ResponsiveGrid(330, 2, 16)
        # Offline pack.
        pack = Card(18, 24); pack.box.addLayout(section_title(t("offline_pack"))); pack.box.addWidget(label(t("offline_pack_text"), "muted", wrap=True))
        self.photos = QCheckBox(t("with_photos")); self.photos.setChecked(True); pack.box.addWidget(self.photos)
        b = button(t("download_all"), self.download, "primary", "download"); b.setEnabled(win.online and not busy and store is not None); pack.box.addWidget(b, 0, Qt.AlignLeft)
        if not win.online: pack.box.addWidget(label(t("need_online"), "caption"))
        pack.box.addStretch(); grid.add(pack)
        # Content updates.
        upd = Card(18, 24); upd.box.addLayout(section_title(t("content_updates"))); upd.box.addWidget(label(t("content_updates_text"), "muted", wrap=True))
        upd.box.addWidget(label(t("content_version", v=win.kb.content_version or "—"), "caption"))
        if self.remote is not None:
            n = len(self.remote["changed"])
            upd.box.addWidget(label(t("updates_found", n=n, v=self.remote["version"]) if n else t("up_to_date", v=self.remote["version"] or win.kb.content_version), "body", wrap=True))
        rowb = QHBoxLayout()
        b1 = button(t("check_now"), self.check, None, "refresh"); b1.setEnabled(win.online and not busy); rowb.addWidget(b1)
        if self.remote and self.remote["changed"]:
            b2 = button(t("install_updates", n=len(self.remote["changed"])), self.install, "primary", "download"); b2.setEnabled(win.online and not busy); rowb.addWidget(b2)
        rowb.addStretch(); upd.box.addLayout(rowb)
        auto = QCheckBox(t("auto_update")); auto.setChecked(bool(win.settings.auto_update)); auto.toggled.connect(self.set_auto); upd.box.addWidget(auto)
        upd.box.addStretch(); grid.add(upd)
        # World Bank.
        wb = Card(18, 24); wb.box.addLayout(section_title(t("world_bank"))); wb.box.addWidget(label(t("world_bank_text"), "muted", wrap=True))
        years = [max((y for y, _ in i.get("series", [])), default=0) for i in win.kb.indicators]
        if years: wb.box.addWidget(label(t("data_year", year=max(years)), "caption"))
        b3 = button(t("refresh_data"), self.indicators, None, "chart"); b3.setEnabled(win.online and not busy); wb.box.addWidget(b3, 0, Qt.AlignLeft)
        wb.box.addStretch(); grid.add(wb)
        # Storage.
        st = Card(18, 24); st.box.addLayout(section_title(t("stored")))
        if store:
            s = store.stats(); st.box.addWidget(label(t("stored_text", e=s["extracts"], p=s["photos"], mb=f"{s['bytes'] / 1e6:.1f}"), "h3"))
            st.box.addWidget(label(t("last_download", d=store.get_meta("offline_download") or t("never")), "caption"))
            b4 = button(t("clear_data"), self.clear, "ghost", "close"); b4.setEnabled(not busy); st.box.addWidget(b4, 0, Qt.AlignLeft)
        st.box.addStretch(); grid.add(st)
        self.col.addWidget(grid); self.col.addStretch()
    # ---------------------------------------------------------------- jobs
    def run(self, fn, done):
        if self.task is not None: return
        self.task = Task(fn); self.task.signals.progress.connect(self.on_progress)
        self.task.signals.done.connect(lambda result, error: self.finished(done, result, error))
        self.message = ""; self.render(); self.win.pool.start(self.task)
    def on_progress(self, done, total, text):
        if getattr(self, "bar", None) is None: return
        try: self.bar.setMaximum(max(1, total)); self.bar.setValue(done); self.status.setText(text)
        except RuntimeError: pass
    def finished(self, done, result, error):
        self.task = None
        if error is not None: self.message = str(error) if isinstance(error, NetworkError) else f"{type(error).__name__}: {error}"
        else:
            try: done(result)
            except Exception as e: self.message = str(e)
        self.render()
    def cancel(self):
        if self.task: self.task.cancel()
    def download(self):
        win = self.win; photos = self.photos.isChecked()
        def done(r):
            self.message = win.t("done_download", t=r["texts"], p=r["pictures"]) + ("  " + win.t("errors_some", e="; ".join(r["errors"][:3])) if r["errors"] else "")
        self.run(lambda progress, cancelled: sync.download_offline(win.kb, win.store, photos=photos, progress=progress, cancelled=cancelled), done)
    def check(self):
        win = self.win
        def done(r): self.remote = r
        self.run(lambda progress, cancelled: sync.check_updates(kb.ASSETS, win.folder / "updates", win.kb.content_version), done)
    def install(self):
        win = self.win; changed = list(self.remote["changed"]) if self.remote else []
        def done(r):
            self.message = win.t("updates_done", n=len(r["saved"])) + ("  " + win.t("errors_some", e="; ".join(r["errors"][:3])) if r["errors"] else "")
            self.remote = None
            if r["saved"]: win.reload_content()
        self.run(lambda progress, cancelled: sync.apply_updates(kb.ASSETS, win.folder / "updates", changed, progress, cancelled), done)
    def indicators(self):
        win = self.win
        def done(r):
            self.message = win.t("indicators_done", n=r["indicators"]) + ("  " + win.t("errors_some", e="; ".join(r["errors"][:3])) if r["errors"] else "")
            if r["indicators"]: win.reload_content()
        self.run(lambda progress, cancelled: sync.update_indicators(win.kb, win.folder / "updates", progress, cancelled), done)
    def auto_update(self):
        """Called by the window every 30 minutes when online and allowed: check quietly, install content updates."""
        if self.task is not None or self.win.review: return
        win = self.win; last = win.store.get_meta("auto_check") if getattr(win, "store", None) else ""
        import time
        if last and time.time() - float(last or 0) < 24 * 3600: return
        def done(r):
            if win.store: win.store.set_meta("auto_check", time.time())
            if r["changed"] and r["newer"]:
                self.remote = r; self.install()
        self.run(lambda progress, cancelled: sync.check_updates(kb.ASSETS, win.folder / "updates", win.kb.content_version), done)
    def clear(self):
        win = self.win
        if QMessageBox.question(self, win.t("clear_data"), win.t("clear_confirm")) != QMessageBox.Yes: return
        try: win.store.clear()
        except OSError as e: self.message = str(e)
        self.render()
    def set_auto(self, on): self.win.settings.auto_update = bool(on); self.win.save_quietly()
    def retranslate(self): self.render()
