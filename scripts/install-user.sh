#!/bin/sh
# Source installation only. No .deb, root, system service or autostart.
set -eu
LAFA_SOURCE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
LAFA_ENV="$LAFA_SOURCE/.venv"
python3 -m venv "$LAFA_ENV"
"$LAFA_ENV/bin/python" -m pip install "$LAFA_SOURCE"
"$LAFA_ENV/bin/python" "$LAFA_SOURCE/scripts/create-launcher.py" "$LAFA_ENV/bin/lafa"
printf 'LAFA is installed. Run: %s/bin/lafa\n' "$LAFA_ENV"
