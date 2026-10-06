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

# ---------------------------------------------------------------------------
# Outfit activities (tuxedo = formal, casual = summer). Each entry:
# activity: (name, duty, caught-on-hover line, [thoughts])
OUTFIT_TEXT = {
"en": {
    "party": ("Party", "At a school celebration", "Oh! You came to the party too? Want me to help with something first?", ["Everyone is dancing! I'll dance after I help you.", "Party rule: be kind, have fun, drink water!"]),
    "meeting": ("Meeting", "In a teachers' meeting", "Shh… I'm in a meeting. Just kidding — I always have time for you!", ["Point one: help students. Point two: help students more!", "Taking notes so I don't forget anything."]),
    "presentation": ("Presentation", "Giving a presentation", "Next slide: YOU! How can I help?", ["The chart goes up — just like your learning!", "Speak slowly, smile, breathe. Good presentation tips!"]),
    "ceremony": ("Ceremony", "At a graduation ceremony", "Congratulations to everyone! Need my help today?", ["One day this diploma will be yours!", "Proud moment for Timor-Leste's students."]),
    "gala_dinner": ("Gala dinner", "At a formal dinner", "Excuse me, I have food in my mouth… ahem. How can I help?", ["Fork on the left, knife on the right. I remembered!", "Good manners make every dinner nicer."]),
    "report": ("Report", "Reading an important report", "This report is long… you are more interesting! Ask me anything.", ["Summary: learning is the best investment.", "Checking the facts twice. Accuracy matters!"]),
    "speech_prep": ("Speech", "Preparing a speech", "I'm practising my speech. Want to hear it? Or shall I help you first?", ["“Ladies and gentlemen…” hmm, too formal?", "A good speech starts with a smile."]),
    "formal_walk": ("Formal walk", "Walking to an event", "Oh, I'm on my way to an event. But you come first!", ["Shoes polished, bow tie straight. Ready!", "Walking tall on the red carpet."]),
    "beach": ("Beach", "Reading at the beach", "Ahh, the sea breeze! Even at the beach I can help you.", ["Timor-Leste has beautiful beaches — Cristo Rei is my favourite.", "Sunscreen first, then fun!"]),
    "sunbathing": ("Sunbathing", "Relaxing on the sand", "Zzz… oh! I was enjoying the sun. How can I help?", ["The waves sound like a lullaby… zzz", "Rest is important for a sharp brain."]),
    "beach_ball": ("Beach ball", "Playing beach ball", "Catch! …Oops. Hehe. What do you need?", ["Up, up, up! Don't let it fall!", "Playing outside keeps the body happy."]),
    "sightseeing": ("Sightseeing", "Exploring the town", "I'm exploring! Do you want to explore something with me?", ["So many places to discover!", "Every street has a story."]),
    "hangout": ("Hanging out", "Hanging out at a café", "Come sit with me! What shall we talk about?", ["Good friends make every day brighter.", "Chatting is great — learning together is even better!"]),
    "shopping": ("Shopping", "Shopping at the market", "I bought snacks for studying! Need help with anything?", ["A list helps me shop smart: bread, fruit, notebooks!", "Saving money is a smart habit too."]),
    "snack": ("Snack", "Having a snack", "Mmm, crunchy! Sorry, mouth full. Can I help?", ["Fruit is the best study snack.", "A little snack, a lot of energy!"]),
    "game_break": ("Game break", "Taking a short game break", "Just one level… okay, paused! How can I help?", ["Short breaks help the brain learn.", "Game over? Time to study again!"]),
},
"id": {
    "party": ("Pesta", "Di perayaan sekolah", "Wah! Kamu juga datang ke pesta? Mau saya bantu sesuatu dulu?", ["Semua menari! Saya menari setelah membantumu.", "Aturan pesta: baik hati, senang, minum air!"]),
    "meeting": ("Rapat", "Di rapat guru", "Ssst… saya sedang rapat. Bercanda — saya selalu ada waktu untukmu!", ["Poin satu: bantu siswa. Poin dua: bantu siswa lebih banyak!", "Mencatat supaya tidak lupa."]),
    "presentation": ("Presentasi", "Sedang presentasi", "Slide berikutnya: KAMU! Bisa saya bantu?", ["Grafiknya naik — seperti belajarmu!", "Bicara pelan, senyum, tarik napas. Tips presentasi!"]),
    "ceremony": ("Upacara", "Di upacara wisuda", "Selamat untuk semua! Perlu bantuan saya hari ini?", ["Suatu hari ijazah ini milikmu!", "Momen bangga untuk siswa Timor-Leste."]),
    "gala_dinner": ("Makan malam resmi", "Di makan malam resmi", "Maaf, mulut saya penuh… ehem. Bisa saya bantu?", ["Garpu di kiri, pisau di kanan. Saya ingat!", "Sopan santun membuat makan malam lebih menyenangkan."]),
    "report": ("Laporan", "Membaca laporan penting", "Laporan ini panjang… kamu lebih menarik! Tanya apa saja.", ["Ringkasan: belajar adalah investasi terbaik.", "Cek fakta dua kali. Ketelitian itu penting!"]),
    "speech_prep": ("Pidato", "Menyiapkan pidato", "Saya latihan pidato. Mau dengar? Atau saya bantu kamu dulu?", ["“Bapak dan Ibu sekalian…” hmm, terlalu resmi?", "Pidato yang baik dimulai dengan senyum."]),
    "formal_walk": ("Jalan resmi", "Berjalan ke acara", "Oh, saya mau ke acara. Tapi kamu lebih dulu!", ["Sepatu mengkilap, dasi kupu-kupu rapi. Siap!", "Berjalan tegak di karpet merah."]),
    "beach": ("Pantai", "Membaca di pantai", "Ahh, angin laut! Di pantai pun saya bisa membantu.", ["Timor-Leste punya pantai indah — Cristo Rei favorit saya.", "Tabir surya dulu, baru bersenang-senang!"]),
    "sunbathing": ("Berjemur", "Bersantai di pasir", "Zzz… oh! Saya sedang menikmati matahari. Bisa saya bantu?", ["Suara ombak seperti lagu tidur… zzz", "Istirahat penting untuk otak yang tajam."]),
    "beach_ball": ("Bola pantai", "Main bola pantai", "Tangkap! …Ups. Hehe. Perlu apa?", ["Ke atas, ke atas! Jangan sampai jatuh!", "Bermain di luar membuat badan senang."]),
    "sightseeing": ("Jalan-jalan", "Menjelajahi kota", "Saya sedang menjelajah! Mau menjelajah sesuatu bersama?", ["Banyak tempat untuk ditemukan!", "Setiap jalan punya cerita."]),
    "hangout": ("Nongkrong", "Nongkrong di kafe", "Ayo duduk bersama! Kita mau ngobrol apa?", ["Teman baik membuat hari lebih cerah.", "Ngobrol itu seru — belajar bersama lebih seru!"]),
    "shopping": ("Belanja", "Belanja di pasar", "Saya beli camilan untuk belajar! Perlu bantuan?", ["Daftar belanja: roti, buah, buku tulis!", "Menabung juga kebiasaan pintar."]),
    "snack": ("Camilan", "Makan camilan", "Nyam, renyah! Maaf, mulut penuh. Bisa saya bantu?", ["Buah adalah camilan belajar terbaik.", "Camilan kecil, energi besar!"]),
    "game_break": ("Istirahat main", "Istirahat main game sebentar", "Satu level lagi… oke, dijeda! Bisa saya bantu?", ["Istirahat singkat membantu otak belajar.", "Game selesai? Waktunya belajar lagi!"]),
},
"pt": {
    "party": ("Festa", "Numa festa da escola", "Oh! Também vieste à festa? Queres que te ajude primeiro?", ["Todos a dançar! Danço depois de te ajudar.", "Regra da festa: sê simpático, diverte-te, bebe água!"]),
    "meeting": ("Reunião", "Numa reunião de professores", "Shh… estou numa reunião. Brincadeira — tenho sempre tempo para ti!", ["Ponto um: ajudar alunos. Ponto dois: ajudar mais!", "A tirar notas para não esquecer."]),
    "presentation": ("Apresentação", "A fazer uma apresentação", "Próximo diapositivo: TU! Como posso ajudar?", ["O gráfico sobe — como a tua aprendizagem!", "Fala devagar, sorri, respira. Boas dicas!"]),
    "ceremony": ("Cerimónia", "Numa cerimónia de graduação", "Parabéns a todos! Precisas de ajuda hoje?", ["Um dia este diploma será teu!", "Momento de orgulho para os alunos de Timor-Leste."]),
    "gala_dinner": ("Jantar de gala", "Num jantar formal", "Desculpa, tenho a boca cheia… ahem. Posso ajudar?", ["Garfo à esquerda, faca à direita. Lembrei-me!", "Boas maneiras tornam o jantar melhor."]),
    "report": ("Relatório", "A ler um relatório importante", "Este relatório é longo… tu és mais interessante! Pergunta.", ["Resumo: aprender é o melhor investimento.", "Verifico os factos duas vezes."]),
    "speech_prep": ("Discurso", "A preparar um discurso", "Estou a ensaiar o discurso. Queres ouvir? Ou ajudo-te primeiro?", ["“Senhoras e senhores…” hmm, demasiado formal?", "Um bom discurso começa com um sorriso."]),
    "formal_walk": ("Passeio formal", "A caminho de um evento", "Vou para um evento. Mas tu primeiro!", ["Sapatos brilhantes, laço direito. Pronto!", "Passo firme na passadeira vermelha."]),
    "beach": ("Praia", "A ler na praia", "Ahh, a brisa do mar! Mesmo na praia posso ajudar.", ["Timor-Leste tem praias lindas — o Cristo Rei é a minha favorita.", "Protetor solar primeiro!"]),
    "sunbathing": ("Banho de sol", "A relaxar na areia", "Zzz… oh! Estava a apanhar sol. Posso ajudar?", ["As ondas parecem uma canção de embalar… zzz", "Descansar é importante."]),
    "beach_ball": ("Bola de praia", "A jogar à bola na praia", "Apanha! …Ups. Hehe. O que precisas?", ["Para cima! Não deixes cair!", "Brincar lá fora faz bem ao corpo."]),
    "sightseeing": ("Passeio", "A explorar a cidade", "Estou a explorar! Queres explorar algo comigo?", ["Tantos lugares para descobrir!", "Cada rua tem uma história."]),
    "hangout": ("Convívio", "Num café com amigos", "Senta-te comigo! Sobre o que falamos?", ["Bons amigos tornam o dia melhor.", "Conversar é bom — aprender juntos é melhor!"]),
    "shopping": ("Compras", "Às compras no mercado", "Comprei lanches para estudar! Precisas de ajuda?", ["Lista: pão, fruta, cadernos!", "Poupar também é inteligente."]),
    "snack": ("Lanche", "A lanchar", "Mmm, crocante! Desculpa, boca cheia. Posso ajudar?", ["Fruta é o melhor lanche de estudo.", "Pequeno lanche, muita energia!"]),
    "game_break": ("Pausa de jogo", "Uma pequena pausa para jogar", "Só mais um nível… pronto, pausa! Posso ajudar?", ["Pausas curtas ajudam o cérebro.", "Fim do jogo? Hora de estudar!"]),
},
"tet": {
    "party": ("Festa", "Iha festa eskola nian", "Ah! Ita mós mai festa? Hakarak ha'u ajuda uluk?", ["Ema hotu dansa! Ha'u dansa depois ajuda ita.", "Regra festa: di'ak, kontente, hemu bee!"]),
    "meeting": ("Enkontru", "Iha enkontru mestre sira", "Shh… ha'u iha enkontru. Halimar de'it — ha'u iha tempu ba ita!", ["Pontu ida: ajuda estudante. Pontu rua: ajuda liu tan!", "Hakerek nota atu labele haluha."]),
    "presentation": ("Aprezentasaun", "Halo aprezentasaun", "Slide tuir mai: ITA! Ha'u bele ajuda saida?", ["Gráfiku sa'e — hanesan ita-nia aprendizajen!", "Koalia neineik, hamnasa, dada iis."]),
    "ceremony": ("Serimónia", "Iha serimónia graduasaun", "Parabéns ba ema hotu! Presiza ajuda ohin?", ["Loron ida diploma ne'e sei sai ita-nian!", "Momentu orgullu ba estudante Timor-Leste."]),
    "gala_dinner": ("Jantar formál", "Iha jantar formál", "Deskulpa, ibun nakonu… ehem. Ha'u bele ajuda?", ["Garfu iha karuk, tudik iha loos. Ha'u hanoin!", "Edukasaun di'ak halo jantar furak liu."]),
    "report": ("Relatóriu", "Lee relatóriu importante", "Relatóriu ne'e naruk… ita interesante liu! Husu saida de'it.", ["Rezumu: aprende mak investimentu di'ak liu.", "Verifika faktu dala rua."]),
    "speech_prep": ("Diskursu", "Prepara diskursu", "Ha'u pratika diskursu. Hakarak rona? Ka ha'u ajuda ita uluk?", ["“Senhoras no senhores…” hmm, formál liu?", "Diskursu di'ak hahú ho hamnasa."]),
    "formal_walk": ("La'o formál", "La'o ba eventu", "Ha'u la'o ba eventu. Maibé ita uluk!", ["Sapatu kroat, laço loos. Prontu!", "La'o ho orgullu iha tapete mean."]),
    "beach": ("Tasi-ibun", "Lee iha tasi-ibun", "Ahh, anin tasi! Iha tasi-ibun mós ha'u bele ajuda.", ["Timor-Leste iha tasi-ibun furak — Cristo Rei ha'u-nia favoritu.", "Krema loro-matan uluk!"]),
    "sunbathing": ("Toba iha loro", "Deskansa iha rai-henek", "Zzz… oh! Ha'u gosta loro-matan. Ha'u bele ajuda?", ["Lian tasi-ben hanesan kanta toba… zzz", "Deskansa importante ba ulun matenek."]),
    "beach_ball": ("Bola tasi-ibun", "Halimar bola iha tasi-ibun", "Kaer! …Ups. Hehe. Presiza saida?", ["Ba leten! Keta husik monu!", "Halimar iha li'ur halo isin kontente."]),
    "sightseeing": ("Pasiar", "Esplora sidade", "Ha'u esplora hela! Hakarak esplora hamutuk?", ["Fatin barak atu deskobre!", "Dalan ida-idak iha istória."]),
    "hangout": ("Tuur hamutuk", "Tuur iha kafé ho belun", "Mai tuur ho ha'u! Ita koalia kona-ba saida?", ["Belun di'ak halo loron naroman.", "Koalia di'ak — aprende hamutuk di'ak liu!"]),
    "shopping": ("Sosa sasán", "Sosa iha merkadu", "Ha'u sosa ai-han ki'ik ba estuda! Presiza ajuda?", ["Lista: paun, ai-fuan, kadernu!", "Rai osan mós hahalok matenek."]),
    "snack": ("Han ki'ik", "Han ai-han ki'ik", "Mmm, krokante! Deskulpa, ibun nakonu. Ha'u bele ajuda?", ["Ai-fuan mak ai-han estuda di'ak liu.", "Ai-han ki'ik, enerjia boot!"]),
    "game_break": ("Deskansa joga", "Deskansa uitoan ho jogu", "Nivel ida tan… diak, para! Ha'u bele ajuda?", ["Deskansa badak ajuda ulun aprende.", "Jogu remata? Tempu estuda fali!"]),
},
}
OUTFIT_NAMES = {
"en": {"traditional": "Tais Mane (default)", "tuxedo": "Tuxedo (formal)", "casual": "Casual (summer)"},
"id": {"traditional": "Tais Mane (bawaan)", "tuxedo": "Tuksedo (resmi)", "casual": "Kasual (musim panas)"},
"pt": {"traditional": "Tais Mane (predefinido)", "tuxedo": "Smoking (formal)", "casual": "Informal (verão)"},
"tet": {"traditional": "Tais Mane (padraun)", "tuxedo": "Tuxedo (formál)", "casual": "Kazuál (tempu bai-loron)"},
}
for _lang, _items in OUTFIT_TEXT.items():
    for _key, (_name, _duty, _caught, _thoughts) in _items.items():
        DUTIES[_lang][_key] = _duty; CAUGHT[_lang][_key] = _caught; THOUGHTS[_lang][_key] = _thoughts

def activity_name(language, activity):
    entry = OUTFIT_TEXT[lang_of(language)].get(activity)
    return entry[0] if entry else None
