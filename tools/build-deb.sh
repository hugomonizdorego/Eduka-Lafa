#!/bin/sh
# Build the LAFA .deb for Edukasaun OS (Debian 13 Trixie).
#   sh tools/build-deb.sh          -> dist/lafa_<version>_all.deb
# Install with apt so every dependency comes from the Debian repository:
#   sudo apt install ./dist/lafa_<version>_all.deb
# The version comes from lafa/__init__.py; packaging/DEBIAN/control must match
# (tools/release.py keeps them together).
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
VER=$(sed -n 's/^__version__ = "\(.*\)"/\1/p' "$ROOT/lafa/__init__.py")
CTRL=$(sed -n 's/^Version: *//p' "$ROOT/packaging/DEBIAN/control")
if [ "$VER" != "$CTRL" ]; then
    echo "Version mismatch: lafa/__init__.py=$VER packaging/DEBIAN/control=$CTRL" >&2
    exit 1
fi

OUT="$ROOT/dist"
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$OUT"

install -d "$STAGE/DEBIAN" "$STAGE/usr/bin" "$STAGE/usr/lib/lafa" "$STAGE/usr/share/applications" \
           "$STAGE/etc/xdg/autostart" "$STAGE/usr/share/eduka-settings/plugins" "$STAGE/usr/share/doc/lafa"
cp "$ROOT/packaging/DEBIAN/control" "$ROOT/packaging/DEBIAN/postinst" "$ROOT/packaging/DEBIAN/prerm" "$STAGE/DEBIAN/"
cp -r "$ROOT/lafa" "$STAGE/usr/lib/lafa/lafa"
cp "$ROOT/integration/eduka_lafa_settings.py" "$STAGE/usr/lib/lafa/"
cp "$ROOT/integration/lafa-page.json" "$STAGE/usr/share/eduka-settings/plugins/lafa.json"
cp "$ROOT/packaging/lafa" "$STAGE/usr/bin/lafa"
cp "$ROOT"/packaging/applications/*.desktop "$STAGE/usr/share/applications/"
cp "$ROOT/packaging/autostart/lafa-virtual.desktop" "$STAGE/etc/xdg/autostart/"
for size in 48 64 128 256; do
    install -D -m 0644 "$ROOT/packaging/icons/lafa-$size.png" "$STAGE/usr/share/icons/hicolor/${size}x${size}/apps/lafa.png"
done
{ cat "$ROOT/packaging/copyright"; echo; sed 's/^/ /' "$ROOT/LICENSE"; } > "$STAGE/usr/share/doc/lafa/copyright"
gzip -9n -c "$ROOT/CHANGELOG.md" > "$STAGE/usr/share/doc/lafa/changelog.gz"
cp "$ROOT/integration/eduka-settings-plugin-pages.patch" "$STAGE/usr/share/doc/lafa/"

find "$STAGE" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$STAGE" -name '*.pyc' -delete
find "$STAGE" -type d -exec chmod 0755 {} +
find "$STAGE" -type f -exec chmod 0644 {} +
chmod 0755 "$STAGE/usr/bin/lafa" "$STAGE/DEBIAN/postinst" "$STAGE/DEBIAN/prerm"

# Syntax-check every Python file before packaging.
find "$STAGE/usr/lib/lafa" "$STAGE/usr/bin" -type f \( -name '*.py' -o -name lafa \) -print | while read -r f; do
    python3 - "$f" <<'PY'
import ast, sys
ast.parse(open(sys.argv[1], encoding='utf-8').read(), sys.argv[1])
PY
done
for f in "$STAGE"/usr/share/applications/*.desktop "$STAGE"/etc/xdg/autostart/*.desktop; do
    command -v desktop-file-validate >/dev/null 2>&1 && desktop-file-validate "$f"
done

SIZE=$(du -sk --exclude=DEBIAN "$STAGE" | cut -f1)
sed -i "s/^Installed-Size:.*/Installed-Size: $SIZE/" "$STAGE/DEBIAN/control"
(cd "$STAGE" && find etc usr -type f -print0 | sort -z | xargs -0 md5sum > DEBIAN/md5sums)
chmod 0644 "$STAGE/DEBIAN/md5sums"

DEB="$OUT/lafa_${VER}_all.deb"
dpkg-deb --root-owner-group -Zxz --build "$STAGE" "$DEB"
echo "Built $DEB"
