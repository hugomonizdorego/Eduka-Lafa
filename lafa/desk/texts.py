"""Words on Lafa Desktop screens in the four languages of Lafa: Tetun and
Português (the official languages, Konstituisaun artigu 13), English and
Bahasa Indonesia (working languages, artigu 159).

Tetun follows docs/TETUN-STYLE.md (official spelling of the Konstituisaun).
`t(lang, key, **values)` gives the text in that language (falling back to a
related language), or the key itself.
"""
from ..kb import LANGS, pick, show

# key: (tet, pt, en, id)
T = {
    # --- shell and navigation
    "app_subtitle": ("Ensiklopédia Timór-Leste", "Enciclopédia de Timor-Leste", "Encyclopedia of Timor-Leste", "Ensiklopedia Timor-Leste"),
    "nav_home": ("Pájina inisiál", "Início", "Home", "Beranda"),
    "nav_encyclopedia": ("Ensiklopédia", "Enciclopédia", "Encyclopedia", "Ensiklopedia"),
    "nav_map": ("Mapa", "Mapa", "Map", "Peta"),
    "nav_timeline": ("Liña tempu", "Linha do tempo", "Timeline", "Lini masa"),
    "nav_places": ("Turizmu", "Turismo", "Tourism", "Wisata"),
    "nav_calendar": ("Kalendáriu", "Calendário", "Calendar", "Kalender"),
    "nav_quiz": ("Kuis Milionáriu", "Quiz Milionário", "Millionaire Quiz", "Kuis Jutawan"),
    "nav_language": ("Aprende lian", "Aprender línguas", "Learn languages", "Belajar bahasa"),
    "nav_paths": ("Nível eskola", "Níveis escolares", "School levels", "Jenjang sekolah"),
    "nav_constitution": ("Konstituisaun", "Constituição", "Constitution", "Konstitusi"),
    "nav_symbols": ("Símbolu Nasionál", "Símbolos Nacionais", "National Symbols", "Simbol Nasional"),
    "nav_institutions": ("Instituisaun Estadu", "Instituições do Estado", "State institutions", "Lembaga negara"),
    "nav_history_game": ("Jogu Istória", "Jogo da História", "History Game", "Permainan Sejarah"),
    "nav_group_explore": ("ESPLORA", "EXPLORAR", "EXPLORE", "JELAJAHI"),
    "nav_group_state": ("ESTADU NO NASAUN", "ESTADO E NAÇÃO", "STATE AND NATION", "NEGARA DAN BANGSA"),
    "nav_group_learn": ("APRENDE NO HALIMAR", "APRENDER E JOGAR", "LEARN AND PLAY", "BELAJAR DAN BERMAIN"),
    "nav_sources": ("Fonte no lisensa", "Fontes e licenças", "Sources and licences", "Sumber dan lisensi"),
    "nav_data": ("Offline no atualiza", "Offline e atualização", "Offline and updates", "Luring dan pembaruan"),
    "nav_settings": ("Konfigurasaun", "Definições", "Settings", "Pengaturan"),
    "nav_about": ("Kona-ba Lafa", "Sobre o Lafa", "About Lafa", "Tentang Lafa"),
    "back": ("Fila", "Voltar", "Back", "Kembali"),
    "search_placeholder": ("Buka artigu, fatin, munisípiu, liafuan…", "Pesquisar artigos, lugares, municípios, palavras…", "Search articles, places, municipalities, words…", "Cari artikel, tempat, munisipio, kata…"),
    "online": ("Online", "Online", "Online", "Daring"),
    "offline": ("Offline", "Offline", "Offline", "Luring"),
    "online_tip": ("Iha internet: Lafa bele atualiza dadus no hatudu imajen foun.", "Com internet: o Lafa pode atualizar dados e mostrar imagens novas.", "Online: Lafa can update data and show new pictures.", "Ada internet: Lafa bisa memperbarui data dan menampilkan gambar baru."),
    "offline_tip": ("La iha internet: ensiklopédia, mapa, kuis no lian hotu servisu nafatin.", "Sem internet: a enciclopédia, o mapa, o quiz e as línguas continuam a funcionar.", "Offline: the encyclopedia, map, quiz and languages all keep working.", "Tanpa internet: ensiklopedia, peta, kuis dan bahasa tetap berfungsi."),
    "notifications": ("Avizu", "Avisos", "Notifications", "Pemberitahuan"),
    "no_notifications": ("La iha avizu foun.", "Sem avisos novos.", "No new notifications.", "Tidak ada pemberitahuan baru."),
    "offline_promo_title": ("Hola dadus ba offline", "Guardar dados offline", "Get data for offline", "Simpan data luring"),
    "offline_promo_text": ("Download testu no imajen hotu, atu aprende la ho internet.", "Descarregue textos e imagens para aprender sem internet.", "Download texts and pictures to learn without internet.", "Unduh teks dan gambar untuk belajar tanpa internet."),
    "offline_promo_button": ("Download agora", "Descarregar agora", "Download now", "Unduh sekarang"),
    "review_banner": ("MODU REVIZAUN · dadus ezemplu · la rai no la haruka buat ida", "MODO DE REVISÃO · dados de exemplo · nada é guardado nem enviado", "REVIEW MODE · sample data · nothing is saved or sent", "MODE TINJAUAN · data contoh · tidak ada yang disimpan atau dikirim"),
    "learner": ("Estudante", "Estudante", "Learner", "Pelajar"),
    # --- home
    "greet_morning": ("Bondia", "Bom dia", "Good morning", "Selamat pagi"),
    "greet_afternoon": ("Botarde", "Boa tarde", "Good afternoon", "Selamat siang"),
    "greet_evening": ("Bonoite", "Boa noite", "Good evening", "Selamat malam"),
    "home_sub": ("Ohin ita sei aprende saida kona-ba Timór-Leste?", "O que vamos aprender hoje sobre Timor-Leste?", "What shall we learn about Timor-Leste today?", "Apa yang akan kita pelajari hari ini tentang Timor-Leste?"),
    "start_learning": ("Hahú aprende", "Começar a aprender", "Start learning", "Mulai belajar"),
    "play_quiz": ("Halimar kuis", "Jogar o quiz", "Play the quiz", "Main kuis"),
    "stat_articles": ("Artigu", "Artigos", "Articles", "Artikel"),
    "stat_articles_note": ("{n} lee ona", "{n} lidos", "{n} read", "{n} sudah dibaca"),
    "stat_municipalities": ("Munisípiu", "Municípios", "Municipalities", "Munisipio"),
    "stat_municipalities_note": ("{n} esplora ona", "{n} explorados", "{n} explored", "{n} dijelajahi"),
    "stat_places": ("Fatin turístiku", "Lugares turísticos", "Tourist places", "Tempat wisata"),
    "stat_places_note": ("{n} haree ona", "{n} vistos", "{n} viewed", "{n} sudah dilihat"),
    "stat_words": ("Liafuan", "Palavras", "Words", "Kata"),
    "stat_words_note": ("{n} aprende ona", "{n} aprendidas", "{n} learned", "{n} sudah dipelajari"),
    "continue_learning": ("Kontinua aprende", "Continuar a aprender", "Continue learning", "Lanjutkan belajar"),
    "upcoming_days": ("Loron importante tuir mai", "Próximas datas importantes", "Coming up", "Hari penting berikutnya"),
    "in_days": ("loron {n} tan", "daqui a {n} dias", "in {n} days", "{n} hari lagi"),
    "today": ("Ohin", "Hoje", "Today", "Hari ini"),
    "tomorrow": ("Aban", "Amanhã", "Tomorrow", "Besok"),
    "today_history": ("Ohin iha istória", "Neste dia na história", "On this day", "Hari ini dalam sejarah"),
    "this_month_history": ("Iha fulan ne'e, iha istória", "Neste mês, na história", "This month in history", "Bulan ini dalam sejarah"),
    "word_of_day": ("Liafuan loron nian", "Palavra do dia", "Word of the day", "Kata hari ini"),
    "did_you_know": ("Ita hatene ka lae?", "Sabia que…?", "Did you know?", "Tahukah kamu?"),
    "read_more": ("Lee liu tan", "Ler mais", "Read more", "Baca selengkapnya"),
    "population_chart": ("Populasaun Timór-Leste", "População de Timor-Leste", "Population of Timor-Leste", "Penduduk Timor-Leste"),
    "content_chart": ("Konteúdu ensiklopédia", "Conteúdo da enciclopédia", "Encyclopedia content", "Isi ensiklopedia"),
    "my_progress": ("Ha'u-nia progresu", "O meu progresso", "My progress", "Kemajuan saya"),
    "progress_caption": ("husi konteúdu hotu", "de todo o conteúdo", "of all content", "dari semua isi"),
    "place_of_week": ("Fatin semana nian", "Lugar da semana", "Place of the week", "Tempat minggu ini"),
    "show_on_map": ("Haree iha mapa", "Ver no mapa", "Show on map", "Lihat di peta"),
    "achievements": ("Konkista sira", "Conquistas", "Achievements", "Pencapaian"),
    "unlocked": ("LOKE ONA", "DESBLOQUEADO", "UNLOCKED", "TERBUKA"),
    "locked": ("Seidauk loke", "Bloqueado", "Locked", "Belum terbuka"),
    "level": ("Nível", "Nível", "Level", "Jenjang"),
    "xp_level": ("Nível {n} · {xp} XP", "Nível {n} · {xp} XP", "Level {n} · {xp} XP", "Level {n} · {xp} XP"),
    "streak": ("Loron {n} tuituir malu", "{n} dias seguidos", "{n}-day streak", "{n} hari berturut-turut"),
    "source_label": ("Fonte", "Fonte", "Source", "Sumber"),
    "data_year": ("Dadus {year}", "Dados de {year}", "Data {year}", "Data {year}"),
    "see_all": ("Haree hotu", "Ver tudo", "See all", "Lihat semua"),
    "open": ("Loke", "Abrir", "Open", "Buka"),
    "close": ("Taka", "Fechar", "Close", "Tutup"),
    "all": ("Hotu", "Todos", "All", "Semua"),
    "empty_content": ("Konteúdu sei to'o", "O conteúdo está a chegar", "Content is on its way", "Isi sedang disiapkan"),
    "empty_content_text": ("Seidauk iha artigu iha ne'e. Atualiza dadus bainhira iha internet.", "Ainda não há artigos aqui. Atualize os dados quando tiver internet.", "No articles here yet. Update the data when you are online.", "Belum ada artikel di sini. Perbarui data saat ada internet."),
    # --- encyclopedia & articles
    "enc_title": ("Ensiklopédia Timór-Leste", "Enciclopédia de Timor-Leste", "Encyclopedia of Timor-Leste", "Ensiklopedia Timor-Leste"),
    "enc_sub": ("Husi tasi-le'un Timór nia moris to'o 2026: istória, kultura, Estadu, ekonomia no natureza.", "Da formação da ilha até 2026: história, cultura, Estado, economia e natureza.", "From the birth of the island to 2026: history, culture, State, economy and nature.", "Dari terbentuknya pulau sampai 2026: sejarah, budaya, negara, ekonomi dan alam."),
    "n_articles": ("artigu {n}", "{n} artigos", "{n} articles", "{n} artikel"),
    "n_items": ("{n}", "{n}", "{n}", "{n}"),
    "all_levels": ("Nível hotu", "Todos os níveis", "All levels", "Semua jenjang"),
    "simple": ("Simples", "Simples", "Simple", "Sederhana"),
    "complete": ("Kompletu", "Completo", "Complete", "Lengkap"),
    "read_tab": ("Lee", "Ler", "Read", "Baca"),
    "quiz_tab": ("Kuis", "Quiz", "Quiz", "Kuis"),
    "key_facts": ("Faktu importante", "Factos principais", "Key facts", "Fakta penting"),
    "timeline_title": ("Liña tempu", "Cronologia", "Timeline", "Lini masa"),
    "related": ("Haree mós", "Ver também", "See also", "Lihat juga"),
    "sources": ("Fonte", "Fontes", "Sources", "Sumber"),
    "licence": ("Lisensa", "Licença", "Licence", "Lisensi"),
    "accessed": ("asesu {date}", "acedido em {date}", "accessed {date}", "diakses {date}"),
    "review_draft": ("Versaun provizória: presiza revizaun husi espesialista", "Rascunho: precisa de revisão por especialista", "Draft: needs expert review", "Draf: perlu ditinjau ahli"),
    "review_ok": ("Revee ona", "Revisto", "Reviewed", "Sudah ditinjau"),
    "save": ("Rai", "Guardar", "Save", "Simpan"),
    "saved": ("Rai ona", "Guardado", "Saved", "Tersimpan"),
    "read_aloud": ("Lee ho lian maka'as", "Ler em voz alta", "Read aloud", "Bacakan"),
    "stop_reading": ("Para lee", "Parar leitura", "Stop reading", "Berhenti membaca"),
    "wiki_online": ("Lee iha Wikipedia", "Ler na Wikipédia", "Read on Wikipedia", "Baca di Wikipedia"),
    "offline_extract": ("Testu husi Wikipedia (download ona)", "Texto da Wikipédia (descarregado)", "Text from Wikipedia (downloaded)", "Teks dari Wikipedia (sudah diunduh)"),
    "photo_credit": ("Foto: {author} · {licence}", "Foto: {author} · {licence}", "Photo: {author} · {licence}", "Foto: {author} · {licence}"),
    "illustration_credit": ("Ilustrasaun Lafa (CC BY-SA 4.0)", "Ilustração Lafa (CC BY-SA 4.0)", "Lafa illustration (CC BY-SA 4.0)", "Ilustrasi Lafa (CC BY-SA 4.0)"),
    "full_text_in": ("Testu kompletu: {langs}", "Texto completo: {langs}", "Full text: {langs}", "Teks lengkap: {langs}"),
    "article_quiz": ("Teste ita-nia koñesimentu", "Teste os seus conhecimentos", "Test what you know", "Uji pengetahuanmu"),
    "question_n": ("Pergunta {i} husi {n}", "Pergunta {i} de {n}", "Question {i} of {n}", "Soal {i} dari {n}"),
    "right": ("Loos!", "Certo!", "Right!", "Benar!"),
    "wrong": ("La loos.", "Errado.", "Not quite.", "Salah."),
    "next": ("Tuir mai", "Seguinte", "Next", "Berikutnya"),
    "finish": ("Remata", "Terminar", "Finish", "Selesai"),
    "score": ("Ita hatán loos {s} husi {n}", "Acertou {s} de {n}", "You got {s} of {n} right", "Benar {s} dari {n}"),
    "again": ("Koko fali", "Tentar de novo", "Try again", "Coba lagi"),
    "no_quiz": ("Artigu ne'e seidauk iha pergunta.", "Este artigo ainda não tem perguntas.", "This article has no questions yet.", "Artikel ini belum punya soal."),
    "municipality": ("Munisípiu", "Município", "Municipality", "Munisipio"),
    "capital": ("Kapitál", "Capital", "Capital", "Ibu kota"),
    "area": ("Área", "Área", "Area", "Luas"),
    "population": ("Populasaun", "População", "Population", "Penduduk"),
    "posts": ("Postu administrativu", "Postos administrativos", "Administrative posts", "Pos administratif"),
    "languages_spoken": ("Lian", "Línguas", "Languages", "Bahasa"),
    "products": ("Produtu", "Produtos", "Products", "Produk"),
    "places_here": ("Fatin turístiku iha ne'e", "Lugares turísticos aqui", "Places to visit here", "Tempat wisata di sini"),
    "visit_tips": ("Konsellu ba vizita", "Dicas para a visita", "Visiting tips", "Tips berkunjung"),
    "coordinates": ("Koordenada", "Coordenadas", "Coordinates", "Koordinat"),
    "type": ("Tipu", "Tipo", "Type", "Jenis"),
    "holiday": ("Feriadu nasionál", "Feriado nacional", "Public holiday", "Hari libur nasional"),
    "commemorative": ("Loron komemorativu", "Data comemorativa", "Commemorative day", "Hari peringatan"),
    "date_this_year": ("Data iha {year}", "Data em {year}", "Date in {year}", "Tanggal pada {year}"),
    "law": ("Lei", "Lei", "Law", "Undang-undang"),
    # --- search
    "search_results": ("Rezultadu ba “{q}”", "Resultados para “{q}”", "Results for “{q}”", "Hasil untuk “{q}”"),
    "no_results": ("La hetan buat ida. Koko liafuan seluk.", "Nada encontrado. Tente outras palavras.", "Nothing found. Try other words.", "Tidak ada hasil. Coba kata lain."),
    "kind_article": ("Artigu", "Artigo", "Article", "Artikel"),
    "kind_municipality": ("Munisípiu", "Município", "Municipality", "Munisipio"),
    "kind_place": ("Fatin", "Lugar", "Place", "Tempat"),
    "kind_day": ("Loron", "Data", "Day", "Hari"),
    "kind_word": ("Liafuan", "Palavra", "Word", "Kata"),
}

def t(lang, key, **values):
    row = T.get(key)
    if row is None: return key
    text = pick(row, lang)
    if values:
        try: text = text.format(**values)
        except (KeyError, IndexError, ValueError): pass
    return show(text, lang)

def index(lang):
    """Position of the language in the (tet, pt, en, id) rows; Tetun for unknown codes."""
    return LANGS.index(lang) if lang in LANGS else 0

def extend(rows):
    """Pages register their own words (keeps each page's texts next to its code)."""
    for key, row in rows.items():
        if len(row) != len(LANGS): raise ValueError(f"{key}: Tetun, Portuguese, English and Indonesian needed")
        T[key] = row
