"""LAFA's character: naive, curious and funny, but very clever and helpful.

Every idle activity is framed as part of a virtual assistant's working day, so
the character entertains while reminding the user what LAFA can do. All text is
data in four languages; nothing here is sent to the internet.
"""
import random

LANGUAGES = ("en", "id", "pt", "tet")

# Activity -> what the assistant is "working on" (shown on hover and in menus).
DUTIES = {
"en": {
    "idle": "Ready to help", "reading": "Reading the Edukasaun OS guide", "thinking": "Thinking about clever answers",
    "walking": "Patrolling the Eduka-Panel", "sitting": "Waiting for your question", "gaming": "Brain-training game",
    "serious": "Checking facts carefully", "angry": "Fighting a bug in the code", "talking": "Talking with you",
    "sleeping": "Power nap · recharging", "bathing": "Bath time · fresh assistant", "toilet": "Be right back!",
    "studying": "Studying new lessons for you", "eating": "Brain-food snack", "stretching": "Stretching after typing",
    "tebe": "Dancing Tebe-tebe", "bidu": "Dancing Bidu",
},
"id": {
    "idle": "Siap membantu", "reading": "Membaca panduan Edukasaun OS", "thinking": "Memikirkan jawaban cerdas",
    "walking": "Patroli di Eduka-Panel", "sitting": "Menunggu pertanyaanmu", "gaming": "Main game asah otak",
    "serious": "Memeriksa fakta dengan teliti", "angry": "Melawan bug di kode", "talking": "Mengobrol denganmu",
    "sleeping": "Tidur sebentar · isi tenaga", "bathing": "Waktu mandi · asisten segar", "toilet": "Sebentar ya!",
    "studying": "Belajar pelajaran baru untukmu", "eating": "Camilan untuk otak", "stretching": "Peregangan setelah mengetik",
    "tebe": "Menari Tebe-tebe", "bidu": "Menari Bidu",
},
"pt": {
    "idle": "Pronto para ajudar", "reading": "A ler o guia do Edukasaun OS", "thinking": "A pensar em respostas espertas",
    "walking": "A patrulhar o Eduka-Panel", "sitting": "À espera da tua pergunta", "gaming": "Jogo de treino mental",
    "serious": "A verificar factos com cuidado", "angry": "A lutar contra um bug", "talking": "A conversar contigo",
    "sleeping": "Sesta rápida · a recarregar", "bathing": "Hora do banho · assistente fresco", "toilet": "Volto já!",
    "studying": "A estudar lições novas para ti", "eating": "Lanche para o cérebro", "stretching": "Alongamento depois de escrever",
    "tebe": "A dançar Tebe-tebe", "bidu": "A dançar Bidu",
},
"tet": {
    "idle": "Prontu atu ajuda", "reading": "Lee hela matadalan Edukasaun OS", "thinking": "Hanoin hela resposta matenek",
    "walking": "La'o patrulla iha Eduka-Panel", "sitting": "Hein hela ita-nia pergunta", "gaming": "Joga jogu hamatenek ulun",
    "serious": "Verifika faktu ho kuidadu", "angry": "Funu hasoru bug iha kódigu", "talking": "Koalia ho ita",
    "sleeping": "Toba uitoan · karga forsa", "bathing": "Oras hariis · asistente moos", "toilet": "Fila fali lalais!",
    "studying": "Estuda lisaun foun ba ita", "eating": "Han ai-han ki'ik ba ulun", "stretching": "Estika isin depois hakerek",
    "tebe": "Dansa Tebe-tebe", "bidu": "Dansa Bidu",
},
}

# Questions when the cursor touches LAFA. Innocent, curious and a little funny.
HOVER = {
"en": [
    "Oh! Hello! Can I help you with something?",
    "A cursor! Is that you? Do you need my help?",
    "Psst… I know lots of things about Edukasaun OS. Want to ask me?",
    "I'm small, but my brain is BIG. What shall we do?",
    "Don't worry, I'm a friendly crocodile. I only bite… bugs! Need help?",
    "Click me! I can find files, check the weather, or explain things.",
    "I was just wondering what you are learning today. Can I help?",
    "Hehe, that tickles! What can I do for you?",
],
"id": [
    "Eh! Halo! Ada yang bisa saya bantu?",
    "Ada kursor! Itu kamu ya? Butuh bantuan saya?",
    "Psst… saya tahu banyak tentang Edukasaun OS. Mau tanya?",
    "Badan saya kecil, tapi otak saya BESAR. Kita mau apa?",
    "Tenang, saya buaya yang ramah. Saya cuma menggigit… bug! Perlu bantuan?",
    "Klik saya! Saya bisa cari file, cek cuaca, atau menjelaskan sesuatu.",
    "Saya penasaran, hari ini kamu belajar apa? Bisa saya bantu?",
    "Hehe, geli! Apa yang bisa saya lakukan untukmu?",
],
"pt": [
    "Oh! Olá! Posso ajudar-te com alguma coisa?",
    "Um cursor! És tu? Precisas da minha ajuda?",
    "Psst… sei muitas coisas sobre o Edukasaun OS. Queres perguntar?",
    "Sou pequeno, mas o meu cérebro é GRANDE. O que fazemos?",
    "Calma, sou um crocodilo simpático. Só mordo… bugs! Precisas de ajuda?",
    "Clica em mim! Posso procurar ficheiros, ver o tempo ou explicar coisas.",
    "Estava a pensar no que vais aprender hoje. Posso ajudar?",
    "Hehe, faz cócegas! O que posso fazer por ti?",
],
"tet": [
    "Ah! Olá! Ha'u bele ajuda ita ho buat ruma?",
    "Kursór ida! Ne'e ita ka? Presiza ha'u-nia ajuda?",
    "Psst… ha'u hatene buat barak kona-ba Edukasaun OS. Hakarak husu?",
    "Ha'u-nia isin ki'ik, maibé ha'u-nia ulun BOOT. Ita halo saida?",
    "Keta ta'uk, ha'u lafaek ne'ebé di'ak. Ha'u tata de'it… bug! Presiza ajuda?",
    "Klik ha'u! Ha'u bele buka ficheiru, haree tempu ka esplika buat ruma.",
    "Ha'u hanoin hela: ohin ita aprende saida? Ha'u bele ajuda?",
    "Hehe, kakiak! Ha'u bele halo saida ba ita?",
],
}

# Activity-specific hover reactions; LAFA is caught in the middle of something.
CAUGHT = {
"en": {
    "sleeping": "Hm? Oh! I wasn't sleeping… I was thinking with my eyes closed. Can I help?",
    "bathing": "Eek! I'm in the bath! …But I can still help you. What do you need?",
    "toilet": "Ahh, privacy please! I'll be right back to help you!",
    "eating": "Mmm, crunchy! Sorry, mouth full. Can I help you?",
    "gaming": "Wait, I'm almost at the next level… okay, pausing! Can I help?",
    "studying": "I just learned something new! Want me to help you learn too?",
    "reading": "This guide is so interesting! Ask me anything about Edukasaun OS.",
    "tebe": "Come dance Tebe with me! Or… can I help you first?",
    "bidu": "Bidu is my favourite dance! Need anything?",
    "angry": "Grr, this bug! …Oh, it's you! Sorry. Can I help?",
    "walking": "Oh! You found me on my walk. Where are we going together?",
    "stretching": "Stretch with me! Arms up… Okay, how can I help?",
},
"id": {
    "sleeping": "Hm? Oh! Saya tidak tidur kok… saya berpikir sambil merem. Bisa saya bantu?",
    "bathing": "Aduh! Saya lagi mandi! …Tapi saya tetap bisa bantu. Perlu apa?",
    "toilet": "Ups, privasi dong! Sebentar lagi saya bantu!",
    "eating": "Nyam, renyah! Maaf, mulut penuh. Bisa saya bantu?",
    "gaming": "Tunggu, hampir naik level… oke, dijeda! Bisa saya bantu?",
    "studying": "Saya baru belajar hal baru! Mau saya bantu belajar juga?",
    "reading": "Panduan ini seru sekali! Tanyakan apa saja tentang Edukasaun OS.",
    "tebe": "Ayo menari Tebe bersama! Atau… saya bantu dulu?",
    "bidu": "Bidu tarian favorit saya! Perlu sesuatu?",
    "angry": "Grr, bug ini! …Oh, kamu! Maaf. Bisa saya bantu?",
    "walking": "Oh! Kamu menemukan saya jalan-jalan. Kita mau ke mana?",
    "stretching": "Ayo peregangan! Tangan ke atas… Oke, bisa saya bantu?",
},
"pt": {
    "sleeping": "Hm? Oh! Não estava a dormir… estava a pensar de olhos fechados. Posso ajudar?",
    "bathing": "Ai! Estou no banho! …Mas posso ajudar-te na mesma. O que precisas?",
    "toilet": "Privacidade, por favor! Volto já para ajudar!",
    "eating": "Mmm, crocante! Desculpa, boca cheia. Posso ajudar?",
    "gaming": "Espera, quase no próximo nível… pronto, pausa! Posso ajudar?",
    "studying": "Acabei de aprender algo novo! Queres que te ajude a aprender também?",
    "reading": "Este guia é tão interessante! Pergunta-me sobre o Edukasaun OS.",
    "tebe": "Vem dançar Tebe comigo! Ou… ajudo-te primeiro?",
    "bidu": "Bidu é a minha dança favorita! Precisas de algo?",
    "angry": "Grr, este bug! …Oh, és tu! Desculpa. Posso ajudar?",
    "walking": "Oh! Encontraste-me a passear. Para onde vamos?",
    "stretching": "Alonga comigo! Braços para cima… Pronto, como posso ajudar?",
},
"tet": {
    "sleeping": "Hm? Oh! Ha'u la toba… ha'u hanoin ho matan taka. Ha'u bele ajuda?",
    "bathing": "Ai! Ha'u hariis hela! …Maibé ha'u sei bele ajuda. Presiza saida?",
    "toilet": "Ai, privasidade favór! Ha'u fila fali lalais atu ajuda!",
    "eating": "Mmm, krokante! Deskulpa, ibun nakonu. Ha'u bele ajuda?",
    "gaming": "Hein, besik ba nivel tuir mai… diak, para! Ha'u bele ajuda?",
    "studying": "Ha'u foin aprende buat foun! Hakarak ha'u ajuda ita aprende mós?",
    "reading": "Matadalan ne'e interesante tebes! Husu ha'u kona-ba Edukasaun OS.",
    "tebe": "Mai dansa Tebe ho ha'u! Ka… ha'u ajuda uluk?",
    "bidu": "Bidu mak ha'u-nia dansa favoritu! Presiza buat ruma?",
    "angry": "Grr, bug ne'e! …Oh, ita! Deskulpa. Ha'u bele ajuda?",
    "walking": "Oh! Ita hetan ha'u la'o hela. Ita ba ne'ebé?",
    "stretching": "Estika ho ha'u! Liman ba leten… Diak, ha'u bele ajuda saida?",
},
}

# LAFA talking to itself while working (short, shown above the head).
THOUGHTS = {
"en": {
    "reading": ["Page 42: how to connect Wi-Fi. Easy!", "Did you know the Files app can search too?"],
    "studying": ["2 + 2 = 4… and 4 + 4 = 8! I'm getting smarter.", "Today I'm learning Tetun proverbs."],
    "thinking": ["Hmm… why is the sky blue? Ah, sunlight scattering!", "If I had a hundred hands, I'd type so fast."],
    "gaming": ["One more level and I'll be a champion!", "This puzzle is hard… but I'm harder! Hehe."],
    "eating": ["Fresh Timor coffee smell… wait, crocodiles drink coffee?", "Brain food = clever answers."],
    "bathing": ["La la la… a clean assistant is a happy assistant!"],
    "sleeping": ["Zzz… dreaming of fast internet… zzz"],
    "stretching": ["Stretch your arms too! Your body will thank you."],
    "walking": ["Walking on the panel… don't click the clock, I'm passing!", "Left, right, left… I'm on patrol!"],
    "tebe": ["Tebe-tebe! Everyone dance together!"],
    "bidu": ["Bidu is graceful… I'm trying my best!"],
    "sitting": ["I'll wait here. Call me anytime!"],
    "idle": ["Ready! Click me when you need help."],
},
"id": {
    "reading": ["Halaman 42: cara sambung Wi-Fi. Gampang!", "Tahukah kamu, aplikasi File juga bisa mencari?"],
    "studying": ["2 + 2 = 4… dan 4 + 4 = 8! Saya makin pintar.", "Hari ini saya belajar peribahasa Tetun."],
    "thinking": ["Hmm… kenapa langit biru? Ah, hamburan cahaya matahari!", "Kalau tangan saya seratus, saya mengetik cepat sekali."],
    "gaming": ["Satu level lagi saya jadi juara!", "Teka-teki ini sulit… tapi saya lebih kuat! Hehe."],
    "eating": ["Wangi kopi Timor… eh, buaya minum kopi ya?", "Makanan otak = jawaban pintar."],
    "bathing": ["La la la… asisten bersih, asisten bahagia!"],
    "sleeping": ["Zzz… mimpi internet cepat… zzz"],
    "stretching": ["Ayo peregangan juga! Badanmu akan berterima kasih."],
    "walking": ["Jalan di panel… jangan klik jam, saya lewat!", "Kiri, kanan, kiri… saya sedang patroli!"],
    "tebe": ["Tebe-tebe! Ayo menari bersama!"],
    "bidu": ["Bidu itu anggun… saya berusaha!"],
    "sitting": ["Saya tunggu di sini. Panggil kapan saja!"],
    "idle": ["Siap! Klik saya kalau perlu bantuan."],
},
"pt": {
    "reading": ["Página 42: como ligar o Wi-Fi. Fácil!", "Sabias que a app Ficheiros também pesquisa?"],
    "studying": ["2 + 2 = 4… e 4 + 4 = 8! Estou mais esperto.", "Hoje aprendo provérbios em Tétum."],
    "thinking": ["Hmm… porque é o céu azul? Ah, dispersão da luz!", "Se tivesse cem mãos, escrevia tão depressa."],
    "gaming": ["Mais um nível e sou campeão!", "Este puzzle é difícil… mas eu sou teimoso! Hehe."],
    "eating": ["Cheiro a café de Timor… espera, crocodilos bebem café?", "Comida para o cérebro = respostas espertas."],
    "bathing": ["La la la… assistente limpo, assistente feliz!"],
    "sleeping": ["Zzz… a sonhar com internet rápida… zzz"],
    "stretching": ["Alonga também! O teu corpo agradece."],
    "walking": ["A passear no painel… não cliques no relógio, estou a passar!", "Esquerda, direita… estou em patrulha!"],
    "tebe": ["Tebe-tebe! Todos a dançar!"],
    "bidu": ["O Bidu é elegante… estou a tentar!"],
    "sitting": ["Espero aqui. Chama-me quando quiseres!"],
    "idle": ["Pronto! Clica em mim quando precisares."],
},
"tet": {
    "reading": ["Pájina 42: oinsá liga Wi-Fi. Fasil!", "Ita hatene ka, aplikasaun Ficheiru bele buka mós?"],
    "studying": ["2 + 2 = 4… no 4 + 4 = 8! Ha'u sai matenek liu.", "Ohin ha'u aprende ai-knanoik Tetun."],
    "thinking": ["Hmm… tanba saa lalehan kór azúl? Ah, naroman loro-matan!", "Se ha'u iha liman atus ida, ha'u hakerek lalais tebes."],
    "gaming": ["Nivel ida tan ha'u sai kampiaun!", "Puzzle ne'e susar… maibé ha'u maka'as liu! Hehe."],
    "eating": ["Morin kafé Timor… hein, lafaek hemu kafé ka?", "Ai-han ba ulun = resposta matenek."],
    "bathing": ["La la la… asistente moos, asistente kontente!"],
    "sleeping": ["Zzz… mehi internet lalais… zzz"],
    "stretching": ["Estika mós! Ita-nia isin sei agradese."],
    "walking": ["La'o iha painel… keta klik relójiu, ha'u liu hela!", "Karuk, loos, karuk… ha'u patrulla hela!"],
    "tebe": ["Tebe-tebe! Ita hotu dansa hamutuk!"],
    "bidu": ["Bidu furak… ha'u koko hela!"],
    "sitting": ["Ha'u hein iha ne'e. Bolu ha'u bainhira de'it!"],
    "idle": ["Prontu! Klik ha'u bainhira presiza ajuda."],
},
}

JOKES = {
"en": [
    "Why did the computer go to school? To improve its memory! 🧠",
    "Why are crocodiles good at computers? We have very strong bytes! 🐊",
    "What did the mouse say to the keyboard? You're just my type!",
    "Why was the math book sad? It had too many problems.",
    "I tried to catch some fog this morning… I mist.",
],
"id": [
    "Kenapa komputer pergi ke sekolah? Supaya memorinya bertambah! 🧠",
    "Kenapa buaya jago komputer? Gigitan kami kuat sekali! 🐊",
    "Apa kata mouse ke keyboard? Kamu tipe aku banget!",
    "Kenapa buku matematika sedih? Karena terlalu banyak masalah.",
    "Kenapa air mata bening? Kalau hijau, itu air mata buaya! 🐊 Hehe.",
],
"pt": [
    "Porque é que o computador foi à escola? Para melhorar a memória! 🧠",
    "Porque é que os crocodilos são bons com computadores? Temos bytes fortes! 🐊",
    "O que disse o rato ao teclado? Tu és mesmo o meu tipo!",
    "Porque é que o livro de matemática estava triste? Tinha muitos problemas.",
    "Qual é o animal mais antigo? A zebra, porque é a preto e branco!",
],
"tet": [
    "Tanba saa komputadór ba eskola? Atu hadi'a ninia memória! 🧠",
    "Tanba saa lafaek matenek ho komputadór? Ami-nia tata maka'as tebes! 🐊",
    "Rato hatete saida ba teklado? Ita mak ha'u-nia tipu!",
    "Tanba saa livru matemátika triste? Tanba iha problema barak liu.",
    "Lafaek ida ba eskola… nia sai mestre ba nadar! Hehe.",
],
}

def lang_of(language):
    return language if language in LANGUAGES else "en"

def duty(language, state):
    return DUTIES[lang_of(language)].get(state, DUTIES[lang_of(language)]["idle"])

def hover_line(language, state, rng=random):
    """A curious offer of help; sometimes reacts to the current activity."""
    lang = lang_of(language)
    caught = CAUGHT[lang].get(state)
    if caught and rng.random() < 0.6: return caught
    return rng.choice(HOVER[lang])

def thought(language, state, rng=random):
    lang = lang_of(language)
    options = THOUGHTS[lang].get(state) or THOUGHTS[lang]["idle"]
    return rng.choice(options)

def joke(language, rng=random):
    return rng.choice(JOKES[lang_of(language)])
