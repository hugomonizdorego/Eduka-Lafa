#!/bin/sh
set -eu
LAFA_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$LAFA_ROOT"
if [ -x "$LAFA_ROOT/.venv/bin/python" ]; then
    exec "$LAFA_ROOT/.venv/bin/python" -m lafa.app "$@"
fi
exec python3 -m lafa.app "$@"
