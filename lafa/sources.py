"""Learning sources from the "Direktori Master: Situs Pembelajaran & Referensi
Global" (curated by the Edukasaun OS team): e-learning platforms, free books
and encyclopedias, biology and medicine, mathematics and space, technology and
architecture, world languages, thinking and strategy, economy, politics and law.

Z-Library from the original list is not included: it distributes copyrighted
books without permission (its domains were seized in 2022). Open Library,
Project Gutenberg and the Internet Archive offer free books legally.

Descriptions are in Indonesian (from the directory) and English. LAFA checks
every hour, when online, whether each site answers, and the list itself can be
updated through the online catalog (lafa/assets/catalog.json)."""

SOURCE_CATEGORIES = [
    ("elearning", {"en": "E-learning & courses", "id": "E-learning & kursus", "pt": "E-learning e cursos", "tet": "Kursu online"}, "#12b886"),
    ("books", {"en": "Free books & encyclopedias", "id": "Buku gratis & ensiklopedia", "pt": "Livros gratuitos e enciclopédias", "tet": "Livru gratuitu no ensiklopédia"}, "#f59f00"),
    ("biomed", {"en": "Biology, chemistry & medicine", "id": "Biologi, kimia & kedokteran", "pt": "Biologia, química e medicina", "tet": "Biolojia, kímika no medisina"}, "#e64980"),
    ("mathspace", {"en": "Maths, physics & space", "id": "Matematika, fisika & antariksa", "pt": "Matemática, física e espaço", "tet": "Matemátika, fízika no espasu"}, "#4c6ef5"),
    ("tech", {"en": "Computers, technology & architecture", "id": "Komputer, teknologi & arsitektur", "pt": "Informática, tecnologia e arquitetura", "tet": "Informátika, teknolojia no arkitetura"}, "#15aabf"),
    ("languages", {"en": "World languages", "id": "Bahasa dunia", "pt": "Línguas do mundo", "tet": "Lian mundu nian"}, "#fd7e14"),
    ("thinking", {"en": "Strategy & philosophy", "id": "Strategi & filsafat", "pt": "Estratégia e filosofia", "tet": "Estratéjia no filozofia"}, "#7950f2"),
    ("society", {"en": "Economy, politics & law", "id": "Ekonomi, politik & hukum", "pt": "Economia, política e direito", "tet": "Ekonomia, polítika no direitu"}, "#2b8a3e"),
]

# (category, name, url, description {id, en})
SOURCES = [
    ("elearning", "Coursera", "https://www.coursera.org/", {"id": "Kursus dari universitas top dunia di berbagai bidang.", "en": "University courses from top universities in many fields."}),
    ("elearning", "edX", "https://www.edx.org/", {"id": "Platform dari Harvard & MIT untuk belajar sains, hukum, politik, dll.", "en": "Harvard and MIT platform for science, law, politics and more."}),
    ("elearning", "Khan Academy", "https://www.khanacademy.org/", {"id": "Pelajaran gratis untuk matematika, sains, dan komputasi.", "en": "Free lessons in mathematics, science and computing."}),
    ("elearning", "Ruangguru", "https://www.ruangguru.com/", {"id": "Aplikasi belajar terbesar di Asia Tenggara untuk pelajar SD-SMA.", "en": "Southeast Asia's largest learning app for primary and secondary school."}),
    ("elearning", "Zenius", "https://www.zenius.net/", {"id": "Platform pembelajaran dengan penekanan pada logika dan pemahaman konsep.", "en": "Learning platform focused on logic and understanding concepts."}),
    ("elearning", "Udemy", "https://www.udemy.com/", {"id": "Ribuan kursus praktis dari pemrograman hingga desain.", "en": "Thousands of practical courses, from programming to design."}),
    ("elearning", "FutureLearn", "https://www.futurelearn.com/", {"id": "Kursus dari universitas Inggris untuk humaniora dan komunikasi.", "en": "Courses from UK universities in humanities and communication."}),
    ("elearning", "MIT OpenCourseWare", "https://ocw.mit.edu/", {"id": "Materi kuliah gratis langsung dari Massachusetts Institute of Technology.", "en": "Free course materials straight from MIT."}),
    ("elearning", "Harvard Online", "https://online-learning.harvard.edu/", {"id": "Akses ke kursus gratis dan berbayar dari Harvard University.", "en": "Free and paid courses from Harvard University."}),
    ("elearning", "Alison", "https://www.alison.com/", {"id": "Kursus gratis dengan sertifikat untuk keterampilan kerja dan bahasa.", "en": "Free certificate courses for work skills and languages."}),
    ("books", "Project Gutenberg", "https://www.gutenberg.org/", {"id": "Lebih dari 70.000 e-book gratis, fokus pada karya sastra klasik.", "en": "More than 70,000 free e-books, mostly classic literature."}),
    ("books", "Internet Archive", "https://archive.org/", {"id": "Jutaan buku, film, dan halaman web historis gratis.", "en": "Millions of free books, films and historic web pages."}),
    ("books", "WikiHow", "https://www.wikihow.com/", {"id": "Panduan langkah-demi-langkah terlengkap untuk melakukan hampir segalanya.", "en": "Step-by-step guides for doing almost anything."}),
    ("books", "Wikipedia", "https://www.wikipedia.org/", {"id": "Ensiklopedia multibahasa terbesar di dunia.", "en": "The world's largest multilingual encyclopedia."}),
    ("books", "Directory of Open Access Journals", "https://www.doaj.org/", {"id": "Direktori jurnal ilmiah gratis berkualitas tinggi.", "en": "Directory of high-quality free scientific journals."}),
    ("books", "Open Library", "https://www.openlibrary.org/", {"id": "Proyek katalog perpustakaan digital terbuka dari Internet Archive.", "en": "Open digital library catalogue from the Internet Archive."}),
    ("books", "Google Scholar", "https://scholar.google.com/", {"id": "Mesin pencari untuk literatur dan jurnal akademis berbagai bidang.", "en": "Search engine for academic literature and journals."}),
    ("books", "Smashwords", "https://www.smashwords.com/", {"id": "Distributor e-book indie dengan banyak koleksi buku gratis.", "en": "Indie e-book distributor with many free books."}),
    ("books", "LibriVox", "https://www.librivox.org/", {"id": "Buku audio domain publik gratis yang dibacakan oleh sukarelawan.", "en": "Free public-domain audiobooks read by volunteers."}),
    ("biomed", "PubMed", "https://pubmed.ncbi.nlm.nih.gov/", {"id": "Basis data utama untuk jurnal biologi dan kedokteran pemerintah AS.", "en": "Main database of biology and medicine journals (US government)."}),
    ("biomed", "Medscape", "https://www.medscape.com/", {"id": "Informasi medis dan edukasi berkelanjutan untuk dokter dan pelajar medis.", "en": "Medical information and continuing education for doctors and students."}),
    ("biomed", "InnerBody", "https://www.innerbody.com/", {"id": "Panduan interaktif anatomi tubuh manusia.", "en": "Interactive guide to human anatomy."}),
    ("biomed", "ChemGuide", "https://chemguide.co.uk/", {"id": "Sumber belajar kimia yang sangat detail untuk pelajar dan mahasiswa.", "en": "Very detailed chemistry learning for students."}),
    ("biomed", "Biology Online", "https://www.biologyonline.com/", {"id": "Ensiklopedia biologi dengan tutorial dan kamus lengkap.", "en": "Biology encyclopedia with tutorials and a dictionary."}),
    ("biomed", "Mayo Clinic", "https://www.mayoclinic.org/", {"id": "Referensi penyakit, gejala, dan kondisi medis terpercaya.", "en": "Trusted reference on diseases, symptoms and conditions."}),
    ("biomed", "Royal Society of Chemistry", "https://www.rsc.org/", {"id": "Sumber daya jurnal dan edukasi kimia global.", "en": "Chemistry journals and education resources."}),
    ("biomed", "Biodiversity Heritage Library", "https://www.biodiversitylibrary.org/", {"id": "Perpustakaan digital terbuka tentang literatur keanekaragaman hayati.", "en": "Open digital library of biodiversity literature."}),
    ("biomed", "Kenhub", "https://www.kenhub.com/", {"id": "Situs terbaik untuk belajar anatomi dan histologi manusia.", "en": "Learn human anatomy and histology."}),
    ("biomed", "Cell Press", "https://www.cell.com/", {"id": "Jurnal-jurnal penelitian biologi sel terkemuka (beberapa akses terbuka).", "en": "Leading cell biology journals (some open access)."}),
    ("mathspace", "Wolfram MathWorld", "https://mathworld.wolfram.com/", {"id": "Ensiklopedia matematika paling ekstensif di internet.", "en": "The most extensive mathematics encyclopedia online."}),
    ("mathspace", "Brilliant", "https://www.brilliant.org/", {"id": "Platform interaktif untuk melatih logika matematika dan fisika.", "en": "Interactive practice for mathematical logic and physics."}),
    ("mathspace", "NASA", "https://www.nasa.gov/", {"id": "Situs resmi badan antariksa AS untuk astronomi, tata surya, dan eksplorasi.", "en": "US space agency: astronomy, the solar system and exploration."}),
    ("mathspace", "Space.com", "https://www.space.com/", {"id": "Berita dan informasi ilmiah terbaru mengenai tata surya dan antariksa.", "en": "News and science about space and the solar system."}),
    ("mathspace", "Physics Classroom", "https://www.physicsclassroom.com/", {"id": "Tutorial fisika dasar hingga menengah dengan simulasi gerak & energi.", "en": "Physics tutorials with motion and energy simulations."}),
    ("mathspace", "Desmos", "https://www.desmos.com/", {"id": "Kalkulator grafik canggih untuk belajar fungsi matematika visual.", "en": "Graphing calculator for visual mathematics."}),
    ("mathspace", "Hubble Site", "https://www.hubblesite.org/", {"id": "Galeri kosmos dan penemuan astronomi dari teleskop Hubble.", "en": "Gallery and discoveries of the Hubble telescope."}),
    ("mathspace", "HyperPhysics", "https://hyperphysics.phy-astr.gsu.edu/", {"id": "Peta konsep interaktif dari semua cabang ilmu fisika.", "en": "Interactive concept maps of all branches of physics."}),
    ("mathspace", "GeoGebra", "https://www.geogebra.org/", {"id": "Aplikasi dinamis untuk belajar geometri, aljabar, dan kalkulus.", "en": "Dynamic geometry, algebra and calculus."}),
    ("mathspace", "arXiv", "https://www.arxiv.org/", {"id": "Repositori pracetak makalah penelitian fisika, matematika, dan astronomi.", "en": "Preprints in physics, mathematics and astronomy."}),
    ("tech", "Codecademy", "https://www.codecademy.com/", {"id": "Platform belajar koding interaktif dari dasar hingga mahir.", "en": "Interactive coding lessons from beginner to advanced."}),
    ("tech", "W3Schools", "https://www.w3schools.com/", {"id": "Tutorial pengembangan web terbesar (HTML, CSS, JavaScript).", "en": "Large web development tutorials (HTML, CSS, JavaScript)."}),
    ("tech", "ArchDaily", "https://www.archdaily.com/", {"id": "Situs arsitektur paling populer dengan ribuan referensi bangunan.", "en": "Popular architecture site with thousands of buildings."}),
    ("tech", "Stack Overflow", "https://www.stackoverflow.com/", {"id": "Forum tanya jawab terbesar untuk pemrogram dan teknologi komputer.", "en": "The largest Q&A forum for programmers."}),
    ("tech", "GitHub", "https://github.com/", {"id": "Platform kolaborasi kode dan tempat belajar proyek open-source.", "en": "Code collaboration and open-source projects to learn from."}),
    ("tech", "Instructables", "https://www.instructables.com/", {"id": "Panduan DIY untuk elektronik, listrik, tata udara, dan teknik bangunan.", "en": "DIY guides for electronics, electricity and building."}),
    ("tech", "IEEE Xplore", "https://ieeexplore.ieee.org/", {"id": "Perpustakaan digital untuk teknik elektro, kelistrikan, dan ilmu komputer.", "en": "Digital library for electrical engineering and computer science."}),
    ("tech", "GeeksforGeeks", "https://www.geeksforgeeks.org/", {"id": "Portal belajar ilmu komputer, algoritma, dan struktur data.", "en": "Computer science, algorithms and data structures."}),
    ("tech", "Dezeen", "https://www.dezeen.com/", {"id": "Majalah online tentang desain, arsitektur, dan rekayasa bangunan.", "en": "Online magazine on design and architecture."}),
    ("tech", "Hackaday", "https://www.hackaday.com/", {"id": "Proyek rekayasa perangkat keras dan kelistrikan / modifikasi elektronik.", "en": "Hardware, electricity and electronics projects."}),
    ("languages", "Duolingo", "https://www.duolingo.com/", {"id": "Belajar puluhan bahasa (termasuk Inggris, Portugis) dengan metode gamifikasi.", "en": "Learn dozens of languages (including English and Portuguese) as a game."}),
    ("languages", "Memrise", "https://www.memrise.com/", {"id": "Aplikasi belajar kosakata dan frasa bahasa asing dari video penutur asli.", "en": "Vocabulary and phrases from videos of native speakers."}),
    ("languages", "BBC Languages", "https://www.bbc.co.uk/languages/", {"id": "Sumber belajar bahasa Eropa dan global secara gratis.", "en": "Free resources for European and world languages."}),
    ("languages", "Tandem", "https://www.tandem.net/", {"id": "Aplikasi pertukaran bahasa global, mengobrol langsung dengan partner lintas negara.", "en": "Language exchange: chat with partners in other countries."}),
    ("languages", "HelloTalk", "https://www.hellotalk.com/", {"id": "Latihan mengobrol langsung dengan penutur asli untuk melatih komunikasi.", "en": "Practise conversation with native speakers."}),
    ("languages", "Italki", "https://www.italki.com/", {"id": "Situs menemukan guru privat untuk hampir setiap bahasa di dunia, termasuk Asia.", "en": "Find a private teacher for almost any language."}),
    ("languages", "Busuu", "https://www.busuu.com/", {"id": "Komunitas belajar bahasa dengan koreksi langsung dari native speaker.", "en": "Language community with corrections from native speakers."}),
    ("languages", "FluentU", "https://www.fluentu.com/", {"id": "Belajar bahasa internasional melalui video musik, berita, dan trailer film.", "en": "Learn languages with music videos, news and trailers."}),
    ("languages", "Portuguese Lab", "https://www.portugueselab.com/", {"id": "Situs spesifik untuk mendalami bahasa Portugis (Eropa/Internasional).", "en": "Dedicated site for learning Portuguese."}),
    ("languages", "SEAsite", "https://seasite.niu.edu/", {"id": "Pusat sumber belajar interaktif khusus untuk bahasa-bahasa Asia Tenggara (ASEAN).", "en": "Interactive learning for Southeast Asian (ASEAN) languages."}),
    ("thinking", "Stanford Encyclopedia of Philosophy", "https://plato.stanford.edu/", {"id": "Referensi akademik filsafat terlengkap dan diakui secara global.", "en": "The most complete academic reference for philosophy."}),
    ("thinking", "Farnam Street", "https://www.fs.blog/", {"id": "Blog tentang strategi berpikir kritis, model mental, dan kebijaksanaan hidup.", "en": "Critical thinking, mental models and wisdom."}),
    ("thinking", "Chess.com", "https://www.chess.com/", {"id": "Situs untuk melatih imajinasi spasial, taktik, dan strategi tingkat tinggi.", "en": "Train imagination, tactics and strategy."}),
    ("thinking", "LessWrong", "https://www.lesswrong.com/", {"id": "Komunitas yang berfokus pada peningkatan rasionalitas pemikiran manusia.", "en": "Community focused on improving rational thinking."}),
    ("thinking", "Big Think", "https://www.bigthink.com/", {"id": "Video dan artikel dari para pemikir top dunia tentang ide-ide revolusioner.", "en": "Videos and articles by leading thinkers."}),
    ("thinking", "Aeon", "https://www.aeon.co/", {"id": "Esai mendalam tentang filsafat, sains, dan psikologi pikiran manusia.", "en": "In-depth essays on philosophy, science and psychology."}),
    ("thinking", "The Marginalian", "https://www.themarginalian.org/", {"id": "Eksplorasi tentang makna kehidupan melalui literatur, sains, dan imajinasi seni.", "en": "Meaning of life through literature, science and art."}),
    ("thinking", "TED", "https://www.ted.com/", {"id": "Video presentasi ide-ide inovatif (ideas worth spreading) dari pakar berbagai bidang.", "en": "Talks with ideas worth spreading."}),
    ("thinking", "Strategy+Business", "https://www.strategy-business.com/", {"id": "Artikel tentang kepemimpinan strategis dan inovasi korporat.", "en": "Strategic leadership and innovation."}),
    ("thinking", "Internet Encyclopedia of Philosophy", "https://iep.utm.edu/", {"id": "Ensiklopedia filsafat gratis dan ditinjau sejawat oleh akademisi.", "en": "Free peer-reviewed philosophy encyclopedia."}),
    ("society", "Investopedia", "https://www.investopedia.com/", {"id": "Ensiklopedia dan panduan terlengkap tentang sistem ekonomi dan keuangan.", "en": "Guide to economics and finance."}),
    ("society", "E-International Relations", "https://www.e-ir.info/", {"id": "Situs akses terbuka terbesar untuk ilmu politik, hukum, dan hubungan internasional.", "en": "Open-access political science, law and international relations."}),
    ("society", "The Economist", "https://www.economist.com/", {"id": "Analisis otoritatif mengenai kebijakan ekonomi, politik, dan urusan tata negara global.", "en": "Analysis of economics, politics and world affairs."}),
    ("society", "Coursera Law & Politics", "https://www.coursera.org/", {"id": "Ribuan jam video kursus tentang sistem hukum negara dan kebijakan publik.", "en": "Courses on legal systems and public policy."}),
    ("society", "World Bank Open Data", "https://data.worldbank.org/", {"id": "Data terbuka tentang ekonomi makro dan profil negara-negara di dunia.", "en": "Open data on economies and countries."}),
    ("society", "Harvard Business Review", "https://www.hbr.org/", {"id": "Kajian tentang komunikasi bisnis, ekonomi strategis, dan manajemen korporat.", "en": "Business communication, strategy and management."}),
    ("society", "Foreign Affairs", "https://www.foreignaffairs.com/", {"id": "Jurnal berpengaruh tentang kebijakan luar negeri, negara, dan perpolitikan global.", "en": "Journal on foreign policy and world politics."}),
    ("society", "FindLaw", "https://www.findlaw.com/", {"id": "Sistem pencarian informasi hukum konstitusi, perdata, dan pidana.", "en": "Search legal information (constitutional, civil and criminal law)."}),
    ("society", "PRSA", "https://www.prsa.org/", {"id": "Sumber daya untuk strategi dan praktik ilmu komunikasi publik.", "en": "Public communication strategy and practice."}),
    ("society", "OEC", "https://www.oec.world/", {"id": "Observatory of Economic Complexity - Visualisasi data perdagangan & ekonomi antar negara.", "en": "Observatory of Economic Complexity: trade data between countries."}),
]

def text(value, lang):
    if isinstance(value, dict): return value.get(lang) or value.get("en") or next(iter(value.values()))
    return value

def by_category(category=None):
    return [s for s in SOURCES if category in (None, s[0])]

def search(query, lang="en"):
    words = [w for w in str(query).casefold().split() if w]
    return [s for s in SOURCES if all(w in (s[1] + " " + s[2] + " " + text(s[3], lang) + " " + text(s[3], "id")).casefold() for w in words)]

# ------------------------------------------------------------ hourly check
import json as _json
import os as _os
import tempfile as _tempfile
import urllib.error as _urlerror
import urllib.request as _urlrequest
from datetime import datetime as _datetime
from pathlib import Path as _Path

def status_path():
    base = _Path(_os.environ.get("XDG_CACHE_HOME", str(_Path.home() / ".cache")))
    return base / "lafa" / "sources-status.json"

def load_status():
    path = status_path()
    try:
        if path.is_file() and not path.is_symlink() and path.stat().st_size < 500_000:
            data = _json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return {k: v for k, v in data.items() if isinstance(v, dict) and v.get("state") in {"up", "down"} and isinstance(v.get("checked"), str)}
    except (OSError, ValueError, UnicodeError):
        pass
    return {}

def _save_status(data):
    path = status_path(); path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, tmp = _tempfile.mkstemp(dir=path.parent, prefix=".sources-")
    try:
        with _os.fdopen(fd, "w", encoding="utf-8") as stream: _json.dump(data, stream, indent=1)
        _os.chmod(tmp, 0o600); _os.replace(tmp, path)
    finally:
        if _os.path.exists(tmp): _os.unlink(tmp)

class _Stop(_urlrequest.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs): return None   # a redirect already proves the site answers

def probe(url, timeout=6):
    """True when the HTTPS site answers (any status below 500)."""
    if not url.startswith("https://"): return False
    request = _urlrequest.Request(url, method="HEAD", headers={"User-Agent": "LAFA (Edukasaun OS) source check"})
    try:
        with _urlrequest.build_opener(_Stop()).open(request, timeout=timeout) as response: return response.status < 500
    except _urlerror.HTTPError as error: return error.code < 500
    except Exception: return False

def check_all(items=None, check=probe):
    """Check every source once (runs in a worker thread); returns (up, down)."""
    data = load_status(); up = down = 0; now = _datetime.now().strftime("%Y-%m-%d %H:%M")
    for source in (items or SOURCES):
        ok = check(source[2]); data[source[2]] = {"state": "up" if ok else "down", "checked": now}
        up, down = up + ok, down + (not ok)
    _save_status(data); return up, down
