"""LAFA's classroom: lessons (study material), quizzes, tests, exams and the
report card.

* Lessons   short study notes per subject with a task to try (offline).
* Quiz      5 questions with instant feedback (practice).
* Test      10 questions about one subject, results at the end (ulangan).
* Exam      20 questions from every subject with a time limit (ujian).
* Report    every result is saved on this computer and can be exported.

Questions come from the school banks (school.QUIZ), generated arithmetic,
vocabulary between LAFA's four languages and Timor-Leste history.
"""
from dataclasses import dataclass, field
from datetime import datetime
import random
import time

from . import school, timorleste
from .school import L, VOCAB, LANGS, _read, _write, data_dir

def text(value, lang):
    return value.get(lang, value["en"]) if isinstance(value, dict) else value

# ------------------------------------------------------------------ lessons
@dataclass(frozen=True)
class Lesson:
    subject: str
    title: dict
    points: tuple
    task: dict

LESSONS = [
    Lesson("math", L("Fractions", "Pecahan", "Frações", "Frasaun"),
           (L("A fraction is a part of a whole: 1/4 means 1 of 4 equal parts.", "Pecahan adalah bagian dari keseluruhan: 1/4 berarti 1 dari 4 bagian sama.", "Uma fração é parte de um todo: 1/4 é 1 de 4 partes iguais.", "Frasaun mak parte husi totál: 1/4 signifika parte 1 husi parte 4 hanesan."),
            L("To add fractions, the bottom numbers (denominators) must be the same: 1/4 + 2/4 = 3/4.", "Untuk menjumlah pecahan, penyebut harus sama: 1/4 + 2/4 = 3/4.", "Para somar frações, os denominadores têm de ser iguais: 1/4 + 2/4 = 3/4.", "Atu soma frasaun, denominadór tenke hanesan: 1/4 + 2/4 = 3/4."),
            L("Equal fractions: 1/2 = 2/4 = 50/100 = 50%.", "Pecahan senilai: 1/2 = 2/4 = 50/100 = 50%.", "Frações equivalentes: 1/2 = 2/4 = 50/100 = 50%.", "Frasaun hanesan: 1/2 = 2/4 = 50/100 = 50%.")),
           L("A papaya is cut into 8 pieces. You eat 3. What fraction is left?", "Pepaya dipotong 8. Kamu makan 3. Berapa bagian tersisa?", "Uma papaia é cortada em 8. Comes 3. Que fração sobra?", "Ai-dila tesi ba parte 8. Ita han 3. Frasaun hira mak sobra?")),
    Lesson("math", L("Area and perimeter", "Luas dan keliling", "Área e perímetro", "Área no perímetru"),
           (L("Perimeter is the distance around a shape: add all the sides.", "Keliling adalah jarak mengelilingi bangun: jumlahkan semua sisi.", "Perímetro é a volta da figura: soma todos os lados.", "Perímetru mak distánsia haleu forma: soma lados hotu."),
            L("Area of a rectangle = length × width (in square metres, m²).", "Luas persegi panjang = panjang × lebar (dalam meter persegi, m²).", "Área do retângulo = comprimento × largura (em m²).", "Área retángulu = naruk × luan (iha metru kuadradu, m²)."),
            L("A 10 m × 6 m school garden has area 60 m² and perimeter 32 m.", "Kebun sekolah 10 m × 6 m luasnya 60 m² dan kelilingnya 32 m.", "Uma horta de 10 m × 6 m tem 60 m² de área e 32 m de perímetro.", "To'os eskola 10 m × 6 m iha área 60 m² no perímetru 32 m.")),
           L("Measure your classroom door. What is its area?", "Ukur pintu kelasmu. Berapa luasnya?", "Mede a porta da sala. Qual é a área?", "Sukat odamatan sala. Ninia área hira?")),
    Lesson("science", L("The water cycle", "Siklus air", "O ciclo da água", "Siklu bee"),
           (L("The Sun heats the sea; water evaporates and rises as vapour.", "Matahari memanaskan laut; air menguap dan naik sebagai uap.", "O Sol aquece o mar; a água evapora e sobe como vapor.", "Loro-matan halo tasi manas; bee sai suar no sa'e."),
            L("Vapour cools in the sky and condenses into clouds.", "Uap mendingin di langit dan mengembun menjadi awan.", "O vapor arrefece e condensa em nuvens.", "Suar sai malirin iha lalehan no sai kalohan."),
            L("Rain falls on the mountains (like Ramelau) and flows back to the sea in rivers.", "Hujan turun di gunung (seperti Ramelau) dan mengalir kembali ke laut lewat sungai.", "A chuva cai nas montanhas (como o Ramelau) e volta ao mar pelos rios.", "Udan tau iha foho (hanesan Ramelau) no suli fila ba tasi liu husi mota.")),
           L("Draw the water cycle with arrows and labels.", "Gambarlah siklus air dengan panah dan keterangan.", "Desenha o ciclo da água com setas e legendas.", "Dezeña siklu bee ho seta no naran.")),
    Lesson("science", L("Coral reefs of Timor-Leste", "Terumbu karang Timor-Leste", "Recifes de coral de Timor-Leste", "Ahu-ruin Timor-Leste"),
           (L("Corals are tiny animals that build reefs; reefs are homes for fish.", "Karang adalah hewan kecil yang membangun terumbu; terumbu adalah rumah ikan.", "Os corais são pequenos animais que constroem recifes, casa de peixes.", "Ahu-ruin mak animál ki'ik ne'ebé harii uma ba ikan."),
            L("The sea around Ataúro has some of the richest reef life measured in the world.", "Laut di sekitar Ataúro memiliki kehidupan terumbu terkaya di dunia yang pernah diukur.", "O mar à volta de Ataúro tem das maiores diversidades de vida em recife medidas no mundo.", "Tasi haleu Ataúro iha moris ahu-ruin riku liu ida iha mundu."),
            L("Plastic and dynamite fishing hurt reefs; clean beaches protect them.", "Plastik dan bom ikan merusak terumbu; pantai bersih melindunginya.", "Plástico e pesca com explosivos destroem recifes; praias limpas protegem-nos.", "Plástiku no kaer ikan ho bomba estraga ahu-ruin; tasi-ibun moos proteje sira.")),
           L("List three things your class can do to protect the sea.", "Tulis tiga hal yang bisa dilakukan kelasmu untuk melindungi laut.", "Escreve três coisas que a turma pode fazer para proteger o mar.", "Hakerek buat tolu ne'ebé ita-nia klase bele halo atu proteje tasi.")),
    Lesson("languages", L("Greetings in four languages", "Salam dalam empat bahasa", "Saudações em quatro línguas", "Kumprimentu iha lian haat"),
           (L("Tetun: Bondia, Botarde, Bonoite. Portuguese: Bom dia, Boa tarde, Boa noite.", "Tetun: Bondia, Botarde, Bonoite. Portugis: Bom dia, Boa tarde, Boa noite.", "Tétum: Bondia, Botarde, Bonoite. Português: Bom dia, Boa tarde, Boa noite.", "Tetun: Bondia, Botarde, Bonoite. Portugés: Bom dia, Boa tarde, Boa noite."),
            L("English: Good morning, Good afternoon, Good evening.", "Inggris: Good morning, Good afternoon, Good evening.", "Inglês: Good morning, Good afternoon, Good evening.", "Inglés: Good morning, Good afternoon, Good evening."),
            L("Indonesian: Selamat pagi, Selamat siang, Selamat malam.", "Indonesia: Selamat pagi, Selamat siang, Selamat malam.", "Indonésio: Selamat pagi, Selamat siang, Selamat malam.", "Indonézia: Selamat pagi, Selamat siang, Selamat malam.")),
           L("Greet three classmates, each in a different language.", "Sapa tiga teman, masing-masing dengan bahasa berbeda.", "Cumprimenta três colegas, cada um numa língua diferente.", "Kumprimenta kolega na'in tolu, ida-idak ho lian diferente.")),
    Lesson("languages", L("Writing a good paragraph", "Menulis paragraf yang baik", "Escrever um bom parágrafo", "Hakerek parágrafu di'ak"),
           (L("Start with one main idea (topic sentence).", "Mulai dengan satu gagasan utama (kalimat topik).", "Começa com uma ideia principal (frase-tópico).", "Hahú ho ideia prinsipál ida (fraze tópiku)."),
            L("Add two or three sentences with details or examples.", "Tambahkan dua atau tiga kalimat dengan rincian atau contoh.", "Junta duas ou três frases com detalhes ou exemplos.", "Aumenta fraze rua ka tolu ho detallu ka ezemplu."),
            L("End with a closing sentence. Read it aloud and check spelling.", "Akhiri dengan kalimat penutup. Bacakan dan periksa ejaan.", "Termina com uma frase de conclusão. Lê em voz alta e revê a ortografia.", "Remata ho fraze taka. Lee ho lian maka'as no haree ortografia.")),
           L("Write a paragraph about your favourite place in your suco.", "Tulis satu paragraf tentang tempat favoritmu di sucomu.", "Escreve um parágrafo sobre o teu lugar preferido no teu suco.", "Hakerek parágrafu ida kona-ba ita-nia fatin favoritu iha suku.")),
    Lesson("ict", L("Staying safe online", "Aman di internet", "Segurança na internet", "Seguru iha internet"),
           (L("Use long, secret passwords; never share them.", "Gunakan kata sandi panjang dan rahasia; jangan dibagikan.", "Usa palavras-passe longas e secretas; nunca as partilhes.", "Uza password naruk no segredu; keta fahe."),
            L("Think before you post: photos and words can stay online forever.", "Pikir sebelum mengunggah: foto dan kata bisa tersimpan selamanya.", "Pensa antes de publicar: fotos e palavras podem ficar para sempre.", "Hanoin uluk molok publika: foto no liafuan bele hela ba nafatin."),
            L("Check news with two trusted sources before sharing.", "Periksa berita dengan dua sumber tepercaya sebelum membagikan.", "Confirma notícias em duas fontes fiáveis antes de partilhar.", "Verifika notísia ho fonte rua ne'ebé fiar molok fahe.")),
           L("Make a poster with five online safety rules.", "Buat poster lima aturan aman di internet.", "Faz um cartaz com cinco regras de segurança online.", "Halo póster ho regra seguransa online lima.")),
    Lesson("ict", L("First steps in Python", "Langkah pertama Python", "Primeiros passos em Python", "Pasu dahuluk iha Python"),
           (L("print('Bondia!') shows text on the screen.", "print('Bondia!') menampilkan teks di layar.", "print('Bondia!') mostra texto no ecrã.", "print('Bondia!') hatudu testu iha ekrán."),
            L("Variables keep values: idade = 12.", "Variabel menyimpan nilai: idade = 12.", "Variáveis guardam valores: idade = 12.", "Variavel rai valór: idade = 12."),
            L("A loop repeats: for i in range(3): print(i)", "Perulangan mengulang: for i in range(3): print(i)", "Um ciclo repete: for i in range(3): print(i)", "Loop halo dala barak: for i in range(3): print(i)")),
           L("Open the Computer lab and run your first program.", "Buka Lab komputer dan jalankan program pertamamu.", "Abre o laboratório e corre o teu primeiro programa.", "Loke laboratóriu komputadór no hala'o ita-nia programa dahuluk.")),
    Lesson("arts", L("Tais: the cloth of Timor", "Tais: kain Timor", "Tais: o tecido de Timor", "Tais: hena Timor nian"),
           (L("Tais is woven by hand, mostly by women, on a back-strap loom.", "Tais ditenun dengan tangan, sebagian besar oleh perempuan, dengan alat tenun gendong.", "O tais é tecido à mão, sobretudo por mulheres, em teares de cintura.", "Tais soru ho liman, barak liu feto sira, ho atis tradisionál."),
            L("Each region has its own colours and patterns; they tell stories.", "Setiap daerah punya warna dan motif sendiri; motif itu bercerita.", "Cada região tem as suas cores e padrões, que contam histórias.", "Rejiaun ida-idak iha kór no motivu rasik; motivu konta istória."),
            L("In 2021 UNESCO listed tais as heritage that needs urgent safeguarding.", "Pada 2021 UNESCO mencatat tais sebagai warisan yang perlu dilindungi segera.", "Em 2021 a UNESCO inscreveu o tais como património que precisa de salvaguarda urgente.", "Iha 2021 UNESCO rejista tais hanesan patrimóniu ne'ebé presiza proteje lalais.")),
           L("Ask an older relative what the patterns of your family's tais mean.", "Tanyakan kepada kerabat tua arti motif tais keluargamu.", "Pergunta a um familiar mais velho o que significam os padrões do tais da família.", "Husu ba família boot sira saida mak motivu tais família nian signifika.")),
    Lesson("arts", L("Music and dance", "Musik dan tari", "Música e dança", "Múzika no dansa"),
           (L("Tebe is a circle dance where people hold hands and sing together.", "Tebe adalah tarian melingkar sambil bergandengan tangan dan bernyanyi.", "O tebe é uma dança em círculo, de mãos dadas, a cantar.", "Tebe mak dansa sírkulu, kaer liman no kanta hamutuk."),
            L("Likurai is danced with small drums (babadok) to welcome heroes.", "Likurai ditarikan dengan gendang kecil (babadok) untuk menyambut pahlawan.", "O likurai dança-se com pequenos tambores (babadok) para receber heróis.", "Likurai dansa ho babadok atu simu eroi sira."),
            L("Music has rhythm (beat), melody (tune) and harmony.", "Musik punya ritme (ketukan), melodi (nada) dan harmoni.", "A música tem ritmo, melodia e harmonia.", "Múzika iha ritmu, melodia no armonia.")),
           L("Clap the rhythm of a song you know and teach it to a friend.", "Tepuk irama lagu yang kamu tahu dan ajarkan ke teman.", "Bate palmas ao ritmo de uma canção e ensina-a a um amigo.", "Baku liman tuir ritmu kanta ida no hanorin ba belun.")),
]

def lessons(subject=None):
    out = [l for l in LESSONS if subject in (None, l.subject)]
    if subject in (None, "history"):
        # Timor-Leste history lessons: one per era, built from the timeline.
        for key, title, _ in timorleste.ERAS:
            events = timorleste.events(key)
            points = tuple({lang: f"{e.when(lang)} · {text(e.title, lang)}: {text(e.text, lang)}" for lang in LANGS} for e in events)
            out.append(Lesson("history", title, points, L("Make a timeline of this era in your notebook.", "Buat garis waktu era ini di buku catatanmu.", "Faz uma linha do tempo desta época no caderno.", "Halo liña tempu ba era ne'e iha kadernu.")))
    return out

# ---------------------------------------------------------------- questions
@dataclass
class Question:
    text: str
    options: list
    correct: str
    subject: str

SUBJECTS = ["math", "science", "languages", "history", "ict", "arts"]
VOCAB_Q = L("How do you say “{word}” in {target}?", "Apa bahasa {target} dari “{word}”?", "Como se diz “{word}” em {target}?", "Oinsá atu dehan “{word}” iha {target}?")
LANG_NAMES = {"en": L("English", "Inggris", "inglês", "Inglés"), "id": L("Indonesian", "Indonesia", "indonésio", "Indonézia"),
              "pt": L("Portuguese", "Portugis", "português", "Portugés"), "tet": L("Tetun", "Tetun", "tétum", "Tetun")}

def _math(lang, rng, n):
    out = []; practice = school.MathPractice(rng)
    for i in range(n):
        q = practice.new(1 + i % 3); a = practice.answer
        options = {a}
        while len(options) < 4: options.add(a + rng.choice([-10, -2, -1, 1, 2, 3, 10]))
        options = [str(o) for o in options]; rng.shuffle(options)
        out.append(Question(q, options, str(a), "math"))
    return out

def _vocab(lang, rng, n):
    out = []
    for _ in range(n):
        targets = [l for l in LANGS if l != lang]; target = rng.choice(targets)
        card = rng.choice(VOCAB); s, t = LANGS.index(lang), LANGS.index(target)
        options = {card[t]}
        while len(options) < 4: options.add(rng.choice(VOCAB)[t])
        options = list(options); rng.shuffle(options)
        out.append(Question(text(VOCAB_Q, lang).format(word=card[s], target=text(LANG_NAMES[target], lang)), options, card[t], "languages"))
    return out

def _bank(subject, lang, rng):
    out = []
    for question, options in school.QUIZ.get(subject, []):
        texts = [text(o, lang) for o in options]; correct = texts[0]; rng.shuffle(texts)
        out.append(Question(text(question, lang), texts, correct, subject))
    if subject == "history":
        out += [Question(q, o, c, "history") for q, o, c in timorleste.history_questions(lang, rng)]
    return out

def questions(subject, lang="en", count=10, rng=None):
    """`count` different questions about a subject ("all" mixes every subject)."""
    rng = rng or random.Random()
    if subject == "all":
        per = max(1, -(-count // len(SUBJECTS))); pool = []
        for s in SUBJECTS: pool += questions(s, lang, per, rng)
        rng.shuffle(pool); return pool[:count]
    if subject == "math": return _math(lang, rng, count)
    if subject == "languages": return _vocab(lang, rng, count)
    pool = _bank(subject, lang, rng); rng.shuffle(pool)
    while len(pool) < count and pool: pool += pool[:count - len(pool)]
    return pool[:count]

# -------------------------------------------------------------------- exams
KINDS = {"quiz": (5, 0), "test": (10, 0), "exam": (20, 20 * 60)}   # questions, seconds (0 = no limit)

GRADES = [
    (90, L("Excellent", "Istimewa", "Excelente", "Exelente")),
    (75, L("Very good", "Sangat baik", "Muito bom", "Di'ak liu")),
    (60, L("Good", "Baik", "Bom", "Di'ak")),
    (50, L("Pass", "Cukup", "Suficiente", "Natoon")),
    (0, L("Keep practising", "Terus berlatih", "Continua a praticar", "Kontinua pratika")),
]

def grade(percent, lang="en"):
    for limit, name in GRADES:
        if percent >= limit: return text(name, lang)

class ExamSession:
    """One quiz, test or exam. Answers are checked on this computer."""
    def __init__(self, kind="quiz", subject="all", lang="en", rng=None, clock=time.monotonic):
        if kind not in KINDS: raise ValueError("Unknown exam kind.")
        if subject != "all" and subject not in SUBJECTS: raise ValueError("Unknown subject.")
        self.kind, self.subject, self.lang, self.clock = kind, subject, lang, clock
        count, self.limit = KINDS[kind]
        self.items = questions(subject, lang, count, rng); self.index = 0; self.answers = []; self.started = clock()
    @property
    def current(self):
        return self.items[self.index] if not self.finished else None
    @property
    def finished(self):
        return self.index >= len(self.items) or self.time_left() == 0
    def time_left(self):
        if not self.limit: return None
        return max(0, int(self.limit - (self.clock() - self.started)))
    def answer(self, choice):
        if self.finished: return False
        q = self.items[self.index]; ok = choice == q.correct
        self.answers.append((q, choice, ok)); self.index += 1; return ok
    @property
    def score(self): return sum(1 for _, _, ok in self.answers if ok)
    @property
    def total(self): return len(self.items)
    @property
    def percent(self): return round(100 * self.score / self.total) if self.total else 0
    def mistakes(self):
        return [(q, choice) for q, choice, ok in self.answers if not ok]

# ------------------------------------------------------------- report card
class ReportCard:
    """Results of quizzes, tests and exams, kept in ~/.local/share/lafa/report.json."""
    def __init__(self, folder=None):
        self.path = (data_dir() if folder is None else __import__("pathlib").Path(folder)) / "report.json"
        self.entries = [e for e in _read(self.path, []) if isinstance(e, dict) and {"when", "kind", "subject", "score", "total"} <= e.keys()][-1000:]
    def add(self, session):
        entry = {"when": datetime.now().strftime("%Y-%m-%d %H:%M"), "kind": session.kind, "subject": session.subject,
                 "score": session.score, "total": session.total}
        self.entries.append(entry); _write(self.path, self.entries); return entry
    def summary(self):
        """subject -> (attempts, best %, average %)"""
        out = {}
        for e in self.entries:
            p = round(100 * e["score"] / e["total"]) if e["total"] else 0
            attempts, best, total = out.get(e["subject"], (0, 0, 0))
            out[e["subject"]] = (attempts + 1, max(best, p), total + p)
        return {s: (a, b, round(t / a)) for s, (a, b, t) in out.items()}
    def export_text(self, lang="en", name=""):
        from .i18n import tr
        lines = [f"LAFA · {tr(lang, 'report_card')}" + (f" · {name}" if name else ""), datetime.now().strftime("%Y-%m-%d"), ""]
        for subject, (attempts, best, average) in sorted(self.summary().items()):
            lines.append(f"{subject_name(subject, lang)}: {tr(lang, 'average')} {average}% · {tr(lang, 'best')} {best}% · {attempts}× · {grade(average, lang)}")
        lines += ["", tr(lang, "history_label")]
        for e in reversed(self.entries[-50:]):
            lines.append(f"{e['when']}  {tr(lang, e['kind'])}  {subject_name(e['subject'], lang)}  {e['score']}/{e['total']}")
        return "\n".join(lines) + "\n"

def subject_name(subject, lang):
    if subject == "all":
        from .i18n import tr
        return tr(lang, "all_subjects")
    teacher = school.BY_KEY.get(subject)
    return teacher.text("name", lang) if teacher else subject
