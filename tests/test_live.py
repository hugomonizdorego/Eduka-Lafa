"""Deterministic tests for fetched data and the session reminder clock."""
from datetime import datetime,timezone
import unittest
from unittest.mock import patch
from lafa.config import Settings
from lafa.live_info import Location,LocationChoices,forecast,weather_query,weather_text,parse_feed,world_news,condition
from lafa.reminders import Reminders
from lafa.agent import Agent,direct_intent,validated_intent
from lafa.config import Secrets
from lafa.tools import RESOURCES,resource_search_url
from lafa.net import NetworkError

WEATHER={'timezone':'Asia/Dili','current':{'time':'2026-10-06T10:00','temperature_2m':29,'apparent_temperature':32,'relative_humidity_2m':65,'wind_speed_10m':12,'weather_code':2},'daily':{'time':['2026-10-06','2026-10-07','2026-10-08'],'temperature_2m_min':[24,24,23],'temperature_2m_max':[31,30,30],'precipitation_probability_max':[20,40,35],'weather_code':[2,80,2]}}
RSS=b'''<rss><channel><item><title>Sample world headline</title><link>https://www.bbc.com/news/1</link><pubDate>Tue, 06 Oct 2026 10:00:00 GMT</pubDate></item><item><title>unsafe</title><link>https://evil.example/1</link></item><item><title>future</title><link>https://www.bbc.com/news/2</link><pubDate>Tue, 06 Oct 2099 10:00:00 GMT</pubDate></item></channel></rss>'''

class LiveTests(unittest.TestCase):
    @patch('lafa.live_info.json_request',return_value=WEATHER)
    def test_weather_units_times_and_attribution(self,request):
        report=forecast(Location('Dili',-8.56,125.57,'Asia/Dili'))
        self.assertEqual(report.temperature,29);self.assertEqual(len(report.days),3)
        self.assertIn('temperature_unit=celsius',request.call_args.args[0]);self.assertIn('wind_speed_unit=kmh',request.call_args.args[0])
        text=weather_text(report,'id');self.assertIn('Open-Meteo',text);self.assertIn('Asia/Dili',text);self.assertIn('Diambil',text)
        self.assertEqual(condition(95,'id'),'Badai petir')
    @patch('lafa.live_info.json_request',return_value={'current':{'temperature_2m':None}})
    def test_incomplete_weather_is_error(self,request):
        with self.assertRaises(NetworkError):forecast(Location('Dili',-8,125))
    def test_invalid_coordinates_rejected(self):
        for lat,lon in [(float('nan'),0),(0,float('inf')),(91,0),(0,181)]:
            with self.assertRaises(ValueError):Location('bad',lat,lon).validate()
    @patch('lafa.live_info.forecast')
    @patch('lafa.live_info.geocode',return_value=[Location('Springfield',1,2),Location('Springfield',3,4)])
    def test_ambiguous_city_needs_selection(self,geocode,forecast):
        result=weather_query('Springfield',Settings());self.assertIsInstance(result,LocationChoices);forecast.assert_not_called()
    @patch('lafa.live_info.forecast')
    @patch('lafa.live_info.geocode')
    def test_home_location_does_not_geocode(self,geocode,forecast):
        weather_query('',Settings());geocode.assert_not_called();self.assertEqual(forecast.call_args.args[0].name,'Dili')
    def test_rss_host_date_query_and_title(self):
        sources=parse_feed(RSS,'BBC',{'www.bbc.com'},now=datetime(2026,10,6,12,tzinfo=timezone.utc))
        self.assertEqual(len(sources),1);self.assertEqual(sources[0].publisher,'BBC');self.assertTrue(sources[0].published.endswith('+00:00'))
        self.assertEqual(parse_feed(RSS,'BBC',{'www.bbc.com'},query='missing'),[])
        with self.assertRaises(ValueError):parse_feed(b'<!DOCTYPE a><rss/>','BBC',{'www.bbc.com'})
    @patch('lafa.live_info.request',side_effect=[RSS,NetworkError('unavailable')])
    def test_partial_news_failure_preserves_source(self,request):
        report=world_news();self.assertEqual(len(report.sources),1);self.assertEqual(report.failures,['The Guardian World'])
    @patch('lafa.live_info.request',side_effect=NetworkError('unavailable'))
    def test_all_news_failures_do_not_invent_headlines(self,request):
        with self.assertRaises(NetworkError):world_news()
    def test_new_direct_commands(self):
        self.assertEqual(direct_intent('cuaca di Dili besok').query,'Dili')
        self.assertEqual(direct_intent('berita dunia').tool,'world_news')
        self.assertEqual(direct_intent('/remind 5 minum air').kind,'5')
        self.assertEqual(direct_intent('/focus').kind,'25')
        self.assertEqual(direct_intent('/source Ruangguru: pecahan').tool,'resource_search')
        self.assertEqual(direct_intent('cari pelajaran pecahan di Ruangguru').kind,'Ruangguru')
        self.assertEqual(validated_intent({'tool':'resource_search','query':'math','source':'Ruangguru'}).kind,'Ruangguru')
        self.assertIsNone(validated_intent({'tool':'resource_search','query':'a','source':'evil'}))
        self.assertIsNotNone(validated_intent({'tool':'weather','query':''}))
    def test_all_library_domains_and_added_sources(self):
        for name,url in RESOURCES:self.assertIn('site%3A',resource_search_url(name,'learning'))
        self.assertTrue({'Ruangguru','wikiHow','Fandom','Everything2','Conservapedia','Miraheze','Baidu Baike'}<=set(n for n,u in RESOURCES))
    @patch('lafa.agent.weather_query')
    @patch('lafa.agent.world_news')
    def test_offline_gates_live_tools_and_reminders(self,news,weather):
        a=Agent(Settings(),Secrets())
        for command in ['/news','/weather','/remind 5 water']:self.assertIsNone(a.run(command,[],False).reminder)
        news.assert_not_called();weather.assert_not_called()
    def test_reminder_clock_cancel_and_offline_delivery(self):
        now=[0];reminders=Reminders(lambda:now[0]);first=reminders.add(1,'Water');second=reminders.add(2,'Stretch')
        reminders.cancel(second.id);now[0]=59;self.assertEqual(reminders.due(True),[])
        now[0]=60;self.assertEqual(reminders.due(False),[]);self.assertEqual(reminders.due(True),[first]);self.assertEqual(reminders.due(True),[])
    def test_reminder_validation(self):
        reminders=Reminders()
        for minutes,text in [(0,'a'),(1441,'a'),(1,''),(1,'a'*241),(float('nan'),'a')]:
            with self.assertRaises(ValueError):reminders.add(minutes,text)

if __name__=='__main__':unittest.main()
