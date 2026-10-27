# Lafa 0.3 content format — Ensiklopédia Timór-Leste

All encyclopedia content is JSON in `lafa/assets/timor/`. Text is our own
wording (never copied), based on the sources listed with each item. Check
every file with:

    python3 tools/check-content.py

`L4` below means an object with the four languages, all required:

```json
{"tet": "Tetun (see docs/TETUN-STYLE.md)", "pt": "Português", "id": "Bahasa Indonesia", "en": "English"}
```

## Articles — `content/<group>.json`

```json
{"articles": [{
  "id": "tl.history.first_peoples",           // from lafa/assets/timor/plan.json (new ids: tl.<category>.<slug>)
  "category": "history",                      // one of plan.json "categories"
  "also": ["colonial"],                       // optional: other categories where it is listed too
  "title": L4,
  "summary": L4,                              // 2–3 short sentences: the simple text for young learners
  "levels": ["eb2", "eb3", "es", "sup"],      // school levels (plan.json "levels") the article suits
  "period": {"from": -44000, "to": -3000},    // optional, years (negative = BCE / years ago)
  "sections": [{"heading": L4, "text": L4}],  // 3–6 sections, 50–150 words each per language
  "facts": [{"label": L4, "value": "1 340 434", "year": 2022}],   // value: string or L4; year when it changes
  "timeline": [{"date": "1975-11-28", "title": L4}],               // optional; "1975", "1975-11", "-42000"
  "figure": {"illustration": "proclamation", "caption": L4},       // key from the list below
  "wiki": {"en": "History of East Timor", "pt": "História de Timor-Leste", "tet": "Istória Timór-Leste", "id": "Sejarah Timor Leste"},
  "related": ["tl.history.restoration_2002", "place.cristo_rei", "mun.dili", "day.proclamation"],
  "tags": ["fretilin", "1975"],
  "quiz": [{"q": L4, "options": [L4, L4, L4, L4], "answer": 2, "why": L4, "difficulty": 4}],
  "sources": [{"title": "History of East Timor", "publisher": "Wikipedia (English)",
               "url": "https://en.wikipedia.org/wiki/History_of_East_Timor", "accessed": "2026-10-27", "licence": "CC BY-SA 4.0"}],
  "review": {"status": "draft", "notes": "what a reviewer should check"}
}]}
```

* `quiz`: 4–6 questions per article, four options each, `answer` is the index
  of the correct option, `why` explains it. `difficulty` 1–15 is the step of
  the millionaire ladder: 1–5 easy (Ensinu Báziku), 6–10 medium, 11–15 hard
  (Ensinu Sekundáriu and above). Give each article at least one easy, one
  medium and one hard question. Wrong options must be plausible and clearly wrong.
* `sources`: at least two, `https://` only, the page you used. Prefer the
  sources named by the owner: Wikipedia (en/pt/tet/id), timor-leste.gov.tl,
  timorleste.tl, timorleste.mafint.org (MAF fact file), timor-research.org,
  data.worldbank.org, britannica.com, tripadvisor.com, moe.gov.tl — plus UN,
  Chega! (chegareport.net), INE census, Banco Central, La'o Hamutuk, Tatoli.
* `wiki`: Wikipedia page titles used to download the introduction and a free
  picture for offline use (leave out a language when no article exists).
* Numbers that change (population, GDP, oil fund…) always carry a `year`.
* Unsure facts: keep them out, or say "about" and explain in `review.notes`.

## Municipalities — `content/municipalities.json`

```json
{"municipalities": [{
  "id": "mun.baucau", "name": {"tet": "Baukau", "pt": "Baucau", "id": "Baucau", "en": "Baucau"},
  "geo": "Baucau",                                   // shapeName in lafa/assets/timor/map (Ataúro: "Atauro")
  "capital": {"tet": "Baukau", "pt": "Baucau", "id": "Baucau", "en": "Baucau"},
  "area_km2": 1494, "population": {"value": 133881, "year": 2022},
  "posts": ["Baguia", "Baucau", "Laga", "Quelicai", "Vemasse", "Venilale"],
  "languages": L4, "products": L4,
  "summary": L4, "sections": [...], "facts": [...], "highlights": ["place.baucau_old_town"],
  "figure": {...}, "wiki": {...}, "quiz": [...], "sources": [...], "review": {...}
}]}
```

## Tourist places — `content/places.json`

```json
{"places": [{
  "id": "place.cristo_rei", "name": L4, "municipality": "mun.dili",
  "type": "statue",                 // beach island mountain viewpoint church statue museum monument memorial lake cave
                                    // hot_spring waterfall fort market park reef village town garden river
  "lat": -8.5130, "lon": 125.6080,  // decimal degrees (WGS84); Timor-Leste lies between lat -9.6…-8.1, lon 124.0…127.4
  "summary": L4, "text": L4,        // text: 80–200 words: what it is, history, what to see
  "tips": L4,                       // how to get there, best time, respect local rules
  "illustration": "statue", "wiki": {...}, "commons": "Cristo Rei of Dili.jpg",   // optional
  "quiz": [...], "sources": [...], "review": {...}
}]}
```

## Holidays and national days — `content/days.json`

```json
{"days": [{
  "id": "day.restoration", "date": "05-20",       // "MM-DD", "easter-2", "easter+60" or "islamic:eid_al_fitr"
  "type": "holiday",                               // holiday | commemorative
  "name": L4, "summary": L4, "sections": [...], "law": "Lei n.º 10/2005, alterada pela Lei n.º 3/2016",
  "illustration": "independence", "related": [...], "quiz": [...], "sources": [...], "review": {...}
}],
 "islamic_dates": {"eid_al_fitr": {"2026": "03-20"}, "eid_al_adha": {"2026": "05-27"}},   // approximate
 "notes": L4}
```

## Indicators — `content/indicators.json`

```json
{"indicators": [{"id": "SP.POP.TOTL", "name": L4, "unit": "people",
  "series": [[2002, 948000], [2022, 1340434]], "source": "World Bank WDI", "url": "https://data.worldbank.org/indicator/SP.POP.TOTL?locations=TL",
  "licence": "CC BY 4.0", "accessed": "2026-10-27"}]}
```

## Vocabulary — `vocab/words.json` and `vocab/<lang>.json`

```json
{"words": [{"id": "w0001", "tet": "bondia", "cat": "greetings", "pos": "phrase",
            "en": "good morning", "pt": "bom dia", "ind": "selamat pagi", "level": 1,
            "ex": {"tet": "Bondia, mestre!", "en": "Good morning, teacher!"}}]}
```

`id` is the word id; the Indonesian meaning is in `ind`. Words are in `vocab/words.json`
(and `vocab/words_*.json`, read the same way).

Other languages (ASEAN and CPLP) are `vocab/<code>.json`: `{"lang": "th", "words": {"w0001": "สวัสดีตอนเช้า"}}`.
Codes: ms (Malay), fil (Filipino), th (Thai), vi (Vietnamese), km (Khmer),
lo (Lao), my (Burmese), zh (Chinese), ta (Tamil), es (Spanish), fr (French).

## Illustration keys

Use one of these for `figure.illustration`, `illustration` or leave it out:

land & nature: `tl-overview island-formation geology mountain mountain-ramelau river lake sea-coast beach coral-reef whale climate flood earthquake forest mangrove sandalwood crocodile birds animals national-park environment cave`
history: `prehistory austronesian-boat kingdom trade-ships caravel fort colonial-town treaty revolt ww2 carnation proclamation resistance memorial nobel ballot un-peace independence constitution camp reconciliation maritime asean diplomacy church-crowd`
state: `parliament palace government-palace justice police military village-council`
symbols: `flag emblem anthem currency languages dili-city`
culture: `tais uma-lulik dance likurai music legend food crafts adornment church mosque procession football literature festival people`
economy: `oil-gas fund exports imports coffee rice maize crops livestock fishing minerals tourism port road electricity bank plan workers`
society: `population school university health youth women media city`
places & days: `island viewpoint statue museum monument hot-spring waterfall market village town garden diving trekking calendar new-year veterans labour christmas easter eid heroes`
