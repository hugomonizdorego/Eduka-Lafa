"""Sub-sections of the encyclopedia catalog: inside each category the articles
are grouped by theme (the "sub-menus" of a category page). Each entry is
(title in tet/pt/en/id, article slugs after "tl.<category>."). Articles that
are not listed are shown at the end under "Other"; categories without an
entry are shown as one list."""
from ... import kb

L = kb.L

SUBSECTIONS = {
    "history": [
        (L("Ema dahuluk no povu sira", "Primeiros povos", "The first peoples", "Manusia pertama dan bangsa-bangsa"), ["overview", "first_peoples", "austronesian_papuan"]),
        (L("Reinu no ai-kameli", "Reinos e sândalo", "Kingdoms and sandalwood", "Kerajaan dan cendana"), ["kingdoms", "sandalwood_trade"]),
        (L("1974–2002: dalan ba ukun rasik", "1974–2002: o caminho para a independência", "1974–2002: the road to independence", "1974–2002: jalan menuju kemerdekaan"),
         ["carnation_parties_1974", "civil_war_1975", "proclamation_1975", "cnrt_1998", "nobel_1996", "referendum_1999", "interfet", "untaet", "restoration_2002"]),
        (L("Estadu foun: 2002 to'o ohin", "O novo Estado: de 2002 até hoje", "The new State: 2002 to today", "Negara baru: 2002 hingga kini"),
         ["state_building", "un_missions", "maritime_boundary", "decade_2012_2022", "recent_2023_2026", "archives_museums"]),
    ],
    "prehistory": [
        (L("Fósil no animál antigu", "Fósseis e animais antigos", "Fossils and ancient animals", "Fosil dan hewan purba"), ["fossils_seas", "pterosaur_lesululi", "ice_age_animals"]),
        (L("Ema dahuluk", "Os primeiros povos", "The first people", "Manusia pertama"), ["overview", "sea_crossing", "cave_sites", "rock_art"]),
        (L("Agrikultór no negósiu dahuluk", "Primeiros agricultores e comércio", "First farmers and trade", "Petani dan perdagangan pertama"), ["first_farmers", "early_records"]),
    ],
    "colonial": [
        (L("Tempu Portugál", "O tempo português", "The Portuguese period", "Masa Portugis"),
         ["portuguese_arrival", "topasses", "lifau_to_dili", "dutch_partition", "colonial_rule", "revolts_manufahi", "ww2", "postwar"]),
        (L("Okupasaun Indonézia", "A ocupação indonésia", "The Indonesian occupation", "Pendudukan Indonesia"), ["indonesian_invasion", "indonesian_occupation"]),
    ],
    "conflicts": [
        (L("Rezisténsia no violénsia (1975–1999)", "Resistência e violência (1975–1999)", "Resistance and violence (1975–1999)", "Perlawanan dan kekerasan (1975–1999)"),
         ["overview", "resistance_fronts", "famine_1977_1979", "kraras_1983", "santa_cruz_1991", "violence_1999"]),
        (L("Krize depois ukun rasik", "Crises depois da independência", "Crises after independence", "Krisis setelah kemerdekaan"), ["crisis_2006", "attacks_2008"]),
        (L("Lia-loos no rekonsiliasaun", "Verdade e reconciliação", "Truth and reconciliation", "Kebenaran dan rekonsiliasi"), ["reconciliation"]),
    ],
    "politics": [
        (L("Konstituisaun no sistema", "Constituição e sistema", "Constitution and system", "Konstitusi dan sistem"), ["constitution", "system", "rights_duties"]),
        (L("Órgaun soberania", "Órgãos de soberania", "Organs of sovereignty", "Lembaga kedaulatan"), ["president_office", "parliament", "government", "courts", "council_state"]),
        (L("Eleisaun no partidu", "Eleições e partidos", "Elections and parties", "Pemilu dan partai"), ["elections", "parties"]),
        (L("Defeza no ukun lokál", "Defesa e poder local", "Defence and local power", "Pertahanan dan pemerintahan lokal"), ["defence_security", "local_government"]),
    ],
    "institutions": [
        (L("Vizaun jerál", "Visão geral", "Overview", "Gambaran umum"), ["overview"]),
        (L("Órgaun soberania", "Órgãos de soberania", "Organs of sovereignty", "Lembaga kedaulatan"),
         ["tl.politics.president_office", "tl.politics.parliament", "tl.politics.government", "tl.politics.courts", "tl.politics.council_state"]),
        (L("Ministériu sira", "Ministérios", "Ministries", "Kementerian"),
         ["ministries", "education_ministry", "higher_education", "justice", "finance", "state_administration", "youth_sport_culture",
          "environment_tourism", "transport_communications"]),
        (L("Justisa", "Justiça", "Justice", "Peradilan"), ["court_of_appeal", "public_prosecution", "public_defender"]),
        (L("Defeza no seguransa", "Defesa e segurança", "Defence and security", "Pertahanan dan keamanan"), ["ffdtl", "pntl", "security_agencies"]),
        (L("Órgaun independente no ajénsia", "Órgãos independentes e agências", "Independent bodies and agencies", "Lembaga independen dan badan"),
         ["independent_bodies", "pdhj", "civil_service", "tic_timor"]),
    ],
    "leaders": [
        (L("Lista no governu sira", "Listas e governos", "Lists and governments", "Daftar dan pemerintahan"), ["presidents", "prime_ministers", "governments", "parliament_presidents"]),
        (L("Biografia", "Biografias", "Biographies", "Biografi"),
         ["xavier_do_amaral", "nicolau_lobato", "xanana_gusmao", "ramos_horta", "mari_alkatiri", "taur_matan_ruak", "lu_olo", "rui_araujo"]),
        (L("Asuwa'in nasionál", "Heróis nacionais", "National heroes", "Pahlawan nasional"), ["national_heroes"]),
    ],
    "symbols": [
        (L("Símbolu ofisiál", "Símbolos oficiais", "Official symbols", "Simbol resmi"), ["flag", "emblem", "anthem", "motto"]),
        (L("Identidade nasionál", "Identidade nacional", "National identity", "Identitas nasional"), ["name", "languages_official", "capital_dili", "currency"]),
    ],
    "land": [
        (L("Rai no foho", "Terra e montanhas", "Land and mountains", "Tanah dan gunung"), ["overview", "island_formation", "geology", "mountains"]),
        (L("Bee no tasi", "Águas e mar", "Water and sea", "Air dan laut"), ["rivers_lakes", "seas_coasts"]),
        (L("Klima no perigu", "Clima e riscos", "Climate and hazards", "Iklim dan bencana"), ["climate", "hazards"]),
    ],
    "nature": [
        (L("Biodiversidade no konservasaun", "Biodiversidade e conservação", "Biodiversity and conservation", "Keanekaragaman hayati dan konservasi"),
         ["biodiversity", "endangered", "protected_areas", "environment", "forests_plants"]),
        (L("Animál iha rai", "Animais em terra", "Land animals", "Hewan darat"), ["animals", "mammals", "birds", "reptiles_amphibians", "crocodile", "insects", "domestic_animals"]),
        (L("Moris iha tasi", "Vida marinha", "Sea life", "Kehidupan laut"), ["marine", "whales_dolphins"]),
    ],
    "culture": [
        (L("Lisan no moris komunidade", "Tradição e vida comunitária", "Tradition and community life", "Adat dan kehidupan masyarakat"),
         ["overview", "lisan", "uma_lulik", "marriage_barlake", "ethnic_groups", "catholic_traditions"]),
        (L("Arte, tais no múzika", "Arte, tais e música", "Art, tais and music", "Seni, tais dan musik"),
         ["tais", "dress_adornment", "crafts", "architecture", "dances", "music", "legends", "arts_literature"]),
        (L("Hahán, lian no jogu", "Comida, língua e jogos", "Food, language and games", "Makanan, bahasa dan permainan"), ["food", "tetun", "sports_games"]),
    ],
    "sports": [
        (L("Futeból", "Futebol", "Football", "Sepak bola"), ["football", "football_league"]),
        (L("Kompetisaun internasionál", "Competições internacionais", "International competitions", "Kompetisi internasional"), ["olympics", "winter_paralympics", "sea_games"]),
        (L("Modalidade sira", "Modalidades", "Sports and disciplines", "Cabang olahraga"), ["martial_arts", "athletics_marathon", "cycling", "team_sports", "water_sports"]),
        (L("Tradisaun, atleta no estádiu", "Tradição, atletas e estádios", "Tradition, athletes and venues", "Tradisi, atlet dan stadion"),
         ["overview", "traditional_games", "athletes", "institutions_venues"]),
    ],
    "society": [
        (L("Ema no lian", "Pessoas e línguas", "People and languages", "Penduduk dan bahasa"), ["population", "languages", "religion", "cities"]),
        (L("Edukasaun, saúde no média", "Educação, saúde e media", "Education, health and media", "Pendidikan, kesehatan dan media"), ["education", "health", "youth_women", "media"]),
    ],
    "economy": [
        (L("Mina-rai no rekursu", "Petróleo e recursos", "Oil and resources", "Minyak dan sumber daya"), ["overview", "petroleum", "petroleum_fund", "natural_resources"]),
        (L("Agrikultura no peska", "Agricultura e pesca", "Farming and fishing", "Pertanian dan perikanan"), ["coffee", "agriculture", "livestock_fisheries"]),
        (L("Komérsiu, osan no dezenvolvimentu", "Comércio, dinheiro e desenvolvimento", "Trade, money and development", "Perdagangan, uang dan pembangunan"),
         ["exports", "imports", "banking", "infrastructure", "development_plan", "jobs_migration"]),
    ],
    "tourism": [
        (L("Gia ba vizitante", "Guia do visitante", "Visitor's guide", "Panduan pengunjung"), ["overview", "practical_info", "events_festivals"]),
        (L("Esperiénsia sira", "Experiências", "Experiences", "Pengalaman"),
         ["beaches_islands", "diving_marine", "mountains_trekking", "coffee_villages", "community_eco", "heritage", "food_markets"]),
    ],
    "world": [
        (L("Organizasaun internasionál", "Organizações internacionais", "International organisations", "Organisasi internasional"),
         ["overview", "united_nations", "cplp", "asean", "g7plus", "wto"]),
        (L("Viziñu no parseiru", "Vizinhos e parceiros", "Neighbours and partners", "Tetangga dan mitra"), ["indonesia", "australia", "portugal", "asia_pacific"]),
    ],
}
OTHER = L("Seluk", "Outros", "Other", "Lainnya")
ALSO = L("Husi kategoria seluk", "De outras categorias", "From other categories", "Dari kategori lain")


def grouped(category, items):
    """[(title or None, [items])] for a category page: the listed groups in order, the category's
    other articles, then articles of other categories that also belong here."""
    groups = SUBSECTIONS.get(category)
    if not groups: return [(None, list(items))]
    by_id = {i.id: i for i in items}; used = set(); out = []
    for title, slugs in groups:
        ids = [s if s.startswith("tl.") else f"tl.{category}.{s}" for s in slugs]
        members = [by_id[i] for i in ids if i in by_id and i not in used]
        if members: out.append((title, members)); used.update(m.id for m in members)
    own = [i for i in items if i.id not in used and i.id.startswith(f"tl.{category}.")]
    also = [i for i in items if i.id not in used and not i.id.startswith(f"tl.{category}.")]
    if own: out.append((OTHER, own))
    if also: out.append((ALSO, also))
    return out
