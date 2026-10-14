from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from lafa.config import Settings
from lafa.tools import FileSearch,plain_html,web_url,encyclopedia_search
from lafa.agent import Agent,direct_intent
from lafa.search import understand
from lafa.net import NetworkError,request,NoRedirect
from lafa.i18n import STRINGS,KEYS

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def test_local_search_categories_and_hidden_files(self):
        (self.root/'lesson.txt').write_text('Math lesson')
        (self.root/'lesson.mp3').write_bytes(b'audio')
        (self.root/'.lesson.txt').write_text('private')
        sub=self.root/'.cache'; sub.mkdir();(sub/'lesson.docx').touch()
        hits=FileSearch([self.root]).search('lesson','documents')
        self.assertEqual([h.name for h in hits.hits],['lesson.txt'])
        self.assertEqual(len(FileSearch([self.root]).search('lesson','music').hits),1)
    def test_local_search_overlapping_roots_deduplicates(self):
        sub=self.root/'docs';sub.mkdir();(sub/'a.txt').touch()
        self.assertEqual(len(FileSearch([self.root,sub]).search('').hits),1)
    def test_symlinks_and_outside_read_blocked(self):
        with tempfile.TemporaryDirectory() as outside:
            p=Path(outside)/'private.txt'; p.write_text('private')
            (self.root/'link.txt').symlink_to(p)
            search=FileSearch([self.root]);self.assertFalse(search.search('link').hits)
            with self.assertRaises(ValueError):search.read(p)
            with self.assertRaises(ValueError):search.read(self.root/'link.txt')
    def test_search_limits_are_reported(self):
        for i in range(8):(self.root/f'file{i}.txt').touch()
        results=FileSearch([self.root]).search('file',limit=3)
        self.assertEqual(len(results.hits),3);self.assertTrue(results.limited)
    def test_read_docx_and_odt_and_truncation(self):
        for ext,member,xml in [('docx','word/document.xml','<w:document xmlns:w="word"><w:p><w:r><w:t>Hello world</w:t></w:r></w:p></w:document>'),('odt','content.xml','<root><p>Hello world</p></root>')]:
            p=self.root/f'doc.{ext}'
            with zipfile.ZipFile(p,'w') as z:z.writestr(member,xml)
            self.assertEqual(FileSearch([self.root]).read(p),'Hello world')
        p=self.root/'long.txt';p.write_text('x'*100)
        self.assertIn('truncated',FileSearch([self.root]).read(p,20))
    def test_xml_entities_rejected(self):
        p=self.root/'doc.docx'
        with zipfile.ZipFile(p,'w') as z:z.writestr('word/document.xml','<!DOCTYPE x [<!ENTITY a "unsafe">]><x>&a;</x>')
        with self.assertRaises(ValueError):FileSearch([self.root]).read(p)
    def test_html_scripts_removed(self):
        self.assertEqual(plain_html('<p>A &amp; B</p><script>secret()</script>'),'A & B')
    def test_config_roundtrip(self):
        s=Settings(language='id',roots=[str(self.root)])
        p=self.root/'settings.json';s.save(p)
        loaded=Settings.load(p);self.assertEqual(loaded.language,'id')
        self.assertNotIn('provider',p.read_text());self.assertEqual(p.stat().st_mode&0o777,0o600)
    def test_all_languages_complete(self):
        for locale,strings in STRINGS.items():self.assertEqual(len(strings),len(KEYS),locale)
    def test_understanding_requests(self):
        self.assertEqual(understand('Cari file tugas matematika'),('files','tugas matematika'))
        self.assertEqual(understand('find file report')[0],'files')
        self.assertEqual(understand('12 * (3 + 4)'),('calc','12 * (3 + 4)'))
        self.assertEqual(understand('Bagaimana mengganti wallpaper?')[0],'guide')
        self.assertEqual(understand('Apa itu fotosintesis?'),('topic','fotosintesis'))
        self.assertEqual(direct_intent('/calc 2+2').tool,'calc');self.assertIsNone(direct_intent('How are you?'))
    @patch('lafa.net.request')
    @patch('lafa.tools.json_request')
    def test_local_answers_never_use_the_network(self,wiki,net):
        (self.root/'tugas matematika.txt').write_text('x')
        a=Agent(Settings(roots=[str(self.root)],language='id'))
        for message,expect in [('Cari file tugas matematika','tugas matematika.txt'),('Apa itu fotosintesis?','fotosintesis'),('/calc 2+3','= 5'),('Bagaimana mengganti wallpaper?','Eduka-Settings')]:
            for online in (False,True):self.assertIn(expect,a.run(message,[],online).text)
        wiki.assert_not_called();net.assert_not_called()
    def test_honest_when_nothing_is_found(self):
        r=Agent(Settings(roots=[],language='en')).run('zzqx unknownword',[],True)
        self.assertIn('found nothing',r.text)
    def test_internet_commands_need_internet(self):
        r=Agent(Settings(language='en')).run('/weather Dili',[],False)
        self.assertIn('needs internet',r.text)
    def test_https_and_redirect_guard(self):
        with self.assertRaises(NetworkError):request('http://example.com')
        with self.assertRaises(NetworkError):NoRedirect().redirect_request(None,None,302,'',{},'https://attacker.example')
    @patch('lafa.tools.json_request')
    def test_wikipedia_sources(self,request):
        request.return_value={'query':{'search':[{'title':'Solar energy','snippet':'<span>Solar</span> energy'}]}}
        s=encyclopedia_search('solar','en')[0]
        self.assertEqual(s.text,'Solar energy');self.assertTrue(s.url.startswith('https://en.wikipedia.org/wiki/'))
    def test_web_query_encoded(self):
        self.assertIn('q=a%26b',web_url('a&b'))
        self.assertTrue(web_url('song','music').startswith('https://archive.org/'))

if __name__=='__main__':unittest.main()
