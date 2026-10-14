"""LAFA's helper for the search box and the Virtual Assistant — no AI.

LAFA does not generate text. A message is handled in this order, all on
this computer unless the learner explicitly asks for an internet service:

1. commands: /calc, /os, /help, /remind, /weather, /news, /timor, /ask;
2. the local search (lafa/search.py): lessons, atlas, Edukasaun OS guides,
   saved material and file names;
3. an honest "not found" with choices — never an invented answer.

Weather, news and Wikipedia (/ask) are only fetched when asked for; offline
they say calmly that they need internet while local features keep working.
"""
from dataclasses import dataclass, field
from typing import Optional
import re
from urllib.parse import urlsplit

from .i18n import tr
from .calculator import calculate
from . import osguide, personality, search

@dataclass
class Result:
    text: str
    mood: str = "talking"
    files: Optional[object] = None
    sources: list = field(default_factory=list)
    link: str = ""
    weather: Optional[object] = None
    news: Optional[object] = None
    reminder: Optional[tuple] = None
    timor: bool = False
    guide: Optional[object] = None
    outcome: Optional[object] = None      # search.Outcome for the window

@dataclass
class Intent:
    tool: str
    query: str
    kind: str = "all"

# Commands that run entirely on this computer.
LOCAL_TOOLS = {"help", "calc", "joke", "os_help", "reminder"}
# Commands that use an internet service (only when the learner asks).
INTERNET_TOOLS = {"weather", "world_news", "timor_news", "public_answer"}

def direct_intent(message):
    m = message.strip()
    m = re.sub(r"^(?:lafa[, ]+|tolong\s+|please\s+)", "", m, flags=re.I).strip()
    weather = re.match(r"^(?:/weather|/cuaca|(?:bagaimana\s+)?(?:cuaca|weather|previsão do tempo|kondisaun tempu))(?:\s+(.*))?$", m, re.I | re.S)
    if weather:
        q = re.sub(r"^(?:di|in|iha|em)\s+", "", (weather.group(1) or "").strip(), flags=re.I)
        q = re.sub(r"\s*(?:hari ini|besok|today|tomorrow|agora|aban|ohin)\??$", "", q, flags=re.I).strip(" ?")
        return Intent("weather", q)
    local_news = re.match(r"^(?:/timor|berita timor(?:-leste)?|timor(?:-leste)? news|notísia timor|notícias de timor)(?:\s+(.*))?$", m, re.I | re.S)
    if local_news: return Intent("timor_news", (local_news.group(1) or "priority").strip())
    news = re.match(r"^(?:/news|/berita)(?:\s+(.*))?$", m, re.I | re.S)
    if news: return Intent("world_news", (news.group(1) or "").strip(" ?"))
    reminder = re.match(r"^/(?:remind|ingatkan)\s+(\d+)\s+(.+)$", m, re.I | re.S)
    if reminder: return Intent("reminder", reminder.group(2).strip(), reminder.group(1))
    if m.casefold() in {"/help", "/bantuan", "/ajuda", "/ajuda?", "/help?"}: return Intent("help", "")
    if m.casefold() in {"/joke", "/lelucon", "/piada", "/anedota"}: return Intent("joke", "")
    os_help = re.match(r"^/(?:os|eduka)(?:\s+(.*))?$", m, re.I | re.S)
    if os_help: return Intent("os_help", (os_help.group(1) or "").strip())
    calc = re.match(r"^/(?:calc|hitung|kalkula)\s+(.+)$", m, re.I | re.S)
    if calc: return Intent("calc", calc.group(1).strip())
    public = re.match(r"^/ask\s+(.+)$", m, re.I | re.S)
    if public: return Intent("public_answer", public.group(1).strip())
    return None

class Agent:
    def __init__(self, settings, secrets=None):
        # `secrets` is accepted for old callers and ignored: LAFA uses no keys.
        self.settings = settings
    @property
    def lang(self): return self.settings.locale
    def run(self, message, history=None, online=False):
        """Answer a message from the search box or the Virtual Assistant."""
        intent = direct_intent(message)
        if intent:
            if intent.tool in INTERNET_TOOLS and not online:
                return Result(tr(self.lang, "needs_internet_calm"), "sitting")
            return self.execute(intent)
        return self.local_answer(message)
    def local_answer(self, message):
        """Everything without internet: lessons, guides, files, calculator."""
        outcome = search.search(message, self.lang, self.settings.roots)
        text = search.summary(outcome, self.lang, tr)
        mood = {"answer": "reading", "guide": "reading", "calc": "studying", "files": "reading", "choices": "thinking"}.get(outcome.mode, "sitting")
        return Result(text, mood, guide=outcome.guide, outcome=outcome)
    # Old name, kept for callers of LAFA 0.1.x.
    offline_answer = local_answer
    def guide_result(self, guide):
        return Result(guide.text(self.lang), "reading", guide=guide)
    def public_answer(self, query):
        """Wikipedia, only when the learner asks for it (/ask or the button)."""
        from .tools import encyclopedia_search, encyclopedia_article
        lang = self.lang
        if not 1 <= len(query) <= 300 or "\n" in query: raise ValueError("Public questions must be one line, 1–300 characters.")
        sources = encyclopedia_search(query, lang)
        if not sources: return Result(tr(lang, "no_public_results"), "reading")
        text = encyclopedia_article(sources[0])[:2400]
        edition = urlsplit(sources[0].url).hostname.split(".")[0]
        return Result(f"📖 {tr(lang, 'article_extract')} · {sources[0].title} · Wikipedia ({edition})\n\n{text}\n\n{sources[0].url}", "reading", sources=sources)
    def execute(self, intent):
        lang = self.lang
        if intent.tool == "public_answer": return self.public_answer(intent.query)
        if intent.tool == "help": return Result(tr(lang, "help_text"), "talking")
        if intent.tool == "joke": return Result(personality.joke(lang), "talking")
        if intent.tool == "os_help":
            guide = osguide.BY_KEY.get(intent.query.casefold()) or (osguide.find(intent.query, False) if intent.query else None)
            if guide: return self.guide_result(guide)
            return Result(tr(lang, "os_list") + "\n" + "\n".join(f'{g.icon} {g.key} — {g.title.get(lang, g.title["en"])}' for g in osguide.GUIDES), "reading")
        if intent.tool == "calc": return Result(f"{tr(lang, 'calc')}: {intent.query} = {calculate(intent.query)}", "studying")
        if intent.tool == "reminder":
            minutes = int(intent.kind)
            if not 1 <= minutes <= 1440 or not 1 <= len(intent.query) <= 240: raise ValueError("Use /remind 1..1440 short message (max 240 characters).")
            return Result(tr(lang, "addreminder") + f" · {minutes} min · {intent.query}", "serious", reminder=(minutes, intent.query))
        if intent.tool == "timor_news":
            from .timor import timor_news
            from .live_info import news_text
            topic = intent.query if intent.query in {"priority", "education", "arts_culture", "development", "technology"} else "priority"
            report = timor_news(topic); text = news_text(report, lang).split(" · ", 1)[1]
            return Result(tr(lang, "timor_news") + " · " + text, "reading", news=report, timor=True)
        if intent.tool == "weather":
            from .live_info import weather_query, weather_text, LocationChoices
            report = weather_query(intent.query, self.settings)
            text = tr(lang, "choosecity") if isinstance(report, LocationChoices) else weather_text(report, lang)
            return Result(text, "thinking", weather=report)
        if intent.tool == "world_news":
            from .live_info import world_news, news_text
            report = world_news(intent.query)
            return Result(news_text(report, lang), "reading", news=report)
        return self.local_answer(intent.query)
