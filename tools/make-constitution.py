#!/usr/bin/env python3
"""Build lafa/assets/timor/constitution.json from the official texts of the
Constitution of the Democratic Republic of Timor-Leste (2002).

Sources (tools/sources/constitution/):
* Constituicao_RDTL_Portugues.pdf — Portuguese text (Jornal da República / Ministério da Justiça)
* Konstituisaun_RDTL_Tetun.pdf    — official Tetun edition (2010)

    python3 tools/make-constitution.py          # needs pdftotext (poppler-utils)

The text is kept as published (only page numbers, line breaks and the
typographic apostrophe are normalised). Structure: preamble, headings (parts,
titles, chapters, sections) and 170 articles with numbered paragraphs and
lettered items, aligned between the two languages by article number.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools" / "sources" / "constitution"
OUT = ROOT / "lafa" / "assets" / "timor" / "constitution.json"
FILES = {"pt": SRC / "Constituicao_RDTL_Portugues.pdf", "tet": SRC / "Konstituisaun_RDTL_Tetun.pdf"}

HEADINGS = [("part", re.compile(r"^PARTE\s+([IVXL]+)$")),
            ("title", re.compile(r"^T[ÍI]TUL[OU]\s+([IVXL]+)$")),
            ("chapter", re.compile(r"^(?:CAP[ÍI]TULO|KAP[ÍI]TULU)\s+([IVXL]+)$")),
            ("section", re.compile(r"^(?:SEC[ÇC][ÃA]O|SEKSAUN)\s+([IVXL]+)$"))]
LEVEL = {"part": 0, "title": 1, "chapter": 2, "section": 3}
ARTICLE = re.compile(r"^Artig[ou]\s+(\d+)\s*\.?\s*[º°˚oO]?\s*\.?$")
PREAMBLE = re.compile(r"^PRE[ÂÁA]MBUL[OU]$")
PARA = re.compile(r"^(\d{1,2})(?:\s*\.\s*|\s+)(\S.*)$")      # "1. Text", "1.Text" and "2 Text" all occur
ITEM = re.compile(r"^([a-z])\s*\)\s*(\S.*)$")

def pdf_lines(path):
    text = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"], check=True,
                          capture_output=True, text=True).stdout
    return text.replace("\f", "\n").replace("’", "'").replace("‘", "'").splitlines()

def join(a, b):
    """Join two text pieces from consecutive lines (a hyphen at the end keeps the compound)."""
    if not a: return b
    return a + b if a.endswith("-") else a + " " + b

def clean(s):
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,;:.)])", r"\1", s)          # "povu , ne'ebé" -> "povu, ne'ebé"
    return s.replace("( ", "(")

def parse(lines):
    # The body starts at the preamble heading (the table of contents comes before it).
    start = next(i for i, l in enumerate(lines) if PREAMBLE.match(l.strip()))
    preamble, headings, articles = [], [], []
    current = None            # the article being read
    pending = None            # heading waiting for its title line(s)
    stack = [None] * 4        # open heading index per level
    mode = "preamble"
    for raw in lines[start + 1:]:
        line = raw.strip()
        if not line or re.fullmatch(r"\d{1,3}", line): continue        # blank lines and page numbers
        indent = len(raw) - len(raw.lstrip(" "))
        kind = next(((k, m) for k, rx in HEADINGS for m in [rx.match(line)] if m), None)
        art = ARTICLE.match(line)
        if kind:
            k, m = kind; level = LEVEL[k]
            headings.append({"kind": k, "num": m.group(1), "title": "", "level": level})
            stack[level] = len(headings) - 1
            for deeper in range(level + 1, 4): stack[deeper] = None
            pending = headings[-1]; current = None; mode = "body"; continue
        if art:
            n = int(art.group(1))
            current = {"n": n, "title": "", "path": [i for i in stack if i is not None], "blocks": [], "open_title": True}
            articles.append(current); pending = None; mode = "body"; continue
        if pending is not None and current is None:
            # Heading titles are upper-case lines right after PARTE/TÍTULO/CAPÍTULO.
            if line.upper() == line and not PARA.match(line):
                pending["title"] = join(pending["title"], line); continue
            pending = None
        if mode == "preamble":
            if indent >= 4 or not preamble: preamble.append(line)
            else: preamble[-1] = join(preamble[-1], line)
            continue
        if current is None: continue
        if current["open_title"]:
            if not current["title"] and not line.startswith("("):
                current["open_title"] = False           # no title in brackets
            else:
                current["title"] = join(current["title"], line)
                if line.endswith(")"): current["open_title"] = False
                continue
        blocks = current["blocks"]
        p = PARA.match(line); it = ITEM.match(line)
        last_num = max([int(b["n"]) for b in blocks if b["n"]] or [0])
        if p and int(p.group(1)) == last_num + 1 and indent <= 12:
            blocks.append({"n": p.group(1), "text": p.group(2), "items": []}); continue
        if it and blocks is not None:
            if not blocks: blocks.append({"n": "", "text": "", "items": []})
            items = blocks[-1]["items"]
            expected = chr(ord(items[-1][0]) + 1) if items else "a"
            if it.group(1) == expected:
                items.append([it.group(1), it.group(2)]); continue
        if not blocks: blocks.append({"n": "", "text": line, "items": []}); continue
        if blocks[-1]["items"]: blocks[-1]["items"][-1][1] = join(blocks[-1]["items"][-1][1], line)
        else: blocks[-1]["text"] = join(blocks[-1]["text"], line)
    for h in headings: h["title"] = clean(h["title"])
    for a in articles:
        a["title"] = clean(a["title"]).strip("()").strip()
        for b in a["blocks"]:
            b["text"] = clean(b["text"]); b["items"] = [[l, clean(t)] for l, t in b["items"]]
        del a["open_title"]
    return [clean(p) for p in preamble], headings, articles

def main():
    parsed = {lang: parse(pdf_lines(path)) for lang, path in FILES.items()}
    pre_pt, heads_pt, arts_pt = parsed["pt"]; pre_tet, heads_tet, arts_tet = parsed["tet"]
    problems = []
    if [a["n"] for a in arts_pt] != list(range(1, 171)): problems.append("pt: articles are not 1–170")
    if [a["n"] for a in arts_tet] != list(range(1, 171)): problems.append("tet: articles are not 1–170")
    if [(h["kind"], h["num"]) for h in heads_pt] != [(h["kind"], h["num"]) for h in heads_tet]: problems.append("headings differ")
    if problems: sys.exit("constitution: " + "; ".join(problems))
    headings = [{"kind": hp["kind"], "num": hp["num"], "title": {"tet": ht["title"], "pt": hp["title"]}}
                for hp, ht in zip(heads_pt, heads_tet)]
    articles = []
    for ap, at in zip(arts_pt, arts_tet):
        if len(ap["blocks"]) != len(at["blocks"]): print(f"note: article {ap['n']}: {len(ap['blocks'])} pt / {len(at['blocks'])} tet paragraphs")
        articles.append({"n": ap["n"], "path": ap["path"], "title": {"tet": at["title"], "pt": ap["title"]},
                         "text": {"tet": at["blocks"], "pt": ap["blocks"]}})
    for h_i, h in enumerate(headings):
        h["first"] = next((a["n"] for a in articles if h_i in a["path"]), None)
    data = {
        "title": {"tet": "Konstituisaun Repúblika Demokrátika Timór-Leste", "pt": "Constituição da República Democrática de Timor-Leste"},
        "approved": "2002-03-22", "in_force": "2002-05-20",
        "note": {"tet": "Testu ofisiál. Iha divérjénsia ruma, testu portugés mak prevalese (Konstituisaun, artigu 13 no 159).",
                 "pt": "Texto oficial. Em caso de divergência, prevalece o texto em português."},
        "sources": [
            {"lang": "pt", "title": "Constituição da República Democrática de Timor-Leste", "publisher": "Ministério da Justiça — Jornal da República",
             "url": "https://www.mj.gov.tl/jornal/lawsTL/RDTL-Law/RDTL-Constitution-P.pdf", "file": FILES["pt"].name},
            {"lang": "tet", "title": "Konstituisaun Repúblika Demokrátika Timór-Leste (edisaun Tetun, 2010)", "publisher": "Repúblika Demokrátika Timór-Leste",
             "url": "https://www.mj.gov.tl/jornal/", "file": FILES["tet"].name}],
        "preamble": {"tet": pre_tet, "pt": pre_pt},
        "headings": headings, "articles": articles}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    words = sum(len(b["text"].split()) + sum(len(t.split()) for _, t in b["items"]) for a in articles for b in a["text"]["pt"])
    print(f"{OUT.relative_to(ROOT)}: {len(headings)} headings, {len(articles)} articles, {words} Portuguese words, {OUT.stat().st_size // 1024} KB")

if __name__ == "__main__":
    main()
