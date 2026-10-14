"""Interface text of LAFA 0.2.0: six sections, local search, reminders,
practice, sources and the calm Virtual Assistant. No AI wording: Lafa looks
things up in its own material; it does not generate answers.

Merged last into i18n.CATALOG (it overrides older texts with the same key).
Keys must be the same in every language.
"""

def _rows(text):
    """'key | en | id | pt | tet' lines → {lang: {key: text}}."""
    out = {"en": {}, "id": {}, "pt": {}, "tet": {}}
    for line in text.strip().splitlines():
        if not line.strip() or line.lstrip().startswith("#"): continue
        key, en, id_, pt, tet = [part.strip() for part in line.split(" | ")]
        for lang, value in zip(("en", "id", "pt", "tet"), (en, id_, pt, tet)):
            out[lang][key] = value.replace("\\n", "\n")
    return out

V2 = _rows(r"""
# ---- shared small texts
type_first | Type something first. | Ketik sesuatu dulu. | Escreva algo primeiro. | Hakerek buat ruma uluk.
choose_first | Choose an item in the list first. | Pilih satu item di daftar dulu. | Escolha primeiro um item da lista. | Hili item ida iha lista uluk.
load_news_first | Load the news first. | Muat berita dulu. | Carregue primeiro as notícias. | Karrega notísia sira uluk.
nothing_to_read | There is nothing to read aloud yet. | Belum ada yang bisa dibacakan. | Ainda não há nada para ler. | Seidauk iha buat ida atu lee.
learner_age | Learner's age | Usia pelajar | Idade do aluno | Estudante nia idade
school_lessons | Timor-Leste school lessons | Pelajaran sekolah Timor-Leste | Lições escolares de Timor-Leste | Lisaun eskola Timor-Leste
every_age | every age | semua usia | todas as idades | idade hotu
all_ages | All ages | Semua usia | Todas as idades | Idade hotu
learn_more | Learn more | Pelajari lebih lanjut | Saber mais | Aprende liután
memory_done | updated {sites} sites, {pages} pages ({failed} did not answer) | {sites} situs, {pages} halaman diperbarui ({failed} tidak menjawab) | {sites} sites, {pages} páginas atualizados ({failed} sem resposta) | sítiu {sites}, pájina {pages} atualiza ona ({failed} la hatán)
# ---- product, menus and section subtitles
product_name | Lafa — learning companion and Edukasaun OS assistant | Lafa — Pendamping Belajar dan Asisten Edukasaun OS | Lafa — companheiro de estudo e assistente do Edukasaun OS | Lafa — belun aprendizajen no asistente Edukasaun OS
home | Home | Beranda | Início | Uma
menu_study | Learn | Belajar | Aprender | Aprende
menu_library | Library | Perpustakaan | Biblioteca | Biblioteka
menu_timor | Timor-Leste | Timor-Leste | Timor-Leste | Timor-Leste
menu_activities | My activities | Aktivitas Saya | As minhas atividades | Ha'u-nia atividade
menu_oshelp | OS help | Bantuan OS | Ajuda do sistema | Ajuda OS
sub_home | Lessons, knowledge and files — on this computer | Pelajaran, pengetahuan, dan file — di komputer ini | Lições, conhecimento e ficheiros — neste computador | Lisaun, koñesimentu no ficheiru — iha komputadór ne'e
sub_study | Lessons, practice, languages, digital literacy and programming examples | Pelajaran, latihan, bahasa, literasi digital, dan contoh pemrograman | Lições, exercícios, línguas, literacia digital e exemplos de programação | Lisaun, prátika, lian, literasia dijitál no ezemplu programasaun
sub_library | Local files, saved material, internet sources and favourites | File lokal, materi tersimpan, sumber internet, dan favorit | Ficheiros locais, material guardado, fontes da internet e favoritos | Ficheiru lokál, materiál rai ona, fonte internet no favoritu
sub_timor | History, geography, culture, national symbols and news | Sejarah, geografi, budaya, simbol nasional, dan berita | História, geografia, cultura, símbolos nacionais e notícias | Istória, jeografia, kultura, símbolu nasionál no notísia
sub_activities | Tasks, timetable, reminders, focus and practice results | Tugas, jadwal, pengingat, fokus, dan hasil latihan | Trabalhos, horário, lembretes, foco e resultados dos exercícios | Knaar, orariu, fó-hanoin, foku no rezultadu prátika
sub_oshelp | Edukasaun OS guides, accessibility, computer check and apps | Panduan Edukasaun OS, aksesibilitas, pemeriksaan komputer, dan aplikasi | Guias do Edukasaun OS, acessibilidade, verificação do computador e aplicações | Matadalan Edukasaun OS, asesibilidade, verifikasaun komputadór no aplikasaun
settings | Settings | Pengaturan | Definições | Konfigurasaun
about | About | Tentang | Sobre | Kona-ba
close | Close | Tutup | Fechar | Taka
status | Status | Status | Estado | Estadu
connection | Connection | Koneksi | Ligação | Koneksaun
local_ready | Local features are available | Fitur lokal tetap tersedia | As funções locais estão disponíveis | Funsaun lokál prontu
online | Online · internet sources too | Online · sumber internet juga | Online · também fontes da internet | Online · fonte internet mós
online_note | Internet adds Wikipedia, news, weather and websites. Everything else works without it. | Internet menambah Wikipedia, berita, cuaca, dan situs web. Fitur lain tetap jalan tanpa internet. | A internet acrescenta Wikipédia, notícias, tempo e sites. Tudo o resto funciona sem ela. | Internet aumenta Wikipédia, notísia, tempu no sítiu. Buat seluk servisu la ho internet.
offline_intro | Local features are available — these work without internet: | Fitur lokal tetap tersedia — ini bisa dipakai tanpa internet: | As funções locais continuam disponíveis — sem internet: | Funsaun lokál sei iha — ida-ne'e servisu la ho internet:
needs_internet_calm | This needs internet. Local lessons, files, tasks and reminders still work. | Ini memerlukan internet. Pelajaran, file, tugas, dan pengingat lokal tetap bisa dipakai. | Isto precisa de internet. As lições, ficheiros, trabalhos e lembretes locais continuam a funcionar. | Ida-ne'e presiza internet. Lisaun, ficheiru, knaar no fó-hanoin lokál sei servisu.
internet_later | Internet sources can be searched when you are online. | Sumber internet bisa dicari saat Anda online. | As fontes da internet podem ser pesquisadas quando estiver online. | Fonte internet bele buka bainhira ita online.
internet_failed | The internet source did not answer. Local results are still shown. | Sumber internet tidak menjawab. Hasil lokal tetap ditampilkan. | A fonte da internet não respondeu. Os resultados locais continuam visíveis. | Fonte internet la hatán. Rezultadu lokál sei hatudu.
review_banner | REVIEW MODE · sample content · nothing is saved or sent | MODE PRATINJAU · contoh isi · tidak ada yang disimpan atau dikirim | MODO DE REVISÃO · conteúdo de exemplo · nada é guardado nem enviado | MODU REVIZAUN · ezemplu · la rai no la haruka buat ida
# ---- Home
search_box | Search lessons, knowledge or files… | Cari pelajaran, pengetahuan, atau file… | Pesquisar lições, conhecimento ou ficheiros… | Buka lisaun, koñesimentu ka ficheiru…
find | Search | Cari | Pesquisar | Buka
start_learning | Start learning | Mulai Belajar | Começar a aprender | Hahú aprende
find_knowledge | Find knowledge | Cari Pengetahuan | Procurar conhecimento | Buka koñesimentu
tasks_schedule | Tasks & schedule | Tugas & Jadwal | Trabalhos e horário | Knaar no orariu
os_help | OS help | Bantuan OS | Ajuda do sistema | Ajuda OS
quick_learn_d | Lessons for every age, practice and languages | Pelajaran untuk semua usia, latihan, dan bahasa | Lições para todas as idades, exercícios e línguas | Lisaun ba idade hotu, prátika no lian
quick_find_d | Search lessons, the atlas and your files | Cari pelajaran, atlas, dan file Anda | Pesquisar lições, o atlas e os seus ficheiros | Buka lisaun, atlas no ita-nia ficheiru
quick_tasks_d | Homework, timetable and reminders | PR, jadwal, dan pengingat | Trabalhos de casa, horário e lembretes | TPC, orariu no fó-hanoin
quick_os_d | Guides for Edukasaun OS and your computer | Panduan Edukasaun OS dan komputer Anda | Guias do Edukasaun OS e do computador | Matadalan Edukasaun OS no ita-nia komputadór
recent_material | Last material | Materi terakhir | Último material | Materiál ikus
no_recent | Nothing opened yet. Start with a lesson in Learn. | Belum ada yang dibuka. Mulailah dengan pelajaran di Belajar. | Ainda nada aberto. Comece com uma lição em Aprender. | Seidauk loke buat ida. Hahú ho lisaun ida iha Aprende.
continue_learning | Continue learning | Lanjut belajar | Continuar a aprender | Kontinua aprende
next_activity | Next activities | Aktivitas berikutnya | Próximas atividades | Atividade tuir mai
nothing_planned | No tasks or reminders yet. | Belum ada tugas atau pengingat. | Ainda não há trabalhos nem lembretes. | Seidauk iha knaar ka fó-hanoin.
virtual_where | The Lafa Virtual Assistant is switched on in Eduka-Settings → Lafa-Configuration. | Lafa Virtual Assistant diaktifkan di Eduka-Settings → Lafa-Configuration. | O Assistente Virtual Lafa ativa-se em Eduka-Settings → Lafa-Configuration. | Asistente Virtuál Lafa ativa iha Eduka-Settings → Lafa-Configuration.
virtual_on | The Lafa Virtual Assistant is on (Eduka-Settings → Lafa-Configuration). | Lafa Virtual Assistant aktif (Eduka-Settings → Lafa-Configuration). | O Assistente Virtual Lafa está ligado (Eduka-Settings → Lafa-Configuration). | Asistente Virtuál Lafa ativu (Eduka-Settings → Lafa-Configuration).
# ---- search results
search_intro | Lafa searches its own lessons, the Timor-Leste atlas, Edukasaun OS guides, material you saved and your files. It does not invent answers. Internet sources are a separate button. | Lafa mencari di pelajarannya sendiri, atlas Timor-Leste, panduan Edukasaun OS, materi yang Anda simpan, dan file Anda. Lafa tidak mengarang jawaban. Sumber internet ada di tombol terpisah. | O Lafa pesquisa nas suas lições, no atlas de Timor-Leste, nos guias do Edukasaun OS, no material guardado e nos seus ficheiros. Não inventa respostas. As fontes da internet estão num botão à parte. | Lafa buka iha ninia lisaun rasik, atlas Timor-Leste, matadalan Edukasaun OS, materiál ne'ebé ita rai no ita-nia ficheiru. Lafa la halo resposta falsu. Fonte internet iha butaun seluk.
search_examples | Try: What is photosynthesis?|Find file maths homework|How to change the wallpaper?|12 * (3 + 4)|Ataúro | Coba: Apa itu fotosintesis?|Cari file tugas matematika|Bagaimana mengganti wallpaper?|12 * (3 + 4)|Ataúro | Experimente: O que é a fotossíntese?|Procurar ficheiro trabalho matemática|Como mudar o fundo do ecrã?|12 * (3 + 4)|Ataúro | Koko: Saida mak fotosíntese?|Buka ficheiru knaar matemátika|Oinsá troka wallpaper?|12 * (3 + 4)|Ataúro
searching | Searching… | Mencari… | A pesquisar… | Buka hela…
results | Results | Hasil | Resultados | Rezultadu
label_lesson | Local material | Materi lokal | Material local | Materiál lokál
label_file | Local file | File lokal | Ficheiro local | Ficheiru lokál
label_saved | Saved material | Materi tersimpan | Material guardado | Materiál rai ona
label_internet | Internet source | Sumber internet | Fonte da internet | Fonte internet
label_guide | OS guide | Panduan OS | Guia do sistema | Matadalan OS
from_material | From | Dari | De | Husi
more_results | Other results | Hasil lain | Outros resultados | Rezultadu seluk
search_choices | Lafa has no exact answer for “{q}”. These materials may help: | Lafa belum menemukan jawaban pasti untuk “{q}”. Materi ini mungkin membantu: | O Lafa não tem uma resposta exata para “{q}”. Estes materiais podem ajudar: | Lafa seidauk iha resposta loloos ba “{q}”. Materiál sira-ne'e bele ajuda:
search_none | Lafa found nothing about “{q}” on this computer. | Lafa tidak menemukan apa pun tentang “{q}” di komputer ini. | O Lafa não encontrou nada sobre “{q}” neste computador. | Lafa la hetan buat ida kona-ba “{q}” iha komputadór ne'e.
try_other_words | Try other or fewer words. | Coba kata lain atau lebih sedikit kata. | Experimente outras palavras ou menos palavras. | Koko liafuan seluk ka liafuan uitoan.
browse_lessons | Browse the lessons | Lihat daftar pelajaran | Ver as lições | Haree lisaun sira
try_internet_button | When online, use “Search internet sources”. | Saat online, gunakan “Cari sumber di internet”. | Quando estiver online, use “Pesquisar fontes na internet”. | Bainhira online, uza “Buka fonte iha internet”.
search_internet | Search internet sources | Cari sumber di internet | Pesquisar fontes na internet | Buka fonte iha internet
search_internet_note | Sends only the topic words to Wikipedia, when you press this button. | Hanya kata topik yang dikirim ke Wikipedia, saat Anda menekan tombol ini. | Só as palavras do tema são enviadas à Wikipédia, quando carrega neste botão. | Liafuan tópiku de'it mak haruka ba Wikipédia, bainhira ita klik butaun ne'e.
searching_internet | Searching Wikipedia… | Mencari di Wikipedia… | A pesquisar na Wikipédia… | Buka hela iha Wikipédia…
show_extract | Show extract | Tampilkan kutipan | Mostrar extrato | Hatudu estratu
article_extract | Article extract | Kutipan artikel | Extrato do artigo | Estratu artigu
extract_note | Extract from an internet article — not Lafa's own explanation. Check the source. | Kutipan dari artikel internet — bukan penjelasan Lafa. Periksa sumbernya. | Extrato de um artigo da internet — não é uma explicação do Lafa. Verifique a fonte. | Estratu husi artigu internet — la'ós Lafa nia esplikasaun. Haree fonte.
local_document_note | Opened on this computer. Lafa does not send files anywhere. | Dibuka di komputer ini. Lafa tidak mengirim file ke mana pun. | Aberto neste computador. O Lafa não envia ficheiros para lado nenhum. | Loke iha komputadór ne'e. Lafa la haruka ficheiru ba fatin ruma.
open_browser | Open in browser | Buka di browser | Abrir no navegador | Loke iha navegadór
open_in_browser | Open in browser | Buka di browser | Abrir no navegador | Loke iha navegadór
save_offline | Save for offline | Simpan untuk offline | Guardar para offline | Rai ba offline
saved_offline | Saved for offline use (Library → Saved material). | Disimpan untuk offline (Perpustakaan → Materi tersimpan). | Guardado para uso offline (Biblioteca → Material guardado). | Rai ona ba offline (Biblioteka → Materiál rai ona).
cannot_save | This source cannot be saved (login, Facebook or no text). | Sumber ini tidak bisa disimpan (login, Facebook, atau tanpa teks). | Esta fonte não pode ser guardada (login, Facebook ou sem texto). | Fonte ne'e la bele rai (login, Facebook ka la iha testu).
files_found | Files found: {n} | File ditemukan: {n} | Ficheiros encontrados: {n} | Ficheiru hetan: {n}
files_none | No file name matches “{q}” in your folders. | Tidak ada nama file yang cocok dengan “{q}” di folder Anda. | Nenhum nome de ficheiro corresponde a “{q}” nas suas pastas. | La iha naran ficheiru ne'ebé hanesan “{q}” iha ita-nia pasta.
files_no_folders | Choose folders in Settings → Files & weather. | Pilih folder di Pengaturan → File & cuaca. | Escolha pastas em Definições → Ficheiros e tempo. | Hili pasta iha Konfigurasaun → Ficheiru no tempu.
files_private | File names and contents stay on this computer. | Nama dan isi file tetap di komputer ini. | Os nomes e conteúdos dos ficheiros ficam neste computador. | Naran no konteúdu ficheiru hela iha komputadór ne'e.
outside_folders | This file is outside the folders chosen in Settings. | File ini di luar folder yang dipilih di Pengaturan. | Este ficheiro está fora das pastas escolhidas nas Definições. | Ficheiru ne'e iha li'ur pasta ne'ebé hili iha Konfigurasaun.
no_app_for_file | No application could open this file. | Tidak ada aplikasi yang bisa membuka file ini. | Nenhuma aplicação conseguiu abrir este ficheiro. | La iha aplikasaun ne'ebé bele loke ficheiru ne'e.
open_guide | Open the guide | Buka panduan | Abrir o guia | Loke matadalan
favourite | Favourite | Favorit | Favorito | Favoritu
favourite_added | Added to favourites. | Ditambahkan ke favorit. | Adicionado aos favoritos. | Aumenta ona ba favoritu.
favourite_removed | Removed from favourites. | Dihapus dari favorit. | Removido dos favoritos. | Hasai ona husi favoritu.
remove_favourite | Remove | Hapus | Remover | Hasai
no_favourites | No favourites yet. Use ☆ on a lesson or a search result. | Belum ada favorit. Gunakan ☆ pada pelajaran atau hasil pencarian. | Ainda sem favoritos. Use ☆ numa lição ou num resultado. | Seidauk iha favoritu. Uza ☆ iha lisaun ka rezultadu.
favourites_intro | Your starred lessons, guides and sources, saved on this computer. | Pelajaran, panduan, dan sumber yang Anda tandai, tersimpan di komputer ini. | As lições, guias e fontes marcados, guardados neste computador. | Lisaun, matadalan no fonte ne'ebé ita marka, rai iha komputadór ne'e.
# ---- tabs
tab_lessons | Lessons | Pelajaran | Lições | Lisaun
tab_subjects | Subjects | Mata pelajaran | Disciplinas | Matéria
tab_practice | Practice | Latihan | Exercícios | Prátika
tab_languages | Languages | Bahasa | Línguas | Lian
tab_digital | Digital literacy | Literasi digital | Literacia digital | Literasia dijitál
tab_coding | Programming | Pemrograman | Programação | Programasaun
tab_fun | Entertainment | Hiburan | Entretenimento | Divertimentu
tab_search | Search | Cari | Pesquisa | Buka
tab_files | My files | File saya | Os meus ficheiros | Ha'u-nia ficheiru
tab_saved | Saved material | Materi tersimpan | Material guardado | Materiál rai ona
tab_sources | Internet sources | Sumber internet | Fontes da internet | Fonte internet
tab_wikipedia | Wikipedia | Wikipedia | Wikipédia | Wikipédia
tab_favourites | Favourites | Favorit | Favoritos | Favoritu
tab_external | External sites | Situs eksternal | Sites externos | Sítiu esternu
tab_atlas | History, places & symbols | Sejarah, tempat & simbol | História, lugares e símbolos | Istória, fatin no símbolu
tab_news | News | Berita | Notícias | Notísia
tab_weather | Weather & world | Cuaca & dunia | Tempo e mundo | Tempu no mundu
tab_tasks | Tasks & timetable | Tugas & jadwal | Trabalhos e horário | Knaar no orariu
tab_reminders | Reminders & focus | Pengingat & fokus | Lembretes e foco | Fó-hanoin no foku
tab_results | Practice results | Hasil Latihan | Resultados dos exercícios | Rezultadu prátika
tab_guides | Guides | Panduan | Guias | Matadalan
tab_access | Accessibility | Aksesibilitas | Acessibilidade | Asesibilidade
tab_computer | Computer & apps | Komputer & aplikasi | Computador e aplicações | Komputadór no aplikasaun
# ---- learning
subject_guide_note | Subject guide: practice here, and search LAFA's lessons below. | Pemandu mata pelajaran: berlatih di sini, dan cari pelajaran LAFA di bawah. | Guia da disciplina: pratique aqui e pesquise as lições do LAFA abaixo. | Matadalan matéria: pratika iha ne'e, no buka lisaun LAFA iha okos.
find_material | Find material | Cari materi | Procurar material | Buka materiál
digital_intro | Lessons about computers, the internet and communication, for every age. All offline. | Pelajaran tentang komputer, internet, dan komunikasi untuk semua usia. Semua offline. | Lições sobre computadores, internet e comunicação, para todas as idades. Tudo offline. | Lisaun kona-ba komputadór, internet no komunikasaun, ba idade hotu. Hotu offline.
phrases_note | Basic phrases (25 per language), not a full course. Tetun, Português, English and Indonesian first; other languages are extras. | Frasa dasar (25 per bahasa), bukan kursus lengkap. Tetun, Portugis, Inggris, dan Indonesia diutamakan; bahasa lain tambahan. | Frases básicas (25 por língua), não é um curso completo. Primeiro tétum, português, inglês e indonésio; as outras línguas são extra. | Fraze báziku (25 kada lian), la'ós kursu kompletu. Tetun, Portugés, Inglés no Indonézia uluk; lian seluk mak aumentu.
language_school | Basic phrases | Frasa dasar | Frases básicas | Fraze báziku
quiz | Practice | Latihan | Exercício | Prátika
quiz_d | 5 questions · answer and explanation at once | 5 soal · jawaban dan penjelasan langsung | 5 perguntas · resposta e explicação logo | Pergunta 5 · resposta no esplikasaun kedas
test | Test simulation | Simulasi Tes | Simulação de teste | Simulasaun teste
test_d | 10 questions · results at the end | 10 soal · hasil di akhir | 10 perguntas · resultados no fim | Pergunta 10 · rezultadu iha ikus
exam | Timed test simulation | Simulasi Tes berwaktu | Simulação de teste com tempo | Simulasaun teste ho tempu
exam_d | up to 20 questions · with a time limit | hingga 20 soal · dengan batas waktu | até 20 perguntas · com limite de tempo | to pergunta 20 · ho limite tempu
exams | Practice | Latihan | Exercícios | Prátika
report_card | Practice results | Hasil Latihan | Resultados dos exercícios | Rezultadu prátika
results_personal | Your personal progress on this computer — not an official school report. | Kemajuan pribadi Anda di komputer ini — bukan rapor resmi sekolah. | O seu progresso pessoal neste computador — não é um boletim oficial da escola. | Ita-nia progresu pesoál iha komputadór ne'e — la'ós boletin ofisiál eskola nian.
no_results | No results yet — try a practice in Learn → Practice. | Belum ada hasil — coba latihan di Belajar → Latihan. | Ainda sem resultados — experimente um exercício em Aprender → Exercícios. | Seidauk iha rezultadu — koko prátika iha Aprende → Prátika.
average | Average score | Rata-rata skor | Média das pontuações | Média pontu
bank_limited | The question bank has only {n} different questions here (not {want}); no question repeats. | Bank soal hanya punya {n} soal berbeda di sini (bukan {want}); tidak ada soal yang diulang. | O banco tem só {n} perguntas diferentes aqui (não {want}); nenhuma se repete. | Banku pergunta iha de'it pergunta diferente {n} iha ne'e (la'ós {want}); pergunta la repete.
retry_mistakes | Practise the wrong answers again | Ulangi soal yang salah | Repetir as respostas erradas | Prátika fali resposta sala
retry_note | Practising only the questions you got wrong (not saved as a result). | Hanya mengulang soal yang salah (tidak disimpan sebagai hasil). | Só as perguntas erradas (não fica guardado como resultado). | Prátika de'it pergunta sala (la rai hanesan rezultadu).
related_lesson | Related lesson | Materi terkait | Lição relacionada | Lisaun relasionadu
# ---- library
saved_intro | Pages you chose to keep for offline use. Saved material may be out of date; the date shows when it was saved. | Halaman yang Anda simpan untuk offline. Materi tersimpan bisa sudah lama; tanggal menunjukkan kapan disimpan. | Páginas guardadas para uso offline. O material guardado pode estar desatualizado; a data mostra quando foi guardado. | Pájina ne'ebé ita rai ba offline. Materiál rai ona bele tuan ona; data hatudu bainhira rai.
saved_on | saved on | disimpan | guardado em | rai iha
saved_count | {n} pages saved on this computer | {n} halaman tersimpan di komputer ini | {n} páginas guardadas neste computador | pájina {n} rai iha komputadór ne'e
saved_none | Nothing saved yet. Use “Save for offline” on a Wikipedia extract. | Belum ada yang disimpan. Gunakan “Simpan untuk offline” pada kutipan Wikipedia. | Nada guardado ainda. Use “Guardar para offline” num extrato da Wikipédia. | Seidauk rai buat ida. Uza “Rai ba offline” iha estratu Wikipédia.
update_saved | Update saved pages | Perbarui halaman tersimpan | Atualizar páginas guardadas | Atualiza pájina rai ona
cache_label | saved copy (cache) — may be out of date | salinan tersimpan (cache) — bisa sudah lama | cópia guardada (cache) — pode estar desatualizada | kópia rai ona (cache) — bele tuan ona
sources_note | Reachable only means the site answers — it does not prove its content is correct. Not every site is free; see the notes on each card. | Bisa diakses hanya berarti situs menjawab — bukan bukti isinya benar. Tidak semua situs gratis; lihat catatan di setiap kartu. | Acessível só significa que o site responde — não prova que o conteúdo está certo. Nem todos são gratuitos; veja as notas de cada cartão. | Bele asesu katak sítiu hatán de'it — la prova katak konteúdu loos. La'ós sítiu hotu gratuitu; haree nota iha kartaun ida-idak.
sources_status | {ok} reachable · {restricted} need login/limited · {missing} not found · {unknown} unknown · checked {date} | {ok} bisa diakses · {restricted} perlu login/dibatasi · {missing} tidak ditemukan · {unknown} tidak pasti · dicek {date} | {ok} acessíveis · {restricted} com login/limitados · {missing} não encontrados · {unknown} incertos · verificado {date} | {ok} bele asesu · {restricted} presiza login/limitadu · {missing} la hetan · {unknown} la klaru · verifika {date}
not_academic | not an academic source | bukan sumber akademik | não é fonte académica | la'ós fonte akadémiku
access_free | free | gratis | gratuito | gratuitu
access_free_account | free, account needed | gratis, perlu akun | gratuito, precisa de conta | gratuitu, presiza konta
access_freemium | partly paid | sebagian berbayar | parcialmente pago | balun selu
access_paid | paid / subscription | berbayar / langganan | pago / assinatura | selu / asinatura
access_facebook | Facebook page search (login may be needed) | pencarian halaman Facebook (mungkin perlu login) | pesquisa de página no Facebook (pode pedir login) | buka pájina Facebook (bele presiza login)
access_youtube | YouTube search | pencarian YouTube | pesquisa no YouTube | buka iha YouTube
wikipedia_note | Wikipedia is searched only when you press Search. Extracts are shown as extracts, not as Lafa's explanation. | Wikipedia dicari hanya saat Anda menekan Cari. Kutipan ditampilkan sebagai kutipan, bukan penjelasan Lafa. | A Wikipédia só é pesquisada quando carrega em Pesquisar. Os extratos aparecem como extratos, não como explicação do Lafa. | Wikipédia buka de'it bainhira ita klik Buka. Estratu hatudu hanesan estratu, la'ós Lafa nia esplikasaun.
external_intro | These sites open in your own web browser. Lafa does not sign in, does not read accounts, cookies or passwords, and sends nothing there by itself. | Situs ini dibuka di browser Anda sendiri. Lafa tidak login, tidak membaca akun, cookie, atau kata sandi, dan tidak mengirim apa pun sendiri. | Estes sites abrem no seu navegador. O Lafa não entra em contas, não lê contas, cookies nem palavras-passe e não envia nada por si. | Sítiu sira-ne'e loke iha ita-nia navegadór rasik. Lafa la tama, la lee konta, cookie ka password, no la haruka buat ida rasik.
references | Reference works | Referensi | Obras de referência | Referénsia
ai_links_title | Optional AI websites | Situs AI opsional | Sites de IA opcionais | Sítiu IA opsionál
ai_links_note | Not part of Lafa. You sign in on the company's website; check their answers with real sources. | Bukan bagian dari Lafa. Login dilakukan di situs perusahaan; periksa jawabannya dengan sumber yang benar. | Não fazem parte do Lafa. A entrada é feita no site da empresa; confirme as respostas em fontes fiáveis. | La'ós parte husi Lafa. Ita tama iha kompañia nia sítiu; verifika resposta ho fonte loloos.
community_title | Community & entertainment wikis (extras) | Wiki komunitas & hiburan (tambahan) | Wikis comunitárias e de entretenimento (extra) | Wiki komunidade no divertimentu (aumentu)
community_note | Written by volunteers or fans, sometimes one-sided — not academic sources. | Ditulis relawan atau penggemar, kadang berat sebelah — bukan sumber akademik. | Escritas por voluntários ou fãs, por vezes parciais — não são fontes académicas. | Hakerek husi voluntáriu ka fan, dala ruma la neutru — la'ós fonte akadémiku.
kiwix_title | Wikipedia and books offline | Wikipedia dan buku offline | Wikipédia e livros offline | Wikipédia no livru offline
kiwix_ready | Kiwix is installed: open it to read the offline archives (ZIM) on this computer. | Kiwix terpasang: buka untuk membaca arsip offline (ZIM) di komputer ini. | O Kiwix está instalado: abra-o para ler os arquivos offline (ZIM) deste computador. | Kiwix instala ona: loke atu lee arkivu offline (ZIM) iha komputadór ne'e.
kiwix_missing | Kiwix is not installed. Ask the school technician: sudo apt install kiwix — then copy a ZIM archive (for example Wikipedia in Portuguese) from a USB drive. Lafa never downloads large archives by itself. | Kiwix belum terpasang. Minta teknisi sekolah: sudo apt install kiwix — lalu salin arsip ZIM (misalnya Wikipedia bahasa Portugis) dari flashdisk. Lafa tidak pernah mengunduh arsip besar sendiri. | O Kiwix não está instalado. Peça ao técnico da escola: sudo apt install kiwix — e copie um arquivo ZIM (por exemplo, a Wikipédia em português) de uma pen USB. O Lafa nunca descarrega arquivos grandes sozinho. | Kiwix seidauk instala. Husu tékniku eskola: sudo apt install kiwix — depois kopia arkivu ZIM (hanesan Wikipédia portugés) husi flashdisk. Lafa nunka download arkivu boot rasik.
# ---- activities
reminders_note | Reminders are saved on this computer and ring offline while Lafa is running. Reminders missed while Lafa was closed are shown once at the next start. | Pengingat disimpan di komputer ini dan berbunyi offline selama Lafa berjalan. Pengingat yang terlewat saat Lafa tertutup ditampilkan sekali saat dibuka lagi. | Os lembretes ficam guardados neste computador e tocam offline enquanto o Lafa está aberto. Os que passaram com o Lafa fechado aparecem uma vez no próximo arranque. | Fó-hanoin rai iha komputadór ne'e no tanis offline bainhira Lafa loke. Fó-hanoin ne'ebé liu bainhira Lafa taka, hatudu dala ida bainhira loke fali.
when | When | Kapan | Quando | Bainhira
remaining | Left | Sisa | Falta | Sobra
in_minutes | Quick: | Cepat: | Rápido: | Lalais:
reminder_saved | Reminder saved. | Pengingat disimpan. | Lembrete guardado. | Fó-hanoin rai ona.
reminder_set | OK! I will remind you in {minutes} minutes: {text} | Siap! Saya ingatkan dalam {minutes} menit: {text} | Combinado! Lembro-o daqui a {minutes} minutos: {text} | Di'ak! Ha'u fó-hanoin ita iha minutu {minutes}: {text}
missed_reminder | Missed reminder | Pengingat terlewat | Lembrete perdido | Fó-hanoin liu ona
focus_title | Focus timer | Timer fokus | Temporizador de foco | Tempu foku
focus_session_only | Only for this session: it stops if Lafa is closed. | Hanya untuk sesi ini: berhenti jika Lafa ditutup. | Só nesta sessão: para se o Lafa for fechado. | Ba sesaun ne'e de'it: para se Lafa taka.
focus_start | Start 25 min | Mulai 25 menit | Começar 25 min | Hahú minutu 25
focus_stop | Stop | Berhenti | Parar | Para
focus_started | Focus for {n} minutes started (this session). | Fokus {n} menit dimulai (sesi ini). | Foco de {n} minutos iniciado (esta sessão). | Foku minutu {n} hahú ona (sesaun ne'e).
focus_done | Focus time is over — take a short break. | Waktu fokus selesai — istirahat sebentar. | O tempo de foco acabou — faça uma pausa curta. | Tempu foku remata — deskansa uitoan.
focus_short | Focus | Fokus | Foco | Foku
tasks_short | Tasks | Tugas | Trabalhos | Knaar
news_note | Headlines show publisher, date and the time they were fetched. Saved headlines are not the latest news. | Judul berita menampilkan penerbit, tanggal, dan waktu pengambilan. Judul tersimpan bukan berita terbaru. | Os títulos mostram editor, data e hora de obtenção. Títulos guardados não são as notícias mais recentes. | Títulu hatudu publikadór, data no oras foti. Títulu rai ona la'ós notísia foun liu.
# ---- OS help
access_intro | Tools that help reading, typing and seeing. Lafa opens them only when installed. | Alat untuk membantu membaca, mengetik, dan melihat. Lafa membukanya hanya jika terpasang. | Ferramentas para ler, escrever e ver melhor. O Lafa só as abre quando estão instaladas. | Ferramenta atu ajuda lee, hakerek no haree. Lafa loke de'it bainhira instala ona.
screen_reader | Screen reader (Orca) | Pembaca layar (Orca) | Leitor de ecrã (Orca) | Lee-na'in ekrán (Orca)
onscreen_keyboard | On-screen keyboard | Keyboard di layar | Teclado no ecrã | Tekladu iha ekrán
magnifier | Magnifier | Kaca pembesar | Lupa | Lente boot
text_size | Text size and contrast | Ukuran teks dan kontras | Tamanho do texto e contraste | Tamañu testu no kontraste
installed | installed | terpasang | instalado | instala ona
not_installed | not installed | belum terpasang | não instalado | seidauk instala
access_tips | Tips: Ctrl + plus/minus zooms in many apps · Tab moves between buttons, Enter opens · Alt+1…6 opens Lafa's sections · Ctrl+F jumps to search. | Tips: Ctrl + plus/minus memperbesar di banyak aplikasi · Tab pindah antar tombol, Enter membuka · Alt+1…6 membuka bagian Lafa · Ctrl+F ke kolom cari. | Dicas: Ctrl + mais/menos amplia em muitas aplicações · Tab muda de botão, Enter abre · Alt+1…6 abre as secções do Lafa · Ctrl+F vai para a pesquisa. | Dika: Ctrl + plus/minus halo boot iha aplikasaun barak · Tab muda butaun, Enter loke · Alt+1…6 loke parte Lafa · Ctrl+F ba buka.
apps_title | Apps on this computer | Aplikasi di komputer ini | Aplicações neste computador | Aplikasaun iha komputadór ne'e
updates_via_eus | Edukasaun OS and Lafa are updated with the Eduka Update System (EUS) / APT — Lafa does not update programs itself. | Edukasaun OS dan Lafa diperbarui dengan Eduka Update System (EUS) / APT — Lafa tidak memperbarui program sendiri. | O Edukasaun OS e o Lafa são atualizados com o Eduka Update System (EUS) / APT — o Lafa não atualiza programas sozinho. | Edukasaun OS no Lafa atualiza ho Eduka Update System (EUS) / APT — Lafa la atualiza programa rasik.
app_browser | Web browser | Browser | Navegador | Navegadór
app_files | File manager | Pengelola file | Gestor de ficheiros | Jestór ficheiru
app_settings | Eduka-Settings | Eduka-Settings | Eduka-Settings | Eduka-Settings
app_calculator | Calculator | Kalkulator | Calculadora | Kalkuladora
app_editor | Text editor | Editor teks | Editor de texto | Editór testu
app_writer | LibreOffice Writer | LibreOffice Writer | LibreOffice Writer | LibreOffice Writer
app_terminal | Terminal | Terminal | Terminal | Terminál
app_screenshot | Screenshot | Tangkapan layar | Captura de ecrã | Foto ekrán
app_sound | Sound | Suara | Som | Son
app_network | Wi-Fi & network | Wi-Fi & jaringan | Wi-Fi e rede | Wi-Fi no rede
app_printer | Printers | Printer | Impressoras | Impresora
app_software | Software | Perangkat lunak | Software | Software
app_music | Music | Musik | Música | Múzika
app_video | Video | Video | Vídeo | Vídeu
app_paint | Drawing | Menggambar | Desenho | Dezeñu
opening | Opening {name}… | Membuka {name}… | A abrir {name}… | Loke hela {name}…
open_failed | Could not open {name}. | Tidak bisa membuka {name}. | Não foi possível abrir {name}. | La konsege loke {name}.
app_missing | {name} is not installed on this computer. | {name} belum terpasang di komputer ini. | {name} não está instalado neste computador. | {name} seidauk instala iha komputadór ne'e.
# ---- settings, assistant and about
virtual_settings_note | Lafa Desktop never switches the Virtual Assistant on by itself. | Lafa Desktop tidak pernah menyalakan Virtual Assistant sendiri. | O Lafa Desktop nunca liga o Assistente Virtual sozinho. | Lafa Desktop nunka ativa Asistente Virtuál rasik.
quiet_mode | Quiet mode (no spontaneous messages) | Mode tenang (tanpa pesan spontan) | Modo silencioso (sem mensagens espontâneas) | Modu nonok (la iha mensajen espontániu)
quiet_short | Quiet | Tenang | Silêncio | Nonok
reduce_motion | Reduce motion (no walking or gestures) | Kurangi gerakan (tanpa berjalan atau gerak tubuh) | Reduzir movimento (sem andar nem gestos) | Hamenus movimentu (la la'o no la halo jestu)
entertainment_setting | Entertainment (magician, mind reader, jokes, bathroom scenes) | Hiburan (pesulap, pembaca pikiran, lelucon, adegan kamar mandi) | Entretenimento (mágico, leitor de mentes, piadas, cenas de casa de banho) | Divertimentu (majiku, lee hanoin, anedota, sena hariis)
messages_per_hour | Spontaneous messages per hour (maximum) | Pesan spontan per jam (maksimum) | Mensagens espontâneas por hora (máximo) | Mensajen espontániu kada oras (másimu)
language_sources | Language & sources | Bahasa & sumber | Língua e fontes | Lian no fonte
smooth_scrolling | Smooth scrolling | Gulir halus | Deslocamento suave | Scroll suave
depth_effects | Soft shadows | Bayangan lembut | Sombras suaves | Sombra suave
no_ai_note | Lafa needs no login, AI key or Lafa server. The internet only adds sources (Wikipedia, news, weather, websites). | Lafa tidak perlu login, kunci AI, atau server Lafa. Internet hanya menambah sumber (Wikipedia, berita, cuaca, situs). | O Lafa não precisa de login, chave de IA nem servidor Lafa. A internet só acrescenta fontes (Wikipédia, notícias, tempo, sites). | Lafa la presiza login, xave IA ka servidór Lafa. Internet aumenta fonte de'it (Wikipédia, notísia, tempu, sítiu).
autoread | Read answers aloud (espeak-ng, offline) | Bacakan jawaban (espeak-ng, offline) | Ler as respostas em voz alta (espeak-ng, offline) | Lee resposta ho lian (espeak-ng, offline)
about_text | Lafa is free, open-source software from Timor-Leste for Edukasaun OS. It helps with lessons, knowledge, languages, Timor-Leste, school activities and using Edukasaun OS — without login, without an AI key, without a Lafa server and without internet. Internet adds Wikipedia, news, weather and learning websites. | Lafa adalah perangkat lunak bebas dan open-source dari Timor-Leste untuk Edukasaun OS. Lafa membantu pelajaran, pengetahuan, bahasa, Timor-Leste, kegiatan belajar, dan penggunaan Edukasaun OS — tanpa login, tanpa kunci AI, tanpa server Lafa, dan tanpa internet. Internet menambah Wikipedia, berita, cuaca, dan situs belajar. | O Lafa é software livre e de código aberto de Timor-Leste para o Edukasaun OS. Ajuda com lições, conhecimento, línguas, Timor-Leste, atividades escolares e o uso do Edukasaun OS — sem login, sem chave de IA, sem servidor Lafa e sem internet. A internet acrescenta Wikipédia, notícias, tempo e sites de aprendizagem. | Lafa mak software livre no open-source husi Timor-Leste ba Edukasaun OS. Nia ajuda lisaun, koñesimentu, lian, Timor-Leste, atividade eskola no uza Edukasaun OS — la ho login, la ho xave IA, la ho servidór Lafa no la ho internet. Internet aumenta Wikipédia, notísia, tempu no sítiu aprendizajen.
about_limits | Lafa does not generate answers and cannot answer everything: it searches its own lessons, guides and the material you saved, and says so when it finds nothing. Lessons are written by the LAFA team and are not (yet) reviewed by the Ministry of Education. | Lafa tidak membuat jawaban dan tidak bisa menjawab semua hal: Lafa mencari di pelajaran, panduan, dan materi yang Anda simpan, dan mengatakannya jika tidak menemukan apa pun. Pelajaran ditulis tim LAFA dan belum ditinjau Kementerian Pendidikan. | O Lafa não gera respostas e não responde a tudo: pesquisa nas suas lições, guias e no material guardado, e diz quando não encontra nada. As lições são escritas pela equipa LAFA e ainda não foram revistas pelo Ministério da Educação. | Lafa la halo resposta no la bele hatán buat hotu: nia buka iha ninia lisaun, matadalan no materiál ne'ebé ita rai, no dehan bainhira la hetan buat ida. Lisaun hakerek husi ekipa LAFA no seidauk revee husi Ministériu Edukasaun.
help_text | Commands (all offline unless marked):\n/calc 12*(3+4) — calculator\n/os wifi — Edukasaun OS guide\n/remind 10 drink water — reminder\n/weather Dili — weather (internet)\n/timor — Timor-Leste news (internet)\n/ask topic — Wikipedia extract (internet) | Perintah (semua offline kecuali yang ditandai):\n/calc 12*(3+4) — kalkulator\n/os wifi — panduan Edukasaun OS\n/remind 10 minum air — pengingat\n/weather Dili — cuaca (internet)\n/timor — berita Timor-Leste (internet)\n/ask topik — kutipan Wikipedia (internet) | Comandos (offline, exceto os marcados):\n/calc 12*(3+4) — calculadora\n/os wifi — guia do Edukasaun OS\n/remind 10 beber água — lembrete\n/weather Dili — tempo (internet)\n/timor — notícias de Timor-Leste (internet)\n/ask tema — extrato da Wikipédia (internet) | Komandu (hotu offline exetu ne'ebé marka):\n/calc 12*(3+4) — kalkuladora\n/os wifi — matadalan Edukasaun OS\n/remind 10 hemu bee — fó-hanoin\n/weather Dili — tempu (internet)\n/timor — notísia Timor-Leste (internet)\n/ask tópiku — estratu Wikipédia (internet)
os_intro | Choose a topic, or type a question in the search box, for example “how do I connect Wi-Fi?”. Lafa only opens tools that are installed; it never changes system settings by itself. | Pilih topik, atau ketik pertanyaan di kolom cari, misalnya “bagaimana menyambung Wi-Fi?”. Lafa hanya membuka alat yang terpasang; tidak pernah mengubah pengaturan sistem sendiri. | Escolha um tema, ou escreva uma pergunta na pesquisa, por exemplo “como ligo o Wi-Fi?”. O Lafa só abre ferramentas instaladas; nunca muda definições do sistema sozinho. | Hili tópiku ida, ka hakerek pergunta iha buka, hanesan “oinsá liga Wi-Fi?”. Lafa loke de'it ferramenta ne'ebé instala ona; nunka troka konfigurasaun sistema rasik.
pet_help | Lafa · click for help · drag to move · right click for more | Lafa · klik untuk bantuan · seret untuk memindah · klik kanan untuk menu | Lafa · clique para ajuda · arraste para mover · clique direito para mais | Lafa · klik ba ajuda · dada atu muda · klik-loos ba menu
welcome_desktop | Hi, I'm Lafa! Type a topic, a file name or a question about Edukasaun OS — I'll look it up on this computer. | Halo, saya Lafa! Ketik topik, nama file, atau pertanyaan tentang Edukasaun OS — saya carikan di komputer ini. | Olá, sou o Lafa! Escreva um tema, um nome de ficheiro ou uma pergunta sobre o Edukasaun OS — procuro neste computador. | Olá, ha'u Lafa! Hakerek tópiku, naran ficheiru ka pergunta kona-ba Edukasaun OS — ha'u buka iha komputadór ne'e.
search_examples_short | e.g. photosynthesis · maths homework file · wallpaper | mis. fotosintesis · file tugas matematika · wallpaper | ex. fotossíntese · ficheiro trabalho matemática · fundo | hanesan fotosíntese · ficheiru knaar matemátika · wallpaper
""")
