"""Timor-Leste atlas: everything a student needs about the country, offline.

From the formation of the Earth and of the island of Timor to today: national
symbols, the map and its history, the municipalities, Ataúro and Jaco, natural
resources, economy and trade, population, fertile regions, tourism, every
President and Prime Minister, the system of government and political history.

Text is written in English and Indonesian; titles are in all four of LAFA's
languages. Each topic names an open source; when the computer is online LAFA
also downloads the current Wikipedia introduction in the reader's language
(lafa/livefacts.py) and shows it with its date, so facts stay up to date.
Numbers that change (population, money) are given with their year.
"""
from dataclasses import dataclass, field

def L(en, id_, pt=None, tet=None):
    return {"en": en, "id": id_, "pt": pt or en, "tet": tet or en}

def T(en, id_):
    """Body text: English and Indonesian (Tetun and Portuguese readers get the
    English text offline and the Wikipedia text in their language online)."""
    return {"en": en, "id": id_}

def text(value, lang):
    if not isinstance(value, dict): return value
    return value.get(lang) or value.get("en", "")

@dataclass(frozen=True)
class Topic:
    key: str
    category: str
    title: dict
    summary: dict
    body: dict = field(default_factory=dict)
    facts: tuple = ()          # (label dict, value str or dict)
    wiki: str = ""             # English Wikipedia title for the online refresh
    when: str = ""             # date or period shown on the tile
    size: int = 1              # tile weight (1 small … 3 large) in the atlas map

CATEGORIES = [
    ("earth", L("Earth & island formation", "Pembentukan bumi & pulau", "Formação da Terra e da ilha", "Formasaun rai no illa"), "#7a5c3e"),
    ("history", L("History", "Sejarah", "História", "Istória"), "#b0372f"),
    ("symbols", L("National symbols", "Lambang negara", "Símbolos nacionais", "Símbolu nasionál"), "#d9a021"),
    ("map", L("Map & geography", "Peta & geografi", "Mapa e geografia", "Mapa no jeografia"), "#2f7fb0"),
    ("municipalities", L("Municipalities", "Munisipalitas", "Municípios", "Munisípiu"), "#3a8f5c"),
    ("islands", L("Ataúro, Jaco & Oé-Cusse", "Ataúro, Jaco & Oé-Cusse", "Ataúro, Jaco e Oé-Cusse", "Ataúro, Jaco no Oé-Cusse"), "#1f9aa5"),
    ("nature", L("Natural wealth", "Kekayaan alam", "Riquezas naturais", "Riku-soin naturál"), "#4c8b2b"),
    ("economy", L("Economy, exports & imports", "Ekonomi, ekspor & impor", "Economia, exportações e importações", "Ekonomia, esportasaun no importasaun"), "#8a5fbf"),
    ("people", L("Population & languages", "Penduduk & bahasa", "População e línguas", "Populasaun no lian"), "#d0643a"),
    ("regions", L("Fertile & famous regions", "Wilayah subur & terkenal", "Regiões férteis e famosas", "Rejiaun bokur no famozu"), "#6b9e1f"),
    ("tourism", L("Tourism", "Pariwisata", "Turismo", "Turizmu"), "#e0803a"),
    ("leaders", L("Presidents & Prime Ministers", "Presiden & Perdana Menteri", "Presidentes e Primeiros-Ministros", "Prezidente no Primeiru-Ministru"), "#38598b"),
    ("government", L("System of government", "Sistem pemerintahan", "Sistema de governo", "Sistema governu"), "#2d6f8f"),
    ("politics", L("Political history", "Sejarah politik", "História política", "Istória polítika"), "#9b3d5a"),
]
CATEGORY_KEYS = [key for key, _, _ in CATEGORIES]

TOPICS = [
# ------------------------------------------------------------------ earth
Topic("earth_age", "earth", L("The Earth is born", "Bumi terbentuk", "Nasce a Terra", "Rai moris"),
      T("The Earth formed about 4.54 billion years ago from dust and rock around the young Sun.",
        "Bumi terbentuk sekitar 4,54 miliar tahun lalu dari debu dan batuan di sekitar Matahari muda."),
      T("Over billions of years oceans, continents and life appeared. Continents move slowly on tectonic plates — a few centimetres a year — and this movement later created Timor.",
        "Selama miliaran tahun muncul lautan, benua dan kehidupan. Benua bergerak perlahan di atas lempeng tektonik — beberapa sentimeter per tahun — dan gerakan inilah yang kemudian membentuk Timor."),
      wiki="Age of Earth", when="4.54 billion years ago", size=2),
Topic("earth_gondwana", "earth", L("Rocks from Gondwana", "Batuan dari Gondwana", "Rochas de Gondwana", "Fatuk husi Gondwana"),
      T("Many of Timor's oldest rocks formed 300–200 million years ago on the sea floor at the edge of the ancient continent that became Australia.",
        "Banyak batuan tertua Timor terbentuk 300–200 juta tahun lalu di dasar laut, di tepi benua purba yang kemudian menjadi Australia."),
      T("These limestones and shales are full of fossils: sea lilies (crinoids), shells and ammonites. Timor's Permian fossils are famous among scientists all over the world.",
        "Batu kapur dan serpih ini penuh fosil: lili laut (krinoid), kerang dan amonit. Fosil Perm dari Timor terkenal di kalangan ilmuwan seluruh dunia."),
      wiki="Geology of Timor", when="300–200 million years ago", size=1),
Topic("earth_collision", "earth", L("Timor rises from the sea", "Timor muncul dari laut", "Timor sai do mar", "Timor sa'e husi tasi"),
      T("Timor was pushed up from the sea when the Australian plate collided with the Banda volcanic arc, starting several million years ago.",
        "Timor terangkat dari laut ketika lempeng Australia bertabrakan dengan busur vulkanik Banda, mulai beberapa juta tahun lalu."),
      T("The island is not a volcano: it is a crumpled pile of rock layers scraped from the Australian margin. It is still rising — raised coral reefs along the north coast and on Ataúro and Jaco show the uplift. That is also why Timor has earthquakes.",
        "Pulau ini bukan gunung berapi: ia tumpukan lapisan batuan yang terlipat dari tepi Australia. Pulau ini masih terus naik — terumbu karang terangkat di pantai utara, Ataúro dan Jaco menunjukkannya. Itulah sebabnya Timor sering mengalami gempa."),
      wiki="Banda Arc", when="last few million years", size=3),
Topic("earth_wallacea", "earth", L("Between Asia and Australia (Wallacea)", "Antara Asia dan Australia (Wallacea)", "Entre a Ásia e a Austrália (Wallacea)", "Entre Ázia no Austrália (Wallacea)"),
      T("Timor lies in Wallacea, the island zone between the animals of Asia and of Australia.",
        "Timor terletak di Wallacea, zona pulau antara fauna Asia dan Australia."),
      T("Deep seas kept these islands apart even in the ice ages, so many birds and plants live only here, such as the Timor green pigeon and the Timor sparrow. The saltwater crocodile (lafaek) is sacred in Timorese culture.",
        "Laut dalam memisahkan pulau-pulau ini bahkan di zaman es, sehingga banyak burung dan tumbuhan hanya hidup di sini, seperti punai Timor dan gelatik Timor. Buaya muara (lafaek) dianggap sakral dalam budaya Timor."),
      wiki="Wallacea", size=1),
Topic("earth_climate", "earth", L("Climate and seasons", "Iklim dan musim", "Clima e estações", "Klima no tempu"),
      T("Tropical climate with a wet season (about December to April) and a long dry season; the mountains are cool.",
        "Iklim tropis dengan musim hujan (sekitar Desember sampai April) dan musim kemarau panjang; pegunungan bersuhu sejuk."),
      T("The north coast around Dili is drier; the south coast is wetter and can have a second rainy season. In the highlands such as Maubisse nights can be cold. El Niño years bring drought, La Niña years bring floods and landslides.",
        "Pantai utara di sekitar Dili lebih kering; pantai selatan lebih basah dan bisa mengalami musim hujan kedua. Di dataran tinggi seperti Maubisse malam bisa dingin. Tahun El Niño membawa kekeringan, tahun La Niña membawa banjir dan longsor."),
      wiki="Geography of East Timor", size=1),
# ------------------------------------------------------------------ symbols
Topic("flag", "symbols", L("The flag", "Bendera", "A bandeira", "Bandeira"),
      T("Red with a black triangle on a yellow triangle and a white star; adopted on 20 May 2002.",
        "Merah dengan segitiga hitam di atas segitiga kuning dan bintang putih; diresmikan 20 Mei 2002."),
      T("Red stands for the struggle for liberation, yellow for the traces of colonialism, black for the obscurantism that must be overcome, and the white star for peace and the light that guides the nation. The flag was first raised at the proclamation of 28 November 1975.",
        "Merah melambangkan perjuangan pembebasan, kuning bekas-bekas kolonialisme, hitam kegelapan yang harus diatasi, dan bintang putih perdamaian serta cahaya yang menuntun bangsa. Bendera ini pertama dikibarkan pada proklamasi 28 November 1975."),
      facts=((L("Proportion", "Proporsi", "Proporção", "Proporsaun"), "1 : 2"), (L("Adopted", "Diresmikan", "Adotada", "Adota"), "20/05/2002")),
      wiki="Flag of East Timor", size=3),
Topic("coat_of_arms", "symbols", L("Coat of arms", "Lambang negara", "Brasão de armas", "Simbolu nasaun"),
      T("The national emblem (2007) shows Mount Ramelau, a star, a book, rice and maize, the weapons of the resistance and the motto “Unidade, Acção, Progresso”.",
        "Lambang negara (2007) menampilkan Gunung Ramelau, bintang, buku, padi dan jagung, senjata perlawanan dan semboyan “Unidade, Acção, Progresso”."),
      T("The motto means Unity, Action, Progress. The mountain recalls the highest peak, the book education, rice and maize the food of the people, the weapons the long struggle, and the star the light that guides the country.",
        "Semboyan itu berarti Persatuan, Tindakan, Kemajuan. Gunung mengingatkan puncak tertinggi, buku melambangkan pendidikan, padi dan jagung pangan rakyat, senjata perjuangan panjang, dan bintang cahaya penuntun negeri."),
      facts=((L("Motto", "Semboyan", "Lema", "Lema"), "Unidade, Acção, Progresso"),),
      wiki="Coat of arms of East Timor", size=2),
Topic("anthem", "symbols", L("National anthem “Pátria”", "Lagu kebangsaan “Pátria”", "Hino nacional “Pátria”", "Hino nasionál “Pátria”"),
      T("“Pátria” (Fatherland): words by the poet Francisco Borja da Costa, music by Afonso Redentor Araújo.",
        "“Pátria” (Tanah Air): lirik oleh penyair Francisco Borja da Costa, musik oleh Afonso Redentor Araújo."),
      T("It was first sung at the proclamation in 1975. Borja da Costa was killed on 7 December 1975, the day of the invasion. The anthem is sung in Portuguese.",
        "Lagu ini pertama dinyanyikan pada proklamasi 1975. Borja da Costa terbunuh pada 7 Desember 1975, hari invasi. Lagu kebangsaan dinyanyikan dalam bahasa Portugis."),
      wiki="Pátria (anthem)", size=1),
Topic("languages_official", "symbols", L("Official languages", "Bahasa resmi", "Línguas oficiais", "Lian ofisiál"),
      T("Tetun and Portuguese are official; Indonesian and English are working languages.",
        "Tetun dan Portugis adalah bahasa resmi; Indonesia dan Inggris adalah bahasa kerja."),
      T("The Constitution also protects the national languages spoken in the municipalities, such as Mambai, Makasae, Baikeno, Fataluku, Kemak, Bunak, Galoli, Tokodede and Naueti.",
        "Konstitusi juga melindungi bahasa-bahasa nasional di munisipalitas, seperti Mambai, Makasae, Baikeno, Fataluku, Kemak, Bunak, Galoli, Tokodede dan Naueti."),
      wiki="Languages of East Timor", size=1),
Topic("national_days", "symbols", L("National days", "Hari nasional", "Dias nacionais", "Loron nasionál"),
      T("28 November (proclamation, 1975) and 20 May (restoration, 2002) are the main national days.",
        "28 November (proklamasi, 1975) dan 20 Mei (pemulihan, 2002) adalah hari nasional utama."),
      T("Other days remember the struggle: 20 August (FALINTIL), 30 August (popular consultation), 12 November (youth, Santa Cruz), 7 December (memory of the invasion) and 31 December (national heroes).",
        "Hari lain mengenang perjuangan: 20 Agustus (FALINTIL), 30 Agustus (jajak pendapat), 12 November (pemuda, Santa Cruz), 7 Desember (peringatan invasi) dan 31 Desember (pahlawan nasional)."),
      size=1),
# ------------------------------------------------------------------ map
Topic("map_size", "map", L("Size and position", "Luas dan letak", "Tamanho e posição", "Medida no fatin"),
      T("About 14,950 km² on the eastern half of Timor island, plus Oé-Cusse, Ataúro and Jaco; about 265 km from west to east.",
        "Sekitar 14.950 km² di separuh timur pulau Timor, ditambah Oé-Cusse, Ataúro dan Jaco; sekitar 265 km dari barat ke timur."),
      T("Sources give 14,870–15,010 km² depending on how islands and coast are measured. The country lies around 8°50′ S, 125°55′ E. The coastline is about 700 km long. North are the Ombai and Wetar straits and the Banda Sea; south is the Timor Sea toward Australia.",
        "Sumber menyebut 14.870–15.010 km² tergantung cara mengukur pulau dan pantai. Negara ini terletak sekitar 8°50′ LS, 125°55′ BT. Garis pantainya sekitar 700 km. Di utara ada Selat Ombai dan Wetar serta Laut Banda; di selatan Laut Timor menuju Australia."),
      facts=((L("Area", "Luas", "Área", "Área"), "≈ 14,950 km²"), (L("Highest point", "Titik tertinggi", "Ponto mais alto", "Fatin aas liu"), "Ramelau 2,986 m"),
             (L("Time zone", "Zona waktu", "Fuso horário", "Zona oras"), "UTC+9"), (L("Calling code / internet", "Kode telepon / internet", "Indicativo / internet", "Kódigu telefone / internet"), "+670 · .tl")),
      wiki="Geography of East Timor", size=3),
Topic("map_mountains", "map", L("Mountains and rivers", "Gunung dan sungai", "Montanhas e rios", "Foho no mota"),
      T("A mountain spine runs along the island: Ramelau (Tatamailau, 2,986 m), Matebian, Kablaki and Mundo Perdido.",
        "Punggung pegunungan membentang sepanjang pulau: Ramelau (Tatamailau, 2.986 m), Matebian, Kablaki dan Mundo Perdido."),
      T("Short rivers run north and south and many dry up in the dry season; the Laclo and the Lóis are among the longest. Lake Ira Lalaro in Lautém is the largest lake.",
        "Sungai-sungai pendek mengalir ke utara dan selatan dan banyak yang kering di musim kemarau; Laclo dan Lóis termasuk yang terpanjang. Danau Ira Lalaro di Lautém adalah danau terbesar."),
      wiki="Mount Ramelau", size=2),
Topic("map_history", "map", L("History of the map", "Sejarah peta", "História do mapa", "Istória mapa"),
      T("The border on Timor was drawn by Portugal and the Netherlands between 1859 and 1916; Oé-Cusse stayed Portuguese inside the Dutch west.",
        "Batas di Timor ditarik oleh Portugal dan Belanda antara 1859 dan 1916; Oé-Cusse tetap Portugis di dalam wilayah barat milik Belanda."),
      T("The Treaty of Lisbon (1859) began the division, a convention in 1904 described the line, and an international arbitration in 1914 settled the last disputes; the border was confirmed in 1916. Indonesia's West Timor inherited the Dutch side. After independence, Timor-Leste and Indonesia agreed most of the land border (2005 agreement); the sea border with Australia was fixed by the 2018 treaty (in force 2019); sea borders with Indonesia are still being negotiated.",
        "Perjanjian Lisboa (1859) memulai pembagian, konvensi 1904 menggambarkan garisnya, dan arbitrase internasional 1914 menyelesaikan sengketa terakhir; perbatasan dikukuhkan 1916. Timor Barat Indonesia mewarisi sisi Belanda. Setelah merdeka, Timor-Leste dan Indonesia menyepakati sebagian besar batas darat (perjanjian 2005); batas laut dengan Australia ditetapkan perjanjian 2018 (berlaku 2019); batas laut dengan Indonesia masih dirundingkan."),
      wiki="Indonesia–Timor-Leste border", when="1859–2019", size=2),
Topic("map_borders", "map", L("Neighbours and borders", "Tetangga dan perbatasan", "Vizinhos e fronteiras", "Viziñu no fronteira"),
      T("Land border with Indonesia (West Timor, East Nusa Tenggara province); sea neighbours Indonesia and Australia.",
        "Perbatasan darat dengan Indonesia (Timor Barat, Provinsi Nusa Tenggara Timur); tetangga laut Indonesia dan Australia."),
      T("Main border crossings include Batugade–Motaain (Bobonaro), Salele–Motamasin (Covalima) and the crossings around Oé-Cusse.",
        "Pos lintas batas utama antara lain Batugade–Motaain (Bobonaro), Salele–Motamasin (Covalima) dan pos-pos di sekitar Oé-Cusse."),
      size=1),
# ------------------------------------------------------------------ islands
Topic("atauro", "islands", L("Ataúro", "Ataúro", "Ataúro", "Ataúro"),
      T("Island about 25 km north of Dili, about 140 km²; a municipality since 2022. Its reefs have some of the richest fish life ever measured.",
        "Pulau sekitar 25 km di utara Dili, luas sekitar 140 km²; menjadi munisipalitas sejak 2022. Terumbunya memiliki kehidupan ikan terkaya yang pernah diukur."),
      T("Ataúro is an old, extinct volcanic island of the Banda arc. Main towns are Vila Maumeta and Beloi. In colonial times it was used to exile prisoners. Today it is known for diving, snorkelling, eco-lodges, wooden dolls and fishing communities.",
        "Ataúro adalah pulau vulkanik tua yang sudah mati di busur Banda. Kota utamanya Vila Maumeta dan Beloi. Di masa kolonial pulau ini dipakai sebagai tempat pembuangan tahanan. Kini terkenal dengan selam, snorkeling, penginapan ramah lingkungan, boneka kayu dan komunitas nelayan."),
      wiki="Atauro Island", size=3),
Topic("jaco", "islands", L("Jaco island", "Pulau Jaco", "Ilha de Jaco", "Illa Jaco"),
      T("Small uninhabited island (about 11 km²) at the eastern tip, next to Tutuala; sacred to the Fataluku people.",
        "Pulau kecil tak berpenghuni (sekitar 11 km²) di ujung timur, di dekat Tutuala; dianggap sakral oleh masyarakat Fataluku."),
      T("Jaco is part of Nino Konis Santana National Park, the country's first national park (2007). Visitors may visit by day with local boatmen but may not stay overnight, out of respect for local custom.",
        "Jaco termasuk Taman Nasional Nino Konis Santana, taman nasional pertama (2007). Pengunjung boleh datang siang hari dengan perahu nelayan setempat tetapi tidak boleh menginap, untuk menghormati adat."),
      wiki="Jaco Island", size=2),
Topic("oecusse", "islands", L("Oé-Cusse Ambeno", "Oé-Cusse Ambeno", "Oé-Cusse Ambeno", "Oé-Cusse Ambeno"),
      T("Exclave on the north coast of West Timor (about 815 km²); where the Portuguese first landed (Lifau, 1515). Special Administrative Region (RAEOA) since 2014.",
        "Eksklave di pantai utara Timor Barat (sekitar 815 km²); tempat Portugis pertama mendarat (Lifau, 1515). Wilayah Administratif Khusus (RAEOA) sejak 2014."),
      T("Its people speak Baikeno. The main town is Pante Macassar. The region has its own authority and special economic zone, connected to Dili by ferry and plane.",
        "Penduduknya berbahasa Baikeno. Kota utamanya Pante Macassar. Wilayah ini memiliki otoritas dan zona ekonomi khusus sendiri, terhubung ke Dili dengan kapal feri dan pesawat."),
      wiki="Oecusse", size=2),
# ------------------------------------------------------------------ nature
Topic("oil_gas", "nature", L("Oil and gas", "Minyak dan gas", "Petróleo e gás", "Mina-rai no gás"),
      T("Oil and gas from the Timor Sea (mainly Bayu-Undan) paid for most of the State budget; the field is near its end, and Greater Sunrise is not yet developed.",
        "Minyak dan gas dari Laut Timor (terutama Bayu-Undan) membiayai sebagian besar anggaran negara; ladang itu hampir habis, dan Greater Sunrise belum dikembangkan."),
      T("Income is saved in the Petroleum Fund, created in 2005, which held around 18 billion US dollars in the early 2020s. The Tasi Mane project on the south coast (Suai, Betano, Beaço) plans a petroleum industry. Using the fund wisely and growing other sectors is a key national challenge.",
        "Pendapatan disimpan di Dana Perminyakan yang dibentuk 2005, berisi sekitar 18 miliar dolar AS pada awal 2020-an. Proyek Tasi Mane di pantai selatan (Suai, Betano, Beaço) merencanakan industri perminyakan. Menggunakan dana dengan bijak dan menumbuhkan sektor lain adalah tantangan nasional utama."),
      wiki="Petroleum Fund of Timor-Leste", size=3),
Topic("coffee", "nature", L("Coffee", "Kopi", "Café", "Kafé"),
      T("Arabica coffee from the mountains (Ermera, Aileu, Ainaro, Manufahi, Liquiçá) is the main non-oil export.",
        "Kopi arabika dari pegunungan (Ermera, Aileu, Ainaro, Manufahi, Liquiçá) adalah ekspor non-migas utama."),
      T("The “Timor Hybrid”, a natural cross of arabica and robusta found in Timor in the 20th century, helped breed coffee plants that resist leaf rust in many countries. Most coffee is organic, grown in the shade by family farmers.",
        "“Hibrida Timor”, persilangan alami arabika dan robusta yang ditemukan di Timor pada abad ke-20, membantu menghasilkan tanaman kopi tahan karat daun di banyak negara. Sebagian besar kopi organik, ditanam di bawah naungan oleh petani keluarga."),
      wiki="Coffee production in East Timor", size=2),
Topic("land_sea_wealth", "nature", L("Land and sea wealth", "Kekayaan darat dan laut", "Riquezas da terra e do mar", "Riku-soin rai no tasi"),
      T("Sandalwood, candlenut, vanilla, cloves, marble, manganese, timber, fish and coral reefs.",
        "Cendana, kemiri, vanili, cengkih, marmer, mangan, kayu, ikan dan terumbu karang."),
      T("Sandalwood brought traders to Timor for centuries and is now rare and protected. The seas around Timor are on the edge of the Coral Triangle; whales and dolphins pass along the north coast. Protecting forests, water sources and reefs keeps this wealth for the future.",
        "Cendana mendatangkan pedagang ke Timor selama berabad-abad dan kini langka serta dilindungi. Laut di sekitar Timor berada di tepi Segitiga Karang; paus dan lumba-lumba melintas di pantai utara. Menjaga hutan, sumber air dan terumbu menyimpan kekayaan ini untuk masa depan."),
      wiki="Natural resources of East Timor", size=1),
# ------------------------------------------------------------------ economy
Topic("economy_overview", "economy", L("Economy at a glance", "Ekonomi sekilas", "A economia em resumo", "Ekonomia iha badak"),
      T("Currency: the US dollar (since 2000) with Timorese centavo coins (since 2003). The State budget, financed largely by the Petroleum Fund, drives the economy.",
        "Mata uang: dolar AS (sejak 2000) dengan koin centavo Timor (sejak 2003). Anggaran negara, yang sebagian besar dibiayai Dana Perminyakan, menggerakkan ekonomi."),
      T("Most families work in farming (rice, maize, cassava, coffee, livestock). Important projects include the Tibar Bay port (opened 2022), roads, electricity and the Dili airport. The main goals are new jobs for young people, agriculture, fisheries and tourism.",
        "Sebagian besar keluarga bekerja di pertanian (padi, jagung, singkong, kopi, ternak). Proyek penting antara lain pelabuhan Teluk Tibar (dibuka 2022), jalan, listrik dan bandara Dili. Tujuan utamanya lapangan kerja bagi pemuda, pertanian, perikanan dan pariwisata."),
      wiki="Economy of East Timor", size=3),
Topic("exports", "economy", L("Exports", "Ekspor", "Exportações", "Esportasaun"),
      T("Oil and gas (largest by value), coffee (largest non-oil export), candlenut, vanilla and other farm products.",
        "Minyak dan gas (nilai terbesar), kopi (ekspor non-migas terbesar), kemiri, vanili dan hasil pertanian lain."),
      T("Coffee is sold to the United States, Europe, Australia, Japan and others. As oil income falls, non-oil exports matter more and more.",
        "Kopi dijual ke Amerika Serikat, Eropa, Australia, Jepang dan lainnya. Ketika pendapatan minyak turun, ekspor non-migas makin penting."),
      wiki="Economy of East Timor", size=2),
Topic("imports", "economy", L("Imports", "Impor", "Importações", "Importasaun"),
      T("Fuel, rice and other food, vehicles, machinery, building materials and electronics.",
        "Bahan bakar, beras dan pangan lain, kendaraan, mesin, bahan bangunan dan elektronik."),
      T("The main suppliers include Indonesia, China, Singapore, Australia, Vietnam and Malaysia. Growing more food at home would reduce imports of rice.",
        "Pemasok utama antara lain Indonesia, Tiongkok, Singapura, Australia, Vietnam dan Malaysia. Menanam lebih banyak pangan sendiri akan mengurangi impor beras."),
      size=2),
# ------------------------------------------------------------------ people
Topic("population", "people", L("Population", "Penduduk", "População", "Populasaun"),
      T("About 1.34 million people (2022 census); a young country — most people are under 25.",
        "Sekitar 1,34 juta jiwa (sensus 2022); negara muda — sebagian besar penduduk berusia di bawah 25 tahun."),
      T("Dili is the largest city. Many families live in rural sucos. The next census figures and estimates are refreshed online when LAFA is connected.",
        "Dili adalah kota terbesar. Banyak keluarga tinggal di suco pedesaan. Angka sensus dan perkiraan terbaru diperbarui secara online ketika LAFA terhubung."),
      facts=((L("Population (2022)", "Penduduk (2022)", "População (2022)", "Populasaun (2022)"), "≈ 1.34 million"),),
      wiki="Demographics of East Timor", size=3),
Topic("religion", "people", L("Faith and culture", "Agama dan budaya", "Fé e cultura", "Fiar no kultura"),
      T("About 97% of people are Catholic; Protestants and Muslims are small communities. Traditional culture (uma lulik sacred houses, tara bandu customary law) stays strong.",
        "Sekitar 97% penduduk beragama Katolik; Protestan dan Muslim adalah komunitas kecil. Budaya tradisional (rumah sakral uma lulik, hukum adat tara bandu) tetap kuat."),
      T("The Church supported the people during the occupation. Popes visited Timor in 1989 (John Paul II, Tasitolu) and 2024 (Francis).",
        "Gereja mendampingi rakyat selama pendudukan. Paus mengunjungi Timor pada 1989 (Yohanes Paulus II, Tasitolu) dan 2024 (Fransiskus)."),
      wiki="Religion in East Timor", size=1),
# ------------------------------------------------------------------ regions
Topic("rice_bowls", "regions", L("Rice plains", "Dataran padi", "Planícies de arroz", "Rai-tetuk hare"),
      T("Maliana (Bobonaro), Uatolari and Uatucarbau (Viqueque), Natarbora (Manatuto) and the Suai–Betano south coast grow most of the rice.",
        "Maliana (Bobonaro), Uatolari dan Uatucarbau (Viqueque), Natarbora (Manatuto) dan pantai selatan Suai–Betano menghasilkan sebagian besar padi."),
      T("Irrigation channels and the wet season make these plains fertile. Maize is grown almost everywhere, cassava and sweet potato in the hills.",
        "Saluran irigasi dan musim hujan membuat dataran ini subur. Jagung ditanam hampir di mana-mana, singkong dan ubi jalar di perbukitan."),
      size=2),
Topic("highlands", "regions", L("Coffee and vegetable highlands", "Dataran tinggi kopi dan sayur", "Planaltos do café e dos legumes", "Foho kafé no modo"),
      T("Ermera and Letefoho (coffee), Maubisse and Hatubuilico (vegetables, cool climate), Aileu and Same.",
        "Ermera dan Letefoho (kopi), Maubisse dan Hatubuilico (sayuran, iklim sejuk), Aileu dan Same."),
      T("Cool mountain air and rich soils give coffee, cabbage, carrots, potatoes and fruit for the markets of Dili.",
        "Udara pegunungan yang sejuk dan tanah subur menghasilkan kopi, kubis, wortel, kentang dan buah untuk pasar Dili."),
      size=2),
Topic("east_plateaus", "regions", L("The east: Baucau and Lospalos", "Timur: Baucau dan Lospalos", "O leste: Baucau e Lospalos", "Parte leste: Baucau no Lospalos"),
      T("Limestone plateaus with springs, caves and Lake Ira Lalaro; known for buffalo, rice and ancient rock art.",
        "Dataran tinggi kapur dengan mata air, gua dan Danau Ira Lalaro; terkenal dengan kerbau, padi dan lukisan batu purba."),
      size=1),
# ------------------------------------------------------------------ tourism
Topic("cristo_rei", "tourism", L("Cristo Rei, Dili", "Cristo Rei, Dili", "Cristo Rei, Díli", "Cristo Rei, Dili"),
      T("A 27-metre statue of Christ (1996) on a cape east of Dili, reached by about 500 steps, with beaches on both sides.",
        "Patung Kristus setinggi 27 meter (1996) di tanjung timur Dili, dicapai dengan sekitar 500 anak tangga, dengan pantai di kedua sisi."),
      wiki="Cristo Rei of Dili", size=2),
Topic("ramelau_trek", "tourism", L("Sunrise on Mount Ramelau", "Matahari terbit di Gunung Ramelau", "Nascer do sol no Ramelau", "Loro-sa'e iha Foho Ramelau"),
      T("Pilgrims and hikers start from Hatubuilico at night to watch the sunrise over both seas next to the statue of the Virgin Mary on the top.",
        "Peziarah dan pendaki berangkat dari Hatubuilico di malam hari untuk melihat matahari terbit di atas kedua laut di samping patung Bunda Maria di puncak."),
      size=2),
Topic("dive_atauro", "tourism", L("Diving at Ataúro", "Menyelam di Ataúro", "Mergulho em Ataúro", "Selam iha Ataúro"),
      T("Clear water, coral walls and countless fish; boats leave from Dili.", "Air jernih, dinding karang dan ikan tak terhitung; kapal berangkat dari Dili."), size=1),
Topic("jaco_tutuala", "tourism", L("Jaco and Tutuala", "Jaco dan Tutuala", "Jaco e Tutuala", "Jaco no Tutuala"),
      T("White sand, turquoise sea and the Valu beach at the eastern tip; ancient paintings in nearby caves such as Lene Hara.",
        "Pasir putih, laut biru kehijauan dan pantai Valu di ujung timur; lukisan purba di gua-gua dekatnya seperti Lene Hara."), size=1),
Topic("heritage_places", "tourism", L("Places of memory", "Tempat bersejarah", "Lugares de memória", "Fatin memória"),
      T("The Resistance Museum (Dili), the Chega! exhibition in the former Balide prison, Santa Cruz cemetery, Balibo fort, Maubara fort and the Lifau monument in Oé-Cusse.",
        "Museum Perlawanan (Dili), pameran Chega! di bekas penjara Balide, pemakaman Santa Cruz, benteng Balibo, benteng Maubara dan monumen Lifau di Oé-Cusse."), size=2),
Topic("nature_places", "tourism", L("Beaches and hot springs", "Pantai dan sumber air panas", "Praias e termas", "Tasi-ibun no bee-manas"),
      T("Areia Branca and Dollar Beach (Dili), Com (Lautém), Betano (Manufahi), Marobo hot springs (Bobonaro) and the cool pousada of Maubisse.",
        "Areia Branca dan Dollar Beach (Dili), Com (Lautém), Betano (Manufahi), sumber air panas Marobo (Bobonaro) dan pousada Maubisse yang sejuk."), size=1),
# ------------------------------------------------------------------ government
Topic("system", "government", L("A semi-presidential republic", "Republik semi-presidensial", "República semipresidencial", "Repúblika semi-prezidensiál"),
      T("Democratic republic under the Constitution adopted on 22 March 2002 and in force since 20 May 2002.",
        "Republik demokratis berdasarkan Konstitusi yang disahkan 22 Maret 2002 dan berlaku sejak 20 Mei 2002."),
      T("The organs of sovereignty are the President of the Republic, the National Parliament, the Government and the Courts. Power is shared: the President is head of State, the Prime Minister leads the Government, which answers to Parliament.",
        "Organ kedaulatan adalah Presiden Republik, Parlemen Nasional, Pemerintah dan Pengadilan. Kekuasaan dibagi: Presiden adalah kepala negara, Perdana Menteri memimpin Pemerintah yang bertanggung jawab kepada Parlemen."),
      wiki="Constitution of East Timor", size=3),
Topic("president_role", "government", L("President of the Republic", "Presiden Republik", "Presidente da República", "Prezidente Repúblika"),
      T("Elected by the people for five years (at most two terms in a row); Supreme Commander of the defence force; promulgates or vetoes laws.",
        "Dipilih rakyat untuk lima tahun (paling banyak dua masa jabatan berturut-turut); Panglima Tertinggi angkatan pertahanan; mengundangkan atau memveto undang-undang."), size=2),
Topic("parliament", "government", L("National Parliament", "Parlemen Nasional", "Parlamento Nacional", "Parlamentu Nasionál"),
      T("One chamber of 65 members elected for five years by proportional representation; makes laws and approves the State budget.",
        "Satu kamar dengan 65 anggota dipilih untuk lima tahun secara proporsional; membuat undang-undang dan menyetujui anggaran negara."), size=2),
Topic("government_body", "government", L("Government and Prime Minister", "Pemerintah dan Perdana Menteri", "Governo e Primeiro-Ministro", "Governu no Primeiru-Ministru"),
      T("The Prime Minister is appointed by the President after the elections and leads the Council of Ministers.",
        "Perdana Menteri diangkat Presiden setelah pemilu dan memimpin Dewan Menteri."), size=1),
Topic("courts", "government", L("Courts", "Pengadilan", "Tribunais", "Tribunál"),
      T("District courts, the Court of Appeal (acting as the highest court until the Supreme Court of Justice is set up) and the Chamber of Auditors.",
        "Pengadilan distrik, Pengadilan Banding (bertindak sebagai pengadilan tertinggi sampai Mahkamah Agung dibentuk) dan Kamar Auditor."), size=1),
Topic("local_power", "government", L("Municipalities, sucos and aldeias", "Munisipalitas, suco dan aldeia", "Municípios, sucos e aldeias", "Munisípiu, suku no aldeia"),
      T("14 municipalities (including Ataúro and the special region of Oé-Cusse), administrative posts, more than 440 sucos and about 2,200 aldeias; suco chiefs are elected by the community.",
        "14 munisipalitas (termasuk Ataúro dan wilayah khusus Oé-Cusse), pos administratif, lebih dari 440 suco dan sekitar 2.200 aldeia; kepala suco dipilih masyarakat."), size=1),
Topic("security", "government", L("Defence and police", "Pertahanan dan polisi", "Defesa e polícia", "Defeza no polísia"),
      T("F-FDTL (FALINTIL–Forças de Defesa de Timor-Leste) defends the country; the PNTL (national police) keeps public order.",
        "F-FDTL (FALINTIL–Angkatan Pertahanan Timor-Leste) mempertahankan negara; PNTL (polisi nasional) menjaga ketertiban umum."), size=1),
Topic("international", "government", L("Timor-Leste in the world", "Timor-Leste di dunia", "Timor-Leste no mundo", "Timor-Leste iha mundu"),
      T("Member of the United Nations (2002), CPLP (Portuguese-speaking countries, 2002), founder of the g7+ group of fragile states (2010) and member of ASEAN (2025).",
        "Anggota PBB (2002), CPLP (negara berbahasa Portugis, 2002), pendiri kelompok g7+ negara rapuh (2010) dan anggota ASEAN (2025)."),
      wiki="Foreign relations of East Timor", size=2),
# ------------------------------------------------------------------ politics
Topic("parties_1974", "politics", L("The first parties (1974–1975)", "Partai pertama (1974–1975)", "Os primeiros partidos (1974–1975)", "Partidu dahuluk (1974–1975)"),
      T("After 25 April 1974, UDT, ASDT (which became FRETILIN), APODETI, KOTA and the Labour Party were founded.",
        "Setelah 25 April 1974, berdiri UDT, ASDT (kemudian FRETILIN), APODETI, KOTA dan Partai Buruh."),
      T("In August 1975 a UDT coup led to a short civil war won by FRETILIN, which proclaimed independence on 28 November 1975, nine days before the Indonesian invasion.",
        "Pada Agustus 1975 kudeta UDT memicu perang saudara singkat yang dimenangkan FRETILIN, yang memproklamasikan kemerdekaan 28 November 1975, sembilan hari sebelum invasi Indonesia."),
      when="1974–1975", size=2),
Topic("resistance", "politics", L("Resistance fronts", "Front-front perlawanan", "Frentes da resistência", "Frente rezisténsia"),
      T("Armed front (FALINTIL), clandestine front (youth and students in towns) and diplomatic front abroad, united in the CNRM (1988) and CNRT (1998).",
        "Front bersenjata (FALINTIL), front klandestin (pemuda dan pelajar di kota) dan front diplomatik di luar negeri, bersatu dalam CNRM (1988) dan CNRT (1998)."),
      T("Leaders included Nicolau Lobato, Xanana Gusmão, Konis Santana and Taur Matan Ruak; abroad, José Ramos-Horta and Mari Alkatiri; at home, the Church and many women's and student groups.",
        "Tokohnya antara lain Nicolau Lobato, Xanana Gusmão, Konis Santana dan Taur Matan Ruak; di luar negeri José Ramos-Horta dan Mari Alkatiri; di dalam negeri Gereja serta banyak kelompok perempuan dan pelajar."),
      when="1975–1999", size=2),
Topic("elections", "politics", L("Elections since 2001", "Pemilu sejak 2001", "Eleições desde 2001", "Eleisaun desde 2001"),
      T("Constituent Assembly 2001; presidential elections 2002, 2007, 2012, 2017, 2022; parliamentary elections 2007, 2012, 2017, 2018 (early) and 2023.",
        "Majelis Konstituante 2001; pemilu presiden 2002, 2007, 2012, 2017, 2022; pemilu parlemen 2007, 2012, 2017, 2018 (dipercepat) dan 2023."),
      T("FRETILIN won the 2001 Constituent Assembly. The 2006 crisis displaced around 150,000 people. CNRT (founded by Xanana Gusmão in 2007) led governments from 2007 and again from 2023. Other important parties include PLP, KHUNTO and PD. Results of newer elections are refreshed online.",
        "FRETILIN memenangkan Majelis Konstituante 2001. Krisis 2006 membuat sekitar 150.000 orang mengungsi. CNRT (didirikan Xanana Gusmão pada 2007) memimpin pemerintahan sejak 2007 dan lagi sejak 2023. Partai penting lain antara lain PLP, KHUNTO dan PD. Hasil pemilu terbaru diperbarui secara online."),
      wiki="Elections in East Timor", size=3),
Topic("crises", "politics", L("Crises and peace", "Krisis dan perdamaian", "Crises e paz", "Krize no pás"),
      T("The country overcame the 1999 destruction, the 2006 crisis and the 11 February 2008 attacks on the President and Prime Minister; the last UN mission left in 2012.",
        "Negara ini mengatasi kehancuran 1999, krisis 2006 dan serangan 11 Februari 2008 terhadap Presiden dan Perdana Menteri; misi PBB terakhir pergi pada 2012."),
      size=1),
]

# Presidents and Prime Ministers: (name, from, to, note)
PRESIDENTS = [
    ("Francisco Xavier do Amaral", "28/11/1975", "1977", L("First President, proclaimed in 1975 (FRETILIN)", "Presiden pertama, proklamasi 1975 (FRETILIN)")),
    ("Nicolau Lobato", "1977", "31/12/1978", L("Led the resistance government; killed in combat, National Hero", "Memimpin pemerintahan perlawanan; gugur dalam pertempuran, Pahlawan Nasional")),
    ("Xanana Gusmão", "20/05/2002", "20/05/2007", L("First President after the restoration of independence", "Presiden pertama setelah pemulihan kemerdekaan")),
    ("José Ramos-Horta", "20/05/2007", "20/05/2012", L("Nobel Peace Prize 1996; wounded in the attack of 11/02/2008", "Nobel Perdamaian 1996; terluka dalam serangan 11/02/2008")),
    ("Taur Matan Ruak", "20/05/2012", "20/05/2017", L("Former FALINTIL commander", "Mantan komandan FALINTIL")),
    ("Francisco Guterres “Lú-Olo”", "20/05/2017", "20/05/2022", L("FRETILIN president and resistance veteran", "Presiden FRETILIN dan veteran perlawanan")),
    ("José Ramos-Horta", "20/05/2022", "—", L("Second term; serving in 2026 (term until 2027)", "Masa jabatan kedua; menjabat pada 2026 (sampai 2027)")),
]
ACTING_PRESIDENTS = L("Acting Presidents in 2008: Vicente Guterres and Fernando “La Sama” de Araújo, while President Ramos-Horta recovered.",
                      "Pejabat Presiden pada 2008: Vicente Guterres dan Fernando “La Sama” de Araújo, selama Presiden Ramos-Horta dirawat.")
PRIME_MINISTERS = [
    ("Nicolau Lobato", "1975", "1977", L("Prime Minister of the 1975 Democratic Republic", "Perdana Menteri Republik Demokratik 1975")),
    ("Mari Alkatiri", "20/05/2002", "26/06/2006", L("First constitutional Prime Minister (FRETILIN)", "Perdana Menteri konstitusional pertama (FRETILIN)")),
    ("José Ramos-Horta", "2006", "2007", L("Prime Minister after the 2006 crisis", "Perdana Menteri setelah krisis 2006")),
    ("Estanislau da Silva", "05/2007", "08/2007", L("Interim Prime Minister", "Perdana Menteri sementara")),
    ("Xanana Gusmão", "08/08/2007", "16/02/2015", L("Two governments (AMP, then CNRT-led coalition)", "Dua pemerintahan (AMP, lalu koalisi pimpinan CNRT)")),
    ("Rui Maria de Araújo", "16/02/2015", "15/09/2017", L("Government of national unity", "Pemerintahan persatuan nasional")),
    ("Mari Alkatiri", "15/09/2017", "22/06/2018", L("Minority government; early elections in 2018", "Pemerintahan minoritas; pemilu dipercepat 2018")),
    ("Taur Matan Ruak", "22/06/2018", "01/07/2023", L("AMP and later coalition governments", "Pemerintahan AMP dan koalisi berikutnya")),
    ("Xanana Gusmão", "01/07/2023", "—", L("CNRT–PD government; serving in 2026", "Pemerintahan CNRT–PD; menjabat pada 2026")),
]
TRANSITION = L("1999–2002: the UN Transitional Administration (UNTAET) governed with Timorese leaders; Sérgio Vieira de Mello was its head. Mari Alkatiri was Chief Minister of the transitional government (2001–2002).",
               "1999–2002: Pemerintahan Transisi PBB (UNTAET) memerintah bersama para pemimpin Timor; Sérgio Vieira de Mello memimpinnya. Mari Alkatiri menjadi Menteri Utama pemerintahan transisi (2001–2002).")

# Municipalities: (name, main town, history/notes en, id)
MUNICIPALITY_NOTES = [
    ("Aileu", "Aileu", T("Mountain municipality south of Dili; FRETILIN's base in 1975–1976; coffee and vegetables.", "Munisipalitas pegunungan di selatan Dili; basis FRETILIN pada 1975–1976; kopi dan sayuran.")),
    ("Ainaro", "Ainaro", T("Home of Mount Ramelau, Hatubuilico and the cool town of Maubisse; vegetables and coffee.", "Rumah Gunung Ramelau, Hatubuilico dan kota sejuk Maubisse; sayuran dan kopi.")),
    ("Ataúro", "Vila Maumeta", T("Island municipality since 2022 (before, part of Dili); diving, fishing and eco-tourism.", "Munisipalitas pulau sejak 2022 (sebelumnya bagian Dili); selam, perikanan dan ekowisata.")),
    ("Baucau", "Baucau", T("Second city; old Portuguese town with a famous market and springs; the long airstrip; Japanese wartime tunnels at Venilale.", "Kota kedua; kota Portugis tua dengan pasar dan mata air terkenal; landasan pacu panjang; terowongan Jepang masa perang di Venilale.")),
    ("Bobonaro", "Maliana", T("Rice plain of Maliana, Marobo hot springs, Balibo fort and the Batugade border crossing; the Balibo Five journalists were killed here in 1975.", "Dataran padi Maliana, air panas Marobo, benteng Balibo dan pos perbatasan Batugade; lima jurnalis Balibo terbunuh di sini pada 1975.")),
    ("Covalima", "Suai", T("South coast; Suai church massacre of 6 September 1999; Suai supply base of the Tasi Mane project.", "Pantai selatan; pembantaian gereja Suai 6 September 1999; pangkalan pasokan Suai proyek Tasi Mane.")),
    ("Díli", "Díli", T("Capital since 1769; seat of State; Cristo Rei, Santa Cruz, the Government Palace and the Tibar port nearby.", "Ibu kota sejak 1769; pusat negara; Cristo Rei, Santa Cruz, Istana Pemerintah dan pelabuhan Tibar di dekatnya.")),
    ("Ermera", "Gleno", T("The coffee heartland (Letefoho, Railaco, Hatulia); most of the export coffee grows here.", "Jantung kopi (Letefoho, Railaco, Hatulia); sebagian besar kopi ekspor tumbuh di sini.")),
    ("Lautém", "Lospalos", T("Eastern tip; Fataluku language; Jaco, Tutuala, Lake Ira Lalaro, cave paintings and Nino Konis Santana National Park.", "Ujung timur; bahasa Fataluku; Jaco, Tutuala, Danau Ira Lalaro, lukisan gua dan Taman Nasional Nino Konis Santana.")),
    ("Liquiçá", "Liquiçá", T("Coast west of Dili; the 18th-century Maubara fort; Liquiçá church massacre of April 1999.", "Pantai barat Dili; benteng Maubara abad ke-18; pembantaian gereja Liquiçá April 1999.")),
    ("Manatuto", "Manatuto", T("North coast and the Natarbora plain; Laclubar mountains; birthplace of Xanana Gusmão (Laleia).", "Pantai utara dan dataran Natarbora; pegunungan Laclubar; tempat kelahiran Xanana Gusmão (Laleia).")),
    ("Manufahi", "Same", T("Land of Dom Boaventura's 1912 revolt; coffee hills of Same and Betano beach.", "Tanah pemberontakan Dom Boaventura 1912; bukit kopi Same dan pantai Betano.")),
    ("Viqueque", "Viqueque", T("South coast rice fields (Uatolari, Uatucarbau); the 1959 Viqueque revolt against colonial rule.", "Sawah pantai selatan (Uatolari, Uatucarbau); pemberontakan Viqueque 1959 melawan penjajahan.")),
    ("Oé-Cusse Ambeno (RAEOA)", "Pante Macassar", T("Exclave where the Portuguese landed at Lifau in 1515; special administrative region and economic zone since 2014.", "Eksklave tempat Portugis mendarat di Lifau 1515; wilayah administratif dan zona ekonomi khusus sejak 2014.")),
]

def topics(category=None):
    return [t for t in TOPICS if category is None or t.category == category]

def find(key):
    return next((t for t in TOPICS if t.key == key), None)

def leader_questions(lang="en", rng=None):
    """Exam questions about Presidents and Prime Ministers since 2002."""
    import random
    rng = rng or random.Random(); out = []
    later = [p for p in PRESIDENTS if p[1].startswith("20/05/")]
    names = sorted({p[0] for p in PRESIDENTS + PRIME_MINISTERS})
    q = {"en": "Who was President of Timor-Leste from {a} to {b}?", "id": "Siapa Presiden Timor-Leste dari {a} sampai {b}?",
         "pt": "Quem foi Presidente de Timor-Leste de {a} a {b}?", "tet": "Se mak Prezidente Timor-Leste husi {a} to'o {b}?"}
    for name, a, b, _ in later:
        if b == "—": continue
        options = [name] + rng.sample([n for n in names if n != name], 3); rng.shuffle(options)
        out.append((q.get(lang, q["en"]).format(a=a[-4:], b=b[-4:]), options, name))
    q = {"en": "Who became Prime Minister on {a}?", "id": "Siapa yang menjadi Perdana Menteri pada {a}?",
         "pt": "Quem se tornou Primeiro-Ministro em {a}?", "tet": "Se mak sai Primeiru-Ministru iha {a}?"}
    for name, a, _, _ in PRIME_MINISTERS[1:]:
        if a.count("/") != 2: continue
        options = [name] + rng.sample([n for n in names if n != name], 3); rng.shuffle(options)
        out.append((q.get(lang, q["en"]).format(a=a), options, name))
    return out
