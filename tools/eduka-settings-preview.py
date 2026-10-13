#!/usr/bin/env python3
"""Screenshot the real Eduka-Settings with LAFA's Lafa-Configuration page.

Developer tool. Copies an Eduka-Desktop checkout to a temporary folder,
applies integration/eduka-settings-plugin-pages.patch, registers LAFA's page
descriptor and renders Eduka-Settings offscreen with PyQt5 (as on Edukasaun OS).
Nothing is installed and no real preferences are touched.

    python3 tools/eduka-settings-preview.py /path/to/Eduka-Desktop out.png [--scroll 0.5]
"""
import argparse
import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def prepare(source, folder):
    shutil.copytree(Path(source) / "usr", folder / "usr")
    target = folder / "usr/bin/eduka-settings"
    if "plugin_descriptors" not in target.read_text():
        subprocess.run(["patch", "-s", "-p1", "-d", str(folder), "-i", str(ROOT / "integration/eduka-settings-plugin-pages.patch")], check=True)
    plugins = folder / "plugins"; plugins.mkdir()
    descriptor = json.loads((ROOT / "integration/lafa-page.json").read_text())
    descriptor["module"] = str(ROOT / "integration/eduka_lafa_settings.py"); descriptor["icon"] = str(ROOT / "packaging/icons/lafa-64.png")
    (plugins / "lafa.json").write_text(json.dumps(descriptor))
    return target, plugins

def render(program, plugins, output, page, scroll):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    sys.path.insert(0, str(Path(program).parents[1] / "lib/edukasaun-desktop"))
    loader = importlib.machinery.SourceFileLoader("eduka_settings", str(program))
    spec = importlib.util.spec_from_loader("eduka_settings", loader); es = importlib.util.module_from_spec(spec); loader.exec_module(es)
    es.PLUGIN_DIRS = [plugins]; es.PLUGIN_ROOTS = ()   # preview only: the real loader requires root-owned files under /usr
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv[:1]); es.install_translations(app)
    window = es.Settings(); window.resize(1100, 900); window.open_page(page); window.show()
    for _ in range(10): app.processEvents()
    if scroll:
        bar = window.stack.currentWidget().verticalScrollBar(); bar.setValue(int(bar.maximum() * scroll))
        for _ in range(5): app.processEvents()
    window.grab().save(str(output))
    print("pages:", ", ".join(window.page_keys))

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("eduka_desktop"); parser.add_argument("output"); parser.add_argument("--page", default="lafa"); parser.add_argument("--scroll", type=float, default=0.0)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="eduka-preview-") as temp:
        folder = Path(temp); program, plugins = prepare(args.eduka_desktop, folder)
        home = folder / "home"; home.mkdir()
        os.environ.update(HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"), XDG_DATA_HOME=str(home / ".local/share"))
        render(program, plugins, Path(args.output).resolve(), args.page, args.scroll)
    os._exit(0)  # PyQt5 teardown order (as in Eduka-Desktop's exit_now)

if __name__ == "__main__":
    main()
