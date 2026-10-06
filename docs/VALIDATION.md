# Validation — LAFA 0.4.0 alpha

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
