import unittest
from unittest.mock import Mock
from tempfile import TemporaryDirectory
from trawler import MemoryWebTrawler
from trawler_enhanced_v2 import OptimizedWebTrawler
from trawler_irgc_monica_witt import IRGCMonicaWittCrawler
from analysis_engine import LocationIntelligence, CorrelationAnalyzer
from offline_session import OfflineSession

class RetainedCapabilityTests(unittest.TestCase):
    def test_legacy_network_request_blocked(self):
        with self.assertRaisesRegex(RuntimeError,'Legacy network execution'):
            OfflineSession().get('https://www.justice.gov/a')

    def test_model_cache_receives_full_context_not_integer(self):
        # Avoid constructing any crawl/cache directories or model connection.
        crawler=OptimizedWebTrawler.__new__(OptimizedWebTrawler)
        crawler.cache_ollama_query=Mock(return_value={'fixture':True})
        text='full evidence context beyond an arbitrary hash'
        crawler.query_ollama('A','B',text)
        crawler.cache_ollama_query.assert_called_once_with('A','B',text)

    def test_distance_and_metadata_patterns_remain_available(self):
        self.assertEqual(LocationIntelligence.haversine_distance(10,20,10,20),0)
        result=CorrelationAnalyzer.detect_metadata_patterns([{'metadata':{'gps':{'latitude':10,'longitude':20}}}])
        self.assertEqual(sum(result['common_locations'].values()),1)

    def test_case_view_does_not_treat_hypothesis_as_identity(self):
        crawler=IRGCMonicaWittCrawler(sources=[])
        self.assertFalse(crawler.is_target_related('Vanilla Latte at the end of the day'))
        self.assertFalse(crawler.is_target_related('Fatemah Zahra'))
        self.assertTrue(crawler.is_target_related('Document mentions Monica Witt.'))
        mentions=crawler.extract_target_mentions('Monica Witt appeared.')["monica_witt"]
        self.assertFalse(mentions[0]['identity_verified'])
        self.assertEqual(crawler.build_intelligence_report()['monica_witt_case']['aliases'],[])

    def test_case_view_checks_complete_text_and_preserves_unrelated_records(self):
        crawler=IRGCMonicaWittCrawler(sources=[])
        crawler.crawler.crawl=Mock(return_value={'records':[{'full_text':'x '*5000+' Monica Witt', 'title':'one'}, {'full_text':'other','title':'two'}]})
        result=crawler.crawl()
        self.assertEqual(len(result['all_records']),2);self.assertEqual(len(result['all_target_documents']),1)

    def test_context_query_is_not_classified_as_a_person(self):
        from unittest.mock import patch
        crawler = IRGCMonicaWittCrawler(sources=[])
        with patch('trawler_irgc_monica_witt.active_search_terms', return_value=['IRGC']):
            mentions = crawler.extract_target_mentions('IRGC mentioned in a document')
        self.assertEqual(mentions['monica_witt'], [])
        self.assertEqual(len(mentions['related']), 1)
