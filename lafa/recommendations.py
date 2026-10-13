"""What LAFA recommends when you click it.

Offline: a free-software tip — programs on Edukasaun OS released under the
GNU GPL (or another open-source licence) that help students. Online: also a
learning website from LAFA's source directory, chosen for the day, which can
be opened from the balloon. Recommendations rotate so each click is new.
"""
import random
from .school import L
from . import sources

# (program, licence, how it helps) — all free software available in Debian.
FREE_SOFTWARE = [
    ("LibreOffice", "MPL 2.0 / LGPLv3", L("Write homework, make slides and tables — and save as PDF.", "Tulis PR, buat slide dan tabel — lalu simpan sebagai PDF.", "Escreve trabalhos, faz apresentações e tabelas — e guarda em PDF.", "Hakerek TPC, halo slide no tabela — depois rai hanesan PDF.")),
    ("GIMP", "GNU GPLv3", L("Edit photos and draw posters for school projects.", "Edit foto dan buat poster untuk proyek sekolah.", "Edita fotos e faz cartazes para projetos.", "Edita foto no halo póster ba projetu eskola.")),
    ("Inkscape", "GNU GPLv2+", L("Draw maps, logos and diagrams that stay sharp.", "Gambar peta, logo dan diagram yang tetap tajam.", "Desenha mapas, logótipos e diagramas nítidos.", "Dezeña mapa, logo no diagrama ne'ebé kroat.")),
    ("GCompris", "GNU AGPLv3", L("More than 100 learning games for children.", "Lebih dari 100 permainan belajar untuk anak.", "Mais de 100 jogos educativos para crianças.", "Jogu aprendizajen liu 100 ba labarik.")),
    ("Kiwix", "GNU GPLv3", L("Read Wikipedia without internet after one download.", "Baca Wikipedia tanpa internet setelah sekali unduh.", "Lê a Wikipédia sem internet depois de um download.", "Lee Wikipédia la ho internet depois download dala ida.")),
    ("Stellarium", "GNU GPLv2+", L("A planetarium: see the stars above Dili tonight.", "Planetarium: lihat bintang di atas Dili malam ini.", "Um planetário: vê as estrelas sobre Díli esta noite.", "Planetáriu: haree fitun iha Dili nia leten kalan ne'e.")),
    ("Audacity", "GNU GPLv2+", L("Record and edit your voice for language practice.", "Rekam dan edit suaramu untuk latihan bahasa.", "Grava e edita a tua voz para praticar línguas.", "Grava no edita ita-nia lian ba pratika lian.")),
    ("VLC", "GNU GPLv2+ / LGPL", L("Plays every video and audio lesson.", "Memutar semua video dan audio pelajaran.", "Reproduz todas as aulas em vídeo e áudio.", "Toka vídeo no áudiu lisaun hotu.")),
    ("Kdenlive", "GNU GPLv3", L("Make a video for your school project.", "Buat video untuk proyek sekolahmu.", "Faz um vídeo para o teu projeto.", "Halo vídeo ba ita-nia projetu eskola.")),
    ("KTurtle", "GNU GPLv2+", L("Learn programming by drawing with a turtle.", "Belajar pemrograman dengan menggambar bersama kura-kura.", "Aprende a programar a desenhar com uma tartaruga.", "Aprende programasaun ho dezeña ho lenuk.")),
    ("Firefox", "MPL 2.0", L("Browse safely; use private windows on shared computers.", "Jelajah dengan aman; pakai jendela pribadi di komputer bersama.", "Navega em segurança; usa janelas privadas em computadores partilhados.", "Navega ho seguru; uza janela privada iha komputadór fahe.")),
    ("GNU/Linux terminal", "GNU GPL", L("Try `ls`, `cd` and `man ls` — the manual explains every command.", "Coba `ls`, `cd` dan `man ls` — manual menjelaskan setiap perintah.", "Experimenta `ls`, `cd` e `man ls` — o manual explica cada comando.", "Koko `ls`, `cd` no `man ls` — manuál esplika komandu hotu.")),
]
GPL_NOTE = L("Free software respects your four freedoms: use, study, share and improve.",
             "Perangkat lunak bebas menghormati empat kebebasanmu: memakai, mempelajari, membagikan dan memperbaiki.",
             "O software livre respeita as tuas quatro liberdades: usar, estudar, partilhar e melhorar.",
             "Software livre respeita ita-nia liberdade haat: uza, estuda, fahe no hadi'ak.")

def _t(value, lang):
    return value.get(lang) or value["en"]

def pick(lang="en", online=True, rng=random):
    """(text, url or '') for the balloon after a click on LAFA."""
    name, licence, why = rng.choice(FREE_SOFTWARE)
    lines = [f"🐧 {name} ({licence}) — {_t(why, lang)}", _t(GPL_NOTE, lang)]
    url = ""
    if online:
        category, site, url, description = rng.choice(sources.SOURCES)
        lines.insert(0, f"🌐 {site} — {sources.text(description, lang)}")
    return "\n\n".join(lines), url
