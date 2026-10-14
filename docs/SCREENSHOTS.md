# Screenshot review — Lafa 0.2.0 Alpha

Regenerate after every UI change:

```bash
QT_QPA_PLATFORM=offscreen LAFA_QT=pyqt5 python3 scripts/capture-screenshots.py
# with the real Eduka-Settings (captures 32–33):
EDUKA_DESKTOP_SRC=/path/to/Eduka-Desktop QT_QPA_PLATFORM=offscreen LAFA_QT=pyqt5 python3 scripts/capture-screenshots.py
```

Captured with **PyQt5 / Qt 5.15** and the Papirus icon theme, the same stack
as Edukasaun OS, in review mode.

- No internet requests are made.
- Preferences, tasks and results go to a temporary folder.
- Internet sources, weather and headlines are labelled `SAMPLE`.
- Greetings are fixed to "morning" (Home captures may show the afternoon
  greeting when they are taken after a page change).
- Captures 40–46 show actual Lafa widgets on an **illustrated** desktop, not
  Edukasaun OS.

| # | File | Content |
|---|---|---|
| 01 | `01-home.png` | Home: greeting, search, four quick accesses, last material, next activities |
| 02 | `02-home-1024x600.png` | Home at 1024×600: compact icon sidebar, page scrolls |
| 03 | `03-search-local-material.png` | “What is photosynthesis?” → *Local material* with its lesson reference |
| 04 | `04-search-with-internet-source.png` | After *Search internet sources*: a separate *Internet source* result (sample) |
| 05 | `05-search-files.png` | “Find file math homework” → file-name search in the chosen folders |
| 06 | `06-search-os-guide.png` | “How do I change the wallpaper?” → the local Edukasaun OS guide |
| 07 | `07-search-nothing-found.png` | Nothing found: said honestly, with options; nothing sent automatically |
| 08 | `08-learn-lessons.png` | Learn → Lessons (school subjects), favourite star |
| 09 | `09-learn-every-age.png` | Lessons for every age (15–18, atoms) |
| 10 | `10-learn-subject-guide.png` | Subject guide (former “teachers”): practice and local answers |
| 11 | `11-practice-explanation.png` | Latihan: wrong answer with the lesson explanation and related lesson |
| 12 | `12-practice-result.png` | Practice result and *Practise the wrong answers again* |
| 13 | `13-learn-languages.png` | First phrases in many languages (not full courses) |
| 14 | `14-learn-programming.png` | Programming examples in the bounded Python interpreter |
| 15 | `15-library-my-files.png` | Library → My files |
| 16 | `16-library-sources.png` | Library → Internet sources with metadata and status |
| 17 | `17-library-timor-leste-government.png` | Official sources: Governo de Timor-Leste, Ministério da Educação |
| 18 | `18-library-external-sites.png` | External sites: reference works, Kiwix, optional AI websites (open in browser), community wikis |
| 19 | `19-timor-leste-history.png` | Timor-Leste atlas: restoration of independence |
| 20 | `20-timor-leste-presidents.png` | Timor-Leste atlas: Presidents and Prime Ministers |
| 21 | `21-timor-leste-news.png` | Timor-Leste news (sample) with publisher and dates |
| 22 | `22-activities-tasks.png` | My activities → Tasks and timetable |
| 23 | `23-activities-reminders-focus.png` | Reminders (date and time, quick +5/15/30/60) and the session focus timer |
| 24 | `24-activities-practice-results.png` | Hasil Latihan: personal progress, average score (not an official report) |
| 25 | `25-os-help-guides.png` | OS help → Guides with installed tools |
| 26 | `26-os-help-accessibility.png` | OS help → Accessibility |
| 27 | `27-offline-home.png` | Offline: calm “Local features are available” badge, internet button disabled |
| 28 | `28-offline-search.png` | Offline search still answers from local material |
| 29 | `29-about.png` | About: version, what Lafa is and is not |
| 30 | `30-lafa-settings-virtual-assistant.png` | Settings → Virtual Assistant: quiet mode, reduce motion, entertainment, messages per hour |
| 31 | `31-lafa-settings-desktop.png` | Settings → Lafa Desktop |
| 32 | `32-eduka-settings-lafa-configuration.png` | Eduka-Settings → Lafa-Configuration (real Eduka-Settings) |
| 33 | `33-eduka-settings-lafa-configuration-2.png` | Lafa-Configuration, lower part |
| 40 | `40-virtual-walking-on-panel.png` | Virtual Assistant on the Eduka-Panel (illustrated desktop) |
| 41 | `41-virtual-hover-question.png` | Hover question (off in quiet mode) |
| 42 | `42-virtual-tuxedo-party.png` | Tuxedo outfit |
| 43 | `43-virtual-casual-beach.png` | Casual outfit |
| 44 | `44-virtual-bubble.png` | Bubble: continue learning, tasks, focus, OS help — offline |
| 45 | `45-virtual-recommendation.png` | Free-software recommendation |
| 46 | `46-virtual-human-movement.png` | Movement frames (off with reduce motion) |
| 50 | `50-outfits.png` | Three outfits |
| 51 | `51-formal-activities.png` | Tuxedo activities |
| 52 | `52-casual-activities.png` | Casual activities |
| 53 | `53-lafa-roles.png` | Roles — optional entertainment |
| 54 | `54-tuxedo-all-poses.png` | Tuxedo on every pose |
| 55 | `55-casual-all-poses.png` | Casual on every pose |
| 56 | `56-tais-mane-activities.png` | Tais Mane activities |
| 60 | `60-home-tetun.png` | Home in Tetun |
| 61 | `61-learn-tetun.png` | Learn in Tetun |
| 62 | `62-home-eduka-dark-theme.png` | Home with the Edukasaun-Dark theme |
| 63 | `63-timor-atlas-dark-theme.png` | Timor-Leste atlas, dark theme |
