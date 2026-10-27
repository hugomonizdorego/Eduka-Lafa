# Security review

## 0.3.0 (27 October 2026)

- **Removed code paths**: file search, PDF reading (pdftotext worker), the
  Python lesson sandbox, RSS news, weather and the source-status checker are
  gone with the old school and library.
- **New network code (`lafa/sync.py`)**: HTTPS only, fixed hosts
  (`*.wikipedia.org`, `commons.wikimedia.org`, `upload.wikimedia.org`,
  `api.worldbank.org`, `raw.githubusercontent.com/hugomonizdorego/Eduka-Lafa`),
  redirects refused, size limits (JSON 4 MB, photos 6 MB, content files 8 MB),
  descriptive user agent, no cookies or personal data.
- **Content updates are data only**: the manifest's paths must match
  `(content|vocab|map)/<name>.json` (no `..`), each file must match its
  SHA-256 and size, and its JSON must have the expected shape before it is
  written atomically to `~/.local/share/lafa/updates`. A broken or unknown
  file is ignored when loading. Trust comes from the project's GitHub
  repository; no code is downloaded or run.
- **Photos**: only Wikimedia Commons files with a free licence (CC0, public
  domain, CC BY, CC BY-SA; non-free flag rejected); the bytes must be a JPEG,
  PNG or WebP; file names are sanitised.
- **Offline store**: SQLite with parameterised queries; a damaged database
  disables downloads but never stops the app.
- **PC help** launches only programs from a fixed list (`actions.APPS`), found
  on PATH, with no arguments and no shell.
- **Calendar export** writes only to the file the learner chooses.

## 0.2.0 (14 October 2026)

The 0.2.0 changes remove most of the external attack surface:

- **No AI clients, API keys or keyring.** `providers`, `aihub` (Qt WebEngine
  with a persistent web profile), `signin` (OAuth loopback listener) and
  microphone transcription are gone. Lafa holds no secrets, so there are none
  to leak. `tests/test_offline_first.py` checks that no module imports a
  keyring or AI client.
- **No automatic transfers.** Search runs locally. The internet is contacted
  only by explicit buttons or commands (Wikipedia, news, weather, source
  status, saving a page) or by the optional data catalogue. The connection
  probe uses fixed public hosts.
- **Reminders and progress files**: atomic writes with mode 0600, bounded and
  validated on load (count, text length, control characters, dates). Broken
  files are ignored, never executed.
- **Source status**: HEAD requests with a fixed user agent, no redirects
  followed, HTTPS only. The result is a state (ok / not found / restricted /
  unknown), never page content.
- **Saved pages**: only front pages and feeds of listed sources, robots.txt
  respected, same-site HTTPS redirects only, size limits.
- **Updates**: Lafa downloads only the validated content catalogue (data). It
  never downloads or runs program code; program updates come from APT / EUS.
- **Fullscreen check** (X11): fixed `xprop` arguments, no shell, short
  timeout.

The table below is the earlier review. Rows about model actions, secrets and
AI transfer no longer apply, because those features were removed.

## Earlier review (0.1 Alpha)

Review date: 6 October 2026. Scope: source logic, automated adversarial fixtures,
Qt worker delivery and packaging. This is not a penetration test or a guarantee
against compromise. An attacker controlling the user's account, dependencies or
host OS can also alter LAFA. Maintain dependency and OS updates.

| Boundary | Controls and checks |
|---|---|
| Actions | Fixed allowlists of apps and Lafa pages; typed/bounded arguments; unknown tools/sources refused; no shell or generated-code executor |
| Local document access | Selected roots; visible names; directory-FD traversal using O_NOFOLLOW; regular-file checks; nonblocking special-file access; 10 MB input bound; internal and external symlink fixtures rejected |
| XML/archives | Bounded archive member size; entity/DOCTYPE declarations refused; no archive extraction into the filesystem |
| PDF conversion | Private copied input, separate worker, fixed Poppler arguments; CPU 10s, address space 768 MB, output file 1 MB, parent timeout 17s; first 30 pages only |
| Python learning | Manual AST interpreter; no eval/exec/import, attributes, objects, files, sockets or processes; code/AST/step/depth/value/output limits; nested list and formatting memory attacks tested |
| HTTP/API | HTTPS, timeouts and size limits; credentials not forwarded through redirects; remote error bodies not echoed; official endpoints fixed in adapters |
| RSS metadata | Publisher-host allowlists; HTTPS links; dates/future-date checks; XML rejection; partial/total failures reported without creating news |
| Local IPC | Same-user socket; instance lock; five fixed roles; newline framing; max 32 bytes; 16 peer cap; two-second peer expiry |
| Configuration | 64 KiB bounded nonblocking reads; regular files only; symlink/FIFO rejection; each invalid field falls back independently; strict booleans and finite numeric ranges |
| Menu launchers | Freedesktop value and Exec argument escaping; literal percent doubled; control characters/equals in executable paths rejected |
| Host integration | Fixed argv, one Qt binding, bounded preference/launcher reads, activation acknowledgement and timeout; AST-only review-copy generation |
| Secrets | None since 0.2.0: no API keys, no keyring access |
| UI content | Plain-text labels, editors and table items for source/model data; website links are opened by explicit user action |
| Transfer of private text | Since 0.2.0 nothing is transferred: documents, code and search text stay local; no microphone |
| Public search | Local search never issues a public query; only the *Search internet sources* button and `/ask` contact Wikipedia |
| Worker delivery | QObject slots receive results on the UI thread; callback failures clear busy state rather than leaving the UI locked |

## Fixes in this revision

- Ordinary no-API chat previously used a privacy heuristic before automatic
  Wikipedia lookup. That path is removed; public lookup now requires the
  explicit search button or public command.
- Preference reads reject named pipes and non-regular files without blocking.
  Malformed fields no longer discard unrelated valid preferences.
- Provider/model changes use a draft. Closing Settings or a failed preference
  write preserves the live preferences; API secrets are managed separately.
- Launchers account for both desktop-file value decoding and Exec quoting,
  including special characters and percent placeholders.
- Native activation waits for the stored state, restores actual state on failure
  and rejects mixed bindings. The source generator rejects ambiguous layouts
  and early returns and never executes supplied host source.

## Existing controls retained from 0.3.0

- Document reads previously resolved a path before opening it; a same-root
  symlink could be followed, and another process could swap path components.
  Secure directory traversal now refuses symlinks at every relative component.
- Special files are rejected after a nonblocking open so a named pipe cannot
  freeze a document worker.
- PDF output no longer accumulates in an unbounded stdout pipe. The input is a
  verified private copy; conversion and output are resource limited.
- Launcher messages now have framing, cumulative bounds, a peer limit and expiry.
- Configuration files have size/type/range limits; invalid values recover to
  defaults instead of enabling features through truthy strings.
- Python lessons reject host access, large sequence multiplication, giant powers,
  format-string padding, infinite loops and recursively expanded shared lists.
- Source/model text uses plain Qt text. Callback exceptions release busy state.

## Remaining limits

The Python interpreter is a small teaching language implemented in Python, not
an OS sandbox for arbitrary Python. Unsupported syntax raises an error. Poppler,
Qt and Python still have their own vulnerability surface. PDF resource
limits reduce denial of service but do not isolate a compromised native parser
from all user privileges. Do not equate resource limits with a full container.

External document opening delegates to the user's desktop application. That
application has its own security behavior; a path can still change after a user
chooses Open. User-selected roots and local configuration are trusted preferences,
not a security boundary against another process running as the same OS user.

Live websites were not contacted from the build sandbox; online features were tested with recorded data.
Real IPC was skipped because the execution environment rejects AF_UNIX sockets.
Deterministic fragmented-frame and command-injection fixtures passed; these
do not replace a real host activation test.
Native Eduka-Settings registration, X11 movement, Wayland placement, transparency,
tray behavior and multi-monitor positioning require tests on the actual OS.

Community encyclopedias and news publishers can contain errors or opinions.
Citations indicate provenance, not automatic truth. The assistant does not
silently obey instructions inside retrieved documents or public content.

## Primary technical references

- [Qt local server access options](https://doc.qt.io/qt-6/qlocalserver.html)
- [Qt local socket buffer controls](https://doc.qt.io/qtforpython-6/PySide6/QtNetwork/QLocalSocket.html)
- [Freedesktop Exec quoting](https://specifications.freedesktop.org/desktop-entry/latest/exec-variables.html)
- [Qt detached process launch](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QProcess.html)
- [Python AST reference and parsing limits](https://docs.python.org/3.11/library/ast.html)
- [Python resource limits](https://docs.python.org/3/library/resource.html)
