"""Checks readings in ./out: no script left, separators aligned with the original, nothing empty."""
import json, re, sys, random
sys.path.insert(0, '.')
from romanize import map_punct
from pathlib import Path
V = str(Path(__file__).resolve().parents[2] / 'lafa' / 'assets' / 'timor' / 'vocab') + '/'
SCRIPT = {'th': '฀-๿', 'km': 'ក-៿', 'lo': '຀-໿', 'my': 'က-႟', 'zh': '一-鿿　-〿＀-￯', 'ta': '஀-௿'}
bad = 0
for lang, rng in SCRIPT.items():
    D = json.load(open(V + lang + '.json'))['words']; R = json.load(open(str(Path(__file__).resolve().parent / 'out' / ('%s.json' % lang))))
    for k, v in D.items():
        r = R.get(k, '')
        o = map_punct(v)
        probs = []
        if not r.strip(): probs.append('empty')
        if re.search('[' + rng + ']', r): probs.append('script left')
        for sep in ';,()/…?!:':
            if o.count(sep) != r.count(sep): probs.append('sep ' + sep)
        if probs:
            bad += 1; print(lang, k, probs, v, '|', r)
print('problems:', bad)
