"""What a connection must carry, and what it must refuse.

Run: python3 -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trawler_public_records import (  # noqa: E402
    EntityMention,
    PublicRecord,
    PublicRecordsCrawler,
)


def record(doc_id, source, url, *mentions):
    return PublicRecord(
        doc_id=doc_id,
        doc_type="INDICTMENT",
        title=f"doc {doc_id}",
        url=url,
        source=source,
        date_filed=None,
        case_number=None,
        court=None,
        parties=[],
        entities_found=list(mentions),
        full_text="",
        pdf_path=None,
        extracted_links=[],
    )


def mention(name, etype, quote, confidence=0.7):
    return EntityMention(name=name, entity_type=etype, context=quote, confidence=confidence)


class ConnectionEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.crawler = PublicRecordsCrawler(seed_urls=[], search_terms=[], sources=[])

    def test_connection_carries_both_quotes_and_source_urls(self):
        line_a = "The defendant Monica Witt departed for Iran in 2013."
        line_b = "A grand jury returned the indictment against Monica Witt."
        self.crawler.records = [
            record("A", "DDC", "https://example.gov/a.pdf", mention("Monica Witt", "PERSON", line_a, 0.9)),
            record("B", "DDC", "https://example.gov/b.pdf", mention("Monica Witt", "PERSON", line_b, 0.9)),
        ]
        conns = self.crawler.find_connections_between_records()
        self.assertEqual(len(conns), 1)
        conn = conns[0]
        self.assertEqual(conn["entity"], "Monica Witt")
        self.assertNotEqual(conn["confidence"], 0.8)  # the old constant
        quotes = [e["quote"] for e in conn["evidence"]]
        urls = [e["url"] for e in conn["evidence"]]
        self.assertIn(line_a, quotes)
        self.assertIn(line_b, quotes)
        self.assertEqual(urls, ["https://example.gov/a.pdf", "https://example.gov/b.pdf"])
        self.assertIn("exact string match", conn["basis"])

    def test_thin_identifier_is_not_a_connection(self):
        """'Case Number 3' matched across two unrelated filings before the guard."""
        self.crawler.records = [
            record("A", "TENN-E", "https://example.gov/a.pdf", mention("Case Number 3", "CASE_NUMBER", "Case Number 3", 0.9)),
            record("B", "TENN-E", "https://example.gov/b.pdf", mention("Case Number 3", "CASE_NUMBER", "Case Number 3", 0.9)),
        ]
        self.assertEqual(self.crawler.find_connections_between_records(), [])

    def test_docket_number_across_two_courts_is_not_one_case(self):
        self.crawler.records = [
            record("A", "TENN-E", "https://example.gov/a.pdf", mention("03-cv-225", "CASE_NUMBER", "No. 03-cv-225", 0.9)),
            record("B", "NC-EB", "https://example.gov/b.pdf", mention("03-cv-225", "CASE_NUMBER", "No. 03-cv-225", 0.9)),
        ]
        self.assertEqual(self.crawler.find_connections_between_records(), [])

    def test_topic_overlap_lowers_confidence(self):
        self.crawler.records = [
            record("A", "DDC", "https://example.gov/a.pdf", mention("Monica Witt", "PERSON", "Monica Witt", 0.6)),
            record("B", "DDC", "https://example.gov/b.pdf", mention("Monica Witte", "PERSON", "Monica Witte", 0.6)),
        ]
        conns = self.crawler.find_connections_between_records()
        self.assertEqual(len(conns), 1)
        self.assertLess(conns[0]["confidence"], 0.6)
        self.assertIn("name similarity", conns[0]["basis"])


class ExtractionTest(unittest.TestCase):
    def test_names_are_extracted_and_stopwords_are_not(self):
        from trawler_public_records import PublicRecordExtractor

        text = "The United States District Court charged Monica Witt in 2014. Filed January 2014."
        names = {m.name for m in PublicRecordExtractor.extract_names(text)}
        self.assertIn("Monica Witt", names)
        self.assertFalse(any(n.startswith("The United") for n in names))
        self.assertFalse(any(n.startswith("January") for n in names))


if __name__ == "__main__":
    unittest.main()
