import json
import unittest
from unittest.mock import Mock, patch
from public_transport import PublicTransport, configured_transport
from search_sources import GovInfoSource, CourtListenerSource, SecEdgarSource
from test_pipeline import Response

class SearchTransportTests(unittest.TestCase):
    def transport(self, data):
        session = Mock()
        session.get.return_value = session.post.return_value = Response(
            json.dumps(data).encode(), **{'Content-Type':'application/json'})
        return PublicTransport(allow_network=True, session=session, resolver=lambda _:None), session

    def test_every_direct_adapter_is_offline_by_default(self):
        for source in (GovInfoSource(api_key='fixture'), SecEdgarSource(user_agent='fixture contact'), CourtListenerSource(token='fixture')):
            with self.subTest(source=source.name), self.assertRaisesRegex(RuntimeError, 'Network disabled'):
                source.search('fixture')

    def test_govinfo_post_uses_host_header_and_preserves_author_without_court_claim(self):
        transport, session = self.transport({'results':[{'packageId':'fixture', 'governmentAuthor':['Generic publisher'],
            'download':{'pdfLink':'https://api.govinfo.gov/fixture/pdf'}}]})
        source = GovInfoSource(api_key='SECRET', transport=transport)
        hit = source.search('Jane Example')[0]
        self.assertIsNone(hit.court)
        self.assertEqual(hit.extra['government_author'], ['Generic publisher'])
        self.assertNotIn('SECRET', json.dumps(hit.as_dict()))
        args = session.post.call_args
        self.assertEqual(args.kwargs['headers']['X-Api-Key'], 'SECRET')
        self.assertNotIn('SECRET', args.args[0])
        self.assertFalse(args.kwargs['allow_redirects'])
        self.assertEqual(args.kwargs['json']['pageSize'], 10)

    def test_search_rejects_redirects_and_oversize_json(self):
        transport, session = self.transport({})
        session.get.return_value = Response(status=302, Location='https://www.justice.gov/a')
        with self.assertRaisesRegex(ValueError, 'redirects'):
            transport.search_json(SecEdgarSource.API)
        session.get.return_value = Response(b'12345', **{'Content-Type':'application/json'})
        transport.max_bytes = 4
        with self.assertRaisesRegex(ValueError, 'size exceeds'):
            transport.search_json(SecEdgarSource.API)

    def test_post_not_general_purpose_and_json_schema_checked(self):
        transport, _ = self.transport([])
        with self.assertRaisesRegex(ValueError, 'Unapproved'):
            transport.search_json('https://www.justice.gov/a', method='POST')
        with self.assertRaisesRegex(ValueError, 'object'):
            transport.search_json(SecEdgarSource.API)

    def test_sec_and_courtlistener_fixture_parsers(self):
        transport, _ = self.transport({'hits':{'hits':[{'_id':'x:filing.htm', '_source':{'ciks':['00042'], 'adsh':'01-02', 'display_names':['Example']}}]}})
        hit = SecEdgarSource(user_agent='Research test@example.test', transport=transport).search('Example')[0]
        self.assertEqual(hit.url, 'https://www.sec.gov/Archives/edgar/data/42/0102/filing.htm')
        transport, session = self.transport({'results':[{'id':3,'absolute_url':'/opinion/3/example/', 'court':'ca1','caseName':'Example'}]})
        hit = CourtListenerSource(token='SECRET', transport=transport).search('Example')[0]
        self.assertEqual(hit.court, 'ca1')
        self.assertEqual(session.get.call_args.kwargs['headers']['Authorization'], 'Token SECRET')

    def test_environment_credentials_are_scoped_to_document_hosts(self):
        with patch.dict('os.environ', {'ARGUS_GOVINFO_KEY':'G','ARGUS_COURTLISTENER_TOKEN':'C','ARGUS_USER_AGENT':'Contact'}):
            transport = configured_transport()
        self.assertFalse(transport.allow_network)
        self.assertEqual(transport.credentials['api.govinfo.gov'], {'X-Api-Key':'G'})
        self.assertEqual(transport.credentials['www.sec.gov'], {'User-Agent':'Contact'})
        self.assertNotIn('www.justice.gov', transport.credentials)

    def test_encoded_private_paths_and_dot_traversal_rejected(self):
        from public_transport import validate_url
        for path in ('/%6cogin', '/%252eenv', '/x/../login', '/%2egit/config', '/x%5cy', '/phpinfo.php'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_url('https://www.justice.gov' + path)
