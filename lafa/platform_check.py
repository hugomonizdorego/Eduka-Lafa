"""LAFA is made exclusively for Edukasaun OS.

On Edukasaun OS (or a system with the Eduka-Desktop suite) LAFA runs normally.
Elsewhere it still starts, so developers can download the .deb and try it,
but it shows that it is a developer preview made for Edukasaun OS.
"""
from pathlib import Path

OS_RELEASE = Path("/etc/os-release")
EDUKA_MARKERS = (Path("/usr/lib/edukasaun-desktop"), Path("/usr/bin/eduka-settings"))

def os_release(path=OS_RELEASE):
    data = {}
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:80]:
            if "=" in line:
                key, value = line.split("=", 1); data[key.strip()] = value.strip().strip('"')
    except OSError:
        pass
    return data

def is_edukasaun(path=OS_RELEASE, markers=EDUKA_MARKERS):
    info = os_release(path)
    names = " ".join(info.get(k, "") for k in ("ID", "ID_LIKE", "NAME", "PRETTY_NAME")).casefold()
    return "edukasaun" in names or any(m.exists() for m in markers)
