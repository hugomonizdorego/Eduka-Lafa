"""Words on Lafa Desktop screens: Tetun and Português, the official languages
(Konstituisaun, artigu 13).

Tetun follows docs/TETUN-STYLE.md (official spelling of the Konstituisaun).
`t(lang, key, **values)` gives the Tetun or Portuguese text, or the key itself.
"""
from ..kb import show

# key: (tet, pt)
T = {
    # --- shell and navigation
    "app_subtitle": ("Ensiklopédia Timór-Leste", "Enciclopédia de Timor-Leste"),
    "nav_home": ("Pájina inisiál", "Início"),
    "nav_encyclopedia": ("Ensiklopédia", "Enciclopédia"),
    "nav_map": ("Mapa", "Mapa"),
    "nav_timeline": ("Liña tempu", "Linha do tempo"),
    "nav_places": ("Turizmu", "Turismo"),
    "nav_calendar": ("Kalendáriu", "Calendário"),
    "nav_quiz": ("Kuis Milionáriu", "Quiz Milionário"),
    "nav_language": ("Aprende lian", "Aprender línguas"),
    "nav_paths": ("Nível eskola", "Níveis escolares"),
    "nav_constitution": ("Konstituisaun", "Constituição"),
    "nav_symbols": ("Símbolu Nasionál", "Símbolos Nacionais"),
    "nav_sources": ("Fonte no lisensa", "Fontes e licenças"),
    "nav_data": ("Offline no atualiza", "Offline e atualização"),
    "nav_settings": ("Konfigurasaun", "Definições"),
    "nav_about": ("Kona-ba Lafa", "Sobre o Lafa"),
    "back": ("Fila", "Voltar"),
    "search_placeholder": ("Buka artigu, fatin, munisípiu, liafuan…", "Pesquisar artigos, lugares, municípios, palavras…"),
    "online": ("Online", "Online"),
    "offline": ("Offline", "Offline"),
    "online_tip": ("Iha internet: Lafa bele atualiza dadus no hatudu imajen foun.", "Com internet: o Lafa pode atualizar dados e mostrar imagens novas."),
    "offline_tip": ("La iha internet: ensiklopédia, mapa, kuis no lian hotu servisu nafatin.", "Sem internet: a enciclopédia, o mapa, o quiz e as línguas continuam a funcionar."),
    "notifications": ("Avizu", "Avisos"),
    "no_notifications": ("La iha avizu foun.", "Sem avisos novos."),
    "offline_promo_title": ("Hola dadus ba offline", "Guardar dados offline"),
    "offline_promo_text": ("Download testu no imajen hotu, atu aprende la ho internet.", "Descarregue textos e imagens para aprender sem internet."),
    "offline_promo_button": ("Download agora", "Descarregar agora"),
    "review_banner": ("MODU REVIZAUN · dadus ezemplu · la rai no la haruka buat ida", "MODO DE REVISÃO · dados de exemplo · nada é guardado nem enviado"),
    "learner": ("Estudante", "Estudante"),
    # --- home
    "greet_morning": ("Bondia", "Bom dia"),
    "greet_afternoon": ("Botarde", "Boa tarde"),
    "greet_evening": ("Bonoite", "Boa noite"),
    "home_sub": ("Ohin ita sei aprende saida kona-ba Timór-Leste?", "O que vamos aprender hoje sobre Timor-Leste?"),
    "start_learning": ("Hahú aprende", "Começar a aprender"),
    "play_quiz": ("Halimar kuis", "Jogar o quiz"),
    "stat_articles": ("Artigu", "Artigos"),
    "stat_articles_note": ("{n} lee ona", "{n} lidos"),
    "stat_municipalities": ("Munisípiu", "Municípios"),
    "stat_municipalities_note": ("{n} esplora ona", "{n} explorados"),
    "stat_places": ("Fatin turístiku", "Lugares turísticos"),
    "stat_places_note": ("{n} haree ona", "{n} vistos"),
    "stat_words": ("Liafuan", "Palavras"),
    "stat_words_note": ("{n} aprende ona", "{n} aprendidas"),
    "continue_learning": ("Kontinua aprende", "Continuar a aprender"),
    "upcoming_days": ("Loron importante tuir mai", "Próximas datas importantes"),
    "in_days": ("loron {n} tan", "daqui a {n} dias"),
    "today": ("Ohin", "Hoje"),
    "tomorrow": ("Aban", "Amanhã"),
    "today_history": ("Ohin iha istória", "Neste dia na história"),
    "this_month_history": ("Iha fulan ne'e, iha istória", "Neste mês, na história"),
    "word_of_day": ("Liafuan loron nian", "Palavra do dia"),
    "did_you_know": ("Ita hatene ka lae?", "Sabia que…?"),
    "read_more": ("Lee liu tan", "Ler mais"),
    "population_chart": ("Populasaun Timór-Leste", "População de Timor-Leste"),
    "content_chart": ("Konteúdu ensiklopédia", "Conteúdo da enciclopédia"),
    "my_progress": ("Ha'u-nia progresu", "O meu progresso"),
    "progress_caption": ("husi konteúdu hotu", "de todo o conteúdo"),
    "place_of_week": ("Fatin semana nian", "Lugar da semana"),
    "show_on_map": ("Haree iha mapa", "Ver no mapa"),
    "achievements": ("Konkista sira", "Conquistas"),
    "unlocked": ("LOKE ONA", "DESBLOQUEADO"),
    "locked": ("Seidauk loke", "Bloqueado"),
    "level": ("Nível", "Nível"),
    "xp_level": ("Nível {n} · {xp} XP", "Nível {n} · {xp} XP"),
    "streak": ("Loron {n} tuituir malu", "{n} dias seguidos"),
    "source_label": ("Fonte", "Fonte"),
    "data_year": ("Dadus {year}", "Dados de {year}"),
    "see_all": ("Haree hotu", "Ver tudo"),
    "open": ("Loke", "Abrir"),
    "close": ("Taka", "Fechar"),
    "all": ("Hotu", "Todos"),
    "empty_content": ("Konteúdu sei to'o", "O conteúdo está a chegar"),
    "empty_content_text": ("Seidauk iha artigu iha ne'e. Atualiza dadus bainhira iha internet.", "Ainda não há artigos aqui. Atualize os dados quando tiver internet."),
    # --- encyclopedia & articles
    "enc_title": ("Ensiklopédia Timór-Leste", "Enciclopédia de Timor-Leste"),
    "enc_sub": ("Husi tasi-le'un Timór nia moris to'o 2026: istória, kultura, Estadu, ekonomia no natureza.", "Da formação da ilha até 2026: história, cultura, Estado, economia e natureza."),
    "n_articles": ("artigu {n}", "{n} artigos"),
    "n_items": ("{n}", "{n}"),
    "all_levels": ("Nível hotu", "Todos os níveis"),
    "simple": ("Simples", "Simples"),
    "complete": ("Kompletu", "Completo"),
    "read_tab": ("Lee", "Ler"),
    "quiz_tab": ("Kuis", "Quiz"),
    "key_facts": ("Faktu importante", "Factos principais"),
    "timeline_title": ("Liña tempu", "Cronologia"),
    "related": ("Haree mós", "Ver também"),
    "sources": ("Fonte", "Fontes"),
    "licence": ("Lisensa", "Licença"),
    "accessed": ("asesu {date}", "acedido em {date}"),
    "review_draft": ("Versaun provizória: presiza revizaun husi espesialista", "Rascunho: precisa de revisão por especialista"),
    "review_ok": ("Revee ona", "Revisto"),
    "save": ("Rai", "Guardar"),
    "saved": ("Rai ona", "Guardado"),
    "read_aloud": ("Lee ho lian maka'as", "Ler em voz alta"),
    "stop_reading": ("Para lee", "Parar leitura"),
    "wiki_online": ("Lee iha Wikipedia", "Ler na Wikipédia"),
    "offline_extract": ("Testu husi Wikipedia (download ona)", "Texto da Wikipédia (descarregado)"),
    "photo_credit": ("Foto: {author} · {licence}", "Foto: {author} · {licence}"),
    "illustration_credit": ("Ilustrasaun Lafa (CC BY-SA 4.0)", "Ilustração Lafa (CC BY-SA 4.0)"),
    "full_text_in": ("Testu kompletu: {langs}", "Texto completo: {langs}"),
    "article_quiz": ("Teste ita-nia koñesimentu", "Teste os seus conhecimentos"),
    "question_n": ("Pergunta {i} husi {n}", "Pergunta {i} de {n}"),
    "right": ("Loos!", "Certo!"),
    "wrong": ("La loos.", "Errado."),
    "next": ("Tuir mai", "Seguinte"),
    "finish": ("Remata", "Terminar"),
    "score": ("Ita hatán loos {s} husi {n}", "Acertou {s} de {n}"),
    "again": ("Koko fali", "Tentar de novo"),
    "no_quiz": ("Artigu ne'e seidauk iha pergunta.", "Este artigo ainda não tem perguntas."),
    "municipality": ("Munisípiu", "Município"),
    "capital": ("Kapitál", "Capital"),
    "area": ("Área", "Área"),
    "population": ("Populasaun", "População"),
    "posts": ("Postu administrativu", "Postos administrativos"),
    "languages_spoken": ("Lian", "Línguas"),
    "products": ("Produtu", "Produtos"),
    "places_here": ("Fatin turístiku iha ne'e", "Lugares turísticos aqui"),
    "visit_tips": ("Konsellu ba vizita", "Dicas para a visita"),
    "coordinates": ("Koordenada", "Coordenadas"),
    "type": ("Tipu", "Tipo"),
    "holiday": ("Feriadu nasionál", "Feriado nacional"),
    "commemorative": ("Loron komemorativu", "Data comemorativa"),
    "date_this_year": ("Data iha {year}", "Data em {year}"),
    "law": ("Lei", "Lei"),
    # --- search
    "search_results": ("Rezultadu ba “{q}”", "Resultados para “{q}”"),
    "no_results": ("La hetan buat ida. Koko liafuan seluk.", "Nada encontrado. Tente outras palavras."),
    "kind_article": ("Artigu", "Artigo"),
    "kind_municipality": ("Munisípiu", "Município"),
    "kind_place": ("Fatin", "Lugar"),
    "kind_day": ("Loron", "Data"),
    "kind_word": ("Liafuan", "Palavra"),
}

def t(lang, key, **values):
    row = T.get(key)
    if row is None: return key
    text = row[index(lang)]
    if values:
        try: text = text.format(**values)
        except (KeyError, IndexError, ValueError): pass
    return show(text, lang)

def index(lang):
    """Position of the language in the (tet, pt) rows: Portuguese for "pt", Tetun otherwise."""
    return 1 if lang == "pt" else 0

def extend(rows):
    """Pages register their own words (keeps each page's texts next to its code)."""
    for key, row in rows.items():
        if len(row) != 2: raise ValueError(f"{key}: Tetun and Portuguese needed")
        T[key] = row
