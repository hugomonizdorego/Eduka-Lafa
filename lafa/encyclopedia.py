"""Lafa's encyclopedia: the World Encyclopedia (in Learn) and Timor-Leste.

Articles come from two places:

* lafa/assets/encyclopedia/<area>/<category>.json — full articles with learning
  objectives, sections, facts with years, sources, related ids, tags, a quiz
  with explanations and review metadata (checked by tools/check-encyclopedia.py);
* the Timor-Leste atlas (timor_atlas, timorleste) — every older topic, history
  event, municipality and the lists of leaders, regrouped into the six
  Timor-Leste categories so nothing is lost. These keep their ids "atlas:<key>".

Articles are linked by id and tags, never copied: a Timor-Leste topic appears
once and the world articles point to it. Everything here works offline.
"""
from dataclasses import dataclass, field
from functools import lru_cache
import json
import random
import re
import unicodedata
from pathlib import Path

from . import timor_atlas, timorleste

FOLDER = Path(__file__).resolve().parent / "assets" / "encyclopedia"
LANGS = ("en", "id", "pt", "tet")

def L(en, id_, pt, tet):
    return {"en": en, "id": id_, "pt": pt, "tet": tet}

def text(value, lang):
    if isinstance(value, dict): return value.get(lang) or value.get("en") or next(iter(value.values()), "")
    if isinstance(value, list): return value
    return value or ""

def has(value, lang):
    return isinstance(value, dict) and bool(value.get(lang))

@dataclass(frozen=True)
class Category:
    key: str
    area: str
    title: dict
    summary: dict
    icon: str
    colour: str
    lessons: tuple = ()      # curriculum subjects shown as related lessons

    @property
    def illustration(self):
        return f"{self.area}-{self.key}"

@dataclass
class Article:
    id: str
    area: str
    category: str
    title: dict
    summary: dict
    objectives: dict = field(default_factory=dict)
    sections: list = field(default_factory=list)       # [{"heading": {}, "body": {}}]
    facts: list = field(default_factory=list)          # [{"label": {}, "value": {}, "year": "", "source": 0}]
    figure: str = ""                                   # illustration key
    caption: dict = field(default_factory=dict)
    sources: list = field(default_factory=list)        # [{"title", "publisher", "url", "year"}]
    related: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    quiz: list = field(default_factory=list)           # [{"q": {}, "options": {lang: [4]}, "answer": i, "explain": {}}]
    review: dict = field(default_factory=dict)
    group: dict = field(default_factory=dict)          # sub-heading in the category list
    when: str = ""
    activity: str = ""                                 # interactive module key
    wiki: str = ""                                     # Wikipedia title for the online extract

    def languages(self):
        """Which languages have the full text, and which only the summary."""
        full = list(self.review.get("langs_full", ["en", "id"]))
        summary = [lang for lang in LANGS if lang not in full and has(self.summary, lang) and self.summary.get(lang) != self.summary.get("en")]
        return full, summary

WORLD = [
    Category("earth", "world", L("Earth & Geology", "Bumi & Geologi", "Terra e Geologia", "Planeta Rai no Jeolojia"),
             L("How our planet formed, moves and changes.", "Bagaimana planet kita terbentuk, bergerak, dan berubah.", "Como o nosso planeta se formou, se move e muda.", 'Oinsá ita-nia planeta mosu, book-an no muda.'), "cat-earth", "#8d6e4a", ("geography", "environment")),
    Category("dinosaurs", "world", L("Dinosaurs & Ancient Life", "Dinosaurus & Kehidupan Purba", "Dinossauros e Vida Antiga", 'Dinosauru no Moris Antigu'),
             L("Fossils, habitats and how life changed.", "Fosil, habitat, dan perubahan kehidupan.", "Fósseis, habitats e como a vida mudou.", "Fósil, fatin moris no oinsá moris muda."), "cat-dinosaur", "#7a6a3a", ("biology",)),
    Category("human_origins", "world", L("Human Origins", "Asal-Usul Manusia", "Origens Humanas", "Ema nia Orijen"),
             L("Where people come from and how they spread.", "Dari mana manusia berasal dan bagaimana menyebar.", "De onde vêm as pessoas e como se espalharam.", "Ema mai husi ne'ebé no oinsá sira habelar-an ba mundu tomak."), "cat-human", "#c08a3e", ("history", "biology")),
    Category("civilizations", "world", L("Civilisations & Societies", "Peradaban & Masyarakat", "Civilizações e Sociedades", "Sivilizasaun no Sosiedade"),
             L("Farming, cities, writing and states.", "Pertanian, kota, tulisan, dan negara.", "Agricultura, cidades, escrita e estados.", "Agrikultura, sidade, hakerek no estadu."), "cat-pyramid", "#c98f4f", ("history",)),
    Category("inventions", "world", L("Inventions & Technology", "Penemuan & Teknologi", "Invenções e Tecnologia", "Invensaun no Teknolojia"),
             L("Ideas and machines that changed daily life.", "Gagasan dan mesin yang mengubah hidup sehari-hari.", "Ideias e máquinas que mudaram a vida diária.", "Ideia no mákina ne'ebé muda moris loroloron."), "cat-invention", "#3f7fbf", ("technology", "computers", "it")),
    Category("colonialism", "world", L("Colonialism & Independence", "Kolonialisme & Kemerdekaan", "Colonialismo e Independência", "Kolonializmu no Independénsia"),
             L("Empires, trade and the road to independence.", "Kekaisaran, perdagangan, dan jalan menuju kemerdekaan.", "Impérios, comércio e o caminho para a independência.", "Impériu, komérsiu no dalan ba independénsia."), "cat-ship", "#a0522d", ("history", "civics")),
    Category("industrial_revolution", "world", L("Industrial Revolution", "Revolusi Industri", "Revolução Industrial", "Revolusaun Industriál"),
             L("Steam, factories, railways and new ways of working.", "Uap, pabrik, kereta api, dan cara kerja baru.", "Vapor, fábricas, comboios e novas formas de trabalho.", "Vapor, fábrika, kareta-ahi no maneira foun atu servisu."), "cat-factory", "#9c5a43", ("history", "economics", "technology")),
    Category("world_wars", "world", L("World Wars & Peace", "Perang Dunia & Perdamaian", "Guerras Mundiais e Paz", "Funu Mundiál no Dame"),
             L("Two world wars and how nations built peace.", "Dua perang dunia dan cara bangsa membangun perdamaian.", "Duas guerras mundiais e como as nações construíram a paz.", "Funu mundiál rua no oinsá nasaun sira harii dame."), "cat-dove", "#577590", ("history", "civics")),
    Category("geography_oceans", "world", L("Geography & Oceans", "Geografi & Lautan", "Geografia e Oceanos", "Jeografia no Oseanu"),
             L("Continents, seas and the living reefs around us.", "Benua, laut, dan terumbu karang di sekitar kita.", "Continentes, mares e os recifes à nossa volta.", "Kontinente, tasi no ahu-ruin ne'ebé haleu ita."), "cat-waves", "#2b8ac4", ("geography",)),
    Category("life_environment", "world", L("Life & Environment", "Kehidupan & Lingkungan", "Vida e Ambiente", "Moris no Ambiente"),
             L("Ecosystems, climate and caring for nature.", "Ekosistem, iklim, dan menjaga alam.", "Ecossistemas, clima e cuidar da natureza.", "Ekosistema, klima no kuidadu natureza."), "cat-leaf", "#4f9a50", ("biology", "environment", "agriculture")),
    Category("science_space", "world", L("Science & Space", "Sains & Antariksa", "Ciência e Espaço", "Siénsia no Espasu"),
             L("The Solar System and how science works.", "Tata Surya dan cara kerja sains.", "O Sistema Solar e como funciona a ciência.", "Sistema Solár no oinsá siénsia servisu."), "cat-planet", "#4a3f8c", ("astronomy", "physics", "chemistry", "atoms")),
    Category("culture_arts", "world", L("Culture, Languages & Arts", "Budaya, Bahasa & Seni", "Cultura, Línguas e Artes", "Kultura, Lian no Arte"),
             L("Languages, music, weaving and heritage.", "Bahasa, musik, tenun, dan warisan budaya.", "Línguas, música, tecelagem e património.", "Lian, múzika, tais no eransa kulturál."), "cat-palette", "#b5651d", ("arts", "communication")),
]
TIMOR = [
    Category("history", "timor", L("History", "Sejarah", "História", "Istória"),
             L("From the first people to today.", "Dari manusia pertama hingga hari ini.", "Dos primeiros habitantes até hoje.", "Husi ema dahuluk to'o ohin loron."), "cat-scroll", "#b0372f"),
    Category("map", "timor", L("Map & Regions", "Peta & Wilayah", "Mapa e Regiões", "Mapa no Rejiaun"),
             L("Municipalities, islands, mountains and coasts.", "Munisipalitas, pulau, gunung, dan pantai.", "Municípios, ilhas, montanhas e costas.", "Munisípiu, illa, foho no tasi-ibun."), "cat-map", "#2f7fb0"),
    Category("culture", "timor", L("Culture & Language", "Budaya & Bahasa", "Cultura e Línguas", "Kultura no Lian"),
             L("Tais, sacred houses, dances, faith and languages.", "Tais, rumah adat, tarian, iman, dan bahasa.", "Tais, casas sagradas, danças, fé e línguas.", "Tais, uma lulik, dansa, fiar no lian."), "cat-culture", "#a23b5b"),
    Category("nature", "timor", L("Nature & Life", "Alam & Kehidupan", "Natureza e Vida", "Natureza no Moris"),
             L("How the island formed, its wildlife and its seas.", "Bagaimana pulau terbentuk, satwa, dan lautnya.", "Como a ilha se formou, a sua fauna e os seus mares.", 'Oinsá illa mosu, ninia animál no ninia tasi.'), "cat-bird", "#4c8b2b"),
    Category("leaders", "timor", L("People & Government", "Tokoh & Pemerintahan", "Figuras e Governo", "Figura no Governu"),
             L("National symbols, leaders and how the state works.", "Lambang negara, pemimpin, dan cara negara bekerja.", "Símbolos nacionais, líderes e como funciona o Estado.", 'Símbolu nasionál, líder sira no oinsá Estadu servisu.'), "cat-landmark", "#38598b"),
    Category("economy", "timor", L("Economy & Society", "Ekonomi & Masyarakat", "Economia e Sociedade", "Ekonomia no Sosiedade"),
             L("Population, coffee, oil, trade and tourism.", "Penduduk, kopi, minyak, perdagangan, dan pariwisata.", "População, café, petróleo, comércio e turismo.", "Populasaun, kafé, mina-rai, komérsiu no turizmu."), "cat-chart", "#8a5fbf"),
]
CATEGORIES = WORLD + TIMOR
BY_KEY = {(c.area, c.key): c for c in CATEGORIES}

# Old atlas categories -> (new Timor-Leste category). Their names become the
# sub-headings in the topic lists.
ATLAS_MAP = {"history": "history", "politics": "history", "map": "map", "municipalities": "map", "islands": "map", "regions": "map",
             "earth": "nature", "symbols": "leaders", "leaders": "leaders", "government": "leaders", "people": "economy",
             "economy": "economy", "nature": "economy", "tourism": "economy"}
ATLAS_OVERRIDE = {"religion": "culture", "languages_official": "culture", "national_days": "culture", "land_sea_wealth": "nature",
                  "heritage_places": "history", "nature_places": "nature"}
# Specific pictures for some atlas topics; the rest use their category picture.
ATLAS_FIGURES = {"flag": "timor-flag", "map_size": "timor-map", "map_history": "timor-map", "map_borders": "timor-map", "map_mountains": "timor-map",
                 "atauro": "timor-map", "jaco": "timor-map", "oecusse": "timor-map", "coffee": "timor-economy", "earth_age": "world-earth",
                 "earth_collision": "world-earth", "earth_gondwana": "world-dinosaurs"}
# Atlas topics that also belong to a world category (linked, not copied).
ATLAS_WORLD = {"earth_age": ["w.earth.formation"], "earth_collision": ["w.earth.plate_tectonics"], "earth_gondwana": ["w.earth.rock_cycle", "w.dinosaurs.fossils"],
               "earth_wallacea": ["w.geography_oceans.coral_triangle", "tl.nature.wildlife"], "earth_climate": ["w.life_environment.climate_change"],
               "languages_official": ["tl.culture.tetun_language", "w.culture_arts.languages_of_the_world"], "dive_atauro": ["w.geography_oceans.coral_triangle"],
               "parties_1974": ["w.colonialism.decolonisation"], "resistance": ["w.colonialism.decolonisation"], "international": ["w.world_wars.second_world_war_peace"]}
ATLAS_REVIEW = {"version": 1, "reviewed": "2026-10-13", "status": "Lafa team text from the listed sources; needs review by a Timorese historian or teacher",
                "licence": "CC BY-SA 4.0"}

OBJECTIVES = {
    "en": ["You will explain the main idea of “{t}” in your own words.", "You will connect “{t}” with related topics.", "You will check what you learned with practice questions."],
    "id": ["Kamu dapat menjelaskan gagasan utama “{t}” dengan kata-katamu sendiri.", "Kamu dapat menghubungkan “{t}” dengan topik terkait.", "Kamu dapat memeriksa pemahamanmu dengan soal latihan."],
    "pt": ["Vais explicar a ideia principal de “{t}” por palavras tuas.", "Vais relacionar “{t}” com temas próximos.", "Vais verificar o que aprendeste com perguntas de exercício."],
    "tet": ["Ita sei esplika ideia prinsipál husi “{t}” ho ita-nia liafuan rasik.", "Ita sei liga “{t}” ho tópiku seluk ne'ebé iha relasaun.", "Ita sei koko saida mak ita aprende ho pergunta prátika."],
}
SUMMARY_HEAD = L("In short", "Ringkasnya", "Em resumo", "Badak de'it")
DETAIL_HEAD = L("More details", "Rincian", "Mais pormenores", "Detalle tan")
FACTS_HEAD = L("Key facts", "Fakta penting", "Factos principais", "Faktu importante")
QUIZ_MATCH = L("Which topic matches this description?", "Topik mana yang sesuai dengan uraian ini?", "Que tema corresponde a esta descrição?", "Tópiku ida ne'ebé mak hanesan deskrisaun ne'e?")
QUIZ_WHEN = L("When did this happen: “{t}”?", "Kapan peristiwa ini terjadi: “{t}”?", "Quando aconteceu isto: “{t}”?", "Bainhira mak ida-ne'e akontese: “{t}”?")
QUIZ_WHY = L("“{t}”: {s}", "“{t}”: {s}", "“{t}”: {s}", "“{t}”: {s}")

def _all_langs(value):
    """Fill missing languages with English so every lookup works (the reader
    still shows honestly which languages are original)."""
    value = dict(value or {}); en = value.get("en", "")
    return {lang: value.get(lang) or en for lang in LANGS}

def _atlas_articles():
    out = []; cats = {k: n for k, n, _ in timor_atlas.CATEGORIES}
    for t in timor_atlas.TOPICS:
        category = ATLAS_OVERRIDE.get(t.key) or ATLAS_MAP.get(t.category, "history")
        sections = [{"heading": SUMMARY_HEAD, "body": dict(t.summary)}]
        if t.body: sections.append({"heading": DETAIL_HEAD, "body": dict(t.body)})
        facts = [{"label": _all_langs(a) if isinstance(a, dict) else L(a, a, a, a), "value": _all_langs(b) if isinstance(b, dict) else L(b, b, b, b), "year": "", "source": 0} for a, b in t.facts]
        sources = [{"title": f"Wikipedia · {t.wiki}", "publisher": "Wikipedia", "url": "https://en.wikipedia.org/wiki/" + t.wiki.replace(" ", "_"), "year": "2026"}] if t.wiki else []
        sources += [{"title": title, "publisher": title.split(" · ")[0], "url": url, "year": "2026"} for title, url in timorleste.SOURCES[:2]]
        full = ["en", "id"] + (["tet"] if t.body and "tet" in t.body else [])
        out.append(Article(f"atlas:{t.key}", "timor", category, dict(t.title), dict(t.summary), sections=sections, facts=facts,
                           figure=ATLAS_FIGURES.get(t.key, ""), sources=sources, related=list(ATLAS_WORLD.get(t.key, [])),
                           tags=[t.category, category], review=dict(ATLAS_REVIEW, langs_full=full), group=dict(cats.get(t.category, {})),
                           when=t.when, wiki=t.wiki))
    era_names = {key: name for key, name, _ in timorleste.ERAS}; era_urls = {key: url for key, _, url in timorleste.ERAS}
    for i, e in enumerate(timorleste.HISTORY):
        sources = [{"title": "Timor-Leste history", "publisher": "Wikipedia", "url": era_urls.get(e.era, "https://en.wikipedia.org/wiki/History_of_East_Timor"), "year": "2026"}]
        sources += [{"title": title, "publisher": title.split(" · ")[0], "url": url, "year": "2026"} for title, url in timorleste.SOURCES[1:3]]
        when = e.when("en") if hasattr(e, "when") else str(e.year)
        out.append(Article(f"atlas:history_{i}", "timor", "history", dict(e.title), dict(e.text), sections=[{"heading": SUMMARY_HEAD, "body": dict(e.text)}],
                           facts=[], figure="timor-history", sources=sources, tags=["history", e.era], review=dict(ATLAS_REVIEW, langs_full=["en", "id", "pt", "tet"]),
                           group=dict(era_names.get(e.era, {})), when=when))
    group = cats.get("municipalities", {})
    for name, town, note in timor_atlas.MUNICIPALITY_NOTES:
        key = "municipality_" + name.split()[0].lower()
        out.append(Article(f"atlas:{key}", "timor", "map", L(name, name, name, name), dict(note), sections=[{"heading": SUMMARY_HEAD, "body": dict(note)}],
                           facts=[{"label": L("Main town", "Kota utama", "Cidade principal", "Sidade prinsipál"), "value": L(town, town, town, town), "year": "", "source": 0}],
                           figure="timor-map", sources=[{"title": "Municipalities of Timor-Leste", "publisher": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Municipalities_of_East_Timor", "year": "2026"}],
                           tags=["municipalities", "map"], review=dict(ATLAS_REVIEW, langs_full=["en", "id"] + (["tet"] if "tet" in note else [])), group=dict(group)))
    leaders = cats.get("leaders", {})
    for key, title, rows, note, wiki in (("presidents", L("Presidents of the Republic", "Presiden Republik", "Presidentes da República", "Prezidente Repúblika sira"), timor_atlas.PRESIDENTS, timor_atlas.ACTING_PRESIDENTS, "President of East Timor"),
                                         ("prime_ministers", L("Prime Ministers", "Perdana Menteri", "Primeiros-Ministros", "Primeiru-Ministru sira"), timor_atlas.PRIME_MINISTERS, timor_atlas.TRANSITION, "Prime Minister of East Timor")):
        body = {lang: "\n".join(f"• {n} ({a} – {b}) — {text(x, lang)}" for n, a, b, x in rows) for lang in LANGS}
        out.append(Article(f"atlas:{key}", "timor", "leaders", title, dict(note), sections=[{"heading": title, "body": body}, {"heading": SUMMARY_HEAD, "body": dict(note)}],
                           figure="timor-leaders", sources=[{"title": wiki, "publisher": "Wikipedia", "url": "https://en.wikipedia.org/wiki/" + wiki.replace(" ", "_"), "year": "2026"}],
                           tags=["leaders"], review=dict(ATLAS_REVIEW, langs_full=["en", "id"]), group=dict(leaders), when="1975 – 2026", wiki=wiki))
    return out

def _load_json():
    out = []; coverage = {}
    for path in sorted(FOLDER.glob("*/*.json")):
        try: data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError): continue
        area, category = data.get("area"), data.get("category")
        if (area, category) not in BY_KEY: continue
        coverage[(area, category)] = data.get("coverage", [])
        for a in data.get("articles", []):
            try:
                figure = a.get("figure") or {}
                out.append(Article(a["id"], area, category, a["title"], a["summary"], a.get("objectives", {}), a.get("sections", []), a.get("facts", []),
                                   figure.get("key", "") if isinstance(figure, dict) else str(figure), figure.get("caption", {}) if isinstance(figure, dict) else {},
                                   a.get("sources", []), a.get("related", []), a.get("tags", []), a.get("quiz", []), a.get("review", {}),
                                   activity=a.get("activity", ""), wiki=a.get("wiki", "")))
            except (KeyError, TypeError, AttributeError):
                continue
    return out, coverage

@lru_cache(maxsize=1)
def _data():
    articles, coverage = _load_json()
    articles += _atlas_articles()
    by_id = {}
    for a in articles: by_id.setdefault(a.id, a)
    for a in by_id.values():
        if not a.figure:
            a.figure = f"{a.area}-{a.category}"
        a.figure = MODULE_FIGURES.get(a.id, a.figure)
        a.activity = a.activity or MODULES.get(a.id, "")
    return by_id, coverage

# Interactive modules (lafa/interactive.py) attached to articles.
MODULES = {"w.dinosaurs.what_are_dinosaurs": "dinosaurs", "w.dinosaurs.fossils": "dinosaurs", "w.dinosaurs.extinction": "dinosaurs",
           "w.earth.formation": "earth_history", "w.earth.rock_cycle": "earth_history", "w.human_origins.homo_sapiens": "earth_history",
           "w.industrial_revolution.steam_factories": "industry", "w.industrial_revolution.changes_society": "industry", "w.inventions.printing": "industry",
           "w.inventions.electricity_communication": "industry"}
MODULE_FIGURES = {"w.dinosaurs.what_are_dinosaurs": "module-trex"}

def reload():
    _data.cache_clear()

def all_articles():
    return list(_data()[0].values())

def get(article_id):
    return _data()[0].get(article_id)

def category(area, key):
    return BY_KEY.get((area, key))

def categories(area):
    return [c for c in CATEGORIES if c.area == area]

def articles(area, key=None):
    return [a for a in _data()[0].values() if a.area == area and (key is None or a.category == key)]

def coverage(area, key):
    """[(topic dict, status, article id)] — available, review or planned."""
    items = [(c.get("topic", {}), c.get("status", "planned"), c.get("article", "")) for c in _data()[1].get((area, key), [])]
    listed = {a for _, _, a in items if a}
    for a in articles(area, key):
        if a.id not in listed and not a.id.startswith("atlas:"): items.insert(0, (a.title, "available", a.id))
    return items

def coverage_counts(area=None):
    counts = {"available": 0, "review": 0, "planned": 0}
    for c in CATEGORIES:
        if area and c.area != area: continue
        for _, status, _ in coverage(c.area, c.key): counts[status] = counts.get(status, 0) + 1
    return counts

def groups(area, key, lang):
    """Topic list of a category, grouped by sub-heading: [(heading, [articles])]."""
    out = {}; order = []
    for a in articles(area, key):
        heading = text(a.group, lang) if a.group else ""
        if heading not in out: out[heading] = []; order.append(heading)
        out[heading].append(a)
    # New articles first, then the atlas groups in their order.
    order.sort(key=lambda h: (h != "",))
    return [(h, out[h]) for h in order]

def related(article, limit=6):
    """Related articles: listed ids first, then same tags, then same group."""
    found = []; seen = {article.id}
    for rid in article.related:
        a = get(rid)
        if a and a.id not in seen: found.append(a); seen.add(a.id)
    tags = set(article.tags) - {article.category}
    for a in all_articles():
        if len(found) >= limit: break
        if a.id in seen: continue
        if (tags & set(a.tags)) and a.area == article.area: found.append(a); seen.add(a.id)
    for a in articles(article.area, article.category):
        if len(found) >= limit: break
        if a.id not in seen and a.group == article.group: found.append(a); seen.add(a.id)
    return found[:limit]

def objectives(article, lang):
    if has(article.objectives, lang) or (isinstance(article.objectives, dict) and article.objectives.get(lang)):
        return article.objectives[lang]
    if article.objectives.get("en") and lang not in OBJECTIVES: return article.objectives["en"]
    title = text(article.title, lang)
    return [line.format(t=title) for line in OBJECTIVES.get(lang, OBJECTIVES["en"])]

def quiz(article, lang, rng=None):
    """The article's quiz, or questions generated from the atlas for older topics:
    [(question, options, answer index, explanation)]."""
    rng = rng or random.Random(article.id)
    out = []
    for q in article.quiz:
        options = q.get("options", {}); opts = options.get(lang) or options.get("en") or []
        if len(opts) == 4 and q.get("answer") in range(4):
            out.append((text(q["q"], lang), list(opts), q["answer"], text(q.get("explain", {}), lang)))
    if out: return out
    same = [a for a in articles(article.area) if a.id != article.id]
    if len(same) >= 3:
        wrong = rng.sample(same, 3); options = [text(article.title, lang)] + [text(a.title, lang) for a in wrong]
        if len(set(options)) == 4:
            order = list(range(4)); rng.shuffle(order); shuffled = [options[i] for i in order]
            out.append((text(QUIZ_MATCH, lang) + "\n\n" + _mask(text(article.summary, lang), text(article.title, lang)), shuffled, order.index(0),
                        text(QUIZ_WHY, lang).format(t=text(article.title, lang), s=text(article.summary, lang))))
    if article.when and re.search(r"\d{3,4}", article.when):
        others = [a.when for a in articles(article.area) if a.when and a.when != article.when and re.search(r"\d{3,4}", a.when)]
        others = list(dict.fromkeys(others))
        if len(others) >= 3:
            options = [article.when] + rng.sample(others, 3)
            order = list(range(4)); rng.shuffle(order); shuffled = [options[i] for i in order]
            out.append((text(QUIZ_WHEN, lang).format(t=text(article.title, lang)), shuffled, order.index(0),
                        text(QUIZ_WHY, lang).format(t=text(article.title, lang), s=text(article.summary, lang))))
    return out

def _mask(summary, title):
    """Hide the answer (the title's own words) in a "which topic?" question."""
    for word in sorted({w for w in re.findall(r"[\w'’-]+", title) if len(w) > 3}, key=len, reverse=True):
        summary = re.sub(rf"(?i)\b{re.escape(word)}\b", "____", summary)
    return summary

# ------------------------------------------------------------------ search
def fold(value):
    value = unicodedata.normalize("NFKD", str(value).casefold())
    return "".join(c for c in value if not unicodedata.combining(c))

WORD = re.compile(r"\w+", re.UNICODE)

def search(query, lang, area=None, limit=40):
    """Simple offline search in titles, summaries, tags and text (all languages)."""
    words = [w for w in WORD.findall(fold(query)) if len(w) > 1]
    if not words: return []
    scored = []
    for a in all_articles():
        if area and a.area != area: continue
        title = fold(" ".join(a.title.values())); summary = fold(" ".join(a.summary.values()) + " " + " ".join(a.tags))
        body = fold(" ".join(text(s.get("body", {}), lang) + " " + text(s.get("body", {}), "en") for s in a.sections))
        score = 0
        for w in words:
            if w in title: score += 6
            elif w in summary: score += 3
            elif w in body: score += 1
            else: score -= 2
        if score > 0: scored.append((score, text(a.title, lang), a))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [a for _, _, a in scored[:limit]]
