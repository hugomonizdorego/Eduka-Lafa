#!/usr/bin/env python3
"""Worksheets for translating Lafa content (docs/CONTENT-SCHEMA.md).

Every text in the content files is an object {"tet", "pt", "en", "id"}.
This tool lists the texts that still miss a language and writes the
translations back without touching anything else.

    python3 tools/translate-sheet.py export lafa/assets/timor/content/sports.json > sheet.json
    # fill "en" and "id" in sheet.json (keep "path", "tet" and "pt" as they are)
    python3 tools/translate-sheet.py import lafa/assets/timor/content/sports.json sheet.json
    python3 tools/translate-sheet.py status                # what is missing, per file

Options for export: --langs en,id (default), --all (also texts already
translated, to review them), --item ID (only one article, place, day or
municipality).
"""
import argparse
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "lafa" / "assets" / "timor"
ORDER = ("tet", "pt", "en", "id")


def is_text(value):
    return (isinstance(value, dict) and value and set(value) <= set(ORDER) and "tet" in value
            and all(isinstance(v, str) for v in value.values()))


def texts(node, path=""):
    """(path, text object) for every text, in file order. Paths look like /articles/3/title."""
    if is_text(node):
        yield path, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from texts(value, f"{path}/{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from texts(value, f"{path}/{i}")


def item_of(data, path):
    """The id of the article/place/day/municipality a path belongs to."""
    parts = path.strip("/").split("/")
    if len(parts) >= 2 and isinstance(data.get(parts[0]), list):
        entry = data[parts[0]][int(parts[1])]
        if isinstance(entry, dict): return entry.get("id", "")
    return ""


def load(path):
    raw = Path(path).read_text(encoding="utf-8")
    return json.loads(raw), raw.endswith("\n")


def save(path, data, newline):
    text = json.dumps(data, ensure_ascii=False, indent=1) + ("\n" if newline else "")
    Path(path).write_text(text, encoding="utf-8")


def export(args):
    data, _ = load(args.file)
    langs = args.langs.split(",")
    rows = []
    for path, value in texts(data):
        if args.item and item_of(data, path) != args.item: continue
        if not args.all and all(value.get(l, "").strip() for l in langs): continue
        row = {"path": path, "item": item_of(data, path), "tet": value.get("tet", ""), "pt": value.get("pt", "")}
        for l in langs:
            if l != "pt": row[l] = value.get(l, "")
        rows.append(row)
    json.dump(rows, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write("\n")
    print(f"{len(rows)} texts", file=sys.stderr)


def resolve(data, path):
    node = data
    for part in path.strip("/").split("/"):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def import_(args):
    data, newline = load(args.file)
    rows = json.loads(Path(args.sheet).read_text(encoding="utf-8"))
    done = skipped = 0
    problems = []
    for row in rows:
        try:
            value = resolve(data, row["path"])
        except (KeyError, IndexError, ValueError):
            problems.append(f"{row['path']}: no such text"); continue
        # The source texts must be the ones that were exported: Tetun always,
        # Portuguese when the file has it (a sheet may also fill a missing one).
        if not is_text(value) or value.get("tet") != row.get("tet") or (value.get("pt", "").strip() and value.get("pt") != row.get("pt")):
            problems.append(f"{row['path']}: Tetun or Portuguese changed since export, skipped"); continue
        new = {l: row[l].strip() for l in ORDER[1:] if isinstance(row.get(l), str) and row[l].strip()
               and not (l == "pt" and value.get("pt", "").strip())}
        if not new:
            skipped += 1; continue
        merged = {**value, **new}
        value.clear()
        value.update({l: merged[l] for l in ORDER if l in merged})
        done += 1
    save(args.file, data, newline)
    for p in problems: print("!", p, file=sys.stderr)
    print(f"{done} texts written, {skipped} empty rows skipped, {len(problems)} problems", file=sys.stderr)
    return 1 if problems else 0


def status(args):
    total = {l: 0 for l in ORDER}
    files = sorted(glob.glob(str(CONTENT / "**" / "*.json"), recursive=True))
    # The Constitution exists officially in Tetun and Portuguese only; it is not translated.
    files = [f for f in files if Path(f).name not in ("constitution.json", "manifest.json")]
    for f in files:
        data, _ = load(f)
        counts = {l: 0 for l in ORDER}; n = 0
        for _, value in texts(data):
            n += 1
            for l in ORDER:
                if not value.get(l, "").strip(): counts[l] += 1
        if n and any(counts.values()):
            print(f"{Path(f).relative_to(CONTENT)}: {n} texts, missing " + ", ".join(f"{l} {c}" for l, c in counts.items() if c))
        for l in ORDER: total[l] += counts[l]
    print("missing in all files: " + ", ".join(f"{l} {c}" for l, c in total.items()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export"); e.add_argument("file"); e.add_argument("--langs", default="en,id")
    e.add_argument("--all", action="store_true"); e.add_argument("--item", default="")
    i = sub.add_parser("import"); i.add_argument("file"); i.add_argument("sheet")
    sub.add_parser("status")
    args = ap.parse_args()
    return {"export": export, "import": import_, "status": status}[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
