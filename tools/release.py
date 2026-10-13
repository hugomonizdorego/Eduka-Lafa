#!/usr/bin/env python3
"""Prepare a LAFA release: bump the version everywhere and date the changelog.

    python3 tools/release.py patch          0.1.1 -> 0.1.2
    python3 tools/release.py minor          0.1.1 -> 0.2.0
    python3 tools/release.py major          0.1.1 -> 1.0.0
    python3 tools/release.py set 0.2.0      explicit version
    python3 tools/release.py check          verify that all version fields agree

Updates lafa/__init__.py (__version__, VERSION_LABEL), packaging/DEBIAN/control
and turns "## Unreleased" in CHANGELOG.md into "## <version> — <date>".
Then: run the tests, regenerate screenshots, build the .deb, commit, tag
v<version> and push the tag (the release workflow publishes the .deb).
"""
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "lafa" / "__init__.py"
CONTROL = ROOT / "packaging" / "DEBIAN" / "control"
CHANGELOG = ROOT / "CHANGELOG.md"
STAGE = "Alpha"   # shown after the version until LAFA leaves alpha

def current():
    match = re.search(r'^__version__ = "(\d+)\.(\d+)\.(\d+)"', INIT.read_text(), re.M)
    if not match: raise SystemExit("lafa/__init__.py has no MAJOR.MINOR.PATCH __version__.")
    return tuple(int(x) for x in match.groups())

def bump(kind, explicit=None):
    major, minor, patch = current()
    if kind == "patch": return f"{major}.{minor}.{patch + 1}"
    if kind == "minor": return f"{major}.{minor + 1}.0"
    if kind == "major": return f"{major + 1}.0.0"
    if kind == "set" and explicit and re.fullmatch(r"\d+\.\d+\.\d+", explicit): return explicit
    raise SystemExit(__doc__)

def write(version, today=None):
    text = INIT.read_text()
    text = re.sub(r'^__version__ = ".*"$', f'__version__ = "{version}"', text, flags=re.M)
    text = re.sub(r'^VERSION_LABEL = ".*"$', f'VERSION_LABEL = "{version} {STAGE}"', text, flags=re.M)
    INIT.write_text(text)
    CONTROL.write_text(re.sub(r"^Version: .*$", f"Version: {version}", CONTROL.read_text(), flags=re.M))
    log = CHANGELOG.read_text(); today = today or datetime.date.today().isoformat()
    if "## Unreleased" in log:
        log = log.replace("## Unreleased", f"## Unreleased\n\n_Nothing yet._\n\n## {version} — {today}", 1)
        CHANGELOG.write_text(log)

def check():
    version = ".".join(map(str, current()))
    control = re.search(r"^Version: (.*)$", CONTROL.read_text(), re.M).group(1)
    problems = [] if control == version else [f"packaging/DEBIAN/control has {control}"]
    if f"## {version}" not in CHANGELOG.read_text(): problems.append(f"CHANGELOG.md has no '## {version}' section")
    for line in problems: print("✗", line)
    print(("✓ " if not problems else "✗ ") + f"LAFA {version}")
    return 1 if problems else 0

def main(argv):
    if not argv: raise SystemExit(__doc__)
    if argv[0] == "check": return check()
    version = bump(argv[0], argv[1] if len(argv) > 1 else None)
    write(version); print(f"LAFA is now {version}. Next: tests, screenshots, sh tools/build-deb.sh, tag v{version}.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
