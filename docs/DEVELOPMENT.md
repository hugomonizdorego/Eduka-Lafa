# Developing Lafa 0.3

## Run from the source tree

```bash
python3 -m lafa.app                 # PyQt5 (as on Edukasaun OS)
LAFA_QT=pyside6 python3 -m lafa.app # PySide6 (pip install PySide6)
python3 -m lafa.app --review        # sample learner, nothing saved or sent
```

## Tests and checks

```bash
LAFA_QT=pyqt5   QT_QPA_PLATFORM=offscreen python3 -m pytest -q
LAFA_QT=pyside6 QT_QPA_PLATFORM=offscreen python3 -m pytest -q
python3 tools/check-content.py [content/<file>.json | vocab/<file>.json] [--strict]
python3 scripts/check-system.py [--network] [--json]
```

The tests cover the content (sources, quizzes, Tetun and Portuguese, map
links, vocabulary), the knowledge base, progress, the millionaire game, tips,
the offline store, the photo gallery and the update channel (with a fake
network), settings and language migration, the interface texts, the
Constitution (references and search), the anthem cues and the audio player,
every page in both languages, items of every kind, the quiz game, the word
page, settings, school levels, small screens and the Virtual Assistant.

## Content

* Format: [CONTENT-SCHEMA.md](CONTENT-SCHEMA.md). Tetun: [TETUN-STYLE.md](TETUN-STYLE.md).
* Planned ids and categories: `lafa/assets/timor/plan.json`.
* Add or fix an article: edit the JSON (with Python, `ensure_ascii=False`),
  run `tools/check-content.py`, then `tools/make-manifest.py` so installed
  copies receive the change through *Konteúdu foun*.
* Every item needs at least two `https://` sources with `accessed`, a
  `review` object and four languages. Quiz `difficulty` 1–15 is the step of
  the millionaire ladder.

## Generators

| Tool | Makes |
| --- | --- |
| `tools/make-fonts.py` | Nunito static fonts |
| `tools/make-map.py` | Post map JSON from geoBoundaries ADM2 (cached in `build/geo`); municipalities are the union of their posts (needs `pip install shapely`) |
| `tools/make-constitution.py` | `constitution.json` from the official PDFs in `tools/sources/constitution/` (needs `pdftotext`, poppler-utils) |
| `tools/anthem/` | How the anthem's lyric times were measured (vocal separation + Whisper scoring); see its README |
| `tools/make-icons.py` | SVG icons |
| `tools/make-illustrations.py` | SVG illustrations + manifest |
| `tools/make-poses.py` | Waving outfit poses from the owner's design sheet |
| `tools/make-outfits.py`, `tools/make-walk.py` | Outfit sheets and the walk cycle |
| `tools/make-manifest.py` | `manifest.json` for content updates |
| `scripts/capture-screenshots.py` | `docs/screenshots/*.png` |

## Release

```bash
python3 tools/release.py minor      # or patch / set X.Y.Z (updates version and changelog)
python3 tools/make-manifest.py
python3 -m pytest -q                # both bindings
python3 scripts/capture-screenshots.py
sh tools/build-deb.sh               # dist/lafa_<version>_all.deb
```

Tag `v<version>`; the release workflow builds and publishes the `.deb`.
