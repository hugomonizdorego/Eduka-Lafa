# Lafa offline and online

Lafa's main functions work without internet, login, an AI key or a Lafa
server. The internet only adds sources. This page says exactly what works
where. The tests that prove it are in `tests/test_offline_first.py`.

## Always available (no internet)

| Feature | Where | Notes |
|---|---|---|
| Search of lessons, atlas, OS guides, saved material | Home, Library → Search | Results labelled *Materi lokal* / *Materi tersimpan*; weak matches are shown as choices |
| File search and reading | Home ("Cari file …"), Library → My files | File names in the chosen folders; TXT, MD, CSV, HTML, DOCX, ODT, PDF (pdftotext) |
| Lessons for ages 5–100 and school subjects | Learn → Lessons | Favourites and *Continue learning* |
| Latihan, Simulasi Tes, retry mistakes | Learn → Practice | No repeated questions; explanations from the lessons |
| Hasil Latihan | My activities → Practice results | Personal progress, not an official report |
| Languages, digital literacy, programming examples | Learn | Python examples run in a bounded interpreter |
| Timor-Leste atlas | Timor-Leste → History, places and symbols | Built-in text; online refresh is optional |
| Tasks, timetable | My activities → Tasks | Saved on this computer |
| Reminders | My activities → Reminders | Saved; ring offline while Lafa runs; missed ones shown once after a restart |
| Focus timer | My activities → Reminders | This session only, labelled so; no alarm when Lafa is closed |
| OS help | OS help | Guides, accessibility, computer check, installed tools |
| Calculator | Search box (`12 * 7`, `/calc`) | No eval |
| Read aloud | Search results, Virtual Assistant | Local espeak-ng |
| Kiwix | Library → External sites | Offline Wikipedia and books once installed and a ZIM file is copied |
| Virtual Assistant | Eduka-Panel | Continue learning, tasks, focus, OS help, quiet mode |

## Adds something when online

| Feature | How it starts | When it fails |
|---|---|---|
| Wikipedia extracts | *Search internet sources* button or `/ask` | The note says the internet search failed; local results stay |
| Save a page for offline | *Save* on an extract or a source | Nothing saved; message in the status line |
| Learning-website status | Opening Library → Internet sources (cached 24 h) or *Check now* | Status stays "unknown" |
| Timor-Leste and world news | Timor-Leste → News | Previous headlines stay, labelled with their fetch date |
| Weather | Timor-Leste → Weather | Message under the weather box |
| Atlas refresh | Timor-Leste → atlas | Built-in text stays |
| Content catalogue (data) | Automatic, at most once per chosen interval, if switched on | Previous catalogue stays |

## What offline looks like

- The badge at the top right says *"Fitur lokal tetap tersedia"* (Local
  features are available). It never shows a pop-up and does not repeat.
- Internet buttons are disabled and explain that they need internet. Local
  buttons are never disabled for lack of internet.
- The connection check runs in the background against public hosts
  (Wikipedia, Open-Meteo, timor-leste.gov.tl) and never blocks the window.

## What Lafa never does

- Send a question, document or file content anywhere by itself.
- Download large archives or AI models, or install Ollama.
- Download whole websites, scrape behind a login, or run downloaded code.
- Call cached data "latest".
