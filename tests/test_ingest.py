import copy
import unittest
from unittest.mock import Mock
import requests
from ingest import ingest,connection_payload
from test_correlation import record,mention
from trawler_public_records import PublicRecordsCrawler

class IngestionTests(unittest.TestCase):
    def setUp(self):
        c=PublicRecordsCrawler([],[],sources=[])
        c.records=[record('A','X','https://www.justice.gov/a',mention('Jane Example','PERSON','Jane Example testified.')),
                   record('B','X','https://www.justice.gov/b',mention('Jane Example','PERSON','Jane Example appeared.'))]
        c.relationships=c.find_connections_between_records();self.data=c.build_output()

    def test_preview_does_not_send(self):
        session=Mock();out=ingest(self.data,session=session)
        session.post.assert_not_called();self.assertEqual(out['links'],1)
        link=out['payloads'][-1]['payload'];self.assertEqual((link['entityA'],link['entityB']),('A','B'))

    def test_timeout_isolated_and_link_not_sent_without_document(self):
        session=Mock();session.post.side_effect=[requests.Timeout('secret'),Mock(status_code=200)]
        out=ingest(self.data,session=session,dry_run=False)
        self.assertEqual(out['documents'],1);self.assertEqual(out['links'],0)
        self.assertEqual(len(out['document_errors']),1);self.assertEqual(len(out['link_errors']),1)

    def test_pair_keys_distinguish_observations(self):
        a=self.data['connections'][0];b=copy.deepcopy(a);b['document_b']='C';b['evidence'][1]['document']='C'
        self.assertNotEqual(connection_payload(a)['evidenceKey'],connection_payload(b)['evidenceKey'])

    def test_repeat_rows_deduplicated(self):
        self.data['records']*=2;self.data['connections']*=2
        out=ingest(self.data);self.assertEqual(out['documents'],2);self.assertEqual(out['links'],1)

    def test_bad_record_does_not_abort_valid_records(self):
        self.data['records'].insert(0,{})
        out=ingest(self.data);self.assertEqual(out['documents'],2);self.assertEqual(out['links'],1)

    def test_external_api_rejected(self):
        with self.assertRaises(ValueError):ingest(self.data,api='https://external.test')

    def test_invalid_scores_and_quotes_rejected(self):
        conn=self.data['connections'][0]
        for score in (float('nan'),float('inf'),-1,2):
            with self.assertRaises(ValueError):connection_payload({**conn,'confidence':score})
        bad=copy.deepcopy(conn);bad['evidence'][0]['quote']='Unrelated text'
        with self.assertRaises(ValueError):connection_payload(bad)

class AdditionalCorrelationTests(unittest.TestCase):
    def test_unknown_court_does_not_match_docket(self):
        c=PublicRecordsCrawler([],[],sources=[])
        c.records=[record(x,'PUBLIC_RECORDS','https://www.justice.gov/'+x,mention('23-cr-1234','CASE_NUMBER','23-cr-1234')) for x in ('A','B')]
        self.assertEqual(c.find_connections_between_records(),[])
        for r in c.records:r.court='DDC'
        self.assertEqual(len(c.find_connections_between_records()),1)

    def test_mirrored_text_not_independent_evidence(self):
        c=PublicRecordsCrawler([],[],sources=[])
        c.records=[c.parse_document_as_record('Jane Example testified in this fixture.','https://www.justice.gov/'+x) for x in ('a','b')]
        self.assertEqual(c.find_connections_between_records(),[])

    def test_document_count_never_boosts_score(self):
        a=mention('Jane Example','PERSON','Jane Example',.6)
        self.assertEqual(PublicRecordsCrawler._connection_confidence('Jane Example','PERSON',a,a,2),
                         PublicRecordsCrawler._connection_confidence('Jane Example','PERSON',a,a,200))
