"""Compatibility with the Eduka-Desktop suite (Eduka-Desktop, Eduka-Panel,
Eduka-Settings) of Edukasaun OS.

LAFA reads Eduka's own preference files so it never contradicts the desktop:
interface language (Eduka-Settings → Language), Eduka-Panel position, height
and style (LAFA walks exactly on top of it), theme and accent colour, the
agenda shown in the Eduka-Panel calendar, and the notification service that
Eduka-Panel provides (org.freedesktop.Notifications). Every read is bounded
and failure-tolerant; without Eduka-Desktop LAFA uses its own defaults.
File formats follow eduka_common.py of edukasaun-desktop-menu 0.9.24.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

THEME_ACCENTS = {"Eduka-Default-Theme": "#00a879", "Eduka-Low-Theme": "#315bef", "Liquid Glass": "#1e9bd7",
                 "Edukasaun-Dark": "#26a69a", "Eduka-Transparan": "#6c6c6c", "Eduka-MultiColor": "#5b6ee1"}
DARK_THEMES = {"Edukasaun-Dark", "Eduka-Transparan"}
PANEL_STYLES = {"full", "floating", "short", "dock"}
COMMON = Path("/usr/lib/edukasaun-desktop/eduka_common.py")

def base():
    return Path.home() / ".config" / "eduka-desktop"

def read_json(path, limit=262_144):
    """Small regular JSON file, or {} (never raises)."""
    try:
        path = Path(path)
        if not path.is_file() or path.is_symlink() or path.stat().st_size > limit: return {}
        value = json.loads(path.read_text(encoding="utf-8"))
        return value
    except (OSError, ValueError, UnicodeError):
        return {}

def panel_config(): return read_json(base() / "panel" / "settings.json") or {}
def menu_config(): return read_json(base() / "menu" / "settings.json") or {}
def desktop_config(): return read_json(base() / "desktop" / "settings.json") or {}

def installed():
    """True on a computer with the Eduka-Desktop suite (or its settings)."""
    return COMMON.is_file() or (base() / "panel" / "settings.json").is_file()

def in_session():
    return bool(os.environ.get("EDUKA_DESKTOP_SESSION"))

# ----------------------------------------------------------------- language
def _system_language():
    for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        for part in os.environ.get(var, "").split(":"):
            first = part.split(".")[0].split("@")[0]
            if first and first not in ("C", "POSIX"): return first
    return "en"

def language():
    """LAFA locale (en, id, pt, tet) that matches Eduka-Desktop's interface.

    Eduka-Settings stores 'tet' or 'system' in menu/settings.json; the login
    screen can also choose Tetun (EDUKA_LOGIN_LANGUAGE). Other system
    languages map to LAFA's closest translation: pt_BR → pt, ms → id.
    """
    menu = menu_config()
    choice = str(menu.get("language", "system") or "system") if isinstance(menu, dict) else "system"
    if choice == "tet" or os.environ.get("EDUKA_LOGIN_LANGUAGE") == "tet": return "tet"
    code = _system_language().replace("-", "_")
    short = code.split("_")[0].casefold()
    return {"tet": "tet", "pt": "pt", "id": "id", "ms": "id", "en": "en"}.get(short, "en")

# -------------------------------------------------------------------- panel
def panel():
    """Eduka-Panel geometry preferences: edge, height, gap, style, width."""
    cfg = panel_config()
    if not isinstance(cfg, dict) or not cfg: return None
    try: height = max(34, min(58, int(cfg.get("height", 40))))
    except (TypeError, ValueError): height = 40
    try: width = max(45, min(100, int(cfg.get("width_percent", 96))))
    except (TypeError, ValueError): width = 96
    style = str(cfg.get("panel_style", "floating"))
    style = style if style in PANEL_STYLES else "floating"
    edge = str(cfg.get("position", "Bottom")).capitalize()
    edge = edge if edge in {"Bottom", "Top", "Left", "Right"} else "Bottom"
    return {"edge": edge.casefold(), "height": height, "gap": 0 if style == "full" else 5,
            "style": style, "width_percent": width, "autohide": bool(cfg.get("autohide", False))}

def panel_span(left, width, info):
    """Horizontal range (x0, x1) of a top/bottom Eduka-Panel on a screen."""
    if not info or info["style"] == "full": return left, left + width
    percent = min(info["width_percent"], 64) if info["style"] == "short" else 50 if info["style"] == "dock" else info["width_percent"]
    length = int(width * percent / 100)
    x0 = left + (width - length) // 2
    return x0, x0 + length

# -------------------------------------------------------------------- theme
def theme():
    """{'name', 'dark', 'accent'} of the current Eduka theme."""
    cfg = desktop_config()
    name = str(cfg.get("theme_style", "Eduka-Default-Theme")) if isinstance(cfg, dict) else "Eduka-Default-Theme"
    name = name if name in THEME_ACCENTS else "Eduka-Default-Theme"
    accent = str(cfg.get("accent_color", "") or "") if isinstance(cfg, dict) else ""
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent): accent = THEME_ACCENTS[name]
    high_contrast = bool(cfg.get("visual_accessibility", False)) if isinstance(cfg, dict) else False
    return {"name": name, "dark": name in DARK_THEMES, "accent": accent.lower(), "high_contrast": high_contrast}

# ------------------------------------------------------------ notifications
def notify(title, body, icon="lafa", seconds=8, runner=subprocess.run):
    """Show a desktop notification through Eduka-Panel (freedesktop D-Bus).

    Uses gdbus (libglib2.0-bin) or notify-send; never a shell. Returns True
    when a notification service accepted it.
    """
    title, body = str(title)[:120], str(body)[:500]
    if shutil.which("gdbus"):
        command = ["gdbus", "call", "--session", "--dest", "org.freedesktop.Notifications",
                   "--object-path", "/org/freedesktop/Notifications", "--method", "org.freedesktop.Notifications.Notify",
                   "LAFA", "0", icon, title, body, "[]", "{}", str(int(seconds * 1000))]
    elif shutil.which("notify-send"):
        command = ["notify-send", "-a", "LAFA", "-i", icon, "-t", str(int(seconds * 1000)), title, body]
    else:
        return False
    try:
        return runner(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=4, check=False).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False

# ------------------------------------------------------------------- agenda
def agenda_path():
    return base() / "agenda.json"

def add_agenda(date, time_text, text, alarm="notify"):
    """Add an entry to the Eduka-Panel calendar agenda (same JSON format)."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date): raise ValueError("Date must be YYYY-MM-DD.")
    if time_text and not re.fullmatch(r"\d{2}:\d{2}", time_text): raise ValueError("Time must be HH:MM.")
    text = " ".join(str(text).split())[:200]
    if not text: raise ValueError("Enter a short description.")
    items = read_json(agenda_path(), 1_000_000)
    items = items if isinstance(items, list) else []
    entry = {"id": f"{date}-{int(time.time() * 1000)}", "date": date, "time": time_text, "text": "LAFA · " + text,
             "alarm": alarm if alarm in {"notify", "sound", "blink"} else "notify", "fired": ""}
    items.append(entry)
    path = agenda_path(); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".agenda-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream: json.dump(items, stream, indent=4, ensure_ascii=False)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    return entry

# ------------------------------------------------------------ Eduka-Settings
PLUGIN_DESCRIPTOR = Path("/usr/share/eduka-settings/plugins/lafa.json")

def settings_page_available():
    """True when Eduka-Settings can show Lafa-Configuration (plugin pages)."""
    program = shutil.which("eduka-settings")
    if not program or not PLUGIN_DESCRIPTOR.is_file(): return False
    try: return "plugin_descriptors" in Path(program).read_text(encoding="utf-8", errors="ignore")
    except OSError: return False

def open_settings_page(runner=subprocess.Popen):
    """Open Eduka-Settings on the Lafa-Configuration page (fixed arguments)."""
    try:
        runner(["eduka-settings", "--page", "lafa"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return True
    except OSError:
        return False

# ------------------------------------------------------------------ session
def prefer_xwayland():
    """Eduka components run through XWayland on Wayland so panel-relative
    placement works; LAFA does the same (LAFA_NATIVE_WAYLAND=1 opts out)."""
    wayland = os.environ.get("XDG_SESSION_TYPE", "").casefold() == "wayland" or bool(os.environ.get("WAYLAND_DISPLAY"))
    if wayland and os.environ.get("DISPLAY") and not os.environ.get("LAFA_NATIVE_WAYLAND") and not os.environ.get("QT_QPA_PLATFORM"):
        os.environ["QT_QPA_PLATFORM"] = "xcb"
        return True
    return False
