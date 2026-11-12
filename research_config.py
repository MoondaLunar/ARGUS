"""Central research vocabulary. Matching a term never verifies a person."""
import json
from pathlib import Path

PROFILE_PATH = Path(__file__).parent / 'research' / 'search-profile.json'


def load_profile(path=PROFILE_PATH):
    profile = json.loads(Path(path).read_text(encoding='utf-8'))
    excluded = {x['term'].casefold() for x in profile['exclusions']}
    for entry in profile['verified_identifiers']:
        if not entry.get('source_url') or not entry.get('source_quote') or not entry.get('reviewed_at'):
            raise ValueError('Verified identifiers require source URL, quotation and review date')
    for category in ('speculative_hypotheses', 'exclusions'):
        if any(x.get('active') for x in profile[category]):
            raise ValueError(f'{category} cannot be active search configuration')
    for category in ('contextual_research_terms', 'verified_identifiers'):
        if any(x.get('active') and x['term'].casefold() in excluded for x in profile[category]):
            raise ValueError('Excluded term cannot be an active query')
    return profile


def active_search_terms():
    p = load_profile()
    return sorted({e['term'] for cat in ('verified_identifiers', 'contextual_research_terms')
                   for e in p[cat] if e.get('active')}, key=str.casefold)


def verified_aliases():
    return sorted({e['term'] for e in load_profile()['verified_identifiers']})
