# Eduka-Desktop and Eduka-Settings integration

LAFA Desktop and the Virtual Assistant use separate Qt surfaces and launch
roles inside one same-user process. They can be visible independently. Opening
Desktop does not enable the character. Disabling the character keeps Desktop
available. Settings is a dedicated top-level dialog.

## LAFA 0.1.1 on Edukasaun OS (Eduka-Desktop Suite 0.9.24)

### What the `lafa` Debian package installs

| Path | Purpose |
|---|---|
| `/usr/bin/lafa` | Launcher (PyQt5, like the Eduka components) |
| `/usr/lib/lafa/lafa/` | LAFA |
| `/usr/lib/lafa/eduka_lafa_settings.py` | Lafa-Configuration page (PyQt5 for Eduka-Settings) |
| `/usr/share/eduka-settings/plugins/lafa.json` | Page descriptor: id `lafa`, group `APPS` |
| `/usr/share/applications/lafa-desktop.desktop` | LAFA Desktop, category `Education` → Eduka-Desktop's **Edukasaun** category |
| `/usr/share/applications/lafa-settings.desktop` | `lafa --configure` (hidden; opened from LAFA) |
| `/etc/xdg/autostart/lafa-virtual.desktop` | `lafa --autostart`: exits at once unless the Virtual Assistant is activated |
| `/usr/share/doc/lafa/eduka-settings-plugin-pages.patch` | Patch for Eduka-Desktop (below) |

### Lafa-Configuration inside Eduka-Settings

Eduka-Settings 0.9.24 builds its page list in code, so external programs
cannot add pages. `integration/eduka-settings-plugin-pages.patch` adds a small,
generic loader to `usr/bin/eduka-settings` (apply in the Eduka-Desktop
repository with `patch -p1 < eduka-settings-plugin-pages.patch`):

- reads descriptors from `/usr/share/eduka-settings/plugins/*.json`;
- loads only **root-owned, not group/world-writable** descriptors and modules
  under `/usr/lib/` or `/usr/share/`;
- shows the pages in an **APPS** group; `eduka-settings --page lafa` opens it;
- a broken plugin shows an explanation instead of breaking Eduka-Settings;
- Apply and Save & Close also call the page's optional `eduka_apply()`;
  plugin pages are excluded from Eduka's own live-apply hook.

The page uses Eduka-Settings' own object names (`pageTitle`, `card`,
`cardTitle`, `settingRow`, `rowTitle`, `rowLine`, `fieldHint`), so every Eduka
theme styles it. Changes apply live: the page writes
`~/.config/lafa/settings.json` (0600) and runs `lafa --reload`; API keys never
pass through it. Verified by rendering the real eduka-settings 0.9.24 with the
patch (`tools/eduka-settings-preview.py`, screenshots 18–19).

Without the patch, `lafa --configure` opens LAFA's own settings window with
the same options.

### Eduka files LAFA reads (never writes, except the agenda)

| File | Used for |
|---|---|
| `~/.config/eduka-desktop/menu/settings.json` | `language` (`tet` or `system`) |
| `~/.config/eduka-desktop/panel/settings.json` | `position`, `height`, `panel_style`, `width_percent` → where LAFA walks |
| `~/.config/eduka-desktop/desktop/settings.json` | `theme_style`, `accent_color` → LAFA Desktop colours |
| `~/.config/eduka-desktop/agenda.json` | LAFA **adds** homework entries in Eduka's agenda format (opt-in) |
| D-Bus `org.freedesktop.Notifications` | Reminders shown by Eduka-Panel (via `gdbus`) |

## Menu installation (source checkout)

`install-user.sh` creates these user entries:

| Entry | Role | Category |
|---|---|---|
| `lafa-desktop.desktop` | `--window` | Education, Utility, X-Edukasaun |
| `lafa-settings.desktop` | `--settings` | Settings, DesktopSettings, X-Eduka-Settings |
| `lafa-virtual.desktop` | `--virtual` | Hidden; callable by the host |

For an XDG menu implementation, the Edukasaun submenu can include:

```xml
<Menu>
  <Name>Edukasaun</Name>
  <Include><Category>X-Edukasaun</Category></Include>
</Menu>
```

The host may use a custom menu implementation instead. Route the Desktop
entry through that implementation; do not replace its entire menu definition.
The custom settings metadata `X-Eduka-Settings-Page=LAFA` is descriptive. It
becomes a host registration only when the host consumes it.

## All LAFA settings in Eduka-Settings

`create_lafa_page()` returns the complete **Eduka-Settings → LAFA** page:

1. the activation group (below), and
2. `add_lafa_preferences()`: grouped controls for every non-secret preference —
   Virtual Assistant (outfit, roaming, panel edge/height, greeting),
   Personality & activities (hover questions, self-talk, jokes, bath/toilet
   poses, cards, activity duration, intervals), AI & language (language,
   provider, model, Ollama/open-source server addresses, read aloud) and Files
   & weather (city, coordinates, time zone, searchable folders).

**Save** merges the values into `~/.config/lafa/settings.json` with an atomic
0600 write, then starts the fixed role `--reload`; a running LAFA re-reads the
file and applies it live while keeping chat, lesson code and drafts. When LAFA
is not running, `--reload` exits immediately and the values load at the next
start. LAFA re-validates every field on load. **API keys…** opens LAFA's own
settings (`--settings`) because keys are kept only in session memory or the
secure system keyring.

```python
from eduka_lafa_settings import create_lafa_page
page = create_lafa_page(parent, binding="PyQt5")
host.register_page("LAFA", page)   # use the host's real page API
```

## LAFA activation card

`integration/eduka_lafa_settings.py` embeds into **PyQt5, PyQt6 or PySide6**
without importing another binding. Call it from the host after creating its
settings layout, or register it under a dedicated LAFA page in the host's menu:

```python
from eduka_lafa_settings import add_lafa_group
self.lafa_group = add_lafa_group(self.page_layout, binding="PyQt5")
```

The group contains the translated activation checkbox, Open LAFA Desktop and
LAFA Settings buttons. It launches only fixed role arguments through QProcess,
without a shell. The checkbox is refreshed from preferences every second. During
activation it is disabled until the saved preference matches the requested
state. Launch failure or a ten-second timeout restores the actual state and
shows a localized status. A successful detached launch alone is not treated as
proof that the character was enabled.
The source installer writes the absolute executable path into
`$XDG_DATA_HOME/eduka-settings/lafa/launcher.json`; no executable must be guessed
from PATH when that file is present.

A review-copy generator can add the group to a known settings class/layout:

```bash
python3 scripts/integrate-eduka-settings.py /path/to/eduka-settings.py \
  --class-name Settings --layout self.page_layout --binding PyQt5 \
  --output /path/to/fresh-review/eduka-settings.py
```

For a constructor-local layout use `--layout v`. The generator parses the host
source, validates the layout expression and compiles the result. It refuses to
overwrite the original or an existing output. It copies the helper beside the
review output. Add that helper directory to the host's import path or package it
with the host's own source. The generator refuses ambiguous/conditional layouts
and early constructor returns. It preserves space/tab indentation and never
executes the input source. Explicit mode requires class, layout and binding.

For a simple host with exactly one directly assigned top-level constructor
`QVBoxLayout` and one supported Qt binding, conservative auto-detection is
available:

```bash
python3 scripts/integrate-eduka-settings.py /path/to/eduka-settings.py \
  --auto --output /path/to/fresh-review/eduka-settings.py
```

For a page registry, register the complete page factory using the host's API:

```python
from eduka_lafa_settings import create_lafa_page
page = create_lafa_page(parent=self, binding="PyQt5")
# Add page to the existing host registry/sidebar using its actual interface.
```

`integration/lafa-page.json` describes that factory and its supported bindings;
it is not an assumed Eduka-Settings registration API. The user installer copies
the helper and descriptor into the user data integration folder. The helper
rejects mixed Qt bindings within one host process.

Review the actual page in a clearly labeled test host:

```bash
.venv/bin/python integration/demo_eduka_settings.py --review
.venv/bin/python integration/demo_eduka_settings.py
```

Review mode uses temporary preferences and disables launches. Normal mode can
launch the installed LAFA roles. This demo is an integration test application,
not a copy of the latest Eduka-Settings application.

**The current Eduka-Settings repository was not supplied.** An earlier user
source snapshot used a PyQt5 `Settings(QWidget)` constructor and `v` layout,
but that historical structure does not establish the latest API. The generic
hook and source generator were tested; no current OS settings source was
patched or executed. Native registration remains a target-host integration step.

## Readiness on the target OS

```bash
.venv/bin/python scripts/check-system.py
.venv/bin/python scripts/check-system.py --network --json
```

The first command is read-only and does not query public sources. The second
also checks fixed Wikipedia/Dili weather queries and Timor-Leste feeds. Warnings
identify missing optional speech commands, menu entries or local socket support.
The diagnostic cannot prove native page registration, correct panel placement
or a provider account's API permission; test those on Edukasaun OS.

## Panel movement

Configure the actual panel edge and height in LAFA Settings. Walking uses the
active screen geometry, reverses at screen edges and places the overlay above a
bottom panel or below a top panel. It does not draw into panel internals or
cover panel buttons. Window movement runs only on X11 (`xcb`). Test actual
window placement, scale factors, multiple monitors and compositor policies on
the target OS. Wayland controls placement and disables automatic roaming.

## Process activation

`desktop`, `settings`, `virtual`, `enable`, `disable` are the only IPC messages.
Messages end with a newline and are limited to 32 bytes; idle peers expire after
two seconds. A same-user Qt local server starts only after the instance lock.
`--virtual-enable` / `--virtual-disable` are host integration controls. No
arbitrary command, URL, chat message or filename can be sent through IPC.
There is no dedicated server, network listener or scheduled system service.
