"""On-demand public weather and world headlines, with explicit source/time."""
from dataclasses import dataclass,field
from datetime import datetime,timezone,timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode,urlsplit
import math
import xml.etree.ElementTree as ET
from .net import json_request,request,NetworkError
from .tools import Source,plain_html

@dataclass
class Location:
    name: str
    latitude: float
    longitude: float
    timezone: str = "auto"
    country: str = ""
    region: str = ""
    @property
    def label(self):return ", ".join(x for x in [self.name,self.region,self.country] if x)
    def validate(self):
        if not math.isfinite(self.latitude) or not math.isfinite(self.longitude) or not (-90<=self.latitude<=90 and -180<=self.longitude<=180):
            raise ValueError("Invalid coordinates.")

@dataclass
class LocationChoices:
    query: str
    locations: list

@dataclass
class ForecastDay:
    date: str
    minimum: float
    maximum: float
    rain_chance: object
    code: int

@dataclass
class WeatherReport:
    location: Location
    valid_at: str
    retrieved_at: str
    timezone: str
    temperature: float
    feels_like: object
    humidity: object
    wind: object
    code: int
    days: list = field(default_factory=list)
    source: str = "https://open-meteo.com/"

@dataclass
class NewsReport:
    sources: list
    retrieved_at: str
    failures: list = field(default_factory=list)
    query: str = ""

# Forecast interpretation; grouped where translations convey the same condition.
CONDITIONS = {
 "en":["Clear","Mostly clear","Partly cloudy","Overcast","Fog","Drizzle","Rain","Snow","Showers","Thunderstorm","Unknown"],
 "id":["Cerah","Umumnya cerah","Berawan sebagian","Mendung","Kabut","Gerimis","Hujan","Salju","Hujan lokal","Badai petir","Tidak diketahui"],
 "pt":["Céu limpo","Pouco nublado","Parcialmente nublado","Encoberto","Nevoeiro","Chuvisco","Chuva","Neve","Aguaceiros","Trovoada","Desconhecido"],
 "tet":["Lalehan moos","Lalehan moos liu","Kalohan balu","Kalohan barak","Abu-rai","Udan ki'ik","Udan","Neve","Udan iha fatin balu","Udan ho rai-tarutu","La hatene"],
}

def condition(code,language="en"):
    if code in {0,1,2,3}:idx=code
    elif code in {45,48}:idx=4
    elif code in {51,53,55,56,57}:idx=5
    elif code in {61,63,65,66,67}:idx=6
    elif code in {71,73,75,77,85,86}:idx=7
    elif code in {80,81,82}:idx=8
    elif code in {95,96,97,99}:idx=9
    else:idx=10
    return CONDITIONS.get(language,CONDITIONS['en'])[idx]

def now_iso():return datetime.now(timezone.utc).isoformat(timespec="seconds")

def home_location(settings):
    return Location(settings.weather_city,float(settings.weather_latitude),float(settings.weather_longitude),settings.weather_timezone,"Timor-Leste" if settings.weather_city.casefold() in {"dili","díli"} else "")

def geocode(query,language="en"):
    query=query.strip()
    if not query or len(query)>120:raise ValueError("Enter a city name (up to 120 characters).")
    lang=language if language in {'en','id','pt'} else 'en'
    params={"name":query,"count":5,"language":lang,"format":"json"}
    data=json_request("https://geocoding-api.open-meteo.com/v1/search?"+urlencode(params),timeout=12)
    if data.get('error'):raise NetworkError('City lookup failed.')
    results=[]
    for entry in data.get('results',[]):
        try:
            location=Location(str(entry['name']),float(entry['latitude']),float(entry['longitude']),entry.get('timezone','auto'),entry.get('country',''),entry.get('admin1',''))
            location.validate();results.append(location)
        except (KeyError,ValueError,TypeError):continue
    if not results:raise ValueError("City not found. Try another spelling or use coordinates in Settings.")
    return results

def forecast(location):
    location.validate()
    params={"latitude":location.latitude,"longitude":location.longitude,
      "current":"temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
      "daily":"temperature_2m_min,temperature_2m_max,precipitation_probability_max,weather_code",
      "timezone":location.timezone or "auto","forecast_days":3,"temperature_unit":"celsius","wind_speed_unit":"kmh"}
    data=json_request("https://api.open-meteo.com/v1/forecast?"+urlencode(params),timeout=15)
    if data.get('error'):raise NetworkError('Weather provider returned an error.')
    try:
        current=data['current'];temperature=float(current['temperature_2m'])
        if not math.isfinite(temperature):raise ValueError()
        daily=data.get('daily',{});days=[]
        for i,date in enumerate(daily.get('time',[])[:3]):
            days.append(ForecastDay(date,float(daily['temperature_2m_min'][i]),float(daily['temperature_2m_max'][i]),daily.get('precipitation_probability_max',[None]*3)[i],int(daily['weather_code'][i])))
        return WeatherReport(location,current['time'],now_iso(),data.get('timezone',location.timezone),temperature,current.get('apparent_temperature'),current.get('relative_humidity_2m'),current.get('wind_speed_10m'),int(current['weather_code']),days)
    except (KeyError,IndexError,ValueError,TypeError):raise NetworkError('Incomplete or invalid forecast response.') from None

def weather_query(query,settings):
    q=query.strip().casefold()
    home=home_location(settings)
    if q in {'','home','here','di sini','iha ne\'e',settings.weather_city.casefold(),'díli' if settings.weather_city.casefold()=='dili' else settings.weather_city.casefold()}:
        return forecast(home)
    matches=geocode(query,settings.locale)
    if len(matches)>1:return LocationChoices(query,matches)
    return forecast(matches[0])

NEWS_FEEDS=[
    ('BBC World','https://feeds.bbci.co.uk/news/world/rss.xml',{'www.bbc.com','www.bbc.co.uk','bbc.com','bbc.co.uk'}),
    ('The Guardian World','https://www.theguardian.com/world/rss',{'www.theguardian.com','theguardian.com'}),
]

def parse_feed(raw,publisher,allowed_hosts,query="",now=None,limit=8):
    if b'<!ENTITY' in raw or b'<!DOCTYPE' in raw:raise ValueError('RSS declarations are not supported.')
    root=ET.fromstring(raw);now=now or datetime.now(timezone.utc)
    results=[]
    for item in root.findall('.//item')[:100]:
        title=plain_html(item.findtext('title','')).strip()[:250]
        url=item.findtext('link','').strip();parts=urlsplit(url)
        if not title or parts.scheme!='https' or parts.hostname not in allowed_hosts or parts.username or parts.password:continue
        # Only headline metadata is retained; no full copyrighted story extraction.
        if query and not all(word in title.casefold() for word in query.casefold().split()):continue
        published=item.findtext('pubDate','').strip()
        try:
            dt=parsedate_to_datetime(published)
            if dt.tzinfo is None:dt=dt.replace(tzinfo=timezone.utc)
            if dt>now+timedelta(minutes=10):continue
            published=dt.astimezone(timezone.utc).isoformat(timespec='seconds')
        except (ValueError,TypeError):published=""
        results.append(Source(title,url,"",publisher,published,tuple(plain_html(e.text or "")[:80] for e in item.findall("category")[:12])))
        if len(results)>=max(1,min(50,limit)):break
    return results

def world_news(query=""):
    sources=[];failures=[]
    for publisher,url,hosts in NEWS_FEEDS:
        try:
            raw=request(url,timeout=10,limit=1_000_000)
            sources.extend(parse_feed(raw,publisher,hosts,query))
        except (NetworkError,ValueError,ET.ParseError):failures.append(publisher)
    if len(failures)==len(NEWS_FEEDS):raise NetworkError('News feeds could not be reached. Try again or open news in your browser.')
    seen=set();unique=[]
    for source in sorted(sources,key=lambda s:s.published,reverse=True):
        if source.url not in seen:unique.append(source);seen.add(source.url)
    return NewsReport(unique[:16],now_iso(),failures,query)

def weather_text(report,language="en"):
    headings={"en":("Weather","Feels like","Humidity","Wind","Forecast","Rain chance","Data time","Retrieved"),"id":("Cuaca","Terasa seperti","Kelembapan","Angin","Prakiraan","Peluang hujan","Waktu data","Diambil"),"pt":("Tempo","Sensação","Humidade","Vento","Previsão","Prob. chuva","Hora dos dados","Obtido"),"tet":("Kondisaun tempu","Sente hanesan","Umidade","Anin","Previzaun","Prob. udan","Tempu dadus","Hetan")}
    h=headings.get(language,headings['en'])
    lines=[f'{h[0]} · {report.location.label}',f'{condition(report.code,language)} · {report.temperature:g} °C',f'{h[1]}: {report.feels_like if report.feels_like is not None else "—"} °C · {h[2]}: {report.humidity if report.humidity is not None else "—"}%',f'{h[3]}: {report.wind if report.wind is not None else "—"} km/h',f'{h[4]}:']
    for day in report.days:
        chance='—' if day.rain_chance is None else f'{day.rain_chance}%'
        lines.append(f'{day.date}: {day.minimum:g}–{day.maximum:g} °C · {condition(day.code,language)} · {h[5]} {chance}')
    lines.extend([f'{h[6]}: {report.valid_at} ({report.timezone})',f'{h[7]}: {report.retrieved_at}','Open-Meteo · '+report.source])
    return '\n'.join(lines)

def news_text(report,language="en"):
    title={'en':'World headlines','id':'Berita dunia','pt':'Notícias do mundo','tet':'Notísia mundu'}.get(language,'World headlines')
    lines=[title+' · '+report.retrieved_at]
    for item in report.sources:lines.extend([item.title+' · '+item.publisher,item.published+' · '+item.url])
    if not report.sources:lines.append({'id':'Tidak ada judul yang cocok; coba kata lain.','pt':'Nenhum título corresponde.','tet':'La hetan títulu.','en':'No matching headlines.'}.get(language,'No matching headlines.'))
    if report.failures:lines.append('Unavailable: '+', '.join(report.failures))
    return '\n'.join(lines)
