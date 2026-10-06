import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from lafa.config import Settings,Secrets,PROVIDERS,STATES
from lafa.tools import FileSearch,plain_html,web_url,encyclopedia_search
from lafa.agent import Agent,validated_intent,envelope,direct_intent
from lafa.providers import ProviderClient,Answer,responses_answer
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
    def test_config_roundtrip_no_secrets(self):
        s=Settings(language='id',roots=[str(self.root)],models={'openai':'test-model'})
        p=self.root/'settings.json';s.save(p)
        loaded=Settings.load(p);self.assertEqual(loaded.language,'id')
        self.assertNotIn('api_key',p.read_text());self.assertEqual(p.stat().st_mode&0o777,0o600)
    def test_secure_keyring_no_plaintext(self):
        from lafa.config import secure_backend
        class Unsafe:pass
        Unsafe.__module__='keyrings.alt.file.PlaintextKeyring'
        self.assertFalse(secure_backend(Unsafe()))
    def test_all_languages_complete(self):
        for locale,strings in STRINGS.items():self.assertEqual(len(strings),len(KEYS),locale)
    def test_natural_language_and_commands(self):
        self.assertEqual(direct_intent('cari musik Timor').kind,'music')
        self.assertEqual(direct_intent('/learn photosynthesis').tool,'encyclopedia')
        self.assertEqual(direct_intent('find documents lesson').query,'lesson')
        self.assertIsNone(direct_intent('How are you?'))
        self.assertEqual(direct_intent('cari pelajaran matematika').tool,'encyclopedia')
        self.assertEqual(direct_intent('cari musik Timor di internet').tool,'web_search')
        self.assertEqual(direct_intent('/web videos tutorial').kind,'videos')
    def test_model_action_allowlist(self):
        self.assertIsNone(validated_intent({'tool':'shell','query':'rm -rf'}))
        self.assertIsNone(validated_intent({'tool':'search_files','query':[], 'kind':'all'}))
        self.assertIsNone(validated_intent({'tool':'web_search','query':'a','kind':'shell'}))
        self.assertEqual(validated_intent({'tool':'search_files','query':'lesson'}).kind,'all')
    def test_envelope_plaintext_and_mood(self):
        self.assertEqual(envelope('Hello')['reply'],'Hello')
        self.assertEqual(envelope('{"reply":"Hi","mood":"invalid"}')['mood'],'talking')
    @patch('lafa.agent.FileSearch.search')
    @patch('lafa.providers.json_request')
    def test_offline_never_searches_or_calls_api(self,api,search):
        s=Settings(roots=[str(self.root)]);a=Agent(s,Secrets())
        for message in ['/files lesson','/learn biology','Hello']:
            a.run(message,[],False)
        api.assert_not_called();search.assert_not_called()
    @patch('lafa.providers.json_request')
    def test_no_api_key_does_not_invent_answer(self,api):
        with patch.dict(os.environ,{},clear=True):
            a=Agent(Settings(),Secrets());a.client.ready=lambda:False
            r=a.run('Explain this code:\nimport os',[],True)
            self.assertIn('API key',r.text);api.assert_not_called()
    @patch('lafa.providers.json_request')
    def test_local_tool_results_never_sent_to_ai(self,api):
        (self.root/'private-music.mp3').touch()
        secrets=Secrets();secrets.set('openai','test-key')
        s=Settings(roots=[str(self.root)],models={'openai':'test-model'})
        api.return_value={'output':[{'content':[{'type':'output_text','text':json.dumps({'reply':'','mood':'reading','action':{'tool':'search_files','query':'private','kind':'music'}})}]}]}
        r=Agent(s,secrets).run('Find my songs',[],True)
        self.assertEqual(len(r.files.hits),1);self.assertEqual(api.call_count,1)
        self.assertNotIn('private-music.mp3',repr(api.call_args))
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

class AdapterTests(unittest.TestCase):
    def client(self,provider):
        s=Settings(provider=provider,models={provider:'test-model'});keys=Secrets();keys.set(provider,'fake-key')
        return ProviderClient(s,keys)
    @patch('lafa.providers.json_request')
    def test_openai(self,req):
        req.return_value={'output':[{'content':[{'type':'output_text','text':'Hi'}]}]}
        self.assertEqual(self.client('openai').chat([{'role':'user','content':'hello'}],'sys').text,'Hi')
        args=req.call_args.args;self.assertEqual(args[0],PROVIDERS['openai'][1]);self.assertFalse(args[1]['store'])
        self.assertEqual(args[1]['instructions'],'sys')
    @patch('lafa.providers.json_request')
    def test_gemini(self,req):
        req.return_value={'candidates':[{'content':{'parts':[{'text':'secret','thought':True},{'text':'Hi'}]}}]}
        self.assertEqual(self.client('gemini').chat([{'role':'assistant','content':'old'},{'role':'user','content':'hello'}],'sys').text,'Hi')
        self.assertEqual(req.call_args.args[1]['contents'][0]['role'],'model')
        self.assertEqual(req.call_args.args[2]['x-goog-api-key'],'fake-key')
    @patch('lafa.providers.json_request')
    def test_anthropic(self,req):
        req.return_value={'content':[{'type':'text','text':'Hi'}]}
        self.assertEqual(self.client('anthropic').chat([{'role':'user','content':'hello'}],'sys').text,'Hi')
        self.assertEqual(req.call_args.args[2]['anthropic-version'],'2023-06-01')
    @patch('lafa.providers.json_request')
    def test_deepseek(self,req):
        req.return_value={'choices':[{'message':{'content':'Hi'}}]}
        self.assertEqual(self.client('deepseek').chat([{'role':'user','content':'hello'}],'sys').text,'Hi')
        self.assertEqual(req.call_args.args[1]['messages'][0]['role'],'system')
    @patch('lafa.providers.json_request')
    def test_perplexity_agent_api(self,req):
        req.return_value={'output':[{'type':'search_results','results':[{'title':'Source','url':'https://example.org/'}]},{'content':[{'type':'output_text','text':'Hi'}]}]}
        answer=self.client('perplexity').chat([{'role':'user','content':'hello'}],'sys')
        self.assertEqual(answer.text,'Hi');self.assertEqual(len(answer.sources),1)
        self.assertEqual(req.call_args.args[0],'https://api.perplexity.ai/v1/agent');self.assertEqual(req.call_args.args[1]['preset'],'fast')
    def test_missing_model_rejected(self):
        client=self.client('openai');client.settings.models={}
        with self.assertRaises(NetworkError):client.chat([],'system')

if __name__=='__main__':unittest.main()
