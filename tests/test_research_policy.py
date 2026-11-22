import ast
import json
import subprocess
import sys
import unittest
from pathlib import Path
from research_config import active_search_terms, load_profile, verified_aliases

ROOT = Path(__file__).resolve().parents[1]

class ResearchPolicyTest(unittest.TestCase):
    def test_exclusions_and_hypotheses_are_not_queries(self):
        p = load_profile()
        self.assertEqual(verified_aliases(), [])
        self.assertEqual(set(active_search_terms()), {'Monica Witt', 'Monica Elfriede Witt'})
        for category in ('exclusions', 'speculative_hypotheses'):
            self.assertFalse(set(active_search_terms()) & {e['term'] for e in p[category]})

    def test_archive_retains_every_literal_list_member(self):
        archive = json.loads((ROOT/'research/vocabulary-original.json').read_text())
        terms = {e['term'] for e in archive['entries']}
        for source in archive['sources']:
            for node in ast.walk(ast.parse((ROOT/source['path']).read_text())):
                if isinstance(node, (ast.List, ast.Set, ast.Tuple)):
                    for e in node.elts:
                        if isinstance(e, ast.Constant) and isinstance(e.value, str):
                            self.assertIn(e.value, terms)

    def test_legacy_import_fails_before_loading_tools(self):
        for name in ('trawler', 'trawler_enhanced', 'trawler_enhanced_v2',
                     'trawler_24_7_continuous', 'trawler_irgc_monica_witt'):
            r = subprocess.run([sys.executable, '-c', f'import {name}'], cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('legacy runtime is disabled', r.stderr)
            self.assertNotIn('ModuleNotFoundError', r.stderr)
