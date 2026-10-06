"""Read-only local tools and public research. No generated code execution."""
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlencode, quote, urlsplit
from html import unescape
from html.parser import HTMLParser
import os
import io
import stat
import tempfile
import re
import shutil
import subprocess
import time
import zipfile
import xml.etree.ElementTree as ET
from .net import json_request

KINDS = {
    "documents": {".pdf", ".txt", ".md", ".odt", ".doc", ".docx", ".rtf", ".xls", ".xlsx", ".ods", ".ppt", ".pptx", ".odp", ".csv"},
    "music": {".mp3", ".flac", ".ogg", ".wav", ".m4a", ".aac", ".opus"},
    "videos": {".mp4", ".mkv", ".avi", ".webm", ".mov", ".m4v"},
    "pictures": {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"},
}
RESOURCES = [
    ("Sources · encyclopedia directory", "https://www.sources.com/SSR/Docs/SSRW-Online_Encyclopedias_List.htm"),
    ("Wikipedia", "https://www.wikipedia.org/"),
    ("Britannica", "https://www.britannica.com/"),
    ("Wikibooks", "https://www.wikibooks.org/"),
    ("Wikiversity", "https://www.wikiversity.org/"),
    ("Khan Academy", "https://www.khanacademy.org/"),
    ("OpenStax", "https://openstax.org/"),
    ("Internet Archive", "https://archive.org/"),
    ("Ruangguru", "https://www.ruangguru.com/"),
    ("wikiHow", "https://www.wikihow.com/Main-Page"),
    ("Fandom", "https://www.fandom.com/"),
    ("Everything2", "https://everything2.com/"),
    ("Conservapedia", "https://www.conservapedia.com/Main_Page"),
    ("Miraheze", "https://miraheze.org/"),
    ("Baidu Baike", "https://baike.baidu.com/"),
]

@dataclass
class FileHit:
    path: str
    name: str
    kind: str
    size: int

@dataclass
class FileResults:
    hits: list = field(default_factory=list)
    limited: bool = False
    scanned: int = 0

@dataclass
class Source:
    title: str
    url: str
    text: str
    publisher: str = ""
    published: str = ""
    categories: tuple = ()

class FileSearch:
    def __init__(self, roots):
        self.roots = list(dict.fromkeys(Path(r).expanduser().resolve() for r in roots))
    def allowed(self, path):
        p = Path(path).expanduser().resolve()
        return any(p.is_relative_to(r) for r in self.roots) and not any(part.startswith(".") for part in p.parts[1:])
    def search(self, query, kind="all", limit=120, seconds=8):
        query = query.strip().casefold()
        words = query.split()
        result, started, seen = FileResults(), time.monotonic(), set()
        for root in self.roots:
            if not root.is_dir(): continue
            for directory, dirs, files in os.walk(root, followlinks=False):
                base = Path(directory)
                dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d not in {"node_modules", "venv", "__pycache__"} and not (base/d).is_symlink())
                if len(base.relative_to(root).parts) >= 10: dirs[:] = []
                for name in sorted(files):
                    result.scanned += 1
                    if time.monotonic()-started > seconds or result.scanned > 40_000:
                        result.limited = True
                        return result
                    if name.startswith(".") or not all(w in name.casefold() for w in words): continue
                    p = base / name
                    if p.is_symlink() or not self.allowed(p): continue
                    suffix = p.suffix.casefold()
                    if kind != "all" and suffix not in KINDS.get(kind, set()): continue
                    try:
                        if not p.is_file() or str(p) in seen: continue
                        hitkind = next((k for k, extensions in KINDS.items() if suffix in extensions), "all")
                        result.hits.append(FileHit(str(p), name, hitkind, p.stat().st_size))
                        seen.add(str(p))
                    except OSError: continue
                    if len(result.hits) >= limit:
                        result.limited = True
                        return result
        return result
    def read_bytes(self,path):
        # Resolve the selected root once, then traverse with directory FDs. No
        # symlinks or special files can be substituted during document access.
        p=Path(os.path.abspath(Path(path).expanduser()))
        root=next((r for r in sorted(self.roots,key=lambda r:len(r.parts),reverse=True) if p.is_relative_to(r)),None)
        if root is None or not self.allowed(p):raise ValueError('Document is outside your selected folders.')
        parts=p.relative_to(root).parts
        if not parts or any(part.startswith('.') for part in parts):raise ValueError('Choose a visible document.')
        if not hasattr(os,'O_NOFOLLOW'):raise ValueError('Secure document reading requires Linux O_NOFOLLOW support.')
        fd=None
        try:
            fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            for part in parts[:-1]:
                next_fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=next_fd
            next_fd=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd);os.close(fd);fd=next_fd
            info=os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_size>10_000_000:raise ValueError('Choose a regular document smaller than 10 MB.')
            with os.fdopen(fd,'rb') as stream:
                fd=None;raw=stream.read(10_000_001)
            if len(raw)>10_000_000:raise ValueError('Document size limit reached.')
            return raw,p.suffix.lower()
        except OSError as error:raise ValueError('Cannot securely open this document. Symlinks are not supported.') from error
        finally:
            if fd is not None:os.close(fd)
    def read(self, path, max_chars=20_000):
        raw,ext=self.read_bytes(path)
        max_chars=max(1,min(20000,int(max_chars)))
        if ext in {".txt", ".md", ".csv", ".html", ".htm"}:
            text = raw.decode("utf-8", errors="replace")
            if ext in {".html", ".htm"}: text = plain_html(text)
        elif ext in {".docx", ".odt"}:
            member = "word/document.xml" if ext == ".docx" else "content.xml"
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                info = archive.getinfo(member)
                if info.file_size > 10_000_000: raise ValueError("Document XML exceeds the size limit.")
                xml = archive.read(member)
            if b"<!DOCTYPE" in xml or b"<!ENTITY" in xml: raise ValueError("XML entities are not supported.")
            root = ET.fromstring(xml)
            paragraphs = ["".join(node.itertext()) for node in root.iter() if node.tag.split("}")[-1] in {"p", "h"}]
            text = "\n".join(paragraphs)
        elif ext == ".pdf":
            if not shutil.which("pdftotext"): raise ValueError("PDF reading needs poppler-utils (pdftotext).")
            with tempfile.TemporaryDirectory(prefix='lafa-pdf-') as folder:
                input_path=Path(folder)/'input.pdf';output_path=Path(folder)/'output.txt';input_path.write_bytes(raw)
                # The helper sets CPU, output file and address-space limits in
                # its own process, never preexec_fn in a multithreaded GUI.
                import sys
                result=subprocess.run([sys.executable,str(Path(__file__).with_name('pdf_worker.py')),str(input_path),str(output_path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=17,check=False)
                if result.returncode or not output_path.is_file():raise ValueError('Could not read this PDF within the resource limits.')
                with output_path.open('rb') as stream:text=stream.read(100000).decode('utf-8',errors='replace')
            if not text.strip(): raise ValueError("This PDF has no readable text; scanned PDFs need OCR.")
        else:
            raise ValueError("Reading supports TXT, MD, CSV, HTML, DOCX, ODT and text PDFs. Open other formats in their desktop application.")
        clipped = len(text) > max_chars
        return text[:max_chars] + ("\n\n[LAFA: text truncated]" if clipped else "")

class TextParser(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}: self.skip += 1
        if tag in {"p", "br", "div", "li"}: self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in {"script", "style"}: self.skip=max(0,self.skip-1)
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def plain_html(value):
    parser = TextParser(); parser.feed(value)
    return unescape("".join(parser.parts)).strip()

def encyclopedia_search(query, language="en"):
    lang = {"tet":"tet", "pt":"pt", "id":"id", "en":"en"}.get(language, "en")
    sources = wiki_search(query, lang)
    # Tetun and other smaller editions often have no article; English Wikipedia
    # is the explicit, labelled fallback (the URL shows which edition answered).
    if not sources and lang != "en": sources = wiki_search(query, "en")
    return sources

def wiki_search(query, lang):
    endpoint = f"https://{lang}.wikipedia.org/w/api.php"
    params = {"action":"query", "list":"search", "srsearch":query[:300], "srlimit":"6", "format":"json", "utf8":"1"}
    data = json_request(endpoint+"?"+urlencode(params), timeout=15)
    if data.get("error"): raise ValueError("Encyclopedia search could not complete.")
    sources=[]
    for item in data.get("query", {}).get("search", []):
        url = f"https://{lang}.wikipedia.org/wiki/" + quote(item["title"].replace(" ", "_"))
        sources.append(Source(item["title"], url, plain_html(item.get("snippet", ""))))
    return sources

def encyclopedia_article(source):
    parsed = urlsplit(source.url)
    if not re.fullmatch(r"(en|id|pt|tet)\.wikipedia\.org", parsed.hostname or ""):
        raise ValueError("Article reading supports the configured Wikipedia sources only.")
    params={"action":"query","prop":"extracts","explaintext":"1","exintro":"1","titles":source.title,"format":"json"}
    data=json_request(f"https://{parsed.hostname}/w/api.php?"+urlencode(params),timeout=15)
    text="\n".join(p.get("extract", "") for p in data.get("query", {}).get("pages", {}).values())[:12_000]
    if not text: raise ValueError("No readable article extract returned.")
    return text

def web_url(query, kind="all"):
    if kind == "videos": return "https://www.youtube.com/results?"+urlencode({"search_query":query})
    if kind == "music": return "https://archive.org/search?"+urlencode({"query":query,"and[]":"mediatype:audio"})
    if kind == "documents": query += " filetype:pdf"
    return "https://www.google.com/search?"+urlencode({"q":query})

RESOURCE_DOMAINS = {"ruangguru":"www.ruangguru.com","wikihow":"www.wikihow.com","fandom":"fandom.com","everything2":"everything2.com","conservapedia":"conservapedia.com","miraheze":"miraheze.org","baidu":"baike.baidu.com","baike":"baike.baidu.com"}

def resource_search_url(source,query):
    domain=RESOURCE_DOMAINS.get(source.casefold())
    if not domain:domain=next((urlsplit(url).hostname for name,url in RESOURCES if name.casefold()==source.casefold()),None)
    if not domain:raise ValueError("Unknown learning source.")
    return web_url("site:"+domain+" "+query.strip())
