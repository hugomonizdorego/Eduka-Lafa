# Architecture

LAFA is a Python/PySide6 native client with one shared process and three
independently visible surfaces: Desktop, Settings and Virtual Assistant. There
is no dedicated network server, embedded login browser or background service.

```mermaid
flowchart TD
    Desktop["LAFA Desktop"] --> Router["Bounded tools and AI router"]
    Settings["LAFA settings"] --> Pet["Virtual assistant"]
    Pet --> Router
    Router --> Local["Local files and lessons"]
    Router --> Public["Public sources, weather and news"]
    Router --> API["Optional official AI API"]
```

Settings enables the mascot, language, outfit, idle popups, local headlines and
panel geometry. Desktop alone never enables it. Same-user IPC routes fixed launch
roles to the process holding the instance lock. Browser sign-in is independent
of API access and belongs to the user's browser.

| Module | Responsibility |
|---|---|
| app | Desktop pages, settings dialog, worker delivery, tray, transfer consent |
| mascot | Three unmodified atlases, runtime cropping, costumes, bubble, idle/popup clock, X11 movement |
| agent | Direct commands, optional model envelopes/actions, cited key-free extracts |
| timor | Three local feeds, topic filtering, curated multilingual culture cards |
| learning | Bounded AST teaching interpreter and examples; no host execution |
| tools | Bounded local filename search, secure document access, Wikipedia and browser links |
| pdf_worker | Resource-limited Poppler conversion of a private input copy |
| live_info | Geocoding, forecasts, RSS metadata and source dates |
| instance | Framed and bounded same-user launch-role socket |
| providers/net | Official schemas, HTTPS bounds, redirect refusal, reachability |
| config | System-language preference, XDG settings and secure secrets |
| desktop_entry | Two-layer freedesktop Exec quoting for fixed launcher paths |
| voice/reminders | Explicit recording, local playback, in-memory timers |
| integration/eduka_lafa_settings | Binding-preserving settings group/page and pending activation state |
| integration/demo_eduka_settings | Clearly labeled runnable host for reviewing the actual integration widget |
| scripts/check-system | Read-only readiness report, isolated Qt probe and opt-in public checks |

Blocking network work, file scans, lessons, PDF conversion and voice run outside
the UI thread. QObject receivers deliver completion/error handling on that
thread. Local filenames are never sent back to models. Documents and lesson code
require separate transfer confirmation. Model actions cannot execute commands.

Source mode formats actual Wikipedia introductions after an explicit public
search action or `/ask`, not generated reasoning. Ordinary chat never triggers
an automatic public query; greetings/support can use local prepared replies.
Curated culture cards have check dates and links; news/weather
have publication/data/retrieval times. Neither failures nor empty feed windows
are replaced by sample content during normal operation.

Filename search stops at 40,000 entries, depth 10, eight seconds or 120 matches.
Documents stop at 10 MB and 20,000 preview characters; PDF reads 30 pages.
Lessons stop at 20,000 code characters, 1,200 AST nodes and 10,000 interpreter
steps with nested-value and output bounds. This is not a full Python runtime.

Idle time is monotonic and observes LAFA input only. Busy work, open bubble,
pause, dragging and offline status suppress random activity. Network checks do
not restart idle timing. Popups dismiss after 15 seconds unless the user
interacts. Local headlines are refreshed at a configurable interval only when
Virtual Assistant and news updates are enabled; automatic popups wait for idle.
Disabling all card types does not block activity rotation. A typed draft, open
bubble or pause suppresses unsolicited popups. Provider/model preference edits
are drafted until Save; rebuilding the UI preserves code, output and chat draft.

On X11, only the walking state changes window position above/below the configured
panel. Wayland owns position. Animation is procedural around still illustrations;
the character does not actually bathe, play games or perform a full dance rig.
