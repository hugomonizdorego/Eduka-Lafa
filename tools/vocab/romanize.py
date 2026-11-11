#!/usr/bin/env python3
"""Latin-letter readings ("rom") for the Lafa word lists written in non-Latin scripts.

    python3 tools/vocab/romanize.py            # write readings to tools/vocab/out/<lang>.json for review
    python3 tools/vocab/romanize.py --write    # also store "rom" and "rom_system" in lafa/assets/timor/vocab/<lang>.json
    python3 tools/vocab/romanize.py --lang km  # one language

Needs (pip): pypinyin jieba pythainlp tltk(+pandas nltk sklearn-crfsuite, imported without its
package __init__) indic-transliteration khmer-nltk laonlp.

zh  Hanyu Pinyin with tone marks: jieba words, pypinyin per word, manual fixes (overrides.json).
th  RTGS: pythainlp word tokens; TLTK th2roman, checked against pythainlp royin; manual fixes.
ta  ISO 15919: Tamil letters mapped one-to-one to Devanagari, then indic_transliteration -> ISO.
km  Simplified UNGEGN-style reading: own rules (two registers, clusters, finals), khmer-nltk words, manual fixes.
lo  Simplified BGN/PCGN (no diacritics, no tones): own syllable rules, laonlp words, manual fixes.
my  Common (informal) Burmese spelling: own syllable rules, voicing of common particles, manual fixes.
Readings keep separators (; , / ( ) …) and Latin text as in the original.
"""
import json, re, sys, os, types, logging, unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
VOCAB = REPO / "lafa" / "assets" / "timor" / "vocab"
OVR = json.loads((HERE / "overrides.json").read_text(encoding="utf-8")) if (HERE / "overrides.json").exists() else {}
for _folder in ("work", "out"): (HERE / _folder).mkdir(exist_ok=True)          # caches and review output (not in git)

SYSTEMS = {
    "zh": "Hanyu Pinyin with tone marks, one word per group (e.g. \"nǐ hǎo\"); citation tones, no tone-sandhi marks. Made automatically with jieba (word splitting) and pypinyin, then every entry checked by hand (neutral tones, readings of characters with two sounds). May contain errors.",
    "th": "Royal Thai General System (RTGS), words separated by spaces, no tones or vowel length (e.g. \"sawatdi\", \"khop khun\"). Made automatically with PyThaiNLP (royin) cross-checked with TLTK, differences fixed by hand; checked on common words. May contain errors.",
    "ta": "ISO 15919 transliteration, letter by letter (e.g. \"vaṇakkam\"): k c ṭ t p are written the same whether they sound voiced or not; ṉ ṟ ḻ ḷ are the Tamil letters ன ற ழ ள. Made automatically with indic_transliteration (Tamil letters taken one-to-one), checked on common words. May contain errors.",
    "km": "Simplified UNGEGN-style romanisation without diacritics, close to common spellings (e.g. \"suostei\", \"aw kun\", \"muoy, pir, bei\"); no vowel length. Made by our own rules (two consonant series, clusters, final consonants) with khmer-nltk word splitting, uroman only as a hint, then fixed by hand; checked on common words. Automatic, may contain errors.",
    "lo": "Simplified BGN/PCGN romanisation without diacritics or tones (e.g. \"sabaidi\", \"khop chai\"): ou = u, u = ɯ, x = ຊ, ny = ຍ, e = ເ and ແ. Made by our own syllable rules with laonlp word splitting, uroman only as a hint, then fixed by hand; checked on common words. Automatic, may contain errors.",
    "my": "Common Burmese romanisation without tones, one syllable per group (e.g. \"mingalaba\", \"kyei zu tin ba de\"), with the usual voicing of particles (ba, de, ga…). Made by our own syllable rules, uroman only as a hint, then fixed by hand; checked on common words. Automatic, may contain errors.",
}

# ----------------------------------------------------------------------------- common text handling
PUNCT = {"；": ";", "，": ",", "、": ",", "（": "(", "）": ")", "？": "?", "！": "!", "：": ":", "。": ".", "“": "\"",
         "”": "\"", "‘": "'", "’": "'", "……": "…", "၊": ",", "။": ".", "។": ".", "៖": ":", "ฯ": "", "ຯ": "…"}


def tidy(s):
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([;,.!?:)])", r"\1", s)
    s = re.sub(r"(^|\()…\s+", r"\1…", s)                  # "…ဖို့" -> "…pho"
    s = re.sub(r"\s+…($|\))", r"…\1", s)
    s = re.sub(r"([(\"“])\s+", r"\1", s)
    s = re.sub(r"([;,!?:])(?=[^\s)\"'…,;.!?:])", r"\1 ", s)
    s = re.sub(r"(\w)\(", r"\1 (", s)
    s = re.sub(r"\)(\w)", r") \1", s)
    s = re.sub(r"(^|[\s(])'\s+([^']+?)\s+'", r"\1'\2'", s)
    return unicodedata.normalize("NFC", s)


def split_runs(text, is_native):
    """[(native?, chunk)] keeping order."""
    runs = []
    for ch in text:
        nat = is_native(ch)
        if runs and runs[-1][0] == nat: runs[-1][1] += ch
        else: runs.append([nat, ch])
    return [(n, c) for n, c in runs]


def map_punct(s):
    s = s.replace("……", "…")
    return "".join(PUNCT.get(ch, ch) for ch in s)


# ----------------------------------------------------------------------------- Chinese
_jieba = None


def zh_reading(text):
    global _jieba
    import jieba
    from pypinyin import lazy_pinyin, Style
    if _jieba is None:
        jieba.setLogLevel(logging.WARNING)
        for w in OVR.get("zh_words", {}): jieba.add_word(w, 10 ** 6)
        _jieba = jieba
    words = OVR.get("zh_words", {})
    out = []
    for nat, chunk in split_runs(text, lambda c: "一" <= c <= "鿿" or c in "〇"):
        if not nat:
            out.append(" " + map_punct(chunk) + " "); continue
        for w in _jieba.cut(chunk, HMM=False):
            if w in words:
                out.append(" " + words[w] + " "); continue
            syl = lazy_pinyin(w, style=Style.TONE, neutral_tone_with_five=False)
            # citation tones for 一 and 不 (pypinyin's phrase data marks their tone sandhi)
            syl = ["yī" if ch == "一" else "bù" if ch == "不" and s in ("bú", "bù") else s for ch, s in zip(w, syl)] if len(syl) == len(w) else syl
            joined = ""
            for k, s in enumerate(syl):
                if k and s[:1] in "aāáǎàoōóǒòeēéěè": joined += "'"
                joined += s
            out.append(" " + joined + " ")
    return tidy("".join(out))


# ----------------------------------------------------------------------------- Thai
_tl = None


def _tltk():
    global _tl
    if _tl is None:
        pkg = types.ModuleType("tltk"); pkg.__path__ = [str(Path(sys.prefix) / "lib" / f"python{sys.version_info[0]}.{sys.version_info[1]}" / "site-packages" / "tltk")]
        sys.modules["tltk"] = pkg
        import tltk.nlp as nlp
        _tl = nlp
    return _tl


_th_cache = {}
_TH_RAW_PATH = HERE / "work" / "th_raw_cache.json"
_th_raw = {k: v for k, v in (json.loads(_TH_RAW_PATH.read_text(encoding="utf-8")) if _TH_RAW_PATH.exists() else {}).items() if len(v) == 3}


def _th_raw_pair(w):
    """(royin, tltk) readings of one Thai word, cached on disk because TLTK is slow."""
    if w not in _th_raw:
        from pythainlp.transliterate import romanize
        r = romanize(w, engine="royin")
        try: k = _tltk().th2roman(w).replace("<s/>", "").strip()
        except Exception: k = ""
        _th_raw[w] = [r, k.replace(" ", ""), 1]
    return _th_raw[w][:2]


def th_word(w):
    """RTGS for one Thai word: TLTK, cross-checked with royin; flagged when they disagree."""
    if w in _th_cache: return _th_cache[w]
    words = OVR.get("th_words", {})
    if w in words:
        _th_cache[w] = (words[w], "override"); return _th_cache[w]
    r, k = _th_raw_pair(w)
    k0 = k.replace("-", "")
    if k and r == k0: res = (k, "agree")
    elif k and re.fullmatch(r"[a-z-]+", k) and len(k0) >= 0.7 * len(re.sub(r"[^a-z]", "", r)): res = (k, "tltk")
    else: res = (re.sub(r"[^a-z]", "", r), "royin?")
    _th_cache[w] = res
    return res


_th_dict = None


def th_split(w):
    """Split a long compound token into dictionary words when the reading of the parts equals the reading of the whole."""
    global _th_dict
    from pythainlp.tokenize import syllable_tokenize
    from pythainlp.corpus import thai_words
    if w in OVR.get("th_words", {}) or w in OVR.get("th_keep", []): return [w]
    nsyl = len(syllable_tokenize(w))
    if nsyl < 2: return [w]
    if _th_dict is None:
        from pythainlp.corpus import tnc
        _th_dict = set(thai_words()); globals()["_th_freq"] = dict(tnc.word_freqs())
    n = len(w)
    best = [None] * (n + 1); best[0] = []
    for i in range(n):
        if best[i] is None: continue
        for j in range(i + 2, n + 1):
            p = w[i:j]
            if p == w or p not in _th_dict: continue
            if best[j] is None or len(best[i]) + 1 < len(best[j]): best[j] = best[i] + [p]
    parts = best[n]
    if not parts or len(parts) < 2: return [w]
    freq = globals()["_th_freq"]
    if any(freq.get(p, 0) < (2500 if nsyl == 2 else 300) for p in parts): return [w]
    whole = th_word(w)[0]
    if "".join(th_word(p)[0] for p in parts).replace("-", "") != whole.replace("-", ""): return [w]
    out = []
    for p in parts: out += th_split(p)
    return out


TH_FLAGS = {}


_th_trie = None


def th_reading(text, wid=None):
    global _th_trie
    from pythainlp.tokenize import word_tokenize
    if _th_trie is None:
        from pythainlp.corpus import thai_words
        from pythainlp.util import Trie
        _th_trie = Trie(set(thai_words()) | set(OVR.get("th_words", {})))
    out = []
    prev = ""
    for nat, chunk in split_runs(text, lambda c: "฀" <= c <= "๿" and c not in "ฯ"):
        if not nat:
            out.append(" " + map_punct(chunk) + " "); continue
        for tok in word_tokenize(chunk, custom_dict=_th_trie, engine="newmm", keep_whitespace=False):
            if tok == "ๆ":
                out.append(" " + prev + " "); continue
            tok = tok.replace("ๆ", "")
            parts = []
            for p in th_split(tok):
                rom, how = th_word(p)
                if how not in ("agree", "override"): TH_FLAGS.setdefault(p, (rom, how, wid))
                parts.append(rom)
            prev = " ".join(parts)
            out.append(" " + prev + " ")
    return tidy("".join(out))


# ----------------------------------------------------------------------------- Tamil
TA2DEV = dict(zip("அஆஇஈஉஊஎஏஐஒஓஔகஙசஞடணதநபமயரலவழளறனஜஷஸஹஶாிீுூெேைொோௌ்ஃ",
                  "अआइईउऊऎएऐऒओऔकङचञटणतनपमयरलवऴळऱऩजषसहशािीुूॆेैॊोौ्ः"))


def ta_reading(text):
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate
    out = []
    for nat, chunk in split_runs(text, lambda c: "஀" <= c <= "௿"):
        if not nat:
            out.append(map_punct(chunk)); continue
        dev = "".join(TA2DEV.get(c, c) for c in unicodedata.normalize("NFC", chunk))
        iso = transliterate(dev, sanscript.DEVANAGARI, sanscript.ISO)
        iso = iso.replace("ḥ", "ḵ")          # Tamil āytam ஃ
        out.append(iso)
    return tidy("".join(out))


# ----------------------------------------------------------------------------- Khmer
KM_C = {"ក": ("k", "A"), "ខ": ("kh", "A"), "គ": ("k", "O"), "ឃ": ("kh", "O"), "ង": ("ng", "O"),
        "ច": ("ch", "A"), "ឆ": ("chh", "A"), "ជ": ("ch", "O"), "ឈ": ("chh", "O"), "ញ": ("nh", "O"),
        "ដ": ("d", "A"), "ឋ": ("th", "A"), "ឌ": ("d", "O"), "ឍ": ("th", "O"), "ណ": ("n", "A"),
        "ត": ("t", "A"), "ថ": ("th", "A"), "ទ": ("t", "O"), "ធ": ("th", "O"), "ន": ("n", "O"),
        "ប": ("b", "A"), "ផ": ("ph", "A"), "ព": ("p", "O"), "ភ": ("ph", "O"), "ម": ("m", "O"),
        "យ": ("y", "O"), "រ": ("r", "O"), "ល": ("l", "O"), "វ": ("v", "O"), "ឝ": ("s", "A"), "ឞ": ("s", "A"),
        "ស": ("s", "A"), "ហ": ("h", "A"), "ឡ": ("l", "A"), "អ": ("", "A")}
KM_SON = set("ងញណនមយរលវ")
KM_NASAL = set("ងញណនម")
KM_FIN = {"ក": "k", "ខ": "k", "គ": "k", "ឃ": "k", "ង": "ng", "ច": "ch", "ឆ": "ch", "ជ": "ch", "ឈ": "ch", "ញ": "nh",
          "ដ": "t", "ឋ": "t", "ឌ": "t", "ឍ": "t", "ណ": "n", "ត": "t", "ថ": "t", "ទ": "t", "ធ": "t", "ន": "n",
          "ប": "p", "ផ": "p", "ព": "p", "ភ": "p", "ម": "m", "យ": "y", "រ": "r", "ល": "l", "វ": "v", "ឝ": "s",
          "ឞ": "s", "ស": "s", "ហ": "h", "ឡ": "l", "អ": ""}
KM_IV = {"ឣ": "a", "ឤ": "a", "ឥ": "e", "ឦ": "ei", "ឧ": "o", "ឨ": "o", "ឩ": "o", "ឪ": "ov", "ឫ": "rue", "ឬ": "rue",
         "ឭ": "lue", "ឮ": "leu", "ឯ": "ae", "ឰ": "ai", "ឱ": "ao", "ឲ": "ao", "ឳ": "au"}
KM_DV = set("ាិីឹឺុូួើឿៀេែៃោៅ")
KM_V = {"": ("a", "o"), "ា": ("a", "ea"), "ិ": ("e", "i"), "ី": ("ei", "i"), "ឹ": ("eu", "eu"), "ឺ": ("eu", "eu"),
        "ុ": ("o", "u"), "ូ": ("o", "u"), "ួ": ("uo", "uo"), "ើ": ("ae", "eu"), "ឿ": ("eua", "eua"), "ៀ": ("ie", "ie"),
        "េ": ("e", "e"), "ែ": ("ae", "ae"), "ៃ": ("ai", "ey"), "ោ": ("ao", "o"), "ៅ": ("au", "ov"),
        "ុំ": ("om", "um"), "ំ": ("am", "um"), "ាំ": ("am", "oam"), "ិំ": ("em", "im"), "ះ": ("ah", "eah"),
        "ុះ": ("oh", "uh"), "េះ": ("eh", "eh"), "ោះ": ("aoh", "uoh"), "ិះ": ("eh", "ih"), "ឹះ": ("euh", "euh"),
        "ែះ": ("aeh", "aeh"), "ាះ": ("ah", "eah"), "ៀះ": ("ieh", "ieh"), "ួះ": ("uoh", "uoh"), "ៈ": ("a", "ea"),
        "័": ("a", "oa"), "ោំ": ("aom", "om"), "ាៈ": ("a", "ea"), "ុៈ": ("o", "u"), "េៈ": ("e", "e")}


def km_units(run):
    units, i, n = [], 0, len(run)
    while i < n:
        ch = run[i]
        if ch in KM_C or ch in KM_IV:
            u = dict(base=ch, subs=[], shift="", v="", sign="", bantoc=False, silent=False, robat=False, iv=ch in KM_IV)
            i += 1
            while i < n:
                c = run[i]
                if c in "៉៊": u["shift"] = c; i += 1
                elif c == "្" and i + 1 < n and run[i + 1] in KM_C: u["subs"].append(run[i + 1]); i += 2
                elif c in KM_DV and not u["v"]: u["v"] = c; i += 1
                elif c in "ំះៈ": u["sign"] += c; i += 1
                elif c == "់": u["bantoc"] = True; i += 1
                elif c == "៍": u["silent"] = True; i += 1
                elif c == "៌": u["robat"] = True; i += 1
                elif c == "័": u["sign"] += "័"; i += 1
                elif c in "៏៎៑៓​‌‍": i += 1
                else: break
            units.append(u)
        else:
            i += 1
    return units


def km_has_v(u): return bool(u["v"] or u["sign"] or u["iv"])


def km_reg(u, prev=None):
    reg = KM_C[u["base"]][1] if u["base"] in KM_C else "A"
    nonson = [s for s in u["subs"] if s not in KM_SON]
    if nonson: reg = KM_C[nonson[-1]][1]
    elif u["subs"] and u["base"] in KM_NASAL and prev is not None and prev.get("role") == "onset" and not prev.get("fin") and not prev["sign"]:
        reg = "A" if km_reg(prev) == 0 else "O"
    if u["shift"] == "៉": reg = "A"
    if u["shift"] == "៊": reg = "O"
    return 0 if reg == "A" else 1


def km_word(word):
    us = [u for u in km_units(word)]
    if not us: return ""
    for u in us: u["role"] = None; u["fin"] = None
    live = [u for u in us if not u["silent"]]
    # Pali words: final Ci / Cu is silent (ជាតិ cheat, ហេតុ haet, ប្រវត្តិ pravot)
    if len(live) >= 2:
        last, pv = live[-1], live[-2]
        if last["v"] in ("ិ", "ុ") and not last["sign"] and not last["bantoc"] and not last["iv"] and (
                (pv["v"] in ("ា", "េ", "ោ", "ៀ") and not pv["sign"]) or (not km_has_v(pv) and last["subs"])):
            last["v"] = ""
    # roles
    for k, u in enumerate(live):
        if u["robat"] and not km_has_v(u): u["role"] = "robat"
        elif u["bantoc"] and not km_has_v(u) and k > 0: u["role"] = "final"
    k = 0
    while k < len(live):
        if live[k]["role"] or km_has_v(live[k]): k += 1; continue
        a = k
        while k < len(live) and not live[k]["role"] and not km_has_v(live[k]): k += 1
        seg = live[a:k]
        at_end = k == len(live)
        prev = live[a - 1] if a > 0 else None
        prev_open = prev is not None and km_has_v(prev) and not prev["sign"] and prev["v"] not in ("ៃ", "ៅ") and not prev["iv"] or (prev is not None and prev["iv"] and prev["base"] in "ឯឱឪ")
        if len(seg) == 1 and prev is not None and prev["sign"] == "ំ" and prev["v"] == "ា" and seg[0]["base"] == "ង" and not seg[0]["subs"]:
            seg[0]["role"] = "final"; continue
        # a lone consonant before a nasal-initial cluster is an open pre-syllable (ទម្លាប់ tomloap, សម្រាប់ samrap)
        if not at_end and len(seg) >= 2 and not seg[-1]["subs"] and live[k]["subs"] and live[k]["base"] in KM_NASAL:
            seg[-1]["role"] = "onset"; seg = seg[:-1]
            if len(seg) == 1 and prev_open and not prev.get("fin"):
                seg[0]["role"] = "final"; continue
        if len(seg) == 1 and prev_open and not prev.get("fin"):
            seg[0]["role"] = "final"; continue
        j = 0
        while j < len(seg):
            u = seg[j]
            last = j == len(seg) - 1
            if u["subs"] and not (last and at_end):
                u["role"] = "onset"
                if j + 1 == len(seg) - 1 and not seg[j + 1]["subs"] and not at_end:   # អ្នក|ស្ដាប់ neak sdap
                    seg[j + 1]["role"] = "final"; j += 2; continue
                j += 1; continue
            if last and at_end and j > 0 and seg[j - 1]["role"] == "onset":
                u["role"] = "final"; j += 1; continue
            if last and at_end and j == 0 and prev is not None and not prev.get("fin") and (not prev["sign"] or prev["sign"] == "័"):
                u["role"] = "final"; j += 1; continue
            if j + 1 < len(seg) and (not seg[j + 1]["subs"] or (j + 1 == len(seg) - 1 and at_end)):
                u["role"] = "onset"; seg[j + 1]["role"] = "final"; j += 2; continue
            u["role"] = "onset"; j += 1
    out, cur = [], None
    for k, u in enumerate(live):
        if u["role"] in ("final", "robat") and cur is not None:
            cur["fin"] = u; continue
        u["role"] = u["role"] or "onset"
        cur = u; out.append(u)
    return join_syllables([km_syll(u, out[k - 1] if k else None) for k, u in enumerate(out)])


def km_syll(u, prev):
    f = u.get("fin")
    if u["iv"]:
        s = KM_IV[u["base"]] + "".join(KM_C[x][0] for x in u["subs"]) + (KM_FIN.get(f["base"], "") if f and f["role"] != "robat" else ("r" if f else ""))
        return s
    reg = km_reg(u, prev)
    base = u["base"]
    ini = KM_C[base][0]
    if base == "អ" and u["subs"]: ini = "a"
    if base == "ប" and (u["subs"] or u["shift"] == "៉"): ini = "p"
    subs = list(u["subs"])
    if subs and subs[0] == base and base in "បញ":   # geminate written once: សប្បាយ sabay, សញ្ញា sanha
        ini = KM_C[base][0]; subs = subs[1:]
    for s in subs:
        ini += "'" if s == "អ" else KM_C[s][0]
    key = u["v"] + u["sign"]
    fin = ""
    if f is not None:
        fin = "r" if f["role"] == "robat" else KM_FIN.get(f["base"], "")
    if key == "ាំ" and f is not None and f["base"] == "ង": key = "ា"
    if key not in KM_V: key = u["v"] if u["v"] in KM_V else ""
    vow = KM_V[key][reg]
    if f is not None and f.get("bantoc"):
        if key == "ា": vow = ("a", "oa")[reg]
        elif key == "": vow = ("a", "o")[reg]
        elif key == "ិ": vow = ("e", "i")[reg]
        elif key == "ុ": vow = ("o", "u")[reg]
        elif key == "េ": vow = ("e", "e")[reg]
    if key == "័" and f is not None and f["base"] == "យ": vow, fin = "ai", ""
    if fin == "y" and vow.endswith(("y", "i")): fin = ""
    if fin == "v" and vow.endswith("v"): fin = ""
    return ini + vow + fin


_km_tok = None


def km_reading(text):
    global _km_tok
    if _km_tok is None:
        import logging as lg
        lg.disable(lg.INFO)
        from khmernltk import word_tokenize
        _km_tok = word_tokenize
    words = OVR.get("km_words", {})
    out, prev = [], ""
    for nat, chunk in split_runs(text, lambda c: "ក" <= c <= "៿" and c not in "។៖ៗ" and not ("០" <= c <= "៩")):
        if not nat:
            for ch in chunk:
                if ch == "ៗ": out.append(" " + prev + " ")
                elif "០" <= ch <= "៩": out.append(str(ord(ch) - 0x17e0))
                else: out.append(map_punct(ch))
            continue
        toks = [t for t in _km_tok(chunk) if t.strip()]
        # merge tokens that form an override phrase
        k = 0
        while k < len(toks):
            done = False
            for L in range(min(5, len(toks) - k), 1, -1):
                ph = "".join(toks[k:k + L])
                if ph in words:
                    toks[k:k + L] = [ph]; done = True; break
            k += 1
        for t in toks:
            r = words.get(t)
            if r is None: r = km_word(t)
            prev = r
            out.append(" " + r + " ")
    return tidy("".join(out))


# ----------------------------------------------------------------------------- Lao
LO_C = {"ກ": "k", "ຂ": "kh", "ຄ": "kh", "ງ": "ng", "ຈ": "ch", "ສ": "s", "ຊ": "x", "ຍ": "ny", "ດ": "d", "ຕ": "t",
        "ຖ": "th", "ທ": "th", "ນ": "n", "ບ": "b", "ປ": "p", "ຜ": "ph", "ຝ": "f", "ພ": "ph", "ຟ": "f", "ມ": "m",
        "ຢ": "y", "ຣ": "r", "ລ": "l", "ວ": "v", "ຫ": "h", "ອ": "", "ຮ": "h", "ໜ": "n", "ໝ": "m", "ຆ": "kh",
        "ຉ": "ch", "ຌ": "ch", "ຎ": "ny", "ຏ": "t", "ຐ": "th", "ຑ": "th", "ຒ": "th", "ຓ": "n", "ຘ": "th",
        "ຠ": "ph", "ຨ": "s", "ຩ": "s", "ຬ": "l"}
LO_F = {"ກ": "k", "ງ": "ng", "ດ": "t", "ນ": "n", "ບ": "p", "ມ": "m", "ຍ": "y", "ວ": "o", "ສ": "s", "ລ": "l",
        "ຣ": "r", "ຟ": "f", "ຊ": "s", "ຕ": "t", "ປ": "p", "ທ": "t", "ຄ": "k", "ພ": "p", "ຂ": "k", "ຈ": "t",
        "ຖ": "t", "ຜ": "p", "ຢ": "y"}
LO_UPPER = set("ັິີຶືຸູົໍ")
LO_TONE = set("່້໊໋")
LO_POSTV = set("ະາຳຽ")


def lo_syllables(w):
    """All parses of a Lao word into (initial, nucleus, final) syllables; returns romanised syllables of the best parse."""
    n = len(w)
    memo = {}

    def initial_at(i, pre=""):
        """Candidates (rom, next_i) for an initial consonant group starting at i."""
        if i >= n or w[i] not in LO_C: return []
        c = w[i]; rom = LO_C[c]; i += 1
        if c == "ຫ" and i < n and w[i] in "ງຍນມລຣວ":
            nxt = w[i + 1] if i + 1 < n else ""
            if not (w[i] == "ວ" and (nxt in LO_F and nxt != "ວ" or nxt == "")):
                rom = LO_C[w[i]]; i += 1
        if i < n and w[i] == "ຼ": rom = ("" if c == "ຫ" else rom) + "l"; i += 1
        out = [(rom, i, 0)]
        nxt = w[i + 1] if i + 1 < n else ""
        if i < n and w[i] == "ວ" and c not in "ອຫ":
            if nxt and (nxt in LO_UPPER and nxt != "ົ" or nxt in "ະາຳ" or nxt in LO_TONE and i + 2 < n and (w[i + 2] in "ະາຳ" or w[i + 2] in LO_UPPER)):
                out = [(rom + "ou", i + 1, 0)]
            elif pre and nxt in LO_F:
                out.append((rom + "ou", i + 1, 1))
        if i < n and w[i] in "ຣລ" and c in "ກຂຄປຜພຕທບດຟສ" and nxt and (nxt in LO_UPPER or nxt in "ະາຳ" or nxt in LO_TONE):
            out.append((rom + LO_C[w[i]], i + 1, 0))
        return out

    def syl(i):
        """List of (rom, next_i) for syllables starting at i."""
        res = []
        pre = ""
        j = i
        if j < n and w[j] in "ເແໂໄໃ": pre = w[j]; j += 1
        for irom, j0, pen in initial_at(j, pre):
            res += syl_from(irom, j0, pre, pen)
        return res

    def syl_from(irom, j, pre, pen):
        res = []
        marks = ""
        while j < n and (w[j] in LO_UPPER or w[j] in LO_TONE or w[j] == "໌"):
            marks += w[j]; j += 1
        vm = "".join(c for c in marks if c in LO_UPPER)
        cands = []  # (nucleus_rom, next_j, can_take_final)

        def nxt(k): return w[k] if k < n else ""
        if pre == "":
            if vm == "ັ":
                if nxt(j) == "ວ": cands.append(("oua", j + 1, True))
                elif nxt(j) == "ອ": cands.append(("o", j + 1, True))
                cands.append(("a", j, True))
            elif vm in ("ິ", "ີ"): cands.append(("i", j, True))
            elif vm in ("ຶ", "ື"):
                if nxt(j) == "ອ": cands.append(("u", j + 1, True))
                cands.append(("u", j, True))
            elif vm in ("ຸ", "ູ"): cands.append(("ou", j, True))
            elif vm == "ົ":
                if nxt(j) == "ວ": cands.append(("oua", j + 1, True))
                else: cands.append(("o", j, True))
            elif vm == "ໍ": cands.append(("o", j, False))
            elif vm == "":
                c = nxt(j)
                if c == "ະ": cands.append(("a", j + 1, False))
                elif c == "າ": cands.append(("a", j + 1, True))
                elif c == "ຳ": cands.append(("am", j + 1, False))
                elif c == "ອ": cands.append(("o", j + 1, True))
                elif c == "ວ": cands.append(("oua", j + 1, True))
                elif c == "ຽ": cands.append(("ia", j + 1, True))
                else: cands.append(("o", j, True)); pen += 3  # no written vowel (old spelling)
        elif pre == "ເ":
            if vm == "ັ":
                if nxt(j) == "ຍ": cands.append(("ia", j + 1, False))
                cands.append(("e", j, True))
            elif vm in ("ິ", "ີ"): cands.append(("eu", j, True))
            elif vm in ("ຶ", "ື"):
                if nxt(j) == "ອ": cands.append(("ua", j + 1, True))
                else: cands.append(("u", j, True))
            elif vm == "ົ" and nxt(j) == "າ": cands.append(("ao", j + 1, False))
            elif vm == "":
                c = nxt(j)
                if c == "າ" and nxt(j + 1) == "ະ": cands.append(("o", j + 2, False))
                elif c == "ະ": cands.append(("e", j + 1, False))
                elif c == "ຍ": cands.append(("ia", j + 1, False))
                elif c == "ົ" and nxt(j + 1) == "າ": cands.append(("ao", j + 2, False))
                cands.append(("e", j, True))
        elif pre == "ແ":
            if vm == "ັ": cands.append(("e", j, True))
            elif vm == "":
                if nxt(j) == "ະ": cands.append(("e", j + 1, False))
                cands.append(("e", j, True))
        elif pre == "ໂ":
            if vm == "":
                if nxt(j) == "ະ": cands.append(("o", j + 1, False))
                cands.append(("o", j, True))
        elif pre in "ໄໃ":
            if vm == "": cands.append(("ai", j, False))
        for nuc, k, can_fin in cands:
            # optional final consonant
            if can_fin and k < n and w[k] in LO_F:
                after = w[k + 1] if k + 1 < n else ""
                if not after or not (after in LO_UPPER or after in LO_TONE or after in "ະາຳຽ" or after == "໌"):
                    fin = w[k]
                    frm = LO_F[fin]
                    if fin == "ຍ": frm = {"a": "i", "oua": "y", "o": "y", "ou": "y", "eu": "y", "u": "y"}.get(nuc, "y")
                    if fin == "ວ": frm = "o" if nuc not in ("i",) else "o"
                    k2 = k + 1
                    if k2 < n and w[k2] == "໌": k2 += 1; frm = ""
                    res.append((irom + nuc + frm, k2, pen))
            res.append((irom + nuc, k, pen))
        return res

    def parse(i):
        if i == n: return ([], 0)
        if i in memo: return memo[i]
        best = None
        for rom, k, pen in syl(i):
            if k <= i: continue
            rest = parse(k)
            if rest is None: continue
            cand = ([rom] + rest[0], 1 + pen + rest[1])
            if best is None or cand[1] < best[1]: best = cand
        if best is None and i < n:
            rest = parse(i + 1)          # skip a stray character
            best = None if rest is None else (rest[0], rest[1] + 5)
        memo[i] = best
        return best
    if n == 0: return []
    r = parse(0)
    return r[0] if r else []


def join_syllables(parts):
    out = ""
    for p in parts:
        if out and p[:1] in "aeiou" and out[-1:] in "aeiou": out += "-"
        out += p
    return out


def lo_word(w):
    return join_syllables(lo_syllables(w))


_lo_dict = None


def lo_split(w):
    """A token of 3+ syllables made of dictionary words is written as separate words (ລົດໂຮງໝໍ lot hongmo)."""
    global _lo_dict
    if _lo_dict is None:
        from laonlp.corpus import lao_words
        _lo_dict = set(lao_words()) | set(OVR.get("lo_words", {}))
    if len(lo_syllables(w)) < 3 or w in OVR.get("lo_keep", []): return [w]
    n = len(w); best = [None] * (n + 1); best[0] = []
    for i in range(n):
        if best[i] is None: continue
        for j in range(i + 1, n + 1):
            p = w[i:j]
            if p != w and p in _lo_dict and (best[j] is None or len(best[i]) + 1 < len(best[j])): best[j] = best[i] + [p]
    parts = best[n]
    if not parts or len(parts) < 2 or "".join(lo_syllables(w)) != "".join("".join(lo_syllables(p)) for p in parts): return [w]
    return parts


_lo_tok = None


def lo_reading(text):
    global _lo_tok
    if _lo_tok is None:
        from laonlp.tokenize import word_tokenize
        _lo_tok = word_tokenize
    words = OVR.get("lo_words", {})
    out, prev = [], ""
    for nat, chunk in split_runs(text, lambda c: "຀" <= c <= "໿" and c not in "ໆຯ" and not ("໐" <= c <= "໙")):
        if not nat:
            for ch in chunk:
                if ch == "ໆ": out.append(" " + prev + " ")
                elif "໐" <= ch <= "໙": out.append(str(ord(ch) - 0x0ed0))
                else: out.append(map_punct(ch))
            continue
        toks = [t for t in _lo_tok(chunk) if t.strip()]
        k = 0
        while k < len(toks):
            for L in range(min(5, len(toks) - k), 1, -1):
                ph = "".join(toks[k:k + L])
                if ph in words: toks[k:k + L] = [ph]; break
            k += 1
        for t in toks:
            r = words.get(t)
            if r is None: r = " ".join(words.get(p) or lo_word(p) for p in lo_split(t))
            prev = r
            out.append(" " + r + " ")
    return tidy("".join(out))


# ----------------------------------------------------------------------------- Burmese
MY_C = {"က": "k", "ခ": "kh", "ဂ": "g", "ဃ": "g", "င": "ng", "စ": "s", "ဆ": "hs", "ဇ": "z", "ဈ": "z", "ည": "ny",
        "ဋ": "t", "ဌ": "ht", "ဍ": "d", "ဎ": "d", "ဏ": "n", "တ": "t", "ထ": "ht", "ဒ": "d", "ဓ": "d", "န": "n",
        "ပ": "p", "ဖ": "ph", "ဗ": "b", "ဘ": "b", "မ": "m", "ယ": "y", "ရ": "y", "လ": "l", "ဝ": "w", "သ": "th",
        "ဟ": "h", "ဠ": "l", "အ": "", "ဿ": "th"}
MY_IV = {"ဣ": "i", "ဤ": "i", "ဥ": "u", "ဦ": "u", "ဧ": "ei", "ဩ": "aw", "ဪ": "aw"}
MY_FCLASS = {"က": "k", "ခ": "k", "ဂ": "k", "ဃ": "k", "င": "ng", "စ": "c", "ဆ": "c", "ဇ": "c", "ဈ": "c", "ည": "nyi",
             "ဉ": "nyin", "ဋ": "t", "ဌ": "t", "ဍ": "t", "ဎ": "t", "ဏ": "n", "တ": "t", "ထ": "t", "ဒ": "t", "ဓ": "t",
             "န": "n", "ပ": "p", "ဖ": "p", "ဗ": "p", "ဘ": "p", "မ": "m", "ယ": "y", "လ": "l", "ဝ": "w", "သ": "t", "ရ": "y",
             "ဟ": "h", "ဠ": "n"}
MY_MED_Y = {"k": "ky", "kh": "ch", "g": "gy", "p": "py", "ph": "phy", "b": "by", "m": "my", "l": "ly", "ng": "ny",
            "ny": "ny", "h": "hy", "y": "y", "s": "s", "hs": "hs", "z": "z", "t": "ty", "ht": "hty", "d": "dy", "n": "ny", "w": "w", "th": "th"}
MY_MED_H = {"m": "hm", "n": "hn", "ng": "hng", "ny": "hny", "l": "hl", "w": "hw", "y": "sh", "ly": "sh", "my": "hmy",
            "py": "py", "ky": "ch", "th": "th"}
MY_VOICE = {"k": "g", "ky": "gy", "kh": "g", "ch": "gy", "s": "z", "hs": "z", "t": "d", "ht": "d", "p": "b", "ph": "b",
            "py": "by", "phy": "by", "th": "dh"}
MY_SYMBOLS = {"၍": "ywei", "၌": "hnaik", "၏": "i", "၎င်း": "lagaung", "၎": "lagaung"}
MY_PARTICLES = set("ပါ တယ် တာ ပဲ ကို က တို့ ပေး ကြ ချင် ပြီ ခဲ့ ကြောင့် တော့ စရာ ပေါ့ ဖို့ တဲ့ သလား သလဲ တုန်း ကြီး ပေမဲ့ တဲ့အခါ".split())


def my_syllables(chunk):
    """Split Burmese text into syllable strings."""
    syls = []
    i, n = 0, len(chunk)
    cur = ""
    while i < n:
        c = chunk[i]
        is_start = (c in MY_C or c in MY_IV or c == "ဉ") and not (i + 1 < n and chunk[i + 1] in "်္")
        if c in MY_C and i + 2 < n and chunk[i + 1] == "့" and chunk[i + 2] == "်": is_start = False
        if is_start and cur:
            syls.append(cur); cur = ""
        cur += c
        i += 1
    if cur: syls.append(cur)
    return syls


def my_syl(s):
    """(initial_rom, rhyme_rom, ends_in_stop) for one syllable."""
    i, n = 0, len(s)
    if s[0] in MY_IV:
        ini, base_iv = "", MY_IV[s[0]]; i = 1
    elif s[0] in MY_C or s[0] == "ဉ":
        ini, base_iv = MY_C.get(s[0], "ny"), None; i = 1
    else:
        return "", s, False
    medy = medw = medh = False
    vs = ""
    fin = None
    while i < n:
        c = s[i]
        if c in "ျြ": medy = True
        elif c == "ွ": medw = True
        elif c == "ှ": medh = True
        elif c in "ါာိီုူေဲံ": vs += c
        elif c in "့း": pass
        elif c in MY_C or c == "ဉ":
            if i + 1 < n and s[i + 1] in "်္" or (i + 2 < n and s[i + 1] == "့" and s[i + 2] == "်"):
                fin = c
            else:
                fin = fin or c
        elif c in "်္": pass
        i += 1
    if medy: ini = MY_MED_Y.get(ini, ini + "y")
    if medh: ini = MY_MED_H.get(ini, "h" + ini)
    v = vs.replace("ါ", "ာ")
    if base_iv is not None:
        if fin:
            cls = MY_FCLASS.get(fin, "")
            rh = {"k": "ouk", "ng": "oun", "n": "oun", "m": "oun", "t": "ouk", "p": "ouk", "nyin": "in", "nyi": "i"}.get(cls, base_iv) if base_iv == "u" else base_iv + {"k": "k", "n": "n"}.get(cls, "")
            return ini, rh, cls in ("k", "t", "p", "c")
        return ini, base_iv + ("n" if "ံ" in v else ""), False
    cls = MY_FCLASS.get(fin, "") if fin else ""
    if "ံ" in v: cls = cls or "m"; v = v.replace("ံ", "")
    w = medw
    table_open = {"": "a", "ာ": "a", "ိ": "i", "ီ": "i", "ု": "u", "ူ": "u", "ေ": "ei", "ဲ": "e", "ော": "aw", "ို": "o",
                  "ိုး": "o", "ော": "aw"}
    stop = cls in ("k", "t", "p", "c")
    if not cls:
        if w and v in ("ေ", "ဲ"): return ini + "w", "e", False
        if w and v == "": return ini + "w", "a", False
        r = table_open.get(v, table_open.get(v.replace("ာ", ""), "a"))
        return ini + ("w" if w else ""), r, False
    if v in ("ော", "ော"):
        r = {"k": "auk", "ng": "aung"}.get(cls, "aw")
    elif v == "ို":
        r = {"k": "aik", "ng": "aing", "l": "o"}.get(cls, "o")
    elif v == "ိ":
        r = {"t": "eik", "p": "eik", "n": "ein", "m": "ein", "k": "eik", "ng": "ein", "c": "eik"}.get(cls, "i")
    elif v == "ု":
        r = {"t": "ouk", "p": "ouk", "n": "oun", "m": "oun", "k": "ouk", "ng": "oun", "nyin": "oun", "c": "ouk"}.get(cls, "u")
    else:
        if w and cls in ("t", "p", "n", "m"):
            return ini, {"t": "ut", "p": "ut", "n": "un", "m": "un"}[cls], stop
        r = {"k": "et", "ng": "in", "c": "it", "nyi": "i", "nyin": "in", "t": "at", "n": "an", "p": "at", "m": "an",
             "y": "e", "l": "an", "w": "aw", "h": "a"}.get(cls, "a")
        if w: return ini + "w", r, stop
    return ini + ("w" if w else ""), r, stop


def my_chunk(chunk):
    """Romanise a Burmese chunk without spaces: syllables separated, voicing of particles, bare 'a' syllables joined."""
    words = OVR.get("my_words", {})
    syls = []
    for piece in re.split(r"(၍|၌|၏|၎င်း|၎)", chunk):
        if piece in MY_SYMBOLS: syls.append(piece)
        elif piece: syls += my_syllables(piece)
    # longest override match over syllable sequences
    pieces = []
    k = 0
    while k < len(syls):
        for L in range(min(8, len(syls) - k), 0, -1):
            ph = "".join(syls[k:k + L])
            if ph in words:
                pieces.append(("ovr", ph, words[ph])); k += L; break
        else:
            pieces.append(("syl", syls[k], None)); k += 1
    out = []
    prev_stop = None
    for kind, s, r in pieces:
        if kind == "ovr":
            out.append([r, False, False, False]); prev_stop = r.endswith(("k", "t", "p")); continue
        if s in MY_SYMBOLS:
            out.append([MY_SYMBOLS[s], False, False, False]); prev_stop = False; continue
        ini, rh, stop = my_syl(s)
        bare = s in MY_C          # a bare consonant (a, ka, ta, sa…) is joined to the next syllable
        if s in MY_PARTICLES and prev_stop is False and ini in MY_VOICE:
            ini = MY_VOICE[ini]
        out.append([ini + rh, bare, stop, s in MY_PARTICLES])
        prev_stop = stop
    text = ""
    for k, item in enumerate(out):
        r, bare = item[0], item[1]
        text += r
        if k < len(out) - 1:
            nxt = out[k + 1]
            join = bare and not nxt[1] and not (len(nxt) > 3 and nxt[3])
            if not join: text += " "
    return text


def my_reading(text):
    out = []
    for nat, chunk in split_runs(text, lambda c: "က" <= c <= "႟" and c not in "၊။" and not ("၀" <= c <= "၉")):
        if not nat:
            for ch in chunk:
                if "၀" <= ch <= "၉": out.append(str(ord(ch) - 0x1040))
                else: out.append(map_punct(ch))
            continue
        out.append(" " + my_chunk(chunk) + " ")
    return tidy("".join(out))


# ----------------------------------------------------------------------------- driver
READERS = {"zh": zh_reading, "th": th_reading, "ta": ta_reading, "km": km_reading, "lo": lo_reading, "my": my_reading}


def reading(lang, text, wid=None):
    ids = OVR.get(lang + "_ids", {})
    if wid in ids: return ids[wid]
    if lang == "th": return th_reading(text, wid)
    return READERS[lang](text)


def main(argv):
    langs = ["th", "km", "lo", "my", "zh", "ta"]
    if "--lang" in argv: langs = argv[argv.index("--lang") + 1].split(",")
    write = "--write" in argv
    (HERE / "out").mkdir(exist_ok=True)
    for lang in langs:
        path = VOCAB / f"{lang}.json"
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        rom = {}
        for wid, text in data["words"].items():
            if isinstance(text, str) and text.strip():
                rom[wid] = reading(lang, text, wid)
        (HERE / "out" / f"{lang}.json").write_text(json.dumps(rom, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        if lang == "th":
            _TH_RAW_PATH.write_text(json.dumps(_th_raw, ensure_ascii=False, indent=0), encoding="utf-8")
        if lang == "th" and TH_FLAGS:
            (HERE / "out" / "th_flags.json").write_text(json.dumps(TH_FLAGS, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(lang, len(rom), "readings")
        if write:
            new = {}
            for key in data:
                new[key] = data[key]
                if key == "source":
                    new["rom_system"] = SYSTEMS[lang]
            new["rom_system"] = SYSTEMS[lang]
            new = {k: new[k] for k in ["lang", "source", "rom_system"] + [k for k in new if k not in ("lang", "source", "rom_system")]}
            new["rom"] = rom
            path.write_text(json.dumps(new, ensure_ascii=False, indent=1) + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
