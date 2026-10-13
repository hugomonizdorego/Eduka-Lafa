"""What LAFA can do without internet, and answers from LAFA's own knowledge.

LAFA keeps working offline: the classroom, exams, report card, homework, the
Timor-Leste atlas (built-in text), world language courses, the computer lab,
the IT help desk, files, reminders, roles and the Virtual Assistant. Features
that need the internet (AI chat, Wikipedia search, weather, news, online
refresh of sources) wait until the connection is back.
"""
from .school import L
from . import timor_atlas, classroom, osguide

# (key, page, name, works offline)
FEATURES = [
    ("classroom", "classroom", L("Classroom lessons", "Pelajaran di kelas", "Aulas", "Lisaun iha klase"), True),
    ("exams", "exams", L("Quizzes, tests and exams", "Kuis, ulangan dan ujian", "Quizzes, testes e exames", "Kuis, teste no ezame"), True),
    ("report", "report", L("Report card", "Rapor", "Boletim", "Boletin"), True),
    ("homework", "homework", L("Homework & timetable", "PR & jadwal", "Trabalhos e horário", "TPC no orariu"), True),
    ("atlas", "culture", L("Timor-Leste atlas", "Atlas Timor-Leste", "Atlas de Timor-Leste", "Atlas Timor-Leste"), True),
    ("languages", "languages", L("World language courses", "Kursus bahasa dunia", "Cursos de línguas do mundo", "Kursu lian mundu"), True),
    ("lab", "coding", L("Computer lab (Python)", "Lab komputer (Python)", "Laboratório (Python)", "Laboratóriu (Python)"), True),
    ("helpdesk", "os_help", L("Edukasaun OS help desk", "Bantuan Edukasaun OS", "Ajuda do Edukasaun OS", "Ajuda Edukasaun OS"), True),
    ("files", "files", L("My files", "File saya", "Os meus ficheiros", "Ha'u-nia ficheiru"), True),
    ("reminders", "reminders", L("Reminders & focus", "Pengingat & fokus", "Lembretes e foco", "Lembransa no foku"), True),
    ("local_chat", "chat", L("Ask LAFA (offline answers, /calc, /os)", "Tanya LAFA (jawaban offline, /calc, /os)", "Perguntar ao LAFA (respostas offline, /calc, /os)", "Husu LAFA (resposta offline, /calc, /os)"), True),
    ("ai_chat", "chat", L("AI chat and teachers", "Chat AI dan guru", "Conversa com IA e professores", "Konversa AI no mestre"), False),
    ("wikipedia", "learn", L("Wikipedia search", "Pencarian Wikipedia", "Pesquisa na Wikipédia", "Buka Wikipédia"), False),
    ("sources", "learn", L("Learning websites (79)", "Situs belajar (79)", "Sites de aprendizagem (79)", "Sítiu aprendizajen (79)"), False),
    ("weather_news", "live", L("Weather and news", "Cuaca dan berita", "Tempo e notícias", "Tempu no notísia"), False),
    ("live_refresh", "culture", L("Hourly refresh of sources and atlas", "Pembaruan sumber dan atlas tiap jam", "Atualização horária de fontes e atlas", "Atualizasaun kada oras ba fonte no atlas"), False),
]

def offline_features(lang="en"):
    return [classroom.text(name, lang) for _, _, name, offline in FEATURES if offline]

def online_features(lang="en"):
    return [classroom.text(name, lang) for _, _, name, offline in FEATURES if not offline]

def _score(words, *texts):
    blob = " ".join(texts).casefold()
    return sum(1 for w in words if w in blob)

def answer(question, lang="en"):
    """Best match from LAFA's own knowledge (atlas, lessons, OS guides), or None."""
    words = [w.strip("?!.,;:") for w in str(question).casefold().split()]
    words = [w for w in words if len(w) >= 4]
    if not words: return None
    best = (0, None)
    for t in timor_atlas.TOPICS:
        score = 2 * _score(words, timor_atlas.text(t.title, lang), timor_atlas.text(t.title, "en")) + _score(words, timor_atlas.text(t.summary, lang), timor_atlas.text(t.summary, "en"))
        if score > best[0]:
            body = timor_atlas.text(t.body, lang) if t.body else ""
            best = (score, f"📘 {timor_atlas.text(t.title, lang)}\n{timor_atlas.text(t.summary, lang)}" + (f"\n\n{body}" if body else ""))
    for lesson in classroom.lessons():
        score = 2 * _score(words, classroom.text(lesson.title, lang), classroom.text(lesson.title, "en")) + _score(words, *[classroom.text(p, lang) for p in lesson.points])
        if score > best[0]:
            best = (score, f"📗 {classroom.subject_name(lesson.subject, lang)} · {classroom.text(lesson.title, lang)}\n" + "\n".join("• " + classroom.text(p, lang) for p in lesson.points))
    return best[1] if best[0] >= max(1, min(2, len(words))) else None
