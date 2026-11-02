# Validation — Lafa 0.3.0

Checks run on 2 November 2026 in a headless Linux container (Ubuntu 24.04,
Qt offscreen). Not yet tested on Edukasaun OS hardware.

| Check | Result |
|---|---|
| Automated tests, **PyQt5** (Qt 5.15) and **PySide6** (Qt 6) | **80 passed** each, 0 skipped; see `test-results.txt` |
| New tests | Interface and content only in Tetun and Portuguese; old English/Indonesian settings become "system"; system language → Tetun or Portuguese; Constitution: 170 articles in both languages, references ("15", "art. 15", "Artigu 59", "artigo 166.º"), search ("bandeira" → 15, "línguas oficiais" → 13, "Provedor" → 27, "liberdade de imprensa" → 41), accent-free highlighting without word parts; anthem cues ordered and inside the recording, intro/interlude, next occurrence of a line; audio player without a backend reports it, external player command starts at the position; Constitution and Symbols pages in the app (search, bilingual view, preamble, copy, karaoke line); links "artigu 15" → reader only in paragraphs about the Constitution; photo gallery with a fake Wikipedia/Commons (maps, flags and logos skipped, nothing fetched twice); every page in both languages |
| Content | `tools/check-content.py`: ✓ 195 articles, 20 days, 6 indicators, 14 municipalities, 113 places, 1 173 words · 0 errors · 0 warnings; 1 321 quiz questions; `docs/REVIEW-NOTES.md` lists 342 items for review |
| Constitution | Parsed from the official PDFs: 170 articles and 33 headings in both languages, paragraph counts equal for every article (after handling "1.Text" and "Artigu 22.O" in the Tetun edition) |
| Anthem timing | Vocal separation (MDX-Net) + Whisper large-v3-turbo teacher-forced scoring + melody matching (`tools/anthem/`): the refrain is sung five times; start times 0:13.4, 0:42.9, 1:13.1, 2:14.2, 2:46.4 (±0.5 s). **Not yet checked by ear** |
| Audio | PySide6 Qt Multimedia plays and seeks (position 61.4 s two seconds after seeking to 60 s); without a sound device it falls back to an external player or reports "can't play audio here" instead of scrolling lyrics in silence; PyQt5 here has no Qt Multimedia, so the ffplay fallback was used |
| Map | Municipalities = union of the posts by the official list (shapely); areas: Díli 227 km², Liquiçá 550, Aileu 736, Cova Lima 1 207; airport and Comoro in Díli, Zumalai in Cova Lima |
| Screens | 44 captures regenerated with PyQt5 and inspected (`SCREENSHOTS.md`): both languages, dark theme, 1024×600, 150 % scaling, assistant |
| Eduka-Settings page | Built directly from `integration/eduka_lafa_settings.py` in Tetun and Portuguese (language choice: system, Tetun, Português) |
| Network | The sandbox blocked every source site (wikipedia.org, commons.wikimedia.org, timorleste.tl, Tatoli, gov.tl sites, WIPO); content was researched with web search only, and the offline pack and gallery were tested with recorded data |
| Debian package | `lafa_0.3.0_all.deb` (17.6 MB) installed with apt over 0.2.1; ran from `/usr/lib/lafa` with the system PyQt5; see `package-smoke.txt` |
| **Not yet tested** | Edukasaun OS hardware; hearing the anthem with a real sound device and `python3-pyqt5.qtmultimedia` on Debian 13; live photo downloads; expert review of the drafts |

## 0.2.1


Checks run on 15 October 2026 in a headless Linux container (Ubuntu 24.04,
Qt offscreen). Not yet tested on Edukasaun OS hardware.

| Check | Result |
|---|---|
| Automated tests, **PyQt5** (Qt 5.15) and **PySide6** (Qt 6) | **253 passed** each, 0 skipped (+10 subtests); see `test-results.txt` |
| New tests (`tests/test_encyclopedia.py`) | encyclopedia checker; 12 + 6 categories with icons, illustrations and 4-language titles; ≥ 2 articles per world category; every article has objectives, sources and questions with explanations; all 0.2.0 atlas topics reachable; accent-folded search; scores saved; Back restores page and scroll; cross-area links; no sideways scrolling at 1024×600; all three modules (hotspots, periods, size chart, exercise; geology vs human scale; order, match, impacts); offline pack with a fake Wikipedia/Commons (extracts, pictures with licence and author, files 0600, stop keeps data, non-free pictures skipped); 8-frame walk follows distance, turn and reduce motion; click mask and popup draft |
| Content | `tools/check-encyclopedia.py`: ✓ 15 files, 34 articles; `tools/check-curriculum.py` valid |
| Screens | 1024×600, 1366×768, 1920×1080, dark theme, Tetun and 150 % scaling (`QT_SCALE_FACTOR=1.5`) captured and inspected (captures 63–85). Lafa has no own text-size setting; 150 % was tested as display scaling |
| Wayland | Weston 13 headless + Qt wayland plugin: `platformName()=wayland`, Lafa does not roam (walks in place ≈ 38 px/s of cycle), window mask set, popup clears the mask, draft kept. Window placement is decided by the compositor; fullscreen pause is X11-only. Not tested on a real Wayland desktop session |
| Network | The sandbox blocked wikipedia.org, upload.wikimedia.org, commons.wikimedia.org and timor-leste.gov.tl, so the offline pack and links were tested with recorded data only |
| Debian package | `lafa_0.2.1_all.deb` (14.8 MB) installed with apt; ran from `/usr/lib/lafa` with the system PyQt5 in Tetun: SVG icons, Timor-Leste article, dinosaur module, 8 walk frames per outfit; see `package-smoke.txt` |

## 0.2.0


Checks run on 14 October 2026 in a headless Linux container (Ubuntu 24.04,
Qt offscreen). Not yet tested on Edukasaun OS hardware.

| Check | Result |
|---|---|
| Automated tests, **PyQt5** (Qt 5.15, Edukasaun OS stack) | **236 passed**, 0 skipped (+10 subtests); see `test-results.txt` |
| Automated tests, **PySide6** (Qt 6) | **236 passed**, 0 skipped (+10 subtests) |
| Offline-first regressions (`tests/test_offline_first.py` and others) | No network for local search, file search/read, calculator, reminders (network, `urlopen` and sockets patched to fail); local search works offline and online without a key; internet failure keeps local results without pop-ups; reminders ring offline, persist across restart, missed ones fire once; upgrade from 0.1.x keeps settings, tasks, results and reminders, backs up AI fields once, never touches the keyring; no AI client import; no AI claims in the UI in four languages |
| Practice | Unique questions per session; limited bank announced; retry of mistakes; "Average score" labelled correctly |
| Interface | Six sections and old routes; 1024×600 and 150 % text (layout hints fit); `Alt+1…6` and `Ctrl+F` without duplicates after rebuilds; four languages complete |
| Virtual Assistant | Quiet mode, hourly limit, fullscreen pause flag, reduce motion, entertainment excluded by default, quick actions offline, Lafa Desktop never switches it on |
| Sources | Status ok / not found / restricted / unknown; 24 h cache; *Check now*; metadata for every source; timor-leste.gov.tl and moe.gov.tl present; community wikis separate |
| Debian package | `sh tools/build-deb.sh` → `lafa_0.2.0_all.deb` (13.7 MB). `apt install` resolved the dependencies (no keyring, no WebEngine); postinst ran without a GUI; see `package-smoke.txt` |
| Installed package smoke test | Lafa 0.2.0 from `/usr/lib/lafa` with the system PyQt5: six sections, compact sidebar at 1024×600, local search modes (answer, files, guide, calc) |
| Version | `tools/release.py check`: `lafa/__init__.py`, `packaging/DEBIAN/control` and `CHANGELOG.md` agree on 0.2.0 |
| Lessons | `tools/check-curriculum.py`: all 18 files valid (IDs, metadata, four languages) |
| Eduka-Settings integration | Real eduka-settings 0.9.24 with the plugin-pages patch renders Lafa-Configuration (screenshots 32–33) |
| Screenshots | 51 captures regenerated with PyQt5 and Papirus icons, visually inspected |
| **Not yet tested** | Wayland (untested by design: report only); real X11 walking, hover and fullscreen detection on a running Eduka-Panel (`xprop` needed); live websites (Wikipedia, RSS, Open-Meteo, source status) — tested with recorded data; Debian 13 itself (Ubuntu container, same package names); espeak-ng audio; real desktop tools from OS help |

The Tuxedo, Casual and extra Tais Mane poses are generated from the original
illustrations (`tools/make-outfits.py`). They are recognisable, but a
professional illustrator should review or replace them.

## 0.1.4 and earlier

0.1.4 passed 214 tests on PyQt5 and PySide6 (6 October 2026).

## Prototype 0.4 results (history)

Completed on 6 October 2026 in a Linux headless environment.

| Check | Result |
|---|---|
| Automated core, live-data, revision and Qt tests | **87 passed, 1 skipped** (88 total), 76.014s; see `test-results.txt` |
| Compilation and shell syntax | All 28 Python source files and launch/install/uninstall shell scripts passed |
| Package build | Version 0.4.0 source wheel built successfully; no `.deb` created |
| Isolated package installation | Installed client loads 17 activities, 9 traditional poses, 9 pages and 3 settings tabs |
| Final translation/UI smoke | Installed package renders EN, ID, PT, TET; tab labels, public search and system-language selection checked after final translation/ampersand changes |
| Screenshots | Seventeen actual Qt/review compositions; settings, native page test host, Indonesian system UI and companion bubble visually inspected |
| Role separation | Desktop visible with virtual off; enabling introduces the traditional character; disabling keeps Desktop available |
| Native settings helper | Same-binding page factory/group renders in a PySide6 test host; mixed bindings rejected; pending, acknowledgement, failure and timeout fixtures passed |
| Source integration | Auto-detection rejects ambiguous/conditional layouts and constructor returns; generated review source preserves space/tab indentation and compiles |
| Idle behavior | Activity changes at 60/120s even with all cards disabled; automatic popups respect pause, drafts, open chat, busy/offline state |
| Preference editing | Cancel/failed writes preserve live preferences; Save preserves lesson code/output and unsent chat; offline Save keeps every character paused |
| Configuration reads | Bounded regular-file reads; FIFO rejection without blocking; invalid fields preserve unrelated valid preferences |
| Launcher quoting | Two-layer desktop/Exec decoding recovers paths containing spaces, backslashes, dollar/backtick, quotes and percent; control/equals paths refused |
| Local IPC fixtures | Fragmented frame accepted; combined/unknown/invalid/oversized messages refused; real socket test skipped below |
| Read-only tools | Hidden/outside files, internal/external/directory symlinks and named pipes rejected; private results not sent to model |
| PDF worker | Existing resource-limited converter and secure copied-input tests retained |
| Coding bounds | Conditions/loops work; host access, giant formatting/powers/sequences, infinite loops and nested expansion rejected |
| Public search privacy | Ordinary source-mode chat never calls Wikipedia or an API; dedicated public button sends `/ask`; cited extracts and personal-support behavior tested |
| Readiness report | Default mode does not query public sources; report excludes keys, model IDs, chat and selected folder paths |
| News/weather/reminders | Metadata/host/date/XML/topic filtering, failure handling, ambiguous cities, monotonic deadlines and offline deferral passed |

## Live public retrieval

The final `scripts/check-system.py --network --json` report is included as
[`system-check.json`](system-check.json). Using this project's HTTPS transport,
Wikipedia search, Dili forecast and the configured Timor-Leste news feeds
completed successfully without AI credentials. A separate Wikipedia check
returned six results for Dili and a 2,884-character introduction.

A separate final Timor-Leste check retrieved **12** topic-matching headline
records from Tatoli, Timor Post and Government of Timor-Leste, with **no failed
feeds**, at `2026-10-06T12:49:38+00:00`. This count is separate from the readiness
report. World-news live access was not repeated in this revision; its unchanged
transport/parser passed the deterministic fixtures.

These checks prove retrieval during the check, not continuing availability,
independent verification of every publisher claim or certainty of forecasts.
Screenshot weather/headlines are labeled fixtures. Coding output in capture 12
was produced by the actual teaching interpreter. Captures 05/14 place actual
companion pixels on an illustrative desktop; capture 15 uses a labeled test host.

## Untested target behavior

The skipped test is real local IPC activation: this runtime rejects AF_UNIX
socket creation with `PermissionError: Operation not permitted`. Fragmented-frame
fixtures passed, but real same-user activation still needs an Edukasaun OS test.
No access restriction was relaxed. API adapter tests mock requests; no paid
inference, provider account sign-in or microphone/speaker hardware was tested.
Optional `espeak-ng` and `arecord` are absent in this runtime.

Native registration in the latest Eduka-Settings/Edukasaun menu, actual
Eduka-Panel/X11 walking, Wayland placement, transparency, tray, multi-monitor and
scale-factor behavior are not verified on the target OS. The latest host source
was not supplied. The project provides hooks, a page factory, a test host and
instructions; it does not claim a current OS patch or installation. Offscreen
Qt notices about raise/size hints reflect this headless renderer.

This is a tested alpha, not a penetration-test certificate or a guarantee that
all vulnerabilities are absent. See `SECURITY.md` for remaining dependency,
parser and host risks.
