"""What Lafa can do without internet, and answers from Lafa's own knowledge.

Everything that matters works offline: search of lessons, the atlas, OS
guides, saved material and file names; lessons for every age, practice and
results; basic phrases in many languages; programming examples; tasks,
timetable, reminders and focus; read aloud; Edukasaun OS help; the Virtual
Assistant. The internet only adds sources: Wikipedia, news, weather, learning
websites and the validated source catalogue. There is no AI and no login.
"""
from .school import L
from . import timor_atlas, classroom

# (key, section, name, works offline)
FEATURES = [
    ("search", "home", L("Search lessons, guides and files", "Cari pelajaran, panduan, dan file", "Pesquisar lições, guias e ficheiros", "Buka lisaun, matadalan no ficheiru"), True),
    ("lessons", "study", L("Lessons for every age (5–100)", "Pelajaran untuk semua usia (5–100)", "Lições para todas as idades (5–100)", "Lisaun ba idade hotu (5–100)"), True),
    ("practice", "study", L("Practice and test simulations", "Latihan dan simulasi tes", "Exercícios e simulações de teste", "Prátika no simulasaun teste"), True),
    ("results", "activities", L("Practice results", "Hasil latihan", "Resultados dos exercícios", "Rezultadu prátika"), True),
    ("phrases", "study", L("Basic phrases in many languages", "Frasa dasar dalam banyak bahasa", "Frases básicas em muitas línguas", "Fraze báziku iha lian barak"), True),
    ("coding", "study", L("Programming examples (Python)", "Contoh pemrograman (Python)", "Exemplos de programação (Python)", "Ezemplu programasaun (Python)"), True),
    ("atlas", "timor", L("Timor-Leste atlas and history", "Atlas dan sejarah Timor-Leste", "Atlas e história de Timor-Leste", "Atlas no istória Timor-Leste"), True),
    ("tasks", "activities", L("Tasks, timetable and reminders", "Tugas, jadwal, dan pengingat", "Trabalhos, horário e lembretes", "Knaar, orariu no fó-hanoin"), True),
    ("helpdesk", "oshelp", L("Edukasaun OS help", "Bantuan Edukasaun OS", "Ajuda do Edukasaun OS", "Ajuda Edukasaun OS"), True),
    ("files", "library", L("My files and saved material", "File saya dan materi tersimpan", "Os meus ficheiros e material guardado", "Ha'u-nia ficheiru no materiál rai ona"), True),
    ("calc", "home", L("Calculator and read aloud", "Kalkulator dan baca keras", "Calculadora e leitura em voz alta", "Kalkuladora no lee ho lian"), True),
    ("wikipedia", "library", L("Wikipedia extracts", "Kutipan Wikipedia", "Extratos da Wikipédia", "Estratu Wikipédia"), False),
    ("sources", "library", L("Learning websites and Timor-Leste media", "Situs belajar dan media Timor-Leste", "Sites de aprendizagem e media de Timor-Leste", "Sítiu aprendizajen no média Timor-Leste"), False),
    ("weather_news", "timor", L("Weather and news", "Cuaca dan berita", "Tempo e notícias", "Tempu no notísia"), False),
]

def offline_features(lang="en"):
    return [classroom.text(name, lang) for _, _, name, offline in FEATURES if offline]

def online_features(lang="en"):
    return [classroom.text(name, lang) for _, _, name, offline in FEATURES if not offline]

def _score(words, *texts):
    blob = " ".join(texts).casefold()
    return sum(1 for w in words if w in blob)

def answer(question, lang="en"):
    """Best match from LAFA's own knowledge (atlas, lessons), or None.

    A topic counts only when the question names it: the title must match, or
    (for longer questions) at least two words must. A single word that merely
    appears inside some text is left to Wikipedia."""
    words = [w.strip("?!.,;:") for w in str(question).casefold().split()]
    words = [w for w in words if len(w) >= 4]
    if not words: return None
    best = (0, 0, None)
    for t in timor_atlas.TOPICS:
        titled = _score(words, timor_atlas.text(t.title, lang), timor_atlas.text(t.title, "en"))
        score = 2 * titled + _score(words, timor_atlas.text(t.summary, lang), timor_atlas.text(t.summary, "en"))
        if score > best[0]:
            body = timor_atlas.text(t.body, lang) if t.body and (lang != "tet" or "tet" in t.body) else ""
            best = (score, titled, f"📘 {timor_atlas.text(t.title, lang)}\n{timor_atlas.text(t.summary, lang)}" + (f"\n\n{body}" if body else ""))
    for lesson in classroom.lessons():
        titled = _score(words, classroom.text(lesson.title, lang), classroom.text(lesson.title, "en"))
        score = 2 * titled + _score(words, *[classroom.text(p, lang) for p in lesson.points])
        if score > best[0]:
            best = (score, titled, f"📗 {classroom.subject_name(lesson.subject, lang)} · {classroom.text(lesson.title, lang)}\n" + "\n".join("• " + classroom.text(p, lang) for p in lesson.points))
    score, titled, text = best
    if titled or (len(words) >= 2 and score >= 3): return text
    return None
