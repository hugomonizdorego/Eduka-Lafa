# Security review — 0.4.0 alpha

Review date: 6 October 2026. Scope: source logic, automated adversarial fixtures,
Qt worker delivery and packaging. This is not a penetration test or a guarantee
against compromise. An attacker controlling the user's account, dependencies or
host OS can also alter LAFA. Maintain dependency and OS updates.

| Boundary | Controls and checks |
|---|---|
| Model actions | Fixed read-only tool allowlist; typed/bounded arguments; unknown tools/sources refused; no shell or generated-code executor |
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
| Secrets | Session by default; approved secure keyring only; preferences hold no API keys; environment keys managed externally |
| UI content | Plain-text labels, editors and table items for source/model data; website links are opened by explicit user action |
| Transfer of private text | Document/code preview and confirmation before AI transfer; local search results never sent back to a model; microphone recording explicitly confirmed |
| Public search | Ordinary source-mode chat never issues a public query; dedicated button and explicit `/ask`/`/learn` commands identify public transfers |
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
Qt, keyring and Python still have their own vulnerability surface. PDF resource
limits reduce denial of service but do not isolate a compromised native parser
from all user privileges. Do not equate resource limits with a full container.

External document opening delegates to the user's desktop application. That
application has its own security behavior; a path can still change after a user
chooses Open. User-selected roots and local configuration are trusted preferences,
not a security boundary against another process running as the same OS user.

No live API credentials, account sessions or microphone hardware were tested.
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
