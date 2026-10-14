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
import re
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

# ------------------------------------------------- more subjects (0.1.3)
# Subjects taught in the classroom and exam hall without a separate teacher.
EXTRA_SUBJECTS = {
    "civics": L("Civics & Citizenship", "Kewarganegaraan", "Educação Cívica", "Edukasaun Sívika"),
    "geography": L("Geography", "Geografi", "Geografia", "Jeografia"),
    "health": L("Health & PE", "Kesehatan & Olahraga", "Saúde e Educação Física", "Saúde no Desportu"),
}
LESSONS += [
    Lesson("civics", L("Our Constitution", "Konstitusi kita", "A nossa Constituição", "Ita-nia Konstituisaun"),
           (L("The Constitution was adopted on 22 March 2002 and came into force on 20 May 2002.", "Konstitusi disahkan 22 Maret 2002 dan berlaku sejak 20 Mei 2002.", "A Constituição foi aprovada a 22 de março de 2002 e entrou em vigor a 20 de maio de 2002.", "Konstituisaun aprova iha 22 Marsu 2002 no tama vigór iha 20 Maiu 2002."),
            L("It protects rights for everyone: life, equality, free speech, faith, education and health.", "Konstitusi melindungi hak semua orang: hidup, kesetaraan, kebebasan berpendapat, beragama, pendidikan dan kesehatan.", "Protege os direitos de todos: vida, igualdade, liberdade de expressão, religião, educação e saúde.", "Proteje direitu ema hotu: moris, igualdade, liberdade espresaun, fiar, edukasaun no saúde."),
            L("Citizens also have duties: respect the law, protect the environment and take part in the community.", "Warga negara juga punya kewajiban: menaati hukum, menjaga lingkungan dan ikut serta dalam masyarakat.", "Os cidadãos também têm deveres: respeitar a lei, proteger o ambiente e participar na comunidade.", "Sidadaun mós iha devér: respeita lei, proteje ambiente no partisipa iha komunidade.")),
           L("Choose one right and explain how it helps students in your school.", "Pilih satu hak dan jelaskan bagaimana hak itu membantu siswa di sekolahmu.", "Escolhe um direito e explica como ajuda os alunos da tua escola.", "Hili direitu ida no esplika oinsá nia ajuda estudante iha ita-nia eskola.")),
    Lesson("civics", L("How the State works", "Cara negara bekerja", "Como funciona o Estado", "Oinsá Estadu servisu"),
           (L("The President is head of State and is elected by the people for five years.", "Presiden adalah kepala negara dan dipilih rakyat untuk lima tahun.", "O Presidente é o chefe de Estado, eleito pelo povo por cinco anos.", "Prezidente mak xefe Estadu, povu mak hili ba tinan lima."),
            L("The National Parliament (65 members) makes laws; the Government, led by the Prime Minister, carries them out.", "Parlemen Nasional (65 anggota) membuat undang-undang; Pemerintah yang dipimpin Perdana Menteri melaksanakannya.", "O Parlamento Nacional (65 deputados) faz as leis; o Governo, liderado pelo Primeiro-Ministro, executa-as.", "Parlamentu Nasionál (membru 65) halo lei; Governu, ho Primeiru-Ministru nu'udar xefe, implementa."),
            L("Courts are independent; sucos elect their own chiefs and councils.", "Pengadilan bersifat independen; suco memilih kepala dan dewannya sendiri.", "Os tribunais são independentes; os sucos elegem os seus chefes e conselhos.", "Tribunál independente; suku hili sira-nia xefe no konsellu rasik.")),
           L("Draw the four organs of sovereignty and connect them with arrows.", "Gambarlah empat organ kedaulatan dan hubungkan dengan panah.", "Desenha os quatro órgãos de soberania e liga-os com setas.", "Dezeña órgaun soberania haat no liga ho seta.")),
    Lesson("geography", L("Reading a map", "Membaca peta", "Ler um mapa", "Lee mapa"),
           (L("Maps have a title, a legend, a scale and a north arrow.", "Peta memiliki judul, legenda, skala dan arah utara.", "Os mapas têm título, legenda, escala e a seta do norte.", "Mapa iha títulu, lejenda, eskala no seta norte."),
            L("Latitude tells how far north or south, longitude how far east or west; Dili is about 8.5° S, 125.6° E.", "Lintang menunjukkan jarak ke utara atau selatan, bujur ke timur atau barat; Dili sekitar 8,5° LS, 125,6° BT.", "A latitude diz a distância a norte ou sul, a longitude a leste ou oeste; Díli fica a cerca de 8,5° S, 125,6° E.", "Latitude hatudu dook ba norte ka sul, longitude ba leste ka oeste; Dili iha 8,5° S, 125,6° L."),
            L("A scale of 1:100,000 means 1 cm on the map is 1 km on the ground.", "Skala 1:100.000 berarti 1 cm di peta sama dengan 1 km di lapangan.", "Uma escala de 1:100 000 quer dizer que 1 cm no mapa é 1 km no terreno.", "Eskala 1:100.000 signifika 1 cm iha mapa hanesan 1 km iha rai.")),
           L("Draw a map of your way from home to school with a legend.", "Gambarlah peta jalan dari rumah ke sekolah lengkap dengan legenda.", "Desenha o mapa do caminho de casa à escola com uma legenda.", "Dezeña mapa dalan husi uma ba eskola ho lejenda.")),
    Lesson("geography", L("Our planet", "Planet kita", "O nosso planeta", "Ita-nia planeta"),
           (L("Earth has seven continents and five oceans; Timor lies between the Indian and Pacific Oceans.", "Bumi memiliki tujuh benua dan lima samudra; Timor terletak di antara Samudra Hindia dan Pasifik.", "A Terra tem sete continentes e cinco oceanos; Timor fica entre o Índico e o Pacífico.", "Rai iha kontinente hitu no oseanu lima; Timor iha entre Oseanu Índiku no Pasífiku."),
            L("The Earth turns once a day (day and night) and goes round the Sun once a year.", "Bumi berputar sekali sehari (siang dan malam) dan mengelilingi Matahari sekali setahun.", "A Terra roda uma vez por dia (dia e noite) e dá a volta ao Sol uma vez por ano.", "Rai fila dala ida kada loron (loron no kalan) no haleu loro-matan dala ida kada tinan."),
            L("Climate change brings stronger storms and higher seas; planting trees and saving water help.", "Perubahan iklim membawa badai lebih kuat dan laut lebih tinggi; menanam pohon dan menghemat air membantu.", "As alterações climáticas trazem tempestades mais fortes e mares mais altos; plantar árvores e poupar água ajuda.", "Mudansa klimátika lori anin-boot no tasi sa'e; kuda ai no poupa bee ajuda."),),
           L("Find Timor-Leste, Indonesia and Australia on a world map.", "Temukan Timor-Leste, Indonesia dan Australia di peta dunia.", "Encontra Timor-Leste, a Indonésia e a Austrália no mapa-múndi.", "Buka Timor-Leste, Indonézia no Austrália iha mapa mundu.")),
    Lesson("health", L("Clean hands, healthy body", "Tangan bersih, badan sehat", "Mãos limpas, corpo saudável", "Liman moos, isin saudável"),
           (L("Wash hands with soap before eating and after the toilet: it stops many diseases.", "Cuci tangan dengan sabun sebelum makan dan setelah ke toilet: ini mencegah banyak penyakit.", "Lava as mãos com sabão antes de comer e depois da casa de banho: evita muitas doenças.", "Fase liman ho sabaun molok han no depois toalete: prevene moras barak."),
            L("Drink clean or boiled water and cover food from flies.", "Minum air bersih atau air matang dan tutup makanan dari lalat.", "Bebe água limpa ou fervida e tapa a comida das moscas.", "Hemu bee moos ka bee nakali no taka ai-han husi lalar."),
            L("Sleep under a mosquito net and remove standing water to prevent malaria and dengue.", "Tidur di bawah kelambu dan buang genangan air untuk mencegah malaria dan demam berdarah.", "Dorme com mosquiteiro e elimina água parada para prevenir a malária e o dengue.", "Toba iha moskiteiru okos no hasai bee ne'ebé para atu prevene malária no dengue.")),
           L("Make a hand-washing poster for your classroom.", "Buat poster cuci tangan untuk kelasmu.", "Faz um cartaz sobre lavar as mãos para a sala.", "Halo póster fase liman ba ita-nia sala.")),
    Lesson("health", L("Food and exercise", "Makanan dan olahraga", "Alimentação e exercício", "Ai-han no ezersísiu"),
           (L("Eat many colours: vegetables, fruit, beans, fish, eggs, rice or maize.", "Makan beragam warna: sayur, buah, kacang, ikan, telur, nasi atau jagung.", "Come muitas cores: legumes, fruta, feijão, peixe, ovos, arroz ou milho.", "Han kór oioin: modo, ai-fuan, fore, ikan, manu-tolun, etu ka batar."),
            L("Move at least 60 minutes a day: football, dance, walking to school.", "Bergerak paling sedikit 60 menit sehari: sepak bola, menari, berjalan ke sekolah.", "Mexe-te pelo menos 60 minutos por dia: futebol, dança, ir a pé para a escola.", "Book-an minutu 60 kada loron: futebol, dansa, la'o ba eskola."),
            L("Sugary drinks harm teeth; water is the best drink.", "Minuman manis merusak gigi; air putih adalah minuman terbaik.", "As bebidas açucaradas estragam os dentes; a água é a melhor bebida.", "Hemu-tasak midar estraga nehan; bee mak hemu di'ak liu.")),
           L("Write a healthy menu for one day using local food.", "Tulis menu sehat satu hari dengan makanan lokal.", "Escreve uma ementa saudável de um dia com comida local.", "Hakerek menu saudável ba loron ida ho ai-han lokál.")),
]
EXTRA_QUIZ = {
"civics": [
    (L("When did the Constitution come into force?", "Kapan Konstitusi mulai berlaku?", "Quando entrou em vigor a Constituição?", "Bainhira mak Konstituisaun tama vigór?"),
     [L("20 May 2002", "20 Mei 2002", "20 de maio de 2002", "20 Maiu 2002"), L("28 November 1975", "28 November 1975", "28 de novembro de 1975", "28 Novembru 1975"), L("30 August 1999", "30 Agustus 1999", "30 de agosto de 1999", "30 Agostu 1999"), L("1 January 2000", "1 Januari 2000", "1 de janeiro de 2000", "1 Janeiru 2000")]),
    (L("How many members does the National Parliament have?", "Berapa anggota Parlemen Nasional?", "Quantos deputados tem o Parlamento Nacional?", "Parlamentu Nasionál iha membru hira?"),
     [L("65", "65", "65", "65"), L("13", "13", "13", "13"), L("100", "100", "100", "100"), L("25", "25", "25", "25")]),
    (L("Who is the head of State?", "Siapa kepala negara?", "Quem é o chefe de Estado?", "Se mak xefe Estadu?"),
     [L("The President of the Republic", "Presiden Republik", "O Presidente da República", "Prezidente Repúblika"), L("The Prime Minister", "Perdana Menteri", "O Primeiro-Ministro", "Primeiru-Ministru"), L("The suco chief", "Kepala suco", "O chefe de suco", "Xefe suku"), L("The judge", "Hakim", "O juiz", "Juís")]),
    (L("For how many years is the President elected?", "Presiden dipilih untuk berapa tahun?", "Por quantos anos é eleito o Presidente?", "Prezidente hili ba tinan hira?"),
     [L("5", "5", "5", "5"), L("2", "2", "2", "2"), L("10", "10", "10", "10"), L("For life", "Seumur hidup", "Para toda a vida", "Ba moris tomak")]),
    (L("What is the national motto?", "Apa semboyan nasional?", "Qual é o lema nacional?", "Lema nasionál mak saida?"),
     [L("Unidade, Acção, Progresso", "Unidade, Acção, Progresso", "Unidade, Acção, Progresso", "Unidade, Acção, Progresso"), L("Ordem e Progresso", "Ordem e Progresso", "Ordem e Progresso", "Ordem e Progresso"), L("Bhinneka Tunggal Ika", "Bhinneka Tunggal Ika", "Bhinneka Tunggal Ika", "Bhinneka Tunggal Ika"), L("Liberty, Equality, Fraternity", "Kebebasan, Kesetaraan, Persaudaraan", "Liberdade, Igualdade, Fraternidade", "Liberdade, Igualdade, Fraternidade")]),
],
"geography": [
    (L("Which island lies about 25 km north of Dili?", "Pulau apa yang terletak sekitar 25 km di utara Dili?", "Que ilha fica a cerca de 25 km a norte de Díli?", "Illa saida mak iha 25 km norte Dili?"),
     [L("Ataúro", "Ataúro", "Ataúro", "Ataúro"), L("Jaco", "Jaco", "Jaco", "Jaco"), L("Bali", "Bali", "Bali", "Bali"), L("Flores", "Flores", "Flores", "Flores")]),
    (L("Which ocean lies south of Timor-Leste?", "Laut apa di selatan Timor-Leste?", "Que mar fica a sul de Timor-Leste?", "Tasi saida iha Timor-Leste nia sul?"),
     [L("Timor Sea", "Laut Timor", "Mar de Timor", "Tasi Timor"), L("Mediterranean Sea", "Laut Tengah", "Mar Mediterrâneo", "Tasi Mediterráneu"), L("Caribbean Sea", "Laut Karibia", "Mar das Caraíbas", "Tasi Karaíba"), L("Arctic Ocean", "Samudra Arktik", "Oceano Ártico", "Oseanu Árctiku")]),
    (L("How many continents are there?", "Ada berapa benua?", "Quantos continentes há?", "Kontinente iha hira?"),
     [L("7", "7", "7", "7"), L("3", "3", "3", "3"), L("5", "5", "5", "5"), L("12", "12", "12", "12")]),
    (L("Where does the exclave Oé-Cusse lie?", "Di mana letak eksklave Oé-Cusse?", "Onde fica o exclave de Oé-Cusse?", "Eksklave Oé-Cusse iha ne'ebé?"),
     [L("On the north coast of West Timor", "Di pantai utara Timor Barat", "Na costa norte de Timor Ocidental", "Iha Timor Oeste nia kosta norte"), L("On Ataúro", "Di Ataúro", "Em Ataúro", "Iha Ataúro"), L("Near Lospalos", "Dekat Lospalos", "Perto de Lospalos", "Besik Lospalos"), L("In Australia", "Di Australia", "Na Austrália", "Iha Austrália")]),
    (L("Which plain in Bobonaro is famous for rice?", "Dataran mana di Bobonaro terkenal dengan padi?", "Que planície de Bobonaro é famosa pelo arroz?", "Rai-tetuk saida iha Bobonaro famozu ho hare?"),
     [L("Maliana", "Maliana", "Maliana", "Maliana"), L("Maubisse", "Maubisse", "Maubisse", "Maubisse"), L("Tutuala", "Tutuala", "Tutuala", "Tutuala"), L("Aileu", "Aileu", "Aileu", "Aileu")]),
],
"health": [
    (L("When should you wash your hands?", "Kapan kamu harus mencuci tangan?", "Quando deves lavar as mãos?", "Bainhira mak ita tenke fase liman?"),
     [L("Before eating and after the toilet", "Sebelum makan dan setelah ke toilet", "Antes de comer e depois da casa de banho", "Molok han no depois toalete"), L("Only on Sundays", "Hanya hari Minggu", "Só ao domingo", "Domingu de'it"), L("Never", "Tidak pernah", "Nunca", "Nunka"), L("Only when they look dirty", "Hanya saat terlihat kotor", "Só quando parecem sujas", "Bainhira haree foer de'it")]),
    (L("Which insect spreads malaria and dengue?", "Serangga apa yang menyebarkan malaria dan demam berdarah?", "Que inseto transmite a malária e o dengue?", "Insetu saida mak hada'et malária no dengue?"),
     [L("Mosquito", "Nyamuk", "Mosquito", "Susuk"), L("Butterfly", "Kupu-kupu", "Borboleta", "Bibi-bulu"), L("Bee", "Lebah", "Abelha", "Bani"), L("Ant", "Semut", "Formiga", "Nehek")]),
    (L("What is the best drink for your body?", "Minuman apa yang terbaik untuk tubuh?", "Qual é a melhor bebida para o corpo?", "Hemu saida mak di'ak liu ba isin?"),
     [L("Clean water", "Air bersih", "Água limpa", "Bee moos"), L("Soft drinks", "Minuman bersoda", "Refrigerantes", "Refrijerante"), L("Coffee only", "Kopi saja", "Só café", "Kafé de'it"), L("Energy drinks", "Minuman energi", "Bebidas energéticas", "Hemu enerjia")]),
    (L("How many minutes should children move each day?", "Berapa menit anak-anak harus bergerak setiap hari?", "Quantos minutos devem as crianças mexer-se por dia?", "Labarik tenke book-an minutu hira kada loron?"),
     [L("At least 60", "Paling sedikit 60", "Pelo menos 60", "Minimu 60"), L("5", "5", "5", "5"), L("None", "Tidak perlu", "Nenhum", "La presiza"), L("Only on holidays", "Hanya saat libur", "Só nas férias", "Feriadu de'it")]),
    (L("Sleeping under what protects you from mosquitoes?", "Tidur di bawah apa yang melindungi dari nyamuk?", "Dormir debaixo de quê protege dos mosquitos?", "Toba iha saida okos mak proteje husi susuk?"),
     [L("A mosquito net", "Kelambu", "Um mosquiteiro", "Moskiteiru"), L("A table", "Meja", "Uma mesa", "Meza"), L("A tree", "Pohon", "Uma árvore", "Ai-hun"), L("An umbrella", "Payung", "Um guarda-chuva", "Sombreiru")]),
],
}

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
    explanation: str = ""      # a sentence from the lesson that explains the answer
    related: str = ""          # title of the related lesson

SUBJECTS = ["math", "science", "languages", "history", "civics", "geography", "health", "ict", "arts"]
VOCAB_Q = L("How do you say “{word}” in {target}?", "Apa bahasa {target} dari “{word}”?", "Como se diz “{word}” em {target}?", "Oinsá atu dehan “{word}” iha {target}?")
LANG_NAMES = {"en": L("English", "Inggris", "inglês", "Inglés"), "id": L("Indonesian", "Indonesia", "indonésio", "Indonézia"),
              "pt": L("Portuguese", "Portugis", "português", "Portugés"), "tet": L("Tetun", "Tetun", "tétum", "Tetun")}

def _math(lang, rng, n):
    out = []; practice = school.MathPractice(rng); seen = set()
    for i in range(n * 5):
        if len(out) >= n: break
        q = practice.new(1 + len(out) % 3); a = practice.answer
        if q in seen: continue
        seen.add(q)
        options = {a}
        while len(options) < 4: options.add(a + rng.choice([-10, -2, -1, 1, 2, 3, 10]))
        options = [str(o) for o in options]; rng.shuffle(options)
        out.append(Question(q, options, str(a), "math", explanation=q.replace("?", str(a))))
    return out

def _vocab(lang, rng, n):
    out = []; seen = set()
    for _ in range(n * 6):
        if len(out) >= n: break
        targets = [l for l in LANGS if l != lang]; target = rng.choice(targets)
        card = rng.choice(VOCAB); s, t = LANGS.index(lang), LANGS.index(target)
        if (card, target) in seen: continue
        seen.add((card, target))
        options = {card[t]}
        while len(options) < 4: options.add(rng.choice(VOCAB)[t])
        options = list(options); rng.shuffle(options)
        out.append(Question(text(VOCAB_Q, lang).format(word=card[s], target=text(LANG_NAMES[target], lang)), options, card[t], "languages",
                            explanation=f"{card[s]} = {card[t]} ({text(LANG_NAMES[target], lang)})"))
    return out

_WORD = re.compile(r"\w{4,}")

def _explain(subject, lang, question, correct):
    """The lesson sentence that best explains an answer, and its lesson title.

    Only a sentence that names the correct answer counts; otherwise nothing is
    shown (Lafa never makes up an explanation)."""
    answer = correct.casefold(); words = set(_WORD.findall(question.casefold()))
    best = (0, "", "")
    for lesson in lessons(subject):
        for point in lesson.points:
            sentence = text(point, lang); low = sentence.casefold()
            if answer not in low: continue
            score = 2 + len(words & set(_WORD.findall(low)))
            if score > best[0]: best = (score, sentence, text(lesson.title, lang))
    return best[1], best[2]

def _bank(subject, lang, rng):
    out = []
    for question, options in school.QUIZ.get(subject, []) + EXTRA_QUIZ.get(subject, []):
        texts = [text(o, lang) for o in options]; correct = texts[0]; rng.shuffle(texts)
        why, related = _explain(subject, lang, text(question, lang), correct)
        out.append(Question(text(question, lang), texts, correct, subject, why, related))
    if subject == "history":
        out += [Question(q, o, c, "history") for q, o, c in timorleste.history_questions(lang, rng)]
        from . import timor_atlas
        out += [Question(q, o, c, "history") for q, o, c in timor_atlas.leader_questions(lang, rng)]
    return out

def unique(items):
    """Questions without repeats (same question text)."""
    seen = set(); out = []
    for q in items:
        if q.text not in seen: seen.add(q.text); out.append(q)
    return out

def questions(subject, lang="en", count=10, rng=None):
    """Up to `count` *different* questions about a subject ("all" mixes every
    subject). When the question bank is smaller, fewer questions are returned:
    a session never repeats a question."""
    rng = rng or random.Random()
    if str(subject).startswith("age:"):
        # Learning for every age: "age:<subject>:<level>" (either part may be empty).
        from . import curriculum
        _, key, level = (subject.split(":") + ["", ""])[:3]
        return unique(curriculum.questions(key or None, level or None, lang, 1000, rng))[:count]
    if subject == "all":
        per = max(1, -(-count // len(SUBJECTS))); pool = []
        for s in SUBJECTS: pool += questions(s, lang, per, rng)
        pool = unique(pool); rng.shuffle(pool); return pool[:count]
    if subject == "math": return _math(lang, rng, count)
    if subject == "languages": return _vocab(lang, rng, count)
    pool = unique(_bank(subject, lang, rng)); rng.shuffle(pool)
    return pool[:count]

def available(subject, lang="en"):
    """How many different questions a subject has (for the "limited bank" note)."""
    if subject in ("math", "languages"): return 10**6
    return len(questions(subject, lang, 10**6, random.Random(0)))

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

def valid_age_subject(subject):
    from . import curriculum
    parts = str(subject).split(":")
    return (len(parts) in (2, 3) and parts[0] == "age" and (not parts[1] or curriculum.subject(parts[1]) is not None)
            and (len(parts) == 2 or not parts[2] or parts[2] in curriculum.LEVEL_KEYS) and any(parts[1:]))

class ExamSession:
    """One quiz, test or exam. Answers are checked on this computer."""
    def __init__(self, kind="quiz", subject="all", lang="en", rng=None, clock=time.monotonic, items=None):
        if kind not in KINDS: raise ValueError("Unknown exam kind.")
        if subject != "all" and subject not in SUBJECTS and not valid_age_subject(subject): raise ValueError("Unknown subject.")
        self.kind, self.subject, self.lang, self.clock = kind, subject, lang, clock
        count, self.limit = KINDS[kind]
        self.items = questions(subject, lang, count, rng) if items is None else unique(items)[:count]
        self.requested = count; self.limited = len(self.items) < count
        if self.limited and self.limit: self.limit = max(60, self.limit * len(self.items) // count)
        self.index = 0; self.answers = []; self.started = clock()
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
    def retry(self, rng=None):
        """A practice session with only the questions answered wrongly."""
        wrong = [q for q, _ in self.mistakes()]
        for q in wrong: (rng or random).shuffle(q.options)
        return ExamSession("quiz", self.subject, self.lang, clock=self.clock, items=wrong)

# ------------------------------------------------------------- report card
class ReportCard:
    """Practice results ("Hasil Latihan"), kept in ~/.local/share/lafa/report.json.

    These are the learner's personal progress, not an official school report.
    Retried mistake sessions are not saved, so averages stay comparable."""
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
        lines = [f"LAFA · {tr(lang, 'report_card')}" + (f" · {name}" if name else ""), datetime.now().strftime("%Y-%m-%d"), tr(lang, "results_personal"), ""]
        for subject, (attempts, best, average) in sorted(self.summary().items()):
            lines.append(f"{subject_name(subject, lang)}: {tr(lang, 'average')} {average}% · {tr(lang, 'best')} {best}% · {attempts}× · {grade(average, lang)}")
        lines += ["", tr(lang, "history_label")]
        for e in reversed(self.entries[-50:]):
            lines.append(f"{e['when']}  {tr(lang, e['kind'])}  {subject_name(e['subject'], lang)}  {e['score']}/{e['total']}")
        return "\n".join(lines) + "\n"

def subject_name(subject, lang):
    if str(subject).startswith("age:"):
        from . import curriculum
        _, key, level = (subject.split(":") + ["", ""])[:3]
        names = [curriculum.subject_name(key, lang) if key else "", curriculum.level_name(level, lang).split(" · ")[0] if level else ""]
        return " · ".join(n for n in names if n)
    if subject == "all":
        from .i18n import tr
        return tr(lang, "all_subjects")
    teacher = school.BY_KEY.get(subject)
    if teacher: return teacher.text("name", lang)
    return text(EXTRA_SUBJECTS[subject], lang) if subject in EXTRA_SUBJECTS else subject
