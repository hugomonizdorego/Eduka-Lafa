#!/usr/bin/env python3
"""Write lafa/assets/timor/manifest.json: the content version and the SHA-256 of
every content, vocabulary and map file. Lafa compares it with the copy on
GitHub to download only changed files (see lafa/sync.py).

    python3 tools/make-manifest.py [VERSION]      # default: today, e.g. 2026.10.27
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lafa.sync import make_manifest  # noqa: E402

BASE = ROOT / "lafa" / "assets" / "timor"
version = sys.argv[1] if len(sys.argv) > 1 else time.strftime("%Y.%m.%d")
manifest = make_manifest(BASE, version)
(BASE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"manifest {version}: {len(manifest['files'])} files")
