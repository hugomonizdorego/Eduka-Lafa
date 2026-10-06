"""Timor-Leste for students: history from the first people to today, national
symbols, municipalities, public holidays and "today in history".

All text is offline (en, id, pt, tet) so LAFA can teach without internet.
Dates are the commonly taught ones; each era links to an open source to read
more. Exam questions about Timor-Leste are generated from this data.
"""
from dataclasses import dataclass
from datetime import date
import random

def L(en, id_, pt, tet):
    return {"en": en, "id": id_, "pt": pt, "tet": tet}

def text(value, lang):
    return value.get(lang, value["en"]) if isinstance(value, dict) else value

ERAS = [
    ("ancient", L("First peoples", "Penduduk pertama", "Primeiros povos", "Povu dahuluk"), "https://en.wikipedia.org/wiki/History_of_East_Timor#Prehistory"),
    ("colonial", L("Portuguese Timor", "Timor Portugis", "Timor Português", "Timor Portugés"), "https://en.wikipedia.org/wiki/Portuguese_Timor"),
    ("struggle", L("Occupation and resistance", "Pendudukan dan perlawanan", "Ocupação e resistência", "Okupasaun no rezisténsia"), "https://en.wikipedia.org/wiki/Indonesian_occupation_of_East_Timor"),
    ("nation", L("Independent nation", "Negara merdeka", "Nação independente", "Nasaun independente"), "https://en.wikipedia.org/wiki/East_Timor"),
]

@dataclass(frozen=True)
class Event:
    year: int
    era: str
    title: dict
    text: dict
    month: int = 0
    day: int = 0
    label: str = ""          # shown instead of the year (e.g. "c. 42,000 years ago")
    def when(self, lang="en"):
        if self.label: return text(LABELS[self.label], lang)
        if self.day: return f"{self.day:02d}/{self.month:02d}/{self.year}"
        return str(self.year)

LABELS = {
    "42k": L("c. 42,000 years ago", "± 42.000 tahun lalu", "há c. 42 000 anos", "± tinan 42.000 liubá"),
    "5k": L("c. 3000 BCE", "± 3000 SM", "c. 3000 a.C.", "± 3000 molok Kristu"),
    "13c": L("1200s–1500s", "abad 13–16", "séculos XIII–XVI", "sékulu 13–16"),
    "1859": L("1859–1916", "1859–1916", "1859–1916", "1859–1916"),
    "ww2": L("1942–1945", "1942–1945", "1942–1945", "1942–1945"),
}

HISTORY = [
    Event(-40000, "ancient", L("The first people", "Manusia pertama", "Os primeiros habitantes", "Ema dahuluk"),
          L("People lived in Jerimalai cave near Tutuala (Lautém) and caught fish in the deep sea — some of the oldest deep-sea fishing in the world.",
            "Manusia tinggal di gua Jerimalai dekat Tutuala (Lautém) dan menangkap ikan di laut dalam — salah satu penangkapan ikan laut dalam tertua di dunia.",
            "Pessoas viviam na gruta de Jerimalai, perto de Tutuala (Lautém), e pescavam no alto mar — das pescas em mar profundo mais antigas do mundo.",
            "Ema hela iha fatuk-kuak Jerimalai besik Tutuala (Lautém) no kaer ikan iha tasi kle'an — kaer ikan tasi kle'an ida tuan liu iha mundu."), label="42k"),
    Event(-3000, "ancient", L("Farmers and sailors", "Petani dan pelaut", "Agricultores e navegadores", "Agrikultór no ró-na'in"),
          L("Austronesian peoples arrived by boat, bringing farming, pottery and new languages. Timor's many languages come from these and older peoples.",
            "Bangsa Austronesia datang dengan perahu, membawa pertanian, tembikar dan bahasa baru. Banyak bahasa di Timor berasal dari mereka dan bangsa yang lebih tua.",
            "Povos austronésios chegaram de barco, trazendo agricultura, cerâmica e novas línguas. As muitas línguas de Timor vêm destes e de povos mais antigos.",
            "Povu austronéziu mai ho ró, lori agrikultura, sanan-rai no lian foun. Lian barak iha Timor mai husi sira no povu tuan liu."), label="5k"),
    Event(1250, "ancient", L("The sandalwood island", "Pulau cendana", "A ilha do sândalo", "Illa ai-kameli"),
          L("Chinese, Javanese and Malay merchants sailed to Timor for its fragrant sandalwood. Local kingdoms (reinos) led by liurai ruled the land.",
            "Pedagang Tiongkok, Jawa dan Melayu berlayar ke Timor untuk kayu cendana yang harum. Kerajaan lokal (reinos) dipimpin liurai.",
            "Mercadores chineses, javaneses e malaios navegavam até Timor pelo sândalo perfumado. Reinos locais eram governados por liurais.",
            "Komersiante Xina, Java no Malaiu mai Timor atu sosa ai-kameli ne'ebé morin. Reinu lokál sira ukun husi liurai."), label="13c"),
    Event(1515, "colonial", L("The Portuguese arrive", "Portugis tiba", "Chegada dos portugueses", "Portugés to'o mai"),
          L("Portuguese ships reached Lifau in Oecusse. Catholic missionaries (Dominican friars) came in the following decades.",
            "Kapal Portugis tiba di Lifau, Oecusse. Misionaris Katolik (biarawan Dominikan) datang pada dekade-dekade berikutnya.",
            "Navios portugueses chegaram a Lifau, em Oecusse. Missionários católicos (frades dominicanos) chegaram nas décadas seguintes.",
            "Ró Portugés to'o Lifau iha Oecusse. Misionáriu katóliku (frade dominikanu) mai iha dékada tuir mai."), month=0),
    Event(1702, "colonial", L("First governor in Lifau", "Gubernur pertama di Lifau", "Primeiro governador em Lifau", "Governadór dahuluk iha Lifau"),
          L("Lifau became the seat of the first Portuguese governor of Timor.",
            "Lifau menjadi tempat kedudukan gubernur Portugis pertama di Timor.",
            "Lifau tornou-se a sede do primeiro governador português de Timor.",
            "Lifau sai fatin ba governadór Portugés dahuluk iha Timor.")),
    Event(1769, "colonial", L("Dili becomes the capital", "Dili menjadi ibu kota", "Díli torna-se capital", "Dili sai kapitál"),
          L("Governor António José Teles de Meneses moved the capital from Lifau to Dili on 10 October 1769.",
            "Gubernur António José Teles de Meneses memindahkan ibu kota dari Lifau ke Dili pada 10 Oktober 1769.",
            "O governador António José Teles de Meneses mudou a capital de Lifau para Díli a 10 de outubro de 1769.",
            "Governadór António José Teles de Meneses muda kapitál husi Lifau ba Dili iha 10 Outubru 1769."), month=10, day=10),
    Event(1859, "colonial", L("The island is divided", "Pulau dibagi", "A ilha é dividida", "Illa fahe ba rua"),
          L("Portugal and the Netherlands signed treaties that split Timor: the east (with Oecusse) Portuguese, the west Dutch. The border was settled in 1914–1916.",
            "Portugal dan Belanda menandatangani perjanjian yang membagi Timor: timur (dengan Oecusse) milik Portugis, barat milik Belanda. Perbatasan ditetapkan 1914–1916.",
            "Portugal e os Países Baixos assinaram tratados que dividiram Timor: o leste (com Oecusse) português, o oeste holandês. A fronteira ficou definida em 1914–1916.",
            "Portugál no Olanda asina tratadu ne'ebé fahe Timor: parte leste (ho Oecusse) ba Portugál, parte oeste ba Olanda. Fronteira hatuur iha 1914–1916."), label="1859"),
    Event(1912, "colonial", L("Manufahi revolt", "Pemberontakan Manufahi", "Revolta de Manufahi", "Revolta Manufahi"),
          L("Liurai Dom Boaventura of Manufahi led a great revolt against colonial taxes and forced labour. He is remembered as a hero.",
            "Liurai Dom Boaventura dari Manufahi memimpin pemberontakan besar melawan pajak kolonial dan kerja paksa. Ia dikenang sebagai pahlawan.",
            "O liurai D. Boaventura de Manufahi liderou uma grande revolta contra os impostos coloniais e o trabalho forçado. É lembrado como herói.",
            "Liurai Dom Boaventura husi Manufahi lidera revolta boot hasoru impostu koloniál no servisu forsadu. Ema hanoin nia hanesan eroi.")),
    Event(1942, "colonial", L("World War II", "Perang Dunia II", "Segunda Guerra Mundial", "Funu Mundiál II"),
          L("Japan occupied Timor. Timorese helped Australian soldiers resist; many thousands of Timorese died from fighting and hunger.",
            "Jepang menduduki Timor. Orang Timor membantu tentara Australia melawan; ribuan orang Timor meninggal karena perang dan kelaparan.",
            "O Japão ocupou Timor. Timorenses ajudaram soldados australianos a resistir; muitos milhares de timorenses morreram na guerra e de fome.",
            "Japaun okupa Timor. Timor oan ajuda soldadu Austrália sira rezisti; rihun ba rihun Timor oan mate tanba funu no hamlaha."), label="ww2"),
    Event(1974, "struggle", L("Carnation Revolution", "Revolusi Anyelir", "Revolução dos Cravos", "Revolusaun Kravu"),
          L("On 25 April 1974 a revolution in Portugal opened the way to decolonisation. Timorese political parties were founded.",
            "Pada 25 April 1974 revolusi di Portugal membuka jalan dekolonisasi. Partai-partai politik Timor didirikan.",
            "A 25 de abril de 1974 uma revolução em Portugal abriu caminho à descolonização. Foram fundados partidos políticos timorenses.",
            "Iha 25 Abríl 1974 revolusaun iha Portugál loke dalan ba deskolonizasaun. Partidu polítiku Timor nian harii."), month=4, day=25),
    Event(1975, "struggle", L("Proclamation of independence", "Proklamasi kemerdekaan", "Proclamação da independência", "Proklamasaun independénsia"),
          L("On 28 November 1975 the Democratic Republic of Timor-Leste was proclaimed in Dili. Francisco Xavier do Amaral became the first president.",
            "Pada 28 November 1975 Republik Demokratik Timor-Leste diproklamasikan di Dili. Francisco Xavier do Amaral menjadi presiden pertama.",
            "A 28 de novembro de 1975 foi proclamada em Díli a República Democrática de Timor-Leste. Francisco Xavier do Amaral foi o primeiro presidente.",
            "Iha 28 Novembru 1975 proklama Repúblika Demokrátika Timor-Leste iha Dili. Francisco Xavier do Amaral sai prezidente dahuluk."), month=11, day=28),
    Event(1975, "struggle", L("The invasion", "Invasi", "A invasão", "Invazaun"),
          L("On 7 December 1975 Indonesia invaded. The occupation lasted 24 years; the truth commission (CAVR) counted at least 102,800 conflict-related deaths between 1974 and 1999.",
            "Pada 7 Desember 1975 Indonesia menginvasi. Pendudukan berlangsung 24 tahun; komisi kebenaran (CAVR) mencatat sedikitnya 102.800 kematian terkait konflik antara 1974 dan 1999.",
            "A 7 de dezembro de 1975 a Indonésia invadiu. A ocupação durou 24 anos; a comissão da verdade (CAVR) contou pelo menos 102 800 mortes ligadas ao conflito entre 1974 e 1999.",
            "Iha 7 Dezembru 1975 Indonézia invade. Okupasaun hela tinan 24; komisaun lia-loos (CAVR) sura mate maizumenus 102.800 tanba konflitu entre 1974 no 1999."), month=12, day=7),
    Event(1981, "struggle", L("Xanana leads the resistance", "Xanana memimpin perlawanan", "Xanana lidera a resistência", "Xanana lidera rezisténsia"),
          L("Xanana Gusmão became leader of the resistance and of FALINTIL. The struggle continued in the mountains, in towns (clandestine youth) and abroad (diplomatic front).",
            "Xanana Gusmão menjadi pemimpin perlawanan dan FALINTIL. Perjuangan berlanjut di gunung, di kota (pemuda klandestin) dan di luar negeri (front diplomatik).",
            "Xanana Gusmão tornou-se líder da resistência e das FALINTIL. A luta continuou nas montanhas, nas cidades (jovens clandestinos) e no estrangeiro (frente diplomática).",
            "Xanana Gusmão sai lider rezisténsia no FALINTIL. Luta kontinua iha foho, iha sidade (joventude klandestina) no iha rai li'ur (frente diplomátika).")),
    Event(1991, "struggle", L("Santa Cruz massacre", "Pembantaian Santa Cruz", "Massacre de Santa Cruz", "Masakre Santa Cruz"),
          L("On 12 November 1991 soldiers fired on young people at Santa Cruz cemetery in Dili. Filmed by journalists, it made the world listen. 12 November is National Youth Day.",
            "Pada 12 November 1991 tentara menembaki anak muda di pemakaman Santa Cruz, Dili. Direkam jurnalis, dunia pun mendengar. 12 November adalah Hari Pemuda Nasional.",
            "A 12 de novembro de 1991 soldados dispararam sobre jovens no cemitério de Santa Cruz, em Díli. Filmado por jornalistas, o mundo passou a ouvir. 12 de novembro é o Dia Nacional da Juventude.",
            "Iha 12 Novembru 1991 soldadu tiru joven sira iha rate Santa Cruz, Dili. Jornalista filma, no mundu komesa rona. 12 Novembru mak Loron Nasionál Juventude."), month=11, day=12),
    Event(1996, "struggle", L("Nobel Peace Prize", "Hadiah Nobel Perdamaian", "Prémio Nobel da Paz", "Prémiu Nobel ba Pás"),
          L("Bishop Carlos Filipe Ximenes Belo and José Ramos-Horta received the Nobel Peace Prize for working toward a just and peaceful solution.",
            "Uskup Carlos Filipe Ximenes Belo dan José Ramos-Horta menerima Hadiah Nobel Perdamaian atas upaya penyelesaian yang adil dan damai.",
            "D. Carlos Filipe Ximenes Belo e José Ramos-Horta receberam o Prémio Nobel da Paz por procurarem uma solução justa e pacífica.",
            "Bispu Carlos Filipe Ximenes Belo no José Ramos-Horta simu Prémiu Nobel ba Pás tanba buka solusaun justu no pasífiku.")),
    Event(1999, "struggle", L("The referendum", "Referendum", "O referendo", "Referendu"),
          L("On 30 August 1999, in a United Nations popular consultation, 78.5% voted for independence. Violence followed; the INTERFET peace force arrived in September.",
            "Pada 30 Agustus 1999, dalam jajak pendapat PBB, 78,5% memilih merdeka. Kekerasan menyusul; pasukan perdamaian INTERFET tiba pada September.",
            "A 30 de agosto de 1999, na consulta popular da ONU, 78,5% votaram pela independência. Seguiu-se violência; a força de paz INTERFET chegou em setembro.",
            "Iha 30 Agostu 1999, iha konsulta populár ONU nian, 78,5% vota ba independénsia. Violénsia mosu; forsa pás INTERFET to'o iha Setembru."), month=8, day=30),
    Event(1999, "nation", L("UN transitional administration", "Pemerintahan transisi PBB", "Administração transitória da ONU", "Administrasaun tranzitória ONU"),
          L("On 25 October 1999 the UN created UNTAET to govern and help build the new state with the Timorese people.",
            "Pada 25 Oktober 1999 PBB membentuk UNTAET untuk memerintah dan membantu membangun negara baru bersama rakyat Timor.",
            "A 25 de outubro de 1999 a ONU criou a UNTAET para governar e ajudar a construir o novo Estado com o povo timorense.",
            "Iha 25 Outubru 1999 ONU harii UNTAET atu ukun no ajuda harii estadu foun hamutuk ho povu Timor."), month=10, day=25),
    Event(2002, "nation", L("Restoration of independence", "Pemulihan kemerdekaan", "Restauração da independência", "Restaurasaun independénsia"),
          L("On 20 May 2002 Timor-Leste became independent again, with Xanana Gusmão as President. On 27 September 2002 it joined the United Nations.",
            "Pada 20 Mei 2002 Timor-Leste kembali merdeka, dengan Xanana Gusmão sebagai Presiden. Pada 27 September 2002 bergabung dengan PBB.",
            "A 20 de maio de 2002 Timor-Leste voltou a ser independente, com Xanana Gusmão como Presidente. A 27 de setembro de 2002 entrou na ONU.",
            "Iha 20 Maiu 2002 Timor-Leste sai independente fali, ho Xanana Gusmão hanesan Prezidente. Iha 27 Setembru 2002 tama ONU."), month=5, day=20),
    Event(2012, "nation", L("Peacekeepers leave", "Pasukan perdamaian pulang", "Saída das missões de paz", "Forsa pás sai"),
          L("The last UN mission (UNMIT) ended on 31 December 2012. Timor-Leste keeps its own peace and security.",
            "Misi PBB terakhir (UNMIT) berakhir pada 31 Desember 2012. Timor-Leste menjaga perdamaian dan keamanannya sendiri.",
            "A última missão da ONU (UNMIT) terminou a 31 de dezembro de 2012. Timor-Leste garante a sua própria paz e segurança.",
            "Misaun ONU ikus (UNMIT) remata iha 31 Dezembru 2012. Timor-Leste rasik kaer nia pás no seguransa."), month=12, day=31),
    Event(2019, "nation", L("Sea border with Australia", "Batas laut dengan Australia", "Fronteira marítima com a Austrália", "Fronteira tasi ho Austrália"),
          L("A treaty setting the maritime boundary in the Timor Sea entered into force on 30 August 2019, twenty years after the referendum.",
            "Perjanjian batas laut di Laut Timor mulai berlaku pada 30 Agustus 2019, dua puluh tahun setelah referendum.",
            "O tratado que fixa a fronteira marítima no Mar de Timor entrou em vigor a 30 de agosto de 2019, vinte anos depois do referendo.",
            "Tratadu ne'ebé hatuur fronteira tasi iha Tasi Timor tama iha vigór iha 30 Agostu 2019, tinan ruanulu depois referendu."), month=8, day=30),
    Event(2024, "nation", L("Papal visit", "Kunjungan Paus", "Visita do Papa", "Vizita Papa"),
          L("Pope Francis visited Timor-Leste in September 2024; a huge Mass was held at Tasitolu.",
            "Paus Fransiskus mengunjungi Timor-Leste pada September 2024; Misa besar diadakan di Tasitolu.",
            "O Papa Francisco visitou Timor-Leste em setembro de 2024; uma enorme missa foi celebrada em Tasitolu.",
            "Papa Francisco vizita Timor-Leste iha Setembru 2024; misa boot ida halo iha Tasitolu.")),
    Event(2025, "nation", L("Member of ASEAN", "Anggota ASEAN", "Membro da ASEAN", "Membru ASEAN"),
          L("In October 2025 Timor-Leste became the 11th member of ASEAN, the Association of Southeast Asian Nations.",
            "Pada Oktober 2025 Timor-Leste menjadi anggota ke-11 ASEAN, Perhimpunan Bangsa-Bangsa Asia Tenggara.",
            "Em outubro de 2025 Timor-Leste tornou-se o 11.º membro da ASEAN, a Associação de Nações do Sudeste Asiático.",
            "Iha Outubru 2025 Timor-Leste sai membru ba dala-11 ASEAN, Asosiasaun Nasaun Sudeste Aziátiku.")),
]

# National facts and symbols: (label, value)
FACTS = [
    (L("Official name", "Nama resmi", "Nome oficial", "Naran ofisiál"), L("Democratic Republic of Timor-Leste", "Republik Demokratik Timor-Leste", "República Democrática de Timor-Leste", "Repúblika Demokrátika Timor-Leste")),
    (L("Capital", "Ibu kota", "Capital", "Kapitál"), L("Dili", "Dili", "Díli", "Dili")),
    (L("Official languages", "Bahasa resmi", "Línguas oficiais", "Lian ofisiál"), L("Tetun and Portuguese (Indonesian and English are working languages)", "Tetun dan Portugis (Indonesia dan Inggris bahasa kerja)", "Tétum e português (indonésio e inglês são línguas de trabalho)", "Tetun no Portugés (Indonézia no Inglés lian servisu)")),
    (L("Flag", "Bendera", "Bandeira", "Bandeira"), L("Red, with a yellow and a black triangle and a white star", "Merah, dengan segitiga kuning dan hitam serta bintang putih", "Vermelha, com um triângulo amarelo, um preto e uma estrela branca", "Mean, ho triángulu kinur no metan no fitun mutin")),
    (L("National anthem", "Lagu kebangsaan", "Hino nacional", "Hino nasionál"), L("Pátria", "Pátria", "Pátria", "Pátria")),
    (L("Currency", "Mata uang", "Moeda", "Osan"), L("US dollar, with Timorese centavo coins", "Dolar AS, dengan koin centavo Timor", "Dólar americano, com moedas de centavo timorenses", "Dólar Amerikanu, ho moeda sentavu Timor nian")),
    (L("Highest mountain", "Gunung tertinggi", "Montanha mais alta", "Foho aas liu"), L("Mount Ramelau (Tatamailau), 2,986 m", "Gunung Ramelau (Tatamailau), 2.986 m", "Monte Ramelau (Tatamailau), 2986 m", "Foho Ramelau (Tatamailau), 2.986 m")),
    (L("Restoration of independence", "Pemulihan kemerdekaan", "Restauração da independência", "Restaurasaun independénsia"), L("20 May 2002", "20 Mei 2002", "20 de maio de 2002", "20 Maiu 2002")),
    (L("Legend", "Legenda", "Lenda", "Lenda"), L("Timor was born from a kind crocodile (lafaek) who became the island — that is LAFA's name!", "Timor lahir dari buaya baik (lafaek) yang menjadi pulau — itulah nama LAFA!", "Timor nasceu de um crocodilo bondoso (lafaek) que se tornou a ilha — daí o nome LAFA!", "Timor moris husi lafaek di'ak ida ne'ebé sai illa — ne'e mak naran LAFA!")),
    (L("Neighbours", "Tetangga", "Vizinhos", "Viziñu"), L("Indonesia (land border) and Australia (across the Timor Sea)", "Indonesia (perbatasan darat) dan Australia (di seberang Laut Timor)", "Indonésia (fronteira terrestre) e Austrália (do outro lado do Mar de Timor)", "Indonézia (fronteira rai) no Austrália (iha Tasi Timor nia sorin)")),
]

# Municipalities and the special region, with their main towns.
MUNICIPALITIES = [
    ("Aileu", "Aileu"), ("Ainaro", "Ainaro"), ("Ataúro", "Vila Maumeta"), ("Baucau", "Baucau"), ("Bobonaro", "Maliana"),
    ("Covalima", "Suai"), ("Díli", "Díli"), ("Ermera", "Gleno"), ("Lautém", "Lospalos"), ("Liquiçá", "Liquiçá"),
    ("Manatuto", "Manatuto"), ("Manufahi", "Same"), ("Viqueque", "Viqueque"), ("Oé-Cusse Ambeno (RAEOA)", "Pante Macassar"),
]

# Public holidays with a fixed date (month, day).
HOLIDAYS = [
    ((1, 1), L("New Year's Day", "Tahun Baru", "Dia de Ano Novo", "Loron Tinan Foun")),
    ((3, 3), L("Veterans Day", "Hari Veteran", "Dia dos Veteranos", "Loron Veteranu")),
    ((5, 1), L("Labour Day", "Hari Buruh", "Dia do Trabalhador", "Loron Traballadór")),
    ((5, 20), L("Restoration of Independence Day", "Hari Pemulihan Kemerdekaan", "Dia da Restauração da Independência", "Loron Restaurasaun Independénsia")),
    ((8, 20), L("FALINTIL Day", "Hari FALINTIL", "Dia das FALINTIL", "Loron FALINTIL")),
    ((8, 30), L("Popular Consultation Day", "Hari Jajak Pendapat", "Dia da Consulta Popular", "Loron Konsulta Populár")),
    ((11, 1), L("All Saints' Day", "Hari Raya Semua Orang Kudus", "Dia de Todos os Santos", "Loron Santu Sira Hotu")),
    ((11, 2), L("All Souls' Day", "Hari Arwah", "Dia dos Fiéis Defuntos", "Loron Matebian")),
    ((11, 12), L("National Youth Day", "Hari Pemuda Nasional", "Dia Nacional da Juventude", "Loron Nasionál Juventude")),
    ((11, 28), L("Proclamation of Independence Day", "Hari Proklamasi Kemerdekaan", "Dia da Proclamação da Independência", "Loron Proklamasaun Independénsia")),
    ((12, 7), L("Memorial Day", "Hari Peringatan", "Dia da Memória", "Loron Memória")),
    ((12, 8), L("Immaculate Conception", "Hari Maria Dikandung Tanpa Noda", "Imaculada Conceição", "Imakulada Konseisaun")),
    ((12, 25), L("Christmas Day", "Hari Natal", "Dia de Natal", "Loron Natál")),
    ((12, 31), L("National Heroes Day", "Hari Pahlawan Nasional", "Dia dos Heróis Nacionais", "Loron Eroi Nasionál")),
]

SOURCES = [
    ("History of Timor-Leste · Wikipedia", "https://en.wikipedia.org/wiki/History_of_East_Timor"),
    ("CAVR report Chega!", "https://chega.tl/"),
    ("Arquivo & Museu da Resistência Timorense", "https://amrtimor.org/"),
    ("Government of Timor-Leste", "https://timor-leste.gov.tl/?lang=en"),
    ("Tatoli · Agência Noticiosa de Timor-Leste", "https://tatoli.tl/"),
]

def events(era=None):
    return [e for e in HISTORY if era is None or e.era == era]

def today_in_history(when=None, lang="en"):
    """Events and holidays that happened on this day of the year."""
    when = when or date.today(); out = []
    for e in HISTORY:
        if e.month == when.month and e.day == when.day:
            out.append(f"{e.year} · {text(e.title, lang)}")
    for (month, day), name in HOLIDAYS:
        if (month, day) == (when.month, when.day):
            out.append(text(name, lang))
    return out

def next_holiday(when=None, lang="en"):
    """(days until, date, name) of the next fixed public holiday."""
    when = when or date.today()
    for year in (when.year, when.year + 1):
        for (month, day), name in HOLIDAYS:
            d = date(year, month, day)
            if d >= when: return (d - when).days, d, text(name, lang)
    return None

QUESTION_TEXT = {
    "year": L("In which year: {title}?", "Tahun berapa: {title}?", "Em que ano: {title}?", "Iha tinan saida: {title}?"),
    "capital": L("What is the main town of {name}?", "Apa kota utama {name}?", "Qual é a sede de {name}?", "Sidade prinsipál {name} mak saida?"),
    "holiday": L("Which day is celebrated on {day}?", "Hari apa yang diperingati pada {day}?", "Que dia se celebra a {day}?", "Loron saida mak selebra iha {day}?"),
}

def history_questions(lang="en", rng=None):
    """Multiple-choice questions generated from the Timor-Leste data:
    list of (question, options, correct)."""
    rng = rng or random.Random(); out = []
    dated = [e for e in HISTORY if e.year > 1000 and not e.label]
    years = sorted({e.year for e in dated})
    for e in dated:
        wrong = rng.sample([y for y in years if y != e.year], 3)
        options = [str(e.year)] + [str(y) for y in wrong]; rng.shuffle(options)
        out.append((text(QUESTION_TEXT["year"], lang).format(title=text(e.title, lang)), options, str(e.year)))
    towns = [town for _, town in MUNICIPALITIES]
    for name, town in MUNICIPALITIES:
        if name == town: continue
        options = [town] + rng.sample([t for t in towns if t != town], 3); rng.shuffle(options)
        out.append((text(QUESTION_TEXT["capital"], lang).format(name=name), options, town))
    names = [text(n, lang) for _, n in HOLIDAYS]
    for (month, day), name in HOLIDAYS:
        correct = text(name, lang)
        options = [correct] + rng.sample([n for n in names if n != correct], 3); rng.shuffle(options)
        out.append((text(QUESTION_TEXT["holiday"], lang).format(day=f"{day:02d}/{month:02d}"), options, correct))
    return out
