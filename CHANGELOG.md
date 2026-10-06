# Changelog

## Unreleased

_Nothing yet._

## 0.1.2 — 2026-10-06

### Outfits fixed
- Clothes are rebuilt with garment shapes per pose that end on the drawn
  outlines; no more cut, broken or straight-band clothes.
- **Casual**: sky-blue shirt, khaki **shorts**, white **socks** and red
  sneakers. **Tuxedo**: one piece with a V shirt front, collar, bow tie,
  black trousers and polished shoes. **Tais Mane**: wrap, sash, beads and
  belak on every pose without hand-drawn art.
- Every activity is dressed (sleeping too) except bathing and the toilet.
- `python3 tools/make-outfits.py --preview` shows every pose in every outfit.

### LAFA's roles
- One character, many hats: **teacher, professor, motivator, magician,
  master, comedian and helper**. Each role has an activity with its own scene
  (chalkboard, mortarboard and books, trophy and stars, top hat and wand,
  calm scroll and chess, microphone and spotlight) in every outfit, lines in
  four languages, and a "LAFA's roles" menu on the Virtual Assistant.
- Magician's **mind reader**: six binary cards guess any number from 1 to 63
  and explain the maths.

### LAFA Desktop is a school
- Sidebar organised like a school building: **School** (lobby, classroom,
  teachers' room, exam hall, report card, homework), **Timor-Leste**,
  **Library & labs** and **Help & tools**.
- **Classroom**: lessons with study notes and a task for every subject; Timor-
  Leste history lessons come from the timeline.
- **Exam hall**: quiz (5 questions, instant feedback), test/ulangan (10 on
  one subject) and exam/ujian (20 from all subjects, 20-minute timer), with a
  review of mistakes. Questions: school banks, generated maths, vocabulary
  between Tetun, Portuguese, English and Indonesian, and Timor-Leste history,
  municipalities and holidays.
- **Report card**: every result saved privately (`~/.local/share/lafa/report.json`,
  mode 0600), averages, best scores, grades, and export to a text file.
- **Timor-Leste**: history from the first people of Jerimalai (c. 42,000 years
  ago) through Portuguese Timor, occupation and resistance, the 1999
  referendum, the restoration of independence (20 May 2002) and ASEAN
  membership (2025); national facts and symbols, the 14 municipalities and
  RAEOA with main towns, public holidays, and the news and culture feed.
- Lobby: word of the day in four languages, LAFA's daily motivation, "today
  in Timor-Leste" or the next public holiday, and the roles panel.

## 0.1.1 — 2026-10-06 · patch release (0.1.1 Alpha)

### Edukasaun OS and Eduka-Desktop Suite
- **Debian package** `lafa_0.1.1_all.deb` (`sh tools/build-deb.sh`). `apt install
  ./lafa_0.1.1_all.deb` installs every dependency from the Debian archive
  (python3-pyqt5, libqt5svg5, python3-keyring, fonts-noto-color-emoji, …).
  Menu entry in the Edukasaun category, autostart that runs only when the
  Virtual Assistant is activated, icons, Eduka-Settings plugin descriptor.
- **PyQt5 like the Eduka-Desktop suite** (Qt 5.15 on Debian 13), with PySide6
  still supported for developers (`lafa/qt.py`, `LAFA_QT=pyqt5|pyside6`).
- **Lafa-Configuration in Eduka-Settings**: a native page (Eduka cards, rows
  and live apply) for activation, outfit, size, walking and animation speed,
  personality, balloon time, LAFA Desktop start page, theme, notifications,
  automatic updates, reading speed, language, AI provider, files and weather.
  `integration/eduka-settings-plugin-pages.patch` adds generic plugin pages to
  Eduka-Settings (APPS group); verified with the real eduka-settings 0.9.24.
- LAFA follows Eduka-Desktop: language chosen in Eduka-Settings (Tetun),
  Eduka-Panel edge/height/style (LAFA stands on the real panel), theme and
  accent colour, reminders as Eduka-Panel notifications, homework in the
  Eduka-Panel calendar agenda, XWayland like the Eduka components.

### LAFA Virtual Assistant
- **Three outfits**: Tais Mane (default), Tuxedo and Casual, drawn on every
  pose (`tools/make-outfits.py` builds the sprite sheets). Wardrobe menu on the
  character.
- Outfit activities with small scenes: formal (party, meeting, presentation,
  graduation ceremony, gala dinner, report, speech, red carpet) and casual
  (beach, sunbathing, beach ball, sightseeing, café, shopping, snack, game
  break), each with lines in four languages.
- Tuning: character size, walking speed, animation speed, balloon time.

### LAFA Desktop — a complete school
- **Teachers**: Mathematics, Science, Languages, History & Geography, ICT &
  Coding, Arts & Culture and a Counsellor, each with free resources, offline
  practice (maths exercises, vocabulary cards in 4 languages, quizzes, study
  tips) and “Ask the teacher” with an AI provider.
- **Homework & timetable** stored on the computer; due dates can go to the
  Eduka-Panel calendar. Home shows today's classes and homework due soon.
- School navigation: Library, Computer lab, Notice board, IT help desk; theme
  icons (Papirus) and a drawn Timor-Leste flag.
- **Automatic updates**: validated source catalog from the LAFA repository
  (links, teacher resources, cards, tips, tool names), notice-board refresh,
  new-release notification. No LAFA server.

### Development
- `tools/release.py` (patch/minor/major, check), CI on PyQt5 and PySide6,
  .deb build + apt install test + screenshots as artifacts, release workflow
  that publishes the .deb for `v*` tags. See `docs/DEVELOPMENT.md`.

## 0.1 Alpha (0.1.0a1) — 6 October 2026 · development restart

Version numbering restarts at **0.1 Alpha**. Every feature, test, screenshot and
document is being re-checked from the beginning; earlier prototype results are
history, not current guarantees.

### Redesign (LAFA Desktop, Virtual Assistant, Eduka-Settings)
- **LAFA Desktop redesigned**: new theme, icon navigation, Home dashboard
  (greeting, quick ask, Virtual Assistant toggle, feature cards, tip of the
  day, system check), chat suggestion chips. Settings left the sidebar list.
- **Edukasaun OS help** page and chat answers: 16 offline guides in EN/ID/PT/TET,
  allowlisted tool launcher without a shell, read-only system check, `/os`.
- **Virtual Assistant behaviour**: snaps onto the Eduka-Panel; idle cycle is
  walk to a random spot → activity → walk; activity duration configurable.
- **Hover questions**: touching LAFA with the cursor stops it and shows a
  changing "Can I help?" balloon that reacts to the current activity; clicking
  the balloon opens chat.
- **Personality**: innocent, curious, clever and funny. Each activity is an
  assistant duty; LAFA comments on activities, tells jokes (`/joke`, 😄 button,
  between cards). New preferences: hover questions, self-talk, jokes.
- **All settings in Eduka-Settings**: the native page now holds every
  non-secret preference, saves atomically and live-reloads LAFA with the new
  `--reload` role. LAFA's own settings window uses Eduka-Settings-style
  categories, including Personality & activities and About.
- Screenshot script rewritten: 23 captures including hover, panel walking and
  the Eduka-Settings page.
- Fixed: tool lookup now resolves `shutil.which` at call time; `&` in host
  group titles is no longer shown as a shortcut marker.

### Added
- **Open-source AI without a main server**: Ollama on this computer (free, no
  key, HTTP allowed only for loopback addresses) and any OpenAI-compatible
  open-source server over HTTPS (llama.cpp, vLLM, LocalAI, a school or
  community host). Key is optional for these servers.
- **Fetch available models** button in Settings for every provider except
  Perplexity, so users choose from real model IDs instead of guessing.
- `/calc` (also `/hitung`, `/kalkula`): bounded calculator parsed with `ast`,
  never `eval`; accepts `×`, `÷`, `^` and decimal commas.
- `/help` (also `/bantuan`, `/ajuda`): translated list of LAFA commands.
- LAFA Virtual Assistant greets by local time of day (morning, afternoon,
  evening) on first activation; can be turned off in Settings.
- LAFA Virtual and the Desktop character give a short hop when an answer arrives.

### Fixed
- Tetun, Indonesian and Portuguese Wikipedia searches with no result now fall
  back to English Wikipedia; the source URL shows which edition answered.
- Consecutive same-role messages are merged before provider calls, so
  providers requiring alternating roles accept the source-synthesis step.
- HTTP User-Agent now reports the real package version instead of a fixed value.
- Chat footer no longer warns about paid API credits when an open-source model
  is selected.

### Validation
- 131 automated tests passed in a headless Linux environment; 23 screenshots
  regenerated. See `docs/VALIDATION.md`.

## Prototype history (before the restart)

### Prototype 0.4

- Explicit Search public sources action and `/ask`; ordinary source-mode chat
  is no longer sent automatically to Wikipedia.
- Three settings tabs, complete common UI translations and translated service
  categories/lesson labels for English, Indonesian, Portuguese and Tetun.
- Provider/model edits use a draft; cancellation and failed preference writes
  preserve live preferences. Saving preserves coding output and chat drafts.
- Fixed 60-second activity rotation when culture and encouragement cards are
  both disabled; automatic popups respect pause, drafts and open chat.
- Native Eduka-Settings page factory, descriptor, integration test host,
  activation acknowledgement/timeout and strict single Qt binding checks.
- Safer source-hook auto-detection and launcher escaping for unusual paths.
- Bounded regular-file preference reads, field-by-field recovery, and a read-only
  system readiness checker with optional live public-source checks.
- 88 tests (87 passed, one environment skip) and 17 review screenshots.

### Prototype 0.3

- Separate Desktop, Settings and Virtual Assistant surfaces and launch roles.
- Virtual assistant off by default, translated activation and introduction.
- Traditional male Timor-Leste costume, Tebe-tebe and Bidu mascot poses.
- Seventeen activities; panel-edge walking configuration and idle source cards.
- Timor-Leste topic headlines from Tatoli, Timor Post and government feeds.
- Public extract mode without AI keys; bounded Python coding lessons and
  JavaScript/HTML/CSS read/export examples.
- English source/build documentation; system-language mode plus four UI locales.
- Native Eduka-Settings group and review-copy source integration generator.
- Hardened document access, special-file rejection, PDF limits, framed IPC,
  settings validation, lesson resource bounds and worker error recovery.
- Fourteen reproducible screenshots and expanded security/validation notes.

### Prototype 0.2

Desktop bubble input, fifteen activities, weather, world RSS headlines,
additional learning links, session reminders and same-user launcher activation.

### Prototype 0.1

Initial native assistant, official provider adapters, local file/document tools,
public encyclopedia, browser service links and nine character poses.
