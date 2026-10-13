"""LAFA's language school: first courses in world languages.

Every course has the same 25 everyday phrases in five units (greetings,
introductions, school, numbers, daily life), with a pronunciation guide for
languages that do not use the Latin alphabet, and a quiz. Meanings are shown
in the learner's language (English, Indonesian, Portuguese or Tetun). The
online sites from LAFA's source directory (Duolingo, BBC Languages, SEAsite,
Portuguese Lab, …) continue the course when the computer is online.
"""
import random
from .school import L

UNITS = [
    ("greetings", L("Greetings", "Salam", "Saudações", "Kumprimentu"), ["hello", "good_morning", "thank_you", "please", "sorry", "goodbye"]),
    ("introductions", L("Introductions", "Perkenalan", "Apresentações", "Aprezenta an"), ["my_name", "how_are_you", "im_fine", "nice_to_meet"]),
    ("school", L("At school", "Di sekolah", "Na escola", "Iha eskola"), ["teacher", "student", "school", "book", "friend"]),
    ("numbers", L("Numbers", "Angka", "Números", "Númeru"), ["one", "two", "three", "ten"]),
    ("daily", L("Daily life", "Sehari-hari", "Dia a dia", "Loron-loron"), ["water", "rice", "eat", "family", "yes", "no"]),
]

MEANINGS = {
    "hello": L("Hello", "Halo", "Olá", "Olá"), "good_morning": L("Good morning", "Selamat pagi", "Bom dia", "Bondia"),
    "thank_you": L("Thank you", "Terima kasih", "Obrigado", "Obrigadu"), "please": L("Please", "Tolong", "Por favor", "Favór"),
    "sorry": L("Sorry", "Maaf", "Desculpe", "Deskulpa"), "goodbye": L("Goodbye", "Selamat tinggal", "Adeus", "Adeus"),
    "my_name": L("My name is …", "Nama saya …", "Chamo-me …", "Ha'u-nia naran …"), "how_are_you": L("How are you?", "Apa kabar?", "Como está?", "Di'ak ka lae?"),
    "im_fine": L("I am fine", "Saya baik", "Estou bem", "Ha'u di'ak"), "nice_to_meet": L("Nice to meet you", "Senang bertemu Anda", "Muito prazer", "Kontente hasoru ita"),
    "teacher": L("teacher", "guru", "professor", "mestre"), "student": L("student", "siswa", "aluno", "estudante"),
    "school": L("school", "sekolah", "escola", "eskola"), "book": L("book", "buku", "livro", "livru"), "friend": L("friend", "teman", "amigo", "belun"),
    "one": L("one", "satu", "um", "ida"), "two": L("two", "dua", "dois", "rua"), "three": L("three", "tiga", "três", "tolu"), "ten": L("ten", "sepuluh", "dez", "sanulu"),
    "water": L("water", "air", "água", "bee"), "rice": L("rice", "nasi", "arroz", "etu"), "eat": L("to eat", "makan", "comer", "han"),
    "family": L("family", "keluarga", "família", "família"), "yes": L("yes", "ya", "sim", "sin"), "no": L("no", "tidak", "não", "lae"),
}
ORDER = [c for _, _, items in UNITS for c in items]

def P(*pairs):
    """Phrases in ORDER: each item is "text" or ("text", "pronunciation")."""
    assert len(pairs) == len(ORDER)
    return {key: (p if isinstance(p, tuple) else (p, "")) for key, p in zip(ORDER, pairs)}

# code: (name, speech code for espeak-ng, region, phrases)
COURSES = {
    "tet": (L("Tetun", "Tetun", "Tétum", "Tetun"), "pt", "timor", P("Olá", "Bondia", "Obrigadu / Obrigada", "Favór", "Deskulpa", "Adeus",
            "Ha'u-nia naran …", "Di'ak ka lae?", "Ha'u di'ak", "Kontente hasoru ita", "mestre", "estudante", "eskola", "livru", "belun",
            "ida", "rua", "tolu", "sanulu", "bee", "etu", "han", "família", "sin", "lae")),
    "pt": (L("Portuguese", "Portugis", "Português", "Portugés"), "pt", "official", P("Olá", "Bom dia", "Obrigado / Obrigada", "Por favor", "Desculpe", "Adeus",
            "Chamo-me …", "Como está?", "Estou bem", "Muito prazer", "professor", "aluno", "escola", "livro", "amigo",
            "um", "dois", "três", "dez", "água", "arroz", "comer", "família", "sim", "não")),
    "id": (L("Indonesian", "Indonesia", "Indonésio", "Indonézia"), "id", "asean", P("Halo", "Selamat pagi", "Terima kasih", "Tolong", "Maaf", "Selamat tinggal",
            "Nama saya …", "Apa kabar?", "Kabar baik", "Senang bertemu Anda", "guru", "siswa", "sekolah", "buku", "teman",
            "satu", "dua", "tiga", "sepuluh", "air", "nasi", "makan", "keluarga", "ya", "tidak")),
    "en": (L("English", "Inggris", "Inglês", "Inglés"), "en", "world", P("Hello", "Good morning", "Thank you", "Please", "Sorry", "Goodbye",
            "My name is …", "How are you?", "I'm fine", "Nice to meet you", "teacher", "student", "school", "book", "friend",
            "one", "two", "three", "ten", "water", "rice", "to eat", "family", "yes", "no")),
    "es": (L("Spanish", "Spanyol", "Espanhol", "Españól"), "es", "world", P("Hola", "Buenos días", "Gracias", "Por favor", "Lo siento", "Adiós",
            "Me llamo …", "¿Cómo estás?", "Estoy bien", "Mucho gusto", "profesor", "estudiante", "escuela", "libro", "amigo",
            "uno", "dos", "tres", "diez", "agua", "arroz", "comer", "familia", "sí", "no")),
    "fr": (L("French", "Prancis", "Francês", "Fransés"), "fr", "world", P("Salut", "Bonjour", "Merci", "S'il vous plaît", "Pardon", "Au revoir",
            "Je m'appelle …", "Comment allez-vous ?", "Je vais bien", "Enchanté", "professeur", "élève", "école", "livre", "ami",
            "un", "deux", "trois", "dix", "eau", "riz", "manger", "famille", "oui", "non")),
    "de": (L("German", "Jerman", "Alemão", "Alemaun"), "de", "world", P("Hallo", "Guten Morgen", "Danke", "Bitte", "Entschuldigung", "Auf Wiedersehen",
            "Ich heiße …", "Wie geht es Ihnen?", "Mir geht es gut", "Freut mich", "Lehrer", "Schüler", "Schule", "Buch", "Freund",
            "eins", "zwei", "drei", "zehn", "Wasser", "Reis", "essen", "Familie", "ja", "nein")),
    "zh": (L("Mandarin Chinese", "Mandarin", "Mandarim", "Mandarin"), "cmn", "asia", P(("你好", "nǐ hǎo"), ("早上好", "zǎoshang hǎo"), ("谢谢", "xièxie"), ("请", "qǐng"), ("对不起", "duìbuqǐ"), ("再见", "zàijiàn"),
            ("我叫…", "wǒ jiào …"), ("你好吗？", "nǐ hǎo ma?"), ("我很好", "wǒ hěn hǎo"), ("很高兴认识你", "hěn gāoxìng rènshi nǐ"), ("老师", "lǎoshī"), ("学生", "xuésheng"), ("学校", "xuéxiào"), ("书", "shū"), ("朋友", "péngyou"),
            ("一", "yī"), ("二", "èr"), ("三", "sān"), ("十", "shí"), ("水", "shuǐ"), ("米饭", "mǐfàn"), ("吃", "chī"), ("家人", "jiārén"), ("是", "shì"), ("不", "bù"))),
    "ja": (L("Japanese", "Jepang", "Japonês", "Japonés"), "ja", "asia", P(("こんにちは", "konnichiwa"), ("おはようございます", "ohayō gozaimasu"), ("ありがとう", "arigatō"), ("お願いします", "onegaishimasu"), ("すみません", "sumimasen"), ("さようなら", "sayōnara"),
            ("私の名前は…です", "watashi no namae wa … desu"), ("お元気ですか", "o-genki desu ka?"), ("元気です", "genki desu"), ("はじめまして", "hajimemashite"), ("先生", "sensei"), ("学生", "gakusei"), ("学校", "gakkō"), ("本", "hon"), ("友達", "tomodachi"),
            ("一", "ichi"), ("二", "ni"), ("三", "san"), ("十", "jū"), ("水", "mizu"), ("ご飯", "gohan"), ("食べる", "taberu"), ("家族", "kazoku"), ("はい", "hai"), ("いいえ", "iie"))),
    "ko": (L("Korean", "Korea", "Coreano", "Koreanu"), "ko", "asia", P(("안녕하세요", "annyeonghaseyo"), ("좋은 아침이에요", "joeun achimieyo"), ("감사합니다", "gamsahamnida"), ("부탁합니다", "butakamnida"), ("죄송합니다", "joesonghamnida"), ("안녕히 가세요", "annyeonghi gaseyo"),
            ("제 이름은 …입니다", "je ireumeun … imnida"), ("잘 지내세요?", "jal jinaeseyo?"), ("잘 지내요", "jal jinaeyo"), ("만나서 반갑습니다", "mannaseo bangapseumnida"), ("선생님", "seonsaengnim"), ("학생", "haksaeng"), ("학교", "hakgyo"), ("책", "chaek"), ("친구", "chingu"),
            ("하나", "hana"), ("둘", "dul"), ("셋", "set"), ("열", "yeol"), ("물", "mul"), ("밥", "bap"), ("먹다", "meokda"), ("가족", "gajok"), ("네", "ne"), ("아니요", "aniyo"))),
    "ar": (L("Arabic", "Arab", "Árabe", "Árabe"), "ar", "world", P(("مرحبا", "marḥaban"), ("صباح الخير", "ṣabāḥ al-khayr"), ("شكرا", "shukran"), ("من فضلك", "min faḍlak"), ("آسف", "āsif"), ("مع السلامة", "maʿa as-salāma"),
            ("اسمي …", "ismī …"), ("كيف حالك؟", "kayfa ḥāluk?"), ("أنا بخير", "anā bikhayr"), ("تشرفنا", "tasharrafnā"), ("معلم", "muʿallim"), ("طالب", "ṭālib"), ("مدرسة", "madrasa"), ("كتاب", "kitāb"), ("صديق", "ṣadīq"),
            ("واحد", "wāḥid"), ("اثنان", "ithnān"), ("ثلاثة", "thalātha"), ("عشرة", "ʿashara"), ("ماء", "māʾ"), ("أرز", "aruzz"), ("أكل", "akala"), ("عائلة", "ʿāʾila"), ("نعم", "naʿam"), ("لا", "lā"))),
    "th": (L("Thai", "Thai", "Tailandês", "Tailandés"), "th", "asean", P(("สวัสดี", "sawatdi"), ("อรุณสวัสดิ์", "arun sawat"), ("ขอบคุณ", "khop khun"), ("กรุณา", "karuna"), ("ขอโทษ", "kho thot"), ("ลาก่อน", "la kon"),
            ("ฉันชื่อ…", "chan chue …"), ("สบายดีไหม", "sabai di mai?"), ("สบายดี", "sabai di"), ("ยินดีที่ได้รู้จัก", "yindi thi dai ruchak"), ("ครู", "khru"), ("นักเรียน", "nak rian"), ("โรงเรียน", "rong rian"), ("หนังสือ", "nangsue"), ("เพื่อน", "phuean"),
            ("หนึ่ง", "nueng"), ("สอง", "song"), ("สาม", "sam"), ("สิบ", "sip"), ("น้ำ", "nam"), ("ข้าว", "khao"), ("กิน", "kin"), ("ครอบครัว", "khrop khrua"), ("ใช่", "chai"), ("ไม่", "mai"))),
    "vi": (L("Vietnamese", "Vietnam", "Vietnamita", "Vietnamita"), "vi", "asean", P("Xin chào", "Chào buổi sáng", "Cảm ơn", "Làm ơn", "Xin lỗi", "Tạm biệt",
            "Tôi tên là …", "Bạn khỏe không?", "Tôi khỏe", "Rất vui được gặp bạn", "giáo viên", "học sinh", "trường học", "sách", "bạn",
            "một", "hai", "ba", "mười", "nước", "cơm", "ăn", "gia đình", "vâng", "không")),
    "tl": (L("Filipino", "Filipina", "Filipino", "Filipinu"), "tl", "asean", P("Kumusta", "Magandang umaga", "Salamat", "Pakiusap", "Paumanhin", "Paalam",
            "Ako si …", "Kumusta ka?", "Mabuti", "Ikinagagalak kitang makilala", "guro", "estudyante", "paaralan", "aklat", "kaibigan",
            "isa", "dalawa", "tatlo", "sampu", "tubig", "kanin", "kumain", "pamilya", "oo", "hindi")),
}
REGIONS = {"timor": L("Timor-Leste", "Timor-Leste", "Timor-Leste", "Timor-Leste"), "official": L("Official language", "Bahasa resmi", "Língua oficial", "Lian ofisiál"),
           "asean": L("ASEAN", "ASEAN", "ASEAN", "ASEAN"), "asia": L("Asia", "Asia", "Ásia", "Ázia"), "world": L("World", "Dunia", "Mundo", "Mundu")}
# Open courses that continue online (names from lafa/sources.py).
ONLINE_COURSES = ["Duolingo", "BBC Languages", "SEAsite", "Portuguese Lab", "Busuu", "Memrise", "Tandem"]

def text(value, lang):
    return value.get(lang) or value["en"]

def phrases(code, unit=None):
    """[(concept, text, pronunciation)] for a course (optionally one unit)."""
    items = next((u[2] for u in UNITS if u[0] == unit), ORDER) if unit else ORDER
    table = COURSES[code][3]
    return [(c, table[c][0], table[c][1]) for c in items]

class LanguageQuiz:
    """Show a phrase in the course language; choose its meaning."""
    def __init__(self, code, lang="en", rng=None):
        self.code, self.lang, self.rng = code, lang, rng or random.Random(); self.correct = ""; self.right = self.total = 0; self.previous = None
    def new(self):
        choices = [c for c in ORDER if c != self.previous]; concept = self.rng.choice(choices); self.previous = concept
        text_, say = COURSES[self.code][3][concept]
        self.correct = text(MEANINGS[concept], self.lang)
        options = {self.correct}
        while len(options) < 4: options.add(text(MEANINGS[self.rng.choice(ORDER)], self.lang))
        options = list(options); self.rng.shuffle(options)
        return text_, say, options
    def check(self, choice):
        ok = choice == self.correct; self.total += 1; self.right += ok; return ok
