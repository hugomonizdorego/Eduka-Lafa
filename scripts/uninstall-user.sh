#!/bin/sh
# Remove only LAFA user launchers and the source-local environment.
set -eu
LAFA_SOURCE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
LAFA_DATA=${XDG_DATA_HOME:-"$HOME/.local/share"}
rm -f "$LAFA_DATA/applications/lafa-desktop.desktop" "$LAFA_DATA/applications/lafa-settings.desktop" "$LAFA_DATA/applications/lafa-virtual.desktop" "$LAFA_DATA/icons/hicolor/128x128/apps/lafa.png" "$LAFA_DATA/eduka-settings/lafa/launcher.json" "$LAFA_DATA/eduka-settings/lafa/eduka_lafa_settings.py" "$LAFA_DATA/eduka-settings/lafa/lafa-page.json"
rm -rf "$LAFA_SOURCE/.venv"
printf 'LAFA launchers and environment removed. Settings and documents are retained.\n'
