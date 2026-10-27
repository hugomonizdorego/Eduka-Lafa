# Lafa — Ensiklopédia Timór-Leste

**Lafa 0.3.0 Alpha** is free software for **Edukasaun OS** (Debian 13 Trixie,
LXQt, the Eduka-Desktop suite). It has two parts:

* **Lafa Desktop** — an interactive **encyclopedia of Timor-Leste**, from the
  formation of the island to 2026, for students of every school level and for
  visitors. Texts are in **Tetun, Português, Bahasa Indonesia and English**.
* **Lafa Virtual Assistant** — Lafa the crocodile on the Eduka-Panel: a
  **Timor-Leste guide, study buddy and computer helper** (switched on in
  Eduka-Settings → Lafa-Configuration).

Everything works **offline**. With internet, Lafa downloads texts and
free-licence photos for offline use and updates its data. No login, no AI,
no Lafa server, no personal data sent.

![Lafa Desktop — home](docs/screenshots/01-home.png)

![Article with sources, key facts and timeline](docs/screenshots/04-article-flag.png)

![Millionaire quiz](docs/screenshots/14-millionaire-game.png)

![Lafa Virtual Assistant](docs/screenshots/40-assistant-traditional.png)

[All screenshots](docs/SCREENSHOTS.md) are captures of the real application
(review mode, sample learner "Maria"). The character sheet in `docs/design/`
is the owner's concept art.

## What is inside Lafa Desktop

| Menu | What you find |
| --- | --- |
| **Pájina inisiál** (home) | Greeting, totals, continue learning, next holidays (calendar), this day in history, Tetun word of the day, "did you know?", population chart (World Bank), content and progress charts, place of the week, achievements |
| **Ensiklopédia** | 15 illustrated categories: land, geology and climate · nature · history · colonialism and occupation · conflicts and reconciliation · State and politics · presidents and prime ministers · national symbols (flag, emblem, anthem, currency…) · map, municipalities and islands · culture and tradition · society · economy (exports, imports, coffee, oil and gas, agriculture, natural resources) · tourism · holidays · Timor-Leste in the world. Every article: simple or complete text, key facts, timeline, related pages, a quiz, sources with licences, read aloud |
| **Mapa** | Interactive map of the 14 municipalities (Ataúro since 2022, Oe-Kusi Ambenu RAEOA), administrative posts, tourist places; zoom, search, details |
| **Liña tempu** | About 200 dated events from 44 000 years ago to 2026, by era and topic, with search |
| **Turizmu** | Beaches, mountains, museums, memorials, churches, reefs and more in every municipality, with filters, pictures, tips and the map |
| **Kalendáriu** | Public holidays and national days for any year (Easter and Islamic dates computed), next holiday, export to `.ics` |
| **Kuis Milionáriu** | "Who wants to be a millionaire?" about Timor-Leste: 15 questions from easy to hard, prizes in US dollars (just for fun), safe havens at 5 and 10, lifelines 50:50, audience and "phone Lafa", optional clock |
| **Aprende lian** | 1 173 Tetun words in 30 topics with their meaning in Portuguese, Indonesian, English and the other ASEAN and CPLP languages (Malay, Filipino, Thai, Vietnamese, Khmer, Lao, Burmese, Chinese, Tamil, Spanish, French); word list, flash cards with spaced repetition, quiz |
| **Nível eskola** | Learning paths for the levels of the Ministry of Education: Ensinu Báziku cycles 1–3, Ensinu Sekundáriu, Ensinu Superiór/adults; units with a unit quiz |
| **Fonte no lisensa** | The owner's main sources, every source used (about 700) with licence and the articles that use it, licences of Lafa, credits, downloaded photos with their authors |
| **Offline no atualizasaun** | Download the offline pack, check for new content, refresh World Bank data, storage used |

Search (Ctrl+F) looks through every article, municipality, place, holiday and
word in all four languages (accents and apostrophes do not matter).

## Lafa Virtual Assistant — what it is for

Recommendation, implemented in 0.3.0: Lafa is a **Timor-Leste guide + study
buddy + computer helper** that is useful without being noisy.

* **Shares knowledge often** (every 10 minutes by default, at most 6 times an
  hour, never in quiet mode or over a full-screen app): holidays coming up,
  this day in history, facts, a Tetun word, **a mini quiz you answer in the
  balloon**, a place to visit, words to review, the next article for your
  school level, encouragement for your learning streak.
* **Answers questions offline**: type in the popup to search the encyclopedia
  and the words; a result opens Lafa Desktop on the right page.
* **Quick tiles**: continue reading, millionaire quiz, words, map, calendar,
  **PC help** (opens safe applications from a fixed list: files, browser,
  settings, Wi-Fi, sound, printer, screenshot, LibreOffice…).
* **Better clothes and design**: the three outfits from the owner's character
  sheet — *Casual Belajar*, *Tais Mane* and *Formal* — with waving poses cut
  from the design (tools/make-poses.py); pastel popup matching Lafa Desktop.
* **Smoother animation**: 60 frames a second with cached pictures, real-time
  timing (falls back to 30 fps on slow computers), smooth walking with easing.

## Install on Edukasaun OS

```bash
sh tools/build-deb.sh                       # -> dist/lafa_0.3.0_all.deb
sudo apt install ./dist/lafa_0.3.0_all.deb  # dependencies come from Debian
lafa                                        # or the "Lafa Desktop" menu entry
```

Depends: `python3-pyqt5`, `python3-pyqt5.qtsvg`, `libqt5svg5`, `xdg-utils`.
Recommends: `espeak-ng` (read aloud), `fonts-noto-core` and `fonts-noto-cjk`
(Thai, Khmer, Lao, Burmese, Tamil and Chinese words), the desktop tools that
PC help can open. Developers can run from the source tree with
`python3 -m lafa.app` (PyQt5) or `LAFA_QT=pyside6 python3 -m lafa.app`.

## Offline and online

* The whole encyclopedia, map, quiz, words and learning paths are in the
  package (`lafa/assets/timor`).
* **Offline pack** (Offline no atualizasaun → Download hotu): the Wikipedia
  introduction of each item in four languages (CC BY-SA 4.0) and one photo per
  item from Wikimedia Commons — **only free licences** (CC0, public domain,
  CC BY, CC BY-SA), saved with author and licence (SQLite in
  `~/.local/share/lafa`).
* **New content**: Lafa reads `manifest.json` from this public repository and
  downloads changed files only after checking SHA-256, size and JSON shape.
  Data only — never code.
* **World Bank** indicators (CC BY 4.0) can be refreshed.

See [docs/OFFLINE.md](docs/OFFLINE.md) and [docs/PRIVACY.md](docs/PRIVACY.md).

## Sources, Tetun and review

* Sources named by the owner come first: wikipedia.org, tet.wikipedia.org,
  timor-leste.gov.tl, timorleste.tl, timorleste.mafint.org, timor-research.org,
  data.worldbank.org, britannica.com, tripadvisor.com and moe.gov.tl, plus the
  UN, the Chega! report, the Central Bank, La'o Hamutuk, Tatoli and others.
  Texts are Lafa's own wording; every item lists its sources with licence and
  date accessed.
* **Tetun follows the official text of the Constitution** (Lei-Inan,
  Prezidente Repúblika, Parlamentu Nasionál, tasi-le'un…): see
  [docs/TETUN-STYLE.md](docs/TETUN-STYLE.md).
* All content is marked **draft** until experts review it; each item has
  review notes. See [docs/CONTENT-REVIEW.md](docs/CONTENT-REVIEW.md).

## Licences

* Code: **MIT** (© 2026 Hugo Moniz do Rego).
* Encyclopedia texts, quizzes, vocabulary and illustrations: **CC BY-SA 4.0**.
* Map: geoBoundaries — OpenStreetMap (**ODbL 1.0**) and OCHA/WHO (**CC BY 3.0 IGO**).
* World Bank data: **CC BY 4.0**. Font Nunito: **SIL OFL 1.1**.
* Downloaded photos keep their own free licence and author (shown in the app).

Details: [docs/ASSETS.md](docs/ASSETS.md) and the in-app page *Fonte no lisensa*.

## Development

```bash
python3 tools/check-content.py           # validate all content (add --strict for warnings)
python3 tools/make-manifest.py           # update the content manifest (release)
LAFA_QT=pyqt5 QT_QPA_PLATFORM=offscreen python3 -m pytest -q
LAFA_QT=pyside6 QT_QPA_PLATFORM=offscreen python3 -m pytest -q
python3 scripts/capture-screenshots.py   # docs/screenshots
sh tools/build-deb.sh                    # dist/lafa_<version>_all.deb
```

More in [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md), [docs/CONTENT-SCHEMA.md](docs/CONTENT-SCHEMA.md)
and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Upgrading from 0.2.x

Settings, progress, favourites and quiz results are kept; old start pages move
to the nearest new page. The old school, library, world encyclopedia, news,
weather and AI links were removed: Lafa Desktop is now only about Timor-Leste.

## Ideas for next versions

Expert review of all drafts with teachers (start with history and the State);
audio pronunciation of Tetun words recorded by native speakers; more places
with photos taken in Timor-Leste under a free licence; Mambai, Makasae and
other national languages in the word list; printable worksheets per school
level; a classroom mode for teachers (quiz on a projector); Kiwix-style full
Wikipedia offline packs.
