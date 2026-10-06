"""Offline Edukasaun OS help: curated guides, safe tool launchers, system check.

Edukasaun OS is Debian-based with LXQt / Eduka-Desktop. Guides describe the
usual menu paths; exact names can differ between OS builds, so every guide also
offers an "Open" action for a fixed allowlist of desktop tools. LAFA never runs
a shell, never uses sudo and never changes system settings by itself.
"""
from dataclasses import dataclass, field
import os
import re
import shutil
import time
import unicodedata
from pathlib import Path

@dataclass
class Guide:
    key: str
    icon: str
    title: dict
    steps: dict
    keywords: tuple
    tools: tuple = ()
    def text(self, lang):
        lang = lang if lang in self.title else "en"
        lines = [self.icon + "  " + self.title[lang]]
        lines += [f"{i}. {step}" for i, step in enumerate(self.steps[lang], 1)]
        return "\n".join(lines)

def G(key, icon, keywords, tools, en, id_, pt, tet):
    return Guide(key, icon, {"en": en[0], "id": id_[0], "pt": pt[0], "tet": tet[0]},
                 {"en": en[1], "id": id_[1], "pt": pt[1], "tet": tet[1]}, tuple(keywords), tuple(tools))

GUIDES = [
G("wifi", "📶", ["wifi", "wi-fi", "wireless", "internet", "network", "jaringan", "rede", "koneksaun", "hotspot", "sinyal"],
  ["nm-connection-editor", "cmst", "connman-gtk"],
  ("Connect to Wi-Fi", ["Click the network icon on the Eduka-Panel (bottom-right, near the clock).", "Choose your Wi-Fi name from the list.", "Type the Wi-Fi password and press Connect.", "No icon? Open the network tool with the button below."]),
  ("Menyambung Wi-Fi", ["Klik ikon jaringan di Eduka-Panel (kanan bawah, dekat jam).", "Pilih nama Wi-Fi dari daftar.", "Ketik kata sandi Wi-Fi lalu tekan Sambungkan.", "Ikon tidak ada? Buka alat jaringan dengan tombol di bawah."]),
  ("Ligar ao Wi-Fi", ["Clique no ícone de rede no Eduka-Panel (canto inferior direito, junto ao relógio).", "Escolha o nome do Wi-Fi na lista.", "Escreva a palavra-passe e prima Ligar.", "Sem ícone? Abra a ferramenta de rede com o botão abaixo."]),
  ("Liga ba Wi-Fi", ["Klik ikone rede iha Eduka-Panel (sorin loos-kraik, besik relójiu).", "Hili naran Wi-Fi iha lista.", "Hakerek password Wi-Fi no klik Liga.", "Ikone la iha? Loke ferramenta rede ho butaun iha okos."])),
G("sound", "🔊", ["sound", "audio", "volume", "speaker", "suara", "som", "lian", "headphone", "microphone", "mikrofon", "mic"],
  ["pavucontrol-qt", "pavucontrol", "lxqt-config-sound"],
  ("Fix sound and volume", ["Click the speaker icon on the Eduka-Panel and raise the volume.", "Make sure the sound is not muted.", "Open the sound mixer below to choose the right speaker or microphone.", "Headphones: unplug and plug them in again, then choose them in the mixer."]),
  ("Memperbaiki suara dan volume", ["Klik ikon speaker di Eduka-Panel dan naikkan volume.", "Pastikan suara tidak dibisukan (mute).", "Buka mixer suara di bawah untuk memilih speaker atau mikrofon yang benar.", "Headphone: cabut lalu colok lagi, kemudian pilih di mixer."]),
  ("Corrigir som e volume", ["Clique no ícone do altifalante no Eduka-Panel e aumente o volume.", "Confirme que o som não está silenciado.", "Abra o misturador abaixo para escolher o altifalante ou microfone certo.", "Auscultadores: desligue e volte a ligar, depois escolha-os no misturador."]),
  ("Hadi'a lian no volume", ["Klik ikone speaker iha Eduka-Panel no hasa'e volume.", "Haree katak lian la mute.", "Loke mixer lian iha okos atu hili speaker ka mikrofone loos.", "Headphone: hasai no tama fali, depois hili iha mixer."])),
G("display", "🖥️", ["screen", "display", "monitor", "brightness", "resolution", "layar", "ecrã", "tela", "ekran", "terang", "projector", "proyektor"],
  ["lxqt-config-monitor", "arandr"],
  ("Screen, brightness and projector", ["Open the monitor settings with the button below.", "Choose the resolution that looks sharp (usually the recommended one).", "For a projector, connect the cable first, then choose 'Mirror' or 'Extend'.", "Brightness on laptops: use the Fn + sun keys."]),
  ("Layar, kecerahan dan proyektor", ["Buka pengaturan monitor dengan tombol di bawah.", "Pilih resolusi yang tajam (biasanya yang direkomendasikan).", "Untuk proyektor, colok kabel dulu, lalu pilih 'Cermin' atau 'Perluas'.", "Kecerahan laptop: gunakan tombol Fn + ikon matahari."]),
  ("Ecrã, brilho e projetor", ["Abra as definições do monitor com o botão abaixo.", "Escolha a resolução nítida (normalmente a recomendada).", "Para um projetor, ligue o cabo primeiro e escolha 'Espelhar' ou 'Estender'.", "Brilho no portátil: use as teclas Fn + sol."]),
  ("Ekran, naroman no projetór", ["Loke konfigurasaun monitor ho butaun iha okos.", "Hili rezolusaun ne'ebé moos (dala barak ida rekomendadu).", "Ba projetór, liga kabu uluk, depois hili 'Espellu' ka 'Estende'.", "Naroman iha laptop: uza butaun Fn + loro-matan."])),
G("files", "📁", ["file", "files", "folder", "document", "ficheiro", "ficheiru", "pasta", "berkas", "dokumen", "copy", "salin", "kopia", "delete", "hapus", "rename", "file manager"],
  ["pcmanfm-qt", "pcmanfm", "thunar", "nautilus"],
  ("Manage files and folders", ["Open the file manager with the button below.", "Your work is in Home → Documents, Downloads, Pictures, Music and Videos.", "Right-click a file to Copy, Rename or Move to Trash.", "Tip: ask me 'find file homework' and I'll search for you."]),
  ("Mengelola file dan folder", ["Buka pengelola file dengan tombol di bawah.", "Pekerjaanmu ada di Home → Dokumen, Unduhan, Gambar, Musik dan Video.", "Klik kanan file untuk Salin, Ganti nama atau Buang ke Tempat Sampah.", "Tips: tanya saya 'cari file tugas', saya akan mencarikannya."]),
  ("Gerir ficheiros e pastas", ["Abra o gestor de ficheiros com o botão abaixo.", "O seu trabalho está em Pasta pessoal → Documentos, Transferências, Imagens, Música e Vídeos.", "Clique com o botão direito para Copiar, Renomear ou Enviar para o Lixo.", "Dica: peça-me 'procura ficheiro trabalho' e eu procuro."]),
  ("Jere ficheiru no pasta", ["Loke jestór ficheiru ho butaun iha okos.", "Ita-nia servisu iha Home → Dokumentu, Download, Imajen, Múzika no Vídeu.", "Klik-loos ficheiru atu Kopia, Troka naran ka Haruka ba Lixu.", "Dika: husu ha'u 'buka ficheiru TPC' no ha'u buka ba ita."])),
G("apps", "🧩", ["install", "instal", "instalar", "aplikasi", "aplikasaun", "app", "apps", "software", "program", "uninstall", "remove app", "hapus aplikasi", "store"],
  ["eduka-store", "plasma-discover", "gnome-software", "synaptic-pkexec", "synaptic"],
  ("Install or remove applications", ["Open the software centre with the button below.", "Search for the app name, for example 'LibreOffice' or 'GCompris'.", "Press Install and type your password if asked.", "To remove an app, find it in the same place and press Remove."]),
  ("Memasang atau menghapus aplikasi", ["Buka pusat perangkat lunak dengan tombol di bawah.", "Cari nama aplikasi, misalnya 'LibreOffice' atau 'GCompris'.", "Tekan Pasang dan ketik kata sandimu jika diminta.", "Untuk menghapus, cari aplikasinya di tempat yang sama lalu tekan Hapus."]),
  ("Instalar ou remover aplicações", ["Abra o centro de software com o botão abaixo.", "Pesquise o nome, por exemplo 'LibreOffice' ou 'GCompris'.", "Prima Instalar e escreva a palavra-passe se pedida.", "Para remover, encontre a aplicação no mesmo sítio e prima Remover."]),
  ("Instala ka hasai aplikasaun", ["Loke sentru software ho butaun iha okos.", "Buka naran aplikasaun, ezemplu 'LibreOffice' ka 'GCompris'.", "Klik Instala no hakerek password se husu.", "Atu hasai, buka aplikasaun iha fatin hanesan no klik Hasai."])),
G("updates", "🔄", ["update", "upgrade", "pembaruan", "perbarui", "atualizar", "atualizasaun", "security"],
  ["eduka-update", "update-manager", "plasma-discover", "gnome-software", "synaptic-pkexec"],
  ("Keep Edukasaun OS updated", ["Connect to the internet (Wi-Fi or cable).", "Open the updater with the button below.", "Press Check / Refresh, then Install updates.", "Keep the computer plugged in and don't turn it off until it finishes."]),
  ("Memperbarui Edukasaun OS", ["Sambungkan ke internet (Wi-Fi atau kabel).", "Buka pembaru dengan tombol di bawah.", "Tekan Periksa / Segarkan, lalu Pasang pembaruan.", "Colokkan charger dan jangan matikan komputer sampai selesai."]),
  ("Manter o Edukasaun OS atualizado", ["Ligue-se à internet (Wi-Fi ou cabo).", "Abra o atualizador com o botão abaixo.", "Prima Verificar / Atualizar lista e depois Instalar atualizações.", "Mantenha o carregador ligado e não desligue até terminar."]),
  ("Atualiza Edukasaun OS", ["Liga ba internet (Wi-Fi ka kabu).", "Loke atualizadór ho butaun iha okos.", "Klik Verifika, depois Instala atualizasaun.", "Liga karregadór no keta hamate komputadór to'o remata."])),
G("printer", "🖨️", ["printer", "print", "cetak", "imprimir", "imprimi", "impresora", "scanner"],
  ["system-config-printer"],
  ("Add a printer and print", ["Turn the printer on and connect the USB cable or the same Wi-Fi.", "Open the printer settings with the button below and press Add.", "Choose your printer and finish the wizard.", "In any app press Ctrl + P to print."]),
  ("Menambah printer dan mencetak", ["Nyalakan printer dan colok kabel USB atau sambung ke Wi-Fi yang sama.", "Buka pengaturan printer dengan tombol di bawah lalu tekan Tambah.", "Pilih printermu dan selesaikan panduannya.", "Di aplikasi apa saja tekan Ctrl + P untuk mencetak."]),
  ("Adicionar impressora e imprimir", ["Ligue a impressora e o cabo USB ou a mesma rede Wi-Fi.", "Abra as definições de impressoras abaixo e prima Adicionar.", "Escolha a impressora e termine o assistente.", "Em qualquer aplicação prima Ctrl + P para imprimir."]),
  ("Aumenta impresora no imprimi", ["Lakan impresora no liga kabu USB ka Wi-Fi hanesan.", "Loke konfigurasaun impresora iha okos no klik Aumenta.", "Hili ita-nia impresora no remata.", "Iha aplikasaun saida de'it klik Ctrl + P atu imprimi."])),
G("usb", "💾", ["usb", "flashdisk", "flash disk", "pendrive", "pen drive", "disk", "eject", "keluarkan", "harddisk"],
  ["pcmanfm-qt", "pcmanfm", "thunar"],
  ("Use a USB flash drive", ["Plug in the USB drive; a window or notice appears.", "Open it in the file manager (button below) to copy files.", "Before unplugging, click the eject ⏏ icon next to the drive.", "Wait for the notice, then remove it safely."]),
  ("Memakai flashdisk USB", ["Colokkan flashdisk; akan muncul jendela atau pemberitahuan.", "Buka di pengelola file (tombol di bawah) untuk menyalin file.", "Sebelum dicabut, klik ikon keluarkan ⏏ di samping drive.", "Tunggu pemberitahuan, lalu cabut dengan aman."]),
  ("Usar uma pen USB", ["Ligue a pen USB; aparece uma janela ou aviso.", "Abra-a no gestor de ficheiros (botão abaixo) para copiar.", "Antes de retirar, clique no ícone ejetar ⏏ ao lado da unidade.", "Espere pelo aviso e retire com segurança."]),
  ("Uza flashdisk USB", ["Tama flashdisk; janela ka avizu sei mosu.", "Loke iha jestór ficheiru (butaun iha okos) atu kopia.", "Molok hasai, klik ikone eject ⏏ iha sorin drive.", "Hein avizu, depois hasai ho seguru."])),
G("screenshot", "📸", ["screenshot", "tangkapan layar", "capture", "captura", "foto ekran", "print screen", "prtsc"],
  ["screengrab", "flameshot", "spectacle"],
  ("Take a screenshot", ["Press the Print Screen (PrtSc) key.", "Or open the screenshot tool with the button below.", "Choose the whole screen, a window or an area.", "Save it — it goes to your Pictures folder."]),
  ("Mengambil tangkapan layar", ["Tekan tombol Print Screen (PrtSc).", "Atau buka alat tangkapan layar dengan tombol di bawah.", "Pilih seluruh layar, jendela, atau area.", "Simpan — hasilnya masuk ke folder Gambar."]),
  ("Fazer uma captura de ecrã", ["Prima a tecla Print Screen (PrtSc).", "Ou abra a ferramenta de captura com o botão abaixo.", "Escolha o ecrã inteiro, uma janela ou uma área.", "Guarde — fica na pasta Imagens."]),
  ("Foti foto ekran", ["Klik butaun Print Screen (PrtSc).", "Ka loke ferramenta foto ekran ho butaun iha okos.", "Hili ekran tomak, janela ida ka área ida.", "Rai — nia sei tama iha pasta Imajen."])),
G("shortcuts", "⌨️", ["shortcut", "keyboard shortcut", "pintasan", "atalho", "tekla", "copy paste", "ctrl"],
  ["lxqt-config-globalkeyshortcuts"],
  ("Useful keyboard shortcuts", ["Ctrl + C copy · Ctrl + V paste · Ctrl + Z undo · Ctrl + S save.", "Alt + Tab switches between open windows.", "Ctrl + Alt + T opens the terminal (if enabled) · Super opens the menu.", "Change shortcuts with the button below."]),
  ("Pintasan keyboard yang berguna", ["Ctrl + C salin · Ctrl + V tempel · Ctrl + Z batal · Ctrl + S simpan.", "Alt + Tab berpindah antar jendela.", "Ctrl + Alt + T membuka terminal (jika aktif) · Super membuka menu.", "Ubah pintasan dengan tombol di bawah."]),
  ("Atalhos de teclado úteis", ["Ctrl + C copiar · Ctrl + V colar · Ctrl + Z desfazer · Ctrl + S guardar.", "Alt + Tab troca entre janelas.", "Ctrl + Alt + T abre o terminal (se ativo) · Super abre o menu.", "Altere atalhos com o botão abaixo."]),
  ("Atallu teklado útil", ["Ctrl + C kopia · Ctrl + V kola · Ctrl + Z fila fali · Ctrl + S rai.", "Alt + Tab troka entre janela.", "Ctrl + Alt + T loke terminal (se ativu) · Super loke menu.", "Troka atallu ho butaun iha okos."])),
G("password", "🔑", ["password", "kata sandi", "sandi", "palavra-passe", "senha", "account", "akun", "user", "login"],
  ["lxqt-config", "users-admin"],
  ("Change your password", ["Use the account settings button below.", "Choose your user and select Change password.", "Type the old password, then the new one twice.", "Use at least 8 characters and never share it."]),
  ("Mengganti kata sandi", ["Gunakan tombol pengaturan akun di bawah.", "Pilih pengguna kamu lalu pilih Ganti kata sandi.", "Ketik kata sandi lama, lalu yang baru dua kali.", "Gunakan minimal 8 karakter dan jangan bagikan ke siapa pun."]),
  ("Alterar a palavra-passe", ["Use o botão de definições de conta abaixo.", "Escolha o seu utilizador e Alterar palavra-passe.", "Escreva a antiga e a nova duas vezes.", "Use pelo menos 8 caracteres e nunca a partilhe."]),
  ("Troka password", ["Uza butaun konfigurasaun konta iha okos.", "Hili ita-nia uzuáriu no hili Troka password.", "Hakerek password tuan, depois foun dala rua.", "Uza karakter 8 ka liu no keta fahe ba ema."])),
G("language", "🌐", ["language", "bahasa", "idioma", "lian", "keyboard layout", "tata letak", "teclado", "locale"],
  ["lxqt-config-locale", "lxqt-config-input"],
  ("Change language or keyboard layout", ["Open the language (locale) settings with the button below.", "Choose English, Bahasa Indonesia, Português or Tetun if available.", "Log out and in again to apply.", "Keyboard layout: open input settings and add a layout."]),
  ("Mengganti bahasa atau tata letak keyboard", ["Buka pengaturan bahasa (locale) dengan tombol di bawah.", "Pilih English, Bahasa Indonesia, Português atau Tetun jika tersedia.", "Keluar lalu masuk lagi agar berlaku.", "Tata letak keyboard: buka pengaturan input dan tambah layout."]),
  ("Alterar idioma ou teclado", ["Abra as definições de idioma (locale) abaixo.", "Escolha English, Bahasa Indonesia, Português ou Tétum se existir.", "Termine a sessão e volte a entrar.", "Teclado: abra as definições de entrada e adicione um esquema."]),
  ("Troka lian ka teklado", ["Loke konfigurasaun lian (locale) ho butaun iha okos.", "Hili English, Bahasa Indonesia, Português ka Tetun se iha.", "Sai no tama fali atu aplika.", "Teklado: loke konfigurasaun input no aumenta layout."])),
G("accessibility", "♿", ["accessibility", "aksesibilitas", "acessibilidade", "font size", "ukuran huruf", "big text", "zoom", "magnifier", "contrast", "kontras"],
  ["lxqt-config-appearance"],
  ("Bigger text and easier reading", ["Open appearance settings with the button below.", "Increase the font size, for example to 12 or 14.", "Choose a high-contrast theme if colours are hard to see.", "In browsers and documents, Ctrl + plus zooms in."]),
  ("Huruf lebih besar dan mudah dibaca", ["Buka pengaturan tampilan dengan tombol di bawah.", "Perbesar ukuran huruf, misalnya 12 atau 14.", "Pilih tema kontras tinggi jika warna sulit dilihat.", "Di browser dan dokumen, Ctrl + plus untuk memperbesar."]),
  ("Texto maior e leitura fácil", ["Abra as definições de aparência abaixo.", "Aumente o tamanho da letra, por exemplo 12 ou 14.", "Escolha um tema de alto contraste.", "Em navegadores e documentos, Ctrl + mais aumenta o zoom."]),
  ("Letra boot no fasil atu lee", ["Loke konfigurasaun aparénsia ho butaun iha okos.", "Hasa'e tamañu letra, ezemplu 12 ka 14.", "Hili tema kontraste aas se kór susar atu haree.", "Iha browser no dokumentu, Ctrl + plus atu hamoris zoom."])),
G("power", "🔋", ["battery", "baterai", "bateria", "power", "daya", "charge", "shutdown", "matikan", "desligar", "hamate", "sleep mode", "restart"],
  ["lxqt-config-powermanagement"],
  ("Battery, sleep and shutdown", ["Battery level is shown on the Eduka-Panel.", "Open power settings below to choose when the screen sleeps.", "Shut down from the menu → Leave → Shutdown; save your work first.", "Low battery? Lower screen brightness and close unused apps."]),
  ("Baterai, tidur dan mematikan", ["Level baterai terlihat di Eduka-Panel.", "Buka pengaturan daya di bawah untuk memilih kapan layar tidur.", "Matikan dari menu → Keluar → Matikan; simpan pekerjaan dulu.", "Baterai lemah? Kurangi kecerahan dan tutup aplikasi yang tidak dipakai."]),
  ("Bateria, suspensão e desligar", ["O nível da bateria aparece no Eduka-Panel.", "Abra as definições de energia abaixo.", "Desligue em menu → Sair → Desligar; guarde primeiro.", "Bateria fraca? Baixe o brilho e feche aplicações."]),
  ("Bateria, toba no hamate", ["Nivel bateria hatudu iha Eduka-Panel.", "Loke konfigurasaun enerjia iha okos.", "Hamate husi menu → Sai → Hamate; rai servisu uluk.", "Bateria ki'ik? Hatun naroman no taka aplikasaun."])),
G("office", "📝", ["office", "libreoffice", "word", "excel", "powerpoint", "writer", "calc spreadsheet", "presentation", "presentasi", "apresentação", "dokumen baru", "pdf export"],
  ["libreoffice"],
  ("Write documents, spreadsheets and slides", ["Open LibreOffice with the button below.", "Writer = documents, Calc = spreadsheets, Impress = presentations.", "Save often with Ctrl + S; choose .docx or .pdf when sharing.", "File → Export as PDF creates a PDF for printing."]),
  ("Membuat dokumen, tabel dan presentasi", ["Buka LibreOffice dengan tombol di bawah.", "Writer = dokumen, Calc = tabel, Impress = presentasi.", "Sering simpan dengan Ctrl + S; pilih .docx atau .pdf untuk dibagikan.", "File → Ekspor sebagai PDF untuk mencetak."]),
  ("Documentos, folhas de cálculo e apresentações", ["Abra o LibreOffice com o botão abaixo.", "Writer = documentos, Calc = folhas, Impress = apresentações.", "Guarde com Ctrl + S; escolha .docx ou .pdf para partilhar.", "Ficheiro → Exportar como PDF."]),
  ("Hakerek dokumentu, tabela no slide", ["Loke LibreOffice ho butaun iha okos.", "Writer = dokumentu, Calc = tabela, Impress = aprezentasaun.", "Rai beibeik ho Ctrl + S; hili .docx ka .pdf atu fahe.", "Ficheiru → Esporta hanesan PDF."])),
G("settings", "⚙️", ["settings", "pengaturan", "definições", "konfigurasaun", "control panel", "eduka-settings", "eduka settings", "wallpaper", "theme", "tema"],
  ["eduka-settings", "lxqt-config"],
  ("Open Eduka-Settings", ["Open Eduka-Settings with the button below.", "Appearance changes wallpaper and theme; Monitor changes the screen.", "LAFA's own page is in Eduka-Settings → LAFA.", "Not sure? Ask me, for example 'how to change wallpaper'."]),
  ("Membuka Eduka-Settings", ["Buka Eduka-Settings dengan tombol di bawah.", "Tampilan mengubah wallpaper dan tema; Monitor mengubah layar.", "Halaman LAFA ada di Eduka-Settings → LAFA.", "Ragu? Tanya saya, misalnya 'cara ganti wallpaper'."]),
  ("Abrir o Eduka-Settings", ["Abra o Eduka-Settings com o botão abaixo.", "Aparência muda o fundo e o tema; Monitor muda o ecrã.", "A página do LAFA está em Eduka-Settings → LAFA.", "Dúvidas? Pergunte-me, por exemplo 'como mudar o fundo'."]),
  ("Loke Eduka-Settings", ["Loke Eduka-Settings ho butaun iha okos.", "Aparénsia troka wallpaper no tema; Monitor troka ekran.", "Pájina LAFA iha Eduka-Settings → LAFA.", "La serteza? Husu ha'u, ezemplu 'oinsá troka wallpaper'."])),
]
BY_KEY = {g.key: g for g in GUIDES}

HELP_WORDS = ("how", "how to", "cara", "bagaimana", "gimana", "como", "oinsá", "oinsa", "help", "bantu", "ajuda", "tidak bisa", "can't", "cannot", "não consigo", "la bele", "problem", "masalah", "problema", "fix", "perbaiki", "where", "di mana", "onde", "iha ne'ebé")

def normal(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(c))

def find(text, require_help_word=True):
    """Best matching guide for a question, or None. Word-boundary matching only."""
    t = normal(text)
    if require_help_word and not any(re.search(r"(?<!\w)" + re.escape(normal(w)) + r"(?!\w)", t) for w in HELP_WORDS): return None
    best, score = None, 0
    for guide in GUIDES:
        s = sum(len(k) for k in guide.keywords if re.search(r"(?<!\w)" + re.escape(normal(k)) + r"(?!\w)", t))
        if s > score: best, score = guide, s
    return best

def available_tool(guide, which=None):
    """First installed tool from the guide's fixed allowlist (absolute path)."""
    which = which or shutil.which
    for name in guide.tools:
        path = which(name)
        if path: return path
    return None

TIPS = {
"en": ["Press Super to open the menu quickly.", "Ctrl + Z undoes a mistake in almost every app.", "Save your work often with Ctrl + S.", "Eject the USB drive before you pull it out.", "Updates keep Edukasaun OS safe — run them weekly.", "Right-click LAFA to see activities and quick actions."],
"id": ["Tekan Super untuk membuka menu dengan cepat.", "Ctrl + Z membatalkan kesalahan di hampir semua aplikasi.", "Sering simpan pekerjaan dengan Ctrl + S.", "Keluarkan flashdisk sebelum dicabut.", "Pembaruan menjaga Edukasaun OS aman — jalankan tiap minggu.", "Klik kanan LAFA untuk melihat aktivitas dan aksi cepat."],
"pt": ["Prima Super para abrir o menu.", "Ctrl + Z desfaz um erro em quase todas as aplicações.", "Guarde com frequência com Ctrl + S.", "Ejete a pen USB antes de a retirar.", "As atualizações mantêm o Edukasaun OS seguro.", "Clique com o botão direito no LAFA para ver ações rápidas."],
"tet": ["Klik Super atu loke menu lalais.", "Ctrl + Z fila fali sala iha aplikasaun hotu-hotu.", "Rai beibeik ho Ctrl + S.", "Eject flashdisk molok hasai.", "Atualizasaun halo Edukasaun OS seguru — halo kada semana.", "Klik-loos LAFA atu haree atividade no asaun lalais."],
}

def tip_of_day(language, day=None):
    tips = TIPS.get(language, TIPS["en"])
    day = int(time.time() // 86400) if day is None else day
    return tips[day % len(tips)]

@dataclass
class SystemReport:
    items: list = field(default_factory=list)  # (label key, value, status ok|warn)

def system_report(home=None, root=Path("/")):
    """Read-only snapshot: OS, desktop, disk, memory, battery. No private data."""
    report = SystemReport()
    try:
        info = dict(line.split("=", 1) for line in Path(root / "etc/os-release").read_text().splitlines() if "=" in line)
        report.items.append(("sys_os", info.get("PRETTY_NAME", "Linux").strip('"'), "ok"))
    except OSError:
        report.items.append(("sys_os", "Linux", "ok"))
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "") or "—"
    session = os.environ.get("XDG_SESSION_TYPE", "") or "—"
    report.items.append(("sys_desktop", f"{desktop} · {session}", "ok"))
    try:
        usage = shutil.disk_usage(home or Path.home())
        free = usage.free / 1e9; pct = usage.used * 100 / max(1, usage.total)
        report.items.append(("sys_disk", f"{free:.1f} GB · {pct:.0f}%", "warn" if free < 2 or pct > 92 else "ok"))
    except OSError: pass
    try:
        mem = {k: int(v.split()[0]) for k, v in (line.split(":", 1) for line in Path(root / "proc/meminfo").read_text().splitlines() if ":" in line) if v.split()}
        total, avail = mem.get("MemTotal", 0) / 1e6, mem.get("MemAvailable", 0) / 1e6
        if total: report.items.append(("sys_memory", f"{avail:.1f} / {total:.1f} GB", "warn" if avail / total < 0.1 else "ok"))
    except (OSError, ValueError): pass
    for battery in sorted(Path(root / "sys/class/power_supply").glob("BAT*")):
        try:
            level = int((battery / "capacity").read_text().strip()); status = (battery / "status").read_text().strip()
            report.items.append(("sys_battery", f"{level}% · {status}", "warn" if level < 20 and status != "Charging" else "ok")); break
        except (OSError, ValueError): continue
    return report
