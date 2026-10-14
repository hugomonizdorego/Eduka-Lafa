"""Learning sources from the "Direktori Master: Situs Pembelajaran & Referensi
Global" (curated by the Edukasaun OS team): e-learning platforms, free books
and encyclopedias, biology and medicine, mathematics and space, technology and
architecture, world languages, thinking and strategy, economy, politics and law.

Z-Library from the original list is not included: it distributes copyrighted
books without permission (its domains were seized in 2022). Open Library,
Project Gutenberg and the Internet Archive offer free books legally.

Descriptions are in Indonesian (from the directory) and English. The sites
are not all free and not of equal quality: lafa/source_meta.py records for
each one its languages, topics, level, whether it needs an account or money,
whether it is recommended as an academic source and why. Availability is
checked only when needed (see below), and the list itself can be updated as
validated data through the online catalog (lafa/assets/catalog.json)."""

from .source_meta import meta, COMMUNITY_RESOURCES  # noqa: F401  (re-exported)

SOURCE_CATEGORIES = [
    ("elearning", {"en": "E-learning & courses", "id": "E-learning & kursus", "pt": "E-learning e cursos", "tet": "Kursu online"}, "#12b886"),
    ("books", {"en": "Books & encyclopedias", "id": "Buku & ensiklopedia", "pt": "Livros e enciclopédias", "tet": "Livru no ensiklopédia"}, "#f59f00"),
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

# ------------------------------------------------------------ availability
# Checked when needed (opening the Library page or a source, or the "Check now"
# button), never the whole catalogue every hour. Results are cached for a day.
# A site that answers is only *reachable*: that never proves its content is
# correct.
import json as _json
import os as _os
import tempfile as _tempfile
import time as _time
import urllib.error as _urlerror
import urllib.request as _urlrequest
from datetime import datetime as _datetime
from pathlib import Path as _Path

STATES = ("ok", "not_found", "restricted", "unknown")
CACHE_HOURS = 24

def status_path():
    base = _Path(_os.environ.get("XDG_CACHE_HOME", str(_Path.home() / ".cache")))
    return base / "lafa" / "sources-status.json"

def load_status():
    """{url: {"state", "checked", "at"}}; old "up"/"down" entries are read as ok/unknown."""
    path = status_path()
    try:
        if path.is_file() and not path.is_symlink() and path.stat().st_size < 500_000:
            data = _json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                clean = {}
                for url, v in data.items():
                    if not isinstance(v, dict) or not isinstance(v.get("checked"), str): continue
                    state = {"up": "ok", "down": "unknown"}.get(v.get("state"), v.get("state"))
                    if state in STATES:
                        at = v.get("at"); clean[url] = {"state": state, "checked": v["checked"], "at": float(at) if isinstance(at, (int, float)) and not isinstance(at, bool) else 0.0}
                return clean
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

def classify(code):
    """State for an HTTP status code (None: no answer at all)."""
    if code is None: return "unknown"
    if 200 <= code < 400: return "ok"
    if code in (404, 410): return "not_found"
    if code in (401, 402, 403, 407, 429, 451): return "restricted"
    return "unknown"

def probe(url, timeout=6):
    """ok, not_found, restricted or unknown for one HTTPS address."""
    if not url.startswith("https://"): return "unknown"
    request = _urlrequest.Request(url, method="HEAD", headers={"User-Agent": "LAFA (Edukasaun OS) source check"})
    try:
        with _urlrequest.build_opener(_Stop()).open(request, timeout=timeout) as response: return classify(response.status)
    except _urlerror.HTTPError as error:
        # A refused HEAD (405) does not mean the page is missing.
        return "unknown" if error.code == 405 else classify(error.code)
    except Exception:
        return "unknown"

def check(items, check=probe, force=False, now=None):
    """Check the given sources (worker thread). Fresh results (< CACHE_HOURS)
    are reused unless force=True. Returns {state: count}."""
    data = load_status(); now = now if now is not None else _time.time(); counts = {s: 0 for s in STATES}
    for source in items:
        url = source[2]; old = data.get(url)
        if not force and old and now - old.get("at", 0) < CACHE_HOURS * 3600:
            counts[old["state"]] += 1; continue
        state = check(url)
        state = state if state in STATES else ("ok" if state is True else "unknown")
        data[url] = {"state": state, "checked": _datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M"), "at": now}
        counts[state] += 1
    _save_status(data); return counts

def check_all(items=None, check_one=probe, force=True):
    """Manual "Check now" for the whole catalogue."""
    return check(items or SOURCES, check_one, force)

# ------------------------------------------------- Timor-Leste media (0.1.4)
# From the Edukasaun OS list of Timor-Leste media. Sources without their own
# website open a Facebook search for the page name (shown as "Facebook").
TIMOR_CATEGORIES = [
    ("tl_news", {"en": "TL news portals & agencies", "id": "Portal & agensi berita TL", "pt": "Portais e agências de notícias", "tet": "Portál no ajénsia notísia"}, "#c92a2a"),
    ("tl_papers", {"en": "TL newspapers", "id": "Surat kabar TL", "pt": "Jornais de TL", "tet": "Jornál TL"}, "#e8590c"),
    ("tl_tv", {"en": "TL television", "id": "Televisi TL", "pt": "Televisão de TL", "tet": "Televizaun TL"}, "#5f3dc4"),
    ("tl_radio", {"en": "TL radio & podcasts", "id": "Radio & podcast TL", "pt": "Rádio e podcasts de TL", "tet": "Rádiu no podcast TL"}, "#1971c2"),
    ("tl_community", {"en": "TL community radio", "id": "Radio komunitas TL", "pt": "Rádios comunitárias", "tet": "Rádiu komunidade"}, "#2b8a3e"),
    ("tl_research", {"en": "TL research & civil society", "id": "Riset & masyarakat sipil TL", "pt": "Investigação e sociedade civil", "tet": "Peskiza no sosiedade sivíl"}, "#5c940d"),
]
TIMOR_CATEGORIES = [("tl_gov", {"en": "Government & education (official)", "id": "Pemerintah & pendidikan (resmi)", "pt": "Governo e educação (oficial)", "tet": "Governu no edukasaun (ofisiál)"}, "#1864ab")] + TIMOR_CATEGORIES
SOURCE_CATEGORIES = SOURCE_CATEGORIES + TIMOR_CATEGORIES

def _fb(name):
    from urllib.parse import quote
    return "https://www.facebook.com/search/pages/?q=" + quote(name)

def _d(id_, en):
    return {"id": id_, "en": en}

TIMOR_MEDIA = [
    ("tl_news", "Wikipédia Tetun", "https://tet.wikipedia.org/wiki/P%C3%A1jina_Mahuluk", _d("Ensiklopedia bebas dalam bahasa Tetun.", "The free encyclopedia in Tetun.")),
    ("tl_news", "TATOLI", "https://tatoli.tl/", _d("Agensi berita nasional Timor-Leste.", "National news agency of Timor-Leste.")),
    ("tl_news", "Timor News", "https://timornews.tl/", _d("Portal berita online Timor-Leste.", "Timor-Leste online news portal.")),
    ("tl_news", "Hatutan", "https://hatutan.com/", _d("Portal berita online.", "Online news portal.")),
    ("tl_news", "O Diligente", "https://odiligente.com/", _d("Berita online dari Dili.", "Online news from Dili.")),
    ("tl_news", "Lafaek News", "https://lafaeknews.tl/", _d("Portal berita online.", "Online news portal.")),
    ("tl_news", "Liquiça Post", "https://liquicapost.com/", _d("Berita dari Liquiçá.", "News from Liquiçá.")),
    ("tl_news", "SMNews", "https://smnews.tl/", _d("Portal berita online.", "Online news portal.")),
    ("tl_news", "Ponto.tl", "https://ponto.tl/", _d("Portal berita online.", "Online news portal.")),
    ("tl_news", "Oekusi Post", "https://oekusipost.com/", _d("Berita dari Oé-Cusse.", "News from Oé-Cusse.")),
    ("tl_news", "Timor Agora", "https://timoragora.blogspot.com/", _d("Blog berita Timor-Leste.", "Timor-Leste news blog.")),
    ("tl_news", "SAPO Timor-Leste", "https://www.sapo.tl/", _d("Portal berita dan layanan online.", "News and online services portal.")),
    ("tl_news", "Neon Metin", "https://neonmetin.info/", _d("Portal berita online.", "Online news portal.")),
    ("tl_news", "Timoroman", "https://timoroman.com/", _d("Portal berita online.", "Online news portal.")),
    ("tl_news", "Lalenok", _fb("Lalenok Ba Ema Hotu"), _d("Halaman Facebook resmi.", "Official Facebook page.")),
    ("tl_papers", "Timor Post", "https://timorpost.com/", _d("Surat kabar harian dengan edisi online.", "Daily newspaper with an online edition.")),
    ("tl_papers", "Suara Timor Lorosae (STL)", "https://stlnews.co/", _d("Surat kabar harian dengan edisi online.", "Daily newspaper with an online edition.")),
    ("tl_papers", "Jornal Independente", "https://independente.tl/", _d("Surat kabar harian.", "Daily newspaper.")),
    ("tl_papers", "Diário Nacional", "https://diarionacional.tl/", _d("Surat kabar harian.", "Daily newspaper.")),
    ("tl_papers", "Tempo Semanal", "https://temposemanal.com/", _d("Surat kabar mingguan investigasi.", "Weekly investigative newspaper.")),
    ("tl_papers", "The Dili Weekly", "https://thediliweekly.com/", _d("Berita mingguan dalam bahasa Tetun dan Inggris.", "Weekly news in Tetun and English.")),
    ("tl_papers", "Kla'ak", "https://klaak.org/", _d("Media dan arsip.", "Media and archive.")),
    ("tl_papers", "Jornal da República", "https://mj.gov.tl/jornal/", _d("Lembaran negara resmi (undang-undang dan keputusan).", "Official gazette (laws and decrees).")),
    ("tl_tv", "RTTL", "https://rttl.tl/", _d("Radio dan Televisi Timor-Leste (publik).", "Rádio e Televisão de Timor-Leste (public).")),
    ("tl_tv", "GMN-TV", "https://gmntv.tl/", _d("Grupo Media Nacional, televisi swasta.", "Grupo Media Nacional, private TV.")),
    ("tl_tv", "TV Edukasaun (TVE)", "https://www.youtube.com/results?search_query=TV+Edukasaun+Timor-Leste", _d("Televisi pendidikan Kementerian Pendidikan.", "Educational TV of the Ministry of Education.")),
    ("tl_radio", "Radio Liberdade", "https://radioliberdade.tl/", _d("Radio komersial dengan siaran online.", "Commercial radio with online streaming.")),
    ("tl_radio", "Radio Timor Kmanek (RTK)", "https://diocesedili.org/", _d("Radio Keuskupan Dili.", "Radio of the Diocese of Dili.")),
    ("tl_radio", "Radio Vox Populi", _fb("Radio Vox Populi Timor-Leste"), _d("Halaman Facebook.", "Facebook page.")),
    ("tl_radio", "Radio Rakambia", "https://radiorakambia.tl/", _d("Radio dengan siaran online.", "Radio with online streaming.")),
    ("tl_radio", "Radio Lorico Lian", _fb("Radio Lorico Lian"), _d("Halaman Facebook.", "Facebook page.")),
    ("tl_radio", "Radio Metro Dili", _fb("Radio Metro Dili"), _d("Halaman Facebook.", "Facebook page.")),
    ("tl_radio", "Radio M3", _fb("Radio M3 Timor-Leste"), _d("Halaman Facebook.", "Facebook page.")),
    ("tl_radio", "JPF Podcast", "https://www.youtube.com/results?search_query=JPF+Podcast+Timor", _d("Podcast di YouTube dan Facebook.", "Podcast on YouTube and Facebook.")),
]
for _name, _place in [("Radio Komunidade Mauloko", "Mauloko"), ("Radio Rai Husar Aileu", "Aileu"), ("Radio Tokodede Liquiçá", "Liquiçá"), ("Afoni Lifau", "Oé-Cusse"),
                      ("Radio Cafe Ermera", "Ermera"), ("Ili Wai Manatuto", "Manatuto"), ("Radio Popular Colelemai Bucoli", "Baucau"), ("Lian Matebian", "Baucau"),
                      ("Radio Comunidade Los Palos", "Lautém"), ("Radio Povu Viqueque", "Viqueque"), ("Radio Don Boaventura", "Manufahi"), ("Lian Tatamailau", "Ainaro"),
                      ("Radio Cova Taroman", "Covalima")]:
    TIMOR_MEDIA.append(("tl_community", _name, _fb(_name), _d(f"Radio komunitas di {_place} (Facebook).", f"Community radio in {_place} (Facebook).")))
TIMOR_MEDIA += [
    ("tl_research", "La'o Hamutuk", "https://www.laohamutuk.org/", _d("Institut pemantauan dan analisis pembangunan Timor-Leste.", "Timor-Leste institute for development monitoring and analysis.")),
    ("tl_research", "Fundasaun Mahein", "https://www.fundasaunmahein.org/", _d("Riset tentang keamanan dan pertahanan.", "Research on security and defence.")),
    ("tl_research", "FONGTIL", "https://fongtil.tl/", _d("Forum LSM Timor-Leste.", "NGO Forum of Timor-Leste.")),
    ("tl_research", "Timor-Leste Press Union (TLPU)", _fb("Timor-Leste Press Union TLPU"), _d("Persatuan pers Timor-Leste.", "Timor-Leste press union.")),
]
OFFICIAL = [
    ("tl_gov", "Governo de Timor-Leste", "https://timor-leste.gov.tl/", {"id": "Portal resmi Pemerintah Timor-Leste: berita dan informasi pemerintahan.", "en": "Official portal of the Government of Timor-Leste: news and government information."}),
    ("tl_gov", "Ministério da Educação (MoE)", "https://moe.gov.tl/", {"id": "Kementerian Pendidikan Timor-Leste: kebijakan, kurikulum dan pengumuman sekolah.", "en": "Ministry of Education of Timor-Leste: policy, curriculum and school announcements."}),
]
SOURCES = SOURCES + OFFICIAL + TIMOR_MEDIA
