"""Timor-Leste public headline metadata and source-linked cultural cards."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from pathlib import Path
import json
import random
import unicodedata
from .live_info import NewsReport,parse_feed,now_iso
from .net import request,NetworkError

FEEDS=[
 ('Tatoli','https://tatoli.tl/feed/',{'tatoli.tl','www.tatoli.tl'}),
 ('Timor Post','https://timorpost.com/feed/',{'timorpost.com','www.timorpost.com'}),
 ('Government of Timor-Leste','https://timor-leste.gov.tl/?feed=rss2&lang=en',{'timor-leste.gov.tl','www.timor-leste.gov.tl'}),
]
NEWS_LINKS=[('Tatoli','https://tatoli.tl/'),('Timor Post','https://timorpost.com/'),('Government of Timor-Leste','https://timor-leste.gov.tl/?lang=en'),('Tatoli Education (English)','https://en.tatoli.tl/category/education/')]
TOPICS={
 'education':['education','educacao','edukasaun','school','eskola','university','universidade','student','estudante','teacher','profesor','professor','aprendizagem'],
 'arts_culture':['culture','cultura','kultura','cultural','arte','artes','artist','dance','dansa','tebe','bidu','tais','museum','museu','festival','music'],
 'development':['development','dezenvolvimentu','desenvolvimento','infrastructure','infraestrutura','construction','konstrusaun','road','estrada','water','bee','sanitation','health','saude','investment'],
 'technology':['technology','teknolojia','teknologia','tecnologia','digital','internet','science','sientifika','cientifica','innovation','inovasaun','inovacao','computer','komputador','artificial intelligence','inteligencia artificial'],
}
def normal(text):return ''.join(c for c in unicodedata.normalize('NFKD',text.casefold()) if not unicodedata.combining(c))
def matches(source,topic):
    text=normal(source.title+' '+' '.join(source.categories))
    keys=TOPICS.get(topic,[word for values in TOPICS.values() for word in values])
    # Word matching avoids treating every word containing 'art' as arts news.
    import re
    return any(re.search(r'(?<!\w)'+re.escape(word)+r'(?!\w)',text) for word in keys)
def fetch_one(feed):
    publisher,url,hosts=feed
    try:return parse_feed(request(url,timeout=12,limit=1_000_000),publisher,hosts,limit=40),None
    except (NetworkError,ValueError,ET.ParseError):return [],publisher

def timor_news(topic='priority'):
    if topic not in {'priority',*TOPICS}:raise ValueError('Unknown Timor-Leste news topic.')
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(fetch_one,FEEDS))
    failures=[failure for items,failure in results if failure]
    if len(failures)==len(FEEDS):raise NetworkError('Timor-Leste feeds are unavailable. Open the source websites or try again later.')
    sources=[];seen=set()
    for items,failure in results:
        for source in items:
            if source.url not in seen and matches(source,topic):sources.append(source);seen.add(source.url)
    sources.sort(key=lambda item:item.published,reverse=True)
    return NewsReport(sources[:18],now_iso(),failures,topic)

@dataclass
class Card:
    text:str
    source:str=''
    mood:str='talking'
    category:str='positive'

class CardDeck:
    def __init__(self):
        self.cards=json.loads((Path(__file__).parent/'assets'/'timor-cards.json').read_text());self.previous=None;self.count=0
        # Cards published later in the online source catalog (validated data).
        from .updates import extra_cards
        known={card['id'] for card in self.cards}
        self.cards.extend(card for card in extra_cards() if card['id'] not in known)
    def next(self,language='en',cultural=True,positive=True):
        candidates=[c for c in self.cards if (c['category']=='positive' and positive) or (c['category']!='positive' and cultural)]
        if not candidates:return None
        options=[c for c in candidates if c['id']!=self.previous] or candidates
        card=random.choice(options);self.previous=card['id'];self.count+=1
        prefix={'en':'Did you know?','id':'Tahukah kamu?','pt':'Sabias que?','tet':'Ita hatene ka?'}.get(language,'Did you know?')
        text=card['text'].get(language,card['text']['en'])
        if card['category']!='positive':text=prefix+'\n'+text+'\n'+card['source']+'\n'+{'en':'Checked','id':'Diperiksa','pt':'Verificado','tet':'Verifika'}.get(language,'Checked')+': '+card['checked_on']
        return Card(text,card.get('source',''),card.get('mood','talking'),card['category'])
