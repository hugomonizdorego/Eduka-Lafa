# Developing LAFA

LAFA is developed in small, tested steps so each version can be checked and
improved in the next one. Source, comments and developer documentation are in
English; the interface is translated (English, Indonesian, Portuguese, Tetun).

## Set up

```bash
# Same stack as Edukasaun OS (Debian 13): system PyQt5
sudo apt install python3-pyqt5 libqt5svg5 python3-keyring python3-pytest papirus-icon-theme fonts-noto-color-emoji
LAFA_QT=pyqt5 python3 -m lafa.app --review      # or: python3 -c "from lafa.app import main; main()" --review

# Or PySide6 in a virtual environment
python3 -m venv .venv && .venv/bin/pip install -e . pytest
LAFA_QT=pyside6 .venv/bin/python -m lafa.app --review
```

`--review` makes no network calls and writes no preferences or homework.

## Every change

1. Work on a branch; keep changes small.
2. Run the tests on **both** Qt bindings:
   ```bash
   LAFA_QT=pyqt5   QT_QPA_PLATFORM=offscreen python3 -m pytest -q
   LAFA_QT=pyside6 QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q
   ```
3. Regenerate and look at the screenshots after any UI change:
   ```bash
   QT_QPA_PLATFORM=offscreen python3 scripts/capture-screenshots.py
   ```
   With an Eduka-Desktop checkout, the script also captures the real
   Eduka-Settings with Lafa-Configuration:
   `EDUKA_DESKTOP_SRC=/path/to/Eduka-Desktop python3 scripts/capture-screenshots.py`.
4. Add a line under `## Unreleased` in `CHANGELOG.md`.

CI (`.github/workflows/ci.yml`) repeats this on every push: tests on PyQt5 and
PySide6, version check, `.deb` build, `apt install` of the package and the
screenshots (downloadable as workflow artifacts).

## Where things live

| Area | Files |
|---|---|
| Qt binding (PyQt5 / PySide6) | `lafa/qt.py` — always import Qt names from here |
| Eduka-Desktop compatibility | `lafa/eduka.py` (language, panel, theme, notifications, agenda) |
| Virtual Assistant | `lafa/mascot.py`, `lafa/personality.py`, `lafa/outfits.py` |
| Outfit art | `tools/make-outfits.py` → `lafa/assets/lafa-{tuxedo,casual,tais}.png` |
| LAFA Desktop (school) | `lafa/app.py`, `lafa/school.py`, `lafa/osguide.py`, `lafa/learning.py` |
| Lafa-Configuration (Eduka-Settings) | `integration/eduka_lafa_settings.py`, `integration/lafa-page.json` |
| Eduka-Settings plugin pages | `integration/eduka-settings-plugin-pages.patch` (apply to Eduka-Desktop) |
| Online source catalog | `lafa/assets/catalog.json`, `lafa/updates.py` |
| Translations | `lafa/i18n.py` (+ texts in `personality.py`, `school.py`, `osguide.py`) |
| Debian package | `packaging/`, `tools/build-deb.sh` |

## Improving the character art

The Tuxedo, Casual and extra Tais Mane sheets are generated from the original
illustrations (`python3 tools/make-outfits.py`, needs numpy and Pillow). Body
regions per pose are in `REGIONS` in that script. Hand-drawn art can replace
any sheet: keep the file name and the JSON format (`canvas`, `states`,
`rects`), and LAFA uses it without code changes.

## Updating learning sources without a release

Edit `lafa/assets/catalog.json` (links, teacher resources, Timor-Leste cards,
tips, desktop tool names), increase `revision` (`YYYYMMDDNN`) and merge to
`main`. Installed LAFA downloads it within `update_hours` (default 24 h),
validates it and merges it. Only HTTPS links and plain text are accepted.

## Releasing a new version

```bash
python3 tools/release.py patch        # or minor / major / set X.Y.Z
LAFA_QT=pyqt5 QT_QPA_PLATFORM=offscreen python3 -m pytest -q
QT_QPA_PLATFORM=offscreen python3 scripts/capture-screenshots.py
sh tools/build-deb.sh                 # dist/lafa_X.Y.Z_all.deb
git commit -am "Release X.Y.Z" && git tag vX.Y.Z && git push --tags
```

The release workflow builds the `.deb` and attaches it to a GitHub release.
Installed LAFA notices the new release and tells the user to update with the
Eduka Update System or the software centre.

## Installing on Edukasaun OS (Cubic or a running system)

```bash
sudo apt update
sudo apt install ./lafa_X.Y.Z_all.deb   # dependencies come from Debian
```

For Lafa-Configuration inside Eduka-Settings, Eduka-Desktop needs the plugin
pages patch (`/usr/share/doc/lafa/eduka-settings-plugin-pages.patch`). Without
it, the menu entry "Lafa-Configuration" opens LAFA's own settings window with
the same options.
