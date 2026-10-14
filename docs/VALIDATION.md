# Validation — Lafa 0.2.0 Alpha

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
