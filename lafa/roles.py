"""LAFA's many hats: one character, many roles.

LAFA is funny, smart and helpful, and can switch into a motivator, magician,
teacher, professor or master whenever a student needs it. Each role has a
name, a short description, a Virtual Assistant activity (pose + scene) and
lines in LAFA's four languages. The magician also has a real mind-reading
trick (binary cards) that teaches how binary numbers work.
"""
import random
from .school import L

def text(value, lang):
    return value.get(lang, value["en"]) if isinstance(value, dict) else value

# role -> (activity, theme icons, name, description)
ROLES = {
    "funny": ("comedy", ["face-laugh", "face-smile-big", "emblem-favorite"], L("Comedian", "Pelawak", "Comediante", "Komediante"),
              L("Jokes and funny moments to make learning lighter.", "Lelucon dan momen lucu agar belajar terasa ringan.", "Piadas e momentos divertidos para aprender com leveza.", "Anedota no momentu kómiku atu aprende sai kmaan.")),
    "smart": ("professor", ["help-hint", "dialog-information", "applications-science"], L("Professor", "Profesor", "Professor catedrático", "Profesór"),
              L("Amazing facts about science and Timor-Leste.", "Fakta menakjubkan tentang sains dan Timor-Leste.", "Factos surpreendentes de ciência e de Timor-Leste.", "Faktu furak kona-ba siénsia no Timor-Leste.")),
    "teacher": ("lecture", ["applications-education", "x-office-presentation", "accessories-dictionary"], L("Teacher", "Guru", "Professor", "Mestre"),
                L("Lessons step by step, quizzes and tests in the classroom.", "Pelajaran langkah demi langkah, kuis dan ulangan di kelas.", "Aulas passo a passo, quizzes e testes na sala de aula.", "Lisaun pasu ba pasu, kuis no teste iha sala aula.")),
    "motivator": ("motivator", ["emblem-favorite", "starred", "face-cool"], L("Motivator", "Motivator", "Motivador", "Motivadór"),
                  L("Encouragement when studying feels hard.", "Semangat saat belajar terasa berat.", "Ânimo quando estudar parece difícil.", "Fó korajen bainhira estuda sente todan.")),
    "magician": ("magic_show", ["applications-games", "games-config-custom", "emblem-generic"], L("Magician", "Pesulap", "Mágico", "Majiku"),
                 L("Magic tricks that are secretly maths.", "Sulap yang diam-diam adalah matematika.", "Truques de magia que são matemática em segredo.", "Majia ne'ebé matemátika iha subar.")),
    "master": ("master", ["preferences-desktop", "view-statistics", "emblem-important"], L("Master", "Master", "Mestre", "Mestre boot"),
               L("Wise study habits from LAFA, master of learning.", "Kebiasaan belajar bijak dari LAFA, master pembelajaran.", "Hábitos de estudo sábios do LAFA, mestre da aprendizagem.", "Hahalok estuda matenek husi LAFA, mestre aprendizajen.")),
    "helper": ("idle", ["help-browser", "system-help", "help-contents"], L("Helper", "Penolong", "Ajudante", "Ajudante"),
               L("Help with Edukasaun OS, files, homework and questions.", "Bantuan Edukasaun OS, berkas, PR dan pertanyaan.", "Ajuda com o Edukasaun OS, ficheiros, trabalhos e perguntas.", "Ajuda ho Edukasaun OS, ficheiru, TPC no pergunta.")),
}
ORDER = ["teacher", "smart", "motivator", "magician", "master", "funny", "helper"]

MOTIVATION = [
    L("You don't have to be perfect — just better than yesterday.", "Kamu tidak harus sempurna — cukup lebih baik dari kemarin.", "Não tens de ser perfeito — só melhor do que ontem.", "La presiza perfeitu — di'ak liu de'it duké horiseik."),
    L("Every expert was once a beginner. Keep going!", "Setiap ahli dulunya pemula. Terus maju!", "Todo o especialista já foi principiante. Continua!", "Espesialista hotu uluk mós hahú husi zero. Kontinua!"),
    L("Mistakes are proof that you are trying.", "Kesalahan adalah bukti kamu sedang berusaha.", "Os erros provam que estás a tentar.", "Sala mak prova katak ita koko hela."),
    L("Our heroes never gave up. You won't either!", "Para pahlawan kita tidak pernah menyerah. Kamu juga tidak!", "Os nossos heróis nunca desistiram. Tu também não!", "Ita-nia eroi sira nunka hakruuk. Ita mós lae!"),
    L("Small steps every day make a big mountain — even Ramelau!", "Langkah kecil setiap hari membuat gunung besar — bahkan Ramelau!", "Pequenos passos todos os dias fazem uma grande montanha — até o Ramelau!", "Pasu ki'ik loron-loron halo foho boot — to'o Ramelau!"),
    L("Learning is the key that opens every door. Timor-Leste needs your talent.", "Belajar adalah kunci semua pintu. Timor-Leste membutuhkan bakatmu.", "Aprender é a chave de todas as portas. Timor-Leste precisa do teu talento.", "Aprende mak xave ba odamatan hotu. Timor-Leste presiza ita-nia talentu."),
    L("Take a deep breath. You can do hard things.", "Tarik napas dalam. Kamu bisa melakukan hal sulit.", "Respira fundo. Tu consegues fazer coisas difíceis.", "Dada iis kle'an. Ita bele halo buat susar."),
    L("Read one more page today. Tomorrow-you will say obrigadu!", "Baca satu halaman lagi hari ini. Kamu besok akan berterima kasih!", "Lê mais uma página hoje. O tu de amanhã agradece!", "Lee pájina ida tan ohin. Ita aban sei dehan obrigadu!"),
]

PROFESSOR = [
    L("A crocodile can't stick out its tongue — but LAFA can! 😛", "Buaya tidak bisa menjulurkan lidah — tapi LAFA bisa! 😛", "Um crocodilo não consegue pôr a língua de fora — mas o LAFA consegue! 😛", "Lafaek labele hasai nanál — maibé LAFA bele! 😛"),
    L("Light from the Sun takes about 8 minutes to reach Timor-Leste.", "Cahaya Matahari butuh sekitar 8 menit untuk sampai ke Timor-Leste.", "A luz do Sol demora cerca de 8 minutos a chegar a Timor-Leste.", "Naroman loro-matan presiza minutu 8 atu to'o Timor-Leste."),
    L("Timor-Leste sits where the Indian and Pacific Oceans meet — whales pass by every year.", "Timor-Leste berada di pertemuan Samudra Hindia dan Pasifik — paus lewat setiap tahun.", "Timor-Leste fica onde se encontram os oceanos Índico e Pacífico — baleias passam todos os anos.", "Timor-Leste iha fatin ne'ebé Oseanu Índiku no Pasífiku hasoru malu — baleia liu kada tinan."),
    L("Your brain has about 86 billion neurons. Feed them with sleep and water!", "Otakmu punya sekitar 86 miliar neuron. Beri mereka tidur dan air!", "O teu cérebro tem cerca de 86 mil milhões de neurónios. Dá-lhes sono e água!", "Ita-nia kakutak iha neurónio biliaun 86. Fó sira toba no bee!"),
    L("Coffee from Timor-Leste is grown in the mountains of Ermera, Aileu and Ainaro and sold around the world.", "Kopi Timor-Leste ditanam di pegunungan Ermera, Aileu dan Ainaro dan dijual ke seluruh dunia.", "O café de Timor-Leste cresce nas montanhas de Ermera, Aileu e Ainaro e é vendido no mundo inteiro.", "Kafé Timor-Leste kuda iha foho Ermera, Aileu no Ainaro no fa'an ba mundu tomak."),
    L("Water expands when it freezes — that is why ice floats.", "Air memuai saat membeku — itulah sebabnya es mengapung.", "A água expande ao congelar — por isso o gelo flutua.", "Bee sai boot bainhira sai jelu — ne'e mak jelu nanu."),
    L("Zero was used as a number in India about 1,500 years ago.", "Angka nol dipakai sebagai bilangan di India sekitar 1.500 tahun lalu.", "O zero começou a ser usado como número na Índia há cerca de 1500 anos.", "Zero komesa uza hanesan númeru iha Índia maizumenus tinan 1.500 liubá."),
]

MASTER = [
    L("Master rule 1: Explain it to a friend. If you can teach it, you know it.", "Aturan master 1: Jelaskan ke teman. Jika bisa mengajarkannya, kamu menguasainya.", "Regra do mestre 1: Explica a um amigo. Se consegues ensinar, sabes.", "Regra mestre 1: Esplika ba belun. Se ita bele hanorin, ita hatene."),
    L("Master rule 2: Test yourself before the test. Try a LAFA quiz!", "Aturan master 2: Uji dirimu sebelum ulangan. Coba kuis LAFA!", "Regra do mestre 2: Testa-te antes do teste. Experimenta um quiz do LAFA!", "Regra mestre 2: Teste an molok teste. Koko kuis LAFA!"),
    L("Master rule 3: Space your study — a little every day beats everything at night.", "Aturan master 3: Belajar sedikit setiap hari lebih baik dari semalam suntuk.", "Regra do mestre 3: Estuda um pouco todos os dias, não tudo numa noite.", "Regra mestre 3: Estuda uitoan loron-loron, la'ós hotu iha kalan ida."),
    L("Master rule 4: Phone away, focus on. 25 minutes is enough to grow.", "Aturan master 4: Jauhkan ponsel, nyalakan fokus. 25 menit cukup untuk tumbuh.", "Regra do mestre 4: Telemóvel longe, foco ligado. 25 minutos chegam.", "Regra mestre 4: Telemovel dook, foku loke. Minutu 25 to'o ona."),
    L("Master rule 5: Ask questions. Curious minds become wise minds.", "Aturan master 5: Bertanyalah. Pikiran penasaran menjadi bijak.", "Regra do mestre 5: Faz perguntas. Mentes curiosas tornam-se sábias.", "Regra mestre 5: Husu pergunta. Ulun ne'ebé hakarak hatene sai matenek."),
]

MAGIC = [
    L("🎩 Think of a number. Double it. Add 10. Halve it. Subtract your first number… Abracadabra: your answer is 5!",
      "🎩 Pikirkan satu angka. Kalikan dua. Tambah 10. Bagi dua. Kurangi angka awalmu… Simsalabim: hasilnya 5!",
      "🎩 Pensa num número. Duplica. Soma 10. Divide por 2. Subtrai o número inicial… Abracadabra: dá 5!",
      "🎩 Hanoin númeru ida. Dala rua. Aumenta 10. Fahe rua. Hasai númeru dahuluk… Abrakadabra: rezultadu 5!"),
    L("🎩 Pick any 3-digit number like 123, write it twice: 123123. Divide by 7, then 11, then 13… your number comes back! (7×11×13 = 1001)",
      "🎩 Pilih angka 3 digit seperti 123, tulis dua kali: 123123. Bagi 7, lalu 11, lalu 13… angkamu kembali! (7×11×13 = 1001)",
      "🎩 Escolhe um número de 3 algarismos, como 123, escreve-o duas vezes: 123123. Divide por 7, 11 e 13… o número volta! (7×11×13 = 1001)",
      "🎩 Hili númeru dijitu 3 hanesan 123, hakerek dala rua: 123123. Fahe ho 7, 11, depois 13… ita-nia númeru fila mai! (7×11×13 = 1001)"),
    L("🎩 Multiply 37 by 3, 6, 9… 37×3 = 111, 37×6 = 222, 37×9 = 333! Magic? No — maths!",
      "🎩 Kalikan 37 dengan 3, 6, 9… 37×3 = 111, 37×6 = 222, 37×9 = 333! Sulap? Bukan — matematika!",
      "🎩 Multiplica 37 por 3, 6, 9… 37×3 = 111, 37×6 = 222, 37×9 = 333! Magia? Não — matemática!",
      "🎩 Multiplika 37 ho 3, 6, 9… 37×3 = 111, 37×6 = 222, 37×9 = 333! Majia? Lae — matemátika!"),
]

def line(role, lang="en", rng=random):
    """One thing LAFA says in a role."""
    if role == "funny":
        from .personality import joke
        return joke(lang, rng)
    if role == "teacher":
        from .school import TIPS
        return text(rng.choice(TIPS), lang)
    if role == "helper":
        from .osguide import tip_of_day
        return tip_of_day(lang)
    pool = {"motivator": MOTIVATION, "smart": PROFESSOR, "magician": MAGIC, "master": MASTER}[role]
    return text(rng.choice(pool), lang)

def daily(pool, when=None):
    """The same item all day long (word, quote, fact of the day)."""
    from datetime import date
    when = when or date.today()
    return pool[when.toordinal() % len(pool)]

class MindReader:
    """Binary card trick: the student thinks of a number from 1 to 63 and says
    on which cards it appears; LAFA adds the first numbers of those cards."""
    CARDS = 6
    def card(self, index):
        return [n for n in range(1, 64) if n >> index & 1]
    def guess(self, chosen):
        return sum(1 << i for i in chosen if 0 <= i < self.CARDS)
