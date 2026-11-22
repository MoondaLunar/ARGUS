import hashlib
import io
import json
import unittest
from unittest.mock import Mock, patch
from public_transport import PublicTransport, DocumentResponse, validate_url, public_url
from search_sources import SearchSource, SourceHit, search_all
from trawler_public_records import PublicRecordsCrawler

class Response:
    def __init__(self, body=b'hello', status=200, **headers):
        self.body=body; self.status_code=status
        self.headers={'Content-Type':'text/plain', **headers};self.encoding='utf-8'
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def iter_content(self,chunk_size):yield self.body

class Source(SearchSource):
    name='fixture'
    def search(self,term,limit=10):
        return [SourceHit(self.name,term,'Fixture','https://www.justice.gov/record','record')]

class FixtureTransport:
    allowed_hosts={'www.justice.gov'}
    def __init__(self, body, mime='text/html'):
        self.body=body;self.mime=mime;self.calls=[]
    def fetch(self,url):
        self.calls.append(url)
        return DocumentResponse(self.body,url,url,self.mime,'2026-01-01T00:00:00Z',hashlib.sha256(self.body).hexdigest())

class PipelineTests(unittest.TestCase):
    def test_url_scope_and_false_positive_substrings(self):
        for url in ['https://www.justice.gov.evil.test/a','https://evil.test/?x=justice.gov',
                    'https://justice.gov@evil.test/a','file:///tmp/a','http://www.justice.gov/a',
                    'https://127.0.0.1/a','https://www.justice.gov:8080/a','https://www.justice.gov/\\evil',
                    'https://www.justice.gov/login']:
            with self.subTest(url=url),self.assertRaises(ValueError):validate_url(url)
        self.assertEqual(validate_url('https://www.justice.gov/administration#x'),'https://www.justice.gov/administration')

    def test_network_is_disabled_without_opt_in(self):
        session=Mock();t=PublicTransport(session=session)
        with self.assertRaises(RuntimeError):t.fetch('https://www.justice.gov/a')
        session.get.assert_not_called()
        self.assertEqual(search_all(['test'])['hits'],[])

    def test_redirect_revalidated_before_request_and_no_head(self):
        session=Mock();session.get.return_value=Response(status=302,Location='https://evil.test/a')
        t=PublicTransport(allow_network=True,session=session,resolver=lambda _:None)
        with self.assertRaises(ValueError):t.fetch('https://www.justice.gov/a')
        self.assertEqual(session.get.call_count,1);session.head.assert_not_called()
        self.assertFalse(session.get.call_args.kwargs['allow_redirects'])

    def test_stream_limit_even_without_content_length(self):
        session=Mock();session.get.return_value=Response(b'123456')
        t=PublicTransport(allow_network=True,session=session,resolver=lambda _:None,max_bytes=5)
        with self.assertRaisesRegex(ValueError,'size exceeds'):t.fetch('https://www.justice.gov/a')

    def test_credentials_never_forwarded_to_redirect_host(self):
        session=Mock();session.get.side_effect=[Response(status=302,Location='https://www.justice.gov/a'),Response()]
        t=PublicTransport(allow_network=True,session=session,resolver=lambda _:None,credentials={'api.govinfo.gov':{'X-Api-Key':'SECRET'}})
        t.fetch('https://api.govinfo.gov/a')
        self.assertIn('X-Api-Key',session.get.call_args_list[0].kwargs['headers'])
        self.assertNotIn('X-Api-Key',session.get.call_args_list[1].kwargs['headers'])

    def test_private_dns_answer_rejected(self):
        from public_transport import require_public_address
        with patch('socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]):
            with self.assertRaises(ValueError):require_public_address('www.justice.gov')

    def test_html_cleaning_stable_identity_and_all_discovery_routes(self):
        t=FixtureTransport(b'<script>Fake Person</script><p>Monica Witt appears in this fixture.</p>')
        c=PublicRecordsCrawler([],['query one','query two'],sources=[Source()],transport=t,rate_limit=0)
        data=c.crawl();r=data['records'][0]
        self.assertNotIn('Fake Person',r['full_text']);self.assertEqual(len(r['provenance']),2)
        self.assertTrue(r['content_sha256']);self.assertEqual(len(t.calls),1)
        c2=PublicRecordsCrawler([],[],sources=[])
        self.assertEqual(r['doc_id'],c2.parse_document_as_record(r['full_text'],r['url']).doc_id)

    def test_failed_source_report_does_not_leak_secret(self):
        s=Source();s.search=Mock(side_effect=RuntimeError('url?api_key=SECRET'))
        report=search_all(['one'],sources=[s]);self.assertEqual(len(report['errors']),1)
        self.assertNotIn('SECRET',json.dumps(report))

    def test_search_hit_export_has_no_fetch_credential(self):
        h=SourceHit('s','q','t','https://api.govinfo.gov/a?api_key=SECRET','x',extra={'fetch_url':'SECRET'})
        self.assertNotIn('SECRET',json.dumps(h.as_dict()))

    def test_pdf_bytes_reach_parser_and_disabled_pdf_is_reported(self):
        t=FixtureTransport(b'%PDF-fixture','application/pdf')
        c=PublicRecordsCrawler(['https://www.justice.gov/a'],[],sources=[],transport=t,rate_limit=0)
        with patch.object(c,'extract_pdf_text',return_value='Fixture legal document') as extract:
            self.assertEqual(len(c.crawl()['records']),1)
            extract.assert_called_once_with(b'%PDF-fixture')
        c=PublicRecordsCrawler(['https://www.justice.gov/a'],[],sources=[],transport=t,extract_pdfs=False,rate_limit=0)
        self.assertEqual(c.crawl()['errors'][0]['error_type'],'PdfDisabled')

    def test_malformed_pdf_does_not_become_text_evidence(self):
        c=PublicRecordsCrawler([],[],sources=[])
        self.assertIsNone(c.extract_pdf_text(b'not a pdf'))

    def test_pdf_character_bound(self):
        c=PublicRecordsCrawler([],[],sources=[])
        with patch('pypdf.PdfReader') as reader:
            reader.return_value.pages=[Mock(extract_text=Mock(return_value='X'*100))]
            self.assertEqual(len(c.extract_pdf_text(b'fixture',max_chars=12)),12)

    def test_failed_fetch_is_visible(self):
        t=FixtureTransport(b'');t.fetch=Mock(side_effect=TimeoutError('secret'))
        c=PublicRecordsCrawler(['https://www.justice.gov/a'],[],sources=[],transport=t,rate_limit=0)
        out=c.crawl();self.assertEqual(out['records'],[]);self.assertEqual(out['errors'][0]['error_type'],'TimeoutError')
